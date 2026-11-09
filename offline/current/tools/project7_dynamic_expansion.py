"""Versioned backend eligibility/repair projection; leaves fixed845e raw asset intact.
This is source-bound offline policy metadata, not native/UI acceptance or a new source table.
"""
import _bootstrap  # noqa: E402,F401
from pathlib import Path
import argparse,json,hashlib,sys
from _bootstrap import ROOT
if str(ROOT)not in sys.path:sys.path.insert(0,str(ROOT))
from project7_dynamic_catalog import load,ASSET_SHA256,BASE_SHA,PINS
from project7_draw_history_ir.codec import untyped
OUT=ROOT/'offline/current/data/project7_dynamic_catalog/expansion-policy-v1.json'
MISSING={42:5657,52:5981,62:6499,72:6767,81:6968,89:7366,107:7657}
SHAPE=(2,3,4)
TICKET_FREE=(362,488)
def project():
 source=load();family=[];repairs=[];nodes=source['base_graph']['records'];bases={};randoms={};leaves={}
 for r in nodes:
  if r[0]in('B','O'):bases.setdefault(int(r[1]),set()).add(int(r[4]))
  elif r[0]=='R':randoms.setdefault(int(r[1]),set()).add(int(r[2]))
  elif r[0]=='L':leaves[int(r[1])]=r
 for row in source['pools']:
  t=row['pool'];raw=untyped(row['raw'])
  if row['charge']and len(row['extra'])==1:
   assert raw.get('times')==6 and not any(k in raw for k in('inc_up_cnt_type','wish_sort','replace_reward','self_choose','is_up'))
   family.append(t)
   if any(not j['hero_file_binding_valid']for j in row['jiaozhi']):
    target=row['extra'][0]['hero'];pieces=set()
    for rid in bases[t]:
     for cid in randoms[rid]:
      leaf=leaves[cid]
      if leaf[2]=='memory'and int(leaf[3])==target:pieces.add(int(leaf[6]))
    assert pieces=={1,2,3}
    repairs.append({'pool':t,'target':target,'derived_pieces':sorted(pieces),'raw_item_tuples':[untyped(j['raw'])['hero_files']for j in row['jiaozhi']],'policy':'source-memory-closure-blessing-v1','retains_original_missing_piece':True,'repeats_uniform_only_among_actual_missing':True})
 assert len(family)==34 and 485 in family and {r['pool']for r in repairs}=={282,283,288}
 ids=sorted(set(family)|set(MISSING)|set(SHAPE)|set(TICKET_FREE))
 return {'schema':'project7-dynamic-backend-expansion-v1','raw_asset_sha256':ASSET_SHA256,'base_graph_sha256':BASE_SHA,'source_pins':PINS,'data_only_artifact':True,'backend_policy_ids':ids,'charge_extra_ids':family,'charge_only_shape_ids':[4],'legacy485':{'policy':'dynamic-resolve-on-reveal-offline-v1','decoder':'unchanged exact fixed845e; no discard or migrated entropy'},'family_policy':'dynamic-charge-extra-offline-v2','blessing_repairs':repairs,'missing_defaults':[{'pool':t,'normal':n,'ordinal':12,'policy':'archive-missing-default-base-v1','replacement':'same pool original base distribution, not S guarantee or same-number RR'}for t,n in MISSING.items()],'six_slot_archive':{'ids':list(SHAPE),'policy':'current640-six-slot-archive-v1','original2016_server_shape_claim':False},'ticket_only_source_offline_free':{'ids':list(TICKET_FREE),'policy':'history-free-v1','requires_public_ui_matching_ready_pin':True},'still_closed':[5,119,126,143,154,164,397,426,445],'public_ui_ready_proof':'owned by independent UI/main integration; backend eligibility alone does not prove it'}
def canonical(x):return(json.dumps(x,ensure_ascii=True,sort_keys=True,separators=(',',':'))+'\n').encode('ascii')
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--write',action='store_true');a=p.parse_args();expected=canonical(project())
 if a.write:OUT.write_bytes(expected)
 else:assert OUT.read_bytes()==expected
 print('PASS dynamic expansion policy ids='+str(len(project()['backend_policy_ids']))+' sha256='+hashlib.sha256(expected).hexdigest())
if __name__=='__main__':main()
