package com.forever7.offline;

import java.io.*;
import java.nio.charset.StandardCharsets;
import java.nio.file.*;
import java.security.*;
import java.util.*;
import java.util.concurrent.atomic.AtomicBoolean;

/** Host tests for the private-ledger fast-start candidate. No Android classes are used: the
 * metadata probe is injected exactly as the production platform gets the reflection probe. */
public final class Project7ResourceFastStartHostTest {
    static void check(boolean v,String m){if(!v)throw new RuntimeException(m);}
    static String hash(byte[] b)throws Exception {
        StringBuilder s=new StringBuilder();for(byte x:MessageDigest.getInstance("SHA-256").digest(b))s.append(String.format("%02x",x&255));return s.toString();
    }
    interface Work{void run()throws Exception;}
    static int failures, cases;
    static void refuse(Work w)throws Exception {
        cases++;
        try{w.run();throw new RuntimeException("Unexpected success");}catch(IOException expected){failures++;}
    }
    static void accept(Work w)throws Exception { cases++; w.run(); }
    static Project7ResourceSnapshot.Asset asset(String n,byte[] b)throws Exception{return new Project7ResourceSnapshot.Asset(n,b.length,hash(b));}
    static void remove(Path p)throws IOException {if(Files.isDirectory(p,LinkOption.NOFOLLOW_LINKS)){try(DirectoryStream<Path>s=Files.newDirectoryStream(p)){for(Path c:s)remove(c);}}Files.deleteIfExists(p);}

    /** Deterministic host metadata: values depend only on entry index, never on wall clock. */
    static final class Probe implements Project7ResourceSnapshot.MetadataProbe {
        final Map<String,long[]> values=new HashMap<String,long[]>();
        boolean available=true,reliable=true,unstable;
        long tick;
        public Project7ResourceSnapshot.Metadata probe(File file) throws IOException {
            if(!available)return null;
            long[] v=values.get(file.getCanonicalPath());
            if(v==null)return null;
            long ctime=v[3];
            if(unstable) ctime=ctime+(++tick);
            return new Project7ResourceSnapshot.Metadata(v[0],v[1],v[2],ctime,v[4]);
        }
        public boolean reliable(){return reliable;}
        void register(File file,long ino,long ctime,long mtime)throws IOException {
            values.put(file.getCanonicalPath(),new long[]{1,ino,file.length(),ctime,mtime});
        }
        void ino(File file,long ino)throws IOException {values.get(file.getCanonicalPath())[1]=ino;}
        void ctime(File file,long ctime)throws IOException {values.get(file.getCanonicalPath())[3]=ctime;}
    }

    static final class Fixture {
        final Path docs,res,internal;
        final List<ResourceImporter.Entry> entries=new ArrayList<ResourceImporter.Entry>();
        final Map<String,byte[]> bundles=new HashMap<String,byte[]>();
        final AtomicBoolean cancel=new AtomicBoolean();
        final Probe probe=new Probe();
        final Project7ResourceSnapshot.TrustedContract contract;
        final Project7ResourceSnapshot.Assets assets;
        final File ledger;
        final File[] resources=new File[312];
        long shaReads;
        final ResourceImporter.Progress progress;

        Fixture()throws Exception {
            docs=Files.createTempDirectory("f7-faststart-docs-").toRealPath();
            internal=Files.createTempDirectory("f7-faststart-internal-").toRealPath();
            res=Files.createDirectory(docs.resolve("res"));
            byte[] resource="tiny-resource".getBytes("UTF-8");
            for(int i=0;i<312;i++) {
                String n="toy"+i+".npk";
                entries.add(new ResourceImporter.Entry(n,resource.length,hash(resource)));
                Path file=res.resolve(n);Files.write(file,resource);resources[i]=file.toFile();
            }
            byte[] template="{\"schema\":1,\"version\":455,\"platform\":\"android\",\"parts\":[[\"toy\",[[0,[[1,\"md5\",2,3,4,5,6]]]]]],\"packs\":[[0,[[\"toy\",\"md5\",10]]]],\"manifest\":{\"toy\":[1,[\"md5\",10]]}}".getBytes("US-ASCII");
            byte[] binding="trusted-contract-fixture".getBytes("US-ASCII"),base="base-script".getBytes("US-ASCII"),overlay="overlay-script".getBytes("US-ASCII");
            bundles.put("template",template);bundles.put("binding",binding);
            bundles.put("assets/script.npk",base);bundles.put("assets/project7_local.npk",overlay);
            contract=new Project7ResourceSnapshot.TrustedContract(455,640,"android",
                Project7ResourceSnapshot.SOURCE_MANIFEST_SHA256,Project7ResourceSnapshot.RESOURCE_MANIFEST_SHA256,
                Project7ResourceSnapshot.entryFingerprint(entries),312,
                asset("template",template),asset("binding",binding),
                Arrays.asList(asset("assets/script.npk",base),asset("assets/project7_local.npk",overlay)));
            assets=n->{byte[] b=bundles.get(n);if(b==null)throw new IOException("Missing bundled asset");return new ByteArrayInputStream(b);};
            progress=(n,b,t)->{if(b==t)shaReads++;};
            ledger=Project7ResourceSnapshot.privateLedger(internal.toFile());
            for(int i=0;i<312;i++)probe.register(resources[i],1000+i,1000000000L+i,2000000000L+i);
        }
        void reset(){shaReads=0;}
        Project7ResourceSnapshot.Receipt publish()throws IOException {
            return Project7ResourceSnapshot.publish(docs.toFile(),entries,contract,assets,cancel,progress,ledger,probe);
        }
        Project7ResourceSnapshot.Receipt forced()throws IOException {
            return Project7ResourceSnapshot.publish(docs.toFile(),entries,contract,assets,cancel,progress);
        }
        Project7ResourceSnapshot.Receipt withLedger(Path path)throws IOException {
            return Project7ResourceSnapshot.publish(docs.toFile(),entries,contract,assets,cancel,progress,path.toFile(),probe);
        }
        Project7ResourceSnapshot.Receipt publish(Project7ResourceSnapshot.Assets source,
                Project7ResourceSnapshot.LedgerCommitObserver observer)throws IOException {
            return Project7ResourceSnapshot.publish(docs.toFile(),entries,contract,source,cancel,progress,ledger,probe,observer);
        }
        Project7ResourceSnapshot.Assets assetsWithMutation(String assetName,Work mutation) {
            final boolean[] done={false};
            return n-> {
                if(!done[0] && n.equals(assetName)) {
                    done[0]=true;
                    try{mutation.run();}catch(Exception error){throw new IOException("fixture mutation failed",error);}
                }
                return assets.open(n);
            };
        }
        void overwrite(int index,String text,long ctime)throws Exception {
            Files.write(resources[index].toPath(),text.getBytes("UTF-8"));
            probe.ctime(resources[index],ctime);
        }
        Path marker(){return docs.resolve(Project7ResourceSnapshot.COMMIT);}
        void close()throws IOException {remove(docs);remove(internal);}
    }

    static void replaceLine(Path ledger,String prefix,String replacement)throws Exception {
        List<String> lines=Files.readAllLines(ledger,StandardCharsets.US_ASCII);boolean found=false;
        for(int i=0;i<lines.size();i++)if(lines.get(i).startsWith(prefix)){lines.set(i,replacement);found=true;break;}
        check(found,"ledger line "+prefix);Files.write(ledger,lines,StandardCharsets.US_ASCII);
    }
    static byte[] tampered(Fixture f,String prefix,String replacement)throws Exception {
        replaceLine(f.ledger.toPath(),prefix,replacement);return Files.readAllBytes(f.ledger.toPath());
    }

    public static void main(String[] args)throws Exception {
        firstPassWritesLedgerOnlyAfterSuccess();
        unchangedFastPathMakesZeroResourceReads();
        ctimeChangeSameSizeSameMtimeForcesFullAndRejects();
        inodeReplacementForcesFullAndSucceeds();
        staleMalformedAndMissingLedgersForceFull();
        pinRootVersionAndManifestChangesForceFull();
        forcedOldApiStillFull();
        externalLedgerNeverTrustedOrWritten();
        failureAndCancellationRetainOldLedgerAndMarker();
        metadataProbeUnavailableForcesFull();
        changedSnapshotOrScriptStillFailsFullValidation();
        fullPassMetadataChangeDuringPublicationFailsClosed();
        fastLedgerMetadataChangeDuringPublicationFailsClosed();
        fastLedgerProbeUnavailableFailsClosed();
        fastFallbackMetadataInstabilityFailsClosed();
        ledgerCommitCancellationNoReceipt();
        ledgerCommitFailureRetainsOldMarker();
        privateLedgerPolicy();
        System.out.println("Project7ResourceFastStartHostTest OK: "+cases+" scenarios, "+failures+" expected failure cases");
    }

    static void firstPassWritesLedgerOnlyAfterSuccess()throws Exception {
        Fixture f=new Fixture();
        try {
            byte[] good=f.bundles.get("binding");
            f.bundles.put("binding","x".getBytes("US-ASCII"));
            refuse(()->f.publish());
            check(!Files.exists(f.ledger.toPath()),"no ledger before a complete successful pass");
            check(!Files.exists(f.marker()),"no commit marker on failure");
            f.bundles.put("binding",good);f.reset();
            accept(()->check(f.publish().verifiedEntries==312,"receipt"));
            check(Files.exists(f.ledger.toPath()),"ledger after full success");
            check(f.shaReads==312,"first pass hashes all 312 resources");
            // Cancellation while the bundled snapshot is being streamed must not write a ledger.
            Project7ResourceSnapshot.Assets cancelStream=n-> {
                if(!n.equals("template"))return f.assets.open(n);
                return new ByteArrayInputStream(f.bundles.get("template")) {
                    public synchronized int read(byte[] b,int o,int l) {
                        int n=super.read(b,o,l);f.cancel.set(true);return n;
                    }
                };
            };
            f.cancel.set(false);
            f.reset();
            refuse(()->Project7ResourceSnapshot.publish(f.docs.toFile(),f.entries,f.contract,cancelStream,f.cancel,f.progress,f.ledger,f.probe));
            f.cancel.set(false);
            check(f.shaReads==0,"fast ledger must not make cancellation write anything");
        } finally {f.close();}
    }

    static void unchangedFastPathMakesZeroResourceReads()throws Exception {
        Fixture f=new Fixture();
        try {
            accept(f::publish);check(f.shaReads==312,"initial full pass");
            byte[] ledger=Files.readAllBytes(f.ledger.toPath()),marker=Files.readAllBytes(f.marker());
            f.reset();accept(()->check(f.publish().verifiedEntries==312,"fast receipt"));
            check(f.shaReads==0,"unchanged fast path performs zero resource SHA reads");
            check(Arrays.equals(ledger,Files.readAllBytes(f.ledger.toPath())),"fast path does not rewrite ledger");
            check(Arrays.equals(marker,Files.readAllBytes(f.marker())),"fast path republishes marker bytes");
        } finally {f.close();}
    }

    static void ctimeChangeSameSizeSameMtimeForcesFullAndRejects()throws Exception {
        Fixture f=new Fixture();
        try {
            accept(f::publish);
            byte[] ledger=Files.readAllBytes(f.ledger.toPath()),marker=Files.readAllBytes(f.marker());
            byte[] changed="tiny-resourcX".getBytes("UTF-8"); // same 13-byte length
            Files.write(f.resources[5].toPath(),changed);
            f.probe.ctime(f.resources[5],1000000000L+5+77);
            f.reset();refuse(()->f.publish());
            check(f.shaReads>0,"ctime change must enter the full SHA-256 path");
            check(Arrays.equals(ledger,Files.readAllBytes(f.ledger.toPath())),"old ledger retained after hash failure");
            check(Arrays.equals(marker,Files.readAllBytes(f.marker())),"old marker retained after hash failure");
        } finally {f.close();}
    }

    static void inodeReplacementForcesFullAndSucceeds()throws Exception {
        Fixture f=new Fixture();
        try {
            accept(f::publish);
            f.probe.ino(f.resources[6],999999);
            f.reset();accept(()->check(f.publish().verifiedEntries==312,"receipt"));
            check(f.shaReads==312,"inode replacement forces a full hash pass");
            f.reset();accept(f::publish);check(f.shaReads==0,"refreshed ledger enables fast path again");
        } finally {f.close();}
    }

    static void staleMalformedAndMissingLedgersForceFull()throws Exception {
        Fixture f=new Fixture();
        try {
            accept(f::publish);
            Files.delete(f.ledger.toPath());f.reset();accept(f::publish);check(f.shaReads==312,"missing ledger -> full");
            Files.write(f.ledger.toPath(),(Project7ResourceSnapshot.LEDGER+"\nformat=0\n").getBytes("US-ASCII"));
            f.reset();accept(f::publish);check(f.shaReads==312,"old format ledger -> full");
            Files.write(f.ledger.toPath(),"garbage".getBytes("US-ASCII"));
            f.reset();accept(f::publish);check(f.shaReads==312,"malformed ledger -> full");
            // A missing ledger entry line must not be partially trusted.
            replaceLine(f.ledger.toPath(),"entry=","");
            f.reset();accept(f::publish);check(f.shaReads==312,"truncated ledger -> full");
        } finally {f.close();}
    }

    static void pinRootVersionAndManifestChangesForceFull()throws Exception {
        Fixture f=new Fixture();
        try {
            accept(f::publish);
            tampered(f,"entryManifest=","entryManifest="+repeat('0',64));
            f.reset();accept(f::publish);check(f.shaReads==312,"entry manifest pin change -> full");
            tampered(f,"clientVersion=","clientVersion=456");
            f.reset();accept(f::publish);check(f.shaReads==312,"client version change -> full");
            tampered(f,"resourceVersion=","resourceVersion=641");
            f.reset();accept(f::publish);check(f.shaReads==312,"resource version change -> full");
            String original=Files.readAllLines(f.ledger.toPath(),StandardCharsets.US_ASCII).get(0);
            replaceLine(f.ledger.toPath(),"snapshot=","snapshot=1 "+repeat('a',64));
            f.reset();accept(f::publish);check(f.shaReads==312,"snapshot pin change -> full");
            replaceLine(f.ledger.toPath(),"script=","script=assets/script.npk 1 "+repeat('b',64));
            f.reset();accept(f::publish);check(f.shaReads==312,"script pin change -> full");
            check(original.length()>0,"ledger header present");
            // Different canonical resource root with an otherwise identical ledger.
            Fixture other=new Fixture();
            try {
                Files.copy(f.ledger.toPath(),other.ledger.toPath(),StandardCopyOption.REPLACE_EXISTING);
                other.reset();accept(other::publish);
                check(other.shaReads==312,"changed resource root -> full");
            } finally {other.close();}
            // A different manifest list is rejected before any ledger consideration.
            List<ResourceImporter.Entry> wrong=new ArrayList<ResourceImporter.Entry>(f.entries);
            wrong.set(0,new ResourceImporter.Entry("replacement.npk",f.entries.get(0).bytes,f.entries.get(0).sha256));
            refuse(()->Project7ResourceSnapshot.publish(f.docs.toFile(),wrong,f.contract,f.assets,f.cancel,f.progress,f.ledger,f.probe));
        } finally {f.close();}
    }

    static void forcedOldApiStillFull()throws Exception {
        Fixture f=new Fixture();
        try {
            accept(f::publish);
            f.reset();accept(()->check(f.forced().verifiedEntries==312,"forced receipt"));
            check(f.shaReads==312,"legacy six-argument publish remains full-force");
        } finally {f.close();}
    }

    static void externalLedgerNeverTrustedOrWritten()throws Exception {
        Fixture f=new Fixture();
        try {
            accept(f::publish);
            byte[] internalLedger=Files.readAllBytes(f.ledger.toPath()),marker=Files.readAllBytes(f.marker());
            Path external=f.docs.resolve("external-ledger");
            Files.copy(f.ledger.toPath(),external);
            byte[] externalBytes=Files.readAllBytes(external);
            f.reset();accept(()->check(f.withLedger(external).verifiedEntries==312,"external receipt"));
            check(f.shaReads==312,"ledger beside Documents/import data is never trusted");
            check(Arrays.equals(externalBytes,Files.readAllBytes(external)),"external ledger is never rewritten");
            check(Arrays.equals(internalLedger,Files.readAllBytes(f.ledger.toPath())),"external call does not touch the private ledger");
            check(Arrays.equals(marker,Files.readAllBytes(f.marker())),"marker still republished");
            Path storage=Paths.get("/storage/emulated/0/project7-ledger-test");
            f.reset();accept(()->check(f.withLedger(storage).verifiedEntries==312,"storage receipt"));
            check(f.shaReads==312,"a ledger shaped like external storage is never trusted");
            check(!Files.exists(storage),"external storage ledger is never created");
            try{Project7ResourceSnapshot.privateLedger(Paths.get("/storage/emulated/0").toFile());throw new RuntimeException("external files dir accepted");}
            catch(IOException expected){cases++;}
        } finally {f.close();}
    }

    static void failureAndCancellationRetainOldLedgerAndMarker()throws Exception {
        Fixture f=new Fixture();
        try {
            accept(f::publish);
            byte[] ledger=Files.readAllBytes(f.ledger.toPath()),marker=Files.readAllBytes(f.marker());
            Files.delete(f.resources[7].toPath());
            f.reset();refuse(()->f.publish());
            check(Arrays.equals(ledger,Files.readAllBytes(f.ledger.toPath())),"missing resource keeps old ledger");
            check(Arrays.equals(marker,Files.readAllBytes(f.marker())),"missing resource keeps old marker");
            Files.write(f.resources[7].toPath(),"tiny-resource".getBytes("UTF-8"));
            Project7ResourceSnapshot.Assets cancelStream=n-> {
                if(!n.equals("template"))return f.assets.open(n);
                return new ByteArrayInputStream(f.bundles.get("template")) {
                    public synchronized int read(byte[] b,int o,int l) {
                        int n=super.read(b,o,l);f.cancel.set(true);return n;
                    }
                };
            };
            f.cancel.set(false);f.reset();
            refuse(()->Project7ResourceSnapshot.publish(f.docs.toFile(),f.entries,f.contract,cancelStream,f.cancel,f.progress,f.ledger,f.probe));
            f.cancel.set(false);
            check(f.shaReads==0,"valid fast ledger followed by cancellation still does not hash resources");
            check(Arrays.equals(ledger,Files.readAllBytes(f.ledger.toPath())),"cancellation keeps old ledger");
            check(Arrays.equals(marker,Files.readAllBytes(f.marker())),"cancellation keeps old marker");
        } finally {f.close();}
    }

    static void metadataProbeUnavailableForcesFull()throws Exception {
        Fixture f=new Fixture();
        try {
            accept(f::publish);
            byte[] ledger=Files.readAllBytes(f.ledger.toPath());
            f.probe.available=false;
            f.reset();accept(f::publish);
            check(f.shaReads==312,"unavailable metadata probe -> full hash");
            check(Arrays.equals(ledger,Files.readAllBytes(f.ledger.toPath())),"no ledger is committed without metadata");
            f.probe.available=true;
            f.probe.reliable=false;
            f.reset();accept(f::publish);
            check(f.shaReads==312,"unreliable metadata precision -> full hash");
            check(Arrays.equals(ledger,Files.readAllBytes(f.ledger.toPath())),"unreliable probe does not rewrite ledger");
            f.probe.reliable=true;
            f.reset();accept(f::publish);check(f.shaReads==0,"old ledger still valid once probe returns");
            check(Project7ResourceSnapshot.androidMetadataProbe()==null,"host must have no Android reflection classes");
            f.reset();
            accept(()->Project7ResourceSnapshot.publish(f.docs.toFile(),f.entries,f.contract,f.assets,f.cancel,f.progress,f.ledger,null));
            check(f.shaReads==312,"reflection-unavailable default probe -> full hash");
        } finally {f.close();}
    }

    static void changedSnapshotOrScriptStillFailsFullValidation()throws Exception {
        Fixture f=new Fixture();
        try {
            accept(f::publish);
            byte[] ledger=Files.readAllBytes(f.ledger.toPath()),marker=Files.readAllBytes(f.marker());
            byte[] template=f.bundles.get("template");
            f.bundles.put("template",Arrays.copyOf(template,template.length));
            f.bundles.get("template")[3]^=1;
            f.reset();refuse(()->f.publish());
            check(Arrays.equals(ledger,Files.readAllBytes(f.ledger.toPath())),"snapshot change keeps old ledger");
            check(Arrays.equals(marker,Files.readAllBytes(f.marker())),"snapshot change keeps old marker");
            f.bundles.put("template",template);
            byte[] overlay=f.bundles.get("assets/project7_local.npk");
            f.bundles.put("assets/project7_local.npk",new byte[]{1});
            f.reset();refuse(()->f.publish());
            check(Arrays.equals(ledger,Files.readAllBytes(f.ledger.toPath())),"script change keeps old ledger");
            f.bundles.put("assets/project7_local.npk",overlay);
        } finally {f.close();}
    }

    static void fullPassMetadataChangeDuringPublicationFailsClosed()throws Exception {
        Fixture f=new Fixture();
        try {
            // The mutation happens after the full SHA pass, while bundled assets stream.
            Project7ResourceSnapshot.Assets source=f.assetsWithMutation("template",
                ()->f.overwrite(5,"tiny-resourcE",1000000000L+5+500));
            f.reset();refuse(()->f.publish(source,null));
            check(f.shaReads==312,"full pass already hashed all 312 resources");
            check(!Files.exists(f.ledger.toPath()),"no ledger after publication-time metadata change");
            check(!Files.exists(f.marker()),"no marker after publication-time metadata change");
            check(!Files.exists(f.docs.resolve(Project7ResourceSnapshot.SNAPSHOT)),"no snapshot published");
        } finally {f.close();}
    }

    static void fastLedgerMetadataChangeDuringPublicationFailsClosed()throws Exception {
        Fixture f=new Fixture();
        try {
            accept(f::publish);
            byte[] ledger=Files.readAllBytes(f.ledger.toPath()),marker=Files.readAllBytes(f.marker());
            // Same-size overwrite with synthetic mtime unchanged and ctime advanced, after the
            // fast ledger check but before the final probe.
            Project7ResourceSnapshot.Assets source=f.assetsWithMutation("template",
                ()->f.overwrite(5,"tiny-resourcE",1000000000L+5+700));
            f.reset();refuse(()->f.publish(source,null));
            check(f.shaReads>0,"observed change forces the full SHA fallback");
            check(Arrays.equals(ledger,Files.readAllBytes(f.ledger.toPath())),"old ledger retained when fallback hash fails");
            check(Arrays.equals(marker,Files.readAllBytes(f.marker())),"old marker retained when fallback hash fails");
        } finally {f.close();}
    }

    static void fastLedgerProbeUnavailableFailsClosed()throws Exception {
        Fixture f=new Fixture();
        try {
            accept(f::publish);
            byte[] ledger=Files.readAllBytes(f.ledger.toPath()),marker=Files.readAllBytes(f.marker());
            Project7ResourceSnapshot.Assets source=f.assetsWithMutation("template",
                ()->f.probe.available=false);
            f.reset();refuse(()->f.publish(source,null));
            check(f.shaReads==0,"probe loss must not publish merely because no ledger exists");
            check(Arrays.equals(ledger,Files.readAllBytes(f.ledger.toPath())),"probe loss keeps old ledger");
            check(Arrays.equals(marker,Files.readAllBytes(f.marker())),"probe loss keeps old marker");
        } finally {f.close();}
    }

    static void fastFallbackMetadataInstabilityFailsClosed()throws Exception {
        Fixture f=new Fixture();
        try {
            accept(f::publish);
            byte[] ledger=Files.readAllBytes(f.ledger.toPath()),marker=Files.readAllBytes(f.marker());
            Project7ResourceSnapshot.Assets source=f.assetsWithMutation("template",
                ()->f.probe.unstable=true);
            f.reset();refuse(()->f.publish(source,null));
            check(f.shaReads==312,"fallback rehashed all resources before rejecting instability");
            check(Arrays.equals(ledger,Files.readAllBytes(f.ledger.toPath())),"unstable fallback keeps old ledger");
            check(Arrays.equals(marker,Files.readAllBytes(f.marker())),"unstable fallback keeps old marker");
        } finally {f.close();}
    }

    static void ledgerCommitCancellationNoReceipt()throws Exception {
        Fixture f=new Fixture();
        try {
            accept(f::publish);
            byte[] marker=Files.readAllBytes(f.marker());
            // Force a full path that will commit a ledger, retaining the old (malformed) ledger.
            Files.write(f.ledger.toPath(),(Project7ResourceSnapshot.LEDGER+"\nformat=0\n").getBytes("US-ASCII"));
            byte[] stale=Files.readAllBytes(f.ledger.toPath());
            f.reset();f.cancel.set(false);
            refuse(()->f.publish(f.assets,()->f.cancel.set(true)));
            f.cancel.set(false);
            check(f.shaReads==312,"commit cancellation follows a full pass");
            check(Arrays.equals(stale,Files.readAllBytes(f.ledger.toPath())),"cancellation before ledger rename keeps old ledger");
            check(Arrays.equals(marker,Files.readAllBytes(f.marker())),"cancellation during ledger commit keeps old marker");
        } finally {f.close();}
    }

    static void ledgerCommitFailureRetainsOldMarker()throws Exception {
        Fixture f=new Fixture();
        try {
            accept(f::publish);
            byte[] marker=Files.readAllBytes(f.marker());
            Files.write(f.ledger.toPath(),(Project7ResourceSnapshot.LEDGER+"\nformat=0\n").getBytes("US-ASCII"));
            byte[] stale=Files.readAllBytes(f.ledger.toPath());
            f.reset();
            refuse(()->f.publish(f.assets,()->{throw new IOException("forced ledger rename failure");}));
            check(f.shaReads==312,"ledger failure follows a full pass");
            check(Arrays.equals(stale,Files.readAllBytes(f.ledger.toPath())),"ledger failure keeps old ledger");
            check(Arrays.equals(marker,Files.readAllBytes(f.marker())),"ledger failure keeps old marker");
            // Real destination failure: a directory at the ledger path fails before rename.
            Files.delete(f.ledger.toPath());Files.createDirectory(f.ledger.toPath());
            f.reset();refuse(()->f.publish(f.assets,null));
            check(f.shaReads==312,"ledger destination failure follows a full pass");
            check(Arrays.equals(marker,Files.readAllBytes(f.marker())),"ledger destination failure keeps old marker");
            check(Files.isDirectory(f.ledger.toPath()),"ledger destination remains untouched");
        } finally {f.close();}
    }

    static void privateLedgerPolicy()throws Exception {
        Fixture f=new Fixture();
        try {
            File expected=new File(f.internal.toFile().getCanonicalFile(),Project7ResourceSnapshot.LEDGER);
            check(Project7ResourceSnapshot.privateLedger(f.internal.toFile()).equals(expected),"private ledger is inside getFilesDir");
            try{Project7ResourceSnapshot.privateLedger(null);throw new RuntimeException("null files dir accepted");}
            catch(IllegalArgumentException expectedError){cases++;}
            check(Project7ResourceSnapshot.LEDGER.indexOf('/')<0 && !Project7ResourceSnapshot.LEDGER.contains(".."),"plain ledger name");
        } finally {f.close();}
    }

    static String repeat(char c,int n){StringBuilder s=new StringBuilder();for(int i=0;i<n;i++)s.append(c);return s.toString();}
}
