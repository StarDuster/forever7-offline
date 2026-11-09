package com.forever7.offline;

import java.io.*;
import java.security.MessageDigest;
import java.util.*;
import java.util.concurrent.atomic.AtomicBoolean;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.locks.ReentrantLock;
import java.util.zip.ZipEntry;
import java.util.zip.ZipInputStream;

/** Bounded, manifest-pinned regular-file import. Never extracts archive paths. */
public final class ResourceImporter implements Closeable {
    private static final ReentrantLock SESSION_LOCK = new ReentrantLock();
    private boolean locked;
    public static final class Entry {
        public final String name, sha256;
        public final long bytes;
        public Entry(String name, long bytes, String sha256) {
            if (!name.matches("(?:[A-Za-z0-9_]+\\.npk|sound/(?:[A-Za-z0-9_.-]+/)*[A-Za-z0-9_.-]+)") || name.equals("script.npk") || name.contains("/../") || name.contains("/./") || bytes <= 0 ||
                    !sha256.matches("[0-9a-f]{64}")) throw new IllegalArgumentException("Invalid bundled manifest");
            this.name = name; this.bytes = bytes; this.sha256 = sha256;
        }
    }
    public interface Cache {
        boolean verified(Entry entry, File file);
        void remember(Entry entry, File file);
        /** Drop cached trust after a failed content check so repair never skips a corrupt file. */
        default void invalidate(Entry entry) { }
    }
    public interface Progress { void update(String name, long bytes, long total); }
    public static final class Cancelled extends IOException { public Cancelled() { super("Import cancelled"); } }
    private final File directory;
    private final LinkedHashMap<String, Entry> entries = new LinkedHashMap<String, Entry>();
    private final Cache cache;
    private final AtomicBoolean cancelled;
    private final Progress progress;
    private static final long RESERVE = 16L * 1024 * 1024;

    public ResourceImporter(File directory, List<Entry> manifest, Cache cache,
                            AtomicBoolean cancelled, Progress progress) throws IOException {
        if ((!directory.isDirectory() && !directory.mkdirs()) || !directory.isDirectory())
            throw new IOException("Resource directory is unavailable");
        this.directory = directory.getCanonicalFile();
        this.cache = cache; this.cancelled = cancelled; this.progress = progress;
        for (Entry entry : manifest) if (entries.put(entry.name, entry) != null)
            throw new IOException("Duplicate bundled resource");
        if (entries.isEmpty()) throw new IOException("Empty bundled resource manifest");
        try {
            while (!SESSION_LOCK.tryLock(100, TimeUnit.MILLISECONDS)) checkpoint();
            locked = true;
            checkpoint();
        } catch (InterruptedException error) {
            Thread.currentThread().interrupt(); throw new IOException("Resource preparation interrupted", error);
        } catch (IOException error) { if (locked) close(); throw error; }
    }
    @Override public void close() { if (locked) { locked = false; SESSION_LOCK.unlock(); } }
    void checkpoint() throws Cancelled { if (cancelled.get()) throw new Cancelled(); }
    File path(String name) throws IOException {
        File result = new File(directory, name);
        if (!result.getParentFile().isDirectory() && !result.getParentFile().mkdirs()) throw new IOException("Cannot create resource directory");
        if (!result.getAbsoluteFile().equals(result.getCanonicalFile()))
            throw new IOException("Resource path is a symbolic link");
        return result;
    }
    static String hex(byte[] value) {
        StringBuilder result = new StringBuilder();
        for (byte b : value) result.append(String.format(Locale.US, "%02x", b & 255));
        return result.toString();
    }
    private static MessageDigest digest() throws IOException {
        try { return MessageDigest.getInstance("SHA-256"); }
        catch (java.security.NoSuchAlgorithmException error) { throw new IOException(error); }
    }
    public boolean verify(Entry entry, boolean force) throws IOException {
        checkpoint();
        File file = path(entry.name);
        if (!file.isFile()) return false;
        if (file.length() != entry.bytes) { cache.invalidate(entry); return false; }
        if (!force && cache.verified(entry, file)) return true;
        MessageDigest hash = digest();
        long bytes = 0;
        try (InputStream stream = new BufferedInputStream(new FileInputStream(file))) {
            byte[] buffer = new byte[128 * 1024];
            int n;
            while ((n = stream.read(buffer)) != -1) {
                checkpoint(); bytes += n; hash.update(buffer, 0, n);
                if (bytes > entry.bytes) { cache.invalidate(entry); return false; }
                progress.update(entry.name, bytes, entry.bytes);
            }
        }
        if (bytes != entry.bytes || !hex(hash.digest()).equals(entry.sha256)) {
            cache.invalidate(entry); return false;
        }
        cache.remember(entry, file);
        return true;
    }
    public void progress(String name,long done,long total) { progress.update(name,done,total); }
    public File destination(Entry entry) throws IOException { return path(entry.name); }
    public void committed(Entry entry) throws IOException { cache.remember(entry, path(entry.name)); }
    public List<String> missing(boolean force) throws IOException {
        List<String> missing = new ArrayList<String>();
        for (Entry entry : entries.values()) if (!verify(entry, force)) missing.add(entry.name);
        return missing;
    }
    public void removeInterruptedTemporaryFiles() throws IOException {
        for (Entry entry : entries.values()) {
            File temporary = path(entry.name + ".f7-import.part");
            if (temporary.exists() && !temporary.delete()) throw new IOException("Cannot remove interrupted import temporary file");
        }
    }
    public void importZip(InputStream source) throws IOException {
        importZip(source, false);
    }

    /** force=true re-hashes the on-disk target before deciding to skip a ZIP member.
     * The caller's explicit ZIP/retry path uses it so a stale mtime+size cache can
     * never hide a same-size damaged destination. Legacy callers keep the old
     * cache-assisted behavior. */
    public void importZip(InputStream source, boolean force) throws IOException {
        removeInterruptedTemporaryFiles();
        long required = 0;
        for (Entry entry : entries.values()) if (!verify(entry, false)) required += entry.bytes;
        if (directory.getUsableSpace() < required + RESERVE)
            throw new IOException("Not enough free space; required bytes: " + (required + RESERVE));
        Set<String> seen = new HashSet<String>();
        try (ZipInputStream zip = new ZipInputStream(new BufferedInputStream(source))) {
            ZipEntry member;
            while ((member = zip.getNextEntry()) != null) {
                checkpoint();
                String archiveName = member.getName();
                if (member.isDirectory() && archiveName.equals("res/")) {
                    if (zip.read() != -1) throw new IOException("Archive directory contains data");
                    zip.closeEntry(); continue;
                }
                String name = entries.containsKey(archiveName) ? archiveName : archiveName.startsWith("res/") ? archiveName.substring(4) : archiveName;
                Entry entry = entries.get(name);
                if (entry == null || member.isDirectory() || !seen.add(name) ||
                        !(archiveName.equals(name) || archiveName.equals("res/" + name)))
                    throw new IOException("Unexpected or duplicate archive entry: " + archiveName);
                if (member.getSize() > entry.bytes) throw new IOException("Oversized archive entry: " + name);
                if (verify(entry, force)) {
                    // closeEntry alone drains unbounded compressed data and
                    // cannot check cancellation. Validate skipped bytes too.
                    MessageDigest skippedHash = digest();
                    long skipped = 0;
                    byte[] skipBuffer = new byte[128 * 1024];
                    int n;
                    while ((n = zip.read(skipBuffer)) != -1) {
                        checkpoint(); skipped += n;
                        if (skipped > entry.bytes) throw new IOException("Oversized existing resource entry: " + name);
                        skippedHash.update(skipBuffer, 0, n);
                        progress.update(name, skipped, entry.bytes);
                    }
                    if (skipped != entry.bytes || !hex(skippedHash.digest()).equals(entry.sha256))
                        throw new IOException("Skipped archive resource hash/size mismatch: " + name);
                    zip.closeEntry(); continue;
                }
                File temporary = path(name + ".f7-import.part");
                File destination = path(name);
                try {
                    MessageDigest hash = digest();
                    long bytes = 0;
                    try (FileOutputStream output = new FileOutputStream(temporary)) {
                        byte[] buffer = new byte[128 * 1024];
                        int n;
                        while ((n = zip.read(buffer)) != -1) {
                            checkpoint(); bytes += n;
                            if (bytes > entry.bytes) throw new IOException("Oversized resource: " + name);
                            output.write(buffer, 0, n); hash.update(buffer, 0, n);
                            progress.update(name, bytes, entry.bytes);
                        }
                        output.getFD().sync();
                    }
                    checkpoint();
                    if (bytes != entry.bytes || !hex(hash.digest()).equals(entry.sha256))
                        throw new IOException("Resource hash/size mismatch: " + name);
                    // Same filesystem rename atomically replaces the old file;
                    // never delete a possibly usable old destination first.
                    if (!temporary.renameTo(destination)) throw new IOException("Cannot commit verified resource: " + name);
                    cache.remember(entry, destination);
                } finally { if (temporary.exists()) temporary.delete(); }
                zip.closeEntry();
            }
        }
    }
}
