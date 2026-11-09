package com.forever7.offline;
/** Finite leaf model of parent hooks, not Android lifecycle acceptance. */
public class ResourceInitActivity extends android.app.Activity {
    public final java.util.concurrent.atomic.AtomicBoolean cancellation = new java.util.concurrent.atomic.AtomicBoolean();
    public boolean failLaunch, destroyDuringFinish;
    private boolean handedOff;
    protected boolean reusePreparedGame(java.util.concurrent.atomic.AtomicBoolean cancel)throws Exception{return false;}
    protected void prepareGame(java.io.File docs,java.util.List<ResourceImporter.Entry> entries,java.util.concurrent.atomic.AtomicBoolean cancel)throws Exception{}
    protected void preparationStatus(String message){}
    protected boolean gameHandedOff(){return handedOff;}
    protected void preparationAbandoned(){}
    protected void preparationWorkerFinished(){}
    protected void launchGame(){
        if(failLaunch)throw new IllegalStateException("synthetic startActivity failure");
        handedOff=true;
        if(destroyDuringFinish){cancellation.set(true);if(!handedOff)preparationAbandoned();}
    }
}
