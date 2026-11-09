package android.os;
/** HOST ONLY type linkage; never called. */
public class Handler {
    public Handler() {}
    public Handler(Looper looper) {}
    public boolean post(Runnable runnable) { throw new UnsupportedOperationException(); }
}
