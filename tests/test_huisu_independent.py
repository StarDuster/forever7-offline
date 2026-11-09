"""Independent finite dream acceptance using literal original data and flat source.

Only project runtime code executes. Original marshals are parsed as data or
inspected as bytecode; no game imports, devices, source archives or saves change.
History before each finite boundary is explicit fixture history, not earned play.
"""
import ast
import builtins
import copy
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / 'runtime'), str(ROOT / 'tools'),
               str(ROOT / 'analysis/research-agent')]
from read_data_table import read
from read_literal_marshal import read as read_marshal
from offline_city_actions import (prepare_city_action, select_city_patrol_event,
                                  complete_city_patrol_event)
from offline_story import evaluate_story_condition
from offline_story_engine import (prepare_story_operation, refresh_story_events,
                                  begin_story_occurrence, story_occurrence_key)
from offline_huisu import (prepare_huisu_operation, huisu_token, project_huisu,
    check_dream_contract, validate_huisu_document, mark_huisu_nextday, huisu_day_guard)
from offline_event_effects import plan_event_effects, apply_event_effects_snapshot
from offline_day import prepare_gateway_day_operation, build_offline_daily_plan, initial_day_state
import test_offline_city_actions as city_fixture
import test_offline_event_effects as effects_fixture


class HuisuIndependentTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.all_content = read(ROOT / 'analysis/decompiled/event_content.py')
        cls.all_triggers = read(ROOT / 'analysis/decompiled/event_condition.py')
        cls.tables = effects_fixture.original_tables()
        cls.tables['story_dream'] = read_marshal(
            ROOT / 'analysis/android640-scripts/com/data/cdata/story_dream.marshal')
        # Include every original dream marker family and the finite actual
        # entry/night/choice rows. Do not mutate those original rows.
        events = {e for e, row in cls.all_content.items() if 'dream_id' in row}
        events.update((1258, 1317, 1259, 1260, 1261, 1264, 1265, 2205, 2208,
                       2206, 1270, 1283, 1287))
        cls.content = {e: cls.all_content[e] for e in events}
        cls.triggers = {e: cls.all_triggers[e] for e in events if e in cls.all_triggers}
        cls.tables.update(event_content=cls.content, event_condition=cls.triggers)

    def setUp(self):
        fixture = city_fixture.CityActionTests()
        fixture.setUp()
        self.catalogs = copy.deepcopy(fixture.catalogs)
        self.catalogs.update(content=copy.deepcopy(self.content), triggers=copy.deepcopy(self.triggers))
        self.content = self.catalogs['content']
        self.triggers = self.catalogs['triggers']
        self.tables = dict(self.tables, event_content=self.content, event_condition=self.triggers)
        self.state = effects_fixture.base_state(self.tables)
        self.state.update(event_traces=[], conditions=[[101, 0]], day=dict(initial_day_state(), stock_day=0))
        self.state['story'].update(week=0, date=0, route='20', emergency=False,
            city_values=copy.deepcopy(fixture.state['story']['city_values']),
            city_areas={str(a): {'id': a, 'lv': 1, 'st': [0, False, False], 'bd': {}}
                        for a in range(1, 9)})
        self.state['completed_events'] = [1245]  # pre-entry finite boundary
        self.abilities = fixture.abilities
        self.api = globals()

    def call(self, name, *args, **kwargs):
        return self.api[name](*args, **kwargs)

    def story(self, operation, arguments):
        self.state, notices = self.call('prepare_story_operation', self.state,
            operation, arguments, self.content, self.triggers, self.tables)
        return notices

    def start(self, event):
        self.call('refresh_story_events', self.state, self.triggers, self.content)
        self.assertIn(event, dict(self.state['available_events']))
        self.call('begin_story_occurrence', self.state, event, self.content, self.triggers)
        self.state['available_events'] = [p for p in self.state['available_events'] if p[0] != event]
        self.state['processing_events'].append(event)
        self.story('start', {'e': event})

    def dialog(self, event):
        return self.story('trace', {'k': 'dialog', 'd': {'c': self.content[event]['dialog']}})

    def enter(self, day=0):
        if day == 1:
            self.state['day']['stock_day'] = self.state['story']['date'] = 1
            self.state['completed_events'] = [1258, 1262, 2203]
        self.state, notices, changed, diagnostic = self.call('prepare_huisu_operation',
            self.state, 'requestStoryhuisu', {}, self.tables,
            operation_id='owner-A:entry:%s' % day)
        self.assertTrue(changed, diagnostic)
        self.assertEqual([name for name, _ in notices], ['syncRoute', 'syncHuiSuData'])
        entry = self.tables['story_dream'][('20', day)]['event']
        self.assertNotIn(entry, self.state['completed_events'])
        self.assertEqual(self.state['story']['route20_huisu']['phase'], 'entering')
        self.state, _, _, _ = self.call('prepare_gateway_day_operation', self.state,
            'statusCheck', {'s': 'nextday'}, [], stock_day=day)
        self.state, _, _, _ = self.call('prepare_gateway_day_operation', self.state,
            'updateEventCondClient', {'c': 102, 'v': '4'})
        self.start(entry)
        self.dialog(entry)
        self.assertNotIn(entry, self.state['completed_events'])  # real choice still required
        child = self.content[entry]['events'][0]
        self.story('option', {'e': entry, 'se': child, 'op': 1})
        self.assertIn(entry, self.state['completed_events'])
        self.assertEqual(self.state['story']['route20_huisu']['phase'], 'active')
        self.dialog(child)
        if day == 0:
            self.story('option', {'e': child, 'se': 1259, 'op': 1})
            self.dialog(1259)
            self.story('option', {'e': 1259, 'se': 1261, 'op': 1})
            self.dialog(1261)
        self.assertFalse(self.state['processing_events'])
        self.assertNotIn(4, self._clientops())
        return notices

    def _clientops(self):
        value = dict(self.state['conditions']).get(102)
        return value if isinstance(value, (list, tuple)) else ([] if value is None else [value])

    def patrol(self, identity, area=4, heroes=None):
        self.state, notices, changed, diagnostic = self.call('prepare_city_action',
            self.state, 'enterPatrolRequest', {'aid': area, 'hs': heroes or []},
            self.catalogs, identity, self.abilities,
            evaluate_condition=self.api['evaluate_story_condition'])
        return notices, changed, diagnostic

    def claim(self, identity):
        self.state, notices, changed, diagnostic = self.call('prepare_city_action',
            self.state, 'patrolReward', {}, self.catalogs, identity, self.abilities,
            evaluate_condition=self.api['evaluate_story_condition'])
        return notices, changed, diagnostic

    def test_literal_first_day_entry_requires_real_trigger_and_dialog_choice(self):
        self.assertNotIn(1, self.triggers[1258]['conds'])
        self.enter()
        self.assertNotIn(1264, self.state['completed_events'])
        self.assertEqual(self.state['story'].get('battle_wins', []), [])
        self.assertEqual(project_huisu(self.state), {'hs': [], 'hsf': True, 'hst': 0, 'lhs': False})

    def test_actual_nonempty_dream_candidates_and_no_ordinary_cost_mutation(self):
        self.enter()
        before_city = copy.deepcopy(self.state['story']['city_values'])
        before_heroes = copy.deepcopy(self.state['profile']['heroes'])
        self.state['story']['city_areas']['4']['bd'] = {'1': {'id': 22, 'uuid': 'real-fixture-building'}}
        building = copy.deepcopy(self.state['story']['city_areas']['4']['bd'])
        notices, changed, diagnostic = self.patrol('owner-A:patrol-1')
        self.assertTrue(changed, diagnostic)
        self.assertIn(1262, self.state['city_actions']['patrol']['events'])
        self.assertIn(1262, notices[-1][1]['ev'])
        self.assertNotIn(1263, notices[-1][1]['ev'])  # wrong actual area
        self.assertEqual(self.state['story']['city_values'], before_city)
        self.assertEqual(self.state['profile']['heroes'], before_heroes)
        self.assertEqual(self.state['story']['city_areas']['4']['bd'], building)
        self.state, changed = self.call('select_city_patrol_event', self.state, 1262)
        self.assertTrue(changed)
        self.start(1262)
        self.assertNotIn(1262, self.state['completed_events'])
        self.dialog(1262)
        self.assertIn(1262, self.state['completed_events'])
        self.state, changed = self.call('complete_city_patrol_event', self.state, 1262)
        self.assertTrue(changed)
        self.assertEqual(self.state['story']['route20_huisu']['used_actions'], 1)
        self.assertEqual(self.state['story']['city_values'], before_city)

    def test_legal_empty_team_never_satisfies_hero_required_trigger(self):
        self.enter()
        event = 987654321
        self.content[event] = dict(self.content[1262])
        self.triggers[event] = copy.deepcopy(self.triggers[1262])
        self.triggers[event]['conds'][10] = 'set([24])'
        self.patrol('owner-A:empty-team')
        self.assertIn(1262, self.state['city_actions']['patrol']['events'])
        self.assertNotIn(event, self.state['city_actions']['patrol']['events'])
        self.assertFalse(evaluate_story_condition(10, 'set([24])', self.state))

    def test_unseen_dream_event_id_uses_original_trigger_and_real_trace(self):
        self.enter()
        event = 987654399
        self.content[event] = copy.deepcopy(self.content[1262])
        self.triggers[event] = copy.deepcopy(self.triggers[1262])
        self.patrol('owner-A:unseen-id')
        self.assertIn(event, self.state['city_actions']['patrol']['events'])
        self.state, _ = self.call('select_city_patrol_event', self.state, event)
        self.start(event)
        self.assertNotIn(event, self.state['completed_events'])
        self.dialog(event)
        self.assertIn(event, self.state['completed_events'])
        self.assertEqual(self.state['story']['route20_huisu']['used_actions'], 1)

    def test_original_prerequisites_and_trigger_facts_still_gate_entry(self):
        # Day1 client condition1 requires2203; no completion is manufactured.
        self.state['story']['date'] = self.state['day']['stock_day'] = 1
        before = copy.deepcopy(self.state)
        candidate, _, changed, diagnostic = self.call('prepare_huisu_operation', self.state,
            'requestStoryhuisu', {}, self.tables, operation_id='owner-A:missing-predecessor')
        self.assertFalse(changed)
        self.assertEqual(diagnostic['pending'], 'actual_entry_predecessors_required')
        self.assertEqual(candidate, before)
        # Day0's absent condition1 permits reservation, but17 and CLIENTOP4
        # remain necessary to start the actual entry event.
        self.state['story']['date'] = self.state['day']['stock_day'] = 0
        self.state['completed_events'] = []
        self.state, _, changed, _ = self.call('prepare_huisu_operation', self.state,
            'requestStoryhuisu', {}, self.tables, operation_id='owner-A:reserved-only')
        self.assertTrue(changed)
        before = copy.deepcopy(self.state)
        with self.assertRaises(ValueError):
            self.call('begin_story_occurrence', self.state, 1258, self.content, self.triggers)
        self.assertEqual(self.state, before)

    def test_selected_original_parent_successor_survives_patrol_cleanup(self):
        self.enter(day=1)
        self.patrol('owner-A:parent', area=3)
        self.assertIn(1270, self.state['city_actions']['patrol']['events'])
        self.state, _ = self.call('select_city_patrol_event', self.state, 1270)
        self.start(1270)
        self.dialog(1270)
        self.assertNotIn(1270, self.state['completed_events'])
        self.story('option', {'e': 1270, 'se': 1283, 'op': 1})
        self.assertIn(1270, self.state['completed_events'])
        self.state, changed = self.call('complete_city_patrol_event', self.state, 1270)
        self.assertTrue(changed)
        self.assertIsNone(self.state['city_actions']['patrol'])
        self.dialog(1283)
        self.story('option', {'e': 1283, 'se': 1287, 'op': 1})
        stale = copy.deepcopy(self.state)
        value = stale['story']['route20_huisu']
        value['generation'] += 1
        for admission in value['admissions'].values():
            admission['token'] = admission['token'].rsplit(':', 1)[0] + ':' + str(value['generation'])
        self.call('validate_huisu_document', stale)
        denied, notices = self.call('prepare_story_operation', stale, 'trace',
            {'k': 'dialog', 'd': {'c': self.content[1287]['dialog']}},
            self.content, self.triggers, self.tables)
        self.assertNotIn(1287, denied['completed_events'])
        self.assertIn(1287, denied['processing_events'])
        self.assertFalse(notices)
        self.dialog(1287)
        self.assertIn(1287, self.state['completed_events'])
        context = self.state['story']['event_contexts'][story_occurrence_key(self.state, 1287)]
        self.assertEqual(context['origin'], 'successor')
        self.assertEqual(context['admission_id'], 'owner-A:parent')
        self.assertEqual(self.state['story']['route20_huisu']['used_actions'], 1)

    def test_three_admissions_retry_reload_fourth_rejected_and_failure_atomic(self):
        self.enter()
        pristine = copy.deepcopy(self.state)
        with self.assertRaises(ValueError):
            self.patrol('owner-A:bad-area', area=99)
        self.assertEqual(self.state, pristine)
        for index in range(3):
            identity = 'owner-A:bounded-%s' % index
            _, changed, _ = self.patrol(identity)
            self.assertTrue(changed)
            durable = json.loads(json.dumps(self.state))
            self.call('validate_huisu_document', durable)
            self.state = durable
            replay, changed, diagnostic = self.patrol(identity)
            self.assertFalse(changed)
            self.assertTrue(diagnostic['replay'])
            self.assertEqual(self.state, durable)
            self.assertEqual(self.state['story']['route20_huisu']['used_actions'], index + 1)
            self.claim('owner-A:decline-%s' % index)
        before = copy.deepcopy(self.state)
        with self.assertRaises(ValueError):
            self.patrol('owner-A:bounded-fourth')
        self.assertEqual(self.state, before)
        retry, _, changed, diagnostic = self.call('prepare_huisu_operation', self.state,
            'requestStoryhuisu', {}, self.tables, operation_id='owner-B:entry-retry')
        self.assertFalse(changed)
        self.assertEqual(retry, self.state)
        self.assertEqual(retry['story']['route20_huisu']['used_actions'], 3)

    def test_out_then_actual_rest_night_dialog_and_committed_day_no_softlock(self):
        self.enter()
        self.patrol('owner-A:before-out')
        self.claim('owner-A:out-decline')
        token = self.call('huisu_token', self.state)
        self.state, notices, changed, _ = self.call('prepare_huisu_operation', self.state,
            'requestStoryhuisuOut', {}, self.tables, token)
        self.assertTrue(changed)
        self.assertEqual([n for n, _ in notices], ['recoverStoryline', 'syncHuiSuData'])
        self.assertEqual(self.state['story']['route20_huisu']['used_actions'], 1)
        self.assertEqual(project_huisu(self.state), {'hs': [], 'hsf': False, 'hst': 0, 'lhs': True})
        denied, _, changed, _ = self.call('prepare_huisu_operation', self.state,
            'requestStoryhuisu', {}, self.tables, operation_id='owner-B:no-refill')
        self.assertFalse(changed)
        self.assertEqual(denied, self.state)
        self.assertIsNotNone(self.call('huisu_day_guard', self.state))
        premature, notices, changed, diagnostic = self.call('prepare_gateway_day_operation',
            self.state, 'incDayWhenNoActionVal', {}, [])
        self.assertFalse(changed)
        self.assertEqual(premature, self.state)
        self.assertEqual(diagnostic['pending'], 'actual_huisu_night_chain_required')
        self.assertGreater(self.state['story']['city_values']['av'], 0)
        date = self.state['story']['date']
        self.state, _, _, _ = self.call('prepare_gateway_day_operation', self.state,
            'statusCheck', {'s': 'nextday'}, [], stock_day=0)
        self.state, _, _, _ = self.call('prepare_gateway_day_operation', self.state,
            'updateEventCondClient', {'c': 102, 'v': '4'})
        self.call('mark_huisu_nextday', self.state, 'owner-A:real-rest', token)
        self.start(1264)
        self.dialog(1264)
        self.assertIsNotNone(self.call('huisu_day_guard', self.state))  # original child pending
        self.story('option', {'e': 1264, 'se': 1265, 'op': 1})
        self.dialog(1265)
        self.assertIsNone(self.call('huisu_day_guard', self.state))
        self.assertEqual(self.state['story']['date'], date)
        daily = json.loads((ROOT / 'tests/fixtures/offline_day_cdata.json').read_text())
        fatigue = {int(k): v for k, v in daily['fatigue_recover'].items()}
        upgrades = {(a, level): {'money_output': output} for a, level, output in daily['upgrade_income']}
        plan, diagnostic = self.call('build_offline_daily_plan', self.state, fatigue, upgrades)
        self.assertIsNotNone(plan, diagnostic)
        self.state, notices, changed, diagnostic = self.call('prepare_gateway_day_operation',
            self.state, 'incDayWhenNoActionVal', {}, [], plan)
        self.assertTrue(changed, diagnostic)
        self.assertEqual(self.state['story']['date'], date + 1)
        self.assertNotIn('route20_huisu', self.state['story'])
        self.assertFalse(project_huisu(self.state)['hsf'])
        self.assertIn('showDailySettlement', [n for n, _ in notices])
        retry, _, changed, diagnostic = self.call('prepare_gateway_day_operation',
            self.state, 'incDayWhenNoActionVal', {}, [])
        self.assertFalse(changed)
        self.assertTrue(diagnostic['replay'])
        self.assertEqual(retry, self.state)

    def test_out_cannot_skip_selected_event_and_applied_receipt_replay_after_exit_is_harmless(self):
        self.enter()
        self.patrol('owner-A:out-pending')
        self.state, _ = self.call('select_city_patrol_event', self.state, 1262)
        self.start(1262)
        before = copy.deepcopy(self.state)
        blocked, notices, changed, diagnostic = self.call('prepare_huisu_operation', self.state,
            'requestStoryhuisuOut', {}, self.tables, self.call('huisu_token', self.state))
        self.assertFalse(changed)
        self.assertEqual(blocked, before)
        self.assertFalse(notices)
        self.dialog(1262)
        receipt = story_occurrence_key(self.state, 1262)
        self.state, _ = self.call('complete_city_patrol_event', self.state, 1262)
        self.state, _, changed, _ = self.call('prepare_huisu_operation', self.state,
            'requestStoryhuisuOut', {}, self.tables, self.call('huisu_token', self.state))
        self.assertTrue(changed)
        before = copy.deepcopy(self.state)
        replay, notices, diagnostic = self.call('plan_event_effects', self.state, 1262,
            self.content, self.tables, {'receipt_key': receipt})
        self.assertTrue(diagnostic['ready'])
        self.assertEqual(diagnostic['status'], 'already-applied')
        self.assertEqual(replay, before)
        self.assertFalse(notices)

    def test_original_base_route_lookup_and_exact_route_override_are_distinct(self):
        self.state['story']['route'] = '20-1'
        entered, _, changed, diagnostic = self.call('prepare_huisu_operation', self.state,
            'requestStoryhuisu', {}, self.tables, operation_id='owner-A:base-fallback')
        self.assertTrue(changed, diagnostic)
        self.assertEqual(entered['story']['route20_huisu']['entry_event'], 1258)
        tables = dict(self.tables, story_dream=dict(self.tables['story_dream']))
        # Distinguish lookup with a new fixture row using an existing original
        # event; this only proves resolution, never starting an invalid trigger.
        tables['story_dream'][('20-1', 0)] = dict(tables['story_dream'][('20', 1)])
        self.state['completed_events'].append(2203)
        entered, _, changed, diagnostic = self.call('prepare_huisu_operation', self.state,
            'requestStoryhuisu', {}, tables, operation_id='owner-A:exact-row')
        self.assertTrue(changed, diagnostic)
        self.assertEqual(entered['story']['route20_huisu']['entry_event'], 2205)

    def test_exact_marker_types_legacy_no_context_and_unknown_original_row_fail_closed(self):
        self.assertEqual(self.content[1318]['dream_id'], ('-1',))
        self.assertNotIn(1318, self.triggers)
        self.assertFalse(check_dream_contract(self.content[1262], None))
        before = copy.deepcopy(self.state)
        candidate, notices, diagnostic = self.call('plan_event_effects', self.state,
            1262, self.content, self.tables, {'receipt_key': 'arbitrary:unearned'})
        self.assertFalse(diagnostic['ready'])
        self.assertEqual(candidate, before)
        self.assertFalse(notices)
        self.enter()
        context = self.state['story']['event_contexts'][story_occurrence_key(self.state, 1258)]
        for marker in ((-1,), (1,), '-1', ('-1', '-1'), (), None):
            self.assertFalse(self.call('check_dream_contract', {'dream_id': marker}, context))
        self.assertTrue(self.call('check_dream_contract', {'dream_id': ['-1']}, context))
        self.assertTrue(self.call('check_dream_contract', {'dream_id': ('-1',)}, context))
        with self.assertRaises(ValueError):
            self.call('begin_story_occurrence', self.state, 1318, self.content, self.triggers)

    def test_stale_generation_rejects_pending_effect_and_old_admission_replay(self):
        self.enter()
        self.patrol('owner-A:old-generation')
        self.state, _ = self.call('select_city_patrol_event', self.state, 1262)
        self.start(1262)
        old = copy.deepcopy(self.state)
        value = self.state['story']['route20_huisu']
        value['generation'] += 1
        new_token = value['admissions']['owner-A:old-generation']['token'].rsplit(':', 1)[0] + ':' + str(value['generation'])
        for admission in value['admissions'].values():
            admission['token'] = new_token
        self.state['city_actions']['patrol']['context_token'] = new_token
        self.call('validate_huisu_document', self.state)
        before = copy.deepcopy(self.state)
        candidate, _, diagnostic = self.call('plan_event_effects', self.state, 1262,
            self.content, self.tables, {'receipt_key': story_occurrence_key(old, 1262)})
        self.assertFalse(diagnostic['ready'])
        self.assertEqual(candidate, before)
        with self.assertRaises(ValueError):
            self.patrol('owner-A:old-generation')
        self.assertEqual(self.state, before)

    def test_route35_original_dream_consumes_only_existing_flashback_admission(self):
        from test_route35_flashback import activate_fixture
        self.state = activate_fixture(self.state)
        self.state['completed_events'] = [7755]
        before_city = copy.deepcopy(self.state['story']['city_values'])
        _, changed, diagnostic = self.patrol('owner-A:route35', area=1, heroes=[7, 8, 24])
        self.assertTrue(changed, diagnostic)
        self.assertIn(7794, self.state['city_actions']['patrol']['events'])
        self.assertNotIn(7797, self.state['city_actions']['patrol']['events'])
        self.state, _ = self.call('select_city_patrol_event', self.state, 7794)
        self.start(7794)
        self.dialog(7794)
        self.assertIn(7794, self.state['completed_events'])
        self.assertEqual(self.state['story']['route35_flashback']['used_actions'], 1)
        self.assertNotIn('route20_huisu', self.state['story'])
        self.assertEqual(self.state['story']['city_values']['av'], before_city['av'])
        self.assertEqual(self.state['story']['city_values']['pn'], before_city['pn'] + 1)

    def test_legacy_snapshot_inactive_preserves_history_and_does_not_mint_context(self):
        self.state['completed_events'].append(1258)
        before = copy.deepcopy(self.state)
        projected = self.call('apply_event_effects_snapshot', self.state,
            {'std': {'hsu': [999], 'hsf': True, 'hst': 3, 'lhs': True}})['std']
        self.assertEqual({k: projected[k] for k in ('hsu', 'hsf', 'hst', 'lhs')},
                         {'hsu': [], 'hsf': False, 'hst': 0, 'lhs': False})
        candidate, _, changed, diagnostic = self.call('prepare_huisu_operation', self.state,
            'requestStoryhuisu', {}, self.tables, operation_id='new-owner:legacy')
        self.assertFalse(changed)
        self.assertEqual(diagnostic['pending'], 'unsupported_legacy_dream_continuation')
        self.assertEqual(candidate, before)
        self.assertEqual(self.state, before)


class HuisuFlatIndependentTests(HuisuIndependentTests):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        from patch_bootstrap import embedded_loader
        loader = embedded_loader(ROOT / 'runtime')
        assignment = ast.parse(loader.splitlines()[0]).body[0]
        cls.flat_source = ast.literal_eval(assignment.value)
        real_import = builtins.__import__
        blocked = []
        def imports(name, globals=None, locals=None, fromlist=(), level=0):
            if name.startswith('offline_'):
                blocked.append(name)
                raise ImportError('Flat project runtime: host module unavailable')
            return real_import(name, globals, locals, fromlist, level)
        cls.flat = {'__builtins__': dict(vars(builtins), __import__=imports),
                    '__name__': 'independent_flat_huisu'}
        exec(compile(cls.flat_source, '<project-flat-huisu-only>', 'exec'), cls.flat, cls.flat)
        cls.blocked = blocked

    def setUp(self):
        super().setUp()
        self.api = self.flat

    def test_flat_has_no_host_dependency_and_allowlist_is_bounded(self):
        self.assertIn('offline_huisu', self.blocked)
        self.assertIs(self.flat['prepare_huisu_operation'].__globals__, self.flat)
        members = json.loads((ROOT / 'offline-project-allowlist.json').read_text())['files']
        self.assertEqual(len(members), 62)
        self.assertEqual(len(set(members)), 62)
        self.assertIn('runtime/offline_huisu.py', members)
        self.assertIn('runtime/offline_daerweila.py', members)
        self.assertIn('runtime/offline_role_mission.py', members)
        self.assertIn('runtime/offline_chapter_campaign.py', members)
        self.assertIn('runtime/offline_battle_terminal.py', members)
        self.assertIn('runtime/offline_special_city_stage.py', members)


class OriginalHuisuConsumerEvidenceTests(unittest.TestCase):
    def test_original_marshal_consumer_syncroute_retains_hsf_before_full_notice(self):
        # Source-only bytecode inspection corroborates the consumer contract;
        # no original Python function is converted or executed.
        import bytecode27
        code = bytecode27.read(ROOT / 'analysis/android640-scripts/entity/avatar_members/StoryMember.marshal')
        def descend(value):
            yield value
            for const in getattr(value, 'co_consts', ()):
                if hasattr(const, 'co_code'):
                    yield from descend(const)
        methods = {item.co_name: item for item in descend(code)}
        for name in ('syncRoute', 'syncHuiSuData', 'requestStoryhuisu'):
            self.assertIn(name, methods)
        route = methods['syncRoute']
        for name in ('syncHuisu', 'huisu_flag', 'notify_huisu_enter', 'recover_storyline'):
            self.assertIn(name, route.co_names)
        full = methods['syncHuiSuData']
        for key in ('hs', 'hsf', 'hst', 'lhs'):
            self.assertIn(key, full.co_consts)
        source = (ROOT / 'analysis/decompiled/StoryMember.py').read_text().split(
            '    def syncRoute(', 1)[1].split('\n    def ', 1)[0]
        self.assertLess(source.index('ori_huisu_flag ='), source.index('self.storyData.syncHuisu('))
        self.assertLess(source.index('self.storyData.syncHuisu('), source.index('if gg.avatar.storyData.huisu_flag:'))
        # Therefore entry syncRoute must carry active hsd before the following
        # full syncHuiSuData; an earlier full sync would swallow false->true.
        fixture = HuisuIndependentTests()
        HuisuIndependentTests.setUpClass()
        fixture.setUp()
        _, notices, changed, diagnostic = prepare_huisu_operation(fixture.state,
            'requestStoryhuisu', {}, fixture.tables, operation_id='consumer:entry')
        self.assertTrue(changed, diagnostic)
        self.assertEqual([name for name, _ in notices], ['syncRoute', 'syncHuiSuData'])
        self.assertTrue(notices[0][1]['hsd']['hsf'])
        self.assertTrue(notices[1][1]['d']['hsf'])


if __name__ == '__main__':
    unittest.main()
