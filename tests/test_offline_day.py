import copy
import json
import hashlib
from pathlib import Path
import sys
import unittest
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'runtime'))
from offline_day import prepare_day_operation, commit_day_operation, week_transition_boundary, prepare_gateway_day_operation, build_offline_daily_plan, offline_city_defaults


class DayProtocolTests(unittest.TestCase):
    def setUp(self):
        self.state = {'weeknum': {'w': 2, 'd': 3, 'c': {}, 'l': {}},
                      'city': {'av': 0, 'dv': 8, 'rv': 11, 'fv': 2, 'areas': {'area_1': {'id': 1}}},
                      'story': {'date': 93, 'week': 2},
                      'profile': {'heroes': {'8': {'cf': 20}}, 'skins': [1], 'treasures': [2]},
                      'completed_events': [1]}
        self.plan = {'source_week': 2, 'source_day': 3,
                     'source_city': copy.deepcopy(self.state['city']), 'next_day': 4,
                     'condition_date': 94, 'city': dict(self.state['city'], av=17),
                     'c': {'rsv': 11, 'dvv': 8, 'frv': 2},
                     'l': {'rsv': 9, 'dvv': 6, 'frv': 1},
                     'evidence': ['test fixture explicit economy policy; not official server formula']}

    def prepare(self, state, op, args=None, blockers=None, plan=None):
        return prepare_day_operation(state, op, args or {}, blockers, plan)

    def armed(self):
        state, notices, changed, _ = self.prepare(self.state, 'statusCheck', {'s': 'nextday'}, [])
        self.assertEqual(notices, [('statusCheckReply', {'r': 'ok', 's': 'nextday'})])
        state, _, _, diag = self.prepare(state, 'updateEventCondClient', {'c': 102, 'v': '4'})
        self.assertEqual(diag['condition_update'], {'type': 102, 'value': [4]})
        return state

    def test_unknown_scan_and_active_event_never_arm_or_change_day(self):
        for blockers in (None, ['event:520'], ['unknown-condition:54']):
            candidate, notices, changed, diag = self.prepare(self.state, 'statusCheck', {'s': 'nextday'}, blockers)
            self.assertFalse(changed)
            self.assertEqual(candidate, self.state)
            self.assertIn('pending', diag)
            if blockers:
                self.assertEqual(notices[0][1]['r'], 'event')
            else:
                self.assertFalse(notices)

    def test_original_three_step_order_and_native_fields(self):
        before = copy.deepcopy(self.state)
        candidate, notices, changed, diag = self.prepare(self.armed(), 'incDayWhenNoActionVal', blockers=[], plan=self.plan)
        self.assertTrue(changed)
        self.assertEqual([x[0] for x in notices], ['get_city_data_reply', 'updateDay', 'showDailySettlement'])
        self.assertEqual(notices[-1][1], {'c': self.plan['c'], 'l': self.plan['l']})
        self.assertEqual(candidate['weeknum']['d'], 4)
        self.assertEqual(candidate['story']['date'], 94)
        self.assertEqual(candidate['city']['av'], 17)
        self.assertEqual(candidate['profile'], before['profile'])
        self.assertEqual(self.state, before)

    def test_missing_order_action_or_plan_stays_pending(self):
        candidate, notices, changed, diag = self.prepare(self.state, 'incDayWhenNoActionVal', blockers=[], plan=self.plan)
        self.assertEqual(diag['pending'], 'nextday_status_check_required')
        armed = self.armed()
        for blockers, plan in ((None, self.plan), (['event'], self.plan), ([], None)):
            candidate, notices, changed, diag = self.prepare(armed, 'incDayWhenNoActionVal', blockers=blockers, plan=plan)
            self.assertFalse(changed)
            self.assertFalse(notices)
            self.assertEqual(candidate, armed)
        armed['city']['av'] = 1
        self.assertEqual(self.prepare(armed, 'incDayWhenNoActionVal', blockers=[], plan=self.plan)[3]['pending'], 'action_value_positive')

    def test_empty_review_stale_plan_or_noninteger_day_cannot_commit(self):
        armed = self.armed()
        for field, value in (('c', {}), ('l', {'rsv': 0}), ('next_day', True), ('condition_date', None), ('city', {'av': 24})):
            plan = copy.deepcopy(self.plan)
            plan[field] = value
            with self.assertRaises(ValueError):
                self.prepare(armed, 'incDayWhenNoActionVal', blockers=[], plan=plan)
        plan = dict(self.plan, source_day=2)
        self.assertEqual(self.prepare(armed, 'incDayWhenNoActionVal', blockers=[], plan=plan)[3]['pending'], 'stale_daily_settlement_plan')

    def test_replay_does_not_apply_income_twice_even_with_positive_new_actions(self):
        done, notices, _, _ = self.prepare(self.armed(), 'incDayWhenNoActionVal', blockers=[], plan=self.plan)
        replay, repeated, changed, diag = self.prepare(done, 'incDayWhenNoActionVal')
        self.assertFalse(changed)
        self.assertEqual(replay, done)
        self.assertEqual(repeated, notices)
        self.assertTrue(diag['replay'])

    def test_failed_save_does_not_publish_or_change_original(self):
        armed = self.armed()
        before = copy.deepcopy(armed)
        published = []
        def fail(candidate):
            candidate['city']['av'] = 999
            raise IOError('disk full')
        with self.assertRaises(IOError):
            commit_day_operation(armed, 'incDayWhenNoActionVal', {}, fail,
                                 lambda *args: published.append(args), [], self.plan)
        self.assertEqual(armed, before)
        self.assertFalse(published)

    def test_commit_before_callbacks_and_restart_replay(self):
        durable, events = [], []
        def save(candidate):
            durable.append(candidate)
            events.append('save')
        def publish(name, payload):
            self.assertTrue(durable)
            events.append(name)
        candidate, changed, _ = commit_day_operation(self.armed(), 'incDayWhenNoActionVal', {}, save, publish, [], self.plan)
        self.assertEqual(events[0], 'save')
        self.assertEqual(candidate, durable[0])
        self.assertTrue(self.prepare(copy.deepcopy(durable[0]), 'incDayWhenNoActionVal')[3]['replay'])

    def test_gateway_adapter_uses_existing_story_and_condition_storage(self):
        state = {'story': {'week': 2, 'date': 93, 'city_values': {k: v for k, v in self.state['city'].items() if k != 'areas'},
                           'city_areas': {'1': {'id': 1}}}, 'profile': self.state['profile'], 'conditions': [[101, 0]]}
        checked, _, changed, _ = prepare_gateway_day_operation(state, 'statusCheck', {'s': 'nextday'}, [], stock_day=3)
        self.assertTrue(changed)
        armed, _, _, _ = prepare_gateway_day_operation(checked, 'updateEventCondClient', {'c': 102, 'v': '4'})
        self.assertEqual(dict(armed['conditions'])[102], 4)
        done, notices, changed, _ = prepare_gateway_day_operation(armed, 'incDayWhenNoActionVal', {}, [], self.plan)
        self.assertTrue(changed)
        self.assertEqual(done['story']['city_values']['av'], 17)
        self.assertEqual(done['story']['city_areas'], {'1': {'id': 1}})
        self.assertEqual(done['day']['stock_day'], 4)
        self.assertNotIn('city', done)
        self.assertNotIn('weeknum', done)
        self.assertEqual(state['story']['date'], 93)

    def provider_state(self):
        state = {'story': {'week': 0, 'date': 0, 'emergency': False,
                          'city_values': dict(offline_city_defaults(), bf=80, rv=5, dv=8, fv=10),
                          'city_areas': {'1': {'id': 1, 'lv': 1, 'st': [0, False, False]},
                                         '2': {'id': 2, 'lv': 3, 'st': [0, False, False]},
                                         '3': {'id': 3, 'lv': 5, 'st': [1, False, False]}}},
                 'profile': {'heroes': {'8': {'cf': 98, 'ef': 20, 'sk': {'uid': {'i': 8}}},
                                        '24': {'cf': 40, 'ef': 9}}, 'treasures': ['owned'], 'skins': ['owned']},
                 'conditions': [[102, 4]], 'processing_events': []}
        fixture = json.loads((ROOT / 'tests/fixtures/offline_day_cdata.json').read_text())
        fatigue = {int(k): v for k, v in fixture['fatigue_recover'].items()}
        upgrades = {(a, level): {'money_output': output} for a, level, output in fixture['upgrade_income']}
        return state, fatigue, upgrades

    def test_real_cdata_provider_builds_complete_city_and_fatigue_day(self):
        state, fatigue, upgrades = self.provider_state()
        before = copy.deepcopy(state)
        plan, diag = build_offline_daily_plan(state, fatigue, upgrades, stock_day=0)
        self.assertEqual(diag['construction_fund_income'], 200)
        self.assertEqual(plan['city']['bf'], 280)
        self.assertEqual(plan['city']['av'], 24)
        self.assertEqual(plan['city']['dvc'], 8)
        self.assertEqual(plan['c'], {'rsv': 5, 'dvv': 8, 'frv': 10})
        self.assertEqual(plan['l'], plan['c'])
        self.assertEqual(plan['profile']['heroes']['8']['cf'], 100)
        self.assertEqual(plan['profile']['heroes']['24']['cf'], 45)
        self.assertEqual(plan['profile']['heroes']['8']['ef'], 20)
        self.assertEqual(plan['profile']['treasures'], ['owned'])
        self.assertEqual(state, before)
        checked = prepare_gateway_day_operation(state, 'statusCheck', {'s': 'nextday'}, [], stock_day=0)[0]
        armed = prepare_gateway_day_operation(checked, 'updateEventCondClient', {'c': 102, 'v': '4'})[0]
        done, notices, changed, _ = prepare_gateway_day_operation(armed, 'incDayWhenNoActionVal', {}, [], plan)
        self.assertTrue(changed)
        self.assertEqual(notices[0], ('updateCurFatigueValue', {'h': 24, 'v': 45}))
        self.assertEqual(notices[-1][0], 'showDailySettlement')
        self.assertNotIn(102, dict(done['conditions']))
        self.assertEqual(done['story']['date'], 1)
        replay = prepare_gateway_day_operation(done, 'incDayWhenNoActionVal', {})
        self.assertFalse(replay[2])
        self.assertEqual(replay[1], notices)
        self.assertEqual(replay[0]['story']['city_values']['bf'], 280)

    def test_previous_review_survives_clear_and_second_real_day(self):
        state, fatigue, upgrades = self.provider_state()
        plan, _ = build_offline_daily_plan(state, fatigue, upgrades, stock_day=0)
        state = prepare_gateway_day_operation(state, 'statusCheck', {'s': 'nextday'}, [], stock_day=0)[0]
        state = prepare_gateway_day_operation(state, 'updateEventCondClient', {'c': 102, 'v': '4'})[0]
        state = prepare_gateway_day_operation(state, 'incDayWhenNoActionVal', {}, [], plan)[0]
        state = prepare_gateway_day_operation(state, 'clearCurDailySettlement', {})[0]
        state['story']['city_values'].update(av=0, rv=15)
        second, _ = build_offline_daily_plan(state, fatigue, upgrades)
        self.assertEqual(second['l'], plan['c'])
        self.assertEqual(second['c']['rsv'], 15)
        self.assertEqual(second['city']['bf'], 480)
        self.assertEqual(second['profile']['heroes']['24']['cf'], 50)

    def test_provider_refuses_real_unfinished_gameplay_or_unknown_data(self):
        for kind in ('battle', 'event', 'effect', 'income', 'fatigue', 'weekend'):
            state, fatigue, upgrades = self.provider_state()
            if kind == 'battle': state['battle'] = {'active': {'fight_id': 'actual'}}
            if kind == 'event': state['processing_events'] = [520]
            if kind == 'effect': state['story']['pending_effects'] = {'520': {'unsupported': 'route'}}
            if kind == 'income': upgrades.clear()
            if kind == 'fatigue': fatigue.clear()
            day = 7 if kind == 'weekend' else 0
            plan, diagnostic = build_offline_daily_plan(state, fatigue, upgrades, stock_day=day)
            self.assertIsNone(plan)
            self.assertIn('pending', diagnostic)

    def test_source_profile_changes_invalidate_prepared_fatigue_grant(self):
        state, fatigue, upgrades = self.provider_state()
        plan, _ = build_offline_daily_plan(state, fatigue, upgrades, stock_day=0)
        state = prepare_gateway_day_operation(state, 'statusCheck', {'s': 'nextday'}, [], stock_day=0)[0]
        state = prepare_gateway_day_operation(state, 'updateEventCondClient', {'c': 102, 'v': '4'})[0]
        state['profile']['heroes']['24']['cf'] = 1
        done, notices, changed, diagnostic = prepare_gateway_day_operation(state, 'incDayWhenNoActionVal', {}, [], plan)
        self.assertFalse(changed)
        self.assertFalse(notices)
        self.assertEqual(diagnostic['pending'], 'stale_daily_settlement_plan')

    def test_provider_fixture_is_pinned_to_original_android_marshal(self):
        fixture = json.loads((ROOT / 'tests/fixtures/offline_day_cdata.json').read_text())
        for name, digest in fixture['sha256'].items():
            source = ROOT / ('analysis/android640-scripts/com/data/cdata/' + name + '.marshal')
            self.assertEqual(hashlib.sha256(source.read_bytes()).hexdigest(), digest)

    def test_nextday_consumes_only_current_client_operation(self):
        state, fatigue, upgrades = self.provider_state()
        plan, _ = build_offline_daily_plan(state, fatigue, upgrades, stock_day=0)
        state = prepare_gateway_day_operation(state, 'statusCheck', {'s': 'nextday'}, [], stock_day=0)[0]
        state = prepare_gateway_day_operation(state, 'updateEventCondClient', {'c': 102, 'v': '4'})[0]
        state['conditions'] = [[101, 0], [102, [2, 4, 7]]]
        done = prepare_gateway_day_operation(state, 'incDayWhenNoActionVal', {}, [], plan)[0]
        self.assertEqual(dict(done['conditions']), {101: 0, 102: [2, 7]})

    def test_clear_review_and_week_boundary_do_not_fake_reset(self):
        done, _, _, _ = self.prepare(self.armed(), 'incDayWhenNoActionVal', blockers=[], plan=self.plan)
        clear, notices, changed, _ = self.prepare(done, 'clearCurDailySettlement')
        self.assertTrue(changed)
        self.assertFalse(notices)
        self.assertEqual(clear['weeknum']['c'], {})
        self.assertIsNone(clear['day_protocol']['review'])
        for operation in ('handleResetWeekAsk', 'handleIncWeekAsk', 'handleResetWeek'):
            self.assertFalse(week_transition_boundary(clear, operation)['mutates'])


if __name__ == '__main__':
    unittest.main()
