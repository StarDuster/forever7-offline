package com.project7.localmanager;
import java.io.*;import java.nio.file.*;import java.lang.reflect.*;import java.util.*;
/** HOST ONLY detached source profiles; never a Store, never grants trial assets. */
public final class TrialProjector {
 public static void main(String[]args)throws Exception{
  File a=new File(args[0]),input=new File(args[1]),output=new File(args[2]);output.mkdirs();
  LocalCombatCatalog c=new LocalCombatCatalog(new FileInputStream(new File(a,"combat_skills.tsv")),new FileInputStream(new File(a,"combat_attrs.tsv")),new FileInputStream(new File(a,"suppression.tsv")),new FileInputStream(new File(a,"growth.tsv")),new FileInputStream(new File(a,"home.tsv")));
  Method m=BsonLite.class.getDeclaredMethod("combatDataDocument",Iterable.class,String.class,byte[].class,LocalCombatCatalog.class,int.class,int.class,int.class);m.setAccessible(true);
  for(File f:input.listFiles()){String[]key=f.getName().replace(".bson","").split("-");int scene=Integer.parseInt(key[0]),hero=Integer.parseInt(key[1]),level=Integer.parseInt(key[2]);byte[]p=Files.readAllBytes(f.toPath());byte[]reply=(byte[])m.invoke(null,Arrays.asList(hero),"trial",p,c,level,0,2);byte[]heroes=BsonLite.documentValue(reply,"heroes"),actor=BsonLite.documentValue(heroes,"('trial', "+hero+")");if(actor==null)throw new AssertionError("actor missing "+BsonLite.keys(reply)+" "+BsonLite.keys(heroes));Files.write(new File(output,scene+"-"+hero+".bson").toPath(),actor);if(!Arrays.equals(p,Files.readAllBytes(f.toPath())))throw new AssertionError("source mutated");}
 }
}
