# -*- coding: ascii -*-
"""Offline inventory/catalog editor entry. UI only; server transactions stay authoritative.

The panel is mounted from an extra BBS-home app next to Settings/Auxiliary/Album and
follows the native settings layout (top bar, left tabs, list + detail). Every edit is a
reliable RPC carrying a persisted operation id. A reply is accepted only when
its echoed op matches the current pending op; old replies cannot unlock a new
request. The pool-switch tab only reads/writes the per-account open-pool
selection owned by project7_draw_ui; no profile bytes are written from Python.
"""
import os
import errno
import hashlib
import json

try:
    _TEXT = (basestring,)
except NameError:
    _TEXT = (str, bytes)

_MARKER = '_f7_inventory_editor_installed'
_BBS_MARKER = '_f7_inventory_bbs_owner'
_LOCK = 'f7_inventory_editor'
_PENDING = 'p7_inventory_editor_pending.json'
_POOL_CAP = 12
_POOL_PAGE = 20
# The catalog RPC answers a bounded slice; the list pages through it.
_CATALOG_PAGE = 50
_TABS = (('item', u'\u7269\u54c1'), ('currency', u'\u8d27\u5e01'),
         ('treasure', u'\u5f71\u88c5'), ('pool', u'\u5361\u6c60\u5f00\u5173'),
         ('bulk', u'\u5feb\u6377'))
# One-tap grants: (gateway key, label, note)
# Cell limits keep a one-tap action reading as a button, not a full-width bar.
_BULK_MIN_W = 380.0
_BULK_MAX_W = 560.0
_BULK_MAX_H = 96.0
_BULK = (('letters_reset', u'\u6e05\u7a7a2018/2019\u60c5\u4e66', u'\u6062\u590d\u590d\u523b\u60c5\u4e66\u53ef\u9009'),
         ('letters_keep', u'\u89e3\u9501\u60c5\u4e66(\u4fdd\u7559\u5151\u6362)', u'\u7559\u4e0b 2018/2019 \u7ed9\u590d\u523b\u60c5\u4e66'),
         ('letters', u'\u89e3\u9501\u5168\u90e8\u60c5\u4e66', u'\u60c5\u4e66\u00b7/+2018 \u5168\u5957'),
         ('gifts', u'\u89e3\u9501\u5168\u90e8\u793c\u7269', u'\u5f71\u88c5\u4ebf\u4e07\u5e26\u6765\u7684\u4eba\u60c5\u793c\u7269'),
         ('shards', u'\u89e3\u9501\u5168\u90e8\u788e\u7247', u'\u795e\u5668\u4f7f\u788e\u7247\u5168\u5f00'),
         ('cg', u'\u89e3\u9501\u5168\u90e8 CG', u'\u56fe\u9274\u00b7CG \u5168\u5f00'),
         ('currency', u'\u8865\u6ee1\u5168\u90e8\u8d27\u5e01', u'\u6bcf\u79cd\u8d27\u5e01\u7f6e\u4e3a\u4e0a\u9650'))
_HEADERS = {'item': u'\u7269\u54c1\u5217\u8868', 'currency': u'\u8d27\u5e01\u5217\u8868',
            'treasure': u'\u5f71\u88c5\u5217\u8868', 'bulk': u'\u5feb\u6377\u64cd\u4f5c'}
_VIEW = {'active': False, 'root': None, 'card': None, 'panel': None, 'group': 'item',
         'rows': [], 'selected': None, 'selected_key': None, 'catalog_query': None,
         'search': None, 'count': None, 'quality': None, 'quality_value': 1,
         'status': None, 'scroll': None, 'busy': False, 'mode': 'set',
         'quality_buttons': {}, 'mode_buttons': {}, 'cta': None,
         'detail_name': None, 'held': None, 'pending_button': None, 'detail_icon': None,
         'detail_rects': [], 'detail_icon_size': 0,
         'native_skin': False, 'catalog_generation': 0, 'query': None,
         'catalog_loading': False, 'catalog_nonce': None, 'ui_epoch': 0,
         'catalog_page': 0, 'catalog_more': False, 'row_width': 0,
         'metrics': None, 'body': None, 'csb': {}, 'tab_comps': {},
         'gap': 0, 'header': None, 'header_native': False, 'row_pool': [],
         'inventory_content': None, 'pool_content': None,
         'tab_labels': {}, 'tab_fills': {}, 'tab_strips': {}, 'tab_pointers': {},
         'list_header': None, 'detail_header': None, 'pool_api': None,
         'pool_all': [], 'pool_page': 0, 'pool_scroll': None, 'pool_search': None,
         'pool_header': None, 'pool_status': None, 'pool_prev': None,
         'pool_next': None, 'pool_page_label': None, 'pool_list_width': 0,
         'geometry': None, 'geo_widgets': {}}


def _doc_dir():
    import game3d
    return game3d.get_doc_dir()


def _pending_path(session=None):
    session = session if session is not None else _identity()
    if not session:
        return ''
    digest = hashlib.sha256(session.encode('ascii')).hexdigest()
    return os.path.join(_doc_dir(), 'p7_inventory_editor_pending_' + digest + '.json')


def _identity():
    import gg
    avatar = getattr(gg, 'avatar', None)
    if avatar is None:
        return ''
    # ClientAvatar.account is initialized from "an" (ClientAvatar.py:134).
    # Never fall back to a repeatable uid/id; an identity-less account must not
    # send a pending operation.
    for name in ('account', 'an'):
        try:
            value = getattr(avatar, name, None)
            if value is not None and value != '':
                return u'%s:%s' % (name, value)
        except Exception:
            pass
    return ''


def _pending_state(session=None):
    path = _pending_path(session)
    if not path:
        return 'missing', None
    try:
        with open(path, 'rb') as stream:
            value = json.loads(stream.read())
    except IOError as error:
        if error.errno == errno.ENOENT:
            return 'missing', None
        return 'corrupt', None
    except Exception:
        return 'corrupt', None
    if not isinstance(value, dict):
        return 'corrupt', None
    op, batch, session = value.get('op'), value.get('batch'), value.get('session')
    if (not isinstance(op, _TEXT) or len(op) != 32 or
            any(ch not in '0123456789abcdef' for ch in op) or
            not isinstance(batch, list) or not batch or
            not isinstance(session, _TEXT) or not session):
        return 'corrupt', None
    # One-tap batches are larger than the 64-row edit cap; accept them so a
    # lost reply can be recognised (and dropped) instead of looking corrupt.
    limit = 64
    if all(isinstance(row, dict) and row.get('k') in ('bulk', 'cg')
           for row in batch):
        limit = 1024
    if len(batch) > limit:
        return 'corrupt', None
    return 'valid', {'op': op, 'batch': batch, 'session': session}


def _load_pending(session=None):
    return _pending_state(session)[1]


def _save_pending(op, batch, session):
    target = _pending_path(session)
    if not target:
        return False
    temporary = target + '.tmp'
    try:
        with open(temporary, 'wb') as stream:
            stream.write(json.dumps({'op': op, 'batch': batch, 'session': session},
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


def _clear_pending(session=None):
    path = _pending_path(session)
    if not path:
        return
    try:
        os.unlink(path)
    except Exception:
        pass


def _new_op():
    return os.urandom(16).encode('hex')


def _status(text):
    label = _VIEW.get('status')
    if label is not None:
        try:
            label.setString(text)
        except Exception:
            pass


def _unlock():
    try:
        import gg
        gg.ui.unlock(_LOCK)
    except Exception:
        pass
    _VIEW['busy'] = False


def _op_from(reply):
    try:
        op = reply.get('op')
        return op if isinstance(op, _TEXT) and len(op) == 32 else ''
    except Exception:
        return ''


def _reply_edit(self, rs, reason=0, op=''):
    import gg
    if self is not getattr(gg, 'avatar', None) or not _VIEW.get('active'):
        return
    identity = _identity()
    state, pending = _pending_state(identity)
    if state == 'corrupt':
        _status(u'\u672a\u51b3\u64cd\u4f5c\u8bb0\u5f55\u635f\u574f\uff0c\u8bf7\u5148\u6062\u590d')
        _unlock()
        return
    if not pending:
        return
    if pending.get('session') != identity or not op or op != pending.get('op'):
        return
    if rs:
        _clear_pending(identity)
        _status(u'\u5df2\u4fdd\u5b58')
        if _VIEW.get('group') == 'bulk' and _VIEW.get('bulk_queue'):
            # Release the UI lock before the next chunk: it is held by _send
            # and a locked avatar channel silently drops the next reliable call.
            _unlock()
            _update_pending_button()
            _bulk_pump()
            return
        if _VIEW.get('group') == 'bulk':
            _bulk_status(u'\u5df2\u5b8c\u6210\uff0c\u80cc\u5305\u5df2\u66f4\u65b0')
        _request_catalog(preserve=True)
    else:
        # Only reason 1 is the server's explicit pre-commit/business
        # rejection. Conflict/read/commit/publish errors are unknown and keep
        # the op durable.
        if reason == 1:
            _clear_pending(identity)
            _status(u'\u672a\u4fdd\u5b58\uff0c\u8bf7\u68c0\u67e5\u8f93\u5165')
        else:
            _status(u'\u64cd\u4f5c\u72b6\u6001\u4e0d\u660e\uff0c\u8bf7\u6838\u5bf9\u4e0a\u6b21\u64cd\u4f5c')
    _unlock()
    _update_pending_button()


def _finish_catalog():
    _VIEW['catalog_loading'] = False


def _reply_catalog(self, rs, rows=None, reason=0, op='', group='', query=''):
    import gg
    if self is not getattr(gg, 'avatar', None) or not _VIEW.get('active'):
        return
    expected_nonce = _VIEW.get('catalog_nonce')
    if expected_nonce is not None and op != expected_nonce:
        return
    expected_query = _VIEW.get('catalog_query')
    if group and group != _VIEW.get('catalog_group'):
        _finish_catalog()
        return
    if query is not None and expected_query is not None and query != expected_query:
        _finish_catalog()
        return
    if rs:
        old_key = _VIEW.get('selected_key')
        _VIEW['rows'] = list(rows or [])
        _VIEW['selected'] = None
        _VIEW['selected_key'] = None
        _VIEW['selected_token'] = None
        for row in _VIEW['rows']:
            if old_key is not None and _row_key(row) == old_key:
                _VIEW['selected'] = row
                _VIEW['selected_key'] = old_key
                _VIEW['selected_token'] = (_VIEW.get('ui_epoch'), _VIEW.get('catalog_generation'))
                break
        _render_rows()
        _refresh_detail()
        _update_pending_button()
        _VIEW['catalog_more'] = len(_VIEW['rows']) >= _CATALOG_PAGE
        _update_pager()
        if old_key is not None:
            _status(u'\u5df2\u4fdd\u5b58\uff0c\u80cc\u5305\u5df2\u66f4\u65b0')
        else:
            _status(u'\u7b2c %d \u9875 \u00b7 %s \u4e2a\u6761\u76ee' % (
                int(_VIEW.get('catalog_page') or 0) + 1, len(_VIEW['rows'])))
    else:
        _VIEW['rows'] = []
        _VIEW['selected'] = None
        _VIEW['selected_key'] = None
        _render_rows()
        _refresh_detail()
        _status(u'\u76ee\u5f55\u8bf7\u6c42\u5931\u8d25\uff0c\u8bf7\u91cd\u8bd5')
    _finish_catalog()

def _install_rpc():
    from entity.ClientAvatar import ClientAvatar
    from common.rpcdecorator import rpc_method, CLIENT_STUB
    from common.RpcMethodArgs import Bool, Int, Str, List
    from common.Md5OrIndexCodec import Md5OrIndexDecoder
    catalog = 'q7InventoryCatalogReply'
    edit = 'q7InventoryEditReply'
    if getattr(ClientAvatar, catalog, None) is None:
        setattr(ClientAvatar, catalog, rpc_method(CLIENT_STUB,
            (Bool('rs'), List('rows'), Int('reason'), Str('op'), Str('g'), Str('q')))(_reply_catalog))
    if getattr(ClientAvatar, edit, None) is None:
        setattr(ClientAvatar, edit, rpc_method(CLIENT_STUB,
            (Bool('rs'), Int('reason'), Str('op')))(_reply_edit))
    # Late setattr is not scanned by EntityFactory.register_entity; wire MD5
    # names must be registered explicitly for Md5OrIndexDecoder.decode.
    Md5OrIndexDecoder.register_str(catalog)
    Md5OrIndexDecoder.register_str(edit)


_UI_EPOCH = 0

# Original grade accent mapping (no new range).
_QUALITY_COLORS = {1: (77, 174, 104), 2: (69, 146, 224), 3: (151, 99, 211),
                   4: (219, 176, 67), 5: (232, 126, 58)}


# Native design-unit typography (see local://editor-native-rewrite-spec.md).
# One design unit is the engine coordinate unit; there is deliberately no
# getWinSize()/1334 multiplier anywhere below.
_FONT_TITLE = 30
_FONT_SECTION = 26
_FONT_BODY = 24
_FONT_META = 24
_FONT_BUTTON = 24
_FONT_TAB = 24
_ROW_H = 88
_TAB_H = 88
_HEADER_H = 88
_SECTION_H = 44
_LEFT_W = 232
_TAB_PAD = 24
_TAB_TOP_GAP = 16
_STACK_GAP = 24
_DETAIL_ICON = 72
# Native checkbox art (`common_confirm_4.checkbox_1` state `sel`) plus its
# 24 pt label renders 43x49 units on device even when given a 32-unit rect.
_CHECK_FOOTPRINT = 49
_CHIP = 32
# Temporary: dump real widget geometry to logcat once per mount.
_DIAG = True
_PAD = 16
_ICON = 72
# Native chrome colours: _FRAME_BG/_DETAIL_BG match the body the shipped
# common_window art paints (measured 236,235,241 on device); list rows keep the
# native white list background. Header art comes from mall_common.title_bar.
_FRAME_BG = (214, 213, 222)
_LIST_BG = (255, 255, 255)
_DETAIL_BG = (236, 235, 243)
_NAV_BG = (212, 210, 220)
_HEADER_BG = (28, 28, 34)
_INK = (63, 68, 87)
_INK_META = (120, 124, 140)


def _nav_width():
    """Left column wide enough for the widest tab label at 24pt plus 2x24 pad."""
    widest = max(_FONT_TAB * len(caption) for _group, caption in _TABS)
    return max(float(_LEFT_W), float(widest + 2 * _TAB_PAD))


def _text(cc, parent, text, x, y, size=_FONT_BODY, color=None, anchor=(0, 0.5)):
    label = cc.ccui.Text.create()
    label.setFontName('cocos/res/hkytw5.ttf')
    label.setFontSize(size)
    label.setString(text)
    label.setColor(cc.cc.Color3B(*(color or (222, 234, 246))))
    label.setAnchorPoint(cc.cc.Vec2(*anchor))
    label.setPosition(cc.cc.Vec2(x, y))
    parent.addChild(label, 5)
    return label


def _caption(cc, card, text, x, y):
    return _text(cc, card, text, x, y, _FONT_META, (90, 96, 112), (1, 0.5))


def _fill(cc, parent, x, y, width, height, color, opacity=255, anchor=(0, 0)):
    node = cc.ccui.Layout.create()
    node.setContentSize(cc.cc.Size(width, height))
    node.setAnchorPoint(cc.cc.Vec2(*anchor))
    node.setPosition(cc.cc.Vec2(x, y))
    node.setLayoutType(cc.ccui.LAYOUT_TYPE_ABSOLUTE)
    node.setBackGroundColorType(1)
    node.setBackGroundColor(cc.cc.Color3B(*color))
    node.setBackGroundColorOpacity(opacity)
    parent.addChild(node, 2)
    return node


def _input(cc, card, placeholder, value, x, y, width, caption=None, height=64,
           digits=False):
    if caption is not None:
        _caption(cc, card, caption, x - width / 2.0 - 12, y)
    border = _fill(cc, card, x, y, width + 4, height + 4,
                   (170, 168, 180), 255, (0.5, 0.5))
    backing = _fill(cc, card, x, y, width, height, (255, 255, 255), 255, (0.5, 0.5))
    field = cc.ccui.TextField.create(placeholder, '', _FONT_BODY)
    field.setContentSize(cc.cc.Size(width - 16, height - 8))
    field.setPosition(cc.cc.Vec2(x, y))
    field.setTextColor(cc.cc.Color4B(48, 52, 66, 255))
    field.setString(value)
    # Without an explicit touch size the field never receives the tap that
    # attaches the IME, so the quantity could only be stepped, never typed.
    # The box is the touch target: the engine's own input view (same one the
    # stock nickname/search dialogs use) is more reliable than the TextField's
    # own IME attach, which did nothing on device.
    _safe(field, 'setTouchSize', cc.cc.Size(0, 0))
    _safe(field, 'setTextVerticalAlignment',
          getattr(cc.cc, 'TEXTVALIGNMENT_CENTER', None))
    _safe(field, 'setAnchorPoint', cc.cc.Vec2(0.5, 0.5))
    _click(backing, lambda: _prompt(cc, field, digits), cc)
    field._f7_box = backing
    field._f7_border = border
    card.addChild(field, 4)
    field._f7_shield = _shield(cc, card, _rect(x - width / 2.0, y - height / 2.0,
                                               width, height),
                               lambda: _prompt(cc, field, digits))
    return field


def _prompt(cc, field, digits=False):
    """Open the stock text input view and write its result into the field."""
    try:
        import cocos.ui_utils as ui_utils
    except Exception:
        return
    try:
        current = field.getString() or u''
    except Exception:
        current = u''

    def apply(value):
        text = u'%s' % (value if value is not None else u'')
        if digits:
            text = u''.join(ch for ch in text if u'0' <= ch <= u'9')
            if len(text) > 7:
                text = text[:7]
            text = u'%d' % (max(0, min(1000000, int(text))) if text else 0)
        _safe(field, 'setString', text)

    try:
        ui_utils.show_input(current, apply, hint=False)
    except Exception:
        pass


def _section(cc, parent, text, x, y, width):
    """Section strip without the native title_static art.

    The stock strip keeps an unloaded tail sprite that renders as a
    checkerboard at the right end of every header; the drawn strip is identical
    in layout (same height, accent bar, 26pt label) and has no artifact.
    """
    return _strip(cc, parent, text, x, y, width)


def _strip(cc, parent, text, x, y, width):
    """Drawn fallback section header, at native 26 design-unit type."""
    strip = _fill(cc, parent, x, y, width, _SECTION_H, (58, 60, 72), 255, (0, 0))
    _fill(cc, strip, 0, 0, 6, _SECTION_H, (72, 220, 230), 255, (0, 0))
    label = _text(cc, strip, text, 16, _SECTION_H / 2.0, _FONT_SECTION,
                  (255, 255, 255), (0, 0.5))
    return strip, label


def _design_metrics(viewport_w, viewport_h):
    """Visible size in engine design units, full screen (no 1334x750 cap)."""
    return {'w': max(1.0, float(viewport_w)), 'h': max(1.0, float(viewport_h))}


def _rect(x, y, w, h):
    """One axis-aligned design-unit rect, parent-local bottom-left origin."""
    return {'x': float(x), 'y': float(y), 'w': float(w), 'h': float(h)}


def _anchor_xy(rect, anchor):
    """Widget position for a rect and the widget's anchor point."""
    return (rect['x'] + float(anchor[0]) * rect['w'],
            rect['y'] + float(anchor[1]) * rect['h'])


def _editor_geometry(w, h, gap=0.0, row_count=0, pool_count=0, quality=True):
    """The single source of truth for every editor rect.

    Each rect is in the coordinate space of the node it is placed in (root,
    nav column, content/list/detail/pool panel, scroll inner container), so
    the mount code never computes a second, parallel position.  Tabs, list
    rows, detail bands/elements and pool rows are all produced here.

    Rows are laid out from the top of an inner container whose height is
    max(viewport, rows * row_h); the scroll is then jumped to the top so row 1
    is fully visible instead of being cut by the viewport.
    """
    w = float(w)
    h = float(h)
    gap = float(gap)
    pad = float(_PAD)
    header_h = float(_HEADER_H)
    body_h = max(1.0, h - header_h)

    header = _rect(0.0, body_h, w, header_h)
    close = _rect(w - gap - 76.0, (header_h - 56.0) / 2.0, 64.0, 56.0)
    title = _rect(gap + 32.0, header_h / 2.0 - _FONT_TITLE / 2.0,
                  max(32.0, w - 2.0 * gap - 160.0), float(_FONT_TITLE))

    # One nav width drives the grey column, the cell width, the label centre
    # and the content panel's left edge. On a narrow viewport the column gives
    # way first so the list and detail panels keep a usable minimum.

    nav_w = min(_nav_width(), max(120.0, (w - gap) * 0.24))
    # x=0 shifted every tab label off the column centre on MACHINE_FIX hosts.
    nav = _rect(gap, 0.0, nav_w, body_h)
    nav_right = nav['x'] + nav['w']
    content_w = max(1.0, w - nav_right - gap)
    content = _rect(nav_right, pad, content_w, max(160.0, body_h - 2.0 * pad))

    # Two columns of fixed-size buttons instead of one full-width strip per
    # tab: a stretched cell reads as a bar, and a second column leaves room
    # for more entries without growing the column. A column too narrow for
    # two 24pt labels falls back to one column so the text still fits.
    tab_gap = 12.0
    glyph = _FONT_TAB * 4 + 2 * 8
    tab_cols = 2 if nav_w >= 2 * glyph + 3 * tab_gap else 1
    tab_w = (nav_w - (tab_cols + 1) * tab_gap) / tab_cols
    tab_h = 56.0
    tabs = []
    for index in range(len(_TABS)):
        col = index % tab_cols
        row = index // tab_cols
        tabs.append(_rect(tab_gap + col * (tab_w + tab_gap),
                          body_h - _TAB_TOP_GAP - (row + 1) * tab_h - row * tab_gap,
                          tab_w, tab_h))

    panel_h = content['h']
    # 0.58/0.42 split, then clamped so neither panel drops below a usable
    # width on a 1024-unit-wide tablet in landscape.
    list_w = content_w * 0.58 - pad
    min_w = min(280.0, (content_w - pad) / 2.0)
    if list_w < min_w:
        list_w = min_w
    detail_l = max(list_w, content_w * 0.58)
    detail_w = max(1.0, content_w - detail_l - pad)
    if detail_w < min_w:
        detail_w = min_w
        detail_l = max(0.0, content_w - detail_w - pad)
        list_w = max(1.0, detail_l - pad) if detail_l > 0 else list_w
    list_panel = _rect(0.0, 0.0, list_w, panel_h)
    detail_panel = _rect(detail_l, 0.0, detail_w, panel_h)
    pool_panel = _rect(0.0, 0.0, content['w'], panel_h)
    bulk_panel = _rect(0.0, 0.0, content['w'], panel_h)
    bulk_rows = []
    # The status line owns its band; rows are laid out above it so a growing
    # list can never push text onto the status or off the panel.
    bulk_status = _rect(pad, 24.0, max(1.0, content['w'] - 2.0 * pad), 28.0)
    bulk_top = panel_h - _SECTION_H - 8.0
    bulk_bottom = bulk_status['y'] + bulk_status['h'] + 16.0
    bulk_gap = 8.0
    bulk_usable = max(1.0, content['w'] - 2.0 * pad)
    bulk_columns = 2 if bulk_usable >= 2.0 * _BULK_MIN_W + bulk_gap else 1
    bulk_count = (len(_BULK) + bulk_columns - 1) // bulk_columns
    bulk_w = min((bulk_usable - (bulk_columns - 1) * bulk_gap) / bulk_columns,
                 _BULK_MAX_W)
    bulk_row_h = min(_BULK_MAX_H, max(48.0, (
        bulk_top - bulk_bottom - (bulk_count - 1) * bulk_gap) / float(bulk_count)))
    for index in range(len(_BULK)):
        column = index % bulk_columns
        row = index // bulk_columns
        bulk_rows.append(_rect(
            pad + column * (bulk_w + bulk_gap),
            bulk_top - (row + 1) * bulk_row_h - row * bulk_gap,
            bulk_w, bulk_row_h))

    section_y = panel_h - _SECTION_H
    list_header = _rect(0.0, section_y, list_w, float(_SECTION_H))
    detail_header = _rect(0.0, section_y, detail_w, float(_SECTION_H))
    pool_header = _rect(0.0, section_y, content['w'], float(_SECTION_H))

    search_center = section_y - 12.0 - 44.0
    field_w = max(120.0, list_w - 2.0 * pad - 128.0)
    list_search = _rect(pad, search_center - 32.0, field_w, 64.0)
    list_query = _rect(list_w - pad - 112.0, search_center - 44.0, 112.0, 88.0)

    scroll_bottom = 64.0
    scroll_h = max(48.0, search_center - 52.0 - scroll_bottom)
    row_w = max(1.0, list_w - 2.0 * pad)
    scroll = _rect(pad, scroll_bottom, row_w, scroll_h)
    # Catalog pager: the reply is a bounded slice, so the list needs explicit
    # page controls below the scroll (a 380-entry treasure table otherwise
    # showed only its first 50 rows). scroll_bottom keeps rows out of the
    # 8..48 page band.
    pager_h = 40.0
    pager_w = min(160.0, max(96.0, row_w * 0.22))
    picker_prev = _rect(pad, 8.0, pager_w, pager_h)
    picker_next = _rect(list_w - pad - pager_w, 8.0, pager_w, pager_h)
    picker_label = _rect(picker_prev['w'] + 2.0 * pad, 8.0,
                         max(1.0, list_w - 2.0 * (pad + pager_w) - 2.0 * pad),
                         pager_h)
    container_h = max(scroll_h, float(row_count) * _ROW_H)
    rows = [_rect(0.0, container_h - (index + 1) * _ROW_H, row_w,
                  float(_ROW_H)) for index in range(int(row_count))]

    check = float(_CHECK_FOOTPRINT)
    detail_space = max(1.0, detail_w - 2.0 * pad)
    # Two chips side by side need their label footprints; the icon gives way
    # first, then the icon shrinks with the panel instead of pushing the stack
    # past the bottom edge.
    icon_size = max(24.0, min(float(_DETAIL_ICON), detail_space * 0.16))
    quality_x = pad
    quality_pitch = check + 8.0 + _FONT_BODY
    quality_span = max(1.0, detail_w - pad - quality_x)
    quality_cols = max(1, min(5, int(quality_span // quality_pitch)))
    quality_rows = (5 + quality_cols - 1) // quality_cols
    quality_step = quality_pitch if quality_cols < 5 else quality_span / 5.0

    bands = _detail_stack(panel_h, quality_rows, icon_size, quality=quality)

    def band(name):
        bottom, top = bands[name]
        return _rect(pad, bottom, detail_w - 2.0 * pad, top - bottom)

    detail_bands = dict((name, band(name)) for name in
                        ('icon', 'held', 'mode', 'quality_label', 'quality',
                         'quantity', 'stepper', 'status', 'actions')
                        if name in bands)
    icon_center = (bands['icon'][0] + bands['icon'][1]) / 2.0
    detail_icon = _rect(pad, icon_center - icon_size / 2.0, icon_size, icon_size)
    name_x = pad + icon_size + 12.0
    detail_name = _rect(name_x, icon_center,
                        max(1.0, detail_w - pad - name_x), float(_FONT_BODY))
    held_h = bands['held'][1] - bands['held'][0]
    held_label_w = min(136.0, detail_space * 0.42)
    held_label = _rect(pad, bands['held'][0], held_label_w, held_h)
    held_value = _rect(pad + held_label_w, bands['held'][0],
                       max(1.0, detail_space - held_label_w), held_h)

    # Two equal cells across the band so the mode row shares the quality row's
    # left and right margins instead of a fixed pitch that left the right half
    # of the panel empty.
    mode_gap = 16.0
    mode_cell = max(check + 10.0 + _FONT_BODY * 2,
                    (detail_space - mode_gap) / 2.0)
    modes = [_rect(pad + index * (mode_cell + mode_gap), bands['mode'][0],
                   check, check) for index in range(2)]
    mode_labels = [_rect(item['x'] + check + 10.0, bands['mode'][0],
                         max(1.0, mode_cell - check - 10.0), item['h'])
                   for item in modes]
    if quality:
        quality_label = _rect(pad, bands['quality_label'][0], 60.0,
                              bands['quality_label'][1] - bands['quality_label'][0])
        # The quality label owns its own band, so the chips use the full panel
        # width: a 60-unit right offset pushed them into two rows and squeezed
        # every gap in the stack.
        quality_rects = [
            _rect(quality_x + (index % quality_cols) * quality_step,
                  bands['quality'][0] + (index // quality_cols) * check,
                  check, check) for index in range(5)]
        quality_labels = [_rect(item['x'] + check + 6.0, item['y'],
                                check, item['h']) for item in quality_rects]
    else:
        quality_label = _rect(pad, 0.0, 0.0, 0.0)
        quality_rects = []
        quality_labels = []

    quantity_label = band('quantity')
    stepper_bottom = bands['stepper'][0]
    stepper_step = 16.0
    stepper_space = max(96.0, detail_w - 2.0 * pad)
    minus_w = min(88.0, stepper_space * 0.28)
    plus_w = minus_w
    count_w = max(56.0, stepper_space - minus_w - plus_w - 2 * stepper_step)
    # Same height and baseline for all three controls: the 48-unit field with
    # a +4 offset read as a misaligned row next to the 56-unit steppers.
    minus = _rect(pad, stepper_bottom, minus_w, 56.0)
    count = _rect(pad + minus_w + stepper_step, stepper_bottom,
                  count_w, 56.0)
    plus = _rect(pad + minus_w + stepper_step + count_w + stepper_step,
                 stepper_bottom, plus_w, 56.0)
    status = band('status')

    action_space = detail_space
    action_gap = 16.0
    cta_w = min(220.0, max(96.0, action_space * 0.45))
    cta = _rect(detail_w - pad - cta_w, bands['actions'][0], cta_w, 72.0)
    pending_w = max(0.0, detail_w - pad - cta_w - action_gap - pad)
    pending = _rect(pad, bands['actions'][0], pending_w, 72.0)

    # Chips reserve their full label footprint for the overlap audit; the
    # native checkbox widget itself is the square `check` rect, and the
    # caption is drawn as a panel-space sibling to the right of it.
    mode_foot = [_rect(item['x'], item['y'],
                       check + 10.0 + _FONT_BODY * len(label), item['h'])
                 for item, label in zip(modes, (u'\u8bbe\u4e3a', u'\u589e\u52a0'))]
    quality_foot = [_rect(item['x'], item['y'],
                          item['w'] + 8.0 + _FONT_BODY, item['h'])
                    for item in quality_rects]
    detail_elements = [('icon', detail_icon), ('name', detail_name),
                       ('held_label', held_label), ('held_value', held_value),
                       ('mode:set', mode_foot[0]), ('mode:add', mode_foot[1]),
                       ('quality_label', quality_label)]
    detail_elements += [('quality:%d' % (index + 1), rect)
                        for index, rect in enumerate(quality_foot)]
    detail_elements += [('quantity_label', quantity_label), ('minus', minus),
                        ('count', count), ('plus', plus), ('status', status),
                        ('pending', pending), ('cta', cta)]

    # Pool bar: field, search button, close button share the content width,
    # shrinking in that order instead of overrunning a narrow viewport.
    pool_space = max(160.0, content['w'] - 2.0 * pad)
    btn = min(88.0, pool_space * 0.12)
    close_w = min(200.0, pool_space * 0.26)
    field_w = max(80.0, pool_space - btn - close_w - 2 * 16.0)
    pool_field = _rect(pad, search_center - 32.0, field_w, 64.0)
    pool_search_btn = _rect(pad + field_w + 16.0, search_center - btn / 2.0,
                            btn, btn)
    pool_close = _rect(content['w'] - pad - close_w, search_center - btn / 2.0,
                       close_w, btn)
    pool_scroll = _rect(pad, scroll_bottom,
                        max(1.0, content['w'] - 2.0 * pad), scroll_h)
    pool_container_h = max(scroll_h, float(pool_count) * _ROW_H)
    pool_rows = [_rect(0.0, pool_container_h - (index + 1) * _ROW_H,
                       pool_scroll['w'], float(_ROW_H))
                 for index in range(int(pool_count))]
    page_y = 28.0
    pager = min(120.0, pool_space * 0.18)
    pool_prev = _rect(pad, page_y - 28.0, pager, 56.0)
    pool_page_label = _rect(pad + pager + 8.0, page_y - 12.0, 40.0, 24.0)
    pool_next = _rect(pad + pager + 56.0, page_y - 28.0, pager, 56.0)
    status_x = pad + 2.0 * pager + 72.0
    pool_status = _rect(status_x, page_y - 12.0,
                        max(1.0, pool_space * 0.4), 24.0)
    pool_note = _rect(content['w'] - pad - min(300.0, pool_space * 0.42),
                      page_y - 12.0, min(300.0, pool_space * 0.42), 24.0)

    return {
        'w': w, 'h': h, 'gap': gap, 'body_h': body_h, 'panel_h': panel_h,
        'header': header, 'title': title, 'close': close,
        'nav': nav, 'nav_width': nav_w, 'nav_right': nav_right,
        'tab_h': tab_h, 'tab_w': tab_w,
        'tabs': tabs, 'content': content,
        'list': list_panel, 'detail': detail_panel, 'pool': pool_panel,
        'list_header': list_header, 'detail_header': detail_header,
        'pool_header': pool_header,
        'list_search': list_search, 'list_query': list_query,
        'list_prev': picker_prev, 'list_next': picker_next,
        'list_page': picker_label,
        'scroll': scroll, 'scroll_container_h': container_h, 'rows': rows,
        'detail_bands': detail_bands,
        'detail_band_rects': _detail_rects(bands, detail_w, pad),
        'detail_elements': detail_elements,
        'detail_icon': detail_icon, 'detail_name': detail_name,
        'held_label': held_label, 'held_value': held_value,
        'modes': modes, 'mode_labels': mode_labels,
        'quality_label': quality_label, 'quality': quality_rects,
        'quality_labels': quality_labels,
        'quantity_label': quantity_label,
        'minus': minus, 'count': count, 'plus': plus, 'status': status,
        'cta': cta, 'pending': pending, 'check_size': check,
        'bulk': bulk_panel, 'bulk_rows': bulk_rows, 'bulk_status': bulk_status,
        'pool_search': pool_field, 'pool_search_button': pool_search_btn,
        'pool_close': pool_close, 'pool_scroll': pool_scroll,
        'pool_container_h': pool_container_h, 'pool_rows': pool_rows,
        'pool_prev': pool_prev, 'pool_next': pool_next,
        'pool_page_label': pool_page_label, 'pool_status': pool_status,
        'pool_note': pool_note,
    }


def _register_geom(name, node, rect, anchor=(0.0, 0.0), check_size=True):
    """Record a placed widget beside the rect it was placed from."""
    if node is None:
        return node
    table = _VIEW.get('geo_widgets')
    if table is None:
        table = {}
        _VIEW['geo_widgets'] = table
    table[name] = {'node': node, 'rect': dict(rect),
                   'anchor': (float(anchor[0]), float(anchor[1])),
                   'check_size': bool(check_size)}
    return node


def _place_rect(node, rect, anchor=(0.0, 0.0)):
    """Place a widget solely from its geometry rect and anchor."""
    import cocosui as cc
    if node is None:
        return None
    node.setAnchorPoint(cc.cc.Vec2(*anchor))
    node.setContentSize(cc.cc.Size(rect['w'], rect['h']))
    node.setPosition(cc.cc.Vec2(*_anchor_xy(rect, anchor)))
    return node


def _cutout_fixed():
    """Same predicate as ui_panel.py:262-277 for `*_iphonex_*` margins."""
    try:
        import profiling
        import com.data.cdata.machine_fix as MACHINE_FIX
        return profiling.get_device_model().lower() in MACHINE_FIX.data
    except Exception:
        return False


def _cutout_gap():
    """const.IPHONEX_FIX_GAP (88) on MACHINE_FIX devices, 0 elsewhere."""
    if not _cutout_fixed():
        return 0
    try:
        import com.const as const
        return int(const.IPHONEX_FIX_GAP)
    except Exception:
        return 0


def _safe(node, method, *args):
    try:
        func = getattr(node, method, None)
        if callable(func):
            return func(*args)
    except Exception:
        pass
    return None


def _apply_iphonex(node):
    """Native `*_iphonex_left/right` margin handling (ui_panel.py:262-277).

    Runs on a loaded csb panel and on the editor card so csb nodes that carry
    the suffix get the same +IPHONEX_FIX_GAP margin as native panels.
    """
    if node is None:
        return
    fixed = _cutout_fixed()
    try:
        gap = int(__import__('com.const', fromlist=['IPHONEX_FIX_GAP']).IPHONEX_FIX_GAP)
    except Exception:
        gap = 88
    try:
        children = list(node.getChildren())
    except Exception:
        return
    for layout in children:
        try:
            name = layout.getName()
        except Exception:
            continue
        if name.endswith('_iphonex_left'):
            suffix = '_iphonex_left'
            side = 'left'
        elif name.endswith('_iphonex_right'):
            suffix = '_iphonex_right'
            side = 'right'
        else:
            continue
        _safe(layout, 'setName', name[0:-len(suffix)])
        if not fixed:
            continue
        try:
            parameter = layout.getLayoutParameter()
            margin = parameter.getMargin()
            if side == 'left':
                margin.left = margin.left + gap
            else:
                margin.right = margin.right + gap
            parameter.setMargin(margin)
            node.requestDoLayout()
        except Exception:
            pass


def _load_csb(name):
    """Load a shipped csb panel node exactly like ui_panel.UIPanel.load."""
    try:
        import cocosui as cc
        import gg
        try:
            info = getattr(getattr(gg, 'ui', None), 'projplistinfo', None) or {}
            for plist in info.get(name + '.json', []):
                cc.cc.SpriteFrameCache.getInstance().addSpriteFrames('cocos/' + plist)
        except Exception:
            pass
        reader = cc.ccs.GUIReader.getInstance()
        import com.const as const
        if getattr(const, 'DEBUG_UI_JSON', False):
            return reader.widgetFromJsonFile('cocos/%s.json' % name, True)
        return reader.widgetFromBinaryFile('cocos/%s.csb' % name, True)
    except Exception:
        return None


def _csb_root(name):
    cache = _VIEW.get('csb')
    if cache is None:
        cache = {}
        _VIEW['csb'] = cache
    if name not in cache:
        cache[name] = _load_csb(name)
    return cache[name]


def _csb_child(node, path):
    current = node
    for part in path.split('.'):
        if current is None:
            return None
        getter = getattr(current, 'getChildByName', None)
        if not callable(getter):
            return None
        try:
            current = getter(part)
        except Exception:
            return None
    return current


def _clone_node(node):
    if node is None:
        return None
    try:
        return node.clone()
    except Exception:
        return None


def _comp_get(comp, path):
    if comp is None:
        return None
    try:
        return comp[path]
    except Exception:
        return None


def _load_comp(pack, name, run_load=True):
    """Clone a native csb comp through gg.ui.comps.<pack>.<name>; None if absent."""
    try:
        import gg
        packs = getattr(getattr(gg, 'ui', None), 'comps', None)
        if packs is None:
            return None
        module = getattr(packs, pack, None)
        if module is None:
            return None
        comp = getattr(module, name, None)
        if comp is None or getattr(comp, '_node', None) is None:
            return None
        if run_load:
            try:
                comp.load()
            except Exception:
                pass
        return comp
    except Exception:
        return None


def _native_confirm_nodes():
    """cocos/common_confirm_4.csb `main.info` button/checkbox templates."""
    main = _csb_child(_csb_root('common_confirm_4'), 'main')
    info = _csb_child(main, 'info')
    if info is None:
        return None, None, None
    return (info, info.getChildByName('btn_confirm'),
            info.getChildByName('checkbox_1'))


def _button_event(cc, events, callback, event):
    """One listener per button: an optional event hook, then the tap callback."""
    if events is not None:
        try:
            events(event)
        except Exception:
            pass
    if event == cc.ccui.TOUCH_EVENT_ENDED:
        callback()


def _probe_button(cc, name, node):
    """Report every carrier that could draw a native button's title."""
    if node is None:
        return
    try:
        size = node.getContentSize()
        pos = node.getPosition()
        anchor = node.getAnchorPoint()
        world = node.convertToWorldSpace(cc.cc.Vec2(0, 0))
        print('P7GEO probe %s node pos=%.1f,%.1f size=%.1f,%.1f anchor=%.1f,%.1f '
              'world0=%.1f,%.1f' % (name, pos.x, pos.y, size.width, size.height,
                                    anchor.x, anchor.y, world.x, world.y))
    except Exception as error:
        print('P7GEO probe %s node failed %s' % (name, error))
    try:
        skin = node.getVirtualRenderer()
        if skin is not None:
            art = skin.getContentSize()
            spot = skin.getPosition()
            anch = skin.getAnchorPoint()
            centre = skin.convertToWorldSpace(
                cc.cc.Vec2(art.width * anch.x, art.height * anch.y))
            print('P7GEO probe %s skin size=%.1f,%.1f at=%.1f,%.1f anchor=%.1f,%.1f '
                  'worldcentre=%.1f,%.1f' % (name, art.width, art.height, spot.x,
                                             spot.y, anch.x, anch.y, centre.x, centre.y))
    except Exception as error:
        print('P7GEO probe %s skin failed %s' % (name, error))
    try:
        getter = getattr(node, 'getTitleRenderer', None)
        title = getter() if callable(getter) else None
        if title is not None:
            spot = title.getPosition()
            art = title.getContentSize()
            print('P7GEO probe %s title pos=%.1f,%.1f size=%.1f,%.1f text=%r' % (
                name, spot.x, spot.y, art.width, art.height,
                getattr(title, 'getString', lambda: '?')()))
    except Exception as error:
        print('P7GEO probe %s title failed %s' % (name, error))
    _dump_children(node, 'probe:%s' % name, depth=1)


def _native_button(cc, parent, text, x, y, width, height, callback, primary=True,
                   events=None):
    """Native csb button (common_confirm_4 btn_confirm/btn_cancel) + title child."""
    info, confirm, _unused = _native_confirm_nodes()
    template = confirm if primary else _csb_child(info, 'btn_cancel')
    node = _clone_node(template)
    if node is None:
        return None
    try:
        node.setVisible(True)
        node.setTouchEnabled(True)
        node.setContentSize(cc.cc.Size(width, height))
        node.setAnchorPoint(cc.cc.Vec2(0.5, 0.5))
        node.setPosition(cc.cc.Vec2(x, y))
        try:
            node.ignoreContentAdaptWithSize(False)
        except Exception:
            pass
        # The cloned button's renderer keeps the csb art size (230x70 on
        # device) whatever setContentSize does. Its anchor is the art centre,
        # which the csb already placed on the node origin; the original
        # comps only setString and setVisible (huacaiji_common/tab_1). Scale
        # the art around that centre so the authored title position stays the
        # rect centre; moving the renderer instead pushed every title onto a
        # rect corner (device r67/r71 probes).
        try:
            node.setClippingEnabled(True)
        except Exception:
            pass
        try:
            renderer = node.getVirtualRenderer()
            art = renderer.getContentSize()
            if art.width > 0 and art.height > 0:
                renderer.setScaleX(float(width) / art.width)
                renderer.setScaleY(float(height) / art.height)
        except Exception:
            pass
        _native_title(node, text)
        _safe(node, 'setTitleFontSize', _FONT_BUTTON)
        node.addTouchEventListener(
            lambda sender, event: _button_event(cc, events, callback, event))
        node._f7_kind = 'native_button'
        node._f7_native = True
        _VIEW['native_skin'] = True
        return node
    except Exception:
        return None


def _first_label(node):
    found = []
    def walk(current):
        for child in getattr(current, 'getChildren', lambda: [])():
            if callable(getattr(child, 'setString', None)):
                found.append(child)
            walk(child)
    walk(node)
    return found[0] if found else None


def _title_children(node):
    """The csb state children that carry a native button's baked title."""
    found = []

    def add(child):
        if child is not None and child not in found and \
                callable(getattr(child, 'setString', None)):
            found.append(child)

    getter = getattr(node, 'getChildByName', None)
    if callable(getter):
        for name in ('text_nml', 'text_gry', 'text', 'title'):
            try:
                add(getter(name))
            except Exception:
                pass
    for child in getattr(node, 'getChildren', lambda: [])():
        try:
            name = child.getName() or ''
        except Exception:
            name = ''
        if name.startswith('Button_'):
            add(child)
    return found


def _native_title(node, text, label=None):
    """Write a cloned native button's label onto its title child(ren).

    `common_confirm_4.csb` buttons bake their own title text into child nodes
    (`text_nml` / `text_gry`, the convention setting.py:164-165 drives). A
    Button's internal title renderer is separate from those children, so
    setTitleText alone leaves the baked string visible and can double-draw.
    Set the child strings first, keep the normal state and hide the grey one,
    then sync setTitleText last. `label` lets a checkbox chip pass its own
    title node.
    """
    if node is None:
        return None
    node._f7_text = text
    titled = []
    if label is not None:
        titled.append(label)
    for child in _title_children(node):
        if child not in titled:
            titled.append(child)
    if not titled:
        first = _first_label(node)
        if first is not None:
            titled.append(first)
    main = []
    for child in titled:
        name = ''
        try:
            name = child.getName() or ''
        except Exception:
            name = ''
        if not name.lower().endswith('_gry'):
            main.append(child)
    visible = main or titled
    for child in titled:
        _safe(child, 'setString', text)
        _safe(child, 'setFontSize', _FONT_BUTTON)
        _safe(child, 'setVisible', child in visible)
        if child in visible:
            # The csb authors the title on the button centre; only font and
            # string change here, as the original comps do. Re-positioning it
            # for the stretched rect is what pushed titles onto a corner.
            _safe(child, 'ignoreContentAdaptWithSize', True)
    # Only after the children are correct; this covers the separate title renderer.
    if callable(getattr(node, 'setTitleText', None)):
        try:
            node.setTitleText(text)
        except Exception:
            pass
        # A csb Button can own a renderer distinct from the authored
        # text_nml/text_gry children. If so, clear it so the child is the
        # single visible title instead of two identical stacked strings.
        getter = getattr(node, 'getTitleRenderer', None)
        if callable(getter):
            try:
                renderer = getter()
            except Exception:
                renderer = None
            if renderer is not None and renderer not in titled:
                try:
                    node.setTitleText(u'')
                except Exception:
                    pass
    node._f7_label = titled[0] if titled else None
    return node._f7_label


def _native_label(node, text, color=None):
    labels = []
    def walk(current):
        for child in getattr(current, 'getChildren', lambda: [])():
            if callable(getattr(child, 'setString', None)):
                labels.append(child)
            walk(child)
    walk(node)
    for label in labels:
        try:
            label.setString(text)
            if color is not None:
                label.setColor(color)
        except Exception:
            pass
    if not labels and callable(getattr(node, 'setTitleText', None)):
        try:
            node.setTitleText(text)
        except Exception:
            pass


def _native_check(cc, parent, x, y, size, callback, selected):
    """Native checkbox from common_confirm_4 (state child `sel`) or setting (`active`)."""
    _info, _confirm, checkbox = _native_confirm_nodes()
    node = _clone_node(checkbox)
    if node is None:
        return None
    try:
        node.setVisible(True)
        node.setTouchEnabled(True)
        node.setContentSize(cc.cc.Size(size, size))
        node.setAnchorPoint(cc.cc.Vec2(0.5, 0.5))
        node.setPosition(cc.cc.Vec2(x, y))
        # The csb checkbox children (`sel`, `checkbox`, the baked label) keep
        # their authored positions, which sit well outside a resized node.
        # Recenter every state sprite on the node and drop the baked label;
        # the chip draws its own text beside the box.
        try:
            for child in node.getChildren():
                if callable(getattr(child, 'setString', None)):
                    child.setVisible(False)
                    continue
                # Child positions are measured from the node's anchor point,
                # so (0, 0) is the box centre; (size/2, size/2) drew the art
                # half a box up-right of the caption row.
                child.setPosition(cc.cc.Vec2(0, 0))
                # The state sprite's renderer ignores the child's anchor and
                # keeps its own, so it draws from the child center offset by
                # that anchor. Pull it back so the art centre lands on the box.
                renderer = getattr(child, 'getVirtualRenderer', lambda: None)()
                if renderer is None:
                    continue
                art = renderer.getContentSize()
                scale = 1.0
                if art.width > size or art.height > size:
                    scale = float(size) / max(art.width, art.height)
                    renderer.setScaleX(scale)
                    renderer.setScaleY(scale)
                anchor = renderer.getAnchorPoint()
                renderer.setPosition(cc.cc.Vec2(
                    (0.5 - anchor.x) * art.width * scale,
                    (0.5 - anchor.y) * art.height * scale))
        except Exception:
            pass
        state = node.getChildByName('active')
        if state is None:
            state = node.getChildByName('sel')
        if state is not None:
            state.setVisible(selected)
        node.addTouchEventListener(
            lambda sender, event: callback() if event == cc.ccui.TOUCH_EVENT_ENDED else None)
        node._f7_kind = 'native_check'
        node._f7_native = True
        node._f7_check = state
        _VIEW['native_skin'] = True
        return node
    except Exception:
        return None


def _section_native(cc, parent, text, x, y, width):
    """Native section strip (common_info.title_static) at the full panel width.

    `title_static.set_title` sizes its own bg to the label + TITLE_TAIL, which
    is why the device strip stopped short of the panel. Override both the
    component node and its `bg` to `width` so the native art spans the panel.
    """
    comp = _load_comp('common_info', 'title_static')
    if comp is not None:
        label = _comp_get(comp, 'bg.label')
        bg = _comp_get(comp, 'bg')
        _safe(comp, 'set_title', text)
        # title_static ships four extra state panels (break/awake x now/need)
        # beside `bg`. They stay visible from the csb and drew their unloaded
        # frames as checkerboards at the strip's right end; the native
        # consumers call useBreak/useAwake to leave exactly one visible.
        _safe(comp, 'useBreak', 0)
        # Belt and braces: keep only `bg` (which owns the label).  Whatever the
        # extra state panels are called in this csb, their unloaded frames drew
        # checkerboards at the strip's right end.
        strip_node = getattr(comp, '_node', None)
        if strip_node is not None:
            try:
                for child in strip_node.getChildren():
                    if child.getName() != 'bg':
                        _safe(child, 'setVisible', False)
            except Exception:
                pass
        if label is not None:
            _safe(label, 'setString', text)
            _safe(label, 'setFontSize', _FONT_SECTION)
            _safe(label, 'setAnchorPoint', cc.cc.Vec2(0, 0.5))
            _safe(label, 'setPosition', cc.cc.Vec2(16, _SECTION_H / 2.0))
        if bg is not None:
            _safe(bg, 'ignoreContentAdaptWithSize', False)
            _safe(bg, 'setAnchorPoint', cc.cc.Vec2(0, 0))
            _safe(bg, 'setPosition', cc.cc.Vec2(0, 0))
            _safe(bg, 'setContentSize', cc.cc.Size(width, _SECTION_H))
            try:
                for child in bg.getChildren():
                    if not callable(getattr(child, 'setString', None)):
                        _safe(child, 'setVisible', False)
            except Exception:
                pass
        node = getattr(comp, '_node', None)
        if node is not None:
            node.setVisible(True)
            _safe(node, 'ignoreContentAdaptWithSize', False)
            _safe(node, 'setContentSize', cc.cc.Size(width, _SECTION_H))
            _safe(node, 'setAnchorPoint', cc.cc.Vec2(0, 0))
            _safe(node, 'setPosition', cc.cc.Vec2(x, y))
            parent.addChild(node, 4)
            node._f7_native = True
            _VIEW['native_skin'] = True
            return node, label
    return _strip(cc, parent, text, x, y, width)


def _detail_stack(panel_h, quality_rows=1, icon_size=None, quality=True):
    """One top-to-bottom detail column with 24-unit gaps.

    Returns {name: (bottom, top)} bands. The icon/name block sits directly
    below the title_static strip and the action row on the panel's bottom
    edge: at design height the nine bands plus eight 24-unit gaps fill the
    panel exactly, so no slack is left over. The gap shrinks on a viewport
    shorter than the design height, never below 8 units, and the icon and the
    quality row give way before anything overlaps: `quality_rows` is the row
    count the detail width forced, `icon_size` the icon that still fits.
    `quality=False` drops the two quality bands entirely, which is the layout
    for every row type that never shows them.
    """
    icon = float(_DETAIL_ICON) if icon_size is None else float(icon_size)
    quality_h = float(_CHECK_FOOTPRINT) * max(1, int(quality_rows))
    items = [('icon', icon), ('held', 24.0), ('mode', float(_CHECK_FOOTPRINT))]
    if quality:
        items += [('quality_label', 24.0), ('quality', quality_h)]
    items += [('quantity', 24.0), ('stepper', 56.0), ('status', 24.0),
              ('actions', 72.0)]
    gap = float(_STACK_GAP)
    limit = max(1.0, float(panel_h) - _SECTION_H)
    total = sum(height for _name, height in items)
    gaps = len(items) - 1
    if gaps > 0 and total + gap * gaps > limit:
        gap = max(8.0, (limit - total) / float(gaps))
    # The gap floor is not enough on a short panel: shrink the action row
    # rather than letting its bottom go negative.
    overflow = total + gap * gaps - limit
    if overflow > 0:
        items = list(items)
        name, height = items[-1]
        items[-1] = (name, max(40.0, height - overflow))
    top = limit
    bands = {}
    for name, height in items:
        bands[name] = (top - height, top)
        top = top - height - gap
    return bands


def _detail_rects(bands, detail_w, pad):
    """Recorded axis-aligned detail rects: used by the host non-overlap test."""
    rects = []
    for name in ('icon', 'held', 'mode', 'quality_label', 'quality',
                 'quantity', 'stepper', 'status', 'actions'):
        if name not in bands:
            continue
        bottom, top = bands[name]
        rects.append({'name': name, 'x': float(pad), 'y': float(bottom),
                      'w': float(detail_w) - 2.0 * pad,
                      'h': float(top - bottom)})
    return rects


def _button(cc, parent, text, x, y, width, callback, height=52, primary=False,
            selected=False, events=None):
    native = _native_button(cc, parent, text, x, y, width, height, callback,
                            primary=primary, events=events)
    if native is not None:
        parent.addChild(native, 6)
        return native
    if primary:
        _fill(cc, parent, x, y, width + 4, height + 4,
              (72, 220, 230), 255, (0.5, 0.5))
        color, title = (24, 24, 30), (255, 255, 255)
    elif selected:
        color, title = (38, 72, 88), (245, 253, 255)
    else:
        color, title = (226, 224, 232), (63, 68, 87)
    backing = _fill(cc, parent, x, y, width, height, color, 255, (0.5, 0.5))
    backing.setTouchEnabled(True)
    backing.addTouchEventListener(
        lambda sender, event: _button_event(cc, events, callback, event))
    label = _text(cc, backing, text, width / 2.0, height / 2.0, _FONT_BUTTON,
                  title, (0.5, 0.5))
    backing._f7_backing = backing
    backing._f7_label = label
    backing._f7_text = text
    backing._f7_primary = primary
    return backing


def _chip(cc, parent, text, x, y, size, callback, selected=False, caption=None):
    """Native checkbox with a 24pt label; drawn square only when the csb is absent.

    `caption` gives a panel-space (x, y) for the label. A checkbox child keeps
    its own authored coordinate frame, which put the caption under the box;
    drawing it beside the box in panel coordinates keeps every chip label on
    the same baseline as the rest of the detail column.
    """
    node = _native_check(cc, parent, x, y, size, callback, selected)
    if node is not None:
        parent.addChild(node, 6)
        if caption is not None:
            _safe(node, 'setTitleText', u'')
            label = _text(cc, parent, text, caption[0], caption[1], _FONT_BODY,
                          (63, 68, 87), (0, 0.5))
        else:
            label = _text(cc, node, text, size, 0, _FONT_BODY,
                          (63, 68, 87), (0, 0.5))
            _native_title(node, text, label=label)
        node._f7_label = label
        node._f7_text = text
        return node
    label_size = _FONT_BODY
    label_w = max(size, (len(u'%s' % text) + 0.5) * label_size)
    box_w = size + 8 + label_w
    box_h = size + 4
    box = _fill(cc, parent, x, y, box_w, box_h, (228, 226, 234), 0, (0.5, 0.5))
    box.setTouchEnabled(True)
    cx, cy = size / 2.0 + 2, box_h / 2.0
    outline = _fill(cc, box, cx, cy, size + 4, size + 4,
                    (120, 130, 150), 255, (0.5, 0.5))
    inner = _fill(cc, box, cx, cy, size, size,
                  (72, 220, 230) if selected else (40, 44, 60), 255, (0.5, 0.5))
    # hkytw5 has no U+2713 glyph (renders as a fallback box); ASCII x is the
    # drawn-path check mark and is covered by the font.
    check = _text(cc, box, u'x', cx, cy, _FONT_BODY,
                  (30, 38, 46), (0.5, 0.5))
    check.setVisible(selected)
    label = _text(cc, box, text, size + 10, cy, label_size,
                  (63, 68, 87), (0, 0.5))
    box.addTouchEventListener(
        lambda sender, event: callback() if event == cc.ccui.TOUCH_EVENT_ENDED else None)
    box._f7_outline = outline
    box._f7_backing = inner
    box._f7_check = check
    box._f7_label = label
    box._f7_text = text
    return box


def _style(button, selected=False, primary=False):
    cc = __import__('cocosui').cc
    kind = getattr(button, '_f7_kind', None)
    if kind == 'native_check':
        state = getattr(button, '_f7_check', None)
        if state is not None:
            _safe(state, 'setVisible', bool(selected))
        return
    if kind == 'native_button':
        title = cc.Color3B(*(245, 253, 255) if (primary or selected) else (63, 68, 87))
        for child in _title_children(button):
            _safe(child, 'setColor', title)
        _safe(button, 'setTitleColor', title)
        return
    outline = getattr(button, '_f7_outline', None)
    backing = getattr(button, '_f7_backing', None)
    if outline is not None and backing is not None:
        try:
            backing.setBackGroundColor(cc.Color3B(*(72, 220, 230) if selected else (40, 44, 60)))
            outline.setBackGroundColor(cc.Color3B(*(72, 220, 230) if selected else (120, 130, 150)))
            button._f7_check.setVisible(selected)
            button._f7_label.setColor(cc.Color3B(63, 68, 87))
        except Exception:
            pass
        return
    if backing is not None:
        primary = primary or bool(getattr(button, '_f7_primary', False))
        if primary:
            color, title = (24, 24, 30), (255, 255, 255)
        elif selected:
            color, title = (38, 72, 88), (245, 253, 255)
        else:
            color, title = (226, 224, 232), (63, 68, 87)
        try:
            backing.setBackGroundColor(cc.Color3B(*color))
            backing.setBackGroundColorOpacity(255)
            backing.setBackGroundColorType(1)
        except Exception:
            pass
        label = getattr(button, '_f7_label', None)
        if label is not None:
            try:
                label.setColor(cc.Color3B(*title))
            except Exception:
                pass
        else:
            try:
                button.setTitleColor(cc.Color3B(*title))
            except Exception:
                pass
    elif getattr(button, '_f7_text', None) is not None:
        _native_label(button, button._f7_text,
                      cc.Color3B(*(88, 230, 240) if selected else (63, 68, 87)))


def _set_button_text(button, text):
    if button is None:
        return
    button._f7_text = text
    if getattr(button, '_f7_kind', None) == 'native_button':
        _native_title(button, text)
        return
    label = getattr(button, '_f7_label', None)
    if label is not None:
        try:
            label.setString(text)
            return
        except Exception:
            pass
    if getattr(button, '_f7_backing', None) is None:
        _native_label(button, text)
        return
    try:
        button.setTitleText(text)
    except Exception:
        pass


def _button_visible(button, visible):
    if button is None:
        return
    for name in ('_f7_backing', '_f7_outline', '_f7_check', '_f7_label'):
        node = getattr(button, name, None)
        if node is not None:
            try:
                node.setVisible(visible)
            except Exception:
                pass
    try:
        button.setVisible(visible)
    except Exception:
        pass


def _row_key(row):
    if row is None:
        return None
    if row.get('k') == 'currency':
        return ('currency', row.get('c'))
    return (row.get('k'), row.get('i'))


def _short(text, limit):
    text = u'%s' % (text or '')
    return text if len(text) <= limit else text[:limit - 3] + '...'


def _row_name(row):
    """Row label: the catalog display name, else the currency/id key.

    Currency rows carry both a display `name` (e.g. `Coins`) and a machine `c`
    key; the machine key must never reach the list.
    """
    return u'%s' % (row.get('name') or row.get('c') or '')


def _row_meta(row):
    return u'\u8d27\u5e01' if row.get('k') == 'currency' else u'\u7f16\u53f7 %s' % row.get('i')


def _update_pending_button():
    button = _VIEW.get('pending_button')
    if button is None:
        return
    identity = _identity()
    state, pending = _pending_state(identity) if identity else ('missing', None)
    _button_visible(button, pending is not None or state == 'corrupt')


def _bulk_status(text):
    _safe(_VIEW.get('bulk_status'), 'setString', text)


def _cg_ids():
    """Every CG id the client table knows, bounded for the request."""
    try:
        table = __import__('com.data.cdata.cg_data', fromlist=['data']).data
    except Exception:
        return []
    try:
        values = sorted(set(int(key) for key in table if int(key) > 0))
    except Exception:
        return []
    return values[:1024]


def _bulk_run(kind):
    """One-tap grants ride the existing edit RPC as bulk/cg rows.

    CG ids are sent in MAX_BATCH-sized chunks: a 465-row batch never came back
    from the reliable channel, while a single-row bulk op did.
    """
    if not _VIEW.get('active'):
        return
    _VIEW['bulk_total'] = 0
    _VIEW['bulk_done'] = 0
    if kind == 'cg':
        ids = _cg_ids()
        if not ids:
            _bulk_status(u'\u672a\u627e\u5230 CG \u8868')
            return
        _VIEW['bulk_queue'] = [{'k': 'cg', 'i': value, 'm': 'add'} for value in ids]
        _VIEW['bulk_total'] = len(ids)
    else:
        _VIEW['bulk_queue'] = [{'k': 'bulk', 'm': kind}]
        _VIEW['bulk_total'] = 1
    _bulk_pump()


def _bulk_pump():
    queue = _VIEW.get('bulk_queue') or []
    if not queue:
        _bulk_status(u'\u5df2\u5b8c\u6210\uff0c\u80cc\u5305\u5df2\u66f4\u65b0')
        return
    rows = queue[:64]
    del queue[:64]
    _VIEW['bulk_queue'] = queue
    done = int(_VIEW.get('bulk_done') or 0) + len(rows)
    _VIEW['bulk_done'] = done
    _bulk_status(u'\u6b63\u5728\u6267\u884c %d/%d\u2026' % (done, _VIEW.get('bulk_total') or done))
    _send(rows)
    if not _VIEW.get('busy'):
        _VIEW['bulk_queue'] = []
        _bulk_status(u'\u672a\u63d0\u4ea4\uff1a\u8bf7\u5148\u6838\u5bf9\u4e0a\u6b21\u64cd\u4f5c')
        return


def _update_pager():
    """Show the current slice and dim the page buttons that cannot move."""
    page = int(_VIEW.get('catalog_page') or 0)
    more = bool(_VIEW.get('catalog_more'))
    label = _VIEW.get('list_page')
    if label is not None:
        try:
            label.setString(u'\u7b2c %d \u9875' % (page + 1))
        except Exception:
            pass
    for node, enabled in ((_VIEW.get('list_prev'), page > 0),
                          (_VIEW.get('list_next'), more)):
        if node is None:
            continue
        try:
            node.setBright(enabled)
        except Exception:
            pass


def _catalog_page_step(delta):
    page = int(_VIEW.get('catalog_page') or 0) + int(delta)
    if page < 0:
        return
    if delta > 0 and not _VIEW.get('catalog_more'):
        return
    _VIEW['catalog_page'] = page
    _request_catalog(preserve=True)


def _request_catalog(preserve=False):
    import gg
    search = _VIEW.get('search')
    query = search.getString() if search is not None else ''
    group = _VIEW.get('group', 'item')
    if group not in ('item', 'currency', 'treasure'):
        # The quick-action page has no catalog of its own; refresh the item
        # list after a one-tap grant instead of asking for an invalid group.
        group = 'item'
    _VIEW['catalog_generation'] = int(_VIEW.get('catalog_generation', 0)) + 1
    _VIEW['catalog_loading'] = True
    _VIEW['catalog_group'] = group
    _VIEW['catalog_query'] = query
    nonce = _new_op()
    _VIEW['catalog_nonce'] = nonce
    if not preserve:
        _VIEW['selected'] = None
        _VIEW['selected_key'] = None
        _VIEW['catalog_page'] = 0
        _VIEW['catalog_more'] = False
    page = int(_VIEW.get('catalog_page') or 0)
    _VIEW['rows'] = []
    _render_rows()
    _refresh_detail()
    _update_pager()
    _status(u'\u6b63\u5728\u67e5\u8be2')
    try:
        gg.avatar.callServerMethodReliable('q7InventoryCatalogAsk',
            {'g': group, 'q': query, 'n': _CATALOG_PAGE,
             'o': page * _CATALOG_PAGE, 'op': nonce})
    except Exception:
        _VIEW['catalog_loading'] = False
        _status(u'\u76ee\u5f55\u8bf7\u6c42\u5931\u8d25\uff0c\u8bf7\u91cd\u8bd5')



def _pending_bulk(pending):
    """True when the pending op is one of the idempotent one-tap grants."""
    try:
        batch = pending.get('batch') or []
    except Exception:
        return False
    if not batch:
        return False
    for row in batch:
        if not isinstance(row, dict) or row.get('k') not in ('bulk', 'cg'):
            return False
    return True


def _send(batch):
    import gg
    if _VIEW.get('busy'):
        return
    identity = _identity()
    state, pending = _pending_state(identity)
    if state == 'corrupt':
        _status(u'\u4e0a\u6b21\u64cd\u4f5c\u72b6\u6001\u4e0d\u660e\uff0c\u8bf7\u5148\u6838\u5bf9')
        return
    if pending is not None:
        # A one-tap grant that lost its reply is safe to drop: the next grant
        # re-applies only what is still missing. Ordinary edits still block.
        if not _pending_bulk(pending):
            _status(u'\u5b58\u5728\u672a\u5b8c\u6210\u64cd\u4f5c\uff0c\u8bf7\u5148\u6838\u5bf9\u4e0a\u6b21\u64cd\u4f5c')
            return
        _clear_pending(identity)
    if not identity:
        _status(u'\u5f53\u524d\u8d26\u53f7\u8eab\u4efd\u4e0d\u53ef\u7528')
        return
    op = _new_op()
    if not _save_pending(op, batch, identity):
        _status(u'\u65e0\u6cd5\u4fdd\u5b58\u672a\u5b8c\u6210\u64cd\u4f5c')
        return
    _VIEW['busy'] = True
    try:
        gg.ui.lock(_LOCK)
        gg.avatar.callServerMethodReliable('q7InventoryEditAsk', {'op': op, 'batch': batch})
        _status(u'\u6b63\u5728\u63d0\u4ea4')
    except Exception:
        _status(u'\u63d0\u4ea4\u5931\u8d25\uff0c\u8bf7\u6838\u5bf9\u4e0a\u6b21\u64cd\u4f5c')
        _unlock()
    _update_pending_button()


def _apply(mode):
    row = _VIEW.get('selected')
    if _VIEW.get('catalog_loading') or not row:
        _status(u'\u8bf7\u5148\u9009\u62e9\u4e00\u9879')
        return
    token = (_VIEW.get('ui_epoch'), _VIEW.get('catalog_generation'))
    canonical = None
    for candidate in _VIEW.get('rows', []):
        if _row_key(candidate) == _row_key(row):
            canonical = candidate
            break
    if (canonical is None or canonical.get('k') != _VIEW.get('group') or
            _VIEW.get('selected_token') != token):
        _status(u'\u76ee\u5f55\u5df2\u53d8\u5316\uff0c\u8bf7\u91cd\u65b0\u9009\u62e9')
        return
    row = canonical
    try:
        value = int(_VIEW.get('count').getString())
    except Exception:
        _status(u'\u6570\u91cf\u5fc5\u987b\u662f\u6574\u6570')
        return
    if value < 0 or value > 1000000:
        _status(u'\u6570\u91cf\u8d85\u51fa\u8303\u56f4')
        return
    kind = row.get('k')
    if kind == 'currency':
        batch = [{'k': 'currency', 'c': row.get('c'), 'm': mode, 'n': value}]
    elif kind == 'treasure':
        batch = [{'k': 'treasure', 'i': int(row.get('i')), 'm': 'create',
                  'n': value, 'q': int(_VIEW.get('quality_value', 1))}]
    else:
        batch = [{'k': 'item', 'i': int(row.get('i')), 'm': mode, 'n': value}]
    _send(batch)


def _retry_pending():
    identity = _identity()
    state, pending = _pending_state(identity)
    if state == 'corrupt':
        _status(u'\u4e0a\u6b21\u64cd\u4f5c\u72b6\u6001\u4e0d\u660e\uff0c\u8bf7\u5148\u6838\u5bf9')
        return
    if not pending:
        _status(u'\u6ca1\u6709\u9700\u8981\u6838\u5bf9\u7684\u64cd\u4f5c')
        return
    if pending.get('session') != identity:
        _status(u'\u6ca1\u6709\u9700\u8981\u6838\u5bf9\u7684\u64cd\u4f5c')
        return
    import gg
    _VIEW['busy'] = True
    try:
        gg.ui.lock(_LOCK)
        gg.avatar.callServerMethodReliable('q7InventoryEditAsk',
            {'op': pending['op'], 'batch': pending['batch']})
        _status(u'\u6b63\u5728\u6838\u5bf9\u4e0a\u6b21\u64cd\u4f5c')
    except Exception:
        _status(u'\u6838\u5bf9\u5931\u8d25\uff0c\u8bf7\u7a0d\u540e\u518d\u8bd5')
        _unlock()
    _update_pending_button()


def _item_image(row):
    """Image id chosen the way common_frame.item does (ITEM_DATA icon).

    Hero entities are not in ITEM_DATA; catalog rows never use kind 'hero'
    today, but when they do the hero frame family is selected in `_icon_path`.
    """
    if row is None or row.get('k') == 'currency':
        return None
    try:
        import com.const as const
        import com.data.cdata.item_data as ITEM_DATA
        item_id = int(row.get('i'))
        data = ITEM_DATA.data.get(item_id, {})
        image = data.get('icon')
        if (data.get('type') == const.ItemType.VIRTUAL and
                data.get('virtual_sub_type') == const.VirtualItemSub.MEMORY_FRAG):
            memory = data.get('memoryFrag')
            if memory and memory[0]:
                image = str(100000 + memory[0])
        if image in (None, ''):
            # Hero rows carry the hero id directly (common_frame.item IMG_PATH hero).
            if row.get('k') == 'hero':
                return str(item_id)
            return None
        return image
    except Exception:
        return None


# common_frame/item.py:10 IMG_PATH; treasure_frame.py:47 keeps item/common for
# treasure art too, so only hero entities use the hero frame family.
_IMG_PATH = {'hero': 'cocos/image/hero/common_frame/'}
_ITEM_IMG = 'cocos/image/item/common/'


def _icon_path(row):
    image = _item_image(row)
    if image in (None, ''):
        return None
    base = _IMG_PATH.get(row.get('k') if row else None, _ITEM_IMG)
    return '%s%s.png' % (base, image)


def _detail_icon(row):
    icon = _VIEW.get('detail_icon')
    if icon is None:
        return
    if row is None or row.get('k') == 'currency':
        icon.setVisible(False)
        _VIEW['detail_icon_key'] = None
        return
    try:
        import cocosui as cc
        item_id = int(row.get('i'))
        path = _icon_path(row)
        if path is None:
            icon.setVisible(False)
            _VIEW['detail_icon_key'] = None
            return
        key = (row.get('k'), item_id, path)
        if _VIEW.get('detail_icon_key') == key:
            icon.setVisible(True)
            return
        # Native loadTexture may silently fail; a fresh view cannot retain the previous item.
        parent = icon.getParent()
        position = icon.getPosition()
        fresh = cc.ccui.ImageView.create()
        fresh.ignoreContentAdaptWithSize(False)
        size = _VIEW.get('detail_icon_size') or _DETAIL_ICON
        fresh.setContentSize(cc.cc.Size(size, size))
        fresh.setAnchorPoint(cc.cc.Vec2(0.5, 0.5))
        fresh.setPosition(cc.cc.Vec2(position.x, position.y))
        fresh.loadTexture(path)
        parent.addChild(fresh, 3)
        icon.removeFromParent()
        _VIEW['detail_icon'] = fresh
        _VIEW['detail_icon_key'] = key
        fresh.setVisible(True)
    except Exception:
        icon.setVisible(False)
        _VIEW['detail_icon_key'] = None


def _reflow_register(node):
    """Remember a quantity-group node and its authored y for the compact stack."""
    if node is None:
        return
    try:
        _VIEW.setdefault('reflow', []).append((node, node.getPosition().y))
    except Exception:
        pass


def _reflow_detail(compact):
    """Move the quantity group between the full and the no-quality stack.

    Row types without a quality band would otherwise leave that band's height
    as dead space between the mode chips and the quantity row. Only this
    group moves, so the CTA and the action row stay anchored to the panel
    bottom.
    """
    full = _VIEW.get('geometry')
    tight = _VIEW.get('geometry_compact')
    if not full or not tight:
        return
    try:
        import cocosui as cc
    except Exception:
        return
    shift = float(full['quantity_label']['y'] - tight['quantity_label']['y']) \
        if compact else 0.0
    for node, authored in _VIEW.get('reflow') or []:
        try:
            node.setPosition(cc.cc.Vec2(node.getPosition().x, authored - shift))
        except Exception:
            pass
    for name in ('quantity_label', 'minus', 'count', 'plus', 'status'):
        entry = (_VIEW.get('geo_widgets') or {}).get(name)
        if entry is None:
            continue
        rect = entry.get('rect')
        if not rect:
            continue
        delta = -shift if compact else 0.0
        rect['y'] = entry.setdefault('_authored_y', rect['y']) + delta


def _refresh_detail():
    row = _VIEW.get('selected')
    name = _VIEW.get('detail_name')
    held = _VIEW.get('held')
    if name is not None:
        name.setString(_short(row.get('name') or row.get('c') or '', 12) if row else u'\u672a\u9009\u62e9\u6761\u76ee')
    if held is not None:
        held.setString(u'%s' % (row.get('n') if row else 0))
    _detail_icon(row)
    treasure = row is not None and row.get('k') == 'treasure'
    for group, button in _VIEW.get('mode_buttons', {}).items():
        _button_visible(button, not treasure)
        _style(button, selected=_VIEW.get('mode') == group)
    quality_label = _VIEW.get('quality_label')
    if quality_label is not None:
        try:
            quality_label.setVisible(treasure)
        except Exception:
            pass
    for value, button in _VIEW.get('quality_buttons', {}).items():
        _button_visible(button, treasure)
        _style(button, selected=int(_VIEW.get('quality_value', 1)) == value)
        label = getattr(button, '_f7_label', None)
        if label is not None:
            try:
                label.setColor(__import__('cocosui').cc.Color3B(*_QUALITY_COLORS[value]))
            except Exception:
                pass
        else:
            try:
                button.setTitleColor(__import__('cocosui').cc.Color3B(*_QUALITY_COLORS[value]))
            except Exception:
                pass
    _reflow_detail(not treasure)
    cta = _VIEW.get('cta')
    if cta is not None:
        if treasure:
            title = u'\u751f\u6210\u5f71\u88c5'
        elif _VIEW.get('mode') == 'add':
            title = u'\u589e\u52a0\u6570\u91cf'
        else:
            title = u'\u4fdd\u5b58\u6570\u91cf'
        _set_button_text(cta, title)


def _set_mode(mode):
    if _VIEW.get('mode') == mode:
        _refresh_detail()
        return
    _VIEW['mode'] = mode
    row = _VIEW.get('selected')
    field = _VIEW.get('count')
    if row is not None and field is not None:
        try:
            field.setString(str(row.get('n', 0)) if mode == 'set' else '1')
        except Exception:
            pass
    _refresh_detail()


def _select_row(row, generation=None):
    token = (_VIEW.get('ui_epoch'), _VIEW.get('catalog_generation'))
    if (_VIEW.get('catalog_loading') or
            (generation is not None and generation != token)):
        return
    canonical = None
    for candidate in _VIEW.get('rows', []):
        if _row_key(candidate) == _row_key(row):
            canonical = candidate
            break
    if canonical is None or canonical.get('k') != _VIEW.get('group'):
        return
    old_key = _VIEW.get('selected_key')
    new_key = _row_key(canonical)
    _VIEW['selected'] = canonical
    _VIEW['selected_key'] = new_key
    _VIEW['selected_token'] = token
    if old_key != new_key:
        field = _VIEW.get('count')
        if field is not None:
            if canonical.get('k') == 'treasure' or _VIEW.get('mode') == 'add':
                field.setString('1')
            else:
                field.setString(str(canonical.get('n', 0)))
    changed = set()
    if old_key is not None:
        changed.add(old_key)
    changed.add(new_key)
    _repaint_rows(changed)
    _refresh_detail()


def _shield(cc, parent, rect, callback, events=None, anchor=(0.5, 0.5)):
    """Invisible full-rect touch target above a native widget.

    Native csb buttons and text fields hit-test against their authored art, so
    taps at the rect centre were dropped on device. A dedicated layer keeps the
    whole rect tappable regardless of the art.
    """
    x, y = _anchor_xy(rect, anchor)
    node = _fill(cc, parent, x, y, rect['w'], rect['h'], (0, 0, 0), 0, anchor)
    node.setName('touch')
    # _fill adds at the default z; the native widgets it has to cover sit at 4..6.
    _safe(node, 'setLocalZOrder', 9)
    _safe(node, 'setZOrder', 9)
    node.setTouchEnabled(True)
    node.addTouchEventListener(
        lambda sender, event: _button_event(cc, events, callback, event))
    return node


def _click(node, callback, cc):
    node.setTouchEnabled(True)
    node.addTouchEventListener(
        lambda sender, event: callback() if event == cc.ccui.TOUCH_EVENT_ENDED else None)


def _row_clicked(node, event, cc):
    if event != cc.ccui.TOUCH_EVENT_ENDED:
        return
    row = getattr(node, '_f7_row', None)
    if row is not None:
        _select_row(row, getattr(node, '_f7_token', None))


def _clamp_item_cell(cc, cell, width):
    """Force the cloned common_frame.item node to (list_w, 88).

    The csb cell keeps its authored grid size after cloning; without this the
    backing stays 590 units wide inside a 732-unit list and the count label
    lands outside it. Every child width derives from the forced cell width.
    """
    if cell is None:
        return
    width = float(width)
    _safe(cell, 'setContentSize', cc.cc.Size(width, _ROW_H))
    _safe(cell, 'setAnchorPoint', cc.cc.Vec2(0, 0))
    row_bg = getattr(cell, '_f7_rowbg', None)
    if row_bg is not None and row_bg is not cell:
        _safe(row_bg, 'setAnchorPoint', cc.cc.Vec2(0, 0))
        _safe(row_bg, 'setPosition', cc.cc.Vec2(0, 0))
        _safe(row_bg, 'setContentSize', cc.cc.Size(width, _ROW_H))
    info_w = max(1.0, width - (_PAD * 2 + _ICON + 8))
    native = bool(getattr(cell, '_f7_native', False))
    info = getattr(cell, '_f7_info', None)
    if info is not None:
        _safe(info, 'setAnchorPoint', cc.cc.Vec2(0, 0))
        _safe(info, 'setPosition', cc.cc.Vec2(_PAD + _ICON + 8, 0))
        _safe(info, 'setContentSize', cc.cc.Size(info_w, _ROW_H))
    inner = getattr(cell, '_f7_name_label', None)
    if inner is not None:
        _safe(inner, 'setAnchorPoint', cc.cc.Vec2(0, 0.5))
        _safe(inner, 'setPosition', cc.cc.Vec2(0 if native else _PAD, 58))
    outter = getattr(cell, '_f7_count_label', None)
    if outter is not None:
        _safe(outter, 'setAnchorPoint', cc.cc.Vec2(1, 0.5))
        _safe(outter, 'setPosition',
              cc.cc.Vec2(info_w - 8 if native else width - _PAD, 56))
    meta = getattr(cell, '_f7_meta_label', None)
    if meta is not None:
        _safe(meta, 'setAnchorPoint', cc.cc.Vec2(0, 0.5))
        _safe(meta, 'setPosition', cc.cc.Vec2(0 if native else _PAD, 24))
    cell._f7_width = width


def _make_item_row(cc, parent, width):
    """One list row on the native common_frame.item cell, sized to the list.

    The cell is the row root; its native `img` is the icon, its `info` strip
    holds the name/count labels and a meta line, and the 9-slice `sel` art
    marks the selection. Everything else in the csb (rarity frames, stars,
    lock/trade/level decorations) is hidden because this is a list row, not a
    grid cell.
    """
    comp = _load_comp('common_frame', 'item')
    cell = getattr(comp, '_node', None) if comp is not None else None
    if cell is not None:
        try:
            cell.setVisible(True)
            cell.setContentSize(cc.cc.Size(width, _ROW_H))
            cell.setAnchorPoint(cc.cc.Vec2(0, 0))
            for child in cell.getChildren():
                if child.getName() not in ('img', 'info', 'sel'):
                    _safe(child, 'setVisible', False)
            row_bg = _fill(cc, cell, 0, 0, width, _ROW_H,
                           _LIST_BG, 255, (0, 0))
            img = _comp_get(comp, 'img')
            icon_x = _PAD + _ICON / 2.0
            if img is not None:
                for method, args in (('setVisible', (True,)),
                                     ('setAnchorPoint', (cc.cc.Vec2(0.5, 0.5),)),
                                     ('setContentSize', (cc.cc.Size(_ICON, _ICON),)),
                                     ('setPosition', (cc.cc.Vec2(icon_x, _ROW_H / 2.0),))):
                    _safe(img, method, *args)
            sel = _comp_get(comp, 'sel')
            if sel is not None:
                _safe(sel, 'setAnchorPoint', cc.cc.Vec2(0.5, 0.5))
                _safe(sel, 'setContentSize', cc.cc.Size(_ICON + 16, _ICON + 16))
                _safe(sel, 'setPosition', cc.cc.Vec2(icon_x, _ROW_H / 2.0))
                _safe(sel, 'setVisible', False)
            info = _comp_get(comp, 'info')
            info_w = max(1.0, width - (_PAD * 2 + _ICON + 8))
            if info is not None:
                _safe(info, 'setVisible', True)
                _safe(info, 'setAnchorPoint', cc.cc.Vec2(0, 0))
                _safe(info, 'setPosition', cc.cc.Vec2(_PAD + _ICON + 8, 0))
                _safe(info, 'setContentSize', cc.cc.Size(info_w, _ROW_H))
                for child in info.getChildren():
                    if child.getName() not in ('inner', 'outter'):
                        _safe(child, 'setVisible', False)
            inner = _comp_get(comp, 'info.inner')
            outter = _comp_get(comp, 'info.outter')
            for label, y in ((inner, 58), (outter, 56)):
                if label is None:
                    continue
                _safe(label, 'setVisible', True)
                _safe(label, 'setFontSize', _FONT_BODY)
                _safe(label, 'setAnchorPoint', cc.cc.Vec2(0 if label is inner else 1, 0.5))
                _safe(label, 'setPosition',
                      cc.cc.Vec2(0 if label is inner else info_w - 8, y))
                _safe(label, 'setColor', cc.cc.Color3B(*_INK))
            meta = _text(cc, info if info is not None else cell, u'',
                         0, 24, _FONT_META, _INK_META, (0, 0.5))
            cell._f7_comp = comp
            cell._f7_native = True
            cell._f7_rowbg = row_bg
            cell._f7_info = info
            cell._f7_name_label = inner
            cell._f7_meta_label = meta
            cell._f7_count_label = outter
            _VIEW['native_skin'] = True
            _clamp_item_cell(cc, cell, width)
        except Exception:
            comp = None
            cell = None
    if cell is None:
        cell = _fill(cc, parent, 0, 0, width, _ROW_H,
                     _LIST_BG, 255, (0, 0))
        cell._f7_comp = None
        cell._f7_native = False
        cell._f7_rowbg = cell
        cell._f7_info = None
        cell._f7_name_label = _text(
            cc, cell, u'', _PAD, _ROW_H * 0.66, _FONT_BODY, _INK, (0, 0.5))
        cell._f7_meta_label = _text(
            cc, cell, u'', _PAD, _ROW_H * 0.30, _FONT_META, _INK_META, (0, 0.5))
        cell._f7_count_label = _text(
            cc, cell, u'', width - _PAD, _ROW_H * 0.55,
            _FONT_BODY, _INK, (1, 0.5))
        _clamp_item_cell(cc, cell, width)
    cell.setTouchEnabled(True)
    cell.addTouchEventListener(
        lambda sender, event, node=cell: _row_clicked(node, event, cc))
    if cell.getParent() is not None:
        cell.removeFromParent()
    return cell


def _paint_item_row(cc, node, row, width, chosen, token):
    node._f7_row = row
    node._f7_token = token
    node._f7_selected = chosen
    row_bg = getattr(node, '_f7_rowbg', None)
    if row_bg is not None:
        _safe(row_bg, 'setBackGroundColorType', 1)
        _safe(row_bg, 'setBackGroundColor',
              cc.cc.Color3B(*(214, 244, 247) if chosen else _LIST_BG))
        _safe(row_bg, 'setBackGroundColorOpacity', 255)
    comp = getattr(node, '_f7_comp', None)
    image = _icon_path(row)
    if comp is not None:
        try:
            img = _comp_get(comp, 'img')
            if img is not None:
                if image is not None:
                    if getattr(node, '_f7_icon', None) != image:
                        img.loadTexture(image)
                        node._f7_icon = image
                    _safe(img, 'setContentSize', cc.cc.Size(_ICON, _ICON))
                    _safe(img, 'setVisible', True)
                else:
                    node._f7_icon = None
                    _safe(img, 'setVisible', False)
            sel = _comp_get(comp, 'sel')
            if sel is not None:
                _safe(sel, 'setVisible', chosen)
        except Exception:
            pass
    limit = max(4, int(max(1.0, float(width) - (_PAD * 2 + _ICON + 8)) / float(_FONT_BODY)))
    _safe(node._f7_name_label, 'setString', _short(_row_name(row), limit))
    _safe(node._f7_meta_label, 'setString', _row_meta(row))
    _safe(node._f7_count_label, 'setString', u'%s' % row.get('n', 0))
    _clamp_item_cell(cc, node, width)
    return node


def _row_live(node):
    """False once the engine released a row node (stale python wrapper)."""
    try:
        node.getContentSize()
        return True
    except Exception:
        return False


def _repaint_rows(keys):
    """Repaint only the rows whose highlight changed.

    Selection used to rebuild the whole list, which re-placed every pooled node
    on each tap. A single stale node aborted that loop and left one highlighted
    row behind an empty list; repainting in place keeps every other row intact.
    """
    if not keys:
        return
    import cocosui as cc
    width = _VIEW.get('row_width')
    if not width:
        return
    token = (_VIEW.get('ui_epoch'), _VIEW.get('catalog_generation'))
    selected_key = _VIEW.get('selected_key')
    for node in _VIEW.get('row_pool') or []:
        row = getattr(node, '_f7_row', None)
        if row is None or _row_key(row) not in keys:
            continue
        if not _row_live(node):
            continue
        _paint_item_row(cc, node, row, width, _row_key(row) == selected_key,
                        token)


def _render_rows():
    import cocosui as cc
    scroll = _VIEW.get('scroll')
    if scroll is None:
        return
    metrics = _VIEW.get('metrics') or {}
    group = _VIEW.get('group')
    rows = [row for row in (_VIEW.get('rows') or [])
            if group is None or row.get('k') == group]
    geo = _editor_geometry(metrics.get('w', 1334), metrics.get('h', 750),
                           _VIEW.get('gap', 0.0), row_count=len(rows))
    width = geo['scroll']['w']
    _VIEW['row_width'] = width
    if _VIEW.get('geometry') is None:
        _VIEW['geometry'] = geo
    _VIEW['geometry']['rows'] = geo['rows']
    _VIEW['geometry']['scroll_container_h'] = geo['scroll_container_h']
    scroll.setInnerContainerSize(cc.cc.Size(width, geo['scroll_container_h']))
    pool = _VIEW.get('row_pool')
    if pool is None:
        pool = []
        _VIEW['row_pool'] = pool
    # Rows are created once and reused: removeFromParent() releases the C++
    # node, so re-adding the wrapper later raised "self == NULL in
    # ...Node_setAnchorPoint" and blanked the list. Slots whose node the engine
    # already released are rebuilt instead of placed.
    while len(pool) < len(rows):
        node = _make_item_row(cc, scroll, width)
        scroll.addChild(node, 3)
        pool.append(node)
    selected_key = _VIEW.get('selected_key')
    token = (_VIEW.get('ui_epoch'), _VIEW.get('catalog_generation'))
    for index, row in enumerate(rows):
        rect = geo['rows'][index]
        node = pool[index]
        if not _row_live(node):
            node = _make_item_row(cc, scroll, width)
            scroll.addChild(node, 3)
            pool[index] = node
        _safe(node, 'setVisible', True)
        _paint_item_row(cc, node, row, width,
                        _row_key(row) == selected_key, token)
        _place_rect(node, rect)
        _register_geom('row:%d' % index, node, rect)
    for node in pool[len(rows):]:
        _safe(node, 'setVisible', False)
    _safe(scroll, 'jumpToPercentVertical', 0)


def _dump_geometry():
    """Temporary device diagnostic: what each widget actually reports."""
    try:
        import cocosui as cc
        geo = _VIEW.get('geometry') or {}
        for name in ('nav', 'content', 'list', 'detail', 'pool'):
            rect = geo.get(name)
            if rect:
                print('P7GEO panel %s %.1f %.1f %.1f %.1f' % (
                    name, rect['x'], rect['y'], rect['w'], rect['h']))
        for name, entry in sorted((_VIEW.get('geo_widgets') or {}).items()):
            node = entry['node']
            rect = entry['rect']
            try:
                pos = node.position
                size = node.size
                anchor = node.anchor
            except Exception:
                continue
            print('P7GEO %s rect=%.1f,%.1f,%.1f,%.1f pos=%.1f,%.1f '
                  'size=%.1f,%.1f anchor=%.1f,%.1f parent=%s' % (
                      name, rect['x'], rect['y'], rect['w'], rect['h'],
                      pos.x, pos.y, size.width, size.height,
                      getattr(anchor, 'x', 0), getattr(anchor, 'y', 0),
                      _parent_name(node)))
        for group, label in sorted((_VIEW.get('tab_labels') or {}).items()):
            try:
                print('P7GEO tab %s pos=%.1f,%.1f size=%.1f,%.1f '
                      'anchor=%.1f,%.1f parentpos=%.1f,%.1f' % (
                          group, label.position.x, label.position.y,
                          label.size.width, label.size.height,
                          label.anchor.x, label.anchor.y,
                          label.getParent().position.x if label.getParent() else -1,
                          label.getParent().position.y if label.getParent() else -1))
            except Exception:
                pass
        for name in ('mode:set', 'mode:add', 'quality:1', 'quality:5',
                     'tab:item', 'tab:currency', 'tab:skin', 'tab:pool',
                     'tab:bulk', 'tabhit:bulk', 'bulk:letters_reset',
                     'list_header', 'pool_header', 'minus', 'plus', 'count',

                     'query', 'list_query', 'cta', 'list_prev', 'list_next', 'close'):
            entry = (_VIEW.get('geo_widgets') or {}).get(name)
            if entry is None:
                continue
            _dump_children(entry['node'], name)
            try:
                pos = entry['node'].getPosition()
                size = entry['node'].getContentSize()
                world = entry['node'].convertToWorldSpace(cc.cc.Vec2(0, 0))
                scale = entry['node'].getScale()
                print('P7GEO world %s %.1f,%.1f scale=%.3f' % (
                    name, world.x, world.y, scale))
                renderer = getattr(
                    entry['node'], 'getVirtualRenderer', lambda: None)()
                extra = ''
                if renderer is not None:
                    rsize = renderer.getContentSize()
                    rpos = renderer.getPosition()
                    extra = ' renderer=%.1f,%.1f@%.1f,%.1f' % (
                        rsize.width, rsize.height, rpos.x, rpos.y)
                scale9 = getattr(entry['node'], 'isScale9Enabled', lambda: '?')()
                texture = getattr(
                    entry['node'], 'getTextureFilenameNormal', lambda: '')()
                print('P7GEO node %s pos=%.1f,%.1f size=%.1f,%.1f%s scale9=%s tex=%s' % (
                    name, pos.x, pos.y, size.width, size.height, extra,
                    scale9, texture))
            except Exception as error:
                print('P7GEO node %s failed %s' % (name, error))
    except Exception as error:
        print('P7GEO dump failed %s' % (error,))


def _parent_name(node):
    try:
        parent = node.getParent()
        if parent is None:
            return 'none'
        return parent.getName() or 'unnamed'
    except Exception:
        return '?'


def _dump_children(node, prefix, depth=0):
    """Report a cloned csb node's children so their real footprint is visible."""
    if node is None or depth > 3:
        return
    try:
        children = node.getChildren() or []
    except Exception:
        return
    for child in children:
        try:
            pos = child.getPosition()
            size = child.getContentSize()
            anchor = child.getAnchorPoint()
            extra = ''
            renderer = getattr(child, 'getVirtualRenderer', lambda: None)()
            if renderer is not None:
                rsize = renderer.getContentSize()
                rpos = renderer.getPosition()
                extra = ' renderer=%.1f,%.1f@%.1f,%.1f' % (
                    rsize.width, rsize.height, rpos.x, rpos.y)
            print('P7GEO %s/%s%s pos=%.1f,%.1f size=%.1f,%.1f '
                  'anchor=%.1f,%.1f vis=%s%s' % (
                      prefix, '  ' * depth, child.getName() or '?',
                      pos.x, pos.y, size.width, size.height,
                      anchor.x, anchor.y, child.isVisible(), extra))
        except Exception:
            continue
        _dump_children(child, prefix, depth + 1)


def _close():
    _VIEW['active'] = False
    root = _VIEW.get('root')
    if root is not None:
        try:
            root.removeFromParent()
        except Exception:
            pass
    _VIEW['root'] = None
    _VIEW['card'] = None
    _VIEW['panel'] = None
    _VIEW['rows'] = []
    _VIEW['selected'] = None
    _VIEW['selected_key'] = None
    _VIEW['selected_token'] = None
    _VIEW['scroll'] = None
    _VIEW['search'] = None
    _VIEW['count'] = None
    _VIEW['status'] = None
    _VIEW['detail_name'] = None
    _VIEW['held'] = None
    _VIEW['cta'] = None
    _VIEW['mode_buttons'] = {}
    _VIEW['quality_buttons'] = {}
    _VIEW['pending_button'] = None
    _VIEW['quality_label'] = None
    _VIEW['detail_icon'] = None
    _VIEW['detail_icon_key'] = None
    _VIEW['detail_rects'] = []
    _VIEW['detail_icon_size'] = 0
    _VIEW['quantity_label'] = None
    _VIEW['catalog_generation'] = 0
    _VIEW['catalog_loading'] = False
    _VIEW['catalog_nonce'] = None
    _VIEW['selected_token'] = None
    _VIEW['group'] = 'item'
    _VIEW['catalog_query'] = ''
    _VIEW['catalog_page'] = 0
    _VIEW['catalog_more'] = False
    _VIEW['row_width'] = 0
    _VIEW['hold_active'] = False
    _VIEW['hold_swallow'] = False
    _VIEW['hold_next'] = 0
    _VIEW['bulk_queue'] = []
    _VIEW['bulk_total'] = 0
    _VIEW['bulk_done'] = 0
    _VIEW['list_prev'] = None
    _VIEW['list_next'] = None
    _VIEW['list_page'] = None

    _VIEW['minus'] = None
    _VIEW['plus'] = None
    _VIEW['body'] = None
    _VIEW['metrics'] = None
    _VIEW['csb'] = {}
    _VIEW['tab_comps'] = {}
    _VIEW['gap'] = 0
    _VIEW['header'] = None
    _VIEW['header_native'] = False
    _VIEW['title'] = None
    _VIEW['query'] = None
    _VIEW['row_pool'] = []
    _VIEW['native_skin'] = False
    _VIEW['inventory_content'] = None
    _VIEW['pool_content'] = None
    _VIEW['tab_labels'] = {}
    _VIEW['tab_fills'] = {}
    _VIEW['tab_strips'] = {}
    _VIEW['tab_pointers'] = {}
    _VIEW['list_header'] = None
    _VIEW['detail_header'] = None
    _VIEW['pool_all'] = []
    _VIEW['pool_page'] = 0
    _VIEW['pool_filtered'] = []
    _VIEW['pool_scroll'] = None
    _VIEW['pool_search'] = None
    _VIEW['pool_header'] = None
    _VIEW['pool_status'] = None
    _VIEW['pool_prev'] = None
    _VIEW['pool_next'] = None
    _VIEW['pool_page_label'] = None
    _VIEW['pool_list_width'] = 0
    _VIEW['geometry'] = None
    _VIEW['geo_widgets'] = {}
    _unlock()


def _pool_api():
    return _VIEW.get('pool_api')


def _pool_selected():
    api = _pool_api()
    try:
        return set(api.selection()) if api is not None else set()
    except Exception:
        return set()


def _pool_pending(draw_type):
    try:
        import gg
        data = getattr(getattr(gg, 'avatar', None), 'luckyDrawData', None)
        if data is None:
            return False
        return bool(data.getIsOpenCard(draw_type))
    except Exception:
        return False


def _pool_end(row):
    value = row.get('end_time') if row else None
    try:
        return tuple(int(part) for part in value[:6])
    except Exception:
        return ()


def _pool_date(value):
    try:
        return u'%04d-%02d-%02d' % (int(value[0]), int(value[1]), int(value[2]))
    except Exception:
        return u''


def _pool_name(draw_type, row):
    for key in ('room_title', 'name', 'title'):
        value = row.get(key) if row else None
        if value:
            return u'%s' % (value,)
    return u'\u5361\u6c60 %s' % (draw_type,)


def _pool_entries():
    api = _pool_api()
    hideable = None
    if api is not None:
        getter = getattr(api, 'hideable', None)
        if callable(getter):
            try:
                hideable = getter()
            except Exception:
                hideable = None
    if hideable is None:
        ready = getattr(api, 'ready', None) if api is not None else None
        hideable = ready
    try:
        hideable = list(hideable or ())
    except Exception:
        return []
    if not hideable:
        return []
    try:
        table = __import__('com.data.cdata.chouka_info', fromlist=['data']).data
    except Exception:
        table = {}
    if not isinstance(table, dict):
        table = {}
    ready = getattr(api, 'ready', ()) if api is not None else ()
    try:
        ready = set(ready or ())
    except Exception:
        ready = set()
    rows = []
    for value in hideable:
        try:
            draw_type = int(value)
        except Exception:
            continue
        row = table.get(draw_type)
        if ready and draw_type not in ready:
            # Stock rows outside the verified catalog cannot be opened, but the
            # player still controls whether they are listed at all.
            row = dict(row) if isinstance(row, dict) else {}
            row['_f7_stock_only'] = True
        rows.append((_pool_end(row), draw_type, row))
    rows.sort(key=lambda item: (item[0], item[1]), reverse=True)
    return rows


def _pool_matches(entry, query):
    if not query:
        return True
    end, draw_type, row = entry
    return query in _pool_name(draw_type, row).lower() or query in u'%s' % (draw_type,)


def _pool_status(text):
    label = _VIEW.get('pool_status')
    if label is not None:
        try:
            label.setString(text)
        except Exception:
            pass


def _pool_refresh_header():
    label = _VIEW.get('pool_header')
    if label is None:
        return
    try:
        label.setString(u'\u5361\u6c60\u5f00\u5173  \u5df2\u5f00\u542f %d/%d'
                        % (len(_pool_selected()), _POOL_CAP))
    except Exception:
        pass


def _pool_query():
    field = _VIEW.get('pool_search')
    try:
        return (field.getString() or '').strip().lower() if field is not None else ''
    except Exception:
        return ''


def _pool_chip(cc, parent, draw_type, x, y, size, pending, selected):
    active = bool(pending) or bool(selected)
    node = _native_check(cc, parent, x, y, size + 8,
                         (lambda: _pool_toggle(draw_type)) if not pending else (lambda: None),
                         active)
    if node is not None:
        parent.addChild(node, 6)
        if pending:
            _safe(node, 'setTouchEnabled', False)
        node.setName('pool_switch_iphonex_right')
        return node
    _fill(cc, parent, x, y, size + 4, size + 4,
          (72, 220, 230) if active else (120, 130, 150), 255, (0.5, 0.5))
    inner = _fill(cc, parent, x, y, size, size,
                  (72, 220, 230) if active else (40, 44, 60), 255, (0.5, 0.5))
    check = _text(cc, parent, u'x', x, y, _FONT_BODY, (30, 38, 46), (0.5, 0.5))
    check.setVisible(active)
    if pending:
        return inner
    _click(inner, lambda: _pool_toggle(draw_type), cc)
    return inner


def _pool_after_change():
    query = _pool_query()
    _VIEW['pool_filtered'] = [entry for entry in (_VIEW.get('pool_all') or [])
                              if _pool_matches(entry, query)]
    _pool_refresh_header()
    _render_pool_rows()
    _pool_status(u'\u4fee\u6539\u540e\u91cd\u65b0\u8fdb\u5165\u767d\u591c\u9986\u751f\u6548')


def _pool_toggle(draw_type):
    api = _pool_api()
    if api is None:
        _pool_status(u'\u5361\u6c60\u5f00\u5173\u4e0d\u53ef\u7528')
        return
    if _pool_pending(draw_type):
        _pool_status(u'\u8fdb\u884c\u4e2d\u7684\u5361\u6c60\u4e0d\u80fd\u5173\u95ed')
        return
    selected = _pool_selected()
    if draw_type in selected:
        values = sorted(selected - set((draw_type,)))
    else:
        if len(selected) >= _POOL_CAP:
            _pool_status(u'\u6700\u591a\u540c\u65f6\u5f00\u542f %d \u4e2a\u5361\u6c60' % _POOL_CAP)
            return
        values = sorted(selected | set((draw_type,)))
    try:
        saved = api.set_selection(values)
    except Exception:
        saved = False
    if not saved:
        _pool_status(u'\u5361\u6c60\u8bbe\u7f6e\u4fdd\u5b58\u5931\u8d25')
        return
    _pool_after_change()


def _pool_close_all():
    api = _pool_api()
    if api is None:
        _pool_status(u'\u5361\u6c60\u5f00\u5173\u4e0d\u53ef\u7528')
        return
    selected = _pool_selected()
    values = sorted(t for t in selected if _pool_pending(t))
    if values == sorted(selected):
        _pool_status(u'\u6ca1\u6709\u53ef\u5173\u95ed\u7684\u5361\u6c60')
        return
    try:
        saved = api.set_selection(values)
    except Exception:
        saved = False
    if not saved:
        _pool_status(u'\u5361\u6c60\u8bbe\u7f6e\u4fdd\u5b58\u5931\u8d25')
        return
    _pool_after_change()


def _pool_apply_search():
    query = _pool_query()
    _VIEW['pool_page'] = 0
    _VIEW['pool_filtered'] = [entry for entry in (_VIEW.get('pool_all') or [])
                              if _pool_matches(entry, query)]
    _render_pool_rows()


def _pool_page_step(delta):
    _VIEW['pool_page'] = int(_VIEW.get('pool_page') or 0) + delta
    _render_pool_rows()


def _pool_row(cc, parent, width, draw_type, row, end, pending, chosen):
    backing = _fill(cc, parent, 0, 0, width, _ROW_H,
                    (214, 244, 247) if chosen else _LIST_BG,
                    255, (0, 0))
    backing._f7_native = False
    backing._f7_comp = None
    _text(cc, backing, _short(_pool_name(draw_type, row), 20),
          _PAD, _ROW_H * 0.66, _FONT_BODY, _INK, (0, 0.5))
    dates = u'%s ~ %s' % (_pool_date(row.get('begin_time') if row else None),
                          _pool_date(end))
    _text(cc, backing, dates, _PAD, _ROW_H * 0.30, _FONT_META,
          _INK_META, (0, 0.5))
    if pending:
        _text(cc, backing, u'\u8fdb\u884c\u4e2d', width - 160,
              _ROW_H * 0.5, _FONT_META, (222, 48, 64), (1, 0.5))
    _pool_chip(cc, backing, draw_type, width - 44, _ROW_H * 0.5,
               36, pending, chosen)
    backing._f7_selected = chosen
    return backing


def _render_pool_rows():
    import cocosui as cc
    scroll = _VIEW.get('pool_scroll')
    if scroll is None:
        return
    metrics = _VIEW.get('metrics') or {}
    entries = _VIEW.get('pool_filtered') or []
    pages = max(1, (len(entries) + _POOL_PAGE - 1) // _POOL_PAGE)
    page = int(_VIEW.get('pool_page') or 0)
    if page < 0:
        page = 0
    if page >= pages:
        page = pages - 1
    _VIEW['pool_page'] = page
    chunk = entries[page * _POOL_PAGE:(page + 1) * _POOL_PAGE]
    scroll.removeAllChildren()
    geo = _editor_geometry(metrics.get('w', 1334), metrics.get('h', 750),
                           _VIEW.get('gap', 0.0), pool_count=len(chunk))
    width = geo['pool_scroll']['w']
    _VIEW['pool_list_width'] = width
    if _VIEW.get('geometry') is None:
        _VIEW['geometry'] = geo
    _VIEW['geometry']['pool_rows'] = geo['pool_rows']
    _VIEW['geometry']['pool_container_h'] = geo['pool_container_h']
    scroll.setInnerContainerSize(cc.cc.Size(width, geo['pool_container_h']))
    selected = _pool_selected()
    for index, (end, draw_type, row) in enumerate(chunk):
        rect = geo['pool_rows'][index]
        pending = _pool_pending(draw_type)
        node = _pool_row(cc, scroll, width, draw_type, row, end, pending,
                         draw_type in selected)
        _place_rect(node, rect)
        _register_geom('pool_row:%d' % index, node, rect)
    _safe(scroll, 'jumpToPercentVertical', 0)
    label = _VIEW.get('pool_page_label')
    if label is not None:
        try:
            label.setString(u'%d/%d' % (page + 1, pages))
        except Exception:
            pass
    _button_visible(_VIEW.get('pool_prev'), page > 0)
    _button_visible(_VIEW.get('pool_next'), page + 1 < pages)


def _render_pool_tab():
    _VIEW['pool_all'] = _pool_entries()
    _VIEW['pool_page'] = 0
    _VIEW['pool_filtered'] = list(_VIEW['pool_all'])
    _pool_refresh_header()
    _render_pool_rows()
    _pool_status(u'')


def _tab_select(comp, chosen):
    """Drive a common_tab cell without installing its global tab_common_select event."""
    active = _comp_get(comp, 'active')
    if active is not None:
        _safe(active, 'setVisible', chosen)
    prs = _comp_get(comp, 'prs')
    nml = _comp_get(comp, 'nml')
    if prs is not None:
        _safe(prs, 'setVisible', chosen)
    if nml is not None:
        _safe(nml, 'setVisible', not chosen)
    for path in ('prs.txt', 'nml.txt', 'nml.txt_shadow'):
        node = _comp_get(comp, path)
        if node is not None:
            _safe(node, 'setFontSize', _FONT_TAB)
            _safe(node, 'setColor', __import__('cocosui').cc.Color3B(
                *(255, 255, 255) if chosen else (63, 68, 87)))


def _show_group(group):
    import cocosui as cc
    _VIEW['group'] = group
    comps = _VIEW.get('tab_comps', {})
    for key, label in _VIEW.get('tab_labels', {}).items():
        chosen = key == group
        comp = comps.get(key)
        if comp is not None:
            _tab_select(comp, chosen)
        try:
            label.setColor(cc.cc.Color3B(*(255, 255, 255) if chosen else (63, 68, 87)))
        except Exception:
            pass
        slot = _VIEW.get('tab_fills', {}).get(key)
        if slot is not None and comp is None:
            try:
                slot.setBackGroundColorOpacity(255 if chosen else 0)
            except Exception:
                pass
        for name in ('tab_strips', 'tab_pointers'):
            node = _VIEW.get(name, {}).get(key)
            if node is not None:
                try:
                    node.setVisible(chosen)
                except Exception:
                    pass
    inventory = _VIEW.get('inventory_content')
    if inventory is not None:
        try:
            inventory.setVisible(group not in ('pool', 'bulk'))
        except Exception:
            pass
    pool = _VIEW.get('pool_content')
    if pool is not None:
        try:
            pool.setVisible(group == 'pool')
        except Exception:
            pass
    bulk = _VIEW.get('bulk_content')
    if bulk is not None:
        try:
            bulk.setVisible(group == 'bulk')
        except Exception:
            pass
    header = _VIEW.get('list_header')
    if header is not None and group != 'pool':
        try:
            header.setString(_HEADERS.get(group, u'\u5217\u8868'))
        except Exception:
            pass
    if group == 'pool':
        _render_pool_tab()
        return
    if group == 'bulk':
        return
    _request_catalog(preserve=False)


def _mount(panel):
    import gg
    import cocosui as cc
    if _VIEW.get('active'):
        _close()
    viewport = cc.cc.Director.getInstance().getWinSize()
    metrics = _design_metrics(viewport.width, viewport.height)
    w, h = metrics['w'], metrics['h']
    gap = _cutout_gap()
    if _DIAG:
        try:
            import profiling
            import com.data.cdata.machine_fix as MACHINE_FIX
            model = profiling.get_device_model()
            print('P7GEO cutout model=%r fixed=%r gap=%r viewport=%.1fx%.1f' % (
                model, model.lower() in MACHINE_FIX.data, gap, w, h))
        except Exception as error:
            print('P7GEO cutout failed %s' % (error,))
    geo = _editor_geometry(w, h, gap)
    # Row types that never show the quality band use this stack instead; the
    # difference only moves the quantity group, so the CTA stays anchored.
    compact = _editor_geometry(w, h, gap, quality=False)
    header_h = geo['header']['h']
    body_h = geo['body_h']
    metrics.update({'header_h': header_h, 'left_w': geo['nav_width'],
                    'body_h': body_h, 'content_w': geo['content']['w'],
                    'list_panel_w': geo['list']['w'],
                    'list_w': geo['scroll']['w'],
                    'detail_w': geo['detail']['w'],
                    'panel_h': geo['panel_h'], 'gap': gap,
                    'tab_h': geo['tab_h'], 'tab_w': geo['tab_w'],
                    'tab_top_gap': _TAB_TOP_GAP})

    root = cc.ccui.Layout.create()
    root.setContentSize(cc.cc.Size(w, h))
    root.setAnchorPoint(cc.cc.Vec2(0, 0))
    root.setPosition(cc.cc.Vec2(0, 0))
    root.setLayoutType(cc.ccui.LAYOUT_TYPE_ABSOLUTE)
    root.setBackGroundColorType(1)
    root.setBackGroundColor(cc.cc.Color3B(16, 18, 24))
    root.setBackGroundColorOpacity(235)
    root.setTouchEnabled(True)
    root.addTouchEventListener(lambda sender, event: None)
    parent = getattr(getattr(gg, 'ui', None), '_root', None) or panel._node
    parent.addChild(root, 20000)
    if _DIAG:
        try:
            ppos = parent.getPosition()
            psize = parent.getContentSize()
            pscale = parent.getScale()
            print('P7GEO parent pos=%.1f,%.1f size=%.1f,%.1f scale=%.3f name=%s' % (
                ppos.x, ppos.y, psize.width, psize.height, pscale,
                parent.getName() or '?'))
        except Exception as error:
            print('P7GEO parent failed %s' % (error,))
    global _UI_EPOCH
    _UI_EPOCH += 1
    _VIEW.update({'active': True, 'root': root, 'card': None, 'body': root,
                  'panel': panel, 'ui_epoch': _UI_EPOCH, 'metrics': metrics,
                  'csb': {}, 'tab_comps': {}, 'gap': gap, 'header': None,
                  'header_native': False,
                  'row_pool': [],
                  'rows': [], 'selected': None, 'selected_key': None,
                  'selected_token': None, 'busy': False, 'mode': 'set',
                  'quality_value': 1, 'quality_buttons': {},
                  'mode_buttons': {}, 'search': None, 'query': None,
                  'count': None, 'status': None,
                  'scroll': None, 'detail_name': None, 'held': None, 'cta': None,
                  'pending_button': None, 'detail_icon': None, 'native_skin': False,
                  'quantity_label': None, 'minus': None, 'plus': None,
                  'geometry_compact': compact, 'reflow': [],
                  'catalog_generation': 0, 'catalog_loading': False,
                  'catalog_nonce': None, 'group': 'item', 'catalog_query': '',
                  'catalog_page': 0, 'catalog_more': False, 'row_width': 0,
                  'hold_active': False, 'hold_swallow': False, 'hold_next': 0,
                  'bulk_queue': [], 'bulk_total': 0, 'bulk_done': 0,
         'bulk_content': None, 'bulk_status': None,
         'bulk_queue': [], 'bulk_total': 0, 'bulk_done': 0,
                  'list_prev': None, 'list_next': None, 'list_page': None,
                  'title': None, 'tab_labels': {}, 'tab_fills': {}, 'tab_strips': {},
                  'tab_pointers': {}, 'pool_all': [], 'pool_page': 0,
                  'pool_filtered': [], 'geometry': geo, 'geo_widgets': {}})

    # Full-screen chrome: dark native title strip flush to the top edge, then
    # the native window body colour. common_window.main is deliberately not
    # stretched: its 9-slice margins are authored for a floating window and
    # produced the 88-unit side gaps. The header itself is the native
    # mall_common.title_bar art (bar/btn_close) when that pack is available.
    card = _fill(cc, root, 0, 0, w, body_h, _FRAME_BG, 255, (0, 0))
    card.setName('editor_body')
    _VIEW['card'] = card
    _register_geom('card', card, _rect(0.0, 0.0, w, body_h))

    close_btn = None
    bar_comp = _load_comp('mall_common', 'title_bar', run_load=False)
    bar = getattr(bar_comp, '_node', None) if bar_comp is not None else None
    if bar is not None:
        try:
            bar.setVisible(True)
            _place_rect(bar, geo['header'])
            root.addChild(bar, 20)
            _safe(_comp_get(bar_comp, 'bar'), 'setContentSize',
                  cc.cc.Size(w, header_h))
            _safe(_comp_get(bar_comp, 'bar'), 'setPosition', cc.cc.Vec2(0, 0))
            close_btn = _comp_get(bar_comp, 'btn_close')
            _safe(_comp_get(bar_comp, 'btn_return'), 'setVisible', False)
            if close_btn is not None:
                _place_rect(close_btn, geo['close'], (0.5, 0.5))
            _VIEW['header_native'] = True
            _VIEW['native_skin'] = True
        except Exception:
            bar = None
    if bar is None:
        rect = geo['header']
        bar = _fill(cc, root, rect['x'], rect['y'], rect['w'], rect['h'],
                    _HEADER_BG, 255, (0, 0))
        bar.setName('editor_header')
    _VIEW['header'] = bar
    _register_geom('header', bar, geo['header'])
    if close_btn is None:
        rect = geo['close']
        close_btn = _button(cc, bar, u'<', *_anchor_xy(rect, (0.5, 0.5)),
                            width=rect['w'], callback=_close,
                            height=rect['h'])
        _register_geom('close', close_btn, rect, (0.5, 0.5))
    else:
        _native_title(close_btn, u'')
        _click(close_btn, _close, cc)
        _safe(close_btn, 'setVisible', True)
        _register_geom('close', close_btn, geo['close'], (0.5, 0.5))
    title_rect = geo['title']
    _VIEW['title'] = _text(cc, bar, u'\u80cc\u5305\u7f16\u8f91',
                           title_rect['x'],
                           title_rect['y'] + title_rect['h'] / 2.0,
                           _FONT_TITLE, (255, 255, 255), (0, 0.5))

    # Left tabs: native common_tab.tab_common_1 cells (text tabs; the
    # tab_setting textures only ship setting tab names, not item/currency/...).
    nav_rect = geo['nav']
    column = _fill(cc, card, nav_rect['x'], nav_rect['y'],
                   nav_rect['w'], nav_rect['h'], _NAV_BG, 255, (0, 0))
    column.setName('nav')
    _register_geom('nav', column, nav_rect)
    for index, (group, caption) in enumerate(_TABS):
        cell = geo['tabs'][index]
        comp = _load_comp('common_tab', 'tab_common_1', run_load=False)
        node = getattr(comp, '_node', None) if comp is not None else None
        if node is not None:
            try:
                node.setVisible(True)
                _safe(node, 'ignoreContentAdaptWithSize', False)
                _safe(node, 'setContentSize', cc.cc.Size(cell['w'], cell['h']))
                _place_rect(node, cell, (0.5, 0.5))
                # The cell node is centred on the column, so its local origin
                # is the cell centre.  Centring the state panels on that origin
                # and the labels on the panel centre keeps the text on the
                # cell centre; anchoring the panels at (0,0) instead shifted
                # every label right by half a cell (measured: 294 px -> 454 px).
                # The state panels keep their csb art size, so size them to
                # the cell and clip; their renderer is anchored at the panel
                # center and ignores the anchor, so shift it back by half.
                _safe(node, 'setClippingEnabled', True)
                for panel_path in ('active', 'prs', 'nml'):
                    panel = _comp_get(comp, panel_path)
                    if panel is None:
                        continue
                    try:
                        panel.ignoreContentAdaptWithSize(False)
                        panel.setContentSize(cc.cc.Size(cell['w'], cell['h']))
                        panel.setAnchorPoint(cc.cc.Vec2(0.5, 0.5))
                        panel.setPosition(cc.cc.Vec2(0, 0))
                        renderer = panel.getVirtualRenderer()
                        art = renderer.getContentSize()
                        if art.width > 0 and art.height > 0:
                            renderer.setScaleX(float(cell['w']) / art.width)
                            renderer.setScaleY(float(cell['h']) / art.height)
                            renderer.setPosition(cc.cc.Vec2(
                                -cell['w'] / 2.0, -cell['h'] / 2.0))
                    except Exception as error:
                        print('P7GEO tab panel %s failed %s' % (panel_path, error))
                for path in ('prs.txt', 'nml.txt', 'nml.txt_shadow'):
                    text_node = _comp_get(comp, path)
                    _safe(text_node, 'setString', caption)
                    _safe(text_node, 'setFontSize', _FONT_TAB)
                    _safe(text_node, 'ignoreContentAdaptWithSize', True)
                    _safe(text_node, 'setAnchorPoint', cc.cc.Vec2(0.5, 0.5))
                    # The label is a child of the state panel, whose anchor is
                    # now the panel centre, so a (0, 0) position draws the text
                    # from the centre toward the top right. Place it at the
                    # panel centre instead.
                    _safe(text_node, 'setPosition', cc.cc.Vec2(
                        cell['w'] / 2.0, cell['h'] / 2.0))
                _tab_select(comp, group == 'item')
                _click(node, (lambda group=group: _show_group(group)), cc)
                column.addChild(node, 3)
                _VIEW['tab_comps'][group] = comp
                _VIEW['tab_labels'][group] = (_comp_get(comp, 'nml.txt') or
                                              _comp_get(comp, 'prs.txt'))
                _VIEW['tab_fills'][group] = node
                _VIEW['native_skin'] = True
                _register_geom('tab:%s' % group, node, cell, (0.5, 0.5))
                # The csb node's hit rect does not follow setContentSize, so a
                # tap on the drawn button misses. Cover the cell with a
                # transparent layer that owns the click, above every sibling.
                hit = _fill(cc, column, cell['x'], cell['y'], cell['w'], cell['h'],
                            (0, 0, 0), 0, (0, 0))
                hit.setLocalZOrder(20)
                _click(hit, (lambda group=group: _show_group(group)), cc)
                _register_geom('tabhit:%s' % group, hit, cell)
            except Exception as error:
                if _DIAG:
                    import traceback
                    print('P7GEO tab cell %s failed %s' % (
                        group, traceback.format_exc()))
                node = None
        if node is None:
            slot = _fill(cc, column, cell['x'], cell['y'],
                         cell['w'], cell['h'], (48, 50, 62), 255, (0, 0))
            slot.setBackGroundColorOpacity(255 if group == 'item' else 0)
            _click(slot, (lambda group=group: _show_group(group)), cc)
            chosen = group == 'item'
            _VIEW['tab_labels'][group] = _text(
                cc, column, caption, cell['x'] + cell['w'] / 2.0,
                cell['y'] + cell['h'] / 2.0,
                _FONT_TAB, (255, 255, 255) if chosen else _INK, (0.5, 0.5))
            _VIEW['tab_fills'][group] = slot
            strip = _fill(cc, column, cell['x'] - 8.0, cell['y'] + 8.0, 4,
                          cell['h'] - 16.0, (222, 48, 64), 255, (0, 0))
            strip.setVisible(chosen)
            _VIEW['tab_strips'][group] = strip
            _register_geom('tab:%s' % group, slot, cell)


    # Inventory column: transparent content container so switching to the pool
    # tab hides the list AND the detail panel (they used to share one panel).
    content_rect = geo['content']
    inv = _fill(cc, card, content_rect['x'], content_rect['y'],
                content_rect['w'], content_rect['h'], _FRAME_BG, 0, (0, 0))
    inv.setName('content')
    _VIEW['inventory_content'] = inv
    _register_geom('content', inv, content_rect)
    list_rect = geo['list']
    list_panel = _fill(cc, inv, list_rect['x'], list_rect['y'],
                       list_rect['w'], list_rect['h'], _LIST_BG, 255, (0, 0))
    list_panel.setName('list')
    _register_geom('list', list_panel, list_rect)
    head_rect = geo['list_header']
    section_node, list_header = _section(cc, list_panel, _HEADERS['item'],
                                         head_rect['x'], head_rect['y'],
                                         head_rect['w'])
    _VIEW['list_header'] = list_header
    _register_geom('list_header', section_node, head_rect)

    search_rect = geo['list_search']
    _VIEW['search'] = _input(cc, list_panel, u'\u540d\u79f0 / ID', '',
                             *_anchor_xy(search_rect, (0.5, 0.5)),
                             width=search_rect['w'], height=search_rect['h'])
    _register_geom('list_search', _VIEW['search']._f7_box, search_rect,
                   (0.5, 0.5))
    query_rect = geo['list_query']
    _VIEW['query'] = _button(cc, list_panel, u'\u67e5\u8be2',
                             *_anchor_xy(query_rect, (0.5, 0.5)),
                             width=query_rect['w'],
                             callback=lambda: _request_catalog(False),
                             height=query_rect['h'])
    _register_geom('list_query', _VIEW['query'], query_rect, (0.5, 0.5))
    scroll_rect = geo['scroll']
    scroll = cc.ccui.ScrollView.create()
    scroll.setAnchorPoint(cc.cc.Vec2(0, 0))
    _place_rect(scroll, scroll_rect)
    scroll.setLayoutType(cc.ccui.LAYOUT_TYPE_ABSOLUTE)
    scroll.setDirection(1)
    scroll.setTouchEnabled(True)
    list_panel.addChild(scroll, 3)
    _VIEW['scroll'] = scroll
    _register_geom('scroll', scroll, scroll_rect)

    rect = geo['list_prev']
    _VIEW['list_prev'] = _button(cc, list_panel, u'< \u4e0a\u4e00\u9875',
                                 *_anchor_xy(rect, (0.5, 0.5)),
                                 width=rect['w'],
                                 callback=lambda: _catalog_page_step(-1),
                                 height=rect['h'])
    _register_geom('list_prev', _VIEW['list_prev'], rect, (0.5, 0.5))
    rect = geo['list_next']
    _VIEW['list_next'] = _button(cc, list_panel, u'\u4e0b\u4e00\u9875 >',
                                 *_anchor_xy(rect, (0.5, 0.5)),
                                 width=rect['w'],
                                 callback=lambda: _catalog_page_step(1),
                                 height=rect['h'])
    _register_geom('list_next', _VIEW['list_next'], rect, (0.5, 0.5))
    rect = geo['list_page']
    page_x, page_y = _anchor_xy(rect, (0.5, 0.5))
    _VIEW['list_page'] = _text(cc, list_panel, u'\u7b2c 1 \u9875',
                               page_x, page_y, _FONT_META, _INK_META, (0.5, 0.5))
    _register_geom('list_page', _VIEW['list_page'], rect, (0.5, 0.5),
                   check_size=False)

    detail_rect = geo['detail']
    detail = _fill(cc, inv, detail_rect['x'], detail_rect['y'],
                   detail_rect['w'], detail_rect['h'], _DETAIL_BG, 255, (0, 0))
    detail.setName('detail')
    _register_geom('detail', detail, detail_rect)
    dhead_rect = geo['detail_header']
    section_node, detail_header = _section(cc, detail, u'\u7f16\u8f91',
                                           dhead_rect['x'], dhead_rect['y'],
                                           dhead_rect['w'])
    _VIEW['detail_header'] = detail_header
    _register_geom('detail_header', section_node, dhead_rect)

    _VIEW['detail_rects'] = geo['detail_band_rects']
    icon_size = float(_DETAIL_ICON)
    _VIEW['detail_icon_size'] = icon_size
    icon_rect = geo['detail_icon']
    icon = cc.ccui.ImageView.create()
    _place_rect(icon, icon_rect, (0.5, 0.5))
    icon.setVisible(False)
    detail.addChild(icon, 3)
    _VIEW['detail_icon'] = icon
    _VIEW['detail_icon_key'] = None
    _register_geom('detail_icon', icon, icon_rect, (0.5, 0.5))
    name_rect = geo['detail_name']
    _VIEW['detail_name'] = _text(cc, detail, u'\u672a\u9009\u62e9\u6761\u76ee',
                                 *_anchor_xy(name_rect, (0, 0.5)),
                                 size=_FONT_BODY, color=_INK, anchor=(0, 0.5))
    held_rect = geo['held_label']
    held_y = held_rect['y'] + held_rect['h'] / 2.0
    _text(cc, detail, u'\u5f53\u524d\u6301\u6709', held_rect['x'], held_y,
          _FONT_META, _INK_META, (0, 0.5))
    value_rect = geo['held_value']
    _VIEW['held'] = _text(cc, detail, u'0',
                          value_rect['x'],
                          value_rect['y'] + value_rect['h'] / 2.0,
                          _FONT_TITLE, _INK, (0, 0.5))

    for index, (mode, label) in enumerate((('set', u'\u8bbe\u4e3a'), ('add', u'\u589e\u52a0'))):
        def choose(mode=mode):
            _set_mode(mode)
        rect = geo['modes'][index]
        caption = geo['mode_labels'][index]
        _VIEW['mode_buttons'][mode] = _chip(
            cc, detail, label, *_anchor_xy(rect, (0.5, 0.5)),
            size=rect['w'], callback=choose, selected=mode == 'set',
            caption=(caption['x'], caption['y'] + caption['h'] / 2.0))
        _register_geom('mode:%s' % mode, _VIEW['mode_buttons'][mode], rect,
                       (0.5, 0.5))

    qlabel_rect = geo['quality_label']
    _VIEW['quality_label'] = _text(cc, detail, u'\u54c1\u8d28',
                                   qlabel_rect['x'],
                                   qlabel_rect['y'] + qlabel_rect['h'] / 2.0,
                                   _FONT_META, _INK_META, (0, 0.5))
    for value in range(1, 6):
        def choose(value=value):
            _VIEW['quality_value'] = value
            _refresh_detail()
        rect = geo['quality'][value - 1]
        caption = geo['quality_labels'][value - 1]
        _VIEW['quality_buttons'][value] = _chip(
            cc, detail, u'%d' % value, *_anchor_xy(rect, (0.5, 0.5)),
            size=rect['w'], callback=choose, selected=value == 1,
            caption=(caption['x'], caption['y'] + caption['h'] / 2.0))
        _register_geom('quality:%d' % value, _VIEW['quality_buttons'][value],
                       rect, (0.5, 0.5))

    qty_rect = geo['quantity_label']
    _VIEW['quantity_label'] = _text(cc, detail, u'\u6570\u91cf',
                                    qty_rect['x'],
                                    qty_rect['y'] + qty_rect['h'] / 2.0,
                                    _FONT_META, _INK_META, (0, 0.5))
    _reflow_register(_VIEW['quantity_label'])
    rect = geo['minus']
    _VIEW['minus'] = _button(cc, detail, u'-', *_anchor_xy(rect, (0.5, 0.5)),
                             width=rect['w'], callback=lambda: _bump(-1),
                             height=rect['h'],
                             events=lambda event: _hold_event(cc, event, -1))
    _register_geom('minus', _VIEW['minus'], rect, (0.5, 0.5))
    _reflow_register(_VIEW['minus'])
    _reflow_register(_shield(cc, detail, rect, lambda: _bump(-1),
                             events=lambda event: _hold_event(cc, event, -1)))
    rect = geo['count']
    _VIEW['count'] = _input(cc, detail, u'\u6570\u91cf', '1',
                            *_anchor_xy(rect, (0.5, 0.5)),
                            width=rect['w'], height=rect['h'], digits=True)
    _register_geom('count', _VIEW['count']._f7_box, rect, (0.5, 0.5))
    for part in (_VIEW['count'], _VIEW['count']._f7_box,
                 _VIEW['count']._f7_border, _VIEW['count']._f7_shield):
        _reflow_register(part)
    rect = geo['plus']
    _VIEW['plus'] = _button(cc, detail, u'+', *_anchor_xy(rect, (0.5, 0.5)),
                            width=rect['w'], callback=lambda: _bump(1),
                            height=rect['h'],
                            events=lambda event: _hold_event(cc, event, 1))
    _register_geom('plus', _VIEW['plus'], rect, (0.5, 0.5))
    _reflow_register(_VIEW['plus'])
    _reflow_register(_shield(cc, detail, rect, lambda: _bump(1),
                             events=lambda event: _hold_event(cc, event, 1)))

    rect = geo['cta']
    _VIEW['cta'] = _button(cc, detail, u'\u4fdd\u5b58\u6570\u91cf',
                           *_anchor_xy(rect, (0.5, 0.5)),
                           width=rect['w'],
                           callback=lambda: _apply(_VIEW.get('mode', 'set')),
                           height=rect['h'], primary=True)
    _safe(_VIEW['cta'], 'setTitleFontSize', 26)
    _register_geom('cta', _VIEW['cta'], rect, (0.5, 0.5))
    rect = geo['pending']
    _VIEW['pending_button'] = _button(cc, detail, u'\u6838\u5bf9\u4e0a\u6b21\u64cd\u4f5c',
                                      *_anchor_xy(rect, (0.5, 0.5)),
                                      width=rect['w'],
                                      callback=_retry_pending,
                                      height=rect['h'])
    _register_geom('pending', _VIEW['pending_button'], rect, (0.5, 0.5))
    status_rect = geo['status']
    _VIEW['status'] = _text(cc, detail, u'\u8bf7\u9009\u62e9\u6761\u76ee',
                            status_rect['x'],
                            status_rect['y'] + status_rect['h'] / 2.0,
                            _FONT_META, _INK_META, (0, 0.5))
    _reflow_register(_VIEW['status'])

    pool_rect = geo['pool']
    pool_origin = _rect(content_rect['x'], content_rect['y'],
                        pool_rect['w'], pool_rect['h'])
    # `pool` is authored in content-local units; drawing it at the card origin
    # put the white panel over the left tab column when the tab was opened.
    pool = _fill(cc, card, pool_origin['x'], pool_origin['y'],
                 pool_origin['w'], pool_origin['h'], _LIST_BG, 255, (0, 0))
    pool.setName('pool')
    _VIEW['pool_content'] = pool
    pool.setVisible(False)
    _register_geom('pool', pool, pool_origin)
    bulk_rect = geo['bulk']
    bulk = _fill(cc, card, content_rect['x'] + bulk_rect['x'],
                 content_rect['y'] + bulk_rect['y'],
                 bulk_rect['w'], bulk_rect['h'], _LIST_BG, 255, (0, 0))
    bulk.setName('bulk')
    _VIEW['bulk_content'] = bulk
    bulk.setVisible(False)
    _register_geom('bulk', bulk, _rect(content_rect['x'], content_rect['y'],
                                       bulk_rect['w'], bulk_rect['h']))
    for index, (key, label, note) in enumerate(_BULK):
        rect = geo['bulk_rows'][index]
        button = _button(cc, bulk, label, *_anchor_xy(rect, (0.5, 0.5)),
                         width=rect['w'], height=rect['h'],
                         callback=(lambda key=key: _bulk_run(key)))
        _register_geom('bulk:%s' % key, button, rect, (0.5, 0.5))
        if _DIAG and index == 0:
            _probe_button(cc, 'bulk0', button)
    bulk_status_rect = geo['bulk_status']
    _VIEW['bulk_status'] = _text(cc, bulk, u'',
                                 bulk_status_rect['x'],
                                 bulk_status_rect['y'] + bulk_status_rect['h'] / 2.0,
                                 _FONT_META, _INK_META, (0, 0.5))
    _VIEW['pool_list_width'] = geo['pool_scroll']['w']
    phead_rect = geo['pool_header']
    section_node, pool_header = _section(
        cc, pool,
        u'\u5361\u6c60\u5f00\u5173  \u5df2\u5f00\u542f 0/%d' % _POOL_CAP,
        phead_rect['x'], phead_rect['y'], phead_rect['w'])
    _VIEW['pool_header'] = pool_header
    _register_geom('pool_header', section_node, phead_rect)

    rect = geo['pool_search']
    _VIEW['pool_search'] = _input(cc, pool, u'\u540d\u79f0 / ID', '',
                                  *_anchor_xy(rect, (0.5, 0.5)),
                                  width=rect['w'], height=rect['h'])
    _register_geom('pool_search', _VIEW['pool_search']._f7_box, rect,
                   (0.5, 0.5))
    rect = geo['pool_search_button']
    _VIEW['pool_search_button'] = _button(
        cc, pool, u'\u641c\u7d22', *_anchor_xy(rect, (0.5, 0.5)),
        width=rect['w'], callback=_pool_apply_search, height=rect['h'])
    _register_geom('pool_search_button', _VIEW['pool_search_button'], rect,
                   (0.5, 0.5))
    rect = geo['pool_close']
    _VIEW['pool_close'] = _button(
        cc, pool, u'\u5168\u90e8\u5173\u95ed', *_anchor_xy(rect, (0.5, 0.5)),
        width=rect['w'], callback=_pool_close_all, height=rect['h'])
    _register_geom('pool_close', _VIEW['pool_close'], rect, (0.5, 0.5))

    rect = geo['pool_scroll']
    pool_scroll = cc.ccui.ScrollView.create()
    pool_scroll.setAnchorPoint(cc.cc.Vec2(0, 0))
    _place_rect(pool_scroll, rect)
    pool_scroll.setLayoutType(cc.ccui.LAYOUT_TYPE_ABSOLUTE)
    pool_scroll.setDirection(1)
    pool_scroll.setTouchEnabled(True)
    pool.addChild(pool_scroll, 3)
    _VIEW['pool_scroll'] = pool_scroll
    _register_geom('pool_scroll', pool_scroll, rect)

    rect = geo['pool_prev']
    _VIEW['pool_prev'] = _button(cc, pool, u'< \u4e0a\u4e00\u9875',
                                 *_anchor_xy(rect, (0.5, 0.5)),
                                 width=rect['w'],
                                 callback=lambda: _pool_page_step(-1),
                                 height=rect['h'])
    _register_geom('pool_prev', _VIEW['pool_prev'], rect, (0.5, 0.5))
    rect = geo['pool_next']
    _VIEW['pool_next'] = _button(cc, pool, u'\u4e0b\u4e00\u9875 >',
                                 *_anchor_xy(rect, (0.5, 0.5)),
                                 width=rect['w'],
                                 callback=lambda: _pool_page_step(1),
                                 height=rect['h'])
    _register_geom('pool_next', _VIEW['pool_next'], rect, (0.5, 0.5))
    rect = geo['pool_page_label']
    page_x, page_y = _anchor_xy(rect, (0.5, 0.5))
    _VIEW['pool_page_label'] = _text(cc, pool, u'1/1', page_x, page_y,
                                     _FONT_META, _INK_META, (0.5, 0.5))
    rect = geo['pool_status']
    _VIEW['pool_status'] = _text(cc, pool, u'', rect['x'],
                                 rect['y'] + rect['h'] / 2.0,
                                 _FONT_META, _INK_META, (0, 0.5))
    rect = geo['pool_note']
    _text(cc, pool, u'\u4fee\u6539\u540e\u91cd\u65b0\u8fdb\u5165\u767d\u591c\u9986\u751f\u6548',
          rect['x'] + rect['w'], rect['y'] + rect['h'] / 2.0,
          _FONT_META, _INK_META, (1, 0.5))

    _update_pending_button()
    _refresh_detail()
    _show_group('item')
    if _DIAG:
        _probe_button(cc, 'query', _VIEW.get('query'))
        _probe_button(cc, 'minus', _VIEW.get('minus'))
        _probe_button(cc, 'cta', _VIEW.get('cta'))
        _dump_geometry()


def _step(delta):
    field = _VIEW.get('count')
    if field is None:
        return
    try:
        value = int(field.getString()) + delta
    except Exception:
        value = 1
    if value < 0:
        value = 0
    if value > 1000000:
        value = 1000000
    field.setString(str(value))


_HOLD_DELAY_MS = 450
_HOLD_INTERVAL_MS = 110
_HOLD_MIN_MS = 35
_HOLD_ACCEL_MS = 12


def _hold_stop():
    _VIEW['hold_active'] = False


def _hold_tick(delta):
    """Repeat while the stepper is held, accelerating to _HOLD_MIN_MS."""
    if not _VIEW.get('hold_active'):
        return
    _VIEW['hold_swallow'] = True
    _step(delta)
    interval = int(_VIEW.get('hold_next') or _HOLD_INTERVAL_MS)
    _VIEW['hold_next'] = max(_HOLD_MIN_MS, interval - _HOLD_ACCEL_MS)
    try:
        import gg
        gg.exec_delay(interval, lambda: _hold_tick(delta))
    except Exception:
        _hold_stop()


def _hold_press(delta):
    _VIEW['hold_active'] = True
    _VIEW['hold_swallow'] = False
    _VIEW['hold_next'] = _HOLD_INTERVAL_MS
    try:
        import gg
        gg.exec_delay(_HOLD_DELAY_MS, lambda: _hold_tick(delta))
    except Exception:
        _hold_stop()


def _hold_event(cc, event, delta):
    """Start/stop the repeat from the stepper's own touch events."""
    began = getattr(cc.ccui, 'TOUCH_EVENT_BEGAN', None)
    ended = getattr(cc.ccui, 'TOUCH_EVENT_ENDED', None)
    canceled = getattr(cc.ccui, 'TOUCH_EVENT_CANCELED', None)
    if began is not None and event == began:
        _hold_press(delta)
    elif event == ended or (canceled is not None and event == canceled):
        _hold_stop()


def _bump(delta):
    """A tap bumps once; a held button already applied its repeats."""
    if _VIEW.get('hold_swallow'):
        return
    _step(delta)


def _add_bbs_home_app(panel):
    try:
        app_dict = getattr(panel, 'app_dict', None)
        if not isinstance(app_dict, dict):
            return False
        for info in app_dict.values():
            if info.get('name') == u'\u80cc\u5305\u7f16\u8f91':
                return False
        index = (max(app_dict) + 1) if app_dict else 0
        app_dict[index] = dict(
            name=u'\u80cc\u5305\u7f16\u8f91',
            cb_click=panel.on_f7_inventory_click,
            icon_name='bag',
            red_cb=None,
            use_jingshenli=False)
        return True
    except Exception:
        return False


def _install_bbs_home():
    import gg
    import cocosui as cc
    import cocos.panels.bbs_home as home
    cls = home.Panel
    if getattr(cls, _BBS_MARKER, None) is not cc:
        original = getattr(cls, 'refresh_app_sort', None)
        if original is None:
            raise RuntimeError('bbs_home panel ABI changed')

        def refresh_app_sort(self, *args, **kwargs):
            result = original(self, *args, **kwargs)
            _add_bbs_home_app(self)
            return result

        def on_f7_inventory_click(self, sender, event):
            if event != cc.ccui.TOUCH_EVENT_ENDED:
                return
            _mount(self)

        cls.refresh_app_sort = refresh_app_sort
        cls.on_f7_inventory_click = on_f7_inventory_click
        setattr(cls, _BBS_MARKER, cc)
    live = getattr(getattr(getattr(gg, 'ui', None), 'panels', None), 'bbs_home', None)
    if live is not None:
        _add_bbs_home_app(live)
        try:
            if getattr(live, 'valid', False) and getattr(live, 'screen_comp', None):
                live.refresh_bbs_home_app_sort()
        except Exception:
            pass
    return cc


def _bind_pool_api(policy):
    """The editor reads/writes the pool selection through draw_ui's installer."""
    api = getattr(policy, 'draw_ui', None)
    if api is not None and callable(getattr(api, 'selection', None)):
        _VIEW['pool_api'] = api
        return api
    return None


def bind_startup(patch, policy):
    """Wrap the already mature patch.clean; import game/avatar only after it.

    The loader must not import gg/ClientAvatar before StartupPolicy.clean has
    purged and reinstalled the original Members. This wrapper has no game
    imports itself and only activates the editor after the old clean returns
    successfully with a live/offline policy.
    """
    original = getattr(patch, 'clean', None)
    if not callable(original):
        raise RuntimeError('patch.clean ABI changed')
    if getattr(patch, '_f7_inventory_clean_owner', None) is not None:
        return patch._f7_inventory_clean_owner

    def clean(*args, **kwargs):
        state = args[0] if args else kwargs.get('state')
        result = original(*args, **kwargs)
        if state and result is not False:
            try:
                _bind_pool_api(policy)
            except Exception:
                pass
            try:
                live = getattr(policy, 'live', None)
                if live is None or live():
                    install()
            except Exception:
                # An editor install failure must not break the mature clean
                # chain or invent a successful startup.
                pass
        return result

    patch.clean = clean
    patch._f7_inventory_clean_owner = clean
    return clean


def install():
    """Idempotent same-generation install. No IO or profile mutation here."""
    import gg
    try:
        _install_rpc()
    except Exception:
        gg.exec_delay(1000, _install_rpc)
    try:
        owner = _install_bbs_home()
    except Exception:
        owner = None
        gg.exec_delay(1000, _install_bbs_home)
    identity = _identity()
    if identity and _load_pending(identity) is not None:
        _VIEW['selected'] = None
    return owner
