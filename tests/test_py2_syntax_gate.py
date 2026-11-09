"""Py2 gate pin: every embedded source must compile on the game's 2.7 loader.

The startup overlay runs its embedded `project7_*.py` sources through the
game's own Python 2.7 `compile()`.  A source that is legal Python 3 but not
2.7 kills the whole overlay at import and shows up as a dead panel on device,
which host tests running on Python 3 never notice.  These tests pin both the
gate's verdicts and the fact that the loader routes through it.
"""
import _paths  # noqa: E402,F401
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'offline' / 'tools'))
sys.path.insert(0, str(ROOT / 'project7_bridge' / 'tools'))

from py2_syntax_gate import (Py2SyntaxError, check_sources,  # noqa: E402
                             check_source_file, find_py2_violations)
from forever7_paths import EMBEDDED_RUNTIME_SOURCES  # noqa: E402
import project7_script_hook  # noqa: E402


class EmbeddedSourcesTest(unittest.TestCase):
    def test_every_embedded_source_compiles_on_python27(self):
        sources = {name: (ROOT / path).read_text(encoding='ascii')
                   for name, path in EMBEDDED_RUNTIME_SOURCES.items()
                   if name.endswith('.py')}
        self.assertIn('project7_inventory_editor_ui.py', sources)
        check_sources(sources)

    def test_inventory_editor_source_is_gated(self):
        check_source_file(ROOT / EMBEDDED_RUNTIME_SOURCES['project7_inventory_editor_ui.py'])


class GateVerdictTest(unittest.TestCase):
    def test_positional_argument_after_star_unpacking_is_rejected(self):
        # Shipped on device: SyntaxError: only named arguments may follow
        # *expression in project7_inventory_editor_ui.py.
        problems = find_py2_violations(
            "def f(cc, pool):\n"
            "    return _text(cc, pool, 'x', *anchor_xy(), A, B)\n")
        self.assertTrue(problems)
        self.assertIn('positional argument after *unpacking', problems[0][1])

    def test_named_arguments_after_star_unpacking_are_accepted(self):
        self.assertEqual(find_py2_violations(
            "def f(cc, pool):\n"
            "    return _button(cc, pool, 'x', *anchor_xy(), width=1)\n"), [])

    def test_python3_only_constructs_are_rejected(self):
        cases = {
            'f(*a, *b)': '*unpacking',
            'f(**a, **b)': '**unpacking',
            'f(**a, k=1)': 'after **unpacking',
            'x = [*a]': 'unpacking',
            'x = {**a}': 'unpacking',
            'x = f"{a}"': 'f-strings',
            'x = 1_000': 'digit separators',
            'def g(a, *, b):\n    pass\n': 'keyword-only',
            'def g(a: int):\n    pass\n': 'annotations',
            'def g() -> int:\n    return 1\n': 'return annotations',
            'x: int = 1\n': 'variable annotations',
            'if (y := 1):\n    pass\n': 'assignment expressions',
            'x = a @ b\n': '@ operator',
            'raise A() from B()\n': 'raise ... from ...',
            'async def g():\n    await h()\n': 'async def',
        }
        for source, reason in cases.items():
            with self.subTest(source=source):
                problems = find_py2_violations(source)
                self.assertTrue(problems, source)
                self.assertIn(reason, ' '.join(text for _, text in problems))

    def test_python2_sources_pass(self):
        source = (
            "def f(cc, a, b, **kw):\n"
            "    items = [i for i in a]\n"
            "    return dict((k, v) for k, v in b.items())\n"
            "\n"
            "class C(object):\n"
            "    def __init__(self, value=None):\n"
            "        self.value = value\n"
            "    def __eq__(self, other):\n"
            "        return self.value == other.value\n"
        )
        self.assertEqual(find_py2_violations(source), [])

    def test_unparseable_source_fails_closed(self):
        self.assertTrue(find_py2_violations('def f(:\n'))

    def test_check_sources_names_every_offender(self):
        with self.assertRaises(Py2SyntaxError) as caught:
            check_sources({'a.py': 'x = 1_0\n', 'b.py': 'y = f"{z}"\n',
                           'c.py': 'x = 1\n'})
        message = str(caught.exception)
        self.assertIn('a.py', message)
        self.assertIn('b.py', message)
        self.assertNotIn('c.py', message)


class LoaderRoutingTest(unittest.TestCase):
    def test_loader_accepts_the_current_embedded_sources(self):
        sources = project7_script_hook._embedded_sources(ROOT)
        self.assertEqual(sorted(sources), sorted(project7_script_hook.EMBEDDED_SOURCES))

    def test_loader_raises_on_a_py3_only_embedded_source(self):
        bad = Path(tempfile.mkdtemp()) / 'project7_inventory_editor_ui.py'
        bad.write_text('x = f(*a, b)\n', encoding='ascii')
        real_path = project7_script_hook._embedded_path

        def patched(root, name):
            if name == 'project7_inventory_editor_ui.py':
                return bad
            return real_path(root, name)

        project7_script_hook._embedded_path = patched
        try:
            with self.assertRaises(Py2SyntaxError) as caught:
                project7_script_hook._embedded_sources(ROOT)
        finally:
            project7_script_hook._embedded_path = real_path
        self.assertIn('project7_inventory_editor_ui.py', str(caught.exception))
        self.assertIn('positional argument after *unpacking', str(caught.exception))


if __name__ == '__main__':
    unittest.main()
