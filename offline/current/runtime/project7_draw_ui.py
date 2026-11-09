# -*- coding: ascii -*-
"""Hide new tutorial draw entries; retain original pending-file UI bodies.
Install after clean/collection, before target panels bind callbacks. No profile,
clock/table mutation, Member edits, RPC success fabrication or server policy.
Historical pools additionally require the per-account open-pool selection
(p7_pool_selection_<sha256(identity)>.json, default empty, 12-pool cap); an
open file always stays reachable.
"""
import sys
import os
import types
import json
import hashlib

_NEWBIE = 354
_NORMAL = 1
# Always reachable stock pools: the memory gap, the treasure draw (id 5, the
# treasure prayer screen), the friend pool and the newbie pool. Every other
# draw-table row (treasure selection, furniture pools, special recommendations,
# event pools, and the other wish gaps) is a limited pool that the player turns
# on from the backpack editor.
_BASELINE = frozenset((_NORMAL, 5, 131, _NEWBIE))
_LOCAL_FREE_TYPES = frozenset((_NORMAL,))
_MARKER = '_q7_draw_ui_owner'
_TARGETS = (('cocos.panels.card_tab', 'Panel'),
            ('cocos.panels.card_box', 'Panel'),
            ('game_scene.city_chouka', 'Scene'))
_METHODS = ((0, 'init_button_comp'), (0, 'on_chouka_btn_click'),
            (0, 'refresh_open_cost_coin_and_btn'), (0, 'on_open_go_click'),
            (0, '_on_open_go_click'), (0, '_on_activity_click'),
            (1, '_on_request_luckydrawfile'), (1, '_on_request_luckydrawallfile'),
            (1, 'refresh_open_cost_coin_and_btn'), (1, 'on_open_click'),
            (1, 'on_open_all_click'), (1, '_on_open_click'),
            (1, 'notify_open_file'), (1, 'on_card_model_rotate'),
            (1, 'set_is_open_file'), (1, 'enter_scene'), (1, 'leave_scene'),
            (2, 'change_scene_to_activity'),
            (2, 'change_scene_to_chouka_main'))

_HISTORY_ASSET = 'b439ab44280a959cab8836595b65489fee3fd8482609ed3caa55477a66fd5c16'
_HISTORY_POLICY = 'ed998856a7970089b4a5d89a15720b0c0bb10cd2cd2cbe97f4b8a52c62af87a3'
_HISTORY_METHODS = ((0, 'on_open_click'), (0, 'on_open_all_click'),
    (0, 'set_card_gift'), (0, 'update_avatar_info'),
    (1, '_do_init_card_info'),
    (1, 'on_card_once_click'), (1, 'on_card_left_or_ten_click'),
    (1, 'on_quit_click'), (1, 'set_card_gift'), (1, 'update_avatar_info'))
try:
    _TEXT = (basestring,)
    _INT = (int, long)
except NameError:
    _TEXT = (str, bytes)
    _INT = (int,)

# Per-account open-pool selection, a separate layer above the embedded history
# policy.  White-night-hall (baiye) only builds the pools named here, so the
# default is empty and the stock non-history pools are untouched.  The file is
# ignored, never surfaced, when it is unreadable or over the cap.
_POOL_CAP = 12
_POOL_PREFIX = 'p7_pool_selection_'
_POOL_CACHE = {}


def _pool_identity():
    """avatar.account / an, mirroring the inventory editor's identity text."""
    try:
        module = __import__('gg')
    except Exception:
        return ''
    avatar = getattr(module, 'avatar', None)
    if avatar is None:
        return ''
    for name in ('account', 'an'):
        try:
            value = getattr(avatar, name, None)
            if value is not None and value != '':
                return u'%s:%s' % (name, value)
        except Exception:
            pass
    return ''


def _pool_path(identity):
    if not identity:
        return ''
    try:
        import game3d
        root = game3d.get_doc_dir()
    except Exception:
        return ''
    try:
        digest = hashlib.sha256(identity.encode('ascii')).hexdigest()
    except Exception:
        return ''
    return os.path.join(root, _POOL_PREFIX + digest + '.json')


def _pool_ids_valid(values):
    if not isinstance(values, (list, tuple, frozenset, set)):
        return None
    try:
        raw = list(values)
    except Exception:
        return None
    if len(raw) > _POOL_CAP:
        return None
    for value in raw:
        if type(value) not in _INT or value <= 0 or value > 2147483647:
            return None
    if len(set(raw)) != len(raw):
        return None
    return sorted(raw)


def _pool_read(identity):
    path = _pool_path(identity)
    if not path:
        return frozenset()
    try:
        with open(path, 'rb') as stream:
            data = json.loads(stream.read())
    except Exception:
        return frozenset()
    if (not isinstance(data, dict) or set(data) != set(('v', 'session', 'ids')) or
            data.get('v') != 1 or data.get('session') != identity):
        return frozenset()
    ids = _pool_ids_valid(data.get('ids'))
    if ids is None:
        return frozenset()
    return frozenset(ids)


def pool_selection(identity=None):
    """Selected historical pool ids; empty when unreadable or identity-less."""
    identity = _pool_identity() if identity is None else identity
    if not identity:
        return frozenset()
    cached = _POOL_CACHE.get(identity)
    if cached is None:
        cached = _pool_read(identity)
        _POOL_CACHE[identity] = cached
    return cached


def _pool_write(identity, ids):
    target = _pool_path(identity)
    if not target:
        return False
    temporary = target + '.tmp'
    try:
        with open(temporary, 'wb') as stream:
            stream.write(json.dumps({'v': 1, 'session': identity, 'ids': list(ids)},
                                    sort_keys=True, separators=(',', ':')).encode('ascii'))
            stream.flush()
            os.fsync(stream.fileno())
        os.rename(temporary, target)
        return True
    except Exception:
        try:
            os.unlink(temporary)
        except Exception:
            pass
        return False


def set_pool_selection(ids, identity=None):
    """Replace the selection atomically; over-cap or identity-less is refused."""
    identity = _pool_identity() if identity is None else identity
    if not identity:
        return False
    values = _pool_ids_valid(ids)
    if values is None:
        return False
    if not _pool_write(identity, values):
        return False
    _POOL_CACHE[identity] = frozenset(values)
    return True


def _history_policy(text):
    if text is None:
        return None
    if not isinstance(text, _TEXT):
        raise ValueError('Embedded history policy text required')
    binary = text.encode('ascii') if not isinstance(text, bytes) else text
    data = json.loads(binary)
    if (not isinstance(data, dict) or set(data) != set(('schema', 'asset_sha256', 'ready_ids', 'all_history_ids')) or
            data['schema'] != 'project7-history-ui-v1' or data['asset_sha256'] != _HISTORY_ASSET):
        raise ValueError('History policy version changed')
    for name in ('ready_ids', 'all_history_ids'):
        values = data[name]
        if (not isinstance(values, list) or any(type(value) not in _INT or value <= 0 or value > 2147483647 for value in values) or
                values != sorted(set(values))):
            raise ValueError('History policy IDs invalid')
    if not set(data['ready_ids']).issubset(data['all_history_ids']) or set(data['all_history_ids']).intersection((1, 354, 484)):
        raise ValueError('History policy scope invalid')
    canonical = json.dumps(data, sort_keys=True, separators=(',', ':')).encode('ascii')
    if hashlib.sha256(canonical).hexdigest() != _HISTORY_POLICY:
        raise ValueError('History policy projection changed')
    return data


def _raw(fn):
    return getattr(fn, 'im_func', getattr(fn, '__func__', fn))


def _globals(fn):
    return getattr(fn, 'func_globals', getattr(fn, '__globals__', {}))


def _cell(value):
    def captured():
        return value
    return getattr(captured, 'func_closure', getattr(captured, '__closure__', None))[0]


def _clone(original, aliases, gg, cancel_body=False):
    namespace = dict(_globals(original))
    namespace.update(aliases)
    code = getattr(original, 'func_code', getattr(original, '__code__', None))
    defaults = getattr(original, 'func_defaults', getattr(original, '__defaults__', None))
    closure = getattr(original, 'func_closure', getattr(original, '__closure__', None))
    if closure:
        cells = list(closure)
        # checkMultiClick captures the original body as func. Cloning only its
        # outer wrapper would leave the ct18 recovery gate on the real avatar.
        for index, name in enumerate(code.co_freevars):
            value = cells[index].cell_contents
            if name in ('func', 'f') and isinstance(value, types.FunctionType):
                if _globals(value).get('gg') is not gg:
                    raise RuntimeError('Draw UI decorated body has stale gg')
                cells[index] = _cell((lambda *args, **kwargs: None) if cancel_body else _clone(value, aliases, gg))
        closure = tuple(cells)
    return types.FunctionType(code, namespace, original.__name__, defaults, closure)


class _View(object):
    def __init__(self, source, **aliases):
        object.__setattr__(self, '_source', source)
        object.__setattr__(self, '_aliases', frozenset(aliases))
        self.__dict__.update(aliases)

    def __getattr__(self, name):
        return getattr(self._source, name)

    def __setattr__(self, name, value):
        if name.startswith('_') and name in ('_source', '_aliases', '_state'):
            object.__setattr__(self, name, value)
        elif name in self._aliases:
            raise RuntimeError('Draw UI scoped alias is read only')
        else:
            setattr(self._source, name, value)


class _HistoryRows(object):
    def __init__(self, source, state):
        self.source, self._state = source, state

    def get(self, key, default=None):
        if key == _NEWBIE and not self._state.pending():
            return default
        if not self._state.allowed(key):
            return default
        data = self.source.get(key, default)
        if data is not default:
            data = dict(data)
            if key in self._state.history:
                data.pop('isRecommend', None)
                if key in self._state.ready:
                    data['show_level_lower_bound'] = 1
                    data['show_level_upper_bound'] = 110
            data = self._state.panel_row(data)
        return data

    def iteritems(self):
        return iter((key, self.get(key)) for key in self.source
                    if key != _NEWBIE and self._state.allowed(key))

    def items(self):
        return list(self.iteritems())

    def __getitem__(self, key):
        marker = object()
        value = self.get(key, marker)
        if value is marker:
            raise KeyError(key)
        return value

    def __iter__(self):
        return iter(key for key, value in self.iteritems())

    def keys(self):
        return list(iter(self))

    def values(self):
        return [value for key, value in self.iteritems()]

    def __contains__(self, key):
        return key in self.keys()


class _HistoryData(_View):
    _FREE_GUARDS = frozenset(('canOpenFile', 'canOpenCard', 'canOpenCardByConsume',
        'checkFileAndOpenAllCostByConsume', 'checkFileAndOpenAllCost',
        'checkLeftAllCardsCostByConsume', 'checkLeftAllCardsCost'))

    def __init__(self, source, state):
        _View.__init__(self, source)
        self._state = state

    def __getattr__(self, name):
        if self._source is not self._state.current().avatar.luckyDrawData:
            raise RuntimeError('History draw data generation changed')
        if name == 'newbie_pool_stay' and self._state.pending():
            return True
        original = getattr(self._source, name)
        if name not in self._FREE_GUARDS and name not in ('getLuckyDrawConsume', 'getOpenConsume'):
            if not callable(original):
                return original
            def delegated(*args, **kwargs):
                if self._source is not self._state.current().avatar.luckyDrawData:
                    raise RuntimeError('History draw data generation changed')
                return original(*args, **kwargs)
            return delegated
        def wrapped(*args, **kwargs):
            self._state.current()
            if self._source is not self._state.gg.avatar.luckyDrawData:
                raise RuntimeError('History draw data generation changed')
            draw_type = args[0] if args else kwargs.get('_type', _NORMAL)
            if draw_type in self._state.ready:
                if name in self._FREE_GUARDS:
                    return True
                if name == 'getOpenConsume':
                    return 0
                if name == 'getLuckyDrawConsume':
                    namespace = _globals(_raw(original))
                    once = namespace['const'].LuckyDrawConsumeStyle.STYLE_ONCE
                    style = args[1] if len(args) > 1 else kwargs.get('_style', once)
                    return [(0, 0)] if style == once else []
            elif draw_type in _LOCAL_FREE_TYPES:
                if name == 'canOpenCard':
                    if not self._source.getIsOpenCard(draw_type):
                        return original(*args, **kwargs)
                    return True
                if name == 'canOpenCardByConsume':
                    return True
                if name == 'canOpenFile':
                    if self._source.getIsOpenCard(draw_type):
                        return original(*args, **kwargs)
                    return True
                if name == 'checkFileAndOpenAllCost':
                    if self._source.getIsOpenCard(draw_type):
                        return original(*args, **kwargs)
                    return True
                if name == 'checkFileAndOpenAllCostByConsume':
                    return True
                if name == 'checkLeftAllCardsCost':
                    if not self._source.getIsOpenCard(draw_type):
                        return original(*args, **kwargs)
                    return True
                if name == 'checkLeftAllCardsCostByConsume':
                    if not self._source.getIsOpenCard(draw_type):
                        return original(*args, **kwargs)
                    return True
                if name == 'getOpenConsume':
                    return 0
                if name == 'getLuckyDrawConsume':
                    namespace = _globals(_raw(original))
                    once = namespace['const'].LuckyDrawConsumeStyle.STYLE_ONCE
                    style = args[1] if len(args) > 1 else kwargs.get('_style', once)
                    return [(0, 0)] if style == once else []
            return original(*args, **kwargs)
        return wrapped


_REQUEST_LOCKS = frozenset(('requestLuckyDrawFile', 'requestLuckyDrawCard',
    'quitFile', 'requestLuckyDrawFileAndOpenAll', 'requestLuckyDrawAllLeftCard'))
_GESTURE_FIELDS = frozenset(('cur_sender', 'cur_panel', 'multi_click'))


class _RequestUI(object):
    """Per cloned call: original UI identity + reset_lock dictionary epoch.
    The original RPC callback is rebound to its own acquired lease, so a second
    callback cannot consume a sibling request's count/recon_lock contribution.
    """
    def __init__(self, state, avatar, draw_type=None):
        self.state, self.avatar, self.source = state, avatar, state.gg.ui
        self.draw_type = draw_type
        self._request_data = getattr(avatar, 'luckyDrawData', None)
        self.leases = []
        self.epoch = getattr(self.source, '_lock', None)
        self.cancel = getattr(state.gg, 'exec_cancel', None)

    def __getattr__(self, name):
        # checkMultiClick keeps its press ledger on gg.ui. A cloned view must
        # read that ledger from the real UI or BEGAN and ENDED use different
        # views and ENDED never sees the retained sender.
        return getattr(self.source, name)

    def __setattr__(self, name, value):
        if name in _GESTURE_FIELDS:
            setattr(self.source, name, value)
        else:
            object.__setattr__(self, name, value)

    def lock(self, key='default', show_panel=True):
        if key not in _REQUEST_LOCKS:
            return self.source.lock(key, show_panel)
        if (self.state.current().avatar is not self.avatar or
                getattr(self.avatar, 'luckyDrawData', None) is not self._request_data or self.state.gg.ui is not self.source or
                getattr(self.source, '_lock', None) is not self.epoch):
            raise RuntimeError('History request owner generation changed')
        epoch = getattr(self.source, '_lock', None)
        if not isinstance(epoch, dict):
            raise RuntimeError('History request lock ABI changed')
        if self.draw_type is not None and key != 'quitFile':
            self.state.check_request_guard(self.draw_type, self.avatar)
        result = self.source.lock(key, show_panel)
        self.leases.append({'key': key, 'show': show_panel, 'epoch': epoch,
                            'bound': False, 'released': False,
                            'wait': getattr(self.source.panels, 'wait', None)})
        return result

    def unlock(self, key='default', show_panel=True):
        if key not in _REQUEST_LOCKS:
            return self.source.unlock(key, show_panel)
        # Production request callbacks are bound at the original send boundary.
        # No matching acquire means no authority to release another request.
        for lease in reversed(self.leases):
            if lease['key'] == key and not lease['bound'] and not lease['released']:
                return self.release(lease, key)
        return None

    def release(self, lease, key):
        if lease['released'] or lease['key'] != key:
            return None
        lease['released'] = True
        current_gg = sys.modules.get('gg')
        if (getattr(current_gg, 'ui', None) is not self.source or
                getattr(self.state.gg, 'ui', None) is not self.source):
            self.retire_wait(lease)
            return None
        if getattr(self.source, '_lock', None) is not lease['epoch']:
            return None
        # Avatar may have changed in the SAME UI/reset epoch. This lease still
        # owns one actual acquire and must clean it up exactly once.
        return self.source.unlock(key, lease['show'])

    def retire_wait(self, lease):
        # The old wait's timer closes over global gg and could reset the new UI.
        # Its destroy/unlock path also accesses current panel caches. Retire
        # only this old wait's scheduling/visibility; its owner owns teardown.
        wait = lease.get('wait')
        if wait is None:
            return
        if callable(self.cancel):
            for name in ('show_desc_timer', 'disconnect_timer'):
                handle = getattr(wait, name, None)
                if handle:
                    self.cancel(handle)
                    setattr(wait, name, None)
        node = getattr(wait, '_node', None)
        if node is not None and getattr(wait, 'valid', False):
            node.setVisible(False)

    def bind_callback(self, callback):
        lease = next((item for item in reversed(self.leases)
                      if not item['bound'] and not item['released']), None)
        if lease is None:
            return callback
        lease['bound'] = True
        callback_gg = _globals(callback).get('gg')
        scoped = _View(callback_gg, ui=_ReleaseUI(self, lease))
        return _clone(callback, {'gg': scoped}, self.state.gg)


class _ReleaseUI(object):
    def __init__(self, owner, lease):
        self.owner, self.lease = owner, lease

    def __getattr__(self, name):
        return getattr(self.owner.source, name)

    def unlock(self, key='default', show_panel=True):
        return self.owner.release(self.lease, key)


def _bind_request_callback(callback):
    if not isinstance(callback, types.FunctionType):
        return callback
    gg = _globals(callback).get('gg')
    ui = getattr(gg, 'ui', None)
    return ui.bind_callback(callback) if isinstance(ui, _RequestUI) else callback


class _HistoryAvatar(_View):
    _NEW_GROUP = frozenset(('requestLuckyDrawFile', 'doRequestLuckyDrawFile',
        'requestLuckyDrawFileAndOpenAll', 'doRequestLuckyDrawFileAndOpenAll'))

    def __init__(self, source, state):
        _View.__init__(self, source, luckyDrawData=_HistoryData(source.luckyDrawData, state))
        self._state = state

    def __getattr__(self, name):
        original = getattr(self._source, name)
        raw = _raw(original)
        if not isinstance(raw, types.FunctionType) or not (hasattr(original, 'im_self') or hasattr(original, '__self__')):
            return original
        def wrapped(*args, **kwargs):
            self._state.current()
            if self._source is not self._state.gg.avatar:
                raise RuntimeError('History Avatar generation changed')
            draw_type = args[0] if args else kwargs.get('_type', _NORMAL)
            guarded = name in self._NEW_GROUP or name in ('requestFile', 'requestLuckyDrawCard', 'requestLuckyDrawAllLeftCard')
            requested = ((args[1] if len(args)>1 else kwargs.get('_type',_NORMAL)) if name=='requestLuckyDrawCard' else draw_type) if guarded else None
            if guarded:self._state.check_request_guard(requested,self._source)
            if name in self._NEW_GROUP and draw_type in self._state.history:
                if not self._state.allowed(draw_type):
                    return False
                if self._state.pending(draw_type):
                    return self.requestFile(draw_type)
            if name == 'isNewbieLuckyAvailable' and self._state.pending():
                return True
            if name == 'checkDrawInTime':
                if draw_type not in _BASELINE and self._state.allowed(draw_type):
                    return True
                if draw_type == _NEWBIE and self._state.pending():
                    return True
            if name == 'checkActivity' and draw_type in self._state.history and self._state.allowed(draw_type):
                namespace = _globals(raw)
                hero_pool = namespace['const'].CardPoolType.TYPE_HERO_TREASURE
                pool_type = args[1] if len(args) > 1 else kwargs.get('pool_type', hero_pool)
                return pool_type == hero_pool and namespace['CHOUKA_INFO_DATA'].data.get(draw_type, {}).get('poolType') == hero_pool
            if name in ('requestFile', 'requestQuitFile', 'requestLuckyDrawAllLeftCard', 'requestLuckyDrawCard'):
                requested = (args[1] if len(args) > 1 else kwargs.get('_type', _NORMAL)) if name == 'requestLuckyDrawCard' else draw_type
                if requested in self._state.history and not self._state.pending(requested):
                    return False
            if name in ('callServerMethod', 'callServerMethodReliable') and 'callback' in kwargs:
                kwargs = dict(kwargs)
                kwargs['callback'] = _bind_request_callback(kwargs['callback'])
            aliases = self._state.history_aliases(_globals(raw), self, requested)
            return _clone(raw, aliases, self._state.gg)(self, *args, **kwargs)
        return wrapped


class _Installation(object):
    def __init__(self, modules, classes, gg, policy=None):
        self.policy = policy
        self.ready = frozenset(policy['ready_ids']) if policy else frozenset()
        self.history = frozenset(policy['all_history_ids']) if policy else frozenset()
        self.modules, self.classes, self.gg = modules, classes, gg
        self.records = []
        self.missing_panels = set()
        self.request_guards = {}
        self.request_guard_owners = []

    def current(self):
        if sys.modules.get('gg') is not self.gg:
            raise RuntimeError('Draw UI gg generation changed')
        for module, cls, (name, attribute) in zip(self.modules, self.classes, _TARGETS):
            if (sys.modules.get(name) is not module or getattr(module, attribute) is not cls or
                    cls.__dict__.get(_MARKER) is not self):
                raise RuntimeError('Draw UI class generation changed')
        return self.gg

    def register_request_guard(self, owner, ids, callback):
        self.current()
        ids = tuple(ids)
        bound = getattr(callback, 'im_self', getattr(callback, '__self__', None))
        expected = getattr(owner, 'before_request', None)
        if (bound is not owner or _raw(callback) is not _raw(expected) or
                getattr(owner, 'draw_owner', None) is not self or not ids or
                any(not isinstance(t, int) or isinstance(t, bool) for t in ids) or len(set(ids)) != len(ids)):
            raise RuntimeError('History request guard ABI changed')
        policy = getattr(owner, 'policy', {})
        if not set(ids).issubset(set(policy.get('verified_ids', ())) & set(policy.get('detail_ids', ())) & self.history):
            raise RuntimeError('History request guard scope unverified')
        ids = tuple(sorted(ids))
        for prior, prior_ids, raw in self.request_guard_owners:
            if prior is owner:
                if prior_ids == ids and raw is _raw(callback):return owner
                raise RuntimeError('History request guard registration changed')
        if any(t in self.request_guards for t in ids):raise RuntimeError('History request guard scope conflict')
        self.request_guard_owners.append((owner, ids, _raw(callback)))
        for t in ids:self.request_guards[t] = (owner, callback, _raw(callback))
        return owner

    def check_request_guard(self, draw_type, avatar):
        gg = self.current()
        if avatar is not gg.avatar:raise RuntimeError('History request guard avatar changed')
        record = self.request_guards.get(draw_type)
        if record is None:return None
        owner, callback, raw = record
        if (getattr(owner, 'draw_owner', None) is not self or
                getattr(callback, 'im_self', getattr(callback, '__self__', None)) is not owner or
                _raw(getattr(owner, 'before_request', None)) is not raw):
            raise RuntimeError('History request guard owner changed')
        return callback(draw_type, avatar)

    def pending(self, draw_type=_NEWBIE):
        return bool(self.current().avatar.luckyDrawData.getIsOpenCard(draw_type))

    def is_local_free(self, draw_type):
        return draw_type in self.ready or draw_type in _LOCAL_FREE_TYPES

    def selection(self):
        return pool_selection()

    def set_selection(self, ids):
        return set_pool_selection(ids)

    def allowed(self, draw_type):
        if draw_type == _NEWBIE:
            return self.pending()
        if type(draw_type) not in _INT or draw_type <= 0:
            # Unknown draw type (panel not initialised yet): keep the stock
            # path instead of silently blocking it.
            return True
        if draw_type in _BASELINE:
            return True
        # An open file must stay reachable, selected or not, or a started draw
        # would be stranded.  Everything else is admitted only when the account
        # opened it in the editor; the cost-free guard stays tied to ready.
        if self.pending(draw_type):
            return True
        if draw_type in self.history:
            return draw_type in self.ready and draw_type in pool_selection()
        # Draw-table rows outside the history catalog (treasure selection,
        # furniture pools, special recommendations, event pools) are limited
        # pools too: turning off the limited pools must hide them.
        return draw_type in pool_selection()

    def hideable(self):
        """Every limited pool id the draw screen can list, baseline excluded."""
        cached = getattr(self, '_hideable_ids', None)
        if cached is not None:
            return cached
        ids = set(self.history)
        try:
            module = __import__('com.data.cdata.chouka_info', fromlist=['data'])
            table = getattr(module, 'data', None)
            if isinstance(table, dict):
                ids.update(int(key) for key in table
                           if type(key) in _INT and key > 0)
        except Exception:
            pass
        ids = frozenset(value for value in ids if value not in _BASELINE)
        self._hideable_ids = ids
        return ids

    def panel_row(self, row):
        # The original dynamic panel alias map, not a per-pool replacement.
        index = row.get('room_enter_index')
        if not index or index == 7:
            return row
        module = sys.modules.get('C_file')
        if module is None:
            module = getattr(sys.modules.get('game3d'), 'C_file', None)
        finder = getattr(module, 'find_res_file', None)
        if finder is None:
            return row
        aliases = {-1: 'card_activity_61', -2: 'card_zixuan', -3: 'card_activity_62'}
        path = 'cocos/%s.csb' % aliases.get(index, 'card_activity_%d' % index)
        try:
            found = finder(path, '')
        except Exception:
            return row
        if not found:
            self.missing_panels.add(path)
            row['room_enter_index'] = 7
        return row

    def history_aliases(self, namespace, avatar=None, draw_type=None):
        if namespace.get('gg', self.gg) is not self.current():
            raise RuntimeError('History method globals have stale gg')
        if avatar is None:
            avatar = _HistoryAvatar(self.gg.avatar, self)
        aliases = {'gg': _View(self.gg, avatar=avatar, ui=_RequestUI(self, avatar._source, draw_type))}
        if 'CHOUKA_INFO_DATA' in namespace:
            table = namespace['CHOUKA_INFO_DATA']
            aliases['CHOUKA_INFO_DATA'] = _View(table, data=_HistoryRows(table.data, self))
        return aliases

    def cancel_stale_jump(self, menu=False):
        gg = self.current()
        params = getattr(gg, 'PanelJumpjumpcbParams', ())
        if (getattr(gg, 'PanelJumpjumpcb', None) in ('_on_request_luckydrawfile', '_on_request_luckydrawallfile') and
                isinstance(params, (tuple, list)) and params and
                (not self.allowed(params[0]) or (menu and params[0] == _NEWBIE))):
            gg.PanelJumpjumpcb = None
            gg.PanelJumpjumpcbParams = ()

    def normalize(self, draw_type):
        if not self.allowed(draw_type):
            self.cancel_stale_jump()
            return _NORMAL
        return draw_type

    def menu_type(self, draw_type):
        if draw_type == _NEWBIE:
            return _NORMAL
        return self.normalize(draw_type)

    def call(self, original, args, kwargs, tab=False, cancel_body=False):
        gg = self.current()
        namespace = _globals(original)
        if namespace.get('gg') is not gg:
            raise RuntimeError('Draw UI original globals have stale gg')
        aliases = {}
        pending = self.pending()
        if self.policy:
            aliases.update(self.history_aliases(namespace))
        elif tab:
            avatar = gg.avatar
            if pending:
                # Preserve ct and every original branch; expose recovery-only
                # availability even at ct18 or after the activity window.
                data = _View(avatar.luckyDrawData, newbie_pool_stay=True)
                check_time = avatar.checkDrawInTime
                avatar = _View(avatar, luckyDrawData=data,
                               isNewbieLuckyAvailable=lambda: True,
                               checkDrawInTime=lambda t: True if t == _NEWBIE else check_time(t))
                aliases['gg'] = _View(gg, avatar=avatar)
            if 'CHOUKA_INFO_DATA' in namespace:
                table = namespace['CHOUKA_INFO_DATA']
                aliases['CHOUKA_INFO_DATA'] = _View(table, data=_HistoryRows(table.data, self))
        return _clone(original, aliases, gg, cancel_body)(*args, **kwargs)

    def bind(self, index, name, make):
        cls = self.classes[index]
        original = _raw(getattr(cls, name))
        replacement = make(original)
        replacement.__dict__.update(getattr(original, '__dict__', {}))
        replacement._q7_draw_ui_wrapped = self
        setattr(cls, name, replacement)
        self.records.append((cls, name, replacement, original))

    def apply(self):
        state = self
        def init(original):
            def wrapped(panel, force_type):
                state.cancel_stale_jump(menu=True)
                if state.policy:
                    force_type = state.menu_type(force_type or _NORMAL)
                else:
                    force_type = state.menu_type(force_type)
                return state.call(original, (panel, force_type), {}, tab=True)
            return wrapped
        def select(original):
            def wrapped(panel, draw_type):
                return state.call(original, (panel, state.menu_type(draw_type)), {})
            return wrapped
        def tab(original):
            def wrapped(*args, **kwargs):
                result = state.call(original, args, kwargs, tab=True)
                panel = args[0]
                if state.policy and state.is_local_free(getattr(panel, 'draw_type', None)) and hasattr(panel, 'once_cost_1_cost_txt'):
                    panel.once_cost_1_cost_txt.setString(u'\u514d\u8d39')
                return result
            return wrapped
        def enter(original):
            def wrapped(panel, *args, **kwargs):
                if not state.allowed(panel.draw_type):
                    state.cancel_stale_jump()
                    return None
                return state.call(original, (panel,) + args, kwargs, tab=True)
            return wrapped
        def go(original):
            def wrapped(panel, *args, **kwargs):
                draw_type = panel.get_luckyDraw_type() if hasattr(panel, 'get_luckyDraw_type') else panel.draw_type
                blocked = not state.allowed(draw_type)
                if blocked:
                    state.cancel_stale_jump()
                    code = getattr(original, 'func_code', getattr(original, '__code__', None))
                    if 'func' not in code.co_freevars:
                        return None
                # checkMultiClick still consumes/release its original touch;
                # only its captured blocked draw body is cancelled.
                return state.call(original, (panel,) + args, kwargs,
                                  tab=True, cancel_body=blocked)
            return wrapped
        def activity(original):
            def wrapped(panel, draw_type):
                if not state.allowed(draw_type):
                    state.cancel_stale_jump()
                    return None
                return state.call(original, (panel, draw_type), {})
            return wrapped
        def jump(original):
            def wrapped(panel, draw_type=_NORMAL, *args, **kwargs):
                if not state.allowed(draw_type):
                    state.cancel_stale_jump()
                    return None
                return state.call(original, (panel, draw_type) + args, kwargs)
            return wrapped
        _MISSING = object()
        def _hide_item_box(panel):
            try:
                panel.item_box_panel.setVisible(False)
            except Exception:
                pass
        def _orb_scene(original):
            try:
                namespace = _globals(original)
                const = namespace.get('const')
                return state.current().city_container.get_scene_by_key(const.SCENE_SUMMON)
            except Exception:
                return None
        def _phase_valid(panel, phase, original):
            if phase is None:
                return False
            try:
                gg = state.current()
                return (getattr(panel, '_q7_orb_phase', None) is phase and
                        phase.get('panel') is panel and
                        phase.get('avatar') is gg.avatar and
                        phase.get('data') is getattr(gg.avatar, 'luckyDrawData', None) and
                        phase.get('scene') is _orb_scene(original) and
                        phase.get('scope') == getattr(panel, 'scene_type', None) and
                        phase.get('draw_type') == getattr(panel, 'draw_type', None))
            except Exception:
                return False
        def _clear_invalid(panel, original):
            phase = getattr(panel, '_q7_orb_phase', None)
            if phase is not None and not _phase_valid(panel, phase, original):
                _restore_orb(panel, phase)
                return None
            return phase
        def _scope_supported(panel):
            return getattr(panel, 'scene_type', None) in ('normal', 'activity')
        def _restore_orb(panel, phase):
            saved = phase.get('auto_scroll', _MISSING)
            try:
                delattr(panel, '_q7_orb_phase')
            except Exception:
                pass
            if saved is not _MISSING:
                try:
                    panel.model_card_auto_scroll(saved)
                except Exception:
                    pass
        def orb_open(original):
            def wrapped(panel, enable, *args, **kwargs):
                if not _scope_supported(panel):
                    phase = _clear_invalid(panel, original)
                    if phase is not None:
                        _restore_orb(panel, phase)
                    return state.call(original, (panel, enable) + args, kwargs)
                phase = _clear_invalid(panel, original)
                if enable:
                    # Restore the panel's own pre-orb scroll before the original
                    # True call; a synchronous requestFile callback must see it.
                    if phase is not None:
                        saved = phase.get('auto_scroll', _MISSING)
                        if saved is not _MISSING and hasattr(panel, '_f7_previous_auto_scroll'):
                            # If the legacy backend hook is present, keep its
                            # cached value in sync so it cannot overwrite the
                            # restored value during this same True call.
                            panel._f7_previous_auto_scroll = saved
                        _restore_orb(panel, phase)
                    return state.call(original, (panel, enable) + args, kwargs)
                created = phase is None
                if created:
                    gg = state.current()
                    phase = {
                        'auto_scroll': getattr(panel, 'auto_scroll', _MISSING),
                        'panel': panel,
                        'avatar': gg.avatar,
                        'data': getattr(gg.avatar, 'luckyDrawData', None),
                        'scene': _orb_scene(original),
                        'scope': getattr(panel, 'scene_type', None),
                        'draw_type': getattr(panel, 'draw_type', None),
                    }
                    try:
                        setattr(panel, '_q7_orb_phase', phase)
                    except Exception:
                        phase = None
                try:
                    if hasattr(panel, 'model_card_auto_scroll'):
                        panel.model_card_auto_scroll(False)
                    result = state.call(original, (panel, enable) + args, kwargs)
                except BaseException:
                    if created and phase is not None:
                        _restore_orb(panel, phase)
                    raise
                if phase is not None and _phase_valid(panel, phase, original):
                    _hide_item_box(panel)
                return result
            return wrapped
        def orb_rotate(original):
            def wrapped(panel, *args, **kwargs):
                phase = _clear_invalid(panel, original)
                try:
                    return state.call(original, (panel,) + args, kwargs)
                finally:
                    if phase is not None and _phase_valid(panel, phase, original):
                        _hide_item_box(panel)
            return wrapped
        def orb_set_open(original):
            def wrapped(panel, enable, *args, **kwargs):
                phase = _clear_invalid(panel, original)
                if phase is not None and enable and getattr(panel, 'is_open_file', False):
                    # The original setter would refresh the card box and show
                    # model_card_panel even though the orb owns the UI. Defer
                    # this pure UI refresh until original notify_open_file(True)
                    # clears the phase and its synchronous requestFile callback
                    # runs the normal setter.
                    phase['deferred_set_open'] = True
                    _hide_item_box(panel)
                    return None
                try:
                    return state.call(original, (panel, enable) + args, kwargs)
                finally:
                    if phase is not None and _phase_valid(panel, phase, original):
                        _hide_item_box(panel)
            return wrapped
        def orb_enter(original):
            def wrapped(panel, *args, **kwargs):
                phase = getattr(panel, '_q7_orb_phase', None)
                if phase is not None:
                    _restore_orb(panel, phase)
                return state.call(original, (panel,) + args, kwargs)
            return wrapped
        def orb_leave(original):
            def wrapped(panel, *args, **kwargs):
                try:
                    return state.call(original, (panel,) + args, kwargs)
                finally:
                    phase = getattr(panel, '_q7_orb_phase', None)
                    if phase is not None:
                        _restore_orb(panel, phase)
            return wrapped
        def box_refresh(original):
            def wrapped(panel):
                if not state.allowed(panel.get_luckyDraw_type()):
                    state.cancel_stale_jump()
                    for name in ('btn_open_once', 'btn_open_all', 'open_light'):
                        getattr(panel, name).setVisible(False)
                    return None
                # A pending old group keeps every original button/state path.
                return state.call(original, (panel,), {}, tab=True)
            return wrapped
        def scene_activity(original):
            def wrapped(scene, _type):
                if not state.allowed(_type):
                    state.cancel_stale_jump()
                    return scene.change_scene_to_chouka_main(_NORMAL)
                return state.call(original, (scene, _type), {})
            return wrapped
        def scene(original):
            def wrapped(scene, _type):
                return state.call(original, (scene, state.menu_type(_type)), {})
            return wrapped
        for index, name, factory in ((0, 'init_button_comp', init),
                (0, 'on_chouka_btn_click', select),
                (0, 'refresh_open_cost_coin_and_btn', tab),
                (0, 'on_open_go_click', go), (0, '_on_open_go_click', enter),
                (0, '_on_activity_click', activity),
                (1, '_on_request_luckydrawfile', jump),
                (1, '_on_request_luckydrawallfile', jump),
                (1, '_on_open_click', jump),
                (1, 'on_open_click', go), (1, 'on_open_all_click', go),
                (1, 'refresh_open_cost_coin_and_btn', box_refresh),
                (1, 'notify_open_file', orb_open),
                (1, 'on_card_model_rotate', orb_rotate),
                (1, 'set_is_open_file', orb_set_open),
                (1, 'enter_scene', orb_enter),
                (1, 'leave_scene', orb_leave),
                (2, 'change_scene_to_activity', scene_activity),
                (2, 'change_scene_to_chouka_main', scene)):
            self.bind(index, name, factory)
        if self.policy:
            def scoped(original):
                def wrapped(*args, **kwargs):
                    return state.call(original, args, kwargs, tab=True)
                return wrapped
            def gift(original):
                def wrapped(panel):
                    state.current()
                    if not panel.valid:
                        return None
                    draw_type = panel.get_luckyDraw_type() if hasattr(panel, 'get_luckyDraw_type') else panel.draw_type
                    if draw_type in state.ready:
                        panel.open_card_gift.setVisible(False)
                        panel.open_card_zhongguojie_icon._node.setVisible(False)
                        panel.open_card_bell_icon.setVisible(False)
                        return None
                    return state.call(original, (panel,), {}, tab=True)
                return wrapped
            for index, name in _HISTORY_METHODS:
                self.bind(index, name, gift if name == 'set_card_gift' else scoped)
        for cls in self.classes:
            setattr(cls, _MARKER, self)
        return self

    def check(self, modules, classes, gg, policy=None):
        if gg is not self.gg or modules != self.modules or classes != self.classes or policy != self.policy:
            raise RuntimeError('Draw UI mixed installation generation')
        self.current()
        for cls, name, replacement, original in self.records:
            if cls.__dict__.get(name) is not replacement or _globals(original).get('gg') is not gg:
                raise RuntimeError('Draw UI installed method identity changed')
        return self


def install(policy_text=None):
    """Idempotent same-generation install; no Avatar class restriction.
    Existing bound target-panel callbacks require a fresh engine, not mutation.
    None retains the 354-only policy. Historical UI uses the exact embedded
    fixed public policy projection; runtime does no file IO.
    """
    policy = _history_policy(policy_text)
    gg = __import__('gg')
    modules = [__import__(name, fromlist=[attribute]) for name, attribute in _TARGETS]
    classes = [getattr(module, attribute) for module, (_, attribute) in zip(modules, _TARGETS)]
    owners = [getattr(cls, _MARKER, None) for cls in classes]
    if owners[0] is not None:
        if any(owner is not owners[0] for owner in owners):
            raise RuntimeError('Draw UI partial installation')
        return owners[0].check(modules, classes, gg, policy)
    if any(owner is not None for owner in owners):
        raise RuntimeError('Draw UI partial class generation')
    panels = getattr(getattr(gg, '__dict__', {}).get('ui'), '__dict__', {}).get('panels')
    cache = getattr(panels, '__dict__', {}).get('_panels', {})
    if any(name in cache for name in ('card_tab', 'card_box')):
        raise RuntimeError('Draw UI target panels already bound')
    game_object = sys.modules.get('com.base.game_object')
    members = getattr(game_object, 'members_cache', {})
    methods = getattr(game_object, 'method_cache', {})
    for index, name in _METHODS + (_HISTORY_METHODS if policy else ()):
        cls = classes[index]
        original = _raw(getattr(cls, name, None))
        if (not isinstance(original, types.FunctionType) or _globals(original).get('gg') is not gg or
                getattr(original, '_q7_draw_ui_wrapped', None) is not None):
            raise RuntimeError('Draw UI original method ABI/globals changed')
        if cls in members or any(len(entry) == 2 and _raw(entry[1]) is original
                                 for entry in methods.get(cls, ())):
            raise RuntimeError('Draw UI target dispatch already cached')
    return _Installation(modules, classes, gg, policy).apply()
