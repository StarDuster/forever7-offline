package com.project7.localmanager;
import java.io.*;
import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.util.*;
import java.util.zip.GZIPInputStream;
import org.json.*;

/** Prepared immutable public metadata. No player/profile/Context owner. */
final class DynamicCatalog {
 static final String ASSET="project7_dynamic/catalog-v1.json.gz";
 static final String SHA="845e146b5fd19fc119ff79ebee6671755c35cfad9a41743003e1898e987b7c5e";
 static final int SIZE=69029,EXPANDED=675947;
 static final String EXPANDED_SHA="611cf669764f3287cd245f48f5a14678891b343701dbcab4b21e98559ce41a7a";
 // Explicit vertical pilot configuration, not a reward/weight handler switch.
 static final Set<Integer> PILOT=Collections.unmodifiableSet(new HashSet<>(Arrays.asList(485))); // legacy decoder only
 // Fixed source-domain repair data, not per-pool reward handlers. Missing IDs
 // are chouka_normal references; never reinterpret them as reward_random IDs.
 static final Map<Integer,Integer> MISSING_DEFAULTS;
 static {Map<Integer,Integer> m=new LinkedHashMap<>();for(int[]r:new int[][]{{42,5657},{52,5981},{62,6499},{72,6767},{81,6968},{89,7366},{107,7657}})m.put(r[0],r[1]);MISSING_DEFAULTS=Collections.unmodifiableMap(m);}
 static final Set<Integer> SIX_SLOT_ARCHIVE=Collections.unmodifiableSet(new HashSet<>(Arrays.asList(2,3,4)));
 static final Set<Integer> FREE_TICKET_ARCHIVE=Collections.unmodifiableSet(new HashSet<>(Arrays.asList(362,488)));
 static boolean family(Map<?,?> value)throws Exception{int id=num(value.get("pool"));return !list(value.get("charge")).isEmpty()&&(list(value.get("extra")).size()==1||SIX_SLOT_ARCHIVE.contains(id)&&list(value.get("extra")).isEmpty());}
 static final class Spec {
  final int id,epoch,target;final boolean repairedBinding;final String policy;final Map<?,?> raw;final DynamicTransition.Rules rules;final List<Map<?,?>> extra;
  Spec(Map<?,?> value)throws Exception{
   id=num(value.get("pool"));policy=DynamicSlotPlan.policyFor(id);epoch=num(value.get("epoch"));raw=map(decode(value.get("raw")));
   List<?> extras=list(value.get("extra"));need(extras.size()<=1,"EXTRA_TARGET");target=extras.isEmpty()?0:num(map(extras.get(0)).get("hero"));List<Map<?,?>> x=new ArrayList<>();for(Object e:extras)x.add(map(e));extra=Collections.unmodifiableList(x);
   need(SIX_SLOT_ARCHIVE.contains(id)||num(raw.get("times"))==6,"SHAPE");for(String key:Arrays.asList("wish_sort","replace_reward","self_choose","is_up","inc_up_cnt_type"))need(!raw.containsKey(key),"UNSUPPORTED_CAPABILITY_"+key);
   List<DynamicTransition.Threshold> charge=new ArrayList<>(),jiaozhi=new ArrayList<>();boolean repair=false;
   for(Object o:list(value.get("charge"))){Map<?,?> t=map(o);charge.add(new DynamicTransition.Threshold(num(t.get("row_id")),num(t.get("threshold")),false,"common",ints(list(t.get("grant_common_ids")))));}
   for(Object o:list(value.get("jiaozhi"))){Map<?,?> t=map(o),r=map(decode(t.get("raw")));need(num(r.get("target_hero"))==target,"JIAOZHI_TARGET");if(!Boolean.TRUE.equals(t.get("hero_file_binding_valid")))repair=true;jiaozhi.add(new DynamicTransition.Threshold(num(t.get("row_id")),num(t.get("threshold")),r.containsKey("open_hero_file")&&num(r.get("open_hero_file"))==1,"random",ints(list(t.get("grant_random_ids")))));}
   need(!charge.isEmpty(),"CHARGE_FAMILY");repairedBinding=repair;rules=new DynamicTransition.Rules(target,charge,jiaozhi);
  }
 }
 final Map<Integer,Spec> specs;final Map<?,?> common,random,items,designs;final String baseHash;
 private DynamicCatalog(Map<?,?> root)throws Exception {
  need("project7-dynamic-catalog-v1".equals(root.get("schema"))&&DynamicSlotPlan.POLICY.equals(root.get("policy")),"SCHEMA");
  baseHash=(String)map(root.get("base_graph")).get("source_sha256");need(baseHash!=null&&baseHash.matches("[0-9a-f]{64}"),"BASE_GRAPH_BINDING");common=map(decode(root.get("common")));random=map(decode(root.get("random")));items=map(decode(root.get("items")));designs=map(decode(root.get("designs")));Map<Integer,Spec> specs=new TreeMap<>();
  for(Object o:list(root.get("pools"))){Map<?,?> p=map(o);int id=num(p.get("pool"));if(!family(p))continue;Spec s=new Spec(p);need(specs.put(id,s)==null,"DUPLICATE_POOL");}
  need(specs.size()==35&&specs.keySet().containsAll(PILOT),"CLOSED_FAMILY_SCOPE");this.specs=Collections.unmodifiableMap(specs);
 }
 static void need(boolean ok,String reason)throws IOException{if(!ok)throw new IOException("Dynamic: "+reason);}
 static void stopped()throws IOException{if(Thread.currentThread().isInterrupted())throw new InterruptedIOException("DYNAMIC_CANCELLED");}
 static byte[] read(InputStream in,int max)throws IOException{ByteArrayOutputStream out=new ByteArrayOutputStream();byte[] b=new byte[8192];int n;while((n=in.read(b))!=-1){stopped();need(n>0&&out.size()+n<=max,"READ_LIMIT");out.write(b,0,n);}return out.toByteArray();}
 static String sha(byte[] bytes)throws Exception{StringBuilder s=new StringBuilder();for(byte b:MessageDigest.getInstance("SHA-256").digest(bytes))s.append(String.format(Locale.ROOT,"%02x",b&255));return s.toString();}
 static DynamicCatalog parse(InputStream in)throws Exception {
  byte[] packed=read(in,SIZE);need(packed.length==SIZE&&sha(packed).equals(SHA),"ASSET_PIN");byte[] raw;
  try(InputStream zip=new GZIPInputStream(new ByteArrayInputStream(packed))){raw=read(zip,EXPANDED);}
  need(raw.length==EXPANDED&&sha(raw).equals(EXPANDED_SHA),"EXPANDED_PIN");return new DynamicCatalog(map(json(new JSONObject(new String(raw,StandardCharsets.UTF_8)))));
 }
 private static Object json(Object value)throws Exception {
  if(value==JSONObject.NULL)return null;
  if(value instanceof JSONObject){Map<String,Object> m=new LinkedHashMap<>();JSONObject j=(JSONObject)value;Iterator<String> keys=j.keys();while(keys.hasNext()){String k=keys.next();m.put(k,json(j.get(k)));}return Collections.unmodifiableMap(m);}
  if(value instanceof JSONArray){List<Object> a=new ArrayList<>();JSONArray j=(JSONArray)value;for(int i=0;i<j.length();i++)a.add(json(j.get(i)));return Collections.unmodifiableList(a);}return value;
 }
 static Object decode(Object value)throws Exception {
  if(!(value instanceof Map))return value;
  Map<?,?> t=map(value);need(t.size()==1,"LITERAL_TAG");if(t.containsKey("$float"))return Double.valueOf((String)t.get("$float"));
  if(t.containsKey("$tuple")||t.containsKey("$list")){List<Object> a=new ArrayList<>();for(Object v:list(t.get(t.containsKey("$tuple")?"$tuple":"$list")))a.add(decode(v));return Collections.unmodifiableList(a);}
  need(t.containsKey("$dict"),"LITERAL_KIND");Map<Object,Object> m=new LinkedHashMap<>();for(Object entry:list(t.get("$dict"))){List<?> pair=list(entry);need(pair.size()==2,"LITERAL_PAIR");Object k=decode(pair.get(0));need(!m.containsKey(k),"LITERAL_DUPLICATE");m.put(k,decode(pair.get(1)));}return Collections.unmodifiableMap(m);
 }
 static Map<?,?> map(Object value)throws IOException{need(value instanceof Map,"EXPECTED_MAP");return (Map<?,?>)value;}
 static List<?> list(Object value)throws IOException{need(value instanceof List,"EXPECTED_LIST");return (List<?>)value;}
 static int num(Object value)throws IOException{need(value instanceof Number&&!(value instanceof Double)&&!(value instanceof Float),"EXPECTED_INT");long n=((Number)value).longValue();need(n>=Integer.MIN_VALUE&&n<=Integer.MAX_VALUE,"INT_BOUNDARY");return (int)n;}
 static int[] ints(List<?> values)throws IOException{int[] r=new int[values.size()];for(int i=0;i<r.length;i++)r[i]=num(values.get(i));return r;}
 static byte[] bson(Map<?,?> value)throws Exception{List<Object> fields=new ArrayList<>();for(Map.Entry<?,?> e:value.entrySet()){need(e.getKey() instanceof String,"BSON_KEY");fields.add(e.getKey());fields.add(bsonValue(e.getValue()));}return BsonLite.document(fields.toArray());}
 static Object bsonValue(Object v)throws Exception{if(v instanceof Map)return bson(map(v));if(v instanceof List){List<Object> a=new ArrayList<>();for(Object x:list(v))a.add(bsonValue(x));return a;}return v;}
}
