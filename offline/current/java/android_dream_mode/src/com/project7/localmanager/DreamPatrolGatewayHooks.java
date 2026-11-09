package com.project7.localmanager;
import java.io.IOException;import java.util.*;
/** Parameter-preserving replacements for the original call + save spans only.
 * Root retains its cache guard, validation, replies and original effect tail. */
public final class DreamPatrolGatewayHooks {
 private DreamPatrolGatewayHooks(){}
 public static LocalPatrolEngine.Result begin(LocalPatrolCatalog catalog,LocalTutorialStore.Progress progress,LocalEventEngine engine,byte[]profile,int area,List<Integer>heroes,LocalGatewayServer gateway,String account)throws IOException{
  if(dream(profile))try{return DreamPatrolFailure.checked(gateway,account,progress,engine,()->DreamCoordinator.begin(gateway,account,progress,engine,area,heroes));}
  catch(DreamPatrolFailure.NotCommitted definite){return new LocalPatrolEngine.Result(false,Collections.<Integer>emptyList(),"本次巡查未提交，请稍后重试。");}
  LocalPatrolEngine.Result result=LocalPatrolEngine.begin(catalog,progress,engine,profile,area,heroes);
  save(gateway,account,progress);return result;
 }
 public static Map<Integer,Integer>claim(LocalTutorialStore.Progress progress,byte[]profile,LocalGatewayServer gateway,String account,LocalEventEngine engine)throws IOException{
  if(dream(profile))try{return DreamPatrolFailure.checked(gateway,account,progress,engine,()->DreamCoordinator.claim(gateway,account,progress,engine));}
  catch(DreamPatrolFailure.NotCommitted definite){return null;} // dedicated negative branch; never emptyMap success
  Map<Integer,Integer>gains=LocalPatrolEngine.claim(progress,profile);save(gateway,account,progress);return gains;
 }
 private static boolean dream(byte[]profile){return Boolean.TRUE.equals(BsonLite.boolValue(BsonLite.documentValue(profile,"std"),"hsf"));}
 private static void save(LocalGatewayServer gateway,String account,LocalTutorialStore.Progress progress)throws IOException{
  DreamAccess.call(DreamAccess.get(gateway,"tutorialStore"),"save",new Class<?>[]{String.class,progress.getClass()},account,progress);
 }
}
