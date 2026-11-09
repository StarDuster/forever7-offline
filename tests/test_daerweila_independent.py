"""Independent full-original-table dispatch boundaries, host/embedded only.

Prior route/building facts are explicitly modeled; no native-earned storyline
or dialogue is claimed. Full event catalogs and all140 owned heroes avoid the
dispatch-only table subset concealing another original patrol candidate.
"""
import ast
import builtins
import copy
import json
from pathlib import Path
import sys
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'runtime'),str(ROOT/'tools'),str(ROOT/'analysis/research-agent')]
from offline_daerweila import (compile_daerweila_dispatch,
    prepare_daerweila_first_choice,daerweila_request_source,project_daerweila,
    validate_daerweila_state)
from offline_city_actions import (prepare_city_action,select_city_patrol_event,
                                  complete_city_patrol_event)
from offline_story_engine import begin_story_occurrence,prepare_story_operation
from offline_conditions import evaluate_offline_condition
from patch_bootstrap import embedded_loader
from read_data_table import read
from read_literal_marshal import read as read_marshal
from test_terminal_stage_independent import ReadOnlyOriginalRow
import test_offline_city_actions as city_fixture


class IndependentDispatchTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        directory=ROOT/'analysis/android640-scripts/com/data/cdata'
        cls.raw={name:read_marshal(directory/(name+'.marshal')) for name in
            ('daerweila_dispatch','city_building','city_development','city_upgrade',
             'city_patrol','city_data','hero','notepad','cg_data','reward_common')}
        cls.content=read(ROOT/'analysis/decompiled/event_content.py')
        cls.triggers=read(ROOT/'analysis/decompiled/event_condition.py')
        cls.api=globals()

    def setUp(self):
        fixture=city_fixture.CityActionTests();fixture.setUp()
        self.state=copy.deepcopy(fixture.state)
        self.state.update(event_traces=[],completed_events=[4203,4208,4209,4210,4211,4212],
                          conditions=[[101,0]])
        self.state['story'].update(route='13-1',week=1,date=3,emergency=False)
        self.state['day']['stock_day']=3
        self.state['profile']['heroes']={str(hero):{'cf':100,'ef':0,'sk':{}}
                                       for hero in self.raw['hero']}
        for area,building in ((3,34),(2,35),(6,36),(7,38),(5,37)):
            self.state['story']['city_areas'][str(area)]={'id':area,'st':[0,False,False],
                'lv':1,'bd':{'1':{'id':building,'uuid':'%024x'%building}}}
        self.tables=dict(self.raw,event_content=self.content,event_condition=self.triggers)
        self.city_tables=dict(fixture.catalogs,content=self.content,triggers=self.triggers,
            daerweila_dispatch=self.raw['daerweila_dispatch'])
        for key,name in (('building','city_building'),('development','city_development'),
                         ('upgrade','city_upgrade'),('patrol','city_patrol'),('hero','hero')):
            self.city_tables[key]=self.raw[name]
        self.abilities={str(hero):{'insight':100,'construct':100,'leadership':100}
                        for hero in (24,7,8)}

    def call(self,name,*args,**kwargs):
        return self.api[name](*args,**kwargs)

    def patrol(self,area=3):
        self.state,notices,changed,diagnostic=self.call('prepare_city_action',self.state,
            'enterPatrolRequest',{'aid':area,'hs':[24,7,8]},self.city_tables,
            'full-original-paid-patrol:%s'%area,self.abilities,
            evaluate_condition=self.api['evaluate_offline_condition'])
        self.assertTrue(changed,diagnostic)
        self.assertEqual(diagnostic['optional_unknown_events'],[])
        self.assertEqual(len(self.state['profile']['heroes']),140)
        return notices

    def begin(self,event):
        # Preserve the whole request transaction on failure. Native gateway
        # tests separately cover its concrete restore/save and reply wrapper.
        candidate,_=self.call('select_city_patrol_event',self.state,event)
        self.call('begin_story_occurrence',candidate,event,self.content,self.triggers,
                  tables=self.tables)
        candidate['available_events']=[pair for pair in candidate['available_events'] if pair[0]!=event]
        candidate['processing_events'].append(event)
        candidate,notices=self.call('prepare_story_operation',candidate,'start',
            {'e':event},self.content,self.triggers,self.tables)
        self.state=candidate
        return notices

    def operation(self,operation,args):
        self.state,notices=self.call('prepare_story_operation',self.state,operation,args,
                                     self.content,self.triggers,self.tables)
        for name,body in notices:
            if name=='completeEventReplyEnd':
                self.state,_=self.call('complete_city_patrol_event',self.state,body['e'])
        return notices

    def test_full_catalog_paid_patrol_to_terminal_survives_root_cleanup_and_reload(self):
        self.patrol()
        self.assertEqual(self.state['city_actions']['patrol']['events'],[4124,4161,4213])
        self.assertEqual(set(dict(self.state['available_events'])),{4124,4161,4213})
        after_paid=copy.deepcopy(self.state['profile'])
        self.begin(4124)
        self.operation('trace',{'k':'dialog','d':{'c':4124}})
        self.operation('option',{'e':4124,'se':4125,'op':0})
        self.assertIsNone(self.state['city_actions']['patrol'])
        self.state['city_actions']['receipts']=[]
        self.state=json.loads(json.dumps(self.state))
        self.operation('trace',{'k':'dialog','d':{'c':4125}})
        self.operation('option',{'e':4125,'se':4126,'op':0})
        self.assertEqual(self.state['story'].get('daerweila_human',0),0)
        notices=self.operation('trace',{'k':'dialog','d':{'c':4126}})
        self.assertEqual(self.state['story']['daerweila_human'],1)
        self.assertNotIn(4213,self.state['completed_events'])
        self.assertNotIn(4161,self.state['completed_events'])
        self.assertEqual(self.state['profile'],after_paid)
        self.assertIn(2,self.state['story']['route_targets']['13-1'])
        self.assertEqual(self.state['story']['city_op_exclam']['3']['patrol'],-1)
        self.assertEqual(sum(name=='offlineDaerweilaAward' for name,_ in notices),1)
        self.call('validate_daerweila_state',self.state)
        before=copy.deepcopy(self.state)
        self.assertEqual(self.operation('trace',{'k':'dialog','d':{'c':4126}}),[])
        self.assertEqual(self.state,before)

    def test_current_lock_is_rechecked_after_paid_patrol_without_consuming_choice(self):
        self.patrol()
        self.state['story']['daerweila_human_lock']=True
        before=copy.deepcopy(self.state)
        with self.assertRaises(ValueError):self.begin(4124)
        self.assertEqual(self.state,before)
        self.state,_=self.call('prepare_daerweila_first_choice',self.state,{},self.tables,
                               self.call('daerweila_request_source',self.state))
        self.assertFalse(self.call('project_daerweila',self.state)['dwca'])
        self.begin(4161)
        self.assertTrue(self.call('project_daerweila',self.state)['dwca'])
        self.assertEqual(self.state['story']['daerweila_dispatch']['awards'],{})

    def test_original_readonly_rows_leave_only_plain_durable_dispatch_proofs(self):
        readonly=lambda rows:ReadOnlyOriginalRow({key:ReadOnlyOriginalRow(row)
                                                for key,row in rows.items()})
        self.content=readonly(self.content)
        self.triggers=readonly(self.triggers)
        dispatch_rows=readonly(self.raw['daerweila_dispatch'])
        self.tables=dict(self.tables,event_content=self.content,event_condition=self.triggers,
                         daerweila_dispatch=dispatch_rows)
        self.city_tables=dict(self.city_tables,content=self.content,triggers=self.triggers,
                              daerweila_dispatch=dispatch_rows)
        self.patrol()
        original=self.call('compile_daerweila_dispatch',self.raw['daerweila_dispatch'],
                            self.api_content,self.api_triggers)
        self.assertEqual(self.state['story']['daerweila_dispatch']['catalog'],original)
        self.begin(4124)
        self.state=json.loads(json.dumps(self.state))
        self.call('validate_daerweila_state',self.state)
        self.assertIs(type(self.state['story']['daerweila_dispatch']['catalog']),dict)

    @property
    def api_content(self):return type(self).content
    @property
    def api_triggers(self):return type(self).triggers


class IndependentFlatDispatchTests(IndependentDispatchTests):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        source=ast.literal_eval(ast.parse(embedded_loader(ROOT/'runtime').splitlines()[0]).body[0].value)
        real_import=builtins.__import__
        def imports(name,globals=None,locals=None,fromlist=(),level=0):
            if name.startswith('offline_'):raise ImportError('production flat namespace')
            return real_import(name,globals,locals,fromlist,level)
        namespace={'__name__':'independent_flat_dispatch',
            '__builtins__':dict(vars(builtins),__import__=imports)}
        exec(compile(source,'<actual-embedded-dispatch>','exec'),namespace,namespace)
        cls.api=namespace


if __name__=='__main__':unittest.main()
