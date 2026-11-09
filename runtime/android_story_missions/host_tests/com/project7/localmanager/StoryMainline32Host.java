package com.project7.localmanager;
import android.content.*;import android.content.res.*;import java.io.*;import java.lang.reflect.*;import java.nio.*;import java.nio.file.*;import java.util.*;
/**
 * Real Main consumers for the promoted generic exact-key chapters.
 *
 * Uses the original Gateway/Store/Engine and the packaged StoryMissionBridge;
 * only synthesized public profiles/progress are written. No D8/APK/native.
 */
public final class StoryMainline32Host {
 static int checks;static void check(boolean b,String m){checks++;if(!b)throw new AssertionError(m);}
 static byte[]doc(byte[]p,String k){byte[]d=BsonLite.documentValue(p,k);return d==null?BsonLite.EMPTY_DOCUMENT:d;}
 static int cs(byte[]stages){return BsonLite.intValue(stages,"cs");}
 static Object call(Object receiver,String name,Class<?>[]types,Object...args)throws Exception{
  Method m=receiver.getClass().getDeclaredMethod(name,types);m.setAccessible(true);
  try{return m.invoke(receiver,args);}catch(InvocationTargetException e){if(e.getCause() instanceof Exception)throw(Exception)e.getCause();throw e;}
 }
 static Object original(String name,Class<?>[]types,Object...args)throws Exception{
  Method m=LocalCityProgress.class.getDeclaredMethod("q7Original"+name,types);m.setAccessible(true);return m.invoke(null,args);
 }
 static final class Disk implements AutoCloseable {
  static final String ACCOUNT="host_mainline32";static final byte[]EID=new byte[12];
  final Path root,file;final LocalProfileStore store;final LocalTutorialStore tutorials;final LocalGatewayServer g;
  final LocalTutorialStore.Progress p;final LocalEventEngine engine;
  Disk(File assets,String rt,int menu,List<Integer> events)throws Exception{
   root=Files.createTempDirectory("mainline32-synthetic-");Files.createDirectory(root.resolve("profiles"));
   file=root.resolve("profiles/"+ACCOUNT+".bson");
   Context context=new Context(root.toFile(),new AssetManager(assets));store=new LocalProfileStore(context);
   tutorials=new LocalTutorialStore(context);
   byte[]raw=BsonLite.withAccountIdentity(Files.readAllBytes(new File(assets,"new_player.bson").toPath()),ACCOUNT,900202);
   raw=BsonLite.withProfileDocument(raw,"weeknum",BsonLite.document("w",3,"d",0,"av",0));
   raw=BsonLite.withProfileDocument(raw,"std",BsonLite.document("rt",rt,"ff",false));
   raw=BsonLite.withProfileInt(raw,"q7ChapterMenu",menu);
   raw=BsonLite.withHero(raw,10);Files.write(file,raw);
   p=LocalTutorialStore.Progress.fresh();p.initPrologue=false;p.inEmergency=false;p.patrolActions=24;
   p.completedEvents.addAll(Arrays.asList(1013,1043));p.completedEvents.addAll(events);
   p.eventConditions.put("battle",new HashSet<Integer>());
   LocalEventCatalog graph=new LocalEventCatalog(new FileInputStream(new File(assets,"event_graph.tsv")));
   LocalNewbeeCatalog nb=new LocalNewbeeCatalog(new ByteArrayInputStream(new byte[0]));
   engine=new LocalEventEngine(graph,nb,p,0,raw,true);p.processingEvents.clear();p.availableEvents.clear();
   tutorials.save(ACCOUNT,p);
   g=new LocalGatewayServer(0,null,store,tutorials,graph,nb,new LocalCombatCatalog(context),new LocalPatrolCatalog(context),new LocalGatewayServer.StatusListener(){public void onStatus(boolean ok,String message){}});
  }
  byte[]read()throws Exception{return Files.readAllBytes(file);}
  LocalTutorialStore.Progress reload()throws Exception{return tutorials.load(ACCOUNT);}
  public void close()throws Exception{g.close();try(java.util.stream.Stream<Path>s=Files.walk(root)){for(Path path:(Iterable<Path>)s.sorted(Comparator.reverseOrder())::iterator)Files.delete(path);}}
 }
 static byte[]begin(int scene,int area){return BsonLite.document("t",1,"s",scene,"h",Arrays.asList(10),"d",BsonLite.document("a",area));}
 static byte[]finish(int scene,int win){return BsonLite.document("t",1,"s",scene,"h",Arrays.asList(10),"w",win,"x",Collections.emptyList());}
 static void gatewayFinish(Disk d,LocalEconomyEngine.Result result,int scene,int win)throws Exception{
  call(d.g,"finishStoryCombat",new Class<?>[]{OutputStream.class,byte[].class,String.class,LocalTutorialStore.Progress.class,LocalEventEngine.class,Set.class,Set.class,int.class,int.class,int.class,LocalEconomyEngine.Result.class},new ByteArrayOutputStream(),Disk.EID,Disk.ACCOUNT,d.p,d.engine,new HashSet<Integer>(),new HashSet<Integer>(),1,scene,win,result);
 }
 static byte[] reliable(Disk d,String method,byte[] params,int seq)throws Exception{
  ByteArrayOutputStream out=new ByteArrayOutputStream();
  byte[] wrapper=BsonLite.document("w",BsonLite.document("r",seq,"m",method,"p",params,"_cbid_",seq));
  call(d.g,"handleReliableRpc",new Class<?>[]{OutputStream.class,byte[].class,byte[].class,String.class,LocalTutorialStore.Progress.class,LocalEventEngine.class,Set.class,Set.class,Map.class,Set.class},out,Disk.EID,wrapper,Disk.ACCOUNT,d.p,d.engine,new HashSet<Integer>(),new HashSet<Integer>(),new HashMap<Integer,Object>(),new HashSet<Integer>());
  return out.toByteArray();
 }
 static byte[] admit(Disk d,int scene,int area,int seq)throws Exception{
  return reliable(d,"combatOfflineRequest",BsonLite.document("t",1,"s",scene,"h",Arrays.asList(10),"d",BsonLite.document("a",area)),seq);
 }
 static byte[] offlineFinish(Disk d,int scene,int win)throws Exception{
  ByteArrayOutputStream out=new ByteArrayOutputStream();
  call(d.g,"handleCombatOfflineFinish",new Class<?>[]{OutputStream.class,byte[].class,byte[].class,String.class,LocalTutorialStore.Progress.class,LocalEventEngine.class,Set.class,Set.class},out,Disk.EID,finish(scene,win),Disk.ACCOUNT,d.p,d.engine,new HashSet<Integer>(),new HashSet<Integer>());
  return out.toByteArray();
 }
 static List<ProtoLite.EntityMessage> frames(byte[]wire)throws IOException{
  List<ProtoLite.EntityMessage>all=new ArrayList<>();ByteBuffer b=ByteBuffer.wrap(wire).order(ByteOrder.LITTLE_ENDIAN);
  while(b.hasRemaining()){int len=b.getInt();check(b.getShort()==5,"opcode");byte[]msg=new byte[len-2];b.get(msg);all.add(ProtoLite.parseEntityMessage(msg));}
  return all;
 }
 static boolean pushHas(byte[]wire,int event)throws Exception{
  byte[]digest=java.security.MessageDigest.getInstance("MD5").digest("pushEvents".getBytes("UTF-8"));
  for(ProtoLite.EntityMessage m:frames(wire))if(Arrays.equals(digest,m.methodMd5)){
   byte[]array=BsonLite.arrayValue(m.parameters,"a");
   if(array!=null)for(String key:BsonLite.keys(array)){
    Integer id=BsonLite.intValue(BsonLite.documentValue(array,key),"0");
    if(id!=null&&id.intValue()==event)return true;
   }
   return false;
  }
  return false;
 }
 static boolean hasFrame(byte[]wire,String method)throws Exception{
  byte[]digest=java.security.MessageDigest.getInstance("MD5").digest(method.getBytes("UTF-8"));
  for(ProtoLite.EntityMessage m:frames(wire))if(Arrays.equals(digest,m.methodMd5))return true;
  return false;
 }
 static void menu32(File assets)throws Exception{
  try(Disk d=new Disk(assets,"35-1",32,new ArrayList<Integer>())){
   byte[] profile=d.read();
   check(StoryMissionBridge.area(1135)==2,"menu32 scene1135 area2");
   byte[] stages=LocalCityProgress.stages(d.p,2,profile);
   check(cs(stages)==1135,"menu32 area2 cs1135 "+BsonLite.messagePackValue(stages,false));
   LocalEconomyEngine.Result begin=d.store.updateEconomy(Disk.ACCOUNT,"begin",begin(1135,2),d.p);
   check(begin.accepted,"menu32 begin1135 "+begin.reason);
   LocalEconomyEngine.Result won=d.store.updateEconomy(Disk.ACCOUNT,"finish",finish(1135,1),d.p);
   check(won.accepted&&won.win==1,"menu32 win1135 "+won.reason);
   gatewayFinish(d,won,1135,1);
   check(cs(LocalCityProgress.stages(d.p,2,d.read()))==1136,"menu32 win advances cs1136");
   check(d.store.updateEconomy(Disk.ACCOUNT,"begin",begin(1136,2),d.p).accepted,"menu32 begin1136");
   LocalEconomyEngine.Result won2=d.store.updateEconomy(Disk.ACCOUNT,"finish",finish(1136,1),d.p);
   check(won2.accepted&&won2.win==1,"menu32 win1136 "+won2.reason);
   gatewayFinish(d,won2,1136,1);
   check(cs(LocalCityProgress.stages(d.p,2,d.read()))==1137,"menu32 win advances cs1137");
   LocalEconomyEngine.Result gated=d.store.updateEconomy(Disk.ACCOUNT,"begin",begin(1137,2),d.p);
   check(!gated.accepted,"menu32 1137 gate blocks without 20007");
   d.p.completedEvents.add(20007);
   check(d.store.updateEconomy(Disk.ACCOUNT,"begin",begin(1137,2),d.p).accepted,"menu32 1137 opens with 20007");
   d.tutorials.save(Disk.ACCOUNT,d.p);
   check(cs(LocalCityProgress.stages(d.reload(),2,d.read()))==1137,"menu32 reload keeps cs1137");
  }
 }
 public static void main(String[]args)throws Exception{
  File assets=new File(args[0]);Context context=new Context(assets,new AssetManager(assets));
  CoreDrawPolicy.prepare(context);HistoryDrawPolicy.prepare(context);SelectorPolicy.prepare(context);
  OfflineMechanismGateway.prepare(context);
  StoryMissionBridge.prepare(context);StoryMissionBridge.prepareSpecial(context);StoryCityPolicy.prepare(context);
  if(args.length>1&&args[1].equals("menu32")){menu32(assets);System.out.println("PASS "+checks+" menu32 C/A/M/G stage/settlement/reload");return;}
  String token=StoryMissionBridge.specialToken();
  check(token!=null&&token.length()==64,"selector11 descriptor loaded with token");
  check(StoryMissionBridge.area(320)==6,"selector11 member keeps area 6, not flattened");
  check(StoryMissionBridge.area(1124)==2&&StoryMissionBridge.area(22010)==1,"generic scene area mapping");
  check(StoryMissionBridge.area(101)==LocalCityProgress.area(101),"unmatched scene keeps original area");
  // Generic chain 1: area2 route31-1 (menu28) scenes 1124..1126, no gate on first scene.
  try(Disk d=new Disk(assets,"31-1",28,Arrays.asList(20007))){
   byte[]profile=d.read();
   check(LocalCityProgress.status(d.p,2,profile)==1&&StoryMissionBridge.status(d.p,2,profile)==1,"area2 route31 fresh status1");
   byte[]stages=LocalCityProgress.stages(d.p,2,profile);
   check(cs(stages)==1124,"generic cs1124 "+BsonLite.messagePackValue(stages,false));
   check(BsonLite.keys(BsonLite.arrayValue(stages,"sl")).size()==10,"ten descriptor groups");
   byte[]minusOne=BsonLite.withProfileDocument(profile,"std",BsonLite.document("rt","-1","ff",false));
   byte[]fallback=(byte[])original("Stages",new Class<?>[]{LocalTutorialStore.Progress.class,int.class,byte[].class},d.p,2,minusOne);
   check(Arrays.equals(LocalCityProgress.stages(d.p,2,minusOne),fallback),"default -1 keeps original stages");
   check(Arrays.equals(StoryMissionBridge.stages(d.p,2,minusOne),fallback),"bridge miss delegates -1");
   byte[]unknown=BsonLite.withProfileDocument(profile,"std",BsonLite.document("rt","99","ff",false));
   check(Arrays.equals(StoryMissionBridge.stages(d.p,2,unknown),(byte[])original("Stages",new Class<?>[]{LocalTutorialStore.Progress.class,int.class,byte[].class},d.p,2,unknown)),"unknown route delegates");
   check(LocalCityProgress.consumeVictory(d.p,profile,1,1124),"area2 victory cost path admitted");
   check(d.p.patrolActions==22,"source va2 action spend");
   d.p.eventConditions.get("battle").clear();
   // Real store admission/loss/replay/win/economy.
   LocalEconomyEngine.Result begin=d.store.updateEconomy(Disk.ACCOUNT,"begin",begin(1124,2),d.p);
   check(begin.accepted,"store begin 1124 "+begin.reason);
   LocalEconomyEngine.Result lost=d.store.updateEconomy(Disk.ACCOUNT,"finish",finish(1124,0),d.p);
   check(lost.accepted&&lost.win==0,"store loss settles "+lost.reason);
   gatewayFinish(d,lost,1124,0);
   check(!d.p.eventConditions.get("battle").contains(1124),"loss leaves no victory trace");
   check(cs(LocalCityProgress.stages(d.p,2,d.read()))==1124,"loss keeps cs1124");
   byte[]afterLoss=d.read();
   LocalEconomyEngine.Result replayLoss=d.store.updateEconomy(Disk.ACCOUNT,"finish",finish(1124,0),d.p);
   check(!replayLoss.accepted||replayLoss.replay,"loss replay cannot settle twice");
   check(Arrays.equals(afterLoss,d.read()),"loss replay image preserved");
   LocalEconomyEngine.Result won=d.store.updateEconomy(Disk.ACCOUNT,"begin",begin(1124,2),d.p);
   check(won.accepted,"second begin 1124 "+won.reason);
   LocalEconomyEngine.Result victory=d.store.updateEconomy(Disk.ACCOUNT,"finish",finish(1124,1),d.p);
   check(victory.accepted&&victory.win==1,"store win 1124 "+victory.reason);
   gatewayFinish(d,victory,1124,1);
   check(d.p.eventConditions.get("battle").contains(1124),"postcommit victory trace 1124");
   check(cs(LocalCityProgress.stages(d.p,2,d.read()))==1125,"real win advances cs1125");
   check(d.p.patrolActions==20,"victory spent two actions");
   byte[]committed=d.read();
   LocalEconomyEngine.Result replayWin=d.store.updateEconomy(Disk.ACCOUNT,"finish",finish(1124,1),d.p);
   check(!replayWin.accepted||replayWin.replay,"win replay cannot regrant");
   check(Arrays.equals(committed,d.read()),"win replay image preserved");
   check(d.store.updateEconomy(Disk.ACCOUNT,"begin",begin(1125,2),d.p).accepted,"gate 1125 opens after real1124");
   LocalEconomyEngine.Result win1125=d.store.updateEconomy(Disk.ACCOUNT,"finish",finish(1125,1),d.p);
   check(win1125.accepted&&win1125.win==1,"win 1125 "+win1125.reason);
   gatewayFinish(d,win1125,1125,1);
   check(cs(LocalCityProgress.stages(d.p,2,d.read()))==1126,"real win advances cs1126");
   check(d.store.updateEconomy(Disk.ACCOUNT,"begin",begin(1126,2),d.p).accepted,"gate 1126 opens with seeded 20007");
   LocalEconomyEngine.Result last=d.store.updateEconomy(Disk.ACCOUNT,"finish",finish(1126,1),d.p);
   check(last.accepted&&last.win==1,"final win 1126");
   gatewayFinish(d,last,1126,1);
   byte[] endStages=LocalCityProgress.stages(d.p,2,d.read());
   check(BsonLite.keys(endStages).isEmpty()||cs(endStages)==0,"chain end closes map");
  }
  // Generic chain 2: area1 route5 (menu4) through the full offline-finish entry.
  // The original consumeVictory area<2 guard still rejects; settlement/advance comes
  // from LocalEconomyEngine.finish plus the Gateway battle trace, never from that guard.
  try(Disk d=new Disk(assets,"5",4,Arrays.asList(5053))){
   byte[]profile=d.read();
   check(LocalCityProgress.status(d.p,1,profile)==1,"area1 route5 status1");
   check(cs(LocalCityProgress.stages(d.p,1,profile))==22010,"area1 cs22010");
   int guardActions=d.p.patrolActions;
   check(!StoryMissionBridge.consumeVictory(d.p,profile,1,22010),"original area<2 consumeVictory rejects area1");
   check(d.p.patrolActions==guardActions,"guard rejection spends nothing");
   byte[] admission=admit(d,22010,1,9001);
   check(hasFrame(admission,"combatOfflineReply"),"area1 raw combatOfflineRequest admission reply");
   int actions=d.p.patrolActions;
   offlineFinish(d,22010,1);
   check(d.p.eventConditions.get("battle").contains(22010),"area1 offline finish traces battle");
   check(cs(LocalCityProgress.stages(d.p,1,d.read()))==22011,"area1 offline finish advances cs22011");
   check(d.p.patrolActions==actions-2,"area1 economy va2 spend");
   check(!d.p.availableEvents.contains(10006),"10006 not offered early");
   byte[] admission2=admit(d,22011,1,9002);
   check(hasFrame(admission2,"combatOfflineReply"),"area1 22011 raw admission reply");
   offlineFinish(d,22011,1);
   byte[] admission3=admit(d,22012,1,9003);
   check(hasFrame(admission3,"combatOfflineReply"),"area1 22012 raw admission reply");
   byte[] wire=offlineFinish(d,22012,1);
   check(d.p.availableEvents.contains(10006),"area1 first push offers 10006");
   check(pushHas(wire,10006),"area1 first pushEvents frame carries 10006");
   check(!d.p.completedEvents.contains(10006),"success offer is not a synthetic completion");
   check(d.reload().availableEvents.contains(10006),"reload keeps 10006 available");
   check(BsonLite.keys(LocalCityProgress.stages(d.p,1,d.read())).isEmpty(),"area1 chain closes map");
   int offered=d.p.availableEvents.size();int afterActions=d.p.patrolActions;
   byte[] duplicate=offlineFinish(d,22012,1);
   check(d.p.availableEvents.size()==offered,"duplicate finish does not duplicate offer");
   check(!d.p.completedEvents.contains(10006),"duplicate finish does not complete event");
   check(BsonLite.keys(LocalCityProgress.stages(d.p,1,d.read())).isEmpty(),"duplicate finish keeps chain closed");
   check(d.p.patrolActions==afterActions,"duplicate finish does not re-spend");
  }
  // Generic chain 3: area2 route21 (menu20) loss/win success outcome and cross-route gate.
  try(Disk d=new Disk(assets,"21",20,Arrays.asList(2118,1120,1375))){
   d.p.eventConditions.get("battle").add(2118);
   byte[]profile=d.read();
   check(cs(LocalCityProgress.stages(d.p,2,profile))==1114,"route21 cs1114");
   check(!d.p.availableEvents.contains(20058),"no success before a real win");
   LocalEconomyEngine.Result first=d.store.updateEconomy(Disk.ACCOUNT,"begin",begin(1114,2),d.p);
   check(first.accepted,"1114 admitted "+first.reason);
   LocalEconomyEngine.Result lost=d.store.updateEconomy(Disk.ACCOUNT,"finish",finish(1114,0),d.p);
   check(lost.accepted&&lost.win==0,"1114 loss settles");
   gatewayFinish(d,lost,1114,0);
   check(!d.p.availableEvents.contains(20058),"loss does not offer 20058");
   check(d.store.updateEconomy(Disk.ACCOUNT,"begin",begin(1114,2),d.p).accepted,"1114 re-admitted");
   LocalEconomyEngine.Result won=d.store.updateEconomy(Disk.ACCOUNT,"finish",finish(1114,1),d.p);
   check(won.accepted&&won.win==1,"1114 win settles");
   gatewayFinish(d,won,1114,1);
   check(d.p.eventConditions.get("battle").contains(1114),"1114 victory trace");
   check(d.p.availableEvents.contains(20058),"1114 success 20058 offered");
   check(cs(LocalCityProgress.stages(d.p,2,d.read()))==1115,"1114 advances cs1115");
   LocalEconomyEngine.Result gated=d.store.updateEconomy(Disk.ACCOUNT,"begin",begin(1115,2),d.p);
   check(!gated.accepted,"1115 cross-route prerequisite 1120 still blocks admission");
   byte[]selector=BsonLite.withProfileDocument(profile,"std",BsonLite.document("rt","10-6","ff",false));
   byte[]after=StoryMissionBridge.stages(d.p,6,selector);
   check(BsonLite.keys(after).isEmpty()||cs(after)==320,"selector11 route remains descriptor/empty");
  }
  // Full offline entry: loss does not offer, trace, advance, or spend.
  try(Disk d=new Disk(assets,"5",4,Arrays.asList(5053))){
   check(d.store.updateEconomy(Disk.ACCOUNT,"begin",begin(22010,1),d.p).accepted,"loss-case begin");
   int actions=d.p.patrolActions;
   byte[] wire=offlineFinish(d,22010,0);
   check(!d.p.eventConditions.get("battle").contains(22010),"loss leaves no battle trace");
   check(cs(LocalCityProgress.stages(d.p,1,d.read()))==22010,"loss keeps cs22010");
   check(!d.p.availableEvents.contains(10006),"loss offers no success");
   check(d.p.patrolActions==actions,"loss spends no actions");
  }
  // Same-week route switch: old battle is claimed only when the current route owns it.
  try(Disk d=new Disk(assets,"21",20,Arrays.asList(2118))){
   d.p.eventConditions.get("battle").add(22012);
   byte[] profile=d.read();
   StoryMissionBridge.offerMissionOutcomes(d.p,profile);
   check(!d.p.availableEvents.contains(10006),"old-route battle not offered under route21");
   byte[] route5=BsonLite.withProfileDocument(profile,"std",BsonLite.document("rt","5","ff",false));
   StoryMissionBridge.offerMissionOutcomes(d.p,route5);
   check(d.p.availableEvents.contains(10006),"same-week route5 claims old 22012 success");
  }
  // Mutex boundary: a completed mutex peer suppresses the success offer.
  try(Disk d=new Disk(assets,"5",4,Arrays.asList(5053))){
   d.p.eventConditions.get("battle").add(22012);
   d.p.completedEvents.add(82);
   StoryMissionBridge.offerMissionOutcomes(d.p,d.read());
   check(!d.p.availableEvents.contains(10006),"mutex peer blocks 10006");
  }
  // New-week relogin with reset battle set emits nothing.
  try(Disk d=new Disk(assets,"5",4,Arrays.asList(5053))){
   d.p.eventConditions.get("battle").clear();
   d.p.weekCommit="next-week";
   StoryMissionBridge.offerMissionOutcomes(d.p,d.read());
   check(!d.p.availableEvents.contains(10006),"new-week reset battle emits no old success");
  }
  System.out.println("PASS "+checks+" real Main consumers: query/-1 fallback/raw admission/full offline finish/first push/reload/loss/duplicate/route switch/new week/mutex/selector11/success outcomes/area1 guard-reject");

 }
}
