# -*- coding: ascii -*-
"""P7 UI-only retirement policy; server-started guidance, original reliable finish.
Install after tutorial bypass, before Member caches / Avatar construction.
Business action observers are intentionally not authorized by this first policy.
"""
import types
import sys

_DISMISS = frozenset((1, 10, 93, 120, 160, 260, 302, 284, 292))
_SCRIPTED = frozenset((150,))
_BUILD = '_p7_tutorial_build_request'
_STATE = '_p7_tutorial_completion_state'
_INSTALL = None


def _raw(value):
    return getattr(value, 'im_func', getattr(value, '__func__', value))


class _View(object):
    def __init__(self, source, **aliases):
        object.__setattr__(self, '_source', source)
        object.__setattr__(self, '_aliases', aliases)
    def __getattr__(self, name):
        if name in self._aliases:
            return self._aliases[name]
        return getattr(self._source, name)
    def __setattr__(self, name, value):
        setattr(self._source, name, value)


def _cell(value):
    function = lambda: value
    return getattr(function, 'func_closure', getattr(function, '__closure__', None))[0]


def _clone(original, gg):
    namespace = dict(getattr(original, 'func_globals', getattr(original, '__globals__', {})))
    namespace['gg'] = gg
    code = getattr(original, 'func_code', getattr(original, '__code__', None))
    closure = getattr(original, 'func_closure', getattr(original, '__closure__', None))
    if closure:
        cells = list(closure)
        for index, name in enumerate(code.co_freevars):
            if name == 'func' and isinstance(cells[index].cell_contents, types.FunctionType):
                cells[index] = _cell(_clone(cells[index].cell_contents, gg))
        closure = tuple(cells)
    defaults = getattr(original, 'func_defaults', getattr(original, '__defaults__', None))
    return types.FunctionType(code, namespace, original.__name__, defaults, closure)


def _area_free(actor, area):
    try:
        info = actor.cityData.get_area_info(area)
        return bool(info) and info.get('st', (2, False, False))[0] == 0
    except Exception:
        return False


def finish_skipped_build_guide(actor, data):
    """Retire the omitted UI-only newbee 20 guide when its real gate is met.

    The offline tutorial bypass suppresses newbee UI, but the stock city
    entrance still hides build/upgrade until newbee 20 is in finish_newbee.
    Newbee 20 is only 'enter the central court' and its only functional effect
    is to unlock build/upgrade. Server-started processing or actual east/central
    liberation satisfies that gate; complete the guide through the original
    finishNewbee RPC so the existing save is updated, never replaced.
    """
    try:
        if 20 in data.finish_newbee:
            return False
        if not _area_free(actor, 1):
            return False
        processing = getattr(data, 'processing_event', ()) or ()
        events = getattr(getattr(actor, 'eventTriggerData', None), 'completedEvents', ()) or ()
        ready = (20 in processing or 30039 in events or 40036 in events or
                 _area_free(actor, 3) or _area_free(actor, 4))
        if not ready or not callable(getattr(actor, 'finishNewbee', None)):
            return False
        actor.finishNewbee((20,))
        return True
    except Exception:
        return False


class Installation(object):
    def __init__(self, gg, member, originals):
        self.gg = gg
        self.member = member
        self.originals = originals
        self.wrappers = {}
        self.observers = []
        self.panels = None
        self.modules = []
        self.member_copies = []

    def reconcile(self, avatar, pending, snapshot=False):
        # Only callers of the two server RPC wrappers reach this method.
        if getattr(self.gg, 'avatar', None) is not avatar:
            return
        if getattr(avatar, 'destroyed', False) or getattr(avatar, 'destroying', False):
            return
        state = getattr(avatar, _STATE, None)
        if state is None:
            state = {'owner': self, 'sent': set(), 'sending': set(), 'started': set()}
            setattr(avatar, _STATE, state)
        if state['owner'] is not self:
            raise RuntimeError('Tutorial completion owner changed')
        valid = set(x for x in pending if type(x) is int and x > 0)
        if snapshot:
            state['started'].intersection_update(valid)
            # Absence is authoritative retirement. Local fn is not a server ACK.
            state['sent'].intersection_update(valid)
        state['started'].update(valid)
        self.finish_started(avatar, valid & (_DISMISS | _SCRIPTED))
        # Same live Avatar's original current city projection; no cross-day cache.
        if 151 in valid and getattr(getattr(avatar, 'cityData', None), 'useCanteen', False) is True:
            self.finish_started(avatar, (151,))

    def finish_started(self, avatar, events):
        if getattr(self.gg, 'avatar', None) is not avatar:
            return
        state = getattr(avatar, _STATE, None)
        if state is None or state['owner'] is not self:
            return
        for event in sorted(set(events) & state['started']):
            if event in state['sent'] or event in state['sending']:
                continue
            state['sending'].add(event)
            try:
                # Preserve original reliable clientFinishNewbee and local fn update.
                # Never call finish on a chain marker that was not server-started.
                avatar.finishNewbee([event])
                state['sent'].add(event)
                state['started'].discard(event)
            finally:
                state['sending'].discard(event)

    def diagnostics(self, avatar):
        state = getattr(avatar, _STATE, None)
        if state is None or state['owner'] is not self:
            return ()
        return tuple((event, 'absent_original_catalog' if event == 74 else 'awaiting_original_action')
                     for event in sorted(state['started'] - state['sent']))

    def check_avatar(self, avatar_cls=None):
        if avatar_cls is None:
            module = sys.modules.get('entity.ClientAvatar')
            avatar_cls = getattr(module, 'ClientAvatar', None) if module else None
        if avatar_cls is None:
            return True
        for name, expected in self.member_copies:
            if _raw(getattr(avatar_cls, name, None)) is not expected:
                raise RuntimeError('Tutorial Avatar has stale copied Member method')
        return True

    def check(self):
        for name, module, clsname, cls in self.modules:
            if sys.modules.get(name) is not module or getattr(module, clsname) is not cls:
                raise RuntimeError('Tutorial module/class generation changed')
        for name, wrapper in self.wrappers.items():
            if _raw(getattr(self.member, name)) is not wrapper:
                raise RuntimeError('Tutorial completion method replaced')
        for cls, name, wrapper in self.observers:
            if _raw(getattr(cls, name)) is not wrapper:
                raise RuntimeError('Tutorial success observer replaced')
        return self


def install():
    global _INSTALL
    import gg
    module = __import__('entity.avatar_members.NewbeeMember', fromlist=['Member'])
    game_object = __import__('com.base.game_object', fromlist=['members_cache'])
    member = module.Member
    if _INSTALL is not None:
        if _INSTALL.member is not member or _INSTALL.gg is not gg:
            raise RuntimeError('Tutorial completion mixed module generation')
        return _INSTALL.check()
    if getattr(gg, 'avatar', None) is not None:
        raise RuntimeError('Tutorial completion requires no live Avatar')
    if member in game_object.members_cache:
        raise RuntimeError('Tutorial Member already copied; fresh engine required')
    names = ('triggerClientNewbee', 'triggerProcessingEvent')
    originals = dict((name, _raw(getattr(member, name))) for name in names)
    for original in originals.values():
        if not callable(original) or not hasattr(original, 'rpcmethod'):
            raise RuntimeError('Original tutorial RPC descriptor missing')
    owner = Installation(gg, member, originals)
    owner.modules.append(('entity.avatar_members.NewbeeMember', module, 'Member', member))

    def decorate(original, typed_body):
        metadata = original.rpcmethod
        # A new original-schema RpcMethod owns the adapted typed body. Both native
        # metadata.call and normal decorated attribute dispatch enter this body.
        wrapped = module.rpc_method(metadata.rpctype, metadata.argtypes,
                                    metadata.pub)(typed_body)
        wrapped.__name__ = original.__name__
        wrapped._p7_tutorial_completion = owner
        return wrapped

    def wrap(name, key, snapshot):
        original = originals[name]
        def typed_body(avatar, value):
            # A newer authenticated server projection supersedes the scheduled
            # login snapshot, including a single newly started root. Otherwise
            # an old safe tick could resurrect cleared roots or erase new starts.
            avatar.newbeeData._p7_tutorial_projection = object()
            result = original.rpcmethod.func(avatar, value)
            owner.reconcile(avatar, value if snapshot else (value,), snapshot)
            return result
        return decorate(original, typed_body)

    for name, key, snapshot in ((names[0], 'e', False), (names[1], 'pe', True)):
        owner.wrappers[name] = wrap(name, key, snapshot)
    # Only proven positive typed business replies authorize these roots.
    # No action is initiated here; root24 is an explicit retire alias, NOT marker20.
    for module_name, name, key, roots in (
            ('entity.avatar_members.CityMember', 'area_build_reply', 'rs', (20, 24)),
            ('entity.avatar_members.LuckyDrawMember', 'replyLuckyDrawFile', 'rt', (90,)),
            ('entity.avatar_members.CityMember', 'get_city_data_reply', 'cd', (151,)),
            ('entity.avatar_members.EventTriggerMember', 'startEventReply', 'r', (30,)),
            ('entity.avatar_members.RoomMember', 'calcCrystalReply', 'rd', (230,)),
            ('entity.avatar_members.RoomMember', 'activeSkillReply', 'sk', (240,)),
            ('entity.avatar_members.LuckyDrawMember', 'replyLuckyDrawFurnitureCard', 'rs', (250,))):
        target_module = __import__(module_name, fromlist=['Member'])
        cls = target_module.Member
        owner.modules.append((module_name, target_module, 'Member', cls))
        if cls in game_object.members_cache:
            raise RuntimeError('Tutorial action Member already copied')
        old = _raw(getattr(cls, name))
        if not hasattr(old, 'rpcmethod'):
            raise RuntimeError('Original action RPC descriptor missing')
        def observer(old, key, roots, name):
            argnames = tuple(arg.getname() for arg in old.rpcmethod.argtypes)
            def typed_body(avatar, *values):
                result = old.rpcmethod.func(avatar, *values)
                parsed = dict(zip(argnames, values))
                positive = parsed.get(key) is True
                if name == 'get_city_data_reply':
                    positive = parsed['cd'].get('uc') is True
                elif name == 'startEventReply':
                    positive = (parsed['e'] == 1011 and bool(parsed['r']) and
                                1011 in avatar.eventTriggerData.processingEventsClient)
                elif name == 'calcCrystalReply':
                    positive = bool(parsed['rd'])
                elif name == 'activeSkillReply':
                    positive = parsed['sk'] == 1101 and parsed['lv'] > 0
                elif name == 'replyLuckyDrawFurnitureCard':
                    info = parsed['i']
                    positive = (positive and 't' in info and 'ct' in info and
                                bool(info.get('rwd')))
                if positive:
                    allowed = True
                    if name == 'area_build_reply':
                        request = getattr(avatar, _BUILD, None)
                        setattr(avatar, _BUILD, None)
                        buildings = avatar.cityData.get_area_building(parsed.get('aid'))
                        allowed = (request is not None and request == (1, avatar.last_build_field, 2) and
                                   parsed.get('aid') == 1 and buildings is not None and
                                   buildings.get(str(request[1])) == 2)
                    if allowed:
                        owner.finish_started(avatar, roots)
                if name == 'area_build_reply' and parsed.get(key) is not True:
                    setattr(avatar, _BUILD, None)
                return result
            return decorate(old, typed_body)
        wrapper = observer(old, key, roots, name)
        owner.observers.append((cls, name, wrapper))
    city = __import__('entity.avatar_members.CityMember', fromlist=['Member']).Member
    original_request = _raw(city.area_build_request)
    def build_request(avatar, area_id, field_id, build_id, heroes, cb=None):
        if getattr(gg, 'avatar', None) is not avatar:
            return original_request(avatar, area_id, field_id, build_id, heroes, cb)
        previous = getattr(avatar, _BUILD, None)
        if not avatar.weeknumData.isFinalDay():
            # Overlap is ambiguous because the original typed reply has no request
            # identity. Refuse retirement rather than associate the wrong build.
            setattr(avatar, _BUILD, (area_id, field_id, build_id) if previous is None else False)
        try:
            return original_request(avatar, area_id, field_id, build_id, heroes, cb)
        except Exception:
            setattr(avatar, _BUILD, None)
            raise
    owner.observers.append((city, 'area_build_request', build_request))
    # Dependency imports must not have materialized any target Member meanwhile.
    if any(cls in game_object.members_cache for cls, _, _ in owner.observers):
        raise RuntimeError('Tutorial target copied during dependency imports')
    furniture_module = __import__('entity.avatar_members.FurnitureMember', fromlist=['Member'])
    furniture_cls = furniture_module.Member
    if furniture_cls in game_object.members_cache:
        raise RuntimeError('Furniture Member already copied')
    owner.modules.append(('entity.avatar_members.FurnitureMember', furniture_module, 'Member', furniture_cls))
    original_save = _raw(furniture_cls.saveFurnitureScheme)
    def save_scheme(actor, scheme_type, scheme_key, data, callback):
        target = getattr(actor, '_p7_tutorial_furniture_target', None)
        entity = data.get('e', {}).get(target[3]) if target else None
        matched = (target is not None and target[0] is actor.furnitureData and
                   target[1:3] == (scheme_type, scheme_key) and data.get('t') == scheme_type and
                   actor.furnitureData.curSchemeType == scheme_type and
                   actor.furnitureData.scheme.get(scheme_type, {}).get('cur') == scheme_key and
                   entity is not None and entity.get('id') == target[4])
        def saved(*args):
            try:
                if (args and args[0] is True and matched and
                        getattr(gg, 'avatar', None) is actor and
                        getattr(actor, '_p7_tutorial_furniture_target', None) is target and
                        actor.furnitureData is target[0]):
                    owner.finish_started(actor, (211,))
            finally:
                callback(*args)
        return original_save(actor, scheme_type, scheme_key, data, saved)
    owner.observers.append((furniture_cls, 'saveFurnitureScheme', save_scheme))
    data_module = __import__('entity.avatar_attrs.NewbeeData', fromlist=['NewbeeData'])
    data_cls = data_module.NewbeeData
    owner.modules.append(('entity.avatar_attrs.NewbeeData', data_module, 'NewbeeData', data_cls))
    original_init = _raw(data_cls.initFromDict)
    def initialized(data, payload):
        result = original_init(data, payload)
        revision = object()
        data._p7_tutorial_projection = revision
        pending = tuple(data.processing_event)
        def after_avatar_initialized():
            actor = getattr(gg, 'avatar', None)
            if (getattr(data, '_p7_tutorial_projection', None) is revision and
                    actor is not None and getattr(actor, 'newbeeData', None) is data):
                finish_skipped_build_guide(actor, data)
                owner.reconcile(actor, pending, True)
        gg.exec_delay(1, after_avatar_initialized)
        return result
    owner.observers.append((data_cls, 'initFromDict', initialized))
    for name, wrapper in owner.wrappers.items():
        setattr(member, name, wrapper)
    for cls, name, wrapper in owner.observers:
        setattr(cls, name, wrapper)
    owner.member_copies = [(name, wrapper) for cls, name, wrapper in owner.observers
                           if cls.__name__ == 'Member'] + list(owner.wrappers.items())
    _INSTALL = owner
    return owner


def install_panels():
    if _INSTALL is None:
        raise RuntimeError('Install tutorial Members first')
    owner = _INSTALL.check()
    gg = owner.gg
    if owner.panels is not None:
        for module, cls in owner.panels:
            if module.Panel is not cls:
                raise RuntimeError('Tutorial panel generation changed')
        return owner.check()
    if getattr(gg, 'avatar', None) is not None:
        raise RuntimeError('Tutorial panel installation requires no live Avatar')
    initial = len(owner.observers)
    panel_module = __import__('cocos.panels.bbs_home', fromlist=['Panel'])
    panel = panel_module.Panel
    show = _raw(panel.notify_show)
    close = _raw(panel.notify_close)
    panels = getattr(getattr(getattr(gg, 'ui', None), 'panels', None), '_panels', {})
    if 'bbs_home' in panels:
        raise RuntimeError('BBS panel already instantiated')
    def shown(instance, *args, **kwargs):
        instance._p7_tutorial_avatar = getattr(gg, 'avatar', None)
        return show(instance, *args, **kwargs)
    def closed(instance, *args, **kwargs):
        actor = getattr(instance, '_p7_tutorial_avatar', None)
        was_valid = getattr(instance, 'valid', False)
        result = close(instance, *args, **kwargs)
        if was_valid and actor is not None and getattr(gg, 'avatar', None) is actor:
            # Transparent retirement of actually started root5, not original marker4.
            owner.finish_started(actor, (5,))
        return result
    prepared = [(panel, 'notify_show', shown), (panel, 'notify_close', closed)]
    room_module = __import__('cocos.panels.city_room_danchi_new', fromlist=['Panel'])
    room_panel = room_module.Panel
    if getattr(room_panel, '_q7_furniture_ui_owner', None) is None:
        raise RuntimeError('Install furniture UI before tutorial completion')
    original_close = _raw(room_panel.on_close_click)
    def close_furniture(instance, sender, event):
        prior = instance.__dict__.get('_q7_furniture_generation')
        actor = prior[0] if prior else None
        source_ui = gg.ui
        old_layer = getattr(instance, '_layer', None)
        original_start = source_ui.actions.city_room_danchi_new.close.start
        def start(callback, *args, **kwargs):
            def ready(*cbargs, **cbkwargs):
                if (instance.__dict__.get('_q7_furniture_generation') is not prior or
                        gg.ui is not source_ui or getattr(instance, '_layer', None) is not old_layer):
                    return
                if actor is None or getattr(gg, 'avatar', None) is not actor:
                    instance.cover = False
                    instance.destroy_self_layer()
                    return
                # This point is reached only by original ENDED body. Finish before
                # its original callback reads fn, including synchronous animation.
                try:
                    owner.finish_started(actor, (253,))
                finally:
                    # Original close cleanup must run even if reliable enqueue fails.
                    # Without local fn, its original stage branch remains false.
                    return_value = callback(*cbargs, **cbkwargs)
                return return_value
            return original_start(ready, *args, **kwargs)
        close_view = _View(source_ui.actions.city_room_danchi_new.close, start=start)
        room_view = _View(source_ui.actions.city_room_danchi_new, close=close_view)
        actions = _View(source_ui.actions, city_room_danchi_new=room_view)
        ui = _View(source_ui, actions=actions)
        return _clone(original_close, _View(gg, ui=ui))(instance, sender, event)
    prepared.append((room_panel, 'on_close_click', close_furniture))
    designer_module = __import__('cocos.panels.city_room_zhuangxiu', fromlist=['Panel'])
    designer_cls = designer_module.Panel
    designer_show = _raw(designer_cls.notify_show)
    designer_refresh = _raw(designer_cls.refresh_panel)
    designer_add = _raw(designer_cls.add_furniture_data)
    def designer_shown(panel, scheme_type, scheme_key):
        panel._p7_tutorial_designer = (getattr(gg, 'avatar', None), scheme_type, scheme_key)
        return designer_show(panel, scheme_type, scheme_key)
    def refreshed(panel, *args, **kwargs):
        result = designer_refresh(panel, *args, **kwargs)
        binding = getattr(panel, '_p7_tutorial_designer', None)
        actor = getattr(gg, 'avatar', None)
        state = getattr(actor, _STATE, None) if actor else None
        items = getattr(panel, 'panel_furnitures', ())
        if (binding and binding[0] is actor and state and 211 in state['started'] and
                len(items) > 4 and getattr(panel, 'valid', False)):
            item = items[4]
            furniture = designer_module.ITEM_DATA.data.get(item.itemid, {}).get('furniture')
            # Public TV-cabinet models, never mistake guidance list index4 for ID4.
            prior_target = getattr(actor, '_p7_tutorial_furniture_target', None)
            if (furniture in (51, 239) and
                    (prior_target is None or prior_target[0] is not actor.furnitureData or
                     prior_target[5] is not binding)):
                actor._p7_tutorial_furniture_target = (actor.furnitureData, binding[1], binding[2], item.key, furniture, binding)
        return result
    def added(panel, entity_key, furniture):
        result = designer_add(panel, entity_key, furniture)
        binding = getattr(panel, '_p7_tutorial_designer', None)
        actor = getattr(gg, 'avatar', None)
        target = getattr(actor, '_p7_tutorial_furniture_target', None) if actor else None
        created = getattr(panel, 'furnitures', {}).get(entity_key)
        if (binding and binding[0] is actor and target and target[5] is binding and
                target[0] is actor.furnitureData and not target[3] and entity_key and
                created is not None and created.selected and created.key == entity_key and
                created.furnitureid == target[4]):
            # The original add succeeded and supplied the real generated entity key.
            actor._p7_tutorial_furniture_target = target[:3] + (entity_key,) + target[4:]
        return result
    prepared.extend(((designer_cls, 'notify_show', designer_shown),
                     (designer_cls, 'add_furniture_data', added),
                     (designer_cls, 'refresh_panel', refreshed)))
    owner.modules.append(('cocos.panels.city_room_zhuangxiu', designer_module, 'Panel', designer_cls))
    owner.modules.extend((('cocos.panels.bbs_home', panel_module, 'Panel', panel),
                          ('cocos.panels.city_room_danchi_new', room_module, 'Panel', room_panel)))
    owner.observers.extend(prepared)
    owner.panels = ((panel_module, panel), (room_module, room_panel), (designer_module, designer_cls))
    for cls, name, wrapper in owner.observers[initial:]:
        setattr(cls, name, wrapper)
    return owner
