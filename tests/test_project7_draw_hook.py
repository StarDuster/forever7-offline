"""Exact pinned DEX seam verification; no APK, VM or game execution."""
from pathlib import Path
import hashlib
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from project7_draw_hook import DATA, TARGET_SHA, apply_draw_hook


class DrawHookTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        path = ROOT / 'analysis/project7/one-command-repair-v3/project7-inputs-rv9qiqez/stage/classes7.dex'
        cls.source = path.read_bytes() if path.is_file() else None

    def baseline(self):
        if self.source is None:
            self.skipTest('Maintainer core-RPC manager baseline absent')
        return self.source

    def test_wrong_baseline_rejected_before_reading_any_patch(self):
        with self.assertRaisesRegex(ValueError, 'Unsupported'):
            apply_draw_hook(b'not-manager', b'bad', b'bad')

    def test_tampered_fixed_payload_rejected(self):
        source = self.baseline()
        with self.assertRaisesRegex(ValueError, 'pin mismatch'):
            apply_draw_hook(source, patch=b'bad')
        with self.assertRaisesRegex(ValueError, 'pin mismatch'):
            apply_draw_hook(source, contract=(DATA / 'contract.json').read_bytes() + b'\n')

    def test_only_three_calls_and_save_prefix_change(self):
        from loguru import logger
        logger.disable('androguard')
        from androguard.core.dex import DEX
        target, contract = apply_draw_hook(self.baseline())
        self.assertEqual(hashlib.sha256(target).hexdigest(), TARGET_SHA)
        def methods(blob):
            return {(c.get_name(), m.get_name(), m.get_descriptor()):
                    (m.get_access_flags(), m.get_code().get_registers_size() if m.get_code() else None,
                     [(i.get_name(), i.get_output()) for i in m.get_instructions()])
                    for c in DEX(blob).get_classes() for m in c.get_methods()}
        before, after = methods(self.baseline()), methods(target)
        added = set(after) - set(before)
        self.assertEqual(len(before), 3700)
        self.assertEqual(len(after), 3701)
        self.assertFalse(set(before) - set(after))
        self.assertEqual({key[1] for key in added}, {'q7OriginalTutorialCard'})
        changes = [key for key in before if before[key] != after[key]]
        self.assertEqual({key[1] for key in changes}, {'applyCurrent', 'saveState'})
        for key in changes:
            self.assertEqual(before[key][:2], after[key][:2])
            old, new = before[key][2], after[key][2]
            if key[1] == 'saveState':
                self.assertEqual(new[2:], old)
                self.assertIn('CoreDrawPolicy;->stateForSave', new[0][1])
                self.assertEqual(new[1], ('move-result-object', 'v12'))
            else:
                self.assertEqual(len(old), len(new))
                diff = [(a, b) for a, b in zip(old, new) if a != b]
                self.assertEqual(len(diff), 3)
                self.assertTrue(all(a[0] == b[0] == 'invoke-static' for a, b in diff))
                self.assertEqual([b[1].split('CoreDrawPolicy;->')[1].split('(')[0] for a, b in diff],
                                 ['makeFile', 'tutorialCandidate', 'reveal'])
        self.assertTrue(contract['original_resource_rpc_prefix_preserved'])
        with self.assertRaisesRegex(ValueError, 'Unsupported'):
            apply_draw_hook(target)


if __name__ == '__main__':
    unittest.main()
