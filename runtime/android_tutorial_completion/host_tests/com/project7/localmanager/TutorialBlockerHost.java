package com.project7.localmanager;
import java.io.*;import java.nio.file.*;import java.lang.reflect.*;import java.util.*;
/** Finite original engine invocation, no gameplay or production implementation. */
public final class TutorialBlockerHost {
 static void check(boolean b,String s){if(!b)throw new AssertionError(s);}
 static LocalTutorialStore.Progress fresh(){LocalTutorialStore.Progress p=LocalTutorialStore.Progress.fresh();p.availableEvents.clear();p.processingEvents.clear();p.completedEvents.clear();p.processingNewbees.clear();p.finishedNewbees.clear();p.initPrologue=false;p.inEmergency=false;return p;}
 static LocalEventEngine engine(File a,LocalTutorialStore.Progress p,byte[]profile)throws Exception{return new LocalEventEngine(new LocalEventCatalog(new FileInputStream(new File(a,"event_graph.tsv"))),new LocalNewbeeCatalog(new FileInputStream(new File(a,"newbee_graph.tsv"))),p,1000,profile);}
 public static void main(String[]args)throws Exception{
 File a=new File(args[0]);byte[]profile=Files.readAllBytes(new File(a,"new_player.bson").toPath());Method complete=LocalEventEngine.class.getDeclaredMethod("complete",int.class,boolean.class);complete.setAccessible(true);
 for(int id:new int[]{1020,1043}){LocalTutorialStore.Progress p=fresh();LocalEventEngine e=engine(a,p,profile);complete.invoke(e,id,false);check(p.completedEvents.contains(id)&&p.processingNewbees.contains(10)&&!p.finishedNewbees.contains(10),"original complete independently starts10: "+id);LocalTutorialStore.Progress restored=LocalTutorialStore.Progress.fromProperties(p.toProperties());restored.processingNewbees.clear();engine(a,restored,profile);check(restored.processingNewbees.contains(10),"constructor restores unfinished tutorial10");check(EventResetWeekPolicy.busy(profile,p)!=null,"actual week reset busy guard sees tutorial10");System.out.println("PASS complete("+id+") -> actual newbee10; original reload restores it");}
 LocalTutorialStore.Progress p=fresh();LocalEventEngine e=engine(a,p,profile);check(!e.beginNewbeeForPanel(93,"card_box"),"93 refuses missing prerequisites");p.finishedNewbees.add(90);p.completedEvents.add(1021);check(!e.beginNewbeeForPanel(93,"city"),"93 enforces original panel");check(e.beginNewbeeForPanel(93,"card_box")&&p.processingNewbees.contains(93),"actual 93 conditional producer");check(!e.beginNewbeeForPanel(93,"card_box"),"duplicate begin not new acceptance");for(int excluded:new int[]{1038,1039,1040}){LocalTutorialStore.Progress q=fresh();q.finishedNewbees.add(90);q.completedEvents.addAll(Arrays.asList(1021,excluded));check(!engine(a,q,profile).beginNewbeeForPanel(93,"card_box"),"original exclusion "+excluded);}
 check(EventResetWeekPolicy.busy(profile,p)!=null,"actual week reset busy guard sees tutorial93");
 // This primitive has no end-condition gate: prove its mechanics, not authorization.
 e.finishNewbees(Collections.singleton(93));check(!p.processingNewbees.contains(93)&&p.finishedNewbees.contains(93),"original finish mutation");System.out.println("PASS actual93 panel/prerequisites/exclusions/duplicate/finish primitive; no card creation/reveal simulated");
 }
}
