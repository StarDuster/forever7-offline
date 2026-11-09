import copy
from pathlib import Path
import sys
import unittest
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'runtime'),str(ROOT/'tools'),str(ROOT/'analysis/research-agent')]
from read_data_table import read
from read_literal_marshal import read as read_marshal
from offline_event_battle import (prepare_event_battle_gate,event_battle_snapshot,
    prepare_event_battle_admission,prepare_event_battle_finish,validate_event_battle_state)

class EventBattleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.content=read(ROOT/'analysis/decompiled/event_content.py')
        cls.missions=read_marshal(ROOT/'analysis/android640-scripts/com/data/cdata/mission.marshal')
    def setUp(self):
        self.state={'processing_events':[1],'completed_events':[],
            'story':{'week':0,'city_values':{'av':24,'fv':5},'battle_wins':[]},
            'profile':{'heroes':{'24':{'cf':100,'ef':0,'cs':'old','sk':{'old':{'i':24}},'ti':{'items':[]}}},
                       'economy':{'version':1,'level':1,'money':0,'exp':0}},
            'battle':{'version':1,'active':None,'receipts':[]}}
        self.arguments={'t':2,'s':104,'h':[24],'d':{}}
    def gate(self,state=None,key='0:0:1:1'):
        return prepare_event_battle_gate(state or self.state,1,self.content,key)[0]
    def admit(self,state=None,fid='actual-fight-1'):
        return prepare_event_battle_admission(state or self.gate(),self.arguments,
            self.missions,self.content,lambda:fid)[0]
    def result(self,win=1):return dict(self.arguments,x=[],w=win,e=123)
    def settle(self,active,result):
        profile=copy.deepcopy(self.current_profile)
        reward={};notices=[]
        if result['w']:
            profile['economy']['money']+=5;reward={'money':5}
        reply={k:copy.deepcopy(result[k]) for k in ('t','s','h','x','w')};reply['r']=reward
        return reply,{'profile':profile,'notices':notices,'granted':[]}
    def finish(self,state,win=1,fid='actual-fight-1'):
        self.current_profile=state['profile']
        return prepare_event_battle_finish(state,self.result(win),self.settle,fid)
    def test_real_event_gate_native_snapshot_restores_only_processing_occurrence(self):
        p,notices,changed=prepare_event_battle_gate(self.state,1,self.content,'0:0:1:1')
        self.assertTrue(changed);self.assertEqual(event_battle_snapshot(p),{'ab':[[104,1]]})
        self.assertEqual(notices,[('setEventBattleStage',{'s':104,'n':1})])
        q,_,changed=prepare_event_battle_gate(p,1,self.content,'0:0:1:1')
        self.assertFalse(changed);self.assertEqual(q,p)
        bad=copy.deepcopy(self.state);bad['processing_events']=[]
        with self.assertRaises(ValueError):prepare_event_battle_gate(bad,1,self.content,'x')
    def test_original_default_heroes_and_wire_event_admission(self):
        p=self.admit();active=p['battle']['active']
        self.assertEqual(active['request']['t'],2);self.assertEqual(active['event_id'],1)
        self.assertEqual(active['request']['d'],{});self.assertEqual(active['hero_level'],1)
        self.assertEqual(active['heroes']['24'],self.state['profile']['heroes']['24'])
        validate_event_battle_state(p['battle'])
        q,changed=prepare_event_battle_admission(p,self.arguments,self.missions,self.content,lambda:'unused')
        self.assertFalse(changed);self.assertEqual(q,p)
    def test_no_gate_or_historical_win_cannot_admit_new_occurrence(self):
        self.state['story']['battle_wins']=[104]
        with self.assertRaises(ValueError):self.admit(self.state)
    def test_default_party_and_unsupported_mode_are_explicit_errors(self):
        p=self.gate();wrong=dict(self.arguments,h=[7]);p['profile']['heroes']['7']=copy.deepcopy(p['profile']['heroes']['24'])
        with self.assertRaises(ValueError):prepare_event_battle_admission(p,wrong,self.missions,self.content,lambda:'a')
        missions=copy.deepcopy(self.missions);missions[104]['system_type']=4
        with self.assertRaisesRegex(ValueError,'mode'):prepare_event_battle_admission(p,self.arguments,missions,self.content,lambda:'b')
        with self.assertRaisesRegex(ValueError,'wire'):prepare_event_battle_admission(p,dict(self.arguments,t=4),self.missions,self.content,lambda:'c')
    def test_original_cine_default_party_cannot_bypass_native_ban_filter(self):
        self.state['story']['banned_heroes']={'24':200}
        with self.assertRaisesRegex(ValueError,'ordered available'):
            self.admit()
        self.assertEqual(self.state['story']['banned_heroes'],{'24':200})
    def test_original_scene500_forced_trial_party_exceeds_max_but_is_exact(self):
        self.assertEqual(self.missions[500]['max_hero_num'],1)
        self.assertEqual(self.missions[500]['defaultHeroes'],(109,113))
        self.state['processing_events']=[8805]
        for h in (109,113):self.state['profile']['heroes'][str(h)]=copy.deepcopy(self.state['profile']['heroes']['24'])
        self.state['story']['banned_heroes']={}
        p,_,_=prepare_event_battle_gate(self.state,8805,self.content,'0:8805:1')
        q,_=prepare_event_battle_admission(p,{'t':2,'s':500,'h':[109,113],'d':{}},self.missions,self.content,lambda:'scene500')
        self.assertEqual(q['battle']['active']['request']['h'],[109,113])
        self.assertEqual(q['story']['banned_heroes'],self.state['story']['banned_heroes'])
    def test_self_selected_party_still_rejects_banned_and_maximum_violations(self):
        self.state['processing_events']=[900]
        content={900:{'release':True,'enterBattle':120}}
        p,_,_=prepare_event_battle_gate(self.state,900,content,'free-team')
        p['story']['banned_heroes']={'24':200}
        with self.assertRaisesRegex(ValueError,'Self-selected'):
            prepare_event_battle_admission(p,dict(self.arguments,s=120),self.missions,content,lambda:'free')
        p['story']['banned_heroes']={}
        for h in (7,8,9):p['profile']['heroes'][str(h)]=copy.deepcopy(p['profile']['heroes']['24'])
        with self.assertRaisesRegex(ValueError,'maximum'):
            prepare_event_battle_admission(p,dict(self.arguments,s=120,h=[24,7,8,9]),self.missions,content,lambda:'large')
    def test_snapshot_excludes_cancelled_processing_event_gates(self):
        p=self.gate();p['processing_events']=[]
        self.assertEqual(event_battle_snapshot(p),{'ab':[]})
    def test_actual_win_binds_one_event_occurrence_without_faking_completed_or_free_city(self):
        p=self.admit();q,reply,effects,changed=self.finish(p)
        self.assertTrue(changed);self.assertEqual(reply['w'],1)
        self.assertEqual(q['completed_events'],[]);self.assertEqual(q['story']['battle_wins'],[104])
        self.assertEqual(effects['event_completion'],{'event':1,'occurrence':'0:0:1:1',
            'fight_id':'actual-fight-1','scene':104,'token':'battle:104'})
        self.assertEqual(event_battle_snapshot(q),{'ab':[]})
        self.assertNotIn('city_areas',q['story'])
        self.assertEqual(p['profile']['economy']['money'],0)
    def test_loss_reopens_gate_without_rewards_then_retry_uses_fresh_fight(self):
        p=self.admit();q,reply,effects,changed=self.finish(p,0)
        self.assertEqual(q['profile'],self.state['profile']);self.assertFalse(reply['r'])
        self.assertIsNone(effects['event_completion']);self.assertEqual(event_battle_snapshot(q),{'ab':[[104,1]]})
        self.assertEqual(q['story']['battle_wins'],[])
        r=self.admit(q,'actual-retry-2');self.assertEqual(r['battle']['active']['fight_id'],'actual-retry-2')
    def test_identical_duplicate_finish_is_idempotent_only_for_same_source_fight(self):
        p=self.admit();q,reply,effects,changed=self.finish(p)
        r,same,effects,changed=self.finish(q)
        self.assertFalse(changed);self.assertEqual(q,r);self.assertEqual(reply,same)
        with self.assertRaises(ValueError):self.finish(q,fid='different-source')
    def test_stale_identical_result_cannot_settle_a_fresh_repeated_event(self):
        p=self.admit();q,_,_,_=self.finish(p)
        r=self.gate(q,key='0:1:1:2');s=self.admit(r,'fresh-occurrence-fight')
        with self.assertRaises(ValueError):self.finish(s,fid='actual-fight-1')
        self.assertEqual(s['profile']['economy']['money'],5)
        self.assertNotIn('0:1:1:2',s['story'].get('event_battle_wins',{}))
    def test_settlement_must_not_convert_loss_to_win_or_award_on_loss(self):
        p=self.admit();before=copy.deepcopy(p)
        def forged(active,result):
            reply={k:result[k] for k in ('t','s','h','x','w')};reply['w']=1;reply['r']={}
            return reply,{'profile':p['profile']}
        with self.assertRaises(ValueError):prepare_event_battle_finish(p,self.result(0),forged,'actual-fight-1')
        self.assertEqual(p,before)
    def test_story_abandoned_scene_and_cancelled_occurrence_cannot_be_admitted_or_settled(self):
        p=self.gate();p['story']['abandoned_missions']=[104]
        with self.assertRaisesRegex(ValueError,'abandoned'):self.admit(p)
        p=self.admit();p['processing_events']=[]
        with self.assertRaises(ValueError):self.finish(p)
    def test_active_request_cannot_be_reused_for_another_same_scene_occurrence(self):
        p=self.admit();p['story']['event_battle_cursor']='0:1:1:2'
        with self.assertRaisesRegex(ValueError,'occurrence'):self.admit(p)
    def test_embedded_module_needs_no_offline_imports(self):
        ns={};exec(compile((ROOT/'runtime/offline_event_battle.py').read_text(),'<embedded-event-battle>','exec'),ns)
        p,_,_=ns['prepare_event_battle_gate'](self.state,1,self.content,'x')
        self.assertEqual(ns['event_battle_snapshot'](p),{'ab':[[104,1]]})

if __name__=='__main__':unittest.main()
