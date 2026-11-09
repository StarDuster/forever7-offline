package com.project7.localmanager;
import android.content.Context;
import java.io.*;import java.lang.reflect.*;import java.nio.charset.StandardCharsets;import java.security.*;import java.util.*;
/** Fixed640 selector roster/leaf resolution. Stock choose/grant/Store own BSON. */
public final class SelectorPolicy {
 public static final String POLICY="fixed640-shared-selector-roster-v1";
 public static final String ASSET="project7_selector/catalog-v1.tsv";
 public static final String SHA256="40a42441c3e55a179c931a4cb5e70a4e6e94e0913f4ef1eb654354a72341b6d7";
 private static volatile Catalog snapshot;
 private static final Map<LocalResourceCatalog.Pool,Integer> owned=Collections.synchronizedMap(new WeakHashMap<LocalResourceCatalog.Pool,Integer>());
 private SelectorPolicy(){}
 private static final class Item {final int pool,sub;Item(int p,int s){pool=p;sub=s;}}
 private static final class Catalog {
  final Map<Integer,Item>items;final Map<Integer,Integer>epochs;final List<Integer>s,a;
  Catalog(Map<Integer,Item>i,Map<Integer,Integer>e,List<Integer>s,List<Integer>a){items=Collections.unmodifiableMap(new HashMap<>(i));epochs=Collections.unmodifiableMap(new HashMap<>(e));this.s=Collections.unmodifiableList(new ArrayList<>(s));this.a=Collections.unmodifiableList(new ArrayList<>(a));}
 }
 private static void need(boolean b,String code)throws IOException{if(!b)throw new IOException("Selector "+code);}
 private static void cancelled()throws InterruptedIOException{if(Thread.currentThread().isInterrupted())throw new InterruptedIOException("Selector CANCELLED");}
 private static Catalog ready()throws IOException{Catalog c=snapshot;need(c!=null,"NOT_PREPARED");return c;}
 private static RuntimeException fail(Exception e){if(e instanceof IllegalArgumentException)return (IllegalArgumentException)e;if(e instanceof ArithmeticException)return (ArithmeticException)e;return new IllegalArgumentException("自选奖励数据校验失败，请重新进入卡池。",e);}
 public static void prepare(Context context)throws Exception{try(InputStream in=context.getAssets().open(ASSET)){prepareStream(in);}}
 static void prepareStream(InputStream in)throws Exception {
  ByteArrayOutputStream out=new ByteArrayOutputStream();byte[]buffer=new byte[4096];int n;while((n=in.read(buffer))!=-1){cancelled();need(n>0&&out.size()+n<=65536,"SIZE");out.write(buffer,0,n);}byte[]data=out.toByteArray();
  StringBuilder hash=new StringBuilder();for(byte b:MessageDigest.getInstance("SHA-256").digest(data))hash.append(String.format(Locale.ROOT,"%02x",b&255));need(SHA256.equals(hash.toString()),"HASH");
  for(byte b:data)need(b==9||b==10||(b>=32&&b<=126),"ASCII");String[]lines=new String(data,StandardCharsets.US_ASCII).split("\n",-1);need(lines[0].equals("P7SELECTOR\t1\t"+POLICY)&&lines[lines.length-1].isEmpty(),"HEADER");
  Map<Integer,Item>items=new HashMap<>();Map<Integer,Integer>epochs=new HashMap<>();List<Integer>s=new ArrayList<>(),a=new ArrayList<>();Set<String>pairs=new HashSet<>();
  for(int i=1;i<lines.length-1;i++){String[]f=lines[i].split("\t",-1);need(f.length>=3,"ROW");int id=Integer.parseInt(f[1]),v=Integer.parseInt(f[2]);need(id>0&&v>0,"INTEGER");
   if(f[0].equals("I")&&f.length==4){int sub=Integer.parseInt(f[3]);need(sub>=61&&sub<=67&&items.put(id,new Item(v,sub))==null&&pairs.add(v+":"+sub),"ITEM_DOMAIN");}
   else if(f[0].equals("H")&&f.length==3){need((id==3||id==4)&&!s.contains(v)&&!a.contains(v),"HERO_DOMAIN");(id==4?s:a).add(v);}
   else if(f[0].equals("P")&&f.length==3)need(epochs.put(id,v)==null,"DUPLICATE_POOL");
   else throw new IOException("Selector RECORD");
  }
  need(items.size()==42&&epochs.size()==6&&!s.isEmpty()&&!a.isEmpty()&&epochs.containsKey(484),"CLOSURE");for(int t:epochs.keySet())for(int sub=61;sub<=67;sub++)need(pairs.contains(t+":"+sub),"POOL_CLOSURE");cancelled();snapshot=new Catalog(items,epochs,s,a);
 }
 static boolean supports(int t){Catalog c=snapshot;return t!=484&&c!=null&&c.epochs.containsKey(t);}
 static List<Integer>candidates(int t,int rank)throws IOException{Catalog c=ready();need(supports(t)&&(rank==3||rank==4),"CANDIDATE_SCOPE");return rank==4?c.s:c.a;}
 static void validateCatalog(LocalResourceCatalog stock)throws IOException {
  Catalog c=ready();for(int hero:c.s){need(stock.heroes.containsKey(hero)&&stock.heroes.get(hero).files==3,"S_RESOURCE");}for(int hero:c.a){need(stock.heroes.containsKey(hero)&&stock.heroes.get(hero).files==2,"A_RESOURCE");}
 }
 static void bind(LocalResourceCatalog.Pool pool)throws IOException {
  Catalog c=ready();need(supports(pool.id)&&pool.stamp==c.epochs.get(pool.id)&&pool.s.equals(c.s)&&pool.a.equals(c.a),"POOL_BINDING");owned.put(pool,pool.id);
 }
 static boolean owns(LocalResourceCatalog.Pool pool,int t){return pool!=null&&Integer.valueOf(t).equals(owned.get(pool));}
 static boolean requiresChoice(LocalResourceCatalog.Pool pool,byte[]state,int t){
  // Original callsite is outside IAE handling. All failures defer admission to
  // the protected factory; valid existing groups bypass new-choice gating.
  if(!owns(pool,t))return false;
  try{byte[]file=BsonLite.documentValue(state,"q7File");return !(Boolean.TRUE.equals(BsonLite.boolValue(state,"iof"))&&file!=null&&!BsonLite.keys(file).isEmpty());}catch(RuntimeException e){return false;}
 }
 static boolean selector(HistoryCatalog.Leaf leaf){return leaf.kind.equals("selector");}
 static void validateSource(int t,HistoryCatalog.Leaf leaf)throws IOException {Catalog c=ready();Item item=c.items.get(leaf.id);need(selector(leaf)&&item!=null&&supports(t)&&item.pool==t&&leaf.count==1&&leaf.design()==null,"SOURCE_SCOPE");}
 static void validateChoice(int t,byte[]state)throws IOException {
  Catalog c=ready();need(supports(t),"CHOICE_SCOPE");List<Integer>ch=BsonLite.intArrayValues(state,"ch");need(ch.size()==3&&ch.get(0).equals(c.epochs.get(t))&&c.s.contains(ch.get(1))&&c.a.contains(ch.get(2)),"CHOICE_EPOCH_OR_ROSTER");
 }
 static final class Resolved {
  final HistoryCatalog.Leaf leaf;final int source,sub,epoch;
  Resolved(HistoryCatalog.Leaf l,int i,int s,int e){leaf=l;source=i;sub=s;epoch=e;}
  byte[]tag(byte[]card){if(source==0)return card;card=BsonLite.withProfileInt(card,"q7SelectorSourceItem",source);card=BsonLite.withProfileInt(card,"q7SelectorSubtype",sub);card=BsonLite.withProfileInt(card,"q7SelectorStamp",epoch);card=BsonLite.withProfileString(card,"q7SelectorPolicy",POLICY);return BsonLite.withProfileString(card,"q7SelectorCatalogHash",SHA256);}
 }
 static Resolved resolve(LocalResourceCatalog stock,int t,byte[]state,HistoryCatalog.Leaf leaf)throws IOException {
  if(!selector(leaf))return new Resolved(leaf,0,0,0);validateSource(t,leaf);validateChoice(t,state);Catalog c=ready();Item item=c.items.get(leaf.id);List<Integer>ch=BsonLite.intArrayValues(state,"ch");
  boolean srank=item.sub==61||(item.sub>=63&&item.sub<=65);int hero=ch.get(srank?1:2),piece=item.sub<=62?0:item.sub<=65?item.sub-62:item.sub-65;
  HistoryCatalog.Leaf result=new HistoryCatalog.Leaf(leaf.common,item.sub<=62?"hero":"memory",hero,1,1,piece,null);result.validate(stock);return new Resolved(result,leaf.id,item.sub,ch.get(0));
 }
 private static final class Original {
  static final Method CHOOSE=method();
  private static Method method(){try{Method m=LocalDrawEngine.class.getDeclaredMethod("choose",byte[].class,LocalResourceCatalog.class,byte[].class,int.class);if(!Modifier.isPrivate(m.getModifiers())||!Modifier.isStatic(m.getModifiers())||m.getReturnType()!=LocalResourceEngine.Result.class)throw new NoSuchMethodException("choose ABI");m.setAccessible(true);return m;}catch(Exception e){throw new ExceptionInInitializerError(e);}}
 }
 private static LocalResourceEngine.Result original(byte[]profile,LocalResourceCatalog c,byte[]params,int t){try{return (LocalResourceEngine.Result)Original.CHOOSE.invoke(null,profile,c,params,t);}catch(InvocationTargetException e){Throwable cause=e.getCause();if(cause instanceof RuntimeException)throw (RuntimeException)cause;if(cause instanceof Error)throw (Error)cause;throw new IllegalArgumentException("原自选请求未完成。",cause);}catch(ReflectiveOperationException e){throw new IllegalArgumentException("原自选接口不可用。",e);}}
 /** Exact original choose descriptor; all484/nonowned paths delegate untouched. */
 public static LocalResourceEngine.Result choose(byte[]profile,LocalResourceCatalog c,byte[]params,int t){
  LocalResourceCatalog.Pool pool=c.pools.get(t);if(!owns(pool,t))return original(profile,c,params,t);
  try {
   cancelled();Catalog rules=ready();byte[]state=LocalDrawEngine.state(profile,t);List<Integer>ch=BsonLite.intArrayValues(state,"ch");byte[]file=BsonLite.documentValue(state,"q7File");boolean pending=Boolean.TRUE.equals(BsonLite.boolValue(state,"iof"))&&file!=null&&!BsonLite.keys(file).isEmpty();
   byte[]candidate=profile;boolean migrated=!pending&&!ch.isEmpty()&&(ch.size()!=3||!ch.get(0).equals(rules.epochs.get(t)));
   if(migrated){LocalResourceEngine.Result temporary=new LocalResourceEngine.Result(profile);LocalDrawEngine.saveState(temporary,BsonLite.withProfileArray(state,"ch",Arrays.asList(0,0,0)),t);candidate=temporary.profile;}
   LocalResourceEngine.Result result=original(candidate,c,params,t);boolean success=false;for(LocalResourceEngine.Reply q:result.replies)if(q.method.equals("replySetChooseHeroes"))success=Integer.valueOf(0).equals(BsonLite.intValue(q.parameters,"r"));
   if(!success&&migrated)result.profile=profile;
   if(success){byte[]saved=LocalDrawEngine.state(result.profile,t);saved=BsonLite.withProfileString(saved,"q7SelectorPolicy",POLICY);saved=BsonLite.withProfileString(saved,"q7SelectorCatalogHash",SHA256);LocalDrawEngine.saveState(result,saved,t);}return result;
  }catch(Exception e){
   LocalResourceEngine.Result result=new LocalResourceEngine.Result(profile);result.add("showMessageStr",BsonLite.document("m","自选奖励数据校验失败，请重新进入卡池。"));result.add("replySetChooseHeroes",BsonLite.document("r",1812,"t",t,"h",Arrays.asList(0,0,0)));return result;
  }
 }
}
