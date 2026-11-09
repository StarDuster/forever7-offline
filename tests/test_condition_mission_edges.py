"""Original graph fixtures; result inputs model accepted wins, not native QA."""
import copy
import sys
import unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT/'runtime'), str(ROOT/'analysis/research-agent')]
from test_offline_event_effects import original_tables, base_state
from offline_stage import (prepare_stage_admission, prepare_stage_finish,
    condition_mission_stage, original_mission_prerequisites_met,
    record_original_mission_edges, refresh_condition_city_missions)


class OriginalMissionEdgeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tables = original_tables()

    def state(self):
        state = base_state(self.tables)
        state.update(conditions=[], event_traces=[])
        state['story'].update(week=0,date=0,route='1',emergency=False,
            city_values={'av':24,'fv':200,'rv':0,'dv':0,'bf':0})
        for aid in range(1,9):
            state['story']['city_areas'][str(aid)] = {'id':aid,'lv':1,'bd':{},'st':[0,False,False]}
        state['day'] = {'stock_day':0}
        state['battle'] = {'version':1,'active':None,'receipts':[]}
        return state

    def finish(self, state, scene, win):
        aid = self.tables['mission'][scene]['ch']
        fight = 'host-original-edge-%s'%scene
        active, changed = prepare_stage_admission(state, {'t':1,'s':scene,'h':[24],'d':{'a':aid}}, self.tables['mission'], lambda:fight)
        def settle(admission, actual):
            return dict(actual,r={'money':1} if actual['w'] else {}), {'profile':copy.deepcopy(state['profile']),'notices':[],'granted':[]}
        return prepare_stage_finish(active, {'t':1,'s':scene,'h':[24],'x':[],'w':win}, self.tables['mission'], self.tables['city_data'], settle, fight)[0]

    def test_actual_cross_area_wins_activate_original_cond_targets_without_event_root(self):
        for source, prior, target in ((2118,2117,1114),(3120,3119,2113)):
            with self.subTest(source=source,target=target):
                state = self.state()
                source_area = self.tables['mission'][source]['ch']
                target_area = self.tables['mission'][target]['ch']
                story = state['story']
                story['battle_wins'] = [prior]
                story['current_mission_wins'] = [prior]
                story['condition_mission_roots'] = {str(source_area):source}
                story['condition_mission_sources'] = {str(source_area):prior}
                story['city_areas'][str(source_area)]['st'][0] = 1
                story['city_areas'][str(target_area)]['st'][0] = 1
                stage, family = condition_mission_stage(story,self.tables['mission'],source,set())
                story['city_areas'][str(source_area)]['stage'] = stage
                lost = self.finish(state,source,0)
                self.assertNotIn(str(target_area),lost['story']['condition_mission_roots'])
                won = self.finish(state,source,1)
                self.assertEqual(won['story']['city_areas'][str(target_area)]['stage']['cs'],target)
                self.assertEqual(won['story']['condition_mission_sources'][str(target_area)],source)
                self.assertNotIn(target,won['story']['current_mission_wins'])
                self.assertNotIn(target,won['story']['battle_wins'])

    def test_original4112_next_edges_survive_family_completion_and_wait_for_area_authorization(self):
        state = self.state()
        state['completed_events'] = [1060]
        story = state['story']
        story['current_mission_wins'] = [4111]
        story['battle_wins'] = [4111]
        story['condition_mission_roots'] = {'5':4112}
        story['city_areas']['5']['st'][0] = 1
        story['city_areas']['3']['st'][0] = 1
        story['city_areas']['5']['stage'] = condition_mission_stage(story,self.tables['mission'],4112,{1060})[0]
        won = self.finish(state,4112,1)
        self.assertEqual(won['story']['city_areas']['3']['stage']['cs'],2107)
        self.assertEqual(won['story']['city_areas']['2']['st'][0],0)
        self.assertEqual(won['story']['condition_mission_edges']['1108'],[4112])
        self.assertTrue(any(edge['target']==1108 and 'waits_for_original_area' in edge['reason'] for edge in won['story']['pending_mission_edges']))

    def test_original_alternative_merge_nodes_accept_each_proven_incoming_entrance(self):
        for target in (1115,2114,6105,3106):
            row = self.tables['mission'][target]
            self.assertFalse(original_mission_prerequisites_met(self.tables['mission'],target,set()))
            for parent in row['cond']:
                self.assertIn(target,self.tables['mission'][parent]['nextstagenums'])
                self.assertTrue(original_mission_prerequisites_met(self.tables['mission'],target,{parent}))

    def test_edge_recording_cannot_create_proof_before_current_actual_source_win(self):
        story = self.state()['story']
        with self.assertRaises(ValueError):
            record_original_mission_edges(story,self.tables['mission'],4112)
        self.assertNotIn('condition_mission_edges',story)

    def test_later_refresh_can_reconcile_previously_completed_root_event(self):
        state = self.state()
        state['completed_events'] = [1060]
        state['story']['event_history'] = [1060]
        state['story']['city_areas']['3']['st'][0] = 1
        refresh_condition_city_missions(state,self.tables['mission'],60083,self.tables['city_data'])
        self.assertEqual(state['story']['city_areas']['3']['stage']['cs'],2107)
        self.assertNotIn(2107,state['story']['battle_wins'])

    def test_locked_or_sentinel_guard_target_keeps_edge_pending_without_unlock(self):
        state = self.state()
        state['story']['current_mission_wins'] = [2118]
        state['story']['battle_wins'] = [2118]
        state['story']['city_areas']['2']['st'] = [1,False,True]
        record_original_mission_edges(state['story'],self.tables['mission'],2118)
        refresh_condition_city_missions(state,self.tables['mission'],city_catalog=self.tables['city_data'])
        self.assertTrue(state['story']['city_areas']['2']['st'][2])
        self.assertNotIn('2',state['story']['condition_mission_roots'])
        self.assertTrue(any(edge['target']==1114 and edge['reason']=='original_target_area_locked' for edge in state['story']['pending_mission_edges']))
