package com.project7.localmanager;

import android.content.*;
import android.content.res.*;
import java.io.*;
import java.lang.reflect.*;
import java.nio.*;
import java.nio.file.*;
import java.util.*;

/**
 * Raw production requestEnterStory(10) evidence.
 *
 * <p>The only entry call is the original client reliable-RPC envelope on the
 * fixed manager {@code LocalGatewayServer.handleReliableRpc}. It is not routed
 * through {@code StoryMenu10Policy.enter} or a direct {@code LocalWeekEngine.apply}.
 * The fixture is the original post-tutorial state: {@code Progress.completed()},
 * week 8 and the menu10 ending/route receipt. Event 477, 478, 479 and the
 * successor offers are driven by the real event engine; no completed event is
 * preloaded. The separately packaged midchain 1129/1141 fixture is not used.</p>
 */
public final class StoryMenu10RawEntryHost {
 private static final String ACCOUNT = "host_menu10_raw_entry";
 private static final String WEEK = "rawentry0000000000000000";
 private static int checks;
 private static File assets;
 private static LocalEventCatalog events;
 private static LocalNewbeeCatalog newbees;
 private static LocalCombatCatalog combat;
 private static LocalWeekCatalog weeks;
 private static boolean prepared;
 private static Method RAW_RELIABLE;
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
  return entryProfile(account, Arrays.asList(28, 29, 30));
 }

 private static byte[] entryProfile(String account, List<Integer> endings) throws IOException {
  byte[] profile = BsonLite.withAccountIdentity(
      Files.readAllBytes(new File(assets, "new_player.bson").toPath()), account, 900911);
  profile = BsonLite.withProfileDocument(profile, "weeknum",
      BsonLite.document("w", 8, "d", 0, "av", 60));
  profile = BsonLite.withProfileDocument(profile, "std",
      BsonLite.document("rt", "1", "ed", endings));
  profile = BsonLite.withProfileInt(profile, "q7ChapterMenu", 1);
  profile = BsonLite.withProfileArray(profile, "q7WeekEventBaseline", Collections.emptyList());
  profile = BsonLite.withProfileDocument(profile, "city", BsonLite.document("av", 60));
  byte[] inventory = BsonLite.documentValue(profile, "inv");
  if (inventory == null) inventory = BsonLite.EMPTY_DOCUMENT;
  inventory = BsonLite.withProfileArray(inventory, "items",
      Arrays.asList(BsonLite.document("i", 345, "w", 1, "u", "0123456789abcdef01234567")));
  return BsonLite.withProfileDocument(profile, "inv", inventory);
 }

 private static LocalTutorialStore.Progress entryProgress(boolean pendingNotes) {
  LocalTutorialStore.Progress progress = pendingNotes
      ? LocalTutorialStore.Progress.fresh()
      : LocalTutorialStore.Progress.completed();
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

  Fixture(boolean withHeroes, boolean pendingNotes) throws Exception {
   this(withHeroes, pendingNotes, Arrays.asList(28, 29, 30));
  }

  Fixture(boolean withHeroes, boolean pendingNotes, List<Integer> endings) throws Exception {
   root = Files.createTempDirectory("menu10-raw-entry-");
   Files.createDirectories(root.resolve("profiles"));
   profileFile = root.resolve("profiles/" + ACCOUNT + ".bson");
   byte[] profile = entryProfile(ACCOUNT, endings);
   if (withHeroes)
    for (int hero : new int[]{135, 136, 137}) profile = BsonLite.withHero(profile, hero);
   Files.write(profileFile, profile);
   Context context = new Context(root.toFile(), new AssetManager(assets));
   store = new LocalProfileStore(context);
   tutorials = new LocalTutorialStore(context);
   progress = entryProgress(pendingNotes);
   tutorials.save(ACCOUNT, progress);
   engine = new LocalEventEngine(events, newbees, progress, 0, profile, true);
   gateway = new LocalGatewayServer(0, null, store, tutorials, events, newbees, combat, null,
       (status, message) -> { });
  }

  /** Original reliable envelope; {@code callback} adds _cbid_ like CityMember. */
  List<ProtoLite.EntityMessage> call(String method, byte[] parameters, int sequence, boolean callback)
      throws Exception {
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

  byte[] reload() throws Exception {
   LocalProfileStore fresh = new LocalProfileStore(new Context(root.toFile(), new AssetManager(assets)));
   LocalTutorialStore.Progress copy = LocalTutorialStore.Progress.fromProperties(progress.toProperties());
   return fresh.load(ACCOUNT, copy);
  }

  void startAndTrace(int event) throws Exception {
   int startSequence = SEQ.getAndIncrement();
   List<ProtoLite.EntityMessage> start = call("startEvent",
       BsonLite.document("e", event), startSequence, true);
   ProtoLite.EntityMessage ack = frame(start, "reliableRpcAck");
   check(ack != null && BsonLite.intValue(ack.parameters, "s") == startSequence,
       "start ack sequence " + event);
   ProtoLite.EntityMessage reply = frame(start, "startEventReply");
   check(reply != null && Integer.valueOf(event).equals(BsonLite.intValue(reply.parameters, "e")) &&
       Integer.valueOf(1).equals(BsonLite.intValue(reply.parameters, "r")),
       "start accepted " + event);
   ProtoLite.EntityMessage carrier = frame(start, "serverCallbackCarrier");
   check(carrier != null && BsonLite.intValue(carrier.parameters, "_cbid_") == startSequence + 10000,
       "start callback lock " + event);
   check(progress.processingEvents.contains(event), "processing after start " + event);
   int traceSequence = SEQ.getAndIncrement();
   List<ProtoLite.EntityMessage> trace = call("clientTraceProcessingEvent",
       BsonLite.document("k", "dialog", "d", BsonLite.document("c", event)), traceSequence, false);
   ProtoLite.EntityMessage done = frame(trace, "completeEventReplyEnd");
   check(done != null && Integer.valueOf(event).equals(BsonLite.intValue(done.parameters, "e")),
       "dialog completion " + event);
   check(progress.completedEvents.contains(event), "completed " + event);
   check(progress.eventCompletions.get(event) == 1, "completion count one " + event);
   check(!progress.processingEvents.contains(event), "processing cleared " + event);
  }

  public void close() throws Exception {
   gateway.close();
   try (java.util.stream.Stream<Path> stream = Files.walk(root)) {
    for (Path path : (Iterable<Path>) stream.sorted(Comparator.reverseOrder())::iterator) Files.delete(path);
   }
  }
 }

 private static void checkMainlineEntry(Fixture f, int route, int initEvent, String internalRoute,
    int sequence) throws Exception {
  byte[] before = f.profile();
  String beforeCycle = f.progress.weekCommit;
  List<ProtoLite.EntityMessage> accepted = f.call("requestEnterStory",
      BsonLite.document("i", route), sequence, false);
  ProtoLite.EntityMessage ack = frame(accepted, "reliableRpcAck");
  check(ack != null && BsonLite.intValue(ack.parameters, "s") == sequence,
      "route " + route + " ack sequence");
  ProtoLite.EntityMessage typed = frame(accepted, "replyEnterStory");
  check(typed != null && Boolean.TRUE.equals(BsonLite.boolValue(typed.parameters, "r")),
      "route " + route + " typed accept");
  check(frame(accepted, "handleResetWeekReply") != null,
      "route " + route + " week reset acknowledgement");
  check(frame(accepted, "showMessageStr") == null, "route " + route + " emits no refusal");
  byte[] settled = f.profile();
  check(Integer.valueOf(route).equals(BsonLite.intValue(settled, "q7ChapterMenu")),
      "route " + route + " commits q7ChapterMenu");
  check("1".equals(BsonLite.stringValue(doc(settled, "std"), "rt")),
      "route " + route + " reset rt is original 1");
  check(Integer.valueOf(route).equals(BsonLite.intValue(doc(settled, "q7WeekTransition"), "route")),
      "route " + route + " transition route");
  check(initEvent == StoryMainlineEntry.initEvent(route)
      && Integer.valueOf(initEvent).equals(weeks.entrances.get(route)),
      "route " + route + " init event matches weeks.tsv");
  check(internalRoute.equals(StoryMainlineEntry.route(route)),
      "route " + route + " internal route string");
  check(!beforeCycle.equals(f.progress.weekCommit), "route " + route + " advances the cycle");
  String settledCycle = f.progress.weekCommit;
  List<ProtoLite.EntityMessage> replay = f.call("requestEnterStory",
      BsonLite.document("i", route), sequence + 1, false);
  ProtoLite.EntityMessage replayTyped = frame(replay, "replyEnterStory");
  check(replayTyped != null && Boolean.TRUE.equals(BsonLite.boolValue(replayTyped.parameters, "r")),
      "route " + route + " replay typed accept");
  byte[] replayed = f.profile();
  check(Integer.valueOf(route).equals(BsonLite.intValue(replayed, "q7ChapterMenu")),
      "route " + route + " replay keeps q7ChapterMenu");
  check(BsonLite.stringValue(doc(settled, "q7WeekTransition"), "id").equals(
      BsonLite.stringValue(doc(replayed, "q7WeekTransition"), "id")),
      "route " + route + " replay keeps transition identity");
  check(Integer.valueOf(route).equals(BsonLite.intValue(doc(replayed, "q7WeekTransition"), "route")),
      "route " + route + " replay keeps transition route");
  check("1".equals(BsonLite.stringValue(doc(replayed, "std"), "rt")),
      "route " + route + " replay keeps rt");
  check(settledCycle.equals(f.progress.weekCommit), "route " + route + " replay keeps the cycle");
  byte[] reloaded = f.reload();
  check(Integer.valueOf(route).equals(BsonLite.intValue(reloaded, "q7ChapterMenu")),
      "route " + route + " reload keeps q7ChapterMenu");
  check("1".equals(BsonLite.stringValue(doc(reloaded, "std"), "rt")),
      "route " + route + " reload keeps rt");
  check(Integer.valueOf(route).equals(BsonLite.intValue(doc(reloaded, "q7WeekTransition"), "route")),
      "route " + route + " reload keeps transition route");
  check(settledCycle.equals(f.progress.weekCommit), "route " + route + " reload keeps the cycle");
 }

 private static int giftCount(byte[] profile, int item) {
  byte[] items = BsonLite.arrayValue(doc(profile, "inv"), "items");
  if (items == null) return 0;
  for (String key : BsonLite.keys(items)) {
   byte[] row = BsonLite.documentValue(items, key);
   if (row != null && Integer.valueOf(item).equals(BsonLite.intValue(row, "i"))) {
    Integer count = BsonLite.intValue(row, "w");
    return count == null ? 0 : count;
   }
  }
  return 0;
 }

 private static boolean entryStateUnchanged(byte[] before, byte[] after) {
  return Objects.equals(BsonLite.intValue(before, "q7ChapterMenu"), BsonLite.intValue(after, "q7ChapterMenu"))
      && Arrays.equals(doc(before, "std"), doc(after, "std"))
      && Arrays.equals(doc(before, "weeknum"), doc(after, "weeknum"))
      && giftCount(before, 345) == giftCount(after, 345)
      && BsonLite.documentValue(after, "q7WeekTransition") == null;
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
  prepared = true;
 }

 private static void checkReply(List<ProtoLite.EntityMessage> frames, int sequence, String failure) {
  ProtoLite.EntityMessage ack = frame(frames, "reliableRpcAck");
  check(ack != null && BsonLite.intValue(ack.parameters, "s") == sequence, "ack " + sequence);
  ProtoLite.EntityMessage reply = frame(frames, "replyEnterStory");
  check(reply != null && Boolean.FALSE.equals(BsonLite.boolValue(reply.parameters, "r")),
      "replyEnterStory false " + sequence);
  check(frame(frames, "handleResetWeekReply") == null, "denial must not reset week " + sequence);
  check(frame(frames, "showMessageStr") != null, failure + " message " + sequence);
 }

 public static void main(String[] args) throws Exception {
  assets = new File(args[0]);
  prepare();

  // Scope and original-menu controls before any RPC.
  check(StoryMenuEntryData.capability(10), "menu10 capability is enabled");
  check(StoryMenuEntryData.entryOpen() && StoryMenuEntryData.ready(10), "menu10 entry data ready");
  check(!StoryMenuEntryData.capability(12) && !StoryMenuEntryData.ready(12), "menu12 stays closed");
  check(StoryCityPolicy.supports(10), "city owner supports menu10");
  // Final StoryCityPolicy.supports is menu-id keyed. Menu ids 12/25 map to
  // internal route strings 13-3/27-1 and init 460/1407, which match the
  // MAINLINE_SCORE_INFO_DATA keys 12/25. Whether admitting score keys 12/25 is
  // intended full-mainline32 behavior or a namespace collision is UNCONFIRMED
  // pending Root/Astra; the raw admission is recorded below without narrowing.
  check(StoryCityPolicy.supports(12) && StoryCityPolicy.supports(25),
      "city policy owns mainline MENU IDS 12/25");
  check("13-3".equals(StoryMainlineEntry.route(12))
      && "27-1".equals(StoryMainlineEntry.route(25)),
      "menu ids 12/25 map to different mainline routes");
  check(!StoryMenuEntryData.capability(12) && !StoryMenuEntryData.ready(12),
      "route 12 is not a menu entry");
  check(!StoryMenuEntryData.capability(25) && !StoryMenuEntryData.ready(25),
      "route 25 is not a menu entry");
  check(!StoryMenuShared.capability(12, events) && !StoryMenuShared.capability(25, events),
      "shared menu gate rejects 12/25");
  check(StoryMainlineEntry.capability(12) && StoryMainlineEntry.capability(25),
      "packaged mainline MENU IDS 12/25 are ready");
  Set<Integer> original = LocalStoryEntryPolicy.SUPPORTED;
  check(original.equals(new LinkedHashSet<>(Arrays.asList(1, 2, 3, 5, 6, 9, 11, 13, 32))),
      "original entry allowlist unchanged");
  check(!original.contains(10) && !original.contains(12), "allowlist excludes 10/12");
  for (int menu : new int[]{1, 2, 3, 5, 6, 9, 11, 13, 32})
   check(StoryCityPolicy.supports(menu), "original menu support " + menu);
  check(!StoryMenuShared.capability(12, events), "menu12 shared capability stays disabled");

  // 1. Raw rejection paths on the same entry-ready fixture.
  try (Fixture rejects = new Fixture(false, false)) {
   byte[] before = rejects.profile();
   List<ProtoLite.EntityMessage> invalid = rejects.call("requestEnterStory",
       BsonLite.document("i", 999), 1, false);
   checkReply(invalid, 1, "invalid route");
   check("路线入口不存在".equals(BsonLite.stringValue(frame(invalid, "showMessageStr").parameters, "m")),
       "invalid route is original message");
   check(entryStateUnchanged(before, rejects.profile()), "invalid route publishes no entry state");
  }

  // 12/25 are legal mainline score keys. Missing ending requirements must be a
  // typed refusal with no week/profile change; satisfying requirements must enter.
  try (Fixture missing = new Fixture(false, false, Collections.emptyList())) {
   byte[] before = missing.profile();
   String cycle = missing.progress.weekCommit;
   for (int route : new int[]{12, 25}) {
    List<ProtoLite.EntityMessage> denied = missing.call("requestEnterStory",
        BsonLite.document("i", route), 100 + route, false);
    ProtoLite.EntityMessage typed = frame(denied, "replyEnterStory");
    check(typed != null && Boolean.FALSE.equals(BsonLite.boolValue(typed.parameters, "r")),
        "missing-ending route " + route + " typed refusal");
    check(frame(denied, "handleResetWeekReply") == null,
        "missing-ending route " + route + " does not reset");
    check("尚未满足原版路线开放条件".equals(
        BsonLite.stringValue(frame(denied, "showMessageStr").parameters, "m")),
        "missing-ending route " + route + " original canEnter message");
    check(entryStateUnchanged(before, missing.profile()),
        "missing-ending route " + route + " publishes no entry state");
    check(cycle.equals(missing.progress.weekCommit),
        "missing-ending route " + route + " keeps the week");
   }
  }
  try (Fixture twelve = new Fixture(false, false, Arrays.asList(28, 29, 30))) {
   checkMainlineEntry(twelve, 12, 460, "13-3", 2);
  }
  try (Fixture twentyFive = new Fixture(false, false, Arrays.asList(24, 63))) {
   checkMainlineEntry(twentyFive, 25, 1407, "27-1", 3);
  }

  // 2. The real guard that blocks scope changes while a notebook delivery is pending.
  try (Fixture pending = new Fixture(true, true)) {
   byte[] before = pending.profile();
   List<ProtoLite.EntityMessage> denied = pending.call("requestEnterStory",
       BsonLite.document("i", 10), 3, false);
   ProtoLite.EntityMessage deniedAck = frame(denied, "reliableRpcAck");
   check(deniedAck != null && BsonLite.intValue(deniedAck.parameters, "s") == 3,
       "pending guard ack");
   check("剧情结果尚待投递，请稍后重试。".equals(
       BsonLite.stringValue(frame(denied, "showMessageStr").parameters, "m")),
       "pending guard is the real EventResetWeekGateway rejection");
   check(frame(denied, "replyEnterStory") == null,
       "guard rejection is message-consumed, not a typed accept");
   check(frame(denied, "handleResetWeekReply") == null, "pending guard does not reset");
   check(entryStateUnchanged(before, pending.profile()), "pending rejection publishes no entry state");
  }

  // 3. Accepted raw original-shape request, then duplicate/reentry idempotence.
  Fixture f = new Fixture(false, false);
  try {
   check(StoryMenuEntryData.entryReady(10, f.profile(), f.progress, weeks), "entryReady");
   check(!f.progress.availableEvents.contains(477), "477 is not preloaded");
   String previousCycle = f.progress.weekCommit;
   List<ProtoLite.EntityMessage> accepted = f.call("requestEnterStory",
       BsonLite.document("i", 10), 10, false);
   ProtoLite.EntityMessage ack = frame(accepted, "reliableRpcAck");
   check(ack != null && BsonLite.intValue(ack.parameters, "s") == 10, "entry ack");
   ProtoLite.EntityMessage typed = frame(accepted, "replyEnterStory");
   check(typed != null && Boolean.TRUE.equals(BsonLite.boolValue(typed.parameters, "r")),
       "raw requestEnterStory(10) typed accept");
   check(frame(accepted, "handleResetWeekReply") != null, "entry week reset acknowledgement");
   check(frame(accepted, "showMessageStr") == null, "raw entry emits no refusal");
   check(frame(accepted, "serverCallbackCarrier") == null, "original shape has no callback carrier");
   byte[] after = f.profile();
   check(Integer.valueOf(10).equals(BsonLite.intValue(after, "q7ChapterMenu")),
       "raw entry commits q7ChapterMenu=10");
   check("1".equals(BsonLite.stringValue(doc(after, "std"), "rt")),
       "entry keeps the original root route before the 10-6 handoff");
   byte[] transition = BsonLite.documentValue(after, "q7WeekTransition");
   check(transition != null && "requestEnterStory".equals(BsonLite.stringValue(transition, "method")) &&
       Integer.valueOf(10).equals(BsonLite.intValue(transition, "route")),
       "entry commits the original Week transition");
   check(!previousCycle.equals(f.progress.weekCommit), "entry commits a new week cycle");
   String entryCycle = f.progress.weekCommit;
   check(f.progress.availableEvents.contains(477), "entry offers original 477");
   check(!f.progress.completedEvents.contains(477), "entry does not complete 477");

   List<ProtoLite.EntityMessage> duplicate = f.call("requestEnterStory",
       BsonLite.document("i", 10), 10, false);
   ProtoLite.EntityMessage duplicateReply = frame(duplicate, "replyEnterStory");
   check(duplicateReply != null && Boolean.TRUE.equals(BsonLite.boolValue(duplicateReply.parameters, "r")),
       "duplicate raw request is idempotent accept");
   check(entryCycle.equals(f.progress.weekCommit), "duplicate does not reset the week again");
   check(Integer.valueOf(10).equals(BsonLite.intValue(f.profile(), "q7ChapterMenu")),
       "duplicate keeps q7ChapterMenu=10");

   List<ProtoLite.EntityMessage> reentry = f.call("requestEnterStory",
       BsonLite.document("i", 10), 11, true);
   ProtoLite.EntityMessage reentryReply = frame(reentry, "replyEnterStory");
   check(reentryReply != null && Boolean.TRUE.equals(BsonLite.boolValue(reentryReply.parameters, "r")),
       "reentry raw request is idempotent accept");
   ProtoLite.EntityMessage carrier = frame(reentry, "serverCallbackCarrier");
   check(carrier != null && BsonLite.intValue(carrier.parameters, "_cbid_") == 10011,
       "reentry preserves callback carrier");
   check(entryCycle.equals(f.progress.weekCommit), "reentry does not reset the week again");

   // 4. Generic post-477 event transitions from the real engine, no preloaded completions.
   f.startAndTrace(477);
   check(f.progress.availableEvents.contains(478), "477 offers 478");
   f.startAndTrace(478);
   check(f.progress.availableEvents.contains(479), "478 offers 479");
   f.startAndTrace(479);
   check(f.progress.availableEvents.contains(1066), "479 offers route source 1066");
   check(!f.progress.completedEvents.contains(1066), "1066 remains uncompleted");
   check(!f.progress.completedEvents.contains(1129) && !f.progress.availableEvents.contains(1129),
       "1129 route-source is not fabricated");
   check(!f.progress.completedEvents.contains(1141), "1141 terminal gate is not fabricated");
   check(!f.progress.availableEvents.contains(480), "480 waits for the original 1129 route source");
   check(f.progress.completedEvents.contains(477)
       && f.progress.completedEvents.contains(478)
       && f.progress.completedEvents.contains(479), "real 477/478/479 chain completed");
   check(entryCycle.equals(f.progress.weekCommit), "post-477 event chain keeps the entry cycle");

   // Generic continuation: follow every offer produced by the original graph,
   // not a preloaded completed-event list. This reaches the real 10-6 source
   // boundary without inventing 1129/1141/1140.
   for (int event : new int[]{1066, 1117, 1118, 1119, 1120, 1121, 1122, 1125, 1123}) {
    check(f.progress.availableEvents.contains(event), "original graph offers " + event);
    f.startAndTrace(event);
   }
   check(!f.progress.availableEvents.contains(1129) &&
       !f.progress.completedEvents.contains(1129), "1129 remains the original route-source boundary");
   check(!f.progress.availableEvents.contains(1141) &&
       !f.progress.completedEvents.contains(1141), "1141 remains the original terminal boundary");
   check(!f.progress.availableEvents.contains(480), "480 still waits for 1129");
   check(!f.progress.availableEvents.contains(1140), "1140 is not fabricated");
   check(entryCycle.equals(f.progress.weekCommit), "generic continuation keeps the entry cycle");

   // 5. Save/reload uses the original stores and then dispatches the same raw RPC.
   String savedCycle = f.progress.weekCommit;
   Set<Integer> savedEvents = new TreeSet<>(f.progress.availableEvents);
   Path root = f.root;
   Context context = new Context(root.toFile(), new AssetManager(assets));
   LocalProfileStore reloadedStore = new LocalProfileStore(context);
   LocalTutorialStore reloadedTutorials = new LocalTutorialStore(context);
   LocalTutorialStore.Progress reloaded = reloadedTutorials.load(ACCOUNT);
   byte[] reloadedProfile = reloadedStore.load(ACCOUNT, reloaded);
   check(Integer.valueOf(10).equals(BsonLite.intValue(reloadedProfile, "q7ChapterMenu")),
       "reload keeps q7ChapterMenu=10");
   check(savedCycle.equals(reloaded.weekCommit), "reload keeps the committed cycle");
   check(reloaded.availableEvents.containsAll(savedEvents), "reload keeps offered events");
   check(reloaded.completedEvents.containsAll(Arrays.asList(477, 478, 479)),
       "reload keeps the real event chain");
   LocalEventEngine engine = new LocalEventEngine(events, newbees, reloaded, 0, reloadedProfile, true);
   LocalGatewayServer gateway = new LocalGatewayServer(0, null, reloadedStore, reloadedTutorials,
       events, newbees, combat, null, (status, message) -> { });
   ByteArrayOutputStream out = new ByteArrayOutputStream();
   byte[] envelope = BsonLite.document("w",
       BsonLite.document("m", "requestEnterStory", "p", BsonLite.document("i", 10), "r", 20),
       "_cbid_", 10020);
   RAW_RELIABLE.invoke(gateway, out, new byte[12], envelope, ACCOUNT, reloaded, engine,
       new LinkedHashSet<Integer>(), new HashSet<Integer>(),
       new HashMap<Integer, LocalPatrolEngine.Result>(), new HashSet<Integer>());
   List<ProtoLite.EntityMessage> reloadedFrames = frames(out.toByteArray());
   ProtoLite.EntityMessage reloadedAck = frame(reloadedFrames, "reliableRpcAck");
   check(reloadedAck != null && BsonLite.intValue(reloadedAck.parameters, "s") == 20,
       "reload raw entry ack");
   ProtoLite.EntityMessage reloadedReply = frame(reloadedFrames, "replyEnterStory");
   check(reloadedReply != null && Boolean.FALSE.equals(BsonLite.boolValue(reloadedReply.parameters, "r")),
       "reload raw request is rejected while 477/478/479 are the active chain");
   check("请先完成当前剧情、巡查或战斗".equals(
       BsonLite.stringValue(frame(reloadedFrames, "showMessageStr").parameters, "m")),
       "reload rejection is the original Week busy guard");
   check(frame(reloadedFrames, "handleResetWeekReply") == null,
       "reload rejection does not reset the committed cycle");
   check(savedCycle.equals(reloaded.weekCommit), "reload request keeps the committed cycle");
   gateway.close();
  } finally {
   f.close();
  }

  System.out.println("PASS " + checks +
      " raw menu10 requestEnterStory dispatch; reject/invalid/pending/duplicate/reentry; event477->478->479; reload");
 }
}
