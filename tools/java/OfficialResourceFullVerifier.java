import com.forever7.offline.OfficialResources;
import com.forever7.offline.ResourceImporter;
import java.io.*;
import java.net.*;
import java.nio.file.*;
import java.security.MessageDigest;
import java.util.*;
import java.util.concurrent.atomic.AtomicBoolean;

/** Host harness only. Reconstruction is performed exclusively by production classes. */
public final class OfficialResourceFullVerifier {
    private static int networkAttempts;
    private static String quote(String value) { return "\""+value.replace("\\","\\\\").replace("\"","\\\"").replace("\n","\\n").replace("\r","\\r")+"\""; }
    private static String sha(Path path) throws Exception {
        MessageDigest hash=MessageDigest.getInstance("SHA-256");
        try(InputStream input=Files.newInputStream(path)) { byte[] data=new byte[1048576];int count;while((count=input.read(data))!=-1)hash.update(data,0,count); }
        StringBuilder result=new StringBuilder();for(byte b:hash.digest())result.append(String.format(Locale.ROOT,"%02x",b&255));return result.toString();
    }
    public static void main(String[] args) throws Exception {
        if(args.length!=4)throw new IllegalArgumentException("plan.tsv cache scratch results.jsonl");
        URL.setURLStreamHandlerFactory(protocol -> new URLStreamHandler() {
            protected URLConnection openConnection(URL url) throws IOException { networkAttempts++;throw new IOException("HOST VERIFIER NETWORK DENIED: "+url); }
        });
        try { new URL("https://offline-verifier.invalid/probe").openConnection();throw new AssertionError("Network denial missing"); } catch(IOException expected) { }
        int probeAttempts=networkAttempts;networkAttempts=0;
        Path scratch=Paths.get(args[2]).toRealPath();
        if(!Files.isRegularFile(scratch.resolve(".official-java-verifier-owned")))throw new IOException("Missing exclusive scratch ownership marker");
        Map<String,OfficialResources.Part> parts=new HashMap<>();
        List<String[]> outputs=new ArrayList<>();
        for(String line:Files.readAllLines(Paths.get(args[0]),java.nio.charset.StandardCharsets.UTF_8)) {
            String[] v=line.split("\t",-1);
            if(v[0].equals("C") || v[0].equals("D")) {
                OfficialResources.Part part=parts.get(v[1]);if(part==null){part=new OfficialResources.Part();part.name=v[1];parts.put(v[1],part);}
                OfficialResources.Payload payload=new OfficialResources.Payload(v[2],Long.parseLong(v[3]),v[4],v[5].equals("-")?null:v[5]);
                if(v[0].equals("C"))part.check=payload;else part.payloads.add(payload);
            } else if(v[0].equals("N") || v[0].equals("R")) outputs.add(v);
            else throw new IOException("Unknown verifier plan row");
        }
        int failures=0;long total=0;
        try(PrintWriter log=new PrintWriter(new BufferedWriter(new FileWriter(args[3],true)))) {
            for(String[] v:outputs) {
                long started=System.nanoTime(),bytes=0;String actual="",error=null;
                ResourceImporter.Entry entry=new ResourceImporter.Entry(v[1],Long.parseLong(v[2]),v[3]);
                Path destination=scratch.resolve("res").resolve(entry.name);
                if(!destination.normalize().startsWith(scratch.resolve("res")))throw new IOException("Unsafe verifier destination");
                try {
                    if(Files.exists(destination))throw new IOException("Output preexists; reconstruction must start empty");
                    ResourceImporter.Cache neverTrust=new ResourceImporter.Cache(){public boolean verified(ResourceImporter.Entry e,File f){return false;}public void remember(ResourceImporter.Entry e,File f){}};
                    try(ResourceImporter importer=new ResourceImporter(scratch.resolve("res").toFile(),Arrays.asList(entry),neverTrust,new AtomicBoolean(false),(name,done,size)->{})) {
                        OfficialResources resources=new OfficialResources(importer,new File(args[1]),null);
                        if(v[0].equals("N")) {
                            Map<String,ResourceImporter.Entry> pinned=new HashMap<>();pinned.put(entry.name,entry);
                            resources.prepare(Arrays.asList(parts.get(v[4])),pinned,Collections.emptyList());
                        } else {
                            OfficialResources.Raw raw=new OfficialResources.Raw();raw.entry=entry;raw.version=Integer.parseInt(v[4]);raw.offset=Long.parseLong(v[5]);
                            resources.prepare(Arrays.asList(parts.get("raw")),Collections.emptyMap(),Arrays.asList(raw));
                        }
                    }
                    // Independent read, not ResourceImporter.verify or its verification cache.
                    bytes=Files.size(destination);actual=sha(destination);
                    if(bytes!=entry.bytes || !actual.equals(entry.sha256))throw new IOException("Independent final output mismatch");
                    total+=bytes;
                } catch(Exception failure) { failures++;error=failure.toString(); }
                finally { Files.deleteIfExists(destination); }
                log.println("{\"name\":"+quote(entry.name)+",\"kind\":"+quote(v[0].equals("N")?"npk":"raw")+",\"expected_bytes\":"+entry.bytes+",\"actual_bytes\":"+bytes+",\"expected_sha256\":"+quote(entry.sha256)+",\"actual_sha256\":"+quote(actual)+",\"ok\":"+(error==null)+",\"deleted\":"+(!Files.exists(destination))+",\"seconds\":"+((System.nanoTime()-started)/1e9)+",\"error\":"+(error==null?"null":quote(error))+"}");log.flush();
                System.out.println("verified="+(error==null)+" output="+entry.name+" bytes="+bytes);System.out.flush();
            }
            log.println("{\"summary\":true,\"outputs\":"+outputs.size()+",\"verified_bytes\":"+total+",\"failures\":"+failures+",\"network_denial_probe_attempts\":"+probeAttempts+",\"network_attempts_during_reconstruction\":"+networkAttempts+"}");
        }
        if(failures!=0 || networkAttempts!=0)System.exit(1);
    }
}
