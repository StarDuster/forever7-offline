"""Pinned public640 dynamic-mechanism projection. No game code/state execution.
This is data preparation, not runtime readiness. Show-reward IDs never grant.
"""
import _bootstrap  # noqa: E402,F401
import argparse,calendar,gzip,hashlib,json,sys,zlib
from fractions import Fraction
from pathlib import Path
from _bootstrap import ROOT
if str(ROOT) not in sys.path:sys.path.insert(0,str(ROOT))
from project7_draw_history_ir.codec import canonical,typed,untyped
DEFAULT=ROOT/'offline/current/data/project7_dynamic_catalog'
POLICY='dynamic-resolve-on-reveal-offline-v1'
PINS={'chouka_info':'b0c2d54fabf49da649a1102d65e3417acfd9d25e94fb91ff603ebfd7f5eecc32','chouka_leiji_reward_index':'7fcecd1fc0ef1169249f365b24a4422622b0ed614bb1ceb6c93561a45806bec8','chouka_leiji_reward':'01245f95726f807eca4f3519ddebab39b0120d974d1ab75eff14bcf6e9181a72','chouka_jiaozhi':'d460c1c0c21338b663b8634a8d4d3f5cba5a99803717cba3222a13139e30f574','reward_random':'8680b7d5a5e1befa9011647317c88fdaf63aff80889c36ed44f249678cd46262','reward_common':'e6433f6a6d521fa57fb98a3d49c3f5194f9c5268ecaf24e114b70e9e89114c29','item_data':'b498b2fc3f850d416fba2c7c9fb3930ddee680f30cd0d6eb5fb6f59c3ca114b6','hero_treasure_generate':'771ceb6415660c9b9650b458f5b988ffb48c4cbf1344d059723a8affbd92b6b6','rule_info_data':'e62704f6169a8aac3b969a14ecfbb4ad0803638bdcf589ef150ab17319570832'}
# Frozen Terra review selects scope only; all reward data below comes from marshals.
SCOPE_SHA='1b734966f1a6a7d36a8347e4ba71bd24eaac395144a2eee5e61c5eb61905ea2e'
ASSET_SHA256='845e146b5fd19fc119ff79ebee6671755c35cfad9a41743003e1898e987b7c5e'
CONTRACT_SHA256='f1eb9e7d1110ed6b288537e6d32370d96cdc42f995c04e39bea2aaa3f46fa209'
BASE_SHA='b439ab44280a959cab8836595b65489fee3fd8482609ed3caa55477a66fd5c16'
MAX=32*1024*1024

def sha(b):return hashlib.sha256(b).hexdigest()
def require(ok,reason):
 if not ok:raise ValueError(reason)
def project(tables,scope):
 pools=[];commons={};randoms={};items={};designs={}
 def common(cid):
  require(type(cid) is int and cid in tables['reward_common'],'missing common '+str(cid))
  row=tables['reward_common'][cid];commons[cid]=row
  for identity in row.get('items',()):
   require(identity in tables['item_data'],'missing item');items[identity]=tables['item_data'][identity]
  if 'design_treasure' in row:
   identity=row['design_treasure'];require(identity in tables['hero_treasure_generate'],'missing design');definition=tables['hero_treasure_generate'][identity]
   doc=json.loads(definition['dumps_info']);require(doc['i']==definition['itemid'] and doc['tr']['cl']==definition['treasureClass'],'design binding')
   # Never distribute a source instance UUID as a grant template.
   designs[identity]={'source':typed({k:v for k,v in definition.items() if k!='dumps_info'}),'item':doc['i'],'tr':doc['tr']}
  return cid
 def random_reward(rid):
  require(type(rid) is int and rid in tables['reward_random'],'missing random '+str(rid))
  row=tables['reward_random'][rid];edges=[];total=0
  for cid,weight in row['weights']:
   require(type(weight) is int and weight>=0,'noninteger or negative weight')
   if not weight:continue
   common(cid);edges.append([cid,weight]);total+=weight
  require(total>0,'empty positive reward random')
  require(sum((Fraction(w,total) for _,w in edges),Fraction())==1,'weight mass')
  randoms[rid]={'raw':typed(row),'positive_edges':edges,'total':total}
  return rid
 for selected in scope:
  t=selected['wire_t'];raw=tables['chouka_info'][t];charge=[];interweave=[]
  for key,index in sorted(tables['chouka_leiji_reward_index'].items()):
   if key[0]!=t:continue
   threshold=key[1];rid=index['id'];row=tables['chouka_leiji_reward'][rid]
   require(row['drawType']==t and row['times']==threshold and index['drawType']==t and index['times']==threshold,'charge index mismatch')
   charge.append({'threshold':threshold,'row_id':rid,'grant_common_ids':[common(cid) for cid in row['rewards']],'raw':typed(row)})
  for key,row in sorted(tables['chouka_jiaozhi'].items()):
   if key[0]!=t:continue
   require(row['drawType']==t and row['id']==key[1],'jiaozhi key mismatch')
   file_binding=True
   for identity in row.get('hero_files',()):
    require(identity in tables['item_data'],'missing jiaozhi hero-file item')
    meta=tables['item_data'][identity];file_binding=file_binding and meta.get('memoryFrag',(None,))[0]==row['target_hero'];items[identity]=meta
   interweave.append({'hero_file_binding_valid':file_binding,'threshold':row['jiaozhi_count'],'row_id':key[1],'grant_random_ids':[random_reward(rid) for rid in row['rewards']],'raw':typed(row)})
  for group in (charge,interweave):require(len({r['threshold'] for r in group})==len(group),'duplicate threshold')
  extra=[]
  for hero,cid in raw.get('get_hero_extra_reward',()):extra.append({'hero':hero,'common':common(cid)})
  known=['base_hierarchy'];known+=['charge_thresholds'] if charge else [];known+=['jiaozhi_thresholds'] if interweave else []
  if extra:known.append('extra_reward_source')
  pools.append({'pool':t,'epoch':calendar.timegm(raw['end_time']),'raw':typed(raw),'rule':typed(tables['rule_info_data'].get(raw.get('rule_index'))),'charge':charge,'jiaozhi':interweave,'extra':extra,'known':known,'policy':['resolve-on-first-reveal','fixed-epoch','charge-per-real-primary','first-ownership-extra-includes-final-memory'],'missing':['runtime-pre-and-post-settlement','stock-reply-order-and-ui-sync']+(['jiaozhi-hero-file-source-binding'] if any(not j['hero_file_binding_valid'] for j in interweave) else [])+selected.get('reason',[]),'runtime_ready':False})
 return {'schema':'project7-dynamic-catalog-v1','policy':POLICY,'source_pins':PINS,'pools':pools,'common':typed(commons),'random':typed(randoms),'items':typed(items),'designs':typed(designs),'runtime_ready_ids':[]}

def base_projection(ids,path=ROOT/'offline/current/data/project7_history_catalog/catalog-v3.tsv'):
 raw=path.read_bytes();require(sha(raw)==BASE_SHA,'unsupported base graph')
 lines=[line.split('\t') for line in raw.decode('ascii').splitlines()[1:]]
 selected=[f for f in lines if f[0] in ('P','B','O','G') and int(f[1]) in ids]
 rids={int(f[-1]) for f in selected if f[0] in ('B','O')}
 edges=[f for f in lines if f[0]=='R' and int(f[1]) in rids]
 leaves={int(f[2]) for f in edges}
 defs=[f for f in lines if f[0]=='L' and int(f[1]) in leaves]
 require({int(f[1]) for f in defs}==leaves,'missing base leaf')
 return {'source_sha256':BASE_SHA,'records':selected+edges+defs,'normal_to_random_explicit':True,'leaf_count':len(leaves)}

def produce(source,output):
 require(not output.exists(),'existing output refused')
 from project7_dream_catalog.produce import literal
 tables={}
 for name,digest in PINS.items():
  p=source/(name+'.marshal');require(not p.is_symlink() and p.is_file() and p.stat().st_size<=64*1024*1024,'source path/limit');b=p.read_bytes();require(sha(b)==digest,'unsupported source '+name);tables[name]=literal(p)
 evidence=ROOT/'reports/terra-p7-remaining-draw-families-current.json';raw=evidence.read_bytes();require(sha(raw)==SCOPE_SHA,'unsupported scope report');scope=json.loads(raw)['pools']
 require(len(scope)==55 and len({r['wire_t'] for r in scope})==55,'scope55')
 data=project(tables,scope);data['base_graph']=base_projection({r['wire_t'] for r in scope});plain=canonical(data)+b'\n';require(len(plain)<=MAX,'expanded size');packed=gzip.compress(plain,compresslevel=9,mtime=0);packed=packed[:9]+b'\xff'+packed[10:]
 contract={'schema':'project7-dynamic-binding-v1','asset_sha256':sha(packed),'asset_size':len(packed),'expanded_sha256':sha(plain),'expanded_size':len(plain),'source_pins':PINS,'scope_report_sha256':SCOPE_SHA,'pool_count':55,'runtime_ready_ids':[]}
 output.mkdir(parents=True);(output/'catalog-v1.json.gz').write_bytes(packed);(output/'contract.json').write_bytes(canonical(contract)+b'\n');return contract

def load(directory=DEFAULT):
 directory=Path(directory);p=directory/'contract.json';require(p.is_file() and not p.is_symlink() and p.stat().st_size<=32768,'contract path/size');b=p.read_bytes();require(sha(b)==CONTRACT_SHA256,'contract pin');c=json.loads(b);p=directory/'catalog-v1.json.gz';require(p.is_file() and not p.is_symlink() and p.stat().st_size==c['asset_size']<=MAX,'asset path/size');b=p.read_bytes();require(sha(b)==ASSET_SHA256==c['asset_sha256'],'asset pin')
 z=zlib.decompressobj(31);plain=z.decompress(b,MAX+1);require(len(plain)<=MAX and z.eof and not z.unused_data and not z.unconsumed_tail,'decompression boundary');require(len(plain)==c['expanded_size'] and sha(plain)==c['expanded_sha256'],'expanded binding');d=json.loads(plain);require(d['source_pins']==PINS and len(d['pools'])==55 and not d['runtime_ready_ids'],'scope binding');return d

def main():
 p=argparse.ArgumentParser();p.add_argument('--source-dir',type=Path);p.add_argument('--output',type=Path);a=p.parse_args()
 if a.source_dir:
  require(a.output is not None,'explicit output required');print(json.dumps(produce(a.source_dir,a.output),sort_keys=True))
 else:print('PASS dynamic data pools='+str(len(load()['pools']))+' ready=0')
if __name__=='__main__':main()
