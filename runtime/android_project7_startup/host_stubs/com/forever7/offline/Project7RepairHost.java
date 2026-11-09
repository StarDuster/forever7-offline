package com.forever7.offline;
/** HOST leaf only: startup tests inject lease/callback; no Android observer or UI. */
public final class Project7RepairHost {
 public interface Lease {boolean active();void close();void awaitDrain(java.util.concurrent.CompletableFuture<Void> future);}
 public static Lease watch(android.content.Context app,java.io.File docs,java.util.function.Consumer<Lease> callback){throw new UnsupportedOperationException("Host startup must inject repair lease");}
}
