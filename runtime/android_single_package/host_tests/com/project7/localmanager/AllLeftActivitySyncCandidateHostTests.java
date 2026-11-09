package com.project7.localmanager;
import java.util.*;
/** Private synthetic contract/negative test; no production use. */
public final class AllLeftActivitySyncCandidateHostTests {
    static byte[] sync(int t){return BsonLite.document("t",t,"d",BsonLite.document("ct",1,"iof",false));}
    static byte[] badSync(int t){return BsonLite.document("t",t);}
    static byte[] terminal(int t,boolean rt){return BsonLite.withProfileArray(BsonLite.document("rt",rt,"t",t),"trwd",Arrays.asList(BsonLite.document("index",0)));}
    static LocalResourceEngine.Result base(){return new LocalResourceEngine.Result(BsonLite.EMPTY_DOCUMENT);}
    static LocalResourceEngine.Result shape(int t,int syncs,boolean rt,boolean finalSync){
        LocalResourceEngine.Result r=base();r.add("updateItems",BsonLite.document("i",1));
        for(int i=0;i<syncs;i++){r.add("syncLuckyDrawActivityData",sync(t)); if(t==5) r.add("syncTreasureWishInfo",BsonLite.document("t",t,"tw_id",1,"s",i+1));}
        r.add("replyLuckyDrawAllLeftCard",terminal(t,rt));
        if(finalSync)r.add("syncLuckyDrawActivityData",sync(t));
        r.add("syncNewAchievementData",BsonLite.document("x",1));return r;
    }
    static int syncs(LocalResourceEngine.Result r){int n=0;for(LocalResourceEngine.Reply x:r.replies)if(x!=null&&"syncLuckyDrawActivityData".equals(x.method))n++;return n;}
    static void check(boolean c,String m){if(!c)throw new AssertionError(m);}
    public static void main(String[] a){
        LocalResourceEngine.Result t5=shape(5,5,true,true);AllLeftActivitySyncCandidate.apply(t5);check(syncs(t5)==2,"t5 first+final");
        LocalResourceEngine.Result t354=shape(354,4,true,true);int before354=t354.replies.size();AllLeftActivitySyncCandidate.apply(t354);check(t354.replies.size()==before354,"unproven other pool unchanged");
        LocalResourceEngine.Result normal=shape(1,3,true,true);AllLeftActivitySyncCandidate.apply(normal);check(syncs(normal)==4,"normal1 unchanged");
        LocalResourceEngine.Result failure=shape(5,3,false,true);int b1=failure.replies.size();AllLeftActivitySyncCandidate.apply(failure);check(failure.replies.size()==b1,"failure unchanged");
        LocalResourceEngine.Result noFinal=shape(5,3,true,false);int b2=noFinal.replies.size();AllLeftActivitySyncCandidate.apply(noFinal);check(noFinal.replies.size()==b2,"no final unchanged");
        LocalResourceEngine.Result zero=shape(0,3,true,true);int b3=zero.replies.size();AllLeftActivitySyncCandidate.apply(zero);check(zero.replies.size()==b3,"t<=0 unchanged");
        LocalResourceEngine.Result malformed=base();malformed.add("syncLuckyDrawActivityData",sync(5));malformed.add("syncLuckyDrawActivityData",sync(5));malformed.add("syncLuckyDrawActivityData",badSync(5));malformed.add("replyLuckyDrawAllLeftCard",terminal(5,true));malformed.add("syncLuckyDrawActivityData",sync(5));int b4=malformed.replies.size();AllLeftActivitySyncCandidate.apply(malformed);check(malformed.replies.size()==b4,"malformed middle after removable unchanged");
        LocalResourceEngine.Result badFinal=base();badFinal.add("syncLuckyDrawActivityData",sync(5));badFinal.add("replyLuckyDrawAllLeftCard",terminal(5,true));badFinal.add("syncLuckyDrawActivityData",badSync(5));int b5=badFinal.replies.size();AllLeftActivitySyncCandidate.apply(badFinal);check(badFinal.replies.size()==b5,"malformed final d unchanged");
        LocalResourceEngine.Result nullReply=base();nullReply.replies.add(null);int b6=nullReply.replies.size();AllLeftActivitySyncCandidate.apply(nullReply);check(nullReply.replies.size()==b6,"null reply unchanged");
        LocalResourceEngine.Result other=base();other.add("syncLuckyDrawActivityData",sync(5));int b7=other.replies.size();AllLeftActivitySyncCandidate.apply(other);check(other.replies.size()==b7,"other method unchanged");
        System.out.println("PASS t5/other-pool/normal1/failure/no-final/t<=0/malformed-middle/malformed-final/null-reply/other-method");
    }
}
