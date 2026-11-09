import _paths  # noqa: E402,F401
from pathlib import Path
import json
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'project7_bridge' / 'tools'))
from project7_compile import compile_sources, verify_stage


class Project7CompileTests(unittest.TestCase):
    def test_existing_compile_output_is_preserved_without_reading_inputs(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / 'existing'
            output.mkdir()
            (output / 'keep').write_bytes(b'keep')
            with self.assertRaisesRegex(ValueError, 'already exists'):
                compile_sources(Path('unused-stage'), output)
            self.assertEqual((output / 'keep').read_bytes(), b'keep')

    def test_rejects_an_incomplete_or_legacy_stage(self):
        with tempfile.TemporaryDirectory() as directory:
            stage = Path(directory)
            (stage / 'build-inputs.json').write_text(json.dumps({'backend': 'legacy'}))
            with self.assertRaisesRegex(ValueError, 'current Project7'):
                verify_stage(stage)

    def test_stage_inventory_traversal_is_rejected_before_access(self):
        with tempfile.TemporaryDirectory() as directory:
            stage = Path(directory)
            report = {'backend': 'project7', 'legacy_gateway_enabled': False,
                      'manager_core_rpc_prefix': True, 'minimum_android_api': 26,
                      'ordinary_draw_policy': True,
                      'beginner_new_groups_blocked': True,
                      'historical_draw_seams': True,
                      'request_event_dispatch': True,
                      'files': [{'path': '../outside', 'bytes': 1, 'sha256': '0' * 64}],
                      'generated_sources': []}
            (stage / 'build-inputs.json').write_text(json.dumps(report))
            with self.assertRaisesRegex(ValueError, 'Unsafe'):
                verify_stage(stage)


if __name__ == '__main__':
    unittest.main()
