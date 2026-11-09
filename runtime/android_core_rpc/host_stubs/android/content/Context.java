package android.content;
import java.io.File;import android.content.res.AssetManager;
/** HOST ONLY, never package. */
public final class Context {
 private final File files;private final AssetManager assets;
 private final java.util.Map<String,SharedPreferences> preferences=new java.util.HashMap<>();
 public Context(File files,AssetManager assets){this.files=files;this.assets=assets;}
 public Context getApplicationContext(){return this;}
 public File getFilesDir(){return files;}
 public AssetManager getAssets(){return assets;}
 public SharedPreferences getSharedPreferences(String name,int mode){
  SharedPreferences existing=preferences.get(name);
  if(existing==null){existing=new MemoryPreferences();preferences.put(name,existing);}
  return existing;
 }
}
final class MemoryPreferences implements SharedPreferences {
 private final java.util.Map<String,Object> values=new java.util.TreeMap<>();
 public java.util.Map<String,?> getAll(){return values;}
 public String getString(String key,String fallback){Object value=values.get(key);return value instanceof String?(String)value:fallback;}
 public java.util.Set<String> getStringSet(String key,java.util.Set<String> fallback){
  Object value=values.get(key);
  if(!(value instanceof java.util.Set))return fallback;
  @SuppressWarnings("unchecked") java.util.Set<String> set=(java.util.Set<String>)value;
  return set;
 }
 public int getInt(String key,int fallback){Object value=values.get(key);return value instanceof Integer?(Integer)value:fallback;}
 public long getLong(String key,long fallback){Object value=values.get(key);return value instanceof Long?(Long)value:fallback;}
 public float getFloat(String key,float fallback){Object value=values.get(key);return value instanceof Float?(Float)value:fallback;}
 public boolean getBoolean(String key,boolean fallback){Object value=values.get(key);return value instanceof Boolean?(Boolean)value:fallback;}
 public boolean contains(String key){return values.containsKey(key);}
 public Editor edit(){return new MemoryEditor(this);}
 public void registerOnSharedPreferenceChangeListener(OnSharedPreferenceChangeListener listener){}
 public void unregisterOnSharedPreferenceChangeListener(OnSharedPreferenceChangeListener listener){}
 void apply(java.util.Map<String,Object> changes,java.util.Set<String> removals,boolean clear){
  if(clear)values.clear();
  for(String key:removals)values.remove(key);
  values.putAll(changes);
 }
}
final class MemoryEditor implements SharedPreferences.Editor {
 private final MemoryPreferences owner;
 private final java.util.Map<String,Object> changes=new java.util.HashMap<>();
 private final java.util.Set<String> removals=new java.util.HashSet<>();
 private boolean clear;
 MemoryEditor(MemoryPreferences owner){this.owner=owner;}
 public SharedPreferences.Editor putString(String key,String value){changes.put(key,value);return this;}
 public SharedPreferences.Editor putStringSet(String key,java.util.Set<String> value){changes.put(key,new java.util.HashSet<>(value));return this;}
 public SharedPreferences.Editor putInt(String key,int value){changes.put(key,value);return this;}
 public SharedPreferences.Editor putLong(String key,long value){changes.put(key,value);return this;}
 public SharedPreferences.Editor putFloat(String key,float value){changes.put(key,value);return this;}
 public SharedPreferences.Editor putBoolean(String key,boolean value){changes.put(key,value);return this;}
 public SharedPreferences.Editor remove(String key){removals.add(key);return this;}
 public SharedPreferences.Editor clear(){clear=true;return this;}
 public boolean commit(){owner.apply(changes,removals,clear);return true;}
 public void apply(){commit();}
}
