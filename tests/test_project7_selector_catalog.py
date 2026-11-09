"""Fixed public selector projection invariants, no game/module execution."""
import copy,json,tempfile,unittest
from pathlib import Path
from tools import project7_selector_catalog as c
class SelectorCatalogTests(unittest.TestCase):
 def toy(self):
  items={1000+t*10+s:{'type':8,'subtype':s,'virtual_sub_type':s,'card_pool':t} for t in c.POOLS for s in range(61,68)}
  return items,{7:{'hero_composite_init_rank':4},9:{'hero_composite_init_rank':3}},{7:{'avaliable':1},9:{'avaliable':1}}, {t:{'self_choose':1,'end_time':(2025,1,1,0,0,0,0,1,-1)} for t in c.POOLS}
 def test_real_fixed42_and_fallback_candidates(self):
  data=c.verify();self.assertEqual(data['rows'],42);self.assertEqual(data['roster_counts'],{'S':3,'A':3});lines=(c.DEFAULT/'catalog-v1.tsv').read_text().splitlines();self.assertEqual([l for l in lines if l.startswith('H\t4')],['H\t4\t67','H\t4\t91','H\t4\t121']);self.assertFalse(data['ready_claim'])
 def test_exact_complete_domain_and_utc_epoch(self):
  args=self.toy();data,meta=c.compile_tables(*args);self.assertEqual(len([l for l in data.splitlines() if l.startswith(b'I\t')]),42);self.assertEqual(set(meta['pool_stamps'].values()),{1735689600});self.assertEqual(c.compile_tables(*args)[0],data)
 def test_duplicate_or_missing_pool_subtype(self):
  args=self.toy();row=next(iter(args[0].values()));args[0][999999]=dict(row)
  with self.assertRaisesRegex(ValueError,'duplicate'):c.compile_tables(*args)
  args=self.toy();args[0].pop(next(iter(args[0])))
  with self.assertRaisesRegex(ValueError,'closure'):c.compile_tables(*args)
 def test_bad_virtual_shape_rank_and_missing_hero(self):
  for field,value in [('type',2),('subtype',1),('card_pool',999)]:
   args=self.toy();next(iter(args[0].values()))[field]=value
   with self.assertRaises(ValueError):c.compile_tables(*args)
  args=self.toy();args[1][7]['hero_composite_init_rank']=2
  with self.assertRaises(ValueError):c.compile_tables(*args)
  args=self.toy();args[1].pop(7)
  with self.assertRaisesRegex(ValueError,'missing'):c.compile_tables(*args)
 def test_asset_contract_tamper_rejected(self):
  for target in ('catalog-v1.tsv','contract.json'):
   with tempfile.TemporaryDirectory() as tmp:
    root=Path(tmp)
    for name in ('catalog-v1.tsv','contract.json'):(root/name).write_bytes((c.DEFAULT/name).read_bytes())
    (root/target).write_bytes((root/target).read_bytes()+b' ')
    with self.assertRaises(ValueError):c.verify(root)
 def test_history_v3_changes_only_five_readiness_flags_and_35_selector_kinds(self):
  old=(c.ROOT/'runtime/project7_history_catalog/catalog-v2.tsv').read_text().splitlines();new=(c.ROOT/'runtime/project7_history_catalog/catalog-v3.tsv').read_text().splitlines();self.assertEqual(len(old),len(new));changes=[]
  for before,after in zip(old,new):
   if before==after:continue
   b,a=before.split('\t'),after.split('\t');changes.append(a[0])
   if a[0]=='P':self.assertIn(int(a[1]),c.POOLS[:-1]);self.assertEqual(b[:4]+b[5:],a[:4]+a[5:]);self.assertEqual((b[4],a[4]),('0','1'))
   else:self.assertEqual(a[0],'L');self.assertEqual(b[:2]+b[3:],a[:2]+a[3:]);self.assertEqual((b[2],a[2]),('unsupported','selector'))
  self.assertEqual(changes.count('P'),5);self.assertEqual(changes.count('L'),35)
 def test_history_producer_preserves_frozen_v2_and_reproduces_v3(self):
  from tools.project7_history_catalog import project
  import hashlib
  old,_=project(version=2);self.assertEqual(hashlib.sha256(old).hexdigest(),'debbda4a6910947a0843774261971f17d217b120c6bd470ef8572bae53f043b0')
  new,contract=project(version=3);self.assertEqual(new,(c.ROOT/'runtime/project7_history_catalog/catalog-v3.tsv').read_bytes());self.assertEqual(contract['ready_count'],385)
 def test_producer_does_not_overwrite_or_accept_unpinned_source(self):
  with tempfile.TemporaryDirectory() as tmp:
   root=Path(tmp);existing=root/'existing';existing.mkdir();(existing/'sentinel').write_text('keep')
   with self.assertRaises(ValueError):c.produce(root,existing)
   self.assertEqual((existing/'sentinel').read_text(),'keep')
   (root/'item_data.marshal').write_bytes(b'not fixed640')
   with self.assertRaises(ValueError):c.produce(root,root/'new')
   self.assertFalse((root/'new').exists())
