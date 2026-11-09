package com.project7.localmanager;

import android.content.*;
import android.content.res.*;
import java.io.*;
import java.lang.reflect.*;
import java.nio.*;
import java.nio.file.*;
import java.util.*;

/**
 * Published host for the shared default-chapter admission path.
 *
 * <p>Runs the published v54 gateway/event engine with the packaged entry asset
 * (menus 7/8/14/15/16/18/21/26 as {@code default_chapter} rows). For every menu
 * it drives requestEnterStory -> original default area stage -> one real battle
 * settlement -> the menu's dialog chain -> completed-event area effects ->
 * save/reload, plus the original new-profile tutorial chain that produces 1004.
 * Menu8/21 route-only effects use the real original triggers: 30015/40012/30045/
 * 40042 through route 9-3, and 1347/1345->1346 through the original clientOp and
 * outcome consumers. The 4/23 8753 case is the accepted mid-chain fixture, not a
 * full route.</p>
 */
public final class StoryDefaultChapterHost {
 private static final String ACCOUNT = "host_default_chapter";
 private static final String WEEK = "dch00000000000000000000";
 private static final int[] MENUS = {7, 8, 14, 15, 16, 18, 21, 26};
 private static final int[][] ROUTE_ONLY_EFFECTS = {
     {},
     {30045, 40042},
     {1184, 2161},
     {5216, 5219},
     {},
     {},
     {1346, 1347},
     {1621, 1637},
 };
 private static final int[][] CHAINS = {
     {508, 509, 510},
     {498, 499, 500, 501, 503, 504, 505, 506, 507, 1108},
     {453, 454, 455, 1169, 1170, 1171},
     {446, 447, 448, 449, 450, 451, 1193},
     {439, 440, 441, 442, 443, 444, 445, 1225, 1226},
     {433, 434, 435, 1240},
     {429, 430, 431, 432, 1339, 1340, 1341},
     {1454, 1634},
 };
 private static final int[] ENDINGS = {2, 6, 7, 19, 20, 21, 22, 23, 42, 43, 47, 48, 49, 54, 99, 100};
 // Original EVENT_DIALOGUE rows: 5215/5218/1620 each carry finish_event
 // 5216/5219/1621 and no optN_event, so real_end passes index+1 = 1.
 private static final int[][] ORIGINAL_OPTIONS = {
     {5215, 5216, 1},
     {5218, 5219, 1},
     {1620, 1621, 1},
 };
 private static final String[] ORIGINAL_OPTION_ROUTES = {"16-5", "16-6", "29-1"};
 private static int checks;
 private static File assets;
 private static LocalEventCatalog events;
 private static LocalWeekCatalog weeks;
 private static LocalNewbeeCatalog newbees;
 private static LocalCombatCatalog combat;
 private static Method RAW_RELIABLE, OFFLINE_FINISH, HIGH_SCHOOL, RESET_PROGRESS;
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

 private static boolean accepted(List<ProtoLite.EntityMessage> frames, String method)
     throws Exception {
  ProtoLite.EntityMessage reply = frame(frames, method);
  return reply != null && Boolean.TRUE.equals(BsonLite.boolValue(reply.parameters, "r"));
 }

 private static final class Fixture implements AutoCloseable {
  final Path root, profileFile;
  final LocalProfileStore store;
  final LocalTutorialStore tutorials;
  final LocalTutorialStore.Progress progress;
  final LocalEventEngine engine;
  final LocalGatewayServer gateway;
  final Set<Integer> reliableSequences = new LinkedHashSet<>();

  Fixture(List<Integer> endings, int seed, boolean seedTutorial) throws Exception {
   root = Files.createTempDirectory("default-chapter-");
   Files.createDirectories(root.resolve("profiles"));
   profileFile = root.resolve("profiles/" + ACCOUNT + ".bson");
   byte[] profile = BsonLite.withAccountIdentity(
       Files.readAllBytes(new File(assets, "new_player.bson").toPath()), ACCOUNT, 903000 + seed);
   profile = BsonLite.withProfileDocument(profile, "weeknum",
       BsonLite.document("w", 8, "d", 0, "av", 60));
   profile = BsonLite.withProfileDocument(profile, "std",
       BsonLite.document("rt", "1", "ed", endings, "ff", false));
   profile = BsonLite.withProfileInt(profile, "q7ChapterMenu", 1);
   profile = BsonLite.withProfileDocument(profile, "city", BsonLite.document("av", 60));
   byte[] inventory = doc(profile, "inv");
   inventory = BsonLite.withProfileArray(inventory, "items",
       Arrays.asList(BsonLite.document("i", 345, "w", 1, "u", "0123456789abcdef01234567")));
   profile = BsonLite.withProfileDocument(profile, "inv", inventory);
   for (int hero : new int[]{135, 136, 137}) profile = BsonLite.withHero(profile, hero);
   Files.write(profileFile, profile);
   Context context = new Context(root.toFile(), new AssetManager(assets));
   store = new LocalProfileStore(context);
   tutorials = new LocalTutorialStore(context);
   progress = LocalTutorialStore.Progress.completed();
   progress.weekIndex = 8;
   progress.weekCommit = WEEK;
   progress.inEmergency = false;
   progress.initPrologue = false;
   progress.patrolActions = 60;
   progress.processingEvents.clear();
   progress.processingNewbees.clear();
   if (seedTutorial) progress.completedEvents.add(1004);
   engine = new LocalEventEngine(events, newbees, progress, 0, profile, true);
   gateway = new LocalGatewayServer(0, null, store, tutorials, events, newbees, combat, null,
       (status, message) -> { });
  }

  Fixture(byte[] midProfile, LocalTutorialStore.Progress midProgress) throws Exception {
   root = Files.createTempDirectory("default-chapter-mid-");
   Files.createDirectories(root.resolve("profiles"));
   profileFile = root.resolve("profiles/" + ACCOUNT + ".bson");
   Files.write(profileFile, midProfile);
   Context context = new Context(root.toFile(), new AssetManager(assets));
   store = new LocalProfileStore(context);
   tutorials = new LocalTutorialStore(context);
   progress = midProgress;
   engine = new LocalEventEngine(events, newbees, progress, 0, midProfile, true);
   gateway = new LocalGatewayServer(0, null, store, tutorials, events, newbees, combat, null,
       (status, message) -> { });
  }

  List<ProtoLite.EntityMessage> call(String method, byte[] parameters, int sequence)
      throws Exception {
   ByteArrayOutputStream out = new ByteArrayOutputStream();
   byte[] wrapper = BsonLite.document("m", method, "p", parameters, "r", sequence);
   byte[] envelope = BsonLite.document("w", wrapper, "_cbid_", sequence + 10000);
   try {
    RAW_RELIABLE.invoke(gateway, out, new byte[12], envelope, ACCOUNT, progress, engine,
        reliableSequences, new HashSet<Integer>(),
        new HashMap<Integer, LocalPatrolEngine.Result>(), new HashSet<Integer>());
   } catch (InvocationTargetException error) {
    if (error.getCause() instanceof Exception) throw (Exception) error.getCause();
    throw error;
   }
   return frames(out.toByteArray());
  }

  List<ProtoLite.EntityMessage> callRaw(String method, byte[] parameters, int sequence)
      throws Exception {
   ByteArrayOutputStream out = new ByteArrayOutputStream();
   byte[] wrapper = BsonLite.document("m", method, "p", parameters, "r", sequence);
   byte[] envelope = BsonLite.document("w", wrapper, "_cbid_", sequence + 10000);
   RAW_RELIABLE.invoke(gateway, out, new byte[12], envelope, ACCOUNT, progress, engine,
       reliableSequences, new HashSet<Integer>(),
       new HashMap<Integer, LocalPatrolEngine.Result>(), new HashSet<Integer>());
   return frames(out.toByteArray());
  }

  byte[] finish(int scene, int win) {
   return BsonLite.document("t", 1, "s", scene, "h", Arrays.asList(135), "w", win,
       "x", Collections.emptyList());
  }

  byte[] offlineFinishDoc(byte[] finish) throws Exception {
   ByteArrayOutputStream out = new ByteArrayOutputStream();
   try {
    OFFLINE_FINISH.invoke(gateway, out, new byte[12], finish, ACCOUNT, progress,
        engine, new HashSet<Integer>(), new HashSet<Integer>());
   } catch (InvocationTargetException error) {
    if (error.getCause() instanceof Exception) throw (Exception) error.getCause();
    throw error;
   }
   return out.toByteArray();
  }

  byte[] offlineFinish(int scene, int win) throws Exception {
   return offlineFinishDoc(finish(scene, win));
  }

  List<ProtoLite.EntityMessage> framesOf(byte[] wire) throws IOException {
   return frames(wire);
  }

  byte[] profile() throws IOException {
   return Files.readAllBytes(profileFile);
  }

  LocalTutorialStore.Progress reload() throws Exception {
   return tutorials.load(ACCOUNT);
  }

  public void close() throws Exception {
   gateway.close();
   try (java.util.stream.Stream<Path> path = Files.walk(root)) {
    for (Path each : (Iterable<Path>) path.sorted(Comparator.reverseOrder())::iterator)
     Files.delete(each);
   }
  }
 }

 private static void clearPending(Fixture fixture) throws Exception {
  fixture.call("getAreaStagesRequest", BsonLite.document("aid", 1), SEQ.getAndIncrement());
  byte[] pending = doc(fixture.profile(), "q7StoryPending");
  if (!BsonLite.keys(pending).isEmpty()) {
   LocalResourceEngine.Result ack = fixture.store.updateServices(ACCOUNT, "q7AckStoryDelivery",
       BsonLite.document("s", pending), fixture.progress);
   check(BsonLite.keys(doc(ack.profile, "q7StoryPending")).isEmpty(),
       "prior delivery acknowledged");
  }
 }

 private static void prepare(String entryRoot) throws Exception {
  Context context = new Context(assets, new AssetManager(assets));
  CoreDrawPolicy.prepare(context);
  HistoryDrawPolicy.prepare(context);
  SelectorPolicy.prepare(context);
  OfflineMechanismGateway.prepare(context);
  StoryMissionBridge.prepare(context);
  StoryMissionBridge.prepareSpecial(context);
  StoryMenuShared.prepare(context);
  StoryMenuEntryData.prepare(context);
  StoryCityPolicy.prepare(context);
  RequestEventGateway.prepare(context);
  StoryMainlineEntry.prepare(new File(entryRoot));
  weeks = new LocalWeekCatalog(new FileInputStream(new File(assets, "weeks.tsv")));
  events = new LocalEventCatalog(new FileInputStream(new File(assets, "event_graph.tsv")));
  newbees = new LocalNewbeeCatalog(new ByteArrayInputStream(new byte[0]));
  combat = new LocalCombatCatalog(context);
  RAW_RELIABLE = LocalGatewayServer.class.getDeclaredMethod("handleReliableRpc",
      OutputStream.class, byte[].class, byte[].class, String.class,
      LocalTutorialStore.Progress.class, LocalEventEngine.class, Set.class, Set.class,
      Map.class, Set.class);
  RAW_RELIABLE.setAccessible(true);
  OFFLINE_FINISH = LocalGatewayServer.class.getDeclaredMethod("handleCombatOfflineFinish",
      OutputStream.class, byte[].class, byte[].class, String.class,
      LocalTutorialStore.Progress.class, LocalEventEngine.class, Set.class, Set.class);
  OFFLINE_FINISH.setAccessible(true);
  HIGH_SCHOOL = LocalGatewayServer.class.getDeclaredMethod("isHighSchoolUnlocked",
      LocalTutorialStore.Progress.class);
  HIGH_SCHOOL.setAccessible(true);
  RESET_PROGRESS = LocalWeekEngine.class.getDeclaredMethod("resetProgress",
      LocalTutorialStore.Progress.class, LocalWeekCatalog.class, int.class, int.class);
  RESET_PROGRESS.setAccessible(true);
 }

 private static boolean highSchool(LocalTutorialStore.Progress progress) throws Exception {
  return (Boolean) HIGH_SCHOOL.invoke(null, progress);
 }

 private static int state(byte[] profile, int area) {
  Integer value = BsonLite.intValue(doc(profile, "q7ChapterStates"), Integer.toString(area));
  return value == null ? -1 : value;
 }

 private static boolean locked(byte[] profile, int area) {
  return Boolean.TRUE.equals(BsonLite.boolValue(doc(profile, "q7ChapterLocks"),
      Integer.toString(area)));
 }

 private static boolean receipt(byte[] profile, int event) {
  return Boolean.TRUE.equals(BsonLite.boolValue(doc(profile, "q7ChapterEffects"),
      Integer.toString(event)));
 }

 private static void applyEffects(byte[] profile, int event) {
  byte[] effect = events.cityEffects.get(event);
  if (effect == null) return;
  for (String field : new String[]{"areaFree", "areaFight", "areaLock", "areaUnlock"}) {
   byte[] areas = BsonLite.arrayValue(effect, field);
   if (areas == null) continue;
   for (String key : BsonLite.keys(areas)) {
    Number value = BsonLite.numericValue(areas, key);
    int area = value.intValue();
    if (field.equals("areaFree")) check(state(profile, area) == 0, event + " areaFree " + area);
    if (field.equals("areaFight")) check(state(profile, area) == 1, event + " areaFight " + area);
    if (field.equals("areaLock")) check(locked(profile, area), event + " areaLock " + area);
    if (field.equals("areaUnlock")) check(!locked(profile, area), event + " areaUnlock " + area);
   }
  }
 }

 private static void complete(Fixture fixture, int event) throws Exception {
  int sequence = SEQ.getAndIncrement();
  List<ProtoLite.EntityMessage> started = fixture.call("startEvent",
      BsonLite.document("e", event), sequence);
  check(frame(started, "startEventReply") != null, "start reply " + event);
  check(fixture.progress.processingEvents.contains(event), "processing " + event);
  LocalEventCatalog.Event row = events.get(event);
  List<ProtoLite.EntityMessage> done;
  if (row != null && row.dialog > 0)
   done = fixture.call("clientTraceProcessingEvent",
       BsonLite.document("k", "dialog", "d", BsonLite.document("c", event)),
       SEQ.getAndIncrement());
  else
   done = fixture.call("q7CompleteUiEvent", BsonLite.document("e", event),
       SEQ.getAndIncrement());
  check(frame(done, "completeEventReplyEnd") != null, "complete frame " + event);
  check(fixture.progress.completedEvents.contains(event), "completed " + event);
  check(!fixture.progress.processingEvents.contains(event), "processing cleared " + event);
 }

 private static boolean hasBattle(Fixture fixture, int scene) {
  return hasBattle(fixture.progress, scene);
 }

 private static boolean hasBattle(LocalTutorialStore.Progress progress, int scene) {
  Set<Integer> battle = progress.eventConditions.get("battle");
  return battle != null && battle.contains(scene);
 }

  private static void checkTutorialGuarantee() throws Exception {
  // Original new-profile tutorial production: fresh() starts at event 1000 with
  // initPrologue=true; the graph chain 1000->1001->1002->1004 completes 1004.
  // isHighSchoolUnlocked then gates area content on 1004, and every later week
  // preserves 1004 through LocalWeekEngine.TUTORIAL_FOUNDATION.
  byte[] profile = BsonLite.withAccountIdentity(
      Files.readAllBytes(new File(assets, "new_player.bson").toPath()), ACCOUNT, 903099);
  LocalTutorialStore.Progress progress = LocalTutorialStore.Progress.fresh();
  progress.weekCommit = "prologue";
  progress.patrolActions = 24;
  progress.processingEvents.clear();
  progress.processingNewbees.clear();
  try (Fixture fixture = new Fixture(profile, progress)) {
   check(fixture.progress.availableEvents.contains(1000), "fresh prologue offers 1000");
   check(fixture.progress.initPrologue, "fresh prologue flag");
   for (int event : new int[]{1000, 1001, 1002, 1004}) complete(fixture, event);
   check(fixture.progress.completedEvents.contains(1004), "prologue completes 1004");
   check(highSchool(fixture.progress), "1004 unlocks high school");
   byte[] stage = LocalCityProgress.stages(fixture.progress, 1, fixture.profile());
   check(Integer.valueOf(101).equals(BsonLite.intValue(stage, "cs")),
       "1004 yields original area1 cs101");
   LocalTutorialStore.Progress reset = (LocalTutorialStore.Progress) RESET_PROGRESS.invoke(null,
       fixture.progress, weeks, 8, weeks.entrances.get(7));
   check(reset.completedEvents.contains(1004), "week reset preserves 1004");
   System.out.println("tutorial production: 1000->1001->1002->1004, high-school unlocked, "
       + "area1 cs101, week reset preserves 1004");
  }
 }



 private static void handoffComplete(Fixture fixture, int event) throws Exception {
  fixture.progress.availableEvents.add(event);
  List<ProtoLite.EntityMessage> started = fixture.call("startEvent",
      BsonLite.document("e", event), SEQ.getAndIncrement());
  check(frame(started, "startEventReply") != null, "route handoff start reply " + event);
  check(fixture.progress.processingEvents.contains(event), "route handoff processing " + event);
  LocalEventCatalog.Event row = events.get(event);
  List<ProtoLite.EntityMessage> done;
  if (row != null && row.dialog > 0)
   done = fixture.call("clientTraceProcessingEvent",
       BsonLite.document("k", "dialog", "d", BsonLite.document("c", event)), SEQ.getAndIncrement());
  else
   done = fixture.call("q7CompleteUiEvent", BsonLite.document("e", event), SEQ.getAndIncrement());
  check(frame(done, "completeEventReplyEnd") != null, "route handoff complete " + event);
  check(fixture.progress.completedEvents.contains(event), "route handoff completed " + event);
  check(!fixture.progress.processingEvents.contains(event), "route handoff processing cleared " + event);
  fixture.call("getAreaStagesRequest", BsonLite.document("aid", 1), SEQ.getAndIncrement());
  check(receipt(fixture.profile(), event), "route handoff receipt " + event);
 }

 private static void checkRouteOnlyEffects() throws Exception {
  // Route selector/handoff fixture: the original route event is supplied in
  // availableEvents, then the real Gateway start/dialog path completes it.
  // This is not a full route replay; prerequisite route events are original
  // completed events only where noted.
  try (Fixture fixture = new Fixture(endings(), 14, true)) {
   clearPending(fixture);
   check(accepted(fixture.call("requestEnterStory", BsonLite.document("i", 14),
       SEQ.getAndIncrement()), "replyEnterStory"), "route14 entry");
   for (int event : CHAINS[2]) complete(fixture, event);
   check(locked(fixture.profile(), 2), "route14 init chain locks area2");
   
   fixture.progress.completedEvents.add(1180);
   handoffComplete(fixture, 1184);
   check("15-1".equals(BsonLite.stringValue(doc(fixture.profile(), "std"), "rt")),
       "route14 effect keeps route 15-1");
   check(!locked(fixture.profile(), 2), "1184 unlocks area2");
   byte[] day1 = fixture.profile();
   byte[] week = BsonLite.withProfileInt(doc(day1, "weeknum"), "d", 1);
   day1 = BsonLite.withProfileDocument(day1, "weeknum", week);
   Files.write(fixture.profileFile, day1);
   fixture.engine.refreshProfile(day1);
   handoffComplete(fixture, 2161);
   check(!locked(fixture.profile(), 2), "2161 keeps area2 unlocked");
   fixture.tutorials.save(ACCOUNT, fixture.progress);
   LocalTutorialStore.Progress reloaded = fixture.reload();
   byte[] persisted = fixture.profile();
   check(reloaded.completedEvents.contains(1184) && reloaded.completedEvents.contains(2161),
       "route14 effects persist");
   check(receipt(persisted, 1184) && receipt(persisted, 2161), "route14 receipts persist");
   check("15-1".equals(BsonLite.stringValue(doc(persisted, "std"), "rt")), "route14 route persists");
  }
  try (Fixture fixture = new Fixture(endings(), 15, true)) {
   clearPending(fixture);
   check(accepted(fixture.call("requestEnterStory", BsonLite.document("i", 15),
       SEQ.getAndIncrement()), "replyEnterStory"), "route15 entry");
   for (int event : CHAINS[3]) complete(fixture, event);
   handoffComplete(fixture, 5216);
   check("16-5".equals(BsonLite.stringValue(doc(fixture.profile(), "std"), "rt")),
       "5216 sets route 16-5");
   for (int area : new int[]{1, 2, 3, 4, 5, 7, 8}) check(locked(fixture.profile(), area),
       "5216 locks area " + area);
   handoffComplete(fixture, 5219);
   check("16-6".equals(BsonLite.stringValue(doc(fixture.profile(), "std"), "rt")),
       "5219 sets route 16-6");
   for (int area = 2; area <= 8; area++) check(locked(fixture.profile(), area),
       "5219 locks area " + area);
   fixture.tutorials.save(ACCOUNT, fixture.progress);
   LocalTutorialStore.Progress reloaded = fixture.reload();
   byte[] persisted = fixture.profile();
   check(reloaded.completedEvents.contains(5216) && reloaded.completedEvents.contains(5219),
       "route15 effects persist");
   check(receipt(persisted, 5216) && receipt(persisted, 5219), "route15 receipts persist");
   check(locked(persisted, 8) && "16-6".equals(BsonLite.stringValue(doc(persisted, "std"), "rt")),
       "route15 lock/route persist");
  }
  try (Fixture fixture = new Fixture(endings(), 26, true)) {
   clearPending(fixture);
   check(accepted(fixture.call("requestEnterStory", BsonLite.document("i", 26),
       SEQ.getAndIncrement()), "replyEnterStory"), "route26 entry");
   for (int event : CHAINS[7]) complete(fixture, event);
   handoffComplete(fixture, 1621);
   check("29-1".equals(BsonLite.stringValue(doc(fixture.profile(), "std"), "rt")),
       "1621 sets route 29-1");
   for (int area = 2; area <= 8; area++) check(state(fixture.profile(), area) == 0,
       "1621 frees area " + area);
   for (int area = 1; area <= 8; area++) check(locked(fixture.profile(), area),
       "1621 locks area " + area);
   handoffComplete(fixture, 1637);
   for (int area = 1; area <= 8; area++) check(!locked(fixture.profile(), area),
       "1637 unlocks area " + area);
   fixture.tutorials.save(ACCOUNT, fixture.progress);
   LocalTutorialStore.Progress reloaded = fixture.reload();
   byte[] persisted = fixture.profile();
   check(reloaded.completedEvents.contains(1621) && reloaded.completedEvents.contains(1637),
       "route26 effects persist");
   check(receipt(persisted, 1621) && receipt(persisted, 1637), "route26 receipts persist");
   check(!locked(persisted, 1) && state(persisted, 7) == 0, "route26 state/lock persist");
  }
 }

 private static void checkMenu(int index, int menu) throws Exception {
  check(StoryMainlineEntry.capability(menu), "candidate capability " + menu);
  check(StoryMainlineEntry.defaultChapter(menu), "candidate default chapter " + menu);
  check(StoryCityPolicy.supports(menu), "candidate supports " + menu);
  check(LocalStoryEntryPolicy.supports(menu), "patched original supports " + menu);
  try (Fixture fixture = new Fixture(endings(), menu, true)) {
   clearPending(fixture);
   byte[] before = fixture.profile();
   check(LocalWeekEngine.canEnter(before, weeks, menu), "canEnter " + menu);
   // Host-only advisory; the Gateway requestEnterStory below is the real gate proof.
   check(StoryMainlineEntry.entryReady(menu, before, fixture.progress, weeks),
       "host-only entryReady advisory " + menu);
   int sequence = SEQ.getAndIncrement();
   List<ProtoLite.EntityMessage> reply = fixture.call("requestEnterStory",
       BsonLite.document("i", menu), sequence);
   check(accepted(reply, "replyEnterStory"), "requestEnterStory accepted " + menu);
   check(Integer.valueOf(menu).equals(BsonLite.intValue(fixture.profile(), "q7ChapterMenu")),
       "committed q7ChapterMenu " + menu);
   check(fixture.progress.weekCommit != null && !fixture.progress.weekCommit.equals(WEEK),
       "committed week " + menu);
   check(fixture.progress.weekCommit.equals(fixture.reload().weekCommit),
       "week persisted " + menu);
   check(StoryCityPolicy.owns(fixture.profile()), "scoped city owner " + menu);
   check(StoryMainlineEntry.cityOwns(fixture.profile()), "default row owns effects " + menu);

   // Original default chapter stage (no chapter_mission_data family row).
   byte[] profile = fixture.profile();
   List<ProtoLite.EntityMessage> stages = fixture.call("getAreaStagesRequest",
       BsonLite.document("aid", 1), SEQ.getAndIncrement());
   ProtoLite.EntityMessage stageReply = frame(stages, "get_area_stages_reply");
   check(stageReply != null && Integer.valueOf(1).equals(BsonLite.intValue(stageReply.parameters, "ai")),
       "area1 reply " + menu);
   byte[] stage = BsonLite.documentValue(stageReply.parameters, "st");
   if (stage == null) stage = BsonLite.EMPTY_DOCUMENT;
   check(Integer.valueOf(101).equals(BsonLite.intValue(stage, "cs")), "default cs101 " + menu);
   check(Arrays.equals(stage, LocalCityProgress.stages(fixture.progress, 1, profile)),
       "default equals original projection " + menu);

   // Minimal real settlement on the default stage.
   List<ProtoLite.EntityMessage> admission = fixture.call("combatOfflineRequest",
       BsonLite.document("t", 1, "s", 101, "h", Arrays.asList(135),
           "d", BsonLite.document("a", 1)), SEQ.getAndIncrement());
   check(frame(admission, "combatOfflineReply") != null, "battle admission " + menu);
   fixture.offlineFinish(101, 0);
   check(!hasBattle(fixture, 101), "loss leaves no battle trace " + menu);
   check(Integer.valueOf(101).equals(BsonLite.intValue(
       LocalCityProgress.stages(fixture.progress, 1, fixture.profile()), "cs")),
       "loss keeps default cs101 " + menu);
   admission = fixture.call("combatOfflineRequest",
       BsonLite.document("t", 1, "s", 101, "h", Arrays.asList(135),
           "d", BsonLite.document("a", 1)), SEQ.getAndIncrement());
   check(frame(admission, "combatOfflineReply") != null, "battle re-admission " + menu);
   fixture.offlineFinish(101, 1);
   check(hasBattle(fixture, 101), "win traces battle " + menu);
   byte[] afterWin = LocalCityProgress.stages(fixture.progress, 1, fixture.profile());
   check(Integer.valueOf(101).equals(BsonLite.intValue(afterWin, "cs")),
       "area1 default projection stays cs101 (fixed single-scene default) " + menu);

   // Dialog chain + completed-event area effects through the real engine.
   for (int event : CHAINS[index]) complete(fixture, event);
   profile = fixture.profile();
   for (int event : CHAINS[index]) {
    if (events.cityEffects.get(event) == null) continue;
    check(receipt(profile, event), "effect receipt " + event);
    applyEffects(profile, event);
   }
   for (int event : ROUTE_ONLY_EFFECTS[index])
    check(!receipt(profile, event),
        "route-only effect not applied by default admission " + event);

   // Save/reload keeps week, receipt, state and lock projection.
   fixture.tutorials.save(ACCOUNT, fixture.progress);
   LocalTutorialStore.Progress reloaded = fixture.reload();
   byte[] persisted = fixture.profile();
   check(reloaded.weekCommit.equals(fixture.progress.weekCommit), "reload week " + menu);
   check(hasBattle(reloaded, 101), "reload keeps battle101 trace " + menu);
   check(Integer.valueOf(menu).equals(BsonLite.intValue(persisted, "q7ChapterMenu")),
       "reload menu " + menu);
   for (int event : CHAINS[index]) {
    if (events.cityEffects.get(event) == null) continue;
    check(receipt(persisted, event), "reload receipt " + event);
    applyEffects(persisted, event);
   }
   check(Arrays.equals(persisted, fixture.profile()), "reload profile stable " + menu);
   int effects = 0;
   for (int event : CHAINS[index]) if (events.cityEffects.get(event) != null) effects++;
   System.out.println("menu " + menu + " entry/default cs101/settlement/reload, effects=" + effects
       + ", route-only=" + Arrays.toString(ROUTE_ONLY_EFFECTS[index]));
  }
 }

 private static List<Integer> endings() {
  List<Integer> out = new ArrayList<>();
  for (int value : ENDINGS) out.add(value);
  return out;
 }

 private static void checkArea2Advance() throws Exception {
  // The original normal-area default chain advances on a real win; area1 is a
  // fixed single-scene projection and intentionally does not.
  try (Fixture fixture = new Fixture(endings(), 7, false)) {
   fixture.progress.completedEvents.add(1013);
   fixture.progress.completedEvents.add(1043);
   clearPending(fixture);
   check(accepted(fixture.call("requestEnterStory", BsonLite.document("i", 7),
       SEQ.getAndIncrement()), "replyEnterStory"), "menu7 area2 entry");
   byte[] stage = LocalCityProgress.stages(fixture.progress, 2, fixture.profile());
   check(Integer.valueOf(1101).equals(BsonLite.intValue(stage, "cs")), "area2 default cs1101");
   check(BsonLite.keys(BsonLite.arrayValue(stage, "sl")).size() == 6, "area2 default six groups");
   List<ProtoLite.EntityMessage> admission = fixture.call("combatOfflineRequest",
       BsonLite.document("t", 1, "s", 1101, "h", Arrays.asList(135),
           "d", BsonLite.document("a", 2)), SEQ.getAndIncrement());
   check(frame(admission, "combatOfflineReply") != null, "area2 admission");
   fixture.offlineFinish(1101, 0);
   check(Integer.valueOf(1101).equals(BsonLite.intValue(
       LocalCityProgress.stages(fixture.progress, 2, fixture.profile()), "cs")),
       "area2 loss keeps cs1101");
   admission = fixture.call("combatOfflineRequest",
       BsonLite.document("t", 1, "s", 1101, "h", Arrays.asList(135),
           "d", BsonLite.document("a", 2)), SEQ.getAndIncrement());
   check(frame(admission, "combatOfflineReply") != null, "area2 re-admission");
   fixture.offlineFinish(1101, 1);
   check(Integer.valueOf(1102).equals(BsonLite.intValue(
       LocalCityProgress.stages(fixture.progress, 2, fixture.profile()), "cs")),
       "area2 default advances to cs1102 on win");
   fixture.tutorials.save(ACCOUNT, fixture.progress);
   check(Integer.valueOf(1102).equals(BsonLite.intValue(
       LocalCityProgress.stages(fixture.reload(), 2, fixture.profile()), "cs")),
       "area2 cs1102 persists after reload");
  }
 }

  private static void checkEventBattleFixture() throws Exception {
  // Synthetic-prerequisite event battle fixture, NOT a city-chapter t1 test and
  // not a native battle: entry/init are not redone; route 25-6, day 7, completed
  // 7596 and client-op 1 are host-injected so trigger 8753 offers its type2
  // scene462 event battle. The real 4/23 city-chapter t1 proof lives in
  // StoryMainlineDataClosedHost.
  LocalTutorialStore.Progress progress = LocalTutorialStore.Progress.completed();
  progress.weekIndex = 8;
  progress.weekCommit = WEEK;
  progress.inEmergency = false;
  progress.initPrologue = false;
  progress.patrolActions = 60;
  progress.processingEvents.clear();
  progress.processingNewbees.clear();
  progress.completedEvents.addAll(Arrays.asList(1398, 1375, 1396, 1395, 7596));
  byte[] profile = BsonLite.withAccountIdentity(
      Files.readAllBytes(new File(assets, "new_player.bson").toPath()), ACCOUNT, 903023);
  profile = BsonLite.withProfileDocument(profile, "weeknum",
      BsonLite.document("w", 8, "d", 7, "av", 60));
  profile = BsonLite.withProfileDocument(profile, "std",
      BsonLite.document("rt", "25-6", "ed", Arrays.asList(63, 39), "ff", false));
  profile = BsonLite.withProfileInt(profile, "q7ChapterMenu", 23);
  profile = BsonLite.withProfileDocument(profile, "city", BsonLite.document("av", 60));
  profile = BsonLite.withHero(profile, 102);
  try (Fixture fixture = new Fixture(profile, progress)) {
   fixture.engine.updateClientOperation(1);
   check(StoryMainlineEntry.capability(23), "v52 menu23 packaged capability (not re-entered)");
   int area = StoryMissionBridge.area(462);
   int status = LocalCityProgress.status(fixture.progress, area, fixture.profile());
   byte[] stage = LocalCityProgress.stages(fixture.progress, area, fixture.profile());
   check(Arrays.equals(stage, StoryMissionBridge.stages(fixture.progress, area, fixture.profile())),
       "synthetic event battle status/stage stays original for area " + area);
   List<ProtoLite.EntityMessage> pull = fixture.call("pullEvents", BsonLite.EMPTY_DOCUMENT,
       SEQ.getAndIncrement());
   check(frame(pull, "pullEventsReply") != null, "synthetic event battle pullEvents reply");
   check(fixture.progress.availableEvents.contains(8753), "synthetic event battle trigger8753 offered");
   fixture.call("startEvent", BsonLite.document("e", 8753), SEQ.getAndIncrement());
   check(fixture.progress.processingEvents.contains(8753), "synthetic event battle 8753 processing");
   byte[] params = BsonLite.document("t", 2, "s", 462, "h", Arrays.asList(102),
       "d", BsonLite.EMPTY_DOCUMENT);
   List<ProtoLite.EntityMessage> admitted = fixture.call("combatOfflineRequest", params,
       SEQ.getAndIncrement());
   ProtoLite.EntityMessage reply = frame(admitted, "combatOfflineReply");
   check(reply != null && Integer.valueOf(2).equals(BsonLite.intValue(reply.parameters, "t"))
       && Integer.valueOf(462).equals(BsonLite.intValue(reply.parameters, "s"))
       && BsonLite.stringValue(reply.parameters, "f") != null
       && !BsonLite.stringValue(reply.parameters, "f").isEmpty(),
       "synthetic event battle admission type2/scene462 (status=" + status + ")");
   byte[] lost = BsonLite.document("t", 2, "s", 462, "h", Arrays.asList(102),
       "x", Arrays.asList(102), "w", 0);
   fixture.offlineFinishDoc(lost);
   check(!hasBattle(fixture, 462), "synthetic event battle loss leaves no battle462 trace");
   check(fixture.progress.processingEvents.contains(8753), "synthetic event battle loss keeps 8753 processing");
   List<ProtoLite.EntityMessage> retry = fixture.call("combatOfflineRequest", params,
       SEQ.getAndIncrement());
   check(frame(retry, "combatOfflineReply") != null, "synthetic event battle retry admission");
   byte[] won = BsonLite.document("t", 2, "s", 462, "h", Arrays.asList(102),
       "x", Arrays.asList(102), "w", 1);
   List<ProtoLite.EntityMessage> settled = fixture.framesOf(fixture.offlineFinishDoc(won));
   check(frame(settled, "combatOfflineReward") != null, "synthetic event battle win reward frame");
   check(hasBattle(fixture, 462), "synthetic event battle win traces battle462");
   check(fixture.progress.processingEvents.contains(8753), "synthetic event battle 8753 waits for dialog");
   check(!receipt(fixture.profile(), 8753), "synthetic event battle 8753 has no city effect row");
   List<ProtoLite.EntityMessage> done = fixture.call("clientTraceProcessingEvent",
       BsonLite.document("k", "dialog", "d", BsonLite.document("c", 8753)),
       SEQ.getAndIncrement());
   check(frame(done, "completeEventReplyEnd") != null, "synthetic event battle dialog completion");
   check(fixture.progress.completedEvents.contains(8753), "synthetic event battle 8753 completed");
   check(!fixture.progress.processingEvents.contains(8753), "synthetic event battle 8753 processing cleared");
   check(Integer.valueOf(1).equals(fixture.progress.eventCompletions.get(8753)),
       "synthetic event battle completion count 1");
   fixture.tutorials.save(ACCOUNT, fixture.progress);
   LocalTutorialStore.Progress loaded = fixture.reload();
   check(loaded.completedEvents.contains(8753) && hasBattle(loaded, 462),
       "event battle completion+battle trace persist after reload");
   System.out.println("menu 23 event battle fixture (type2/scene462, NOT t1 chapter): area="
       + area + " status=" + status + " stage="
       + BsonLite.messagePackValue(stage, false)
       + " admission/scene462/loss-retry-win/dialog/reload");
  }
 }

 private static void pull(Fixture fixture) throws Exception {
  fixture.call("pullEvents", BsonLite.EMPTY_DOCUMENT, SEQ.getAndIncrement());
 }

 private static void offer(Fixture fixture, int event, boolean expected) {
  check(fixture.progress.availableEvents.contains(event) == expected,
      (expected ? "trigger offers " : "trigger withholds ") + event);
 }

 private static void startTriggered(Fixture fixture, int event) throws Exception {
  offer(fixture, event, true);
  List<ProtoLite.EntityMessage> started = fixture.call("startEvent",
      BsonLite.document("e", event), SEQ.getAndIncrement());
  check(frame(started, "startEventReply") != null, "trigger start reply " + event);
  check(fixture.progress.processingEvents.contains(event), "trigger processing " + event);
 }

 private static void completeTriggered(Fixture fixture, int event) throws Exception {
  startTriggered(fixture, event);
  LocalEventCatalog.Event row = events.get(event);
  List<ProtoLite.EntityMessage> done;
  if (row != null && row.dialog > 0)
   done = fixture.call("clientTraceProcessingEvent",
       BsonLite.document("k", "dialog", "d", BsonLite.document("c", event)),
       SEQ.getAndIncrement());
  else
   done = fixture.call("q7CompleteUiEvent", BsonLite.document("e", event),
       SEQ.getAndIncrement());
  check(frame(done, "completeEventReplyEnd") != null, "trigger complete " + event);
  check(fixture.progress.completedEvents.contains(event), "trigger completed " + event);
  check(!fixture.progress.processingEvents.contains(event),
      "trigger processing cleared " + event);
 }

 private static void settle(Fixture fixture) throws Exception {
  fixture.call("getAreaStagesRequest", BsonLite.document("aid", 1), SEQ.getAndIncrement());
 }

 private static void setDay(Fixture fixture, int day) throws Exception {
  byte[] profile = fixture.profile();
  byte[] week = BsonLite.withProfileInt(doc(profile, "weeknum"), "d", day);
  profile = BsonLite.withProfileDocument(profile, "weeknum", week);
  Files.write(fixture.profileFile, profile);
  fixture.engine.refreshProfile(profile);
 }

 private static String route(byte[] profile) {
  return BsonLite.stringValue(doc(profile, "std"), "rt");
 }

 private static void checkMenu8RealTriggers() throws Exception {
  // Real original trigger path for menu8: 30015/40012 are offered by the
  // frozen @trigger rows after their original battle facts, their completion
  // satisfies the 30045/40042 preAll, and the original 2049 -> 2055 -> 2054
  // chain applies @route 9-3. No target is inserted into availableEvents.
  try (Fixture fixture = new Fixture(endings(), 8, true)) {
   clearPending(fixture);
   check(accepted(fixture.call("requestEnterStory", BsonLite.document("i", 8),
       SEQ.getAndIncrement()), "replyEnterStory"), "menu8 real entry");
   for (int event : CHAINS[1]) complete(fixture, event);
   settle(fixture);
   check("1".equals(route(fixture.profile())), "menu8 starts on original route 1");
   // Original tutorial foundation plus the cond9 battle facts of 30015/40012.
   // 1066 is the completed week-3 reset event for this later-week profile; it
   // is not a menu8 trigger and keeps the fixture out of the original emergency.
   fixture.progress.completedEvents.addAll(Arrays.asList(1004, 1013, 1043, 1066));
   fixture.engine.trace("battle", Collections.singletonList(2106));
   fixture.engine.trace("battle", Collections.singletonList(3106));
   fixture.progress.completedEvents.add(40008);
   pull(fixture);
   offer(fixture, 30015, true);
   offer(fixture, 40012, true);
   offer(fixture, 30045, false);
   offer(fixture, 40042, false);
   fixture.progress.completedEvents.add(30015);
   fixture.progress.completedEvents.add(40012);
   pull(fixture);
   offer(fixture, 30045, false);
   offer(fixture, 40042, false);

   setDay(fixture, 1);
   pull(fixture);
   offer(fixture, 2000, true);
   completeTriggered(fixture, 2000);
   pull(fixture);
   offer(fixture, 2049, true);
   completeTriggered(fixture, 2049);
   offer(fixture, 2055, true);
   offer(fixture, 2056, true);
   completeTriggered(fixture, 2055);
   for (int event : new int[]{2050, 2051, 2052, 2053, 2054})
    completeTriggered(fixture, event);
   settle(fixture);
   check("9-3".equals(route(fixture.profile())), "original 2054 applies route 9-3");
   pull(fixture);
   offer(fixture, 30045, true);
   offer(fixture, 40042, true);
   // Mutex 1129 is an original trigger prerequisite, not a target pre-offer.
   fixture.progress.completedEvents.add(1129);
   pull(fixture);
   offer(fixture, 30045, false);
   offer(fixture, 40042, false);
   fixture.progress.completedEvents.remove(1129);
   pull(fixture);
   offer(fixture, 30045, true);
   offer(fixture, 40042, true);
   completeTriggered(fixture, 30045);
   completeTriggered(fixture, 40042);
   settle(fixture);
   byte[] profile = fixture.profile();
   check(receipt(profile, 30045) && receipt(profile, 40042),
       "menu8 route triggers receipt");
   check(!locked(profile, 4), "30045 unlocks area4");
   check(!locked(profile, 3), "40042 unlocks area3");
   fixture.tutorials.save(ACCOUNT, fixture.progress);
   LocalTutorialStore.Progress reloaded = fixture.reload();
   byte[] persisted = fixture.profile();
   check(reloaded.completedEvents.contains(30045) && reloaded.completedEvents.contains(40042),
       "menu8 route triggers persist");
   check(receipt(persisted, 30045) && receipt(persisted, 40042),
       "menu8 receipts persist");
   check(!locked(persisted, 3) && !locked(persisted, 4),
       "menu8 unlocks persist");
   check("9-3".equals(route(persisted)), "menu8 route persists");
  }
 }

 private static void checkMenu21RealTriggers() throws Exception {
  // 1347 is offered by its original @trigger only with clientOp 4, completed
  // 1339, route 22/22-1 and no 1345 mutex. 1346 is not a 1347 successor: it is
  // the original @outcome successor of the 1345 battle branch, so the two
  // branches are proved separately.
  try (Fixture fixture = new Fixture(endings(), 21, true)) {
   clearPending(fixture);
   check(accepted(fixture.call("requestEnterStory", BsonLite.document("i", 21),
       SEQ.getAndIncrement()), "replyEnterStory"), "menu21 real entry");
   for (int event : CHAINS[6]) complete(fixture, event);
   settle(fixture);
   fixture.progress.completedEvents.add(1066);
   pull(fixture);
   check("22-1".equals(route(fixture.profile())), "1341 applies route 22-1");
   pull(fixture);
   offer(fixture, 1347, false);
   offer(fixture, 1345, false);
   offer(fixture, 1346, false);
   fixture.engine.updateClientOperation(4);
   pull(fixture);
   offer(fixture, 1347, true);
   offer(fixture, 1345, false);
   completeTriggered(fixture, 1347);
   settle(fixture);
   byte[] profile = fixture.profile();
   check("22-9".equals(route(profile)), "1347 applies route 22-9");
   check(receipt(profile, 1347), "1347 receipt");
   for (int area : new int[]{1, 2, 3, 4, 5, 6, 8})
    check(!locked(profile, area), "1347 unlocks area " + area);
   offer(fixture, 1345, false);
   offer(fixture, 1346, false);
   fixture.tutorials.save(ACCOUNT, fixture.progress);
   LocalTutorialStore.Progress reloaded = fixture.reload();
   byte[] persisted = fixture.profile();
   check(reloaded.completedEvents.contains(1347), "1347 persists");
   check(receipt(persisted, 1347), "1347 receipt persists");
   check("22-9".equals(route(persisted)), "1347 route persists");
  }
  try (Fixture fixture = new Fixture(endings(), 21, true)) {
   clearPending(fixture);
   check(accepted(fixture.call("requestEnterStory", BsonLite.document("i", 21),
       SEQ.getAndIncrement()), "replyEnterStory"), "menu21 battle branch entry");
   for (int event : CHAINS[6]) complete(fixture, event);
   settle(fixture);
   fixture.progress.completedEvents.add(1066);
   fixture.progress.completedEvents.add(1344);
   fixture.engine.updateClientOperation(4);
   pull(fixture);
   offer(fixture, 1345, true);
   offer(fixture, 1346, false);
   startTriggered(fixture, 1345);
   check(!fixture.progress.availableEvents.contains(1347), "1345 start mutexes 1347");
   List<ProtoLite.EntityMessage> admission = fixture.call("combatOfflineRequest",
       BsonLite.document("t", 2, "s", 418, "h", Arrays.asList(135),
           "d", BsonLite.EMPTY_DOCUMENT), SEQ.getAndIncrement());
   check(frame(admission, "combatOfflineReply") != null,
       "1345 story battle admission scene418");
   byte[] won = BsonLite.document("t", 2, "s", 418, "h", Arrays.asList(135),
       "x", Arrays.asList(135), "w", 1);
   List<ProtoLite.EntityMessage> settled = fixture.framesOf(fixture.offlineFinishDoc(won));
   check(frame(settled, "combatOfflineReward") != null,
       "1345 story battle win reward");
   check(fixture.progress.processingEvents.contains(1345),
       "1345 waits for original dialog");
   List<ProtoLite.EntityMessage> done = fixture.call("clientTraceProcessingEvent",
       BsonLite.document("k", "dialog", "d", BsonLite.document("c", 1345)),
       SEQ.getAndIncrement());
   check(frame(done, "completeEventReplyEnd") != null, "1345 dialog completion");
   check(fixture.progress.completedEvents.contains(1345), "1345 completed");
   offer(fixture, 1346, true);
   completeTriggered(fixture, 1346);
   settle(fixture);
   byte[] profile = fixture.profile();
   check("22-9".equals(route(profile)), "1346 outcome applies route 22-9");
   check(receipt(profile, 1346), "1346 receipt");
   for (int area : new int[]{1, 2, 3, 4, 5, 6, 8})
    check(!locked(profile, area), "1346 unlocks area " + area);
   fixture.tutorials.save(ACCOUNT, fixture.progress);
   LocalTutorialStore.Progress reloaded = fixture.reload();
   byte[] persisted = fixture.profile();
   check(reloaded.completedEvents.contains(1345) && reloaded.completedEvents.contains(1346),
       "1345/1346 persist");
   check(receipt(persisted, 1346), "1346 receipt persists");
   check("22-9".equals(route(persisted)), "1346 route persists");
  }
 }

 private static void checkNegatives() throws Exception {
  // A menu outside the 1..32 mainline scope stays closed.
  try (Fixture fixture = new Fixture(endings(), 33, true)) {
   check(!StoryCityPolicy.supports(33), "menu33 remains closed");
   boolean rejected = false;
   try {
    List<ProtoLite.EntityMessage> reply = fixture.call("requestEnterStory",
        BsonLite.document("i", 33), SEQ.getAndIncrement());
    rejected = !accepted(reply, "replyEnterStory");
   } catch (IllegalArgumentException expected) {
    rejected = true;
   }
   check(rejected, "menu33 entry rejected");
   check(Integer.valueOf(1).equals(BsonLite.intValue(fixture.profile(), "q7ChapterMenu")),
       "menu33 does not commit");
  }
  // Original ending precondition still gates the candidate menu.
  try (Fixture fixture = new Fixture(Collections.emptyList(), 7, true)) {
   check(!LocalWeekEngine.canEnter(fixture.profile(), weeks, 7), "menu7 endings required");
   boolean rejected = false;
   try {
    List<ProtoLite.EntityMessage> reply = fixture.call("requestEnterStory",
        BsonLite.document("i", 7), SEQ.getAndIncrement());
    rejected = !accepted(reply, "replyEnterStory");
   } catch (IllegalArgumentException expected) {
    rejected = true;
   }
   check(rejected, "menu7 without endings rejected");
  }
  // Without the original tutorial foundation the default projection has no stage.
  try (Fixture fixture = new Fixture(endings(), 7, false)) {
   clearPending(fixture);
   check(accepted(fixture.call("requestEnterStory", BsonLite.document("i", 7),
       SEQ.getAndIncrement()), "replyEnterStory"), "menu7 entry without seed accepted");
   List<ProtoLite.EntityMessage> stages = fixture.call("getAreaStagesRequest",
       BsonLite.document("aid", 1), SEQ.getAndIncrement());
   ProtoLite.EntityMessage reply = frame(stages, "get_area_stages_reply");
   check(reply != null, "no-seed area1 reply");
   byte[] stage = BsonLite.documentValue(reply.parameters, "st");
   check(!highSchool(fixture.progress), "no-seed profile fails original high-school gate");
   check(stage == null || BsonLite.keys(stage).isEmpty(),
       "no-seed projection is empty by the original gate, not accepted closure");
  }
 }


 private static void checkSelectorBranches() throws Exception {
  try (Fixture fixture = new Fixture(endings(), 7, true)) {
   fixture.progress.processingEvents.add(1013103);
   fixture.progress.availableEvents.clear();
   check(fixture.engine.selectEventOption(1013103, 1013104), "original selector chooses branch A");
   check(fixture.progress.availableEvents.contains(1013104), "selected branch A offered");
   check(!fixture.progress.availableEvents.contains(1013105), "unselected sibling B not offered");
   fixture.tutorials.save(ACCOUNT, fixture.progress);
   LocalTutorialStore.Progress reloaded = fixture.reload();
   check(reloaded.availableEvents.contains(1013104), "selected A survives reload");
   check(!reloaded.availableEvents.contains(1013105), "unselected B stays closed after reload");
  }
 }
 private static boolean siblingOffered(LocalTutorialStore.Progress progress, int child) {
  return progress.availableEvents.contains(child) || progress.processingEvents.contains(child)
      || progress.completedEvents.contains(child);
 }

 // 5215 and 5218 are the two original route-16 branch parents (their mutex
 // predecessors 5214/5217 choose the branch); 1620 has no parent sibling.
 private static int siblingParent(int parent) {
  if (parent == 5215) return 5218;
  if (parent == 5218) return 5215;
  return 0;
 }

 private static void checkOriginalManagerSelector() throws Exception {
  // Manager-level contract: the selected original child is offered; the other
  // route-selection children in this fixture are not.
  for (int[] option : ORIGINAL_OPTIONS) {
   int parent = option[0], child = option[1];
   try (Fixture fixture = new Fixture(endings(), 15, true)) {
    fixture.progress.processingEvents.clear();
    fixture.progress.processingEvents.add(parent);
    // The real alternative branch parent is completed without its own child:
    // a generic all-successors offer would leak that unselected child here.
    int siblingBranch = siblingParent(parent);
    if (siblingBranch != 0) fixture.progress.completedEvents.add(siblingBranch);
    fixture.progress.availableEvents.clear();
    check(!fixture.progress.availableEvents.contains(child),
        "target child not pre-offered " + child);
    check(fixture.engine.selectEventOption(parent, child),
        "manager selects original parent " + parent + "->" + child);
    check(fixture.progress.availableEvents.contains(child),
        "manager offers selected child " + child);
    check(fixture.progress.completedEvents.contains(parent),
        "manager completes selected parent " + parent);
    check(!fixture.progress.processingEvents.contains(parent),
        "manager clears selected parent processing " + parent);
    for (int[] sibling : ORIGINAL_OPTIONS)
     if (sibling[1] != child)
      check(!siblingOffered(fixture.progress, sibling[1]),
          "unselected route child " + sibling[1] + " stays closed");
    fixture.tutorials.save(ACCOUNT, fixture.progress);
    LocalTutorialStore.Progress reloaded = fixture.reload();
    check(reloaded.completedEvents.contains(parent), "selector parent survives reload " + parent);
    check(reloaded.availableEvents.contains(child), "selected child survives reload " + child);
    for (int[] sibling : ORIGINAL_OPTIONS)
     if (sibling[1] != child)
      check(!siblingOffered(reloaded, sibling[1]),
          "unselected route child " + sibling[1] + " stays closed after reload");
   }
  }
 }

 private static void checkOriginalStartEventOption() throws Exception {
  // Reliable RPC: only the original parent is processing; {e,se,op} completes
  // the parent, starts only the selected child, then the child's original
  // dialog trace applies its city effect/receipt. No target is pre-offered.
  for (int i = 0; i < ORIGINAL_OPTIONS.length; i++) {
   int[] option = ORIGINAL_OPTIONS[i];
   int parent = option[0], child = option[1], op = option[2];
   String route = ORIGINAL_OPTION_ROUTES[i];
   try (Fixture fixture = new Fixture(endings(), 15, true)) {
    int menu = child == 1621 ? 26 : 15;
    clearPending(fixture);
    check(accepted(fixture.call("requestEnterStory", BsonLite.document("i", menu),
        SEQ.getAndIncrement()), "replyEnterStory"), "original option menu entry " + menu);
    fixture.progress.processingEvents.clear();
    fixture.progress.processingEvents.add(parent);
    // The real alternative branch parent is completed without its own child.
    int siblingBranch = siblingParent(parent);
    if (siblingBranch != 0) fixture.progress.completedEvents.add(siblingBranch);
    fixture.progress.availableEvents.clear();
    check(!fixture.progress.availableEvents.contains(child), "target child not pre-offered " + child);
    List<ProtoLite.EntityMessage> optionReply = fixture.call("startEventOption",
        BsonLite.document("e", parent, "se", child, "op", op), SEQ.getAndIncrement());
    check(frame(optionReply, "completeEventReplyStart") != null,
        "reliable option parent start frame " + parent);
    ProtoLite.EntityMessage parentEnd = frame(optionReply, "completeEventReplyEnd");
    check(parentEnd != null && Integer.valueOf(parent).equals(
        BsonLite.intValue(parentEnd.parameters, "e")),
        "reliable option completes parent " + parent);
    ProtoLite.EntityMessage started = frame(optionReply, "startEventReply");
    check(started != null && Integer.valueOf(child).equals(BsonLite.intValue(started.parameters, "e"))
        && Integer.valueOf(1).equals(BsonLite.intValue(started.parameters, "r")),
        "reliable option starts selected child " + child + " op=" + op);
    check(fixture.progress.completedEvents.contains(parent), "RPC parent completed " + parent);
    check(fixture.progress.processingEvents.contains(child), "RPC selected child processing " + child);
    check(!fixture.progress.availableEvents.contains(child),
        "RPC selected child started rather than left offered " + child);
    for (int[] sibling : ORIGINAL_OPTIONS)
     if (sibling[1] != child)
      check(!siblingOffered(fixture.progress, sibling[1]),
          "unselected route child " + sibling[1] + " stays closed");
    List<ProtoLite.EntityMessage> done = fixture.call("clientTraceProcessingEvent",
        BsonLite.document("k", "dialog", "d", BsonLite.document("c", child)),
        SEQ.getAndIncrement());
    ProtoLite.EntityMessage childEnd = frame(done, "completeEventReplyEnd");
    check(childEnd != null && Integer.valueOf(child).equals(
        BsonLite.intValue(childEnd.parameters, "e")),
        "selected child dialog completion " + child);
    check(fixture.progress.completedEvents.contains(child), "selected child completed " + child);
    check(!fixture.progress.processingEvents.contains(child),
        "selected child processing cleared " + child);
    fixture.call("getAreaStagesRequest", BsonLite.document("aid", 1), SEQ.getAndIncrement());
    byte[] profile = fixture.profile();
    check(receipt(profile, child), "selected child receipt " + child);
    check(route.equals(BsonLite.stringValue(doc(profile, "std"), "rt")),
        "selected child route " + route);
    applyEffects(profile, child);
    for (int[] sibling : ORIGINAL_OPTIONS)
     if (sibling[1] != child) {
      check(!receipt(profile, sibling[1]),
          "unselected route child " + sibling[1] + " has no receipt");
      check(!siblingOffered(fixture.progress, sibling[1]),
          "unselected route child " + sibling[1] + " not completed");
     }
    fixture.tutorials.save(ACCOUNT, fixture.progress);
    LocalTutorialStore.Progress reloaded = fixture.reload();
    byte[] persisted = fixture.profile();
    check(reloaded.completedEvents.contains(parent) && reloaded.completedEvents.contains(child),
        "RPC parent+child survive reload " + parent + "->" + child);
    check(receipt(persisted, child), "child receipt survives reload " + child);
    check(route.equals(BsonLite.stringValue(doc(persisted, "std"), "rt")),
        "route survives reload " + route);
    applyEffects(persisted, child);
    check(Arrays.equals(persisted, fixture.profile()), "reload profile stable " + parent);
    for (int[] sibling : ORIGINAL_OPTIONS)
     if (sibling[1] != child)
      check(!receipt(persisted, sibling[1]),
          "unselected route child " + sibling[1] + " receipt stays closed");
    System.out.println("original startEventOption " + parent + "->" + child
        + " op=" + op + " route=" + route + " receipt=" + receipt(persisted, child));
   }
  }
 }

 public static void main(String[] args) throws Exception {
  assets = new File(args[0]);
  prepare(args[1]);
  if (args.length > 2 && "original-option".equals(args[2])) {
   checkOriginalManagerSelector();
   checkOriginalStartEventOption();
   System.out.println("PASS " + checks + " original startEventOption manager+RPC: "
       + "5215->5216/5218->5219/1620->1621 op=1, selected child only, "
       + "effects/receipt/reload; no target pre-offered");
   return;
  }
  for (int index = 0; index < MENUS.length; index++) checkMenu(index, MENUS[index]);
  checkRouteOnlyEffects();
  checkMenu8RealTriggers();
  checkMenu21RealTriggers();
  checkTutorialGuarantee();
  checkArea2Advance();
  checkEventBattleFixture();
  checkSelectorBranches();
  checkOriginalManagerSelector();
  checkOriginalStartEventOption();
  checkNegatives();
  System.out.println("PASS " + checks + " default-chapter admission: "
      + "7/8/14/15/16/18/21/26 entry, default cs101, settlement, dialog effects, reload; "
      + "original startEventOption 5215->5216/5218->5219/1620->1621 op=1; "
      + "menu8 real triggers 30015/40012/30045/40042 via original route 9-3; "
      + "menu21 real trigger 1347 clientOp/order and 1345 outcome 1346; "
      + "negative 33/missing-ending/absent-stage; 4/23 event battle fixture only (not t1)");
 }
}
