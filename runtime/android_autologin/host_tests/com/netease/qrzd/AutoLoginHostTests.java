package com.netease.qrzd;
import java.util.*;
public final class AutoLoginHostTests {
    static void check(boolean condition) { if (!condition) throw new AssertionError(); }
    static final class Harness {
        final Deque<Runnable> queue = new ArrayDeque<>();
        final List<String> values = new ArrayList<>(); final List<Boolean> flags = new ArrayList<>();
        AutoLoginCore.Session session = ready(new Object());
        boolean alive = true, inShow, nativeSlot; int invocations; Runnable duringNative;
        final AutoLoginCore core = new AutoLoginCore(queue::add, (v,b) -> {
            check(!inShow && nativeSlot); values.add(v); flags.add(b);
            if (duringNative != null) { Runnable r = duringNative; duringNative = null; r.run(); }
            nativeSlot = false; // native clears after returning from callback
        }, () -> session, code -> {});
        static AutoLoginCore.Session ready(Object generation) {
            return new AutoLoginCore.Session(generation,true,true,true,new AutoLoginCore.Credentials("synthetic", "test-secret"));
        }
        void show(String mode,String token,String error) {
            nativeSlot = true; invocations++; inShow = true;
            core.show(new AutoLoginCore.Request(mode,token,error), () -> alive,true); inShow = false;
        }
        void drain() { while (!queue.isEmpty()) queue.remove().run(); }
        String token() { String v=values.get(values.size()-1); return v.substring(v.indexOf("\"token\":\"")+9,v.length()-2); }
    }
    public static void main(String[] args) {
        Harness h = new Harness(); h.show("login",null,null); check(h.values.isEmpty() && h.core.isVisible());
        Runnable duplicate = h.queue.peek(); h.drain(); check(h.flags.get(0)); String token = h.token(); UUID.fromString(token);
        duplicate.run(); check(h.values.size()==1 && !h.core.isVisible());
        h.show("accepted","mismatch",null); h.drain(); check(h.flags.get(1));
        h.show("login",null,null); h.drain(); check(!h.flags.get(2)); // unmatched ACK preserves pending
        h.show("discard",token,null); h.drain(); check(h.flags.get(3));
        h.show("login",null,null); h.drain(); check(h.flags.get(4) && !token.equals(h.token()));
        h.show("accepted",h.token(),null); h.drain();
        h.show("login",null,"synthetic failure"); h.drain(); check(!h.flags.get(6));
        h.show("login",null,null); h.core.cancel(); h.drain(); check(!h.flags.get(7));
        Harness dead=new Harness();dead.show("login",null,null);dead.alive=false;dead.drain();
        check(dead.values.isEmpty() && !dead.core.isVisible());
        h.show("login",null,null); h.session=Harness.ready(new Object()); h.drain(); check(!h.flags.get(8));
        h.session=new AutoLoginCore.Session(new Object(),false,true,true,new AutoLoginCore.Credentials("synthetic","test"));
        h.show("login",null,null); h.drain(); check(!h.flags.get(9));
        h.session=Harness.ready(new Object());
        h.show("login",null,null); Runnable stale=h.queue.remove(); h.show("cancel",null,null);
        stale.run(); h.drain(); check(h.values.size()==11 && !h.flags.get(10));
        // Real protocol defers control until native callback returns and slot is cleared.
        h.show("login",null,null);
        h.duringNative=() -> h.queue.add(() -> h.show("accepted",h.token(),null)); h.drain();
        check(h.flags.get(11) && h.flags.get(12));
        h.show("login",null,null); h.drain(); check(h.flags.get(13));
        // Native exception consumes the invocation; even duplicate task must never retry.
        Deque<Runnable> q=new ArrayDeque<>(); int[] calls={0};
        AutoLoginCore c=new AutoLoginCore(q::add,(v,b)->{calls[0]++;throw new LinkageError();},()->Harness.ready(new Object()),s->{});
        c.show(new AutoLoginCore.Request("cancel",null,null),()->true,true);
        Runnable r=q.remove();r.run();r.run();check(calls[0]==1);
        // Every readiness component independently blocks credentials.
        for (int gate=0;gate<3;gate++) {
            Harness blocked=new Harness();
            blocked.session=new AutoLoginCore.Session(new Object(),gate!=0,gate!=1,gate!=2,
                new AutoLoginCore.Credentials("synthetic","test"));
            blocked.show("login",null,null);blocked.drain();check(!blocked.flags.get(0));
        }
        Harness malformed=new Harness(); malformed.nativeSlot=true;
        malformed.core.show(null,()->true,true); malformed.drain();check(!malformed.flags.get(0));
        malformed.core.show(null,()->true,false);malformed.core.cancel();check(malformed.queue.isEmpty());
        // Two Activities share one native slot. A destroyed old Activity must not
        // deliver even false into an unrelated newly registered slot.
        Deque<Runnable> tasks=new ArrayDeque<>();List<String> sent=new ArrayList<>();List<Boolean> confirmed=new ArrayList<>();
        Object owner=new Object();boolean[] oldAlive={true},newAlive={true};
        AutoLoginCore two=new AutoLoginCore(tasks::add,(value,ok)->{sent.add(value);confirmed.add(ok);},
            ()->Harness.ready(owner),code->{}); // new immutable Session each snapshot, SAME owner reference
        two.show(new AutoLoginCore.Request("login",null,null),()->oldAlive[0],true);
        oldAlive[0]=false;tasks.remove().run();check(sent.isEmpty());
        oldAlive[0]=true;
        two.show(new AutoLoginCore.Request("login",null,null),()->oldAlive[0],true);tasks.remove().run();
        String oldValue=sent.get(0);String oldToken=oldValue.substring(oldValue.indexOf("\"token\":\"")+9,oldValue.length()-2);
        // Alive old pending blocks another Activity; no indiscriminate clearing on show.
        two.show(new AutoLoginCore.Request("login",null,null),()->newAlive[0],true);tasks.remove().run();check(!confirmed.get(1));
        oldAlive[0]=false;
        two.show(new AutoLoginCore.Request("login",null,null),()->newAlive[0],true);tasks.remove().run();check(confirmed.get(2));
        check(!sent.get(2).equals(oldValue));
        two.show(new AutoLoginCore.Request("accepted",oldToken,null),()->newAlive[0],true);tasks.remove().run();check(confirmed.get(3));
        two.show(new AutoLoginCore.Request("login",null,null),()->newAlive[0],true);tasks.remove().run();check(!confirmed.get(4));
        two.show(new AutoLoginCore.Request("discard",oldToken,null),()->newAlive[0],true);tasks.remove().run();check(confirmed.get(5));
        two.show(new AutoLoginCore.Request("login",null,null),()->newAlive[0],true);tasks.remove().run();check(!confirmed.get(6));
        // Live queued cancellation retains its sole false ACK.
        two.cancel();two.show(new AutoLoginCore.Request("login",null,null),()->newAlive[0],true);two.cancel();tasks.remove().run();check(!confirmed.get(7));
        // A delayed old-Activity hide must not cancel a newer Activity invocation
        // or clear its already submitted pending token. Host states have explicit identity.
        Deque<Runnable> hideTasks=new ArrayDeque<>();List<Boolean> hideReplies=new ArrayList<>();
        AutoLoginCore scoped=new AutoLoginCore(hideTasks::add,(v,ok)->hideReplies.add(ok),()->Harness.ready(owner),code->{});
        AutoLoginCore.ActivityState oldState=()->true,newState=()->true;
        scoped.show(new AutoLoginCore.Request("login",null,null),newState,true);
        scoped.show(null,oldState,false);hideTasks.remove().run();check(hideReplies.get(0));
        scoped.show(null,oldState,false); // no active invocation: never clear new pending
        scoped.show(new AutoLoginCore.Request("login",null,null),newState,true);hideTasks.remove().run();check(!hideReplies.get(1));
        scoped.cancel();
        scoped.show(new AutoLoginCore.Request("login",null,null),oldState,true);
        scoped.show(null,oldState,false); // cancels exact current old invocation
        scoped.show(new AutoLoginCore.Request("login",null,null),newState,true);
        hideTasks.remove().run();check(hideReplies.size()==2); // stale epoch cannot consume new native slot
        hideTasks.remove().run();check(hideReplies.get(2));
        System.out.println("PASS AutoLoginHostTests: asynchronous single-slot, ACK, token, stale, cancel, readiness, error, exception");
    }
}
