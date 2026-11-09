"""Finite original producer/RPC/push/start bodies, actual Java BSON frames.
No NeoX opcode/JNI execution. Renderer/event panel/network are explicit seams.
"""
from pathlib import Path
import base64,json,sys,textwrap,types,hashlib,builtins
from bson import BSON
ROOT=Path(__file__).resolve().parents[3];NS=types.SimpleNamespace;pins={}
def original(relative,name,env,indent=0,kind='def'):
 path=ROOT/relative;pins[relative]=hashlib.sha256(path.read_bytes()).hexdigest();lines=path.read_text().splitlines(True);prefix=' '*indent
 start=next(i for i,line in enumerate(lines) if line.startswith(prefix+kind+' '+name+('(' if kind=='def' else '')))
 end=next((i for i in range(start+1,len(lines)) if lines[i].strip() and not lines[i].startswith(prefix+' ') and not lines[i].startswith('\n')),len(lines))
 source=textwrap.dedent(''.join(line for line in lines[start:end] if not line.lstrip().startswith('print ')))
 exec(compile(source,str(path),'exec'),env);return env[name]
sys.path.insert(0,str(ROOT));sys.path.insert(0,str(ROOT/'tools'))
from bytecode27 import read
from marshal27 import dumps
def functions(code):
 result={}
 for c in code.co_consts:
  if hasattr(c,'co_code'):result[c.co_name]=c;result.update(functions(c))
 return result
for module,names in [('entity/avatar_members/StoryMember',['requestStoryhuisu','syncRoute','syncHuiSuData']),('entity/avatar_members/EventTriggerMember',['pushEvents','canStartEvent','startEvent','tryNotifyEvent','filterProcessingEvents','getEventsWithPriority'])]:
 p7=functions(read(ROOT/'analysis/project7/scripts'/(module+'.marshal')));stock=functions(read(ROOT/'analysis/android640-scripts'/(module+'.marshal')))
 for name in names:assert dumps(p7[name])==dumps(stock[name]),(module,name)
# Use static literal reader only, not import original cdata or execute its code.
sys.path.insert(0,str(ROOT/'runtime/project7_dream_catalog'))
from produce import literal
data=literal(ROOT/'analysis/android640-scripts/com/data/cdata/event_content.marshal');entry=data[1258]
locks=set();sent=[];events=[];panels=[]
ui=NS(lock=lambda key,**kwargs:locks.add(key),unlock=lambda key:locks.discard(key),_tree=NS(proc_event=lambda *a,**kw:events.append(a[0])),panels=NS(city=NS(notify_huisu_enter=lambda:events.append('enter_animation_boundary')),city_event=NS(notify_events=lambda values:panels.append(list(values)))))
gg=NS(ui=ui,logic=NS(event_valid=True),battle=NS(_started=False),emergency=NS(in_emergency=False),avatar_callback_map={},avatar_callback_need_result={})
env={'unicode':str,'long':int,'gg':gg,'xrange':range,'filter':lambda fn,values:list(builtins.filter(fn,values)),'StandardError':Exception,'ConvertError':type('ConvertError',(Exception,),{}),'_logger':NS(warn=lambda *a:None,error=lambda *a:None),'CLIENT_STUB':3,'EntityManager':NS(getentity=lambda *a:None),'const':NS(DEBUG_SKIP_EVENT=False,EventCond=NS(COND_PREEVENT1=1)),'EventContentDataMod':NS(data={1258:entry})}
args='analysis/original-py-640/lib/common/RpcMethodArgs.py'
for name in ['RpcMethodArg','NoLimit','NumeralLimit','Dict','Avatar','MailBox','Int','List','Str','Bool']:original(args,name,env,kind='class')
rpc='analysis/original-py-640/lib/common/rpcdecorator.py';original(rpc,'RpcMethod',env,kind='class');decorate=original(rpc,'rpc_method',env)
env['helpers']=NS(toIntKeyDict=lambda value:value)
story='analysis/original-py-640/entity/avatar_members/StoryMember.py';event='analysis/original-py-640/entity/avatar_members/EventTriggerMember.py'
attrs={}
for name,source in [('requestStoryhuisu',story),('syncRoute',story),('syncHuiSuData',story),('pushEvents',event),('tryNotifyEvent',event),('filterProcessingEvents',event),('isEmergencyEvent',event),('filterEventWithClientLimit',event),('getEventsWithPriority',event),('canStartEvent',event),('startEvent',event),('serverCallbackCarrier','analysis/original-py-640/entity/avatar_members/ReliableRpcMember.py')]:attrs[name]=original(source,name,env,4)
for name,schema in [('syncRoute',(env['Str']('rt'),env['List']('srt'),env['Bool']('i'),env['Dict']('hsd'),env['Dict']('fbd'))),('syncHuiSuData',(env['Dict']('d'),)),('pushEvents',(env['List']('a'),env['List']('p'))),('serverCallbackCarrier',(env['Dict']('_r_'),))]:attrs[name]=decorate(3,schema)(attrs[name])
Avatar=type('FiniteOriginalAvatar',(),attrs);avatar=Avatar();gg.avatar=avatar;avatar.logger=NS(debug=lambda *a:None)
Story=type('FiniteOriginalStoryData',(),{name:original('analysis/original-py-640/entity/avatar_attrs/StoryData.py',name,env,4) for name in ['syncRoute','syncSubStoryTarget','syncHuisu','syncFlashback']})
avatar.storyData=Story();avatar.storyData.route='20';avatar.storyData.subRouteTarget=[];avatar.storyData.huisu=[];avatar.storyData.huisu_flag=False;avatar.storyData.flashback_flag=False;avatar.weeknumData=NS(daynum=0)
avatar.eventTriggerData=NS(availableEvents={},processingEventsServer=[],processingEventsClient=set(),completedEvents={1245},gmLockEvents=set())
callback_id=[73]
def reliable(method,params,callback=None):
 sent.append((method,dict(params)))
 if callback is not None:gg.avatar_callback_map[callback_id[0]]=callback
avatar.callServerMethodReliable=reliable
env['STORY_DREAM_DATA']=NS(data=literal(ROOT/'analysis/android640-scripts/com/data/cdata/story_dream.marshal'));env['EVENT_CONDITION_DATA']=NS(data=literal(ROOT/'analysis/android640-scripts/com/data/cdata/event_condition.marshal'))
# Original producer has empty parameters and its callback only unlocks.
assert avatar.requestStoryhuisu()['event']==1258;assert locks=={'requestStoryhuisu'} and sent==[('requestStoryhuisu',{})]
for row in json.loads(Path(sys.argv[1]).read_text())['entry']:
 if row['method']=='reliableRpcAck':continue  # transport ACK boundary, Java asserts it is first
 getattr(avatar,row['method'])(BSON(base64.b64decode(row['parameters_b64'])).decode())
assert avatar.storyData.huisu_flag and avatar.storyData.huisu_time==0 and not avatar.storyData.leave_huisu
assert events[0]=='enter_animation_boundary' and panels==[[1258]],(events,panels)
assert not locks and avatar.canStartEvent(1258)
assert avatar.startEvent(1258) and sent[-1]==('startEvent',{'e':1258}) and locks=={'startEvent'}
if 'entry_precommit_negative' in json.loads(Path(sys.argv[1]).read_text()):
 # Precommit typed negative still uses the original request callback unlock.
 locks.discard('startEvent');avatar.requestStoryhuisu();assert locks=={'requestStoryhuisu'}
 for row in json.loads(Path(sys.argv[1]).read_text())['entry_precommit_negative']:
  payload=BSON(base64.b64decode(row['parameters_b64'])).decode()
  if row['method']=='serverCallbackCarrier':avatar.serverCallbackCarrier(payload)
  else:assert row['method']=='showMessageStr' and payload['m']
 assert not locks
locks.discard('startEvent')
# Original typed same-day updateDay is the real negative unlock protocol.
ui.panels.city.notify_update_days=lambda **kw:events.append('update_day_widget_boundary')
ui.panels.bbs_home=NS(notify_inc_day=lambda:events.append('bbs_day_boundary'));ui.panels.city_3year=None
gg.city=NS(update_weekday=lambda:events.append('city_weekday_boundary'))
update_day=original('analysis/original-py-640/entity/avatar_members/WeekNumMember.py','updateDay',env,4)
Avatar.updateDay=decorate(3,(env['Int']('d'),))(update_day)
locks.add('updateDay');old_day=avatar.weeknumData.daynum
cases=json.loads(Path(sys.argv[1]).read_text())
for row in cases['night_negative']:
 if row['method']=='updateDay':avatar.updateDay(BSON(base64.b64decode(row['parameters_b64'])).decode())
assert 'updateDay' not in locks and avatar.weeknumData.daynum==old_day
locks.add('updateDay')
for row in cases['night_positive_day']:
 if row['method']=='updateDay':avatar.updateDay(BSON(base64.b64decode(row['parameters_b64'])).decode())
assert 'updateDay' not in locks and avatar.weeknumData.daynum==1
if 'patrol_begin' in cases:
 for name in ('patrol_friendly_request','enter_patrol_request'):
  setattr(Avatar,name,original('analysis/original-py-640/entity/avatar_members/CityMember.py',name,env,4))
 avatar.weeknumData.isFinalDay=lambda:False;avatar.cityData=NS(is_patrol_locked=lambda area:False)
 gg.logic.enable_event=lambda name:events.append('enable_'+name);gg.logic.disable_event=lambda name:events.append('disable_'+name);ui.enable_settlement=lambda value:events.append('settlement_boundary')
 for key in ('patrol_begin','patrol_begin_negative','patrol_claim_negative'):
  rows=cases[key];payloads=[(row['method'],BSON(base64.b64decode(row['parameters_b64'])).decode()) for row in rows]
  callback_id[0]=next(payload['_cbid_'] for name,payload in payloads if name=='serverCallbackCarrier')
  observed=[];before_budget=avatar.storyData.huisu_time
  if key=='patrol_claim_negative':avatar.patrol_friendly_request();assert 'patrolReward' in locks
  else:avatar.enter_patrol_request(4,[],cb=lambda:observed.append(avatar.storyData.huisu_time));assert 'patrol' in locks
  for name,payload in payloads:
   if name in ('syncHuiSuData','serverCallbackCarrier'):getattr(avatar,name)(payload)
  if key=='patrol_claim_negative':assert 'patrolReward' not in locks and avatar.storyData.huisu_time==before_budget
  else:
   expected=next(payload['d']['hst'] for name,payload in payloads if name=='syncHuiSuData')
   assert observed==[expected] and 'patrol' not in locks
print('PASS actual Java syncRoute -> syncHuiSuData -> original pushEvents/tryNotifyEvent processing-entry projection -> original startEvent producer; StoryMember callback unlock; original same-day negative updateDay unlock and genuine day-change projection; original CityMember budget-before-continuation and negative unlock when lifecycle cases supplied')
Path(sys.argv[2]).write_text(json.dumps({'status':'PASS','source_sha256':pins,'boundaries':['selected original function source projection, no game opcode','city enter animation and city_event notify renderer are explicit seams','startEvent network send captured; actual original Java startEvent idempotence tested separately','no native/UI/client ACK/exact-once assertion']},indent=2)+'\n')
