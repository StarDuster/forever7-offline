"""Finite original-consumer/gateway contracts; no native playback claim."""
import copy
import json
import textwrap
import types
import sys
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import patch
ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / 'runtime'), str(ROOT / 'tools')]
import offline_huisu as huisu
import offline_story_engine as engine
from offline_event_effects import apply_event_effects_snapshot
from offline_day import prepare_gateway_day_operation
import test_gateway_integrations as integrations
from test_local_gateway import gateway

ENTRY, PATROL, CHILD, NIGHT = 987601, 987602, 987603, 987604


def catalogs():
    content = {
        ENTRY: {'release': True, 'dialog': 76501},
        PATROL: {'release': True, 'dialog': 76502, 'dream_id': ('-1',), 'events': (CHILD,)},
        CHILD: {'release': True, 'dialog': 76503},
        NIGHT: {'release': True, 'dialog': 76504, 'isAutoTriggerEvent': True}}
    common = {4: '[0,0]', 52: "set(['20'])", 101: '0'}
    triggers = {
        ENTRY: {'release': True, 'conds': dict(common, **{})},
        PATROL: {'release': True, 'conds': dict(common)},
        NIGHT: {'release': True, 'conds': dict(common)}}
    triggers[ENTRY]['conds'].update({102: 'set([4])'})
    triggers[PATROL]['conds'].update({1: 'set([%s])' % ENTRY, 3: 'set([1])', 102: 'set([2])'})
    triggers[NIGHT]['conds'].update({1: 'set([%s])' % ENTRY, 102: 'set([4])'})
    return {'event_content': content, 'event_condition': triggers,
        'story_dream': {('20', 0): {'event': ENTRY, 'goodnight_event': NIGHT}}}


class HuisuGatewayTests(integrations.IntegratedGatewayTests):
    # Reuse only fixture setup, not inherited unrelated regression methods.
    def setUp(self):
        super().setUp()
        self.tables = catalogs()
        for name, value in self.tables.items():
            self.table(name, value)
        self.table('fatigue_recover', {-1: {'fatigue_recover': 5}})
        self.proxy.story.update(route='20', date=0, week=0)
        self.proxy.completed_events.clear()
        self.proxy.conditions.clear()
        self.proxy.save_progress()
        self.proxy.prepare_story_gate = lambda state, event: (state, [])
        self.proxy.process_week_handoffs = lambda: None
        self.engine.logic = SimpleNamespace(game_state=SimpleNamespace(current='city'))
        self.modules['com.const'].GameState = SimpleNamespace(CITY='city')
        self.engine.ui = SimpleNamespace(_dialogue=None)
        for module in (huisu, engine):
            for name, value in vars(module).items():
                if callable(value) and not name.startswith('_'):
                    setattr(gateway, name, value)

    def enter(self):
        source = huisu.huisu_request_source(self.proxy.progress_snapshot())
        self.proxy.process_huisu_operation('requestStoryhuisu', {}, source, 31, 'entry-1', self.owner)
        self.assertEqual(self.proxy.story['route20_huisu']['phase'], 'entering')
        return source

    def rest_intent(self, identity='rest-1'):
        self.proxy.process_day_operation('statusCheck', {'s': 'nextday'})
        self.proxy.process_day_operation('updateEventCondClient', {'c': 102, 'v': '4'},
            huisu_source=(huisu.huisu_token(self.proxy.progress_snapshot()), identity))

    def start(self, event, sequence):
        self.proxy.reliable_call({'w': {'m': 'startEvent', 'r': sequence, 'p': {'e': event}}})

    def trace(self, dialog):
        self.proxy.process_story('trace', {'k': 'dialog', 'd': {'c': dialog}})

    def test_original_syncroute_edge_entry_real_rest_then_three_atomic_admissions(self):
        self.owner.replies.clear()
        source = self.enter()
        names = [name for name, payload in self.owner.replies]
        self.assertLess(names.index('syncRoute'), names.index('syncHuiSuData'))
        self.assertNotIn(ENTRY, self.proxy.completed_events)
        self.assertNotIn(ENTRY, self.proxy.available_events)
        self.proxy.handle_city_action('enterPatrolRequest', {'aid': 1, 'hs': []}, 'premature')
        self.assertEqual(self.proxy.story['route20_huisu']['used_actions'], 0)
        self.rest_intent()
        self.assertIn(ENTRY, self.proxy.available_events)
        self.start(ENTRY, 5)
        self.trace(76501)
        self.assertIn(ENTRY, self.proxy.completed_events)
        self.assertEqual(self.proxy.story['route20_huisu']['phase'], 'active')
        self.assertNotIn(NIGHT, self.proxy.available_events)
        ordinary = copy.deepcopy(self.proxy.story['city_values'])
        profile = copy.deepcopy(self.proxy.profile)
        for number in range(3):
            self.proxy.handle_city_action('enterPatrolRequest', {'aid': 1, 'hs': []}, 'admit-%s' % number)
            self.assertEqual(self.proxy.story['route20_huisu']['used_actions'], number + 1)
            # Exact retry and a same-admission resume do not consume another slot.
            self.proxy.handle_city_action('enterPatrolRequest', {'aid': 1, 'hs': []}, 'admit-%s' % number)
            self.assertEqual(self.proxy.story['route20_huisu']['used_actions'], number + 1)
            if number == 0:
                self.assertIn(PATROL, self.proxy.available_events)
                self.start(PATROL, 6)
                self.trace(76502)
                self.proxy.process_story('option', {'e': PATROL, 'se': CHILD})
                self.assertIsNone(self.proxy.city_actions['patrol'])
                self.assertIn(CHILD, self.proxy.processing_events)
                self.trace(76503)
                self.assertIn(CHILD, self.proxy.completed_events)
            else:
                self.proxy.handle_city_action('patrolReward', {}, 'claim-%s' % number)
        self.proxy.handle_city_action('enterPatrolRequest', {'aid': 1, 'hs': []}, 'fourth')
        self.assertIsNone(self.proxy.city_actions['patrol'])
        self.assertEqual(self.proxy.story['city_values'], ordinary)
        self.assertEqual(self.proxy.profile, profile)
        durable = self.proxy._store.load()
        self.assertEqual(durable['story']['route20_huisu']['used_actions'], 3)
        self.assertEqual(huisu.project_huisu(durable), {'hs': [], 'hsf': True, 'hst': 3, 'lhs': False})
        gateway.validate_gateway_progress(durable)

    def test_save_failure_and_publication_failure_keep_atomic_entry_and_replay_animation(self):
        previous = self.proxy.progress_snapshot()
        self.owner.replies.clear()
        with patch.object(self.proxy, 'save_progress', side_effect=IOError('disk full')):
            with self.assertRaises(IOError):
                self.proxy.process_huisu_operation('requestStoryhuisu', {}, huisu.huisu_request_source(previous), 31, 'entry-1', self.owner)
        self.assertEqual(self.proxy.progress_snapshot(), previous)
        self.assertIn('serverCallbackCarrier', [name for name, payload in self.owner.replies])
        source = huisu.huisu_request_source(previous)
        real_reply = self.proxy.reply
        def publish(name, payload, callback_id=None):
            if name == 'syncRoute':
                raise IOError('publication')
            return real_reply(name, payload, callback_id)
        self.owner.replies.clear()
        with patch.object(self.proxy, 'reply', side_effect=publish):
            with self.assertRaises(IOError):
                self.proxy.process_huisu_operation('requestStoryhuisu', {}, source, 31, 'entry-1', self.owner)
        self.assertEqual([name for name, payload in self.owner.replies], ['serverCallbackCarrier'])
        committed = self.proxy._store.load()
        self.assertEqual(committed['story']['route20_huisu']['generation'], 1)
        self.owner.replies.clear()
        self.proxy.process_huisu_operation('requestStoryhuisu', {}, source, 31, 'entry-1', self.owner)
        self.assertEqual([name for name, payload in self.owner.replies][:2], ['syncRoute', 'syncHuiSuData'])
        self.assertEqual(self.proxy.story['huisu_generation'], 1)

    def test_queued_entry_and_out_sources_cannot_rebind_after_context_change(self):
        source = huisu.huisu_request_source(self.proxy.progress_snapshot())
        self.proxy.story['date'] = 1
        self.proxy.day['stock_day'] = 1
        self.tables['story_dream'][('20', 1)] = {'event': ENTRY, 'goodnight_event': NIGHT}
        self.proxy.process_huisu_operation('requestStoryhuisu', {}, source, 31, 'old-entry', self.owner)
        self.assertNotIn('route20_huisu', self.proxy.story)
        self.proxy.story['date'] = self.proxy.day['stock_day'] = 0
        self.enter()
        token = huisu.huisu_token(self.proxy.progress_snapshot())
        self.proxy.story['route20_huisu']['generation'] += 1
        self.proxy.story['huisu_generation'] += 1
        self.proxy.process_huisu_operation('requestStoryhuisuOut', {}, token, source_owner=self.owner)
        self.assertEqual(self.proxy.story['route20_huisu']['phase'], 'entering')

    def test_fresh_original_opening_seed_starts_without_fabricated_predecessor(self):
        opening = json.loads((ROOT / 'tests/fixtures/opening-story.json').read_text())
        row = opening['content']['1000']
        trigger = opening['triggers']['1000']
        trigger = dict(trigger, conds={int(kind): value for kind, value in trigger['conds'].items()})
        self.assertEqual(trigger['conds'][1], 'set([6])')
        self.table('event_content', {1000: row})
        self.table('event_condition', {1000: trigger})
        fresh = gateway.LocalProxy(None, self.owner, persistent=False)
        fresh.prepare_story_gate = lambda state, event: (state, [])
        fresh.process_week_handoffs = lambda: None
        self.assertIn(1000, fresh.available_events)
        self.assertNotIn(6, fresh.completed_events)
        self.assertFalse(engine.evaluate_story_trigger(trigger, fresh.progress_snapshot()))
        # Native create_avatar runs this refresh path before its first snapshot.
        fresh.ensure_postbattle_progress()
        self.assertIn(1000, fresh.available_events)
        self.assertEqual(fresh.story['available_origins']['1000']['source'], 'offline-initial-seed')
        fresh.reliable_call({'w': {'m': 'startEvent', 'r': 300, 'p': {'e': 1000}}})
        self.assertIn(1000, fresh.processing_events)
        self.assertIn(('startEventReply', {'e': 1000, 'r': 1}), self.owner.replies)
        self.assertNotIn(1000, fresh.completed_events)
        self.assertNotIn(6, fresh.completed_events)
        self.assertNotIn('route20_huisu', fresh.story)
        self.assertNotIn('event_contexts', fresh.story)
        self.assertNotIn('1000', fresh.story['available_origins'])

        # An unmarked archive and incompatible real facts get no seed exception.
        for mutation in ('missing_origin', 'wrong_route', 'not_emergency', 'unreleased', 'mutex', 'different_predecessor'):
            candidate = gateway.LocalProxy(None, self.owner, persistent=False).progress_snapshot()
            original_row, original_trigger = copy.deepcopy(row), copy.deepcopy(trigger)
            if mutation == 'missing_origin': candidate['story'].pop('available_origins')
            if mutation == 'wrong_route': candidate['story']['route'] = '20'
            if mutation == 'not_emergency': candidate['story']['emergency'] = False
            if mutation == 'unreleased': original_row['release'] = False
            if mutation == 'mutex':
                original_row['mutexEvent'] = [321]
                candidate['completed_events'] = [321]
            if mutation == 'different_predecessor': original_trigger['conds'][1] = 'set([777])'
            engine.refresh_story_events(candidate, {1000: original_trigger}, {1000: original_row})
            self.assertNotIn(1000, dict(candidate['available_events']), mutation)
            self.assertNotIn(6, candidate['completed_events'])

    def test_initial_original_statuscheck_allows_confirmed_rest_with_av_preserved(self):
        before = copy.deepcopy(self.proxy.story['city_values'])
        self.proxy.process_day_operation('statusCheck', {'s': 'nextday'})
        self.assertIn(('statusCheckReply', {'r': 'ok', 's': 'nextday'}), self.owner.replies)
        self.assertEqual({key: self.proxy.story['city_values'][key] for key in before}, before)
        self.assertNotIn('route20_huisu', self.proxy.story)
        self.assertNotIn(102, self.proxy.conditions)

    def test_reload_preserves_generation_and_old_queued_starts_cannot_bind_to_new_context(self):
        self.enter()
        self.rest_intent()
        self.start(ENTRY, 100)
        self.trace(76501)
        self.proxy.handle_city_action('enterPatrolRequest', {'aid': 1, 'hs': []}, 'saved-admission')
        state = self.proxy.progress_snapshot()
        reloaded = gateway.LocalProxy(None, self.owner, persistent=True)
        self.assertEqual(reloaded.story['route20_huisu'], self.proxy.story['route20_huisu'])
        self.assertEqual(json.loads(json.dumps(reloaded.city_actions)), json.loads(json.dumps(self.proxy.city_actions)))
        old_token = huisu.huisu_token(state)
        changed = copy.deepcopy(state)
        value = changed['story']['route20_huisu']
        value['generation'] += 1
        changed['story']['huisu_generation'] += 1
        new_token = old_token.rsplit(':', 1)[0] + ':' + str(value['generation'])
        for admission in value['admissions'].values():
            admission['token'] = new_token
        changed['city_actions']['patrol']['context_token'] = new_token
        reloaded.restore_progress(changed)
        before = reloaded.progress_snapshot()
        reloaded.reliable_call({'w': {'m': 'startEvent', 'r': 101, 'p': {'e': PATROL}}},
            source_owner=self.owner, source_huisu_token=old_token)
        reloaded.handle_city_action('enterPatrolRequest', {'aid': 1, 'hs': []}, 'old-context-admission',
            source_context=(self.owner, old_token))
        self.assertEqual(reloaded.progress_snapshot(), before)
        self.assertNotIn(PATROL, reloaded.processing_events)

    def test_owner_replacement_drops_queued_entry_city_and_exit(self):
        original_owner = self.owner
        source = huisu.huisu_request_source(self.proxy.progress_snapshot())
        self.proxy.owner = SimpleNamespace(id='replacement-owner')
        before = self.proxy.progress_snapshot()
        self.proxy.process_huisu_operation('requestStoryhuisu', {}, source, 31, 'old-owner-entry', original_owner)
        self.proxy.process_huisu_operation('requestStoryhuisuOut', {}, None, source_owner=original_owner)
        self.proxy.handle_city_action('enterPatrolRequest', {'aid': 1, 'hs': []}, 'old-owner-city',
            source_context=(original_owner, None))
        self.assertEqual(self.proxy.progress_snapshot(), before)

    def test_original_source_consumer_syncroute_animation_and_full_sync_replay(self):
        def original_method(filename, name, namespace):
            lines = (ROOT / filename).read_text().splitlines()
            start = next(i for i, line in enumerate(lines) if line.startswith('    def ' + name + '('))
            end = next((i for i in range(start + 1, len(lines))
                if lines[i].startswith('    def ') or lines[i].startswith('    @')), len(lines))
            exec(compile(textwrap.dedent('\n'.join(lines[start:end])) + '\n', filename + ':' + name, 'exec'), namespace)
            return namespace[name]
        calls = []
        city = SimpleNamespace(notify_huisu_enter=lambda: calls.append('enter'),
            notify_story_custom=lambda: calls.append('refresh'),
            recover_storyline=lambda: calls.append('recover'))
        tree = SimpleNamespace(proc_event=lambda *args, **kwargs: None)
        native_story = SimpleNamespace(route='20', subRouteTarget=[], huisu=[], huisu_flag=False,
            huisu_time=0, leave_huisu=False, flashback_flag=False)
        native_owner = SimpleNamespace(storyData=native_story)
        gg = SimpleNamespace(avatar=native_owner, ui=SimpleNamespace(panels=SimpleNamespace(city=city), _tree=tree))
        namespace = {'gg': gg}
        for name in ('syncRoute', 'syncHuisu', 'syncFlashback', 'syncSubStoryTarget'):
            setattr(native_story, name, types.MethodType(original_method('analysis/decompiled/StoryData.py', name, namespace), native_story))
        route_method = original_method('analysis/decompiled/StoryMember.py', 'syncRoute', namespace)
        full_method = original_method('analysis/decompiled/StoryMember.py', 'syncHuiSuData', namespace)
        state, notices, changed, diag = huisu.prepare_huisu_operation(self.proxy.progress_snapshot(),
            'requestStoryhuisu', {}, self.tables, operation_id='native-consumer')
        for name, payload in notices:
            if name == 'syncRoute':
                route_method(native_owner, payload['rt'], payload['srt'], payload['i'], payload['hsd'], payload['fbd'])
            else:
                full_method(native_owner, payload['d'])
        self.assertEqual(calls, ['enter'])
        self.assertTrue(native_story.huisu_flag)
        self.assertEqual(native_story.huisu, [])
        replay = huisu.prepare_huisu_operation(state, 'requestStoryhuisu', {}, self.tables,
            operation_id='native-consumer')[1]
        for name, payload in replay:
            if name == 'syncRoute':
                route_method(native_owner, payload['rt'], payload['srt'], payload['i'], payload['hsd'], payload['fbd'])
            else:
                full_method(native_owner, payload['d'])
        self.assertEqual(calls, ['enter', 'refresh'])

    def test_snapshot_defaults_clear_legacy_template_without_inferring_context(self):
        snapshot = apply_event_effects_snapshot(self.proxy.progress_snapshot(),
            {'std': {'hsu': [99], 'hsf': True, 'hst': 3, 'lhs': True}})
        self.assertEqual({k: snapshot['std'][k] for k in ('hsu', 'hsf', 'hst', 'lhs')},
            {'hsu': [], 'hsf': False, 'hst': 0, 'lhs': False})
        self.assertNotIn('route20_huisu', self.proxy.story)

# This subclass reuses setup only; inherited tests have their own separate suite.
for _name in tuple(vars(integrations.IntegratedGatewayTests)):
    if _name.startswith('test_'):
        setattr(HuisuGatewayTests, _name, None)

if __name__ == '__main__':
    unittest.main()
