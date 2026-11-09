"""Maintainer projection of pinned reviewed request binding + original640 condition.
Consumers use fixed request-events.tsv, never analysis or this producer's inputs.
"""
from pathlib import Path
import argparse,hashlib,json,sys
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
PINNED_INPUT_SHA256 = ('44947082bb601ed603c86a94ec9928026ed306fb7dd5633e7d7e0c4b26f06f67', '9965c150c89624b8adca1e23a83c70c6ad833bb7ff15ae384b8d7e41a70c860d', '7a0f781c0a84b2fc46b1f71b0dcc6f85e80b4047ba415e8af25a08e97f11c9ba', '78e6e3193c0f0a6f52d85c1d83bce332b4ba69893a18caa4ebabbd866673bd05')
def project(contract,condition,graph,producer):
 if tuple(sha(p) for p in (contract,condition,graph,producer)) != PINNED_INPUT_SHA256:raise ValueError('Pinned public sources changed')
 sys.path.insert(0,str(ROOT/'tools'))
 from read_data_table import read
 source=producer.read_text();assert 'gg.avatar.weeknumData.weeknum >= 3' in source and 'gg.avatar.requestTriggerDaXuanWo()' in source
 review=json.loads(contract.read_text());data=review['data_contract_417']
 content=data['event_content_417']['fields'];conditions=read(condition)
 # Binding is maintainer-reviewed public configuration, not an ID branch in Java.
 binding=review['request_admission_contract']['row_example'].split('\\t')
 name,event,kind=binding[:3];event=int(event)
 row=conditions[event];assert row['release'] and row['conds']=={42:'set([281])',4:'[0,0]',101:'0'}
 rows=[l.replace('\\t','\t').split('\t') for l in graph.read_text().splitlines()]
 node=next(r for r in rows if r[0]==str(event));assert node[1:]==['60','0','0','10','','']
 assert content['eventType']==int(kind) and not content['completeConds']
 trigger=['@trigger',str(event),'','','','','','0,0','3,2147483647','0','','','','42=281']
 fields=[name,hashlib.md5(name.encode()).hexdigest(),str(event),kind]+node[1:5]+['immediate','true']+trigger
 payload=('# request digest event type flags dialog newbee priority completion server_idle + original Trigger columns\n'+'\t'.join(fields)+'\n').encode('ascii')
 pins={'format':'project7-request-events-public-v1','producer':'reviewed-contract projection, independently read original640 condition literal and fixed graph row; eventType from reviewed original-content extraction','sources':{str(p):sha(p) for p in (contract,condition,graph,producer)},'payload_sha256':hashlib.sha256(payload).hexdigest(),'source_rule':'offline strict original-condition AND original producer week>=3 admission; client scene-only gates are not server facts'}
 return payload,pins
def main():
 p=argparse.ArgumentParser();p.add_argument('--contract',type=Path);p.add_argument('--condition',type=Path);p.add_argument('--graph',type=Path);p.add_argument('--producer-source',type=Path);p.add_argument('--write',action='store_true');a=p.parse_args()
 if a.write:
  if any(x is None for x in (a.contract,a.condition,a.graph,a.producer_source)):raise ValueError('Explicit pinned public inputs required')
  data,pins=project(a.contract,a.condition,a.graph,a.producer_source);(HERE/'request-events.tsv').write_bytes(data);(HERE/'pins.json').write_text(json.dumps(pins,indent=2)+'\n')
 else:
  pins=json.loads((HERE/'pins.json').read_text());assert sha(HERE/'request-events.tsv')==pins['payload_sha256']
 print('PASS fixed request-event catalog')
if __name__=='__main__':main()
