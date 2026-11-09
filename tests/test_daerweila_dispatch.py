"""Five original dispatch pairs, paid patrol source and real event lineage; host only."""
import ast
import builtins
import copy
import json
from pathlib import Path
import sys
import unittest
ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT/'runtime'),str(ROOT/'tools'),str(ROOT/'analysis/research-agent'),str(ROOT/'tests')]
import offline_daerweila as dispatch
import offline_city_actions as city
import offline_story_engine as engine
from offline_conditions import evaluate_offline_condition
from read_data_table import read
from read_literal_marshal import read as read_marshal
import test_offline_city_actions as city_fixture


class NativeRow:
    def __init__(self,values):self.values=dict(values)
    def items(self):return list(self.values.items())
    def get(self,key,default=None):return self.values.get(key,default)
    def __getitem__(self,key):return self.values[key]
    def __iter__(self):return iter(self.values)
    def __len__(self):return len(self.values)
    def __deepcopy__(self,memo):return self


def native(value):
    if isinstance(value,dict):return NativeRow({key:native(item) for key,item in value.items()})
    if isinstance(value,list):return [native(v) for v in value]
    if isinstance(value,tuple):return tuple(native(v) for v in value)
    return value


class DispatchTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows=read_marshal(ROOT/'analysis/android640-scripts/com/data/cdata/daerweila_dispatch.marshal')
        cls.city_data=read_marshal(ROOT/'analysis/android640-scripts/com/data/cdata/city_data.marshal')
        cls.all_events=read(ROOT/'analysis/decompiled/event_content.py')
        cls.all_triggers=read(ROOT/'analysis/decompiled/event_condition.py')
        cls.catalog=dispatch.compile_daerweila_dispatch(cls.rows,cls.all_events,cls.all_triggers)
        cls.api=dict(vars(dispatch),prepare_city_action=city.prepare_city_action,
            select_city_patrol_event=city.select_city_patrol_event,complete_city_patrol_event=city.complete_city_patrol_event,
            begin_story_occurrence=engine.begin_story_occurrence,prepare_story_operation=engine.prepare_story_operation)

    def setUp(self):
        f=city_fixture.CityActionTests();f.setUp()
        self.state=copy.deepcopy(f.state);self.state['event_traces']=[]
        self.state['story'].update(route='13-1',week=1,date=3,emergency=False)
        self.state['day']['stock_day']=3
        # Explicit finite history and original placed buildings, not an earned
        # route playthrough. New patrol/choice/dialog/award remain actual gates.
        self.state['completed_events']=[4208,4209,4210,4211,4212]
        self.state['conditions']=[[101,0]]
        for aid,bid in ((3,34),(2,35),(6,36),(7,38),(5,37)):
            self.state['story']['city_areas'][str(aid)]={'id':aid,'st':[0,False,False],'lv':1,
                'bd':{'1':{'id':bid,'uuid':('%024x'%bid)}}}
        ids=set(int(e) for e in self.catalog['nodes'])|set(int(e) for e in self.catalog['pairs'])
        self.events={e:self.all_events[e] for e in ids}
        self.triggers={int(e):self.all_triggers[int(e)] for e in self.catalog['conditions']}
        self.tables={'daerweila_dispatch':self.rows,'event_content':self.events,'event_condition':self.triggers,'reward_common':{},'city_data':self.city_data}
        self.city_tables=dict(f.catalogs,content=self.events,triggers=self.triggers,daerweila_dispatch=self.rows)
        self.abilities={str(h):{'insight':100,'construct':100,'leadership':100} for h in (7,8,24)}
        self.sequence=0

    def call(self,name,*args,**kwargs):return self.api[name](*args,**kwargs)
    def patrol(self,area=3,identity=None):
        self.sequence+=1
        identity=identity or 'actual-paid-patrol:%s'%self.sequence
        self.state,notices,changed,diagnostic=self.call('prepare_city_action',self.state,'enterPatrolRequest',
            {'aid':area,'hs':[24]},self.city_tables,identity,self.abilities,evaluate_condition=evaluate_offline_condition)
        self.assertTrue(changed,diagnostic)
        return notices
    def start(self,event):
        self.state,_=self.call('select_city_patrol_event',self.state,event)
        self.call('begin_story_occurrence',self.state,event,self.events,self.triggers,tables=self.tables)
        self.state['available_events']=[p for p in self.state['available_events'] if p[0] != event]
        self.state['processing_events'].append(event)
        return self.story('start',{'e':event})
    def story(self,operation,arguments):
        self.state,notices=self.call('prepare_story_operation',self.state,operation,arguments,self.events,self.triggers,self.tables)
        for name,body in notices:
            if name == 'completeEventReplyEnd':
                self.state,_=self.call('complete_city_patrol_event',self.state,body['e'])
        return notices
    def finish_side(self,pair=4213,side='human'):
        row=self.catalog['pairs'][str(pair)]
        if side == 'devil':
            self.state,_=self.call('prepare_daerweila_first_choice',self.state,{},self.tables,
                self.call('daerweila_request_source',self.state))
        event=row[side];self.start(event)
        all_notices=[]
        while True:
            all_notices.extend(self.story('trace',{'k':'dialog','d':{'c':self.events[event]['dialog']}}))
            children=self.events[event].get('events',())
            if not children:break
            child=children[0]
            all_notices.extend(self.story('option',{'e':event,'se':child}))
            event=child
        return all_notices

    def test_compile_original_five_pairs_and_no_raw_native_snapshot(self):
        catalog=self.call('compile_daerweila_dispatch',native(self.rows),native(self.events),native(self.triggers))
        self.assertEqual(catalog,self.catalog)
        self.assertEqual(len(catalog['pairs']),5)
        self.assertEqual(len(catalog['nodes']),48)
        self.assertEqual(catalog,json.loads(json.dumps(catalog)))
        extra=copy.deepcopy(self.rows)
        for row in extra.values():row.update(unused_native=object(),unused_float=1.5)
        self.assertEqual(self.call('compile_daerweila_dispatch',native(extra),self.events,self.triggers),catalog)
        bad=copy.deepcopy(self.rows);bad[(4124,4161)]['human_event_id']=True
        with self.assertRaises(ValueError):self.call('compile_daerweila_dispatch',bad,self.events,self.triggers)
        bad=copy.deepcopy(self.events);bad[4125]=dict(bad[4125],events=(4166,))
        with self.assertRaises(ValueError):self.call('compile_daerweila_dispatch',self.rows,bad,self.triggers)

    def test_actual_patrol_produces_three_available_ids_but_show_never_completes(self):
        before=copy.deepcopy(self.state['profile']);notices=self.patrol()
        self.assertEqual(self.state['city_actions']['patrol']['events'],[4124,4161,4213])
        self.assertTrue(set((4213,4124,4161)).issubset(dict(self.state['available_events'])))
        self.assertNotIn(4213,self.state['completed_events'])
        self.assertEqual(self.state['story']['daerweila_dispatch']['awards'],{})
        self.assertLess(self.state['profile']['heroes']['24']['cf'],before['heroes']['24']['cf'])
        with self.assertRaises(ValueError):self.start(4213)
        self.assertNotIn(4213,self.state['completed_events'])

    def test_actual_root_dialog_option_cleans_patrol_then_descendants_award_once(self):
        self.patrol();self.start(4124)
        with self.assertRaises(ValueError):self.story('option',{'e':4124,'se':4125})
        self.story('trace',{'k':'dialog','d':{'c':4124}})
        self.story('option',{'e':4124,'se':4125})
        self.assertIsNone(self.state['city_actions']['patrol'])
        self.assertEqual(self.state['story']['daerweila_dispatch']['awards'],{})
        self.state['city_actions']['receipts']=[]
        self.state=json.loads(json.dumps(self.state))
        self.story('trace',{'k':'dialog','d':{'c':4125}})
        self.story('option',{'e':4125,'se':4126})
        self.assertEqual(self.state['story'].get('daerweila_human',0),0)
        with self.assertRaises(ValueError):
            self.call('apply_daerweila_event',copy.deepcopy(self.state),4126,self.events[4126],self.tables,'1:4126:1')
        notices=self.story('trace',{'k':'dialog','d':{'c':4126}})
        self.assertEqual(self.state['story']['daerweila_human'],1)
        self.assertIn(2,self.state['story']['route_targets']['13-1'])
        self.assertEqual(self.state['story']['city_op_exclam']['3']['patrol'],-1)
        self.assertEqual(sum(n=='offlineDaerweilaAward' for n,_ in notices),1)
        self.call('validate_daerweila_state',self.state)
        before=copy.deepcopy(self.state)
        self.assertEqual(self.story('trace',{'k':'dialog','d':{'c':4126}}),[])
        self.assertEqual(self.state,before)

    def test_first_devil_intent_pending_reload_and_matching_original_start_only(self):
        self.patrol();source=self.call('daerweila_request_source',self.state)
        with self.assertRaises(ValueError):self.start(4161)
        # start() failed after the occurrence increment on this private local
        # object; use transaction copy rollback as the actual gateway does.
        self.setUp();self.patrol();source=self.call('daerweila_request_source',self.state)
        pending,changed=self.call('prepare_daerweila_first_choice',self.state,{},self.tables,source)
        self.assertTrue(changed)
        self.assertEqual(pending['story']['daerweila_dispatch']['first_devil']['phase'],'intro_pending')
        self.assertFalse(self.call('project_daerweila',pending)['dwca'])
        self.assertEqual(pending['story']['daerweila_dispatch']['awards'],{})
        self.state=json.loads(json.dumps(pending))
        replay,changed=self.call('prepare_daerweila_first_choice',self.state,{},self.tables,source)
        self.assertFalse(changed);self.assertEqual(replay,self.state)
        # pending itself does not change the immutable queued source.
        self.assertTrue(self.call('daerweila_queued_operation_matches',self.state,'startEvent',{'e':4161},source,self.tables))
        self.start(4161)
        self.assertTrue(self.call('project_daerweila',self.state)['dwca'])
        self.assertNotIn(4161,self.state['completed_events'])
        self.assertEqual(self.state['story']['daerweila_dispatch']['awards'],{})

    def test_pending_devil_then_actual_human_or_new_day_does_not_permanently_block_intro(self):
        self.patrol();self.state,_=self.call('prepare_daerweila_first_choice',self.state,{},self.tables,self.call('daerweila_request_source',self.state))
        self.finish_side()
        self.assertEqual(self.state['story']['daerweila_dispatch']['first_devil']['phase'],'unseen')
        self.patrol(2)
        self.state,changed=self.call('prepare_daerweila_first_choice',self.state,{},self.tables,self.call('daerweila_request_source',self.state))
        self.assertTrue(changed)
        self.assertEqual(self.state['story']['daerweila_dispatch']['first_devil']['phase'],'intro_pending')

    def test_two_locks_and_changed_conditions_fail_before_award_or_branch(self):
        self.state['story']['daerweila_human_lock']=True
        self.patrol()
        self.assertNotIn(4124,dict(self.state['available_events']))
        self.assertIn(4161,dict(self.state['available_events']))
        with self.assertRaises(ValueError):self.start(4124)
        self.setUp();self.state['story'].update(daerweila_human_lock=True,daerweila_devil_lock=True)
        self.patrol()
        self.assertFalse(set((4124,4161,4213)).intersection(dict(self.state['available_events'])))
        self.setUp();self.patrol();self.state['story']['city_areas']['3']['bd']={}
        with self.assertRaises(ValueError):self.start(4124)

    def test_full_five_pair_awards_naturally_bound_counts_and_forbid_other_side(self):
        for pair,area,side in ((4213,3,'human'),(4214,2,'devil'),(4215,6,'human'),(4216,7,'devil'),(4217,5,'human')):
            self.patrol(area);self.finish_side(pair,side)
            self.call('validate_daerweila_state',self.state)
        doc=self.state['story']['daerweila_dispatch']
        self.assertEqual(len(doc['awards']),5)
        self.assertEqual(self.state['story']['daerweila_human'],3)
        self.assertEqual(self.state['story']['daerweila_devil'],2)
        self.assertEqual(self.call('project_daerweila',self.state)['dwhv'],3)
        before=copy.deepcopy(self.state)
        with self.assertRaises(ValueError):self.start(4161)
        self.state=before
        self.assertEqual(sum((self.state['story']['daerweila_human'],self.state['story']['daerweila_devil'])),5)

    def test_terminal_late_invalid_reward_is_atomic_and_direct_terminal_has_no_source(self):
        self.patrol();self.start(4124);self.story('trace',{'k':'dialog','d':{'c':4124}})
        self.story('option',{'e':4124,'se':4125});self.story('trace',{'k':'dialog','d':{'c':4125}})
        self.story('option',{'e':4125,'se':4126})
        self.events=dict(self.events);self.events[4126]=dict(self.events[4126],rewards=[999999])
        self.tables=dict(self.tables,event_content=self.events)
        before=copy.deepcopy(self.state)
        notices=self.story('trace',{'k':'dialog','d':{'c':4126}})
        self.assertFalse(notices)
        self.assertEqual(self.state['story']['daerweila_dispatch']['awards'],{})
        self.assertEqual(self.state['story'].get('route_targets'),before['story'].get('route_targets'))
        self.assertEqual(self.state['story'].get('city_op_exclam'),before['story'].get('city_op_exclam'))
        self.setUp()
        with self.assertRaises(ValueError):self.start(4126)

    def test_queue_none_old_patrol_week_and_occurrence_cannot_rebind(self):
        none_source=self.call('daerweila_request_source',self.state)
        self.patrol();source=self.call('daerweila_request_source',self.state)
        self.assertFalse(self.call('daerweila_queued_operation_matches',self.state,'startEvent',{'e':4124},none_source,self.tables))
        self.start(4124)
        root_source=self.call('daerweila_request_source',self.state)
        self.story('trace',{'k':'dialog','d':{'c':4124}});self.story('option',{'e':4124,'se':4125})
        self.assertIsNone(self.state['city_actions']['patrol'])
        child_source=self.call('daerweila_request_source',self.state)
        self.assertFalse(self.call('daerweila_occurrence_matches',self.state,4125,root_source))
        # A bound child uses immutable occurrence/choice, not current patrol.
        child_source['patrol']='already-cleaned-root-patrol'
        self.assertTrue(self.call('daerweila_occurrence_matches',self.state,4125,child_source))
        bad=dict(child_source,week=99)
        self.assertFalse(self.call('daerweila_occurrence_matches',self.state,4125,bad))
        before=copy.deepcopy(self.state)
        self.story('trace',{'k':'dialog','d':{'c':4125},'_daerweila_source':root_source})
        self.assertEqual(self.state,before)

    def test_native_readonly_original_rows_and_extra_float_metadata_never_persist(self):
        self.tables=dict(self.tables,daerweila_dispatch=native(self.rows),event_content=native(self.events),event_condition=native(self.triggers))
        self.city_tables=dict(self.city_tables,daerweila_dispatch=native(self.rows),content=native(self.events),triggers=native(self.triggers))
        self.patrol();self.finish_side()
        self.call('validate_daerweila_state',json.loads(json.dumps(self.state)))
        bad=copy.deepcopy(self.state)
        bad['story']['daerweila_dispatch']['offers'][next(iter(bad['story']['daerweila_dispatch']['offers']))]['area']=3.0
        with self.assertRaises(ValueError):self.call('validate_daerweila_state',bad)
        bad=copy.deepcopy(self.state);bad['story']['daerweila_dispatch']=NativeRow(bad['story']['daerweila_dispatch'])
        with self.assertRaises(ValueError):self.call('validate_daerweila_state',bad)

    def test_awards_survive_day_refresh_and_week_reset_archives_then_projects_zero(self):
        import test_offline_week as week_fixture
        from offline_week import prepare_week_transition,read_week_history
        self.patrol();self.finish_side()
        self.state['day']['stock_day']=self.state['story']['date']=4
        self.assertEqual(self.call('project_daerweila',self.state)['dwhv'],1)
        self.call('validate_daerweila_state',self.state)
        f=week_fixture.WeekCycleTests();f.setUp()
        f.state['story']['week']=1
        for key in ('daerweila_dispatch','daerweila_human','daerweila_devil','event_effect_receipts','event_occurrences'):
            f.state['story'][key]=copy.deepcopy(self.state['story'][key])
        next_week,_,_=prepare_week_transition(f.state,'handleResetWeekAsk','dispatch-week-reset',f.tables,authorized_reset=True)
        self.assertNotIn('daerweila_dispatch',next_week['story'])
        self.assertEqual(read_week_history(next_week['week_protocol']['history'][0])['story']['daerweila_dispatch']['awards']['4213']['side'],'human')
        self.assertEqual(self.call('project_daerweila',next_week,{'dwhv':1,'dwdv':0,'dwca':True})['dwhv'],0)
        self.assertFalse(self.call('project_daerweila',next_week,{'dwhv':1,'dwca':True})['dwca'])

    def test_source_receipt_pruning_before_root_and_route_departure_are_fenced(self):
        self.patrol();self.state['city_actions']['receipts']=[]
        self.finish_side()
        self.assertEqual(self.state['story']['daerweila_human'],1)
        self.setUp();self.patrol()
        source=self.call('daerweila_request_source',self.state)
        self.state,_=self.call('prepare_daerweila_first_choice',self.state,{},self.tables,source)
        self.call('expire_daerweila_dispatch',self.state,'1')
        self.state['story']['route']='1'
        self.assertEqual(self.state['story']['daerweila_dispatch']['first_devil']['phase'],'unseen')
        with self.assertRaises(ValueError):self.start(4161)
        self.assertEqual(self.state['story']['daerweila_dispatch']['awards'],{})

    def test_stale_pending_intro_can_be_replayed_on_a_new_real_day_source(self):
        self.patrol();self.state,_=self.call('prepare_daerweila_first_choice',self.state,{},self.tables,self.call('daerweila_request_source',self.state))
        self.state['city_actions']['patrol']=None
        self.state['story']['patrol_pending']=self.state['story']['patrol_reward_pending']=False
        self.state['day']['stock_day']=self.state['story']['date']=4
        self.patrol(2)
        self.state,changed=self.call('prepare_daerweila_first_choice',self.state,{},self.tables,self.call('daerweila_request_source',self.state))
        self.assertTrue(changed)
        self.assertEqual(self.state['story']['daerweila_dispatch']['first_history'][0]['reason'],'source-expired')
        self.start(4167)
        self.assertTrue(self.call('project_daerweila',self.state)['dwca'])

    def test_malformed_occurrence_award_sequence_and_first_intro_save_reject(self):
        self.patrol();self.finish_side()
        for mutation in ('root','occurrence','sequence','terminal','first','float'):
            invalid=copy.deepcopy(self.state);doc=invalid['story']['daerweila_dispatch']
            if mutation=='root':doc['occurrences'].pop('1:4124:1')
            elif mutation=='occurrence':doc['occurrences']['1:4126:0']=doc['occurrences'].pop('1:4126:1')
            elif mutation=='sequence':doc['awards']['4213']['before']['human']=1;doc['awards']['4213']['after']['human']=2
            elif mutation=='terminal':doc['awards']['4213']['receipt']='1:4125:1'
            elif mutation=='float':doc['generation']=1.0
            else:doc['first_devil']={'phase':'continued','offer':next(iter(doc['offers']))}
            with self.subTest(mutation=mutation):
                with self.assertRaises(ValueError):self.call('validate_daerweila_state',invalid)

    def test_legacy_nonzero_baseline_is_preserved_pending_without_patrol_fee(self):
        self.state['story']['daerweila_human']=2
        before=copy.deepcopy(self.state['profile'])
        self.state,notices,changed,diagnostic=self.call('prepare_city_action',self.state,'enterPatrolRequest',{'aid':3,'hs':[24]},
            self.city_tables,'legacy-patrol',self.abilities,evaluate_condition=evaluate_offline_condition)
        self.assertEqual(self.state['profile'],before)
        self.assertEqual(self.state['story']['city_values']['av'],24)
        self.assertEqual(self.state['story']['daerweila_dispatch']['status'],'legacy-pending')
        self.assertEqual(self.call('project_daerweila',self.state)['dwhv'],2)
        self.assertIn('legacy',diagnostic['pending'])
        self.assertFalse(notices[0][1]['s'])
        self.call('validate_daerweila_state',self.state)


class FlatDispatchTests(DispatchTests):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        from patch_bootstrap import embedded_loader
        source=ast.literal_eval(ast.parse(embedded_loader(ROOT/'runtime').splitlines()[0]).body[0].value)
        real_import=builtins.__import__
        def imports(name,globals=None,locals=None,fromlist=(),level=0):
            if name.startswith('offline_'):raise ImportError('Actual flat runtime has no host offline modules')
            return real_import(name,globals,locals,fromlist,level)
        cls.api={'__builtins__':dict(vars(builtins),__import__=imports),'__name__':'actual_flat_dispatch'}
        exec(compile(source,'<actual-flat-dispatch>','exec'),cls.api,cls.api)


if __name__=='__main__':unittest.main()
