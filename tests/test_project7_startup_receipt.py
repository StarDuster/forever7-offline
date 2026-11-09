"""Finite consumer contract for the pre-updater loopback receipt."""
import _paths  # noqa: E402,F401
import importlib.util
import sys
import time
import types
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('p7_receipt_hook', ROOT / 'runtime/project7_startup_hook.py')
hook = importlib.util.module_from_spec(spec)
spec.loader.exec_module(hook)


class Response(object):
    def __init__(self, data): self.data = data
    def read(self, limit): return self.data[:limit]
    def close(self): pass


class ReceiptHarness(object):
    def __init__(self, response=None, error=None, errors=None):
        self.calls = []
        self.repairs = []
        self.panels = []
        self.opener_calls = []
        self.response = response
        self.error = error
        self.pending_errors = list(errors or [])
        self._urllib2 = sys.modules.get('urllib2')
        module = types.ModuleType('urllib2')

        class ProxyHandler(object):
            def __init__(self, proxies): self.proxies = proxies

        class Opener(object):
            def __init__(self, owner): self.owner = owner
            def open(self, url, timeout=0):
                self.owner.opener_calls.append((url, timeout))
                if self.owner.pending_errors:
                    raise self.owner.pending_errors.pop(0)
                if self.owner.error is not None:
                    raise self.owner.error
                return Response(self.owner.response)

        module.ProxyHandler = ProxyHandler
        module.build_opener = lambda handler: Opener(self)
        sys.modules['urllib2'] = module

        self.render = types.SimpleNamespace(logic=None)
        self.render.set_logic = lambda callback: setattr(self.render, 'logic', callback)
        namespace = {'calls': self.calls, 'render': self.render,
                     'panels': self.panels, '_step_skip': False}
        exec(compile("""
def clean(state):
    calls.append(('clean', state))
def done(state):
    calls.append(('done', state))
    clean(state)
def start():
    calls.append('orig_start')
""", '<receipt-harness>', 'exec'), namespace, namespace)
        def panel_init(self):
            self.text = None
        def panel_set_text(self, text):
            self.text = text
            namespace['panels'].append(text)
        namespace['patch_panel'] = type('Panel', (), {
            '__init__': panel_init, 'set_text': panel_set_text,
        })
        self.namespace = namespace
        self.patch = types.SimpleNamespace(
            start=namespace['start'],
            clean=namespace['clean'],
            _q7_verify_offline_resources=lambda: {'ok': True},
            _q7_activate_game_mode=lambda state: self.calls.append(('activate', state)),
        )
        self.policy = types.SimpleNamespace(
            patch=self.patch, repair=self.repairs.append,
            log=lambda code: self.calls.append(('log', code)))
        self.installed = hook.StartupPolicy.install_startup_receipt(self.policy)
        self.patch.start()

    def dispatch(self, until=2.0):
        deadline = time.time() + until
        while time.time() < deadline:
            callback = self.render.logic
            if callback is None:
                break
            callback()
            if any(isinstance(item, tuple) and item[0] == 'done' for item in self.calls):
                break
            if self.repairs:
                break
            time.sleep(0.01)

    def close(self):
        if self._urllib2 is None:
            sys.modules.pop('urllib2', None)
        else:
            sys.modules['urllib2'] = self._urllib2


class StartupReceiptTests(unittest.TestCase):
    def setUp(self):
        # Never wait the production window out: the fake clock advances only on
        # sleep, so the retry budget expires deterministically.
        self._saved_budget = (hook._BOOTSTRAP_WINDOW_S, hook._BOOTSTRAP_CLOCK,
                              hook._BOOTSTRAP_SLEEP)
        self.now = [0.0]
        hook._BOOTSTRAP_WINDOW_S = 1.5
        hook._BOOTSTRAP_CLOCK = lambda: self.now[0]

        def sleep(seconds):
            self.now[0] += seconds
        hook._BOOTSTRAP_SLEEP = sleep

    def tearDown(self):
        (hook._BOOTSTRAP_WINDOW_S, hook._BOOTSTRAP_CLOCK,
         hook._BOOTSTRAP_SLEEP) = self._saved_budget
        sys.modules.pop('urllib2', None)

    def test_exact_game_verifies_activates_and_calls_done_clean_once(self):
        harness = ReceiptHarness('project7-bootstrap-v1\ngame\n')
        try:
            harness.dispatch()
            for unused in range(4):
                harness.render.logic()
            self.assertEqual(harness.calls.count('orig_start'), 0)
            self.assertEqual(sum(1 for c in harness.calls if isinstance(c, tuple) and c[0] == 'done'), 1)
            self.assertEqual(sum(1 for c in harness.calls if isinstance(c, tuple) and c[0] == 'clean'), 1)
            self.assertEqual(sum(1 for c in harness.calls if isinstance(c, tuple) and c[0] == 'activate'), 1)
            self.assertEqual(harness.repairs, [])
        finally:
            harness.close()

    def test_resources_calls_original_start_once(self):
        harness = ReceiptHarness('project7-bootstrap-v1\nresources\n')
        try:
            harness.dispatch()
            for unused in range(4):
                harness.render.logic()
            self.assertEqual(harness.calls.count('orig_start'), 1)
            self.assertEqual(sum(1 for c in harness.calls if isinstance(c, tuple) and c[0] == 'done'), 0)
        finally:
            harness.close()

    def test_http_error_exhausts_budget_then_repairs_once_without_done(self):
        harness = ReceiptHarness(error=OSError('RemoteDisconnected'))
        try:
            harness.dispatch()
            # Budget 1.5s with a 0.5s backoff is exactly three attempts.
            self.assertEqual(len(harness.opener_calls), 3)
            self.assertEqual(harness.repairs, ['resource_verify_failed'])
            self.assertEqual(sum(1 for c in harness.calls if isinstance(c, tuple) and c[0] == 'done'), 0)
            self.assertEqual(harness.calls.count('orig_start'), 0)
        finally:
            harness.close()

    def test_invalid_reply_exhausts_budget_then_repairs_once_without_done(self):
        harness = ReceiptHarness('not-a-receipt')
        try:
            harness.dispatch()
            self.assertEqual(len(harness.opener_calls), 3)
            self.assertEqual(harness.repairs, ['resource_verify_failed'])
            self.assertEqual(sum(1 for c in harness.calls if isinstance(c, tuple) and c[0] == 'done'), 0)
            self.assertEqual(harness.calls.count('orig_start'), 0)
        finally:
            harness.close()

    def test_transient_error_then_game_receipt_skips_repair_and_done_once(self):
        harness = ReceiptHarness('project7-bootstrap-v1\ngame\n',
                                 errors=[OSError('ECONNREFUSED')])
        try:
            harness.dispatch()
            self.assertEqual(len(harness.opener_calls), 2)
            self.assertEqual(harness.repairs, [])
            self.assertEqual(sum(1 for c in harness.calls if isinstance(c, tuple) and c[0] == 'done'), 1)
            self.assertEqual(harness.calls.count('orig_start'), 0)
        finally:
            harness.close()

    def test_snapshot_failure_repairs_without_done(self):
        harness = ReceiptHarness('project7-bootstrap-v1\ngame\n')
        harness.patch._q7_verify_offline_resources = lambda: (_ for _ in ()).throw(ValueError('bad snapshot'))
        try:
            harness.dispatch()
            self.assertEqual(len(harness.repairs), 1)
            self.assertEqual(sum(1 for c in harness.calls if isinstance(c, tuple) and c[0] == 'done'), 0)
            self.assertEqual(harness.calls.count('orig_start'), 0)
        finally:
            harness.close()

    def test_missing_render_controller_is_an_explicit_install_error(self):
        namespace = {'calls': []}
        exec(compile("def start():\n    pass\ndef done(state):\n    pass\ndef clean(state):\n    pass\n", '<missing-render>', 'exec'), namespace, namespace)
        patch = types.SimpleNamespace(start=namespace['start'], clean=namespace['clean'])
        policy = types.SimpleNamespace(patch=patch, repair=lambda code: None, log=lambda code: None)
        with self.assertRaises(RuntimeError):
            hook.StartupPolicy.install_startup_receipt(policy)


if __name__ == '__main__':
    unittest.main()

class RpcCleanupTests(unittest.TestCase):
    def test_unreg_listener_is_idempotent_after_disconnect(self):
        import types
        package = types.ModuleType('mobilerpc')
        module = types.ModuleType('mobilerpc.RpcChannel')
        class MobileRpcChannel(object):
            def __init__(self):
                self.con_listeners = set()
            def unreg_listener(self, listener):
                self.con_listeners.remove(listener)
        module.MobileRpcChannel = MobileRpcChannel
        previous = {name: sys.modules.get(name) for name in ('mobilerpc', 'mobilerpc.RpcChannel')}
        sys.modules['mobilerpc'] = package
        sys.modules['mobilerpc.RpcChannel'] = module
        try:
            policy = types.SimpleNamespace()
            self.assertTrue(hook.StartupPolicy.install_rpc_listener_guard(policy))
            channel = MobileRpcChannel()
            listener = object()
            channel.con_listeners.add(listener)
            channel.unreg_listener(listener)
            channel.unreg_listener(listener)
            channel.con_listeners = None
            channel.unreg_listener(listener)
        finally:
            for name, value in previous.items():
                if value is None:
                    sys.modules.pop(name, None)
                else:
                    sys.modules[name] = value
