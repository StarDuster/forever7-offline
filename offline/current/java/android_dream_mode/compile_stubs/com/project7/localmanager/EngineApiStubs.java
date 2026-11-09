package com.project7.localmanager;
import java.util.*;
/** Compile only exact original package APIs, never packaged. */
final class LocalEventEngine {
 LocalEventEngine(LocalEventCatalog c,LocalNewbeeCatalog n,LocalTutorialStore.Progress p,int start){}
 LocalEventEngine(LocalEventCatalog c,LocalNewbeeCatalog n,LocalTutorialStore.Progress p,int start,byte[]profile){}
 LocalEventEngine(LocalEventCatalog c,LocalNewbeeCatalog n,LocalTutorialStore.Progress p,int start,byte[]profile,boolean memo){}
 List<Integer>patrolEvents(int area,Collection<Integer>heroes,LocalPatrolCatalog catalog){return null;}
 void refreshProfile(byte[] profile){}
 List<Integer>trace(String kind,Collection<Integer>scenes){return null;}}
final class LocalPatrolCatalog {}

final class LocalGatewayServer {}
final class LocalTutorialStore {static final class Progress {String weekCommit;}}
final class LocalPatrolEngine {static Result begin(LocalPatrolCatalog c,LocalTutorialStore.Progress p,LocalEventEngine e,byte[]b,int a,List<Integer>h){return null;}static Map<Integer,Integer>claim(LocalTutorialStore.Progress p,byte[]b){return null;}static final class Result {Result(boolean ok,List<Integer>events,String reason){}}}

final class LocalEconomyCatalog {LocalEconomyCatalog(java.io.InputStream input)throws java.io.IOException {}}
final class LocalResourceCatalog {}
final class LocalResourceEngine {static final class Reply {final String method=null;final byte[]parameters=null;Reply(String s,byte[]b){}}static final class Result {byte[]profile;final List<Reply>replies=new ArrayList<>();Result(byte[]p){}}}
final class LocalEconomyEngine {static Result apply(byte[]p,LocalEconomyCatalog c,LocalResourceCatalog r,LocalTutorialStore.Progress x,String m,byte[]a){return null;}static String nextDayBlocker(byte[]p,LocalTutorialStore.Progress x){return null;}static final class Result {boolean accepted;String reason;byte[]profile;final List<LocalResourceEngine.Reply>replies=new ArrayList<>();Result(byte[]p){}}}

final class LocalServiceEngine {static void syncRoute(LocalResourceEngine.Result r){}}

final class LocalEventCatalog {}
final class LocalNewbeeCatalog {}

final class LocalWeekCatalog {LocalWeekCatalog(java.io.InputStream input)throws java.io.IOException {}}
final class LocalWeekEngine {static LocalResourceEngine.Result apply(byte[]p,LocalWeekCatalog c,LocalTutorialStore.Progress x,String m,byte[]a){return null;}}

final class EventResetWeekPolicy {private EventResetWeekPolicy(){}public static LocalResourceEngine.Result apply(byte[]p,LocalWeekCatalog c,LocalTutorialStore.Progress s,String m,byte[]a){return null;}}
