package android.os;
/** HOST ONLY type linkage; finite main-thread distinction, no Android event loop runs. */
public final class Looper {
    private static final Looper MAIN = new Looper();
    private static final Thread MAIN_THREAD = Thread.currentThread();
    private Looper() {}
    public static Looper getMainLooper() { return MAIN; }
    public static Looper myLooper() { return Thread.currentThread() == MAIN_THREAD ? MAIN : null; }
}
