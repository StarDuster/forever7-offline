package com.project7.localmanager;

import android.content.*;
import android.content.res.*;
import java.io.*;
import java.nio.file.*;
import java.util.*;

/**
 * Post-1140-commit projection host for menu10 selector11.
 *
 * <p>The manager frame exposes no public original event-completion entry, so
 * this host cannot start event 1129/1140 itself. It begins from an explicit
 * post-commit snapshot (Progress completions + route/menu profile) and then
 * drives the real packaged descriptor, the real original Store begin/finish
 * transactions and the original cityOutcome trace. A missing or baseline 1140
 * is rejected by the commit gate. The genuine event-commit -> effects ->
 * Gateway query/admission/settlement -> 1132 consumer chain is verified by the
 * v38 Java host StoryMenu10GatewayHost through the private
 * LocalGatewayServer entries; no Python/Legacy backend substitutes for it.</p>
 */
public final class StoryMenuProductionHost {
 private static final String ACCOUNT = "host_menu10_selector11";
 private static final String WEEK = "menu10-selector11-week";
 private static int checks;
 private static File assets;

 private static void check(boolean value, String why) {
  checks++;
  if (!value) throw new AssertionError(why);
 }

 private static byte[] doc(byte[] profile, String key) {
  byte[] d = BsonLite.documentValue(profile, key);
  return d == null ? BsonLite.EMPTY_DOCUMENT : d;
 }

 private static byte[] request(int scene, int area, int type, List<Integer> heroes) {
  return BsonLite.document("t", type, "s", scene, "d", BsonLite.document("a", area), "h", heroes);
 }

 private static byte[] finish(int scene, int area, int win, List<Integer> heroes) {
  return BsonLite.document("t", 1, "s", scene, "d", BsonLite.document("a", area),
      "h", heroes, "w", win, "x", Collections.emptyList());
 }

 private static boolean same(byte[] a, byte[] b) {
  return Arrays.equals(a, b);
 }

 private static byte[] fixture() throws IOException {
  byte[] profile = BsonLite.withAccountIdentity(
      Files.readAllBytes(new File(assets, "new_player.bson").toPath()), ACCOUNT, 900781);
  profile = BsonLite.withProfileDocument(profile, "weeknum", BsonLite.document("w", 8, "d", 0, "av", 60));
  profile = BsonLite.withProfileDocument(profile, "std", BsonLite.document("rt", "10-6"));
  profile = BsonLite.withProfileInt(profile, "q7ChapterMenu", 10);
  profile = BsonLite.withProfileDocument(profile, "q7WenziCity",
      BsonLite.document("version", 1, "week", 8, "cycle", WEEK));
  profile = BsonLite.withProfileArray(profile, "q7WeekEventBaseline", Collections.emptyList());
  profile = BsonLite.withProfileDocument(profile, "city", BsonLite.document("av", 60, "fv", 50));
  for (int hero : new int[]{135, 136, 137}) profile = BsonLite.withHero(profile, hero);
  return profile;
 }

 /** Explicit post-1140 commit snapshot; not an event completion driver. */
 private static LocalTutorialStore.Progress committedSnapshot() {
  LocalTutorialStore.Progress p = LocalTutorialStore.Progress.fresh();
  p.weekIndex = 8;
  p.weekCommit = WEEK;
  p.initPrologue = false;
  p.inEmergency = false;
  p.processingEvents.clear();
  p.patrolActions = 60;
  for (int event : new int[]{1066, 1129, 1140, 1141}) {
   p.completedEvents.add(event);
   p.eventCompletions.put(event, 1);
   p.eventDays.put(event, "8:0");
  }
  return p;
 }

 private static void rejectBegin(LocalProfileStore store, LocalTutorialStore.Progress p, byte[] profile,
                                 List<Integer> team, String why) throws IOException {
  try {
   LocalEconomyEngine.Result result = store.updateEconomy(ACCOUNT, "begin", request(320, 6, 1, team), p);
   check(!result.accepted, why + " accepted");
  } catch (IllegalArgumentException expected) {
   check(true, why);
  }
 }

 public static void main(String[] args) throws Exception {
  assets = new File(args[0]);
  Path scratch = new File(args[1]).toPath();
  Files.createDirectories(scratch);
  Context context = new Context(assets, new AssetManager(assets));
  CoreDrawPolicy.prepare(context);
  HistoryDrawPolicy.prepare(context);
  SelectorPolicy.prepare(context);
  StoryMissionBridge.prepare(context);
  StoryMenuShared.prepare(context);
  StoryCityPolicy.prepare(context);
  LocalEventCatalog events = new LocalEventCatalog(new FileInputStream(new File(assets, "event_graph.tsv")));
  LocalNewbeeCatalog newbees = new LocalNewbeeCatalog(new ByteArrayInputStream(new byte[0]));
  LocalTutorialStore.Progress p = committedSnapshot();
  byte[] profile = fixture();
  StoryMenuShared.Descriptor descriptor = StoryMenuShared.resolveSelector11(profile, p, 1);
  check(descriptor.catalogToken.equals(StoryMissionBridge.specialToken()), "query/admission/victory share the packaged descriptor");
  LocalTutorialStore.Progress missing = committedSnapshot();
  missing.completedEvents.remove(Integer.valueOf(1140));
  missing.eventCompletions.remove(1140);
  missing.eventDays.remove(1140);
  try {
   StoryMenuShared.cityEffect1140(profile, missing);
   check(false, "missing 1140 must not publish city effects");
  } catch (IllegalStateException expected) {
   check(true, "missing 1140 is rejected by the commit gate");
  }
  byte[] baseline = BsonLite.withProfileArray(profile, "q7WeekEventBaseline", Collections.singletonList(1140));
  try {
   StoryMenuShared.cityEffect1140(baseline, p);
   check(false, "baseline 1140 must not publish city effects");
  } catch (IllegalStateException expected) {
   check(true, "baseline 1140 is rejected by the commit gate");
  }
  check(StoryMenuShared.capability(10, events), "menu10 capability with original 1129 effect");
  byte[] cityEffect = StoryMenuShared.cityEffect1140(profile, p);
  check(BsonLite.intArrayValues(cityEffect, "areaFight").equals(Collections.singletonList(6)), "committed 1140 areaFight6");
  check(Integer.valueOf(11).equals(BsonLite.intValue(doc(cityEffect, "areaSpecialStage"), "6")), "committed 1140 areaSpecialStage6=11");
  check(StoryMissionBridge.area(320) == 6, "mission320 area6 through the bridge descriptor");
  check(BsonLite.intValue(StoryMissionBridge.stages(p, 6, profile), "cs") == 320, "area query returns 320 before a win");
  check(StoryMissionBridge.status(p, 6, profile) == 1, "area6 FIGHT1 before a win");

  List<Integer> team = Arrays.asList(135, 136, 137);
  check(StoryMissionBridge.partyAllowed(request(320, 6, 1, team)), "selector11 party shape");
  check(!StoryMissionBridge.partyAllowed(request(320, 6, 2, team)), "stage wire type1 only");
  check(!StoryMissionBridge.partyAllowed(request(320, 5, 1, team)), "area6 only");
  check(!StoryMissionBridge.partyAllowed(request(320, 6, 1, Arrays.asList(135, 136, 137, 138))), "four heroes rejected");
  check(!StoryMissionBridge.partyAllowed(request(320, 6, 1, Arrays.asList(135, 135))), "duplicate heroes rejected");

  Path root = Files.createTempDirectory(scratch, "menu10-store-");
  Files.createDirectory(root.resolve("profiles"));
  Path profileFile = root.resolve("profiles/" + ACCOUNT + ".bson");
  Files.write(profileFile, profile);
  LocalProfileStore store = new LocalProfileStore(new Context(root.toFile(), new AssetManager(assets)));
  LocalTutorialStore tutorials = new LocalTutorialStore(new Context(root.toFile(), new AssetManager(assets)));

  Map<Integer, Integer> fatigueByHero = new HashMap<>();
  for (int hero : team) {
   Integer value = BsonLite.intValue(BsonLite.profileHeroDocument(profile, hero), "cf");
   check(value != null && value > 5, "fixture hero carries the original fatigue resource");
   fatigueByHero.put(hero, value);
  }
  int fatigue = fatigueByHero.get(135);
  LocalEconomyEngine.Result begin = store.updateEconomy(ACCOUNT, "begin", request(320, 6, 1, team), p);
  check(begin.accepted && !begin.replay, "real Store begin accepted");
  check(p.patrolActions == 60, "begin does not spend actions");
  byte[] open = Files.readAllBytes(profileFile);
  check(!BsonLite.keys(doc(open, "q7Battle")).isEmpty(), "begin writes original q7Battle pending");
  check(BsonLite.intValue(StoryMissionBridge.stages(p, 6, open), "cs") == 320, "pending keeps stage 320");

  LocalEconomyEngine.Result loss = store.updateEconomy(ACCOUNT, "finish", finish(320, 6, 0, team), p);
  byte[] lost = Files.readAllBytes(profileFile);
  check(loss.accepted && loss.win == 0, "loss accepted without win");
  check(p.patrolActions == 60, "loss spends no actions");
  check(BsonLite.intValue(BsonLite.profileHeroDocument(lost, 135), "cf") == fatigue, "loss spends no hero fatigue");
  check(BsonLite.keys(doc(doc(lost, "q7BattleReceipts"), "8:320")).isEmpty(), "loss writes no victory receipt");
  check(p.eventConditions.get("battle") == null || !p.eventConditions.get("battle").contains(320), "loss writes no battle trace");
  check(BsonLite.intValue(StoryMissionBridge.stages(p, 6, lost), "cs") == 320, "loss keeps stage 320 retryable");

  LocalEconomyEngine.Result retry = store.updateEconomy(ACCOUNT, "begin", request(320, 6, 1, team), p);
  check(retry.accepted, "retry after loss begins");
  byte[] opened = Files.readAllBytes(profileFile);
  LocalEventEngine engine = new LocalEventEngine(events, newbees, p, 0, opened, true);
  check(p.eventConditions.get("battle") == null || !p.eventConditions.get("battle").contains(320), "no hand-set win before finish");
  engine.refreshProfile(opened);
  check(!p.availableEvents.contains(1132), "1132 is not offered before a real win");

  LocalEconomyEngine.Result win = store.updateEconomy(ACCOUNT, "finish", finish(320, 6, 1, team), p);
  byte[] settled = Files.readAllBytes(profileFile);
  check(win.accepted && win.win == 1, "real Store win accepted");
  check(p.patrolActions == 58, "original va2 cost spent once");
  for (int hero : team)
   check(BsonLite.intValue(BsonLite.profileHeroDocument(settled, hero), "cf") == fatigueByHero.get(hero) - 5,
       "original mission fatigue5 spent once per party hero " + hero);
  check(!BsonLite.keys(doc(doc(settled, "q7BattleReceipts"), "8:320")).isEmpty(), "win writes original victory receipt");
  check(!same(opened, settled), "win commits once");
  check(BsonLite.intValue(StoryMissionBridge.stages(p, 6, settled), "cs") == 0, "win advances the shared stage projection");
  check(StoryMissionBridge.status(p, 6, settled) == 0, "win advances area6 status");
  engine.refreshProfile(settled);
  engine.trace("battle", Arrays.asList(320));
  check(p.eventConditions.get("battle") != null && p.eventConditions.get("battle").contains(320), "real battle trace writes 320");
  check(p.availableEvents.contains(1132), "original cityOutcome offers successEvent1132");
  check(!p.completedEvents.contains(1132) && !p.processingEvents.contains(1132), "1132 is offered, not hand-completed");
  check(BsonLite.keys(doc(settled, "q7Battle")).isEmpty(), "win clears pending q7Battle");

  LocalEconomyEngine.Result duplicate = store.updateEconomy(ACCOUNT, "finish", finish(320, 6, 1, team), p);
  check(duplicate.replay, "duplicate finish is replay");
  check(p.patrolActions == 58 && same(settled, Files.readAllBytes(profileFile)), "replay spends and commits nothing");
  check(BsonLite.intValue(BsonLite.profileHeroDocument(Files.readAllBytes(profileFile), 135), "cf") == fatigue - 5,
      "replay spends no extra fatigue");
  rejectBegin(store, p, settled, team, "completed stage rejects a new begin");

  // The original Store cost rule is force-sensitive: below force_recommend5
  // the same mission charges overFatigue25 instead of fatigue5.
  String lowAccount = ACCOUNT + "_lowforce";
  byte[] lowProfile = BsonLite.withAccountIdentity(fixture(), lowAccount, 900783);
  lowProfile = BsonLite.withProfileDocument(lowProfile, "city", BsonLite.document("av", 60, "fv", 0));
  Files.write(root.resolve("profiles/" + lowAccount + ".bson"), lowProfile);
  LocalTutorialStore.Progress low = committedSnapshot();
  int lowFatigue = BsonLite.intValue(BsonLite.profileHeroDocument(lowProfile, 135), "cf");
  LocalEconomyEngine.Result lowBegin = store.updateEconomy(lowAccount, "begin", request(320, 6, 1, team), low);
  LocalEconomyEngine.Result lowWin = store.updateEconomy(lowAccount, "finish", finish(320, 6, 1, team), low);
  byte[] lowSettled = Files.readAllBytes(root.resolve("profiles/" + lowAccount + ".bson"));
  check(lowBegin.accepted && lowWin.accepted && lowWin.win == 1, "low-force Store begin/win accepted");
  check(low.patrolActions == 58, "overFatigue path still spends va2 actions once");
  check(BsonLite.intValue(BsonLite.profileHeroDocument(lowSettled, 135), "cf") == lowFatigue - 25,
      "force below recommend5 charges original overFatigue25");

  tutorials.save(ACCOUNT, p);
  LocalTutorialStore.Progress loaded = tutorials.load(ACCOUNT);
  check(loaded.patrolActions == 58, "actions persist");
  check(loaded.eventConditions.get("battle") != null && loaded.eventConditions.get("battle").contains(320), "battle trace persists");
  check(loaded.availableEvents.contains(1132), "1132 availability persists");
  Path copy = scratch.resolve("menu10-final.bson");
  Files.write(copy, settled);
  byte[] reloaded = Files.readAllBytes(copy);
  check(same(settled, reloaded), "profile save/reload byte-identical");
  check(BsonLite.intValue(BsonLite.profileHeroDocument(reloaded, 135), "cf") == fatigue - 5,
      "fatigue5 persists across reload");
  check(BsonLite.intValue(StoryMissionBridge.stages(loaded, 6, reloaded), "cs") == 0, "reloaded stage remains completed");
  check(!BsonLite.keys(doc(doc(reloaded, "q7BattleReceipts"), "8:320")).isEmpty(), "reloaded receipt remains");

  System.out.println("PASS " + checks + " menu10 selector11 post-commit query/store/loss/va2/fatigue5/win/replay/1132 checks");
 }
}
