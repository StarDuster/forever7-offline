package com.project7.localmanager;

import java.io.File;
import java.io.IOException;
import java.lang.reflect.*;
import java.util.Arrays;
import java.util.Properties;

/** Minimal generic Store-write failure handling at the original ProfileProvider seam.
 *  The day transaction is observed under the original store monitor + PROFILE_LOCK:
 *  before bytes are read without load/repair, the original updateEconomy runs, and only a
 *  strict byte-identical re-read may produce the old-day updateDay unlock + explicit message.
 *  A different re-read is an uncertain commit and rethrows the original IOException, which
 *  uses the existing handleClient disconnect/reconnect resync; a failed re-read does the same.
 *  No partial replies, settlement or rewards are ever reused. All non-day calls delegate. */
final class FailureSafeProfileProvider implements LocalGatewayServer.ProfileProvider {
    static final String MESSAGE = "本地存档失败，请重试。";
    private static volatile Object profileLock;
    private static volatile Field profilesDirectory;
    private static volatile Method readAll;
    private static volatile Method cityDataReply;

    private final LocalProfileStore delegate;

    FailureSafeProfileProvider(LocalProfileStore delegate) {
        if (delegate == null) throw new IllegalArgumentException("delegate");
        this.delegate = delegate;
    }

    LocalProfileStore delegate() { return delegate; }

    static Object unwrap(Object provider) {
        while (provider instanceof FailureSafeProfileProvider) provider = ((FailureSafeProfileProvider) provider).delegate();
        return provider;
    }

    /** Exact wrapper-only store view for COC seams; never duck-types an unrelated provider. */
    static LocalProfileStore unwrapStore(Object provider) {
        Object current = provider;
        while (current instanceof FailureSafeProfileProvider) current = ((FailureSafeProfileProvider) current).delegate();
        return current instanceof LocalProfileStore ? (LocalProfileStore) current : null;
    }

    public String clientCompatibility() throws IOException { return delegate.clientCompatibility(); }
    public boolean ensureHero(String account, int hero) throws IOException { return delegate.ensureHero(account, hero); }
    private static void diagnostic(String stage, long started) {
        try { android.util.Log.i("Project7Gateway", "PROFILE stage=" + stage +
            " elapsed_ms=" + ((System.nanoTime() - started) / 1000000L)); }
        catch (Throwable ignored) { }
    }
    public byte[] load(String account, LocalTutorialStore.Progress progress) throws IOException {
        long started = System.nanoTime();
        diagnostic("load_begin", started);
        try {
            byte[] result = delegate.load(account, progress);
            diagnostic("load_ok", started);
            return result;
        } catch (IOException failure) {
            diagnostic("load_fail", started);
            throw failure;
        } catch (RuntimeException failure) {
            diagnostic("load_fail", started);
            throw failure;
        }
    }
    public void savePlayerName(String account, String name) throws IOException { delegate.savePlayerName(account, name); }
    /** Delegate exactly; snapshot performs time-driven refreshes and may write. */
    public byte[] snapshot(String account, LocalTutorialStore.Progress progress) throws IOException {
        return delegate.snapshot(account, progress);
    }
    public LocalCommerceEngine.Result updateCommerce(String account, String method, byte[] request) throws IOException { return delegate.updateCommerce(account, method, request); }
    public LocalProfileEngine.Result updateProfile(String account, String method, byte[] request) throws IOException { return delegate.updateProfile(account, method, request); }
    public LocalResourceEngine.Result updateResources(String account, String method, byte[] request) throws IOException {
        if ("requestLuckyDrawAllLeftCard".equals(method)) {
            return AllLeftActivitySyncCandidate.apply(delegate.updateResources(account, method, request));
        }
        if (!"requestLuckyDrawFile".equals(method)) return delegate.updateResources(account, method, request);
        long started = System.nanoTime();
        diagnostic("draw_file_begin", started);
        try {
            LocalResourceEngine.Result result = delegate.updateResources(account, method, request);
            diagnostic("draw_file_ok", started);
            return result;
        } catch (IOException failure) {
            diagnostic("draw_file_fail", started);
            throw failure;
        } catch (RuntimeException failure) {
            diagnostic("draw_file_fail", started);
            throw failure;
        }
    }
    public LocalResourceEngine.Result updateServices(String account, String method, byte[] request, LocalTutorialStore.Progress progress) throws IOException { return delegate.updateServices(account, method, request, progress); }

    public LocalEconomyEngine.Result updateEconomy(String account, String method, byte[] request, LocalTutorialStore.Progress progress) throws IOException {
        if (!"incDayWhenNoActionVal".equals(method)) {
            LocalEconomyEngine.Result result = delegate.updateEconomy(account, method, request, progress);
            if ("canteenRequest".equals(method) && result != null && progress != null && result.profile != null) {
                // The stock canteen reply serializes only profile.city, while the
                // authoritative action count lives in Progress. Rebuild that one
                // reply with the same progress overlay used by normal city replies.
                byte[] corrected = cityReply(progress, result.profile);
                if (corrected != null) {
                    for (int i = 0; i < result.replies.size(); i++) {
                        Object raw = result.replies.get(i);
                        if (!(raw instanceof LocalResourceEngine.Reply)) continue;
                        LocalResourceEngine.Reply reply = (LocalResourceEngine.Reply) raw;
                        if ("get_city_data_reply".equals(reply.method)) {
                            result.replies.set(i, new LocalResourceEngine.Reply("get_city_data_reply", corrected));
                        }
                    }
                }
            }
            return result;
        }
        synchronized (delegate) {
            synchronized (profileLock()) {
                byte[] before = readDirect(account);
                Properties beforeProgress = progress == null ? null : progress.toProperties();
                try {
                    return delegate.updateEconomy(account, method, request, progress);
                } catch (IOException failure) {
                    byte[] actual;
                    try {
                        actual = readDirect(account);
                    } catch (IOException readFailure) {
                        failure.addSuppressed(readFailure);
                        throw failure;
                    }
                    if (!Arrays.equals(before, actual)) throw failure; // uncertain commit -> disconnect/reconnect resync
                    if (beforeProgress != null && !beforeProgress.equals(progress.toProperties())) throw failure; // progress changed -> uncertain state
                    LocalEconomyEngine.Result result = new LocalEconomyEngine.Result(actual);
                    result.accepted = false;
                    result.reason = MESSAGE;
                    result.replies.add(new LocalResourceEngine.Reply("showMessageStr", BsonLite.document("m", MESSAGE)));
                    Integer day = BsonLite.intValue(BsonLite.documentValue(actual, "weeknum"), "d");
                    result.replies.add(new LocalResourceEngine.Reply("updateDay", BsonLite.intDocument("d", day == null ? 0 : day)));
                    return result;
                }
            }
        }
    }

    private static byte[] cityReply(LocalTutorialStore.Progress progress, byte[] profile) {
        try {
            Method method = cityDataReply;
            if (method == null) {
                method = BsonLite.class.getDeclaredMethod(
                        "cityDataReplyDocument", LocalTutorialStore.Progress.class, byte[].class);
                method.setAccessible(true);
                cityDataReply = method;
            }
            return (byte[]) method.invoke(null, progress, profile);
        } catch (Exception ignored) {
            return null;
        }
    }

    private static Object profileLock() throws IOException {
        prepareStoreAccess();
        return profileLock;
    }

    private byte[] readDirect(String account) throws IOException {
        prepareStoreAccess();
        try {
            File directory = (File) profilesDirectory.get(delegate);
            String name = LocalAccountStore.normalizeUsername(account);
            File file = new File(directory, name + ".bson");
            if (!file.isFile()) throw new IOException("profile does not exist");
            return (byte[]) readAll.invoke(null, file);
        } catch (InvocationTargetException failure) {
            Throwable cause = failure.getCause();
            if (cause instanceof IOException) throw (IOException) cause;
            throw new IOException("profile read failed", cause);
        } catch (ReflectiveOperationException failure) {
            throw new IOException("profile read failed", failure);
        } catch (RuntimeException failure) {
            throw new IOException("profile read failed", failure);
        }
    }

    private static synchronized void prepareStoreAccess() throws IOException {
        if (profileLock != null) return;
        try {
            Field lock = LocalProfileStore.class.getDeclaredField("PROFILE_LOCK");
            lock.setAccessible(true);
            Field directory = LocalProfileStore.class.getDeclaredField("profilesDirectory");
            directory.setAccessible(true);
            Method read = LocalProfileStore.class.getDeclaredMethod("readAll", File.class);
            read.setAccessible(true);
            Object value = lock.get(null);
            if (value == null) throw new IOException("profile lock missing");
            profilesDirectory = directory;
            readAll = read;
            profileLock = value;
        } catch (ReflectiveOperationException failure) {
            throw new IOException("profile store seams unavailable", failure);
        }
    }
}
