"""Focused contracts for the offline code20 committed-action ledger."""
import copy
import json
import sys
import unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'runtime'))
sys.path.insert(0, str(ROOT / 'tools'))
sys.path.insert(0, str(ROOT / 'tests'))
from offline_action_ledger import (ACTION_LEDGER_INVALID_POLICY, ACTION_LEDGER_POLICY,
    action_spent_since_event, code20_condition_values, initial_action_ledger,
    invalidate_action_ledger, next_week_action_ledger, record_committed_spend,
    set_event_baseline, validate_action_ledger)
from offline_conditions import evaluate_offline_condition as cond


def state(week=3, av=24, spent=0, ledger=True):
    value = {'story': {'version': 1, 'week': week, 'date': 2, 'route': '5',
                       'city_values': {'av': av}}, 'completed_events': [],
             'processing_events': [], 'day': {'stock_day': 1}}
    if ledger:
        value['story']['action_ledger'] = initial_action_ledger()
        if spent:
            value['story']['action_ledger']['spent'] = spent
    return value


class ActionLedgerTests(unittest.TestCase):
    def test_policy_and_shape_are_explicit(self):
        ledger = initial_action_ledger()
        self.assertEqual(ledger['policy'], ACTION_LEDGER_POLICY)
        validate_action_ledger(ledger)
        broken = [None, {}, dict(ledger, version=2), dict(ledger, policy='x'),
                  dict(ledger, generation=0), dict(ledger, spent=-1),
                  dict(ledger, spent=True), dict(ledger, baselines=[]),
                  dict(ledger, receipts=[{'id': 'a', 'spent': 0, 'total': 0}]),
                  dict(ledger, baselines={'510': {'week': 1, 'spent': 1,
                                                  'generation': 1}})]
        for value in broken:
            with self.assertRaises(ValueError):
                validate_action_ledger(value)

    def test_commit_counts_only_observed_accepted_charge(self):
        value = state()
        self.assertTrue(record_committed_spend(value, 2, 'city:one'))
        self.assertEqual(value['story']['action_ledger']['spent'], 2)
        self.assertTrue(record_committed_spend(value, 3))
        self.assertEqual(action_spent_since_event(value, 510), None)
        set_event_baseline(value, 510, 3)
        self.assertEqual(action_spent_since_event(value, 510), 0)
        self.assertTrue(record_committed_spend(value, 3))
        self.assertEqual(action_spent_since_event(value, 510), 3)
        self.assertEqual(value['story']['action_ledger']['receipts'],
                         [{'id': 'city:one', 'spent': 2, 'total': 2}])

    def test_duplicate_and_retry_receipts_never_double_charge(self):
        value = state()
        self.assertTrue(record_committed_spend(value, 2, 'battle:f1'))
        self.assertFalse(record_committed_spend(value, 2, 'battle:f1'))
        self.assertEqual(value['story']['action_ledger']['spent'], 2)
        with self.assertRaises(ValueError):
            record_committed_spend(value, 1, 'battle:f1')
        self.assertEqual(value['story']['action_ledger']['spent'], 2)
        # A retry after the state advanced observes a zero av delta and never
        # calls the ledger at all; amount zero is a no-op here.
        self.assertFalse(record_committed_spend(value, 0, 'battle:f2'))
        self.assertEqual(value['story']['action_ledger']['spent'], 2)
        for bad in (-1, 1.0, True, '1'):
            with self.assertRaises(ValueError):
                record_committed_spend(value, bad, 'bad')

    def test_completion_baseline_is_week_scoped_and_repeatable(self):
        value = state(week=3)
        record_committed_spend(value, 5)
        set_event_baseline(value, 510, 3)
        record_committed_spend(value, 4)
        self.assertEqual(action_spent_since_event(value, 510), 4)
        # A genuine repeat completion moves the baseline to the current spend.
        set_event_baseline(value, 510, 3)
        self.assertEqual(action_spent_since_event(value, 510), 0)
        record_committed_spend(value, 1)
        self.assertEqual(action_spent_since_event(value, 510), 1)
        self.assertEqual(value['story']['action_ledger']['baselines']['510'],
                         {'week': 3, 'spent': 9, 'generation': 1})

    def test_reload_preserves_ledger_and_fact(self):
        value = state()
        value['completed_events'] = [510]
        record_committed_spend(value, 2, 'city:one')
        set_event_baseline(value, 510, 3)
        record_committed_spend(value, 6, 'battle:f2')
        reloaded = json.loads(json.dumps(value))
        validate_action_ledger(reloaded['story']['action_ledger'])
        self.assertEqual(action_spent_since_event(reloaded, 510), 6)
        self.assertEqual(cond(20, '{510:6}', reloaded), True)
        self.assertEqual(cond(20, '{510:7}', reloaded), False)

    def test_missing_baseline_and_invalid_ledger_are_unknown(self):
        value = state()
        value['completed_events'] = [510]
        self.assertIsNone(action_spent_since_event(value, 510))
        self.assertIsNone(cond(20, '{510:0}', value))
        # Completed event without a baseline is explicitly unknown, not zero.
        self.assertEqual(code20_condition_values(value, {510: 1}, [510]), {510: None})
        # No ledger and no legacy producer is unknown too.
        legacy_free = state(ledger=False)
        legacy_free['completed_events'] = [510]
        self.assertIsNone(action_spent_since_event(legacy_free, 510))
        self.assertIsNone(cond(20, '{510:0}', legacy_free))
        # Invalid document stays untouched and unsupported.
        invalid = state()
        invalid['completed_events'] = [510]
        invalid['story']['action_ledger']['spent'] = '7'
        self.assertIsNone(action_spent_since_event(invalid, 510))
        self.assertIsNone(cond(20, '{510:0}', invalid))
        self.assertIsNone(record_committed_spend(invalid, 2, 'city:x'))
        self.assertIs(set_event_baseline(invalid, 510, 3), False)
        self.assertEqual(invalid['story']['action_ledger']['spent'], '7')

    def test_legacy_same_week_baseline_is_read_only_compatibility(self):
        value = state(ledger=False)
        value['story'].update(week_actions_spent=12, event_action_baselines={'510': 4},
                              event_days={'510': {'week': 3, 'day': 1}})
        value['completed_events'] = [510]
        self.assertEqual(action_spent_since_event(value, 510), 8)
        self.assertTrue(cond(20, '{510:8}', value))
        self.assertFalse(cond(20, '{510:9}', value))
        # Older week or inconsistent counter never becomes a negative/false fact.
        value['story']['event_days']['510']['week'] = 2
        self.assertIsNone(action_spent_since_event(value, 510))
        self.assertIsNone(cond(20, '{510:0}', value))
        value['story']['event_days']['510']['week'] = 3
        value['story']['week_actions_spent'] = 3
        self.assertIsNone(action_spent_since_event(value, 510))
        self.assertIsNone(cond(20, '{510:0}', value))
        value['story']['week_actions_spent'] = '12'
        self.assertIsNone(action_spent_since_event(value, 510))
        # An exact zero legacy counter may be the host default; unknown, not 0.
        value['story'].update(week_actions_spent=0, event_action_baselines={'510': 0})
        self.assertIsNone(action_spent_since_event(value, 510))
        self.assertIsNone(cond(20, '{510:0}', value))

    def test_condition_treats_incomplete_event_as_known_false(self):
        value = state()
        record_committed_spend(value, 3)
        set_event_baseline(value, 510, 3)
        self.assertFalse(cond(20, '{510:1}', value))
        self.assertEqual(code20_condition_values(value, {510: 1}, []), {})
        value['completed_events'] = [510]
        self.assertTrue(cond(20, '{510:0}', value))

    def test_explicit_condition_value_still_overrides_the_ledger(self):
        value = state()
        set_event_baseline(value, 510, 3)
        value['completed_events'] = [510]
        self.assertFalse(cond(20, '{510:2}', value))
        self.assertTrue(cond(20, '{510:2}', value, {'condition_values': {20: {510: 2}}}))

    def test_ledger_rides_in_the_same_document_and_is_never_inferred(self):
        # A baseline written by a different ledger generation is unusable.
        value = state()
        set_event_baseline(value, 510, 3)
        value['completed_events'] = [510]
        value['story']['action_ledger']['generation'] = 2
        self.assertIsNone(cond(20, '{510:0}', value))
        # Malformed event keys are unknown, never crash the evaluator.
        self.assertIsNone(cond(20, '{"bad":1}', value))
        self.assertIsNone(cond(20, '{510:8.5}', value))


    def test_next_week_carry_preserves_spend_and_advances_generation(self):
        value = state(week=3)
        record_committed_spend(value, 5, 'city:old')
        set_event_baseline(value, 510, 3)
        record_committed_spend(value, 2, 'battle:old')
        carried = next_week_action_ledger(value['story']['action_ledger'])
        self.assertEqual(carried['generation'], 2)
        self.assertEqual(carried['spent'], 7)
        self.assertEqual(carried['baselines'], {})
        self.assertEqual(carried['receipts'], [])
        validate_action_ledger(carried)
        self.assertIsNone(next_week_action_ledger(None))
        broken = copy.deepcopy(value['story']['action_ledger'])
        broken['spent'] = '7'
        self.assertIsNone(next_week_action_ledger(broken))

    def test_invalidated_ledger_is_unknown_and_never_repaired(self):
        value = state()
        value['completed_events'] = [510]
        record_committed_spend(value, 2, 'city:one')
        set_event_baseline(value, 510, 3)
        record_committed_spend(value, 3, 'battle:one')
        self.assertEqual(cond(20, '{510:3}', value), True)
        invalidate_action_ledger(value['story'])
        self.assertEqual(value['story']['action_ledger']['policy'],
                         ACTION_LEDGER_INVALID_POLICY)
        self.assertIsNone(action_spent_since_event(value, 510))
        self.assertIsNone(cond(20, '{510:0}', value))
        self.assertIsNone(record_committed_spend(value, 1, 'city:two'))
        self.assertIs(set_event_baseline(value, 510, 3), False)
        self.assertEqual(value['story']['action_ledger']['policy'],
                         ACTION_LEDGER_INVALID_POLICY)


class PatrolOrderingPolicyTests(unittest.TestCase):
    def test_real_patrol_selection_sees_pre_transaction_ledger(self):
        from test_offline_city_actions import CityActionTests
        from offline_city_actions import prepare_city_action
        from offline_story import evaluate_story_condition
        import local_gateway as gateway
        fixture = CityActionTests()
        fixture.setUp()
        value = fixture.state
        value['completed_events'] = [8, 510]
        set_event_baseline(value, 510, 0)
        record_committed_spend(value, 1, 'city:before')
        fixture.catalogs['triggers'] = {
            111: {'release': 1, 'conds': {3: 'set([1])', 10: 'set([24])',
                                         20: '{510: 1}'}},
            112: {'release': 1, 'conds': {3: 'set([1])', 10: 'set([24])',
                                         20: '{510: 2}'}}}
        fixture.catalogs['content'] = {111: {'release': 1}, 112: {'release': 1}}
        seen = []

        def probe(kind, table_value, probe_state):
            if kind == 20:
                seen.append((table_value,
                             action_spent_since_event(probe_state, 510),
                             probe_state['story']['action_ledger']['spent']))
            return evaluate_story_condition(kind, table_value, probe_state)

        candidate, notices, changed, diagnostic = prepare_city_action(
            value, 'enterPatrolRequest', {'aid': 1, 'hs': fixture.heroes},
            fixture.catalogs, 'city:patrol', fixture.abilities,
            lambda: 'building-order', evaluate_condition=probe)
        self.assertTrue(changed)
        self.assertTrue(seen)
        self.assertEqual(set(entry[1] for entry in seen), {1})
        self.assertEqual(set(entry[2] for entry in seen), {1})
        events = candidate['city_actions']['patrol']['events']
        self.assertIn(111, events)
        self.assertNotIn(112, events)
        self.assertFalse(cond(20, '{510:2}', candidate))
        # The accepted transaction charges only now, at the host save seam;
        # the next selection sees the new value.
        charged = gateway.LocalProxy.record_action_spend(
            None, value, candidate, 'city:patrol')
        self.assertEqual(charged['story']['action_ledger']['spent'], 3)
        self.assertEqual(action_spent_since_event(charged, 510), 3)
        self.assertTrue(cond(20, '{510:2}', charged))


class WeekOwnerLedgerTests(unittest.TestCase):
    def setUp(self):
        import copy as copy_module
        from export_game_catalogs import decode
        from offline_week import prepare_week_transition, prepare_week_result
        self.copy = copy_module
        self.transition = prepare_week_transition
        self.result = prepare_week_result
        fixture = json.loads((ROOT / 'tests/fixtures/offline_week_cdata.json').read_text())
        self.tables = decode(fixture['tables'])
        self.state = {'story': {'version': 1, 'week': 0, 'date': 7, 'route': '1',
                         'sub_routes': [1], 'emergency': False, 'cg': [11], 'endings': [2],
                         'notes': {'p': {}, 'n': {}, 'pn': [123], 'ppn': False},
                         'battle_wins': [101, 1101], 'blackcores': {'2': 1},
                         'pending_effects': {},
                         'city_values': {'av': 0, 'bf': 300, 'rv': 20, 'dv': 10, 'fv': 30},
                         'city_areas': {'1': {'id': 1, 'lv': 3, 'st': [0, False, False],
                                              'bd': {}}}},
                      'profile': {'heroes': {'24': {'sl': 3, 'so': 2, 'cf': 10, 'ef': 75,
                          'cs': 'a' * 24, 'sk': {'a' * 24: {'u': 'a' * 24, 'i': 24}},
                          'ti': {'items': [{'u': 'b' * 24}]}, 'as': 2}},
                          'economy': {'version': 1, 'money': 12345, 'exp': 300, 'level': 7},
                          'treasures': {'version': 1, 'items': [{'u': 'b' * 24, 'i': 1002}]}},
                      'gacha': {'opened_total': 99, 'items': [{'u': 'c' * 24, 'i': 1003}],
                                'group': {'cards': [1, 2]}},
                      'completed_events': [8029], 'processing_events': [],
                      'available_events': [], 'conditions': [[102, 4]],
                      'event_traces': [[8029, [['dialog', [8029]]]]],
                      'battle': {'version': 1, 'active': None, 'receipts': []},
                      'day': {'version': 1, 'stock_day': 7, 'intent': None, 'receipt': None,
                              'review': None},
                      'status': 'city', 'player_name': 'host-name'}
        self.handoff = {'kind': 'week_result', 'event': 8029, 'result': 1,
                        'token': 'ending:8029', 'in_advance': False}

    def earned(self, state):
        return self.result(state, self.handoff, self.tables['events'],
                           self.tables['endings'])[0]

    def test_real_week_owner_carries_generation_and_drops_stale_baselines(self):
        value = self.copy.deepcopy(self.state)
        set_event_baseline(value, 9, 0)
        set_event_baseline(value, 8029, 0)
        record_committed_spend(value, 5, 'city:old')
        value['story']['action_ledger']['baselines']['510'] = {
            'week': 0, 'spent': 5, 'generation': 1}
        earned = self.earned(value)
        self.assertIn('action_ledger', earned['story'])
        transitioned, unused, changed = self.transition(
            earned, 'handleIncWeekAsk', 'ledger:week', self.tables)
        self.assertTrue(changed)
        ledger = transitioned['story']['action_ledger']
        self.assertEqual(ledger['generation'], 2)
        self.assertEqual(ledger['spent'], 5)
        self.assertEqual(ledger['baselines'], {})
        self.assertEqual(ledger['receipts'], [])
        validate_action_ledger(ledger)
        self.assertIsNone(action_spent_since_event(transitioned, 9))
        self.assertIsNone(action_spent_since_event(transitioned, 8029))
        # A completion in the new generation uses the carried generation.
        self.assertTrue(set_event_baseline(transitioned, 510, 1))
        self.assertEqual(ledger['baselines']['510']['generation'], 2)
        record_committed_spend(transitioned, 2, 'city:new')
        self.assertEqual(action_spent_since_event(transitioned, 510), 2)

    def test_real_week_owner_does_not_create_a_ledger(self):
        value = self.copy.deepcopy(self.state)
        self.assertNotIn('action_ledger', value['story'])
        transitioned, unused, changed = self.transition(
            self.earned(value), 'handleIncWeekAsk', 'ledger:none', self.tables)
        self.assertTrue(changed)
        self.assertNotIn('action_ledger', transitioned['story'])


class GatewayLedgerIntegrationTests(unittest.TestCase):
    def test_gateway_records_committed_delta_and_rejects_duplicate_receipt(self):
        import local_gateway as gateway
        previous = state()
        candidate = copy.deepcopy(previous)
        candidate['story']['city_values']['av'] = 22
        result = gateway.LocalProxy.record_action_spend(None, previous, candidate, 'city:one')
        self.assertEqual(result['story']['action_ledger']['spent'], 2)
        self.assertEqual(result['story']['week_actions_spent'], 2)
        self.assertEqual(result['day']['actions_spent'], 2)
        again_previous = copy.deepcopy(result)
        again = copy.deepcopy(result)
        again['story']['city_values']['av'] = 20
        again = gateway.LocalProxy.record_action_spend(None, again_previous, again, 'city:one')
        self.assertEqual(again['story']['action_ledger']['spent'], 2)
        self.assertEqual(again['story']['week_actions_spent'], 2)
        self.assertEqual(again['day']['actions_spent'], 2)

    def test_gateway_does_not_count_a_non_decrease(self):
        import local_gateway as gateway
        previous = state(ledger=False)
        candidate = copy.deepcopy(previous)
        candidate['story']['city_values']['av'] = 24
        result = gateway.LocalProxy.record_action_spend(None, previous, candidate, 'city:free')
        self.assertNotIn('action_ledger', result['story'])
        self.assertEqual(result['story'].get('week_actions_spent'), None)

    def test_gateway_keeps_action_playable_with_invalid_ledger(self):
        import local_gateway as gateway
        previous = state()
        previous['story']['action_ledger']['spent'] = '7'
        candidate = copy.deepcopy(previous)
        candidate['story']['city_values']['av'] = 23
        result = gateway.LocalProxy.record_action_spend(None, previous, candidate, 'city:two')
        self.assertEqual(result['story']['week_actions_spent'], 1)
        self.assertEqual(result['story']['action_ledger']['spent'], '7')
        self.assertIsNone(cond(20, '{510:0}', dict(result, completed_events=[510])))

    def test_gateway_receipt_conflict_invalidates_instead_of_undercounting(self):
        import local_gateway as gateway
        previous = state()
        previous['completed_events'] = [510]
        set_event_baseline(previous, 510, 3)
        record_committed_spend(previous, 2, 'city:one')
        self.assertEqual(cond(20, '{510:2}', previous), True)
        candidate = copy.deepcopy(previous)
        candidate['story']['city_values']['av'] = 21
        result = gateway.LocalProxy.record_action_spend(None, previous, candidate, 'city:one')
        self.assertEqual(result['story']['action_ledger']['policy'],
                         ACTION_LEDGER_INVALID_POLICY)
        self.assertIsNone(action_spent_since_event(result, 510))
        self.assertIsNone(cond(20, '{510:0}', result))
        # The action itself and the legacy audit counter still commit.
        self.assertEqual(result['story']['week_actions_spent'], 3)
        self.assertEqual(result['day']['actions_spent'], 3)
        self.assertEqual(result['story']['city_values']['av'], 21)


class StoryCompletionBaselineTests(unittest.TestCase):
    def completion_state(self):
        from offline_story import initial_story_state
        from offline_gacha import new_gacha_state
        return {'story': initial_story_state(), 'profile': {'heroes': {},
            'economy': {'version': 1, 'money': 100, 'exp': 0, 'level': 1}},
            'gacha': new_gacha_state(), 'available_events': [], 'processing_events': [],
            'completed_events': [], 'event_traces': [], 'conditions': []}

    def complete(self, state, event, content, tables=None):
        from offline_story_engine import prepare_story_operation, begin_story_occurrence
        begin_story_occurrence(state, event)
        state['processing_events'].append(event)
        state, notices = prepare_story_operation(state, 'start', {'e': event},
                                                 content, {}, tables or {})
        state, notices = prepare_story_operation(state, 'callback',
                                                 {'e': event, 'token': 'ui:%d' % event},
                                                 content, {}, tables or {})
        return state, notices

    def test_real_completion_writes_the_baseline_at_current_committed_spend(self):
        value = self.completion_state()
        record_committed_spend(value, 3)
        content = {510: {'release': True, 'ui': ['panel', 'method'], 'completeConds': {}}}
        value, notices = self.complete(value, 510, content)
        self.assertIn(510, value['completed_events'])
        self.assertEqual(value['story']['action_ledger']['baselines']['510'],
                         {'week': 0, 'spent': 3, 'generation': 1})
        self.assertEqual(action_spent_since_event(value, 510), 0)
        record_committed_spend(value, 2)
        self.assertEqual(action_spent_since_event(value, 510), 2)

    def test_pending_completion_writes_no_baseline(self):
        value = self.completion_state()
        content = {510: {'release': True, 'ui': ['panel', 'method'],
                         'completeConds': {}, 'server_only_unknown': 1}}
        value, notices = self.complete(value, 510, content)
        self.assertNotIn(510, value['completed_events'])
        self.assertNotIn('action_ledger', value['story'])
        self.assertFalse([name for name, payload in notices
                          if name == 'completeEventReplyEnd'])

    def test_completion_never_requires_a_prior_ledger_to_be_present(self):
        value = self.completion_state()
        self.assertNotIn('action_ledger', value['story'])
        content = {510: {'release': True, 'ui': ['panel', 'method'], 'completeConds': {}}}
        value, notices = self.complete(value, 510, content)
        self.assertIn(510, value['completed_events'])
        self.assertEqual(value['story']['action_ledger']['spent'], 0)
        self.assertIn('510', value['story']['action_ledger']['baselines'])


if __name__ == '__main__':
    unittest.main()
