package com.project7.localmanager;

import android.content.Context;
import android.content.res.AssetManager;
import java.io.File;
import java.lang.reflect.Field;
import java.nio.file.Files;
import java.nio.file.Path;
import java.security.MessageDigest;
import java.util.Arrays;
import java.util.Comparator;
import java.util.stream.Stream;

/** Host-only proof: a session handoff carries the exact prepared LocalProfileStore and the
 * formal gateway profile seam still performs one full load per request with a stable persisted
 * result. The actual profile fixture is copied to a temporary directory and deleted on exit.
 */
public final class ProfileHandoffRealProfileHost {
    private static void check(boolean value, String detail) { if (!value) throw new AssertionError(detail); }
    private static String sha(byte[] value) throws Exception {
        StringBuilder text = new StringBuilder();
        for (byte b : MessageDigest.getInstance("SHA-256").digest(value)) text.append(String.format("%02x", b & 255));
        return text.toString();
    }
    private static void deleteTree(Path root) throws Exception {
        try (Stream<Path> walk = Files.walk(root)) {
            walk.sorted(Comparator.reverseOrder()).forEach(path -> { try { Files.deleteIfExists(path); } catch (Exception ignored) { } });
        }
    }
    public static void main(String[] args) throws Exception {
        Path assets = new File(args[0]).toPath();
        Path fixture = new File(args[1]).toPath();
        String fixtureHash = sha(Files.readAllBytes(fixture));
        String account = fixture.getFileName().toString().replaceFirst("\\.bson$", "");
        Path root = Files.createTempDirectory("p7-profile-handoff-");
        try {
            Files.createDirectories(root.resolve("profiles"));
            Path profile = root.resolve("profiles").resolve(account + ".bson");
            Files.copy(fixture, profile);
            Context context = new Context(root.toFile(), new AssetManager(assets.toFile()));
            CoreDrawPolicy.prepare(context);
            HistoryDrawPolicy.prepare(context);
            SelectorPolicy.prepare(context);
            StoryMissionBridge.prepare(context);
            StoryCityPolicy.prepare(context);
            StoryCityCocPolicy.prepare(context);

            LocalProfileStore prepared = new LocalProfileStore(context);
            prepared.load(account, LocalTutorialStore.Progress.fresh());
            Object lock = new Object();
            ProfileStoreHandoff handoff = new ProfileStoreHandoff(lock);
            handoff.publish(prepared);
            for (Field field : ProfileStoreHandoff.class.getDeclaredFields())
                check(field.getType() != byte[].class, "handoff field retains profile bytes: " + field.getName());
            LocalProfileStore handed;
            synchronized (lock) { handed = handoff.take(); }
            check(handed == prepared, "handoff did not carry the exact prepared LocalProfileStore");
            check(handoff.consumed() && !handoff.available(), "handoff was not one-shot");

            FailureSafeProfileProvider provider = new FailureSafeProfileProvider(handed);
            byte[] first = provider.load(account, LocalTutorialStore.Progress.fresh());
            String firstHash = sha(first);
            check(firstHash.equals(sha(Files.readAllBytes(profile))), "formal request did not persist the stable result");
            long size = Files.size(profile);
            byte[] second = provider.load(account, LocalTutorialStore.Progress.fresh());
            check(sha(second).equals(sha(Files.readAllBytes(profile))), "second formal request did not persist the stable result");
            check(size == Files.size(profile), "formal request changed the profile size");
            byte[] changed = BsonLite.withProfileInt(second, "__handoff_probe", 1);
            Files.write(profile, changed);
            byte[] third = provider.load(account, LocalTutorialStore.Progress.fresh());
            check(!Arrays.equals(second, third), "formal request served a cached profile instead of a full load");
            Integer probe = BsonLite.intValue(third, "__handoff_probe");
            check(probe != null && probe.intValue() == 1, "formal request overwrote newer persisted profile data");
            check(sha(third).equals(sha(Files.readAllBytes(profile))), "reloaded profile was not persisted stably");
            check(fixtureHash.equals(sha(Files.readAllBytes(fixture))), "source profile fixture was modified");
            synchronized (lock) {
                try { handoff.take(); throw new AssertionError("handoff reused after requests"); }
                catch (java.io.IOException expected) { }
            }
            System.out.println("HANDOFF_SAME_STORE=true CONSUMED_ONCE=true FULL_LOADS_PER_REQUEST=true STABLE_PERSISTED=true PROFILE_BYTES_IN_HANDOFF=false");
        } finally {
            deleteTree(root);
        }
    }
}
