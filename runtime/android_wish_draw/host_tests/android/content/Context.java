package android.content;
import java.io.File;import android.content.res.AssetManager;
/** HOST ONLY, never package. */
public class Context {
 private final File files;private final AssetManager assets;
 public Context(File files,AssetManager assets){this.files=files;this.assets=assets;}
 public Context getApplicationContext(){return this;}
 public File getFilesDir(){return files;}
 public AssetManager getAssets(){return assets;}
}
