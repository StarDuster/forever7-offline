"""Actual DEX identity, argument relocation and stock-cache control-flow proof."""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
PKG = 'Lcom/project7/localmanager/'


def methods(path):
    from loguru import logger
    logger.disable('androguard')
    from androguard.core.dex import DEX
    return {(c.get_name(), m.get_name(), m.get_descriptor()): m
            for c in DEX(path.read_bytes()).get_classes() for m in c.get_methods()}


def raw(method):
    return [(i.get_name(), i.get_output()) for i in method.get_instructions()]


class DreamHookTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        source = ROOT / 'analysis/project7/furniture-hook-v3/classes7.dex'
        target = ROOT / 'analysis/project7/dream-hook-v1/classes7.dex'
        if not source.exists() or not target.exists():
            raise unittest.SkipTest('Maintainer fixed source/target absent')
        cls.old, cls.new = methods(source), methods(target)

    def test_only_four_callers_changed_no_original_definitions_added(self):
        self.assertEqual(set(self.old), set(self.new))
        self.assertEqual(len(self.old), 3705)
        changes = []
        for key, old in self.old.items():
            new = self.new[key]
            self.assertEqual(old.get_access_flags(), new.get_access_flags())
            if raw(old) != raw(new):
                changes.append(key[1])
            elif old.get_code():
                self.assertEqual(old.get_code().get_registers_size(), new.get_code().get_registers_size())
        self.assertCountEqual(changes, ['handleServiceRpc', 'handleReliableRpc', 'handleCalendar', 'updateEconomy'])

    def test_same_shape_dispatch_and_store_calls(self):
        for name in ['handleServiceRpc', 'handleCalendar', 'updateEconomy']:
            owner = PKG + ('LocalProfileStore;' if name == 'updateEconomy' else 'LocalGatewayServer;')
            key = next(k for k in self.old if k[0] == owner and k[1] == name)
            old, new = raw(self.old[key]), raw(self.new[key])
            self.assertEqual(len(old), len(new))
            differences = [(a, b) for a, b in zip(old, new) if a != b]
            self.assertEqual(len(differences), 1, name)
            a, b = differences[0]
            if name == 'handleServiceRpc':
                self.assertEqual(a, (b[0], b[1].replace('OfflineMechanismGateway;', 'RequestEventGateway;')))
            elif name == 'updateEconomy':
                self.assertEqual(a, (b[0], b[1].replace('DreamEconomyPolicy;', 'LocalEconomyEngine;')))
            else:
                self.assertEqual(a[0], 'invoke-virtual')
                self.assertEqual(b[0], 'invoke-static')
                self.assertEqual(b[1].split(', ')[:3], a[1].split(', ')[:2] + ['v0'])
                self.assertIn('DreamEconomyPolicy;->refreshCalendarEngine(', b[1])

    def test_reliable_stock_cache_and_every_original_branch_preserved(self):
        from androguard.core.dex import Operand
        key = next(k for k in self.old if k[1] == 'handleReliableRpc')
        old_method, new_method = self.old[key], self.new[key]
        self.assertEqual(old_method.get_code().get_ins_size(), 11)
        self.assertEqual(new_method.get_code().get_ins_size(), 11)
        self.assertEqual(old_method.get_code().get_registers_size(), 48)
        self.assertEqual(new_method.get_code().get_registers_size(), 58)
        old, new = list(old_method.get_instructions()), list(new_method.get_instructions())
        expected = [('move-object/from16', 'v%d, v%d' % (37+i, 47+i)) for i in range(11)]
        self.assertEqual(raw(new_method)[:11], expected)
        originals = {}
        for name in ['begin', 'claim']:
            found = [i for i, op in enumerate(old) if 'LocalPatrolEngine;->' + name + '(' in op.get_output()]
            self.assertEqual(len(found), 1)
            pos = found[0]
            self.assertEqual(old[pos+1].get_name(), 'move-result-object')
            self.assertIn('->tutorialStore', old[pos+2].get_output())
            self.assertIn('LocalTutorialStore;->save(', old[pos+3].get_output())
            originals[name] = ((old[pos].get_name(), old[pos].get_output()),
                               (old[pos+3].get_name(), old[pos+3].get_output()))
        packs = {
            'begin': [('move-object/from16', 'v48, v0'), ('move-object/from16', 'v49, v1'),
                      ('move-object/from16', 'v50, v2'), ('move-object/from16', 'v51, v3'),
                      ('move/from16', 'v52, v4'), ('move-object/from16', 'v53, v5'),
                      ('move-object/from16', 'v54, v11'), ('move-object/from16', 'v55, v7')],
            'claim': [('move-object/from16', 'v48, v9'), ('move-object/from16', 'v49, v0'),
                      ('move-object/from16', 'v50, v11'), ('move-object/from16', 'v51, v7'),
                      ('move-object/from16', 'v52, v43')],
        }
        groups = {}
        for j, op in enumerate(new):
            for name, prefix in packs.items():
                if 'DreamPatrolGatewayHooks;->' + name + '(' in op.get_output():
                    self.assertEqual([(i.get_name(), i.get_output()) for i in new[j-len(prefix):j]], prefix)
                    groups[j-len(prefix)] = (j, name)
        self.assertEqual(len(groups), 2)
        records, actual_map = [], {i: 0 for i in range(11)}
        index, save_name, after_call = 11, None, 0
        while index < len(new):
            if index in groups:
                end, save_name = groups[index]
                for pos in range(index, end+1):
                    actual_map[pos] = len(records)
                name, text = originals[save_name][0]
                records.append((name, text, None))
                after_call = 2
                index = end+1
                continue
            op = new[index]; name, text = op.get_name(), op.get_output()
            actual_map[index] = len(records)
            if name.startswith(('if-', 'goto')):
                records.append((name, None, index))
            else:
                text = text.replace('OfflineMechanismGateway;', 'RequestEventGateway;')
                text = text.replace('DreamCoordinator;->hasPendingChoice', 'LocalPatrolEngine;->hasPendingChoice')
                text = text.replace('DreamCoordinator;->canResume', 'LocalPatrolEngine;->canResume')
                records.append((name, text, None))
            if after_call:
                if after_call == 2:
                    self.assertEqual((name, text), ('move-result-object', 'v0'))
                else:
                    self.assertEqual(name, 'iget-object')
                    self.assertIn('v1, v11, ' + PKG + 'LocalGatewayServer;->tutorialStore', text)
                after_call -= 1
                if not after_call:
                    restored = originals[save_name][1]
                    records.append((restored[0], restored[1], None))
            index += 1
        self.assertEqual(len(old), len(records))
        def offsets(seq):
            out = {}; pos = 0
            for j, op in enumerate(seq):
                out[pos] = j; pos += op.get_length()
            return out
        ao, bo = offsets(old), offsets(new)
        ap, bp = {v:k for k,v in ao.items()}, {v:k for k,v in bo.items()}
        for i, (name, text, branch) in enumerate(records):
            original = old[i]
            self.assertEqual(name.split('/')[0], original.get_name().split('/')[0])
            if branch is None:
                self.assertEqual(text, original.get_output())
            else:
                registers = lambda op: tuple(v[1] for v in op.get_operands() if v[0] == Operand.REGISTER)
                self.assertEqual(registers(original), registers(new[branch]))
                self.assertEqual(ao[ap[i]+2*original.get_ref_off()],
                                 actual_map[bo[bp[branch]+2*new[branch].get_ref_off()]])


if __name__ == '__main__':
    unittest.main()
