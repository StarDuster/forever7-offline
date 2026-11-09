package com.project7.localmanager;
import java.io.*;import java.nio.file.*;import java.util.*;
/** Pure reducer/store evidence with real original BSON and stock writer. No game. */
public final class DreamStateHost {
 static void check(boolean value,String message){if(!value)throw new AssertionError(message);}
 static byte[]base(){return BsonLite.document("account","dream_synthetic","opaque","keep","money",19,"cgs",Arrays.asList(281),"std",BsonLite.document("rt","20","ff",false,"fd",3,"unknown","preserve"));}
 static int budget(byte[]p){return BsonLite.intValue(BsonLite.documentValue(p,"std"),"hst");}
 public static void main(String[]args)throws Exception{
  DreamCatalog catalog=DreamCatalog.fromBytes(Files.readAllBytes(Paths.get(args[0])));DreamState.Scope scope=new DreamState.Scope("host_week_commit",3,"20",0);
  check(catalog.plans().size()==7,"original source rows");check(catalog.lookup("20-1",0).event==catalog.lookup("20",0).event,"exact/base lookup");
  check(!catalog.lookup("35",6).hasEvents(),"route35 zero entry isolated");check(catalog.rules().stream().filter(rule->rule.dreamSentinel).count()==47,"exact sentinel source");
  check(catalog.rule(catalog.lookup("20",0).event).conditions().get(1)==null,"day0 entry has no condition1; not fabricated");
  byte[]input=BsonLite.withProfileDocument(base(),"weeknum",BsonLite.document("w",3,"d",0));DreamState.Change entered=DreamState.enterAuthorized(input,catalog,scope);check(entered.reason==DreamState.Reason.ENTERED&&budget(entered.profile)==0,"mode activation not event completion");
  check(DreamState.enterAuthorized(entered.profile,catalog,scope).profile==entered.profile,"entry retry preserves budget/state reference");
  check(DreamState.canPatrol(entered.profile,catalog,scope).reason==DreamState.Reason.PATROL_ALLOWED,"entry event completion is not patrol precondition");
  LocalTutorialStore.Progress progress=LocalTutorialStore.Progress.fresh();progress.weekIndex=3;progress.initPrologue=false;progress.completedEvents.add(1047);progress.availableEvents.clear();progress.processingEvents.clear();progress.inEmergency=false;
  LocalEventCatalog graph=new LocalEventCatalog(new FileInputStream(args[1]));LocalNewbeeCatalog newbees=new LocalNewbeeCatalog(new ByteArrayInputStream(new byte[0]));
  LocalEventEngine originalEngine=new LocalEventEngine(graph,newbees,progress,0,entered.profile,false);
  List<Integer>stock=originalEngine.patrolEvents(1,Collections.<Integer>emptyList(),null);List<Integer>dream=DreamPatrolCandidates.eligible(originalEngine,null,catalog,1,Collections.<Integer>emptyList());
  check(stock.containsAll(dream),"no condition bypass or synthesized candidate");for(Integer event:dream)check(catalog.rule(event).dreamSentinel&&catalog.rule(event).hasCondition,"exact source sentinel plus actual rule");

  // Synthetic genuine original facts, not forced production completions.
  progress.completedEvents.addAll(Arrays.asList(1258,1043,1013));progress.eventConditions.put("battle",new LinkedHashSet<>(Arrays.asList(3106)));DreamAccess.invalidate(originalEngine);
  check(DreamPatrolCandidates.eligible(originalEngine,null,catalog,4,Collections.<Integer>emptyList()).equals(Arrays.asList(1262)),"nonempty original trigger: completed entry, battle-owned area state, route/date source conditions");

  byte[]p=entered.profile;
  for(int i=0;i<3;i++){DreamState.Change accepted=DreamState.recordAcceptedPatrol(p,catalog,scope,"coordinator_commit_"+i);check(accepted.reason==DreamState.Reason.PATROL_APPLIED&&budget(accepted.profile)==i+1,"accepted patrol increments exactly once");p=accepted.profile;}
  check(DreamState.recordAcceptedPatrol(p,catalog,scope,"coordinator_commit_0").reason==DreamState.Reason.PATROL_RETRY&&budget(p)==3,"nonlatest retry deduplicated");
  check(DreamState.recordAcceptedPatrol(p,catalog,scope,"fourth").profile==p,"fourth refused unchanged");
  int night=catalog.lookup(scope.route,scope.day).night;check(DreamState.exitAfterNight(p,catalog,scope,Collections.<Integer>emptySet(),Collections.<Integer>emptySet()).reason==DreamState.Reason.NIGHT_PENDING,"no fake night");
  // These collections are pure policy input facts, NOT evidence that original
  // dialogs/night runner has been executed; coordinator proof is separate.
  DreamState.Change left=DreamState.exitAfterNight(p,catalog,scope,Collections.singleton(night),Collections.<Integer>emptySet());check(left.reason==DreamState.Reason.EXITED&&budget(left.profile)==0,"exit projection");
  check(DreamState.enterAuthorized(left.profile,catalog,scope).reason==DreamState.Reason.LEFT,"same-day tombstone");
  check(BsonLite.intValue(left.profile,"money")==19&&"keep".equals(BsonLite.stringValue(left.profile,"opaque"))&&Integer.valueOf(3).equals(BsonLite.intValue(BsonLite.documentValue(left.profile,"std"),"fd")),"no whole-profile rollback, route35 fields retained");
  DreamState.Scope tomorrow=new DreamState.Scope(scope.weekCommit,3,"20",1);DreamState.Change reset=DreamState.afterCalendarCommit(left.profile,tomorrow);check(reset.reason==DreamState.Reason.CALENDAR_CLEARED&&BsonLite.documentValue(reset.profile,DreamState.CONTEXT)==null,"committed day reset");
  check(DreamState.enterAuthorized(reset.profile,catalog,tomorrow).reason==DreamState.Reason.ENTERED,"new day budget may begin");
  byte[]legacy=BsonLite.withProfileDocument(input,"std",BsonLite.document("rt","20","hsf",true,"hst",1));check(DreamState.enterAuthorized(legacy,catalog,scope).reason==DreamState.Reason.LEGACY_UNSCOPED,"do not replenish legacy unscoped mode");
  Path temp=Files.createTempDirectory("p7-dream-stock-store-");Files.createDirectory(temp.resolve("profiles"));Path file=temp.resolve("profiles/dream_synthetic.bson");Files.write(file,p);
  // Real original atomic writer; platform Os.rename is the only filesystem seam.
  java.lang.reflect.Method write=LocalProfileStore.class.getDeclaredMethod("writeAtomic",File.class,byte[].class);write.setAccessible(true);write.invoke(null,file.toFile(),p);byte[]loaded=Files.readAllBytes(file);
  check(DreamState.recordAcceptedPatrol(loaded,catalog,scope,"coordinator_commit_0").reason==DreamState.Reason.PATROL_RETRY&&budget(loaded)==3,"receipt/budget survives original BSON store");
  byte[]projection=DreamState.huiSuProjection(loaded);check(Boolean.TRUE.equals(BsonLite.boolValue(projection,"hsf"))&&BsonLite.intValue(projection,"hst")==3,"typed source std projection");
  Files.delete(file);Files.delete(temp.resolve("profiles"));Files.delete(temp);
  System.out.println("PASS DreamCatalog fixed source + pure BSON budget/receipts/tombstone/calendar reducer + original writeAtomic reload; runner/coordinator not yet wired");
 }
}
