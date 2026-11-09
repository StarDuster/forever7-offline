from pathlib import Path
import hashlib
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from project7_manager_hook import DATA, TARGET_SHA, apply_manager_hook


class Project7ManagerHookTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        path = ROOT / 'analysis/project7/official-build-inputs-v4/classes7.dex'
        cls.original = path.read_bytes() if path.is_file() else None

    def manager(self):
        if self.original is None:
            self.skipTest('Maintainer fixed component materialization absent')
        return self.original

    def test_unrecognized_manager_rejected_before_reading_patch(self):
        with self.assertRaisesRegex(ValueError, 'Unsupported'):
            apply_manager_hook(b'not the pinned manager', b'not read', b'not read')

    def test_patch_and_contract_tampering_rejected(self):
        original = self.manager()
        with self.assertRaisesRegex(ValueError, 'pin mismatch'):
            apply_manager_hook(original, b'bad patch')
        with self.assertRaisesRegex(ValueError, 'pin mismatch'):
            apply_manager_hook(original, contract=(DATA / 'contract.json').read_bytes() + b'\n')

    def test_exact_single_method_prefix_and_sdk_structure(self):
        original = self.manager()
        target, contract = apply_manager_hook(original)
        self.assertEqual(hashlib.sha256(target).hexdigest(), TARGET_SHA)
        self.assertEqual(contract['prefix_instructions'], 5)
        from loguru import logger
        logger.disable('androguard')
        from androguard.core.dex import DEX
        before, after = DEX(original), DEX(target)
        def methods(dex):
            return {(c.get_name(), m.get_name(), m.get_descriptor()):
                    (m.get_access_flags(), m.get_code().get_registers_size() if m.get_code() else None,
                     [(i.get_name(), i.get_output()) for i in m.get_instructions()])
                    for c in dex.get_classes() for m in c.get_methods()}
        old, new = methods(before), methods(after)
        self.assertEqual(set(old), set(new))
        self.assertEqual(len(old), 3700)
        changed = [key for key in old if old[key] != new[key]]
        expected = ('Lcom/project7/localmanager/LocalGatewayServer;', 'handleResourceRpc',
                    '(Ljava/io/OutputStream; [B [B [B Ljava/lang/String;)Z')
        self.assertEqual(changed, [expected])
        self.assertEqual(new[expected][:2], old[expected][:2])
        self.assertEqual(new[expected][2][5:], old[expected][2])
        self.assertEqual([name for name, output in new[expected][2][:5]],
                         ['invoke-static/range', 'move-result', 'if-eqz', 'const/4', 'return'])
        self.assertIn('CoreGapBridge;->handleResourceRpc', new[expected][2][0][1])
        self.assertEqual(new[expected][2][2][1], 'v0, +004h')
        tool = ROOT / 'toolchains/build-tools/android-37.0/dexdump'
        if tool.is_file():
            with tempfile.TemporaryDirectory() as directory:
                path = Path(directory) / 'classes7.dex'
                path.write_bytes(target)
                result = subprocess.run([str(tool), '-c', str(path)], capture_output=True, text=True)
                self.assertEqual(result.returncode, 0, result.stderr)
        with self.assertRaisesRegex(ValueError, 'Unsupported'):
            apply_manager_hook(target)


if __name__ == '__main__':
    unittest.main()
