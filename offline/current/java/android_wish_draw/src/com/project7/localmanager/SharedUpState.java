package com.project7.localmanager;
import java.io.*;import java.util.*;
/** Source-bound offline seed; canonical f persists across pools and epochs. */
final class SharedUpState {
 static final String KEY="q7WishSharedUp",POLICY="shared-up-failure-seed-v1";
 final int failures;final byte[]canonical;
 private SharedUpState(int f,byte[]d){failures=f;canonical=d;}
 static SharedUpState read(byte[]profile)throws IOException{byte[]d=BsonLite.documentValue(profile,KEY);WishCatalog.need(!BsonLite.keys(profile).contains(KEY)||d!=null,"UP canonical type");if(d!=null){WishCatalog.need(Integer.valueOf(1).equals(BsonLite.intValue(d,"v"))&&POLICY.equals(BsonLite.stringValue(d,"policy"))&&WishCatalog.SHA256.equals(BsonLite.stringValue(d,"hash")),"UP schema");int f=WishChoosePolicy.value(d,"f",-1);WishProbability.projected(f);return new SharedUpState(f,d);}
  byte[]ldd=BsonLite.documentValue(profile,"ldd"),pairs=BsonLite.arrayValue(ldd,"iuc");WishCatalog.need(ldd==null||!BsonLite.keys(ldd).contains("iuc")||pairs!=null,"UP seed type");int old=0;boolean found=false;if(pairs!=null)for(byte[]p:LocalResourceEngine.array(pairs)){Integer k=BsonLite.intValue(p,"0");WishCatalog.need(k!=null,"UP seed pair");if(k==1){WishCatalog.need(!found,"UP seed duplicate");found=true;Number n=BsonLite.numericValue(p,"1");WishCatalog.need((n instanceof Integer||n instanceof Long)&&n.longValue()>=0&&n.longValue()<=Integer.MAX_VALUE,"UP seed value");old=n.intValue();}}
  int f=Math.min(old,179);return new SharedUpState(f,BsonLite.document("v",1,"policy",POLICY,"hash",WishCatalog.SHA256,"seed_policy","old-iuc-as-failures-v1","seed_raw",old,"f",f));
 }
 byte[] advance(byte[]profile,boolean sourceHit)throws IOException{int f=sourceHit?0:Math.min(179,failures+1);byte[]d=BsonLite.withProfileInt(canonical,"f",f);profile=BsonLite.withProfileDocument(profile,KEY,d);byte[]ldd=BsonLite.documentValue(profile,"ldd");if(ldd==null)ldd=BsonLite.EMPTY_DOCUMENT;ldd=WishChoosePolicy.pair(ldd,"iuc",1,WishProbability.projected(f));return BsonLite.withProfileDocument(profile,"ldd",ldd);}
}
