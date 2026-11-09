package com.project7.localmanager;
import java.io.*;import java.lang.reflect.*;import java.nio.*;import java.util.*;
/** Original Store monitor -> PROFILE_LOCK -> original writer; no second owner. */
public final class BaiyeTransactions {
 private BaiyeTransactions(){}
 static final class UncertainCommit extends IOException{private static final long serialVersionUID=1;}
 static final class Access {
  static final Field PROVIDER=field(LocalGatewayServer.class,"profileProvider",LocalGatewayServer.ProfileProvider.class,false),LOCK=field(LocalProfileStore.class,"PROFILE_LOCK",Object.class,true),DIR=field(LocalProfileStore.class,"profilesDirectory",File.class,false);
  static final Method READ=method(LocalProfileStore.class,"readAll",byte[].class,true,File.class),WRITE=method(LocalProfileStore.class,"writeAtomic",void.class,true,File.class,byte[].class);
  static Field field(Class<?>c,String name,Class<?>type,boolean stat){try{Field f=c.getDeclaredField(name);if(f.getType()!=type||Modifier.isStatic(f.getModifiers())!=stat)throw new NoSuchFieldException();f.setAccessible(true);return f;}catch(ReflectiveOperationException e){throw new IllegalStateException("Pinned field ABI",e);}}
  static Method method(Class<?>c,String name,Class<?>type,boolean stat,Class<?>...args){try{Method m=c.getDeclaredMethod(name,args);if(m.getReturnType()!=type||Modifier.isStatic(m.getModifiers())!=stat)throw new NoSuchMethodException();m.setAccessible(true);return m;}catch(ReflectiveOperationException e){throw new IllegalStateException("Pinned method ABI",e);}}
 }
 static Object call(Method method,Object receiver,Object...args)throws IOException{try{return method.invoke(receiver,args);}catch(InvocationTargetException e){Throwable c=e.getCause();if(c instanceof IOException)throw(IOException)c;if(c instanceof RuntimeException)throw(RuntimeException)c;throw new IOException("Stock operation",c);}catch(IllegalAccessException e){throw new IOException(e);}}
 static void document(byte[]b){if(b==null||b.length<5||b[b.length-1]!=0||ByteBuffer.wrap(b).order(ByteOrder.LITTLE_ENDIAN).getInt()!=b.length)throw new IllegalArgumentException("BSON bounds");List<String>keys=BsonLite.keys(b);if(new HashSet<>(keys).size()!=keys.size())throw new IllegalArgumentException("BSON duplicate keys");}
 static int positive(Number v){if(!(v instanceof Integer)&&!(v instanceof Long))throw new IllegalArgumentException("Integer required");long n=v.longValue();if(n<=0||n>Integer.MAX_VALUE)throw new IllegalArgumentException("Integer bounds");return(int)n;}
 static long count(byte[]profile,int id){byte[]inv=BsonLite.documentValue(profile,"inv"),array=BsonLite.arrayValue(inv,"items");document(array);List<byte[]>rows=LocalResourceEngine.array(array);if(rows.size()!=BsonLite.keys(array).size())throw new IllegalArgumentException("Inventory rows");Set<String>uuids=new HashSet<>();long total=0;for(byte[]row:rows){document(row);String uuid=BsonLite.uuidValue(row,"u");if(uuid==null||!uuids.add(uuid))throw new IllegalArgumentException("Inventory identity");if(Integer.valueOf(id).equals(BsonLite.intValue(row,"i")))total=Math.addExact(total,positive(BsonLite.numericValue(row,"w")));}return total;}
 interface Mutation {LocalResourceEngine.Result apply(byte[]profile,LocalResourceCatalog resources)throws IOException;}
 interface Verifier {LocalResourceEngine.Result verify(byte[]observed)throws IOException;}
 static final class Replay extends IOException{final LocalResourceEngine.Result result;Replay(LocalResourceEngine.Result result){this.result=result;}}
 static final class Outcome{final LocalResourceEngine.Result result;final boolean wrote;Outcome(LocalResourceEngine.Result result,boolean wrote){this.result=result;this.wrote=wrote;}}
 static LocalResourceEngine.Result fusion(LocalProfileStore store,String account,final int from,final int to,final int number)throws IOException{
  final int amount=BaiyeCatalog.cost(from,to,number);
  return transact(store,account,(before,resources)->{
   if(count(before,from)<amount||Math.addExact(count(before,to),(long)number)>Integer.MAX_VALUE)throw new IllegalArgumentException("Inventory bounds");
   LocalResourceEngine.Result result=new LocalResourceEngine.Result(before);LocalGiftEngine.consume(result,from,amount);LocalResourceEngine.grant(result,resources,"item",to,number,1);
   if(count(result.profile,from)!=count(before,from)-amount||count(result.profile,to)!=count(before,to)+number)throw new IllegalStateException("Original inventory delta");
   result.add("commonItemFusionReply",BsonLite.document("r",result.reward()));return result;
  });
 }
 static LocalResourceEngine.Result transact(LocalProfileStore store,String account,Mutation operation)throws IOException{return transactOutcome(store,account,operation,null).result;}
 static LocalResourceEngine.Result transact(LocalProfileStore store,String account,Mutation operation,Verifier verifier)throws IOException{return transactOutcome(store,account,operation,verifier).result;}
 static Outcome transactOutcome(LocalProfileStore store,String account,Mutation operation,Verifier verifier)throws IOException{
  if(account==null||!account.matches("[a-z0-9_.-]{1,32}")||LocalAccountStore.isTemplateAccount(account))throw new IllegalArgumentException("Account");
  try{synchronized(store){synchronized(Access.LOCK.get(null)){
   File dir=(File)Access.DIR.get(store),file=new File(dir,account+".bson");if(!file.isFile()||!file.getCanonicalFile().getParentFile().equals(dir.getCanonicalFile()))throw new IllegalArgumentException("Profile path");byte[]before=(byte[])call(Access.READ,null,file);document(before);if(!account.equals(BsonLite.stringValue(before,"account"))||!account.equals(BsonLite.stringValue(before,"an")))throw new IllegalArgumentException("Identity");
   LocalResourceEngine.Result result;
   try{result=operation.apply(before,store.resources());}
   catch(Replay replay){return new Outcome(replay.result,false);}
   document(result.profile);
   try{call(Access.WRITE,null,file,result.profile);}catch(IOException|RuntimeException failed){byte[]observed;try{observed=(byte[])call(Access.READ,null,file);}catch(Exception unreadable){throw new UncertainCommit();}if(Arrays.equals(observed,result.profile))return new Outcome(result,true);if(verifier!=null){LocalResourceEngine.Result verified=verifier.verify(observed);if(verified!=null)return new Outcome(verified,true);}if(!Arrays.equals(observed,before))throw new UncertainCommit();throw failed;}
   return new Outcome(result,true);
  }}}catch(IllegalAccessException e){throw new IOException(e);}
 }
}
