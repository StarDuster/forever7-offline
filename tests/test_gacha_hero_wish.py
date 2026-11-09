"""Original hero-wish formula body and bounded accepted-reveal transitions."""
import builtins
import copy
from pathlib import Path
import sys
import textwrap
from types import SimpleNamespace,MethodType
import unittest
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'runtime'),str(ROOT/'analysis/research-agent'),str(ROOT/'tools')]
import test_offline_gacha_rewards as base
from read_literal_marshal import read
from offline_gacha_special import (HERO_WISH_WIRES,HERO_WISH_PERIOD_POLICY,prepare_hero_wish_reveal,
    finalize_hero_wish_reveal,hero_wish_probabilities,hero_wish_eligibility_view,
    hero_wish_period_for_group,project_special_gacha_snapshot,prepare_special_gacha_operation)
from offline_gacha_rewards import make_original_gacha_resolver,make_table_hero_result

class HeroWishTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        base.OriginalGachaRewardTests.setUpClass();cls.tables=dict(base.OriginalGachaRewardTests.tables)
        cls.tables['chouka_treasure_wish']=read(ROOT/'analysis/android640-scripts/com/data/cdata/chouka_treasure_wish.marshal')
        cls.body=(ROOT/'analysis/research-agent/LuckyDrawData.py').read_text()
    def rows(self,wire):return sorted((r for r in self.tables['chouka_treasure_wish'].values()if r.get('drawType')==wire and r.get('wish_type')==2),key=lambda r:r['id'])
    def pinned(self,wire):return {'hero_wish_policy':HERO_WISH_PERIOD_POLICY,'hero_wish_ids':[r['id']for r in self.rows(wire)]}
    def original_probabilities(self,wire,wi,return_object=False):
        # Compile the unchanged original method bodies, with Python2 list-filter
        # semantics supplied at the host boundary; no reimplementation of formula.
        namespace={'CHOUKA_TREASURE_WISH':SimpleNamespace(data=self.tables['chouka_treasure_wish']),
            'filter':lambda fn,seq:list(builtins.filter(fn,seq))}
        obj=SimpleNamespace(getWishGroupInfoListsByDrawType=lambda t:{gid:[r['id']for r in self.rows(t)if r['gid']==gid]for gid in set(r['gid']for r in self.rows(t))},
            getWishGroupInfoDict=lambda t,gid:wi.get(str(gid),{}))
        for name in ('getWishGroupListTotalFixedRate','getWishGroupProbDicts'):
            start=self.body.index('    def '+name+'(');end=self.body.find('\n    def ',start+5)
            source=textwrap.dedent(self.body[start:end if end!=-1 else None])
            exec(compile(source,'original-LuckyDrawData-'+name,'exec'),namespace)
            setattr(obj,name,MethodType(namespace[name],obj))
        return obj if return_object else obj.getWishGroupProbDicts(wire)
    def test_all14_rows_original_formula_body_miss_boundaries_and_finished_filter(self):
        checked=0
        for wire in sorted(HERO_WISH_WIRES):
            rows=self.rows(wire);checked+=len(rows)
            for count in (0,5,6,17,18,35,36,89,90,99,100,99999):
                for finished in ([],[rows[0]['id']]):
                    wi={str(r['gid']):{'c':count,'f':finished,'a':[]}for r in rows}
                    actual,groups=hero_wish_probabilities(rows,wi)
                    original,original_groups=self.original_probabilities(wire,wi)
                    self.assertEqual(set(actual),set(original))
                    for rid,units in actual.items():self.assertAlmostEqual(units/1000000.,original[rid],places=12)
                    for gid,units in groups.items():self.assertAlmostEqual(units/1000000.,original_groups[gid],places=12)
        self.assertEqual(checked,14)
    def test_all14_exact_categorical_boundaries_replace_primary_original_common(self):
        for wire in sorted(HERO_WISH_WIRES):
            rows=self.rows(wire);probabilities,_=hero_wish_probabilities(rows,{})
            boundary=0
            for row in rows:
                pools={'pools':{}}
                context,plan=prepare_hero_wish_reveal(pools,self.tables,wire,self.pinned(wire),set(),lambda total:boundary)
                self.assertEqual(plan['selected_row'],row['id'])
                card=make_original_gacha_resolver(self.tables,lambda n:0,lambda *a:None,
                    make_table_hero_result(self.tables,set(self.tables['hero'])),lambda *a:context)(wire,999999)
                self.assertEqual(card['hero'],[row['wish_target']]);self.assertEqual(card['hero_file'],0)
                self.assertFalse(card['get_hero'])
                self.assertNotIn('normal_row',card['_gacha_source'])
                self.assertEqual(card['_gacha_source']['reward_ids'],list(row['reward']))
                finalize_hero_wish_reveal(pools,self.tables,wire,plan,card)
                group=pools['special']['pools'][str(wire)]['wi'][str(row['gid'])]
                self.assertIn(row['id'],group['f']);self.assertNotIn(row['wish_target'],group['f'])
                self.assertEqual(group['a'],[])
                boundary+=probabilities[row['id']]
            context,plan=prepare_hero_wish_reveal({'pools':{}},self.tables,wire,self.pinned(wire),set(),lambda total:999999)
            self.assertEqual(context,{})
            self.assertIsNone(plan['selected_row'])
            self.assertGreater(plan['ordinary_probability_units'],0)
    def test_119_sharedS_reset_fixedA_preservesS_and_no_safe_times_guarantee(self):
        pools={'pools':{}};pinned=self.pinned(119)
        for unused in range(18):
            context,plan=prepare_hero_wish_reveal(pools,self.tables,119,pinned,set(),lambda n:999999)
            finalize_hero_wish_reveal(pools,self.tables,119,plan,{'item':[[24,1]]})
        wi=pools['special']['pools']['119']['wi']
        probabilities,_=hero_wish_probabilities(self.rows(119),wi)
        self.assertEqual((wi['20']['c'],probabilities[19],probabilities[20]),(18,7500,7500))
        context,plan=prepare_hero_wish_reveal(pools,self.tables,119,pinned,set(),lambda n:999999)
        finalize_hero_wish_reveal(pools,self.tables,119,plan,{'hero':[93],'hero_file':0})
        self.assertEqual(wi['20']['c'],19);self.assertEqual(wi['21']['c'],19)
        context,plan=prepare_hero_wish_reveal(pools,self.tables,119,pinned,set(),lambda n:999999)
        finalize_hero_wish_reveal(pools,self.tables,119,plan,{'hero':[96],'hero_file':0,'get_hero':False})
        self.assertEqual(wi['20']['c'],0);self.assertEqual(wi['20']['f'],[19])
        probabilities,_=hero_wish_probabilities(self.rows(119),wi)
        self.assertEqual(probabilities[20],10000)
        fresh={'20':{'c':90,'f':[],'a':[]},'21':{'c':90,'f':[],'a':[]}}
        self.assertEqual(hero_wish_probabilities(self.rows(119),fresh)[0][21],35000)
    def test_owned_migration_pureview_normal_root_snapshot_and_animation_ack(self):
        state={'profile':{'heroes':{str(h):{}for h in self.tables['hero']}},'gacha_pools':{'pools':{}}}
        before=copy.deepcopy(state);archive=dict(self.pinned(1),wire_t=1)
        view=hero_wish_eligibility_view(state,self.tables,archive)
        self.assertEqual(state,before)
        wi=view['gacha_pools']['special']['pools']['1']['wi']
        self.assertTrue(all(v['c']==0 and v['f']==v['a']for v in wi.values()))
        projected=project_special_gacha_snapshot(view,{'ad':[]})
        self.assertEqual(dict(projected['wi']),{int(k):v for k,v in wi.items()})
        self.assertNotIn('special',state['gacha_pools'])
        pools={'pools':{}};context,plan=prepare_hero_wish_reveal(pools,self.tables,1,self.pinned(1),set(),lambda n:0)
        finalize_hero_wish_reveal(pools,self.tables,1,plan,{'hero':[90],'hero_file':0})
        current={'gacha_pools':pools}
        candidate,notices,changed,diag=prepare_special_gacha_operation(current,'setWishGroupAnimPlayed',{'t':1,'gi':[[1,[11]]]},self.tables,'anim11')
        self.assertTrue(diag['success']);self.assertEqual(notices,[])
        self.assertEqual(candidate['gacha_pools']['special']['pools']['1']['wi']['1']['a'],[11])
        repeated=prepare_special_gacha_operation(candidate,'setWishGroupAnimPlayed',{'t':1,'gi':[[1,[11]]]},self.tables,'anim11')
        self.assertEqual(repeated[0],candidate);self.assertFalse(repeated[2])
        rejected=prepare_special_gacha_operation(candidate,'setWishGroupAnimPlayed',{'t':1,'gi':[[1,[90]]]},self.tables,'not-row-id')
        self.assertFalse(rejected[3]['success']);self.assertEqual(rejected[0],candidate)
        self.assertIsNone(hero_wish_period_for_group(self.tables,1,{}))
    def test_original_normal_sync_finish_animation_selection_and_ack_body(self):
        wi={'1':{'c':0,'f':[11],'a':[]},'2':{'c':1,'f':[],'a':[]}}
        obj=self.original_probabilities(1,wi,return_object=True)
        obj.wish_info={}
        obj.activity_data={}
        namespace={'gg':SimpleNamespace(avatar=SimpleNamespace(luckyDrawData=obj)),
            'const':SimpleNamespace(LuckyDrawType=SimpleNamespace(NORMAL=1)),
            'CHOUKA_TREASURE_WISH':SimpleNamespace(data=self.tables['chouka_treasure_wish']),
            'filter':lambda fn,seq:list(builtins.filter(fn,seq))}
        member=(ROOT/'analysis/research-agent/LuckyDrawMember.py').read_text()
        def original_method(name):
            start=member.index('    def '+name+'(');end=member.find('\n    def ',start+5)
            exec(compile(textwrap.dedent(member[start:end]),'original-Member-'+name,'exec'),namespace)
            return namespace[name]
        original_method('syncWishGroupInfo')(None,1,[(1,wi['1']),(2,wi['2'])])
        self.assertIs(obj.wish_info[1],wi['1'])
        ui=(ROOT/'analysis/native-mainline-delivery/card_yingzhuang.py').read_text()
        start=ui.index('            _id_prob_dict, gid_prob_dict =',ui.index('    def set_scroll_view'))
        end=ui.index('            s_ids.sort()',start)
        block=textwrap.dedent(ui[start:end])
        namespace.update(self=SimpleNamespace(lucky_draw_type=1),show_out_anim=True,show_anim_info={})
        exec(compile(block,'original-card-yingzhuang-animation-selection','exec'),namespace)
        self.assertEqual(namespace['show_anim_list'],[11])
        self.assertEqual(namespace['show_anim_info'],{1:[11]})
        calls=[]
        actor=SimpleNamespace(callServerMethod=lambda name,args:calls.append((name,args)),heroMgrData=None)
        actor.luckyDrawData=obj
        original_method('setWishGroupAnimPlayed')(actor,1,{1:[11]})
        self.assertEqual(wi['1']['a'],[11])
        self.assertEqual(calls[0][0],'setWishGroupAnimPlayed')
        self.assertEqual(calls[0][1]['t'],1)
        self.assertEqual(list(calls[0][1]['gi']),[(1,[11])])
        namespace.update(show_anim_info={})
        exec(compile(block,'original-card-yingzhuang-animation-selection','exec'),namespace)
        self.assertEqual(namespace['show_anim_list'],[])

    def test_bonus_ownership_after_initialization_does_not_migrate_or_complete(self):
        pools={'pools':{}};pinned=self.pinned(126)
        context,plan=prepare_hero_wish_reveal(pools,self.tables,126,pinned,set(),lambda n:999999)
        finalize_hero_wish_reveal(pools,self.tables,126,plan,{'hero':[97],'hero_file':1})
        context,plan=prepare_hero_wish_reveal(pools,self.tables,126,pinned,{'97'},lambda n:0)
        self.assertEqual(plan['selected_row'],24)
        self.assertEqual(pools['special']['pools']['126']['wi']['24']['f'],[])
        finalize_hero_wish_reveal(pools,self.tables,126,plan,{'hero':[97],'hero_file':0,'get_hero':False})
        self.assertEqual(pools['special']['pools']['126']['wi']['24']['f'],[24])
