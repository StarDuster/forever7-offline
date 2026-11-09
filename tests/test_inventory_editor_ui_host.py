"""Client-side synthetic host for the inventory editor UI wiring.

This is not the original Cocos engine and not native acceptance. It proves
BBS-home app installation idempotence, ClientAvatar typed handlers, pending-op
persistence and one-op retry admission without a second profile owner.
"""
import _paths  # noqa: E402,F401
import importlib.util
import json
import os
import sys
import tempfile
import types

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODULE = os.path.join(ROOT, 'offline', 'current', 'runtime', 'project7_inventory_editor_ui.py')


def module(name, **attrs):
    value = types.ModuleType(name)
    for key, item in attrs.items():
        setattr(value, key, item)
    sys.modules[name] = value
    return value


def main():
    calls = []
    locks = []

    class Label(object):
        def __init__(self):
            self.value = ''

        def setString(self, value):
            self.value = value

    class Avatar(object):
        account = 'host-account'

        def callServerMethodReliable(self, name, params, **kwargs):
            calls.append((name, params))

    class UI(object):
        def lock(self, key):
            locks.append(('lock', key))

        def unlock(self, key):
            locks.append(('unlock', key))

    class Panels(object):
        pass

    ui = UI()
    ui._lock = None
    prompts = []
    module('cocos.ui_utils',
           show_input=lambda text, cb, type=0, hint=False: prompts.append(cb))
    gg = module('gg', avatar=Avatar(), ui=ui)
    scheduled = []
    gg.exec_delay = lambda ms, fn: scheduled.append((ms, fn))

    class Margin(object):
        def __init__(self):
            self.left = 0
            self.right = 0
            self.top = 0
            self.bottom = 0

    class LayoutParameter(object):
        def __init__(self):
            self.margin = Margin()
        def getMargin(self): return self.margin
        def setMargin(self, value): self.margin = value

    class NodeImpl(object):
        @staticmethod
        def create():
            return NodeImpl()
        def __init__(self):
            self.children = []
            self.position = None
            self.name = ''
            self.layout_parameter = LayoutParameter()
        def getName(self): return self.name
        def setName(self, value): self.name = value
        def getLayoutParameter(self): return self.layout_parameter
        def requestDoLayout(self): self.layout_requested = True
        def clone(self):
            value = NodeImpl()
            value.name = self.name
            for child in self.children:
                value.addChild(child.clone())
            return value
        def setAnchorPoint(self, value): self.anchor = value
        def setPosition(self, value): self.position = value
        def setContentSize(self, value): self.size = value
        def getContentSize(self): return self.size
        def getParent(self): return getattr(self, 'parent', None)
        def getPosition(self): return self.position
        def setLayoutType(self, value): self.layout_type = value
        def setLocalZOrder(self, value): self.z_order = value
        def ignoreContentAdaptWithSize(self, value): self.ignore_adapt = value
        def setRotation(self, value): self.rotation = value
        def setVisible(self, value): self.visible = value
        def isVisible(self): return getattr(self, 'visible', True)
        def setTouchEnabled(self, value): self.touch = value
        def addTouchEventListener(self, value): self.listener = value
        def convertToNodeSpace(self, value): return value
        def getChildren(self): return list(getattr(self, 'children', []))
        def getChildByName(self, name):
            for child in getattr(self, 'children', []):
                if getattr(child, 'name', '') == name:
                    return child
            return None
        def addChild(self, child, *args):
            child.parent = self
            self.children.append(child)
        def removeFromParent(self):
            if getattr(self, 'parent', None) is not None:
                try:
                    self.parent.children.remove(self)
                except Exception:
                    pass
            self.parent = None

    class TemplateButtonImpl(NodeImpl):
        """common_confirm_4 button: baked csb title states text_nml/text_gry."""
        def __init__(self):
            NodeImpl.__init__(self)
            self.title = TextImpl()
            self.title.setName('text_nml')
            self.title.setString(u'\u53d6\u6d88')
            self.gray = TextImpl()
            self.gray.setName('text_gry')
            self.gray.setString(u'\u53d6\u6d88')
            self.children.extend((self.title, self.gray))
        def clone(self):
            return TemplateButtonImpl()
        def ignoreContentAdaptWithSize(self, value): pass
        def setTitleText(self, value): self.title.setString(value)

    class LayoutImpl(NodeImpl):
        @staticmethod
        def create():
            return LayoutImpl()
        def setBackGroundColorType(self, value): pass
        def setBackGroundColor(self, value): pass
        def setBackGroundColorOpacity(self, value): pass

    class ButtonImpl(NodeImpl):
        @staticmethod
        def create():
            return ButtonImpl()
        def setTitleText(self, value): pass
        def setTitleFontSize(self, value): pass
        def setTitleColor(self, value): pass
        def ignoreContentAdaptWithSize(self, value): pass
        def setTouchEnabled(self, value): pass
        def addTouchEventListener(self, value): pass

    class TextFieldImpl(NodeImpl):
        @staticmethod
        def create(*args):
            value = TextFieldImpl()
            value.text = ''
            value.font = args[1] if len(args) > 1 else ''
            return value
        def setTextColor(self, value): pass
        def setString(self, value): self.text = value
        def getString(self): return self.text
        def setTouchSize(self, size): self.touch_size = size
        def setTextVerticalAlignment(self, value): self.alignment = value
        def addEventListener(self, listener):
            self.listeners = getattr(self, 'listeners', [])
            self.listeners.append(listener)
        def emit(self, event):
            for listener in getattr(self, 'listeners', []):
                listener(self, event)

    class ImageViewImpl(NodeImpl):
        @staticmethod
        def create():
            return ImageViewImpl()
        def __init__(self):
            NodeImpl.__init__(self)
            self.textures = []
        def loadTexture(self, path): self.textures.append(path)
        def ignoreContentAdaptWithSize(self, value): self.ignore_adapt = value

    class TextImpl(NodeImpl):
        @staticmethod
        def create(*args):
            return TextImpl()
        def __init__(self):
            NodeImpl.__init__(self)
            self.text = ''
            self.font_size = 0
        def setString(self, value): self.text = value
        def setColor(self, value): pass
        def setFontName(self, value): pass
        def setFontSize(self, value): self.font_size = value

    class CheckboxImpl(NodeImpl):
        def __init__(self):
            NodeImpl.__init__(self)
            self.sel = NodeImpl()
            self.sel.setName('sel')
            self.sel.setVisible(False)
            self.children.append(self.sel)
        def clone(self):
            value = CheckboxImpl()
            value.setName(self.name)
            return value

    class FakeComp(object):
        def __init__(self, node):
            self._node = node
        def load(self):
            return None
        def __getitem__(self, path):
            node = self._node
            for part in path.split('.'):
                node = node.getChildByName(part)
                if node is None:
                    raise KeyError(path)
            return node
        def set_title(self, text):
            self['bg.label'].setString(text)

    class FakeTabComp(FakeComp):
        def set_info(self, index, name):
            for path in ('prs.txt', 'nml.txt', 'nml.txt_shadow'):
                self[path].setString(name)

    class FakeBarComp(FakeComp):
        pass

    class GUIReader(object):
        @classmethod
        def getInstance(cls):
            return cls()
        def widgetFromBinaryFile(self, path, *args):
            if path.endswith('common_window.csb'):
                root = NodeImpl()
                main = NodeImpl()
                main.setName('main')
                for name in ('bg', 'back', 'close', 'currency'):
                    child = ButtonImpl()
                    child.setName(name)
                    main.addChild(child)
                root.addChild(main)
                return root
            if path.endswith('common_confirm_4.csb'):
                root = NodeImpl()
                main = NodeImpl()
                main.setName('main')
                info = NodeImpl()
                info.setName('info')
                confirm = TemplateButtonImpl()
                confirm.setName('btn_confirm')
                cancel = TemplateButtonImpl()
                cancel.setName('btn_cancel')
                checkbox_1 = CheckboxImpl()
                checkbox_1.setName('checkbox_1')
                checkbox_2 = CheckboxImpl()
                checkbox_2.setName('checkbox_2')
                info.addChild(confirm)
                info.addChild(cancel)
                info.addChild(checkbox_1)
                info.addChild(checkbox_2)
                main.addChild(info)
                root.addChild(main)
                return root
            raise RuntimeError('missing csb: %s' % path)
        def widgetFromJsonFile(self, path, *args):
            raise RuntimeError('missing json: %s' % path)

    class ScrollViewImpl(NodeImpl):
        percent = None
        @staticmethod
        def create():
            return ScrollViewImpl()
        def setDirection(self, value): pass
        def setInnerContainerSize(self, value): self.inner = value
        def jumpToPercentVertical(self, value): self.percent = value
        def setTouchEnabled(self, value): pass
        def removeAllChildren(self): self.children = []

    class CCUI(object):
        TOUCH_EVENT_ENDED = 2
        TOUCH_EVENT_BEGAN = 1
        TOUCH_EVENT_CANCELED = 3
        TEXTFIELD_EVENT_INSERT_TEXT = 10
        TEXTFIELD_EVENT_DETACH_WITH_IME = 11
        LAYOUT_TYPE_ABSOLUTE = 1
        Button = ButtonImpl
        Layout = LayoutImpl
        TextField = TextFieldImpl
        Text = TextImpl
        ImageView = ImageViewImpl
        ScrollView = ScrollViewImpl

    class CC(object):
        ccui = CCUI
        ccs = types.SimpleNamespace(GUIReader=GUIReader)
        class Size(object):
            def __init__(self, *args):
                self.width = args[0] if args else 0
                self.height = args[1] if len(args) > 1 else 0
        class Vec2(object):
            def __init__(self, *args): self.x = args[0] if args else 0; self.y = args[1] if len(args) > 1 else 0
        class Color3B(object):
            def __init__(self, *args): pass
        class Color4B(object):
            def __init__(self, *args): pass
        class Node(NodeImpl):
            pass
        class Director(object):
            @classmethod
            def getInstance(cls):
                return cls()
            def getWinSize(self):
                return types.SimpleNamespace(width=1334, height=750)

    cocosui = module('cocosui', ccui=CCUI, cc=CC, ccs=CC.ccs)
    setting = module('cocos.panels.setting')
    class SettingPanel(object):
        def __init__(self):
            self._node = NodeImpl()
            self.children = self._node.children
        def on_load(self):
            return 'stock'
        def notify_show(self):
            return 'shown'
        def on_navigation_canvas_close(self):
            return 'closed'
    setting.Panel = SettingPanel
    class BbsPanel(NodeImpl):
        def __init__(self):
            NodeImpl.__init__(self)
            self._node = self
            self.app_dict = {0: dict(name=u'\u8bbe\u7f6e', cb_click=lambda *a: None,
                                      icon_name='set', red_cb=None, use_jingshenli=False)}
            self.valid = False
        def refresh_app_sort(self):
            return None
    setting_bbs = module('cocos.panels.bbs_home', Panel=BbsPanel)
    panels = Panels()
    late_panel = SettingPanel()
    bbs_panel = BbsPanel()
    panels.setting = late_panel
    panels.bbs_home = bbs_panel
    ui.panels = panels

    def fake_label(name, text=''):
        value = TextImpl()
        value.setName(name)
        value.setString(text)
        return value

    def tab_tree():
        root = NodeImpl()
        for panel_name in ('prs', 'nml'):
            panel = NodeImpl()
            panel.setName(panel_name)
            panel.addChild(fake_label('txt'))
            if panel_name == 'nml':
                panel.addChild(fake_label('txt_shadow'))
            root.addChild(panel)
        active = NodeImpl()
        active.setName('active')
        active.setVisible(False)
        root.addChild(active)
        return root

    def item_tree():
        root = NodeImpl()
        for name in ('bg', 'sel'):
            child = NodeImpl()
            child.setName(name)
            root.addChild(child)
        img = ImageViewImpl()
        img.setName('img')
        root.addChild(img)
        info = NodeImpl()
        info.setName('info')
        info.addChild(fake_label('outter'))
        info.addChild(fake_label('inner'))
        root.addChild(info)
        return root

    def title_tree():
        root = NodeImpl()
        bg = NodeImpl()
        bg.setName('bg')
        bg.addChild(fake_label('label'))
        root.addChild(bg)
        return root

    def bar_tree():
        root = NodeImpl()
        bar = NodeImpl()
        bar.setName('bar')
        root.addChild(bar)
        for name in ('btn_close', 'btn_return'):
            node = TemplateButtonImpl()
            node.setName(name)
            root.addChild(node)
        return root

    class FactoryPack(object):
        def __init__(self, name, factory):
            self.name = name
            self.factory = factory
        def __getattr__(self, attr):
            if attr.startswith('_'):
                raise AttributeError(attr)
            return self.factory(attr)

    def tab_factory(attr):
        if attr != 'tab_common_1':
            return None
        return FakeTabComp(tab_tree())

    def item_factory(attr):
        return FakeComp(item_tree()) if attr == 'item' else None

    def title_factory(attr):
        return FakeComp(title_tree()) if attr == 'title_static' else None

    def bar_factory(attr):
        return FakeBarComp(bar_tree()) if attr == 'title_bar' else None

    ui.comps = types.SimpleNamespace(
        common_tab=FactoryPack('common_tab', tab_factory),
        common_frame=FactoryPack('common_frame', item_factory),
        common_info=FactoryPack('common_info', title_factory),
        mall_common=FactoryPack('mall_common', bar_factory))
    ui.projplistinfo = {}
    model = {'name': 'desktop'}
    module('profiling', get_device_model=lambda: model['name'])
    module('com.data.cdata.machine_fix', data={'fake_full_screen_phone': 1})
    module('cocos', panels=types.SimpleNamespace(setting=setting, bbs_home=setting_bbs))
    module('cocos.panels', setting=setting, bbs_home=setting_bbs)

    decorated = []
    def rpc_method(rpctype, argtypes=(), pub=True):
        def wrap(fn):
            decorated.append((fn.__name__, argtypes))
            return fn
        return wrap
    class Arg(object):
        def __init__(self, name): self.name = name
    module('common.rpcdecorator', rpc_method=rpc_method, CLIENT_STUB=3)
    module('common.RpcMethodArgs', Bool=Arg, Int=Arg, Str=Arg, List=Arg,
           Dict=Arg)
    registered = []
    class Decoder(object):
        @staticmethod
        def register_str(name):
            registered.append(name)
    module('common.Md5OrIndexCodec', Md5OrIndexDecoder=Decoder)
    class ClientAvatar(object):
        pass
    module('entity.ClientAvatar', ClientAvatar=ClientAvatar)
    module('entity', ClientAvatar=ClientAvatar)
    calls_dir = tempfile.mkdtemp(prefix='inventory-ui-host-')
    module('game3d', get_doc_dir=lambda: calls_dir)

    com = module('com')
    com.data = module('com.data')
    com.data.cdata = module('com.data.cdata')
    com.data.cdata.item_data = module('com.data.cdata.item_data', data={
        1: {'icon': '10005', 'type': 1}, 2: {'icon': '1001', 'type': 5}})
    pools = {}
    for draw_type in range(1, 441):
        pools[draw_type] = dict(room_title=u'pool %d' % draw_type,
                                begin_time=(2020, 1, 1, 7, 0, 0, 0, 0, 0),
                                end_time=(2020, 1, 1 + draw_type % 28, 7, 0, 0, 0, 0, 0),
                                poolType=1)
    com.data.cdata.chouka_info = module('com.data.cdata.chouka_info', data=pools)
    com.data.cdata.cg_data = module('com.data.cdata.cg_data',
                                    data={3: {}, 1: {}, 2: {}})

    class PoolApi(object):
        def __init__(self):
            self.ready = frozenset(pools)
            self.ids = []
            self.calls = []

        def selection(self):
            return frozenset(self.ids)

        def set_selection(self, ids):
            ids = sorted(set(ids))
            if len(ids) > 12:
                return False
            self.ids = ids
            self.calls.append(tuple(ids))
            return True

    pool_api = PoolApi()
    com.const = module('com.const', ItemType=types.SimpleNamespace(VIRTUAL=3),
                       VirtualItemSub=types.SimpleNamespace(MEMORY_FRAG=7),
                       IPHONEX_FIX_GAP=88)

    spec = importlib.util.spec_from_file_location('project7_inventory_editor_ui', MODULE)
    editor = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(editor)
    editor._new_op = lambda: 'a' * 32
    editor._VIEW['pool_api'] = pool_api

    assert editor.install() is cocosui
    assert editor.install() is cocosui
    apps = bbs_panel.app_dict
    matches = [info for info in apps.values()
               if info.get('name') == u'\u80cc\u5305\u7f16\u8f91']
    assert len(matches) == 1, 'BBS home receives exactly one backpack editor app'
    app = matches[0]
    assert app['icon_name'] == 'bag', 'reuse the shipped backpack icon'
    app['cb_click'](None, CCUI.TOUCH_EVENT_ENDED)
    assert editor._VIEW.get('active') is True, 'BBS app click opens the editor overlay'
    editor._close()
    pre_reopen_token = (editor._VIEW.get('ui_epoch'), editor._VIEW.get('catalog_generation'))
    editor._close()
    ui._root = NodeImpl()
    editor._mount(late_panel)
    overlay = ui._root.children[-1]
    assert overlay is editor._VIEW['root'], 'full-screen layer is the overlay root'
    assert (overlay.position.x, overlay.position.y) == (0, 0), 'full viewport origin'
    assert (overlay.size.width, overlay.size.height) == (1334, 750), 'covers the win size'
    assert overlay.layout_type == CCUI.LAYOUT_TYPE_ABSOLUTE, 'backdrop absolute layout'
    assert 'scale' not in editor._VIEW, 'no design-to-pixel multiplier state'
    assert editor._VIEW['native_skin'] is True, 'native csb comps drive the chrome'
    header = editor._VIEW['header']
    assert header is not None, 'full-screen header strip built'
    assert (header.size.width, header.size.height) == (1334, 88), 'header spans the screen edge-to-edge'
    assert header.getParent() is overlay, 'header is flush with the top edge, not inside a card'
    assert editor._VIEW['header_native'] is True, 'mall_common.title_bar supplies the header art'
    assert (header.position.x, header.position.y) == (0, 662), 'header sits at the top, body below'
    assert editor._VIEW['card'] is not header
    assert (editor._VIEW['card'].size.width, editor._VIEW['card'].size.height) == (1334, 662), 'body fills the rest'
    assert editor._VIEW['title'].font_size == 30, 'title keeps native 30pt type'
    assert editor._VIEW['title'].position.y == 44, 'title is vertically centred in the 88-unit header'
    assert editor._VIEW['metrics']['header_h'] == 88
    assert editor._VIEW['gap'] == 0, 'non-MACHINE_FIX host keeps the native zero margin'
    assert len(editor._VIEW['tab_comps']) == len(editor._TABS), 'native common_tab.tab_common_1 cells'
    assert editor._VIEW['cta']._f7_kind == 'native_button', 'native confirm button'
    assert editor._VIEW['quality_buttons'][1]._f7_kind == 'native_check', 'native checkbox'
    assert editor._VIEW['mode_buttons']['add']._f7_kind == 'native_check', 'native checkbox'
    detail_w = editor._VIEW['metrics']['detail_w']
    detail_space = detail_w - 2 * editor._PAD
    cta = editor._VIEW['cta']
    # Sizes follow the panel, not a fixed design width: a 1024-unit-wide
    # tablet must not push the CTA or stepper past the detail edge.
    assert cta.size.height == 72, 'CTA keeps the native bar height'
    assert cta.size.width >= detail_space * 0.44, 'CTA keeps a usable width'
    assert cta.position.x + cta.size.width / 2 <= detail_w, 'CTA stays inside the detail panel'
    assert cta.position.y - cta.size.height / 2 >= 0, 'CTA keeps a bottom margin'
    pending = editor._VIEW['pending_button']
    assert pending.position.x + pending.size.width / 2 <= cta.position.x - cta.size.width / 2, \
        'pending and CTA share the action row without intersecting'
    assert pending.position.x - pending.size.width / 2 >= 0, 'pending stays inside the detail panel'
    minus = editor._VIEW['minus']
    plus = editor._VIEW['plus']
    for button in (minus, plus):
        assert button.size.height == 56, 'native stepper button keeps its bar height'
        assert button.size.width > 0
        assert button.position.x + button.size.width / 2 <= detail_w, \
            'stepper buttons stay inside the detail panel'
    assert editor._VIEW['query'].size.height >= 88, 'query is a native-height button'
    assert editor._VIEW['inventory_content'] is not None and editor._VIEW['pool_content'] is not None
    assert sorted(editor._VIEW['tab_labels']) == ['bulk', 'currency', 'item', 'pool', 'treasure'], \
        'left native tabs'
    assert editor._VIEW['tab_labels']['item'].text == u'\u7269\u54c1'
    assert editor._VIEW['tab_labels']['pool'].text == u'\u5361\u6c60\u5f00\u5173'

    # Single geometry table drives placement: every registered widget's live
    # position/size must equal the rect it was placed from.
    def assert_geometry_matches(label='after mount'):
        geo = editor._VIEW['geometry']
        widgets = editor._VIEW['geo_widgets']
        assert widgets, 'geometry registry is populated'
        for name, entry in widgets.items():
            node = entry['node']
            rect = entry['rect']
            ax, ay = entry['anchor']
            expect_x = rect['x'] + ax * rect['w']
            expect_y = rect['y'] + ay * rect['h']
            assert abs(node.position.x - expect_x) <= 1e-6, \
                '%s %s x: %r != %r' % (label, name, node.position.x, expect_x)
            assert abs(node.position.y - expect_y) <= 1e-6, \
                '%s %s y: %r != %r' % (label, name, node.position.y, expect_y)
            if entry['check_size']:
                assert abs(node.size.width - rect['w']) <= 1e-6, \
                    '%s %s width: %r != %r' % (label, name, node.size.width, rect['w'])
                assert abs(node.size.height - rect['h']) <= 1e-6, \
                    '%s %s height: %r != %r' % (label, name, node.size.height, rect['h'])
    assert_geometry_matches()
    geo = editor._VIEW['geometry']
    for name in ('nav', 'content', 'list', 'detail', 'pool', 'scroll',
                 'pool_scroll', 'list_header', 'detail_header', 'pool_header',
                 'list_search', 'list_query', 'detail_icon', 'cta', 'pending',
                 'mode:set', 'mode:add', 'quality:1', 'quality:5', 'minus',
                 'count', 'plus', 'tab:item', 'tab:pool'):
        assert name in editor._VIEW['geo_widgets'], 'geometry element %s' % name
    assert geo['content']['x'] == geo['nav_right'] == \
        geo['nav']['x'] + geo['nav']['w'], 'content starts at nav_right'
    # Tab cells are nav-column-local and laid out in two columns, so the
    # rightmost cell ends short of the column edge by the column gutter.
    assert geo['nav']['x'] + geo['tabs'][0]['x'] + geo['tabs'][0]['w'] < \
        geo['content']['x']
    for index, (group, caption) in enumerate(editor._TABS):
        cell = geo['tabs'][index]
        label = editor._VIEW['tab_labels'][group]
        label_w = len(caption) * editor._FONT_TAB
        # The tab node is anchored at its cell centre, so a label left at the
        # cell centre in node-local units doubles the offset (device r17:
        # cell centre 294 px, rendered text centre 454 px).
        assert label.position.x == cell['w'] / 2.0 and label.position.y == cell['h'] / 2.0, \
            'tab label %s sits at %r,%r in a %rx%r cell' % (
                group, label.position.x, label.position.y, cell['w'], cell['h'])
        assert (label.anchor.x, label.anchor.y) == (0.5, 0.5), \
            'tab label centred on its anchor'
        centre = geo['nav']['x'] + cell['x'] + cell['w'] / 2.0
        label_left = centre - label_w / 2.0
        label_right = centre + label_w / 2.0
        assert label_left >= geo['nav']['x'] + cell['x'], 'tab label left pad'
        assert label_right <= geo['nav']['x'] + cell['x'] + cell['w'], \
            'tab label stays inside the nav column'
    # Native checkbox art renders 49 units tall; a 32-unit band put the chip
    # row over 当前持有 on device.
    assert editor._CHECK_FOOTPRINT >= 49
    for name in ('mode', 'quality'):
        band = geo['detail_bands'][name]
        assert band['h'] >= editor._CHECK_FOOTPRINT, '%s band fits the chip art' % name
    for name in ('mode:set', 'mode:add', 'quality:1', 'quality:5'):
        rect = editor._VIEW['geo_widgets'][name]['rect']
        assert rect['h'] >= editor._CHECK_FOOTPRINT, '%s box fits the chip art' % name
    # Detail element rects (including chip label footprints) never overlap.
    elements = geo['detail_elements']
    for index, (name_a, first) in enumerate(elements):
        for name_b, second in elements[index + 1:]:
            overlap_x = (first['x'] < second['x'] + second['w'] and
                         second['x'] < first['x'] + first['w'])
            overlap_y = (first['y'] < second['y'] + second['h'] and
                         second['y'] < first['y'] + first['h'])
            assert not (overlap_x and overlap_y), \
                'detail elements intersect: %s / %s' % (name_a, name_b)

    # Every cloned native button must drive its csb title children, not just
    # setTitleText: the baked 取消 state is what r14 rendered.
    def assert_native_state(button, expected, check_visible=True):
        nml = button.getChildByName('text_nml')
        gry = button.getChildByName('text_gry')
        assert nml is not None and gry is not None, 'csb title state children kept'
        assert nml.text == expected, 'rendered title child says %r, want %r' % (nml.text, expected)
        assert gry.text == expected
        if check_visible:
            assert nml.visible is True and gry.visible is False, 'normal title state only'

    assert_native_state(editor._VIEW['query'], u'\u67e5\u8be2')
    assert_native_state(editor._VIEW['minus'], u'-')
    assert_native_state(editor._VIEW['plus'], u'+')
    assert_native_state(editor._VIEW['cta'], u'\u4fdd\u5b58\u6570\u91cf')
    assert_native_state(editor._VIEW['pending_button'], u'\u6838\u5bf9\u4e0a\u6b21\u64cd\u4f5c',
                        check_visible=False)
    assert_native_state(header.getChildByName('btn_close'), u'')
    pool_labels = set()
    def collect_buttons(node):
        if getattr(node, '_f7_kind', None) == 'native_button':
            pool_labels.add(node._f7_text)
            assert_native_state(node, node._f7_text)
        for child in node.getChildren():
            collect_buttons(child)
    collect_buttons(editor._VIEW['pool_content'])
    assert pool_labels == {u'\u641c\u7d22', u'\u5168\u90e8\u5173\u95ed',
                           u'< \u4e0a\u4e00\u9875', u'\u4e0b\u4e00\u9875 >'}, pool_labels
    assert editor._VIEW['mode_buttons']['set']._f7_label.text == u'\u8bbe\u4e3a'
    assert editor._VIEW['mode_buttons']['add']._f7_label.text == u'\u589e\u52a0'
    for index, mode in enumerate(('set', 'add')):
        chip = editor._VIEW['mode_buttons'][mode]
        box = geo['modes'][index]
        caption = geo['mode_labels'][index]
        assert caption['x'] >= box['x'] + box['w'], 'caption starts clear of the box'
        assert chip._f7_label.position.x == caption['x'], 'caption uses the panel rect'
        assert chip._f7_label.position.y == caption['y'] + caption['h'] / 2.0, \
            'caption sits on the band centre'
    assert geo['modes'][1]['x'] > geo['modes'][0]['x'] + geo['modes'][0]['w'], \
        'the two mode cells do not overlap'
    assert geo['mode_labels'][1]['x'] + geo['mode_labels'][1]['w'] <= \
        geo['detail']['w'] - 15.0, 'second caption stays in the panel'
    assert editor._VIEW['mode_buttons']['set']._f7_text == u'\u8bbe\u4e3a'
    for value, chip in editor._VIEW['quality_buttons'].items():
        assert chip._f7_label.text == u'%d' % value
    # Rows without a quality band raise the quantity group; the CTA stays put.
    tight = editor._VIEW['geometry_compact']
    assert tight['minus']['y'] > geo['minus']['y'], 'compact stack lifts the stepper'
    assert editor._VIEW['minus'].position.y == \
        tight['minus']['y'] + tight['minus']['h'] / 2.0, 'stepper follows the compact rect'
    assert editor._VIEW['cta'].position.y == \
        geo['cta']['y'] + geo['cta']['h'] / 2.0, 'CTA stays anchored'
    assert editor._VIEW['query']._f7_text == u'\u67e5\u8be2'
    assert u'\u53d6\u6d88' not in pool_labels, 'no native button keeps the baked csb string'

    # One-tap cells: bounded buttons laid out in columns above a status band
    # that owns its own height, so no cell ever sits on the status text.
    bulk_rows = geo['bulk_rows']
    bulk_status = geo['bulk_status']
    assert len(bulk_rows) == len(editor._BULK), 'one cell per one-tap action'
    assert len({round(row['w'], 6) for row in bulk_rows}) == 1, 'uniform cell width'
    assert len({round(row['h'], 6) for row in bulk_rows}) == 1, 'uniform cell height'
    cell_w = bulk_rows[0]['w']
    assert editor._BULK_MIN_W <= cell_w <= editor._BULK_MAX_W + 1e-6, \
        'cell width stays button-sized'
    per_row = 1
    if len(bulk_rows) > 1 and 2.0 * cell_w + 8.0 <= geo['bulk']['w']:
        per_row = 2
    assert len({round(row['y'], 6) for row in bulk_rows}) == \
        (len(bulk_rows) + per_row - 1) // per_row, 'cells share row baselines'
    for index, row in enumerate(bulk_rows):
        assert row['x'] >= 0 and row['x'] + row['w'] <= geo['bulk']['w'] + 1e-6, \
            'cell %d stays inside the bulk panel' % index
        assert row['y'] >= bulk_status['y'] + bulk_status['h'], \
            'cell %d clears the status band' % index
        assert row['h'] <= editor._BULK_MAX_H + 1e-6, 'cell %d stays button-height' % index

    # Labels centre on their own cell, so the pad is measured against the cell
    # width, not the whole column.
    for index, (group, caption) in enumerate(editor._TABS):
        label = editor._VIEW['tab_labels'][group]
        label_w = len(caption) * editor._FONT_TAB
        cell_w = geo['tabs'][index]['w']
        assert (label.anchor.x, label.anchor.y) == (0.5, 0.5), 'tab text centred anchor'
        assert (label.position.x, label.position.y) == (cell_w / 2.0, geo['tabs'][index]['h'] / 2.0), \
            'tab text sits on the cell node origin'
        assert cell_w / 2.0 - label_w / 2.0 >= 0.0, 'left pad survives'
        assert cell_w / 2.0 + label_w / 2.0 <= cell_w, \
            'right edge not clipped'
        assert label.font_size == editor._FONT_TAB
    first_tab = editor._VIEW['tab_fills']['item']
    assert (first_tab.position.y + editor._VIEW['metrics']['tab_h'] / 2.0 ==
            editor._VIEW['metrics']['body_h'] - editor._TAB_TOP_GAP), 'first tab clears the header'

    # Detail column: recorded rect table has no intersections and >=24 gaps.
    rects = editor._VIEW['detail_rects']
    assert len(rects) == 9, 'full detail stack recorded'
    ordered = sorted(rects, key=lambda rect: rect['y'])
    for lower, upper in zip(ordered, ordered[1:]):
        assert lower['y'] + lower['h'] <= upper['y'] - editor._STACK_GAP + 1e-6, \
            'detail rows keep a 24-unit gap'
    for index, first_rect in enumerate(rects):
        for second_rect in rects[index + 1:]:
            overlap_x = (first_rect['x'] < second_rect['x'] + second_rect['w'] and
                         second_rect['x'] < first_rect['x'] + first_rect['w'])
            overlap_y = (first_rect['y'] < second_rect['y'] + second_rect['h'] and
                         second_rect['y'] < first_rect['y'] + first_rect['h'])
            assert not (overlap_x and overlap_y), 'detail rects intersect: %r / %r' % (
                first_rect, second_rect)
    assert max(rect['y'] + rect['h'] for rect in rects) <= editor._VIEW['metrics']['panel_h'] - editor._SECTION_H

    assert editor._VIEW['body'] is overlay and editor._VIEW['card'] is not overlay
    fonts = []
    def walk_fonts(node):
        for child in node.getChildren():
            if isinstance(child, TextImpl) and getattr(child, 'font_size', 0):
                fonts.append(child.font_size)
            walk_fonts(child)
    walk_fonts(overlay)
    assert fonts and min(fonts) >= 24, 'every label uses a native design-unit size'
    fields = []
    def walk(node):
        for child in node.getChildren():
            if isinstance(child, TextFieldImpl):
                fields.append(child)
            walk(child)
    walk(overlay)
    assert len(fields) >= 3, 'inventory search/quantity and pool search fields'
    assert editor._VIEW['count'].getString() == '1', 'quantity has a real editable default'
    assert editor._VIEW['quality_value'] == 1 and len(editor._VIEW['quality_buttons']) == 5, 'treasure grades 1..5 chips'
    assert len(editor._VIEW['mode_buttons']) == 2, 'set/add mode chips'
    assert all(field.font == '' for field in fields), 'values must not be passed as font names'
    assert editor._VIEW['pool_content'].visible is False, 'pool tab is built but hidden until chosen'
    editor._reply_catalog(gg.avatar, True, [], 0, editor._VIEW.get('catalog_nonce'), 'item', '')
    old_row = {'k': 'item', 'i': 1, 'name': 'OLD', 'n': 3}
    current_row = {'k': 'item', 'i': 1, 'name': 'CURRENT', 'n': 23}
    editor._VIEW['rows'] = [current_row]
    editor._render_rows()
    current_token = (editor._VIEW.get('ui_epoch'), editor._VIEW.get('catalog_generation'))
    editor._select_row(old_row, current_token)
    assert editor._VIEW['selected']['n'] == 23 and editor._VIEW['count'].getString() == '23', 'canonical current row wins over stale row object'
    editor._select_row(old_row, pre_reopen_token)
    assert editor._VIEW['selected']['n'] == 23, 'old panel listener cannot reseed qty3'
    editor._VIEW['rows'] = [old_row]
    editor._render_rows()
    old_generation = editor._VIEW['catalog_generation']
    old_catalog_nonce = editor._VIEW.get('catalog_nonce')
    editor._request_catalog(False)
    editor._VIEW['catalog_nonce'] = 'c' * 32
    current_catalog_nonce = editor._VIEW.get('catalog_nonce')
    editor._reply_catalog(gg.avatar, True, [old_row], 0, old_catalog_nonce, 'item', '')
    assert editor._VIEW['rows'] == [] and editor._VIEW['selected'] is None, 'old op catalog response rejected'
    editor._reply_catalog(gg.avatar, True, [], 0, current_catalog_nonce, 'item', '')
    before_retry = len(calls)
    editor._request_catalog(False)
    editor._request_catalog(False)
    assert len(calls) == before_retry + 2, 'explicit query retry sends new request despite lost reply'
    editor._reply_catalog(gg.avatar, True, [], 0, editor._VIEW.get('catalog_nonce'), 'item', '')
    before_old_apply = len(calls)
    editor._select_row(old_row, old_generation)
    assert editor._VIEW['selected'] is None, 'old row callback ignored after new query'
    editor._apply('set')
    assert len(calls) == before_old_apply, 'old row apply blocked while loading'
    editor._reply_catalog(gg.avatar, False, [], 0, editor._VIEW.get('catalog_nonce'), 'item', '')
    editor._VIEW['group'] = 'currency'
    editor._request_catalog(False)
    before_switch_apply = len(calls)
    editor._select_row(old_row, old_generation)
    editor._apply('set')
    assert len(calls) == before_switch_apply, 'old item row apply blocked after category switch'
    editor._reply_catalog(gg.avatar, True, [], 0, editor._VIEW.get('catalog_nonce'), 'currency', '')
    rows = [{'k': 'item', 'i': 1, 'name': 'A', 'n': 3},
            {'k': 'item', 'i': 2, 'name': 'B', 'n': 4}]
    editor._VIEW['catalog_query'] = ''
    editor._VIEW['group'] = 'item'
    editor._VIEW['rows'] = rows
    editor._render_rows()
    editor._select_row(rows[0])
    assert editor._VIEW['count'].getString() == '3', 'new row in set mode seeds current amount'
    # The quantity field asks the stock input view; its result is filtered and
    # clamped. (The TextField's own IME attach did nothing on device.)
    count = editor._VIEW['count']
    box = count._f7_box

    def open_input():
        box.listener(box, CCUI.TOUCH_EVENT_ENDED)

    del prompts[:]
    open_input()
    assert prompts, 'tapping the box opens the stock input view'
    prompts[-1](u'12abc')
    assert count.getString() == u'12', 'typed quantity keeps digits only'
    open_input()
    prompts[-1](u'')
    assert count.getString() == u'0', 'empty typed quantity clamps to zero'
    open_input()
    prompts[-1](u'1000001')
    assert count.getString() == u'1000000', 'typed quantity clamps to the API range'
    # Holding a stepper repeats and accelerates; the release adds nothing more.
    count.setString(u'0')
    del scheduled[:]
    plus = editor._VIEW['plus']
    plus.listener(plus, CCUI.TOUCH_EVENT_BEGAN)
    assert scheduled, 'hold arms the first repeat'
    for _ in range(3):
        delay, tick = scheduled.pop(0)
        tick()
    held = int(count.getString())
    assert held == 3, 'held stepper repeats once per tick'
    plus.listener(plus, CCUI.TOUCH_EVENT_ENDED)
    assert editor._VIEW['hold_active'] is False, 'release stops the repeat'
    plus.listener(plus, CCUI.TOUCH_EVENT_ENDED)
    assert int(count.getString()) == held, 'release after a hold does not add one more'
    count.setString(u'5')
    plus.listener(plus, CCUI.TOUCH_EVENT_BEGAN)
    del scheduled[:]
    plus.listener(plus, CCUI.TOUCH_EVENT_ENDED)
    assert int(count.getString()) == 6, 'a quick tap inside the delay bumps once'
    plus.listener(plus, CCUI.TOUCH_EVENT_BEGAN)
    plus.listener(plus, CCUI.TOUCH_EVENT_ENDED)
    assert int(count.getString()) == 7, 'the next tap bumps once more'
    editor._set_mode('add')
    assert editor._VIEW['count'].getString() == '1', 'mode change add seeds 1'
    editor._VIEW['count'].setString('9')
    editor._set_mode('add')
    assert editor._VIEW['count'].getString() == '9', 'same mode click keeps user amount'
    editor._set_mode('set')
    assert editor._VIEW['count'].getString() == '3', 'mode change set seeds current amount'
    editor._select_row(rows[1])
    assert editor._VIEW['count'].getString() == '4', 'new selected row in set mode seeds current amount'
    editor._select_row(rows[0])
    editor._VIEW['count'].setString('7')
    assert editor._VIEW['detail_icon'].textures[-1] == 'cocos/image/item/common/10005.png', 'full inventory uses original common icon without wallet remap'
    first_icon = editor._VIEW['detail_icon']
    editor._detail_icon(rows[1])
    assert editor._VIEW['detail_icon'] is not first_icon, 'new item gets fresh image instead of a stale native texture'
    assert editor._VIEW['detail_icon'].textures[-1] == 'cocos/image/item/common/1001.png'
    assert editor._VIEW['detail_icon'].ignore_adapt is False, 'icon respects explicit detail size'
    editor._detail_icon({'k': 'item', 'i': 999999})
    assert editor._VIEW['detail_icon'].visible is False, 'missing metadata hides image instead of inventing an icon'
    editor._detail_icon(rows[0])
    editor._reply_catalog(gg.avatar, True, rows[:1], 0, editor._VIEW.get('catalog_nonce'), 'item', '')
    scroll = editor._VIEW['scroll']
    first_row = scroll.children[0]
    assert first_row.position.y + first_row.size.height == scroll.size.height, 'single result sits at the top of the viewport'
    geo = editor._VIEW['geometry']
    assert geo['scroll_container_h'] == scroll.size.height
    assert geo['rows'][0]['y'] + geo['rows'][0]['h'] == geo['scroll_container_h']
    assert scroll.percent == 0, 'scroll starts at the top offset so row 1 is fully visible'
    assert_geometry_matches('single row')
    assert first_row._f7_native is True, 'row is a native common_frame.item cell'
    assert first_row.size.height == 88, 'native row rhythm'
    assert first_row.size.width == editor._VIEW['metrics']['list_w'], 'cell spans the list width'
    assert first_row._f7_width == editor._VIEW['metrics']['list_w']
    assert first_row._f7_info is not None
    assert first_row._f7_info.size.width + editor._PAD * 2 + editor._ICON + 8 == first_row.size.width, \
        'info strip derives from the forced cell width'
    assert first_row._f7_selected is True and first_row._f7_comp['sel'].visible is True, 'native selection node marks the chosen row'
    assert first_row._f7_name_label.text == 'A', 'item name is rendered inside the native info strip'
    assert first_row._f7_name_label.font_size >= 24
    assert first_row._f7_meta_label.text == u'\u7f16\u53f7 1', 'item id meta line'
    assert first_row._f7_meta_label.font_size >= 24
    assert first_row._f7_count_label.text == '3', 'count is right-aligned in the cell info strip'
    assert first_row._f7_count_label.font_size >= 24
    count_right = first_row._f7_info.position.x + first_row._f7_count_label.position.x
    assert count_right <= first_row.size.width - editor._PAD, \
        'count stays inside the cell padding (right %r, cell %r)' % (count_right, first_row.size.width)
    assert editor._icon_path({'k': 'item', 'i': 1}) == 'cocos/image/item/common/10005.png', 'item rows use the item family'
    assert editor._icon_path({'k': 'treasure', 'i': 2}) == 'cocos/image/item/common/1001.png', 'treasure art follows treasure_frame.py'
    assert editor._icon_path({'k': 'hero', 'i': 7}) == 'cocos/image/hero/common_frame/7.png', 'hero rows use the hero family'
    editor._VIEW['rows'] = [rows[0], {'k': 'treasure', 'i': 2, 'name': 'T', 'n': 1}]
    editor._render_rows()
    visible_rows = [node for node in editor._VIEW['scroll'].children
                    if node.isVisible()]
    assert len(visible_rows) == 1, '物品 tab never renders treasure rows'
    # Selection repaints in place: the pool keeps its nodes and every other row
    # stays visible. Device r19 destroyed the pool and left one highlighted row
    # behind an empty list.
    saved_count = editor._VIEW['count'].getString()
    editor._VIEW['rows'] = rows
    editor._render_rows()
    editor._VIEW['selected_key'] = None
    pool_before = list(editor._VIEW['row_pool'])
    editor._select_row(rows[0])
    assert editor._VIEW['row_pool'] == pool_before, 'selection reuses row nodes'
    shown = [node for node in editor._VIEW['scroll'].children
             if node.isVisible()]
    assert len(shown) == len(rows), 'selection keeps every row visible'
    assert editor._VIEW['row_pool'][0]._f7_selected is True
    assert editor._VIEW['row_pool'][1]._f7_selected is False, \
        'the previously chosen row loses its highlight without a rebuild'
    editor._VIEW['count'].setString(saved_count)
    editor._VIEW['rows'] = rows
    editor._render_rows()
    editor._VIEW['rows'] = rows
    editor._render_rows()
    short_geo = editor._VIEW['geometry']
    assert short_geo['scroll_container_h'] == short_geo['scroll']['h'], \
        'short list fills the viewport, not a taller container'
    for rect in short_geo['rows']:
        assert rect['y'] >= short_geo['scroll_container_h'] - short_geo['scroll']['h']
        assert rect['y'] + rect['h'] <= short_geo['scroll_container_h']
    many = [dict(rows[0], i=index + 1) for index in range(40)]
    editor._VIEW['rows'] = many
    editor._render_rows()
    tall_geo = editor._VIEW['geometry']
    assert tall_geo['scroll_container_h'] == 40 * editor._ROW_H
    assert tall_geo['rows'][0]['y'] + tall_geo['rows'][0]['h'] == \
        tall_geo['scroll_container_h'], 'row 1 is flush with the container top'
    assert tall_geo['rows'][0]['y'] >= \
        tall_geo['scroll_container_h'] - tall_geo['scroll']['h'], \
        'row 1 is fully inside the viewport'
    for rect in tall_geo['rows']:
        assert rect['x'] >= 0 and rect['x'] + rect['w'] <= tall_geo['scroll']['w']
        assert rect['y'] >= 0 and rect['y'] + rect['h'] <= tall_geo['scroll_container_h']
    assert_geometry_matches('tall list')
    editor._VIEW['rows'] = rows
    editor._render_rows()
    assert editor._row_key(editor._VIEW['selected']) == ('item', 1), 'selection survives successful refresh'
    assert editor._VIEW['count'].getString() == '7', 'user amount survives selected refresh'
    editor._request_catalog(True)
    assert calls[-1][1].get('o') == 0, 'first page asks offset 0'
    editor._VIEW['catalog_more'] = True
    editor._catalog_page_step(1)
    assert calls[-1][0] == 'q7InventoryCatalogAsk'
    assert calls[-1][1].get('o') == editor._CATALOG_PAGE, 'page 2 asks offset == page size'
    editor._VIEW['catalog_page'] = 0
    editor._VIEW['catalog_more'] = False
    editor._request_catalog(True)
    refreshed = [dict(rows[0], n=24), rows[1]]
    editor._reply_catalog(gg.avatar, True, refreshed, 0, editor._VIEW.get('catalog_nonce'), 'item', '')
    assert editor._VIEW['selected_token'] == (editor._VIEW['ui_epoch'], editor._VIEW['catalog_generation'])
    editor._VIEW['count'].setString('25')
    repeated_sends = []
    original_send = editor._send
    editor._send = repeated_sends.append
    editor._apply('set')
    editor._send = original_send
    assert repeated_sends == [[{'k': 'item', 'i': 1, 'm': 'set', 'n': 25}]], 'refreshed selection can submit again without reselecting'

    editor._request_catalog(False)
    assert editor._VIEW['selected'] is None, 'new query clears selection'

    # 卡池开关: lazy paged list, 12-pool cap, pending lock, close-all, search.
    before_pool_rpc = len(calls)
    pool_slot = editor._VIEW['tab_fills']['pool']
    pool_slot.listener(pool_slot, CCUI.TOUCH_EVENT_ENDED)
    assert editor._VIEW['group'] == 'pool'
    assert editor._VIEW['inventory_content'].visible is False
    assert editor._VIEW['pool_content'].visible is True
    assert len(calls) == before_pool_rpc, 'pool tab sends no inventory catalog request'
    pool_scroll = editor._VIEW['pool_scroll']
    assert editor._POOL_PAGE <= 60
    assert len(pool_scroll.children) == editor._POOL_PAGE, 'page one only, never 440 rows'
    pool_geo = editor._VIEW['geometry']
    assert len(pool_geo['pool_rows']) == editor._POOL_PAGE
    assert pool_geo['pool_container_h'] == editor._POOL_PAGE * editor._ROW_H
    for rect in pool_geo['pool_rows']:
        assert rect['x'] >= 0 and rect['x'] + rect['w'] <= pool_geo['pool_scroll']['w']
        assert rect['y'] >= 0 and rect['y'] + rect['h'] <= pool_geo['pool_container_h']
    assert_geometry_matches('pool rows')
    pool_chip = pool_scroll.children[0].getChildByName('pool_switch_iphonex_right')
    assert pool_chip is not None and pool_chip.size.width >= 44, 'native toggle chip is touch-sized'
    assert editor._VIEW['pool_header'].text == u'\u5361\u6c60\u5f00\u5173  \u5df2\u5f00\u542f 0/12'
    assert editor._VIEW['pool_page_label'].text == '1/22'
    editor._pool_toggle(2)
    assert pool_api.ids == [2], 'toggle writes through draw_ui set_selection'
    assert editor._VIEW['pool_header'].text.endswith(u'1/12')
    assert editor._VIEW['pool_status'].text == u'\u4fee\u6539\u540e\u91cd\u65b0\u8fdb\u5165\u767d\u591c\u9986\u751f\u6548'
    pool_api.ids = list(range(1, 13))
    editor._pool_refresh_header()
    editor._render_pool_rows()
    writes = len(pool_api.calls)
    editor._pool_toggle(20)
    assert len(pool_api.calls) == writes, 'a 13th pool is refused before writing'
    assert editor._VIEW['pool_status'].text == u'\u6700\u591a\u540c\u65f6\u5f00\u542f 12 \u4e2a\u5361\u6c60'
    gg.avatar.luckyDrawData = types.SimpleNamespace(getIsOpenCard=lambda t: t == 7)
    pool_api.ids = [2]
    editor._render_pool_rows()
    editor._pool_toggle(7)
    assert len(pool_api.calls) == writes, 'a started draw cannot be hidden'
    assert u'\u8fdb\u884c\u4e2d' in editor._VIEW['pool_status'].text
    pool_api.ready = frozenset([7, 100])
    editor._render_pool_tab()
    pool_texts = []
    def collect_pool(node):
        for child in node.getChildren():
            if isinstance(child, TextImpl) and getattr(child, 'text', None):
                pool_texts.append(child.text)
            collect_pool(child)
    collect_pool(pool_scroll)
    assert u'\u8fdb\u884c\u4e2d' in pool_texts, 'pending pool row carries the running tag'
    assert editor._VIEW['pool_page_label'].text == '1/1'
    pool_api.ids = [2, 7]
    editor._pool_close_all()
    assert pool_api.ids == [7], 'close-all keeps the started draw'
    assert editor._VIEW['pool_header'].text.endswith(u'1/12')
    pool_api.ready = frozenset(pools)
    editor._render_pool_tab()
    assert len(editor._VIEW['pool_all']) == 440
    editor._pool_page_step(1)
    assert editor._VIEW['pool_page'] == 1 and editor._VIEW['pool_page_label'].text == '2/22'
    assert len(pool_scroll.children) == editor._POOL_PAGE
    editor._VIEW['pool_search'].setString(u'pool 1')
    editor._pool_apply_search()
    assert editor._VIEW['pool_page'] == 0
    assert 0 < len(editor._VIEW['pool_filtered']) < 440
    editor._VIEW['pool_search'].setString('')
    editor._pool_apply_search()
    assert len(editor._VIEW['pool_filtered']) == 440
    all_texts = []
    def collect_all(node):
        for child in node.getChildren():
            if isinstance(child, TextImpl) and getattr(child, 'text', None):
                all_texts.append(child.text)
            collect_all(child)
    collect_all(overlay)
    assert u'\u4fee\u6539\u540e\u91cd\u65b0\u8fdb\u5165\u767d\u591c\u9986\u751f\u6548' in all_texts
    # Every emitted character must exist in hkytw5: ASCII, CJK unified, CJK
    # punctuation or full-width forms. U+2713/U+2212/U+25BC are absent from the
    # shipped font and used to render as fallback boxes.
    for text in all_texts:
        for char in text:
            point = ord(char)
            assert (point < 128 or 0x3000 <= point <= 0x9fff or
                    0xff00 <= point <= 0xffef), 'missing hkytw5 glyph: %r' % char
    source = open(MODULE).read()
    assert u'\\u2713' not in source and u'\\u2212' not in source, 'no missing-glyph marks'

    # 快捷: one-tap grants ride the existing edit RPC as bulk/cg rows.
    editor._show_group('bulk')
    assert editor._VIEW['bulk_content'].isVisible() is True, 'bulk panel shown'
    bulk_geo = editor._VIEW['geometry']
    assert len(bulk_geo['bulk_rows']) == len(editor._BULK), 'one row per quick action'
    for rect in bulk_geo['bulk_rows']:
        assert rect['y'] >= 0 and rect['y'] + rect['h'] <= bulk_geo['bulk']['h'] - \
            editor._SECTION_H, 'quick rows stay inside the panel'
    assert editor._VIEW['inventory_content'].isVisible() is False
    assert editor._VIEW['pool_content'].isVisible() is False
    before_bulk = len(calls)
    editor._bulk_run('letters')
    assert calls[before_bulk][0] == 'q7InventoryEditAsk', 'bulk reuses the edit RPC'
    batch = calls[before_bulk][1]['batch']
    assert batch == [{'k': 'bulk', 'm': 'letters'}], 'one bulk row per class'
    assert len(calls[before_bulk][1]['op']) == 32
    pending = editor._load_pending()
    assert pending and pending['op'] == calls[before_bulk][1]['op']
    editor._reply_edit(gg.avatar, True, 0, pending['op'])
    assert u'\u5df2\u5b8c\u6210' in editor._VIEW['bulk_status'].text, \
        'successful edit reports the one-tap result'
    assert editor._load_pending() is None
    before_cg = len(calls)
    editor._bulk_run('cg')
    cg_batch = calls[before_cg][1]['batch']
    assert calls[before_cg][0] == 'q7InventoryEditAsk'
    assert [row['i'] for row in cg_batch] == [1, 2, 3], 'every client CG id is sent'
    assert {row['k'] for row in cg_batch} == {'cg'}
    pending = editor._load_pending()
    editor._reply_edit(gg.avatar, True, 0, pending['op'])
    # A 465-row one-tap pending must parse (not 'corrupt') and then be dropped.
    editor._save_pending('c' * 32, [{'k': 'cg', 'i': 500 + i, 'm': 'add'}
                                    for i in range(465)], editor._identity())
    assert editor._pending_state(editor._identity())[0] == 'valid', 'bulk pending parses'
    before_big = len(calls)
    editor._bulk_run('letters')
    assert calls[before_big][0] == 'q7InventoryEditAsk', 'large bulk pending is dropped'
    editor._reply_edit(gg.avatar, True, 0, calls[before_big][1]['op'])
    # A one-tap op that lost its reply must not block the next grant.
    editor._save_pending('b' * 32, [{'k': 'cg', 'i': 9, 'm': 'add'}], editor._identity())
    before_retry = len(calls)
    editor._bulk_run('letters')
    assert calls[before_retry][0] == 'q7InventoryEditAsk', 'bulk grant supersedes a bulk pending'
    assert editor._load_pending()['op'] == calls[before_retry][1]['op']
    editor._reply_edit(gg.avatar, True, 0, calls[before_retry][1]['op'])
    assert editor._VIEW['bulk_queue'] == [], 'the CG queue drains'
    assert u'\u5df2\u5b8c\u6210' in editor._VIEW['bulk_status'].text
    # The chunked driver unlocks before the next chunk (a held lock drops it).
    assert ('unlock', editor._LOCK) in locks, 'each chunk releases the UI lock'
    editor._show_group('item')
    assert editor._VIEW['bulk_content'].isVisible() is False
    editor._close()

    # No comp pack and no readable csb: the drawn fallback must not raise into
    # the UI thread and must still use native design-unit font sizes.
    saved_comps = ui.comps
    saved_ccs = cocosui.ccs
    ui.comps = None
    class MissingReader(object):
        @classmethod
        def getInstance(cls):
            return cls()
        def widgetFromBinaryFile(self, path, *args):
            raise RuntimeError('no csb: %s' % path)
    cocosui.ccs = types.SimpleNamespace(GUIReader=MissingReader)
    editor._mount(late_panel)
    fallback_overlay = ui._root.children[-1]
    assert editor._VIEW['native_skin'] is False, 'missing csb pack takes the drawn path'
    assert editor._VIEW['header_native'] is False and editor._VIEW['tab_comps'] == {}
    assert editor._VIEW['header'].size.height == 88, 'drawn header keeps the native height'
    assert editor._VIEW['gap'] == 0
    assert getattr(editor._VIEW['cta'], '_f7_kind', None) is None
    assert editor._VIEW['minus'].size.width >= 88 and editor._VIEW['minus'].size.height >= 56
    assert editor._VIEW['query'].size.height >= 88
    fallback_fonts = []
    def walk_fallback(node):
        for child in node.getChildren():
            if isinstance(child, TextImpl) and getattr(child, 'font_size', 0):
                fallback_fonts.append(child.font_size)
            walk_fallback(child)
    walk_fallback(fallback_overlay)
    assert fallback_fonts and min(fallback_fonts) >= 24, 'fallback text stays native size'
    editor._VIEW['rows'] = rows
    editor._render_rows()
    fallback_row = editor._VIEW['scroll'].children[0]
    assert getattr(fallback_row, '_f7_native', False) is False
    assert fallback_row.size.height == 88, 'fallback row keeps native rhythm'
    editor._close()
    ui.comps = saved_comps
    cocosui.ccs = saved_ccs

    # Cutout margins: * _iphonex_left/right + IPHONEX_FIX_GAP + MACHINE_FIX.
    def cutout_probe():
        node = NodeImpl()
        left_node = LayoutImpl()
        left_node.setName('nav_iphonex_left')
        right_node = LayoutImpl()
        right_node.setName('content_iphonex_right')
        node.addChild(left_node)
        node.addChild(right_node)
        return node, left_node, right_node
    probe, left_node, right_node = cutout_probe()
    model['name'] = 'desktop'
    editor._apply_iphonex(probe)
    assert left_node.getLayoutParameter().getMargin().left == 0
    assert right_node.getLayoutParameter().getMargin().right == 0
    assert left_node.getName() == 'nav' and right_node.getName() == 'content'
    probe, left_node, right_node = cutout_probe()
    model['name'] = 'fake_full_screen_phone'
    editor._apply_iphonex(probe)
    assert left_node.getLayoutParameter().getMargin().left == 88, 'IPHONEX_FIX_GAP on the left margin'
    assert right_node.getLayoutParameter().getMargin().right == 88, 'IPHONEX_FIX_GAP on the right margin'
    assert left_node.getName() == 'nav' and right_node.getName() == 'content'
    model['name'] = 'desktop'

    source = open(MODULE).read()
    assert 'min(w / 1334.0' not in source and '84 * scale' not in source, 'no double scaling / ad-hoc 84 inset'
    assert '_FONT_BODY = 24' in source, 'native typography floor'
    del calls[:]
    # Fallback must use the proven gg.exec_delay API, not an invented defer.
    original_rpc = editor._install_rpc
    fallback_calls = []
    def flaky_rpc():
        fallback_calls.append('rpc')
        if len(fallback_calls) == 1:
            raise RuntimeError('first install seam')
        return original_rpc()
    editor._install_rpc = flaky_rpc
    editor.install()
    assert scheduled and scheduled[-1][0] == 1000
    scheduled[-1][1]()
    assert len(fallback_calls) == 2, 'exec_delay retries the failed install branch'
    editor._install_rpc = original_rpc
    assert getattr(ClientAvatar, 'q7InventoryEditReply') is not None
    assert getattr(ClientAvatar, 'q7InventoryCatalogReply') is not None
    assert set(('q7InventoryEditReply', 'q7InventoryCatalogReply')).issubset(
        set(ClientAvatar.__dict__))
    assert set(('q7InventoryEditReply', 'q7InventoryCatalogReply')).issubset(
        set(registered))

    # Loader binding must not install before the mature clean(True) succeeds.
    bind_calls = []
    original_install = editor.install
    editor.install = lambda: bind_calls.append('install')
    editor._VIEW['pool_api'] = None
    class FakePatch(object):
        def __init__(self): self.clean = lambda state: state
    fake_patch = FakePatch()
    editor.bind_startup(fake_patch, types.SimpleNamespace(live=lambda: True, draw_ui=pool_api))
    assert bind_calls == [], 'bind must not touch gg/avatar before clean'
    assert editor._VIEW['pool_api'] is None, 'policy is not read before clean'
    fake_patch.clean(False)
    assert bind_calls == [], 'non-state clean does not install'
    fake_patch.clean(True)
    assert bind_calls == ['install'], 'successful clean activates editor'
    assert editor._VIEW['pool_api'] is pool_api, 'editor uses draw_ui selection store'
    fake_patch.clean(True)
    assert bind_calls == ['install', 'install'], 'reclean re-runs idempotent install'
    editor.install = original_install

    editor._VIEW['status'] = Label()
    Avatar.uid = 999
    Avatar.account = ''
    assert editor._identity() == '', 'account-less avatar must not fall back to uid'
    Avatar.account = 'host-account'
    editor._VIEW['active'] = True
    editor._send([{'k': 'item', 'i': 1, 'm': 'add', 'n': 1}])
    assert len(calls) == 1 and calls[0][0] == 'q7InventoryEditAsk'
    pending = editor._load_pending()
    assert pending and pending['op'] == 'a' * 32
    first_op = pending['op']
    editor._send([{'k': 'item', 'i': 1, 'm': 'add', 'n': 1}])
    assert len(calls) == 1, 'pending operation must not be overwritten by a new op'
    editor._reply_edit(gg.avatar, False, 7, 'b' * 32)
    assert editor._load_pending()['op'] == first_op, 'stale typed reply ignored'
    editor._reply_edit(gg.avatar, True, 0, first_op)
    assert editor._load_pending() is None
    assert calls[-1][0] == 'q7InventoryCatalogAsk'

    editor._send([{'k': 'item', 'i': 1, 'm': 'add', 'n': 1}])
    saved = editor._load_pending()
    assert saved is not None
    Avatar.account = 'other-account'
    before = len(calls)
    editor._retry_pending()
    assert len(calls) == before, 'pending operation is account-bound'
    Avatar.account = 'host-account'
    editor._retry_pending()
    assert len(calls) == before + 1, 'same account retries the same op'
    assert calls[-1][1] == {'op': saved['op'], 'batch': saved['batch']}
    pending_path = editor._pending_path(editor._identity())
    with open(pending_path, 'wb') as stream:
        stream.write(b'{broken')
    before_corrupt = len(calls)
    editor._send([{'k': 'item', 'i': 1, 'm': 'add', 'n': 1}])
    assert len(calls) == before_corrupt, 'corrupt pending blocks a new op'
    with open(pending_path, 'rb') as stream:
        assert stream.read() == b'{broken', 'corrupt pending is not overwritten'

    assert_layout_matrix(editor)
    try:
        os.unlink(pending_path)
    except OSError:
        pass
    print('PASS inventory editor UI host: BBS entry, typed handlers, pending op persistence, account binding, no overwrite')
    print(calls_dir)

def assert_layout_matrix(editor):
    """One layout for every real viewport: nothing may leave its panel.

    The editor ships a single geometry function, so a device with a different
    design size (iPad 4:3, 1024-unit tablets, foldables, even a portrait
    window) must still contain every widget. Fixed design-unit widths used to
    push the quality chips and the stepper past the detail edge.
    """
    cases = (
        ('Pixel 6a', 1666.67, 750.0, 88.0),
        ('iPhone 15 Pro', 1680.0, 780.0, 88.0),
        ('iPad 4:3 landscape', 1333.33, 1000.0, 0.0),
        ('Nexus 7', 1280.0, 800.0, 0.0),
        ('small phone', 1280.0, 750.0, 0.0),
        ('tablet wide', 2048.0, 1536.0, 0.0),
        ('fold open', 1768.0, 828.0, 88.0),
        ('legacy 16:10', 1200.0, 750.0, 0.0),
        ('tiny 4:3', 1024.0, 768.0, 0.0),
        ('portrait phone', 750.0, 1666.0, 0.0),
    )

    def overlap(first, second):
        return (first['x'] < second['x'] + second['w'] and
                second['x'] < first['x'] + first['w'] and
                first['y'] < second['y'] + second['h'] and
                second['y'] < first['y'] + first['h'])

    for label, width, height, gap in cases:
        geo = editor._editor_geometry(width, height, gap, 50, 12)
        detail, listing, content = geo['detail'], geo['list'], geo['content']
        # Nav cells are column-local and laid out in two columns, so the first
        # cell starts after the column gutter rather than flush at x=0.
        assert geo['nav']['x'] == gap, '%s: nav starts after the gap' % label
        assert geo['tabs'][0]['x'] > 0.0, '%s: tab cells are column-local' % label
        assert geo['nav']['x'] + geo['nav']['w'] == geo['content']['x'], \
            '%s: tabs and content meet at nav_right' % label
        for index, (group, caption) in enumerate(editor._TABS):
            cell = geo['tabs'][index]
            centre = geo['nav']['x'] + cell['x'] + cell['w'] / 2.0
            half = len(caption) * editor._FONT_TAB / 2.0
            assert centre - half >= geo['nav']['x'] + cell['x'] - 1e-6, \
                '%s %s: label leaves the column on the left' % (label, group)
            assert centre + half <= geo['nav']['x'] + cell['x'] + cell['w'] + 1e-6, \
                '%s %s: label leaves the column on the right' % (label, group)
        for name in ('detail_icon', 'detail_name', 'minus', 'count', 'plus',
                     'cta', 'pending', 'held_label', 'held_value'):
            rect = geo[name]
            assert rect['x'] >= -1e-6, '%s %s: negative x' % (label, name)
            assert rect['x'] + rect['w'] <= detail['w'] - editor._PAD + 1e-6, \
                '%s %s: leaves the detail panel' % (label, name)
        for index, rect in enumerate(geo['modes'] + geo['quality']):
            assert rect['x'] + rect['w'] <= detail['w'] - editor._PAD + 1e-6, \
                '%s chip %d: leaves the detail panel' % (label, index)
        for name in ('list_search', 'list_query'):
            rect = geo[name]
            assert rect['x'] + rect['w'] <= listing['w'] + 1e-6, \
                '%s %s: leaves the list panel' % (label, name)
        for name in ('pool_search', 'pool_search_button', 'pool_close',
                     'pool_status', 'pool_note', 'pool_next', 'pool_prev'):
            rect = geo[name]
            assert rect['x'] + rect['w'] <= content['w'] + 1e-6, \
                '%s %s: leaves the content panel' % (label, name)
        elements = geo['detail_elements']
        for index, (name_a, first) in enumerate(elements):
            for name_b, second in elements[index + 1:]:
                assert not overlap(first, second), \
                    '%s detail elements intersect: %s / %s' % (label, name_a, name_b)
        for name, rect in geo['detail_bands'].items():
            assert rect['y'] >= -1e-6, '%s band %s: below the panel' % (label, name)
            assert rect['y'] + rect['h'] <= detail['h'] - editor._SECTION_H + 1e-6, \
                '%s band %s: crosses the section strip' % (label, name)


if __name__ == '__main__':
    main()
