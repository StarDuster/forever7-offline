package com.project7.localmanager;
import java.util.*;
/** Same original Week.apply seam, preserving original result/recovery codec. */
public final class DreamWeekPolicy {
 private static final Set<String> SCOPE_CHANGES=Collections.unmodifiableSet(new HashSet<String>(Arrays.asList(
  "handleIncWeekAsk","handleResetWeekAsk","requestEnterStory","requestEnterStoryByEnding","handleResetWeek")));
 public static boolean isScopeChange(String method){return SCOPE_CHANGES.contains(method);}
 private DreamWeekPolicy(){}
 public static LocalResourceEngine.Result apply(byte[]profile,LocalWeekCatalog catalog,LocalTutorialStore.Progress progress,String method,byte[]params){
  // Executed inside the original Store transaction. A different connection may
  // have committed a receipt after the earlier Gateway recovery checkpoint.
  if(SCOPE_CHANGES.contains(method)&&BsonLite.documentValue(profile,"q7TrialRetryPending")!=null){
   LocalResourceEngine.Result blocked=new LocalResourceEngine.Result(profile);
   blocked.replies.add(new LocalResourceEngine.Reply("showMessageStr",BsonLite.document("m","请先恢复当前试炼结果，再切换周目。")));
   return blocked;
  }
  if(SCOPE_CHANGES.contains(method)){
   byte[] storyPending=BsonLite.documentValue(profile,"q7StoryPending");
   if(storyPending!=null&&!BsonLite.keys(storyPending).isEmpty()){
    LocalResourceEngine.Result blocked=new LocalResourceEngine.Result(profile);
    blocked.replies.add(new LocalResourceEngine.Reply("showMessageStr",BsonLite.document("m","剧情结果尚待投递，请稍后重试。")));
    return blocked;
   }
  }
  String before=id(profile);LocalResourceEngine.Result result=("handleResetWeek".equals(method)?EventResetWeekPolicy.apply(profile,catalog,progress,method,params):LocalWeekEngine.apply(profile,catalog,progress,method,params));String after=id(result.profile);
  if(after!=null&&!after.isEmpty()&&!Objects.equals(before,after)&&(hasDream(profile)||hasDream(result.profile)))result.profile=DreamState.afterWeekTransition(result.profile);
  return result;
 }
 private static boolean hasDream(byte[]profile){
  if(BsonLite.documentValue(profile,DreamState.CONTEXT)!=null||BsonLite.documentValue(profile,"q7DreamPatrolCommit")!=null)return true;
  byte[]std=BsonLite.documentValue(profile,"std"),used=BsonLite.arrayValue(std,"hsu");Integer count=BsonLite.intValue(std,"hst");
  return Boolean.TRUE.equals(BsonLite.boolValue(std,"hsf"))||Boolean.TRUE.equals(BsonLite.boolValue(std,"lhs"))||(count!=null&&count!=0)||(used!=null&&!BsonLite.keys(used).isEmpty());
 }
 private static String id(byte[]profile){return BsonLite.stringValue(BsonLite.documentValue(profile,"q7WeekTransition"),"id");}
}
