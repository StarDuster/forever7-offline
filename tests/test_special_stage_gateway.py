"""True LocalProxy special320 admission/result adapter contracts; host only."""
import copy
import hashlib
from pathlib import Path
import sys
import unittest
from unittest.mock import patch
ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT/'tests'),str(ROOT/'tools'),str(ROOT/'runtime'),str(ROOT/'analysis/research-agent')]
import test_gateway_integrations as fixtures
from read_data_table import read
from read_literal_marshal import read as read_marshal
from test_offline_event_effects import original_tables
from offline_special_city_stage import validate_special_city_stages


class SpecialStageGatewayTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.content = read(ROOT/'analysis/decompiled/event_content.py')
        cls.tables = original_tables()
        base = ROOT/'analysis/android640-scripts/com/data/cdata'
        cls.chapters = read_marshal(base/'chapter_mission_data.marshal')
        cls.routes = read_marshal(base/'story_route.marshal')
        cls.notes = read(ROOT/'analysis/decompiled/notepad.py')

    def setUp(self):
        self.boot()

    def boot(self, force=50):
        self.f = fixtures.IntegratedGatewayTests(methodName='runTest')
        self.f.setUp()
        self.addCleanup(self.f.doCleanups)
        self.proxy = self.f.proxy
        for name in ('mission','city_data','reward_common','cg_data','hero'):
            self.f.table(name,self.tables[name])
        self.f.table('event_content',self.content)
        self.f.table('chapter_mission_data',self.chapters)
        self.f.table('story_route',self.routes)
        self.f.table('ending_data',{})
        self.f.table('notepad',self.notes)
        self.proxy.story['route'] = '1'
        self.proxy.story['city_areas']['6'] = {'id':6,'st':[2,False,False],'lv':1,'bd':{},'stage':{'cs':5101,'sl':[[5101]]}}
        self.proxy.story['city_values']['fv'] = force
        # Host entry availability fixture; subsequent original dialogue, handoff,
        # source effect, native-calculator adapter and accepted result are real.
        self.proxy.available_events = {1129:1}
        self.proxy.reliable_call({'w':{'m':'startEvent','p':{'e':1129},'r':1129}})
        self.proxy.process_story('trace',{'k':'dialog','d':{'c':1129}})
        self.assertEqual(self.proxy.story['route'],'10-6')
        self.assertIn('route:1129',self.proxy.week_protocol['consumed_handoffs'])
        self.proxy.available_events[1140] = 1
        self.proxy.reliable_call({'w':{'m':'startEvent','p':{'e':1140},'r':1140}})
        self.assertIn(1140,self.proxy.completed_events)
        self.assertEqual(self.proxy.story['city_areas']['6']['stage'],{'cs':320,'sl':[[320]]})
        # The commit is produced by the original event-effect owner, not by a
        # hand-written city field: receipt + areaFight6 + selector context.
        document = self.proxy.story['special_city_stages']
        context = document['contexts']['6']
        self.assertEqual(context['source']['event'],1140)
        self.assertEqual(context['source']['route_source']['event'],1129)
        self.assertTrue(context['source']['receipt'])
        self.assertEqual(self.proxy.story['event_effect_receipts'][context['source']['receipt']],1140)
        self.assertEqual(context['descriptor']['key'],[6,0,'10-6',11])
        self.assertEqual(context['descriptor']['members'],[320])
        self.assertEqual(context['descriptor']['missions']['320']['fatigue'],5)
        self.assertEqual(context['descriptor']['missions']['320']['overFatigue'],25)
        self.assertEqual(context['descriptor']['missions']['320']['va'],2)
        self.assertEqual(context['before_stage'],{'cs':5101,'sl':[[5101]]})
        self.assertEqual(context['last_stage'],{'cs':320,'sl':[[320]]})
        self.assertEqual(context['week'],self.proxy.story['week'])
        self.assertEqual(context['route'],'10-6')
        validate_special_city_stages(self.proxy.progress_snapshot())
        weights = self.f.stage['reward_pool304']['weights']
        total = sum(w for _,w in weights)
        uid = next('%024x'%n for n in range(320000,321000)
            if int(hashlib.sha256(('stage-drop-v1:%024x:304:0'%n).encode()).hexdigest(),16)%total < 147000)
        self.f.modules['common.IdManager'].IdManager.genid = lambda:uid
        self.proxy.handle_battle_admission({'t':1,'s':320,'h':[24],'d':{'a':6}},7)
        self.active = copy.deepcopy(self.proxy.battle['active'])
        self.assertIsNotNone(self.active)
        self.assertIn('special_city_stage_source',self.active)
        self.result = {'t':1,'s':320,'h':[24],'x':[],'w':1,'e':{}}
        self.f.owner.replies[:] = []

    def test_actual_win_offers_original_terminal_once_without_free_area_or_edges(self):
        self.assertEqual(self.active['costs'],{'actions':2,'fatigue':5})
        actions = self.proxy.story['city_values']['av']
        fatigue = self.proxy.profile['heroes']['24']['cf']
        self.assertNotIn(1132,self.proxy.available_events)
        self.proxy.handle_battle_finish(self.result,self.active['fight_id'])
        self.assertEqual(self.proxy.story['city_values']['av'],actions-2)
        self.assertEqual(self.proxy.day['actions_spent'],2)
        self.assertEqual(self.proxy.profile['heroes']['24']['cf'],fatigue-5)
        self.assertIn(('updateCurFatigueValue',{'h':24,'v':fatigue-5}),self.f.owner.replies)
        self.assertIsNone(self.proxy.battle['active'])
        self.assertIn(1132,self.proxy.available_events)
        self.assertNotIn(1132,self.proxy.completed_events)
        self.assertEqual(self.proxy.story['available_origins']['1132'],{'source':'accepted_mission_result',
            'fight_id':self.active['fight_id'],'scene':320,'outcome':1})
        self.assertEqual(self.proxy.story['city_areas']['6']['st'][0],1)
        self.assertEqual(self.proxy.story['city_areas']['6']['stage']['cs'],0)
        self.assertNotIn('3101',self.proxy.story.get('condition_mission_edges',{}))
        self.assertNotIn('4101',self.proxy.story.get('condition_mission_edges',{}))
        snapshot = self.proxy.progress_snapshot()
        self.proxy.handle_battle_finish(self.result,self.active['fight_id'])
        self.assertEqual(self.proxy.progress_snapshot(),snapshot)
        projections = [payload for name,payload in self.f.owner.replies if name == 'get_all_area_info_reply']
        self.assertTrue(projections)
        # Source projection precedes the ordinary accepted battle settlement.
        # The latter retains its existing sm=True policy and changes no status.
        self.assertIs(projections[0]['sm'],False)
        self.assertIs(projections[-1]['sm'],True)
        self.assertTrue(all(p['ais']['area_6']['st'][0] == 1 for p in projections))

    def test_actual_loss_and_duplicate_offer_no_terminal_cost_or_reward(self):
        self.result['w'] = 0
        before = copy.deepcopy(self.proxy.profile)
        actions = self.proxy.story['city_values']['av']
        fatigue = self.proxy.profile['heroes']['24']['cf']
        self.proxy.handle_battle_finish(self.result,self.active['fight_id'])
        self.assertIsNone(self.proxy.battle['active'])
        self.assertNotIn(1132,self.proxy.available_events)
        self.assertEqual(self.proxy.profile,before)
        self.assertEqual(self.proxy.story['city_values']['av'],actions)
        self.assertEqual(self.proxy.profile['heroes']['24']['cf'],fatigue)
        self.assertNotIn('updateCurFatigueValue',[name for name,_ in self.f.owner.replies])
        self.assertEqual(self.proxy.story['city_areas']['6']['stage']['cs'],320)
        snapshot = self.proxy.progress_snapshot()
        self.proxy.handle_battle_finish(self.result,self.active['fight_id'])
        self.assertEqual(self.proxy.progress_snapshot(),snapshot)

    def test_actual_win_save_failure_rolls_back_terminal_and_typed_source_then_retries(self):
        before = self.proxy.progress_snapshot()
        with patch.object(self.proxy._store,'write',side_effect=OSError('disk full')):
            with self.assertRaises(OSError):self.proxy.handle_battle_finish(self.result,self.active['fight_id'])
        self.assertEqual(self.proxy.progress_snapshot(),before)
        self.assertNotIn(1132,self.proxy.available_events)
        self.assertEqual(self.f.owner.replies,[])
        self.proxy.handle_battle_finish(self.result,self.active['fight_id'])
        self.assertIn(1132,self.proxy.available_events)

    def test_gateway_area_stage_query_reads_the_committed_selector_projection(self):
        self.f.owner.replies[:] = []
        self.proxy.reliable_call({'w':{'m':'getAreaStagesRequest','p':{'aid':6},'r':900}})
        query = [payload for name,payload in self.f.owner.replies
            if name == 'get_area_stages_reply' and payload['ai'] == 6]
        self.assertEqual(query[-1],{'ai':6,'st':{'cs':320,'sl':[[320]]}})
        self.proxy.handle_battle_finish(self.result,self.active['fight_id'])
        self.f.owner.replies[:] = []
        self.proxy.reliable_call({'w':{'m':'getAreaStagesRequest','p':{'aid':6},'r':901}})
        query = [payload for name,payload in self.f.owner.replies
            if name == 'get_area_stages_reply' and payload['ai'] == 6]
        self.assertEqual(query[-1],{'ai':6,'st':{'cs':0,'sl':[[320]]}})

    def test_low_force_admission_pins_overfatigue25_and_settles_it_once(self):
        self.boot(force=0)
        self.assertEqual(self.active['costs'],{'actions':2,'fatigue':25})
        actions = self.proxy.story['city_values']['av']
        fatigue = self.proxy.profile['heroes']['24']['cf']
        self.proxy.handle_battle_finish(self.result,self.active['fight_id'])
        self.assertIn(1132,self.proxy.available_events)
        self.assertEqual(self.proxy.story['city_values']['av'],actions-2)
        self.assertEqual(self.proxy.profile['heroes']['24']['cf'],fatigue-25)
        self.assertIn(('updateCurFatigueValue',{'h':24,'v':fatigue-25}),self.f.owner.replies)
        snapshot = self.proxy.progress_snapshot()
        self.proxy.handle_battle_finish(self.result,self.active['fight_id'])
        self.assertEqual(self.proxy.progress_snapshot(),snapshot)

    def test_original_1132_consumer_frees_area6_without_successors_or_fake_win(self):
        self.proxy.handle_battle_finish(self.result,self.active['fight_id'])
        self.assertIn(1132,self.proxy.available_events)
        self.proxy.available_events[1132] = 1
        self.proxy.reliable_call({'w':{'m':'startEvent','p':{'e':1132},'r':1132}})
        self.proxy.process_story('trace',{'k':'dialog','d':{'c':1132}})
        self.assertIn(1132,self.proxy.processing_events)
        self.assertEqual(self.proxy.story['city_areas']['6']['st'][0],1)
        self.proxy.process_story('ui_complete',{'e':1132})
        self.assertIn(1132,self.proxy.processing_events)
        self.assertEqual(self.proxy.story['city_areas']['6']['st'][0],1)
        self.proxy.process_story('option',{'e':1132,'se':1133,'op':0})
        self.assertIn(1132,self.proxy.completed_events)
        self.assertNotIn(1132,self.proxy.available_events)
        self.assertEqual(self.proxy.story['city_areas']['6']['st'][0],0)
        self.assertEqual(self.proxy.story['city_areas']['6']['stage']['cs'],0)
        self.assertIn(1133,self.proxy.processing_events)
        self.assertNotIn(1133,self.proxy.completed_events)
        self.assertNotIn('3101',self.proxy.story.get('condition_mission_edges',{}))
        self.assertNotIn('4101',self.proxy.story.get('condition_mission_edges',{}))
        self.assertNotIn(3101,self.proxy.completed_events)
        self.assertNotIn(4101,self.proxy.completed_events)


if __name__ == '__main__':unittest.main()
