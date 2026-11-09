package com.project7.localmanager;

import android.content.Context;
import java.io.IOException;
import java.lang.reflect.Field;
import java.util.concurrent.CompletableFuture;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.ExecutionException;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicBoolean;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.concurrent.atomic.AtomicReference;
import java.util.function.BooleanSupplier;

/** Explicit host lifecycle assertions; NO Android runtime/game/native execution. */
public final class ProcessOwnerHostTests {
    private static int passed;
    private static final Context APP = new Context();
    private static void check(boolean value, String detail) { if (!value) throw new AssertionError(detail); }
    private static void await(CountDownLatch latch) throws Exception {
        if (!latch.await(2, TimeUnit.SECONDS)) throw new AssertionError("latch timeout");
    }
    private static void success(CompletableFuture<Void> future) throws Exception { future.get(2, TimeUnit.SECONDS); }
    private static void failure(CompletableFuture<Void> future) throws Exception {
        try { future.get(2, TimeUnit.SECONDS); throw new AssertionError("expected future failure"); }
        catch (ExecutionException expected) { check(expected.getCause() != null, "missing failure"); }
    }
    private static void until(BooleanSupplier condition) throws Exception {
        long deadline = System.nanoTime() + TimeUnit.SECONDS.toNanos(2);
        while (!condition.getAsBoolean() && System.nanoTime() < deadline) Thread.sleep(5);
        check(condition.getAsBoolean(), "condition timeout");
    }
    private static void done(String name) { passed++; System.out.println("PASS " + name); }

    private static final class FakeDriver implements LifecycleDriver {
        final Object lock = new Object();
        final AtomicInteger claims = new AtomicInteger();
        final AtomicInteger constructions = new AtomicInteger();
        final AtomicInteger activations = new AtomicInteger();
        final AtomicInteger releases = new AtomicInteger();
        final CountDownLatch enteredConstructor = new CountDownLatch(1);
        final CountDownLatch enteredClaim = new CountDownLatch(1);
        volatile CountDownLatch constructorGate = new CountDownLatch(0);
        volatile CountDownLatch claimGate = new CountDownLatch(0);
        volatile CountDownLatch readyGate = new CountDownLatch(0);
        volatile CountDownLatch stopPublicationGate = new CountDownLatch(0);
        final CountDownLatch stopDecision = new CountDownLatch(1);
        final CountDownLatch readyDecision = new CountDownLatch(1);
        volatile CountDownLatch stopped = new CountDownLatch(1);
        volatile boolean reserved;
        volatile boolean running;
        volatile boolean writersStopped = true;
        volatile boolean stickWriters;
        volatile Thread stubbornWriter;
        final CountDownLatch writerExit = new CountDownLatch(1);
        volatile boolean legacyActive;
        volatile boolean foreignRegistry;
        volatile int registerFailure;
        volatile int registrations;
        volatile int closeCalls;
        volatile Context constructedContext;
        volatile Status status;
        volatile boolean portConflict;
        volatile boolean bindFailure;
        volatile boolean failConstructAfterHandoff;
        volatile boolean skipHandoffTake;
        volatile boolean ignoreHandoffOverride;
        volatile ProfileStoreHandoff handedHandoff;
        volatile LocalProfileStore handedStore;
        final AtomicInteger handoffTakes = new AtomicInteger();
        public Object saveAccess() { return lock; }
        public void claim() throws Exception {
            check(Thread.holdsLock(lock), "claim without SAVE_ACCESS");
            enteredClaim.countDown(); claimGate.await();
            if (legacyActive) throw new IllegalStateException("legacy writers active");
            check(!reserved, "duplicate reservation");
            reserved = true; claims.incrementAndGet(); stopped = new CountDownLatch(1);
        }
        public void activate() { check(reserved, "activate without owner"); running = true; activations.incrementAndGet(); }
        public void construct(Context app, Status callback) throws Exception {
            constructedContext = app; status = callback; constructions.incrementAndGet();
            enteredConstructor.countDown(); constructorGate.await();
            if (portConflict) throw new IOException("23333 occupied; no client attach");
            if (failConstructAfterHandoff) throw new IOException("host construct failure after handoff");
            writersStopped = false;
            if (stickWriters) {
                stubbornWriter = new Thread(() -> {
                    while (writerExit.getCount() != 0) {
                        try { writerExit.await(); } catch (InterruptedException ignored) { /* Explicit stubborn writer model. */ }
                    }
                }, "host-stubborn-save-writer");
                stubbornWriter.setDaemon(true); stubbornWriter.start();
            }
        }
        public void construct(Context app, Status callback, ProfileStoreHandoff handoff) throws Exception {
            if (ignoreHandoffOverride) {
                LifecycleDriver.super.construct(app, callback, handoff);
                return;
            }
            check(Thread.holdsLock(lock), "construct without SAVE_ACCESS");
            handedHandoff = handoff;
            if (handoff != null && !skipHandoffTake) {
                handedStore = handoff.take();
                handoffTakes.incrementAndGet();
            }
            construct(app, callback);
        }
        public void register(Thread thread) throws Exception {
            if (registerFailure == 1) throw new IOException("before registration");
            registrations++;
            if (registerFailure == 2) throw new IOException("after owned registration");
        }
        public void beforeReadyPublication() {
            readyDecision.countDown(); LocalGatewayServer.await(readyGate);
        }
        public void beforeStoppedPublication() {
            stopDecision.countDown(); LocalGatewayServer.await(stopPublicationGate);
        }
        public void runGateway() {
            status.changed(!bindFailure, bindFailure ? "own bind failed; port occupied" : "own fake bound 23333");
            LocalGatewayServer.await(stopped);
        }
        public void runBootstrap() { LocalGatewayServer.await(stopped); }
        public void closeOwned() {
            closeCalls++; stopped.countDown();
            if (!stickWriters) writersStopped = true;
            if (stubbornWriter != null) stubbornWriter.interrupt();
        }
        public boolean writersStopped() { return stubbornWriter == null ? writersStopped : !stubbornWriter.isAlive(); }
        public void release() {
            check(Thread.holdsLock(lock), "release without SAVE_ACCESS");
            if (foreignRegistry) throw new IllegalStateException("foreign values retained");
            if (reserved) { reserved = false; running = false; releases.incrementAndGet(); }
        }
    }
    private static SinglePackageGateway handle(ProcessGatewayOwner owner) { return new SinglePackageGateway(owner, null); }
    private static SinglePackageGateway.PreStartInitializer initializer(FakeDriver driver, AtomicInteger calls) {
        return app -> {
            check(Thread.holdsLock(driver.lock), "initializer outside SAVE_ACCESS");
            check(driver.reserved && !driver.running, "initializer must be reserved and service stopped");
            check(app == APP, "initializer retained Activity context"); calls.incrementAndGet();
        };
    }
    /** Host model of the production initializer: publishes only its original prepared store. */
    private static final class HandoffInitializer implements SinglePackageGateway.PreStartInitializer, ProfileStoreHandoff.Aware {
        final LocalProfileStore prepared;
        volatile ProfileStoreHandoff.Sink sink;
        volatile CountDownLatch gate = new CountDownLatch(0);
        final CountDownLatch entered = new CountDownLatch(1);
        volatile boolean publish = true;
        volatile boolean throwFailure;
        volatile IOException publishFailure;
        HandoffInitializer(LocalProfileStore prepared) { this.prepared = prepared; }
        public void bindHandoff(ProfileStoreHandoff.Sink sink) { this.sink = sink; }
        public void initialize(Context app) throws Exception {
            entered.countDown();
            try { gate.await(); } catch (InterruptedException error) { Thread.currentThread().interrupt(); }
            if (throwFailure) throw new IOException("initializer failure");
            if (publish) {
                try { sink.publish(prepared); }
                catch (IOException error) { publishFailure = error; throw error; }
            }
        }
    }
    private static void hardBlockedConstructor() throws Exception {
        FakeDriver driver = new FakeDriver(); driver.constructorGate = new CountDownLatch(1);
        ProcessGatewayOwner owner = new ProcessGatewayOwner(driver, 100, 120);
        SinglePackageGateway first = handle(owner); AtomicInteger init = new AtomicInteger();
        long start = System.nanoTime();
        CompletableFuture<Void> ready = first.start(APP, true, initializer(driver, init));
        await(driver.enteredConstructor); failure(ready);
        check(TimeUnit.NANOSECONDS.toMillis(System.nanoTime() - start) < 1000, "constructor delayed hard deadline");
        failure(first.closeAsync());
        check(driver.reserved && !first.drained().isDone() && owner.hasActiveReservation(), "blocked constructor released owner");
        failure(handle(owner).start(APP, true, initializer(driver, init)));
        check(driver.constructions.get() == 1 && init.get() == 1, "second owner initialized");
        driver.constructorGate.countDown(); success(first.drained());
        check(driver.registrations == 0 && driver.releases.get() == 1, "late constructor started listeners");
        done("hard_timeout_blocked_constructor_retains_owner_until_exit");
    }
    private static void closeDuringInitializer() throws Exception {
        FakeDriver driver = new FakeDriver(); ProcessGatewayOwner owner = new ProcessGatewayOwner(driver, 1000, 100);
        SinglePackageGateway gateway = handle(owner); CountDownLatch entered = new CountDownLatch(1), release = new CountDownLatch(1);
        CompletableFuture<Void> ready = gateway.start(APP, true, app -> { entered.countDown(); release.await(); });
        await(entered); CompletableFuture<Void> close = gateway.closeAsync(); failure(ready); failure(close);
        check(driver.reserved && !gateway.drained().isDone(), "initializer released early");
        release.countDown(); success(gateway.drained());
        check(driver.constructions.get() == 0 && driver.activations.get() == 0, "late initializer created listener");
        done("close_during_initializer_never_starts_late_listener");
    }
    private static void failedInitialization() throws Exception {
        FakeDriver driver = new FakeDriver(); ProcessGatewayOwner owner = new ProcessGatewayOwner(driver, 1000, 1000);
        SinglePackageGateway gateway = handle(owner);
        failure(gateway.start(APP, true, app -> { throw new IOException("initialization failed"); }));
        success(gateway.drained()); check(driver.constructions.get() == 0 && !driver.reserved, "failed initializer constructed listener");
        check(gateway.state() == SinglePackageGateway.State.FAILED, "failure overwritten as success");
        done("initialization_failure_builds_no_listener");
    }
    private static void concurrentHandlesAndRestart() throws Exception {
        FakeDriver driver = new FakeDriver(); ProcessGatewayOwner owner = new ProcessGatewayOwner(driver, 1000, 1000);
        SinglePackageGateway first = new SinglePackageGateway(owner, (state, detail) -> { throw new AssertionError("observer failure"); });
        SinglePackageGateway second = handle(owner); AtomicInteger init = new AtomicInteger();
        SinglePackageGateway.PreStartInitializer hook = initializer(driver, init);
        CountDownLatch go = new CountDownLatch(1);
        Thread a = new Thread(() -> { LocalGatewayServer.await(go); first.start(APP, true, hook); });
        Thread b = new Thread(() -> { LocalGatewayServer.await(go); second.start(APP, true, hook); });
        a.start(); b.start(); go.countDown(); a.join(); b.join();
        success(first.start(APP, true, hook)); success(second.start(APP, true, hook));
        check(driver.claims.get() == 1 && init.get() == 1, "duplicate process initialization");
        AtomicReference<CompletableFuture<Void>> closeA = new AtomicReference<>(), closeB = new AtomicReference<>();
        CountDownLatch closeGo = new CountDownLatch(1);
        Thread closeFirst = new Thread(() -> { LocalGatewayServer.await(closeGo); closeA.set(first.closeAsync()); });
        Thread closeSecond = new Thread(() -> { LocalGatewayServer.await(closeGo); closeB.set(second.closeAsync()); });
        closeFirst.start(); closeSecond.start(); closeGo.countDown(); closeFirst.join(); closeSecond.join();
        check(closeA.get() == closeB.get(), "close is not shared/idempotent"); success(closeA.get()); success(first.drained());
        success(first.start(APP, true, hook)); check(driver.claims.get() == 2, "restart missing new owner");
        success(second.closeAsync()); check(driver.reserved, "old handle closed new session");
        success(first.closeAsync()); success(first.drained());
        done("two_concurrent_handles_observer_error_idempotent_close_restart");
    }
    private static void stuckWriters() throws Exception {
        FakeDriver driver = new FakeDriver(); driver.stickWriters = true;
        ProcessGatewayOwner owner = new ProcessGatewayOwner(driver, 1000, 100);
        SinglePackageGateway gateway = handle(owner); AtomicInteger init = new AtomicInteger();
        success(gateway.start(APP, true, initializer(driver, init))); failure(gateway.closeAsync());
        check(driver.reserved && !gateway.drained().isDone(), "live writers falsely drained");
        failure(gateway.start(APP, true, initializer(driver, init)));
        check(driver.claims.get() == 1, "restart bypassed live writers");
        check(driver.stubbornWriter.isAlive(), "stubborn writer model exited early");
        driver.writerExit.countDown(); success(gateway.drained()); check(!driver.reserved, "actual drain not released");
        done("writer_drain_timeout_never_releases_or_restarts_early");
    }
    private static void readinessDeadlineDecision() throws Exception {
        FakeDriver driver = new FakeDriver(); driver.readyGate = new CountDownLatch(1);
        ProcessGatewayOwner owner = new ProcessGatewayOwner(driver, 100, 1000);
        SinglePackageGateway gateway = handle(owner);
        CompletableFuture<Void> ready = gateway.start(APP, true, initializer(driver, new AtomicInteger()));
        await(driver.readyDecision); Thread.sleep(180);
        check(gateway.state() == SinglePackageGateway.State.READY && !ready.isDone(), "deadline overrode ready decision");
        driver.readyGate.countDown(); success(ready); success(gateway.closeAsync());
        done("barrier_ready_decision_cannot_race_hard_deadline_into_false_success");
    }
    private static void cancelledClaim() throws Exception {
        FakeDriver driver = new FakeDriver(); driver.claimGate = new CountDownLatch(1);
        ProcessGatewayOwner owner = new ProcessGatewayOwner(driver, 100, 1000);
        SinglePackageGateway gateway = handle(owner); AtomicInteger init = new AtomicInteger();
        CompletableFuture<Void> ready = gateway.start(APP, true, initializer(driver, init));
        await(driver.enteredClaim); failure(ready); driver.claimGate.countDown(); success(gateway.drained());
        check(init.get() == 0 && driver.constructions.get() == 0, "late claim began new writes after cancel");
        done("late_claim_after_deadline_never_begins_initializer");
    }
    private static void gatesContextsAndPortConflict() throws Exception {
        FakeDriver driver = new FakeDriver(); ProcessGatewayOwner owner = new ProcessGatewayOwner(driver, 1000, 1000);
        SinglePackageGateway gateway = handle(owner); AtomicInteger init = new AtomicInteger();
        failure(gateway.start(APP)); failure(gateway.start(APP, false, initializer(driver, init)));
        check(driver.claims.get() == 0, "resource gate bypassed");
        Context activity = new Context() { public Context getApplicationContext() { return APP; } };
        success(gateway.start(activity, true, initializer(driver, init)));
        check(driver.constructedContext == APP, "Activity context retained");
        failure(handle(owner).start(new Context(), true, initializer(driver, init)));
        failure(gateway.start(APP, false, initializer(driver, init)));
        check(gateway.state() == SinglePackageGateway.State.READY, "rejected gate lost active handle");
        success(gateway.closeAsync());
        driver.portConflict = true;
        failure(gateway.start(APP, true, initializer(driver, init))); success(gateway.drained());
        check(driver.registrations == 1 && !driver.reserved, "port conflict attached to foreign listener");
        done("resource_context_gate_and_port_conflict_fail_closed_without_attach");
    }
    private static void stoppedDeadlineDecision() throws Exception {
        FakeDriver driver = new FakeDriver(); driver.stickWriters = true;
        driver.stopPublicationGate = new CountDownLatch(1);
        SinglePackageGateway gateway = handle(new ProcessGatewayOwner(driver, 1000, 100));
        success(gateway.start(APP, true, initializer(driver, new AtomicInteger())));
        CompletableFuture<Void> stopped = gateway.closeAsync();
        await(driver.stopDecision); // Timeout selected, but publication is held.
        check(!stopped.isDone(), "stop barrier did not hold publication");
        check(driver.stubbornWriter.isAlive(), "stubborn writer model exited early");
        driver.writerExit.countDown(); success(gateway.drained());
        check(gateway.state() == SinglePackageGateway.State.FAILED, "actual drain overwrote timeout failure");
        driver.stopPublicationGate.countDown(); failure(stopped);
        done("barrier_stopped_timeout_decision_stays_failed_after_actual_drain");
    }
    private static void registrationAndBindFailures() throws Exception {
        for (int phase = 1; phase <= 2; phase++) {
            FakeDriver driver = new FakeDriver(); driver.registerFailure = phase;
            SinglePackageGateway gateway = handle(new ProcessGatewayOwner(driver, 1000, 1000));
            failure(gateway.start(APP, true, initializer(driver, new AtomicInteger()))); success(gateway.drained());
            check(driver.closeCalls == 1 && driver.releases.get() == 1 && !driver.reserved, "registration failure leaked owner");
        }
        done("registration_before_and_after_failure_drains_only_owned_resources");
        FakeDriver driver = new FakeDriver(); driver.bindFailure = true;
        SinglePackageGateway gateway = handle(new ProcessGatewayOwner(driver, 1000, 1000));
        failure(gateway.start(APP, true, initializer(driver, new AtomicInteger()))); success(gateway.drained());
        check(gateway.state() == SinglePackageGateway.State.FAILED && driver.registrations == 1 && !driver.reserved, "bind failure became ready/attached");
        done("own_listener_bind_failure_never_becomes_ready_or_attaches_foreign_port");
    }
    private static void blockedPublicFutureDependents() throws Exception {
        FakeDriver driver = new FakeDriver();
        ProcessGatewayOwner owner = new ProcessGatewayOwner(driver, 100, 1000);
        SinglePackageGateway gateway = handle(owner);
        CountDownLatch releaseDependents = new CountDownLatch(1);
        for (int index = 0; index < 3; index++) {
            driver.constructorGate = new CountDownLatch(1);
            CountDownLatch dependentEntered = new CountDownLatch(1);
            CompletableFuture<Void> ready = gateway.start(APP, true, initializer(driver, new AtomicInteger()));
            ready.whenComplete((value, error) -> { dependentEntered.countDown(); LocalGatewayServer.await(releaseDependents); });
            failure(ready); await(dependentEntered);
            driver.constructorGate.countDown(); success(gateway.drained()); success(gateway.closeAsync());
        }
        releaseDependents.countDown();
        done("blocked_ready_dependents_cannot_exhaust_hard_deadline_threads");
        FakeDriver next = new FakeDriver();
        SinglePackageGateway other = handle(new ProcessGatewayOwner(next, 1000, 1000));
        success(other.start(APP, true, initializer(next, new AtomicInteger())));
        CountDownLatch entered = new CountDownLatch(1), release = new CountDownLatch(1);
        other.drained().thenRun(() -> { entered.countDown(); LocalGatewayServer.await(release); });
        CompletableFuture<Void> stopped = other.closeAsync();
        await(entered); success(stopped); release.countDown();
        done("blocked_drained_dependent_cannot_block_stopped_future");
    }
    private static void publicReservationObservation() throws Exception {
        check(!SinglePackageGateway.hasActiveProcessReservation(), "unexpected initial process reservation");
        SinglePackageGateway gateway = new SinglePackageGateway(null);
        CountDownLatch entered = new CountDownLatch(1), release = new CountDownLatch(1);
        CompletableFuture<Void> ready = gateway.start(APP, true, app -> { entered.countDown(); release.await(); });
        await(entered);
        check(!GatewayService.isRunning() && SinglePackageGateway.hasActiveProcessReservation(), "readonly probe missed stopped initializer reservation");
        CompletableFuture<Void> stopped = gateway.closeAsync(); failure(ready);
        check(SinglePackageGateway.hasActiveProcessReservation() && !stopped.isDone(), "cancel falsely erased reservation");
        release.countDown(); success(gateway.drained()); success(stopped);
        check(!SinglePackageGateway.hasActiveProcessReservation(), "probe stayed busy after actual release");
        done("public_readonly_reservation_includes_running_false_initializer_and_cancel_drain");
    }
    private static void phasedBudgets() throws Exception {
        FakeDriver driver = new FakeDriver(); driver.constructorGate = new CountDownLatch(1);
        ProcessGatewayOwner owner = new ProcessGatewayOwner(driver, 1000, 1000);
        SinglePackageGateway gateway = handle(owner);
        CompletableFuture<Void> ready = gateway.start(APP, true, app -> Thread.sleep(60),
            SinglePackageGateway.StartupBudget.phasedForHostTests(120, 600));
        await(driver.enteredConstructor); Thread.sleep(200);
        check(!ready.isDone() && gateway.state() != SinglePackageGateway.State.FAILED,
            "late prestart timer killed current construct/bind phase");
        failure(ready); check(owner.hasActiveReservation(), "bind timeout released blocked constructor");
        driver.constructorGate.countDown(); success(gateway.drained());
        done("phased_old_timer_ignored_then_new_construct_bind_deadline_fails");

        FakeDriver slow = new FakeDriver(); ProcessGatewayOwner slowOwner = new ProcessGatewayOwner(slow, 1000, 100);
        SinglePackageGateway slowHandle = handle(slowOwner);
        CountDownLatch initEntered = new CountDownLatch(1), initRelease = new CountDownLatch(1);
        ready = slowHandle.start(APP, true, app -> { initEntered.countDown(); initRelease.await(); },
            SinglePackageGateway.StartupBudget.phasedForHostTests(100, 1000));
        await(initEntered); failure(ready); failure(slowHandle.closeAsync());
        check(slowOwner.hasActiveReservation() && slow.constructions.get() == 0, "prestart timeout continued construction");
        initRelease.countDown(); success(slowHandle.drained());
        done("phased_prestart_timeout_retains_blocked_initializer_until_real_exit");

        FakeDriver cancelled = new FakeDriver(); ProcessGatewayOwner cancelledOwner = new ProcessGatewayOwner(cancelled, 1000, 100);
        SinglePackageGateway cancelledHandle = handle(cancelledOwner);
        CountDownLatch entered = new CountDownLatch(1), release = new CountDownLatch(1);
        ready = cancelledHandle.start(APP, true, app -> { entered.countDown(); release.await(); },
            SinglePackageGateway.StartupBudget.phasedForHostTests(1000, 1000));
        await(entered); CompletableFuture<Void> stopped = cancelledHandle.closeAsync(); failure(ready); failure(stopped);
        check(cancelledOwner.hasActiveReservation(), "phase cancellation released live initializer");
        release.countDown(); success(cancelledHandle.drained());
        check(cancelled.constructions.get() == 0, "cancelled initializer entered bind phase");
        done("phased_cancel_blocked_initializer_never_enters_next_budget");

        FakeDriver successDriver = new FakeDriver(); SinglePackageGateway successHandle = handle(new ProcessGatewayOwner(successDriver, 80, 1000));
        success(successHandle.start(APP, true, app -> Thread.sleep(160),
            SinglePackageGateway.StartupBudget.phasedForHostTests(600, 300)));
        success(successHandle.closeAsync());
        FakeDriver original = new FakeDriver(); SinglePackageGateway defaultHandle = handle(new ProcessGatewayOwner(original, 80, 1000));
        failure(defaultHandle.start(APP, true, app -> Thread.sleep(160))); success(defaultHandle.drained());
        check(original.constructions.get() == 0, "default continuous deadline silently widened");
        done("explicit_phase_budget_extends_hook_without_changing_default_continuous_deadline");
    }
    private static void handoffSameStoreSingleConsumption() throws Exception {
        FakeDriver driver = new FakeDriver();
        ProcessGatewayOwner owner = new ProcessGatewayOwner(driver, 1000, 1000);
        SinglePackageGateway gateway = handle(owner);
        LocalProfileStore prepared = new LocalProfileStore(APP);
        HandoffInitializer hook = new HandoffInitializer(prepared);
        success(gateway.start(APP, true, hook));
        check(driver.handedStore == prepared, "construct did not receive the exact prepared store");
        check(driver.handoffTakes.get() == 1, "handoff consumed more or less than once");
        check(driver.handedHandoff != null && driver.handedHandoff.consumed() && !driver.handedHandoff.available(),
            "handoff still reusable after construct");
        try {
            synchronized (driver.lock) { driver.handedHandoff.take(); }
            throw new AssertionError("second consumption succeeded");
        } catch (IOException expected) { }
        try {
            synchronized (driver.lock) { hook.sink.publish(prepared); }
            throw new AssertionError("second publication succeeded");
        } catch (IOException expected) { }
        success(gateway.closeAsync()); success(gateway.drained());
        done("prepared_profile_store_handed_to_construct_once_same_identity");
    }
    private static void profileStoreHandoffIsOneShotStoreOnly() throws Exception {
        Object lock = new Object();
        LocalProfileStore store = new LocalProfileStore(APP);
        ProfileStoreHandoff handoff = new ProfileStoreHandoff(lock);
        try {
            synchronized (lock) { handoff.take(); }
            throw new AssertionError("unpublished handoff consumed");
        } catch (IOException expected) { }
        handoff.publish(store);
        try {
            handoff.take();
            throw new AssertionError("handoff consumed without SAVE_ACCESS");
        } catch (IOException expected) { }
        LocalProfileStore taken;
        synchronized (lock) { taken = handoff.take(); }
        check(taken == store, "handoff did not return the published store instance");
        try {
            synchronized (lock) { handoff.take(); }
            throw new AssertionError("handoff consumed twice");
        } catch (IOException expected) { }
        try {
            handoff.publish(store);
            throw new AssertionError("handoff published twice");
        } catch (IOException expected) { }
        for (Field candidate : ProfileStoreHandoff.class.getDeclaredFields())
            check(candidate.getType() != byte[].class, "handoff retains profile bytes");
        ProfileStoreHandoff closed = new ProfileStoreHandoff(lock);
        closed.invalidate();
        try { closed.publish(store); throw new AssertionError("closed handoff published"); }
        catch (IOException expected) { }
        try { synchronized (lock) { closed.take(); } throw new AssertionError("closed handoff consumed"); }
        catch (IOException expected) { }
        done("profile_store_handoff_is_typed_one_shot_store_not_bytes");
    }
    private static void missingOrFailedInitializerNeverPublishesOrConstructs() throws Exception {
        FakeDriver missingDriver = new FakeDriver();
        SinglePackageGateway missingGateway = handle(new ProcessGatewayOwner(missingDriver, 1000, 1000));
        LocalProfileStore missingStore = new LocalProfileStore(APP);
        HandoffInitializer missingHook = new HandoffInitializer(missingStore);
        missingHook.publish = false;
        failure(missingGateway.start(APP, true, missingHook));
        success(missingGateway.drained());
        check(missingDriver.constructions.get() == 0 && missingGateway.state() != SinglePackageGateway.State.READY,
            "missing handoff reached construct or READY");
        try { missingHook.sink.publish(missingStore); throw new AssertionError("failed session handoff published"); }
        catch (IOException expected) { }
        done("missing_prepared_handoff_fails_before_construct_with_no_publication");

        FakeDriver failingDriver = new FakeDriver();
        SinglePackageGateway failingGateway = handle(new ProcessGatewayOwner(failingDriver, 1000, 1000));
        LocalProfileStore failingStore = new LocalProfileStore(APP);
        HandoffInitializer failingHook = new HandoffInitializer(failingStore);
        failingHook.throwFailure = true;
        failure(failingGateway.start(APP, true, failingHook));
        success(failingGateway.drained());
        check(failingDriver.constructions.get() == 0 && failingGateway.state() == SinglePackageGateway.State.FAILED,
            "failed initializer built a listener or became READY");
        try { failingHook.sink.publish(failingStore); throw new AssertionError("failed initializer session published"); }
        catch (IOException expected) { }
        done("failed_initializer_never_publishes_handoff_or_reaches_ready");

        FakeDriver cancelledDriver = new FakeDriver();
        SinglePackageGateway cancelledGateway = handle(new ProcessGatewayOwner(cancelledDriver, 1000, 1000));
        LocalProfileStore cancelledStore = new LocalProfileStore(APP);
        HandoffInitializer cancelledHook = new HandoffInitializer(cancelledStore);
        cancelledHook.gate = new CountDownLatch(1);
        CompletableFuture<Void> ready = cancelledGateway.start(APP, true, cancelledHook);
        await(cancelledHook.entered);
        CompletableFuture<Void> stopped = cancelledGateway.closeAsync();
        cancelledHook.gate.countDown();
        failure(ready); success(stopped); success(cancelledGateway.drained());
        check(cancelledHook.publishFailure != null && cancelledDriver.constructions.get() == 0,
            "cancelled initializer published or constructed");
        check(cancelledGateway.state() != SinglePackageGateway.State.READY, "cancelled startup became READY");
        try { cancelledHook.sink.publish(cancelledStore); throw new AssertionError("cancelled session handoff reused"); }
        catch (IOException expected) { }
        done("cancelled_initializer_never_publishes_handoff_or_reaches_ready");
    }
    private static void consumedHandoffNeverReusedByLaterSession() throws Exception {
        FakeDriver driver = new FakeDriver();
        ProcessGatewayOwner owner = new ProcessGatewayOwner(driver, 1000, 1000);
        SinglePackageGateway gateway = handle(owner);
        LocalProfileStore firstStore = new LocalProfileStore(APP);
        success(gateway.start(APP, true, new HandoffInitializer(firstStore)));
        ProfileStoreHandoff firstHandoff = driver.handedHandoff;
        check(driver.handedStore == firstStore && firstHandoff != null, "first session did not consume its store");
        success(gateway.closeAsync()); success(gateway.drained());
        check(firstHandoff.consumed() && !firstHandoff.available(), "drained session handoff stayed reusable");
        try {
            synchronized (driver.lock) { firstHandoff.take(); }
            throw new AssertionError("old handoff consumed after drain");
        } catch (IOException expected) { }
        LocalProfileStore secondStore = new LocalProfileStore(APP);
        success(gateway.start(APP, true, new HandoffInitializer(secondStore)));
        check(driver.handedStore == secondStore && driver.handedHandoff != firstHandoff,
            "later session reused the old handoff or store");
        success(gateway.closeAsync()); success(gateway.drained());
        try {
            synchronized (driver.lock) { firstHandoff.take(); }
            throw new AssertionError("old handoff consumed after later drain");
        } catch (IOException expected) { }
        done("close_drain_then_new_session_never_reuses_old_handoff");
    }
    private static void failedConstructConsumesHandoffWithoutReuse() throws Exception {
        FakeDriver driver = new FakeDriver();
        driver.failConstructAfterHandoff = true;
        ProcessGatewayOwner owner = new ProcessGatewayOwner(driver, 1000, 1000);
        SinglePackageGateway gateway = handle(owner);
        LocalProfileStore firstStore = new LocalProfileStore(APP);
        failure(gateway.start(APP, true, new HandoffInitializer(firstStore)));
        success(gateway.drained());
        ProfileStoreHandoff failedHandoff = driver.handedHandoff;
        check(driver.handoffTakes.get() == 1 && driver.handedStore == firstStore && failedHandoff != null,
            "failed construct did not consume the prepared handoff exactly once");
        check(failedHandoff.consumed() && !failedHandoff.available(), "failed construct left a reusable handoff");
        try {
            synchronized (driver.lock) { failedHandoff.take(); }
            throw new AssertionError("failed construct handoff reused");
        } catch (IOException expected) { }
        driver.failConstructAfterHandoff = false;
        LocalProfileStore secondStore = new LocalProfileStore(APP);
        success(gateway.start(APP, true, new HandoffInitializer(secondStore)));
        check(driver.handoffTakes.get() == 2 && driver.handedStore == secondStore,
            "later session did not consume its own prepared store");
        success(gateway.closeAsync()); success(gateway.drained());
        done("failed_construct_consumes_handoff_and_later_session_gets_fresh_store");
    }
    private static void actualDriverUsesHandoffWithoutSecondColdStore() throws Exception {
        resetLegacy();
        ManagerLifecycleDriver driver = new ManagerLifecycleDriver();
        synchronized (driver.saveAccess()) {
            driver.claim(); driver.activate();
            LocalProfileStore prepared = new LocalProfileStore(APP);
            int constructions = HostControl.profileConstructions.get();
            ProfileStoreHandoff handoff = new ProfileStoreHandoff(driver.saveAccess());
            handoff.publish(prepared);
            driver.construct(APP, (running, detail) -> {}, handoff);
            check(HostControl.profileConstructions.get() == constructions,
                "handoff construct opened a second cold LocalProfileStore");
            check(handoff.consumed() && !handoff.available(), "actual driver did not consume handoff once");
            try { driver.construct(APP, (running, detail) -> {}, handoff); throw new AssertionError("actual driver reused handoff"); }
            catch (IOException expected) { }
            driver.closeOwned(); driver.release();
        }
        check(!GatewayService.isRunning() && field(GatewayService.class, "lastServer").get(null) == null,
            "handoff construct altered registry ownership");
        resetLegacy(); done("actual_driver_consumes_handoff_without_second_cold_store");
    }
    private static void ownerFailsClosedWhenHandoffNotConsumed() throws Exception {
        FakeDriver legacy = new FakeDriver();
        legacy.ignoreHandoffOverride = true;
        SinglePackageGateway legacyGateway = handle(new ProcessGatewayOwner(legacy, 1000, 1000));
        LocalProfileStore firstStore = new LocalProfileStore(APP);
        failure(legacyGateway.start(APP, true, new HandoffInitializer(firstStore)));
        success(legacyGateway.drained());
        check(legacy.constructions.get() == 0 && legacy.registrations == 0,
            "default construct overload accepted an unconsumed handoff or started listeners");
        check(legacyGateway.state() == SinglePackageGateway.State.FAILED, "unconsumed handoff became READY");
        done("default_driver_construct_overload_rejects_required_handoff");

        FakeDriver skipping = new FakeDriver();
        skipping.skipHandoffTake = true;
        SinglePackageGateway skippingGateway = handle(new ProcessGatewayOwner(skipping, 1000, 1000));
        LocalProfileStore secondStore = new LocalProfileStore(APP);
        failure(skippingGateway.start(APP, true, new HandoffInitializer(secondStore)));
        success(skippingGateway.drained());
        check(skipping.constructions.get() == 1, "fake driver did not reach construct");
        check(skipping.handoffTakes.get() == 0 && skipping.registrations == 0,
            "unconsumed handoff reached registration/listeners");
        check(skipping.handedHandoff != null && !skipping.handedHandoff.consumed(),
            "unconsumed handoff was consumed unexpectedly");
        check(!skipping.handedHandoff.available(), "unconsumed handoff remained reusable after fail");
        check(skippingGateway.state() == SinglePackageGateway.State.FAILED, "unconsumed handoff construction became READY");
        done("owner_fails_closed_when_construct_does_not_consume_required_handoff");
    }
    private static Field field(Class<?> type, String name) throws Exception {
        Field field = type.getDeclaredField(name); field.setAccessible(true); return field;
    }
    private static void resetLegacy() throws Exception {
        field(GatewayService.class, "lastServer").set(null, null);
        field(GatewayService.class, "lastServerThread").set(null, null);
        ((AtomicBoolean) field(GatewayService.class, "RUNNING").get(null)).set(false);
        HostControl.failAt = null; HostControl.blockAt = null;
        HostControl.constructorEntered = new CountDownLatch(1);
        HostControl.constructorRelease = new CountDownLatch(0);
        HostControl.profileConstructions.set(0);
    }
    private static LocalGatewayServer legacy(boolean stopped) throws Exception {
        LocalGatewayServer server = new LocalGatewayServer(23333, null, null, null, null, null, null, null, (r, d) -> {});
        if (stopped) server.close(); return server;
    }
    private static void actualDriverBlockedConstructor() throws Exception {
        resetLegacy(); HostControl.blockAt = "profiles";
        HostControl.constructorRelease = new CountDownLatch(1);
        ProcessGatewayOwner owner = new ProcessGatewayOwner(new ManagerLifecycleDriver(), 100, 120);
        SinglePackageGateway gateway = handle(owner);
        long start = System.nanoTime();
        CompletableFuture<Void> ready = gateway.start(APP, true, app -> {
            check(Thread.holdsLock(GatewayService.SAVE_ACCESS) && !GatewayService.isRunning(), "real API hook lock/state incorrect");
        });
        await(HostControl.constructorEntered); failure(ready); failure(gateway.closeAsync());
        check(TimeUnit.NANOSECONDS.toMillis(System.nanoTime() - start) < 1200, "stub constructor blocked deadline");
        check(GatewayService.isRunning() && !gateway.drained().isDone(), "blocked new LocalProfileStore released reservation");
        failure(handle(owner).start(APP, true, app -> {}));
        check(HostControl.profileConstructions.get() == 1, "second actual driver entered constructor");
        HostControl.constructorRelease.countDown(); success(gateway.drained());
        check(!GatewayService.isRunning() && field(GatewayService.class, "lastServer").get(null) == null, "late constructor did not drain own resources");
        resetLegacy(); done("actual_production_driver_blocked_new_profile_constructor_hard_deadline");
    }
    private static void activeLegacyUntouched() throws Exception {
        resetLegacy(); LocalGatewayServer other = legacy(false);
        field(GatewayService.class, "lastServer").set(null, other);
        ProcessGatewayOwner owner = new ProcessGatewayOwner(new ManagerLifecycleDriver(), 1000, 1000);
        SinglePackageGateway gateway = handle(owner); AtomicInteger init = new AtomicInteger();
        failure(gateway.start(APP, true, app -> init.incrementAndGet())); success(gateway.drained());
        check(init.get() == 0 && other.closeCalls == 0, "touched active legacy server");
        check(field(GatewayService.class, "lastServer").get(null) == other, "erased legacy reference");
        other.close(); resetLegacy(); done("actual_driver_preserves_active_legacy_server");
    }
    private static void constructorBeforeRegistrationPreservesLegacy() throws Exception {
        resetLegacy(); LocalGatewayServer previous = legacy(true); Thread previousThread = new Thread(() -> {});
        field(GatewayService.class, "lastServer").set(null, previous);
        field(GatewayService.class, "lastServerThread").set(null, previousThread);
        HostControl.failAt = "bootstrap";
        ManagerLifecycleDriver driver = new ManagerLifecycleDriver();
        synchronized (driver.saveAccess()) {
            driver.claim(); check(!GatewayService.isRunning(), "prestart RUNNING=true"); driver.activate();
            try { driver.construct(APP, (r, d) -> {}); throw new AssertionError("expected constructor failure"); }
            catch (IOException expected) {}
        }
        driver.closeOwned(); synchronized (driver.saveAccess()) { driver.release(); }
        check(field(GatewayService.class, "lastServer").get(null) == previous, "cleared unowned server before registration");
        check(field(GatewayService.class, "lastServerThread").get(null) == previousThread, "cleared unowned thread");
        check(previous.closeCalls == 1 && !GatewayService.isRunning(), "closed/reflagged legacy reference");
        resetLegacy(); done("actual_driver_constructor_failure_preserves_legacy_registry");
    }
    private static void partialRegistrationAndForeignValues() throws Exception {
        resetLegacy(); LocalGatewayServer previous = legacy(true);
        field(GatewayService.class, "lastServer").set(null, previous);
        ManagerLifecycleDriver driver = new ManagerLifecycleDriver(() -> { throw new IllegalStateException("host fault after server field write"); });
        synchronized (driver.saveAccess()) {
            driver.claim(); driver.activate(); driver.construct(APP, (r, d) -> {});
            try { driver.register(new Thread(() -> {})); throw new AssertionError("expected registration failure"); }
            catch (IllegalStateException expected) {}
            check(field(GatewayService.class, "lastServer").get(null) != previous, "partial registration not reproduced");
            driver.closeOwned(); driver.release();
        }
        check(field(GatewayService.class, "lastServer").get(null) == previous && !GatewayService.isRunning(), "partial registration cleanup erased legacy");
        resetLegacy(); driver = new ManagerLifecycleDriver();
        LocalGatewayServer foreign = legacy(false);
        synchronized (driver.saveAccess()) {
            driver.claim(); driver.activate(); driver.construct(APP, (r, d) -> {}); driver.register(new Thread(() -> {}));
            field(GatewayService.class, "lastServer").set(null, foreign);
            driver.closeOwned();
            try { driver.release(); throw new AssertionError("expected foreign ownership failure"); }
            catch (IllegalStateException expected) {}
        }
        check(field(GatewayService.class, "lastServer").get(null) == foreign && foreign.closeCalls == 0 && GatewayService.isRunning(), "foreign registry modified");
        foreign.close(); resetLegacy(); done("actual_driver_partial_registration_restore_and_foreign_owner_retention");
    }
    public static void main(String[] args) throws Exception {
        hardBlockedConstructor(); closeDuringInitializer(); failedInitialization();
        concurrentHandlesAndRestart(); stuckWriters(); readinessDeadlineDecision();
        cancelledClaim(); gatesContextsAndPortConflict(); stoppedDeadlineDecision();
        publicReservationObservation(); phasedBudgets();
        handoffSameStoreSingleConsumption(); profileStoreHandoffIsOneShotStoreOnly();
        missingOrFailedInitializerNeverPublishesOrConstructs(); consumedHandoffNeverReusedByLaterSession();
        failedConstructConsumesHandoffWithoutReuse(); actualDriverUsesHandoffWithoutSecondColdStore();
        ownerFailsClosedWhenHandoffNotConsumed();
        registrationAndBindFailures(); blockedPublicFutureDependents(); actualDriverBlockedConstructor(); activeLegacyUntouched();
        constructorBeforeRegistrationPreservesLegacy(); partialRegistrationAndForeignValues();
        System.out.println("HOST_LIFECYCLE_TESTS_PASSED=" + passed);
    }
}
