"""Original1011 patrol admission/selection/dialogue chain, without fake wins."""
import copy
from pathlib import Path
import sys
import unittest
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'runtime'),str(ROOT/'tools')]
from read_data_table import read
import test_offline_city_actions as city_fixtures
from offline_city_actions import select_city_patrol_event,complete_city_patrol_event
from offline_event_effects import plan_event_effects
from offline_story_engine import prepare_story_operation,begin_story_occurrence


class FirstWeekPatrolTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.content=read(ROOT/'analysis/decompiled/event_content.py')
        all_triggers=read(ROOT/'analysis/decompiled/event_condition.py')
        cls.triggers={event:all_triggers[event] for event in (1011,1013,1005)}
    def setUp(self):
        self.fixture=city_fixtures.CityActionTests()
        self.fixture.setUp()
        self.fixture.state['event_traces']=[]
        self.fixture.catalogs['content']=self.content
        self.fixture.catalogs['triggers']={1011:self.triggers[1011]}
    def admitted(self):
        state,notices,changed,diagnostic=self.fixture.act('enterPatrolRequest',{'aid':1,'hs':self.fixture.heroes},identity='actual-central-patrol')
        self.assertTrue(changed)
        self.assertIn(1011,state['city_actions']['patrol']['events'])
        state,changed=select_city_patrol_event(state,1011)
        self.assertTrue(changed)
        return state
    def begin(self,state,event):
        state=copy.deepcopy(state)
        state['available_events']=[row for row in state['available_events'] if row[0]!=event]
        state['processing_events'].append(event)
        begin_story_occurrence(state,event)
        return prepare_story_operation(state,'start',{'e':event},self.content,self.triggers,{})[0]
    def test_original_patrol1011_option1025_then_real_countdown_callback_unlocks1005(self):
        admitted=self.admitted()
        state=self.begin(admitted,1011)
        state,notices=prepare_story_operation(state,'trace',{'k':'dialog','d':{'c':1011}},self.content,self.triggers,{})
        self.assertNotIn(1011,state['completed_events'])
        state,notices=prepare_story_operation(state,'option',{'e':1011,'se':1025,'op':1},self.content,self.triggers,{})
        self.assertIn(1011,state['completed_events'])
        self.assertIn(1025,state['processing_events'])
        receipt=next(iter(state['story']['tutorial_patrol_receipts'].values()))
        self.assertEqual(receipt['admission_id'],'actual-central-patrol')
        self.assertEqual(receipt['area'],1)
        state,changed=complete_city_patrol_event(state,1011)
        self.assertTrue(changed)
        self.assertIsNone(state['city_actions']['patrol'])
        state,notices=prepare_story_operation(state,'trace',{'k':'dialog','d':{'c':1025}},self.content,self.triggers,{})
        self.assertIn(1025,state['completed_events'])
        self.assertIn(1013,dict(state['available_events']))
        state=self.begin(state,1013)
        state,notices=prepare_story_operation(state,'trace',{'k':'dialog','d':{'c':1013}},self.content,self.triggers,{})
        self.assertNotIn(1013,state['completed_events'])
        state,notices=prepare_story_operation(state,'callback',{'e':1013,'token':'ui:1013'},self.content,self.triggers,{})
        self.assertIn(1013,state['completed_events'])
        self.assertIn(1005,dict(state['available_events']))
        self.assertEqual(state['story'].get('battle_wins',[]),[])
        self.assertEqual(state['story']['city_values']['av'],22)
    def test_existing_active_patrol_migrates_only_from_unique_real_saved_admission(self):
        state=self.admitted()
        for key in ('admission_id','week','day'):
            state['city_actions']['patrol'].pop(key)
        planned,notices,diagnostic=plan_event_effects(state,1011,self.content,{})
        self.assertTrue(diagnostic['ready'],diagnostic)
        self.assertEqual(planned['city_actions']['patrol']['admission_id'],'actual-central-patrol')
        self.assertNotIn('admission_id',state['city_actions']['patrol'])
        state['city_actions']['receipts']=[]
        planned,notices,diagnostic=plan_event_effects(state,1011,self.content,{})
        self.assertFalse(diagnostic['ready'],diagnostic)
        self.assertEqual(planned,state)

    def test_tutorial_effect_refuses_missing_wrong_area_selection_day_or_admission_atomically(self):
        state=self.admitted()
        for kind in ('missing','area','selection','day','admission'):
            candidate=copy.deepcopy(state)
            if kind=='missing':candidate['city_actions']['patrol']=None
            if kind=='area':candidate['city_actions']['patrol']['area']=2
            if kind=='selection':candidate['city_actions']['patrol']['selected']=None
            if kind=='day':candidate['day']['stock_day']=1
            if kind=='admission':candidate['city_actions']['receipts']=[]
            with self.subTest(kind=kind):
                planned,notices,diagnostic=plan_event_effects(candidate,1011,self.content,{})
                self.assertFalse(diagnostic['ready'],diagnostic)
                self.assertEqual(planned,candidate)
                self.assertEqual(notices,[])
