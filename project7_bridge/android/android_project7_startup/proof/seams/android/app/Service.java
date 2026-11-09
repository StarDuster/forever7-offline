package android.app;
/** HOST ONLY type linkage for the translated GatewayService class; never instantiated or called.
 *  It extends the host Context type so verifier stack maps match real Android Service/ContextWrapper. */
public class Service extends android.content.Context {
    public Service() {}
    public Object getSystemService(Class<?> serviceClass) { throw new UnsupportedOperationException(); }
    public android.content.ComponentName startService(android.content.Intent intent) { throw new UnsupportedOperationException(); }
    public boolean stopService(android.content.Intent intent) { throw new UnsupportedOperationException(); }
    public android.os.IBinder onBind(android.content.Intent intent) { return null; }
    public void onConfigurationChanged(android.content.res.Configuration configuration) {}
    public void onCreate() {}
    public void onDestroy() {}
    public int onStartCommand(android.content.Intent intent, int flags, int startId) { return 0; }
}
