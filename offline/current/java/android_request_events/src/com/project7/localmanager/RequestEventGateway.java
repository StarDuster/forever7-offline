package com.project7.localmanager;

import android.content.Context;
import java.io.*;
import java.lang.reflect.*;
import java.nio.charset.StandardCharsets;
import java.util.*;

/** Shared ordinary/reliable request body. The caller owns ACK/sequence transport.
 * No socket, new profile owner, fabricated reply or client-supplied event ID.
 */
public final class RequestEventGateway {
    private static volatile RequestEventCatalog preparedCatalog;
    private static volatile EndingTriggerCatalog endingCatalog;
    private static final String NOTICE_ROOT="q7RequestEventNotice:v2:";
    private static final String ENDING_TRIGGER="requestTriggerEventByEnding";
    private static final String ENDING_RECEIPT_ROOT="q7EndingTrigger:v1:";
    private RequestEventGateway(){}
    public static void prepare(Context context)throws IOException {
        preparedCatalog=RequestEventCatalog.prepare(context);
        endingCatalog=EndingTriggerCatalog.prepare(context);
    }
    /** Host verification only. Production reaches the catalog only through
     * prepare(context) and its source-pinned SHA256. */
    static void prepareEndingForHost(Context context,String expectedSha)throws IOException {
        endingCatalog=EndingTriggerCatalog.prepare(context,expectedSha);
    }
    public static boolean handleDirect(LocalGatewayServer gateway,OutputStream out,byte[] eid,byte[] digest,
            byte[] params,String account,LocalTutorialStore.Progress progress,LocalEventEngine engine)throws IOException {
        RequestEventCatalog catalog=preparedCatalog;
        if(catalog==null)throw new IOException("Request event catalog not prepared");
        if(endingCatalog==null)throw new IOException("Ending-trigger catalog not prepared");
        String method=catalog.requestForDigest(digest);
        if(method==null && digest!=null && Arrays.equals(digest,
                RequestEventCatalog.hash("MD5",ENDING_TRIGGER.getBytes(StandardCharsets.UTF_8))))
            method=ENDING_TRIGGER;
        if(method==null)return false;
        Integer cbid=params==null?null:(Integer)callStatic(type("BsonLite"),"intValue",
                new Class<?>[]{byte[].class,String.class},params,"_cbid_");
        return handleRequest(gateway,out,eid,method,params,cbid,account,progress,engine);
    }
    public static boolean handleAfterAck(LocalGatewayServer gateway,OutputStream out,byte[] eid,String method,
            byte[] params,Integer cbid,String account,LocalTutorialStore.Progress progress,LocalEventEngine engine)throws IOException {
        return handleRequest(gateway,out,eid,method,params,cbid,account,progress,engine);
    }
    public static boolean handleRequest(LocalGatewayServer gateway,OutputStream out,byte[] eid,String method,
            byte[] params,Integer cbid,String account,LocalTutorialStore.Progress progress,LocalEventEngine engine)throws IOException {
        RequestEventCatalog catalog=preparedCatalog;
        if(catalog==null)throw new IOException("Request event catalog not prepared");
        if(ENDING_TRIGGER.equals(method))return handleEndingTrigger(gateway,out,eid,method,params,cbid,account,progress,engine);
        if(!catalog.requests().contains(method))return false;
        if((Boolean)callStatic(type("LocalAccountStore"),"isTemplateAccount",new Class<?>[]{String.class},account)){
            negative(gateway,out,eid,cbid,method,"template account is read only");return true;
        }
        if(engine==null || progress==null){negative(gateway,out,eid,cbid,method,"event engine unavailable");return true;}
        synchronized(engine) {
            if(get(engine,"progress")!=progress)throw new IOException("Live event Progress identity mismatch");
            if(!((Collection<?>)get(engine,"checkingMessages")).isEmpty())throw new IOException("Event evaluator already active");
            Object store=get(gateway,"tutorialStore");
            if(store==null)throw new IOException("Event progress store unavailable");
            LocalEventEngine candidate=fork(engine,progress);
            Object staged=get(candidate,"progress");
            RequestEventAdmission.Prepared admission;
            synchronized(candidate){admission=RequestEventAdmission.stage(candidate,catalog,method,
                    RequestEventCatalog.hash("MD5",method.getBytes(StandardCharsets.UTF_8)));}
            if(!admission.admitted()){
                negative(gateway,out,eid,cbid,method,admission.status.name());return true;
            }
            String noticeKey=noticeScope(method,staged,candidate);
            pruneStale(staged,noticeKey);
            if(admission.changed)enqueue(staged,noticeKey,admission.completedNotices);
            if(admission.changed || !properties(staged).equals(properties(progress))){
                if(!commitCandidate(gateway,account,engine,progress,candidate,staged,admission)){
                    negative(gateway,out,eid,cbid,method,"event save failed");return true;
                }
            }
            // This is intentionally after durable Progress save/adoption.
            // Match the stock immediate-completion callers: Start/End first,
            // then stock effects/delivery, then authoritative push/callback.
            // Publication failure must not restore the old Progress.
            List<Integer> notices=notices(progress,noticeKey);
            for(Integer event:notices){
                emit(gateway,out,eid,"completeEventReplyStart",(byte[])callStatic(type("BsonLite"),"eventRewardDocument",new Class<?>[]{int.class},event.intValue()));
                emit(gateway,out,eid,"completeEventReplyEnd",(byte[])callStatic(type("BsonLite"),"eventDocument",new Class<?>[]{int.class},event.intValue()));
            }
            call(gateway,"syncEventEffects",new Class<?>[]{OutputStream.class,byte[].class,String.class,
                    progress.getClass(),engine.getClass()},out,eid,account,progress,engine);
            emit(gateway,out,eid,"pushEvents",(byte[])callStatic(type("BsonLite"),"eventListsDocument",new Class<?>[]{Iterable.class,Iterable.class},
                    call(engine,"availableEvents",new Class<?>[0]),call(engine,"processingEvents",new Class<?>[0])));
            if(!notices.isEmpty()){
                Object acknowledged=callStatic(progress.getClass(),"fresh",new Class<?>[0]);copyProgress(progress,acknowledged);
                clearNotices(acknowledged,noticeKey);
                call(store,"save",new Class<?>[]{String.class,progress.getClass()},account,acknowledged);
                copyProgress(acknowledged,progress);set(engine,"conditionPass",null);set(engine,"lastScanState",null);invalidateQueries(gateway);
            }
            callback(gateway,out,eid,cbid,method);
            return true;
        }
    }

    /** Commit only after the isolated stock engine produced an admissible change.
     * Returns false for a proved pre-commit image; an uncertain image throws. */
    private static boolean commitCandidate(Object gateway,String account,LocalEventEngine engine,Object progress,
            LocalEventEngine candidate,Object staged,RequestEventAdmission.Prepared admission)throws IOException {
        Object store=get(gateway,"tutorialStore");
        if(store==null)throw new IOException("Event progress store unavailable");
        try {
            call(store,"save",new Class<?>[]{String.class,progress.getClass()},account,staged);
        }catch(IOException failure){
            // A rename exception is not proof of no commit. Read only through
            // the original store and reconcile an exact image.
            Object disk;
            try {disk=call(store,"load",new Class<?>[]{String.class},account);}
            catch(IOException unknown){failure.addSuppressed(unknown);throw failure;}
            if(!properties(staged).equals(properties(disk))){
                if(properties(progress).equals(properties(disk))){
                    synchronized(candidate){admission.abortBeforeCommit();}
                    return false;
                }
                throw new IOException("Uncertain event commit; reconnect required",failure);
            }
        }
        admission.markCommitted();
        adopt(candidate,engine,progress);
        invalidateQueries(gateway);
        return true;
    }
    @SuppressWarnings("unchecked") private static Map<String,Set<Integer>> conditions(Object progress)throws IOException{return(Map<String,Set<Integer>>)get(progress,"eventConditions");}

    private static boolean handleEndingTrigger(LocalGatewayServer gateway,OutputStream out,byte[] eid,String method,
            byte[] params,Integer cbid,String account,LocalTutorialStore.Progress progress,LocalEventEngine engine)throws IOException {
        EndingTriggerCatalog catalog=endingCatalog;
        if(catalog==null)throw new IOException("Ending-trigger catalog not prepared");
        if((Boolean)callStatic(type("LocalAccountStore"),"isTemplateAccount",new Class<?>[]{String.class},account)){
            negativeTrigger(gateway,out,eid,cbid);return true;
        }
        if(engine==null || progress==null){negativeTrigger(gateway,out,eid,cbid);return true;}
        synchronized(engine) {
            if(get(engine,"progress")!=progress)throw new IOException("Live event Progress identity mismatch");
            if(!((Collection<?>)get(engine,"checkingMessages")).isEmpty())throw new IOException("Event evaluator already active");
            if(get(gateway,"tutorialStore")==null)throw new IOException("Event progress store unavailable");
            Integer event=endingEvent(params);
            if(event==null){negativeTrigger(gateway,out,eid,cbid);return true;}
            byte[] profile=profileSnapshot(gateway,account,progress);
            String receipt=endingReceiptScope(progress,profile,event,catalog);
            if(receipt==null){negativeTrigger(gateway,out,eid,cbid);return true;}
            if(hasEndingReceipt(progress,receipt)){
                publishEndingTrigger(gateway,out,eid,account,progress,engine,cbid);
                return true;
            }
            if(endingStatus(profile,progress,event,catalog)!=TriggerStatus.OK){
                negativeTrigger(gateway,out,eid,cbid);return true;
            }
            LocalEventEngine candidate=fork(engine,progress);
            Object staged=get(candidate,"progress");
            RequestEventAdmission.Prepared admission;
            synchronized(candidate){admission=RequestEventAdmission.stageEndingTrigger(candidate,event);}
            if(!admission.admitted()){negativeTrigger(gateway,out,eid,cbid);return true;}
            pruneEndingReceipts(staged,endingReceiptPrefix(progress));
            conditions(staged).put(receipt,new LinkedHashSet<>(Collections.singleton(1)));
            if(!commitCandidate(gateway,account,engine,progress,candidate,staged,admission)){
                negativeTrigger(gateway,out,eid,cbid);return true;
            }
            publishEndingTrigger(gateway,out,eid,account,progress,engine,cbid);
            return true;
        }
    }
    private enum TriggerStatus { OK, BAD_REQUEST, NO_RESULT, WRONG_WEEK, WRONG_ENDING, INELIGIBLE,
        PENDING, BUSY, NO_RULE, AMBIGUOUS, WRONG_EVENT }
    /** Reuse the original week-ending receipt: current week, exact event, mapped
     * ending and completed source event, then the original failed-rule table. */
    private static TriggerStatus endingStatus(byte[] profile,LocalTutorialStore.Progress progress,
            int event,EndingTriggerCatalog catalog)throws IOException {
        Class<?> bson=type("BsonLite");
        byte[] weeknum=(byte[])callStatic(bson,"documentValue",new Class<?>[]{byte[].class,String.class},profile,"weeknum");
        Integer week=weeknum==null?null:(Integer)callStatic(bson,"intValue",new Class<?>[]{byte[].class,String.class},weeknum,"w");
        if(week==null || week<0)return TriggerStatus.NO_RESULT;
        byte[] std=(byte[])callStatic(bson,"documentValue",new Class<?>[]{byte[].class,String.class},profile,"std");
        Boolean cef=std==null?null:(Boolean)callStatic(bson,"boolValue",new Class<?>[]{byte[].class,String.class},std,"cef");
        if(!Boolean.FALSE.equals(cef))return TriggerStatus.INELIGIBLE;
        byte[] result=(byte[])callStatic(bson,"documentValue",new Class<?>[]{byte[].class,String.class},profile,"q7WeekResult");
        if(result==null)return TriggerStatus.NO_RESULT;
        Integer version=(Integer)callStatic(bson,"intValue",new Class<?>[]{byte[].class,String.class},result,"version");
        Integer resultWeek=(Integer)callStatic(bson,"intValue",new Class<?>[]{byte[].class,String.class},result,"week");
        Integer resultEvent=(Integer)callStatic(bson,"intValue",new Class<?>[]{byte[].class,String.class},result,"event");
        Integer resultEnding=(Integer)callStatic(bson,"intValue",new Class<?>[]{byte[].class,String.class},result,"ending");
        if(version==null || version<1 || resultWeek==null || resultEvent==null || resultEnding==null)
            return TriggerStatus.NO_RESULT;
        if(resultWeek!=week)return TriggerStatus.WRONG_WEEK;
        if(!progress.completedEvents.contains(resultEvent))return TriggerStatus.INELIGIBLE;
        int[] ending=catalog.ending(resultEvent);
        if(ending==null || ending.length<3 || ending[0]!=resultEnding)return TriggerStatus.WRONG_ENDING;
        if(progress.weekCommit==null || progress.weekCommit.isEmpty())return TriggerStatus.INELIGIBLE;
        if(nonEmptyDocument(profile,"q7WeekTransition"))return TriggerStatus.PENDING;
        if(nonEmptyDocument(profile,"q7Battle"))return TriggerStatus.BUSY;
        if(Boolean.TRUE.equals(get(progress,"patrolRewardPending")) ||
                !((Collection<?>)get(progress,"processingNewbees")).isEmpty() ||
                !progress.processingEvents.isEmpty())return TriggerStatus.BUSY;
        @SuppressWarnings("unchecked") List<Integer> endings=(List<Integer>)callStatic(bson,"intArrayValues",
                new Class<?>[]{byte[].class,String.class},std,"ed");
        EndingTriggerCatalog.Authorized authorized=catalog.authorize(week,
                endings==null?Collections.<Integer>emptyList():endings);
        if(authorized==null)return TriggerStatus.NO_RULE;
        if(authorized==EndingTriggerCatalog.Authorized.AMBIGUOUS)return TriggerStatus.AMBIGUOUS;
        return authorized.event==event?TriggerStatus.OK:TriggerStatus.WRONG_EVENT;
    }
    private static boolean nonEmptyDocument(byte[] profile,String name)throws IOException {
        byte[] value=(byte[])callStatic(type("BsonLite"),"documentValue",new Class<?>[]{byte[].class,String.class},profile,name);
        return value!=null && !((List<?>)callStatic(type("BsonLite"),"keys",new Class<?>[]{byte[].class},value)).isEmpty();
    }
    private static Integer endingEvent(byte[] params)throws IOException {
        if(params==null)return null;
        Class<?> bson=type("BsonLite");
        @SuppressWarnings("unchecked") List<String> keys=(List<String>)callStatic(bson,"keys",new Class<?>[]{byte[].class},params);
        if(keys==null || !(keys.size()==1 && "e".equals(keys.get(0))) &&
                !(keys.size()==2 && keys.contains("e") && keys.contains("_cbid_")))return null;
        Object value=callStatic(bson,"numericValue",new Class<?>[]{byte[].class,String.class},params,"e");
        if(!(value instanceof Integer) && !(value instanceof Long))return null;
        long number=((Number)value).longValue();
        if(number<=0 || number>Integer.MAX_VALUE)return null;
        return (int)number;
    }
    private static byte[] profileSnapshot(Object gateway,String account,Object progress)throws IOException {
        Object provider=get(gateway,"profileProvider");
        if(provider==null)return null;
        try{return(byte[])callPublic(provider,"snapshot",new Class<?>[]{String.class,progress.getClass()},account,progress);}
        catch(IOException|RuntimeException failure){return null;}
    }
    private static String endingReceiptPrefix(Object progress)throws IOException {
        Object commit=get(progress,"weekCommit");
        if(!(commit instanceof String) || !((String)commit).matches("[A-Za-z0-9_.-]{1,64}"))return "";
        return ENDING_RECEIPT_ROOT+commit+":";
    }
    private static String endingReceiptScope(Object progress,byte[] profile,int event,EndingTriggerCatalog catalog)throws IOException {
        String prefix=endingReceiptPrefix(progress);
        if(prefix.isEmpty() || profile==null)return null;
        Class<?> bson=type("BsonLite");
        byte[] result=(byte[])callStatic(bson,"documentValue",new Class<?>[]{byte[].class,String.class},profile,"q7WeekResult");
        Integer resultEvent=result==null?null:(Integer)callStatic(bson,"intValue",new Class<?>[]{byte[].class,String.class},result,"event");
        if(resultEvent==null || catalog.ending(resultEvent)==null)return null;
        return prefix+resultEvent+":"+event;
    }
    private static boolean hasEndingReceipt(Object progress,String scope)throws IOException {
        Set<Integer> marker=conditions(progress).get(scope);
        return marker!=null && marker.contains(1);
    }
    private static void pruneEndingReceipts(Object progress,String keep)throws IOException {
        Iterator<String> keys=conditions(progress).keySet().iterator();
        while(keys.hasNext()){String key=keys.next();if(key.startsWith(ENDING_RECEIPT_ROOT) && !key.startsWith(keep))keys.remove();}
    }
    private static void publishEndingTrigger(Object gateway,OutputStream out,byte[] eid,String account,
            Object progress,LocalEventEngine engine,Integer cbid)throws IOException {
        call(gateway,"syncEventEffects",new Class<?>[]{OutputStream.class,byte[].class,String.class,
                progress.getClass(),engine.getClass()},out,eid,account,progress,engine);
        emit(gateway,out,eid,"pushEvents",(byte[])callStatic(type("BsonLite"),"eventListsDocument",
                new Class<?>[]{Iterable.class,Iterable.class},call(engine,"availableEvents",new Class<?>[0]),
                call(engine,"processingEvents",new Class<?>[0])));
        byte[] body=(byte[])callStatic(type("BsonLite"),"document",new Class<?>[]{Object[].class},
                (Object)new Object[]{"r",Boolean.TRUE});
        emit(gateway,out,eid,"replyTriggerEventByEnding",body);
        callback(gateway,out,eid,cbid,ENDING_TRIGGER);
    }
    private static void negativeTrigger(Object gateway,OutputStream out,byte[] eid,Integer cbid)throws IOException {
        byte[] body=(byte[])callStatic(type("BsonLite"),"document",new Class<?>[]{Object[].class},
                (Object)new Object[]{"r",Boolean.FALSE});
        emit(gateway,out,eid,"replyTriggerEventByEnding",body);
        callback(gateway,out,eid,cbid,ENDING_TRIGGER);
    }
    private static String noticeScope(String method,Object progress,Object engine)throws IOException {
        String epoch=String.valueOf(get(progress,"weekCommit"))+"|"+get(progress,"weekIndex")+"|"+get(engine,"week");
        return NOTICE_ROOT+RequestEventCatalog.SHA256+":"+RequestEventCatalog.hex(RequestEventCatalog.hash("MD5",method.getBytes(StandardCharsets.UTF_8)))+":"+
                RequestEventCatalog.hex(RequestEventCatalog.hash("SHA-256",epoch.getBytes(StandardCharsets.UTF_8)))+":";
    }
    private static void pruneStale(Object progress,String scope)throws IOException {
        String[] current=scope.split(":",-1);Set<String> authorized=new HashSet<>();
        for(String method:preparedCatalog.requests())authorized.add(RequestEventCatalog.hex(RequestEventCatalog.hash("MD5",method.getBytes(StandardCharsets.UTF_8))));
        Iterator<String> keys=conditions(progress).keySet().iterator();
        while(keys.hasNext()){
            String key=keys.next();if(!key.startsWith("q7RequestEventNotice:"))continue;
            String[] parts=key.split(":",-1);
            if(parts.length!=6 || !parts[1].equals("v2") || !parts[2].equals(current[2]) ||
                    !authorized.contains(parts[3]) || !parts[4].equals(current[4]))keys.remove();
        }
    }
    private static List<Integer> notices(Object progress,String scope)throws IOException {
        Map<String,Set<Integer>> all=conditions(progress);Set<Integer> header=all.get(scope+"count");
        if(header==null){for(String key:all.keySet())if(key.startsWith(scope))throw new IOException("Request notice header missing");return Collections.emptyList();}
        if(header.size()!=1)throw new IOException("Request notice header invalid");
        int count=header.iterator().next();if(count<1 || count>10000)throw new IOException("Request notice count bound");
        List<Integer> result=new ArrayList<>();
        for(int index=0;index<count;index++){
            Set<Integer> value=all.get(scope+index);
            if(value==null || value.size()!=1 || value.iterator().next()<=0)throw new IOException("Request notice sequence invalid");
            result.add(value.iterator().next());
        }
        int entries=0;for(String key:all.keySet())if(key.startsWith(scope))entries++;
        if(entries!=count+1)throw new IOException("Request notice trailing entries");
        return result;
    }
    private static void enqueue(Object progress,String scope,Set<Integer> values)throws IOException {
        if(values.isEmpty())return;Map<String,Set<Integer>> all=conditions(progress);List<Integer> out=new ArrayList<>(notices(progress,scope));
        for(Integer event:values)if(!out.contains(event)){if(event<=0)throw new IOException("Request notice event invalid");out.add(event);}
        if(out.size()>10000)throw new IOException("Request notice bound");
        all.put(scope+"count",new LinkedHashSet<>(Collections.singleton(out.size())));
        for(int index=0;index<out.size();index++)all.put(scope+index,new LinkedHashSet<>(Collections.singleton(out.get(index))));
    }
    private static void clearNotices(Object progress,String scope)throws IOException {Iterator<String> keys=conditions(progress).keySet().iterator();while(keys.hasNext())if(keys.next().startsWith(scope))keys.remove();}
    private static void emit(Object gateway,OutputStream out,byte[] eid,String method,byte[] params)throws IOException {
        byte[] frame=(byte[])callStatic(type("ProtoLite"),"entityMessage",new Class<?>[]{byte[].class,byte[].class,byte[].class},eid,
                RequestEventCatalog.hash("MD5",method.getBytes(StandardCharsets.UTF_8)),params);
        call(gateway,"writeFrame",new Class<?>[]{OutputStream.class,int.class,byte[].class},out,5,frame);
    }
    private static LocalEventEngine fork(LocalEventEngine live,Object progress)throws IOException {
        Class<?> engineClass=live.getClass(),progressClass=progress.getClass();
        Object copy=callStatic(progressClass,"fresh",new Class<?>[0]);
        copyProgress(progress,copy);
        Object graph=get(live,"catalog"),newbees=get(live,"newbeeCatalog");
        byte[] profile=(byte[])get(live,"profile");
        try {
            Constructor<?> ctor=engineClass.getDeclaredConstructor(graph.getClass(),newbees.getClass(),progressClass,int.class,byte[].class,boolean.class);
            ctor.setAccessible(true);
            LocalEventEngine candidate=(LocalEventEngine)ctor.newInstance(graph,newbees,copy,
                    (Integer)get(live,"starterEvent"),profile==null?null:profile.clone(),(Boolean)get(live,"memoizeConditions"));
            // Original constructor runs restore/reevaluate. That is not this
            // request's admission, so discard its candidate Progress changes.
            copyProgress(progress,copy);
            copyEngineContext(live,candidate);
            return candidate;
        }catch(ReflectiveOperationException failure){throw reflectionFailure(failure);}
    }
    private static void adopt(LocalEventEngine candidate,LocalEventEngine live,Object progress)throws IOException {
        copyProgress(get(candidate,"progress"),progress);
        copyEngineContext(candidate,live);
    }
    private static void copyEngineContext(Object source,Object target)throws IOException {
        for(String name:new String[]{"areaClick","clientOperation","date","week","profile","eventBaseline",
                "lastConditionEvaluations","lastConditionRequests","lifecycleScans","triggerChecks"})set(target,name,copy(get(source,name)));
        // A stock condition pass contains its engine/progress context. Never
        // transfer one between engines, even when Progress values are equal.
        set(target,"conditionPass",null);set(target,"lastScanState",null);
        @SuppressWarnings("unchecked") Collection<Object> checking=(Collection<Object>)get(target,"checkingMessages");checking.clear();
    }
    private static void invalidateQueries(Object gateway)throws IOException {
        for(String name:new String[]{"eventQueries","preparedQuery"})((ThreadLocal<?>)get(gateway,name)).remove();
    }
    @SuppressWarnings({"unchecked","rawtypes"}) private static void copyProgress(Object source,Object target)throws IOException {
        if(source.getClass()!=target.getClass())throw new IOException("Progress class generation mismatch");
        for(Field f:source.getClass().getDeclaredFields())if(!Modifier.isStatic(f.getModifiers())){
            try {
                f.setAccessible(true);Object value=copy(f.get(source)),current=f.get(target);
                if(current instanceof Set){((Set)current).clear();((Set)current).addAll((Set)value);}
                else if(current instanceof Map){((Map)current).clear();((Map)current).putAll((Map)value);}
                else {if(Modifier.isFinal(f.getModifiers()))throw new IOException("Unsupported final Progress scalar");f.set(target,value);}
            }catch(IllegalAccessException failure){throw new IOException(failure);}
        }
    }
    private static Object copy(Object value)throws IOException {
        if(value instanceof byte[])return ((byte[])value).clone();
        if(value instanceof Map){Map<Object,Object> result=new LinkedHashMap<>();for(Map.Entry<?,?> e:((Map<?,?>)value).entrySet())result.put(e.getKey(),copy(e.getValue()));return result;}
        if(value instanceof Set){Set<Object> result=new LinkedHashSet<>();for(Object entry:(Set<?>)value)result.add(copy(entry));return result;}
        if(value==null || value instanceof String || value instanceof Number || value instanceof Boolean)return value;
        throw new IOException("Unsupported isolated event state type");
    }
    private static Object properties(Object progress)throws IOException {return call(progress,"toProperties",new Class<?>[0]);}
    private static void negative(Object gateway,OutputStream out,byte[] eid,Integer cbid,String method,String reason)throws IOException {
        Class<?> bson=type("BsonLite"),proto=type("ProtoLite");
        String displayText;
        if(reason.equals("BUSY"))displayText="请先完成当前剧情。";
        else if(reason.equals("CONDITIONS")||reason.equals("MUTEX"))displayText="当前条件未满足。";
        else if(reason.equals("template account is read only"))displayText="预览账号为只读模式。";
        else if(reason.equals("event save failed"))displayText="本次请求未提交，请稍后重试。";
        else displayText="当前离线版本暂时无法处理该请求。";
        byte[] doc=(byte[])callStatic(bson,"document",new Class<?>[]{Object[].class},(Object)new Object[]{"m",displayText});
        byte[] message=(byte[])callStatic(proto,"entityMessage",new Class<?>[]{byte[].class,byte[].class,byte[].class},eid,
                RequestEventCatalog.hash("MD5","showMessageStr".getBytes(StandardCharsets.UTF_8)),doc);
        call(gateway,"writeFrame",new Class<?>[]{OutputStream.class,int.class,byte[].class},out,5,message);
        callback(gateway,out,eid,cbid,method);
    }
    private static void callback(Object gateway,OutputStream out,byte[] eid,Integer cbid,String method)throws IOException {
        if(cbid!=null)call(gateway,"completeCallback",new Class<?>[]{OutputStream.class,byte[].class,int.class,String.class},out,eid,cbid.intValue(),method);
    }
    private static Class<?> type(String name)throws IOException {try{return Class.forName("com.project7.localmanager."+name);}catch(ClassNotFoundException e){throw new IOException(e);}}
    private static Object get(Object owner,String name)throws IOException {try{Field f=owner.getClass().getDeclaredField(name);f.setAccessible(true);return f.get(owner);}catch(ReflectiveOperationException e){throw new IOException("Stock field ABI "+name,e);}}
    private static void set(Object owner,String name,Object value)throws IOException {try{Field f=owner.getClass().getDeclaredField(name);if(Modifier.isFinal(f.getModifiers()))throw new IOException("Refuse final field update");f.setAccessible(true);f.set(owner,value);}catch(ReflectiveOperationException e){throw new IOException("Stock mutable field ABI "+name,e);}}
    private static Object call(Object owner,String name,Class<?>[] types,Object... args)throws IOException{return invoke(owner.getClass(),owner,name,types,args);}
    private static Object callPublic(Object owner,String name,Class<?>[] types,Object... args)throws IOException{
        try{Method m=owner.getClass().getMethod(name,types);m.setAccessible(true);return m.invoke(owner,args);}
        catch(ReflectiveOperationException failure){throw reflectionFailure(failure);}
    }
    private static Object callStatic(Class<?> owner,String name,Class<?>[] types,Object... args)throws IOException{return invoke(owner,null,name,types,args);}
    private static Object invoke(Class<?> owner,Object receiver,String name,Class<?>[] types,Object[] args)throws IOException {
        try{Method m=owner.getDeclaredMethod(name,types);m.setAccessible(true);return m.invoke(receiver,args);}catch(ReflectiveOperationException e){throw reflectionFailure(e);}
    }
    private static IOException reflectionFailure(ReflectiveOperationException failure){
        Throwable cause=failure instanceof InvocationTargetException?((InvocationTargetException)failure).getCause():failure;
        if(cause instanceof IOException)return(IOException)cause;
        if(cause instanceof RuntimeException)throw(RuntimeException)cause;
        if(cause instanceof Error)throw(Error)cause;
        return new IOException("Stock request-event gateway ABI",cause);
    }
}
