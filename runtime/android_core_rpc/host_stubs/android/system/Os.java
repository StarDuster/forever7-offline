package android.system;
import java.io.*;import java.nio.file.*;
/** HOST ONLY atomic rename seam/fault injection. No ART claim. */
public final class Os {
 public interface RenameHook { void after(String name) throws Exception; }
 public static volatile boolean failBefore,failAfter; public static int renames; public static RenameHook afterRename;
 public static void rename(String from,String to)throws ErrnoException {
  if(failBefore){failBefore=false;throw new ErrnoException("host before rename",5);}
  try{Files.move(Paths.get(from),Paths.get(to),StandardCopyOption.ATOMIC_MOVE,StandardCopyOption.REPLACE_EXISTING);renames++;}
  catch(IOException e){throw new ErrnoException("host rename",5);}
  if(failAfter){failAfter=false;throw new ErrnoException("host after rename",5);}
  if(afterRename!=null){try{afterRename.after(to);}catch(RuntimeException e){throw e;}catch(Exception e){throw new ErrnoException("host after rename",5);}}
 }
}
