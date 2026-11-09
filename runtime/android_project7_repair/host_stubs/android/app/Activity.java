package android.app;
public class Activity extends android.content.Context {public boolean finishing,destroyed;public int finishes;public boolean isFinishing(){return finishing;}public boolean isDestroyed(){return destroyed;}public void finish(){finishes++;finishing=true;}}
