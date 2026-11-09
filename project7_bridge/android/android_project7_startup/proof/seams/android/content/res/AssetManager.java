package android.content.res;
import java.io.File;
import java.io.FileInputStream;
import java.io.IOException;
import java.io.InputStream;
import java.util.Set;
import java.util.TreeSet;
/** HOST ONLY asset seam. The three-argument form opens only the pinned public catalogs;
 *  the one-argument form exposes the staged asset tree to the nine production prepare calls. */
public final class AssetManager {
    private final File publicAssets,catalog,targets;private final boolean tree;public final Set<String> opened=new TreeSet<>();
    public AssetManager(File publicAssets,File catalog,File targets){this.publicAssets=publicAssets;this.catalog=catalog;this.targets=targets;this.tree=false;}
    public AssetManager(File root){this.publicAssets=root;this.catalog=new File(root,"resources.tsv");this.targets=new File(root,"project7_catalog/target-manifest.json");this.tree=true;}
    public InputStream open(String name)throws IOException{
        File f;
        if(tree){
            File root=publicAssets.getCanonicalFile(),target=new File(root,name).getCanonicalFile();
            if(!target.getPath().startsWith(root.getPath()+File.separator))throw new IOException("Host asset traversal rejected");
            f=target;
        }else if(name.equals("resources.tsv"))f=catalog;
        else if(name.equals("project7_catalog/target-manifest.json"))f=targets;
        else{if(!name.matches("[a-z_]+\\.tsv"))throw new IOException("Host rejects non-public-catalog asset");f=new File(publicAssets,name);}
        if(!f.isFile())throw new IOException("Missing public asset "+name);
        opened.add(name);return new FileInputStream(f);
    }
}
