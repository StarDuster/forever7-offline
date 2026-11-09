import copy
import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'runtime'))
from offline_yumi import apply_yumi_event, ensure_yumi, prepare_yumi_operation, yumi_context
from offline_route_agreements import apply_route_agreement, project_route_agreements, validate_route_agreements

class GenericAdapters(unittest.TestCase):
    def test_yumi_signed_clamp_and_unseen_ids(self):
        story={}
        for event,delta,want in ((999901,70,100),(999902,-130,0),(999903,17,17)):
            apply_yumi_event(story,event,{'gainBaiyuVal':delta})
            self.assertEqual(story['baiyu_value'],want)
        apply_yumi_event(story,999904,{'special_agreement':'2'})
        self.assertTrue(story['yumi']['ycyo'])
        for bad in (True,1.0,'3',[],{}):
            before=copy.deepcopy(story)
            with self.assertRaises(ValueError):apply_yumi_event(story,999905,{'gainBaiyuVal':bad})
            self.assertEqual(story,before)

    def test_routes_and_exact_strings(self):
        for route,flag,method,wire in (('9-3','jiaohui_special_goodnight','syncJiaohuiSpecialNight','jsn'),('11-1','alanSpecialGoodNight','syncAlanSpecialNight','asn')):
            story={'route':route}
            self.assertEqual(apply_route_agreement(story,999991,{'special_agreement':'6'}),[(method,{wire:True})])
            self.assertTrue(story[flag])
        for route in ('12','1',''):
            story={'route':route};before=copy.deepcopy(story)
            with self.assertRaises(ValueError):apply_route_agreement(story,4044,{'special_agreement':'6'})
            self.assertEqual(story,before)
        for bad in (1,True,'7','unknown'):
            with self.assertRaises(ValueError):apply_route_agreement({},9,{'special_agreement':bad})

    def test_pure_projection_validation_and_no_admission(self):
        # These adapters never choose/complete an event or evaluate engine conditions.
        story={'route':'7','available_events':[7],'completed_events':[]}
        apply_yumi_event(story,99999,{'gainBaiyuVal':1,'completeConds':{'dialog':[7]}})
        self.assertEqual(story['completed_events'],[])
        self.assertEqual(story['available_events'],[7])
        before=copy.deepcopy(story)
        project_route_agreements(story,{'wlc':[1]});validate_route_agreements(story)
        self.assertEqual(story,before)

    def test_durable_original_reply_and_legacy_schema(self):
        state={'story':{'route':'7','week':1}}
        y=ensure_yumi(state['story']);y.update(ycyo=True,byn=2)
        context=yumi_context(state)
        candidate,reply,changed=prepare_yumi_operation(state,'consumeYumiDrag',{'t':1},'receipt',context)
        self.assertTrue(changed);self.assertEqual(reply['i']['b'],50)
        candidate['story']['yumi']['byv']=70;candidate['story']['baiyu_value']=70
        replay,again,changed=prepare_yumi_operation(candidate,'consumeYumiDrag',{'t':1},'receipt',context)
        self.assertFalse(changed);self.assertEqual(again,reply);self.assertEqual(replay,candidate)
        receipt=candidate['story']['yumi']['receipts']['receipt']
        self.assertEqual((receipt['before'],receipt['after']),(50,52))
        candidate['story']['yumi']['receipts']['legacy']=['consumeYumiDrag',1]
        validate_route_agreements(candidate['story'])
        with self.assertRaisesRegex(ValueError,'Legacy'):
            prepare_yumi_operation(candidate,'consumeYumiDrag',{'t':1},'legacy',context)

if __name__=='__main__':unittest.main()
