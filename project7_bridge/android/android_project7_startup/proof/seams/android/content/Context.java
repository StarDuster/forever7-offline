package android.content;
import java.io.File;
import android.content.res.AssetManager;
/** HOST ONLY exact minimal Android platform seam, never packaged. Extendable solely so the
 *  type-only android.app.Service stub can mirror the real Context/ContextWrapper hierarchy. */
public class Context {
    private final File files;private final AssetManager assets;
    public Context(){this.files=null;this.assets=null;}
    public Context(File files,AssetManager assets){this.files=files;this.assets=assets;}
    public Context getApplicationContext(){return this;}
    public File getFilesDir(){return files;}
    public File getExternalFilesDir(String type){return files;}
    public AssetManager getAssets(){return assets;}
    private final java.util.Map<String,android.content.SharedPreferences> prefs=new java.util.HashMap<>();
    public android.content.SharedPreferences getSharedPreferences(String name,int mode){return prefs.computeIfAbsent(name,n->new android.content.SharedPreferences(){final java.util.Map<String,Object> m=new java.util.TreeMap<>(); public java.util.Map<String,?> getAll(){return m;} public String getString(String k,String d){Object v=m.get(k);return v instanceof String?(String)v:d;} public java.util.Set<String> getStringSet(String k,java.util.Set<String> d){Object v=m.get(k);return v instanceof java.util.Set?(java.util.Set<String>)v:d;} public int getInt(String k,int d){Object v=m.get(k);return v instanceof Integer?(Integer)v:d;} public long getLong(String k,long d){Object v=m.get(k);return v instanceof Long?(Long)v:d;} public float getFloat(String k,float d){Object v=m.get(k);return v instanceof Float?(Float)v:d;} public boolean getBoolean(String k,boolean d){Object v=m.get(k);return v instanceof Boolean?(Boolean)v:d;} public boolean contains(String k){return m.containsKey(k);} public Editor edit(){return new Editor(){final java.util.Map<String,Object> e=new java.util.HashMap<>();final java.util.Set<String> r=new java.util.HashSet<>();boolean clear;public Editor putString(String k,String v){e.put(k,v);return this;}public Editor putStringSet(String k,java.util.Set<String> v){e.put(k,new java.util.HashSet<>(v));return this;}public Editor putInt(String k,int v){e.put(k,v);return this;}public Editor putLong(String k,long v){e.put(k,v);return this;}public Editor putFloat(String k,float v){e.put(k,v);return this;}public Editor putBoolean(String k,boolean v){e.put(k,v);return this;}public Editor remove(String k){r.add(k);return this;}public Editor clear(){clear=true;return this;}public boolean commit(){if(clear)m.clear();for(String k:r)m.remove(k);m.putAll(e);return true;}public void apply(){commit();}};} public void registerOnSharedPreferenceChangeListener(OnSharedPreferenceChangeListener l){} public void unregisterOnSharedPreferenceChangeListener(OnSharedPreferenceChangeListener l){} });}
}
