package com.forever7.offline;
import android.app.*;
import android.os.*;
import com.netease.qrzd.Client;
import java.nio.file.*;
import java.io.*;
import java.util.*;
import java.util.concurrent.*;
import java.util.concurrent.atomic.*;
import java.util.regex.*;

/** Finite real protocol/file tests and explicit Android observer/UI leaf seams. */
public final class RepairHostTests {
 static int groups;
 static void need(boolean b,String message){if(!b)throw new AssertionError(message);}
 static void done(String name){groups++;System.out.println("PASS "+name);}
 static String nonce(Path docs)throws Exception{String s=new String(Files.readAllBytes(docs.resolve(Project7RepairProtocol.LAUNCH)),"US-ASCII");Matcher m=Pattern.compile("[0-9a-f]{32}").matcher(s);need(m.find(),"launch nonce");return m.group();}
 static void request(Path docs,String nonce,String code)throws Exception{Project7RepairProtocol.write(docs.resolve(Project7RepairProtocol.REQUEST).toFile(),"{\"code\":\""+code+"\",\"generation\":\""+nonce+"\",\"schema\":1}");}
 static void protocol(Path docs)throws Exception{
  AtomicInteger accepted=new AtomicInteger();Project7RepairProtocol.Session a=Project7RepairProtocol.create(docs.toFile(),ignored->accepted.incrementAndGet());String n=nonce(docs);
  need(Files.size(docs.resolve(Project7RepairProtocol.LAUNCH))==256,"bounded launch");
  request(docs,"00000000000000000000000000000000","resource_verify_failed");a.inspect();
  request(docs,n,"unknown_code");a.inspect();
  Files.write(docs.resolve(Project7RepairProtocol.REQUEST),new byte[257]);a.inspect();
  Files.write(docs.resolve(Project7RepairProtocol.REQUEST),"{}".getBytes("US-ASCII"));a.inspect();need(accepted.get()==0&&a.active(),"invalid input consumed current session");
  request(docs,n,"resource_verify_failed");a.inspect();a.inspect();need(accepted.get()==1&&!a.active(),"valid request not exactly once");
  Project7RepairProtocol.Session b=Project7RepairProtocol.create(docs.toFile(),ignored->accepted.incrementAndGet());String nn=nonce(docs);need(!n.equals(nn),"new original attempt nonce");
  request(docs,n,"resource_query_failed");b.inspect();need(accepted.get()==1,"stale launch accepted");b.close();request(docs,nn,"resource_query_failed");b.inspect();need(accepted.get()==1,"closed session accepted late request");
  done("fixed_size_allowlisted_protocol_rejects_partial_large_unknown_stale_duplicate_and_closed_requests");
 }
 static void host(Path docs)throws Exception{
  Application app=new Application();AtomicInteger repairs=new AtomicInteger();AtomicReference<Project7RepairHost.Lease> accepted=new AtomicReference<>();
  Project7RepairHost.Lease watch=Project7RepairHost.watch(app,docs.toFile(),lease->{repairs.incrementAndGet();accepted.set(lease);});FileObserver observer=FileObserver.latest;
  need(app.registrations==1&&AlertDialog.latest==null&&watch.active(),"normal path made UI or failed setup");Client old=new Client();app.callbacks.onActivityResumed(old);
  observer.emit("unrelated");request(docs,nonce(docs),"resource_verify_failed");observer.emit(Project7RepairProtocol.REQUEST);observer.emit(Project7RepairProtocol.REQUEST);
  need(repairs.get()==1&&observer.stops==1&&!watch.active(),"observer/notification cleanup not once");
  CompletableFuture<Void> drained=new CompletableFuture<>();accepted.get().awaitDrain(drained);Handler.pump();AlertDialog waiting=AlertDialog.latest;
  need(waiting!=null&&waiting.positive==null&&old.finishes==0,"blocked drain enabled finish");waiting.press();need(old.finishes==0,"waiting UI finished Client");
  app.callbacks.onActivityPaused(old);need(waiting.dismissed,"background UI retained activity");old.destroyed=true;app.callbacks.onActivityDestroyed(old);Handler.pump();need(!drained.isDone(),"destroy fabricated drain ACK");
  Client next=new Client();app.callbacks.onActivityResumed(next);AlertDialog still=AlertDialog.latest;need(still.positive==null,"new resumed Client bypassed stuck writer gate");
  drained.complete(null);need(next.finishes==0,"completion finished outside UI action/main");Handler.pump();AlertDialog ready=AlertDialog.latest;need(ready.positive!=null,"actual drain did not enable UI exit");
  app.callbacks.onActivityPaused(next);Client latest=new Client();app.callbacks.onActivityResumed(latest);ready.press();need(next.finishes==0,"stale button finished old Activity");AlertDialog.latest.press();need(latest.finishes==1&&old.finishes==0,"real current resumed Client not finished after true drain");
  done("real_drain_gates_main_thread_exit_background_destroy_is_not_ack_and_stale_activity_cannot_finish");
  CompletableFuture<Void> failed=new CompletableFuture<>();Project7RepairHost.Lease second=Project7RepairHost.watch(app,docs.toFile(),lease->lease.awaitDrain(failed));request(docs,nonce(docs),"resource_download_failed");FileObserver.latest.emit(Project7RepairProtocol.REQUEST);failed.completeExceptionally(new IOException("synthetic actual drain failed"));Handler.pump();Client fail=new Client();app.callbacks.onActivityResumed(fail);need(AlertDialog.latest.positive==null&&fail.finishes==0,"exceptional drain enabled exit");need(app.registrations==1,"registered lifecycle on every lease");second.close();
  done("exceptional_drain_never_enables_finish_and_lifecycle_tracker_is_process_singleton");
 }
 static void interop(Path docs,String python,String sender)throws Exception{
  AtomicInteger accepted=new AtomicInteger();Project7RepairProtocol.Session session=Project7RepairProtocol.create(docs.toFile(),ignored->accepted.incrementAndGet());
  Process process=new ProcessBuilder(python,sender,docs.toString()).redirectErrorStream(true).start();
  need(process.waitFor(10,TimeUnit.SECONDS)&&process.exitValue()==0,"actual Python notification process failed");session.inspect();need(accepted.get()==1,"Java did not accept actual Python wire");
  done("actual_python_atomic_marker_is_accepted_by_real_java_bounded_protocol");
 }
 public static void main(String[]args)throws Exception{Path docs=Files.createTempDirectory("p7-repair-host-");try{protocol(docs);host(docs);interop(docs,args[0],args[1]);}finally{try(java.util.stream.Stream<Path>s=Files.walk(docs)){s.sorted(Comparator.reverseOrder()).forEach(p->{try{Files.delete(p);}catch(IOException e){throw new RuntimeException(e);}});}}System.out.println("REPAIR_HOST_GROUPS_PASSED="+groups);}
}
