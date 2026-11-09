package com.project7.localmanager;

import java.io.IOException;

/** Session-scoped, one-shot handoff of the exact LocalProfileStore already prepared by
 * StableIdentityBootstrap. It carries only the original store instance, never profile bytes.
 * The process owner creates exactly one per session. The initializer may publish it once,
 * after bootstrap.initialize returns and the prepared identity/policy is verified; the
 * driver may consume it once while SAVE_ACCESS is held. Cancel/failure/close/drain
 * invalidates it so a later session can never reuse the same handoff.
 */
final class ProfileStoreHandoff {
    /** Same-package initializer seam. The owner binds the session handoff before initialize. */
    interface Aware { void bindHandoff(Sink sink); }
    /** Publication seam; only the initializer that produced the prepared store may publish. */
    interface Sink { void publish(LocalProfileStore prepared) throws IOException; }

    private final Object saveAccess;
    private LocalProfileStore store;
    private boolean published;
    private boolean consumed;
    private boolean invalidated;

    ProfileStoreHandoff(Object saveAccess) {
        if (saveAccess == null) throw new IllegalArgumentException("SAVE_ACCESS required");
        this.saveAccess = saveAccess;
    }
    Sink sink() { return this::publish; }

    synchronized void publish(LocalProfileStore prepared) throws IOException {
        if (invalidated) throw new IOException("PROFILE_STORE_HANDOFF_SESSION_CLOSED");
        if (published || consumed) throw new IOException("PROFILE_STORE_HANDOFF_ALREADY_PUBLISHED");
        if (prepared == null) throw new IOException("PROFILE_STORE_HANDOFF_MISSING");
        store = prepared;
        published = true;
    }
    synchronized boolean available() { return !invalidated && published && !consumed; }
    synchronized LocalProfileStore take() throws IOException {
        if (invalidated) throw new IOException("PROFILE_STORE_HANDOFF_SESSION_CLOSED");
        if (!Thread.holdsLock(saveAccess)) throw new IOException("PROFILE_STORE_HANDOFF_SAVE_ACCESS_REQUIRED");
        if (!published || consumed || store == null) throw new IOException("PROFILE_STORE_HANDOFF_UNAVAILABLE");
        LocalProfileStore result = store;
        store = null;
        published = false;
        consumed = true;
        return result;
    }
    /** Cancel/failure/close/drain: no publication or reuse may survive into another session. */
    synchronized void invalidate() {
        invalidated = true;
        store = null;
        published = false;
    }
    synchronized boolean consumed() { return consumed; }
}
