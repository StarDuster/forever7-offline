"""Public source-bound mandatory-trial client replay marker policy; no game execution."""
from pathlib import Path
import hashlib,json
R=Path(__file__).resolve().parents[4];HERE=Path(__file__).resolve().parent
catalog=R/'offline/current/data/project7_story_mission_catalog/catalog-v1.tsv';graph=R/'analysis/project7/manager/assets/event_graph.tsv'
pins=json.loads((R/'offline/current/data/project7_story_mission_catalog/pins.json').read_text())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();assert sha(catalog)==pins['outputs']['catalog-v1.tsv']
assert sha(graph)=='7a0f781c0a84b2fc46b1f71b0dcc6f85e80b4047ba415e8af25a08e97f11c9ba'
outcomes={}
for row in graph.read_text().splitlines():
 r=row.split('\t')
 if r[0]=='@outcome':outcomes[int(r[1])]=(int(r[2]),r[4])
mandatory={}
for row in catalog.read_text().splitlines():
 r=row.split('\t')
 if r[0]!='T':continue
 scene,event=int(r[1]),int(r[2]);outcome=outcomes.get(event)
 if not outcome or not outcome[1]:mandatory[str(scene)]=event
 else:assert outcome[0]==scene
policy={'schema':1,'policy':'mandatory-trial-rearm-v1','source_catalog_sha256':sha(catalog),'source_event_graph_sha256':sha(graph),'mandatory':mandatory}
raw=json.dumps(policy,sort_keys=True,ensure_ascii=True,separators=(',',':'));(HERE/'trial-ui-policy-v1.json').write_text(raw+'\n');print(hashlib.sha256(raw.encode('ascii')).hexdigest())
