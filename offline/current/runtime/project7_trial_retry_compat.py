# -*- coding: ascii -*-
"""Early source-bound mandatory-trial playback-marker rearm, no server mutation."""
import sys,json,hashlib
_TARGET='entity.avatar_members.BattleStageMember'
_SHA='f198e19879e2b819dad3e6a545476e64fbf7ef6664df629264e1ec781cda766c'
_MARKER='_q7_mandatory_trial_rearm_owner'
def _globals(fn):return getattr(fn,'func_globals',getattr(fn,'__globals__',{}))
def install(member_module,gg,policy_text):
 policy=json.loads(policy_text)
 canonical=json.dumps(policy,sort_keys=True,ensure_ascii=True,separators=(',',':')).encode('ascii')
 if hashlib.sha256(canonical).hexdigest()!=_SHA:raise ValueError('Trial rearm UI source changed')
 if sys.modules.get(_TARGET) is not member_module:raise RuntimeError('Trial rearm Member generation changed')
 avatar_module=sys.modules.get('entity.ClientAvatar')
 if avatar_module is not None and getattr(avatar_module,'ClientAvatar',None) is not None:raise RuntimeError('Trial rearm must install before Avatar cache materializes')
 member=member_module.Member
 game_object=sys.modules.get('com.base.game_object')
 if game_object is None:raise RuntimeError('Trial rearm game_object generation unavailable')
 members_cache=getattr(game_object,'members_cache',None);method_cache=getattr(game_object,'method_cache',None)
 if not isinstance(members_cache,dict) or not isinstance(method_cache,dict):raise RuntimeError('Trial rearm cache schema changed')
 if member in members_cache or member in method_cache:raise RuntimeError('Trial rearm must install before Member cache materializes')
 prior=member.__dict__.get(_MARKER)
 if prior is not None:
  if prior[0] is not gg or prior[1]!=policy or member.__dict__.get('battleRealFailWithEventMode') is not prior[3]:raise RuntimeError('Trial rearm UI reinstall changed')
  return prior
 original=member.__dict__.get('battleRealFailWithEventMode')
 if not callable(original) or _globals(original).get('gg') is not gg or _globals(original).get('game_object') is not game_object:raise RuntimeError('Trial rearm original producer binding changed')
 def giveup(self,scene):
  owner=policy['mandatory'].get(str(scene))
  if owner is None:return original(self,scene)
  if (getattr(gg,'avatar',None) is not self or sys.modules.get(_TARGET) is not member_module or member_module.Member is not member or sys.modules.get('com.base.game_object') is not game_object or game_object.members_cache is not members_cache or game_object.method_cache is not method_cache):raise RuntimeError('Stale trial Avatar/Member generation')
  data=self.eventTriggerData;battle=self.battleStageData;fight=getattr(self.combatData,'fight_id',None)
  seen=getattr(self,'_q7_trial_rearm_seen',{})
  token=(fight,data,battle)
  eligible=(bool(fight) and seen.get(scene)!=token) and (owner in data.processingEventsServer and owner in data.processingEventsClient and battle.eventBattleStage.get(scene,0)>0)
  result=original(self,scene) # Failed enqueue leaves playback marker untouched.
  if (eligible and getattr(gg,'avatar',None) is self and self.eventTriggerData is data and self.battleStageData is battle and
      owner in data.processingEventsServer and owner in data.processingEventsClient and battle.eventBattleStage.get(scene,0)>0):
   data.delProcessingEvent(owner)
   seen=dict(seen);seen[scene]=token;self._q7_trial_rearm_seen=seen
  return result
 setattr(member,'battleRealFailWithEventMode',giveup)
 state=(gg,policy,original,giveup);setattr(member,_MARKER,state);return state
