"""Pinned original public literal projection; never execute original game opcodes.
Default checks bundled data. Regeneration requires an explicit pinned cdata directory.
"""
import _bootstrap  # noqa: E402,F401
from pathlib import Path
import argparse,hashlib,json,sys
from _bootstrap import ROOT;OUT=ROOT/'offline/current/data/project7_baiye_catalog'
HERO_PIN='3acfd4335b3a8b0e7e32c051712c2e172c553c20155c8faf89503641238725a0'
PIN='b498b2fc3f850d416fba2c7c9fb3930ddee680f30cd0d6eb5fb6f59c3ca114b6'
def project(directory):
 sys.path.insert(0,str(ROOT));sys.path.insert(0,str(ROOT/'offline'/'current'/'tools'))
 from project7_dream_catalog.produce import literal
 source=directory/'item_data.marshal';assert hashlib.sha256(source.read_bytes()).hexdigest()==PIN
 items=literal(source);rows=[]
 for identity,row in sorted(items.items()):
  rule=row.get('fusion')
  if rule:
   assert len(rule)==2 and all(type(n)is int and n>0 for n in rule) and identity!=rule[1] and rule[1]in items
   rows.append((identity,*rule))
 assert rows==[(10313,4,10314),(10314,4,10315),(10315,4,10316)],rows
 return ('P7BAIYE\t1\tstock-item-fusion-v1\n'+''.join('F\t%d\t%d\t%d\n'%r for r in rows)).encode('ascii')
def fragments(directory):
 sys.path.insert(0,str(ROOT));sys.path.insert(0,str(ROOT/'offline'/'current'/'tools'))
 from project7_dream_catalog.produce import literal
 hero=directory/'chouka_hero_file.marshal';assert hashlib.sha256(hero.read_bytes()).hexdigest()==HERO_PIN
 item=directory/'item_data.marshal';assert hashlib.sha256(item.read_bytes()).hexdigest()==PIN
 heroes=literal(hero);items=literal(item);assert len(heroes)==138
 rows=['P7BAIYEFRAG\t1\tvoucher-one-stock-memory-v1']
 for identity,row in sorted(heroes.items()):
  count=row.get('file_num',0);assert type(count)is int and 0<=count<=3
  rows.append('H\t%d\t%d\t%d\t%d\t%d'%(identity,count,row['exchange'],row['hero_exchange'],row['jj_hero_exchange']))
 kinds={6:0,7:0}
 for identity,row in sorted(items.items()):
  kind=row.get('use_type')
  if kind not in kinds:continue
  choices=tuple(row['select_heroes']) if kind==6 else (row['heroid'],)
  assert choices and all(type(n)is int and n in heroes for n in choices)
  kinds[kind]+=1;rows.append('V\t%d\t%d\t%s'%(identity,kind,','.join(map(str,choices))))
 assert kinds=={6:17,7:4},kinds
 return ('\n'.join(rows)+'\n').encode('ascii')
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--cdata',type=Path);p.add_argument('--write',action='store_true');a=p.parse_args()
 if a.write:
  assert a.cdata;data=project(a.cdata);OUT.mkdir(exist_ok=True);(OUT/'catalog-v1.tsv').write_bytes(data)
  fragment=fragments(a.cdata);(OUT/'fragments-v1.tsv').write_bytes(fragment)
  (OUT/'fragment-pins-v1.json').write_text(json.dumps({'schema':1,'policy':'voucher-one-stock-memory-v1','offline_policy':'consume one owned source voucher, no extra24 fee; not official hidden server proof','source_item_data_sha256':PIN,'source_hero_file_sha256':HERO_PIN,'catalog_sha256':hashlib.sha256(fragment).hexdigest(),'heroes':138,'selectors':17,'named_vouchers':4},indent=2)+'\n')
  (OUT/'pins-v1.json').write_text(json.dumps({'schema':1,'source_item_data_sha256':PIN,'catalog_sha256':hashlib.sha256(data).hexdigest(),'projection':'exact pinned literal subset, no game execution','rows':3},indent=2)+'\n')
 else:
  pins=json.loads((OUT/'pins-v1.json').read_text());assert hashlib.sha256((OUT/'catalog-v1.tsv').read_bytes()).hexdigest()==pins['catalog_sha256'];fragment=json.loads((OUT/'fragment-pins-v1.json').read_text());assert hashlib.sha256((OUT/'fragments-v1.tsv').read_bytes()).hexdigest()==fragment['catalog_sha256'];print('PASS fixed Baiye catalogs')
if __name__=='__main__':main()
