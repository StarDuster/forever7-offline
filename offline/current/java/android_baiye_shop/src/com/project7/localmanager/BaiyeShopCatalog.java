package com.project7.localmanager;
import android.content.Context;import java.io.*;import java.security.*;import java.util.*;import java.util.Base64;
/** Fixed original public shop prices/designs, never account state. */
public final class BaiyeShopCatalog {
 static final String SHA="ae6523fd78136fa7a1ef893911ca191ff764a1fe7866d9101b62a518216a0501";
 static final class Product {final int id,item,quality,quantity,costItem,cost,total,weekly,minWeek,design,reget,regetCount;final String kind,payment;final byte[]tr;
  Product(String[]r){id=n(r[1]);kind=r[2];item=n(r[3]);quality=n(r[4]);quantity=n(r[5]);payment=r[6];costItem=n(r[7]);cost=n(r[8]);total=n(r[9]);weekly=n(r[10]);minWeek=n(r[11]);design=n(r[12]);reget=n(r[13]);regetCount=n(r[14]);tr=r[15].equals("-")?null:Base64.getDecoder().decode(r[15]);if(id<=0||item<=0||cost<=0||quantity!=1||quality<1||!Arrays.asList("item","treasure").contains(kind)||!Arrays.asList("item","giftCoin","yuanbao").contains(payment)||kind.equals("treasure")!=(tr!=null))throw new IllegalArgumentException("Product shape");if(tr!=null)BaiyeTransactions.document(tr);}
 }
 private static volatile Map<Integer,Product> products;
 private BaiyeShopCatalog(){}
 static int n(String s){int n=Integer.parseInt(s);if(n<0)throw new IllegalArgumentException("Negative catalog int");return n;}
 public static void prepare(Context c)throws IOException{ByteArrayOutputStream out=new ByteArrayOutputStream();try(InputStream in=c.getAssets().open("project7_baiye_shop/catalog-v1.tsv")){byte[]b=new byte[4096];int n;while((n=in.read(b))!=-1){if(out.size()+n>65536)throw new IOException("Shop catalog bound");out.write(b,0,n);}}byte[]data=out.toByteArray();try{StringBuilder h=new StringBuilder();for(byte b:MessageDigest.getInstance("SHA-256").digest(data))h.append(String.format(Locale.ROOT,"%02x",b&255));if(!SHA.equals(h.toString()))throw new IOException("Shop catalog hash");}catch(NoSuchAlgorithmException e){throw new IOException(e);}String[]rows=new String(data,"US-ASCII").split("\n");if(rows.length!=9||!rows[0].equals("P7BAIYESHOP\t1\tsource640-baiye-shop-current-ownership-v1"))throw new IOException("Shop header");Map<Integer,Product>m=new LinkedHashMap<>();try{for(int i=1;i<rows.length;i++){String[]r=rows[i].split("\t");if(r.length!=16||!r[0].equals("S"))throw new IOException("Shop row");Product p=new Product(r);if(m.put(p.id,p)!=null)throw new IOException("Shop duplicate");}}catch(RuntimeException e){throw new IOException("Shop catalog",e);}products=Collections.unmodifiableMap(m);}
 static Product get(int id){Map<Integer,Product>m=products;if(m==null)throw new IllegalStateException("Shop not prepared");return m.get(id);}
 static boolean supports(int id){return Arrays.asList(8,157,158,478,480,540,595,617).contains(id);}
}
