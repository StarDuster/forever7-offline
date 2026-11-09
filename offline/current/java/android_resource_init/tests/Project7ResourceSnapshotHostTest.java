import com.forever7.offline.*;
import java.io.*;
import java.nio.file.*;
import java.security.*;
import java.util.*;
import java.util.concurrent.atomic.AtomicBoolean;

public final class Project7ResourceSnapshotHostTest {
    static void check(boolean v,String m){if(!v)throw new RuntimeException(m);}
    static String hash(byte[] b)throws Exception {
        StringBuilder s=new StringBuilder();for(byte x:MessageDigest.getInstance("SHA-256").digest(b))s.append(String.format("%02x",x&255));return s.toString();
    }
    interface Work{void run()throws Exception;}
    static int failures;
    static void refuse(Work w)throws Exception{try{w.run();throw new RuntimeException("Unexpected success");}catch(IOException expected){failures++;}}
    static Project7ResourceSnapshot.Asset asset(String n,byte[] b)throws Exception{return new Project7ResourceSnapshot.Asset(n,b.length,hash(b));}
    static void remove(Path p)throws IOException {if(Files.isDirectory(p,LinkOption.NOFOLLOW_LINKS)){try(DirectoryStream<Path>s=Files.newDirectoryStream(p)){for(Path c:s)remove(c);}}Files.deleteIfExists(p);}
    public static void main(String[] args)throws Exception {
        Path docs=Files.createTempDirectory("project7-snapshot-host-").toRealPath();
        try {
            Path res=Files.createDirectory(docs.resolve("res"));List<ResourceImporter.Entry> entries=new ArrayList<>();
            byte[] resource="tiny-resource".getBytes("UTF-8");
            for(int i=0;i<312;i++){String n="toy"+i+".npk";entries.add(new ResourceImporter.Entry(n,resource.length,hash(resource)));Files.write(res.resolve(n),resource);}
            byte[] template="{\"schema\":1,\"version\":455,\"platform\":\"android\",\"parts\":[[\"toy\",[[0,[[1,\"md5\",2,3,4,5,6]]]]]],\"packs\":[[0,[[\"toy\",\"md5\",10]]]],\"manifest\":{\"toy\":[1,[\"md5\",10]]}}".getBytes("US-ASCII");
            byte[] binding="trusted-contract-fixture".getBytes("US-ASCII"),base="base-script".getBytes("US-ASCII"),overlay="overlay-script".getBytes("US-ASCII");
            Map<String,byte[]> bundles=new HashMap<>();bundles.put("template",template);bundles.put("binding",binding);bundles.put("assets/script.npk",base);bundles.put("assets/project7_local.npk",overlay);
            Project7ResourceSnapshot.TrustedContract c=new Project7ResourceSnapshot.TrustedContract(455,640,"android",Project7ResourceSnapshot.SOURCE_MANIFEST_SHA256,Project7ResourceSnapshot.RESOURCE_MANIFEST_SHA256,Project7ResourceSnapshot.entryFingerprint(entries),312,asset("template",template),asset("binding",binding),Arrays.asList(asset("assets/script.npk",base),asset("assets/project7_local.npk",overlay)));
            AtomicBoolean cancel=new AtomicBoolean();ResourceImporter.Progress progress=(n,b,t)->{};
            Project7ResourceSnapshot.Assets assets=n->{byte[]b=bundles.get(n);if(b==null)throw new IOException("Missing");return new ByteArrayInputStream(b);};
            Project7ResourceSnapshot.Receipt receipt=Project7ResourceSnapshot.publish(docs.toFile(),entries,c,assets,cancel,progress);
            check(receipt.verifiedEntries==312 && receipt.snapshotSha256.equals(hash(template)),"receipt");
            Path snapshot=docs.resolve(Project7ResourceSnapshot.SNAPSHOT),bind=docs.resolve(Project7ResourceSnapshot.BINDING),marker=docs.resolve(Project7ResourceSnapshot.COMMIT);
            check(Arrays.equals(Files.readAllBytes(snapshot),template),"six-field bytes unchanged");
            byte[] priorMarker=Files.readAllBytes(marker);
            // A matching old marker never exempts newly corrupt or missing resources.
            byte[] corrupt=resource.clone();corrupt[0]^=1;Files.write(res.resolve("toy5.npk"),corrupt);
            refuse(()->Project7ResourceSnapshot.publish(docs.toFile(),entries,c,assets,cancel,progress));Files.write(res.resolve("toy5.npk"),resource);
            Files.delete(res.resolve("toy7.npk"));refuse(()->Project7ResourceSnapshot.publish(docs.toFile(),entries,c,assets,cancel,progress));Files.write(res.resolve("toy7.npk"),resource);
            cancel.set(true);refuse(()->Project7ResourceSnapshot.publish(docs.toFile(),entries,c,assets,cancel,progress));cancel.set(false);
            byte[] badTemplate=template.clone();badTemplate[3]^=1;bundles.put("template",badTemplate);refuse(()->Project7ResourceSnapshot.publish(docs.toFile(),entries,c,assets,cancel,progress));bundles.put("template",template);
            bundles.put("assets/project7_local.npk",new byte[]{1});refuse(()->Project7ResourceSnapshot.publish(docs.toFile(),entries,c,assets,cancel,progress));bundles.put("assets/project7_local.npk",overlay);
            // Mid-template source failure and cancellation must not replace prior outputs.
            Project7ResourceSnapshot.Assets partial=n->n.equals("template")?new InputStream(){int count;public int read()throws IOException{if(count++==12)throw new IOException("partial stream");return 'x';}}:assets.open(n);
            refuse(()->Project7ResourceSnapshot.publish(docs.toFile(),entries,c,partial,cancel,progress));
            Project7ResourceSnapshot.Assets cancelStream=n->{if(!n.equals("template"))return assets.open(n);return new ByteArrayInputStream(template){public synchronized int read(byte[]b,int o,int l){int n=super.read(b,o,l);cancel.set(true);return n;}};};
            refuse(()->Project7ResourceSnapshot.publish(docs.toFile(),entries,c,cancelStream,cancel,progress));cancel.set(false);
            List<ResourceImporter.Entry> wrong=new ArrayList<>(entries);wrong.set(0,new ResourceImporter.Entry("replacement.npk",resource.length,hash(resource)));refuse(()->Project7ResourceSnapshot.publish(docs.toFile(),wrong,c,assets,cancel,progress));
            Path target=docs.resolve("target");Files.write(target,resource);Files.delete(res.resolve("toy3.npk"));Files.createSymbolicLink(res.resolve("toy3.npk"),target);
            refuse(()->Project7ResourceSnapshot.publish(docs.toFile(),entries,c,assets,cancel,progress));Files.delete(res.resolve("toy3.npk"));Files.write(res.resolve("toy3.npk"),resource);
            Path linked=docs.resolveSibling(docs.getFileName()+"-link");Files.createSymbolicLink(linked,docs);try{refuse(()->Project7ResourceSnapshot.publish(linked.toFile(),entries,c,assets,cancel,progress));}finally{Files.delete(linked);}
            check(Arrays.equals(Files.readAllBytes(snapshot),template),"old snapshot preserved on every failure");check(Arrays.equals(Files.readAllBytes(bind),binding),"old binding preserved");check(Arrays.equals(Files.readAllBytes(marker),priorMarker),"old commit preserved");
            try(DirectoryStream<Path>s=Files.newDirectoryStream(docs,"*.part")){check(!s.iterator().hasNext(),"temporary cleanup");}
            // Successful repeat rehashes all entries even when the prior marker matches.
            final long[] checked={0};Project7ResourceSnapshot.publish(docs.toFile(),entries,c,assets,cancel,(n,b,t)->{if(b==t)checked[0]++;});check(checked[0]==312,"force verification all312");
            System.out.println("Project7ResourceSnapshotHostTest OK:312 force checks, "+failures+" failure cases; prior snapshot/binding/commit retained");
        } finally {remove(docs);}
    }
}
