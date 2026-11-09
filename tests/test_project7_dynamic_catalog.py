import copy,gzip,hashlib,importlib.util,json,tempfile,unittest
from pathlib import Path
from tools import project7_dynamic_catalog as tool
from tools.project7_draw_history_ir.codec import untyped
class DynamicCatalogTests(unittest.TestCase):
 def test_fixed_485_source_oracle(self):
  d=tool.load();p=next(p for p in d['pools'] if p['pool']==485)
  self.assertEqual([(x['threshold'],x['row_id']) for x in p['charge']],[(12,274),(36,275),(90,276),(180,277)])
  self.assertEqual([x['threshold'] for x in p['jiaozhi']],[1,2,3,4,5,6])
  r=untyped(d['random']);self.assertEqual({rid:r[rid]['positive_edges'] for rid in [17982,17983,17985,23500,23501,17987,23505]},{17982:[[57682,10]],17983:[[57683,10]],17985:[[57685,10]],23500:[[62945,10]],23501:[[62946,10]],17987:[[57687,10]],23505:[[62950,10]]})
  c=untyped(d['common']);self.assertEqual(c[62950]['items'],(16673,));self.assertEqual(untyped(d['items'])[16673]['pendant'],(147,18))
 def test_scope55_no_readiness_claim(self):
  d=tool.load();self.assertEqual(len({p['pool'] for p in d['pools']}),55);self.assertFalse(d['runtime_ready_ids']);self.assertTrue(all(not p['runtime_ready'] for p in d['pools']))
 def test_every_positive_edge_preserves_bundle(self):
  d=tool.load();c=untyped(d['common']);r=untyped(d['random'])
  for node in r.values():
   raw=untyped(node['raw']);self.assertEqual(node['positive_edges'],[[i,w] for i,w in raw['weights'] if w>0]);self.assertEqual(node['total'],sum(w for _,w in node['positive_edges']))
   self.assertTrue(all(i in c for i,w in node['positive_edges']))
 def test_base_normal_domain_and_defaults_retained(self):
  rows=tool.load()['base_graph']['records'];self.assertIn(['B','485','5151','15','23507'],rows)
  self.assertTrue(any(r[0]=='O' for r in rows));self.assertTrue(any(r[0]=='L' for r in rows))
 def test_no_template_uuid(self):
  for design in untyped(tool.load()['designs']).values():self.assertNotIn('u',design);self.assertNotIn('dumps_info',untyped(design['source']));self.assertIn('tr',design)
 def test_tamper_and_symlink_fail_closed(self):
  with tempfile.TemporaryDirectory() as td:
   root=Path(td)
   for name in ['catalog-v1.json.gz','contract.json']:(root/name).write_bytes((tool.DEFAULT/name).read_bytes())
   p=root/'catalog-v1.json.gz';b=p.read_bytes();p.write_bytes(b[:-1]+bytes([b[-1]^1]))
   with self.assertRaises(ValueError):tool.load(root)
   p.unlink();p.symlink_to(tool.DEFAULT/'catalog-v1.json.gz')
   with self.assertRaises(ValueError):tool.load(root)
 def test_producer_nonoverwrite_before_source_read(self):
  with tempfile.TemporaryDirectory() as td:
   with self.assertRaisesRegex(ValueError,'existing output'):tool.produce(Path('/nonexistent'),Path(td))
 def test_scope_source_pin_no_analysis_consumer(self):
  self.assertEqual(tool.sha((tool.ROOT/'reports/terra-p7-remaining-draw-families-current.json').read_bytes()),tool.SCOPE_SHA)
  d=tool.load();self.assertEqual(d['source_pins'],tool.PINS)
 def test_actual_unopened_scene_projection(self):
  path=tool.ROOT/'runtime/android_dynamic_draw/host_tests/verify_slot_projection.py';spec=importlib.util.spec_from_file_location('dynamic_slot_probe',path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);self.assertTrue(m.verify()['pass'])
if __name__=='__main__':unittest.main()
