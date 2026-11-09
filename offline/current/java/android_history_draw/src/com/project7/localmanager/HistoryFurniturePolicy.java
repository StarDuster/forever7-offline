package com.project7.localmanager;
import android.content.Context;
import java.io.*;
import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.util.*;
/** Readonly furniture selection overlay; all mutation/replies remain original HomeEngine. */
public final class HistoryFurniturePolicy {
    public static final String POLICY="history-furniture-free-v1";
    public static final String ASSET="project7_history/furniture-v1.tsv";
    public static final String SHA256="dd85b09e9f3094a2c5a9f72a3300e04ad85e63b9730c6cdd8ab2a32b54ba4a2d";
    private static volatile Map<Integer,Spec> snapshot;
    private static final class Spec {
        final byte[] rule;final List<byte[]> base;final Map<Integer,byte[]> defaults;final boolean enabled;
        Spec(byte[] r,List<byte[]> b,Map<Integer,byte[]> d,boolean e){rule=r.clone();base=Collections.unmodifiableList(b);defaults=Collections.unmodifiableMap(d);enabled=e;}
    }
    private static void stopped()throws IOException{if(Thread.currentThread().isInterrupted())throw new IOException("FURNITURE_CANCELLED");}
    private static IllegalArgumentException failure(Exception e){if(e instanceof ArithmeticException)throw (ArithmeticException)e;if(e instanceof IllegalArgumentException)return (IllegalArgumentException)e;return new IllegalArgumentException("离线配送数据校验失败，请重新进入",e);}
    public static void prepare(Context context)throws Exception{try(InputStream in=context.getAssets().open(ASSET)){prepareStream(in);}}
    static void prepareStream(InputStream in)throws Exception{
        ByteArrayOutputStream out=new ByteArrayOutputStream();byte[] buf=new byte[8192];int n;
        while((n=in.read(buf))!=-1){stopped();HistoryCatalog.need(n>0&&out.size()+n<=4*1024*1024,"FURNITURE_READ_LIMIT");out.write(buf,0,n);}
        byte[] data=out.toByteArray();StringBuilder sha=new StringBuilder();for(byte b:MessageDigest.getInstance("SHA-256").digest(data))sha.append(String.format(Locale.ROOT,"%02x",b&255));HistoryCatalog.need(sha.toString().equals(SHA256),"FURNITURE_ASSET_SHA");
        String[] lines=new String(data,StandardCharsets.US_ASCII).split("\n",-1);HistoryCatalog.need(lines.length>2&&lines[0].equals("P7FURNITURE\t1")&&lines[lines.length-1].isEmpty(),"FURNITURE_FORMAT");Map<Integer,Spec> all=new TreeMap<>();
        for(int i=1;i<lines.length-1;i++){
            stopped();String[] row=lines[i].split("\t",-1);HistoryCatalog.need(row.length==3&&row[0].equals("F"),"FURNITURE_ROW");int t=HistoryCatalog.integer(row[1]);HistoryCatalog.need(t>0&&t!=162&&!all.containsKey(t),"FURNITURE_SCOPE");byte[] rule=Base64.getDecoder().decode(row[2]);HistoryBson.Value parsed=HistoryBson.parse(rule);
            HistoryCatalog.need(HistoryBson.integer(parsed,"wire_t")==t&&HistoryBson.required(parsed,"q7HistoryFurniturePolicy").string().equals(POLICY),"FURNITURE_POLICY");List<byte[]> base=new ArrayList<>();for(HistoryBson.Value entry:HistoryBson.required(parsed,"base").values()){base.add(entry.bytes.clone());validateOptions(entry);validateProjection(entry);}
            Map<Integer,byte[]> defaults=new TreeMap<>();for(Map.Entry<String,HistoryBson.Value> entry:HistoryBson.required(parsed,"defaults").fields.entrySet()){int ordinal=HistoryCatalog.integer(entry.getKey());HistoryCatalog.need(ordinal>0,"FURNITURE_ORDINAL");validateOptions(entry.getValue());validateProjection(entry.getValue());defaults.put(ordinal,entry.getValue().bytes.clone());}
            boolean enabled=HistoryBson.required(parsed,"enabled").bool();HistoryCatalog.need(!enabled||!base.isEmpty(),"FURNITURE_EMPTY");all.put(t,new Spec(rule,base,defaults,enabled));
        }
        HistoryCatalog.need(all.size()==40,"FURNITURE_POOL_COUNT");stopped();snapshot=Collections.unmodifiableMap(all);
    }
    private static void validateOptions(HistoryBson.Value row)throws IOException{
        HistoryBson.Value options=HistoryBson.required(row,"options");HistoryCatalog.need(options.fields.size()>0,"FURNITURE_NO_OPTIONS");long total=0;
        for(HistoryBson.Value option:options.values()){int w=HistoryBson.integer(option,"w");HistoryCatalog.need(w>0,"FURNITURE_WEIGHT");total+=w;HistoryCatalog.need(total<=Integer.MAX_VALUE,"FURNITURE_WEIGHT_OVERFLOW");HistoryCatalog.need(!HistoryBson.required(option,"g").fields.isEmpty(),"FURNITURE_EMPTY_BUNDLE");}
    }
    private static void validateProjection(HistoryBson.Value row)throws IOException{
        for(HistoryBson.Value option:HistoryBson.required(row,"options").values())for(HistoryBson.Value grant:HistoryBson.required(option,"g").values()){
            HistoryCatalog.need(HistoryBson.integer(grant,"i")>0&&HistoryBson.integer(grant,"n")>0,"FURNITURE_SOURCE_GRANT");
            if(!HistoryBson.required(grant,"pendant").fields.isEmpty()){HistoryCatalog.need(HistoryBson.integer(grant,"skin")==0&&HistoryBson.required(grant,"trans").fields.size()==1,"PENDANT_TRANS_PROJECTION_SHAPE");}
        }
    }
    private static void add(Map<Integer,Integer> amounts,int id,int count)throws IOException{HistoryCatalog.need(id>0&&count>=0,"FURNITURE_ACTUAL_AMOUNT");if(count>0)amounts.put(id,Math.addExact(amounts.containsKey(id)?amounts.get(id):0,count));}
    private static boolean knownOption(Spec spec,byte[] selected)throws IOException{
        List<byte[]> all=new ArrayList<>(spec.base);all.addAll(spec.defaults.values());for(byte[] row:all)for(HistoryBson.Value option:HistoryBson.required(HistoryBson.parse(row),"options").values())if(Arrays.equals(selected,option.bytes))return true;return false;
    }
    public static byte[] reward(LocalResourceEngine.Result child,int t,byte[] selectedOption){
        byte[] original=child.reward();Spec s=spec(t);if(s==null)return original;
        try{
            stopped();HistoryCatalog.need(s.enabled&&selectedOption!=null&&knownOption(s,selectedOption),"FURNITURE_REWARD_SOURCE");Map<Integer,Integer> actual=new HashMap<>(),expected=new HashMap<>();
            for(List<Integer> item:child.itemRewards){HistoryCatalog.need(item.size()==2&&item.get(1)>0,"FURNITURE_ACTUAL_REWARD");add(actual,item.get(0),item.get(1));}
            List<List<Integer>> skins=new ArrayList<>(),exchanged=new ArrayList<>();Map<Integer,HistoryBson.Value> definitions=new LinkedHashMap<>();Map<Integer,Integer> quantities=new HashMap<>();
            for(HistoryBson.Value grant:HistoryBson.required(HistoryBson.parse(selectedOption),"g").values()){int item=HistoryBson.integer(grant,"i");HistoryBson.Value prior=definitions.put(item,grant);HistoryCatalog.need(prior==null||Arrays.equals(BsonLite.withProfileInt(prior.bytes,"n",0),BsonLite.withProfileInt(grant.bytes,"n",0)),"FURNITURE_DUPLICATE_SOURCE_CONFLICT");add(quantities,item,HistoryBson.integer(grant,"n"));}
            for(Map.Entry<Integer,HistoryBson.Value> definition:definitions.entrySet()){
                int item=definition.getKey(),count=quantities.get(item);HistoryBson.Value grant=definition.getValue(),pendant=HistoryBson.required(grant,"pendant");
                if(!pendant.fields.isEmpty()){
                    int newlyOwned=actual.containsKey(item)?actual.get(item):0;HistoryCatalog.need(newlyOwned<=count,"PENDANT_NEW_COUNT");add(expected,item,newlyOwned);int copies=count-newlyOwned;
                    HistoryBson.Value trans=HistoryBson.required(grant,"trans");HistoryCatalog.need(trans.fields.size()==1,"PENDANT_TRANS_SHAPE");HistoryBson.Value pair=trans.values().iterator().next();int id=HistoryBson.integer(pair,"0"),amount=Math.multiplyExact(copies,HistoryBson.integer(pair,"1"));add(expected,id,amount);if(copies>0)exchanged.add(Arrays.asList(item,copies,id,amount));
                }else{add(expected,item,count);if(HistoryBson.integer(grant,"skin")>0)skins.add(Arrays.asList(item,count));}
            }
            HistoryCatalog.need(actual.equals(expected),"FURNITURE_ACTUAL_SOURCE_DELTA");byte[] output=skins.isEmpty()?original:BsonLite.withProfileArray(original,"skin",skins);return exchanged.isEmpty()?output:BsonLite.withProfileArray(output,"pendantExchange",exchanged);
        }catch(Exception e){throw failure(e);}
    }
    private static HistoryBson.Value container(HistoryBson.Value parent,String key)throws IOException{HistoryBson.Value value=parent.get(key);return value==null?HistoryBson.parse(BsonLite.EMPTY_DOCUMENT):value;}
    private static List<Integer> ints(HistoryBson.Value parent,String key)throws IOException{List<Integer> values=new ArrayList<>();HistoryBson.Value field=parent.get(key);if(field!=null)for(HistoryBson.Value value:field.values())values.add(value.integer());return values;}
    private static byte[] pendingTimes(byte[] manager,String key,List<Integer> oldSkins,List<Integer> oldTimes,int skin,int limit,int timestamp)throws IOException{
        HistoryBson.Value hm=HistoryBson.parse(manager);List<Integer> after=ints(container(hm,"ps"),key);int added=after.size()-oldSkins.size();HistoryCatalog.need(added>0&&added<=limit&&after.subList(0,oldSkins.size()).equals(oldSkins),"PENDING_SKIN_DELTA");for(int i=oldSkins.size();i<after.size();i++)HistoryCatalog.need(after.get(i)==skin,"PENDING_SKIN_OUTCOME");
        List<Integer> times=new ArrayList<>(oldTimes);for(int i=0;i<added;i++)times.add(timestamp);HistoryBson.Value psc=container(hm,"psc");return BsonLite.withProfileDocument(manager,"psc",BsonLite.withProfileArray(psc.bytes,key,times));
    }
    public static void skinCopies(LocalResourceEngine.Result result,LocalResourceCatalog catalog,int skin,int count,long now,int t){
        Spec s=spec(t);if(s==null){LocalHomeEngine.q7OriginalSkinCopies(result,catalog,skin,count,now);return;}
        try{
            stopped();HistoryCatalog.need(s.enabled&&catalog.skins.containsKey(skin)&&count>0,"FURNITURE_SKIN_CONTRACT");int hero=catalog.skins.get(skin).hero;
            if(LocalResourceEngine.ownsHero(result.profile,hero)){LocalHomeEngine.q7OriginalSkinCopies(result,catalog,skin,count,now);return;}
            String key=Integer.toString(hero);HistoryBson.Value before=container(HistoryBson.parse(result.profile),"heromgr");List<Integer> oldSkins=ints(container(before,"ps"),key),oldTimes=ints(container(before,"psc"),key);
            HistoryCatalog.need(oldSkins.size()==oldTimes.size(),"EXISTING_PENDING_SKIN_TIME_MISMATCH");for(int timestamp:oldTimes)HistoryCatalog.need(timestamp>=0,"EXISTING_PENDING_SKIN_TIME");HistoryCatalog.need(now>=0,"PENDING_SKIN_TIME");int timestamp=Math.toIntExact(now/1000);int replies=result.replies.size();
            LocalHomeEngine.q7OriginalSkinCopies(result,catalog,skin,count,now); // original mutation exactly once
            HistoryBson.Value after=container(HistoryBson.parse(result.profile),"heromgr");byte[] manager=pendingTimes(after.bytes,key,oldSkins,oldTimes,skin,count,timestamp);HistoryCatalog.need(ints(container(HistoryBson.parse(manager),"ps"),key).size()==oldSkins.size()+count,"PENDING_SKIN_COUNT");result.profile=BsonLite.withProfileDocument(result.profile,"heromgr",manager);
            int synchronizedCopies=0;
            for(int i=replies;i<result.replies.size();i++){LocalResourceEngine.Reply reply=result.replies.get(i);if(!reply.method.equals("syncHeroMgrPendingData"))continue;HistoryBson.Value payload=HistoryBson.parse(reply.parameters),body=HistoryBson.required(payload,"d");byte[] repaired=pendingTimes(body.bytes,key,oldSkins,oldTimes,skin,count,timestamp);result.replies.set(i,new LocalResourceEngine.Reply(reply.method,BsonLite.withProfileDocument(reply.parameters,"d",repaired)));synchronizedCopies++;}
            HistoryCatalog.need(synchronizedCopies==count,"PENDING_SKIN_SYNC_COUNT");
        }catch(Exception e){throw failure(e);}
    }
    private static Spec spec(int t){Map<Integer,Spec> all=snapshot;return all==null?null:all.get(t);}
    public static boolean acceptsPool(int t){Spec s=spec(t);return t==162||(s!=null&&s.enabled);}
    public static byte[] poolRule(LocalFeatureCatalog catalog,String key,Object identity){
        try{Spec s=identity instanceof Integer?spec((Integer)identity):null;if(s==null||!key.equals("P"))return LocalHomeEngine.rule(catalog,key,identity);stopped();HistoryCatalog.need(s.enabled,"FURNITURE_POOL_DISABLED");return s.rule.clone();}catch(Exception e){throw failure(e);}
    }
    public static byte[] defaultRow(LocalFeatureCatalog catalog,String key,Object ordinal,int t){
        try{Spec s=spec(t);if(s==null)return catalog.get(key,ordinal);stopped();HistoryCatalog.need(s.enabled&&key.equals("G")&&ordinal instanceof Integer,"FURNITURE_DEFAULT_SCOPE");byte[] row=s.defaults.get((Integer)ordinal);return row==null?null:row.clone();}catch(Exception e){throw failure(e);}
    }
    private static byte[] pick(List<byte[]> rows,Random random)throws IOException{
        stopped();long total=0;for(byte[] row:rows){int w=HistoryBson.integer(HistoryBson.parse(row),"w");HistoryCatalog.need(w>0,"FURNITURE_WEIGHT");total+=w;}HistoryCatalog.need(total>0&&total<=Integer.MAX_VALUE,"FURNITURE_WEIGHT_TOTAL");int point=random.nextInt((int)total);for(byte[] row:rows){point-=HistoryBson.integer(HistoryBson.parse(row),"w");if(point<0)return row.clone();}throw new AssertionError();
    }
    public static byte[] chooseOuter(List<byte[]> original,Random random,int t){try{Spec s=spec(t);if(s==null)return LocalHomeEngine.q7OriginalChoose(original,random);HistoryCatalog.need(s.enabled,"FURNITURE_POOL_DISABLED");return pick(s.base,random);}catch(Exception e){throw failure(e);}}
    public static byte[] chooseInner(List<byte[]> options,Random random,int t){try{Spec s=spec(t);if(s==null)return LocalHomeEngine.q7OriginalChoose(options,random);HistoryCatalog.need(s.enabled,"FURNITURE_POOL_DISABLED");return pick(options,random);}catch(Exception e){throw failure(e);}}
}
