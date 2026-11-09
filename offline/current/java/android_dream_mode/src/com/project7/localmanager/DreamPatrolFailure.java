package com.project7.localmanager;
import java.io.*;import java.util.*;
/** Definite precommit classification only. Both authoritative files and live
 * Progress must exactly match the pre-call images while holding original locks. */
final class DreamPatrolFailure {
 interface Attempt<T>{T run()throws IOException;}
 static final class NotCommitted extends IOException {NotCommitted(IOException cause){super("Dream patrol not committed",cause);}}
 static <T>T checked(LocalGatewayServer gateway,String account,LocalTutorialStore.Progress p,LocalEventEngine e,Attempt<T> attempt)throws IOException{
  synchronized(e){return DreamStorage.locked(gateway,account,tx->{
   byte[]before=tx.read();Properties liveBefore=DreamProgressDelta.props(p),diskBefore=disk(gateway,account,p);
   try{return attempt.run();}catch(IOException failure){
    try{
     byte[]after=tx.read();Properties diskAfter=disk(gateway,account,p);
     if(Arrays.equals(before,after)&&BsonLite.documentValue(after,"q7DreamPatrolCommit")==null&&liveBefore.equals(DreamProgressDelta.props(p))&&diskBefore.equals(diskAfter))throw new NotCommitted(failure);
    }catch(NotCommitted definite){throw definite;}catch(IOException unknown){failure.addSuppressed(unknown);}
    throw failure;
   }
  });}
 }
 private static Properties disk(LocalGatewayServer g,String account,Object p)throws IOException{
  Object store=DreamAccess.get(g,"tutorialStore"),loaded=DreamAccess.call(store,"load",new Class<?>[]{String.class},account);return DreamProgressDelta.props(loaded);
 }
}
