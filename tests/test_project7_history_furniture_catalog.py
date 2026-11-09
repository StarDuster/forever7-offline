import base64,unittest
from fractions import Fraction
from pathlib import Path
from tools.project7_history_catalog import project_furniture,furniture_reward
from tools.project7_draw_history_ir.consumer import load
from tools.project7_draw_history_ir.codec import typed
from runtime.android_draw_policy.host_tests.verify_original_consumers import bson
class FurnitureCatalogTests(unittest.TestCase):
    def test_real_family_projection_and_separate_scope(self):
        data,contract=project_furniture(defaults_proven=True)
        rows=[line.split('\t') for line in data.decode().splitlines()[1:]]
        self.assertEqual(len(rows),40);self.assertNotIn(162,{int(row[1]) for row in rows})
        self.assertEqual(contract['ready_count'],40)
        ir=load();source={p['wire_t']:p for p in ir['ui_pools'] if p['rpc_family']=='furniture' and p['wire_t']!=162}
        self.assertEqual({int(row[1]) for row in rows},set(source))
        for _,t,payload in rows:
            doc=bson(base64.b64decode(payload));self.assertEqual(doc['cost'][1],0);self.assertEqual(doc['ticket'],0)
            self.assertEqual([(r['source_normal'],r['w'],r['source_random']) for r in doc['base']],[(b['source'],b['weight'][0],b['target']) for b in source[int(t)]['positive_base']])
    def test_real_106_and_108_positive_rows_are_not_coerced_to_five_tiers(self):
        data,_=project_furniture();docs={int(r[1]):bson(base64.b64decode(r[2])) for line in data.decode().splitlines()[1:] for r in [line.split('\t')]}
        self.assertEqual([r['source_normal'] for r in docs[106]['base']],[1110,1111,1112,1116,1117])
        self.assertEqual([r['w'] for r in docs[106]['base']],[540,300,70,60,30])
        self.assertEqual([r['source_normal'] for r in docs[108]['base']],list(range(1118,1127)))
        self.assertEqual([r['w'] for r in docs[108]['base']],[100]*9)
        self.assertEqual(sum(r['source_random']==7663 for r in docs[108]['base']),2)
    def test_default_direct_rr_is_explicit_gate(self):
        _,pending=project_furniture(defaults_proven=False);self.assertEqual(pending['ready_count'],37)
        self.assertEqual([p['wire_t'] for p in pending['pools'] if not p['ready']],[106,132,161])
        data,_=project_furniture(defaults_proven=True)
        docs={int(r[1]):bson(base64.b64decode(r[2])) for line in data.decode().splitlines()[1:] for r in [line.split('\t')]}
        self.assertEqual(docs[106]['defaults']['1']['source_random'],7660)
    def test_original_permanent_G1_matches_actual_RR9174_complete_bundles(self):
        # Independent shipped stock catalog oracle: source pool9174 is a random ID,
        # not a normal row. This compares the complete original g bundles.
        home=Path('analysis/project7/fixed-component-v2-stage/assets/home.tsv')
        if not home.exists():self.skipTest('maintainer public original-assets oracle absent')
        raw=next(l.split('\t')[2] for l in home.read_text().splitlines() if l.startswith('G\t1\t'))
        original=bson(base64.b64decode(raw))['options'];ir=load();rr=ir['random_pools']['9174'];branches=rr['branches']
        self.assertEqual(len(original),18);self.assertEqual([v['g'] for v in original],[furniture_reward(ir['common_bundles'][str(b['target'])]) for b in branches])
        total=sum(b['weight'][0] for b in branches)
        self.assertEqual([Fraction(v['w']).limit_denominator(total) for v in original],[Fraction(b['weight'][0],total) for b in branches])
    def test_entire_multi_item_bundle_remains_one_outcome(self):
        node={'component_fields':['items'],'raw':typed({'items':(2,3),'itemsNum':(4,5)}),'references':{'item:2':typed({'type':1}),'item:3':typed({'type':1})}}
        grants=furniture_reward(node);self.assertEqual([(g['i'],g['n']) for g in grants],[(2,4),(3,5)])
        node['references']['item:3']=typed({'type':8,'subtype':61})
        with self.assertRaises(ValueError):furniture_reward(node)
if __name__=='__main__':unittest.main()
