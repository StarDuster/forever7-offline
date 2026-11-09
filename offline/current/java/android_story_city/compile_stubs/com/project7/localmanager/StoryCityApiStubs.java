package com.project7.localmanager;
import java.io.*;
import java.util.*;
/** Compile-only descriptors; no implementation is packaged or used by host runtime. */
final class BsonLite {
 static final byte[] EMPTY_DOCUMENT=null;
 static byte[]document(Object...v){throw new UnsupportedOperationException();}
 static byte[]documentValue(byte[]b,String k){throw new UnsupportedOperationException();}
 static byte[]arrayValue(byte[]b,String k){throw new UnsupportedOperationException();}
 static String stringValue(byte[]b,String k){throw new UnsupportedOperationException();}
 static Integer intValue(byte[]b,String k){throw new UnsupportedOperationException();}
 static Boolean boolValue(byte[]b,String k){throw new UnsupportedOperationException();}
 static Number numericValue(byte[]b,String k){throw new UnsupportedOperationException();}
 static List<String>keys(byte[]b){throw new UnsupportedOperationException();}
 static List<Integer>intArrayValues(byte[]b,String k){throw new UnsupportedOperationException();}
 static byte[]withProfileDocument(byte[]b,String k,byte[]v){throw new UnsupportedOperationException();}
 static byte[]withProfileInt(byte[]b,String k,int v){throw new UnsupportedOperationException();}
 static byte[]withProfileBool(byte[]b,String k,boolean v){throw new UnsupportedOperationException();}
 static byte[]withProfileArray(byte[]b,String k,List<?>v){throw new UnsupportedOperationException();}
 static byte[]withoutProfileKey(byte[]b,String k){throw new UnsupportedOperationException();}
 static byte[]q7OriginalAllAreaInfoReplyDocument(boolean b,LocalTutorialStore.Progress p,byte[]v){throw new UnsupportedOperationException();}
 static byte[]withLocalCityState(byte[] b,LocalTutorialStore.Progress p){throw new UnsupportedOperationException();}
 static byte[]allAreaInfoReplyDocument(boolean b,LocalTutorialStore.Progress p,byte[] v){throw new UnsupportedOperationException();}
}
final class LocalTutorialStore {
 LocalTutorialStore(android.content.Context c){throw new UnsupportedOperationException();}
 static final class Progress {
  static Progress fresh(){throw new UnsupportedOperationException();}
  final Set<Integer>completedEvents=null; final Set<Integer>availableEvents=null;
  final Map<String,Set<Integer>>eventConditions=null;
  final Set<Integer>processingEvents=null;
  String weekCommit;int weekIndex;int patrolActions; final Map<Integer,Integer> eventCompletions=null;
 }
}
final class LocalResourceEngine {static final class Result {byte[]profile; java.util.List<Reply> replies=null; void add(String m,byte[]p){throw new UnsupportedOperationException();}} static final class Reply {String method;byte[] parameters;}}

final class LocalGatewayServer {}
final class LocalAlanCityEngine { static boolean active(byte[] p,LocalTutorialStore.Progress g){return false;} static int state(byte[] p,LocalTutorialStore.Progress g,int a){return 0;} }
final class LocalPatrolEngine { static final class Result {} }

final class LocalWeekCatalog { final Map<Integer,Integer> entrances=null; LocalWeekCatalog(java.io.InputStream in)throws java.io.IOException{} }
final class LocalWeekEngine { static LocalResourceEngine.Result apply(byte[] p,LocalWeekCatalog c,LocalTutorialStore.Progress g,String m,byte[] a){return null;} static boolean canEnter(byte[] p,LocalWeekCatalog c,int m){return false;} }
final class LocalStoryItemRewardEngine {static int completedDay(byte[] p,LocalTutorialStore.Progress g,int e){return 0;}}
final class LocalEventCatalog {static final class Event{final boolean autoTrigger=false;final boolean release=false;final java.util.List<Integer> successors=null;} final Map<Integer,byte[]>cityEffects=null;final Map<Integer,int[]>consumptions=null;final Map<Integer,String>routes=null; Event get(int id){return null;} LocalEventCatalog(java.io.InputStream in)throws java.io.IOException{} LocalEventCatalog(android.content.Context c)throws java.io.IOException{}}
final class LocalNewbeeCatalog {LocalNewbeeCatalog(InputStream s){throw new UnsupportedOperationException();}}
final class LocalEventEngine {
 LocalEventEngine(LocalEventCatalog a,LocalNewbeeCatalog b,LocalTutorialStore.Progress c,int d,byte[]e,boolean f){throw new UnsupportedOperationException();}
 void refreshProfile(byte[]p){throw new UnsupportedOperationException();}
 List<Integer>trace(String kind,Collection<Integer>scenes){throw new UnsupportedOperationException();}
}
final class LocalProfileStore {
 LocalProfileStore(android.content.Context c){throw new UnsupportedOperationException();}
 LocalEconomyEngine.Result updateEconomy(String account,String method,byte[]request,LocalTutorialStore.Progress progress){throw new UnsupportedOperationException();}
}
final class LocalEconomyEngine {
 static final class Result {boolean accepted,replay;int win;byte[]reward,profile;}
 static int actions(byte[]profile,LocalTutorialStore.Progress progress){throw new UnsupportedOperationException();}
}
final class LocalChapterCityEngine {static void refresh(LocalResourceEngine.Result r,LocalEventCatalog c,LocalTutorialStore.Progress p){throw new UnsupportedOperationException();} static void applyHeroes(LocalResourceEngine.Result r,byte[]e){throw new UnsupportedOperationException();}}
final class StoryMenuShared {static void prepare(android.content.Context c)throws java.io.IOException{throw new UnsupportedOperationException();}}
final class LocalStoryEntryPolicy {static boolean q7OriginalSupports(int i){throw new UnsupportedOperationException();}}
 final class StoryMissionBridge {
 static void prepare(android.content.Context c)throws java.io.IOException{throw new UnsupportedOperationException();}
 static void prepareSpecial(android.content.Context c)throws java.io.IOException{throw new UnsupportedOperationException();}
 static void offerMissionOutcomes(LocalTutorialStore.Progress p,byte[] b,LocalEventCatalog e){throw new UnsupportedOperationException();}
 static boolean chapterReady(int a,String r){throw new UnsupportedOperationException();}
 static String specialToken(){throw new UnsupportedOperationException();}
 public static int area(int i){throw new UnsupportedOperationException();}
 public static int status(LocalTutorialStore.Progress p,int a,byte[]b){throw new UnsupportedOperationException();}
 public static byte[]mapStages(LocalTutorialStore.Progress p,int a,byte[]b){throw new UnsupportedOperationException();}
 public static byte[]stages(LocalTutorialStore.Progress p,int a,byte[]b){throw new UnsupportedOperationException();}
 public static boolean consumeVictory(LocalTutorialStore.Progress p,byte[]b,int t,int s){throw new UnsupportedOperationException();}
 public static boolean partyAllowed(byte[]b){throw new UnsupportedOperationException();}
}
final class LocalAnCityEngine { static final java.util.Set<Integer> LOCK_EVENTS=null; static boolean active(byte[]p){return false;} static boolean locked(byte[]p,int area){return false;} static void refresh(LocalResourceEngine.Result r,LocalEventCatalog e,LocalTutorialStore.Progress p){} }
