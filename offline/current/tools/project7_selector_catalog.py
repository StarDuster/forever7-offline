"""Fixed640 selector-item projection; no game execution or player data.
Producer reads pinned public marshals. Default consumer verifies bundled bytes.
Candidate policy is explicit fixed640 fallback, not historical rotation recovery.
"""
import _bootstrap  # noqa: E402,F401
from pathlib import Path
import argparse,calendar,hashlib,json,sys
from _bootstrap import ROOT;DEFAULT=ROOT/'offline/current/data/project7_selector_catalog'
POLICY='fixed640-shared-selector-roster-v1'
POOLS=(265,369,427,454,455,484)
PINS={'item_data':'b498b2fc3f850d416fba2c7c9fb3930ddee680f30cd0d6eb5fb6f59c3ca114b6','hero':'5fd8f55649e12030a76ec34d50fcf10b414fc07cb8055437177be8ecf29f771e','hero_self_choose_info':'664378ac922d2f0b288d8f70530ab92303de9f080d4e463dbbd9cda066c4aeb6','chouka_info':'b0c2d54fabf49da649a1102d65e3417acfd9d25e94fb91ff603ebfd7f5eecc32'}
CONTRACT_SHA256='43059e981492ca5a41e4545520a3e90ca74378e194242aca15dd65e7e40f6d72'
ASSET_SHA256='40a42441c3e55a179c931a4cb5e70a4e6e94e0913f4ef1eb654354a72341b6d7'
def sha(b):return hashlib.sha256(b).hexdigest()
def canonical(v):return json.dumps(v,ensure_ascii=True,sort_keys=True,separators=(',',':'),allow_nan=False).encode('ascii')
def require(b,why):
 if not b:raise ValueError(why)
def integer(x):require(type(x) is int and 0<x<=2147483647,'positive int32');return x

def compile_tables(items,heroes,roster,pools):
 rows=[];seen=set();metadata={}
 for identity,row in sorted(items.items()):
  sub=row.get('virtual_sub_type')
  if type(sub) is not int or sub not in range(61,68):continue
  identity=integer(identity);t=integer(row.get('card_pool'))
  require(row.get('type')==8 and row.get('subtype')==sub and t in POOLS,'selector item source shape')
  require((t,sub) not in seen,'duplicate selector pool/subtype');seen.add((t,sub))
  rows.append((identity,t,sub));metadata[str(identity)]=row
 require(seen=={(t,s) for t in POOLS for s in range(61,68)},'selector42 closure')
 candidates={3:[],4:[]}
 for identity,row in sorted(roster.items()):
  if row.get('avaliable')!=1:continue
  require(identity in heroes,'missing roster hero');rank=heroes[identity].get('hero_composite_init_rank')
  require(type(rank) is int and rank in candidates,'unsupported fallback rank');candidates[rank].append(integer(identity))
 require(all(candidates.values()),'empty S/A roster')
 lines=['P7SELECTOR\t1\t'+POLICY]
 for identity,t,sub in rows:lines.append('I\t%d\t%d\t%d'%(identity,t,sub))
 for rank in (4,3):
  for identity in candidates[rank]:lines.append('H\t%d\t%d'%(rank,identity))
 stamps={}
 for t in POOLS:
  row=pools[t];stamp=calendar.timegm(row['end_time']);require(0<stamp<=2147483647,'epoch int32');require(row.get('self_choose')==1,'pool selector source flag');stamps[str(t)]=stamp;lines.append('P\t%d\t%d'%(t,stamp))
 return ('\n'.join(lines)+'\n').encode('ascii'),{'policy':POLICY,'rows':len(rows),'roster_counts':{'S':len(candidates[4]),'A':len(candidates[3])},'pool_stamps':stamps,'selector_items':metadata,'roster_source':'original640 hero_self_choose_info.avaliable1 + hero initial rank4/3; not player owned filter, not historical rotation snapshot','stock484':'index included for audit only; runtime484 must delegate original candidates/choose/factory/spend/reveal'}

def produce(source,output):
 require(not output.exists(),'existing output refused')
 sys.path.insert(0,str(ROOT))
 from project7_dream_catalog.produce import literal
 from project7_draw_history_ir.codec import typed
 tables={}
 for name,digest in PINS.items():
  p=source/(name+'.marshal');require(p.is_file() and p.stat().st_size<64*1024*1024,'source size');require(sha(p.read_bytes())==digest,'unsupported source '+name);tables[name]=literal(p)
 asset,contract=compile_tables(tables['item_data'],tables['hero'],tables['hero_self_choose_info'],tables['chouka_info'])
 contract['selector_items']=typed(contract['selector_items']);contract['selector_rows_encoding']='literal-codec-v1'
 contract.update(schema='project7-selector-candidate-v1',source_marshal_sha256=PINS,asset_sha256=sha(asset),asset_size=len(asset),ready_claim=False)
 output.mkdir(parents=True);(output/'catalog-v1.tsv').write_bytes(asset);(output/'contract.json').write_bytes(canonical(contract)+b'\n')
 return contract

def verify(directory=DEFAULT):
 path=directory/'catalog-v1.tsv';require(path.is_file() and not path.is_symlink() and 0<path.stat().st_size<65536,'selector asset path/limit');raw=path.read_bytes();require(len(raw)<65536 and sha(raw)==ASSET_SHA256,'selector bundled asset hash')
 path=directory/'contract.json';require(path.is_file() and not path.is_symlink() and 0<path.stat().st_size<131072,'selector contract path/limit');contract_bytes=path.read_bytes();require(sha(contract_bytes)==CONTRACT_SHA256,'selector contract hash');c=json.loads(contract_bytes);require(c['source_marshal_sha256']==PINS and c['asset_sha256']==ASSET_SHA256 and c['asset_size']==len(raw),'selector contract binding')
 lines=raw.decode('ascii').splitlines();require(lines[0]=='P7SELECTOR\t1\t'+POLICY,'selector header')
 seen=set();ids=set();rosters={3:set(),4:set()};stamps={}
 for line in lines[1:]:
  f=line.split('\t')
  if f[0]=='I' and len(f)==4:
   identity,t,sub=map(int,f[1:]);require(identity not in ids and (t,sub) not in seen and t in POOLS and sub in range(61,68),'selector index duplicate/domain');ids.add(identity);seen.add((t,sub))
  elif f[0]=='H' and len(f)==3:
   rank,identity=map(int,f[1:]);require(rank in rosters and identity not in rosters[rank] and identity>0,'roster duplicate/domain');rosters[rank].add(identity)
  elif f[0]=='P' and len(f)==3:
   t,stamp=map(int,f[1:]);require(t in POOLS and t not in stamps and stamp==c['pool_stamps'][str(t)],'epoch domain');stamps[t]=stamp
  else:raise ValueError('unknown selector record')
 require(len(ids)==42 and len(stamps)==6 and all(rosters.values()),'selector incomplete')
 return c



def ui_policy(directory=DEFAULT):
 """Readonly loader projection, exact same fixed candidates/epochs as Java."""
 directory=Path(directory);contract=verify(directory);s=[];a=[]
 for line in (directory/'catalog-v1.tsv').read_text('ascii').splitlines():
  f=line.split('\t')
  if f[0]=='H':(s if f[1]=='4' else a).append(int(f[2]))
 ids=[t for t in POOLS if t!=484]
 return {'schema':'project7-selector-ui-v1','asset_sha256':ASSET_SHA256,'policy':POLICY,'ready_ids':ids,'s':s,'a':a,'epochs':{str(t):contract['pool_stamps'][str(t)] for t in ids}}

def audit_history():
 """Exact positive fixed IR closure for only this five-pool family; no reroll."""
 sys.path.insert(0,str(ROOT))
 from project7_draw_history_ir.consumer import load,CONTRACT_SHA256 as HISTORY_SHA
 from project7_draw_history_ir.codec import untyped
 from project7_history_catalog import leaf
 ir=load();rows=[]
 for row in ir['ui_pools']:
  t=row['wire_t']
  if t not in POOLS or t==484:continue
  require(row['rpc_family']=='six_cards' and untyped(row['raw']).get('times')==6 and row['base_total_resolved_mass']==[1,1],'selector complete outer mass/family')
  require(all(type(b['target']) is int and b['weight'][0]>0 and b['weight'][1]==1 for b in row['positive_base']),'selector outer refs')
  require(all(not d.get('unresolved') and (untyped(d['raw']).get('pool') is None or ('normal_row_id' in d and len(untyped(d['random_reward_refs']))==1)) for d in row['default_rows']),'selector default normal refs')
  selectors={};other={};common=set()
  for rid in row['referenced_random_ids']:
   require(str(rid) in ir['random_pools'],'missing random')
   for edge in ir['random_pools'][str(rid)]['branches']:
    require(edge['weight'][0]>0 and edge['weight'][1]>0,'nonpositive IR edge')
    cid=edge['target'];common.add(cid);node=ir['common_bundles'][str(cid)];raw=untyped(node['raw'])
    if node['component_fields']==['items'] and len(raw['items'])==1:
     identity=raw['items'][0];meta=untyped(node['references'].get('item:'+str(identity)))
     if meta and meta.get('type')==8 and meta.get('virtual_sub_type') in range(61,68):
      require(meta['card_pool']==t and raw['itemsNum']==(1,),'selector pool/count closure')
      selectors[str(identity)]={'subtype':meta['virtual_sub_type'],'source_pool':t,'count':1};continue
    kind=leaf(node)[0];other[kind]=other.get(kind,0)+1
  require(len(selectors)==7 and 'unsupported' not in other,'five-pool leaf closure incomplete')
  rows.append({'pool':t,'kind':row['kind'],'family':row['rpc_family'],'source_capability':row['capability'],'epoch_utc':row['epoch_utc'],'random_ids':row['referenced_random_ids'],'positive_unique_common_count':len(common),'selector_items':selectors,'nonselector_edge_kind_counts':other,'default_rows':row['default_rows'],'source_times':untyped(row['raw']).get('times')})
 require(len(rows)==5,'five selector pools missing')
 return {'schema':'project7-selector-positive-closure-v1','source_history_contract_sha256':HISTORY_SHA,'runtime_ready_claim':False,'pools':rows}

def main():
 p=argparse.ArgumentParser();p.add_argument('--source-dir',type=Path);p.add_argument('--output',type=Path);p.add_argument('--history-audit',type=Path);a=p.parse_args()
 if a.history_audit:
  require(not a.history_audit.exists(),'existing audit refused');a.history_audit.write_bytes(canonical(audit_history())+b'\n');print('PASS five selector pool positive closures');return
 if a.source_dir:
  require(a.output is not None,'explicit new producer output required');c=produce(a.source_dir,a.output)
 else:c=verify()
 print('PASS selector42 candidates S=%d A=%d asset=%s'%(c['roster_counts']['S'],c['roster_counts']['A'],c['asset_sha256']))
if __name__=='__main__':main()
