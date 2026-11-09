"""Actual original640 set/clear/reward/result-panel retry and giveup bodies."""
import importlib.util,json,sys,types
from pathlib import Path
R=Path(__file__).resolve().parents[3];sys.path.insert(0,str(R));N=types.SimpleNamespace
spec=importlib.util.spec_from_file_location('original_ui',R/'tests/test_project7_furniture_ui.py');h=importlib.util.module_from_spec(spec);spec.loader.exec_module(h)
events=[];prompts=[];sent=[];gg=N();env={'gg':gg,'CombatData':N(STATE_OFFLINE=4),'STATE_NONE':0,'STATE_OFFLINE':4,'LOST_NONE':0,'const':N(BattleType=N(EVENT=2))}
D=type('Data',(),{})
for name in ('setState','setLost','reset'):setattr(D,name,h.original('analysis/original-py-640/entity/avatar_attrs/CombatData.py',name,env))
B=type('BattleData',(),{});B.initFromDict=h.original('analysis/original-py-640/entity/avatar_attrs/BattleStageData.py','initFromDict',env)
A=type('Avatar',(),{})
for name in ('setEventBattleStage','clearEventBattleStage','battleRealFailWithEventMode'):setattr(A,name,h.original('analysis/original-py-640/entity/avatar_members/BattleStageMember.py',name,env))
A.combatOfflineReward=h.original('analysis/original-py-640/entity/avatar_members/CombatMember.py','combatOfflineReward',env)
a=A();gg.avatar=a;a.combatData=D();a.battleStageData=B();a.battleStageData.initFromDict({'ab':[[315,3]]});a.logger=N(info=lambda *args:None);a.callServerMethod=lambda m,p:sent.append((m,p));a.isA179RoleTryScene=lambda sid:False;a.battleEnterWithEventMode=lambda sid:sent.append(('retry-entry',sid));a.battleOfflineOnReward=lambda *args:events.append(('reward',args))
confirm=N(valid=False,destroy=lambda:None,notify_confirm=lambda code,**kwargs:prompts.append((code,kwargs)))
gg.ui=N(panels=N(common_confirm=confirm),enable_settlement=lambda *a:None);gg.logic=N(interface_visible=lambda *a,**kw:None,enter_city=lambda:events.append('city'),enter_emergency=lambda:events.append('emergency'));gg.emergency=N(in_emergency=False);gg.posteffect_mgr=N(enable_screen_gray=lambda *a:None,enable_gaussian_blur=lambda *a:None);gg.audio_mgr=N(ui_sound=lambda *a:None);gg.battle=N(combat=N(view=N(scene_id=315)));gg.battle_result_cache={'battle_type':2}
P=type('Panel',(),{});P.exit_result=h.original('analysis/original-py-640/cocos/panels/combat_result.py','exit_result',env);panel=P();panel.valid=False;panel.result_state=False
cases=json.loads(Path(sys.argv[1]).read_text())
for n in (2,1,0):
 rows=cases['loss'+str(n)];a.combatData.state=4;events.clear();prompts.clear()
 for method,r in rows:
  if method=='setEventBattleStage':a.setEventBattleStage(r['s'],r['n'])
  elif method=='clearEventBattleStage':a.clearEventBattleStage(r['s'])
  elif method=='combatOfflineReward':a.combatOfflineReward(r['t'],r['s'],r['h'],r['x'],r['r'],r['w'])
 assert a.battleStageData.eventBattleStage.get(315,0)==n and a.combatData.state==0 and events[0][0]=='reward' and events[0][1][-1]==0
 panel.exit_result()
 if n:
  assert prompts[-1][0]==175 and prompts[-1][1]['text_args']==(n,);prompts[-1][1]['confirm_cb']();assert sent[-1]==('retry-entry',315);prompts[-1][1]['cancel_cb']();assert sent[-1]==('battleRealFailWithEventMode',{'s':315})
 else:assert not prompts and events[-1]=='city'
print('PASS actual original640 absolute setter before reward/reset; full exit_result retries2/1, no retry0; original cancel callback sends giveup RPC')
# Re-enter the mandatory original story UI after giveup without a fake completion.
source=json.loads((R/'runtime/project7_story_mission_catalog/public-source-v1.json').read_text())
env['EventContentDataMod']=N(data={1342:{'release':True,'priority':5,'dialog':1342,'enterBattle':426,'patrolEvent':1}})
env['MissionDataMod']=N(data={426:source['trial_source']['426']['mission']})
env['helpers']=N(toStrKeyDict=lambda d:{str(k):v for k,v in d.items()})
env['const'].DEBUG_SKIP_EVENT=False;env['const'].EventCompleteCond=N(DICT_COND_SET=set());env['const'].StoryRouteConst=N(ZHOUNIAN2_TRIGGER_EVENTID=-1);env['const'].MissionMode=N(CINE_SET={1,2});env['const'].QIANSHI_SCENE_SET=set()
env['CombatData'].STATE_NONE=0;env['CombatData'].LOST_NONE=0
for method in ('pushEvents','tryNotifyEvent','filterProcessingEvents','isEmergencyEvent','filterEventWithClientLimit','getEventsWithPriority','canStartEvent','startEvent','startEventReply','completeBase','completeCityAttention','completeEventDialog','startSettlement','startCaidanScene','startPuzzleRoom','startEventUI','startMovie','startEventBattle','clientTraceProcessingEvent'):
 setattr(A,method,h.original('analysis/original-py-640/entity/avatar_members/EventTriggerMember.py',method,env))
for method in ('checkEventBattleStage','battleEnterWithEventMode'):setattr(A,method,h.original('analysis/original-py-640/entity/avatar_members/BattleStageMember.py',method,env))
del a.battleEnterWithEventMode
A.combatOfflineRequest=h.original('analysis/original-py-640/entity/avatar_members/CombatMember.py','combatOfflineRequest',env);D.offlineRequest=h.original('analysis/original-py-640/entity/avatar_attrs/CombatData.py','offlineRequest',env)
E=type('EventData',(),{})
for method in ('addProcessingEvent','delProcessingEvent'):setattr(E,method,h.original('analysis/original-py-640/entity/avatar_attrs/EventTriggerData.py',method,env))
a.eventTriggerData=E();ed=a.eventTriggerData;ed.availableEvents={};ed.processingEventsServer={1342};ed.processingEventsClient={1342};ed.gmLockEvents=set();ed.completedEvents=set();ed.selectedEvent=None
a.battleStageData.eventBattleStage[426]=1;a.combatData.reset();a.combatData.fight_id=cases['mandatory_begin']['f'];a.weeknumData=N(weeknum=3);a.queryEventOptAsk=lambda e:events.append(('query-option',e));a.startCheckNewbee=lambda:events.append('newbee-check');a.logger.debug=lambda *args:None
# Rendering, coroutine timing and transport enqueue are finite seams; producers remain original.
def reliable(method,params,callback=None,**kwargs):
 sent.append((method,params))
 if method=='clientTraceProcessingEvent'and callback:callback({})
a.callServerMethodReliable=reliable
gg.battle._started=False;gg.logic.event_valid=True;gg.logic.disable_event=lambda *args:None;gg.logic.enable_event=lambda *args,**kwargs:None;gg.city=N(active=False,touchable=True);gg.dialogue_forcehide=None;gg.ui.lock=lambda *args:None;gg.ui.unlock=lambda *args:None;gg.ui._procing_settlement=False;gg.ui.panels.city=N(is_in_city=lambda:True)
gg.ui.panels.dialogue=N(forcehide=False,trigger_event_dialogue=lambda event,callback:(events.append(('dialog',event)),callback()))
CityPanel=type('CityEventPanel',(),{});CityPanel.notify_events=h.original('analysis/original-py-640/cocos/panels/city_event.py','notify_events',env);gg.ui.panels.city_event=CityPanel()
# Baseline marker blocks another local playback even though server processing remains.
sent.clear();a.pushEvents([], [1342]);assert not sent
game_object=types.ModuleType('com.base.game_object');game_object.members_cache={};game_object.method_cache={};sys.modules[game_object.__name__]=game_object;env['game_object']=game_object
member=types.ModuleType('entity.avatar_members.BattleStageMember');member.Member=A;sys.modules[member.__name__]=member
spec=importlib.util.spec_from_file_location('trial_ui',R/'runtime/project7_trial_retry_compat.py');compat=importlib.util.module_from_spec(spec);spec.loader.exec_module(compat)
policy=(R/'runtime/android_trial_retry/trial-ui-policy-v1.json').read_text();owner=compat.install(member,gg,policy);assert compat.install(member,gg,policy)is owner
# Failed sends do not clear any generation's marker.
def failed(*args):raise IOError('synthetic enqueue rejected')
a.callServerMethod=failed
try:a.battleRealFailWithEventMode(426);raise AssertionError('send failure')
except IOError:pass
assert ed.processingEventsClient=={1342}
a.callServerMethod=lambda method,params:sent.append((method,params));a.battleRealFailWithEventMode(426);assert ed.processingEventsClient==set(),(ed.processingEventsClient,gg.avatar is a,a.combatData.fight_id,a.battleStageData.eventBattleStage,getattr(a,'_q7_trial_rearm_seen',None));assert set(ed.processingEventsServer)=={1342}and ed.completedEvents==set()and sent[-1]==('battleRealFailWithEventMode',{'s':426}),(ed.processingEventsServer,ed.completedEvents,sent[-1])
# Same accepted-fight duplicate cannot clear a newly restored playback marker.
ed.processingEventsClient.add(1342);a.battleRealFailWithEventMode(426);assert ed.processingEventsClient=={1342};ed.processingEventsClient.clear()
assert cases['mandatory_start_allowed']is True
push=cases['mandatory_push'];sent.clear();a.pushEvents(push['a'],push['p']);assert ('startEvent',{'e':1342})in sent
a.startEventReply(1342,1);assert ('dialog',1342)in events and ('combatOfflineRequest',{'t':2,'s':426,'h':[10],'d':{}})in sent and a.combatData.state==4
# A stale Avatar cannot clear the replacement's client marker; no hot-cache patch.
replacement=A();replacement.eventTriggerData=E();replacement.eventTriggerData.processingEventsClient={1342};gg.avatar=replacement
try:a.battleRealFailWithEventMode(426);raise AssertionError('stale avatar')
except RuntimeError:pass
assert replacement.eventTriggerData.processingEventsClient=={1342}
# Both original game_object cache dictionaries reject a materialized Member.
for original_cache in (game_object.members_cache,game_object.method_cache):
 original_cache[A]=[('battleRealFailWithEventMode',owner[2])]
 try:compat.install(member,gg,policy);raise AssertionError('materialized original Member cache')
 except RuntimeError as failure:assert 'Member cache' in str(failure)
 assert A.__dict__['battleRealFailWithEventMode']is owner[3]
 original_cache.clear()
# Actual entity.ClientAvatar exports ClientAvatar, not Avatar. Isolate this guard
# with empty Member caches so the old wrong-name test cannot pass incidentally.
cache=types.ModuleType('entity.ClientAvatar');cache.ClientAvatar=type('ClientAvatar',(),{});sys.modules[cache.__name__]=cache
assert not game_object.members_cache and not game_object.method_cache and not hasattr(cache,'Avatar')
try:compat.install(member,gg,policy);raise AssertionError('late ClientAvatar class install')
except RuntimeError as failure:assert 'Avatar cache' in str(failure)
assert A.__dict__['battleRealFailWithEventMode']is owner[3]
print('PASS early mandatory shim generation/send/duplicate guards; actual pushEvents -> tryNotifyEvent -> city_event -> original dialogue/trace -> original t2 default10 battle producer; no server complete')
