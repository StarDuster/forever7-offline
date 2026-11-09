package com.project7.localmanager;

import android.content.Context;
import android.content.res.AssetManager;
import java.io.*;
import java.lang.reflect.*;
import java.net.InetAddress;
import java.net.ServerSocket;
import java.net.Socket;
import java.net.SocketTimeoutException;
import java.nio.ByteBuffer;
import java.nio.ByteOrder;
import java.nio.charset.StandardCharsets;
import java.nio.file.*;
import java.security.MessageDigest;
import java.util.*;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.TimeUnit;
import org.json.JSONArray;
import org.json.JSONObject;

/** Finite v65/f81b host for the legal week-2 handoff chain 534..539.
 *
 * Production classes are the published v65 OWN inputs; the manager is the
 * existing f81b translated-frame jar and the assets are the v65 stage assets.
 * This file only drives the real LocalWeekEngine settlement/handoff, real
 * Gateway startEvent/clientTraceProcessingEvent dispatches, and reads the real
 * LocalCityProgress status / BsonLite area-info + city-data projections.
 *
 * The same fixture also starts an ordinary loopback LocalGatewayServer with a
 * temp account store. A real client handshake (method 0/1/3) then sends
 * getAllAreaInfoRequest and reads the method 5 get_all_area_info_reply before
 * and after 534..539, storing the exact ais/cd/sm parameters as base64.
 * verify_route539.py builds the existing two-call InterfaceCallFix host copy of
 * the f81b manager jar in a temp dir; the raw jar remains the pinned input.
 *
 * No route value, 539 receipt, area1 state or city effect is pre-seeded.
 * No prepare, no production recompile, no D8/APK/native. */
public final class Route539EffectHost {
    static final String ACCOUNT = "host_route539_effect";
    static final int SOURCE_EVENT = 8028; // real released ending event
    static final int NEXT_ROUTE = 2;      // weeks.tsv route 2 -> event 534
    static final int[] CHAIN = {534, 535, 536, 537, 538, 539};

    static int checks;
    static void check(boolean value, String message) { checks++; if (!value) throw new AssertionError("FAIL: " + message); }
    static byte[] md5(String value) { return RequestEventCatalog.hash("MD5", value.getBytes(StandardCharsets.UTF_8)); }
    static String sha(byte[] bytes) { try { StringBuilder s = new StringBuilder(); for (byte b : MessageDigest.getInstance("SHA-256").digest(bytes)) s.append(String.format(Locale.ROOT, "%02x", b & 255)); return s.toString(); } catch (Exception e) { throw new IllegalStateException(e); } }
    static byte[] doc(byte[] profile, String key) { byte[] value = BsonLite.documentValue(profile, key); return value == null ? BsonLite.EMPTY_DOCUMENT : value; }
    static boolean receipt(byte[] profile, int event) { return Boolean.TRUE.equals(BsonLite.boolValue(doc(profile, "q7ChapterEffects"), Integer.toString(event))); }
    static boolean receiptKey(byte[] profile, int event) { return BsonLite.keys(doc(profile, "q7ChapterEffects")).contains(Integer.toString(event)); }

    static List<ProtoLite.EntityMessage> frames(byte[] wire) throws IOException {
        List<ProtoLite.EntityMessage> out = new ArrayList<>();
        ByteBuffer buffer = ByteBuffer.wrap(wire).order(ByteOrder.LITTLE_ENDIAN);
        while (buffer.hasRemaining()) {
            int length = buffer.getInt();
            check(buffer.getShort() == 5, "original opcode 5 frame");
            byte[] data = new byte[length - 2];
            buffer.get(data);
            out.add(ProtoLite.parseEntityMessage(data));
        }
        return out;
    }
    static String name(ProtoLite.EntityMessage frame, String... candidates) {
        for (String candidate : candidates) if (Arrays.equals(frame.methodMd5, md5(candidate))) return candidate;
        return "other:" + sha(frame.methodMd5).substring(0, 12);
    }
    static ProtoLite.EntityMessage one(List<ProtoLite.EntityMessage> frames, String method) {
        for (ProtoLite.EntityMessage frame : frames) if (Arrays.equals(frame.methodMd5, md5(method))) return frame;
        return null;
    }
    static int count(List<ProtoLite.EntityMessage> frames, String method) {
        int n = 0;
        for (ProtoLite.EntityMessage frame : frames) if (Arrays.equals(frame.methodMd5, md5(method))) n++;
        return n;
    }
    static JSONArray names(List<ProtoLite.EntityMessage> frames, String... candidates) {
        JSONArray out = new JSONArray();
        for (ProtoLite.EntityMessage frame : frames) out.put(name(frame, candidates));
        return out;
    }
    static int countInt(byte[] document, String key) {
        Integer value = BsonLite.intValue(document, key);
        check(value != null, "missing int " + key);
        return value.intValue();
    }
    static int infoStatus(byte[] reply) {
        byte[] area = doc(doc(reply, "ais"), "area_1");
        byte[] st = BsonLite.arrayValue(area, "st");
        if (st == null) return -1;
        Number value = BsonLite.numericValue(st, "0");
        return value == null ? -1 : value.intValue();
    }

    /** Ordinary client transport copied from DayRpcSocketHost.Wire: the same
     *  4-byte little-endian size + 2-byte method framing used by handleClient. */
    static final class Wire implements AutoCloseable {
        final Socket socket;
        final DataInputStream in;
        final OutputStream out;
        Wire(Socket connected) throws Exception {
            socket = connected;
            socket.setSoTimeout(20000);
            in = new DataInputStream(new BufferedInputStream(socket.getInputStream()));
            out = new BufferedOutputStream(socket.getOutputStream());
        }
        void write(int method, byte[] payload) throws Exception {
            int size = payload.length + 2;
            out.write(new byte[] {(byte) (size & 255), (byte) ((size >> 8) & 255),
                    (byte) ((size >> 16) & 255), (byte) ((size >> 24) & 255),
                    (byte) (method & 255), (byte) ((method >> 8) & 255)});
            out.write(payload);
            out.flush();
        }
        static final class Frame {
            final int method;
            final byte[] payload;
            Frame(int method, byte[] payload) { this.method = method; this.payload = payload; }
        }
        Frame read() throws IOException {
            int s0 = in.readUnsignedByte(), s1 = in.readUnsignedByte();
            int s2 = in.readUnsignedByte(), s3 = in.readUnsignedByte();
            int size = s0 | (s1 << 8) | (s2 << 16) | (s3 << 24);
            int method = in.readUnsignedByte() | (in.readUnsignedByte() << 8);
            byte[] payload = new byte[size - 2];
            in.readFully(payload);
            return new Frame(method, payload);
        }
        static final class Fields {
            final Map<Integer, byte[]> values = new LinkedHashMap<Integer, byte[]>();
            Fields(byte[] payload) throws IOException {
                int[] at = {0};
                while (at[0] < payload.length) {
                    int tag = varint(payload, at);
                    int field = tag >>> 3, wire = tag & 7;
                    if (wire != 2) throw new IOException("unexpected wire type " + wire);
                    int length = varint(payload, at);
                    if (length < 0 || at[0] + length > payload.length) throw new IOException("bad length");
                    values.put(field, Arrays.copyOfRange(payload, at[0], at[0] + length));
                    at[0] += length;
                }
            }
            static int varint(byte[] data, int[] at) throws IOException {
                int value = 0, shift = 0;
                while (true) {
                    if (at[0] >= data.length) throw new IOException("truncated varint");
                    int b = data[at[0]++] & 255;
                    value |= (b & 127) << shift;
                    if ((b & 128) == 0) return value;
                    shift += 7;
                }
            }
        }
        static byte[] nestedMd5(byte[] value) throws IOException {
            int[] at = {0};
            int tag = Fields.varint(value, at);
            if ((tag >>> 3) != 1 || (tag & 7) != 2) throw new IOException("nested md5 shape");
            int length = Fields.varint(value, at);
            return Arrays.copyOfRange(value, at[0], at[0] + length);
        }
        ProtoLite.EntityMessage untilEntityInfo(String className, long deadline) throws Exception {
            while (System.currentTimeMillis() < deadline) {
                socket.setSoTimeout((int)Math.max(1, deadline - System.currentTimeMillis()));
                Frame frame = read();
                if (frame.method != 3) continue;
                Fields fields = new Fields(frame.payload);
                if (!Arrays.equals(nestedMd5(fields.values.get(2)), md5(className))) continue;
                ProtoLite.EntityMessage message = new ProtoLite.EntityMessage();
                message.id = fields.values.get(3);
                message.parameters = fields.values.get(4);
                return message;
            }
            throw new AssertionError("timeout waiting for entity " + className);
        }
        ProtoLite.EntityMessage untilReply(String method, long deadline) throws Exception {
            long started=System.currentTimeMillis();int reads=0;
            while (System.currentTimeMillis() < deadline) {
                long remaining=deadline-System.currentTimeMillis();if(remaining<=0)break;
                socket.setSoTimeout((int)Math.min(remaining,10000));
                Frame frame;
                try { frame = read(); reads++; }
                catch (SocketTimeoutException timeout) { break; }
                if (frame.method != 5) continue;
                ProtoLite.EntityMessage message = ProtoLite.parseEntityMessage(frame.payload);
                if (Arrays.equals(message.methodMd5, md5(method))) {
                    System.out.println("AREA_CAPTURE reply="+method+" elapsedMs="+(System.currentTimeMillis()-started)+" remainingMs="+(deadline-System.currentTimeMillis())+" reads="+reads);
                    return message;
                }
            }
            throw new AssertionError("timeout waiting for reply " + method + " elapsedMs="+(System.currentTimeMillis()-started)+" remainingMs="+(deadline-System.currentTimeMillis())+" reads="+reads);
        }
        public void close() throws Exception { socket.close(); }
    }

    static final String BRIDGE_PASSWORD = "hostpass";

    static final class AreaReply {
        final byte[] parameters;
        final byte[] ais;
        final byte[] cd;
        final boolean sm;
        AreaReply(byte[] payload) throws IOException {
            parameters = payload;
            ais = BsonLite.documentValue(payload, "ais");
            cd = BsonLite.documentValue(payload, "cd");
            Boolean flag = BsonLite.boolValue(payload, "sm");
            check(ais != null, "area reply ais document");
            check(cd != null, "area reply cd document");
            check(flag != null, "area reply sm flag");
            sm = flag.booleanValue();
            check(BsonLite.keys(payload).equals(Arrays.asList("ais", "cd", "sm")),
                    "area reply parameter order " + BsonLite.keys(payload));
        }
        JSONObject json() throws Exception {
            return new JSONObject()
                    .put("source", "ordinary handleClient method 5 get_all_area_info_reply")
                    .put("parameters_b64", Base64.getEncoder().encodeToString(parameters))
                    .put("parameters_sha256", sha(parameters))
                    .put("parameters_bytes", parameters.length)
                    .put("ais_b64", Base64.getEncoder().encodeToString(ais))
                    .put("ais_sha256", sha(ais))
                    .put("cd_b64", Base64.getEncoder().encodeToString(cd))
                    .put("cd_sha256", sha(cd))
                    .put("sm", sm)
                    .put("area_1_st", infoStatus(parameters))
                    .put("keys", new JSONArray(BsonLite.keys(parameters)));
        }
    }

    static AreaReply socketAreaReply(int port, String account) throws Exception {
        Wire wire = new Wire(new Socket("127.0.0.1", port));
        try {
            long started=System.currentTimeMillis();
            long accountDeadline=started+10000;wire.socket.setSoTimeout(10000);
            wire.write(0, new byte[0]);
            ProtoLite.EntityMessage accountInfo = wire.untilEntityInfo("ClientAccount", accountDeadline);
            check(accountInfo.id != null, "bridge account identity");
            System.out.println("AREA_CAPTURE account elapsedMs="+(System.currentTimeMillis()-started));
            long avatarDeadline=System.currentTimeMillis()+10000;wire.socket.setSoTimeout(10000);
            wire.write(1, ProtoLite.entityMessage(accountInfo.id, md5("login"),
                    BsonLite.document("name", account, "psw", BRIDGE_PASSWORD)));
            ProtoLite.EntityMessage avatar = wire.untilEntityInfo("ClientAvatar", avatarDeadline);
            check(avatar.id != null, "bridge avatar identity");
            System.out.println("AREA_CAPTURE avatar elapsedMs="+(System.currentTimeMillis()-started));
            long areaDeadline=System.currentTimeMillis()+10000;wire.socket.setSoTimeout(10000);
            wire.write(1, ProtoLite.entityMessage(avatar.id, md5("getAllAreaInfoRequest"),
                    BsonLite.EMPTY_DOCUMENT));
            ProtoLite.EntityMessage reply = wire.untilReply("get_all_area_info_reply", areaDeadline);
            check(Arrays.equals(reply.id, avatar.id), "area reply addressed to avatar");
            return new AreaReply(reply.parameters);
        } finally {
            wire.close();
        }
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
        LocalAccountStore accounts;
        int port;
        Thread server;
        CountDownLatch listening;
        boolean gatewayClosed;

        Fixture(Path root, String account) { this.root = root; this.account = account; this.file = root.resolve("profiles/" + account + ".bson").toFile(); }

        static Fixture create(File assets, String account) throws Exception {
            Path root = Files.createTempDirectory("route539-effect-");
            Files.createDirectories(root.resolve("profiles"));
            Fixture fixture = new Fixture(root, account);
            fixture.prepareAssets(assets);
            byte[] raw = BsonLite.withAccountIdentity(Files.readAllBytes(new File(assets, "new_player.bson").toPath()), account, 900539);
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
            progress.weekCommit = "host_route539_source";
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
            fixture.accounts = new LocalAccountStore(new File(root.toFile(), "accounts.properties"));
            fixture.accounts.registerOne(account, BRIDGE_PASSWORD);
            try (ServerSocket probe = new ServerSocket(0, 1, InetAddress.getByName("127.0.0.1"))) {
                fixture.port = probe.getLocalPort();
            }
            fixture.listening = new CountDownLatch(1);
            fixture.gateway = new LocalGatewayServer(fixture.port, fixture.accounts, fixture.store,
                    fixture.tutorials, fixture.graph, fixture.newbees, null, null,
                    new LocalGatewayServer.StatusListener() {
                        public void onStatus(boolean success, String message) {
                            if (success) fixture.listening.countDown();
                        }
                    });
            fixture.server = new Thread(fixture.gateway, "p7-route539-bridge-" + account);
            fixture.server.setDaemon(true);
            fixture.server.start();
            check(fixture.listening.await(10, TimeUnit.SECONDS), "ordinary bridge listening " + account);
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

        void completeSourceEvent() throws IOException {
            progress.completedEvents.add(SOURCE_EVENT);
            tutorials.save(account, progress);
        }

        List<ProtoLite.EntityMessage> settle() throws Exception {
            Method method = LocalGatewayServer.class.getDeclaredMethod("syncEventEffects", OutputStream.class,
                    byte[].class, String.class, LocalTutorialStore.Progress.class, LocalEventEngine.class);
            method.setAccessible(true);
            ByteArrayOutputStream out = new ByteArrayOutputStream();
            method.invoke(gateway, out, new byte[12], account, progress, engine);
            return frames(out.toByteArray());
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
            check(weekRpc(out, "requestEnterStoryByEnding", BsonLite.document("i", route, "_cbid_", callback)),
                    "week RPC consumed");
            return frames(out.toByteArray());
        }

        List<ProtoLite.EntityMessage> reliable(String method, byte[] params, int sequence) throws Exception {
            Method rpc = LocalGatewayServer.class.getDeclaredMethod("handleReliableRpc", OutputStream.class,
                    byte[].class, byte[].class, String.class, LocalTutorialStore.Progress.class,
                    LocalEventEngine.class, Set.class, Set.class, Map.class, Set.class);
            rpc.setAccessible(true);
            ByteArrayOutputStream out = new ByteArrayOutputStream();
            byte[] envelope = BsonLite.document("w",
                    BsonLite.document("m", method, "p", params, "r", sequence), "_cbid_", sequence + 10000);
            rpc.invoke(gateway, out, new byte[12], envelope, account, progress, engine,
                    new HashSet<Integer>(), new HashSet<Integer>(),
                    new HashMap<Integer, LocalPatrolEngine.Result>(), new HashSet<Integer>());
            return frames(out.toByteArray());
        }

        List<ProtoLite.EntityMessage> start(int event, int sequence) throws Exception {
            return reliable("startEvent", BsonLite.document("e", event), sequence);
        }

        List<ProtoLite.EntityMessage> dialog(int event, int sequence) throws Exception {
            return reliable("clientTraceProcessingEvent",
                    BsonLite.document("k", "dialog", "d", BsonLite.document("c", event)), sequence);
        }

        void waitBridgeIdle() throws Exception {
            Field clientsField = LocalGatewayServer.class.getDeclaredField("clients");
            clientsField.setAccessible(true);
            Object clients = clientsField.get(gateway);
            check(clients instanceof java.util.Collection, "ordinary bridge clients ABI");
            long deadline = System.currentTimeMillis() + 5000;
            while (clients instanceof java.util.Collection && !((java.util.Collection<?>) clients).isEmpty()
                    && System.currentTimeMillis() < deadline) Thread.sleep(20);
            check(!(clients instanceof java.util.Collection) || ((java.util.Collection<?>) clients).isEmpty(),
                    "ordinary bridge session did not close");
        }
        JSONObject captureAreaReply() throws Exception {
            tutorials.save(account, progress);
            byte[] beforeProfile = profile();
            JSONObject reply;
            try { reply = socketAreaReply(port, account).json(); }
            catch (Exception | AssertionError error) {
                StringBuilder detail = new StringBuilder("route539 socket capture failure\n")
                        .append("error=").append(error).append('\n')
                        .append("account=").append(account).append('\n')
                        .append("profile_sha256=").append(sha(beforeProfile)).append('\n');
                try { Field f = LocalGatewayServer.class.getDeclaredField("clients"); f.setAccessible(true);
                    detail.append("clients=").append(f.get(gateway)).append('\n'); } catch (Throwable ignored) {}
                try { Files.write(Paths.get("reports/project7-route539-socket-failure.txt"), detail.toString().getBytes(java.nio.charset.StandardCharsets.UTF_8)); } catch (Throwable ignored) {}
                throw error;
            }
            waitBridgeIdle();
            byte[] afterProfile = profile();
            reply.put("profile_changed_by_login", !Arrays.equals(beforeProfile, afterProfile));
            reply.put("profile_sha256_before", sha(beforeProfile));
            reply.put("profile_sha256_after", sha(afterProfile));
            tutorials.save(account, progress);
            return reply;
        }

        void closeGateway() {
            if (!gatewayClosed) {
                gateway.close();
                gatewayClosed = true;
                if (server != null) {
                    try { server.join(5000); }
                    catch (InterruptedException interrupted) { Thread.currentThread().interrupt(); }
                }
            }
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

    static int status(Fixture f) throws IOException { return LocalCityProgress.status(f.progress, 1, f.profile()); }
    static int policyStatus(Fixture f) throws IOException { return StoryCityPolicy.status(f.progress, 1, f.profile()); }
    static boolean highSchool(LocalTutorialStore.Progress progress) {
        try {
            Method method = LocalGatewayServer.class.getDeclaredMethod("isHighSchoolUnlocked", LocalTutorialStore.Progress.class);
            method.setAccessible(true);
            return Boolean.TRUE.equals(method.invoke(null, progress));
        } catch (Exception error) { throw new IllegalStateException(error); }
    }
    static int info(Fixture f) throws IOException { return infoStatus(BsonLite.allAreaInfoReplyDocument(highSchool(f.progress), f.progress, f.profile())); }
    static byte[] cityData(Fixture f) throws IOException { return BsonLite.cityDataReplyDocument(f.progress, f.profile()); }
    static String cityKey(Fixture f) throws IOException { return sha(BsonLite.withoutProfileKey(doc(cityData(f), "cd"), "jpvt")); }
    static int cityJpvt(Fixture f) throws IOException { Integer v = BsonLite.intValue(doc(cityData(f), "cd"), "jpvt"); return v == null ? -1 : v.intValue(); }

    static boolean chapterActive(byte[] profile) {
        try {
            Method method = LocalChapterCityEngine.class.getDeclaredMethod("active", byte[].class);
            method.setAccessible(true);
            return Boolean.TRUE.equals(method.invoke(null, profile));
        } catch (Exception error) { throw new IllegalStateException(error); }
    }

    static Map<String, Object> state(Fixture f) throws Exception {
        byte[] profile = f.profile();
        Map<String, Object> out = new LinkedHashMap<>();
        out.put("std_rt", BsonLite.stringValue(doc(profile, "std"), "rt"));
        out.put("chapter_menu", BsonLite.intValue(profile, "q7ChapterMenu"));
        out.put("route_event_539", BsonLite.boolValue(doc(profile, "q7routeEvents"), "539"));
        out.put("chapter_receipt_539", receipt(profile, 539));
        out.put("chapter_receipt_key_539", receiptKey(profile, 539));
        out.put("chapter_effect_keys", new JSONArray(BsonLite.keys(doc(profile, "q7ChapterEffects"))));
        out.put("chapter_state_keys", new JSONArray(BsonLite.keys(doc(profile, "q7ChapterStates"))));
        out.put("chapter_state_1", BsonLite.intValue(doc(profile, "q7ChapterStates"), "1"));
        out.put("chapter_lock_1", BsonLite.boolValue(doc(profile, "q7ChapterLocks"), "1"));
        out.put("high_school_unlocked", highSchool(f.progress));
        out.put("city_status", status(f));
        out.put("story_city_status", policyStatus(f));
        out.put("all_area_info_status", info(f));
        out.put("city_data_sha256", cityKey(f));
        out.put("city_data_jpvt", cityJpvt(f));
        out.put("city_data_keys", new JSONArray(BsonLite.keys(doc(cityData(f), "cd"))));
        out.put("story_city_owns", StoryCityPolicy.owns(profile));
        out.put("chapter_city_active", chapterActive(profile));
        out.put("completed_539", f.progress.completedEvents.contains(539));
        out.put("completed_1043", f.progress.completedEvents.contains(1043));
        out.put("completed_1004", f.progress.completedEvents.contains(1004));
        out.put("available_events", new JSONArray(new TreeSet<>(f.progress.availableEvents)).toString());
        return out;
    }

    static JSONObject json(Map<String, Object> values) {
        JSONObject out = new JSONObject();
        for (Map.Entry<String, Object> entry : values.entrySet()) out.put(entry.getKey(), entry.getValue() == null ? JSONObject.NULL : entry.getValue());
        return out;
    }

    static void addFoundation(LocalTutorialStore.Progress progress, String mode) {
        if (mode.equals("1043")) progress.completedEvents.addAll(Arrays.asList(1004, 1013, 1043));
        else if (mode.equals("1004")) progress.completedEvents.add(1004);
        else if (!mode.equals("none")) throw new IllegalArgumentException(mode);
    }

    static JSONObject runScenario(File assets, String foundation, LocalWeekCatalog weeks, boolean candidate) throws Exception {
        Fixture fixture = Fixture.create(assets, ACCOUNT + "_" + foundation.toLowerCase(Locale.ROOT));
        JSONObject out = new JSONObject();
        try {
            byte[] beforeSettlement = fixture.profile();
            fixture.completeSourceEvent();
            List<ProtoLite.EntityMessage> settled = fixture.settle();
            check(count(settled, "showWeekResult") == 1, foundation + ": settlement notice");
            check(countInt(parameters(settled, "showWeekResult"), "r") == 7,
                    foundation + ": earned ending 7");
            check(BsonLite.intArrayValues(BsonLite.documentValue(fixture.snapshot(), "std"), "ed")
                    .equals(Collections.singletonList(7)), foundation + ": persisted ending");
            out.put("settlement_frames", names(settled, "showWeekResult", "addCg", "syncWeeknumScoreInfo", "updateStoryFlag"));
            out.put("settled_profile_changed", !Arrays.equals(beforeSettlement, fixture.snapshot()));

            addFoundation(fixture.progress, foundation);
            fixture.tutorials.save(fixture.account, fixture.progress);
            List<ProtoLite.EntityMessage> handoff = fixture.handoff(NEXT_ROUTE, 701);
            check(name(handoff.get(0), "replyEnterStoryByEnding").equals("replyEnterStoryByEnding"),
                    foundation + ": selector reply");
            check(Boolean.TRUE.equals(BsonLite.boolValue(parameters(handoff, "replyEnterStoryByEnding"), "r")),
                    foundation + ": route 2 accepted");
            check(fixture.progress.availableEvents.contains(534), foundation + ": 534 available");
            check(fixture.progress.weekIndex == 2, foundation + ": week 2 progress");
            fixture.engine.refreshProfile(fixture.profile());
            JSONObject areaReply = new JSONObject();
            JSONObject beforeArea = fixture.captureAreaReply();
            areaReply.put("before", beforeArea);
            fixture.engine.refreshProfile(fixture.profile());

            Map<String, Object> before = state(fixture);
            out.put("before_chain", json(before));
            check(Integer.valueOf((Integer) before.get("all_area_info_status")).equals(beforeArea.getInt("area_1_st")),
                    foundation + ": ordinary before area_1 status matches host projection");
            out.put("handoff_frames", names(handoff, "replyEnterStoryByEnding", "handleIncWeekReply", "showMessageStr"));
            check("1".equals(before.get("std_rt")), foundation + ": legal pre-entry route base 1");
            check(Integer.valueOf(2).equals(before.get("chapter_menu")), foundation + ": menu selector 2");
            check(!Boolean.TRUE.equals(before.get("chapter_receipt_539")), foundation + ": no 539 receipt before chain");
            check(before.get("chapter_state_1") == null, foundation + ": no area1 state before chain");

            JSONArray chain = new JSONArray();
            ProtoLite.EntityMessage sync539 = null;
            int sequence = 1000;
            for (int event : CHAIN) {
                List<ProtoLite.EntityMessage> started = fixture.start(event, sequence++);
                ProtoLite.EntityMessage accept = one(started, "startEventReply");
                check(accept != null && Integer.valueOf(1).equals(BsonLite.intValue(accept.parameters, "r")),
                        foundation + ": start accepted " + event);
                check(fixture.progress.processingEvents.contains(event), foundation + ": processing " + event);
                List<ProtoLite.EntityMessage> trace = fixture.dialog(event, sequence++);
                ProtoLite.EntityMessage done = one(trace, "completeEventReplyEnd");
                check(done != null && Integer.valueOf(event).equals(BsonLite.intValue(done.parameters, "e")),
                        foundation + ": dialog completed " + event);
                check(fixture.progress.completedEvents.contains(event), foundation + ": completed set " + event);
                check(!fixture.progress.processingEvents.contains(event), foundation + ": processing cleared " + event);
                JSONObject step = new JSONObject();
                step.put("event", event);
                step.put("start_frames", names(started, "startEventReply", "reliableRpcAck", "pushEvents", "serverCallbackCarrier"));
                step.put("trace_frames", names(trace, "completeEventReplyEnd", "completeEventReplyStart",
                        "reliableRpcAck", "syncRoute", "get_all_area_info_reply", "pushEvents", "putEvents"));
                step.put("sync_route", count(trace, "syncRoute"));
                chain.put(step);
                if (event == 539) sync539 = one(trace, "syncRoute");
            }
            out.put("chain", chain);

            JSONObject afterArea = fixture.captureAreaReply();
            areaReply.put("after", afterArea);
            areaReply.put("fixture", foundation);
            out.put("area_reply", areaReply);
            fixture.engine.refreshProfile(fixture.profile());
            Map<String, Object> afterChain = state(fixture);
            out.put("after_chain", json(afterChain));
            check(Integer.valueOf((Integer) afterChain.get("all_area_info_status")).equals(afterArea.getInt("area_1_st")),
                    foundation + ": ordinary after area_1 status matches host projection");
            int jpvtDelta = ((Integer) afterChain.get("city_data_jpvt")) - ((Integer) before.get("city_data_jpvt"));
            out.put("city_data_jpvt_delta", jpvtDelta);
            check("4-1".equals(afterChain.get("std_rt")), foundation + ": 539 writes std.rt 4-1");
            check(Boolean.TRUE.equals(afterChain.get("route_event_539")), foundation + ": 539 route ledger");
            check(sync539 != null, foundation + ": real syncRoute after 539");
            byte[] syncDoc = sync539.parameters;
            check("4-1".equals(BsonLite.stringValue(syncDoc, "rt")), foundation + ": syncRoute rt 4-1");
            out.put("sync_route_parameters", new JSONObject()
                    .put("keys", new JSONArray(BsonLite.keys(syncDoc)))
                    .put("rt", BsonLite.stringValue(syncDoc, "rt"))
                    .put("sha256", sha(syncDoc)));
            Map<String, Object> after = afterChain;
            if (candidate) {
                check(Boolean.TRUE.equals(afterChain.get("chapter_receipt_539")), foundation + ": candidate gateway receipt true");
                check(Boolean.TRUE.equals(afterChain.get("chapter_receipt_key_539")), foundation + ": candidate gateway receipt key");
                check(Integer.valueOf(0).equals(afterChain.get("chapter_state_1")), foundation + ": candidate gateway area1 state 0");
                check(Integer.valueOf(0).equals(afterChain.get("city_status")), foundation + ": candidate gateway area1 status 0");
                check(Integer.valueOf(0).equals(afterChain.get("story_city_status")), foundation + ": candidate gateway story-city status 0");
                check(Boolean.TRUE.equals(afterChain.get("story_city_owns")), foundation + ": candidate gateway owns unclaimed menu2");
                check(!Boolean.TRUE.equals(afterChain.get("chapter_city_active")), foundation + ": chapter city still inactive");
                out.put("candidate_effect_applied_by_gateway", true);
                out.put("candidate_regressions", candidateRegressions(fixture));
                fixture.engine.refreshProfile(fixture.profile());
                List<ProtoLite.EntityMessage> duplicateFrames = fixture.settle();
                Map<String, Object> duplicateState = state(fixture);
                check(business(after).toString().equals(business(duplicateState).toString()),
                        foundation + ": duplicate gateway effect pass leaves business state unchanged");
                out.put("candidate_duplicate_frames", names(duplicateFrames, "get_all_area_info_reply", "syncRoute", "showWeekResult"));
                out.put("candidate_duplicate_unchanged", true);
                out.put("area1_effect_applied", true);
                out.put("effect_observable", false);
            } else {
                check(!Boolean.TRUE.equals(afterChain.get("chapter_receipt_539")), foundation + ": 539 city receipt false before seam");
                check(!Boolean.TRUE.equals(afterChain.get("chapter_receipt_key_539")), foundation + ": 539 city receipt absent before seam");
                check(afterChain.get("chapter_state_1") == null, foundation + ": 539 areaFree state absent before seam");
                check(!Boolean.TRUE.equals(afterChain.get("story_city_owns")), foundation + ": baseline menu2/rt4-1 not in shared city scope");
                check(!Boolean.TRUE.equals(afterChain.get("chapter_city_active")), foundation + ": chapter city inactive at menu2/rt4-1");
                if (foundation.equals("1043")) {
                    check(Integer.valueOf(0).equals(before.get("city_status")) && Integer.valueOf(0).equals(after.get("city_status")),
                            "1043: area1 status free before and after 539");
                    check(Integer.valueOf(0).equals(before.get("all_area_info_status")) &&
                            Integer.valueOf(0).equals(after.get("all_area_info_status")),
                            "1043: actual area info status free before and after 539");
                    check(before.get("city_data_sha256").equals(after.get("city_data_sha256")),
                            "1043: get_city_data projection unchanged except stock jpvt");
                    check(jpvtDelta >= 0 && jpvtDelta <= 2, "1043: stock jpvt bounded " + jpvtDelta);
                    out.put("effect_observable", false);
                } else if (foundation.equals("1004")) {
                    check(Integer.valueOf(1).equals(before.get("city_status")) && Integer.valueOf(1).equals(after.get("city_status")),
                            "1004-only: area1 stays FIGHT; 539 effect would have freed it");
                    out.put("effect_observable", true);
                    out.put("control_only", true);
                } else {
                    check(Objects.equals(before.get("city_status"), after.get("city_status")),
                            "none: bare-handoff area1 status stable before=" + before.get("city_status") + " after=" + after.get("city_status"));
                    check(Integer.valueOf(2).equals(after.get("city_status")),
                            "none: bare handoff leaves area1 status 2 (not free)");
                    out.put("effect_observable", true);
                    out.put("bare_handoff", true);
                }
                out.put("area1_effect_applied", false);
            }

            // The ownership seam itself: baseline delegates to the inactive chapter
            // engine; the candidate owns menu2 and is receipt-idempotent.
            byte[] seamBefore = fixture.profile();
            LocalResourceEngine.Result seam = new LocalResourceEngine.Result(seamBefore);
            StoryCityPolicy.refresh(seam, fixture.graph, fixture.progress);
            check(Arrays.equals(seamBefore, seam.profile), foundation + ": shared seam is receipt-idempotent");
            out.put("seam_profile_unchanged", true);
            out.put("seam_frames", seam.replies.size());

            // Save/reload through the real Store + tutorial Properties.
            fixture.closeGateway();
            Fixture reloaded = Fixture.attach(assets, fixture.root, fixture.account);
            JSONObject reload = new JSONObject();
            byte[] persistedProfile = null;
            try {
                Map<String, Object> reloadedState = state(reloaded);
                reload.put("state", json(reloadedState));
                check(reloaded.progress.completedEvents.contains(539), foundation + ": reload keeps 539 completion");
                check("4-1".equals(BsonLite.stringValue(doc(reloaded.profile(), "std"), "rt")),
                        foundation + ": reload keeps std.rt 4-1");
                check(reloadedState.get("city_status").equals(after.get("city_status")),
                        foundation + ": reload area1 status stable");
                if (candidate) {
                    check(Boolean.TRUE.equals(reloadedState.get("chapter_receipt_539")) &&
                            Integer.valueOf(0).equals(reloadedState.get("chapter_state_1")),
                            foundation + ": reload keeps candidate receipt/state");
                    reloaded.engine.refreshProfile(reloaded.profile());
                    List<ProtoLite.EntityMessage> reloadFrames = reloaded.settle();
                    Map<String, Object> reloadApplied = state(reloaded);
                    check(business(reloadedState).toString().equals(business(reloadApplied).toString()),
                            foundation + ": reload gateway effect pass is idempotent");
                    reload.put("candidate_reload_frames", names(reloadFrames, "get_all_area_info_reply", "syncRoute", "showWeekResult"));
                    reload.put("candidate_reload_unchanged", true);
                } else {
                    check(!Boolean.TRUE.equals(reloadedState.get("chapter_receipt_539")) &&
                            reloadedState.get("chapter_state_1") == null, foundation + ": reload keeps effect absent");
                }
                reload.put("event_completions_539", reloaded.progress.eventCompletions.get(539));

                // Replay after reload: original Gateway must not duplicate the completion
                // or route sync; the candidate must not duplicate the city effect.
                reloaded.snapshot();
                Map<String, Object> replayBefore = state(reloaded);
                int replaySequence = 3000;
                List<ProtoLite.EntityMessage> replayStart = reloaded.start(539, replaySequence++);
                List<ProtoLite.EntityMessage> replayTrace = reloaded.dialog(539, replaySequence++);
                JSONArray replayCandidate = new JSONArray();
                if (candidate) {
                    reloaded.engine.refreshProfile(reloaded.profile());
                    for (ProtoLite.EntityMessage frame : reloaded.settle())
                        replayCandidate.put(name(frame, "get_all_area_info_reply", "syncRoute", "showWeekResult"));
                }
                reloaded.snapshot();
                Map<String, Object> replayState = state(reloaded);
                JSONObject replayBeforeJson = json(replayBefore), replayAfterJson = json(replayState);
                replayBeforeJson.remove("city_data_jpvt");
                replayAfterJson.remove("city_data_jpvt");
                check(replayBeforeJson.toString().equals(replayAfterJson.toString()),
                        foundation + ": replay leaves all business documents unchanged");
                check(replayState.get("city_status").equals(after.get("city_status")),
                        foundation + ": replay area1 status stable");
                check(reloaded.progress.eventCompletions.get(539) == null || reloaded.progress.eventCompletions.get(539) == 1,
                        foundation + ": replay completion count <= 1");
                reload.put("replay_frames", names(replayTrace, "completeEventReplyEnd", "syncRoute", "showMessageStr"));
                reload.put("replay_sync_route", count(replayTrace, "syncRoute"));
                reload.put("replay_state", json(replayState));
                reload.put("replay_business_unchanged", true);
                if (candidate) {
                    check(Boolean.TRUE.equals(replayState.get("chapter_receipt_539")) &&
                            Integer.valueOf(0).equals(replayState.get("chapter_state_1")),
                            foundation + ": replay keeps candidate receipt/state");
                    reload.put("candidate_replay_replies", replayCandidate);
                }
                check(count(replayTrace, "syncRoute") == 0, foundation + ": replay emits no second syncRoute");
                persistedProfile = reloaded.profile();
            } finally {
                reloaded.close();
            }
            out.put("reload", reload);
            fixture.closeGateway();

            // resetProgress / 1043 equivalence, using the original private methods
            // exactly like EventResetWeekPolicy.
            Method reset = LocalWeekEngine.class.getDeclaredMethod("resetProgress",
                    LocalTutorialStore.Progress.class, LocalWeekCatalog.class, int.class, int.class);
            reset.setAccessible(true);
            Integer entrance = weeks.entrances.get(NEXT_ROUTE);
            check(entrance != null && entrance.intValue() == 534, foundation + ": route2 entrance 534");
            LocalTutorialStore.Progress next = (LocalTutorialStore.Progress) reset.invoke(null,
                    fixture.progress, weeks, 3, entrance);
            Method resetProfile = LocalWeekEngine.class.getDeclaredMethod("resetProfile",
                    byte[].class, LocalTutorialStore.Progress.class, int.class, LocalWeekCatalog.class);
            resetProfile.setAccessible(true);
            byte[] nextProfile = (byte[]) resetProfile.invoke(null, persistedProfile, next, NEXT_ROUTE, weeks);
            JSONObject resetOut = new JSONObject();
            resetOut.put("completed_1004", next.completedEvents.contains(1004));
            resetOut.put("completed_1013", next.completedEvents.contains(1013));
            resetOut.put("completed_1043", next.completedEvents.contains(1043));
            resetOut.put("completed_539", next.completedEvents.contains(539));
            resetOut.put("week_index", next.weekIndex);
            resetOut.put("available_534", next.availableEvents.contains(534));
            resetOut.put("status_area1", LocalCityProgress.status(next, 1, nextProfile));
            resetOut.put("chapter_state_1", BsonLite.intValue(doc(nextProfile, "q7ChapterStates"), "1"));
            check(!next.completedEvents.contains(539), foundation + ": resetProgress never retains 539");
            if (foundation.equals("1043")) {
                check(next.completedEvents.contains(1043), foundation + ": resetProgress retains 1043 foundation");
                check(Integer.valueOf(0).equals(resetOut.get("status_area1")),
                        "1043: next week area1 remains free without 539 replay");
            }
            out.put("reset_progress", resetOut);
            Object foundationField = LocalWeekEngine.class.getDeclaredField("TUTORIAL_FOUNDATION");
            ((Field) foundationField).setAccessible(true);
            Object typed = ((Field) foundationField).get(null);
            out.put("tutorial_foundation", typed);
            check(((Collection<?>) typed).contains(1043), foundation + ": 1043 in original foundation");
            check(!((Collection<?>) typed).contains(539), foundation + ": 539 not in original foundation");
            check(!weeks.stay.contains(539), foundation + ": 539 not in weeks stay");
        } finally {
            fixture.close();
        }
        return out;
    }

    static JSONObject candidateRegressions(Fixture fixture) throws Exception {
        JSONObject out = new JSONObject();
        byte[] transition = BsonLite.document("id", "candidate-regression");
        byte[] menu2 = BsonLite.document("q7ChapterMenu", 2, "std", BsonLite.document("rt", "4-1"),
                "q7WeekTransition", transition);
        byte[] menu2NoTransition = BsonLite.withoutProfileKey(menu2, "q7WeekTransition");
        byte[] menu3 = BsonLite.document("q7ChapterMenu", 3, "std", BsonLite.document("rt", "4-1"),
                "q7WeekTransition", transition);
        byte[] legacy = BsonLite.document("q7ChapterMenu", 11, "std", BsonLite.document("rt", "12"),
                "q7WeekTransition", transition);
        byte[] menu25 = BsonLite.document("q7ChapterMenu", 25, "std", BsonLite.document("rt", "27-1"),
                "q7WeekTransition", transition);
        byte[] menu4 = BsonLite.document("q7ChapterMenu", 4, "std", BsonLite.document("rt", "4-1"),
                "q7WeekTransition", transition, "q7AnCityLocks", BsonLite.document("2", true),
                "q7WeekEventBaseline", BsonLite.EMPTY_DOCUMENT);
        byte[] menu4NoTransition = BsonLite.withoutProfileKey(menu4, "q7WeekTransition");
        byte[] menu2AnLock = BsonLite.document("q7ChapterMenu", 2, "std", BsonLite.document("rt", "4-1"),
                "q7WeekTransition", transition, "q7AnCityLocks", BsonLite.document("2", true),
                "q7WeekEventBaseline", BsonLite.EMPTY_DOCUMENT);
        out.put("menu2_transition_owns", StoryCityPolicy.owns(menu2));
        out.put("menu2_no_transition_owns", StoryCityPolicy.owns(menu2NoTransition));
        out.put("menu3_transition_owns", StoryCityPolicy.owns(menu3));
        out.put("legacy_transition_owns", StoryCityPolicy.owns(legacy));
        out.put("menu25_transition_owns", StoryCityPolicy.owns(menu25));
        out.put("menu4_dedicated_owns", StoryCityPolicy.owns(menu4));
        out.put("menu4_no_transition_owns", StoryCityPolicy.owns(menu4NoTransition));
        out.put("menu4_an_active", LocalAnCityEngine.active(menu4));
        out.put("menu4_an_locked", LocalAnCityEngine.locked(menu4, 2));
        out.put("menu4_shared_locked", StoryCityPolicy.locked(menu4, 2));
        LocalTutorialStore.Progress probe = LocalTutorialStore.Progress.fresh();
        probe.weekCommit = "candidate-regression-week";
        probe.completedEvents.add(7044);
        LocalResourceEngine.Result refreshed = new LocalResourceEngine.Result(menu2AnLock);
        StoryCityPolicy.refresh(refreshed, fixture.graph, probe);
        out.put("menu2_7044_an_locked", LocalAnCityEngine.locked(refreshed.profile, 2));
        out.put("menu2_7044_shared_locked", StoryCityPolicy.locked(refreshed.profile, 2));
        out.put("menu2_7044_an_lock_preserved",
                Boolean.TRUE.equals(BsonLite.boolValue(doc(refreshed.profile, "q7AnCityLocks"), "2")));
        out.put("menu2_7044_chapter_lock_written", BsonLite.keys(doc(refreshed.profile, "q7ChapterLocks")).contains("2"));
        out.put("menu2_7044_chapter_lock_keys", new JSONArray(BsonLite.keys(doc(refreshed.profile, "q7ChapterLocks"))));
        out.put("menu2_7044_receipt_keys", new JSONArray(BsonLite.keys(doc(refreshed.profile, "q7ChapterEffects"))));
        out.put("menu2_7044_receipt_written", receiptKey(refreshed.profile, 7044));
        check(Boolean.TRUE.equals(out.get("menu2_transition_owns")), "candidate regression: menu2 opt-in");
        check(Boolean.FALSE.equals(out.get("menu2_no_transition_owns")), "candidate regression: transition required");
        check(Boolean.FALSE.equals(out.get("menu3_transition_owns")), "candidate regression: menu3 not generalized");
        check(Boolean.FALSE.equals(out.get("legacy_transition_owns")), "candidate regression: legacy route untouched");
        check(Boolean.TRUE.equals(out.get("menu25_transition_owns")), "candidate regression: menu25 dedicated owner");
        check(Boolean.TRUE.equals(out.get("menu4_dedicated_owns")), "candidate regression: menu4 dedicated owner");
        check(Boolean.FALSE.equals(out.get("menu4_no_transition_owns")), "candidate regression: menu4 no transition");
        check(Boolean.TRUE.equals(out.get("menu4_an_active")) && Boolean.TRUE.equals(out.get("menu4_an_locked")),
                "candidate regression: AN dedicated lock visible");
        check(Boolean.TRUE.equals(out.get("menu4_shared_locked")), "candidate regression: AN lock preserved in shared lock");
        check(Boolean.TRUE.equals(out.get("menu2_7044_an_locked")), "candidate regression: AN lock preserved");
        check(Boolean.TRUE.equals(out.get("menu2_7044_shared_locked")), "candidate regression: AN lock preserved in shared lock");
        check(Boolean.TRUE.equals(out.get("menu2_7044_an_lock_preserved")), "candidate regression: q7AnCityLocks unchanged");
        check(Boolean.FALSE.equals(out.get("menu2_7044_chapter_lock_written")), "candidate regression: AN event not adopted");
        check(((JSONArray) out.get("menu2_7044_chapter_lock_keys")).length() == 0, "candidate regression: no chapter locks from AN event");
        check(((JSONArray) out.get("menu2_7044_receipt_keys")).length() == 0, "candidate regression: no receipts from AN event");
        check(Boolean.FALSE.equals(out.get("menu2_7044_receipt_written")), "candidate regression: AN receipt not adopted");
        return out;
    }

    static JSONObject business(Map<String, Object> state) {
        JSONObject out = json(state);
        out.remove("city_data_jpvt");
        return out;
    }

    static byte[] parameters(List<ProtoLite.EntityMessage> frames, String method) {
        ProtoLite.EntityMessage frame = one(frames, method);
        check(frame != null, "missing frame " + method);
        return frame.parameters;
    }

    public static void main(String[] args) throws Exception {
        File assets = new File(args[0]);
        String output = args[1];
        byte[] prePareProbe = BsonLite.document("q7ChapterMenu", 2,
                "q7WeekTransition", BsonLite.document("id", "probe"),
                "std", BsonLite.document("rt", "4-1"));
        check(!StoryCityPolicy.owns(prePareProbe), "owns false before prepare");
        LocalStoryEnvironment.Scope environment = LocalStoryEnvironment.fixture(20261105L, 1762348800000L);
        LocalWeekCatalog weeks = new LocalWeekCatalog(new FileInputStream(new File(assets, "weeks.tsv")));
        boolean candidate = args.length > 2 && args[2].equals("candidate");
        JSONObject cases = new JSONObject();
        try {
            cases.put("foundation_1043", runScenario(assets, "1043", weeks, candidate));
            cases.put("foundation_none", runScenario(assets, "none", weeks, candidate));
            cases.put("control_1004_only", runScenario(assets, "1004", weeks, candidate));
            JSONObject facts = new JSONObject();
            facts.put("account", ACCOUNT);
            facts.put("source_event", SOURCE_EVENT);
            facts.put("next_route", NEXT_ROUTE);
            facts.put("chain", new JSONArray(CHAIN));
            JSONObject seeds = new JSONObject();
            seeds.put("foundation_1043", new JSONArray(Arrays.asList(1004, 1013, 1043)));
            seeds.put("foundation_none", new JSONArray());
            seeds.put("control_1004_only", new JSONArray(Arrays.asList(1004)));
            facts.put("foundation_seeds_after_settlement", seeds);
            facts.put("q7WeekResult_pre_seeded", false);
            facts.put("route_4_1_pre_seeded", false);
            facts.put("area1_result_pre_seeded", false);
            facts.put("checks", checks);
            facts.put("mode", candidate ? "candidate" : "baseline");
            cases.put("facts", facts);
            JSONObject control = cases.getJSONObject("control_1004_only").getJSONObject("area_reply");
            JSONObject payload = new JSONObject();
            payload.put("schema", "project7-route539-area-reply-payload-v1");
            payload.put("fixture", "control_1004_only");
            payload.put("before", control.getJSONObject("before"));
            payload.put("after", control.getJSONObject("after"));
            Path casesPath = Paths.get(output).toAbsolutePath();
            Path directory = casesPath.getParent();
            Files.write(directory.resolve("area_reply_payload.json"),
                    payload.toString(2).getBytes(StandardCharsets.UTF_8));
            Files.write(directory.resolve("area_reply_before.bson"),
                    Base64.getDecoder().decode(control.getJSONObject("before").getString("parameters_b64")));
            Files.write(directory.resolve("area_reply_after.bson"),
                    Base64.getDecoder().decode(control.getJSONObject("after").getString("parameters_b64")));
            Files.write(casesPath, cases.toString(2).getBytes(StandardCharsets.UTF_8));
            System.out.println("PASS route539 effect host checks=" + checks);
        } finally {
            // Fixtures clean their own roots; clean any root that failed before close().
            try (java.util.stream.Stream<Path> roots = Files.list(Paths.get(System.getProperty("java.io.tmpdir")))) {
                for (Path path : (Iterable<Path>) roots::iterator)
                    if (path.getFileName().toString().startsWith("route539-effect-")) {
                        try (java.util.stream.Stream<Path> walk = Files.walk(path)) {
                            for (Path each : (Iterable<Path>) walk.sorted(Comparator.reverseOrder())::iterator) Files.deleteIfExists(each);
                        }
                    }
            }
        }
    }
}
