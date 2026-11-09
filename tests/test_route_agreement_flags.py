import copy
from pathlib import Path
import sys
import unittest
from types import SimpleNamespace
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'runtime'))
from offline_route_agreements import *
from offline_route_agreements import _ROUTE_FLAGS as FLAGS
EVENTS = {5073:"1",5080:"5",4044:"6",2142:"daerweila_clue_open",2068:"daerweila_clue_close",6183:"daerweila_human_close",6184:"daerweila_devil_close"}
from offline_yumi import apply_yumi_event
from test_offline_rpc_rejections import original_definition


class AgreementTests(unittest.TestCase):
    def test_exact_events_types_and_garden_separation(self):
        for event, value in EVENTS.items():
            story = {'route': '9', 'daerweila_human': 8, 'daerweila_devil': 4}
            notices = apply_route_agreement(story, event, {'special_agreement': value})
            before = copy.deepcopy(story)
            self.assertEqual(apply_route_agreement(story, event, {'special_agreement': value}), notices)
            self.assertEqual(story, before)
            self.assertEqual(story['route'], '9')
            self.assertEqual((story['daerweila_human'], story['daerweila_devil']), (8, 4))
            other = {'route':'9'}
            self.assertEqual(apply_route_agreement(other,event+99999,{'special_agreement':value}),
                             apply_route_agreement({'route':'9'},event,{'special_agreement':value}))
        for value in (1, True, ['1'], 'unknown'):
            with self.assertRaises(ValueError): apply_route_agreement({}, 5073, {'special_agreement': value})
        story = {}
        self.assertEqual(apply_route_agreement(story, 3147, {'special_agreement':'2'}), [])
        self.assertEqual(story, {})
        apply_yumi_event(story, 3147, {'special_agreement':'2'})
        self.assertTrue(story['yumi']['ycyo'])
        story['route']='9'
        apply_route_agreement(story, 4044, {'special_agreement':'6'})
        self.assertNotIn('alanSpecialGoodNight', story)

    def test_native_seed_partial_canonical_and_independent_locks(self):
        native = {'wlc':[101], 'wlr':True, 'wldr':[[101, True]]}
        original = copy.deepcopy(native)
        story = {'wuluClue':[202]}
        body = apply_route_agreement(story,5080,{'special_agreement':'5'},native)[0][1]
        self.assertEqual(body,dict(wlc=[202],wlr=True,wldr=[[101,True]],wsg=True))
        self.assertEqual(native,original)
        self.assertEqual(reset_route_goodnights(story)[0][1]['wlc'],[202])
        for event in (6184,6183): apply_route_agreement(story,event,{'special_agreement':EVENTS[event]})
        self.assertTrue(story['daerweila_human_lock']);self.assertTrue(story['daerweila_devil_lock'])

    def test_day_and_week_policy(self):
        story = {'route':'9'}
        apply_yumi_event(story,3147,{'special_agreement':'2'})
        for event in EVENTS: apply_route_agreement(story,event,{'special_agreement':EVENTS[event]})
        unchanged=copy.deepcopy(story)
        std=project_route_agreements(story,{'dwc':[9],'wlc':[3],'wlr':True})
        self.assertEqual(story,unchanged)  # snapshot/window-open does not clear nights
        notices=reset_route_goodnights(story)
        self.assertEqual(len(notices),3)
        self.assertEqual(reset_route_goodnights(story),[])
        self.assertTrue(story['yumi']['ycyo']);self.assertTrue(story['daerweila_devil_lock'])
        fresh=project_route_agreements({},std)
        for wire in ('ysg','wsg','jsg','sdh','dwhl','dwdl','ycyo'): self.assertFalse(fresh[wire])
        self.assertEqual(fresh['dwc'],[9])
        # Root week builder explicitly supplies fresh canonical empty clue state.
        fresh=project_route_agreements(dict(wuluClue=[],wuluClueReaded=False,wuluDetailReaded=[]),std)
        self.assertEqual(fresh['wlc'],[]);self.assertFalse(fresh['wlr'])

    def test_original_rpc_converters_consumers_and_reload(self):
        ns={'StandardError':Exception}
        for cls in ('ConvertError','RpcMethodArg','NoLimit','NumeralLimit','Int','Bool','Dict','List'):
            original_definition(ROOT/'analysis/decompiled/RpcMethodArgs.py',cls,ns)
        ns.update(CLIENT_STUB=3,Avatar=type('Avatar',(),{}),MailBox=type('MailBox',(),{}),xrange=range,
                  _logger=SimpleNamespace(warn=lambda *a:None,error=lambda *a:None))
        for name in ('RpcMethod','rpc_method'):
            original_definition(ROOT/'analysis/decompiled/rpcdecorator.py',name,ns)
        ns['gg']=SimpleNamespace(ui=SimpleNamespace(_tree=SimpleNamespace(proc_event=lambda *a,**kw:None)))
        data=SimpleNamespace(wuluClue=[])
        owner=SimpleNamespace(storyData=data)
        story={'route':'9'}
        import msgpack
        for event in (5080,4044,2142,6184,6183,2068):
            method,body=apply_route_agreement(story,event,{'special_agreement':EVENTS[event]},
                                            {'wlc':[12],'wlr':True,'wldr':[[12,True]]})[0]
            callback=original_definition(ROOT/'analysis/decompiled/StoryMember.py',method,ns)
            body=msgpack.unpackb(msgpack.packb(body,use_bin_type=True),raw=False)
            callback(owner,body)
        std=project_route_agreements(story,{})
        for attr,wire in FLAGS.items(): self.assertEqual(getattr(data,attr,False),std[wire])
        self.assertEqual(data.wuluClue,std['wlc'])
        self.assertEqual(data.wuluDetailReaded,dict(std['wldr']))
        # Actual original full-load assignments, not an invented loader.
        source=(ROOT/'analysis/decompiled/StoryData.py').read_text()
        import textwrap
        start=source.index("        self.wuluClue = initDict.get('wlc'")
        end=source.index('        self.clue =',start)
        code=textwrap.dedent(source[start:end])
        reloaded=SimpleNamespace()
        exec(code,{'self':reloaded,'initDict':std,'helpers':SimpleNamespace(toIntKeyDict=lambda d:d)})
        for attr in FLAGS: self.assertEqual(getattr(data,attr,False),getattr(reloaded,attr))

if __name__ == '__main__': unittest.main()
