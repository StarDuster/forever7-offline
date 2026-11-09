"""Exact original-table bucket/default contracts and atomic canonical grants."""
import copy
import hashlib
import json
from pathlib import Path
import sys
import unittest
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'runtime'),str(ROOT/'tools'),str(ROOT/'analysis/research-agent')]
from read_literal_marshal import read
from offline_gacha_rewards import make_original_gacha_resolver,make_table_hero_result,apply_original_gacha_rewards
from offline_treasure import make_table_treasure_reward


class OriginalGachaRewardTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        names=('chouka_normal','chouka_default','chouka_info','chouka_friend','chouka_friend_default',
            'reward_random','reward_common','item_data','hero','chouka_hero_file','hero_treasure','hero_treasure_generate','hero_self_choose_info')
        cls.tables={name:read(ROOT/'analysis/android640-scripts/com/data/cdata'/(name+'.marshal')) for name in names}
        cls.indices=json.loads((ROOT/'tests/fixtures/combat-attribute-indices.json').read_text())['indices']
    def setUp(self):
        self.uid=1000000
        self.state={'profile':{'heroes':{str(h):{'cf':100} for h in self.tables['hero']},
            'economy':{'money':0,'summoncoin':0},'treasures':{'version':1,'items':[]}},
            'gacha':{'items':[]}}
    def make_id(self):
        self.uid+=1
        return '%024x'%self.uid
    def treasure(self,template,quality,trade):
        return make_table_treasure_reward(template,quality,self.tables['hero_treasure'],self.indices,self.make_id,123,trade)
    def resolver(self,draw=None,tables=None,context=None):
        tables=tables or self.tables
        return make_original_gacha_resolver(tables,draw or (lambda total:0),self.treasure,
            make_table_hero_result(tables,self.state['profile']['heroes']),context)
    def apply(self,card,state=None):
        return apply_original_gacha_rewards(state or self.state,[card],self.make_id,lambda tid:999999)
    def test_normal_original_integer_weights_are_mixed_and_total200000(self):
        rows=sorted((k,r)for k,r in self.tables['chouka_normal'].items()if r.get('type')==1 and r.get('weight',0)>0)
        self.assertEqual(sum(r['weight']for k,r in rows),200000)
        boundary=0; kinds=set()
        for key,row in rows:
            calls=[]
            def draw(total):
                calls.append(total)
                return boundary if len(calls)==1 else 0
            card=self.resolver(draw)(1,999999,False)
            self.assertEqual(card['_gacha_source']['normal_row'],key)
            self.assertEqual(calls[0],200000)
            planned,client,notices=self.apply(card)
            kinds.update(k for k in ('hero','treasure','item','summoncoin')if card.get(k))
            self.assertEqual(self.state['profile']['treasures']['items'],[])
            if card.get('treasure'):
                self.assertEqual(len(planned['profile']['treasures']['items']),1)
                item=planned['profile']['treasures']['items'][0]
                self.assertTrue(item['tr']['attr'])
                self.assertEqual(card['treasure'][0][3],[item['u']])
                self.assertEqual(len(card['treasure'][0]),4)
            boundary+=int(row['weight'])
        self.assertTrue({'hero','treasure','summoncoin'}.issubset(kinds),kinds)
    def test_every_positive_normal_inner_reward_constructs_and_applies(self):
        rows=[r for r in self.tables['chouka_normal'].values()if r.get('type')==1 and r.get('weight',0)>0]
        checked=0
        for row in rows:
            for pool in row['random_reward']:
                boundary=0
                for reward,weight in self.tables['reward_random'][pool]['weights']:
                    if not weight:continue
                    tables=dict(self.tables,chouka_default={(1,999999):{'pool':pool}})
                    card=self.resolver(lambda total:boundary,tables)(1,999999,False)
                    self.assertEqual(card['_gacha_source']['reward_ids'][0],reward)
                    self.apply(card)
                    boundary+=weight
                    checked+=1
        self.assertGreater(checked,100)
    def test_all_original_configured_positive_leaf_rewards_construct_and_apply(self):
        pools=set()
        for row in self.tables['chouka_normal'].values():
            if row.get('weight',0)>0:pools.update(row.get('random_reward',()))
        for row in self.tables['chouka_default'].values():
            if row.get('pool'):pools.add(row['pool'])
        for row in self.tables['chouka_friend'].values():
            if row.get('weight',0)>0:pools.update(row.get('rewards',()))
        for row in self.tables['chouka_friend_default'].values():
            if row.get('pool'):pools.add(row['pool'])
        targets={}
        for pool in sorted(pools):
            self.assertIn(pool,self.tables['reward_random'])
            boundary=0
            for rid,weight in self.tables['reward_random'][pool]['weights']:
                if weight>0:targets.setdefault(rid,(pool,boundary))
                boundary+=weight
        self.assertGreaterEqual(len(targets),1829)
        for rid,(pool,boundary) in sorted(targets.items()):
            with self.subTest(reward=rid,pool=pool):
                # Audit each original virtual leaf with its own original pool and
                # explicit fixture user choices; production never supplies choices.
                from offline_gacha_special import original_self_choose_hash
                row=self.tables['reward_common'][rid]
                virtual=[self.tables['item_data'][iid] for iid in row.get('items',()) if self.tables['item_data'][iid].get('virtual_sub_type',self.tables['item_data'][iid].get('subtype')) in range(61,68)]
                wire=virtual[0]['card_pool'] if virtual else 1
                available=[h for h,r in self.tables['hero_self_choose_info'].items()if r.get('avaliable')]
                choices=[next(h for h in available if self.tables['hero'][h]['hero_composite_init_rank']==rank) for rank in (4,3)]
                context={'choose_heroes':[original_self_choose_hash(self.tables['chouka_info'][wire])]+choices} if virtual else {}
                tables=dict(self.tables,chouka_default={(wire,999999):{'pool':pool}})
                card=self.resolver(lambda total:boundary,tables,lambda t,n:context)(wire,999999,False)
                self.assertEqual(card['_gacha_source']['reward_ids'][0],rid)
                self.apply(card)

    def test_original_fragment_converts_owned_hero_using_actual_rank_and_file_metadata(self):
        pool=371
        tables=dict(self.tables,chouka_default={(1,12345):{'pool':pool}})
        card=self.resolver(tables=tables)(1,12345,False)
        self.assertEqual(card['hero'],[12]);self.assertEqual(card['hero_file'],1)
        self.assertEqual(card['hero_frag'],{'4256':1})
        planned,client,notices=self.apply(card)
        self.assertEqual([(i['i'],i['w'])for i in planned['gacha']['items']],[(4256,1)])
        self.assertFalse(card['get_hero'])
    def test_original_friend_first10_uses_its_own_default(self):
        card=self.resolver()(99,1,False)
        self.assertEqual(card['_gacha_source']['default_pool'],1114)
    def test_atomic_failure_after_valid_currency_never_mutates_original_inventory(self):
        card={'money':10,'hero_frag':{'4256':2},'treasure':[[1033,4,1,['a'*24]]], '_gacha_treasures':[]}
        before=copy.deepcopy(self.state)
        with self.assertRaises(ValueError):self.apply(card)
        self.assertEqual(before,self.state)
    def test_unknown_bucket_is_diagnostic_not_rerolled_into_hero(self):
        tables=dict(self.tables,chouka_default={(1,5):{'pool':1}},reward_random={1:{'weights':((999,1),)}},reward_common={999:{'id':999,'unknownOfficialField':1}})
        with self.assertRaisesRegex(ValueError,'unknownOfficialField'):self.resolver(tables=tables)(1,5,False)
    def test_real_UP_rules_require_original_shared_count_context(self):
        examples=[t for t,row in self.tables['chouka_info'].items()if row.get('up_n') and any(r.get('type')==t and r.get('weight',0)>0 for r in self.tables['chouka_normal'].values())]
        self.assertTrue(examples)
        t=examples[0]
        with self.assertRaisesRegex(ValueError,'inc_up_cnt'):self.resolver()(t,999999,False)
        info=self.tables['chouka_info'][t]
        resolver=self.resolver(context=lambda pool,ordinal:{'inc_up_cnt':{info.get('inc_up_cnt_type',0):info['up_n']}})
        card=resolver(t,999999,False)
        self.assertTrue(card['_gacha_source']['forced_up'])
        row=self.tables['chouka_normal'][card['_gacha_source']['normal_row']]
        self.assertTrue(row.get('is_up'))
