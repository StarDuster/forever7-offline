package com.project7.localmanager;

import java.io.File;
import java.io.IOException;
import java.io.OutputStream;
import java.util.List;

/** COMPILE ONLY exact pinned manager API. Never place these classes in DEX/APK. */
final class LocalGatewayServer {
    interface ProfileProvider {}
    private final ProfileProvider profileProvider = null;
    private void writeFrame(OutputStream output, int opcode, byte[] payload) throws IOException {}
}
final class LocalProfileStore {
    static final Object PROFILE_LOCK = null;
    private final File profilesDirectory = null;
    private static byte[] readAll(File file) throws IOException { return null; }
    private static void writeAtomic(File file, byte[] bytes) throws IOException {}
    LocalResourceCatalog resources() throws IOException { return null; }
    LocalEconomyEngine.Result updateEconomy(String account, String method, byte[] request, LocalTutorialStore.Progress progress) { return null; }
}
final class LocalResourceCatalog {}
final class LocalResourceEngine {
    static final class Result {
        byte[] profile;
        final List<Reply> replies = null;
        final List<List<Integer>> itemRewards = null;
        final List<Integer> heroRewards = null;
        final List<List<Object>> treasureRewards = null;
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
    static void grant(Result result, LocalResourceCatalog catalog, String kind, int item, int amount, int quality, byte[] design) {}
    static void syncCurrencies(Result result) {}
    static int value(byte[] profile, String key) { return 0; }
    static boolean currency(String key) { return false; }
    static int currencyItem(String kind) { return 0; }
    static List<byte[]> array(byte[] bytes) { return null; }
}
final class LocalTutorialStore { static final class Progress { static Progress fresh(){return null;} final java.util.Set<Integer> completedEvents=null; final java.util.Set<Integer> availableEvents=null; final java.util.Map<String,java.util.Set<Integer>> eventConditions=null; final java.util.Set<Integer> processingEvents=null; String weekCommit; int weekIndex; int patrolActions; final java.util.Map<Integer,Integer> eventCompletions=null; } }
final class LocalEconomyCatalog {}
final class LocalEconomyEngine { static Result apply(byte[] profile, LocalEconomyCatalog catalog, LocalResourceCatalog resources, LocalTutorialStore.Progress progress, String method, byte[] args) { return null; } static String nextDayBlocker(byte[] profile, LocalTutorialStore.Progress progress) { return null; } static int actions(byte[] profile, LocalTutorialStore.Progress progress) { return 0; } static final class Result { boolean accepted,replay; int win; String reason; byte[] reward,profile; java.util.List<Object> replies; } }
final class LocalEventCatalog { final java.util.Map<Integer,Object> consumptions=null; final java.util.Map<Integer,byte[]> cityEffects=null;
 final java.util.Map<Integer,String> routes=null; java.util.Set<Integer> mutex(int e){return null;} }
final class BsonLite {
    static final class UuidValue {final byte[] bytes;UuidValue(String value){bytes=null;}}
    static String uuidValue(byte[] bytes, String key) { return null; }
    static final byte[] EMPTY_DOCUMENT = null;
    static byte[] document(Object... values) { return null; }
    static byte[] documentValue(byte[] bytes, String key) { return null; }
    static byte[] intDocument(String key, int value) { return null; }
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
    static byte[] q7OriginalAllAreaInfoReplyDocument(boolean unlocked, LocalTutorialStore.Progress progress, byte[] profile) { return null; }
    static byte[] withLocalCityState(byte[] bytes, LocalTutorialStore.Progress progress) { return null; }
    static byte[] allAreaInfoReplyDocument(boolean unlocked, LocalTutorialStore.Progress progress, byte[] profile) { return null; }
    static byte[] withProfileArray(byte[] bytes, String key, List<?> value) { return null; }
    static byte[] withProfileInt(byte[] bytes, String key, int value) { return null; }
    static byte[] withProfileString(byte[] bytes, String key, String value) { return null; }
    static byte[] withProfileDocument(byte[] bytes, String key, byte[] value) { return null; }
    static byte[] withCopiedValue(byte[] target, String targetKey, byte[] source, String sourceKey) { return null; }
}
final class ProtoLite {
    static byte[] entityMessage(byte[] id, byte[] digest, byte[] parameters) { return null; }
}

final class LocalWeekCatalog { final java.util.Map<Integer,Integer> entrances=null; final java.util.Map<Integer,int[]> endings=null; LocalWeekCatalog(java.io.InputStream in)throws java.io.IOException{} }

final class LocalWeekEngine { static boolean canEnter(byte[] p,LocalWeekCatalog c,int m){return false;} static LocalResourceEngine.Result apply(byte[] p,LocalWeekCatalog c,LocalTutorialStore.Progress g,String m,byte[] a){return null;} }
