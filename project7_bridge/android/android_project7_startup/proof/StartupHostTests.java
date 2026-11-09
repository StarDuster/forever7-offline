package com.project7.localmanager;

import android.content.Context;
import com.forever7.offline.Project7ResourceInitActivity;
import com.forever7.offline.ResourceImporter;
import com.forever7.offline.Project7RepairHost;
import java.util.function.Consumer;
import com.netease.qrzd.AutoLoginCore;
import java.io.File;
import java.io.IOException;
import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.CompletableFuture;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicBoolean;
import java.util.concurrent.atomic.AtomicReference;

/** Injected finite orchestration proofs only, never real resources/account/game. */
public final class StartupHostTests {
    private static int passed;
    private static final Context APP = new Context();
    private static final String HASH = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa";
    private static void check(boolean value,String message){if(!value)throw new AssertionError(message);}
    private static void done(String name){passed++;System.out.println("PASS "+name);}
    private static void await(CountDownLatch latch)throws Exception{if(!latch.await(2,TimeUnit.SECONDS))throw new AssertionError("latch timeout");}
    private static final class FakeBackend implements Project7StartupCoordinator.Backend {
        final CompletableFuture<Void> ready=new CompletableFuture<>(), drained=new CompletableFuture<>();
        final CountDownLatch entered=new CountDownLatch(1);
        final Project7StartupCoordinator.Guard guard;
        boolean hook=true, ownerReady, failed, immediate=true;
        int closeCalls, closeRequests;
        StableIdentityBootstrap.PreparedIdentity identity;
        AutoLoginCore.Credentials credentials;
        FakeBackend(Project7StartupCoordinator.Guard guard){this.guard=guard;replaceIdentity(false);}
        void replaceIdentity(boolean profileOnly){
            StableIdentityBootstrap.Identity id=new StableIdentityBootstrap.Identity("offline_123456789012345678901234",901,"same-value-identity-generation");
            String secret="synthetic-only-not-a-real-secret";
            identity=new StableIdentityBootstrap.PreparedIdentity(new StableIdentityBootstrap.Credentials(id,secret),profileOnly?"identity-profile-only-v1":FullCollectionInitializer.POLICY);
            credentials=new AutoLoginCore.Credentials(id.username(),secret);
        }
        public CompletableFuture<Void> start(){entered.countDown();if(immediate)makeReady();return ready;}
        void makeReady(){ownerReady=true;ready.complete(null);}
        public boolean hookExecuted(){return hook;}
        public boolean ownerReady(){return ownerReady&&!failed;}
        public boolean ownerFailed(){return failed;}
        public StableIdentityBootstrap.PreparedIdentity identity(){return identity;}
        public AutoLoginCore.Credentials credentials(){return credentials;}
        public void closeIfOwned(){closeRequests++;if(hook&&closeCalls==0){closeCalls++;failed=true;ownerReady=false;}}
        public CompletableFuture<Void> drained(){return drained;}
    }
    private static final class FakeServices implements Project7StartupCoordinator.Services {
        boolean foreign, nullReceipt, publishFailure, immediate=true, foreignJoin, profileOnly;
        int publications, backendCount, installs, watches;
        boolean watchFailure, repairDuringWatch;
        FakeRepair repair;
        CountDownLatch publisherEntered=new CountDownLatch(0), publisherRelease=new CountDownLatch(0);
        AutoLoginCore.SessionProvider provider;
        volatile FakeBackend latest;
        final List<String> calls=new ArrayList<>();
        public boolean foreignOwnerActive(){return foreign;}
        public void installProvider(AutoLoginCore.SessionProvider source){installs++;provider=source;}
        public String approvedPolicy(){return FullCollectionInitializer.POLICY;}
        public Project7RepairHost.Lease watchRepair(File docs,Consumer<Project7RepairHost.Lease> callback)throws IOException {
            watches++;if(watchFailure)throw new IOException("synthetic observer failure");
            repair=new FakeRepair(callback);if(repairDuringWatch)repair.fire();return repair;
        }
        public Project7StartupCoordinator.Evidence publish(File docs,List<ResourceImporter.Entry> entries,AtomicBoolean cancel,Project7StartupCoordinator.Status status)throws Exception{
            calls.add("publish");publications++;publisherEntered.countDown();publisherRelease.await();status.update("synthetic status");
            if(publishFailure)throw new IOException("synthetic publication failed");
            return nullReceipt?null:new Project7StartupCoordinator.Evidence(new Object(),HASH,HASH,312);
        }
        public Project7StartupCoordinator.Backend backend(Project7StartupCoordinator.Guard guard){
            calls.add("backend");backendCount++;latest=new FakeBackend(guard);latest.immediate=immediate;latest.hook=!foreignJoin;
            if(profileOnly)latest.replaceIdentity(true);return latest;
        }
    }
    private static final class FakeRepair implements Project7RepairHost.Lease {
        boolean active=true;int waits;CompletableFuture<Void> drain;
        final Consumer<Project7RepairHost.Lease> callback;
        FakeRepair(Consumer<Project7RepairHost.Lease> callback){this.callback=callback;}
        public boolean active(){return active;}
        public void close(){active=false;}
        public void awaitDrain(CompletableFuture<Void> future){waits++;drain=future;}
        void fire(){active=false;callback.accept(this);} // Can deliberately replay even after close.
    }
    private static Project7StartupCoordinator core(FakeServices services){return new Project7StartupCoordinator(APP,services);}
    private static void prepare(Project7StartupCoordinator core,Project7StartupCoordinator.Ticket ticket)throws Exception{
        try{core.prepare(ticket,new File("/synthetic-documents-not-read"),new ArrayList<ResourceImporter.Entry>(),message->{});}
        finally{core.workerFinished(ticket);}
    }
    private static void fails(Throwing operation)throws Exception{try{operation.run();throw new AssertionError("expected rejection");}catch(IOException expected){}}
    private interface Throwing{void run()throws Exception;}
    private static Thread preparing(Project7StartupCoordinator core,Project7StartupCoordinator.Ticket ticket,AtomicReference<Throwable> result){
        Thread thread=new Thread(()->{try{prepare(core,ticket);}catch(Throwable error){result.set(error);}});thread.start();return thread;
    }
    private static void publicationBeforeBackend()throws Exception{
        FakeServices s=new FakeServices();s.publisherEntered=new CountDownLatch(1);s.publisherRelease=new CountDownLatch(1);s.immediate=false;
        Project7StartupCoordinator c=core(s);Project7StartupCoordinator.Ticket t=c.reserve(new AtomicBoolean(),null);
        AtomicReference<Throwable> result=new AtomicReference<>();Thread worker=preparing(c,t,result);await(s.publisherEntered);
        check(c.currentSession()==null&&s.backendCount==0,"backend started without fresh proof");
        s.publisherRelease.countDown();while(s.latest==null)Thread.sleep(2);await(s.latest.entered);
        check(c.currentSession()==null,"provider ready before owned bind");s.latest.makeReady();worker.join(2000);
        check(!worker.isAlive()&&result.get()==null&&c.currentSession()!=null,"valid pipeline did not complete");
        check(s.calls.indexOf("publish")<s.calls.indexOf("backend"),"publication order changed");
        done("fresh_publication_precedes_backend_and_all_ready_gates_precede_provider");
    }
    private static void missingProofAndProfileOnly()throws Exception{
        for(boolean failure:new boolean[]{false,true}){
            FakeServices s=new FakeServices();s.nullReceipt=!failure;s.publishFailure=failure;Project7StartupCoordinator c=core(s);
            Project7StartupCoordinator.Ticket t=c.reserve(new AtomicBoolean(),null);fails(()->prepare(c,t));
            check(s.backendCount==0&&c.currentSession()==null,"missing receipt created profile/backend");
        }
        FakeServices s=new FakeServices();s.profileOnly=true;Project7StartupCoordinator c=core(s);Project7StartupCoordinator.Ticket t=c.reserve(new AtomicBoolean(),null);
        fails(()->prepare(c,t));check(c.currentSession()==null&&s.latest.closeCalls==1,"profile-only pretended full collection ready");
        done("no_receipt_or_profile_only_policy_cannot_publish_game_credentials");
    }
    private static void concurrentTicketAndRetry()throws Exception{
        FakeServices s=new FakeServices();Project7StartupCoordinator c=core(s);AtomicBoolean flag=new AtomicBoolean();
        Project7StartupCoordinator.Ticket first=c.reserve(flag,null);
        fails(()->c.reserve(new AtomicBoolean(),null));
        c.workerFinished(first);
        Project7StartupCoordinator.Ticket retry=c.reserve(flag,first);
        check(retry!=first&&!retry.reusesHandedOffGame()&&s.publications==0&&s.backendCount==0,"retry reused an old worker ticket or did IO early");
        prepare(c,retry);AutoLoginCore.Session a=c.currentSession(),b=c.currentSession();
        check(a.generation==b.generation&&!(a.generation instanceof String),"generation is equal-value token instead of Attempt object");
        done("atomic_ticket_blocks_other_activity_and_own_retry_reuses_attempt_object");
    }
    private static void successfulHandoffAndReuse()throws Exception{
        FakeServices s=new FakeServices();Project7StartupCoordinator c=core(s);AtomicBoolean activity=new AtomicBoolean();
        Project7StartupCoordinator.Ticket t=c.reserve(activity,null);prepare(c,t);Object generation=c.currentSession().generation;
        c.requireHandoff(t);activity.set(true); // normal finish can set this before marker callback returns
        c.handedOff(t);c.abandon(t);check(c.currentSession()!=null&&s.latest.closeCalls==0,"normal finish stopped process owner");
        s.foreign=true; // The live process owner is ours, not a foreign reservation.
        Project7StartupCoordinator.Ticket lease=c.reserve(new AtomicBoolean(),null);
        check(lease.reusesHandedOffGame()&&c.currentSession().generation==generation,"reuse replaced original attempt/proof");
        c.abandon(lease);c.handedOff(lease);
        check(s.publications==1&&s.backendCount==1&&s.installs==1&&s.latest.closeCalls==0,"reuse repeated initialization or closed game");
        done("handoff_ignores_normal_activity_finish_and_reuses_original_receipt_generation");
    }
    private static void cancelledLatePublisherCannotTouchNewAttempt()throws Exception{
        FakeServices s=new FakeServices();s.publisherEntered=new CountDownLatch(1);s.publisherRelease=new CountDownLatch(1);
        Project7StartupCoordinator c=core(s);Project7StartupCoordinator.Ticket old=c.reserve(new AtomicBoolean(),null);
        AtomicReference<Throwable> result=new AtomicReference<>();Thread worker=preparing(c,old,result);await(s.publisherEntered);c.abandon(old);
        fails(()->c.reserve(new AtomicBoolean(),null));
        s.publisherRelease.countDown();worker.join(2000);
        check(result.get()!=null&&s.backendCount==0,"late old publisher started backend");
        Project7StartupCoordinator.Ticket fresh=c.reserve(new AtomicBoolean(),null);
        c.abandon(old);prepare(c,fresh);check(c.currentSession()!=null&&s.backendCount==1,"old cleanup affected fresh attempt");
        done("cancelled_late_publisher_cannot_start_or_close_new_attempt");
    }
    private static void closeAndActualDrain()throws Exception{
        FakeServices s=new FakeServices();s.immediate=false;Project7StartupCoordinator c=core(s);
        Project7StartupCoordinator.Ticket t=c.reserve(new AtomicBoolean(),null);AtomicReference<Throwable> error=new AtomicReference<>();
        Thread worker=preparing(c,t,error);while(s.latest==null)Thread.sleep(2);await(s.latest.entered);c.abandon(t);c.abandon(t);
        worker.join(2000);check(error.get()!=null&&s.latest.closeCalls==1&&c.currentSession()==null,"cancel was not idempotent");
        fails(()->c.reserve(new AtomicBoolean(),null));s.latest.drained.complete(null);
        Project7StartupCoordinator.Ticket fresh=c.reserve(new AtomicBoolean(),null);c.abandon(t);
        check(fresh!=t,"restart before actual drain reused old ticket");
        done("cancel_invalidates_provider_once_and_blocks_restart_until_true_drain");
    }
    private static void blockedResourceReaderAndStaleWorkerSignal()throws Exception{
        FakeServices s=new FakeServices();Project7StartupCoordinator c=core(s);
        java.io.PipedInputStream input=new java.io.PipedInputStream();java.io.PipedOutputStream output=new java.io.PipedOutputStream(input);
        CountDownLatch reading=new CountDownLatch(1);AtomicReference<Project7StartupCoordinator.Ticket> owned=new AtomicReference<>();
        Thread worker=new Thread(()->{
            Project7StartupCoordinator.Ticket ticket=null;
            try{ticket=c.reserve(new AtomicBoolean(),null);owned.set(ticket);reading.countDown();input.read();}
            catch(Exception ignored){}
            finally{try{input.close();}catch(Exception ignored){}if(ticket!=null)c.workerFinished(ticket);}
        });worker.start();await(reading);c.abandon(owned.get());
        fails(()->c.reserve(new AtomicBoolean(),null));
        check(s.backendCount==0&&s.publications==0,"resource read gap started another job");
        output.write(1);output.close();worker.join(2000);check(!worker.isAlive(),"synthetic resource reader did not exit");
        Project7StartupCoordinator.Ticket next=c.reserve(new AtomicBoolean(),null);c.workerFinished(next);
        Project7StartupCoordinator.Ticket retry=c.reserve(new AtomicBoolean(),next);c.abandon(retry);c.workerFinished(next);
        fails(()->c.reserve(new AtomicBoolean(),null));c.workerFinished(retry);
        check(c.reserve(new AtomicBoolean(),null)!=null,"true latest-worker completion did not unblock");
        done("blocked_resource_reader_and_old_worker_finally_cannot_fake_resource_drain");
    }
    private static void duplicatePrepareIsNonDestructive()throws Exception{
        FakeServices s=new FakeServices();Project7StartupCoordinator c=core(s);Project7StartupCoordinator.Ticket t=c.reserve(new AtomicBoolean(),null);
        c.prepare(t,new File("/synthetic"),new ArrayList<ResourceImporter.Entry>(),message->{});
        fails(()->c.prepare(t,new File("/synthetic"),new ArrayList<ResourceImporter.Entry>(),message->{}));
        c.workerFinished(t);
        check(c.currentSession()!=null&&s.publications==1&&s.backendCount==1&&s.latest.closeCalls==0,"duplicate prepare replaced/closed active backend");
        done("duplicate_same_worker_prepare_is_rejected_without_closing_live_backend");
    }
    private static void foreignOwnerChecks()throws Exception{
        FakeServices s=new FakeServices();s.foreign=true;Project7StartupCoordinator c=core(s);
        fails(()->c.reserve(new AtomicBoolean(),null));check(s.installs==0&&s.publications==0&&s.backendCount==0,"foreign owner mutated provider/resources");
        s.foreign=false;s.foreignJoin=true;Project7StartupCoordinator.Ticket t=c.reserve(new AtomicBoolean(),null);
        fails(()->prepare(c,t));check(s.latest.closeCalls==0&&c.currentSession()==null,"joined foreign owner was adopted/closed");
        fails(()->c.reserve(new AtomicBoolean(),null));s.latest.drained.complete(null);
        check(c.reserve(new AtomicBoolean(),null)!=null,"foreign real drain did not unblock retry");
        done("foreign_owner_preflight_and_final_hook_proof_never_adopt_or_close_other_session");
    }
    private static void dynamicProviderGates()throws Exception{
        FakeServices s=new FakeServices();Project7StartupCoordinator c=core(s);Project7StartupCoordinator.Ticket t=c.reserve(new AtomicBoolean(),null);prepare(c,t);
        Object generation=c.currentSession().generation;s.latest.failed=true;
        check(c.currentSession()==null&&s.latest.guard.cancelled(),"provider/cancellation ignored owner failure");
        fails(()->c.reserve(new AtomicBoolean(),null));s.latest.drained.complete(null);
        Project7StartupCoordinator.Ticket next=c.reserve(new AtomicBoolean(),null);prepare(c,next);
        check(c.currentSession().generation!=generation&&s.installs==1,"restart epoch/provider changed incorrectly");
        s.latest.replaceIdentity(false);check(c.currentSession()==null,"equal-value replacement identity bypassed reference guard");
        done("provider_rechecks_live_owner_identity_policy_and_uses_new_attempt_epoch_only_after_drain");
    }
    private static final class Actor extends Project7ResourceInitActivity {
        final Project7StartupCoordinator core;
        Actor(Project7StartupCoordinator c){core=c;}
        protected Project7StartupCoordinator coordinator(){return core;}
        void reserve()throws Exception{reusePreparedGame(cancellation);}
        void prepare()throws Exception{try{prepareGame(new File("/synthetic"),new ArrayList<ResourceImporter.Entry>(),cancellation);}finally{preparationWorkerFinished();}}
        void launch(){launchGame();}
        void abandon(){preparationAbandoned();}
    }
    private static void actualSubclassLeafLifecycle()throws Exception{
        FakeServices s=new FakeServices();Project7StartupCoordinator c=core(s);Actor actor=new Actor(c);actor.reserve();actor.prepare();actor.destroyDuringFinish=true;actor.launch();actor.abandon();
        check(c.currentSession()!=null&&s.latest.closeCalls==0,"subclass successful finish abandoned owner");
        FakeServices bad=new FakeServices();Project7StartupCoordinator broken=core(bad);Actor fail=new Actor(broken);fail.reserve();fail.prepare();fail.failLaunch=true;fail.launch();fail.abandon();
        check(broken.currentSession()==null&&bad.latest.closeCalls==1,"startActivity failure did not cancel own attempt");
        done("real_activity_subclass_with_finite_base_leaf_preserves_handoff_and_cleans_failed_launch");
    }
    private static void nativeHandoffRequiresProcessRestartForRepair()throws Exception{
        FakeServices s=new FakeServices();Project7StartupCoordinator c=core(s);Project7StartupCoordinator.Ticket t=c.reserve(new AtomicBoolean(),null);prepare(c,t);
        c.requireHandoff(t); // Dispatch may have reached Client, even if later startActivity reports failure.
        c.abandon(t);s.latest.drained.complete(null);
        fails(()->c.reserve(new AtomicBoolean(),null));
        check(s.publications==1&&s.backendCount==1&&c.currentSession()==null,"uncertain Client dispatch allowed live resource repair");
        FakeServices live=new FakeServices();Project7StartupCoordinator handed=core(live);Project7StartupCoordinator.Ticket h=handed.reserve(new AtomicBoolean(),null);prepare(handed,h);handed.handedOff(h);
        live.latest.failed=true;live.latest.drained.complete(null);
        fails(()->handed.reserve(new AtomicBoolean(),null));
        check(handed.currentSession()==null&&live.publications==1,"manager drain was mistaken for native resource stop");
        done("uncertain_or_unhealthy_client_handoff_never_infers_native_stop_from_java_drain");
    }
    private static void reusedGenerationWithDeadClientPending()throws Exception{
        FakeServices s=new FakeServices();Project7StartupCoordinator c=core(s);Project7StartupCoordinator.Ticket ticket=c.reserve(new AtomicBoolean(),null);prepare(c,ticket);c.handedOff(ticket);
        Object generation=c.currentSession().generation;
        List<Runnable> queue=new ArrayList<>();List<String> inputs=new ArrayList<>();
        AutoLoginCore auto=new AutoLoginCore(queue::add,(value,confirmed)->{if(confirmed)inputs.add(value);},c::currentSession,code->{});
        AtomicBoolean oldAlive=new AtomicBoolean(true);
        auto.show(new AutoLoginCore.Request("login",null,null),oldAlive::get,true);queue.remove(0).run();
        check(inputs.size()==1,"initial synthetic input missing");
        oldAlive.set(false);Project7StartupCoordinator.Ticket lease=c.reserve(new AtomicBoolean(),null);
        check(lease.reusesHandedOffGame()&&c.currentSession().generation==generation,"reuse changed process generation");
        auto.show(new AutoLoginCore.Request("login",null,null),()->true,true);queue.remove(0).run();
        check(inputs.size()==2&&!inputs.get(0).equals(inputs.get(1)),"dead Client pending token blocked fresh same-generation input");
        check(s.publications==1&&s.backendCount==1,"new Client repeated resources/account preparation");
        done("real_autologin_core_allows_new_client_after_dead_pending_with_same_process_attempt");
    }
    private static void statusAndAssetNames()throws Exception{
        FakeServices s=new FakeServices();Project7StartupCoordinator c=core(s);Project7StartupCoordinator.Ticket t=c.reserve(new AtomicBoolean(),null);
        c.prepare(t,new File("/synthetic"),new ArrayList<ResourceImporter.Entry>(),message->{throw new AssertionError("observer failure");});
        check(c.currentSession()!=null,"status observer controlled lifecycle");
        check("script.npk".equals(Project7StartupPlatform.assetName("assets/script.npk"))&&"offline/snapshot.json".equals(Project7StartupPlatform.assetName("offline/snapshot.json")),"asset prefix must strip exactly7 only when prefixed");
        done("status_observer_is_advisory_and_asset_manager_prefix_mapping_is_exact");
    }
    private static void repairBoundToOriginalAttemptAndActualDrain()throws Exception{
        FakeServices s=new FakeServices();Project7StartupCoordinator c=core(s);Project7StartupCoordinator.Ticket t=c.reserve(new AtomicBoolean(),null);prepare(c,t);c.requireHandoff(t);c.handedOff(t);
        FakeRepair original=s.repair;Object generation=c.currentSession().generation;
        check(c.reserve(new AtomicBoolean(),null).reusesHandedOffGame()&&s.watches==1&&s.repair==original&&c.currentSession().generation==generation,"healthy reuse rotated engine nonce/watch");
        original.fire();original.fire();
        check(c.currentSession()==null&&s.latest.closeRequests==1&&original.waits==1&&original.drain==s.latest.drained&&!original.drain.isDone(),"repair did not invalidate/close once or used fake drain");
        fails(()->c.reserve(new AtomicBoolean(),null));s.latest.drained.complete(null);fails(()->c.reserve(new AtomicBoolean(),null));
        check(s.publications==1&&s.backendCount==1,"repair restarted resources in possibly live native process");
        done("repair_retains_original_nonce_on_reuse_invalidates_provider_closes_once_and_waits_actual_drain");
    }
    private static void lateRepairCannotCloseNewAttempt()throws Exception{
        FakeServices s=new FakeServices();Project7StartupCoordinator c=core(s);Project7StartupCoordinator.Ticket old=c.reserve(new AtomicBoolean(),null);prepare(c,old);FakeRepair stale=s.repair;FakeBackend prior=s.latest;
        c.abandon(old);prior.drained.complete(null);Project7StartupCoordinator.Ticket next=c.reserve(new AtomicBoolean(),null);prepare(c,next);stale.fire();
        check(c.currentSession()!=null&&s.latest.closeRequests==0&&prior.closeRequests==1&&stale.waits==0,"old repair callback touched new owner or opened old UI");
        s.repair.close();check(c.currentSession()==null,"stopped watch did not fail provider closed");fails(()->c.reserve(new AtomicBoolean(),null));
        done("cancelled_old_repair_callback_cannot_close_new_owner_and_stopped_watch_cannot_be_reused");
    }
    private static void observerSetupFailureAndImmediateRequest()throws Exception{
        for(boolean early:new boolean[]{false,true}){
            FakeServices s=new FakeServices();s.watchFailure=!early;s.repairDuringWatch=early;Project7StartupCoordinator c=core(s);Project7StartupCoordinator.Ticket t=c.reserve(new AtomicBoolean(),null);fails(()->prepare(c,t));
            check(c.currentSession()==null&&s.latest.closeRequests==1,"observer setup/early signal left credentials or duplicate close");
            if(early)check(s.repair.waits==0,"pre-dispatch repair queued UI for an engine that was never sent");
        }
        done("repair_observer_setup_failure_or_request_during_registration_never_hands_off_credentials");
    }
    public static void main(String[] args)throws Exception{
        android.os.Looper.getMainLooper();
        publicationBeforeBackend();missingProofAndProfileOnly();concurrentTicketAndRetry();successfulHandoffAndReuse();
        cancelledLatePublisherCannotTouchNewAttempt();closeAndActualDrain();blockedResourceReaderAndStaleWorkerSignal();duplicatePrepareIsNonDestructive();foreignOwnerChecks();dynamicProviderGates();actualSubclassLeafLifecycle();nativeHandoffRequiresProcessRestartForRepair();reusedGenerationWithDeadClientPending();statusAndAssetNames();repairBoundToOriginalAttemptAndActualDrain();lateRepairCannotCloseNewAttempt();observerSetupFailureAndImmediateRequest();
        System.out.println("STARTUP_HOST_GROUPS_PASSED="+passed);
    }
}
