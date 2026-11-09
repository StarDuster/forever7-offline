"""Finite original 640/P7 ordinary producer/RPC/consumer bodies; no game opcodes.
Actual Java ProtoLite/BSON frame parameters are decoded unchanged. Widget/audio,
city appearance, network call and pullEvents scheduling are explicit boundaries.
"""
from pathlib import Path
import base64,json,sys,textwrap,types,hashlib,io
from bson import BSON
ROOT=Path(__file__).resolve().parents[3];NS=types.SimpleNamespace
cases=json.loads(Path(sys.argv[1]).read_text());pins={}
def original(relative,name,env,indent=0,kind='def'):
 path=ROOT/relative;pins[relative]=hashlib.sha256(path.read_bytes()).hexdigest();lines=path.read_text().splitlines(True);prefix=' '*indent
 start=next(i for i,l in enumerate(lines) if l.startswith(prefix+kind+' '+name+('(' if kind=='def' else '')))
 end=next((i for i in range(start+1,len(lines)) if lines[i].strip() and not lines[i].startswith(prefix+' ') and not lines[i].startswith('\n')),len(lines))
 source=textwrap.dedent(''.join(l for l in lines[start:end] if not l.lstrip().startswith('print ')))
 if name=='completeEventReplyEnd':
  position=source.rfind('    return')
  source=source[:position]+'    if event == 1000 and gg.emergency.in_emergency:\n        gg.logic.leave_emergency()\n'+source[position:]
 exec(compile(source,str(path),'exec'),env);return env[name]
# Same original modules are byte-identical between P7 and Android640; sources
# below project only the selected methods, not Avatar/GameObject initialization.
for module in ['entity/ClientAvatar','entity/avatar_members/StoryMember','entity/avatar_members/ReliableRpcMember','lib/common/rpcdecorator','lib/common/RpcMethodArgs']:
 a=ROOT/'analysis/project7/scripts'/(module+'.marshal');b=ROOT/'analysis/android640-scripts'/(module+'.marshal');assert a.read_bytes()==b.read_bytes(),module
sys.path.insert(0,str(ROOT/'tools'))
from bytecode27 import read
from marshal27 import dumps
def functions(code):
 result={}
 for value in code.co_consts:
  if hasattr(value,'co_code'):result[value.co_name]=value;result.update(functions(value))
 return result
p7=functions(read(ROOT/'analysis/project7/scripts/entity/avatar_members/EventTriggerMember.marshal'));base=functions(read(ROOT/'analysis/android640-scripts/entity/avatar_members/EventTriggerMember.marshal'))
for name in ['completeEventReplyStart','pushEvents']:assert dumps(p7[name])==dumps(base[name]),name
# Actual P7 adds only independent event1000 emergency-leave tail to End.
# Project that exact tail below, never execute game bytecode on the host.
a=p7['completeEventReplyEnd'];b=base['completeEventReplyEnd']
assert a.co_code[:222]==b.co_code[:222] and a.co_names[:len(b.co_names)]==b.co_names and a.co_consts[:len(b.co_consts)]==b.co_consts
assert a.co_consts[-1]==1000 and a.co_names[-4:]==('emergency','in_emergency','logic','leave_emergency')
locks=set();events=[];sent=[]
ui=NS(lock=lambda name:locks.add(name),unlock=lambda name:locks.discard(name),panels=NS(settlement_fullscreen=NS(notify_reward=lambda *a:events.append('reward fullscreen boundary')),settlement_window=NS(notify_reward=lambda *a:events.append('reward window boundary'))))
gg=NS(ui=ui,emergency=NS(in_emergency=False),logic=NS(leave_emergency=lambda:events.append('leave emergency boundary')),city=NS(appear_daxuanwo=lambda:events.append('appear_daxuanwo boundary')),avatar_callback_map={},avatar_callback_need_result={})
env={'gg':gg,'xrange':range,'StandardError':Exception,'ConvertError':type('ConvertError',(Exception,),{}),'_logger':NS(warn=lambda *a:None,error=lambda *a:None),'CLIENT_STUB':3,'EntityManager':NS(getentity=lambda *a:None)}
args='analysis/original-py-640/lib/common/RpcMethodArgs.py'
for name in ['RpcMethodArg','NoLimit','NumeralLimit','Dict','Avatar','MailBox','Int','List']:original(args,name,env,kind='class')
rpc='analysis/original-py-640/lib/common/rpcdecorator.py';original(rpc,'RpcMethod',env,kind='class');decorate=original(rpc,'rpc_method',env)
env['utils']=NS(RotatedIdGenerator=NS(genid=lambda:73));env['helpers']=NS(toIntKeyDict=lambda value:value)
env['const']=NS(DAXUANWO_EVENT=417,RewardType=NS(EVENT=1));env['EventContentDataMod']=NS(data={417:{}});env['RESET_WEEK_EVENT']=NS(data={})
methods={}
for name,relative in [('callServerMethod','entity/ClientAvatar'),('requestTriggerDaXuanWo','entity/avatar_members/StoryMember'),('serverCallbackCarrier','entity/avatar_members/ReliableRpcMember'),('completeEventReplyStart','entity/avatar_members/EventTriggerMember'),('completeEventReplyEnd','entity/avatar_members/EventTriggerMember'),('pushEvents','entity/avatar_members/EventTriggerMember'),('pullEventsReply','entity/avatar_members/EventTriggerMember')]:methods[name]=original('analysis/original-py-640/'+relative+'.py',name,env,4)
for name,schema in [('serverCallbackCarrier',(env['Dict']('_r_'),)),('completeEventReplyStart',(env['Int']('e'),env['Dict']('r'))),('completeEventReplyEnd',(env['Int']('e'),)),('pushEvents',(env['List']('a'),env['List']('p'))),('pullEventsReply',(env['List']('a'),env['List']('p')))]:methods[name]=decorate(3,schema)(methods[name])
Client=type('ProjectedOriginalClientAvatar',(),methods);avatar=Client();gg.avatar=avatar;avatar.id=123;avatar.logger=NS(debug=lambda *a:None)
avatar.server=NS(call_server_method=lambda method,params,entityid:sent.append((method,dict(params))))
processing=set();avatar.eventTriggerData=NS(completedEvents=set(),delProcessingEvent=lambda event:processing.discard(event));avatar.checkEvents=lambda:events.append('original checkEvents/pull boundary');avatar.tryNotifyEvent=lambda:events.append('original tryNotifyEvent boundary')
avatar.requestTriggerDaXuanWo();assert locks=={'requestTriggerDaXuanWo'} and sent[-1][0]=='requestTriggerDaXuanWo';assert sent[-1][1]['_cbid_']==73
for row in cases['direct_success']:
 name=row['method'];payload=BSON(base64.b64decode(row['parameters_b64'])).decode()
 if name in methods:getattr(avatar,name)(payload)
assert 417 in avatar.eventTriggerData.completedEvents and 'appear_daxuanwo boundary' in events and not locks
assert not any(name.startswith('reliable') for name,params in sent)
# Negative is a genuine original callback unlock, with no completion mutation.
locks.add('requestTriggerDaXuanWo');gg.avatar_callback_map[91]=lambda *a:ui.unlock('requestTriggerDaXuanWo');before=set(avatar.eventTriggerData.completedEvents)
for row in cases['condition_negative']:
 if row['method']=='serverCallbackCarrier':avatar.serverCallbackCarrier(BSON(base64.b64decode(row['parameters_b64'])).decode())
assert not locks and avatar.eventTriggerData.completedEvents==before
data_init=original('analysis/original-py-640/entity/avatar_attrs/EventTriggerData.py','initFromDict',env,4)
restored=NS();data_init(restored,BSON(base64.b64decode(cases['reconnect_eventTrigger_b64'])).decode());assert 417 in restored.completedEvents
avatar.eventTriggerData=restored
if 'pull_events' in cases:
 locks.add('pullEvents')
 for row in cases['pull_events']:
  if row['method']=='pullEventsReply':avatar.pullEventsReply(BSON(base64.b64decode(row['parameters_b64'])).decode())
 assert 'pullEvents' not in locks and 417 in avatar.eventTriggerData.completedEvents
print('PASS actual ordinary StoryMember -> ClientAvatar callback registration -> original RPC conversion -> completeStart/End/push -> city boundary + callback unlock; negative unlock')
Path(sys.argv[2]).write_text(json.dumps({'status':'PASS','source_hashes':pins,'limitations':['finite function projection, not NeoX/GameObject/UI runtime','EventContent membership for the verified source node only','network, reward widgets, city appearance and pull scheduling are explicit seams','no client ACK/exactly-once claim']},indent=2)+'\n')
