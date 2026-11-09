package com.forever7.offline;

import java.io.*;
import java.lang.reflect.Constructor;
import java.lang.reflect.Field;
import java.lang.reflect.Method;
import java.security.*;
import java.util.*;
import java.util.concurrent.atomic.AtomicBoolean;

/** Publishes a trusted bundled six-field template only after fresh full resource validation.
 * No downloader, game mode setter, native-check bypass, or on-disk READY discovery.
 * Call after closing the downloader's session. A returned Receipt is per-call evidence.
 *
 * A private in-app-files ledger may shorten repeated startup: it binds the pinned contract,
 * the canonical resource root and per-entry device/inode/size/ctime/mtime metadata. The fast
 * path never hashes resources and only runs when every pin and all metadata still match.
 * Any uncertainty falls back to the original forced SHA-256 pass; a new ledger is committed
 * only after that complete pass, via fsync plus same-directory atomic rename.
 */
public final class Project7ResourceSnapshot {
    private Project7ResourceSnapshot() { }
    private static final long LIMIT = 64L * 1024 * 1024;
    public static final String SOURCE_MANIFEST_SHA256="421dd73952cdc4903a52c2f91f0283401b56acbb293a4cf693e149db612e3082";
    public static final String RESOURCE_MANIFEST_SHA256="c2e926909541ea2070f58a3b5c702c8989c10db081d299abb6f1fc193ec8ae4f";
    public static final String SNAPSHOT = "project7-verified-resources.json";
    public static final String BINDING = "project7-verified-resources.binding.json";
    public static final String COMMIT = "project7-verified-resources.commit";
    /** Ledger name; always resolved inside a caller-supplied private files directory. */
    public static final String LEDGER = "project7-verified-resources.ledger";
    private static final String LEDGER_FORMAT = "project7-resource-ledger-v1";
    private static final int LEDGER_FORMAT_VERSION = 1;
    private static final long LEDGER_LIMIT = 4L * 1024 * 1024;
    public interface Assets { InputStream open(String name) throws IOException; }
    public static final class Asset {
        public final String name, sha256;
        public final long bytes;
        public Asset(String name, long bytes, String sha256) {
            if (name == null || !name.matches("[A-Za-z0-9_./-]+") || name.startsWith("/") ||
                name.contains("//") || Arrays.asList(name.split("/", -1)).contains("..") ||
                Arrays.asList(name.split("/", -1)).contains(".") || name.endsWith("/") ||
                bytes <= 0 || !validHash(sha256)) throw new IllegalArgumentException("Invalid trusted asset");
            this.name=name; this.bytes=bytes; this.sha256=sha256;
        }
    }
    /** Construct only from bundled code or a bundled asset loader anchored by a source pin.
     * Never populate these fields from Documents or an existing marker. Binding asset's
     * pinned bytes bind source/resource manifests, scripts, counts and dual versions.
     */
    public static final class TrustedContract {
        public final int clientVersion, resourceVersion, entryCount;
        public final String platform, sourceManifestSha256, resourceManifestSha256, entryManifestSha256;
        public final Asset snapshot, binding;
        public final List<Asset> scripts;
        public TrustedContract(int clientVersion, int resourceVersion, String platform,
                String sourceManifestSha256, String resourceManifestSha256,
                String entryManifestSha256, int entryCount, Asset snapshot, Asset binding,
                List<Asset> scripts) {
            if (clientVersion != 455 || resourceVersion != 640 || !"android".equals(platform) ||
                !SOURCE_MANIFEST_SHA256.equals(sourceManifestSha256) || !RESOURCE_MANIFEST_SHA256.equals(resourceManifestSha256) ||
                !validHash(entryManifestSha256) || entryCount != 312 || snapshot == null || binding == null ||
                snapshot.bytes > LIMIT || binding.bytes > 1024*1024 || scripts == null || scripts.size()!=2)
                throw new IllegalArgumentException("Invalid trusted contract");
            HashSet<String> names=new HashSet<String>();
            for (Asset a:scripts) if(a==null || a.bytes>LIMIT || !names.add(a.name)) throw new IllegalArgumentException("Duplicate script asset");
            if (!names.equals(new HashSet<String>(Arrays.asList("assets/script.npk","assets/project7_local.npk"))))
                throw new IllegalArgumentException("Wrong script assets");
            this.clientVersion=clientVersion;this.resourceVersion=resourceVersion;this.platform=platform;
            this.sourceManifestSha256=sourceManifestSha256;this.resourceManifestSha256=resourceManifestSha256;
            this.entryManifestSha256=entryManifestSha256;this.entryCount=entryCount;
            this.snapshot=snapshot;this.binding=binding;this.scripts=Collections.unmodifiableList(new ArrayList<Asset>(scripts));
        }
    }
    public static final class Receipt {
        public final String snapshotSha256, bindingSha256;
        public final int verifiedEntries;
        private Receipt(TrustedContract c) { snapshotSha256=c.snapshot.sha256;bindingSha256=c.binding.sha256;verifiedEntries=c.entryCount; }
    }
    /** Injectable metadata probe. Returning null (or throwing) means "unavailable"; the caller
     * then uses the original forced SHA-256 pass and commits no ledger. The Android default is
     * public reflection over android.system.Os.stat/StructStat/StructTimespec, never hidden API.
     */
    public interface MetadataProbe {
        Metadata probe(File file) throws IOException;
        /** False means timestamps/identity precision is not trustworthy; force the full hash. */
        default boolean reliable() { return true; }
    }
    public static final class Metadata {
        public final long dev, ino, size, ctimeNs, mtimeNs;
        public Metadata(long dev, long ino, long size, long ctimeNs, long mtimeNs) {
            if (dev < 0 || ino < 0 || size < 0 || ctimeNs < 0 || mtimeNs < 0)
                throw new IllegalArgumentException("Invalid file metadata");
            this.dev=dev; this.ino=ino; this.size=size; this.ctimeNs=ctimeNs; this.mtimeNs=mtimeNs;
        }
    }
    /** Package-private host-test seam invoked after the temp ledger fsync and before its rename.
     * Production overloads always pass null. */
    interface LedgerCommitObserver { void beforeRename() throws IOException; }
    private static final class Ledger { final Metadata[] metadata; Ledger(Metadata[] metadata) { this.metadata=metadata; } }
    /** Resolve the one private ledger location under the caller's internal files dir. */
    public static File privateLedger(File filesDir) throws IOException {
        if (filesDir == null) throw new IllegalArgumentException("Missing internal files directory");
        File directory = canonical(filesDir);
        if (externalStorage(directory)) throw new IOException("External storage ledger rejected");
        if (!directory.isDirectory()) throw new IOException("Internal files directory unavailable");
        return new File(directory, LEDGER);
    }
    private static boolean externalStorage(File file) {
        String path=file.getPath();
        return path.startsWith("/storage/") || path.startsWith("/sdcard/") ||
            path.startsWith("/mnt/sdcard/") || path.startsWith("/data/media/");
    }
    private static boolean validHash(String s) { return s!=null && s.matches("[0-9a-f]{64}"); }
    private static MessageDigest hash() throws IOException {
        try { return MessageDigest.getInstance("SHA-256"); }
        catch (NoSuchAlgorithmException e) { throw new IOException(e); }
    }
    private static File canonical(File file) throws IOException {
        File absolute=file.getAbsoluteFile();
        if(!absolute.equals(absolute.getCanonicalFile())) throw new IOException("Symbolic or noncanonical path");
        return absolute;
    }
    private static void checkpoint(AtomicBoolean cancelled) throws IOException {
        if(cancelled.get() || Thread.currentThread().isInterrupted()) throw new ResourceImporter.Cancelled();
    }
    public static String entryFingerprint(List<ResourceImporter.Entry> entries) throws IOException {
        if(entries==null || entries.isEmpty()) throw new IOException("Empty resource manifest");
        ArrayList<ResourceImporter.Entry> sorted=new ArrayList<ResourceImporter.Entry>(entries);
        Collections.sort(sorted,new Comparator<ResourceImporter.Entry>() {
            public int compare(ResourceImporter.Entry a,ResourceImporter.Entry b) { return a.name.compareTo(b.name); }
        });
        MessageDigest d=hash();String previous=null;
        for(ResourceImporter.Entry e:sorted) {
            if(e.name.equals(previous)) throw new IOException("Duplicate resource manifest entry");previous=e.name;
            d.update((e.name+"\t"+e.bytes+"\t"+e.sha256+"\n").getBytes("US-ASCII"));
        }
        return ResourceImporter.hex(d.digest());
    }
    private static List<ResourceImporter.Entry> sortedEntries(List<ResourceImporter.Entry> entries) {
        ArrayList<ResourceImporter.Entry> sorted=new ArrayList<ResourceImporter.Entry>(entries);
        Collections.sort(sorted,new Comparator<ResourceImporter.Entry>() {
            public int compare(ResourceImporter.Entry a,ResourceImporter.Entry b) { return a.name.compareTo(b.name); }
        });
        return sorted;
    }
    private static void streamAsset(Assets assets,Asset expected,File destination,AtomicBoolean cancel) throws IOException {
        checkpoint(cancel);MessageDigest digest=hash();long bytes=0;
        try(InputStream in=assets.open(expected.name)) {
            if(in==null) throw new IOException("Missing bundled asset");
            FileOutputStream out=destination==null?null:new FileOutputStream(destination);
            try {
                byte[] buffer=new byte[128*1024];int n;
                while((n=in.read(buffer))!=-1) {
                    checkpoint(cancel);bytes+=n;if(bytes>expected.bytes)throw new IOException("Oversized bundled asset");
                    digest.update(buffer,0,n);if(out!=null)out.write(buffer,0,n);
                }
                if(bytes!=expected.bytes || !ResourceImporter.hex(digest.digest()).equals(expected.sha256))
                    throw new IOException("Bundled asset hash/size mismatch");
                checkpoint(cancel);if(out!=null)out.getFD().sync();
            } finally { if(out!=null)out.close(); }
        }
    }
    private static void writeSynced(File file,byte[] bytes) throws IOException {
        try(FileOutputStream out=new FileOutputStream(file)) {out.write(bytes);out.getFD().sync();}
    }
    private static void rename(File temporary,File target) throws IOException {
        canonical(target);if(target.exists()&&!target.isFile())throw new IOException("Publication destination not regular");
        // Android/Linux and host POSIX rename is atomic in the same directory.
        if(!temporary.renameTo(target))throw new IOException("Atomic snapshot rename failed");
    }
    private static void verifyAll(ResourceImporter session,File res,List<ResourceImporter.Entry> entries,
            AtomicBoolean cancelled) throws IOException {
        for(ResourceImporter.Entry e:entries) {
            checkpoint(cancelled);File actual=canonical(session.destination(e));
            if(!actual.equals(canonical(new File(res,e.name))) || !session.verify(e,true))
                throw new IOException("Resource verification failed: "+e.name);
        }
    }
    /** Only a ledger outside Documents/import storage is considered; a planted external ledger
     * is ignored and never rewritten. */
    private static File trustedLedger(File ledger,File documents) {
        if(ledger==null) return null;
        try {
            File candidate=canonical(ledger);
            if(externalStorage(candidate)) return null;
            String root=documents.getPath();
            if(candidate.getPath().equals(root) || candidate.getPath().startsWith(root+File.separator)) return null;
            return candidate;
        } catch(IOException error) { return null; }
    }
    private static byte[] readCapped(File file,long limit) throws IOException {
        if(!file.isFile()) return null;
        long length=file.length();if(length<=0 || length>limit) return null;
        ByteArrayOutputStream out=new ByteArrayOutputStream((int)length);
        try(InputStream in=new FileInputStream(file)) {
            byte[] buffer=new byte[8192];int n;long total=0;
            while((n=in.read(buffer))!=-1) { total+=n;if(total>limit) return null;out.write(buffer,0,n); }
        }
        return out.toByteArray();
    }
    private static boolean same(Metadata a,Metadata b) {
        return a!=null && b!=null && a.dev==b.dev && a.ino==b.ino && a.size==b.size &&
            a.ctimeNs==b.ctimeNs && a.mtimeNs==b.mtimeNs;
    }
    private static boolean same(Metadata[] a,Metadata[] b) {
        if(a==null || b==null || a.length!=b.length) return false;
        for(int i=0;i<a.length;i++) if(!same(a[i],b[i])) return false;
        return true;
    }
    private static Metadata[] probeAll(MetadataProbe probe,File res,List<ResourceImporter.Entry> entries,
            AtomicBoolean cancelled) throws IOException {
        Metadata[] result=new Metadata[entries.size()];
        for(int i=0;i<entries.size();i++) {
            checkpoint(cancelled);
            ResourceImporter.Entry e=entries.get(i);
            File file;
            try { file=canonical(new File(res,e.name)); }
            catch(IOException error) { if(error instanceof ResourceImporter.Cancelled) throw error; return null; }
            if(!file.isFile()) return null;
            Metadata metadata;
            try { metadata=probe.probe(file); }
            catch(IOException error) { if(error instanceof ResourceImporter.Cancelled) throw error; return null; }
            catch(RuntimeException error) { return null; }
            if(metadata==null || metadata.size!=e.bytes || file.length()!=metadata.size ||
                    metadata.ino<=0 || metadata.ctimeNs<=0 || metadata.mtimeNs<=0) return null;
            result[i]=metadata;
        }
        return result;
    }
    private static String hex(byte[] value) { return ResourceImporter.hex(value); }
    private static byte[] unhex(String value) {
        if(value==null || value.length()%2!=0) return null;
        byte[] result=new byte[value.length()/2];
        for(int i=0;i<result.length;i++) {
            int high=Character.digit(value.charAt(i*2),16),low=Character.digit(value.charAt(i*2+1),16);
            if(high<0 || low<0) return null;
            result[i]=(byte)((high<<4)|low);
        }
        return result;
    }
    private static byte[] encodeLedger(TrustedContract contract,File res,List<ResourceImporter.Entry> sorted,
            Metadata[] metadata) throws IOException {
        StringBuilder out=new StringBuilder();
        out.append(LEDGER_FORMAT).append('\n');
        out.append("format=").append(LEDGER_FORMAT_VERSION).append('\n');
        out.append("sourceManifest=").append(contract.sourceManifestSha256).append('\n');
        out.append("resourceManifest=").append(contract.resourceManifestSha256).append('\n');
        out.append("entryManifest=").append(contract.entryManifestSha256).append('\n');
        out.append("clientVersion=").append(contract.clientVersion).append('\n');
        out.append("resourceVersion=").append(contract.resourceVersion).append('\n');
        out.append("entryCount=").append(contract.entryCount).append('\n');
        out.append("resRoot=").append(hex(res.getPath().getBytes("UTF-8"))).append('\n');
        appendPin(out,"snapshot",contract.snapshot);
        appendPin(out,"binding",contract.binding);
        ArrayList<Asset> scripts=new ArrayList<Asset>(contract.scripts);
        Collections.sort(scripts,new Comparator<Asset>() {
            public int compare(Asset a,Asset b) { return a.name.compareTo(b.name); }
        });
        for(Asset script:scripts)
            out.append("script=").append(script.name).append(' ').append(script.bytes).append(' ')
                .append(script.sha256).append('\n');
        for(int i=0;i<sorted.size();i++) {
            ResourceImporter.Entry e=sorted.get(i);Metadata m=metadata[i];
            out.append("entry=").append(e.name).append('\t').append(e.bytes).append('\t').append(e.sha256)
                .append('\t').append(m.dev).append('\t').append(m.ino).append('\t').append(m.size)
                .append('\t').append(m.ctimeNs).append('\t').append(m.mtimeNs).append('\n');
        }
        return out.toString().getBytes("US-ASCII");
    }
    private static void appendPin(StringBuilder out,String key,Asset asset) {
        out.append(key).append('=').append(asset.bytes).append(' ').append(asset.sha256).append('\n');
    }
    private static Asset parsePin(String key,String value) {
        if(value==null) throw new IllegalArgumentException("Missing "+key);
        String[] fields=value.split(" ", -1);
        if(fields.length!=2) throw new IllegalArgumentException("Bad "+key);
        long bytes=Long.parseLong(fields[0]);
        if(bytes<=0) throw new IllegalArgumentException("Bad "+key+" bytes");
        return new Asset(key.equals("snapshot")?"template":key.equals("binding")?"binding":key,bytes,fields[1]);
    }
    private static Metadata parseEntry(String value,ResourceImporter.Entry expected) {
        String[] fields=value.split("\t", -1);
        if(fields.length!=8) throw new IllegalArgumentException("Bad ledger entry");
        if(!fields[0].equals(expected.name)) throw new IllegalArgumentException("Ledger entry order mismatch");
        long bytes=Long.parseLong(fields[1]),dev=Long.parseLong(fields[3]),ino=Long.parseLong(fields[4]),
            size=Long.parseLong(fields[5]),ctime=Long.parseLong(fields[6]),mtime=Long.parseLong(fields[7]);
        if(bytes!=expected.bytes || !fields[2].equals(expected.sha256) || size!=bytes ||
                ino<=0 || ctime<=0 || mtime<=0) throw new IllegalArgumentException("Ledger entry mismatch");
        return new Metadata(dev,ino,size,ctime,mtime);
    }
    /** Validate every pin and every metadata value. Returns null on any doubt; never throws for
     * a malformed/stale ledger and never reads resource content. */
    private static Ledger loadLedger(File ledger,TrustedContract contract,File res,
            List<ResourceImporter.Entry> sorted,MetadataProbe probe,AtomicBoolean cancelled) throws IOException {
        byte[] raw;
        try { raw=readCapped(ledger,LEDGER_LIMIT); }
        catch(IOException error) { if(error instanceof ResourceImporter.Cancelled) throw error; return null; }
        if(raw==null) return null;
        String text=new String(raw,"US-ASCII");
        String[] lines=text.split("\n",-1);
        if(lines.length<13 || !LEDGER_FORMAT.equals(lines[0]) || !lines[lines.length-1].isEmpty()) return null;
        HashMap<String,String> values=new HashMap<String,String>();
        ArrayList<String> scriptLines=new ArrayList<String>(),entryLines=new ArrayList<String>();
        for(int i=1;i<lines.length-1;i++) {
            String line=lines[i];int split=line.indexOf('=');
            if(split<=0) return null;
            String key=line.substring(0,split),value=line.substring(split+1);
            if(key.equals("script")) scriptLines.add(value);
            else if(key.equals("entry")) entryLines.add(value);
            else if(values.put(key,value)!=null) return null;
        }
        if(values.size()!=10) return null;
        try {
            if(Integer.parseInt(values.get("format"))!=LEDGER_FORMAT_VERSION) return null;
            if(!contract.sourceManifestSha256.equals(values.get("sourceManifest")) ||
                    !contract.resourceManifestSha256.equals(values.get("resourceManifest")) ||
                    !contract.entryManifestSha256.equals(values.get("entryManifest"))) return null;
            if(Integer.parseInt(values.get("clientVersion"))!=contract.clientVersion ||
                    Integer.parseInt(values.get("resourceVersion"))!=contract.resourceVersion ||
                    Integer.parseInt(values.get("entryCount"))!=contract.entryCount) return null;
            if(!Arrays.equals(unhex(values.get("resRoot")),res.getPath().getBytes("UTF-8"))) return null;
            Asset ledgerSnapshot=parsePin("snapshot",values.get("snapshot"));
            Asset ledgerBinding=parsePin("binding",values.get("binding"));
            if(ledgerSnapshot.bytes!=contract.snapshot.bytes || !ledgerSnapshot.sha256.equals(contract.snapshot.sha256) ||
                    ledgerBinding.bytes!=contract.binding.bytes || !ledgerBinding.sha256.equals(contract.binding.sha256)) return null;
            if(scriptLines.size()!=contract.scripts.size()) return null;
            HashMap<String,Asset> expectedScripts=new HashMap<String,Asset>();
            for(Asset script:contract.scripts) expectedScripts.put(script.name,script);
            HashSet<String> seenScripts=new HashSet<String>();
            for(String line:scriptLines) {
                String[] fields=line.split(" ",-1);
                if(fields.length!=3 || !seenScripts.add(fields[0])) return null;
                Asset expected=expectedScripts.get(fields[0]);
                if(expected==null) return null;
                long bytes=Long.parseLong(fields[1]);
                if(bytes!=expected.bytes || !fields[2].equals(expected.sha256)) return null;
            }
            if(!seenScripts.equals(expectedScripts.keySet())) return null;
            if(entryLines.size()!=sorted.size()) return null;
            Metadata[] metadata=new Metadata[sorted.size()];
            for(int i=0;i<sorted.size();i++) {
                ResourceImporter.Entry entry=sorted.get(i);
                Metadata value=parseEntry(entryLines.get(i),entry);
                metadata[i]=value;
            }
            for(int i=0;i<sorted.size();i++) {
                checkpoint(cancelled);
                File file;
                Metadata current;
                try {
                    file=canonical(new File(res,sorted.get(i).name));
                    if(!file.isFile()) return null;
                    current=probe.probe(file);
                } catch(IOException error) {
                    if(error instanceof ResourceImporter.Cancelled) throw error;
                    return null;
                } catch(RuntimeException error) { return null; }
                if(!same(metadata[i],current) || file.length()!=current.size) return null;
            }
            return new Ledger(metadata);
        } catch(RuntimeException error) { return null; }
    }
    private static void commitLedger(File ledger,byte[] bytes,AtomicBoolean cancelled,
            LedgerCommitObserver observer) throws IOException {
        File directory=ledger.getParentFile();
        if(directory==null || (!directory.isDirectory() && !directory.mkdirs()))
            throw new IOException("Ledger directory unavailable");
        canonical(ledger);
        if(ledger.exists() && !ledger.isFile()) throw new IOException("Ledger destination not regular");
        checkpoint(cancelled);
        File temporary=File.createTempFile(".project7-ledger-",".part",directory);
        try {
            writeSynced(temporary,bytes);
            // Deterministic host-test seam; production always passes null.
            if(observer!=null) observer.beforeRename();
            checkpoint(cancelled);
            if(!temporary.renameTo(ledger)) throw new IOException("Atomic ledger rename failed");
            checkpoint(cancelled);
        } finally {
            if(temporary.exists() && !temporary.delete()) throw new IOException("Ledger temporary cleanup failed");
        }
    }
    /** Public-reflection Android probe using only android.system.Os.stat and public StructStat /
     * StructTimespec fields (API 26 safe). Any missing class, field or invoke -> null (full hash). */
    public static MetadataProbe androidMetadataProbe() {
        try {
            final Class<?> os=Class.forName("android.system.Os");
            final Class<?> statClass=Class.forName("android.system.StructStat");
            final Class<?> timespec=Class.forName("android.system.StructTimespec");
            final Field dev=statClass.getField("st_dev"),ino=statClass.getField("st_ino"),
                size=statClass.getField("st_size"),ctime=statClass.getField("st_ctim"),mtime=statClass.getField("st_mtim");
            final Field seconds=timespec.getField("tv_sec"),nanos=timespec.getField("tv_nsec");
            if(dev.getType()!=long.class || ino.getType()!=long.class || size.getType()!=long.class ||
                    ctime.getType()!=timespec || mtime.getType()!=timespec ||
                    seconds.getType()!=long.class || nanos.getType()!=long.class) return null;
            Method stat;
            boolean returnsStat;
            try {
                stat=os.getMethod("stat",String.class);
                if(stat.getReturnType()!=statClass) return null;
                returnsStat=true;
            } catch(NoSuchMethodException missing) {
                stat=os.getMethod("stat",String.class,statClass);
                if(stat.getReturnType()!=void.class) return null;
                returnsStat=false;
            }
            final Method statMethod=stat;
            final boolean statReturns=returnsStat;
            final Constructor<?> constructor=returnsStat?null:statClass.getConstructor();
            return new MetadataProbe() {
                public Metadata probe(File file) throws IOException {
                    try {
                        Object value;
                        if(statReturns) value=statMethod.invoke(null,file.getAbsolutePath());
                        else {
                            value=constructor.newInstance();
                            statMethod.invoke(null,file.getAbsolutePath(),value);
                        }
                        if(value==null) return null;
                        Object c=ctime.get(value),m=mtime.get(value);
                        long cs=(Long)seconds.get(c),cn=(Long)nanos.get(c);
                        long ms=(Long)seconds.get(m),mn=(Long)nanos.get(m);
                        if(cs<0 || ms<0 || cn<0 || cn>=1000000000L || mn<0 || mn>=1000000000L) return null;
                        long ctimeNs=Math.addExact(Math.multiplyExact(cs,1000000000L),cn);
                        long mtimeNs=Math.addExact(Math.multiplyExact(ms,1000000000L),mn);
                        return new Metadata((Long)dev.get(value),(Long)ino.get(value),(Long)size.get(value),ctimeNs,mtimeNs);
                    } catch(Throwable unavailable) { return null; }
                }
            };
        } catch(Throwable unavailable) { return null; }
    }
    /** Original entry point: always a full forced SHA-256 pass, no ledger. */
    public static Receipt publish(File documents,List<ResourceImporter.Entry> manifest,TrustedContract contract,
            Assets assets,AtomicBoolean cancelled,ResourceImporter.Progress progress) throws IOException {
        return publish(documents,manifest,contract,assets,cancelled,progress,null,null);
    }
    /** Guarded fast path used by the startup platform; probe is the public-reflection default. */
    public static Receipt publish(File documents,List<ResourceImporter.Entry> manifest,TrustedContract contract,
            Assets assets,AtomicBoolean cancelled,ResourceImporter.Progress progress,File ledger) throws IOException {
        return publish(documents,manifest,contract,assets,cancelled,progress,ledger,null);
    }
    /** Host-testable overload with an injected metadata probe. */
    public static Receipt publish(File documents,List<ResourceImporter.Entry> manifest,TrustedContract contract,
            Assets assets,AtomicBoolean cancelled,ResourceImporter.Progress progress,File ledger,
            MetadataProbe probe) throws IOException {
        return publish(documents,manifest,contract,assets,cancelled,progress,ledger,probe,null);
    }
    /** Package-private overload adding the deterministic ledger-commit test observer. */
    static Receipt publish(File documents,List<ResourceImporter.Entry> manifest,TrustedContract contract,
            Assets assets,AtomicBoolean cancelled,ResourceImporter.Progress progress,File ledger,
            MetadataProbe probe,LedgerCommitObserver observer) throws IOException {
        if(contract==null || assets==null || cancelled==null || progress==null)throw new IllegalArgumentException("Missing publication input");
        checkpoint(cancelled);File docs=canonical(documents);
        if(!docs.isDirectory())throw new IOException("Documents directory unavailable");
        File res=canonical(new File(docs,"res"));if(!res.isDirectory())throw new IOException("Resources missing");
        // Copy to avoid caller mutations after the trust comparison.
        List<ResourceImporter.Entry> entries=new ArrayList<ResourceImporter.Entry>(manifest);
        if(entries.size()!=contract.entryCount || !entryFingerprint(entries).equals(contract.entryManifestSha256))
            throw new IOException("Resource manifest binding mismatch");
        List<ResourceImporter.Entry> sorted=sortedEntries(entries);
        File privateLedger=trustedLedger(ledger,docs);
        MetadataProbe effective=probe;
        if(effective==null && privateLedger!=null) effective=androidMetadataProbe();
        if(effective!=null && !effective.reliable()) effective=null;
        ResourceImporter.Cache noCache=new ResourceImporter.Cache() {
            public boolean verified(ResourceImporter.Entry e,File f) {return false;}
            public void remember(ResourceImporter.Entry e,File f) { }
        };
        try(ResourceImporter session=new ResourceImporter(res,entries,noCache,cancelled,progress)) {
            Ledger loaded=null;
            Metadata[] fastMetadata=null;
            if(privateLedger!=null && effective!=null) {
                loaded=loadLedger(privateLedger,contract,res,sorted,effective,cancelled);
                if(loaded!=null) fastMetadata=loaded.metadata;
            }
            boolean fast=fastMetadata!=null;
            boolean probesAvailable=privateLedger!=null && effective!=null;
            Metadata[] ledgerMetadata=null;
            if(!fast) {
                Metadata[] start=probesAvailable?probeAll(effective,res,sorted,cancelled):null;
                verifyAll(session,res,entries,cancelled);
                if(start!=null) {
                    Metadata[] end=probeAll(effective,res,sorted,cancelled);
                    if(end==null || !same(start,end))
                        throw new IOException("Resource metadata changed during verification");
                    ledgerMetadata=end;
                }
            }
            File snapshot=canonical(new File(docs,SNAPSHOT)),binding=canonical(new File(docs,BINDING)),
                commit=canonical(new File(docs,COMMIT));
            for(File f:Arrays.asList(snapshot,binding,commit))if(f.exists()&&!f.isFile())throw new IOException("Nonregular publication destination");
            // Unique same-directory temporaries: never follow/overwrite stale .part paths.
            File s=File.createTempFile(".project7-snapshot-",".part",docs),b=null,m=null;
            try {
                b=File.createTempFile(".project7-binding-",".part",docs);m=File.createTempFile(".project7-commit-",".part",docs);
                for(Asset script:contract.scripts)streamAsset(assets,script,null,cancelled);
                streamAsset(assets,contract.snapshot,s,cancelled);streamAsset(assets,contract.binding,b,cancelled);
                byte[] marker=("project7-resource-commit-v1\n"+contract.snapshot.sha256+"\n"+contract.binding.sha256+"\n").getBytes("US-ASCII");
                writeSynced(m,marker);checkpoint(cancelled);
                // Re-probe immediately before publication. Any observed change forces a stable
                // full-SHA re-verification or a closed failure; it never falls through to a
                // Receipt merely because the ledger is dropped.
                if(fast) {
                    Metadata[] now=probeAll(effective,res,sorted,cancelled);
                    if(now==null)
                        throw new IOException("Resource metadata unavailable after fast verification");
                    if(!same(fastMetadata,now)) {
                        Metadata[] start=probeAll(effective,res,sorted,cancelled);
                        if(start==null)
                            throw new IOException("Resource metadata unavailable during fallback verification");
                        verifyAll(session,res,entries,cancelled);
                        Metadata[] end=probeAll(effective,res,sorted,cancelled);
                        if(end==null || !same(start,end))
                            throw new IOException("Resource metadata changed during fallback verification");
                        ledgerMetadata=end;
                    }
                }
                if(ledgerMetadata!=null) {
                    Metadata[] now=probeAll(effective,res,sorted,cancelled);
                    if(now==null || !same(ledgerMetadata,now))
                        throw new IOException("Resource metadata changed during publication");
                }
                checkpoint(cancelled);
                // All source checks and cancellation precede publication. Snapshot/binding are
                // replaced, then the ledger, then the marker. A ledger commit failure therefore
                // leaves the old marker intact. No READY inference is made from any old marker.
                rename(s,snapshot);rename(b,binding);
                if(privateLedger!=null && ledgerMetadata!=null)
                    commitLedger(privateLedger,encodeLedger(contract,res,sorted,ledgerMetadata),
                        cancelled,observer);
                checkpoint(cancelled);
                rename(m,commit);
                checkpoint(cancelled);
                return new Receipt(contract);
            } finally {s.delete();if(b!=null)b.delete();if(m!=null)m.delete();}
        }
    }
}
