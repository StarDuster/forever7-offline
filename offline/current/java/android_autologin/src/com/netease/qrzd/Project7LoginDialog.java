package com.netease.qrzd;

import android.app.Activity;
import android.os.Handler;
import android.os.Looper;
import com.netease.neox.NativeInterface;
import org.json.JSONObject;
import java.lang.ref.WeakReference;

/** Same descriptor replacement. No form exists; visible means queued native input. */
public final class Project7LoginDialog {
    private static volatile AutoLoginCore.SessionProvider provider = () -> null;
    private static volatile String status = "startup_not_connected";
    private static final Handler MAIN = new Handler(Looper.getMainLooper());
    private static final AutoLoginCore CORE = new AutoLoginCore(
        task -> MAIN.post(task), NativeInterface::NativeOnInputFinish,
        () -> provider.current(), code -> status = code);
    private Project7LoginDialog() {}
    /** Install once during production startup, before any type120 invocation. No IO here. */
    public static synchronized void installSessionProvider(AutoLoginCore.SessionProvider source) {
        if (source == null) throw new IllegalArgumentException("Session provider required");
        CORE.cancel(); provider = source;
    }
    public static String status() { return status; }
    public static void show(Activity activity, String request, boolean visible) {
        AutoLoginCore.Request parsed = null;
        try {
            JSONObject json = new JSONObject(request);
            Object mode = json.opt("mode"), token = json.opt("token"), error = json.opt("error");
            if ((mode != null && !(mode instanceof String)) ||
                (token != null && !(token instanceof String)) ||
                (error != null && !(error instanceof String))) throw new IllegalArgumentException();
            parsed = new AutoLoginCore.Request((String)mode, (String)token, (String)error);
        } catch (Exception malformed) { /* fail closed, never include request in status */ }
        CORE.show(parsed, new WeakActivityState(activity), visible);
    }
    private static final class WeakActivityState implements AutoLoginCore.ActivityState {
        private final WeakReference<Activity> reference;
        WeakActivityState(Activity activity) { reference = new WeakReference<>(activity); }
        public boolean isAlive() {
            Activity current = reference.get();
            return current != null && !current.isFinishing() && !current.isDestroyed();
        }
        public boolean sameOwner(AutoLoginCore.ActivityState other) {
            if (!(other instanceof WeakActivityState)) return false;
            Activity current = reference.get();
            return current != null && current == ((WeakActivityState) other).reference.get();
        }
    }
    public static void cancel() { CORE.cancel(); }
    public static boolean isVisible() { return CORE.isVisible(); }
}
