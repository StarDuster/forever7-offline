package com.project7.localmanager;

import android.content.Context;

/** Package-private dependency seam. Production uses the unchanged manager API. */
interface LifecycleDriver {
    interface Status { void changed(boolean running, String detail); }
    Object saveAccess();
    void claim() throws Exception;
    void activate() throws Exception;
    void construct(Context app, Status status) throws Exception;
    /** Production construct must consume the prepared store handoff when the owner supplies one.
     * Legacy/test drivers may keep the old overload and ignore the handoff.
     */
    default void construct(Context app, Status status, ProfileStoreHandoff handoff) throws Exception {
        if (handoff != null) throw new IllegalStateException("Lifecycle driver does not support prepared profile handoff");
        construct(app, status);
    }
    void register(Thread gatewayThread) throws Exception;
    // No work in production; finite host publication-race barriers only.
    default void beforeReadyPublication() {}
    default void beforeStoppedPublication() {}
    void runGateway();
    void runBootstrap();
    void closeOwned() throws Exception;
    boolean writersStopped();
    void release() throws Exception;
}
