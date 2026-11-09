import copy
import json
from pathlib import Path
import sys
from types import ModuleType, SimpleNamespace
import unittest
from unittest.mock import patch
import msgpack
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'runtime'))
from offline_avatar_snapshot import build_local_avatar_snapshot, native_city_reply, normalize_avatar_wire, pack_original_avatar
from offline_week import validate_full_week_avatar
from offline_story import initial_story_state
from offline_gacha import new_gacha_state
from test_offline_week import ModelObjectId

class AvatarSnapshotTests(unittest.TestCase):
    def setUp(self):
        hero = json.loads((ROOT / 'tests/fixtures/native-hero24.json').read_text())['hero']
        self.skin = hero['cs']
        self.item = {'u': 'b' * 24, 'i': 1002, 'w': 1, 'tr': {'cl': 5}}
        hero['ti']['items'] = [copy.deepcopy(self.item)]
        self.state = {'profile': {'version': 1, 'migrations': [], 'heroes': {'24': hero}, 'economy': {'money': 12345, 'exp': 700, 'level': 2},
                                 'treasures': {'items': [copy.deepcopy(self.item)]}},
            'story': initial_story_state(), 'day': {'stock_day': 1}, 'gacha': new_gacha_state(),
            'available_events': [[40000, 1]], 'processing_events': [], 'completed_events': [1000], 'player_name': 'Host'}
        self.state['gacha']['items'] = [{'u': 'c' * 24, 'i': 4253, 'w': 10}]
        self.state['gacha']['opened_total'] = 12
        self.state['story'].update(cgs=[2, 3], new_cgs=[3], endings=[1], city_values={'dv': 1, 'av': 24, 'bf': 50, 'fv': 5, 'ev': 0, 'rv': 5},
            city_areas={'1': {'id': 1, 'st': [0, False, False], 'lv': 1,
                             'stage': {'cs': 101, 'sl': [[101]]},
                             'bd': {'1': {'id': 1, 'uuid': 'd' * 24, 'u': False}}}})
        self.template = {'st': 100, 'name': 'old', 'an': 'offline', 'uid': 1, 'sv': 1, 'role': 1,
                         'inv': {}, 'ldd': {'hfp': {}}, 'std': {}, 'extra_stock_loader_fields': {'values': set([1, 2])}}
        modules = {name: ModuleType(name) for name in ('common', 'common.IdManager')}
        modules['common.IdManager'].IdManager = SimpleNamespace(str2id=ModelObjectId)
        context = patch.dict(sys.modules, modules)
        context.start()
        self.addCleanup(context.stop)

    def test_full_reload_preserves_native_ids_ownership_balances_and_realized_fields(self):
        snapshot = build_local_avatar_snapshot(self.state, self.template)
        validate_full_week_avatar(snapshot, self.state)
        hero = dict(snapshot['heromgr']['hrs'])[24]
        self.assertIsInstance(hero['cs'], ModelObjectId)
        self.assertIsInstance(hero['ti']['items'][0]['u'], ModelObjectId)
        self.assertIsInstance(snapshot['city']['areas']['area_1']['bd']['1']['uuid'], ModelObjectId)
        self.assertEqual(snapshot['city']['areas']['area_1']['bd']['1']['u'], False)
        self.assertEqual(snapshot['ldd']['ct'], 12)
        self.assertEqual(snapshot['extra_stock_loader_fields'], self.template['extra_stock_loader_fields'])
        self.assertEqual(self.state['story']['city_areas']['1']['bd']['1']['uuid'], 'd' * 24)

    def test_pending_pendant_reload_preserves_other_pending_and_hero_state(self):
        self.template['heromgr'] = {'ps': {24: [100031]}, 'psc': {'kept': 7},
            'pp': {97: [17]}, 'ppc': {'kept': 8}, 'bhrs': [(9999, {'stale': True})]}
        self.state['profile']['hero_pending'] = {'pp': {'151': [18]}}
        before = copy.deepcopy(self.state)
        snapshot = build_local_avatar_snapshot(self.state, self.template)
        manager = snapshot['heromgr']
        self.assertEqual(manager['pp'], {151: [18]})
        self.assertEqual(manager['ps'], {24: [100031]})
        self.assertEqual(manager['psc'], {'kept': 7})
        self.assertEqual(manager['ppc'], {'kept': 8})
        self.assertNotIn(9999, dict(manager.get('bhrs', [])))
        self.assertEqual(self.state, before)
        self.assertIsInstance(dict(manager['hrs'])[24]['cs'], ModelObjectId)
        manager['pp'][151].append(19)
        self.assertEqual(self.state, before)

    def test_new_week_clears_known_weekly_story_fields_from_old_realized_template(self):
        self.template['std'] = {'cl': [8], 'fc': [9], 'cr': True, 'dr': {'8': True},
            'srv': 50, 'ssv': 30, 'yiv': 10, 'cm': 2, 'ct': 3, 'unknown_permanent': [7]}
        self.state['story']['week'] = 1
        self.state['week_protocol'] = {'transition': {'target_week': 1}}
        snapshot = build_local_avatar_snapshot(self.state, self.template)
        self.assertEqual({k: snapshot['std'][k] for k in ('cl', 'fc', 'cr', 'dr', 'srv', 'ssv', 'yiv', 'cm', 'ct')},
            {'cl': [], 'fc': [], 'cr': False, 'dr': {}, 'srv': 0, 'ssv': 0, 'yiv': 0, 'cm': None, 'ct': None})
        self.assertEqual(snapshot['std']['unknown_permanent'], [7])

    def test_original_codec_subset_uses_extended_json_and_object_hook_not_str(self):
        snapshot = build_local_avatar_snapshot(self.state, self.template)
        modules = {name: ModuleType(name) for name in ('msgpack.embed', 'bson', 'bson.json_util')}
        def default(value):
            if isinstance(value, ModelObjectId): return {'$oid': str(value)}
            raise TypeError('Unsupported native value')
        # Host modern msgpack models only the original0.4-compatible raw subset.
        modules['bson.json_util'].default = default
        modules['msgpack.embed'].dumps = msgpack.packb
        with patch.dict(sys.modules, modules):
            wire = pack_original_avatar(snapshot)
        decoded = msgpack.unpackb(wire, raw=False, strict_map_key=False,
            object_hook=lambda value: ModelObjectId(value['$oid']) if '$oid' in value else value)
        validate_full_week_avatar(decoded, self.state)
        self.assertIsInstance(dict(decoded['heromgr']['hrs'])[24]['cs'], ModelObjectId)
        self.assertEqual(decoded['extra_stock_loader_fields']['values'], [1, 2])

    def test_city_callback_converts_building_uuid_only_and_preserves_authoritative_status(self):
        area = self.state['story']['city_areas']['1']
        reply = native_city_reply('get_area_info_reply', {'ai': area})
        self.assertIsInstance(reply['ai']['bd']['1']['uuid'], ModelObjectId)
        self.assertEqual(reply['ai']['st'], [0, False, False])
        self.assertIs(reply['ai']['bd']['1']['u'], False)
        self.assertEqual(area['bd']['1']['uuid'], 'd' * 24)

if __name__ == '__main__': unittest.main()
