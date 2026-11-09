package com.project7.localmanager;
import java.util.*;
/** Original/synthetic ABI declarations only. Never package these class bodies. */
final class BsonLite {
    static final byte[] EMPTY_DOCUMENT=null;
    static byte[] document(Object... values){throw new UnsupportedOperationException("compile stub");}
    static byte[] withProfileBool(byte[] doc,String key,boolean value){throw new UnsupportedOperationException("compile stub");}
    static byte[] withProfileInt(byte[] doc,String key,int value){throw new UnsupportedOperationException("compile stub");}
    static byte[] withProfileDocument(byte[] doc,String key,byte[] value){throw new UnsupportedOperationException("compile stub");}
    static byte[] withProfileString(byte[] doc,String key,String value){throw new UnsupportedOperationException("compile stub");}
    static byte[] withProfileArray(byte[] doc,String key,List<?> value){throw new UnsupportedOperationException("compile stub");}
}
final class LocalResourceCatalog {
    final Map<Integer,Skin> skins;final Map<Integer,Hero> heroes;final Map<Integer,Item> items;final Map<String,Treasure> treasures;final Map<Integer,Pool> pools;
    LocalResourceCatalog(java.io.InputStream input)throws java.io.IOException{throw new UnsupportedOperationException("compile stub");}
    static final class Hero {final int files;Hero(String[] columns){throw new UnsupportedOperationException("compile stub");}}
    static final class Skin {final int id,hero,item;Skin(String[] columns){throw new UnsupportedOperationException("compile stub");}}
    static final class Item {final int hero,id,type,wrap;final String name;Item(String[] columns){hero=id=type=wrap=0;name=null;}}
    static final class Treasure {Treasure(String[] columns){throw new UnsupportedOperationException("compile stub");}}
    static final class Drop {Drop(String[] columns){throw new UnsupportedOperationException("compile stub");}}
    static final class Pool {
        final int id,stamp,ticket;final List<Integer>s,a;final List<Drop>drops;
        Pool(int id,int stamp,int ticket,List<Integer>s,List<Integer>a,List<Drop>drops){throw new UnsupportedOperationException("compile stub");}
    }
}
final class LocalResourceEngine {
    static final class Reply {final String method;final byte[] parameters;Reply(String method,byte[] params){throw new UnsupportedOperationException("compile stub");}}
    static final class Result {byte[] profile;final List<Reply> replies;final List<List<Integer>> itemRewards;byte[] reward(){throw new UnsupportedOperationException("compile stub");}Result(byte[] profile){throw new UnsupportedOperationException("compile stub");}}
    static void grant(Result result,LocalResourceCatalog catalog,String kind,int id,int count,int quality){throw new UnsupportedOperationException("compile stub");}
    static boolean ownsHero(byte[] profile,int hero){throw new UnsupportedOperationException("compile stub");}
    static int currencyItem(String kind){throw new UnsupportedOperationException("compile stub");}
}
final class LocalDrawEngine {
    static byte[] q7OriginalTutorialCard(int index){throw new UnsupportedOperationException("compile stub");}
    static byte[] state(byte[] profile,int t){throw new UnsupportedOperationException("compile stub");}
    static void q7OriginalSpend(LocalResourceEngine.Result r,int amount,LocalResourceCatalog.Pool p,int t){throw new UnsupportedOperationException("compile stub");}
    static byte[] makeActivityFile(LocalResourceCatalog c,LocalResourceCatalog.Pool p,byte[] state,Random random){throw new UnsupportedOperationException("compile stub");}
    static byte[] reveal(LocalResourceEngine.Result r,LocalResourceCatalog c,byte[] card){throw new UnsupportedOperationException("compile stub");}
}
final class CoreDrawPolicy {
    static byte[] stateForSave(byte[] state,int t)throws Exception{throw new UnsupportedOperationException("compile stub");}
    static byte[] reveal(LocalResourceEngine.Result r,LocalResourceCatalog c,byte[] card)throws Exception{throw new UnsupportedOperationException("compile stub");}
}

final class LocalDrawDailyEngine {static String day(long now){throw new UnsupportedOperationException("compile stub");}}
final class LocalStoryEnvironment {static long now(){throw new UnsupportedOperationException("compile stub");}}

final class LocalFeatureCatalog {LocalFeatureCatalog(java.io.InputStream input) throws java.io.IOException {} byte[] get(String key,Object identity){throw new UnsupportedOperationException("compile stub");}}
final class LocalHomeEngine {static void q7OriginalSkinCopies(LocalResourceEngine.Result result,LocalResourceCatalog catalog,int skin,int count,long now){throw new UnsupportedOperationException("compile stub");}static byte[] rule(LocalFeatureCatalog catalog,String key,Object identity){throw new UnsupportedOperationException("compile stub");}static byte[] q7OriginalChoose(List<byte[]> rows,Random random){throw new UnsupportedOperationException("compile stub");}}
