package com.project7.localmanager;
import java.io.*;
import java.lang.reflect.*;
import java.util.*;

/** Exact signatures from the pinned manager DEX; no alternative game engine. */
final class CollectionStockBridge implements FullCollectionInitializer.Engine {
    private final Class<?> catalogClass,resultClass,bsonClass,featuresClass;private final Object catalog,features;private final List<List<Integer>> groups=new ArrayList<>();
    CollectionStockBridge(byte[] catalogBytes,CollectionTargets targets,Object profiles)throws Exception{
        featuresClass=Class.forName("com.project7.localmanager.LocalFeatureCatalog");features=invoke(method(Class.forName("com.project7.localmanager.LocalProfileStore"),"features"),profiles);
        Map<?,?> entries=(Map<?,?>)field(featuresClass,"entries").get(features);TreeSet<String> keys=new TreeSet<>();for(Object key:entries.keySet())keys.add((String)key);for(String key:keys)if(key.startsWith("LS:")){CollectionBson.Value row=CollectionBson.parse((byte[])entries.get(key));CollectionBson.Value share=row.get("liberate_share");if(share!=null)groups.add(CollectionBson.ints(share));}
        CollectionBson.need(groups.equals(Arrays.asList(Arrays.asList(34,122),Arrays.asList(45,139),Arrays.asList(63,145))),"SHARED_LIBERATE_GROUP_BINDING");
        catalogClass=Class.forName("com.project7.localmanager.LocalResourceCatalog");resultClass=Class.forName("com.project7.localmanager.LocalResourceEngine$Result");bsonClass=Class.forName("com.project7.localmanager.BsonLite");
        Constructor<?> constructor=catalogClass.getDeclaredConstructor(InputStream.class);constructor.setAccessible(true);catalog=constructor.newInstance(new ByteArrayInputStream(catalogBytes));
        Set<?> heroes=((Map<?,?>)field(catalogClass,"heroes").get(catalog)).keySet();Set<Integer> expected=new HashSet<>(targets.heroes);expected.remove(46);expected.remove(125);CollectionBson.need(heroes.equals(expected),"STOCK_H_CATALOG_SET");for(int id:expected){Object h=((Map<?,?>)field(catalogClass,"heroes").get(catalog)).get(id);CollectionBson.need(field(h.getClass(),"rank").getInt(h)==targets.ranks.get(id),"STOCK_HERO_RANK");}
        Map<?,?> skins=(Map<?,?>)field(catalogClass,"skins").get(catalog);CollectionBson.need(skins.keySet().equals(targets.skins.keySet()),"STOCK_S_CATALOG_SET");for(Map.Entry<Integer,Integer> e:targets.skins.entrySet()){Object s=skins.get(e.getKey());CollectionBson.need(field(s.getClass(),"hero").getInt(s)==e.getValue(),"STOCK_SKIN_MAPPING");}
        Map<?,?> treasures=(Map<?,?>)field(catalogClass,"treasures").get(catalog);CollectionBson.need(treasures.keySet().equals(targets.treasures.keySet()),"STOCK_T_CATALOG_SET");
    }
    static Field field(Class<?> c,String name)throws Exception{Field f=c.getDeclaredField(name);f.setAccessible(true);return f;}
    static Method method(Class<?> c,String name,Class<?>... args)throws Exception{Method m=c.getDeclaredMethod(name,args);m.setAccessible(true);return m;}
    static Object invoke(Method m,Object instance,Object... args)throws Exception{try{return m.invoke(instance,args);}catch(InvocationTargetException e){Throwable t=e.getCause();if(t instanceof Exception)throw (Exception)t;throw new IOException("Original engine failed",t);}}
    private byte[] profile(Object result)throws Exception{return (byte[])field(result.getClass(),"profile").get(result);}
    private Object result(byte[] p)throws Exception{Constructor<?> c=resultClass.getDeclaredConstructor(byte[].class);c.setAccessible(true);return c.newInstance((Object)p);}
    public List<List<Integer>> liberateGroups(){return groups;}
    public byte[] normalize(byte[] p)throws Exception{return (byte[])invoke(method(Class.forName("com.project7.localmanager.LocalSharedLiberateEngine"),"normalize",byte[].class,featuresClass),null,p,features);}
    public byte[] heroes(byte[] p)throws Exception{return profile(invoke(method(Class.forName("com.project7.localmanager.LocalLevelAdmin"),"grantAllHeroes",byte[].class,catalogClass),null,p,catalog));}
    public byte[] helper(byte[] p,int id)throws Exception{Object r=result(p);invoke(method(Class.forName("com.project7.localmanager.LocalResourceEngine"),"addMissingHero",resultClass,int.class,int.class),null,r,id,4);return profile(r);}
    public byte[] skins(byte[] p)throws Exception{return profile(invoke(method(Class.forName("com.project7.localmanager.LocalCollectionEngine"),"grantAll",byte[].class,catalogClass,String.class),null,p,catalog,"skin"));}
    public byte[] treasure(byte[] p,int id,int q)throws Exception{Object r=result(p);invoke(method(Class.forName("com.project7.localmanager.LocalResourceEngine"),"grant",resultClass,catalogClass,String.class,int.class,int.class,int.class),null,r,catalog,"treasure",id,1,q);return profile(r);}
    public byte[] receipt(byte[] p)throws Exception{
        Object[] values={"schema",1,"policy",FullCollectionInitializer.POLICY,"targets",CollectionTargets.TARGET_SHA,"catalog",CollectionTargets.CATALOG_SHA,"contract",CollectionTargets.CONTRACT_SHA};
        byte[] document=(byte[])invoke(method(bsonClass,"document",Object[].class),null,(Object)values);
        return (byte[])invoke(method(bsonClass,"withProfileDocument",byte[].class,String.class,byte[].class),null,p,FullCollectionInitializer.RECEIPT,document);
    }
}
