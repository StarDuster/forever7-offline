package com.project7.localmanager;
import java.io.*;
import java.util.*;
/** Compact immutable rule graph, independent of Context/profile ownership. */
final class HistoryCatalog {
    static void need(boolean ok,String reason)throws IOException{if(!ok)throw new IOException("History: "+reason);}
    static final class Edge {final int source,target,weight;Edge(int s,int t,int w){source=s;target=t;weight=w;}}
    static final class Distribution {
        final List<Edge> edges;final int total;
        Distribution(List<Edge> input)throws IOException {long n=0;for(Edge e:input){need(e.weight>0,"WEIGHT");n+=e.weight;}need(n<=Integer.MAX_VALUE,"WEIGHT_OVERFLOW");total=(int)n;edges=Collections.unmodifiableList(new ArrayList<>(input));}
        Edge pick(Random random)throws IOException{need(total>0,"EMPTY_DISTRIBUTION");int point=random.nextInt(total);for(Edge e:edges){if(point<e.weight)return e;point-=e.weight;}throw new AssertionError();}
    }
    static final class Leaf {
        final int common,id,count,quality,piece;final String kind;private final byte[] design;
        Leaf(int c,String k,int i,int n,int q,int f,byte[] d){common=c;kind=k;id=i;count=n;quality=q;piece=f;design=d==null?null:d.clone();}
        byte[] design(){return design==null?null:design.clone();}
        void validate(LocalResourceCatalog stock)throws IOException {
            need(count>0&&count<=1000000,"COUNT");
            if(kind.equals("hero")||kind.equals("memory")){need(stock.heroes.containsKey(id),"MISSING_HERO");if(kind.equals("memory"))need(count==1&&piece>=1&&piece<=stock.heroes.get(id).files,"PIECE");}
            else if(kind.equals("item"))need(stock.items.containsKey(id),"MISSING_ITEM");
            else if(kind.equals("skin")){
                need(stock.skins.containsKey(id)&&count==1&&design!=null,"MISSING_SKIN");HistoryBson.Value d=HistoryBson.parse(design);
                need(HistoryBson.integer(d,"skin")==id&&HistoryBson.integer(d,"n")==count&&stock.skins.get(id).item==HistoryBson.integer(d,"i"),"SKIN_CONTRACT");
            }else if(kind.equals("pendant")){
                need(stock.items.containsKey(id)&&design!=null,"MISSING_PENDANT_ITEM");HistoryBson.Value d=HistoryBson.parse(design),pair=HistoryBson.required(d,"pendant");
                need(HistoryBson.integer(d,"i")==id&&HistoryBson.integer(d,"n")==count&&pair.fields!=null&&pair.fields.size()==2&&stock.heroes.containsKey(HistoryBson.integer(pair,"0"))&&HistoryBson.integer(pair,"1")>0,"PENDANT_CONTRACT");
                for(HistoryBson.Value t:HistoryBson.required(d,"trans").values())need(t.fields.size()==2&&stock.items.containsKey(HistoryBson.integer(t,"0"))&&HistoryBson.integer(t,"1")>0,"PENDANT_TRANS");
            }
            else if(kind.equals("treasure"))need(stock.items.containsKey(id)&&stock.treasures.containsKey(id+":"+quality),"MISSING_TREASURE");
            else need(kind.equals("money")||kind.equals("summonCoin"),"UNSUPPORTED_LEAF");
            if(design!=null){need(kind.equals("treasure")||kind.equals("skin")||kind.equals("pendant"),"DESIGN_KIND");HistoryBson.parse(design);}
        }
    }
    static final class Spec {
        final int id,epoch,ticket,gift,giftCoin,giftNum,giftAt,giftPerDay;final boolean enabled;final Distribution base;final Map<Integer,Edge> defaults;
        Spec(int i,int e,int t,int g,boolean enabled,Distribution b,Map<Integer,Edge> o,int[] giftSpec){giftCoin=giftSpec[0];giftNum=giftSpec[1];giftAt=giftSpec[2];giftPerDay=giftSpec[3];id=i;epoch=e;ticket=t;gift=g;this.enabled=enabled;base=b;defaults=Collections.unmodifiableMap(new TreeMap<>(o));}
    }
    final Map<Integer,Spec> specs;final Map<Integer,Distribution> random;final Map<Integer,Leaf> leaves;
    HistoryCatalog(Map<Integer,Spec>s,Map<Integer,Distribution>r,Map<Integer,Leaf>l){specs=Collections.unmodifiableMap(s);random=Collections.unmodifiableMap(r);leaves=Collections.unmodifiableMap(l);}
    static int integer(String value)throws IOException{try{return Integer.parseInt(value);}catch(NumberFormatException e){throw new IOException("History integer",e);}}
    static HistoryCatalog parse(byte[] data)throws IOException {
        need(data.length>0&&data.length<=2*1024*1024,"ASSET_LIMIT");for(byte b:data)need(b==9||b==10||(b>=32&&b<=126),"ASCII");
        String[] lines=new String(data,"US-ASCII").split("\n",-1);need(lines[0].equals("P7HISTORY\t1\thistory-free-v1")&&lines[lines.length-1].isEmpty(),"HEADER");
        Map<Integer,int[]> meta=new TreeMap<>(),gifts=new TreeMap<>();Map<Integer,List<Edge>> base=new TreeMap<>(),rawRandom=new TreeMap<>();Map<Integer,Map<Integer,Edge>> defaults=new TreeMap<>();Map<Integer,Leaf> leaves=new TreeMap<>();
        for(int i=1;i<lines.length-1;i++){
            String[] f=lines[i].split("\t",-1);String op=f[0];
            if(op.equals("P")&&f.length==6){int id=integer(f[1]);need(id>0&&id!=1&&id!=354&&id!=484&&meta.put(id,new int[]{integer(f[2]),integer(f[3]),integer(f[4]),integer(f[5])})==null,"DUPLICATE_OR_RESERVED_POOL");}
            else if(op.equals("G")&&f.length==6){int id=integer(f[1]);need(gifts.put(id,new int[]{integer(f[2]),integer(f[3]),integer(f[4]),integer(f[5])})==null,"DUPLICATE_GIFT");}
            else if(op.equals("B")&&f.length==5){int id=integer(f[1]);List<Edge> list=base.get(id);if(list==null){list=new ArrayList<>();base.put(id,list);}list.add(new Edge(integer(f[2]),integer(f[4]),integer(f[3])));}
            else if(op.equals("O")&&f.length==5){int id=integer(f[1]);Map<Integer,Edge> map=defaults.get(id);if(map==null){map=new TreeMap<>();defaults.put(id,map);}need(map.put(integer(f[2]),new Edge(integer(f[3]),integer(f[4]),1))==null,"DUPLICATE_ORDINAL");}
            else if(op.equals("R")&&f.length==4){int id=integer(f[1]);List<Edge> list=rawRandom.get(id);if(list==null){list=new ArrayList<>();rawRandom.put(id,list);}list.add(new Edge(integer(f[2]),integer(f[2]),integer(f[3])));}
            else if(op.equals("L")&&f.length==8){int id=integer(f[1]);byte[] d=f[7].equals("-")?null:Base64.getDecoder().decode(f[7]);need(leaves.put(id,new Leaf(id,f[2],integer(f[3]),integer(f[4]),integer(f[5]),integer(f[6]),d))==null,"DUPLICATE_LEAF");}
            else throw new IOException("History unsupported row "+i);
        }
        Map<Integer,Distribution> random=new TreeMap<>();for(Map.Entry<Integer,List<Edge>> e:rawRandom.entrySet())random.put(e.getKey(),new Distribution(e.getValue()));
        Map<Integer,Spec> specs=new TreeMap<>();for(Map.Entry<Integer,int[]>e:meta.entrySet()){
            int id=e.getKey();int[] m=e.getValue();need((m[2]==0||m[2]==1)&&(m[3]==0||m[3]==1),"CAPABILITY_BOOL");
            Distribution b=new Distribution(base.containsKey(id)?base.get(id):Collections.<Edge>emptyList());Map<Integer,Edge> o=defaults.containsKey(id)?defaults.get(id):Collections.<Integer,Edge>emptyMap();
            if(m[2]==1){need(b.total>0,"ENABLED_EMPTY_BASE");List<Edge> targets=new ArrayList<>(b.edges);targets.addAll(o.values());for(Edge edge:targets){Distribution pool=random.get(edge.target);need(pool!=null&&pool.total>0,"MISSING_RANDOM");for(Edge leaf:pool.edges)need(leaves.containsKey(leaf.target)&&!leaves.get(leaf.target).kind.equals("unsupported"),"UNSUPPORTED_ENABLED_LEAF");}}
            specs.put(id,new Spec(id,m[0],m[1],m[3],m[2]==1,b,o,gifts.containsKey(id)?gifts.get(id):new int[]{0,0,0,0}));
        }
        return new HistoryCatalog(specs,random,leaves);
    }
}
