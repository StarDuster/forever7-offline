package com.project7.localmanager;
import android.content.Context;import android.content.res.AssetManager;
import java.io.*;import java.lang.reflect.*;import java.nio.*;import java.nio.file.*;import java.util.*;

/** Original store/engine/effects/protocol, platform filesystem seams only. */
public final class RequestGatewayHost {
 static final String ACCOUNT="host_request_synthetic",METHOD="requestTriggerDaXuanWo";static final byte[]ID=new byte[12];
 static void check(boolean v,String m){if(!v)throw new AssertionError(m);}
 static Object get(Object owner,String n)throws Exception{Field f=owner.getClass().getDeclaredField(n);f.setAccessible(true);return f.get(owner);}
 static void set(Object owner,String n,Object value)throws Exception{Field f=owner.getClass().getDeclaredField(n);f.setAccessible(true);f.set(owner,value);}
 static byte[]md5(String s){return RequestEventCatalog.hash("MD5",s.getBytes(java.nio.charset.StandardCharsets.UTF_8));}
 static List<ProtoLite.EntityMessage>frames(byte[]wire)throws IOException{List<ProtoLite.EntityMessage>r=new ArrayList<>();ByteBuffer b=ByteBuffer.wrap(wire).order(ByteOrder.LITTLE_ENDIAN);while(b.hasRemaining()){int length=b.getInt();check(b.getShort()==5,"opcode5");byte[]data=new byte[length-2];b.get(data);r.add(ProtoLite.parseEntityMessage(data));}return r;}
 static boolean has(List<ProtoLite.EntityMessage>frames,String name){for(ProtoLite.EntityMessage f:frames)if(Arrays.equals(f.methodMd5,md5(name)))return true;return false;}
 static int callbacks(List<ProtoLite.EntityMessage>frames,int id){int count=0;for(ProtoLite.EntityMessage f:frames)if(Arrays.equals(f.methodMd5,md5("serverCallbackCarrier"))){check(BsonLite.intValue(f.parameters,"_cbid_")==id,"actual callback id");count++;}return count;}
 static boolean completion(List<ProtoLite.EntityMessage>frames,int event){for(ProtoLite.EntityMessage f:frames)if(Arrays.equals(f.methodMd5,md5("completeEventReplyEnd"))){Object v=BsonLite.messagePackValue(f.parameters,false);if(((Map<?,?>)v).containsValue(event))return true;}return false;}
 static final class Fixture implements AutoCloseable {
  final Path root;final LocalProfileStore store;final LocalTutorialStore tutorials;final LocalGatewayServer gateway;final LocalEventEngine engine;final LocalTutorialStore.Progress p;final File profile;
  Fixture(File assets,boolean cg)throws Exception{
   root=Files.createTempDirectory("p7-request-gateway-synthetic-");Files.createDirectories(root.resolve("profiles"));profile=root.resolve("profiles/"+ACCOUNT+".bson").toFile();
   Context context=new Context(root.toFile(),new AssetManager(assets));store=new LocalProfileStore(context);tutorials=new LocalTutorialStore(context);
   byte[]publicTemplate=Files.readAllBytes(new File(assets,"new_player.bson").toPath());Files.write(profile.toPath(),BsonLite.withAccountIdentity(publicTemplate,ACCOUNT,900001));
   p=LocalTutorialStore.Progress.fresh();p.initPrologue=false;p.inEmergency=false;p.weekIndex=3;p.weekCommit="host_request_cycle";p.availableEvents.clear();p.processingEvents.clear();p.completedEvents.add(1047);p.completedEvents.add(1004);
   byte[]raw=store.load(ACCOUNT,p);byte[]week=BsonLite.documentValue(raw,"weeknum");week=BsonLite.withProfileInt(week,"w",3);week=BsonLite.withProfileInt(week,"d",0);raw=BsonLite.withProfileDocument(raw,"weeknum",week);
   raw=BsonLite.withProfileArray(raw,"cgs",cg?Arrays.asList(281):Collections.emptyList());raw=BsonLite.withoutProfileKey(raw,"q7Battle");raw=BsonLite.withoutProfileKey(raw,"q7StoryPending");raw=BsonLite.withoutProfileKey(raw,"q7WeekResult");Files.write(profile.toPath(),raw);
   LocalEventCatalog graph=new LocalEventCatalog(new FileInputStream(new File(assets,"event_graph.tsv")));LocalNewbeeCatalog newbees=new LocalNewbeeCatalog(new ByteArrayInputStream(new byte[0]));
   engine=new LocalEventEngine(graph,newbees,p,0,raw,true);
   // Synthetic third-week idle fixture, not stock fresh prologue semantics.
   p.availableEvents.clear();p.processingEvents.clear();p.processingNewbees.clear();p.inEmergency=false;p.weekIndex=3;p.initPrologue=false;
   set(engine,"conditionPass",null);set(engine,"lastScanState",null);set(engine,"areaClick","7:3");set(engine,"clientOperation",2);
   tutorials.save(ACCOUNT,p);
   gateway=new LocalGatewayServer(0,null,store,tutorials,graph,newbees,null,null,(status,message)->{});
  }
  boolean call(OutputStream out,int id)throws Exception{return RequestEventGateway.handleDirect(gateway,out,ID,md5(METHOD),BsonLite.document("_cbid_",id),ACCOUNT,p,engine);}
  public void close()throws Exception{gateway.close();try(java.util.stream.Stream<Path>s=Files.walk(root)){for(Path path:(Iterable<Path>)s.sorted(Comparator.reverseOrder())::iterator)Files.delete(path);}}
 }
 public static void main(String[]args)throws Exception{
  Path temp=Files.createTempDirectory("p7-request-catalog-public-");Files.createDirectories(temp.resolve("offline"));Files.copy(Paths.get(args[1]),temp.resolve("offline/request-events.tsv"));Files.copy(Paths.get(args[0],"weeks.tsv"),temp.resolve("weeks.tsv"));String endingAsset=System.getProperty("p7.ending.asset");if(endingAsset==null)throw new IllegalStateException("p7.ending.asset missing");Files.copy(Paths.get(endingAsset),temp.resolve("offline/ending-trigger-v1.json"));RequestEventGateway.prepare(new Context(temp.toFile(),new AssetManager(temp.toFile())));Files.delete(temp.resolve("offline/request-events.tsv"));Files.delete(temp.resolve("offline/ending-trigger-v1.json"));Files.delete(temp.resolve("weeks.tsv"));Files.delete(temp.resolve("offline"));Files.delete(temp);
  File assets=new File(args[0]);
  if(System.getProperty("p7.history.assets")!=null)Class.forName("com.project7.localmanager.HistoryDrawPolicy").getMethod("prepare",Context.class).invoke(null,new Context(temp.toFile(),new AssetManager(assets)));
  Map<String,Object>cases=new LinkedHashMap<>();
  try(Fixture f=new Fixture(assets,true)){
   Properties initial=f.p.toProperties();Object pass=new LocalStoryConditionPass((byte[])get(f.engine,"profile"),f.p,true);set(f.engine,"conditionPass",pass);
   Method fork=RequestEventGateway.class.getDeclaredMethod("fork",LocalEventEngine.class,Object.class);fork.setAccessible(true);LocalEventEngine candidate=(LocalEventEngine)fork.invoke(null,f.engine,f.p);
   check(get(candidate,"progress")!=f.p&&get(candidate,"conditionPass")==null&&get(f.engine,"conditionPass")==pass,"fork caches isolated");
   check(get(candidate,"profile")!=get(f.engine,"profile")&&get(candidate,"eventBaseline")!=get(f.engine,"eventBaseline"),"fork arrays/sets isolated");check(f.p.toProperties().equals(initial),"constructor candidate restore does not mutate live");
   check(((LocalTutorialStore.Progress)get(candidate,"progress")).toProperties().equals(initial),"constructor admission has no premature Progress changes");
   Method scope=RequestEventGateway.class.getDeclaredMethod("noticeScope",String.class,Object.class,Object.class);scope.setAccessible(true);String key=(String)scope.invoke(null,METHOD,f.p,f.engine);
   Method enqueue=RequestEventGateway.class.getDeclaredMethod("enqueue",Object.class,String.class,Set.class);enqueue.setAccessible(true);enqueue.invoke(null,f.p,key,new LinkedHashSet<>(Arrays.asList(9002,9001)));
   f.tutorials.save(ACCOUNT,f.p);LocalTutorialStore.Progress reloaded=f.tutorials.load(ACCOUNT);
   Method notices=RequestEventGateway.class.getDeclaredMethod("notices",Object.class,String.class);notices.setAccessible(true);check(notices.invoke(null,reloaded,key).equals(Arrays.asList(9002,9001)),"singleton ordinal ledger retains order through original Store sorting");
   set(f.engine,"date",1);check(scope.invoke(null,METHOD,reloaded,f.engine).equals(key),"same-week cross-day retry preserves pending notice scope");
   reloaded.weekCommit="next_epoch";String next=(String)scope.invoke(null,METHOD,reloaded,f.engine);Method prune=RequestEventGateway.class.getDeclaredMethod("pruneStale",Object.class,String.class);prune.setAccessible(true);prune.invoke(null,reloaded,next);check(((List<?>)notices.invoke(null,reloaded,next)).isEmpty(),"stale epoch notices not replayed");
  }
  try(Fixture f=new Fixture(assets,true)){
   ByteArrayOutputStream out=new ByteArrayOutputStream();Properties before=f.p.toProperties();
   check(!RequestEventGateway.handleDirect(f.gateway,out,ID,md5("requestNotBound"),BsonLite.document("_cbid_",71),ACCOUNT,f.p,f.engine),"unknown direct stays original");check(out.size()==0&&f.p.toProperties().equals(before),"unknown no output/change");
   Object liveCompleted=f.p.completedEvents;byte[]profileBefore=Files.readAllBytes(f.profile.toPath());
   Method fileFor=LocalTutorialStore.class.getDeclaredMethod("fileFor",String.class);fileFor.setAccessible(true);File target=(File)fileFor.invoke(f.tutorials,ACCOUNT);File block=new File(target.getParentFile(),target.getName()+".tmp");check(block.mkdir(),"pre-save failure fixture");
   check(f.call(out,72),"known direct consumed");check(f.p.toProperties().equals(before)&&Arrays.equals(profileBefore,Files.readAllBytes(f.profile.toPath())),"save precommit live/profile unchanged");check(callbacks(frames(out.toByteArray()),72)==1&&has(frames(out.toByteArray()),"showMessageStr"),"save failure negative callback");check(block.delete(),"remove failure fixture");
   out.reset();check(f.call(out,73),"direct success consumed");List<ProtoLite.EntityMessage>first=frames(out.toByteArray());
   check(f.p.completedEvents.contains(417)&&f.p.eventCompletions.get(417)==1,"live adopted original completion");check(f.p.completedEvents==liveCompleted&&get(f.engine,"progress")==f.p,"live Progress/final set identity retained");
   check("7:3".equals(get(f.engine,"areaClick"))&&(Integer)get(f.engine,"clientOperation")==2,"full engine context retained");
   check(get(f.engine,"conditionPass")==null || get(get(f.engine,"conditionPass"),"progress")==f.p,"live condition pass never candidate");
   check(callbacks(first,73)==1&&!has(first,"requestTriggerDaXuanWoReply"),"real callback, no fabricated reply");
   cases.put("direct_success",capture(first));System.out.println("success methods="+names(first));check(completion(first,417),"real completeEventReplyEnd for event");
   out.reset();f.call(out,74);check(f.p.eventCompletions.get(417)==1&&callbacks(frames(out.toByteArray()),74)==1,"retry no second completion + callback");check(!completion(frames(out.toByteArray()),417),"successful local send ledger cleared; ordinary retry no new UI notice");
  }
  try(Fixture f=new Fixture(assets,true)){
   Properties before=f.p.toProperties();OutputStream disconnected=new OutputStream(){public void write(int value)throws IOException{throw new IOException("synthetic disconnected");}};
   try{f.call(disconnected,81);throw new AssertionError("disconnect expected");}catch(IOException expected){}
   check(f.p.completedEvents.contains(417)&&f.tutorials.load(ACCOUNT).completedEvents.contains(417),"post-save disconnect retains durable/live completion");
   ByteArrayOutputStream retry=new ByteArrayOutputStream();f.call(retry,82);check(f.p.eventCompletions.get(417)==1&&callbacks(frames(retry.toByteArray()),82)==1,"post-save retry completion once");LocalTutorialStore.Progress restored=f.tutorials.load(ACCOUNT);byte[]avatar=BsonLite.withTutorialProgress(f.store.load(ACCOUNT,restored),restored);byte[]eventTrigger=BsonLite.documentValue(avatar,"eventTrigger");check(BsonLite.intArrayValues(eventTrigger,"ecm").contains(417),"original reconnect projection completed state");cases.put("reconnect_eventTrigger_b64",Base64.getEncoder().encodeToString(eventTrigger));check(completion(frames(retry.toByteArray()),417),"durable notice replay after disconnect");cases.put("disconnect_retry",capture(frames(retry.toByteArray())));
  }
  try(Fixture f=new Fixture(assets,false)){
   ByteArrayOutputStream out=new ByteArrayOutputStream();Properties before=f.p.toProperties();f.call(out,91);check(f.p.toProperties().equals(before),"condition negative leaves live unchanged");check(has(frames(out.toByteArray()),"showMessageStr")&&callbacks(frames(out.toByteArray()),91)==1,"condition negative callback unlock");for(ProtoLite.EntityMessage message:frames(out.toByteArray()))if(Arrays.equals(message.methodMd5,md5("showMessageStr")))check("当前条件未满足。".equals(BsonLite.stringValue(message.parameters,"m")),"localized negative message");cases.put("condition_negative",capture(frames(out.toByteArray())));
  }
  try(Fixture f=new Fixture(assets,true)){
   android.system.Os.failAfter=true;ByteArrayOutputStream out=new ByteArrayOutputStream();f.call(out,92);
   check(f.p.completedEvents.contains(417)&&f.p.eventCompletions.get(417)==1&&callbacks(frames(out.toByteArray()),92)==1,"rename-after-save exception reconciled from original Store");
  }
  try(Fixture f=new Fixture(assets,true)){
   ByteArrayOutputStream out=new ByteArrayOutputStream(){boolean armed;
    public synchronized void write(byte[]b,int offset,int length){super.write(b,offset,length);try{if(!armed&&has(frames(toByteArray()),"pushEvents")){armed=true;android.system.Os.failBefore=true;}}catch(IOException partial){}}
   };
   try{f.call(out,93);throw new AssertionError("notice cleanup failure expected");}catch(IOException expected){}
   check(f.p.completedEvents.contains(417)&&f.p.eventCompletions.get(417)==1,"cleanup failure retains completed business state");
   check(f.p.eventConditions.keySet().stream().anyMatch(key->key.startsWith("q7RequestEventNotice:v2:")),"cleanup failure retains notice ledger");
   int money=LocalResourceEngine.value(Files.readAllBytes(f.profile.toPath()),"money");ByteArrayOutputStream retry=new ByteArrayOutputStream();f.call(retry,94);
   check(f.p.eventCompletions.get(417)==1&&LocalResourceEngine.value(Files.readAllBytes(f.profile.toPath()),"money")==money&&callbacks(frames(retry.toByteArray()),94)==1,"cleanup retry no rerun/reward + callback");
  }
  if(System.getProperty("p7.dispatch.prefix")!=null){
   try(Fixture f=new Fixture(assets,true)){
    Method direct=LocalGatewayServer.class.getDeclaredMethod("handleServiceRpc",OutputStream.class,byte[].class,byte[].class,byte[].class,String.class,LocalTutorialStore.Progress.class,LocalEventEngine.class);direct.setAccessible(true);
    ByteArrayOutputStream out=new ByteArrayOutputStream();check(Boolean.TRUE.equals(direct.invoke(f.gateway,out,ID,md5(METHOD),BsonLite.document("_cbid_",73),ACCOUNT,f.p,f.engine)),"actual direct dispatch consumed");
    List<ProtoLite.EntityMessage> messages=frames(out.toByteArray());check(completion(messages,417)&&callbacks(messages,73)==1&&!has(messages,"reliableRpcAck"),"actual ordinary producer: completion+carrier no ACK");cases.put("direct_dispatch",capture(messages));
    out.reset();Properties before=f.p.toProperties();check(Boolean.FALSE.equals(direct.invoke(f.gateway,out,ID,md5("requestNotBound"),BsonLite.EMPTY_DOCUMENT,ACCOUNT,f.p,f.engine)),"unknown direct preserves original false path");check(out.size()==0&&f.p.toProperties().equals(before),"unknown direct unchanged");
   }
   try(Fixture f=new Fixture(assets,true)){
    Method reliable=LocalGatewayServer.class.getDeclaredMethod("handleReliableRpc",OutputStream.class,byte[].class,byte[].class,String.class,LocalTutorialStore.Progress.class,LocalEventEngine.class,Set.class,Set.class,Map.class,Set.class);reliable.setAccessible(true);
    byte[]envelope=BsonLite.document("w",BsonLite.document("m",METHOD,"p",BsonLite.EMPTY_DOCUMENT,"r",1),"_cbid_",101);
    ByteArrayOutputStream out=new ByteArrayOutputStream();reliable.invoke(f.gateway,out,ID,envelope,ACCOUNT,f.p,f.engine,new HashSet<Integer>(),new HashSet<Integer>(),new HashMap<Integer,LocalPatrolEngine.Result>(),new HashSet<Integer>());
    List<ProtoLite.EntityMessage>messages=frames(out.toByteArray());check(!messages.isEmpty()&&Arrays.equals(messages.get(0).methodMd5,md5("reliableRpcAck")),"actual reliable ACK first");
    check(completion(messages,417)&&callbacks(messages,101)==1&&f.p.eventCompletions.get(417)==1,"actual reliable completion then callback");cases.put("reliable_dispatch",capture(messages));
    byte[]pull=BsonLite.document("w",BsonLite.document("m","pullEvents","p",BsonLite.EMPTY_DOCUMENT,"r",2),"_cbid_",102);out.reset();reliable.invoke(f.gateway,out,ID,pull,ACCOUNT,f.p,f.engine,new HashSet<Integer>(),new HashSet<Integer>(),new HashMap<Integer,LocalPatrolEngine.Result>(),new HashSet<Integer>());
    check(has(frames(out.toByteArray()),"pullEventsReply"),"original pullEvents reconciliation");cases.put("pull_events",capture(frames(out.toByteArray())));
   }
   System.out.println("PASS actual patched private direct/reliable dispatch: ordinary no ACK; reliable ACK first; both original completion+callback");
  }
  Files.write(Paths.get(args[2]),new org.json.JSONObject(cases).toString(2).getBytes("UTF-8"));
  System.out.println("PASS real gateway/store/effects/frame/callback chain; unknown/pre-save/publish-disconnect/retry/conditions");
 }
 static List<Map<String,String>>capture(List<ProtoLite.EntityMessage>frames){List<Map<String,String>>out=new ArrayList<>();for(ProtoLite.EntityMessage frame:frames)for(String name:new String[]{"completeEventReplyStart","completeEventReplyEnd","pushEvents","pullEventsReply","serverCallbackCarrier","showMessageStr"})if(Arrays.equals(frame.methodMd5,md5(name))){Map<String,String>row=new LinkedHashMap<>();row.put("method",name);row.put("parameters_b64",Base64.getEncoder().encodeToString(frame.parameters));out.add(row);}return out;}
 static List<String>names(List<ProtoLite.EntityMessage>frames){List<String>out=new ArrayList<>();for(ProtoLite.EntityMessage f:frames){String name="other";for(String s:new String[]{"completeEventReplyStart","completeEventReplyEnd","pushEvents","pullEventsReply","serverCallbackCarrier","showMessageStr"})if(Arrays.equals(f.methodMd5,md5(s)))name=s;out.add(name);}return out;}
}
