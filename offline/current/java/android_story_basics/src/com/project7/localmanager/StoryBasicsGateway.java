package com.project7.localmanager;
import android.content.Context;import java.io.*;import java.lang.reflect.*;import java.util.*;
/** Two bounded ordinary client RPCs; persistent writes share the stock Store owner. */
public final class StoryBasicsGateway {
 private StoryBasicsGateway(){}
 private static final String SHARE="getShareLink",READ="readDailyWish";
 private static final Method WRITE=BaiyeTransactions.Access.method(LocalGatewayServer.class,"writeFrame",void.class,false,OutputStream.class,int.class,byte[].class),CALLBACK=BaiyeTransactions.Access.method(LocalGatewayServer.class,"completeCallback",void.class,false,OutputStream.class,byte[].class,int.class,String.class);
 public static void prepare(Context context)throws IOException{}
 public static boolean handleDirect(LocalGatewayServer g,OutputStream out,byte[]eid,byte[]digest,byte[]params,String account,LocalTutorialStore.Progress p,LocalEventEngine engine)throws IOException{
  String method=Arrays.equals(digest,BaiyeGateway.digest(SHARE))?SHARE:Arrays.equals(digest,BaiyeGateway.digest(READ))?READ:null;if(method==null)return false;
  Integer cb=null;try{BaiyeTransactions.document(params);Number n=BsonLite.numericValue(params,"_cbid_");if(n!=null)cb=BaiyeTransactions.positive(n);}catch(RuntimeException ignored){}
  return handleRequest(g,out,eid,method,params,cb,account,p,engine);
 }
 public static boolean handleRequest(LocalGatewayServer g,OutputStream out,byte[]eid,String method,byte[]params,Integer callback,String account,LocalTutorialStore.Progress p,LocalEventEngine engine)throws IOException{
  if(!SHARE.equals(method)&&!READ.equals(method))return false;
  if(SHARE.equals(method)){
   // Original Str('l') consumer clears wait_for_link before testing link truthiness.
   // Empty is an explicit unavailable result, never a fake public share URL.
   send(g,out,eid,"replyShareLink",BsonLite.document("l",""));
   send(g,out,eid,"showMessageStr",BsonLite.document("m","离线模式不支持生成公开分享链接，结局CG仍可在本地查看。"));
  }else{
   LocalResourceEngine.Result result;
   try{
    BaiyeTransactions.document(params);Set<String>keys=new HashSet<>(BsonLite.keys(params));if(keys.contains("_cbid_"))BaiyeTransactions.positive(BsonLite.numericValue(params,"_cbid_"));keys.remove("_cbid_");if(!keys.isEmpty())throw new IllegalArgumentException("readDailyWish parameters");
    Object owner=unwrapProvider(BaiyeTransactions.Access.PROVIDER.get(g));if(owner==null||owner.getClass()!=LocalProfileStore.class)throw new IllegalArgumentException("Original Store required");
    result=BaiyeTransactions.transact((LocalProfileStore)owner,account,(before,resources)->{
     byte[]std=BsonLite.documentValue(before,"std");if(std==null)throw new IllegalArgumentException("Missing story data");BaiyeTransactions.document(std);
     byte[]dw=BsonLite.arrayValue(std,"dw");Integer hero=BsonLite.intValue(std,"dwh");if(dw==null||hero==null)throw new IllegalArgumentException("Missing daily wish state");BaiyeTransactions.document(dw);
     LocalResourceEngine.Result r=new LocalResourceEngine.Result(BsonLite.withProfileDocument(before,"std",BsonLite.withProfileBool(std,"dwr",true)));
     byte[]ack=BsonLite.document("dwh",hero,"dwr",true);ack=BsonLite.withCopiedValue(ack,"dw",std,"dw");r.add("syncDailyWish",ack);return r;
    });
   }catch(BaiyeTransactions.UncertainCommit uncertain){throw uncertain;}
   catch(IllegalAccessException e){throw new IOException(e);}
   catch(RuntimeException|IOException rejected){send(g,out,eid,"showMessageStr",BsonLite.document("m","心愿已读状态未能保存，请重新打开信件后重试。"));finish(g,out,eid,method,callback);return true;}
   for(LocalResourceEngine.Reply reply:result.replies)send(g,out,eid,reply.method,reply.parameters);
  }
  finish(g,out,eid,method,callback);return true;
 }
 private static void finish(LocalGatewayServer g,OutputStream out,byte[]eid,String method,Integer callback)throws IOException{if(callback!=null&&callback>0)BaiyeTransactions.call(CALLBACK,g,out,eid,callback.intValue(),method);}
 private static void send(LocalGatewayServer g,OutputStream out,byte[]eid,String method,byte[]params)throws IOException{BaiyeTransactions.call(WRITE,g,out,5,ProtoLite.entityMessage(eid,BaiyeGateway.digest(method),params));}
 private static Object unwrapProvider(Object provider){if(provider==null||!"FailureSafeProfileProvider".equals(provider.getClass().getSimpleName()))return provider;try{java.lang.reflect.Method m=provider.getClass().getDeclaredMethod("delegate");m.setAccessible(true);Object d=m.invoke(provider);if(d!=null)return d;}catch(Exception ignored){}return provider;}
}
