package android.system;
import java.io.*;
import java.nio.file.*;
/** HOST ONLY atomic rename seam with volatile before/after failure; never packaged. */
public final class Os {
    public static volatile boolean failNextRename, failAfterRename;
    public static int renames;
    public static void rename(String from,String to)throws IOException{
        if(failNextRename){failNextRename=false;throw new IOException("Host fault before atomic rename");}
        Files.move(Paths.get(from),Paths.get(to),StandardCopyOption.ATOMIC_MOVE,StandardCopyOption.REPLACE_EXISTING);
        renames++;
        if(failAfterRename){failAfterRename=false;throw new IOException("Host fault after atomic rename");}
    }
}
