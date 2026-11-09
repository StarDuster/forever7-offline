package android.content.res;
import java.io.*;
/** HOST ONLY exact public assets; never packaged. */
public final class AssetManager {
 private final File root;
 public AssetManager(File root){this.root=root;}
 public InputStream open(String name)throws IOException{
  String overlayPath=System.getProperty("p7.overlay");
  if(overlayPath!=null&&(name.equals("resources.tsv")||name.equals("project7_draw_policy/catalog-v2.tsv")||name.equals("project7_history/catalog-v2.tsv")||name.equals("project7_history/furniture-v1.tsv")))return new FileInputStream(new File(overlayPath,name));
  File repo=new File(System.getProperty("p7.repo"));
  if(name.equals("project7_dream/catalog-v1.tsv"))return new FileInputStream(new File(repo,"runtime/project7_dream_catalog/catalog-v1.tsv"));
  if(name.equals("offline/request-events.tsv"))return new FileInputStream(new File(repo,"runtime/project7_request_events/request-events.tsv"));
  if(name.equals("project7_history/catalog-v2.tsv"))return new FileInputStream(new File(repo,"runtime/project7_history_catalog/catalog-v2.tsv"));
  if(name.equals("project7_history/furniture-v1.tsv"))return new FileInputStream(new File(repo,"runtime/project7_history_catalog/furniture-v1.tsv"));
  if(!name.matches("[a-z_]+\\.tsv")&&!name.equals("new_player.bson")&&!name.equals("local_notice.txt")&&!name.matches("client_[a-z_]+\\.py"))throw new IOException("Not fixed public host asset");return new FileInputStream(new File(root,name));
 }
}
