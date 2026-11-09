package com.project7.localmanager;
import android.content.*;import android.content.res.*;import java.io.*;import java.net.*;import java.nio.*;import java.nio.file.*;import java.security.*;import java.util.*;import java.util.concurrent.*;import org.json.*;
/** Real loopback socket -> LocalGatewayServer.handleClient -> day dispatch.
 *  Baseline proves the outer IOException path sends nothing and closes; fixed provider seam
 *  returns old-day updateDay + explicit error, no settlement/reward, profile unchanged, retry works. */
public final class DayRpcSocketHost {
 static final String ACCOUNT="host_day_socket";
 static int checks;
 static void check(boolean ok,String message){checks++;if(!ok)throw new AssertionError(message);}
 static byte[] md5(String value)throws Exception{return MessageDigest.getInstance("MD5").digest(value.getBytes("UTF-8"));}
 static final class Wire implements AutoCloseable {
  final Socket socket;final DataInputStream in;final OutputStream out;
  Wire(Socket connected)throws Exception{socket=connected;socket.setSoTimeout(15000);in=new DataInputStream(new BufferedInputStream(socket.getInputStream()));out=new BufferedOutputStream(socket.getOutputStream());}
  void write(int method,byte[]payload)throws Exception{int size=payload.length+2;out.write(new byte[]{(byte)(size&255),(byte)((size>>8)&255),(byte)((size>>16)&255),(byte)((size>>24)&255),(byte)(method&255),(byte)((method>>8)&255)});out.write(payload);out.flush();}
  static final class Frame{final int method;final byte[]payload;Frame(int method,byte[]payload){this.method=method;this.payload=payload;}}
  Frame read()throws IOException{int s0=in.readUnsignedByte(),s1=in.readUnsignedByte(),s2=in.readUnsignedByte(),s3=in.readUnsignedByte();int size=s0|(s1<<8)|(s2<<16)|(s3<<24);int method=in.readUnsignedByte()|(in.readUnsignedByte()<<8);byte[]payload=new byte[size-2];in.readFully(payload);return new Frame(method,payload);}
  static final class Fields{final Map<Integer,byte[]>values=new LinkedHashMap<Integer,byte[]>();Fields(byte[]payload)throws IOException{int[]at={0};while(at[0]<payload.length){int tag=varint(payload,at);int field=tag>>>3,wire=tag&7;if(wire!=2)throw new IOException("unexpected wire type "+wire);int length=varint(payload,at);if(length<0||at[0]+length>payload.length)throw new IOException("bad length");values.put(field,Arrays.copyOfRange(payload,at[0],at[0]+length));at[0]+=length;}}static int varint(byte[]data,int[]at){int value=0,shift=0;while(true){int b=data[at[0]++]&255;value|=(b&127)<<shift;if((b&128)==0)return value;shift+=7;}}}
  static byte[] nestedMd5(byte[]value)throws IOException{int[]at={0};int tag=Fields.varint(value,at);if((tag>>>3)!=1||(tag&7)!=2)throw new IOException("nested md5 shape");int length=Fields.varint(value,at);return Arrays.copyOfRange(value,at[0],at[0]+length);}
  ProtoLite.EntityMessage untilEntityInfo(String className,long deadline)throws Exception{while(System.currentTimeMillis()<deadline){Frame frame=read();if(frame.method!=3)continue;Fields fields=new Fields(frame.payload);if(!Arrays.equals(nestedMd5(fields.values.get(2)),md5(className)))continue;ProtoLite.EntityMessage message=new ProtoLite.EntityMessage();message.id=fields.values.get(3);message.parameters=fields.values.get(4);return message;}throw new AssertionError("timeout waiting for entity "+className);}
  public void close()throws Exception{socket.close();}
 }
 static final class Row{final String method;final byte[]parameters;Row(String method,byte[]parameters){this.method=method;this.parameters=parameters;}}
 static final List<String>DAY=Arrays.asList("statusCheckReply","showMessageStr","updateDay","showDailySettlement","get_city_data_reply","pullEventsReply","serverCallbackCarrier","reliableRpcAck");
 static String name(ProtoLite.EntityMessage m)throws Exception{for(String s:DAY)if(Arrays.equals(m.methodMd5,md5(s)))return s;return "other:"+hex(m.methodMd5);}
 static String hex(byte[]data){StringBuilder s=new StringBuilder();for(byte b:data)s.append(String.format("%02x",b&255));return s.toString();}
 static final class Fixture implements AutoCloseable {
  final Path root;final File file;final Context context;final LocalProfileStore store;final LocalTutorialStore tutorials;final int port;final LocalGatewayServer gateway;final Thread thread;final CountDownLatch ready=new CountDownLatch(1);final List<String> status=Collections.synchronizedList(new ArrayList<String>());Socket socket;Wire wire;byte[]avatar;
  Fixture(File assets,boolean safe)throws Exception{
   root=Files.createTempDirectory("p7-day-socket-v63-");Files.createDirectory(root.resolve("profiles"));file=new File(root.toFile(),"profiles/"+ACCOUNT+".bson");
   context=new Context(root.toFile(),new AssetManager(assets));
   LocalAccountStore accounts=new LocalAccountStore(new File(root.toFile(),"accounts.properties"));accounts.registerOne(ACCOUNT,"hostpass");
   store=new LocalProfileStore(context);tutorials=new LocalTutorialStore(context);LocalTutorialStore.Progress legal=LocalTutorialStore.Progress.fresh();legal.weekCommit="host_day_socket_week";legal.weekIndex=1;legal.initPrologue=false;legal.inEmergency=false;legal.status="city";legal.patrolActions=-1;legal.sandglassActions=-1;legal.completedEvents.add(1047);legal.availableEvents.clear();legal.processingEvents.clear();legal.processingNewbees.clear();tutorials.save(ACCOUNT,legal);
   LocalEventCatalog events=new LocalEventCatalog(new FileInputStream(new File(assets,"event_graph.tsv")));
   LocalNewbeeCatalog newbees=new LocalNewbeeCatalog(new ByteArrayInputStream(new byte[0]));
   LocalCombatCatalog combat=new LocalCombatCatalog(context);LocalPatrolCatalog patrol=new LocalPatrolCatalog(context);
   Files.write(file.toPath(),template(assets));
   int chosen;try(ServerSocket probe=new ServerSocket(0,1,InetAddress.getByName("127.0.0.1"))){chosen=probe.getLocalPort();}port=chosen;
   LocalGatewayServer.ProfileProvider provider=safe?new FailureSafeProfileProvider(store):store;
   gateway=new LocalGatewayServer(chosen,accounts,provider,tutorials,events,newbees,combat,patrol,new LocalGatewayServer.StatusListener(){public void onStatus(boolean ok,String message){status.add(ok+":"+message);if(ok)ready.countDown();}});
   thread=new Thread(new Runnable(){public void run(){try{gateway.run();}catch(Throwable error){status.add("false:"+error);}}},safe?"p7-day-socket-safe":"p7-day-socket-baseline");thread.setDaemon(true);thread.start();
   check(ready.await(10,TimeUnit.SECONDS),"gateway listening status "+status);
   connect();
  }
  void connect()throws Exception{socket=new Socket("127.0.0.1",port);socket.setSoTimeout(15000);wire=new Wire(socket);wire.write(0,new byte[0]);ProtoLite.EntityMessage account=wire.untilEntityInfo("ClientAccount",System.currentTimeMillis()+10000);wire.write(1,ProtoLite.entityMessage(account.id,md5("login"),BsonLite.document("name",ACCOUNT,"psw","hostpass")));ProtoLite.EntityMessage info=wire.untilEntityInfo("ClientAvatar",System.currentTimeMillis()+15000);avatar=info.id;socket.setSoTimeout(2500);}
  void statusCheck()throws Exception{wire.write(1,ProtoLite.entityMessage(avatar,md5("statusCheck"),BsonLite.document("s","nextday")));Row row=until("statusCheckReply");check("ok".equals(BsonLite.stringValue(row.parameters,"r"))&&"nextday".equals(BsonLite.stringValue(row.parameters,"s")),"socket statusCheck ok");}
  void incDay()throws Exception{wire.write(1,ProtoLite.entityMessage(avatar,md5("incDayWhenNoActionVal"),BsonLite.EMPTY_DOCUMENT));}
  Row until(String target)throws Exception{ProtoLite.EntityMessage found=null;while(found==null){Wire.Frame frame=wire.read();if(frame.method!=5)continue;ProtoLite.EntityMessage m=ProtoLite.parseEntityMessage(frame.payload);if(target.equals(name(m)))found=m;}return new Row(target,found.parameters);}
  List<Row> collect(String target,long millis)throws Exception{List<Row> rows=new ArrayList<Row>();long deadline=System.currentTimeMillis()+millis;while(System.currentTimeMillis()<deadline){Wire.Frame frame=wire.read();if(frame.method!=5)continue;ProtoLite.EntityMessage m=ProtoLite.parseEntityMessage(frame.payload);rows.add(new Row(name(m),m.parameters));if(target.equals(name(m)))return rows;}throw new AssertionError("timeout waiting for "+target+" rows="+rows.size());}
  Drain drain(long millis)throws Exception{List<Row> rows=new ArrayList<Row>();long deadline=System.currentTimeMillis()+millis;boolean closed=false,timeout=false;while(System.currentTimeMillis()<deadline){try{Wire.Frame frame=wire.read();if(frame.method==5){ProtoLite.EntityMessage m=ProtoLite.parseEntityMessage(frame.payload);rows.add(new Row(name(m),m.parameters));}}catch(SocketTimeoutException e){timeout=true;break;}catch(EOFException e){closed=true;break;}}return new Drain(rows,closed,timeout);}
  byte[] profile()throws Exception{return Files.readAllBytes(file.toPath());}
  java.util.Properties progress()throws Exception{return tutorials.load(ACCOUNT).toProperties();}
  void normalize()throws Exception{LocalTutorialStore.Progress copy=LocalTutorialStore.Progress.fromProperties(tutorials.load(ACCOUNT).toProperties());store.load(ACCOUNT,copy);}
  public void close()throws Exception{try{wire.close();}catch(Throwable ignore){}gateway.close();thread.join(5000);for(int attempt=0;attempt<5&&Files.exists(root);attempt++){try(java.util.stream.Stream<Path>walk=Files.walk(root)){for(Path path:(Iterable<Path>)walk.sorted(Comparator.reverseOrder())::iterator)Files.deleteIfExists(path);}catch(Exception retry){}if(Files.exists(root))Thread.sleep(25);}if(Files.exists(root))try(java.util.stream.Stream<Path>walk=Files.walk(root)){for(Path path:(Iterable<Path>)walk.sorted(Comparator.reverseOrder())::iterator)Files.deleteIfExists(path);}}
 }
 static final class Drain{final List<Row>rows;final boolean closed,timeout;Drain(List<Row>rows,boolean closed,boolean timeout){this.rows=rows;this.closed=closed;this.timeout=timeout;}}
 static byte[] template(File assets)throws Exception{byte[]profile=Files.readAllBytes(new File(assets,"new_player.bson").toPath());profile=BsonLite.withAccountIdentity(profile,ACCOUNT,900704);byte[]week=BsonLite.documentValue(profile,"weeknum");week=BsonLite.withProfileInt(week,"w",1);week=BsonLite.withProfileInt(week,"d",0);profile=BsonLite.withProfileDocument(profile,"weeknum",week);byte[]city=BsonLite.documentValue(profile,"city");city=BsonLite.withProfileInt(city,"av",0);profile=BsonLite.withProfileDocument(profile,"city",city);byte[]std=BsonLite.documentValue(profile,"std");std=BsonLite.withProfileBool(std,"ff",false);return BsonLite.withProfileDocument(profile,"std",std);}
 static int day(byte[]p)throws Exception{return BsonLite.intValue(BsonLite.documentValue(p,"weeknum"),"d");}
 static int cityAv(byte[]p)throws Exception{return BsonLite.intValue(BsonLite.documentValue(p,"city"),"av");}
 static int cityInt(byte[]p,String key)throws Exception{return BsonLite.intValue(BsonLite.documentValue(p,"city"),key);}
 static boolean has(byte[]p,String key)throws Exception{return BsonLite.documentValue(p,key)!=null;}
 static boolean sameAll(byte[]a,byte[]b)throws Exception{return Objects.equals(BsonLite.messagePackValue(a,false),BsonLite.messagePackValue(b,false));}
 static void stabilize(Fixture f)throws Exception{for(int attempt=0;attempt<10;attempt++){long now=System.currentTimeMillis(),millis=now%1000;if(millis>100)Thread.sleep(1010-millis);f.normalize();if(System.currentTimeMillis()%1000<600)return;}throw new AssertionError("unable to stabilize profile second");}
  static boolean named(List<Row>rows,String name){for(Row r:rows)if(r.method.equals(name))return true;return false;}
 static int count(List<Row>rows,String name){int n=0;for(Row r:rows)if(r.method.equals(name))n++;return n;}
 public static void main(String[]args)throws Exception{
  File assets=new File(args[0]);Context prepareContext=new Context(assets,new AssetManager(assets));CoreDrawPolicy.prepare(prepareContext);HistoryDrawPolicy.prepare(prepareContext);SelectorPolicy.prepare(prepareContext);DynamicDrawPolicy.prepare(prepareContext);WishGateway.prepare(prepareContext);StoryMissionBridge.prepare(prepareContext);StoryCityBootstrap.prepare(prepareContext);TrialRetryGateway.prepare(prepareContext);OfflineMechanismGateway.prepare(prepareContext);
  JSONObject cases=new JSONObject();
  try(Fixture f=new Fixture(assets,false)){
   f.statusCheck();byte[]before=f.profile();check(day(before)==0&&cityAv(before)==0,"baseline precondition day 0/av 0");
   android.system.Os.failNextRename=true;f.incDay();Drain drain=f.drain(3000);List<Row>rows=drain.rows;
   check(!named(rows,"updateDay")&&!named(rows,"showDailySettlement")&&!named(rows,"showMessageStr"),"outer handleClient IOException sends no day reply");
   check(drain.closed&&!drain.timeout,"outer path closes the socket instead of unlocking the client");
   check(Arrays.equals(before,f.profile())&&day(f.profile())==0&&cityAv(f.profile())==0,"baseline failure leaves profile unchanged");
   JSONObject baseline=new JSONObject().put("reply_frames",rows.size()).put("closed",drain.closed).put("timeout",drain.timeout).put("day",day(f.profile())).put("city_av",cityAv(f.profile())).put("outer_path","dispatch IOException escapes handleClient -> lambda$run$5 close/log, no reply");cases.put("baseline_outer",baseline);
  }
  try(Fixture f=new Fixture(assets,true)){
   f.statusCheck();stabilize(f);byte[]before=f.profile();java.util.Properties beforeProgress=f.progress();check(day(before)==0&&cityAv(before)==0,"fixed precondition day 0/av 0");
   android.system.Os.failNextRename=true;f.incDay();List<Row>failed=f.collect("updateDay",8000);
   check(named(failed,"showMessageStr"),"fixed failure sends explicit message");check(count(failed,"updateDay")==1,"fixed failure sends exactly one updateDay");check(!named(failed,"showDailySettlement")&&!named(failed,"get_city_data_reply"),"fixed failure never sends settlement/reward projection");
   Row unlock=null;for(Row r:failed)if(r.method.equals("updateDay"))unlock=r;check(BsonLite.intValue(unlock.parameters,"d")==0,"fixed failure unlocks the original old day 0");
   byte[] afterFail=f.profile();boolean progressUnchanged=beforeProgress.equals(f.progress());check(progressUnchanged,"fixed failure does not mutate tutorial progress");check(day(afterFail)==0&&cityAv(afterFail)==0&&cityInt(afterFail,"dv")==cityInt(before,"dv")&&!has(afterFail,"q7EconomyCommit")&&sameAll(before,afterFail),"fixed failure leaves every persisted document field unchanged");
   f.incDay();List<Row>retry=f.collect("pullEventsReply",8000);Row update=null;for(Row r:retry)if(r.method.equals("updateDay"))update=r;check(update!=null&&BsonLite.intValue(update.parameters,"d")==1,"retry after fixed failure advances once");check(named(retry,"showDailySettlement")&&named(retry,"get_city_data_reply"),"retry publishes normal calendar replies");check(day(f.profile())==1&&cityAv(f.profile())==24,"retry persists day 1/city av 24");
   JSONObject fixed=new JSONObject().put("failure_frames",failed.size()).put("message",named(failed,"showMessageStr")).put("update_day",BsonLite.intValue(unlock.parameters,"d")).put("settlement",named(failed,"showDailySettlement")).put("day_after_failure",0).put("profile_bytes_changed",!Arrays.equals(before,afterFail)).put("profile_semantically_unchanged",sameAll(before,afterFail)).put("profile_exact_unchanged",sameAll(before,afterFail)).put("progress_unchanged",progressUnchanged).put("retry_update_day",BsonLite.intValue(update.parameters,"d")).put("retry_day",day(f.profile())).put("retry_city_av",cityAv(f.profile()));cases.put("fixed_provider",fixed);
  }
  try(Fixture f=new Fixture(assets,true)){
   f.statusCheck();byte[]before=f.profile();check(day(before)==0&&cityAv(before)==0,"uncertain precondition day 0/av 0");
   android.system.Os.failAfterRename=true;f.incDay();Drain drain=f.drain(3000);List<Row>rows=drain.rows;
   check(!named(rows,"updateDay")&&!named(rows,"showDailySettlement")&&!named(rows,"showMessageStr"),"uncertain commit does not publish old-day fallback or success replies");
   check(drain.closed&&!drain.timeout,"uncertain commit disconnects for resync");
   byte[] committed=f.profile();check(day(committed)==1&&cityAv(committed)==24,"after-rename failure actually persisted day 1/city av 24");
   f.connect();byte[]reloaded=f.profile();check(day(reloaded)==1,"reconnect sees committed day 1");
   JSONObject uncertain=new JSONObject().put("reply_frames",rows.size()).put("closed",drain.closed).put("timeout",drain.timeout).put("persisted_day",day(committed)).put("persisted_city_av",cityAv(committed)).put("reconnect_day",day(reloaded));cases.put("uncertain_commit",uncertain);
  }
  Files.write(Paths.get(args[1]),cases.toString(2).getBytes("UTF-8"));System.out.println("PASS real-socket day failure: outer path sends nothing/closes; provider seam unlocks old day + message without settlement, profile unchanged, retry advances; uncertain commit disconnects/resyncs");
 }
}
