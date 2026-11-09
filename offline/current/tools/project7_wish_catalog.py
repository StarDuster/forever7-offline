"""Pinned public literal sidecar. No game opcode or player state execution."""
import _bootstrap  # noqa: E402,F401
import argparse,hashlib,json,sys
from pathlib import Path
from _bootstrap import ROOT
if str(ROOT) not in sys.path:sys.path.insert(0,str(ROOT))
from project7_dynamic_catalog import PINS as BASE_PINS,load
from project7_draw_history_ir.codec import typed,canonical
PINS={**BASE_PINS,'chouka_treasure_wish':'e0da090f3ba670f45d9161c0e2f59dacabe13b9a6aa173541757ad47ece9fee9','chouka_wish_treasure_choose':'b6bc05a699f67d3a561e57a378961bdb1c9791002e866d5a1d7f2bfde0b3c1ec','item_store_wish_change':'3fc33df12dd78688f9b92fe253638fa2009731c6d070f52cce95d56c9ae1e6a4','hero_treasure':'670c26a82b7632845550b50ed5c28c78401210412efaca21980612c4f9e89c9a','treasure_exclusive':'d99dcecb7f7c12796a9d367ca8b07f94adbe0f84cfba51c7056e696903d6ab6a','chouka_normal':'936b936c59212bba1eaffd910505354b8913f85ba38401d3463a65195a7e4c32'}
OUT=ROOT/'offline/current/data/project7_wish_catalog'
def sha(b):return hashlib.sha256(b).hexdigest()
def produce(source):
 from project7_dream_catalog.produce import literal
 tables={}
 for n,d in PINS.items():
  p=source/(n+'.marshal');assert p.is_file() and not p.is_symlink() and p.stat().st_size<=64*1024*1024 and sha(p.read_bytes())==d,n
  tables[n]=literal(p)
 wish=tables['chouka_treasure_wish'];choose=tables['chouka_wish_treasure_choose'];fee=tables['item_store_wish_change']
 assert (len(wish),len(choose),len(fee))==(143,117,6)
 common={};items={};designs={};display={}
 def design(i,dest):
  row=tables['hero_treasure_generate'][i];doc=json.loads(row['dumps_info']);assert doc['i']==row['itemid'] and doc['tr']['cl']==row['treasureClass']
  dest[i]={'source':typed({k:v for k,v in row.items() if k!='dumps_info'}),'item':doc['i'],'tr':doc['tr']}
 for row in list(wish.values())+list(choose.values()):
  assert len(row.get('reward',row.get('rewards',())))==1 or 'can_choose' not in row and 'drawType' not in row,'multi-common primary requires explicit semantics'
  for cid in row.get('reward',row.get('rewards',())):
   c=tables['reward_common'][cid];common[cid]=c
   for i in list(c.get('items',()))+list(c.get('treasure',())):items[i]=tables['item_data'][i]
   if c.get('design_treasure'):design(c['design_treasure'],designs)
  for k in ('show_id','treasure_design'):
   if row.get(k):design(row[k],display)
 for row in list(items.values()):
  for pair in row.get('reget_trans',()):
   if isinstance(pair,(tuple,list)) and pair:items.setdefault(pair[0],tables['item_data'][pair[0]])
 families=load()['pools'];dynamic=[p for p in families if p['pool'] in (5,119,126,143,154,164,397,426,445)]
 default_normals={int(row[3]) for row in load()['base_graph']['records'] if row[0]=='O' and int(row[1])in(5,119,126,143,154,164,397,426,445)}
 normals={i:r for i,r in tables['chouka_normal'].items() if r['type'] in (5,119,126,143,154,164,397,426,445) or i in default_normals};replacements={}
 for row in normals.values():
  for conditions,reward_ids in row.get('replace_reward',()):
   for rid in reward_ids:
    rr=tables['reward_random'][rid];replacements[rid]=rr
    assert sum(w for _,w in rr['weights'] if w>0)>0
    for cid,weight in rr['weights']:
     if weight<=0:continue
     c=tables['reward_common'][cid];common[cid]=c
     for i in list(c.get('items',()))+list(c.get('treasure',())):items[i]=tables['item_data'][i]
     if c.get('design_treasure'):design(c['design_treasure'],designs)
 exclusive={};base=load()['base_graph']['records']
 source_items={int(r[3]) for r in base if r[0]=='L' and r[2]=='treasure'}
 for common_row in common.values():
  source_items.update(common_row.get('treasure',()))
  if common_row.get('design_treasure'):source_items.add(designs[common_row['design_treasure']]['item'])
 for i in sorted(source_items):
  meta=tables['hero_treasure'].get((i,3),{});binding=[r for r in tables['treasure_exclusive'].values() if r.get('treasureId')==i]
  if not meta.get('validHeroes'):continue
  assert binding and tables['item_data'][i].get('reget_trans'),('exclusive reget missing',i)
  item=tables['item_data'][i];target,amount=item['reget_trans'];assert amount>0 and target in tables['item_data']
  items[i]=item;items[target]=tables['item_data'][target]
  exclusive[i]={'item':i,'quality':3,'reget_item':target,'reget_count':amount,'hero_treasure':typed(meta),'exclusive_rows':typed(binding)}
 up=[]
 for t in (397,426,445):
  up_normals=[r for r in tables['chouka_normal'].values() if r.get('type')==t and r.get('is_up')]
  assert len(up_normals)==1
  up.append({'pool':t,'raw_pool':typed(tables['chouka_info'][t]),'normal':typed(up_normals[0])})
 return {'schema':'project7-wish-source-v1','dynamic_sha256':'845e146b5fd19fc119ff79ebee6671755c35cfad9a41743003e1898e987b7c5e','source_pins':PINS,'wish':typed(wish),'choose':typed(choose),'fees':typed(fee),'common':typed(common),'items':typed(items),'grant_designs':typed(designs),'display_designs':typed(display),'dynamic':dynamic,'normals':typed(normals),'replacement_random':typed(replacements),'exclusive':typed(exclusive),'up':up,'policies':{'treasure':'wish-treasure-miss-reset-v1','groups':'wish-group-first-acquisition-v1','group_default':'wish-group-ordinal-residual-v1','replacement':'owned-subset-normal-replacement-v1','up':'shared-up-failure-seed-v1','payment':'history-free-v1','choose_fee':'source-yuanbao-only-v1','gift':'history-source-gift-daily-cap-v1','safe90':'fixed-wish-safe90-offline-v1'},'offline_policy':'wish-treasure-miss-reset-v1','default_scope':{'pool':5,'wish_id':1},'data_only_artifact':True}
def main():
 p=argparse.ArgumentParser();p.add_argument('--source-dir',type=Path);p.add_argument('--output',type=Path,default=OUT);a=p.parse_args()
 if a.source_dir:
  data=canonical(produce(a.source_dir))+b'\n';a.output.mkdir(parents=True,exist_ok=True);(a.output/'catalog-v1.json').write_bytes(data);(a.output/'contract-v1.json').write_bytes(canonical({'schema':1,'asset_sha256':sha(data),'bytes':len(data),'source_pins':PINS,'data_only_artifact':True})+b'\n');print(sha(data),len(data))
 else:
  c=json.loads((a.output/'contract-v1.json').read_text());b=(a.output/'catalog-v1.json').read_bytes();assert sha(b)==c['asset_sha256'] and len(b)==c['bytes'];print('PASS wish source143 choose117 fee6',sha(b))
if __name__=='__main__':main()
