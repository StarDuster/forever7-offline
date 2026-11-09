package com.project7.localmanager;
import java.util.*;
/** Compile-only original DEX descriptors. No implementation, never packaged. */
final class BsonLite {
    static final byte[] EMPTY_DOCUMENT=null;
    static byte[] document(Object... values){throw new UnsupportedOperationException("compile stub");}
    static byte[] documentValue(byte[] value,String key){throw new UnsupportedOperationException("compile stub");}
    static byte[] withProfileInt(byte[] value,String key,int n){throw new UnsupportedOperationException("compile stub");}
    static byte[] withProfileDocument(byte[] value,String key,byte[] document){throw new UnsupportedOperationException("compile stub");}
    static byte[] withProfileArray(byte[] value,String key,List<?> array){throw new UnsupportedOperationException("compile stub");}
    static byte[] withCopiedValue(byte[] target,String targetKey,byte[] source,String sourceKey){throw new UnsupportedOperationException("compile stub");}
}
final class LocalResourceCatalog {
    final Map<Integer,Hero> heroes;
    final Map<Integer,Item> items;
    final Map<String,Treasure> treasures;
    LocalResourceCatalog(java.io.InputStream input) throws java.io.IOException{throw new UnsupportedOperationException("compile stub");}
    static final class Hero {final int files;Hero(String[] columns){throw new UnsupportedOperationException("compile stub");}}
    static final class Item {Item(String[] columns){throw new UnsupportedOperationException("compile stub");}}
    static final class Treasure {Treasure(String[] columns){throw new UnsupportedOperationException("compile stub");}}
}
final class LocalResourceEngine {
    static final class Result {byte[] profile;Result(byte[] profile){throw new UnsupportedOperationException("compile stub");}}
}
