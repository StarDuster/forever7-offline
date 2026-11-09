"""Charge and extra plans across actual gateway save, replay, and batch paths."""
import copy
from unittest.mock import patch
import test_gacha_gateway_pools as base
gateway,rewards=base.gateway,base.rewards

class ChargeGatewayTests(base.GatewayOriginalPoolIntegration):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        for name in ('chouka_leiji_reward','chouka_jiaozhi'):
            cls.tables[name]=rewards.read(rewards.ROOT/'analysis/android640-scripts/com/data/cdata'/(name+'.marshal'))
    def fixture(self,hero=None):
        tables=dict(self.tables)
        tables['chouka_default']={}
        tables['chouka_normal']={999999:{'id':999999,'type':491,'weight':1,'random_reward':(999999,)}}
        tables['reward_random']=dict(tables['reward_random'],**{})
        tables['reward_random'][999999]={'weights':((999999,1),)}
        tables['reward_common']=dict(tables['reward_common'])
        tables['reward_common'][999999]={'hero':(hero,)} if hero else {'money':1}
        return tables
    def test_actual_threshold_atomic_savefail_replay_restart_and_primary_preservation(self):
        tables=self.fixture()
        with patch.object(self.proxy,'gacha_tables',return_value=tables):
            self.rpc('requestLuckyDrawFile',{'t':491})
            self.proxy.gacha_pools['pools']['491']['opened_total']=179
            self.proxy.save_progress()
            before=copy.deepcopy(self.proxy.progress_snapshot())
            with patch.object(self.proxy._store,'write',side_effect=OSError('full')):
                replies=self.rpc('requestLuckyDrawCard',{'t':491,'idx':0})
            self.assertEqual(self.proxy.progress_snapshot(),before)
            self.assertFalse(any(n=='syncJiaozhiData'for n,v in replies))
            replies=self.rpc('requestLuckyDrawCard',{'t':491,'idx':0})
            card=self.proxy.gacha_pools['pools']['491']['group']['cards'][0]
            self.assertEqual(card['money'],1);self.assertNotIn('hero',card)
            bonus=card['_gacha_bonus_cards'][0]
            self.assertEqual(bonus['hero'],[151])
            self.assertEqual(self.proxy.gacha_pools['special']['pools']['491']['jzc']['151'],3)
            self.assertEqual(self.proxy.gacha_pools['pools']['491']['opened_total'],180)
            receipt=self.proxy.gacha_pools['charge_progress']['claims']['289']
            self.assertEqual(receipt['status'],'granted-with-primary-transaction')
            self.assertEqual(receipt['awards'][0]['hero'],[151])
            self.assertTrue(card['other_reward']['activityReward']['item'])
            saved=copy.deepcopy(self.proxy.progress_snapshot())
            replies=self.rpc('requestLuckyDrawCard',{'t':491,'idx':0})
            self.assertEqual(saved,self.proxy.progress_snapshot())
            self.assertFalse(any(n in ('updateItems','syncJiaozhiData')for n,v in replies))
            restarted=gateway.LocalProxy(None,self.owner,persistent=True)
            self.assertEqual(restarted.gacha_pools,self.proxy.gacha_pools)
            self.assertEqual(restarted.profile,self.proxy.profile)
    def test_batch_six_primary_extras_one_charge_threshold_no_bonus_count(self):
        tables=self.fixture(151)
        with patch.object(self.proxy,'gacha_tables',return_value=tables):
            self.rpc('requestLuckyDrawFile',{'t':491})
            self.proxy.gacha_pools['pools']['491']['opened_total']=11
            self.proxy.save_progress()
            before=len(self.proxy.profile['treasures']['items'])
            before_state=copy.deepcopy(self.proxy.progress_snapshot())
            with patch.object(self.proxy._store,'write',side_effect=OSError('full')):
                self.rpc('requestLuckyDrawAllLeftCard',{'t':491})
            self.assertEqual(self.proxy.progress_snapshot(),before_state)
            self.rpc('requestLuckyDrawAllLeftCard',{'t':491})
            self.assertEqual(self.proxy.gacha_pools['pools']['491']['opened_total'],17)
            claims=self.proxy.gacha_pools['charge_progress']['claims']
            self.assertEqual(list(claims),['286'])
            cards=self.proxy.gacha_pools['pools']['491']['group']['cards']
            self.assertEqual(sum(sum(b['_gacha_source']['source_kind']=='hero_extra_reward'for b in c['_gacha_bonus_cards'])for c in cards),6)
            self.assertEqual(len(self.proxy.profile['treasures']['items'])-before,6)
            self.assertEqual(self.proxy.gacha_pools['special']['pools']['491']['jzc']['151'],18)
            self.assertTrue(self.proxy.profile['heroes']['151']['pa'])
            self.assertFalse(any(i['i']==16932 for i in self.proxy.gacha['items']))
            saved=copy.deepcopy(self.proxy.progress_snapshot())
            self.rpc('requestLuckyDrawAllLeftCard',{'t':491})
            self.assertEqual(saved,self.proxy.progress_snapshot())

for name in list(vars(base.GatewayOriginalPoolIntegration)):
    if name.startswith('test_'):setattr(ChargeGatewayTests,name,None)
