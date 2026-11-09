package com.project7.localmanager;
import android.content.Context;import java.io.*;import java.lang.reflect.*;import java.nio.charset.StandardCharsets;import java.security.*;import java.util.*;
/** Named event-reset offline policy. Original Week primitives/Store own reset,
 * serialization and commit; original event runner owns white dialog/trace. */
public final class EventResetWeekPolicy {
 public static final String REQUEST="handleResetWeek",ASSET="project7_week_reset/catalog-v1.tsv",POLICY="event-reset-source-white-v1",SHA256="dc43ebe5d922443100f3aa8ec55151ecd5f94b6c8ed85b780d3248338d3d3b4a";
 private static final String META="q7EventReset";private static volatile Map<Integer,Row>catalog;
 private static final class Row {final int event,white;final boolean enabled;Row(String[]f){event=positive(f[1]);white=positive(f[2]);enabled=bit(f[3])&bit(f[4])&bit(f[5]);}}
 private EventResetWeekPolicy(){}
 /** Pure class-initializer hook: no assets, prepare state or WeekEngine access. */
 public static String[]weekMethods(String[]original){if(original==null)throw new IllegalArgumentException("Original week methods required");LinkedHashSet<String>names=new LinkedHashSet<>(Arrays.asList(original));if(names.contains(null))throw new IllegalArgumentException("Null week method");names.add(REQUEST);return names.toArray(new String[names.size()]);}
 public static void prepare(Context context)throws IOException{
  byte[]data;try(InputStream in=context.getAssets().open(ASSET)){ByteArrayOutputStream out=new ByteArrayOutputStream();byte[]buffer=new byte[4096];int n;while((n=in.read(buffer))!=-1){if(out.size()+n>16384)throw new IOException("Event reset catalog limit");out.write(buffer,0,n);}data=out.toByteArray();}
  if(!SHA256.equals(hash(data)))throw new IOException("Event reset catalog hash");for(byte b:data)if(b!=9&&b!=10&&(b<32||b>126))throw new IOException("Event reset catalog ASCII");
  String[]lines=new String(data,StandardCharsets.US_ASCII).split("\n",-1);if(!lines[0].equals("P7EVENTRESET\t1\t"+POLICY)||!lines[lines.length-1].isEmpty())throw new IOException("Event reset header");Map<Integer,Row>rows=new LinkedHashMap<>();
  try{LocalEventCatalog events=new LocalEventCatalog(context);
   for(int i=1;i<lines.length-1;i++){String[]f=lines[i].split("\t",-1);if(f.length!=6||!f[0].equals("E"))throw new IOException("Event reset row");Row row=new Row(f);if(rows.put(row.event,row)!=null)throw new IOException("Event reset duplicate");if(row.enabled){LocalEventCatalog.Event source=events.get(row.event),white=events.get(row.white);if(source==null||white==null||!source.release||!white.release)throw new IOException("Event reset original release mismatch "+row.event+"/"+row.white+" source="+(source!=null&&source.release)+" white="+(white!=null&&white.release));}}
  }catch(IllegalArgumentException invalid){throw new IOException("Event reset literal",invalid);}
  if(rows.size()!=4)throw new IOException("Event reset fixed row count");catalog=Collections.unmodifiableMap(rows);
 }
 public static LocalResourceEngine.Result apply(byte[]profile,LocalWeekCatalog weeks,LocalTutorialStore.Progress progress,String method,byte[]params){
  if(!REQUEST.equals(method))return LocalWeekEngine.apply(profile,weeks,progress,method,params);
  Map<Integer,Row>rows=catalog;if(rows==null)throw new IllegalStateException("Event reset catalog not prepared");LocalResourceEngine.Result result=new LocalResourceEngine.Result(profile);
  try{
   int event=event(params);Row row=rows.get(event);require(row!=null&&row.enabled,"当前离线版本未开放该周目重置。");
   Set<Integer>stay=set(field(weeks,"stay"));@SuppressWarnings("unchecked")Collection<Integer>foundation=(Collection<Integer>)staticField(LocalWeekEngine.class,"TUTORIAL_FOUNDATION");for(Row value:rows.values())require(!stay.contains(value.event)&&!foundation.contains(value.event),"重置事件目录与原保留规则冲突。");
   Integer week=BsonLite.intValue(BsonLite.documentValue(profile,"weeknum"),"w");require(week!=null&&week>=0,"当前周目数据无效。");
   @SuppressWarnings("unchecked")Map<Integer,Integer>resetEvents=(Map<Integer,Integer>)field(weeks,"resetEvents");Integer white=resetEvents.get(event);require(white!=null&&white==row.white,"原事件重置映射与固定来源不符。");
   @SuppressWarnings("unchecked")Map<Integer,Integer>entrances=(Map<Integer,Integer>)field(weeks,"entrances");Integer menu=null;for(Map.Entry<Integer,Integer>entry:entrances.entrySet())if(white.equals(entry.getValue())){require(menu==null,"白屏入口对应的原菜单不唯一。");menu=entry.getKey();}require(menu!=null&&menu>0,"原白屏路线入口不存在。");
   String current=(String)field(progress,"weekCommit");require(current!=null&&!current.isEmpty(),"当前周目状态尚未就绪。");byte[]transition=BsonLite.documentValue(profile,"q7WeekTransition"),meta=BsonLite.documentValue(transition,META);String target=BsonLite.stringValue(transition,"id");
   if(!set(field(progress,"completedEvents")).contains(event)){
    if(current.equals(target)&&REQUEST.equals(BsonLite.stringValue(transition,"method"))&&week.equals(BsonLite.intValue(transition,"week"))&&menu.equals(BsonLite.intValue(transition,"route"))&&matches(meta,row,target)&&(Boolean)call(LocalWeekEngine.class,"awaitingEntrance",new Class<?>[]{byte[].class,progress.getClass()},profile,progress)){reply(result);return result;}
    throw new Rejected("该事件当前尚未完成，或本次入口已经处理。");
   }
   String blocked=busy(profile,progress);require(blocked==null,blocked);
   byte[]pendingDelivery=BsonLite.documentValue(profile,"q7StoryPending");require(pendingDelivery==null||BsonLite.keys(pendingDelivery).isEmpty(),"请先完成剧情结果同步。");
   // Completed source facts authorize this fixed entrance. Never re-run their
   // now-stale date/CG triggers, fake completion, consume a black letter or grant.
   // This is an already-authorized event continuation, not a new Ask/menu
   // admission. Do not apply the unrelated menu ed/supports gates. Neither
   // global gate is changed; original resetProfile owns its temporary std.rt.
   Object candidate=call(LocalWeekEngine.class,"resetProgress",new Class<?>[]{progress.getClass(),LocalWeekCatalog.class,int.class,int.class},progress,weeks,week,white);
   byte[]next=(byte[])call(LocalWeekEngine.class,"resetProfile",new Class<?>[]{byte[].class,progress.getClass(),int.class,LocalWeekCatalog.class},profile,candidate,menu,weeks);String id=(String)field(candidate,"weekCommit");require(id!=null&&!id.equals(current),"原周目提交标识无效。");
   byte[]snapshot=(byte[])call(LocalWeekEngine.class,"serialize",new Class<?>[]{progress.getClass()},candidate);
   byte[]metadata=BsonLite.document("v",1,"event",event,"white",row.white,"sourceCommit",current,"catalog",SHA256,"policy",POLICY);
   result.profile=BsonLite.withProfileDocument(next,"q7WeekTransition",BsonLite.document("id",id,"week",week,"method",REQUEST,"route",menu,"progress",snapshot,META,metadata));reply(result);return result;
  }catch(Rejected negative){result.replies.add(new LocalResourceEngine.Reply("showMessageStr",BsonLite.document("m",negative.getMessage())));return result;}
  catch(ReflectiveOperationException mismatch){throw new IllegalStateException("Original event reset ABI mismatch",mismatch);}
 }
 private static boolean matches(byte[]meta,Row row,String target){
  String source=BsonLite.stringValue(meta,"sourceCommit");
  return Integer.valueOf(1).equals(BsonLite.intValue(meta,"v"))&&POLICY.equals(BsonLite.stringValue(meta,"policy"))&&SHA256.equals(BsonLite.stringValue(meta,"catalog"))&&Integer.valueOf(row.event).equals(BsonLite.intValue(meta,"event"))&&Integer.valueOf(row.white).equals(BsonLite.intValue(meta,"white"))&&source!=null&&!source.isEmpty()&&!source.equals(target);
 }
 /** Called again after the original effects closure/ACK has completed. */
 static String busy(byte[]profile,LocalTutorialStore.Progress progress)throws ReflectiveOperationException{
  if(BsonLite.documentValue(profile,"q7DreamPatrolCommit")!=null)return "请先恢复当前巡查请求。";
  if(Boolean.TRUE.equals(field(progress,"patrolRewardPending")))return "请先领取当前巡查结果。";
  byte[]battle=BsonLite.documentValue(profile,"q7Battle");if(battle!=null&&!BsonLite.keys(battle).isEmpty())return "请先完成当前战斗。";
  for(Integer active:set(field(progress,"processingEvents")))if(!(Boolean)call(LocalWeekEngine.class,"lambda$awaitingEntrance$0",new Class<?>[]{Integer.class},active))return "请先完成当前剧情。";
  return set(field(progress,"processingNewbees")).isEmpty()?null:"请先完成当前引导。";
 }
 private static void reply(LocalResourceEngine.Result result)throws ReflectiveOperationException{call(LocalWeekEngine.class,"replies",new Class<?>[]{LocalResourceEngine.Result.class,String.class},result,"handleResetWeekAsk");}
 private static int event(byte[]params)throws Rejected{try{require(params!=null&&BsonLite.keys(params).equals(Arrays.asList("e")),"重置请求格式无效。");Number n=BsonLite.numericValue(params,"e");require(n instanceof Integer||n instanceof Long,"重置事件必须为整数。");long id=n.longValue();require(id>0&&id<=Integer.MAX_VALUE&&Arrays.equals(params,BsonLite.document("e",n)),"重置事件参数无效。");return(int)id;}catch(IllegalArgumentException invalid){throw new Rejected("重置请求格式无效。");}}
 private static Object field(Object o,String name)throws ReflectiveOperationException{Field f=o.getClass().getDeclaredField(name);f.setAccessible(true);return f.get(o);}
 private static Object staticField(Class<?>c,String name)throws ReflectiveOperationException{Field f=c.getDeclaredField(name);f.setAccessible(true);return f.get(null);}
 private static Object call(Class<?>c,String name,Class<?>[]types,Object...args)throws ReflectiveOperationException{Method m=c.getDeclaredMethod(name,types);m.setAccessible(true);try{return m.invoke(null,args);}catch(InvocationTargetException e){Throwable cause=e.getCause();if(cause instanceof RuntimeException)throw(RuntimeException)cause;throw e;}}
 private static Class<?>type(String name)throws ClassNotFoundException{return Class.forName("com.project7.localmanager."+name);}
 @SuppressWarnings("unchecked")private static Set<Integer>set(Object v){return(Set<Integer>)v;}
 private static void require(boolean v,String reason)throws Rejected{if(!v)throw new Rejected(reason);}
 private static final class Rejected extends Exception{Rejected(String message){super(message);}}
 private static int positive(String text){int n=Integer.parseInt(text);if(n<=0)throw new IllegalArgumentException("Positive event");return n;}
 private static boolean bit(String text){if(!text.equals("0")&&!text.equals("1"))throw new IllegalArgumentException("Release flag");return text.equals("1");}
 private static String hash(byte[]data){try{StringBuilder out=new StringBuilder();for(byte b:MessageDigest.getInstance("SHA-256").digest(data))out.append(String.format(Locale.ROOT,"%02x",b&255));return out.toString();}catch(NoSuchAlgorithmException impossible){throw new AssertionError(impossible);}}
}
