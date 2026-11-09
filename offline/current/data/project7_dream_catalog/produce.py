"""Project fixed original640 public dream/condition literals; never execute game code.
Maintainer --write needs exact marshal inputs. Default checks bundled public data.
"""
from pathlib import Path
import argparse,base64,hashlib,json,sys
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3]
PINS={'story_dream':'17734bb2f674650a791d8ea2e78b133acdb2b4f10a246ae3216b375eeabb353c','event_condition':'1ab7a968ebc01bccfa9419172ed92e91d9d491aa7288d616f2c8181de5389ec1','event_content':'0ddb80bbe56259a2f54acdb7accef49ad390240b0cac504ba1375a3c8976afe7'}
def sha(data):return hashlib.sha256(data).hexdigest()
def literal(path):
 from bytecode27 import read
 from xdis.bytecode import Bytecode
 from xdis.opcodes import opcode_27
 aliases={'TD':'literal_dict','set':'literal_set','True':True,'False':False,'None':None}
 stack=[];started=False
 for number,ins in enumerate(Bytecode(read(path),opcode_27)):
  if number>=4000000 or len(stack)>200000:raise ValueError('Literal bound')
  op,count=ins.opname,ins.arg or 0
  if not started:
   if op=='STORE_NAME' and ins.argval=='_reload_all':started=True
   continue
  if op=='LOAD_CONST':stack.append(ins.argval)
  elif op=='LOAD_NAME':stack.append(aliases[ins.argval])
  elif op=='STORE_NAME':aliases[ins.argval]=stack.pop()
  elif op in ('BUILD_TUPLE','BUILD_LIST','BUILD_SET'):
   values=stack[-count:] if count else []
   if count:del stack[-count:]
   stack.append(tuple(values) if op=='BUILD_TUPLE' else set(values) if op=='BUILD_SET' else list(values))
  elif op=='BUILD_MAP':stack.append({})
  elif op=='STORE_MAP':
   key,value=stack.pop(),stack.pop();stack[-1][key]=value
  elif op=='BINARY_SUBSCR':
   key,value=stack.pop(),stack.pop();stack.append(value[key])
  elif op=='UNARY_NEGATIVE':stack.append(-stack.pop())
  elif op=='CALL_FUNCTION':
   if count not in (0,1):raise ValueError('Nonliteral call arity')
   value=stack.pop() if count else None;fn=stack.pop()
   if fn=='literal_dict' and count==1 and isinstance(value,dict):stack.append(dict(value))
   elif fn=='literal_set' and (count==0 or isinstance(value,(list,tuple,set))):stack.append(set(value or ()))
   else:raise ValueError('Nonliteral constructor')
  elif op=='RETURN_VALUE':
   if not isinstance(aliases.get('data'),dict):raise ValueError('No literal data')
   def validate(value,depth=0):
    if depth>100:raise ValueError('Literal nesting bound')
    if value is None or type(value) in (str,bool,int,float):return
    if isinstance(value,dict):
     for k,v in value.items():validate(k,depth+1);validate(v,depth+1)
    elif isinstance(value,(tuple,list,set)):
     for v in value:validate(v,depth+1)
    else:raise ValueError('Nonliteral value type')
   validate(aliases['data'])
   return aliases['data']
  else:raise ValueError('Nonliteral opcode '+op)
 raise ValueError('Truncated literal data')
def project(directory):
 sys.path.insert(0,str(ROOT));sys.path.insert(0,str(ROOT/'offline'/'current'/'tools'))
 tables={}
 for name,digest in PINS.items():
  p=directory/(name+'.marshal')
  if sha(p.read_bytes())!=digest:raise ValueError('Original public source changed: '+name)
  tables[name]=literal(p)
 story,conditions,content=(tables[n] for n in ('story_dream','event_condition','event_content'))
 lines=['P7DREAM\t1\tdream-three-patrol-offline-v1'];referenced=set()
 for (route,day),row in sorted(story.items()):
  entry,night=int(row.get('event',0)),int(row.get('goodnight_event',0))
  if (row['route'],row['date'])!=(route,day):raise ValueError('Dream key/body mismatch')
  lines.append('\t'.join(map(str,('D',route,day,entry,night,row.get('comp_type',0),row.get('subTarget_count',0)))))
  referenced.update(x for x in (entry,night) if x)
 sentinel={event for event,row in content.items() if row.get('dream_id')==('-1',)}
 if len(sentinel)!=47:raise ValueError('Dream sentinel population changed')
 referenced|=sentinel
 for event in sorted(referenced):
  if event not in content:raise ValueError('Referenced dream event missing')
  row=content[event];cond=conditions.get(event)
  lines.append('\t'.join(map(str,('E',event,int(event in sentinel),int(cond is not None),int(bool(row.get('release',False))),int(bool(cond and cond.get('release',False)))))))
  if cond:
   for code,value in sorted(cond.get('conds',{}).items()):
    if not isinstance(value,str):raise ValueError('Condition literal shape changed')
    lines.append('C\t%d\t%d\t%s'%(event,code,base64.b64encode(value.encode('utf-8')).decode('ascii')))
 data=('\n'.join(lines)+'\n').encode('ascii')
 return data,{'format':'project7-dream-public-v1','policy':'dream-three-patrol-offline-v1','original_marshal_sha256':PINS,'asset_sha256':sha(data),'story_rows':len(story),'sentinel_rows':len(sentinel),'event_rows':len(referenced),'source_semantics':'Literal dream_id exact string tuple only; not a grant of patrol/event authority. Conditions retained as original strings for original evaluator.'}
def main():
 p=argparse.ArgumentParser();p.add_argument('--source-dir',type=Path);p.add_argument('--write',action='store_true');a=p.parse_args()
 if a.write:
  if a.source_dir is None:raise ValueError('Explicit original public source dir required')
  data,pins=project(a.source_dir);(HERE/'catalog-v1.tsv').write_bytes(data);(HERE/'pins.json').write_text(json.dumps(pins,indent=2)+'\n')
 else:
  pins=json.loads((HERE/'pins.json').read_text())
  if sha((HERE/'catalog-v1.tsv').read_bytes())!=pins['asset_sha256']:raise ValueError('Bundled dream catalog mismatch')
 print('PASS fixed dream catalog')
if __name__=='__main__':main()
