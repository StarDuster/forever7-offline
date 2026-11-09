"""Original candidate-period binding and actual Cocos callback wiring on a host fake."""
import copy
import json
import sys
import types
import unittest
from unittest.mock import patch
from test_gacha_archive import ROOT, archive


class RotationPeriodTests(unittest.TestCase):
    def setUp(self):
        contract = json.loads((ROOT / 'reports/special-gacha-p1-producer-review.json').read_text())
        self.rotations = {row['uaid']: row['original'] for row in contract['rotation_contract']['rows']}
        self.templates = {18801: {'tmp_type': 88}, 1: {'tmp_type': 7}}
        archive.offline_archive_clear()

    def tearDown(self):
        archive.offline_archive_clear()

    def test_all_21_periods_explicit_for_all_six_pools_and_unchanged_sources(self):
        before = copy.deepcopy(self.rotations)
        rows = archive.archive_rotation_periods(self.rotations, self.templates)
        self.assertEqual(len(rows), 21)
        self.assertEqual({r['rotation_uaid'] for r in rows}, set(self.rotations))
        for wire in (265, 369, 427, 454, 455, 484):
            row = dict(wire_t=wire, category='hero_treasure')
            with self.assertRaises(ValueError):
                archive.archive_make_session(row, {})
            with self.assertRaises(ValueError):
                archive.archive_make_session(row, {}, rotation_uaid=999, rotations=self.rotations, templates=self.templates)
            for period in rows:
                uaid = period['rotation_uaid']
                context = archive.archive_make_session(row, {}, rotation_uaid=uaid, rotations=self.rotations, templates=self.templates)
                self.assertEqual(context['rotation'], self.rotations[uaid])
                self.assertEqual(context['self_choose_wire'], wire)
                self.assertEqual(context['rotation_uaid'], uaid)
                self.assertIn(period, archive.archive_filter(rows, str(uaid)))
                self.assertIn(period, archive.archive_filter(rows, archive.archive_date(period['begin'])))
                self.assertIn('\u6863\u6848\u5019\u9009\u65f6\u671f', period['name'])
                context['rotation']['self_choose_S'].append(999)
        self.assertEqual(self.rotations, before)
        wrong = {1: dict(tmp_id=1, self_choose_S=[1], self_choose_A=[2], open_range=[2020] * 12)}
        self.assertEqual(archive.archive_rotation_periods(wrong, self.templates), [])
        with self.assertRaises(ValueError):
            archive.archive_make_session(dict(wire_t=265, category='hero_treasure'), {}, rotation_uaid=1, rotations=wrong, templates=self.templates)

    def test_contract_matches_all_original_rotation_88_marshal_rows(self):
        import importlib.util
        spec = importlib.util.spec_from_file_location('archive_literal_reader', ROOT / 'analysis/research-agent/read_literal_marshal.py')
        reader = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(reader)
        base = ROOT / 'analysis/android640-scripts/com/data/cdata'
        configs = reader.read(base / 'activity_config.marshal')
        templates = reader.read(base / 'activity_template.marshal')
        originals = {uaid: row for uaid, row in configs.items()
                     if templates.get(row.get('tmp_id'), {}).get('tmp_type') == 88}
        normalized = json.loads(json.dumps(originals))
        self.assertEqual({int(k): v for k, v in normalized.items()}, self.rotations)
        self.assertEqual(len(archive.archive_rotation_periods(configs, templates)), 21)

    def test_getter_only_overrides_rotation_88_in_matching_valid_archive_context(self):
        calls = []
        getter = archive.make_archive_rotation_getter(
            lambda kind, online=True: calls.append((kind, online)) or ('original', {}), self.rotations, self.templates)
        row = dict(wire_t=265, category='hero_treasure')
        context = archive.archive_make_session(row, {}, rotation_uaid=175, rotations=self.rotations, templates=self.templates)
        archive._f7_archive_session = context
        self.assertEqual(getter(88), (175, self.rotations[175]))
        self.assertEqual(getter(88, False), (175, self.rotations[175]))
        returned = getter(88)[1]
        returned['self_choose_S'].append(999)
        self.assertNotIn(999, self.rotations[175]['self_choose_S'])
        self.assertEqual(getter(7, False), ('original', {}))
        for bad in ({'wire_t': 354}, {'wire_t': 5}, dict(context, self_choose_wire=484),
                    dict(context, rotation_uaid=999), dict(context, rotation={}), None):
            archive._f7_archive_session = bad
            self.assertEqual(getter(88), ('original', {}))
        self.assertEqual(len(calls), 7)

    def test_native_tagged_mapping_compares_every_original_field_by_value(self):
        class TaggedRow:
            def __init__(self, fields): self.fields = fields
            def get(self, key, default=None): return self.fields.get(key, default)
            def items(self): return self.fields.items()
            def __eq__(self, other): return self is other
            def __deepcopy__(self, memo): return copy.deepcopy(self.fields, memo)

        original = copy.deepcopy(self.rotations[175])
        tagged = TaggedRow(original)
        self.assertNotEqual(tagged, original)
        rotations = dict(self.rotations)
        rotations[175] = tagged
        context = archive.archive_make_session(dict(wire_t=265, category='hero_treasure'),
            {}, rotation_uaid=175, rotations=rotations, templates=self.templates)
        self.assertIsInstance(context['rotation'], dict)
        archive._f7_archive_session = context
        getter = archive.make_archive_rotation_getter(lambda *a: ('original', {}),
            rotations, self.templates)
        self.assertEqual(getter(88), (175, original))
        for changed in (dict(original, uaid=999), dict(original, extra=1),
                        {k: v for k, v in original.items() if k != 'payment_time'}):
            archive._f7_archive_session = dict(context, rotation=changed)
            self.assertEqual(getter(88), ('original', {}))
        self.assertEqual(tagged.fields, original)

    def test_native_callback_graph_select_cancel_and_reopen(self):
        created = []

        class Node:
            def __init__(self):
                self.title = ''
                self.value = ''
                self.children = []
                self.removed = False
                created.append(self)
            @classmethod
            def create(cls, *args):
                return cls()
            def setTitleText(self, text): self.title = text
            def addTouchEventListener(self, callback): self.callback = callback
            def addChild(self, node, *args): self.children.append(node)
            def removeAllChildren(self): self.children = []
            def removeFromParent(self): self.removed = True
            def getString(self): return self.value
            def setString(self, text): self.value = text
            def convertToNodeSpace(self, point): return point
            def __getattr__(self, name):
                if name.startswith('set') or name == 'ignoreContentAdaptWithSize':
                    return lambda *args: None
                raise AttributeError(name)

        class Color3B(tuple):
            def __new__(cls, red, green, blue):
                return tuple.__new__(cls, (red, green, blue))

        class Color4B(tuple):
            def __new__(cls, red, green, blue, alpha):
                return tuple.__new__(cls, (red, green, blue, alpha))

        class TextField(Node):
            def setTextColor(self, color):
                if not isinstance(color, Color4B):
                    raise TypeError('TextField requires Color4B')
                self.text_color = color

            def setPlaceHolderColor(self, color):
                if not isinstance(color, Color4B):
                    raise TypeError('TextField placeholder requires Color4B')
                self.placeholder_color = color

        modules = {}
        def module(name, **attrs):
            obj = types.ModuleType(name)
            obj.__path__ = []
            obj.__dict__.update(attrs)
            modules[name] = obj
            return obj
        for name in ('com', 'com.data', 'com.data.cdata'): module(name)
        module('com.const', SCENE_SUMMON=1)
        module('com.data.cdata.chouka_info', data={1: {}, 5: {}, 265: {'self_choose': True}, 354: {}})
        module('com.data.cdata.furniture_delivery', data={})
        module('com.data.cdata.hero_treasure', data={1141: {'name': 'Treasure'}})
        module('com.data.cdata.hero', data={90: {'name': 'Hero90'}, 91: {'name': 'Hero91'}})
        module('com.data.cdata.chouka_treasure_wish', data={
            1: dict(drawType=5, treasure_id=1141, begin_time=[2019, 1, 2], end_time=[2019, 1, 16]),
            11: dict(drawType=1, wish_type=2, wish_target=90, gid=1, begin_time=[2016, 4, 3], end_time=[2016, 4, 24]),
            12: dict(drawType=1, wish_type=2, wish_target=91, gid=1, begin_time=[2016, 4, 3], end_time=[2016, 4, 24])})
        module('com.data.cdata.activity_config', data=self.rotations)
        module('com.data.cdata.activity_template', data=self.templates)
        for name, obj in list(modules.items()):
            if '.' in name:
                parent, child = name.rsplit('.', 1)
                setattr(modules[parent], child, obj)
        ns = types.SimpleNamespace
        module('cocosui', ccui=ns(Button=Node, Layout=Node, TextField=TextField, ScrollView=Node, TOUCH_EVENT_ENDED=2),
               cc=ns(Size=lambda *args: args, Vec2=lambda *args: args, Color3B=Color3B, Color4B=Color4B,
                     Director=ns(getInstance=lambda: ns(getWinSize=lambda: ns(width=1050, height=620))),
                     FileUtils=ns(getInstance=lambda: ns(isFileExist=lambda path: True))))
        failures = []
        module('gg', city_container=ns(get_scene_by_key=lambda key: 1, check_scene=lambda scene: True),
               ui=ns(projplistinfo={}, panels=ns(common_confirm=ns(notify_confirm=lambda reason, callback: failures.append(reason)))))
        sync_contexts = []
        modules['gg']._f7_avatar_proxy = ns(sync_gacha_native_state=lambda: sync_contexts.append(archive.offline_archive_context()))
        entries = []
        go_entries = []
        panel = ns(_node=Node(), on_chouka_btn_click=lambda wire: entries.append((wire, archive.offline_archive_context())),
                   _on_open_go_click=lambda: go_entries.append(entries[-1][0]))
        def press(fragment, nodes):
            node = next(node for node in nodes if fragment in node.title)
            node.callback(node, 2)
        with patch.dict(sys.modules, modules):
            archive.show_gacha_archive(panel)
            scroll = next(node for node in created if any('[t=265]' in child.title for child in node.children))
            press('[t=265]', scroll.children)
            self.assertEqual(entries, [])
            self.assertIsNone(archive.offline_archive_context())
            self.assertEqual(sum('rotation_uaid=' in n.title for n in scroll.children), 21)
            press('\u5173\u95ed', created)
            self.assertIsNone(archive.offline_archive_context())
            created[:] = []
            archive.show_gacha_archive(panel)
            scroll = next(node for node in created if any('[t=265]' in child.title for child in node.children))
            press('[t=265]', scroll.children)
            press('rotation_uaid=175]', scroll.children)
            self.assertEqual(entries[-1][0], 265)
            self.assertEqual(entries[-1][1]['rotation_uaid'], 175)
            self.assertEqual(entries[-1][1]['rotation'], self.rotations[175])
            self.assertEqual(go_entries, [])
            archive.offline_archive_clear()
            created[:] = []
            archive.show_gacha_archive(panel)
            scroll = next(node for node in created if any('[t=5]' in child.title for child in node.children))
            press('[t=5]', scroll.children)
            self.assertIsNone(archive.offline_archive_context())
            press('wish_id=1]', scroll.children)
            self.assertEqual(entries[-1][0], 5)
            self.assertEqual(entries[-1][1]['wish_id'], 1)
            self.assertEqual(sync_contexts[-1]['wish_id'], 1)
            self.assertEqual(go_entries, [5])
            self.assertEqual(failures, [])
            archive.offline_archive_clear()
            created[:] = []
            archive.show_gacha_archive(panel)
            scroll = next(node for node in created if any('[t=1]' in child.title for child in node.children))
            press('[t=1]', scroll.children)
            self.assertIsNone(archive.offline_archive_context())
            self.assertEqual(sum('hero_wish_id=' in node.title for node in scroll.children), 1)
            press('hero_wish_id=11]', scroll.children)
            self.assertEqual(entries[-1][0], 1)
            self.assertEqual(entries[-1][1]['hero_wish_ids'], [11, 12])
            self.assertEqual(sync_contexts[-1]['hero_wish_ids'], [11, 12])
            self.assertEqual(go_entries, [5, 1])
            previous = {'wire_t': 265, 'category': 'hero_treasure'}
            archive._f7_archive_session = copy.deepcopy(previous)
            attempts = []
            def failing_sync():
                attempts.append(archive.offline_archive_context())
                raise RuntimeError('projection unavailable')
            modules['gg']._f7_avatar_proxy.sync_gacha_native_state = failing_sync
            before_entries = len(entries)
            panel.cover = True
            created[:] = []
            archive.show_gacha_archive(panel)
            scroll = next(node for node in created if any('[t=5]' in child.title for child in node.children))
            press('[t=5]', scroll.children)
            press('wish_id=1]', scroll.children)
            self.assertEqual(len(attempts), 2)
            self.assertEqual(attempts[0]['wish_id'], 1)
            self.assertEqual(attempts[1], previous)
            self.assertEqual(archive.offline_archive_context(), previous)
            self.assertFalse(panel.cover)
            self.assertEqual(len(entries), before_entries)
            self.assertEqual(len(failures), 1)
            self.assertIn('projection unavailable', failures[0])
            created[:] = []
            with patch.object(TextField, 'setTextColor', side_effect=RuntimeError('native binding failure')):
                with self.assertRaisesRegex(RuntimeError, 'native binding failure'):
                    archive.show_gacha_archive(panel)
            # A partially built modal must still have an actual working exit.
            root = created[0]
            self.assertFalse(root.removed)
            press('\u5173\u95ed', created)
            self.assertTrue(root.removed)
            self.assertEqual(archive.offline_archive_context(), previous)


if __name__ == '__main__':
    unittest.main()
