package com.project7.localmanager;
import java.io.*;import java.nio.charset.StandardCharsets;import java.security.*;
/** Original reliable handler calls these only at its existing reply seam. */
public final class DreamPatrolReply {
 private DreamPatrolReply(){}
 /** Before original callback/enter_patrol_reply, including cached/resume result.
  * No admission, selection, budget change, profile write or reliable ACK. */
 public static void project(LocalGatewayServer g,OutputStream out,byte[]eid,String account,LocalTutorialStore.Progress p,LocalEventEngine engine)throws IOException{
  synchronized(engine){byte[]live=(byte[])DreamAccess.get(engine,"profile");
   if(BsonLite.documentValue(live,DreamState.CONTEXT)==null&&!Boolean.TRUE.equals(BsonLite.boolValue(BsonLite.documentValue(live,"std"),"hsf")))return;
   byte[]profile=DreamStorage.locked(g,account,tx->tx.read());
   if(BsonLite.documentValue(profile,DreamState.CONTEXT)!=null||Boolean.TRUE.equals(BsonLite.boolValue(BsonLite.documentValue(profile,"std"),"hsf")))emit(g,out,eid,"syncHuiSuData",BsonLite.document("d",DreamState.huiSuProjection(profile)));
  }
 }
 /** Exact callback replacement, preserving original delegate for every method.
  * Current CityMember producers supply callbacks for begin and claim. */
 public static void complete(LocalGatewayServer g,OutputStream out,byte[]eid,int callback,String method,String account,LocalTutorialStore.Progress p,LocalEventEngine engine)throws IOException{
  if(("enterPatrolRequest".equals(method)||"patrolReward".equals(method))&&account!=null&&p!=null&&engine!=null)project(g,out,eid,account,p,engine);
  DreamAccess.call(g,"completeCallback",new Class<?>[]{OutputStream.class,byte[].class,int.class,String.class},out,eid,callback,method);
 }
 /** Only claim's null sentinel: stop original friendly/cache/success tail. */
 public static void rejectClaim(LocalGatewayServer g,OutputStream out,byte[]eid,Integer callback)throws IOException{
  emit(g,out,eid,"showMessageStr",BsonLite.document("m","本次巡查领取未提交，请稍后重试。"));
  if(callback!=null)DreamAccess.call(g,"completeCallback",new Class<?>[]{OutputStream.class,byte[].class,int.class,String.class},out,eid,callback.intValue(),"patrolReward");
 }
 private static void emit(LocalGatewayServer g,OutputStream out,byte[]eid,String method,byte[]params)throws IOException{
  byte[]digest;try{digest=MessageDigest.getInstance("MD5").digest(method.getBytes(StandardCharsets.UTF_8));}catch(NoSuchAlgorithmException impossible){throw new AssertionError(impossible);}
  byte[]frame=(byte[])DreamAccess.stat(DreamAccess.type("ProtoLite"),"entityMessage",new Class<?>[]{byte[].class,byte[].class,byte[].class},eid,digest,params);DreamAccess.call(g,"writeFrame",new Class<?>[]{OutputStream.class,int.class,byte[].class},out,5,frame);
 }
}
