"""Original-table lifecycle/RPC host contracts, not native gameplay acceptance.

Fixture starts at the pre-entry date6 boundary. Every later round prerequisite
is earned through original event traces/options. Combat result inputs are host
fixtures and do not certify an actual emulator victory.
"""
import copy
import json
from pathlib import Path
import sys
import unittest
from unittest.mock import patch
ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT/'runtime'), str(ROOT/'tools'), str(ROOT/'analysis/research-agent')]
from read_data_table import read
from read_literal_marshal import read as read_marshal
from offline_flashback import (flashback_context, flashback_token, flashback_data,
    flashback_route_handoff, prepare_flashback_operation, flashback_spend_action)
from offline_conditions import evaluate_offline_condition
from offline_event_effects import apply_event_effects_snapshot
from offline_story_engine import prepare_story_operation, refresh_story_events, begin_story_occurrence, story_occurrence_key
from offline_week import prepare_week_route_handoff, prepare_week_result
from offline_event_battle import prepare_event_battle_gate, prepare_event_battle_admission, prepare_event_battle_finish
import test_offline_event_effects as effects
import test_gateway_integrations as integrations
import test_offline_city_actions as citytests
import test_offline_stage as stagetests

STARTS = (7755, 7763, 7768, 7774, 7780, 7784, 7788)
NIGHTS = (7758, 7765, 7770, 7776, 7781, 7785, 7790)
TERMINALS = (7761, 7766, 7772, 7778, 7783, 7786)


def activate_fixture(state, index=1):
    # Pure action planner fixtures only: the full lifecycle tests below earn it.
    state['story'].update(route='35-3', date=6, week=0, emergency=False)
    state['story']['route35_flashback'] = {'version':1,'active':True,'week':0,
        'entry_occurrence':'fixture-entry','index':index,'used_actions':0,
        'transition_receipts':{},'night_intent':None}
    state.setdefault('day', {})['stock_day'] = 6
    return state


class Route35OriginalChainTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if hasattr(cls,'tables'):
            return
        cls.tables = effects.original_tables()
        cls.content = read(ROOT/'analysis/decompiled/event_content.py')
        cls.triggers = read(ROOT/'analysis/decompiled/event_condition.py')
        cls.routes = read_marshal(ROOT/'analysis/android640-scripts/com/data/cdata/story_route.marshal')
        cls.endings = read_marshal(ROOT/'analysis/android640-scripts/com/data/cdata/ending_data.marshal')

    def setUp(self):
        self.state = effects.base_state(self.tables)
        self.state.update(conditions=[],event_traces=[],day={'stock_day':6},
                          battle={'version':1,'active':None,'receipts':[]})
        self.state['story'].update(version=1,week=0,date=6,route='35',emergency=False,
            pending_effects={},city_values={'av':0,'fv':50,'rv':5,'dv':5,'bf':100})
        self.notices = []

    def step(self, operation, args):
        self.state, notices = prepare_story_operation(self.state,operation,args,
            self.content,self.triggers,self.tables)
        self.notices.extend(notices)
        return notices

    def start(self, event, entry_fixture=False):
        refresh_story_events(self.state,self.triggers,self.content)
        if not entry_fixture:
            self.assertIn(event,dict(self.state['available_events']))
        begin_story_occurrence(self.state,event)
        self.state['available_events'] = [p for p in self.state['available_events'] if p[0]!=event]
        self.state['processing_events'].append(event)
        self.step('start',{'e':event})

    def dialog(self,event):
        self.step('trace',{'k':'dialog','d':{'c':self.content[event]['dialog']}})

    def chain(self,event,choice=None):
        while True:
            self.dialog(event)
            children=self.content[event].get('events',())
            if not children: break
            selected = choice if choice in children else children[0]
            self.step('option',{'e':event,'se':selected,'op':1})
            self.assertIn(event,self.state['completed_events'])
            event=selected
        return event

    def enter(self):
        self.start(7752,entry_fixture=True)
        self.dialog(7752)
        self.assertIsNone(flashback_context(self.state))
        self.step('option',{'e':7752,'se':7754,'op':1})
        self.assertIn('route35_entry_authorization',self.state['story'])
        self.assertIsNone(flashback_context(self.state))
        self.dialog(7754)
        self.assertIn(7754,self.state['completed_events'])
        handoff=self.state['story']['event_handoffs'][story_occurrence_key(self.state,7754)][0]
        self.state,notices,changed=prepare_week_route_handoff(self.state,handoff,self.content,self.routes)
        self.assertTrue(changed);self.notices.extend(notices)
        self.assertEqual(notices[0][1]['fbd'],{'ff':True,'fd':1,'fa':0,'fv':0})
        self.assertEqual(flashback_data(self.state)['fd'],1)
        replay,again,changed=prepare_week_route_handoff(self.state,handoff,self.content,self.routes)
        self.assertFalse(changed);self.assertEqual(replay,self.state);self.assertEqual(again,[])

    def night_intent(self, identity):
        self.state,_,changed,diag=prepare_flashback_operation(self.state,'updateEventCondClient',
            {'c':102,'v':'4'},flashback_token(self.state),identity)
        self.assertTrue(changed,diag)

    def round_to_terminal(self,index,decline=False):
        self.start(STARTS[index-1]);self.chain(STARTS[index-1])
        self.assertNotIn(NIGHTS[index-1],dict(self.state['available_events']))
        self.night_intent('real-click-%s'%index)
        self.start(NIGHTS[index-1])
        choices={1:7762,2:7767,3:7773,4:7779,6:7787}
        return self.chain(NIGHTS[index-1],choices.get(index) if decline else None)

    def test_actual_entry_and_six_real_round_chains_require_night_rpc(self):
        self.enter()
        preserved=copy.deepcopy(self.state['story']['city_values'])
        for index in range(1,7):
            self.assertEqual(flashback_context(self.state)['index'],index)
            for i,start in enumerate(STARTS,1):
                if i>=index:
                    self.assertEqual(evaluate_offline_condition(54,'[%s,%s]'%(i,i),self.state),i==index)
            terminal=self.round_to_terminal(index)
            self.assertEqual(terminal,TERMINALS[index-1])
            self.assertEqual(flashback_context(self.state)['index'],index)
            old_token=flashback_token(self.state)
            self.state,notices,changed,diag=prepare_flashback_operation(self.state,
                'requestFlashbackIncDay',{},old_token)
            self.assertTrue(changed,diag)
            self.assertEqual([n for n,p in notices],['syncStoryGeneralValue','syncFlashbackData','replyFlashbackIncDay'])
            self.assertEqual(self.state['story']['date'],6)
            self.assertEqual(self.state['day']['stock_day'],6)
            self.assertEqual(self.state['story']['city_values'],preserved)
            self.assertEqual(flashback_data(self.state)['fd'],index+1)
            self.assertNotIn(STARTS[index],self.state['completed_events'])
            before=copy.deepcopy(self.state)
            replay,again,changed,diag=prepare_flashback_operation(before,'requestFlashbackIncDay',{},old_token)
            self.assertFalse(changed);self.assertEqual(replay,before)
            self.assertEqual(again[-1],('replyFlashbackIncDay',{'d':index+1,'v':0}))
            stale,_,changed,_=prepare_flashback_operation(before,'updateEventCondClient',
                {'c':102,'v':'4'},flashback_token(before),'real-click-%s'%index)
            self.assertFalse(changed);self.assertEqual(stale,before)
        self.start(7788);self.chain(7788)
        self.night_intent('real-click-7');self.start(7790)
        self.assertEqual(self.chain(7790),7792)
        self.assertIn(7792,self.state['processing_events'])
        self.assertNotIn(7792,self.state['completed_events'])
        before=copy.deepcopy(self.state)
        self.step('trace',{'k':'battle','d':{'c':600}})
        self.assertNotIn(7792,self.state['completed_events'])
        unchanged,_,changed,_=prepare_flashback_operation(self.state,'requestFlashbackIncDay',{},flashback_token(self.state))
        self.assertFalse(changed);self.assertEqual(unchanged,self.state)
        # Actual EVENT admission and accepted finish contract, with explicit host
        # win input. This proves the 600 gate, never a real native victory.
        key=story_occurrence_key(self.state,7792)
        self.state,_,_=prepare_event_battle_gate(self.state,7792,self.content,key)
        args={'t':2,'s':600,'h':[152,34,28],'d':{}}
        self.state,_=prepare_event_battle_admission(self.state,args,self.tables['mission'],self.content,lambda:'actual600')
        active=self.state['battle']['active']
        self.assertEqual((active['hero_level'],active['monster_level']),(100,250))
        def settle(active,result):
            reply={k:copy.deepcopy(result[k]) for k in ('t','s','h','x','w')};reply['r']={}
            return reply,{'profile':copy.deepcopy(self.state['profile']),'notices':[],'granted':[]}
        result=dict(args,w=1,x=[],e=1)
        self.state,reply,proof,changed=prepare_event_battle_finish(self.state,result,settle,'actual600',self.tables['mission'],self.content)
        self.assertTrue(changed)
        self.step('combat_win',{'k':'battle','d':{'c':600},'source_event':7792,
            'source_receipt':key,'source_occurrence':[0,self.state['story']['event_occurrences']['7792']]})
        self.assertIn(7792,self.state['completed_events'])
        self.assertEqual(flashback_data(self.state)['fa'],0)
        self.assertIn(7793,self.tables['mission'][600]['successEvent'])
        self.start(7793,entry_fixture=True);self.chain(7793)
        self.assertIn(8884,self.state['processing_events'])
        self.assertNotIn(8884,self.state['completed_events'])
        key=story_occurrence_key(self.state,8884)
        self.state,_,_=prepare_event_battle_gate(self.state,8884,self.content,key)
        args={'t':2,'s':602,'h':[24],'d':{}}
        self.state,_=prepare_event_battle_admission(self.state,args,self.tables['mission'],self.content,lambda:'actual602')
        self.state,_,proof,changed=prepare_event_battle_finish(self.state,dict(args,w=1,x=[],e=1),
            settle,'actual602',self.tables['mission'],self.content)
        self.assertTrue(changed)
        self.step('combat_win',{'k':'battle','d':{'c':602},'source_event':8884,'source_receipt':key})
        self.assertIn(8884,self.state['completed_events'])
        self.assertIn(8902,self.tables['mission'][602]['successEvent'])
        self.start(8902,entry_fixture=True);self.assertEqual(self.chain(8902),8909)
        handoff=self.state['story']['event_handoffs'][story_occurrence_key(self.state,8909)][0]
        self.state,notices,changed=prepare_week_result(self.state,handoff,self.content,self.endings)
        self.assertTrue(changed);self.assertEqual(notices[-1][1]['r'],152)
        self.assertEqual(flashback_data(self.state)['fd'],7)
        self.assertEqual(self.state['story']['city_values'],preserved)

    def test_actual_terminal_still_rejects_missing_intent_wrong_week_and_live_gameplay(self):
        self.enter();self.round_to_terminal(1)
        earned=copy.deepcopy(self.state)
        for mutation in ('intent','processing','battle','patrol','pending_effect','week','occurrence'):
            candidate=copy.deepcopy(earned)
            if mutation=='intent':candidate['story']['route35_flashback']['night_intent']=None
            if mutation=='processing':candidate['processing_events']=[7759]
            if mutation=='battle':candidate['battle']['active']={'fight_id':'actual-pending'}
            if mutation=='patrol':candidate['story']['patrol_pending']=True
            if mutation=='pending_effect':candidate['story']['pending_effects']={'unresolved':{}}
            if mutation=='week':candidate['story']['week']=1
            if mutation=='occurrence':candidate['story']['event_occurrences'].pop('7761')
            result,notices,changed,_=prepare_flashback_operation(candidate,'requestFlashbackIncDay',{},flashback_token(earned))
            self.assertFalse(changed,mutation);self.assertEqual(result,candidate);self.assertFalse(notices)

    def test_actual_early_decline_ending153_never_increments(self):
        self.enter();self.assertEqual(self.round_to_terminal(1,decline=True),7762)
        self.assertNotIn(7761,self.state['completed_events'])
        handoff=self.state['story']['event_handoffs'][story_occurrence_key(self.state,7762)][0]
        self.state,notices,changed=prepare_week_result(self.state,handoff,self.content,self.endings)
        self.assertTrue(changed);self.assertEqual(notices[-1][1]['r'],153)
        before=copy.deepcopy(self.state)
        candidate,notices,changed,_=prepare_flashback_operation(before,'requestFlashbackIncDay',{},flashback_token(before))
        self.assertFalse(changed);self.assertEqual(candidate,before);self.assertEqual(notices,[])

    def test_snapshot_exit_and_foreign_week_keep_unrelated_general_value(self):
        self.enter();self.state['story']['general_value']=308
        snapshot=apply_event_effects_snapshot(self.state,{'std':{'keep':7}})
        self.assertEqual(snapshot['std']['gr'],1);self.assertTrue(snapshot['std']['ff'])
        self.state['story']['route']='31-4'
        flashback_route_handoff(self.state,5530)
        snapshot=apply_event_effects_snapshot(self.state,{'std':{}})
        self.assertEqual(snapshot['std']['gr'],308);self.assertFalse(snapshot['std']['ff'])
        self.assertFalse(self.state['story']['route35_flashback']['active'])


class Route35ActionPolicyTests(unittest.TestCase):
    def test_real_build_develop_patrol_three_units_preserve_av_and_real_cost_guards(self):
        fixture=citytests.CityActionTests('test_build_spends_original_table_costs_and_updates_real_native_area_callback');fixture.setUp()
        state=activate_fixture(fixture.state);state['story']['city_values']['av']=0
        state['story']['city_values']['bf']=10000
        state['story']['city_values']['dv']=100
        fixture.abilities={str(h):{'construct':1000,'leadership':1000,'insight':1000} for h in fixture.heroes}
        for op,args in [('areaBuildRequest',{'aid':1,'fi':1,'bi':2,'hs':fixture.heroes}),
                        ('areaLevelUpRequest',{'aid':1,'hs':fixture.heroes,'luv':1}),
                        ('enterPatrolRequest',{'aid':1,'hs':fixture.heroes})]:
            previous=copy.deepcopy(state)
            state,notices,changed,diag=fixture.act(op,args,state)
            self.assertTrue(changed,diag)
            self.assertEqual(state['story']['city_values']['av'],0)
            self.assertEqual(flashback_data(state)['fa'],flashback_data(previous)['fa']+1)
            self.assertIn('syncFlashbackData',[n for n,p in notices])
        self.assertEqual(flashback_data(state)['fa'],3)
        with self.assertRaises(ValueError):flashback_spend_action(state)
        bad=activate_fixture(copy.deepcopy(fixture.state));bad['profile']['heroes']['24']['cf']=0
        with self.assertRaises(ValueError):fixture.act('areaBuildRequest',{'aid':1,'fi':1,'bi':7,'hs':fixture.heroes},bad)

    def test_stage_reserves_unit_spends_only_accepted_win_and_replay_keeps_fa(self):
        fixture=stagetests.NormalStageTests('test_original_fixture_hashes_and_all_ordinary_chains')
        fixture.setUp();fixture.state=activate_fixture(fixture.state)
        fixture.state['story']['city_values']['av']=0
        admitted,_=fixture.admit();self.assertEqual(flashback_data(admitted)['fa'],0)
        won,reply,proof,changed=fixture.finish(admitted)
        self.assertTrue(changed);self.assertEqual(flashback_data(won)['fa'],1)
        self.assertEqual(won['story']['city_values']['av'],0)
        from offline_stage import prepare_stage_finish
        result=dict(admitted['battle']['active']['request'],x=[],w=1,e={});result.pop('d')
        replay,_,_,changed=prepare_stage_finish(won,result,fixture.missions,fixture.city,
            fixture.reward,admitted['battle']['active']['fight_id'])
        self.assertFalse(changed);self.assertEqual(replay,won)
        lost,_,_,changed=fixture.finish(admitted,win=0)
        self.assertEqual(flashback_data(lost)['fa'],0)
        spent=copy.deepcopy(fixture.state);spent['story']['route35_flashback']['used_actions']=3
        with self.assertRaises(ValueError):fixture.admit(spent)


class Route35GatewayTests(unittest.TestCase):
    table=integrations.IntegratedGatewayTests.table
    @classmethod
    def setUpClass(cls):Route35OriginalChainTests.setUpClass()
    def setUp(self):
        integrations.IntegratedGatewayTests.setUp(self)
        self.content=Route35OriginalChainTests.content
        self.triggers=Route35OriginalChainTests.triggers
        self.proxy.story_effect_tables=lambda:Route35OriginalChainTests.tables
        self.table('event_content',self.content);self.table('event_condition',self.triggers)
        self.table('ending_data',Route35OriginalChainTests.endings)
        self.table('story_route',Route35OriginalChainTests.routes)
        self.proxy.story.update(route='35',date=6)
        self.proxy.day['stock_day']=6;self.owner.weeknumData.daynum=6
        self.proxy.available_events={7752:1}
        self.proxy.save_progress()
    def reliable(self,name,args,serial):
        self.proxy.call_server_method('reliableRpcCall',{'w':{'m':name,'p':args,'r':serial}})
        self.engine.drain()
    def install_original_flashback_callbacks(self):
        # Execute exact original bodies; only Python2 print statement is omitted.
        import textwrap
        from types import SimpleNamespace, MethodType
        def original(path,name):
            lines=path.read_text().splitlines();start=next(i for i,l in enumerate(lines) if l.startswith('    def '+name+'('))
            end=start+1
            while end<len(lines) and (not lines[end].strip() or lines[end].startswith('        ')):
                end+=1
            return textwrap.dedent('\n'.join(l for l in lines[start:end] if not l.lstrip().startswith('print ')))
        events=[];locked=set()
        native=SimpleNamespace(storyData=SimpleNamespace(flashback_day=1,flashback_action_val=0),
            cityData=SimpleNamespace(action_val=0),callServerMethod=self.proxy.call_server_method)
        ui=SimpleNamespace(lock=lambda key,**kw:locked.add(key),
            unlock=lambda key,**kw:(events.append('unlock'),locked.discard(key)),
            panels=SimpleNamespace(city=SimpleNamespace(notify_flashback_inc_day=lambda:events.append('notify'))))
        gg=SimpleNamespace(avatar=native,ui=ui,exec_delay=self.engine.exec_delay,
            exec_cancel=lambda t:None,logic=SimpleNamespace(
                disable_event=lambda key:events.append('disable'),enable_event=lambda key:events.append('enable')))
        city=SimpleNamespace(around_timer=None,force_night=False,_update_daynight=lambda a,b:events.append('animation'))
        gg.city=city
        namespace={'gg':gg,'const':SimpleNamespace(ACT_VAL_TIME={0:21},
            EventCond=SimpleNamespace(COND_CLIENTOP=102),EventClientOp=SimpleNamespace(NEXTDAY_CLICK=4))}
        for path,name,obj in [(ROOT/'analysis/research-agent/city_scene.py','day_night_around',city),
            (ROOT/'analysis/decompiled/StoryMember.py','replyFlashbackIncDay',native),
            (ROOT/'analysis/decompiled/StoryMember.py','requestFlashbackIncDay',native)]:
            exec(original(path,name),namespace)
            setattr(obj,name,MethodType(namespace[name],obj))
        def reply(payload):
            self.owner.replies.append(('replyFlashbackIncDay',copy.deepcopy(payload)))
            native.replyFlashbackIncDay(payload['d'],payload['v'])
        self.owner.replyFlashbackIncDay=reply
        exec(original(ROOT/'analysis/research-agent/city.py','_flashback_next_day'),namespace)
        native.updateEventCond=lambda c,v:self.proxy.call_server_method('reliableRpcCall',
            {'w':{'m':'updateEventCondClient','p':{'c':c,'v':str(v)},'r':7001}})
        def pull(callback):
            def reply():
                self.proxy.reliable_call({'w':{'m':'pullEvents','p':{},'r':7002}})
                callback(None)
            self.engine.exec_delay(1,reply)
        native.pullEvents=pull
        native.tryNotifyEvent=lambda:True
        self.native_night_generator=namespace['_flashback_next_day'](city)
        city._flashback_next_day=SimpleNamespace(next=lambda:next(self.native_night_generator,None))
        return native,events,locked

    def test_original_decline_generator_tail_unlocks_without_advance_or_dismissing_ending(self):
        self.reliable('startEvent',{'e':7752},1)
        self.proxy.process_story('trace',{'k':'dialog','d':{'c':7752}})
        self.reliable('startEventOption',{'e':7752,'se':7754,'op':1},2)
        self.proxy.process_story('trace',{'k':'dialog','d':{'c':7754}})
        native,events,locked=self.install_original_flashback_callbacks()
        serial=[100]
        def chain(event,choice=None):
            while True:
                self.proxy.process_story('trace',{'k':'dialog','d':{'c':self.content[event]['dialog']}})
                children=self.content[event].get('events',())
                if not children:break
                selected=choice if choice in children else children[0]
                serial[0]+=1
                self.reliable('startEventOption',{'e':event,'se':selected,'op':1},serial[0])
                event=selected
        self.reliable('startEvent',{'e':7755},3);chain(7755)
        next(self.native_night_generator);self.engine.drain()
        self.assertFalse(locked)
        self.reliable('startEvent',{'e':7758},4);chain(7758,7762)
        self.assertIn(7762,self.proxy.completed_events)
        self.assertEqual(self.proxy.week_protocol['result']['ending'],153)
        ending=copy.deepcopy(self.proxy.week_protocol['result'])
        before=copy.deepcopy(self.proxy.progress_snapshot())
        # Original generator resumes after the actual ending choice and sends
        # its tail request. The unchanged original reply only animates the city.
        next(self.native_night_generator);self.assertIn('flashback_inc_day',locked)
        self.engine.drain()
        self.assertFalse(locked);self.assertEqual(self.proxy.progress_snapshot(),before)
        self.assertEqual(self.proxy.week_protocol['result'],ending)
        self.assertEqual(events[-5:],['disable','notify','animation','enable','unlock'])
        self.assertEqual(flashback_data(before)['fd'],1)
        self.assertEqual(self.proxy.day['stock_day'],6);self.assertEqual(self.proxy.story['date'],6)
        from offline_week import prepare_week_transition
        # Existing actual-ending week handshake remains authorized: no flashback
        # flag blocks it, and the new-week canonical story drops this context.
        fresh,notices,changed=prepare_week_transition(before,'handleIncWeekAsk',
            'actual-decline-next-week',self.week)
        self.assertTrue(changed);self.assertIsNone(flashback_context(fresh))
        self.assertNotIn('route35_flashback',fresh['story'])
        self.assertEqual(notices[-1][0],'handleIncWeekReply')

    def test_original_gateway_entry_and_round_rpc_rollback_replay_restart(self):
        self.reliable('startEvent',{'e':7752},1)
        self.proxy.process_story('trace',{'k':'dialog','d':{'c':7752}})
        self.reliable('startEventOption',{'e':7752,'se':7754,'op':1},2)
        if 7754 not in self.proxy.processing_events:
            # Wire event option method is checked explicitly below, no direct
            # fabricated completion is used to work around a missing handler.
            self.fail('Original option RPC did not start 7754')
        self.proxy.process_story('trace',{'k':'dialog','d':{'c':7754}})
        self.assertEqual(flashback_data(self.proxy.progress_snapshot())['fd'],1)
        native,events,locked=self.install_original_flashback_callbacks()
        unchanged=copy.deepcopy(self.proxy.progress_snapshot())
        native.requestFlashbackIncDay();self.assertIn('flashback_inc_day',locked)
        self.engine.drain()
        self.assertEqual(self.proxy.progress_snapshot(),unchanged)
        self.assertFalse(locked);self.assertEqual(events[-5:],['disable','notify','animation','enable','unlock'])
        serial=[10]
        def chain(event):
            while True:
                self.proxy.process_story('trace',{'k':'dialog','d':{'c':self.content[event]['dialog']}})
                children=self.content[event].get('events',())
                if not children: break
                serial[0]+=1
                self.reliable('startEventOption',{'e':event,'se':children[0],'op':1},serial[0])
                event=children[0]
        self.reliable('startEvent',{'e':7755},3);chain(7755)
        self.reliable('updateEventCondClient',{'c':102,'v':'4'},90)
        self.assertEqual(self.proxy.story['route35_flashback']['night_intent'],
            flashback_token(self.proxy.progress_snapshot()))
        self.reliable('startEvent',{'e':7758},4);chain(7758)
        self.assertIn(7761,self.proxy.completed_events)
        before=copy.deepcopy(self.proxy.progress_snapshot());self.owner.replies=[]
        token=flashback_token(before)
        native.requestFlashbackIncDay();self.assertIn('flashback_inc_day',locked)
        with patch.object(self.proxy._store,'write',side_effect=OSError('full')):
            with self.assertRaises(OSError):self.engine.drain()
        self.engine.drain()
        self.assertFalse(locked)
        self.assertEqual(events[-5:],['disable','notify','animation','enable','unlock'])
        self.assertEqual(self.proxy.progress_snapshot(),before)
        self.assertEqual([p for n,p in self.owner.replies if n=='replyFlashbackIncDay'],[{'d':1,'v':0}])
        self.assertFalse(any(n=='syncStoryGeneralValue' for n,p in self.owner.replies))
        areas=copy.deepcopy(self.proxy.story['city_areas'])
        self.proxy.call_server_method('requestFlashbackIncDay',{})
        # These admissions arrive in old round before the deferred advance.
        # Processing after it must refuse instead of charging the new round.
        self.proxy.call_server_method('reliableRpcCall',{'w':{'m':'areaBuildRequest',
            'p':{'aid':1,'fi':1,'bi':2,'hs':[24]},'r':8001}})
        self.proxy.call_server_method('areaLevelUpRequest',{'aid':1,'hs':[24],'luv':1})
        self.proxy.call_server_method('reliableRpcCall',{'w':{'m':'combatOfflineRequest',
            'p':{'t':1,'s':1101,'h':[24],'d':{'a':2}},'r':8002}})
        self.engine.drain()
        self.assertEqual(flashback_data(self.proxy.progress_snapshot())['fd'],2)
        self.assertEqual(flashback_data(self.proxy.progress_snapshot())['fa'],0)
        self.assertEqual(self.proxy.story['city_areas'],areas)
        self.assertIsNone(self.proxy.battle['active'])
        committed=copy.deepcopy(self.proxy.progress_snapshot())
        self.proxy.process_flashback_operation('requestFlashbackIncDay',{},token)
        self.assertEqual(self.proxy.progress_snapshot(),committed)
        restarted=integrations.gateway.LocalProxy(None,self.owner,persistent=True)
        self.assertEqual(json.loads(json.dumps(restarted.progress_snapshot())),json.loads(json.dumps(committed)))
        restarted.process_flashback_operation('requestFlashbackIncDay',{},token)
        self.assertEqual(json.loads(json.dumps(restarted.progress_snapshot())),json.loads(json.dumps(committed)))
        self.assertEqual(self.owner.replies[-1],('replyFlashbackIncDay',{'d':2,'v':0}))
        # Captured normal-mode None is an immutable boundary too: it must not
        # silently adopt a flashback entered before deferred dispatch.
        self.proxy.handle_city_action('areaBuildRequest',{'aid':1,'fi':1,'bi':2,'hs':[24]},
            'stale-normal-build',source_context=(self.owner,None))
        self.proxy.handle_battle_admission({'t':1,'s':1101,'h':[24],'d':{'a':2}},
            source_context=(self.owner,None))
        self.assertEqual(self.proxy.progress_snapshot(),committed)
        # Reverse active->inactive context changes also refuse old admissions.
        departed=copy.deepcopy(committed);departed['story']['route']='31-4'
        self.proxy.restore_progress(departed)
        self.proxy.handle_city_action('areaBuildRequest',{'aid':1,'fi':1,'bi':2,'hs':[24]},
            'stale-flashback-build',source_context=(self.owner,flashback_token(committed)))
        self.assertEqual(self.proxy.progress_snapshot(),departed)
        self.proxy.restore_progress(committed)
        self.proxy.owner=integrations.Owner()
        self.proxy.process_flashback_operation('requestFlashbackIncDay',{},flashback_token(committed),source_owner=self.owner)
        self.assertEqual(self.proxy.progress_snapshot(),committed)


if __name__=='__main__':unittest.main()
