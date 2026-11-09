"""Original first-week EVENT outcomes; host results are not native wins."""
import copy
import hashlib
from pathlib import Path
import sys
from types import SimpleNamespace
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'tools'),str(ROOT/'analysis/research-agent')]
import test_gateway_integrations as integration_fixtures
from test_local_gateway import gateway
from read_data_table import read
from read_literal_marshal import read as read_marshal


class FirstWeekEventGatewayTests(integration_fixtures.IntegratedGatewayTests):
    @classmethod
    def setUpClass(cls):
        cls.content=read(ROOT/'analysis/decompiled/event_content.py')
        cls.missions=read_marshal(ROOT/'analysis/android640-scripts/com/data/cdata/mission.marshal')
        cls.notes=read(ROOT/'analysis/decompiled/notepad.py')
        cls.cgs=read_marshal(ROOT/'analysis/android640-scripts/com/data/cdata/cg_data.marshal')

    def begin_original(self,source,scene):
        if not hasattr(self,'_first_week_profile'):
            self._first_week_profile=copy.deepcopy(self.proxy.profile)
        self.proxy.profile=copy.deepcopy(self._first_week_profile)
        self.table('mission',{scene:self.missions[scene]})
        self.table('event_content',self.content)
        self.table('notepad',self.notes)
        self.table('cg_data',self.cgs)
        self.proxy.available_events={source:1}
        self.proxy.processing_events=set()
        self.proxy.completed_events=set()
        self.proxy.battle={'version':1,'active':None,'receipts':[]}
        self.proxy.story.pop('event_terminal_failures',None)
        self.proxy.story.pop('event_battle_gates',None)
        self.proxy.story.pop('event_battle_cursor',None)
        # Each loop starts an independent fixture world, including provenance.
        for key in ('event_terminal_offers','event_terminal_contexts','event_terminal_effect_audit'):
            self.proxy.story.pop(key,None)
        self.proxy.story.pop('battle_wins',None)
        self.owner.replies[:]=[]
        self.removed=[]
        self.owner.eventTriggerData=SimpleNamespace(delProcessingEvent=self.removed.append)
        self.proxy.save_progress()
        self.proxy.reliable_call({'w':{'m':'startEvent','p':{'e':source},'r':scene},'_cbid_':7})
        self.proxy.process_story('trace',{'k':'dialog','d':{'c':self.content[source]['dialog']}})
        total=sum(w for r,w in self.stage['reward_pool304']['weights'])
        uid=next('%024x'%n for n in range(scene*1000,scene*1000+1000)
            if int(hashlib.sha256(('stage-drop-v1:%024x:304:0'%n).encode()).hexdigest(),16)%total<147000)
        self.modules['common.IdManager'].IdManager.genid=lambda:uid
        self.proxy.handle_battle_admission({'t':2,'s':scene,'h':[24],'d':{}},8)
        active=copy.deepcopy(self.proxy.battle['active'])
        self.assertIsNotNone(active)
        return active

    def test_original120_131_154_actual_win_and_loss_offer_only_original_successor(self):
        for source,scene,target in ((2003,120,2006),(3008,131,3009),(8041,154,8028)):
            for win in (0,1):
                with self.subTest(scene=scene,win=win):
                    active=self.begin_original(source,scene)
                    before=copy.deepcopy(self.proxy.profile)
                    self.assertNotIn(target,self.proxy.available_events)
                    result={'t':2,'s':scene,'h':[24],'x':[],'w':win,'e':{}}
                    self.proxy.handle_battle_finish(result,active['fight_id'])
                    self.assertIsNone(self.proxy.battle['active'])
                    self.assertIn(target,self.proxy.available_events)
                    self.assertNotIn(target,self.proxy.completed_events)
                    self.assertNotIn(source,self.proxy.processing_events)
                    if win:
                        self.assertIn(scene,self.proxy.story['battle_wins'])
                        self.assertIn(source,self.proxy.completed_events)
                    else:
                        self.assertEqual(self.proxy.profile,before)
                        self.assertNotIn(scene,self.proxy.story.get('battle_wins',[]))
                        self.assertNotIn(source,self.proxy.completed_events)
                        self.assertEqual(self.removed,[source])
                        self.assertNotIn(str(source),self.proxy.story.get('pending_effects',{}))
                        self.assertFalse(any(name=='completeEventReplyEnd' and payload.get('e')==source for name,payload in self.owner.replies))
                    origin=self.proxy.story['available_origins'][str(target)]
                    self.assertEqual(origin['fight_id'],active['fight_id'])
                    self.assertEqual(origin['outcome'],win)
                    snapshot=self.proxy.progress_snapshot()
                    self.proxy.handle_battle_finish(result,active['fight_id'])
                    self.assertEqual(self.proxy.progress_snapshot(),snapshot)
                    if scene==131:
                        receipt=self.proxy.battle['receipts'][-1]
                        self.assertEqual(receipt['raw_prize'],13)
                        self.assertEqual(receipt['event_reward_policy'],'scene131-prize13-enabled-base-offline-v1')

    def test_original_final_day_fixture_needs8028_dialogue_before_ending7_and_incweek1030(self):
        # This is an established final-day HOST fixture, not a native seven-day
        # playthrough or an instruction to alter a user's saved date.
        active=self.begin_original(8041,154)
        self.proxy.day['stock_day']=7
        self.proxy.story['date']=7
        self.table('ending_data',read_marshal(ROOT/'analysis/android640-scripts/com/data/cdata/ending_data.marshal'))
        self.table('story_route',self.week['routes'])
        self.proxy.handle_battle_finish({'t':2,'s':154,'h':[24],'x':[],'w':0,'e':{}},active['fight_id'])
        self.assertIn(8028,self.proxy.available_events)
        self.assertIsNone(self.proxy.week_protocol['result'])
        self.proxy.reliable_call({'w':{'m':'startEvent','p':{'e':8028},'r':8028},'_cbid_':9})
        self.assertIsNone(self.proxy.week_protocol['result'])
        self.proxy.process_story('trace',{'k':'dialog','d':{'c':8028}})
        self.assertIn(8028,self.proxy.completed_events)
        self.assertEqual(self.proxy.week_protocol['result']['ending'],7)
        self.assertTrue(any(name=='showWeekResult' and payload['r']==7 for name,payload in self.owner.replies))
        self.assertNotIn(154,self.proxy.story.get('battle_wins',[]))
        for key,name in (('scores','mainline_score_info'),('building','city_building'),
                ('development','city_development'),('missions','mission'),('hero','hero'),('items','item_data')):
            self.table(name,self.week[key])
        self.proxy.process_week_operation('handleIncWeekAsk',{},source_week=0)
        self.assertEqual(self.proxy.story['week'],1)
        self.assertEqual(self.proxy.available_events,{1030:1})
        self.assertTrue(any(name=='handleIncWeekReply' for name,payload in self.owner.replies))
        self.assertTrue(self.proxy.week_protocol['awaiting_avatar'])

    def test_actual_event_finish_save_failure_does_not_offer_or_close_parent(self):
        active=self.begin_original(8041,154)
        previous=self.proxy.progress_snapshot()
        replies=len(self.owner.replies)
        with patch.object(self.proxy._store,'write',side_effect=OSError('disk full')):
            with self.assertRaises(OSError):
                self.proxy.handle_battle_finish({'t':2,'s':154,'h':[24],'x':[],'w':0,'e':{}},active['fight_id'])
        self.assertEqual(self.proxy.progress_snapshot(),previous)
        self.assertNotIn(8028,self.proxy.available_events)
        self.assertEqual(self.removed,[])
        self.assertEqual(len(self.owner.replies),replies)

    def test_original_terminal_loss_does_not_reenter_parent_when_trigger_still_matches(self):
        from offline_story_engine import refresh_story_events
        active=self.begin_original(8041,154)
        self.proxy.handle_battle_finish({'t':2,'s':154,'h':[24],'x':[],'w':0,'e':{}},active['fight_id'])
        state=self.proxy.progress_snapshot()
        refresh_story_events(state,{8041:{'release':True,'conds':{}}},self.content)
        self.assertNotIn(8041,dict(state['available_events']))
        self.assertNotIn(8041,state['completed_events'])
