import copy
import unittest
from types import SimpleNamespace
from unittest.mock import patch
import test_gateway_integrations as integrations
import test_offline_item_exchange as exchange_tests

gateway=integrations.gateway

class ExchangeGatewayTests(unittest.TestCase):
    table=integrations.IntegratedGatewayTests.table
    @classmethod
    def setUpClass(cls):exchange_tests.OriginalItemExchangeTests.setUpClass();cls.tables=exchange_tests.OriginalItemExchangeTests.tables
    def setUp(self):
        integrations.IntegratedGatewayTests.setUp(self)
        self.engine.avatar=self.owner
        self.modules['com.const'].FRAGMENT_COMMON_ID=24
        for name,rows in self.tables.items():
            if isinstance(rows,dict):self.table(name,rows)
        self.proxy.defer=lambda delay,callback:callback()
        self.proxy._item_exchange_clock=lambda:1700000000
        self.proxy.profile['economy'].update(yuanbao=100000,crystal=100000,bind_crystal=0,summoncoin=0)
        self.proxy.gacha['items']=[{'u':'%024x'%1,'i':4253,'w':5,'tt':3,'c':0,'ctt':0,'le':0,'lo':None,'ele':0}]
        self.proxy.save_progress()
    def call(self,args):
        self.owner.replies=[]
        self.proxy.call_server_method('memoryCrystalExchangeSuipian',args)
        return self.owner.replies
    def test_plain_true_callback_reply_inventory_and_same_request_replay(self):
        replies=self.call({'ii':[[4253,1]],'_cbid_':77})
        self.assertEqual(replies[-1],('replyMemoryCrystalExchangeSuipian',{'ii':[[4253,1]],'sp':10,'_cbid_':77}))
        self.assertTrue(any(n=='updateItems'for n,p in replies))
        saved=self.proxy.progress_snapshot()
        replies=self.call({'ii':[[4253,1]],'_cbid_':77})
        self.assertEqual(self.proxy.progress_snapshot(),saved)
        self.assertEqual(replies,[('serverCallbackCarrier',{'_r_':{},'_cbid_':77})])
    def test_save_failure_and_invalid_quantity_only_callback_failure(self):
        before=self.proxy.progress_snapshot()
        with patch.object(self.proxy._store,'write',side_effect=OSError('diskfull')):
            replies=self.call({'ii':[[4253,1]],'_cbid_':88})
        self.assertEqual(self.proxy.progress_snapshot(),before)
        self.assertEqual(replies,[('serverCallbackCarrier',{'_r_':False,'_cbid_':88})])
        replies=self.call({'ii':[[4253,-1]],'_cbid_':89})
        self.assertEqual(self.proxy.progress_snapshot(),before)
        self.assertFalse(any(n=='replyMemoryCrystalExchangeSuipian'for n,p in replies))
    def test_restart_new_nonce_same_callback_and_owner_is_new_purchase(self):
        self.call({'ii':[[4253,1]],'_cbid_':77})
        old_session=self.proxy._item_exchange_session
        second=gateway.LocalProxy(None,self.owner,persistent=True)
        self.assertNotEqual(second._item_exchange_session,old_session)
        second.defer=lambda delay,callback:callback()
        second._item_exchange_clock=self.proxy._item_exchange_clock
        self.owner.replies=[]
        second.call_server_method('memoryCrystalExchangeSuipian',{'ii':[[4253,1]],'_cbid_':77})
        self.assertEqual(sum(i['w']for i in second.gacha['items']if i['i']==4253),3)
        self.assertEqual(sum(i['w']for i in second.gacha['items']if i['i']==24),20)
    def test_reliable_ack_original_reply_and_replay_not_credited_twice(self):
        parameters={'w':{'m':'memoryCrystalExchangeSuipian','p':{'ii':[[4253,1]]},'r':3},'_cbid_':20}
        self.owner.replies=[];self.proxy.reliable_call(parameters)
        self.assertEqual(self.owner.replies[0],('reliableRpcAck',{'s':3}))
        self.assertEqual(self.owner.replies[-1][1]['_cbid_'],20)
        before=self.proxy.progress_snapshot();self.proxy.reliable_call(parameters)
        self.assertEqual(self.proxy.progress_snapshot(),before)
    def test_old_owner_after_delay_cannot_spend_or_notify_new_avatar(self):
        callbacks=[];self.proxy.defer=lambda delay,callback:callbacks.append(callback)
        self.proxy.call_server_method('memoryCrystalExchangeSuipian',{'ii':[[4253,1]],'_cbid_':9})
        before=self.proxy.progress_snapshot();self.engine.avatar=object();self.owner.replies=[]
        callbacks.pop()()
        self.assertEqual(self.proxy.progress_snapshot(),before);self.assertEqual(self.owner.replies,[])
    def test_owner_changes_during_inventory_notice_no_old_success_delivery(self):
        original=self.owner.updateItems
        def update(payload):
            original(payload)
            self.engine.avatar=object()
        self.owner.updateItems=update
        replies=self.call({'ii':[[4253,1]],'_cbid_':43})
        self.assertTrue(any(n=='updateItems'for n,p in replies))
        self.assertFalse(any(n=='replyMemoryCrystalExchangeSuipian'for n,p in replies))
    def test_production_module_ascii_python27_grammar_and_loader_order(self):
        from lib2to3.refactor import RefactoringTool
        import patch_bootstrap
        source=(exchange_tests.ROOT/'runtime/offline_item_exchange.py').read_text(encoding='ascii')
        RefactoringTool([]).refactor_string(source,'offline_item_exchange.py')
        embedded=patch_bootstrap.embedded_loader(exchange_tests.ROOT/'runtime')
        self.assertIn('def prepare_item_exchange',embedded)
        self.assertLess(embedded.index('def prepare_item_exchange'),embedded.index('def handle_item_exchange'))

    def test_live_ui_limit_projection_and_calendar_rollover(self):
        data=SimpleNamespace(checkSummoncoinExchangeNum=lambda index,num=1:data.summoncoin_weekly_limit.get(index,0)+num<=5)
        self.owner.luckyDrawData=data
        self.proxy.install_item_exchange_limit_check()
        for cb in range(5):self.proxy.handle_item_exchange('summoncoinExchange',{'i':4},cb+1)
        self.assertFalse(data.checkSummoncoinExchangeNum(4))
        self.proxy.story['week']=3;self.assertFalse(data.checkSummoncoinExchangeNum(4))
        self.proxy._item_exchange_clock=lambda:1700000000+7*86400
        self.assertTrue(data.checkSummoncoinExchangeNum(4))

if __name__=='__main__':unittest.main()
