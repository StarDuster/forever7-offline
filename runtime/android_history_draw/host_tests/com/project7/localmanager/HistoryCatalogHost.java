package com.project7.localmanager;
import java.nio.file.*;
import java.util.*;
/** Pure compact graph boundaries, not an original-engine execution proof. */
public final class HistoryCatalogHost {
    static int checks;
    static void check(boolean ok,String message){if(!ok)throw new AssertionError(message);checks++;}
    public static void main(String[] args)throws Exception{
        byte[] input=Files.readAllBytes(Paths.get(args[0]));HistoryCatalog c=HistoryCatalog.parse(input);
        check(c.specs.size()==440,"all history six-card metadata recognized");check(!c.specs.containsKey(1)&&!c.specs.containsKey(354)&&!c.specs.containsKey(484),"reserved IDs excluded");
        List<HistoryCatalog.Distribution> all=new ArrayList<>(c.random.values());for(HistoryCatalog.Spec spec:c.specs.values())all.add(spec.base);
        for(HistoryCatalog.Distribution distribution:all){int offset=0;for(HistoryCatalog.Edge edge:distribution.edges){final int low=offset,high=offset+edge.weight-1;Random a=new Random(){public int nextInt(int bound){return low;}};Random b=new Random(){public int nextInt(int bound){return high;}};check(distribution.pick(a)==edge&&distribution.pick(b)==edge,"unbiased integer edge interval");offset+=edge.weight;}check(offset==distribution.total,"exact total");}
        boolean immutable=false;try{c.specs.clear();}catch(UnsupportedOperationException expected){immutable=true;}check(immutable,"immutable rule snapshot");
        byte[] wrong=input.clone();wrong[0]='X';boolean bad=false;try{HistoryCatalog.parse(wrong);}catch(java.io.IOException expected){bad=true;}check(bad,"unknown format rejected");
        System.out.println("HISTORY_COMPACT_GRAPH_HOST_PASS checks="+checks+"; parser only, not original grant/transactions");
    }
}
