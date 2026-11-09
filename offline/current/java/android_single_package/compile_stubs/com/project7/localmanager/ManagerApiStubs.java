package com.project7.localmanager;

import android.content.Context;
import java.io.IOException;
import java.util.function.Supplier;

// COMPILE ONLY. Never package these stubs. See verify_compile.py for DEX checks.
final class GatewayService {
    static final Object SAVE_ACCESS = new Object();
    private static final java.util.concurrent.atomic.AtomicBoolean RUNNING = new java.util.concurrent.atomic.AtomicBoolean();
    private static LocalGatewayServer lastServer;
    private static Thread lastServerThread;
    static boolean saveAccessBlocked() { throw new UnsupportedOperationException(); }
    static boolean isRunning() { throw new UnsupportedOperationException(); }
}
final class LocalGatewayServer implements Runnable {
    interface ProfileProvider {}
    private final ProfileProvider profileProvider = null;
    private void writeFrame(java.io.OutputStream out, int opcode, byte[] payload) throws IOException {}
    private void completeCallback(java.io.OutputStream out, byte[] eid, int callback, String method) throws IOException {}
    private void refreshResourceProfile(byte[] digest, String account, LocalTutorialStore.Progress progress, LocalEventEngine engine) throws IOException {}
    interface StatusListener { void onStatus(boolean running, String detail); }
    LocalGatewayServer(int port, LocalAccountStore accounts, ProfileProvider profiles,
        LocalTutorialStore tutorials, LocalEventCatalog events, LocalNewbeeCatalog newbee,
        LocalCombatCatalog combat, LocalPatrolCatalog patrol, StatusListener listener) throws IOException {}
    public void run() { throw new UnsupportedOperationException(); }
    public void close() { throw new UnsupportedOperationException(); }
    boolean saveWritersStopped() { throw new UnsupportedOperationException(); }
}
final class LocalBootstrapServer implements Runnable {
    LocalBootstrapServer(int port, Supplier<String> mode) throws IOException {}
    public void run() { throw new UnsupportedOperationException(); }
    public void close() { throw new UnsupportedOperationException(); }
}
final class LocalEventEngine {}
final class LocalProfileStore implements LocalGatewayServer.ProfileProvider {
    private static final Object PROFILE_LOCK = null;
    private final java.io.File profilesDirectory = null;
    private static byte[] readAll(java.io.File file) throws IOException { return null; }
    private static void writeAtomic(java.io.File file, byte[] bytes) throws IOException {}
    LocalResourceCatalog resources() throws IOException { return null; }
    LocalEconomyEngine.Result updateEconomy(String account, String method, byte[] request, LocalTutorialStore.Progress progress) throws IOException { return null; }
    public String clientCompatibility() throws IOException { return null; }
    public boolean ensureHero(String account, int hero) throws IOException { return false; }
    public byte[] load(String account, LocalTutorialStore.Progress progress) throws IOException { throw new UnsupportedOperationException(); }
    public void savePlayerName(String account, String name) throws IOException {}
    public byte[] snapshot(String account, LocalTutorialStore.Progress progress) throws IOException { return null; }
    public LocalCommerceEngine.Result updateCommerce(String account, String method, byte[] request) throws IOException { return null; }
    public LocalProfileEngine.Result updateProfile(String account, String method, byte[] request) throws IOException { return null; }
    public LocalResourceEngine.Result updateResources(String account, String method, byte[] request) throws IOException { return null; }
    public LocalResourceEngine.Result updateServices(String account, String method, byte[] request, LocalTutorialStore.Progress progress) throws IOException { return null; }
    LocalProfileStore(Context context) throws IOException {}
}
final class LocalAccountStore { static String normalizeUsername(String a){return a;}
    static boolean isTemplateAccount(String account) { throw new UnsupportedOperationException(); }
    static final Object FILE_LOCK = new Object();
    LocalAccountStore(Context context) throws IOException {}
    java.util.List<String> listAccounts() throws IOException { throw new UnsupportedOperationException(); }
    int registerOne(String account, String secret) throws IOException { throw new UnsupportedOperationException(); }
    int numericId(String account) throws IOException { throw new UnsupportedOperationException(); }
    Result authenticate(String account, String secret) throws IOException { throw new UnsupportedOperationException(); }
    static final class Result {
        final boolean accepted, registered; final String username;
        private Result(String username, boolean accepted, boolean registered) {
            this.username = username; this.accepted = accepted; this.registered = registered;
        }
    }
}
final class LocalTutorialStore {
    LocalTutorialStore(Context context) throws IOException {}
    static final class Progress { static Progress fresh(){return null;} java.util.Properties toProperties(){return null;} final java.util.Set<Integer> completedEvents=null; final java.util.Set<Integer> availableEvents=null; final java.util.Map<String,java.util.Set<Integer>> eventConditions=null; final java.util.Set<Integer> processingEvents=null; String weekCommit; int weekIndex; int patrolActions; final java.util.Map<Integer,Integer> eventCompletions=null; }
    Progress load(String account) throws IOException { throw new UnsupportedOperationException(); }
    void save(String account, Progress progress) throws IOException { throw new UnsupportedOperationException(); }
}
final class LocalAccountArchive {
    LocalAccountArchive(Context context, LocalAccountStore accounts) throws IOException {}
    static final class Snapshot { Snapshot(String account, byte[] profile, byte[] tutorial) {} }
    Snapshot snapshot(String account) throws IOException { throw new UnsupportedOperationException(); }
}
final class BsonLite {
    static final byte[] EMPTY_DOCUMENT = new byte[0];
    static java.util.List<String> keys(byte[] data) { throw new UnsupportedOperationException(); }
    static Integer intValue(byte[] data, String key) { throw new UnsupportedOperationException(); } static byte[] document(Object...v){return null;} static byte[] documentValue(byte[] p,String k){return null;} static Boolean boolValue(byte[] p,String k){return null;} static byte[] arrayValue(byte[] p,String k){return null;} static byte[] withCopiedValue(byte[] d,String dk,byte[] s,String sk){return null;} static byte[] intDocument(String k,int v){return null;}
    static String stringValue(byte[] data, String key) { throw new UnsupportedOperationException(); }
}
final class LocalEconomyCatalog {}
final class LocalEconomyEngine { static Result apply(byte[] profile, LocalEconomyCatalog catalog, LocalResourceCatalog resources, LocalTutorialStore.Progress progress, String method, byte[] args) { return null; } static String nextDayBlocker(byte[] profile, LocalTutorialStore.Progress progress) { return null; } static int actions(byte[] profile, LocalTutorialStore.Progress progress) { return 0; } static final class Result { boolean accepted,replay; int win; String reason; byte[] reward,profile; java.util.List<Object> replies; Result(byte[] profile){} } }
final class LocalEventCatalog { final java.util.Map<Integer,Object> consumptions=null; final java.util.Map<Integer,byte[]> cityEffects=null;
 final java.util.Map<Integer,String> routes=null; LocalEventCatalog(Context context) throws IOException {} }
final class LocalNewbeeCatalog { LocalNewbeeCatalog(Context context) throws IOException {} }
final class LocalCombatCatalog { LocalCombatCatalog(Context context) throws IOException {} }
final class LocalPatrolCatalog { LocalPatrolCatalog(Context context) throws IOException {} }
final class LocalStartupMode {
    static String get(Context context) { throw new UnsupportedOperationException(); }
    static void set(Context context, int mode) { throw new UnsupportedOperationException(); }
}
/** Own policy ABI for the isolated startup compile group, never runtime code. */
final class CoreDrawPolicy {
    static void prepare(Context context) throws Exception { throw new UnsupportedOperationException(); }
}
/** Own feature preparation descriptors for the isolated startup group only. */
final class HistoryDrawPolicy {
    static void prepare(Context context) throws Exception { throw new UnsupportedOperationException(); }
}
final class SelectorPolicy {
    static void prepare(Context context) throws Exception { throw new UnsupportedOperationException(); }
}
final class DynamicDrawPolicy {
    static void prepare(Context context) throws Exception { throw new UnsupportedOperationException(); }
}
final class WishGateway {
    static void prepare(Context context) throws IOException { throw new UnsupportedOperationException(); }
    public static void prepareStoppedProfile(Object exactStore, String account, int uid,
            java.util.function.BooleanSupplier cancelled) throws IOException { throw new UnsupportedOperationException(); }
}
final class StoryMissionBridge {
    static void prepare(Context context) throws IOException { throw new UnsupportedOperationException(); }
}
final class TrialRetryGateway {
    public static void prepare(Context context) throws IOException { throw new UnsupportedOperationException(); }
}
final class RequestEventGateway {
    static void prepare(Context context) throws IOException { throw new UnsupportedOperationException(); }
}

final class LocalResourceCatalog {}
final class OfflineMechanismGateway { static void prepare(Context context) throws IOException { throw new UnsupportedOperationException(); } }

final class LocalCommerceEngine { static final class Result {} static byte[] refreshStoreLimits(byte[]p,long nowMillis){return null;} private static byte[] spend(byte[]p,String kind,int n){return null;} private static java.util.Map<Integer,Integer> pairCounts(byte[]p){return null;} private static java.util.List<java.util.List<Integer>> pairs(java.util.Map<Integer,Integer>m){return null;} private static java.util.Map<Integer,java.util.Map<Integer,Integer>> storyCounts(byte[]p){return null;} private static java.util.List<java.util.List<Object>> storyPairs(java.util.Map<Integer,java.util.Map<Integer,Integer>>m){return null;} }

final class LocalProfileEngine { static final class Result {} }

final class LocalResourceEngine { static java.util.List<byte[]> array(byte[] b){return null;} static final class Result { byte[] profile; java.util.List<Reply> replies=new java.util.ArrayList<>(); } static final class Reply { final String method; final byte[] parameters; Reply(String method,byte[] parameters){this.method=method;this.parameters=parameters;} } }
