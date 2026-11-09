"""Actual city-action/RPC transactions admit original route6 task predicates."""
import copy
import io
import contextlib
import textwrap
from unittest.mock import patch
from types import SimpleNamespace as NS
import test_gacha_gateway_pools as base
from offline_event_effects import plan_event_effects,daily_wish_token
from offline_story_engine import refresh_story_events,begin_story_occurrence
from offline_conditions import evaluate_offline_condition
from read_literal_marshal import read
from read_data_table import read as read_source

gateway,rewards=base.gateway,base.rewards

class DailyWishGatewayTests(base.GatewayOriginalPoolIntegration):
    @classmethod
    def setUpClass(cls):
        super().setUpClass();cls.tables=dict(cls.tables)
        p=rewards.ROOT/'analysis/android640-scripts/com/data/cdata'
        cls.content=read_source(rewards.ROOT/'analysis/decompiled/event_content.py')
        cls.triggers=read(p/'event_condition.marshal')
        for name in('daily_wish','city_building','city_development','city_upgrade','city_patrol'):
            cls.tables[name]=read(p/(name+'.marshal'))
    def setUp(self):
        super().setUp()
        self.table('event_content',self.content)
        self.table('event_condition',{e:self.triggers[e]for e in(2033,5061,6086)})
        self.proxy.story.update(emergency=False,route='6',city_values=dict(self.proxy.story['city_values'],rv=100,bf=1000),
            daily_wish=[],daily_wish_hero=0,daily_wish_read=False,daily_wish_generation=0)
        self.proxy.available_events={};self.proxy.processing_events=set();self.proxy.completed_events={8}
        self.proxy.story['conquered_heroes']=[]
        self.proxy.save_progress();self.owner.replies=[]
    def letter(self,event):
        candidate,notices,diag=plan_event_effects(self.proxy.progress_snapshot(),event,self.content,self.proxy.story_effect_tables(),{})
        self.assertTrue(diag['ready'],diag)
        self.proxy.restore_progress(candidate);self.proxy.save_progress()
    def action_state(self,predecessor,area,level,cleared):
        self.proxy.completed_events.add(predecessor)
        self.proxy.story['city_areas'][str(area)]={'id':area,'lv':level,'st':[0,False,False],'bd':{}}
        # Explicit fixture preconditions are earned-hero facts, not ownership.
        self.proxy.story['conquered_heroes']=cleared
        self.proxy.save_progress()
    def test_library_real_build_refreshes2033_in_same_saved_transaction_and_preserves_callback(self):
        self.letter(2032);self.action_state(2032,2,1,[24])
        self.assertNotIn(2033,self.proxy.available_events)
        self.assertEqual(self.proxy.story['daily_wish'],[2])
        before=copy.deepcopy(self.proxy.progress_snapshot())
        args={'aid':2,'fi':1,'bi':11,'hs':[24]}
        with patch.object(self.proxy._store,'write',side_effect=OSError('full')):
            with self.assertRaises(OSError):self.proxy.handle_city_action('areaBuildRequest',args,'library-one',91)
        self.assertEqual(self.proxy.progress_snapshot(),before)
        self.assertFalse(any(n=='pushEvents'for n,v in self.owner.replies))
        self.owner.replies=[];self.proxy.handle_city_action('areaBuildRequest',args,'library-one',92)
        self.assertEqual(self.proxy.story['city_areas']['2']['bd']['1']['id'],11)
        self.assertIn(2033,self.proxy.available_events);self.assertNotIn(2033,self.proxy.completed_events)
        self.assertEqual(self.proxy.story['daily_wish'],[2]) # Availability is not event completion.
        reply=next(v for n,v in self.owner.replies if n=='area_build_reply')
        push=next(v for n,v in self.owner.replies if n=='pushEvents')
        self.assertEqual(reply['_cbid_'],92);self.assertNotIn('_cbid_',push)
        self.assertIn([2033,1],push['a'])
        self.assertEqual(self.proxy.story['city_values']['av'],22)
        self.assertEqual(self.proxy.profile['heroes']['24']['cf'],95)
        saved=copy.deepcopy(self.proxy.progress_snapshot());self.owner.replies=[]
        self.proxy.handle_city_action('areaBuildRequest',args,'library-one',93)
        self.assertEqual(self.proxy.progress_snapshot(),saved)
        self.assertFalse(any(n=='pushEvents'for n,v in self.owner.replies))
        # Use original reliable start and original dialog trace, not a manual
        # trigger refresh or direct letter write, to finish the now-admitted task.
        self.proxy.reliable_call({'w':{'r':101,'m':'startEvent','p':{'e':2033}}})
        self.proxy.process_story('trace',{'k':'dialog','d':{'c':2033}})
        self.assertIn(2033,self.proxy.completed_events);self.assertEqual(self.proxy.story['daily_wish'],[3])
    def test_real_development_to4_and_detector_build_admit5061_6086_without_manual_refresh(self):
        self.letter(5060);self.action_state(5060,6,3,[7,8,24,37])
        self.proxy.handle_city_action('areaLevelUpRequest',{'aid':6,'hs':[24],'luv':1},'develop-six',94)
        self.assertEqual(self.proxy.story['city_areas']['6']['lv'],4)
        self.assertIn(5061,self.proxy.available_events)
        self.assertTrue(any(n=='pushEvents'and[5061,1]in v['a']for n,v in self.owner.replies))
        self.assertEqual(self.proxy.story['daily_wish'],[6])
        self.letter(6084);self.action_state(6084,7,1,[7,8,24,37,18]);self.owner.replies=[]
        self.proxy.handle_city_action('areaBuildRequest',{'aid':7,'hs':[24],'fi':1,'bi':6},'detector-seven',95)
        self.assertIn(6086,self.proxy.available_events)
        self.assertEqual(self.proxy.story['city_areas']['7']['bd']['1']['id'],6)
        self.assertEqual(self.proxy.story['daily_wish'],[9])
    def test_full140ownership_is_not_conquest_and_read_does_not_build_or_admit_tasks(self):
        self.assertEqual(len(self.proxy.profile['heroes']),140)
        self.letter(2032);self.action_state(2032,2,1,[])
        self.assertFalse(evaluate_offline_condition(50,'[1,)',self.proxy.progress_snapshot()))
        self.proxy.call_server_method('readDailyWish',{});self.engine.drain()
        self.assertTrue(self.proxy.story['daily_wish_read']);self.assertEqual(self.proxy.story['city_areas']['2']['bd'],{})
        self.proxy.handle_city_action('areaBuildRequest',{'aid':2,'hs':[24],'fi':1,'bi':11},'owned-not-cleared',96)
        self.assertEqual(self.proxy.story['city_areas']['2']['bd']['1']['id'],11)
        self.assertNotIn(2033,self.proxy.available_events)
        self.assertFalse(any(n=='pushEvents'and[2033,1]in v['a']for n,v in self.owner.replies))
    def test_read_save_failure_syncs_original_false_and_stale_queue_does_not_read_replacement(self):
        self.letter(2032);before=copy.deepcopy(self.proxy.progress_snapshot())
        with patch.object(self.proxy._store,'write',side_effect=OSError('full')):
            self.proxy.call_server_method('readDailyWish',{});self.engine.drain()
        self.assertEqual(self.proxy.progress_snapshot(),before)
        self.assertEqual(self.owner.replies[-1],('syncDailyWish',{'dw':[2],'dwh':0,'dwr':False}))
        self.owner.replies=[];self.proxy.call_server_method('readDailyWish',{})
        self.letter(2033);self.engine.drain()
        self.assertFalse(self.proxy.story['daily_wish_read'])
        self.assertEqual(self.owner.replies[-1],('syncDailyWish',{'dw':[3],'dwh':0,'dwr':False}))
        self.proxy.call_server_method('readDailyWish',{});self.engine.drain()
        saved=copy.deepcopy(self.proxy.progress_snapshot());self.assertTrue(self.proxy.story['daily_wish_read'])
        self.proxy.call_server_method('readDailyWish',{});self.engine.drain();self.assertEqual(self.proxy.progress_snapshot(),saved)
        restarted=gateway.LocalProxy(None,self.owner,persistent=True)
        self.assertEqual(restarted.story,self.proxy.story)
    def test8078_savefail_blocks_real_callback_and_UI4_then_user_retry_uses_original_stage(self):
        self.proxy.processing_events={8078};state=self.proxy.progress_snapshot();begin_story_occurrence(state,8078)
        state['story']['conquered_heroes']=[8];self.proxy.restore_progress(state);self.proxy.save_progress()
        self.engine.avatar=self.owner;self.engine._f7_avatar_proxy=self.proxy
        dialogs=[];promise=NS(valid=True,visible=True);confirm=NS(visible=False,notify_confirm=lambda message,cb,**kw:dialogs.append((cb,kw)))
        self.engine.ui=NS(panels=NS(promise_main=promise,common_confirm=confirm),_dialogue=None)
        payload={'w':{'r':700,'m':'dailyPureChooseHero','p':{'h':8}}}
        occurrence=[self.proxy.story['week'],self.proxy.story['event_occurrences']['8078']]
        from bytecode27 import read as read_code
        from uncompyle6.main import decompile
        output=io.StringIO()
        with contextlib.redirect_stdout(io.StringIO()),contextlib.redirect_stderr(io.StringIO()):
            decompile(read_code(rewards.ROOT/'analysis/android640-scripts/cocos/panels/promise_main.marshal'),bytecode_version=(2,7),out=output)
        source=output.getvalue();start=source.index('    def on_click(');end=source.index('    def ue_hero_select(',start)
        namespace={'cc':NS(ccui=NS(TOUCH_EVENT_ENDED=2)),'gg':NS(
            avatar=NS(dailyPureChooseHero=lambda h:self.proxy.call_server_method('reliableRpcCall',payload),
                clientTraceProcessingEvent=lambda k,c:self.proxy.defer(1,lambda:self.proxy.process_story('trace',{'k':k,'d':{'c':c}}))),
            ui=NS(actions=NS(promise_main=NS(close=NS(start=lambda cb:None)))),audio_mgr=NS(ui_sound=lambda sound:None))}
        exec(compile(textwrap.dedent(source[start:end]),'original-promise_main-on_click','exec'),namespace)
        panel=NS(hero_id=8,destroy=lambda:None,cb=lambda:self.proxy.defer(1,lambda:self.proxy.process_story(
            'callback',{'e':8078,'token':'ui:8078','source_occurrence':occurrence})))
        def enqueue_real_click():namespace['on_click'](panel,None,2)
        before=copy.deepcopy(self.proxy.progress_snapshot())
        with patch.object(self.proxy._store,'write',side_effect=OSError('full')):
            enqueue_real_click();self.engine.drain()
        self.assertEqual(self.proxy.progress_snapshot(),before)
        self.assertEqual(self.proxy.event_traces,{})
        self.assertEqual(self.proxy.story.get('event_callbacks',{}).get('8078',[]),[])
        self.assertEqual(len(dialogs),1)
        self.assertFalse(any(n=='completeEventReplyEnd'for n,v in self.owner.replies))
        dialogs[0][0]() # Explicit user retry; close animation has not finished.
        self.engine.timers.pop(0)()
        self.assertFalse(any(n=='startEventUI'for n,v in self.owner.replies))
        promise.valid=False;promise.visible=False;self.engine.drain()
        self.assertEqual([v for n,v in self.owner.replies if n=='startEventUI'],[8078])
        enqueue_real_click();self.engine.drain()
        self.assertEqual(self.proxy.story['daily_wish_hero'],8)
        self.assertIn('ui:8078',self.proxy.story['event_callbacks']['8078'])
        self.assertEqual(self.proxy.event_traces[8078]['ui'],{4})
        self.assertIn(8078,self.proxy.processing_events) # Original dialog still required.
        self.assertNotIn(8078,self.proxy.completed_events)
        dialogs[0][0]();self.engine.drain()
        self.assertEqual([v for n,v in self.owner.replies if n=='startEventUI'],[8078])

    def test_original_explicit_reliable8078_choice_no_auto_UI4_trace_and_stale_occurrence(self):
        self.proxy.processing_events={8078};state=self.proxy.progress_snapshot();begin_story_occurrence(state,8078)
        state['story']['conquered_heroes']=[8];self.proxy.restore_progress(state);self.proxy.save_progress()
        before=copy.deepcopy(self.proxy.progress_snapshot())
        args={'w':{'r':400,'m':'dailyPureChooseHero','p':{'h':8}},'_cbid_':99}
        with patch.object(self.proxy._store,'write',side_effect=OSError('full')):self.proxy.reliable_call(args)
        self.assertEqual(self.proxy.progress_snapshot(),before)
        self.owner.replies=[];self.proxy.reliable_call(args)
        self.assertEqual(self.proxy.story['daily_wish_hero'],8)
        self.assertIn(8078,self.proxy.processing_events);self.assertNotIn(8078,self.proxy.completed_events)
        self.assertEqual(self.proxy.event_traces,{})
        self.assertTrue(any(n=='serverCallbackCarrier'and v.get('_cbid_')==99 for n,v in self.owner.replies))
        saved=copy.deepcopy(self.proxy.progress_snapshot());self.proxy.reliable_call(args);self.assertEqual(self.proxy.progress_snapshot(),saved)
        self.proxy.call_server_method('reliableRpcCall',{'w':{'r':401,'m':'dailyPureChooseHero','p':{'h':24}}})
        self.proxy.story['event_occurrences']['8078']+=1
        self.engine.drain();self.assertEqual(self.proxy.story['daily_wish_hero'],8)

for name in list(vars(base.GatewayOriginalPoolIntegration)):
    if name.startswith('test_'):setattr(DailyWishGatewayTests,name,None)
