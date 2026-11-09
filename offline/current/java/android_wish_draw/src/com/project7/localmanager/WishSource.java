package com.project7.localmanager;
import java.io.*;import java.util.*;
/** Converts actual reward_common only. show_id/treasure_design are never read. */
final class WishSource {
 static HistoryCatalog.Leaf leaf(int cid)throws Exception{WishCatalog c=WishCatalog.ready();Map<?,?>r=WishCatalog.row(c.common,cid);Set<String>keys=new HashSet<>(Arrays.asList("id","tradeType","hero","treasure","treasureNum","treasureLevel","design_treasure","items","itemsNum"));for(Object key:r.keySet())WishCatalog.need(keys.contains(key),"unsupported wish common");
  if(r.containsKey("hero")){List<?>a=DynamicCatalog.list(r.get("hero"));WishCatalog.need(a.size()==1&&!r.containsKey("treasure")&&!r.containsKey("design_treasure"),"hero primary shape");return new HistoryCatalog.Leaf(cid,"hero",DynamicCatalog.num(a.get(0)),1,1,0,null);}
  if(r.containsKey("items")){List<?>ids=DynamicCatalog.list(r.get("items")),counts=DynamicCatalog.list(r.get("itemsNum"));WishCatalog.need(ids.size()==1&&counts.size()==1,"item primary shape");int id=DynamicCatalog.num(ids.get(0)),count=DynamicCatalog.num(counts.get(0));Map<?,?>item=WishCatalog.row(c.items,id);if(item.containsKey("memoryFrag")){List<?>memory=DynamicCatalog.list(item.get("memoryFrag"));WishCatalog.need(memory.size()==2&&count==1,"memory primary binding");return new HistoryCatalog.Leaf(cid,"memory",DynamicCatalog.num(memory.get(0)),1,1,DynamicCatalog.num(memory.get(1)),null);}return new HistoryCatalog.Leaf(cid,"item",id,count,1,0,null);}
  List<?>n=DynamicCatalog.list(r.get("treasureNum")),q=DynamicCatalog.list(r.get("treasureLevel"));WishCatalog.need(n.size()==1&&q.size()==1,"treasure primary shape");int count=DynamicCatalog.num(n.get(0)),quality=DynamicCatalog.num(q.get(0));byte[]design=null;int item;
  if(r.containsKey("design_treasure")){Map<?,?>d=WishCatalog.row(c.designs,DynamicCatalog.num(r.get("design_treasure")));item=DynamicCatalog.num(d.get("item"));Map<?,?>tr=DynamicCatalog.map(d.get("tr"));WishCatalog.need(DynamicCatalog.num(tr.get("cl"))==quality,"grant design quality");design=DynamicCatalog.bson(tr);}else{List<?>a=DynamicCatalog.list(r.get("treasure"));WishCatalog.need(a.size()==1,"treasure primary count");item=DynamicCatalog.num(a.get(0));}
  return new HistoryCatalog.Leaf(cid,"treasure",item,count,quality,0,design);
 }
 static HistoryCatalog.Leaf pick(Map<?,?>row,String key,Random random)throws Exception{List<?>rewards=DynamicCatalog.list(row.get(key));WishCatalog.need(rewards.size()==1,"wish rewards");return leaf(DynamicCatalog.num(rewards.get(random.nextInt(rewards.size()))));}
}
