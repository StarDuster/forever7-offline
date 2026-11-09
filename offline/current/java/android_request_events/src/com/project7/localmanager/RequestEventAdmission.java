package com.project7.localmanager;

import java.lang.reflect.*;
import java.util.*;

/** Stage on an isolated stock engine/Progress under its transaction owner's lock.
 * This class neither persists nor publishes. Never pass a shared live engine:
 * the adapter owns the original store/profile/Progress commit boundary.
 */
public final class RequestEventAdmission {
    private RequestEventAdmission(){}
    public enum Status { UNKNOWN_REQUEST, MISSING_EVENT, GRAPH_MISMATCH, UNRELEASED,
        MUTEX, BUSY, ALREADY_COMPLETED, ALREADY_PROCESSING, CONDITIONS, COMPLETED, STARTED, RUNNER_REJECTED }
    public static final class Prepared {
        public final Status status;
        public final int event;
        public final boolean changed;
        public final Set<Integer> completedNotices, availableNotices, processingNotices;
        private final Object progress;
        private final Map<Field,Object> before;
        private boolean closed, committed;
        Prepared(Status status,int event,boolean changed,Object progress,Map<Field,Object> before){
            this.status=status;this.event=event;this.changed=changed;this.progress=progress;this.before=before;
            completedNotices=delta(progress,before,"completedEvents");
            availableNotices=delta(progress,before,"availableEvents");
            processingNotices=delta(progress,before,"processingEvents");
        }
        /** Call ONLY after the existing authoritative commit succeeded. Publication
         * failure after this point must replay notices, never rollback or rerun. */
        public synchronized void markCommitted(){if(closed)throw new IllegalStateException("Admission closed");committed=true;closed=true;before.clear();}
        /** Proven precommit failure/discard only. Must hold the engine transaction
         * lock and have no concurrent modifications to this isolated candidate.
         * Discard its engine after abort (query/cache internals are not restored). */
        public synchronized void abortBeforeCommit(){if(committed)throw new IllegalStateException("Already committed");if(!closed){restore(progress,before);closed=true;}}
        public boolean admitted(){return status==Status.COMPLETED || status==Status.STARTED || status==Status.ALREADY_COMPLETED || status==Status.ALREADY_PROCESSING;}
    }
    public static Prepared stage(LocalEventEngine engine,RequestEventCatalog catalog,String name,byte[] digest) {
        if(engine==null || catalog==null)throw new IllegalArgumentException("Engine/catalog required");
        if(!Thread.holdsLock(engine))throw new IllegalStateException("Isolated engine transaction monitor required");
        Object mutationProgress=null;Map<Field,Object> rollback=null;
        try {
            RequestEventCatalog.Binding b=catalog.find(name,digest);
            Object progress=field(engine,"progress");
            Map<Field,Object> before=snapshot(progress);mutationProgress=progress;rollback=before;
            if(b==null)return result(Status.UNKNOWN_REQUEST,0,false,progress,before);
            Object graph=field(engine,"catalog");Object event=invoke(graph,"get",new Class<?>[]{int.class},b.event);
            if(event==null)return result(Status.MISSING_EVENT,b.event,false,progress,before);
            if(!matches(event,b))return result(Status.GRAPH_MISMATCH,b.event,false,progress,before);
            if(!(Boolean)field(event,"release"))return result(Status.UNRELEASED,b.event,false,progress,before);
            if(((Collection<?>)field(progress,"completedEvents")).contains(b.event))return result(Status.ALREADY_COMPLETED,b.event,false,progress,before);
            if(((Collection<?>)field(progress,"processingEvents")).contains(b.event))return result(Status.ALREADY_PROCESSING,b.event,false,progress,before);
            if(b.serverIdle && (!((Collection<?>)field(progress,"processingEvents")).isEmpty() ||
                    !((Collection<?>)field(progress,"processingNewbees")).isEmpty()))return result(Status.BUSY,b.event,false,progress,before);
            if((Boolean)invoke(engine,"isMutex",new Class<?>[]{int.class},b.event))return result(Status.MUTEX,b.event,false,progress,before);
            Class<?> triggerClass=Class.forName("com.project7.localmanager.LocalEventCatalog$Trigger");
            Constructor<?> constructor=triggerClass.getDeclaredConstructor(int.class,String[].class);constructor.setAccessible(true);
            Object trigger=constructor.newInstance(b.event,b.triggerColumns());
            if(!(Boolean)invoke(engine,"triggerMatches",new Class<?>[]{triggerClass},trigger))return result(Status.CONDITIONS,b.event,false,progress,before);
            try {
                if(b.completion.equals("immediate")) {
                    if((Integer)field(event,"dialog")!=0 || !((Map<?,?>)field(event,"completeConditions")).isEmpty())return result(Status.GRAPH_MISMATCH,b.event,false,progress,before);
                    invoke(engine,"complete",new Class<?>[]{int.class,boolean.class},b.event,true);
                    if(!((Collection<?>)field(progress,"completedEvents")).contains(b.event))return result(Status.RUNNER_REJECTED,b.event,false,progress,before);
                    return new Prepared(Status.COMPLETED,b.event,true,progress,before);
                }
                @SuppressWarnings("unchecked") Collection<Integer> available=(Collection<Integer>)field(progress,"availableEvents");
                available.add(b.event);
                if(!(Boolean)invoke(engine,"startEvent",new Class<?>[]{int.class},b.event))return result(Status.RUNNER_REJECTED,b.event,false,progress,before);
                return new Prepared(Status.STARTED,b.event,true,progress,before);
            }catch(RuntimeException failure){restore(progress,before);throw failure;}
        }catch(ReflectiveOperationException failure){if(rollback!=null)restore(mutationProgress,rollback);throw new IllegalStateException("Stock request-event ABI mismatch",failure);}
        catch(RuntimeException failure){if(rollback!=null)restore(mutationProgress,rollback);throw failure;}
    }
    /** Stage one exact failure-rule event through the stock startEvent path.
     * The caller has already authenticated the rule and current ending result;
     * no trigger columns or arbitrary client event IDs enter this method. */
    public static Prepared stageEndingTrigger(LocalEventEngine engine,int event) {
        if(engine==null)throw new IllegalArgumentException("Engine required");
        if(!Thread.holdsLock(engine))throw new IllegalStateException("Isolated engine transaction monitor required");
        Object progress=null;Map<Field,Object> before=null;
        try {
            progress=field(engine,"progress");before=snapshot(progress);
            Object graph=field(engine,"catalog");Object row=invoke(graph,"get",new Class<?>[]{int.class},event);
            if(row==null)return result(Status.MISSING_EVENT,event,false,progress,before);
            if(!(Boolean)field(row,"release"))return result(Status.UNRELEASED,event,false,progress,before);
            if(((Collection<?>)field(progress,"completedEvents")).contains(event))return result(Status.ALREADY_COMPLETED,event,false,progress,before);
            if(((Collection<?>)field(progress,"processingEvents")).contains(event))return result(Status.ALREADY_PROCESSING,event,false,progress,before);
            if(!((Collection<?>)field(progress,"processingEvents")).isEmpty() ||
                    !((Collection<?>)field(progress,"processingNewbees")).isEmpty())return result(Status.BUSY,event,false,progress,before);
            if((Boolean)invoke(engine,"isMutex",new Class<?>[]{int.class},event))return result(Status.MUTEX,event,false,progress,before);
            @SuppressWarnings("unchecked") Collection<Integer> available=(Collection<Integer>)field(progress,"availableEvents");
            available.add(event);
            if(!(Boolean)invoke(engine,"startEvent",new Class<?>[]{int.class},event))
                return result(Status.RUNNER_REJECTED,event,false,progress,before);
            return new Prepared(Status.STARTED,event,true,progress,before);
        }catch(ReflectiveOperationException failure){
            if(before!=null)restore(progress,before);
            throw new IllegalStateException("Stock ending-trigger ABI mismatch",failure);
        }catch(RuntimeException failure){
            if(before!=null)restore(progress,before);
            throw failure;
        }
    }
    @SuppressWarnings("unchecked") private static Set<Integer> delta(Object progress,Map<Field,Object> before,String name){
        try{
            Field f=progress.getClass().getDeclaredField(name);f.setAccessible(true);
            Set<Integer> result=new LinkedHashSet<>((Set<Integer>)f.get(progress));
            result.removeAll((Set<Integer>)before.get(f));return Collections.unmodifiableSet(result);
        }catch(ReflectiveOperationException failure){throw new IllegalStateException(failure);}
    }
    private static Prepared result(Status status,int event,boolean changed,Object progress,Map<Field,Object> before){
        restore(progress,before);return new Prepared(status,event,changed,progress,before);
    }
    private static boolean matches(Object e,RequestEventCatalog.Binding b)throws ReflectiveOperationException {
        String[] bits={"emergency","leaveEmergency","completeEnterMainPanel","autoTrigger","autoStart","release","newbee","repeatable"};
        int flags=0;for(int i=0;i<bits.length;i++)if((Boolean)field(e,bits[i]))flags|=1<<i;
        return flags==b.flags && (Integer)field(e,"id")==b.event && (Integer)field(e,"dialog")==b.dialog &&
            (Integer)field(e,"newbeeEvent")==b.newbee && (Integer)field(e,"priority")==b.priority;
    }
    private static Object field(Object owner,String name)throws ReflectiveOperationException {
        Field f=owner.getClass().getDeclaredField(name);f.setAccessible(true);return f.get(owner);
    }
    private static Object invoke(Object owner,String name,Class<?>[] types,Object... args)throws ReflectiveOperationException {
        Method m=owner.getClass().getDeclaredMethod(name,types);m.setAccessible(true);
        try{return m.invoke(owner,args);}catch(InvocationTargetException e){Throwable cause=e.getCause();if(cause instanceof RuntimeException)throw(RuntimeException)cause;if(cause instanceof Error)throw(Error)cause;throw new IllegalStateException(cause);}
    }
    private static Map<Field,Object> snapshot(Object progress)throws IllegalAccessException {
        Map<Field,Object> result=new LinkedHashMap<>();
        for(Field f:progress.getClass().getDeclaredFields())if(!Modifier.isStatic(f.getModifiers())){f.setAccessible(true);result.put(f,copy(f.get(progress)));}return result;
    }
    private static Object copy(Object v){
        if(v instanceof Map){Map<Object,Object> out=new LinkedHashMap<>();for(Map.Entry<?,?> e:((Map<?,?>)v).entrySet())out.put(e.getKey(),copy(e.getValue()));return out;}
        if(v instanceof Set){Set<Object> out=new LinkedHashSet<>();for(Object x:(Set<?>)v)out.add(copy(x));return out;}
        if(v==null || v instanceof String || v instanceof Number || v instanceof Boolean)return v;
        throw new IllegalStateException("Unreviewed Progress member type");
    }
    @SuppressWarnings({"unchecked","rawtypes"}) private static void restore(Object progress,Map<Field,Object> before){
        try{for(Map.Entry<Field,Object> entry:before.entrySet()){
            Field f=entry.getKey();Object current=f.get(progress),value=copy(entry.getValue());
            if(Objects.equals(current,value))continue;
            if(current instanceof Map){((Map)current).clear();((Map)current).putAll((Map)value);}
            else if(current instanceof Set){((Set)current).clear();((Set)current).addAll((Set)value);}
            else {if(Modifier.isFinal(f.getModifiers()))throw new IllegalStateException("Final scalar Progress member");f.set(progress,value);}
        }}catch(IllegalAccessException failure){throw new IllegalStateException(failure);}
    }
}
