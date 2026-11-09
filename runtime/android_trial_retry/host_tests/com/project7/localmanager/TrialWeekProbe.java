package com.project7.localmanager;
import android.content.*;import android.content.res.*;import java.io.*;import java.nio.file.*;import java.util.*;
/** Actual accepted original Week RPC across real terminal-ACK receipt; no manual scope mutation. */
public final class TrialWeekProbe {
 public static void main(String[]args)throws Exception{File assets=new File(args[0]);boolean fixed=Boolean.parseBoolean(args[1]);Context c=new Context(assets,new AssetManager(assets));CoreDrawPolicy.prepare(c);HistoryDrawPolicy.prepare(c);SelectorPolicy.prepare(c);OfflineMechanismGateway.prepare(c);StoryMissionBridge.prepare(c);TrialRetryGateway.prepare(c);
  try(TrialRetryHost.Fixture f=new TrialRetryHost.Fixture(assets,7144)){
   byte[]raw=f.d.read(),inv=TrialRetryHost.doc(raw,"inv");List<byte[]>items=new ArrayList<>(LocalResourceEngine.array(TrialRetryHost.doc(inv,"items")));items.add(BsonLite.document("i",345,"w",1,"u",new BsonLite.UuidValue(LocalResourceEngine.uuid())));Files.write(f.d.file,BsonLite.withProfileDocument(raw,"inv",BsonLite.withProfileArray(inv,"items",items)));
   f.begin(315,14);f.finish(315,14,0);f.begin(315,14);f.finish(315,14,0);f.begin(315,14);
   android.system.Os.afterRename=name->{if(name.endsWith(StoryMissionStoreHost.ACCOUNT+".bson")){android.system.Os.afterRename=null;android.system.Os.failBefore=true;}};
   try{f.finish(315,14,0);throw new AssertionError("terminal ACK must fail");}catch(IOException expected){}
   TrialRetryHost.check(BsonLite.documentValue(f.d.read(),"q7TrialRetryPending")!=null,"real terminal pending retained");
   LocalTutorialStore.Progress loaded=f.d.tutorials.load(StoryMissionStoreHost.ACCOUNT);String old=loaded.weekCommit;
   LocalEventEngine engine=new LocalEventEngine((LocalEventCatalog)DreamAccess.get(f.d.engine,"catalog"),(LocalNewbeeCatalog)DreamAccess.get(f.d.engine,"newbeeCatalog"),loaded,0,f.d.read(),true);
   if(fixed){byte[]pendingImage=f.d.read();try{TrialRetryGateway.beforeScopeChange(f.d.g,StoryMissionStoreHost.ACCOUNT,loaded,null);throw new AssertionError("null engine scope change blocked");}catch(IOException expected){}TrialRetryHost.check(Arrays.equals(pendingImage,f.d.read())&&old.equals(loaded.weekCommit),"missing engine cannot skip pending scope guard");
    android.system.Os.failBefore=true;ByteArrayOutputStream rejected=new ByteArrayOutputStream();try{StoryMissionStoreHost.call(f.d.g,"handleWeekRpc",new Class<?>[]{OutputStream.class,byte[].class,byte[].class,byte[].class,String.class,LocalTutorialStore.Progress.class,LocalEventEngine.class},rejected,TrialRetryHost.EID,java.security.MessageDigest.getInstance("MD5").digest("handleResetWeekAsk".getBytes("UTF-8")),BsonLite.EMPTY_DOCUMENT,StoryMissionStoreHost.ACCOUNT,loaded,engine);throw new AssertionError("pending ACK fault must block week");}catch(IOException expected){}TrialRetryHost.check(old.equals(loaded.weekCommit)&&BsonLite.documentValue(f.d.read(),"q7TrialRetryPending")!=null&&rejected.size()==0,"actual Week RPC ACK recovery failure blocks before scope commit/publication");System.out.println("PASS actual Week recovery fault and missing-engine gate preserve scope/receipt");}
   ByteArrayOutputStream out=new ByteArrayOutputStream();StoryMissionStoreHost.call(f.d.g,"handleWeekRpc",new Class<?>[]{OutputStream.class,byte[].class,byte[].class,byte[].class,String.class,LocalTutorialStore.Progress.class,LocalEventEngine.class},out,TrialRetryHost.EID,java.security.MessageDigest.getInstance("MD5").digest("handleResetWeekAsk".getBytes("UTF-8")),BsonLite.EMPTY_DOCUMENT,StoryMissionStoreHost.ACCOUNT,loaded,engine);
   List<ProtoLite.EntityMessage>frames=StoryMissionStoreHost.frames(out.toByteArray());boolean accepted=TrialRetryHost.has(frames,"handleResetWeekReply");System.out.println("WEEK accepted="+accepted+" old="+old+" current="+loaded.weekCommit+" pending="+(BsonLite.documentValue(f.d.read(),"q7TrialRetryPending")!=null)+" processing="+loaded.processingEvents);
   for(ProtoLite.EntityMessage m:frames)if(Arrays.equals(m.methodMd5,java.security.MessageDigest.getInstance("MD5").digest("showMessageStr".getBytes("UTF-8"))))System.out.println(BsonLite.messagePackValue(m.parameters,false));
   if(!fixed){
    TrialRetryHost.check(!accepted&&old.equals(loaded.weekCommit)&&BsonLite.documentValue(f.d.read(),"q7TrialRetryPending")!=null,"baseline real pending scenario original processing gate rejects scope transition");System.out.println("PASS baseline real terminal ACK pending cannot cross tested Ask gate; cross-week P1 not reproduced");
    TrialRetryGateway.recover(f.d.g,StoryMissionStoreHost.ACCOUNT,loaded,engine);
    StoryMissionStoreHost.call(f.d.g,"syncEventEffects",new Class<?>[]{OutputStream.class,byte[].class,String.class,LocalTutorialStore.Progress.class,LocalEventEngine.class},new ByteArrayOutputStream(),TrialRetryHost.EID,StoryMissionStoreHost.ACCOUNT,loaded,engine);
    f.d.tutorials.save(StoryMissionStoreHost.ACCOUNT,loaded);out.reset();
    StoryMissionStoreHost.call(f.d.g,"handleWeekRpc",new Class<?>[]{OutputStream.class,byte[].class,byte[].class,byte[].class,String.class,LocalTutorialStore.Progress.class,LocalEventEngine.class},out,TrialRetryHost.EID,java.security.MessageDigest.getInstance("MD5").digest("handleResetWeekAsk".getBytes("UTF-8")),BsonLite.EMPTY_DOCUMENT,StoryMissionStoreHost.ACCOUNT,loaded,engine);
    frames=StoryMissionStoreHost.frames(out.toByteArray());accepted=TrialRetryHost.has(frames,"handleResetWeekReply");
   }
   TrialRetryHost.check(accepted&&!old.equals(loaded.weekCommit)&&BsonLite.documentValue(f.d.read(),"q7TrialRetryPending")==null,"original accepted Ask new scope only after pending recovery");
   System.out.println("PASS actual accepted Week RPC new scope; receipt recovered/acknowledged before commit");
   byte[]before=f.d.read();ByteArrayOutputStream replay=new ByteArrayOutputStream();try{TrialRetryHost.finishCall(f,replay,BsonLite.document("t",2,"s",315,"w",1),loaded,engine);throw new AssertionError("old result must reconnect");}catch(IOException expected){}TrialRetryHost.check(!TrialRetryHost.has(StoryMissionStoreHost.frames(replay.toByteArray()),"combatOfflineReward")&&Arrays.equals(before,f.d.read()),"old terminal outcome cannot publish into accepted new scope");System.out.println("PASS original accepted scope transition after closure; old terminal replay emits no w0/completion");
  }
 }
}
