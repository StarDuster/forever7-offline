package com.project7.localmanager;

import android.content.Context;
import android.content.res.AssetManager;
import java.io.*;
import java.lang.reflect.*;
import java.nio.ByteBuffer;
import java.nio.ByteOrder;
import java.nio.charset.StandardCharsets;
import java.nio.file.*;
import java.security.MessageDigest;
import java.util.*;
import java.util.zip.Inflater;
import org.json.JSONArray;
import org.json.JSONObject;

/** Finite v63/f81b host for the existing shared week settlement and successful
 * ending route handoff. Production classes are the published v63 OWN inputs;
 * this file only drives the real manager Store/WeekEngine/settlement consumers.
 * The retry delivery also captures the exact get_all_area_info_reply parameter
 * bytes for the original CityMember/CityData consumer.
 * No production recompile, no stage mutation, no D8/APK/native. */
public final class WeekSettlementV63Host {
    static final String ACCOUNT = "host_week_settlement_v63";
    static final int SOURCE_EVENT = 8028;      // real released ending event: ending 7, cg 12
    static final int NEXT_ROUTE = 2;           // original route requiring ending 2|6|7
    static final int WRONG_ROUTE = 3;          // requires ending 8|9, not earned
    static void check(boolean value, String message) { if (!value) throw new AssertionError(message); }
    static byte[] md5(String value) { return RequestEventCatalog.hash("MD5", value.getBytes(StandardCharsets.UTF_8)); }
    static String sha(byte[] bytes) {
        try {
            MessageDigest digest = MessageDigest.getInstance("SHA-256");
            return hex(digest.digest(bytes));
        } catch (Exception failure) { throw new IllegalStateException(failure); }
    }
    static String hex(byte[] bytes) {
        StringBuilder out = new StringBuilder();
        for (byte value : bytes) out.append(String.format(Locale.ROOT, "%02x", value & 255));
        return out.toString();
    }
    static List<ProtoLite.EntityMessage> frames(byte[] wire) throws IOException {
        List<ProtoLite.EntityMessage> result = new ArrayList<ProtoLite.EntityMessage>();
        ByteBuffer buffer = ByteBuffer.wrap(wire).order(ByteOrder.LITTLE_ENDIAN);
        while (buffer.hasRemaining()) {
            int length = buffer.getInt();
            check(buffer.getShort() == 5, "original frame opcode");
            byte[] payload = new byte[length - 2];
            buffer.get(payload);
            result.add(ProtoLite.parseEntityMessage(payload));
        }
        return result;
    }
    static String name(ProtoLite.EntityMessage frame, String... candidates) {
        for (String candidate : candidates) if (Arrays.equals(frame.methodMd5, md5(candidate))) return candidate;
        return "other";
    }
    static int count(List<ProtoLite.EntityMessage> frames, String method) {
        int count = 0;
        for (ProtoLite.EntityMessage frame : frames) if (Arrays.equals(frame.methodMd5, md5(method))) count++;
        return count;
    }
    static byte[] parameters(List<ProtoLite.EntityMessage> frames, String method) {
        for (ProtoLite.EntityMessage frame : frames) if (Arrays.equals(frame.methodMd5, md5(method))) return frame.parameters;
        throw new AssertionError("missing frame " + method);
    }
    static void keys(byte[] document, String... expected) {
        check(document != null, "missing document");
        List<String> actual = BsonLite.keys(document);
        check(actual.equals(Arrays.asList(expected)), "field order " + actual + " != " + Arrays.asList(expected));
    }
    static int countInt(byte[] document, String key) {
        Integer value = BsonLite.intValue(document, key);
        check(value != null, "missing int " + key);
        return value.intValue();
    }
    static final class Fixture {
        final Path root;
        final String account;
        final File file;
        LocalProfileStore store;
        LocalTutorialStore tutorials;
        LocalTutorialStore.Progress progress;
        LocalEventCatalog graph;
        LocalNewbeeCatalog newbees;
        LocalEventEngine engine;
        LocalGatewayServer gateway;
        boolean gatewayClosed;
        Fixture(Path root, String account) { this.root = root; this.account = account; this.file = root.resolve("profiles/" + account + ".bson").toFile(); }
        static Fixture create(File assets, String account) throws Exception {
            Path root = Files.createTempDirectory("week-settlement-v63-");
            Files.createDirectories(root.resolve("profiles"));
            Fixture fixture = new Fixture(root, account);
            fixture.prepareAssets(assets);
            byte[] raw = BsonLite.withAccountIdentity(Files.readAllBytes(new File(assets, "new_player.bson").toPath()), account, 900007);
            raw = BsonLite.withProfileDocument(raw, "weeknum", BsonLite.document("w", 1, "d", 7,
                    "c", BsonLite.EMPTY_DOCUMENT, "l", BsonLite.EMPTY_DOCUMENT));
            raw = BsonLite.withProfileDocument(raw, "std", BsonLite.document("rt", "1", "cef", false,
                    "ed", Collections.<Integer>emptyList()));
            raw = BsonLite.withProfileDocument(raw, "q7WeekResult", BsonLite.EMPTY_DOCUMENT);
            for (String key : new String[] {"q7WeekTransition", "q7DailyPure", "q7EndingEvents",
                    "q7CgClaims", "q7CgNotices", "q7Battle"})
                raw = BsonLite.withoutProfileKey(raw, key);
            Files.write(fixture.file.toPath(), raw);
            LocalTutorialStore.Progress progress = LocalTutorialStore.Progress.fresh();
            progress.initPrologue = false;
            progress.inEmergency = true;
            progress.weekIndex = 1;
            progress.weekCommit = "host_week_source";
            progress.patrolRewardPending = false;
            progress.completedEvents.clear();
            progress.availableEvents.clear();
            progress.processingEvents.clear();
            progress.processingNewbees.clear();
            fixture.tutorials = new LocalTutorialStore(fixture.context(assets));
            fixture.tutorials.save(account, progress);
            fixture.graph = new LocalEventCatalog(new FileInputStream(new File(assets, "event_graph.tsv")));
            fixture.newbees = new LocalNewbeeCatalog(new ByteArrayInputStream(new byte[0]));
            byte[] loaded = fixture.store.load(account, progress);
            fixture.progress = progress;
            fixture.engine = new LocalEventEngine(fixture.graph, fixture.newbees, progress, 0, loaded, true);
            progress.availableEvents.clear();
            progress.processingEvents.clear();
            progress.processingNewbees.clear();
            fixture.tutorials.save(account, progress);
            fixture.gateway = new LocalGatewayServer(0, null, fixture.store, fixture.tutorials,
                    fixture.graph, fixture.newbees, null, null, new LocalGatewayServer.StatusListener() {
                        public void onStatus(boolean success, String message) { }
                    });
            return fixture;
        }
        static Fixture attach(File assets, Path root, String account) throws Exception {
            Fixture fixture = new Fixture(root, account);
            fixture.prepareAssets(assets);
            fixture.graph = new LocalEventCatalog(new FileInputStream(new File(assets, "event_graph.tsv")));
            fixture.newbees = new LocalNewbeeCatalog(new ByteArrayInputStream(new byte[0]));
            fixture.progress = fixture.tutorials.load(account);
            byte[] loaded = fixture.store.load(account, fixture.progress);
            fixture.engine = new LocalEventEngine(fixture.graph, fixture.newbees, fixture.progress, 0, loaded, true);
            fixture.gateway = new LocalGatewayServer(0, null, fixture.store, fixture.tutorials,
                    fixture.graph, fixture.newbees, null, null, new LocalGatewayServer.StatusListener() {
                        public void onStatus(boolean success, String message) { }
                    });
            return fixture;
        }
        Context context(File assets) { return new Context(root.toFile(), new AssetManager(assets)); }
        void prepareAssets(File assets) throws Exception {
            Context context = context(assets);
            CoreDrawPolicy.prepare(context);
            HistoryDrawPolicy.prepare(context);
            SelectorPolicy.prepare(context);
            DynamicDrawPolicy.prepare(context);
            StoryMissionBridge.prepare(context);
            StoryCityPolicy.prepare(context);
            OfflineMechanismGateway.prepare(context);
            EventResetWeekPolicy.prepare(context);
            store = new LocalProfileStore(context);
            tutorials = new LocalTutorialStore(context);
        }
        byte[] profile() throws IOException { return Files.readAllBytes(file.toPath()); }
        byte[] snapshot() throws IOException { return store.load(account, progress); }
        void completeSourceEvent() throws IOException { progress.completedEvents.add(SOURCE_EVENT); tutorials.save(account, progress); }
        List<ProtoLite.EntityMessage> settle() throws Exception {
            ByteArrayOutputStream out = new ByteArrayOutputStream();
            settle(out);
            return frames(out.toByteArray());
        }
        void settle(OutputStream out) throws Exception {
            Method method = LocalGatewayServer.class.getDeclaredMethod("syncEventEffects", OutputStream.class,
                    byte[].class, String.class, LocalTutorialStore.Progress.class, LocalEventEngine.class);
            method.setAccessible(true);
            try { method.invoke(gateway, out, new byte[12], account, progress, engine); }
            catch (InvocationTargetException error) {
                Throwable cause = error.getCause();
                if (cause instanceof Exception) throw (Exception) cause;
                throw new IOException(cause);
            }
        }
        LocalResourceEngine.Result resume() throws IOException {
            return store.updateServices(account, "q7ResumeWeekResult", BsonLite.EMPTY_DOCUMENT, progress);
        }
        boolean weekRpc(OutputStream out, String method, byte[] params) throws Exception {
            Method rpc = LocalGatewayServer.class.getDeclaredMethod("handleWeekRpc", OutputStream.class,
                    byte[].class, byte[].class, byte[].class, String.class,
                    LocalTutorialStore.Progress.class, LocalEventEngine.class);
            rpc.setAccessible(true);
            Object result = rpc.invoke(gateway, out, new byte[12], md5(method), params, account, progress, engine);
            return Boolean.TRUE.equals(result);
        }
        List<ProtoLite.EntityMessage> handoff(int route, int callback) throws Exception {
            ByteArrayOutputStream out = new ByteArrayOutputStream();
            check(weekRpc(out, "requestEnterStoryByEnding",
                    BsonLite.document("i", route, "_cbid_", callback)), "week RPC consumed");
            return frames(out.toByteArray());
        }
        List<ProtoLite.EntityMessage> avatar() throws Exception {
            ByteArrayOutputStream out = new ByteArrayOutputStream();
            check(weekRpc(out, "updateClientAvatarAsk", BsonLite.EMPTY_DOCUMENT), "avatar RPC consumed");
            return frames(out.toByteArray());
        }
        void reliable(OutputStream out, String method, byte[] params, int sequence, int callback) throws Exception {
            Method dispatch = LocalGatewayServer.class.getDeclaredMethod("dispatchReliableRpc", OutputStream.class,
                    byte[].class, byte[].class, String.class, LocalTutorialStore.Progress.class,
                    LocalEventEngine.class, Set.class, Set.class, Map.class, Set.class);
            dispatch.setAccessible(true);
            byte[] wrapper = BsonLite.document("w",
                    BsonLite.document("m", method, "p", params, "r", sequence), "_cbid_", callback);
            try {
                dispatch.invoke(gateway, out, new byte[12], wrapper, account, progress, engine,
                        new HashSet<Integer>(), new HashSet<Integer>(), new HashMap<Integer, Object>(), new HashSet<Integer>());
            } catch (InvocationTargetException error) {
                Throwable cause = error.getCause();
                if (cause instanceof Exception) throw (Exception) cause;
                throw new IOException(cause);
            }
        }
        List<ProtoLite.EntityMessage> pull() throws Exception {
            ByteArrayOutputStream out = new ByteArrayOutputStream();
            pull(out);
            return frames(out.toByteArray());
        }
        void pull(OutputStream out) throws Exception {
            reliable(out, "pullEvents", BsonLite.EMPTY_DOCUMENT, 1, 9001);
        }
        boolean serviceRpc(OutputStream out, String method, byte[] params) throws Exception {
            Method rpc = LocalGatewayServer.class.getDeclaredMethod("handleServiceRpc", OutputStream.class,
                    byte[].class, byte[].class, byte[].class, String.class,
                    LocalTutorialStore.Progress.class, LocalEventEngine.class);
            rpc.setAccessible(true);
            Object result = rpc.invoke(gateway, out, new byte[12], md5(method), params, account, progress, engine);
            return Boolean.TRUE.equals(result);
        }
        void closeGateway() {
            if (!gatewayClosed) { gateway.close(); gatewayClosed = true; }
        }
        void close() {
            closeGateway();
            try {
                if (Files.exists(root)) {
                    java.util.stream.Stream<Path> stream = Files.walk(root);
                    try {
                        for (Path path : (Iterable<Path>) stream.sorted(Comparator.reverseOrder())::iterator)
                            Files.deleteIfExists(path);
                    } finally { stream.close(); }
                }
            } catch (IOException failure) { throw new IllegalStateException(failure); }
        }
    }
    static JSONArray names(List<ProtoLite.EntityMessage> frames, String... candidates) {
        JSONArray out = new JSONArray();
        for (ProtoLite.EntityMessage frame : frames) out.put(name(frame, candidates));
        return out;
    }
    static JSONArray intArray(byte[] document, String key) {
        JSONArray out = new JSONArray();
        for (Integer value : BsonLite.intArrayValues(document, key)) out.put(value.intValue());
        return out;
    }
    static void alignSecond() throws InterruptedException {
        long wait = 1000 - (System.currentTimeMillis() % 1000) + 30;
        Thread.sleep(wait);
    }
    static int int32(byte[] bytes, int offset) {
        return (bytes[offset] & 255) | ((bytes[offset + 1] & 255) << 8) |
                ((bytes[offset + 2] & 255) << 16) | ((bytes[offset + 3] & 255) << 24);
    }
    static int valueEnd(byte[] document, int offset, int type) {
        switch (type) {
            case 0x01: return offset + 8;
            case 0x02: return offset + 4 + int32(document, offset);
            case 0x03:
            case 0x04: return offset + int32(document, offset);
            case 0x05: return offset + 5 + int32(document, offset);
            case 0x06: return offset;
            case 0x07: return offset + 12;
            case 0x08: return offset + 1;
            case 0x09: return offset + 8;
            case 0x0A: return offset;
            case 0x0B: {
                int end = offset + 1;
                while (document[end] != 0) end++;
                end++;
                while (document[end] != 0) end++;
                return end + 1;
            }
            case 0x0C: return offset + 4 + int32(document, offset) + 12;
            case 0x0D:
            case 0x0E: return offset + 4 + int32(document, offset);
            case 0x0F: return offset + int32(document, offset);
            case 0x10: return offset + 4;
            case 0x11: return offset + 8;
            case 0x12: return offset + 8;
            case 0x13: return offset + 16;
            case 0x7F:
            case 0xFF: return offset;
            default: throw new IllegalArgumentException("Unsupported BSON type " + type);
        }
    }
    static Map<String, byte[]> elements(byte[] document) {
        Map<String, byte[]> result = new LinkedHashMap<String, byte[]>();
        if (document == null) return result;
        int end = document.length - 1;
        int offset = 4;
        while (offset < end) {
            int start = offset;
            int type = document[offset++] & 255;
            int keyStart = offset;
            while (document[offset] != 0) offset++;
            String key = new String(document, keyStart, offset - keyStart, StandardCharsets.UTF_8);
            offset++;
            int valueEnd = valueEnd(document, offset, type);
            result.put(key, Arrays.copyOfRange(document, start, valueEnd));
            offset = valueEnd;
        }
        return result;
    }
    static void addDiff(JSONArray out, String path) {
        if (!out.toList().contains(path)) out.put(path);
    }
    static void collectDiff(byte[] left, byte[] right, String path, JSONArray out) {
        Map<String, byte[]> leftElements = elements(left);
        Map<String, byte[]> rightElements = elements(right);
        List<String> keys = new ArrayList<String>(leftElements.keySet());
        for (String key : rightElements.keySet()) if (!keys.contains(key)) keys.add(key);
        for (String key : keys) {
            String child = path.isEmpty() ? key : path + "/" + key;
            byte[] leftValue = leftElements.get(key);
            byte[] rightValue = rightElements.get(key);
            if (leftValue == null || rightValue == null) { addDiff(out, child); continue; }
            int leftType = leftValue[0] & 255;
            int rightType = rightValue[0] & 255;
            if (leftType != rightType) { addDiff(out, child); continue; }
            if (leftType == 0x03) {
                int leftStart = 1 + key.getBytes(StandardCharsets.UTF_8).length + 1;
                byte[] leftDocument = Arrays.copyOfRange(leftValue, leftStart, leftValue.length);
                byte[] rightDocument = Arrays.copyOfRange(rightValue, leftStart, rightValue.length);
                collectDiff(leftDocument, rightDocument, child, out);
            } else if (!Arrays.equals(leftValue, rightValue)) {
                addDiff(out, child);
            }
        }
    }
    static JSONArray profileDiff(byte[] left, byte[] right) {
        JSONArray out = new JSONArray();
        collectDiff(left, right, "", out);
        return out;
    }
    static void rejectCanonical(byte[] weeknum, byte[] std, byte[] transition, byte[] result,
            List<Integer> cgs, byte[] endingEvents, byte[] profile, String prefix) {
        check(Arrays.equals(weeknum, BsonLite.documentValue(profile, "weeknum")), prefix + " week unchanged");
        check(Arrays.equals(std, BsonLite.documentValue(profile, "std")), prefix + " story flags unchanged");
        check(Arrays.equals(transition, BsonLite.documentValue(profile, "q7WeekTransition")), prefix + " transition unchanged");
        check(Arrays.equals(result, BsonLite.documentValue(profile, "q7WeekResult")), prefix + " result unchanged");
        check(cgs.equals(BsonLite.intArrayValues(profile, "cgs")), prefix + " cgs unchanged");
        check(Arrays.equals(endingEvents, BsonLite.documentValue(profile, "q7EndingEvents")), prefix + " ending markers unchanged");
    }
    public static void main(String[] args) throws Exception {
        File assets = new File(args[0]);
        String output = args[1];
        String avatarWirePath = args.length > 2 ? args[2] : null;
        // Deterministic original clock/random: the manager reads LocalStoryEnvironment
        // for time-sensitive normalization; this removes rerun drift without changing state.
        LocalStoryEnvironment.Scope environment = LocalStoryEnvironment.fixture(20261105L, 1762348800000L);
        JSONObject cases = new JSONObject();
        Fixture fixture = Fixture.create(assets, ACCOUNT);
        String committedId = null;
        byte[] avatarWire = null;
        try {
            String probeAccount = ACCOUNT + "_probe";
            Path probeFile = fixture.root.resolve("profiles/" + probeAccount + ".bson");
            byte[] probeRaw = BsonLite.withAccountIdentity(Files.readAllBytes(new File(assets, "new_player.bson").toPath()), probeAccount, 900008);
            Files.write(probeFile, probeRaw);
            LocalTutorialStore.Progress probeProgress = LocalTutorialStore.Progress.fresh();
            fixture.tutorials.save(probeAccount, probeProgress);
            fixture.store.load(probeAccount, probeProgress);
            JSONArray stockLoadNormalization = profileDiff(probeRaw, Files.readAllBytes(probeFile));
            cases.put("stock_load_normalization", new JSONObject()
                    .put("changed_fields", stockLoadNormalization)
                    .put("before_sha256", sha(probeRaw))
                    .put("after_sha256", sha(Files.readAllBytes(probeFile))));

            byte[] beforeSettlement = fixture.profile();
            fixture.completeSourceEvent();
            List<ProtoLite.EntityMessage> settled = fixture.settle();
            byte[] settledProfile = fixture.snapshot();
            check(count(settled, "showWeekResult") == 1, "one settlement notice");
            byte[] weekNotice = parameters(settled, "showWeekResult");
            keys(weekNotice, "r", "rd");
            check(countInt(weekNotice, "r") == 7, "earned ending 7");
            byte[] rewardNotice = BsonLite.documentValue(weekNotice, "rd");
            check(rewardNotice != null, "week reward document");
            List<String> rewardKeys = BsonLite.keys(rewardNotice);
            for (String required : new String[] {"money", "exp", "item", "hero", "treasure"})
                check(rewardKeys.contains(required), "week reward field " + required);
            byte[] cgNotice = parameters(settled, "addCg");
            keys(cgNotice, "c");
            check(BsonLite.intArrayValues(cgNotice, "c").contains(Integer.valueOf(12)), "earned cg 12");
            keys(parameters(settled, "syncWeeknumScoreInfo"), "wsi", "ls");
            keys(parameters(settled, "updateStoryFlag"), "f");
            byte[] std = BsonLite.documentValue(settledProfile, "std");
            check(BsonLite.intArrayValues(std, "ed").equals(Collections.singletonList(7)), "persisted ending 7");
            check(BsonLite.intArrayValues(settledProfile, "cgs").equals(Collections.singletonList(12)), "persisted cg 12");
            byte[] weekResult = BsonLite.documentValue(settledProfile, "q7WeekResult");
            keys(weekResult, "version", "week", "event", "ending", "score", "reward");
            check(countInt(weekResult, "version") == 2, "settled week result version");
            check(countInt(weekResult, "week") == 1, "settled week result week");
            check(countInt(weekResult, "event") == SOURCE_EVENT, "settled source event");
            check(countInt(weekResult, "ending") == 7, "settled ending");
            check(Boolean.TRUE.equals(BsonLite.boolValue(BsonLite.documentValue(settledProfile, "q7EndingEvents"), "8028")),
                    "settlement marker");
            check(BsonLite.boolValue(std, "cef") == null || !BsonLite.boolValue(std, "cef").booleanValue(),
                    "terminal story flag cleared");
            check(!Arrays.equals(beforeSettlement, settledProfile), "settlement persisted");

            byte[] beforeResume = fixture.profile();
            LocalResourceEngine.Result resumed = fixture.resume();
            boolean resumeCg = false, resumeWeek = false;
            for (LocalResourceEngine.Reply reply : resumed.replies) {
                if (reply.method.equals("addCg")) resumeCg = BsonLite.intArrayValues(reply.parameters, "c").contains(Integer.valueOf(12));
                if (reply.method.equals("showWeekResult")) {
                    check(countInt(reply.parameters, "r") == 7, "resumed ending");
                    resumeWeek = true;
                }
            }
            check(resumeCg && resumeWeek, "showWeekResult/addCg replay on reload");
            check(Arrays.equals(beforeResume, fixture.profile()), "replay does not duplicate settlement");
            JSONObject settlement = new JSONObject();
            settlement.put("notices", names(settled, "addCg", "syncWeeknumScoreInfo", "updateStoryFlag", "showWeekResult"));
            settlement.put("showWeekResult_keys", new JSONArray(BsonLite.keys(weekNotice)));
            settlement.put("q7WeekResult_keys", new JSONArray(BsonLite.keys(weekResult)));
            settlement.put("reward_keys", new JSONArray(rewardKeys));
            settlement.put("q7WeekResult_version", countInt(weekResult, "version"));
            settlement.put("std_ed", intArray(std, "ed"));
            settlement.put("cgs", intArray(settledProfile, "cgs"));
            settlement.put("resume_notices", resumed.replies.size());
            cases.put("settlement", settlement);

            fixture.snapshot();
            byte[] beforeRouteReject = fixture.profile();
            Properties progressBeforeRouteReject = fixture.progress.toProperties();
            byte[] routeRejectWeeknum = BsonLite.documentValue(beforeRouteReject, "weeknum");
            byte[] routeRejectStd = BsonLite.documentValue(beforeRouteReject, "std");
            byte[] routeRejectTransition = BsonLite.documentValue(beforeRouteReject, "q7WeekTransition");
            byte[] routeRejectResult = BsonLite.documentValue(beforeRouteReject, "q7WeekResult");
            List<Integer> routeRejectCgs = BsonLite.intArrayValues(beforeRouteReject, "cgs");
            byte[] routeRejectEndingEvents = BsonLite.documentValue(beforeRouteReject, "q7EndingEvents");
            List<ProtoLite.EntityMessage> routeRejected = fixture.handoff(WRONG_ROUTE, 700);
            check(routeRejected.size() == 2, "positive-ending route rejection emits message and reply");
            check(name(routeRejected.get(0), "showMessageStr").equals("showMessageStr"), "route rejection message first");
            check(Boolean.FALSE.equals(BsonLite.boolValue(parameters(routeRejected, "replyEnterStoryByEnding"), "r")),
                    "route rejection typed false");
            rejectCanonical(routeRejectWeeknum, routeRejectStd, routeRejectTransition, routeRejectResult,
                    routeRejectCgs, routeRejectEndingEvents, fixture.profile(), "route rejection");
            check(progressBeforeRouteReject.equals(fixture.progress.toProperties()), "route rejection Progress unchanged");
            JSONObject routeRejection = new JSONObject();
            routeRejection.put("frames", names(routeRejected, "showMessageStr", "replyEnterStoryByEnding"));
            routeRejection.put("reason", BsonLite.stringValue(parameters(routeRejected, "showMessageStr"), "m"));
            cases.put("negative_route", routeRejection);

            String sourceCommit = fixture.progress.weekCommit;
            List<ProtoLite.EntityMessage> handoff = fixture.handoff(NEXT_ROUTE, 701);
            check(handoff.size() == 2, "handoff emits selector reply and increment ack: " + names(handoff));
            check(name(handoff.get(0), "replyEnterStoryByEnding").equals("replyEnterStoryByEnding"), "selector reply first");
            check(name(handoff.get(1), "handleIncWeekReply").equals("handleIncWeekReply"), "increment ack second");
            check(count(handoff, "showMessageStr") == 0, "no handoff rejection");
            check(count(handoff, "replyTriggerEventByEnding") == 0, "success handoff is not the failure trigger");
            byte[] enterReply = parameters(handoff, "replyEnterStoryByEnding");
            keys(enterReply, "r");
            check(Boolean.TRUE.equals(BsonLite.boolValue(enterReply, "r")), "selector accepted");
            byte[] transitionProfile = fixture.snapshot();
            byte[] transition = BsonLite.documentValue(transitionProfile, "q7WeekTransition");
            keys(transition, "id", "week", "method", "route", "progress");
            committedId = BsonLite.stringValue(transition, "id");
            check(committedId != null && committedId.length() > 0 && !committedId.equals(sourceCommit), "new week transaction id");
            check(countInt(transition, "week") == 2, "target week 2");
            check("requestEnterStoryByEnding".equals(BsonLite.stringValue(transition, "method")), "handoff method");
            check(countInt(transition, "route") == NEXT_ROUTE, "target route 2");
            byte[] transitionProgress = BsonLite.documentValue(transition, "progress");
            check(transitionProgress != null, "serialized progress");
            check("534".equals(BsonLite.stringValue(transitionProgress, "availableEvents")),
                    "original route 2 starting event available");
            check(committedId.equals(BsonLite.stringValue(transitionProgress, "week.commit")),
                    "serialized progress identity");
            check(committedId.equals(fixture.progress.weekCommit), "Progress recovered from transition");
            check(fixture.progress.weekIndex == 2, "Progress week index");
            byte[] weeknum = BsonLite.documentValue(transitionProfile, "weeknum");
            check(countInt(weeknum, "w") == 2 && countInt(weeknum, "d") == 0, "new week day reset");
            check(BsonLite.keys(BsonLite.documentValue(transitionProfile, "q7WeekResult")).isEmpty(), "settled result consumed");
            check(BsonLite.intArrayValues(transitionProfile, "cgs").equals(Collections.singletonList(12)), "permanent cg retained");
            check(BsonLite.intArrayValues(BsonLite.documentValue(transitionProfile, "std"), "ed").equals(Collections.singletonList(7)),
                    "permanent ending retained");
            check(NEXT_ROUTE == countInt(transitionProfile, "q7ChapterMenu"), "route selector committed");
            JSONObject handoffCase = new JSONObject();
            handoffCase.put("frames", names(handoff, "replyEnterStoryByEnding", "handleIncWeekReply", "replyEnterStory", "handleResetWeekReply", "showMessageStr"));
            handoffCase.put("transition_keys", new JSONArray(BsonLite.keys(transition)));
            handoffCase.put("week", countInt(transition, "week"));
            handoffCase.put("route", countInt(transition, "route"));
            handoffCase.put("method", BsonLite.stringValue(transition, "method"));
            handoffCase.put("transition_id", committedId);
            handoffCase.put("progress_keys", new JSONArray(BsonLite.keys(transitionProgress)));
            handoffCase.put("available_event", BsonLite.stringValue(transitionProgress, "availableEvents"));
            cases.put("handoff", handoffCase);

            List<ProtoLite.EntityMessage> avatar = fixture.avatar();
            check(avatar.size() >= 2, "avatar chain emits code and payload");
            check(name(avatar.get(0), "evalCode").equals("evalCode"), "transient reset first");
            check(name(avatar.get(1), "updateClientAvatarReply").equals("updateClientAvatarReply"), "full avatar reply second");
            byte[] evalCode = parameters(avatar, "evalCode");
            keys(evalCode, "s");
            check(BsonLite.stringValue(evalCode, "s").contains("event_trigger_cache"), "original transient reset code");
            byte[] avatarReply = parameters(avatar, "updateClientAvatarReply");
            keys(avatarReply, "s");
            avatarWire = BsonLite.binaryValue(avatarReply, "s");
            check(avatarWire != null && avatarWire.length > 0, "nonempty avatar wire");
            if (avatarWirePath != null) Files.write(Paths.get(avatarWirePath), avatarWire);
            Inflater inflater = new Inflater();
            inflater.setInput(avatarWire);
            byte[] decoded = new byte[1 << 20];
            int decodedLength = inflater.inflate(decoded);
            inflater.end();
            check(decodedLength > 1024, "full avatar payload length");
            check((decoded[0] & 255) >= 0x80 && (decoded[0] & 255) <= 0x8f || (decoded[0] & 255) == 0xde,
                    "msgpack map payload");
            String decodedText = new String(decoded, 0, decodedLength, StandardCharsets.UTF_8);
            check(decodedText.contains("weeknum") && decodedText.contains("std"), "full avatar documents");
            byte[] avatarReset = fixture.profile();
            check(committedId.equals(BsonLite.stringValue(BsonLite.documentValue(avatarReset, "q7WeekTransition"), "id")),
                    "avatar handshake keeps transition");
            List<ProtoLite.EntityMessage> avatarReplay = fixture.avatar();
            byte[] replayWire = parameters(avatarReplay, "updateClientAvatarReply");
            check(BsonLite.binaryValue(replayWire, "s") != null && BsonLite.binaryValue(replayWire, "s").length > 0,
                    "avatar replay payload");
            byte[] replayProfile = fixture.profile();
            check(committedId.equals(BsonLite.stringValue(BsonLite.documentValue(replayProfile, "q7WeekTransition"), "id")),
                    "avatar replay keeps transition");
            check(countInt(BsonLite.documentValue(replayProfile, "weeknum"), "w") == 2, "avatar replay keeps week");
            check(committedId.equals(fixture.progress.weekCommit), "avatar replay keeps committed identity");
            boolean avatarReplaySame = Arrays.equals(replayWire, avatarReply);
            JSONObject avatarCase = new JSONObject();
            avatarCase.put("frames", names(avatar, "evalCode", "updateClientAvatarReply"));
            avatarCase.put("wire_sha256", sha(avatarWire));
            avatarCase.put("wire_bytes", avatarWire.length);
            avatarCase.put("msgpack_bytes", decodedLength);
            avatarCase.put("replay_same_wire", avatarReplaySame);
            cases.put("avatar", avatarCase);

            byte[] beforeWarm = fixture.profile();
            fixture.snapshot();
            byte[] warmed = fixture.profile();
            JSONArray warmNormalization = profileDiff(beforeWarm, warmed);
            // The stock week guard calls profileProvider.snapshot, whose load path writes
            // city.jpvt from System.currentTimeMillis. Align to a fresh second and make one
            // warm idempotent request so the measured repeat stays inside the same second.
            alignSecond();
            fixture.handoff(NEXT_ROUTE, 699);
            byte[] beforeFailedDelivery = fixture.profile();
            boolean failedWrite = false;
            try { fixture.pull(new OutputStream(){ public void write(int b) throws IOException { throw new IOException("host pending write failure"); } }); }
            catch (IOException expected) { failedWrite = true; }
            check(failedWrite, "pending delivery write failure propagates");
            byte[] pendingFailed = BsonLite.documentValue(fixture.profile(), "q7StoryPending");
            check(pendingFailed != null && !BsonLite.keys(pendingFailed).isEmpty(), "write failure retains pending delivery");
            check(Arrays.equals(BsonLite.documentValue(beforeFailedDelivery, "q7StoryPending"), pendingFailed), "write failure preserves exact pending payload");
            check(Arrays.equals(BsonLite.documentValue(beforeFailedDelivery, "q7WeekTransition"), BsonLite.documentValue(fixture.profile(), "q7WeekTransition")), "write failure does not duplicate week transition");
            List<ProtoLite.EntityMessage> pendingDelivery = fixture.pull();
            check(count(pendingDelivery, "pullEventsReply") == 1, "real pullEvents delivery reply");
            byte[] areaReply = parameters(pendingDelivery, "get_all_area_info_reply");
            check(areaReply != null, "pullEvents retry emits pending area reply");
            if (args.length > 3) Files.write(Paths.get(args[3]), areaReply);
            cases.put("area_reply", new JSONObject()
                    .put("method", "get_all_area_info_reply")
                    .put("keys", new JSONArray(BsonLite.keys(areaReply)))
                    .put("bytes", areaReply.length)
                    .put("sha256", sha(areaReply))
                    .put("sm", BsonLite.boolValue(areaReply, "sm"))
                    .put("area_keys", new JSONArray(BsonLite.keys(BsonLite.documentValue(areaReply, "ais")))));
            byte[] pendingAfter = BsonLite.documentValue(fixture.profile(), "q7StoryPending");
            boolean pendingCleared = pendingAfter == null || BsonLite.keys(pendingAfter).isEmpty();
            System.out.println("PENDING_DELIVERY frames=" + names(pendingDelivery, "reliableRpcAck", "pullEventsReply",
                    "get_all_area_info_reply", "pushEvents", "putEvents") + " cleared=" + pendingCleared);
            check(pendingCleared, "gateway delivery clears q7StoryPending");
            cases.put("pending_delivery", new JSONObject()
                    .put("method", "pullEvents")
                    .put("params", "{}")
                    .put("frames", names(pendingDelivery, "reliableRpcAck", "pullEventsReply",
                            "get_all_area_info_reply"))
                    .put("pending_cleared", pendingCleared));
            byte[] beforeRepeat = fixture.profile();
            System.out.println("BEFORE_REPEAT pending=" + Base64.getEncoder().encodeToString(BsonLite.documentValue(beforeRepeat,"q7StoryPending")==null?new byte[0]:BsonLite.documentValue(beforeRepeat,"q7StoryPending")));
            System.out.println("BEFORE_REPEAT transition=" + Base64.getEncoder().encodeToString(BsonLite.documentValue(beforeRepeat,"q7WeekTransition")==null?new byte[0]:BsonLite.documentValue(beforeRepeat,"q7WeekTransition")));
            Properties progressBeforeRepeat = fixture.progress.toProperties();
            List<ProtoLite.EntityMessage> repeated = fixture.handoff(NEXT_ROUTE, 702);
            boolean repeatedOk = repeated.size() == 2 && Boolean.TRUE.equals(BsonLite.boolValue(parameters(repeated, "replyEnterStoryByEnding"), "r"));
            if (!repeatedOk) {
                System.out.println("REPEAT frames=" + names(repeated));
                for (ProtoLite.EntityMessage frame : repeated)
                    System.out.println("REPEAT frame=" + name(frame) + " params=" + Base64.getEncoder().encodeToString(frame.parameters));
                System.out.println("REPEAT profile_diff=" + profileDiff(beforeRepeat, fixture.profile()));
                System.out.println("REPEAT progress_same=" + progressBeforeRepeat.equals(fixture.progress.toProperties()));
            }
            check(repeatedOk,
                    "repeated selector accepted without new transition");
            byte[] repeatedProfile = fixture.profile();
            JSONArray requestSideEffect = profileDiff(beforeRepeat, repeatedProfile);
            check(Arrays.equals(beforeRepeat, repeatedProfile),
                    "repeated handoff raw profile changed: " + requestSideEffect);
            check(requestSideEffect.length() == 0, "repeated handoff wrote profile fields: " + requestSideEffect);
            check(committedId.equals(BsonLite.stringValue(BsonLite.documentValue(repeatedProfile, "q7WeekTransition"), "id")),
                    "repeated handoff keeps transaction");
            check(countInt(BsonLite.documentValue(repeatedProfile, "weeknum"), "w") == 2, "repeated handoff does not advance again");
            check(progressBeforeRepeat.equals(fixture.progress.toProperties()), "repeated handoff Progress unchanged");
            fixture.snapshot();
            byte[] afterLoad = fixture.profile();
            JSONArray readNormalization = profileDiff(repeatedProfile, afterLoad);
            JSONObject repeatCase = new JSONObject();
            repeatCase.put("frames", names(repeated, "replyEnterStoryByEnding", "handleIncWeekReply", "showMessageStr"));
            repeatCase.put("request_side_effect_before_sha256", sha(beforeRepeat));
            repeatCase.put("request_side_effect_after_sha256", sha(repeatedProfile));
            repeatCase.put("request_side_effect_changed_fields", requestSideEffect);
            repeatCase.put("warm_normalization_changed_fields", warmNormalization);
            repeatCase.put("read_normalization_changed_fields", readNormalization);
            cases.put("idempotent", repeatCase);

            fixture.snapshot();
            byte[] beforeFailure = fixture.profile();
            Properties progressBeforeFailure = fixture.progress.toProperties();
            byte[] beforeFailureWeeknum = BsonLite.documentValue(beforeFailure, "weeknum");
            byte[] beforeFailureStd = BsonLite.documentValue(beforeFailure, "std");
            byte[] beforeFailureTransition = BsonLite.documentValue(beforeFailure, "q7WeekTransition");
            byte[] beforeFailureResult = BsonLite.documentValue(beforeFailure, "q7WeekResult");
            List<Integer> beforeFailureCgs = BsonLite.intArrayValues(beforeFailure, "cgs");
            byte[] beforeFailureEndingEvents = BsonLite.documentValue(beforeFailure, "q7EndingEvents");
            List<ProtoLite.EntityMessage> rejected = fixture.handoff(WRONG_ROUTE, 703);
            check(rejected.size() == 2, "typed rejection emits message and reply");
            check(name(rejected.get(0), "showMessageStr").equals("showMessageStr"), "rejection message first");
            byte[] rejectedReply = parameters(rejected, "replyEnterStoryByEnding");
            check(Boolean.FALSE.equals(BsonLite.boolValue(rejectedReply, "r")), "rejection typed false");
            check(BsonLite.stringValue(parameters(rejected, "showMessageStr"), "m").length() > 0, "rejection reason");
            rejectCanonical(beforeFailureWeeknum, beforeFailureStd, beforeFailureTransition, beforeFailureResult,
                    beforeFailureCgs, beforeFailureEndingEvents, fixture.profile(), "rejection");
            check(progressBeforeFailure.equals(fixture.progress.toProperties()), "rejection Progress unchanged");
            check(committedId.equals(BsonLite.stringValue(BsonLite.documentValue(fixture.profile(),
                    "q7WeekTransition"), "id")), "rejection keeps committed transition");

            ByteArrayOutputStream triggerOut = new ByteArrayOutputStream();
            check(fixture.serviceRpc(triggerOut, "requestTriggerEventByEnding",
                    BsonLite.document("e", 8029, "_cbid_", 704)), "failure trigger consumed");
            List<ProtoLite.EntityMessage> trigger = frames(triggerOut.toByteArray());
            check(count(trigger, "replyTriggerEventByEnding") == 1, "typed failure trigger reply");
            check(Boolean.FALSE.equals(BsonLite.boolValue(parameters(trigger, "replyTriggerEventByEnding"), "r")),
                    "failure trigger typed false");
            check(count(trigger, "replyEnterStoryByEnding") == 0, "failure trigger is not success handoff");
            rejectCanonical(beforeFailureWeeknum, beforeFailureStd, beforeFailureTransition, beforeFailureResult,
                    beforeFailureCgs, beforeFailureEndingEvents, fixture.profile(), "failure trigger");
            JSONObject failure = new JSONObject();
            failure.put("selector_frames", names(rejected, "showMessageStr", "replyEnterStoryByEnding"));
            failure.put("selector_reason", BsonLite.stringValue(parameters(rejected, "showMessageStr"), "m"));
            failure.put("trigger_frames", names(trigger, "replyTriggerEventByEnding", "serverCallbackCarrier"));
            cases.put("failure", failure);

            fixture.closeGateway();
            Fixture reloaded = Fixture.attach(assets, fixture.root, ACCOUNT);
            try {
                byte[] reloadProfile = reloaded.snapshot();
                byte[] reloadWeeknum = BsonLite.documentValue(reloadProfile, "weeknum");
                check(countInt(reloadWeeknum, "w") == 2 && countInt(reloadWeeknum, "d") == 0, "reload week 2");
                check(committedId.equals(BsonLite.stringValue(BsonLite.documentValue(reloadProfile, "q7WeekTransition"), "id")),
                        "reload transition id");
                check(committedId.equals(reloaded.progress.weekCommit), "reload Progress identity");
                check(BsonLite.keys(BsonLite.documentValue(reloadProfile, "q7WeekResult")).isEmpty(), "reload result consumed");
                check(BsonLite.intArrayValues(BsonLite.documentValue(reloadProfile, "std"), "ed").equals(Collections.singletonList(7)),
                        "reload ending retained");
                check(BsonLite.intArrayValues(reloadProfile, "cgs").equals(Collections.singletonList(12)), "reload cg retained");
                List<ProtoLite.EntityMessage> reloadRepeat = reloaded.handoff(NEXT_ROUTE, 705);
                check(reloadRepeat.size() == 2, "reload replay frames");
                check(committedId.equals(BsonLite.stringValue(BsonLite.documentValue(reloaded.snapshot(), "q7WeekTransition"), "id")),
                        "reload replay keeps transition");
                List<ProtoLite.EntityMessage> reloadAvatar = reloaded.avatar();
                List<ProtoLite.EntityMessage> reloadAvatarAgain = reloaded.avatar();
                byte[] reloadWire = parameters(reloadAvatar, "updateClientAvatarReply");
                byte[] reloadWireAgain = parameters(reloadAvatarAgain, "updateClientAvatarReply");
                check(BsonLite.binaryValue(reloadWire, "s") != null && BsonLite.binaryValue(reloadWire, "s").length > 0,
                        "reload avatar payload");
                boolean reloadAvatarSame = Arrays.equals(reloadWire, reloadWireAgain);
                Inflater reloadInflater = new Inflater();
                reloadInflater.setInput(BsonLite.binaryValue(reloadWire, "s"));
                byte[] reloadDecoded = new byte[1 << 20];
                int reloadLength = reloadInflater.inflate(reloadDecoded);
                reloadInflater.end();
                check(reloadLength > 1024, "reload avatar payload");
                cases.put("reload", new JSONObject().put("week", countInt(reloadWeeknum, "w"))
                        .put("transition_id", committedId).put("avatar_identical", reloadAvatarSame)
                        .put("avatar_msgpack_bytes", reloadLength));
            } finally { reloaded.close(); }
        } finally {
            fixture.close();
        }
        cases.put("temp_removed", !Files.exists(fixture.root));
        Files.write(Paths.get(output), cases.toString(2).getBytes(StandardCharsets.UTF_8));
        System.out.println("PASS v63/f81b shared week settlement + successful ending handoff: "
                + "ending7/cg12/showWeekResult/addCg persisted; requestEnterStoryByEnding route2 committed; "
                + "zlib msgpack avatar; replay/reload keep the same committed week; wrong route and failure trigger typed false with no pollution");
    }
}
