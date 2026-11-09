"""Bounded host verification of dedicated/special request ownership and replay."""
import copy
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
import unittest

import test_gateway_gacha_special as special_base
from test_offline_rpc_rejections import original_definition
gateway = special_base.gateway

ROOT = Path(__file__).resolve().parents[1]
ORIGINAL = ROOT / 'analysis/research-agent/LuckyDrawMember.py'


class GachaRpcLifecycleTests(special_base.GatewaySpecialTests):
    def setUp(self):
        super().setUp()
        self.messages, self.locks = [], []
        self.panel = SimpleNamespace(valid=True, draw_type=5, _node=object(), _f7_presentation_epoch=0)
        self.engine.ui = SimpleNamespace(panels=SimpleNamespace(card_tab=self.panel,
            common_message=SimpleNamespace(notify_message=self.messages.append)),
            unlock=lambda name: self.locks.remove(name), lock=lambda name: self.locks.append(name))
        self.engine.avatar = self.owner
        self.engine._f7_avatar_proxy = self.proxy
        self.engine.avatar_callback_map, self.engine.avatar_callback_need_result = {}, {}
        self.owner.luckyDrawData.friend_draw = False
        self.context = {'wire_t': 5, 'wish_id': 129, 'choice_cost_policy': 'offline-free-treasure-wish-selection-v1'}
        self.archive = patch.object(gateway, 'offline_archive_context', side_effect=lambda wire=None: copy.deepcopy(self.context) if wire in (None, self.context.get('wire_t')) else None)
        self.archive.start(); self.addCleanup(self.archive.stop)
        self.selected = next(item for item, row in self.tables['chouka_wish_treasure_choose'].items()
            if row.get('can_choose') and item not in (1146, self.tables['chouka_treasure_wish'][128]['treasure_id']))

    def original_reply(self, name, fields):
        # The actual source bodies and actual field converters, with only the
        # native object's bookkeeping/graphics represented by the host fixture.
        namespace = {'gg': self.engine, 'StandardError': Exception}
        path = ROOT / 'analysis/decompiled/RpcMethodArgs.py'
        for cls in ('ConvertError', 'RpcMethodArg', 'NoLimit', 'NumeralLimit', 'Int', 'Bool', 'Dict', 'List'):
            original_definition(path, cls, namespace)
        namespace.update(CLIENT_STUB=3, Avatar=type('Avatar', (), {}), MailBox=type('MailBox', (), {}),
            xrange=range, _logger=SimpleNamespace(warn=lambda *args: self.fail(args), error=lambda *args: self.fail(args)))
        decorator = ROOT / 'analysis/decompiled/rpcdecorator.py'
        original_definition(decorator, 'RpcMethod', namespace)
        original_definition(decorator, 'rpc_method', namespace)
        path = ROOT / 'analysis/decompiled/ReliableRpcMember.py' if name == 'serverCallbackCarrier' else ORIGINAL
        body = original_definition(path, name, namespace)
        def consume(parameters):
            self.owner.replies.append((name, copy.deepcopy(parameters)))
            body(self.owner, parameters)
        setattr(self.owner, name, consume)

    def queue(self, name, arguments, reliable=False, sequence=1, callback=None):
        if reliable:
            payload = {'w': {'m': name, 'p': arguments, 'r': sequence}}
            if callback is not None:
                payload['_cbid_'] = callback
            self.proxy.call_server_method('reliableRpcCall', payload)
        else:
            self.proxy.call_server_method(name, dict(arguments, **({'_cbid_': callback} if callback is not None else {})))

    def restart(self):
        self.proxy = gateway.LocalProxy(None, self.owner, persistent=True)
        self.proxy.gacha_tables = lambda: self.tables
        self.engine._f7_avatar_proxy = self.proxy

    def original_counted_locks(self):
        ui = self.engine.ui
        ui._lock, ui.recon_lock = {}, 0
        self.wait_events = []
        ui.panels.wait = SimpleNamespace(notify_show=lambda *args: self.wait_events.append('show'),
            notify_hide=lambda: self.wait_events.append('hide'), cancel_timer=lambda: self.wait_events.append('cancel'))
        for name in ('lock', 'unlock', 'reset_lock'):
            method = original_definition(ROOT / 'analysis/decompiled/ui_manager.py', name, {'gg': self.engine}, decorated=False)
            setattr(ui, name, lambda *args, _method=method, **kwargs: _method(ui, *args, **kwargs))
        return ui

    def original_choose_request(self, sequence):
        self.owner.validSetChooseTreasure = lambda *args: 0
        self.owner.callServerMethodReliable = lambda method, args: self.queue(method, args, True, sequence)
        method = original_definition(ORIGINAL, 'setChooseTreasure', {'gg': self.engine}, decorated=False)
        method(self.owner, 5, self.selected)

    def original_friend_request(self, callback_id=77):
        self.owner.luckyDrawData.friend_draw_count = 0
        self.owner.luckyDrawData.canSummonFriendFirst = lambda: True
        def send(name, args, callback):
            self.engine.avatar_callback_map[callback_id] = callback
            self.queue(name, args, callback=callback_id)
        self.owner.callServerMethod = send
        method = original_definition(ORIGINAL, 'requestLuckyDrawFriendCard', {'gg': self.engine,
            'const': SimpleNamespace(SUMMON_FRIEND_COST=0, MAX_SUMMON_FRIEND_TIMES_DAY=100)}, decorated=False)
        method(self.owner)

    def test_dedicated_same_owner_callback_and_sequence_reuse_after_restart_are_new_draws(self):
        for reliable in (False, True):
            with self.subTest(reliable=reliable):
                method = 'requestLuckyDrawNewFriendCard' if reliable else 'requestLuckyDrawFriendCard'
                pool = '131' if reliable else '99'
                self.queue(method, {}, reliable, 77, 77); self.engine.drain()
                before = self.proxy.gacha_pools['pools'][pool]['opened_total']
                saved = copy.deepcopy(self.proxy.progress_snapshot())
                self.queue(method, {}, reliable, 77, 77); self.engine.drain()
                self.assertEqual(self.proxy.progress_snapshot(), saved)
                old_namespace = self.proxy._gacha_rpc_namespaces['dedicated']
                self.restart()
                self.queue(method, {}, reliable, 77, 77); self.engine.drain()
                self.assertEqual(self.proxy.gacha_pools['pools'][pool]['opened_total'], before + 1)
                self.assertNotEqual(old_namespace, self.proxy._gacha_rpc_namespaces['dedicated'])

    def test_special_reliable_sequence_reuse_after_restart_cannot_replay_old_success(self):
        args = {'t': 5, 'i': self.selected}
        self.queue('setChooseTreasure', args, True, 91); self.engine.drain()
        self.assertEqual(next(v for n, v in reversed(self.owner.replies) if n == 'replySetChooseTreasure')['r'], 0)
        saved = copy.deepcopy(self.proxy.progress_snapshot())
        self.queue('setChooseTreasure', args, True, 91); self.engine.drain()
        self.assertEqual(self.proxy.progress_snapshot(), saved)
        self.restart(); self.owner.replies = []
        self.queue('setChooseTreasure', args, True, 91); self.engine.drain()
        self.assertNotEqual(next(v for n, v in self.owner.replies if n == 'replySetChooseTreasure')['r'], 0)
        self.assertEqual(self.proxy.progress_snapshot(), saved)

    def test_queued_special_period_switch_rejects_without_writing_either_period(self):
        self.original_reply('replySetChooseTreasure', [('Int', 'r'), ('Int', 't'), ('List', 'i')])
        for reliable in (False, True):
            with self.subTest(reliable=reliable):
                self.context['wish_id'] = 129
                saved = copy.deepcopy(self.proxy.progress_snapshot())
                self.locks.append('setChooseTreasure')
                self.queue('setChooseTreasure', {'t': 5, 'i': self.selected}, reliable, 18)
                self.context['wish_id'] = 128
                self.engine.drain()
                self.assertEqual(self.proxy.progress_snapshot(), saved)
                self.assertEqual(self.locks, [])
                self.assertEqual(next(v for n, v in reversed(self.owner.replies) if n == 'replySetChooseTreasure')['r'], 1882)
                self.assertTrue(self.messages)

    def test_same_reliable_sequence_in_another_wish_period_has_independent_receipt(self):
        for period in (129, 128):
            self.context['wish_id'] = period
            self.queue('setChooseTreasure', {'t': 5, 'i': self.selected}, True, 49); self.engine.drain()
        history = self.proxy.gacha_pools['special']['pools']['5']['ctr_by_wish']
        self.assertEqual(history['129'][:2], [129, self.selected])
        self.assertEqual(history['128'][:2], [128, self.selected])
        receipts = self.proxy.gacha_pools['special']['receipts']
        self.assertEqual(len({row['id'] for row in receipts}), 2)

    def test_owner_replacement_before_drain_never_commits_or_replies_to_new_owner(self):
        for name, args in (('requestLuckyDrawFurnitureCard', {'t': 106}), ('setChooseTreasure', {'t': 5, 'i': self.selected})):
            self.proxy.owner = self.owner; self.engine.avatar = self.owner
            saved = copy.deepcopy(self.proxy.progress_snapshot())
            self.owner.replies = []
            self.queue(name, args)
            replacement = SimpleNamespace()
            self.proxy.owner = replacement; self.engine.avatar = replacement
            self.engine.drain()
            self.assertEqual(self.proxy.progress_snapshot(), saved)
            self.assertEqual(self.owner.replies, [])

    def test_newer_special_request_keeps_lock_until_its_original_typed_reply(self):
        ui = self.original_counted_locks()
        self.original_reply('replySetChooseTreasure', [('Int', 'r'), ('Int', 't'), ('List', 'i')])
        self.original_choose_request(10)
        self.context['wish_id'] = 128
        self.original_choose_request(11)
        self.assertEqual(ui._lock, {'setChooseTreasure': 2})
        # Drain just the first logical scheduled work. The engine's scheduler
        # owns FIFO; observe its old source directly before the second runs.
        sources = self.proxy._gacha_operation_sources
        latest = sources['setChooseTreasure']
        seen_locks = []
        original = self.proxy.reject_stale_gacha_operation
        def observe(source):
            original(source); seen_locks.append(dict(ui._lock))
        with patch.object(self.proxy, 'reject_stale_gacha_operation', side_effect=observe):
            self.engine.drain()
        self.assertEqual(seen_locks, [{'setChooseTreasure': 1}])
        self.assertEqual(ui._lock, {'setChooseTreasure': 0})
        self.assertEqual(ui.recon_lock, 0)
        self.assertEqual(self.proxy.gacha_pools['special']['pools']['5']['ctr'][0], 128)
        self.assertIs(latest, sources['setChooseTreasure'])

    def test_replaced_panel_cancels_callback_and_completes_its_original_counted_lock(self):
        ui = self.original_counted_locks()
        saved = copy.deepcopy(self.proxy.progress_snapshot())
        self.original_friend_request(77)
        self.assertEqual(ui._lock, {'LuckyDrawFriendCard': 1})
        self.panel._node = object()
        self.engine.drain()
        self.assertEqual(self.proxy.progress_snapshot(), saved)
        self.assertNotIn(77, self.engine.avatar_callback_map)
        self.assertEqual(ui._lock, {'LuckyDrawFriendCard': 0})
        self.assertEqual(ui.recon_lock, 0)
        self.assertEqual(self.wait_events[-1], 'hide')
        self.assertFalse(self.owner.luckyDrawData.friend_draw)

    def test_reset_generation_keeps_new_original_lock_and_callback_untouched(self):
        ui = self.original_counted_locks()
        self.original_friend_request(77)
        old = self.proxy._gacha_operation_sources['requestLuckyDrawFriendCard']
        old_generation = ui._lock
        ui.reset_lock()
        self.original_friend_request(77)
        callback = self.engine.avatar_callback_map[77]
        self.assertIsNot(ui._lock, old_generation)
        self.proxy.reject_stale_gacha_operation(old)
        self.assertEqual(ui._lock, {'LuckyDrawFriendCard': 1})
        self.assertEqual(ui.recon_lock, 1)
        self.assertIs(self.engine.avatar_callback_map[77], callback)
        # Cancel the current request as well; only its new-generation lease
        # can remove its count. Queued repeats cannot release it twice.
        self.panel._node = object()
        saved = copy.deepcopy(self.proxy.progress_snapshot())
        self.engine.drain()
        self.assertEqual(ui._lock, {'LuckyDrawFriendCard': 0})
        self.assertEqual(ui.recon_lock, 0)
        self.assertEqual(self.proxy.progress_snapshot(), saved)

    def test_reliable_retry_without_another_original_lock_reuses_one_lease(self):
        ui = self.original_counted_locks()
        self.original_reply('replySetChooseTreasure', [('Int', 'r'), ('Int', 't'), ('List', 'i')])
        self.original_choose_request(73)
        source = self.proxy._gacha_operation_sources['setChooseTreasure']
        self.queue('setChooseTreasure', {'t': 5, 'i': self.selected}, True, 73)
        self.assertIs(source, self.proxy._gacha_operation_sources['setChooseTreasure'])
        self.assertEqual(ui._lock, {'setChooseTreasure': 1})
        self.engine.drain()
        self.assertEqual(ui._lock, {'setChooseTreasure': 0})
        self.assertEqual(ui.recon_lock, 0)
        self.assertEqual(len(self.proxy.gacha_pools['special']['receipts']), 1)
        self.assertEqual(sum(name == 'replySetChooseTreasure' for name, payload in self.owner.replies), 1)

    def test_reliable_retry_cannot_supersede_newer_ticket_or_double_release(self):
        ui = self.original_counted_locks()
        self.original_reply('replySetChooseTreasure', [('Int', 'r'), ('Int', 't'), ('List', 'i')])
        self.original_choose_request(10)
        old = self.proxy._gacha_operation_sources['setChooseTreasure']
        self.context['wish_id'] = 128
        self.original_choose_request(11)
        latest = self.proxy._gacha_operation_sources['setChooseTreasure']
        self.queue('setChooseTreasure', {'t': 5, 'i': self.selected}, True, 10)
        self.assertIs(self.proxy._gacha_operation_sources['setChooseTreasure'], latest)
        self.assertIsNot(old, latest)
        self.engine.drain()
        self.assertEqual(ui._lock, {'setChooseTreasure': 0})
        self.assertEqual(ui.recon_lock, 0)
        self.assertEqual(self.proxy.gacha_pools['special']['pools']['5']['ctr'][0], 128)

    def test_original_consumer_reentry_before_callback_reserves_both_real_locks(self):
        ui = self.original_counted_locks()
        self.original_reply('replyLuckyDrawFriendCard', [('Dict', 'r'), ('Bool', 'st')])
        opened, counts, leases = [], [], []
        def opened_card(info):
            opened.append(info)
            if len(opened) == 1:
                self.original_friend_request(78)
                latest = self.proxy._gacha_operation_sources['requestLuckyDrawFriendCard']
                leases.append(latest['lock_lease'])
                counts.append(ui._lock['LuckyDrawFriendCard'])
        ui.panels.card_open = SimpleNamespace(notify_scene_friend_card_open=opened_card)
        ui.panels.settlement_fullscreen = SimpleNamespace(check_gonglue_cache_result=lambda *args: None)
        self.original_friend_request(77)
        self.engine.drain()
        self.assertEqual(counts, [2])
        self.assertIsNotNone(leases[0])
        self.assertEqual(len(opened), 2)
        self.assertEqual(ui._lock, {'LuckyDrawFriendCard': 0})
        self.assertEqual(ui.recon_lock, 0)
        self.assertEqual(self.engine.avatar_callback_map, {})
        self.assertEqual(self.proxy.gacha_pools['pools']['99']['opened_total'], 2)

    def test_committed_notice_frame_change_preserves_one_result_and_truthful_notice(self):
        ui = self.original_counted_locks()
        self.original_reply('replyLuckyDrawFriendCard', [('Dict', 'r'), ('Bool', 'st')])
        base_reply = self.proxy.reply
        changed = []
        def notice(name, payload, callback_id=None):
            if not changed and not name.startswith('reply') and name != 'serverCallbackCarrier':
                self.assertTrue(self.proxy._gacha_operation_sources['requestLuckyDrawFriendCard']['canonical_result_saved'])
                self.panel._node = object()
                changed.append(name)
            return base_reply(name, payload, callback_id)
        self.original_friend_request(77)
        with patch.object(self.proxy, 'reply', side_effect=notice):
            self.engine.drain()
        self.assertTrue(changed)
        self.assertEqual(self.proxy.gacha_pools['pools']['99']['opened_total'], 1)
        saved = copy.deepcopy(self.proxy.progress_snapshot())
        self.assertEqual(ui._lock, {'LuckyDrawFriendCard': 0})
        self.assertEqual(ui.recon_lock, 0)
        self.assertTrue(any('\u7ed3\u679c\u5df2\u4fdd\u5b58' in message for message in self.messages))
        self.assertFalse(any('\u672a\u6267\u884c' in message for message in self.messages))
        self.assertFalse(any(name == 'replyLuckyDrawFriendCard' for name, payload in self.owner.replies))
        self.queue('requestLuckyDrawFriendCard', {}, callback=77)
        self.engine.drain()
        self.assertEqual(self.proxy.progress_snapshot(), saved)
        self.assertEqual(ui._lock, {'LuckyDrawFriendCard': 0})

    def test_committed_native_projection_error_completes_lease_and_retains_one_reward(self):
        ui = self.original_counted_locks()
        self.original_friend_request(77)
        with patch.object(self.proxy, 'native_gacha_card', side_effect=ValueError('native projection unavailable')):
            self.engine.drain()
        self.assertEqual(self.proxy.gacha_pools['pools']['99']['opened_total'], 1)
        self.assertEqual(ui._lock, {'LuckyDrawFriendCard': 0})
        self.assertEqual(ui.recon_lock, 0)
        self.assertEqual(self.engine.avatar_callback_map, {})
        self.assertTrue(any('\u7ed3\u679c\u5df2\u4fdd\u5b58' in message for message in self.messages))
        self.assertFalse(any('\u672a\u6267\u884c' in message for message in self.messages))
        self.assertFalse(any(name == 'replyLuckyDrawFriendCard' for name, payload in self.owner.replies))
        saved = copy.deepcopy(self.proxy.progress_snapshot())
        self.queue('requestLuckyDrawFriendCard', {}, callback=77)
        self.engine.drain()
        self.assertEqual(self.proxy.progress_snapshot(), saved)
        self.assertEqual(ui._lock, {'LuckyDrawFriendCard': 0})

    def test_callback_reuse_by_new_request_never_removes_or_invokes_new_callback(self):
        old = lambda *args: self.fail('obsolete callback invoked')
        new = lambda *args: self.fail('new callback invoked by old result')
        self.engine.avatar_callback_map[77] = old
        self.queue('requestLuckyDrawFurnitureCard', {'t': 106}, callback=77)
        self.engine.avatar_callback_map[77] = new
        saved = copy.deepcopy(self.proxy.progress_snapshot())
        self.engine.drain()
        self.assertIs(self.engine.avatar_callback_map[77], new)
        self.assertEqual(self.proxy.progress_snapshot(), saved)

    def test_dispatch_copies_mutable_arguments_before_queue(self):
        args = {'t': 5, 'i': self.selected}
        self.proxy.call_server_method('setChooseTreasure', args)
        args['t'], args['i'] = 354, -1
        self.engine.drain()
        self.assertEqual(self.proxy.gacha_pools['special']['pools']['5']['ctr'][1], self.selected)

    def test_original_friend_negative_changes_flag_but_stale_period_uses_only_carrier(self):
        namespace = {'gg': self.engine}
        body = original_definition(ORIGINAL, 'replyLuckyDrawFriendCard', namespace, decorated=False)
        body(self.owner, {}, False)
        self.assertTrue(self.owner.luckyDrawData.friend_draw)
        self.owner.luckyDrawData.friend_draw = False
        self.context = {'wire_t': 99, 'period': 1}
        self.engine.avatar_callback_map[88] = lambda *args: self.engine.ui.unlock('LuckyDrawFriendCard')
        self.original_reply('serverCallbackCarrier', [('Dict', '_r_')])
        self.locks.append('LuckyDrawFriendCard')
        self.queue('requestLuckyDrawFriendCard', {}, callback=88)
        self.context['period'] = 2
        saved = copy.deepcopy(self.proxy.progress_snapshot())
        self.engine.drain()
        self.assertEqual(self.locks, [])
        self.assertFalse(self.owner.luckyDrawData.friend_draw)
        self.assertEqual(self.proxy.progress_snapshot(), saved)
        self.assertFalse(any(name == 'replyLuckyDrawFriendCard' for name, _ in self.owner.replies))
        self.engine.avatar_callback_map[89] = lambda *args: self.engine.ui.unlock('LuckyDrawFriendCard')
        self.locks.append('LuckyDrawFriendCard')
        with patch.object(self.proxy._store, 'write', side_effect=OSError('disk full')):
            self.queue('requestLuckyDrawFriendCard', {}, callback=89)
            self.engine.drain()
        self.assertEqual(self.locks, [])
        self.assertFalse(self.owner.luckyDrawData.friend_draw)
        self.assertEqual(self.proxy.progress_snapshot(), saved)


# Reuse the original-data fixture without re-running the inherited suite here.
for _base in GachaRpcLifecycleTests.__mro__[1:]:
    for _name in vars(_base):
        if _name.startswith('test_') and _name not in vars(GachaRpcLifecycleTests):
            setattr(GachaRpcLifecycleTests, _name, None)

if __name__ == '__main__':
    unittest.main()
