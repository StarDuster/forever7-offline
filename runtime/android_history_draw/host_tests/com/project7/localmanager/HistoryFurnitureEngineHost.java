package com.project7.localmanager;
import android.content.Context;
import android.content.res.AssetManager;
import android.system.Os;
import java.io.*;
import java.nio.file.*;
import java.util.*;
/** Finite original HomeEngine/Store tests, synthetic profile and fixed public source graph. */
public final class HistoryFurnitureEngineHost {
    static int checks;
    static void check(boolean ok,String why){if(!ok)throw new AssertionError(why);checks++;}
    static int v(byte[] d,String k){Integer n=BsonLite.intValue(d,k);return n==null?0:n;}
    static LocalResourceEngine.Reply reply(LocalResourceEngine.Result r,String method){return HistoryEngineHost.reply(r,method);}
    static LocalResourceEngine.Result request(LocalProfileStore store,String method,byte[] args)throws Exception{return store.updateServices("furniture_host",method,args,LocalTutorialStore.Progress.fresh());}
    static byte[] seed(){return BsonLite.withProfileInt(HistoryEngineHost.seed(),"level",110);}
    static int skins(byte[] profile,int hero){byte[] d=BsonLite.documentValue(BsonLite.profileHeroDocument(profile,hero),"sk");return d==null?0:BsonLite.keys(d).size();}
    static final class Target {int t,outer,inner;HistoryBson.Value grant;}
    static Target target(byte[] asset,String kind)throws Exception{
        for(String line:new String(asset,"US-ASCII").split("\n")){
            if(!line.startsWith("F\t"))continue;String[] cells=line.split("\t");HistoryBson.Value spec=HistoryBson.parse(Base64.getDecoder().decode(cells[2]));if(!spec.get("enabled").bool())continue;int outer=0;
            for(HistoryBson.Value row:spec.get("base").values()){int inner=0;for(HistoryBson.Value option:row.get("options").values()){
                for(HistoryBson.Value g:option.get("g").values())if((kind.equals("skin")&&HistoryBson.integer(g,"skin")>0)||(kind.equals("pendant")&&!g.get("pendant").fields.isEmpty())){Target result=new Target();result.t=Integer.parseInt(cells[1]);result.outer=outer;result.inner=inner;result.grant=g;return result;}
                inner+=HistoryBson.integer(option,"w");}outer+=HistoryBson.integer(row,"w");}
        }throw new AssertionError("fixed family lacks "+kind);
    }
    static Random exact(Target t){return new Random(){int n;public int nextInt(int bound){int x=(n++%2==0)?t.outer:t.inner;if(x<0||x>=bound)throw new AssertionError("selector boundary");return x;}};}
    public static void main(String[] args)throws Exception{
        Path root=Files.createTempDirectory("history-furniture-synthetic-");
        try{
            Context context=new Context(root.toFile(),new AssetManager(new File(args[0]),new File(args[1]),new File(args[2]),new File(args[3]),new File(args[4])));
            CoreDrawPolicy.prepare(context);HistoryDrawPolicy.prepare(context);HistoryFurniturePolicy.prepare(context);
            LocalResourceCatalog catalog;try(InputStream in=new FileInputStream(args[1])){catalog=new LocalResourceCatalog(in);}LocalFeatureCatalog home;try(InputStream in=new FileInputStream(new File(args[0],"home.tsv"))){home=new LocalFeatureCatalog(in);}
            byte[] asset=Files.readAllBytes(Paths.get(args[4]));Target skin=target(asset,"skin"),pendant=target(asset,"pendant");
            for(String kind:Arrays.asList("skin","pendant")){
                Target t=kind.equals("skin")?skin:pendant;int hero=kind.equals("skin")?catalog.skins.get(HistoryBson.integer(t.grant,"skin")).hero:HistoryBson.integer(t.grant.get("pendant"),"0");LocalResourceEngine.Result base=new LocalResourceEngine.Result(seed());LocalResourceEngine.grant(base,catalog,"hero",hero,1,1);
                if(kind.equals("skin"))for(int skinId:catalog.skins.keySet())LocalResourceEngine.grant(base,catalog,"skin",skinId,1,1);
                byte[] initial=BsonLite.document(new Object[]{"ct",1000,"cctd",0});base.profile=HistoryEngineHost.withState(base.profile,t.t,initial);
                int before=skins(base.profile,hero);byte[] oldSk=BsonLite.documentValue(BsonLite.profileHeroDocument(base.profile,hero),"sk");LocalResourceEngine.Result first=LocalHomeEngine.apply(base.profile,home,catalog,"requestLuckyDrawFurnitureCard",BsonLite.document(new Object[]{"t",t.t}),LocalStoryEnvironment.now(),exact(t));
                check(Boolean.TRUE.equals(BsonLite.boolValue(reply(first,"replyLuckyDrawFurnitureCard").parameters,"rs")),"real Home "+kind+" request succeeds");
                if(kind.equals("skin"))check(skins(first.profile,hero)==before+1,"delivery uses real original skinCopies for already-owned skin");
                else check(BsonLite.intArrayValues(BsonLite.profileHeroDocument(first.profile,hero),"pa").contains(HistoryBson.integer(t.grant.get("pendant"),"1")),"original pendant owned state pa");
                byte[] firstReward=BsonLite.documentValue(BsonLite.documentValue(reply(first,"replyLuckyDrawFurnitureCard").parameters,"i"),"rwd");
                if(kind.equals("skin"))check(BsonLite.documentValue(firstReward,"skin")!=null,"actual rtype2 source skin primary projection");
                check(BsonLite.documentValue(firstReward,"activityReward")==null&&BsonLite.documentValue(firstReward,"other_reward")==null,"furniture single primary queue");
                System.out.println("HISTORY_FURNITURE_FIXTURE "+kind+"_first "+Base64.getEncoder().encodeToString(reply(first,"replyLuckyDrawFurnitureCard").parameters));
                LocalResourceEngine.Result second=LocalHomeEngine.apply(first.profile,home,catalog,"requestLuckyDrawFurnitureCard",BsonLite.document(new Object[]{"t",t.t}),LocalStoryEnvironment.now(),exact(t));reply(second,"replyLuckyDrawFurnitureCard");
                if(kind.equals("skin")){check(skins(second.profile,hero)==before+2,"second delivery retains distinct wardrobe copy after all494 owned/pending baseline");byte[] newSk=BsonLite.documentValue(BsonLite.profileHeroDocument(second.profile,hero),"sk");for(String uuid:BsonLite.keys(oldSk))check(Arrays.equals(BsonLite.documentValue(oldSk,uuid),BsonLite.documentValue(newSk,uuid)),"existing skin UUID and full document preserved");}
                else for(HistoryBson.Value trans:t.grant.get("trans").values())check(HistoryEngineHost.inventory(second.profile,HistoryBson.integer(trans,"0"))-HistoryEngineHost.inventory(first.profile,HistoryBson.integer(trans,"0"))==HistoryBson.integer(trans,"1"),"duplicate pendant original conversion exact");
                byte[] repeatReward=BsonLite.documentValue(BsonLite.documentValue(reply(second,"replyLuckyDrawFurnitureCard").parameters,"i"),"rwd");
                if(kind.equals("pendant"))check(BsonLite.documentValue(repeatReward,"pendantExchange")!=null,"actual duplicate pendant primary exchange projection");
                System.out.println("HISTORY_FURNITURE_FIXTURE "+kind+"_repeat "+Base64.getEncoder().encodeToString(reply(second,"replyLuckyDrawFurnitureCard").parameters));
            }
            // Missing-hero pending branch receives only original now for new copies.
            int pendingHero=catalog.skins.get(HistoryBson.integer(skin.grant,"skin")).hero;String heroKey=Integer.toString(pendingHero);long pendingNow=LocalStoryEnvironment.now();
            byte[] pendingBase=HistoryEngineHost.withState(seed(),skin.t,BsonLite.document(new Object[]{"ct",1000}));
            LocalResourceEngine.Result pending=LocalHomeEngine.apply(pendingBase,home,catalog,"requestLuckyDrawFurnitureCard",BsonLite.document(new Object[]{"t",skin.t}),pendingNow,exact(skin));
            check(Boolean.TRUE.equals(BsonLite.boolValue(reply(pending,"replyLuckyDrawFurnitureCard").parameters,"rs")),"original pending skin copy succeeds");
            byte[] hm=BsonLite.documentValue(pending.profile,"heromgr"),ps=BsonLite.documentValue(hm,"ps"),psc=BsonLite.documentValue(hm,"psc");
            check(BsonLite.intArrayValues(ps,heroKey).size()==1&&BsonLite.intArrayValues(psc,heroKey).equals(Arrays.asList(Math.toIntExact(pendingNow/1000))),"new pending skin exact original timestamp");
            int syncs=0;for(LocalResourceEngine.Reply q:pending.replies)if(q.method.equals("syncHeroMgrPendingData")){byte[] body=BsonLite.documentValue(q.parameters,"d");check(BsonLite.intArrayValues(BsonLite.documentValue(body,"ps"),heroKey).size()==BsonLite.intArrayValues(BsonLite.documentValue(body,"psc"),heroKey).size(),"first emitted pending payload already has matching times");syncs++;}check(syncs==1,"one original pending sync, no extra queue");
            LocalResourceEngine.Result pendingAgain=LocalHomeEngine.apply(pending.profile,home,catalog,"requestLuckyDrawFurnitureCard",BsonLite.document(new Object[]{"t",skin.t}),pendingNow+1000,exact(skin));reply(pendingAgain,"replyLuckyDrawFurnitureCard");
            check(BsonLite.intArrayValues(BsonLite.documentValue(BsonLite.documentValue(pendingAgain.profile,"heromgr"),"psc"),heroKey).equals(Arrays.asList(Math.toIntExact(pendingNow/1000),Math.toIntExact(pendingNow/1000)+1)),"existing time preserved, only new delta timestamp appended");
            byte[] malformed=BsonLite.withProfileDocument(pending.profile,"heromgr",BsonLite.withProfileDocument(hm,"psc",BsonLite.withProfileArray(psc,heroKey,Collections.emptyList())));
            LocalResourceEngine.Result rejected=LocalHomeEngine.apply(malformed,home,catalog,"requestLuckyDrawFurnitureCard",BsonLite.document(new Object[]{"t",skin.t}),pendingNow,exact(skin));
            check(Boolean.FALSE.equals(BsonLite.boolValue(reply(rejected,"replyLuckyDrawFurnitureCard").parameters,"rs"))&&Arrays.equals(BsonLite.documentValue(BsonLite.documentValue(rejected.profile,"heromgr"),"ps"),ps),"old missing timestamp typed rejection without invented dates or new grant");
            System.out.println("HISTORY_FURNITURE_PENDING "+Base64.getEncoder().encodeToString(BsonLite.documentValue(pendingAgain.profile,"heromgr")));
            // Actual unmodified Store owner: no injected RNG or replacement save path.
            Path dir=root.resolve("profiles");Files.createDirectories(dir);Path file=dir.resolve("furniture_host.bson");Files.write(file,seed());LocalProfileStore store=new LocalProfileStore(context);int before=Os.renames;
            LocalResourceEngine.Result single=request(store,"requestLuckyDrawFurnitureCard",BsonLite.document(new Object[]{"t",skin.t}));if(!Boolean.TRUE.equals(BsonLite.boolValue(reply(single,"replyLuckyDrawFurnitureCard").parameters,"rs")))for(LocalResourceEngine.Reply q:single.replies)if(q.method.equals("showMessageStr"))System.out.println("FURNITURE_FAILURE_DIAGNOSTIC "+BsonLite.stringValue(q.parameters,"m"));check(Boolean.TRUE.equals(BsonLite.boolValue(reply(single,"replyLuckyDrawFurnitureCard").parameters,"rs")),"actual Store furniture single");check(Os.renames==before+1&&Arrays.equals(Files.readAllBytes(file),single.profile),"single original atomic commit");
            LocalResourceEngine.Result ten=request(new LocalProfileStore(context),"requestLuckyDrawFurnitureLianchouCard",BsonLite.document(new Object[]{"t",skin.t}));check(Boolean.TRUE.equals(BsonLite.boolValue(reply(ten,"replyLuckyDrawFurnitureLianchouCard").parameters,"rs")),"actual Store ten/relogin");
            byte[] scopeBefore=LocalDrawEngine.state(ten.profile,skin.t);
            LocalResourceEngine.Result different=request(store,"requestLuckyDrawFurnitureCard",BsonLite.document(new Object[]{"t",384}));
            check(Boolean.TRUE.equals(BsonLite.boolValue(reply(different,"replyLuckyDrawFurnitureCard").parameters,"rs"))&&Arrays.equals(scopeBefore,LocalDrawEngine.state(different.profile,skin.t)),"actual native384 family and per-t state isolation");
            check(HistoryEngineHost.inventory(different.profile,10051)==0&&HistoryEngineHost.inventory(different.profile,11491)==0&&v(different.profile,"summonCoin")==1000,"history free scope does not fake or consume tickets/currency");
            byte[] legacySeed=seed();LocalResourceEngine.Result funded=new LocalResourceEngine.Result(legacySeed);LocalResourceEngine.grant(funded,catalog,"item",10225,1000,1);Files.write(file,funded.profile);
            LocalResourceEngine.Result legacy=request(store,"requestLuckyDrawFurnitureCard",BsonLite.document(new Object[]{"t",162}));check(Boolean.TRUE.equals(BsonLite.boolValue(reply(legacy,"replyLuckyDrawFurnitureCard").parameters,"rs"))&&HistoryEngineHost.inventory(legacy.profile,10225)==990,"legacy162 original ten-unit fee");
            LocalResourceEngine.Result legacyTen=request(store,"requestLuckyDrawFurnitureLianchouCard",BsonLite.document(new Object[]{"t",162}));check(Boolean.TRUE.equals(BsonLite.boolValue(reply(legacyTen,"replyLuckyDrawFurnitureLianchouCard").parameters,"rs"))&&HistoryEngineHost.inventory(legacyTen.profile,10225)==940,"legacy162 first ten original fifty-unit discounted fee");
            byte[] limitedState=BsonLite.withProfileInt(LocalDrawEngine.state(different.profile,skin.t),"cctd",500);byte[] limited=HistoryEngineHost.withState(different.profile,skin.t,limitedState);Files.write(file,limited);
            LocalResourceEngine.Result capped=request(store,"requestLuckyDrawFurnitureCard",BsonLite.document(new Object[]{"t",skin.t}));check(Boolean.FALSE.equals(BsonLite.boolValue(reply(capped,"replyLuckyDrawFurnitureCard").parameters,"rs"))&&v(LocalDrawEngine.state(capped.profile,skin.t),"ct")==v(limitedState,"ct"),"original five-hundred daily cap retained without new grant");
            byte[] yesterday=HistoryEngineHost.withState(limited,skin.t,BsonLite.withProfileString(limitedState,"q7DrawDay","2000-01-01"));Files.write(file,yesterday);
            LocalResourceEngine.Result rolled=request(store,"requestLuckyDrawFurnitureCard",BsonLite.document(new Object[]{"t",skin.t}));check(Boolean.TRUE.equals(BsonLite.boolValue(reply(rolled,"replyLuckyDrawFurnitureCard").parameters,"rs"))&&v(LocalDrawEngine.state(rolled.profile,skin.t),"cctd")==1,"native day rollover resets daily cap without global clock change");
            Files.write(file,different.profile);
            byte[] committed=Files.readAllBytes(file);Os.failNextRename=true;boolean failed=false;
            try{request(store,"requestLuckyDrawFurnitureCard",BsonLite.document(new Object[]{"t",skin.t}));}catch(Exception expected){failed=true;}
            check(failed&&Arrays.equals(committed,Files.readAllBytes(file)),"original furniture atomic failure preserves committed profile");
            LocalResourceEngine.Result failureSingle=request(store,"requestLuckyDrawFurnitureCard",BsonLite.document(new Object[]{"t",987654}));
            LocalResourceEngine.Result failureTen=request(store,"requestLuckyDrawFurnitureLianchouCard",BsonLite.document(new Object[]{"t",987654}));
            check(Boolean.FALSE.equals(BsonLite.boolValue(reply(failureSingle,"replyLuckyDrawFurnitureCard").parameters,"rs"))&&Boolean.FALSE.equals(BsonLite.boolValue(reply(failureTen,"replyLuckyDrawFurnitureLianchouCard").parameters,"rs")),"unknown furniture retains original typed failures");
            Thread.currentThread().interrupt();LocalResourceEngine.Result cancelled;
            try{cancelled=LocalHomeEngine.apply(seed(),home,catalog,"requestLuckyDrawFurnitureCard",BsonLite.document(new Object[]{"t",skin.t}),LocalStoryEnvironment.now(),exact(skin));}finally{Thread.interrupted();}
            check(Boolean.FALSE.equals(BsonLite.boolValue(reply(cancelled,"replyLuckyDrawFurnitureCard").parameters,"rs")),"cancelled selection preserves original failure");
            System.out.println("HISTORY_FURNITURE_FIXTURE failure_single "+Base64.getEncoder().encodeToString(reply(failureSingle,"replyLuckyDrawFurnitureCard").parameters));
            System.out.println("HISTORY_FURNITURE_FIXTURE failure_ten "+Base64.getEncoder().encodeToString(reply(failureTen,"replyLuckyDrawFurnitureLianchouCard").parameters));
            System.out.println("HISTORY_FURNITURE_FIXTURE single "+Base64.getEncoder().encodeToString(reply(single,"replyLuckyDrawFurnitureCard").parameters));
            System.out.println("HISTORY_FURNITURE_FIXTURE ten "+Base64.getEncoder().encodeToString(reply(ten,"replyLuckyDrawFurnitureLianchouCard").parameters));
            System.out.println("HISTORY_FURNITURE_ORIGINAL_ENGINE_PASS checks="+checks+" skinPool="+skin.t+" pendantPool="+pendant.t+"; no renderer/ART/game acceptance");
        }finally{try(java.util.stream.Stream<Path> walk=Files.walk(root)){for(Path p:(Iterable<Path>)walk.sorted(Comparator.reverseOrder())::iterator)Files.deleteIfExists(p);}}
    }
}
