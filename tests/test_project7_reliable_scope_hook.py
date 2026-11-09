"""One reliable call receives its original sequence and connection identity.

Checks actual rewritten DEX, including branch and exception target preservation.
This is not an APK, ART, or business implementation acceptance test.
"""
import _paths  # noqa: E402,F401
from pathlib import Path
import unittest
from test_project7_dream_hook import methods, raw, PKG

ROOT = Path(__file__).resolve().parents[1]


def offsets(ops):
    positions, pos = {}, 0
    for index, op in enumerate(ops):
        positions[pos] = index
        pos += op.get_length()
    positions[pos] = len(ops)
    return positions


class ReliableScopeHookTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        source = ROOT / 'analysis/project7/selector-hook-v1/classes7.dex'
        target = ROOT / 'analysis/project7/reliable-scope-hook-v1/classes7.dex'
        if not source.exists() or not target.exists():
            raise unittest.SkipTest('Maintainer fixed source/target absent')
        cls.old, cls.new = methods(source), methods(target)
        cls.key = next(k for k in cls.old if k[:2] == (PKG+'LocalGatewayServer;', 'handleReliableRpc'))

    def test_only_reliable_body_changes_no_definitions_or_registers_added(self):
        self.assertEqual(set(self.old), set(self.new))
        self.assertEqual(len(self.old), 3705)
        changed = []
        for key, old in self.old.items():
            new = self.new[key]
            self.assertEqual(old.get_access_flags(), new.get_access_flags())
            if old.get_code():
                self.assertEqual(old.get_code().get_registers_size(), new.get_code().get_registers_size())
                self.assertEqual(old.get_code().get_ins_size(), new.get_code().get_ins_size())
            if raw(old) != raw(new):
                changed.append(key)
        self.assertEqual(changed, [self.key])
        self.assertEqual(self.new[self.key].get_code().get_registers_size(), 58)
        self.assertEqual(self.new[self.key].get_code().get_ins_size(), 11)

    def normalized(self):
        old, new = list(self.old[self.key].get_instructions()), list(self.new[self.key].get_instructions())
        calls = [i for i, op in enumerate(new) if 'OfflineMechanismGateway;->handleSequencedRequest(' in op.get_output()]
        self.assertEqual(len(calls), 1)
        call = calls[0]
        self.assertEqual([(op.get_name(), op.get_output()) for op in new[call-2:call]],
                         [('move-object/from16', 'v30, v4'), ('move-object/from16', 'v31, v47')])
        self.assertEqual(new[call].get_name(), 'invoke-static/range')
        self.assertEqual(new[call].get_output().split(', ', 1)[0], 'v21 ... v31')
        mapping = {}
        for i in range(len(new)+1):
            mapping[i] = i if i < call-2 else call-2 if i <= call else i-2
        return old, new, call, mapping

    def test_original_instructions_branches_and_exception_handlers_preserved(self):
        from androguard.core.dex import Operand
        old, new, call, mapping = self.normalized()
        ao, bo = offsets(old), offsets(new)
        ap, bp = {v:k for k,v in ao.items()}, {v:k for k,v in bo.items()}
        records = [(i, op) for i, op in enumerate(new) if i not in (call-2, call-1)]
        self.assertEqual(len(old), len(records))
        for index, (ni, op) in enumerate(records):
            previous = old[index]
            self.assertEqual(previous.get_name().split('/')[0], op.get_name().split('/')[0])
            if ni == call:
                self.assertIn('OfflineMechanismGateway;->handleRequest(', previous.get_output())
                self.assertEqual(op.get_output().split('(', 1)[1], previous.get_output().split('(', 1)[1].replace(')Z', ' Ljava/lang/Integer; Ljava/util/Set;)Z'))
            elif op.get_name().startswith(('if-', 'goto')):
                regs = lambda x: [v[1] for v in x.get_operands() if v[0] == Operand.REGISTER]
                self.assertEqual(regs(previous), regs(op))
                self.assertEqual(ao[ap[index]+2*previous.get_ref_off()], mapping[bo[bp[ni]+2*op.get_ref_off()]])
            else:
                self.assertEqual(previous.get_output(), op.get_output())
        def exception_shape(method, positions, index_map):
            code = method.get_code()
            handlers = code.get_handlers()
            handler_map = {h.get_off()-handlers.get_off(): h for h in handlers.get_list()}
            rows = []
            for tr in code.get_tries():
                h = handler_map[tr.get_handler_off()]
                typed = [(p.get_type_idx(), index_map[positions[2*p.get_addr()]]) for p in h.get_handlers()]
                catch_all = index_map[positions[2*h.get_catch_all_addr()]] if h.get_size() <= 0 else None
                rows.append((index_map[positions[2*tr.get_start_addr()]],
                             index_map[positions[2*(tr.get_start_addr()+tr.get_insn_count())]], typed, catch_all))
            return rows
        self.assertEqual(exception_shape(self.old[self.key], ao, {i:i for i in range(len(old)+1)}),
                         exception_shape(self.new[self.key], bo, mapping))

    def test_ack_precedes_extension_and_original_seen_gate_is_retained(self):
        old, new, call, mapping = self.normalized()
        ack = next(i for i, op in enumerate(new) if '->writeFrame(' in op.get_output())
        self.assertLess(ack, call-2)
        self.assertEqual((new[ack].get_name(), new[ack].get_output()),
                         ('invoke-direct', 'v11, v12, v6, v0, '+PKG+'LocalGatewayServer;->writeFrame(Ljava/io/OutputStream; I [B)V'))
        self.assertTrue(any('reliableRpcAck' in op.get_output() for op in new[:ack]))
        old_gates = [i for i, op in enumerate(old) if 'Ljava/util/Set;->add(' in op.get_output()]
        new_gates = [i for i, op in enumerate(new) if 'Ljava/util/Set;->add(' in op.get_output()]
        self.assertEqual([mapping[i] for i in new_gates], old_gates)
        self.assertTrue(all(i > call for i in new_gates))

    def test_scratch_registers_not_read_before_original_redefinition(self):
        from androguard.core.dex import Operand
        _, ops, call, _ = self.normalized()
        positions = offsets(ops)
        reverse = {v:k for k,v in positions.items()}
        for register in (30, 31):
            pending, visited, definitions = [call+1], set(), 0
            while pending:
                index = pending.pop()
                if index in visited: continue
                visited.add(index)
                op = ops[index]; name = op.get_name()
                regs = [x[1] for x in op.get_operands() if x[0] == Operand.REGISTER]
                if register in regs:
                    # Every reached first reference must be a pure assignment.
                    self.assertEqual(name, 'move-object/from16')
                    self.assertEqual(regs[0], register)
                    self.assertNotIn(register, regs[1:])
                    definitions += 1
                    continue
                if name.startswith(('return', 'throw')): continue
                self.assertNotIn(name, ('packed-switch', 'sparse-switch'))
                if name.startswith(('if-', 'goto')):
                    pending.append(positions[reverse[index]+2*op.get_ref_off()])
                if not name.startswith('goto'): pending.append(index+1)
            self.assertGreater(definitions, 0)


if __name__ == '__main__':
    unittest.main()
