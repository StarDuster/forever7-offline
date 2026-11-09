package com.project7.localmanager;

import android.content.Context;

/** Production driver: original pinned manager APIs, no alternate account/profile engine. */
final class StockIdentityStorage implements StableIdentityBootstrap.Storage {
    public Object saveAccess() { return GatewayService.SAVE_ACCESS; }
    public boolean stopped() { return !GatewayService.isRunning() && !GatewayService.saveAccessBlocked(); }
    public StableIdentityBootstrap.Stores open(Context app) throws Exception {
        LocalAccountStore accounts = new LocalAccountStore(app);
        return new StableIdentityBootstrap.Stores(accounts, new LocalTutorialStore(app), new LocalProfileStore(app));
    }
    public boolean contains(StableIdentityBootstrap.Stores stores, String account) throws Exception {
        return stores.accounts.listAccounts().contains(account);
    }
    public int register(StableIdentityBootstrap.Stores stores, String account, String secret) throws Exception {
        return stores.accounts.registerOne(account, secret);
    }
    public void authenticateExisting(StableIdentityBootstrap.Stores stores, String account, String secret) throws Exception {
        // Close authenticate's auto-registration branch under its original lock.
        // Release FILE_LOCK before snapshot/profile calls to preserve lock order.
        synchronized (LocalAccountStore.FILE_LOCK) {
            if (!stores.accounts.listAccounts().contains(account)) throw new java.io.IOException("ACCOUNT_MISSING_BEFORE_AUTH");
            LocalAccountStore.Result result = stores.accounts.authenticate(account, secret);
            if (!result.accepted || result.registered || !account.equals(result.username))
                throw new java.io.IOException("GENERATED_CREDENTIALS_REJECTED");
        }
    }
    public int numericId(StableIdentityBootstrap.Stores stores, String account) throws Exception { return stores.accounts.numericId(account); }
    public LocalTutorialStore.Progress loadProgress(StableIdentityBootstrap.Stores stores, String account) throws Exception {
        return stores.tutorials.load(account);
    }
    public void loadProfile(StableIdentityBootstrap.Stores stores, String account, LocalTutorialStore.Progress progress) throws Exception {
        stores.profiles.load(account, progress);
    }
    public void saveProgress(StableIdentityBootstrap.Stores stores, String account, LocalTutorialStore.Progress progress) throws Exception {
        stores.tutorials.save(account, progress);
    }
    public void validateSnapshot(Context app, StableIdentityBootstrap.Stores stores, String account) throws Exception {
        new LocalAccountArchive(app, stores.accounts).snapshot(account);
        // Portable Snapshot.profile is intentionally discarded, never written back.
    }
    public void verifyProfileIdentity(byte[] profile, String account, int uid) throws Exception {
        Integer stored = BsonLite.intValue(profile, "uid");
        if (stored == null || stored.intValue() != uid ||
                !account.equals(BsonLite.stringValue(profile, "account")) ||
                !account.equals(BsonLite.stringValue(profile, "an")))
            throw new java.io.IOException("PROFILE_IDENTITY_MISMATCH");
    }
}
