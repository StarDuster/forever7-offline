package com.project7.localmanager;

import android.content.Context;
import java.io.File;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.Arrays;

/** Host benchmark only: real 517KB profile through FailureSafeProfileProvider.snapshot(). */
public final class SnapshotCacheHost {
  public static void main(String[] args) throws Exception {
    Path fixture = java.nio.file.Paths.get(args[0]);
    Path assets = java.nio.file.Paths.get(args[1]);
    Path root = Files.createTempDirectory("p7-snapshot-cache-");
    try {
      String account = fixture.getFileName().toString().replaceFirst("\\.bson$", "");
      Files.createDirectories(root.resolve("profiles"));
      Path profile = root.resolve("profiles").resolve(account + ".bson");
      Files.copy(fixture, profile);
      Context context = new Context(root.toFile(), new android.content.res.AssetManager(assets.toFile()));
      CoreDrawPolicy.prepare(context);
      HistoryDrawPolicy.prepare(context);
      SelectorPolicy.prepare(context);
      StoryMissionBridge.prepare(context);
      StoryCityPolicy.prepare(context);
      StoryCityCocPolicy.prepare(context);
      LocalProfileStore store = new LocalProfileStore(context);
      FailureSafeProfileProvider provider = new FailureSafeProfileProvider(store);
      LocalTutorialStore.Progress progress = LocalTutorialStore.Progress.fresh();
      long first = System.nanoTime();
      byte[] a = provider.snapshot(account, progress);
      long firstMs = (System.nanoTime() - first) / 1000000;
      long second = System.nanoTime();
      byte[] b = provider.snapshot(account, progress);
      long secondMs = (System.nanoTime() - second) / 1000000;
      if (!Arrays.equals(a, b)) throw new AssertionError("cached snapshot changed bytes");
      byte[] changed = BsonLite.withProfileInt(a, "__snapshot_bench", 1);
      Files.write(profile, changed);
      long third = System.nanoTime();
      byte[] c = provider.snapshot(account, progress);
      long invalidatedMs = (System.nanoTime() - third) / 1000000;
      if (Arrays.equals(a, c)) throw new AssertionError("raw profile change did not invalidate snapshot cache");
      System.out.println("PASS snapshot bytes=" + a.length + " firstMs=" + firstMs + " cachedMs=" + secondMs + " invalidatedMs=" + invalidatedMs);
    } finally {
      try (java.util.stream.Stream<Path> walk = Files.walk(root)) {
        walk.sorted(java.util.Comparator.reverseOrder()).forEach(p -> { try { Files.deleteIfExists(p); } catch (Exception ignored) {} });
      }
    }
  }
}
