package com.forever7.offline;

import java.io.File;
import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.StandardCopyOption;
import java.security.SecureRandom;
import java.util.Arrays;
import java.util.HashSet;
import java.util.Set;
import java.util.concurrent.atomic.AtomicBoolean;
import java.util.function.Consumer;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

/** Notification only. The random generation prevents stale launches, not hostile writers. */
public final class Project7RepairProtocol {
    public static final String LAUNCH = ".p7-launch.json";
    public static final String REQUEST = ".p7-repair-request.json";
    public static final int BYTES = 256;
    private static final Set<String> CODES = new HashSet<>(Arrays.asList(
        "resource_verify_failed", "unverified_activation", "resource_activation_failed",
        "resource_query_failed", "resource_query_exception", "resource_download_failed",
        "inactive_game_start", "startup_policy_install_failed"));
    private static final Pattern REQUEST_PATTERN = Pattern.compile(
        "\\{\"code\":\"([a-z_]+)\",\"generation\":\"([0-9a-f]{32})\",\"schema\":1\\}");
    private Project7RepairProtocol() { }
    public static final class Session {
        private final File documents;
        private final String generation;
        private final Consumer<String> notification;
        private final AtomicBoolean active = new AtomicBoolean(true);
        private Session(File documents, String generation, Consumer<String> notification) {
            this.documents = documents; this.generation = generation; this.notification = notification;
        }
        public boolean active() { return active.get(); }
        public void close() { active.set(false); }
        /** FileObserver event names never become paths; the one fixed request is reread. */
        public void inspect() {
            if (!active.get()) return;
            try {
                String text = read(new File(documents, REQUEST));
                Matcher match = REQUEST_PATTERN.matcher(text.trim());
                if (!match.matches() || !CODES.contains(match.group(1)) || !generation.equals(match.group(2))) return;
                if (active.compareAndSet(true, false)) notification.accept(match.group(1));
            } catch (IOException ignored) { /* A partial/missing/stale notification grants nothing. */ }
        }
    }
    public static Session create(File documents, Consumer<String> notification) throws IOException {
        if (documents == null || !documents.isDirectory() || notification == null) throw new IOException("Repair notification unavailable");
        byte[] nonce = new byte[16]; new SecureRandom().nextBytes(nonce);
        StringBuilder hex = new StringBuilder();
        for (byte value : nonce) hex.append(String.format(java.util.Locale.ROOT, "%02x", value & 255));
        String generation = hex.toString();
        // Old request is not evidence for this launch even if deletion is unavailable.
        Files.deleteIfExists(new File(documents, REQUEST).toPath());
        write(new File(documents, LAUNCH), "{\"generation\":\"" + generation + "\",\"schema\":1}");
        return new Session(documents, generation, notification);
    }
    static String read(File file) throws IOException {
        if (!file.isFile() || file.length() != BYTES) throw new IOException("Invalid notification size");
        byte[] bytes = new byte[BYTES];
        try (FileInputStream input = new FileInputStream(file)) {
            int at = 0, count;
            while (at < bytes.length && (count = input.read(bytes, at, bytes.length - at)) > 0) at += count;
            if (at != BYTES || input.read() != -1) throw new IOException("Invalid notification length");
        }
        for (byte value : bytes) if (value < 32 || value > 126) throw new IOException("Invalid notification encoding");
        return new String(bytes, StandardCharsets.US_ASCII);
    }
    static void write(File file, String json) throws IOException {
        byte[] body = json.getBytes(StandardCharsets.US_ASCII);
        if (body.length > BYTES) throw new IOException("Invalid notification payload");
        byte[] padded = new byte[BYTES]; Arrays.fill(padded, (byte)' '); System.arraycopy(body, 0, padded, 0, body.length);
        File temporary = new File(file.getParentFile(), file.getName() + ".tmp-" + java.util.UUID.randomUUID());
        try {
            try (FileOutputStream output = new FileOutputStream(temporary)) { output.write(padded); output.getFD().sync(); }
            Files.move(temporary.toPath(), file.toPath(), StandardCopyOption.ATOMIC_MOVE, StandardCopyOption.REPLACE_EXISTING);
        } finally { Files.deleteIfExists(temporary.toPath()); }
    }
}
