package com.project7.localmanager;
import java.io.*;import java.lang.reflect.*;import java.nio.charset.StandardCharsets;import java.security.*;
/** Matched Week-method seam. Real original effects/ACK must finish before a
 * reset may discard old Progress. No effects interpreter or reward grant here. */
public final class EventResetWeekGateway {
 private EventResetWeekGateway(){}
 private static boolean scopeChange(String method){return "handleIncWeekAsk".equals(method)||"handleResetWeekAsk".equals(method)||"requestEnterStory".equals(method)||"requestEnterStoryByEnding".equals(method);}

 /** true: continue original Week.updateServices; false: message consumed request. */
 public static boolean beforeWeek(LocalGatewayServer g,OutputStream out,byte[]eid,String account,LocalTutorialStore.Progress p,LocalEventEngine engine,String method)throws IOException{
  boolean eventReset=EventResetWeekPolicy.REQUEST.equals(method);
  if(account==null||p==null)return eventReset?deny(g,out,eid,"当前周目状态尚未就绪。"):true;
  if(Boolean.TRUE.equals(callStatic("LocalAccountStore","isTemplateAccount",new Class<?>[]{String.class},account)))return eventReset?deny(g,out,eid,"预览账号为只读模式。"):true;
  boolean scopeChange=eventReset||scopeChange(method);
  TrialRetryGateway.beforeScopeChange(g,account,p,engine);
  if(engine==null){
   if(eventReset)return deny(g,out,eid,"当前剧情引擎尚未就绪，请重新连接后重试。");
   byte[]profile=(byte[])call(field(g,"profileProvider"),"snapshot",new Class<?>[]{String.class,p.getClass()},account,p);
   Object flag=((ThreadLocal<?>)field(g,"storyClosureIncomplete")).get();
   byte[]pending=BsonLite.documentValue(profile,"q7StoryPending");
   if(scopeChange&&Boolean.TRUE.equals(flag))return deny(g,out,eid,"剧情结果尚未同步完成，请稍后重试。");
   if(scopeChange&&pending!=null&&!BsonLite.keys(pending).isEmpty())return deny(g,out,eid,"剧情结果尚待投递，请稍后重试。");
   if(BsonLite.documentValue(profile,"q7DreamPatrolCommit")!=null)return deny(g,out,eid,"请先恢复当前巡查请求，再切换周目。");
   return true;
  }
  DreamCoordinator.recover(g,account,p,engine);
  if(!eventReset){
   if(!scopeChange)return true;
   byte[]profile=(byte[])call(field(g,"profileProvider"),"snapshot",new Class<?>[]{String.class,p.getClass()},account,p);
   Object flag=((ThreadLocal<?>)field(g,"storyClosureIncomplete")).get();
   byte[]pending=BsonLite.documentValue(profile,"q7StoryPending");
   if(Boolean.TRUE.equals(flag))return deny(g,out,eid,"剧情结果尚未同步完成，请稍后重试。");
   if(pending!=null&&!BsonLite.keys(pending).isEmpty())return deny(g,out,eid,"剧情结果尚待投递，请稍后重试。");
   return true;
  }
  synchronized(engine){
   byte[]profile;
   try{
    call(g,"syncEventEffects",new Class<?>[]{OutputStream.class,byte[].class,String.class,p.getClass(),engine.getClass()},out,eid,account,p,engine);
    profile=(byte[])call(field(g,"profileProvider"),"snapshot",new Class<?>[]{String.class,p.getClass()},account,p);
   }catch(IOException failure){
    // Never reset after publication/write ambiguity; retain actual old-scope
    // facts derived by the original closure for owner-ledger reconciliation.
    try{save(g,account,p);}catch(IOException saveFailure){failure.addSuppressed(saveFailure);}
    throw failure;
   }
   save(g,account,p);
   Object flag=((ThreadLocal<?>)field(g,"storyClosureIncomplete")).get();
   String blocked=null;byte[]pending=BsonLite.documentValue(profile,"q7StoryPending");
   if(Boolean.TRUE.equals(flag))blocked="剧情结果尚未同步完成，请稍后重试。";
   else if(pending!=null&&!BsonLite.keys(pending).isEmpty())blocked="剧情结果尚待投递，请稍后重试。";
   else try{blocked=EventResetWeekPolicy.busy(profile,p);}catch(ReflectiveOperationException mismatch){throw new IOException("Event reset original busy ABI",mismatch);}
   if(blocked==null)return true;
   return deny(g,out,eid,blocked);
  }
 }
 private static void save(LocalGatewayServer g,String account,LocalTutorialStore.Progress p)throws IOException{call(field(g,"tutorialStore"),"save",new Class<?>[]{String.class,p.getClass()},account,p);}
 private static boolean deny(LocalGatewayServer g,OutputStream out,byte[]eid,String message)throws IOException{
  byte[]digest;try{digest=MessageDigest.getInstance("MD5").digest("showMessageStr".getBytes(StandardCharsets.UTF_8));}catch(NoSuchAlgorithmException impossible){throw new AssertionError(impossible);}
  byte[]frame=(byte[])callStatic("ProtoLite","entityMessage",new Class<?>[]{byte[].class,byte[].class,byte[].class},eid,digest,BsonLite.document("m",message));call(g,"writeFrame",new Class<?>[]{OutputStream.class,int.class,byte[].class},out,5,frame);return false;
 }
 private static Object field(Object o,String name)throws IOException{try{Field f=o.getClass().getDeclaredField(name);f.setAccessible(true);return f.get(o);}catch(ReflectiveOperationException failure){throw new IOException("Event reset original field ABI",failure);}}
 private static Object call(Object o,String name,Class<?>[]types,Object...args)throws IOException{return invoke(o.getClass(),o,name,types,args);}
 private static Object callStatic(String owner,String name,Class<?>[]types,Object...args)throws IOException{try{return invoke(Class.forName("com.project7.localmanager."+owner),null,name,types,args);}catch(ClassNotFoundException failure){throw new IOException(failure);}}
 private static Object invoke(Class<?>owner,Object o,String name,Class<?>[]types,Object[]args)throws IOException{try{Method m=owner.getDeclaredMethod(name,types);m.setAccessible(true);return m.invoke(o,args);}catch(ReflectiveOperationException failure){Throwable cause=failure instanceof InvocationTargetException?((InvocationTargetException)failure).getCause():failure;if(cause instanceof IOException)throw(IOException)cause;if(cause instanceof RuntimeException)throw(RuntimeException)cause;throw new IOException("Event reset original method ABI",cause);}}
}
