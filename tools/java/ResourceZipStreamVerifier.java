import com.forever7.offline.ResourceImporter;
import java.io.*;
import java.nio.file.*;
import java.nio.file.attribute.BasicFileAttributes;
import java.util.*;
import java.util.concurrent.atomic.AtomicBoolean;

/** Verify a full streamed archive against existing targets without copying assets. */
public final class ResourceZipStreamVerifier {
    static final class Stream extends FilterInputStream {
        long bytes;
        Stream(InputStream input) { super(input); }
        public int read() throws IOException { int n=in.read();if(n>=0)bytes++;return n; }
        public int read(byte[] b,int off,int len) throws IOException {
            int n=in.read(b,off,len);if(n>0)bytes+=n;return n;
        }
        public void close() {} // Drain the central directory after ZipInputStream ends.
    }
    static String identity(Path path) throws IOException {
        BasicFileAttributes a=Files.readAttributes(path,BasicFileAttributes.class);
        if(!a.isRegularFile())throw new IOException("Not a regular source file: "+path);
        return a.fileKey()+":"+a.size()+":"+a.lastModifiedTime();
    }
    public static void main(String[] args) throws Exception {
        if(args.length!=3)throw new IllegalArgumentException("plan.tsv resource-directory result.json");
        Path root=Paths.get(args[1]).toRealPath();
        List<ResourceImporter.Entry> entries=new ArrayList<>();
        Map<Path,String> before=new LinkedHashMap<>();
        long expected=0;
        for(String line:Files.readAllLines(Paths.get(args[0]))) {
            String[] row=line.split("\t",-1);
            if(row.length!=3)throw new IOException("Bad manifest plan");
            ResourceImporter.Entry entry=new ResourceImporter.Entry(row[0],Long.parseLong(row[1]),row[2]);
            Path path=root.resolve(entry.name);
            if(!path.toAbsolutePath().equals(path.toRealPath()))throw new IOException("Symlink source");
            if(Files.size(path)!=entry.bytes)throw new IOException("Source size mismatch: "+entry.name);
            before.put(path,identity(path));entries.add(entry);expected+=entry.bytes;
        }
        Set<String> validated=new HashSet<>();
        ResourceImporter.Cache existing=new ResourceImporter.Cache() {
            public boolean verified(ResourceImporter.Entry entry,File file) { return true; }
            public void remember(ResourceImporter.Entry entry,File file) {
                throw new IllegalStateException("Verifier must never write a target: "+entry.name);
            }
        };
        Stream input=new Stream(System.in);
        try(ResourceImporter importer=new ResourceImporter(root.toFile(),entries,existing,
                new AtomicBoolean(false),(name,done,total)->{if(done==total)validated.add(name);})) {
            importer.importZip(input); // Production code hashes every skipped archive member.
            if(!importer.missing(false).isEmpty())throw new IOException("Missing final target");
        }
        byte[] tail=new byte[128*1024];while(input.read(tail,0,tail.length)!=-1){}
        if(validated.size()!=entries.size())throw new IOException("Incomplete streamed archive");
        for(Map.Entry<Path,String> entry:before.entrySet())
            if(!entry.getValue().equals(identity(entry.getKey())))throw new IOException("Source changed: "+entry.getKey());
        String result="{\"status\":\"passed\",\"scope\":\"production-importer-full-stream-existing-targets\","+
            "\"entries\":"+entries.size()+",\"validated_resource_bytes\":"+expected+
            ",\"archive_bytes\":"+input.bytes+",\"fresh_writes\":0,\"targets_changed\":0}";
        Files.write(Paths.get(args[2]),Collections.singletonList(result));System.out.println(result);
    }
}
