package com.project7.localmanager;

import java.io.File;
import java.io.IOException;
import java.io.OutputStream;
import java.lang.reflect.Field;
import java.lang.reflect.InvocationTargetException;
import java.lang.reflect.Method;
import java.lang.reflect.Modifier;
import java.nio.ByteBuffer;
import java.nio.ByteOrder;
import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collections;
import java.util.HashSet;
import java.util.List;

/** One stock-BSON live CG claim extension. No profile owner, event or Week engine. */
public final class CoreGapBridge {
    static final String RECEIPTS = "_p7_cg_claims_v1";
    private static final byte[] REQUEST = digest("requestMainlineCgRewards");
    private CoreGapBridge() {}

    /** Called only by original authenticated dispatcher; never trust account from params. */
    public static boolean handleResourceRpc(LocalGatewayServer gateway, OutputStream output,
            byte[] entityId, byte[] methodDigest, byte[] parameters, String account) throws IOException {
        if (!Arrays.equals(REQUEST, methodDigest)) return false;
        LocalResourceEngine.Result result;
        try {
            Object provider = unwrapProvider(Access.PROVIDER.get(gateway));
            if (provider == null || provider.getClass() != LocalProfileStore.class) throw new Rejected();
            result = claim((LocalProfileStore) provider, account, parameters);
        } catch (UncertainCommit error) {
            throw error; // ambiguous commit: drop transport, retry reconciles persisted receipt
        } catch (ReflectiveOperationException | RuntimeException | Rejected error) {
            result = failure();
        } catch (IOException error) {
            result = failure(); // only definite precommit/read failure reaches this branch
        }
        // No store/PROFILE_LOCK while calling a socket or UI continuation.
        for (LocalResourceEngine.Reply reply : result.replies) {
            byte[] frame = ProtoLite.entityMessage(entityId, digest(reply.method), reply.parameters);
            invoke(Access.WRITE_FRAME, gateway, output, 5, frame);
        }
        return true;
    }

    static LocalResourceEngine.Result claim(LocalProfileStore store, String account, byte[] parameters)
            throws IOException, ReflectiveOperationException, Rejected {
        if (account == null || !account.matches("[a-z0-9_.-]{1,32}")) throw new Rejected();
        checkDocument(parameters);
        List<String> keys = BsonLite.keys(parameters);
        if (keys.size() != 2 || !new HashSet<>(keys).equals(new HashSet<>(Arrays.asList("li", "cg"))))
            throw new Rejected();
        int line = integer(BsonLite.numericValue(parameters, "li"));
        int cg = integer(BsonLite.numericValue(parameters, "cg"));
        // Exact scalar request encoding rejects trailing malformed/unparsed elements,
        // while retaining either key order and BSON int32/int64 representation.
        byte[] canonical = BsonLite.document(keys.get(0), BsonLite.numericValue(parameters,keys.get(0)),
            keys.get(1), BsonLite.numericValue(parameters,keys.get(1)));
        if (!Arrays.equals(parameters,canonical)) throw new Rejected();
        if (!CgRewardPlan.eligible(line, cg)) throw new Rejected();
        synchronized (store) {
            synchronized (Access.PROFILE_LOCK.get(null)) {
                File directory = (File) Access.DIRECTORY.get(store);
                File file = new File(directory, account + ".bson");
                if (!file.isFile() || !file.getCanonicalFile().getParentFile().equals(directory.getCanonicalFile()))
                    throw new Rejected();
                byte[] current = (byte[]) invoke(Access.READ, null, file);
                checkDocument(current);
                if (!account.equals(BsonLite.stringValue(current, "account")) ||
                        !account.equals(BsonLite.stringValue(current, "an"))) throw new Rejected();
                List<?> owned = array(current, "cgs", false);
                boolean owns = false;
                for (Object value : owned) if (integer(value) == cg) owns = true;
                if (!owns) throw new Rejected();
                byte[] oaed = document(current, "oaed", true);
                List<?> claims = array(oaed, "mcr", true);
                boolean claimed = false;
                List<Object> pairs = new ArrayList<>();
                for (Object entry : claims) {
                    if (!(entry instanceof List) || ((List<?>) entry).size() != 2) throw new Rejected();
                    List<?> pair = (List<?>) entry;
                    int existing = integer(pair.get(0));
                    if (!(pair.get(1) instanceof Boolean)) throw new Rejected();
                    if (existing == cg) claimed = true; // original Python tests dictionary key membership
                    pairs.add(pair);
                }
                byte[] receipts = document(current, RECEIPTS, true);
                List<byte[]> receiptRows = new ArrayList<>();
                byte[] replay = null;
                if (BsonLite.keys(current).contains(RECEIPTS)) {
                    if (!Integer.valueOf(1).equals(BsonLite.intValue(receipts,"schema"))) throw new Rejected();
                    byte[] rows = BsonLite.arrayValue(receipts,"claims");
                    if (rows == null) throw new Rejected();
                    receiptRows.addAll(LocalResourceEngine.array(rows));
                    if (receiptRows.size() != BsonLite.keys(rows).size()) throw new Rejected();
                    HashSet<Integer> seen = new HashSet<>();
                    for (byte[] row : receiptRows) {
                        int id = integer(BsonLite.numericValue(row,"cg"));
                        if (!seen.add(id) || !CgRewardPlan.SHA256.equals(BsonLite.stringValue(row,"plan")) ||
                                integer(BsonLite.numericValue(row,"commit")) < 1) throw new Rejected();
                        byte[] reward = BsonLite.documentValue(row,"reward");
                        if (!Arrays.equals(reward, plannedReward())) throw new Rejected();
                        if (id == cg) replay = reward;
                    }
                }
                if (replay != null && !claimed) throw new Rejected();
                if (BsonLite.keys(current).contains("souvenir")) {
                    Number balance = BsonLite.numericValue(current,"souvenir");
                    if (!(balance instanceof Integer) && !(balance instanceof Long)) throw new Rejected();
                    if (balance.longValue()<0 || balance.longValue()>Integer.MAX_VALUE) throw new Rejected();
                }
                LocalResourceEngine.Result result = new LocalResourceEngine.Result(current);
                if (claimed) {
                    // Legacy claim has no modern receipt: reconcile with EMPTY reward, never invent 700.
                    byte[] reward = replay == null ? result.reward() : replay;
                    success(result, cg, reward);
                    return result;
                }
                LocalResourceEngine.grant(result, store.resources(), "souvenir", CgRewardPlan.ITEM, CgRewardPlan.AMOUNT, 1);
                byte[] reward = result.reward();
                if (!Arrays.equals(reward, plannedReward())) throw new Rejected();
                pairs.add(Arrays.asList(cg, true));
                oaed = BsonLite.withProfileArray(oaed,"mcr",pairs);
                result.profile = BsonLite.withProfileDocument(result.profile,"oaed",oaed);
                receiptRows.add(BsonLite.document("cg",cg,"plan",CgRewardPlan.SHA256,
                    "reward",reward,"commit",Math.addExact(receiptRows.size(),1)));
                receipts = BsonLite.withProfileInt(receipts,"schema",1);
                receipts = BsonLite.withProfileArray(receipts,"claims",receiptRows);
                result.profile = BsonLite.withProfileDocument(result.profile,RECEIPTS,receipts);
                success(result,cg,reward); // construct all replies before durable commit, never emit here
                try {
                    invoke(Access.WRITE,null,file,result.profile);
                } catch (IOException failedWrite) {
                    byte[] observed;
                    try { observed = (byte[]) invoke(Access.READ,null,file); }
                    catch (Exception unreadable) { throw new UncertainCommit(); }
                    if (Arrays.equals(observed,result.profile)) return result; // rename completed despite thrown platform error
                    if (!Arrays.equals(observed,current)) throw new UncertainCommit();
                    throw failedWrite; // definite unchanged profile: false reply is safe
                }
                return result;
            }
        }
    }

    private static void success(LocalResourceEngine.Result result, int cg, byte[] reward) {
        LocalResourceEngine.syncCurrencies(result);
        result.add("replyMainlineCgRewards",BsonLite.document("rs",true,"i",BsonLite.document("cg",cg,"rwd",reward)));
    }
    static LocalResourceEngine.Result failure() {
        LocalResourceEngine.Result result = new LocalResourceEngine.Result(BsonLite.EMPTY_DOCUMENT);
        result.add("replyMainlineCgRewards",BsonLite.document("rs",false,"i",BsonLite.EMPTY_DOCUMENT));
        return result;
    }
    private static byte[] plannedReward() {
        return BsonLite.document("item",Arrays.asList(Arrays.asList(CgRewardPlan.ITEM,CgRewardPlan.AMOUNT)),
            "hero",Collections.emptyList(),"treasure",Collections.emptyList());
    }
    private static int integer(Object value) throws Rejected {
        if (!(value instanceof Integer) && !(value instanceof Long)) throw new Rejected();
        long number = ((Number) value).longValue();
        if (number < 1 || number > Integer.MAX_VALUE) throw new Rejected();
        return (int) number;
    }
    private static List<?> array(byte[] doc, String key, boolean optional) throws Rejected {
        byte[] value = BsonLite.arrayValue(doc,key);
        if (value == null) {
            if (optional && !BsonLite.keys(doc).contains(key)) return Collections.emptyList();
            throw new Rejected();
        }
        checkDocument(value);
        List<String> keys = BsonLite.keys(value);
        for (int i=0;i<keys.size();i++) if (!Integer.toString(i).equals(keys.get(i))) throw new Rejected();
        Object decoded = BsonLite.messagePackValue(value,true);
        if (!(decoded instanceof List)) throw new Rejected();
        return (List<?>) decoded;
    }
    private static byte[] document(byte[] doc, String key, boolean optional) throws Rejected {
        byte[] value = BsonLite.documentValue(doc,key);
        if (value == null) {
            if (optional && !BsonLite.keys(doc).contains(key)) return BsonLite.EMPTY_DOCUMENT;
            throw new Rejected();
        }
        checkDocument(value); return value;
    }
    private static void checkDocument(byte[] bytes) throws Rejected {
        if (bytes == null || bytes.length<5 || bytes[bytes.length-1]!=0 ||
                ByteBuffer.wrap(bytes).order(ByteOrder.LITTLE_ENDIAN).getInt()!=bytes.length) throw new Rejected();
        List<String> keys=BsonLite.keys(bytes);
        if (keys.size()!=new HashSet<>(keys).size()) throw new Rejected();
    }
    private static byte[] digest(String name) {
        try { return MessageDigest.getInstance("MD5").digest(name.getBytes(StandardCharsets.UTF_8)); }
        catch (NoSuchAlgorithmException error) { throw new IllegalStateException("MD5 unavailable"); }
    }
    private static Object invoke(Method method,Object receiver,Object...args) throws IOException {
        try { return method.invoke(receiver,args); }
        catch (InvocationTargetException error) {
            Throwable cause=error.getCause();
            if (cause instanceof IOException) throw (IOException) cause;
            if (cause instanceof RuntimeException) throw (RuntimeException) cause;
            throw new IOException("Stock operation failed",cause);
        } catch (IllegalAccessException error) { throw new IOException("Stock seam inaccessible",error); }
    }
    static final class Rejected extends Exception { private static final long serialVersionUID=1; }
    static final class UncertainCommit extends IOException { private static final long serialVersionUID=1; }
    /** Exact declared members only; no arbitrary name/class supplied by input. */
    private static final class Access {
        static final Field PROVIDER=field(LocalGatewayServer.class,"profileProvider",LocalGatewayServer.ProfileProvider.class,false);
        static final Field PROFILE_LOCK=field(LocalProfileStore.class,"PROFILE_LOCK",Object.class,true);
        static final Field DIRECTORY=field(LocalProfileStore.class,"profilesDirectory",File.class,false);
        static final Method READ=method(LocalProfileStore.class,"readAll",byte[].class,true,File.class);
        static final Method WRITE=method(LocalProfileStore.class,"writeAtomic",void.class,true,File.class,byte[].class);
        static final Method WRITE_FRAME=method(LocalGatewayServer.class,"writeFrame",void.class,false,OutputStream.class,int.class,byte[].class);
        private static Field field(Class<?> owner,String name,Class<?> type,boolean isStatic) {
            try { Field f=owner.getDeclaredField(name);
                if(f.getType()!=type || Modifier.isStatic(f.getModifiers())!=isStatic)throw new NoSuchFieldException();
                f.setAccessible(true);return f;
            } catch(ReflectiveOperationException error){throw new IllegalStateException("Pinned stock field mismatch",error);}
        }
        private static Method method(Class<?> owner,String name,Class<?> result,boolean isStatic,Class<?>...args) {
            try {Method m=owner.getDeclaredMethod(name,args);
                if(m.getReturnType()!=result || Modifier.isStatic(m.getModifiers())!=isStatic)throw new NoSuchMethodException();
                m.setAccessible(true);return m;
            } catch(ReflectiveOperationException error){throw new IllegalStateException("Pinned stock method mismatch",error);}
        }
    }
 private static Object unwrapProvider(Object provider){if(provider==null||!"FailureSafeProfileProvider".equals(provider.getClass().getSimpleName()))return provider;try{java.lang.reflect.Method m=provider.getClass().getDeclaredMethod("delegate");m.setAccessible(true);Object d=m.invoke(provider);if(d!=null)return d;}catch(Exception ignored){}return provider;}
}
