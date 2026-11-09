package com.project7.localmanager;

import android.content.Context;
import java.io.*;
import java.lang.reflect.*;
import java.util.*;
import java.util.concurrent.atomic.AtomicInteger;

/**
 * Source-only menu10 selector11 chain over the original P7 gateway.
 *
 * <p>Every step goes through the compiled v38 frame entry points:
 * {@code LocalGatewayServer.handleReliableRpc} for startEvent /
 * q7CompleteUiEvent / getAreaStagesRequest / combatOfflineRequest and the
 * private {@code handleCombatOfflineFinish} for settlement. The original
 * {@link LocalEventEngine} and {@link LocalProfileStore} therefore own
 * completion, effects, receipts and persistence. No profile bytes are written
 * here and no victory, receipt or successEvent is fabricated.</p>
 *
 * <p>1140 has no dialog/completion condition; the original client flow is
 * startEvent followed by q7CompleteUiEvent, which calls
 * {@code LocalEventEngine.completeImmediateEvent}. 1132 is a dialog event and
 * is completed by clientTraceProcessingEvent with kind=dialog value=1132.</p>
 */
public final class StoryMenu10Policy {
 private StoryMenu10Policy() {}

 public static final String POLICY = "source-menu10-selector11-gateway-v1";
 public static final String ROUTE = "10-6";
 public static final int MENU = 10, AREA = 6, SELECTOR = 11, MISSION = 320, EVENT = 1140, SUCCESS = 1132;
 public static final int ENTRY = 477, CONTINUATION = 1133;
 private static final AtomicInteger SEQUENCE = new AtomicInteger(1), CALLBACK = new AtomicInteger(1);
 private static final byte[] ENTITY = new byte[12];
 private static final Method RELIABLE, FINISH;
 private static final Field ENGINE_PROFILE;

 static {
  try {
   ENGINE_PROFILE = LocalEventEngine.class.getDeclaredField("profile");
   ENGINE_PROFILE.setAccessible(true);
   RELIABLE = LocalGatewayServer.class.getDeclaredMethod("handleReliableRpc",
       OutputStream.class, byte[].class, byte[].class, String.class,
       LocalTutorialStore.Progress.class, LocalEventEngine.class,
       Set.class, Set.class, Map.class, Set.class);
   RELIABLE.setAccessible(true);
   FINISH = LocalGatewayServer.class.getDeclaredMethod("handleCombatOfflineFinish",
       OutputStream.class, byte[].class, byte[].class, String.class,
       LocalTutorialStore.Progress.class, LocalEventEngine.class, Set.class, Set.class);
   FINISH.setAccessible(true);
  } catch (ReflectiveOperationException error) {
   throw new ExceptionInInitializerError(error);
  }
 }

 /** Packaged closure + selector asset must be valid before any gateway call. */
 public static void prepare(Context context) throws IOException {
  StoryMenuEntryData.prepare(context);
  StoryMissionBridge.prepare(context);
  StoryMenuShared.prepare(context);
 }

 /**
  * Original Week entry for menu10 only. The original LocalWeekEngine owns
  * ending requirements (28/29/30), entrance 477 and the new week/cycle commit;
  * this wrapper only rejects a missing or non-menu10 result.
  */
 static LocalResourceEngine.Result enter(byte[] profile, LocalWeekCatalog weeks,
                                        LocalTutorialStore.Progress progress) {
  if (profile == null || weeks == null || progress == null)
   throw new IllegalArgumentException("menu10 entry input");
  if (!StoryMenuEntryData.entryReady(MENU, profile, progress, weeks))
   throw new IllegalStateException("original menu10 entry state is not ready");
  LocalResourceEngine.Result result = LocalWeekEngine.apply(profile, weeks, progress,
      "requestEnterStory", BsonLite.document("i", MENU));
  boolean accepted = false;
  for (LocalResourceEngine.Reply reply : result.replies) {
   if ("replyEnterStory".equals(reply.method))
    accepted = Boolean.TRUE.equals(BsonLite.boolValue(reply.parameters, "r"));
   if ("showMessageStr".equals(reply.method))
    throw new IllegalStateException("original menu10 entry refused: " +
        BsonLite.stringValue(reply.parameters, "m"));
  }
  if (!accepted) throw new IllegalStateException("original requestEnterStory did not accept menu10");
  if (!Integer.valueOf(MENU).equals(BsonLite.intValue(result.profile, "q7ChapterMenu")))
   throw new IllegalStateException("original menu10 entry did not commit q7ChapterMenu");
  return result;
 }

 /**
  * True only after the original 1140 occurrence is committed, route 10-6 and
  * the Wenzi week/cycle are current, the Alan city gate is active, and the
  * original stage projection is selector320 at FIGHT1.
  */
 public static boolean ready(byte[] profile, LocalTutorialStore.Progress progress) {
  try {
   if (!eligible(profile, progress) || !prerequisites(profile, progress)) return false;
   if (!completed1140(profile, progress) || !LocalAlanCityEngine.active(profile, progress)) return false;
   if (StoryMissionBridge.status(progress, AREA, profile) != 1) return false;
   return Integer.valueOf(MISSION).equals(
       BsonLite.intValue(StoryMissionBridge.stages(progress, AREA, profile), "cs"));
  } catch (RuntimeException invalid) {
   return false;
  }
 }

 /** menu10 route10-6 with a bound current week/cycle and the original Wenzi receipt. */
 public static boolean eligible(byte[] profile, LocalTutorialStore.Progress progress) {
  if (profile == null || progress == null || progress.weekCommit == null || progress.weekCommit.isEmpty())
   return false;
  if (!Integer.valueOf(MENU).equals(BsonLite.intValue(profile, "q7ChapterMenu"))) return false;
  if (!ROUTE.equals(BsonLite.stringValue(doc(profile, "std"), "rt"))) return false;
  byte[] wenzi = doc(profile, StoryMenuShared.WENZI_KEY);
  if (BsonLite.intValue(wenzi, "version") == null || BsonLite.intValue(wenzi, "version") != 1)
   return false;
  if (BsonLite.intValue(wenzi, "week") == null || BsonLite.intValue(wenzi, "week") != progress.weekIndex)
   return false;
  return progress.weekCommit.equals(BsonLite.stringValue(wenzi, "cycle"));
 }

 /** Original 1066/1129/1141 occurrences required by LocalAlanCityEngine.active. */
 public static boolean prerequisites(byte[] profile, LocalTutorialStore.Progress progress) {
  for (int event : new int[]{1066, 1129, 1141})
   if (!completed(profile, progress, event)) return false;
  return true;
 }

 /** True only when the original engine owns a day0, once-only 1140 completion. */
 public static boolean completed1140(byte[] profile, LocalTutorialStore.Progress progress) {
  return completed(profile, progress, EVENT);
 }

 public static boolean successOffered(LocalTutorialStore.Progress progress) {
  return progress != null && progress.availableEvents.contains(SUCCESS)
      && !progress.completedEvents.contains(SUCCESS);
 }

 /**
  * Original client area-focus condition ({@code updateEventCondClient} c=100,
  * v=json "area:status"). The original event engine owns the area-click state
  * and re-evaluates the original area triggers; this wrapper only forwards the
  * exact client request shape. It is the generic transition that lets the
  * original 10-6 source chain (1126) open without any per-event write.
  */
 public static byte[] focusArea(LocalGatewayServer gateway, String account,
                                LocalTutorialStore.Progress progress, LocalEventEngine engine,
                                String areaStatus) throws IOException {
  if (progress == null || engine == null)
   throw new IllegalArgumentException("menu10 area focus input");
  if (areaStatus == null || !areaStatus.matches("[0-9]+:[0-9]+"))
   throw new IllegalArgumentException("original area focus shape");
  return reliable(gateway, account, progress, engine, "updateEventCondClient",
      BsonLite.document("c", 100, "v", "\"" + areaStatus + "\""));
 }

 /**
  * Original 1140 start + UI-only completion through the real gateway.
  *
  * <p>Availability must already come from the original event flow: trigger 480
  * (preAll 1129, preAny 479) offers successor 1140. Event 1141 is the later
  * selector/CG gate owned by {@code LocalAlanCityEngine.active}; it is not part
  * of the original 1140 trigger and is therefore not required here.</p>
  */
 public static boolean complete1140(LocalGatewayServer gateway, String account,
                                    LocalTutorialStore.Progress progress, LocalEventEngine engine)
   throws IOException {
  if (progress == null || engine == null)
   throw new IllegalArgumentException("menu10 1140 input");
  byte[] profile = engineProfile(engine);
  if (!eligible(profile, progress))
   throw new IllegalStateException("menu10 route/cycle is not current");
  if (progress.completedEvents.contains(EVENT)) return false;
  if (!progress.availableEvents.contains(EVENT))
   throw new IllegalStateException("1140 is not offered by the original event flow");
  reliable(gateway, account, progress, engine, "startEvent", BsonLite.document("e", EVENT));
  if (!progress.processingEvents.contains(EVENT))
   throw new IllegalStateException("original startEvent did not process 1140");
  reliable(gateway, account, progress, engine, "q7CompleteUiEvent", BsonLite.document("e", EVENT));
  if (!completed1140(engineProfile(engine), progress))
   throw new IllegalStateException("original completeImmediateEvent did not complete 1140");
  return true;
 }

 /** Gateway getAreaStagesRequest for the selector area. */
 public static byte[] query(LocalGatewayServer gateway, String account,
                            LocalTutorialStore.Progress progress, LocalEventEngine engine)
   throws IOException {
  requireActive(engineProfile(engine), progress);
  return reliable(gateway, account, progress, engine, "getAreaStagesRequest",
      BsonLite.document("aid", AREA));
 }

 /** Gateway combatOfflineRequest admission for mission320. */
 public static byte[] admit(LocalGatewayServer gateway, String account,
                            LocalTutorialStore.Progress progress, LocalEventEngine engine,
                            List<Integer> heroes) throws IOException {
  requireActive(engineProfile(engine), progress);
  if (heroes == null || heroes.isEmpty() || heroes.size() > 3 || new HashSet<>(heroes).size() != heroes.size())
   throw new IllegalArgumentException("menu10 selector party shape");
  return reliable(gateway, account, progress, engine, "combatOfflineRequest",
      BsonLite.document("t", 1, "s", MISSION, "d", BsonLite.document("a", AREA), "h", heroes));
 }

 /** Original Store settlement through the private gateway finish entry. */
 public static byte[] finish(LocalGatewayServer gateway, String account,
                             LocalTutorialStore.Progress progress, LocalEventEngine engine,
                             List<Integer> heroes, int win) throws IOException {
  requireActive(engineProfile(engine), progress);
  ByteArrayOutputStream out = new ByteArrayOutputStream();
  byte[] params = BsonLite.document("t", 1, "s", MISSION, "h", heroes, "x", Collections.emptyList(), "w", win);
  try {
   FINISH.invoke(gateway, out, ENTITY, params, account, progress, engine,
       new HashSet<Integer>(), new HashSet<Integer>());
  } catch (ReflectiveOperationException error) {
   throw failure(error);
  }
  return out.toByteArray();
 }

 /** Original 1132 offer: startEvent then the real dialog trace. */
 public static boolean consume1132(LocalGatewayServer gateway, String account,
                                   LocalTutorialStore.Progress progress, LocalEventEngine engine)
   throws IOException {
  if (!successOffered(progress)) throw new IllegalStateException("1132 is not offered by the original result");
  return consumeDialog(gateway, account, progress, engine, SUCCESS);
 }

 /** Original startEvent + client dialog trace for one offered continuation event. */
 public static boolean consumeDialog(LocalGatewayServer gateway, String account,
                                     LocalTutorialStore.Progress progress,
                                     LocalEventEngine engine, int event) throws IOException {
  if (progress == null || !progress.availableEvents.contains(event))
   throw new IllegalStateException("event " + event + " is not offered by the original flow");
  if (progress.completedEvents.contains(event)) return false;
  reliable(gateway, account, progress, engine, "startEvent", BsonLite.document("e", event));
  if (!progress.processingEvents.contains(event))
   throw new IllegalStateException("original startEvent did not process " + event);
  reliable(gateway, account, progress, engine, "clientTraceProcessingEvent",
      BsonLite.document("k", "dialog", "d", BsonLite.document("c", event)));
  return progress.completedEvents.contains(event) && progress.eventCompletions.get(event) == 1;
 }

 /** True only when the original 1133 successor set is offered. */
 public static boolean successorsOffered(LocalTutorialStore.Progress progress) {
  return progress != null && progress.availableEvents.contains(1134)
      && progress.availableEvents.contains(1135) && progress.availableEvents.contains(1136);
 }

 private static void requireActive(byte[] profile, LocalTutorialStore.Progress progress) {
  if (!eligible(profile, progress) || !completed1140(profile, progress))
   throw new IllegalStateException("menu10 selector source is not committed");
  if (!LocalAlanCityEngine.active(profile, progress))
   throw new IllegalStateException("original Alan city gate is not active");
 }

 private static byte[] reliable(LocalGatewayServer gateway, String account,
                                LocalTutorialStore.Progress progress, LocalEventEngine engine,
                                String method, byte[] parameters) throws IOException {
  ByteArrayOutputStream out = new ByteArrayOutputStream();
  byte[] envelope = BsonLite.document("w",
      BsonLite.document("m", method, "p", parameters, "r", SEQUENCE.getAndIncrement()),
      "_cbid_", CALLBACK.getAndIncrement());
  try {
   RELIABLE.invoke(gateway, out, ENTITY, envelope, account, progress, engine,
       new HashSet<Integer>(), new HashSet<Integer>(),
       new HashMap<Integer, LocalPatrolEngine.Result>(), new HashSet<Integer>());
  } catch (ReflectiveOperationException error) {
   throw failure(error);
  }
  return out.toByteArray();
 }

 private static byte[] engineProfile(LocalEventEngine engine) {
  if (engine == null) throw new IllegalArgumentException("menu10 engine");
  try {
   byte[] profile = (byte[]) ENGINE_PROFILE.get(engine);
   if (profile == null) throw new IllegalStateException("menu10 engine profile");
   return profile;
  } catch (IllegalAccessException error) {
   throw new IllegalStateException("Pinned engine profile ABI", error);
  }
 }

 private static boolean completed(byte[] profile, LocalTutorialStore.Progress progress, int event) {
  Integer count = progress == null ? null : progress.eventCompletions.get(event);
  if (progress == null || !progress.completedEvents.contains(event) || count == null || count != 1)
   return false;
  return LocalStoryItemRewardEngine.completedDay(profile, progress, event) == 0;
 }

 private static byte[] doc(byte[] profile, String key) {
  byte[] value = profile == null ? null : BsonLite.documentValue(profile, key);
  return value == null ? BsonLite.EMPTY_DOCUMENT : value;
 }

 private static IOException failure(ReflectiveOperationException error) {
  Throwable cause = error instanceof InvocationTargetException ? ((InvocationTargetException) error).getCause() : error;
  if (cause instanceof IOException) return (IOException) cause;
  if (cause instanceof RuntimeException) throw (RuntimeException) cause;
  return new IOException("Pinned P7 gateway ABI", cause);
 }
}
