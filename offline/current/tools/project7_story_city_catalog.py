"""Fixed public city/chapter/menu projection. Consumer uses bundled data only."""
import _bootstrap  # noqa: E402,F401
from pathlib import Path
import argparse,gzip,hashlib,json,re,sys
from _bootstrap import ROOT
if str(ROOT) not in sys.path:sys.path.insert(0,str(ROOT))
DEFAULT=ROOT/'offline/current/data/project7_story_city_catalog'
SCHEMA='project7-story-city-v1'
ASSET_SHA256='af2328b97372c27fd392b5b399d03daa17fa73acdd35d2b1ad5b0a8f07218069'
PINS={'city_data':'155ebc4d9c63c15fa921b8b3753617ef6c1d4cde2604a72263798e46c7aa775f','chapter_mission_data':'c637bbf1665c8118b238c702145a22df0ceaf860bdf80595edbcf0d20882cdb4','mission':'2019aab0289ffdac6aacde82b21cd283ef0c8d8afb6bb264d087e8cde262390f','mainline_score_info':'dbab43659cd8a4c2983bc3ae46b340465b51b7b227c472523e4ac7d89a79ccff','coc_area_link_data':'ef14e11a29bce26f5d96bf440245437ee870f5a133e42e05e3acf1a1171e4889','event_content':'0ddb80bbe56259a2f54acdb7accef49ad390240b0cac504ba1375a3c8976afe7','mission_hero_attr':'25647eaa103bb23bc22c27910e1f119e7ed2f169f52ac440dee69f573a60cc8b'}
FIELDS=('areaFree','areaFight','areaLock','areaUnlock')
def sha(b):return hashlib.sha256(b).hexdigest()
def canonical(x):return json.dumps(x,sort_keys=True,ensure_ascii=True,separators=(',',':'),allow_nan=False).encode('ascii')
def require(v,s):
 if not v:raise ValueError(s)
def pairs(rows):
 x={}
 for k,v in rows:require(k not in x,'Duplicate JSON key');x[k]=v
 return x
def load(directory=DEFAULT):
 import zlib
 b=(Path(directory)/'catalog-v1.json.gz').read_bytes();require(len(b)<1000000 and sha(b)==ASSET_SHA256,'Unsupported story city component');d=zlib.decompressobj(31);raw=d.decompress(b,4000001);require(len(raw)<=4000000 and d.eof and not d.unused_data,'Story city decompression bound');x=json.loads(raw,object_pairs_hook=pairs);require(x['schema']==SCHEMA,'Story city schema');return x

def project(source,graph,chapters):
 from project7_dream_catalog.produce import literal
 tables={};source=Path(source)
 for name,digest in PINS.items():
  p=source/(name+'.marshal');b=p.read_bytes();require(sha(b)==digest,'Unsupported source '+name);tables[name]=literal(p)
 raw_graph=Path(graph).read_bytes();raw_chapters=Path(chapters).read_bytes();route_keys=set();base_chapters=[]
 for line in raw_chapters.decode().splitlines():
  r=line.split('\t')
  if r[0]=='C':route_keys.add(r[3]);base_chapters.append((int(r[1]),int(r[2]),r[3],int(r[4])))
 require(len(base_chapters)==39 and len(route_keys)==13,'Base chapter selector changed')
 edges={};routes={};trigger_routes={};raw_rows={}
 for line in raw_graph.decode().splitlines():
  r=line.split('\t')
  if r[0].isdigit():
   require(len(r)==7,'Event row schema');eid=int(r[0]);require(eid not in edges,'Duplicate event');edges[eid]=[int(v) for v in r[5].split(',')if v];raw_rows[eid]=r
  elif r[0]=='@route':require(len(r)==3 and int(r[1])not in routes,'Route row');routes[int(r[1])]=r[2]
  elif r[0]=='@trigger':
   for token in r[-1].split(';'):
    if token.startswith('52='):trigger_routes[int(r[1])]=set(token[3:].split(','))
 def closure(seeds):
  seen=set();queue=list(seeds)
  while queue:
   eid=queue.pop();require(len(seen)<100000,'Graph bound')
   if eid in seen:continue
   require(eid in edges,'Missing event reference '+str(eid));seen.add(eid);queue.extend(edges[eid])
  return seen
 menus=[];scope_menus=[];scope_events=set()
 for menu,row in sorted(tables['mainline_score_info'].items()):
  init=row.get('init_event',0);reachable=closure([init]) if init in edges else set();tags={routes[e]for e in reachable if e in routes};candidate=bool(tags&route_keys)
  seed=reachable|{e for e,rs in trigger_routes.items()if rs&route_keys} if candidate else reachable
  dependency=closure(seed) if seed else set()
  if candidate:scope_menus.append(menu);scope_events.update(dependency)
  menus.append({'id':menu,'init':init,'requires':row.get('requires',()),'level':row.get('level',0),'name':row.get('name',''),'candidate':candidate,'city_ready':candidate,'ready':False,'missing':['mechanism-consumer-proof-pending']if candidate else ['outside-current-shared-city-scope'],'route_keys':sorted(route_keys)if candidate else sorted(tags),'events':sorted(dependency)if candidate else []})
 require(scope_menus,'No source menu reaches selector routes')
 selected=[];mission_ids=set();areas=tables['city_data'];missions=tables['mission']
 for key,row in sorted(tables['chapter_mission_data'].items()):
  if key[2] not in route_keys or key[1]!=0 or key[3]!=0:continue
  require(key[0] in areas and key==(row['chapter'],row['specialStage'],row['route'],row['status']),'Chapter key mismatch');groups=row['section'];require(set(groups)==set(range(10)),'Chapter section schema');scenes=[s for i in range(10)for s in groups[i]];require(scenes and all(len(groups[i])<=1 for i in range(10)),'Unsupported chapter group')
  virtual=areas[key[0]].get('virtual',0)==1
  if virtual:require(all(missions[s].get('system_type')==2 and missions[s].get('type')==10 and missions[s].get('release')==1 for s in scenes),'Unsupported virtual family')
  elif key not in base_chapters and not (key[2] in route_keys and key[0] in (2,4,6)):continue
  selected.append({'area':key[0],'special':key[1],'route':key[2],'status':key[3],'groups':[groups[i]for i in range(10)],'kind':'virtual'if virtual else 'normal'});mission_ids.update(scenes)
 def inherited(s,chain=()):
  require(s not in chain and s in missions,'Mission inheritance');row=missions[s];parent=row.get('inherit_mission');return dict(inherited(parent,chain+(s,))if parent else {},**row)
 targets={};economy=[]
 for s in sorted(mission_ids):
  row=inherited(s);virtual=areas[row['ch']].get('virtual',0)==1;party=row.get('target_hero',()) or ();coc=bool(party);require(not coc or len(party)<=row.get('max_hero_num',3),'COC cast closure');fields=[row.get(n,d)for n,d in [('va',0),('fatigue',0),('overFatigue',0),('force_recommend',0),('least_hero_num',1),('max_hero_num',3),('prize',1)]]
  require(all(type(v)is int and v>=0 for v in fields),'Mission economy type');targets[str(s)]={'area':row['ch'],'wire':1,'party':party,'minimum':fields[4],'maximum':fields[5],'kind':'virtual'if virtual else ('coc' if coc else 'normal'),'mission':row,'mission_hero_override':tables['mission_hero_attr'].get((s,party[0])) if party else None,'economy':fields}
  if virtual or coc:economy.append('\t'.join(map(str,['M',s]+fields)))
 effects={}
 for eid in sorted(scope_events):
  row=tables['event_content'].get(eid,{})
  effect={f:row[f]for f in FIELDS if row.get(f)}
  if effect:
   require(all(type(a)is int and a in areas for values in effect.values()for a in values),'Unknown effect area');effects[str(eid)]=effect
 links=[dict(row,id=k)for k,row in sorted(tables['coc_area_link_data'].items())]
 area_rows=[dict(raw=row,id=a,kind='virtual'if row.get('virtual')==1 else ('normal'if row.get('show_build')==1 and row.get('show_upgrade')==1 else 'auxiliary'))for a,row in sorted(areas.items())]
 return {'schema':SCHEMA,'source_pins':PINS,'base_graph_sha256':sha(raw_graph),'base_chapter_sha256':sha(raw_chapters),'policy':'source-city-normal-and-coc-v1','namespace':'q7StoryCity','route_keys':sorted(route_keys),'menus':menus,'areas':area_rows,'chapters':selected,'missions':targets,'effects':effects,'links':links,'economy_extra':economy,'capabilities':{'city':True,'snapshot':False,'virtual_battle':False,'menu_entry':False},'scope_menus':scope_menus,'public_ready_ids':[]}

def produce(source,graph,chapters,output):
 output=Path(output);require(not output.exists(),'Existing output refused');data=project(source,graph,chapters);raw=canonical(data);packed=gzip.compress(raw,mtime=0);output.mkdir(parents=True)
 (output/'catalog-v1.json.gz').write_bytes(packed);(output/'economy-extra.tsv').write_text('\n'.join(data['economy_extra'])+'\n');contract={'schema':SCHEMA,'asset_sha256':sha(packed),'asset_size':len(packed),'expanded_sha256':sha(raw),'source_pins':PINS,'base_graph_sha256':data['base_graph_sha256'],'base_chapter_sha256':data['base_chapter_sha256'],'scope_menus':data['scope_menus'],'areas':len(data['areas']),'chapters':len(data['chapters']),'missions':len(data['missions']),'effects':len(data['effects']),'ready_ids':[]};(output/'contract-v1.json').write_text(json.dumps(contract,indent=2)+'\n');return contract

def main():
 p=argparse.ArgumentParser();p.add_argument('--source',type=Path);p.add_argument('--graph',type=Path);p.add_argument('--chapters',type=Path);p.add_argument('--output',type=Path);a=p.parse_args()
 if a.source:
  if not(a.graph and a.chapters and a.output):p.error('produce requires source/graph/chapters/output')
  print(json.dumps(produce(a.source,a.graph,a.chapters,a.output),sort_keys=True))
 else:
  x=load();print(json.dumps({'scope_menus':x['scope_menus'],'chapters':len(x['chapters']),'ready':x['public_ready_ids']}))
if __name__=='__main__':main()
