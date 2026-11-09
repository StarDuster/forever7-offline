package com.project7.localmanager;
import android.content.Context;
import android.content.res.AssetManager;
import android.system.Os;
import java.io.*;
import java.nio.*;
import java.nio.file.*;
import java.security.*;
import java.util.*;
import java.util.concurrent.*;

/** Real translated stock engines/BSON/writer, with host Android filesystem seams only. */
public final class CoreGapHostTests {
 static void check(boolean yes,String message){if(!yes)throw new AssertionError(message);}
 static final byte[] ID=new byte[12];static final String ACCOUNT="host_synthetic";
 static byte[] md5(String value)throws Exception{return MessageDigest.getInstance("MD5").digest(value.getBytes("UTF-8"));}
 static final class Disk implements AutoCloseable {
  final Path root;final File file;final LocalProfileStore store;final LocalGatewayServer gateway;
  Disk(File assets,byte[] profile)throws Exception {
   root=Files.createTempDirectory("p7-cg-synthetic-");Files.createDirectory(root.resolve("profiles"));
   file=root.resolve("profiles/"+ACCOUNT+".bson").toFile();Files.write(file.toPath(),profile);
   store=new LocalProfileStore(new Context(root.toFile(),new AssetManager(assets)));
   gateway=new LocalGatewayServer(0,null,store,null,null,null,null,null,null);
  }
  byte[]read()throws Exception{return Files.readAllBytes(file.toPath());}
  List<ProtoLite.EntityMessage> call(byte[]params)throws Exception {
   ByteArrayOutputStream out=new ByteArrayOutputStream();
   check(CoreGapBridge.handleResourceRpc(gateway,out,ID,md5("requestMainlineCgRewards"),params,ACCOUNT),"consumed");
   return frames(out.toByteArray());
  }
  public void close()throws Exception {
   gateway.close();try(java.util.stream.Stream<Path> all=Files.walk(root)){
    for(Path p:(Iterable<Path>)all.sorted(Comparator.reverseOrder())::iterator)Files.delete(p);
   }
  }
 }
 static List<ProtoLite.EntityMessage>frames(byte[] wire)throws Exception {
  List<ProtoLite.EntityMessage> result=new ArrayList<>();ByteBuffer b=ByteBuffer.wrap(wire).order(ByteOrder.LITTLE_ENDIAN);
  while(b.hasRemaining()){
   int size=b.getInt();check(size>=2&&b.remaining()>=size,"framing");check(b.getShort()==5,"stock opcode5");
   byte[]message=new byte[size-2];b.get(message);result.add(ProtoLite.parseEntityMessage(message));
  }
  return result;
 }
 static byte[]profile(int balance,boolean owned,boolean legacy){
  byte[]oaed=BsonLite.document("other","preserve","mcr",legacy?Arrays.asList(Arrays.asList(11,true)):Collections.emptyList());
  return BsonLite.document("account",ACCOUNT,"an",ACCOUNT,"st",900001,"host_unknown","preserve",
   "souvenir",balance,"cgs",owned?Arrays.asList(11,13):Collections.emptyList(),"oaed",oaed,
   "week_state",BsonLite.document("week",9,"day",4),"opaque",new byte[]{5,0,0,0,0});
 }
 static byte[]request(int line,int cg){return BsonLite.document("li",line,"cg",cg);}
 static ProtoLite.EntityMessage last(List<ProtoLite.EntityMessage> replies)throws Exception {
  check(!replies.isEmpty(),"reply exists");ProtoLite.EntityMessage last=replies.get(replies.size()-1);
  check(Arrays.equals(last.methodMd5,md5("replyMainlineCgRewards")),"claim last");return last;
 }
 static void success(List<ProtoLite.EntityMessage>replies)throws Exception {
  check(Boolean.TRUE.equals(BsonLite.boolValue(last(replies).parameters,"rs")),"success true");
  int coin=-1;
  for(int i=0;i<replies.size();i++)if(Arrays.equals(replies.get(i).methodMd5,md5("updateSouvenirCoin")))coin=i;
  check(coin>=0&&coin<replies.size()-1,"currency before reply");
 }
 static void fail(Disk disk,byte[]params)throws Exception {
  byte[]before=disk.read();int renames=Os.renames;List<ProtoLite.EntityMessage>replies=disk.call(params);
  check(replies.size()==1&&Boolean.FALSE.equals(BsonLite.boolValue(last(replies).parameters,"rs")),"false unlock reply");
  check(BsonLite.keys(BsonLite.documentValue(last(replies).parameters,"i")).isEmpty(),"failure info empty");
  check(Arrays.equals(before,disk.read())&&renames==Os.renames,"failure untouched");
 }
 static void persisted(byte[]p,int balance)throws Exception {
  check(BsonLite.intValue(p,"souvenir")==balance,"real souvenir balance");
  check("preserve".equals(BsonLite.stringValue(p,"host_unknown")),"unknown field retained");
  check(BsonLite.intValue(BsonLite.documentValue(p,"week_state"),"week")==9,"week unchanged");
  byte[]oaed=BsonLite.documentValue(p,"oaed");check("preserve".equals(BsonLite.stringValue(oaed,"other")),"oaed unknown retained");
  Object pairs=BsonLite.messagePackValue(BsonLite.arrayValue(oaed,"mcr"),true);
  check(pairs instanceof List,"mcr array");List<?>pair=(List<?>)((List<?>)pairs).get(0);
  check(pair.get(0) instanceof Integer&&Integer.valueOf(11).equals(pair.get(0))&&Boolean.TRUE.equals(pair.get(1)),"integer Bool pair");
  check(BsonLite.documentValue(p,"inventory")==null,"no fake329 inventory");
 }
 public static void main(String[]args)throws Exception {
  File assets=new File(args[0]);int tests=0;
  Map<String,Object>consumerCases=new LinkedHashMap<>();
  try(Disk disk=new Disk(assets,profile(10,true,false))){
   int before=Os.renames;List<ProtoLite.EntityMessage> first=disk.call(request(1,11));success(first);
   consumerCases.put("success",BsonLite.messagePackValue(last(first).parameters,false));
   consumerCases.put("profile",BsonLite.messagePackValue(disk.read(),false));
   consumerCases.put("failure",BsonLite.messagePackValue(CoreGapBridge.failure().replies.get(0).parameters,false));
   persisted(disk.read(),710);check(Os.renames==before+1,"one atomic writer");
   byte[]committed=disk.read();success(disk.call(request(1,11)));check(Arrays.equals(committed,disk.read()),"retry no second write");
   check(Os.renames==before+1,"retry no rename");tests++;
   // Real stock normalization/tutorial projection preserves claim and receipt.
   byte[]normalized=BsonLite.withRequiredClientDefaults(committed);
   normalized=BsonLite.withCanonicalHeroPairs(normalized);
   normalized=BsonLite.withTutorialProgress(normalized,LocalTutorialStore.Progress.fresh());
   persisted(normalized,710);check(Arrays.equals(BsonLite.documentValue(committed,CoreGapBridge.RECEIPTS),BsonLite.documentValue(normalized,CoreGapBridge.RECEIPTS)),"receipt survives stock normalization");tests++;
   java.lang.reflect.Method reset=LocalWeekEngine.class.getDeclaredMethod("resetProfile",byte[].class,LocalTutorialStore.Progress.class,int.class,LocalWeekCatalog.class);
   reset.setAccessible(true);
   LocalWeekCatalog weeks=new LocalWeekCatalog(new FileInputStream(new File(assets,"weeks.tsv")));
   byte[]resetProfile=(byte[])reset.invoke(null,committed,LocalTutorialStore.Progress.fresh(),1,weeks);
   check(Arrays.equals(BsonLite.documentValue(committed,CoreGapBridge.RECEIPTS),BsonLite.documentValue(resetProfile,CoreGapBridge.RECEIPTS)),"receipt survives original week reset");
   check(Arrays.equals(BsonLite.arrayValue(BsonLite.documentValue(committed,"oaed"),"mcr"),BsonLite.arrayValue(BsonLite.documentValue(resetProfile,"oaed"),"mcr")),"mcr survives original week reset");tests++;

   fail(disk,request(2,11));fail(disk,request(1,999));fail(disk,BsonLite.document("li",1.0,"cg",11));
   fail(disk,BsonLite.document("li",true,"cg",11));fail(disk,BsonLite.document("li",1,"cg",11,"account","other"));tests++;
   ByteArrayOutputStream lockCheck=new ByteArrayOutputStream(){
    public synchronized void write(int value){check(!Thread.holdsLock(disk.store)&&!Thread.holdsLock(LocalProfileStore.PROFILE_LOCK),"network outside locks");super.write(value);}
    public synchronized void write(byte[] bytes,int off,int len){check(!Thread.holdsLock(disk.store)&&!Thread.holdsLock(LocalProfileStore.PROFILE_LOCK),"network outside locks");super.write(bytes,off,len);}
   };
   CoreGapBridge.handleResourceRpc(disk.gateway,lockCheck,ID,md5("requestMainlineCgRewards"),request(1,11),ACCOUNT);
   success(frames(lockCheck.toByteArray()));
   ByteArrayOutputStream unused=new ByteArrayOutputStream();check(!CoreGapBridge.handleResourceRpc(disk.gateway,unused,ID,new byte[16],request(1,11),ACCOUNT)&&unused.size()==0,"unknown unchanged");tests++;
  }
  try(Disk disk=new Disk(assets,profile(0,false,false))){fail(disk,request(1,11));tests++;}
  try(Disk disk=new Disk(assets,profile(Integer.MAX_VALUE-699,true,false))){fail(disk,request(1,11));tests++;}
  try(Disk disk=new Disk(assets,profile(1,true,true))){
   byte[]before=disk.read();List<ProtoLite.EntityMessage>r=disk.call(request(1,11));success(r);
   byte[]reward=BsonLite.documentValue(BsonLite.documentValue(last(r).parameters,"i"),"rwd");
   check(((List<?>)BsonLite.messagePackValue(BsonLite.arrayValue(reward,"item"),true)).isEmpty(),"legacy empty reward");
   check(Arrays.equals(before,disk.read()),"legacy never grant/write");tests++;
  }
  try(Disk disk=new Disk(assets,profile(0,true,false))){
   Os.failBefore=true;fail(disk,request(1,11));success(disk.call(request(1,11)));persisted(disk.read(),700);tests++;
  }
  try(Disk disk=new Disk(assets,profile(0,true,false))){
   Os.failAfter=true;success(disk.call(request(1,11)));persisted(disk.read(),700);
   success(disk.call(request(1,11)));persisted(disk.read(),700);tests++;
  }
  try(Disk disk=new Disk(assets,profile(0,true,false))){
   OutputStream broken=new OutputStream(){public void write(int value)throws IOException{throw new IOException("synthetic disconnected");}};
   try{CoreGapBridge.handleResourceRpc(disk.gateway,broken,ID,md5("requestMainlineCgRewards"),request(1,11),ACCOUNT);throw new AssertionError("disconnect");}catch(IOException expected){}
   persisted(disk.read(),700);success(disk.call(request(1,11)));persisted(disk.read(),700);tests++;
  }
  try(Disk disk=new Disk(assets,profile(0,true,false))){
   ExecutorService pool=Executors.newFixedThreadPool(8);CountDownLatch start=new CountDownLatch(1);List<Future<?>>f=new ArrayList<>();
   int before=Os.renames;
   for(int i=0;i<16;i++)f.add(pool.submit(()->{start.await();success(disk.call(request(1,11)));return null;}));
   start.countDown();for(Future<?>future:f)future.get(30,TimeUnit.SECONDS);pool.shutdown();
   persisted(disk.read(),700);check(Os.renames==before+1,"concurrent one commit");tests++;
  }
  try(Disk disk=new Disk(assets,profile(0,true,false))){
   byte[]before=disk.read();ByteArrayOutputStream out=new ByteArrayOutputStream();
   CoreGapBridge.handleResourceRpc(disk.gateway,out,ID,md5("requestMainlineCgRewards"),request(1,11),"other_account");
   check(Boolean.FALSE.equals(BsonLite.boolValue(last(frames(out.toByteArray())).parameters,"rs")),"wrong authenticated account no file");
   check(Arrays.equals(before,disk.read()),"other identity untouched");tests++;
  }
  if(args.length>1)Files.write(Paths.get(args[1]),new org.json.JSONObject(consumerCases).toString().getBytes("UTF-8"));
  System.out.println("PASS "+tests+" finite original-engine CG transaction groups; business idempotence only, UI replay is repeatable");
 }
}
