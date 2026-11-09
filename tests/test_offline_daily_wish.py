"""All13 original letter effects, wire body, reads/choices and reset policy."""
import copy
import json
import io
import contextlib
from pathlib import Path
import sys
import textwrap
from types import SimpleNamespace as NS
import unittest
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'runtime'),str(ROOT/'tools'),str(ROOT/'analysis/research-agent')]
from read_literal_marshal import read
from read_data_table import read as read_source
import test_offline_event_effects as base
from offline_event_effects import (plan_event_effects,daily_wish_notice,daily_wish_token,prepare_daily_wish_read,
    prepare_daily_wish_choice,daily_choice_token,apply_event_effects_snapshot,validate_daily_wish)
from offline_week import prepare_week_transition
from offline_day import build_offline_daily_plan,prepare_gateway_day_operation
from offline_conditions import evaluate_offline_condition

class DailyWishTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tables=base.original_tables();cls.tables['daily_wish']=read(ROOT/'analysis/android640-scripts/com/data/cdata/daily_wish.marshal')
        cls.content=read_source(ROOT/'analysis/decompiled/event_content.py')
    def setUp(self):
        self.state=base.base_state(self.tables);self.state['story'].update(week=2,date=3,daily_wish=[],daily_wish_hero=8,daily_wish_read=False)
    def test_all13_original_rows_replace_letter_once_and_preserve_other_actual_state(self):
        rows=[(event,row)for event,row in self.content.items()if 'daily_wish'in row]
        self.assertEqual(len(rows),13)
        for event,row in rows:
            with self.subTest(event=event):
                state=copy.deepcopy(self.state);state['story'].update(daily_wish=[1],daily_wish_read=True)
                candidate,notices,diagnostic=plan_event_effects(state,event,self.content,self.tables,base.evidence_context(event,row))
                self.assertTrue(diagnostic['ready'],diagnostic)
                self.assertEqual(candidate['story']['daily_wish'],list(row['daily_wish']))
                self.assertFalse(candidate['story']['daily_wish_read']);self.assertEqual(candidate['story']['daily_wish_hero'],8)
                self.assertEqual(candidate['profile'],state['profile']);self.assertEqual(candidate['story']['city_areas'],{})
                self.assertEqual(next(payload for name,payload in notices if name=='syncDailyWish'),{'dw':list(row['daily_wish']),'dwh':8,'dwr':False})
                candidate['story']['daily_wish_read']=True
                replay,again,diag=plan_event_effects(candidate,event,self.content,self.tables,base.evidence_context(event,row))
                self.assertEqual(replay,candidate);self.assertEqual(again,[])
                if event in(2029,2030):self.assertEqual(diagnostic['deferred_handoffs'][0]['route'],'6-3')
    def test_unknown_damaged_catalog_or_list_is_rejected_atomically(self):
        before=copy.deepcopy(self.state)
        for bad in ((999,),('11',),(),{11}):
            content={2032:dict(self.content[2032],daily_wish=bad)}
            candidate,notices,diag=plan_event_effects(self.state,2032,content,self.tables,{})
            self.assertFalse(diag['ready']);self.assertEqual(candidate,before);self.assertEqual(notices,[])
        for wishes in ([999],['11'],None):
            damaged=dict(self.state['story'],daily_wish=wishes)
            with self.assertRaises(ValueError):validate_daily_wish(damaged,self.tables['daily_wish'])
    def test_original_sync_and_read_body_exact_schema_no_dedicated_reply(self):
        source=(ROOT/'analysis/decompiled/StoryMember.py').read_text()
        events=[];rpc=[];owner=NS(storyData=NS(),callServerMethod=lambda name,args:rpc.append((name,args)))
        namespace={'gg':NS(ui=NS(_tree=NS(proc_event=lambda *args,**kw:events.append((args,kw)))))}
        for name in('syncDailyWish','readDailyWish'):
            start=source.index('    def '+name+'(');end=source.find('\n    def ',start+5)
            body=source[start:end];body=body.split('\n    @')[0]
            exec(compile(textwrap.dedent(body),'original-StoryMember-'+name,'exec'),namespace)
        name,payload=daily_wish_notice(dict(daily_wish=[11],daily_wish_hero=8,daily_wish_read=False))
        self.assertEqual(name,'syncDailyWish');namespace[name](owner,payload['dw'],payload['dwh'],payload['dwr'])
        self.assertEqual((owner.storyData.dailyWish,owner.storyData.dailyWishHero,owner.storyData.dailyWishReaded),([11],8,False))
        self.assertEqual(events,[(('daily_wish_update',),{'_children':True})])
        namespace['readDailyWish'](owner);self.assertTrue(owner.storyData.dailyWishReaded)
        self.assertEqual(rpc,[('readDailyWish',{})])
    def test_original_city_letter_refresh_body_consumes_catalog_text_in_wire_order(self):
        from bytecode27 import read as read_code
        from uncompyle6.main import decompile
        output=io.StringIO()
        with contextlib.redirect_stdout(io.StringIO()),contextlib.redirect_stderr(io.StringIO()):
            decompile(read_code(ROOT/'analysis/android640-scripts/cocos/panels/city_letter.marshal'),bytecode_version=(2,7),out=output)
        source=output.getvalue();start=source.index('    def refresh(');end=source.index('    def on_close_click',start)
        texts=[];scroll=NS(setInnerContainerSize=lambda size:None,getContentSize=lambda:NS(width=300))
        class Panel:
            LEFT_BEGIN=10;TOP_BEGIN=0
            def __getitem__(self,key):return scroll
            def load_comp(self,*args):
                margin=NS(left=0,top=0)
                node=NS(getLayoutParameter=lambda:NS(getMargin=lambda:margin,setMargin=lambda value:None))
                return NS(set_string=texts.append,_node=node,get_content_size=lambda:NS(height=20))
        namespace={'Panel':Panel,'gg':NS(avatar=NS(storyData=NS(dailyWish=[11,3]))),
            'DAILY_WISH_DATA':NS(data=self.tables['daily_wish']),'cc':NS(cc=NS(Size=lambda w,h:(w,h)))}
        exec(compile(textwrap.dedent(source[start:end]),'original-city_letter-refresh','exec'),namespace)
        namespace['refresh'](Panel())
        self.assertEqual(texts,[self.tables['daily_wish'][11]['cont'],self.tables['daily_wish'][3]['cont']])

    def test_read_token_same_letter_occurrence_fence_and_snapshot_empty_defaults(self):
        state=copy.deepcopy(self.state);state['story'].update(daily_wish=[11],daily_wish_generation=1)
        token=daily_wish_token(state['story'])
        read_state,changed=prepare_daily_wish_read(state,{},token,self.tables['daily_wish'])
        self.assertTrue(changed);self.assertTrue(read_state['story']['daily_wish_read'])
        self.assertFalse(prepare_daily_wish_read(read_state,{},token,self.tables['daily_wish'])[1])
        state['story']['daily_wish_generation']=2
        self.assertFalse(prepare_daily_wish_read(state,{},token,self.tables['daily_wish'])[1])
        self.assertFalse(state['story']['daily_wish_read'])
        projected=apply_event_effects_snapshot({'story':{}},{'std':{'dw':[15],'dwh':99,'dwr':True}})
        self.assertEqual({k:projected['std'][k]for k in('dw','dwh','dwr')},{'dw':[],'dwh':0,'dwr':False})
    def test_explicit8078_choice_uses_actual_conquered_not_full_ownership_and_no_UI_completion(self):
        state=copy.deepcopy(self.state);state['processing_events']=[8078];state['story']['event_occurrences']={'8078':1}
        token=daily_choice_token(state)
        with self.assertRaises(ValueError):prepare_daily_wish_choice(state,{'h':8},token,self.content,self.tables['hero'])
        state['story']['conquered_heroes']=[8]
        candidate,changed=prepare_daily_wish_choice(state,{'h':8},token,self.content,self.tables['hero'])
        self.assertTrue(changed);self.assertEqual(candidate['story']['daily_wish_hero'],8)
        self.assertEqual(candidate['processing_events'],[8078]);self.assertEqual(candidate['completed_events'],[])
        self.assertNotIn('event_callbacks',candidate['story']);self.assertEqual(candidate['profile'],state['profile'])
        self.assertFalse(prepare_daily_wish_choice(candidate,{'h':8},token,self.content,self.tables['hero'])[1])
        with self.assertRaises(ValueError):prepare_daily_wish_choice(candidate,{'h':24},token,self.content,self.tables['hero'])
        state['event_traces']=[[8078,[['ui',[4]]]]]
        with self.assertRaises(ValueError):prepare_daily_wish_choice(state,{'h':8},token,self.content,self.tables['hero'])
        projected=apply_event_effects_snapshot(candidate,{'heromgr':{'hrs':[(8,{}),(24,{})]}})
        records=dict(projected['heromgr']['hrs']);self.assertTrue(records[8]['cfd']);self.assertNotIn('cfd',records[24])
        self.assertEqual(evaluate_offline_condition(50,'[1,)',state),True)
        state['story']['conquered_heroes']=[]
        self.assertEqual(evaluate_offline_condition(50,'[1,)',state),False)
    def test_unverified_hero0_fatigue_and_route27_special_areas_remain_blocked(self):
        for event in(7026,1448,1450,1452):
            candidate,notices,diagnostic=plan_event_effects(self.state,event,self.content,self.tables,base.evidence_context(event,self.content[event]))
            self.assertFalse(diagnostic['ready'],(event,diagnostic));self.assertEqual(candidate,self.state);self.assertEqual(notices,[])

    def test_ordinary_day_retains_and_newweek_clears_with_full_snapshot_no_old_letter_leak(self):
        from test_offline_day import DayProtocolTests
        fixture=DayProtocolTests();state,fatigue,upgrades=fixture.provider_state()
        state['story'].update(daily_wish=[3],daily_wish_hero=8,daily_wish_read=True)
        plan,diag=build_offline_daily_plan(state,fatigue,upgrades,stock_day=0)
        armed=prepare_gateway_day_operation(state,'statusCheck',{'s':'nextday'},[],stock_day=0)[0]
        armed=prepare_gateway_day_operation(armed,'updateEventCondClient',{'c':102,'v':'4'})[0]
        done=prepare_gateway_day_operation(armed,'incDayWhenNoActionVal',{},[],plan)[0]
        self.assertEqual(daily_wish_notice(done['story'])[1],{'dw':[3],'dwh':8,'dwr':True})
        from test_offline_week import WeekCycleTests
        week=WeekCycleTests();week.setUp();week.state['story'].update(daily_wish=[11],daily_wish_hero=24,daily_wish_read=True)
        changed=prepare_week_transition(week.state,'handleResetWeekAsk','wish-reset',week.tables,authorized_reset=True)[0]
        projected=apply_event_effects_snapshot(changed,{'std':{'dw':[11],'dwh':24,'dwr':True}})
        self.assertEqual({k:projected['std'][k]for k in('dw','dwh','dwr')},{'dw':[],'dwh':0,'dwr':False})
