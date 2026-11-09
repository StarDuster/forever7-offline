package com.project7.localmanager;
import android.content.Context;
import android.content.res.AssetManager;
import android.system.Os;
import java.io.*;
import java.nio.file.*;
import java.util.*;
/** Actual patched engine and original Store, entirely synthetic profiles. */
public final class HistoryEngineHost {
    static int checks;
    static void check(boolean b,String m){if(!b)throw new AssertionError(m);checks++;}
    static LocalResourceEngine.Reply reply(LocalResourceEngine.Result r,String method){for(LocalResourceEngine.Reply q:r.replies)if(q.method.equals(method))return q;throw new AssertionError("No reply "+method);}
    static byte[] state(byte[] p,int t){return LocalDrawEngine.state(p,t);}
    static int value(byte[] d,String k){Integer n=BsonLite.intValue(d,k);return n==null?0:n;}
    static int inventory(byte[] p,int id){int n=0;for(byte[] item:LocalResourceEngine.array(BsonLite.documentValue(BsonLite.documentValue(p,"inv"),"items")))if(value(item,"i")==id)n+=value(item,"w");return n;}
    static byte[] seed(){return BsonLite.withRequiredClientDefaults(BsonLite.document(new Object[]{"uid",7,"money",1000,"summonCoin",1000,"giftCoin",0,"heromgr",BsonLite.document(new Object[]{"hrs",new ArrayList<>()}),"inv",BsonLite.document(new Object[]{"items",new ArrayList<>(),"mc",100}),"ldd",BsonLite.document(new Object[]{"ct",0,"iof",false,"hfp",BsonLite.EMPTY_DOCUMENT})}));}
    static void remove(Path p)throws Exception{if(Files.isDirectory(p))try(DirectoryStream<Path>d=Files.newDirectoryStream(p)){for(Path f:d)remove(f);}Files.deleteIfExists(p);}
    static byte[] withState(byte[] profile,int t,byte[] s){LocalResourceEngine.Result r=new LocalResourceEngine.Result(profile);LocalDrawEngine.saveState(r,s,t);return r.profile;}
    static LocalResourceEngine.Result apply(byte[] p,LocalResourceCatalog c,String method,int t,int idx){return LocalDrawEngine.apply(p,c,method,BsonLite.document(new Object[]{"t",t,"idx",idx}),new Random(9));}
    static byte[] force(HistoryCatalog graph,LocalResourceCatalog catalog,int common)throws Exception{
        for(HistoryCatalog.Spec spec:graph.specs.values())if(spec.enabled){int outer=0;for(HistoryCatalog.Edge b:spec.base.edges){int inner=0;for(HistoryCatalog.Edge e:graph.random.get(b.target).edges){if(e.target==common){int ordinal=1001;boolean conflict=true;while(conflict){conflict=false;for(int i=0;i<6;i++)if(spec.defaults.containsKey(ordinal+i)){ordinal+=6;conflict=true;break;}}
            final int a=outer,z=inner;Random random=new Random(){int n;public int nextInt(int bound){return (n++%2==0)?a:z;}};
            byte[] file=HistoryDrawPolicy.makeFile(catalog,catalog.pools.get(spec.id),BsonLite.document(new Object[]{"ct",ordinal-1}),random);return BsonLite.documentValue(file,"0");}inner+=e.weight;}outer+=b.weight;}}
        return null;
    }
    public static void main(String[] args)throws Exception{
        Path root=Files.createTempDirectory("history-original-engine-synthetic-");
        try{
            AssetManager assets=new AssetManager(new File(args[0]),new File(args[1]),new File(args[2]),new File(args[3]),new File(args[4]));Context context=new Context(root.toFile(),assets);
            CoreDrawPolicy.prepare(context);HistoryDrawPolicy.prepare(context);
            LocalResourceCatalog catalog;try(InputStream in=new FileInputStream(args[1])){catalog=new LocalResourceCatalog(in);}
            HistoryCatalog graph=HistoryCatalog.parse(Files.readAllBytes(Paths.get(args[3])));
            check(graph.specs.values().stream().filter(p->p.enabled).count()==380,"real ready family count");
            check(!catalog.pools.containsKey(1)&&!catalog.pools.containsKey(354),"reserved normal/newbie not inserted");
            LocalResourceCatalog.Pool old484=catalog.pools.get(484);int oldDrops=old484.drops.size();HistoryDrawPolicy.augmentCatalog(catalog);
            check(catalog.pools.get(484)==old484&&old484.drops.size()==oldDrops&&oldDrops>0,"existing484 untouched/idempotent");
            check(catalog.pools.get(229).s.isEmpty()&&catalog.pools.get(229).a.isEmpty()&&catalog.pools.get(229).drops.isEmpty(),"true empty plain lists, no dummy P/drop");
            byte[] ordinalTen=HistoryDrawPolicy.makeFile(catalog,catalog.pools.get(229),BsonLite.document(new Object[]{"ct",9}),new Random(5));
            byte[] tenth=BsonLite.documentValue(ordinalTen,"0");check(value(tenth,"q7HistoryNormalRow")==360&&value(tenth,"q7HistoryRandomId")==5069&&value(tenth,"q7HistoryOrdinal")==10,"official default oracle normal360 to RR5069, not RR360");
            boolean scopeRejected=false;try{HistoryDrawPolicy.stateForSave(BsonLite.document(new Object[]{"ct",9,"q7File",ordinalTen}),243);}catch(IllegalArgumentException expected){scopeRejected=true;}
            check(scopeRejected,"cross-pool reservation cannot be saved");
            LocalResourceEngine.Result base=new LocalResourceEngine.Result(seed());LocalResourceEngine.grant(base,catalog,"item",11452,2,1);byte[] baseline=base.profile;
            Path directory=root.resolve("profiles");Files.createDirectory(directory);Path file=directory.resolve("history_host.bson");Files.write(file,baseline);
            Set<Integer> sourceGiftIds=new LinkedHashSet<>();
            for(String row:Files.readAllLines(Paths.get(args[1])))if(row.startsWith("B\t"))sourceGiftIds.add(Integer.parseInt(row.split("\t")[1]));
            check(sourceGiftIds.equals(new LinkedHashSet<Integer>(Arrays.asList(1,354,484))),"fixed B gift keys are1/354/484, six is interval not type");
            check(catalog.drawGifts.keySet().equals(sourceGiftIds),"actual original parsed gift map equals fixed source rows");
            for(int historical:graph.specs.keySet())check(!sourceGiftIds.contains(historical),"every historical pool has unique gift owner, no stock source overlap");
            System.out.println("HISTORY_STOCK_GIFT_IDS "+catalog.drawGifts.keySet());
            // Actual original t6 regression: source gift interval6 is not a pool6 map key.
            LocalProfileStore overlapStore=new LocalProfileStore(context);int[] overlapWallet=new int[3];
            for(int round=0;round<3;round++){
                if(round>0)overlapStore.updateResources("history_host","requestQuitFile",BsonLite.document(new Object[]{"t",6}));
                if(round==2){byte[] prior=Files.readAllBytes(file),priorState=state(prior,6),priorCards=BsonLite.documentValue(priorState,"q7File");
                    for(String k:BsonLite.keys(priorCards))priorCards=BsonLite.withProfileDocument(priorCards,k,BsonLite.withProfileString(BsonLite.documentValue(priorCards,k),"q7HistoryGiftDay","2000-01-01"));
                    priorState=BsonLite.withProfileDocument(priorState,"q7File",priorCards);priorState=BsonLite.withProfileString(priorState,"q7HistoryGiftDay","2000-01-01");priorState=BsonLite.withProfileString(priorState,"q7DrawDay","2000-01-01");Files.write(file,withState(prior,6,priorState));}
                LocalResourceEngine.Result got=new LocalProfileStore(context).updateResources("history_host","requestLuckyDrawFileAndOpenAll",BsonLite.document(new Object[]{"t",6}));reply(got,"replyLuckyDrawFileAndOpenAll");overlapWallet[round]=value(got.profile,"giftCoin");
                check(overlapWallet[round]==(round==2?2:1)&&value(state(got.profile,6),"ct")==6*(round+1),"t6 unique gift owner first/same-day/cross-day");
            }
            System.out.println("HISTORY_STOCK_GIFT_OVERLAP wallets="+Arrays.toString(overlapWallet));Files.write(file,baseline);
            LocalProfileStore store=new LocalProfileStore(context);baseline=store.updateResources("history_host","requestFile",BsonLite.document(new Object[]{"t",229})).profile;
            int before=Os.renames;LocalResourceEngine.Result opened=store.updateResources("history_host","requestLuckyDrawFile",BsonLite.document(new Object[]{"t",229}));
            check(Boolean.TRUE.equals(BsonLite.boolValue(reply(opened,"replyLuckyDrawFile").parameters,"rt")),"actual plain new group without choice succeeds");
            check(Os.renames-before==1&&Arrays.equals(Files.readAllBytes(file),opened.profile),"one original Store atomic whole commit");
            check(value(opened.profile,"summonCoin")==1000&&inventory(opened.profile,11452)==2,"history free no money/ticket debit");
            check(value(state(opened.profile,229),"ct")==0&&value(state(opened.profile,229),"q7HistoryNextOrdinal")==7,"reserve only, no pre-reveal ct increment");
            byte[] cards=BsonLite.documentValue(state(opened.profile,229),"q7File");for(int i=0;i<6;i++){byte[] card=BsonLite.documentValue(cards,Integer.toString(i));check(value(card,"q7HistoryPool")==229&&value(card,"q7HistoryOrdinal")==i+1&&!BsonLite.boolValue(card,"is_open"),"fixed masked per-t card");}
            LocalResourceEngine.Result resumed=new LocalProfileStore(context).updateResources("history_host","requestFile",BsonLite.document(new Object[]{"t",229}));
            check(Arrays.equals(cards,BsonLite.documentValue(state(resumed.profile,229),"q7File")),"new Store/relogin no reroll");
            byte[] aBefore=state(resumed.profile,229);LocalResourceEngine.Result other=store.updateResources("history_host","requestLuckyDrawFile",BsonLite.document(new Object[]{"t",243}));reply(other,"replyLuckyDrawFile");
            check(Arrays.equals(aBefore,state(other.profile,229))&&value(state(other.profile,243),"q7HistoryNextOrdinal")==7,"two simultaneous pools isolated");
            LocalResourceEngine.Result all=store.updateResources("history_host","requestLuckyDrawAllLeftCard",BsonLite.document(new Object[]{"t",229}));reply(all,"replyLuckyDrawAllLeftCard");
            check(value(state(all.profile,229),"ct")==6&&value(state(all.profile,243),"ct")==0,"only accepted pool reveals count");
            check(value(all.profile,"giftCoin")==1&&value(state(all.profile,229),"q7HistoryGiftUsed")==1,"source105 real global gift, daily receipt");
            check(value(all.profile,"summonCoin")>=1000&&inventory(all.profile,11452)>=2,"free applies through all reveal spend sites");
            byte[] afterAll=all.profile;LocalResourceEngine.Result replay=store.updateResources("history_host","requestLuckyDrawCard",BsonLite.document(new Object[]{"t",229,"idx",0}));
            check(value(replay.profile,"giftCoin")==value(afterAll,"giftCoin")&&Arrays.equals(BsonLite.documentValue(state(afterAll,229),"q7File"),BsonLite.documentValue(state(replay.profile,229),"q7File")),"opened replay no primary/gift duplication");
            // Same day second interval awards no second daily gift.
            store.updateResources("history_host","requestQuitFile",BsonLite.document(new Object[]{"t",229}));
            LocalResourceEngine.Result again=store.updateResources("history_host","requestLuckyDrawFileAndOpenAll",BsonLite.document(new Object[]{"t",229}));reply(again,"replyLuckyDrawFileAndOpenAll");
            check(value(state(again.profile,229),"ct")==12&&value(again.profile,"giftCoin")==1,"same day cap at second interval");
            // Other pool's receipt is independent, wallet sharing follows source coin.
            LocalResourceEngine.Result bAll=store.updateResources("history_host","requestLuckyDrawAllLeftCard",BsonLite.document(new Object[]{"t",243}));reply(bAll,"replyLuckyDrawAllLeftCard");
            check(value(bAll.profile,"giftCoin")==2&&value(state(bAll.profile,243),"q7HistoryGiftUsed")==1,"per-t daily receipt independent, actual shared105 wallet");
            // Seed an actual prior-day persisted snapshot; never alter the process clock.
            byte[] yesterdayState=state(again.profile,229);byte[] yesterdayCards=BsonLite.documentValue(yesterdayState,"q7File");
            for(String key:BsonLite.keys(yesterdayCards))yesterdayCards=BsonLite.withProfileDocument(yesterdayCards,key,BsonLite.withProfileString(BsonLite.documentValue(yesterdayCards,key),"q7HistoryGiftDay","2000-01-01"));
            yesterdayState=BsonLite.withProfileDocument(yesterdayState,"q7File",yesterdayCards);yesterdayState=BsonLite.withProfileString(yesterdayState,"q7HistoryGiftDay","2000-01-01");yesterdayState=BsonLite.withProfileString(yesterdayState,"q7DrawDay","2000-01-01");
            Files.write(file,withState(again.profile,229,yesterdayState));store.updateResources("history_host","requestQuitFile",BsonLite.document(new Object[]{"t",229}));
            LocalResourceEngine.Result nextDay=new LocalProfileStore(context).updateResources("history_host","requestLuckyDrawFileAndOpenAll",BsonLite.document(new Object[]{"t",229}));reply(nextDay,"replyLuckyDrawFileAndOpenAll");
            check(value(state(nextDay.profile,229),"ct")==18&&value(nextDay.profile,"giftCoin")==2,"new native day resets gift cap, cumulative ct interval retained");
            check(value(state(nextDay.profile,229),"q7HistoryNextOrdinal")==19,"day does not reset reserved ordinals");
            // Nonhistory policies still use the unchanged private stock spend bridge.
            Files.write(file,baseline);LocalResourceEngine.Result normal=store.updateResources("history_host","requestLuckyDrawFileAndOpenAll",BsonLite.document(new Object[]{"t",1}));reply(normal,"replyLuckyDrawFileAndOpenAll");
            check(inventory(normal.profile,11452)<2||value(normal.profile,"summonCoin")<1000,"normal is not made history-free");
            Files.write(file,baseline);store.updateResources("history_host","setChooseHeroes",BsonLite.document(new Object[]{"t",484,"h",Arrays.asList(old484.s.get(0),old484.a.get(0))}));
            LocalResourceEngine.Result legacy484=store.updateResources("history_host","requestLuckyDrawFile",BsonLite.document(new Object[]{"t",484}));reply(legacy484,"replyLuckyDrawFile");
            check(value(legacy484.profile,"summonCoin")==993,"existing484 stock charge unchanged");
            check(BsonLite.intValue(BsonLite.documentValue(BsonLite.documentValue(state(legacy484.profile,484),"q7File"),"0"),"q7HistoryVersion")==null,"existing484 never tagged as history");
            // Non105 source reward coin is an original inventory grant and true extra.
            int inventoryPool=0;for(HistoryCatalog.Spec spec:graph.specs.values())if(spec.enabled&&spec.giftCoin!=105){inventoryPool=spec.id;break;}
            check(inventoryPool>0,"real non105 family present");int coin=graph.specs.get(inventoryPool).giftCoin;
            Files.write(file,baseline);LocalResourceEngine.Result bonus=store.updateResources("history_host","requestLuckyDrawFileAndOpenAll",BsonLite.document(new Object[]{"t",inventoryPool}));LocalResourceEngine.Reply batch=reply(bonus,"replyLuckyDrawFileAndOpenAll");
            check(inventory(bonus.profile,coin)==inventory(baseline,coin)+1,"source non105 inventory gift exactly once");
            List<byte[]> results=LocalResourceEngine.array(BsonLite.documentValue(batch.parameters,"trwd"));boolean extra=false;
            for(byte[] result:results){byte[] otherDoc=BsonLite.documentValue(result,"other_reward");byte[] items=BsonLite.documentValue(otherDoc,"item");if(items!=null)for(byte[] pair:LocalResourceEngine.array(items))if(value(pair,"0")==coin&&value(pair,"1")==1)extra=true;}
            check(extra,"actual non105 true extra reaches original other_reward.item");
            for(byte[] r:results)if(value(r,"gift")>0||BsonLite.documentValue(BsonLite.documentValue(r,"other_reward"),"item")!=null)System.out.println("HISTORY_GIFT_FIXTURE "+Base64.getEncoder().encodeToString(r));
            // Existing source epochs/list changes cannot invalidate fixed pending outcomes.
            byte[] unchanged=BsonLite.documentValue(state(bonus.profile,inventoryPool),"q7File");check(unchanged!=null,"persisted history outcomes");
            // Corrupt a synthetic candidate scope: original typed catch discards actual in-memory grants.
            Files.write(file,baseline);LocalResourceEngine.Result pending=store.updateResources("history_host","requestLuckyDrawFile",BsonLite.document(new Object[]{"t",229}));
            byte[] corruptState=state(pending.profile,229),corruptFile=BsonLite.documentValue(corruptState,"q7File");
            corruptFile=BsonLite.withProfileDocument(corruptFile,"0",BsonLite.withProfileInt(BsonLite.documentValue(corruptFile,"0"),"q7HistoryPool",243));
            // Seed raw per-t state without using the intentionally rejecting production save helper.
            byte[] ad=BsonLite.documentValue(BsonLite.documentValue(pending.profile,"ldd"),"ad");List<byte[]> pairs=LocalResourceEngine.array(ad);List<List<Object>> replacement=new ArrayList<>();
            for(byte[] pair:pairs){int t=value(pair,"0");byte[] entry=BsonLite.documentValue(pair,"1");if(t==229)entry=BsonLite.withProfileDocument(entry,"q7File",corruptFile);replacement.add(Arrays.<Object>asList(t,entry));}
            byte[] corrupted=BsonLite.withProfileDocument(pending.profile,"ldd",BsonLite.withProfileArray(BsonLite.documentValue(pending.profile,"ldd"),"ad",replacement));Files.write(file,corrupted);
            LocalResourceEngine.Result invalid=store.updateResources("history_host","requestLuckyDrawCard",BsonLite.document(new Object[]{"t",229,"idx",0}));
            check(Boolean.FALSE.equals(BsonLite.boolValue(reply(invalid,"replyLuckyDrawCard").parameters,"rt")),"invalid scope gives original typed failure");
            check(Arrays.equals(BsonLite.documentValue(corrupted,"inv"),BsonLite.documentValue(invalid.profile,"inv"))&&value(invalid.profile,"giftCoin")==value(corrupted,"giftCoin"),"scope failure discards main and gift inventory changes");
            // Unsupported positive-leaf family is rejected whole, never renormalized.
            for(String request:new String[]{"requestLuckyDrawFile","requestLuckyDrawFileAndOpenAll"}){
                Files.write(file,baseline);LocalResourceEngine.Result denied=store.updateResources("history_host",request,BsonLite.document(new Object[]{"t",17}));String response=request.equals("requestLuckyDrawFile")?"replyLuckyDrawFile":"replyLuckyDrawFileAndOpenAll";
                LocalResourceEngine.Reply packet=reply(denied,response);check(Boolean.FALSE.equals(BsonLite.boolValue(packet.parameters,"rt"))&&BsonLite.documentValue(state(denied.profile,17),"q7File")==null,"unsupported whole pool original typed failure");
                System.out.println("HISTORY_FAILURE "+(request.equals("requestLuckyDrawFile")?"failure_file":"failure_all")+" "+Base64.getEncoder().encodeToString(packet.parameters));
            }
            Files.write(file,baseline);Thread.currentThread().interrupt();
            try{LocalResourceEngine.Result cancelled=store.updateResources("history_host","requestLuckyDrawFile",BsonLite.document(new Object[]{"t",229}));check(Boolean.FALSE.equals(BsonLite.boolValue(reply(cancelled,"replyLuckyDrawFile").parameters,"rt")),"cancelled history gives original failure");}finally{Thread.interrupted();}
            check(BsonLite.documentValue(state(Files.readAllBytes(file),229),"q7File")==null,"cancelled factory publishes no group");
            // Original writer failure after actual in-memory awards publishes none.
            Files.write(file,baseline);byte[] old=Files.readAllBytes(file);Os.failNextRename=true;boolean failed=false;
            try{store.updateResources("history_host","requestLuckyDrawFileAndOpenAll",BsonLite.document(new Object[]{"t",229}));}catch(IOException expected){failed=true;}
            check(failed&&Arrays.equals(old,Files.readAllBytes(file)),"original Store failure rolls back all debit/main/gift/receipt/cursor");Files.deleteIfExists(Paths.get(file+".tmp"));
            LocalResourceEngine.Result retry=new LocalProfileStore(context).updateResources("history_host","requestLuckyDrawFileAndOpenAll",BsonLite.document(new Object[]{"t",229}));reply(retry,"replyLuckyDrawFileAndOpenAll");check(value(retry.profile,"giftCoin")==1,"retry grants committed daily bonus once");
            // Generic real original primary adapters, exact public common forcing.
            Set<String> covered=new TreeSet<>();for(HistoryCatalog.Leaf leaf:graph.leaves.values())if(!covered.contains(leaf.kind)&&!leaf.kind.equals("unsupported")){
                byte[] card=force(graph,catalog,leaf.common);if(card==null)continue;int t=value(card,"q7HistoryPool"),ordinal=value(card,"q7HistoryOrdinal");LocalResourceEngine.Result seeded=new LocalResourceEngine.Result(baseline);
                LocalDrawEngine.saveState(seeded,BsonLite.document(new Object[]{"ct",ordinal-1,"iof",true}),t);
                // Direct adapter does not save an incomplete fixture group.
                byte[] actual=HistoryDrawPolicy.reveal(seeded,catalog,card);check(BsonLite.boolValue(actual,"is_open"),"actual original adapter "+leaf.kind);covered.add(leaf.kind);
            }
            boolean designVerified=false;for(HistoryCatalog.Leaf leaf:graph.leaves.values())if(leaf.design()!=null){byte[] card=force(graph,catalog,leaf.common);if(card==null)continue;LocalResourceEngine.Result r=new LocalResourceEngine.Result(baseline);HistoryDrawPolicy.reveal(r,catalog,card);for(byte[] item:LocalResourceEngine.array(BsonLite.documentValue(BsonLite.documentValue(r.profile,"inv"),"items")))if(value(item,"i")==leaf.id&&Arrays.equals(BsonLite.documentValue(item,"tr"),BsonLite.documentValue(card,"q7Design")))designVerified=true;}
            check(designVerified,"history factory actual design tr preserved by original grant");
            // The sole official money leaf is friendship-family only: test adapter in
            // isolation, never claim its wire131 RPC/factory has been enabled.
            byte[] moneyCard=BsonLite.document(new Object[]{"index",0,"is_open",false,"get_hero",false,"hero",Collections.emptyList(),"hero_file",0,"hero_frag",BsonLite.EMPTY_DOCUMENT,"item",Collections.emptyList(),"treasure",Collections.emptyList(),"q7Kind","money","q7Id",0,"q7Count",10000,"q7Quality",0,"q7Wire",2,"q7HistoryVersion",1,"q7HistoryPool",9990,"q7HistoryHash",HistoryDrawPolicy.SHA256,"q7HistoryPolicy",HistoryDrawPolicy.POLICY,"q7HistoryOrdinalPolicy",HistoryDrawPolicy.ORDINAL_POLICY,"q7HistoryCommonId",3508,"q7HistoryGiftMode",0});
            LocalResourceEngine.Result moneyResult=new LocalResourceEngine.Result(baseline);byte[] moneyOut=HistoryDrawPolicy.reveal(moneyResult,catalog,moneyCard);
            List<byte[]> moneyItems=LocalResourceEngine.array(BsonLite.documentValue(moneyOut,"item"));
            check(value(moneyResult.profile,"money")==11000&&moneyItems.size()==1&&value(moneyItems.get(0),"0")==LocalResourceEngine.currencyItem("money")&&value(moneyItems.get(0),"1")==10000,"standalone original money adapter uses actual mapping and delta");
            check(covered.contains("hero")&&covered.contains("memory")&&covered.contains("treasure")&&covered.contains("item"),"multiple real supported primary kinds");
            System.out.println("HISTORY_ACTUAL_PATCHED_ENGINE_STORE_PASS checks="+checks+" primaryKinds="+covered+" source105Pool=229 inventoryGiftPool="+inventoryPool+"; no ART/render/gameplay claim");
        }finally{remove(root);}
    }
}
