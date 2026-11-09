"""Reviewed Week/patrol seams; inverse mapping proves original cache/branches."""
from pathlib import Path
import unittest
from test_project7_dream_hook import methods, raw, PKG

ROOT = Path(__file__).resolve().parents[1]


class DreamLifecycleHookTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        old = ROOT / 'analysis/project7/dream-hook-v1/classes7.dex'
        new = ROOT / 'analysis/project7/dream-lifecycle-hook-v1/classes7.dex'
        if not old.exists() or not new.exists():
            raise unittest.SkipTest('Maintainer source/target absent')
        cls.old, cls.new = methods(old), methods(new)

    def key(self, name):
        owner = PKG + ('LocalProfileStore;' if name == 'updateServices' else 'LocalGatewayServer;')
        return next(k for k in self.old if k[0] == owner and k[1] == name)

    def test_only_three_callers_changed_no_register_or_definition_changes(self):
        self.assertEqual(set(self.old), set(self.new))
        self.assertEqual(len(self.old), 3705)
        changed = []
        for key, old in self.old.items():
            new = self.new[key]
            self.assertEqual(old.get_access_flags(), new.get_access_flags())
            if old.get_code():
                self.assertEqual(old.get_code().get_registers_size(), new.get_code().get_registers_size())
                self.assertEqual(old.get_code().get_ins_size(), new.get_code().get_ins_size())
            if raw(old) != raw(new): changed.append(key[1])
        self.assertCountEqual(changed, ['handleWeekRpc', 'handleReliableRpc', 'updateServices'])

    def test_store_keeps_original_writer_and_recover(self):
        key = self.key('updateServices')
        old, new = raw(self.old[key]), raw(self.new[key])
        self.assertEqual(len(old), len(new))
        differences = [(a, b) for a, b in zip(old, new) if a != b]
        self.assertEqual(len(differences), 1)
        a, b = differences[0]
        self.assertEqual(a, (b[0], b[1].replace('DreamWeekPolicy;->apply', 'LocalWeekEngine;->apply')))

    def inverse(self, name):
        key = self.key(name)
        old, new = list(self.old[key].get_instructions()), list(self.new[key].get_instructions())
        records, mapping = [], {}
        i, callbacks, guards, recover = 0, 0, 0, 0
        while i < len(new):
            # Eight reviewed argument moves + same original callback invocation.
            if (i+8 < len(new) and 'DreamPatrolReply;->complete(' in new[i+8].get_output()):
                prefix = raw_sequence(new[i:i+8])
                self.assertEqual(prefix[:3], [('move-object/from16','v48, v11'), ('move-object/from16','v49, v12'), ('move-object/from16','v50, v13')])
                self.assertEqual(prefix[3][0], 'move/from16')
                self.assertEqual(prefix[4][0], 'move-object/from16')
                self.assertEqual(prefix[5:], [('move-object/from16','v53, v41'), ('move-object/from16','v54, v42'), ('move-object/from16','v55, v43')])
                cb = prefix[3][1].split(', ')[1]; method = prefix[4][1].split(', ')[1]
                for j in range(i,i+9): mapping[j] = len(records)
                records.append(('invoke-direct', 'v11, v12, v13, '+cb+', '+method+', '+PKG+'LocalGatewayServer;->completeCallback(Ljava/io/OutputStream; [B I Ljava/lang/String;)V', None))
                callbacks += 1; i += 9; continue
            op = new[i]; kind, text = op.get_name(), op.get_output()
            if 'DreamCoordinator;->recover(' in text:
                self.assertEqual(text, 'v0, v4, v5, v6, '+PKG+'DreamCoordinator;->recover('+PKG+'LocalGatewayServer; Ljava/lang/String; '+PKG+'LocalTutorialStore$Progress; '+PKG+'LocalEventEngine;)V')
                mapping[i] = len(records); recover += 1; i += 1; continue
            mapping[i] = len(records)
            records.append((kind, None if kind.startswith(('if-','goto')) else text, i if kind.startswith(('if-','goto')) else None))
            i += 1
            if (kind == 'move-result-object' and text == 'v0' and i >= 2 and
                    'DreamPatrolGatewayHooks;->claim(' in new[i-2].get_output()):
                extra = new[i:i+7]
                self.assertEqual(extra[0].get_name(), 'if-nez')
                self.assertEqual(raw_sequence(extra[1:5]), [('move-object/from16','v48, v11'), ('move-object/from16','v49, v12'), ('move-object/from16','v50, v13'), ('move-object/from16','v51, v40')])
                self.assertIn('DreamPatrolReply;->rejectClaim(', extra[5].get_output())
                self.assertEqual(extra[6].get_name(), 'return-void')
                for j in range(i,i+7): mapping[j] = len(records)
                # New accepted branch jumps past reject-only code to the stock tail.
                self.assertEqual(sum(x.get_length() for x in extra), 2*extra[0].get_ref_off())
                guards += 1; i += 7
        self.assertEqual(len(old), len(records))
        from androguard.core.dex import Operand
        def offsets(seq):
            result={}; pos=0
            for j,op in enumerate(seq): result[pos]=j; pos+=op.get_length()
            return result
        ao, bo = offsets(old), offsets(new)
        ap, bp = {v:k for k,v in ao.items()}, {v:k for k,v in bo.items()}
        for j, (kind,text,branch) in enumerate(records):
            self.assertEqual(kind.split('/')[0], old[j].get_name().split('/')[0])
            if branch is None: self.assertEqual(text, old[j].get_output())
            else:
                registers=lambda op:tuple(x[1] for x in op.get_operands() if x[0]==Operand.REGISTER)
                self.assertEqual(registers(old[j]),registers(new[branch]))
                self.assertEqual(ao[ap[j]+2*old[j].get_ref_off()], mapping[bo[bp[branch]+2*new[branch].get_ref_off()]])
        return callbacks, guards, recover

    def test_week_recovery_preserves_every_original_branch(self):
        self.assertEqual(self.inverse('handleWeekRpc'), (0,0,1))

    def test_reliable_original_sequence_cache_and_nonnull_tail_preserved(self):
        self.assertEqual(self.inverse('handleReliableRpc'), (11,1,0))


def raw_sequence(seq):
    return [(i.get_name(), i.get_output()) for i in seq]


if __name__ == '__main__': unittest.main()
