package com.project7.localmanager;

import android.content.Context;
import android.content.res.AssetManager;
import java.io.*;
import java.lang.reflect.*;
import java.nio.charset.StandardCharsets;
import java.nio.file.*;
import java.util.*;

/** Finite v63/f81b host: current compiled OWN, full stage assets, real manager
 * dispatch. The production ending-trigger catalog has no nonzero failed event,
 * so both ordinary and reliable requests must produce typed false without any
 * profile/week/event mutation.
 */
public final class EndingTriggerHost {
    static final String ACCOUNT="host_ending_v63_synthetic";
    static final String METHOD="requestTriggerEventByEnding";
    static final byte[] ID=new byte[12];
    static final int ENDING_EVENT=8029, ENDING_ID=1, REQUEST_EVENT=8029;
    static void check(boolean value,String message){if(!value)throw new AssertionError(message);}
    static Object get(Object owner,String name)throws Exception{java.lang.reflect.Field f=owner.getClass().getDeclaredField(name);f.setAccessible(true);return f.get(owner);}
    static Method method(Class<?> owner,String name,Class<?>...types)throws Exception{Method m=owner.getDeclaredMethod(name,types);m.setAccessible(true);return m;}
    static byte[] md5(String value){return RequestEventCatalog.hash("MD5",value.getBytes(StandardCharsets.UTF_8));}
    static final class Fixture implements AutoCloseable {
        final Path root;
        final LocalProfileStore store;
        final LocalTutorialStore tutorials;
        final LocalGatewayServer gateway;
        final LocalEventEngine engine;
        final LocalTutorialStore.Progress progress;
        final File profile;
        Fixture(File stageAssets)throws Exception {
            root=Files.createTempDirectory("p7-ending-trigger-v63-");
            Files.createDirectories(root.resolve("profiles"));
            Context context=new Context(root.toFile(),new AssetManager(stageAssets));
            CoreDrawPolicy.prepare(context);
            HistoryDrawPolicy.prepare(context);
            SelectorPolicy.prepare(context);
            DynamicDrawPolicy.prepare(context);
            StoryMissionBridge.prepare(context);
            StoryCityPolicy.prepare(context);
            OfflineMechanismGateway.prepare(context);
            RequestEventGateway.prepare(context);
            store=new LocalProfileStore(context);tutorials=new LocalTutorialStore(context);
            profile=root.resolve("profiles/"+ACCOUNT+".bson").toFile();
            byte[]publicTemplate=Files.readAllBytes(new File(stageAssets,"new_player.bson").toPath());
            Files.write(profile.toPath(),BsonLite.withAccountIdentity(publicTemplate,ACCOUNT,900003));
            progress=LocalTutorialStore.Progress.fresh();
            progress.initPrologue=false;progress.inEmergency=false;progress.weekIndex=0;
            progress.weekCommit="host_ending_v63_cycle";progress.availableEvents.clear();
            progress.processingEvents.clear();progress.processingNewbees.clear();
            progress.completedEvents.add(ENDING_EVENT);
            byte[] raw=store.load(ACCOUNT,progress);
            byte[] week=BsonLite.documentValue(raw,"weeknum");
            week=BsonLite.withProfileInt(week,"w",0);week=BsonLite.withProfileInt(week,"d",0);
            raw=BsonLite.withProfileDocument(raw,"weeknum",week);
            byte[] std=BsonLite.documentValue(raw,"std");
            if(std==null)std=BsonLite.EMPTY_DOCUMENT;
            std=BsonLite.withProfileBool(std,"cef",false);
            std=BsonLite.withProfileArray(std,"ed",Collections.<Integer>emptyList());
            raw=BsonLite.withProfileDocument(raw,"std",std);
            byte[] result=BsonLite.document("version",2,"week",0,"event",ENDING_EVENT,"ending",ENDING_ID,
                    "score",BsonLite.EMPTY_DOCUMENT,"reward",BsonLite.EMPTY_DOCUMENT);
            raw=BsonLite.withProfileDocument(raw,"q7WeekResult",result);
            raw=BsonLite.withoutProfileKey(raw,"q7WeekTransition");
            raw=BsonLite.withoutProfileKey(raw,"q7Battle");
            Files.write(profile.toPath(),raw);
            LocalEventCatalog graph=new LocalEventCatalog(new FileInputStream(new File(stageAssets,"event_graph.tsv")));
            LocalNewbeeCatalog newbees=new LocalNewbeeCatalog(new ByteArrayInputStream(new byte[0]));
            engine=new LocalEventEngine(graph,newbees,progress,0,raw,true);
            progress.availableEvents.clear();progress.processingEvents.clear();progress.processingNewbees.clear();
            tutorials.save(ACCOUNT,progress);
            gateway=new LocalGatewayServer(0,null,store,tutorials,graph,newbees,null,null,(status,message)->{});
        }
        public void close()throws Exception{
            gateway.close();
            try(java.util.stream.Stream<Path> stream=Files.walk(root)){
                for(Path path:(Iterable<Path>)stream.sorted(Comparator.reverseOrder())::iterator)Files.delete(path);
            }
        }
    }

    static List<ProtoLite.EntityMessage> frames(byte[] wire)throws IOException{
        List<ProtoLite.EntityMessage> result=new ArrayList<>();
        java.nio.ByteBuffer buffer=java.nio.ByteBuffer.wrap(wire).order(java.nio.ByteOrder.LITTLE_ENDIAN);
        while(buffer.hasRemaining()){
            int length=buffer.getInt();check(buffer.getShort()==5,"original frame opcode");
            byte[] payload=new byte[length-2];buffer.get(payload);result.add(ProtoLite.parseEntityMessage(payload));
        }
        return result;
    }
    static int count(List<ProtoLite.EntityMessage> frames,String name)throws IOException{
        int count=0;for(ProtoLite.EntityMessage frame:frames)if(Arrays.equals(frame.methodMd5,md5(name)))count++;
        return count;
    }
    static Boolean triggerResult(List<ProtoLite.EntityMessage> frames)throws IOException{
        for(ProtoLite.EntityMessage frame:frames)if(Arrays.equals(frame.methodMd5,md5("replyTriggerEventByEnding")))
            return BsonLite.boolValue(frame.parameters,"r");
        return null;
    }
    static int callbacks(List<ProtoLite.EntityMessage> frames,int id)throws IOException{
        int count=0;for(ProtoLite.EntityMessage frame:frames)if(Arrays.equals(frame.methodMd5,md5("serverCallbackCarrier"))){
            check(BsonLite.intValue(frame.parameters,"_cbid_")==id,"callback identity");count++;
        }
        return count;
    }
    static String names(List<ProtoLite.EntityMessage> frames)throws IOException{
        StringBuilder out=new StringBuilder();
        for(ProtoLite.EntityMessage frame:frames){
            String name="other";
            for(String candidate:new String[]{"reliableRpcAck","replyTriggerEventByEnding","pushEvents",
                    "syncEventEffects","serverCallbackCarrier","showMessageStr","updateStoryFlag"})
                if(Arrays.equals(frame.methodMd5,md5(candidate)))name=candidate;
            if(out.length()>0)out.append(',');
            out.append(name);
        }
        return out.toString();
    }

    static void canonicalUnchanged(byte[] before,byte[] after,String prefix)throws Exception{
        for(String key:new String[]{"weeknum","std","q7WeekResult","q7EndingEvents","q7CgClaims",
                "q7CgNotices","eventTrigger"}){
            byte[] left=BsonLite.documentValue(before,key);
            byte[] right=BsonLite.documentValue(after,key);
            check(Arrays.equals(left,right),prefix+" canonical "+key+" unchanged");
        }
    }
    public static void main(String[] args)throws Exception{
        File stageAssets=new File(args[0]);
        String output=args[1];
        org.json.JSONObject cases=new org.json.JSONObject();
        // Ordinary authenticated dispatch through the real patched manager.
        try(Fixture f=new Fixture(stageAssets)){
            Method direct=method(LocalGatewayServer.class,"handleServiceRpc",OutputStream.class,byte[].class,
                    byte[].class,byte[].class,String.class,LocalTutorialStore.Progress.class,LocalEventEngine.class);
            ByteArrayOutputStream out=new ByteArrayOutputStream();
            byte[] rawBeforeWarm=Files.readAllBytes(f.profile.toPath());
            // Stock snapshot reconciles known daily/login bookkeeping (ldd keys and
            // city.jpvt) before the request. Capture after that, then require the
            // request itself to leave the profile bytes and these canonical
            // event/week/claim/ending documents untouched.
            f.store.snapshot(ACCOUNT,f.progress);
            Properties before=f.progress.toProperties();byte[] profileBefore=Files.readAllBytes(f.profile.toPath());
            Object consumed=direct.invoke(f.gateway,out,ID,md5(METHOD),
                    BsonLite.document("e",REQUEST_EVENT,"_cbid_",601),ACCOUNT,f.progress,f.engine);
            check(Boolean.TRUE.equals(consumed),"ordinary dispatch consumed by shared gateway");
            List<ProtoLite.EntityMessage> messages=frames(out.toByteArray());
            check(Boolean.FALSE.equals(triggerResult(messages)),"ordinary production no-rule r=false");
            check(count(messages,"reliableRpcAck")==0,"ordinary path emits no ACK");
            check(count(messages,"pushEvents")==0&&count(messages,"syncEventEffects")==0,
                    "ordinary rejection publishes no event mutation");
            check(callbacks(messages,601)==1,"ordinary typed callback");
            check(f.progress.toProperties().equals(before),"ordinary Progress unchanged");
            byte[] profileAfter=Files.readAllBytes(f.profile.toPath());
            check(Arrays.equals(profileBefore,profileAfter),"ordinary request did not mutate profile");
            canonicalUnchanged(rawBeforeWarm,profileAfter,"ordinary");
            cases.put("ordinary_dispatch",names(messages));

            Method reliable=method(LocalGatewayServer.class,"handleReliableRpc",OutputStream.class,byte[].class,
                    byte[].class,String.class,LocalTutorialStore.Progress.class,LocalEventEngine.class,
                    Set.class,Set.class,Map.class,Set.class);
            byte[] envelope=BsonLite.document("w",BsonLite.document("m",METHOD,
                    "p",BsonLite.document("e",REQUEST_EVENT,"_cbid_",602),"r",1),"_cbid_",602);
            ByteArrayOutputStream reliableOut=new ByteArrayOutputStream();
            byte[] rawBeforeReliable=Files.readAllBytes(f.profile.toPath());
            f.store.snapshot(ACCOUNT,f.progress);
            Properties reliableBefore=f.progress.toProperties();
            byte[] reliableProfileBefore=Files.readAllBytes(f.profile.toPath());
            reliable.invoke(f.gateway,reliableOut,ID,envelope,ACCOUNT,f.progress,f.engine,
                    new HashSet<Integer>(),new HashSet<Integer>(),new HashMap<Integer,LocalPatrolEngine.Result>(),
                    new HashSet<Integer>());
            List<ProtoLite.EntityMessage> reliableMessages=frames(reliableOut.toByteArray());
            check(!reliableMessages.isEmpty()&&Arrays.equals(reliableMessages.get(0).methodMd5,md5("reliableRpcAck")),
                    "reliable ACK first");
            check(Boolean.FALSE.equals(triggerResult(reliableMessages)),"reliable production no-rule r=false");
            check(count(reliableMessages,"pushEvents")==0,"reliable rejection publishes no event mutation");
            check(callbacks(reliableMessages,602)==1,"reliable typed callback");
            check(f.progress.toProperties().equals(reliableBefore),"reliable Progress unchanged");
            check(Arrays.equals(reliableProfileBefore,Files.readAllBytes(f.profile.toPath())),
                    "reliable request did not mutate profile");
            canonicalUnchanged(rawBeforeReliable,Files.readAllBytes(f.profile.toPath()),"reliable");
            cases.put("reliable_dispatch",names(reliableMessages));
        }
        Files.write(Paths.get(output),cases.toString(2).getBytes(StandardCharsets.UTF_8));
        System.out.println("PASS v63/f81b real manager dispatch: production no-rule typed false; no push/effect/completion; Progress/profile unchanged; ordinary no ACK, reliable ACK first");
    }
}
