package com.project7.localmanager;

import android.content.Context;
import com.forever7.offline.Project7BundledResources;
import com.forever7.offline.Project7ResourceSnapshot;
import com.forever7.offline.ResourceImporter;
import com.forever7.offline.Project7RepairHost;
import java.util.function.Consumer;
import com.netease.qrzd.AutoLoginCore;
import com.netease.qrzd.Project7LoginDialog;
import java.io.ByteArrayOutputStream;
import java.io.File;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.util.List;
import java.util.concurrent.CompletableFuture;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicBoolean;

/** Production wiring to real resource, owner, identity, collection and input modules. */
final class Project7StartupPlatform implements Project7StartupCoordinator.Services {
    private final Context app;
    /** Private startup ledger; deliberately rooted in app.getFilesDir(), never external storage. */
    private final File resourceLedger;
    Project7StartupPlatform(Context app) {
        if (app == null) throw new IllegalArgumentException("Application context required");
        this.app = app;
        try {
            configureNativeRuntime(app);
            this.resourceLedger = Project7ResourceSnapshot.privateLedger(app.getFilesDir());
        } catch (IOException error) { throw new IllegalStateException("原生运行目录未准备好", error); }
    }
    public boolean foreignOwnerActive() {
        return SinglePackageGateway.hasActiveProcessReservation() || GatewayService.isRunning() || GatewayService.saveAccessBlocked();
    }
    public void installProvider(AutoLoginCore.SessionProvider provider) { Project7LoginDialog.installSessionProvider(provider); }
    public Project7RepairHost.Lease watchRepair(File documents, Consumer<Project7RepairHost.Lease> repair) throws IOException { return Project7RepairHost.watch(app, documents, repair); }
    public String approvedPolicy() { return FullCollectionInitializer.POLICY; }
    static String assetName(String name) { return name.startsWith("assets/") ? name.substring(7) : name; }

    /** Publish neox.xml under the normalized neox_root contract before Client starts. */
    private static void configureNativeRuntime(Context context) throws IOException {
        File external = context.getExternalFilesDir(null);
        File internal = context.getFilesDir();
        if (external == null || internal == null) throw new IOException("应用数据目录不可用");
        File externalRoot = new File(external, "netease/qrzd");
        File internalRoot = new File(internal, "netease/qrzd");
        byte[] loader;
        try (InputStream input = context.getAssets().open("neox.xml")) {
            ByteArrayOutputStream output = new ByteArrayOutputStream();
            byte[] buffer = new byte[8192];
            int count;
            while ((count = input.read(buffer)) != -1) output.write(buffer, 0, count);
            loader = output.toByteArray();
        }
        if (loader.length == 0) throw new IOException("neox.xml 为空");
        for (File root : new File[]{externalRoot, internalRoot})
            writeAtomic(new File(root, "neox.xml"), loader);
        android.content.SharedPreferences preferences = context.getSharedPreferences("neox_config", 0);
        if (!preferences.edit().putString("NeoXRoot", externalRoot.getAbsolutePath()).commit())
            throw new IOException("NeoXRoot 保存失败");
        String selected = preferences.getString("NeoXRoot", null);
        if (selected == null || !selected.equals(externalRoot.getAbsolutePath()) ||
                !new File(externalRoot, "neox.xml").isFile())
            throw new IOException("NeoXRoot 交接未完成");
    }

    private static void writeAtomic(File target, byte[] bytes) throws IOException {
        File directory = target.getParentFile();
        if (directory == null || (!directory.isDirectory() && !directory.mkdirs()))
            throw new IOException("无法创建资源目录");
        File temporary = File.createTempFile(".neox-", ".tmp", directory);
        try {
            try (FileOutputStream output = new FileOutputStream(temporary)) {
                output.write(bytes);
                output.getFD().sync();
            }
            if (!temporary.renameTo(target))
                throw new IOException("neox.xml 原子替换失败");
        } finally {
            if (temporary.exists() && !temporary.delete())
                throw new IOException("neox.xml 临时文件清理失败");
        }
        if (!target.isFile() || target.length() != bytes.length)
            throw new IOException("neox.xml 写入校验失败");
    }

    public Project7StartupCoordinator.Evidence publish(File documents, List<ResourceImporter.Entry> entries,
                                                      AtomicBoolean cancel, Project7StartupCoordinator.Status status) throws Exception {
        Project7ResourceSnapshot.TrustedContract trusted = Project7BundledResources.contract();
        final long[] lastProgress = new long[]{0};
        Project7ResourceSnapshot.Receipt receipt = Project7ResourceSnapshot.publish(documents, entries, trusted,
            name -> app.getAssets().open(assetName(name)), cancel,
            (name, bytes, total) -> {
                long now = System.nanoTime();
                if (bytes == total || now - lastProgress[0] > TimeUnit.MILLISECONDS.toNanos(250)) {
                    lastProgress[0] = now;
                    status.update("正在核验素材：" + bytes / 1048576 + " / " + total / 1048576 + " MiB");
                }
            }, resourceLedger);
        if (receipt == null || receipt.verifiedEntries != trusted.entryCount ||
                !receipt.snapshotSha256.equals(trusted.snapshot.sha256) || !receipt.bindingSha256.equals(trusted.binding.sha256))
            throw new IOException("新资源核验凭据不匹配。");
        return new Project7StartupCoordinator.Evidence(receipt, receipt.snapshotSha256, receipt.bindingSha256, receipt.verifiedEntries);
    }
    public Project7StartupCoordinator.Backend backend(Project7StartupCoordinator.Guard guard) { return new OwnedBackend(guard); }
    private final class OwnedBackend implements Project7StartupCoordinator.Backend {
        private final SinglePackageGateway gateway = new SinglePackageGateway(null);
        private final Project7StartupCoordinator.Guard guard;
        private final AtomicBoolean executed = new AtomicBoolean();
        private final StableIdentityBootstrap bootstrap;
        private volatile StableIdentityBootstrap.PreparedIdentity identity;
        private volatile AutoLoginCore.Credentials credentials;
        private volatile LocalProfileStore preparedProfiles;
        OwnedBackend(Project7StartupCoordinator.Guard guard) {
            this.guard = guard;
            final FullCollectionInitializer collection = new FullCollectionInitializer(guard::cancelled);
            bootstrap = StableIdentityBootstrap.withPostProfile(FullCollectionInitializer.POLICY,
                (context, bound, stores) -> {
                    collection.initialize(context, bound, stores);
                    checkpoint();
                    // Separate stopped-owner commits. A failed seed prevents READY;
                    // the next preparation safely resumes both idempotent steps.
                    WishGateway.prepareStoppedProfile(stores.profiles, bound.username(),
                        bound.numericId(), guard::cancelled);
                    checkpoint();
                    // Session handoff is published only after initialize returns and policy
                    // validation succeeds; this is the same original store, never bytes.
                    preparedProfiles = stores.profiles();
                });
        }
        private void checkpoint() throws IOException {
            if (guard.cancelled() || ownerFailed()) throw new ResourceImporter.Cancelled();
        }
        public CompletableFuture<Void> start() {
            return gateway.start(app, true, new StartupHook(),
                SinglePackageGateway.StartupBudget.fullCollectionPreparation());
        }
        /** Production hook: publishes the already prepared store only after full validation. */
        private final class StartupHook implements SinglePackageGateway.PreStartInitializer, ProfileStoreHandoff.Aware {
            private volatile ProfileStoreHandoff.Sink handoffSink;
            @Override public void bindHandoff(ProfileStoreHandoff.Sink sink) { handoffSink = sink; }
            @Override public void initialize(Context context) throws Exception {
                preparedProfiles = null;
                executed.set(true); checkpoint();
                // Reservation/SAVE_ACCESS belongs to this exact hook; still stopped.
                LocalStartupMode.set(context, 0);
                CoreDrawPolicy.prepare(context); checkpoint();
                HistoryDrawPolicy.prepare(context); checkpoint();
                SelectorPolicy.prepare(context); checkpoint();
                DynamicDrawPolicy.prepare(context); checkpoint();
                WishGateway.prepare(context); checkpoint();
                StoryMissionBridge.prepare(context); checkpoint();
                try {
                    Class.forName("com.project7.localmanager.StoryCityBootstrap")
                        .getDeclaredMethod("prepare", Context.class).invoke(null, context);
                } catch (ReflectiveOperationException error) {
                    throw new IOException("StoryCity startup preparation failed", error);
                }
                checkpoint();
                TrialRetryGateway.prepare(context); checkpoint();
                OfflineMechanismGateway.prepare(context); checkpoint();
                bootstrap.initialize(context); checkpoint();
                StableIdentityBootstrap.PreparedIdentity prepared = bootstrap.preparedIdentity();
                if (!prepared.postProfilePolicyApplied() || !FullCollectionInitializer.POLICY.equals(prepared.postProfilePolicy()))
                    throw new IOException("收藏初始化凭据未形成。");
                LocalProfileStore handed = preparedProfiles;
                ProfileStoreHandoff.Sink sink = handoffSink;
                if (handed == null || sink == null) throw new IOException("PROFILE_STORE_HANDOFF_MISSING");
                sink.publish(handed);
                prepared.credentials().deliver((username, secret) -> credentials = new AutoLoginCore.Credentials(username, secret));
                identity = prepared; checkpoint();
                LocalStartupMode.set(context, 1);
                if (!"game".equals(LocalStartupMode.get(context))) throw new IOException("本地启动模式未生效。");
            }
        }
        public boolean hookExecuted() { return executed.get(); }
        public boolean ownerReady() { return gateway.state() == SinglePackageGateway.State.READY; }
        public boolean ownerFailed() {
            SinglePackageGateway.State state = gateway.state();
            return state == SinglePackageGateway.State.FAILED || state == SinglePackageGateway.State.CLOSING || state == SinglePackageGateway.State.CLOSED;
        }
        public StableIdentityBootstrap.PreparedIdentity identity() { return identity; }
        public AutoLoginCore.Credentials credentials() { return credentials; }
        public void closeIfOwned() { if (executed.get()) gateway.closeAsync(); }
        public CompletableFuture<Void> drained() { return gateway.drained(); }
    }
}
