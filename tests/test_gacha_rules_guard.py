"""Run original rule-button body with missing historical rule references."""
from pathlib import Path
import sys
from types import SimpleNamespace as NS
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'runtime'))
from offline_gacha_ui import make_gacha_rule_guard
from test_offline_rpc_rejections import original_definition


class OriginalRuleGuardTests(unittest.TestCase):
    def test_missing_rule_is_reported_before_original_layer_creation(self):
        self._exercise_original_button('card_tab.py')

    def test_card_box_rule_button_has_the_same_missing_reference_guard(self):
        self._exercise_original_button('card_box.py')

    def _exercise_original_button(self, filename):
        layers, messages, rendered = [], [], []
        cc = NS(ccui=NS(TOUCH_EVENT_ENDED=2))
        gg = NS(ui=NS(panels=NS(treasure_rules=object())))
        original = original_definition(ROOT / 'analysis/research-agent' / filename,
            'on_rule_click', {'cc': cc, 'gg': gg}, decorated=False)
        table = {17: object()}
        def show(event, **kwargs):
            rendered.append(table[kwargs['info']])
        panel = NS(can_show_rule=lambda: 615,
            add_layer=lambda value: layers.append(value), proc_event=show)
        with self.assertRaises(KeyError):
            original(panel, None, 2)
        layers.clear()
        guarded = make_gacha_rule_guard(original, table, messages.append)
        with patch.dict(sys.modules, {'cc': cc}):
            guarded(panel, None, 0)
            self.assertEqual(messages, [])
            guarded(panel, None, 2)
            self.assertEqual(len(messages), 1)
            self.assertEqual(layers, [])
            panel.can_show_rule = lambda: 17
            guarded(panel, None, 2)
        self.assertEqual(rendered, [table[17]])
        self.assertEqual(len(layers), 1)


if __name__ == '__main__':
    unittest.main()
