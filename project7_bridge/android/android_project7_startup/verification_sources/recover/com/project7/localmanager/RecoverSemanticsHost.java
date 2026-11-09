package com.project7.localmanager;
import java.text.SimpleDateFormat;
import java.util.Date;
import java.util.Locale;
/** Direct actual-manager LocalServiceEngine.recover boundary host. Host-only; no production edit. */
public class RecoverSemanticsHost {
 static byte[] city(int jpv,int jpvt,int mjpv,String day)throws Exception{byte[] c=BsonLite.document("jpv",jpv,"jpvt",jpvt,"mjpv",mjpv,"cjsla",0);byte[] p=BsonLite.document("city",c);if(day!=null)p=BsonLite.withProfileString(p,"q7powerDay",day);return p;}
 static byte[] out(int jpv,int jpvt,int mjpv,String day,int now)throws Exception{return LocalServiceEngine.recover(city(jpv,jpvt,mjpv,day),now*1000L);}
 static int[] vals(byte[]p)throws Exception{byte[] c=BsonLite.documentValue(p,"city");return new int[]{BsonLite.intValue(c,"jpv"),BsonLite.intValue(c,"jpvt")};}
 static void check(boolean v,String m){if(!v)throw new AssertionError(m);}
 public static void main(String[]a)throws Exception{
  int now=1700000000;String today=new SimpleDateFormat("yyyy-MM-dd",Locale.ROOT).format(new Date(now*1000L));String old="2000-01-01";
  int[]v;
  byte[] fixture=city(100,now-10,240,today);
  check(today.equals(BsonLite.stringValue(fixture,"q7powerDay")),"fixture date is at actual profile root");
  check(BsonLite.stringValue(BsonLite.documentValue(fixture,"city"),"q7powerDay")==null,"fixture date is not nested in city");
  byte[] sameDay=LocalServiceEngine.recover(fixture,now*1000L);
  check(java.util.Arrays.equals(fixture,sameDay),"same-day partial recovery preserves entire profile");
  byte[] oldDay=city(100,now-10,240,old);
  oldDay=BsonLite.withProfileDocument(oldDay,"city",BsonLite.withProfileInt(BsonLite.documentValue(oldDay,"city"),"cjsla",7));
  byte[] refreshed=LocalServiceEngine.recover(oldDay,now*1000L);
  check(today.equals(BsonLite.stringValue(refreshed,"q7powerDay")),"new date updates root power day");
  check(BsonLite.intValue(BsonLite.documentValue(refreshed,"city"),"cjsla")==0,"new date resets purchase counter");
  byte[] sameWithPurchases=BsonLite.withProfileString(oldDay,"q7powerDay",today);
  check(java.util.Arrays.equals(sameWithPurchases,LocalServiceEngine.recover(sameWithPurchases,now*1000L)),"same date preserves purchase counter and full profile");
  v=vals(out(240,now-1000,240,old,now));check(v[0]==240&&v[1]==now,"full+old date writes jpvt=now");
  v=vals(out(240,now-1000,240,today,now));check(v[0]==240&&v[1]==now,"full+today writes jpvt=now");
  v=vals(out(100,now-359,240,today,now));check(v[0]==100&&v[1]==now-359,"partial 359 keeps jpv/jpvt");
  v=vals(out(100,now-360,240,today,now));check(v[0]==101&&v[1]==now,"partial 360 advances one and stamps now");
  v=vals(out(100,now-10,240,today,now));check(v[0]==100&&v[1]==now-10,"partial 10 keeps jpv/jpvt across seconds");
  v=vals(out(100,now-10,240,old,now));check(v[0]==100&&v[1]==now-10,"partial 10 old day keeps jpv/jpvt");
  System.out.println("PASS recovery: full=now; 359/360 boundary; partial preserves timestamp; date variation");
 }
}
