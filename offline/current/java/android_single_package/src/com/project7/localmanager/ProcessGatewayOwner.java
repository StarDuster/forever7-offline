package com.project7.localmanager;

import android.content.Context;
import java.util.concurrent.CompletableFuture;
import java.util.concurrent.CopyOnWriteArrayList;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.ScheduledExecutorService;
import java.util.concurrent.TimeUnit;

/** One application-context controller and reservation per process/classloader.
 * No socket probe/client and no fallback to another manager on port 23333.
 */
public final class ProcessGatewayOwner {
    private static final ProcessGatewayOwner INSTANCE = new ProcessGatewayOwner();
    static ProcessGatewayOwner instance() { return INSTANCE; }
    synchronized boolean hasActiveReservation() { return current != null; }
    private final ScheduledExecutorService deadlines = Executors.newScheduledThreadPool(2,
        r -> daemon(r, "p7-owner-deadline"));
    private final ExecutorService notifications = Executors.newCachedThreadPool(
        r -> daemon(r, "p7-owner-notification"));
    private final ExecutorService completions = Executors.newCachedThreadPool(
        r -> daemon(r, "p7-owner-future-completion"));
    private final long startupMillis;
    private final long drainMillis;
    private final LifecycleDriver testDriver;
    private Context applicationContext;
    private Session current;

    private ProcessGatewayOwner() { this(null, 30000, 30000); }
    /** Host injection only; not exposed as an alternative production owner. */
    ProcessGatewayOwner(LifecycleDriver driver, long startupMillis, long drainMillis) {
        this.testDriver = driver; this.startupMillis = startupMillis; this.drainMillis = drainMillis;
    }
    static final class Session {
        final LifecycleDriver driver;
        final SinglePackageGateway.StartupBudget budget;
        /** One handoff per process-owner session; never shared with an earlier/later session. */
        final ProfileStoreHandoff handoff;
        /** Aware initializers (production) must publish a prepared store before construct. */
        final boolean handoffRequired;
        long startupEpoch;
        final CompletableFuture<Void> ready = new CompletableFuture<>();
        final CompletableFuture<Void> stopped = new CompletableFuture<>();
        final CompletableFuture<Void> drained = new CompletableFuture<>();
        final CopyOnWriteArrayList<SinglePackageGateway.Observer> observers = new CopyOnWriteArrayList<>();
        volatile SinglePackageGateway.State state = SinglePackageGateway.State.STARTING;
        volatile String detail = "startup requested";
        volatile boolean cancelled;
        volatile boolean startupExited;
        volatile boolean drainStarted;
        volatile boolean failed;
        volatile boolean released;
        int startupDecision; // 0 pending, 1 bound/ready, 2 failed; decided under this session monitor.
        Throwable startupError;
        int stopDecision; // 0 pending, 1 actual release success, 2 timeout/failure.
        Throwable stopError;
        volatile Thread gatewayThread;
        volatile Thread bootstrapThread;
        Session(LifecycleDriver driver, SinglePackageGateway.StartupBudget budget, boolean handoffRequired) {
            this.driver = driver;
            this.budget = budget;
            this.handoff = driver == null ? null : new ProfileStoreHandoff(driver.saveAccess());
            this.handoffRequired = handoffRequired;
        }
    }
    synchronized Session start(Context context, boolean resourcesReady,
                               SinglePackageGateway.PreStartInitializer initializer,
                               SinglePackageGateway.Observer observer, SinglePackageGateway.StartupBudget requestedBudget) {
        if (!resourcesReady || initializer == null) return rejected("Resource gate/initializer required");
        if (context == null) return rejected("Application Context required");
        Context app = context.getApplicationContext();
        if (app == null) return rejected("Application Context required");
        if (applicationContext != null && applicationContext != app)
            return rejected("Different application context for process owner");
        if (current != null) {
            if (observer != null) current.observers.addIfAbsent(observer);
            return current;
        }
        applicationContext = app;
        SinglePackageGateway.StartupBudget budget = requestedBudget == null ?
            SinglePackageGateway.StartupBudget.continuous(startupMillis) : requestedBudget;
        Session s = new Session(testDriver == null ? new ManagerLifecycleDriver() : testDriver, budget,
            initializer instanceof ProfileStoreHandoff.Aware);
        current = s;
        if (observer != null) s.observers.add(observer);
        deadlines.schedule(() -> {
            startupTimeout(s, 0);
        }, budget.prestartMillis, TimeUnit.MILLISECONDS);
        daemon(() -> startup(s, app, initializer), "p7-owner-startup").start();
        return s;
    }
    private Session rejected(String message) {
        Session rejected = new Session(null, SinglePackageGateway.StartupBudget.continuous(startupMillis), false);
        rejected.state = SinglePackageGateway.State.FAILED; rejected.detail = message;
        rejected.ready.completeExceptionally(new IllegalStateException(message));
        rejected.released = true; rejected.stopped.complete(null); rejected.drained.complete(null);
        return rejected;
    }
    CompletableFuture<Void> ready(Session s) {
        if (!s.cancelled) return s.ready;
        CompletableFuture<Void> rejected = new CompletableFuture<>();
        rejected.completeExceptionally(new IllegalStateException("Owner closing/failed; await actual drained before restart"));
        return rejected;
    }
    private void startup(Session s, Context app, SinglePackageGateway.PreStartInitializer initializer) {
        try {
            synchronized (s.driver.saveAccess()) {
                if (s.cancelled) return;
                s.driver.claim();
                if (s.cancelled) return;
                if (initializer instanceof ProfileStoreHandoff.Aware)
                    ((ProfileStoreHandoff.Aware) initializer).bindHandoff(s.handoff.sink());
                publish(s, SinglePackageGateway.State.INITIALIZING, "exclusive stopped-service initialization");
                initializer.initialize(app);
                if (s.cancelled) return;
                if (s.handoffRequired && !s.handoff.available())
                    throw new IllegalStateException("Prepared profile store handoff missing");
                if (s.budget.phased && !beginBindPhase(s)) return;
                s.driver.activate();
                ProfileStoreHandoff handoff = s.handoffRequired || s.handoff.available() ? s.handoff : null;
                s.driver.construct(app, (running, detail) -> status(s, running, detail), handoff);
                if (s.handoffRequired && (s.handoff == null || !s.handoff.consumed()))
                    throw new IllegalStateException("Prepared profile store handoff was not consumed");
                if (s.cancelled) return;
                s.gatewayThread = daemon(() -> listen(s, true), "p7-owner-gateway");
                s.bootstrapThread = daemon(() -> listen(s, false), "p7-owner-bootstrap");
                s.driver.register(s.gatewayThread);
                synchronized (s) {
                    if (s.cancelled) return;
                    s.bootstrapThread.start(); s.gatewayThread.start();
                }
            }
        } catch (Throwable error) { fail(s, error); }
        finally { s.startupExited = true; if (s.cancelled) beginDrain(s); }
    }
    private void listen(Session s, boolean gateway) {
        try { if (gateway) s.driver.runGateway(); else s.driver.runBootstrap(); }
        catch (Throwable error) { if (!s.cancelled) fail(s, error); }
        finally { if (!s.cancelled) fail(s, new IllegalStateException("Owned listener exited")); }
    }
    private void status(Session s, boolean running, String detail) {
        if (!running) { if (!s.cancelled) fail(s, new IllegalStateException(detail)); return; }
        synchronized (s) {
            if (s.cancelled || s.failed || s.startupDecision != 0) return;
            s.startupDecision = 1;
            s.state = SinglePackageGateway.State.READY; s.detail = detail;
        }
        s.driver.beforeReadyPublication();
        completeStartup(s);
        notifyObservers(s, SinglePackageGateway.State.READY, detail);
    }
    private void fail(Session s, Throwable error) {
        synchronized (s) {
            if (s.released) return;
            if (s.startupDecision == 0) { s.startupDecision = 2; s.startupError = error; }
            s.failed = true; s.cancelled = true;
            s.state = SinglePackageGateway.State.FAILED; s.detail = error.toString();
        }
        if (s.handoff != null) s.handoff.invalidate();
        beginDrain(s);
        completeStartup(s);
        notifyObservers(s, SinglePackageGateway.State.FAILED, error.toString());
    }
    CompletableFuture<Void> close(Session s) {
        synchronized (s) {
            if (s.released || s.cancelled) return s.stopped;
            s.cancelled = true;
            if (s.startupDecision == 0) {
                s.startupDecision = 2; s.startupError = new IllegalStateException("Gateway closing");
            }
            s.state = SinglePackageGateway.State.CLOSING; s.detail = "stopping owned listeners and writers";
        }
        if (s.handoff != null) s.handoff.invalidate();
        beginDrain(s);
        completeStartup(s);
        notifyObservers(s, SinglePackageGateway.State.CLOSING, s.detail);
        return s.stopped;
    }
    private boolean beginBindPhase(Session s) {
        final long epoch;
        synchronized (s) {
            if (s.cancelled || s.startupDecision != 0) return false;
            epoch = ++s.startupEpoch;
        }
        deadlines.schedule(() -> startupTimeout(s, epoch), s.budget.bindMillis, TimeUnit.MILLISECONDS);
        publish(s, SinglePackageGateway.State.STARTING, "constructing owned listeners");
        return true;
    }
    private void startupTimeout(Session s, long expectedEpoch) {
        IllegalStateException error = new IllegalStateException("Gateway startup hard deadline exceeded");
        synchronized (s) {
            if (s.startupDecision != 0 || s.startupEpoch != expectedEpoch) return;
            s.startupDecision = 2; s.startupError = error;
            s.failed = true; s.cancelled = true;
            s.state = SinglePackageGateway.State.FAILED; s.detail = error.toString();
        }
        if (s.handoff != null) s.handoff.invalidate();
        beginDrain(s);
        completeStartup(s);
        notifyObservers(s, SinglePackageGateway.State.FAILED, error.toString());
    }
    private void completeStartup(Session s) {
        final int decision;
        final Throwable error;
        synchronized (s) { decision = s.startupDecision; error = s.startupError; }
        // Never run arbitrary CompletableFuture dependents under the session lock.
        if (decision == 1) complete(s.ready, null);
        else if (decision == 2) complete(s.ready, error);
    }
    private void beginDrain(Session s) {
        if (s.handoff != null) s.handoff.invalidate();
        synchronized (s) {
            if (s.drainStarted) return;
            s.drainStarted = true;
        }
        deadlines.schedule(() -> {
            IllegalStateException error = new IllegalStateException("Drain deadline exceeded; owner retained until actual stop");
            synchronized (s) {
                if (s.released || s.stopDecision != 0) return;
                s.stopDecision = 2; s.stopError = error;
                s.failed = true; s.state = SinglePackageGateway.State.FAILED; s.detail = error.getMessage();
            }
            completeStopped(s);
            notifyObservers(s, SinglePackageGateway.State.FAILED, error.getMessage());
        }, drainMillis, TimeUnit.MILLISECONDS);
        daemon(() -> drain(s), "p7-owner-drain").start();
    }
    private void drain(Session s) {
        try {
            // A cancelled Future/interrupt is not evidence that a constructor or
            // initializer stopped writing. Never release while startup is in flight.
            while (!s.startupExited) Thread.sleep(10);
            s.driver.closeOwned();
            while (alive(s.gatewayThread) || alive(s.bootstrapThread) || !s.driver.writersStopped())
                Thread.sleep(10);
            synchronized (s.driver.saveAccess()) { s.driver.release(); }
            synchronized (s) {
                if (!s.failed) s.state = SinglePackageGateway.State.CLOSED;
                s.detail = "owned startup/listeners/writers drained; restart permitted";
                s.released = true;
                if (s.stopDecision == 0) s.stopDecision = 1;
            }
            synchronized (this) { if (current == s) current = null; }
            complete(s.drained, null); completeStopped(s);
            notifyObservers(s, s.state, s.detail);
        } catch (Throwable error) {
            synchronized (s) {
                s.failed = true; s.state = SinglePackageGateway.State.FAILED;
                s.detail = "Drain failed; reservation retained: " + error;
                if (s.stopDecision == 0) { s.stopDecision = 2; s.stopError = error; }
            }
            completeStartup(s); completeStopped(s);
            notifyObservers(s, SinglePackageGateway.State.FAILED, s.detail);
            // No release on uncertain shutdown/registry ownership.
        }
    }
    private void completeStopped(Session s) {
        final int decision;
        final Throwable error;
        synchronized (s) { decision = s.stopDecision; error = s.stopError; }
        if (decision == 0) return;
        s.driver.beforeStoppedPublication();
        complete(s.stopped, decision == 1 ? null : error);
    }
    private void complete(CompletableFuture<Void> future, Throwable error) {
        // Each public future gets its own completion task. Arbitrary synchronous
        // dependents cannot occupy deadline/drain threads or another future's publication.
        completions.execute(() -> {
            if (error == null) future.complete(null); else future.completeExceptionally(error);
        });
    }
    private static boolean alive(Thread thread) { return thread != null && thread.isAlive(); }
    private void publish(Session s, SinglePackageGateway.State next, String detail) {
        synchronized (s) { if (s.cancelled) return; s.state = next; s.detail = detail; }
        notifyObservers(s, next, detail);
    }
    private void notifyObservers(Session s, SinglePackageGateway.State state, String detail) {
        notifications.execute(() -> {
            for (SinglePackageGateway.Observer observer : s.observers) {
                try { observer.changed(state, detail); }
                catch (Throwable ignored) { /* An observer cannot control ownership/drain. */ }
            }
        });
    }
    private static Thread daemon(Runnable task, String name) {
        Thread thread = new Thread(task, name); thread.setDaemon(true); return thread;
    }
}
