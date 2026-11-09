package com.project7.localmanager;
import java.io.*;
import java.util.*;
import org.json.*;

/** Fixed-data target loader. A hash mismatch is fatal before any profile read. */
final class CollectionTargets {
    static final String TARGET_SHA="7e3849b6ed316b7cdc2ef9f103b90e0bc8e20f9b5da70ab3b585fbd72c0da62d";
    static final String CATALOG_SHA="5e716bd9a34cfd678af9aba6385ba3fae92d4b17486ee480f76bd95320268e99";
    static final String CONTRACT_SHA="1d5627de39c2a960e368313dfa34c3a63c8f04de3ae46be30edee839dfb1a18f";
    final LinkedHashSet<Integer> heroes=new LinkedHashSet<>();
    final Map<Integer,Integer> ranks=new LinkedHashMap<>();
    final LinkedHashMap<Integer,Integer> skins=new LinkedHashMap<>();
    final LinkedHashMap<Integer,Integer> dyeParents=new LinkedHashMap<>();
    final LinkedHashMap<Integer,Integer> dyeSourceCanDye=new LinkedHashMap<>();
    final LinkedHashMap<String,Treasure> treasures=new LinkedHashMap<>();
    static final class Attr {final double low,high;Attr(double a,double b){low=a;high=b;}}
    static final class Treasure {
        final int id,quality;final List<Integer> tricks;final Map<String,Attr> attrs;
        Treasure(int i,int q,List<Integer> t,Map<String,Attr>a){id=i;quality=q;tricks=t;attrs=a;}
        String key(){return id+":"+quality;}
    }
    static CollectionTargets load(byte[] bytes)throws Exception{
        CollectionBson.need(FullCollectionInitializer.sha(bytes).equals(TARGET_SHA),"TARGET_ASSET_HASH");
        JSONObject root=new JSONObject(new String(bytes,"UTF-8"));CollectionBson.need("project7-full-collection-target-v1".equals(root.getString("format")),"TARGET_FORMAT");CollectionTargets t=new CollectionTargets();
        JSONArray heroes=root.getJSONArray("heroes");for(int i=0;i<heroes.length();i++){JSONObject h=heroes.getJSONObject(i);int id=h.getInt("id");t.ranks.put(id,h.getInt("rank"));CollectionBson.need(t.heroes.add(id),"DUPLICATE_HERO_TARGET");CollectionBson.need((id==46||id==125)?"stock-addMissingHero".equals(h.getString("grant")):"stock-grantAllHeroes".equals(h.getString("grant")),"HERO_GRANT_POLICY");}
        JSONArray skins=root.getJSONArray("skins");for(int i=0;i<skins.length();i++){JSONObject s=skins.getJSONObject(i);int sid=s.getInt("id"),hid=s.getInt("hero");CollectionBson.need(t.skins.put(sid,hid)==null,"DUPLICATE_SKIN_TARGET");if(s.optInt("isDyeSkin",0)!=0){CollectionBson.need(!s.isNull("oriSkin"),"DYE_PARENT_MISSING");t.dyeParents.put(sid,s.getInt("oriSkin"));t.dyeSourceCanDye.put(sid,s.optInt("sourceCanDye",0));}else CollectionBson.need(s.isNull("oriSkin"),"NON_DYE_PARENT_PRESENT");}
        JSONArray treasures=root.getJSONArray("treasures");for(int i=0;i<treasures.length();i++){JSONObject r=treasures.getJSONObject(i);int id=r.getInt("id");JSONArray qs=r.getJSONArray("qualities");for(int j=0;j<qs.length();j++){JSONObject q=qs.getJSONObject(j);List<Integer> tricks=new ArrayList<>();JSONArray ts=q.getJSONArray("tricks");for(int k=0;k<ts.length();k++)tricks.add(ts.getInt(k));Map<String,Attr> attrs=new LinkedHashMap<>();JSONArray aa=q.getJSONArray("attrs");for(int k=0;k<aa.length();k++){JSONObject a=aa.getJSONObject(k);JSONArray bounds=a.getJSONArray("sourceBounds");CollectionBson.need(attrs.put(a.getString("name"),new Attr(bounds.getDouble(0),bounds.getDouble(1)))==null,"DUPLICATE_ATTR_TARGET");}Treasure tr=new Treasure(id,q.getInt("quality"),tricks,attrs);CollectionBson.need(t.treasures.put(tr.key(),tr)==null,"DUPLICATE_TREASURE_TARGET");}}
        t.validate();return t;
    }
    void validate()throws IOException{
        CollectionBson.need(heroes.size()==140&&ranks.size()==140&&heroes.contains(46)&&heroes.contains(125)&&skins.size()==494&&treasures.size()==1900,"TARGET_COVERAGE");
        for(int hid:skins.values())CollectionBson.need(heroes.contains(hid),"SKIN_HERO_FOREIGN_KEY");
        for(Map.Entry<Integer,Integer> dye:dyeParents.entrySet()){int sid=dye.getKey(),parent=dye.getValue();CollectionBson.need(skins.containsKey(parent),"DYE_PARENT_MISSING");CollectionBson.need(skins.get(parent).intValue()==skins.get(sid).intValue(),"DYE_PARENT_HERO");CollectionBson.need(dyeSourceCanDye.get(sid)==1,"DYE_SOURCE_CAN_DYE");}
        Set<Integer> ids=new HashSet<>();for(Treasure t:treasures.values()){CollectionBson.need(t.quality>=1&&t.quality<=5,"TARGET_QUALITY");ids.add(t.id);}CollectionBson.need(ids.size()==380,"TREASURE_ID_COVERAGE");for(int id:ids)for(int q=1;q<=5;q++)CollectionBson.need(treasures.containsKey(id+":"+q),"MISSING_QUALITY");
    }
}
