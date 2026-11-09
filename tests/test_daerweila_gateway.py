"""Real LocalProxy patrol/start/first-intro/terminal save boundaries, host only."""
import copy
from pathlib import Path
import sys
from types import SimpleNamespace
import unittest
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'runtime'),str(ROOT/'tools'),str(ROOT/'analysis/research-agent'),str(ROOT/'tests')]
import test_gateway_integrations as fixtures
import test_daerweila_dispatch as dispatch_fixture
native = dispatch_fixture.native
from test_local_gateway import gateway
import offline_daerweila as dispatch


class DispatchGatewayTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):dispatch_fixture.DispatchTests.setUpClass()
    def setUp(self):
        self.f=fixtures.IntegratedGatewayTests(methodName='runTest');self.f.setUp();self.addCleanup(self.f.doCleanups)
        pure=dispatch_fixture.DispatchTests();pure.setUp();self.data=pure
        self.proxy=self.f.proxy;self.owner=self.f.owner
        self.proxy.story.update(route='13-1',week=1,date=3)
        self.proxy.story['city_areas']=copy.deepcopy(pure.state['story']['city_areas'])
        self.proxy.completed_events=set(pure.state['completed_events'])
        self.proxy.conditions={101:0}
        self.proxy.day['stock_day']=3
        self.owner.weeknumData=SimpleNamespace(daynum=3,weeknum=1)
        self.owner.storyData=SimpleNamespace(daerweila_human=0,daerweila_devil=0,
            daerweila_human_lock=False,daerweila_devil_lock=False,daerweila_choose_asazile=False)
        self.f.engine.avatar=self.owner
        self.pending=[];self.refreshes=[]
        self.f.engine.ui=SimpleNamespace(panels=SimpleNamespace(settlement_window=SimpleNamespace(
            notify_daerweila=lambda side,callback:self.pending.append((side,callback)))))
        def add(body):
            self.owner.replies.append(('addDaerweilaHumanityValue',body))
            field='daerweila_'+body['t'];setattr(self.owner.storyData,field,getattr(self.owner.storyData,field)+1)
            self.f.engine.ui.panels.settlement_window.notify_daerweila(body['t'],lambda:self.refreshes.append(body['t']))
        def sync(body):
            self.owner.replies.append(('syncDaerweilaLineData',body))
            for key,field in (('dh','daerweila_human'),('dd','daerweila_devil'),('dca','daerweila_choose_asazile')):
                setattr(self.owner.storyData,field,body[key])
        self.owner.addDaerweilaHumanityValue=add;self.owner.syncDaerweilaLineData=sync
        for name,rows in (('event_content',pure.events),('event_condition',pure.triggers),('daerweila_dispatch',pure.rows),
                ('city_data',pure.city_data),('reward_common',{})):
            self.f.table(name,rows)
        self.proxy.save_progress();self.owner.replies[:]=[]
        self.seq=0

    def patrol(self,identity='actual-gateway-patrol'):
        self.proxy.handle_city_action('enterPatrolRequest',{'aid':3,'hs':[24]},identity,41)
        self.assertIsNotNone(self.proxy.city_actions['patrol'])
    def reliable(self,name,args):
        self.seq+=1
        self.proxy.reliable_call({'w':{'m':name,'p':args,'r':self.seq},'_cbid_':100+self.seq})
    def start(self,event):self.reliable('startEvent',{'e':event})
    def trace(self,event):self.reliable('clientTraceProcessingEvent',{'k':'dialog','d':{'c':event}})
    def reach_terminal(self):
        self.patrol();self.start(4124);self.trace(4124)
        self.reliable('startEventOption',{'e':4124,'se':4125})
        self.assertIsNone(self.proxy.city_actions['patrol'])
        self.trace(4125);self.reliable('startEventOption',{'e':4125,'se':4126})

    def test_push_events_precedes_actual_patrol_display_and_same_paid_resume(self):
        self.patrol()
        names=[name for name,_ in self.owner.replies]
        self.assertLess(names.index('pushEvents'),names.index('enter_patrol_reply'))
        self.assertTrue(set((4124,4161,4213)).issubset(self.proxy.available_events))
        profile=copy.deepcopy(self.proxy.profile);actions=self.proxy.story['city_values']['av']
        self.owner.replies[:]=[]
        self.patrol('different-wrapper-same-paid-patrol')
        names=[name for name,_ in self.owner.replies]
        self.assertLess(names.index('pushEvents'),names.index('enter_patrol_reply'))
        self.assertEqual(self.proxy.profile,profile)
        self.assertEqual(self.proxy.story['city_values']['av'],actions)
        self.owner.replies[:]=[];self.patrol()
        names=[name for name,_ in self.owner.replies]
        self.assertLess(names.index('pushEvents'),names.index('enter_patrol_reply'))
        self.assertNotIn(4213,self.proxy.completed_events)

    def test_real_terminal_commits_target_exclam_award_before_original_increment(self):
        self.reach_terminal();self.assertEqual(self.owner.storyData.daerweila_human,0)
        self.trace(4126)
        self.assertEqual(self.proxy.story['daerweila_human'],1)
        self.assertEqual(self.owner.storyData.daerweila_human,1)
        self.assertEqual(self.refreshes,[])
        self.assertEqual(len(self.pending),1)
        self.pending.pop()[1]();self.assertEqual(self.refreshes,['human'])
        self.assertIn(2,self.proxy.story['route_targets']['13-1'])
        self.assertEqual(self.proxy.story['city_op_exclam']['3']['patrol'],-1)
        durable=self.proxy._store.load();gateway.validate_gateway_progress(durable)
        snapshot=self.proxy.progress_snapshot();self.trace(4126)
        self.assertEqual(self.proxy.progress_snapshot(),snapshot)
        self.assertEqual(self.owner.storyData.daerweila_human,1)

    def test_terminal_save_failure_has_no_increment_or_other_effect_and_retry_works(self):
        self.reach_terminal();previous=self.proxy.progress_snapshot();self.owner.replies[:]=[]
        with patch.object(self.proxy._store,'write',side_effect=OSError('disk full')):
            with self.assertRaises(OSError):self.trace(4126)
        self.assertEqual(self.proxy.progress_snapshot(),previous)
        self.assertEqual(self.owner.storyData.daerweila_human,0)
        self.assertFalse(any(n=='addDaerweilaHumanityValue' for n,_ in self.owner.replies))
        self.trace(4126)
        self.assertEqual(self.proxy.story['daerweila_human'],1)

    def test_original_first_devil_request_is_intent_without_ack_then_callback_start(self):
        self.patrol();self.owner.replies[:]=[]
        self.owner.storyData.daerweila_choose_asazile=True # original optimistic UI after registering1359_cb
        self.proxy.call_server_method('daerweilaFirstChooseAsazile',{})
        self.f.engine.drain()
        self.assertEqual(self.owner.replies,[])
        self.assertEqual(self.proxy.story['daerweila_dispatch']['first_devil']['phase'],'intro_pending')
        self.assertNotIn(4161,self.proxy.processing_events)
        snapshot=self.proxy.progress_snapshot()
        self.assertFalse(dispatch.project_daerweila(snapshot)['dwca'])
        self.start(4161) # same original start wire emitted only by1359 continuation
        self.assertIn(4161,self.proxy.processing_events)
        self.assertEqual(self.proxy.story['daerweila_dispatch']['first_devil']['phase'],'continued')
        self.assertNotIn(4161,self.proxy.completed_events)
        self.assertEqual(self.proxy.story['daerweila_dispatch']['awards'],{})

    def test_first_request_save_failure_corrects_optimistic_flag_and_retry(self):
        self.patrol();source=dispatch.daerweila_request_source(self.proxy.progress_snapshot())
        self.owner.storyData.daerweila_choose_asazile=True
        previous=self.proxy.progress_snapshot()
        with patch.object(self.proxy._store,'write',side_effect=OSError('disk full')):
            self.proxy.handle_daerweila_first_choice({},source,self.owner)
        self.assertEqual(self.proxy.progress_snapshot(),previous)
        self.assertFalse(self.owner.storyData.daerweila_choose_asazile)
        self.proxy.handle_daerweila_first_choice({},source,self.owner)
        self.assertEqual(self.proxy.story['daerweila_dispatch']['first_devil']['phase'],'intro_pending')

    def test_branch_save_failure_keeps_pending_and_clears_original_start_lock(self):
        self.patrol();source=dispatch.daerweila_request_source(self.proxy.progress_snapshot())
        self.proxy.handle_daerweila_first_choice({},source,self.owner)
        previous=self.proxy.progress_snapshot();self.owner.replies[:]=[]
        self.owner.storyData.daerweila_choose_asazile=True
        with patch.object(self.proxy._store,'write',side_effect=OSError('disk full')):
            with self.assertRaises(OSError):self.start(4161)
        self.assertEqual(self.proxy.progress_snapshot(),previous)
        self.assertIn(('startEventReply',{'e':4161,'r':0,'_cbid_':101}),self.owner.replies)
        self.assertEqual(self.proxy.story['daerweila_dispatch']['first_devil']['phase'],'intro_pending')
        self.assertFalse(self.owner.storyData.daerweila_choose_asazile)

    def test_old_queued_none_and_owner_sources_never_take_new_patrol(self):
        self.proxy.call_server_method('reliableRpcCall',{'w':{'m':'startEvent','p':{'e':4124},'r':11},'_cbid_':711})
        self.patrol();self.f.engine.drain()
        self.assertNotIn(4124,self.proxy.processing_events)
        self.assertIn(('startEventReply',{'e':4124,'r':0,'_cbid_':711}),self.owner.replies)
        self.proxy.call_server_method('daerweilaFirstChooseAsazile',{})
        self.f.engine.avatar=SimpleNamespace()
        self.f.engine.drain()
        self.assertEqual(self.proxy.story['daerweila_dispatch']['first_devil']['phase'],'unseen')

    def test_committed_trace_replay_and_pull_repair_lost_notice_without_add(self):
        self.reach_terminal()
        original=self.proxy.reply
        def lose(name,body,*args):
            if name=='offlineDaerweilaAward':return
            return original(name,body,*args)
        with patch.object(self.proxy,'reply',side_effect=lose):self.trace(4126)
        self.assertEqual(self.proxy.story['daerweila_human'],1)
        self.assertEqual(self.owner.storyData.daerweila_human,0)
        self.owner.replies[:]=[];self.trace(4126)
        self.assertEqual(self.owner.storyData.daerweila_human,1)
        self.assertFalse(any(name=='addDaerweilaHumanityValue' for name,_ in self.owner.replies))
        self.owner.storyData.daerweila_human=0
        self.reliable('pullEvents',{})
        self.assertEqual(self.owner.storyData.daerweila_human,1)

    def test_first_intro_and_continuation_queued_before_pending_save_keep_same_source(self):
        self.patrol()
        self.proxy.call_server_method('daerweilaFirstChooseAsazile',{})
        self.proxy.call_server_method('reliableRpcCall',{'w':{'m':'startEvent','p':{'e':4161},'r':76},'_cbid_':176})
        self.f.engine.drain()
        self.assertIn(4161,self.proxy.processing_events)
        self.assertEqual(self.proxy.story['daerweila_dispatch']['first_devil']['phase'],'continued')
        self.assertEqual(self.proxy.story['daerweila_dispatch']['awards'],{})

    def test_pending_restart_replays_original_intro_and_paid_choice_without_new_fee(self):
        self.patrol();source=dispatch.daerweila_request_source(self.proxy.progress_snapshot())
        self.proxy.handle_daerweila_first_choice({},source,self.owner)
        before=copy.deepcopy(self.proxy.profile)
        self.proxy=gateway.LocalProxy(None,self.owner,persistent=True)
        self.owner.storyData.daerweila_choose_asazile=dispatch.project_daerweila(self.proxy.progress_snapshot())['dwca']
        self.assertFalse(self.owner.storyData.daerweila_choose_asazile)
        self.owner.replies[:]=[];self.patrol('restart-resume')
        self.assertEqual(self.proxy.profile,before)
        source=dispatch.daerweila_request_source(self.proxy.progress_snapshot())
        self.proxy.handle_daerweila_first_choice({},source,self.owner)
        self.start(4161)
        self.assertIn(4161,self.proxy.processing_events)

    def test_unknown_first_intro_preserves_original_legacy_baseline_without_award(self):
        self.proxy._snapshot_template={'std':{'dwhv':2,'dwdv':1,'dwca':True}}
        self.owner.storyData.daerweila_human=2;self.owner.storyData.daerweila_devil=1
        source=dispatch.daerweila_request_source(self.proxy.progress_snapshot())
        self.proxy.handle_daerweila_first_choice({},source,self.owner)
        self.assertEqual(self.owner.storyData.daerweila_human,2)
        self.assertEqual(self.owner.storyData.daerweila_devil,1)
        self.assertNotIn('daerweila_dispatch',self.proxy.story)

    def test_native_tagged_data_at_actual_loader_boundary_still_commits(self):
        for name,rows in (('event_content',self.data.events),('event_condition',self.data.triggers),('daerweila_dispatch',self.data.rows)):
            # Actual native event rows are tagged mappings; their exclam and
            # completeConds nested literals remain ordinary dictionaries.
            self.f.table(name,dispatch_fixture.NativeRow({key:dispatch_fixture.NativeRow(row) for key,row in rows.items()}))
        self.reach_terminal();self.trace(4126)
        self.assertEqual(self.proxy.story['daerweila_human'],1)
        gateway.validate_gateway_progress(self.proxy._store.load())


if __name__=='__main__':unittest.main()
