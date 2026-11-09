package com.project7.localmanager;
import android.content.Context;import java.io.*;import java.lang.reflect.*;import java.nio.charset.StandardCharsets;import java.security.*;import java.util.*;
/** Actual StoryMember request binding; caller owns authentication/ACK/sequence.
 * No standalone night exit, fabricated completion or invented reply method. */
public final class DreamRequestGateway {
 public static final String REQUEST="requestStoryhuisu";
 private DreamRequestGateway(){}
 public static void prepare(Context context)throws IOException{DreamCoordinator.prepare(context);}
 public static boolean handleDirect(LocalGatewayServer g,OutputStream out,byte[]eid,byte[]digest,byte[]params,String account,LocalTutorialStore.Progress p,LocalEventEngine e)throws IOException{
  if(!MessageDigest.isEqual(md5(REQUEST),digest==null?new byte[0]:digest))return false;
  return handleRequest(g,out,eid,REQUEST,params,params==null?null:BsonLite.intValue(params,"_cbid_"),account,p,e);
 }
 public static boolean handleRequest(LocalGatewayServer g,OutputStream out,byte[]eid,String method,byte[]params,Integer cbid,String account,LocalTutorialStore.Progress p,LocalEventEngine e)throws IOException{
  if(!REQUEST.equals(method))return false;
  if((Boolean)DreamAccess.stat(DreamAccess.type("LocalAccountStore"),"isTemplateAccount",new Class<?>[]{String.class},account)){negative(g,out,eid,cbid,"预览账号为只读模式。");return true;}
  if(p==null||e==null){negative(g,out,eid,cbid,"当前离线版本暂时无法处理该请求。");return true;}
  synchronized(e){
   if(DreamAccess.get(e,"progress")!=p)throw new IOException("Live dream Progress identity mismatch");
   if(!((Collection<?>)DreamAccess.get(e,"checkingMessages")).isEmpty())throw new IOException("Dream evaluator already active");
   byte[]before=DreamStorage.locked(g,account,tx->tx.read());DreamState.Reason reason;
   try{reason=DreamCoordinator.enterRequest(g,account,p,e,method);}catch(IOException failure){
    byte[]after=DreamStorage.locked(g,account,tx->tx.read());if(!Arrays.equals(before,after)||BsonLite.documentValue(after,"q7DreamPatrolCommit")!=null)throw failure;
    negative(g,out,eid,cbid,"本次请求未提交，请稍后重试。");return true;
   }
   if(reason!=DreamState.Reason.ENTERED&&reason!=DreamState.Reason.ALREADY_ACTIVE){negative(g,out,eid,cbid,"当前条件未满足，请先完成当前剧情。");return true;}
   for(String key:new String[]{"eventQueries","preparedQuery"})((ThreadLocal<?>)DreamAccess.get(g,key)).remove();
   byte[]profile=DreamStorage.locked(g,account,tx->tx.read());
   Object result;try{Constructor<?>ctor=DreamAccess.type("LocalResourceEngine$Result").getDeclaredConstructor(byte[].class);ctor.setAccessible(true);result=ctor.newInstance((Object)profile);}catch(ReflectiveOperationException failure){throw DreamAccess.failure(failure);}
   DreamAccess.stat(DreamAccess.type("LocalServiceEngine"),"syncRoute",new Class<?>[]{result.getClass()},result);
   for(Object reply:(Iterable<?>)DreamAccess.get(result,"replies"))emit(g,out,eid,(String)DreamAccess.get(reply,"method"),(byte[])DreamAccess.get(reply,"parameters"));
   emit(g,out,eid,"syncHuiSuData",BsonLite.document("d",DreamState.huiSuProjection(profile)));
   byte[]events=(byte[])DreamAccess.stat(DreamAccess.type("BsonLite"),"eventListsDocument",new Class<?>[]{Iterable.class,Iterable.class},DreamAccess.call(e,"availableEvents",new Class<?>[0]),DreamAccess.call(e,"processingEvents",new Class<?>[0]));
   emit(g,out,eid,"pushEvents",events);callback(g,out,eid,cbid);return true;
  }
 }
 private static void negative(LocalGatewayServer g,OutputStream out,byte[]eid,Integer cbid,String text)throws IOException{emit(g,out,eid,"showMessageStr",BsonLite.document("m",text));callback(g,out,eid,cbid);}
 private static void callback(LocalGatewayServer g,OutputStream out,byte[]eid,Integer cbid)throws IOException{if(cbid!=null)DreamAccess.call(g,"completeCallback",new Class<?>[]{OutputStream.class,byte[].class,int.class,String.class},out,eid,cbid.intValue(),REQUEST);}
 private static void emit(LocalGatewayServer g,OutputStream out,byte[]eid,String method,byte[]params)throws IOException{byte[]frame=(byte[])DreamAccess.stat(DreamAccess.type("ProtoLite"),"entityMessage",new Class<?>[]{byte[].class,byte[].class,byte[].class},eid,md5(method),params);DreamAccess.call(g,"writeFrame",new Class<?>[]{OutputStream.class,int.class,byte[].class},out,5,frame);}
 private static byte[]md5(String method){try{return MessageDigest.getInstance("MD5").digest(method.getBytes(StandardCharsets.UTF_8));}catch(NoSuchAlgorithmException impossible){throw new AssertionError(impossible);}}
}
