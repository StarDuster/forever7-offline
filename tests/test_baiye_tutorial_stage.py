"""Original completion notification persists without rewards or fake replies."""
import copy
from types import SimpleNamespace as NS
import unittest
from unittest.mock import patch
import test_gateway_integrations as integrations
from test_offline_rpc_rejections import original_definition, LUCKY
from offline_gacha_gateway import gacha_snapshot_projection


class AxiliyaTutorialStageTests(unittest.TestCase):
    table = integrations.IntegratedGatewayTests.table
    def setUp(self):
        integrations.IntegratedGatewayTests.setUp(self)
        self.engine.avatar = self.owner
        self.messages = []
        self.engine.ui = NS(panels=NS(common_message=NS(notify_message=self.messages.append)))
        self.owner.luckyDrawData = NS(newbee_axiliya_finish_stage=0)
        self.owner.callServerMethod = self.proxy.call_server_method
        self.pending = []
        self.proxy.defer = lambda delay, callback: self.pending.append(callback)
        self.original = original_definition(LUCKY, 'finishAxiliyaNewbee', {}, decorated=False)

    def send(self, stage):
        self.original(self.owner, stage)
        self.pending.pop(0)()

    def test_real_notification_monotonic_replay_restart_and_snapshot(self):
        self.send(1)
        self.send(2)
        before = copy.deepcopy(self.proxy.progress_snapshot())
        self.send(1)
        self.assertEqual(self.proxy.progress_snapshot(), before)
        self.assertEqual(self.owner.luckyDrawData.newbee_axiliya_finish_stage, 2)
        restarted = integrations.gateway.LocalProxy(None, self.owner, persistent=True)
        self.assertEqual(restarted.gacha['axiliya_tutorial_stage'], 2)
        self.assertEqual(gacha_snapshot_projection(restarted.progress_snapshot(), {'axlyn': 0})['axlyn'], 2)
        self.assertEqual(self.owner.replies, [])

    def test_save_failure_and_invalid_version_restore_native_and_canonical_stage(self):
        before = copy.deepcopy(self.proxy.progress_snapshot())
        with patch.object(self.proxy._store, 'write', side_effect=OSError('disk full')):
            self.send(2)
        self.assertEqual(self.proxy.progress_snapshot(), before)
        self.assertEqual(self.owner.luckyDrawData.newbee_axiliya_finish_stage, 0)
        for stage in (True, -1, 3, '2'):
            self.send(stage)
            self.assertEqual(self.proxy.progress_snapshot(), before)
            self.assertEqual(self.owner.luckyDrawData.newbee_axiliya_finish_stage, 0)
        self.assertEqual(self.owner.replies, [])

    def test_old_owner_notification_does_not_touch_new_session(self):
        before = copy.deepcopy(self.proxy.progress_snapshot())
        self.original(self.owner, 2)
        self.engine.avatar = NS()
        self.pending.pop(0)()
        self.assertEqual(self.proxy.progress_snapshot(), before)
        self.assertEqual(self.owner.replies, [])
