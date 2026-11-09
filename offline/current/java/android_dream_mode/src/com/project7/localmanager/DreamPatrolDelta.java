package com.project7.localmanager;
import java.io.*;import java.util.*;
/** Only patrol-owned scalars/sets/map entries and available/replay differences.
 * Never restores a whole Progress, processing/completed or unrelated events. */
final class DreamPatrolDelta {
 static final String[]SCALARS={"patrolDay","patrolArea","patrolFavor","patrolRewardPending"};
 static final String[]SETS={"patrolHeroes","patrolEvents"};
 static final String[]MAPS={"patrolFavorBonus","patrolFriendly"};
 static final String[]DIFFS={"availableEvents","patrolReplays"};
 static byte[]capture(Object before,Object after)throws IOException{
  byte[] result=BsonLite.EMPTY_DOCUMENT;
  for(String key:SCALARS){Object a=DreamAccess.get(before,key),b=DreamAccess.get(after,key);if(!Objects.equals(a,b))result=BsonLite.withProfileDocument(result,key,BsonLite.document("a",a,"b",b));}
  for(String key:SETS){Set<Integer>a=set(before,key),b=set(after,key);if(!a.equals(b))result=BsonLite.withProfileDocument(result,key,BsonLite.document("a",new ArrayList<>(a),"b",new ArrayList<>(b)));}
  for(String key:DIFFS){Set<Integer>a=set(before,key),b=set(after,key),add=new LinkedHashSet<>(b),remove=new LinkedHashSet<>(a);add.removeAll(a);remove.removeAll(b);if(!add.isEmpty()||!remove.isEmpty())result=BsonLite.withProfileDocument(result,key,BsonLite.document("add",new ArrayList<>(add),"remove",new ArrayList<>(remove)));}
  for(String key:MAPS){Map<Integer,Integer>a=map(before,key),b=map(after,key);List<Integer>remove=new ArrayList<>();byte[] put=BsonLite.EMPTY_DOCUMENT;for(Integer id:a.keySet())if(!b.containsKey(id))remove.add(id);for(Map.Entry<Integer,Integer>e:b.entrySet())if(!Objects.equals(a.get(e.getKey()),e.getValue()))put=BsonLite.withProfileInt(put,Integer.toString(e.getKey()),e.getValue());if(!remove.isEmpty()||!BsonLite.keys(put).isEmpty())result=BsonLite.withProfileDocument(result,key,BsonLite.document("remove",remove,"put",put));}
  return result;
 }
 static void apply(Object target,byte[]delta)throws IOException{
  Set<String>allowed=new HashSet<>();Collections.addAll(allowed,SCALARS);Collections.addAll(allowed,SETS);Collections.addAll(allowed,MAPS);Collections.addAll(allowed,DIFFS);if(!allowed.containsAll(BsonLite.keys(delta)))throw new IOException("Unknown dream owned delta");
  for(String key:SCALARS){byte[]d=BsonLite.documentValue(delta,key);if(d==null)continue;Object old=DreamAccess.get(target,key),a,b;if(key.equals("patrolDay")){a=BsonLite.stringValue(d,"a");b=BsonLite.stringValue(d,"b");}else if(key.equals("patrolRewardPending")){a=BsonLite.boolValue(d,"a");b=BsonLite.boolValue(d,"b");}else{a=BsonLite.intValue(d,"a");b=BsonLite.intValue(d,"b");}if(!Objects.equals(old,a)&&!Objects.equals(old,b))throw new IOException("Dream scalar revision conflict");DreamAccess.set(target,key,b);}
  for(String key:SETS){byte[]d=BsonLite.documentValue(delta,key);if(d==null)continue;Set<Integer>current=set(target,key),a=new LinkedHashSet<>(BsonLite.intArrayValues(d,"a")),b=new LinkedHashSet<>(BsonLite.intArrayValues(d,"b"));if(!current.equals(a)&&!current.equals(b))throw new IOException("Dream set revision conflict");current.clear();current.addAll(b);}
  for(String key:DIFFS){byte[]d=BsonLite.documentValue(delta,key);if(d==null)continue;Set<Integer>value=set(target,key);value.removeAll(BsonLite.intArrayValues(d,"remove"));value.addAll(BsonLite.intArrayValues(d,"add"));}
  for(String key:MAPS){byte[]d=BsonLite.documentValue(delta,key);if(d==null)continue;Map<Integer,Integer>value=map(target,key);for(Integer id:BsonLite.intArrayValues(d,"remove"))value.remove(id);byte[]put=BsonLite.documentValue(d,"put");for(String id:BsonLite.keys(put)){if(!id.matches("[0-9]+"))throw new IOException("Dream map key");Integer n=BsonLite.intValue(put,id);if(n==null)throw new IOException("Dream map value");value.put(Integer.parseInt(id),n);}}
 }
 @SuppressWarnings("unchecked")static Set<Integer>set(Object p,String key)throws IOException{return(Set<Integer>)DreamAccess.get(p,key);}
 @SuppressWarnings("unchecked")static Map<Integer,Integer>map(Object p,String key)throws IOException{return(Map<Integer,Integer>)DreamAccess.get(p,key);}
}
