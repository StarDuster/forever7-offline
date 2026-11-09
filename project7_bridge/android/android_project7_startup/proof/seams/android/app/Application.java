package android.app;
/** HOST ONLY type linkage; the host never constructs an Android Application. */
public class Application extends android.content.Context {
    public interface ActivityLifecycleCallbacks {}
    public void registerActivityLifecycleCallbacks(ActivityLifecycleCallbacks callbacks) {}
    public void unregisterActivityLifecycleCallbacks(ActivityLifecycleCallbacks callbacks) {}
}
