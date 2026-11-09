package com.project7.localmanager;
import java.io.*;
import java.util.*;
import static com.project7.localmanager.CollectionBson.*;

/** Independent, exact validator for the original LS group-max normalization only. */
final class CollectionLiberateRules {
    static final List<String> FIELDS=Arrays.asList("ls","lh","la","ld");
    static void verify(byte[] source,byte[] normalized,List<List<Integer>> groups,CollectionTargets targets)throws IOException {
        CollectionValidator.Index before=CollectionValidator.scan(source,targets),after=CollectionValidator.scan(normalized,targets);
        need(before.heroes.keySet().equals(after.heroes.keySet()),"NORMALIZE_CHANGED_HERO_SET");
        Map<Integer,Map<String,Value>> expected=new HashMap<>();for(Map.Entry<Integer,Value> e:before.heroes.entrySet()){Map<String,Value> state=new HashMap<>();for(String f:FIELDS)state.put(f,e.getValue().get(f));expected.put(e.getKey(),state);}
        for(List<Integer> group:groups){List<Integer> owned=new ArrayList<>();int[] maxima=new int[4];boolean valid=true;
            for(int id:group)if(expected.containsKey(id)){owned.add(id);for(int n=0;n<4;n++){Value v=expected.get(id).get(FIELDS.get(n));if(v!=null&&v.stockInteger()==null){valid=false;continue;}int value=v==null?0:v.integer();if(value<0||(n==0&&value>4))valid=false;maxima[n]=Math.max(maxima[n],value);}}
            if(!valid||owned.size()<2)continue;
            for(int id:owned)for(int n=0;n<4;n++){String f=FIELDS.get(n);Value v=expected.get(id).get(f);if((v==null?0:v.integer())!=maxima[n])expected.get(id).put(f,intValue(maxima[n]));}
        }
        Set<String> allowed=new HashSet<>();Value hrs=CollectionValidator.container(CollectionValidator.container(before.root,"heromgr"),"hrs");
        for(Map.Entry<String,Value> pair:hrs.fields.entrySet()){int id=integer(pair.getValue(),"0");Value actual=after.heroes.get(id);for(String f:FIELDS){Value value=expected.get(id).get(f);need(value==null?actual.get(f)==null:equal(value,actual.get(f)),"NORMALIZE_NOT_EXACT_GROUP_MAX");allowed.add("heromgr.hrs."+pair.getKey()+".1."+f);}}
        unchanged(before.root,after.root,"",allowed);
    }
    private static Value intValue(int v){return new Value(16,new byte[]{(byte)v,(byte)(v>>>8),(byte)(v>>>16),(byte)(v>>>24)},null);}
    private static void unchanged(Value before,Value after,String path,Set<String> allowed)throws IOException {
        if(allowed.contains(path))return;need(before!=null&&after!=null&&before.type==after.type,"NORMALIZE_UNRELATED_TYPE_CHANGE");
        if(before.fields==null){need(Arrays.equals(before.bytes,after.bytes),"NORMALIZE_UNRELATED_VALUE_CHANGE");return;}
        Set<String> keys=new HashSet<>(before.fields.keySet());keys.addAll(after.fields.keySet());for(String k:keys)unchanged(before.get(k),after.get(k),path.isEmpty()?k:path+"."+k,allowed);
    }
}
