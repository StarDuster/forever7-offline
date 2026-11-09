"""Configured pools and disabled-entry guards through gateway save/reply boundaries."""
import copy
from types import ModuleType, SimpleNamespace
import unittest
from unittest.mock import patch
import test_gateway_integrations as integrations
gateway=integrations.gateway
import test_offline_gacha_rewards as rewards
from offline_gacha_gateway import migrate_gateway_gacha_state, gacha_snapshot_projection

class GatewayOriginalPoolIntegration(unittest.TestCase):
    table = integrations.IntegratedGatewayTests.table
    @classmethod
    def setUpClass(cls):
        rewards.OriginalGachaRewardTests.setUpClass()
        cls.tables = rewards.OriginalGachaRewardTests.tables
        cls.indices = rewards.OriginalGachaRewardTests.indices
        cls.tables['skin'] = rewards.read(rewards.ROOT/'analysis/android640-scripts/com/data/cdata/skin.marshal')
    def setUp(self):
        integrations.IntegratedGatewayTests.setUp(self)
        self.proxy.gacha_tables = lambda: self.tables
        self.modules['com.const'].CombatAttrs.NAME_TO_INDEX = self.indices
        self.modules['com.const'].MAX_FURNITURE_TIMES_DAY = 500
        self.modules['com.const'].SUMMON_FURNITURE_LIANCHOU_TIMES = 10
        from offline_profile import grant_profile_skins
        gateway.grant_profile_skins = grant_profile_skins
        for name, rows in self.tables.items():self.table(name, rows)
        template = copy.deepcopy(self.proxy.profile['heroes']['24'])
        self.proxy.profile['heroes'] = {}
        for hero in self.tables['hero']:
            saved = copy.deepcopy(template)
            uid = '%024x' % (200000 + hero)
            saved['sk'] = {uid: dict(next(iter(template['sk'].values())), u=uid, i=hero)}
            saved['cs'] = uid
            self.proxy.profile['heroes'][str(hero)] = saved
        class Activity:
            def __init__(self, wire):self._type=wire
        self.modules['entity.avatar_attrs.LuckyDrawData'] = SimpleNamespace(ActivityData=Activity)
        self.table('unused_for_stub', {})
        import sys
        sys.modules['entity.avatar_attrs.LuckyDrawData'] = self.modules['entity.avatar_attrs.LuckyDrawData']
        self.addCleanup(lambda: sys.modules.pop('entity.avatar_attrs.LuckyDrawData', None))
        self.draw_info = {}
        self.owner.luckyDrawData = SimpleNamespace(activity_data={}, set_draw_info=lambda t, v: self.draw_info.update({t:v}))
        self.proxy.save_progress()
    def rpc(self, name, parameters):
        self.owner.replies=[]
        self.proxy.handle_gacha(name, parameters)
        return self.owner.replies
    def test_user_disabled354_rejects_without_deleting_saved_group_or_rewarding(self):
        from offline_gacha_pools import new_gacha_pools_state, prepare_pool
        self.proxy.gacha_pools = new_gacha_pools_state()
        self.proxy.gacha_pools, _ = prepare_pool(self.proxy.gacha_pools,354,{'slots':6,'lazy':True},None,seed_factory=lambda:'preserved')
        self.proxy.save_progress()
        before=copy.deepcopy(self.proxy.progress_snapshot())
        for name,args in [('requestLuckyDrawFile',{'t':354}),('requestLuckyDrawCard',{'t':354,'idx':0}),('requestFile',{'t':354}),('requestQuitFile',{'t':354})]:
            replies=self.rpc(name,args)
            self.assertFalse(next(v for n,v in replies if n.startswith('reply'))['rt'])
            self.assertEqual(self.proxy.progress_snapshot(),before)

    def test_normal_real_mixed_group_lazy_replay_and_disk_rollback(self):
        replies=self.rpc('requestLuckyDrawFile',{'t':1})
        self.assertTrue(next(v for n,v in replies if n=='replyLuckyDrawFile')['rt'])
        seeds=copy.deepcopy(self.proxy.gacha_pools['pools']['1']['group'])
        self.assertTrue(all('hero' not in c for c in seeds['cards']))
        before=copy.deepcopy(self.proxy.progress_snapshot())
        with patch.object(self.proxy._store,'write',side_effect=OSError('full')):
            replies=self.rpc('requestLuckyDrawCard',{'t':1,'idx':5})
        self.assertFalse(next(v for n,v in replies if n=='replyLuckyDrawCard')['rt'])
        self.assertEqual(self.proxy.progress_snapshot(),before)
        for idx in [5,1,3,2,4,0]:
            replies=self.rpc('requestLuckyDrawCard',{'t':1,'idx':idx})
            self.assertTrue(next(v for n,v in replies if n=='replyLuckyDrawCard')['rt'],replies)
            before=copy.deepcopy(self.proxy.progress_snapshot())
            self.rpc('requestLuckyDrawCard',{'t':1,'idx':idx})
            self.assertEqual(self.proxy.progress_snapshot(),before)
        self.assertEqual(self.proxy.gacha['opened_total'],6)
        self.assertEqual(self.owner.luckyDrawData.card_times,6)
        self.assertIsNone(self.proxy.gacha['group'])
        restored=gateway.LocalProxy(None,self.owner,persistent=True)
        self.assertEqual(restored.gacha_pools,self.proxy.gacha_pools)
        self.assertEqual(restored.gacha,self.proxy.gacha)
    def test_friend_newfriend_original_rpc_schema_independent_daily_count_and_reliable_replay(self):
        for method,pool in [('requestLuckyDrawFriendCard',99),('requestLuckyDrawNewFriendCard',131)]:
            self.owner.replies=[]
            self.proxy.handle_dedicated_gacha(method,{},operation_id='same-id-per-pool')
            expected=method.replace('request','reply',1)
            result=next(v for n,v in self.owner.replies if n==expected)
            self.assertTrue(result['st'],self.owner.replies)
            self.assertIsInstance(result['r'],dict)
            before=copy.deepcopy(self.proxy.progress_snapshot())
            self.proxy.handle_dedicated_gacha(method,{},operation_id='same-id-per-pool')
            self.assertEqual(self.proxy.progress_snapshot(),before)
            self.assertEqual(self.proxy.gacha_pools['pools'][str(pool)]['daily_count'],1)
        self.owner.replies=[]
        self.proxy.handle_dedicated_gacha('requestLuckyDrawFriendLianChouCard',{},operation_id='ten')
        result=next(v for n,v in self.owner.replies if n=='replyLuckyDrawFriendLianChouCard')
        self.assertTrue(result['st']);self.assertEqual(len(result['r']),10)
        self.assertEqual(self.proxy.gacha_pools['pools']['99']['daily_count'],11)
        self.assertEqual(self.proxy.gacha_pools['pools']['131']['daily_count'],1)
        self.assertEqual(self.proxy.gacha['opened_total'],0)

    def test_furniture_original_dedicated_schema_canonical_item_inventory_and_batch_counter(self):
        self.owner.replies=[]
        self.proxy.handle_dedicated_gacha('requestLuckyDrawFurnitureCard',{'t':106},operation_id='furniture-once')
        result=next(v for n,v in self.owner.replies if n=='replyLuckyDrawFurnitureCard')
        self.assertTrue(result['rs'],self.owner.replies)
        self.assertEqual(result['i']['ct'],1);self.assertEqual(result['i']['t'],106)
        self.assertIsInstance(result['i']['rwd'],dict)
        self.assertTrue(any(self.tables['item_data'][item['i']]['type']==20 for item in self.proxy.gacha['items']))
        self.owner.replies=[]
        self.proxy.handle_dedicated_gacha('requestLuckyDrawFurnitureLianchouCard',{'t':106},operation_id='furniture-ten')
        result=next(v for n,v in self.owner.replies if n=='replyLuckyDrawFurnitureLianchouCard')
        self.assertTrue(result['rs'],self.owner.replies)
        self.assertEqual(len(result['i']['rwd']),11)
        self.assertEqual(result['i']['ct'],12);self.assertEqual(result['i']['lt'],1)
        before=copy.deepcopy(self.proxy.progress_snapshot())
        self.proxy.handle_dedicated_gacha('requestLuckyDrawFurnitureLianchouCard',{'t':106},operation_id='furniture-ten')
        self.assertEqual(self.proxy.progress_snapshot(),before)
        self.assertEqual(self.proxy.gacha['opened_total'],0)
        self.assertEqual(self.proxy.gacha_pools['pools']['106']['items'],[])

    def test_real_direct_dispatch_callback_success_replay_and_new_avatar_identity(self):
        for method,params,pool in [('requestLuckyDrawFriendCard',{},99),('requestLuckyDrawNewFriendCard',{},131),('requestLuckyDrawFurnitureCard',{'t':106},106)]:
            self.owner.replies=[]
            self.proxy.call_server_method(method,dict(params,_cbid_=77))
            self.engine.drain()
            reply=method.replace('request','reply',1)
            payload=next(v for n,v in self.owner.replies if n==reply)
            self.assertEqual(payload.get('_cbid_'),77,'Native direct callback must receive its original identity')
            self.assertTrue(payload.get('rs',payload.get('st')))
            before=copy.deepcopy(self.proxy.progress_snapshot())
            self.owner.replies=[]
            self.proxy.call_server_method(method,dict(params,_cbid_=77));self.engine.drain()
            replay=next(v for n,v in self.owner.replies if n==reply)
            self.assertEqual(replay.get('_cbid_'),77)
            self.assertEqual(self.proxy.progress_snapshot(),before,'Same callback operation must not grant twice')
        self.owner.id='new-avatar-identity'
        restored=gateway.LocalProxy(None,self.owner,persistent=True)
        before=restored.gacha_pools['pools']['99']['opened_total']
        self.owner.replies=[]
        restored.call_server_method('requestLuckyDrawFriendCard',{'_cbid_':77});self.engine.drain()
        self.assertEqual(restored.gacha_pools['pools']['99']['opened_total'],before+1)
        self.assertEqual(next(v for n,v in self.owner.replies if n=='replyLuckyDrawFriendCard')['_cbid_'],77)
    def test_real_direct_dispatch_failed_friend_and_furniture_preserve_save_and_ack(self):
        self.proxy.handle_dedicated_gacha('requestLuckyDrawFriendCard',{},operation_id='cap-fixture')
        pool=self.proxy.gacha_pools['pools']['99']
        pool['daily_count']=100;pool['opened_total']=100
        self.proxy.save_progress()
        for method,params in [('requestLuckyDrawFriendCard',{}),('requestLuckyDrawFurnitureCard',{'t':1})]:
            before=copy.deepcopy(self.proxy.progress_snapshot())
            for repeat in range(2):
                self.owner.replies=[]
                self.proxy.call_server_method(method,dict(params,_cbid_=88));self.engine.drain()
                reply_name = 'serverCallbackCarrier' if method == 'requestLuckyDrawFriendCard' else method.replace('request','reply',1)
                payload=next(v for n,v in self.owner.replies if n==reply_name)
                self.assertEqual(payload.get('_cbid_'),88)
                if method == 'requestLuckyDrawFriendCard':
                    self.assertEqual(payload['_r_'], {})
                    self.assertFalse(any(n == 'replyLuckyDrawFriendCard' for n, _ in self.owner.replies))
                else:
                    self.assertFalse(payload.get('rs',payload.get('st')))
                self.assertEqual(self.proxy.progress_snapshot(),before)

    def test_projection_uses_pool1_group_without_rehydrating_consumed_history_items(self):
        state=migrate_gateway_gacha_state(self.proxy.progress_snapshot())
        state['gacha_pools']['pools']['1']['group']={'id':1,'cards':[{'index':i,'is_open':False,'_gacha_seed':str(i)}for i in range(6)]}
        state['gacha_pools']['pools']['1']['next_group']=2
        state['gacha']['group']=None
        projected=gacha_snapshot_projection(state,{},self.tables['chouka_info'])
        self.assertTrue(projected['iof'])
        self.assertEqual(state['gacha']['items'],[])
        self.assertIn(354,dict(projected['ad']))

if __name__=='__main__':unittest.main()
