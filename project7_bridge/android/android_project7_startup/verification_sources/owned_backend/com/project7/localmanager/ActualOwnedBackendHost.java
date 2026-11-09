package com.project7.localmanager;
import android.content.Context;
import android.content.res.AssetManager;
import java.io.File;
import java.nio.file.Files;
import java.util.concurrent.*;
/** Finite JVM host for the real Project7StartupPlatform.OwnedBackend.
 * Android Service fields are the only host seam; ports 23333/23334 must be free. */
public class ActualOwnedBackendHost {
 public static void main(String[] a)throws Exception{
  File assets=new File(a[0]);
  File root=new File(a[1]).getCanonicalFile();
  if(!root.mkdirs())throw new IllegalStateException("isolated profile directory unavailable");
  Context c=new Context(root,new AssetManager(assets));
  Project7StartupPlatform p=new Project7StartupPlatform(c);
  Project7StartupCoordinator.Guard g=()->false;
  Project7StartupCoordinator.Backend b=p.backend(g);
  try {
  CompletableFuture<Void> f=b.start();
  f.get(120,TimeUnit.SECONDS);
  long end=System.nanoTime()+TimeUnit.SECONDS.toNanos(30);
  while(!b.ownerReady()&&System.nanoTime()<end)Thread.sleep(50);
  System.out.println("READY="+b.ownerReady()+" HOOK="+b.hookExecuted()+" IDENTITY="+(b.identity()!=null)+" CREDS="+(b.credentials()!=null)+" FAILED="+b.ownerFailed());
  if(!b.ownerReady()||!b.hookExecuted()||b.identity()==null||b.credentials()==null||b.ownerFailed())
   throw new AssertionError("Actual backend did not publish ready identity and credentials");
  if(!b.identity().identity().username().equals(b.credentials().username))
   throw new AssertionError("Prepared identity and delivered credentials differ");
  } finally {
  b.closeIfOwned();
  b.drained().get(30,TimeUnit.SECONDS);
  if(SinglePackageGateway.hasActiveProcessReservation()||GatewayService.saveAccessBlocked())
   throw new AssertionError("Owner reservation or save writer leaked after drain");
  System.out.println("DRAINED");
  }
 }
}
