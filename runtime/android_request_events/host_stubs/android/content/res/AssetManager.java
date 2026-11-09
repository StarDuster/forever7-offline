package android.content.res;
import java.io.*;
/** Host-only public request catalog seam, never packaged. */
public final class AssetManager {
 private final File root;
 public AssetManager(File root){this.root=root;}
 public InputStream open(String name)throws IOException {
  if(name.equals("project7_history/catalog-v1.tsv") && System.getProperty("p7.history.assets")!=null)return new FileInputStream(new File(System.getProperty("p7.history.assets"),name));
  if(!name.equals("offline/request-events.tsv") && !name.equals("offline/ending-trigger-v1.json") && !name.matches("[a-z_]+\\.tsv") && !name.equals("new_player.bson") && !name.equals("local_notice.txt") && !name.matches("client_[a-z_]+\\.py"))throw new IOException("Not fixed public request catalog");
  return new FileInputStream(new File(root,name));
 }
}
