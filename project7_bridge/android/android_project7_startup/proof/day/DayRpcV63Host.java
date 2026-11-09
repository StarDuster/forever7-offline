package com.project7.localmanager;
import android.content.*;import android.content.res.*;import java.io.*;import java.lang.reflect.*;import java.nio.*;import java.nio.file.*;import java.security.*;import java.util.*;import org.json.*;
/** Actual v63 OWN + f81b fixed-manager day RPC host: real Reliable/Calendar entries, Store, replies,
 *  atomic persistence, reload, duplicate request and writer-failure purity. No D8/APK/native. */
public final class DayRpcV63Host {
 static final String ACCOUNT="host_day_v63";static final byte[] EID=new byte[12];
 static final List<String>KNOWN=Arrays.asList("reliableRpcAck","statusCheckReply","showMessageStr","updateDay","showDailySettlement","get_city_data_reply","syncHeroMgrData","syncAllIntelligence","updateCurFatigueValue","updateFriendlyValue","pullEventsReply","serverCallbackCarrier");
 static void check(boolean b,String m){if(!b)throw new AssertionError(m);}
 static byte[]md5(String s)throws Exception{return MessageDigest.getInstance("MD5").digest(s.getBytes("UTF-8"));}
 static Object invoke(Object o,String name,Class<?>[]types,Object...args)throws Exception{Method m=o.getClass().getDeclaredMethod(name,types);m.setAccessible(true);try{return m.invoke(o,args);}catch(InvocationTargetException e){if(e.getCause() instanceof Exception)throw(Exception)e.getCause();throw e;}}
 static final class Fixture implements AutoCloseable {
  final Path root,file;final Context context;final LocalProfileStore store;final LocalTutorialStore tutorials;final LocalGatewayServer gateway;final LocalEventCatalog graph;LocalTutorialStore.Progress p;LocalEventEngine engine;
  Fixture(File assets,int day,int actionValue,boolean patrolPending)throws Exception{
   root=Files.createTempDirectory("p7-day-rpc-v63-");Files.createDirectory(root.resolve("profiles"));file=root.resolve("profiles/"+ACCOUNT+".bson");
   context=new Context(root.toFile(),new AssetManager(assets));store=new LocalProfileStore(context);tutorials=new LocalTutorialStore(context);
   byte[]raw=BsonLite.withAccountIdentity(Files.readAllBytes(new File(assets,"new_player.bson").toPath()),ACCOUNT,900004);
   byte[]weeknum=BsonLite.documentValue(raw,"weeknum");weeknum=BsonLite.withProfileInt(weeknum,"w",1);weeknum=BsonLite.withProfileInt(weeknum,"d",day);raw=BsonLite.withProfileDocument(raw,"weeknum",weeknum);
   byte[]city=BsonLite.documentValue(raw,"city");city=BsonLite.withProfileInt(city,"av",actionValue);raw=BsonLite.withProfileDocument(raw,"city",city);
   byte[]std=BsonLite.documentValue(raw,"std");std=BsonLite.withProfileBool(std,"ff",false);raw=BsonLite.withProfileDocument(raw,"std",std);
   Files.write(file,raw);
   p=LocalTutorialStore.Progress.fresh();p.weekCommit="host_day_v63_week";p.weekIndex=1;p.initPrologue=false;p.patrolActions=-1;p.sandglassActions=-1;p.completedEvents.clear();p.eventConditions.clear();
   graph=new LocalEventCatalog(new FileInputStream(new File(assets,"event_graph.tsv")));LocalNewbeeCatalog nb=new LocalNewbeeCatalog(new ByteArrayInputStream(new byte[0]));engine=new LocalEventEngine(graph,nb,p,0,raw,true);p.availableEvents.clear();p.processingEvents.clear();p.processingNewbees.clear();p.inEmergency=false;p.status="city";p.patrolRewardPending=patrolPending;tutorials.save(ACCOUNT,p);
   gateway=new LocalGatewayServer(0,null,store,tutorials,graph,nb,null,new LocalPatrolCatalog(context),(a,b)->{});
  }
  ByteArrayOutputStream reliable(String method,byte[]parameters,int seq,int cbid)throws Exception{ByteArrayOutputStream out=new ByteArrayOutputStream();invoke(gateway,"handleReliableRpc",new Class<?>[]{OutputStream.class,byte[].class,byte[].class,String.class,LocalTutorialStore.Progress.class,LocalEventEngine.class,Set.class,Set.class,Map.class,Set.class},out,EID,BsonLite.document("w",BsonLite.document("m",method,"p",parameters,"r",seq),"_cbid_",cbid),ACCOUNT,p,engine,new HashSet<Integer>(),new HashSet<Integer>(),new HashMap<Integer,LocalPatrolEngine.Result>(),new HashSet<Integer>());return out;}
  ByteArrayOutputStream calendar()throws Exception{ByteArrayOutputStream out=new ByteArrayOutputStream();invoke(gateway,"handleCalendar",new Class<?>[]{OutputStream.class,byte[].class,String.class,LocalTutorialStore.Progress.class,LocalEventEngine.class,String.class},out,EID,ACCOUNT,p,engine,"incDayWhenNoActionVal");return out;}
  byte[] reload()throws Exception{LocalProfileStore fresh=new LocalProfileStore(context);LocalTutorialStore.Progress copy=LocalTutorialStore.Progress.fresh();copy.weekIndex=1;copy.initPrologue=false;copy.inEmergency=false;copy.status="city";return fresh.load(ACCOUNT,copy);}
  public void close()throws Exception{gateway.close();try(java.util.stream.Stream<Path>s=Files.walk(root)){for(Path v:(Iterable<Path>)s.sorted(Comparator.reverseOrder())::iterator)Files.delete(v);}}
 }
 static List<ProtoLite.EntityMessage>frames(byte[]wire)throws Exception{List<ProtoLite.EntityMessage>all=new ArrayList<>();ByteBuffer b=ByteBuffer.wrap(wire).order(ByteOrder.LITTLE_ENDIAN);while(b.hasRemaining()){int n=b.getInt();check(b.getShort()==5,"original wire opcode");byte[]v=new byte[n-2];b.get(v);all.add(ProtoLite.parseEntityMessage(v));}return all;}
 static String method(ProtoLite.EntityMessage f)throws Exception{for(String s:KNOWN)if(Arrays.equals(f.methodMd5,md5(s)))return s;return "other";}
 static int count(List<ProtoLite.EntityMessage>frames,String name)throws Exception{int n=0;for(ProtoLite.EntityMessage f:frames)if(Arrays.equals(f.methodMd5,md5(name)))n++;return n;}
 static ProtoLite.EntityMessage one(List<ProtoLite.EntityMessage>frames,String name)throws Exception{ProtoLite.EntityMessage found=null;for(ProtoLite.EntityMessage f:frames)if(Arrays.equals(f.methodMd5,md5(name))){check(found==null,"duplicate "+name);found=f;}check(found!=null,"missing "+name);return found;}
 static JSONArray capture(byte[]wire)throws Exception{JSONArray all=new JSONArray();for(ProtoLite.EntityMessage f:frames(wire)){String name=method(f);if(!"other".equals(name))all.put(new JSONObject().put("method",name).put("parameters_b64",Base64.getEncoder().encodeToString(f.parameters)));}return all;}
 static int unknown(byte[]wire)throws Exception{int n=0;for(ProtoLite.EntityMessage f:frames(wire))if("other".equals(method(f)))n++;return n;}
 static ProtoLite.EntityMessage firstUnknown(byte[]wire)throws Exception{for(ProtoLite.EntityMessage f:frames(wire))if("other".equals(method(f)))return f;return null;}
 static String unknownKeys(byte[]wire)throws Exception{ProtoLite.EntityMessage f=firstUnknown(wire);return f==null?"[]":BsonLite.keys(f.parameters).toString();}
 static String unknownMd5(byte[]wire)throws Exception{ProtoLite.EntityMessage f=firstUnknown(wire);if(f==null)return "";StringBuilder s=new StringBuilder();for(byte b:f.methodMd5)s.append(String.format("%02x",b&255));return s.toString();}
 static String unknownB64(byte[]wire)throws Exception{ProtoLite.EntityMessage f=firstUnknown(wire);return f==null?"":Base64.getEncoder().encodeToString(f.parameters);}
 static int index(List<ProtoLite.EntityMessage>frames,String name)throws Exception{for(int i=0;i<frames.size();i++)if(Arrays.equals(frames.get(i).methodMd5,md5(name)))return i;return -1;}
 static JSONObject wire(String requestMethod,byte[]requestParameters,byte[]wire)throws Exception{return new JSONObject().put("request",new JSONObject().put("method",requestMethod).put("parameters_b64",Base64.getEncoder().encodeToString(requestParameters))).put("frames",capture(wire)).put("unknown_frames",unknown(wire)).put("unknown_first_keys",unknownKeys(wire)).put("unknown_first_md5",unknownMd5(wire)).put("unknown_first_b64",unknownB64(wire));}
 static int day(byte[]profile)throws Exception{return BsonLite.intValue(BsonLite.documentValue(profile,"weeknum"),"d");}
 static int cityInt(byte[]profile,String key)throws Exception{return BsonLite.intValue(BsonLite.documentValue(profile,"city"),key);}
 static boolean cityBool(byte[]profile,String key)throws Exception{return Boolean.TRUE.equals(BsonLite.boolValue(BsonLite.documentValue(profile,"city"),key));}
 static boolean has(byte[]profile,String key)throws Exception{return BsonLite.documentValue(profile,key)!=null;}

 static boolean cityWithoutJpvt(byte[]a,byte[]b)throws Exception{return Arrays.equals(BsonLite.withoutProfileKey(a,"jpvt"),BsonLite.withoutProfileKey(b,"jpvt"));}
 static boolean boundedCityStable(byte[]a,byte[]b,long start,long end)throws Exception{
  if(a==null||b==null||!cityWithoutJpvt(a,b))return false;
  Number ta=BsonLite.numericValue(a,"jpvt"),tb=BsonLite.numericValue(b,"jpvt");if(ta==null||tb==null)return false;
  long v=tb.longValue();return v>=start&&v<=end;
 }
 static void comparisonRegression()throws Exception{
  byte[] powerDate=BsonLite.document("q7powerDay","2026-11-05");
  check(samePowerDay(powerDate,powerDate),"power date exact comparison accepts same string");
  check(!samePowerDay(powerDate,BsonLite.document("q7powerDay","2026-11-06")),"power date rejects changed string");
  check(!samePowerDay(powerDate,BsonLite.EMPTY_DOCUMENT),"power date rejects missing field");
  byte[] base=BsonLite.document("jpvt",100,"av",24,"label","same","nested",BsonLite.document("n",1));
  check(boundedCityStable(base,base,100,100),"comparison accepts identical city");
  check(boundedCityStable(base,BsonLite.withProfileInt(base,"jpvt",101),100,101),"comparison accepts jpvt at inclusive end");
  check(!boundedCityStable(base,BsonLite.withProfileInt(base,"jpvt",99),100,101),"comparison rejects jpvt below start");
  check(!boundedCityStable(base,BsonLite.withProfileInt(base,"jpvt",102),100,101),"comparison rejects jpvt above end");
  check(!boundedCityStable(base,BsonLite.withProfileInt(base,"av",25),100,101),"comparison rejects action value change");
  check(!boundedCityStable(base,BsonLite.document("jpvt",100,"av",24,"label","different","nested",BsonLite.document("n",1)),100,101),"comparison rejects string change");
  check(!boundedCityStable(base,BsonLite.withProfileInt(base,"extra",1),100,101),"comparison rejects added key");
  check(!boundedCityStable(base,BsonLite.withoutProfileKey(base,"label"),100,101),"comparison rejects removed key");
  check(!boundedCityStable(base,BsonLite.withProfileDocument(base,"nested",BsonLite.document("n",2)),100,101),"comparison rejects nested change");
  check(!boundedCityStable(base,BsonLite.withoutProfileKey(base,"jpvt"),100,101),"comparison rejects missing timestamp");
  System.out.println("PASS duplicate comparison regression: scalar, keys, nested data and inclusive timestamp bounds");
 }
 static boolean samePowerDay(byte[]a,byte[]b)throws Exception{
  String x=BsonLite.stringValue(a,"q7powerDay"),y=BsonLite.stringValue(b,"q7powerDay");
  return x!=null&&x.equals(y);
 }
 static void duplicateStable(byte[]a,byte[]b,long start,long end)throws Exception{
  for(String field:new String[]{"weeknum","q7EconomyCommit"}){byte[]x=BsonLite.documentValue(a,field),y=BsonLite.documentValue(b,field);check(Arrays.equals(x,y),"duplicate incDay keeps "+field+" exact");}
  byte[]ca=BsonLite.documentValue(a,"city"),cb=BsonLite.documentValue(b,"city");
  check(boundedCityStable(ca,cb,start,end),"duplicate jpvt within inclusive request epoch bounds and all other city fields exact");
  check(samePowerDay(a,b),"duplicate keeps root q7powerDay exact");
  check(cityInt(a,"jpv")==240&&cityInt(b,"jpv")==240,"bounded timestamp policy only applies at full power");
  check(day(b)==1,"duplicate incDay keeps day1");
 }
 static void duplicateExact(byte[]a,byte[]b)throws Exception{
  for(String field:new String[]{"weeknum","city","q7EconomyCommit"})check(Arrays.equals(BsonLite.documentValue(a,field),BsonLite.documentValue(b,field)),"duplicate keeps "+field+" byte-exact");
  check(samePowerDay(a,b),"partial duplicate keeps root power day exact");
  check(day(b)==1,"duplicate exact keeps day1");
 }
 static void setCity(Path file,int jpv,int jpvt,int mjpv,String powerDay)throws Exception{
  byte[]raw=Files.readAllBytes(file);byte[]city=BsonLite.documentValue(raw,"city");
  city=BsonLite.withProfileInt(city,"jpv",jpv);city=BsonLite.withProfileInt(city,"jpvt",jpvt);city=BsonLite.withProfileInt(city,"mjpv",mjpv);
  raw=BsonLite.withProfileDocument(raw,"city",city);
  raw=BsonLite.withProfileString(raw,"q7powerDay",powerDay);
  Files.write(file,raw);
 }
 public static void main(String[]args)throws Exception{
  comparisonRegression();
  File assets=new File(args[0]);Context prepareContext=new Context(assets,new AssetManager(assets));CoreDrawPolicy.prepare(prepareContext);HistoryDrawPolicy.prepare(prepareContext);SelectorPolicy.prepare(prepareContext);DynamicDrawPolicy.prepare(prepareContext);WishGateway.prepare(prepareContext);StoryMissionBridge.prepare(prepareContext);StoryCityBootstrap.prepare(prepareContext);TrialRetryGateway.prepare(prepareContext);OfflineMechanismGateway.prepare(prepareContext);
  JSONObject cases=new JSONObject();
  try(Fixture f=new Fixture(assets,0,0,false)){
   byte[]before=Files.readAllBytes(f.file);check(day(before)==0,"legal precondition starts at stock day 0");check(cityInt(before,"av")==0,"legal precondition has no action power");check(!has(before,"q7EconomyCommit"),"target result is not pre-seeded");
   ByteArrayOutputStream status=f.reliable("statusCheck",BsonLite.document("s","nextday"),1,41);byte[]statusWire=status.toByteArray();List<ProtoLite.EntityMessage>sf=frames(statusWire);
   check(method(sf.get(0)).equals("reliableRpcAck")&&index(sf,"statusCheckReply")>0&&index(sf,"serverCallbackCarrier")>index(sf,"statusCheckReply"),"reliable statusCheck ACK then typed reply then callback");check(count(sf,"statusCheckReply")==1,"one typed statusCheckReply");check(count(sf,"showMessageStr")==0,"unblocked statusCheck has no message");check(count(sf,"updateDay")==0,"statusCheck is a permission check, not an advance");
   ProtoLite.EntityMessage reply=one(sf,"statusCheckReply");check("ok".equals(BsonLite.stringValue(reply.parameters,"r"))&&"nextday".equals(BsonLite.stringValue(reply.parameters,"s")),"statusCheckReply r=ok,s=nextday");check(Arrays.equals(BsonLite.keys(reply.parameters).toArray(new String[0]),new String[]{"r","s"}),"statusCheckReply keeps original r,s order");
   byte[]afterStatus=Files.readAllBytes(f.file);check(day(afterStatus)==0&&cityInt(afterStatus,"av")==0,"statusCheck does not advance or spend");check(Arrays.equals(BsonLite.documentValue(before,"weeknum"),BsonLite.documentValue(afterStatus,"weeknum")),"statusCheck leaves persisted stock day document untouched");check(cityInt(afterStatus,"av")==0&&cityInt(afterStatus,"dv")==0&&!has(afterStatus,"q7EconomyCommit"),"statusCheck leaves persisted city day/economy state untouched");
   ByteArrayOutputStream duplicateStatus=f.reliable("statusCheck",BsonLite.document("s","nextday"),2,42);ProtoLite.EntityMessage duplicateReply=one(frames(duplicateStatus.toByteArray()),"statusCheckReply");check("ok".equals(BsonLite.stringValue(duplicateReply.parameters,"r"))&&day(Files.readAllBytes(f.file))==0,"duplicate statusCheck is read-only and idempotent");
   JSONObject statusCase=wire("statusCheck",BsonLite.document("s","nextday"),statusWire);statusCase.put("duplicate_frames",capture(duplicateStatus.toByteArray()));statusCase.put("day_before",0).put("day_after",0);cases.put("status_check",statusCase);
  }
  try(Fixture f=new Fixture(assets,0,0,false)){
   byte[]before=Files.readAllBytes(f.file);check(day(before)==0&&cityInt(before,"av")==0&&!has(before,"q7EconomyCommit"),"calendar legal precondition is day 0 with empty action power and no receipt");
   ByteArrayOutputStream calendar=f.calendar();byte[]calendarWire=calendar.toByteArray();List<ProtoLite.EntityMessage>cf=frames(calendarWire);
   check(count(cf,"showMessageStr")==0,"accepted calendar has no rejection message");check(count(cf,"updateDay")==1,"calendar emits exactly one updateDay");check(index(cf,"get_city_data_reply")<index(cf,"updateDay")&&index(cf,"updateDay")<index(cf,"showDailySettlement"),"original city state precedes updateDay and settlement");ProtoLite.EntityMessage update=one(cf,"updateDay");check(BsonLite.intValue(update.parameters,"d")==1,"original updateDay carries advanced stock day 1");
   ProtoLite.EntityMessage settlement=one(cf,"showDailySettlement");check(BsonLite.intValue(BsonLite.documentValue(settlement.parameters,"c"),"rsv")==0&&BsonLite.intValue(BsonLite.documentValue(settlement.parameters,"l"),"rsv")==0,"showDailySettlement carries original c/l review");check(Arrays.equals(BsonLite.keys(settlement.parameters).toArray(new String[0]),new String[]{"c","l"}),"showDailySettlement keeps original c,l order");
   ProtoLite.EntityMessage cityReply=one(cf,"get_city_data_reply");check(BsonLite.intValue(BsonLite.documentValue(cityReply.parameters,"cd"),"av")==24,"get_city_data_reply exposes reset action power 24");check(count(cf,"pullEventsReply")==1,"accepted calendar publishes original pullEventsReply");
   byte[]after=Files.readAllBytes(f.file);check(day(after)==1,"persisted weeknum.d advances 0 to 1");check(BsonLite.intValue(BsonLite.documentValue(after,"weeknum"),"w")==1,"persisted stock week is unchanged");check(cityInt(after,"av")==24,"persisted city action power resets to 24");check(cityInt(after,"dvc")==0&&cityInt(after,"pn")==1&&!cityBool(after,"uc"),"persisted city daily markers dvc/pn/uc are stock values");check(has(after,"q7EconomyCommit"),"persisted stock economy receipt exists");byte[]commit=BsonLite.documentValue(after,"q7EconomyCommit");check(BsonLite.intValue(commit,"av")==24&&BsonLite.intValue(commit,"sgw")==0&&BsonLite.intValue(commit,"pn")==0&&BsonLite.intValue(commit,"scene")==0,"stock receipt records av/sgw/pn/scene");check(!Arrays.equals(before,after),"calendar really persisted the advanced image");
   byte[]loaded=f.reload();check(day(loaded)==1,"reload returns persisted stock day 1");check(cityInt(loaded,"av")==24&&cityInt(loaded,"dvc")==0&&cityInt(loaded,"pn")==1&&!cityBool(loaded,"uc"),"reload returns persisted city day state");check(BsonLite.intValue(BsonLite.documentValue(loaded,"q7EconomyCommit"),"av")==24,"reload returns persisted stock economy receipt");
   byte[]afterFirst=Files.readAllBytes(f.file);long epochStart=System.currentTimeMillis()/1000;ByteArrayOutputStream duplicate=f.calendar();long epochEnd=System.currentTimeMillis()/1000;List<ProtoLite.EntityMessage>df=frames(duplicate.toByteArray());check(count(df,"showMessageStr")==1,"duplicate incDay is rejected by the stock action guard");check(count(df,"updateDay")==1&&BsonLite.intValue(one(df,"updateDay").parameters,"d")==1,"duplicate incDay republishes same stock day for the original UI unlock");check(count(df,"showDailySettlement")==0,"duplicate incDay does not replay the settlement");byte[] afterDuplicate=Files.readAllBytes(f.file);duplicateStable(afterFirst,afterDuplicate,epochStart,epochEnd);
   JSONObject calendarCase=wire("incDayWhenNoActionVal",BsonLite.EMPTY_DOCUMENT,calendarWire);calendarCase.put("duplicate_frames",capture(duplicate.toByteArray())).put("day_before",0).put("day_after",1).put("city_av_after",24).put("reload_day",day(loaded)).put("reload_city_av",24).put("duplicate_semantically_identical",true);cases.put("calendar",calendarCase);
  }
  try(Fixture f=new Fixture(assets,1,24,false)){
   f.calendar();int now=(int)(System.currentTimeMillis()/1000);setCity(f.file,240,now-1000,240,new java.text.SimpleDateFormat("yyyy-MM-dd",Locale.ROOT).format(new Date()));byte[]before=Files.readAllBytes(f.file);
   long start=System.currentTimeMillis()/1000;ByteArrayOutputStream dup=f.calendar();long end=System.currentTimeMillis()/1000;byte[]after=Files.readAllBytes(f.file);
   duplicateStable(before,after,start,end);check(cityInt(after,"jpv")==240,"full recovery keeps jpv 240");cases.put("recovery_full",new JSONObject().put("jpvt_before",cityInt(before,"jpvt")).put("jpvt_after",cityInt(after,"jpvt")).put("start",start).put("end",end));
  }
  try(Fixture f=new Fixture(assets,1,24,false)){
   f.calendar();int now=(int)(System.currentTimeMillis()/1000);String today=new java.text.SimpleDateFormat("yyyy-MM-dd",Locale.ROOT).format(new Date());setCity(f.file,100,now-10,240,today);
   Thread.sleep(1100);byte[]before=Files.readAllBytes(f.file);ByteArrayOutputStream dup=f.calendar();byte[]after=Files.readAllBytes(f.file);
   duplicateExact(before,after);cases.put("recovery_partial",new JSONObject().put("jpvt",cityInt(after,"jpvt")).put("jpv",cityInt(after,"jpv")));
  }
  try(Fixture f=new Fixture(assets,0,0,false)){
   byte[]before=Files.readAllBytes(f.file);Properties beforeProgress=f.p.toProperties();android.system.Os.failNextRename=true;ByteArrayOutputStream failed=new ByteArrayOutputStream();Exception thrown=null;try{invoke(f.gateway,"handleCalendar",new Class<?>[]{OutputStream.class,byte[].class,String.class,LocalTutorialStore.Progress.class,LocalEventEngine.class,String.class},failed,EID,ACCOUNT,f.p,f.engine,"incDayWhenNoActionVal");}catch(Exception e){thrown=e;}
   check(thrown instanceof IOException,"stock writer failure propagates");check(failed.size()==0,"writer failure emits no reply frames");check(Arrays.equals(before,Files.readAllBytes(f.file)),"writer failure leaves the profile byte-identical");check(day(Files.readAllBytes(f.file))==0,"writer failure keeps stock day 0");check(beforeProgress.equals(f.p.toProperties()),"writer failure does not mutate tutorial progress");
   android.system.Os.failNextRename=false;ByteArrayOutputStream retried=f.calendar();List<ProtoLite.EntityMessage>rf=frames(retried.toByteArray());check(count(rf,"updateDay")==1&&BsonLite.intValue(one(rf,"updateDay").parameters,"d")==1,"retry after writer failure advances once");check(day(Files.readAllBytes(f.file))==1,"retry persists day 1 with no poisoned half-state");
   JSONObject failureCase=wire("incDayWhenNoActionVal",BsonLite.EMPTY_DOCUMENT,failed.toByteArray());failureCase.put("retry_frames",capture(retried.toByteArray())).put("day_after_failure",0).put("day_after_retry",1);cases.put("writer_failure",failureCase);
  }
  try(Fixture f=new Fixture(assets,0,0,true)){
   byte[]before=Files.readAllBytes(f.file);ByteArrayOutputStream blocked=f.reliable("statusCheck",BsonLite.document("s","nextday"),3,43);List<ProtoLite.EntityMessage>bf=frames(blocked.toByteArray());ProtoLite.EntityMessage reply=one(bf,"statusCheckReply");check("blocked".equals(BsonLite.stringValue(reply.parameters,"r"))&&"nextday".equals(BsonLite.stringValue(reply.parameters,"s")),"pending patrol statusCheck returns typed blocked reply");check(count(bf,"showMessageStr")==1,"blocked statusCheck emits original message");check(count(bf,"updateDay")==0,"blocked statusCheck does not publish a day change");byte[]after=Files.readAllBytes(f.file);check(day(after)==0&&Arrays.equals(BsonLite.documentValue(before,"weeknum"),BsonLite.documentValue(after,"weeknum")),"blocked statusCheck leaves persisted stock day untouched");JSONObject blockedCase=wire("statusCheck",BsonLite.document("s","nextday"),blocked.toByteArray());blockedCase.put("day_before",0).put("day_after",0);cases.put("status_check_blocked",blockedCase);
  }
  Files.write(Paths.get(args[1]),cases.toString(2).getBytes("UTF-8"));System.out.println("PASS v63 real Reliable statusCheck + real handleCalendar incDay + stock Store replies/day/city/receipt + reload + duplicate guard + writer-failure purity");
 }
}
