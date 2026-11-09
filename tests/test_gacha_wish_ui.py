"""Free historical target selection must preserve stock validation and wallets."""
import copy
from pathlib import Path
import sys
from types import ModuleType, SimpleNamespace
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'runtime'))
import offline_gacha_ui as ui


class WishSelectionUiTests(unittest.TestCase):
    def setUp(self):
        self.context = {'wire_t': 5, 'wish_id': 14,
                        'choice_cost_policy': 'offline-free-treasure-wish-selection-v1'}
        self.wishes = {14: {'drawType': 5}, 15: {'drawType': 5}, 99: {'drawType': 1}}
        self.provider = lambda wire=None: self.context

    def test_original_modal_sees_zero_and_reused_other_modal_keeps_its_price(self):
        calls, prices = [], []
        panel = SimpleNamespace(price_num=SimpleNamespace(
            setVisible=lambda value: prices.append(('visible', value)),
            setString=lambda value: prices.append(('text', value))))
        refresh = ui.make_free_wish_window_refresh(
            lambda owner: prices.append(('original', owner.yuanbao)), self.provider, self.wishes)
        def original(owner, *args, **kwargs):
            owner.yuanbao = kwargs['yuanbao']
            calls.append((args, kwargs))
            refresh(owner)
            return 'shown'
        show = ui.make_free_wish_window_show(original, self.provider, self.wishes)
        kwargs = {'type': 'treasure_wish', 'yuanbao': 200, 'chooseList': [1234]}
        before = copy.deepcopy(kwargs)
        self.assertEqual(show(panel, 'original-arg', **kwargs), 'shown')
        self.assertEqual(kwargs, before)
        self.assertEqual(calls[0], (('original-arg',), dict(kwargs, yuanbao=0)))
        self.assertEqual(prices, [('original', 0), ('visible', True), ('text', '0')])
        prices[:] = []
        show(panel, type='other_shop', yuanbao=300)
        self.assertEqual(panel.yuanbao, 300)
        self.assertIsNone(panel._f7_free_wish_period)
        self.assertEqual(prices, [('original', 300)])

    def test_validation_only_waives_insufficient_funds_after_original_item_checks(self):
        player = SimpleNamespace(yuanbao=0)
        calls = []
        def original(owner, wire, item):
            calls.append((wire, item))
            return {100: 1883, 101: 1884, 102: 1882}.get(item, 1885)
        valid = ui.make_free_wish_validation(original, self.provider, self.wishes)
        for item, expected in [(100, 1883), (101, 1884), (102, 1882), (103, 0)]:
            self.assertEqual(valid(player, 5, item), expected)
        self.assertEqual(player.yuanbao, 0)
        self.assertEqual(len(calls), 4)
        self.assertEqual(valid(player, 1, 103), 1885)

    def test_missing_or_mismatched_period_never_enables_free_policy(self):
        valid = ui.make_free_wish_validation(lambda *args: 1885, self.provider, self.wishes)
        original_context = copy.deepcopy(self.context)
        for context in [None, {}, {'wire_t': 5, 'wish_id': 14},
                        dict(original_context, wish_id=99),
                        dict(original_context, wish_id=999),
                        dict(original_context, wire_t=354)]:
            self.context = context
            self.assertEqual(valid(object(), 5, 103), 1885)

    def test_refresh_marker_cannot_leak_across_period_or_archive_exit(self):
        prices = []
        panel = SimpleNamespace(_f7_free_wish_period=14, price_num=SimpleNamespace(
            setVisible=lambda value: prices.append(value),
            setString=lambda value: prices.append(value)))
        refresh = ui.make_free_wish_window_refresh(lambda owner: 'stock', self.provider, self.wishes)
        self.context['wish_id'] = 15
        self.assertEqual(refresh(panel), 'stock')
        self.assertEqual(prices, [])
        self.context = None
        self.assertEqual(refresh(panel), 'stock')
        self.assertEqual(prices, [])

    def test_installer_wires_existing_avatar_and_modal_once(self):
        modules = {}
        for name in ('cocos.panels.activity_102_window',
                     'com.data.cdata.chouka_treasure_wish', 'entity.ClientAvatar'):
            parts = name.split('.')
            for count in range(1, len(parts) + 1):
                key = '.'.join(parts[:count])
                if key not in modules:
                    modules[key] = ModuleType(key)
                    modules[key].__path__ = []
                if count > 1:
                    setattr(modules['.'.join(parts[:count-1])], parts[count-1], modules[key])
        modal = type('Panel', (), {'notify_show': lambda owner, **kw: kw,
                                  'refresh': lambda owner: None,
                                  'save_choice': lambda owner, sender, event: None})
        avatar = type('Avatar', (), {'validSetChooseTreasure': lambda *args: 1885})
        modules['cocos.panels.activity_102_window'].Panel = modal
        modules['entity.ClientAvatar'].ClientAvatar = avatar
        modules['com.data.cdata.chouka_treasure_wish'].data = self.wishes
        modules['gg'] = SimpleNamespace(avatar=avatar(), ui=SimpleNamespace(panels=SimpleNamespace()))
        modules['cocosui'] = SimpleNamespace(ccui=SimpleNamespace(TOUCH_EVENT_ENDED=2))
        with patch.dict(sys.modules, modules), patch.object(
                ui, 'offline_archive_context', self.provider, create=True):
            ui.install_treasure_wish_free_ui()
            installed = avatar.validSetChooseTreasure
            ui.install_treasure_wish_free_ui()
            self.assertIs(avatar.validSetChooseTreasure, installed)
            self.assertEqual(avatar().validSetChooseTreasure(5, 103), 0)
            self.assertEqual(modal().notify_show(type='treasure_wish', yuanbao=100)['yuanbao'], 0)


if __name__ == '__main__':
    unittest.main()
