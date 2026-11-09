package com.project7.localmanager;
import java.io.*;import java.lang.reflect.*;import java.util.*;
/** Original LocalProfileStore instance/path/monitor/PROFILE_LOCK/readAll/writeAtomic. */
final class DreamStorage {
 interface Action<T>{T run(DreamStorage tx)throws IOException;}
 final Object store;final File file;private final Class<?>type;
 private DreamStorage(Object store,File file,Class<?>type){this.store=store;this.file=file;this.type=type;}
 static <T>T locked(LocalGatewayServer gateway,String account,Action<T> action)throws IOException{
  Object provider=unwrapProvider(DreamAccess.get(gateway,"profileProvider"));Class<?>type=DreamAccess.type("LocalProfileStore");
  if(provider==null||provider.getClass()!=type)throw new IOException("Original profile store required");
  if(account==null||!account.matches("[A-Za-z0-9_]{1,64}"))throw new IOException("Trusted account shape");
  Class<?>accounts=DreamAccess.type("LocalAccountStore");if((Boolean)DreamAccess.stat(accounts,"isTemplateAccount",new Class<?>[]{String.class},account))throw new IOException("Read only profile");
  String name=(String)DreamAccess.stat(accounts,"normalizeUsername",new Class<?>[]{String.class},account);
  synchronized(provider){try{Field field=type.getDeclaredField("PROFILE_LOCK");field.setAccessible(true);synchronized(field.get(null)){
   File directory=((File)DreamAccess.get(provider,"profilesDirectory")).getCanonicalFile();File file=new File(directory,name+".bson").getCanonicalFile();
   if(!directory.equals(file.getParentFile())||!file.isFile())throw new IOException("Existing profile path required");
   return action.run(new DreamStorage(provider,file,type));
  }}catch(ReflectiveOperationException e){throw new IOException(e);}}
 }
 byte[]read()throws IOException{return(byte[])DreamAccess.stat(type,"readAll",new Class<?>[]{File.class},file);}
 void commit(byte[]expected,byte[]next)throws IOException{
  if(!Arrays.equals(expected,read()))throw new IOException("Dream profile revision changed");
  try{DreamAccess.stat(type,"writeAtomic",new Class<?>[]{File.class,byte[].class},file,next);}
  catch(IOException failure){byte[]actual;try{actual=read();}catch(IOException unknown){failure.addSuppressed(unknown);throw failure;}
   if(Arrays.equals(actual,next))return;if(Arrays.equals(actual,expected))throw failure;throw new IOException("Uncertain dream commit; reconnect required",failure);
  }
 }
 private static Object unwrapProvider(Object provider){if(provider==null||!"FailureSafeProfileProvider".equals(provider.getClass().getSimpleName()))return provider;try{java.lang.reflect.Method m=provider.getClass().getDeclaredMethod("delegate");m.setAccessible(true);Object d=m.invoke(provider);if(d!=null)return d;}catch(Exception ignored){}return provider;}
}
