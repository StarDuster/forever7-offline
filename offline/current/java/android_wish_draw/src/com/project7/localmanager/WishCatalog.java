package com.project7.localmanager;
import android.content.Context;import java.io.*;import java.nio.charset.StandardCharsets;import java.util.*;import org.json.*;
/** Immutable fixed public source sidecar; display designs never become grants. */
public final class WishCatalog {
 public static final String ASSET="project7_wish/catalog-v1.json",SHA256="4abad0f105f6b2088632369e5ff86040791640c9724deb85d75c57660a168c91";
 static volatile WishCatalog snapshot;
 final Map<?,?> wish,choose,fees,common,items,designs,display,exclusive,normals,replacement;final List<?> up,dynamic;
 private WishCatalog(Map<?,?>d)throws Exception{need("project7-wish-source-v1".equals(d.get("schema")),"schema");wish=literalMap(d,"wish");choose=literalMap(d,"choose");fees=literalMap(d,"fees");common=literalMap(d,"common");items=literalMap(d,"items");designs=literalMap(d,"grant_designs");display=literalMap(d,"display_designs");exclusive=literalMap(d,"exclusive");normals=literalMap(d,"normals");replacement=literalMap(d,"replacement_random");dynamic=DynamicCatalog.list(d.get("dynamic"));up=DynamicCatalog.list(d.get("up"));need(wish.size()==143&&choose.size()==117&&fees.size()==6&&up.size()==3,"scope");}
 public static void prepare(Context c)throws IOException{try(InputStream in=c.getAssets().open(ASSET)){prepareStream(in);}catch(IOException e){throw e;}catch(Exception e){throw new IOException("许愿源数据校验失败",e);}}
 static void prepareStream(InputStream in)throws Exception{byte[]b=DynamicCatalog.read(in,2*1024*1024);need(DynamicCatalog.sha(b).equals(SHA256),"pin");snapshot=new WishCatalog(DynamicCatalog.map(json(new JSONObject(new String(b,StandardCharsets.UTF_8)))));}
 static Map<?,?>literalMap(Map<?,?>d,String k)throws Exception{try{return DynamicCatalog.map(DynamicCatalog.decode(d.get(k)));}catch(Exception e){throw new IOException("Wish literal: "+k,e);}}
 static WishCatalog ready()throws IOException{need(snapshot!=null,"prepare required");return snapshot;}
 static void need(boolean b,String s)throws IOException{if(!b)throw new IOException("Wish: "+s);}
 static Object json(Object v)throws Exception{if(v==JSONObject.NULL)return null;if(v instanceof JSONObject){Map<String,Object>m=new LinkedHashMap<>();JSONObject j=(JSONObject)v;Iterator<String>i=j.keys();while(i.hasNext()){String k=i.next();m.put(k,json(j.get(k)));}return Collections.unmodifiableMap(m);}if(v instanceof JSONArray){List<Object>a=new ArrayList<>();JSONArray j=(JSONArray)v;for(int i=0;i<j.length();i++)a.add(json(j.get(i)));return Collections.unmodifiableList(a);}return v;}
 static Map<?,?> row(Map<?,?>m,int id)throws IOException{return DynamicCatalog.map(m.get(id));}
}
