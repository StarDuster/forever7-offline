package com.project7.localmanager;

import android.content.Context;
import java.io.*;
import java.lang.reflect.*;
import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.util.*;
import org.json.*;

/**
 * Source-key chapter projection plus the exact selector11 descriptor.
 *
 * <p>Normal chapters remain indexed by area:route exactly as before. Selector11
 * is a separate complete (area,statusBucket,route,selector) descriptor loaded
 * from the packaged original-evidence asset. Query, admission and victory
 * consumption all read that one descriptor; every other route still delegates
 * to the original LocalCityProgress implementation.</p>
 */
public final class StoryMissionBridge {
 private StoryMissionBridge() {}
 private static volatile Catalog catalog;
 private static volatile Special special;
 private static volatile LocalEventCatalog eventCatalog;

 private static final class Chapter {
  final int area;
  final String route;
  final List<List<Integer>> groups;
  final List<Integer> scenes;
  Chapter(int a, String r, List<List<Integer>> g) {
   area = a; route = r; groups = g; scenes = new ArrayList<>();
   for (List<Integer> x : g) scenes.addAll(x);
  }
 }

 private static final class Catalog {
  final Map<String, Chapter> chapters = new HashMap<>();
  final Map<Integer, Integer> areas = new HashMap<>();
  final Map<Integer, List<Integer>> parties = new HashMap<>();
  final Map<Integer, List<Integer>> success = new HashMap<>();
 }

 /** Complete original selector descriptor. No selector is treated as a mission id. */
 private static final class Special {
  final int area, bucket, selector, event, least, max;
  final String route, missionSha, token;
  final List<List<Integer>> groups;
  final List<Integer> members;
  Special(int area, int bucket, String route, int selector, int event, int least, int max,
          List<List<Integer>> groups, List<Integer> members, String missionSha, String token) {
   this.area = area; this.bucket = bucket; this.route = route; this.selector = selector;
   this.event = event; this.least = least; this.max = max;
   this.groups = groups; this.members = members; this.missionSha = missionSha; this.token = token;
  }
 }

 public static void prepare(Context context) throws IOException {
  Catalog next = new Catalog();
  try (BufferedReader in = new BufferedReader(new InputStreamReader(
      context.getAssets().open("project7_story_missions/catalog-v1.tsv"), "UTF-8"))) {
   String line;
   int rows = 0;
   while ((line = in.readLine()) != null) {
    if (++rows > 10000 || line.length() > 100000) throw new IOException("Chapter catalog bound");
    String[] r = line.split("\t", -1);
    if (r[0].equals("P7STORYMISSIONS")) {
     if (r.length != 3 || !r[1].equals("1")) throw new IOException("Chapter catalog version");
     continue;
    }
    try {
     if (r[0].equals("C")) {
      if (r.length != 6 || !r[2].equals("0") || !r[4].equals("0")) throw new IllegalArgumentException();
      int area = Integer.parseInt(r[1]);
      if (area < 1 || area > 8 || !r[3].matches("[0-9]+(?:-[0-9]+)?")) throw new IllegalArgumentException();
      String[] sections = r[5].split(";", -1);
      if (sections.length != 10) throw new IllegalArgumentException();
      List<List<Integer>> groups = new ArrayList<>();
      Set<Integer> seen = new HashSet<>();
      for (String section : sections) {
       List<Integer> g = new ArrayList<>();
       if (!section.isEmpty()) {
        for (String value : section.split(",")) {
         int scene = Integer.parseInt(value);
         if (scene <= 0 || !seen.add(scene)) throw new IllegalArgumentException();
         g.add(scene);
        }
       }
       if (g.size() > 1) throw new IllegalArgumentException();
       groups.add(Collections.unmodifiableList(g));
      }
      if (seen.isEmpty() || next.chapters.put(area + ":" + r[3],
          new Chapter(area, r[3], Collections.unmodifiableList(groups))) != null)
       throw new IllegalArgumentException();
     } else if (r[0].equals("A")) {
      if (r.length != 3) throw new IllegalArgumentException();
      int scene = Integer.parseInt(r[1]), area = Integer.parseInt(r[2]);
      if (scene <= 0 || area < 1 || area > 8 || next.areas.put(scene, area) != null) throw new IllegalArgumentException();
     } else if (r[0].equals("T")) {
      if (r.length != 7) throw new IllegalArgumentException();
      int scene = Integer.parseInt(r[1]);
      List<Integer> party = new ArrayList<>();
      for (String value : r[3].split(",")) {
       int hero = Integer.parseInt(value);
       if (hero <= 0 || party.contains(hero)) throw new IllegalArgumentException();
       party.add(hero);
      }
      if (party.isEmpty() || next.parties.put(scene, Collections.unmodifiableList(party)) != null)
       throw new IllegalArgumentException();
     } else if (r[0].equals("S")) {
      if (r.length != 3) throw new IllegalArgumentException();
      int scene = Integer.parseInt(r[1]);
      List<Integer> success = new ArrayList<>();
      for (String value : r[2].split(",")) {
       int event = Integer.parseInt(value);
       if (event <= 0 || success.contains(event)) throw new IllegalArgumentException();
       success.add(event);
      }
      if (scene <= 0 || success.isEmpty() ||
          next.success.put(scene, Collections.unmodifiableList(success)) != null)
       throw new IllegalArgumentException();
     } else throw new IllegalArgumentException();
    } catch (RuntimeException invalid) {
     throw new IOException("Chapter catalog row " + rows, invalid);
    }
   }
  }
  for (Chapter c : next.chapters.values())
   for (int scene : c.scenes)
    if (!Integer.valueOf(c.area).equals(next.areas.get(scene))) throw new IOException("Chapter mission area closure");
  catalog = next;
  try { eventCatalog = new LocalEventCatalog(context.getAssets().open("event_graph.tsv")); }
  catch (IOException missingGraph) { eventCatalog = null; }
  try {
   special = loadSpecial(context);
  } catch (FileNotFoundException missing) {
   special = null;
  }
 }

 /** Bootstrap requirement: the original selector11 asset must be packaged and valid. */
 public static void prepareSpecial(Context context) throws IOException {
  Special next = loadSpecial(context);
  if (next == null) throw new IOException("Special selector asset missing");
  special = next;
 }

 private static Special loadSpecial(Context context) throws IOException {
  byte[] data;
  try (InputStream in = context.getAssets().open("project7_story_shared/special-selector-v1.json")) {
   ByteArrayOutputStream out = new ByteArrayOutputStream();
   byte[] buffer = new byte[8192];
   for (int n; (n = in.read(buffer)) != -1; ) {
    if (out.size() > 1000000 - n) throw new IOException("Special selector bound");
    out.write(buffer, 0, n);
   }
   data = out.toByteArray();
  }
  try {
   JSONObject root = new JSONObject(new String(data, StandardCharsets.UTF_8));
   if (!"project7-menu-shared-v1".equals(root.getString("schema"))) throw new IOException("Special schema");
   JSONArray key = root.getJSONObject("selector").getJSONArray("key");
   if (key.length() != 4) throw new IOException("Special key");
   int area = key.getInt(0), bucket = key.getInt(1), selector = key.getInt(3);
   String route = key.getString(2);
   JSONObject row = root.getJSONObject("selector").getJSONObject("row");
   if (row.getInt("chapter") != area || row.getInt("status") != bucket ||
       !route.equals(row.getString("route")) || row.getInt("specialStage") != selector)
    throw new IOException("Special row");
   JSONObject section = row.getJSONObject("section");
   if (section.length() != 10) throw new IOException("Special sections");
   List<List<Integer>> groups = new ArrayList<>();
   List<Integer> members = new ArrayList<>();
   for (int i = 0; i < 10; i++) {
    List<Integer> group = ints(section.getJSONArray(Integer.toString(i)));
    if (!group.isEmpty()) groups.add(Collections.unmodifiableList(group));
    members.addAll(group);
   }
   if (members.isEmpty()) throw new IOException("Special membership");
   JSONObject mission = root.getJSONObject("missions").getJSONObject(Integer.toString(members.get(0)));
   if (mission.getInt("id") != members.get(0) || mission.getInt("ch") != area ||
       mission.getInt("system_type") != 1 || mission.getInt("release") != 1)
    throw new IOException("Special mission");
   int least = mission.getInt("least_hero_num"), max = mission.getInt("max_hero_num");
   if (least < 1 || max < least) throw new IOException("Special party bounds");
   String missionSha = root.getJSONObject("mission_sha256").getString(Integer.toString(members.get(0)));
   if (missionSha.length() != 64) throw new IOException("Special mission hash");
   JSONObject ev = root.getJSONObject("event1140");
   int event = ev.getInt("id");
   if (!ev.getBoolean("release") || !ints(ev.getJSONArray("areaFight")).equals(Collections.singletonList(area)))
    throw new IOException("Special occurrence");
   JSONObject map = ev.getJSONObject("areaSpecialStage");
   if (map.length() != 1 || map.getInt(Integer.toString(area)) != selector)
    throw new IOException("Special effect");
   String token = sha256(area + "|" + bucket + "|" + route + "|" + selector + "|" +
       groups + "|" + members + "|" + missionSha);
   return new Special(area, bucket, route, selector, event, least, max,
       Collections.unmodifiableList(groups), Collections.unmodifiableList(members), missionSha, token);
  } catch (JSONException invalid) {
   throw new IOException("Special selector JSON", invalid);
  }
 }

 private static List<Integer> ints(JSONArray array) throws JSONException {
  List<Integer> out = new ArrayList<>();
  for (int i = 0; i < array.length(); i++) {
   Object value = array.get(i);
   if (!(value instanceof Integer)) throw new JSONException("Special integer");
   out.add((Integer) value);
  }
  return out;
 }

 private static String sha256(String value) {
  try {
   byte[] digest = MessageDigest.getInstance("SHA-256").digest(value.getBytes(StandardCharsets.UTF_8));
   StringBuilder out = new StringBuilder();
   for (byte v : digest) out.append(String.format(Locale.ROOT, "%02x", v & 255));
   return out.toString();
  } catch (Exception error) {
   throw new IllegalStateException("SHA-256", error);
  }
 }

 /** Shared descriptor token; null before the packaged asset is loaded. */
 static String specialToken() {
  Special s = special;
  return s == null ? null : s.token;
 }

 private static Special resolveSpecial(LocalTutorialStore.Progress p, int area, byte[] profile) {
  Special s = special;
  if (s == null || p == null || profile == null || area != s.area) return null;
  String route = BsonLite.stringValue(BsonLite.documentValue(profile, "std"), "rt");
  if (!s.route.equals(route)) return null;
  return (Boolean) invoke("LocalAlanCityEngine", "active",
      new Class<?>[]{byte[].class, LocalTutorialStore.Progress.class}, profile, p) ? s : null;
 }

 /** Admission filter only. Original beginStoryBattle still owns processing/pending checks. */
 public static boolean partyAllowed(byte[] params) {
  Special s = special;
  Integer scene = BsonLite.intValue(params, "s");
  Integer type = BsonLite.intValue(params, "t");
  if (s != null && scene != null && scene.intValue() == s.members.get(0).intValue()) {
   if (!Integer.valueOf(1).equals(type)) return false;
   if (!Integer.valueOf(s.area).equals(BsonLite.intValue(BsonLite.documentValue(params, "d"), "a"))) return false;
   byte[] heroes = BsonLite.arrayValue(params, "h");
   if (heroes == null) return false;
   int size = BsonLite.keys(heroes).size();
   if (size < s.least || size > s.max) return false;
   Set<Integer> seen = new HashSet<>();
   for (int i = 0; i < size; i++) {
    Number value = BsonLite.numericValue(heroes, Integer.toString(i));
    if (!(value instanceof Integer) || (Integer) value <= 0 || !seen.add((Integer) value)) return false;
   }
   return true;
  }
  Catalog c = catalog;
  if (c == null) return true;
  Integer sourceArea = scene == null ? null : c.areas.get(scene);
  if (Integer.valueOf(1).equals(type) && sourceArea != null &&
      !sourceArea.equals(BsonLite.intValue(BsonLite.documentValue(params, "d"), "a"))) return false;
  List<Integer> expected = scene == null ? null : c.parties.get(scene);
  if (expected == null) return true;
  if (!Integer.valueOf(2).equals(BsonLite.intValue(params, "t"))) return false;
  byte[] array = BsonLite.arrayValue(params, "h");
  if (array == null || BsonLite.keys(array).size() != expected.size()) return false;
  for (int i = 0; i < expected.size(); i++) {
   Number value = BsonLite.numericValue(array, Integer.toString(i));
   if (!(value instanceof Integer) || !expected.get(i).equals(value)) return false;
  }
  return true;
 }

 /**
  * Offer original mission successEvent targets after a real battle trace.
  *
  * <p>Only a scene on the profile's current exact chapter route is owned here.
  * Existing dedicated owners keep their own restore path; the selector11 scene
  * stays with LocalAlanCityEngine. Existing release/completed/processing/mutex
  * guards stay in force, and replay or loss never offers twice.</p>
  */
 public static void offerMissionOutcomes(LocalTutorialStore.Progress p, byte[] profile) {
  offerMissionOutcomes(p, profile, eventCatalog);
 }

 public static void offerMissionOutcomes(LocalTutorialStore.Progress p, byte[] profile,
                                         LocalEventCatalog events) {
  Catalog c = catalog;
  if (c == null || p == null || profile == null || events == null) return;
  Set<Integer> battle = p.eventConditions.get("battle");
  if (battle == null || battle.isEmpty()) return;
  for (int scene : battle) {
   List<Integer> success = c.success.get(scene);
   if (success == null || !ownedOutcomeScene(c, profile, scene)) continue;
   for (int event : success) {
    if (p.completedEvents.contains(event) || p.processingEvents.contains(event)) continue;
    LocalEventCatalog.Event row = events.get(event);
    if (row == null || !row.release || blockedByMutex(p, events, event)) continue;
    p.availableEvents.add(event);
   }
  }
 }

 private static boolean blockedByMutex(LocalTutorialStore.Progress p,
                                       LocalEventCatalog events, int event) {
  for (int other : events.mutex(event))
   if (p.completedEvents.contains(other) || p.processingEvents.contains(other) ||
       p.availableEvents.contains(other)) return true;
  return false;
 }

 private static boolean ownedOutcomeScene(Catalog c, byte[] profile, int scene) {
  Integer area = c.areas.get(scene);
  if (area == null) return false;
  String route = BsonLite.stringValue(BsonLite.documentValue(profile, "std"), "rt");
  if (route == null) return false;
  Chapter chapter = c.chapters.get(area + ":" + route);
  if (chapter == null) return false;
  for (int owned : chapter.scenes) if (owned == scene) return true;
  return false;
 }

 private static Chapter resolve(LocalTutorialStore.Progress p, int area, byte[] profile) {
  Catalog c = catalog;
  if (c == null || p == null || profile == null) return null;
  String route = BsonLite.stringValue(BsonLite.documentValue(profile, "std"), "rt");
  return route == null ? null : c.chapters.get(area + ":" + route);
 }

 /** Exact promoted route/area chapter presence; no scene or route is invented. */
 public static boolean chapterReady(int area, String route) {
  Catalog c = catalog;
  return c != null && route != null && c.chapters.containsKey(area + ":" + route);
 }

 public static int area(int scene) {
  Special s = special;
  if (s != null && !s.members.isEmpty() && scene == s.members.get(0)) return s.area;
  Catalog c = catalog;
  Integer result = c == null ? null : c.areas.get(scene);
  return result == null ? (Integer) original("Area", new Class<?>[]{int.class}, scene) : result;
 }

 public static byte[] mapStages(LocalTutorialStore.Progress p, int area, byte[] profile) {
  Special s = resolveSpecial(p, area, profile);
  if (s != null) {
   int scene = battle(p, s.members.get(0)) ? 0 : s.members.get(0);
   return BsonLite.document("cs", scene, "sl", s.groups);
  }
  Chapter c = resolve(p, area, profile);
  if (c == null) return (byte[]) original("MapStages", types(), p, area, profile);
  if (status(p, area, profile) != 1) return BsonLite.EMPTY_DOCUMENT;
  int current = 0;
  for (int scene : c.scenes) if (!battle(p, scene)) { current = scene; break; }
  return BsonLite.document("cs", current, "sl", c.groups);
 }

 public static byte[] stages(LocalTutorialStore.Progress p, int area, byte[] profile) {
  offerMissionOutcomes(p, profile, eventCatalog);
  Special s = resolveSpecial(p, area, profile);
  if (s != null) {
   if ((Boolean) invoke("LocalChapterCityEngine", "locked",
       new Class<?>[]{byte[].class, int.class}, profile, area)) return BsonLite.EMPTY_DOCUMENT;
   return mapStages(p, area, profile);
  }
  Chapter c = resolve(p, area, profile);
  if (c == null) return (byte[]) original("Stages", types(), p, area, profile);
  if ((Boolean) invoke("LocalChapterCityEngine", "locked",
      new Class<?>[]{byte[].class, int.class}, profile, area)) return BsonLite.EMPTY_DOCUMENT;
  return mapStages(p, area, profile);
 }

 public static int status(LocalTutorialStore.Progress p, int area, byte[] profile) {
  offerMissionOutcomes(p, profile, eventCatalog);
  Special s = resolveSpecial(p, area, profile);
  if (s != null) return battle(p, s.members.get(0)) ? 0 : 1;
  Chapter c = resolve(p, area, profile);
  if (c == null) return (Integer) original("Status", types(), p, area, profile);
  int previous = (Integer) original("Status", types(), p, area, profile);
  if (previous == 2 || previous == 5) return previous;
  return battle(p, c.scenes.get(c.scenes.size() - 1)) ? 0 : 1;
 }

 public static boolean consumeVictory(LocalTutorialStore.Progress p, byte[] profile, int type, int scene) {
  Special s = resolveSpecial(p, area(scene), profile);
  if (s != null && !s.members.isEmpty() && scene == s.members.get(0)) {
   if (type != 1 || battle(p, scene)) return false;
   if (!Integer.valueOf(scene).equals(BsonLite.intValue(stages(p, s.area, profile), "cs"))) return false;
   return (Boolean) original("ConsumeVictory",
       new Class<?>[]{LocalTutorialStore.Progress.class, byte[].class, int.class, int.class}, p, profile, type, scene);
  }
  Catalog c = catalog;
  Integer area = c == null ? null : c.areas.get(scene);
  Chapter selected = area == null ? null : resolve(p, area, profile);
  if (selected == null) return (Boolean) original("ConsumeVictory",
      new Class<?>[]{LocalTutorialStore.Progress.class, byte[].class, int.class, int.class}, p, profile, type, scene);
  if (type != 1 || battle(p, scene)) return false;
  byte[] stages = stages(p, area, profile);
  if (!Integer.valueOf(scene).equals(BsonLite.intValue(stages, "cs"))) return false;
  return (Boolean) original("ConsumeVictory",
      new Class<?>[]{LocalTutorialStore.Progress.class, byte[].class, int.class, int.class}, p, profile, type, scene);
 }

 private static boolean battle(LocalTutorialStore.Progress p, int scene) {
  return (Boolean) invoke("LocalCityProgress", "hasBattle",
      new Class<?>[]{LocalTutorialStore.Progress.class, int.class}, p, scene);
 }

 private static Class<?>[] types() { return new Class<?>[]{LocalTutorialStore.Progress.class, int.class, byte[].class}; }

 private static Object original(String name, Class<?>[] types, Object... args) {
  try {
   Class<?> owner = Class.forName("com.project7.localmanager.LocalCityProgress");
   Method m;
   try { m = owner.getDeclaredMethod("q7Original" + name, types); }
   catch (NoSuchMethodException hostOriginal) {
    m = owner.getDeclaredMethod(Character.toLowerCase(name.charAt(0)) + name.substring(1), types);
   }
   m.setAccessible(true);
   return m.invoke(null, args);
  } catch (ReflectiveOperationException error) {
   throw failure(error);
  }
 }

 private static Object invoke(String name, String method, Class<?>[] types, Object... args) {
  try {
   Method m = Class.forName("com.project7.localmanager." + name).getDeclaredMethod(method, types);
   m.setAccessible(true);
   return m.invoke(null, args);
  } catch (ReflectiveOperationException error) {
   throw failure(error);
  }
 }

 private static RuntimeException failure(ReflectiveOperationException error) {
  Throwable cause = error instanceof InvocationTargetException ? ((InvocationTargetException) error).getCause() : error;
  if (cause instanceof RuntimeException) return (RuntimeException) cause;
  return new IllegalStateException("Pinned story mission ABI", cause);
 }
}
