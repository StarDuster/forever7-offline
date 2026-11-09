"""Authorized committed successor delivery through the original native handler."""
import copy
from pathlib import Path
from types import SimpleNamespace
import textwrap
import unittest
from unittest.mock import patch
import test_gateway_integrations as integrations
from offline_story_engine import begin_story_occurrence

ROOT=Path(__file__).resolve().parents[1]

class StoryStartDeliveryTests(unittest.TestCase):
    table=integrations.IntegratedGatewayTests.table
    def setUp(self):
        integrations.IntegratedGatewayTests.setUp(self)
        self.engine.avatar=self.owner
        self.engine.logic=SimpleNamespace(event_valid=False,event_semaphore={'settlement_fullscreen':1})
        self.starts=[];self.bases=[]
        client=set()
        self.owner.eventTriggerData=SimpleNamespace(processingEventsClient=client,addProcessingEvent=client.add)
        self.owner.queryEventOptAsk=lambda event:None
        self.owner.logger=SimpleNamespace(debug=lambda *args:None)
        self.owner.writeNewPlayerCheckpointSALog=lambda value:None
        self.owner.completeBase=lambda event:self.bases.append(event)
        self.engine.logic.disable_event=lambda name:setattr(self.engine.logic,'event_valid',False)
        source=(ROOT/'analysis/decompiled/EventTriggerMember.py').read_text()
        source=source[source.index('    def startEventReply('):source.index('    def canStartEventOption(')]
        source=textwrap.dedent(source).replace("print 'can`t start ', gg.logic.event_semaphore","print('can`t start ', gg.logic.event_semaphore)")
        namespace={'gg':self.engine};exec(source,namespace)
        handler=namespace['startEventReply']
        def original(parameters):
            self.starts.append(parameters['e'])
            handler(self.owner,parameters['e'],parameters['r'])
        self.owner.startEventReply=original
        self.proxy.processing_events={1047}
        candidate=self.proxy.progress_snapshot();begin_story_occurrence(candidate,1047)
        self.proxy.restore_progress(candidate);self.proxy.save_progress()
    def tick(self):self.engine.timers.pop(0)()
    def release(self):
        self.engine.logic.event_semaphore={};self.engine.logic.event_valid=True
    def test_original_busy_cg_then_release_once_without_dialogue_zero_or_fake_progress(self):
        self.engine.ui=SimpleNamespace(_dialogue=1024)
        before=copy.deepcopy(self.proxy.progress_snapshot())
        self.proxy.reply('startEventReply',{'e':1047,'r':1})
        self.proxy.reply('startEventReply',{'e':1047,'r':1})
        self.assertEqual(self.starts,[]);self.assertNotIn(1047,self.proxy._started_this_session)
        self.assertEqual(len(self.engine.timers),1)
        self.tick();self.assertEqual(self.starts,[])
        self.proxy.reply('unrelatedReply',{'v':1})
        self.assertIn(('unrelatedReply',{'v':1}),self.owner.replies)
        self.release();self.engine.drain()
        self.assertEqual(self.starts,[1047]);self.assertEqual(self.bases,[1047])
        self.assertIn(1047,self.proxy._started_this_session)
        self.assertEqual(self.engine.ui._dialogue,1024)
        self.assertEqual(self.proxy.progress_snapshot(),before)
        self.proxy.reply('startEventReply',{'e':1047,'r':1})
        self.assertEqual(self.starts,[1047]);self.assertFalse(self.proxy._pending_event_starts)
    def test_original_client_already_accepted_never_sends_even_when_busy(self):
        self.owner.eventTriggerData.processingEventsClient.add(1047)
        self.proxy.reply('startEventReply',{'e':1047,'r':1})
        self.assertFalse(self.starts);self.assertFalse(self.engine.timers)
        self.assertIn(1047,self.proxy._started_this_session)
    def test_original_purge_rearms_once_and_stale_callbacks_do_not_send(self):
        self.proxy.reply('startEventReply',{'e':1047,'r':1})
        self.engine.exec_cancel_all();self.engine.exec_cancel_all()
        self.release()
        for callback in self.engine.cancelled:callback()
        self.assertFalse(self.starts)
        self.engine.drain();self.assertEqual(self.starts,[1047])
    def test_owner_avatar_week_occurrence_completion_and_destroy_retire_pending(self):
        for change in ('owner','avatar','week','occurrence','complete','destroy'):
            with self.subTest(change=change):
                self.setUp()
                self.proxy.reply('startEventReply',{'e':1047,'r':1})
                if change=='owner':self.proxy.owner=SimpleNamespace()
                elif change=='avatar':self.engine.avatar=SimpleNamespace()
                elif change=='week':self.proxy.story['week']=1
                elif change=='occurrence':self.proxy.story['event_occurrences']['1047']+=1
                elif change=='complete':self.proxy.processing_events.remove(1047);self.proxy.completed_events.add(1047)
                else:self.proxy.destroy()
                self.release();self.engine.drain()
                self.assertFalse(self.starts);self.assertFalse(self.proxy._pending_event_starts)
    def test_actual1024_reward_once_then1047_waits_normal_no_reward_chain_also_delivers(self):
        import sys
        sys.path[:0]=[str(ROOT/'analysis/research-agent'),str(ROOT/'tools')]
        from read_data_table import read
        from read_literal_marshal import read as read_marshal
        content=read(ROOT/'analysis/decompiled/event_content.py')
        rewards=read(ROOT/'analysis/decompiled/reward_common.py')
        cg=read_marshal(ROOT/'analysis/android640-scripts/com/data/cdata/cg_data.marshal')
        self.table('event_content',{e:content[e]for e in (1024,1047)})
        self.table('event_condition',{})
        self.table('reward_common',{12:rewards[12]})
        self.proxy.story_effect_tables=lambda:{'reward_common':{12:rewards[12]},'cg_data':{1:cg[1]}}
        self.proxy.processing_events={1024}
        state=self.proxy.progress_snapshot();begin_story_occurrence(state,1024)
        self.proxy.restore_progress(state);self.proxy.save_progress()
        self.proxy.process_story('trace',{'k':'dialog','d':{'c':1024}})
        self.proxy.process_story('option',{'e':1024,'se':1047},callback_id=72)
        self.assertIn(('serverCallbackCarrier',{'_r_':{},'_cbid_':72}),self.owner.replies)
        self.assertIn(1024,self.proxy.completed_events);self.assertIn(1047,self.proxy.processing_events)
        self.assertFalse(self.starts)
        self.assertEqual(self.proxy.story['cgs'],[1])
        reward_replies=[(n,p)for n,p in self.owner.replies if n=='completeEventReplyStart']
        self.assertEqual(len(reward_replies),1)
        saved=copy.deepcopy(self.proxy.progress_snapshot())
        self.proxy.process_story('option',{'e':1024,'se':1047})
        self.assertEqual(self.proxy.progress_snapshot(),saved)
        self.release();self.engine.drain()
        self.assertEqual(self.starts,[1047]);self.assertEqual(self.proxy.progress_snapshot(),saved)
        self.assertEqual(len([(n,p)for n,p in self.owner.replies if n=='completeEventReplyStart']),1)
        self.assertNotIn(1047,self.proxy.completed_events)
        # A second original chain with no reward uses the same delivery path.
        parent,child=3,6
        row=content[parent]
        self.assertFalse(row.get('rewards'));self.assertIn(child,row['events'])
        self.table('event_content',{parent:row,child:content[child]})
        self.proxy.processing_events={parent}
        state=self.proxy.progress_snapshot();begin_story_occurrence(state,parent)
        self.proxy.restore_progress(state);self.proxy.save_progress()
        self.proxy.process_story('trace',{'k':'dialog','d':{'c':row['dialog']}})
        self.proxy.process_story('option',{'e':parent,'se':child})
        self.release();self.engine.drain()
        self.assertEqual(self.starts,[1047,child])
    def test_restart_requeues_authoritative_processing_without_state_or_reward_mutation(self):
        before=copy.deepcopy(self.proxy.progress_snapshot())
        self.proxy.reply('startEventReply',{'e':1047,'r':1})
        self.proxy.destroy()
        restored=integrations.gateway.LocalProxy(None,self.owner,persistent=True)
        restored.reply('startEventReply',{'e':1047,'r':1})
        self.release();self.engine.exec_cancel_all();self.engine.drain()
        self.assertEqual(self.starts,[1047])
        self.assertEqual(restored.progress_snapshot(),before)
        self.assertIn(1047,restored._started_this_session)
    def test_original_handler_nonacceptance_is_one_shot_without_probe_retries(self):
        calls=[]
        self.owner.startEventReply=lambda payload:calls.append(payload)
        self.release()
        self.proxy.reply('startEventReply',{'e':1047,'r':1})
        self.assertEqual(len(calls),1)
        self.assertFalse(self.engine.timers);self.assertFalse(self.proxy._pending_event_starts)
        self.assertNotIn(1047,self.proxy._started_this_session)
    def test_committed_batch_completed_successor_never_starts_stale_original_ui(self):
        before=self.proxy.progress_snapshot()
        candidate=copy.deepcopy(before)
        candidate['processing_events']=[];candidate['completed_events']=[1047]
        # Delivery protocol fixture: final committed batch invalidates its old
        # start notice. This does not infer or add any production completion.
        with patch.object(integrations.gateway,'prepare_story_operation',return_value=(candidate,[('startEventReply',{'e':1047,'r':1}),('completeEventReplyEnd',{'e':1047})])):
            self.proxy.process_story('callback',{'e':1047},callback_id=88)
        self.assertFalse(self.starts);self.assertFalse(self.proxy._pending_event_starts)
        self.assertIn(('serverCallbackCarrier',{'_r_':{},'_cbid_':88}),self.owner.replies)
    def test_parent_queue_no_callback_then_reliable60_61_resolve_once_each(self):
        self.proxy.reply('startEventReply',{'e':1047,'r':1})
        for callback in (60,61,60):
            self.proxy.reliable_call({'w':{'m':'startEvent','p':{'e':1047},'r':callback},'_cbid_':callback})
        self.assertFalse(self.starts)
        self.assertEqual(len(self.engine.timers),1)
        self.release();self.engine.drain()
        self.assertEqual(self.starts,[1047])
        carriers=[p['_cbid_']for n,p in self.owner.replies if n=='serverCallbackCarrier']
        self.assertEqual(carriers,[60,61])
        self.proxy.reliable_call({'w':{'m':'startEvent','p':{'e':1047},'r':63},'_cbid_':60})
        self.assertEqual([p['_cbid_']for n,p in self.owner.replies if n=='serverCallbackCarrier'],[60,61])
    def test_primary_callback_not_resolved_twice_and_alreadyaccepted_callback_carrier(self):
        self.proxy.reply('startEventReply',{'e':1047,'r':1},60)
        self.proxy.reply('startEventReply',{'e':1047,'r':1},61)
        self.release();self.engine.drain()
        self.assertEqual(self.starts,[1047])
        self.assertEqual([p['_cbid_']for n,p in self.owner.replies if n=='serverCallbackCarrier'],[61])
        self.proxy.reply('startEventReply',{'e':1047,'r':1},62)
        self.assertEqual([p['_cbid_']for n,p in self.owner.replies if n=='serverCallbackCarrier'],[61,62])
        self.assertEqual(self.starts,[1047])
    def test_expired_same_avatar_releases_callbacks_but_new_avatar_never_gets_old_callback(self):
        self.proxy.reply('startEventReply',{'e':1047,'r':1},60)
        self.proxy.processing_events.clear()
        self.engine.drain()
        self.assertFalse(self.starts)
        self.assertIn(('serverCallbackCarrier',{'_r_':{},'_cbid_':60}),self.owner.replies)
        self.proxy.processing_events.add(1047)
        self.proxy.reply('startEventReply',{'e':1047,'r':1},61)
        self.engine.avatar=SimpleNamespace()
        self.engine.drain()
        self.assertFalse(any(n=='serverCallbackCarrier' and p.get('_cbid_')==61 for n,p in self.owner.replies))
    def test_fail_or_unprocessing_reply_keeps_original_direct_behavior(self):
        self.proxy.reply('startEventReply',{'e':1047,'r':0})
        self.assertEqual(self.starts,[1047]);self.assertFalse(self.bases)
        self.release();self.proxy.reply('startEventReply',{'e':123,'r':1})
        self.assertEqual(self.starts,[1047,123]);self.assertEqual(self.bases,[123])
        self.assertFalse(self.proxy._pending_event_starts)
