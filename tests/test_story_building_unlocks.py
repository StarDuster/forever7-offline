"""Original event reward -> blueprint -> actual user construction -> condition.

These host fixtures exercise producers without claiming original event/date/win
completion. The original story engine remains responsible for admitting events.
"""
import copy
import json
from pathlib import Path
import sys
import unittest
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'runtime'),str(ROOT/'tools'),str(ROOT/'analysis/research-agent')]
from read_literal_marshal import read
from read_data_table import read as read_source
from export_game_catalogs import decode
from offline_city_actions import prepare_city_action
from offline_event_effects import plan_event_effects,apply_event_effects_snapshot
from offline_conditions import evaluate_offline_condition
import test_offline_event_effects as effects

class OriginalStoryBuildingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tables=effects.original_tables()
        cls.content=read_source(ROOT/'analysis/decompiled/event_content.py')
        cls.triggers=read_source(ROOT/'analysis/decompiled/event_condition.py')
        base=ROOT/'analysis/android640-scripts/com/data/cdata'
        cls.catalogs={key:read(base/(name+'.marshal'))for key,name in [('building','city_building'),('development','city_development'),('upgrade','city_upgrade'),('patrol','city_patrol'),('hero','hero')]}
        cls.fixture=decode(json.loads((ROOT/'tests/fixtures/offline_city_actions_cdata.json').read_text())['tables'])
    def setUp(self):
        self.state={'story':{'week':0,'date':0,'emergency':False,'route':'11','city_values':{'av':24,'fv':5,'rv':300,'dv':5,'bf':100,'pn':1},
            'city_areas':{str(a):{'id':a,'lv':1,'st':[0,False,False],'bd':{}}for a in range(1,9)}},
            'profile':{'heroes':{str(h):{'cf':100,'ef':0,'sk':{}}for h in (129,145,125)},'economy':{'money':1000000}},
            'completed_events':[],'processing_events':[],'available_events':[],'conditions':[],'day':{'stock_day':0}}
        self.heroes=[129,145,125]
        self.abilities={str(h):{'construct':self.catalogs['hero'][h]['constructValue'],'leadership':self.catalogs['hero'][h]['leadershipValue'],'insight':self.catalogs['hero'][h]['insightValue']}for h in self.heroes}
    def unlock(self,event,state=None):
        candidate,notices,diag=plan_event_effects(state or self.state,event,self.content,self.tables,effects.evidence_context(event,self.content[event]))
        self.assertTrue(diag['ready'],diag)
        self.assertEqual(candidate['completed_events'],[])
        return candidate,notices
    def build(self,state,bid,aid,identity='build',slot=1):
        return prepare_city_action(state,'areaBuildRequest',{'aid':aid,'hs':self.heroes,'fi':slot,'bi':bid},self.catalogs,identity,self.abilities,lambda:'placed-'+identity,evaluate_condition=evaluate_offline_condition)
    def test_real5094_reward41295_unlock39_and_actual_placement_satisfies5095(self):
        self.assertEqual(self.content[5094]['rewards'],(41295,))
        self.assertEqual(self.tables['reward_common'][41295]['buildableBuilding'],(39,))
        with self.assertRaisesRegex(ValueError,'blueprint'):self.build(self.state,39,1)
        state,notices=self.unlock(5094)
        self.assertEqual(state['story']['buildable_buildings'],[39])
        self.assertTrue(any(n=='add_hidden_building' and p['hb']==[39]for n,p in notices))
        snapshot=apply_event_effects_snapshot(state,{'city':{}})
        self.assertEqual(snapshot['city']['hb'],[39])
        cond=self.triggers[5095]['conds'][18]
        self.assertFalse(evaluate_offline_condition(18,cond,state))
        done,notices,changed,diag=self.build(state,39,1)
        self.assertTrue(changed);self.assertTrue(evaluate_offline_condition(18,cond,done))
        self.assertEqual(done['story']['city_values']['av'],22)
        self.assertEqual(done['profile']['heroes']['129']['cf'],95)
        self.assertEqual(done['story']['city_areas']['1']['bd']['1']['id'],39)
        replay,again,changed,diag=self.build(done,39,1)
        self.assertFalse(changed);self.assertEqual(replay,done)
        with self.assertRaisesRegex(ValueError,'limit'):self.build(done,39,1,'duplicate',2)
        self.assertEqual(done['completed_events'],[])
    def test_real2235_unlocks_all_eight_barriers_in_exact_original_areas(self):
        self.assertEqual(self.content[2235]['rewards'],(54376,))
        for bid in range(40,48):
            state,notices=self.unlock(2235)
            self.assertEqual(state['story']['buildable_buildings'],list(range(40,48)))
            row=self.catalogs['building'][bid]
            aid=next(a for a,n in row['al'].items()if n==1)
            wrong=next(a for a,n in row['al'].items()if n==0)
            before=copy.deepcopy(state)
            with self.assertRaisesRegex(ValueError,'limit'):self.build(state,bid,wrong)
            self.assertEqual(state,before)
            done,unused,changed,diag=self.build(state,bid,aid)
            self.assertTrue(changed)
            self.assertEqual(done['story']['city_areas'][str(aid)]['bd']['1']['id'],bid)
            self.assertTrue(evaluate_offline_condition(18,{aid:(bid,)},done))
            if bid==40:self.assertTrue(evaluate_offline_condition(18,self.triggers[2237]['conds'][18],done))
            with self.assertRaisesRegex(ValueError,'limit'):self.build(done,bid,aid,'second',2)
    def test_unlocked_building_still_requires_research_capability_budget_and_free_area(self):
        state,unused=self.unlock(5094)
        for reason in ('research','capability','budget','fatigue','area','ban','clientBan'):
            candidate=copy.deepcopy(state);catalogs=copy.deepcopy(self.catalogs);abilities=copy.deepcopy(self.abilities)
            if reason=='research':candidate['story']['city_values']['rv']=79
            elif reason=='capability':
                for values in abilities.values():values['construct']=0
            elif reason=='budget':candidate['story']['city_values']['av']=1
            elif reason=='fatigue':candidate['profile']['heroes']['129']['cf']=4
            elif reason=='area':candidate['story']['city_areas']['1']['st'][0]=1
            else:catalogs['building'][39][reason]=1
            before=copy.deepcopy(candidate)
            with self.assertRaises(ValueError):prepare_city_action(candidate,'areaBuildRequest',{'aid':1,'hs':self.heroes,'fi':1,'bi':39},catalogs,'reject',abilities,lambda:'no')
            self.assertEqual(candidate,before)

import test_gateway_integrations as integrations
from unittest.mock import patch

class StoryBuildingGatewayTests(unittest.TestCase):
    table=integrations.IntegratedGatewayTests.table
    @classmethod
    def setUpClass(cls):
        OriginalStoryBuildingTests.setUpClass()
    def setUp(self):
        integrations.IntegratedGatewayTests.setUp(self)
        for key,name in [('building','city_building'),('development','city_development')]:
            self.table(name,OriginalStoryBuildingTests.catalogs[key])
        self.proxy.story['city_values'].update(av=24,rv=80)
    def test_actual_blueprint_reward_build_failure_atomic_replay_and_restart(self):
        candidate,notices,diag=plan_event_effects(self.proxy.progress_snapshot(),5094,OriginalStoryBuildingTests.content,OriginalStoryBuildingTests.tables,{})
        self.assertTrue(diag['ready'],diag)
        self.proxy.restore_progress(candidate);self.proxy.save_progress()
        before=copy.deepcopy(self.proxy.progress_snapshot())
        args={'aid':1,'fi':1,'bi':39,'hs':[24]}
        with patch.object(self.proxy._store,'write',side_effect=OSError('full')):
            with self.assertRaises(OSError):self.proxy.handle_city_action('areaBuildRequest',args,'actual-ark',31)
        self.assertEqual(self.proxy.progress_snapshot(),before)
        self.assertFalse(self.owner.replies[-1][1]['rs'])
        self.owner.replies=[]
        self.proxy.handle_city_action('areaBuildRequest',args,'actual-ark',32)
        self.assertTrue(self.owner.replies[-1][1]['rs'])
        self.assertEqual(self.proxy.story['city_areas']['1']['bd']['1']['id'],39)
        done=copy.deepcopy(self.proxy.progress_snapshot())
        self.proxy.handle_city_action('areaBuildRequest',args,'actual-ark',33)
        self.assertEqual(self.proxy.progress_snapshot(),done)
        restored=integrations.gateway.LocalProxy(None,self.owner,persistent=True)
        self.assertEqual(restored.story,self.proxy.story)
        self.assertEqual(restored.city_actions,json.loads(json.dumps(self.proxy.city_actions)))
        restarted=copy.deepcopy(restored.progress_snapshot())
        restored.handle_city_action('areaBuildRequest',args,'actual-ark',34)
        self.assertEqual(restored.progress_snapshot(),restarted)
        self.assertTrue(evaluate_offline_condition(18,OriginalStoryBuildingTests.triggers[5095]['conds'][18],restored.progress_snapshot()))
