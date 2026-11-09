package com.project7.localmanager;
import android.content.Context;
import java.io.*;
import java.lang.reflect.*;
import java.security.*;
import java.nio.file.Files;
import java.nio.file.LinkOption;
import java.util.*;
import static com.project7.localmanager.CollectionBson.*;

/** One whole-profile in-memory transaction using the pinned original P7 engines.
 * Never a second save, fake H row, count-only receipt shortcut or game-readiness flag.
 */
public final class FullCollectionInitializer implements StableIdentityBootstrap.PostProfileInitializer {
    public static final String POLICY="p7-full-collection-v1";
    static final String RECEIPT="q7FullCollectionReceiptV1";
    interface Engine {
        List<List<Integer>> liberateGroups();byte[] normalize(byte[] p)throws Exception;byte[] heroes(byte[] p)throws Exception;byte[] helper(byte[] p,int id)throws Exception;
        byte[] skins(byte[] p)throws Exception;byte[] treasure(byte[] p,int id,int quality)throws Exception;
        byte[] receipt(byte[] p)throws Exception;
    }
    interface Faults {void check(String point)throws Exception;}
    static final Faults NO_FAULTS=point->{};
    public interface Cancellation {boolean cancelled();}
    private final Faults faults;private final Cancellation cancellation;
    public FullCollectionInitializer(){this(()->false,NO_FAULTS);}
    public FullCollectionInitializer(Cancellation cancellation){this(cancellation,NO_FAULTS);}
    FullCollectionInitializer(Faults faults){this(()->false,faults);}
    private FullCollectionInitializer(Cancellation cancellation,Faults faults){if(cancellation==null||faults==null)throw new IllegalArgumentException("Missing cancellation/fault input");this.cancellation=cancellation;this.faults=faults;}
    static void cancellationPoint(Cancellation cancellation)throws IOException{if(cancellation.cancelled()||Thread.currentThread().isInterrupted())throw new IOException("Collection initialization cancelled");}
    private void checkpoint()throws Exception{cancellationPoint(cancellation);requireStopped();}

    public void initialize(Context app,StableIdentityBootstrap.Identity identity,StableIdentityBootstrap.Stores stores)throws Exception{
        need(app!=null&&identity!=null&&stores!=null&&stores.profiles!=null,"MISSING_BOOTSTRAP_CONTEXT");
        checkpoint();
        // Asset hashes are fixed in source; a disk receipt never supplies trust roots.
        byte[] targetBytes=read(app.getAssets().open("project7_catalog/target-manifest.json"),2*1024*1024);
        CollectionTargets targets=CollectionTargets.load(targetBytes);checkpoint();
        byte[] catalog=read(app.getAssets().open("resources.tsv"),2*1024*1024);need(sha(catalog).equals(CollectionTargets.CATALOG_SHA),"EXTENDED_CATALOG_HASH");
        Object profiles=stores.profiles;
        Class<?> store=Class.forName("com.project7.localmanager.LocalProfileStore");Object lock=CollectionStockBridge.field(store,"PROFILE_LOCK").get(null);
        synchronized(profiles){synchronized(lock){
            checkpoint();Engine engine=new CollectionStockBridge(catalog,targets,profiles);
            File root=app.getFilesDir().getCanonicalFile(),expected=new File(root,"profiles").getAbsoluteFile();need(expected.equals(expected.getCanonicalFile())&&expected.isDirectory(),"PROFILE_DIRECTORY_SYMLINK_OR_MISSING");
            File owned=(File)CollectionStockBridge.field(store,"profilesDirectory").get(profiles);need(owned.getCanonicalFile().equals(expected),"WRONG_STOCK_PROFILE_OWNER");
            String account=identity.username();need(account.matches("[a-zA-Z0-9_.-]{1,128}")&&!account.equals(".")&&!account.equals(".."),"UNSAFE_BOUND_ACCOUNT");
            File file=new File(expected,account+".bson");canonicalRegular(file);
            Method reader=CollectionStockBridge.method(store,"readAll",File.class),writer=CollectionStockBridge.method(store,"writeAtomic",File.class,byte[].class);
            Storage storage=new Storage(){
                public byte[] read()throws Exception{checkpoint();canonicalRegular(file);return (byte[])CollectionStockBridge.invoke(reader,null,file);}
                public void write(byte[] data)throws Exception{
                    // The original writer owns exactly this sibling temporary pathname.
                    File temporary=new File(file.getParentFile(),file.getName()+".tmp");
                    need(!Files.isSymbolicLink(temporary.toPath())&&temporary.getAbsoluteFile().equals(temporary.getCanonicalFile()),"PROFILE_TEMP_SYMLINK");
                    if(Files.exists(temporary.toPath(),LinkOption.NOFOLLOW_LINKS))need(temporary.isFile()&&temporary.delete(),"STALE_PROFILE_TEMP_CLEANUP_FAILED");
                    checkpoint();CollectionStockBridge.invoke(writer,null,file,data);
                }
                public void stopped()throws Exception{checkpoint();}
            };
            transact(storage,engine,targets,account,identity.numericId(),faults);
        }}
    }
    private static void canonicalRegular(File f)throws IOException{need(!Files.isSymbolicLink(f.toPath())&&f.getAbsoluteFile().equals(f.getCanonicalFile())&&f.isFile()&&f.length()>0&&f.length()<=CollectionBson.MAX,"PROFILE_PATH_OR_SIZE");}
    static void requireStopped()throws Exception{
        Class<?> service=Class.forName("com.project7.localmanager.GatewayService");Object access=CollectionStockBridge.field(service,"SAVE_ACCESS").get(null);
        need(Thread.holdsLock(access),"SAVE_ACCESS_NOT_HELD");
        boolean running=(Boolean)CollectionStockBridge.invoke(CollectionStockBridge.method(service,"isRunning"),null);
        boolean blocked=(Boolean)CollectionStockBridge.invoke(CollectionStockBridge.method(service,"saveAccessBlocked"),null);
        need(!running&&!blocked,"SERVICE_OR_SAVE_WRITERS_ACTIVE");
        if(Thread.currentThread().isInterrupted())throw new IOException("Collection initialization interrupted");
    }
    interface Storage {byte[] read()throws Exception;void write(byte[] candidate)throws Exception;void stopped()throws Exception;}
    static void transact(Storage storage,Engine engine,CollectionTargets targets,String account,int uid,Faults faults)throws Exception{
        targets.validate();storage.stopped();byte[] original=storage.read();CollectionValidator.Index before=CollectionValidator.scan(original,targets);identity(before.root,account,uid);receipt(before.root,false);faults.check("AFTER_READ");
        // A durable receipt means first-grant has completed. Missing target treasures
        // are then normal consumption evidence, not repair work.
        if(before.root.get(RECEIPT)!=null){receipt(before.root,true);storage.stopped();need(Arrays.equals(original,storage.read()),"PROFILE_CHANGED_DURING_INITIALIZED_READ");faults.check("AFTER_INITIALIZED_READBACK");return;}
        for(int id:targets.heroes)if(!before.heroes.containsKey(id))need(!before.uuids.contains(String.format(Locale.ROOT,"%08x%016x",id,(long)id)),"DEFAULT_SKIN_UUID_COLLISION");
        byte[] candidate=engine.heroes(original);candidate=normalized(candidate,engine,targets);storage.stopped();faults.check("AFTER_HERO_BATCH");
        candidate=engine.helper(candidate,46);candidate=engine.helper(candidate,125);candidate=normalized(candidate,engine,targets);CollectionValidator.Index approvedLiberate=CollectionValidator.scan(candidate,targets);storage.stopped();faults.check("AFTER_HIDDEN_HELPERS");
        candidate=engine.skins(candidate);storage.stopped();faults.check("AFTER_SKIN_BATCH");
        CollectionValidator.Index index=CollectionValidator.scan(candidate,targets);int granted=0;
        for(CollectionTargets.Treasure t:targets.treasures.values())if(!index.treasures.contains(t.key())){
            storage.stopped();candidate=engine.treasure(candidate,t.id,t.quality);need(candidate!=null&&candidate.length<=CollectionBson.MAX,"CANDIDATE_SIZE_LIMIT");granted++;faults.check("AFTER_TREASURE_"+granted);
        }
        CollectionValidator.Index complete=CollectionValidator.scan(candidate,targets);CollectionValidator.complete(complete,targets);CollectionValidator.newTypes(before,complete,targets);CollectionValidator.preserved(before,complete,approvedLiberate);identity(complete.root,account,uid);storage.stopped();faults.check("AFTER_VALIDATION");
        candidate=engine.receipt(candidate);CollectionValidator.Index withReceipt=CollectionValidator.scan(candidate,targets);receipt(withReceipt.root,true);CollectionValidator.complete(withReceipt,targets);CollectionValidator.newTypes(before,withReceipt,targets);CollectionValidator.preserved(before,withReceipt,approvedLiberate);identity(withReceipt.root,account,uid);
        storage.stopped();need(Arrays.equals(original,storage.read()),"PROFILE_CHANGED_DURING_CANDIDATE");faults.check("BEFORE_COMMIT");storage.stopped();
        if(!Arrays.equals(original,candidate))storage.write(candidate);faults.check("AFTER_COMMIT");
        storage.stopped();byte[] disk=storage.read();need(Arrays.equals(candidate,disk),"PROFILE_COMMIT_READBACK_MISMATCH");CollectionValidator.Index verified=CollectionValidator.scan(disk,targets);CollectionValidator.complete(verified,targets);receipt(verified.root,true);identity(verified.root,account,uid);faults.check("AFTER_READBACK");
    }
    private static byte[] normalized(byte[] candidate,Engine engine,CollectionTargets targets)throws Exception{byte[] result=engine.normalize(candidate);CollectionLiberateRules.verify(candidate,result,engine.liberateGroups(),targets);return result;}
    static void identity(Value root,String account,int uid)throws IOException{need(uid>0&&integer(root,"uid")==uid&&required(root,"account").string().equals(account)&&required(root,"an").string().equals(account),"BOUND_IDENTITY_MISMATCH");}
    static void receipt(Value root,boolean required)throws IOException{
        Value value=root.get(RECEIPT);if(value==null){need(!required,"MISSING_RECEIPT");return;}
        need(value.type==3&&value.fields.keySet().equals(new HashSet<String>(Arrays.asList("schema","policy","targets","catalog","contract"))),"RECEIPT_KEY_COLLISION");
        need(integer(value,"schema")==1&&required(value,"policy").string().equals(POLICY)&&required(value,"targets").string().equals(CollectionTargets.TARGET_SHA)&&required(value,"catalog").string().equals(CollectionTargets.CATALOG_SHA)&&required(value,"contract").string().equals(CollectionTargets.CONTRACT_SHA),"RECEIPT_POLICY_COLLISION");
    }
    static byte[] read(InputStream stream,int limit)throws IOException{try(InputStream in=stream;ByteArrayOutputStream out=new ByteArrayOutputStream()){byte[] b=new byte[65536];int n;while((n=in.read(b))!=-1){need(out.size()+n<=limit,"ASSET_SIZE_LIMIT");out.write(b,0,n);}return out.toByteArray();}}
    static String sha(byte[] bytes)throws Exception{StringBuilder s=new StringBuilder();for(byte b:MessageDigest.getInstance("SHA-256").digest(bytes))s.append(String.format(Locale.ROOT,"%02x",b&255));return s.toString();}
}
