package com.project7.localmanager;

import android.content.*;
import android.content.res.*;
import java.io.*;
import java.lang.reflect.*;
import java.nio.*;
import java.nio.file.*;
import java.util.*;

/**
 * V55 entry closure host for menus 12/19/22/25.
 *
 * <p>Uses the published v55 production classes and stage assets. Proves the
 * original Week/Gateway entry positive and persisted wrong-ending refusal, the
 * promoted chapter stage/settlement path for one representative area per menu,
 * and the city-effect path that each menu actually owns: the shared reducer for
 * 19/22, and the existing dedicated owner for 12/25. No D8, APK, native or full
 * route replay.</p>
 */
public final class StoryMainlineEntryClosureHost {
 private static final String ACCOUNT = "host_mainline_entry_closure";
 private static final String WEEK = "ecl00000000000000000000";
 private static final int[] SCOPED = {12, 19, 22, 25};
 private static final int[][] ENDINGS = {{28}, {59, 36}, {63, 1}, {24, 63}};
 // Area/scene for one representative promoted chapter per menu. Menu25 uses
 // the normal area3 route27-1 chapter; area2 route27-1 scene488 is the COC row.
 private static final int[] T1_AREA = {2, 2, 2, 2};
 private static final int[] T1_SCENE = {359, 1114, 1120, 488};
 private static final int[] T1_NEXT = {-1, 1115, 1115, 488};
 // Original mission formation: 359 is customizeHero with hero36/max1; the others accept a normal trio.
 private static final int[][] T1_HEROES = {{36}, {135, 136}, {135, 136}, {135}};
 // Original economy gate battle traces required by the selected stage.
 private static final int[][] T1_GATE_BATTLES = {{}, {2118}, {}, {}};
 // Menu25 scene488 is the promoted COC area2 row; its COC chain predecessor
 // 10003 is seeded FREE (synthetic prerequisite, not a natural arrival claim).
 private static final int[][] T1_PREDECESSORS = {{}, {}, {}, {10003}};
 private static final int[] COC_COMPLETION = {0, 0, 0, 1441};
 private static int checks;
 private static File assets;
 private static LocalEventCatalog events;
 private static LocalNewbeeCatalog newbees;
 private static LocalCombatCatalog combat;
 private static LocalWeekCatalog weeks;
 private static boolean prepared;
 private static Method RAW_RELIABLE;
 private static Method RAW_FINISH;
 private static final java.util.concurrent.atomic.AtomicInteger SEQ =
     new java.util.concurrent.atomic.AtomicInteger(1);

 private static void check(boolean value, String why) {
  checks++;
  if (!value) throw new AssertionError("FAIL: " + why);
 }

 private static byte[] doc(byte[] profile, String key) {
  byte[] value = BsonLite.documentValue(profile, key);
  return value == null ? BsonLite.EMPTY_DOCUMENT : value;
 }

 private static byte[] md5(String value) throws Exception {
  return java.security.MessageDigest.getInstance("MD5")
      .digest(value.getBytes(java.nio.charset.StandardCharsets.UTF_8));
 }

 private static List<ProtoLite.EntityMessage> frames(byte[] wire) throws IOException {
  List<ProtoLite.EntityMessage> out = new ArrayList<>();
  ByteBuffer buffer = ByteBuffer.wrap(wire).order(ByteOrder.LITTLE_ENDIAN);
  while (buffer.hasRemaining()) {
   int length = buffer.getInt();
   check(buffer.getShort() == 5, "opcode5 frame");
   byte[] data = new byte[length - 2];
   buffer.get(data);
   out.add(ProtoLite.parseEntityMessage(data));
  }
  return out;
 }

 private static ProtoLite.EntityMessage frame(List<ProtoLite.EntityMessage> frames, String method)
     throws Exception {
  byte[] digest = md5(method);
  for (ProtoLite.EntityMessage frame : frames)
   if (Arrays.equals(frame.methodMd5, digest)) return frame;
  return null;
 }

 private static byte[] entryProfile(int menu, List<Integer> endings) throws IOException {
  byte[] profile = BsonLite.withAccountIdentity(
      Files.readAllBytes(new File(assets, "new_player.bson").toPath()), ACCOUNT, 901300 + menu);
  profile = BsonLite.withProfileDocument(profile, "weeknum",
      BsonLite.document("w", 8, "d", 0, "av", 60));
  profile = BsonLite.withProfileDocument(profile, "std",
      BsonLite.document("rt", "1", "ed", endings));
  profile = BsonLite.withProfileInt(profile, "q7ChapterMenu", 1);
  profile = BsonLite.withProfileArray(profile, "q7WeekEventBaseline", Collections.emptyList());
  profile = BsonLite.withProfileDocument(profile, "city", BsonLite.document("av", 60));
  byte[] inventory = doc(profile, "inv");
  inventory = BsonLite.withProfileArray(inventory, "items",
      Arrays.asList(BsonLite.document("i", 345, "w", 1, "u", "0123456789abcdef01234567")));
  profile = BsonLite.withProfileDocument(profile, "inv", inventory);
  for (int hero : new int[]{36, 114, 135, 136, 137}) profile = BsonLite.withHero(profile, hero);
  return profile;
 }

 private static LocalTutorialStore.Progress progress() {
  LocalTutorialStore.Progress progress = LocalTutorialStore.Progress.completed();
  progress.weekIndex = 8;
  progress.weekCommit = WEEK;
  progress.inEmergency = false;
  progress.initPrologue = false;
  progress.patrolActions = 60;
  progress.processingEvents.clear();
  progress.processingNewbees.clear();
  return progress;
 }

 private static final class Fixture implements AutoCloseable {
  final Path root, profileFile;
  final LocalProfileStore store;
  final LocalTutorialStore tutorials;
  final LocalTutorialStore.Progress progress;
  final LocalEventEngine engine;
  final LocalGatewayServer gateway;

  Fixture(int menu, List<Integer> endings) throws Exception {
   root = Files.createTempDirectory("mainline-entry-closure-");
   Files.createDirectories(root.resolve("profiles"));
   profileFile = root.resolve("profiles/" + ACCOUNT + ".bson");
   Files.write(profileFile, entryProfile(menu, endings));
   Context context = new Context(root.toFile(), new AssetManager(assets));
   store = new LocalProfileStore(context);
   tutorials = new LocalTutorialStore(context);
   progress = progress();
   tutorials.save(ACCOUNT, progress);
   engine = new LocalEventEngine(events, newbees, progress, 0, profile(), true);
   gateway = new LocalGatewayServer(0, null, store, tutorials, events, newbees, combat, null,
       (status, message) -> { });
  }

  List<ProtoLite.EntityMessage> call(String method, byte[] parameters, int sequence) throws Exception {
   return call(engine, method, parameters, sequence);
  }

  List<ProtoLite.EntityMessage> call(LocalEventEngine eng, String method, byte[] parameters,
                                     int sequence) throws Exception {
   ByteArrayOutputStream out = new ByteArrayOutputStream();
   byte[] wrapper = BsonLite.document("m", method, "p", parameters, "r", sequence);
   byte[] envelope = BsonLite.document("w", wrapper, "_cbid_", sequence + 10000);
   RAW_RELIABLE.invoke(gateway, out, new byte[12], envelope, ACCOUNT, progress, eng,
       new LinkedHashSet<Integer>(), new HashSet<Integer>(),
       new HashMap<Integer, LocalPatrolEngine.Result>(), new HashSet<Integer>());
   return frames(out.toByteArray());
  }

  List<ProtoLite.EntityMessage> finish(LocalEventEngine eng, byte[] parameters) throws Exception {
   ByteArrayOutputStream out = new ByteArrayOutputStream();
   RAW_FINISH.invoke(gateway, out, new byte[12], parameters, ACCOUNT, progress, eng,
       new HashSet<Integer>(), new HashSet<Integer>());
   return frames(out.toByteArray());
  }

  int stageCs(LocalEventEngine eng, int area) throws Exception {
   List<ProtoLite.EntityMessage> reply = call(eng, "getAreaStagesRequest",
       BsonLite.document("aid", area), SEQ.getAndIncrement());
   ProtoLite.EntityMessage stages = frame(reply, "get_area_stages_reply");
   if (stages == null) return -1;
   byte[] st = BsonLite.documentValue(stages.parameters, "st");
   Integer cs = st == null ? null : BsonLite.intValue(st, "cs");
   return cs == null ? -1 : cs.intValue();
  }

  void chapterBattleT1(LocalEventEngine eng, int area, int scene, int[] heroes) throws Exception {
   int menuForScene = menuFor(scene);
   List<Integer> party = new ArrayList<>();
   for (int hero : heroes) party.add(hero);
   List<ProtoLite.EntityMessage> admitted = call(eng, "combatOfflineRequest",
       BsonLite.document("t", 1, "s", scene, "d", BsonLite.document("a", area),
           "h", party), SEQ.getAndIncrement());
   ProtoLite.EntityMessage reply = frame(admitted, "combatOfflineReply");
   if (reply == null || !Integer.valueOf(1).equals(BsonLite.intValue(reply.parameters, "t")))
    for (ProtoLite.EntityMessage message : admitted)
     System.out.println("chapter t1 admit " + scene + " frame "
         + BsonLite.messagePackValue(message.parameters, false));
   check(reply != null && Integer.valueOf(1).equals(BsonLite.intValue(reply.parameters, "t")) &&
       Integer.valueOf(scene).equals(BsonLite.intValue(reply.parameters, "s")) &&
       BsonLite.stringValue(reply.parameters, "f") != null &&
       !BsonLite.stringValue(reply.parameters, "f").isEmpty(),
       "chapter t1 admission " + scene);
   List<ProtoLite.EntityMessage> won = finish(eng,
       BsonLite.document("t", 1, "s", scene, "h", party,
           "x", Collections.emptyList(), "w", 1));
   check(frame(won, "combatOfflineReward") != null, "chapter t1 reward " + scene);
   int completion = COC_COMPLETION[Arrays.binarySearch(SCOPED, menuForScene)];
   if (completion != 0) {
    // The COC server-pending event is admitted by the original Store settlement;
    // the existing COC host owns the separate dialog/completion trace claim.
    check(progress.completedEvents.contains(completion) ||
        progress.processingEvents.contains(completion),
        "COC pending completion " + completion);
   }
   else check(progress.eventConditions.get("battle") != null &&
       progress.eventConditions.get("battle").contains(scene),
       "chapter t1 battle trace " + scene);
  }

  byte[] profile() throws IOException {
   return Files.readAllBytes(profileFile);
  }

  void persist(byte[] profile) throws IOException {
   Files.write(profileFile, profile);
  }

  LocalTutorialStore.Progress reload() throws Exception {
   return tutorials.load(ACCOUNT);
  }

  void entry(int menu) throws Exception {
   call("getAreaStagesRequest", BsonLite.document("aid", 2), SEQ.getAndIncrement());
   byte[] pending = doc(profile(), "q7StoryPending");
   if (!BsonLite.keys(pending).isEmpty()) {
    LocalResourceEngine.Result ack = store.updateServices(ACCOUNT, "q7AckStoryDelivery",
        BsonLite.document("s", pending), progress);
    check(BsonLite.keys(doc(ack.profile, "q7StoryPending")).isEmpty(),
        "original ack consumed prior delivery menu" + menu);
   }
   List<ProtoLite.EntityMessage> reply = call("requestEnterStory",
       BsonLite.document("i", menu), SEQ.getAndIncrement());
   ProtoLite.EntityMessage accepted = frame(reply, "replyEnterStory");
   check(accepted != null && Boolean.TRUE.equals(BsonLite.boolValue(accepted.parameters, "r")),
       "original requestEnterStory accepted menu" + menu);
   check(Integer.valueOf(menu).equals(BsonLite.intValue(profile(), "q7ChapterMenu")),
       "entry committed q7ChapterMenu " + menu);
   check(progress.weekCommit != null && !progress.weekCommit.equals(WEEK) &&
       progress.weekCommit.equals(reload().weekCommit),
       "entry committed and persisted a new week cycle " + menu);
  }

  void deniedEntry(int menu) throws Exception {
   call("getAreaStagesRequest", BsonLite.document("aid", 2), SEQ.getAndIncrement());
   byte[] pending = doc(profile(), "q7StoryPending");
   if (!BsonLite.keys(pending).isEmpty()) {
    LocalResourceEngine.Result ack = store.updateServices(ACCOUNT, "q7AckStoryDelivery",
        BsonLite.document("s", pending), progress);
    check(BsonLite.keys(doc(ack.profile, "q7StoryPending")).isEmpty(),
        "denied prelude ack menu" + menu);
   }
   byte[] before = profile();
   String weekBefore = progress.weekCommit;
   int weekIndexBefore = progress.weekIndex;
   Integer menuBefore = BsonLite.intValue(before, "q7ChapterMenu");
   byte[] stdBefore = doc(before, "std");
   List<ProtoLite.EntityMessage> reply = call("requestEnterStory",
       BsonLite.document("i", menu), SEQ.getAndIncrement());
   ProtoLite.EntityMessage refused = frame(reply, "replyEnterStory");
   check(refused != null && Boolean.FALSE.equals(BsonLite.boolValue(refused.parameters, "r")),
       "original gateway refuses unmet endings menu" + menu);
   byte[] after = profile();
   check(Objects.equals(menuBefore, BsonLite.intValue(after, "q7ChapterMenu")),
       "refused entry leaves q7ChapterMenu unchanged menu" + menu);
   check(Arrays.equals(stdBefore, doc(after, "std")),
       "refused entry leaves route/endings unchanged menu" + menu);
   check(Objects.equals(weekBefore, progress.weekCommit) && weekIndexBefore == progress.weekIndex,
       "refused entry leaves week progress unchanged menu" + menu);
   List<ProtoLite.EntityMessage> again = call("requestEnterStory",
       BsonLite.document("i", menu), SEQ.getAndIncrement());
   ProtoLite.EntityMessage refusedAgain = frame(again, "replyEnterStory");
   check(refusedAgain != null &&
       Boolean.FALSE.equals(BsonLite.boolValue(refusedAgain.parameters, "r")),
       "original gateway refuses unmet endings again menu" + menu);
   check(Arrays.equals(after, profile()), "repeated refusal leaves profile bytes unchanged menu" + menu);
  }

  void startAndTrace(int event) throws Exception {
   List<ProtoLite.EntityMessage> start = call("startEvent",
       BsonLite.document("e", event), SEQ.getAndIncrement());
   ProtoLite.EntityMessage reply = frame(start, "startEventReply");
   check(reply != null && Integer.valueOf(event).equals(BsonLite.intValue(reply.parameters, "e")) &&
       Integer.valueOf(1).equals(BsonLite.intValue(reply.parameters, "r")),
       "start accepted " + event);
   List<ProtoLite.EntityMessage> trace = call("clientTraceProcessingEvent",
       BsonLite.document("k", "dialog", "d", BsonLite.document("c", event)), SEQ.getAndIncrement());
   ProtoLite.EntityMessage done = frame(trace, "completeEventReplyEnd");
   check(done != null && Integer.valueOf(event).equals(BsonLite.intValue(done.parameters, "e")),
       "dialog completion " + event);
  }

  public void close() throws Exception {
   gateway.close();
   try (java.util.stream.Stream<Path> stream = Files.walk(root)) {
    for (Path path : (Iterable<Path>) stream.sorted(Comparator.reverseOrder())::iterator)
     Files.delete(path);
   }
  }
 }

 private static int state(byte[] profile, int area) {
  Integer value = BsonLite.intValue(doc(profile, "q7ChapterStates"), Integer.toString(area));
  return value == null ? -1 : value;
 }

 private static boolean receipt(byte[] profile, int event) {
  return Boolean.TRUE.equals(BsonLite.boolValue(doc(profile, "q7ChapterEffects"),
      Integer.toString(event)));
 }

 private static byte[] reduce(Fixture fixture, int event) {
  try {
   LocalResourceEngine.Result result = new LocalResourceEngine.Result(fixture.profile());
   fixture.progress.completedEvents.add(event);
   StoryCityPolicy.refresh(result, events, fixture.progress);
   fixture.progress.completedEvents.remove(event);
   return result.profile;
  } catch (IOException error) {
   throw new AssertionError(error);
  }
 }

 private static void prepare(String entryRoot) throws Exception {
  if (prepared) return;
  Context context = new Context(assets, new AssetManager(assets));
  CoreDrawPolicy.prepare(context);
  HistoryDrawPolicy.prepare(context);
  SelectorPolicy.prepare(context);
  OfflineMechanismGateway.prepare(context);
  RequestEventGateway.prepare(context);
  StoryMissionBridge.prepare(context);
  StoryMissionBridge.prepareSpecial(context);
  StoryMenuShared.prepare(context);
  StoryMenuEntryData.prepare(context);
  StoryCityPolicy.prepare(context);
  StoryCityCocPolicy.prepare(context);
  StoryMainlineEntry.prepare(new File(entryRoot));
  weeks = new LocalWeekCatalog(new FileInputStream(new File(assets, "weeks.tsv")));
  events = new LocalEventCatalog(new FileInputStream(new File(assets, "event_graph.tsv")));
  newbees = new LocalNewbeeCatalog(new ByteArrayInputStream(new byte[0]));
  combat = new LocalCombatCatalog(context);
  try {
   RAW_RELIABLE = LocalGatewayServer.class.getDeclaredMethod("handleReliableRpc",
       OutputStream.class, byte[].class, byte[].class, String.class,
       LocalTutorialStore.Progress.class, LocalEventEngine.class, Set.class, Set.class,
       Map.class, Set.class);
   RAW_RELIABLE.setAccessible(true);
   RAW_FINISH = LocalGatewayServer.class.getDeclaredMethod("handleCombatOfflineFinish",
       OutputStream.class, byte[].class, byte[].class, String.class,
       LocalTutorialStore.Progress.class, LocalEventEngine.class, Set.class, Set.class);
   RAW_FINISH.setAccessible(true);
  } catch (ReflectiveOperationException error) {
   throw new AssertionError("Gateway reliable ABI", error);
  }
  prepared = true;
 }

 private static List<Integer> endings(int menu) {
  List<Integer> out = new ArrayList<>();
  for (int ending : ENDINGS[Arrays.binarySearch(SCOPED, menu)]) out.add(ending);
  return out;
 }

 private static void checkChapterT1(int menu, int area, int scene, int next) throws Exception {
  try (Fixture fixture = new Fixture(menu, endings(menu))) {
   fixture.entry(menu);
   byte[] profile = fixture.profile();
   String route = StoryMainlineEntry.route(menu);
   List<Integer> permanent = BsonLite.intArrayValues(doc(profile, "std"), "ed");
   profile = BsonLite.withProfileDocument(profile, "std",
       BsonLite.document("rt", route, "ed", permanent));
   fixture.persist(profile);
   fixture.progress.completedEvents.addAll(Arrays.asList(1013, 1043));
   Set<Integer> battleTraces = fixture.progress.eventConditions.computeIfAbsent(
       "battle", key -> new HashSet<Integer>());
   for (int gate : T1_GATE_BATTLES[Arrays.binarySearch(SCOPED, menu)]) battleTraces.add(gate);
   byte[] states = doc(profile, "q7ChapterStates");
   for (int predecessor : T1_PREDECESSORS[Arrays.binarySearch(SCOPED, menu)])
    states = BsonLite.withProfileInt(states, Integer.toString(predecessor), 0);
   profile = BsonLite.withProfileDocument(profile, "q7ChapterStates", states);
   fixture.persist(profile);
   LocalEventEngine chapterEngine =
       new LocalEventEngine(events, newbees, fixture.progress, 0, profile, true);
   byte[] stage = StoryCityPolicy.stages(fixture.progress, area, profile);
   check(Integer.valueOf(scene).equals(BsonLite.intValue(stage, "cs")),
       "menu" + menu + " promoted area" + area + " cs" + scene);
   check(fixture.stageCs(chapterEngine, area) == scene,
       "menu" + menu + " gateway getAreaStages cs" + scene);
   fixture.chapterBattleT1(chapterEngine, area, scene,
       T1_HEROES[Arrays.binarySearch(SCOPED, menu)]);
   byte[] settled = fixture.profile();
   LocalEventEngine settledEngine =
       new LocalEventEngine(events, newbees, fixture.progress, 0, settled, true);
   int advanced = fixture.stageCs(settledEngine, area);
   System.out.println("t1 menu" + menu + " route=" + route + " advanced=" + advanced
       + " state=" + state(settled, area));
   check(advanced == next, "menu" + menu + " area" + area + " advances to " + next + " (got " + advanced + ")");
   LocalTutorialStore.Progress loaded = fixture.reload();
   int completion = COC_COMPLETION[Arrays.binarySearch(SCOPED, menu)];
   if (completion != 0) check(loaded.processingEvents.contains(completion) ||
       loaded.completedEvents.contains(completion), "menu" + menu + " COC pending persists");
   else check(loaded.eventConditions.get("battle") != null &&
       loaded.eventConditions.get("battle").contains(scene),
       "menu" + menu + " chapter t1 battle persists");
  }
 }

 private static int menuFor(int scene) {
  for (int i = 0; i < T1_SCENE.length; i++) if (T1_SCENE[i] == scene) return SCOPED[i];
  return 0;
 }

 public static void main(String[] args) throws Exception {
  assets = new File(args[0]);
  prepare(args[1]);
  for (int menu : SCOPED) {
   check(StoryMainlineEntry.capability(menu), "capability menu" + menu);
   check(StoryCityPolicy.supports(menu), "supports menu" + menu);
   try (Fixture fixture = new Fixture(menu, endings(menu))) {
    byte[] before = fixture.profile();
    check(LocalWeekEngine.canEnter(before, weeks, menu), "canEnter menu" + menu);
    check(StoryMainlineEntry.entryReady(menu, before, fixture.progress, weeks),
        "entryReady pre-entry menu" + menu);
    byte[] wrong = BsonLite.withProfileDocument(before, "std",
        BsonLite.document("rt", "1", "ed", Collections.singletonList(999999)));
    check(!LocalWeekEngine.canEnter(wrong, weeks, menu), "canEnter negative menu" + menu);
    check(!StoryMainlineEntry.entryReady(menu, wrong, fixture.progress, weeks),
        "entryReady negative menu" + menu);
    try (Fixture denied = new Fixture(menu, Collections.singletonList(999999))) {
     denied.deniedEntry(menu);
    }
    fixture.entry(menu);
    byte[] profile = fixture.profile();
    check(StoryMainlineEntry.entryReady(menu, profile, fixture.progress, weeks),
        "entryReady post-entry menu" + menu);
    boolean dedicated = menu == 12 || menu == 25;
    check(dedicated != StoryMainlineEntry.cityOwns(profile),
        "city reducer ownership menu" + menu);
    if (menu == 25) check(StoryCityPolicy.owns(profile), "story city owner menu25");
    if (menu == 12) check(!StoryCityPolicy.owns(profile), "dedicated city owner menu12");
    check(fixture.reload().weekCommit.equals(fixture.progress.weekCommit),
        "reload keeps week menu" + menu);
   }
  }

  // Real promoted chapter t1 per entry menu.
  checkChapterT1(12, T1_AREA[0], T1_SCENE[0], T1_NEXT[0]);
  checkChapterT1(19, T1_AREA[1], T1_SCENE[1], T1_NEXT[1]);
  checkChapterT1(22, T1_AREA[2], T1_SCENE[2], T1_NEXT[2]);
  checkChapterT1(25, T1_AREA[3], T1_SCENE[3], T1_NEXT[3]);

  // Shared reducer on 19/22 (real effect event, receipt, state, reload).
  for (int[] pair : new int[][]{{19, 1256}, {22, 1357}}) {
   int menu = pair[0], event = pair[1];
   try (Fixture fixture = new Fixture(menu, endings(menu))) {
    fixture.entry(menu);
    byte[] profile = reduce(fixture, event);
    fixture.persist(profile);
    check(receipt(profile, event), "menu" + menu + " receipt " + event);
    if (event == 1256) check(state(profile, 5) == 0, "menu19 areaFree[5]");
    if (event == 1357) check(state(profile, 2) == 1, "menu22 areaFight[2]");
    byte[] reloaded = fixture.profile();
    check(receipt(reloaded, event), "menu" + menu + " receipt persists " + event);
   }
  }

  // Menu25 existing StoryCity catalog effects (event 1424 route27-1).
  try (Fixture fixture = new Fixture(25, Arrays.asList(24, 63))) {
   fixture.entry(25);
   byte[] profile = reduce(fixture, 1424);
   fixture.persist(profile);
   check(receipt(profile, 1424), "menu25 receipt 1424");
   check(state(profile, 7) == 0, "menu25 areaFree[7]");
   check(Boolean.TRUE.equals(BsonLite.boolValue(doc(profile, "q7ChapterLocks"), "1")),
       "menu25 areaLock[1]");
  }

  // Menu12 dedicated Dalvira state, not the shared reducer.
  try (Fixture fixture = new Fixture(12, Collections.singletonList(28))) {
   fixture.entry(12);
   byte[] profile = fixture.profile();
   profile = BsonLite.withProfileDocument(profile, "std",
       BsonLite.document("rt", "13-3", "ed", Collections.singletonList(28)));
   fixture.persist(profile);
   check(!StoryMainlineEntry.cityOwns(profile) && !StoryCityPolicy.owns(profile),
       "menu12 dedicated only");
   check(StoryCityPolicy.status(fixture.progress, 2, profile) >= 0,
       "menu12 dedicated area2 status");
  }
  System.out.println("PASS " + checks);
 }
}
