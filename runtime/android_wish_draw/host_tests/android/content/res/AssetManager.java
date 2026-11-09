package android.content.res;import java.io.*;import java.util.*;
/** HOST ONLY explicit public-asset mapping. No Android resource/native behavior. */
public final class AssetManager {
 final File root,resources,normal,history,furniture;public final Set<String>opened=new TreeSet<>();
 public AssetManager(File root){this(root,null,null,null,null);}
 public AssetManager(File root,File resources,File normal,File history,File furniture){this.root=root;this.resources=resources;this.normal=normal;this.history=history;this.furniture=furniture;}
 public InputStream open(String name)throws IOException{File f=null;
  if(name.equals("resources.tsv"))f=resources;else if(name.equals("project7_draw_policy/catalog-v2.tsv"))f=normal;else if(name.equals("project7_history/catalog-v3.tsv"))f=history;else if(name.equals("project7_history/furniture-v1.tsv"))f=furniture;
  String property=name.equals("project7_wish/catalog-v1.json")?"p7.wish":name.equals("project7_baiye/catalog-v1.tsv")?"p7.baiye.catalog":name.equals("project7_baiye/fragments-v1.tsv")?"p7.baiye.fragments":name.equals("project7_baiye_shop/catalog-v1.tsv")?"p7.baiye.shop":null;if(property!=null&&System.getProperty(property)!=null)f=new File(System.getProperty(property));
  if(f==null){if(!name.matches("[a-zA-Z0-9_./-]+")||name.contains(".."))throw new IOException("non-public fixture");f=new File(root,name);if(!f.getCanonicalFile().toPath().startsWith(root.getCanonicalFile().toPath()))throw new IOException("public fixture path");}if(!f.isFile())throw new IOException("public fixture absent: "+name);opened.add(name);return new FileInputStream(f);
 }
}
