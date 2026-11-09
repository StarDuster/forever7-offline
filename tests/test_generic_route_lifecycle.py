"""Mechanism-level lifecycle tests; no story traversal or device input."""
import copy
import json
import unittest
import test_offline_day as day_fixtures
import test_offline_week as week_fixtures
from offline_day import prepare_gateway_day_operation
from offline_event_effects import apply_event_effects_snapshot
from offline_story import initial_story_state
from offline_week import prepare_week_route_handoff, prepare_week_transition
from offline_yumi import ensure_yumi, yumi_projection


class GenericRouteLifecycleTests(unittest.TestCase):
    def test_real_route_handoff_initializes_once_and_replay_preserves_value(self):
        fixture = week_fixtures.WeekCycleTests(); fixture.setUp()
        state = copy.deepcopy(fixture.state)
        event = 987654321
        state['completed_events'] = [event]
        handoff = {'kind': 'route', 'event': event, 'route': '7-1', 'token': 'route:%s' % event}
        content = {event: {'release': True, 'enterStoryRoute': '7-1'}}
        with self.assertRaises(ValueError):
            prepare_week_route_handoff(dict(state, completed_events=[]), handoff, content, fixture.tables['routes'])
        candidate, notices, changed = prepare_week_route_handoff(state, handoff, content, fixture.tables['routes'])
        self.assertTrue(changed)
        self.assertEqual(candidate['story']['baiyu_value'], 50)
        self.assertEqual(notices[-1][0], 'syncBaiyuInfos')
        candidate['story']['yumi']['byv'] = candidate['story']['baiyu_value'] = 56
        again, notices, changed = prepare_week_route_handoff(candidate, handoff, content, fixture.tables['routes'])
        self.assertFalse(changed)
        self.assertEqual(again['story']['baiyu_value'], 56)
        self.assertNotIn('yumi', state['story'])

    def test_new_week_erases_route_state_and_overlays_stale_original_template(self):
        fixture = week_fixtures.WeekCycleTests(); fixture.setUp()
        state = fixture.earned()
        story = state['story']
        ensure_yumi(story).update(byv=80, ysg=True, ycyo=True, ycn=13)
        story.update(baiyu_value=80, wulu_special_goodnight=True, jiaohui_special_goodnight=True,
                     wuluClue=[12], wuluClueReaded=True, wuluDetailReaded=[[12, True]])
        new, notices, changed = prepare_week_transition(state, 'handleIncWeekAsk', 'generic:week', fixture.tables)
        self.assertTrue(changed)
        stale = {'std': {'ysg': True, 'wsg': True, 'jsg': True, 'ycyo': True,
                         'byv': 80, 'wlc': [12], 'wlr': True, 'wldr': [[12, True]]}}
        projected = apply_event_effects_snapshot(new, stale)['std']
        self.assertEqual(projected['byv'], 50)
        for key in ('ysg', 'wsg', 'jsg', 'ycyo', 'wlr'):
            self.assertFalse(projected[key])
        self.assertEqual(projected['wlc'], [])
        self.assertEqual(projected['wldr'], [])
        # Weekly fatigue restoration is expected; permanent assets must match.
        assets = []
        for profile in (new['profile'], state['profile']):
            value = copy.deepcopy(profile)
            for hero in value['heroes'].values():
                hero.pop('cf', None); hero.pop('cfd', None)
            assets.append(value)
        self.assertEqual(*assets)

    def test_day_commit_resets_nights_once_replay_projects_current_state(self):
        fixture = day_fixtures.DayProtocolTests(); fixture.setUp()
        state = {'story': dict(initial_story_state(), week=2, date=93,
                    city_values={k: v for k, v in fixture.state['city'].items() if k != 'areas'},
                    city_areas={'1': {'id': 1}}, wulu_special_goodnight=True,
                    jiaohui_special_goodnight=True, wuluClue=[12]),
                 'profile': copy.deepcopy(fixture.state['profile']), 'conditions': [[101, 0]]}
        ensure_yumi(state['story']).update(ysg=True, ycyo=True, ycn=17)
        original = copy.deepcopy(state)
        checked, _, _, _ = prepare_gateway_day_operation(state, 'statusCheck', {'s': 'nextday'}, [], stock_day=3)
        self.assertTrue(checked['story']['yumi']['ysg'])
        armed, _, _, _ = prepare_gateway_day_operation(checked, 'updateEventCondClient', {'c': 102, 'v': '4'})
        failed, _, changed, _ = prepare_gateway_day_operation(armed, 'incDayWhenNoActionVal', {}, [], None)
        self.assertFalse(changed)
        self.assertTrue(failed['story']['yumi']['ysg'])
        done, notices, changed, _ = prepare_gateway_day_operation(armed, 'incDayWhenNoActionVal', {}, [], fixture.plan)
        self.assertTrue(changed)
        self.assertEqual([n for n, p in notices[:3]], ['syncBaiyuInfos', 'syncWuluLineData', 'syncJiaohuiSpecialNight'])
        self.assertFalse(done['story']['yumi']['ysg'])
        self.assertTrue(done['story']['yumi']['ycyo'])
        self.assertEqual(done['story']['yumi']['ycn'], 17)
        self.assertEqual(done['story']['wuluClue'], [12])
        self.assertEqual(state, original)
        # A late retry must repair the renderer using CURRENT flags; it must
        # neither clear a new day's earned flag nor replay old full clue data.
        done['story']['wulu_special_goodnight'] = True
        done['story']['wuluClue'].append(13)
        again, replay, changed, diag = prepare_gateway_day_operation(done, 'incDayWhenNoActionVal', {}, [])
        self.assertFalse(changed); self.assertTrue(diag['replay'])
        self.assertEqual(again, done)
        wulu = next(p for n, p in replay if n == 'syncWuluLineData')
        self.assertTrue(wulu['wsg']); self.assertEqual(wulu['wlc'], [12, 13])

    def test_legacy_value_projection_is_pure_and_preserved(self):
        story = {'route': '7', 'baiyu_value': 67}
        before = copy.deepcopy(story)
        self.assertEqual(yumi_projection(story)['byv'], 67)
        self.assertEqual(story, before)
        self.assertEqual(json.loads(json.dumps(story)), before)
