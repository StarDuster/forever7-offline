"""Contract checks for the corpus x runtime RPC cross-reference tool."""
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
import rpc_cross_reference as xref  # noqa: E402


class CrossReferenceTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.base = Path(self.temporary.name)

    def tearDown(self):
        self.temporary.cleanup()

    def _write(self, relative, text):
        path = self.base / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding='utf-8')
        return path

    def test_multiline_call_keeps_callback_and_its_line(self):
        self._write('corpus/entity/Member.py', (
            'class Member(object):\n'
            '    def _on_done(self, result):\n'
            '        pass\n'
            '\n'
            '    def go(self):\n'
            '        self.callServerMethod("alpha", {"a": 1},\n'
            '                              callback=self._on_done)\n'
            '\n'
            '    def go_seq(self):\n'
            '        self.callServerMethodSeq("beta", {})\n'))
        files, requests, replies = xref.corpus_index([self.base / 'corpus'])
        self.assertEqual(len(files), 1)
        alpha = requests['alpha'][0]
        self.assertEqual(alpha['callback'], 'self._on_done')
        self.assertEqual(alpha['callback_line'], 2)
        self.assertEqual(alpha['scope'], 'Member.go')
        self.assertIsNone(requests['beta'][0]['callback'])

    def test_reply_handlers_are_indexed_separately_from_requests(self):
        self._write('corpus/entity/Member.py', (
            'class Member(object):\n'
            '    def replyAlpha(self, result):\n'
            '        pass\n'
            '\n'
            '    def ask(self):\n'
            '        self.callServerMethod("alpha", {})\n'))
        _, requests, replies = xref.corpus_index([self.base / 'corpus'])
        self.assertIn('replyAlpha', replies)
        self.assertNotIn('replyAlpha', requests)

    def test_runtime_dispatch_registration_and_rejection_precedence(self):
        self._write('runtime/gateway.py', (
            'BETA = frozenset(("beta", "gamma"))\n'
            '\n'
            'def handle(name, parameters):\n'
            '    if name == "alpha":\n'
            '        pass\n'
            '    elif name in BETA:\n'
            '        pass\n'))
        self._write('runtime/other.py', (
            'TABLE = {"delta": 1}\n'
            'NOTE = "epsilon"\n'))
        rejection = self._write('runtime/rejections.py', (
            'RPC_TYPED_REJECTION_OPERATIONS = frozenset(("beta",))\n'
            'RPC_REJECTION_OPERATIONS = RPC_TYPED_REJECTION_OPERATIONS\n'))
        dispatch, registered, mentioned, unparsed = xref.runtime_index(self.base / 'runtime')
        import ast
        rejected = {}
        for label, values in xref._module_string_sets(
                ast.parse(rejection.read_text(encoding='utf-8'))).items():
            if label.startswith('RPC_') and 'REJECTION' in label:
                for value in values:
                    rejected[value] = ['runtime/rejections.py:%s' % label]
        self.assertEqual(unparsed, [])
        self.assertEqual(xref._classify('alpha', dispatch, registered, mentioned, rejected)[0], 'handled')
        self.assertEqual(xref._classify('beta', dispatch, registered, mentioned, rejected)[0], 'rejected')
        self.assertEqual(xref._classify('gamma', dispatch, registered, mentioned, rejected)[0], 'registered')
        self.assertEqual(xref._classify('delta', dispatch, registered, mentioned, rejected)[0], 'registered')
        self.assertEqual(xref._classify('epsilon', dispatch, registered, mentioned, rejected)[0], 'mentioned_only')
        self.assertEqual(xref._classify('zeta', dispatch, registered, mentioned, rejected)[0], 'unhandled')

    def test_python2_bootstrap_keeps_literals_visible(self):
        self._write('runtime/bootstrap.py', (
            'try:\n'
            '    exec _code in globals()\n'
            'except:\n'
            '    pass\n'
            'if name == "eta":\n'
            '    NOTE = "theta"\n'))
        dispatch, registered, mentioned, unparsed = xref.runtime_index(self.base / 'runtime')
        self.assertEqual(len(unparsed), 1)
        self.assertTrue(unparsed[0].endswith('runtime/bootstrap.py'))
        self.assertIn('eta', dispatch)
        self.assertIn('theta', mentioned)

    def test_log_evidence_counts_only_unimplemented_lines(self):
        self._write('logs/a.log', (
            '1793609486.4 RPC UNIMPLEMENTED enterPlace\n'
            '1793609486.5 RPC enterPlace {}\n'
            '1793609486.6 RPC UNIMPLEMENTED enterPlace\n'))
        observed = xref.log_evidence([self.base / 'logs'])
        self.assertEqual(observed['enterPlace']['count'], 2)
        self.assertEqual(len(observed['enterPlace']['files']), 1)


if __name__ == '__main__':
    unittest.main()
