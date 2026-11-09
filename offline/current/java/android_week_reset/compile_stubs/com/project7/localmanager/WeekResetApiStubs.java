package com.project7.localmanager;
import android.content.Context;import java.util.*;import java.io.*;
/** COMPILE ONLY exact used original APIs; no constant-value release fields. */
final class LocalTutorialStore {
 LocalTutorialStore(Context c){}LocalTutorialStore(File f){}
 static final class Progress { static Progress fresh(){return null;} final java.util.Set<Integer> completedEvents=null; final java.util.Set<Integer> availableEvents=null; final java.util.Map<String,java.util.Set<Integer>> eventConditions=null; final java.util.Set<Integer> processingEvents=null; String weekCommit; int weekIndex; int patrolActions; final java.util.Map<Integer,Integer> eventCompletions=null; }}
final class LocalWeekCatalog { final java.util.Map<Integer,Integer> entrances=null;LocalWeekCatalog(InputStream in)throws IOException{}}
final class LocalWeekEngine {static LocalResourceEngine.Result apply(byte[]p,LocalWeekCatalog c,LocalTutorialStore.Progress s,String m,byte[]a){return null;}}
final class LocalResourceEngine {
 static final class Result {byte[]profile;final List<Reply>replies=null;Result(byte[]p){}}
 static final class Reply{Reply(String m,byte[]p){}}
}
final class LocalEventCatalog { final java.util.Map<Integer,Object> consumptions=null;
 final java.util.Map<Integer,byte[]> cityEffects=null;
 final java.util.Map<Integer,String> routes=null;
 LocalEventCatalog(Context c)throws IOException{}Event get(int e){return null;} java.util.Set<Integer> mutex(int e){return null;}
 static final class Event {
  final boolean release;
  final boolean autoTrigger;
  final java.util.List<Integer> successors;
  Event(int id,boolean a,boolean b,boolean c,boolean d,boolean e,boolean f,boolean g,boolean h,int i,int j,int k,List<Integer>l,Map<String,Set<Integer>>m){throw new UnsupportedOperationException();}
 }
}
final class BsonLite {
 private BsonLite(){}
 static byte[]document(Object...v){return null;}static byte[]documentValue(byte[]p,String k){return null;}static byte[]withProfileDocument(byte[]p,String k,byte[]v){return null;}static List<String>keys(byte[]p){return null;}static String stringValue(byte[]p,String k){return null;}static Integer intValue(byte[]p,String k){return null;}static Number numericValue(byte[]p,String k){return null;}
}
final class LocalGatewayServer implements Runnable,AutoCloseable {
 interface ProfileProvider{}interface StatusListener{void onStatus(boolean active,String detail);}
 LocalGatewayServer(int port,LocalAccountStore accounts,ProfileProvider profiles,LocalTutorialStore tutorials,LocalEventCatalog events,LocalNewbeeCatalog newbees,LocalCombatCatalog combat,LocalPatrolCatalog patrol,StatusListener listener){}
 public void run(){}public void close(){}
}
final class LocalEventEngine {
 LocalEventEngine(LocalEventCatalog c,LocalNewbeeCatalog n,LocalTutorialStore.Progress p,int event){}
 LocalEventEngine(LocalEventCatalog c,LocalNewbeeCatalog n,LocalTutorialStore.Progress p,int event,byte[]profile){}
 LocalEventEngine(LocalEventCatalog c,LocalNewbeeCatalog n,LocalTutorialStore.Progress p,int event,byte[]profile,boolean memoize){}
}
final class LocalAccountStore{LocalAccountStore(Context c)throws IOException{}}
final class LocalNewbeeCatalog{LocalNewbeeCatalog(Context c)throws IOException{}}
final class LocalCombatCatalog{LocalCombatCatalog(Context c)throws IOException{}}
final class LocalPatrolCatalog{LocalPatrolCatalog(Context c)throws IOException{}}
final class DreamCoordinator{private DreamCoordinator(){}public static void recover(LocalGatewayServer g,String a,LocalTutorialStore.Progress p,LocalEventEngine e)throws IOException{}}
final class TrialRetryGateway{public static void beforeScopeChange(LocalGatewayServer g,String a,LocalTutorialStore.Progress p,LocalEventEngine e)throws IOException{}}
