package com.project7.localmanager;

import android.content.Context;
import android.util.Log;
import com.forever7.offline.ResourceImporter;
import com.forever7.offline.Project7RepairHost;
import java.util.function.Consumer;
import com.netease.qrzd.AutoLoginCore;
import java.io.File;
import java.io.IOException;
import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.concurrent.CompletableFuture;
import java.util.concurrent.CompletionException;
import java.util.concurrent.ExecutionException;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.TimeoutException;
import java.util.concurrent.atomic.AtomicBoolean;

/** Process-wide preparation ownership. Activity tickets never own another session. */
public final class Project7StartupCoordinator {
    private static final String DIAGNOSTIC_TAG = "P7Startup";

    /** Privacy-safe stage/type/stack only; never log messages, accounts or secrets. */
    private static void diagnosticStage(String stage) {
        try { Log.i(DIAGNOSTIC_TAG, "stage=" + stage); }
        catch (Throwable ignored) { /* Diagnostics never alter startup semantics. */ }
    }

    private static Throwable diagnosticCause(Throwable error) {
        Throwable current = error;
        for (int depth = 0; depth < 4 && current.getCause() != null &&
                (current instanceof ExecutionException || current instanceof CompletionException); depth++)
            current = current.getCause();
        return current;
    }

    private static void diagnosticFailure(String stage, Throwable error) {
        Throwable cause = diagnosticCause(error);
        StringBuilder text = new StringBuilder("stage=").append(stage)
            .append(" type=").append(cause.getClass().getName())
            .append(" cause=").append(cause.getCause() == null ? "none" : cause.getCause().getClass().getName());
        StackTraceElement[] frames = cause.getStackTrace();
        for (int i = 0; i < frames.length && i < 12; i++) {
            StackTraceElement frame = frames[i];
            text.append(" frame=").append(frame.getClassName()).append('#')
                .append(frame.getMethodName()).append(':').append(frame.getLineNumber());
        }
        try { Log.w(DIAGNOSTIC_TAG, text.toString()); }
        catch (Throwable ignored) { /* Diagnostics never alter startup semantics. */ }
    }

    private static Project7StartupCoordinator instance;
    public static synchronized Project7StartupCoordinator get(Context context) {
        Context app = context == null ? null : context.getApplicationContext();
        if (app == null) throw new IllegalArgumentException("Application context required");
        if (instance == null) instance = new Project7StartupCoordinator(app, new Project7StartupPlatform(app));
        else if (instance.app != app) throw new IllegalStateException("Different application context");
        return instance;
    }
    public interface Status { void update(String message); }
    interface Guard { boolean cancelled(); }
    interface Backend {
        CompletableFuture<Void> start();
        boolean hookExecuted();
        boolean ownerReady();
        boolean ownerFailed();
        StableIdentityBootstrap.PreparedIdentity identity();
        AutoLoginCore.Credentials credentials();
        void closeIfOwned();
        CompletableFuture<Void> drained();
    }
    interface Services {
        boolean foreignOwnerActive(); // observation only, no lock held over downloads
        void installProvider(AutoLoginCore.SessionProvider provider);
        Evidence publish(File documents, List<ResourceImporter.Entry> entries, AtomicBoolean cancel, Status status) throws Exception;
        Backend backend(Guard guard);
        String approvedPolicy();
        Project7RepairHost.Lease watchRepair(File documents, Consumer<Project7RepairHost.Lease> repair) throws Exception;
    }
    /** Production source is the exact publish() Receipt; host injection is explicit. */
    static final class Evidence {
        final Object receipt;
        final String snapshotHash, bindingHash;
        final int entries;
        Evidence(Object receipt, String snapshotHash, String bindingHash, int entries) {
            if (receipt == null || snapshotHash == null || !snapshotHash.matches("[0-9a-f]{64}") || bindingHash == null || !bindingHash.matches("[0-9a-f]{64}") || entries != 312)
                throw new IllegalArgumentException("Missing fresh resource publication");
            this.receipt = receipt; this.snapshotHash = snapshotHash; this.bindingHash = bindingHash; this.entries = entries;
        }
    }
    private static final class Attempt {
        final AtomicBoolean cancelled = new AtomicBoolean();
        AtomicBoolean activityCancellation;
        boolean handedOff;
        boolean gameMayBeRunning;
        boolean prepared;
        boolean repairAccepted;
        Object repairEpoch;
        Project7RepairHost.Lease repairLease;
        Evidence evidence;
        Backend backend;
        Ticket resourceWork;
        StableIdentityBootstrap.PreparedIdentity identity;
        AutoLoginCore.Credentials credentials;
        Attempt(AtomicBoolean cancellation) { activityCancellation = cancellation; }
    }
    public static final class Ticket {
        private final Attempt attempt;
        private final boolean creator;
        private boolean workerFinished;
        private boolean prepareStarted;
        private Ticket(Attempt attempt, boolean creator) { this.attempt = attempt; this.creator = creator; }
        public boolean reusesHandedOffGame() { return !creator; }
    }
    private final Context app;
    private final Services services;
    private Attempt current;
    private boolean providerInstalled;
    Project7StartupCoordinator(Context app, Services services) { this.app = app; this.services = services; }

    /** Worker pre-hook, before the base importer opens or writes anything. */
    public synchronized Ticket reserve(AtomicBoolean cancellation, Ticket previous) throws IOException {
        if (cancellation == null || cancellation.get()) throw cancelled();
        if (current != null) {
            if (current.handedOff && healthy(current) && current.repairLease != null && current.repairLease.active()) return new Ticket(current, false);
            if (current.gameMayBeRunning && !healthy(current))
                throw new IOException("游戏可能仍在读取素材，请完整关闭应用后再准备。数据已保留。");
            if (previous != null && previous.creator && previous.attempt == current &&
                    previous == current.resourceWork && previous.workerFinished &&
                    !current.cancelled.get() && current.backend == null) {
                current.activityCancellation = cancellation;
                Ticket retry = new Ticket(current, true); current.resourceWork = retry; return retry;
            }
            boolean ending = current.cancelled.get() || (current.backend != null &&
                (current.backend.ownerFailed() || (current.prepared && !healthy(current))));
            if (ending && drained(current)) current = null;
            else throw new IOException("本地游戏仍在准备或停止，请稍后重试。");
        }
        if (services.foreignOwnerActive()) throw new IOException("已有本地服务或存档写入在运行，未改动资源或账号。");
        Attempt attempt = new Attempt(cancellation);
        Ticket ticket = new Ticket(attempt, true); attempt.resourceWork = ticket; current = attempt;
        try {
            if (!providerInstalled) {
                services.installProvider(this::currentSession); providerInstalled = true;
            }
        } catch (Throwable ignored) {
            diagnosticFailure("PROVIDER_INSTALL", ignored);
            current = null; throw new IOException("登录交接尚不可用，未启动游戏。");
        }
        return ticket;
    }
    /** Worker post-hook. The downloader must already have closed its importer. */
    public void prepare(Ticket ticket, File documents, List<ResourceImporter.Entry> entries, Status status) throws IOException {
        Attempt attempt = creator(ticket);
        String stage = "RESOURCE_PUBLISH";
        try {
            AtomicBoolean flag;
            synchronized (this) {
                requireCurrent(attempt); if (cancelled(attempt)) throw cancelled();
                flag = attempt.activityCancellation;
            }
            notifyStatus(status, "正在核验游戏素材与本地启动凭据。");
            List<ResourceImporter.Entry> manifest = Collections.unmodifiableList(new ArrayList<>(entries));
            Evidence evidence = services.publish(documents, manifest, flag, message -> notifyStatus(status, message));
            if (evidence == null) throw new IOException("未形成新的资源核验凭据。");
            synchronized (this) {
                requireCurrent(attempt); if (cancelled(attempt)) throw cancelled();
                attempt.evidence = evidence;
            }
            notifyStatus(status, "正在准备本地身份、档案和收藏，首次可能需要数分钟。");
            stage = "BACKEND_CONSTRUCT";
            diagnosticStage(stage);
            Backend backend = services.backend(() -> cancelledNow(attempt));
            CompletableFuture<Void> ready;
            synchronized (this) {
                requireCurrent(attempt); if (cancelled(attempt)) throw cancelled();
                attempt.backend = backend;
                // Nonblocking initiation only. No SAVE_ACCESS or future wait here.
                stage = "BACKEND_START";
                diagnosticStage(stage);
                ready = backend.start();
            }
            stage = "BACKEND_READY";
            diagnosticStage(stage);
            while (true) {
                if (cancelledNow(attempt)) throw cancelled();
                try { ready.get(50, TimeUnit.MILLISECONDS); break; }
                catch (TimeoutException waiting) { /* UI cancellation stays responsive. */ }
            }
            synchronized (this) {
                requireCurrent(attempt);
                if (cancelled(attempt) || !backend.hookExecuted() || !backend.ownerReady())
                    throw new IOException("当前启动预约未完成，未连接其它本地服务。");
                stage = "IDENTITY_CREDENTIALS";
                diagnosticStage(stage);
                StableIdentityBootstrap.PreparedIdentity identity = backend.identity();
                AutoLoginCore.Credentials credentials = backend.credentials();
                if (identity == null || !identity.postProfilePolicyApplied() ||
                        !services.approvedPolicy().equals(identity.postProfilePolicy()) || credentials == null ||
                        !identity.identity().username().equals(credentials.username) || identity.identity().numericId() <= 0)
                    throw new IOException("本地身份或收藏准备尚未完成。");
                attempt.identity = identity; attempt.credentials = credentials; attempt.prepared = true;
                if (!healthy(attempt)) throw new IOException("本地服务状态已变化，未启动游戏。");
            }
            stage = "REPAIR_NOTIFICATION";
            diagnosticStage(stage);
            prepareRepairNotification(attempt, documents);
            notifyStatus(status, "本地游戏已准备，正在进入。");
        } catch (InterruptedException ignored) {
            Thread.currentThread().interrupt(); abandon(ticket); throw cancelled();
        } catch (Throwable error) {
            diagnosticFailure(stage, error);
            abandon(ticket);
            if (error instanceof ResourceImporter.Cancelled) throw cancelled();
            // Do not expose underlying callback/storage messages or credentials.
            throw new IOException("本地游戏准备未完成。数据已保留，请等待停止后重试。");
        }
    }
    public synchronized void requireHandoff(Ticket ticket) throws IOException {
        if (!validTicket(ticket) || !healthy(current) || current.repairLease == null || !current.repairLease.active())
            throw new IOException("本地启动状态已变化，未进入游戏。");
        // Sticky before startActivity: no Activity/backend event proves native
        // C_file workers stopped. A failed/uncertain dispatch requires process restart.
        current.gameMayBeRunning = true;
    }
    /** Call only after the base startActivity handoff returned successfully. */
    public synchronized void handedOff(Ticket ticket) throws IOException {
        if (validTicket(ticket)) current.gameMayBeRunning = true;
        if (!validTicket(ticket) || !healthy(current, true))
            throw new IOException("本地交接状态已变化。");
        current.handedOff = true;
        // Base Activity.onDestroy sets its flag even on normal successful finish.
        // It must no longer own process lifetime after this point.
        current.activityCancellation = null;
    }
    public void abandon(Ticket ticket) {
        Backend backend;
        Project7RepairHost.Lease repairLease;
        synchronized (this) {
            if (ticket == null || !ticket.creator || ticket.attempt != current || ticket != current.resourceWork || current.handedOff || current.cancelled.get()) return;
            current.cancelled.set(true);
            if (current.activityCancellation != null) current.activityCancellation.set(true);
            backend = current.backend; repairLease = current.repairLease;
        }
        if (repairLease != null) repairLease.close();
        // A start() that joined an unrelated reservation never authorizes close.
        if (backend != null) backend.closeIfOwned();
    }
    /** Worker-only: one nonce/observer per original Attempt, retained on healthy reuse. */
    private void prepareRepairNotification(Attempt attempt, File documents) throws Exception {
        Object epoch = new Object();
        synchronized (this) {
            requireCurrent(attempt);
            if (!healthy(attempt) || attempt.repairLease != null) throw new IOException("Repair notification state changed");
            attempt.repairEpoch = epoch;
        }
        Project7RepairHost.Lease lease = services.watchRepair(documents, accepted -> repairRequested(attempt, epoch, accepted));
        synchronized (this) {
            if (current == attempt && attempt.repairEpoch == epoch && healthy(attempt) && lease != null && lease.active()) {
                attempt.repairLease = lease; return;
            }
        }
        if (lease != null) lease.close();
        throw new IOException("Repair notification unavailable");
    }
    private void repairRequested(Attempt attempt, Object epoch, Project7RepairHost.Lease lease) {
        Backend backend;
        boolean clientMayRun;
        synchronized (this) {
            if (current != attempt || attempt.repairEpoch != epoch || attempt.repairAccepted ||
                    attempt.cancelled.get() || attempt.backend == null || !attempt.backend.hookExecuted()) return;
            attempt.repairAccepted = true; attempt.cancelled.set(true);
            // Invalidate provider before closing; handoff does not exempt repair.
            backend = attempt.backend; clientMayRun = attempt.gameMayBeRunning;
        }
        lease.close();
        try { backend.closeIfOwned(); }
        finally { if (clientMayRun) lease.awaitDrain(backend.drained()); }
    }
    private synchronized boolean cancelledNow(Attempt attempt) {
        return current != attempt || cancelled(attempt);
    }
    private boolean cancelled(Attempt attempt) {
        return attempt.cancelled.get() || (!attempt.handedOff && attempt.activityCancellation != null && attempt.activityCancellation.get()) ||
            (attempt.backend != null && attempt.backend.ownerFailed());
    }
    private boolean healthy(Attempt attempt) { return healthy(attempt, false); }
    private boolean healthy(Attempt attempt, boolean actualHandoff) {
        boolean invalid = attempt == null || attempt.cancelled.get() ||
            (attempt.backend != null && attempt.backend.ownerFailed()) ||
            (!actualHandoff && !attempt.handedOff && attempt.activityCancellation != null && attempt.activityCancellation.get());
        return !invalid && attempt.prepared && attempt.evidence != null &&
            attempt.evidence.receipt != null && attempt.backend != null && attempt.backend.hookExecuted() &&
            attempt.backend.ownerReady() && attempt.identity != null && attempt.backend.identity() == attempt.identity &&
            attempt.credentials != null && attempt.backend.credentials() == attempt.credentials &&
            attempt.identity.postProfilePolicyApplied() && services.approvedPolicy().equals(attempt.identity.postProfilePolicy());
    }
    private boolean drained(Attempt attempt) {
        // No backend is not evidence that an importer/publisher stopped.
        if (attempt.resourceWork == null || !attempt.resourceWork.workerFinished) return false;
        if (attempt.backend == null) return true;
        CompletableFuture<Void> drained = attempt.backend.drained();
        return drained.isDone() && !drained.isCancelled() && !drained.isCompletedExceptionally();
    }
    /** Called by AutoLogin for every snapshot/delivery check; no disk IO. */
    public synchronized AutoLoginCore.Session currentSession() {
        if (!healthy(current) || current.repairLease == null || !current.repairLease.active()) return null;
        // The unique Attempt OBJECT is the epoch. Never a String or equal-value token.
        return new AutoLoginCore.Session(current, true, true, true, current.credentials);
    }
    /** Base worker-finally signal, after its importer/publisher has closed.
     * The ticket is per worker job; a late old worker cannot finish a newer job.
     */
    public synchronized void workerFinished(Ticket ticket) {
        if (ticket != null && ticket.creator) ticket.workerFinished = true;
    }
    private boolean validTicket(Ticket ticket) {
        return ticket != null && ticket.attempt == current && (!ticket.creator || ticket == current.resourceWork);
    }
    private synchronized Attempt creator(Ticket ticket) throws IOException {
        if (!validTicket(ticket) || !ticket.creator || ticket.workerFinished || ticket.prepareStarted)
            throw new IOException("启动预约已失效或已经准备。");
        ticket.prepareStarted = true;
        return ticket.attempt;
    }
    private void requireCurrent(Attempt attempt) throws IOException { if (current != attempt) throw new IOException("启动预约已失效。"); }
    private static void notifyStatus(Status status, String message) {
        if (status != null) try { status.update(message); } catch (Throwable ignored) { /* UI is advisory. */ }
    }
    private static ResourceImporter.Cancelled cancelled() { return new ResourceImporter.Cancelled(); }
}
