package com.project7.localmanager;
import android.content.Context;import java.io.*;import java.security.*;import java.util.*;
/** Immutable fixed public data, not profile state. */
public final class BaiyeCatalog {
 static final String SHA="0c2a8199eb0ff9ed2d678fc29128a95e267af94642af471f7050c5d0565e4141";
 private static volatile Map<Integer,int[]> fusion;
 private BaiyeCatalog(){}
 public static void prepare(Context context)throws IOException{
  ByteArrayOutputStream b=new ByteArrayOutputStream();try(InputStream in=context.getAssets().open("project7_baiye/catalog-v1.tsv")){byte[]buf=new byte[4096];int n;while((n=in.read(buf))!=-1){if(b.size()+n>65536)throw new IOException("Catalog bound");b.write(buf,0,n);}}
  byte[]bytes=b.toByteArray();try{StringBuilder hex=new StringBuilder();for(byte v:MessageDigest.getInstance("SHA-256").digest(bytes))hex.append(String.format(java.util.Locale.ROOT,"%02x",v&255));if(!SHA.equals(hex.toString()))throw new IOException("Baiye catalog hash");}catch(NoSuchAlgorithmException e){throw new IOException(e);}
  String[]lines=new String(bytes,"US-ASCII").split("\n");if(lines.length!=4||!lines[0].equals("P7BAIYE\t1\tstock-item-fusion-v1"))throw new IOException("Baiye catalog schema");Map<Integer,int[]> m=new HashMap<>();try{for(int i=1;i<lines.length;i++){String[]v=lines[i].split("\t");if(v.length!=4||!v[0].equals("F"))throw new IOException("Fusion row");int from=Integer.parseInt(v[1]),ratio=Integer.parseInt(v[2]),to=Integer.parseInt(v[3]);if(from<=0||ratio<=0||to<=0||from==to||m.put(from,new int[]{ratio,to})!=null)throw new IOException("Fusion rule");}}catch(NumberFormatException e){throw new IOException(e);}fusion=Collections.unmodifiableMap(m);
 }
 static int cost(int from,int to,int count){Map<Integer,int[]>m=fusion;if(m==null)throw new IllegalStateException("Baiye catalog not prepared");int[]r=m.get(from);if(r==null||r[1]!=to||count<=0)throw new IllegalArgumentException("Fusion rule");return Math.multiplyExact(r[0],count);}
}
