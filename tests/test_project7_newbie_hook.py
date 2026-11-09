"""One new-group invoke changes; no APK or engine/game execution."""
from pathlib import Path
import hashlib
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from project7_newbie_hook import DATA, TARGET_SHA, apply_newbie_hook


class NewbieBlockHookTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        path = ROOT / 'analysis/project7/draw-policy-hook-v1/classes7.dex'
        cls.source = path.read_bytes() if path.is_file() else None

    def baseline(self):
        if self.source is None:
            self.skipTest('Maintainer ordinary-policy manager baseline absent')
        return self.source

    def test_wrong_baseline_fails_without_reading_component(self):
        with self.assertRaisesRegex(ValueError, 'Unsupported'):
            apply_newbie_hook(b'bad source', b'bad patch', b'bad contract')

    def test_tampering_fails(self):
        with self.assertRaisesRegex(ValueError, 'pin mismatch'):
            apply_newbie_hook(self.baseline(), patch=b'bad patch')
        with self.assertRaisesRegex(ValueError, 'pin mismatch'):
            apply_newbie_hook(self.baseline(), contract=(DATA / 'contract.json').read_bytes() + b'\n')

    def test_exact_single_invoke_preserves_all_other_method_instructions(self):
        from loguru import logger
        logger.disable('androguard')
        from androguard.core.dex import DEX
        target, contract = apply_newbie_hook(self.baseline())
        self.assertEqual(hashlib.sha256(target).hexdigest(), TARGET_SHA)
        def methods(blob):
            return {(c.get_name(), m.get_name(), m.get_descriptor()):
                    (m.get_access_flags(), m.get_code().get_registers_size() if m.get_code() else None,
                     [(i.get_name(), i.get_output()) for i in m.get_instructions()])
                    for c in DEX(blob).get_classes() for m in c.get_methods()}
        before, after = methods(self.baseline()), methods(target)
        self.assertEqual(set(before), set(after))
        self.assertEqual(len(before), 3701)
        changes = [key for key in before if before[key] != after[key]]
        self.assertEqual(len(changes), 1)
        key = changes[0]
        self.assertEqual(key[1], 'applyCurrent')
        self.assertEqual(before[key][:2], after[key][:2])
        old, new = before[key][2], after[key][2]
        self.assertEqual(len(old), len(new))
        diff = [(a, b) for a, b in zip(old, new) if a != b]
        self.assertEqual(len(diff), 1)
        self.assertEqual(diff[0][0][0], 'invoke-static')
        self.assertEqual(diff[0][1][0], 'invoke-static')
        self.assertIn('v8, v2, v3, Lcom/project7/localmanager/LocalNewbieDrawEngine;->makeFile', diff[0][0][1])
        self.assertIn('v8, v2, v3, Lcom/project7/localmanager/CoreDrawPolicy;->newbieFile', diff[0][1][1])
        self.assertTrue(contract['resume_reveal_quit_unchanged'])
        self.assertTrue(contract['no_faked_ct'])
        with self.assertRaisesRegex(ValueError, 'Unsupported'):
            apply_newbie_hook(target)


if __name__ == '__main__':
    unittest.main()
