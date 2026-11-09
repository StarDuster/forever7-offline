package com.project7.localmanager;

import java.io.*;
import java.util.*;

/** Immutable integer-weight graph. No account state or retained Android context. */
final class DrawPolicyCatalog {
    static final class Branch {
        final int source, target, weight;
        Branch(int s,int t,int w){source=s;target=t;weight=w;}
    }
    static final class Distribution {
        final List<Branch> branches; final int total;
        Distribution(List<Branch> input)throws IOException {
            need(input!=null&&!input.isEmpty(),"EMPTY_DISTRIBUTION");
            long sum=0;Set<Integer> ids=new HashSet<>();
            for(Branch b:input){need(b.weight>0&&ids.add(b.source),"INVALID_WEIGHT_OR_DUPLICATE");sum+=b.weight;}
            need(sum<=Integer.MAX_VALUE,"WEIGHT_OVERFLOW");
            total=(int)sum;branches=Collections.unmodifiableList(new ArrayList<>(input));
        }
        Branch pick(Random random){int point=random.nextInt(total);for(Branch b:branches){if(point<b.weight)return b;point-=b.weight;}throw new AssertionError();}
    }
    static final class Leaf {
        final int common,id,count,quality,file;final String kind;final byte[] design;
        Leaf(int c,String k,int i,int n,int q,int f,byte[] d){common=c;kind=k;id=i;count=n;quality=q;file=f;design=d;}
        void supported()throws IOException {
            need(kind.equals("hero")||kind.equals("memory")||kind.equals("item")||kind.equals("treasure")||kind.equals("summonCoin"),"UNSUPPORTED_STOCK_GRANT_"+kind+"_COMMON_"+common);
            need(count>0&&count<=1000000,"INVALID_LEAF_COUNT");
            if(!kind.equals("summonCoin"))need(id>0&&quality>0,"INVALID_LEAF");
            if(design!=null){need(kind.equals("treasure"),"DESIGN_KIND");DrawPolicyBson.parse(design);}
            if(kind.equals("memory"))need(file>=1&&file<=30&&count==1,"INVALID_FRAGMENT");
        }
    }
    final Distribution base;final Map<Integer,Distribution> pools;final Map<Integer,Branch> overrides;final Map<Integer,Leaf> leaves;
    private DrawPolicyCatalog(Distribution b,Map<Integer,Distribution> p,Map<Integer,Branch> o,Map<Integer,Leaf> l){base=b;pools=Collections.unmodifiableMap(p);overrides=Collections.unmodifiableMap(o);leaves=Collections.unmodifiableMap(l);}
    static void need(boolean ok,String error)throws IOException{if(!ok)throw new IOException("Draw policy: "+error);}
    static int number(String s)throws IOException{try{int n=Integer.parseInt(s);need(n>=0,"NEGATIVE_VALUE");return n;}catch(NumberFormatException e){throw new IOException("Invalid catalog integer",e);}}
    static DrawPolicyCatalog parse(byte[] data)throws IOException{
        need(data.length>0&&data.length<=262144,"CATALOG_SIZE");
        for(byte b:data)need(b==10||b==9||(b>=32&&b<=126),"NON_ASCII_CATALOG");
        String[] lines=new String(data,"US-ASCII").split("\n",-1);
        need(lines[0].equals("P7DRAW\t1\tnormal-ordinal-reserve-on-group-v1")&&lines[lines.length-1].isEmpty(),"CATALOG_HEADER");
        List<Branch> base=new ArrayList<>();Map<Integer,List<Branch>> raw=new TreeMap<>();Map<Integer,Branch> overrides=new TreeMap<>();Map<Integer,Leaf> leaves=new TreeMap<>();
        for(int i=1;i<lines.length-1;i++){
            String[] f=lines[i].split("\t",-1);
            if(f[0].equals("B")&&f.length==4)base.add(new Branch(number(f[1]),number(f[3]),number(f[2])));
            else if(f[0].equals("O")&&f.length==4){int ord=number(f[1]);need(ord>0&&overrides.put(ord,new Branch(number(f[2]),number(f[3]),1))==null,"DUPLICATE_ORDINAL");}
            else if(f[0].equals("R")&&f.length==4){int rid=number(f[1]);List<Branch> r=raw.get(rid);if(r==null){r=new ArrayList<>();raw.put(rid,r);}r.add(new Branch(number(f[2]),number(f[2]),number(f[3])));}
            else if(f[0].equals("L")&&f.length==8){Leaf l=new Leaf(number(f[1]),f[2],number(f[3]),number(f[4]),number(f[5]),number(f[6]),f[7].equals("-")?null:Base64.getDecoder().decode(f[7]));l.supported();need(leaves.put(l.common,l)==null,"DUPLICATE_LEAF");}
            else throw new IOException("Unsupported catalog row "+i);
        }
        Map<Integer,Distribution> pools=new TreeMap<>();for(Map.Entry<Integer,List<Branch>> e:raw.entrySet())pools.put(e.getKey(),new Distribution(e.getValue()));
        for(Branch b:base)need(pools.containsKey(b.target),"MISSING_BASE_POOL");
        for(Branch override:overrides.values())need(pools.containsKey(override.target),"MISSING_OVERRIDE_POOL");
        for(Distribution p:pools.values())for(Branch b:p.branches)need(leaves.containsKey(b.target),"MISSING_COMMON");
        return new DrawPolicyCatalog(new Distribution(base),pools,overrides,leaves);
    }
}
