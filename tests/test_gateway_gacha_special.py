import copy
from unittest.mock import patch
import test_gacha_gateway_pools as base
gateway,rewards=base.gateway,base.rewards
from offline_gacha_special import original_self_choose_hash

class GatewaySpecialTests(base.GatewayOriginalPoolIntegration):
    # Reuse setup only; avoid duplicating unrelated inherited test execution.
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        for name in ('chouka_jiaozhi','hero_self_choose_info','chouka_wish_treasure_choose','item_store_wish_change','chouka_treasure_wish'):
            cls.tables[name]=rewards.read(rewards.ROOT/'analysis/android640-scripts/com/data/cdata'/(name+'.marshal'))
    def chosen(self):
        available=[h for h,r in self.tables['hero_self_choose_info'].items()if r.get('avaliable')]
        return [next(h for h in available if self.tables['hero'][h]['hero_composite_init_rank']==rank)for rank in (4,3)]
    def test_special_reliable_save_before_success_replay_and_restart(self):
        args={'t':265,'h':self.chosen()}
        context={'wire_t':265}
        with patch.object(gateway,'offline_archive_context',return_value=context):
            self.proxy.reliable_call({'w':{'r':781,'m':'setChooseHeroes','p':args}})
            self.assertEqual(next(v for n,v in self.owner.replies if n=='replySetChooseHeroes')['r'],0)
            saved=copy.deepcopy(self.proxy.progress_snapshot())
            self.assertEqual(self.owner.luckyDrawData.activity_data[265].choose_heroes,[original_self_choose_hash(self.tables['chouka_info'][265])]+self.chosen())
            self.proxy.reliable_call({'w':{'r':781,'m':'setChooseHeroes','p':args}})
            self.assertEqual(self.proxy.progress_snapshot(),saved)
            restored=gateway.LocalProxy(None,self.owner,persistent=True)
            self.assertEqual(restored.gacha_pools,self.proxy.gacha_pools)
    def test_original_plain_animation_rpc_persists_only_finished_ids(self):
        from offline_gacha_special import SPECIAL_GACHA_POLICY
        from offline_gacha_gateway import migrate_gateway_gacha_state
        self.proxy.restore_progress(migrate_gateway_gacha_state(self.proxy.progress_snapshot()))
        self.proxy.gacha_pools['special']={'version':1,'policy':SPECIAL_GACHA_POLICY,'receipts':[],'retired_operations':[],
            'pools':{'5':{'wi':{'12':{'c':3,'f':[17,18],'a':[]}}}}}
        self.proxy.save_progress()
        self.owner.replies=[]
        self.proxy.call_server_method('setWishGroupAnimPlayed',{'t':5,'gi':[[12,[17]]]});self.engine.drain()
        self.assertEqual(self.proxy.gacha_pools['special']['pools']['5']['wi']['12']['a'],[17])
        saved=copy.deepcopy(self.proxy.progress_snapshot())
        self.proxy.call_server_method('setWishGroupAnimPlayed',{'t':5,'gi':[[12,[99]]]});self.engine.drain()
        self.assertEqual(self.proxy.progress_snapshot(),saved)
        self.assertEqual(self.owner.replies,[])
    def test_actual_wish_reveal_pinned_period_rollback_replay_and_mixed_normal(self):
        from offline_gacha_special import prepare_treasure_wish_reveal
        archive={'wire_t':5,'wish_id':129,'choice_cost_policy':'offline-free-treasure-wish-selection-v1'}
        with patch.object(gateway,'offline_archive_context',return_value=archive):
            selected=next(i for i,r in self.tables['chouka_wish_treasure_choose'].items()if r.get('can_choose') and i!=1146)
            self.proxy.handle_special_gacha('setChooseTreasure',{'t':5,'i':selected},'target-before-group')
            self.assertEqual(self.proxy.gacha_pools['special']['pools']['5']['ctr'],[129,selected,1])
            self.rpc('requestLuckyDrawFile',{'t':5})
            self.assertEqual(self.proxy.gacha_pools['pools']['5']['group']['special_context']['wish_id'],129)
            self.assertNotIn('tw',self.proxy.gacha_pools['special']['pools']['5'])
            before=copy.deepcopy(self.proxy.progress_snapshot())
            def hit(pools,tables,wire,wish,rng):return prepare_treasure_wish_reveal(pools,tables,wire,wish,lambda total:0)
            with patch.object(gateway,'prepare_treasure_wish_reveal',side_effect=hit),patch.object(self.proxy._store,'write',side_effect=OSError('full')):
                self.rpc('requestLuckyDrawCard',{'t':5,'idx':0})
            self.assertEqual(self.proxy.progress_snapshot(),before)
            archive['wish_id']=128
            with patch.object(gateway,'prepare_treasure_wish_reveal',side_effect=hit):
                replies=self.rpc('requestLuckyDrawCard',{'t':5,'idx':0})
            card=self.proxy.gacha_pools['pools']['5']['group']['cards'][0]
            source=card['_gacha_source']['treasure_wish']
            self.assertEqual(source['wish_id'],129)
            self.assertEqual(source['branch'],'wish-replacement')
            self.assertEqual(len(card['treasure']),1)
            self.assertEqual(card['treasure'][0][0],selected)
            self.proxy.sync_gacha_native_state()
            self.assertEqual(self.owner.luckyDrawData.activity_data[5].choose_treasure,[128,0,0])
            archive['wish_id']=129
            self.proxy.sync_gacha_native_state()
            self.assertEqual(self.owner.luckyDrawData.activity_data[5].choose_treasure,[129,selected,1])
            self.assertTrue(any(n=='syncTreasureWishInfo' for n,v in replies))
            saved=copy.deepcopy(self.proxy.progress_snapshot())
            replies=self.rpc('requestLuckyDrawCard',{'t':5,'idx':0})
            self.assertEqual(saved,self.proxy.progress_snapshot())
            self.assertFalse(any(n=='syncTreasureWishInfo' for n,v in replies))
            def miss(pools,tables,wire,wish,rng):return prepare_treasure_wish_reveal(pools,tables,wire,wish,lambda total:total-1)
            with patch.object(gateway,'prepare_treasure_wish_reveal',side_effect=miss):
                self.rpc('requestLuckyDrawCard',{'t':5,'idx':1})
            self.assertEqual(self.proxy.gacha_pools['special']['pools']['5']['tw']['129'],1)
            restarted=gateway.LocalProxy(None,self.owner,persistent=True)
            self.assertEqual(restarted.gacha_pools,self.proxy.gacha_pools)
    def test_jiaozhi_real_reveal_savefail_replay_restart(self):
        tables=copy.deepcopy(self.tables)
        tables['chouka_default']={}
        tables['chouka_normal']={999999:{'id':999999,'type':491,'weight':1,'random_reward':(999999,)}}
        tables['reward_random'][999999]={'weights':((999999,1),)}
        tables['reward_common'][999999]={'hero':(151,)}
        with patch.object(self.proxy,'gacha_tables',return_value=tables):
            self.rpc('requestLuckyDrawFile',{'t':491})
            before=copy.deepcopy(self.proxy.progress_snapshot())
            with patch.object(self.proxy._store,'write',side_effect=OSError('full')):
                self.rpc('requestLuckyDrawCard',{'t':491,'idx':0})
            self.assertEqual(self.proxy.progress_snapshot(),before)
            replies=self.rpc('requestLuckyDrawCard',{'t':491,'idx':0})
            self.assertEqual(self.proxy.gacha_pools['special']['pools']['491']['jzc']['151'],3)
            self.assertTrue(any(n=='syncJiaozhiData' for n,v in replies))
            card=self.proxy.gacha_pools['pools']['491']['group']['cards'][0]
            self.assertTrue(card['jiaozhi']['item'])
            saved=copy.deepcopy(self.proxy.progress_snapshot())
            replies=self.rpc('requestLuckyDrawCard',{'t':491,'idx':0})
            self.assertEqual(self.proxy.progress_snapshot(),saved)
            self.assertFalse(any(n=='syncJiaozhiData' for n,v in replies))
            restarted=gateway.LocalProxy(None,self.owner,persistent=True)
            self.assertEqual(restarted.gacha_pools,self.proxy.gacha_pools)

    def test_pendant_capture_keeps_existing_manager_pending(self):
        from types import SimpleNamespace
        self.owner.heroMgrData=SimpleNamespace(pendingSkins={151:[7]},pendingSkinsCreateTime={151:{7:123}},
            pendingPendant={151:[18]},pendingPendantCreateTime={151:{18:456}})
        state={'profile':{'heroes':{}}}
        converted=self.proxy.grant_gacha_pendant(state,{'pendant':(151,18),'pendant_trans':((24,5),)})
        self.assertEqual(converted,[(24,5)])
        self.assertEqual(state['profile']['hero_pending']['pp'],{'151':[18]})
        self.assertEqual(state['profile']['hero_pending']['ps'],{'151':[7]})
        self.assertEqual(state['profile']['hero_pending']['ppc'],{'151':{18:456}})

    def test_special_disk_failure_unlocks_without_receipt_or_choice(self):
        before=copy.deepcopy(self.proxy.progress_snapshot())
        with patch.object(gateway,'offline_archive_context',return_value={'wire_t':265}),patch.object(self.proxy._store,'write',side_effect=OSError('full')):
            self.proxy.handle_special_gacha('setChooseHeroes',{'t':265,'h':self.chosen()},'failed')
        self.assertEqual(self.proxy.progress_snapshot(),before)
        reply=next(v for n,v in self.owner.replies if n=='replySetChooseHeroes')
        self.assertNotEqual(reply['r'],0)

# Inherited tests are already collected in their own module.
for _name in list(vars(base.GatewayOriginalPoolIntegration)):
    if _name.startswith('test_'):setattr(GatewaySpecialTests,_name,None)
