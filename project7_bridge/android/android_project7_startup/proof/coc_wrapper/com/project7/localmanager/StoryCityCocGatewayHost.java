package com.project7.localmanager;

import android.content.Context;
import android.content.res.AssetManager;
import java.io.*;
import java.lang.reflect.*;
import java.nio.charset.StandardCharsets;
import java.nio.file.*;
import java.security.MessageDigest;
import java.util.*;
import org.json.JSONObject;

/**
 * COC 482 gateway seam evidence against the C-patched manager DEX frames.
 *
 * Real caller: LocalGatewayServer.handleReliableRpc("combatOfflineRequest") for
 * admission, then the exact LocalGatewayServer.handleCombatOfflineFinish
 * consumer that handleClient invokes for the COMBAT_OFFLINE_FINISH frame.
 * Fixture only: the route-27-1 profile/progress snapshot and the explicit
 * win=1 finish flag (no real battle was played).
 */
public final class StoryCityCocGatewayHost {
 static final String ACCOUNT = "host_story_city_coc_gateway";
 static final String WEEK = "coc-gateway-week";
 static final String CATALOG = "af2328b97372c27fd392b5b399d03daa17fa73acdd35d2b1ad5b0a8f07218069";
 static final int SCENE = 482, AREA = 10000, PREDECESSOR = 7, COMPLETION = 1435;
 static final byte[] FRAME_ID = new byte[12];
 static int checks;
 static final List<String> lines = new ArrayList<>();

 static void check(boolean value, String why) { checks++; if (!value) throw new AssertionError(why); }
 static void line(String text) { lines.add(text); System.out.println(text); }
 static String hex(byte[] value) throws Exception {
  StringBuilder out = new StringBuilder();
  for (byte b : MessageDigest.getInstance("SHA-256").digest(value)) out.append(String.format("%02x", b & 255));
  return out.toString();
 }
 static byte[] read(Path path) throws IOException { return Files.readAllBytes(path); }
 static byte[] doc(byte[] profile, String key) {
  byte[] value = profile == null ? null : BsonLite.documentValue(profile, key);
  return value == null ? BsonLite.EMPTY_DOCUMENT : value;
 }
 static int money(byte[] profile) { Number value = BsonLite.intValue(profile, "money"); return value == null ? 0 : value.intValue(); }
 static byte[] request(int scene, int area) {
  return BsonLite.document("t", 1, "s", scene, "d", BsonLite.document("a", area), "h", Arrays.asList(135));
 }
 static byte[] finishRequest(int scene, int area, int win) {
  return BsonLite.document("t", 1, "s", scene, "d", BsonLite.document("a", area), "h", Arrays.asList(135), "w", win, "x", Collections.emptyList());
 }
 static byte[] baseProfile(byte[] player) throws Exception { return baseProfile(player, ACCOUNT, WEEK); }
 static byte[] baseProfile(byte[] player, String account, String week) throws Exception {
  byte[] profile = BsonLite.withAccountIdentity(player, account, 900777);
  profile = BsonLite.withProfileDocument(profile, "weeknum", BsonLite.document("w", 3, "d", 0, "av", 60));
  profile = BsonLite.withProfileDocument(profile, "std", BsonLite.document("rt", "27-1", "ff", false));
  profile = BsonLite.withProfileInt(profile, "q7ChapterMenu", 25);
  profile = BsonLite.withProfileInt(profile, "level", 50);
  profile = BsonLite.withProfileDocument(profile, "q7ChapterStates", BsonLite.document(Integer.toString(PREDECESSOR), 0, Integer.toString(AREA), 1));
  profile = BsonLite.withProfileDocument(profile, "q7ChapterLocks", BsonLite.EMPTY_DOCUMENT);
  profile = BsonLite.withProfileArray(profile, "q7WeekEventBaseline", Collections.emptyList());
  profile = BsonLite.withProfileDocument(profile, "q7StoryCity", BsonLite.document("schema", 1, "catalog", CATALOG, "week", week));
  profile = BsonLite.withProfileDocument(profile, "city", BsonLite.document("av", 60));
  profile = BsonLite.withHero(profile, 135);
  return profile;
 }
 static LocalTutorialStore.Progress progress() { return progress(WEEK); }
 static LocalTutorialStore.Progress progress(String week) {
  LocalTutorialStore.Progress p = LocalTutorialStore.Progress.fresh();
  p.initPrologue = false; p.inEmergency = false; p.patrolActions = 60; p.weekCommit = week; p.weekIndex = 3;
  return p;
 }
 static List<ProtoLite.EntityMessage> frames(byte[] wire) throws IOException {
  List<ProtoLite.EntityMessage> out = new ArrayList<>();
  java.nio.ByteBuffer buffer = java.nio.ByteBuffer.wrap(wire).order(java.nio.ByteOrder.LITTLE_ENDIAN);
  while (buffer.hasRemaining()) {
   int length = buffer.getInt();
   check(buffer.getShort() == 5, "frame opcode");
   byte[] data = new byte[length - 2];
   buffer.get(data);
   out.add(ProtoLite.parseEntityMessage(data));
  }
  return out;
 }
 static ProtoLite.EntityMessage frame(List<ProtoLite.EntityMessage> frames, String name) {
  byte[] md5 = md5(name);
  for (ProtoLite.EntityMessage frame : frames) if (Arrays.equals(frame.methodMd5, md5)) return frame;
  return null;
 }
 static int count(List<ProtoLite.EntityMessage> frames, String name) {
  byte[] md5 = md5(name); int total = 0;
  for (ProtoLite.EntityMessage frame : frames) if (Arrays.equals(frame.methodMd5, md5)) total++;
  return total;
 }
 static byte[] md5(String text) {
  try { return MessageDigest.getInstance("MD5").digest(text.getBytes(StandardCharsets.UTF_8)); }
  catch (Exception e) { throw new RuntimeException(e); }
 }
 static Object call(Object owner, String name, Class<?>[] types, Object... args) throws Exception {
  Method method = owner.getClass().getDeclaredMethod(name, types);
  method.setAccessible(true);
  try { return method.invoke(owner, args); }
  catch (InvocationTargetException e) { throw (Exception) e.getCause(); }
 }

 static final class Fault {
  final String account, week; final Path file; byte[] profile; final LocalTutorialStore.Progress p; final LocalEventEngine engine;
  Fault(Path root, Path assetsPath, LocalProfileStore store, LocalTutorialStore tutorials, LocalEventCatalog events, LocalNewbeeCatalog newbees, String account, String week) throws Exception {
   this.account = account; this.week = week;
   file = root.resolve("profiles/" + account + ".bson");
   String fixture = System.getProperty("f7.profile");
   profile = baseProfile(read(fixture == null ? assetsPath.resolve("new_player.bson") : Paths.get(fixture)), account, week);
   Files.write(file, profile);
   p = progress(week);
   byte[] normalized = store.load(account, p);
   if (!Arrays.equals(normalized, profile)) { profile = normalized; Files.write(file, profile); }
   engine = new LocalEventEngine(events, newbees, p, 0, profile, true);
  }
 }
 static final class FailStream extends OutputStream {
  final ByteArrayOutputStream buffer = new ByteArrayOutputStream(); boolean armed = true, fired;
  public synchronized void write(int value) throws IOException { buffer.write(value); check(); }
  public synchronized void write(byte[] value, int offset, int length) throws IOException { buffer.write(value, offset, length); check(); }
  void check() throws IOException {
   if (!armed) return;
   byte[] data = buffer.toByteArray(), marker = md5("combatOfflineReward");
   for (int i = 0; i + marker.length <= data.length; i++) {
    boolean match = true;
    for (int j = 0; j < marker.length; j++) if (data[i + j] != marker[j]) { match = false; break; }
    if (match) { armed = false; fired = true; throw new IOException("injected first combatOfflineReward frame failure"); }
   }
  }
 }
 static void admitFault(LocalGatewayServer gateway, String account, LocalTutorialStore.Progress progress, LocalEventEngine engine, int seq, int callback) throws Exception {
  ByteArrayOutputStream out = new ByteArrayOutputStream();
  byte[] envelope = BsonLite.document("w", BsonLite.document("m", "combatOfflineRequest", "p", request(SCENE, AREA), "r", seq), "_cbid_", callback);
  call(gateway, "handleReliableRpc", new Class<?>[] {OutputStream.class, byte[].class, byte[].class, String.class, LocalTutorialStore.Progress.class, LocalEventEngine.class, Set.class, Set.class, Map.class, Set.class},
   out, FRAME_ID, envelope, account, progress, engine, new HashSet<Integer>(), new HashSet<Integer>(), new HashMap<Integer, Object>(), new HashSet<Integer>());
  ProtoLite.EntityMessage reply = frame(frames(out.toByteArray()), "combatOfflineReply");
  check(reply != null && BsonLite.intValue(reply.parameters, "t") == 1, "fault admission " + account);
 }
 static void finishRaw(LocalGatewayServer gateway, String account, LocalTutorialStore.Progress progress, LocalEventEngine engine, OutputStream out, byte[] request) throws Exception {
  call(gateway, "handleCombatOfflineFinish", new Class<?>[] {OutputStream.class, byte[].class, byte[].class, String.class, LocalTutorialStore.Progress.class, LocalEventEngine.class, Set.class, Set.class},
   out, FRAME_ID, request, account, progress, engine, new HashSet<Integer>(), new HashSet<Integer>());
 }
 static File tutorialFile(LocalTutorialStore tutorials, String account) throws Exception {
  java.lang.reflect.Method method = LocalTutorialStore.class.getDeclaredMethod("fileFor", String.class);
  method.setAccessible(true);
  return (File) method.invoke(tutorials, account);
 }
 static void admitFault(LocalGatewayServer gateway, Fault fault, int seq, int callback) throws Exception {
  ByteArrayOutputStream out = new ByteArrayOutputStream();
  byte[] envelope = BsonLite.document("w", BsonLite.document("m", "combatOfflineRequest", "p", request(SCENE, AREA), "r", seq), "_cbid_", callback);
  call(gateway, "handleReliableRpc", new Class<?>[] {OutputStream.class, byte[].class, byte[].class, String.class, LocalTutorialStore.Progress.class, LocalEventEngine.class, Set.class, Set.class, Map.class, Set.class},
   out, FRAME_ID, envelope, fault.account, fault.p, fault.engine, new HashSet<Integer>(), new HashSet<Integer>(), new HashMap<Integer, Object>(), new HashSet<Integer>());
  ProtoLite.EntityMessage reply = frame(frames(out.toByteArray()), "combatOfflineReply");
  check(reply != null && BsonLite.intValue(reply.parameters, "t") == 1, "fault admission " + fault.account);
 }
 static void finishFault(LocalGatewayServer gateway, String account, LocalTutorialStore.Progress progress, LocalEventEngine engine, OutputStream out, int win) throws Exception {
  call(gateway, "handleCombatOfflineFinish", new Class<?>[] {OutputStream.class, byte[].class, byte[].class, String.class, LocalTutorialStore.Progress.class, LocalEventEngine.class, Set.class, Set.class},
   out, FRAME_ID, finishRequest(SCENE, AREA, win), account, progress, engine, new HashSet<Integer>(), new HashSet<Integer>());
 }
 static void finishFault(LocalGatewayServer gateway, Fault fault, OutputStream out, int win) throws Exception {
  finishFault(gateway, fault.account, fault.p, fault.engine, out, win);
 }

 /** Foreign ProfileProvider must fall through to the original Store call. */
 static final class ForeignProvider implements LocalGatewayServer.ProfileProvider {
  int economyCalls; String action; String account; byte[] request;
  public boolean ensureHero(String account, int hero) { return false; }
  public byte[] load(String account, LocalTutorialStore.Progress progress) { return null; }
  public byte[] snapshot(String account, LocalTutorialStore.Progress progress) { return null; }
  public void savePlayerName(String account, String name) {}
  public LocalCommerceEngine.Result updateCommerce(String account, String action, byte[] request) { return null; }
  public LocalEconomyEngine.Result updateEconomy(String account, String action, byte[] request, LocalTutorialStore.Progress progress) {
   economyCalls++; this.action = action; this.account = account; this.request = request;
   return new LocalEconomyEngine.Result(new byte[] {1, 2, 3});
  }
  public LocalProfileEngine.Result updateProfile(String account, String action, byte[] request) { return null; }
  public LocalResourceEngine.Result updateResources(String account, String action, byte[] request) { return null; }
  public LocalResourceEngine.Result updateServices(String account, String action, byte[] request, LocalTutorialStore.Progress progress) { return null; }
 }

 public static void main(String[] args) throws Exception {
  Path assetsPath = Paths.get(args[0]);
  Path classes7 = Paths.get(args[1]);
  Path framesJar = Paths.get(args[2]);
  Path production = Paths.get(args[3]);
  Path resultPath = Paths.get(args[4]);
  File assets = assetsPath.toFile();
  Context prepareContext = new Context(assets, new AssetManager(assets));
  CoreDrawPolicy.prepare(prepareContext);
  HistoryDrawPolicy.prepare(prepareContext);
  SelectorPolicy.prepare(prepareContext);
  OfflineMechanismGateway.prepare(prepareContext);
  StoryMissionBridge.prepare(prepareContext);
  StoryCityPolicy.prepare(prepareContext);
  StoryCityCocPolicy.prepare(prepareContext);

  LocalEventCatalog events = new LocalEventCatalog(new FileInputStream(new File(assets, "event_graph.tsv")));
  LocalNewbeeCatalog newbees = new LocalNewbeeCatalog(new FileInputStream(new File(assets, "newbee_graph.tsv")));
  LocalPatrolCatalog patrols = new LocalPatrolCatalog(new FileInputStream(new File(assets, "patrol.tsv")));
  LocalCombatCatalog combat = new LocalCombatCatalog(
   new FileInputStream(new File(assets, "combat_skills.tsv")),
   new FileInputStream(new File(assets, "combat_attrs.tsv")),
   new FileInputStream(new File(assets, "suppression.tsv")),
   new FileInputStream(new File(assets, "growth.tsv")),
   new FileInputStream(new File(assets, "home.tsv")));

  Path root = Files.createTempDirectory("story-coc-gateway-");
  Files.createDirectories(root.resolve("profiles"));
  Path profileFile = root.resolve("profiles/" + ACCOUNT + ".bson");
  Context context = new Context(root.toFile(), new AssetManager(assets));
  LocalProfileStore store = new LocalProfileStore(context);
  LocalTutorialStore tutorials = new LocalTutorialStore(context);
  String fixture = System.getProperty("f7.profile");
  byte[] profile = baseProfile(read(fixture == null ? Paths.get(assetsPath.toString(), "new_player.bson") : Paths.get(fixture)));
  Files.write(profileFile, profile);
  LocalTutorialStore.Progress p = progress();
  byte[] normalized = store.load(ACCOUNT, p);
  if (!Arrays.equals(normalized, profile)) { profile = normalized; Files.write(profileFile, profile); }
  LocalEventEngine engine = new LocalEventEngine(events, newbees, p, 0, profile, true);
  StoryCityCocPolicy.Admission fixtureAdmission = StoryCityCocPolicy.admit(p, profile, SCENE, request(SCENE, AREA));
  check(fixtureAdmission.allowed, "fixture admission " + fixtureAdmission.reason);
  byte[] gatewayProfile = store.snapshot(ACCOUNT, p);
  StoryCityCocPolicy.Admission gatewayAdmission = StoryCityCocPolicy.admit(p, gatewayProfile, SCENE, request(SCENE, AREA));
  check(gatewayAdmission.allowed, "gateway snapshot admission " + gatewayAdmission.reason);
  check(combat.supportsHero(135), "combat catalog supports hero 135");
  check(LocalCityProgress.area(SCENE) != 0, "gateway area mapping for scene " + SCENE + " area=" + LocalCityProgress.area(SCENE));
  LocalGatewayServer gateway = new LocalGatewayServer(0, null, new FailureSafeProfileProvider(store), tutorials, events, newbees, combat, patrols, (status, message) -> {});

  // Real admission entry: reliable RPC combatOfflineRequest.
  ByteArrayOutputStream admissionOut = new ByteArrayOutputStream();
  byte[] admissionEnvelope = BsonLite.document("w", BsonLite.document("m", "combatOfflineRequest", "p", request(SCENE, AREA), "r", 7001), "_cbid_", 41);
  call(gateway, "handleReliableRpc", new Class<?>[] {OutputStream.class, byte[].class, byte[].class, String.class, LocalTutorialStore.Progress.class, LocalEventEngine.class, Set.class, Set.class, Map.class, Set.class},
   admissionOut, FRAME_ID, admissionEnvelope, ACCOUNT, p, engine, new HashSet<Integer>(), new HashSet<Integer>(), new HashMap<Integer, Object>(), new HashSet<Integer>());
  List<ProtoLite.EntityMessage> admissionFrames = frames(admissionOut.toByteArray());
  check(count(admissionFrames, "reliableRpcAck") == 1, "actual reliable ACK");
  ProtoLite.EntityMessage admissionReply = frame(admissionFrames, "combatOfflineReply");
  check(admissionReply != null, "actual combatOfflineReply");
  check(BsonLite.intValue(admissionReply.parameters, "t") == 1, "admission accepted reply type");
  check(BsonLite.intValue(admissionReply.parameters, "s") == SCENE, "admission reply scene");
  byte[] open = read(profileFile);
  check(!BsonLite.keys(doc(open, "q7Battle")).isEmpty(), "real Store begin wrote q7Battle");
  check(p.processingEvents.contains(COMPLETION), "pending mission event after begin");
  LocalTutorialStore.Progress persistedAtAdmission = tutorials.load(ACCOUNT);
  check(persistedAtAdmission.processingEvents.contains(COMPLETION), "pending event persisted at admission");
  check(p.patrolActions == 60, "begin spends no action");
  int moneyBefore = money(open);
  line("REAL admission handleReliableRpc/combatOfflineRequest scene=" + SCENE + " area=" + AREA + " reply_t=1 pending=" + COMPLETION + " open_profile=" + hex(open) + " actions=" + p.patrolActions + " money=" + moneyBefore);

  // Real finish consumer for the direct COMBAT_OFFLINE_FINISH frame; win=1 is the fixture battle result.
  ByteArrayOutputStream finishOut = new ByteArrayOutputStream();
  call(gateway, "handleCombatOfflineFinish", new Class<?>[] {OutputStream.class, byte[].class, byte[].class, String.class, LocalTutorialStore.Progress.class, LocalEventEngine.class, Set.class, Set.class},
   finishOut, FRAME_ID, finishRequest(SCENE, AREA, 1), ACCOUNT, p, engine, new HashSet<Integer>(), new HashSet<Integer>());
  List<ProtoLite.EntityMessage> finishFrames = frames(finishOut.toByteArray());
  ProtoLite.EntityMessage rewardFrame = frame(finishFrames, "combatOfflineReward");
  check(rewardFrame != null, "actual combatOfflineReward");
  int rewardWin = BsonLite.intValue(rewardFrame.parameters, "w");
  byte[] reward = BsonLite.documentValue(rewardFrame.parameters, "r");
  check(rewardWin == 1, "reward win flag");
  check(reward != null && BsonLite.keys(reward).size() > 0, "reward document");
  int rewardMoney = BsonLite.intValue(reward, "money");
  check(rewardMoney > 0, "original reward money");
  check(BsonLite.intValue(reward, "sid") == SCENE, "reward scene id");
  byte[] settled = read(profileFile);
  check(money(settled) - moneyBefore == rewardMoney, "one reward delta");
  check(p.patrolActions == 58, "source va2 once");
  check(p.completedEvents.contains(COMPLETION), "completion event traced");
  check(p.eventConditions.get("battle") != null && p.eventConditions.get("battle").contains(SCENE), "battle condition");
  check(BsonLite.keys(doc(settled, "q7Battle")).isEmpty(), "settle clears battle");
  check(!BsonLite.keys(BsonLite.documentValue(doc(settled, "q7BattleReceipts"), "3:" + SCENE)).isEmpty(), "Store receipt");
  check(count(finishFrames, "completeEventReplyEnd") >= 1, "completion frame from original finishStoryCombat");
  LocalTutorialStore.Progress reloaded = tutorials.load(ACCOUNT);
  check(reloaded.completedEvents.contains(COMPLETION), "Progress persisted by finishStoryCombat");
  check(reloaded.patrolActions == 58, "Progress actions persisted");
  String settledHash = hex(settled);
  line("REAL finish handleCombatOfflineFinish win=1 reward_money=" + rewardMoney + " reward_sid=" + SCENE + " settled_profile=" + settledHash + " actions=" + p.patrolActions + " completion=" + COMPLETION + " persisted=true");

  // Replay admission at a new sequence: policy rejects before any Store call.
  ByteArrayOutputStream replayAdmissionOut = new ByteArrayOutputStream();
  byte[] replayAdmissionEnvelope = BsonLite.document("w", BsonLite.document("m", "combatOfflineRequest", "p", request(SCENE, AREA), "r", 7002), "_cbid_", 42);
  call(gateway, "handleReliableRpc", new Class<?>[] {OutputStream.class, byte[].class, byte[].class, String.class, LocalTutorialStore.Progress.class, LocalEventEngine.class, Set.class, Set.class, Map.class, Set.class},
   replayAdmissionOut, FRAME_ID, replayAdmissionEnvelope, ACCOUNT, p, engine, new HashSet<Integer>(), new HashSet<Integer>(), new HashMap<Integer, Object>(), new HashSet<Integer>());
  ProtoLite.EntityMessage replayReply = frame(frames(replayAdmissionOut.toByteArray()), "combatOfflineReply");
  check(replayReply != null, "replay admission reply");
  check(BsonLite.intValue(replayReply.parameters, "t") == 0, "replay admission rejected type");
  check(settledHash.equals(hex(read(profileFile))), "replay admission leaves profile bytes");

  // Duplicate finish: rejected before Store, no second reward, no second completion.
  ByteArrayOutputStream replayFinishOut = new ByteArrayOutputStream();
  call(gateway, "handleCombatOfflineFinish", new Class<?>[] {OutputStream.class, byte[].class, byte[].class, String.class, LocalTutorialStore.Progress.class, LocalEventEngine.class, Set.class, Set.class},
   replayFinishOut, FRAME_ID, finishRequest(SCENE, AREA, 1), ACCOUNT, p, engine, new HashSet<Integer>(), new HashSet<Integer>());
  ProtoLite.EntityMessage replayReward = frame(frames(replayFinishOut.toByteArray()), "combatOfflineReward");
  check(replayReward != null, "replay reward reply");
  check(BsonLite.intValue(replayReward.parameters, "w") == 0, "replay win zero");
  check(settledHash.equals(hex(read(profileFile))), "replay finish leaves profile bytes");
  check(p.patrolActions == 58, "replay spends no action");
  check(p.completedEvents.contains(COMPLETION) && p.eventConditions.get("battle").contains(SCENE), "replay keeps completion once");
  line("REPLAY admission_t=0 finish_w=0 profile_unchanged=true actions=58 money=" + money(read(profileFile)));

  // Post-commit first-frame failure: persisted pending must survive and relogin must complete it.
  Fault fault = new Fault(root, assetsPath, store, tutorials, events, newbees, "host_coc_fault", WEEK + "_fault");
  admitFault(gateway, fault, 7201, 51);
  LocalTutorialStore.Progress faultPersisted = tutorials.load(fault.account);
  check(faultPersisted.processingEvents.contains(COMPLETION), "fault account pending persisted at admission");
  FailStream failStream = new FailStream();
  try { finishFault(gateway, fault, failStream, 1); throw new AssertionError("expected first-frame failure"); }
  catch (IOException expected) { check(failStream.fired, "injected reward-frame failure fired"); }
  byte[] faultSettled = read(fault.file);
  check(!BsonLite.keys(BsonLite.documentValue(doc(faultSettled, "q7BattleReceipts"), "3:" + SCENE)).isEmpty(), "fault receipt committed");
  int faultMoney = money(faultSettled);
  LocalTutorialStore.Progress faultLogin = tutorials.load(fault.account);
  check(!faultLogin.completedEvents.contains(COMPLETION), "completion absent before relogin engine");
  check(faultLogin.processingEvents.contains(COMPLETION), "fault login has persisted pending");
  check(StoryCityCocPolicy.recoverableProgress(faultLogin, faultSettled, SCENE, finishRequest(SCENE, AREA, 1)), "policy recoverableProgress true");
  LocalEventEngine faultLoginEngine = new LocalEventEngine(events, newbees, faultLogin, 0, faultSettled, true);
  ByteArrayOutputStream faultRetry = new ByteArrayOutputStream();
  finishFault(gateway, fault.account, faultLogin, faultLoginEngine, faultRetry, 1);
  ProtoLite.EntityMessage recoverReward = frame(frames(faultRetry.toByteArray()), "combatOfflineReward");
  check(recoverReward != null, "recovery retry emitted combatOfflineReward, w=" + (recoverReward == null ? "none" : BsonLite.intValue(recoverReward.parameters, "w")));
  check(faultLogin.completedEvents.contains(COMPLETION), "finish retry recovered completion 1435");
  check(tutorials.load(fault.account).completedEvents.contains(COMPLETION), "recovered completion persisted");
  check(money(read(fault.file)) == faultMoney, "recovery retry grants no second reward");
  ByteArrayOutputStream faultW0 = new ByteArrayOutputStream();
  finishFault(gateway, fault.account, faultLogin, faultLoginEngine, faultW0, 0);
  ProtoLite.EntityMessage faultW0Reward = frame(frames(faultW0.toByteArray()), "combatOfflineReward");
  check(faultW0Reward != null && BsonLite.intValue(faultW0Reward.parameters, "w") == 0, "w0 retry is not a success frame");
  check(money(read(fault.file)) == faultMoney, "post-commit failure grants one reward");
  check(faultLogin.completedEvents.contains(COMPLETION), "completion survives w0 retry");
  line("FAILURE first-frame IOException receipt=true money_once=" + faultMoney + " recovery_retry_completed=true money_once=true w0_retry_completion=true");

  // Negative: the same failure without persisted pending cannot be auto-completed.
  Fault unsaved = new Fault(root, assetsPath, store, tutorials, events, newbees, "host_coc_unsaved", WEEK + "_unsaved");
  admitFault(gateway, unsaved, 7202, 52);
  LocalTutorialStore.Progress cleared = tutorials.load(unsaved.account);
  cleared.processingEvents.remove(COMPLETION);
  tutorials.save(unsaved.account, cleared);
  FailStream unsavedFail = new FailStream();
  try { finishFault(gateway, unsaved, unsavedFail, 1); throw new AssertionError("expected unsaved-pending frame failure"); }
  catch (IOException expected) { check(unsavedFail.fired, "unsaved injection fired"); }
  byte[] unsavedSettled = read(unsaved.file);
  int unsavedMoney = money(unsavedSettled);
  LocalTutorialStore.Progress unsavedLogin = tutorials.load(unsaved.account);
  LocalEventEngine unsavedLoginEngine = new LocalEventEngine(events, newbees, unsavedLogin, 0, unsavedSettled, true);
  ByteArrayOutputStream unsavedRetry = new ByteArrayOutputStream();
  finishFault(gateway, unsaved.account, unsavedLogin, unsavedLoginEngine, unsavedRetry, 1);
  check(!unsavedLogin.completedEvents.contains(COMPLETION), "unsaved case remains unrecoverable");
  check(!unsavedLogin.completedEvents.contains(COMPLETION), "unsaved pending is not auto-completed");
  ByteArrayOutputStream unsavedW0 = new ByteArrayOutputStream();
  finishFault(gateway, unsaved.account, unsavedLogin, unsavedLoginEngine, unsavedW0, 0);
  check(money(read(unsaved.file)) == unsavedMoney, "unsaved case grants one reward");
  check(!unsavedLogin.completedEvents.contains(COMPLETION), "w0 retry leaves completion absent without pending");
  line("NEGATIVE unsaved pending receipt=true money_once=" + unsavedMoney + " relogin_auto_completed=false completion_after_w0=false");

  // 1) Store begin committed without a Progress save (the save-failure state): cold retry preserves fight identity.
  Fault beginFault = new Fault(root, assetsPath, store, tutorials, events, newbees, "host_coc_beginsave", WEEK + "_b1");
  StoryCityCocPolicy.Settlement beginOnly = StoryCityCocPolicy.begin(store, beginFault.account, beginFault.p, beginFault.profile, SCENE, request(SCENE, AREA));
  check(beginOnly.accepted, "fixture Store begin committed");
  byte[] beginCommitted = read(beginFault.file);
  String openFight = BsonLite.stringValue(doc(beginCommitted, "q7Battle"), "f");
  check(openFight != null && !openFight.isEmpty(), "begin committed fight identity");
  LocalTutorialStore.Progress beginCold = progress(beginFault.week);
  LocalEventEngine beginEngine = new LocalEventEngine(events, newbees, beginCold, 0, beginCommitted, true);
  admitFault(gateway, beginFault.account, beginCold, beginEngine, 7302, 62);
  byte[] beginReopened = read(beginFault.file);
  check(openFight.equals(BsonLite.stringValue(doc(beginReopened, "q7Battle"), "f")), "cold retry preserves fight identity");
  check(beginCold.patrolActions == 60, "cold retry costs no action");
  line("BEGIN-SAVE-FAIL fight_preserved=true actions=" + beginCold.patrolActions);

  // 2) Cold login already restored battle: completion missing must not trigger recovery.
  Fault battleFault = new Fault(root, assetsPath, store, tutorials, events, newbees, "host_coc_battlerestore", WEEK + "_b2");
  admitFault(gateway, battleFault, 7311, 63);
  FailStream battleFail = new FailStream();
  try { finishFault(gateway, battleFault, battleFail, 1); throw new AssertionError("expected battle-restore failure"); }
  catch (IOException expected) {}
  byte[] battleSettled = read(battleFault.file);
  int battleMoney = money(battleSettled);
  LocalTutorialStore.Progress battleLogin = tutorials.load(battleFault.account);
  LocalEventEngine battleEngine = new LocalEventEngine(events, newbees, battleLogin, 0, battleSettled, true);
  battleLogin.eventConditions.computeIfAbsent("battle", key -> new LinkedHashSet<Integer>()).add(SCENE);
  check(!StoryCityCocPolicy.recoverableProgress(battleLogin, battleSettled, SCENE, finishRequest(SCENE, AREA, 1)), "battle restored blocks recovery");
  ByteArrayOutputStream battleOut = new ByteArrayOutputStream();
  finishFault(gateway, battleFault.account, battleLogin, battleEngine, battleOut, 1);
  check(!battleLogin.completedEvents.contains(COMPLETION), "battle-present no recovery");
  check(money(read(battleFault.file)) == battleMoney, "battle-present no reward");
  line("BATTLE-RESTORED recovery=false completion=false money_once=true");

  // 3) Wrong type/area/party must not pass the recovery bindings.
  Fault bindFault = new Fault(root, assetsPath, store, tutorials, events, newbees, "host_coc_bind", WEEK + "_b3");
  admitFault(gateway, bindFault, 7321, 64);
  FailStream bindFail = new FailStream();
  try { finishFault(gateway, bindFault, bindFail, 1); throw new AssertionError("expected bind failure"); }
  catch (IOException expected) {}
  byte[] bindSettled = read(bindFault.file);
  int bindMoney = money(bindSettled);
  LocalTutorialStore.Progress bindLogin = tutorials.load(bindFault.account);
  LocalEventEngine bindEngine = new LocalEventEngine(events, newbees, bindLogin, 0, bindSettled, true);
  check(StoryCityCocPolicy.recoverableProgress(bindLogin, bindSettled, SCENE, finishRequest(SCENE, AREA, 1)), "recovery base eligible");
  byte[][] wrong = {
   BsonLite.document("t", 2, "s", SCENE, "d", BsonLite.document("a", AREA), "h", Arrays.asList(135), "w", 1, "x", Collections.emptyList()),
   finishRequest(SCENE, AREA + 1, 1),
   BsonLite.document("t", 1, "s", SCENE, "d", BsonLite.document("a", AREA), "h", Arrays.asList(134), "w", 1, "x", Collections.emptyList())
  };
  for (byte[] bad : wrong) {
   ByteArrayOutputStream badOut = new ByteArrayOutputStream();
   finishRaw(gateway, bindFault.account, bindLogin, bindEngine, badOut, bad);
   ProtoLite.EntityMessage badReward = frame(frames(badOut.toByteArray()), "combatOfflineReward");
   check(badReward != null && BsonLite.intValue(badReward.parameters, "w") == 0, "wrong binding rejected");
   check(!bindLogin.completedEvents.contains(COMPLETION), "wrong binding no completion");
   check(money(read(bindFault.file)) == bindMoney, "wrong binding no reward");
  }
  LocalEconomyEngine.Result originalReplay = store.updateEconomy(bindFault.account, "finish", finishRequest(SCENE, AREA, 1), bindLogin);
  check(originalReplay.replay && money(read(bindFault.file)) == bindMoney, "original Store replay comparison");
  line("WRONG-BINDINGS type/area/party rejected completion=false money_once=true original_store_replay=true");

  // Foreign provider falls through to the original Store method, not COC admission.
  ForeignProvider foreign = new ForeignProvider();
  Method beginHelper = LocalGatewayServer.class.getDeclaredMethod("q7StoryCityCocBegin", LocalGatewayServer.ProfileProvider.class, String.class, LocalTutorialStore.class, byte[].class, LocalTutorialStore.Progress.class);
  beginHelper.setAccessible(true);
  Object foreignResult = beginHelper.invoke(null, foreign, ACCOUNT, tutorials, request(SCENE, AREA), p);
  check(foreignResult instanceof LocalEconomyEngine.Result, "foreign begin result");
  check(foreign.economyCalls == 1 && "begin".equals(foreign.action), "foreign begin delegates original Store");
  ForeignProvider foreignFinish = new ForeignProvider();
  Method finishHelper = LocalGatewayServer.class.getDeclaredMethod("q7StoryCityCocFinish", LocalGatewayServer.ProfileProvider.class, String.class, String.class, byte[].class, LocalTutorialStore.Progress.class);
  finishHelper.setAccessible(true);
  Object foreignFinishResult = finishHelper.invoke(null, foreignFinish, ACCOUNT, "finish", finishRequest(SCENE, AREA, 1), p);
  check(foreignFinishResult instanceof LocalEconomyEngine.Result, "foreign finish result");
  check(foreignFinish.economyCalls == 1 && "finish".equals(foreignFinish.action), "foreign finish delegates original Store");
  line("FOREIGN provider fallback begin/finish updateEconomy calls=1/1");

  JSONObject result = new JSONObject();
  result.put("format", "story-city-coc-gateway-seam-v1");
  result.put("status", "PASS");
  result.put("checks", checks);
  result.put("scene", SCENE);
  result.put("real_caller_admission", "LocalGatewayServer.handleReliableRpc(combatOfflineRequest)");
  result.put("real_caller_finish", "LocalGatewayServer.handleCombatOfflineFinish (the exact handleClient COMBAT_OFFLINE_FINISH consumer)");
  result.put("fixture", "route-27-1 profile/progress snapshot; finish win=1 is an explicit fixture battle result, not a natural battle");
  result.put("classes7_sha256", hex(read(classes7)));
  result.put("frames_sha256", hex(read(framesJar)));
  result.put("production_classes", production.toString());
  result.put("open_profile_sha256", hex(open));
  result.put("settled_profile_sha256", settledHash);
  result.put("reward_money", rewardMoney);
  result.put("actions_after", p.patrolActions);
  result.put("lines", new org.json.JSONArray(lines));
  Files.write(resultPath, result.toString(2).getBytes(StandardCharsets.UTF_8));
  System.out.println("PASS checks=" + checks + " status=PASS real Gateway entry + real Store/Progress/EventEngine, replay no double reward");

  gateway.close();
  try (java.util.stream.Stream<Path> stream = Files.walk(root)) {
   for (Path path : (Iterable<Path>) stream.sorted(Comparator.reverseOrder())::iterator) Files.delete(path);
  }
 }
}
