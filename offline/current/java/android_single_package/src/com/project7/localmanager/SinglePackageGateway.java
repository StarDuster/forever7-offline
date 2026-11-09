package com.project7.localmanager;

import android.content.Context;
import java.util.concurrent.CompletableFuture;

/** Nonblocking handle to the single process-owned manager controller.
 * READY means our listener bound, not resource/account/login completion.
 * Compile stubs and host tests must never be included in a DEX/APK.
 */
public final class SinglePackageGateway {
    public enum State { IDLE, STARTING, INITIALIZING, READY, CLOSING, CLOSED, FAILED }
    /** Read-only process observation; not an exclusive reservation. */
    public static boolean hasActiveProcessReservation() { return ProcessGatewayOwner.instance().hasActiveReservation(); }
    public static final class StartupBudget {
        final long prestartMillis, bindMillis;
        final boolean phased;
        private StartupBudget(long prestartMillis, long bindMillis, boolean phased) {
            if (prestartMillis <= 0 || prestartMillis > 600000 || bindMillis <= 0 || bindMillis > 30000)
                throw new IllegalArgumentException("Startup budget outside trusted bounds");
            this.prestartMillis = prestartMillis; this.bindMillis = bindMillis; this.phased = phased;
        }
        /** Policy cap for the approved whole-profile collection bootstrap, not a performance claim. */
        public static StartupBudget fullCollectionPreparation() { return new StartupBudget(600000, 30000, true); }
        static StartupBudget continuous(long millis) { return new StartupBudget(millis, Math.min(millis, 30000), false); }
        static StartupBudget phasedForHostTests(long prestart, long bind) { return new StartupBudget(prestart, bind, true); }
    }
    public interface Observer { void changed(State state, String detail); }
    public interface PreStartInitializer {
        /** Worker only, SAVE_ACCESS held, service stopped. Do not await start/close here. */
        void initialize(Context applicationContext) throws Exception;
    }
    private final ProcessGatewayOwner owner;
    private final Observer observer;
    private volatile ProcessGatewayOwner.Session session;
    private volatile State idleState = State.IDLE;

    public SinglePackageGateway(Observer observer) { this(ProcessGatewayOwner.instance(), observer); }
    SinglePackageGateway(ProcessGatewayOwner owner, Observer observer) {
        this.owner = owner; this.observer = observer;
    }
    public State state() { return session == null ? idleState : session.state; }
    public String detail() { return session == null ? "not started" : session.detail; }

    /** Old callers must supply the explicit resource gate and prestart policy. */
    public CompletableFuture<Void> start(Context context) {
        CompletableFuture<Void> rejected = new CompletableFuture<>();
        rejected.completeExceptionally(new IllegalStateException("Explicit resource readiness and initializer required"));
        return rejected;
    }
    /** The first accepted caller supplies the one initializer for this session.
     * Concurrent handles join it; Activity recreation never runs initialization twice.
     * resourcesReady is the caller's verified gate, not a resource check performed here.
     */
    public synchronized CompletableFuture<Void> start(Context context, boolean resourcesReady,
                                                     PreStartInitializer initializer) {
        return start(context, resourcesReady, initializer, null);
    }
    public synchronized CompletableFuture<Void> start(Context context, boolean resourcesReady,
                                                     PreStartInitializer initializer, StartupBudget budget) {
        ProcessGatewayOwner.Session candidate = owner.start(context, resourcesReady, initializer, observer, budget);
        if (candidate.driver == null) {
            if (session == null || session.released) session = candidate;
            return candidate.ready;
        }
        session = candidate;
        return owner.ready(candidate);
    }
    public synchronized CompletableFuture<Void> closeAsync() {
        ProcessGatewayOwner.Session current = session;
        if (current == null) { idleState = State.CLOSED; return CompletableFuture.completedFuture(null); }
        return owner.close(current);
    }
    /** Completes only after startup exited, own listeners/writers stopped and
     * own reservation was released. Unlike closeAsync, it never times out as success.
     */
    public CompletableFuture<Void> drained() {
        ProcessGatewayOwner.Session current = session;
        return current == null ? CompletableFuture.completedFuture(null) : current.drained;
    }
}
