package com.project7.localmanager;

import android.content.Context;
import java.lang.reflect.Field;
import java.util.concurrent.atomic.AtomicBoolean;

/** Exact same-package API for pinned manager 2.10.1; no engine replacements. */
final class ManagerLifecycleDriver implements LifecycleDriver {
    private final Runnable afterServerRegistration;
    ManagerLifecycleDriver() { this(() -> {}); }
    /** Finite host fault-injection seam; default production path is a no-op. */
    ManagerLifecycleDriver(Runnable afterServerRegistration) { this.afterServerRegistration = afterServerRegistration; }
    private LegacyState legacy;
    private Object previousServer;
    private Object previousThread;
    private boolean claimed;
    private boolean activated;
    private boolean serverWritten;
    private boolean threadWritten;
    private LocalGatewayServer gateway;
    private LocalBootstrapServer bootstrap;
    private Thread ownedThread;

    public Object saveAccess() { return GatewayService.SAVE_ACCESS; }
    public void claim() throws Exception {
        legacy = new LegacyState();
        if (GatewayService.saveAccessBlocked())
            throw new IllegalStateException("Legacy gateway/save writers active; will not attach or replace");
        previousServer = legacy.lastServer.get(null);
        previousThread = legacy.lastThread.get(null);
        claimed = true;
        // Keep RUNNING=false throughout stopped-service initialization.
    }
    public void activate() throws Exception {
        requireOriginalRegistry();
        if (legacy.running.get()) throw new IllegalStateException("Legacy RUNNING changed during initialization");
        legacy.running.set(true); activated = true;
    }
    public void construct(Context app, Status status) throws Exception { construct(app, status, null); }
    /** Non-production/legacy callers without a handoff keep the original cold-store path.
     * The production owner always supplies a required handoff, so a missing or already
     * consumed prepared store fails here instead of silently opening a second store.
     */
    public void construct(Context app, Status status, ProfileStoreHandoff handoff) throws Exception {
        LocalProfileStore profiles = handoff == null ? new LocalProfileStore(app) : handoff.take();
        LocalGatewayServer.ProfileProvider safeProfiles = new FailureSafeProfileProvider(profiles);
        LocalTutorialStore tutorials = new LocalTutorialStore(app);
        LocalAccountStore accounts = new LocalAccountStore(app);
        LocalEventCatalog events = new LocalEventCatalog(app);
        LocalNewbeeCatalog newbee = new LocalNewbeeCatalog(app);
        LocalCombatCatalog combat = new LocalCombatCatalog(app);
        LocalPatrolCatalog patrol = new LocalPatrolCatalog(app);
        gateway = new LocalGatewayServer(23333, accounts, safeProfiles, tutorials, events,
            newbee, combat, patrol, status::changed);
        bootstrap = new LocalBootstrapServer(23334, () -> LocalStartupMode.get(app));
    }
    public void register(Thread thread) throws Exception {
        requireOriginalRegistry();
        ownedThread = thread;
        legacy.lastServer.set(null, gateway); serverWritten = true;
        afterServerRegistration.run();
        legacy.lastThread.set(null, thread); threadWritten = true;
    }
    private void requireOriginalRegistry() throws Exception {
        if (!claimed || legacy.lastServer.get(null) != previousServer ||
                legacy.lastThread.get(null) != previousThread)
            throw new IllegalStateException("Legacy registry changed; reservation retained");
    }
    public void runGateway() { gateway.run(); }
    public void runBootstrap() { bootstrap.run(); }
    public void closeOwned() throws Exception {
        Throwable failure = null;
        try { if (bootstrap != null) bootstrap.close(); } catch (Throwable error) { failure = error; }
        try { if (gateway != null) gateway.close(); } catch (Throwable error) { if (failure == null) failure = error; }
        if (failure != null) throw new IllegalStateException("Owned close failed; reservation retained", failure);
    }
    public boolean writersStopped() { return gateway == null || gateway.saveWritersStopped(); }
    public void release() throws Exception {
        if (!claimed) return;
        Object expectedServer = serverWritten ? gateway : previousServer;
        Object expectedThread = threadWritten ? ownedThread : previousThread;
        if (legacy.lastServer.get(null) != expectedServer || legacy.lastThread.get(null) != expectedThread)
            throw new IllegalStateException("Foreign registry values; never clear another owner");
        // Restore only fields successfully written by this driver. A failure
        // before registration must not erase an older stopped legacy reference.
        if (serverWritten) legacy.lastServer.set(null, previousServer);
        if (threadWritten) legacy.lastThread.set(null, previousThread);
        if (activated) legacy.running.set(false);
        claimed = false;
    }
    private static final class LegacyState {
        final AtomicBoolean running;
        final Field lastServer;
        final Field lastThread;
        LegacyState() throws ReflectiveOperationException {
            running = (AtomicBoolean) field("RUNNING").get(null);
            lastServer = field("lastServer"); lastThread = field("lastServerThread");
        }
        private static Field field(String name) throws ReflectiveOperationException {
            Field result = GatewayService.class.getDeclaredField(name);
            result.setAccessible(true); return result;
        }
    }
}
