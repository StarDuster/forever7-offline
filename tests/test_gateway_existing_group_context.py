"""Canonical effective period reaches actual native projection and setting RPC."""
import copy
from types import SimpleNamespace as NS
import unittest
import test_gacha_gateway_pools as base
import offline_gacha_archive as archive
from offline_gacha_gateway import migrate_gateway_gacha_state
from offline_gacha_special import SPECIAL_GACHA_POLICY
import offline_gacha_ui as ui

gateway,rewards=base.gateway,base.rewards

class ExistingGroupGatewayTests(base.GatewayOriginalPoolIntegration):
    @classmethod
    def setUpClass(cls):
        super().setUpClass();cls.tables=dict(cls.tables)
        for name in ('chouka_treasure_wish','chouka_wish_treasure_choose','item_store_wish_change'):
            cls.tables[name]=rewards.read(rewards.ROOT/'analysis/android640-scripts/com/data/cdata'/(name+'.marshal'))
    def setUp(self):
        super().setUp();del self.proxy.__dict__['gacha_tables']
        self.engine.avatar=self.owner;self.engine._f7_avatar_proxy=self.proxy
        archive.offline_archive_clear();self.addCleanup(archive.offline_archive_clear)
    def test_t5_groupA_projection_free_validation_and_failure_reply_allA_not_selectedB(self):
        ids=sorted(k for k,r in self.tables['chouka_treasure_wish'].items()if r.get('drawType')==5)
        a,b=ids[0],ids[-1]
        archive._f7_archive_session=archive.archive_make_session({'wire_t':5,'category':'hero_treasure'},self.tables['chouka_treasure_wish'],a)
        self.rpc('requestLuckyDrawFile',{'t':5})
        self.assertEqual(self.proxy.gacha_pools['pools']['5']['group']['special_context']['wish_id'],a)
        self.proxy.gacha_pools['special']={'version':1,'policy':SPECIAL_GACHA_POLICY,'receipts':[],'retired_operations':[],
            'pools':{'5':{'ctr':[b,1146,4],'ctr_by_wish':{str(a):[a,1141,2],str(b):[b,1146,4]}}}}
        self.proxy.save_progress();before=copy.deepcopy(self.proxy.progress_snapshot())
        archive._f7_archive_session=archive.archive_make_session({'wire_t':5,'category':'hero_treasure'},self.tables['chouka_treasure_wish'],b)
        self.proxy.sync_gacha_native_state(5)
        self.assertEqual(self.owner.luckyDrawData.activity_data[5].choose_treasure,[a,1141,2])
        effective=archive.offline_archive_context(5)
        self.assertEqual(effective['wish_id'],a)
        self.assertTrue(ui.free_wish_selection_context(effective,self.tables['chouka_treasure_wish']))
        getter=archive.make_archive_wish_getter(lambda *args:b,self.tables['chouka_treasure_wish'])
        self.assertEqual(getter(None,5),a)
        valid=ui.make_free_wish_validation(lambda *args:1885,lambda:archive.offline_archive_context(5),self.tables['chouka_treasure_wish'])
        self.assertEqual(valid(self.owner,5,1143),0)
        item=next(i for i,r in self.tables['chouka_wish_treasure_choose'].items()if r.get('can_choose')and i!=1141)
        self.owner.replies=[];self.proxy.handle_special_gacha('setChooseTreasure',{'t':5,'i':item},'active-choice')
        payload=next(v for n,v in self.owner.replies if n=='replySetChooseTreasure')
        self.assertEqual(payload['r'],1884);self.assertEqual(payload['i'],[a,1141,2])
        self.assertEqual(self.proxy.progress_snapshot(),before)
    def test_expired_restore_blocks_newgroup_until_explicit_original_tab_choice(self):
        self.proxy.restore_progress(migrate_gateway_gacha_state(self.proxy.progress_snapshot()));self.proxy.save_progress()
        archive._f7_archive_session={'wire_t':1,'effective_group_id':7,'no_wish':True}
        before=copy.deepcopy(self.proxy.progress_snapshot())
        replies=self.rpc('requestLuckyDrawFile',{'t':1})
        payload=next(v for n,v in replies if n=='replyLuckyDrawFile')
        self.assertFalse(payload['rt']);self.assertEqual(self.proxy.progress_snapshot(),before)
        selected=[];panel=NS(draw_type=1)
        choose=archive.make_archive_direct_selection(lambda p,w:selected.append(w))
        choose(panel,1)
        self.assertIsNone(archive.offline_archive_context())
        self.rpc('requestLuckyDrawFile',{'t':1})
        self.assertIsNotNone(self.proxy.gacha_pools['pools']['1']['group'])
        self.assertNotIn('special_context',self.proxy.gacha_pools['pools']['1']['group'])
        self.assertEqual(selected,[1])
    def test_legacy_t5_no_wish_rejects_stale_setting_and_preserves_group(self):
        self.rpc('requestLuckyDrawFile',{'t':5})
        old=next(k for k,r in self.tables['chouka_treasure_wish'].items()if r.get('drawType')==5)
        self.proxy.gacha_pools['special']={'version':1,'policy':SPECIAL_GACHA_POLICY,'receipts':[],'retired_operations':[],
            'pools':{'5':{'ctr':[old,1141,4],'ctr_by_wish':{str(old):[old,1141,4]}}}}
        self.proxy.save_progress()
        before=copy.deepcopy(self.proxy.progress_snapshot())
        context=archive.offline_archive_context(5)
        self.assertTrue(context['no_wish'])
        self.proxy.sync_gacha_native_state(5)
        self.assertEqual(self.owner.luckyDrawData.activity_data[5].choose_treasure,[0,0,0])
        item=next(i for i,r in self.tables['chouka_wish_treasure_choose'].items()if r.get('can_choose'))
        self.owner.replies=[];self.proxy.handle_special_gacha('setChooseTreasure',{'t':5,'i':item},'no-wish-choice')
        payload=next(v for n,v in self.owner.replies if n=='replySetChooseTreasure')
        self.assertEqual(payload['r'],1882);self.assertEqual(payload['i'],[0,0,0])
        self.assertEqual(self.proxy.progress_snapshot(),before)

for name in list(vars(base.GatewayOriginalPoolIntegration)):
    if name.startswith('test_'):setattr(ExistingGroupGatewayTests,name,None)
