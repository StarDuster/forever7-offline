"""Actual original zero-price no-op and scoped UI confirmation lifecycle."""
import copy
from pathlib import Path
import sys
import textwrap
from types import SimpleNamespace
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'runtime'))
import offline_gacha_ui as ui


class ZeroPriceWishTests(unittest.TestCase):
    def setUp(self):
        self.context = dict(wire_t=5, wish_id=1,
                            choice_cost_policy='offline-free-treasure-wish-selection-v1')
        self.wishes = {1: {'drawType': 5}, 2: {'drawType': 5}}
        self.confirmations, self.messages, self.calls, self.close_callbacks = [], [], [], []
        self.avatar = SimpleNamespace(yuanbao=0)
        self.panels = SimpleNamespace(
            common_confirm=SimpleNamespace(notify_confirm=lambda *args, **kw: self.confirmations.append((args, kw))),
            common_message=SimpleNamespace(notify_message=self.messages.append))
        source = (ROOT / 'analysis/native-mainline-delivery/activity_102_window.py').read_text()
        source = source[source.index('    def save_choice('):source.index('    def ue_filter_choose(')]
        namespace = {'cc': SimpleNamespace(ccui=SimpleNamespace(TOUCH_EVENT_ENDED=2)),
                     'gg': SimpleNamespace(avatar=self.avatar, ui=SimpleNamespace(panels=self.panels))}
        exec(textwrap.dedent(source), namespace)
        self.original = namespace['save_choice']
        self.item = SimpleNamespace(itemid=1025)
        self.window = SimpleNamespace(valid=True, cover=False, yuanbao=0,
            _f7_free_wish_period=1, _f7_wish_show_token=1,
            chooseList=['new'], chooseListBak=['old'], item_container={'new': self.item})
        self.window.clickConfirm = lambda items: self.calls.append(('original-validator', items)) or True
        self.window.window_close = self.close_callbacks.append
        self.window.proc_event = lambda event, items: self.calls.append(('parent-event', event, items))
        self.window.remove_from_parent = lambda: self.calls.append(('remove',))
        self.save = ui.make_free_wish_window_save(self.original, lambda: self.context,
            self.wishes, 2, lambda: self.avatar, lambda: self.panels)

    def confirm(self):
        self.confirmations[-1][0][1]()

    def test_original_zero_price_body_noops_but_hook_reaches_original_confirm_close_chain(self):
        self.original(self.window, None, 2)
        self.assertEqual(self.confirmations, [])
        self.assertEqual(self.calls, [])
        self.save(self.window, None, 2)
        args, kwargs = self.confirmations[0]
        self.assertEqual(args[0], 1886)
        self.assertEqual(kwargs, {'text_args': (0,)})
        self.assertEqual(self.calls, [])
        self.confirm()
        self.assertEqual(self.calls, [('original-validator', [self.item])])
        self.assertTrue(self.window.cover)
        self.save(self.window, None, 2)  # Closing animation consumes further touches.
        self.assertEqual(len(self.confirmations), 1)
        self.close_callbacks[0]()
        self.assertEqual(self.calls[1:], [('parent-event', 'treasure_select_list', [self.item]), ('remove',)])
        self.assertFalse(self.window.cover)
        self.confirm()
        self.close_callbacks[0]()
        self.assertEqual(len(self.calls), 3)
        self.assertEqual(self.avatar.yuanbao, 0)

    def test_empty_unchanged_missing_and_original_validator_rejection_do_not_send(self):
        self.window.chooseList = []
        self.save(self.window, None, 2)
        self.assertEqual(self.messages, [1887])
        self.window.chooseList = ['old']
        self.save(self.window, None, 2)
        self.assertEqual(self.messages, [1887, 1884])
        self.window.chooseList = ['missing']
        self.save(self.window, None, 2)
        self.confirm()
        self.assertEqual(self.messages[-1], 1883)
        self.assertEqual(self.calls, [])
        self.window.chooseList = ['new']
        self.window.clickConfirm = lambda items: False
        self.save(self.window, None, 2)
        self.confirm()
        self.assertEqual(self.close_callbacks, [])
        self.assertEqual(self.calls, [])

    def test_paid_and_other_scopes_keep_real_original_behavior(self):
        self.window.yuanbao = 100
        self.avatar.yuanbao = 100
        self.save(self.window, None, 2)
        self.assertEqual(self.confirmations[-1][1], {'text_args': (100,)})
        self.window.yuanbao = 0
        self.context['wire_t'] = 99
        before = len(self.confirmations)
        self.save(self.window, None, 2)
        self.assertEqual(len(self.confirmations), before)
        self.context['wire_t'] = 5
        self.window._f7_free_wish_period = 2
        self.save(self.window, None, 2)
        self.assertEqual(len(self.confirmations), before)

    def test_no_ended_touch_or_cancel_has_no_business_side_effect(self):
        self.save(self.window, None, 0)
        self.assertEqual(self.confirmations, [])
        before = copy.deepcopy(vars(self.avatar))
        self.save(self.window, None, 2)
        # Dismissing the original common_confirm never invokes its confirm CB.
        self.assertEqual(self.calls, [])
        self.assertEqual(self.close_callbacks, [])
        self.assertEqual(vars(self.avatar), before)

    def test_stale_confirm_is_retired_on_avatar_period_show_or_selection_change(self):
        for change in ('avatar', 'period', 'show', 'selection', 'destroyed'):
            with self.subTest(change=change):
                self.setUp()
                self.save(self.window, None, 2)
                if change == 'avatar': self.avatar = SimpleNamespace(yuanbao=0)
                elif change == 'period': self.context['wish_id'] = 2
                elif change == 'show': self.window._f7_wish_show_token += 1
                elif change == 'selection': self.window.chooseList = ['different']
                else: self.window.valid = False
                self.confirm()
                self.assertEqual(self.calls, [])
                self.assertEqual(self.close_callbacks, [])

    def test_stale_close_does_not_clear_reused_windows_cover_or_fire_parent(self):
        self.save(self.window, None, 2)
        self.confirm()
        self.window._f7_wish_show_token += 1
        self.close_callbacks[0]()
        self.assertTrue(self.window.cover)
        self.assertEqual(self.calls, [('original-validator', [self.item])])

    def test_destroyed_during_close_does_not_fire_parent_selection(self):
        self.save(self.window, None, 2)
        self.confirm()
        self.window.valid = False
        self.close_callbacks[0]()
        self.assertEqual(self.calls, [('original-validator', [self.item])])
        self.assertFalse(self.window.cover)
        self.close_callbacks[0]()
        self.assertEqual(self.calls, [('original-validator', [self.item])])


if __name__ == '__main__':
    unittest.main()
