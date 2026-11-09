package com.project7.localmanager;

import android.content.Context;
import java.io.IOException;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.atomic.AtomicBoolean;
import java.util.function.Supplier;

// HOST TEST ONLY. In-memory finite lifecycle model; never DEX/APK input.
final class HostControl {
    static boolean storageMode;
    static String failAt;
    static volatile String blockAt;
    static volatile CountDownLatch constructorEntered = new CountDownLatch(1);
    static volatile CountDownLatch constructorRelease = new CountDownLatch(0);
    static final java.util.concurrent.atomic.AtomicInteger profileConstructions = new java.util.concurrent.atomic.AtomicInteger();
    static void construct(String stage) throws IOException {
        if (stage.equals("profiles")) profileConstructions.incrementAndGet();
        if (stage.equals(blockAt)) {
            constructorEntered.countDown();
            LocalGatewayServer.await(constructorRelease);
        }
        if (stage.equals(failAt)) throw new IOException("host injected " + stage + " constructor failure");
    }
}
final class GatewayService {
    static final Object SAVE_ACCESS = new Object();
    private static final AtomicBoolean RUNNING = new AtomicBoolean();
    private static LocalGatewayServer lastServer;
    private static Thread lastServerThread;
    static boolean isRunning() { return RUNNING.get(); }
    static boolean saveAccessBlocked() {
        return RUNNING.get() || (lastServerThread != null && lastServerThread.isAlive()) ||
            (lastServer != null && !lastServer.saveWritersStopped());
    }
}
final class LocalGatewayServer implements Runnable {
    interface ProfileProvider {}
    interface StatusListener { void onStatus(boolean running, String detail); }
    final StatusListener status;
    final CountDownLatch closed = new CountDownLatch(1);
    volatile boolean stopped;
    int closeCalls;
    LocalGatewayServer(int port, LocalAccountStore accounts, ProfileProvider profiles,
        LocalTutorialStore tutorials, LocalEventCatalog events, LocalNewbeeCatalog newbee,
        LocalCombatCatalog combat, LocalPatrolCatalog patrol, StatusListener listener) throws IOException {
        HostControl.construct("gateway"); status = listener;
    }
    public void run() { status.onStatus(true, "host fake bound 23333"); await(closed); }
    public void close() { closeCalls++; stopped = true; closed.countDown(); }
    boolean saveWritersStopped() { return stopped; }
    static void await(CountDownLatch latch) {
        try { latch.await(); } catch (InterruptedException error) { Thread.currentThread().interrupt(); }
    }
}
final class LocalBootstrapServer implements Runnable {
    final CountDownLatch closed = new CountDownLatch(1);
    LocalBootstrapServer(int port, Supplier<String> mode) throws IOException { HostControl.construct("bootstrap"); }
    public void run() { LocalGatewayServer.await(closed); }
    public void close() { closed.countDown(); }
}
final class LocalProfileStore implements LocalGatewayServer.ProfileProvider {
    final java.io.File root;
    LocalProfileStore(Context app) throws IOException {
        HostControl.construct("profiles"); root = HostControl.storageMode ? app.getFilesDir() : null;
    }
    public byte[] load(String account, LocalTutorialStore.Progress progress) throws IOException {
        HostStorage.calls.add("profile.load"); HostStorage.profileLoads++;
        java.io.File file = new java.io.File(new java.io.File(root, "profiles"), account + ".bson");
        java.util.Properties p = file.isFile() ? HostStorage.read(file) : new java.util.Properties();
        int uid = new LocalAccountStore(new Context(root)).numericId(account);
        p.setProperty("uid", Integer.toString(uid)); p.setProperty("account", account); p.setProperty("an", account);
        for (String key : new String[]{"heromgr", "weeknum", "city"}) p.setProperty("doc." + key, "valid");
        p.setProperty("stock-normalized", "true");
        progress.p.setProperty("stock-load-touched", "true");
        HostStorage.write(file, p); return java.nio.file.Files.readAllBytes(file.toPath());
    }
    public String clientCompatibility() throws IOException { return null; }
    public boolean ensureHero(String account, int hero) throws IOException { return false; }
    public void savePlayerName(String account, String name) throws IOException {}
    public byte[] snapshot(String account, LocalTutorialStore.Progress progress) throws IOException { return load(account, progress); }
    public LocalCommerceEngine.Result updateCommerce(String account, String method, byte[] request) throws IOException { return null; }
    public LocalProfileEngine.Result updateProfile(String account, String method, byte[] request) throws IOException { return null; }
    public LocalResourceEngine.Result updateResources(String account, String method, byte[] request) throws IOException { return null; }
    public LocalResourceEngine.Result updateServices(String account, String method, byte[] request, LocalTutorialStore.Progress progress) throws IOException { return null; }
    public LocalEconomyEngine.Result updateEconomy(String account, String method, byte[] request, LocalTutorialStore.Progress progress) throws IOException { return null; }
}
final class LocalCommerceEngine { static final class Result {} }
final class LocalProfileEngine { static final class Result {} }
final class LocalResourceEngine {
    static java.util.List<byte[]> array(byte[] data) {
        return data == null ? java.util.Collections.<byte[]>emptyList() : java.util.Collections.singletonList(new byte[]{1});
    }
    static final class Result {
        byte[] profile;
        Result(byte[] profile) { this.profile = profile; }
        final java.util.List<Reply> replies = new java.util.ArrayList<>();
        void add(String method, byte[] parameters) { replies.add(new Reply(method, parameters)); }
    }
    static final class Reply {
        final String method;
        final byte[] parameters;
        Reply(String method, byte[] parameters) { this.method = method; this.parameters = parameters; }
    }
}
final class LocalEconomyEngine {
    static final class Result {
        boolean accepted, replay; int win; String reason; byte[] reward, profile;
        final java.util.List<LocalResourceEngine.Reply> replies = new java.util.ArrayList<>();
        Result(byte[] profile) {}
    }
}
final class LocalAccountStore {
    static String normalizeUsername(String account){return account;}
    static final Object FILE_LOCK = new Object();
    final java.io.File root;
    LocalAccountStore(Context app) throws IOException {
        HostControl.construct("accounts"); root = HostControl.storageMode ? app.getFilesDir() : null;
        if (root != null) HostStorage.accountConstructions++;
    }
    java.util.List<String> listAccounts() throws IOException {
        return new java.util.ArrayList<>(HostStorage.readOrEmpty(new java.io.File(root, "accounts.properties")).stringPropertyNames());
    }
    int registerOne(String account, String secret) throws IOException {
        HostStorage.calls.add("account.register"); HostStorage.registrations++;
        java.io.File file = new java.io.File(root, "accounts.properties");
        java.util.Properties p = HostStorage.readOrEmpty(file);
        if (p.containsKey(account)) throw new IOException("duplicate synthetic account");
        p.setProperty(account, HostStorage.secretHash(secret)); HostStorage.write(file, p);
        if ("after-account-write".equals(HostStorage.fail)) throw new IOException("synthetic interrupted account registration");
        return numericId(account);
    }
    int numericId(String account) throws IOException {
        HostStorage.calls.add("account.numericId");
        if (!listAccounts().contains(account)) throw new IOException("missing synthetic account");
        java.io.File file = new java.io.File(root, "account-ids.properties");
        java.util.Properties p = HostStorage.readOrEmpty(file);
        if (!p.containsKey(account)) { p.setProperty(account, "901"); HostStorage.write(file, p); }
        return Integer.parseInt(p.getProperty(account));
    }
    Result authenticate(String account, String secret) throws IOException {
        if (!Thread.holdsLock(FILE_LOCK)) throw new IOException("synthetic auth lock missing");
        HostStorage.calls.add("account.authenticate");
        String stored = HostStorage.readOrEmpty(new java.io.File(root, "accounts.properties")).getProperty(account);
        if (stored == null) { HostStorage.unexpectedAutoRegisters++; registerOne(account, secret); return new Result(account, true, true); }
        return new Result(account, stored.equals(HostStorage.secretHash(secret)), false);
    }
    static final class Result {
        final boolean accepted, registered; final String username;
        Result(String username, boolean accepted, boolean registered) {
            this.username = username; this.accepted = accepted; this.registered = registered;
        }
    }
}
final class LocalTutorialStore {
    final java.io.File root;
    LocalTutorialStore(Context app) throws IOException {
        HostControl.construct("tutorials"); root = HostControl.storageMode ? app.getFilesDir() : null;
    }
    static final class Progress {
        final java.util.Properties p;
        Progress(java.util.Properties p) { this.p = p; }
        java.util.Properties toProperties(){return (java.util.Properties)p.clone();}
        static Progress fromProperties(java.util.Properties p){return new Progress(p);}
    }
    Progress load(String account) throws IOException {
        HostStorage.calls.add("tutorial.load");
        java.io.File file = new java.io.File(new java.io.File(root, "tutorials"), account + ".properties");
        return new Progress(file.isFile() ? HostStorage.read(file) : HostStorage.fresh());
    }
    void save(String account, Progress progress) throws IOException {
        HostStorage.calls.add("tutorial.save"); HostStorage.tutorialSaves++;
        HostStorage.write(new java.io.File(new java.io.File(root, "tutorials"), account + ".properties"), progress.p);
    }
}
final class LocalAccountArchive {
    final java.io.File root;
    LocalAccountArchive(Context app, LocalAccountStore accounts) { root = app.getFilesDir(); }
    static final class Snapshot {}
    Snapshot snapshot(String account) throws IOException {
        HostStorage.calls.add("archive.snapshot"); HostStorage.snapshots++;
        java.io.File profile = new java.io.File(new java.io.File(root, "profiles"), account + ".bson");
        java.io.File tutorial = new java.io.File(new java.io.File(root, "tutorials"), account + ".properties");
        if (!profile.isFile()) throw new IOException("missing synthetic profile");
        java.util.Properties p = HostStorage.read(profile);
        for (String key : new String[]{"heromgr", "weeknum", "city"})
            if (!"valid".equals(p.getProperty("doc." + key))) throw new IOException("synthetic profile validation failed");
        java.util.Properties progress = tutorial.isFile() ? HostStorage.read(tutorial) : HostStorage.fresh();
        if (!"2".equals(progress.getProperty("schemaVersion"))) throw new IOException("synthetic progress validation failed");
        return new Snapshot(); // No canonical write or portable-profile writeback.
    }
}
final class BsonLite {
    static final byte[] EMPTY_DOCUMENT = new byte[0];
    static java.util.List<String> keys(byte[] data) {
        return new java.util.ArrayList<String>(HostStorage.parse(data).stringPropertyNames());
    }
    static Boolean boolValue(byte[] data, String key) {
        if (data == null) return null;
        String value = HostStorage.parse(data).getProperty(key);
        return value == null ? null : Boolean.valueOf(value);
    }
    static byte[] arrayValue(byte[] data, String key) { return data == null ? null : new byte[]{1}; }
    static byte[] withProfileArray(byte[] data, String key, java.util.List<?> values) { return data; }
    static byte[] withCopiedValue(byte[] data, String key, byte[] source, String sourceKey) { return data; }
    static Integer intValue(byte[] data, String key) {
        String value = HostStorage.parse(data).getProperty(key);
        return value == null ? null : Integer.valueOf(value);
    }
    static String stringValue(byte[] data, String key) { return HostStorage.parse(data).getProperty(key); }
    static byte[] document(Object... values) {
        StringBuilder out = new StringBuilder();
        for (int i = 0; i + 1 < values.length; i += 2) out.append(values[i]).append('=').append(values[i + 1]).append('\n');
        return out.toString().getBytes(java.nio.charset.StandardCharsets.UTF_8);
    }
    static byte[] intDocument(String key, int value) { return document(key, value); }
    static byte[] documentValue(byte[] data, String key) { return data == null ? null : new byte[]{1}; }
}
final class HostStorage {
    static int accountConstructions, registrations, profileLoads, tutorialSaves, snapshots, unexpectedAutoRegisters;
    static String fail;
    static final java.util.List<String> calls = new java.util.ArrayList<>();
    static void reset() {
        accountConstructions = registrations = profileLoads = tutorialSaves = snapshots = unexpectedAutoRegisters = 0;
        calls.clear(); fail = null; HostControl.storageMode = true;
    }
    static java.util.Properties parse(byte[] raw) {
        java.util.Properties p = new java.util.Properties();
        try { p.load(new java.io.ByteArrayInputStream(raw)); }
        catch (IOException error) { throw new IllegalArgumentException("invalid synthetic profile"); }
        return p;
    }
    static java.util.Properties read(java.io.File file) throws IOException {
        return parse(java.nio.file.Files.readAllBytes(file.toPath()));
    }
    static java.util.Properties readOrEmpty(java.io.File file) throws IOException {
        return file.isFile() ? read(file) : new java.util.Properties();
    }
    static void write(java.io.File file, java.util.Properties p) throws IOException {
        file.getParentFile().mkdirs();
        try (java.io.FileOutputStream out = new java.io.FileOutputStream(file)) { p.store(out, "synthetic host fixture"); }
    }
    static String secretHash(String secret) throws IOException {
        try { return StableIdentityBootstrap.digest(secret); }
        catch (Exception error) { throw new IOException("synthetic hash failure"); }
    }
    static java.util.Properties fresh() {
        java.util.Properties p = new java.util.Properties();
        for (String key : new String[]{"availableEvents", "processingEvents", "completedEvents", "processingNewbees", "finishedNewbees", "status", "scene", "patrol.day", "economy.commit", "week.commit", "patrol.heroes", "patrol.events", "patrol.replays"}) p.setProperty(key, "");
        p.setProperty("availableEvents", "1000"); p.setProperty("schemaVersion", "2");
        for (String key : new String[]{"initPrologue", "inEmergency", "patrol.rewardPending"}) p.setProperty(key, "false");
        for (String key : new String[]{"patrol.count", "patrol.area", "patrol.actions", "patrol.sandglass", "week.index", "patrol.favor"}) p.setProperty(key, "0");
        return p;
    }
}
final class LocalEventCatalog { LocalEventCatalog(Context app) throws IOException { HostControl.construct("events"); } }
final class LocalNewbeeCatalog { LocalNewbeeCatalog(Context app) throws IOException { HostControl.construct("newbee"); } }
final class LocalCombatCatalog { LocalCombatCatalog(Context app) throws IOException { HostControl.construct("combat"); } }
final class LocalPatrolCatalog { LocalPatrolCatalog(Context app) throws IOException { HostControl.construct("patrol"); } }
final class LocalStartupMode {
    static String mode = "resources";
    static String get(Context app) { return mode; }
    static void set(Context app, int value) { mode = value == 1 ? "game" : "resources"; }
}
