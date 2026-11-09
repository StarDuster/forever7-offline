package com.project7.localmanager;
// HOST-ONLY static owner seam. Never packaged; represents the Android Service fields
// needed by the production ManagerLifecycleDriver in a finite JVM host.
final class GatewayService {
 static final Object SAVE_ACCESS=new Object();
 static final java.util.concurrent.atomic.AtomicBoolean RUNNING=new java.util.concurrent.atomic.AtomicBoolean();
 static LocalGatewayServer lastServer;
 static Thread lastServerThread;
 static boolean isRunning(){return RUNNING.get();}
 static boolean saveAccessBlocked(){return RUNNING.get()||(lastServerThread!=null&&lastServerThread.isAlive())||(lastServer!=null&&!lastServer.saveWritersStopped());}
}
