package com.project7.localmanager;
import java.io.*;
import java.nio.file.*;
import java.util.*;
/** Original-engine synthetic old-354 fixture plus finite rejection cases. */
public final class Newbie354BlockHost {
    static int checks;
    static void check(boolean b,String m){if(!b)throw new AssertionError(m);checks++;}
    static byte[] profile(){return BsonLite.withRequiredClientDefaults(BsonLite.document(new Object[]{"uid",7,"summonCoin",1000,"giftCoin",50,"money",1000,"heromgr",BsonLite.document(new Object[]{"hrs",new ArrayList<>()}),"inv",BsonLite.document(new Object[]{"items",new ArrayList<>(),"mc",100}),"ldd",BsonLite.document(new Object[]{"ct",0,"iof",false,"hfp",BsonLite.EMPTY_DOCUMENT})}));}
    static LocalResourceEngine.Reply reply(LocalResourceEngine.Result r,String method){for(LocalResourceEngine.Reply q:r.replies)if(q.method.equals(method))return q;throw new AssertionError("Missing "+method);}
    static LocalResourceEngine.Result request(byte[] p,LocalResourceCatalog c,String method,int idx){return LocalDrawEngine.apply(p,c,method,BsonLite.document(new Object[]{"t",354,"idx",idx}),new Random(91));}
    static void oldFixture(LocalResourceCatalog catalog)throws Exception {
        byte[] six=LocalNewbieDrawEngine.makeFile(catalog,0,new Random(17));
        check(BsonLite.keys(six).size()==6,"original native-free engine constructs six old cards");
        byte[] s=BsonLite.document(new Object[]{"ct",0,"iof",true,"q7File",six});
        byte[] p=profile();LocalResourceEngine.Result seeded=new LocalResourceEngine.Result(p);LocalDrawEngine.saveState(seeded,s,354);p=seeded.profile;
        LocalResourceCatalog emptyCatalog=new LocalResourceCatalog(new ByteArrayInputStream(new byte[0]));
        LocalResourceEngine.Result missing=request(p,emptyCatalog,"requestLuckyDrawCard",0);
        LocalResourceEngine.Reply missingReply=reply(missing,"replyLuckyDrawCard");
        check(Boolean.FALSE.equals(BsonLite.boolValue(missingReply.parameters,"rt")),"old missing-resource reveal retains original failure");
        check(BsonLite.intValue(missing.profile,"summonCoin").equals(BsonLite.intValue(p,"summonCoin")),"old missing-resource failure no debit");
        System.out.println("ORIGINAL_GUARD missing_resource "+Base64.getEncoder().encodeToString(missingReply.parameters));
        for(LocalResourceEngine.Reply q:missing.replies)if(q.method.toLowerCase(Locale.ROOT).contains("message"))System.out.println("ORIGINAL_GUARD_MESSAGE missing_resource "+q.method+" "+Base64.getEncoder().encodeToString(q.parameters));
        LocalResourceEngine.Result resumed=request(p,catalog,"requestFile",0);check(Boolean.TRUE.equals(BsonLite.boolValue(reply(resumed,"replyFile").parameters,"rt")),"old354 resumed");
        byte[] before=BsonLite.documentValue(LocalDrawEngine.state(resumed.profile,354),"q7File");
        LocalResourceEngine.Result single=request(resumed.profile,catalog,"requestLuckyDrawCard",0);
        byte[] info=BsonLite.documentValue(reply(single,"replyLuckyDrawCard").parameters,"info");check(Boolean.TRUE.equals(BsonLite.boolValue(info,"is_open")),"old354 actual reveal");
        byte[] partial=BsonLite.documentValue(LocalDrawEngine.state(single.profile,354),"q7File");
        int open=0;for(String key:BsonLite.keys(partial))if(Boolean.TRUE.equals(BsonLite.boolValue(BsonLite.documentValue(partial,key),"is_open")))open++;
        check(open==1,"original partially revealed fixture");
        LocalResourceEngine.Result again=request(single.profile,catalog,"requestFile",0);check(Arrays.equals(partial,BsonLite.documentValue(LocalDrawEngine.state(again.profile,354),"q7File")),"old partial resume byte-identical");
        LocalResourceEngine.Result replay=request(again.profile,catalog,"requestLuckyDrawCard",0);check(BsonLite.intValue(replay.profile,"summonCoin").equals(BsonLite.intValue(single.profile,"summonCoin")),"old replay no extra debit");
        LocalResourceEngine.Result quit=request(replay.profile,catalog,"requestQuitFile",0);check(Boolean.TRUE.equals(BsonLite.boolValue(reply(quit,"replyQuitFile").parameters,"rt")),"old354 quit");
        if(Boolean.getBoolean("p7.newbie.block.expected")){
            LocalResourceEngine.Result denied=request(quit.profile,catalog,"requestLuckyDrawFile",0);check(Boolean.FALSE.equals(BsonLite.boolValue(reply(denied,"replyLuckyDrawFile").parameters,"rt")),"new354 after old quit denied");
            check(Arrays.equals(BsonLite.documentValue(LocalDrawEngine.state(quit.profile,354),"q7File"),BsonLite.documentValue(LocalDrawEngine.state(denied.profile,354),"q7File")),"quit then reject never recreates cards");
            check(BsonLite.intValue(quit.profile,"summonCoin").equals(BsonLite.intValue(denied.profile,"summonCoin"))&&BsonLite.intValue(LocalDrawEngine.state(quit.profile,354),"ct").equals(BsonLite.intValue(LocalDrawEngine.state(denied.profile,354),"ct")),"quit then reject no debit/count change");
        }
    }
    public static void main(String[] args)throws Exception {
        LocalResourceCatalog catalog;try(InputStream in=new FileInputStream(args[0])){catalog=new LocalResourceCatalog(in);}
        try{CoreDrawPolicy.newbieFile(catalog,0,new Random(1));throw new AssertionError("helper did not refuse");}catch(IllegalArgumentException expected){check(expected.getMessage().contains("初遇"),"fixed understandable rejection");}
        oldFixture(catalog);
        // Original guards are reached before the new single creation seam.
        for(int ct:new int[]{18}){
            LocalResourceEngine.Result seeded=new LocalResourceEngine.Result(profile());
            LocalDrawEngine.saveState(seeded,BsonLite.document(new Object[]{"ct",ct,"iof",false}),354);
            LocalResourceEngine.Result limited=request(seeded.profile,catalog,"requestLuckyDrawFile",0);
            LocalResourceEngine.Reply response=reply(limited,"replyLuckyDrawFile");
            check(Boolean.FALSE.equals(BsonLite.boolValue(response.parameters,"rt")),"original limit state remains failure");
            check(BsonLite.intValue(LocalDrawEngine.state(limited.profile,354),"ct")==18,"original limit count preserved");
            System.out.println("ORIGINAL_GUARD limit18 "+Base64.getEncoder().encodeToString(response.parameters));
            for(LocalResourceEngine.Reply q:limited.replies)if(q.method.toLowerCase(Locale.ROOT).contains("message"))System.out.println("ORIGINAL_GUARD_MESSAGE limit18 "+q.method+" "+Base64.getEncoder().encodeToString(q.parameters));
        }
        LocalResourceEngine.Result noActive=request(profile(),catalog,"requestFile",0);
        LocalResourceEngine.Reply noActiveReply=reply(noActive,"replyFile");
        check(Boolean.FALSE.equals(BsonLite.boolValue(noActiveReply.parameters,"rt")),"old absent-group requestFile failure retained");
        System.out.println("ORIGINAL_GUARD no_active "+Base64.getEncoder().encodeToString(noActiveReply.parameters));
        for(LocalResourceEngine.Reply q:noActive.replies)if(q.method.toLowerCase(Locale.ROOT).contains("message"))System.out.println("ORIGINAL_GUARD_MESSAGE no_active "+q.method+" "+Base64.getEncoder().encodeToString(q.parameters));
        if(Boolean.getBoolean("p7.newbie.block.expected")){
            for(int ct:new int[]{0,7})for(String method:new String[]{"requestLuckyDrawFile","requestLuckyDrawFileAndOpenAll"}){
                byte[] p=profile();LocalResourceEngine.Result seeded=new LocalResourceEngine.Result(p);LocalDrawEngine.saveState(seeded,BsonLite.document(new Object[]{"ct",ct,"iof",false}),354);p=seeded.profile;
                LocalResourceEngine.Result failed=request(p,catalog,method,0);String name=method.equals("requestLuckyDrawFile")?"replyLuckyDrawFile":"replyLuckyDrawFileAndOpenAll";
                LocalResourceEngine.Reply response=reply(failed,name);check(Boolean.FALSE.equals(BsonLite.boolValue(response.parameters,"rt")),"new354 typed false");
                byte[] state=LocalDrawEngine.state(failed.profile,354);check(BsonLite.intValue(state,"ct")==ct,"no fake18 or changed count");
                check(BsonLite.documentValue(state,"q7File")==null,"no new group");check(BsonLite.intValue(failed.profile,"summonCoin")==1000,"no failed debit");
                String label=method.equals("requestLuckyDrawFile")?"failure_file":"failure_all";
                System.out.println("NEWBIE_FAILURE "+ct+" "+label+" "+Base64.getEncoder().encodeToString(response.parameters));
            }
        }
        System.out.println("NEWBIE354_ORIGINAL_ENGINE_PASS checks="+checks+" patchedBlock="+Boolean.getBoolean("p7.newbie.block.expected"));
    }
}
