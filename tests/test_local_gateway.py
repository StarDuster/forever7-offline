import importlib.util
import json
from pathlib import Path
import sys
import tempfile
from types import ModuleType, SimpleNamespace
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
sys.path.insert(0, str(ROOT / 'runtime'))
from offline_store import OfflineSaveStore
from offline_wardrobe_completion import remaining_skin_resources_available
from offline_avatar_snapshot import native_city_snapshot, native_city_reply
from offline_city_actions import initial_city_actions_state, validate_city_actions_state, city_action_area_snapshot, select_city_patrol_event, complete_city_patrol_event
from offline_story_engine import prepare_story_operation, refresh_story_events, begin_story_occurrence
from offline_gacha import new_gacha_state
from offline_conditions import evaluate_offline_condition
from offline_event_battle import prepare_event_battle_gate, event_battle_snapshot
from offline_story_engine import story_occurrence_key
from offline_week import initial_week_state, validate_week_state
from offline_day import initial_day_state, validate_day_state, offline_city_defaults, build_offline_daily_plan, prepare_gateway_day_operation
from offline_postbattle import apply_first_battle_clearance
from offline_transport import schedule_local_rpc, install_local_purge_recovery
from offline_battle import initial_battle_state, validate_battle_state, offer_pending_battle_resume
from offline_story import initial_story_state, refresh_opening_triggers, prepare_opening_story, prepare_starter_choice, offer_story_starter_choice, story_city_snapshot, story_reward_snapshot, scan_nextday_story_events, story_week_snapshot, show_day_pending_notice, merge_client_operations
from offline_profile import validate_hero_profile
from offline_gacha import validate_gacha_state, prepare_gacha_group, open_gacha_cards

spec = importlib.util.spec_from_file_location('gateway_under_test', ROOT / 'runtime/local_gateway.py')
gateway = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gateway)
gateway.OfflineSaveStore = OfflineSaveStore
gateway.validate_hero_profile = validate_hero_profile
gateway.validate_gacha_state = validate_gacha_state
gateway.SKIP_TUTORIAL_UI = True
gateway.new_gacha_state = new_gacha_state
gateway.prepare_story_operation = prepare_story_operation
gateway.refresh_story_events = refresh_story_events
gateway.begin_story_occurrence = begin_story_occurrence
gateway.native_city_snapshot = native_city_snapshot
gateway.native_city_reply = native_city_reply
gateway.initial_city_actions_state = initial_city_actions_state
gateway.validate_city_actions_state = validate_city_actions_state
gateway.city_action_area_snapshot = city_action_area_snapshot
gateway.select_city_patrol_event = select_city_patrol_event
gateway.complete_city_patrol_event = complete_city_patrol_event
gateway.evaluate_offline_condition = evaluate_offline_condition
gateway.prepare_event_battle_gate = prepare_event_battle_gate
gateway.event_battle_snapshot = event_battle_snapshot
gateway.story_occurrence_key = story_occurrence_key
gateway.initial_week_state = initial_week_state
gateway.validate_week_state = validate_week_state
gateway.initial_day_state = initial_day_state
gateway.validate_day_state = validate_day_state
gateway.offline_city_defaults = offline_city_defaults
gateway.build_offline_daily_plan = build_offline_daily_plan
gateway.prepare_gateway_day_operation = prepare_gateway_day_operation
gateway.scan_nextday_story_events = scan_nextday_story_events
gateway.story_week_snapshot = story_week_snapshot
gateway.show_day_pending_notice = show_day_pending_notice
gateway.merge_client_operations = merge_client_operations
gateway.remaining_skin_resources_available = remaining_skin_resources_available
gateway.schedule_local_rpc = schedule_local_rpc
gateway.install_local_purge_recovery = install_local_purge_recovery
gateway.initial_battle_state = initial_battle_state
gateway.validate_battle_state = validate_battle_state
gateway.offer_pending_battle_resume = offer_pending_battle_resume
gateway.initial_story_state = initial_story_state
gateway.refresh_opening_triggers = refresh_opening_triggers
gateway.prepare_opening_story = prepare_opening_story
gateway.prepare_starter_choice = prepare_starter_choice
gateway.offer_story_starter_choice = offer_story_starter_choice
gateway.story_city_snapshot = story_city_snapshot
gateway.story_reward_snapshot = story_reward_snapshot
gateway.apply_first_battle_clearance = apply_first_battle_clearance


class Owner:
    def __init__(self):
        self.name = 'Before'
        self.replies = []

    def __getattr__(self, method):
        return lambda parameters: self.replies.append((method, parameters))


class LocalGatewayTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        data = json.loads((ROOT / 'tests/fixtures/opening-events.json').read_text())
        cls.events = {int(key): value for key, value in data['rows'].items()}

    def setUp(self):
        self.folder = tempfile.TemporaryDirectory()
        self.addCleanup(self.folder.cleanup)
        gateway._f7_doc = self.folder.name
        gateway._f7_log = lambda _: None
        self.owner = Owner()
        self.proxy = gateway.LocalProxy(None, self.owner, persistent=True)
        event_patch = self.install_event_data()
        event_patch.start()
        self.addCleanup(event_patch.stop)

    def rpc(self, name, arguments, callback=7, sequence=1):
        self.proxy.reliable_call({'w': {'m': name, 'p': arguments, 'r': sequence}, '_cbid_': callback})

    def install_event_data(self):
        modules = {name: ModuleType(name) for name in (
            'com', 'com.data', 'com.data.cdata', 'com.data.cdata.event_content',
            'com.data.cdata.event_condition', 'com.data.cdata.reward_common', 'com.data.cdata.city_development', 'com.data.cdata.notepad')}
        modules['com.data.cdata.notepad'].data = {10044: {'type': 1}}
        modules['com.data.cdata.city_development'].data = {}
        # Fresh seed admission exempts only original predecessor6; keep its
        # actual remaining trigger facts in the gateway fixture.
        original = json.loads((ROOT / 'tests/fixtures/opening-story.json').read_text())['triggers']['1000']
        modules['com.data.cdata.event_condition'].data = {1000: dict(original,
            conds={int(kind): value for kind, value in original['conds'].items()})}
        modules['com.data.cdata.reward_common'].data = {}
        modules['com.data.cdata.event_content'].data = self.events
        return patch.dict(sys.modules, modules)

    def test_original_telemetry_reads_native_gate_object_and_world_identifiers(self):
        import ast
        source = (ROOT/'analysis/dctool_log-original.py').read_text()
        function = next(node for node in ast.parse(source).body if isinstance(node, ast.FunctionDef) and node.name == '_dctool_log')
        calls = []
        dctool = SimpleNamespace(start_dctool=lambda payload:calls.append(json.loads(payload)))
        gg = SimpleNamespace(platform='android', channel_loginname='offline',
            server_current=gateway.LocalWorld(), avatar=SimpleNamespace(userid='actual-local-user'))
        namespace = {'gg':gg, 'game3d':SimpleNamespace(PLATFORM_WIN32='win32'),
            'const':SimpleNamespace(DEBUG=False, DCTOOL_GAME='original-game'),
            'json':json, 'logger':SimpleNamespace(info=lambda _:None)}
        code = compile(ast.Module(body=[function], type_ignores=[]), 'original_dctool_contract', 'exec')
        with patch.dict(sys.modules, {'dctool':dctool}):
            exec(code, namespace)
            namespace['_dctool_log']('battle_finish', {'result':'actual'})
        self.assertEqual(len(calls), 1)
        self.assertEqual(calls[0]['ServerIP'], '127.0.0.1')
        self.assertEqual(calls[0]['ServerPort'], 18767)
        self.assertEqual(calls[0]['GroupId'], '1')
        self.assertEqual(calls[0]['ServerName'], '1')
        self.assertEqual(calls[0]['UserName'], 'actual-local-user')
        self.assertEqual(gg.server_current.region.gate_next(), ('127.0.0.1',18767))

    def test_gacha_commit_failure_rolls_back_reward_and_pending_card_together(self):
        state, _ = prepare_gacha_group(None, [24], lambda n: 0, lambda h: {4253: 3})
        self.proxy.gacha = state
        self.proxy.save_progress()
        candidate, _, _ = open_gacha_cards(state, [0], lambda: '0' * 24, lambda item: 99)
        self.proxy.gacha = candidate
        with patch.object(self.proxy._store, 'write', side_effect=OSError('disk full')):
            with self.assertRaises(OSError):
                self.proxy.save_progress()
        self.assertEqual(self.proxy.gacha, state)
        restored = gateway.LocalProxy(None, Owner(), persistent=True)
        self.assertEqual(restored.gacha, state)
        self.assertFalse(self.owner.replies)

    def test_unknown_gacha_policy_is_not_silently_reset_or_accepted(self):
        self.proxy.gacha, _ = prepare_gacha_group(None, [24], lambda n: 0, lambda h: {})
        self.proxy.save_progress()
        self.proxy.gacha['policy'] = 'future-unknown-policy'
        with self.assertRaises(ValueError):
            self.proxy.save_progress()
        self.assertEqual(self.proxy.gacha['policy'], 'local-uniform-owned-heroes-free-v1')

    def test_summon_feature_gate_allows_original_configured_pools_and_rejects_unknown(self):
        pending = []
        tab = SimpleNamespace(valid=True, draw_type=1)
        fake_gg = SimpleNamespace(exec_delay=lambda delay, callback: pending.append(callback),
                                  ui=SimpleNamespace(panels=SimpleNamespace(card_tab=tab)))
        package, const = ModuleType('com'), ModuleType('com.const')
        package.const = const
        const.GamePlayName = SimpleNamespace(SUMMON='summonCard', FRIENDSUMMON='friendSummon')
        const.LuckyDrawType = SimpleNamespace(NORMAL=1)
        catalog = ModuleType('com.data.cdata.chouka_info'); catalog.data = {1: {'drawType': 1}, 354: {'drawType': 354}}
        data_package, cdata_package = ModuleType('com.data'), ModuleType('com.data.cdata')
        package.data = data_package; data_package.cdata = cdata_package; cdata_package.chouka_info = catalog
        with patch.dict(sys.modules, {'gg': fake_gg, 'com': package, 'com.const': const, 'com.data': data_package, 'com.data.cdata': cdata_package, 'com.data.cdata.chouka_info': catalog}):
            self.proxy.call_server_method('checkGamePlaySwitchAsk', {'g': 'friendSummon'})
            self.assertFalse(self.owner.replies)
            pending.pop()()
            self.assertEqual(self.owner.replies[-1][1]['s'], 1)
            for configured in (99,):
                tab.draw_type = configured
                self.proxy.call_server_method('checkGamePlaySwitchAsk', {'g': 'friendSummon'})
                pending.pop()()
                self.assertEqual(self.owner.replies[-1][1]['s'], 1)
            tab.draw_type = 354
            self.proxy.call_server_method('checkGamePlaySwitchAsk', {'g': 'friendSummon'})
            pending.pop()()
            self.assertEqual(self.owner.replies[-1][1]['s'], 0)
            tab.draw_type = 2
            self.proxy.call_server_method('checkGamePlaySwitchAsk', {'g': 'friendSummon'})
            pending.pop()()
            self.assertEqual(self.owner.replies[-1][1]['s'], 0)
            self.proxy.call_server_method('checkGamePlaySwitchAsk', {'g': 'summonCard'})
            pending.pop()()
            self.assertEqual(self.owner.replies[-1][1]['s'], 1)

    def test_name_and_in_progress_event_survive_gateway_recreation(self):
        self.proxy.set_player_name({'n': 'Local', 'in': True})
        self.rpc('startEvent', {'e': 1000})
        restored = gateway.LocalProxy(None, Owner(), persistent=True)
        self.assertEqual(restored.player_name, 'Local')
        self.assertEqual(restored.processing_events, {1000})
        self.assertNotIn(1000, restored.available_events)
        self.proxy = restored
        # Session suppression now requires actual original client acceptance,
        # rather than merely recording a serialized successful reply.
        client = set()
        restored.owner.eventTriggerData = SimpleNamespace(processingEventsClient=client)
        def accept_start(parameters):
            restored.owner.replies.append(('startEventReply',parameters))
            if parameters['r']: client.add(parameters['e'])
        restored.owner.startEventReply = accept_start
        native = patch.dict(sys.modules,{'gg':SimpleNamespace(avatar=restored.owner,logic=SimpleNamespace(event_valid=True))})
        native.start();self.addCleanup(native.stop)
        self.rpc('startEvent', {'e': 1000})
        self.assertTrue(any(method == 'startEventReply' and params['r'] == 1
                            for method, params in restored.owner.replies))
        restored.owner.replies.clear()
        self.rpc('startEvent', {'e': 1000}, sequence=2)
        self.assertFalse(any(method == 'startEventReply' for method, _ in restored.owner.replies))

    def test_real_opening_event_completion_is_durable_and_cannot_start_twice(self):
        self.rpc('startEvent', {'e': 1000})
        with self.install_event_data():
            self.proxy.trace_event({'k': 'dialog', 'd': {'c': 1000}})
        restored_owner = Owner()
        self.proxy = gateway.LocalProxy(None, restored_owner, persistent=True)
        self.assertEqual(self.proxy.completed_events, {1000})
        self.rpc('startEvent', {'e': 1000})
        self.assertIn(('startEventReply', {'e': 1000, 'r': 0, '_cbid_': 7}), restored_owner.replies)

    def test_reward_event_remains_pending_until_reward_logic_exists(self):
        self.proxy.available_events = {1001: 1}
        self.proxy.save_progress()
        self.rpc('startEvent', {'e': 1001})
        with self.install_event_data():
            self.proxy.trace_event({'k': 'dialog', 'd': {'c': 1001}})
        self.assertIn(1001, self.proxy.processing_events)
        self.assertNotIn(1001, self.proxy.completed_events)
        self.assertFalse(any(method == 'completeEventReplyEnd' for method, _ in self.owner.replies))

    def test_disk_failure_rolls_back_event_and_never_reports_business_success(self):
        with patch.object(self.proxy._store, 'write', side_effect=OSError('disk full')):
            with self.assertRaises(OSError):
                self.rpc('startEvent', {'e': 1000})
        self.assertIn(1000, self.proxy.available_events)
        self.assertFalse(self.proxy.processing_events)
        self.assertEqual(self.owner.replies, [('reliableRpcAck', {'s': 1}), ('startEventReply', {'e': 1000, 'r': 0, '_cbid_': 7})])
        self.assertIn(1000, gateway.LocalProxy(None, Owner(), persistent=True).available_events)

    def test_disk_failure_does_not_change_player_name_or_send_success(self):
        with patch.object(self.proxy._store, 'write', side_effect=OSError('disk full')):
            with self.assertRaises(OSError):
                self.proxy.set_player_name({'n': 'Changed'})
        self.assertEqual(self.owner.name, 'Before')
        self.assertIsNone(self.proxy.player_name)
        self.assertFalse(self.owner.replies)

    def test_unknown_rpc_is_not_a_successful_business_call(self):
        self.rpc('unknownFutureOperation', {'cost': 999})
        self.assertEqual(self.owner.replies, [('reliableRpcAck', {'s': 1})])

    def test_known_pending_teaching_request_completes_its_callback_when_teaching_disabled(self):
        self.rpc('clientAskTriggerNewbee', {'e': 172})
        self.assertEqual(self.owner.replies, [('reliableRpcAck', {'s': 1}),
                         ('serverCallbackCarrier', {'_r_': {}, '_cbid_': 7})])
        self.assertFalse(self.proxy.completed_events)

    def install_hero_profile(self):
        hero = json.loads((ROOT / 'tests/fixtures/native-hero24.json').read_text())['hero']
        ids = {skin['i']: instance for instance, skin in hero['sk'].items()}
        hero['cs'] = ids[24]
        self.proxy.profile = {'version': 1, 'heroes': {'24': hero}, 'migrations': []}
        self.proxy.save_progress()
        return ids

    def test_skin_change_is_saved_before_success_callback_and_survives_recreation(self):
        ids = self.install_hero_profile()
        self.proxy.set_skin({'h': 24, 'sid': ids[10023], '_cbid_': 9})
        self.assertEqual(self.owner.replies, [('setSkinReply', {'s': True, 'sid': ids[10023], 'ass': False, '_cbid_': 9})])
        restored = gateway.LocalProxy(None, Owner(), persistent=True)
        self.assertEqual(restored.profile['heroes']['24']['cs'], ids[10023])

    def test_skin_instance_cannot_be_selected_for_another_hero(self):
        ids = self.install_hero_profile()
        self.proxy.set_skin({'h': 20, 'sid': ids[10023], '_cbid_': 9})
        self.assertFalse(self.owner.replies[0][1]['s'])
        self.assertEqual(self.proxy.profile['heroes']['24']['cs'], ids[24])

    def test_skin_save_failure_preserves_previous_selection_without_success_reply(self):
        ids = self.install_hero_profile()
        with patch.object(self.proxy._store, 'write', side_effect=OSError('disk full')):
            with self.assertRaises(OSError):
                self.proxy.set_skin({'h': 24, 'sid': ids[10023], '_cbid_': 9})
        self.assertEqual(self.proxy.profile['heroes']['24']['cs'], ids[24])
        self.assertEqual(self.owner.replies, [('setSkinReply', {'s': False, 'sid': ids[10023], 'ass': False, '_cbid_': 9})])

    def test_development_probe_reinstalls_after_original_city_entry_only_when_opted_in(self):
        pending, entered = [], []
        class Logic:
            def gs_enter_city(self, *args, **kwargs):
                entered.append((args, kwargs))
                return 'original-city'
        logic = Logic()
        original_bound = logic.gs_enter_city
        logic.game_state = SimpleNamespace(_cb={6: {'enter': {'func': original_bound}}})
        fake_gg = SimpleNamespace(logic=logic, exec_delay=lambda delay, callback: pending.append(callback))
        const = ModuleType('com.const')
        const.GameState = SimpleNamespace(CITY=6)
        with patch.dict(sys.modules, {'gg': fake_gg, 'com.const': const}):
            original = Logic.gs_enter_city
            gateway.install_development_probe()
            self.assertIs(Logic.gs_enter_city, original)
            Path(self.folder.name, 'offline_development.flag').touch()
            gateway.install_development_probe()
            self.assertEqual(len(pending), 1)
            old_poll = pending.pop()
            self.assertIs(Logic.gs_enter_city, original)
            self.assertEqual(logic.game_state._cb[6]['enter']['func']('source', ud={'scene': 'city'}), 'original-city')
            self.assertEqual(entered, [(('source',), {'ud': {'scene': 'city'}})])
            self.assertEqual(len(pending), 1)
            old_poll()
            self.assertEqual(len(pending), 1)

    def test_reliable_pull_survives_scene_purge_with_one_ack_and_business_callback(self):
        from test_offline_transport import FakeEngine
        engine = FakeEngine()
        with patch.dict(sys.modules, {'gg': engine}):
            self.proxy.call_server_method('reliableRpcCall', {'w': {'m': 'pullEvents', 'p': {}, 'r': 13}, '_cbid_': 17})
            self.assertFalse(self.owner.replies)
            engine.exec_cancel_all()
            engine.exec_cancel_all()
            engine.drain()
            self.assertEqual(self.owner.replies, [
                ('reliableRpcAck', {'s': 13}),
                ('pullEventsReply', {'a': self.proxy.available_events.items(), 'p': [], '_cbid_': 17})])
            engine.exec_cancel_all()
            engine.drain()
            self.assertEqual(len(self.owner.replies), 2)

    def test_login_replacement_and_destroy_invalidate_old_pending_calls(self):
        from test_offline_transport import FakeEngine
        engine, seen = FakeEngine(), []
        with patch.dict(sys.modules, {'gg': engine}), patch.object(gateway, 'create_avatar', side_effect=lambda logic: seen.append('login')):
            self.proxy.defer(1, lambda: seen.append('old-request'))
            self.proxy.call_server_method('login')
            self.proxy.call_server_method('login')
            engine.exec_cancel_all()
            engine.drain()
            self.assertEqual(seen, ['login'])
            self.proxy.defer(1, lambda: seen.append('destroyed-request'))
            self.proxy.destroy()
            engine.exec_cancel_all()
            engine.drain()
            self.assertEqual(seen, ['login'])

    def test_recreated_city_uses_stock_area_keys_and_both_query_callbacks(self):
        area = {'id': 1, 'st': [1, False, False], 'lv': 1, 'bd': {}, 'stage': {'cs': 101, 'sl': [[101]]}}
        self.proxy.story['city_areas'] = {'1': area}
        self.proxy.save_progress()
        restored = gateway.LocalProxy(None, self.owner, persistent=True)
        city = gateway.story_city_snapshot(restored.story)
        self.assertEqual(city['areas'].get('area_%d' % 1), area)
        self.assertNotIn(1, city['areas'])
        self.assertNotIn('1', city['areas'])
        restored.reply_city_areas('getAreaInfoRequest', {'id': 1, '_cbid_': 3})
        self.assertEqual(self.owner.replies[-1], ('get_area_info_reply', {'ai': area, '_cbid_': 3}))
        restored.reply_city_areas('getAllAreaInfoRequest', {'_cbid_': 4})
        self.assertEqual(self.owner.replies[-1][0], 'get_all_area_info_reply')
        self.assertEqual(self.owner.replies[-1][1]['ais'], {'area_1': area})
        self.assertFalse(self.owner.replies[-1][1]['sm'])
        self.assertEqual(self.owner.replies[-1][1]['_cbid_'], 4)
        self.assertEqual(restored.story['city_areas'], {'1': area})


if __name__ == '__main__':
    unittest.main()
