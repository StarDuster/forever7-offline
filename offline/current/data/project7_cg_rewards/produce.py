"""Pinned public-data producer from the reviewed static contract, never game execution.
Normal check consumes only bundled public-data.json; maintainer regeneration
requires the explicit reviewed contract. No independent source re-extraction is claimed.
"""
from pathlib import Path
import argparse,hashlib,json
ROOT=Path(__file__).resolve().parents[4]
HERE=Path(__file__).resolve().parent
JAVA=ROOT/'offline/current/java/android_core_rpc/src/com/project7/localmanager/CgRewardPlan.java'
MARSHAL_PINS={
'mainline_score_info':'dbab43659cd8a4c2983bc3ae46b340465b51b7b227c472523e4ac7d89a79ccff',
'reward_random':'8680b7d5a5e1befa9011647317c88fdaf63aff80889c36ed44f249678cd46262',
'reward_common':'e6433f6a6d521fa57fb98a3d49c3f5194f9c5268ecaf24e114b70e9e89114c29',
'item_data':'b498b2fc3f850d416fba2c7c9fb3930ddee680f30cd0d6eb5fb6f59c3ca114b6'}
CONST_PIN='926483f82a397faeb9002ba504e08461d7f36dc4dbb669d0789710a392909b0a'
BUNDLE_PIN='647a1ec62aa56d87a291ce1b9121cbd3a97cf5c00fa71e97d1f6e1d283080675'

def sha(data):return hashlib.sha256(data).hexdigest()
def encoded(data):return (json.dumps(data,sort_keys=True,separators=(',',':'))+'\n').encode('ascii')
def require(ok,message):
 if not ok:raise ValueError(message)
CONTRACT_PIN='e25fa5137b755b414b9108415cd422e695bb636cdb7ba09422a871599acc3219'
def project(contract):
 blob=Path(contract).read_bytes();require(sha(blob)==CONTRACT_PIN,'reviewed contract pin changed')
 data=json.loads(blob);evidence=data['data_evidence']
 lines=evidence['mainline_score_info']['line_cgs']
 require(len(lines)==32 and len({cg for values in lines.values() for cg in values})==74,'eligibility shape changed')
 require(data['cg']['reward']['kind']=='souvenir' and data['cg']['reward']['item_id']==329 and data['cg']['reward']['amount']==700,'reviewed reward changed')
 require(evidence['reward_random']['selected']['weights']==[[49770,10]],'random plan changed')
 require(evidence['reward_common']['selected']['items']==[329] and evidence['reward_common']['selected']['itemsNum']==[700],'common plan changed')
 require(all(evidence[name]['sha256']==pin for name,pin in MARSHAL_PINS.items()),'original table provenance changed')
 return {'format':'project7-cg-reward-plan-v1','projection':'reviewed-contract projection; not independent marshal re-extraction',
  'reviewed_contract_sha256':CONTRACT_PIN,'line_cgs':lines,'reward':{'kind':'souvenir','item':329,'amount':700,'random':11523,'common':49770},
  'original_table_sha256':MARSHAL_PINS,'const_source_sha256':CONST_PIN}
def java(data,pin):
 rows=',\n        '.join('{'+','.join(map(str,[int(k)]+values))+'}' for k,values in sorted(data['line_cgs'].items(),key=lambda x:int(x[0])))
 return '''package com.project7.localmanager;
/** Generated from pinned public tables by project7_cg_rewards/produce.py. */
final class CgRewardPlan {
    static final String SHA256 = "%s";
    static final int ITEM = 329, AMOUNT = 700;
    private static final int[][] LINES = {
        %s
    };
    static boolean eligible(int line, int cg) {
        for (int[] row : LINES) if (row[0] == line) {
            for (int i=1;i<row.length;i++) if (row[i]==cg) return true;
            return false;
        }
        return false;
    }
    private CgRewardPlan() {}
}
'''%(pin,rows)
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--contract',type=Path);p.add_argument('--write',action='store_true');a=p.parse_args()
 if a.write:
  require(a.contract,'explicit reviewed contract path required')
  data=project(a.contract);blob=encoded(data)
  require(not BUNDLE_PIN or sha(blob)==BUNDLE_PIN,'projected bundle differs from frozen plan')
  (HERE/'public-data.json').write_bytes(blob);JAVA.write_text(java(data,sha(blob)));print(sha(blob))
 else:
  blob=(HERE/'public-data.json').read_bytes();require(sha(blob)==BUNDLE_PIN,'bundled plan changed')
  require(JAVA.read_text()==java(json.loads(blob),BUNDLE_PIN),'generated Java differs');print('PASS bundled public-data and generated Java pins')
if __name__=='__main__':main()
