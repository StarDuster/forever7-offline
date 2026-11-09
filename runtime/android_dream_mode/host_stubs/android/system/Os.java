package android.system;
import java.io.*;import java.nio.file.*;
/** HOST ONLY atomic rename seam/fault injection. No ART claim. */
public final class Os {
 public static volatile boolean failBefore,failAfter,failDreamBefore; public static int renames;
 public static void rename(String from,String to)throws ErrnoException {
  boolean dreamCommit=false;for(StackTraceElement frame:Thread.currentThread().getStackTrace())if(frame.getClassName().equals("com.project7.localmanager.DreamStorage")&&frame.getMethodName().equals("commit"))dreamCommit=true;
  if(failDreamBefore&&dreamCommit){failDreamBefore=false;throw new ErrnoException("host dream before rename",5);}
  if(failBefore){failBefore=false;throw new ErrnoException("host before rename",5);}
  try{Files.move(Paths.get(from),Paths.get(to),StandardCopyOption.ATOMIC_MOVE,StandardCopyOption.REPLACE_EXISTING);renames++;}
  catch(IOException e){throw new ErrnoException("host rename",5);}
  if(failAfter){failAfter=false;throw new ErrnoException("host after rename",5);}
 }
}
