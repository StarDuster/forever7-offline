"""Independent original RPC/animation contracts, not a native route playthrough.

Only extracted original consumer definitions execute in a bounded host harness;
game bytecode/modules, scene code and original data package are never imported.
"""
from contextlib import redirect_stdout
import io
from pathlib import Path
import sys
from types import SimpleNamespace
import unittest
from unittest.mock import patch

import msgpack

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT/'runtime'),str(ROOT/'tools')]
from test_offline_rpc_rejections import original_definition


class Slot:
    def __init__(self):
        self.info = None
        self.animations = 0

    def set_info(self, *values):
        self.info = values

    def do_anim(self):
        self.animations += 1


class OriginalDispatchConsumer:
    def __init__(self, human=0, devil=0):
        self.data = SimpleNamespace(daerweila_human=human,daerweila_devil=devil,
            daerweila_human_lock=False,daerweila_devil_lock=False,
            daerweila_choose_asazile=False)
        self.pending, self.events = [], []
        self.owner = SimpleNamespace(storyData=self.data)
        self.comp = SimpleNamespace(daerweila_human_comps=[Slot() for _ in range(5)],
            daerweila_devil_comps=[Slot() for _ in range(5)])
        self.gg = SimpleNamespace(avatar=self.owner,
            ui=SimpleNamespace(_tree=SimpleNamespace(proc_event=self.event),
                panels=SimpleNamespace(settlement_window=SimpleNamespace(
                    notify_daerweila=lambda side,callback:self.pending.append((side,callback))))))
        self.component_namespace = {'gg':self.gg}
        path = ROOT/'reports/astra-storyline_daerweila_zhuangtai-original.txt'
        for name in ('refresh','sync_daerweila_line_update'):
            original_definition(path,name,self.component_namespace,decorated=False)
        self.comp.refresh = lambda:self.component_namespace['refresh'](self.comp)
        namespace = {'StandardError':Exception,'unicode':str,'xrange':range}
        for name in ('ConvertError','RpcMethodArg','NoLimit','NumeralLimit','Int','Bool','Str'):
            original_definition(ROOT/'analysis/decompiled/RpcMethodArgs.py',name,namespace)
        namespace.update(CLIENT_STUB=3,Avatar=type('Avatar',(),{}),MailBox=type('MailBox',(),{}),
            _logger=SimpleNamespace(warn=lambda *args:None,error=lambda *args:None),gg=self.gg)
        for name in ('RpcMethod','rpc_method'):
            original_definition(ROOT/'analysis/decompiled/rpcdecorator.py',name,namespace)
        self.methods = {name:original_definition(ROOT/'analysis/decompiled/StoryMember.py',name,namespace)
            for name in ('syncDaerweilaLineData','daerweilaDispatchClose','addDaerweilaHumanityValue')}

    def event(self, name, *args, **kwargs):
        self.events.append((name,args,kwargs))
        if name == 'sync_daerweila_line_update':
            self.component_namespace['sync_daerweila_line_update'](self.comp,*args,**kwargs)

    def deliver(self, name, payload):
        payload = msgpack.unpackb(msgpack.packb(payload,use_bin_type=True),raw=False)
        with redirect_stdout(io.StringIO()):
            self.methods[name](self.owner,payload)

    def absolute(self, human, devil, chosen=False):
        self.deliver('syncDaerweilaLineData',dict(dh=human,dd=devil,dhl=False,ddl=False,
                                               dca=chosen,u=True))

    def animate(self):
        self.pending.pop(0)[1]()


class OriginalDispatchConsumerTests(unittest.TestCase):
    def test_increment_happens_before_real_settlement_callback_and_uses_wire_t(self):
        native = OriginalDispatchConsumer(human=1)
        native.deliver('addDaerweilaHumanityValue',{'t':'human'})
        self.assertEqual(native.data.daerweila_human,2)
        self.assertEqual(native.events,[])
        self.assertEqual(len(native.pending),1)
        native.animate()
        self.assertEqual([slot.animations for slot in native.comp.daerweila_human_comps],
                         [0,1,0,0,0])
        self.assertEqual(native.events[-1][1],('human',))

    def test_absolute_sync_requires_original_close_refresh_and_never_animates(self):
        native = OriginalDispatchConsumer()
        for _ in range(2):
            native.absolute(3,1,True)
            self.assertEqual(native.data.daerweila_human,3)
            native.deliver('daerweilaDispatchClose',{'h':False,'d':False})
        self.assertEqual(native.data.daerweila_human,3)
        self.assertEqual(native.data.daerweila_devil,1)
        self.assertTrue(native.data.daerweila_choose_asazile)
        self.assertEqual([slot.info for slot in native.comp.daerweila_human_comps],
                         [(False,True)]*3+[(False,False)]*2)
        self.assertEqual([slot.animations for slot in native.comp.daerweila_human_comps],[0]*5)
        self.assertEqual([event[1] for event in native.events],[(),()])
        self.assertEqual(native.pending,[])

    def test_absolute_then_increment_is_a_double_count_negative_control(self):
        native = OriginalDispatchConsumer(human=1)
        native.absolute(2,0)
        self.assertEqual(native.events,[])  # u=True does not refresh by itself
        native.deliver('addDaerweilaHumanityValue',{'t':'human'})
        self.assertEqual(native.data.daerweila_human,3)
        native.animate()
        self.assertEqual([slot.animations for slot in native.comp.daerweila_human_comps],
                         [0,0,1,0,0])

    def test_original_five_slot_limit_requires_source_award_bound(self):
        native = OriginalDispatchConsumer(devil=4)
        native.deliver('addDaerweilaHumanityValue',{'t':'devil'});native.animate()
        self.assertEqual(native.comp.daerweila_devil_comps[4].animations,1)
        native.deliver('addDaerweilaHumanityValue',{'t':'devil'})
        self.assertEqual(native.data.daerweila_devil,6)
        with self.assertRaises(IndexError):native.animate()

    def test_old_callback_reads_reset_count_and_animates_wrong_slot_negative_control(self):
        native = OriginalDispatchConsumer(human=0)
        native.deliver('addDaerweilaHumanityValue',{'t':'human'})
        native.absolute(0,0)
        native.animate()
        self.assertEqual(native.data.daerweila_human,0)
        self.assertEqual([slot.animations for slot in native.comp.daerweila_human_comps],
                         [0,0,0,0,1])


class DispatchPublicationConsumerTests(unittest.TestCase):
    """Post-commit fixture exercises publication through real original bodies.

    This deliberately does not claim the fixture earned an award: admission,
    lineage and actual terminal transactions are different integration tests.
    """
    def setup_publication(self):
        from offline_daerweila import publish_daerweila_award
        native = OriginalDispatchConsumer()
        award = {'pair':4213,'side':'human','choice':'0:4124:1','terminal':4126,
            'receipt':'0:4126:1','week':0,'source':{'id':'post-commit-fixture'},
            'before':{'human':0,'devil':0},'after':{'human':1,'devil':0}}
        document = {'week':0,'baseline':{'human':0,'devil':0,'choose':False},
            'first_devil':{'phase':'unseen'},'awards':{'4213':award}}
        proxy = SimpleNamespace(owner=native.owner,
            state={'story':{'week':0,'route':'13-1','daerweila_dispatch':document}})
        proxy.progress_snapshot = lambda:proxy.state
        proxy.reply = lambda name,body,*args:native.deliver(name,body)
        self.addCleanup(patch.stopall)
        patch.dict(sys.modules,{'gg':native.gg}).start()
        return native,proxy,award,publish_daerweila_award

    def test_committed_award_animates_once_and_replay_uses_absolute_refresh(self):
        native,proxy,award,publish = self.setup_publication()
        original_notify = native.gg.ui.panels.settlement_window.notify_daerweila
        publish(proxy,award)
        self.assertIs(native.gg.ui.panels.settlement_window.notify_daerweila,original_notify)
        self.assertEqual(native.data.daerweila_human,1)
        self.assertEqual(len(native.pending),1)
        native.animate()
        self.assertEqual(native.comp.daerweila_human_comps[0].animations,1)
        publish(proxy,award)
        self.assertEqual(native.data.daerweila_human,1)
        self.assertEqual(native.pending,[])
        self.assertEqual([slot.animations for slot in native.comp.daerweila_human_comps],
                         [1,0,0,0,0])

    def test_stale_original_callback_after_week_reset_cannot_animate_fifth_slot(self):
        native,proxy,award,publish = self.setup_publication()
        publish(proxy,award)
        proxy.state={'story':{'week':1,'route':'1','daerweila_dispatch':{
            'week':1,'baseline':{'human':0,'devil':0,'choose':False},
            'first_devil':{'phase':'unseen'},'awards':{}}}}
        native.absolute(0,0)
        native.animate()
        self.assertEqual(native.data.daerweila_human,0)
        self.assertEqual([slot.animations for slot in native.comp.daerweila_human_comps],[0]*5)

    def test_callback_of_replaced_owner_does_not_touch_old_or_new_ui(self):
        native,proxy,award,publish = self.setup_publication()
        publish(proxy,award)
        new_owner=SimpleNamespace(storyData=SimpleNamespace(daerweila_human=0))
        proxy.owner=new_owner
        native.gg.avatar=new_owner
        native.animate()
        self.assertEqual(native.events,[])
        self.assertEqual(new_owner.storyData.daerweila_human,0)
        self.assertEqual([slot.animations for slot in native.comp.daerweila_human_comps],[0]*5)

    def test_absolute_replay_preserves_live_optimistic_pending_intro(self):
        native,proxy,award,publish = self.setup_publication()
        publish(proxy,award)
        proxy.state['story']['daerweila_dispatch']['first_devil']['phase']='intro_pending'
        native.data.daerweila_choose_asazile=True
        publish(proxy,award)
        self.assertTrue(native.data.daerweila_choose_asazile)
        self.assertEqual(native.data.daerweila_human,1)

    def test_same_owner_reloaded_story_data_cancels_old_animation(self):
        native,proxy,award,publish = self.setup_publication()
        publish(proxy,award)
        native.data=SimpleNamespace(daerweila_human=1,daerweila_devil=0,
            daerweila_human_lock=False,daerweila_devil_lock=False,
            daerweila_choose_asazile=False)
        native.owner.storyData=native.data
        native.animate()
        self.assertEqual(native.data.daerweila_human,1)
        self.assertEqual([slot.animations for slot in native.comp.daerweila_human_comps],[0]*5)

    def test_later_award_repairs_absolute_state_before_its_one_current_animation(self):
        native,proxy,award,publish = self.setup_publication()
        publish(proxy,award)
        later=dict(award,pair=4214,choice='0:4127:1',terminal=4133,
            receipt='0:4133:1',before={'human':1,'devil':0},after={'human':2,'devil':0})
        proxy.state['story']['daerweila_dispatch']['awards']['4214']=later
        publish(proxy,later)
        self.assertEqual(native.data.daerweila_human,2)
        self.assertEqual(len(native.pending),2)
        native.animate()
        self.assertEqual([slot.animations for slot in native.comp.daerweila_human_comps],[0]*5)
        native.animate()
        self.assertEqual(native.data.daerweila_human,2)
        self.assertEqual([slot.animations for slot in native.comp.daerweila_human_comps],
                         [0,1,0,0,0])
        self.assertEqual([slot.info for slot in native.comp.daerweila_human_comps[:2]],
                         [(False,True)]*2)


if __name__ == '__main__':unittest.main()
