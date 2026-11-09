package android.os;
import java.util.*;
/** Explicit queue seam; tests must pump main callbacks. */
public final class Handler {private static final List<Runnable> queue=new ArrayList<>();public Handler(Looper ignored){}public boolean post(Runnable r){synchronized(queue){queue.add(r);}return true;}public static void pump(){while(true){Runnable r;synchronized(queue){if(queue.isEmpty())return;r=queue.remove(0);}r.run();}}}
