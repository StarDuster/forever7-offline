package com.project7.localmanager;
import android.content.Context;
import android.content.res.AssetManager;
import java.io.*;
import java.nio.file.*;
import java.util.*;
/** Two separate verified JVMs, original Store, entirely synthetic persisted v1 profile. */
public final class HistoryV1ReloadHost {
    public static void main(String[] args)throws Exception{
        Path root=Paths.get(args[5]);Files.createDirectories(root.resolve("profiles"));Path file=root.resolve("profiles/compat_host.bson");
        Context context=new Context(root.toFile(),new AssetManager(new File(args[1]),new File(args[2]),new File(args[3]),new File(args[4]),new File(args[6])));
        CoreDrawPolicy.prepare(context);HistoryDrawPolicy.prepare(context);LocalProfileStore store=new LocalProfileStore(context);
        if(args[0].equals("create")){
            byte[] profile=BsonLite.withRequiredClientDefaults(BsonLite.document(new Object[]{"uid",7,"money",1000,"summonCoin",1000,"giftCoin",0,"heromgr",BsonLite.document(new Object[]{"hrs",new ArrayList<>()}),"inv",BsonLite.document(new Object[]{"items",new ArrayList<>(),"mc",100}),"ldd",BsonLite.document(new Object[]{"ct",0,"iof",false,"hfp",BsonLite.EMPTY_DOCUMENT})}));Files.write(file,profile);
            LocalResourceEngine.Result r=store.updateResources("compat_host","requestLuckyDrawFile",BsonLite.document(new Object[]{"t",229}));byte[] cards=BsonLite.documentValue(LocalDrawEngine.state(r.profile,229),"q7File");
            if(!"73fff055e25966ab39960ae65f3ec72589a285e020476045910ccd15a974e669".equals(BsonLite.stringValue(BsonLite.documentValue(cards,"0"),"q7HistoryHash")))throw new AssertionError("not actual v1 factory");
            Files.write(root.resolve("expected-cards.bson"),cards);System.out.println("HISTORY_V1_FACTORY_PERSIST_PASS");
        }else{
            byte[] expected=Files.readAllBytes(root.resolve("expected-cards.bson"));LocalResourceEngine.Result resume=store.updateResources("compat_host","requestFile",BsonLite.document(new Object[]{"t",229}));
            if(!Arrays.equals(expected,BsonLite.documentValue(LocalDrawEngine.state(resume.profile,229),"q7File")))throw new AssertionError("v1 pending rerolled");
            LocalResourceEngine.Result reveal=store.updateResources("compat_host","requestLuckyDrawAllLeftCard",BsonLite.document(new Object[]{"t",229}));byte[] state=LocalDrawEngine.state(reveal.profile,229);
            if(!Integer.valueOf(6).equals(BsonLite.intValue(state,"ct")))throw new AssertionError("v1 reveal failed");
            byte[] opened=BsonLite.documentValue(state,"q7File");for(String key:BsonLite.keys(expected)){
                byte[] a=BsonLite.documentValue(expected,key),b=BsonLite.documentValue(opened,key);
                for(String field:Arrays.asList("q7Id","q7Kind","q7HistoryHash","q7HistoryOrdinal","q7HistoryCommonId")){HistoryBson.Value x=HistoryBson.parse(a).get(field),y=HistoryBson.parse(b).get(field);if(x.type!=y.type||!Arrays.equals(x.bytes,y.bytes))throw new AssertionError("v1 outcome changed "+field);}
            }
            System.out.println("HISTORY_V1_TO_V2_ORIGINAL_STORE_RESUME_REVEAL_PASS");
        }
    }
}
