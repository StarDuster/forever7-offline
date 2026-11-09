import copy
import sys
import unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'runtime'))
sys.path.insert(0, str(ROOT / 'analysis/research-agent'))
from read_literal_marshal import read
from offline_treasure import migrate_treasure_inventory, prepare_treasure_equipment, validate_treasure_inventory

class TreasureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        base = ROOT / 'analysis/android640-scripts/com/data/cdata'
        cls.catalog = read(base / 'hero_treasure.marshal')
        cls.items = read(base / 'item_data.marshal')

    def test_all_380_templates_get_nonempty_table_attributes_and_matching_fixed_tricks(self):
        import json
        indices = json.loads((ROOT / 'tests/fixtures/combat-attribute-indices.json').read_text())['indices']
        ids = iter('%024x' % n for n in range(1, 1000))
        inv, changed = migrate_treasure_inventory(None, self.catalog, self.items, indices, lambda: next(ids), 123)
        self.assertTrue(changed)
        self.assertEqual(len(inv['items']), 380)
        for item in inv['items']:
            row = self.catalog[(item['i'], 5)]
            expected = []
            for field, prefix in (('secondAttrs', 'f'), ('thridAttrs', 't')):
                expected.extend({'n': prefix + str(indices[n]), 'v': limits[0]}
                                for n, limits in sorted(row.get(field, {}).items()))
            self.assertEqual(item['tr']['attr'], expected)
            self.assertEqual(item['tr']['ft'], list(row.get('fixTrick', ())))
        again, changed = migrate_treasure_inventory(inv, self.catalog, self.items, indices,
            lambda: self.fail('duplicate grant'), 999)
        self.assertFalse(changed)
        self.assertEqual(inv, again)

    def inventory(self):
        return {'version': 1, 'items': [{'u': '%024x' % n, 'i': n, 'tr': {'cl': 5, 'attr': [{'n': 'f34', 'v': 10}]}} for n in (1, 2, 3)]}

    def profile(self):
        return {'heroes': {'24': {'ti': {'items': [], 'mc': 5}}, '20': {'ti': {'items': [], 'mc': 5}}}}

    def test_equipment_replacement_and_shared_references_are_idempotent(self):
        inv, profile = self.inventory(), self.profile()
        catalog = {(i, 5): {'cost': 2} for i in (1, 2, 3)}
        uid = inv['items'][0]['u']
        args = {'h': 24, 'i': {uid: 0}, 'pi': ''}
        one, inv2, reply, result, restored = prepare_treasure_equipment(profile, inv, 'equipTreasureBatch', args, catalog)
        self.assertEqual(reply, 'equipTreasureBatchReply')
        self.assertEqual(result['e'][0][0], uid)
        self.assertEqual(profile, self.profile())
        two, inv3, _, _, _ = prepare_treasure_equipment(one, inv2, 'equipTreasureBatch', args, catalog)
        self.assertEqual(one, two)
        self.assertEqual(inv, inv3)
        args['h'] = 20
        shared, _, _, _, _ = prepare_treasure_equipment(two, inv3, 'equipTreasureBatch', args, catalog)
        self.assertEqual(shared['heroes']['24']['ti']['items'], shared['heroes']['20']['ti']['items'])
        empty, _, _, _, _ = prepare_treasure_equipment(shared, inv3, 'unequipAllTreasure', {'h': 24}, catalog)
        self.assertFalse(empty['heroes']['24']['ti']['items'])
        self.assertTrue(empty['heroes']['20']['ti']['items'])

    def test_invalid_cost_exclusive_and_source_do_not_mutate(self):
        inv, profile = self.inventory(), self.profile()
        before = copy.deepcopy((inv, profile))
        for selection, catalog in (
            ({i['u']: 0 for i in inv['items']}, {(i, 5): {'cost': 2} for i in (1, 2, 3)}),
            ({inv['items'][0]['u']: 0}, {(1, 5): {'validHeroes': [20]}}),
            ({inv['items'][0]['u']: 20}, {(1, 5): {'cost': 1}})):
            with self.assertRaises(ValueError):
                prepare_treasure_equipment(profile, inv, 'equipTreasureBatch', {'h': 24, 'i': selection}, catalog)
        self.assertEqual((inv, profile), before)

    def test_legacy_detached_equipment_is_restored_once(self):
        inv, profile = self.inventory(), self.profile()
        item = inv['items'].pop()
        profile['heroes']['24']['ti']['items'] = [item]
        profile, restored_inv, _, _, restored = prepare_treasure_equipment(profile, inv, 'unequipAllTreasure', {'h': 24}, {})
        self.assertEqual(restored, [item])
        _, again, _, _, restored = prepare_treasure_equipment(profile, restored_inv, 'unequipAllTreasure', {'h': 24}, {})
        self.assertEqual(again, restored_inv)
        self.assertFalse(restored)

    def test_embedded_gateway_equips_persists_and_syncs_with_gacha(self):
        import json
        import tempfile
        from types import ModuleType, SimpleNamespace
        from unittest.mock import patch
        from test_local_gateway import Owner
        scope = {'__name__': 'embedded_runtime'}
        for name in ('offline_store.py', 'offline_wardrobe_completion.py', 'offline_transport.py', 'offline_event_battle.py', 'offline_battle.py', 'offline_stage.py', 'offline_week.py', 'offline_day.py', 'offline_conditions.py', 'offline_story.py', 'offline_event_effects.py', 'offline_story_engine.py', 'offline_city_actions.py', 'offline_avatar_snapshot.py', 'offline_postbattle.py', 'offline_profile.py', 'offline_treasure.py', 'offline_gacha.py', 'local_gateway.py'):
            exec(compile((ROOT / 'runtime' / name).read_text(), name, 'exec'), scope)
        indices = json.loads((ROOT / 'tests/fixtures/combat-attribute-indices.json').read_text())['indices']
        modules = {name: ModuleType(name) for name in ('com', 'com.const', 'com.data', 'com.data.cdata', 'com.data.cdata.hero_treasure', 'com.data.cdata.item_data', 'common', 'common.IdManager')}
        modules['com.const'].CombatAttrs = SimpleNamespace(NAME_TO_INDEX=indices)
        modules['com.data.cdata.hero_treasure'].data = self.catalog
        modules['com.data.cdata.item_data'].data = self.items
        ids = iter('%024x' % n for n in range(100, 1000))
        modules['common.IdManager'].IdManager = SimpleNamespace(genid=lambda: next(ids), str2id=lambda uid: ('native', uid))
        hero = json.loads((ROOT / 'tests/fixtures/native-hero24.json').read_text())['hero']
        with tempfile.TemporaryDirectory() as folder, patch.dict(sys.modules, dict(modules, offline_treasure=None)):
            scope['_f7_doc'], scope['_f7_log'] = folder, lambda _: None
            owner = Owner()
            proxy = scope['LocalProxy'](None, owner, persistent=True)
            proxy.profile = {'version': 1, 'heroes': {'24': hero}, 'migrations': []}
            proxy.ensure_treasure_inventory()
            before = copy.deepcopy(proxy.profile)
            proxy.ensure_treasure_inventory()
            self.assertEqual(proxy.profile, before)
            selected = next(i for i in proxy.profile['treasures']['items'] if i['i'] == 1001)
            proxy.handle_treasure_equipment('equipTreasureBatch', {'h': 24, 'i': {selected['u']: 0}, '_cbid_': 7})
            self.assertEqual(owner.replies[-1][0], 'equipTreasureBatchReply')
            self.assertEqual(owner.replies[-1][1]['_cbid_'], 7)
            self.assertEqual(owner.replies[-1][1]['e'][0][2]['u'], ('native', selected['u']))
            saved = copy.deepcopy(proxy.profile)
            with patch.object(proxy._store, 'write', side_effect=OSError('disk full')):
                with self.assertRaises(OSError):
                    proxy.handle_treasure_equipment('unequipAllTreasure', {'h': 24, '_cbid_': 8})
            self.assertEqual(proxy.profile, saved)
            self.assertEqual(owner.replies[-1], ('serverCallbackCarrier', {'_r_': {}, '_cbid_': 8}))
            restored = scope['LocalProxy'](None, Owner(), persistent=True)
            self.assertEqual(restored.profile, saved)
            proxy.gacha = {'items': [{'u': 'f' * 24, 'i': 4253}]}
            proxy.sync_gacha_items()
            synced = owner.replies[-1][1]['i']
            self.assertEqual(len(synced), 381)
            self.assertTrue(any(i['i'] == 4253 for i in synced))
            snapshots = scope['hero_snapshots_for_client'](proxy.profile)
            self.assertEqual(snapshots[0][1]['ti']['items'][0]['u'], ('native', selected['u']))
