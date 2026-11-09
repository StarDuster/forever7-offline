"""Regression for client_event_compat re-exec during a live wait_reward owner."""
import unittest

from tests.test_event_continuation_locks import COMPAT, Install, _exec


class ReinjectTests(unittest.TestCase):
    def test_same_globals_reexec_keeps_old_live_owner(self):
        fixture = Install()
        fixture.reply()
        self.assertEqual(fixture.locks(), 1)
        old_echo = fixture.avatar.echoes[0]['callback']
        _exec(COMPAT, fixture.namespace)
        old_echo({'e': None})
        self.assertEqual(fixture.locks(), 0)
        self.assertEqual(fixture.avatar.scenes, [4007])

    def test_version_marker_is_seven_after_reinject(self):
        fixture = Install()
        namespace = _exec(COMPAT, {})
        self.assertEqual(namespace['Q7_CLIENT_EVENT_COMPAT_VERSION'], 7)
        self.assertEqual(fixture.gg._q7_wait_reward_registry_v5['version'], 7)

    def test_old_record_without_whole_event_field_does_not_release_unknown_reference(self):
        fixture = Install()
        fixture.gg.logic.event_semaphore['wholeEvent'] = 1
        old = {'phase': 'created', 'lock': False, 'token': None, 'since': 0}
        fixture.avatar._q7_settlement_continuations = {4007: old}
        fixture.namespace['_q7_cancel_continuation'](fixture.avatar, 4007, 'retried')
        self.assertEqual(fixture.gg.logic.event_semaphore['wholeEvent'], 1)

    def test_new_globals_reexec_does_not_duplicate_settlement(self):
        fixture = Install()
        fixture.reply()
        old_echo = fixture.avatar.echoes[0]['callback']
        _exec(COMPAT, {})
        fixture.reply(cbid=1002)
        self.assertEqual(fixture.locks(), 1)
        old_echo({'e': None})
        self.assertEqual(fixture.locks(), 0)
        self.assertEqual(len(fixture.avatar.echoes), 1)

    def test_legacy_untracked_record_is_not_globally_cleared(self):
        fixture = Install()
        fixture.ui.lock('wait_reward')
        fixture.avatar._q7_settlement_continuations = {4007: {'lock': True, 'token': None}}
        released = fixture.namespace['_q7_release_wait_reward'](fixture.avatar._q7_settlement_continuations[4007])
        self.assertFalse(released)
        self.assertEqual(fixture.locks(), 1)

    def test_first_install_with_legacy_lock_does_not_clear_it(self):
        fixture = Install()
        delattr(fixture.gg, '_q7_wait_reward_registry_v5')
        fixture.ui.lock('wait_reward')
        _exec(COMPAT, {})
        self.assertEqual(fixture.locks(), 1)

    def test_acquire_on_legacy_lock_does_not_steal_or_clear_it(self):
        fixture = Install()
        delattr(fixture.gg, '_q7_wait_reward_registry_v5')
        fixture.ui.lock('wait_reward')
        _exec(COMPAT, {})
        self.assertEqual(fixture.locks(), 1)
        fixture.reply()
        self.assertEqual(fixture.locks(), 2)
        fixture.fire_echo()
        self.assertEqual(fixture.locks(), 1)

    def test_old_avatar_echo_after_reexec_and_new_owner_does_not_release_new(self):
        fixture = Install()
        fixture.reply()
        old_echo = fixture.avatar.echoes[0]['callback']
        _exec(COMPAT, {})
        replacement = fixture.avatar_class(fixture.gg)
        fixture.gg.avatar = replacement
        replacement.completeEventDialog(4007)
        self.assertEqual(fixture.locks(), 1)
        old_echo({'e': None})
        self.assertEqual(fixture.locks(), 1)
        replacement.echoes[0]['callback']({'e': None})
        self.assertEqual(fixture.locks(), 0)

    def test_legacy_lock_plus_owner_transfer_uses_one_owned_reference(self):
        fixture = Install()
        delattr(fixture.gg, '_q7_wait_reward_registry_v5')
        fixture.ui.lock('wait_reward')
        _exec(COMPAT, {})
        fixture.reply()
        self.assertEqual(fixture.locks(), 2)
        old_echo = fixture.avatar.echoes[0]['callback']
        replacement = fixture.avatar_class(fixture.gg)
        fixture.gg.avatar = replacement
        replacement.completeEventDialog(4007)
        self.assertEqual(fixture.locks(), 2)
        old_echo({'e': None})
        self.assertEqual(fixture.locks(), 2)
        replacement.echoes[0]['callback']({'e': None})
        self.assertEqual(fixture.locks(), 1)

if __name__ == '__main__':
    unittest.main()
