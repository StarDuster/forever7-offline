from pathlib import Path
import sys
from types import ModuleType, SimpleNamespace
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'runtime'))
import offline_gacha_ui as ui


class FreeGachaHookTests(unittest.TestCase):
    def test_zero_balance_keeps_file_state_guards_and_other_pools_unchanged(self):
        modules = {}
        for name in ('com.const', 'entity.avatar_attrs.LuckyDrawData',
                     'cocos.panels.card_box', 'cocos.panels.common_confirm_3', 'cocos.panels.card_tab'):
            parts = name.split('.')
            for count in range(1, len(parts) + 1):
                key = '.'.join(parts[:count])
                if key not in modules:
                    modules[key] = ModuleType(key)
                    modules[key].__path__ = []
                if count > 1:
                    setattr(modules['.'.join(parts[:count-1])], parts[count-1], modules[key])
        modules['com.const'].LuckyDrawType = SimpleNamespace(NORMAL=1)
        modules['com.const'].VirtualItem = SimpleNamespace(SUMMONCOIN=42)
        cls = type('LuckyDrawData', (), {'is_open': False,
                    'getIsOpenCard': lambda self, pool: self.is_open})
        names = ('canOpenFile', 'checkFileAndOpenAllCost', 'canOpenCard', 'checkLeftAllCardsCost',
                 'canOpenCardByConsume', 'checkFileAndOpenAllCostByConsume',
                 'checkLeftAllCardsCostByConsume', 'getOpenConsume', 'getOpenConsumeWithoutFree',
                 'getLuckyDrawConsume')
        def original(self, pool, *args, **kwargs):
            return ('original', pool, args, kwargs)
        for name in names:
            setattr(cls, name, original)
        modules['entity.avatar_attrs.LuckyDrawData'].LuckyDrawData = cls
        modules['cocos.panels.card_box'].Panel = type('Panel', (), {
            '_do_init_card_info': lambda *args: None, 'on_rule_click': lambda *args: None,
            'notify_open_file': lambda *args: None})
        modules['cocos.panels.common_confirm_3'].Panel = type('Panel', (), {
            'notify_confirm': lambda *args, **kwargs: None})
        modules['cocos.panels.card_tab'].Panel = type('Tab', (), {'_on_open_go_click': lambda self: 'entered'})
        ui._f7_log = lambda message: None
        with patch.dict(sys.modules, modules):
            ui.install_gacha_ui()
            ui.install_gacha_ui()  # Idempotent install must not stack wrappers.
        tab = modules['cocos.panels.card_tab'].Panel()
        tab.draw_type, tab.cover = 354, True
        self.assertIsNone(tab._on_open_go_click())
        self.assertFalse(tab.cover)
        tab.draw_type = 1
        sync_wires=[]
        with patch.dict(sys.modules,{'gg':SimpleNamespace(_f7_avatar_proxy=SimpleNamespace(sync_gacha_native_state=lambda wire,**kwargs:sync_wires.append((wire,kwargs))))}):
            self.assertEqual(tab._on_open_go_click(), 'entered')
        self.assertEqual(sync_wires,[(1,{'refresh_cards':True})])
        player = cls()
        self.assertFalse(player.isNewbieLuckyAvailable())
        self.assertFalse(ui.is_local_gacha_pool(354))
        self.assertTrue(player.canOpenFile(1))
        self.assertFalse(player.canOpenCard(1))
        player.is_open = True
        self.assertFalse(player.canOpenFile(1))
        self.assertFalse(player.checkFileAndOpenAllCost(1))
        self.assertTrue(player.canOpenCard(1))
        self.assertEqual(player.getOpenConsume(1), 0)
        self.assertEqual(player.getLuckyDrawConsume(1), [(42, 0)])
        for name in names:
            self.assertEqual(getattr(player, name)(77, 'argument', only_draw_coin=True),
                             ('original', 77, ('argument',), {'only_draw_coin': True}))

    def test_reused_card_panel_does_not_cover_charging_orb_with_old_card_hit_boxes(self):
        visible = []
        panel = SimpleNamespace(scene_type='normal', auto_scroll=True,
                                item_box_panel=SimpleNamespace(setVisible=visible.append))
        panel.model_card_auto_scroll = lambda value: setattr(panel, 'auto_scroll', value)
        phases = []
        wrapped = ui.make_gacha_open_file_hook(lambda self, enable: phases.append(enable))
        wrapped(panel, False)
        self.assertFalse(panel.auto_scroll)
        self.assertEqual(visible, [False])
        wrapped(panel, True)
        self.assertTrue(panel.auto_scroll)
        self.assertEqual(phases, [False, True])

    def test_activity_charging_pauses_old_item_updater_and_restores_original_flag(self):
        for initial in (True,False):
            visible=[];events=[]
            panel=SimpleNamespace(scene_type='activity',auto_scroll=initial,item_box_panel=SimpleNamespace(setVisible=visible.append))
            panel.model_card_auto_scroll=lambda value:setattr(panel,'auto_scroll',value)
            def original(owner,enable):
                events.append((enable,owner.auto_scroll))
                owner.item_box_panel.setVisible(True)
                return 'original-result'
            wrapped=ui.make_gacha_open_file_hook(original)
            self.assertEqual(wrapped(panel,False),'original-result')
            wrapped(panel,False)
            self.assertFalse(panel.auto_scroll);self.assertEqual(visible,[True,False,True,False])
            wrapped(panel,True)
            self.assertEqual(panel.auto_scroll,initial)
            self.assertFalse(hasattr(panel,'_f7_previous_auto_scroll'))
            self.assertEqual(events,[(False,False),(False,False),(True,False)])
    def test_friend_newfriend_furniture_charging_keeps_original_behavior(self):
        for scene in ('friend','newfriend','furniture'):
            visible=[];scroll=[];events=[]
            panel=SimpleNamespace(scene_type=scene,auto_scroll=True,item_box_panel=SimpleNamespace(setVisible=visible.append),model_card_auto_scroll=scroll.append)
            wrapped=ui.make_gacha_open_file_hook(lambda owner,enable:events.append(enable))
            wrapped(panel,False);wrapped(panel,True)
            self.assertEqual(events,[False,True]);self.assertEqual(visible,[]);self.assertEqual(scroll,[])
            self.assertTrue(panel.auto_scroll);self.assertFalse(hasattr(panel,'_f7_previous_auto_scroll'))


if __name__ == '__main__':
    unittest.main()

class GachaEntryFailureTests(unittest.TestCase):
    def test_failed_entry_releases_cover_and_preserves_original_notification(self):
        panel = SimpleNamespace(valid=True, cover=True)
        requests, messages = [], []
        def original(owner, kind, success, failure):
            requests.append((success, failure))
        guarded = ui.make_gacha_entry_switch_guard(original, lambda: panel, 'friendsummon')
        success = lambda: None
        guarded(object(), 'friendsummon', success, messages.append)
        self.assertIs(requests[0][0], success)
        requests[0][1]('Unavailable')
        self.assertFalse(panel.cover)
        self.assertEqual(messages, ['Unavailable'])

    def test_old_failure_cannot_uncover_a_newer_entry(self):
        panel = SimpleNamespace(valid=True, cover=True)
        pending = []
        guarded = ui.make_gacha_entry_switch_guard(
            lambda owner, kind, success, failure: pending.append(failure),
            lambda: panel, 'friendsummon')
        guarded(object(), 'friendsummon', lambda: None)
        guarded(object(), 'friendsummon', lambda: None)
        pending[0]('Old failure')
        self.assertTrue(panel.cover)
        pending[1]('Current failure')
        self.assertFalse(panel.cover)

class FriendCurrencyPresentationTests(unittest.TestCase):
    def test_money_only_uses_original_single_animation_then_currency_settlement(self):
        calls = []
        result = {'money': 10000, 'hero_frag': {}, 'get_hero': False}
        panel = SimpleNamespace(notify_show_friend_lianchou=lambda rows, preview: calls.append(('settlement', rows, preview)))
        def animate(owner, payload, callback):
            self.assertIs(owner, panel)
            self.assertEqual(payload, dict(result, friendCard=True))
            calls.append(('single_animation',))
            callback()
        wrapped = ui.make_friend_currency_display_hook(lambda *args: self.fail('Unsupported blank panel used'), animate)
        wrapped(panel, result)
        self.assertEqual(calls, [('single_animation',), ('settlement', [dict(result, friendCard=True)], False)])
        self.assertEqual(result, {'money': 10000, 'hero_frag': {}, 'get_hero': False})

    def test_hero_and_item_singles_keep_original_presentation(self):
        seen = []
        wrapped = ui.make_friend_currency_display_hook(lambda owner, result: seen.append(result),
            lambda *args: self.fail('Normal result incorrectly rerouted'))
        for result in ({'hero': [7]}, {'item': [[54, 1]], 'money': 100}, {}):
            wrapped(None, result)
        self.assertEqual(len(seen), 3)
        self.assertTrue(all(result['friendCard'] for result in seen))
