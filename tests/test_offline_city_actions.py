"""Static original cdata and host city RPC contracts; no live game automation."""
import copy
import hashlib
import json
from pathlib import Path
import sys
from types import SimpleNamespace
import unittest
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'runtime'))
sys.path.insert(0, str(ROOT / 'tools'))
from export_game_catalogs import decode
from offline_story import evaluate_story_condition
from offline_city_actions import (prepare_city_action, native_city_action_abilities,
    select_city_patrol_event, complete_city_patrol_event, city_action_area_snapshot)


class CityActionTests(unittest.TestCase):
    def setUp(self):
        self.fixture = json.loads((ROOT / 'tests/fixtures/offline_city_actions_cdata.json').read_text())
        self.catalogs = decode(self.fixture['tables'])
        self.state = {'story': {'week': 0, 'date': 0, 'emergency': False, 'route': '1',
                               'city_values': {'av': 24, 'fv': 5, 'rv': 5, 'dv': 5, 'bf': 100, 'pn': 1},
                               'city_areas': {'1': {'id': 1, 'lv': 1, 'st': [0, False, False], 'bd': {}}}},
                      'profile': {'heroes': {str(h): {'cf': 100, 'ef': 0, 'sk': {'owned': h}} for h in (7,8,24)},
                                  'treasures': ['owned']},
                      'available_events': [], 'completed_events': [8], 'processing_events': [],
                      'conditions': [], 'day': {'stock_day': 0}}
        self.heroes = [7,8,24]
        self.abilities = {str(h): {'insight': self.catalogs['hero'][h]['insightValue'],
                                 'construct': self.catalogs['hero'][h]['constructValue'],
                                 'leadership': self.catalogs['hero'][h]['leadershipValue']} for h in self.heroes}
        self.count = 0

    def act(self, operation, arguments, state=None, identity=None):
        self.count += 1
        return prepare_city_action(state or self.state, operation, arguments, self.catalogs,
            identity or 'session:%s' % self.count, self.abilities, lambda: 'building-%s' % self.count,
            evaluate_condition=evaluate_story_condition)

    def test_fixture_hashes_and_native_capabilities_call_actual_original_getters(self):
        for name,digest in self.fixture['sha256'].items():
            source = ROOT / ('analysis/android640-scripts/com/data/cdata/' + name + '.marshal')
            self.assertEqual(hashlib.sha256(source.read_bytes()).hexdigest(), digest)
        hero = SimpleNamespace(getInsightValue=lambda: 17, getConstructValue=lambda: 19,
                               getLeadershipValue=lambda: 23)
        owner = SimpleNamespace(heroMgrData=SimpleNamespace(getHero=lambda hid: hero if hid==24 else None))
        self.assertEqual(native_city_action_abilities(owner,[24]), {'24': {'insight':17,'construct':19,'leadership':23}})
        with self.assertRaises(ValueError): native_city_action_abilities(owner,[999])

    def test_build_spends_original_table_costs_and_updates_real_native_area_callback(self):
        before = copy.deepcopy(self.state)
        done, notices, changed, _ = self.act('areaBuildRequest', {'aid':1,'fi':1,'bi':2,'hs':self.heroes})
        self.assertTrue(changed)
        self.assertEqual(done['story']['city_values']['av'],22)
        self.assertEqual(done['story']['city_values']['fv'],10)
        self.assertEqual(done['story']['city_areas']['1']['fv'],5)
        self.assertEqual(done['profile']['heroes']['24']['cf'],95)
        self.assertEqual(done['story']['city_areas']['1']['bd']['1']['id'],2)
        self.assertEqual(done['story']['city_values']['tbn'],1)
        self.assertEqual(notices[-1], ('area_build_reply',{'rs':True,'aid':1,'ext':{}}))
        self.assertEqual(notices[-2][0],'get_all_area_info_reply')
        self.assertIn('area_1',notices[-2][1]['ais'])
        self.assertEqual(self.state,before)
        self.assertEqual(done['profile']['treasures'],['owned'])

    def test_build_reliable_replay_cannot_double_charge_or_reuse_identity(self):
        args={'aid':1,'fi':1,'bi':7,'hs':self.heroes}
        done, notices, _, _ = self.act('areaBuildRequest',args,identity='same')
        replay, again, changed, diagnostic = self.act('areaBuildRequest',args,done,'same')
        self.assertFalse(changed)
        self.assertTrue(diagnostic['replay'])
        self.assertEqual(replay,done)
        self.assertEqual(again,notices)
        with self.assertRaises(ValueError): self.act('areaBuildRequest',dict(args,fi=2),done,'same')
        next_done,_,changed,_=self.act('areaBuildRequest',dict(args,fi=2),done,'new')
        self.assertTrue(changed)
        self.assertEqual(next_done['story']['city_values']['av'],20)

    def test_original_field_level_limits_team_power_and_resources_guard_without_spend(self):
        for kind in ('slot','level','power','action','fatigue','area','special','team'):
            self.setUp()
            args={'aid':1,'fi':1,'bi':2,'hs':self.heroes}
            if kind=='slot': args['fi']=99
            if kind=='level': args['fi']=5
            if kind=='power': self.abilities['24']['construct']=0;self.abilities['8']['construct']=0
            if kind=='action': self.state['story']['city_values']['av']=1
            if kind=='fatigue': self.state['profile']['heroes']['24']['cf']=1
            if kind=='area': self.state['story']['city_areas']['1']['st'][0]=1
            if kind=='special': args['bi']=35
            if kind=='team': args['hs']=[24,24]
            before=copy.deepcopy(self.state)
            with self.assertRaises(ValueError,msg=kind): self.act('areaBuildRequest',args)
            self.assertEqual(self.state,before)

    def test_development_advances_one_original_level_and_unlocks_original_field(self):
        done, notices, changed, _=self.act('areaLevelUpRequest',{'aid':1,'luv':1,'hs':self.heroes})
        self.assertEqual(done['story']['city_areas']['1']['lv'],2)
        self.assertEqual(done['story']['city_areas']['1']['mbn'],5)
        self.assertEqual(done['story']['city_values']['tvn'],1)
        self.assertEqual(done['story']['city_values']['av'],22)
        self.assertEqual(notices[-1],('area_level_up_reply',{'rs':True,'aid':1,'ext':{}}))
        self.act('areaBuildRequest',{'aid':1,'fi':5,'bi':2,'hs':self.heroes},done)
        with self.assertRaises(ValueError): self.act('areaLevelUpRequest',{'aid':1,'luv':2,'hs':self.heroes})

    def test_patrol_enters_original_choice_ui_and_friendship_requires_real_choice(self):
        args={'aid':1,'hs':self.heroes}
        done,notices,_,_=self.act('enterPatrolRequest',args)
        self.assertEqual(notices[-1],('enter_patrol_reply',{'s':True,'rs':True,'ext':{},'ev':[]}))
        self.assertEqual(done['story']['city_values']['av'],22)
        self.assertEqual(done['story']['city_values']['pn'],2)
        self.assertEqual(done['story']['city_values']['tpn'],1)
        self.assertEqual(done['profile']['heroes']['24']['ef'],0)
        repeated,_,changed,diag=self.act('enterPatrolRequest',args,done)
        self.assertFalse(changed)
        self.assertTrue(diag['resume_patrol'])
        self.assertEqual(repeated,done)
        claimed,notices,_,_=self.act('patrolReward',{},done,'claim-one')
        self.assertEqual(claimed['profile']['heroes']['24']['ef'],4)
        self.assertEqual(claimed['story']['city_values']['av'],22)
        self.assertIsNone(claimed['city_actions']['patrol'])
        self.assertFalse(claimed['story']['patrol_pending'])
        self.assertEqual(notices[-2],('notify_add_friendly',{'fr':{'7':4,'8':4,'24':4},'n':{}}))
        again=self.act('patrolReward',{},claimed,'claim-one')
        self.assertFalse(again[2])
        self.assertEqual(again[0],claimed)

    def patrol_fixture(self):
        self.catalogs['triggers']={
            111:{'release':1,'conds':{3:'set([1])',10:'set([24])',102:'set([2])',1:'set([8])'}},
            222:{'release':1,'conds':{3:'set([1])',52:"set(['other-route'])",999:'unsupported'}},
            333:{'release':1,'conds':{3:'set([2])',999:'unsupported'}}}
        self.catalogs['content']={111:{'release':1,'eventType':1},222:{'release':1,'autoStart':True},333:{'release':1,'autoStart':True}}

    def test_patrol_context_drives_real_events_false_other_routes_do_not_block(self):
        self.patrol_fixture()
        done,notices,changed,diag=self.act('enterPatrolRequest',{'aid':1,'hs':self.heroes})
        self.assertTrue(changed)
        self.assertEqual(notices[-1][1]['ev'],[111])
        self.assertIn([111,1],done['available_events'])
        self.assertNotIn(111,done['completed_events'])
        selected,changed=select_city_patrol_event(done,111)
        self.assertTrue(changed)
        self.assertNotIn(111,selected['completed_events'])
        with self.assertRaises(ValueError): complete_city_patrol_event(selected,111)
        with self.assertRaises(ValueError): self.act('patrolReward',{},selected)
        selected['completed_events'].append(111) # fixture of REAL event planner completion
        complete,changed=complete_city_patrol_event(selected,111)
        self.assertTrue(changed)
        self.assertIsNone(complete['city_actions']['patrol'])
        self.assertEqual(complete['profile']['heroes']['24']['ef'],0)
        self.assertEqual(complete['story']['city_values']['av'],22)

    def test_current_required_unknown_event_stays_pending_before_spending(self):
        self.catalogs['triggers']={111:{'release':1,'conds':{3:'set([1])',999:'unknown'}}}
        self.catalogs['content']={111:{'release':1,'autoStart':True}}
        before=copy.deepcopy(self.state)
        done,notices,changed,diagnostic=self.act('enterPatrolRequest',{'aid':1,'hs':self.heroes})
        self.assertFalse(changed)
        self.assertFalse(notices)
        self.assertIn('pending',diagnostic)
        self.assertEqual(done,before)

    def test_original_metro_fireworks_and_gender_friendship_modifiers(self):
        area=self.state['story']['city_areas']['1']
        area['bd']={str(index):{'id':bid,'uuid':'fixture%s'%index} for index,bid in enumerate([21,22,23,24],1)}
        for hero in self.heroes: self.state['profile']['heroes'][str(hero)]['cf']=60
        done,_,_,_=self.act('enterPatrolRequest',{'aid':1,'hs':self.heroes})
        self.assertEqual(done['story']['city_values']['av'],23)
        self.assertEqual(done['profile']['heroes']['24']['cf'],85)
        self.assertNotIn(22,[b['id'] for b in done['story']['city_areas']['1']['bd'].values()])
        claimed,_,_,_=self.act('patrolReward',{},done)
        self.assertEqual(claimed['profile']['heroes']['24']['ef'],5)
        self.assertEqual(claimed['profile']['heroes']['8']['ef'],5)

    def test_building_capacity_synergies_and_cross_city_action_capability(self):
        # Original district research bonus gives +1 per producer; city +50%
        # rounds to nearest integer; capacities update by delta, preserving story offsets.
        area=self.state['story']['city_areas']['1']
        area['lv']=2
        area['rv']=20
        area['bd']={str(i):{'id':7,'uuid':'existing%s'%i} for i in range(1,5)}
        self.state['story']['city_values']['rv']=25
        done,_,_,_=self.act('areaBuildRequest',{'aid':1,'fi':5,'bi':8,'hs':self.heroes})
        self.assertEqual(done['story']['city_values']['rv'],35) # +5 base and +5 district synergy
        self.assertEqual(done['story']['city_areas']['1']['rv'],30)

    def test_original_research_coupon_consumed_once_and_used_coupon_cannot_discount(self):
        area=self.state['story']['city_areas']['1']
        area['bd']={'1':{'id':20,'uuid':'coupon','u':False}}
        self.state['story']['city_values']['rv']=10
        done,_,_,_=self.act('areaBuildRequest',{'aid':1,'fi':2,'bi':26,'hs':self.heroes})
        ids=[b['id'] for b in done['story']['city_areas']['1']['bd'].values()]
        self.assertNotIn(20,ids)
        self.assertIn(26,ids)
        self.assertEqual(done['story']['city_values']['rv'],10)
        area['bd']['1']['u']=True
        with self.assertRaises(ValueError):
            self.act('areaBuildRequest',{'aid':1,'fi':2,'bi':26,'hs':self.heroes})

    def test_original_global_metro_hub_supplies_actual_patrol_insight_bonus(self):
        self.state['story']['city_areas']['2']={'id':2,'lv':1,'st':[0,False,False],
            'bd':{'1':{'id':26,'uuid':'global-hub'}}}
        self.state['story']['city_values']['pn']=6 # original requirement22, base team insight18
        with self.assertRaises(ValueError): self.act('enterPatrolRequest',{'aid':1,'hs':self.heroes})
        self.state['story']['city_areas']['2']['bd']['2']={'id':26,'uuid':'second-global-hub'}
        done,_,changed,_=self.act('enterPatrolRequest',{'aid':1,'hs':self.heroes})
        self.assertTrue(changed)
        self.assertEqual(done['story']['city_values']['av'],22)

    def test_patrol_decline_and_finished_event_clear_only_actual_client_operation2(self):
        self.state['conditions']=[[101,0],[102,[4,7]]]
        done,_,_,_=self.act('enterPatrolRequest',{'aid':1,'hs':self.heroes})
        self.assertEqual(dict(done['conditions'])[102],[2,4,7])
        claimed,_,_,_=self.act('patrolReward',{},done)
        self.assertEqual(dict(claimed['conditions'])[102],[4,7])
        self.assertEqual(dict(claimed['conditions'])[101],0)
        other,changed=select_city_patrol_event(claimed,999)
        self.assertFalse(changed)
        self.assertEqual(other,claimed)

    def test_restart_and_failed_persistence_keep_prepared_effects_unpublished(self):
        entered,_,_,_=self.act('enterPatrolRequest',{'aid':1,'hs':self.heroes})
        restarted=json.loads(json.dumps(entered))
        before=copy.deepcopy(restarted)
        claimed,notices,changed,_=self.act('patrolReward',{},restarted,'claim-persist')
        self.assertTrue(changed)
        published=[]
        def persist(candidate): raise IOError('disk full')
        with self.assertRaises(IOError):
            persist(claimed)
            published.extend(notices)
        self.assertEqual(restarted,before)
        self.assertFalse(published)
        retry=self.act('patrolReward',{},restarted,'claim-persist')
        self.assertEqual(retry[0],claimed)


    def test_concatenated_android_namespace_needs_no_runtime_module_import(self):
        scope={'__name__':'embedded_city_actions'}
        for name in ('offline_conditions.py','offline_story.py','offline_city_actions.py'):
            exec(compile((ROOT/'runtime'/name).read_text(),name,'exec'),scope)
        self.patrol_fixture()
        done,notices,changed,diagnostic=scope['prepare_city_action'](
            self.state,'enterPatrolRequest',{'aid':1,'hs':self.heroes},self.catalogs,
            'embedded:one',self.abilities,lambda:'building-native')
        self.assertTrue(changed)
        self.assertEqual(notices[-1][1]['ev'],[111])
        self.assertNotIn(111,done['completed_events'])


    def test_original_building_slot_snapshot_supports_initial_native_city_ui(self):
        area=self.state['story']['city_areas']['1']
        snapshot=city_action_area_snapshot(area,self.catalogs['development'])
        self.assertEqual(snapshot['mbn'],4)
        self.assertNotIn('mbn',area)
        snapshot['lv']=5
        self.assertEqual(city_action_area_snapshot(snapshot,self.catalogs['development'])['mbn'],8)


    def test_original_gender_both_is4_and_neither_is3(self):
        self.assertEqual(hashlib.sha256((ROOT/'analysis/android640-scripts/com/const.marshal').read_bytes()).hexdigest(),self.fixture['const_sha256'])
        self.assertEqual(self.fixture['gender_values']['BOTH'],4)
        area=self.state['story']['city_areas']['1']
        area['bd']={'1':{'id':23,'uuid':'male'},'2':{'id':24,'uuid':'female'}}
        self.catalogs['hero'][8]['gender']=4
        self.catalogs['hero'][7]['gender']=3
        entered,_,_,_=self.act('enterPatrolRequest',{'aid':1,'hs':self.heroes})
        claimed,_,_,_=self.act('patrolReward',{},entered)
        self.assertEqual(claimed['profile']['heroes']['8']['ef'],6)
        self.assertEqual(claimed['profile']['heroes']['7']['ef'],4)


    def test_safe_original_numeric_sets_need_no_ast_or_table_execution(self):
        self.assertNotIn('import ast',(ROOT/'runtime/offline_city_actions.py').read_text())
        self.catalogs['triggers']={111:{'release':1,'conds':{3:"set([__import__('os').system('bad')])"}}}
        self.catalogs['content']={111:{'release':1,'autoStart':True}}
        done,notices,changed,diagnostic=self.act('enterPatrolRequest',{'aid':1,'hs':self.heroes})
        self.assertFalse(changed)
        self.assertFalse(notices)
        self.assertIn('pending',diagnostic)
        self.assertEqual(done,self.state)


if __name__=='__main__': unittest.main()
