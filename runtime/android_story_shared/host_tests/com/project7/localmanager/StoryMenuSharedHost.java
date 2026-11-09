package com.project7.localmanager;

import java.io.*;
import java.nio.file.*;
import java.util.*;

/**
 * Finite host evidence for the menu10 selector11 provider and the menu12
 * q7WenziCity initializer. It drives the original manager consumers
 * (LocalWeekEngine entry, LocalStoryRuleRegistry, LocalWenziCityEngine,
 * LocalDalviraHeroEngine, LocalEventCatalog, LocalBlock/BSON) but never writes
 * player files. No APK, D8 or native execution.
 */
public final class StoryMenuSharedHost {
 private static int checks;
 private static File assets;
 private static File scratch;

 private static void check(boolean value, String why) {
  checks++;
  if (!value) throw new AssertionError(why);
 }

 private static byte[] doc(byte[] profile, String key) {
  byte[] d = BsonLite.documentValue(profile, key);
  return d == null ? BsonLite.EMPTY_DOCUMENT : d;
 }

 private static String route(byte[] profile) {
  return BsonLite.stringValue(doc(profile, "std"), "rt");
 }

 private static int menu(byte[] profile) {
  Integer v = BsonLite.intValue(profile, "q7ChapterMenu");
  return v == null ? -1 : v;
 }

 private static byte[] profile(String rt, int menu, int week, String cycle, List<Integer> baseline, int day) {
  return BsonLite.document(
      "std", BsonLite.document("rt", rt, "ed", Arrays.asList(28, 29, 30)),
      "q7ChapterMenu", menu,
      "q7WeekEventBaseline", baseline,
      "weeknum", BsonLite.document("w", week, "d", day),
      "city", BsonLite.document("av", 24),
      "unknown", "preserved");
 }

 private static LocalTutorialStore.Progress progress(int week, String cycle) {
  LocalTutorialStore.Progress p = LocalTutorialStore.Progress.fresh();
  p.weekIndex = week;
  p.weekCommit = cycle;
  p.initPrologue = false;
  p.inEmergency = false;
  p.processingEvents.clear();
  p.patrolRewardPending = false;
  p.patrolActions = 24;
  return p;
 }

 private static void current(LocalTutorialStore.Progress p, int event, int day) {
  p.completedEvents.add(event);
  p.eventCompletions.put(event, 1);
  p.eventDays.put(event, p.weekIndex + ":" + day);
 }

 private static byte[] saveReload(byte[] profile, String name) throws IOException {
  File file = new File(scratch, name);
  Files.write(file.toPath(), profile);
  return Files.readAllBytes(file.toPath());
 }

 private static boolean same(byte[] a, byte[] b) {
  return Arrays.equals(a, b);
 }

 private static void reject(Runnable action, Class<? extends Throwable> type, String why) {
  try {
   action.run();
   check(false, why);
  } catch (Throwable e) {
   check(type.isInstance(e), why + " got " + e.getClass().getSimpleName());
  }
 }

 public static void main(String[] args) throws Exception {
  assets = new File(args[0]);
  scratch = new File(args[1]);
  if (!scratch.isDirectory() && !scratch.mkdirs()) throw new IOException("Scratch");
  StoryMenuShared.prepare(new File(assets, "project7_story_shared"));
  LocalEventCatalog events = new LocalEventCatalog(new FileInputStream(new File(assets, "event_graph.tsv")));
  LocalWeekCatalog weeks = new LocalWeekCatalog(new FileInputStream(new File(assets, "weeks.tsv")));

  // 1. Shared capability is data/state scoped and never a bulk allowlist.
  check(StoryMenuShared.capability(10), "menu10 capability after prepare");
  check(!StoryMenuShared.capability(12), "menu12 capability stays disabled");
  check(!StoryMenuShared.capability(11) && !StoryMenuShared.capability(13) &&
      !StoryMenuShared.capability(25) && !StoryMenuShared.capability(1), "other menus stay closed");
  check(StoryMenuShared.capability(10, events), "menu10 event-catalog capability");
  check(!StoryMenuShared.capability(12, events), "menu12 event-catalog capability stays disabled");
  byte[] e1129 = events.cityEffects.get(1129);
  events.cityEffects.remove(1129);
  check(!StoryMenuShared.capability(10, events), "missing Wenzi effect closes menu10");
  events.cityEffects.put(1129, e1129);

  // 2. Original entry data proves route ids/requires without enabling them.
  check(LocalAlanCityEngine.area(320) == 6, "original mission320 area6");
  check(!LocalStoryEntryPolicy.SUPPORTED.contains(10) && !LocalStoryEntryPolicy.SUPPORTED.contains(12),
      "original allowlist does not contain menu10/12");
  check(weeks.entrances.get(10) == 477 && weeks.entrances.get(12) == 460, "original route/init ids");
  Set<Integer> required = new HashSet<>(Arrays.asList(28, 29, 30));
  check(weeks.requires.get(10) != null && weeks.requires.get(10).contains(required), "menu10 requires 28/29/30");
  check(weeks.requires.get(12) != null && weeks.requires.get(12).contains(required), "menu12 requires 28/29/30");

  // 3. Unprepared city/entry owners leave menu10 closed; menu12 stays closed.
  LocalTutorialStore.Progress entry = progress(8, "entry-week");
  byte[] entryProfile = profile("1", 0, 8, "entry-week", Collections.<Integer>emptyList(), 0);
  for (int m : new int[]{10, 12}) {
   LocalResourceEngine.Result r = LocalWeekEngine.apply(entryProfile, weeks, entry, "requestEnterStory",
       BsonLite.document("i", m));
   boolean message = false, denied = false;
   for (LocalResourceEngine.Reply reply : r.replies) {
    if (reply.method.equals("showMessageStr"))
     message = "此特殊路线的地区初始化尚未接入，已保留进度与黑色信函".equals(BsonLite.stringValue(reply.parameters, "m"));
    if (reply.method.equals("replyEnterStory"))
     denied = Boolean.FALSE.equals(BsonLite.boolValue(reply.parameters, "r"));
   }
   check(message && denied, "original Week entry rejects menu" + m);
   check(same(entryProfile, r.profile), "rejected entry publishes nothing " + m);
  }

  // 4. menu10 selector11 resolution from the original 10-6 handoff + 1140 occurrence.
  LocalTutorialStore.Progress p10 = progress(8, "week-menu10");
  current(p10, 1129, 0);
  current(p10, 1140, 0);
  byte[] alan = profile("10-6", 10, 8, "week-menu10", Collections.<Integer>emptyList(), 0);
  StoryMenuShared.Descriptor desc = StoryMenuShared.resolveSelector11(alan, p10, 1);
  check(desc.area == 6 && desc.bucket == 0 && desc.route.equals("10-6") && desc.selector == 11, "selector key");
  check(desc.groups.equals(Collections.singletonList(Collections.singletonList(320))) &&
      desc.members.equals(Collections.singletonList(320)), "selector membership");
  check(desc.missionSha256.length() == 64 && desc.catalogToken.length() == 64, "catalog evidence hash");
  byte[] stages = StoryMenuShared.stages(desc, Collections.<Integer>emptyList());
  check(BsonLite.intValue(stages, "cs") == 320, "first original section scene");
  check(BsonLite.keys(BsonLite.arrayValue(stages, "sl")).size() == 1, "original group count");
  check(BsonLite.intValue(StoryMenuShared.stages(desc, Collections.singletonList(320)), "cs") == 0, "completed section");
  check(StoryMenuShared.admit(desc, alan, p10, 320, 6, 1), "selector11 admission");
  check(!StoryMenuShared.admit(desc, alan, p10, 321, 6, 1) &&
      !StoryMenuShared.admit(desc, alan, p10, 320, 5, 1) &&
      !StoryMenuShared.admit(desc, alan, p10, 320, 6, 4), "selector11 admission bounds");

  // Exact key and occurrence guards; every rejection is read-only.
  final byte[] alanStable = alan;
  reject(() -> StoryMenuShared.resolveSelector11(alanStable, p10, 5), IllegalStateException.class, "bucket5 has no row");
  reject(() -> StoryMenuShared.resolveSelector11(alanStable, p10, 0), IllegalArgumentException.class, "invalid status");
  byte[] wrongRoute = profile("10-5", 10, 8, "week-menu10", Collections.<Integer>emptyList(), 0);
  reject(() -> StoryMenuShared.resolveSelector11(wrongRoute, p10, 1), IllegalStateException.class, "exact route");
  byte[] wrongMenu = profile("10-6", 11, 8, "week-menu10", Collections.<Integer>emptyList(), 0);
  reject(() -> StoryMenuShared.resolveSelector11(wrongMenu, p10, 1), IllegalStateException.class, "exact menu");
  LocalTutorialStore.Progress no1140 = progress(8, "week-menu10");
  current(no1140, 1129, 0);
  reject(() -> StoryMenuShared.resolveSelector11(alanStable, no1140, 1), IllegalStateException.class, "occurrence required");
  LocalTutorialStore.Progress no1129 = progress(8, "week-menu10");
  current(no1129, 1140, 0);
  reject(() -> StoryMenuShared.resolveSelector11(alanStable, no1129, 1), IllegalStateException.class, "route source required");
  byte[] baselined = profile("10-6", 10, 8, "week-menu10", Arrays.asList(1140), 0);
  reject(() -> StoryMenuShared.resolveSelector11(baselined, p10, 1), IllegalStateException.class, "baseline occurrence excluded");
  LocalTutorialStore.Progress zero = progress(8, "week-menu10");
  current(zero, 1129, 0);
  zero.completedEvents.add(1140);
  zero.eventCompletions.put(1140, 0);
  zero.eventDays.put(1140, "8:0");
  reject(() -> StoryMenuShared.resolveSelector11(alanStable, zero, 1), IllegalStateException.class, "completion must be one");
  StoryMenuShared.Effect real = StoryMenuShared.effect1140();
  reject(() -> StoryMenuShared.resolveSelector11(alanStable, p10, 1,
      new StoryMenuShared.Effect(1140, false, Arrays.asList(6), Collections.singletonMap(6, 11))), IllegalArgumentException.class, "unreleased effect");
  reject(() -> StoryMenuShared.resolveSelector11(alanStable, p10, 1,
      new StoryMenuShared.Effect(1140, true, Arrays.asList(5), Collections.singletonMap(6, 11))), IllegalArgumentException.class, "wrong areaFight");
  reject(() -> StoryMenuShared.resolveSelector11(alanStable, p10, 1,
      new StoryMenuShared.Effect(1141, true, Arrays.asList(6), Collections.singletonMap(6, 11))), IllegalArgumentException.class, "wrong event");
  reject(() -> StoryMenuShared.resolveSelector11(alanStable, p10, 1,
      new StoryMenuShared.Effect(1140, true, Arrays.asList(6), Collections.singletonMap(6, 10))), IllegalArgumentException.class, "wrong selector");
  check(same(alan, alanStable), "selector rejection is read-only");
  byte[] alanReload = saveReload(alan, "menu10-selector.bson");
  check(same(alan, alanReload), "selector profile save/reload");
  check(StoryMenuShared.resolveSelector11(alanReload, p10, 1).catalogToken.equals(desc.catalogToken), "selector token after reload");

  // 5. Original WenziCity consumer initializes the receipt for menu10/rt10-6.
  LocalResourceEngine.Result w10 = new LocalResourceEngine.Result(alan);
  byte[] before10 = w10.profile;
  LocalStoryRuleRegistry.apply(LocalStoryRuleRegistry.Phase.AFTER_ROUTE, w10, events, p10);
  byte[] wenzi10 = doc(w10.profile, "q7WenziCity");
  check(BsonLite.keys(wenzi10).equals(Arrays.asList("version", "week", "cycle")), "original Wenzi receipt keys");
  check(Integer.valueOf(1).equals(BsonLite.intValue(wenzi10, "version")) &&
      Integer.valueOf(8).equals(BsonLite.intValue(wenzi10, "week")) &&
      "week-menu10".equals(BsonLite.stringValue(wenzi10, "cycle")), "original Wenzi receipt binding");
  check(!same(before10, w10.profile), "Wenzi projection published");
  check(w10.replies.stream().anyMatch(r -> r.method.equals("get_all_area_info_reply")), "Wenzi area reply");
  check(StoryMenuShared.capability(10, events), "menu10 capability still scoped");
  check(LocalWenziCityEngine.state(w10.profile, p10, 3) != null &&
      LocalWenziCityEngine.state(w10.profile, p10, 3) == 0, "original Wenzi state after receipt");
  byte[] wenzi10Reload = saveReload(w10.profile, "menu10-wenzi.bson");
  check(Arrays.equals(wenzi10Reload, w10.profile), "menu10 Wenzi save/reload");
  LocalResourceEngine.Result replay10 = new LocalResourceEngine.Result(wenzi10Reload);
  LocalStoryRuleRegistry.apply(LocalStoryRuleRegistry.Phase.AFTER_ROUTE, replay10, events, p10);
  check(same(wenzi10Reload, replay10.profile), "menu10 Wenzi replay idempotent");

  // 6. menu12 initializes q7WenziCity from canonical prior-cycle history; no
  // current 1129 completion and no route13 progress is fabricated.
  LocalTutorialStore.Progress p12 = progress(8, "week-menu12");
  byte[] dalvira = profile("13-3", 12, 8, "week-menu12", Arrays.asList(1129), 0);
  LocalResourceEngine.Result w12 = new LocalResourceEngine.Result(dalvira);
  check(!StoryMenuShared.initializeWenziCity(w12, events, p12), "baseline-only Wenzi history must not create current receipt");
  check(same(dalvira, w12.profile), "baseline-only Wenzi publishes nothing");
  check(BsonLite.keys(doc(w12.profile, "q7WenziCity")).isEmpty(), "baseline-only receipt remains absent");
  check(!StoryMenuShared.dalviraGate(w12.profile, p12, events), "prior history alone does not fabricate route13 progress");
  byte[] wenzi12Reload = saveReload(w12.profile, "menu12-baseline-only.bson");
  check(Arrays.equals(wenzi12Reload, w12.profile), "baseline-only save/reload unchanged");

  // 7. Actual Dalvira route13 consumer runs only with current-cycle Wenzi
  // cooperation, 4203 day3, 6189 day5 and the original hero effect.
  LocalTutorialStore.Progress q12 = progress(8, "week-menu12-live");
  current(q12, 1129, 0);
  current(q12, 1140, 0);
  current(q12, 4203, 3);
  current(q12, 6189, 5);
  byte[] live = profile("13-3", 12, 8, "week-menu12-live", Collections.<Integer>emptyList(), 5);
  LocalResourceEngine.Result liveResult = new LocalResourceEngine.Result(live);
  check(StoryMenuShared.initializeWenziCity(liveResult, events, q12), "menu12 live initializer");
  check(StoryMenuShared.dalviraGate(liveResult.profile, q12, events), "Dalvira gate from original fields");
  LocalStoryRuleRegistry.apply(LocalStoryRuleRegistry.Phase.AFTER_ROUTE, liveResult, events, q12);
  byte[] liveWenzi = doc(liveResult.profile, "q7WenziCity");
  check(Boolean.TRUE.equals(BsonLite.boolValue(liveWenzi, "dalviraDeparture")), "actual DalviraHero consumer");
  byte[] liveReload = saveReload(liveResult.profile, "menu12-dalvira.bson");
  check(BsonLite.boolValue(doc(liveReload, "q7WenziCity"), "dalviraDeparture").booleanValue(), "Dalvira receipt after reload");
  LocalResourceEngine.Result replay12 = new LocalResourceEngine.Result(liveReload);
  LocalStoryRuleRegistry.apply(LocalStoryRuleRegistry.Phase.AFTER_ROUTE, replay12, events, q12);
  check(same(liveReload, replay12.profile), "menu12 replay idempotent");

  // 8. menu12 negative gates: default closed, altered effect, wrong cycle.
  LocalTutorialStore.Progress fresh12 = progress(8, "week-menu12-fresh");
  byte[] freshProfile = profile("13-3", 12, 8, "week-menu12-fresh", Collections.<Integer>emptyList(), 0);
  LocalResourceEngine.Result fresh = new LocalResourceEngine.Result(freshProfile);
  check(!StoryMenuShared.initializeWenziCity(fresh, events, fresh12), "fresh menu12 stays closed");
  check(same(freshProfile, fresh.profile), "fresh menu12 publishes nothing");
  check(!StoryMenuShared.dalviraGate(freshProfile, fresh12, events), "fresh Dalvira gate closed");
  byte[] tampered1129 = BsonLite.document("areaFree", Arrays.asList(4));
  events.cityEffects.put(1129, tampered1129);
  final LocalResourceEngine.Result tampered = new LocalResourceEngine.Result(freshProfile);
  reject(() -> StoryMenuShared.initializeWenziCity(tampered, events, fresh12), IllegalArgumentException.class, "Wenzi effect must be areaFree=[3]");
  check(same(freshProfile, tampered.profile), "tampered effect publishes nothing");
  events.cityEffects.put(1129, e1129);
  byte[] wrongCycle = BsonLite.withProfileDocument(profile("13-3", 12, 8, "week-menu12", Collections.<Integer>emptyList(), 0),
      "q7WenziCity", BsonLite.document("version", 1, "week", 9, "cycle", "old-cycle"));
  LocalResourceEngine.Result old = new LocalResourceEngine.Result(wrongCycle);
  check(!StoryMenuShared.initializeWenziCity(old, events, p12), "baseline-only does not touch an existing binding");
  check(same(wrongCycle, old.profile), "baseline-only leaves wrong-cycle receipt untouched");
  LocalTutorialStore.Progress liveCycle = progress(8, "week-menu12");
  current(liveCycle, 1129, 0);
  current(liveCycle, 1140, 0);
  reject(() -> StoryMenuShared.initializeWenziCity(old, events, liveCycle), IllegalArgumentException.class,
      "already-bound receipt is not rewritten");
  check(same(wrongCycle, old.profile), "wrong-cycle receipt untouched");
  LocalTutorialStore.Progress other = progress(8, "week-menu12");
  byte[] rt10 = profile("10-6", 10, 8, "week-menu12", Arrays.asList(1129), 0);
  LocalResourceEngine.Result otherResult = new LocalResourceEngine.Result(rt10);
  check(!StoryMenuShared.initializeWenziCity(otherResult, events, other), "rt10 owner unchanged");
  check(same(rt10, otherResult.profile), "rt10 owner publishes nothing");

  System.out.println("PASS " + checks + " menu10 selector11 + menu12 WenziCity shared-mechanism checks; original consumers, no bulk entry, synthetic BSON only");
 }
}
