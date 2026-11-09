package com.project7.localmanager;

import android.content.Context;
import java.io.*;
import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.util.*;
import org.json.*;

/**
 * menu10 non-27 data-closure contract. It packages only original chapter,
 * mission, event, city and stage facts; it never authors plot, win state or
 * entry permission.
 *
 * <p>Entry is scoped to menu10 by construction. {@link #capability(int)} is
 * false before prepare, true only after the validated menu10 closure asset is
 * loaded and false for every other menu. {@link #ready(int)} additionally
 * requires the original selector data. {@link #entryOpen()} never edits the
 * original {@code LocalStoryEntryPolicy.SUPPORTED} allowlist; the original
 * Week consumer still owns route requirements, entry event 477, endings
 * 28/29/30 and week/cycle state.</p>
 */
public final class StoryMenuEntryData {
 public static final String SCHEMA = "project7-menu10-entry-v1";
 public static final int MENU = 10, AREA = 6, SELECTOR = 11, MISSION = 320;
 public static final String ROUTE = "10-6";
 public static final String ECONOMY_320 = "M\t320\t2\t5\t25\t5\t1\t3\t1";
 private static volatile Row row;

 private StoryMenuEntryData() {}

 private static final class Row {
  final int menu, va, fatigue, overFatigue, recommend;
  final boolean open;
  final String reason, missionSha, assetSha;

  Row(int menu, int va, int fatigue, int overFatigue, int recommend,
      boolean open, String reason, String missionSha, String assetSha) {
   this.menu = menu; this.va = va; this.fatigue = fatigue; this.overFatigue = overFatigue;
   this.recommend = recommend; this.open = open; this.reason = reason;
   this.missionSha = missionSha; this.assetSha = assetSha;
  }
 }

 /** Bootstrap path: the fixed closure asset must be packaged and valid. */
 public static void prepare(Context context) throws IOException {
  if (context == null) throw new IOException("Menu entry context");
  byte[] data;
  try (InputStream in = context.getAssets().open("project7_story_shared/menu10-entry-v1.json")) {
   data = read(in);
  }
  install(data);
 }

 /** Evidence path for hosts that receive the asset directory directly. */
 public static void prepare(File directory) throws IOException {
  if (directory == null) throw new IOException("Menu entry directory");
  File file = new File(directory, "menu10-entry-v1.json");
  if (!file.isFile()) throw new IOException("Menu entry asset missing");
  try (InputStream in = new FileInputStream(file)) { install(read(in)); }
 }

 private static void install(byte[] data) throws IOException {
  if (data.length == 0 || data.length > 1000000) throw new IOException("Menu entry asset bound");
  try {
   JSONObject root = new JSONObject(new String(data, StandardCharsets.UTF_8));
   if (!SCHEMA.equals(root.getString("schema"))) throw new IOException("Menu entry schema");
   int menu = root.getInt("menu");
   JSONObject entry = root.getJSONObject("entry");
   boolean open = entry.getBoolean("open");
   if (menu != MENU) throw new IOException("Menu entry scope");
   if (entry.getString("allowlist").trim().isEmpty()) throw new IOException("Menu entry allowlist name");
   if (entry.getString("reason").trim().isEmpty() ||
       entry.getJSONArray("preconditions").length() == 0)
    throw new IOException("Menu entry closure reason");

   JSONObject rows = root.getJSONObject("rows");
   JSONObject selector = rows.getJSONObject("chapter_selector");
   JSONArray key = selector.getJSONArray("key");
   if (key.length() != 4 || key.getInt(0) != AREA || key.getInt(1) != 0 ||
       !ROUTE.equals(key.getString(2)) || key.getInt(3) != SELECTOR)
    throw new IOException("Menu entry selector key");
   JSONObject selectorRow = selector.getJSONObject("row");
   if (selectorRow.getInt("chapter") != AREA || selectorRow.getInt("status") != 0 ||
       !ROUTE.equals(selectorRow.getString("route")) || selectorRow.getInt("specialStage") != SELECTOR)
    throw new IOException("Menu entry selector row");
   JSONObject section = selectorRow.getJSONObject("section");
   if (section.length() != 10) throw new IOException("Menu entry selector sections");
   List<List<Integer>> groups = new ArrayList<>();
   List<Integer> members = new ArrayList<>();
   for (int i = 0; i < 10; i++) {
    List<Integer> group = ints(section.getJSONArray(Integer.toString(i)));
    if (group.size() > 1) throw new IOException("Menu entry selector group");
    if (!group.isEmpty()) groups.add(group);
    members.addAll(group);
   }
   if (!members.equals(Collections.singletonList(MISSION)) ||
       !groups.equals(Collections.singletonList(Collections.singletonList(MISSION))) ||
       !arrays(selector.getJSONArray("sections_nonempty"))
           .equals(Collections.singletonList(Collections.singletonList(MISSION))))
    throw new IOException("Menu entry selector membership");

   JSONObject missions = rows.getJSONObject("missions");
   if (missions.length() != 1) throw new IOException("Menu entry mission scope");
   JSONObject mission = missions.getJSONObject(Integer.toString(MISSION));
   if (mission.getInt("id") != MISSION || mission.getInt("ch") != AREA ||
       mission.getInt("system_type") != 1 || mission.getInt("release") != 1 ||
       mission.getInt("va") != 2 || mission.getInt("fatigue") != 5 ||
       mission.getInt("overFatigue") != 25 || mission.getInt("force_recommend") != 5 ||
       mission.getInt("inherit_mission") != 5105 ||
       mission.getInt("least_hero_num") != 1 || mission.getInt("max_hero_num") != 3)
    throw new IOException("Menu entry mission fields");
   if (!ints(mission.getJSONArray("successEvent")).equals(Collections.singletonList(1132)) ||
       !ints(mission.getJSONArray("nextstagenums")).equals(Arrays.asList(3101, 4101)))
    throw new IOException("Menu entry mission successors");
   JSONObject hashes = rows.getJSONObject("mission_sha256");
   String missionSha = hashes.getString(Integer.toString(MISSION));
   if (missionSha.length() != 64 || !missionSha.matches("[0-9a-f]+"))
    throw new IOException("Menu entry mission hash");

   JSONObject events = rows.getJSONObject("events");
   if (!new TreeSet<>(keys(events)).equals(new TreeSet<>(Arrays.asList("1129", "1132", "1140", "1141"))))
    throw new IOException("Menu entry event scope");
   JSONObject route = events.getJSONObject("1129");
   if (!route.getBoolean("release") || !ROUTE.equals(route.getString("enterStoryRoute")) ||
       !ints(route.getJSONObject("completeConds").getJSONArray("dialog")).equals(Collections.singletonList(1129)) ||
       !ints(route.getJSONArray("areaFree")).equals(Collections.singletonList(3)))
    throw new IOException("Menu entry 1129 route source");
   JSONObject success = events.getJSONObject("1132");
   if (!success.getBoolean("release") ||
       !ints(success.getJSONArray("areaFree")).equals(Collections.singletonList(AREA)) ||
       !ints(success.getJSONArray("events")).equals(Collections.singletonList(1133)) ||
       !ints(success.getJSONObject("completeConds").getJSONArray("dialog")).equals(Collections.singletonList(1132)))
    throw new IOException("Menu entry 1132 success consumer");
   JSONObject occurrence = events.getJSONObject("1140");
   if (!occurrence.getBoolean("release") ||
       !ints(occurrence.getJSONArray("areaFight")).equals(Collections.singletonList(AREA)) ||
       occurrence.getJSONObject("areaSpecialStage").length() != 1 ||
       occurrence.getJSONObject("areaSpecialStage").getInt(Integer.toString(AREA)) != SELECTOR)
    throw new IOException("Menu entry 1140 occurrence");
   JSONObject terminal = events.getJSONObject("1141");
   if (!terminal.getBoolean("release") || terminal.has("areaFight") || terminal.has("areaFree") ||
       terminal.has("areaSpecialStage"))
    throw new IOException("Menu entry 1141 terminal gate");

   JSONObject economy = rows.getJSONObject("economy");
   if (!ECONOMY_320.equals(economy.getString("tsv"))) throw new IOException("Menu entry economy row");
   JSONObject stage = rows.getJSONObject("stage");
   if (stage.getInt("area") != AREA || !ROUTE.equals(stage.getString("route")) ||
       stage.getInt("selector") != SELECTOR || stage.getInt("mission") != MISSION)
    throw new IOException("Menu entry stage binding");
   JSONObject area = rows.getJSONObject("city_area").getJSONObject("6");
   if (area.getInt("id") != AREA) throw new IOException("Menu entry city area");

   JSONObject gaps = root.getJSONObject("gaps");
   for (String gap : new String[]{"post_commit_hook", "next_stages", "manager_catalog", "entry"})
    if (gaps.getString(gap).trim().isEmpty()) throw new IOException("Menu entry gap");
   if (root.getJSONObject("consumers").length() == 0) throw new IOException("Menu entry consumers");

   Row candidate = new Row(menu, mission.getInt("va"), mission.getInt("fatigue"),
       mission.getInt("overFatigue"), mission.getInt("force_recommend"), open,
       entry.getString("reason"), missionSha, hex(MessageDigest.getInstance("SHA-256").digest(data)));
   synchronized (StoryMenuEntryData.class) { row = candidate; }
  } catch (IOException e) {
   throw e;
  } catch (Exception e) {
   throw new IOException("Menu entry fixed catalog", e);
  }
 }

 private static byte[] read(InputStream in) throws IOException {
  ByteArrayOutputStream out = new ByteArrayOutputStream();
  byte[] buffer = new byte[8192];
  for (int n; (n = in.read(buffer)) != -1; ) {
   if (out.size() > 1000000 - n) throw new IOException("Menu entry bound");
   out.write(buffer, 0, n);
  }
  return out.toByteArray();
 }

 private static List<Integer> ints(JSONArray array) throws JSONException {
  List<Integer> out = new ArrayList<>();
  for (int i = 0; i < array.length(); i++) {
   Object value = array.get(i);
   if (!(value instanceof Integer)) throw new JSONException("Menu entry integer");
   out.add((Integer) value);
  }
  return out;
 }

 private static List<List<Integer>> arrays(JSONArray array) throws JSONException {
  List<List<Integer>> out = new ArrayList<>();
  for (int i = 0; i < array.length(); i++) out.add(ints(array.getJSONArray(i)));
  return out;
 }

 private static List<String> keys(JSONObject value) {
  List<String> out = new ArrayList<>();
  for (Iterator<String> it = value.keys(); it.hasNext(); ) out.add(it.next());
  return out;
 }

 private static String hex(byte[] bytes) {
  StringBuilder out = new StringBuilder();
  for (byte value : bytes) out.append(String.format(Locale.ROOT, "%02x", value & 255));
  return out.toString();
 }

 /** True only for the prepared menu10 closure asset; every other menu is false. */
 public static boolean capability(int menu) {
  Row current = row;
  return current != null && current.open && current.menu == menu;
 }

 /** Capability plus the prepared original selector data. Never edits the allowlist. */
 public static boolean ready(int menu) {
  Row current = row;
  return current != null && current.open && current.menu == menu && StoryMenuShared.capability(menu);
 }

 /**
  * Original Week entry state for menu10: entry event, ending requirements and a
  * committed week/cycle. Other menus are always false.
  */
 public static boolean entryReady(int menu, byte[] profile,
                                  LocalTutorialStore.Progress progress, LocalWeekCatalog weeks) {
  if (!ready(menu) || profile == null || progress == null || weeks == null) return false;
  if (progress.weekCommit == null || progress.weekCommit.isEmpty()) return false;
  Integer entrance = weeks.entrances.get(menu);
  if (entrance == null || entrance <= 0) return false;
  try {
   return LocalWeekEngine.canEnter(profile, weeks, menu);
  } catch (RuntimeException invalid) {
   return false;
  }
 }

 public static boolean entryOpen() {
  Row current = row;
  return current != null && current.open;
 }

 public static int menu() {
  Row current = row;
  return current == null ? -1 : current.menu;
 }

 public static String closedReason() {
  Row current = row;
  return current == null ? "menu entry data not prepared" : current.reason;
 }

 public static String missionSha256(int mission) {
  Row current = row;
  return current == null || mission != MISSION ? null : current.missionSha;
 }

 public static String assetSha256() {
  Row current = row;
  return current == null ? null : current.assetSha;
 }

 /** Original mission320 action/fatigue/overFatigue/recommend cost fields. */
 public static int cost(String field) {
  Row current = row;
  if (current == null) throw new IllegalStateException("menu entry data not prepared");
  if ("va".equals(field)) return current.va;
  if ("fatigue".equals(field)) return current.fatigue;
  if ("overFatigue".equals(field)) return current.overFatigue;
  if ("force_recommend".equals(field)) return current.recommend;
  throw new IllegalArgumentException("Unknown menu10 mission cost field");
 }
}
