package com.project7.localmanager;
import java.io.*;import java.util.*;
/** Actual original codec key deltas from an isolated runner invocation. Never a
 * whole-Progress rollback. Original fromProperties owns decoding/collection types. */
final class DreamProgressDelta {
 static byte[]capture(Object before,Object after)throws IOException{
  Properties a=props(before),b=props(after);Set<String>keys=new TreeSet<>(a.stringPropertyNames());keys.addAll(b.stringPropertyNames());List<byte[]>rows=new ArrayList<>();
  for(String k:keys)if(!Objects.equals(a.getProperty(k),b.getProperty(k)))rows.add(BsonLite.document("k",k,"ha",a.containsKey(k),"a",a.getProperty(k,""),"hb",b.containsKey(k),"b",b.getProperty(k,"")));
  return BsonLite.document("rows",rows);
 }
 static void apply(Object target,byte[]delta)throws IOException{
  Properties p=props(target);byte[]rows=BsonLite.arrayValue(delta,"rows");if(rows==null)throw new IOException("Missing original Progress delta");
  for(String index:BsonLite.keys(rows)){byte[]row=BsonLite.documentValue(rows,index);String key=BsonLite.stringValue(row,"k"),a=BsonLite.stringValue(row,"a"),b=BsonLite.stringValue(row,"b");Boolean ha=BsonLite.boolValue(row,"ha"),hb=BsonLite.boolValue(row,"hb");if(key==null||a==null||b==null||ha==null||hb==null)throw new IOException("Original Progress delta shape");String old=p.getProperty(key);if(!Objects.equals(old,ha?a:null)&&!Objects.equals(old,hb?b:null))throw new IOException("Original Progress revision conflict");if(hb)p.setProperty(key,b);else p.remove(key);}
  Object parsed=DreamAccess.stat(target.getClass(),"fromProperties",new Class<?>[]{Properties.class},p);DreamAccess.copyProgress(parsed,target);
 }
 static Properties props(Object p)throws IOException{return(Properties)DreamAccess.call(p,"toProperties",new Class<?>[0]);}
}
