package com.project7.localmanager;
import java.io.*;
import java.nio.file.*;
import java.util.*;
import java.lang.reflect.*;
public final class RequestEventsHost {
 static final String REQUEST="requestTriggerDaXuanWo";
 static byte[] digest(){return RequestEventCatalog.hash("MD5",REQUEST.getBytes(java.nio.charset.StandardCharsets.UTF_8));}
 static LocalTutorialStore.Progress normal(){LocalTutorialStore.Progress p=LocalTutorialStore.Progress.fresh();p.inEmergency=false;p.initPrologue=false;p.completedEvents.add(1047);p.weekIndex=3;p.availableEvents.clear();p.processingEvents.clear();return p;}
 static void check(boolean v,String m){if(!v)throw new AssertionError(m);}
 static LocalEventEngine engine(LocalEventCatalog graph,LocalTutorialStore.Progress p,boolean cg,int day)throws IOException{return engineAtWeek(graph,p,cg,day,3);}
 static LocalEventEngine engineAtWeek(LocalEventCatalog graph,LocalTutorialStore.Progress p,boolean cg,int day,int week)throws IOException{
  byte[]profile=BsonLite.document("weeknum",BsonLite.document("w",week,"d",day),"cgs",cg?Arrays.asList(281):Collections.emptyList());
  return new LocalEventEngine(graph,new LocalNewbeeCatalog(new ByteArrayInputStream(new byte[0])),p,0,profile,false);
 }
 static RequestEventAdmission.Prepared stage(LocalEventEngine e,RequestEventCatalog c,String name){synchronized(e){return RequestEventAdmission.stage(e,c,name,digest());}}
 public static void main(String[]args)throws Exception{
  RequestEventCatalog c=RequestEventCatalog.fromBytes(Files.readAllBytes(Paths.get(args[0])));
  Path temp=Files.createTempDirectory("p7-request-events-public-");Files.createDirectory(temp.resolve("offline"));Files.copy(Paths.get(args[0]),temp.resolve("offline/request-events.tsv"));
  RequestEventCatalog prepared=RequestEventCatalog.prepare(new android.content.Context(temp.toFile(),new android.content.res.AssetManager(temp.toFile())));
  check(prepared.requests().equals(c.requests()),"actual prepare asset loader");
  Files.delete(temp.resolve("offline/request-events.tsv"));Files.delete(temp.resolve("offline"));Files.delete(temp);
  LocalEventCatalog graph=new LocalEventCatalog(new FileInputStream(args[1]));
  check(!graph.externalEvents.contains(417)&&graph.trigger(417)==null,"original authorization absent");
  check(stage(engine(graph,LocalTutorialStore.Progress.fresh(),true,0),c,REQUEST).status==RequestEventAdmission.Status.CONDITIONS,"stock fresh prologue not idle");
  for(int week:new int[]{1,2})check(stage(engineAtWeek(graph,normal(),true,0,week),c,REQUEST).status==RequestEventAdmission.Status.CONDITIONS,"producer minweek via original engine");
  LocalTutorialStore.Progress p=normal();LocalEventEngine e=engine(graph,p,true,0);
  try{RequestEventAdmission.stage(e,c,REQUEST,digest());throw new AssertionError("monitor");}catch(IllegalStateException expected){}
  check(LocalEventEngine.class.getProtectionDomain().getCodeSource().getLocation().toString().endsWith("manager-translated-frames.jar"),"original class origin");
  java.util.Properties before=p.toProperties();RequestEventAdmission.Prepared outcome=stage(e,c,REQUEST);
  if(outcome.status!=RequestEventAdmission.Status.COMPLETED){
   LocalEventCatalog.Trigger t=new LocalEventCatalog.Trigger(417,c.find(REQUEST,digest()).triggerColumns());
   Method blocker=LocalEventEngine.class.getDeclaredMethod("triggerBlocker",LocalEventCatalog.Trigger.class,int.class,int.class);blocker.setAccessible(true);
   throw new AssertionError("original complete path: "+outcome.status+" blocker="+blocker.invoke(e,t,0,0)+" emergency="+p.inEmergency+" reqEmergency="+t.emergency+" auto="+graph.get(417).autoTrigger);
  }
  check(p.completedEvents.contains(417)&&p.eventCompletions.get(417)==1&&!p.processingEvents.contains(417),"original completion facts");
  check(outcome.completedNotices.contains(417),"actual original completion notice delta");
  check(!graph.effects.containsKey(417),"source event has no effect payload");
  check("3:0".equals(p.eventDays.get(417)),"actual engine calendar");
  RequestEventAdmission.Prepared retry=stage(e,c,REQUEST);check(retry.status==RequestEventAdmission.Status.ALREADY_COMPLETED&&p.eventCompletions.get(417)==1,"idempotent");
  outcome.abortBeforeCommit();check(p.toProperties().equals(before),"whole Progress rollback");
  outcome=stage(e,c,REQUEST);outcome.markCommitted();try{outcome.abortBeforeCommit();throw new AssertionError("postcommit rollback");}catch(IllegalStateException expected){}
  check(p.completedEvents.contains(417),"postcommit delivery failure retains completion");
  for(int day:new int[]{0,1}){
   LocalTutorialStore.Progress n=normal();LocalEventEngine x=engine(graph,n,false,day);java.util.Properties initial=n.toProperties();
   check(stage(x,c,REQUEST).status==RequestEventAdmission.Status.CONDITIONS,"missing CG condition");check(n.toProperties().equals(initial),"negative unchanged");
  }
  LocalTutorialStore.Progress n=normal();LocalEventEngine x=engine(graph,n,true,1);
  check(stage(x,c,REQUEST).status==RequestEventAdmission.Status.CONDITIONS,"actual date condition");
  n.inEmergency=true;n.availableEvents.add(1);check(stage(engine(graph,n,true,0),c,REQUEST).status==RequestEventAdmission.Status.CONDITIONS,"emergency condition");
  n=normal();n.processingEvents.add(417);check(stage(engine(graph,n,true,0),c,REQUEST).status==RequestEventAdmission.Status.ALREADY_PROCESSING,"no duplicate processing");
  LocalTutorialStore.Progress busy=normal();LocalEventEngine busyEngine=engine(graph,busy,true,0);busy.processingEvents.add(999999);
  java.util.Properties busyBefore=busy.toProperties();check(stage(busyEngine,c,REQUEST).status==RequestEventAdmission.Status.BUSY,"other event busy");check(busy.toProperties().equals(busyBefore),"busy unchanged");
  busy.processingEvents.clear();busy.processingNewbees.add(999999);check(stage(busyEngine,c,REQUEST).status==RequestEventAdmission.Status.BUSY,"newbee busy");
  busy.processingEvents.add(417);check(stage(busyEngine,c,REQUEST).status==RequestEventAdmission.Status.ALREADY_PROCESSING,"own processing retry precedes idle");
  busy.completedEvents.add(417);check(stage(busyEngine,c,REQUEST).status==RequestEventAdmission.Status.ALREADY_COMPLETED,"completed retry precedes idle");
  check(stage(e,c,"requestUnknown").status==RequestEventAdmission.Status.UNKNOWN_REQUEST,"no fallback authorization");
  LocalEventCatalog absent=new LocalEventCatalog(new ByteArrayInputStream(new byte[0]));check(stage(engine(absent,normal(),true,0),c,REQUEST).status==RequestEventAdmission.Status.MISSING_EVENT,"missing node");
  Field mutexField=LocalEventCatalog.class.getDeclaredField("mutexEvents");mutexField.setAccessible(true);@SuppressWarnings("unchecked") Map<Integer,Set<Integer>>mutex=(Map<Integer,Set<Integer>>)mutexField.get(graph);
  mutex.put(417,new HashSet<>(Arrays.asList(777)));n=normal();n.completedEvents.add(777);
  check(stage(engine(graph,n,true,0),c,REQUEST).status==RequestEventAdmission.Status.MUTEX,"original isMutex");mutex.remove(417);
  check(!graph.externalEvents.contains(417)&&graph.trigger(417)==null,"global membership untouched");
  byte[] corrupted=Files.readAllBytes(Paths.get(args[0]));corrupted[0]^=1;try{RequestEventCatalog.fromBytes(corrupted);throw new AssertionError("hash");}catch(IllegalArgumentException expected){}
  System.out.println("PASS original-engine admission: completion/retry/rollback/postcommit; CG/date/emergency; processing/unknown/missing/mutex/hash; external/trigger unchanged");
 }
}
