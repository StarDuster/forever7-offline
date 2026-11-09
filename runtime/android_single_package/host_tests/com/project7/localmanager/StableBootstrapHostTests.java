package com.project7.localmanager;

import android.content.Context;
import java.io.ByteArrayOutputStream;
import java.io.File;
import java.io.IOException;
import java.io.PrintStream;
import java.nio.file.Files;
import java.nio.file.Path;
import java.security.SecureRandom;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Properties;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicBoolean;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.concurrent.atomic.AtomicReference;

/** Finite synthetic storage only. No manager DEX, Android/game or real BSON. */
public final class StableBootstrapHostTests {
    private static int passed;
    private static void check(boolean value, String message) { if (!value) throw new AssertionError(message); }
    private static void done(String name) { passed++; System.out.println("PASS " + name); }
    private static final class Fixture implements AutoCloseable {
        final File root;
        final Context app;
        Fixture() throws Exception {
            HostStorage.reset(); HostControl.blockAt = null; HostControl.failAt = null;
            root = Files.createTempDirectory("p7-bootstrap-synthetic-").toFile(); app = new Context(root);
        }
        StableIdentityBootstrap bootstrap(StableIdentityBootstrap.Faults faults) {
            return new StableIdentityBootstrap("identity-profile-only-v1", null, new StockIdentityStorage(), faults, new SecureRandom());
        }
        StableIdentityBootstrap bootstrap() { return bootstrap(code -> {}); }
        StableIdentityBootstrap.PreparedIdentity prepare(StableIdentityBootstrap b) throws Exception {
            synchronized (GatewayService.SAVE_ACCESS) { return b.prepare(app); }
        }
        Properties journal() throws Exception { return HostStorage.read(new File(root, StableIdentityBootstrap.JOURNAL)); }
        String account() throws Exception { return journal().getProperty("account"); }
        public void close() throws Exception {
            try (java.util.stream.Stream<Path> files = Files.walk(root.toPath())) {
                for (Path p : (Iterable<Path>) files.sorted(java.util.Comparator.reverseOrder())::iterator) Files.deleteIfExists(p);
            }
            HostControl.storageMode = false;
        }
    }
    private static StableIdentityBootstrap.Faults once(String target) {
        AtomicBoolean fired = new AtomicBoolean();
        return code -> { if (target.equals(code) && fired.compareAndSet(false, true)) throw new IOException("synthetic interrupted stage"); };
    }
    private static void failure(Fixture f, StableIdentityBootstrap bootstrap) throws Exception {
        try { f.prepare(bootstrap); throw new AssertionError("bootstrap unexpectedly succeeded"); }
        catch (StableIdentityBootstrap.BootstrapException expected) { check(expected.getCause() == null, "raw cause exposed"); }
    }
    private static Map<String, byte[]> snapshot(File root) throws Exception {
        Map<String, byte[]> values = new LinkedHashMap<>();
        try (java.util.stream.Stream<Path> files = Files.walk(root.toPath())) {
            for (Path p : (Iterable<Path>) files.filter(Files::isRegularFile).sorted()::iterator)
                values.put(root.toPath().relativize(p).toString(), Files.readAllBytes(p));
        }
        return values;
    }
    private static void unchanged(Map<String, byte[]> before, File root) throws Exception {
        Map<String, byte[]> after = snapshot(root);
        check(before.keySet().equals(after.keySet()), "storage file set changed on rejection");
        for (String key : before.keySet()) check(Arrays.equals(before.get(key), after.get(key)), "storage bytes changed on rejection");
    }
    private static String delivered(StableIdentityBootstrap.Credentials credentials) throws Exception {
        AtomicReference<String> secret = new AtomicReference<>();
        credentials.deliver((name, generated) -> secret.set(generated)); return secret.get();
    }
    private static void freshAndRestart() throws Exception {
        try (Fixture f = new Fixture()) {
            StableIdentityBootstrap b = f.bootstrap();
            StableIdentityBootstrap.PreparedIdentity first = f.prepare(b);
            String account = first.identity().username(), secret = delivered(first.credentials());
            check(account.matches("offline_[0-9a-f]{24}") && account.length() <= 32, "invalid generated account");
            check(secret.matches("[0-9a-f]{64}"), "invalid generated secret");
            check(!first.postProfilePolicyApplied(), "profile-only pretended collection ready");
            check("READY".equals(f.journal().getProperty("phase")), "ready receipt missing");
            check(HostStorage.registrations == 1 && HostStorage.unexpectedAutoRegisters == 0, "fresh registration count wrong");
            StableIdentityBootstrap.PreparedIdentity second = f.prepare(f.bootstrap());
            check(second.identity().username().equals(account) && second.identity().numericId() == first.identity().numericId(), "identity rotated on restart");
            check(secret.equals(delivered(second.credentials())), "secret rotated on restart");
            check(!first.identity().generation().equals(second.identity().generation()), "preparation generation reused");
            check(HostStorage.registrations == 1, "restart registered another account");
            Properties progress = HostStorage.read(StableIdentityBootstrap.progress(f.root, account));
            check("1000".equals(progress.getProperty("availableEvents")) && "".equals(progress.getProperty("completedEvents")), "bootstrap skipped prologue");
        }
        done("fresh_generated_identity_profile_then_restart_same_credentials_and_uid");
    }
    private static void crashCheckpoints() throws Exception {
        for (String checkpoint : new String[]{"AFTER_IDENTITY_WRITTEN", "AFTER_REGISTER", "AFTER_ACCOUNT_BOUND", "AFTER_PROFILE_LOAD", "AFTER_TUTORIAL_SAVE", "AFTER_POST_PROFILE", "AFTER_READY"}) {
            try (Fixture f = new Fixture()) {
                StableIdentityBootstrap b = f.bootstrap(once(checkpoint)); failure(f, b);
                Properties prior = f.journal(); String account = prior.getProperty("account"), secret = prior.getProperty("secret");
                StableIdentityBootstrap.PreparedIdentity recovered = f.prepare(f.bootstrap());
                check(account.equals(recovered.identity().username()) && secret.equals(delivered(recovered.credentials())), "interruption regenerated identity");
                check(HostStorage.registrations == 1 && HostStorage.unexpectedAutoRegisters == 0, "recovery re-registered account");
                check("READY".equals(f.journal().getProperty("phase")), "recovery not committed");
            }
        }
        done("seven_interruption_checkpoints_resume_same_identity_and_bind_once");
    }
    private static void atomicInitialJournalRecovery() throws Exception {
        try (Fixture f = new Fixture()) {
            failure(f, f.bootstrap(once("BEFORE_JOURNAL_RENAME")));
            File temp = new File(f.root, StableIdentityBootstrap.JOURNAL + ".tmp");
            Properties pending = HostStorage.read(temp);
            check(!new File(f.root, StableIdentityBootstrap.JOURNAL).exists() && HostStorage.registrations == 0, "account before identity commit");
            StableIdentityBootstrap.PreparedIdentity result = f.prepare(f.bootstrap());
            check(pending.getProperty("account").equals(result.identity().username()) && pending.getProperty("secret").equals(delivered(result.credentials())), "atomic temp recovery rotated identity");
        }
        done("synced_initial_identity_temp_promoted_without_regeneration");
    }
    private static void partialAccountRegistration() throws Exception {
        try (Fixture f = new Fixture()) {
            HostStorage.fail = "after-account-write"; failure(f, f.bootstrap());
            String account = f.account();
            check(new File(f.root, "accounts.properties").isFile() && !new File(f.root, "account-ids.properties").exists(), "account/id crash boundary not reproduced");
            HostStorage.fail = null;
            StableIdentityBootstrap.PreparedIdentity result = f.prepare(f.bootstrap());
            check(account.equals(result.identity().username()) && HostStorage.registrations == 1, "partial account registration did not resume existing account");
            check(result.identity().numericId() > 0, "numeric identity not recovered");
        }
        done("account_committed_numeric_mapping_interruption_recovers_same_account");
    }
    private static void readyMissingFiles() throws Exception {
        for (String kind : new String[]{"accounts", "ids", "profile", "tutorial"}) {
            try (Fixture f = new Fixture()) {
                StableIdentityBootstrap b = f.bootstrap(); f.prepare(b); String account = f.account();
                File missing = kind.equals("accounts") ? new File(f.root, "accounts.properties") :
                    kind.equals("ids") ? new File(f.root, "account-ids.properties") :
                    kind.equals("profile") ? StableIdentityBootstrap.profile(f.root, account) : StableIdentityBootstrap.progress(f.root, account);
                Files.delete(missing.toPath()); Map<String, byte[]> before = snapshot(f.root); int opened = HostStorage.accountConstructions;
                failure(f, b); unchanged(before, f.root);
                check(HostStorage.accountConstructions == opened, "READY missing file reached stock constructor");
                try { b.preparedIdentity(); throw new AssertionError("stale prepared getter remained available"); }
                catch (StableIdentityBootstrap.BootstrapException expected) {}
            }
        }
        done("ready_missing_account_id_profile_or_progress_fails_before_store_construction_without_writes");
    }
    private static void readyCorruptAndMismatch() throws Exception {
        for (String kind : new String[]{"numeric", "uid", "account", "progress", "credential-record"}) {
            try (Fixture f = new Fixture()) {
                f.prepare(f.bootstrap()); String account = f.account();
                File changed;
                Properties p;
                if (kind.equals("numeric")) {
                    changed = new File(f.root, "account-ids.properties"); p = HostStorage.read(changed); p.setProperty(account, "902");
                } else if (kind.equals("credential-record")) {
                    changed = new File(f.root, "accounts.properties"); p = HostStorage.read(changed); p.setProperty(account, "changed synthetic credential record");
                } else if (kind.equals("progress")) {
                    changed = StableIdentityBootstrap.progress(f.root, account); p = HostStorage.read(changed); p.remove("schemaVersion");
                } else {
                    changed = StableIdentityBootstrap.profile(f.root, account); p = HostStorage.read(changed);
                    p.setProperty(kind.equals("uid") ? "uid" : "account", kind.equals("uid") ? "902" : "different-synthetic-account");
                }
                HostStorage.write(changed, p); Map<String, byte[]> before = snapshot(f.root); int opened = HostStorage.accountConstructions;
                failure(f, f.bootstrap()); unchanged(before, f.root);
                check(HostStorage.accountConstructions == opened, "corrupt identity preflight opened store");
            }
        }
        done("ready_corrupt_progress_numeric_uid_account_and_record_mismatch_are_preserved");
    }
    private static void stockSnapshotRejectsBeforeCanonicalWrite() throws Exception {
        try (Fixture f = new Fixture()) {
            f.prepare(f.bootstrap()); String account = f.account();
            File file = StableIdentityBootstrap.profile(f.root, account); Properties p = HostStorage.read(file);
            p.setProperty("doc.heromgr", "synthetic nested corruption"); HostStorage.write(file, p);
            Map<String, byte[]> before = snapshot(f.root); int loads = HostStorage.profileLoads, saves = HostStorage.tutorialSaves, snapshots = HostStorage.snapshots;
            failure(f, f.bootstrap()); unchanged(before, f.root);
            check(HostStorage.snapshots > snapshots && HostStorage.profileLoads == loads && HostStorage.tutorialSaves == saves, "snapshot validation did not precede canonical loads");
        }
        done("stock_archive_snapshot_validation_rejects_nested_corruption_before_profile_progress_writes");
    }
    private static void missingProgressDuringPreparing() throws Exception {
        try (Fixture f = new Fixture()) {
            failure(f, f.bootstrap(once("AFTER_PROFILE_LOAD"))); String account = f.account();
            check(StableIdentityBootstrap.profile(f.root, account).isFile() && !StableIdentityBootstrap.progress(f.root, account).exists(), "profile/tutorial gap not reproduced");
            check("PROFILE_STARTED".equals(f.journal().getProperty("step")), "profile-started marker absent");
            Properties p = HostStorage.read(StableIdentityBootstrap.profile(f.root, account)); p.setProperty("name", "synthetic-player");
            HostStorage.write(StableIdentityBootstrap.profile(f.root, account), p);
            f.prepare(f.bootstrap());
            check("synthetic-player".equals(HostStorage.read(StableIdentityBootstrap.profile(f.root, account)).getProperty("name")), "recovery overwrote existing profile");
            check(StableIdentityBootstrap.progress(f.root, account).isFile(), "progress not saved after recovery");
        }
        done("preparing_profile_written_progress_missing_uses_stock_load_save_recovery");
    }
    private static void exactStockOrderAndPreservation() throws Exception {
        try (Fixture f = new Fixture()) {
            f.prepare(f.bootstrap()); String account = f.account();
            File tutorial = StableIdentityBootstrap.progress(f.root, account); Properties p = HostStorage.read(tutorial);
            p.setProperty("completedEvents", "7,2,9"); p.setProperty("week.commit", "synthetic-week-receipt");
            p.setProperty("economy.commit", "synthetic-economy-receipt");
            p.setProperty("event.day.7", "synthetic-day"); p.setProperty("event.completed.7", "2"); p.setProperty("patrol.fatigue.7", "12"); HostStorage.write(tutorial, p);
            HostStorage.calls.clear(); f.prepare(f.bootstrap());
            List<String> calls = new ArrayList<>(HostStorage.calls);
            check(calls.indexOf("archive.snapshot") < calls.indexOf("tutorial.load") && calls.indexOf("tutorial.load") < calls.indexOf("profile.load") && calls.indexOf("profile.load") < calls.indexOf("tutorial.save"), "stock validation/load/recovery/save order changed");
            p = HostStorage.read(tutorial);
            check("7,2,9".equals(p.getProperty("completedEvents")) && "synthetic-day".equals(p.getProperty("event.day.7")) && "2".equals(p.getProperty("event.completed.7")) && "12".equals(p.getProperty("patrol.fatigue.7")), "ordered or known dynamic Progress data lost");
            check("synthetic-week-receipt".equals(p.getProperty("week.commit")) && "synthetic-economy-receipt".equals(p.getProperty("economy.commit")), "bootstrap replaced stock receipts");
        }
        done("original_api_sequence_preserves_progress_order_known_dynamic_fields_and_recovery_receipts");
    }
    private static void postProfilePolicyAndRetry() throws Exception {
        try (Fixture f = new Fixture()) {
            AtomicInteger applications = new AtomicInteger();
            StableIdentityBootstrap.PostProfileInitializer hook = (app, identity, stores) -> {
                check(Thread.holdsLock(GatewayService.SAVE_ACCESS) && !GatewayService.isRunning() && stores.progress != null, "post initializer not stopped/formed");
                File receipt = new File(app.getFilesDir(), "synthetic-post-policy.receipt");
                if (!receipt.isFile()) { Files.write(receipt.toPath(), new byte[]{1}); applications.incrementAndGet(); }
            };
            StableIdentityBootstrap b = new StableIdentityBootstrap("synthetic-post-v1", hook, new StockIdentityStorage(), once("AFTER_POST_PROFILE"), new SecureRandom());
            failure(f, b); check("PREPARING".equals(f.journal().getProperty("phase")), "post failure published READY");
            StableIdentityBootstrap retry = new StableIdentityBootstrap("synthetic-post-v1", hook, new StockIdentityStorage(), code -> {}, new SecureRandom());
            StableIdentityBootstrap.PreparedIdentity result = f.prepare(retry);
            check(applications.get() == 1 && result.postProfilePolicyApplied(), "post policy retry ignored idempotent receipt");
            Map<String, byte[]> before = snapshot(f.root); failure(f, f.bootstrap()); unchanged(before, f.root);
        }
        done("explicit_versioned_post_profile_policy_required_before_receipt_and_retry_is_idempotent");
    }
    private static void credentialsNeverLoggedAndRealSecretVerified() throws Exception {
        try (Fixture f = new Fixture()) {
            StableIdentityBootstrap.PreparedIdentity result = f.prepare(f.bootstrap()); String secret = delivered(result.credentials());
            ByteArrayOutputStream bytes = new ByteArrayOutputStream(); PrintStream capture = new PrintStream(bytes, true, "UTF-8");
            capture.println(result); capture.println(result.credentials()); capture.println(result.identity());
            try { result.credentials().deliver((name, generated) -> { throw new IOException(generated); }); }
            catch (IOException expected) { expected.printStackTrace(capture); }
            check(!bytes.toString("UTF-8").contains(secret), "credential exposed by result/exception");
            Properties journal = f.journal(); journal.setProperty("secret", secret.equals(repeat('a',64)) ? repeat('b',64) : repeat('a',64));
            HostStorage.write(new File(f.root, StableIdentityBootstrap.JOURNAL), journal);
            int registrations = HostStorage.registrations, loads = HostStorage.profileLoads;
            failure(f, f.bootstrap());
            check(HostStorage.registrations == registrations && HostStorage.profileLoads == loads && HostStorage.unexpectedAutoRegisters == 0, "wrong secret created account or loaded profile");
        }
        try (Fixture f = new Fixture()) {
            StableIdentityBootstrap.PostProfileInitializer leaking = (app, identity, stores) -> {
                throw new IOException(f.journal().getProperty("secret"));
            };
            StableIdentityBootstrap b = new StableIdentityBootstrap("synthetic-error-redaction-v1", leaking,
                new StockIdentityStorage(), code -> {}, new SecureRandom());
            try { f.prepare(b); throw new AssertionError("expected post policy failure"); }
            catch (StableIdentityBootstrap.BootstrapException expected) {
                ByteArrayOutputStream bytes = new ByteArrayOutputStream();
                expected.printStackTrace(new PrintStream(bytes, true, "UTF-8"));
                check(!bytes.toString("UTF-8").contains(f.journal().getProperty("secret")), "post policy cause leaked secret");
            }
        }
        done("credential_handles_delivery_post_policy_errors_are_redacted_and_stock_auth_checks_secret");
    }
    private static String repeat(char value, int count) { char[] chars = new char[count]; Arrays.fill(chars, value); return new String(chars); }
    private static void unmanagedAndMalformedJournal() throws Exception {
        try (Fixture f = new Fixture()) {
            Properties p = new Properties(); p.setProperty("synthetic-existing", "not selected"); HostStorage.write(new File(f.root, "accounts.properties"), p);
            Map<String, byte[]> before = snapshot(f.root); failure(f, f.bootstrap()); unchanged(before, f.root);
            check(HostStorage.accountConstructions == 0, "unmanaged account auto-adopted");
        }
        try (Fixture f = new Fixture()) {
            failure(f, f.bootstrap(once("AFTER_IDENTITY_WRITTEN")));
            Properties journal = f.journal(); journal.setProperty("managerDex", "wrong-artifact"); HostStorage.write(new File(f.root, StableIdentityBootstrap.JOURNAL), journal);
            Map<String, byte[]> before = snapshot(f.root); failure(f, f.bootstrap()); unchanged(before, f.root);
            check(HostStorage.accountConstructions == 0, "wrong artifact opened store");
        }
        done("unmanaged_storage_or_malformed_backend_journal_never_selects_existing_account_or_regenerates");
    }
    private static void stoppedLockGate() throws Exception {
        try (Fixture f = new Fixture()) {
            try { f.bootstrap().prepare(f.app); throw new AssertionError("missing SAVE_ACCESS allowed"); }
            catch (StableIdentityBootstrap.BootstrapException expected) {}
            java.lang.reflect.Field field = GatewayService.class.getDeclaredField("RUNNING"); field.setAccessible(true);
            AtomicBoolean running = (AtomicBoolean) field.get(null); running.set(true);
            try { failure(f, f.bootstrap()); } finally { running.set(false); }
            check(snapshot(f.root).isEmpty(), "invalid owner gate wrote identity");
        }
        done("stopped_service_and_existing_save_access_lock_required_before_any_write");
    }
    private static void ownerHookIntegration() throws Exception {
        try (Fixture f = new Fixture()) {
            StableIdentityBootstrap bootstrap = f.bootstrap();
            SinglePackageGateway gateway = new SinglePackageGateway(new ProcessGatewayOwner(new ManagerLifecycleDriver(), 2000, 2000), null);
            gateway.start(f.app, true, bootstrap).get(3, TimeUnit.SECONDS);
            check(gateway.state() == SinglePackageGateway.State.READY && bootstrap.preparedIdentity().identity().numericId() > 0, "owner did not await bootstrap");
            check(!bootstrap.preparedIdentity().postProfilePolicyApplied(), "owner READY implied collection/game readiness");
            gateway.closeAsync().get(3, TimeUnit.SECONDS); gateway.drained().get(3, TimeUnit.SECONDS);
        }
        done("production_process_owner_prestart_hook_awaits_profile_receipt_before_owned_listener_ready");
    }
    public static void main(String[] args) throws Exception {
        freshAndRestart(); crashCheckpoints(); atomicInitialJournalRecovery(); partialAccountRegistration();
        readyMissingFiles(); readyCorruptAndMismatch(); stockSnapshotRejectsBeforeCanonicalWrite();
        missingProgressDuringPreparing(); exactStockOrderAndPreservation(); postProfilePolicyAndRetry();
        credentialsNeverLoggedAndRealSecretVerified(); unmanagedAndMalformedJournal(); stoppedLockGate(); ownerHookIntegration();
        System.out.println("HOST_BOOTSTRAP_TESTS_PASSED=" + passed);
    }
}
