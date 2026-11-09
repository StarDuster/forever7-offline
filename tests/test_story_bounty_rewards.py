"""Finite original route31 virtual bounty producers, not route35 cycle state."""
import copy
from pathlib import Path
import sys
import unittest
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'runtime'),str(ROOT/'tools'),str(ROOT/'analysis/research-agent')]
import test_offline_event_effects as effects
from offline_event_effects import plan_event_effects,apply_event_effects_snapshot
from offline_conditions import evaluate_offline_condition
from read_data_table import read

class BountyRewardTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tables=effects.original_tables()
        cls.content=read(ROOT/'analysis/decompiled/event_content.py')
        cls.triggers=read(ROOT/'analysis/decompiled/event_condition.py')
        cls.reward_ids={rid for rid,row in cls.tables['reward_common'].items()if 13624 in row.get('items',())}
        cls.events={e:r for e,r in cls.content.items()if set(r.get('rewards',())) & cls.reward_ids}
    def setUp(self):
        self.state=effects.base_state(self.tables)
        self.state['story'].update(route='31',week=0,date=2)
    def award(self,event,state=None,receipt=None):
        context={'receipt_key':receipt or 'actual:'+str(event)}
        return plan_event_effects(state or self.state,event,self.content,self.tables,context)
    def test_all17_actual_event_refs_and9_original_reward_amounts_once(self):
        self.assertEqual(len(self.reward_ids),9);self.assertEqual(len(self.events),17)
        self.assertEqual(set(self.events),{3506,3507,3508,3509,3510,3513,3514,3515,3516,3517,3522,3523,5539,5541,5542,5545,5546})
        for route in ('31','31-4'):
            for event,row in self.events.items():
                state=copy.deepcopy(self.state);state['story']['route']=route
                before=copy.deepcopy(state)
                done,notices,diag=self.award(event,state)
                self.assertTrue(diag['ready'],diag)
                amount=sum(r['itemsNum'][r['items'].index(13624)]for rid in row['rewards']for r in [self.tables['reward_common'][rid]]if 13624 in r.get('items',()))
                self.assertEqual(done['story']['general_value'],amount)
                self.assertIn(('syncStoryGeneralValue',{'v':amount}),notices)
                self.assertEqual(done['gacha']['items'],before['gacha']['items'])
                self.assertEqual(done['completed_events'],[])
                replay,again,diag=self.award(event,done)
                self.assertEqual(replay,done);self.assertEqual(again,[])
                self.assertEqual(apply_event_effects_snapshot(done,{'std':{'keep':7}})['std']['gr'],amount)
    def test_real_reward_accumulation_crosses_original50_and300_conditions(self):
        state=self.state
        self.assertTrue(evaluate_offline_condition(54,self.triggers[4481]['conds'][54],state))
        for event in (3506,3522):
            state,unused,diag=self.award(event,state);self.assertTrue(diag['ready'])
        self.assertEqual(state['story']['general_value'],50)
        self.assertTrue(evaluate_offline_condition(54,self.triggers[4480]['conds'][54],state))
        self.assertFalse(evaluate_offline_condition(54,self.triggers[4481]['conds'][54],state))
        for event in (3507,3508,3509,3510,3513,3514,3515,3516,3517,3523):
            state,unused,diag=self.award(event,state);self.assertTrue(diag['ready'])
        self.assertEqual(state['story']['general_value'],308)
        self.assertTrue(evaluate_offline_condition(54,self.triggers[3525]['conds'][54],state))
    def test_route_scoped_zero_and_no_legacy_inventory_exchange_or_route35_counter(self):
        initial=copy.deepcopy(self.state)
        self.assertTrue(evaluate_offline_condition(54,'[0,0]',initial))
        self.assertEqual(apply_event_effects_snapshot(initial,{'std':{}})['std']['gr'],0)
        self.assertEqual(initial,self.state)
        initial['story']['route']='35'
        self.assertIsNone(evaluate_offline_condition(54,'[1,7]',initial))
        done,notices,diag=self.award(3506,initial)
        self.assertFalse(diag['ready']);self.assertEqual(done,initial);self.assertEqual(notices,[])
        self.assertNotIn('general_value',done['story'])
    def test_late_bad_reward_rolls_back_scalar_and_nonnegative_debit_guard(self):
        tables=dict(self.tables,reward_common=dict(self.tables['reward_common']))
        tables['reward_common'][999999]={'id':999999,'items':(13624,),'itemsNum':(-26,)}
        content={3506:dict(self.content[3506],rewards=(60089,999999))}
        done,notices,diag=plan_event_effects(self.state,3506,content,tables,{})
        self.assertFalse(diag['ready']);self.assertEqual(done,self.state);self.assertEqual(notices,[])

import test_gateway_integrations as integrations

class BountyGatewayTests(unittest.TestCase):
    table=integrations.IntegratedGatewayTests.table
    @classmethod
    def setUpClass(cls):BountyRewardTests.setUpClass()
    def setUp(self):
        integrations.IntegratedGatewayTests.setUp(self)
        self.proxy.story.update(route='31',date=2)
        self.proxy.story_effect_tables=lambda:BountyRewardTests.tables
        self.table('event_content',{3506:BountyRewardTests.content[3506]})
        self.table('event_condition',{})
        self.table('reward_common',BountyRewardTests.tables['reward_common'])
        self.proxy.available_events={3506:1}
        self.proxy.save_progress()
    def test_actual_dialog_completion_saves_before_scalar_notice_rollback_replay_restart(self):
        self.proxy.reliable_call({'w':{'m':'startEvent','p':{'e':3506},'r':901}})
        self.assertIn(3506,self.proxy.processing_events)
        before=copy.deepcopy(self.proxy.progress_snapshot())
        self.owner.replies=[]
        with patch.object(self.proxy._store,'write',side_effect=OSError('full')):
            with self.assertRaises(OSError):self.proxy.process_story('trace',{'k':'dialog','d':{'c':3506}})
        self.assertEqual(self.proxy.progress_snapshot(),before)
        self.assertFalse(any(n=='syncStoryGeneralValue' for n,p in self.owner.replies))
        self.proxy.process_story('trace',{'k':'dialog','d':{'c':3506}})
        self.assertEqual(self.proxy.story['general_value'],25)
        self.assertIn(3506,self.proxy.completed_events)
        self.assertIn(('syncStoryGeneralValue',{'v':25}),self.owner.replies)
        saved=copy.deepcopy(self.proxy.progress_snapshot())
        self.owner.replies=[]
        self.proxy.process_story('trace',{'k':'dialog','d':{'c':3506}})
        self.assertEqual(self.proxy.progress_snapshot(),saved)
        self.assertFalse(any(n=='syncStoryGeneralValue' for n,p in self.owner.replies))
        restored=integrations.gateway.LocalProxy(None,self.owner,persistent=True)
        self.assertEqual(restored.story,self.proxy.story)
        self.assertEqual(restored.story['general_value'],25)
        self.assertEqual(apply_event_effects_snapshot(restored.progress_snapshot(),{'std':{}})['std']['gr'],25)
