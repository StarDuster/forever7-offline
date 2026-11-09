package com.project7.localmanager;

import android.content.Context;
import android.content.res.AssetManager;
import com.forever7.offline.Project7RepairHost;
import com.forever7.offline.ResourceImporter;
import com.netease.qrzd.AutoLoginCore;
import java.io.File;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.LinkOption;
import java.nio.file.DirectoryStream;
import java.nio.file.Path;
import java.util.ArrayDeque;
import java.util.ArrayList;
import java.util.Deque;
import java.util.List;
import java.util.UUID;
import java.util.concurrent.CompletableFuture;
import java.util.concurrent.atomic.AtomicBoolean;
import java.util.function.Consumer;

/**
 * Real v62 production coordinator + real StableIdentityBootstrap prepared identity + real
 * AutoLoginCore credential delivery. Only the resource publication receipt, repair observer and
 * manager process owner are host leaves; they are named in the emitted evidence.
 *
 * This does not run Android ART, DEX, an APK, the game or native code.
 */
public final class StartupCredentialBindingHost {
    private static int passed;
    private static final String HASH = "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb";
    private static final String POLICY = FullCollectionInitializer.POLICY;

    private static void check(boolean value, String message) {
        if (!value) throw new AssertionError(message);
    }
    private static void done(String name) {
        passed++;
        System.out.println("PASS " + name);
    }

    /** Same JSON escaping as AutoLoginCore.quote, which is package-private to com.netease.qrzd. */
    private static String quote(String value) {
        StringBuilder out = new StringBuilder("\"");
        for (int i = 0; i < value.length(); i++) {
            char c = value.charAt(i);
            if (c == '\\' || c == '"') out.append('\\').append(c);
            else if (c < 32) out.append(String.format("\\u%04x", (int) c));
            else out.append(c);
        }
        return out.append('"').toString();
    }

    private static final List<File> TEMPORARIES = new ArrayList<>();
    private static File temporary(String prefix) throws IOException {
        File root = Files.createTempDirectory(prefix).toFile();
        TEMPORARIES.add(root);
        return root;
    }
    private static void remove(Path path) throws IOException {
        if (Files.isDirectory(path, LinkOption.NOFOLLOW_LINKS)) {
            try (DirectoryStream<Path> children = Files.newDirectoryStream(path)) {
                for (Path child : children) remove(child);
            }
        }
        Files.deleteIfExists(path);
    }
    private static void cleanup() {
        for (File root : TEMPORARIES) {
            try { remove(root.toPath()); } catch (IOException ignored) { }
        }
        TEMPORARIES.clear();
    }

    private static void prepareProductionPolicies(Context app) throws Exception {
        CoreDrawPolicy.prepare(app);
        HistoryDrawPolicy.prepare(app);
        SelectorPolicy.prepare(app);
        DynamicDrawPolicy.prepare(app);
        WishGateway.prepare(app);
        StoryMissionBridge.prepare(app);
        StoryCityBootstrap.prepare(app);
        TrialRetryGateway.prepare(app);
        OfflineMechanismGateway.prepare(app);
        System.out.println("PREPARE PASS nine production prepare calls");
    }

    /** Mirrors Project7StartupPlatform.OwnedBackend for identity and credential delivery. */
    static final class HostBackend implements Project7StartupCoordinator.Backend {
        final Context app;
        final Project7StartupCoordinator.Guard guard;
        final StableIdentityBootstrap bootstrap;
        final CompletableFuture<Void> drained = new CompletableFuture<>();
        volatile StableIdentityBootstrap.PreparedIdentity identity;
        volatile AutoLoginCore.Credentials credentials;
        volatile boolean executed, ownerReady, failed;
        volatile String deliveryError;
        volatile boolean wrongUsername, zeroNumericId;
        volatile boolean throwFromReceiver;

        HostBackend(Context app, Project7StartupCoordinator.Guard guard, boolean profileOnly) {
            this.app = app;
            this.guard = guard;
            if (profileOnly) {
                bootstrap = StableIdentityBootstrap.identityAndProfileOnly();
            } else {
                bootstrap = StableIdentityBootstrap.withPostProfile(POLICY, (context, bound, stores) -> {
                    new FullCollectionInitializer(guard::cancelled).initialize(context, bound, stores);
                    WishGateway.prepareStoppedProfile(stores.profiles, bound.username(), bound.numericId(), guard::cancelled);
                });
            }
        }

        public CompletableFuture<Void> start() {
            CompletableFuture<Void> ready = new CompletableFuture<>();
            try {
                executed = true;
                if (guard.cancelled()) throw new IOException("cancelled");
                StableIdentityBootstrap.PreparedIdentity prepared;
                // Production owner contract: stopped service, SAVE_ACCESS held for the whole preparation.
                synchronized (GatewayService.SAVE_ACCESS) {
                    prepared = bootstrap.prepare(app);
                }
                if (!prepared.postProfilePolicyApplied() || !POLICY.equals(prepared.postProfilePolicy()))
                    throw new IOException("collection policy not applied");
                if (zeroNumericId) {
                    // Injected synthetic identity, only for the coordinator numeric-id gate.
                    prepared = new StableIdentityBootstrap.PreparedIdentity(
                        new StableIdentityBootstrap.Credentials(
                            new StableIdentityBootstrap.Identity("offline_000000000000000000000000", 0, "synthetic"), "synthetic-secret"), POLICY);
                }
                prepared.credentials().deliver((username, secret) -> {
                    if (throwFromReceiver) throw new IOException("synthetic receiving native slot failure");
                    credentials = wrongUsername
                        ? new AutoLoginCore.Credentials("offline_ffffffffffffffffffffffff", secret)
                        : new AutoLoginCore.Credentials(username, secret);
                });
                identity = prepared;
                ownerReady = true;
                ready.complete(null);
            } catch (Throwable error) {
                failed = true;
                ownerReady = false;
                deliveryError = error.getClass().getSimpleName() + ":" + error.getMessage();
                ready.completeExceptionally(error);
            }
            return ready;
        }

        public boolean hookExecuted() { return executed; }
        public boolean ownerReady() { return ownerReady && !failed; }
        public boolean ownerFailed() { return failed; }
        public StableIdentityBootstrap.PreparedIdentity identity() { return identity; }
        public AutoLoginCore.Credentials credentials() { return credentials; }
        public void closeIfOwned() { failed = true; ownerReady = false; }
        public CompletableFuture<Void> drained() { return drained; }
    }

    static final class HostRepair implements Project7RepairHost.Lease {
        boolean active = true;
        public boolean active() { return active; }
        public void close() { active = false; }
        public void awaitDrain(CompletableFuture<Void> drained) {}
    }

    static final class HostServices implements Project7StartupCoordinator.Services {
        final Context app;
        final boolean profileOnly, wrongUsername, zeroNumericId, throwFromReceiver, publishFailure;
        final List<String> calls = new ArrayList<>();
        HostBackend latest;
        AutoLoginCore.SessionProvider provider;
        int installs, publications;
        HostRepair repair;

        HostServices(Context app, boolean profileOnly, boolean wrongUsername, boolean zeroNumericId,
                     boolean throwFromReceiver, boolean publishFailure) {
            this.app = app;
            this.profileOnly = profileOnly;
            this.wrongUsername = wrongUsername;
            this.zeroNumericId = zeroNumericId;
            this.throwFromReceiver = throwFromReceiver;
            this.publishFailure = publishFailure;
        }

        public boolean foreignOwnerActive() { return false; }
        public void installProvider(AutoLoginCore.SessionProvider source) { installs++; provider = source; }
        public String approvedPolicy() { return POLICY; }
        public Project7StartupCoordinator.Evidence publish(File documents, List<ResourceImporter.Entry> entries,
                AtomicBoolean cancel, Project7StartupCoordinator.Status status) throws Exception {
            calls.add("publish");
            publications++;
            if (publishFailure) throw new IOException("synthetic publication failure");
            // Host leaf: no 312-entry resource scan is executed by this credential-binding fixture.
            return new Project7StartupCoordinator.Evidence(new Object(), HASH, HASH, 312);
        }
        public Project7StartupCoordinator.Backend backend(Project7StartupCoordinator.Guard guard) {
            calls.add("backend");
            latest = new HostBackend(app, guard, profileOnly);
            latest.wrongUsername = wrongUsername;
            latest.zeroNumericId = zeroNumericId;
            latest.throwFromReceiver = throwFromReceiver;
            return latest;
        }
        public Project7RepairHost.Lease watchRepair(File documents, Consumer<Project7RepairHost.Lease> callback) {
            calls.add("watchRepair");
            repair = new HostRepair();
            return repair;
        }
    }

    private static Project7StartupCoordinator.Ticket run(Project7StartupCoordinator coordinator, File documents) throws Exception {
        Project7StartupCoordinator.Ticket ticket = coordinator.reserve(new AtomicBoolean(), null);
        coordinator.prepare(ticket, documents, new ArrayList<ResourceImporter.Entry>(), message -> {});
        return ticket;
    }

    private static final class AutoLoginReceiver {
        final Deque<Runnable> queue = new ArrayDeque<>();
        final List<String> values = new ArrayList<>();
        final List<Boolean> confirmed = new ArrayList<>();
        final List<String> statuses = new ArrayList<>();
        final AutoLoginCore core;
        AutoLoginReceiver(Project7StartupCoordinator coordinator) {
            core = new AutoLoginCore(queue::add, (value, ok) -> { values.add(value); confirmed.add(ok); },
                coordinator::currentSession, statuses::add);
        }
        void login() {
            core.show(new AutoLoginCore.Request("login", null, null), () -> true, true);
            while (!queue.isEmpty()) queue.remove().run();
        }
        String last() { return values.isEmpty() ? null : values.get(values.size() - 1); }
    }

    private static void reload(File assets, File documents, File root, String username, String secret) throws Exception {
        Context app = new Context(root, new AssetManager(assets));
        prepareProductionPolicies(app);
        HostServices services = new HostServices(app, false, false, false, false, false);
        Project7StartupCoordinator coordinator = new Project7StartupCoordinator(app, services);
        Project7StartupCoordinator.Ticket ticket = run(coordinator, documents);
        AutoLoginCore.Session session = coordinator.currentSession();
        check(session != null && session.credentials.username.equals(username) && session.credentials.secret.equals(secret),
            "reload changed the prepared account or generated secret");
        AutoLoginReceiver login = new AutoLoginReceiver(coordinator);
        login.login();
        check(login.confirmed.size() == 1 && login.confirmed.get(0), "reload AutoLogin did not submit");
        check(login.last().contains("\"username\":" + quote(username)), "reload AutoLogin username changed");
        check(login.last().contains("\"password\":" + quote(secret)), "reload AutoLogin secret changed");
        done("coordinator_reload_over_same_journal_keeps_identity_secret_and_autologin_delivery");
        coordinator.abandon(ticket);
    }

    private static void negativeProfileOnly(File assets, File documents) throws Exception {
        File root = temporary("p7-credential-profileonly-");
        Context app = new Context(root, new AssetManager(assets));
        prepareProductionPolicies(app);
        HostServices services = new HostServices(app, true, false, false, false, false);
        Project7StartupCoordinator coordinator = new Project7StartupCoordinator(app, services);
        boolean rejected = false;
        try { run(coordinator, documents); } catch (IOException expected) { rejected = true; }
        check(rejected, "profile-only preparation was accepted");
        check(coordinator.currentSession() == null, "profile-only preparation published a session");
        AutoLoginReceiver login = new AutoLoginReceiver(coordinator);
        login.login();
        check(login.values.size() == 1 && login.last().isEmpty() && !login.confirmed.get(0),
            "profile-only AutoLogin delivered credentials");
        check("startup_not_ready".equals(login.statuses.get(login.statuses.size() - 1)),
            "profile-only AutoLogin status was not startup_not_ready");
        done("profile_only_policy_never_publishes_session_or_autologin_credentials");
    }

    private static void negativeUsername(File assets, File documents) throws Exception {
        File root = temporary("p7-credential-username-");
        Context app = new Context(root, new AssetManager(assets));
        prepareProductionPolicies(app);
        HostServices services = new HostServices(app, false, true, false, false, false);
        Project7StartupCoordinator coordinator = new Project7StartupCoordinator(app, services);
        boolean rejected = false;
        try { run(coordinator, documents); } catch (IOException expected) { rejected = true; }
        check(rejected && coordinator.currentSession() == null,
            "mismatched delivered username reached a ready session");
        check(services.latest.credentials != null &&
            !services.latest.credentials.username.equals(services.latest.identity.identity().username()),
            "negative fixture did not mismatch the username");
        done("coordinator_rejects_delivered_username_that_differs_from_prepared_identity");
    }

    private static void negativeZeroNumericId(File assets, File documents) throws Exception {
        File root = temporary("p7-credential-uid-");
        Context app = new Context(root, new AssetManager(assets));
        prepareProductionPolicies(app);
        HostServices services = new HostServices(app, false, false, true, false, false);
        Project7StartupCoordinator coordinator = new Project7StartupCoordinator(app, services);
        boolean rejected = false;
        try { run(coordinator, documents); } catch (IOException expected) { rejected = true; }
        check(rejected && coordinator.currentSession() == null, "zero numeric id reached a ready session");
        done("coordinator_rejects_prepared_identity_without_a_bound_numeric_id");
    }

    private static void negativeReceiverFailure(File assets, File documents) throws Exception {
        File root = temporary("p7-credential-receiver-");
        Context app = new Context(root, new AssetManager(assets));
        prepareProductionPolicies(app);
        HostServices services = new HostServices(app, false, false, false, true, false);
        Project7StartupCoordinator coordinator = new Project7StartupCoordinator(app, services);
        boolean rejected = false;
        try { run(coordinator, documents); } catch (IOException expected) { rejected = true; }
        check(rejected && coordinator.currentSession() == null,
            "credential delivery failure still published a session");
        check(services.latest.deliveryError != null && services.latest.deliveryError.contains("CREDENTIAL_DELIVERY_FAILED"),
            "receiver exception did not fail closed as CREDENTIAL_DELIVERY_FAILED: " + services.latest.deliveryError);
        done("credential_receiver_exception_fails_preparation_without_publishing_session");
    }

    public static void main(String[] args) throws Exception {
        try {
        File assets = new File(args[0]);
        File documents = temporary("p7-credential-documents-");
        // Positive and reload share one private app root to exercise the READY journal.
        File root = temporary("p7-credential-root-");
        Context app = new Context(root, new AssetManager(assets));
        prepareProductionPolicies(app);
        HostServices services = new HostServices(app, false, false, false, false, false);
        Project7StartupCoordinator coordinator = new Project7StartupCoordinator(app, services);
        Project7StartupCoordinator.Ticket ticket = run(coordinator, documents);
        AutoLoginCore.Session session = coordinator.currentSession();
        check(session != null, "positive session missing");
        String username = session.credentials.username, secret = session.credentials.secret;
        AutoLoginReceiver login = new AutoLoginReceiver(coordinator);
        login.login();
        check(login.confirmed.size() == 1 && login.confirmed.get(0), "positive AutoLogin did not submit");
        check(login.last().contains("\"username\":" + quote(username)) &&
            login.last().contains("\"password\":" + quote(secret)),
            "positive AutoLogin payload does not carry the coordinator identity");
        System.out.println("POSITIVE identity=" + username + " secret_sha256=" + StableIdentityBootstrap.digest(secret));
        done("real_bootstrap_prepared_identity_delivers_exact_credentials_into_coordinator_session_and_autologin");
        coordinator.abandon(ticket);

        reload(assets, documents, root, username, secret);
        negativeProfileOnly(assets, documents);
        negativeUsername(assets, documents);
        negativeZeroNumericId(assets, documents);
        negativeReceiverFailure(assets, documents);
        System.out.println("STARTUP_CREDENTIAL_BINDING_PASSED=" + passed);
        } finally { cleanup(); }
    }
}
