package com.project7.localmanager;

import android.content.Context;
import java.io.ByteArrayOutputStream;
import java.io.File;
import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.StandardCopyOption;
import java.security.MessageDigest;
import java.security.SecureRandom;
import java.util.HashSet;
import java.util.Properties;
import java.util.Set;

/** Stable app-private identity/profile preparation, NOT resource/login/game readiness.
 * Invoke only as the process owner's stopped SAVE_ACCESS prestart hook.
 */
public final class StableIdentityBootstrap implements SinglePackageGateway.PreStartInitializer {
    static final String ARTIFACT = "087656832b8150984c81c997c7c1f3966da22902c5226b0f6ef2f3e71d602325";
    static final String JOURNAL = "p7-bootstrap/identity.properties";
    private static final String NO_POST_POLICY = "identity-profile-only-v1";
    private final String policy;
    private final PostProfileInitializer postProfile;
    private final Storage storage;
    private final Faults faults;
    private final SecureRandom random;
    private volatile PreparedIdentity prepared;

    public interface PostProfileInitializer {
        /** Stopped, SAVE_ACCESS held. Must be versioned/idempotent across interrupted retries. */
        void initialize(Context app, Identity identity, Stores stores) throws Exception;
    }
    public interface CredentialReceiver { void accept(String username, String generatedSecret) throws Exception; }
    public static final class Identity {
        private final String username;
        private final int numericId;
        private final String generation;
        Identity(String username, int numericId, String generation) {
            this.username = username; this.numericId = numericId; this.generation = generation;
        }
        public String username() { return username; }
        public int numericId() { return numericId; }
        /** Opaque preparation-attempt nonce for session-scoped native handoff. */
        public String generation() { return generation; }
        @Override public String toString() { return "Identity[app-private]"; }
    }
    public static final class Credentials {
        private final Identity identity;
        private final String secret;
        Credentials(Identity identity, String secret) { this.identity = identity; this.secret = secret; }
        public Identity identity() { return identity; }
        public void deliver(CredentialReceiver receiver) throws IOException {
            try { receiver.accept(identity.username, secret); }
            catch (Throwable ignored) { throw new BootstrapException("CREDENTIAL_DELIVERY_FAILED"); }
        }
        @Override public String toString() { return "Credentials[redacted]"; }
    }
    /** Same-package post-profile adapters use these original stores/progress.
     * This object does not grant any collection or claim gameplay readiness.
     */
    public static final class Stores {
        final LocalAccountStore accounts;
        final LocalTutorialStore tutorials;
        final LocalProfileStore profiles;
        LocalTutorialStore.Progress progress;
        Stores(LocalAccountStore accounts, LocalTutorialStore tutorials, LocalProfileStore profiles) {
            this.accounts = accounts; this.tutorials = tutorials; this.profiles = profiles;
        }
        /** The original prepared store, for the owner's session-scoped handoff; never profile bytes. */
        LocalProfileStore profiles() { return profiles; }
    }
    public static final class PreparedIdentity {
        private final Credentials credentials;
        private final String postPolicy;
        PreparedIdentity(Credentials credentials, String postPolicy) { this.credentials = credentials; this.postPolicy = postPolicy; }
        public Credentials credentials() { return credentials; }
        public Identity identity() { return credentials.identity(); }
        public boolean postProfilePolicyApplied() { return !NO_POST_POLICY.equals(postPolicy); }
        public String postProfilePolicy() { return postPolicy; }
        @Override public String toString() { return "PreparedIdentity[profile-only; credentials redacted]"; }
    }
    public static final class BootstrapException extends IOException {
        private final String code;
        private BootstrapException(String code) { super("Stable bootstrap: " + code); this.code = code; }
        public String code() { return code; }
    }
    interface Storage {
        Object saveAccess();
        boolean stopped();
        Stores open(Context app) throws Exception;
        boolean contains(Stores stores, String account) throws Exception;
        int register(Stores stores, String account, String secret) throws Exception;
        void authenticateExisting(Stores stores, String account, String secret) throws Exception;
        int numericId(Stores stores, String account) throws Exception;
        LocalTutorialStore.Progress loadProgress(Stores stores, String account) throws Exception;
        void loadProfile(Stores stores, String account, LocalTutorialStore.Progress progress) throws Exception;
        void saveProgress(Stores stores, String account, LocalTutorialStore.Progress progress) throws Exception;
        void validateSnapshot(Context app, Stores stores, String account) throws Exception;
        void verifyProfileIdentity(byte[] profile, String account, int uid) throws Exception;
    }
    interface Faults { void checkpoint(String code) throws Exception; }
    private static final Faults NO_FAULTS = code -> {};

    public static StableIdentityBootstrap identityAndProfileOnly() {
        return new StableIdentityBootstrap(NO_POST_POLICY, null, new StockIdentityStorage(), NO_FAULTS, new SecureRandom());
    }
    public static StableIdentityBootstrap withPostProfile(String policy, PostProfileInitializer initializer) {
        if (policy == null || !policy.matches("[A-Za-z0-9_.-]{1,80}") || NO_POST_POLICY.equals(policy) || initializer == null)
            throw new IllegalArgumentException("Explicit versioned post-profile policy and initializer required");
        return new StableIdentityBootstrap(policy, initializer, new StockIdentityStorage(), NO_FAULTS, new SecureRandom());
    }
    StableIdentityBootstrap(String policy, PostProfileInitializer initializer, Storage storage, Faults faults, SecureRandom random) {
        this.policy = policy; this.postProfile = initializer; this.storage = storage; this.faults = faults; this.random = random;
    }
    @Override public void initialize(Context app) throws IOException { prepare(app); }
    public PreparedIdentity preparedIdentity() throws IOException {
        PreparedIdentity result = prepared;
        if (result == null) throw new BootstrapException("NO_SUCCESSFUL_PROFILE_PREPARATION");
        return result;
    }
    public synchronized PreparedIdentity prepare(Context context) throws IOException {
        prepared = null;
        String stage = "STOPPED_OWNER_REQUIRED";
        try {
            if (!Thread.holdsLock(storage.saveAccess()) || !storage.stopped()) throw new BootstrapException(stage);
            Context app = context == null ? null : context.getApplicationContext();
            if (app == null || app.getFilesDir() == null) throw new BootstrapException("APPLICATION_CONTEXT_REQUIRED");
            File root = app.getFilesDir();
            stage = "READ_IDENTITY_JOURNAL";
            Record record = readOrCreate(root);
            boolean committed = record.ready();
            stage = "READ_ONLY_PREFLIGHT";
            preflight(root, record, committed);
            faults.checkpoint("AFTER_PREFLIGHT");
            stage = "OPEN_STOCK_STORES";
            Stores stores = storage.open(app);
            if (!storage.stopped()) throw new BootstrapException("SERVICE_BECAME_ACTIVE");
            stage = "ACCOUNT_REGISTER_OR_RESUME";
            if (!storage.contains(stores, record.account)) {
                if (committed || record.uid != 0 || !"IDENTITY_WRITTEN".equals(record.step))
                    throw new BootstrapException("BOUND_ACCOUNT_MISSING");
                storage.register(stores, record.account, record.secret);
                faults.checkpoint("AFTER_REGISTER");
            }
            stage = "VERIFY_GENERATED_CREDENTIALS";
            storage.authenticateExisting(stores, record.account, record.secret);
            stage = "BIND_NUMERIC_ID";
            int uid = storage.numericId(stores, record.account);
            if (uid <= 0 || (record.uid != 0 && uid != record.uid)) throw new BootstrapException("NUMERIC_ID_MISMATCH");
            record.uid = uid;
            String accountHash = accountFingerprint(root, record.account);
            if (record.accountHash != null && !record.accountHash.equals(accountHash)) throw new BootstrapException("ACCOUNT_RECORD_CHANGED");
            record.accountHash = accountHash;
            if (!committed && "IDENTITY_WRITTEN".equals(record.step)) {
                record.step = "ACCOUNT_BOUND"; write(root, record); faults.checkpoint("AFTER_ACCOUNT_BOUND");
            }
            // Full stock validators are called before any canonical load/save
            // when a profile already exists. PREPARING may lack tutorial only.
            stage = "VALIDATE_EXISTING_STOCK_SNAPSHOT";
            if (profile(root, record.account).isFile()) storage.validateSnapshot(app, stores, record.account);
            if (!committed && !"PROFILE_SAVED".equals(record.step)) {
                record.step = "PROFILE_STARTED"; write(root, record);
            }
            stage = "ORIGINAL_TUTORIAL_LOAD";
            stores.progress = storage.loadProgress(stores, record.account);
            stage = "ORIGINAL_PROFILE_LOAD_RECOVERY";
            storage.loadProfile(stores, record.account, stores.progress);
            faults.checkpoint("AFTER_PROFILE_LOAD");
            stage = "ORIGINAL_TUTORIAL_SAVE";
            storage.saveProgress(stores, record.account, stores.progress);
            faults.checkpoint("AFTER_TUTORIAL_SAVE");
            if (!committed) { record.step = "PROFILE_SAVED"; write(root, record); }
            stage = "POST_PROFILE_POLICY";
            Identity identity = new Identity(record.account, record.uid, randomHex(16));
            if (postProfile != null) postProfile.initialize(app, identity, stores);
            faults.checkpoint("AFTER_POST_PROFILE");
            stage = "VALIDATE_FINAL_PROFILE_AND_PROGRESS";
            preflight(root, record, true);
            storage.validateSnapshot(app, stores, record.account);
            if (!storage.stopped()) throw new BootstrapException("SERVICE_BECAME_ACTIVE");
            stage = "COMMIT_PROFILE_READY_RECEIPT";
            record.phase = "READY"; record.step = "PROFILE_SAVED";
            write(root, record); faults.checkpoint("AFTER_READY");
            PreparedIdentity result = new PreparedIdentity(new Credentials(identity, record.secret), record.policy);
            prepared = result;
            return result;
        } catch (BootstrapException error) { throw error; }
        catch (Throwable ignored) {
            // Stock/plugin exception messages and causes may contain credentials.
            // Preserve files, return only a fixed stage code, never attach cause.
            throw new BootstrapException(stage + "_FAILED");
        }
    }
    private Record readOrCreate(File root) throws Exception {
        File journal = new File(root, JOURNAL), temporary = new File(root, JOURNAL + ".tmp");
        if (journal.isFile()) return Record.read(properties(journal, 65536), policy);
        if (journal.exists()) throw new BootstrapException("JOURNAL_NOT_REGULAR_FILE");
        requireVirgin(root);
        if (temporary.exists()) {
            Record interrupted = Record.read(properties(temporary, 65536), policy);
            if (interrupted.ready() || interrupted.uid != 0 || !"IDENTITY_WRITTEN".equals(interrupted.step))
                throw new BootstrapException("UNRECOGNIZED_ORPHAN_JOURNAL");
            Files.move(temporary.toPath(), journal.toPath(), StandardCopyOption.ATOMIC_MOVE);
            return interrupted;
        }
        Record fresh = new Record(); fresh.account = "offline_" + randomHex(12);
        fresh.secret = randomHex(32); fresh.policy = policy;
        write(root, fresh); faults.checkpoint("AFTER_IDENTITY_WRITTEN");
        return fresh;
    }
    private String randomHex(int bytes) { byte[] value = new byte[bytes]; random.nextBytes(value); return hex(value); }
    static String hex(byte[] value) {
        StringBuilder result = new StringBuilder(value.length * 2);
        for (byte part : value) result.append(String.format(java.util.Locale.ROOT, "%02x", part & 255));
        return result.toString();
    }
    static String digest(String value) throws Exception {
        return hex(MessageDigest.getInstance("SHA-256").digest(value.getBytes("UTF-8")));
    }
    static File profile(File root, String account) { return new File(new File(root, "profiles"), account + ".bson"); }
    static File progress(File root, String account) { return new File(new File(root, "tutorials"), account + ".properties"); }
    private void requireVirgin(File root) throws IOException {
        for (String name : new String[]{"accounts.properties", "accounts.properties.tmp", "account-ids.properties", "account-ids.properties.tmp", "profiles", "tutorials", "save-transactions"}) {
            File file = new File(root, name);
            if (file.isDirectory()) {
                String[] children = file.list();
                if (children == null || children.length != 0) throw new BootstrapException("UNMANAGED_STORAGE_WITHOUT_IDENTITY");
            } else if (file.exists()) throw new BootstrapException("UNMANAGED_STORAGE_WITHOUT_IDENTITY");
        }
    }
    private static final String[] PROGRESS_KEYS = {"schemaVersion", "availableEvents", "processingEvents", "completedEvents",
        "initPrologue", "processingNewbees", "finishedNewbees", "inEmergency", "status", "scene", "patrol.count",
        "patrol.area", "patrol.day", "patrol.actions", "patrol.sandglass", "economy.commit", "week.commit", "week.index",
        "patrol.favor", "patrol.rewardPending", "patrol.heroes", "patrol.events", "patrol.replays"};
    private void preflight(File root, Record r, boolean strict) throws Exception {
        File accountsFile = new File(root, "accounts.properties"), idsFile = new File(root, "account-ids.properties");
        Properties accounts = accountsFile.exists() ? properties(accountsFile, 4194304) : new Properties();
        Properties ids = idsFile.exists() ? properties(idsFile, 4194304) : new Properties();
        for (String name : accounts.stringPropertyNames()) {
            if (!name.matches("[A-Za-z0-9_.-]{1,32}") || accounts.getProperty(name).isEmpty())
                throw new BootstrapException("MALFORMED_ACCOUNT_REGISTRY");
        }
        Set<Integer> assigned = new HashSet<>();
        for (String name : ids.stringPropertyNames()) {
            int value = Integer.parseInt(ids.getProperty(name));
            if (!name.matches("[A-Za-z0-9_.-]{1,32}") || value <= 0 || value == Integer.MAX_VALUE || !assigned.add(value)) throw new BootstrapException("MALFORMED_NUMERIC_ID_REGISTRY");
        }
        boolean present = accounts.containsKey(r.account);
        if (!present && ids.containsKey(r.account)) throw new BootstrapException("ORPHAN_NUMERIC_ID");
        if (strict || r.uid != 0) {
            if (!accountsFile.isFile() || !idsFile.isFile() || !present) throw new BootstrapException("COMMITTED_ACCOUNT_FILES_MISSING");
            if (!Integer.toString(r.uid).equals(ids.getProperty(r.account))) throw new BootstrapException("NUMERIC_ID_MISMATCH");
            if (r.accountHash == null || !r.accountHash.equals(digest(accounts.getProperty(r.account))))
                throw new BootstrapException("ACCOUNT_RECORD_CHANGED");
        }
        File profile = profile(root, r.account), tutorial = progress(root, r.account);
        if (strict || "PROFILE_SAVED".equals(r.step)) {
            if (!profile.isFile() || !tutorial.isFile()) throw new BootstrapException("COMMITTED_PROFILE_FILES_MISSING");
        }
        if ((profile.exists() || tutorial.exists()) && r.uid == 0) throw new BootstrapException("UNBOUND_PROFILE_FILES");
        if (tutorial.exists() && !profile.isFile()) throw new BootstrapException("PROGRESS_WITHOUT_PROFILE");
        if (profile.exists()) storage.verifyProfileIdentity(bytes(profile, 33554432), r.account, r.uid);
        if (tutorial.exists()) {
            Properties p = properties(tutorial, 4194304);
            for (String key : PROGRESS_KEYS) if (!p.containsKey(key)) throw new BootstrapException("INCOMPLETE_PROGRESS_SCHEMA");
            if (!"2".equals(p.getProperty("schemaVersion"))) throw new BootstrapException("PROGRESS_SCHEMA_MISMATCH");
            for (String key : new String[]{"initPrologue", "inEmergency", "patrol.rewardPending"})
                if (!"true".equals(p.getProperty(key)) && !"false".equals(p.getProperty(key)))
                    throw new BootstrapException("MALFORMED_PROGRESS_BOOLEAN");
            for (String key : new String[]{"patrol.count", "patrol.area", "patrol.actions", "patrol.sandglass", "week.index", "patrol.favor"})
                Integer.parseInt(p.getProperty(key));
        }
    }
    private String accountFingerprint(File root, String account) throws Exception {
        Properties accounts = properties(new File(root, "accounts.properties"), 4194304);
        String record = accounts.getProperty(account);
        if (record == null || record.isEmpty()) throw new BootstrapException("ACCOUNT_RECORD_MISSING");
        return digest(record);
    }
    static byte[] bytes(File file, int limit) throws IOException {
        if (!file.isFile() || file.length() <= 0 || file.length() > limit) throw new BootstrapException("INVALID_FILE_SIZE_OR_TYPE");
        try (FileInputStream input = new FileInputStream(file); ByteArrayOutputStream output = new ByteArrayOutputStream()) {
            byte[] buffer = new byte[8192]; int count;
            while ((count = input.read(buffer)) != -1) {
                if (output.size() + count > limit) throw new BootstrapException("FILE_SIZE_LIMIT");
                output.write(buffer, 0, count);
            }
            return output.toByteArray();
        }
    }
    static Properties properties(File file, int limit) throws IOException {
        Properties p = new Properties();
        try { p.load(new java.io.ByteArrayInputStream(bytes(file, limit))); }
        catch (IllegalArgumentException ignored) { throw new BootstrapException("MALFORMED_PROPERTIES"); }
        return p;
    }
    private void write(File root, Record r) throws Exception {
        File destination = new File(root, JOURNAL), temp = new File(root, JOURNAL + ".tmp");
        File directory = destination.getParentFile();
        if (!directory.isDirectory() && !directory.mkdirs()) throw new BootstrapException("JOURNAL_DIRECTORY_UNAVAILABLE");
        try (FileOutputStream output = new FileOutputStream(temp)) {
            if (!temp.setReadable(false, false) || !temp.setWritable(false, false) ||
                    !temp.setReadable(true, true) || !temp.setWritable(true, true))
                throw new BootstrapException("PRIVATE_JOURNAL_PERMISSIONS_FAILED");
            r.properties().store(output, "App-private bootstrap identity; do not export");
            output.getFD().sync();
        }
        faults.checkpoint("BEFORE_JOURNAL_RENAME");
        Files.move(temp.toPath(), destination.toPath(), StandardCopyOption.ATOMIC_MOVE, StandardCopyOption.REPLACE_EXISTING);
    }
    private static final class Record {
        String account, secret, policy, accountHash;
        String phase = "PREPARING", step = "IDENTITY_WRITTEN";
        int uid;
        boolean ready() { return "READY".equals(phase); }
        Properties properties() {
            Properties p = new Properties(); p.setProperty("schema", "1"); p.setProperty("backend", "project7");
            p.setProperty("managerDex", ARTIFACT); p.setProperty("account", account); p.setProperty("secret", secret);
            p.setProperty("phase", phase); p.setProperty("step", step); p.setProperty("postProfilePolicy", policy);
            if (uid != 0) p.setProperty("numericId", Integer.toString(uid));
            if (accountHash != null) p.setProperty("accountRecordSha256", accountHash);
            return p;
        }
        static Record read(Properties p, String policy) throws IOException {
            if (!"1".equals(p.getProperty("schema")) || !"project7".equals(p.getProperty("backend")) ||
                    !ARTIFACT.equals(p.getProperty("managerDex")) || !policy.equals(p.getProperty("postProfilePolicy")))
                throw new BootstrapException("JOURNAL_SCHEMA_BACKEND_OR_POLICY_MISMATCH");
            Record r = new Record(); r.account = p.getProperty("account", ""); r.secret = p.getProperty("secret", "");
            r.phase = p.getProperty("phase", ""); r.step = p.getProperty("step", ""); r.policy = policy;
            if (!r.account.matches("offline_[0-9a-f]{24}") || !r.secret.matches("[0-9a-f]{64}") ||
                    !("PREPARING".equals(r.phase) || "READY".equals(r.phase)) ||
                    !("IDENTITY_WRITTEN".equals(r.step) || "ACCOUNT_BOUND".equals(r.step) || "PROFILE_STARTED".equals(r.step) || "PROFILE_SAVED".equals(r.step)))
                throw new BootstrapException("MALFORMED_IDENTITY_JOURNAL");
            try { r.uid = Integer.parseInt(p.getProperty("numericId", "0")); }
            catch (NumberFormatException ignored) { throw new BootstrapException("MALFORMED_JOURNAL_NUMERIC_ID"); }
            r.accountHash = p.getProperty("accountRecordSha256");
            if (r.uid < 0 || (r.accountHash != null && !r.accountHash.matches("[0-9a-f]{64}")) ||
                    (!"IDENTITY_WRITTEN".equals(r.step) && (r.uid == 0 || r.accountHash == null)) ||
                    (r.ready() && !"PROFILE_SAVED".equals(r.step)))
                throw new BootstrapException("INCOMPLETE_IDENTITY_BINDING");
            return r;
        }
    }
}
