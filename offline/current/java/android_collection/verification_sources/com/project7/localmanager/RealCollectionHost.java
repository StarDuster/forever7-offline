package com.project7.localmanager;
import android.content.Context;
import android.content.res.AssetManager;
import android.system.Os;
import java.io.*;
import java.lang.reflect.*;
import java.nio.file.*;
import java.util.*;

/** REAL translated original P7 engines; baseline is entirely synthetic, platform seams explicit. */
public final class RealCollectionHost {
    static void check(boolean v,String m){if(!v)throw new AssertionError(m);}
    static byte[] synthetic()throws Exception{byte[] p=BsonLite.document("uid",7,"account","synthetic-original-engine","an","synthetic-original-engine","unknownScalar",123456789,"unknownNested",BsonLite.document("keep","unchanged","version",42),"heromgr",BsonLite.document("hrs",new ArrayList<>()),"inv",BsonLite.document("items",new ArrayList<>(),"mc",500));Method raw=BsonLite.class.getDeclaredMethod("replaceElement",byte[].class,String.class,int.class,byte[].class);raw.setAccessible(true);return (byte[])raw.invoke(null,p,"unknownScalar",18,java.nio.ByteBuffer.allocate(8).order(java.nio.ByteOrder.LITTLE_ENDIAN).putLong(1234567890123L).array());}
    static final class Counts implements FullCollectionInitializer.Engine {
        final CollectionStockBridge original;int heroes,helpers,skins,normalizes,treasures;long inputBytes,outputBytes;
        Counts(CollectionStockBridge original){this.original=original;}
        public List<List<Integer>>liberateGroups(){return original.liberateGroups();}
        public byte[]normalize(byte[]p)throws Exception{normalizes++;return original.normalize(p);}
        public byte[]heroes(byte[]p)throws Exception{heroes++;return original.heroes(p);}
        public byte[]helper(byte[]p,int id)throws Exception{helpers++;return original.helper(p,id);}
        public byte[]skins(byte[]p)throws Exception{skins++;return original.skins(p);}
        public byte[]treasure(byte[]p,int id,int q)throws Exception{treasures++;inputBytes+=p.length;byte[]r=original.treasure(p,id,q);outputBytes+=r.length;return r;}
        public byte[]receipt(byte[]p)throws Exception{return original.receipt(p);}
    }
    static final class Disk implements FullCollectionInitializer.Storage {
        final File file;final Method reader,writer;int writes;boolean stopped=true;
        Disk(File file)throws Exception{this.file=file;reader=LocalProfileStore.class.getDeclaredMethod("readAll",File.class);writer=LocalProfileStore.class.getDeclaredMethod("writeAtomic",File.class,byte[].class);reader.setAccessible(true);writer.setAccessible(true);}
        public byte[]read()throws Exception{return (byte[])CollectionStockBridge.invoke(reader,null,file);}
        public void write(byte[]candidate)throws Exception{File tmp=new File(file+".tmp");if(Files.exists(tmp.toPath(),LinkOption.NOFOLLOW_LINKS)){check(!Files.isSymbolicLink(tmp.toPath()),"No temp symlink");Files.delete(tmp.toPath());}CollectionStockBridge.invoke(writer,null,file,candidate);writes++;}
        public void stopped()throws Exception{CollectionBson.need(stopped,"HOST_WRITER_GATE");}
    }
    interface Work{void run()throws Exception;}
    static int rejected;
    static void reject(Work work)throws Exception{try{work.run();throw new AssertionError("Unexpected acceptance");}catch(IOException expected){rejected++;}}
    static void remove(Path p)throws Exception{if(Files.isDirectory(p,LinkOption.NOFOLLOW_LINKS)){try(DirectoryStream<Path>s=Files.newDirectoryStream(p)){for(Path c:s)remove(c);}}Files.deleteIfExists(p);}
    public static void main(String[]args)throws Exception{
        Path root=Files.createTempDirectory("p7-real-engine-synthetic-").toRealPath();
        try {
            for(Class<?> original:Arrays.asList(BsonLite.class,LocalResourceEngine.class,LocalLevelAdmin.class,LocalCollectionEngine.class,LocalSharedLiberateEngine.class,LocalResourceCatalog.class,LocalFeatureCatalog.class,LocalProfileStore.class))check(original.getProtectionDomain().getCodeSource().getLocation().toString().endsWith("manager-translated-frames.jar"),"Original class source must be verified translated jar");
            AssetManager assets=new AssetManager(new File(args[0]),new File(args[1]),new File(args[2]));Context context=new Context(root.toFile(),assets);
            byte[] targetBytes=Files.readAllBytes(Paths.get(args[2]));CollectionTargets targets=CollectionTargets.load(targetBytes);
            byte[] catalog=Files.readAllBytes(Paths.get(args[1]));check(FullCollectionInitializer.sha(catalog).equals(CollectionTargets.CATALOG_SHA),"Pinned extended catalog");
            LocalProfileStore store=new LocalProfileStore(context);Files.createDirectories(root.resolve("profiles"));File file=root.resolve("profiles/synthetic-original-engine.bson").toFile();
            CollectionStockBridge stock=new CollectionStockBridge(catalog,targets,store);Counts count=new Counts(stock);Disk disk=new Disk(file);byte[] baseline=synthetic();Files.write(file.toPath(),baseline);
            long start=System.nanoTime();FullCollectionInitializer.transact(disk,count,targets,"synthetic-original-engine",7,FullCollectionInitializer.NO_FAULTS);long millis=(System.nanoTime()-start)/1000000L;
            byte[] complete=disk.read();check(disk.writes==1&&count.treasures==1900,"Original1900 grants and one original private writeAtomic");CollectionValidator.Index index=CollectionValidator.scan(complete,targets);CollectionValidator.complete(index,targets);check(index.heroes.size()==140&&index.skins.size()==494&&index.treasures.size()==1900,"Exact real engine targets");
            check(BsonLite.intValue(BsonLite.document("x",7),"x")==7,"Real BsonLite read/write");check(CollectionBson.equal(CollectionBson.parse(baseline).get("unknownScalar"),CollectionBson.parse(complete).get("unknownScalar")),"Original unknown BSON int64 retained");
            Counts repeat=new Counts(stock);FullCollectionInitializer.transact(disk,repeat,targets,"synthetic-original-engine",7,FullCollectionInitializer.NO_FAULTS);check(disk.writes==1&&repeat.treasures==0&&Arrays.equals(complete,disk.read()),"Real engine repeat byte-idempotent no write");
            // A real original grant after a missing exact pair, even under matching receipt.
            // Receipt is authoritative: a missing target pair is consumed, not repaired.
            byte[] inv=BsonLite.documentValue(complete,"inv");List<byte[]> old=LocalResourceEngine.array(BsonLite.documentValue(inv,"items"));old.remove(0);byte[] missing=BsonLite.withProfileDocument(complete,"inv",BsonLite.withProfileArray(inv,"items",old));Files.write(file.toPath(),missing);Counts repair=new Counts(stock);FullCollectionInitializer.transact(disk,repair,targets,"synthetic-original-engine",7,FullCollectionInitializer.NO_FAULTS);check(repair.treasures==0&&disk.writes==1&&Arrays.equals(missing,disk.read()),"Matching real receipt preserves consumed pair without grant");
            // Partial actual-grant candidate never written.
            Files.write(file.toPath(),baseline);int writes=disk.writes;Counts partial=new Counts(stock);reject(()->FullCollectionInitializer.transact(disk,partial,targets,"synthetic-original-engine",7,p->{if(p.equals("AFTER_TREASURE_1"))throw new IOException("host partial candidate fault");}));check(Arrays.equals(baseline,disk.read())&&disk.writes==writes,"Actual partial grants preserve old full bytes");
            // Original private writer file fsync, host-only Os.rename seam and restart recovery.
            byte[] noReceipt=BsonLite.withoutProfileKey(complete,FullCollectionInitializer.RECEIPT);Files.write(file.toPath(),noReceipt);Os.failNextRename=true;reject(()->FullCollectionInitializer.transact(disk,new Counts(stock),targets,"synthetic-original-engine",7,FullCollectionInitializer.NO_FAULTS));check(Arrays.equals(noReceipt,disk.read()),"Original writer fault before host rename retains source");check(Files.exists(Paths.get(file+".tmp")),"Original writer left only owned temporary");
            FullCollectionInitializer.transact(disk,new Counts(stock),targets,"synthetic-original-engine",7,FullCollectionInitializer.NO_FAULTS);int committed=disk.writes;check(!Files.exists(Paths.get(file+".tmp")),"Retry handles owned temporary");
            Files.write(file.toPath(),BsonLite.withoutProfileKey(disk.read(),FullCollectionInitializer.RECEIPT));
            reject(()->FullCollectionInitializer.transact(disk,new Counts(stock),targets,"synthetic-original-engine",7,p->{if(p.equals("AFTER_COMMIT"))throw new IOException("host postcommit interruption");}));FullCollectionInitializer.transact(disk,new Counts(stock),targets,"synthetic-original-engine",7,FullCollectionInitializer.NO_FAULTS);check(disk.writes==committed+1,"Interrupted completed receipt does not regrant/rewrite");
            System.out.println("REAL_TRANSLATED_ENGINE_PASS heroes="+index.heroes.size()+" skins="+index.skins.size()+" treasurePairs="+index.treasures.size()+" firstOriginalGrants="+count.treasures+" firstPrivateWrites=1 initialBytes="+baseline.length+" finalBytes="+complete.length+" cumulativeInputBytes="+count.inputBytes+" cumulativeOutputBytes="+count.outputBytes+" firstMillis="+millis+" faultCases="+rejected+" repeatOriginalGrants="+repeat.treasures+" repairOriginalGrants="+repair.treasures);
            System.out.println("PLATFORM_SEAMS Context,AssetManager,Os.rename only; Stub! Android methods not used. -Xverify:all; no ART/device/game/native acceptance.");System.out.println("PUBLIC_ASSETS_OPENED "+assets.opened);
        } finally {remove(root);}
    }
}
