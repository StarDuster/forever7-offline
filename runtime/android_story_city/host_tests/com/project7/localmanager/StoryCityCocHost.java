package com.project7.localmanager;
import android.content.*;import android.content.res.*;import java.io.*;import java.nio.file.*;import java.util.*;
/** Actual Store/Progress/EventEngine host for the seven route-27-1 COC missions. */
public final class StoryCityCocHost {
 static final String ACCOUNT="host_story_city_coc", WEEK="coc-week", CATALOG="af2328b97372c27fd392b5b399d03daa17fa73acdd35d2b1ad5b0a8f07218069";
 static final int[] SCENES={482,483,484,485,486,487,488};
 static final int[] AREAS={10000,6,10001,4,10002,10003,2};
 static final int[] PREDECESSORS={7,10000,6,10001,4,10002,10003};
 static final int[] COMPLETIONS={1435,1436,1437,1438,1439,1440,1441};
 static int checks;
 static File assets;
 static void check(boolean value,String why){checks++;if(!value)throw new AssertionError(why);}
 static byte[]doc(byte[]p,String k){byte[]d=p==null?null:BsonLite.documentValue(p,k);return d==null?BsonLite.EMPTY_DOCUMENT:d;}
 static byte[]request(int scene,int area,int type,List<Integer>heroes){return BsonLite.document("t",type,"s",scene,"d",BsonLite.document("a",area),"h",heroes);}
 static byte[]finishRequest(int scene,int area,int win,List<Integer>heroes){return BsonLite.document("t",1,"s",scene,"d",BsonLite.document("a",area),"h",heroes,"w",win,"x",Collections.emptyList());}
 static final class Disk implements AutoCloseable {
  final Path root,file,progressFile;final LocalProfileStore store;final LocalTutorialStore tutorials;final Context context;
  Disk()throws Exception{root=Files.createTempDirectory("story-city-coc-");Files.createDirectory(root.resolve("profiles"));file=root.resolve("profiles/"+ACCOUNT+".bson");progressFile=root.resolve("progress.tsv");context=new Context(root.toFile(),new AssetManager(assets));store=new LocalProfileStore(context);tutorials=new LocalTutorialStore(context);}
  byte[]profile()throws IOException{return Files.readAllBytes(file);}
  byte[]writeProfile(byte[]profile)throws IOException{Files.write(file,profile);return profile;}
  byte[]save(LocalTutorialStore.Progress p)throws Exception{tutorials.save(ACCOUNT,p);try(java.util.stream.Stream<Path>s=Files.walk(root)){for(Path path:(Iterable<Path>)s::iterator)if(Files.isRegularFile(path)&&!path.equals(file))return Files.readAllBytes(path);}throw new AssertionError("tutorial store file");}
  LocalTutorialStore.Progress load()throws Exception{return tutorials.load(ACCOUNT);}
  public void close()throws Exception{try(java.util.stream.Stream<Path>s=Files.walk(root)){for(Path path:(Iterable<Path>)s.sorted(Comparator.reverseOrder())::iterator)Files.delete(path);}}
 }
 static byte[]baseProfile(int scene,int area,int predecessor,int week)throws Exception{
  byte[]profile=BsonLite.withAccountIdentity(Files.readAllBytes(new File(assets,"new_player.bson").toPath()),ACCOUNT,900777);
  profile=BsonLite.withProfileDocument(profile,"weeknum",BsonLite.document("w",week,"d",0,"av",60));
  profile=BsonLite.withProfileDocument(profile,"std",BsonLite.document("rt","27-1","ff",false));
  profile=BsonLite.withProfileInt(profile,"q7ChapterMenu",25);
  profile=BsonLite.withProfileInt(profile,"level",50);
  profile=BsonLite.withProfileDocument(profile,"q7ChapterStates",BsonLite.document(Integer.toString(predecessor),0,Integer.toString(area),1));
  profile=BsonLite.withProfileDocument(profile,"q7ChapterLocks",BsonLite.EMPTY_DOCUMENT);
  profile=BsonLite.withProfileArray(profile,"q7WeekEventBaseline",Collections.emptyList());
  profile=BsonLite.withProfileDocument(profile,"q7StoryCity",BsonLite.document("schema",1,"catalog",CATALOG,"week",WEEK));
  profile=BsonLite.withProfileDocument(profile,"city",BsonLite.document("av",60));
  profile=BsonLite.withHero(profile,135);
  return profile;
 }
 static LocalTutorialStore.Progress progress(){LocalTutorialStore.Progress p=LocalTutorialStore.Progress.fresh();p.initPrologue=false;p.inEmergency=false;p.patrolActions=60;p.weekCommit=WEEK;p.weekIndex=3;return p;}
 static void reject(StoryCityCocPolicy.Admission a,String reason,String why){check(!a.allowed&&reason.equals(a.reason),why+" got="+a.reason);}
 public static void main(String[]args)throws Exception{
  assets=new File(args[0]);
  Context context=new Context(assets,new AssetManager(assets));
  CoreDrawPolicy.prepare(context);HistoryDrawPolicy.prepare(context);SelectorPolicy.prepare(context);OfflineMechanismGateway.prepare(context);StoryMissionBridge.prepare(context);StoryCityPolicy.prepare(context);StoryCityCocPolicy.prepare(context);
  LocalEventCatalog events=new LocalEventCatalog(new FileInputStream(new File(assets,"event_graph.tsv")));
  LocalNewbeeCatalog newbees=new LocalNewbeeCatalog(new ByteArrayInputStream(new byte[0]));
  for(int i=0;i<SCENES.length;i++){
   int scene=SCENES[i],area=AREAS[i],predecessor=PREDECESSORS[i],completion=COMPLETIONS[i];
   try(Disk disk=new Disk()){
    byte[]profile=disk.writeProfile(baseProfile(scene,area,predecessor,3));
    LocalTutorialStore.Progress p=progress();
    StoryCityCocPolicy.Admission admitted=StoryCityCocPolicy.admit(p,profile,scene,request(scene,area,1,Arrays.asList(135)));
    check(admitted.allowed,"admit "+scene+" "+admitted.reason);check(admitted.actionCost==2,"cost source 2 "+scene);check(admitted.party.equals(Arrays.asList(135)),"party source "+scene);
    reject(StoryCityCocPolicy.admit(p,profile,scene,request(scene,area,1,Arrays.asList(134))),StoryCityCocPolicy.PARTY,"wrong party "+scene);
    reject(StoryCityCocPolicy.admit(p,profile,scene,request(scene,area,1,Arrays.asList(135,136))),StoryCityCocPolicy.PARTY,"extra party "+scene);
    reject(StoryCityCocPolicy.admit(p,profile,scene,request(scene,area,2,Arrays.asList(135))),StoryCityCocPolicy.PARTY,"wire type "+scene);
    reject(StoryCityCocPolicy.admit(p,profile,scene,request(scene,area+1,1,Arrays.asList(135))),StoryCityCocPolicy.PARTY,"wire area "+scene);
    p.patrolActions=1;reject(StoryCityCocPolicy.admit(p,profile,scene,request(scene,area,1,Arrays.asList(135))),StoryCityCocPolicy.COST,"cost gate "+scene);p.patrolActions=60;
    byte[]unfree=baseProfile(scene,area,predecessor,3);unfree=BsonLite.withProfileDocument(unfree,"q7ChapterStates",BsonLite.document(Integer.toString(area),1));
    reject(StoryCityCocPolicy.admit(p,unfree,scene,request(scene,area,1,Arrays.asList(135))),StoryCityCocPolicy.GATE_PREDECESSOR,"predecessor gate "+scene);
    byte[]locked=baseProfile(scene,area,predecessor,3);locked=BsonLite.withProfileDocument(locked,"q7ChapterLocks",BsonLite.document(Integer.toString(area),true));
    reject(StoryCityCocPolicy.admit(p,locked,scene,request(scene,area,1,Arrays.asList(135))),StoryCityCocPolicy.GATE_LOCKED,"lock gate "+scene);
    byte[]closed=baseProfile(scene,area,predecessor,3);closed=BsonLite.withProfileDocument(closed,"q7ChapterStates",BsonLite.document(Integer.toString(predecessor),0,Integer.toString(area),0));
    reject(StoryCityCocPolicy.admit(p,closed,scene,request(scene,area,1,Arrays.asList(135))),StoryCityCocPolicy.GATE_STATUS,"status gate "+scene);

    StoryCityCocPolicy.Settlement begin=StoryCityCocPolicy.begin(disk.store,ACCOUNT,p,profile,scene,request(scene,area,1,Arrays.asList(135)));
    check(begin.accepted&&begin.reason.equals(StoryCityCocPolicy.ALLOWED),"store begin "+scene+" "+begin.reason);
    check(p.patrolActions==60,"begin does not spend "+scene);
    check(p.processingEvents.contains(completion),"server pending event "+completion);
    byte[]open=disk.profile();check(!BsonLite.keys(doc(open,"q7Battle")).isEmpty(),"store begin wrote q7Battle "+scene);

    LocalEventEngine engine=new LocalEventEngine(events,newbees,p,0,open,true);
    byte[]beforeImage=disk.profile();
    StoryCityCocPolicy.Settlement settled=StoryCityCocPolicy.settle(disk.store,ACCOUNT,p,open,scene,finishRequest(scene,area,1,Arrays.asList(135)),1,engine);
    check(settled.accepted&&settled.reason.equals(StoryCityCocPolicy.SETTLED),"store settle "+scene+" "+settled.reason);
    check(p.patrolActions==58,"source va2 once "+scene);
    check(p.eventConditions.get("battle")!=null&&p.eventConditions.get("battle").contains(scene),"battle trace "+scene);
    check(p.completedEvents.contains(completion),"completion event "+completion);
    check(settled.completed,"engine completion "+scene);
    int money=BsonLite.intValue(settled.reward,"money");check(money>0,"original level reward "+scene);check(BsonLite.intValue(settled.reward,"sid")==scene,"reward sid "+scene);
    byte[]settledImage=disk.profile();check(!Arrays.equals(beforeImage,settledImage),"settlement commits once "+scene);
    check(!BsonLite.keys(BsonLite.documentValue(doc(settledImage,"q7BattleReceipts"),"3:"+scene)).isEmpty(),"store receipt "+scene);

    StoryCityCocPolicy.Admission replayAdmission=StoryCityCocPolicy.admit(p,settledImage,scene,request(scene,area,1,Arrays.asList(135)));
    reject(replayAdmission,StoryCityCocPolicy.ALREADY_SETTLED,"admission replay "+scene);
    StoryCityCocPolicy.Settlement replay=StoryCityCocPolicy.settle(disk.store,ACCOUNT,p,settledImage,scene,finishRequest(scene,area,1,Arrays.asList(135)),1,engine);
    check(!replay.accepted&&replay.reason.equals(StoryCityCocPolicy.ALREADY_SETTLED),"settle replay rejected "+scene);
    check(Arrays.equals(settledImage,disk.profile()),"replay profile unchanged "+scene);
    LocalEconomyEngine.Result duplicate=disk.store.updateEconomy(ACCOUNT,"finish",finishRequest(scene,area,1,Arrays.asList(135)),p);
    check(duplicate.replay&&Arrays.equals(settledImage,disk.profile()),"store duplicate replay no regrant "+scene);
    byte[]saved=disk.save(p);LocalTutorialStore.Progress loaded=disk.load();
    check(loaded.completedEvents.contains(completion)&&loaded.eventConditions.get("battle").contains(scene),"progress persisted "+scene);
    check(loaded.patrolActions==58,"progress actions persisted "+scene);
    check(Arrays.equals(saved,disk.save(loaded)),"same progress snapshot "+scene);
    System.out.println("COC "+scene+" area="+area+" gate="+predecessor+"->0 cost=2 party=135 actions=58 completion="+completion+" money="+money+" replay=rejected");
   }
  }
  // Loss is an explicit no-reward settlement and leaves the mission retryable.
  try(Disk disk=new Disk()){
   byte[]profile=disk.writeProfile(baseProfile(482,10000,7,3));
   LocalTutorialStore.Progress p=progress();
   check(StoryCityCocPolicy.begin(disk.store,ACCOUNT,p,profile,482,request(482,10000,1,Arrays.asList(135))).accepted,"loss begin 482");
   byte[]open=disk.profile();LocalEventEngine engine=new LocalEventEngine(events,newbees,p,0,open,true);
   StoryCityCocPolicy.Settlement lost=StoryCityCocPolicy.settle(disk.store,ACCOUNT,p,open,482,finishRequest(482,10000,0,Arrays.asList(135)),0,engine);
   check(lost.accepted&&lost.reason.equals(StoryCityCocPolicy.LOSS_NO_REWARD)&&lost.reward==null,"loss no reward 482");
   check(p.patrolActions==60&&!p.completedEvents.contains(1435)&&p.processingEvents.isEmpty(),"loss leaves no completion/cost 482");
   check(StoryCityCocPolicy.admit(p,disk.profile(),482,request(482,10000,1,Arrays.asList(135))).allowed,"loss retryable 482");
  }
  // Fixed suppression MH rows must drive the real combat reply without touching player data.
  LocalCombatCatalog baselineCombat=new LocalCombatCatalog(new FileInputStream(new File(assets,"combat_skills.tsv")),new FileInputStream(new File(assets,"combat_attrs.tsv")),new FileInputStream(new File(assets,"suppression-baseline.tsv")),new FileInputStream(new File(assets,"growth.tsv")),new FileInputStream(new File(assets,"home.tsv")));
  LocalCombatCatalog combat=new LocalCombatCatalog(new FileInputStream(new File(assets,"combat_skills.tsv")),new FileInputStream(new File(assets,"combat_attrs.tsv")),new FileInputStream(new File(assets,"suppression.tsv")),new FileInputStream(new File(assets,"growth.tsv")),new FileInputStream(new File(assets,"home.tsv")));
  for(int scene:SCENES)check(baselineCombat.missionHero(scene,135)==null,"baseline MH gap "+scene);
  check(Arrays.equals(baselineCombat.missionHero(315,14),combat.missionHero(315,14)),"normal MH row unchanged");
  Map<Integer,byte[]>expected=new LinkedHashMap<>();
  for(String line:new String(Files.readAllBytes(new File(assets,"suppression-extra.tsv").toPath()),"US-ASCII").split("\n")){
   if(line.isEmpty())continue;String[]row=line.split("\t");check(row.length==3&&row[0].equals("MH"),"MH row schema");
   int scene=Integer.parseInt(row[1].split(":")[0]);expected.put(scene,Base64.getDecoder().decode(row[2]));
  }
  check(expected.size()==7&&expected.keySet().equals(new LinkedHashSet<>(Arrays.asList(482,483,484,485,486,487,488))),"MH scene scope");
  byte[]base=BsonLite.withAccountIdentity(Files.readAllBytes(new File(assets,"new_player.bson").toPath()),ACCOUNT,900778);
  base=BsonLite.withProfileInt(base,"level",50);base=BsonLite.withHero(base,135);base=BsonLite.withHero(base,136);
  byte[]ownedHeroes=BsonLite.documentValue(doc(base,"heromgr"),"hrs");
  java.lang.reflect.Method reply=BsonLite.class.getDeclaredMethod("combatDataDocument",Iterable.class,String.class,byte[].class,LocalCombatCatalog.class,int.class,int.class,int.class);reply.setAccessible(true);
  for(int scene:SCENES){
   byte[]mh=combat.missionHero(scene,135);check(mh!=null&&Arrays.equals(mh,expected.get(scene)),"missionHero "+scene);
   check(combat.missionHero(scene,134)==null,"missionHero wrong hero "+scene);
   byte[]before=base.clone();byte[]wire=(byte[])reply.invoke(null,Arrays.asList(135),"coc",base,combat,50,scene,1);
   check(Arrays.equals(before,base),"combatDataDocument mutated profile "+scene);
   byte[]heroes=BsonLite.documentValue(wire,"heroes"),actor=BsonLite.documentValue(heroes,"('coc', 135)");
   check(actor!=null&&Arrays.equals(actor,mh),"combatDataDocument MH override "+scene);
  }
  check(Arrays.equals(ownedHeroes,BsonLite.documentValue(doc(base,"heromgr"),"hrs")),"owned hero list unchanged");
  check(combat.missionHero(2114,135)==null,"non-COC missionHero null");
  byte[]normal=(byte[])reply.invoke(null,Arrays.asList(135),"coc",base,combat,50,2114,1);
  byte[]none=(byte[])reply.invoke(null,Arrays.asList(135),"coc",base,combat,50,999999,1);
  byte[]normalActor=BsonLite.documentValue(BsonLite.documentValue(normal,"heroes"),"('coc', 135)");
  byte[]noneActor=BsonLite.documentValue(BsonLite.documentValue(none,"heroes"),"('coc', 135)");
  check(normalActor!=null&&noneActor!=null&&Arrays.equals(normalActor,noneActor),"non-COC hero document unchanged");
  check(!Arrays.equals(normalActor,expected.get(482)),"non-COC does not receive COC override");
  check(combat.missionHero(315,14)!=null&&combat.missionHero(315,135)==null&&!Arrays.equals(combat.missionHero(315,14),expected.get(482)),"normal MH preserved");
  System.out.println("PASS MH 7 missionHero(482..488:135) + combatDataDocument MH override, normal MH/player data unchanged");
  System.out.println("PASS "+checks+" actual Store begin/finish/replay, original reward, Progress/EventEngine completion, gate/cost/party negatives, fixed MH override for 482..488");
 }
}
