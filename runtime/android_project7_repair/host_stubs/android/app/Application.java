package android.app;
public final class Application extends android.content.Context {
 public ActivityLifecycleCallbacks callbacks;public int registrations;
 public void registerActivityLifecycleCallbacks(ActivityLifecycleCallbacks c){callbacks=c;registrations++;}
 public interface ActivityLifecycleCallbacks {
  void onActivityCreated(Activity a,android.os.Bundle b);void onActivityStarted(Activity a);void onActivityResumed(Activity a);void onActivityPaused(Activity a);void onActivityStopped(Activity a);void onActivitySaveInstanceState(Activity a,android.os.Bundle b);void onActivityDestroyed(Activity a);
 }
}
