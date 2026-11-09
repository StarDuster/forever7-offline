package com.forever7.offline;

import android.app.Activity;
import android.app.AlertDialog;
import android.app.Application;
import android.content.Context;
import android.os.Bundle;
import android.os.FileObserver;
import android.os.Handler;
import android.os.Looper;
import java.io.File;
import java.io.IOException;
import java.lang.ref.WeakReference;
import java.util.concurrent.CompletableFuture;
import java.util.concurrent.atomic.AtomicBoolean;
import java.util.function.Consumer;

/** Process-lived notification/UI only. Client destruction is never a native stop ACK. */
public final class Project7RepairHost implements Application.ActivityLifecycleCallbacks {
    public interface Lease {
        boolean active();
        void close();
        void awaitDrain(CompletableFuture<Void> drained);
    }
    private static Project7RepairHost instance;
    private final Handler main = new Handler(Looper.getMainLooper());
    private WeakReference<Activity> resumed = new WeakReference<>(null);
    private Watch pending;
    private AlertDialog dialog;
    private Activity dialogOwner;
    private Project7RepairHost(Application app) { app.registerActivityLifecycleCallbacks(this); }
    private static synchronized Project7RepairHost host(Context context) throws IOException {
        Context app = context.getApplicationContext();
        if (!(app instanceof Application)) throw new IOException("Application lifecycle unavailable");
        if (instance == null) instance = new Project7RepairHost((Application) app);
        return instance;
    }
    public static Lease watch(Context context, File documents, Consumer<Lease> repair) throws IOException {
        Project7RepairHost host = host(context);
        return host.new Watch(documents, repair);
    }
    private final class Watch implements Lease {
        private final Project7RepairProtocol.Session protocol;
        private final FileObserver observer;
        private final AtomicBoolean closed = new AtomicBoolean();
        private final AtomicBoolean drainAttached = new AtomicBoolean();
        private volatile boolean drained;
        Watch(File documents, Consumer<Lease> repair) throws IOException {
            protocol = Project7RepairProtocol.create(documents, ignored -> {
                close(); repair.accept(this);
            });
            observer = new FileObserver(documents.getAbsolutePath(), FileObserver.MOVED_TO | FileObserver.CLOSE_WRITE) {
                @Override public void onEvent(int event, String path) {
                    if (Project7RepairProtocol.REQUEST.equals(path) && !closed.get()) protocol.inspect();
                }
            };
            observer.startWatching(); protocol.inspect();
        }
        public boolean active() { return !closed.get() && protocol.active(); }
        public void close() {
            if (!closed.compareAndSet(false, true)) return;
            protocol.close();
            if (observer != null) observer.stopWatching();
        }
        public void awaitDrain(CompletableFuture<Void> actualDrain) {
            if (actualDrain == null || !drainAttached.compareAndSet(false, true)) return;
            main.post(() -> { pending = this; render(); });
            actualDrain.whenComplete((ignored, error) -> {
                if (error == null && !actualDrain.isCancelled()) {
                    drained = true;
                    main.post(() -> { if (pending == this) render(); });
                }
                // Exceptional or stuck drain never enables finish or claims saved data.
            });
        }
    }
    private static boolean client(Activity activity) { return activity != null && activity.getClass().getName().equals("com.netease.qrzd.Client"); }
    private void dismiss() {
        if (dialog != null) { dialog.dismiss(); dialog = null; dialogOwner = null; }
    }
    private void render() {
        Activity activity = resumed.get();
        if (pending == null || !client(activity) || activity.isFinishing() || activity.isDestroyed()) { dismiss(); return; }
        dismiss(); Watch expected = pending;
        AlertDialog.Builder builder = new AlertDialog.Builder(activity).setTitle("素材检查未通过").setCancelable(false);
        if (!expected.drained) builder.setMessage("正在停止本地存档服务，请暂勿关闭应用。停止完成后可退出并重新打开。");
        else builder.setMessage("本地存档服务已停止。请退出游戏并重新打开应用。")
            .setPositiveButton("退出游戏", (button, which) -> {
                if (pending == expected && expected.drained && resumed.get() == activity && !activity.isFinishing() && !activity.isDestroyed()) activity.finish();
            });
        try { dialogOwner = activity; dialog = builder.create(); dialog.show(); }
        catch (RuntimeException ignored) { dismiss(); }
    }
    public void onActivityResumed(Activity activity) { if (client(activity)) { resumed = new WeakReference<>(activity); render(); } }
    public void onActivityPaused(Activity activity) { if (resumed.get() == activity) resumed.clear(); if (dialogOwner == activity) dismiss(); }
    public void onActivityDestroyed(Activity activity) { if (resumed.get() == activity) resumed.clear(); if (dialogOwner == activity) dismiss(); }
    public void onActivityCreated(Activity activity, Bundle state) { }
    public void onActivityStarted(Activity activity) { }
    public void onActivityStopped(Activity activity) { }
    public void onActivitySaveInstanceState(Activity activity, Bundle state) { }
}
