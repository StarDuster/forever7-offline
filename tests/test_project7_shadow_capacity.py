"""Original 640 consumer host/static checks for the offline shadow-capacity projection.

Only finite original method bodies execute: InvData.__init__/checkBagFull/
isFullByIDs, InvMember.checkUnlinkTreasureFull, bbs_home.notify_hero_show and
treasure_treasurelist.refresh/on_load boundaries. UI nodes, GridScrollView and
gg are synthetic. No NeoX, Python2 opcode, D8, APK, native or device execution.
"""
import _paths  # noqa: E402,F401
from pathlib import Path
import copy
import importlib.util
import json
import sys
import textwrap
import types
import unittest
import warnings

from lib2to3.refactor import RefactoringTool

ROOT = Path(__file__).resolve().parents[1]
POLICY = (ROOT / 'offline/current/data/project7_shadow_capacity/policy.json').read_text('ascii')
TARGET = json.loads((ROOT / 'offline/current/data/project7_catalog/target-manifest.json').read_text())
ITEM_CATALOG = json.loads((ROOT / 'analysis/catalogs/item_data.json').read_text())
ITEMS = dict((int(key), value) for key, value in ITEM_CATALOG['data']['items'])
HERO_TREASURE = json.loads((ROOT / 'analysis/catalogs/hero_treasure.json').read_text())


def _unbox(value):
    if isinstance(value, dict) and value.get('$f7type') == 'tuple':
        return value['items']
    return value


HT_ROWS = dict((tuple(_unbox(key)), value) for key, value in HERO_TREASURE['data']['items'])
TARGET_IDS = [row['id'] for row in TARGET['treasures']]
TARGET_SET = frozenset(TARGET_IDS)
SUBBAG = dict((template, ITEMS[template]['subbag']) for template in TARGET_IDS)
FIX = RefactoringTool(['lib2to3.fixes.fix_print', 'lib2to3.fixes.fix_except',
                       'lib2to3.fixes.fix_dict', 'lib2to3.fixes.fix_xrange',
                       'lib2to3.fixes.fix_filter'])
NS = types.SimpleNamespace


def original(relative, name, namespace, indent=4):
    path = ROOT / 'analysis/original-py-640' / relative
    lines = path.read_text().splitlines(True)
    prefix = ' ' * indent
    start = next(i for i, line in enumerate(lines) if line.startswith(prefix + 'def ' + name + '('))
    end = next((i for i in range(start + 1, len(lines))
                if lines[i].strip() and not lines[i].startswith(prefix + ' ')
                and not lines[i].startswith('\n')), len(lines))
    source = textwrap.dedent(''.join(lines[start:end]))
    with warnings.catch_warnings():
        warnings.simplefilter('ignore', DeprecationWarning)
        converted = str(FIX.refactor_string(source, str(path) + ':' + name))
    exec(compile(converted, '<finite-original-consumer>', 'exec'), namespace)
    return namespace[name]


class ItemType(object):
    HERO_TREASURE = 5
    COMMON = 1
    HERO_FRAGMENT = 2
    MEMORY_CRYSTAL = 3
    YIJIETI_HERO_FRAGMENT = 4
    YIJIETI_HERO_MEMORY_CRYSTAL = 6
    HERO_CRYSTAL = 7
    REFRESH = 8
    BREAK = 9
    HERO_ITEM = 10
    VIRTUAL = 11
    DYE = 12
    XUNZHANG = 13
    TREASUREEXPITEM = 14
    SKIN_TEXTURE = 15
    HERO_HOME_GIFT = 16
    SPE_LIBERATE_ITEM = 17
    CATEGORY_TREASURE = (5,)
    CATEGORY_COMMON = (1, 2, 3, 4, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17)
    CATEGORY_TASK = (18, 19)
    CATEGORY_GIFT = (20, 21)
    CATEGORY_FURNITURE = (22, 23)
    CATEGORY_XINWU = (24,)


class FullReason(object):
    TreasureBagIsFull = 1
    ItemBagIsFull = 2


class InvQueryReturnMsg(object):
    NEW_TREASURELIST = 1
    FullReason = FullReason


CONST = NS(ItemType=ItemType, InvQueryReturnMsg=InvQueryReturnMsg)
CC = NS(cc=NS(Color3B=lambda r, g, b: (r, g, b)))
ITEM_DATA = NS(data={})


def item_rows():
    rows = dict(ITEM_DATA.data)
    for itemid in TARGET_IDS:
        rows[itemid] = {'type': 5, 'subbag': SUBBAG[itemid], 'wrap': 1}
    rows[900001] = {'type': 5, 'subbag': 1, 'wrap': 1}
    rows[900002] = {'type': 5, 'subbag': 2, 'wrap': 1}
    item_rows.result = rows
    return rows


def build_inv_data():
    namespace = {'const': CONST, 'ITEM_DATA': NS(data=item_rows()), 'ItemData': NS(ItemData=object)}
    InvData = type('InvData', (object,), {})
    for name in ('__init__', 'initType2Category', 'checkBagFull', '_isFullByIdsWithCategory', 'isFullByIDs'):
        setattr(InvData, name, original('entity/avatar_attrs/InvData.py', name, namespace))
    namespace['InvData'] = InvData
    return InvData


class Node(object):
    def __init__(self):
        self.text = None
        self.visible = None
        self.color = None
        self.bright = None

    def setString(self, value):
        self.text = value

    def setVisible(self, value):
        self.visible = value

    def setColor(self, value):
        self.color = value

    def setBright(self, value):
        self.bright = value


class Grid(object):
    def __init__(self):
        self.view_row = 3
        self.calls = []
        self.focus = []

    def update_data_info(self, count, data, **kwargs):
        self.calls.append((count, data, kwargs))

    def focus_on_row(self, row):
        self.focus.append(('row', row))

    def focus_on_targetY(self, row):
        self.focus.append(('targetY', row))


class PanelBase(object):
    def __init__(self):
        self.nodes = {}
        self.num = Node()
        self.btn_treasure_full_tips = Node()
        self.btn_cuiqu = Node()
        self.scroll = Node()
        self.no_treasure = Node()
        self.text_on = Node()
        self.icon_on = Node()
        self.btn_shop = Node()
        self.gridScrollView = Grid()
        self.slider = NS(refresh=lambda: None)
        self.sort = lambda values: values
        self.s_filter = {}
        self.last_treasure = None
        self.last_targetY = 0
        self.zhuanshu_show = False
        self.treasure_list = []

    def __getitem__(self, key):
        return self.nodes.setdefault(key, Node())

    def on_load(self):
        self['main.num.num_last'].setString('/500')

    def is_exchange_available(self):
        return True


class ClientAvatarBase(object):
    def __init__(self):
        self.invData = None
        self.counter = 0

    def init_from_dict(self, bdict):
        self.invData = InvData()
        for itemid, subbag in bdict.get('records', ()):
            self.counter += 1
            item = NS(uuid='u%06d' % self.counter, itemid=itemid, type=5, subbag=subbag,
                      wrap=1, prior=0, invId=0, treasureExclusive=(subbag == 2), treasureClass=5,
                      treasureCost=1, treasureSuit=[], treasureForbid=False,
                      calcTreasureAttr=lambda: [])
            self.invData.inv.append(item)
            self.invData.invByType.setdefault(5, []).append(item)
            self.invData.invByID.setdefault(itemid, []).append(item)


def target_records():
    return [(template, SUBBAG[template]) for template in TARGET_IDS for _quality in range(5)]


class Harness(object):
    def __init__(self):
        self.saved = {}
        self.mods = {}
        global InvData
        InvData = build_inv_data()
        item_rows()
        self.InvData = InvData
        self.gg = self.module('gg')
        self.gg.avatar = None
        self.gg.ui = NS(panels=NS(common_confirm=NS(notify_get=lambda *args, **kwargs: None),
                                 common_fullscreen=object(), hero_herolist=object(),
                                 navigation_canvas=object()))
        self.const = self.module('com.const')
        self.const.ItemType = ItemType
        self.const.InvQueryReturnMsg = InvQueryReturnMsg
        self.ClientAvatar = type('ClientAvatar', (ClientAvatarBase,), {})
        self.Panel = type('Panel', (PanelBase,), {})
        self.raw_refresh = original('cocos/panels/treasure_treasurelist.py', 'refresh', {
            'gg': self.gg, 'const': self.const, 'cc': CC})
        self.Panel.refresh = self.raw_refresh
        self.avatar_module = self.module('entity.ClientAvatar')
        self.avatar_module.ClientAvatar = self.ClientAvatar
        self.avatar_module.gg = self.gg
        self.panel_module = self.module('cocos.panels.treasure_treasurelist')
        self.panel_module.Panel = self.Panel
        self.panel_module.gg = self.gg
        self.panel_module.const = self.const
        self.panel_module.cc = CC
        self.raw_gate = original('entity/avatar_members/InvMember.py', 'checkUnlinkTreasureFull',
                                 {'const': self.const})
        self.raw_show = original('cocos/panels/bbs_home.py', 'notify_hero_show', {'gg': self.gg})
        self.spec = importlib.util.spec_from_file_location(
            'shadow_capacity', ROOT / 'offline/current/runtime/project7_shadow_capacity.py')
        self.capacity_module = importlib.util.module_from_spec(self.spec)
        self.spec.loader.exec_module(self.capacity_module)
        self.state = self.capacity_module.install(POLICY)

    def module(self, name):
        if name in self.mods:
            return self.mods[name]
        self.saved[name] = sys.modules.get(name)
        value = types.ModuleType(name)
        self.mods[name] = value
        sys.modules[name] = value
        if '.' in name:
            parent, leaf = name.rsplit('.', 1)
            setattr(self.module(parent), leaf, value)
        return value

    def close(self):
        for name, value in self.saved.items():
            if value is None:
                sys.modules.pop(name, None)
            else:
                sys.modules[name] = value

    def avatar(self, records):
        value = self.ClientAvatar()
        value.init_from_dict({'records': records})
        self.gg.avatar = value
        value.heroMgrData = NS(getAllHeroes=lambda: {})
        value.checkUnlinkTreasureFull = types.MethodType(self.raw_gate, value)
        return value

    def new_inv(self, records):
        value = self.InvData()
        for itemid, subbag in records:
            item = NS(uuid=str(len(value.inv)), itemid=itemid, type=5, subbag=subbag,
                      wrap=1, prior=0, invId=0, treasureExclusive=(subbag == 2), treasureClass=5,
                      treasureCost=1, treasureSuit=[], treasureForbid=False)
            value.inv.append(item)
            value.invByType.setdefault(5, []).append(item)
            value.invByID.setdefault(itemid, []).append(item)
        return value

    def append_items(self, inv, itemid, subbag, count):
        for _ in range(count):
            item = NS(uuid='a%06d' % len(inv.inv), itemid=itemid, type=5, subbag=subbag,
                      wrap=1, prior=0, invId=0, treasureExclusive=(subbag == 2), treasureClass=5,
                      treasureCost=1, treasureSuit=[], treasureForbid=False)
            inv.inv.append(item)
            inv.invByType.setdefault(5, []).append(item)
            inv.invByID.setdefault(itemid, []).append(item)

    def show_panel(self, avatar=None):
        self.gg.avatar = avatar or self.gg.avatar
        panel = self.Panel()
        return panel


class ShadowCapacityTests(unittest.TestCase):
    def setUp(self):
        self.harness = Harness()

    def tearDown(self):
        self.harness.close()

    def test_original_gate_count_display_and_normal_pagination(self):
        h = self.harness
        records = target_records()
        avatar = h.avatar(records)
        inv = avatar.invData
        category = h.const.ItemType.CATEGORY_TREASURE
        # Original instance before projection is still the stock 500/400 gate.
        raw = h.new_inv(records)
        self.assertEqual(raw.subCategorySize[(category, 1)], 500)
        self.assertEqual(raw.subCategorySize[(category, 2)], 400)
        self.assertEqual(raw.categorySize[category], 500)
        self.assertTrue(raw.checkBagFull(category, 1))
        self.assertTrue(raw.checkBagFull(category, 2))
        self.assertTrue(raw.isFullByIDs({TARGET_IDS[0]: 1}))
        # Only the current Avatar.invData is projected; original methods run.
        self.assertEqual(inv.categorySize[category], 2100)
        self.assertEqual(inv.subCategorySize[(category, 1)], 1310)
        self.assertEqual(inv.subCategorySize[(category, 2)], 790)
        self.assertEqual(inv.maxCost, 25)
        self.assertFalse(inv.checkBagFull(category, 1))
        self.assertFalse(inv.checkBagFull(category, 2))
        self.assertFalse(inv.isFullByIDs({TARGET_IDS[0]: 1}))
        self.assertFalse(avatar.checkUnlinkTreasureFull())
        # Another InvData (the hero.treasureInv shape) and ordinary category are untouched.
        other = h.InvData()
        self.assertEqual(other.subCategorySize[(category, 1)], 500)
        self.assertEqual(other.subCategorySize[(category, 2)], 400)
        self.assertEqual(inv.categorySize[h.const.ItemType.CATEGORY_COMMON], 500)
        # Original hero-list entry gate now follows the normal path.
        events = []
        h.gg.ui.panels.common_confirm.notify_get = lambda *args, **kwargs: events.append('fullscreen')
        home = NS(can_rebuild_panels=True,
                  add_layer=lambda *args: events.append('hero_list'),
                  proc_event=lambda *args, **kwargs: events.append('show'),
                  notify_treasure_show=lambda: events.append('treasure'))
        h.raw_show(home)
        self.assertIn('hero_list', events)
        self.assertNotIn('fullscreen', events)
        raw_events = []
        h.gg.ui.panels.common_confirm.notify_get = lambda *args, **kwargs: raw_events.append('fullscreen')
        raw_home = NS(can_rebuild_panels=True, add_layer=lambda *args: raw_events.append('hero_list'),
                      proc_event=lambda *args, **kwargs: None, notify_treasure_show=lambda: None)
        raw_avatar = h.new_inv(records)
        h.gg.avatar = NS(invData=raw_avatar, checkUnlinkTreasureFull=lambda: raw_avatar.checkBagFull(category, 1))
        h.raw_show(raw_home)
        self.assertIn('fullscreen', raw_events)
        # Display and pagination: the original refresh body still feeds every item to GridScrollView.
        panel = h.show_panel(avatar)
        panel.on_load()
        self.assertEqual(panel['main.num.num_last'].text, '/1310')
        panel.refresh()
        count, data, _kwargs = panel.gridScrollView.calls[-1]
        self.assertEqual(count, 1210)
        self.assertEqual(len(data), 1210)
        self.assertEqual(len(panel.treasure_list), 1210)
        self.assertEqual(panel['main.num.num'].text, '1210')
        self.assertEqual(panel['main.num.num_last'].text, '/1310')
        self.assertFalse(panel['main.num.tips'].visible)
        # The exclusive list has its own subbag capacity, not the 2100 total.
        panel.zhuanshu_show = True
        panel.refresh()
        exclusive = panel.gridScrollView.calls[-1][0]
        self.assertEqual(exclusive, 690)
        self.assertEqual(panel['main.num.num'].text, '690')
        self.assertEqual(panel['main.num.num_last'].text, '/790')
        self.assertFalse(panel['main.num.tips'].visible)
        self.assertEqual(count + exclusive, 1900)
        # Intake/display stay consistent against the load-scoped 100 draw margin.
        # Original InvData gate is `cur > limit`; original NEW_TREASURELIST display
        # marks full at `count >= limit`. Preserve both exact operators.
        h.append_items(avatar.invData, 900001, 1, 99)
        panel.zhuanshu_show = False
        self.assertFalse(avatar.checkUnlinkTreasureFull())
        panel.refresh()
        self.assertEqual(panel.gridScrollView.calls[-1][0], 1309)
        self.assertEqual(panel['main.num.num'].text, '1309')
        self.assertEqual(panel['main.num.num_last'].text, '/1310')
        self.assertFalse(panel['main.num.tips'].visible)
        h.append_items(avatar.invData, 900001, 1, 1)
        self.assertFalse(avatar.checkUnlinkTreasureFull())
        panel.refresh()
        self.assertEqual(panel.gridScrollView.calls[-1][0], 1310)
        self.assertEqual(panel['main.num.num_full'].text, '1310')
        self.assertEqual(panel['main.num.num_last'].text, '/1310')
        self.assertTrue(panel['main.num.tips'].visible)
        h.append_items(avatar.invData, 900001, 1, 1)
        self.assertTrue(avatar.checkUnlinkTreasureFull())
        panel.refresh()
        self.assertEqual(panel.gridScrollView.calls[-1][0], 1311)
        self.assertEqual(panel['main.num.num_full'].text, '1311')
        self.assertEqual(panel['main.num.num_last'].text, '/1310')
        self.assertTrue(panel['main.num.tips'].visible)
        # Unpatched original body still marks the list full against its hard-coded 500.
        h.gg.avatar = h.avatar(records)
        raw_panel = h.Panel()
        h.raw_refresh(raw_panel, False, False)
        self.assertEqual(raw_panel.gridScrollView.calls[-1][0], 1210)
        self.assertTrue(raw_panel['main.num.tips'].visible)

    def test_reproject_after_reload_and_persistent_scope(self):
        h = self.harness
        records = target_records()
        extra = records + [(900001, 1), (900002, 2)]
        avatar = h.avatar(extra)
        category = h.const.ItemType.CATEGORY_TREASURE
        grown = avatar.invData.categorySize[category]
        self.assertEqual(grown, 2102)
        self.assertEqual(avatar.invData.subCategorySize[(category, 1)], 1311)
        self.assertEqual(avatar.invData.subCategorySize[(category, 2)], 791)
        profile = {'records': list(records), 'unrelated': {'keep': True}}
        before = copy.deepcopy(profile)
        avatar.init_from_dict(profile)
        self.assertEqual(profile, before)
        self.assertEqual(avatar.invData.categorySize[category], 2100)
        self.assertEqual(avatar.invData.subCategorySize[(category, 1)], 1310)
        # The projection is instance state only; a fresh InvData starts from stock limits.
        self.assertEqual(h.InvData().categorySize[category], 500)

    def test_static_consumers_policy_and_separate_q5_dye_gaps(self):
        overlay = (ROOT / 'offline/current/runtime/project7_shadow_capacity.py').read_text('ascii')
        for forbidden in ('.checkBagFull =', '.checkUnlinkTreasureFull =', '.isFullByIDs =',
                          '.maxCost =', '.treasureInv =', '.su =', '.era ='):
            self.assertNotIn(forbidden, overlay)
        inv_member = (ROOT / 'analysis/original-py-640/entity/avatar_members/InvMember.py').read_text()
        self.assertIn('return self.invData.checkBagFull(const.ItemType.CATEGORY_TREASURE, 1)', inv_member)
        home = (ROOT / 'analysis/original-py-640/cocos/panels/bbs_home.py').read_text()
        self.assertIn('if gg.avatar.checkUnlinkTreasureFull():', home)
        list_panel = (ROOT / 'analysis/original-py-640/cocos/panels/treasure_treasurelist.py').read_text()
        self.assertIn("setString('/500')", list_panel)
        self.assertIn('if len(treasure[\'all\']) >= 500:', list_panel)
        policy = json.loads(POLICY)
        self.assertEqual(policy['format'], 'project7-shadow-capacity-policy-v1')
        self.assertEqual(policy['target_template_ids'], sorted(TARGET_IDS))
        self.assertEqual(policy['target_total'], 1900)
        self.assertEqual(policy['target_subbag_counts'], {'1': 1210, '2': 690})
        self.assertEqual(policy['draw_margin_per_subbag'], 100)
        # Original subbag classification matches the panel's normal/exclusive lists.
        for row in TARGET['treasures']:
            exclusive = bool(HT_ROWS[(row['id'], 1)].get('validHeroes'))
            self.assertEqual(SUBBAG[row['id']] == 2, exclusive)
        # q5 stays an unlock, not a cultivation roll: no era/su arrays in target rows.
        for row in TARGET['treasures']:
            for quality in row['qualities']:
                self.assertNotIn('era', quality)
                self.assertNotIn('su', quality)
        # Dye metadata is validated, not rewritten: parent exists on the same hero.
        skins = dict((row['id'], row) for row in TARGET['skins'])
        for row in TARGET['skins']:
            if row.get('isDyeSkin'):
                self.assertIn(row['oriSkin'], skins)
                self.assertEqual(skins[row['oriSkin']]['hero'], row['hero'])
                self.assertEqual(row.get('sourceCanDye'), 1)
            else:
                self.assertIsNone(row.get('oriSkin'))
        # The runtime source still parses with the Python2 grammar used by the game.
        with warnings.catch_warnings():
            warnings.simplefilter('ignore', DeprecationWarning)
            RefactoringTool([]).refactor_string(overlay, 'project7_shadow_capacity.py')

    def test_changed_policy_and_partial_cache_are_rejected(self):
        h = self.harness
        self.assertIs(h.capacity_module.install(POLICY), h.state)
        with self.assertRaises(ValueError):
            h.capacity_module.install(POLICY + ' ')
        h.Panel.refresh = lambda self, resort=False, lastRow=False: None
        with self.assertRaises(RuntimeError):
            h.capacity_module.install(POLICY)


if __name__ == '__main__':
    unittest.main()
