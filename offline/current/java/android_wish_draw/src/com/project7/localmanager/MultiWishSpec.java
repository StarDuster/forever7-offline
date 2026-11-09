package com.project7.localmanager;
import java.io.*;import java.util.*;
final class MultiWishSpec {
 final int pool,epoch,target;final Map<Integer,List<Map<?,?>>>groups;final Map<?,?>dynamic;final DynamicTransition.Rules rules;
 MultiWishSpec(Map<?,?>d)throws Exception{dynamic=d;pool=DynamicCatalog.num(d.get("pool"));epoch=DynamicCatalog.num(d.get("epoch"));Map<Integer,List<Map<?,?>>>g=new TreeMap<>();for(Object v:WishCatalog.ready().wish.values()){Map<?,?>r=DynamicCatalog.map(v);if(DynamicCatalog.num(r.get("drawType"))!=pool)continue;WishCatalog.need(DynamicCatalog.num(r.get("wish_type"))==2,"group wish type");int gid=DynamicCatalog.num(r.get("gid"));g.computeIfAbsent(gid,k->new ArrayList<Map<?,?>>()).add(r);HistoryCatalog.Leaf leaf=WishSource.pick(r,"reward",new Random(0));WishCatalog.need(leaf.kind.equals("hero")&&leaf.id==DynamicCatalog.num(r.get("wish_target")),"wish hero binding");}
  WishCatalog.need(!g.isEmpty(),"group source");Map<Integer,List<Map<?,?>>>frozen=new TreeMap<>();for(Map.Entry<Integer,List<Map<?,?>>>e:g.entrySet())frozen.put(e.getKey(),Collections.unmodifiableList(e.getValue()));groups=Collections.unmodifiableMap(frozen);
  List<DynamicTransition.Threshold>jz=new ArrayList<>();int hero=0;for(Object v:DynamicCatalog.list(d.get("jiaozhi"))){Map<?,?>j=DynamicCatalog.map(v),raw=DynamicCatalog.map(DynamicCatalog.decode(j.get("raw")));int t=DynamicCatalog.num(raw.get("target_hero"));WishCatalog.need(hero==0||hero==t,"jiaozhi target");hero=t;WishCatalog.need(!raw.containsKey("open_hero_file"),"unsupported group blessing");jz.add(new DynamicTransition.Threshold(DynamicCatalog.num(j.get("row_id")),DynamicCatalog.num(j.get("threshold")),false,"random",DynamicCatalog.ints(DynamicCatalog.list(j.get("grant_random_ids")))));}
  target=hero;rules=new DynamicTransition.Rules(target,Collections.<DynamicTransition.Threshold>emptyList(),jz);
 }
 Set<Integer>rowIds(int gid)throws Exception{Set<Integer>s=new TreeSet<>();List<Map<?,?>>rows=groups.get(gid);WishCatalog.need(rows!=null,"group identity");for(Map<?,?>r:rows)s.add(DynamicCatalog.num(r.get("id")));return s;}
}
