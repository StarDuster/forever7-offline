package com.project7.localmanager;
import android.content.Context;import java.io.*;import java.lang.reflect.*;import java.util.*;
/** Eight fixed stock purchase transactions; shared original Store only. */
public final class BaiyeShopGateway {
 private static final String METHOD="buyCardMallItem";
 private static final Method WRITE=BaiyeTransactions.Access.method(LocalGatewayServer.class,"writeFrame",void.class,false,OutputStream.class,int.class,byte[].class),CALLBACK=BaiyeTransactions.Access.method(LocalGatewayServer.class,"completeCallback",void.class,false,OutputStream.class,byte[].class,int.class,String.class),REFRESH=BaiyeTransactions.Access.method(LocalGatewayServer.class,"refreshResourceProfile",void.class,false,byte[].class,String.class,LocalTutorialStore.Progress.class,LocalEventEngine.class);
 private BaiyeShopGateway(){}
 public static void prepare(Context c)throws IOException{BaiyeShopCatalog.prepare(c);}
 static boolean selected(byte[]params){try{BaiyeTransactions.document(params);return BaiyeShopCatalog.supports(BaiyeTransactions.positive(BsonLite.numericValue(params,"store_id")));}catch(RuntimeException invalid){return false;}}
 public static boolean handleDirect(LocalGatewayServer g,OutputStream out,byte[]eid,byte[]method,byte[]params,String account,LocalTutorialStore.Progress p,LocalEventEngine e)throws IOException{
  if(!Arrays.equals(method,BaiyeGateway.digest(METHOD))||!selected(params))return false;Integer cb=null;
  if(BsonLite.keys(params).contains("_cbid_")){
   try{cb=BaiyeTransactions.positive(BsonLite.numericValue(params,"_cbid_"));}
   catch(RuntimeException invalid){publish(g,out,eid,failure("本次购买参数无效，未扣除任何道具或代币。"),null);return true;}
  }
  LocalResourceEngine.Result r;boolean committed=false;
  try{Object store=unwrapProvider(BaiyeTransactions.Access.PROVIDER.get(g));if(store==null||store.getClass()!=LocalProfileStore.class)throw new IllegalArgumentException("Original owner required");r=BaiyeTransactions.transact((LocalProfileStore)store,account,(before,catalog)->BaiyeShopPolicy.apply(before,catalog,params,System.currentTimeMillis()));committed=true;}
  catch(BaiyeTransactions.UncertainCommit uncertain){throw uncertain;}catch(IllegalAccessException failure){throw new IOException(failure);}catch(IOException|RuntimeException rejection){r=failure("本次购买未提交，请检查余额、数量或限购条件。");}
  if(committed&&e!=null)synchronized(e){BaiyeTransactions.call(REFRESH,g,BaiyeGateway.digest(METHOD),account,p,e);}
  publish(g,out,eid,r,cb);return true;
 }
 public static boolean handleRequest(LocalGatewayServer g,OutputStream out,byte[]eid,String method,byte[]params,Integer cb,String account,LocalTutorialStore.Progress p,LocalEventEngine e)throws IOException{if(!METHOD.equals(method)||!selected(params))return false;publish(g,out,eid,failure("请从商品界面重新发起本次购买。"),cb);return true;}
 static LocalResourceEngine.Result failure(String message){LocalResourceEngine.Result r=new LocalResourceEngine.Result(BsonLite.EMPTY_DOCUMENT);r.add("showMessageStr",BsonLite.document("m",message));r.add("replyBuyCardMallItem",BsonLite.document("r",false,"i",BsonLite.EMPTY_DOCUMENT));return r;}
 static void publish(LocalGatewayServer g,OutputStream out,byte[]eid,LocalResourceEngine.Result result,Integer cb)throws IOException{for(LocalResourceEngine.Reply r:result.replies)BaiyeTransactions.call(WRITE,g,out,5,ProtoLite.entityMessage(eid,BaiyeGateway.digest(r.method),r.parameters));if(cb!=null&&cb>0)BaiyeTransactions.call(CALLBACK,g,out,eid,cb.intValue(),METHOD);}
 private static Object unwrapProvider(Object provider){if(provider==null||!"FailureSafeProfileProvider".equals(provider.getClass().getSimpleName()))return provider;try{java.lang.reflect.Method m=provider.getClass().getDeclaredMethod("delegate");m.setAccessible(true);Object d=m.invoke(provider);if(d!=null)return d;}catch(Exception ignored){}return provider;}
}
