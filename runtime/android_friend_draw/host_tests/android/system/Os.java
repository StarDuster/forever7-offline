package android.system;
import java.io.*;
import java.nio.file.*;
/** HOST ONLY platform rename seam. This is NOT Android Os or native acceptance. */
public final class Os {
    public static boolean failNextRename;public static int renames;
    public static void rename(String from,String to)throws IOException{
        if(failNextRename){failNextRename=false;throw new IOException("Host fault before atomic rename");}
        Files.move(Paths.get(from),Paths.get(to),StandardCopyOption.ATOMIC_MOVE,StandardCopyOption.REPLACE_EXISTING);renames++;
    }
}
