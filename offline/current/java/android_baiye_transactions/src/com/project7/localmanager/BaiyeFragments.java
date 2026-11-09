package com.project7.localmanager;
import java.io.*;import java.util.*;
/** One owned source voucher per request; original memory runner owns hfp/hero/grants. */
final class BaiyeFragments {
 private BaiyeFragments(){}
 static final class Rejected extends IllegalArgumentException{final int reason;Rejected(int r){reason=r;}}
 static byte[]doc(byte[]p,String key){byte[]d=BsonLite.documentValue(p,key);if(d==null){if(BsonLite.keys(p).contains(key))throw new Rejected(0);return BsonLite.EMPTY_DOCUMENT;}BaiyeTransactions.document(d);return d;}
 static LocalResourceEngine.Result exchange(LocalProfileStore store,String account,boolean selector,int item,int hero,int piece)throws IOException{
  BaiyeFragmentRules rules=BaiyeFragmentRules.current();BaiyeFragmentRules.Voucher voucher=rules.vouchers.get(item);Integer files=rules.files.get(hero);
  if(voucher==null||voucher.type!=(selector?6:7)||!voucher.heroes.contains(hero)||files==null||piece<0||selector&&piece==0||piece>0&&(files==0||piece>files))throw new Rejected(0);
  return BaiyeTransactions.transact(store,account,(before,resources)->{
   LocalResourceCatalog.Hero meta=resources.heroes.get(hero);if(meta==null||piece>0&&meta.files!=files)throw new Rejected(0);
   if(piece==0&&!LocalResourceEngine.ownsHero(before,hero))throw new Rejected(1);
   if(BaiyeTransactions.count(before,item)<1)throw new Rejected(2);
   byte[]ldd=doc(before,"ldd"),hfp=doc(ldd,"hfp");String key=Integer.toString(hero);Number raw=BsonLite.numericValue(hfp,key);int mask=0;
   if(BsonLite.keys(hfp).contains(key)){if(!(raw instanceof Integer))throw new Rejected(0);mask=raw.intValue();if(mask<0||files>0&&mask>((1<<files)-1))throw new Rejected(0);}
   int crystal=4252+Math.max(1,Math.min(4,meta.rank));if((piece==0||LocalResourceEngine.ownsHero(before,hero)||(mask&(1<<(piece-1)))!=0)&&BaiyeTransactions.count(before,crystal)>=Integer.MAX_VALUE)throw new Rejected(0);
   LocalResourceEngine.Result result=new LocalResourceEngine.Result(before);LocalGiftEngine.consume(result,item,1);byte[]reward;
   if(piece==0){LocalResourceEngine.grant(result,resources,"item",crystal,1,1);reward=result.reward();result.add("syncProgInfo",BsonLite.document("prog",hfp));result.add("replyExchangeSuipianWithItem",BsonLite.document("rs",true,"i",BsonLite.document("fn",0,"hi",hero,"rw",result.itemRewards)));}
   else{
    byte[]card=BsonLite.document("q7Kind","memory","q7Id",hero,"hero_file",piece);
    reward=LocalDrawEngine.reveal(result,resources,card);
    byte[]after=doc(doc(result.profile,"ldd"),"hfp");result.add("syncProgInfo",BsonLite.document("prog",after));
    if(selector)result.add("invExchangeHeroFragmentReply",BsonLite.document("r",true,"i",BsonLite.document("hero",hero,"file_num",piece,"reward",reward)));
    else result.add("replyExchangeSuipianWithItem",BsonLite.document("rs",true,"i",BsonLite.document("fn",piece,"hi",hero,"rw",reward)));
   }
   return result;
  });
 }
}
