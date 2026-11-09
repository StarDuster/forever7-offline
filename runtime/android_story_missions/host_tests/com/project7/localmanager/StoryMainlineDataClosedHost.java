package com.project7.localmanager;

import android.content.*;
import android.content.res.*;
import java.io.*;
import java.lang.reflect.*;
import java.nio.*;
import java.nio.file.*;
import java.util.*;

/**
 * Limited v48 host for data-closed menus and the shared typed city-effect reducer.
 *
 * <p>Scoped entry is proven for 24/29/31: negative canEnter, original
 * requestEnterStory, committed/persisted week cycle, reload and init-chain city
 * effects. Menus 17/27/30 are host-verified data closure only (canEnter, chapter
 * route, first stage) and stay closed on purpose. The reducer split is proven
 * with a real hero effect event, plus unknown/friendly rejection. No D8, APK,
 * native or full route replay is used.</p>
 */
public final class StoryMainlineDataClosedHost {
 private static final String ACCOUNT = "host_mainline_dataclosed";
 private static final String WEEK = "dcl00000000000000000000";
 private static final int[] SCOPED = {4, 17, 23, 24, 27, 29, 30, 31};
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

 private static byte[] entryProfile(int menu, List<Integer> endings, int[] heroes,
                                    List<Integer> completed, boolean ownHero114) throws IOException {
  byte[] profile = BsonLite.withAccountIdentity(
      Files.readAllBytes(new File(assets, "new_player.bson").toPath()), ACCOUNT, 901200 + menu);
  profile = BsonLite.withProfileDocument(profile, "weeknum",
      BsonLite.document("w", 8, "d", 0, "av", 60));
  profile = BsonLite.withProfileDocument(profile, "std",
      BsonLite.document("rt", "1", "ed", endings));
  profile = BsonLite.withProfileInt(profile, "q7ChapterMenu", 1);
  profile = BsonLite.withProfileArray(profile, "q7WeekEventBaseline", completed);
  profile = BsonLite.withProfileDocument(profile, "city", BsonLite.document("av", 60));
  byte[] inventory = doc(profile, "inv");
  inventory = BsonLite.withProfileArray(inventory, "items",
      Arrays.asList(BsonLite.document("i", 345, "w", 1, "u", "0123456789abcdef01234567")));
  profile = BsonLite.withProfileDocument(profile, "inv", inventory);
  for (int hero : heroes) profile = BsonLite.withHero(profile, hero);
  if (ownHero114) profile = BsonLite.withHero(profile, 114);
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
  final Set<Integer> reliableSequences = new LinkedHashSet<>();

  Fixture(int menu, List<Integer> endings, boolean ownHero114) throws Exception {
   root = Files.createTempDirectory("mainline-dataclosed-");
   Files.createDirectories(root.resolve("profiles"));
   profileFile = root.resolve("profiles/" + ACCOUNT + ".bson");
   byte[] profile = entryProfile(menu, endings, new int[]{135, 136, 137}, Collections.emptyList(),
       ownHero114);
   Files.write(profileFile, profile);
   Context context = new Context(root.toFile(), new AssetManager(assets));
   store = new LocalProfileStore(context);
   tutorials = new LocalTutorialStore(context);
   progress = progress();
   tutorials.save(ACCOUNT, progress);
   engine = new LocalEventEngine(events, newbees, progress, 0, profile, true);
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
       reliableSequences, new HashSet<Integer>(),
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

  void chapterBattleT1(LocalEventEngine eng, int area, int scene) throws Exception {
   List<ProtoLite.EntityMessage> admitted = call(eng, "combatOfflineRequest",
       BsonLite.document("t", 1, "s", scene, "d", BsonLite.document("a", area),
           "h", Arrays.asList(135, 136)), SEQ.getAndIncrement());
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
       BsonLite.document("t", 1, "s", scene, "h", Arrays.asList(135, 136),
           "x", Collections.emptyList(), "w", 1));
   check(frame(won, "combatOfflineReward") != null, "chapter t1 reward " + scene);
   check(progress.eventConditions.get("battle") != null &&
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
   int sequence = SEQ.getAndIncrement();
   List<ProtoLite.EntityMessage> reply = call("requestEnterStory",
       BsonLite.document("i", menu), sequence);
   ProtoLite.EntityMessage accepted = frame(reply, "replyEnterStory");
   if (accepted == null) for (ProtoLite.EntityMessage message : reply)
    System.out.println("entry frame " + BsonLite.messagePackValue(message.parameters, false));
   check(accepted != null && Boolean.TRUE.equals(BsonLite.boolValue(accepted.parameters, "r")),
       "original requestEnterStory accepted menu" + menu);
   check(frame(reply, "reliableRpcAck") != null, "entry ack menu" + menu);
   check(Integer.valueOf(menu).equals(BsonLite.intValue(profile(), "q7ChapterMenu")),
       "entry committed q7ChapterMenu " + menu);
   check(progress.weekCommit != null && !progress.weekCommit.equals(WEEK) &&
       progress.weekCommit.equals(reload().weekCommit),
       "entry committed and persisted a new week cycle " + menu);
  }

  /**
   * True Gateway negative: the persisted profile has unmet original ending requirements.
   * requestEnterStory must refuse and must not mutate profile or week state.
   */
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
   Integer weekNumBefore = BsonLite.intValue(doc(before, "weeknum"), "w");
   Integer dayBefore = BsonLite.intValue(doc(before, "weeknum"), "d");
   boolean transitionBefore = BsonLite.documentValue(before, "q7WeekTransition") != null;
   List<ProtoLite.EntityMessage> reply = call("requestEnterStory",
       BsonLite.document("i", menu), SEQ.getAndIncrement());
   ProtoLite.EntityMessage refused = frame(reply, "replyEnterStory");
   if (refused == null) for (ProtoLite.EntityMessage message : reply)
    System.out.println("denied frame " + BsonLite.messagePackValue(message.parameters, false));
   check(refused != null && Boolean.FALSE.equals(BsonLite.boolValue(refused.parameters, "r")),
       "original gateway refuses unmet endings menu" + menu);
   byte[] after = profile();
   check(Objects.equals(menuBefore, BsonLite.intValue(after, "q7ChapterMenu")),
       "refused entry leaves q7ChapterMenu unchanged menu" + menu);
   check(Arrays.equals(stdBefore, doc(after, "std")),
       "refused entry leaves route/endings unchanged menu" + menu);
   check(Objects.equals(weekNumBefore, BsonLite.intValue(doc(after, "weeknum"), "w")) &&
       Objects.equals(dayBefore, BsonLite.intValue(doc(after, "weeknum"), "d")),
       "refused entry leaves week/day unchanged menu" + menu);
   check(transitionBefore == (BsonLite.documentValue(after, "q7WeekTransition") != null),
       "refused entry writes no week transition menu" + menu);
   check(Objects.equals(weekBefore, progress.weekCommit) && weekIndexBefore == progress.weekIndex,
       "refused entry leaves week progress unchanged menu" + menu);
   // A second refusal must be byte-stable: original daily bookkeeping reconciles once,
   // never as part of an accepted week entry.
   List<ProtoLite.EntityMessage> again = call("requestEnterStory",
       BsonLite.document("i", menu), SEQ.getAndIncrement());
   ProtoLite.EntityMessage refusedAgain = frame(again, "replyEnterStory");
   check(refusedAgain != null &&
       Boolean.FALSE.equals(BsonLite.boolValue(refusedAgain.parameters, "r")),
       "original gateway refuses unmet endings again menu" + menu);
   check(Arrays.equals(after, profile()),
       "repeated refusal leaves profile bytes unchanged menu" + menu);
  }

  void startAndTrace(int event) throws Exception {
   int startSequence = SEQ.getAndIncrement();
   List<ProtoLite.EntityMessage> start = call("startEvent",
       BsonLite.document("e", event), startSequence);
   ProtoLite.EntityMessage reply = frame(start, "startEventReply");
   check(reply != null && Integer.valueOf(event).equals(BsonLite.intValue(reply.parameters, "e")) &&
       Integer.valueOf(1).equals(BsonLite.intValue(reply.parameters, "r")),
       "start accepted " + event);
   check(progress.processingEvents.contains(event), "processing after start " + event);
   int traceSequence = SEQ.getAndIncrement();
   List<ProtoLite.EntityMessage> trace = call("clientTraceProcessingEvent",
       BsonLite.document("k", "dialog", "d", BsonLite.document("c", event)), traceSequence);
   ProtoLite.EntityMessage done = frame(trace, "completeEventReplyEnd");
   check(done != null && Integer.valueOf(event).equals(BsonLite.intValue(done.parameters, "e")),
       "dialog completion " + event);
   check(progress.completedEvents.contains(event), "completed " + event);
   check(!progress.processingEvents.contains(event), "processing cleared " + event);
  }

  void startOnly(LocalEventEngine eng, int event) throws Exception {
   List<ProtoLite.EntityMessage> start = call(eng, "startEvent",
       BsonLite.document("e", event), SEQ.getAndIncrement());
   ProtoLite.EntityMessage reply = frame(start, "startEventReply");
   if (reply == null || !Integer.valueOf(1).equals(BsonLite.intValue(reply.parameters, "r")))
    for (ProtoLite.EntityMessage message : start)
     System.out.println("start frame " + BsonLite.messagePackValue(message.parameters, false));
   check(reply != null && Integer.valueOf(event).equals(BsonLite.intValue(reply.parameters, "e")) &&
       Integer.valueOf(1).equals(BsonLite.intValue(reply.parameters, "r")),
       "start accepted " + event);
   check(progress.processingEvents.contains(event), "processing after start " + event);
  }

  void traceDialog(LocalEventEngine eng, int event) throws Exception {
   List<ProtoLite.EntityMessage> trace = call(eng, "clientTraceProcessingEvent",
       BsonLite.document("k", "dialog", "d", BsonLite.document("c", event)),
       SEQ.getAndIncrement());
   ProtoLite.EntityMessage done = frame(trace, "completeEventReplyEnd");
   check(done != null && Integer.valueOf(event).equals(BsonLite.intValue(done.parameters, "e")),
       "dialog completion " + event);
   check(progress.completedEvents.contains(event), "completed " + event);
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

 private static boolean locked(byte[] profile, int area) {
  return Boolean.TRUE.equals(BsonLite.boolValue(doc(profile, "q7ChapterLocks"),
      Integer.toString(area)));
 }

 private static boolean receipt(byte[] profile, int event) {
  return Boolean.TRUE.equals(BsonLite.boolValue(doc(profile, "q7ChapterEffects"),
      Integer.toString(event)));
 }

 private static boolean core(byte[] profile, int area) {
  return Boolean.TRUE.equals(BsonLite.boolValue(doc(profile, "q7ChapterCore"),
      Integer.toString(area)));
 }

 private static byte[] apply(Fixture fixture, byte[] profile, int event) {
  LocalResourceEngine.Result result = new LocalResourceEngine.Result(profile);
  fixture.progress.completedEvents.add(event);
  StoryCityPolicy.refresh(result, events, fixture.progress);
  fixture.progress.completedEvents.remove(event);
  return result.profile;
 }

 /** Direct reducer call on a real owned profile; used for one representative event per group. */
 private static byte[] reduce(Fixture fixture, int event) {
  byte[] profile;
  try {
   profile = fixture.profile();
  } catch (IOException error) {
   throw new AssertionError(error);
  }
  LocalResourceEngine.Result result = new LocalResourceEngine.Result(profile);
  fixture.progress.completedEvents.add(event);
  StoryCityPolicy.refresh(result, events, fixture.progress);
  fixture.progress.completedEvents.remove(event);
  return result.profile;
 }

 private static void prepare(String entryRoot) throws Exception {
  if (prepared) return;
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

 /** Original LocalCityProgress Status through reflection (the manager method is not javac-visible). */
 private static int originalStatus(LocalTutorialStore.Progress progress, int area, byte[] profile) {
  try {
   Method method = Class.forName("com.project7.localmanager.LocalCityProgress")
       .getDeclaredMethod("q7OriginalStatus", LocalTutorialStore.Progress.class, int.class,
           byte[].class);
   method.setAccessible(true);
   return ((Integer) method.invoke(null, progress, area, profile)).intValue();
  } catch (ReflectiveOperationException error) {
   throw new AssertionError("LocalCityProgress Status ABI", error);
  }
 }

 /** Carry an already-applied city-effect receipt for a seeded prerequisite event. */
 private static byte[] withReceipt(byte[] profile, int event) {
  byte[] receipts = doc(profile, "q7ChapterEffects");
  List<Object> fields = new ArrayList<>();
  for (String key : BsonLite.keys(receipts)) {
   Boolean value = BsonLite.boolValue(receipts, key);
   if (value != null) {
    fields.add(key);
    fields.add(value);
   }
  }
  fields.add(Integer.toString(event));
  fields.add(Boolean.TRUE);
  return BsonLite.withProfileDocument(profile, "q7ChapterEffects",
      BsonLite.document(fields.toArray()));
 }

 /** Real city-chapter t1 path for 4/23: original Status -> gateway stages -> admission -> win. */
 private static void checkChapterT1(int menu, List<Integer> endings, String route, int[] chain,
                                    int[] gateEvents, int expectedScene, int nextScene) throws Exception {
  try (Fixture fixture = new Fixture(menu, endings, true)) {
   fixture.entry(menu);
   for (int event : chain) fixture.startAndTrace(event);
   byte[] profile = fixture.profile();
   if (route != null) {
    List<Integer> permanent = BsonLite.intArrayValues(doc(profile, "std"), "ed");
    profile = BsonLite.withProfileDocument(profile, "std",
        BsonLite.document("rt", route, "ed", permanent));
    fixture.persist(profile);
   }
   // Original tutorial foundation required by LocalCityProgress area Status.
   fixture.progress.completedEvents.addAll(Arrays.asList(1013, 1043));
   for (int event : gateEvents) {
    fixture.progress.completedEvents.add(event);
    profile = withReceipt(profile, event);
   }
   fixture.persist(profile);
   LocalEventEngine chapterEngine =
       new LocalEventEngine(events, newbees, fixture.progress, 0, profile, true);
   check(originalStatus(fixture.progress, 2, profile) == 1,
       "menu" + menu + " original area2 Status 1");
   byte[] stage = StoryCityPolicy.stages(fixture.progress, 2, profile);
   check(Integer.valueOf(expectedScene).equals(BsonLite.intValue(stage, "cs")),
       "menu" + menu + " promoted area2 cs" + expectedScene);
   check(fixture.stageCs(chapterEngine, 2) == expectedScene,
       "menu" + menu + " gateway getAreaStages cs" + expectedScene);
   fixture.chapterBattleT1(chapterEngine, 2, expectedScene);
   byte[] settledProfile = fixture.profile();
   LocalEventEngine settledEngine =
       new LocalEventEngine(events, newbees, fixture.progress, 0, settledProfile, true);
   int advanced = fixture.stageCs(settledEngine, 2);
   System.out.println("t1 post menu" + menu + " advanced=" + advanced
       + " policyStatus=" + StoryCityPolicy.status(fixture.progress, 2, settledProfile)
       + " origStatus=" + originalStatus(fixture.progress, 2, settledProfile)
       + " state=" + state(settledProfile, 2) + " locked=" + locked(settledProfile, 2)
       + " battle=" + fixture.progress.eventConditions.get("battle")
       + " route=" + BsonLite.stringValue(doc(settledProfile, "std"), "rt")
       + " menu=" + BsonLite.intValue(settledProfile, "q7ChapterMenu"));
   check(advanced == nextScene,
       "menu" + menu + " area2 advances to " + nextScene + " (got " + advanced + ")");
   LocalTutorialStore.Progress loaded = fixture.reload();
   check(loaded.eventConditions.get("battle") != null &&
       loaded.eventConditions.get("battle").contains(expectedScene),
       "menu" + menu + " chapter t1 battle persists");
  }
 }

 public static void main(String[] args) throws Exception {
  assets = new File(args[0]);
  prepare(args[1]);
  for (int menu : SCOPED) check(StoryMainlineEntry.capability(menu),
      "scoped capability menu" + menu);
  for (int menu : new int[]{25})
   check(StoryCityPolicy.supports(menu), "v55 entry closure support menu" + menu);
  for (int menu : SCOPED) check(StoryCityPolicy.supports(menu), "scoped support menu" + menu);

  int[][] initEndings = {{1}, {28}, {63, 39}, {2}, {2}, {114}, {99}, {99}};
  int[][] chains = {{540, 541, 542, 543, 544, 545, 546, 547}, {436, 437, 438, 1230},
                    {1398, 1375, 1396, 1395}, {575, 576, 577, 578},
                    {1640, 1641, 1642, 1643}, {1675},
                    {1690, 1691, 1692, 1693, 1809}, {1812, 1813, 1814, 1815}};
  int[] effectEvents = {547, 438, 1395, 578, 1643, 0, 1809, 1815};
  for (int index = 0; index < SCOPED.length; index++) {
   int menu = SCOPED[index];
   List<Integer> endings = new ArrayList<>();
   for (int ending : initEndings[index]) endings.add(ending);
   try (Fixture fixture = new Fixture(menu, endings, true)) {
    byte[] before = fixture.profile();
    check(LocalWeekEngine.canEnter(before, weeks, menu), "canEnter menu" + menu);
    check(StoryMainlineEntry.entryReady(menu, before, fixture.progress, weeks),
        "entryReady pre-entry menu" + menu);
    byte[] wrong = BsonLite.withProfileDocument(before, "std",
        BsonLite.document("rt", "1", "ed", Collections.singletonList(999999)));
    check(!LocalWeekEngine.canEnter(wrong, weeks, menu), "canEnter negative menu" + menu);
    check(!StoryMainlineEntry.entryReady(menu, wrong, fixture.progress, weeks),
        "entryReady negative menu" + menu);
    try (Fixture denied = new Fixture(menu, Collections.singletonList(999999), true)) {
     denied.deniedEntry(menu);
    }
    fixture.entry(menu);
    byte[] profile = fixture.profile();
    check(StoryMainlineEntry.entryReady(menu, profile, fixture.progress, weeks),
        "entryReady post-entry menu" + menu);
    check(StoryCityPolicy.owns(profile) && StoryMainlineEntry.cityOwns(profile),
        "scoped city ownership menu" + menu);
    for (int event : chains[index]) fixture.startAndTrace(event);
    profile = fixture.profile();
    if (effectEvents[index] != 0)
     check(receipt(profile, effectEvents[index]), "init-chain receipt " + effectEvents[index]);
    if (menu == 4) {
     check(state(profile, 1) == 0 && state(profile, 2) == 1,
         "menu4 areaFree[1]/areaFight[2]");
    } else if (menu == 23) {
     for (int area = 2; area <= 6; area++)
      check(state(profile, area) == 1, "menu23 areaFight[" + area + "]");
     check(state(profile, 7) == 0 && state(profile, 8) == 0, "menu23 areaFree[7,8]");
    }
    check(fixture.reload().weekCommit.equals(fixture.progress.weekCommit),
        "reload keeps week menu" + menu);
   }
  }

  // 24 init chain: 578 is areaFight[5] + areaLock[2].
  try (Fixture fixture = new Fixture(24, Collections.singletonList(2), true)) {
   fixture.entry(24);
   for (int event : new int[]{575, 576, 577, 578}) fixture.startAndTrace(event);
   byte[] profile = fixture.profile();
   check(state(profile, 5) == 1, "areaFight[5] state");
   check(locked(profile, 2), "areaLock[2] lock");
   check(receipt(profile, 578), "area receipt 578");
  }

  // 31 init chain effect.
  try (Fixture fixture = new Fixture(31, Collections.singletonList(99), true)) {
   fixture.entry(31);
   for (int event : new int[]{1812, 1813, 1814, 1815}) fixture.startAndTrace(event);
   byte[] profile = fixture.profile();
   check(state(profile, 2) == 0, "areaFree[2] state");
   check(receipt(profile, 1815), "area receipt 1815");
  }

  // 29: init chain has no effect; its route event 1678 is reduced directly on the owned profile.
  try (Fixture fixture = new Fixture(29, Collections.singletonList(114), true)) {
   fixture.entry(29);
   fixture.startAndTrace(1675);
   byte[] profile = reduce(fixture, 1678);
   check(state(profile, 6) == 0, "menu29 areaFree[6]");
   check(locked(profile, 1) && state(profile, 1) == -1, "menu29 areaLock[1] without fight state");
   check(state(profile, 2) == 1, "menu29 areaFight[2]");
   check(receipt(profile, 1678), "menu29 receipt 1678");
  }

  // 17/27/30 init-chain effects (also entry-proven by the loop above).
  try (Fixture fixture = new Fixture(17, Collections.singletonList(28), true)) {
   fixture.entry(17);
   for (int event : new int[]{436, 437, 438, 1230}) fixture.startAndTrace(event);
   byte[] profile = fixture.profile();
   check(state(profile, 1) == 0 && receipt(profile, 438), "menu17 areaFree[1]");
  }
  try (Fixture fixture = new Fixture(27, Collections.singletonList(2), true)) {
   fixture.entry(27);
   for (int event : new int[]{1640, 1641, 1642, 1643}) fixture.startAndTrace(event);
   byte[] profile = fixture.profile();
   check(state(profile, 1) == 0 && state(profile, 6) == 1 && receipt(profile, 1643),
       "menu27 areaFree/areaFight");
  }
  try (Fixture fixture = new Fixture(30, Collections.singletonList(99), true)) {
   fixture.entry(30);
   for (int event : new int[]{1690, 1691, 1692, 1693, 1809}) fixture.startAndTrace(event);
   byte[] profile = fixture.profile();
   check(state(profile, 1) == 0 && state(profile, 2) == 1 && receipt(profile, 1809),
       "menu30 areaFree/areaFight");
  }

  // Hero type delegates to the original fixed owner; a second refresh is byte-idempotent.
  try (Fixture fixture = new Fixture(24, Collections.singletonList(2), true)) {
   fixture.entry(24);
   byte[] profile = fixture.profile();
   LocalResourceEngine.Result result = new LocalResourceEngine.Result(profile);
   fixture.progress.completedEvents.add(6401);
   StoryCityPolicy.refresh(result, events, fixture.progress);
   fixture.progress.completedEvents.remove(6401);
   byte[] after = result.profile;
   check(receipt(after, 6401), "hero effect receipt 6401");
   check(BsonLite.intArrayValues(doc(after, "heromgr"), "c").contains(114),
       "cineLockHeroes[114] owned hero");
   boolean heroReply = false;
   for (LocalResourceEngine.Reply reply : result.replies)
    heroReply |= "cineLockHeroes".equals(reply.method);
   check(heroReply, "hero effect reply");
   LocalResourceEngine.Result again = new LocalResourceEngine.Result(after);
   fixture.progress.completedEvents.add(6401);
   StoryCityPolicy.refresh(again, events, fixture.progress);
   fixture.progress.completedEvents.remove(6401);
   check(Arrays.equals(after, again.profile), "hero receipt replay idempotent");

   // Unknown and friendly fields must reject without publishing a candidate.
   byte[] unknownDoc = BsonLite.document("areaStrike", Arrays.asList(3));
   events.cityEffects.put(1000001, unknownDoc);
   fixture.progress.completedEvents.add(1000001);
   LocalResourceEngine.Result rejected = new LocalResourceEngine.Result(after);
   try {
    StoryCityPolicy.refresh(rejected, events, fixture.progress);
    throw new AssertionError("unknown effect accepted");
   } catch (IllegalArgumentException expected) {
    check(Arrays.equals(after, rejected.profile), "unknown effect publishes nothing");
   }
   fixture.progress.completedEvents.remove(1000001);
   events.cityEffects.remove(1000001);

   byte[] friendlyDoc = BsonLite.document("friendly", BsonLite.document("14", 10));
   events.cityEffects.put(1000002, friendlyDoc);
   fixture.progress.completedEvents.add(1000002);
   LocalResourceEngine.Result friendly = new LocalResourceEngine.Result(after);
   try {
    StoryCityPolicy.refresh(friendly, events, fixture.progress);
    throw new AssertionError("friendly effect accepted on the scoped path");
   } catch (IllegalArgumentException expected) {
    check(Arrays.equals(after, friendly.profile), "friendly effect publishes nothing");
   }
   fixture.progress.completedEvents.remove(1000002);
   events.cityEffects.remove(1000002);
  }

  // Original event1331 areaFall and event3017 areaCR7 projection/semantics + save/reload.
  try (Fixture fixture = new Fixture(24, Collections.singletonList(2), true)) {
   fixture.entry(24);
   byte[] profile = apply(fixture, fixture.profile(), 1331);
   for (int area : new int[]{1, 2, 4, 6, 9}) check(state(profile, area) == 2,
       "areaFall[2] area" + area);
   check(state(profile, 8) == 0 && state(profile, 5) == 1, "1331 free/fight preserved");
   check(!core(profile, 1) && receipt(profile, 1331), "1331 fall receipt no core");
   fixture.persist(profile);
   byte[] loaded = fixture.store.load(ACCOUNT, fixture.progress);
   check(state(loaded, 4) == 2 && receipt(loaded, 1331), "1331 fall save/reload");

   profile = apply(fixture, loaded, 3017);
   check(state(profile, 1) == 4 && state(profile, 2) == 4, "areaCR7 status4 after fall2");
   check(core(profile, 1) && core(profile, 2), "areaCR7 core true");
   check(state(profile, 6) == 1 && state(profile, 3) == 0 && state(profile, 4) == 0 &&
       state(profile, 5) == 0, "3017 areaFight/Free");
   profile = apply(fixture, profile, 3020);
   check(state(profile, 3) == 3 && core(profile, 3), "areaCR7 status3 when not fall2");
   fixture.persist(profile);
   loaded = fixture.store.load(ACCOUNT, fixture.progress);
   check(core(loaded, 1) && core(loaded, 3) && state(loaded, 3) == 3 &&
       receipt(loaded, 3020), "CR7 save/reload");

  }

  try (Fixture fixture = new Fixture(24, Collections.singletonList(2), true)) {
   fixture.entry(24);
   byte[] profile = fixture.profile();
   events.cityEffects.put(1331, BsonLite.document("areaFall", Arrays.asList(9999)));
   LocalResourceEngine.Result bad = new LocalResourceEngine.Result(profile);
   fixture.progress.completedEvents.add(1331);
   try {
    StoryCityPolicy.refresh(bad, events, fixture.progress);
    throw new AssertionError("unknown areaFall accepted");
   } catch (IllegalArgumentException expected) {
    check(Arrays.equals(profile, bad.profile), "unknown areaFall publishes nothing");
   }
   fixture.progress.completedEvents.remove(1331);
   events.cityEffects.put(1331, BsonLite.document("areaFall", Arrays.asList(1, 1)));
   bad = new LocalResourceEngine.Result(profile);
   fixture.progress.completedEvents.add(1331);
   try {
    StoryCityPolicy.refresh(bad, events, fixture.progress);
    throw new AssertionError("duplicate areaFall accepted");
   } catch (IllegalArgumentException expected) {
    check(Arrays.equals(profile, bad.profile), "duplicate areaFall publishes nothing");
   }
   fixture.progress.completedEvents.remove(1331);
  }

  // Menu23 host-simulated event battle. SYNTHETIC PREREQUISITE FIXTURE, not a natural
  // route: the host injects route 25-6, day 7, owned hero 102 and completed 7596 to make
  // the original trigger scan offer 8753. startEvent opens the original gate; t2/s462
  // admission and the original finish write the battle trace; a host-simulated win plus
  // dialog trace completes it. No native battle and no full route replay are claimed.
  try (Fixture fixture = new Fixture(23, Arrays.asList(63, 39), true)) {
   fixture.entry(23);
   for (int event : new int[]{1398, 1375, 1396, 1395}) fixture.startAndTrace(event);
   byte[] patched = fixture.profile();
   List<Integer> permanentEndings = BsonLite.intArrayValues(doc(patched, "std"), "ed");
   patched = BsonLite.withProfileDocument(patched, "std",
       BsonLite.document("rt", "25-6", "ed", permanentEndings));
   Integer week = BsonLite.intValue(doc(patched, "weeknum"), "w");
   patched = BsonLite.withProfileDocument(patched, "weeknum",
       BsonLite.document("w", week == null ? 8 : week.intValue(), "d", 7, "av", 60));
   patched = BsonLite.withHero(patched, 102);
   fixture.persist(patched);
   LocalEventEngine battleEngine =
       new LocalEventEngine(events, newbees, fixture.progress, 0, patched, true);
   battleEngine.updateClientOperation(1);
   fixture.progress.completedEvents.add(7596);
   List<ProtoLite.EntityMessage> pull = fixture.call(battleEngine, "pullEvents",
       BsonLite.EMPTY_DOCUMENT, SEQ.getAndIncrement());
   check(frame(pull, "pullEventsReply") != null, "menu23 original pullEvents reply");
   check(fixture.progress.availableEvents.contains(8753), "menu23 trigger8753 offered");

   fixture.startOnly(battleEngine, 8753);
   List<ProtoLite.EntityMessage> admitted = fixture.call(battleEngine, "combatOfflineRequest",
       BsonLite.document("t", 2, "s", 462, "h", Arrays.asList(102),
           "d", BsonLite.EMPTY_DOCUMENT), SEQ.getAndIncrement());
   ProtoLite.EntityMessage admittedReply = frame(admitted, "combatOfflineReply");
   check(admittedReply != null &&
       Integer.valueOf(2).equals(BsonLite.intValue(admittedReply.parameters, "t")) &&
       Integer.valueOf(462).equals(BsonLite.intValue(admittedReply.parameters, "s")) &&
       BsonLite.stringValue(admittedReply.parameters, "f") != null &&
       !BsonLite.stringValue(admittedReply.parameters, "f").isEmpty(),
       "menu23 event battle admission type2/scene462");
   List<ProtoLite.EntityMessage> won = fixture.finish(battleEngine,
       BsonLite.document("t", 2, "s", 462, "h", Arrays.asList(102),
           "x", Arrays.asList(102), "w", 1));
   check(frame(won, "combatOfflineReward") != null, "menu23 event battle reward reply");
   check(fixture.progress.eventConditions.get("battle") != null &&
       fixture.progress.eventConditions.get("battle").contains(462),
       "menu23 original battle462 trace");
   check(fixture.progress.processingEvents.contains(8753),
       "menu23 event waits for its dialog after battle");
   fixture.traceDialog(battleEngine, 8753);
   check(fixture.progress.eventCompletions.get(8753) == 1, "menu23 completion count 1");
   LocalTutorialStore.Progress loaded = fixture.reload();
   check(loaded.completedEvents.contains(8753) &&
       loaded.eventConditions.get("battle") != null &&
       loaded.eventConditions.get("battle").contains(462),
       "menu23 battle completion persisted after reload");
  }

  // Real city-chapter t1 settlement for 4/23 (no event-battle substitution).
  checkChapterT1(4, Collections.singletonList(1), "5",
      new int[]{540, 541, 542, 543, 544, 545, 546, 547}, new int[]{5052}, 22007, 22008);
  checkChapterT1(23, Arrays.asList(63, 39), null,
      new int[]{1398, 1375, 1396, 1395}, new int[]{}, 1121, 1122);

  System.out.println("PASS " + checks +
      " v48 data-closed menus + typed city effects: scoped 4/17/23/24/27/29/30/31 entry,"
      + " event battle462, hero delegation");
 }
}
