import copy
import unittest
import textwrap
from unittest.mock import patch
import test_gateway_integrations as base
from offline_yumi import *
from offline_event_effects import plan_event_effects

class Route7MedicineTests(unittest.TestCase):
    table = base.IntegratedGatewayTests.table
    def setUp(self):
        base.IntegratedGatewayTests.setUp(self)
        self.engine.avatar=self.owner;self.engine._f7_avatar_proxy=self.proxy
        self.proxy.story['route']='7'
        y=ensure_yumi(self.proxy.story);y.update(ycyo=True,ycn=20)
        self.proxy.save_progress();self.owner.replies=[]
    def request(self,method,t,key='one',context=None):
        self.proxy.handle_yumi(method,{'t':t},key,(self.owner,context or yumi_context(self.proxy.progress_snapshot())))
    def test_gateway_save_replay_restart_stale_and_failure(self):
        self.request('makeYumiDrug',1)
        self.assertEqual(self.proxy.story['yumi']['ycn'],10)
        self.assertEqual(self.owner.replies[-1][1]['i']['d']['byn'],1)
        saved=self.proxy.progress_snapshot()
        self.request('makeYumiDrug',1)
        self.assertEqual(self.proxy.progress_snapshot(),saved)
        restarted=base.gateway.LocalProxy(None,self.owner,persistent=True)
        self.assertEqual(restarted.story['yumi'],self.proxy.story['yumi'])
        self.owner.replies=[]
        with patch.object(self.proxy._store,'write',side_effect=OSError('full')):
            self.request('consumeYumiDrag',1,'consume')
        self.assertEqual(self.proxy.progress_snapshot(),saved)
        self.assertFalse(self.owner.replies[-1][1]['rs'])
        self.request('consumeYumiDrag',1,'consume')
        self.assertEqual(self.proxy.story['yumi']['byv'],52)
        self.request('makeYumiDrug',2,'stale',(999,'7',0,()))
        self.assertFalse(self.owner.replies[-1][1]['rs'])
    def test_invalid_closed_insufficient_and_owner(self):
        saved=self.proxy.progress_snapshot()
        for t in (True,0,3,'1'):
            self.request('makeYumiDrug',t)
            self.assertEqual(self.proxy.progress_snapshot(),saved)
        self.request('consumeYumiDrag',2)
        self.assertEqual(self.proxy.progress_snapshot(),saved)
        self.proxy.handle_yumi('makeYumiDrug',{'t':1},'foreign',(object(),yumi_context(saved)))
        self.assertEqual(self.proxy.progress_snapshot(),saved)
        self.proxy.story['yumi']['ycyo']=False;self.proxy.save_progress()
        self.request('makeYumiDrug',1)
        self.assertFalse(self.owner.replies[-1][1]['rs'])
    def test_original_reply_body_full_wire_projection(self):
        # Execute the original consumer body under its original rs/i contract.
        source=(base.ROOT/'analysis/decompiled/StoryMember.py').read_text()
        start=source.index('    def makeYumiDrugReply(');end=source.index('    @',start)
        body=textwrap.dedent(source[start:end]).replace("    print '==================', result, infos\n",'')
        ns={'gg':type('GG',(),{'ui':type('UI',(),{'unlock':lambda *a:None,'_tree':type('Tree',(),{'proc_event':lambda *a,**k:None})()})()})()}
        exec(body,ns)
        projected=[]
        consumer=type('Consumer',(),{'storyData':type('Data',(),{'initYumDataFromDict':lambda _,d:projected.append(d)})()})()
        self.request('makeYumiDrug',1)
        payload=self.owner.replies[-1][1]
        ns['makeYumiDrugReply'](consumer,payload['rs'],payload['i'])
        self.assertEqual(set(projected[0]),{'rt','byv','ysg','slm','ycyo','ycn','byn','hyn'})
        import msgpack
        payload=msgpack.unpackb(msgpack.packb(payload,use_bin_type=True),raw=False)
        ns['makeYumiDrugReply'](consumer,payload['rs'],payload['i'])
        start=source.index('    def consumeYumiDragReply(');end=source.index('    @',start)
        ns['const']=type('Const',(),{'MAX_BAIYU_VAL':100})()
        consumer.storyData.baiyuval=52
        exec(textwrap.dedent(source[start:end]),ns)
        self.request('consumeYumiDrag',1,'native-consume')
        payload=self.owner.replies[-1][1]
        payload=msgpack.unpackb(msgpack.packb(payload,use_bin_type=True),raw=False)
        ns['consumeYumiDragReply'](consumer,payload['rs'],payload['i'])
        self.assertEqual(projected[-1]['byv'],52)
    def test_true_completed_event_once_and_no_fake_ui(self):
        state=self.proxy.progress_snapshot();state['story'].pop('yumi');state['story'].pop('baiyu_value')
        # Literal minimal catalog retains real dialog and original deltas.
        catalog={3147:{'dialog':3147,'special_agreement':'2'},3141:{'gainBaiyuVal':5}}
        c,n,d=plan_event_effects(state,3147,catalog,{}, {})
        # Event effects are called only after story engine completion gates.
        self.assertTrue(d['ready']);self.assertTrue(c['story']['yumi']['ycyo'])
        c,n,d=plan_event_effects(state,3147,catalog,{}, {'completed_callbacks':['dialog:3147']})
        # Callback spelling is deliberately checked by the actual engine below.
        self.assertFalse(any(name=='completeEventReplyEnd' for name,payload in n))
        c,n,d=plan_event_effects(state,3141,catalog,{}, {'receipt_key':'event3141'})
        self.assertTrue(d['ready'],d);self.assertEqual(c['story']['baiyu_value'],55)
        c2,n,d=plan_event_effects(c,3141,catalog,{}, {'receipt_key':'event3141'})
        self.assertEqual(c2['story']['baiyu_value'],55)
    def test_actual_count_policy_and_counterexamples(self):
        p=self.proxy.progress_snapshot();c=copy.deepcopy(p)
        active={'fight_id':'native291','request':{'s':291}}
        notices=settle_yumi_herbs(p,c,{'s':291,'w':1,'e':{'yaocao_num':13}},active)
        self.assertEqual(c['story']['yumi']['ycn'],33)
        self.assertEqual(notices[0][0],'syncBaiyuInfos')
        with self.assertRaises(ValueError):settle_yumi_herbs(p,c,{'s':291,'w':1,'e':{'yaocao_num':13}},active)
        for count in (-1,True,'13'):
            with self.assertRaises(ValueError):settle_yumi_herbs(p,copy.deepcopy(p),{'s':291,'w':1,'e':{'yaocao_num':count}},active)
        c=copy.deepcopy(p);self.assertEqual(settle_yumi_herbs(p,c,{'s':291,'w':0},active),[])
        self.assertEqual(c,p)
    def test_original_3147_dialog_required_and_real_291_win_settles_once(self):
        import sys
        sys.path.insert(0,str(base.ROOT/'analysis/research-agent'))
        from read_literal_marshal import read
        from read_data_table import read as source_read
        content=source_read(base.ROOT/'analysis/decompiled/event_content.py')
        missions=read(base.ROOT/'analysis/android640-scripts/com/data/cdata/mission.marshal')
        self.table('event_content',{3146:content[3146],3147:content[3147]})
        self.table('mission',{291:missions[291]})
        self.proxy.story['yumi']['ycyo']=False
        self.proxy.available_events={3147:1};self.proxy.save_progress()
        self.proxy.reliable_call({'w':{'m':'startEvent','p':{'e':3147},'r':50}})
        self.assertFalse(self.proxy.story['yumi']['ycyo'])
        self.proxy.process_story('trace',{'k':'dialog','d':{'c':3147}})
        self.assertTrue(self.proxy.story['yumi']['ycyo'])
        self.assertIn(3147,self.proxy.completed_events)
        self.proxy.available_events={3146:1};self.proxy.save_progress()
        self.proxy.reliable_call({'w':{'m':'startEvent','p':{'e':3146},'r':51}})
        self.proxy.process_story('trace',{'k':'dialog','d':{'c':3146}})
        self.assertNotIn(3146,self.proxy.completed_events)
        self.proxy.handle_battle_admission({'t':2,'s':291,'h':[24],'d':{}},52)
        active=copy.deepcopy(self.proxy.battle['active'])
        self.assertIsNotNone(active)
        self.assertEqual(self.proxy.story['yumi']['ycn'],20)
        result={'t':2,'s':291,'h':[24],'x':[],'w':True,'e':{'yaocao_num':11}}
        before=self.proxy.progress_snapshot()
        with patch.object(self.proxy._store,'write',side_effect=OSError('full')):
            with self.assertRaises(OSError):self.proxy.handle_battle_finish(result,active['fight_id'])
        self.assertEqual(self.proxy.progress_snapshot(),before)
        self.proxy.handle_battle_finish(result,active['fight_id'])
        self.assertEqual(self.proxy.story['yumi']['ycn'],31)
        self.assertIn(3146,self.proxy.completed_events)
        self.proxy.handle_battle_finish(result,active['fight_id'])
        self.assertEqual(self.proxy.story['yumi']['ycn'],31)
