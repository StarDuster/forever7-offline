"""Original rescue branch via real host admission/result and event proof."""
import copy
from pathlib import Path
import sys
import unittest
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'runtime'),str(ROOT/'tools')]
from test_offline_event_effects import original_tables,base_state,read_source
from offline_stage import prepare_stage_admission,prepare_stage_finish
from offline_story_engine import refresh_story_events,begin_story_occurrence,prepare_story_operation
from offline_gacha import new_gacha_state,validate_gacha_state


class SchoolRescueProgressionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tables=original_tables()
        cls.content=read_source(ROOT/'analysis/decompiled/event_content.py')
        triggers=read_source(ROOT/'analysis/decompiled/event_condition.py')
        cls.triggers={20007:triggers[20007]}
    def setUp(self):
        self.state=base_state(self.tables)
        self.state.update(conditions=[],event_traces=[],completed_events=[20003],
            day={'stock_day':0},battle={'version':1,'active':None,'receipts':[]})
        self.state['gacha']=new_gacha_state()
        self.state['gacha']['items']=[{'i':54,'u':'a'*24,'w':1,'tt':3}]
        self.state['story'].update(week=0,date=0,route='1',emergency=False,
            battle_wins=[101,1101,1102,1103,1104],
            city_values={'av':24,'fv':200,'rv':0,'dv':0,'bf':0},
            city_areas={str(a):{'id':a,'lv':1,'bd':{},'st':[0 if a==1 else 1 if a==2 else 2,False,False]}for a in range(1,9)})
        self.state['story']['city_areas']['2']['stage']={'cs':1105,'sl':[[1105],[1106]]}
    def fight(self,state,scene,win):
        fid='actual-source-%s'%scene
        active,changed=prepare_stage_admission(state,{'t':1,'s':scene,'h':[24],'d':{'a':2}},self.tables['mission'],lambda:fid)
        def settle(admission,result):
            return dict(result,r={'money':1}if win else {}),{'profile':copy.deepcopy(state['profile']),'notices':[],'granted':[]}
        result={'t':1,'s':scene,'h':[24],'x':[],'w':win}
        return prepare_stage_finish(active,result,self.tables['mission'],self.tables['city_data'],settle,fid)
    def rescue(self,state):
        refresh_story_events(state,self.triggers,self.content)
        self.assertIn(20007,dict(state['available_events']))
        state['available_events']=[r for r in state['available_events']if r[0]!=20007]
        state['processing_events'].append(20007)
        begin_story_occurrence(state,20007)
        state,notices=prepare_story_operation(state,'start',{'e':20007},self.content,self.triggers,self.tables)
        self.assertNotIn(20007,state['completed_events'])
        state,notices=prepare_story_operation(state,'trace',{'k':'dialog','d':{'c':20007}},self.content,self.triggers,self.tables)
        self.assertIn(20007,state['completed_events'])
        self.assertFalse(any(item['i']==54 for item in state['gacha']['items']))
        validate_gacha_state(state['gacha'])
        self.assertEqual(state['story']['city_areas']['2']['stage']['cs'],1107)
        return state
    def test_actual1105_then_original_rescue_then_actual1107_opens_only_required_areas(self):
        state,reply,effects,changed=self.fight(self.state,1105,1)
        self.assertNotIn(20007,state['completed_events'])
        self.assertEqual(state['story']['city_areas']['2']['stage']['cs'],1106)
        state=self.rescue(state)
        lost,reply,effects,changed=self.fight(state,1107,0)
        self.assertEqual(lost['story']['city_areas']['3']['st'][0],2)
        self.assertEqual(lost['story']['city_areas']['4']['st'][0],2)
        won,reply,effects,changed=self.fight(state,1107,1)
        self.assertEqual(won['story']['city_areas']['2']['st'][0],0)
        for aid,scene in ((3,2101),(4,3101)):
            self.assertEqual(won['story']['city_areas'][str(aid)]['st'][0],1)
            self.assertEqual(won['story']['city_areas'][str(aid)]['stage']['cs'],scene)
            self.assertNotIn(scene,won['story']['battle_wins'])
        self.assertNotIn(1106,won['story']['battle_wins'])
        for aid in (5,6,7,8):self.assertEqual(won['story']['city_areas'][str(aid)]['st'][0],2)
        replay,reply,effects,changed=prepare_stage_finish(won,{'t':1,'s':1107,'h':[24],'x':[],'w':1},self.tables['mission'],self.tables['city_data'],lambda a,r:None,'actual-source-1107')
        self.assertFalse(changed);self.assertEqual(replay,won)
    def test_rescue_terminal_respects_target_lock_and_original_route_sentinel(self):
        for mode in ('locked','route5'):
            with self.subTest(mode=mode):
                state,_,_,_=self.fight(copy.deepcopy(self.state),1105,1)
                state=self.rescue(state)
                if mode=='locked':state['story']['city_areas']['3']['st'][2]=True
                else:state['story']['route']='5'
                won,_,_,_=self.fight(state,1107,1)
                self.assertEqual(won['story']['city_areas']['3']['st'][0],2)
                if mode=='route5':self.assertEqual(won['story']['city_areas']['4']['st'][0],2)
                else:self.assertEqual(won['story']['city_areas']['4']['st'][0],1)
