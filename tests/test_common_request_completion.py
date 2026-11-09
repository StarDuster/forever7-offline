"""Original Yumi wire, decoder, panel consumers and counted UI lock bodies."""
import copy
from pathlib import Path
import sys
from types import SimpleNamespace
import unittest
from unittest.mock import patch

import test_gateway_integrations as base
from test_offline_rpc_rejections import original_definition
from offline_yumi import ensure_yumi, yumi_projection

ROOT = Path(__file__).resolve().parents[1]
STORY = ROOT / 'analysis/decompiled/StoryMember.py'


class CommonRequestCompletionTests(unittest.TestCase):
    table = base.IntegratedGatewayTests.table

    def setUp(self):
        base.IntegratedGatewayTests.setUp(self)
        self.engine.avatar, self.engine._f7_avatar_proxy = self.owner, self.proxy
        self.engine.avatar_callback_map, self.engine.avatar_callback_need_result = {}, {}
        self.proxy.story['route'] = '7'
        ensure_yumi(self.proxy.story).update(ycyo=True, ycn=40, byn=2, hyn=1)
        self.proxy.save_progress()
        self.events, self.effects, self.messages, self.waits = [], [], [], []
        self.panel = SimpleNamespace(valid=True, _node=object(), cover=False)
        self.ui = SimpleNamespace(_lock={}, recon_lock=0, panels=SimpleNamespace(
            storyline_yuni=self.panel, common_message=SimpleNamespace(notify_message=self.messages.append),
            wait=SimpleNamespace(notify_show=lambda *args: self.waits.append('show'),
                notify_hide=lambda: self.waits.append('hide'), cancel_timer=lambda: self.waits.append('cancel'))))
        self.engine.ui = self.ui
        for name in ('lock', 'unlock', 'reset_lock'):
            method = original_definition(ROOT / 'analysis/decompiled/ui_manager.py', name, {'gg': self.engine}, decorated=False)
            setattr(self.ui, name, lambda *args, _method=method, **kwargs: _method(self.ui, *args, **kwargs))
        const = SimpleNamespace(DEFAULT_BAIYU_VAL=50, MAX_BAIYU_VAL=100,
            YuMiDrugType=SimpleNamespace(WITHE_DRUG=1, BLACK_DRUG=2))
        self.namespace = dict(gg=self.engine, const=const, StandardError=Exception)
        codec = ROOT / 'analysis/decompiled/RpcMethodArgs.py'
        for name in ('ConvertError', 'RpcMethodArg', 'NoLimit', 'NumeralLimit', 'Int', 'Bool', 'Dict'):
            original_definition(codec, name, self.namespace)
        self.namespace.update(CLIENT_STUB=3, Avatar=type('Avatar', (), {}),
            MailBox=type('MailBox', (), {}), xrange=range,
            _logger=SimpleNamespace(warn=lambda *args: self.fail(args), error=lambda *args: self.fail(args)))
        decorator = ROOT / 'analysis/decompiled/rpcdecorator.py'
        original_definition(decorator, 'RpcMethod', self.namespace)
        original_definition(decorator, 'rpc_method', self.namespace)
        data = self.owner.storyData = SimpleNamespace()
        initializer = original_definition(ROOT / 'analysis/decompiled/StoryData.py', 'initYumDataFromDict', self.namespace, decorated=False)
        data.initYumDataFromDict = lambda payload: initializer(data, payload)
        data.initYumDataFromDict(yumi_projection(self.proxy.story))
        for name in ('makeYumiDrugReply', 'consumeYumiDragReply', 'syncBaiyuInfos'):
            consumer = original_definition(STORY, name, self.namespace)
            def receive(payload, _name=name, _consumer=consumer):
                self.owner.replies.append((_name, copy.deepcopy(payload)))
                return _consumer(self.owner, payload)
            setattr(self.owner, name, receive)
        self.panel.yaocao_num_before = SimpleNamespace(setVisible=lambda value: None)
        self.panel.yaocao_num_now = SimpleNamespace(setString=lambda value: None)
        self.panel.update_zhiyao_page = lambda: None
        self.panel.update_weiyao_page = lambda: None
        self.panel.set_chat_msg = lambda message: None
        self.panel.play_model_anim = lambda name, **kwargs: None
        def effect(name):
            def start(callback=None):
                self.effects.append(name)
                if callback:
                    callback()
            return SimpleNamespace(start=start)
        self.ui.actions = SimpleNamespace(storyline_yuni=SimpleNamespace(
            zhiyao_num=effect('make'), weiyao_pb=effect('consume'),
            baiyao_common_eff=effect('white'), heiyao_common_eff=effect('black')))
        self.engine.audio_mgr = SimpleNamespace(play_sound=lambda *args: None, ui_sound=lambda *args: None)
        consumers = {name: original_definition(ROOT / 'reports/common-request-storyline-yuni-original.py',
            name, self.namespace, decorated=False) for name in ('reply_makeYumiDrug', 'reply_consumeYumiDrag')}
        def event(name, result, infos, **kwargs):
            self.events.append((name, result, copy.deepcopy(infos)))
            return consumers[name](self.panel, result, infos)
        self.ui._tree = SimpleNamespace(proc_event=event)
        sys.path.insert(0, str(ROOT / 'analysis/research-agent'))
        from read_literal_marshal import read
        class OriginalValuesDict(dict):
            def values(self):
                return list(super().values())
        config = read(ROOT / 'analysis/android640-scripts/com/data/cdata/yumixian_heibaiyu_const.marshal')
        self.namespace['YumixianHeiBaiYuConstDataMod'] = SimpleNamespace(data=OriginalValuesDict(config))
        self.requests = {name: original_definition(STORY, name, self.namespace, decorated=False)
            for name in ('makeYumiDrug', 'consumeYumiDrag')}
        self.reliable = None
        self.owner.callServerMethod = self.send
        self.owner.replies = []

    def send(self, name, arguments):
        if self.reliable is None:
            self.proxy.call_server_method(name, arguments)
        else:
            self.retry(name, arguments, self.reliable)

    def retry(self, name, arguments, sequence):
        self.proxy.call_server_method('reliableRpcCall', {'w': {'m': name, 'p': arguments, 'r': sequence}})

    def click(self, method='makeYumiDrug', kind=1):
        self.requests[method](self.owner, kind)

    def test_two_real_plain_clicks_same_arguments_each_commit_and_finish_original_count(self):
        self.click(); self.click()
        self.assertEqual(self.ui._lock, {'makeYumiDrug': 2})
        self.engine.drain()
        self.assertEqual(self.ui._lock, {'makeYumiDrug': 0})
        self.assertEqual(self.ui.recon_lock, 0)
        self.assertEqual(self.proxy.story['yumi']['ycn'], 20)
        self.assertEqual(self.proxy.story['yumi']['byn'], 4)
        self.assertEqual(self.effects.count('make'), 2)
        self.assertEqual(len(self.proxy.story['yumi']['receipts']), 2)
        self.click('consumeYumiDrag', 1); self.engine.drain()
        payload = next(p for n, p in reversed(self.owner.replies) if n == 'consumeYumiDragReply')
        self.assertEqual(payload['i']['_type'], 1)
        self.assertEqual(payload['i']['b'], 50)
        self.assertEqual(payload['i']['d']['byv'], 52)
        self.assertEqual(self.effects.count('consume'), 1)
        self.assertEqual(self.ui._lock['consumeYumiDrag'], 0)

    def test_wrapped_reliable_retry_and_durable_replay_never_repeat_success_animation(self):
        self.reliable = 73
        self.click()
        source = self.proxy._yumi_transport_tickets[('makeYumiDrug', 'reliable:73')]
        self.retry('makeYumiDrug', {'t': 1}, 73)
        self.assertIs(source, self.proxy._yumi_transport_tickets[('makeYumiDrug', 'reliable:73')])
        self.engine.drain()
        self.assertEqual(self.effects.count('make'), 1)
        self.assertEqual(self.ui._lock, {'makeYumiDrug': 0})
        self.assertEqual(self.proxy.story['yumi']['ycn'], 30)
        self.assertEqual(sum(n == 'reliableRpcAck' for n, _ in self.owner.replies), 2)
        # A fresh physical wait for the same durable transport identity gets
        # read-only sync and completion, never the old business animation.
        self.ui.lock('makeYumiDrug'); self.retry('makeYumiDrug', {'t': 1}, 73)
        self.engine.drain()
        self.assertEqual(self.effects.count('make'), 1)
        self.assertEqual(self.ui._lock['makeYumiDrug'], 0)
        self.reliable = None; self.click(); self.engine.drain()
        self.retry('makeYumiDrug', {'t': 1}, 73); self.engine.drain()
        self.assertEqual(self.effects.count('make'), 2)
        self.assertEqual(self.owner.storyData.yaocao_num, 20, 'Replay must not project old receipt d')
        self.assertEqual(len(self.proxy.story['yumi']['receipts']), 2)
        self.assertFalse(any(n == 'serverCallbackCarrier' for n, _ in self.owner.replies))

    def test_reset_generation_preserves_new_wait_until_its_own_original_reply(self):
        self.click()
        old = self.ui._lock
        self.ui.reset_lock(); self.click()
        self.assertIsNot(old, self.ui._lock)
        counts = []
        failure = self.proxy.fail_yumi_source
        def observe(source):
            failure(source); counts.append(dict(self.ui._lock))
        with patch.object(self.proxy, 'fail_yumi_source', side_effect=observe):
            self.engine.drain()
        self.assertEqual(counts, [{'makeYumiDrug': 1}])
        self.assertEqual(self.ui._lock, {'makeYumiDrug': 0})
        self.assertEqual(self.proxy.story['yumi']['ycn'], 30)
        self.assertEqual(self.effects.count('make'), 1)

    def test_stale_route_week_or_owner_never_writes_or_grants(self):
        original = copy.deepcopy(self.proxy.progress_snapshot())
        for reliable, scope in ((reliable, scope) for reliable in (False, True) for scope in ('route', 'week', 'owner')):
            with self.subTest(scope=scope, reliable=reliable):
                self.reliable = 99 if reliable else None
                self.proxy.owner = self.owner; self.engine.avatar = self.owner
                self.proxy.restore_progress(copy.deepcopy(original))
                self.owner.storyData.initYumDataFromDict(yumi_projection(self.proxy.story))
                self.click()
                if scope == 'owner':
                    self.proxy.owner = self.engine.avatar = SimpleNamespace()
                elif scope == 'route':
                    self.proxy.story['route'] = '1'
                else:
                    self.proxy.story['week'] += 1
                current = copy.deepcopy(self.proxy.progress_snapshot())
                with patch.object(self.proxy._store, 'write', side_effect=AssertionError('Stale request wrote save')):
                    self.engine.drain()
                self.assertEqual(self.proxy.progress_snapshot(), current)
                self.assertEqual(self.ui._lock['makeYumiDrug'], 0)
                self.assertEqual(self.effects, [])

    def test_save_failure_uses_original_typed_false_and_original_panel_failure_only(self):
        for method, message in (('makeYumiDrug', 782), ('consumeYumiDrag', 784)):
            with self.subTest(method=method):
                before = copy.deepcopy(self.proxy.progress_snapshot())
                self.click(method)
                with patch.object(self.proxy._store, 'write', side_effect=OSError('disk full')):
                    self.engine.drain()
                self.assertEqual(self.proxy.progress_snapshot(), before)
                self.assertEqual(self.ui._lock[method], 0)
                self.assertEqual(self.ui.recon_lock, 0)
                self.assertEqual(self.events[-1][1:], (False, {'rsn': 1, '_type': 1}))
                self.assertIn(message, self.messages)
                self.assertEqual(self.effects, [])

    def test_postcommit_frame_change_or_original_consumer_error_keeps_saved_result_and_finishes(self):
        for failure in ('frame', 'consumer'):
            with self.subTest(failure=failure):
                self.messages.clear()
                before = self.proxy.story['yumi']['ycn']
                if failure == 'frame':
                    save = self.proxy.save_progress
                    def save_and_replace():
                        save(); self.panel._node = object()
                    context = patch.object(self.proxy, 'save_progress', side_effect=save_and_replace)
                else:
                    context = patch.object(self.panel, 'update_zhiyao_page', side_effect=ValueError('native UI consumer failed'))
                with context:
                    self.click(); self.engine.drain()
                self.assertEqual(self.proxy.story['yumi']['ycn'], before - 10)
                self.assertEqual(self.owner.storyData.yaocao_num, before - 10)
                self.assertEqual(self.ui._lock['makeYumiDrug'], 0)
                self.assertEqual(self.ui.recon_lock, 0)
                self.assertTrue(any(isinstance(m, str) and '\u7ed3\u679c\u5df2\u4fdd\u5b58' in m for m in self.messages))
                self.assertFalse(any(isinstance(m, str) and '\u672a\u6267\u884c' in m for m in self.messages))
                self.assertFalse(any(n == 'makeYumiDrugReply' and not p['rs'] for n, p in self.owner.replies))

    def test_source_copies_arguments_and_reliable_session_namespace_changes_on_restart(self):
        captured = []
        send = self.owner.callServerMethod
        def mutate_after_dispatch(name, args):
            send(name, args); args['t'] = 2; captured.append(args)
        self.owner.callServerMethod = mutate_after_dispatch
        self.click(); self.engine.drain()
        self.assertEqual(self.proxy.story['yumi']['byn'], 3)
        self.assertEqual(self.proxy.story['yumi']['hyn'], 1)
        self.reliable = 8
        self.click(); self.engine.drain()
        previous = self.proxy._yumi_rpc_namespace
        before = self.proxy.story['yumi']['ycn']
        self.proxy = base.gateway.LocalProxy(None, self.owner, persistent=True)
        self.engine._f7_avatar_proxy = self.proxy
        self.click(); self.engine.drain()
        self.assertNotEqual(previous, self.proxy._yumi_rpc_namespace)
        self.assertEqual(self.proxy.story['yumi']['ycn'], before - 10)
        self.assertEqual(self.ui._lock['makeYumiDrug'], 0)

    def test_actual_flat_runtime_uses_shared_utility_without_offline_import_fallback(self):
        import test_generic_embedded_runtime as flat
        flat.GenericEmbeddedRuntimeTests.setUpClass()
        namespace = flat.GenericEmbeddedRuntimeTests.namespace
        namespace['_f7_doc'], namespace['_f7_log'] = self.folder.name, lambda message: None
        for name in ('acquire_ui_lock_lease', 'complete_ui_lock_lease', 'deliver_ui_lock_reply'):
            self.assertIs(namespace[name].__globals__, namespace)
        self.proxy = namespace['LocalProxy'](None, self.owner, persistent=True)
        self.engine._f7_avatar_proxy = self.proxy
        self.reliable = 91
        self.click(); self.engine.drain()
        self.assertEqual(self.proxy.story['yumi']['ycn'], 30)
        self.assertEqual(self.ui._lock['makeYumiDrug'], 0)
        self.assertEqual(self.effects.count('make'), 1)
        self.assertIn('offline_transport', flat.GenericEmbeddedRuntimeTests.blocked)


if __name__ == '__main__':
    unittest.main()
