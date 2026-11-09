package com.project7.localmanager;
import java.io.*;
final class DreamAccess {
 static Object get(Object o,String n)throws IOException{return null;}static void set(Object o,String n,Object v)throws IOException{}
 static Object call(Object o,String n,Class<?>[]t,Object...a)throws IOException{return null;}static Object stat(Class<?>c,String n,Class<?>[]t,Object...a)throws IOException{return null;}
 static Class<?>type(String n)throws IOException{return null;}static Object cloneProgress(Object p)throws IOException{return null;}
 static LocalEventEngine fork(LocalEventEngine e,Object p,byte[]profile)throws IOException{return null;}static void adopt(Object p,Object live,LocalEventEngine e,byte[]profile)throws IOException{}
}
final class DreamStorage {interface Action<T>{T run(DreamStorage tx)throws IOException;}static <T>T locked(LocalGatewayServer g,String a,Action<T>op)throws IOException{return null;}byte[]read()throws IOException{return null;}void commit(byte[]a,byte[]b)throws IOException{}}
final class DreamProgressDelta {static byte[]capture(Object a,Object b)throws IOException{return null;}static void apply(Object p,byte[]d)throws IOException{}static java.util.Properties props(Object p)throws IOException{return null;}}
