"""Loader/clean ordering pin for the inventory editor.

The full game bootstrap is Root/native; this finite test proves the generated
loader binds activation after clean and that bind_startup itself does not
import gg/ClientAvatar before the mature clean returns.
"""
import _paths  # noqa: E402,F401
import importlib.util
import sys
import types
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'offline' / 'current' / 'tools'))


def load_editor():
    spec = importlib.util.spec_from_file_location(
        'inventory_loader_ui', ROOT / 'offline/current/runtime/project7_inventory_editor_ui.py')
    editor = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(editor)
    return editor


class LoaderLifecycleTest(unittest.TestCase):
    def test_loader_binds_after_clean_and_before_original_start(self):
        from project7_script_hook import embedded_loader
        loader = embedded_loader()
        bind = loader.index("_p7_editor_namespace['bind_startup']")
        start = loader.index('_f7_original_start()')
        self.assertLess(bind, start)
        self.assertNotIn("_p7_inventory_ui = _p7_namespace['install']()", loader)
        self.assertIn('project7_inventory_editor_ui.py', loader)

    def test_bind_has_no_game_import_before_clean(self):
        editor = load_editor()
        calls = []
        original = editor.install
        editor.install = lambda: calls.append('install')
        try:
            class Patch(object):
                def __init__(self):
                    self.clean = lambda state: state
            patch = Patch()
            editor.bind_startup(patch, types.SimpleNamespace(live=lambda: True))
            self.assertEqual(calls, [])
            self.assertNotIn('gg', sys.modules)
            self.assertNotIn('entity.ClientAvatar', sys.modules)
            patch.clean(False)
            self.assertEqual(calls, [])
            patch.clean(True)
            self.assertEqual(calls, ['install'])
        finally:
            editor.install = original

    def test_failed_clean_does_not_install(self):
        editor = load_editor()
        calls = []
        original = editor.install
        editor.install = lambda: calls.append('install')
        try:
            class Patch(object):
                def __init__(self):
                    self.clean = self.fail
                def fail(self, state):
                    raise RuntimeError('clean failed')
            patch = Patch()
            editor.bind_startup(patch, types.SimpleNamespace(live=lambda: True))
            with self.assertRaises(RuntimeError):
                patch.clean(True)
            self.assertEqual(calls, [])
        finally:
            editor.install = original


if __name__ == '__main__':
    unittest.main(verbosity=2)
