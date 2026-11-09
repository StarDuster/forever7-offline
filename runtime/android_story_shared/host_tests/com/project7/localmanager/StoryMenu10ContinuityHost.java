package com.project7.localmanager;

import android.content.*;
import android.content.res.*;
import java.io.*;
import java.lang.reflect.*;
import java.nio.*;
import java.nio.file.*;
import java.util.*;

/**
 * v43 menu10 continuity on the frozen production classes.
 *
 * <p>Initial state is a consistent post-ending save, not a menu10 replay:
 * ending 30's original ending event 8310 (weeks.tsv) supplies std.ed=[30] and
 * CG 159, q7EndingEvents 8310, baseline [8310], q7WeekCgBaseline [159]. The
 * tutorial foundation 1013/1043 is retained by the original week reset. The
 * prior ending's one-shot syncAllNote delivery is consumed with the original
 * LocalProfileStore q7AckStoryDelivery path before entry. No current menu10
 * event (477/478/479/1129/480/1140/1141) is seeded.</p>
 *
 * <p>Area 3 is ordinary city state, not story state: the area-2 city battle
 * trace 1106 is cleared in the current week, so the original
 * LocalCityProgress.status and the original get_all_area_info wire both report
 * area 3 status 1. The host reads that status from the profile/wire and builds
 * the original client focus condition from it; it does not hard-code "3:1"
 * before the profile agrees.</p>
 *
 * <p>requestEnterStory uses the original client {i,o} payload. startEvent and
 * clientTraceProcessingEvent are the original event RPCs. q7CompleteUiEvent is
 * the existing Project7 client-compat RPC for UI-only events (1141/1140), not
 * an original-client RPC. Event 1141 (CG_OR 159/160/161 + route 10-6) then
 * makes LocalAlanCityEngine.active and selector320 visible; admission, loss,
 * retry, win, 1132 dialog and 1133-1136 continuation are all real gateway
 * traffic on the same profile.</p>
 */
public final class StoryMenu10ContinuityHost {
 private static final String ACCOUNT = "host_menu10_continuity";
 private static final String WEEK = "continuity0000000000";
 private static final int[] FOUNDATION = {1013, 1043};
 private static int checks;
 private static File assets;
 private static LocalEventCatalog events;
 private static LocalNewbeeCatalog newbees;
 private static LocalCombatCatalog combat;
 private static LocalWeekCatalog weeks;
 private static boolean prepared;
 private static Method RAW_RELIABLE, RAW_FINISH;
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

 private static byte[] fields(byte[] value) { return value == null ? BsonLite.EMPTY_DOCUMENT : value; }

 private static List<String> keys(byte[] value) { return BsonLite.keys(fields(value)); }

 private static byte[] md5(String value) {
  return RequestEventCatalog.hash("MD5", value.getBytes(java.nio.charset.StandardCharsets.UTF_8));
 }

 private static List<ProtoLite.EntityMessage> frames(byte[] wire) throws IOException {
  List<ProtoLite.EntityMessage> out = new ArrayList<>();
  ByteBuffer buffer = ByteBuffer.wrap(wire).order(ByteOrder.LITTLE_ENDIAN);
  while (buffer.hasRemaining()) {
   int length = buffer.getInt();
   if (buffer.getShort() != 5) throw new AssertionError("FAIL: opcode5 frame");
   byte[] data = new byte[length - 2];
   buffer.get(data);
   out.add(ProtoLite.parseEntityMessage(data));
  }
  return out;
 }

 private static ProtoLite.EntityMessage frame(List<ProtoLite.EntityMessage> frames, String method) {
  byte[] digest = md5(method);
  for (ProtoLite.EntityMessage frame : frames)
   if (Arrays.equals(frame.methodMd5, digest)) return frame;
  return null;
 }

 private static byte[] entryProfile(String account) throws IOException {
  byte[] profile = BsonLite.withAccountIdentity(
      Files.readAllBytes(new File(assets, "new_player.bson").toPath()), account, 900911);
  profile = BsonLite.withProfileDocument(profile, "weeknum",
      BsonLite.document("w", 8, "d", 0, "av", 60));
  // Original weeks.tsv row: ending 8310 -> ending 30, CG 159.
  profile = BsonLite.withProfileDocument(profile, "std",
      BsonLite.document("rt", "1", "ed", Arrays.asList(30)));
  profile = BsonLite.withProfileInt(profile, "q7ChapterMenu", 1);
  profile = BsonLite.withProfileArray(profile, "q7WeekEventBaseline", Arrays.asList(8310));
  profile = BsonLite.withProfileArray(profile, "q7WeekCgBaseline", Arrays.asList(159));
  profile = BsonLite.withProfileArray(profile, "cgs", Arrays.asList(159));
  profile = BsonLite.withProfileDocument(profile, "q7EndingEvents",
      BsonLite.document("8310", true));
  profile = BsonLite.withProfileDocument(profile, "city", BsonLite.document("av", 60));
  byte[] inventory = BsonLite.documentValue(profile, "inv");
  if (inventory == null) inventory = BsonLite.EMPTY_DOCUMENT;
  inventory = BsonLite.withProfileArray(inventory, "items",
      Arrays.asList(BsonLite.document("i", 345, "w", 1, "u", "0123456789abcdef01234567")));
  profile = BsonLite.withProfileDocument(profile, "inv", inventory);
  for (int hero : new int[]{135, 136, 137}) profile = BsonLite.withHero(profile, hero);
  return profile;
 }

 private static final class Fixture implements AutoCloseable {
  final Path root, profileFile;
  final LocalProfileStore store;
  final LocalTutorialStore tutorials;
  final LocalTutorialStore.Progress progress;
  final LocalEventEngine engine;
  final LocalGatewayServer gateway;
  final Set<Integer> reliableSequences = new LinkedHashSet<>();

  Fixture() throws Exception {
   root = Files.createTempDirectory("menu10-continuity-");
   Files.createDirectories(root.resolve("profiles"));
   profileFile = root.resolve("profiles/" + ACCOUNT + ".bson");
   Files.write(profileFile, entryProfile(ACCOUNT));
   Context context = new Context(root.toFile(), new AssetManager(assets));
   store = new LocalProfileStore(context);
   tutorials = new LocalTutorialStore(context);
   progress = LocalTutorialStore.Progress.completed();
   for (int event : FOUNDATION) {
    progress.completedEvents.add(event);
    progress.eventCompletions.put(event, 1);
    progress.eventDays.put(event, "7:0");
   }
   progress.weekIndex = 8;
   progress.weekCommit = WEEK;
   progress.initPrologue = false;
   progress.inEmergency = false;
   progress.patrolActions = 60;
   progress.processingEvents.clear();
   progress.processingNewbees.clear();
   tutorials.save(ACCOUNT, progress);
   engine = new LocalEventEngine(events, newbees, progress, 0,
       Files.readAllBytes(profileFile), true);
   gateway = new LocalGatewayServer(0, null, store, tutorials, events, newbees, combat, null,
       (status, message) -> { });
  }

  /** Original reliable envelope without callback (updateEventCond/entry shape). */
  List<ProtoLite.EntityMessage> call(String method, byte[] parameters) throws Exception {
   return call(method, parameters, false);
  }

  List<ProtoLite.EntityMessage> call(String method, byte[] parameters, boolean callback)
    throws Exception {
   int sequence = SEQ.getAndIncrement();
   ByteArrayOutputStream out = new ByteArrayOutputStream();
   byte[] wrapper = BsonLite.document("m", method, "p", parameters, "r", sequence);
   byte[] envelope = callback
       ? BsonLite.document("w", wrapper, "_cbid_", sequence + 10000)
       : BsonLite.document("w", wrapper);
   RAW_RELIABLE.invoke(gateway, out, new byte[12], envelope, ACCOUNT, progress, engine,
       reliableSequences, new HashSet<Integer>(),
       new HashMap<Integer, LocalPatrolEngine.Result>(), new HashSet<Integer>());
   return frames(out.toByteArray());
  }

  byte[] profile() throws IOException { return Files.readAllBytes(profileFile); }

  /** Ordinary stage settlement through the private gateway finish entry. */
  byte[] finishScene(int scene, int area, List<Integer> heroes, int win) throws Exception {
   ByteArrayOutputStream out = new ByteArrayOutputStream();
   byte[] params = BsonLite.document("t", 1, "s", scene, "h", heroes,
       "x", Collections.emptyList(), "w", win);
   RAW_FINISH.invoke(gateway, out, new byte[12], params, ACCOUNT, progress, engine,
       new HashSet<Integer>(), new HashSet<Integer>());
   return out.toByteArray();
  }

  /** Real client stage query; the original projection is empty unless FIGHT1/5. */
  byte[] stageDoc(int area) throws Exception {
   List<ProtoLite.EntityMessage> reply = call("getAreaStagesRequest",
       BsonLite.document("aid", area));
   ProtoLite.EntityMessage frame = frame(reply, "get_area_stages_reply");
   check(frame != null, "get_area_stages_reply area " + area);
   check(BsonLite.intValue(frame.parameters, "ai") == area, "query echoes area " + area);
   return doc(frame.parameters, "st");
  }

  /** Original dialog event: startEvent callback then the client dialog trace. */
  void dialog(int event) throws Exception {
   check(progress.availableEvents.contains(event), "original graph offers " + event);
   List<ProtoLite.EntityMessage> start = call("startEvent",
       BsonLite.document("e", event), true);
   ProtoLite.EntityMessage reply = frame(start, "startEventReply");
   check(reply != null && Integer.valueOf(1).equals(BsonLite.intValue(reply.parameters, "r")),
       "start accepted " + event);
   check(progress.processingEvents.contains(event), "processing " + event);
   List<ProtoLite.EntityMessage> trace = call("clientTraceProcessingEvent",
       BsonLite.document("k", "dialog", "d", BsonLite.document("c", event)));
   ProtoLite.EntityMessage done = frame(trace, "completeEventReplyEnd");
   check(done != null && Integer.valueOf(event).equals(BsonLite.intValue(done.parameters, "e")),
       "original dialog completion " + event);
   check(progress.completedEvents.contains(event), "completed " + event);
   check(progress.eventCompletions.get(event) == 1, "completion count one " + event);
   check(!progress.availableEvents.contains(event), "offer withdrawn " + event);
  }

 /**
  * UI-only event: startEvent then the existing Project7 client-compat
  * q7CompleteUiEvent (not an original-client RPC).
  */
  void immediate(int event) throws Exception {
   check(progress.availableEvents.contains(event), "original graph offers UI event " + event);
   List<ProtoLite.EntityMessage> start = call("startEvent",
       BsonLite.document("e", event), true);
   ProtoLite.EntityMessage reply = frame(start, "startEventReply");
   check(reply != null && Integer.valueOf(1).equals(BsonLite.intValue(reply.parameters, "r")),
       "start accepted UI event " + event);
   check(progress.processingEvents.contains(event), "UI event processing " + event);
   call("q7CompleteUiEvent", BsonLite.document("e", event));
   check(progress.completedEvents.contains(event), "UI event completed " + event);
   check(progress.eventCompletions.get(event) == 1, "UI event completion count one " + event);
  }

  public void close() throws Exception {
   gateway.close();
   try (java.util.stream.Stream<Path> s = Files.walk(root)) {
    for (Path p : (Iterable<Path>) s.sorted(Comparator.reverseOrder())::iterator) Files.delete(p);
   }
  }
 }

 private static void prepare() throws Exception {
  if (prepared) return;
  Context context = new Context(assets, new AssetManager(assets));
  CoreDrawPolicy.prepare(context);
  HistoryDrawPolicy.prepare(context);
  SelectorPolicy.prepare(context);
  StoryCityPolicy.prepare(context);
  StoryMenu10Policy.prepare(context);
  RequestEventGateway.prepare(context);
  events = new LocalEventCatalog(new FileInputStream(new File(assets, "event_graph.tsv")));
  newbees = new LocalNewbeeCatalog(new ByteArrayInputStream(new byte[0]));
  combat = new LocalCombatCatalog(
      new FileInputStream(new File(assets, "combat_skills.tsv")),
      new FileInputStream(new File(assets, "combat_attrs.tsv")),
      new FileInputStream(new File(assets, "suppression.tsv")),
      new FileInputStream(new File(assets, "growth.tsv")),
      new FileInputStream(new File(assets, "home.tsv")));
  weeks = new LocalWeekCatalog(new FileInputStream(new File(assets, "weeks.tsv")));
  RAW_RELIABLE = LocalGatewayServer.class.getDeclaredMethod("handleReliableRpc",
      OutputStream.class, byte[].class, byte[].class, String.class,
      LocalTutorialStore.Progress.class, LocalEventEngine.class,
      Set.class, Set.class, Map.class, Set.class);
  RAW_RELIABLE.setAccessible(true);
  RAW_FINISH = LocalGatewayServer.class.getDeclaredMethod("handleCombatOfflineFinish",
      OutputStream.class, byte[].class, byte[].class, String.class,
      LocalTutorialStore.Progress.class, LocalEventEngine.class, Set.class, Set.class);
  RAW_FINISH.setAccessible(true);
  prepared = true;
 }

 private static void checkOffer(Fixture f, int event) {
  check(f.progress.availableEvents.contains(event), "original graph offers " + event);
  check(!f.progress.completedEvents.contains(event), "not preloaded " + event);
 }

 public static void main(String[] args) throws Exception {
  assets = new File(args[0]);
  prepare();

  // Runtime must load the frozen production classes, not a rebuilt shared overlay.
  File production = new File(args[1]).getCanonicalFile();
  for (Class<?> owner : new Class<?>[]{StoryMenu10Policy.class, StoryCityPolicy.class,
      StoryMissionBridge.class, StoryMenuShared.class, StoryMenuEntryData.class}) {
   File source = new File(owner.getProtectionDomain().getCodeSource().getLocation().toURI())
       .getCanonicalFile();
   check(source.equals(production), "runtime class from frozen production: " + owner.getSimpleName());
  }

  // Scope contract before any RPC.
  check(StoryMenuEntryData.capability(10) && StoryMenuEntryData.entryOpen()
      && StoryMenuEntryData.ready(10), "menu10 entry data ready");
  check(!StoryMenuEntryData.capability(12) && !StoryMenuEntryData.ready(12), "menu12 stays closed");
  check(StoryCityPolicy.supports(10) && !StoryCityPolicy.supports(12)
      && !StoryCityPolicy.supports(25), "city owner enables menu10 only");
  check(!LocalStoryEntryPolicy.SUPPORTED.contains(10)
      && !LocalStoryEntryPolicy.SUPPORTED.contains(12), "original allowlist unchanged");

  try (Fixture f = new Fixture()) {
   // Consistent post-ending save: derive and verify the ending receipt against
   // the original tables, not a literal.
   int[] ending = weeks.endings.get(8310);
   check(ending != null && ending[0] == 30 && ending[1] == 159,
       "weeks.tsv 8310 supplies ending30/CG159");
   check(BsonLite.intArrayValues(f.profile(), "cgs").contains(159), "CG159 receipt present");
   check(BsonLite.intArrayValues(f.profile(), "q7WeekEventBaseline").contains(8310),
       "prior ending event is baseline history");
   check(f.progress.completedEvents.stream().allMatch(e -> Arrays.stream(FOUNDATION).anyMatch(x -> x == e)),
       "current completions are only tutorial foundation");

   // Consume the prior ending's one-shot syncAllNote delivery using the original
   // LocalProfileStore ack owner before entry (no menu10 event is involved).
   check(f.call("getAreaStagesRequest", BsonLite.document("aid", 6)).size() > 0,
       "service pass emits the prior-ending delivery");
   byte[] pending = doc(f.profile(), "q7StoryPending");
   check(keys(pending).size() == 1 && keys(pending).get(0).equals("syncAllNote"),
       "prior ending produced exactly one syncAllNote delivery");
   LocalResourceEngine.Result acknowledged = f.store.updateServices(ACCOUNT,
       "q7AckStoryDelivery", BsonLite.document("s", pending), f.progress);
   check(keys(doc(acknowledged.profile, "q7StoryPending")).isEmpty()
       && keys(doc(f.profile(), "q7StoryPending")).isEmpty(),
       "original ack owner consumes the prior delivery");
   check(StoryMenuEntryData.entryReady(10, f.profile(), f.progress, weeks), "entry state ready");

   // 1. Original requestEnterStory payload {i,o}.
   String beforeCycle = f.progress.weekCommit;
   List<ProtoLite.EntityMessage> entry = f.call("requestEnterStory",
       BsonLite.document("i", 10, "o", ""));
   ProtoLite.EntityMessage ack = frame(entry, "reliableRpcAck");
   ProtoLite.EntityMessage typed = frame(entry, "replyEnterStory");
   check(ack != null && BsonLite.intValue(ack.parameters, "s") == 2, "entry ACK");
   check(typed != null && Boolean.TRUE.equals(BsonLite.boolValue(typed.parameters, "r")),
       "original requestEnterStory(10) accepted");
   check(frame(entry, "handleResetWeekReply") != null, "entry week reset acknowledgement");
   check(frame(entry, "showMessageStr") == null, "entry emits no refusal");
   byte[] entered = f.profile();
   check(Integer.valueOf(10).equals(BsonLite.intValue(entered, "q7ChapterMenu")),
       "entry commits q7ChapterMenu=10");
   check("1".equals(BsonLite.stringValue(doc(entered, "std"), "rt")),
       "entry keeps root route before the 1129 source");
   check(!beforeCycle.equals(f.progress.weekCommit), "entry commits a new cycle");
   checkOffer(f, 477);

   // 2. Ordinary city progression through the real Gateway stage owner: the
   // area-2 FIGHT1 stage is admitted and settled, then the real all-area query
   // must return area 3 FIGHT1. No progress/profile field is written here.
   check(keys(doc(doc(f.profile(), "city"), "areas")).isEmpty(),
       "profile city areas are not hand-seeded");
   List<Integer> heroes = Arrays.asList(135, 136, 137);
   int settled = 0, lastScene = 0;
   for (; settled < 12; settled++) {
    byte[] stage = f.stageDoc(2);
    Integer scene = BsonLite.intValue(stage, "cs");
    if (scene == null || scene == 0) break;
    lastScene = scene;
    if (settled == 0) check(keys(doc(stage, "sl")).size() > 0,
        "real query: area2 FIGHT1 carries stage sections");
    List<ProtoLite.EntityMessage> admit = f.call("combatOfflineRequest",
        BsonLite.document("t", 1, "s", scene, "d", BsonLite.document("a", 2), "h", heroes));
    byte[] reply = frame(admit, "combatOfflineReply") == null
        ? new byte[0] : frame(admit, "combatOfflineReply").parameters;
    check(BsonLite.intValue(reply, "t") == 1, "ordinary area2 admission accepted scene " + scene);
    check(BsonLite.stringValue(reply, "f") != null
        && !BsonLite.stringValue(reply, "f").isEmpty(), "ordinary area2 fight id scene " + scene);
    List<ProtoLite.EntityMessage> won = frames(f.finishScene(scene, 2, heroes, 1));
    check(frame(won, "combatOfflineReward") != null,
        "ordinary area2 win settlement scene " + scene);
   }
   check(settled > 0, "ordinary area2 stage chain settled at least one stage");
   check(lastScene == 1106, "ordinary area2 chain ends at the original trace 1106");
   check(f.progress.eventConditions.get("battle") != null
       && f.progress.eventConditions.get("battle").contains(1106),
       "ordinary settlement writes the original battle trace 1106");
   byte[] stage2After = f.stageDoc(2);
   byte[] stage3 = f.stageDoc(3);
   Integer area2After = BsonLite.intValue(stage2After, "cs");
   Integer area3Scene = BsonLite.intValue(stage3, "cs");
   check(area2After == null || area2After == 0,
       "real query: area2 stage is consumed after settlement");
   check(area3Scene != null && area3Scene > 0, "real query: area3 FIGHT1 returns a stage scene");
   check(LocalCityProgress.status(f.progress, 3, f.profile()) == 1,
       "original owner agrees area3 is FIGHT1 after settlement");
   check(keys(doc(stage3, "sl")).size() > 0, "real query: area3 carries stage sections");

   // 3. Original entry dialogs 477 -> 478 -> 479.
   f.dialog(477);
   checkOffer(f, 478);
   checkOffer(f, 1066);
   f.dialog(478);
   checkOffer(f, 479);
   f.dialog(479);
   checkOffer(f, 1117);
   check(f.progress.eventDays.get(477).equals("8:0"), "entry day recorded 8:0");

   // 4. Original emergency and dialog-choice chain to the route source.
   for (int event : new int[]{1066, 1067, 1117, 1118, 1119, 1120, 1121, 1122, 1125, 1123})
    f.dialog(event);
   check(f.progress.availableEvents.contains(1130), "original 1130 auto offer");
   check(!f.progress.inEmergency, "original emergency state cleared");

   // 5. Focus is derived from the real all-area query at focus time.
   byte[] stage3Focus = f.stageDoc(3);
   check(BsonLite.intValue(stage3Focus, "cs") > 0,
       "real query: area3 is still FIGHT1 at focus time");
   int focusStatus = 1; // a non-empty original stage projection requires FIGHT1.
   check(LocalCityProgress.status(f.progress, 3, f.profile()) == 1,
       "original owner agrees area3 is FIGHT1 at focus time");
   String focus = 3 + ":" + focusStatus;
   check(!f.progress.availableEvents.contains(1126), "1126 waits for original area focus");
   List<ProtoLite.EntityMessage> focusFrames = f.call("updateEventCondClient",
       BsonLite.document("c", 100, "v", "\"" + focus + "\""));
   check(frame(focusFrames, "reliableRpcAck") != null, "area focus ACK");
   check(f.progress.availableEvents.contains(1126), "area focus opens original 1126");
   check(focus.equals(f.engine.queryState().getProperty("query.areaClick")),
       "original engine area focus equals the queried client value " + focus);

   // 6. Route source 1126 -> 1127 -> 1128 -> 1129; original owners commit route
   // 10-6 and the current-cycle Wenzi receipt.
   for (int event : new int[]{1126, 1127, 1128}) f.dialog(event);
   checkOffer(f, 1129);
   f.dialog(1129);
   byte[] sourced = f.profile();
   check("10-6".equals(BsonLite.stringValue(doc(sourced, "std"), "rt")),
       "original 1129 source commits route 10-6");
   byte[] wenzi = doc(sourced, StoryMenuShared.WENZI_KEY);
   check(BsonLite.intValue(wenzi, "version") == 1
       && BsonLite.intValue(wenzi, "week") == f.progress.weekIndex
       && f.progress.weekCommit.equals(BsonLite.stringValue(wenzi, "cycle")),
       "original Wenzi receipt binds the current cycle");

   // 7. Original CG-gated 1141 and trigger-480 successor 1140.
   checkOffer(f, 1141);
   checkOffer(f, 480);
   check(!f.progress.availableEvents.contains(1140), "1140 waits for 480");
   f.immediate(1141);
   check(!LocalAlanCityEngine.active(f.profile(), f.progress),
       "Alan gate needs the 1140 occurrence too");
   f.dialog(480);
   checkOffer(f, 1140);
   check(f.progress.completedEvents.contains(1141), "1141 completed before the 1140 occurrence");
   check(StoryMenu10Policy.prerequisites(f.profile(), f.progress),
       "original 1066/1129/1141 prerequisites also hold");
   check(StoryMenu10Policy.complete1140(f.gateway, ACCOUNT, f.progress, f.engine),
       "original 1140 start + P7 UI completion");
   check(f.progress.completedEvents.contains(1140), "1140 completed");
   check(f.progress.eventCompletions.get(1140) == 1, "1140 completion count one");
   check("8:0".equals(f.progress.eventDays.get(1140)), "1140 day is the original current day");
   check(LocalAlanCityEngine.active(f.profile(), f.progress), "original Alan gate active");
   check(StoryMenu10Policy.ready(f.profile(), f.progress),
       "selector322 ready under 1141/CG/route/1140");

   // 8. Selector query, admission, loss, retry, win, success and continuation.
   List<ProtoLite.EntityMessage> query = frames(
       StoryMenu10Policy.query(f.gateway, ACCOUNT, f.progress, f.engine));
   ProtoLite.EntityMessage stages = frame(query, "get_area_stages_reply");
   check(stages != null && BsonLite.intValue(stages.parameters, "ai") == 6, "query area6");
   byte[] stage = doc(stages.parameters, "st");
   check(BsonLite.intValue(stage, "cs") == StoryMenu10Policy.MISSION, "query cs=320");
   check(BsonLite.keys(doc(stage, "sl")).size() > 0, "query carries selector sections");

   List<ProtoLite.EntityMessage> admitted = frames(
       StoryMenu10Policy.admit(f.gateway, ACCOUNT, f.progress, f.engine, heroes));
   ProtoLite.EntityMessage combatReply = frame(admitted, "combatOfflineReply");
   check(combatReply != null && BsonLite.intValue(combatReply.parameters, "t") == 1,
       "admission type1");
   check(BsonLite.intValue(combatReply.parameters, "s") == 320, "admission scene320");
   check(BsonLite.stringValue(combatReply.parameters, "f") != null
       && !BsonLite.stringValue(combatReply.parameters, "f").isEmpty(), "admission fight id");

   List<ProtoLite.EntityMessage> lost = frames(
       StoryMenu10Policy.finish(f.gateway, ACCOUNT, f.progress, f.engine, heroes, 0));
   check(frame(lost, "combatOfflineReward") != null, "loss settlement");
   check(keys(doc(doc(f.profile(), "q7BattleReceipts"), "8:320")).isEmpty(),
       "loss writes no victory receipt");
   check(!StoryMenu10Policy.successOffered(f.progress), "loss offers no 1132");
   check(BsonLite.intValue(LocalCityProgress.stages(f.progress, 6, f.profile()), "cs") == 320,
       "loss keeps stage320 retryable");

   admitted = frames(StoryMenu10Policy.admit(f.gateway, ACCOUNT, f.progress, f.engine, heroes));
   check(frame(admitted, "combatOfflineReply") != null, "retry admission");
   List<ProtoLite.EntityMessage> won = frames(
       StoryMenu10Policy.finish(f.gateway, ACCOUNT, f.progress, f.engine, heroes, 1));
   check(frame(won, "combatOfflineReward") != null, "win settlement");
   check(!keys(doc(doc(f.profile(), "q7BattleReceipts"), "8:320")).isEmpty(),
       "win writes the original 8:320 receipt");
   check(StoryMenu10Policy.successOffered(f.progress), "original 1132 offered");
   check(BsonLite.intValue(LocalCityProgress.stages(f.progress, 6, f.profile()), "cs") == 0,
       "win advances selector stage");

   check(StoryMenu10Policy.consume1132(f.gateway, ACCOUNT, f.progress, f.engine),
       "1132 completed by the original dialog");
   check(f.progress.availableEvents.contains(1133), "1133 offered");
   for (int event : new int[]{1133, 1134, 1135, 1136})
    check(StoryMenu10Policy.consumeDialog(f.gateway, ACCOUNT, f.progress, f.engine, event),
        "continuation dialog " + event);
   check(f.progress.availableEvents.contains(1137), "1137 offered after 1134-1136");
   check(!f.progress.completedEvents.contains(1137), "1137 is offered only, not completed");
   check("10-6".equals(BsonLite.stringValue(doc(f.profile(), "std"), "rt")),
       "continuation keeps route 10-6");

   // 9. Durable save/reload through the original stores.
   String savedCycle = f.progress.weekCommit;
   Set<Integer> savedCompleted = new TreeSet<>(f.progress.completedEvents);
   LocalTutorialStore reloadedTutorials = new LocalTutorialStore(
       new Context(f.root.toFile(), new AssetManager(assets)));
   LocalTutorialStore.Progress loaded = reloadedTutorials.load(ACCOUNT);
   byte[] loadedProfile = f.store.load(ACCOUNT, loaded);
   check(savedCycle.equals(loaded.weekCommit), "reload keeps the committed cycle");
   check(loaded.completedEvents.containsAll(savedCompleted)
       && Arrays.asList(477, 478, 479, 1129, 480, 1140, 1141, 1132, 1133, 1134, 1135, 1136)
           .stream().allMatch(loaded.completedEvents::contains), "reload keeps the chain");
   check(loaded.eventCompletions.get(1140) == 1, "reload keeps 1140 completion");
   check("8:0".equals(loaded.eventDays.get(1140)), "reload keeps the 1140 day");
   check("10-6".equals(BsonLite.stringValue(doc(loadedProfile, "std"), "rt")),
       "reload keeps route 10-6");
   byte[] loadedWenzi = doc(loadedProfile, StoryMenuShared.WENZI_KEY);
   check(BsonLite.intValue(loadedWenzi, "version") == 1
       && savedCycle.equals(BsonLite.stringValue(loadedWenzi, "cycle")),
       "reload keeps the Wenzi cycle receipt");
   check(StoryMenu10Policy.eligible(loadedProfile, loaded),
       "reload keeps route/cycle eligibility");
   check(LocalAlanCityEngine.active(loadedProfile, loaded),
       "reload keeps the original Alan gate");
   check(!StoryMenu10Policy.ready(loadedProfile, loaded),
       "selector is consumed by the real win, not left ready");
   check(BsonLite.intValue(LocalCityProgress.stages(loaded, 6, loadedProfile), "cs") == 0,
       "reload keeps the post-win selector stage");
  }

  System.out.println("PASS " + checks + " menu10 continuity "
      + "477->478->479->1129->480->1141->1140->selector320->loss/win/1132/1133-1136 "
      + "(consistent prior-ending CG, real area2 stage chain to area3 FIGHT1, save/reload)");
 }
}
