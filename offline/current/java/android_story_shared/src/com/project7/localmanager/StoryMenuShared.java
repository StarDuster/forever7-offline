package com.project7.localmanager;

import android.content.Context;
import java.io.*;
import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.util.*;
import org.json.*;

/**
 * Source-only shared mechanism for the two closed routes whose original engines
 * already exist after entry.
 *
 * <p>menu10: the original chapter selector {@code (6,0,"10-6",11)} selects
 * mission 320. The route tag {@code 10-6} is the actual original 1129 handoff;
 * event 1140 is the released occurrence that carries {@code areaFight=[6]} and
 * {@code areaSpecialStage={6:11}}. FIGHT1 to table bucket0 is an explicit
 * offline projection, exactly as in the original selector consumer; bucket0 is
 * not cityFREE.</p>
 *
 * <p>menu12: the q7WenziCity receipt binds the original Wenzi cooperation
 * history (event 1129, city effect {@code areaFree=[3]}) to the current
 * week/cycle for route13 consumers. The existing LocalWenziCityEngine owns the
 * rt10 path; this class only initializes the route13/menu12 gap. It never
 * writes a current-cycle 1129 completion and never writes areaFree.</p>
 *
 * <p>No entry allowlist is changed. {@link #capability(int)} is a state/data
 * scoped capability and defaults to false. Unsupported fields, wrong route,
 * week/cycle mismatch and non-canonical effects reject without publishing.</p>
 */
public final class StoryMenuShared {
 public static final String SCHEMA = "project7-menu-shared-v1";
 public static final int ALAN_MENU = 10, DALVIRA_MENU = 12;
 public static final int SELECTOR_AREA = 6, SELECTOR = 11, SELECTOR_MISSION = 320;
 public static final String SELECTOR_ROUTE = "10-6";
 public static final int SELECTOR_EVENT = 1140;
 public static final String WENZI_KEY = "q7WenziCity";
 public static final int WENZI_EVENT = 1129, WENZI_AREA = 3;
 public static final int DALVIRA_EVENT = 4203, DALVIRA_EVENT_DAY = 3;
 public static final int DALVIRA_HERO_EVENT = 6189, DALVIRA_HERO_DAY = 5;

 private StoryMenuShared() {}

 private static volatile Source source;

 /** Immutable original occurrence/effect row supplied by the event-content owner. */
 public static final class Effect {
  public final int event;
  public final boolean release;
  public final List<Integer> areaFight;
  public final Map<Integer, Integer> areaSpecialStage;
  public Effect(int event, boolean release, List<Integer> areaFight, Map<Integer, Integer> areaSpecialStage) {
   this.event = event;
   this.release = release;
   this.areaFight = areaFight == null ? Collections.<Integer>emptyList() : Collections.unmodifiableList(new ArrayList<>(areaFight));
   this.areaSpecialStage = areaSpecialStage == null ? Collections.<Integer, Integer>emptyMap() : Collections.unmodifiableMap(new TreeMap<>(areaSpecialStage));
  }
 }

 /** Resolved original selector descriptor. No victory, cost or reward is implied. */
 public static final class Descriptor {
  public final int area, bucket, selector;
  public final String route;
  public final List<List<Integer>> groups;
  public final List<Integer> members;
  public final String missionSha256;
  public final String catalogToken;
  private Descriptor(int area, int bucket, String route, int selector, List<List<Integer>> groups,
                     List<Integer> members, String missionSha256, String catalogToken) {
   this.area = area; this.bucket = bucket; this.route = route; this.selector = selector;
   this.groups = Collections.unmodifiableList(groups);
   this.members = Collections.unmodifiableList(members);
   this.missionSha256 = missionSha256; this.catalogToken = catalogToken;
  }
 }

 private static final class Source {
  final int area, selector, mission, event, wenziEvent, wenziArea, dalviraEvent, dalviraHeroEvent;
  final String route;
  final List<List<Integer>> groups;
  final List<Integer> members;
  final String missionSha256;
  final Effect effect;
  final List<Integer> wenziAreaFree, dalviraCineLock;
  final int dalviraDay, dalviraHeroDay;

  Source(JSONObject root) throws IOException {
   try {
    if (!SCHEMA.equals(root.getString("schema"))) throw new IOException("Menu shared schema");
    JSONObject sel = root.getJSONObject("selector");
    JSONArray key = sel.getJSONArray("key");
    if (key.length() != 4 || key.getInt(0) != SELECTOR_AREA || key.getInt(1) != 0 ||
        !SELECTOR_ROUTE.equals(key.getString(2)) || key.getInt(3) != SELECTOR)
     throw new IOException("Menu shared selector key");
    JSONObject row = sel.getJSONObject("row");
    if (row.getInt("chapter") != SELECTOR_AREA || row.getInt("status") != 0 ||
        !SELECTOR_ROUTE.equals(row.getString("route")) || row.getInt("specialStage") != SELECTOR)
     throw new IOException("Menu shared selector row");
    JSONObject section = row.getJSONObject("section");
    if (section.length() != 10) throw new IOException("Menu shared selector section count");
    groups = new ArrayList<>(); members = new ArrayList<>();
    for (int i = 0; i < 10; i++) {
     JSONArray values = section.getJSONArray(Integer.toString(i));
     List<Integer> group = ints(values, true);
     if (!group.isEmpty()) groups.add(group);
     members.addAll(group);
    }
    if (members.size() != 1 || members.get(0) != SELECTOR_MISSION || groups.size() != 1 ||
        groups.get(0).size() != 1 || groups.get(0).get(0) != SELECTOR_MISSION)
     throw new IOException("Menu shared selector membership");

    JSONObject missions = root.getJSONObject("missions");
    if (missions.length() != 1) throw new IOException("Menu shared mission scope");
    JSONObject missionRow = missions.getJSONObject(Integer.toString(SELECTOR_MISSION));
    if (missionRow.getInt("id") != SELECTOR_MISSION || missionRow.getInt("ch") != SELECTOR_AREA ||
        missionRow.getInt("system_type") != 1 || missionRow.getInt("release") != 1 ||
        missionRow.getInt("va") != 2 || missionRow.getInt("inherit_mission") != 5105 ||
        missionRow.getInt("fatigue") != 5 || missionRow.getInt("least_hero_num") < 1 ||
        missionRow.getInt("max_hero_num") < missionRow.getInt("least_hero_num"))
     throw new IOException("Menu shared mission fields");
    if (!ints(missionRow.getJSONArray("successEvent"), false).equals(Collections.singletonList(1132)) ||
        !ints(missionRow.getJSONArray("nextstagenums"), false).equals(Arrays.asList(3101, 4101)))
     throw new IOException("Menu shared mission successors");
    JSONObject hashes = root.getJSONObject("mission_sha256");
    missionSha256 = hashes.getString(Integer.toString(SELECTOR_MISSION));
    if (missionSha256.length() != 64 || !missionSha256.matches("[0-9a-f]+"))
     throw new IOException("Menu shared mission hash");

    JSONObject ev = root.getJSONObject("event1140");
    if (ev.getInt("id") != SELECTOR_EVENT || !ev.getBoolean("release") ||
        !ints(ev.getJSONArray("areaFight"), false).equals(Collections.singletonList(SELECTOR_AREA)))
     throw new IOException("Menu shared selector occurrence");
    JSONObject special = ev.getJSONObject("areaSpecialStage");
    if (special.length() != 1 || special.getInt(Integer.toString(SELECTOR_AREA)) != SELECTOR)
     throw new IOException("Menu shared selector effect");
    Map<Integer, Integer> specialMap = new TreeMap<>();
    specialMap.put(SELECTOR_AREA, SELECTOR);
    effect = new Effect(SELECTOR_EVENT, true, Collections.singletonList(SELECTOR_AREA), specialMap);

    JSONObject wenzi = root.getJSONObject("wenzi");
    wenziEvent = wenzi.getInt("event"); wenziArea = wenzi.getInt("area");
    wenziAreaFree = ints(wenzi.getJSONArray("areaFree"), false);
    if (wenziEvent != WENZI_EVENT || wenziArea != WENZI_AREA ||
        !wenziAreaFree.equals(Collections.singletonList(WENZI_AREA)))
     throw new IOException("Menu shared Wenzi gate");

    JSONObject dalvira = root.getJSONObject("dalvira");
    if (dalvira.getInt("menu") != DALVIRA_MENU || dalvira.getInt("event") != DALVIRA_EVENT ||
        dalvira.getInt("eventDay") != DALVIRA_EVENT_DAY ||
        dalvira.getInt("heroEvent") != DALVIRA_HERO_EVENT ||
        dalvira.getInt("heroDay") != DALVIRA_HERO_DAY)
     throw new IOException("Menu shared Dalvira gate");
    dalviraCineLock = ints(dalvira.getJSONArray("cineLockHeroes"), false);
    if (!dalviraCineLock.equals(Collections.singletonList(36))) throw new IOException("Menu shared Dalvira heroes");
    dalviraEvent = DALVIRA_EVENT; dalviraHeroEvent = DALVIRA_HERO_EVENT;
    dalviraDay = DALVIRA_EVENT_DAY; dalviraHeroDay = DALVIRA_HERO_DAY;
    area = SELECTOR_AREA; selector = SELECTOR; mission = SELECTOR_MISSION;
    event = SELECTOR_EVENT; route = SELECTOR_ROUTE;
   } catch (JSONException e) {
    throw new IOException("Menu shared fixed catalog", e);
   }
  }
 }

 private static List<Integer> ints(JSONArray a, boolean allowEmpty) throws JSONException {
  List<Integer> out = new ArrayList<>();
  for (int i = 0; i < a.length(); i++) {
   Object v = a.get(i);
   if (!(v instanceof Integer)) throw new JSONException("Menu shared integer");
   out.add((Integer) v);
  }
  if (!allowEmpty && out.isEmpty()) throw new JSONException("Menu shared empty array");
  return Collections.unmodifiableList(out);
 }

 /** Load the evidence-scoped source once. Never infers missing rows. */
 public static void prepare(File directory) throws IOException {
  if (directory == null) throw new IOException("Menu shared directory");
  install(read(new File(directory, "special-selector-v1.json")));
 }

 /** Bootstrap path: the fixed asset must be packaged and valid. */
 public static void prepare(Context context) throws IOException {
  if (context == null) throw new IOException("Menu shared context");
  byte[] data;
  try (InputStream in = context.getAssets().open("project7_story_shared/special-selector-v1.json")) {
   data = read(in);
  }
  StoryMissionBridge.prepareSpecial(context);
  install(data);
 }

 private static void install(byte[] data) throws IOException {
  try {
   Source candidate = new Source(new JSONObject(new String(data, StandardCharsets.UTF_8)));
   synchronized (StoryMenuShared.class) { source = candidate; }
  } catch (JSONException e) {
   throw new IOException("Menu shared JSON", e);
  }
 }

 private static byte[] read(File file) throws IOException {
  if (!file.isFile()) throw new IOException("Menu shared catalog missing");
  try (InputStream in = new FileInputStream(file)) { return read(in); }
 }

 private static byte[] read(InputStream in) throws IOException {
  ByteArrayOutputStream out = new ByteArrayOutputStream();
  byte[] buf = new byte[8192];
  for (int n; (n = in.read(buf)) != -1; ) {
   if (out.size() > 1000000 - n) throw new IOException("Menu shared catalog bound");
   out.write(buf, 0, n);
  }
  return out.toByteArray();
 }

 /** Data-only capability; false before prepare and false for every other menu. */
 public static boolean capability(int menu) {
  Source s = source;
  if (s == null) return false;
  if (menu == ALAN_MENU) return s.selector == SELECTOR && SELECTOR_ROUTE.equals(s.route);
  // menu12 stays disabled until prior-cycle/current-cycle semantics are frozen.
  return false;
 }

 /** Capability also bound to the current original event catalog owner. */
 public static boolean capability(int menu, LocalEventCatalog events) {
  Source s = source;
  if (s == null || events == null) return false;
  if (menu == ALAN_MENU) return s.selector == SELECTOR && hasAreaFree(events, s.wenziEvent, s.wenziAreaFree);
  if (menu == DALVIRA_MENU) return false; // Astra owns the current-cycle semantics.
  return false;
 }

 /**
  * City-owner input after the original 1140 completion commit. Returns the
  * exact released areaFight + areaSpecialStage row; never writes city state.
  */
 public static byte[] cityEffect1140(byte[] profile, LocalTutorialStore.Progress progress) {
  Source s = require();
  if (profile == null || progress == null || !current(profile, progress, s.event))
   throw new IllegalStateException("1140 completion is not committed");
  return BsonLite.document("areaFight", s.effect.areaFight,
      "areaSpecialStage", BsonLite.document(Integer.toString(s.area), s.selector));
 }

 /** The original 1140 occurrence row, for callers that already own event content. */
 public static Effect effect1140() {
  Source s = source;
  if (s == null) throw new IllegalStateException("Menu shared source not prepared");
  return s.effect;
 }

 /**
  * Resolve only the exact original selector key. {@code areaStatus} is the
  * original city status (1=FIGHT1 -> table bucket0, 5 -> bucket5). Empty
  * buckets have no row and reject.
  */
 public static Descriptor resolveSelector11(byte[] profile, LocalTutorialStore.Progress progress,
                                            int areaStatus, Effect effect) {
  Source s = require();
  if (profile == null || progress == null || effect == null) throw new IllegalArgumentException("Menu shared input");
  if (areaStatus != 1 && areaStatus != 5) throw new IllegalArgumentException("Original selector requires FIGHT1/FIGHT5");
  int bucket = areaStatus == 1 ? 0 : 5;
  if (bucket != 0) throw new IllegalStateException("Missing exact original chapter selector");
  if (!SELECTOR_ROUTE.equals(route(profile))) throw new IllegalStateException("Selector requires the original 10-6 route handoff");
  if (menu(profile) != ALAN_MENU) throw new IllegalStateException("Selector belongs to menu10");
  if (effect.event != s.event || !effect.release || !effect.areaFight.contains(s.area) ||
      !Integer.valueOf(s.selector).equals(effect.areaSpecialStage.get(s.area)))
   throw new IllegalArgumentException("Released 1140 areaSpecialStage is required");
  if (!current(profile, progress, s.wenziEvent)) throw new IllegalStateException("Selector requires actual 1129 route source");
  if (!current(profile, progress, effect.event)) throw new IllegalStateException("Selector requires actual 1140 occurrence");
  return new Descriptor(s.area, bucket, s.route, s.selector, s.groups, s.members, s.missionSha256, token(s));
 }

 /** Production call using the loaded original 1140 row. */
 public static Descriptor resolveSelector11(byte[] profile, LocalTutorialStore.Progress progress, int areaStatus) {
  return resolveSelector11(profile, progress, areaStatus, effect1140());
 }

 /** Canonical get_area_stages reply payload for the original section order. */
 public static byte[] stages(Descriptor descriptor, Collection<Integer> wins) {
  if (descriptor == null) throw new IllegalArgumentException("Selector descriptor");
  Set<Integer> done = wins == null ? Collections.<Integer>emptySet() : new HashSet<>(wins);
  int current = 0;
  for (int scene : descriptor.members) if (!done.contains(scene)) { current = scene; break; }
  return BsonLite.document("cs", current, "sl", descriptor.groups);
 }

 /** Admission guard only; no victory, cost, reward or areaFree is produced. */
 public static boolean admit(Descriptor descriptor, byte[] profile, LocalTutorialStore.Progress progress,
                             int scene, int area, int teamSize) {
  Source s = require();
  if (descriptor == null || profile == null || progress == null) return false;
  if (scene != s.mission || area != s.area || teamSize < 1 || teamSize > 3) return false;
  if (!s.route.equals(route(profile)) || menu(profile) != ALAN_MENU) return false;
  if (!current(profile, progress, s.wenziEvent) || !current(profile, progress, s.event)) return false;
  return descriptor.members.equals(s.members) && descriptor.catalogToken.equals(token(s));
 }

 /**
  * menu12 route13 q7WenziCity initialization. The original rt10 owner remains
  * LocalWenziCityEngine.refresh; this method returns false outside menu12/route13.
  *
  * <p>The proof is either the current-cycle Wenzi cooperation (1129 day0,
  * completion1, not in q7WeekEventBaseline) or the P7 canonical prior-cycle
  * history (q7WeekEventBaseline contains 1129). In both cases the loaded
  * original 1129 city effect must be exactly areaFree=[3]. No completion or
  * area state is fabricated.</p>
  */
 public static boolean initializeWenziCity(LocalResourceEngine.Result result, LocalEventCatalog events,
                                           LocalTutorialStore.Progress progress) {
  Source s = require();
  if (result == null || events == null || progress == null) throw new IllegalArgumentException("Menu shared Wenzi input");
  byte[] profile = result.profile;
  if (profile == null || menu(profile) != DALVIRA_MENU) return false;
  String rt = route(profile);
  if (rt == null || !(rt.equals("13") || rt.startsWith("13-"))) return false;
  byte[] effect = events.cityEffects.get(s.wenziEvent);
  if (effect == null) throw new IllegalStateException("Wenzi event effect missing");
  if (!keys(effect).equals(Collections.singletonList("areaFree")))
   throw new IllegalArgumentException("Wenzi effect shape changed");
  if (!array(effect, "areaFree").equals(s.wenziAreaFree))
   throw new IllegalArgumentException("Wenzi effect is not areaFree=[3]");
  if (!current(profile, progress, s.wenziEvent)) return false;

  byte[] existing = doc(profile, WENZI_KEY);
  if (!BsonLite.keys(existing).isEmpty()) {
   Integer version = BsonLite.intValue(existing, "version");
   Integer week = BsonLite.intValue(existing, "week");
   String cycle = BsonLite.stringValue(existing, "cycle");
   if (version == null || version != 1 || week == null || week != progress.weekIndex ||
       !Objects.equals(cycle, progress.weekCommit))
    throw new IllegalArgumentException("城市周期数据不一致，请重新进入");
   return false;
  }
  byte[] candidate = BsonLite.withProfileDocument(profile, WENZI_KEY,
      BsonLite.document("version", 1, "week", progress.weekIndex, "cycle", progress.weekCommit));
  byte[] projected = BsonLite.withLocalCityState(candidate, progress);
  if (Arrays.equals(projected, profile)) return false;
  byte[] reply = BsonLite.allAreaInfoReplyDocument(true, progress, projected);
  result.profile = projected;
  result.add("get_all_area_info_reply", reply);
  return true;
 }

 /** Guard used by the route13 consumer host; no state is written here. */
 public static boolean dalviraGate(byte[] profile, LocalTutorialStore.Progress progress, LocalEventCatalog events) {
  Source s = require();
  if (profile == null || progress == null || events == null) return false;
  if (menu(profile) != DALVIRA_MENU) return false;
  String rt = route(profile);
  if (rt == null || !(rt.equals("13") || rt.startsWith("13-"))) return false;
  byte[] wenzi = doc(profile, WENZI_KEY);
  if (BsonLite.keys(wenzi).isEmpty()) return false;
  Integer version = BsonLite.intValue(wenzi, "version");
  if (version == null || version != 1 || !Objects.equals(progress.weekCommit, BsonLite.stringValue(wenzi, "cycle")))
   return false;
  Integer week = BsonLite.intValue(wenzi, "week");
  if (week == null || week != progress.weekIndex) return false;
  if (!current(profile, progress, s.wenziEvent)) return false;
  if (completedDay(profile, progress, s.dalviraEvent) != s.dalviraDay) return false;
  if (!completedOnce(profile, progress, s.dalviraEvent)) return false;
  if (baseline(profile).contains(s.dalviraEvent)) return false;
  if (baseline(profile).contains(s.dalviraHeroEvent)) return false;
  byte[] effect = events.cityEffects.get(s.dalviraHeroEvent);
  return effect != null && cinematic(effect).equals(s.dalviraCineLock) &&
      completedDay(profile, progress, s.dalviraHeroEvent) == s.dalviraHeroDay &&
      completedOnce(profile, progress, s.dalviraHeroEvent);
 }

 private static Source require() {
  Source s = source;
  if (s == null) throw new IllegalStateException("Menu shared source not prepared");
  return s;
 }

 private static String token(Source s) {
  String canonical = s.area + "|" + 0 + "|" + s.route + "|" + s.selector + "|" + s.groups + "|" +
      s.members + "|" + s.missionSha256;
  return sha256(canonical);
 }

 private static String sha256(String value) {
  try {
   byte[] d = MessageDigest.getInstance("SHA-256").digest(value.getBytes(StandardCharsets.UTF_8));
   StringBuilder b = new StringBuilder();
   for (byte v : d) b.append(String.format(Locale.ROOT, "%02x", v & 255));
   return b.toString();
  } catch (Exception e) {
   throw new IllegalStateException("SHA-256", e);
  }
 }

 private static byte[] doc(byte[] profile, String key) {
  byte[] d = BsonLite.documentValue(profile, key);
  return d == null ? BsonLite.EMPTY_DOCUMENT : d;
 }

 private static String route(byte[] profile) {
  return profile == null ? null : BsonLite.stringValue(doc(profile, "std"), "rt");
 }

 private static int menu(byte[] profile) {
  Integer v = profile == null ? null : BsonLite.intValue(profile, "q7ChapterMenu");
  return v == null ? -1 : v;
 }

 private static List<Integer> baseline(byte[] profile) {
  List<Integer> v = BsonLite.intArrayValues(profile, "q7WeekEventBaseline");
  return v == null ? Collections.<Integer>emptyList() : v;
 }

 private static boolean current(byte[] profile, LocalTutorialStore.Progress progress, int event) {
  if (baseline(profile).contains(event)) return false;
  if (!completedOnce(profile, progress, event)) return false;
  return completedDay(profile, progress, event) == 0;
 }

 private static boolean completedOnce(byte[] profile, LocalTutorialStore.Progress progress, int event) {
  Integer n = progress.eventCompletions.get(event);
  return progress.completedEvents.contains(event) && n != null && n == 1;
 }

 private static int completedDay(byte[] profile, LocalTutorialStore.Progress progress, int event) {
  return LocalStoryItemRewardEngine.completedDay(profile, progress, event);
 }

 private static List<String> keys(byte[] value) {
  return BsonLite.keys(value);
 }

 private static List<Integer> array(byte[] value, String key) {
  List<Integer> v = BsonLite.intArrayValues(value, key);
  return v == null ? Collections.<Integer>emptyList() : v;
 }

 private static List<Integer> cinematic(byte[] value) {
  return array(value, "cineLockHeroes");
 }

 private static boolean hasAreaFree(LocalEventCatalog events, int event, List<Integer> expected) {
  byte[] effect = events.cityEffects.get(event);
  if (effect == null || !keys(effect).equals(Collections.singletonList("areaFree"))) return false;
  return array(effect, "areaFree").equals(expected);
 }
}
