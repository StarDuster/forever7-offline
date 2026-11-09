import copy
from pathlib import Path
import sys
import unittest
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'runtime'))
from offline_story import initial_story_state
from offline_story_engine import prepare_story_operation, refresh_story_events, begin_story_occurrence
from offline_gacha import new_gacha_state

class StoryEngineTests(unittest.TestCase):
    def setUp(self):
        self.state = {'story': initial_story_state(), 'profile': {'heroes': {},
            'economy': {'version': 1, 'money': 100, 'exp': 0, 'level': 1}},
            'gacha': new_gacha_state(), 'available_events': [], 'processing_events': [],
            'completed_events': [], 'event_traces': [], 'conditions': []}
        self.content = {40000: {'release': True, 'dialog': 42, 'completeConds': {'dialog': [42]}, 'events': [40001]},
            40001: {'release': True, 'dialog': 43, 'completeConds': {'dialog': [43]}, 'rewards': [7]},
            40002: {'release': True, 'ui': ['some_original_panel', 'method'], 'completeConds': {}},
            40003: {'release': True, 'client_event': 1, 'mutexEvent': [40004]},
            40004: {'release': True},
            40005: {'release': True, 'enterBattle': [1101], 'completeConds': {'battle': [1101]}}}
        self.tables = {'reward_common': {7: {'money': 5}}}

    def start(self, event):
        begin_story_occurrence(self.state, event)
        self.state['processing_events'].append(event)
        self.state, notices = self.step('start', {'e': event})
        return notices

    def step(self, operation, args):
        return prepare_story_operation(self.state, operation, args, self.content, {}, self.tables)

    def test_original_option_outside_opening_scope_preserves_parent_until_real_choice(self):
        self.start(40000)
        self.state, notices = self.step('trace', {'k': 'dialog', 'd': {'c': 42}})
        self.assertIn(40000, self.state['processing_events'])
        self.assertFalse(notices)
        self.state, notices = self.step('option', {'e': 40000, 'se': 40001, 'op': 1})
        self.assertIn(40000, self.state['completed_events'])
        self.assertIn(40001, self.state['processing_events'])
        self.assertEqual(notices[-1], ('startEventReply', {'e': 40001, 'r': 1}))
        self.state, notices = self.step('trace', {'k': 'dialog', 'd': {'c': 43}})
        self.assertEqual(self.state['profile']['economy']['money'], 105)
        repeated, notices = self.step('trace', {'k': 'dialog', 'd': {'c': 43}})
        self.assertEqual(repeated, self.state)
        self.assertEqual(notices, [])

    def test_empty_conditions_do_not_substitute_for_actual_ui_return(self):
        self.start(40002)
        self.assertIn(40002, self.state['processing_events'])
        self.state, _ = self.step('callback', {'e': 40002, 'token': 'ui:40002'})
        self.assertIn(40002, self.state['completed_events'])

    def test_unsupported_effect_retains_retryable_parent_without_partial_rewards(self):
        self.content[40000]['server_only_unknown'] = 1
        self.content[40000]['rewards'] = [7]
        self.start(40000)
        self.state, notices = self.step('option', {'e': 40000, 'se': 40001, 'op': 1})
        self.assertIn(40000, self.state['processing_events'])
        self.assertNotIn(40001, self.state['processing_events'])
        self.assertEqual(self.state['profile']['economy']['money'], 100)
        self.assertFalse(notices)

    def test_real_occurrences_get_separate_receipts_and_do_not_reuse_old_ui_proof(self):
        self.start(40002)
        self.state, _ = self.step('callback', {'e': 40002, 'token': 'ui:40002'})
        self.start(40002)
        self.assertIn(40002, self.state['processing_events'])
        self.assertNotIn(40002, self.state['completed_events'])
        self.assertEqual(self.state['story']['event_callbacks']['40002'], [])

    def test_external_uses_actual_release_client_event_mutex_and_dedicated_reply(self):
        self.state['completed_events'] = [40004]
        self.state, notices = self.step('external', {'e': 40003})
        self.assertNotIn(40003, self.state['completed_events'])
        self.assertIn(('triggerExternalEventReply', {}), notices)
        self.state['completed_events'] = []
        self.state, _ = self.step('external', {'e': 40003})
        self.assertIn(40003, self.state['completed_events'])
        ledger = copy.deepcopy(self.state['story']['event_effect_receipts'])
        self.state, _ = self.step('external', {'e': 40003})
        self.assertEqual(self.state['story']['event_effect_receipts'], ledger)

    def test_untrusted_battle_trace_never_awards_or_completes(self):
        self.start(40005)
        self.state, _ = self.step('trace', {'k': 'battle', 'd': {'c': 1101}})
        self.assertIn(40005, self.state['processing_events'])
        self.state, _ = self.step('combat_win', {'k': 'battle', 'd': {'c': 1101}, 'source_event': 40005, 'source_receipt': '0:40005:1'})
        self.assertIn(40005, self.state['completed_events'])

    def test_old_callback_cannot_finish_restarted_same_event_occurrence(self):
        self.start(40002)
        old = [0, self.state['story']['event_occurrences']['40002']]
        self.state, _ = self.step('callback', {'e': 40002, 'token': 'ui:40002', 'source_occurrence': old})
        self.start(40002)
        before = copy.deepcopy(self.state)
        self.state, notices = self.step('callback', {'e': 40002, 'token': 'ui:40002', 'source_occurrence': old})
        self.assertEqual(self.state, before)
        self.assertFalse(notices)

    def test_trigger_candidates_expire_on_route_change_but_explicit_patrol_choice_remains(self):
        triggers = {40001: {'release': True, 'conds': {52: "set(['1'])"}}}
        refresh_story_events(self.state, triggers, self.content)
        self.assertIn([40001, 1], self.state['available_events'])
        self.state['story']['route'] = '2'
        refresh_story_events(self.state, triggers, self.content)
        self.assertNotIn([40001, 1], self.state['available_events'])
        self.state['available_events'] = [[40001, 1]]
        self.state['city_actions'] = {'patrol': {'events': [40001]}}
        refresh_story_events(self.state, triggers, self.content)
        self.assertIn([40001, 1], self.state['available_events'])

    def test_all_original_trigger_rows_are_considered_with_known_false_short_circuit(self):
        triggers = {40001: {'release': True, 'conds': {1: 'set([40000])', 999: 'unknown'}},
                    40002: {'release': True, 'conds': {101: '1'}}}
        refresh_story_events(self.state, triggers, self.content)
        self.assertEqual(self.state['available_events'], [[40002, 1]])

if __name__ == '__main__':
    unittest.main()
