import copy
import json
from pathlib import Path
import sys
import tempfile
from types import ModuleType, SimpleNamespace
import unittest
from unittest.mock import patch
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'runtime'))
sys.path.insert(0, str(ROOT / 'analysis/research-agent'))
from read_literal_marshal import read
from offline_day import offline_city_defaults
from offline_story import evaluate_story_condition, merge_client_operations, scan_nextday_story_events, story_week_snapshot, story_city_snapshot
from test_local_gateway import gateway, Owner
from test_offline_transport import FakeEngine

class DayGatewayTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        base = ROOT / 'analysis/android640-scripts/com/data/cdata'
        cls.fatigue = read(base / 'fatigue_recover.marshal')
        cls.upgrades = read(base / 'city_upgrade.marshal')

    def setUp(self):
        self.folder = tempfile.TemporaryDirectory()
        self.addCleanup(self.folder.cleanup)
        gateway._f7_doc, gateway._f7_log = self.folder.name, lambda _: None
        self.owner = Owner()
        self.owner.weeknumData = SimpleNamespace(weeknum=0, daynum=0)
        def update_day(data):
            self.owner.weeknumData.daynum = data['d']
            self.owner.replies.append(('updateDay', data))
        self.owner.updateDay = update_day
        self.proxy = gateway.LocalProxy(None, self.owner, persistent=True)
        hero = json.loads((ROOT / 'tests/fixtures/native-hero24.json').read_text())['hero']
        hero['cf'] = 95
        self.proxy.profile = {'version': 1, 'heroes': {'24': hero}, 'migrations': [],
                              'economy': {'version': 1, 'money': 10000, 'exp': 0, 'level': 1}}
        self.proxy.story.update(emergency=False, route='1', city_values=offline_city_defaults(),
            city_areas={'1': {'id': 1, 'st': [0, False, False], 'lv': 1, 'bd': {}, 'stage': {'cs': 101, 'sl': [[101]]}}})
        self.proxy.available_events = {}
        self.proxy.save_progress()
        self.engine = FakeEngine()
        self.modules = {n: ModuleType(n) for n in ('com', 'com.const', 'com.data', 'com.data.cdata')}
        self.modules['gg'] = self.engine
        data = {'event_content': {1010: {'release': True, 'dialog': 1010, 'completeConds': {'dialog': [1010]}, 'newbee_event': 30}},
                'event_condition': {}, 'reward_common': {}, 'fatigue_recover': self.fatigue, 'city_upgrade': self.upgrades, 'city_development': {}}
        for name, rows in data.items():
            module = ModuleType('com.data.cdata.' + name)
            module.data = rows
            self.modules[module.__name__] = module
        context = patch.dict(sys.modules, self.modules)
        context.start()
        self.addCleanup(context.stop)

    def arm(self):
        self.proxy.process_day_operation('statusCheck', {'s': 'nextday'}, 7)
        self.assertEqual(self.owner.replies[-1][1]['r'], 'ok')
        self.proxy.process_day_operation('updateEventCondClient', {'c': 102, 'v': '4'}, 8)
        self.assertEqual(self.proxy.conditions[102], 4)
        self.assertEqual(self.proxy.day['intent']['phase'], 'clientop')

    def test_native_flow_commits_real_policy_then_replays_without_double_income(self):
        self.arm()
        before_money = copy.deepcopy(self.proxy.profile['economy'])
        self.proxy.call_server_method('incDayWhenNoActionVal', {})
        self.engine.exec_cancel_all()
        self.engine.drain()
        self.assertEqual(self.proxy.day['stock_day'], 1)
        self.assertEqual(self.proxy.story['date'], 1)
        self.assertEqual(self.proxy.story['city_values']['av'], 24)
        self.assertEqual(self.proxy.story['city_values']['bf'], 50)
        self.assertEqual(self.proxy.profile['heroes']['24']['cf'], 100)
        self.assertEqual(self.proxy.profile['heroes']['24']['ef'], 0)
        self.assertEqual(self.proxy.profile['economy'], before_money)
        self.assertNotIn(102, self.proxy.conditions)
        names = [name for name, args in self.owner.replies]
        self.assertLess(names.index('get_city_data_reply'), names.index('updateDay'))
        self.assertLess(names.index('updateDay'), names.index('showDailySettlement'))
        saved = self.proxy.progress_snapshot()
        revision = self.proxy._store.revision
        self.proxy.process_day_operation('incDayWhenNoActionVal', {}, source_context=(0, 0))
        self.assertEqual(self.proxy.progress_snapshot(), saved)
        self.assertEqual(self.proxy._store.revision, revision)
        restored = gateway.LocalProxy(None, self.owner, persistent=True)
        self.assertEqual(story_week_snapshot(restored.story, restored.day)['d'], 1)
        self.assertEqual(story_city_snapshot(restored.story)['av'], 24)
        self.proxy.call_server_method('clearCurDailySettlement', {})
        self.engine.drain()
        self.assertIsNone(self.proxy.day['review'])
        self.assertTrue(self.proxy.day['previous_values'])
        self.assertEqual(self.proxy.profile['economy'], before_money)

    def test_failed_save_preserves_true_day_and_only_resynchronizes_unchanged_day(self):
        self.arm()
        before = self.proxy.progress_snapshot()
        self.owner.replies.clear()
        with patch.object(self.proxy._store, 'write', side_effect=OSError('disk full')):
            with self.assertRaises(OSError):
                self.proxy.process_day_operation('incDayWhenNoActionVal', {}, source_context=(0, 0))
        self.assertEqual(self.proxy.progress_snapshot(), before)
        self.assertEqual(self.owner.replies, [('updateDay', {'d': 0})])
        self.assertFalse(any(name == 'showDailySettlement' for name, args in self.owner.replies))
        self.engine.drain()

    def test_actual_pending_dialogue_blocks_inc_until_original_trace_completes_it(self):
        self.arm()
        self.proxy.processing_events.add(1010)
        self.proxy.save_progress()
        self.owner.replies.clear()
        self.proxy.process_day_operation('incDayWhenNoActionVal', {}, source_context=(0, 0))
        self.assertEqual(self.proxy.day['stock_day'], 0)
        self.assertEqual(self.proxy.story['city_values']['bf'], 0)
        self.assertIn(1010, self.proxy.processing_events)
        self.proxy.process_story('trace', {'k': 'dialog', 'd': {'c': 1010}}, 11)
        self.assertIn(1010, self.proxy.completed_events)
        self.proxy.process_day_operation('incDayWhenNoActionVal', {}, source_context=(0, 0))
        self.assertEqual(self.proxy.day['stock_day'], 1)

    def test_known_false_route_prunes_unknown_and_clientop_is_original_allset(self):
        state = self.proxy.progress_snapshot()
        state['conditions'] = [[102, 4]]
        self.assertFalse(evaluate_story_condition(102, 'set([4,5])', state))
        state['conditions'] = [[102, merge_client_operations(4, 5)]]
        self.assertTrue(evaluate_story_condition(102, 'set([4,5])', state))
        self.assertTrue(evaluate_story_condition(4, '[0,)', state))
        self.assertFalse(evaluate_story_condition(4, '(0,)', state))
        table = {9001: {'release': True, 'conds': {52: "set(['12'])", 102: 'set([4])', 999: 'unknown'}}}
        candidate, blockers = scan_nextday_story_events(state, {}, table)
        self.assertFalse(blockers)
        table[9001]['conds'][52] = "set(['1'])"
        candidate, blockers = scan_nextday_story_events(state, {}, table)
        self.assertEqual(blockers[0]['conditions'], [999])

    def test_reachable_unknown_preflight_rejects_before_status_success(self):
        self.modules['com.data.cdata.event_condition'].data = {
            9001: {'release': True, 'conds': {52: "set(['1'])", 102: 'set([4])', 999: 'unknown'}}}
        self.proxy.process_day_operation('statusCheck', {'s': 'nextday'}, 7)
        self.assertEqual(self.owner.replies[-1][1]['r'], 'event')
        self.assertIsNone(self.proxy.day['intent'])
        self.assertNotIn(102, self.proxy.conditions)
