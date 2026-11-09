"""One-time budget policy using native bootstrap save action evidence."""
import copy
import json
from pathlib import Path
import sys
import unittest
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'runtime'),str(ROOT/'tools')]
from offline_postbattle import prepare_initial_city_budget,apply_first_battle_clearance
from offline_city_actions import prepare_city_action
from offline_stage import prepare_stage_admission,prepare_stage_finish
from export_game_catalogs import decode
import test_gateway_integrations as gateway_fixtures


class InitialBudgetTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.fixture=json.loads((ROOT/'tests/fixtures/initial-city-budget-native-save.json').read_text())
        cls.city=decode(json.loads((ROOT/'tests/fixtures/offline_city_actions_cdata.json').read_text())['tables'])
        raw=json.loads((ROOT/'tests/fixtures/offline_stage_cdata.json').read_text())
        cls.missions={int(k):v for k,v in raw['missions'].items()}
        cls.cities={int(k):v for k,v in raw['city_data'].items()}
    def setUp(self):self.state=copy.deepcopy(self.fixture['state'])
    def test_actual_native_zero_placeholder_migrates_once_and_real_first_patrol_costs2(self):
        self.assertEqual(len(self.fixture['source_file_sha256']),64)
        self.assertEqual(self.state['story']['city_values']['av'],0)
        original=copy.deepcopy(self.state)
        state,changed,diagnostic=prepare_initial_city_budget(self.state)
        self.assertTrue(changed,diagnostic)
        self.assertEqual(state['story']['city_values']['av'],24)
        self.assertEqual(state['story']['initial_action_budget']['first_fight_id'],'6ae8d87b421aa914d65b0dda')
        self.assertEqual(state['completed_events'],original['completed_events'])
        self.assertEqual(state['story']['battle_wins'],[101])
        self.assertEqual(state['story']['date'],0)
        self.assertEqual(state['day'],original['day'])
        self.assertEqual(self.state,original)
        self.assertEqual(prepare_initial_city_budget(state)[0],state)
        heroes=[7,8,24]
        abilities={str(h):{'insight':100,'construct':100,'leadership':100}for h in heroes}
        catalogs=dict(self.city,triggers={},content={})
        patrolled,notices,changed,diagnostic=prepare_city_action(state,'enterPatrolRequest',{'aid':1,'hs':heroes},catalogs,'actual-host-first-patrol',abilities,lambda:'a'*24)
        self.assertTrue(changed)
        self.assertEqual(patrolled['story']['city_values']['av'],22)
        self.assertEqual(patrolled['city_actions']['patrol']['admission_id'],'actual-host-first-patrol')
        self.assertEqual(prepare_initial_city_budget(patrolled)[0],patrolled)
    def test_fresh_pending_marker_activates_only_after_actual101_clearance(self):
        from offline_story import initial_story_state
        state=copy.deepcopy(self.state)
        state['story']['initial_action_budget']=initial_story_state()['initial_action_budget']
        state['story']['first_clearance_applied']=False
        state['story']['city_areas']['1']['st'][0]=1
        state['story']['city_areas'].pop('2')
        missing=copy.deepcopy(state);missing['battle']['receipts']=[];missing['story']['battle_wins']=[]
        self.assertFalse(prepare_initial_city_budget(missing)[1])
        cleared,notices,changed=apply_first_battle_clearance(state,self.missions)
        self.assertTrue(changed)
        self.assertEqual(cleared['story']['city_values']['av'],24)
        self.assertEqual(cleared['story']['initial_action_budget']['source'],'fresh-first-clearance')
        self.assertTrue(any(n=='get_all_area_info_reply'and p['cd']['av']==24 for n,p in notices))
        self.assertEqual(apply_first_battle_clearance(cleared,self.missions)[0],cleared)
    def test_contrary_history_day_week_and_markers_never_refill_zero(self):
        for mode in ('day_spent','week_spent','city_receipt','patrol','non101_win','other_fight','active','day_receipt','intent','review','week_history','day1','week1','marker','area_build'):
            state=copy.deepcopy(self.state)
            if mode=='day_spent':state['day']['actions_spent']=2
            if mode=='week_spent':state['story']['week_actions_spent']=2
            if mode=='city_receipt':state['city_actions']['receipts']=[{'id':'real-prior-city-operation'}]
            if mode=='patrol':state['city_actions']['patrol']={'area':1}
            if mode=='non101_win':state['story']['battle_wins'].append(1101)
            if mode=='other_fight':state['battle']['receipts'].append({'fight_id':'real-stage','reply':{'t':1,'s':1101,'w':0}})
            if mode=='active':state['battle']['active']={'fight_id':'actual-active'}
            if mode=='day_receipt':state['day']['receipt']={'day':0}
            if mode=='intent':state['day']['intent']={'day':0}
            if mode=='review':state['day']['review']={'c':{},'l':{}}
            if mode=='week_history':state['week_protocol']['history']=[{'week':0}]
            if mode=='day1':state['day']['stock_day']=1
            if mode=='week1':state['story']['week']=1
            if mode=='marker':state['story']['initial_action_budget']={'status':'activated'}
            if mode=='area_build':state['story']['city_areas']['1']['bd']={'1':{'id':1}}
            before=copy.deepcopy(state)
            with self.subTest(mode=mode):
                planned,changed,diagnostic=prepare_initial_city_budget(state)
                self.assertFalse(changed,diagnostic)
                self.assertEqual(planned,before)
                self.assertEqual(state,before)
    def test_positive_existing_budget_is_preserved_and_marked_without_addition(self):
        self.state['story']['city_values']['av']=22
        state,changed,diagnostic=prepare_initial_city_budget(self.state)
        self.assertTrue(changed)
        self.assertEqual(state['story']['city_values']['av'],22)
        self.assertEqual(state['story']['initial_action_budget']['granted'],0)
        state['story']['city_values']['av']=0
        self.assertFalse(prepare_initial_city_budget(state)[1])
        self.assertEqual(prepare_initial_city_budget(state)[0]['story']['city_values']['av'],0)
    def test_actual_stage_cost_transactions_exhaust_budget_and_restart_stays_zero(self):
        state,changed,diagnostic=prepare_initial_city_budget(self.state)
        scenes=list(range(1101,1107))+list(range(2101,2107))
        for index,scene in enumerate(scenes):
            hero=(24,7,8)[index//4]
            area=self.missions[scene]['ch']
            active,_=prepare_stage_admission(state,{'t':1,'s':scene,'h':[hero],'d':{'a':area}},self.missions,lambda:'host-actual-%s'%scene)
            def settle(admission,result):return dict(result,r={'money':1}),{'profile':copy.deepcopy(state['profile']),'notices':[],'granted':[]}
            state,reply,effects,changed=prepare_stage_finish(active,{'t':1,'s':scene,'h':[hero],'x':[],'w':1},self.missions,self.cities,settle,'host-actual-%s'%scene)
        self.assertEqual(state['story']['city_values']['av'],0)
        self.assertEqual(len(state['battle']['receipts']),13)
        self.assertFalse(prepare_initial_city_budget(state)[1])
        self.assertEqual(prepare_initial_city_budget(state)[0]['story']['city_values']['av'],0)


class InitialBudgetGatewayTests(gateway_fixtures.IntegratedGatewayTests):
    def test_actual_native_legacy_migration_save_failure_has_no_budget_or_marker(self):
        state=copy.deepcopy(InitialBudgetTests.fixture['state']) if hasattr(InitialBudgetTests,'fixture') else json.loads((ROOT/'tests/fixtures/initial-city-budget-native-save.json').read_text())['state']
        self.proxy.restore_progress(state)
        self.proxy.save_progress()
        before=self.proxy.progress_snapshot()
        with patch.object(self.proxy._store,'write',side_effect=OSError('disk full')):
            with self.assertRaises(OSError):self.proxy.ensure_postbattle_progress()
        self.assertEqual(self.proxy.progress_snapshot(),before)
        self.assertNotIn('initial_action_budget',self.proxy.story)
        self.proxy.ensure_postbattle_progress()
        self.assertEqual(self.proxy.story['city_values']['av'],24)
        self.assertEqual(self.proxy.story['initial_action_budget']['status'],'activated')
        self.assertEqual(self.proxy.profile,before['profile'])
