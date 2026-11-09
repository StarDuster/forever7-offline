"""Host end-to-end adapter transactions, with actual-table fixture contracts."""
import copy
import hashlib
import json
from pathlib import Path
import sys
import tempfile
from types import ModuleType, SimpleNamespace
import unittest
from unittest.mock import patch
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'runtime'))
sys.path.insert(0, str(ROOT / 'tools'))
from export_game_catalogs import decode
import offline_event_battle, offline_gacha, offline_treasure, offline_stage, offline_battle, offline_city_actions, offline_week, offline_avatar_snapshot
from test_local_gateway import gateway, Owner
from test_offline_transport import FakeEngine
from offline_story import initial_story_state, evaluate_story_condition
from offline_gacha import new_gacha_state

class IntegratedGatewayTests(unittest.TestCase):
    def setUp(self):
        self.folder = tempfile.TemporaryDirectory()
        self.addCleanup(self.folder.cleanup)
        gateway._f7_doc, gateway._f7_log = self.folder.name, lambda _: None
        for module in (offline_event_battle, offline_gacha, offline_treasure, offline_stage, offline_battle, offline_city_actions, offline_week, offline_avatar_snapshot):
            for name, value in vars(module).items():
                if callable(value) and not name.startswith('_'):
                    setattr(gateway, name, value)
        gateway.evaluate_story_condition = evaluate_story_condition
        self.owner = Owner()
        self.owner.id, self.owner.level = 'original-id', 1
        self.owner.weeknumData = SimpleNamespace(daynum=0, weeknum=0)
        hero_obj = SimpleNamespace(calcAllAttr=lambda lv: {'_base_max_hp': 123, '_hp_delta': 5},
            calcSkill=lambda: ([(11, 2)], []), calcTricks=lambda: [],
            getCurSkinObj=lambda: SimpleNamespace(getPersistentDict=lambda: {'i': 24, 'u': 'a' * 24}),
            getInsightValue=lambda: 100, getConstructValue=lambda: 100, getLeadershipValue=lambda: 100)
        self.owner.heroMgrData = SimpleNamespace(getHero=lambda hid: hero_obj,
            getArtifactInfo=lambda hid: (False, 0), getAwakeStage=lambda hid: 1)
        self.proxy = gateway.LocalProxy(None, self.owner, persistent=True)
        hero = json.loads((ROOT / 'tests/fixtures/native-hero24.json').read_text())['hero']
        self.proxy.profile = {'version': 1, 'heroes': {'24': hero}, 'migrations': [],
            'economy': {'version': 1, 'money': 10000, 'exp': 0, 'level': 1}, 'treasures': {'version': 1, 'items': []}}
        self.proxy.gacha = new_gacha_state()
        self.proxy.available_events = {}
        self.proxy.story.update(emergency=False, city_values={'dv': 5, 'av': 24, 'bf': 1000, 'fv': 50, 'ev': 0, 'rv': 5, 'pn': 1},
            city_areas={'1': {'id': 1, 'st': [0, False, False], 'lv': 1, 'bd': {}, 'stage': {'cs': 0, 'sl': [[101]]}},
                        '2': {'id': 2, 'st': [1, False, False], 'lv': 1, 'bd': {}, 'stage': {'cs': 1101, 'sl': [[1101]]}}},
            week_actions_spent=0)
        self.proxy.day.update(stock_day=0, actions_spent=0)
        self.proxy.save_progress()
        self.city = decode(json.loads((ROOT / 'tests/fixtures/offline_city_actions_cdata.json').read_text())['tables'])
        self.stage = json.loads((ROOT / 'tests/fixtures/offline_stage_cdata.json').read_text())
        self.week = decode(json.loads((ROOT / 'tests/fixtures/offline_week_cdata.json').read_text())['tables'])
        self._patch_active = False
        self.modules = {n: ModuleType(n) for n in ('common', 'common.IdManager', 'com', 'com.const', 'com.data', 'com.data.cdata')}
        self.engine = FakeEngine()
        self.modules['gg'] = self.engine
        self.ids = iter('%024x' % n for n in range(10000, 11000))
        self.modules['common.IdManager'].IdManager = SimpleNamespace(genid=lambda: next(self.ids), str2id=lambda uid: ('native', uid), id2str=str)
        self.modules['com.const'].CombatAttrs = SimpleNamespace(NAME_TO_INDEX={})
        self.modules['C_file'] = SimpleNamespace(find_res_file=lambda path, root: 'actual-fixture-resource')
        data = {'mission': {int(k): v for k, v in self.stage['missions'].items()},
            'city_data': {int(k): v for k, v in self.stage['city_data'].items()},
            'city_building': self.city['building'], 'city_development': self.city['development'],
            'city_upgrade': self.city['upgrade'], 'city_patrol': self.city['patrol'], 'hero': self.city['hero'],
            'event_content': {}, 'event_condition': {}, 'reward_common': {}, 'hero_treasure': {},
            'city_fight_reward': {1: self.stage['fight_reward_level1']}, 'player_exp': {int(k): v for k, v in self.stage['player_exp'].items()},
            'reward_random': {304: self.stage['reward_pool304']}, 'skin': {24: {'hero': 24, 'model_id': 24}}, 'ui_model_data': {}}
        for name, rows in data.items(): self.table(name, rows)
        context = patch.dict(sys.modules, self.modules)
        context.start()
        self._patch_active = True
        self.addCleanup(context.stop)

    def table(self, name, rows):
        module = ModuleType('com.data.cdata.' + name)
        module.data = rows
        self.modules[module.__name__] = module
        if self._patch_active:
            sys.modules[module.__name__] = module

    def test_real_calculator_stage1101_then_actual_finish_cost_reward_and_replay(self):
        # Select a lawful no-drop304 outcome; currency/exp/friendly still real.
        total = sum(w for r, w in self.stage['reward_pool304']['weights'])
        for n in range(2000, 3000):
            uid = '%024x' % n
            if int(hashlib.sha256(('stage-drop-v1:%s:304:0' % uid).encode()).hexdigest(), 16) % total < 147000:
                break
        self.modules['common.IdManager'].IdManager.genid = lambda: uid
        self.proxy.handle_battle_admission({'t': 1, 's': 1101, 'h': [24], 'd': {'a': 2}}, 7)
        admission = copy.deepcopy(self.proxy.battle['active'])
        self.assertIsNotNone(admission)
        self.assertEqual(self.owner.replies[-1][0], 'combatOfflineReply')
        self.assertEqual(self.owner.replies[-1][1]['c']['heroes'][str(('', 24))]['d']['_hp_delta'], 5)
        self.assertEqual(self.proxy.story['city_values']['av'], 24)
        result = {'t': 1, 's': 1101, 'h': [24], 'x': [], 'w': True, 'e': {}}
        self.proxy.handle_battle_finish(result, admission['fight_id'])
        self.assertIsNone(self.proxy.battle['active'])
        self.assertEqual(self.proxy.story['city_values']['av'], 22)
        self.assertEqual(self.proxy.day['actions_spent'], 2)
        self.assertEqual(self.proxy.story['city_areas']['2']['stage']['cs'], 1102)
        self.assertEqual(self.proxy.profile['economy'], {'version': 1, 'money': 13267, 'exp': 700, 'level': 2})
        self.assertEqual(self.proxy.profile['heroes']['24']['cf'], 95)
        before = self.proxy.progress_snapshot()
        self.proxy.handle_battle_finish(result, admission['fight_id'])
        self.assertEqual(self.proxy.progress_snapshot(), before)
        self.assertEqual(self.owner.replies[-1][0], 'combatOfflineReward')
        self.assertEqual(self.owner.replies[-1][1]['s'], 1101)

    def test_city_build_commit_precedes_native_id_reply_and_disk_failure_rolls_back(self):
        self.proxy.handle_city_action('areaBuildRequest', {'aid': 1, 'fi': 1, 'bi': 7, 'hs': [24]}, 'city:one', 9)
        building = self.proxy.story['city_areas']['1']['bd']['1']
        self.assertIsInstance(building['uuid'], str)
        native = [p for n, p in self.owner.replies if n == 'get_all_area_info_reply'][-1]
        self.assertEqual(native['ais']['area_1']['bd']['1']['uuid'], ('native', building['uuid']))
        self.assertEqual(self.proxy.story['city_areas']['1']['mbn'], 4)
        before = self.proxy.progress_snapshot()
        self.proxy.handle_city_action('areaBuildRequest', {'aid': 1, 'fi': 1, 'bi': 7, 'hs': [24]}, 'city:one', 10)
        self.assertEqual(before, self.proxy.progress_snapshot())
        with patch.object(self.proxy._store, 'write', side_effect=OSError('disk full')):
            with self.assertRaises(OSError):
                self.proxy.handle_city_action('areaBuildRequest', {'aid': 1, 'fi': 2, 'bi': 7, 'hs': [24]}, 'city:two', 11)
        self.assertEqual(before, self.proxy.progress_snapshot())
        self.assertFalse(self.owner.replies[-1][1]['rs'])
        self.assertEqual(self.owner.replies[-1][1]['_cbid_'], 11)

    def test_event_gate_precedes_real_start_and_actual_win_only_completes_bound_occurrence(self):
        sys.path.insert(0, str(ROOT / 'analysis/research-agent'))
        from read_data_table import read
        from read_literal_marshal import read as read_marshal
        content = read(ROOT / 'analysis/decompiled/event_content.py')
        missions = read_marshal(ROOT / 'analysis/android640-scripts/com/data/cdata/mission.marshal')
        self.table('mission', {104: missions[104]})
        self.table('event_content', {1: content[1], 40005: copy.deepcopy(content[1])})
        self.proxy.available_events = {1: 1}
        self.proxy.story['current_mission_wins'] = []
        self.proxy.save_progress()
        self.proxy.reliable_call({'w': {'m': 'startEvent', 'p': {'e': 1}, 'r': 1}, '_cbid_': 7})
        names = [name for name, p in self.owner.replies]
        self.assertLess(names.index('setEventBattleStage'), names.index('startEventReply'))
        self.assertEqual(offline_event_battle.event_battle_snapshot(self.proxy.progress_snapshot()), {'ab': [[104, 1]]})
        self.proxy.process_story('trace', {'k': 'dialog', 'd': {'c': 1}})
        self.proxy.processing_events.add(40005)
        state = self.proxy.progress_snapshot()
        gateway.begin_story_occurrence(state, 40005)
        self.proxy.restore_progress(state)
        self.proxy.save_progress()
        self.proxy.process_story('trace', {'k': 'dialog', 'd': {'c': 1}})
        total = sum(w for r, w in self.stage['reward_pool304']['weights'])
        for n in range(3000, 4000):
            uid = '%024x' % n
            if int(hashlib.sha256(('stage-drop-v1:%s:304:0' % uid).encode()).hexdigest(), 16) % total < 147000:
                break
        self.modules['common.IdManager'].IdManager.genid = lambda: uid
        self.proxy.handle_battle_admission({'t': 2, 's': 104, 'h': [24], 'd': {}}, 8)
        active = copy.deepcopy(self.proxy.battle['active'])
        self.assertEqual(active['event_id'], 1)
        self.assertEqual(active['event_occurrence'], '0:1:1')
        before_city = copy.deepcopy(self.proxy.story['city_areas'])
        self.proxy.handle_battle_finish({'t': 2, 's': 104, 'h': [24], 'x': [], 'w': True, 'e': {}}, active['fight_id'])
        self.assertIn(1, self.proxy.completed_events)
        self.assertEqual(self.proxy.story['current_mission_wins'], [104])
        self.assertIn(40005, self.proxy.processing_events)
        self.assertNotIn(40005, self.proxy.completed_events)
        self.assertEqual(self.proxy.story['city_areas'], before_city)
        self.assertEqual(offline_event_battle.event_battle_snapshot(self.proxy.progress_snapshot()), {'ab': []})

    def test_explicit_week_reset_preserves_assets_and_delivers_real_full_reload_wire(self):
        import zlib
        import msgpack
        from test_offline_week import ModelObjectId
        for key, name in (('events', 'event_content'), ('endings', 'ending_data'),
                ('routes', 'story_route'), ('scores', 'mainline_score_info'),
                ('building', 'city_building'), ('development', 'city_development'),
                ('missions', 'mission'), ('hero', 'hero'), ('items', 'item_data')):
            self.table(name, self.week[key])
        self.modules['common.IdManager'].IdManager.str2id = ModelObjectId
        self.proxy._snapshot_template = {'st': 100, 'name': 'old', 'an': 'offline', 'uid': 1,
            'sv': 1, 'role': 1, 'inv': {}, 'ldd': {}, 'std': {'cl': [999], 'srv': 50}}
        self.owner.luckyDrawData = SimpleNamespace(set_draw_info=lambda *a: None)
        profile = copy.deepcopy(self.proxy.profile)
        self.proxy.process_week_operation('handleResetWeekAsk', {}, source_week=0)
        self.assertEqual(self.proxy.story['week'], 1)
        self.assertTrue(self.proxy.week_protocol['awaiting_avatar'])
        self.assertEqual(self.proxy.profile, profile)
        self.assertEqual(self.owner.replies[-1][0], 'handleResetWeekReply')
        state = self.proxy.progress_snapshot()
        self.proxy.process_week_operation('handleResetWeekAsk', {}, source_week=0)
        self.assertEqual(self.proxy.progress_snapshot(), state)
        def pack(snapshot):
            return msgpack.packb(offline_avatar_snapshot.normalize_avatar_wire(snapshot),
                default=lambda obj: {'$oid': str(obj)} if isinstance(obj, ModelObjectId) else None, use_bin_type=False)
        with patch.object(gateway, 'pack_original_avatar', pack):
            self.proxy.process_week_operation('updateClientAvatarAsk', {})
        self.assertFalse(self.proxy.week_protocol['awaiting_avatar'])
        name, payload = self.owner.replies[-1]
        self.assertEqual(name, 'updateClientAvatarReply')
        decoded = msgpack.unpackb(zlib.decompress(payload['s']), raw=False, strict_map_key=False,
            object_hook=lambda item: ModelObjectId(item['$oid']) if '$oid' in item else item)
        offline_week.validate_full_week_avatar(decoded, self.proxy.progress_snapshot())
        self.assertEqual(decoded['std']['cl'], [])
        self.assertEqual(decoded['std']['srv'], 0)
        self.assertIsInstance(dict(decoded['heromgr']['hrs'])[24]['cs'], ModelObjectId)
        self.assertNotIn(1000, decoded['eventTrigger']['ecm'])
        self.assertEqual(decoded['eventTrigger']['ae'], [[1030, 1]])

if __name__ == '__main__': unittest.main()
