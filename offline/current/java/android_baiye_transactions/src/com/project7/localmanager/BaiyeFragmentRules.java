package com.project7.localmanager;
import android.content.Context;import java.io.*;import java.security.*;import java.util.*;
/** Source-bound public voucher policy. Unknown official server charges are not invented. */
final class BaiyeFragmentRules {
 static final String SHA="61425f912e2bd5fc613aebc75ab43819b801e0b6a608afd37230bb7a37d4d5f1";
 static final class Voucher{final int type;final Set<Integer> heroes;Voucher(int t,Set<Integer>h){type=t;heroes=Collections.unmodifiableSet(h);}}
 private static volatile BaiyeFragmentRules prepared;
 final Map<Integer,Integer> files;final Map<Integer,Voucher> vouchers;
 private BaiyeFragmentRules(Map<Integer,Integer> f,Map<Integer,Voucher>v){files=Collections.unmodifiableMap(f);vouchers=Collections.unmodifiableMap(v);}
 static void prepare(Context c)throws IOException{
  ByteArrayOutputStream out=new ByteArrayOutputStream();try(InputStream in=c.getAssets().open("project7_baiye/fragments-v1.tsv")){byte[]b=new byte[4096];int n;while((n=in.read(b))!=-1){if(out.size()+n>65536)throw new IOException("Fragment catalog bounds");out.write(b,0,n);}}
  byte[]data=out.toByteArray();try{StringBuilder hex=new StringBuilder();for(byte b:MessageDigest.getInstance("SHA-256").digest(data))hex.append(String.format(Locale.ROOT,"%02x",b&255));if(!SHA.equals(hex.toString()))throw new IOException("Fragment catalog hash");}catch(NoSuchAlgorithmException e){throw new IOException(e);}
  String[]rows=new String(data,"US-ASCII").split("\n");if(!rows[0].equals("P7BAIYEFRAG\t1\tvoucher-one-stock-memory-v1"))throw new IOException("Fragment schema");Map<Integer,Integer>files=new HashMap<>();Map<Integer,Voucher>vouchers=new HashMap<>();int named=0,select=0;
  try{for(int i=1;i<rows.length;i++){String[]r=rows[i].split("\t");int id=Integer.parseInt(r[1]);if(id<=0)throw new IOException("Fragment id");if(r[0].equals("H")&&r.length==6){int n=Integer.parseInt(r[2]);if(n<0||n>3||files.put(id,n)!=null)throw new IOException("Fragment files");for(int k=3;k<6;k++)if(Integer.parseInt(r[k])<=0)throw new IOException("Fragment audit values");}else if(r[0].equals("V")&&r.length==4){int type=Integer.parseInt(r[2]);Set<Integer>heroes=new HashSet<>();for(String h:r[3].split(",")){int hero=Integer.parseInt(h);if(hero<=0||!heroes.add(hero))throw new IOException("Voucher heroes");}if(type==6)select++;else if(type==7&&heroes.size()==1)named++;else throw new IOException("Voucher type");if(vouchers.put(id,new Voucher(type,heroes))!=null)throw new IOException("Voucher duplicate");}else throw new IOException("Fragment row");}}catch(RuntimeException e){throw new IOException("Fragment format",e);}
  if(files.size()!=138||select!=17||named!=4)throw new IOException("Fragment counts");for(Voucher v:vouchers.values())if(!files.keySet().containsAll(v.heroes))throw new IOException("Voucher reference");prepared=new BaiyeFragmentRules(files,vouchers);
 }
 static BaiyeFragmentRules current(){BaiyeFragmentRules p=prepared;if(p==null)throw new IllegalStateException("Fragment policy not prepared");return p;}
}
