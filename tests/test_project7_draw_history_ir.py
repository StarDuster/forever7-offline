import gzip,hashlib,json,tempfile,unittest
from fractions import Fraction
from pathlib import Path
from tools.project7_draw_history_ir.compiler import compile_history,distribution,epoch
from tools.project7_draw_history_ir.codec import canonical,typed,untyped
from tools.project7_draw_history_ir.consumer import load,lookup,inflate,DEFAULT

class HistoryIRTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.real=load()
    def toy(self):
        return {'chouka_info':{1:{'drawType':1,'poolType':1,'end_time':(2035,9,22,7,0,0,0,0,0),'begin_time':(),'show_level_lower_bound':1,'show_level_upper_bound':110}},'chouka_normal':{1:{'id':1,'type':1,'weight':1,'random_reward':(20,)},360:{'id':360,'type':30,'random_reward':(30,)}},'chouka_default':{(1,10):{'draw_type':1,'chouka_time':10,'pool':360}},'reward_random':{20:{'id':20,'weights':((100,1),(101,2))},30:{'id':30,'weights':((101,1),)}},'reward_common':{100:{'id':100,'hero':(12,),'items':(8,),'itemsNum':(3,),'tradeType':3},101:{'id':101,'money':5,'futureAward':{'keep':(1,2)}}},'item_data':{8:{'id':8,'type':1}},'hero':{12:{'hero_composite_init_rank':4}},'chouka_hero_file':{},'hero_self_choose_info':{},'hero_treasure_generate':{}}
    def test_full_actual_shape(self):
        s=self.real['summary'];self.assertEqual(s['ui_rows'],485)
        self.assertEqual(s['kind_counts'],{'normal':1,'plain':435,'choice':6,'newbie':1,'friendship':1,'furniture':41})
        self.assertFalse(self.real['all_runtime_enabled'])
        self.assertEqual(lookup(self.real,484)['epoch_utc'],2074057200)
        for t in [0,-1,True,999999]:
            with self.assertRaises(ValueError):lookup(self.real,t)
    def test_actual_oracle_default_and_missing(self):
        p=lookup(self.real,1);m={r['ordinal']:(r.get('normal_row_id'),untyped(r['random_reward_refs'])[0]) for r in p['default_rows'] if 'normal_row_id' in r}
        self.assertEqual(m[10],(360,5069));self.assertEqual(m[1],(358,369));self.assertEqual(m[2],(361,5070));self.assertEqual(m[12],(363,364))
        self.assertIn('missing_default_normal:5657',lookup(self.real,42)['issues'])
        self.assertEqual(len(p['positive_base']),13);self.assertNotIn(4,{b['source'] for b in p['positive_base']})
    def test_every_positive_distribution_exact(self):
        for node in list(self.real['random_pools'].values()):
            if node['branches']:self.assertEqual(sum(Fraction(*r['mass']) for r in node['branches']),1)
        for p in self.real['ui_pools']:
            if p['positive_base']:self.assertEqual(sum(Fraction(*r['mass']) for r in p['positive_base']),1)
    def test_bundle_atomic_and_unknown_retained(self):
        ir=compile_history(self.toy());bundle=ir['common_bundles']['100'];self.assertEqual(bundle['component_fields'],['hero','items']);self.assertTrue(bundle['bundle_atomic'])
        self.assertEqual(untyped(bundle['raw'])['itemsNum'],(3,))
        self.assertEqual(untyped(ir['common_bundles']['101']['raw'])['futureAward'],{'keep':(1,2)})
        self.assertTrue(ir['common_bundles']['101']['issues'])
        self.assertEqual(ir['ui_pools'][0]['base_bundle_signature_mass']['hero+items'],[1,3])
    def test_default_refers_normal_not_rr(self):
        ir=compile_history(self.toy());r=ir['ui_pools'][0]['default_rows'][0]
        self.assertEqual(r['normal_row_id'],360);self.assertEqual(untyped(r['random_reward_refs']),(30,))
    def test_missing_default_never_guessed(self):
        t=self.toy();del t['chouka_normal'][360];p=compile_history(t)['ui_pools'][0]
        self.assertIn('missing_default_normal:360',p['issues']);self.assertEqual(p['capability'],'unresolved')
    def test_weight_bounds(self):
        for w in [-1,float('nan'),float('inf'),'1',True]:
            with self.assertRaises(ValueError):distribution([(1,2,w)])
        self.assertEqual(distribution([(1,2,0)]),[])
        d=distribution([(1,7,1),(2,7,2)]);self.assertEqual([x['mass'] for x in d],[[1,3],[2,3]])
    def test_gzip_limits_and_tamper(self):
        data=b'abc'*20;packed=gzip.compress(data,mtime=0);sha=hashlib.sha256(data).hexdigest();self.assertEqual(inflate(packed,len(data),sha),data)
        for value,size in [(packed[:-1],len(data)),(packed+b'x',len(data)),(packed,len(data)-1),(packed,0)]:
            with self.assertRaises(ValueError):inflate(value,size,sha)
        with tempfile.TemporaryDirectory() as t:
            root=Path(t)
            for name in ['contract.json','history-ir.json.gz']:(root/name).write_bytes((DEFAULT/name).read_bytes())
            a=bytearray((root/'history-ir.json.gz').read_bytes());a[15]^=1;(root/'history-ir.json.gz').write_bytes(a)
            with self.assertRaises(ValueError):load(root)
    def test_rpc_families_and_choices(self):
        self.assertEqual(lookup(self.real,131)['rpc_family'],'friendship')
        self.assertEqual(len([p for p in self.real['ui_pools'] if p['rpc_family']=='furniture']),41)
        for p in self.real['ui_pools']:
            if p['kind']=='choice':self.assertFalse(p['choice_candidates']['resolved'])
        self.assertEqual(self.real['manual_ui_entries'][0]['wire_t'],99)
        self.assertEqual(lookup(self.real,99)['rpc_family'],'friendship');self.assertFalse(lookup(self.real,99)['runtime_enabled_by_this_component'])
        self.assertEqual(lookup(self.real,354)['capability'],'new_groups_disabled')
    def test_canonical_stability_and_originals_untouched(self):
        t=self.toy();before=canonical(typed(t));a=canonical(compile_history(t));self.assertEqual(a,canonical(compile_history(t)));self.assertEqual(canonical(typed(t)),before)

if __name__=='__main__':unittest.main()

class ProducerConsumerBoundaryTests(unittest.TestCase):
    def test_wrong_source_and_existing_output_unchanged(self):
        from tools.project7_draw_history_ir.produce import produce
        with tempfile.TemporaryDirectory() as t:
            root=Path(t);(root/'chouka_friend.marshal').write_bytes(b'wrong')
            with self.assertRaises(ValueError):produce(root,root/'new')
            self.assertFalse((root/'new').exists())
            (root/'existing').mkdir();(root/'existing'/'keep').write_bytes(b'keep')
            with self.assertRaises(FileExistsError):produce(root,root/'existing')
            self.assertEqual((root/'existing'/'keep').read_bytes(),b'keep')
    def test_isolated_consumer_no_analysis_network_or_xdis(self):
        import shutil,subprocess,sys
        package=Path('tools/project7_draw_history_ir').resolve()
        with tempfile.TemporaryDirectory() as t:
            root=Path(t);dest=root/'tools/project7_draw_history_ir';(dest/'data/history-v1').mkdir(parents=True)
            for name in ['__init__.py','codec.py','compiler.py','consumer.py']:shutil.copyfile(package/name,dest/name)
            for name in ['contract.json','history-ir.json.gz']:shutil.copyfile(DEFAULT/name,dest/'data/history-v1'/name)
            code='''import sys,socket,urllib.request
sys.path.insert(0,sys.argv[1])
def denied(*a,**k):raise AssertionError("network forbidden")
socket.socket=denied;urllib.request.urlopen=denied
def audit(event,args):
 if event=="open" and isinstance(args[0],str) and "/analysis/" in args[0]:raise AssertionError("analysis forbidden")
sys.addaudithook(audit)
from tools.project7_draw_history_ir.consumer import load,lookup
ir=load();assert len(ir["ui_pools"])==485;assert lookup(ir,484)["epoch_utc"]==2074057200
assert not any(n=="xdis" or n.startswith("tools.project7_draw_ir") for n in sys.modules)
print("ISOLATED_READONLY_CONSUMER_PASS")
'''
            r=subprocess.run([sys.executable,'-I','-c',code,str(root)],capture_output=True,text=True)
            self.assertEqual(r.returncode,0,r.stderr);self.assertIn('ISOLATED_READONLY_CONSUMER_PASS',r.stdout)
