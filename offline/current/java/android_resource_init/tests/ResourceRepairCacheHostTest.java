import com.forever7.offline.ResourceImporter;
import java.io.*;
import java.nio.file.*;
import java.nio.file.attribute.FileTime;
import java.util.*;
import java.util.concurrent.atomic.AtomicBoolean;

/** Regression: a failed forced hash must invalidate metadata trust before repair. */
public final class ResourceRepairCacheHostTest {
    public static void main(String[] args) throws Exception {
        Path root = Files.createTempDirectory("f7-cache-repair-");
        Map<String,String> saved = new HashMap<>();
        ResourceImporter.Cache cache = new ResourceImporter.Cache() {
            String fingerprint(ResourceImporter.Entry e, File f) {
                return "fixture:" + e.sha256 + ":" + f.length() + ":" + f.lastModified();
            }
            public boolean verified(ResourceImporter.Entry e, File f) {
                return fingerprint(e,f).equals(saved.get(e.name));
            }
            public void remember(ResourceImporter.Entry e, File f) { saved.put(e.name,fingerprint(e,f)); }
            public void invalidate(ResourceImporter.Entry e) { saved.remove(e.name); }
        };
        byte[] good = "original-resource".getBytes("UTF-8");
        ResourceImporter.Entry entry = new ResourceImporter.Entry("hero.npk",good.length,ResourceImporterHostTest.hash(good));
        try {
            Path target=root.resolve(entry.name); Files.write(target,good);
            try(ResourceImporter session=new ResourceImporter(root.toFile(),Arrays.asList(entry),cache,new AtomicBoolean(),(n,b,t)->{})) {
                ResourceImporterHostTest.check(session.verify(entry,true),"initial forced verification");
            }
            FileTime timestamp=Files.getLastModifiedTime(target);
            byte[] bad=good.clone();bad[0]^=1;Files.write(target,bad);Files.setLastModifiedTime(target,timestamp);
            ResourceImporterHostTest.check(cache.verified(entry,target.toFile()),"same metadata reproduces stale trust");
            try(ResourceImporter session=new ResourceImporter(root.toFile(),Arrays.asList(entry),cache,new AtomicBoolean(),(n,b,t)->{})) {
                ResourceImporterHostTest.check(!session.verify(entry,true),"forced check detects corruption");
                ResourceImporterHostTest.check(!cache.verified(entry,target.toFile()),"forced failure invalidates persisted trust");
            }
            try(ResourceImporter session=new ResourceImporter(root.toFile(),Arrays.asList(entry),cache,new AtomicBoolean(),(n,b,t)->{})) {
                ResourceImporterHostTest.check(!session.verify(entry,false),"new session cannot skip corrupt resource");
                session.importZip(new ByteArrayInputStream(ResourceImporterHostTest.zip(new String[]{entry.name},new byte[][]{good})));
                ResourceImporterHostTest.check(Arrays.equals(Files.readAllBytes(target),good),"ZIP actually replaced corrupt bytes");
                ResourceImporterHostTest.check(session.verify(entry,true),"repaired resource passes independent hash");
            }
            // Real Activity order: importZip(source, force=true) before missing(force).
            // A same-size/same-mtime damaged disk hit the cached fingerprint; the
            // old importZip(false) skipped the disk and left the bad file for the
            // next forced pass. One explicit ZIP import must now replace it.
            FileTime cachedTimestamp=Files.getLastModifiedTime(target);
            Files.write(target,good);
            byte[] stale=good.clone();stale[0]^=1;Files.write(target,stale);Files.setLastModifiedTime(target,cachedTimestamp);
            ResourceImporterHostTest.check(cache.verified(entry,target.toFile()),"stale fingerprint before Activity import");
            try(ResourceImporter legacy=new ResourceImporter(root.toFile(),Arrays.asList(entry),cache,new AtomicBoolean(),(n,b,t)->{})) {
                legacy.importZip(new ByteArrayInputStream(ResourceImporterHostTest.zip(new String[]{entry.name},new byte[][]{good})),false);
                ResourceImporterHostTest.check(!Arrays.equals(Files.readAllBytes(target),good),"legacy non-force import leaves stale same-metadata disk");
            }
            try(ResourceImporter session=new ResourceImporter(root.toFile(),Arrays.asList(entry),cache,new AtomicBoolean(),(n,b,t)->{})) {
                session.importZip(new ByteArrayInputStream(ResourceImporterHostTest.zip(new String[]{entry.name},new byte[][]{good})),true);
                ResourceImporterHostTest.check(Arrays.equals(Files.readAllBytes(target),good),"one forced ZIP import replaced bad same-metadata disk");
                ResourceImporterHostTest.check(session.missing(true).isEmpty(),"post-import force verification clean");
            }
            System.out.println("PASS stale-cache corruption -> invalidation -> new-session ZIP repair; host only");
            System.out.println("PASS Activity-order importZip(force=true) replaces same-metadata bad disk in one import");
        } finally {
            try(java.util.stream.Stream<Path> files=Files.walk(root)) {
                for(Path p:(Iterable<Path>)files.sorted(Comparator.reverseOrder())::iterator) Files.delete(p);
            }
        }
    }
}
