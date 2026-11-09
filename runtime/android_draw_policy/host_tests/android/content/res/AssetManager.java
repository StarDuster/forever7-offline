package android.content.res;
import java.io.*;
import java.util.*;
/** Host public-catalog-only filesystem seam. Template/private BSON always refused. */
public final class AssetManager {
    final File publicRoot,resources,policy;public final Set<String> opened=new TreeSet<>();
    public AssetManager(File root,File resources,File policy){publicRoot=root;this.resources=resources;this.policy=policy;}
    public InputStream open(String name)throws IOException {
        File f;
        if(name.equals("resources.tsv"))f=resources;
        else if(name.equals("project7_draw_policy/catalog-v2.tsv"))f=policy;
        else {if(!name.matches("[a-z_]+\\.tsv"))throw new IOException("Host forbids non-public asset");f=new File(publicRoot,name);}
        if(!f.isFile())throw new IOException("Missing approved asset "+name);opened.add(name);return new FileInputStream(f);
    }
}
