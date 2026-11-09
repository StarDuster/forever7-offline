"""User-facing set/add buttons must dispatch the matching resource operation."""
import _paths  # noqa: E402,F401
import importlib.util
from pathlib import Path
import sys
import types
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]

class InventoryActionsTest(unittest.TestCase):
    def setUp(self):
        spec = importlib.util.spec_from_file_location('inventory_actions', ROOT / 'offline/current/runtime/project7_inventory_editor_ui.py')
        self.editor = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.editor)
        self.sent = []
        self.editor._send = self.sent.append
        self.editor._VIEW.update({'count': types.SimpleNamespace(getString=lambda: '2'),
                                  'quality': types.SimpleNamespace(getString=lambda: '3'), 'quality_value': 3})
        self.fake = patch.dict(sys.modules, {'gg': types.ModuleType('gg')})
        self.fake.start()
        self.addCleanup(self.fake.stop)

    def select(self, row):
        self.editor._VIEW.update({'selected': row, 'rows': [row], 'catalog_loading': False, 'group': row['k'], 'selected_token': (self.editor._VIEW.get('ui_epoch'), self.editor._VIEW.get('catalog_generation'))})

    def test_visible_add_button_generates_treasure_instances(self):
        self.select({'k': 'treasure', 'i': 100})
        self.editor._apply('add')
        self.assertEqual(self.sent, [[{'k': 'treasure', 'i': 100, 'm': 'create', 'n': 2, 'q': 3}]])

    def test_item_and_currency_buttons_keep_their_modes(self):
        self.select({'k': 'item', 'i': 1})
        self.editor._apply('add')
        self.select({'k': 'currency', 'c': 'summonCoin'})
        self.editor._apply('set')
        self.assertEqual(self.sent, [[{'k': 'item', 'i': 1, 'm': 'add', 'n': 2}],
                                     [{'k': 'currency', 'c': 'summonCoin', 'm': 'set', 'n': 2}]])

    def test_currency_row_uses_display_name(self):
        label = self.editor._row_name({'k': 'currency', 'c': 'money', 'name': 'Coins', 'n': 12})
        self.assertIn('Coins', label)
        self.assertNotIn('money', label)
        self.assertNotIn('money', self.editor._row_meta({'k': 'currency', 'c': 'money'}))

if __name__ == '__main__':
    unittest.main(verbosity=2)
