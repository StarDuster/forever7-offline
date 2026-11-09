package com.project7.localmanager;

import android.content.Context;
import java.io.ByteArrayOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.security.MessageDigest;
import java.util.*;
import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

/**
 * Source-bound offline policy for the seven route-27-1 COC missions 482..488.
 *
 * <p>Admission is checked here from the fixed virtual-data contract before the
 * original Store is asked to begin a battle. Settlement stays on the original
 * LocalProfileStore/LocalEconomyEngine transaction; this class never writes
 * profile bytes itself. The two named offline-compat rules are explicit:
 * <ul>
 *   <li>{@code server-pending-mission-event-v1}: the original mission events
 *       1435..1441 are release=false and are normally created by the server.
 *       Offline we add exactly that one event for the admitted scene to
 *       Progress.processingEvents, then let LocalEventEngine.trace complete it.</li>
 *   <li>{@code original-offline-city-fight-reward-v1}: win settlement uses the
 *       already pinned manager city_fight_reward mapping. The original server
 *       drop/reward rule is not present in client tables and is not invented.</li>
 * </ul>
 * Losses never grant a reward. Both admission and settlement are once-only;
 * a settled scene is rejected before any Store call and a duplicate Store
 * finish is reported as replay without a second grant.
 */
public final class StoryCityCocPolicy {
 private StoryCityCocPolicy() {}

 public static final String POLICY = "source-city-coc-offline-v1";
 public static final String REWARD_POLICY = "original-offline-city-fight-reward-v1";
 public static final String PENDING_EVENT_POLICY = "server-pending-mission-event-v1";
 public static final String DATA = "project7_story_city_virtual/virtual-data-v1.json";
 public static final String DATA_HASH = "83fae3199e308db88513f4a6e6bf6af2288ca749258e3d81b5c81451f8fec6de";

 public static final String ALLOWED = "allowed";
 public static final String NOT_PREPARED = "not-prepared";
 public static final String UNKNOWN_SCENE = "unknown-scene";
 public static final String NOT_OWNED = "not-owned";
 public static final String WEEK_BINDING = "week-binding";
 public static final String GATE_PREDECESSOR = "gate-predecessor";
 public static final String GATE_STATUS = "gate-status";
 public static final String GATE_LOCKED = "gate-locked";
 public static final String PARTY = "party";
 public static final String COST = "cost";
 public static final String UNSUPPORTED_COST = "unsupported-cost-policy";
 public static final String ALREADY_SETTLED = "already-settled";
 public static final String LOSS_NO_REWARD = "loss-no-reward";
 public static final String STORE_REJECTED = "store-rejected";
 public static final String SETTLED = "settled";

 private static final String NS = "q7StoryCity";
 private static final String CATALOG_HASH = "af2328b97372c27fd392b5b399d03daa17fa73acdd35d2b1ad5b0a8f07218069";
 private static final int[] EXPECTED = {482, 483, 484, 485, 486, 487, 488};
 private static volatile Catalog catalog;

 private static final class Mission {
  final int scene, area, completion, va, fatigue, overFatigue, forceRecommend, chainIndex;
  final int[] chain;
  final List<Integer> party;
  Mission(int scene, int area, int completion, int va, int fatigue, int overFatigue, int forceRecommend, int chainIndex, int[] chain, List<Integer> party) {
   this.scene = scene; this.area = area; this.completion = completion; this.va = va;
   this.fatigue = fatigue; this.overFatigue = overFatigue; this.forceRecommend = forceRecommend;
   this.chainIndex = chainIndex; this.chain = chain; this.party = party;
  }
 }
 private static final class Catalog {
  final Map<Integer, Mission> missions = new LinkedHashMap<>();
 }
 public static final class Admission {
  public final int scene, area, actionCost;
  public final boolean allowed;
  public final String reason, rewardPolicy;
  public final List<Integer> party;
  Admission(int scene, int area, int actionCost, boolean allowed, String reason, List<Integer> party) {
   this.scene = scene; this.area = area; this.actionCost = actionCost; this.allowed = allowed;
   this.reason = reason; this.party = party; this.rewardPolicy = REWARD_POLICY;
  }
 }
 public static final class Settlement {
  public final boolean accepted, replay, completed;
  public final String reason, rewardPolicy, pendingEventPolicy;
  public final byte[] reward;
  public final int remainingActions;
  /** Exact original Store result for accepted/store-rejected begin/finish; null when admission rejected before the Store call. */
  public LocalEconomyEngine.Result storeResult;
  Settlement(boolean accepted, boolean replay, boolean completed, String reason, byte[] reward, int remainingActions) {
   this.accepted = accepted; this.replay = replay; this.completed = completed; this.reason = reason;
   this.reward = reward; this.remainingActions = remainingActions;
   this.rewardPolicy = REWARD_POLICY; this.pendingEventPolicy = PENDING_EVENT_POLICY;
  }
 }

 /** Read and validate the pinned runtime virtual-data contract. No analysis dependency. */
 public static void prepare(Context context) throws IOException {
  Catalog next = new Catalog();
  try (InputStream in = context.getAssets().open(DATA)) {
   byte[] raw = read(in, 400000);
   if (!hex(MessageDigest.getInstance("SHA-256").digest(raw)).equals(DATA_HASH)) throw new IOException("COC virtual data hash");
   JSONObject root = new JSONObject(new String(raw, "UTF-8"));
   if (!"project7-story-city-virtual-data-v1".equals(root.getString("schema"))) throw new IOException("COC virtual schema");
   if (root.getJSONObject("checks").getInt("failed") != 0) throw new IOException("COC virtual checks");
   if (!"source-coc-route-27-1-v1".equals(root.getString("policy"))) throw new IOException("COC virtual policy");
   JSONArray missions = root.getJSONArray("missions");
   if (missions.length() != EXPECTED.length) throw new IOException("COC mission count");
   for (int i = 0; i < missions.length(); i++) {
    JSONObject m = missions.getJSONObject(i);
    int scene = m.getInt("scene");
    if (scene != EXPECTED[i] || next.missions.containsKey(scene)) throw new IOException("COC mission order");
    JSONObject cost = m.getJSONObject("cost");
    int va = cost.getInt("va"), fatigue = cost.getInt("fatigue"), over = cost.getInt("overFatigue"), force = cost.getInt("force_recommend");
    if (va < 0 || fatigue < 0 || over < 0 || force < 0) throw new IOException("COC cost");
    JSONArray chainJson = m.getJSONArray("area_chain");
    int[] chain = new int[chainJson.length()];
    for (int j = 0; j < chain.length; j++) chain[j] = chainJson.getInt(j);
    int chainIndex = m.getInt("chain_index");
    if (chainIndex < 1 || chainIndex >= chain.length || chain[chainIndex] != m.getInt("area")) throw new IOException("COC chain");
    JSONArray partyJson = m.getJSONObject("party").getJSONArray("request_heroes");
    List<Integer> party = new ArrayList<>();
    for (int j = 0; j < partyJson.length(); j++) party.add(partyJson.getInt(j));
    if (party.isEmpty() || party.size() != m.getJSONObject("party").getInt("minimum") || party.size() != m.getJSONObject("party").getInt("maximum")) throw new IOException("COC party");
    int completion = m.getJSONObject("success").getInt("event");
    if (completion < 1) throw new IOException("COC completion event");
    next.missions.put(scene, new Mission(scene, m.getInt("area"), completion, va, fatigue, over, force, chainIndex, chain, Collections.unmodifiableList(party)));
   }
   catalog = next;
  } catch (IOException e) { throw e; }
  catch (Exception e) { throw new IOException("COC fixed virtual data", e); }
 }

 /** Pure admission gate: ownership, week, route-27-1 chain gate, replay, party and cost. */
 public static Admission admit(LocalTutorialStore.Progress progress, byte[] profile, int scene, byte[] request) {
  Catalog c = catalog;
  Mission m = c == null ? null : c.missions.get(scene);
  if (m == null) return new Admission(scene, 0, 0, false, c == null ? NOT_PREPARED : UNKNOWN_SCENE, Collections.<Integer>emptyList());
  if (progress == null || !StoryCityPolicy.owns(profile)) return new Admission(scene, m.area, m.va, false, NOT_OWNED, m.party);
  if (progress.weekCommit == null || progress.weekCommit.isEmpty()) return new Admission(scene, m.area, m.va, false, WEEK_BINDING, m.party);
  byte[] binding = doc(profile, NS);
  if (!BsonLite.keys(binding).isEmpty() && (!CATALOG_HASH.equals(BsonLite.stringValue(binding, "catalog")) || !progress.weekCommit.equals(BsonLite.stringValue(binding, "week"))))
   return new Admission(scene, m.area, m.va, false, WEEK_BINDING, m.party);
  if (settled(progress, profile, scene)) return new Admission(scene, m.area, m.va, false, ALREADY_SETTLED, m.party);
  int predecessor = m.chain[m.chainIndex - 1];
  Integer previous = StoryCityPolicy.state(profile, predecessor);
  if (previous == null || previous.intValue() != 0) return new Admission(scene, m.area, m.va, false, GATE_PREDECESSOR, m.party);
  if (StoryCityPolicy.locked(profile, predecessor)) return new Admission(scene, m.area, m.va, false, GATE_LOCKED, m.party);
  if (StoryCityPolicy.status(progress, m.area, profile) != 1) return new Admission(scene, m.area, m.va, false, GATE_STATUS, m.party);
  if (StoryCityPolicy.locked(profile, m.area)) return new Admission(scene, m.area, m.va, false, GATE_LOCKED, m.party);
  if (!partyMatches(request, m)) return new Admission(scene, m.area, m.va, false, PARTY, m.party);
  if (m.fatigue != 0 || m.overFatigue != 0 || m.forceRecommend != 0) return new Admission(scene, m.area, m.va, false, UNSUPPORTED_COST, m.party);
  try { if (LocalEconomyEngine.actions(profile, progress) < m.va) return new Admission(scene, m.area, m.va, false, COST, m.party); }
  catch (RuntimeException invalid) { return new Admission(scene, m.area, m.va, false, COST, m.party); }
  return new Admission(scene, m.area, m.va, true, ALLOWED, m.party);
 }

 /** Admit and ask the original Store to begin the stage. No profile write on rejection. */
 public static Settlement begin(LocalProfileStore store, String account, LocalTutorialStore.Progress progress, byte[] profile, int scene, byte[] request) {
  Admission a = admit(progress, profile, scene, request);
  if (!a.allowed) return new Settlement(false, false, false, a.reason, null, progress == null ? 0 : progress.patrolActions);
  try {
   LocalEconomyEngine.Result result = store.updateEconomy(account, "begin", request, progress);
   Settlement out;
   if (!result.accepted) out = new Settlement(false, false, false, STORE_REJECTED, null, progress.patrolActions);
   else {
    Mission m = catalog.missions.get(scene);
    if (!progress.completedEvents.contains(m.completion)) progress.processingEvents.add(m.completion);
    out = new Settlement(true, false, false, ALLOWED, null, progress.patrolActions);
   }
   out.storeResult = result;
   return out;
  } catch (RuntimeException rejected) {
   return new Settlement(false, false, false, STORE_REJECTED, null, progress.patrolActions);
  }
 }

 /**
  * Settle exactly once through the original Store. Win only grants through the
  * pinned original offline reward mapping; loss clears the pending battle with
  * no reward. The one server-pending mission event is then completed by the
  * original LocalEventEngine.
  */
 public static Settlement settle(LocalProfileStore store, String account, LocalTutorialStore.Progress progress, byte[] profile, int scene, byte[] request, int win, LocalEventEngine engine) {
  Admission a = admit(progress, profile, scene, request);
  if (!a.allowed) return new Settlement(false, false, false, a.reason, null, progress == null ? 0 : progress.patrolActions);
  try {
   LocalEconomyEngine.Result result = store.updateEconomy(account, "finish", request, progress);
   Settlement out;
   if (result.replay) out = new Settlement(true, true, false, ALREADY_SETTLED, result.reward, progress.patrolActions);
   else if (!result.accepted) out = new Settlement(false, false, false, STORE_REJECTED, null, progress.patrolActions);
   else {
    Mission m = catalog.missions.get(scene);
    if (win != 1) {
     progress.processingEvents.remove(m.completion);
     out = new Settlement(true, false, false, LOSS_NO_REWARD, null, progress.patrolActions);
    } else {
     if (!progress.completedEvents.contains(m.completion) && !progress.processingEvents.contains(m.completion)) progress.processingEvents.add(m.completion);
     boolean completed = false;
     if (engine != null) {
      engine.refreshProfile(result.profile);
      engine.trace("battle", Collections.singleton(scene));
      completed = progress.completedEvents.contains(m.completion);
     }
     out = new Settlement(true, false, completed, SETTLED, result.reward, progress.patrolActions);
    }
   }
   out.storeResult = result;
   return out;
  } catch (RuntimeException rejected) {
   return new Settlement(false, false, false, STORE_REJECTED, null, progress.patrolActions);
  }
 }

 /** Durable receipt exists, Progress lacks completion/battle, and the pending completion event is persisted. */
 public static boolean recoverableProgress(LocalTutorialStore.Progress progress, byte[] profile, int scene, byte[] request) {
  if (progress == null || profile == null || catalog == null) return false;
  Mission m = catalog.missions.get(scene);
  if (m == null) return false;
  Set<Integer> battles = progress.eventConditions.get("battle");
  if ((battles != null && battles.contains(scene)) || progress.completedEvents.contains(m.completion)) return false;
  if (!progress.processingEvents.contains(m.completion)) return false;
  if (request == null || !Integer.valueOf(1).equals(BsonLite.intValue(request, "t")) || !Integer.valueOf(scene).equals(BsonLite.intValue(request, "s"))) return false;
  if (!Integer.valueOf(m.area).equals(BsonLite.intValue(doc(request, "d"), "a"))) return false;
  if (!partyMatches(request, m)) return false;
  byte[] receipts = doc(profile, "q7BattleReceipts");
  Integer week = BsonLite.intValue(doc(profile, "weeknum"), "w");
  byte[] receipt = BsonLite.documentValue(receipts, (week == null ? 0 : week.intValue()) + ":" + scene);
  return receipt != null && !BsonLite.keys(receipt).isEmpty();
 }

 /** Once-only predicate shared by admission and the host replay check. */
 public static boolean settled(LocalTutorialStore.Progress progress, byte[] profile, int scene) {
  if (progress == null) return false;
  Set<Integer> battles = progress.eventConditions.get("battle");
  if (battles != null && battles.contains(scene)) return true;
  Catalog c = catalog;
  Mission m = c == null ? null : c.missions.get(scene);
  if (m != null && progress.completedEvents.contains(m.completion)) return true;
  if (profile == null) return false;
  byte[] receipts = doc(profile, "q7BattleReceipts");
  Integer week = BsonLite.intValue(doc(profile, "weeknum"), "w");
  String key = (week == null ? 0 : week.intValue()) + ":" + scene;
  byte[] receipt = BsonLite.documentValue(receipts, key);
  return receipt != null && !BsonLite.keys(receipt).isEmpty();
 }

 public static List<Integer> party(int scene) {
  Catalog c = catalog;
  Mission m = c == null ? null : c.missions.get(scene);
  return m == null ? Collections.<Integer>emptyList() : m.party;
 }

 public static int completionEvent(int scene) {
  Catalog c = catalog;
  Mission m = c == null ? null : c.missions.get(scene);
  return m == null ? 0 : m.completion;
 }

 private static boolean partyMatches(byte[] request, Mission m) {
  if (request == null || !Integer.valueOf(1).equals(BsonLite.intValue(request, "t")) || !Integer.valueOf(m.scene).equals(BsonLite.intValue(request, "s"))) return false;
  if (!Integer.valueOf(m.area).equals(BsonLite.intValue(doc(request, "d"), "a"))) return false;
  byte[] heroes = BsonLite.arrayValue(request, "h");
  if (heroes == null || BsonLite.keys(heroes).size() != m.party.size()) return false;
  for (int i = 0; i < m.party.size(); i++) {
   Number value = BsonLite.numericValue(heroes, Integer.toString(i));
   if (!(value instanceof Integer) || !m.party.get(i).equals(value)) return false;
  }
  return true;
 }
 private static byte[] doc(byte[] profile, String key) {
  byte[] value = profile == null ? null : BsonLite.documentValue(profile, key);
  return value == null ? BsonLite.EMPTY_DOCUMENT : value;
 }
 private static byte[] read(InputStream in, int limit) throws IOException {
  ByteArrayOutputStream out = new ByteArrayOutputStream(); byte[] buffer = new byte[8192];
  for (int n; (n = in.read(buffer)) != -1; ) { if (out.size() > limit - n) throw new IOException("COC data bound"); out.write(buffer, 0, n); }
  return out.toByteArray();
 }
 private static String hex(byte[] value) {
  StringBuilder out = new StringBuilder();
  for (byte b : value) out.append(String.format(Locale.ROOT, "%02x", b & 255));
  return out.toString();
 }
}
