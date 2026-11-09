package android.os;
/** Explicit event seam: does not pretend to be inotify. */
public abstract class FileObserver {public static final int MOVED_TO=128,CLOSE_WRITE=8;public static FileObserver latest;public boolean stopped;public int stops;public FileObserver(String path,int mask){latest=this;}public void startWatching(){}public void stopWatching(){stopped=true;stops++;}public abstract void onEvent(int event,String path);public void emit(String path){onEvent(MOVED_TO,path);}}
