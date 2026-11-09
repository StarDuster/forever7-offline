package com.project7.localmanager;

import java.io.File;
import java.io.IOException;
import java.io.OutputStream;
import java.util.List;

/** COMPILE ONLY exact pinned manager API. Never place these classes in DEX/APK. */
final class LocalGatewayServer {
    LocalGatewayServer(int port, LocalAccountStore a, ProfileProvider p, LocalTutorialStore t, LocalEventCatalog e, LocalNewbeeCatalog n, LocalCombatCatalog c, LocalPatrolCatalog l, StatusListener s) {}
    interface StatusListener {}
    interface ProfileProvider {}
    private final ProfileProvider profileProvider = null;
    private void completeCallback(OutputStream out,byte[] eid,int callback,String method) throws IOException {}
    private void refreshResourceProfile(byte[]digest,String account,LocalTutorialStore.Progress p,LocalEventEngine e) throws IOException {}
    private void writeFrame(OutputStream output, int opcode, byte[] payload) throws IOException {}
}
final class LocalProfileStore {
    LocalProfileStore(android.content.Context c) {}
    static final Object PROFILE_LOCK = null;
    private final File profilesDirectory = null;
    private static byte[] readAll(File file) throws IOException { return null; }
    private static void writeAtomic(File file, byte[] bytes) throws IOException {}
    LocalResourceCatalog resources() throws IOException { return null; }
}
final class LocalResourceCatalog {final java.util.Map<Integer,Hero> heroes=null;static final class Hero{final int files,rank;Hero(String[]row){files=rank=0;}}LocalResourceCatalog(java.io.InputStream in) throws IOException {}}
final class LocalResourceEngine {
    static final class Result {
        byte[] profile;
        final List<Reply> replies = null;
        final List<List<Integer>> itemRewards = null;
        Result(byte[] profile) {}
        void add(String method, byte[] parameters) {}
        byte[] reward() { return null; }
    }
    static final class Reply {
        final String method = null;
        final byte[] parameters = null;
        Reply(String method, byte[] parameters) {}
    }
    static boolean ownsHero(byte[] profile, int hero) { return false; }
    static void grant(Result result, LocalResourceCatalog catalog, String kind, int item, int amount, int quality) {}
    static void syncCurrencies(Result result) {}
    static int currencyItem(String kind) { return 0; }
    static List<byte[]> array(byte[] bytes) { return null; }
}
final class BsonLite {
    private BsonLite() {}
    static String uuidValue(byte[] bytes,String key) {return null;}
    static final byte[] EMPTY_DOCUMENT = null;
    static byte[] document(Object... values) { return null; }
    static byte[] documentValue(byte[] bytes, String key) { return null; }
    static byte[] arrayValue(byte[] bytes, String key) { return null; }
    static String stringValue(byte[] bytes, String key) { return null; }
    static Integer intValue(byte[] bytes, String key) { return null; }
    static Boolean boolValue(byte[] bytes, String key) { return null; }
    static List<Integer> intArrayValues(byte[] bytes, String key) { return null; }
    static byte[] profileHeroDocument(byte[] bytes, int hero) { return null; }
    static byte[] withHeroDocument(byte[] bytes, int hero, byte[] value) { return null; }
    static byte[] withProfileBool(byte[] bytes, String key, boolean value) { return null; }
    static byte[] withoutProfileKey(byte[] bytes, String key) { return null; }
    static Number numericValue(byte[] bytes, String key) { return null; }
    static List<String> keys(byte[] bytes) { return null; }
    static Object messagePackValue(byte[] bytes, boolean array) { return null; }
    static byte[] withProfileArray(byte[] bytes, String key, List<?> value) { return null; }
    static byte[] withProfileInt(byte[] bytes, String key, int value) { return null; }
    static byte[] withProfileString(byte[] bytes, String key, String value) { return null; }
    static byte[] withProfileDocument(byte[] bytes, String key, byte[] value) { return null; }
    static byte[] withCopiedValue(byte[] target, String targetKey, byte[] source, String sourceKey) { return null; }
}
final class ProtoLite {
    private ProtoLite() {}
    static byte[] entityMessage(byte[] id, byte[] digest, byte[] parameters) { return null; }
}

final class LocalGiftEngine {LocalGiftEngine() {} static void consume(LocalResourceEngine.Result r,int id,int n) {}}
final class LocalAccountStore {LocalAccountStore(android.content.Context c) throws IOException {} static boolean isTemplateAccount(String account) {return false;}}
final class LocalTutorialStore {LocalTutorialStore(android.content.Context c) {} static final class Progress {java.util.Set<Integer> completedEvents,processingEvents,availableEvents;java.util.Map<String,java.util.Set<Integer>> eventConditions;private Progress(java.util.Set<Integer>a,java.util.Set<Integer>b,boolean c,java.util.Set<Integer>d,java.util.Set<Integer>e,java.util.Set<Integer>f,java.util.Map<String,java.util.Set<Integer>>g,boolean h,String i,String j){}}}
final class LocalEventEngine {LocalEventEngine(LocalEventCatalog a,LocalNewbeeCatalog b,LocalTutorialStore.Progress c,int d) {}}
final class LocalEventCatalog {LocalEventCatalog(java.io.InputStream s) throws IOException {} static final class Event {boolean release;} Event get(int id){return null;} java.util.Set<Integer> mutex(int id){return null;}}
final class LocalNewbeeCatalog {LocalNewbeeCatalog(java.io.InputStream s) throws IOException {}}
final class LocalCombatCatalog {LocalCombatCatalog(java.io.InputStream s) throws IOException {}}
final class LocalPatrolCatalog {LocalPatrolCatalog(java.io.InputStream s) throws IOException {}}

final class LocalDrawEngine {LocalDrawEngine() {} static byte[] reveal(LocalResourceEngine.Result r,LocalResourceCatalog c,byte[]card){return null;}}
