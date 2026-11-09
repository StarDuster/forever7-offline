import copy
import unittest
from fractions import Fraction
from tools.project7_draw_ir.closure import compile_t1, select_bundle, ticket_select

class HierarchyTests(unittest.TestCase):
    def inputs(self):
        return ({1:{'id':1,'type':1,'weight':1,'random_reward':(10,)},2:{'id':2,'type':1,'weight':3,'random_reward':(11,)}},
                {(1,1):{'draw_type':1,'chouka_time':1,'pool':2}},
                {10:{'id':10,'weights':((100,1),(101,2))},11:{'id':11,'weights':((102,7),)}},
                {100:{'id':100,'hero':(12,),'tradeType':3},101:{'id':101,'items':(2,),'itemsNum':(1,),'future':'keep'},102:{'id':102,'hero':(33,),'items':(5,),'itemsNum':(4,)}})

    def test_bundle_and_default_preserved(self):
        ir = compile_t1(*self.inputs())
        result = select_bundle(ir,ordinal=1,outer_ticket=(0,1),inner_ticket=(0,1))
        self.assertEqual(result['common_reward_id'],102)
        self.assertEqual(result['bundle'], ir['reward_bundles']['102'])
        self.assertIn('hero+items',ir['base_component_signature_mass'])
        self.assertEqual(sum(Fraction(*v) for v in ir['base_component_signature_mass'].values()),1)
        result = select_bundle(ir,ordinal=2,outer_ticket=(0,1),inner_ticket=(1,3))
        self.assertEqual(result['common_reward_id'],101)
        self.assertIn('future',str(result['bundle']))

    def test_exact_boundaries(self):
        b=[{'id':1,'mass':[1,3]},{'id':2,'mass':[2,3]}]
        self.assertEqual(ticket_select(b,1,3)['id'],2)
        self.assertEqual(ticket_select(b,0,1)['id'],1)
        for n,d in [(1,1),(-1,2),(0,0),(True,2)]:
            with self.assertRaises(ValueError): ticket_select(b,n,d)

    def test_unproven_multi_reference_rejected(self):
        n,d,r,c=self.inputs();n[1]['random_reward']=(10,11)
        with self.assertRaises(ValueError): compile_t1(n,d,r,c)

    def test_missing_nested_duplicate_negative_empty(self):
        for edit in ['missing','nested','duplicate','negative','empty']:
            n,d,r,c=self.inputs()
            if edit=='missing': del c[100]
            if edit=='nested': c[100]['award_pool']=(4,)
            if edit=='duplicate':r[10]['weights']=((100,1),(100,2))
            if edit=='negative':r[10]['weights']=((100,-1),)
            if edit=='empty':r[10]['weights']=((100,0),)
            with self.assertRaises(ValueError): compile_t1(n,d,r,c)

if __name__ == '__main__':unittest.main()

class FixedArtifactTests(unittest.TestCase):
    def test_real_graph_mass_closure_and_fixed_rr(self):
        from tools.project7_draw_ir.consumer import load
        ir = load()
        self.assertEqual(len(ir['random_pools']),15)
        self.assertEqual(len(ir['reward_bundles']),888)
        self.assertEqual(len(ir['outer']['ordinal_overrides']),8)
        self.assertEqual(len(ir['random_pools']['1095']['branches']),36)
        self.assertEqual(len(ir['random_pools']['371']['branches']),108)
        for p in ir['random_pools'].values():
            self.assertEqual(sum(Fraction(*b['mass']) for b in p['branches']),1)
        self.assertEqual(ir['base_component_signature_mass']['hero'],[29,80])
        # Selecting data proves neither rank classification nor gameplay grants.
        self.assertFalse(ir['stock_grants_implemented'])
        self.assertFalse(ir['ordinal_lifecycle_proven'])

    def test_fixed_consumer_tamper(self):
        import tempfile
        from pathlib import Path
        from tools.project7_draw_ir.consumer import load, DEFAULT
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)
            for name in ['contract.json','t1-reward-ir.json']:
                (p/name).write_bytes((DEFAULT/name).read_bytes())
            data=bytearray((p/'t1-reward-ir.json').read_bytes());data[-3]^=1
            (p/'t1-reward-ir.json').write_bytes(data)
            with self.assertRaises(ValueError):load(p)
            (p/'contract.json').write_bytes(b'{}')
            with self.assertRaises(ValueError):load(p)

class LiteralRoundtripTests(unittest.TestCase):
    def test_typed_roundtrip(self):
        from tools.project7_draw_ir import typed, untyped
        value={(1,2):[1.25,(None,True)],'new':{'flag':False}}
        result=untyped(typed(value))
        self.assertEqual(result,value)
        self.assertIsInstance(next(k for k in result if isinstance(k,tuple)),tuple)
        with self.assertRaises(ValueError):untyped({'$dict':[[1,2],[1,3]]})

    def test_pinned_producer_failclosed_nonoverwrite(self):
        import tempfile
        from pathlib import Path
        from tools.project7_draw_ir.produce import produce
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);(root/'chouka_normal.marshal').write_bytes(b'bad')
            out=root/'new'
            with self.assertRaises(ValueError):produce(root,out)
            self.assertFalse(out.exists())
            out.mkdir();(out/'old').write_bytes(b'keep')
            with self.assertRaises(FileExistsError):produce(root,out)
            self.assertEqual((out/'old').read_bytes(),b'keep')

    def test_fixed_rank_proof(self):
        import json
        from tools.project7_draw_ir.consumer import DEFAULT
        audit=json.loads((DEFAULT/'rank-audit.json').read_bytes())
        for rid,count in [('1095',36),('371',108)]:
            entries=audit['rank_evidence'][rid]['leaves']
            self.assertEqual(len(entries),count)
            self.assertTrue(all(r['initial_rank']==4 for r in entries))
            self.assertEqual(len({r['hero_id'] for r in entries}),36)
        fragments=audit['rank_evidence']['371']['leaves']
        self.assertEqual({r['fragment_ordinal'] for r in fragments},{1,2,3})

class OfficialDefaultOracleTests(unittest.TestCase):
    def test_official_default_references_normal_rows_not_rr(self):
        from tools.project7_draw_ir.consumer import load
        ir=load()
        expected={1:(358,369),2:(361,5070),3:(359,370),4:(362,375),5:(360,5069),6:(859,364),10:(360,5069),12:(363,364)}
        actual={r['ordinal']:(r['normal_row_id'],r['random_reward_refs'][0]) for r in ir['outer']['ordinal_overrides']}
        self.assertEqual(actual,expected)
        self.assertEqual(len({a[0] for a in actual.values()}),7)
        self.assertTrue(all(i not in actual for i in [7,8,9,11]))
        base=ir['outer']['pools'][0]['branches']
        self.assertEqual(len(base),13)
        self.assertNotIn(4,{r['row_id'] for r in base})
        refs={r['random_reward_refs'][0] for r in base}
        common={b['id'] for rid in refs for b in ir['random_pools'][str(rid)]['branches']}
        self.assertEqual(len(common),868)
        self.assertEqual(len(ir['reward_bundles']),888)
