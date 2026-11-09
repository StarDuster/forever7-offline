"""Checks for the Project7 manager dispatch-table extractor."""
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
import manager_gateway_coverage as coverage  # noqa: E402


class ManagerCoverageTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.base = Path(self.temporary.name)

    def tearDown(self):
        self.temporary.cleanup()

    def _write(self, name, text):
        path = self.base / (name + '.dis')
        path.write_text(text, encoding='utf-8')
        return path

    def test_methods_field_and_inline_digest_tables_are_distinguished(self):
        self._write('EngineRegistered', (
            'METHOD <clinit>()V\n'
            'const-string v0, "alpha"\n'
            'const-string v1, "beta"\n'
            'filled-new-array/range v0 ... v1, [Ljava/lang/String;\n'
            'move-result-object v0\n'
            'sput-object v0, Lcom/x/EngineRegistered;->METHODS [Ljava/lang/String;\n'))
        self._write('EngineInline', (
            'METHOD <clinit>()V\n'
            'const-string v16, "gamma"\n'
            'filled-new-array/range v16 ... v16, [Ljava/lang/String;\n'
            'move-result-object v7\n'
            'invoke-static v8, Lcom/x/EngineInline;->digest(Ljava/lang/String;)[B\n'))
        self._write('EngineFilter', (
            'METHOD m()Z\n'
            'const-string v1, "delta"\n'
            'filled-new-array/range v1 ... v1, [Ljava/lang/String;\n'
            'move-result-object v0\n'
            'invoke-static v0, Ljava/util/Arrays;->asList([Ljava/lang/Object;)Ljava/util/List;\n'
            'invoke-interface v0, v8, Ljava/util/List;->contains(Ljava/lang/Object;)Z\n'))
        engines = coverage.scan(self.base, {'alpha', 'beta', 'gamma', 'delta'})
        self.assertEqual(engines['EngineRegistered']['strong'], ['alpha', 'beta'])
        self.assertIn('gamma', engines['EngineInline']['strong'])
        self.assertIn('delta', engines['EngineFilter']['mentioned'])
        self.assertNotIn('delta', engines['EngineFilter']['strong'])

    def test_client_name_filter_ignores_non_request_literals(self):
        self._write('EngineRegistered', (
            'METHOD <clinit>()V\n'
            'const-string v0, "alpha"\n'
            'const-string v1, "Project7Gateway"\n'
            'filled-new-array/range v0 ... v1, [Ljava/lang/String;\n'
            'move-result-object v0\n'
            'sput-object v0, Lcom/x/EngineRegistered;->METHODS [Ljava/lang/String;\n'))
        engines = coverage.scan(self.base, {'alpha'})
        self.assertEqual(engines['EngineRegistered']['tables'][0]['names'], ['alpha'])


if __name__ == '__main__':
    unittest.main()
