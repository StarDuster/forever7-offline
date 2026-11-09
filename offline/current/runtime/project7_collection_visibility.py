# -*- coding: ascii -*-
"""P7 display-only collection policy; original function bodies stay intact.
Install after clean/tutorial policy, before target panels bind callbacks.
An existing Avatar class/data is checked by identity; no Member method is changed.
The caller embeds the fixed public policy text; this module does no file IO.
"""
import hashlib
import json
import sys
import types

POLICY_SHA256 = '453340b4f36c5de867d2288ef2e4afc70561c62098ee5fd60d1ddbd74d506fb9'
MODEL_INDEX_SHA256 = 'd9e3dadcb084dfa05f0e86dd7d0a0532c8c1d9653d550f8a2fe72ceb7a914758'
try:
    _TEXT_TYPES = (basestring,)
except NameError:
    _TEXT_TYPES = (str, bytes)

_MARKER = '_q7_collection_visibility_owner'
_TARGETS = (
    ('entity.avatar_attrs.HeroMgrData', 'HeroMgrData'),
    ('cocos.panels.hero_herolist', 'Panel'),
    ('cocos.panels.collect_hero', 'Panel'),
    ('cocos.panels.bbs_playerinfo_main', 'Panel'),
    ('cocos.panels.hero_wardrobe', 'Panel'),
    ('cocos.comps.hero_herolist_common.wardrobe', 'Comp'),
    ('cocos.panels.hero_common', 'Panel'),
    ('cocos.panels.collect_info', 'Panel'))


def _raw(function):
    return getattr(function, 'im_func', getattr(function, '__func__', function))


def _globals(function):
    function = _raw(function)
    return getattr(function, 'func_globals', getattr(function, '__globals__', {}))


class _ModuleView(object):
    def __init__(self, original, data):
        self.original = original
        self.data = data

    def __getattr__(self, name):
        return getattr(self.original, name)


class _TableView(object):
    """Per-call read view; transformed rows are copies, never original dictionaries."""
    def __init__(self, original, transform):
        self.original = original
        self.transform = transform

    def __getitem__(self, key):
        return self.transform(key, self.original[key])

    def get(self, key, default=None):
        return self[key] if key in self.original else default

    def __contains__(self, key):
        return key in self.original

    def __len__(self):
        return len(self.original)

    def __iter__(self):
        return iter(self.original)

    def keys(self):
        return list(self.original.keys())

    def iterkeys(self):
        return iter(self.original.keys())

    def items(self):
        return [(key, self[key]) for key in self.original]

    def iteritems(self):
        return iter(self.items())

    def values(self):
        return [self[key] for key in self.original]

    def itervalues(self):
        return iter(self.values())


def _clone_call(function, alias, view, args):
    """Clone only this invocation's globals, retaining defaults/closure/raw Py2 code.
    Current globals are read each time: later aliases/callbacks are not frozen.
    """
    function = _raw(function)
    namespace = dict(_globals(function))
    if isinstance(alias, dict):
        namespace.update(alias)
    else:
        namespace[alias] = view
    code = getattr(function, 'func_code', getattr(function, '__code__', None))
    defaults = getattr(function, 'func_defaults', getattr(function, '__defaults__', None))
    closure = getattr(function, 'func_closure', getattr(function, '__closure__', None))
    clone = types.FunctionType(code, namespace, function.__name__, defaults, closure)
    clone.__dict__.update(getattr(function, '__dict__', {}))
    return clone(*args)


class _CollectionMetadataView(_TableView):
    def __init__(self, original, owned):
        self.original = original
        self.owned = owned
        self.transform = self.row

    def row(self, hero_id, data):
        if hero_id in self.owned:
            result = dict(data or {})
            result['release'] = True
            return result
        return data

    def get(self, hero_id, default=None):
        data = self.original.get(hero_id, default)
        return self.row(hero_id, data)


def _check_avatar_data(classes, gg):
    avatar = getattr(gg, '__dict__', {}).get('avatar')
    if avatar is not None:
        data = getattr(avatar, '__dict__', {}).get('heroMgrData')
        if type(data) is not classes[0] or not isinstance(getattr(data, 'heroes', None), dict):
            raise RuntimeError('Collection Avatar data generation/incomplete initialization')


class _Installation(object):
    def __init__(self, policy, modules, classes, gg, helpers):
        self.policy_sha = POLICY_SHA256
        self.indexed_models = frozenset(policy['indexed_model_ids'])
        self.modules = modules
        self.classes = classes
        self.gg = gg
        self.helpers = helpers
        self.records = []
        self.last_route = 'not_used'

    def check(self, modules, classes, gg, helpers):
        if (self.policy_sha != POLICY_SHA256 or self.gg is not gg or self.helpers is not helpers or
                len(self.modules) != len(modules) or any(a is not b for a, b in zip(self.modules, modules)) or
                any(a is not b for a, b in zip(self.classes, classes))):
            raise RuntimeError('Collection module generation changed; fresh engine required')
        _check_avatar_data(classes, gg)
        for cls, name, replacement, original in self.records:
            if cls.__dict__.get(name) is not replacement:
                raise RuntimeError('Collection policy method identity changed')
            original_gg = _globals(original).get('gg')
            if original_gg is not None and original_gg is not gg:
                raise RuntimeError('Collection function has stale gg module')
        return self

    def bind(self, cls, name, replacement):
        original = _raw(getattr(cls, name))
        replacement.__dict__.update(getattr(original, '__dict__', {}))
        setattr(cls, name, replacement)
        self.records.append((cls, name, replacement, original))
        return original

    def current_gg(self):
        current = sys.modules.get('gg')
        if current is not self.gg:
            raise RuntimeError('Collection gg generation changed; fresh install required')
        return current

    def current_globals(self, original):
        namespace = _globals(original)
        if namespace.get('gg', self.gg) is not self.current_gg():
            raise RuntimeError('Collection function globals have stale gg identity')
        return namespace

    def mgr(self):
        avatar = getattr(self.current_gg(), 'avatar', None)
        return getattr(avatar, 'heroMgrData', None) if avatar is not None else None

    def owned(self):
        mgr = self.mgr()
        return frozenset(getattr(mgr, 'heroes', {}))

    def display_call(self, original, args):
        namespace = self.current_globals(original)
        source = namespace['HERO_DATA']
        owned = self.owned()
        def row(hero_id, data):
            if hero_id in owned and data.get('hero_forbid', 0):
                result = dict(data)
                result['hero_forbid'] = 0
                return result
            return data
        aliases = {'HERO_DATA': _ModuleView(source, _TableView(source.data, row))}
        # Owned records can lack collect_msg rows entirely. This is only the
        # current refresh availability view, not fabricated collection/story data.
        if 'COLLECT_MSG' in namespace:
            metadata = namespace['COLLECT_MSG']
            aliases['COLLECT_MSG'] = _ModuleView(metadata, _CollectionMetadataView(metadata.data, owned))
        return _clone_call(original, aliases, None, args)

    def skin_call(self, original, args, hero_id):
        source = self.current_globals(original)['SKIN_DATA']
        mgr = self.mgr()
        hero = mgr.getHero(hero_id) if mgr is not None else None
        owned = frozenset(skin.id for skin in hero.skins.values()) if hero is not None else frozenset()
        def row(skin_id, data):
            # Change only availability. Original title/else non-dye predicates
            # and family handling (including the currently selected dye) remain intact.
            if skin_id in owned and data.get('release') != 1:
                result = dict(data)
                result['release'] = 1
                return result
            return data
        return _clone_call(original, 'SKIN_DATA', _ModuleView(source, _TableView(source.data, row)), args)

    def indexed_actor(self, mgr, hero_id):
        try:
            # Never infer a model from hero ID when the selected skin row is absent.
            self.current_globals(self.helpers.get_hero_model)
            source = self.modules[0].SkinDataMod.data
            skin_id = mgr.getHeroSkin(hero_id)
            skin = source.get(skin_id)
            if skin is None or 'model_id' not in skin:
                return False
            int(skin['model_id'])
            # This is the actual normal hero-show resolver, with no dialogue/home remapping.
            model = self.helpers.get_hero_model(hero_id)
            return str(int(model)) in self.indexed_models
        except (KeyError, TypeError, ValueError, AttributeError):
            return False

    def missing_message(self, code):
        self.last_route = code
        self.gg.ui.panels.common_message.notify_message(
            u'\u8be5\u795e\u5668\u4f7f\u6682\u4e0d\u652f\u6301 3D \u5c55\u793a\uff0c\u90e8\u5206\u8d44\u6599\u53ef\u80fd\u5c1a\u672a\u5b9e\u88c5\u3002')

    def open_info(self, caller, hero_id, original_show, original_hide):
        panel = self.gg.ui.panels.collect_info
        layer = None
        marker = None
        try:
            layer = caller.add_layer(panel, self.gg.ui.panels.navigation_canvas)
            if not layer:
                raise RuntimeError('Collection information layer unavailable')
            marker = (self, layer)
            panel._q7_collection_fallback_layer = marker
            # Bypass our normal-show marker reset for this exact fallback layer.
            original_show(panel, hero_id)
            self.missing_message('two_d_opened_partial_assets')
        except Exception:
            if layer is not None and getattr(panel, '_layer', None) is layer:
                try:
                    original_hide(panel)
                except Exception:
                    pass
            current = panel.__dict__.get('_q7_collection_fallback_layer')
            if layer is not None and current is marker:
                panel.__dict__.pop('_q7_collection_fallback_layer', None)
            self.missing_message('two_d_unavailable')
        return None

    def apply(self):
        mgr_cls, hero_list, collect, card, wardrobe, quick, common, info = self.classes
        hero_data = self.modules[0].HeroDataMod
        installation = self
        for name in ('isHeroDisplayable', 'isHeroListVisible', 'q7_display_heroes', 'q7HasRenderableModel'):
            if name in mgr_cls.__dict__:
                raise RuntimeError('Unexpected existing collection API')
        def isHeroDisplayable(instance, hero_id):
            installation.current_gg()
            data = hero_data.data.get(hero_id)
            return data is not None and (hero_id in instance.heroes or not data.get('hero_forbid', 0))
        def isHeroListVisible(instance, hero_id):
            return hero_id in instance.heroes and isHeroDisplayable(instance, hero_id)
        def display_alias(instance):
            # A bounded fresh immutable projection also covers incremental hrs updates
            # between initFromDict and hero_mgr_data_update, with no global event hook.
            return frozenset(hero_id for hero_id in hero_data.data if isHeroDisplayable(instance, hero_id))
        def q7HasRenderableModel(instance, hero_id):
            return installation.indexed_actor(instance, hero_id)
        mgr_cls.isHeroDisplayable = isHeroDisplayable
        mgr_cls.isHeroListVisible = isHeroListVisible
        mgr_cls.q7_display_heroes = property(display_alias)
        mgr_cls.q7HasRenderableModel = q7HasRenderableModel
        for name in ('isHeroDisplayable', 'isHeroListVisible', 'q7_display_heroes', 'q7HasRenderableModel'):
            self.records.append((mgr_cls, name, mgr_cls.__dict__[name], mgr_cls.__dict__[name]))
        old_init = _raw(mgr_cls.initFromDict)
        def initFromDict(instance, initDict):
            result = old_init(instance, initDict)
            display_alias(instance)
            return result
        self.bind(mgr_cls, 'initFromDict', initFromDict)
        old_list = _raw(hero_list.update_heroes)
        def update_heroes(instance, jump=True):
            return installation.display_call(old_list, (instance, jump))
        self.bind(hero_list, 'update_heroes', update_heroes)
        old_collect = _raw(collect.refresh)
        def refresh(instance):
            return installation.display_call(old_collect, (instance,))
        self.bind(collect, 'refresh', refresh)
        old_card = _raw(card.refresh_hero_info)
        def refresh_hero_info(instance, isme, info_dict):
            if not isme:
                return old_card(instance, isme, info_dict)
            return installation.display_call(old_card, (instance, isme, info_dict))
        self.bind(card, 'refresh_hero_info', refresh_hero_info)
        old_title = _raw(wardrobe.refresh_title)
        def refresh_title(instance):
            return installation.skin_call(old_title, (instance,), instance.hero_id)
        self.bind(wardrobe, 'refresh_title', refresh_title)
        old_quick = _raw(quick.set_hero)
        def set_hero(instance, heroId, skinId=None, call_from=None):
            return installation.skin_call(old_quick, (instance, heroId, skinId, call_from), heroId)
        self.bind(quick, 'set_hero', set_hero)
        old_show = _raw(info.notify_show)
        old_hide = _raw(info.notify_hide)
        old_close = _raw(info.on_btn_close)
        def notify_show(instance, heroid):
            instance.__dict__.pop('_q7_collection_fallback_layer', None)
            return old_show(instance, heroid)
        self.bind(info, 'notify_show', notify_show)
        def notify_hide(instance):
            marker = instance.__dict__.get('_q7_collection_fallback_layer')
            try:
                return old_hide(instance)
            finally:
                if instance.__dict__.get('_q7_collection_fallback_layer') is marker:
                    instance.__dict__.pop('_q7_collection_fallback_layer', None)
        self.bind(info, 'notify_hide', notify_hide)
        def on_btn_close(instance, sender, event):
            marker = instance.__dict__.get('_q7_collection_fallback_layer')
            if marker is not None and marker[0] is installation and marker[1] is getattr(instance, '_layer', None):
                if event == installation.modules[7].cc.ccui.TOUCH_EVENT_ENDED:
                    notify_hide(instance)
                    installation.gg.audio_mgr.ui_sound('tongyong/ui_guanbi')
                return None
            return old_close(instance, sender, event)
        self.bind(info, 'on_btn_close', on_btn_close)
        old_click = _raw(hero_list.on_hero_click)
        def on_hero_click(instance, hero_id, jump_type=''):
            mgr = installation.mgr()
            if mgr is not None and installation.indexed_actor(mgr, hero_id):
                installation.last_route = 'indexed_model_original_path'
                return old_click(instance, hero_id, jump_type)
            instance.notify_attack_tips_hide()
            instance.last_hero_click = hero_id
            return installation.open_info(instance, hero_id, old_show, old_hide)
        self.bind(hero_list, 'on_hero_click', on_hero_click)
        old_enter = _raw(common.enter_scene)
        def enter_scene(instance, ui_info):
            mgr = installation.mgr()
            if mgr is None or not installation.indexed_actor(mgr, ui_info.get('hero_id', 0)):
                installation.missing_message('blocked_before_actor_after_scene')
                return None
            return old_enter(instance, ui_info)
        self.bind(common, 'enter_scene', enter_scene)
        for cls in self.classes:
            setattr(cls, _MARKER, self)
        return self


def install(policy_data=None):
    """Install after clean, preferably before Avatar data/panels initialize.
    An already-defined Avatar class is safe: no Member functions are changed.
    policy_data is the exact embedded JSON text. Repeating an identical install is safe; changed modules/gg/methods require a
    fresh engine instead of repairing old Member/panel caches in place.
    """
    if policy_data is None:
        raise RuntimeError('Embedded fixed collection policy required')
    if not isinstance(policy_data, _TEXT_TYPES):
        raise ValueError('Collection policy must be ASCII JSON text')
    try:
        binary = policy_data.encode('ascii') if not isinstance(policy_data, bytes) else policy_data
        if hashlib.sha256(binary).hexdigest() != POLICY_SHA256:
            raise ValueError('Collection policy hash mismatch')
        policy = json.loads(binary)
        if (policy.get('format') != 'project7-collection-visibility-policy-v1' or
                policy.get('model_index_sha256') != MODEL_INDEX_SHA256 or
                len(policy['indexed_model_ids']) != 393):
            raise ValueError('Unexpected collection model policy')
    except (TypeError, KeyError, UnicodeError):
        raise ValueError('Invalid collection policy text')
    gg = __import__('gg')
    modules = [__import__(name, fromlist=[cls]) for name, cls in _TARGETS]
    classes = [getattr(module, cls) for module, (name, cls) in zip(modules, _TARGETS)]
    helpers = __import__('cutils.chelpers', fromlist=['get_hero_model'])
    existing = getattr(classes[0], _MARKER, None)
    if existing is not None:
        if any(getattr(cls, _MARKER, None) is not existing for cls in classes):
            raise RuntimeError('Collection class cache generation mismatch')
        return existing.check(modules, classes, gg, helpers)
    _check_avatar_data(classes, gg)
    if any(getattr(cls, _MARKER, None) is not None for cls in classes):
        raise RuntimeError('Partial collection class cache requires fresh engine')
    for module in modules + [helpers]:
        if getattr(module, 'gg', gg) is not gg:
            raise RuntimeError('Collection import contains stale gg module')
    # Exact known raw-method ABI before mutating any class. No Member functions
    # are patched; late Avatar/loaded target panel instances are rejected instead.
    methods = ((0, 'initFromDict', 2), (1, 'update_heroes', 2), (1, 'on_hero_click', 3),
               (2, 'refresh', 1), (3, 'refresh_hero_info', 3), (4, 'refresh_title', 1),
               (5, 'set_hero', 4), (6, 'enter_scene', 2), (7, 'notify_show', 2),
               (7, 'notify_hide', 1), (7, 'on_btn_close', 3))
    for index, name, count in methods:
        function = _raw(getattr(classes[index], name, None))
        code = getattr(function, 'func_code', getattr(function, '__code__', None))
        if code is None or code.co_argcount != count:
            raise RuntimeError('Collection original method ABI changed')
    # GameObjectMeta copies only GameObjectMember bases. Our ordinary data and
    # Panel/Comp methods are not Member edits; an already-defined Avatar class
    # alone is safe. Reject only a real cached copy of a target method/class.
    game_object = sys.modules.get('com.base.game_object')
    if game_object is not None:
        members = getattr(game_object, 'members_cache', {})
        cached = getattr(game_object, 'method_cache', {})
        for index, name, count in methods:
            cls = classes[index]
            function = _raw(getattr(cls, name))
            if cls in members:
                raise RuntimeError('Collection target copied into Member cache')
            for entry in cached.get(cls, ()):
                if len(entry) == 2 and _raw(entry[1]) is function:
                    raise RuntimeError('Collection target method already cached for dispatch')
    ui = getattr(gg, '__dict__', {}).get('ui')
    panels = getattr(ui, '__dict__', {}).get('panels')
    cache = getattr(panels, '__dict__', {}).get('_panels', {})
    names = ('hero_herolist', 'collect_hero', 'bbs_playerinfo_main', 'hero_wardrobe', 'hero_common', 'collect_info')
    if any(name in cache for name in names):
        raise RuntimeError('Collection panel instances already cached before install')
    state = _Installation(policy, modules, classes, gg, helpers)
    return state.apply()
