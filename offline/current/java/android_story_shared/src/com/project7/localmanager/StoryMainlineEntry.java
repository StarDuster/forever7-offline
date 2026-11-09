package com.project7.localmanager;

import android.content.Context;
import java.io.*;
import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.util.*;

/**
 * Data-scoped entry and city-effect capability for proven mainline menus.
 *
 * <p>Only menus listed in the packaged {@code proven} set are exposed. The
 * original {@link LocalStoryEntryPolicy#SUPPORTED} allowlist is never edited;
 * the original {@link LocalWeekEngine} still owns entrance, ending
 * requirements, week reset and the requestEnterStory commit. This class only
 * answers whether the shared mechanism closure (chapter route, first stage,
 * city-effect shape and original week row) is proven for a menu.</p>
 *
 * <p>It contains no per-event writes and no inferred route. Default/unknown
 * menus stay false, and menu10/menu12 ownership is untouched.</p>
 */
public final class StoryMainlineEntry {
 public static final String SCHEMA = "project7-mainline32-entry-v1";
 private static final String ASSET = "project7_story_shared/mainline32-entry-v1.json";
 private static final String HASH = "3fac026a76a947f5bca4d60a7d70d619510f145fa253b9ee3429f3082ce5bd86";
 private static final String[] EFFECT_FIELDS = {"areaFree", "areaFight", "areaLock", "areaUnlock"};
 private static volatile Map<Integer, Row> rows;
 private static volatile Set<Integer> proven;

 private StoryMainlineEntry() {}

 private static final class Row {
  final int id, init, firstScene, firstArea, chapterKeys, scenes;
  final String route, family;
  final boolean effectsSupported, defaultChapter, cityReducer;
  final List<List<Integer>> requires;

  Row(int id, int init, String route, String family, int firstScene, int firstArea,
      int chapterKeys, int scenes, boolean effectsSupported, boolean defaultChapter,
      boolean cityReducer, List<List<Integer>> requires) {
   this.id = id; this.init = init; this.route = route; this.family = family;
   this.firstScene = firstScene; this.firstArea = firstArea;
   this.chapterKeys = chapterKeys; this.scenes = scenes;
   this.effectsSupported = effectsSupported; this.defaultChapter = defaultChapter;
   this.cityReducer = cityReducer;
   this.requires = requires;
  }
 }

 /** Bootstrap asset path. */
 public static void prepare(Context context) throws IOException {
  if (context == null) throw new IOException("Mainline entry context");
  try (InputStream in = context.getAssets().open(ASSET)) { install(read(in)); }
 }

 /** Evidence/host path for callers that receive the asset directory directly. */
 public static void prepare(File directory) throws IOException {
  if (directory == null) throw new IOException("Mainline entry directory");
  File file = new File(directory, ASSET);
  if (!file.isFile()) throw new IOException("Mainline entry asset missing");
  try (InputStream in = new FileInputStream(file)) { install(read(in)); }
 }

 private static void install(byte[] data) throws IOException {
  if (data.length == 0 || data.length > 1000000) throw new IOException("Mainline entry asset bound");
  try {
   if (!HASH.equals(hex(MessageDigest.getInstance("SHA-256").digest(data))))
    throw new IOException("Mainline entry asset hash");
  } catch (java.security.NoSuchAlgorithmException error) {
   throw new IOException("Mainline entry hash", error);
  }
  try {
   org.json.JSONObject root = new org.json.JSONObject(new String(data, StandardCharsets.UTF_8));
   if (!SCHEMA.equals(root.getString("schema"))) throw new IOException("Mainline entry schema");
   org.json.JSONArray list = root.getJSONArray("menus");
   Map<Integer, Row> next = new LinkedHashMap<>();
   for (int i = 0; i < list.length(); i++) {
    org.json.JSONObject value = list.getJSONObject(i);
    int id = value.getInt("id");
    if (id < 1 || id > 32 || next.containsKey(id))
     throw new IOException("Mainline entry menu id");
    String route = value.getString("route");
    String family = value.getString("family");
    if (route.isEmpty() || family.isEmpty() || !route.matches("[0-9]+(?:-[0-9]+)*") ||
        !family.matches("[0-9]+")) throw new IOException("Mainline entry route");
    boolean defaultChapter = value.optBoolean("default_chapter", false);
    int init = value.getInt("init"), firstScene = value.getInt("first_scene");
    int firstArea = value.getInt("first_area"), chapterKeys = value.getInt("chapter_keys");
    int scenes = value.getInt("scenes");
    if (init <= 0 || firstScene <= 0 || firstArea < 1 || firstArea > 8 || scenes <= 0 ||
        (defaultChapter ? chapterKeys != 0 : chapterKeys <= 0))
     throw new IOException("Mainline entry stage fields");
    org.json.JSONArray requirements = value.getJSONArray("requires");
    List<List<Integer>> requires = new ArrayList<>();
    for (int j = 0; j < requirements.length(); j++) {
     org.json.JSONArray group = requirements.getJSONArray(j);
     if (group.length() == 0) throw new IOException("Mainline entry requirement");
     List<Integer> ids = new ArrayList<>();
     for (int k = 0; k < group.length(); k++) {
      int ending = group.getInt(k);
      if (ending <= 0 || ids.contains(ending)) throw new IOException("Mainline entry ending");
      ids.add(ending);
     }
     requires.add(Collections.unmodifiableList(ids));
    }
    boolean effects = value.getBoolean("effects_supported");
    boolean cityReducer = value.optBoolean("city_reducer", true);
    org.json.JSONObject effectsRow = value.optJSONObject("effects");
    if (effects) {
     if (effectsRow == null || effectsRow.length() == 0)
      throw new IOException("Mainline entry effect shape");
     for (Iterator<String> keys = effectsRow.keys(); keys.hasNext(); ) {
      String field = keys.next();
      if (!Arrays.asList(EFFECT_FIELDS).contains(field))
       throw new IOException("Mainline entry effect field");
      org.json.JSONArray areas = effectsRow.getJSONArray(field);
      Set<Integer> seen = new HashSet<>();
      for (int j = 0; j < areas.length(); j++) {
       int area = areas.getInt(j);
       // Fixed original city ids: normal areas 1..8, auxiliary 9, virtual 10000..10003.
       boolean known = (area >= 1 && area <= 9) ||
           (area >= 10000 && area <= 10003);
       if (!known || !seen.add(area))
        throw new IOException("Mainline entry effect area");
      }
     }
    }
    next.put(id, new Row(id, init, route, family, firstScene, firstArea,
        chapterKeys, scenes, effects, defaultChapter, cityReducer, requires));
   }
   org.json.JSONArray enable = root.getJSONArray("proven");
   Set<Integer> allowed = new LinkedHashSet<>();
   for (int i = 0; i < enable.length(); i++) {
    int menu = enable.getInt(i);
    if (!next.containsKey(menu) || !next.get(menu).effectsSupported || !allowed.add(menu))
     throw new IOException("Mainline entry proven scope");
   }
   if (allowed.isEmpty()) throw new IOException("Mainline entry proven set");
   rows = Collections.unmodifiableMap(next);
   proven = Collections.unmodifiableSet(allowed);
  } catch (IOException error) {
   throw error;
  } catch (Exception error) {
   throw new IOException("Mainline entry fixed catalog", error);
  }
 }

 private static byte[] read(InputStream in) throws IOException {
  ByteArrayOutputStream out = new ByteArrayOutputStream();
  byte[] buffer = new byte[8192];
  for (int n; (n = in.read(buffer)) != -1; ) {
   if (out.size() > 1000000 - n) throw new IOException("Mainline entry bound");
   out.write(buffer, 0, n);
  }
  return out.toByteArray();
 }

 private static String hex(byte[] bytes) {
  StringBuilder out = new StringBuilder();
  for (byte value : bytes) out.append(String.format(Locale.ROOT, "%02x", value & 255));
  return out.toString();
 }

 private static Row row(int menu) {
  Map<Integer, Row> current = rows;
  if (current == null || proven == null || !proven.contains(menu)) return null;
  return current.get(menu);
 }

 /** True only for the packaged proven set; false before prepare and for all others. */
 public static boolean capability(int menu) {
  return row(menu) != null;
 }

 /** Proven entry closure plus the original Week entrance and canEnter ending gate. */
 public static boolean entryReady(int menu, byte[] profile, LocalTutorialStore.Progress progress,
                                  LocalWeekCatalog weeks) {
  Row value = row(menu);
  if (value == null || profile == null || progress == null || weeks == null) return false;
  if (progress.weekCommit == null || progress.weekCommit.isEmpty()) return false;
  if (!weeks.entrances.containsKey(menu) || weeks.entrances.get(menu) != value.init) return false;
  if (!value.defaultChapter && !StoryMissionBridge.chapterReady(value.firstArea, value.route))
   return false;
  if (StoryMissionBridge.area(value.firstScene) != value.firstArea) return false;
  try {
   return LocalWeekEngine.canEnter(profile, weeks, menu);
  } catch (RuntimeException invalid) {
   return false;
  }
 }

 /** City-effect reducer ownership for a proven menu; legacy route10/12 stays original. */
 public static boolean cityOwns(byte[] profile) {
  if (profile == null) return false;
  if (BsonLite.documentValue(profile, "q7WeekTransition") == null) return false;
  Integer menu = BsonLite.intValue(profile, "q7ChapterMenu");
  if (menu == null) return false;
  String rt = BsonLite.stringValue(BsonLite.documentValue(profile, "std"), "rt");
  if (rt != null && (rt.equals("12") || rt.startsWith("12-"))) return false;
  Row value = row(menu);
  return value != null && value.effectsSupported && value.cityReducer;
 }

 /** True only for a packaged default-chapter row (no chapter_mission_data family row). */
 public static boolean defaultChapter(int menu) {
  Row value = row(menu);
  return value != null && value.defaultChapter;
 }

 public static String route(int menu) {
  Row value = row(menu);
  return value == null ? null : value.route;
 }

 public static int firstScene(int menu) {
  Row value = row(menu);
  return value == null ? 0 : value.firstScene;
 }

 public static int initEvent(int menu) {
  Row value = row(menu);
  return value == null ? 0 : value.init;
 }

 public static int chapterKeys(int menu) {
  Row value = row(menu);
  return value == null ? 0 : value.chapterKeys;
 }

 public static int scenes(int menu) {
  Row value = row(menu);
  return value == null ? 0 : value.scenes;
 }

 public static List<List<Integer>> requires(int menu) {
  Row value = row(menu);
  return value == null ? Collections.<List<Integer>>emptyList() : value.requires;
 }

 public static boolean prepared() {
  return rows != null && proven != null;
 }
}
