"""Actual publication adapter with original decoded consumer exception boundaries."""
import sys
from pathlib import Path
import unittest
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'tests'),str(ROOT/'runtime')]
import test_daerweila_consumer_contract as original


class PublicationFailuresTests(unittest.TestCase):
    def fixture(self):return original.DispatchPublicationConsumerTests.setup_publication(self)

    def test_failure_before_increment_recovers_absolute_without_retrying_add(self):
        native,proxy,award,publish=self.fixture();calls=[]
        def deliver(name,body):
            calls.append(name)
            if name=='addDaerweilaHumanityValue':raise IOError('before original consumer')
            native.deliver(name,body)
        proxy.reply=deliver
        publish(proxy,award);publish(proxy,award)
        self.assertEqual(native.data.daerweila_human,1)
        self.assertEqual(calls.count('addDaerweilaHumanityValue'),1)
        self.assertEqual(native.pending,[])
        self.assertTrue(native.events)

    def test_original_increment_then_notify_failure_does_not_double_and_restores_method(self):
        native,proxy,award,publish=self.fixture()
        def broken(side,callback):raise IOError('notify before storing original callback')
        panel=native.gg.ui.panels.settlement_window;panel.notify_daerweila=broken
        publish(proxy,award)
        self.assertIs(panel.notify_daerweila,broken)
        self.assertEqual(native.data.daerweila_human,1)
        self.assertEqual(native.pending,[])
        publish(proxy,award)
        self.assertEqual(native.data.daerweila_human,1)

    def test_notify_stores_real_callback_then_throws_still_never_reincrements(self):
        native,proxy,award,publish=self.fixture()
        def broken(side,callback):
            native.pending.append((side,callback))
            raise IOError('notify after retaining callback')
        panel=native.gg.ui.panels.settlement_window;panel.notify_daerweila=broken
        publish(proxy,award)
        self.assertIs(panel.notify_daerweila,broken)
        self.assertEqual(native.data.daerweila_human,1)
        native.animate()
        self.assertEqual(native.comp.daerweila_human_comps[0].animations,1)
        publish(proxy,award)
        self.assertEqual(native.data.daerweila_human,1)
        self.assertEqual(native.pending,[])

    def test_immediate_original_callback_uses_after_count_and_method_is_restored(self):
        native,proxy,award,publish=self.fixture()
        def immediate(side,callback):callback()
        panel=native.gg.ui.panels.settlement_window;panel.notify_daerweila=immediate
        publish(proxy,award)
        self.assertIs(panel.notify_daerweila,immediate)
        self.assertEqual(native.data.daerweila_human,1)
        self.assertEqual(native.comp.daerweila_human_comps[0].animations,1)

    def test_readonly_native_panel_falls_back_to_absolute_without_unsafe_increment(self):
        native,proxy,award,publish=self.fixture()
        class Panel:
            __slots__=()
            def notify_daerweila(self,side,callback):raise RuntimeError('must not call unguardable notify')
        native.gg.ui.panels.settlement_window=Panel()
        publish(proxy,award)
        self.assertEqual(native.data.daerweila_human,1)
        self.assertEqual(native.pending,[])
        self.assertEqual([slot.animations for slot in native.comp.daerweila_human_comps],[0]*5)


if __name__=='__main__':unittest.main()
