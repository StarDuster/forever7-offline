"""Actual original ROLE rows with modeled admissions/results; no native fights."""
import ast
import builtins
import copy
import json
from pathlib import Path
import sys
import unittest
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'runtime'),str(ROOT/'tools'),str(ROOT/'analysis/research-agent')]
from read_literal_marshal import read
import offline_role_mission as role
import offline_event_battle as event
from offline_battle import settle_stage_economy
from offline_battle_terminal import resolve_winning_party_fatigue
from read_data_table import read as read_events
from test_special_city_stage import NativeTaggedLiteral, tagged_literals, DuplicateTaggedLiteral


def original_role_tables():
    path=ROOT/'analysis/android640-scripts/com/data/cdata'
    names=('mission','mission_hero_attr','hero','hero_star_attr','hero_star_skill','hero_artifact_attr',
        'hero_artifact_allot_lv_point_data','hero_treasure_generate','hero_treasure','item_data','skin',
        'liberate_tupo','liberate_lv','treasure_exclusive','hero_treasure_suit','skill','trick_data','monster','hero_treasure_third_attr')
    tables={name:read(path/(name+'.marshal')) for name in names}
    for scene in (315,316,426,427,428):
        source=tables['mission'][scene]['dataSource']
        for prefix in ('refresh_hero_','refresh_monster_'):
            tables[prefix+source]=read(path/(prefix+source+'.marshal'))
    return tables


class RoleMissionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tables=original_role_tables()
        cls.events=read_events(ROOT/'analysis/decompiled/event_content.py')
        cls.api=dict(vars(role),**{key:value for key,value in vars(event).items() if not key.startswith('_')})

    def setUp(self):
        self.state={'story':{'week':1,'route':'10','city_values':{'av':24,'fv':0},'battle_wins':[],
            'event_occurrences':{},'banned_heroes':{'10':200,'14':200}},'day':{'stock_day':2},
            'processing_events':[],'completed_events':[],'available_events':[], 'event_traces':[],
            'profile':{'heroes':{'10':{'cf':3,'ef':17,'cs':'owned-special','ti':{'items':[{'u':'permanent'}]},'awake':4},
                                '14':{'cf':7,'ef':23,'skin':'owned'}},
                'economy':{'version':1,'level':1,'exp':0,'money':0},'treasures':{'version':1,'items':[]}},
            'battle':{'version':1,'active':None,'receipts':[]}}
        self.fight=0

    def gate(self,scene=315):
        eid=next(eid for eid,row in self.events.items() if row.get('enterBattle')==scene and row.get('release'))
        self.state['processing_events']=[eid]
        self.state['story']['event_occurrences'][str(eid)]=1
        self.state=self.api['prepare_event_battle_gate'](self.state,eid,self.events,'1:%s:1'%eid)[0]
        return eid

    def admit(self,scene=315):
        self.fight+=1
        args={'t':2,'s':scene,'h':list(self.tables['mission'][scene]['defaultHeroes']),'d':{}}
        self.state=self.api['prepare_event_battle_admission'](self.state,args,self.tables['mission'],self.events,
            lambda:'actual-host-fight-%s'%self.fight,role_tables=self.tables,role_owner='actual-host-owner')[0]
        return self.state['battle']['active']

    def finish(self,win=0):
        active=self.state['battle']['active'];scene=active['request']['s']
        result=dict(active['request'],w=win,x=[],e={});result.pop('d')
        def settle(admission,actual):
            return settle_stage_economy(self.state['profile'],admission,actual,
                {1:{'money':7,'exp':3,'friendly':9}}, {1:{'lv_exp':100}}, {},{},lambda *args:None,self.tables['mission'][scene])
        self.state,reply,effects,changed=self.api['prepare_event_battle_finish'](self.state,result,settle,active['fight_id'],self.tables['mission'],self.events)
        return reply,effects,changed,result,active['fight_id']

    def test_all_five_actual_original_snapshots_fixed_party_equipment_and_monster_levels(self):
        for scene in (315,316,426,427,428):
            team=list(self.tables['mission'][scene]['defaultHeroes'])
            descriptor=self.api['compile_role_mission'](scene,team,self.tables)
            self.api['validate_role_descriptor'](json.loads(json.dumps(descriptor)))
            actor=descriptor['actors'][str(team[0])]
            self.assertEqual(actor['fixed']['level'],60 if scene<400 else 100)
            self.assertEqual(len(actor['equipment']),0 if scene<400 else 15)
            self.assertEqual(len({item['template']['u'] for item in actor['equipment']}),len(actor['equipment']))
            self.assertTrue(all(row.get('level',1)==1 for row in descriptor['references']['monsters'].values()))
            self.assertEqual(descriptor['total_attempts'],3)
            if scene>400:
                self.assertEqual(sum(self.tables['hero_treasure'][(item['template']['i'],item['template']['tr']['cl'])]['cost'] for item in actor['equipment']),42)
                self.assertEqual(actor['fixed']['artifact']['attrs']['_base_max_hp'],45)
                self.assertEqual(actor['fixed']['artifact']['attrs']['_base_phy_att_str'],180)

    def test_trial_admission_unowned_and_banned_does_not_touch_permanent_profile(self):
        self.gate(426);self.state['profile']['heroes']={}
        before=copy.deepcopy(self.state['profile']);active=self.admit(426)
        self.assertEqual(active['party_kind'],'trial');self.assertEqual(active['request']['h'],[10])
        self.assertEqual(active['hero_level'],100);self.assertEqual(active['reward_level'],1)
        self.assertEqual(active['monster_level'],1);self.assertEqual(self.state['profile'],before)
        self.assertEqual(self.api['event_battle_snapshot'](self.state),{'ab':[[426,3]]})
        self.api['validate_role_missions'](self.state)

    def test_complete_snapshot_required_not_global_mode4_bypass(self):
        for mutate in ('missing-row','extra-party','nonzero-cost','missing-template','wrong-position','missing-spawn','wrong-fixed-class'):
            tables=copy.deepcopy(self.tables);team=[10]
            if mutate=='missing-row':tables['mission_hero_attr'].pop((426,10))
            if mutate=='extra-party':team=[10,14]
            if mutate=='nonzero-cost':tables['mission'][426]['fatigue']=1
            if mutate=='missing-template':tables['hero_treasure_generate'][18038].pop('dumps_info')
            if mutate=='wrong-fixed-class':
                fixed=json.loads(tables['hero_treasure_generate'][18038]['dumps_info']);fixed['tr']['cl']=1
                tables['hero_treasure_generate'][18038]['dumps_info']=json.dumps(fixed)
            if mutate=='wrong-position':tables['mission_hero_attr'][(426,10)]['pos_id']=2
            if mutate=='missing-spawn':tables.pop('refresh_monster_jdtushuguan1')
            with self.subTest(mutate=mutate),self.assertRaises(ValueError):
                self.api['compile_role_mission'](426,team,tables)

    def test_three_total_attempts_debit_only_real_losses_and_exact_duplicates(self):
        self.gate();eid=self.state['processing_events'][0]
        for remaining in (2,1,0):
            self.admit();reply,effects,changed,result,fight=self.finish()
            self.assertEqual(reply['w'],0);self.assertFalse(reply['r']);self.assertNotIn(315,self.state['story']['battle_wins'])
            gate=self.state['story']['event_battle_gates']['1:%s:1'%eid]
            self.assertEqual(gate['role_episode']['remaining'],remaining)
            self.assertEqual(gate['status'],'open' if remaining else 'terminal-loss')
            replay=self.api['prepare_event_battle_finish'](self.state,result,lambda *_:self.fail('duplicate settlement'),fight,self.tables['mission'],self.events)
            self.assertFalse(replay[3]);self.assertEqual(replay[0],self.state)
            if remaining:self.assertIn(eid,self.state['processing_events']);self.assertNotIn(7146,dict(self.state['available_events']))
        self.assertIn(7146,dict(self.state['available_events']));self.assertNotIn(eid,self.state['completed_events'])

    def test_giveup_requires_latest_unconsumed_real_loss_and_exact_epoch_source(self):
        self.gate();before=copy.deepcopy(self.state)
        with self.assertRaises(ValueError):self.api['prepare_role_giveup'](self.state,315,self.api['role_battle_source'](self.state),self.tables['mission'],self.events)
        self.assertEqual(self.state,before)
        self.admit();self.finish();source=self.api['role_battle_source'](self.state)
        bad=dict(source,epoch=source['epoch']+1)
        with self.assertRaises(ValueError):self.api['prepare_role_giveup'](self.state,315,bad,self.tables['mission'],self.events)
        self.state,notices=self.api['prepare_role_giveup'](self.state,315,source,self.tables['mission'],self.events)
        self.assertIn(7146,dict(self.state['available_events']));self.assertIn(('setEventBattleStage',{'s':315,'n':0}),notices)
        with self.assertRaises(ValueError):self.api['prepare_role_giveup'](self.state,315,self.api['role_battle_source'](self.state),self.tables['mission'],self.events)

    def test_no_failure_branch_pauses_without_completion_rearm_is_new_episode(self):
        eid=self.gate(426)
        for unused in range(3):self.admit(426);self.finish()
        source=self.api['role_battle_source'](self.state);before=copy.deepcopy(self.state)
        gate=self.state['story']['event_battle_gates'][source['occurrence']]
        self.assertEqual(gate['status'],'paused');self.assertIn(eid,self.state['processing_events'])
        self.assertNotIn(eid,self.state['completed_events']);self.assertEqual(self.state['available_events'],[])
        with self.assertRaises(ValueError):self.admit(426)
        self.assertEqual(self.state,before)
        self.state=self.api['prepare_role_rearm'](self.state,source)
        self.assertEqual(self.state['story']['event_battle_gates'][source['occurrence']]['role_episode']['epoch'],2)
        with self.assertRaises(ValueError):self.api['prepare_role_rearm'](self.state,source)
        self.assertEqual(self.admit(426)['role_epoch'],2)

    def test_win_rewards_player_only_preserves_owned_hero_and_marks_trial_provenance(self):
        self.gate();before=copy.deepcopy(self.state['profile']['heroes']);self.admit()
        reply,effects,_,_,_=self.finish(1)
        self.assertEqual(reply['r']['money'],7);self.assertEqual(self.state['profile']['heroes'],before)
        self.assertFalse(any(name in ('updateFriendlyValue','updateCurFatigueValue') for name,_ in effects['notices']))
        self.assertEqual(self.state['battle']['receipts'][-1]['party_kind'],'trial')
        won=next(iter(self.state['story']['event_battle_wins'].values()))
        self.assertEqual(won['party_kind'],'trial');self.assertEqual(won['winning_terminal_provenance']['party_kind'],'trial')
        self.assertFalse(self.state['story'].get('event_terminal_offers'))
        self.assertNotIn(7144,self.state['completed_events'])

    def test_native_readonly_mapping_utf8_and_lossless_float_json_snapshot(self):
        tables={name:NativeTaggedLiteral({key:tagged_literals(value,True) for key,value in rows.items()}) for name,rows in self.tables.items()}
        descriptor=self.api['compile_role_mission'](426,[10],tables)
        canonical=self.api['compile_role_mission'](426,[10],self.tables)
        self.assertEqual(descriptor,canonical)
        restored=json.loads(json.dumps(descriptor));self.assertEqual(restored,descriptor)
        self.api['validate_role_descriptor'](restored)
        self.assertIn('__role_float__',json.dumps(restored))
        literal=self.api['_rm_literal'] if '_rm_literal' in self.api else role._rm_literal
        with self.assertRaises(ValueError):literal(DuplicateTaggedLiteral([(b'x',1),('x',2)]))
        with self.assertRaises(ValueError):literal({'x':object()})
        with self.assertRaises(ValueError):literal({'x':float('nan')})
        with self.assertRaises(UnicodeError):literal({b'x':b'\xff'})
        alias={'x':1};self.assertEqual(literal([alias,alias]),[{'x':1},{'x':1}])

    def test_pinned_catalog_corruption_and_week_drift_rejected(self):
        self.gate();self.admit();restored=json.loads(json.dumps(self.state));self.api['validate_role_missions'](restored)
        restored['battle']['active']['role_mission']['actors']['14']['fixed']['level']=100
        with self.assertRaises(ValueError):self.api['validate_role_missions'](restored)
        self.state['story']['week']=2
        with self.assertRaises(ValueError):self.api['validate_role_missions'](self.state)

    def test_trial_owned_ids_never_authorize_selector0_and_proof_survives_receipt_pruning(self):
        self.gate();self.admit();self.finish(1)
        before=copy.deepcopy(self.state['profile'])
        self.state['story'].setdefault('available_origins',{})['7145']={'source':'accepted_mission_result',
            'fight_id':self.state['battle']['receipts'][-1]['fight_id'],'scene':315,'outcome':1,'party_kind':'trial'}
        with self.assertRaisesRegex(ValueError,'trial-party'):
            resolve_winning_party_fatigue(self.state,self.events,{'mission':self.tables['mission']},7145,'1:7145:1',114,100)
        self.assertEqual(self.state['profile'],before)
        self.state['battle']['receipts']=[]
        self.api['validate_role_missions'](self.state)
        won=next(iter(self.state['story']['event_battle_wins'].values()))
        self.assertEqual(won['party'],[14]);self.assertEqual(won['provider'],role.ROLE_MISSION_POLICY)
        self.assertEqual(won['party_kind'],'trial');self.assertTrue(won['catalog_token'])
        with self.assertRaises(ValueError):
            resolve_winning_party_fatigue(self.state,self.events,{'mission':self.tables['mission']},7145,'1:7145:1',114,100)
        self.assertEqual(self.state['profile'],before)

    def test_legacy_untyped_active_and_changed_mission_result_fail_closed(self):
        self.gate();self.admit();before=copy.deepcopy(self.state)
        legacy=copy.deepcopy(self.state);legacy['battle']['active']['party_kind']='owned'
        legacy['battle']['active']['heroes']={'14':copy.deepcopy(legacy['profile']['heroes']['14'])}
        next(iter(legacy['story']['event_battle_gates'].values())).pop('role_episode')
        with self.assertRaisesRegex(ValueError,'Legacy untyped'):
            self.api['prepare_event_battle_admission'](legacy,{'t':2,'s':315,'h':[14],'d':{}},self.tables['mission'],self.events,lambda:'unused',role_tables=self.tables,role_owner='actual-host-owner')
        changed=dict(self.tables['mission']);changed[315]=dict(changed[315],retry_times=4)
        active=self.state['battle']['active'];result={'t':2,'s':315,'h':[14],'x':[],'w':0,'e':{}}
        with self.assertRaisesRegex(ValueError,'mission changed'):
            self.api['prepare_event_battle_finish'](self.state,result,lambda *_:self.fail('changed mission must reject before settlement'),active['fight_id'],changed,self.events)
        self.assertEqual(self.state,before)


class RoleMissionFlatTests(RoleMissionTests):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        from patch_bootstrap import embedded_loader
        source=ast.literal_eval(ast.parse(embedded_loader(ROOT/'runtime').splitlines()[0]).body[0].value)
        native_import=builtins.__import__
        def block(name,*args,**kwargs):
            if name.startswith('offline_'):raise ImportError('Actual flat runtime')
            return native_import(name,*args,**kwargs)
        cls.api={'__name__':'actual_flat_role','__builtins__':dict(vars(builtins),__import__=block)}
        exec(compile(source,'<actual-flat-role>','exec'),cls.api,cls.api)


if __name__=='__main__':unittest.main()
