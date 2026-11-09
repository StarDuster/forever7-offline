package com.project7.localmanager;

import android.content.*;
import android.content.res.*;
import java.io.*;
import java.lang.reflect.*;
import java.nio.*;
import java.nio.file.*;
import java.util.*;

/**
 * Read-only host for the v49 chapter-absent / trigger-gap classification.
 *
 * <p>Proves on the published stage assets that (a) menus without
 * {@code chapter_mission_data} family rows still use the original
 * {@link LocalCityProgress} default stage projection through the Bridge miss
 * path, while the entry gate stays {@link LocalStoryEntryPolicy}; and (b) every
 * v49 flagged auto-trigger gap is an unreleased event with no {@code @trigger}
 * row, which the original engine cannot expose. Positive controls are a real
 * promoted chapter route and a released auto event with a real trigger row.
 * No D8/APK/native and no production writes.</p>
 */
public final class StoryMainlineFallbackHost {
 private static final String ACCOUNT = "host_mainline_fallback";
 private static final String WEEK = "fbl00000000000000000000";
 private static int checks;
 private static File assets;
 private static LocalEventCatalog events;
 private static LocalWeekCatalog weeks;
 private static LocalNewbeeCatalog newbees;
 private static LocalCombatCatalog combat;
 private static Method RAW_RELIABLE;
 private static Method TRIGGER_MATCHES;
 private static Method TRIGGER_BLOCKER;
 private static Method REEVALUATE;
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

  Fixture(String route, List<Integer> endings, int menu, int week, int day, boolean completed)
      throws Exception {
   root = Files.createTempDirectory("mainline-fallback-");
   Files.createDirectories(root.resolve("profiles"));
   profileFile = root.resolve("profiles/" + ACCOUNT + ".bson");
   byte[] profile = BsonLite.withAccountIdentity(
       Files.readAllBytes(new File(assets, "new_player.bson").toPath()), ACCOUNT, 902500 + menu);
   profile = BsonLite.withProfileDocument(profile, "weeknum",
       BsonLite.document("w", week, "d", day, "av", 60));
   profile = BsonLite.withProfileDocument(profile, "std",
       BsonLite.document("rt", route, "ed", endings, "ff", false));
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
   progress = completed ? LocalTutorialStore.Progress.completed()
       : LocalTutorialStore.Progress.fresh();
   progress.weekIndex = week;
   progress.weekCommit = WEEK;
   progress.inEmergency = false;
   progress.initPrologue = false;
   progress.patrolActions = 60;
   progress.processingEvents.clear();
   progress.processingNewbees.clear();
   engine = new LocalEventEngine(events, newbees, progress, 0, profile, true);
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

  byte[] profile() throws IOException {
   return Files.readAllBytes(profileFile);
  }

  void persist(byte[] profile) throws IOException {
   Files.write(profileFile, profile);
  }

  LocalTutorialStore.Progress reload() throws Exception {
   return tutorials.load(ACCOUNT);
  }

  public void close() throws Exception {
   gateway.close();
   try (java.util.stream.Stream<Path> stream = Files.walk(root)) {
    for (Path path : (Iterable<Path>) stream.sorted(Comparator.reverseOrder())::iterator)
     Files.delete(path);
   }
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
  TRIGGER_MATCHES = LocalEventEngine.class.getDeclaredMethod("triggerMatches",
      LocalEventCatalog.Trigger.class);
  TRIGGER_MATCHES.setAccessible(true);
  TRIGGER_BLOCKER = LocalEventEngine.class.getDeclaredMethod("triggerBlocker",
      LocalEventCatalog.Trigger.class, int.class, int.class);
  TRIGGER_BLOCKER.setAccessible(true);
  REEVALUATE = LocalEventEngine.class.getDeclaredMethod("reevaluateLifecycle");
  REEVALUATE.setAccessible(true);
 }

 private static boolean matches(LocalEventEngine engine, LocalEventCatalog.Trigger trigger)
     throws Exception {
  return (Boolean) TRIGGER_MATCHES.invoke(engine, trigger);
 }

 private static boolean unblocked(LocalEventEngine engine, LocalEventCatalog.Trigger trigger)
     throws Exception {
  return TRIGGER_BLOCKER.invoke(engine, trigger, 0, 0) == null;
 }

 private static void rescan(LocalEventEngine engine) throws Exception {
  REEVALUATE.invoke(engine);
 }

 private static boolean triggerRow(int event) {
  return events.trigger(event) != null;
 }

 private static void checkChapterClassification() {
  int[] absent = {1, 7, 8, 14, 15, 16, 18, 21, 26};
  for (int menu : absent) {
   check(!StoryMainlineEntry.capability(menu), "chapter-absent menu not packaged " + menu);
   check(!StoryMissionBridge.chapterReady(2, "1"), "no invented family 1 chapter");
  }
  // Positive promoted control and every absent family's route key.
  check(StoryMissionBridge.chapterReady(2, "31-1"), "promoted chapter 31-1");
  check(StoryMissionBridge.chapterReady(1, "5"), "promoted chapter route5 area1");
  String[] families = {"1", "8", "8-1", "9-1", "15-1", "16-1", "17-1", "19-1", "22-1", "29-1"};
  for (String route : families)
   check(!StoryMissionBridge.chapterReady(2, route), "absent family route " + route);
  check(LocalStoryEntryPolicy.supports(1), "original SUPPORTED keeps menu1");
  check(!LocalStoryEntryPolicy.supports(7), "original SUPPORTED excludes menu7");
  check(StoryCityPolicy.supports(1), "original allowlist keeps menu1");
  for (int menu : new int[]{7, 8, 14, 15, 16, 18, 21, 26})
   check(!StoryCityPolicy.supports(menu), "policy closed menu" + menu);
  check(StoryCityPolicy.supports(17) && StoryCityPolicy.supports(28),
      "proven menu support control");
 }

 private static void clearPending(Fixture fixture) throws Exception {
  fixture.call("getAreaStagesRequest", BsonLite.document("aid", 2), SEQ.getAndIncrement());
  byte[] pending = doc(fixture.profile(), "q7StoryPending");
  if (!BsonLite.keys(pending).isEmpty()) {
   LocalResourceEngine.Result ack = fixture.store.updateServices(ACCOUNT, "q7AckStoryDelivery",
       BsonLite.document("s", pending), fixture.progress);
   check(BsonLite.keys(doc(ack.profile, "q7StoryPending")).isEmpty(),
       "prior delivery acknowledged before entry");
  }
 }

 private static void checkMenu1Positive() throws Exception {
  try (Fixture fixture = new Fixture("1", Collections.emptyList(), 1, 8, 0, true)) {
   clearPending(fixture);
   byte[] before = fixture.profile();
   check(LocalWeekEngine.canEnter(before, weeks, 1), "menu1 canEnter (no endings)");
   // The original default chapter/stage projection is already served before entry.
   // 1013 + 1043 are the original fresh-week gates that make normal area2 FIGHT.
   fixture.progress.completedEvents.add(1013);
   fixture.progress.completedEvents.add(1043);
   for (int area : new int[]{2, 5}) {
    List<ProtoLite.EntityMessage> stagesReply = fixture.call("getAreaStagesRequest",
        BsonLite.document("aid", area), SEQ.getAndIncrement());
    ProtoLite.EntityMessage message = frame(stagesReply, "get_area_stages_reply");
    check(message != null, "pre-entry area stages reply " + area);
    byte[] stages = BsonLite.documentValue(message.parameters, "st");
    if (stages == null) stages = BsonLite.EMPTY_DOCUMENT;
    byte[] original = LocalCityProgress.stages(fixture.progress, area, fixture.profile());
    check(Arrays.equals(stages, original), "pre-entry default stages area " + area);
    if (area == 2) {
     check(LocalCityProgress.status(fixture.progress, area, fixture.profile()) == 1,
         "default status FIGHT area2");
     check(Integer.valueOf(1101).equals(BsonLite.intValue(stages, "cs")),
         "default cs1101 area2");
     check(BsonLite.keys(BsonLite.arrayValue(stages, "sl")).size() == 6,
         "default six scene groups area2");
    } else {
     check(LocalCityProgress.status(fixture.progress, area, fixture.profile()) == 2,
         "area5 stays original FALL");
     check(BsonLite.keys(stages).isEmpty(), "area5 original empty projection");
    }
   }
   check(!StoryMainlineEntry.entryReady(1, before, fixture.progress, weeks),
       "menu1 is not in the packaged proven set");
   int sequence = SEQ.getAndIncrement();
   List<ProtoLite.EntityMessage> reply = fixture.call("requestEnterStory",
       BsonLite.document("i", 1), sequence);
   if (!accepted(reply, "replyEnterStory"))
    for (ProtoLite.EntityMessage message : reply)
     System.out.println("menu1 frame " + BsonLite.messagePackValue(message.parameters, false));
   check(accepted(reply, "replyEnterStory"), "original requestEnterStory accepted menu1");
   check(frame(reply, "reliableRpcAck") != null, "menu1 reliable ack");
   byte[] after = fixture.profile();
   check(Integer.valueOf(1).equals(BsonLite.intValue(after, "q7ChapterMenu")),
       "menu1 committed q7ChapterMenu");
   check(fixture.progress.weekCommit != null && !fixture.progress.weekCommit.equals(WEEK),
       "menu1 committed a new week");
   check(fixture.progress.weekCommit.equals(fixture.reload().weekCommit),
       "menu1 week persisted");

   // Area 2 and 5 are the menu1 areaUnlock targets; no family table row exists.
   for (int area : new int[]{2, 5}) {
    List<ProtoLite.EntityMessage> stagesReply = fixture.call("getAreaStagesRequest",
        BsonLite.document("aid", area), SEQ.getAndIncrement());
    ProtoLite.EntityMessage message = frame(stagesReply, "get_area_stages_reply");
    check(message != null, "area stages reply " + area);
    check(Integer.valueOf(area).equals(BsonLite.intValue(message.parameters, "ai")),
        "area stages ai " + area);
    byte[] stages = BsonLite.documentValue(message.parameters, "st");
    if (stages == null) stages = BsonLite.EMPTY_DOCUMENT;
    byte[] original = LocalCityProgress.stages(fixture.progress, area, fixture.profile());
    byte[] bridge = StoryMissionBridge.stages(fixture.progress, area, fixture.profile());
    check(Arrays.equals(stages, original), "gateway default stages area " + area);
    check(Arrays.equals(bridge, original), "bridge miss delegates area " + area);

   }

   // Save/reload: the committed week and default projection survive a reload.
   fixture.tutorials.save(ACCOUNT, fixture.progress);
   check(fixture.reload().weekCommit.equals(fixture.progress.weekCommit),
       "menu1 reload keeps week");
   byte[] persisted = fixture.profile();
   check(Arrays.equals(persisted, after), "menu1 profile image preserved across reload");
   check(Integer.valueOf(8).equals(BsonLite.intValue(
       BsonLite.documentValue(persisted, "weeknum"), "w")),
       "menu1 persisted week num");
  }
 }

 private static void checkMenu7Negative() throws Exception {
  try (Fixture fixture = new Fixture("8", Arrays.asList(19, 20, 21), 7, 8, 0, true)) {
   clearPending(fixture);
   byte[] before = fixture.profile();
   check(LocalWeekEngine.canEnter(before, weeks, 7), "menu7 endings satisfy canEnter");
   check(!StoryCityPolicy.supports(7), "menu7 not in original allowlist or proven set");
   int sequence = SEQ.getAndIncrement();
   boolean threw = false;
   List<ProtoLite.EntityMessage> reply = Collections.emptyList();
   try {
    reply = fixture.call("requestEnterStory", BsonLite.document("i", 7), sequence);
   } catch (IllegalArgumentException expected) {
    threw = true;
   }
   if (!threw)
    check(!accepted(reply, "replyEnterStory"), "menu7 requestEnterStory not accepted");
   check(Integer.valueOf(1).equals(BsonLite.intValue(fixture.profile(), "q7ChapterMenu")),
       "menu7 leaves q7ChapterMenu untouched");
   check(WEEK.equals(fixture.progress.weekCommit), "menu7 leaves week commit untouched");
   check(WEEK.equals(fixture.reload().weekCommit), "menu7 reload keeps week");

   // Missing family rows do not corrupt the default projection.
   List<ProtoLite.EntityMessage> stagesReply = fixture.call("getAreaStagesRequest",
       BsonLite.document("aid", 1), SEQ.getAndIncrement());
   ProtoLite.EntityMessage message = frame(stagesReply, "get_area_stages_reply");
   check(message != null, "menu7 area1 stages reply");
   byte[] stages = BsonLite.documentValue(message.parameters, "st");
   if (stages == null) stages = BsonLite.EMPTY_DOCUMENT;
   check(Arrays.equals(stages, LocalCityProgress.stages(fixture.progress, 1, fixture.profile())),
       "menu7 default projection unchanged");
  }
 }

 private static int[] positiveTrigger() throws Exception {
  // Real released auto rows for menu8's family (routes 9-1..9-3). The first
  // engine scan can leave inEmergency latched from the shipped fresh progress;
  // a second real scan settles the lifecycle before matching.
  int[] candidates = {3177, 3178, 4042, 5081, 6102, 6106, 7110, 7112};
  String[] routes = {"9-1", "9-2", "9-3"};
  for (int event : candidates) {
   LocalEventCatalog.Trigger trigger = events.trigger(event);
   if (trigger == null) continue;
   for (String route : routes)
    for (int week = 0; week <= 3; week++)
     for (int day = 0; day <= 7; day++) {
      try (Fixture fixture = new Fixture(route, Collections.emptyList(), 8, week, day, false)) {
       rescan(fixture.engine);
       rescan(fixture.engine);
       if (!matches(fixture.engine, trigger) || !unblocked(fixture.engine, trigger)) continue;
       rescan(fixture.engine);
       if (!fixture.engine.availableEvents().contains(event)) continue;
       check(triggerRow(event), "positive row exists " + event);
       int[] found = {event, week, day};
       fixture.progress.weekIndex = week;
       fixture.tutorials.save(ACCOUNT, fixture.progress);
       LocalTutorialStore.Progress reloaded = fixture.reload();
       byte[] profile = fixture.profile();
       LocalEventCatalog.Trigger saved = events.trigger(event);
       LocalEventEngine engine = new LocalEventEngine(events, newbees, reloaded, 0, profile, true);
       rescan(engine);
       rescan(engine);
       check(matches(engine, saved) && unblocked(engine, saved), "reload matches " + event);
       check(engine.availableEvents().contains(event), "reload keeps positive " + event);
       for (int gap : new int[]{7115, 1010103, 1625, 7224, 1435}) {
        check(events.get(gap) != null && events.get(gap).autoTrigger,
            "gap auto event " + gap);
        check(!events.get(gap).release, "gap event unreleased " + gap);
        check(events.trigger(gap) == null, "gap event rowless " + gap);
        check(!engine.availableEvents().contains(gap), "gap stays unavailable " + gap);
       }
       return found;
      }
     }
  }
  throw new AssertionError("FAIL: no released menu8 auto trigger could be exposed");
 }

 public static void main(String[] args) throws Exception {
  assets = new File(args[0]);
  prepare(args[1]);
  checkChapterClassification();
  checkMenu1Positive();
  checkMenu7Negative();
  int[] positive = positiveTrigger();
  // Representative negatives across the other gap menus at the same real engine.
  for (int event : new int[]{1010103, 1625, 7224, 1435}) {
   check(events.get(event) != null && events.get(event).autoTrigger, "representative auto " + event);
   check(!events.get(event).release, "representative unreleased " + event);
   check(events.trigger(event) == null, "representative rowless " + event);
  }
  System.out.println("PASS " + checks + " fallback classification: menu1 allowlist+default stages, "
      + "menu7 closed/no invented chapter, released trigger " + positive[0] + " week " + positive[1]
      + " day " + positive[2] + ", 5 unreleased rowless gaps, save/reload");
 }
}
