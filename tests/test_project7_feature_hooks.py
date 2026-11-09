"""Reviewed binary seams: preserve stock dispatch/control flow, no APK/device."""
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from project7_feature_hooks import PINS, apply_feature_hook, sha


def methods(blob):
    from loguru import logger
    logger.disable('androguard')
    from androguard.core.dex import DEX
    return {(c.get_name(), m.get_name(), m.get_descriptor()): m
            for c in DEX(blob).get_classes() for m in c.get_methods()}


def instructions(method):
    return [(i.get_name(), i.get_output()) for i in method.get_instructions()]


class FeatureHookTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        path = ROOT / 'analysis/project7/newbie354-hook-v1/classes7.dex'
        if not path.is_file():
            raise unittest.SkipTest('Maintainer source DEX absent')
        cls.base = path.read_bytes()
        cls.history, cls.history_contract = apply_feature_hook(cls.base, 'history')
        cls.target, cls.request_contract = apply_feature_hook(cls.history, 'request_events')

    def test_exact_chain_and_no_reapplication(self):
        self.assertEqual(sha(self.history), PINS['history']['target'])
        self.assertEqual(sha(self.target), PINS['request_events']['target'])
        for blob, feature in ((self.history, 'history'), (self.target, 'request_events'),
                              (self.base, 'request_events')):
            with self.assertRaisesRegex(ValueError, 'Unsupported'):
                apply_feature_hook(blob, feature)

    def test_tampering_is_rejected(self):
        for source, feature in ((self.base, 'history'), (self.history, 'request_events')):
            with self.assertRaisesRegex(ValueError, 'pin mismatch'):
                apply_feature_hook(source, feature, patch=b'bad')
            with self.assertRaisesRegex(ValueError, 'pin mismatch'):
                apply_feature_hook(source, feature, contract=b'{}')

    def test_new_furniture_dream_chain_is_exact_and_rejects_wrong_base(self):
        furniture, _ = apply_feature_hook(self.target, 'furniture')
        dream, _ = apply_feature_hook(furniture, 'dream')
        self.assertEqual(sha(furniture), PINS['furniture']['target'])
        self.assertEqual(sha(dream), PINS['dream']['target'])
        lifecycle, _ = apply_feature_hook(dream, 'dream_lifecycle')
        self.assertEqual(sha(lifecycle), PINS['dream_lifecycle']['target'])
        event_reset, _ = apply_feature_hook(lifecycle, 'event_reset_week')
        self.assertEqual(sha(event_reset), PINS['event_reset_week']['target'])
        selector, _ = apply_feature_hook(event_reset, 'selector')
        self.assertEqual(sha(selector), PINS['selector']['target'])
        reliable, _ = apply_feature_hook(selector, 'reliable_scope')
        self.assertEqual(sha(reliable), PINS['reliable_scope']['target'])
        story, _ = apply_feature_hook(reliable, 'story_missions')
        self.assertEqual(sha(story), PINS['story_missions']['target'])
        trial, _ = apply_feature_hook(story, 'trial_retry')
        self.assertEqual(sha(trial), PINS['trial_retry']['target'])
        for source in (reliable, trial):
            with self.assertRaisesRegex(ValueError, 'Unsupported'):
                apply_feature_hook(source, 'trial_retry')
        for part in ('patch', 'contract'):
            with self.assertRaisesRegex(ValueError, 'pin mismatch'):
                apply_feature_hook(story, 'trial_retry', **{part: b'bad'})
        with self.assertRaisesRegex(ValueError, 'Unsupported'):
            apply_feature_hook(selector, 'story_missions')
        for part in ('patch', 'contract'):
            with self.assertRaisesRegex(ValueError, 'pin mismatch'):
                apply_feature_hook(reliable, 'story_missions', **{part: b'bad'})
        for source in (event_reset, reliable):
            with self.assertRaisesRegex(ValueError, 'Unsupported'):
                apply_feature_hook(source, 'reliable_scope')
        for part in ('patch', 'contract'):
            with self.assertRaisesRegex(ValueError, 'pin mismatch'):
                apply_feature_hook(selector, 'reliable_scope', **{part: b'bad'})
        with self.assertRaisesRegex(ValueError, 'Unsupported'):
            apply_feature_hook(lifecycle, 'selector')
        for feature, source in [('furniture', furniture), ('dream', self.target), ('dream', dream)]:
            with self.assertRaisesRegex(ValueError,'Unsupported'):
                apply_feature_hook(source, feature)
        for feature, source in [('furniture',self.target), ('dream',furniture)]:
            with self.assertRaisesRegex(ValueError,'pin mismatch'):
                apply_feature_hook(source, feature, patch=b'bad')

    def test_request_prefixes_preserve_every_original_instruction(self):
        before, after = methods(self.history), methods(self.target)
        self.assertEqual(set(before), set(after))
        self.assertEqual(len(before), 3703)
        changed = []
        for key, old_method in before.items():
            new_method = after[key]
            self.assertEqual(old_method.get_access_flags(), new_method.get_access_flags())
            if old_method.get_code():
                self.assertEqual(old_method.get_code().get_registers_size(),
                                 new_method.get_code().get_registers_size())
            old, new = instructions(old_method), instructions(new_method)
            if old == new:
                continue
            changed.append(key[1])
            self.assertEqual(key[0], 'Lcom/project7/localmanager/LocalGatewayServer;')
            if key[1] == 'handleServiceRpc':
                self.assertEqual([n for n, _ in new[:4]],
                                 ['invoke-static/range', 'move-result', 'if-eqz', 'return'])
                self.assertIn('v34 ... v41, Lcom/project7/localmanager/RequestEventGateway;->handleDirect', new[0][1])
                self.assertEqual(old, new[4:])
            else:
                self.assertEqual(key[1], 'handleReliableRpc')
                at = next(i for i, (_, s) in enumerate(new)
                          if 'RequestEventGateway;->handleRequest' in s)
                added = new[at-9:at+4]
                self.assertEqual(len(added), 13)
                self.assertTrue(all(n == 'move-object/from16' for n, _ in added[:9]))
                self.assertEqual([n for n, _ in added[9:]],
                                 ['invoke-static/range', 'move-result', 'if-eqz', 'return-void'])
                self.assertIn('->writeFrame', new[at-10][1])
                self.assertIn('reliableRpcAck', str(new[:at-10]))
                self.assertEqual(old, new[:at-9] + new[at+4:])
        self.assertCountEqual(changed, ['handleServiceRpc', 'handleReliableRpc'])

    def test_history_changes_are_scoped_and_keep_branch_destinations(self):
        before, after = methods(self.base), methods(self.history)
        added = set(after) - set(before)
        self.assertEqual(len(added), 2)
        self.assertEqual({(k[0].split('/')[-1], k[1]) for k in added},
                         {('LocalResourceCatalog$Pool;', '<init>'), ('LocalDrawEngine;', 'q7OriginalSpend')})
        changed = []
        for key, original in before.items():
            current = after[key]
            self.assertEqual(original.get_access_flags(), current.get_access_flags())
            if original.get_code():
                self.assertEqual(original.get_code().get_registers_size(), current.get_code().get_registers_size())
            old, new = instructions(original), instructions(current)
            if old == new:
                continue
            changed.append((key[0].split('/')[-1], key[1]))
            if key[1] == '<init>':
                i = next(i for i, (_, s) in enumerate(new) if 'HistoryDrawPolicy;->augmentCatalog' in s)
                self.assertEqual(new[i+1][0], 'return-void')
                self.assertEqual(old, new[:i] + new[i+1:])
            elif key[1] == 'saveState':
                self.assertEqual(old, [(n, s.replace('HistoryDrawPolicy;->stateForSave', 'CoreDrawPolicy;->stateForSave')) for n, s in new])
            else:
                self.assertEqual(key[1], 'applyCurrent')
                guard = next(i for i, (_, s) in enumerate(new) if 'HistoryDrawPolicy;->requiresStockChoice' in s)
                self.assertEqual(new[guard-1][0], 'if-eqz')
                self.assertEqual([n for n, _ in new[guard:guard+3]], ['invoke-static', 'move-result', 'if-eqz'])
                kept = [i for i in range(len(new)) if i not in range(guard, guard+3)]
                old_ins = list(original.get_instructions()); new_ins = list(current.get_instructions())
                def offsets(ins):
                    result = {}; offset = 0
                    for index, op in enumerate(ins):
                        result[offset] = index; offset += op.get_length()
                    return result
                old_offsets, new_offsets = offsets(old_ins), offsets(new_ins)
                old_positions = {i: off for off, i in old_offsets.items()}
                new_positions = {i: off for off, i in new_offsets.items()}
                map_back = {new_i: old_i for old_i, new_i in enumerate(kept)}
                self.assertEqual(len(old_ins), len(kept))
                for old_i, new_i in enumerate(kept):
                    a, b = old_ins[old_i], new_ins[new_i]
                    self.assertEqual(a.get_name(), b.get_name())
                    if a.get_name().startswith(('if-', 'goto')):
                        old_dest = old_offsets[old_positions[old_i] + 2*a.get_ref_off()]
                        new_dest = new_offsets[new_positions[new_i] + 2*b.get_ref_off()]
                        self.assertEqual(old_dest, map_back[new_dest])
                    else:
                        expected = b.get_output().replace('HistoryDrawPolicy;->spend', 'LocalDrawEngine;->spend').replace('HistoryDrawPolicy;->makeFile', 'LocalDrawEngine;->makeActivityFile').replace('HistoryDrawPolicy;->reveal', 'CoreDrawPolicy;->reveal')
                        self.assertEqual(a.get_output(), expected)
                null_guard_dest = new_offsets[new_positions[guard-1] + 2*new_ins[guard-1].get_ref_off()]
                history_guard_dest = new_offsets[new_positions[guard+2] + 2*new_ins[guard+2].get_ref_off()]
                self.assertEqual(null_guard_dest, history_guard_dest)
        self.assertCountEqual(changed, [('LocalResourceCatalog;', '<init>'),
                                       ('LocalDrawEngine;', 'applyCurrent'),
                                       ('LocalDrawEngine;', 'saveState')])


if __name__ == '__main__':
    unittest.main()
