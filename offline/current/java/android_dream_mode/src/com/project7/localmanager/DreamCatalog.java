package com.project7.localmanager;
import android.content.Context;
import java.io.*;
import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.util.*;
/** Fixed public source references, not an alternate event-condition interpreter. */
public final class DreamCatalog {
 public static final String ASSET="project7_dream/catalog-v1.tsv";
 public static final String SHA256="b0c44413ecaad293b622933f8ece4b3199dfd6de7f63c64b4cc3655bea2ef8c1";
 public static final String POLICY="dream-three-patrol-offline-v1";
 public static final class Plan {
  public final String route;public final int day,event,night,component,subtargets;
  private Plan(String[]f){route=f[1];day=Integer.parseInt(f[2]);event=Integer.parseInt(f[3]);night=Integer.parseInt(f[4]);component=Integer.parseInt(f[5]);subtargets=Integer.parseInt(f[6]);}
  public boolean hasEvents(){return event>0&&night>0;}
 }
 public static final class Rule {
  public final int event;public final boolean dreamSentinel,hasCondition,contentRelease,conditionRelease;
  private final Map<Integer,String> conditions;
  private Rule(String[]f,Map<Integer,String>c){event=Integer.parseInt(f[1]);dreamSentinel=bit(f[2]);hasCondition=bit(f[3]);contentRelease=bit(f[4]);conditionRelease=bit(f[5]);conditions=Collections.unmodifiableMap(new TreeMap<>(c));}
  public Map<Integer,String> conditions(){return conditions;}
 }
 private final Map<String,Plan> plans;private final Map<Integer,Rule> rules;
 private DreamCatalog(byte[]data){
  if(!SHA256.equals(hash(data)))throw new IllegalArgumentException("Dream catalog hash");
  for(byte b:data)if(b!=9&&b!=10&&(b<32||b>126))throw new IllegalArgumentException("Dream catalog ASCII");
  String[]lines=new String(data,StandardCharsets.US_ASCII).split("\n",-1);
  if(!lines[0].equals("P7DREAM\t1\t"+POLICY)||!lines[lines.length-1].isEmpty())throw new IllegalArgumentException("Dream header");
  Map<String,Plan>p=new TreeMap<>();Map<Integer,String[]>r=new TreeMap<>();Map<Integer,Map<Integer,String>>c=new HashMap<>();
  for(int i=1;i<lines.length-1;i++){
   String[]f=lines[i].split("\t",-1);
   if(f[0].equals("D")&&f.length==7){Plan value=new Plan(f);if(p.put(key(value.route,value.day),value)!=null)throw new IllegalArgumentException("Duplicate dream plan");}
   else if(f[0].equals("E")&&f.length==6){int id=Integer.parseInt(f[1]);if(id<=0||r.put(id,f)!=null)throw new IllegalArgumentException("Duplicate dream rule");c.put(id,new TreeMap<Integer,String>());}
   else if(f[0].equals("C")&&f.length==4){int id=Integer.parseInt(f[1]),code=Integer.parseInt(f[2]);Map<Integer,String>m=c.get(id);if(m==null||m.put(code,new String(Base64.getDecoder().decode(f[3]),StandardCharsets.UTF_8))!=null)throw new IllegalArgumentException("Dream condition");}
   else throw new IllegalArgumentException("Dream row shape");
  }
  Map<Integer,Rule>values=new TreeMap<>();for(Map.Entry<Integer,String[]>e:r.entrySet())values.put(e.getKey(),new Rule(e.getValue(),c.get(e.getKey())));
  for(Plan value:p.values())if(value.hasEvents()&&(!values.containsKey(value.event)||!values.containsKey(value.night)))throw new IllegalArgumentException("Dream event reference");
  plans=Collections.unmodifiableMap(p);rules=Collections.unmodifiableMap(values);
 }
 public static DreamCatalog prepare(Context context)throws IOException {try(InputStream in=context.getAssets().open(ASSET)){ByteArrayOutputStream out=new ByteArrayOutputStream();byte[]b=new byte[8192];int n;while((n=in.read(b))!=-1){if(out.size()+n>1024*1024)throw new IOException("Dream asset limit");out.write(b,0,n);}return fromBytes(out.toByteArray());}}
 public static DreamCatalog fromBytes(byte[]bytes){return new DreamCatalog(bytes.clone());}
 public Plan lookup(String route,int day){if(route==null)return null;Plan exact=plans.get(key(route,day));return exact!=null?exact:plans.get(key(route.split("-",2)[0],day));}
 public Rule rule(int event){return rules.get(event);}
 public Collection<Plan>plans(){return plans.values();}
 public Collection<Rule>rules(){return rules.values();}
 private static String key(String route,int day){return route+"|"+day;}
 private static boolean bit(String text){if(!text.equals("0")&&!text.equals("1"))throw new IllegalArgumentException("Dream bit");return text.equals("1");}
 private static String hash(byte[]b){try{StringBuilder s=new StringBuilder();for(byte v:MessageDigest.getInstance("SHA-256").digest(b))s.append(String.format(Locale.ROOT,"%02x",v&255));return s.toString();}catch(Exception e){throw new IllegalStateException(e);}}
}
