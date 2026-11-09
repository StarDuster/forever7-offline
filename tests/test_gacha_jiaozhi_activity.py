"""Original all-threshold coverage and finite transaction activity policies."""
import copy
import sys
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'runtime'),str(ROOT/'analysis/research-agent'),str(ROOT/'tools')]
from read_literal_marshal import read
from offline_gacha_special import (finalize_jiaozhi_reveal,prepare_jiaozhi_context,
    advance_gacha_shadow,grant_original_pendant,gacha_pending_for_client)
from offline_gacha_rewards import make_original_gacha_resolver,make_table_hero_result,apply_original_gacha_rewards

class ActivityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        names=('chouka_jiaozhi','chouka_normal','chouka_default','chouka_info','reward_random','reward_common','item_data','hero','chouka_hero_file')
        cls.tables={n:read(ROOT/'analysis/android640-scripts/com/data/cdata'/(n+'.marshal')) for n in names}
    def test_all_156_thresholds_real_items_and_idempotence(self):
        seen=set(); leaves=0; pendant=0
        for row in self.tables['chouka_jiaozhi'].values():
            pools={'pools':{}}
            card={'hero':[row['target_hero']],'hero_file':0,'get_hero':False}
            # Above every threshold, still one grant per original row.
            pools['special']={'version':1,'policy':'original-special-choice-v1','pools':{str(row['drawType']):{'jzc':{str(row['target_hero']):100}}},'receipts':[]}
            rewards=[]
            def expand(rid):
                for common,weight in self.tables['reward_random'][rid]['weights']:
                    rewards.append(common)
            finalize_jiaozhi_reveal(pools,self.tables,row['drawType'],card,expand)
            count=len(rewards)
            finalize_jiaozhi_reveal(pools,self.tables,row['drawType'],card,expand)
            self.assertEqual(count,len(rewards))
            for rid in row['rewards']:
                for cid,w in self.tables['reward_random'][rid]['weights']:
                    common=self.tables['reward_common'][cid]
                    self.assertTrue(common.get('items'))
                    leaves+=1
                    pendant+=sum(self.tables['item_data'][i].get('virtual_sub_type')==13 for i in common['items'])
            seen.add(row['drawType'])
        self.assertEqual((len(seen),len(self.tables['chouka_jiaozhi']),leaves,pendant),(28,156,188,27))
    def test_owned_whole_three_and_natural_blessing_shadow(self):
        wire=491; hero=151; pools={'pools':{}}
        for unused in range(2):
            finalize_jiaozhi_reveal(pools,self.tables,wire,{'hero':[hero],'get_hero':False,'hero_file':0},lambda rid:None)
        self.assertEqual(pools['special']['pools'][str(wire)]['jzc'][str(hero)],6)
        owned=set(); masks={str(hero):1}
        ctx=prepare_jiaozhi_context(pools,self.tables,wire,owned,masks)
        piece=ctx['bless_fragment'](hero,1)
        self.assertEqual(piece,2)
        advance_gacha_shadow({'hero':[hero],'hero_file':piece},owned,masks,self.tables)
        ctx=prepare_jiaozhi_context(pools,self.tables,wire,owned,masks)
        self.assertEqual(ctx['bless_fragment'](hero,1),3)
        owned.add(str(hero))
        self.assertEqual(ctx['bless_fragment'](hero,1),1)
    def test_pendant_real_ownership_no_equip_or_skin_reset_and_duplicate(self):
        definition=self.tables['item_data'][16932]
        state={'profile':{'heroes':{'151':{'pa':[],'wpa':[9],'pat':{'9':17},'sk':{'keep':1}}}}}
        before=copy.deepcopy(state)
        self.assertEqual(grant_original_pendant(state,definition),[])
        self.assertEqual(state['profile']['heroes']['151']['pa'],[18])
        for key in ('wpa','pat','sk'):
            self.assertEqual(state['profile']['heroes']['151'][key],before['profile']['heroes']['151'][key])
        self.assertEqual(grant_original_pendant(state,definition),list(definition['pendant_trans']))
        pending={'profile':{'heroes':{},'hero_pending':{'ps':{'keep':[2]},'psc':{'keep':3},'pp':{},'ppc':{'keep':4}}}}
        grant_original_pendant(pending,definition)
        self.assertEqual(pending['profile']['hero_pending']['pp'],{'151':[18]})
        self.assertEqual(pending['profile']['hero_pending']['ps'],{'keep':[2]})
    def test_canonical_bonus_pendant_inventory_and_full_sync_source(self):
        state={'profile':{'heroes':{'151':{'pa':[],'wpa':[7]}},'economy':{},'treasures':{'items':[]}},'gacha':{'items':[]}}
        card={'jiaozhi':{'item':[[16932,1]],'treasure':[]}}
        candidate,rendered,notices=apply_original_gacha_rewards(state,[card],lambda:'0'*24,lambda i:999,
            item_definitions=self.tables['item_data'],grant_pendant=grant_original_pendant)
        self.assertEqual(candidate['profile']['heroes']['151']['pa'],[18])
        self.assertEqual(candidate['profile']['heroes']['151']['wpa'],[7])
        self.assertEqual(candidate['gacha']['items'],[])
        self.assertEqual(state['profile']['heroes']['151']['pa'],[])
        self.assertEqual(rendered[0]['jiaozhi']['item'],[[16932,1]])

    def test_archive_time_bypass_only_exact_selected_wire_original_row(self):
        import offline_gacha_archive as archive
        from unittest.mock import patch
        check=archive.make_archive_jiaozhi_checker(lambda obj,key:False,{(491,156):{'drawType':491},(491,999):{'drawType':354},(425,1):{'drawType':425}})
        with patch.object(archive,'_f7_archive_session',{'wire_t':491}):
            self.assertTrue(check(None,(491,156)))
            self.assertFalse(check(None,(491,999)))
            self.assertFalse(check(None,(425,1)))
            self.assertFalse(check(None,(491,111)))
        pending=gacha_pending_for_client({'hero_pending':{'pp':{'151':[18]}}},{'ps':{7:[1]},'ppc':{7:12},'bhrs':[99]})
        self.assertEqual(pending['pp'],{151:[18]})
        self.assertEqual(pending['ps'],{7:[1]})
        self.assertNotIn('bhrs',pending)
        nested=gacha_pending_for_client({'hero_pending':{'psc':{'151':{'18':23,'opaque':9}}}})
        self.assertEqual(nested['psc'],{151:{18:23,'opaque':9}})

    def test_six_transaction_local_fragment_choices_and_unowned_whole(self):
        hero=151; pools={'pools':{}}; owned=set(); masks={}
        pools['special']={'version':1,'policy':'original-special-choice-v1','receipts':[],
            'pools':{'491':{'rc':{'151':6}}}}
        revealed=[]
        for unused in range(3):
            context=prepare_jiaozhi_context(pools,self.tables,491,owned,masks)
            piece=context['bless_fragment'](hero,1)
            revealed.append(piece)
            advance_gacha_shadow({'hero':[hero],'hero_file':piece},owned,masks,self.tables)
        self.assertEqual(revealed,[1,2,3])
        advance_gacha_shadow({'hero':[hero],'hero_file':0},owned,masks,self.tables)
        for unused in range(2):
            context=prepare_jiaozhi_context(pools,self.tables,491,owned,masks)
            self.assertEqual(context['bless_fragment'](hero,1),1)
        self.assertEqual(pools['special']['pools']['491']['rc']['151'],3)

    def test_replace_keeps_all_original_row_boundaries(self):
        for wire in (126,143,154,164):
            rows=sorted((k,r)for k,r in self.tables['chouka_normal'].items() if r.get('type')==wire and r.get('weight',0)>0)
            boundary=0
            for key,row in rows:
                selected=[]; calls=[]
                def rng(total):
                    calls.append(total)
                    return boundary if len(calls)==1 else 0
                # Replace nested rewards with simple original hero leaves, preserving row pools.
                tables=copy.deepcopy(self.tables)
                for rid in tables['reward_random']:
                    tables['reward_random'][rid]['weights']=((999999,1),)
                tables['reward_common'][999999]={'items':(24,),'itemsNum':(1,)}
                owned=set(self.tables['hero'])
                resolver=make_original_gacha_resolver(tables,rng,lambda *a:None,make_table_hero_result(tables,owned),lambda *a:{'owned_heroes':owned})
                card=resolver(wire,999999)
                self.assertEqual(card['_gacha_source']['normal_row'],key)
                expected=row.get('replace_reward',())
                self.assertEqual(bool(card['_gacha_source'].get('replace')),bool(expected))
                boundary+=int(row['weight'])
