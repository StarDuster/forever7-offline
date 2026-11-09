# -*- coding: ascii -*-
"""Scoped historical furniture admission/presentation; original owner/RPC/rewards."""
import hashlib
import json
import sys
import types

_TARGET = 'cocos.panels.city_room_danchi_new'
_ENTRY = 'cocos.panels.city'
_ENTRY_METHODS = ('visible_functional', 'on_back_home_click', 'do_city_danchi_click')
_MARKER = '_q7_furniture_ui_owner'
_ASSET = 'dd85b09e9f3094a2c5a9f72a3300e04ad85e63b9730c6cdd8ab2a32b54ba4a2d'
_POLICY = '8b44a2ef9e061db25ba70f1d62b91fb68fc989e478d5d01e5b2917908e29ff2b'
_METHODS = ('init_data', 'refresh_neirong', 'refresh_daibi', 'refresh_btn_card',
            'on_arrow_click', 'on_btn_once_click', 'on_btn_ten_click',
            'try_fast_buy', 'on_destroy', 'refresh_xiangqing')
try:
    _TEXT = (basestring,)
    _INT = (int, long)
except NameError:
    _TEXT = (str, bytes)
    _INT = (int,)


def _pairs(pairs):
    out = {}
    for key, value in pairs:
        if key in out:
            raise ValueError('Duplicate furniture policy key')
        out[key] = value
    return out


def _policy(text):
    if not isinstance(text, _TEXT):
        raise ValueError('Embedded furniture policy text required')
    data = json.loads(text, object_pairs_hook=_pairs)
    if (not isinstance(data, dict) or set(data) != set(('schema', 'asset_sha256', 'ready_ids', 'all_history_ids')) or
            data['schema'] != 'project7-history-furniture-ui-v1' or data['asset_sha256'] != _ASSET):
        raise ValueError('Furniture policy version changed')
    for key in ('ready_ids', 'all_history_ids'):
        values = data[key]
        if (not isinstance(values, list) or len(values) != 40 or
                any(type(value) not in _INT or value <= 0 or value > 2147483647 for value in values) or
                values != sorted(set(values)) or 162 in values):
            raise ValueError('Furniture policy IDs invalid')
    if data['ready_ids'] != data['all_history_ids']:
        raise ValueError('Furniture policy admission changed')
    canonical = json.dumps(data, sort_keys=True, separators=(',', ':')).encode('ascii')
    if hashlib.sha256(canonical).hexdigest() != _POLICY:
        raise ValueError('Furniture policy projection changed')
    return data


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
                    raise RuntimeError('Furniture decorated body has stale gg')
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
            raise RuntimeError('Furniture original UI lock ABI changed')
        if not isinstance(self.unlock_body, types.FunctionType):
            raise RuntimeError('Furniture original UI unlock ABI changed')

    def claim(self, key, show_panel=True):
        if key != self.key or self.claimed or self.released or self.ui._lock is not self.epoch:
            raise RuntimeError('Furniture request lock scope changed')
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
                    raise RuntimeError('Furniture original wait scheduler changed')
                self.exec_cancel(handle)
                setattr(wait, name, None)
        node = getattr(wait, '_node', None)
        if node is not None and getattr(wait, 'valid', False):
            node.setVisible(False)
        return None

    def release(self, key=None):
        if key is not None and key != self.key:
            raise RuntimeError('Furniture cleanup lock scope changed')
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
            raise RuntimeError('Furniture request UI generation changed')
        return current

    def lock(self, key='default', show_panel=True):
        self.live()
        return self.lease.claim(key, show_panel)

    def unlock(self, key='default', show_panel=True):
        return self.lease.release(key)

    def __getattr__(self, name):
        self.live()
        return getattr(self.lease.ui, name)


class _OwnerView(object):
    def __init__(self, source, state, avatar):
        object.__setattr__(self, '_source', source)
        object.__setattr__(self, '_state', state)
        object.__setattr__(self, '_avatar', avatar)
        object.__setattr__(self, '_ui', state.gg.ui)
        object.__setattr__(self, '_epoch', state.gg.ui._lock)

    def _live(self):
        current = self._state.current()
        if current.avatar is not self._avatar or current.ui is not self._ui or self._ui._lock is not self._epoch:
            raise RuntimeError('Furniture avatar/UI generation changed')

    def __getattr__(self, name):
        self._live()
        return getattr(self._source, name)

    def __setattr__(self, name, value):
        if name in ('_source', '_state', '_avatar', '_data', '_lease', '_ui', '_epoch', 'luckyDrawData'):
            raise RuntimeError('Furniture scoped alias is read only')
        self._live()
        setattr(self._source, name, value)


class _Data(_OwnerView):
    def _live(self):
        _OwnerView._live(self)
        if self._avatar.luckyDrawData is not self._source:
            raise RuntimeError('Furniture data generation changed')

    def __getattr__(self, name):
        self._live()
        original = getattr(self._source, name)
        if name == 'getCurrActivedFurnitureCard':
            def listing(*args, **kwargs):
                self._live()
                result = list(original(*args, **kwargs))
                skin_num = args[0] if args else kwargs.get('skin_num')
                if skin_num in (None, 3):
                    result = sorted(set(result).union(self._state.ready),
                                    key=lambda t: (self._state.info.get(t, {}).get('sort', 0), t))
                return result
            return listing
        if name in ('checkFurnitureCardCost', 'getFurnitureCardConsume'):
            def cost(*args, **kwargs):
                self._live()
                draw_type = args[0] if args else kwargs.get('_type')
                if draw_type in self._state.ready:
                    if name == 'checkFurnitureCardCost':
                        return True
                    row = self._state.delivery.get(draw_type, {})
                    item = row.get('fur_consume_item', self._state.info[draw_type]['fur_consume_item'])[0]
                    return [(item, 0)]
                return original(*args, **kwargs)
            return cost
        if not callable(original):
            return original
        def delegated(*args, **kwargs):
            self._live()
            return original(*args, **kwargs)
        return delegated


class _Avatar(_OwnerView):
    def __init__(self, source, state, avatar, lease=None):
        _OwnerView.__init__(self, source, state, avatar)
        object.__setattr__(self, '_data', source.luckyDrawData)
        object.__setattr__(self, '_lease', lease)

    def _live(self):
        _OwnerView._live(self)
        if self._source.luckyDrawData is not self._data:
            raise RuntimeError('Furniture avatar data generation changed')

    def __getattr__(self, name):
        self._live()
        if name == 'luckyDrawData':
            return _Data(self._source.luckyDrawData, self._state, self._source)
        original = getattr(self._source, name)
        raw = _raw(original)
        if not isinstance(raw, types.FunctionType) or not (hasattr(original, 'im_self') or hasattr(original, '__self__')):
            return original
        def called(*args, **kwargs):
            self._live()
            t = args[0] if args else kwargs.get('_type')
            if t in self._state.ready:
                if name == 'checkDrawInTime':
                    return True
                if name == 'checkActivity':
                    const = _globals(raw)['const']
                    expected = const.CardPoolType.TYPE_FURNITURE
                    pool = args[1] if len(args) > 1 else kwargs.get('pool_type', const.CardPoolType.TYPE_HERO_TREASURE)
                    return pool == expected and self._state.info[t].get('poolType') == expected
            lease = self._lease
            actor = self
            if name in ('requestLuckyDrawFurnitureCard', 'requestLuckyDrawFurnitureLianchouCard'):
                lease = _RequestLease(self._state, name)
                actor = _Avatar(self._source, self._state, self._source, lease)
            gg = _ScopedGG(self._state, self._source, lease)
            try:
                return _clone(raw, {'gg': gg}, self._state.gg)(actor, *args, **kwargs)
            except Exception:
                if lease is not None:
                    lease.release()
                raise
        return called


class _ScopedGG(object):
    def __init__(self, state, avatar, lease=None):
        self._state, self._avatar, self._data = state, avatar, avatar.luckyDrawData
        self._lease = lease
        self._ui = lease.ui if lease is not None else state.gg.ui
        self._epoch = lease.epoch if lease is not None else self._ui._lock

    def live(self):
        gg = self._state.current()
        if (gg.avatar is not self._avatar or gg.avatar.luckyDrawData is not self._data or
                gg.ui is not self._ui or self._ui._lock is not self._epoch):
            raise RuntimeError('Furniture callback generation changed')
        return gg

    def __getattr__(self, name):
        if name == 'ui' and self._lease is not None:
            return _RequestUI(self, self._lease)
        gg = self.live()
        return _Avatar(self._avatar, self._state, self._avatar, self._lease) if name == 'avatar' else getattr(gg, name)


class _Installation(object):
    def __init__(self, module, cls, gg, policy, info, delivery, entry_module, entry_cls):
        self.module, self.cls, self.gg, self.policy = module, cls, gg, policy
        self.entry_module, self.entry_cls = entry_module, entry_cls
        self.ready = frozenset(policy['ready_ids'])
        self.info, self.delivery = info, delivery
        self.records = []

    def current(self):
        if (sys.modules.get('gg') is not self.gg or sys.modules.get(_TARGET) is not self.module or
                self.module.Panel is not self.cls or self.cls.__dict__.get(_MARKER) is not self or
                sys.modules.get(_ENTRY) is not self.entry_module or self.entry_module.Panel is not self.entry_cls or
                self.entry_cls.__dict__.get(_MARKER) is not self):
            raise RuntimeError('Furniture UI generation changed')
        for cls, name, replacement, original in self.records:
            fn = original.fget if isinstance(original, property) else original
            if cls.__dict__.get(name) is not replacement or _globals(fn).get('gg') is not self.gg:
                raise RuntimeError('Furniture UI installed method identity changed')
        return self.gg

    def call(self, original, panel, args, kwargs):
        gg = self.current()
        return _clone(original, {'gg': _ScopedGG(self, gg.avatar)}, gg)(panel, *args, **kwargs)

    def pin_panel(self, panel):
        gg = self.current()
        pair = (gg.avatar, gg.avatar.luckyDrawData)
        prior = panel.__dict__.get('_q7_furniture_generation')
        if prior is not None and (prior[0] is not pair[0] or prior[1] is not pair[1]):
            raise RuntimeError('Furniture panel initialization generation changed')
        panel._q7_furniture_generation = pair

    def panel_live(self, panel):
        gg = self.current()
        prior = panel.__dict__.get('_q7_furniture_generation')
        if prior is None or prior[0] is not gg.avatar or prior[1] is not gg.avatar.luckyDrawData:
            raise RuntimeError('Furniture panel generation changed')

    def release_only(self, panel):
        panel.__dict__.pop('_q7_furniture_widget_flags', None)
        first = None
        for name in ('show_anim', 'idle_anim'):
            animation = panel.__dict__.get(name)
            if animation is not None:
                try:
                    animation.release()
                except Exception as error:
                    if first is None:
                        first = error
                finally:
                    setattr(panel, name, None)
        if first is not None:
            raise first

    def historical(self, panel):
        self.panel_live(panel)
        return panel.curr_type in self.ready

    def save_widgets(self, panel):
        if panel.__dict__.get('_q7_furniture_widget_flags') is not None:
            return
        nodes = ([panel.board, panel.title_pic[0], panel.dabi1_comp._node, panel.dabi2_comp._node,
                  panel.btn_drawing, panel.panel_tv, panel.panel_tuzhi] +
                 list(panel.left_arrow) + list(panel.right_arrow) + list(panel.skin_imgs[0]) +
                 list(panel.furnitures_reward) + list(panel.light_list) + list(panel.btn_view_list) +
                 list(panel.btn_shop) + [comp._node for comp in panel.jiaju_comps3])
        panel._q7_furniture_widget_flags = [(node, node.isVisible()) for node in nodes]

    def restore_widgets(self, panel):
        saved = panel.__dict__.get('_q7_furniture_widget_flags')
        if saved is not None:
            for node, visible in saved:
                node.setVisible(visible)
            delattr(panel, '_q7_furniture_widget_flags')

    def present(self, panel):
        self.save_widgets(panel)
        row = self.info[panel.curr_type]
        panel.fixed_draw.setVisible(False)
        panel.fixed_draw_sp.setVisible(False)
        panel.limit_draw.setVisible(True)
        for index in range(3):
            panel.left_arrow[index].setVisible(index == 0 and len(panel.type_list) > 1)
            panel.right_arrow[index].setVisible(index == 0 and len(panel.type_list) > 1)
        panel.panel_title.setString(u'\u79bb\u7ebf\u914d\u9001 %d - %s' % (panel.curr_type, row.get('room_title', '')))
        panel.board.setVisible(False)
        panel.title_pic[0].setVisible(False)
        panel.time_txt[0].setString(u'\u5386\u53f2\u914d\u9001 - \u514d\u8d39')
        for node in panel.skin_imgs[0]:
            node.setVisible(False)
        panel.furnitures_reward[0].setVisible(True)
        panel.furnitures_reward[1].setVisible(False)
        panel.info_1.setString(row.get('skin_infos', ''))
        panel.info_2.setString(row.get('furniture_infos', ''))
        items = row.get('furniture_items', ())
        for index, comp in enumerate(panel.jiaju_comps3):
            comp._node.setVisible(index < len(items))
            if index < len(items):
                comp.set_info(items[index], list(items))
                comp.set_not_stop_bg_music(True)
        for node in tuple(panel.light_list) + tuple(panel.btn_view_list) + tuple(panel.btn_shop):
            node.setVisible(False)
        panel.btn_drawing.setVisible(False)
        panel.panel_tv.setVisible(False)
        panel.panel_tuzhi.setVisible(False)

    def entry_visible(self, panel):
        gg = self.current()
        const = self.entry_module.const
        if (not self.ready or not getattr(gg, 'avatar', None) or panel.in_dialogue or
                sum(panel.visible_semaphore.values()) != 0 or
                gg.scene_mgr.active_scn_path != const.SCENE_CITY or
                gg.city_container.cur_scene_key != const.SCENE_CITY):
            return False
        return const.MAX_DAYNUM - gg.avatar.weeknumData.daynum - 1 > 0

    def bind_entry(self):
        state = self
        for name in _ENTRY_METHODS:
            original = _raw(getattr(self.entry_cls, name))
            def factory(name, original):
                def wrapped(panel, *args, **kwargs):
                    gg = state.current()
                    if name == 'visible_functional':
                        # Keep all original progress/layout decisions, then expose
                        # only this existing room/home navigation node.
                        result = original(panel, *args, **kwargs)
                        if state.entry_visible(panel):
                            panel.btn_home.setVisible(True)
                        return result
                    if name == 'do_city_danchi_click':
                        return state.call(original, panel, args, kwargs)
                    event = args[1] if len(args) > 1 else kwargs.get('event')
                    if event != state.entry_module.cc.ccui.TOUCH_EVENT_ENDED:
                        return original(panel, *args, **kwargs)
                    avatar, data, owner_ui, epoch = gg.avatar, gg.avatar.luckyDrawData, gg.ui, gg.ui._lock
                    def live():
                        current = state.current()
                        if (current.avatar is not avatar or avatar.luckyDrawData is not data or
                                current.ui is not owner_ui or owner_ui._lock is not epoch or not panel.valid):
                            raise RuntimeError('Furniture navigation generation changed')
                    def delivery(*unused):
                        live()
                        return panel.do_city_danchi_click(0)
                    def home(*unused):
                        live()
                        return original(panel, *args, **kwargs)
                    live()
                    return gg.ui.panels.common_confirm.notify_confirm(
                        u'\u8bf7\u9009\u62e9\u5c45\u5ba4\u6216\u5386\u53f2\u914d\u9001', delivery,
                        confirm_label=u'\u5386\u53f2\u914d\u9001', cancel_cb=home,
                        cancel_label=u'\u5c45\u5ba4')
                return wrapped
            replacement = factory(name, original)
            setattr(self.entry_cls, name, replacement)
            self.records.append((self.entry_cls, name, replacement, original))

    def apply(self):
        state = self
        for name in _METHODS:
            original = _raw(getattr(self.cls, name))
            def factory(name, original):
                def wrapped(panel, *args, **kwargs):
                    if name == 'on_destroy':
                        try:
                            state.panel_live(panel)
                        except RuntimeError:
                            return state.release_only(panel)
                        panel.__dict__.pop('_q7_furniture_widget_flags', None)
                    if name == 'init_data':
                        state.pin_panel(panel)
                    else:
                        state.panel_live(panel)
                    history = name != 'init_data' and state.historical(panel)
                    if history and name == 'refresh_neirong':
                        return state.present(panel)
                    if history and name == 'refresh_daibi':
                        state.save_widgets(panel)
                        panel.dabi1_comp._node.setVisible(False)
                        panel.dabi2_comp._node.setVisible(False)
                        return None
                    if history and name == 'try_fast_buy':
                        return False
                    if not history and name == 'refresh_neirong':
                        state.restore_widgets(panel)
                    return state.call(original, panel, args, kwargs)
                return wrapped
            replacement = factory(name, original)
            setattr(self.cls, name, replacement)
            self.records.append((self.cls, name, replacement, original))
        original = self.cls.__dict__['fixed_type']
        def fixed(panel):
            state.current()
            if panel.__dict__.get('_q7_furniture_generation') is not None:
                state.panel_live(panel)
            return 0 if panel.curr_type in state.ready else original.fget(panel)
        replacement = property(fixed, original.fset, original.fdel, original.__doc__)
        setattr(self.cls, 'fixed_type', replacement)
        self.records.append((self.cls, 'fixed_type', replacement, original))
        self.bind_entry()
        setattr(self.cls, _MARKER, self)
        setattr(self.entry_cls, _MARKER, self)
        return self


def install(policy_text):
    policy = _policy(policy_text)
    gg = __import__('gg')
    module = __import__(_TARGET, fromlist=['Panel'])
    cls = module.Panel
    entry_module = __import__(_ENTRY, fromlist=['Panel'])
    entry_cls = entry_module.Panel
    owner = cls.__dict__.get(_MARKER)
    if owner is not None:
        if not isinstance(owner, _Installation) or owner.policy != policy or entry_cls.__dict__.get(_MARKER) is not owner:
            raise RuntimeError('Furniture UI mixed installation')
        owner.current()
        return owner
    if entry_cls.__dict__.get(_MARKER) is not None:
        raise RuntimeError('Furniture UI partial installation')
    panels = getattr(getattr(gg, 'ui', None), 'panels', None)
    if set(('city_room_danchi_new', 'city')).intersection(getattr(panels, '__dict__', {}).get('_panels', {})):
        raise RuntimeError('Furniture UI panel already bound')
    cache = sys.modules.get('com.base.game_object')
    if any(target in getattr(cache, 'members_cache', {}) or getattr(cache, 'method_cache', {}).get(target) for target in (cls, entry_cls)):
        raise RuntimeError('Furniture UI dispatch already cached')
    for name in _METHODS:
        original = _raw(getattr(cls, name, None))
        if not isinstance(original, types.FunctionType) or _globals(original).get('gg') is not gg:
            raise RuntimeError('Furniture UI original method ABI changed')
    for name in _ENTRY_METHODS:
        original = _raw(getattr(entry_cls, name, None))
        if not isinstance(original, types.FunctionType) or _globals(original).get('gg') is not gg:
            raise RuntimeError('Furniture navigation original ABI changed')
    if not isinstance(cls.__dict__.get('fixed_type'), property):
        raise RuntimeError('Furniture UI original property ABI changed')
    info = __import__('com.data.cdata.chouka_info', fromlist=['data']).data
    delivery = __import__('com.data.cdata.furniture_delivery', fromlist=['data']).data
    if any(t not in info or info[t].get('poolType') != 2 or not info[t].get('fur_consume_item') for t in policy['ready_ids']):
        raise RuntimeError('Furniture source metadata incomplete')
    return _Installation(module, cls, gg, policy, info, delivery, entry_module, entry_cls).apply()
