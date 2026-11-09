"""Project exact official640 reset-week literals; no original game execution.
Normal builds consume the pinned TSV. Maintainer --write needs exact marshals.
"""
from pathlib import Path
import argparse,hashlib,json,sys
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3]
PINS={'reset_week_event':'67ae08ed2c999e314aa7551bc48c17d3501f450b7f0349e84bb4d44bf6c62da6','event_content':'0ddb80bbe56259a2f54acdb7accef49ad390240b0cac504ba1375a3c8976afe7','event_condition':'1ab7a968ebc01bccfa9419172ed92e91d9d491aa7288d616f2c8181de5389ec1'}
POLICY='event-reset-source-white-v1'
def sha(data):return hashlib.sha256(data).hexdigest()
def project(source):
 sys.path.insert(0,str(ROOT))
 from project7_dream_catalog.produce import literal
 tables={}
 for name,digest in PINS.items():
  path=source/(name+'.marshal')
  if sha(path.read_bytes())!=digest:raise ValueError('Original640 source changed: '+name)
  tables[name]=literal(path)
 reset,content,conditions=(tables[name] for name in PINS)
 lines=['P7EVENTRESET\t1\t'+POLICY];rows=[];seen=set()
 for event,row in sorted(reset.items()):
  white=row.get('white_screen_id')
  if type(event) is not int or row.get('event_id')!=event or type(white) is not int or min(event,white)<=0 or event in seen:raise ValueError('Event-reset row shape')
  if event not in content or white not in content:raise ValueError('Referenced content missing')
  e,w,c=content[event],content[white],conditions.get(white)
  flags=[int(bool(e.get('release'))),int(bool(w.get('release'))),int(bool(c and c.get('release')))]
  if not w.get('isAutoTriggerEvent') or not w.get('emergencyEvent') or w.get('eventType')!=1 or not w.get('completeConds',{}).get('dialog'):raise ValueError('White source runner shape')
  lines.append('\t'.join(map(str,['E',event,white]+flags)));seen.add(event)
  rows.append({'event':event,'white':white,'released':bool(all(flags)),'white_trigger_conditions':c.get('conds') if c else None,'white_dialogues':list(w['completeConds']['dialog'])})
 if len(rows)!=4:raise ValueError('Pinned family population changed')
 data=('\n'.join(lines)+'\n').encode('ascii')
 return data,{'format':'project7-event-reset-public-v1','policy':POLICY,'original_marshal_sha256':PINS,'asset_sha256':sha(data),'rows':rows,'semantics':'Explicit offline choice uses the source white_screen_id as original resetProgress entrance. Authorization uses actual server completion, release and current source epoch; does not re-run finished trigger conditions, invent a 417 gate or interpret condition4 as week. Original dialog/start/trace still required. Hidden official reset semantics are not claimed.'}
def main():
 p=argparse.ArgumentParser();p.add_argument('--source-dir',type=Path);p.add_argument('--write',action='store_true');a=p.parse_args()
 if a.write:
  if a.source_dir is None:raise ValueError('Explicit official640 source directory required')
  data,pins=project(a.source_dir);(HERE/'catalog-v1.tsv').write_bytes(data);(HERE/'pins.json').write_text(json.dumps(pins,indent=2)+'\n')
 else:
  pins=json.loads((HERE/'pins.json').read_text());assert sha((HERE/'catalog-v1.tsv').read_bytes())==pins['asset_sha256']
 print('PASS fixed event-reset catalog')
if __name__=='__main__':main()
