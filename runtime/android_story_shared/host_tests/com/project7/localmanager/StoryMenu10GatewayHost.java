package com.project7.localmanager;

import android.content.*;
import android.content.res.*;
import java.io.*;
import java.lang.reflect.*;
import java.nio.*;
import java.nio.file.*;
import java.util.*;

/**
 * v38 P7 gateway closure for menu10 selector11.
 *
 * <p>1140 is started and completed by the real LocalGatewayServer +
 * LocalEventEngine + effects owner (startEvent then q7CompleteUiEvent), then
 * queried, admitted, lost, retried and won through the same private gateway
 * entries. 1132 is completed by the original dialog trace. Only the 1066/1129/
 * 1141 prerequisite snapshot and 1140 availability are fixtures; every 1140,
 * Store, receipt, fatigue, query, admission, settlement and 1132 step is real.
 */
public final class StoryMenu10GatewayHost {
 private static final String ACCOUNT = "host_menu10_gateway";
 private static final String WEEK = "menu10-gateway-week";
 private static int checks;
 private static File assets;
 private static LocalEventCatalog events;
 private static LocalNewbeeCatalog newbees;
 private static LocalCombatCatalog combat;
 private static LocalWeekCatalog weeks;
 private static boolean prepared;
 private static Method RAW_RELIABLE, RAW_FINISH;
 private static final java.util.concurrent.atomic.AtomicInteger RAW_SEQ =
     new java.util.concurrent.atomic.AtomicInteger(1);
 private static final java.util.concurrent.atomic.AtomicInteger RAW_CB =
     new java.util.concurrent.atomic.AtomicInteger(1);
 private static final java.util.concurrent.atomic.AtomicInteger ORIGINAL_SEQ =
     new java.util.concurrent.atomic.AtomicInteger(100);
 private static final java.util.concurrent.atomic.AtomicInteger CONT_SEQ =
     new java.util.concurrent.atomic.AtomicInteger(200);

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
  for (ProtoLite.EntityMessage frame : frames)
   if (Arrays.equals(frame.methodMd5, md5(method))) return frame;
  return null;
 }

 private static final class Fixture implements AutoCloseable {
  final Path root, profileFile;
  final LocalProfileStore store;
  final LocalTutorialStore tutorials;
  final LocalTutorialStore.Progress progress;
  final LocalEventEngine engine;
  final LocalGatewayServer gateway;

  Fixture() throws Exception {
   root = Files.createTempDirectory("menu10-gateway-");
   Files.createDirectories(root.resolve("profiles"));
   profileFile = root.resolve("profiles/" + ACCOUNT + ".bson");
   Context context = new Context(root.toFile(), new AssetManager(assets));
   store = new LocalProfileStore(context);
   tutorials = new LocalTutorialStore(context);
   byte[] profile = BsonLite.withAccountIdentity(
       Files.readAllBytes(new File(assets, "new_player.bson").toPath()), ACCOUNT, 900910);
   profile = BsonLite.withProfileDocument(profile, "weeknum", BsonLite.document("w", 8, "d", 0, "av", 60));
   profile = BsonLite.withProfileDocument(profile, "std",
       BsonLite.document("rt", StoryMenu10Policy.ROUTE, "ed", Arrays.asList(28, 29, 30)));
   profile = BsonLite.withProfileInt(profile, "q7ChapterMenu", StoryMenu10Policy.MENU);
   profile = BsonLite.withProfileDocument(profile, "q7WenziCity",
       BsonLite.document("version", 1, "week", 8, "cycle", WEEK));
   profile = BsonLite.withProfileArray(profile, "q7WeekEventBaseline", Collections.emptyList());
   profile = BsonLite.withProfileDocument(profile, "city", BsonLite.document("av", 60, "fv", 50));
   for (int hero : new int[]{135, 136, 137}) profile = BsonLite.withHero(profile, hero);
   Files.write(profileFile, profile);
   progress = LocalTutorialStore.Progress.fresh();
   progress.weekIndex = 8;
   progress.weekCommit = WEEK;
   progress.initPrologue = false;
   progress.inEmergency = false;
   progress.processingEvents.clear();
   progress.patrolActions = 60;
   for (int event : new int[]{1066, 1129, 1141}) {
    progress.completedEvents.add(event);
    progress.eventCompletions.put(event, 1);
    progress.eventDays.put(event, "8:0");
   }
   progress.availableEvents.add(StoryMenu10Policy.EVENT);
   tutorials.save(ACCOUNT, progress);
   engine = new LocalEventEngine(events, newbees, progress, 0, profile, true);
   gateway = new LocalGatewayServer(0, null, store, tutorials, events, newbees, combat, null,
       (status, message) -> { });
  }

  byte[] profile() throws IOException { return Files.readAllBytes(profileFile); }
  List<Integer> team() { return Arrays.asList(135, 136, 137); }
  public void close() throws Exception {
   gateway.close();
   try (java.util.stream.Stream<Path> stream = Files.walk(root)) {
    for (Path path : (Iterable<Path>) stream.sorted(Comparator.reverseOrder())::iterator) Files.delete(path);
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

 private static List<Integer> heroes() { return Arrays.asList(135, 136, 137); }

 /** Raw gateway call with no policy precheck, used for negative evidence. */
 private static byte[] raw(Fixture fixture, String method, byte[] parameters) throws Exception {
  ByteArrayOutputStream out = new ByteArrayOutputStream();
  byte[] envelope = BsonLite.document("w",
      BsonLite.document("m", method, "p", parameters, "r", RAW_SEQ.getAndIncrement()),
      "_cbid_", RAW_CB.getAndIncrement());
  RAW_RELIABLE.invoke(fixture.gateway, out, new byte[12], envelope, ACCOUNT, fixture.progress,
      fixture.engine, new HashSet<Integer>(), new HashSet<Integer>(),
      new HashMap<Integer, LocalPatrolEngine.Result>(), new HashSet<Integer>());
  return out.toByteArray();
 }

 /** Original-shape reliable call: no _cbid_, as CityMember/CombatMember/client_event compat send. */
 private static byte[] original(Fixture fixture, String method, byte[] parameters) throws Exception {
  ByteArrayOutputStream out = new ByteArrayOutputStream();
  byte[] envelope = BsonLite.document("w",
      BsonLite.document("m", method, "p", parameters, "r", ORIGINAL_SEQ.getAndIncrement()));
  RAW_RELIABLE.invoke(fixture.gateway, out, new byte[12], envelope, ACCOUNT, fixture.progress,
      fixture.engine, new HashSet<Integer>(), new HashSet<Integer>(),
      new HashMap<Integer, LocalPatrolEngine.Result>(), new HashSet<Integer>());
  return out.toByteArray();
 }

 /** Original client callback shape with an explicit callback id. */
 private static byte[] callback(Fixture fixture, String method, byte[] parameters, int callbackId)
   throws Exception {
  ByteArrayOutputStream out = new ByteArrayOutputStream();
  byte[] envelope = BsonLite.document("w",
      BsonLite.document("m", method, "p", parameters, "r", ORIGINAL_SEQ.getAndIncrement()),
      "_cbid_", callbackId);
  RAW_RELIABLE.invoke(fixture.gateway, out, new byte[12], envelope, ACCOUNT, fixture.progress,
      fixture.engine, new HashSet<Integer>(), new HashSet<Integer>(),
      new HashMap<Integer, LocalPatrolEngine.Result>(), new HashSet<Integer>());
  return out.toByteArray();
 }

 /** Post-1133 original-shape no-callback call with its own sequence. */
 private static byte[] cont(Fixture fixture, String method, byte[] parameters) throws Exception {
  ByteArrayOutputStream out = new ByteArrayOutputStream();
  byte[] envelope = BsonLite.document("w",
      BsonLite.document("m", method, "p", parameters, "r", CONT_SEQ.getAndIncrement()));
  RAW_RELIABLE.invoke(fixture.gateway, out, new byte[12], envelope, ACCOUNT, fixture.progress,
      fixture.engine, new HashSet<Integer>(), new HashSet<Integer>(),
      new HashMap<Integer, LocalPatrolEngine.Result>(), new HashSet<Integer>());
  return out.toByteArray();
 }

 /** One real 1133-successor dialog: start callback unlock then original dialog trace. */
 private static void continueDialog(Fixture fixture, int event, int callbackId,
                                    int startSeq, int traceSeq) throws Exception {
  List<ProtoLite.EntityMessage> start = frames(
      contCallback(fixture, "startEvent", BsonLite.document("e", event), callbackId));
  check(start.size() == 3, "successor start frame count " + event);
  ProtoLite.EntityMessage ack = frame(start, "reliableRpcAck");
  check(ack != null && BsonLite.intValue(ack.parameters, "s") == startSeq,
      "successor start ACK seq" + startSeq);
  ProtoLite.EntityMessage reply = frame(start, "startEventReply");
  check(reply != null && Integer.valueOf(event).equals(BsonLite.intValue(reply.parameters, "e")) &&
      Integer.valueOf(1).equals(BsonLite.intValue(reply.parameters, "r")),
      "successor start accepted " + event);
  ProtoLite.EntityMessage carrier = frame(start, "serverCallbackCarrier");
  check(carrier != null && BsonLite.intValue(carrier.parameters, "_cbid_") == callbackId,
      "successor start callback unlock " + event);
  check(frame(start, "pushEvents") == null, "successor start emits no synthetic pushEvents " + event);
  check(fixture.progress.processingEvents.contains(event), "successor processing " + event);

  List<ProtoLite.EntityMessage> trace = frames(cont(fixture, "clientTraceProcessingEvent",
      BsonLite.document("k", "dialog", "d", BsonLite.document("c", event))));
  check(trace.size() == 3, "successor trace frame count " + event);
  ProtoLite.EntityMessage traceAck = frame(trace, "reliableRpcAck");
  check(traceAck != null && BsonLite.intValue(traceAck.parameters, "s") == traceSeq,
      "successor trace ACK seq" + traceSeq);
  ProtoLite.EntityMessage done = frame(trace, "completeEventReplyEnd");
  check(done != null && Integer.valueOf(event).equals(BsonLite.intValue(done.parameters, "e")),
      "successor original completion " + event);
  check(frame(trace, "get_all_area_info_reply") == null,
      "successor has no city effect refresh " + event);
  check(frame(trace, "pushEvents") == null, "successor trace emits no synthetic pushEvents " + event);
  check(fixture.progress.completedEvents.contains(event), "successor completed " + event);
  check(fixture.progress.eventCompletions.get(event) == 1, "successor completion count one " + event);
 }

 /** Post-1133 original client callback shape with its own sequence. */
 private static byte[] contCallback(Fixture fixture, String method, byte[] parameters, int callbackId)
   throws Exception {
  ByteArrayOutputStream out = new ByteArrayOutputStream();
  byte[] envelope = BsonLite.document("w",
      BsonLite.document("m", method, "p", parameters, "r", CONT_SEQ.getAndIncrement()),
      "_cbid_", callbackId);
  RAW_RELIABLE.invoke(fixture.gateway, out, new byte[12], envelope, ACCOUNT, fixture.progress,
      fixture.engine, new HashSet<Integer>(), new HashSet<Integer>(),
      new HashMap<Integer, LocalPatrolEngine.Result>(), new HashSet<Integer>());
  return out.toByteArray();
 }

 /** Raw private combat finish with no policy precheck. */
 private static byte[] rawFinish(Fixture fixture, byte[] parameters) throws Exception {
  ByteArrayOutputStream out = new ByteArrayOutputStream();
  RAW_FINISH.invoke(fixture.gateway, out, new byte[12], parameters, ACCOUNT, fixture.progress,
      fixture.engine, new HashSet<Integer>(), new HashSet<Integer>());
  return out.toByteArray();
 }

 public static void main(String[] args) throws Exception {
  assets = new File(args[0]);
  prepare();

  // Scoped readiness: menu10 only, menu12 and every other menu unchanged.
  check(StoryMenuEntryData.capability(StoryMenu10Policy.MENU), "menu10 entry is enabled");
  check(StoryMenuEntryData.entryOpen() && StoryMenuEntryData.ready(10), "menu10 entry data is ready");
  check(!StoryMenuEntryData.capability(12), "menu12 entry stays closed");
  check(!StoryMenuEntryData.ready(12), "menu12 readiness stays closed");
  check(StoryCityPolicy.supports(10) && !StoryCityPolicy.supports(12) && !StoryCityPolicy.supports(25),
      "city owner enables menu10 only among the new scope");
  check(!StoryMenuShared.capability(12, events), "menu12 data capability stays disabled");
  check(!LocalStoryEntryPolicy.SUPPORTED.contains(10) && !LocalStoryEntryPolicy.SUPPORTED.contains(12),
      "original entry allowlist is unchanged");

  // 0. Original requestEnterStory(10) entry result under proven ending state.
  byte[] entryProfile = BsonLite.withAccountIdentity(
      Files.readAllBytes(new File(assets, "new_player.bson").toPath()), "host_menu10_entry", 900911);
  entryProfile = BsonLite.withProfileDocument(entryProfile, "weeknum",
      BsonLite.document("w", 8, "d", 0, "av", 60));
  entryProfile = BsonLite.withProfileDocument(entryProfile, "std",
      BsonLite.document("rt", "1", "ed", Arrays.asList(28)));
  entryProfile = BsonLite.withProfileInt(entryProfile, "q7ChapterMenu", 1);
  entryProfile = BsonLite.withProfileArray(entryProfile, "q7WeekEventBaseline", Collections.emptyList());
  entryProfile = BsonLite.withProfileDocument(entryProfile, "city", BsonLite.document("av", 60));
  entryProfile = BsonLite.withProfileDocument(entryProfile, "inv",
      BsonLite.withProfileArray(doc(entryProfile, "inv"), "items",
          Arrays.asList(BsonLite.document("i", 345, "w", 1,
              "u", "0123456789abcdef01234567"))));
  for (int hero : new int[]{135, 136, 137}) entryProfile = BsonLite.withHero(entryProfile, hero);
  LocalTutorialStore.Progress entryProgress = LocalTutorialStore.Progress.fresh();
  entryProgress.weekIndex = 8;
  entryProgress.weekCommit = "0123456789abcdef01234567";
  entryProgress.initPrologue = false;
  entryProgress.inEmergency = false;
  entryProgress.patrolActions = 60;
  entryProgress.processingEvents.clear();
  check(StoryMenuEntryData.entryReady(10, entryProfile, entryProgress, weeks),
      "original menu10 entry state is ready (477 + endings28-30 + week)");
  check(!StoryMenuEntryData.entryReady(12, entryProfile, entryProgress, weeks),
      "menu12 entry state is never ready");
  LocalResourceEngine.Result denied12 = LocalWeekEngine.apply(entryProfile, weeks, entryProgress,
      "requestEnterStory", BsonLite.document("i", 12));
  boolean deniedReply = false, deniedMessage = false;
  for (LocalResourceEngine.Reply reply : denied12.replies) {
   if ("replyEnterStory".equals(reply.method))
    deniedReply = Boolean.FALSE.equals(BsonLite.boolValue(reply.parameters, "r"));
   if ("showMessageStr".equals(reply.method))
    deniedMessage = "此特殊路线的地区初始化尚未接入，已保留进度与黑色信函"
        .equals(BsonLite.stringValue(reply.parameters, "m"));
  }
  check(deniedReply && deniedMessage, "menu12 requestEnterStory stays denied");
  check(Arrays.equals(entryProfile, denied12.profile), "menu12 denial publishes no profile change");
  String previousCycle = entryProgress.weekCommit;
  LocalResourceEngine.Result entry = StoryMenu10Policy.enter(entryProfile, weeks, entryProgress);
  boolean entryAccepted = false, resetReply = false;
  for (LocalResourceEngine.Reply reply : entry.replies) {
   if ("replyEnterStory".equals(reply.method) && Boolean.TRUE.equals(BsonLite.boolValue(reply.parameters, "r")))
    entryAccepted = true;
   if ("handleResetWeekReply".equals(reply.method)) resetReply = true;
   check(!"showMessageStr".equals(reply.method), "menu10 entry emits no refusal message");
  }
  check(entryAccepted && resetReply, "original requestEnterStory(10) accepted with reset acknowledgement");
  check(Integer.valueOf(10).equals(BsonLite.intValue(entry.profile, "q7ChapterMenu")),
      "entry result commits q7ChapterMenu=10");
  check("1".equals(BsonLite.stringValue(doc(entry.profile, "std"), "rt")),
      "entry keeps the original root route before the 10-6 handoff");
  LocalWeekEngine.recover(entry.profile, entryProgress);
  check(entryProgress.availableEvents.contains(StoryMenu10Policy.ENTRY),
      "entry result offers the original entry event 477");
  check(!entryProgress.completedEvents.contains(StoryMenu10Policy.ENTRY),
      "entry does not complete 477");
  check(!previousCycle.equals(entryProgress.weekCommit), "entry commits a new week cycle");

  try (Fixture f = new Fixture()) {
   byte[] before = f.profile();
   check(!StoryMenu10Policy.completed1140(before, f.progress), "1140 starts uncompleted");
   check(!LocalAlanCityEngine.active(before, f.progress), "Alan gate inactive before real 1140");
   check(!StoryMenu10Policy.successOffered(f.progress), "1132 not offered before any result");

   // 1. Real gateway startEvent + q7CompleteUiEvent.
   check(StoryMenu10Policy.complete1140(f.gateway, ACCOUNT, f.progress, f.engine),
       "real 1140 completion through the P7 gateway");
   check(f.progress.completedEvents.contains(StoryMenu10Policy.EVENT), "original completedEvents has 1140");
   check(f.progress.eventCompletions.get(StoryMenu10Policy.EVENT) == 1, "original completion count is 1");
   check("8:0".equals(f.progress.eventDays.get(StoryMenu10Policy.EVENT)), "original 1140 day is current");
   check(!StoryMenu10Policy.complete1140(f.gateway, ACCOUNT, f.progress, f.engine),
       "duplicate 1140 start/completion is a no-op");
   byte[] after1140 = f.profile();
   check(LocalAlanCityEngine.active(after1140, f.progress), "original Alan city gate active");
   check(LocalAlanCityEngine.state(after1140, f.progress, StoryMenu10Policy.AREA) == 1,
       "original effects wrote area6 FIGHT1");
   check(LocalCityProgress.area(StoryMenu10Policy.MISSION) == StoryMenu10Policy.AREA,
       "P7 city progress maps mission320 to area6");
   check(LocalCityProgress.status(f.progress, StoryMenu10Policy.AREA, after1140) == 1,
       "P7 city status FIGHT1 after real effects");
   check(BsonLite.intValue(LocalCityProgress.stages(f.progress, StoryMenu10Policy.AREA, after1140), "cs")
       == StoryMenu10Policy.MISSION, "P7 city stages returns selector mission320");
   check(StoryMenu10Policy.ready(after1140, f.progress),
       "menu10 ready under committed 1140/selector320/10-6/week-cycle");

   // 2. Real gateway query wire.
   List<ProtoLite.EntityMessage> query = frames(
       StoryMenu10Policy.query(f.gateway, ACCOUNT, f.progress, f.engine));
   ProtoLite.EntityMessage stages = frame(query, "get_area_stages_reply");
   check(stages != null, "gateway get_area_stages_reply");
   check(BsonLite.intValue(stages.parameters, "ai") == StoryMenu10Policy.AREA, "query area6");
   byte[] stage = doc(stages.parameters, "st");
   check(BsonLite.intValue(stage, "cs") == StoryMenu10Policy.MISSION, "query cs=320 before win");
   check(BsonLite.keys(stage).contains("sl"), "query carries selector section list");

   // 3. Real gateway admission, loss, retry and win.
   int fatigue = BsonLite.intValue(BsonLite.profileHeroDocument(after1140, 135), "cf");
   List<ProtoLite.EntityMessage> admitted = frames(
       StoryMenu10Policy.admit(f.gateway, ACCOUNT, f.progress, f.engine, heroes()));
   ProtoLite.EntityMessage combatReply = frame(admitted, "combatOfflineReply");
   check(combatReply != null, "gateway combatOfflineReply");
   check(BsonLite.intValue(combatReply.parameters, "t") == 1, "admission type1");
   check(BsonLite.intValue(combatReply.parameters, "s") == StoryMenu10Policy.MISSION, "admission scene320");
   String fight = BsonLite.stringValue(combatReply.parameters, "f");
   check(fight != null && !fight.isEmpty(), "gateway generated fight id");

   List<ProtoLite.EntityMessage> lost = frames(
       StoryMenu10Policy.finish(f.gateway, ACCOUNT, f.progress, f.engine, heroes(), 0));
   check(frame(lost, "combatOfflineReward") != null, "loss settlement reply");
   check(f.progress.patrolActions == 60, "loss spends no actions");
   check(BsonLite.intValue(BsonLite.profileHeroDocument(f.profile(), 135), "cf") == fatigue,
       "loss spends no fatigue");
   check(BsonLite.keys(doc(doc(f.profile(), "q7BattleReceipts"), "8:320")).isEmpty(),
       "loss writes no victory receipt");
   check(!StoryMenu10Policy.successOffered(f.progress), "loss offers no 1132");
   check(BsonLite.intValue(LocalCityProgress.stages(f.progress, StoryMenu10Policy.AREA, f.profile()), "cs")
       == StoryMenu10Policy.MISSION, "loss keeps stage 320 retryable");

   admitted = frames(StoryMenu10Policy.admit(f.gateway, ACCOUNT, f.progress, f.engine, heroes()));
   check(frame(admitted, "combatOfflineReply") != null, "retry admission after loss");
   List<ProtoLite.EntityMessage> won = frames(
       StoryMenu10Policy.finish(f.gateway, ACCOUNT, f.progress, f.engine, heroes(), 1));
   check(frame(won, "combatOfflineReward") != null, "win settlement reply");
   check(f.progress.patrolActions == 58, "win spends original va2 once");
   for (int hero : heroes())
    check(BsonLite.intValue(BsonLite.profileHeroDocument(f.profile(), hero), "cf") ==
        BsonLite.intValue(BsonLite.profileHeroDocument(after1140, hero), "cf") - 5,
        "win spends original fatigue5 for hero " + hero);
   byte[] settled = f.profile();
   check(!BsonLite.keys(doc(doc(settled, "q7BattleReceipts"), "8:320")).isEmpty(),
       "win writes original q7BattleReceipts 8:320");
   check(f.progress.eventConditions.get("battle") != null &&
       f.progress.eventConditions.get("battle").contains(StoryMenu10Policy.MISSION),
       "win writes original battle320 trace");
   check(StoryMenu10Policy.successOffered(f.progress), "original successEvent1132 offered");
   check(!f.progress.completedEvents.contains(1132), "1132 offered, not hand-completed");
   check(LocalCityProgress.status(f.progress, StoryMenu10Policy.AREA, settled) == 0,
       "win advances area6 status");
   check(BsonLite.intValue(LocalCityProgress.stages(f.progress, StoryMenu10Policy.AREA, settled), "cs") == 0,
       "win advances selector stage to cs=0");
   check(!f.progress.completedEvents.contains(3101) && !f.progress.completedEvents.contains(4101),
       "nextstagenums are not granted");

   // 4. Duplicate finish is a replay without further spend.
   Properties beforeReplay = f.progress.toProperties();
   int money = LocalResourceEngine.value(settled, "money");
   int heroFatigue = BsonLite.intValue(BsonLite.profileHeroDocument(settled, 135), "cf");
   byte[] receipt = doc(doc(settled, "q7BattleReceipts"), "8:320");
   List<ProtoLite.EntityMessage> replay = frames(
       StoryMenu10Policy.finish(f.gateway, ACCOUNT, f.progress, f.engine, heroes(), 1));
   check(frame(replay, "combatOfflineReward") != null, "duplicate finish reply");
   check(f.progress.patrolActions == 58, "duplicate finish spends no actions");
   check(f.progress.toProperties().equals(beforeReplay), "duplicate finish mutates no Progress state");
   check(LocalResourceEngine.value(f.profile(), "money") == money, "duplicate finish regrants no money");
   check(BsonLite.intValue(BsonLite.profileHeroDocument(f.profile(), 135), "cf") == heroFatigue,
       "duplicate finish spends no fatigue");
   check(Arrays.equals(receipt, doc(doc(f.profile(), "q7BattleReceipts"), "8:320")),
       "duplicate finish keeps the same receipt");

   // 5. Original 1132 consumer through the gateway dialog trace.
   check(StoryMenu10Policy.consume1132(f.gateway, ACCOUNT, f.progress, f.engine),
       "original 1132 dialog completion");
   check(f.progress.completedEvents.contains(1132), "1132 completed by original trace");
   check(f.progress.eventCompletions.get(1132) == 1, "1132 completed once");
   check(f.progress.availableEvents.contains(1133), "original successor 1133 offered");
   byte[] consumed = f.profile();
   check(LocalCityProgress.status(f.progress, StoryMenu10Policy.AREA, consumed) == 0,
       "original areaFree6 effect keeps area6 free");
   check(BsonLite.intValue(LocalCityProgress.stages(f.progress, StoryMenu10Policy.AREA, consumed), "cs") == 0,
       "1132 keeps stage zero");
   check(!f.progress.completedEvents.contains(3101) && !f.progress.completedEvents.contains(4101),
       "1132 does not create successor mission edges");

   // Post-1133 continuation: original event/route/city/UI state after 1132.
   List<ProtoLite.EntityMessage> s3 = frames(contCallback(f, "startEvent", BsonLite.document("e", 1133), 88));
   check(s3.size() == 3, "post1133 start frame count");
   ProtoLite.EntityMessage s3a = frame(s3, "reliableRpcAck");
   check(s3a != null && BsonLite.intValue(s3a.parameters, "s") == 200, "post1133 start ACK seq200");
   ProtoLite.EntityMessage s3r = frame(s3, "startEventReply");
   check(s3r != null && Integer.valueOf(1133).equals(BsonLite.intValue(s3r.parameters, "e")) &&
       Integer.valueOf(1).equals(BsonLite.intValue(s3r.parameters, "r")), "post1133 start accepted r=1");
   ProtoLite.EntityMessage s3c = frame(s3, "serverCallbackCarrier");
   check(s3c != null && BsonLite.intValue(s3c.parameters, "_cbid_") == 88,
       "post1133 start callback id88 unlocks the client");
   check(frame(s3, "pushEvents") == null, "post1133 start emits no synthetic pushEvents");
   check(f.progress.processingEvents.contains(1133), "post1133 1133 is processing");

   List<ProtoLite.EntityMessage> u3 = frames(cont(f, "clientTraceProcessingEvent",
       BsonLite.document("k", "dialog", "d", BsonLite.document("c", 1133))));
   check(u3.size() == 3, "post1133 trace frame count");
   ProtoLite.EntityMessage u3a = frame(u3, "reliableRpcAck");
   check(u3a != null && BsonLite.intValue(u3a.parameters, "s") == 201, "post1133 trace ACK seq201");
   ProtoLite.EntityMessage u3s = frame(u3, "completeEventReplyStart");
   ProtoLite.EntityMessage u3e = frame(u3, "completeEventReplyEnd");
   check(u3s != null && u3e != null && Integer.valueOf(1133).equals(BsonLite.intValue(u3e.parameters, "e")),
       "post1133 original completion frames for 1133");
   check(frame(u3, "get_all_area_info_reply") == null, "post1133 has no city effect refresh to send");
   check(frame(u3, "pushEvents") == null, "post1133 trace emits no synthetic pushEvents");
   check(f.progress.completedEvents.contains(1133), "post1133 1133 completed once");
   check(f.progress.eventCompletions.get(1133) == 1, "post1133 1133 completion count one");
   for (int successor : new int[]{1134, 1135, 1136})
    check(f.progress.availableEvents.contains(successor), "post1133 original successor available " + successor);
   byte[] continued = f.profile();
   check("10-6".equals(BsonLite.stringValue(doc(continued, "std"), "rt")), "post1133 route stays 10-6");
   check(LocalAlanCityEngine.active(continued, f.progress), "post1133 Alan cycle gate stays active");
   check(LocalCityProgress.status(f.progress, StoryMenu10Policy.AREA, continued) == 0,
       "post1133 area6 remains free");
   check(BsonLite.intValue(LocalCityProgress.stages(f.progress, StoryMenu10Policy.AREA, continued), "cs") == 0,
       "post1133 client stage.cs remains 0");
   check(!f.progress.completedEvents.contains(3101) && !f.progress.completedEvents.contains(4101),
       "post1133 does not grant nextstagenums-derived stages");
   check(StoryMenuEntryData.capability(10) && StoryMenuEntryData.ready(10),
       "post1133 menu10 entry remains ready");
   check(StoryCityPolicy.supports(10) && !StoryCityPolicy.supports(12),
       "post1133 city entry keeps menu10 only");
   check(!f.progress.completedEvents.contains(3101) && !f.progress.completedEvents.contains(4101),
       "post1133 route completion is not claimed");
   check(StoryMenu10Policy.successorsOffered(f.progress),
       "post1133 original successor set 1134/1135/1136 offered");

   // Complete each real 1133 successor dialog over the gateway.
   continueDialog(f, 1134, 89, 202, 203);
   check(f.progress.availableEvents.contains(1135) && f.progress.availableEvents.contains(1136),
       "1134 keeps the remaining successor offers");
   continueDialog(f, 1135, 90, 204, 205);
   check(f.progress.availableEvents.contains(1136), "1136 still offered after 1135");
   continueDialog(f, 1136, 91, 206, 207);
   check(f.progress.availableEvents.contains(1137), "original 1137 offered after 1134/1135/1136");

   byte[] finished = f.profile();
   check("10-6".equals(BsonLite.stringValue(doc(finished, "std"), "rt")),
       "post1134-1136 route stays 10-6");
   check(LocalAlanCityEngine.active(finished, f.progress), "post1134-1136 Alan cycle gate stays active");
   check(LocalCityProgress.status(f.progress, StoryMenu10Policy.AREA, finished) == 0,
       "post1134-1136 area6 remains free");
   check(BsonLite.intValue(LocalCityProgress.stages(f.progress, StoryMenu10Policy.AREA, finished), "cs") == 0,
       "post1134-1136 client stage.cs remains 0");
   check(!StoryMenu10Policy.ready(finished, f.progress),
       "selector readiness is false after the real win");
   check(!f.progress.completedEvents.contains(3101) && !f.progress.completedEvents.contains(4101),
       "post1134-1136 does not grant nextstagenums-derived stages");

   // Real city/UI refresh after the continuation: original get_area_stages reply.
   List<ProtoLite.EntityMessage> refreshed = frames(
       StoryMenu10Policy.query(f.gateway, ACCOUNT, f.progress, f.engine));
   ProtoLite.EntityMessage refreshedReply = frame(refreshed, "get_area_stages_reply");
   check(refreshedReply != null && BsonLite.intValue(refreshedReply.parameters, "ai") == 6,
       "post1134-1136 city query area6");
   byte[] refreshedStage = doc(refreshedReply.parameters, "st");
   check(BsonLite.intValue(refreshedStage, "cs") == 0, "post1134-1136 UI stage.cs is 0");
   check(BsonLite.keys(refreshedStage).contains("sl"), "post1134-1136 UI keeps selector sections");

   // Original menu10 entry data stays scoped while menu12 remains disabled.
   check(weeks.entrances.get(10) != null && weeks.entrances.get(10) == 477,
       "original week entrance data for menu10 is readable");
   check(weeks.requires.get(10) != null && weeks.requires.get(10).contains(
       new HashSet<>(Arrays.asList(28, 29, 30))), "original menu10 prerequisites are readable");
   check(!LocalStoryEntryPolicy.SUPPORTED.contains(10),
       "menu10 readiness does not edit the original allowlist");
   check(!LocalStoryEntryPolicy.SUPPORTED.contains(12), "menu12 allowlist stays closed");

   // 6. Durable progress reload with scoped entry state.
   LocalTutorialStore.Progress loaded = f.tutorials.load(ACCOUNT);
   check(loaded.completedEvents.contains(1140) && loaded.eventCompletions.get(1140) == 1,
       "1140 completion persists");
   check(loaded.completedEvents.contains(1132) && loaded.eventCompletions.get(1132) == 1,
       "1132 completion persists");
   check(loaded.completedEvents.contains(1133) && loaded.eventCompletions.get(1133) == 1,
       "1133 completion persists");
   for (int event : new int[]{1134, 1135, 1136})
    check(loaded.completedEvents.contains(event) && loaded.eventCompletions.get(event) == 1,
        "successor completion persists " + event);
   check(loaded.patrolActions == 58, "actions persist");
   check(loaded.eventConditions.get("battle") != null && loaded.eventConditions.get("battle").contains(320),
       "battle trace persists");
   check(StoryMenuEntryData.capability(10) && StoryMenuEntryData.ready(10),
       "menu10 entry stays scoped after the real chain");
   check(!LocalStoryEntryPolicy.SUPPORTED.contains(10) && !LocalStoryEntryPolicy.SUPPORTED.contains(12),
       "manager entry allowlist still excludes menu10/menu12");
  }

  // 7. Negative: source gates reject an uncommitted 1140.
  try (Fixture f = new Fixture()) {
   try {
    StoryMenu10Policy.query(f.gateway, ACCOUNT, f.progress, f.engine);
    check(false, "query without 1140 must reject");
   } catch (IllegalStateException expected) {
    check(true, "query without 1140 rejects");
   }
   try {
    StoryMenu10Policy.admit(f.gateway, ACCOUNT, f.progress, f.engine, heroes());
    check(false, "admission without 1140 must reject");
   } catch (IllegalStateException expected) {
    check(true, "admission without 1140 rejects");
   }
   try {
    StoryMenu10Policy.finish(f.gateway, ACCOUNT, f.progress, f.engine, heroes(), 1);
    check(false, "finish without 1140 must reject");
   } catch (IllegalStateException expected) {
    check(true, "finish without 1140 rejects");
   }
   f.progress.availableEvents.remove(Integer.valueOf(1140));
   try {
    StoryMenu10Policy.complete1140(f.gateway, ACCOUNT, f.progress, f.engine);
    check(false, "unavailable 1140 must reject");
   } catch (IllegalStateException expected) {
    check(true, "unavailable 1140 rejects");
   }
   f.progress.availableEvents.add(1140);
   f.progress.completedEvents.remove(Integer.valueOf(1141));
   f.progress.eventCompletions.remove(1141);
   f.progress.eventDays.remove(1141);
   check(StoryMenu10Policy.complete1140(f.gateway, ACCOUNT, f.progress, f.engine)
       && f.progress.completedEvents.contains(1140) && f.progress.eventCompletions.get(1140) == 1,
       "1140 follows the original 480 offer; event 1141 is a later selector/CG gate");
  }

  // 8. Raw gateway negatives: no StoryMenu10Policy precheck, actual RPC only.
  // Assert the exact original reply/callback shapes a client consumes.
  try (Fixture f = new Fixture()) {
   List<ProtoLite.EntityMessage> query = frames(raw(f, "getAreaStagesRequest",
       BsonLite.document("aid", StoryMenu10Policy.AREA)));
   check(query.size() == 3, "raw query failure frame count");
   ProtoLite.EntityMessage queryAck = frame(query, "reliableRpcAck");
   check(queryAck != null && BsonLite.intValue(queryAck.parameters, "s") == 1, "raw query ACK seq1");
   ProtoLite.EntityMessage stages = frame(query, "get_area_stages_reply");
   check(stages != null && BsonLite.intValue(stages.parameters, "ai") == 6, "raw query area6 reply");
   byte[] emptyStage = doc(stages.parameters, "st");
   check(BsonLite.keys(emptyStage).isEmpty(), "raw query stage is empty, no cs/sl");
   ProtoLite.EntityMessage queryCarrier = frame(query, "serverCallbackCarrier");
   check(queryCarrier != null && BsonLite.intValue(queryCarrier.parameters, "_cbid_") == 1,
       "raw query callback cbid1");
   check(BsonLite.keys(doc(queryCarrier.parameters, "_r_")).isEmpty(), "raw query empty callback body");
   check(frame(query, "completeEventReplyStart") == null && frame(query, "completeEventReplyEnd") == null,
       "raw query emits no completion frames");
   check(!StoryMenu10Policy.completed1140(f.profile(), f.progress),
       "raw query negative leaves 1140 uncommitted");

   List<ProtoLite.EntityMessage> admitted = frames(raw(f, "combatOfflineRequest",
       BsonLite.document("t", 1, "s", 320, "d", BsonLite.document("a", StoryMenu10Policy.AREA),
           "h", heroes())));
   check(admitted.size() == 4, "raw admission failure frame count");
   ProtoLite.EntityMessage admissionAck = frame(admitted, "reliableRpcAck");
   check(admissionAck != null && BsonLite.intValue(admissionAck.parameters, "s") == 2, "raw admission ACK seq2");
   ProtoLite.EntityMessage message = frame(admitted, "showMessageStr");
   check(message != null && "此关卡尚未开放".equals(BsonLite.stringValue(message.parameters, "m")),
       "raw admission original refusal message");
   ProtoLite.EntityMessage reply = frame(admitted, "combatOfflineReply");
   check(reply != null, "raw admission has a combatOfflineReply");
   check(Integer.valueOf(0).equals(BsonLite.intValue(reply.parameters, "t")), "raw admission t=0");
   check(Integer.valueOf(320).equals(BsonLite.intValue(reply.parameters, "s")), "raw admission s=320");
   check("".equals(BsonLite.stringValue(reply.parameters, "f")), "raw admission empty fight id");
   check(BsonLite.intArrayValues(reply.parameters, "h").isEmpty(), "raw admission empty heroes");
   check(Integer.valueOf(6).equals(BsonLite.intValue(doc(reply.parameters, "d"), "a")),
       "raw admission request area6 echoed");
   check(BsonLite.keys(doc(doc(reply.parameters, "c"), "heroes")).isEmpty(),
       "raw admission empty combat heroes");
   ProtoLite.EntityMessage admissionCarrier = frame(admitted, "serverCallbackCarrier");
   check(admissionCarrier != null && BsonLite.intValue(admissionCarrier.parameters, "_cbid_") == 2,
       "raw admission callback cbid2");
   check(BsonLite.keys(doc(admissionCarrier.parameters, "_r_")).isEmpty(),
       "raw admission empty callback body");
   check(frame(admitted, "completeEventReplyEnd") == null, "raw admission emits no completion");
   check(f.progress.patrolActions == 60, "raw admission negative spends no actions");

   byte[] finish = rawFinish(f, BsonLite.document("t", 1, "s", 320, "h", heroes(),
       "x", Collections.emptyList(), "w", 1));
   List<ProtoLite.EntityMessage> finishFrames = frames(finish);
   check(finishFrames.size() == 2, "raw finish failure frame count");
   ProtoLite.EntityMessage finishMessage = frame(finishFrames, "showMessageStr");
   check(finishMessage != null &&
       "没有与本次结算对应的已开始战斗".equals(BsonLite.stringValue(finishMessage.parameters, "m")),
       "raw finish original refusal message");
   ProtoLite.EntityMessage reward = frame(finishFrames, "combatOfflineReward");
   check(reward != null, "raw finish combatOfflineReward");
   check(Integer.valueOf(1).equals(BsonLite.intValue(reward.parameters, "t")), "raw finish type1 echoed");
   check(Integer.valueOf(320).equals(BsonLite.intValue(reward.parameters, "s")), "raw finish scene320");
   check(Integer.valueOf(0).equals(BsonLite.intValue(reward.parameters, "w")), "raw finish win=0");
   check(BsonLite.keys(doc(reward.parameters, "r")).isEmpty(), "raw finish empty reward");
   check(Integer.valueOf(135).equals(BsonLite.intArrayValues(reward.parameters, "h").get(0)),
       "raw finish echoes admitted party");
   check(frame(finishFrames, "serverCallbackCarrier") == null, "raw finish emits no callback");
   check(frame(finishFrames, "completeEventReplyEnd") == null, "raw finish emits no completion");
   check(f.progress.patrolActions == 60, "raw finish without admission spends no actions");
   check(BsonLite.keys(doc(doc(f.profile(), "q7BattleReceipts"), "8:320")).isEmpty(),
       "raw finish without admission writes no receipt");
   check(!StoryMenu10Policy.successOffered(f.progress), "raw finish without admission offers no 1132");
   check(!StoryMenu10Policy.completed1140(f.profile(), f.progress),
       "raw finish without admission leaves 1140 uncommitted");

   f.progress.availableEvents.remove(Integer.valueOf(1140));
   List<ProtoLite.EntityMessage> start = frames(raw(f, "startEvent", BsonLite.document("e", 1140)));
   check(start.size() == 4, "raw start1140 failure frame count");
   ProtoLite.EntityMessage startAck = frame(start, "reliableRpcAck");
   check(startAck != null && BsonLite.intValue(startAck.parameters, "s") == 3, "raw start1140 ACK seq3");
   ProtoLite.EntityMessage startReply = frame(start, "startEventReply");
   check(startReply != null && Integer.valueOf(1140).equals(BsonLite.intValue(startReply.parameters, "e")) &&
       Integer.valueOf(0).equals(BsonLite.intValue(startReply.parameters, "r")), "raw start1140 e=1140 r=0");
   check(frame(start, "pushEvents") != null, "raw start1140 original pushEvents");
   ProtoLite.EntityMessage startCarrier = frame(start, "serverCallbackCarrier");
   check(startCarrier != null && BsonLite.intValue(startCarrier.parameters, "_cbid_") == 3,
       "raw start1140 callback cbid3");
   check(frame(start, "completeEventReplyEnd") == null, "raw start1140 emits no completion");
   check(!f.progress.processingEvents.contains(1140) && !f.progress.completedEvents.contains(1140),
       "raw startEvent negative leaves 1140 untouched");

   List<ProtoLite.EntityMessage> ui = frames(raw(f, "q7CompleteUiEvent", BsonLite.document("e", 1140)));
   check(ui.size() == 2, "raw ui-only failure frame count");
   ProtoLite.EntityMessage uiAck = frame(ui, "reliableRpcAck");
   check(uiAck != null && BsonLite.intValue(uiAck.parameters, "s") == 4, "raw ui-only ACK seq4");
   ProtoLite.EntityMessage uiCarrier = frame(ui, "serverCallbackCarrier");
   check(uiCarrier != null && BsonLite.intValue(uiCarrier.parameters, "_cbid_") == 4,
       "raw ui-only callback cbid4");
   check(BsonLite.keys(doc(uiCarrier.parameters, "_r_")).isEmpty(), "raw ui-only empty callback body");
   check(frame(ui, "completeEventReplyStart") == null && frame(ui, "completeEventReplyEnd") == null,
       "raw q7CompleteUiEvent without processing completes nothing");
   check(frame(ui, "pushEvents") == null, "raw ui-only emits no pushEvents");
   check(!f.progress.completedEvents.contains(1140), "raw UI-only negative leaves 1140 uncompleted");

   List<ProtoLite.EntityMessage> success = frames(raw(f, "startEvent", BsonLite.document("e", 1132)));
   check(success.size() == 4, "raw start1132 failure frame count");
   ProtoLite.EntityMessage successAck = frame(success, "reliableRpcAck");
   check(successAck != null && BsonLite.intValue(successAck.parameters, "s") == 5, "raw start1132 ACK seq5");
   ProtoLite.EntityMessage successReply = frame(success, "startEventReply");
   check(successReply != null && Integer.valueOf(1132).equals(BsonLite.intValue(successReply.parameters, "e")) &&
       Integer.valueOf(0).equals(BsonLite.intValue(successReply.parameters, "r")), "raw start1132 e=1132 r=0");
   check(frame(success, "pushEvents") != null, "raw start1132 original pushEvents");
   ProtoLite.EntityMessage successCarrier = frame(success, "serverCallbackCarrier");
   check(successCarrier != null && BsonLite.intValue(successCarrier.parameters, "_cbid_") == 5,
       "raw start1132 callback cbid5");
   check(frame(success, "completeEventReplyEnd") == null, "raw start1132 emits no completion");
   check(!f.progress.completedEvents.contains(1132), "raw 1132 negative completes nothing");
  }

  // 9. Original no-callback shapes and the real startEvent callback unlock.
  try (Fixture f = new Fixture()) {
   // CityMember: no callback, typed empty-stage reply, no carrier required.
   List<ProtoLite.EntityMessage> q = frames(original(f, "getAreaStagesRequest",
       BsonLite.document("aid", StoryMenu10Policy.AREA)));
   check(q.size() == 2, "original no-cbid query frame count");
   ProtoLite.EntityMessage qa = frame(q, "reliableRpcAck");
   check(qa != null && BsonLite.intValue(qa.parameters, "s") == 100, "original query ACK seq100");
   ProtoLite.EntityMessage qs = frame(q, "get_area_stages_reply");
   check(qs != null && BsonLite.intValue(qs.parameters, "ai") == 6, "original query typed area6 reply");
   check(BsonLite.keys(doc(qs.parameters, "st")).isEmpty(), "original query empty st consumer no stage update");
   check(frame(q, "serverCallbackCarrier") == null, "original no-cbid query has no carrier");

   // CombatMember: no callback, typed t=0 unlock, no carrier required.
   List<ProtoLite.EntityMessage> c = frames(original(f, "combatOfflineRequest",
       BsonLite.document("t", 1, "s", 320, "d", BsonLite.document("a", 6), "h", heroes())));
   check(c.size() == 3, "original no-cbid combat frame count");
   ProtoLite.EntityMessage ca = frame(c, "reliableRpcAck");
   check(ca != null && BsonLite.intValue(ca.parameters, "s") == 101, "original combat ACK seq101");
   check(frame(c, "showMessageStr") != null, "original combat refusal message");
   ProtoLite.EntityMessage cr = frame(c, "combatOfflineReply");
   check(cr != null, "original combat typed reply");
   boolean uiLocked = true;
   int combatState = 1;
   if (BsonLite.intValue(cr.parameters, "t") == 0) { uiLocked = false; combatState = 0; }
   check(!uiLocked && combatState == 0, "original combat t=0 consumer unlocks and restores STATE_NONE");
   check(Integer.valueOf(320).equals(BsonLite.intValue(cr.parameters, "s")), "original combat s=320");
   check("".equals(BsonLite.stringValue(cr.parameters, "f")), "original combat empty fight id");
   check(BsonLite.intArrayValues(cr.parameters, "h").isEmpty(), "original combat empty party");
   check(BsonLite.keys(doc(cr.parameters, "d")).contains("a") &&
       Integer.valueOf(6).equals(BsonLite.intValue(doc(cr.parameters, "d"), "a")), "original combat d.a=6");
   check(BsonLite.keys(doc(cr.parameters, "c")).contains("heroes"), "original combat c document");
   check(frame(c, "serverCallbackCarrier") == null, "original no-cbid combat has no carrier");
   check(f.progress.patrolActions == 60, "original combat rejection spends nothing");

   // q7CompleteUiEvent: no callback, ACK only, no completion/progress.
   List<ProtoLite.EntityMessage> u = frames(original(f, "q7CompleteUiEvent", BsonLite.document("e", 1140)));
   check(u.size() == 1, "original no-cbid q7 frame count");
   ProtoLite.EntityMessage ua = frame(u, "reliableRpcAck");
   check(ua != null && BsonLite.intValue(ua.parameters, "s") == 102, "original q7 ACK seq102");
   check(frame(u, "serverCallbackCarrier") == null, "original no-cbid q7 has no carrier");
   check(frame(u, "completeEventReplyStart") == null && frame(u, "completeEventReplyEnd") == null,
       "original q7 failure does not require typed completion");
   check(!f.progress.completedEvents.contains(1140) && !f.progress.processingEvents.contains(1140),
       "original q7 failure does not progress");

   // startEvent: ACK alone must not unlock; matching callback id releases the lock.
   f.progress.availableEvents.remove(Integer.valueOf(1140));
   int callbackId = 77;
   List<ProtoLite.EntityMessage> s = frames(callback(f, "startEvent", BsonLite.document("e", 1140), callbackId));
   check(s.size() == 4, "original start callback frame count");
   ProtoLite.EntityMessage sa = frame(s, "reliableRpcAck");
   check(sa != null && BsonLite.intValue(sa.parameters, "s") == 103, "original start ACK seq103");
   ProtoLite.EntityMessage sr = frame(s, "startEventReply");
   check(sr != null && Integer.valueOf(0).equals(BsonLite.intValue(sr.parameters, "r")),
       "original start r=0 refusal");
   boolean startLocked = true;
   if (frame(s, "reliableRpcAck") != null) { /* ACK only clears retransmit, never unlocks */ }
   ProtoLite.EntityMessage sc = frame(s, "serverCallbackCarrier");
   if (sc != null && BsonLite.intValue(sc.parameters, "_cbid_") == callbackId) startLocked = false;
   check(!startLocked, "matching startEvent callback id unlocks the original UI lock");
   check(BsonLite.keys(doc(sc.parameters, "_r_")).isEmpty(), "original start callback empty body");
   check(frame(s, "completeEventReplyEnd") == null, "original start failure completes nothing");
   check(!f.progress.processingEvents.contains(1140) && !f.progress.completedEvents.contains(1140),
       "original start failure leaves 1140 untouched");
  }

  System.out.println("PASS " + checks + " menu10 selector11 v38 gateway 1140/effects/query/admission/loss/win/1132 checks");
 }
}
