"""Hero wish via production loader, real original reward body and atomic RPCs."""
import copy
import random
from unittest.mock import patch
import test_gacha_gateway_pools as base
from offline_gacha_special import HERO_WISH_PERIOD_POLICY
from offline_gacha_archive import archive_catalog,archive_make_session

gateway,rewards=base.gateway,base.rewards

class HeroWishGatewayTests(base.GatewayOriginalPoolIntegration):
    @classmethod
    def setUpClass(cls):
        super().setUpClass();cls.tables=dict(cls.tables)
        for name in ('chouka_treasure_wish','chouka_jiaozhi','chouka_leiji_reward'):
            cls.tables[name]=rewards.read(rewards.ROOT/'analysis/android640-scripts/com/data/cdata'/(name+'.marshal'))
    def setUp(self):
        super().setUp();del self.proxy.__dict__['gacha_tables']
        self.assertIs(self.proxy.gacha_tables.__func__,gateway.LocalProxy.gacha_tables)
        normal={900000+w:{'id':900000+w,'type':w,'weight':1,'random_reward':(999999,)}for w in (1,119,126,143,154,164)}
        rr=dict(self.tables['reward_random']);rr[999999]={'weights':((999999,1),)}
        common=dict(self.tables['reward_common']);common[999999]={'money':1}
        self.table('chouka_normal',normal);self.table('chouka_default',{});self.table('reward_random',rr);self.table('reward_common',common)
    def archive(self,wire):
        rows=self.proxy.gacha_tables()['chouka_treasure_wish']
        row=next(r for r in archive_catalog(self.proxy.gacha_tables()['chouka_info'])if r['wire_t']==wire)
        representative=min(k for k,r in rows.items()if r.get('drawType')==wire and r.get('wish_type')==2)
        return archive_make_session(row,rows,hero_wish_id=representative)
    def seed_hit(self):return next(i for i in range(10000)if random.Random(i).randrange(1000000)<10000)
    def test_primary_wish_real_grant_firstS3_extra_once_rollback_replay_restart(self):
        template=copy.deepcopy(self.proxy.profile['heroes']['97'])
        self.proxy.profile['heroes'].pop('97');self.proxy.profile['heroes'].pop('98');self.proxy.save_progress()
        archive=self.archive(126)
        with patch.object(gateway,'offline_archive_context',return_value=archive),patch.object(gateway,'native_default_hero_snapshot',return_value=template,create=True):
            self.rpc('requestLuckyDrawFile',{'t':126})
            group=self.proxy.gacha_pools['pools']['126']['group']
            self.assertEqual(group['special_context']['hero_wish_ids'],[24,25])
            self.assertNotIn('special',self.proxy.gacha_pools)
            group['cards'][0]['_gacha_seed']=self.seed_hit();self.proxy.save_progress()
            before=copy.deepcopy(self.proxy.progress_snapshot())
            with patch.object(self.proxy._store,'write',side_effect=OSError('full')):
                self.rpc('requestLuckyDrawCard',{'t':126,'idx':0})
            self.assertEqual(self.proxy.progress_snapshot(),before)
            archive.clear();archive.update(self.archive(143)) # A different valid archive cannot change the pinned group.
            replies=self.rpc('requestLuckyDrawCard',{'t':126,'idx':0})
            card=self.proxy.gacha_pools['pools']['126']['group']['cards'][0]
            self.assertEqual(card['hero'],[97]);self.assertTrue(card['get_hero'])
            self.assertNotIn('normal_row',card['_gacha_source'])
            self.assertEqual(card['_gacha_source']['hero_wish']['selected_row'],24)
            row=self.proxy.gacha_pools['special']['pools']['126']
            self.assertEqual(row['jzc']['97'],3)
            self.assertEqual(row['wi']['24'],{'c':0,'f':[24],'a':[]})
            self.assertEqual(len(self.proxy.profile['treasures']['items']),1)
            names=[n for n,v in replies];self.assertLess(names.index('syncWishGroupInfo'),names.index('replyLuckyDrawCard'))
            saved=copy.deepcopy(self.proxy.progress_snapshot())
            replies=self.rpc('requestLuckyDrawCard',{'t':126,'idx':0})
            self.assertEqual(self.proxy.progress_snapshot(),saved)
            self.assertFalse(any(n in ('syncWishGroupInfo','updateItems')for n,v in replies))
            restarted=gateway.LocalProxy(None,self.owner,persistent=True)
            self.assertEqual(restarted.gacha_pools,self.proxy.gacha_pools)
            self.assertEqual(restarted.profile,self.proxy.profile)
    def test_fresh_normal1_wish_without_extra_still_syncs_full_hero_snapshot(self):
        template=copy.deepcopy(self.proxy.profile['heroes']['90'])
        for hero in ('90','91','92'):self.proxy.profile['heroes'].pop(hero)
        self.proxy.save_progress()
        with patch.object(gateway,'offline_archive_context',return_value=self.archive(1)),patch.object(gateway,'native_default_hero_snapshot',return_value=template,create=True):
            self.rpc('requestLuckyDrawFile',{'t':1})
            seed=next(i for i in range(10000)if random.Random(i).randrange(1000000)<5000)
            self.proxy.gacha_pools['pools']['1']['group']['cards'][0]['_gacha_seed']=seed
            self.proxy.save_progress()
            replies=self.rpc('requestLuckyDrawCard',{'t':1,'idx':0})
            card=self.proxy.gacha_pools['pools']['1']['group']['cards'][0]
            self.assertEqual(card['hero'],[90]);self.assertTrue(card['get_hero'])
            self.assertNotIn('_gacha_bonus_cards',card)
            sync=next(v for n,v in replies if n=='syncHeroesData')
            self.assertIn(90,[hero for hero,snapshot in sync['d']])
            self.assertEqual(self.owner.luckyDrawData.wish_info[1],{'c':0,'f':[11],'a':[]})
            self.assertIn('90',self.proxy.profile['heroes'])

    def test_full_roster_view_prepare_firstdraw_no_fake_award_and_normal_root_animation(self):
        archive=self.archive(1)
        with patch.object(gateway,'offline_archive_context',return_value=archive):
            before=copy.deepcopy(self.proxy.progress_snapshot())
            self.proxy.sync_gacha_native_state()
            self.assertEqual(self.proxy.progress_snapshot(),before)
            self.assertEqual(self.owner.luckyDrawData.wish_info[1],{'c':0,'f':[11,12],'a':[11,12]})
            self.rpc('requestLuckyDrawFile',{'t':1})
            self.assertNotIn('special',self.proxy.gacha_pools)
            self.assertEqual(self.proxy.gacha_pools['pools']['1']['opened_total'],0)
            before_heroes=copy.deepcopy(self.proxy.profile['heroes'])
            replies=self.rpc('requestLuckyDrawCard',{'t':1,'idx':0})
            wi=self.proxy.gacha_pools['special']['pools']['1']['wi']
            self.assertTrue(all(v['c']==0 and v['f']==v['a']for v in wi.values()))
            self.assertEqual(self.owner.luckyDrawData.wish_info,{int(k):v for k,v in wi.items()})
            self.assertEqual(self.proxy.profile['heroes'],before_heroes)
            self.assertNotIn('jzc',self.proxy.gacha_pools['special']['pools']['1'])
            self.assertEqual(self.proxy.profile['treasures']['items'],[])
            self.assertEqual(self.proxy.gacha_pools['pools']['1']['opened_total'],1)
            saved=copy.deepcopy(self.proxy.progress_snapshot())
            self.rpc('requestFile',{'t':1});self.proxy.sync_gacha_native_state()
            self.assertEqual(self.proxy.progress_snapshot(),saved)
    def test_no_implicit_historical_normal1_and_sequential_six_miss_progress(self):
        self.rpc('requestLuckyDrawFile',{'t':1})
        self.rpc('requestLuckyDrawCard',{'t':1,'idx':0})
        self.assertNotIn('special',self.proxy.gacha_pools)
        self.proxy.profile['heroes'].pop('94');self.proxy.profile['heroes'].pop('96');self.proxy.profile['heroes'].pop('93')
        with patch.object(gateway,'offline_archive_context',return_value=self.archive(119)):
            self.rpc('requestLuckyDrawFile',{'t':119})
            miss=next(i for i in range(100)if random.Random(i).randrange(1000000)>45000)
            for card in self.proxy.gacha_pools['pools']['119']['group']['cards']:card['_gacha_seed']=miss
            self.proxy.save_progress()
            self.rpc('requestLuckyDrawAllLeftCard',{'t':119})
            wi=self.proxy.gacha_pools['special']['pools']['119']['wi']
            self.assertEqual(wi['20'],{'c':6,'f':[],'a':[]})
            self.assertEqual(wi['21'],{'c':6,'f':[],'a':[]})
            saved=copy.deepcopy(self.proxy.progress_snapshot())
            self.rpc('requestLuckyDrawAllLeftCard',{'t':119})
            self.assertEqual(self.proxy.progress_snapshot(),saved)

for name in list(vars(base.GatewayOriginalPoolIntegration)):
    if name.startswith('test_'):setattr(HeroWishGatewayTests,name,None)
