package com.netease.qrzd;

import java.util.UUID;

/** No IO, authentication, journal parsing, or Android dependency. */
public final class AutoLoginCore {
    public interface Dispatcher { void post(Runnable task); }
    public interface InputSink { void finish(String value, boolean confirmed); }
    public interface ActivityState {
        boolean isAlive();
        default boolean sameOwner(ActivityState other) { return this == other; }
    }
    public interface SessionProvider { Session current(); }
    public interface Status { void update(String code); }
    public static final class Credentials {
        public final String username, secret;
        public Credentials(String username, String secret) {
            if (username == null || !username.matches("[a-z0-9_.-]{1,32}") ||
                secret == null || secret.length() < 1 || secret.length() > 128)
                throw new IllegalArgumentException("Invalid identity");
            this.username = username; this.secret = secret;
        }
    }
    /** generation must identify one owner reservation, never be reused. */
    public static final class Session {
        public final Object generation;
        public final boolean ownerReady, resourcesReady, identityReady;
        public final Credentials credentials;
        public Session(Object generation, boolean ownerReady, boolean resourcesReady,
                       boolean identityReady, Credentials credentials) {
            this.generation = generation; this.ownerReady = ownerReady;
            this.resourcesReady = resourcesReady; this.identityReady = identityReady;
            this.credentials = credentials;
        }
        boolean ready() { return generation != null && ownerReady && resourcesReady && identityReady && credentials != null; }
    }
    public static final class Request {
        public final String mode, token, error;
        public Request(String mode, String token, String error) {
            this.mode = mode == null ? "login" : mode;
            this.token = token == null ? "" : token; this.error = error == null ? "" : error;
        }
    }
    private static final class Invocation {
        final long epoch; final Request request; final ActivityState activity; final Session session;
        boolean delivered, cancelled;
        Invocation(long epoch, Request request, ActivityState activity, Session session) {
            this.epoch = epoch; this.request = request; this.activity = activity; this.session = session;
        }
    }
    private final Dispatcher dispatcher; private final InputSink sink;
    private final SessionProvider sessions; private final Status status;
    private long epoch; private Invocation active;
    private String pending; private Object pendingGeneration; private ActivityState pendingActivity;
    public AutoLoginCore(Dispatcher dispatcher, InputSink sink, SessionProvider sessions, Status status) {
        this.dispatcher = dispatcher; this.sink = sink; this.sessions = sessions; this.status = status;
    }
    private Session snapshot() { try { return sessions.current(); } catch (RuntimeException e) { return null; } }
    public synchronized void show(Request request, ActivityState activity, boolean visible) {
        if (!visible) { hide(activity); return; }
        Invocation next = new Invocation(++epoch, request, activity, snapshot());
        active = next;
        dispatcher.post(() -> deliver(next));
    }
    public synchronized boolean isVisible() { return active != null && !active.delivered; }
    private void hide(ActivityState activity) {
        // visible=false has no native input of its own. Only the Activity owning
        // this exact current queued invocation may cancel it; delivery keeps its epoch guard.
        if (active == null || active.delivered || active.activity == null || activity == null ||
                !active.activity.sameOwner(activity)) return;
        active.cancelled = true;
        if (pendingActivity != null && pendingActivity.sameOwner(activity)) {
            pending = null; pendingGeneration = null; pendingActivity = null;
        }
    }
    public synchronized void cancel() {
        pending = null; pendingGeneration = null; pendingActivity = null;
        if (active == null || active.delivered) return;
        active.cancelled = true;
        // The queued task remains the sole delivery for this input; newer show invalidates it.
    }
    private synchronized void deliver(Invocation call) {
        if (active != call || call.epoch != epoch || call.delivered) return;
        call.delivered = true; active = null; // before JNI, including reentrant callbacks or exceptions
        String value = ""; boolean confirmed = false;
        Request r = call.request;
        Session now = snapshot();
        boolean same = now != null && call.session != null && now.generation == call.session.generation;
        if (pendingGeneration != null && (now == null || now.generation != pendingGeneration)) {
            pending = null; pendingGeneration = null; pendingActivity = null;
        }
        if (pending != null && pendingActivity != null && !pendingActivity.isAlive()) {
            pending = null; pendingGeneration = null; pendingActivity = null;
        }
        boolean alive = call.activity != null && call.activity.isAlive();
        if (!alive) {
            status.update("activity_gone");
            return; // destroyed Activity no longer owns the process-global native callback slot
        }
        if (call.cancelled) status.update("cancelled");
        else if (r == null) status.update("invalid_request");
        else if (r.mode.equals("cancel")) { pending = null; pendingGeneration = null; pendingActivity = null; status.update("cancelled"); }
        else if (r.mode.equals("accepted") || r.mode.equals("discard")) {
            if (same && pendingGeneration == now.generation && r.token.equals(pending)) {
                pending = null; pendingGeneration = null; pendingActivity = null;
            }
            confirmed = true; // ACK only; never marks authenticated/ONLINE.
        } else if (!r.mode.equals("login")) status.update("invalid_request");
        else if (!r.error.isEmpty()) status.update("login_repair_required");
        else if (!same || !now.ready()) status.update("startup_not_ready");
        else if (pending != null) status.update("attempt_pending");
        else {
            pending = UUID.randomUUID().toString(); pendingGeneration = now.generation; pendingActivity = call.activity;
            value = "{\"username\":" + quote(now.credentials.username) + ",\"password\":" +
                quote(now.credentials.secret) + ",\"token\":" + quote(pending) + "}";
            confirmed = true; status.update("input_submitted");
        }
        try { sink.finish(value, confirmed); }
        catch (Throwable error) { status.update("native_delivery_failed"); } // consumption unknown: never retry
    }
    static String quote(String value) {
        StringBuilder out = new StringBuilder("\"");
        for (int i = 0; i < value.length(); i++) {
            char c = value.charAt(i);
            if (c == '\\' || c == '"') out.append('\\').append(c);
            else if (c < 32) out.append(String.format("\\u%04x", (int)c));
            else out.append(c);
        }
        return out.append('"').toString();
    }
}
