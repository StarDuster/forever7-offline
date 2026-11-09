package com.project7.localmanager;
import java.io.*;import java.util.*;
/** Same six-argument original apply seam. Original Store owns lock, atomic write,
 * recovery/reconcile and publication. No separate early dream-exit commit. */
public final class DreamEconomyPolicy {
 private static final Map<LocalEconomyEngine.Result,Boolean>CALENDAR=Collections.synchronizedMap(new WeakHashMap<LocalEconomyEngine.Result,Boolean>());
 private DreamEconomyPolicy(){}
 public static LocalEconomyEngine.Result apply(byte[]profile,LocalEconomyCatalog economy,LocalResourceCatalog resources,LocalTutorialStore.Progress progress,String method,byte[]params){
  if(!"incDayWhenNoActionVal".equals(method)||!Boolean.TRUE.equals(BsonLite.boolValue(BsonLite.documentValue(profile,"std"),"hsf")))return LocalEconomyEngine.apply(profile,economy,resources,progress,method,params);
  try{
   DreamState.Scope scope=DreamCoordinator.scope(profile,progress);
   if(BsonLite.documentValue(profile,"q7DreamPatrolCommit")!=null)return denied(profile,"当前请求尚未恢复，请重新连接后重试。");
   String busy=LocalEconomyEngine.nextDayBlocker(profile,progress);if(busy!=null)return denied(profile,busy);
   DreamState.Change night=DreamState.nightGuard(profile,DreamCoordinator.preparedCatalog(),scope,DreamPatrolDelta.set(progress,"completedEvents"),DreamPatrolDelta.set(progress,"processingEvents"));
   if(night.reason!=DreamState.Reason.NIGHT_READY)return denied(profile,"请先完成本次梦境的晚安剧情。");
   LocalEconomyEngine.Result result=LocalEconomyEngine.apply(profile,economy,resources,progress,method,params);
   if(result.accepted){byte[]oldWeek=BsonLite.documentValue(profile,"weeknum"),newWeek=BsonLite.documentValue(result.profile,"weeknum");if(!Objects.equals(BsonLite.intValue(oldWeek,"w"),BsonLite.intValue(newWeek,"w"))||!Objects.equals(BsonLite.intValue(oldWeek,"d"),BsonLite.intValue(newWeek,"d"))){DreamState.Change reset=DreamState.afterCalendarCommit(result.profile,DreamCoordinator.scope(result.profile,progress));if(reset.reason==DreamState.Reason.INVALID_STATE)throw new IOException("Dream calendar context invalid");result.profile=reset.profile;
    result.replies.removeIf(reply->reply.method.equals("syncRoute")||reply.method.equals("syncHuiSuData"));
    LocalResourceEngine.Result projection=new LocalResourceEngine.Result(result.profile);LocalServiceEngine.syncRoute(projection);result.replies.addAll(projection.replies);result.replies.add(new LocalResourceEngine.Reply("syncHuiSuData",BsonLite.document("d",DreamState.huiSuProjection(result.profile))));CALENDAR.put(result,Boolean.TRUE);}}
   return result;
  }catch(IOException|IllegalArgumentException invalid){return denied(profile,"当前梦境状态需要重新连接后恢复。");}
 }
 /** Only after original profile commit. Ordinary result has original refresh
  * semantics; a true dream date change consumes op4 BEFORE reevaluation. */
 public static void refreshCalendarEngine(LocalEventEngine engine,byte[]loadedProfile,LocalEconomyEngine.Result result)throws IOException{
  if(CALENDAR.remove(result)!=null)DreamAccess.call(engine,"resetWeekContext",new Class<?>[]{byte[].class},loadedProfile);
  else DreamAccess.call(engine,"refreshProfile",new Class<?>[]{byte[].class},loadedProfile);
 }
 private static LocalEconomyEngine.Result denied(byte[]profile,String reason){LocalEconomyEngine.Result r=new LocalEconomyEngine.Result(profile);r.accepted=false;r.reason=reason;r.replies.add(new LocalResourceEngine.Reply("showMessageStr",BsonLite.document("m",reason)));Integer d=BsonLite.intValue(BsonLite.documentValue(profile,"weeknum"),"d");r.replies.add(new LocalResourceEngine.Reply("updateDay",BsonLite.document("d",d==null?0:d)));return r;}
}
