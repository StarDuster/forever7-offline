package com.project7.localmanager;
import android.content.Context;
import android.content.res.AssetManager;
import android.system.Os;
import java.io.*;
import java.nio.file.*;
import java.util.*;

/** Actual four-seam-patched engine + original public Store, not an engine stub. */
public final class DrawPolicySeamHost {
    static int checks;
    static void check(boolean b,String m){if(!b)throw new AssertionError(m);checks++;}
    static byte[] state(byte[]profile){return BsonLite.documentValue(profile,"ldd");}
    static LocalResourceEngine.Reply reply(LocalResourceEngine.Result result,String method){for(LocalResourceEngine.Reply r:result.replies)if(r.method.equals(method))return r;throw new AssertionError("No typed reply "+method);}
    static Set<String> changed(byte[] a,byte[] b)throws Exception {DrawPolicyBson.Value x=DrawPolicyBson.parse(a),y=DrawPolicyBson.parse(b);Set<String> keys=new TreeSet<>();keys.addAll(x.fields.keySet());keys.addAll(y.fields.keySet());Set<String> changed=new TreeSet<>();for(String k:keys)if(x.get(k)==null||y.get(k)==null||!Arrays.equals(x.get(k).bytes,y.get(k).bytes))changed.add(k);return changed;}
    static void remove(Path p)throws Exception {if(Files.isDirectory(p))try(DirectoryStream<Path>s=Files.newDirectoryStream(p)){for(Path c:s)remove(c);}Files.deleteIfExists(p);}
    public static void main(String[]args)throws Exception {
        Path root=Files.createTempDirectory("p7-draw-seam-pure-synthetic-");
        try {
            AssetManager assets=new AssetManager(new File(args[0]),new File(args[1]),new File(args[2]));Context context=new Context(root.toFile(),assets);
            Path profiles=root.resolve("profiles");Files.createDirectory(profiles);Path file=profiles.resolve("draw_host.bson");
            byte[] baseline=BsonLite.withRequiredClientDefaults(BsonLite.document(new Object[]{"uid",7,"summonCoin",1000,"giftCoin",50,"money",1000,
                "heromgr",BsonLite.document(new Object[]{"hrs",new ArrayList<>()}),"inv",BsonLite.document(new Object[]{"items",new ArrayList<>(),"mc",100}),
                "ldd",BsonLite.document(new Object[]{"ct",0,"iof",false,"hfp",BsonLite.EMPTY_DOCUMENT})}));
            LocalResourceCatalog unpreparedCatalog;try(InputStream in=new FileInputStream(args[1])){unpreparedCatalog=new LocalResourceCatalog(in);}
            byte[] paidBaseline=BsonLite.withProfileDocument(baseline,"ldd",BsonLite.document(new Object[]{"ct",12,"iof",false}));
            LocalResourceEngine.Result rejected=LocalDrawEngine.apply(paidBaseline,unpreparedCatalog,"requestLuckyDrawFile",BsonLite.document(new Object[]{"t",1}),new Random(9));
            LocalResourceEngine.Reply rejectedReply=reply(rejected,"replyLuckyDrawFile");
            check(Boolean.FALSE.equals(BsonLite.boolValue(rejectedReply.parameters,"rt")),"catalog missing gives original typed failure");
            check(BsonLite.intValue(rejected.profile,"summonCoin")==1000&&BsonLite.documentValue(state(rejected.profile),"q7File")==null,"catalog missing rolls back attempted debit and does not uniform-fallback");
            Files.write(file,paidBaseline);
            paidBaseline=new LocalProfileStore(context).updateResources("draw_host","requestFile",BsonLite.document(new Object[]{"t",1})).profile;
            int rejectedWrites=Os.renames;
            LocalResourceEngine.Result rejectedStore=new LocalProfileStore(context).updateResources("draw_host","requestLuckyDrawFile",BsonLite.document(new Object[]{"t",1}));
            check(Boolean.FALSE.equals(BsonLite.boolValue(reply(rejectedStore,"replyLuckyDrawFile").parameters,"rt")),"original Store returns original typed catalog failure");
            check(Arrays.equals(Files.readAllBytes(file),paidBaseline)&&Os.renames==rejectedWrites,"catalog failure never commits original paid BSON byteSame="+Arrays.equals(Files.readAllBytes(file),paidBaseline)+" renames="+(Os.renames-rejectedWrites)+" changedKeys="+changed(paidBaseline,Files.readAllBytes(file)));
            LocalResourceEngine.Result rejectedAll=LocalDrawEngine.apply(paidBaseline,unpreparedCatalog,"requestLuckyDrawFileAndOpenAll",BsonLite.document(new Object[]{"t",1}),new Random(11));
            LocalResourceEngine.Reply allFailure=reply(rejectedAll,"replyLuckyDrawFileAndOpenAll");
            check(Boolean.FALSE.equals(BsonLite.boolValue(allFailure.parameters,"rt")),"AndOpenAll catalog failure typed false");
            System.out.println("DRAW_FAILURE failure_file "+Base64.getEncoder().encodeToString(rejectedReply.parameters));
            System.out.println("DRAW_FAILURE failure_all "+Base64.getEncoder().encodeToString(allFailure.parameters));
            CoreDrawPolicy.prepare(context);
            Files.write(file,baseline);LocalProfileStore store=new LocalProfileStore(context);
            baseline=store.updateResources("draw_host","requestFile",BsonLite.document(new Object[]{"t",1})).profile;
            Thread.currentThread().interrupt();
            try {
                LocalResourceEngine.Result cancelled=store.updateResources("draw_host","requestLuckyDrawFile",BsonLite.document(new Object[]{"t",1}));
                check(Boolean.FALSE.equals(BsonLite.boolValue(reply(cancelled,"replyLuckyDrawFile").parameters,"rt")),"cancelled hook gives original typed failure");
            }finally{Thread.interrupted();}
            check(Arrays.equals(Files.readAllBytes(file),baseline),"cancelled transaction never commits");
            // Subsequent successful request proves the original monitors were released.
            int writes=Os.renames;
            LocalResourceEngine.Result opened=store.updateResources("draw_host","requestLuckyDrawFile",BsonLite.document(new Object[]{"t",1}));
            reply(opened,"replyLuckyDrawFile");check(Os.renames-writes==1,"one original private writeAtomic commit for create");
            check(Arrays.equals(Files.readAllBytes(file),opened.profile),"store committed whole returned candidate");
            byte[] st=state(opened.profile),cards=BsonLite.documentValue(st,"q7File");
            check(BsonLite.intValue(st,"q7WeightedNextOrdinal")==7,"patched saveState reservation committed");
            for(int i=0;i<6;i++){byte[] card=BsonLite.documentValue(cards,Integer.toString(i));check(BsonLite.intValue(card,"q7WeightedVersion")==1,"patched makeFile tagged each new card");check(BsonLite.intValue(card,"q7WeightedOrdinal")==i+1,"slot ordinal stable");}
            byte[] beforeResume=cards.clone();int balance=BsonLite.intValue(opened.profile,"summonCoin");
            LocalResourceEngine.Result resumed=store.updateResources("draw_host","requestFile",BsonLite.document(new Object[]{"t",1}));reply(resumed,"replyFile");
            check(Arrays.equals(beforeResume,BsonLite.documentValue(state(resumed.profile),"q7File")),"requestFile never rerolls");check(BsonLite.intValue(resumed.profile,"summonCoin")==balance,"resume no spend");
            LocalResourceEngine.Result single=store.updateResources("draw_host","requestLuckyDrawCard",BsonLite.document(new Object[]{"t",1,"idx",0}));
            LocalResourceEngine.Reply cardReply=reply(single,"replyLuckyDrawCard");byte[] info=BsonLite.documentValue(cardReply.parameters,"info");
            check(Boolean.TRUE.equals(BsonLite.boolValue(info,"is_open")),"typed single revealed");
            check(BsonLite.intValue(info,"q7WeightedSourceRow")==358&&BsonLite.intValue(info,"q7WeightedRandomId")==369,"tutorial seam kept actual default source rather than hero7");
            check(BsonLite.intValue(info,"q7WeightedCommonId")!=0,"source provenance survived actual grant and reply");
            check(BsonLite.intValue(state(single.profile),"q7WeightedNextOrdinal")==7,"reveal does not reserve again");
            check(LocalResourceEngine.array(BsonLite.documentValue(BsonLite.documentValue(BsonLite.documentValue(info,"other_reward"),"activityReward"),"treasure")).isEmpty(),"primary treasury excluded from generic settlement");
            byte[] afterSingle=Files.readAllBytes(file);
            LocalResourceEngine.Result replay=store.updateResources("draw_host","requestLuckyDrawCard",BsonLite.document(new Object[]{"t",1,"idx",0}));
            reply(replay,"replyLuckyDrawCard");check(BsonLite.intValue(replay.profile,"summonCoin").equals(BsonLite.intValue(single.profile,"summonCoin")),"opened replay no duplicate spend before="+BsonLite.intValue(single.profile,"summonCoin")+" after="+BsonLite.intValue(replay.profile,"summonCoin")+" oldopen="+BsonLite.boolValue(BsonLite.documentValue(BsonLite.documentValue(state(single.profile),"q7File"),"0"),"is_open")+" newopen="+BsonLite.boolValue(BsonLite.documentValue(BsonLite.documentValue(state(replay.profile),"q7File"),"0"),"is_open"));
            check(Arrays.equals(BsonLite.documentValue(state(single.profile),"q7File"),BsonLite.documentValue(state(replay.profile),"q7File")),"opened replay byte-identical group");
            LocalResourceEngine.Result rest=new LocalProfileStore(context).updateResources("draw_host","requestLuckyDrawAllLeftCard",BsonLite.document(new Object[]{"t",1}));
            reply(rest,"replyLuckyDrawAllLeftCard");
            check(BsonLite.intValue(reply(rest,"updateSummonCoin").parameters,"v").equals(BsonLite.intValue(rest.profile,"summonCoin")),"original typed currency update reflects committed actual balance");check(BsonLite.intValue(state(rest.profile),"q7WeightedNextOrdinal")==7,"restart + remaining reveal retains cursor");
            Files.write(file,afterSingle);
            LocalResourceEngine.Result quit=new LocalProfileStore(context).updateResources("draw_host","requestQuitFile",BsonLite.document(new Object[]{"t",1}));reply(quit,"replyQuitFile");
            LocalResourceEngine.Result secondGroup=new LocalProfileStore(context).updateResources("draw_host","requestLuckyDrawFile",BsonLite.document(new Object[]{"t",1}));reply(secondGroup,"replyLuckyDrawFile");
            byte[] secondState=state(secondGroup.profile),secondFile=BsonLite.documentValue(secondState,"q7File");
            check(BsonLite.intValue(BsonLite.documentValue(secondFile,"0"),"q7WeightedOrdinal")==7&&BsonLite.intValue(secondState,"q7WeightedNextOrdinal")==13,"abandon does not refund reservation after restart");
            check(BsonLite.intValue(secondState,"ct")==1,"new group never preadvances actual reveal counter");
            // An actual old stock-generated pending group remains unmarked on resume.
            byte[] legacyFile=LocalDrawEngine.makeFile(unpreparedCatalog,new Random(7),false);
            byte[] legacyState=BsonLite.document(new Object[]{"ct",12,"iof",true,"q7File",legacyFile});
            Files.write(file,BsonLite.withProfileDocument(baseline,"ldd",legacyState));
            LocalResourceEngine.Result oldResume=new LocalProfileStore(context).updateResources("draw_host","requestFile",BsonLite.document(new Object[]{"t",1}));reply(oldResume,"replyFile");
            byte[] oldCards=BsonLite.documentValue(state(oldResume.profile),"q7File");
            for(int i=0;i<6;i++)check(BsonLite.intValue(BsonLite.documentValue(oldCards,Integer.toString(i)),"q7WeightedVersion")==null,"old pending group never retroactively tagged");
            // The private stock writer still owns rename; failure cannot publish cursor/cards/debit.
            Files.write(file,baseline);Os.failNextRename=true;boolean failed=false;
            try{new LocalProfileStore(context).updateResources("draw_host","requestLuckyDrawFile",BsonLite.document(new Object[]{"t",1}));}catch(IOException expected){failed=true;}
            check(failed&&Arrays.equals(Files.readAllBytes(file),baseline),"original store commit failure preserves old complete BSON");
            Files.deleteIfExists(Paths.get(file+".tmp"));
            LocalResourceEngine.Result retry=new LocalProfileStore(context).updateResources("draw_host","requestLuckyDrawFile",BsonLite.document(new Object[]{"t",1}));reply(retry,"replyLuckyDrawFile");
            check(BsonLite.intValue(state(retry.profile),"q7WeightedNextOrdinal")==7,"retry reserves once after failed commit");
            // Actual synthetic tutorial bridge still preserves the old unmarked path.
            byte[] legacy=BsonLite.document(new Object[]{"index",2});byte[] tutorial=CoreDrawPolicy.tutorialCandidate(2,legacy);
            check(BsonLite.intValue(tutorial,"q7Id")==7&&BsonLite.intValue(tutorial,"index")==2,"actual private original tutorial bridge");
            System.out.println("DRAW_POLICY_PATCHED_SEAM_STORE_PASS checks="+checks+" publicAssets="+assets.opened.size()+"; synthetic profile only; no Android/ART/native gameplay");
        }finally{remove(root);}
    }
}
