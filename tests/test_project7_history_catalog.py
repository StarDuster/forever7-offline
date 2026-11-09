import unittest
from tools.project7_history_catalog import project,leaf
from tools.project7_draw_history_ir.consumer import load
from tools.project7_draw_history_ir.codec import typed

class HistoryCatalogTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.data,cls.contract=project()
    def test_exclusions_and_free_policy(self):
        rows=[line.split('\t') for line in self.data.decode().splitlines()]
        ids={int(r[1]) for r in rows if r[0]=='P'}
        self.assertEqual(len(ids),440);self.assertFalse(ids&{1,354,484})
        self.assertTrue(all(p['cost_policy']=='history-free-v1' for p in self.contract['pools']))
    def test_fixed_ready_family_exact_output(self):
        from pathlib import Path
        self.assertEqual(self.contract['ready_count'],380)
        self.assertEqual(self.data,Path('runtime/project7_history_catalog/catalog-v2.tsv').read_bytes())
        self.assertTrue(all(p['gift_policy']=='history-source-gift-daily-cap-v1' for p in self.contract['pools']))
    def test_pending_gift_is_not_silently_omitted(self):
        _,pending=project(gift_policy='pending');self.assertEqual(pending['ready_count'],0)
        self.assertTrue(any('explicit_gift_not_supported' in p['reasons'] for p in pending['pools']))
    def test_no_base_probability_renormalization(self):
        ir=load();wire=229;source=next(p for p in ir['ui_pools'] if p['wire_t']==wire)
        projected=[r.split('\t') for r in self.data.decode().splitlines() if r.startswith('B\t'+str(wire)+'\t')]
        self.assertEqual([(int(r[2]),int(r[3]),int(r[4])) for r in projected],[(r['source'],r['weight'][0],r['target']) for r in source['positive_base']])
    def test_unsupported_virtual_and_bundle_not_reclassified_item(self):
        n={'raw':typed({'id':1,'items':(9,),'itemsNum':(1,)}),'component_fields':['items'],'references':{'item:9':typed({'id':9,'type':8,'subtype':10,'skin':100})}}
        self.assertEqual(leaf(n)[0],'skin');self.assertEqual(leaf(n,version=1)[0],'unsupported')
        n['component_fields']=['hero','items'];self.assertEqual(leaf(n)[0],'unsupported')
    def test_v1_unchanged_and_v2_virtual_leaf_not_inventory(self):
        from pathlib import Path
        data,_=project(version=1);self.assertEqual(data,Path('runtime/project7_history_catalog/catalog-v1.tsv').read_bytes())
        ir=load();skin=leaf(ir['common_bundles']['45195']);pendant=leaf(ir['common_bundles']['45190'])
        self.assertEqual(skin[:3],('skin',10046,1));self.assertEqual(pendant[:3],('pendant',10085,1))
        self.assertNotIn(skin[0],('item','unsupported'));self.assertNotIn(pendant[0],('item','unsupported'))
        self.assertEqual(sum(line.startswith(b'L\t') and b'\tskin\t' in line for line in self.data.splitlines()),48)
        self.assertEqual(sum(line.startswith(b'L\t') and b'\tpendant\t' in line for line in self.data.splitlines()),80)
    def test_memory_and_currency_keep_truthful_mapping(self):
        n={'raw':typed({'id':1,'items':(9,),'itemsNum':(1,)}),'component_fields':['items'],'references':{'item:9':typed({'id':9,'memoryFrag':(12,3)})}}
        self.assertEqual(leaf(n)[:5],('memory',12,1,1,3))
        for field,kind in [('money','money'),('summoncoin','summonCoin')]:
            n={'raw':typed({'id':1,field:8}),'component_fields':[field],'references':{}}
            self.assertEqual(leaf(n)[:5],(kind,0,8,0,0))

if __name__=='__main__':unittest.main()
