"""All original charge/extra leaves execute as distinct canonical award plans."""
import copy
import json
from pathlib import Path
import sys
import unittest
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'runtime'),str(ROOT/'tools'),str(ROOT/'analysis/research-agent')]
import test_offline_gacha_rewards as original
from read_literal_marshal import read
from offline_gacha_rewards import make_original_gacha_resolver,make_table_hero_result,apply_original_gacha_rewards
from offline_gacha_special import (prepare_gacha_activity_bonuses,prepare_charge_crossings,
    original_self_choose_hash,CHARGE_HERO_CORRECTIONS,CHARGE_JIAOZHI_WIRES,finalize_jiaozhi_reveal,CHARGE_POLICY)
from offline_treasure import make_table_treasure_reward

class ChargeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        original.OriginalGachaRewardTests.setUpClass()
        cls.tables=dict(original.OriginalGachaRewardTests.tables)
        cls.indices=original.OriginalGachaRewardTests.indices
        for n in ('chouka_leiji_reward','chouka_jiaozhi'):
            cls.tables[n]=read(ROOT/'analysis/android640-scripts/com/data/cdata'/(n+'.marshal'))
        cls.contract=json.loads((ROOT/'reports/gacha-charge-extra-producer-contract.json').read_text())
    def setUp(self):
        self.counter=1000000
        self.owned=set(str(h)for h in self.tables['hero']);self.fragments={};self.notices=[];self.calls=[]
        self.state={'profile':{'heroes':{h:{'pa':[]}for h in self.owned},'economy':{},'treasures':{'items':[]}},'gacha':{'items':[]}}
    def uid(self):
        self.counter+=1
        return '%024x'%self.counter
    def treasure(self,i,c,t):
        return make_table_treasure_reward(i,c,self.tables['hero_treasure'],self.indices,self.uid,123,t)
    def resolve_for(self,wire):
        def resolve(rid,kind,rowid,correction,parent=None):
            self.calls.append((kind,rid))
            context={'special_random_reward_ids' if kind=='jiaozhi_threshold' else 'special_common_reward_ids':[rid]}
            if self.tables['chouka_info'][wire].get('self_choose'):
                choices=[next(h for h,r in self.tables['hero_self_choose_info'].items() if r.get('avaliable') and self.tables['hero'][h]['hero_composite_init_rank']==rank)for rank in (4,3)]
                context['choose_heroes']=[original_self_choose_hash(self.tables['chouka_info'][wire])]+choices
            if correction:
                context.update(direct_hero_reward=correction,original_common_reward_id=rid)
            card=make_original_gacha_resolver(self.tables,lambda n:0,self.treasure,
                make_table_hero_result(self.tables,self.owned,self.fragments),lambda *a:context)(wire,1)
            if parent is not None:
                parent.setdefault('item',[]).extend(card.get('item',[]))
                parent.setdefault('_gacha_item_trade_types',{}).update(card.get('_gacha_item_trade_types',{}))
            return card
        return resolve
    def apply(self,card):
        self.state,rendered,notices=apply_original_gacha_rewards(self.state,[card],self.uid,lambda i:self.tables['item_data'][i]['wrap'],item_definitions=self.tables['item_data'])
        return rendered[0]
    def test_all289_thresholds_108_isolated_wires_523_actual_leaves(self):
        wires=set(r['drawType']for r in self.tables['chouka_leiji_reward'].values())
        pools={'pools':{},'charge_progress':{'version':1,'policy':CHARGE_POLICY,'baselines':{str(w):0 for w in wires},'claims':{}}}
        checked=0
        for row in sorted(self.tables['chouka_leiji_reward'].values(),key=lambda r:r['id']):
            card={'money':1}
            before=copy.deepcopy(pools)
            prepare_gacha_activity_bonuses(pools,self.tables,row['drawType'],row['times'],card,self.owned,self.fragments,self.resolve_for(row['drawType']),self.notices)
            self.assertEqual(len(card['_gacha_bonus_cards']),len(row['rewards']))
            self.apply(card)
            receipt=pools['charge_progress']['claims'][str(row['id'])]
            self.assertEqual(receipt['common_ids'],list(row['rewards']))
            self.assertEqual(receipt['status'],'granted-with-primary-transaction')
            second={'money':1}
            prepare_gacha_activity_bonuses(pools,self.tables,row['drawType'],row['times'],second,self.owned,self.fragments,self.resolve_for(row['drawType']),self.notices)
            self.assertNotIn('_gacha_bonus_cards',second)
            checked+=1
        self.assertEqual((checked,len(wires)),(289,108))
        self.assertEqual(sum(k=='charge_threshold'for k,r in self.calls),523)
        self.assertEqual(len(pools['charge_progress']['claims']),289)
        self.assertTrue(self.state['gacha']['items'])
    def test_all43_primary_whole_extras_real_equipment_once_per_leaf(self):
        pairs=[(w,h,r)for w,d in self.tables['chouka_info'].items()for h,r in d.get('get_hero_extra_reward',())]
        self.assertEqual((len(set(w for w,h,r in pairs)),len(pairs)),(42,43))
        expected=0
        for wire,hero,rid in pairs:
            for piece in (1,0):
                card={'hero':[hero],'hero_file':piece,'get_hero':False}
                prepare_gacha_activity_bonuses({'pools':{}},self.tables,wire,1,card,self.owned,self.fragments,self.resolve_for(wire),self.notices)
                if piece:
                    self.assertNotIn('_gacha_bonus_cards',card)
                else:
                    expected+=1
                    self.assertEqual(len(card['_gacha_bonus_cards']),1)
                    bonus=card['_gacha_bonus_cards'][0]
                    self.assertEqual(bonus['_gacha_source']['source_kind'],'hero_extra_reward')
                    self.assertEqual(bonus['_gacha_source']['reward_ids'],[rid])
                    self.assertTrue(bonus['_gacha_treasures'])
                    before=len(self.state['profile']['treasures']['items'])
                    self.apply(card)
                    self.assertEqual(len(self.state['profile']['treasures']['items'])-before,len(bonus['_gacha_treasures']))
                    for treasure in bonus['_gacha_treasures']:
                        self.assertTrue(treasure['tr']['attr'])
        self.assertEqual(expected,43)
    def test_fresh_charge_hero_updates_next_card_shadow_and_migrates_pending_pa(self):
        self.owned.remove('151')
        self.state['profile']['heroes'].pop('151')
        self.state['profile']['hero_pending']={'ps':{'151':[9]},'psc':{'151':{'9':1}},'pp':{'151':[18]},'ppc':{'151':{'18':2}}}
        pools={'pools':{}};primary={'money':1}
        prepare_gacha_activity_bonuses(pools,self.tables,491,180,primary,self.owned,self.fragments,self.resolve_for(491),self.notices)
        bonus=primary['_gacha_bonus_cards'][0]
        self.assertTrue(bonus['get_hero'])
        self.assertIn('151',self.owned)
        self.assertNotIn('hero',primary)
        nextcard=self.resolve_for(491)(63138,'primary_draw',None,None)
        self.assertFalse(nextcard['get_hero']);self.assertTrue(nextcard['hero_frag'])
        prepare_gacha_activity_bonuses(pools,self.tables,491,181,nextcard,self.owned,self.fragments,self.resolve_for(491),self.notices)
        self.assertEqual(len(nextcard['_gacha_bonus_cards']),1)
        self.assertEqual(nextcard['_gacha_bonus_cards'][0]['_gacha_source']['source_kind'],'hero_extra_reward')
        candidate,rendered,notices=apply_original_gacha_rewards(self.state,[primary,nextcard],self.uid,lambda i:self.tables['item_data'][i]['wrap'],
            grant_hero=lambda state,h:{'pa':[]},item_definitions=self.tables['item_data'])
        self.assertEqual(candidate['profile']['heroes']['151']['pa'],[18])
        self.assertEqual(candidate['profile']['hero_pending']['pp'],{})
        self.assertEqual(candidate['profile']['hero_pending']['ps'],{'151':[9]})
        self.assertEqual(len(candidate['profile']['treasures']['items']),1)
        expected={int(i):v for i,v in nextcard['hero_frag'].items()}
        for i,amount in bonus.get('jiaozhi',{}).get('item',[]):
            expected[i]=expected.get(i,0)+amount
        actual={}
        for item in candidate['gacha']['items']:
            actual[item['i']]=actual.get(item['i'],0)+item['w']
        self.assertEqual(actual,expected)
        self.assertEqual(len(rendered),2)
        self.assertNotIn('151',self.state['profile']['heroes'])

    def test_archive460_conflict_label_short_and_original_dates_searchable(self):
        from offline_gacha_archive import archive_catalog,archive_filter,archive_row_label
        rows=archive_catalog(self.tables['chouka_info'])
        row=next(r for r in rows if r['wire_t']==460)
        label=archive_row_label(row)
        self.assertEqual(label,'460 资料冲突：普通十玖/维恩；充能达尔维拉/菲尼克（离线）')
        self.assertLess(len(label),55)
        begin='%04d-%02d-%02d'%tuple(row['begin'][:3])
        self.assertIn(row,archive_filter(rows,begin))
        self.assertNotIn('427',label)

    def test_source_matrix_all_wires_187zero_491three_no_bonus_recursion(self):
        for matrix in self.contract['source_kind_permission_matrix']:
            if not matrix['jiaozhi_target']:
                continue
            wire,hero=matrix['wire_t'],matrix['jiaozhi_target']
            for kind in ('charge_threshold','jiaozhi_threshold','hero_extra_reward'):
                pools={'pools':{}}
                card={'hero':[hero],'hero_file':0,'get_hero':False,'_gacha_source':{'source_kind':kind}}
                finalize_jiaozhi_reveal(pools,self.tables,wire,card,lambda rid:None)
                actual=pools.get('special',{}).get('pools',{}).get(str(wire),{}).get('jzc',{}).get(str(hero),0)
                self.assertEqual(actual,matrix['charge_target_whole_delta'] if kind=='charge_threshold' else 0)
    def test_legacy_no_retro_baselines_and_exact_future_crossing(self):
        pools={'pools':{}}
        rows=prepare_charge_crossings(pools,self.tables,491,180,'491:180')
        self.assertEqual([r['id']for r in rows],[289])
        ledger=pools['charge_progress']
        self.assertEqual(ledger['baselines'],{'491':179})
        self.assertTrue(all(ledger['claims'][str(i)]['status']=='historical-unimplemented-no-retro'for i in (286,287,288)))
        self.assertEqual(prepare_charge_crossings(pools,self.tables,491,180,'replay'),[])
        self.assertNotIn('425',ledger['baselines'])
    def test_six_finite_charge_corrections_never_alias427_or_modify_tables(self):
        before=copy.deepcopy(self.tables['chouka_leiji_reward']);norm=copy.deepcopy(self.tables['chouka_normal'])
        for rowid,hero in CHARGE_HERO_CORRECTIONS.items():
            row=self.tables['chouka_leiji_reward'][rowid];card={'money':1}
            prepare_gacha_activity_bonuses({'pools':{}},self.tables,row['drawType'],row['times'],card,self.owned,self.fragments,self.resolve_for(row['drawType']),[])
            bonus=card['_gacha_bonus_cards'][0]
            self.assertEqual(bonus['hero'],[hero]);self.assertEqual(bonus['hero_file'],0)
            self.assertFalse(bonus['get_hero'])
            self.assertTrue(bonus['hero_frag'])
            self.assertEqual(bonus['_gacha_source']['original_wire_t'],row['drawType'])
            self.assertIn('conflict_policy',bonus['_gacha_source'])
        self.assertEqual(self.tables['chouka_leiji_reward'],before)
        self.assertEqual(self.tables['chouka_normal'],norm)
