"""Finite original producer/reset reply/actual avatar payload consumer.
No NeoX opcodes or renderer. Real payloads are synthetic public-template accounts.
"""
from pathlib import Path
import base64,json,sys,textwrap,types,hashlib,zlib,msgpack
from bson import BSON,json_util
ROOT=Path(__file__).resolve().parents[3];NS=types.SimpleNamespace;pins={}
def original(relative,name,env,indent=0,kind='def'):
 p=ROOT/relative;pins[relative]=hashlib.sha256(p.read_bytes()).hexdigest();lines=p.read_text().splitlines(True);prefix=' '*indent
 start=next(i for i,l in enumerate(lines)if l.startswith(prefix+kind+' '+name+('('if kind=='def'else'')));end=next((i for i in range(start+1,len(lines))if lines[i].strip()and not lines[i].startswith(prefix+' ')and not lines[i].startswith('\n')),len(lines))
 src=textwrap.dedent(''.join(l for l in lines[start:end]if not l.lstrip().startswith('print ')));exec(compile(src,str(p),'exec'),env);return env[name]
locks=set();sent=[];queue=[];events=[]
gg=NS(ui=NS(lock=lambda key:locks.add(key),unlock=lambda key:locks.discard(key)),logic=NS(enter_emergency=lambda:events.append('enter_emergency_boundary')),city_container=NS(cur_scene_key='city',pop_and_push_scene=lambda key:events.append('scene_boundary')))
env={'gg':gg,'const':NS(StoryRouteConst=NS(ZHOUNIAN2_WEEK_REFRESH_EVENTID=1267),DAXUANWO_EVENT=417,SCENE_CITY='city'),'xrange':range,'StandardError':Exception,'helpers':NS(toIntKeyDict=lambda d:d),'zlib':zlib,'json_util':json_util,'msgpack':NS(loads=lambda data,object_hook:msgpack.unpackb(data,raw=False,strict_map_key=False,object_hook=object_hook)),'CLIENT_STUB':3,'Avatar':type('Avatar',(),{}),'MailBox':type('MailBox',(),{}),'_logger':NS(warn=lambda *a:None,error=lambda *a:None)}
for name in ('ConvertError','RpcMethodArg','BinData'):original('analysis/original-py-640/lib/common/RpcMethodArgs.py',name,env,kind='class')
original('analysis/original-py-640/lib/common/rpcdecorator.py','RpcMethod',env,kind='class');decorate=original('analysis/original-py-640/lib/common/rpcdecorator.py','rpc_method',env)
attrs={name:original('analysis/original-py-640/'+module+'.py',name,env,4)for name,module in [('handleResetWeek','entity/avatar_members/EventTriggerMember'),('handleResetWeekReply','entity/avatar_members/WeekNumMember'),('updateClientAvatarAsk','entity/ClientAvatar'),('updateClientAvatarReply','entity/ClientAvatar')]}
attrs['handleResetWeekReply']=decorate(3,())(attrs['handleResetWeekReply']);attrs['updateClientAvatarReply']=decorate(3,(env['BinData']('s'),))(attrs['updateClientAvatarReply']);Avatar=type('FiniteOriginalResetAvatar',(),attrs)
init_events=original('analysis/original-py-640/entity/avatar_attrs/EventTriggerData.py','initFromDict',env,4)
gg.exec_delay=lambda ms,fn:queue.append(fn)
for source,cases in json.loads(Path(sys.argv[1]).read_text()).items():
 source=int(source);avatar=Avatar();gg.avatar=avatar;avatar.eventTriggerData=NS(completedEvents={source});avatar.callServerMethod=lambda name,p:sent.append((name,dict(p)));avatar.avatarClientDataSave=lambda:events.append('client_save_boundary');avatar.avatarClientDataLoad=lambda:events.append('client_load_boundary');avatar.on_entity_creation=lambda:events.append('entity_creation_boundary')
 def init_from_dict(data):
  init_events(avatar.eventTriggerData,data['eventTrigger'])
 avatar.init_from_dict=init_from_dict
 avatar.handleResetWeek(source);assert 'handleResetWeek'in locks and queue
 queue.pop(0)();assert not locks and sent[-1]==('handleResetWeek',{'e':source})
 # Source1267 can send from CITY without417, exactly as original producer.
 assert 417 not in avatar.eventTriggerData.completedEvents
 for row in cases['reset']:
  if row['method']=='handleResetWeekReply':avatar.handleResetWeekReply(BSON(base64.b64decode(row['parameters_b64'])).decode())
 assert sent[-1]==('updateClientAvatarAsk',{}) and hasattr(avatar,'updateClientAvatarCb')
 for row in cases['avatar']:
  if row['method']=='updateClientAvatarReply':avatar.updateClientAvatarReply(BSON(base64.b64decode(row['parameters_b64'])).decode())
 assert avatar.updateClientAvatarCb is None and cases['white']in avatar.eventTriggerData.availableEvents and source not in avatar.eventTriggerData.completedEvents
 assert events[-1]=='enter_emergency_boundary'
print('PASS original direct delayed reset producer (CITY1267 without417), reset reply -> original avatar ask/reply with actual payload -> explicit white available -> emergency callback boundary')
Path(sys.argv[2]).write_text(json.dumps({'status':'PASS','source_sha256':pins,'limits':['selected original source bodies, no game opcode/render/JNI','entity init/client local save/load and emergency renderer are explicit boundaries','actual payload decoding and original EventTriggerData projection retained','no cross-epoch exactly-once assertion']},indent=2)+'\n')
