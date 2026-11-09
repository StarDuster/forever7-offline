package com.project7.localmanager;
import android.content.Context;import java.io.*;import java.util.*;
/** Same-owner profile-first patrol transaction. Caller must invoke recover before
 * every mutation and after the original per-connection result-cache guard.
 * No frames, reliable ACK, event completion, currency or ordinary action debit. */
public final class DreamCoordinator {
 private static volatile DreamCatalog catalog;
 private static final String PENDING="q7DreamPatrolCommit",MARK="q7DreamPatrolApplied:";
 private DreamCoordinator(){}
 public static void prepare(Context context)throws IOException{catalog=DreamCatalog.prepare(context);}
 static DreamCatalog preparedCatalog()throws IOException{return catalog();}
 private static DreamCatalog catalog()throws IOException{DreamCatalog c=catalog;if(c==null)throw new IOException("Dream catalog not prepared");return c;}
 static void installForHost(DreamCatalog c){catalog=c;}
 public static void recover(final LocalGatewayServer gateway,final String account,final LocalTutorialStore.Progress progress,final LocalEventEngine engine)throws IOException{
  synchronized(engine){DreamStorage.locked(gateway,account,tx->{recoverLocked(gateway,account,progress,engine,tx);return null;});}
 }
 private static void recoverLocked(LocalGatewayServer gateway,String account,Object live,LocalEventEngine engine,DreamStorage tx)throws IOException{
  byte[]profile=tx.read(),receipt=BsonLite.documentValue(profile,PENDING);if(receipt==null)return;
  String id=BsonLite.stringValue(receipt,"id");if(id==null||!id.matches("[A-Za-z0-9-]{1,128}")||!Integer.valueOf(1).equals(BsonLite.intValue(receipt,"v"))||!DreamCatalog.SHA256.equals(BsonLite.stringValue(receipt,"catalog")))throw new IOException("Invalid dream recovery receipt");
  DreamState.Scope scope=scope(profile,live);if(!scope.weekCommit.equals(BsonLite.stringValue(receipt,"wc"))||scope.week!=integer(receipt,"w")||scope.day!=integer(receipt,"d")||!scope.route.equals(BsonLite.stringValue(receipt,"rt")))throw new IOException("Dream recovery scope changed; repair required");
  Object candidate=DreamAccess.cloneProgress(live);Map<String,Set<Integer>>conditions=conditions(candidate);
  if(!conditions.containsKey(MARK+id)){byte[]delta=BsonLite.documentValue(receipt,"delta");if(delta==null)throw new IOException("Missing dream owned delta");if("entry".equals(BsonLite.stringValue(receipt,"kind")))DreamProgressDelta.apply(candidate,delta);else DreamPatrolDelta.apply(candidate,delta);conditions.keySet().removeIf(k->k.startsWith(MARK));conditions.put(MARK+id,new LinkedHashSet<>(Collections.singleton(1)));}
  save(gateway,account,candidate); // must be durable before clearing profile receipt
  byte[]ack=BsonLite.withoutProfileKey(profile,PENDING);tx.commit(profile,ack);
  DreamAccess.adopt(candidate,live,engine,ack);if("entry".equals(BsonLite.stringValue(receipt,"kind")))DreamAccess.set(engine,"clientOperation",0); // consumed actual rest intent
 }
 private static void save(LocalGatewayServer gateway,String account,Object candidate)throws IOException{
  Object store=DreamAccess.get(gateway,"tutorialStore");try{DreamAccess.call(store,"save",new Class<?>[]{String.class,candidate.getClass()},account,candidate);}catch(IOException failure){
   Object loaded;try{loaded=DreamAccess.call(store,"load",new Class<?>[]{String.class},account);}catch(IOException unknown){failure.addSuppressed(unknown);throw failure;}
   if(!DreamAccess.call(candidate,"toProperties",new Class<?>[0]).equals(DreamAccess.call(loaded,"toProperties",new Class<?>[0])))throw failure;
  }
 }
 public static LocalPatrolEngine.Result begin(final LocalGatewayServer gateway,final String account,final LocalTutorialStore.Progress progress,final LocalEventEngine engine,final int area,final List<Integer>heroes)throws IOException{
  synchronized(engine){return DreamStorage.locked(gateway,account,tx->{
   recoverLocked(gateway,account,progress,engine,tx);byte[]profile=tx.read();DreamCatalog c=catalog();
   if(!Boolean.TRUE.equals(BsonLite.boolValue(BsonLite.documentValue(profile,"std"),"hsf")))return ordinaryBegin(gateway,account,progress,engine,profile,area,heroes);
   if(heroes==null)return result(false,Collections.emptyList(),"heroes");
   DreamState.Scope scope=scope(profile,progress);DreamState.Change gate=DreamState.canPatrol(profile,c,scope);
   if(Boolean.TRUE.equals(DreamAccess.get(progress,"patrolRewardPending"))){if(canResume(progress,profile,area,heroes))return result(true,new ArrayList<>(DreamPatrolDelta.set(progress,"patrolEvents")),null);return result(false,Collections.emptyList(),"pending");}
   if(gate.reason!=DreamState.Reason.PATROL_ALLOWED)return result(false,Collections.emptyList(),"dream_budget");
   if(heroes==null||heroes.size()>3||new HashSet<>(heroes).size()!=heroes.size())return result(false,Collections.emptyList(),"heroes");
   Object patrol=DreamAccess.get(gateway,"patrolCatalog"),cost=DreamAccess.call(patrol,"cost",new Class<?>[]{int.class,int.class},area,1);
   if(cost==null||(Integer)DreamAccess.stat(DreamAccess.type("LocalCityProgress"),"status",new Class<?>[]{progress.getClass(),int.class,byte[].class},progress,area,profile)!=0||(Boolean)DreamAccess.stat(DreamAccess.type("LocalChapterCityEngine"),"locked",new Class<?>[]{byte[].class,int.class},profile,area)||Boolean.TRUE.equals(DreamAccess.get(progress,"inEmergency")))return result(false,Collections.emptyList(),"area");
   // Nonempty dream teams must own every hero. Actual source trigger evaluator
   // still handles exclusions/insight/conditions; empty team is offline policy.
   for(Integer hero:heroes)if(hero==null||BsonLite.keys(BsonLite.profileHeroDocument(profile,hero)).isEmpty())return result(false,Collections.emptyList(),"heroes");
   Object candidate=DreamAccess.cloneProgress(progress);LocalEventEngine fork=DreamAccess.fork(engine,candidate,profile);
   DreamAccess.stat(DreamAccess.type("LocalPatrolEngine"),"alignDay",new Class<?>[]{byte[].class,progress.getClass()},profile,candidate);
   List<Integer>selected=DreamPatrolCandidates.eligible(fork,(LocalPatrolCatalog)patrol,c,area,heroes);
   DreamAccess.call(fork,"queuePatrolReplays",new Class<?>[]{Collection.class},selected);
   DreamPatrolDelta.set(candidate,"availableEvents").removeAll(DreamPatrolDelta.set(candidate,"patrolEvents"));replace(candidate,"patrolEvents",selected);DreamPatrolDelta.set(candidate,"availableEvents").addAll(selected);replace(candidate,"patrolHeroes",heroes);
   DreamAccess.set(candidate,"patrolFavor",DreamAccess.get(cost,"favor"));Map<Integer,Integer>bonus=DreamPatrolDelta.map(candidate,"patrolFavorBonus");bonus.clear();
   for(Integer hero:heroes){int gender=(Integer)DreamAccess.call(patrol,"gender",new Class<?>[]{int.class},hero);int value=gender==1||gender==2?(Integer)DreamAccess.stat(DreamAccess.type("LocalPatrolEngine"),"buildingCount",new Class<?>[]{byte[].class,int.class,int.class},profile,area,gender==1?23:24):0;bonus.put(hero,value);}
   DreamAccess.set(candidate,"patrolRewardPending",true);DreamAccess.set(candidate,"patrolArea",area);
   String id=UUID.randomUUID().toString();DreamState.Change accepted=DreamState.recordAcceptedPatrol(profile,c,scope,id);if(!accepted.changed)throw new IOException("Dream acceptance changed during transaction");
   commit(gateway,account,progress,engine,tx,profile,accepted.profile,candidate,scope,id,"begin");return result(true,selected,null);
  });}
 }
 @SuppressWarnings("unchecked")public static Map<Integer,Integer>claim(final LocalGatewayServer gateway,final String account,final LocalTutorialStore.Progress progress,final LocalEventEngine engine)throws IOException{
  synchronized(engine){return DreamStorage.locked(gateway,account,tx->{recoverLocked(gateway,account,progress,engine,tx);byte[]profile=tx.read();Object candidate=DreamAccess.cloneProgress(progress);
   Map<Integer,Integer>gains=(Map<Integer,Integer>)DreamAccess.stat(DreamAccess.type("LocalPatrolEngine"),"claim",new Class<?>[]{progress.getClass(),byte[].class},candidate,profile);
   if(!Boolean.TRUE.equals(BsonLite.boolValue(BsonLite.documentValue(profile,"std"),"hsf"))){save(gateway,account,candidate);DreamAccess.adopt(candidate,progress,engine,profile);return gains;}
   byte[]next=profile;for(Integer hero:gains.keySet()){byte[]row=BsonLite.profileHeroDocument(next,hero);if(row==null||BsonLite.keys(row).isEmpty())throw new IOException("Claim hero disappeared");next=BsonLite.withHeroDocument(next,hero,BsonLite.withProfileInt(row,"ef",DreamPatrolDelta.map(candidate,"patrolFriendly").get(hero)));}
   commit(gateway,account,progress,engine,tx,profile,next,candidate,scope(profile,progress),UUID.randomUUID().toString(),"claim");return gains;
  });}
 }
 /** Fixed named producer is a real rest intent. No public arbitrary op bridge. */
 public static DreamState.Reason enterRequest(final LocalGatewayServer g,final String account,final LocalTutorialStore.Progress p,final LocalEventEngine e,final String method)throws IOException{
  if(!"requestStoryhuisu".equals(method))return DreamState.Reason.INVALID_STATE;
  synchronized(e){return DreamStorage.locked(g,account,tx->{
   recoverLocked(g,account,p,e,tx);byte[]before=tx.read();DreamState.Scope scope=scope(before,p);DreamState.Change change=DreamState.enterAuthorized(before,catalog(),scope);
   if(!change.changed)return change.reason;
   if((Integer)DreamAccess.stat(DreamAccess.type("LocalEconomyEngine"),"actions",new Class<?>[]{byte[].class,p.getClass()},before,p)!=0)return DreamState.Reason.INVALID_STATE;
   if(!DreamPatrolDelta.set(p,"processingEvents").isEmpty()||!DreamPatrolDelta.set(p,"processingNewbees").isEmpty()||Boolean.TRUE.equals(DreamAccess.get(p,"patrolRewardPending")))return DreamState.Reason.INVALID_STATE;
   DreamCatalog.Plan plan=catalog().lookup(scope.route,scope.day);DreamCatalog.Rule rule=catalog().rule(plan.event);
   if(rule==null||!rule.hasCondition||!rule.contentRelease||!rule.conditionRelease)return DreamState.Reason.NO_PLAN;
   Object candidate=DreamAccess.cloneProgress(p);LocalEventEngine fork=DreamAccess.fork(e,candidate,change.profile);
   Object graph=DreamAccess.get(fork,"catalog"),event=DreamAccess.call(graph,"get",new Class<?>[]{int.class},plan.event),trigger=DreamAccess.call(graph,"trigger",new Class<?>[]{int.class},plan.event);
   if(event==null||trigger==null||!Boolean.TRUE.equals(DreamAccess.get(event,"release")))return DreamState.Reason.NO_PLAN;
   DreamAccess.call(fork,"updateClientOperation",new Class<?>[]{int.class},4);
   if(!(Boolean)DreamAccess.call(fork,"triggerMatches",new Class<?>[]{trigger.getClass()},trigger)||(Boolean)DreamAccess.call(fork,"isMutex",new Class<?>[]{int.class},plan.event))return DreamState.Reason.INVALID_STATE;
   if(!(Boolean)DreamAccess.call(fork,"startEvent",new Class<?>[]{int.class},plan.event)||!DreamPatrolDelta.set(candidate,"processingEvents").contains(plan.event))return DreamState.Reason.INVALID_STATE;
   DreamAccess.call(fork,"updateClientOperation",new Class<?>[]{int.class},0);
   String id=UUID.randomUUID().toString();byte[]receipt=BsonLite.document("v",1,"id",id,"kind","entry","catalog",DreamCatalog.SHA256,"wc",scope.weekCommit,"w",scope.week,"d",scope.day,"rt",scope.route,"delta",DreamProgressDelta.capture(p,candidate));
   tx.commit(before,BsonLite.withProfileDocument(change.profile,PENDING,receipt));recoverLocked(g,account,p,e,tx);return DreamState.Reason.ENTERED;
  });}
 }
 /** Compatibility entry name; still uses the fixed actual request binding. */
 public static DreamState.Reason enterAuthorized(LocalGatewayServer g,String account,LocalTutorialStore.Progress p,LocalEventEngine e)throws IOException{return enterRequest(g,account,p,e,"requestStoryhuisu");}
 /** Replaces only the two original pending guards; no fake flashback flag. */
 public static boolean hasPendingChoice(LocalTutorialStore.Progress progress,byte[]profile)throws IOException{
  if(activePending(progress,profile)){
   if(Boolean.TRUE.equals(DreamAccess.get(progress,"inEmergency")))return false;
   for(Integer id:DreamPatrolDelta.set(progress,"processingEvents"))if((Boolean)DreamAccess.stat(DreamAccess.type("LocalPatrolEngine"),"lambda$hasPendingChoice$0",new Class<?>[]{Integer.class},id))return false;
   byte[]battle=BsonLite.documentValue(profile,"q7Battle");return battle==null||BsonLite.keys(battle).isEmpty();
  }
  return(Boolean)DreamAccess.stat(DreamAccess.type("LocalPatrolEngine"),"hasPendingChoice",new Class<?>[]{progress.getClass(),byte[].class},progress,profile);
 }
 public static boolean canResume(LocalTutorialStore.Progress progress,byte[]profile,int area,List<Integer>heroes)throws IOException{
  if(activePending(progress,profile))return heroes!=null&&heroes.size()==DreamPatrolDelta.set(progress,"patrolHeroes").size()&&area==(Integer)DreamAccess.get(progress,"patrolArea")&&new LinkedHashSet<>(heroes).equals(DreamPatrolDelta.set(progress,"patrolHeroes"));
  return(Boolean)DreamAccess.stat(DreamAccess.type("LocalPatrolEngine"),"canResume",new Class<?>[]{progress.getClass(),byte[].class,int.class,List.class},progress,profile,area,heroes);
 }
 private static boolean activePending(Object progress,byte[]profile)throws IOException{
  if(!Boolean.TRUE.equals(DreamAccess.get(progress,"patrolRewardPending")))return false;
  int area=(Integer)DreamAccess.get(progress,"patrolArea");if(area<1||area>8||!Objects.equals(DreamAccess.stat(DreamAccess.type("LocalPatrolEngine"),"dayKey",new Class<?>[]{byte[].class},profile),DreamAccess.get(progress,"patrolDay")))return false;
  DreamState.Change gate=DreamState.canPatrol(profile,catalog(),scope(profile,progress));
  return gate.reason==DreamState.Reason.PATROL_ALLOWED||gate.reason==DreamState.Reason.PATROL_LIMIT_REACHED;
 }
 private static void commit(LocalGatewayServer gateway,String account,Object live,LocalEventEngine engine,DreamStorage tx,byte[]before,byte[]next,Object candidate,DreamState.Scope scope,String id,String kind)throws IOException{
  byte[]receipt=BsonLite.document("v",1,"id",id,"kind",kind,"catalog",DreamCatalog.SHA256,"wc",scope.weekCommit,"w",scope.week,"d",scope.day,"rt",scope.route,"delta",DreamPatrolDelta.capture(live,candidate));
  tx.commit(before,BsonLite.withProfileDocument(next,PENDING,receipt));recoverLocked(gateway,account,live,engine,tx);
 }
 private static LocalPatrolEngine.Result ordinaryBegin(LocalGatewayServer g,String a,Object p,LocalEventEngine e,byte[]profile,int area,List<Integer>heroes)throws IOException{
  LocalPatrolEngine.Result r=(LocalPatrolEngine.Result)DreamAccess.stat(DreamAccess.type("LocalPatrolEngine"),"begin",new Class<?>[]{LocalPatrolCatalog.class,p.getClass(),LocalEventEngine.class,byte[].class,int.class,List.class},DreamAccess.get(g,"patrolCatalog"),p,e,profile,area,heroes);save(g,a,p);return r;
 }
 private static LocalPatrolEngine.Result result(boolean success,List<Integer>events,String reason){return new LocalPatrolEngine.Result(success,events,reason);}
 private static void replace(Object p,String key,Collection<Integer>v)throws IOException{Set<Integer>s=DreamPatrolDelta.set(p,key);s.clear();s.addAll(v);}
 @SuppressWarnings("unchecked")private static Map<String,Set<Integer>>conditions(Object p)throws IOException{return(Map<String,Set<Integer>>)DreamAccess.get(p,"eventConditions");}
 private static int integer(byte[]d,String k)throws IOException{Integer v=BsonLite.intValue(d,k);if(v==null)throw new IOException("Dream integer "+k);return v;}
 static DreamState.Scope scope(byte[]p,Object progress)throws IOException{byte[]w=BsonLite.documentValue(p,"weeknum"),s=BsonLite.documentValue(p,"std");try{return new DreamState.Scope((String)DreamAccess.get(progress,"weekCommit"),integer(w,"w"),BsonLite.stringValue(s,"rt"),integer(w,"d"));}catch(IllegalArgumentException e){throw new IOException("Dream authoritative scope",e);}}
}
