package com.project7.localmanager;
import android.content.Context;import java.io.*;import java.lang.reflect.*;import java.nio.charset.StandardCharsets;import java.security.*;import java.util.*;
/** Ordinary RPC transactions only. Reliable entry lacks seq: reject explicitly. */
public final class BaiyeGateway {
 private static final String FUSION="commonItemFusionAsk";
 private static final String NAMED="requestExchangeSuipianWithItem",SELECT="invExchangeHeroFragmentAsk";
 private static final String[] METHODS={FUSION,NAMED,SELECT};
 private static final Method WRITE=BaiyeTransactions.Access.method(LocalGatewayServer.class,"writeFrame",void.class,false,OutputStream.class,int.class,byte[].class),CALLBACK=BaiyeTransactions.Access.method(LocalGatewayServer.class,"completeCallback",void.class,false,OutputStream.class,byte[].class,int.class,String.class),REFRESH=BaiyeTransactions.Access.method(LocalGatewayServer.class,"refreshResourceProfile",void.class,false,byte[].class,String.class,LocalTutorialStore.Progress.class,LocalEventEngine.class);
 private BaiyeGateway(){}
 public static void prepare(Context context)throws IOException{BaiyeCatalog.prepare(context);BaiyeFragmentRules.prepare(context);}
 public static boolean handleDirect(LocalGatewayServer gateway,OutputStream out,byte[]eid,byte[]methodDigest,byte[]params,String account,LocalTutorialStore.Progress progress,LocalEventEngine engine)throws IOException{
  String method=null;for(String candidate:METHODS)if(Arrays.equals(digest(candidate),methodDigest))method=candidate;if(method==null)return false;
  Integer cb=null;try{BaiyeTransactions.document(params);Number n=BsonLite.numericValue(params,"_cbid_");if(n!=null)cb=BaiyeTransactions.positive(n);}catch(RuntimeException ignored){}
  transact(gateway,out,eid,method,params,cb,account,progress,engine);return true;
 }
 public static boolean handleRequest(LocalGatewayServer gateway,OutputStream out,byte[]eid,String method,byte[]params,Integer callback,String account,LocalTutorialStore.Progress progress,LocalEventEngine engine)throws IOException{
  if(!Arrays.asList(METHODS).contains(method))return false;
  // Caller has ACKed reliableRpc but passed no seq/session transaction identity.
  // Executing here would bypass stock replay guards and charge a retry twice.
  publish(gateway,out,eid,method,failure(method,"请从道具界面重新发起本次操作。",0),callback);return true;
 }
 private static void transact(LocalGatewayServer gateway,OutputStream out,byte[]eid,String method,byte[]params,Integer cb,String account,LocalTutorialStore.Progress progress,LocalEventEngine engine)throws IOException{
  LocalResourceEngine.Result result;boolean committed=false;
  try{
   BaiyeTransactions.document(params);List<String>keys=BsonLite.keys(params);String[]fields=FUSION.equals(method)?new String[]{"i","f","n"}:NAMED.equals(method)?new String[]{"ii","hi","fn"}:new String[]{"i","h","s"};
   Set<String>expected=new HashSet<>(Arrays.asList(fields));if(keys.contains("_cbid_"))expected.add("_cbid_");if(!expected.equals(new HashSet<>(keys)))throw new IllegalArgumentException("Parameter keys");Object[]canonical=new Object[keys.size()*2];for(int i=0;i<keys.size();i++){canonical[i*2]=keys.get(i);Number n=BsonLite.numericValue(params,keys.get(i));canonical[i*2+1]=n;if(!FUSION.equals(method)&&keys.get(i).equals(fields[2])){if(!(n instanceof Integer)||n.intValue()<0)throw new IllegalArgumentException("Fragment number");}else BaiyeTransactions.positive(n);}if(!Arrays.equals(params,BsonLite.document(canonical)))throw new IllegalArgumentException("Parameter encoding");
   Object provider=unwrapProvider(BaiyeTransactions.Access.PROVIDER.get(gateway));if(provider==null||provider.getClass()!=LocalProfileStore.class)throw new IllegalArgumentException("Original owner required");
   if(FUSION.equals(method))result=BaiyeTransactions.fusion((LocalProfileStore)provider,account,BaiyeTransactions.positive(BsonLite.numericValue(params,"i")),BaiyeTransactions.positive(BsonLite.numericValue(params,"f")),BaiyeTransactions.positive(BsonLite.numericValue(params,"n")));
   else result=BaiyeFragments.exchange((LocalProfileStore)provider,account,SELECT.equals(method),BaiyeTransactions.positive(BsonLite.numericValue(params,fields[0])),BaiyeTransactions.positive(BsonLite.numericValue(params,fields[1])),BsonLite.intValue(params,fields[2]));
   committed=true;
  }catch(BaiyeTransactions.UncertainCommit uncertain){throw uncertain;}
  catch(IllegalAccessException error){throw new IOException(error);}
  catch(RuntimeException|IOException rejected){result=failure(method,"本次兑换未提交，请检查道具和数量后重试。",rejected instanceof BaiyeFragments.Rejected?((BaiyeFragments.Rejected)rejected).reason:0);}
  if(committed&&engine!=null){synchronized(engine){BaiyeTransactions.call(REFRESH,gateway,digest(method),account,progress,engine);}}
  publish(gateway,out,eid,method,result,cb);
 }
 static LocalResourceEngine.Result failure(String message){return failure(FUSION,message,0);}
 static LocalResourceEngine.Result failure(String method,String message,int reason){LocalResourceEngine.Result r=new LocalResourceEngine.Result(BsonLite.EMPTY_DOCUMENT);r.add("showMessageStr",BsonLite.document("m",message));if(FUSION.equals(method))r.add("commonItemFusionReply",BsonLite.document("r",BsonLite.EMPTY_DOCUMENT));else if(NAMED.equals(method))r.add("replyExchangeSuipianWithItem",BsonLite.document("rs",false,"i",BsonLite.document("rsn",reason)));else r.add("invExchangeHeroFragmentReply",BsonLite.document("r",false,"i",BsonLite.EMPTY_DOCUMENT));return r;}
 private static void publish(LocalGatewayServer g,OutputStream out,byte[]eid,String method,LocalResourceEngine.Result r,Integer cb)throws IOException{for(LocalResourceEngine.Reply reply:r.replies)BaiyeTransactions.call(WRITE,g,out,5,ProtoLite.entityMessage(eid,digest(reply.method),reply.parameters));if(cb!=null&&cb>0)BaiyeTransactions.call(CALLBACK,g,out,eid,cb.intValue(),method);}
 static byte[]digest(String method){try{return MessageDigest.getInstance("MD5").digest(method.getBytes(StandardCharsets.UTF_8));}catch(NoSuchAlgorithmException e){throw new IllegalStateException(e);}}
 private static Object unwrapProvider(Object provider){if(provider==null||!"FailureSafeProfileProvider".equals(provider.getClass().getSimpleName()))return provider;try{java.lang.reflect.Method m=provider.getClass().getDeclaredMethod("delegate");m.setAccessible(true);Object d=m.invoke(provider);if(d!=null)return d;}catch(Exception ignored){}return provider;}
}
