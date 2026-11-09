# -*- coding: ascii -*-
"""Bind original friendship requests/cleanup to their real UI/avatar generation.
Standalone scoped globals only; no reward/cost/table/clock or profile owner.
Install after other panel adapters, before login and card_box construction.
"""
import sys
import types
_TARGET = 'entity.ClientAvatar'
_PANEL = 'cocos.panels.card_box'
_MARKER = '_q7_friend_ui_owner'
_REQUESTS = ('requestLuckyDrawFriendCard', 'requestLuckyDrawNewFriendCard',
             'requestLuckyDrawFriendLianChouCard', 'requestLuckyDrawNewFriendLianChouCard')
_LOCKS = dict((name, name[len('request'):]) for name in _REQUESTS)
_FRIEND_STATES = frozenset(('friend_card_open', 'friend_card_free', 'new_friend_card_open'))
_ENTRIES = ('_on_open_jiban_click', '_on_open_friend_click', 'on_card_left_or_ten_click')

def _raw(fn):
    return getattr(fn, 'im_func', getattr(fn, '__func__', fn))


def _globals(fn):
    return getattr(fn, 'func_globals', getattr(fn, '__globals__', {}))


def _cell(value):
    def captured():
        return value
    return getattr(captured, 'func_closure', getattr(captured, '__closure__', None))[0]


def _clone(original, aliases, gg):
    namespace = dict(_globals(original))
    namespace.update(aliases)
    code = getattr(original, 'func_code', getattr(original, '__code__', None))
    closure = getattr(original, 'func_closure', getattr(original, '__closure__', None))
    if closure:
        cells = list(closure)
        for index, name in enumerate(code.co_freevars):
            value = cells[index].cell_contents
            if name in ('func', 'f') and isinstance(value, types.FunctionType):
                if _globals(value).get('gg') is not gg:
                    raise RuntimeError('Friendship decorated body has stale gg')
                cells[index] = _cell(_clone(value, aliases, gg))
        closure = tuple(cells)
    defaults = getattr(original, 'func_defaults', getattr(original, '__defaults__', None))
    return types.FunctionType(code, namespace, original.__name__, defaults, closure)


class _CleanupGG(object):
    def __init__(self, source, ui):
        self._source, self.ui = source, ui

    def __getattr__(self, name):
        return getattr(self._source, name)


class _RequestLease(object):
    """One original UI lock count, bound to its UI and reset generation."""
    def __init__(self, state, key):
        self.state, self.ui, self.key = state, state.gg.ui, key
        self.epoch = self.ui._lock
        self.mapping, self.claimed, self.released = None, False, False
        self.show_panel = True
        self.wait = None
        self.exec_cancel = getattr(state.gg, 'exec_cancel', None)
        self.unlock_body = _raw(self.ui.unlock)
        if not isinstance(getattr(self.ui, '_lock', None), dict):
            raise RuntimeError('Friendship original UI lock ABI changed')
        if not isinstance(self.unlock_body, types.FunctionType):
            raise RuntimeError('Friendship original UI unlock ABI changed')

    def claim(self, key, show_panel=True):
        if key != self.key or self.claimed or self.released or self.ui._lock is not self.epoch:
            raise RuntimeError('Friendship request lock scope changed')
        self.mapping = self.ui._lock
        self.show_panel = show_panel
        before = self.mapping.get(key, 0)
        self.wait = self.ui.panels.wait
        try:
            return self.ui.lock(key, show_panel)
        finally:
            self.claimed = self.mapping.get(key, 0) > before

    def retire_wait(self):
        # UIPanel.destroy uses current gg.ui even for an old wait instance.
        # Cancel only the captured old scheduler handles; never call destroy.
        wait = self.wait
        if wait is None:
            return None
        for name in ('show_desc_timer', 'disconnect_timer'):
            handle = getattr(wait, name, None)
            if handle:
                if not callable(self.exec_cancel):
                    raise RuntimeError('Friendship original wait scheduler changed')
                self.exec_cancel(handle)
                setattr(wait, name, None)
        node = getattr(wait, '_node', None)
        if node is not None and getattr(wait, 'valid', False):
            node.setVisible(False)
        return None

    def release(self, key=None):
        if key is not None and key != self.key:
            raise RuntimeError('Friendship cleanup lock scope changed')
        if self.released:
            return None
        self.released = True
        if not self.claimed:
            return None
        if sys.modules.get('gg') is not self.state.gg or self.state.gg.ui is not self.ui:
            return self.retire_wait()
        if self.ui._lock is not self.mapping or self.mapping.get(self.key, 0) <= 0:
            return None
        # Original unlock's gg.ui.panels.wait must also stay on the old UI.
        return _clone(self.unlock_body, {'gg': _CleanupGG(self.state.gg, self.ui)}, self.state.gg)(
            self.ui, self.key, self.show_panel)


class _RequestUI(object):
    def __init__(self, gg, lease):
        self.gg, self.lease = gg, lease

    def live(self):
        current = self.gg.live()
        if current.ui is not self.lease.ui:
            raise RuntimeError('Friendship request UI generation changed')
        return current

    def lock(self, key='default', show_panel=True):
        self.live()
        return self.lease.claim(key, show_panel)

    def unlock(self, key='default', show_panel=True):
        return self.lease.release(key)

    def __getattr__(self, name):
        self.live()
        return getattr(self.lease.ui, name)



class _Scope(object):
    def __init__(self, state, avatar, lease):
        self.state, self._avatar, self._data, self.lease = state, avatar, avatar.luckyDrawData, lease
        self._ui, self.epoch = state.gg.ui, state.gg.ui._lock

    def live(self):
        gg = self.state.current()
        if (gg.avatar is not self._avatar or self._avatar.luckyDrawData is not self._data or
                gg.ui is not self._ui or self._ui._lock is not self.epoch):
            raise RuntimeError('Friendship request generation changed')
        return gg

    def __getattr__(self, name):
        if name == 'ui':
            return _RequestUI(self, self.lease)
        gg = self.live()
        return _Avatar(self) if name == 'avatar' else getattr(gg, name)


class _Data(object):
    def __init__(self, scope):
        object.__setattr__(self, '_scope', scope)

    def __getattr__(self, name):
        scope = self._scope
        scope.live()
        original = getattr(scope._data, name)
        if not callable(original):
            return original
        def called(*args, **kwargs):
            scope.live()
            return original(*args, **kwargs)
        return called

    def __setattr__(self, name, value):
        self._scope.live()
        setattr(self._scope._data, name, value)


class _Transport(object):
    def __init__(self, scope, source):
        self.scope, self.source = scope, source

    def __getattr__(self, name):
        self.scope.live()
        original = getattr(self.source, name)
        if name != 'call_server_method':
            return original
        def send(*args, **kwargs):
            self.scope.live()
            gg = self.scope.live()
            parameters = args[1] if len(args) > 1 else kwargs.get('parameters')
            callback_id = parameters.get('_cbid_') if isinstance(parameters, dict) else None
            callbacks = getattr(gg, 'avatar_callback_map', None)
            pending = getattr(gg, 'avatar_callback_need_result', None)
            callback = callbacks.get(callback_id) if isinstance(callbacks, dict) else None
            try:
                return original(*args, **kwargs)
            except Exception:
                # Definite send failure: clean only this registration. A later
                # stale completion cannot consume another owner's callback ID.
                if (callback is not None and getattr(gg, 'avatar_callback_map', None) is callbacks and
                        callbacks.get(callback_id) is callback):
                    callbacks.pop(callback_id, None)
                    if getattr(gg, 'avatar_callback_need_result', None) is pending and isinstance(pending, dict):
                        pending.pop(callback_id, None)
                self.scope.lease.release()
                raise
        return send


class _Avatar(object):
    def __init__(self, scope):
        object.__setattr__(self, '_scope', scope)

    def __getattr__(self, name):
        scope = self._scope
        scope.live()
        if name == 'luckyDrawData':
            return _Data(scope)
        original = getattr(scope._avatar, name)
        if name == 'server':
            return _Transport(scope, original)
        raw = scope.state.originals.get(name, _raw(original))
        if not isinstance(raw, types.FunctionType) or not (hasattr(original, 'im_self') or hasattr(original, '__self__')):
            return original
        def called(*args, **kwargs):
            scope.live()
            try:
                return _clone(raw, {'gg': scope}, scope.state.gg)(self, *args, **kwargs)
            except Exception:
                scope.lease.release()
                raise
        return called

    def __setattr__(self, name, value):
        self._scope.live()
        setattr(self._scope._avatar, name, value)


class _Installation(object):
    def __init__(self, module, cls, panel_module, panel_cls, gg, originals, on_init, history_avatar_type):
        self.module, self.cls, self.panel_module, self.panel_cls, self.gg = module, cls, panel_module, panel_cls, gg
        self.originals, self.on_init, self.records = originals, on_init, []
        self.history_avatar_type = history_avatar_type

    def current(self):
        if (sys.modules.get('gg') is not self.gg or sys.modules.get(_TARGET) is not self.module or
                self.module.ClientAvatar is not self.cls or sys.modules.get(_PANEL) is not self.panel_module or
                self.panel_module.Panel is not self.panel_cls or self.cls.__dict__.get(_MARKER) is not self or
                self.panel_cls.__dict__.get(_MARKER) is not self):
            raise RuntimeError('Friendship installed class generation changed')
        for cls, name, wrapper in self.records:
            if cls.__dict__.get(name) is not wrapper:
                raise RuntimeError('Friendship installed method changed')
        return self.gg

    def request(self, name, avatar, args, kwargs):
        gg = self.current()
        if avatar is not gg.avatar:
            # Existing normal/history panel adapter passes one trusted view.
            # No generic duck unwrapping: bind to its installed owner identities.
            owner = self.panel_cls.__dict__.get('_q7_draw_ui_owner')
            values = getattr(avatar, '__dict__', {})
            if (owner is None or self.history_avatar_type is None or type(avatar) is not self.history_avatar_type or
                    values.get('_state') is not owner or values.get('_source') is not gg.avatar or
                    owner.current() is not gg):
                raise RuntimeError('Friendship avatar changed')
            avatar = gg.avatar
        lease = _RequestLease(self, _LOCKS[name])
        scope = _Scope(self, avatar, lease)
        try:
            return _clone(self.originals[name], {'gg': scope}, gg)(_Avatar(scope), *args, **kwargs)
        except Exception:
            lease.release()
            raise

    def pin(self, panel):
        gg = self.current()
        generation = (gg.avatar, gg.avatar.luckyDrawData, gg.ui)
        prior = panel.__dict__.get('_q7_friend_generation')
        if prior is not None and any(a is not b for a, b in zip(prior, generation)):
            raise RuntimeError('Friendship panel initialization changed')
        if prior is not None:
            return
        panel._q7_friend_generation = generation
        # Instance-only guards preserve other adapters' class methods and checks.
        for name in _ENTRIES:
            original = getattr(panel, name)
            def make(original, name):
                def guarded(*args, **kwargs):
                    if name != 'on_card_left_or_ten_click' or panel.cur_state in _FRIEND_STATES:
                        current = self.current()
                        if (not getattr(panel, 'valid', False) or current.avatar is not generation[0] or
                                current.avatar.luckyDrawData is not generation[1] or current.ui is not generation[2]):
                            raise RuntimeError('Friendship panel generation changed')
                    return original(*args, **kwargs)
                return guarded
            setattr(panel, name, make(original, name))

    def apply(self):
        state = self
        for name in _REQUESTS:
            def make(name):
                def wrapped(avatar, *args, **kwargs):
                    return state.request(name, avatar, args, kwargs)
                wrapped.__dict__.update(getattr(state.originals[name], '__dict__', {}))
                return wrapped
            replacement = make(name)
            setattr(self.cls, name, replacement)
            self.records.append((self.cls, name, replacement))
        def init(panel, *args, **kwargs):
            state.pin(panel)
            return state.on_init(panel, *args, **kwargs)
        setattr(self.panel_cls, 'on_init', init)
        self.records.append((self.panel_cls, 'on_init', init))
        setattr(self.cls, _MARKER, self)
        setattr(self.panel_cls, _MARKER, self)
        return self


def install(history_avatar_type=None):
    """Idempotent same-class installation before login/panel callback binding."""
    gg = __import__('gg')
    module = __import__(_TARGET, fromlist=['ClientAvatar'])
    panel_module = __import__(_PANEL, fromlist=['Panel'])
    cls, panel_cls = module.ClientAvatar, panel_module.Panel
    owners = [cls.__dict__.get(_MARKER), panel_cls.__dict__.get(_MARKER)]
    if any(owner is not None for owner in owners):
        if owners[0] is None or owners[0] is not owners[1]:
            raise RuntimeError('Friendship partial installation')
        if owners[0].history_avatar_type is not history_avatar_type:
            raise RuntimeError('Friendship view type changed')
        return owners[0].current() and owners[0]
    if getattr(gg, 'avatar', None) is not None:
        raise RuntimeError('Friendship install requires pre-login engine')
    panels = getattr(getattr(gg, 'ui', None), 'panels', None)
    if 'card_box' in getattr(panels, '__dict__', {}).get('_panels', {}):
        raise RuntimeError('Friendship panel already bound')
    originals = dict((name, _raw(getattr(cls, name, None))) for name in _REQUESTS)
    on_init = _raw(getattr(panel_cls, 'on_init', None))
    for original in list(originals.values()) + [on_init]:
        if not isinstance(original, types.FunctionType) or _globals(original).get('gg') is not gg:
            raise RuntimeError('Friendship original globals/ABI changed')
    for name in _ENTRIES:
        if not callable(getattr(panel_cls, name, None)):
            raise RuntimeError('Friendship panel entry missing')
    return _Installation(module, cls, panel_module, panel_cls, gg, originals, on_init, history_avatar_type).apply()
