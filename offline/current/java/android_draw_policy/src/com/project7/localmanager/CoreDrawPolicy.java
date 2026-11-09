package com.project7.localmanager;

import android.content.Context;
import java.io.*;
import java.security.*;
import java.util.*;

/** Ordinary t=1 selector only. The original BSON transaction remains sole owner. */
public final class CoreDrawPolicy {
    public static final String POLICY="normal-ordinal-reserve-on-group-v1";
    public static final String ASSET="project7_draw_policy/catalog-v2.tsv";
    public static final String CATALOG_SHA256="e250ace8d74eaf87769a709532e5a4e1ae69eb2d1acfedf520b79e0323136319";
    private static volatile DrawPolicyCatalog catalog;
    private static final String MARK="q7WeightedVersion", HASH="q7WeightedRuleHash", ORD="q7WeightedOrdinal", END="q7WeightedReservationEnd", NEXT="q7WeightedNextOrdinal";
    private CoreDrawPolicy(){}
    /** Reject only new initial-encounter groups; existing stock groups never call this seam. */
    public static byte[] newbieFile(LocalResourceCatalog stock,int ordinal,Random random){
        throw new IllegalArgumentException("初遇卡池暂不开放新卡组，已有卡组可继续开启或退出。");
    }
    public static void prepare(Context context)throws Exception {
        if(context==null)throw new IOException("Draw policy: NULL_CONTEXT");
        try(InputStream in=context.getAssets().open(ASSET)){prepareStream(in);}
    }
    private static void interrupted()throws InterruptedIOException {if(Thread.currentThread().isInterrupted())throw new InterruptedIOException("Draw policy: CANCELLED");}
    static void prepareStream(InputStream input)throws Exception {
        interrupted();
        ByteArrayOutputStream out=new ByteArrayOutputStream();byte[] buffer=new byte[8192];int n;
        while((n=input.read(buffer))!=-1){interrupted();if(n==0)throw new IOException("Draw policy: EMPTY_STREAM_READ");DrawPolicyCatalog.need(out.size()+n<=262144,"CATALOG_LIMIT");out.write(buffer,0,n);}
        byte[] bytes=out.toByteArray();byte[] digest=MessageDigest.getInstance("SHA-256").digest(bytes);StringBuilder hash=new StringBuilder();for(byte b:digest)hash.append(String.format(Locale.ROOT,"%02x",b&255));
        DrawPolicyCatalog.need(hash.toString().equals(CATALOG_SHA256),"CATALOG_SHA");
        DrawPolicyCatalog parsed=DrawPolicyCatalog.parse(bytes);interrupted();catalog=parsed; // publish only after complete verification
    }
    private static DrawPolicyCatalog ready()throws IOException {DrawPolicyCatalog c=catalog;DrawPolicyCatalog.need(c!=null,"NOT_PREPARED");return c;}
    private static int integer(DrawPolicyBson.Value d,String key,int fallback)throws IOException {DrawPolicyBson.Value v=d.get(key);return v==null?fallback:v.integer();}
    private static byte[] blankSettlement(){return BsonLite.document(new Object[]{"activityReward",BsonLite.document(new Object[]{"hero",Collections.emptyList(),"item",Collections.emptyList(),"treasure",Collections.emptyList(),"fragment",Collections.emptyList(),"treasure_trans",Collections.emptyList()})});}
    private static RuntimeException engineFailure(Exception failure){
        if(failure instanceof IllegalArgumentException)return (IllegalArgumentException)failure;
        if(failure instanceof ArithmeticException)return (ArithmeticException)failure;
        return new IllegalArgumentException("普通抽卡数据校验未通过，本次请求未提交。",failure);
    }
    public static byte[] makeFile(LocalResourceCatalog stock,Random random,boolean first,byte[] state)throws Exception {
        try{return makeFileChecked(stock,random,first,state);}catch(Exception failure){throw engineFailure(failure);}
    }
    private static byte[] makeFileChecked(LocalResourceCatalog stock,Random random,boolean first,byte[] state)throws Exception {
        interrupted();DrawPolicyCatalog c=ready();DrawPolicyCatalog.need(stock!=null&&random!=null,"NULL_STOCK_OR_RANDOM");
        DrawPolicyBson.Value s=DrawPolicyBson.parse(state);
        int ct=integer(s,"ct",0);DrawPolicyCatalog.need(ct>=0&&ct<Integer.MAX_VALUE,"CT_OVERFLOW");
        int base=integer(s,NEXT,ct+1);DrawPolicyCatalog.need(base>=1,"INVALID_CURSOR");base=Math.max(base,ct+1);
        DrawPolicyCatalog.need(base<=Integer.MAX_VALUE-6,"ORDINAL_OVERFLOW");int end=base+6;
        byte[] file=BsonLite.EMPTY_DOCUMENT;
        for(int i=0;i<6;i++){
            interrupted();int ordinal=base+i;DrawPolicyCatalog.Branch override=c.overrides.get(ordinal);int source=0;int rid;
            if(override!=null){rid=override.target;source=override.source;}else{DrawPolicyCatalog.Branch b=c.base.pick(random);source=b.source;rid=b.target;}
            DrawPolicyCatalog.Branch selected=c.pools.get(rid).pick(random);DrawPolicyCatalog.Leaf leaf=c.leaves.get(selected.target);leaf.supported();
            if(leaf.kind.equals("hero")||leaf.kind.equals("memory")){
                DrawPolicyCatalog.need(stock.heroes.containsKey(leaf.id),"MISSING_STOCK_HERO");
                if(leaf.kind.equals("memory"))DrawPolicyCatalog.need(leaf.file<=stock.heroes.get(leaf.id).files,"STOCK_FRAGMENT_RANGE");
            }else if(leaf.kind.equals("treasure"))DrawPolicyCatalog.need(stock.treasures.containsKey(leaf.id+":"+leaf.quality)&&stock.items.containsKey(leaf.id),"MISSING_STOCK_TREASURE");
            else if(leaf.kind.equals("item"))DrawPolicyCatalog.need(stock.items.containsKey(leaf.id),"MISSING_STOCK_ITEM");
            List<Integer> hero=(leaf.kind.equals("hero")||leaf.kind.equals("memory"))?Collections.singletonList(leaf.id):Collections.<Integer>emptyList();
            byte[] card=BsonLite.document(new Object[]{"index",i,"is_open",false,"get_hero",false,"hero",hero,"hero_file",leaf.file,"hero_frag",BsonLite.EMPTY_DOCUMENT,
                "item",Collections.emptyList(),"treasure",Collections.emptyList(),"q7Kind",leaf.kind,"q7Id",leaf.id,"q7Count",leaf.count,"q7Quality",leaf.quality,"q7Wire",2,
                "other_reward",blankSettlement(),MARK,1,"q7WeightedPool",1,HASH,CATALOG_SHA256,"q7WeightedPolicy",POLICY,ORD,ordinal,END,end,
                "q7WeightedSourceRow",source,"q7WeightedRandomId",rid,"q7WeightedCommonId",leaf.common});
            if(leaf.design!=null)card=BsonLite.withProfileDocument(card,"q7Design",leaf.design);
            file=BsonLite.withProfileDocument(file,Integer.toString(i),card);
        }
        return file;
    }
    private static boolean marked(DrawPolicyBson.Value card)throws IOException {
        DrawPolicyBson.Value marker=card.get(MARK);if(marker==null)return false;
        DrawPolicyCatalog.need(marker.integer()==1&&integer(card,"q7WeightedPool",0)==1,"INVALID_RULE_VERSION");
        String hash=DrawPolicyBson.required(card,HASH).string();DrawPolicyCatalog.need(hash.matches("[0-9a-f]{64}"),"INVALID_RULE_HASH");
        DrawPolicyCatalog.need(DrawPolicyBson.required(card,"q7WeightedPolicy").string().equals(POLICY),"INVALID_RULE_POLICY");return true;
    }
    public static byte[] tutorialCandidate(int index,byte[] candidate)throws Exception {
        try{return tutorialCandidateChecked(index,candidate);}catch(Exception failure){throw engineFailure(failure);}
    }
    private static byte[] tutorialCandidateChecked(int index,byte[] candidate)throws Exception {
        if(marked(DrawPolicyBson.parse(candidate))){interrupted();return candidate;}
        return LocalDrawEngine.q7OriginalTutorialCard(index);
    }
    public static byte[] stateForSave(byte[] state,int t)throws Exception {
        try{return stateForSaveChecked(state,t);}catch(Exception failure){throw engineFailure(failure);}
    }
    private static byte[] stateForSaveChecked(byte[] state,int t)throws Exception {
        if(t!=1)return state;
        DrawPolicyBson.Value s=DrawPolicyBson.parse(state),file=s.get("q7File");
        if(file==null)return state;DrawPolicyCatalog.need(file.type==3,"INVALID_FILE_DOCUMENT");
        boolean any=false;for(DrawPolicyBson.Value v:file.values())if(v.get(MARK)!=null)any=true;
        if(!any)return state;interrupted();
        DrawPolicyCatalog.need(file.fields.size()==6,"INVALID_GROUP_SIZE");
        int end=-1,base=-1;String hash=null;
        for(int i=0;i<6;i++){
            DrawPolicyBson.Value card=DrawPolicyBson.required(file,Integer.toString(i));DrawPolicyCatalog.need(marked(card),"MIXED_GROUP");
            int ordinal=DrawPolicyBson.integer(card,ORD),cursor=DrawPolicyBson.integer(card,END);
            String h=DrawPolicyBson.required(card,HASH).string();
            if(i==0){base=ordinal;end=cursor;hash=h;DrawPolicyCatalog.need(base>=1&&base<=Integer.MAX_VALUE-6&&end==base+6,"INVALID_RESERVATION");}
            DrawPolicyCatalog.need(ordinal==base+i&&cursor==end&&h.equals(hash)&&DrawPolicyBson.integer(card,"index")==i,"INCONSISTENT_RESERVATION");
        }
        int old=integer(s,NEXT,1);DrawPolicyCatalog.need(old>=1,"INVALID_CURSOR");
        return BsonLite.withProfileInt(state,NEXT,Math.max(old,end));
    }
    public static byte[] reveal(LocalResourceEngine.Result result,LocalResourceCatalog stock,byte[] card)throws Exception {
        try{return revealChecked(result,stock,card);}catch(Exception failure){throw engineFailure(failure);}
    }
    private static byte[] revealChecked(LocalResourceEngine.Result result,LocalResourceCatalog stock,byte[] card)throws Exception {
        DrawPolicyBson.Value parsed=DrawPolicyBson.parse(card);boolean weighted=marked(parsed);
        if(weighted){
            // Replays never grant again. Original applyCurrent already skips this call.
            DrawPolicyBson.Value opened=parsed.get("is_open");if(opened!=null&&opened.bool())return card;
            interrupted();
            String kind=DrawPolicyBson.required(parsed,"q7Kind").string();
            DrawPolicyCatalog.need(kind.equals("hero")||kind.equals("memory")||kind.equals("item")||kind.equals("treasure")||kind.equals("summonCoin"),"UNSUPPORTED_REVEAL_KIND");
        }
        String kind=weighted?DrawPolicyBson.required(parsed,"q7Kind").string():null;
        int beforeCoin=weighted&&kind.equals("summonCoin")?integer(DrawPolicyBson.parse(result.profile),"summonCoin",0):0;
        byte[] output=LocalDrawEngine.reveal(result,stock,card); // exactly one original grant chain
        if(!weighted)return output;
        if(kind.equals("summonCoin")){
            int after=integer(DrawPolicyBson.parse(result.profile),"summonCoin",0);
            long delta=(long)after-beforeCoin;int count=DrawPolicyBson.integer(parsed,"q7Count");
            DrawPolicyCatalog.need(delta==count&&count>0,"CURRENCY_GRANT_DELTA_MISMATCH");
            // Original grant emits currency item 90; expose it only to the stock
            // primary card renderer. Never copy primary rewards to generic settlement.
            output=BsonLite.withProfileArray(output,"item",Collections.singletonList(Arrays.asList(90,count)));
        }
        return output;
    }
}
