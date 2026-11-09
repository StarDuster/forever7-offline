package com.project7.localmanager;
import java.io.*;
import java.nio.file.*;
import java.util.*;

/** Real original BSON/stock grant methods, synthetic profile only. No Android SDK runtime. */
public final class DrawPolicyHost {
    static int checks;
    static void check(boolean b,String m){if(!b)throw new AssertionError(m);checks++;}
    interface Work{void run()throws Exception;}
    static void rejects(Work work)throws Exception{try{work.run();}catch(IOException|IllegalArgumentException expected){checks++;return;}throw new AssertionError("expected explicit failure");}
    static class Zero extends Random {public int nextInt(int bound){return 0;}}
    static byte[] state(int ct){return BsonLite.document(new Object[]{"ct",ct,"unknown",99});}
    static byte[] forceCommon(DrawPolicyCatalog graph,LocalResourceCatalog stock,int common)throws Exception {
        int outer=0;
        for(DrawPolicyCatalog.Branch base:graph.base.branches){
            int inner=0;
            for(DrawPolicyCatalog.Branch leaf:graph.pools.get(base.target).branches){
                if(leaf.target==common){final int a=outer,b=inner;Random selected=new Random(){int n;public int nextInt(int bound){return (n++%2==0)?a:b;}};return BsonLite.documentValue(CoreDrawPolicy.makeFile(stock,selected,false,state(12)),"0");}
                inner+=leaf.weight;
            }
            outer+=base.weight;
        }
        throw new AssertionError("common not in base "+common);
    }
    static int firstKind(DrawPolicyCatalog graph,String kind){for(DrawPolicyCatalog.Leaf leaf:graph.leaves.values())if(leaf.kind.equals(kind)&&leaf.design==null)return leaf.common;throw new AssertionError(kind);}
    public static void main(String[]args)throws Exception{
        LocalResourceCatalog stock;try(InputStream in=Files.newInputStream(Paths.get(args[1]))){stock=new LocalResourceCatalog(in);}
        rejects(()->CoreDrawPolicy.makeFile(stock,new Zero(),false,state(0)));
        byte[] asset=Files.readAllBytes(Paths.get(args[0]));CoreDrawPolicy.prepareStream(new ByteArrayInputStream(asset));
        byte[] tamper=asset.clone();tamper[10]^=1;rejects(()->CoreDrawPolicy.prepareStream(new ByteArrayInputStream(tamper)));
        DrawPolicyCatalog graph=DrawPolicyCatalog.parse(asset);
        List<DrawPolicyCatalog.Distribution> distributions=new ArrayList<>();distributions.add(graph.base);distributions.addAll(graph.pools.values());
        for(DrawPolicyCatalog.Distribution distribution:distributions){
            int position=0;
            for(DrawPolicyCatalog.Branch branch:distribution.branches){
                final int lower=position,upper=position+branch.weight-1;
                Random low=new Random(){public int nextInt(int bound){return lower;}};
                Random high=new Random(){public int nextInt(int bound){return upper;}};
                check(distribution.pick(low).source==branch.source&&distribution.pick(high).source==branch.source,"exact inclusive/exclusive integer boundaries");position+=branch.weight;
            }
            check(position==distribution.total,"integer mass conservation");
        }
        byte[] file=CoreDrawPolicy.makeFile(stock,new Zero(),true,state(0));
        DrawPolicyBson.Value parsed=DrawPolicyBson.parse(file);check(parsed.fields.size()==6,"six cards");
        int[] expected={2034,40283,1937,2228,40280,1841};
        for(int i=0;i<6;i++){
            byte[] card=BsonLite.documentValue(file,Integer.toString(i));
            check(BsonLite.intValue(card,"q7WeightedCommonId")==expected[i],"original default leaf");
            check(BsonLite.intValue(card,"q7WeightedOrdinal")==i+1,"fixed ordinal");
            check(!BsonLite.boolValue(card,"is_open"),"masked unopened");
            check(CoreDrawPolicy.tutorialCandidate(i,card)==card,"marked candidate cannot become tutorial hero7");
        }
        byte[] s=BsonLite.withProfileDocument(state(0),"q7File",file);
        byte[] saved=CoreDrawPolicy.stateForSave(s,1);
        check(BsonLite.intValue(saved,"q7WeightedNextOrdinal")==7,"reserve six once");
        check(BsonLite.intValue(saved,"ct")==0&&BsonLite.intValue(saved,"unknown")==99,"preserve count and unknown");
        check(Arrays.equals(saved,CoreDrawPolicy.stateForSave(saved,1)),"repeat cursor idempotent");
        byte[] advanced=BsonLite.withProfileInt(saved,"q7WeightedNextOrdinal",22);
        check(BsonLite.intValue(CoreDrawPolicy.stateForSave(advanced,1),"q7WeightedNextOrdinal")==22,"max reservation");
        check(CoreDrawPolicy.stateForSave(s,5)==s,"pool isolation");
        byte[] old=BsonLite.withProfileDocument(state(0),"q7File",BsonLite.document(new Object[]{"0",BsonLite.document(new Object[]{"index",0})}));
        check(CoreDrawPolicy.stateForSave(old,1)==old,"old group unchanged");
        byte[] corrupt=BsonLite.withProfileDocument(file,"1",BsonLite.withProfileInt(BsonLite.documentValue(file,"1"),"q7WeightedOrdinal",100));
        rejects(()->CoreDrawPolicy.stateForSave(BsonLite.withProfileDocument(state(0),"q7File",corrupt),1));
        rejects(()->CoreDrawPolicy.makeFile(stock,new Zero(),false,state(Integer.MAX_VALUE-3)));
        // Same actual stock Result and original reveal, not synthetic reward construction.
        byte[] profile=BsonLite.document(new Object[]{"uid",7,"heromgr",BsonLite.document(new Object[]{"hrs",new ArrayList<>()}),"inv",BsonLite.document(new Object[]{"items",new ArrayList<>(),"mc",100}),"ldd",state(0),"summonCoin",100});
        LocalResourceEngine.Result result=new LocalResourceEngine.Result(profile);
        byte[] before=result.profile.clone();
        byte[] revealed=CoreDrawPolicy.reveal(result,stock,forceCommon(graph,stock,firstKind(graph,"hero")));
        check(!Arrays.equals(before,result.profile),"original stock hero grant changed profile");
        check(BsonLite.boolValue(revealed,"is_open"),"original reveal opened");
        check(BsonLite.boolValue(revealed,"get_hero"),"actual original new hero");
        before=result.profile.clone();byte[] replay=CoreDrawPolicy.reveal(result,stock,revealed);
        check(replay==revealed&&Arrays.equals(before,result.profile),"already open no duplicate grant");
        byte[] treasure=CoreDrawPolicy.reveal(result,stock,forceCommon(graph,stock,firstKind(graph,"treasure")));
        check(!LocalResourceEngine.array(BsonLite.documentValue(treasure,"treasure")).isEmpty(),"original treasure UUIDs returned");
        result=new LocalResourceEngine.Result(profile);
        byte[] memory=CoreDrawPolicy.reveal(result,stock,forceCommon(graph,stock,firstKind(graph,"memory")));
        check(BsonLite.boolValue(memory,"is_open"),"original memory reveal");
        check(BsonLite.intValue(BsonLite.documentValue(BsonLite.documentValue(result.profile,"ldd"),"hfp"),Integer.toString(BsonLite.intValue(memory,"q7Id")))>0,"real hfp bitmask");
        check(LocalResourceEngine.array(BsonLite.documentValue(BsonLite.documentValue(BsonLite.documentValue(treasure,"other_reward"),"activityReward"),"treasure")).isEmpty(),"primary treasure excluded from generic settlement");
        byte[] currency=CoreDrawPolicy.reveal(result,stock,forceCommon(graph,stock,2228));
        check(BsonLite.intValue(result.profile,"summonCoin")==108,"real original currency grant exactly8");
        byte[] activity=BsonLite.documentValue(BsonLite.documentValue(currency,"other_reward"),"activityReward");
        check(LocalResourceEngine.array(BsonLite.documentValue(activity,"item")).isEmpty(),"currency excluded from generic settlement");
        check(BsonLite.intValue(LocalResourceEngine.array(BsonLite.documentValue(currency,"item")).get(0),"0")==90,"original currency item mapping");
        byte[] designCard=forceCommon(graph,stock,50390);byte[] design=CoreDrawPolicy.reveal(result,stock,designCard);
        boolean matched=false;
        for(byte[] item:LocalResourceEngine.array(BsonLite.documentValue(BsonLite.documentValue(result.profile,"inv"),"items")))if(BsonLite.intValue(item,"i")==1332&&Arrays.equals(BsonLite.documentValue(item,"tr"),BsonLite.documentValue(designCard,"q7Design")))matched=true;
        check(matched,"real grant installed exact tr, no nested tr or reused original UUID");
        byte[] heroCandidate=forceCommon(graph,stock,firstKind(graph,"hero"));
        LocalResourceEngine.Result dupResult=new LocalResourceEngine.Result(profile);
        byte[] firstHero=CoreDrawPolicy.reveal(dupResult,stock,heroCandidate);
        byte[] duplicateHero=CoreDrawPolicy.reveal(dupResult,stock,heroCandidate);
        check(!BsonLite.boolValue(duplicateHero,"get_hero"),"duplicate hero not shown as new");
        check(LocalResourceEngine.array(BsonLite.documentValue(BsonLite.documentValue(BsonLite.documentValue(duplicateHero,"other_reward"),"activityReward"),"fragment")).isEmpty(),"primary duplicate conversion excluded from generic settlement");
        String[] labels={"unopened_hero","opened_hero","duplicate_hero","memory","treasure","design","currency"};
        byte[][] fixtures={heroCandidate,firstHero,duplicateHero,memory,treasure,design,currency};
        for(int i=0;i<labels.length;i++)System.out.println("DRAW_FIXTURE "+labels[i]+" "+Base64.getEncoder().encodeToString(fixtures[i]));
        System.out.println("DRAW_POLICY_REAL_TRANSLATED_HOST_PASS checks="+checks+"; no Android/ART/gameplay or full settlement claim");
    }
}
