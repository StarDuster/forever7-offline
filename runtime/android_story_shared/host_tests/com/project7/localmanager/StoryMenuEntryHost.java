package com.project7.localmanager;

import android.content.*;
import android.content.res.*;
import java.io.*;
import java.nio.file.Files;
import java.util.*;

/**
 * Finite host checks for the menu10 non-27 data closure and the closed entry
 * capability. It reads the packaged original-evidence rows, drives the real
 * original consumer projection classes and proves that the manager entry
 * allowlist stays untouched. No player file is written; no APK/D8/native run.
 */
public final class StoryMenuEntryHost {
 private static final String WEEK = "menu10-entry-week";
 private static int checks;
 private static File assets;

 private static void check(boolean value, String why) {
  checks++;
  if (!value) throw new AssertionError("FAIL: " + why);
 }

 private static byte[] doc(byte[] profile, String key) {
  byte[] value = BsonLite.documentValue(profile, key);
  return value == null ? BsonLite.EMPTY_DOCUMENT : value;
 }

 private static LocalTutorialStore.Progress progress() {
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

 private static byte[] profile() throws IOException {
  byte[] profile = BsonLite.withAccountIdentity(
      Files.readAllBytes(new File(assets, "new_player.bson").toPath()), "host_menu10_entry", 900782);
  profile = BsonLite.withProfileDocument(profile, "weeknum", BsonLite.document("w", 8, "d", 0, "av", 60));
  profile = BsonLite.withProfileDocument(profile, "std", BsonLite.document("rt", "10-6"));
  profile = BsonLite.withProfileInt(profile, "q7ChapterMenu", 10);
  profile = BsonLite.withProfileDocument(profile, "q7WenziCity",
      BsonLite.document("version", 1, "week", 8, "cycle", WEEK));
  profile = BsonLite.withProfileArray(profile, "q7WeekEventBaseline", Collections.emptyList());
  profile = BsonLite.withProfileDocument(profile, "city", BsonLite.document("av", 60));
  for (int hero : new int[]{135, 136, 137}) profile = BsonLite.withHero(profile, hero);
  return profile;
 }

 private static byte[] request(int scene, int area, int type, List<Integer> heroes) {
  return BsonLite.document("t", type, "s", scene, "d", BsonLite.document("a", area), "h", heroes);
 }

 public static void main(String[] args) throws Exception {
  assets = new File(args[0]);
  Context context = new Context(assets, new AssetManager(assets));
  SelectorPolicy.prepare(context);
  StoryMissionBridge.prepare(context);
  StoryMenuShared.prepare(context);
  check(!StoryMenuEntryData.capability(10) && !StoryMenuEntryData.entryOpen(),
      "entry capability is closed before the closure asset is prepared");
  check(!StoryMenuEntryData.ready(10), "entry readiness is closed before prepare");
  check("menu entry data not prepared".equals(StoryMenuEntryData.closedReason()),
      "unprepared closure reports a closed reason");
  StoryMenuEntryData.prepare(context);
  StoryCityPolicy.prepare(context);
  LocalEventCatalog events = new LocalEventCatalog(new FileInputStream(new File(assets, "event_graph.tsv")));

  // 1. The closure asset is present, original-sourced and scoped to menu10.
  check(StoryMenuEntryData.menu() == 10, "closure asset binds menu10");
  check(StoryMenuEntryData.entryOpen(), "menu10 scoped entry asset is open");
  check(StoryMenuEntryData.capability(10), "entry capability is enabled for menu10");
  check(StoryMenuEntryData.ready(10), "menu10 entry is ready with the selector data");
  check(!StoryMenuEntryData.capability(12), "entry capability stays closed for menu12");
  check(!StoryMenuEntryData.capability(25), "entry capability stays closed for every other menu");
  check(!StoryMenuEntryData.ready(12), "menu12 readiness stays disabled");
  check(StoryCityPolicy.supports(10), "original city owner supports menu10 only");
  check(!StoryCityPolicy.supports(12) && !StoryCityPolicy.supports(25),
      "other newly scoped menus stay closed");
  check(StoryCityPolicy.supports(11), "original allowlisted menu11 behavior is unchanged");
  check(StoryMenuEntryData.closedReason().contains("menu12"), "entry reason keeps menu12 disabled");
  String assetSha = StoryMenuEntryData.assetSha256();
  check(assetSha != null && assetSha.length() == 64 && assetSha.matches("[0-9a-f]+"),
      "closure asset sha256 recorded");
  check("51e49a9d21961570ad1fc0d9bba231d825f2b007b29eee56c475e5f312ed905a"
      .equals(StoryMenuEntryData.missionSha256(320)), "mission320 original row hash");

  // 2. The packaged selector/occurrence rows keep exact original values.
  StoryMenuShared.Effect effect = StoryMenuShared.effect1140();
  check(effect.event == 1140 && effect.release, "1140 occurrence identity and release");
  check(effect.areaFight.equals(Collections.singletonList(6)), "1140 areaFight6");
  check(Integer.valueOf(11).equals(effect.areaSpecialStage.get(6)), "1140 areaSpecialStage6=11");

  LocalTutorialStore.Progress committed = progress();
  byte[] profile = profile();
  StoryMenuShared.Descriptor descriptor = StoryMenuShared.resolveSelector11(profile, committed, 1);
  check(descriptor.area == 6 && descriptor.bucket == 0 && descriptor.selector == 11,
      "selector key (6,0,10-6,11)");
  check(descriptor.groups.equals(Collections.singletonList(Collections.singletonList(320))),
      "selector section [[320]]");
  check(descriptor.missionSha256.equals(StoryMenuEntryData.missionSha256(320)),
      "closure mission hash matches the consumer descriptor");
  check(descriptor.catalogToken.equals(StoryMissionBridge.specialToken()),
      "query/admission share the packaged descriptor token");

  // 3. Committed route state keeps the capability scoped to menu10.
  check(StoryMenuEntryData.capability(10) && StoryMenuEntryData.ready(10),
      "committed 1140 state keeps only menu10 ready");
  check(!LocalStoryEntryPolicy.SUPPORTED.contains(10) && !LocalStoryEntryPolicy.SUPPORTED.contains(12),
      "manager entry allowlist still excludes menu10/menu12");
  check(!LocalStoryEntryPolicy.SUPPORTED.contains(25), "closure class does not edit unrelated entries");
  check(LocalStoryEntryPolicy.supports(10) && !LocalStoryEntryPolicy.supports(12),
      "original entry policy delegates menu10 readiness without opening menu12");

  // 4. Original consumers read the row: query, admission, stage projection.
  check(StoryMenuShared.capability(10, events), "menu10 data capability from original 1129 effect");
  check(!StoryMenuShared.capability(12, events), "menu12 data capability stays disabled");
  check(StoryMissionBridge.area(320) == 6, "mission320 maps to area6");
  check(StoryMissionBridge.status(committed, 6, profile) == 1, "area6 FIGHT1 before the original win");
  check(BsonLite.intValue(StoryMissionBridge.stages(committed, 6, profile), "cs") == 320,
      "original stage query returns selector11 mission320");
  check(BsonLite.intValue(StoryMenuShared.stages(descriptor, Collections.<Integer>emptySet()), "cs") == 320,
      "descriptor stage projection returns 320");
  check(BsonLite.intValue(StoryMenuShared.stages(descriptor, Collections.singletonList(320)), "cs") == 0,
      "descriptor stage projection advances only after a real 320 win");

  List<Integer> team = Arrays.asList(135, 136, 137);
  check(StoryMissionBridge.partyAllowed(request(320, 6, 1, team)), "original admission accepts 1..3 distinct heroes");
  check(StoryMissionBridge.partyAllowed(request(320, 6, 1, Collections.singletonList(135))),
      "original admission accepts the least_hero_num bound");
  check(!StoryMissionBridge.partyAllowed(request(320, 6, 2, team)), "stage type1 only");
  check(!StoryMissionBridge.partyAllowed(request(320, 5, 1, team)), "area6 only");
  check(!StoryMissionBridge.partyAllowed(request(320, 6, 1, Arrays.asList(135, 136, 137, 138))),
      "max_hero_num 3 enforced");
  check(!StoryMissionBridge.partyAllowed(request(320, 6, 1, Arrays.asList(135, 135))),
      "duplicate party rejected");
  check(StoryMenuShared.admit(descriptor, profile, committed, 320, 6, 3), "descriptor admission");
  check(!StoryMenuShared.admit(descriptor, profile, committed, 320, 6, 4), "descriptor max bound");
  check(!StoryMenuShared.admit(descriptor, profile, committed, 321, 6, 3), "descriptor scene binding");

  // 5. Non-special routes keep delegating to the original catalog/consumer.
  check(StoryMissionBridge.area(2119) == 3, "route27 catalog mapping unchanged");
  byte[] route27 = BsonLite.withProfileDocument(profile, "std", BsonLite.document("rt", "27-1"));
  route27 = BsonLite.withProfileInt(route27, "q7ChapterMenu", 25);
  check(!StoryCityPolicy.owns(profile), "COC city policy does not own the menu10 profile");
  check(StoryCityPolicy.owns(route27), "COC city policy still owns its route27 profile");
  check(StoryCityPolicy.knownArea(6), "original city area6 remains readable");

  // 6. No fake win, no successor grant, no menu12 enablement.
  check(!committed.completedEvents.contains(1132), "1132 is not completed by the closure asset");
  check(!committed.completedEvents.contains(3101) && !committed.completedEvents.contains(4101),
      "nextstagenums are not granted");
  check(StoryMenuShared.capability(12) == false, "menu12 capability remains closed");

  System.out.println("PASS " + checks + " menu10 scoped entry readiness and non-27 data closure checks");
 }
}
