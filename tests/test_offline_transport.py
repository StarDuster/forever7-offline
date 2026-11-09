from pathlib import Path
import sys
import unittest
from types import SimpleNamespace
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'runtime'))
from offline_transport import schedule_local_rpc

class FakeEngine:
    def __init__(self):
        self.timers = []
        self.cancelled = []
    def exec_delay(self, delay, callback):
        self.timers.append(callback)
    def exec_cancel_all(self):
        self.cancelled.extend(self.timers)
        self.timers = []
    def drain(self):
        while self.timers:
            callback = self.timers.pop(0)
            callback()

class TransportTests(unittest.TestCase):
    def test_repeated_purge_preserves_global_fifo_and_does_not_replay_cancelled_timers(self):
        engine, seen = FakeEngine(), []
        first, second = SimpleNamespace(owner=object()), SimpleNamespace(owner=object())
        for proxy, value in ((first, 1), (second, 2), (first, 3)):
            schedule_local_rpc(proxy, engine, 1, lambda value=value: seen.append(value))
        engine.exec_cancel_all()
        engine.exec_cancel_all()
        self.assertFalse(seen)
        for stale in engine.cancelled:
            stale()
        self.assertFalse(seen)
        engine.drain()
        self.assertEqual(seen, [1, 2, 3])
        engine.exec_cancel_all()
        engine.drain()
        self.assertEqual(seen, [1, 2, 3])

    def test_nested_purge_does_not_replay_started_business_or_drop_new_work(self):
        engine, seen = FakeEngine(), []
        proxy = SimpleNamespace(owner=object())
        def business():
            seen.append('ack')
            schedule_local_rpc(proxy, engine, 1, lambda: seen.append('nested-pull-reply'))
            engine.exec_cancel_all()
            seen.append('commit-and-business-callback')
        schedule_local_rpc(proxy, engine, 1, business)
        engine.drain()
        self.assertEqual(seen, ['ack', 'commit-and-business-callback', 'nested-pull-reply'])

    def test_destroyed_scheduler_has_no_callbacks_and_exception_does_not_poison_other_dispatch(self):
        engine, seen = FakeEngine(), []
        old = SimpleNamespace(owner=object())
        schedule_local_rpc(old, engine, 1, lambda: seen.append('stale-owner'))
        old._rpc_scheduler.close()
        engine.exec_cancel_all()
        engine.drain()
        self.assertFalse(seen)
        live = SimpleNamespace(owner=object())
        def fail():
            raise ValueError('original callback error')
        schedule_local_rpc(live, engine, 1, fail)
        schedule_local_rpc(live, engine, 1, lambda: seen.append('next'))
        with self.assertRaises(ValueError):
            engine.timers.pop(0)()
        self.assertEqual(len(live._rpc_scheduler.pending), 1)
        engine.drain()
        self.assertEqual(seen, ['next'])
