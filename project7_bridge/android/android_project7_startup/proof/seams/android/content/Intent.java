package android.content;
/** HOST ONLY type linkage; never called. */
public class Intent {
    public Intent() {}
    public Intent(Context context, Class<?> target) {}
    public Intent setAction(String action) { return this; }
    public String getAction() { return null; }
}
