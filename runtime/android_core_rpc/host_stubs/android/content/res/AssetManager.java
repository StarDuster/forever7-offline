package android.content.res;
import java.io.*;
/** HOST ONLY fixed public catalog directory, never private templates/profiles. */
public final class AssetManager {
 private final File assets;
 public AssetManager(File assets){this.assets=assets;}
 public InputStream open(String name)throws IOException {
  if(!name.matches("[a-z_]+\\.tsv"))throw new IOException("Not public catalog");
  return new FileInputStream(new File(assets,name));
 }
}
