package com.project7.localmanager;
import android.content.*;import android.content.res.*;
import java.io.*;import java.nio.charset.StandardCharsets;import java.nio.file.*;
import java.security.MessageDigest;import java.util.*;
/** Real v26-stage host proof for puzzle room 4.
 *
 * Stage inputs: the pinned prepare classes7.dex and merged event_graph.tsv.  The
 * runnable manager frame is the dex2jar+FrameFix translation of that exact DEX
 * (stage hashes are re-checked here).  All event/room/clue state enters through
 * original consumers:
 *   LocalPatrolEngine.begin(area 7) -> LocalEventEngine.startEvent(3437)
 *   LocalProfileStore.updateServices(q7PuzzleBegin / puzzleRoomGetClue / q7PuzzleExit)
 *   LocalEventEngine.trace(dialog 3437) / trace(ui 1)
 * Processing/available/completed sets are never written by this host; only the
 * fixture profile (prior event 3436, route 27-2, area 7 state) is staged.
 */
public final class PuzzleRoom4StageHost {
 static final String DEX_SHA="fee369231e8924923f774cdbda4961f91b6ab87cee237b249cff8229b535f1c6";
 static final String GRAPH_SHA="50d211e2108524dbce10e9babf9de77cf9faf9e331f8a70f8d1a8f6d771f927f";
 static final String CATALOG="af2328b97372c27fd392b5b399d03daa17fa73acdd35d2b1ad5b0a8f07218069";
 static final String WEEK="puzzle-room4-stage-week";
 static final Set<Integer> ROOM4_CLUES=set(17,18,19,20,21);
 static int checks;
 static File assets;
 static LocalEventCatalog catalog;
 static LocalNewbeeCatalog newbees;
 static LocalPatrolCatalog patrols;
 static void check(boolean value,String why){checks++;if(!value)throw new AssertionError(why);}
 static Set<Integer> set(Integer...values){return new LinkedHashSet<>(Arrays.asList(values));}
 static List<Integer> list(int...values){List<Integer>x=new ArrayList<>();for(int v:values)x.add(v);return x;}
 static byte[] read(File file)throws IOException{return Files.readAllBytes(file.toPath());}
 static String sha(File file)throws Exception{return hex(MessageDigest.getInstance("SHA-256").digest(read(file)));}
 static String hex(byte[]bytes){StringBuilder out=new StringBuilder();for(byte b:bytes)out.append(String.format(Locale.ROOT,"%02x",b&255));return out.toString();}
 static byte[] doc(byte[]profile,String key){byte[]value=profile==null?null:BsonLite.documentValue(profile,key);return value==null?BsonLite.EMPTY_DOCUMENT:value;}
 static List<String> keys(byte[]value){return value==null?Collections.<String>emptyList():BsonLite.keys(value);}
 static boolean hasCamera(byte[]value){return new String(value,StandardCharsets.ISO_8859_1).toLowerCase(Locale.ROOT).contains("camera");}
 static LocalResourceEngine.Reply reply(LocalResourceEngine.Result result,String method){
  for(LocalResourceEngine.Reply reply:result.replies)if(reply.method.equals(method))return reply;
  return null;
 }
 static byte[] profile(String account,int uid)throws Exception{
  byte[]profile=BsonLite.withAccountIdentity(read(new File(assets,"new_player.bson")),account,uid);
  profile=BsonLite.withProfileDocument(profile,"weeknum",BsonLite.document("w",3,"d",2,"av",600));
  profile=BsonLite.withProfileDocument(profile,"std",BsonLite.document("rt","27-2","ff",false));
  profile=BsonLite.withProfileInt(profile,"q7ChapterMenu",25);
  profile=BsonLite.withProfileInt(profile,"level",50);
  profile=BsonLite.withProfileDocument(profile,"q7ChapterStates",BsonLite.document("7",0));
  profile=BsonLite.withProfileDocument(profile,"q7ChapterLocks",BsonLite.EMPTY_DOCUMENT);
  profile=BsonLite.withProfileArray(profile,"q7WeekEventBaseline",Collections.emptyList());
  profile=BsonLite.withProfileDocument(profile,"q7StoryCity",BsonLite.document("schema",1,"catalog",CATALOG,"week",WEEK));
  // Two original insight buildings (id 26) make the reviewed area-7 patrol affordable.
  byte[]building=BsonLite.document("id",26);
  byte[]bd=BsonLite.document("0",building,"1",building);
  byte[]city=BsonLite.document("av",600,"areas",BsonLite.document("area_7",BsonLite.document("bd",bd)));
  profile=BsonLite.withProfileDocument(profile,"city",city);
  profile=BsonLite.withHero(profile,135);
  check(keys(doc(profile,"q7Puzzle")).isEmpty(),"fixture must not seed q7Puzzle");
  check(keys(doc(profile,"q7PuzzleExits")).isEmpty(),"fixture must not seed q7PuzzleExits");
  return profile;
 }
 static LocalTutorialStore.Progress progress(){
  LocalTutorialStore.Progress p=LocalTutorialStore.Progress.fresh();
  p.initPrologue=false;p.inEmergency=false;p.patrolActions=60;p.weekCommit=WEEK;p.weekIndex=3;
  p.completedEvents.add(3436); // prior route 27-2 completion, the trigger prerequisite
  check(p.processingEvents.isEmpty(),"fixture processing set starts empty");
  return p;
 }
 static final class Disk implements AutoCloseable {
  final String account;final Path root,file;final LocalProfileStore store;final LocalTutorialStore tutorials;
  Disk(String account)throws Exception{
   this.account=account;root=Files.createTempDirectory("puzzle-room4-stage-");
   Files.createDirectory(root.resolve("profiles"));file=root.resolve("profiles/"+account+".bson");
   Context context=new Context(root.toFile(),new AssetManager(assets));
   store=new LocalProfileStore(context);tutorials=new LocalTutorialStore(context);
  }
  void write(byte[]profile)throws IOException{Files.write(file,profile);}
  byte[] load(LocalTutorialStore.Progress p)throws IOException{return store.load(account,p);}
  void save(LocalTutorialStore.Progress p)throws IOException{tutorials.save(account,p);}
  LocalTutorialStore.Progress loadProgress()throws IOException{return tutorials.load(account);}
  public void close()throws Exception{
   try(java.util.stream.Stream<Path>stream=Files.walk(root)){
    for(Path path:(Iterable<Path>)stream.sorted(Comparator.reverseOrder())::iterator)Files.delete(path);
   }
  }
 }
 static void checkCatalog(){
  LocalEventCatalog.Event event=catalog.get(3437);
  check(event!=null&&event.release&&event.autoTrigger&&event.repeatable&&!event.autoStart,"3437 patrol trigger flags");
  check(event.dialog==3437&&event.completeConditions.get("dialog").equals(set(3437))&&event.completeConditions.get("ui").equals(set(1)),"3437 dialog/ui conditions");
  LocalEventCatalog.Trigger trigger=catalog.trigger(3437);
  check(trigger.preAll.equals(set(3436))&&trigger.preAny.isEmpty(),"3437 prerequisite 3436");
  check(trigger.mutex.equals(set(3444))&&trigger.areaClicks.isEmpty(),"3437 mutex 3444");
  check(trigger.areas.equals(Collections.singletonMap(7,set(0))),"3437 area 7 state 0");
  check(Arrays.equals(trigger.date,new int[]{2,2})&&trigger.clientOps.equals(set(2))&&trigger.patrolAreas.equals(set(7)),"3437 date/op/patrol");
  check("27,27-2".equals(trigger.predicates.get(52)),"3437 route 27/27-2 predicate");
  check(catalog.mutex(3437).equals(set(3444))&&catalog.mutex(3444).equals(set(3455))&&catalog.mutex(3455).equals(set(3444)),"room4 mutex rows");
  LocalEventCatalog.Event clear=catalog.get(3444),fail=catalog.get(3455);
  check(clear!=null&&clear.release&&!clear.repeatable&&clear.dialog==0&&clear.completeConditions.isEmpty(),"3444 clear event");
  check(fail!=null&&fail.release&&!fail.repeatable&&fail.dialog==0&&fail.completeConditions.isEmpty(),"3455 fail event");
  LocalPuzzleEngine.Room room=catalog.puzzleRooms.get(3437);
  check(room!=null&&room.id==4&&room.clear==3444&&room.incomplete==3455,"room4 keyed by 3437");
  check(room.routes.equals(Collections.singleton("27-2"))&&room.clues.equals(ROOM4_CLUES),"room4 route/clues");
  for(int clue:ROOM4_CLUES){
   LocalPuzzleEngine.Clue row=catalog.puzzleClues.get(clue);
   check(row!=null&&row.room==4&&row.cg==0,"room4 clue "+clue+" cg=0");
  }
  // Old reviewed rooms/clues stay exactly accepted by the merged catalog.
  check(catalog.puzzleRooms.size()==4&&catalog.puzzleClues.size()==21,"4 rooms/21 clues");
  check(catalog.puzzleRooms.get(4229).id==1&&catalog.puzzleRooms.get(4229).clear==4230&&catalog.puzzleRooms.get(4229).incomplete==4231,"old room1");
  check(catalog.puzzleRooms.get(6228).id==2&&catalog.puzzleRooms.get(6228).clear==6229&&catalog.puzzleRooms.get(6228).incomplete==6230,"old room2");
  check(catalog.puzzleRooms.get(7346).id==3&&catalog.puzzleRooms.get(7346).clear==7347&&catalog.puzzleRooms.get(7346).incomplete==7348,"old room3");
  check(catalog.puzzleRooms.get(4229).clues.equals(set(1,2,3,4,5,6)),"old room1 clues");
  check(catalog.puzzleRooms.get(6228).clues.equals(set(7,8,9,10,11)),"old room2 clues");
  check(catalog.puzzleRooms.get(7346).clues.equals(set(12,13,14,15,16)),"old room3 clues");
  for(int clue=1;clue<=16;clue++)check(catalog.puzzleClues.get(clue)!=null&&catalog.puzzleClues.get(clue).room==(clue<=6?1:clue<=11?2:3),"old clue "+clue+" preserved");
 }
 static void checkOpenRoom(byte[]profile,int clues){
  byte[]room=doc(profile,"q7Puzzle");
  check(BsonLite.intValue(room,"format")==1&&BsonLite.intValue(room,"e")==3437&&BsonLite.intValue(room,"r")==4,"open q7Puzzle identity");
  check(BsonLite.intValue(room,"w")==3&&BsonLite.intValue(room,"d")==2,"open q7Puzzle clock");
  check(Boolean.TRUE.equals(BsonLite.boolValue(room,"open")),"q7Puzzle is open");
  check(BsonLite.intArrayValues(room,"clues").size()==clues,"open q7Puzzle clues="+clues);
  check(!hasCamera(room),"open q7Puzzle carries no camera data");
  check(keys(room).equals(Arrays.asList("format","e","r","w","d","n","open","generation","clues")),"open q7Puzzle schema");
  check(BsonLite.intArrayValues(doc(profile,"std"),"prc").size()==clues,"std.prc clues="+clues);
 }
 static byte[] begin(Disk disk,LocalTutorialStore.Progress p,int generation)throws Exception{
  LocalResourceEngine.Result result=disk.store.updateServices(disk.account,"q7PuzzleBegin",BsonLite.document("e",3437),p);
  byte[]profile=result.profile;
  checkOpenRoom(profile,0);
  byte[]room=doc(profile,"q7Puzzle");
  check(BsonLite.intValue(room,"n")==generation,"q7Puzzle generation counter "+generation);
  check(BsonLite.intValue(room,"generation")==LocalPuzzleEngine.generation(p,3437),"q7Puzzle generation value");
  check(reply(result,"evalCode")!=null&&reply(result,"syncPuzzleRoomClue")!=null,"begin replies evalCode+syncPuzzleRoomClue");
  byte[]sync=reply(result,"syncPuzzleRoomClue").parameters;
  check(keys(sync).equals(Collections.singletonList("d"))&&BsonLite.intArrayValues(sync,"d").isEmpty(),"begin sync document has only empty clue data");
  return profile;
 }
 static byte[] collect(Disk disk,LocalTutorialStore.Progress p,byte[]profile,int from,int to)throws Exception{
  List<Integer>expected=new ArrayList<>();
  for(int clue=from;clue<=to;clue++){
   expected.add(clue);
   LocalResourceEngine.Result result=disk.store.updateServices(disk.account,"puzzleRoomGetClue",BsonLite.document("c",clue),p);
   profile=result.profile;
   byte[]room=doc(profile,"q7Puzzle");
   check(BsonLite.intArrayValues(room,"clues").equals(expected),"q7Puzzle clue order "+expected);
   check(BsonLite.intArrayValues(doc(profile,"std"),"prc").equals(expected),"std.prc clue order "+expected);
   LocalResourceEngine.Reply clueReply=reply(result,"puzzleRoomGetClueReturn");
   check(clueReply!=null,"clue "+clue+" getClueReturn reply");
   byte[]payload=clueReply.parameters;
   check(keys(payload).equals(Arrays.asList("r","c","g")),"clue "+clue+" getClueReturn schema");
   check(Boolean.TRUE.equals(BsonLite.boolValue(payload,"r"))&&BsonLite.intValue(payload,"c")==clue,"clue "+clue+" getClueReturn payload");
   check(!hasCamera(room)&&!hasCamera(payload),"clue "+clue+" carries no camera data");
  }
  return profile;
 }
 static byte[] exit(Disk disk,LocalTutorialStore.Progress p,int expectedOutcome,int expectedClues)throws Exception{
  LocalResourceEngine.Result result=disk.store.updateServices(disk.account,"q7PuzzleExit",BsonLite.document("e",3437),p);
  byte[]profile=result.profile;
  byte[]room=doc(profile,"q7Puzzle");
  check(Boolean.FALSE.equals(BsonLite.boolValue(room,"open")),"q7Puzzle closed");
  check(BsonLite.intValue(room,"outcome")==expectedOutcome,"q7Puzzle outcome "+expectedOutcome);
  check(BsonLite.intArrayValues(room,"clues").size()==expectedClues,"exit clue count "+expectedClues);
  check(BsonLite.intArrayValues(doc(profile,"std"),"prc").size()==expectedClues,"exit std.prc count");
  byte[]exits=doc(profile,"q7PuzzleExits");
  check(keys(exits).contains(Integer.toString(expectedOutcome)),"q7PuzzleExits key "+expectedOutcome);
  check(BsonLite.intValue(doc(exits,Integer.toString(expectedOutcome)),"outcome")==expectedOutcome,"q7PuzzleExits outcome");
  check(!hasCamera(room)&&!hasCamera(exits),"exit carries no camera data");
  return profile;
 }
 static LocalPatrolEngine.Result patrol(LocalEventEngine engine,LocalTutorialStore.Progress p,byte[]profile)throws Exception{
  return LocalPatrolEngine.begin(patrols,p,engine,profile,7,list(135));
 }
 static void enterRoom(LocalEventEngine engine,LocalTutorialStore.Progress p,byte[]profile,String tag)throws Exception{
  check(!p.processingEvents.contains(3437),tag+": 3437 not processing before trigger");
  List<Integer>ready=engine.patrolEvents(7,p.patrolHeroes,patrols);
  check(ready.contains(3437),tag+": real patrol trigger offers 3437");
  LocalPatrolEngine.Result result=patrol(engine,p,profile);
  check(result.success&&result.events.contains(3437),tag+": real patrol begin events "+result.events);
  check(p.availableEvents.contains(3437),tag+": 3437 available after patrol begin");
  check(engine.startEvent(3437),tag+": engine startEvent(3437)");
  check(p.processingEvents.contains(3437),tag+": 3437 processing after startEvent");
  check(!p.availableEvents.contains(3437),tag+": 3437 moved available->processing");
  check(engine.trace("dialog",list(3437)).isEmpty(),tag+": dialog trace alone does not complete");
  check(p.processingEvents.contains(3437),tag+": 3437 still processing after dialog");
 }
 static void terminal(LocalEventEngine engine,LocalTutorialStore.Progress p,int outcome,String tag)throws Exception{
  check(engine.startEvent(outcome),tag+": start terminal event "+outcome);
  check(p.processingEvents.contains(outcome),tag+": terminal event "+outcome+" processing");
  check(engine.completeImmediateEvent(outcome),tag+": complete immediate terminal event "+outcome);
  check(p.completedEvents.contains(outcome),tag+": terminal event "+outcome+" completed");
  check(!p.availableEvents.contains(outcome)&&!p.processingEvents.contains(outcome),tag+": terminal event cleared");
  check(!p.availableEvents.contains(3455)&&!p.availableEvents.contains(3444),tag+": outcome events pruned");
  check(!p.availableEvents.contains(3437),tag+": room4 not re-offered at terminal");
  check(engine.patrolEvents(7,p.patrolHeroes,patrols).isEmpty(),tag+": no patrol replay at terminal");
 }
 static void reloadAssert(Disk disk,LocalTutorialStore.Progress p,byte[]profile,int outcome,int clues,int completions)throws Exception{
  disk.save(p);
  LocalTutorialStore.Progress reloadedProgress=disk.loadProgress();
  byte[]reloaded=disk.load(reloadedProgress);
  check(Arrays.equals(doc(profile,"q7Puzzle"),doc(reloaded,"q7Puzzle")),"Store reload q7Puzzle bytes stable");
  check(Arrays.equals(doc(profile,"std"),doc(reloaded,"std")),"Store reload std bytes stable");
  check(BsonLite.intValue(doc(reloaded,"q7Puzzle"),"outcome")==outcome,"Store reload outcome "+outcome);
  check(BsonLite.intArrayValues(doc(reloaded,"q7Puzzle"),"clues").size()==clues,"Store reload clue count");
  check(reloadedProgress.completedEvents.contains(3437),"Store reload completed 3437");
  check(reloadedProgress.eventCompletions.get(3437)==completions,"Store reload completions "+completions);
  check(reloadedProgress.processingEvents.isEmpty(),"Store reload processing empty");
  check(!reloadedProgress.availableEvents.contains(3437),"Store reload 3437 not available");
  LocalEventEngine engine=new LocalEventEngine(catalog,newbees,reloadedProgress,0,reloaded);
  check(engine.updateAreaClick("7:0"),"reload area click");
  check(engine.processingEvents().isEmpty(),"reload engine processing empty");
  check(Arrays.equals(doc(reloaded,"q7Puzzle"),doc(disk.load(reloadedProgress),"q7Puzzle")),"reload double-load stable");
  int before=reloadedProgress.eventCompletions.get(3437);
  check(engine.trace("ui",list(1)).isEmpty(),"reload terminal trace is a no-op");
  check(reloadedProgress.eventCompletions.get(3437)==before,"reload trace preserves completion count");
  check(Arrays.equals(doc(reloaded,"q7Puzzle"),doc(disk.load(reloadedProgress),"q7Puzzle")),"reload trace preserves q7Puzzle");
 }
 static void partialReload(Disk disk,LocalTutorialStore.Progress p)throws Exception{
  disk.save(p);
  LocalTutorialStore.Progress reloadedProgress=disk.loadProgress();
  byte[]reloaded=disk.load(reloadedProgress);
  check(BsonLite.intArrayValues(doc(reloaded,"q7Puzzle"),"clues").size()==4,"partial reload q7Puzzle clues=4");
  check(BsonLite.intArrayValues(doc(reloaded,"std"),"prc").size()==4,"partial reload std.prc clues=4");
  check(Boolean.TRUE.equals(BsonLite.boolValue(doc(reloaded,"q7Puzzle"),"open")),"partial reload room open");
  check(!reloadedProgress.completedEvents.contains(3437),"partial reload 3437 not completed");
 }
 static void clearAccount(String account,int uid)throws Exception{
  try(Disk disk=new Disk(account)){
   disk.write(profile(account,uid));
   LocalTutorialStore.Progress p=progress();
   byte[]current=disk.load(p);
   check(keys(doc(current,"q7Puzzle")).isEmpty(),account+": no seeded q7Puzzle");
   check(LocalCityProgress.status(p,7,current)==0,account+": area 7 state 0");
   LocalEventEngine engine=new LocalEventEngine(catalog,newbees,p,0,current);
   check(engine.updateAreaClick("7:0")&&!p.inEmergency,account+": real area entry clears emergency state");
   enterRoom(engine,p,current,account);
   current=begin(disk,p,1);
   current=collect(disk,p,current,17,21);
   check(BsonLite.intArrayValues(doc(current,"q7Puzzle"),"clues").equals(new ArrayList<>(ROOM4_CLUES)),account+": all five clues saved");
   current=exit(disk,p,3444,5);
   engine.refreshProfile(current);
   check(p.processingEvents.contains(3437)&&!p.completedEvents.contains(3437),account+": exit alone does not complete 3437");
   check(engine.trace("ui",list(1)).contains(3437),account+": ui trace completes 3437");
   check(p.completedEvents.contains(3437)&&p.processingEvents.isEmpty(),account+": 3437 completed, processing empty");
   check(p.eventCompletions.get(3437)==1,account+": completion count 1");
   check(p.availableEvents.contains(3444)&&!p.availableEvents.contains(3455),account+": clear 3444 only");
   check(!p.availableEvents.contains(3437),account+": completed room not re-offered");
   reloadAssert(disk,p,current,3444,5,1);
   // Terminal event 3444 is the immediate no-dialog outcome event; completing it closes the room for good.
   LocalTutorialStore.Progress reloadedProgress=disk.loadProgress();
   byte[]reloadedProfile=disk.load(reloadedProgress);
   LocalEventEngine reloadedEngine=new LocalEventEngine(catalog,newbees,reloadedProgress,0,reloadedProfile);
   check(reloadedEngine.updateAreaClick("7:0"),account+": terminal reload area entry");
   terminal(reloadedEngine,reloadedProgress,3444,account);
   byte[]closed=disk.load(reloadedProgress);
   disk.save(reloadedProgress);
   LocalTutorialStore.Progress freshClear=disk.loadProgress();
   check(freshClear.completedEvents.contains(3444)&&!freshClear.availableEvents.contains(3444),account+": clear terminal fresh store completed 3444");
   reloadAssert(disk,freshClear,closed,3444,5,1);
   System.out.println("CLEAR "+account+" processing=3437 exit=3444 clues=5 reload_outcome=3444 terminal=3444 completed3455="+reloadedProgress.completedEvents.contains(3455)+" available3455="+reloadedProgress.availableEvents.contains(3455));
  }
 }
 static void failAccount(String account,int uid)throws Exception{
  try(Disk disk=new Disk(account)){
   disk.write(profile(account,uid));
   LocalTutorialStore.Progress p=progress();
   byte[]current=disk.load(p);
   LocalEventEngine engine=new LocalEventEngine(catalog,newbees,p,0,current);
   check(engine.updateAreaClick("7:0")&&!p.inEmergency,account+": area entry");
   enterRoom(engine,p,current,account);
   current=begin(disk,p,1);
   current=collect(disk,p,current,17,20);
   check(!BsonLite.intArrayValues(doc(current,"q7Puzzle"),"clues").contains(21),account+": incomplete room lacks clue 21");
   partialReload(disk,p);
   current=exit(disk,p,3455,4);
   engine.refreshProfile(current);
   check(engine.trace("ui",list(1)).contains(3437),account+": fail trace completes 3437");
   check(p.completedEvents.contains(3437)&&p.processingEvents.isEmpty(),account+": 3437 completed after fail");
   check(p.availableEvents.contains(3455)&&!p.availableEvents.contains(3444),account+": fail 3455 only");
   check(!p.completedEvents.contains(3455),account+": fail outcome is not auto-completed");
   check(p.eventCompletions.get(3437)==1,account+": first completion count 1");
   reloadAssert(disk,p,current,3455,4,1);
   LocalTutorialStore.Progress replayProgress=disk.loadProgress();
   byte[]replayProfile=disk.load(replayProgress);
   LocalEventEngine replayEngine=new LocalEventEngine(catalog,newbees,replayProgress,0,replayProfile);
   check(replayEngine.updateAreaClick("7:0"),account+": replay area entry");
   check(replayEngine.patrolEvents(7,replayProgress.patrolHeroes,patrols).contains(3437),account+": repeatable room replay offered after fail");
   enterRoom(replayEngine,replayProgress,replayProfile,account+"/replay");
   byte[]replay=begin(disk,replayProgress,2);
   replay=collect(disk,replayProgress,replay,17,21);
   replay=exit(disk,replayProgress,3444,5);
   replayEngine.refreshProfile(replay);
   check(replayEngine.trace("ui",list(1)).contains(3437),account+"/replay: clear trace completes 3437");
   check(replayProgress.eventCompletions.get(3437)==2,account+"/replay: completion count 2");
   check(replayProgress.availableEvents.contains(3444),account+"/replay: clear 3444 available");
   terminal(replayEngine,replayProgress,3444,account+"/replay");
   byte[]closed=disk.load(replayProgress);
   disk.save(replayProgress);
   LocalTutorialStore.Progress freshRetry=disk.loadProgress();
   check(freshRetry.completedEvents.contains(3444)&&!freshRetry.availableEvents.contains(3444),account+"/replay: retry terminal fresh store completed 3444");
   reloadAssert(disk,freshRetry,closed,3444,5,2);
   System.out.println("FAIL "+account+" processing=3437 exit=3455 clues=4 reload_outcome=3455 replay=3437 retry_exit=3444 terminal=3444 completed3455="+replayProgress.completedEvents.contains(3455)+" available3455="+replayProgress.availableEvents.contains(3455));
  }
 }
 static void stageOnly()throws Exception{
  LocalTutorialStore.Progress p=progress();
  // v29 stage carries project7_story_city/catalog-v1.json.gz.
  String prepare="ok";
  try{StoryCityPolicy.prepare(new Context(assets,new AssetManager(assets)));}
  catch(IOException missing){prepare="missing";}
  check("ok".equals(prepare),"stage StoryCityPolicy.prepare must load the catalog");
  byte[]current=profile("stage_only",900803);
  check(StoryCityPolicy.owns(current),"stage StoryCityPolicy is prepared and owns current route");
  System.out.println("STAGE_ONLY catalog_prepare="+prepare+" owns="+StoryCityPolicy.owns(current));
  System.out.println("PASS "+checks+" stage-only checks: project7_story_city catalog is present");
 }
 public static void main(String[]args)throws Exception{
  check(args.length==3||(args.length==4&&args[3].equals("stage-only")),"usage: assets classes7.dex event_graph.tsv [stage-only]");
  assets=new File(args[0]);
  File dex=new File(args[1]),graph=new File(args[2]);
  check(sha(dex).equals(DEX_SHA),"stage classes7.dex sha256");
  check(sha(graph).equals(GRAPH_SHA),"stage event_graph.tsv sha256");
  catalog=new LocalEventCatalog(new FileInputStream(graph));
  newbees=new LocalNewbeeCatalog(new ByteArrayInputStream(new byte[0]));
  patrols=new LocalPatrolCatalog(new FileInputStream(new File(assets,"patrol.tsv")));
  checkCatalog();
  System.out.println("LEGACY rooms=4229,6228,7346 clues=1..16 catalog=accepted");
  if(args.length==4){stageOnly();return;}
  Context context=new Context(assets,new AssetManager(assets));
  CoreDrawPolicy.prepare(context);HistoryDrawPolicy.prepare(context);SelectorPolicy.prepare(context);
  StoryMissionBridge.prepare(context);StoryCityPolicy.prepare(context);
  check(StoryCityPolicy.owns(profile("owned_probe",900800)),"story-city runtime catalog owns route 27-2");
  clearAccount("host_puzzle_room4_clear",900801);
  failAccount("host_puzzle_room4_fail",900802);
  System.out.println("CAMERA server_clues=17..21 cg=0 profile_camera_keys=0");
  System.out.println("PASS "+checks+" actual v36-stage LocalEventCatalog/LocalEventEngine/LocalPuzzleEngine/LocalProfileStore checks; clear=3444 fail=3455");
 }
}
