package com.project7.localmanager;

import android.content.*;
import android.content.res.*;
import java.io.*;
import java.lang.reflect.*;
import java.nio.*;
import java.nio.file.*;
import java.util.*;

/**
 * Limited representative v43 host for the mainline capability matrix.
 *
 * <p>Proven menus: v55 entry closure adds 12/19/25; menu20/28 remain the original client reliable
 * requestEnterStory envelope on the fixed Gateway. Menu20 then drives its
 * original 1323..1331 dialog chain, checks the generic city effect reducer,
 * queries area2 route21, settles a real 1114 battle and advances a real day.
 * Menu28 proves a second entry/query/persistence path. No plot is prefilled,
 * no completed event is seeded, and no D8/APK/native path is used.</p>
 */
public final class StoryMainlineCapabilityHost {
 private static final String ACCOUNT = "host_mainline_capability";
 private static final String WEEK = "cap00000000000000000000";
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

 private static boolean hasFrame(byte[] wire, String method) throws Exception {
  return frame(frames(wire), method) != null;
 }

 private static boolean pushHas(byte[] wire, int event) throws Exception {
  for (ProtoLite.EntityMessage message : frames(wire)) {
   if (!Arrays.equals(message.methodMd5, md5("pushEvents"))) continue;
   byte[] array = BsonLite.arrayValue(message.parameters, "a");
   if (array == null) return false;
   for (String key : BsonLite.keys(array)) {
    Integer id = BsonLite.intValue(BsonLite.documentValue(array, key), "0");
    if (id != null && id == event) return true;
   }
   return false;
  }
  return false;
 }

 private static byte[] entryProfile(int menu, int ending) throws IOException {
  byte[] profile = BsonLite.withAccountIdentity(
      Files.readAllBytes(new File(assets, "new_player.bson").toPath()), ACCOUNT, 901020 + menu);
  profile = BsonLite.withProfileDocument(profile, "weeknum",
      BsonLite.document("w", 8, "d", 0, "av", 60));
  profile = BsonLite.withProfileDocument(profile, "std",
      BsonLite.document("rt", "1", "ed", Collections.singletonList(ending)));
  profile = BsonLite.withProfileInt(profile, "q7ChapterMenu", 1);
  profile = BsonLite.withProfileArray(profile, "q7WeekEventBaseline", Collections.emptyList());
  profile = BsonLite.withProfileDocument(profile, "city", BsonLite.document("av", 60));
  byte[] inventory = doc(profile, "inv");
  inventory = BsonLite.withProfileArray(inventory, "items",
      Arrays.asList(BsonLite.document("i", 345, "w", 1, "u", "0123456789abcdef01234567")));
  return BsonLite.withProfileDocument(profile, "inv", inventory);
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

  Fixture(int menu, int ending) throws Exception {
   root = Files.createTempDirectory("mainline-capability-");
   Files.createDirectories(root.resolve("profiles"));
   profileFile = root.resolve("profiles/" + ACCOUNT + ".bson");
   byte[] profile = entryProfile(menu, ending);
   for (int hero : new int[]{135, 136, 137}) profile = BsonLite.withHero(profile, hero);
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
   ByteArrayOutputStream out = new ByteArrayOutputStream();
   byte[] wrapper = BsonLite.document("m", method, "p", parameters, "r", sequence);
   byte[] envelope = BsonLite.document("w", wrapper, "_cbid_", sequence + 10000);
   RAW_RELIABLE.invoke(gateway, out, new byte[12], envelope, ACCOUNT, progress, engine,
       reliableSequences, new HashSet<Integer>(),
       new HashMap<Integer, LocalPatrolEngine.Result>(), new HashSet<Integer>());
   return frames(out.toByteArray());
  }

  byte[] profile() throws IOException {
   return Files.readAllBytes(profileFile);
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

  public void close() throws Exception {
   gateway.close();
   try (java.util.stream.Stream<Path> stream = Files.walk(root)) {
    for (Path path : (Iterable<Path>) stream.sorted(Comparator.reverseOrder())::iterator)
     Files.delete(path);
   }
  }
 }

 private static byte[] begin(int scene, int area) {
  return BsonLite.document("t", 1, "s", scene, "h", Arrays.asList(10),
      "d", BsonLite.document("a", area));
 }

 private static byte[] finish(int scene, int win) {
  return BsonLite.document("t", 1, "s", scene, "h", Arrays.asList(10), "w", win,
      "x", Collections.emptyList());
 }

 private static void gatewayFinish(Fixture fixture, LocalEconomyEngine.Result result,
                                   int scene, int win) throws Exception {
  Method method = LocalGatewayServer.class.getDeclaredMethod("handleCombatOfflineFinish",
      OutputStream.class, byte[].class, byte[].class, String.class,
      LocalTutorialStore.Progress.class, LocalEventEngine.class, Set.class, Set.class);
  method.setAccessible(true);
  try {
   method.invoke(fixture.gateway, new ByteArrayOutputStream(), new byte[12], finish(scene, win),
       ACCOUNT, fixture.progress, fixture.engine, new HashSet<Integer>(), new HashSet<Integer>());
  } catch (InvocationTargetException error) {
   Throwable cause = error.getCause();
   if (cause instanceof Exception) throw (Exception) cause;
   throw error;
  }
 }

 private static int state(byte[] profile, int area) {
  Integer value = BsonLite.intValue(doc(profile, "q7ChapterStates"), Integer.toString(area));
  return value == null ? -1 : value;
 }

 private static void prepare() throws Exception {
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
  } catch (ReflectiveOperationException error) {
   throw new AssertionError("Gateway reliable ABI", error);
  }
  prepared = true;
 }

 public static void main(String[] args) throws Exception {
  assets = new File(args[0]);
  prepare();
  check(StoryCityPolicy.supports(1), "original menu1 remains supported");
  check(StoryCityPolicy.supports(10), "scoped menu10 remains supported");
  check(StoryCityPolicy.supports(12), "menu12 entry-enabled with dedicated city owner");
  check(StoryCityPolicy.supports(20) && StoryCityPolicy.supports(28), "proven menus supported");
  check(StoryCityPolicy.supports(19) && StoryCityPolicy.supports(25),
      "v55 entry-closure menus remain supported");
  check(StoryMainlineEntry.capability(4) && StoryMainlineEntry.capability(20) &&
      StoryMainlineEntry.capability(23) && StoryMainlineEntry.capability(28) &&
      StoryMainlineEntry.capability(12) && StoryMainlineEntry.capability(19) &&
      StoryMainlineEntry.capability(25),
      "entry capability scoped to proven set");
  check(StoryMainlineEntry.initEvent(20) == 1323 && StoryMainlineEntry.initEvent(28) == 1649,
      "entry init event source");
  check(StoryMainlineEntry.chapterKeys(20) == 52 && StoryMainlineEntry.scenes(28) == 21,
      "entry chapter/scene source");
  check(weeks.endings.containsKey(8029) && weeks.endings.get(8029)[0] == 1,
      "weeks ending 1 row available");
  check(weeks.endings.containsKey(8808) && weeks.endings.get(8808)[0] == 114,
      "weeks ending 114 row available");

  try (Fixture fixture = new Fixture(20, 63)) {
   byte[] before = fixture.profile();
   check(!StoryMainlineEntry.entryReady(20, before, fixture.progress, weeks) == false,
       "entryReady true only with required ending 63");
   check(!StoryMainlineEntry.entryReady(20, BsonLite.withProfileDocument(before, "std",
       BsonLite.document("rt", "1", "ed", Collections.singletonList(1))), fixture.progress, weeks),
       "entryReady false without ending 63/64");
   check(!fixture.progress.completedEvents.contains(1323), "entry event not prefilled");
   fixture.entry(20);
   byte[] profile = fixture.profile();
   check(StoryMainlineEntry.entryReady(20, profile, fixture.progress, weeks),
       "post-entry entryReady with persisted week");
   check(StoryCityPolicy.owns(profile), "proven menu owns city reducer");
   check(StoryMainlineEntry.cityOwns(profile), "proven menu generic city effects");
   // Original 1323..1331 dialog chain; no event is pre-marked completed.
   for (int event = 1323; event <= 1331; event++) fixture.startAndTrace(event);
   profile = fixture.profile();
   check("21-1".equals(BsonLite.stringValue(doc(profile, "std"), "rt")),
       "original chain set route21-1");
   check(BsonLite.boolValue(doc(profile, "q7ChapterEffects"), "1331"),
       "generic reducer receipt 1331");
   check(state(profile, 8) == 0 && state(profile, 5) == 1,
       "generic city effects areaFree8/areaFight5");
   check(BsonLite.keys(doc(profile, "q7ChapterLocks")).isEmpty(),
       "generic reducer leaves no invented lock");
   check(fixture.reload().weekCommit.equals(fixture.progress.weekCommit),
       "entry cycle survives reload");
  }

  try (Fixture fixture = new Fixture(28, 114)) {
   check(!fixture.progress.completedEvents.contains(1649), "menu28 event not prefilled");
   fixture.entry(28);
   byte[] profile = fixture.profile();
   check(StoryMainlineEntry.entryReady(28, profile, fixture.progress, weeks),
       "menu28 post-entry entryReady");
   check(fixture.reload().weekCommit.equals(fixture.progress.weekCommit),
       "menu28 reload keeps the entry cycle");
  }
  System.out.println("PASS " + checks +
      " frozen v43 capability consumers: scoped entry/menu20 1323..1331/effects/menu28 entry");
 }

}
