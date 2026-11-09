package com.forever7.offline;

import com.project7.localmanager.Project7StartupCoordinator;
import android.os.Looper;
import java.io.File;
import java.util.List;
import java.util.concurrent.atomic.AtomicBoolean;

/** Project7 entry; the legacy ResourceInitActivity remains the default elsewhere. */
public class Project7ResourceInitActivity extends ResourceInitActivity {
    private volatile Project7StartupCoordinator.Ticket ticket;
    private final ThreadLocal<Project7StartupCoordinator.Ticket> workerTicket = new ThreadLocal<>();
    protected Project7StartupCoordinator coordinator() { return Project7StartupCoordinator.get(getApplicationContext()); }
    @Override protected boolean reusePreparedGame(AtomicBoolean cancellation) throws Exception {
        Project7StartupCoordinator.Ticket reserved = coordinator().reserve(cancellation, ticket);
        workerTicket.set(reserved); ticket = reserved; return reserved.reusesHandedOffGame();
    }
    @Override protected void prepareGame(File documents, List<ResourceImporter.Entry> entries,
                                         AtomicBoolean cancellation) throws Exception {
        coordinator().prepare(workerTicket.get(), documents, entries, this::preparationStatus);
    }
    @Override protected void preparationAbandoned() {
        Project7StartupCoordinator.Ticket own = workerTicket.get();
        if (own != null) coordinator().abandon(own);
        else if (Looper.myLooper() == Looper.getMainLooper()) coordinator().abandon(ticket);
    }
    @Override protected void preparationWorkerFinished() {
        Project7StartupCoordinator.Ticket own = workerTicket.get();
        try { if (own != null) coordinator().workerFinished(own); }
        finally { workerTicket.remove(); }
    }
    @Override protected void launchGame() {
        try {
            coordinator().requireHandoff(ticket);
            super.launchGame();
            coordinator().handedOff(ticket);
        } catch (Throwable ignored) {
            if (gameHandedOff()) {
                try { coordinator().handedOff(ticket); }
                catch (Throwable failed) { coordinator().abandon(ticket); }
            } else coordinator().abandon(ticket);
            preparationStatus("本地游戏交接未确认。数据已保留，请完整关闭应用后重试。");
        }
    }
}
