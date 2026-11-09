import unittest
from fractions import Fraction
from tools.project7_draw_ir import canonical, compile_outer, resolve_outer, require_executable, typed

class DrawIRTests(unittest.TestCase):
    def table(self):
        return {1: {'id': 1, 'type': 1, 'weight': 1, 'random_reward': (12,)}, 2: {'id': 2, 'type': 1, 'weight': 2, 'random_reward': (13, 14)}, 3: {'id': 3, 'type': 1, 'random_reward': (15,)}}

    def test_exact_mass_and_opaque_order(self):
        ir = compile_outer(self.table(), {})
        b = resolve_outer(ir, 1, 2)['branches']
        self.assertEqual([r['mass'] for r in b], [[1,3],[2,3]])
        self.assertEqual(b[1]['random_reward_refs'], [13,14])
        self.assertEqual(sum(Fraction(*r['mass']) for r in b), 1)
        with self.assertRaises(ValueError): require_executable(ir)

    def test_default_not_category_fallback(self):
        ir = compile_outer(self.table(), {(5, 8): {'draw_type': 5, 'chouka_time': 8, 'pool': 2}})
        self.assertEqual(resolve_outer(ir, 5, 8), {'override':2,'random_reward_refs':[13,14]})
        with self.assertRaises(ValueError): resolve_outer(ir, 5, 9)

    def test_bad_weights(self):
        for value in [-1, float('nan'), float('inf'), '1', True]:
            t = self.table();t[1]['weight'] = value
            with self.assertRaises(ValueError): compile_outer(t, {})

    def test_stable_lossless_metadata(self):
        t = self.table();t[1]['future'] = {(2,3): (1.25, None)}
        a = compile_outer(t, {})
        self.assertEqual(canonical(a), canonical(compile_outer(dict(reversed(list(t.items()))), {})))
        self.assertIn(b'$tuple', canonical(a));self.assertIn(b'$float', canonical(a))

    def test_bad_refs_and_ids(self):
        t = self.table();t[1]['random_reward'] = ()
        with self.assertRaises(ValueError): compile_outer(t, {})
        t = self.table();t[1]['id'] = 2
        with self.assertRaises(ValueError): compile_outer(t, {})

if __name__ == '__main__': unittest.main()
