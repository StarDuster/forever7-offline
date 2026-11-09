package android.content;
/** HOST TEST ONLY. Never include in Android classes/DEX. */
public class Context {
    private final java.io.File files;
    public Context() { this.files = null; }
    public Context(java.io.File files) { this.files = files; }
    public java.io.File getFilesDir() {
        if (files == null) throw new UnsupportedOperationException("Synthetic files root required");
        return files;
    }
    public Context getApplicationContext() { return this; }
}
