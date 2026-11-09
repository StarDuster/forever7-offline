package android.content;
public class Context {
    private java.io.File files;
    public Context() { }
    public Context(java.io.File file) { files = file; }
    public Context getApplicationContext() { return this; }
    public java.io.File getFilesDir() { if(files==null)throw new UnsupportedOperationException("Synthetic root required");return files; }
    public android.content.res.AssetManager getAssets() { throw new UnsupportedOperationException("No real assets in host model"); }
    public java.io.File getExternalFilesDir(String type) { return files; }
    public android.content.SharedPreferences getSharedPreferences(String name, int mode) { return null; }
}
