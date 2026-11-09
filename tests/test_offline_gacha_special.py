import copy
from pathlib import Path
import sys
import unittest
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'runtime'),str(ROOT/'tools'),str(ROOT/'analysis/research-agent')]
from read_literal_marshal import read
from offline_gacha_special import *
from offline_gacha_gateway import migrate_gateway_gacha_state

class SpecialGachaTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        names=('chouka_info','hero','hero_self_choose_info','item_data','chouka_wish_treasure_choose','item_store_wish_change','chouka_treasure_wish','activity_config','activity_template')
        cls.tables={n:read(ROOT/'analysis/android640-scripts/com/data/cdata'/(n+'.marshal'))for n in names}
    def setUp(self):
        self.state=migrate_gateway_gacha_state({'profile':{'economy':{'yuanbao':1000}}})
    def heroes(self):
        available=[h for h,r in self.tables['hero_self_choose_info'].items()if r.get('avaliable')]
        return [next(h for h in available if self.tables['hero'][h]['hero_composite_init_rank']==rank)for rank in (4,3)]
    def test_all_six_original_choices_and_all_42_virtual_leaves(self):
        count=0
        for wire in SELF_CHOOSE_POOLS:
            original=copy.deepcopy(self.state)
            state,notices,changed,diag=prepare_special_gacha_operation(original,'setChooseHeroes',{'t':wire,'h':self.heroes()},self.tables,'choice-'+str(wire),{'archive_wire_t':wire})
            self.assertTrue(diag['success'],diag);self.assertTrue(changed)
            self.assertEqual(original,self.state)
            self.assertEqual(notices[0][0],'replySetChooseHeroes')
            context=special_pool_context(state,wire)
            for iid,row in self.tables['item_data'].items():
                subtype=row.get('virtual_sub_type',row.get('subtype'))
                if row.get('card_pool')==wire and subtype in range(61,68):
                    result=resolve_self_choose_item(self.tables,wire,iid,1,context)
                    self.assertEqual(result[0][0],self.heroes()[0 if subtype in (61,63,64,65)else 1]);count+=1
            replay=prepare_special_gacha_operation(state,'setChooseHeroes',{'t':wire,'h':self.heroes()},self.tables,'choice-'+str(wire),{'archive_wire_t':wire})
            self.assertFalse(replay[2]);self.assertTrue(replay[3]['replay'])
            self.assertEqual(replay[0],state)
        self.assertEqual(count,42)
    def test_actual_weighted_virtual_leaf_converts_without_raw_item(self):
        from offline_gacha_rewards import make_original_gacha_resolver
        names=('reward_common','reward_random','chouka_normal','chouka_default')
        tables=dict(self.tables,**{n:read(ROOT/'analysis/android640-scripts/com/data/cdata'/(n+'.marshal'))for n in names})
        state,unused,changed,diag=prepare_special_gacha_operation(self.state,'setChooseHeroes',{'t':265,'h':self.heroes()},tables,'choose',{'archive_wire_t':265})
        context=special_pool_context(state,265)
        weighted=tables['reward_random'][13760]['weights']
        boundary=0
        for rid,weight in weighted:
            if rid==52792:break
            boundary+=weight
        totals=[]
        def draw(total):totals.append(total);return boundary
        resolver=make_original_gacha_resolver(dict(tables,chouka_default={(265,999999):{'pool':13760}}),draw,lambda *a:None,
            lambda hid,piece:{'hero':[hid],'hero_file':piece,'get_hero':True},lambda t,n:context)
        card=resolver(265,999999)
        self.assertEqual(card['hero'],[self.heroes()[0]])
        self.assertFalse(card.get('item'));self.assertEqual(card['_gacha_source']['self_choose_items'],[[2062,1]])
        self.assertEqual(totals,[sum(weight for rid,weight in weighted)])
    def test_explicit_original_rotation_candidates_verified_not_trusted(self):
        rows=[(k,r)for k,r in self.tables['activity_config'].items()if self.tables['activity_template'].get(r.get('tmp_id'),{}).get('tmp_type')==88 and r.get('self_choose_S')and r.get('self_choose_A')]
        self.assertEqual(len(rows),21)
        for uaid,row in rows:
            context={'archive_wire_t':265,'self_choose_wire':265,'rotation_uaid':uaid,'rotation':copy.deepcopy(row),'rotation_policy':'offline-archive-candidate-period-v1'}
            args={'t':265,'h':[row['self_choose_S'][0],row['self_choose_A'][0]]}
            state,unused,changed,diag=prepare_special_gacha_operation(self.state,'setChooseHeroes',args,self.tables,'row-'+str(uaid),context)
            self.assertTrue(diag['success'],diag)
            context['rotation']['self_choose_S']=[999999]
            failed=prepare_special_gacha_operation(self.state,'setChooseHeroes',args,self.tables,'bad',context)
            self.assertFalse(failed[3]['success']);self.assertEqual(failed[0],self.state)
    def test_disabled_pool_is_unchanged(self):
        for op,args in [('setChooseHeroes',{'t':354,'h':[]}),('setChooseTreasure',{'t':354,'i':1})]:
            state,notices,changed,diag=prepare_special_gacha_operation(self.state,op,args,self.tables,'disabled',{})
            self.assertEqual(state,self.state);self.assertFalse(changed);self.assertFalse(diag['success']);self.assertNotEqual(notices[0][1]['r'],0)
    def test_missing_choice_never_grants_virtual_inventory(self):
        with self.assertRaises(ValueError):resolve_self_choose_item(self.tables,265,2062,1,{})
    def test_treasure_original_paid_and_explicit_free_policy_replay(self):
        wish=next(k for k,r in self.tables['chouka_treasure_wish'].items()if r.get('drawType')==5)
        iid=next(k for k,r in self.tables['chouka_wish_treasure_choose'].items()if r.get('can_choose') and k!=self.tables['chouka_treasure_wish'][wish].get('treasure_id'))
        for policy in (None,FREE_TREASURE_WISH_POLICY):
            context={'archive_wire_t':5,'wish_id':wish,'choice_cost_policy':policy}
            state,notices,changed,diag=prepare_special_gacha_operation(self.state,'setChooseTreasure',{'t':5,'i':iid},self.tables,'target',context)
            self.assertTrue(diag['success'],diag)
            self.assertEqual(state['profile']['economy']['yuanbao'],1000-diag['effective_cost'])
            replay=prepare_special_gacha_operation(state,'setChooseTreasure',{'t':5,'i':iid},self.tables,'target',context)
            self.assertEqual(state,replay[0]);self.assertFalse(replay[2])
    def test_treasure_period_switch_preserves_old_choice_count(self):
        wishes=[k for k,r in self.tables['chouka_treasure_wish'].items()if r.get('drawType')==5][:2]
        self.assertEqual(len(wishes),2)
        state=self.state
        items=[k for k,r in self.tables['chouka_wish_treasure_choose'].items()if r.get('can_choose')]
        for index,wish in enumerate(wishes+[wishes[0]]):
            old=(state['gacha_pools'].get('special',{}).get('pools',{}).get('5',{}).get('ctr_by_wish',{}).get(str(wish)) or [0,0,0])
            item=next(i for i in items if i not in (old[1],self.tables['chouka_treasure_wish'][wish].get('treasure_id')))
            state,unused,changed,diag=prepare_special_gacha_operation(state,'setChooseTreasure',{'t':5,'i':item},self.tables,'change-'+str(index),{'archive_wire_t':5,'wish_id':wish,'choice_cost_policy':FREE_TREASURE_WISH_POLICY})
            self.assertTrue(diag['success'],diag)
        row=state['gacha_pools']['special']['pools']['5']
        self.assertEqual(row['ctr_by_wish'][str(wishes[0])][2],2)
        self.assertEqual(row['ctr_by_wish'][str(wishes[1])][2],1)
        before=copy.deepcopy(state)
        for wish in wishes:
            projected=project_special_gacha_snapshot(state,{'ad':[]},{'wire_t':5,'wish_id':wish})
            self.assertEqual(dict(projected['ad'])[5]['ctr'],row['ctr_by_wish'][str(wish)])
        self.assertEqual(state,before)
    def test_wish_display_formula_and_offline_hit_reset_are_distinct_policy(self):
        tables=dict(self.tables,reward_common=read(ROOT/'analysis/android640-scripts/com/data/cdata/reward_common.marshal'))
        wish=129
        for before,expected in ((0,.02),(5,.02),(6,.03),(12,.04),(600,1)):
            state=copy.deepcopy(self.state)
            state['gacha_pools']['special']={'version':1,'policy':SPECIAL_GACHA_POLICY,'receipts':[],'pools':{'5':{'tw':{'129':before}}}}
            context,notice=prepare_treasure_wish_reveal(state['gacha_pools'],tables,5,wish,lambda total:total-1)
            source=context['treasure_wish_source']
            self.assertAlmostEqual(source['display_probability'],expected)
            self.assertEqual(source['probability_evidence'],'original-client-display-formula-only')
            self.assertEqual(source['step_after'],0 if expected==1 else before+1)
        state=copy.deepcopy(self.state)
        context,notice=prepare_treasure_wish_reveal(state['gacha_pools'],tables,5,wish,lambda total:0)
        self.assertEqual(context['special_common_reward_ids'],list(tables['chouka_treasure_wish'][wish]['reward']))
        self.assertEqual(context['treasure_wish_source']['branch'],'wish-replacement')
        self.assertEqual(notice,('syncTreasureWishInfo',{'t':5,'tw_id':129,'s':0}))
    def test_unpinned_wish_and_active_group_refused(self):
        state=copy.deepcopy(self.state);state['gacha_pools']['pools']['265']={'group':{'cards':[]}}
        result=prepare_special_gacha_operation(state,'setChooseHeroes',{'t':265,'h':self.heroes()},self.tables,'x',{'archive_wire_t':265})
        self.assertEqual(result[0],state);self.assertFalse(result[3]['success'])

if __name__=='__main__':unittest.main()
