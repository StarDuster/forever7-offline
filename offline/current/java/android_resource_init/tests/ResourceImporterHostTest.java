import com.forever7.offline.ResourceImporter;
import java.io.*;
import java.nio.file.*;
import java.security.*;
import java.util.*;
import java.util.concurrent.*;
import java.util.concurrent.atomic.*;
import java.util.zip.*;

public final class ResourceImporterHostTest {
    static void check(boolean value, String message) { if (!value) throw new RuntimeException(message); }
    static String hash(byte[] bytes) throws Exception {
        StringBuilder out = new StringBuilder();
        for (byte b : MessageDigest.getInstance("SHA-256").digest(bytes)) out.append(String.format("%02x", b & 255));
        return out.toString();
    }
    static byte[] zip(String[] names, byte[][] values) throws Exception {
        ByteArrayOutputStream out = new ByteArrayOutputStream();
        try (ZipOutputStream z = new ZipOutputStream(out)) {
            for (int i = 0; i < names.length; i++) { z.putNextEntry(new ZipEntry(names[i])); z.write(values[i]); z.closeEntry(); }
        }
        return out.toByteArray();
    }
    static ResourceImporter.Cache cache() {
        return new ResourceImporter.Cache() {
            public boolean verified(ResourceImporter.Entry entry, File file) { return false; }
            public void remember(ResourceImporter.Entry entry, File file) { }
        };
    }
    interface Checked { void run() throws Exception; }
    static void refused(Checked work, String reason) throws Exception {
        try { work.run(); throw new RuntimeException("Unexpected acceptance: " + reason); }
        catch (IOException expected) { }
    }
    public static void main(String[] args) throws Exception {
        Path root = Files.createTempDirectory("f7-resource-host-");
        try {
            byte[] good = "original-npk-fixture".getBytes("UTF-8");
            ResourceImporter.Entry entry = new ResourceImporter.Entry("hero.npk", good.length, hash(good));
            List<ResourceImporter.Entry> manifest = Arrays.asList(entry);
            AtomicBoolean cancel = new AtomicBoolean();
            ResourceImporter.Progress progress = (n, b, t) -> { };
            try (ResourceImporter importer = new ResourceImporter(root.toFile(), manifest, cache(), cancel, progress)) {
                check(importer.missing(false).size() == 1, "initial missing");
                importer.importZip(new ByteArrayInputStream(zip(new String[]{"res/hero.npk"}, new byte[][]{good})));
                check(importer.missing(true).isEmpty(), "valid commit");
                refused(() -> importer.importZip(new ByteArrayInputStream(zip(new String[]{"hero.npk"}, new byte[][]{"corrupt".getBytes("UTF-8")}))), "hash mismatch");
                check(Arrays.equals(Files.readAllBytes(root.resolve("hero.npk")), good), "old valid data retained");
                byte[] bomb = new byte[1024 * 1024];
                refused(() -> importer.importZip(new ByteArrayInputStream(zip(new String[]{"hero.npk"}, new byte[][]{bomb}))), "unknown-size existing-file drain is bounded");
                refused(() -> importer.importZip(new ByteArrayInputStream(zip(new String[]{"../offline_progress.json"}, new byte[][]{good}))), "traversal");
                refused(() -> importer.importZip(new ByteArrayInputStream(zip(new String[]{"script.npk"}, new byte[][]{good}))), "script excluded");
                refused(() -> importer.importZip(new ByteArrayInputStream(zip(new String[]{"res/"}, new byte[][]{good}))), "directory payload");
                refused(() -> importer.importZip(new ByteArrayInputStream(zip(new String[]{"hero.npk", "res/hero.npk"}, new byte[][]{good, good}))), "duplicate normalized name");
            }
            Path separate = root.resolve("symlink-target"); Files.write(separate, good);
            Files.delete(root.resolve("hero.npk")); Files.createSymbolicLink(root.resolve("hero.npk"), separate);
            try (ResourceImporter importer = new ResourceImporter(root.toFile(), manifest, cache(), cancel, progress)) {
                refused(() -> importer.missing(true), "destination symlink");
            }
            Files.delete(root.resolve("hero.npk"));
            byte[] large = new byte[400000]; Arrays.fill(large, (byte)71);
            ResourceImporter.Entry big = new ResourceImporter.Entry("hero.npk", large.length, hash(large));
            byte[] archive = zip(new String[]{"hero.npk"}, new byte[][]{large});
            CountDownLatch reading = new CountDownLatch(1), release = new CountDownLatch(1);
            AtomicBoolean oldCancel = new AtomicBoolean(), newLock = new AtomicBoolean();
            AtomicReference<Throwable> failure = new AtomicReference<Throwable>();
            Thread oldWorker = new Thread(() -> {
                try (ResourceImporter importer = new ResourceImporter(root.toFile(), Arrays.asList(big), cache(), oldCancel,
                    (n, b, t) -> { reading.countDown(); try { release.await(); } catch (InterruptedException e) { throw new RuntimeException(e); } })) {
                    importer.importZip(new ByteArrayInputStream(archive)); failure.set(new RuntimeException("Old worker was not cancelled"));
                } catch (ResourceImporter.Cancelled expected) { } catch (Throwable error) { failure.set(error); }
            });
            Thread newWorker = new Thread(() -> {
                try (ResourceImporter importer = new ResourceImporter(root.toFile(), Arrays.asList(big), cache(), new AtomicBoolean(), progress)) {
                    newLock.set(true); importer.importZip(new ByteArrayInputStream(archive));
                    check(importer.missing(true).isEmpty(), "new worker completed after old cleanup");
                } catch (Throwable error) { failure.set(error); }
            });
            oldWorker.start(); check(reading.await(5, TimeUnit.SECONDS), "old worker started");
            newWorker.start(); Thread.sleep(150);
            check(!newLock.get(), "activity recreation cannot overlap old cleanup/writer");
            oldCancel.set(true); release.countDown(); oldWorker.join(5000); newWorker.join(5000);
            check(!oldWorker.isAlive() && !newWorker.isAlive(), "workers ended");
            if (failure.get() != null) throw new RuntimeException(failure.get());
            check(Arrays.equals(Files.readAllBytes(root.resolve("hero.npk")), large), "committed replacement intact");
            check(!Files.exists(root.resolve(".f7-import-hero.npk.part")), "no partial temporary left");
            System.out.println("10 resource import contracts passed; host only");
        } finally {
            try (java.util.stream.Stream<Path> files = Files.walk(root)) {
                files.sorted(Comparator.reverseOrder()).forEach(p -> { try { Files.deleteIfExists(p); } catch (IOException e) { throw new RuntimeException(e); } });
            }
        }
    }
}
