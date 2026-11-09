"""Compare actual fixed DEX bodies/control flow; never assemble an APK."""
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]
HOME = 'Lcom/project7/localmanager/LocalHomeEngine;'
POLICY = 'Lcom/project7/localmanager/HistoryFurniturePolicy;'


def methods(path):
    from loguru import logger
    logger.disable('androguard')
    from androguard.core.dex import DEX
    return {(c.get_name(), m.get_name(), m.get_descriptor()): m
            for c in DEX(path.read_bytes()).get_classes() for m in c.get_methods()}


def raw(method):
    return [(i.get_name(), i.get_output()) for i in method.get_instructions()]


class FurnitureHookTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        source = ROOT / 'analysis/project7/request-event-hook-v1/classes7.dex'
        target = ROOT / 'analysis/project7/furniture-hook-v3/classes7.dex'
        if not source.exists() or not target.exists():
            raise unittest.SkipTest('Maintainer fixed source/target absent')
        cls.before, cls.after = methods(source), methods(target)

    def test_only_two_reviewed_methods_and_two_exact_original_bridges(self):
        self.assertEqual(len(self.before), 3703)
        self.assertEqual(len(self.after), 3705)
        added = set(self.after) - set(self.before)
        self.assertEqual({(k[0], k[1]) for k in added},
                         {(HOME, 'q7OriginalChoose'), (HOME, 'q7OriginalSkinCopies')})
        changed = []
        for key, old in self.before.items():
            new = self.after[key]
            self.assertEqual(old.get_access_flags(), new.get_access_flags())
            if raw(old) != raw(new):
                changed.append(key)
            elif old.get_code():
                self.assertEqual(old.get_code().get_registers_size(), new.get_code().get_registers_size())
        self.assertEqual({(k[0], k[1]) for k in changed}, {(HOME, 'draw'), (HOME, 'apply')})
        for key in added:
            method = self.after[key]
            self.assertEqual(method.get_access_flags(), 0x1009)
            code = raw(method)
            name = key[1].replace('q7Original', '')
            original = name[:1].lower() + name[1:]
            self.assertIn(HOME + '->' + original + '(', code[0][1])
            if original == 'choose':
                self.assertEqual([n for n, _ in code], ['invoke-static', 'move-result-object', 'return-object'])
                self.assertEqual(method.get_code().get_registers_size(), 2)
            else:
                self.assertEqual([n for n, _ in code], ['invoke-static/range', 'return-void'])
                self.assertEqual(method.get_code().get_registers_size(), 6)

    def test_open_check_keeps_every_other_original_instruction(self):
        key = next(k for k in self.before if k[0] == HOME and k[1] == 'apply' and 'Random;' in k[2])
        old, new = raw(self.before[key]), raw(self.after[key])
        self.assertEqual(self.before[key].get_code().get_registers_size(), 45)
        self.assertEqual(self.after[key].get_code().get_registers_size(), 45)
        diff = [(a, b) for a, b in zip(old, new) if a != b]
        self.assertEqual(len(old), len(new))
        self.assertEqual(len(diff), 1)
        self.assertEqual(diff[0][0][0], 'invoke-static')
        self.assertEqual(diff[0][0][1], diff[0][1][1].replace(POLICY + '->poolRule', HOME + '->rule'))

    def test_original_draw_awards_order_and_branch_targets_survive_remap(self):
        from androguard.core.dex import Operand
        key = next(k for k in self.before if k[0] == HOME and k[1] == 'draw')
        old_method, new_method = self.before[key], self.after[key]
        self.assertEqual(old_method.get_code().get_registers_size(), 39)
        self.assertEqual(new_method.get_code().get_registers_size(), 46)
        old, new = list(old_method.get_instructions()), list(new_method.get_instructions())
        # Lease the old params register only after its unique original read.
        refs = [i for i in old if any(v[0] == Operand.REGISTER and v[1] == 35 for v in i.get_operands())]
        self.assertEqual([(i.get_name(), i.get_output()) for i in refs], [('move-object/from16', 'v4, v35')])
        old_raw = raw(old_method)
        def original_call(fragment, prefix=None):
            found = [(n, s) for n, s in old_raw if fragment in s and (prefix is None or s.startswith(prefix))]
            self.assertEqual(len(found), 1, fragment)
            return found[0]
        calls = {'poolRule': original_call(HOME + '->rule('),
                 'defaultRow': original_call('LocalFeatureCatalog;->get('),
                 'chooseOuter': original_call(HOME + '->choose(', 'v3,'),
                 'chooseInner': original_call(HOME + '->choose(', 'v6,'),
                 'skinCopies': original_call(HOME + '->skinCopies('),
                 'reward': original_call('LocalResourceEngine$Result;->reward(')}
        packs = {
            'defaultRow': [('move-object/from16', 'v31, v1'), ('move-object/from16', 'v32, v6'),
                           ('move-object/from16', 'v33, v12'), ('move/from16', 'v34, v19')],
            'chooseOuter': [('move-object/from16', 'v31, v3'), ('move-object/from16', 'v32, v2'), ('move/from16', 'v33, v19')],
            'chooseInner': [('move-object/from16', 'v31, v6'), ('move-object/from16', 'v32, v2'), ('move/from16', 'v33, v19')],
            'skinCopies': [('move-object/from16', 'v31, v22'), ('move-object/from16', 'v32, v23'),
                           ('move/from16', 'v33, v24'), ('move/from16', 'v34, v25'),
                           ('move-wide/from16', 'v35, v26'), ('move/from16', 'v37, v19')],
            'reward': [('move-object/from16', 'v31, v12'), ('move/from16', 'v32, v19'), ('move-object/from16', 'v33, v42')],
        }
        groups = {}
        for index, op in enumerate(new):
            for name, prefix in packs.items():
                if POLICY + '->' + name + '(' in op.get_output():
                    start = index - len(prefix)
                    self.assertEqual([(x.get_name(), x.get_output()) for x in new[start:index]], prefix)
                    self.assertEqual(op.get_name(), 'invoke-static/range')
                    groups[start] = (index, calls[name])
        self.assertEqual(len(groups), 5)
        records, actual_to_record = [], {}
        def restore_register(number):
            value = int(number.group(1))
            self.assertFalse(31 <= value <= 37, 'Scratch word escaped into original instruction')
            return 'v' + str(value - 7 if value >= 38 else value)
        index = 0
        saved_selection = 0
        while index < len(new):
            if index in groups:
                end, restored = groups[index]
                for i in range(index, end + 1):
                    actual_to_record[i] = len(records)
                records.append((restored[0], restored[1], None, None))
                index = end + 1
                continue
            op = new[index]; name, text = op.get_name(), op.get_output()
            if name == 'move-object/from16' and text == 'v42, v6':
                self.assertEqual((new[index-1].get_name(), new[index-1].get_output()), ('move-result-object', 'v6'))
                self.assertIn(POLICY + '->chooseInner(', new[index-2].get_output())
                actual_to_record[index] = len(records) - 1
                saved_selection += 1
                index += 1
                continue
            if POLICY + '->acceptsPool(' in text:
                self.assertEqual(text.split(',')[0], 'v4')
                self.assertEqual([(i.get_name(), i.get_output().split(',')[0]) for i in new[index+1:index+3]],
                                 [('move-result', 'v9'), ('if-eqz', 'v9')])
                actual_to_record[index] = actual_to_record[index+1] = len(records)
                records.append(('const/16', 'v9, 162', None, None))
                actual_to_record[index+2] = len(records)
                records.append(('if-ne', None, index+2, (4, 9)))
                index += 3
                continue
            actual_to_record[index] = len(records)
            if name.startswith(('if-', 'goto')):
                registers = tuple(v[1] - 7 if v[1] >= 38 else v[1]
                                  for v in op.get_operands() if v[0] == Operand.REGISTER)
                records.append((name, None, index, registers))
            else:
                text = re.sub(r'\bv(\d+)\b', restore_register, text)
                text = text.replace(POLICY + '->poolRule', HOME + '->rule')
                text = text.replace('该配送池尚未开放或角色等级不足。', '仅常驻都市配送已接入')
                records.append((name, text, None, None))
            index += 1
        self.assertEqual(len(old), len(records))
        self.assertEqual(saved_selection, 1)
        def offsets(seq):
            pos = {}; offset = 0
            for j, op in enumerate(seq):
                pos[offset] = j; offset += op.get_length()
            return pos
        before_offsets, after_offsets = offsets(old), offsets(new)
        old_position = {v:k for k,v in before_offsets.items()}
        new_position = {v:k for k,v in after_offsets.items()}
        for old_index, (name, text, branch, registers) in enumerate(records):
            original = old[old_index]
            self.assertEqual(original.get_name().split('/')[0], name.split('/')[0])
            if branch is None:
                self.assertEqual(original.get_output(), text)
                continue
            old_regs = tuple(v[1] for v in original.get_operands() if v[0] == Operand.REGISTER)
            self.assertEqual(old_regs, registers)
            old_dest = before_offsets[old_position[old_index] + original.get_ref_off()*2]
            new_dest = after_offsets[new_position[branch] + new[branch].get_ref_off()*2]
            self.assertEqual(old_dest, actual_to_record[new_dest])


if __name__ == '__main__':
    unittest.main()
