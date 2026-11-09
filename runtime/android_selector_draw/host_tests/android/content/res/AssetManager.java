package android.content.res;
import java.io.*;
import java.util.*;
/** Explicit host public-assets seam, not Android/renderer behavior. */
public final class AssetManager {
    final File root,resources,normal,history,furniture;public final Set<String> opened=new TreeSet<>();
    public AssetManager(File root,File resources,File normal,File history){this(root,resources,normal,history,null);}
    public AssetManager(File root,File resources,File normal,File history,File furniture){this.root=root;this.resources=resources;this.normal=normal;this.history=history;this.furniture=furniture;}
    public InputStream open(String name)throws IOException{
        File path;
        if(name.equals("resources.tsv"))path=resources;
        else if(name.equals("project7_draw_policy/catalog-v2.tsv"))path=normal;
        else if((name.equals("project7_history/catalog-v3.tsv")||name.equals("project7_history/catalog-v2.tsv")||name.equals("project7_history/catalog-v1.tsv")))path=history;
        else if(name.equals("project7_history/furniture-v1.tsv")){if(furniture==null)throw new IOException("Furniture fixture absent");path=furniture;}
        else {if(!name.matches("[a-z_]+\\.tsv"))throw new IOException("Host non-public asset denied");path=new File(root,name);}
        if(!path.isFile())throw new IOException("Missing approved public asset "+name);opened.add(name);return new FileInputStream(path);
    }
}
