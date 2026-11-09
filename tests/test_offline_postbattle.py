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
from offline_story import initial_story_state, refresh_opening_triggers, prepare_opening_story, story_city_snapshot, story_reward_snapshot
from offline_postbattle import apply_first_battle_clearance, install_postbattle_ui_completion

class PostBattleTests(unittest.TestCase):
    def setUp(self):
        raw = json.loads((ROOT / 'tests/fixtures/opening-story.json').read_text())
        self.content = {int(k): v for k, v in raw['content'].items()}
        self.triggers = {int(k): dict(v, conds={int(n): value for n, value in v['conds'].items()}) for k, v in raw['triggers'].items()}
        self.rewards = {int(k): v for k, v in raw['rewards'].items()}
        self.missions = {int(k): v for k, v in raw['postbattle_missions'].items()}
        story = initial_story_state()
        story['emergency'] = False
        story['city_areas'] = {'1': {'id': 1, 'st': [1, False, False], 'lv': 1, 'bd': {}, 'stage': {'cs': 101, 'sl': [[101]]}}}
        self.state = {'story': story, 'available_events': [], 'processing_events': [],
                      'completed_events': [8, 1043], 'event_traces': [],
                      'battle': {'version': 1, 'active': None, 'receipts': [{'fight_id': 'actual-101', 'fingerprint': 'a' * 64,
                          'reply': {'t': 1, 's': 101, 'h': [24], 'x': [], 'r': {'money': 3267}, 'w': 1}}]}}

    def act(self, operation, arguments):
        self.state, notices = prepare_opening_story(self.state, operation, arguments, self.content, self.triggers, self.rewards)
        return notices

    def clearance(self):
        self.state, notices, changed = apply_first_battle_clearance(self.state, self.missions)
        refresh_opening_triggers(self.state, self.triggers)
        return notices

    def begin(self, event):
        self.state['available_events'] = [r for r in self.state['available_events'] if r[0] != event]
        self.state['processing_events'].append(event)
        return self.act('start', {'e': event})

    def test_only_accepted_win_clears_and_unlocks_once_with_silent_original_sync(self):
        loss = copy.deepcopy(self.state)
        loss['battle']['receipts'][0]['reply']['w'] = 0
        unchanged, notices, changed = apply_first_battle_clearance(loss, self.missions)
        self.assertEqual(loss, unchanged)
        self.assertFalse(changed)
        self.assertFalse(notices)
        notices = self.clearance()
        self.assertEqual(self.state['story']['city_areas']['1']['st'][0], 0)
        self.assertEqual(self.state['story']['city_areas']['1']['stage']['cs'], 101)
        self.assertEqual(self.state['story']['city_areas']['2']['stage'], {'cs': 1101, 'sl': [[1101]]})
        self.assertEqual(notices[0][0], 'get_all_area_info_reply')
        self.assertFalse(notices[0][1]['sm'])
        self.assertEqual(set(notices[0][1]['ais']), {'area_1', 'area_2'})
        self.assertIn(10000, dict(self.state['available_events']))
        self.state['story']['city_areas']['1']['st'][0] = 3  # A later independent city effect.
        before = copy.deepcopy(self.state)
        after, notices, changed = apply_first_battle_clearance(before, self.missions)
        self.assertEqual(after, before)
        self.assertFalse(changed)
        self.assertFalse(notices)

    def test_liberation_waits_for_actual_original_ui_callback_not_start_or_echo_trace(self):
        self.clearance()
        self.assertFalse(self.begin(10000))
        self.assertIn(10000, self.state['processing_events'])
        self.assertNotIn(10000, self.state['completed_events'])
        self.act('trace', {'k': 'ui', 'd': {'c': 10000}})
        self.assertNotIn(10000, self.state['completed_events'])
        notices = self.act('ui_complete', {'e': 10000})
        self.assertIn(('completeEventReplyEnd', {'e': 10000}), notices)
        self.assertIn(1007, dict(self.state['available_events']))
        before = copy.deepcopy(self.state)
        self.assertFalse(self.act('ui_complete', {'e': 10000}))
        self.assertEqual(self.state, before)

    def test_both_original_dialogue_choices_apply_blackcore_and_reach_1022(self):
        for branch in (1008, 1041):
            self.setUp()
            self.clearance()
            self.begin(10000)
            self.act('ui_complete', {'e': 10000})
            self.begin(1007)
            self.act('trace', {'k': 'dialog', 'd': {'c': 1007}})
            self.assertIn(1007, self.state['processing_events'])
            self.act('option', {'e': 1007, 'se': branch, 'op': 1})
            if branch == 1041:
                self.act('option', {'e': 1041, 'se': 1008, 'op': 1})
            self.act('option', {'e': 1008, 'se': 1009, 'op': 1})
            notices = self.act('trace', {'k': 'dialog', 'd': {'c': 1009}})
            self.assertIn(('updateBlackCore', {'c': 1, 'b': 1}), notices)
            self.assertEqual(dict(story_reward_snapshot(self.state['story'])['bc']), {1: 1})
            self.assertIn(1022, dict(self.state['available_events']))
            before = copy.deepcopy(self.state)
            self.assertFalse(self.act('trace', {'k': 'dialog', 'd': {'c': 1009}}))
            self.assertEqual(self.state, before)
            self.begin(1022)
            self.act('option', {'e': 1022, 'se': 1010, 'op': 1})
            self.assertIn(1010, self.state['processing_events'])

    def test_original_ui_observer_preserves_continuation_and_defers_durable_ack(self):
        calls, pending = [], []
        class Avatar:
            def startMovie(self, event):
                calls.append(('original-startMovie', event))
                return 'original-return'
        proxy = SimpleNamespace(defer=lambda delay, callback: pending.append(callback),
                                complete_story_ui=lambda event: calls.append(('durable-ui-ack', event)))
        avatar = Avatar()
        avatar.server = proxy
        module = ModuleType('entity.ClientAvatar')
        module.ClientAvatar = Avatar
        with patch.dict(sys.modules, {'entity': ModuleType('entity'), module.__name__: module}):
            install_postbattle_ui_completion()
            installed = Avatar.startMovie
            install_postbattle_ui_completion()
            self.assertIs(Avatar.startMovie, installed)
            self.assertEqual(avatar.startMovie(10000), 'original-return')
            self.assertEqual(calls, [('original-startMovie', 10000)])
            pending.pop()()
            self.assertEqual(calls[-1], ('durable-ui-ack', 10000))
            avatar.startMovie(8)
            self.assertFalse(pending)

    def test_ui_completion_failed_write_rolls_back_and_restart_can_replay_ui(self):
        from test_local_gateway import gateway, Owner
        self.clearance()
        self.begin(10000)
        modules = {n: ModuleType(n) for n in ('com', 'com.data', 'com.data.cdata', 'com.data.cdata.event_content', 'com.data.cdata.event_condition', 'com.data.cdata.reward_common', 'com.data.cdata.city_development')}
        modules['com.data.cdata.event_content'].data = self.content
        modules['com.data.cdata.event_condition'].data = self.triggers
        modules['com.data.cdata.reward_common'].data = self.rewards
        modules['com.data.cdata.city_development'].data = {}
        with tempfile.TemporaryDirectory() as folder, patch.dict(sys.modules, modules):
            gateway._f7_doc, gateway._f7_log = folder, lambda _: None
            owner = Owner()
            proxy = gateway.LocalProxy(None, owner, persistent=True)
            proxy.story = copy.deepcopy(self.state['story'])
            proxy.available_events, proxy.processing_events, proxy.completed_events = {}, {10000}, set(self.state['completed_events'])
            proxy.battle = copy.deepcopy(self.state['battle'])
            proxy.save_progress()
            before = proxy.progress_snapshot()
            with patch.object(proxy._store, 'write', side_effect=OSError('disk full')):
                with self.assertRaises(OSError):
                    proxy.complete_story_ui(10000)
            self.assertEqual(proxy.progress_snapshot(), before)
            self.assertFalse(owner.replies)
            restored = gateway.LocalProxy(None, owner, persistent=True)
            self.assertIn(10000, restored.processing_events)
            self.assertEqual(story_city_snapshot(restored.story)['areas']['area_1']['st'][0], 0)
            restored.complete_story_ui(10000)
            self.assertIn(10000, restored.completed_events)
            self.assertIn(1007, restored.available_events)
