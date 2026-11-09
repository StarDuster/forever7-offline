package com.project7.localmanager;

import java.io.*;
import java.lang.reflect.*;
import java.nio.file.*;
import java.util.*;
import org.json.*;

/** Host proof for the generic event auto-trigger candidate asset.
 *
 * Frozen v43 assets/classes only. Builds LocalEventCatalog from the frozen
 * event_graph.tsv and from a temp merged stream (frozen + candidate increment),
 * then exercises the real LocalEventEngine consumer.
 */
public final class AutoTriggerMechanismHost {
    static int checks;
    static Method matchesMethod;
    static Method blockerMethod;

    static void check(boolean value, String message) {
        if (!value) throw new AssertionError(message);
        checks++;
    }

    static LocalEventCatalog load(Path path) throws IOException {
        try (InputStream in = new FileInputStream(path.toFile())) {
            return new LocalEventCatalog(in);
        }
    }

    static LocalEventCatalog load(byte[] data) throws IOException {
        return new LocalEventCatalog(new ByteArrayInputStream(data));
    }

    static byte[] merged(Path base, Path extra) throws IOException {
        ByteArrayOutputStream out = new ByteArrayOutputStream();
        out.write(Files.readAllBytes(base));
        for (String line : Files.readAllLines(extra, java.nio.charset.StandardCharsets.UTF_8)) {
            if (line.isEmpty() || line.startsWith("#")) continue;
            out.write((line + "\n").getBytes("UTF-8"));
        }
        return out.toByteArray();
    }

    static LocalTutorialStore.Progress progress(Integer... completed) {
        LocalTutorialStore.Progress progress = LocalTutorialStore.Progress.fresh();
        progress.inEmergency = false;
        progress.initPrologue = false;
        progress.availableEvents.clear();
        progress.processingEvents.clear();
        progress.processingNewbees.clear();
        progress.completedEvents.addAll(Arrays.asList(completed));
        return progress;
    }

    static byte[] profile(byte[] base, int week, int day, String route) throws IOException {
        byte[] raw = BsonLite.withProfileDocument(base, "weeknum",
                BsonLite.document("w", week, "d", day, "av", 0));
        return BsonLite.withProfileDocument(raw, "std",
                BsonLite.document("rt", route, "ff", false));
    }

    static LocalEventEngine engine(LocalEventCatalog catalog, int starter, byte[] profile,
                                   LocalTutorialStore.Progress progress) throws IOException {
        return new LocalEventEngine(catalog,
                new LocalNewbeeCatalog(new ByteArrayInputStream(new byte[0])),
                progress, starter, profile, true);
    }

    static boolean matches(LocalEventEngine engine, LocalEventCatalog.Trigger trigger) throws Exception {
        return (Boolean) matchesMethod.invoke(engine, trigger);
    }

    static String blocker(LocalEventEngine engine, LocalEventCatalog.Trigger trigger, int clientOperation)
            throws Exception {
        return (String) blockerMethod.invoke(engine, trigger, 0, clientOperation);
    }

    static int triggerCount(LocalEventCatalog catalog) {
        int count = 0;
        for (LocalEventCatalog.Trigger unused : catalog.triggers()) count++;
        return count;
    }

    static boolean sameTrigger(LocalEventCatalog.Trigger left, LocalEventCatalog.Trigger right) {
        return left.eventId == right.eventId
                && left.preAll.equals(right.preAll)
                && left.preAny.equals(right.preAny)
                && left.battles.equals(right.battles)
                && left.mutex.equals(right.mutex)
                && left.areas.equals(right.areas)
                && Arrays.equals(left.date, right.date)
                && Arrays.equals(left.week, right.week)
                && Objects.equals(left.emergency, right.emergency)
                && left.patrolAreas.equals(right.patrolAreas)
                && left.clientOps.equals(right.clientOps)
                && left.areaClicks.equals(right.areaClicks)
                && left.predicates.equals(right.predicates);
    }

    static void checkCandidateAvailable(LocalEventCatalog catalog, byte[] baseProfile, int event,
                                        int week, int day, String route, int operation,
                                        Integer... completed) throws Exception {
        LocalEventCatalog.Trigger trigger = catalog.trigger(event);
        check(trigger != null, "candidate parsed " + event);
        LocalEventEngine engine = engine(catalog, 0, profile(baseProfile, week, day, route),
                progress(completed));
        engine.updateClientOperation(operation);
        check(matches(engine, trigger), "candidate matches " + event);
        check(blocker(engine, trigger, operation) == null, "candidate unblocked " + event);
        Method rescan = LocalEventEngine.class.getDeclaredMethod("reevaluateLifecycle");
        rescan.setAccessible(true);
        rescan.invoke(engine);
        check(engine.availableEvents().contains(event), "candidate available " + event);
    }

    static void checkCandidateBlocked(LocalEventCatalog catalog, byte[] baseProfile, int event,
                                      int week, int day, String route, int operation,
                                      Integer... completed) throws Exception {
        LocalEventCatalog.Trigger trigger = catalog.trigger(event);
        check(trigger != null, "candidate parsed " + event);
        LocalEventEngine engine = engine(catalog, 0, profile(baseProfile, week, day, route),
                progress(completed));
        engine.updateClientOperation(operation);
        check(blocker(engine, trigger, operation) != null, "candidate blocked " + event);
        check(!engine.availableEvents().contains(event), "candidate absent " + event);
    }

    public static void main(String[] args) throws Exception {
        Path assets = Paths.get(args[0]);
        Path extra = Paths.get(args[1]);
        JSONObject contract = new JSONObject(new String(Files.readAllBytes(Paths.get(args[2])), "UTF-8"));
        JSONObject counts = contract.getJSONObject("counts");

        matchesMethod = LocalEventEngine.class.getDeclaredMethod("triggerMatches", LocalEventCatalog.Trigger.class);
        matchesMethod.setAccessible(true);
        blockerMethod = LocalEventEngine.class.getDeclaredMethod("triggerBlocker",
                LocalEventCatalog.Trigger.class, int.class, int.class);
        blockerMethod.setAccessible(true);

        Path baseGraph = assets.resolve("event_graph.tsv");
        byte[] baseProfile = Files.readAllBytes(assets.resolve("new_player.bson"));
        LocalEventCatalog original = load(baseGraph);
        LocalEventCatalog merged = load(merged(baseGraph, extra));

        int frozen = triggerCount(original);
        check(frozen == counts.getInt("frozen_trigger_rows"), "frozen trigger count");

        List<Integer> candidate = new ArrayList<>();
        for (String line : Files.readAllLines(extra, java.nio.charset.StandardCharsets.UTF_8)) {
            if (line.isEmpty() || line.startsWith("#")) continue;
            String[] parts = line.split("\t", -1);
            check(parts.length == 14 && "@trigger".equals(parts[0]), "candidate row schema");
            candidate.add(Integer.parseInt(parts[1]));
        }
        check(candidate.size() == counts.getInt("candidate_rows"), "candidate row count");
        check(triggerCount(merged) == frozen + candidate.size(), "merged trigger count");

        // Every candidate row is a genuine gap row for a released auto event, and the
        // merged catalog parses it back with the projected fields.
        for (Integer event : candidate) {
            LocalEventCatalog.Event row = original.get(event);
            check(row != null && row.autoTrigger && row.release, "candidate auto/release " + event);
            check(original.trigger(event) == null, "candidate was absent " + event);
            LocalEventCatalog.Trigger trigger = merged.trigger(event);
            check(trigger != null, "candidate parsed " + event);
            check(trigger.eventId == event && trigger.emergency != null, "candidate identity " + event);
        }

        // Fallback events keep no row: week entry / @route / successor supplies them.
        JSONObject fallback = contract.getJSONObject("fallback");
        int fallbackCount = 0;
        for (String kind : new String[]{"week", "route", "successor"}) {
            JSONArray list = fallback.getJSONArray(kind);
            fallbackCount += list.length();
            for (int i = 0; i < list.length(); i++) {
                int event = list.getInt(i);
                check(original.get(event) != null && original.get(event).autoTrigger, "fallback auto " + event);
                check(original.trigger(event) == null, "fallback originally absent " + event);
                check(merged.trigger(event) == null, "fallback not invented " + event);
            }
        }
        check(fallbackCount == counts.getInt("fallback_events"), "fallback count");

        // Unproven entry evidence stays rowless; it is neither a candidate nor a normal fallback.
        JSONObject unproven = contract.getJSONObject("unproven");
        int unprovenCount = 0;
        for (String kind : new String[]{"week", "entry"}) {
            JSONArray list = unproven.getJSONArray(kind);
            unprovenCount += list.length();
            for (int i = 0; i < list.length(); i++) {
                int event = list.getInt(i);
                check(original.get(event) != null && original.get(event).autoTrigger, "unproven auto " + event);
                check(original.trigger(event) == null, "unproven originally absent " + event);
                check(merged.trigger(event) == null, "unproven not invented " + event);
            }
        }
        check(unprovenCount == counts.getInt("unproven_events"), "unproven count");

        // Blocked events stay rowless and their codes are outside the evaluator set.
        JSONArray blocked = contract.getJSONArray("blocked");
        check(blocked.length() == counts.getInt("blocked_events"), "blocked count");
        for (int i = 0; i < blocked.length(); i++) {
            JSONObject entry = blocked.getJSONObject(i);
            int event = entry.getInt("event");
            check(original.get(event) != null && original.get(event).autoTrigger, "blocked auto " + event);
            check(merged.trigger(event) == null, "blocked not fabricated " + event);
            JSONArray codes = entry.getJSONArray("codes");
            for (int c = 0; c < codes.length(); c++) {
                Object code = codes.get(c);
                if (!(code instanceof Integer)) continue;
                check(!LocalStoryConditions.SUPPORTED.contains(code), "blocked code unsupported " + code);
            }
        }
        check("unsupported".equals(LocalStoryConditions.evaluate(46, "1,999", baseProfile,
                progress()).status), "code 46 reported unsupported by real evaluator");
        check("unsupported".equals(LocalStoryConditions.evaluate(20, "2:10000", baseProfile,
                progress()).status), "code 20 reported unsupported by real evaluator");

        // Frozen trigger rows are preserved exactly by the append-only merge.
        int compared = 0;
        for (String line : Files.readAllLines(baseGraph, java.nio.charset.StandardCharsets.UTF_8)) {
            if (!line.startsWith("@trigger\t")) continue;
            int event = Integer.parseInt(line.split("\t", -1)[1]);
            LocalEventCatalog.Trigger before = original.trigger(event);
            LocalEventCatalog.Trigger after = merged.trigger(event);
            check(before != null && after != null && sameTrigger(before, after), "frozen row preserved " + event);
            compared++;
        }
        check(compared == frozen, "frozen row comparison count");

        // Case A: previously absent released auto event 1393 becomes consumable after the merge.
        check(original.trigger(1393) == null, "1393 originally absent");
        LocalEventCatalog.Trigger added = merged.trigger(1393);
        check(added != null && added.preAll.isEmpty()
                && added.clientOps.equals(new HashSet<>(Arrays.asList(4)))
                && added.predicates.containsKey(52), "1393 projected row fields");
        byte[] profile = profile(baseProfile, 3, 0, "25");
        LocalEventEngine originalEngine = engine(original, 0, profile, progress());
        check(!originalEngine.availableEvents().contains(1393), "original engine cannot expose 1393");
        LocalEventEngine mergedEngine = engine(merged, 0, profile, progress());
        mergedEngine.updateClientOperation(4);
        check(matches(mergedEngine, added), "1393 triggerMatches on merged catalog");
        check(blocker(mergedEngine, added, 4) == null, "1393 unblocked in matching context");
        Method rescan = LocalEventEngine.class.getDeclaredMethod("reevaluateLifecycle");
        rescan.setAccessible(true);
        rescan.invoke(mergedEngine);
        check(mergedEngine.availableEvents().contains(1393), "1393 available after merge scan");

        // Negative contexts keep the same row blocked.
        LocalEventEngine wrongDay = engine(merged, 0, profile(baseProfile, 3, 1, "25"), progress());
        check(blocker(wrongDay, merged.trigger(1393), 4) != null, "1393 day window");
        LocalEventEngine wrongRoute = engine(merged, 0, profile(baseProfile, 3, 0, "1"), progress());
        check(blocker(wrongRoute, merged.trigger(1393), 4) != null, "1393 route predicate");
        LocalEventEngine wrongOp = engine(merged, 0, profile, progress());
        check(blocker(wrongOp, merged.trigger(1393), 0) != null, "1393 client operation");
        check(!wrongOp.availableEvents().contains(1393), "1393 absent without client operation");

        // Case A2: released events whose only prior exclusion was an @route key or a
        // predecessor edge. Positive and negative contexts, including mutex and completion.
        for (int event : new int[]{1404, 1531, 1592, 1509}) {
            check(original.trigger(event) == null && merged.trigger(event) != null,
                    "route/successor candidate row " + event);
            check(merged.get(event) != null && merged.get(event).release && merged.get(event).autoTrigger,
                    "route/successor candidate auto+release " + event);
        }
        checkCandidateAvailable(merged, baseProfile, 1404, 0, 0, "26", 4);
        checkCandidateBlocked(merged, baseProfile, 1404, 0, 1, "26", 4);          // date
        checkCandidateBlocked(merged, baseProfile, 1404, 0, 0, "25", 4);          // route
        checkCandidateBlocked(merged, baseProfile, 1404, 0, 0, "26", 0);          // operation
        checkCandidateBlocked(merged, baseProfile, 1404, 0, 0, "26", 4, 1403);    // mutex

        checkCandidateAvailable(merged, baseProfile, 1531, 0, 0, "28", 1057);
        checkCandidateBlocked(merged, baseProfile, 1531, 0, 7, "28", 1057);       // date upper bound
        checkCandidateBlocked(merged, baseProfile, 1531, 0, 0, "27", 1057);       // route
        checkCandidateBlocked(merged, baseProfile, 1531, 0, 0, "28", 0);          // operation

        checkCandidateAvailable(merged, baseProfile, 1592, 0, 6, "28-5", 1089);
        checkCandidateBlocked(merged, baseProfile, 1592, 0, 7, "28-5", 1089);     // date upper bound
        checkCandidateBlocked(merged, baseProfile, 1592, 0, 6, "28-4", 1089);     // route
        checkCandidateBlocked(merged, baseProfile, 1592, 0, 6, "28-5", 0);        // operation

        checkCandidateAvailable(merged, baseProfile, 1509, 0, 0, "28-3", 1035);
        checkCandidateBlocked(merged, baseProfile, 1509, 0, 7, "28-3", 1035);     // date upper bound
        checkCandidateBlocked(merged, baseProfile, 1509, 0, 0, "27", 1035);       // route
        checkCandidateBlocked(merged, baseProfile, 1509, 0, 0, "28-3", 0);        // operation
        LocalEventEngine parentDone = engine(merged, 0, profile(baseProfile, 0, 0, "28-3"),
                progress(1508));
        parentDone.updateClientOperation(1035);
        Method parentRescan = LocalEventEngine.class.getDeclaredMethod("reevaluateLifecycle");
        parentRescan.setAccessible(true);
        parentRescan.invoke(parentDone);
        check(Collections.frequency(new ArrayList<>(parentDone.availableEvents()), 1509) == 1,
                "1509 successor dedup after 1508");
        LocalEventEngine selfDone = engine(merged, 0, profile(baseProfile, 0, 0, "28-3"),
                progress(1509));
        selfDone.updateClientOperation(1035);
        parentRescan.invoke(selfDone);
        check(!selfDone.availableEvents().contains(1509), "1509 absent once completed");

        // Case B: unproven week-entry event 1323 is auto but intentionally has no row.
        LocalWeekCatalog weeks = new LocalWeekCatalog(
                new FileInputStream(assets.resolve("weeks.tsv").toFile()));
        check(weeks.entrances.get(20) == 1323, "week 20 entrance is event 1323");
        LocalEventCatalog.Event entry = original.get(1323);
        check(entry != null && entry.autoTrigger, "1323 auto unproven entry event");
        check(original.trigger(1323) == null && merged.trigger(1323) == null, "1323 stays rowless");
        LocalTutorialStore.Progress entryProgress = progress(1047);
        entryProgress.weekIndex = 0;
        LocalEventEngine entryEngine = engine(merged, 1323, profile(baseProfile, 0, 0, "20"), entryProgress);
        check(entryEngine.availableEvents().contains(1323), "1323 supplied by entry path without trigger row");
        check(!entryEngine.availableEvents().contains(1393), "unproven scan does not invent rows");

        System.out.println("PASS " + checks + " v43 auto-trigger checks: projection rows="
                + candidate.size() + " fallback=" + fallbackCount + " blocked=" + blocked.length()
                + " frozen preserved=" + frozen + "; absent 1393 consumable; fallback 1323 rowless");
    }
}
