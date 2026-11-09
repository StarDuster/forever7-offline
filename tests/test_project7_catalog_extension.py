"""Static source projection and fixed catalog consumer tests; no game/profile execution."""
import hashlib,json,pathlib,sys,tempfile,unittest
ROOT=pathlib.Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools'))
import project7_catalog_extension as c
from read_data_table import read
BUNDLE=ROOT/'runtime/project7_catalog';BASE=ROOT/'analysis/project7/fixed-component-v2-stage/assets/resources.tsv'

class CatalogParserTests(unittest.TestCase):
    def test_stock_rows_and_trailing_empty_field(self):
        catalog,rows=c.parse_catalog(b'S\t9\t2\t3\tname\r\nI\t7\titem\t5\t1\t0\r\nT\t7\t1\t\t\r\n')
        self.assertEqual(catalog['S'][9],['S','9','2','3','name'])
        self.assertEqual(catalog['T'][(7,1)],['T','7','1','',''])
    def test_duplicate_ids_and_shapes(self):
        for data in [b'S\t9\t2\t3\ta\nS\t9\t2\t4\tb\n',b'T\t7\t1\t\t\nT\t7\t1\t\t\n',b'I\t7\tx\t5\t1\t0\nI\t7\ty\t5\t1\t0\n',b'S\t1\t2\t3\n',b'Z\t1\n',b'T\t7\t6\t\t\n']:
            with self.assertRaises(ValueError):c.parse_catalog(data)
    def test_attr_types_invalid_and_duplicate(self):
        for attrs in ['f1:NaN','f1:Infinity','f1:1,f1:2','wrong:2','f2','f1:1:2']:
            with self.assertRaises(ValueError):c.parse_catalog(('T\t7\t1\t\t'+attrs+'\n').encode())
        tricks,attrs,details=c.project_treasure({'secondAttrs':{'z':[2,4],'a':[1,3]},'thridAttrs':{'b':[0.5,1.5]},'fixTrick':[8,3]},{'a':9,'z':2,'b':4})
        self.assertEqual((tricks,attrs),('8,3','f9:1.0,f2:2.0,t4:0.5'))
        self.assertEqual(details[0]['sourceBounds'],[1,3]);self.assertIs(type(details[0]['value']),float)
        with self.assertRaises(ValueError):c.project_treasure({'secondAttrs':{'unknown':[1,2]}},{})
    def test_no_forged_h_or_pools(self):
        for row in [b'H\t46\tx\t1\t4\t1\n',b'P\t1\t2\t3\t4\t5\n']:
            with self.assertRaisesRegex(ValueError,'may not add H'):c.parse_catalog(row,True)
    def test_wrong_baseline_refused(self):
        with self.assertRaisesRegex(ValueError,'baseline'):c.extend_catalog(b'wrong')
    def test_existing_output_unchanged(self):
        with tempfile.TemporaryDirectory() as t:
            p=pathlib.Path(t)/'output';p.write_bytes(b'old-output')
            with self.assertRaisesRegex(ValueError,'output exists'):c.apply('missing',p)
            self.assertEqual(p.read_bytes(),b'old-output')
            bad=pathlib.Path(t)/'bad';bad.write_bytes(b'bad');new=pathlib.Path(t)/'not-created'
            with self.assertRaises(ValueError):c.apply(bad,new)
            self.assertFalse(new.exists())

class FixedCatalogTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not BASE.is_file():raise unittest.SkipTest('Pinned static component baseline unavailable')
        cls.base=BASE.read_bytes();cls.ext=(BUNDLE/'extension.tsv').read_bytes();cls.contract=(BUNDLE/'contract.json').read_bytes();cls.targets=(BUNDLE/'target-manifest.json').read_bytes();cls.provenance=(BUNDLE/'provenance.json').read_bytes()
    def test_real_output_preserves_baseline_all_rows_and_flags(self):
        output=c.extend_catalog(self.base)
        self.assertEqual(output[:len(self.base)],self.base)
        self.assertEqual(output,self.base+self.ext)
        self.assertEqual(hashlib.sha256(output).hexdigest(),'5e716bd9a34cfd678af9aba6385ba3fae92d4b17486ee480f76bd95320268e99')
        final,rows=c.parse_catalog(output);targets=json.loads(self.targets)
        self.assertEqual({k:len(v) for k,v in final.items()},{'H':138,'S':494,'I':5065,'T':1900})
        self.assertEqual(set(final['H'])|{46,125},{r['id'] for r in targets['heroes']})
        self.assertNotIn(46,final['H']);self.assertNotIn(125,final['H'])
        self.assertEqual({(r['id'],q['quality']) for r in targets['treasures'] for q in r['qualities']},set(final['T']))
        self.assertEqual({r['id'] for r in targets['skins']},set(final['S']))
        self.assertEqual({r['id'] for r in targets['heroes'] if r['grant']=='stock-addMissingHero'},{46,125})
        for r in targets['heroes']:
            if r['id'] in (46,125):self.assertEqual((r['rank'],r['sourceFlags']['hero_forbid']),(4,1))
        self.assertFalse(targets['profileConstraints']['runtimeModelUiPersistenceVerified'])
    def test_every_bundle_tamper_rejected_without_p7_apk(self):
        # Consumer takes baseline/spec bytes; there is no source APK/profile parameter.
        for position in range(4):
            args=[self.ext,self.contract,self.targets,self.provenance]
            damaged=bytearray(args[position]);damaged[len(damaged)//2]^=1;args[position]=bytes(damaged)
            with self.assertRaises(ValueError):c.extend_catalog(self.base,*args)
        bad=bytearray(self.base);bad[0]^=1
        with self.assertRaises(ValueError):c.extend_catalog(bytes(bad))
    def test_same_counts_wrong_id_set_not_accepted(self):
        catalog,_=c.parse_catalog(c.extend_catalog(self.base));targets=json.loads(self.targets)
        first=next(iter(catalog['S']));catalog['S'][9999999]=catalog['S'].pop(first)
        with self.assertRaisesRegex(ValueError,'ID set'):c.verify_full_target(catalog,targets)
    def test_fixed_rows_match_research_candidate_without_runtime_dependency(self):
        candidate=ROOT/'analysis/project7/catalog-extension/candidate-resources.tsv'
        if not candidate.is_file():self.skipTest('Research candidate unavailable')
        _,ours=c.parse_catalog(self.ext,True);_,original=c.parse_catalog(candidate.read_bytes(),True)
        self.assertEqual(ours,original)
        self.assertEqual(len(ours),52)
        self.assertEqual({r[0] for r in ours},{'S','I','T'})
    def test_real_stock_parser_static_format(self):
        base=ROOT/'analysis/project7/manager'
        if not (base/'com.project7.localmanager.LocalResourceCatalog.dis').is_file():self.skipTest('Static stock DEX listing unavailable')
        loader=(base/'com.project7.localmanager.LocalResourceCatalog.dis').read_text()
        self.assertIn('split(Ljava/lang/String; I)',loader)
        self.assertIn('const/4 v3, -1',loader)
        for tag,fields in [('Hero',['id I','name Ljava/lang/String;','files I','rank I','duplicate I']),('Skin',['id I','hero I','item I','name Ljava/lang/String;']),('Item',['id I','name Ljava/lang/String;','type I','wrap I','hero I']),('Treasure',['item I','quality I','tricks Ljava/util/List;','attrs Ljava/util/List;'])]:
            dis=(base/f'com.project7.localmanager.LocalResourceCatalog${tag}.dis').read_text()
            for f in fields:self.assertIn('->'+f,dis)
        treasure=(base/'com.project7.localmanager.LocalResourceCatalog$Treasure.dis').read_text()
        self.assertIn('Double;->parseDouble',treasure)
    def test_real_cdata_exact_target_sets_and_1890_existing_t(self):
        directory=ROOT/'analysis/decompiled'
        if not directory.is_dir():self.skipTest('Maintainer cdata fixtures unavailable')
        hero,skin,tr=(read(directory/(n+'.py')) for n in ('hero','skin','hero_treasure'))
        targets=json.loads(self.targets);self.assertEqual({x['id'] for x in targets['heroes']},set(hero));self.assertEqual({x['id'] for x in targets['skins']},set(skin));self.assertEqual({(x['id'],q['quality']) for x in targets['treasures'] for q in x['qualities']},set(tr))
        for r in targets['skins']:
            source=skin[r['id']];self.assertEqual([r['hero'],r['item'],r['variantId'],r['sourceName']],[source['hero'],source['item'],source['id'],source['name']]);self.assertEqual(r['sourceFlags'],{k:v for k,v in source.items() if 'forbid' in k or 'release' in k})
        const=ast_source=ROOT/'analysis/original-py-640/com/const.py'
        import ast
        tree=ast.parse(const.read_text());cls=next(n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='CombatAttrs');index=ast.literal_eval(next(n.value for n in cls.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='NAME_TO_INDEX' for t in n.targets)))
        base,_=c.parse_catalog(self.base);self.assertEqual(len(base['T']),1890)
        for key,row in base['T'].items():
            source=tr[key];expected={prefix+str(index[n]):float(bounds[0]) for field,prefix in [('secondAttrs','f'),('thridAttrs','t')] for n,bounds in source.get(field,{}).items()}
            actual={n:float(v) for n,v in (f.split(':') for f in row[4].split(',') if f)}
            self.assertEqual(actual,expected);self.assertEqual([int(v) for v in row[3].split(',')] if row[3] else [],list(source.get('fixTrick',())))
        eq=(ROOT/'analysis/project7/fixed-component-v2-stage/assets/treasure.tsv').read_text();keys={line.split('\t')[1] for line in eq.splitlines() if line.startswith('EQ\t')}
        self.assertTrue({f'{i}:{q}' for i in (1188,1343) for q in range(1,6)}<=keys)
    def test_maintainer_reproduction_from_explicit_sources(self):
        if not (ROOT/'analysis/decompiled/hero.py').is_file():self.skipTest('Maintainer cdata fixtures unavailable')
        with tempfile.TemporaryDirectory() as t:
            out=pathlib.Path(t)/'spec'
            c.maintainer_generate(BASE,ROOT/'analysis/decompiled',ROOT/'analysis/original-py-640/com/const.py',ROOT/'analysis/original-py-640/com/data/cdata/chouka_hero_file.py',ROOT/'analysis/project7/fixed-component-v2-stage/assets/treasure.tsv',out)
            for name in ['extension.tsv','contract.json','target-manifest.json','provenance.json']:self.assertEqual((out/name).read_bytes(),(BUNDLE/name).read_bytes())
if __name__=='__main__':unittest.main()
