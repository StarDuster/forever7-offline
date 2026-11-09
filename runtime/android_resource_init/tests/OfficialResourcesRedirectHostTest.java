import com.forever7.offline.OfficialResources;
import com.forever7.offline.ResourceImporter;
import java.io.*;
import java.net.*;
import java.nio.file.*;
import java.security.MessageDigest;
import java.util.*;
import java.util.concurrent.atomic.AtomicBoolean;

/** Scripted URL connections only: invokes real production prepare/raw/download/commit. */
public final class OfficialResourcesRedirectHostTest {
    static final String PATH="patch2.android.640/0/raw.data";
    static final String OFFICIAL="https://g58.gph.netease.com/"+PATH;
    static final String MIRROR="https://huggingface.co/datasets/offline/resolve/main/";
    static final String HUB=MIRROR+PATH;
    static final byte[] DATA={9,2,3};
    static final Map<String,Response> responses=new HashMap<String,Response>();
    static final List<Connection> connections=new ArrayList<Connection>();
    static int scenarios;
    static void require(boolean condition,String message){if(!condition)throw new AssertionError(message);}
    static String hash(byte[] bytes,String algorithm)throws Exception {
        StringBuilder result=new StringBuilder();for(byte b:MessageDigest.getInstance(algorithm).digest(bytes))result.append(String.format(Locale.US,"%02x",b&255));return result.toString();
    }
    static final class Response {
        final int status;final String location;final byte[] data;
        Runnable onStatus;boolean streamFailure,originCredential,statusFailure;
        Response(int status,String location,byte[] data){this.status=status;this.location=location;this.data=data;}
    }
    static final class Connection extends HttpURLConnection {
        final Response response;final Map<String,String> headers=new HashMap<String,String>();
        boolean disconnected,inputClosed;
        Connection(URL url,Response response){super(url);this.response=response;}
        public void connect(){}
        public boolean usingProxy(){return false;}
        public void disconnect(){disconnected=true;}
        public void setRequestProperty(String name,String value){headers.put(name,value);}
        public String getRequestProperty(String name){return headers.get(name);}
        public Map<String,List<String>> getRequestProperties(){Map<String,List<String>> result=new HashMap<String,List<String>>();for(Map.Entry<String,String> entry:headers.entrySet())result.put(entry.getKey(),Arrays.asList(entry.getValue()));return result;}
        public int getResponseCode()throws IOException {
            if(response.statusFailure)throw new IOException("scripted status failure");
            if(response.onStatus!=null)response.onStatus.run();
            if(response.originCredential){headers.put("Authorization","fake-origin-only");headers.put("Cookie","fake-origin-cookie");headers.put("Proxy-Authorization","fake-origin-proxy");}
            return response.status;
        }
        public String getHeaderField(String name){return name.equalsIgnoreCase("Location")?response.location:null;}
        public InputStream getInputStream()throws IOException {
            if(response.streamFailure)throw new IOException("scripted input failure");
            return new ByteArrayInputStream(response.data){public void close()throws IOException{super.close();inputClosed=true;}};
        }
    }
    static void setup(){responses.clear();connections.clear();responses.put(OFFICIAL,new Response(503,null,new byte[0]));}
    static void allDisconnected(){
        for(Connection c:connections){
            require(c.disconnected,"Connection leaked: "+c.getURL());
            require(c.getConnectTimeout()==15000 && c.getReadTimeout()==15000,"Timeout configuration lost");
            require(!c.getInstanceFollowRedirects(),"Implicit platform redirects enabled");
            require("identity".equals(c.headers.get("Accept-Encoding")),"Payload encoding not pinned");
            if(!c.response.originCredential)require(!c.headers.containsKey("Authorization") && !c.headers.containsKey("Cookie") && !c.headers.containsKey("Proxy-Authorization"),"Credentials forwarded to "+c.getURL());
        }
    }
    static final class Fixture implements AutoCloseable {
        final Path root,cache,res;final AtomicBoolean cancelled=new AtomicBoolean(false);
        final ResourceImporter.Entry output;
        final ResourceImporter importer;
        final OfficialResources resources;final boolean badSourceSha;
        Fixture()throws Exception {this(false);}
        Fixture(boolean badSourceSha)throws Exception {
            this.badSourceSha=badSourceSha;
            root=Files.createTempDirectory("f7-redirect-host-");cache=root.resolve("cache");res=root.resolve("res");
            output=new ResourceImporter.Entry("sound/output/object.fsb",2,hash(new byte[]{2,3},"SHA-256"));
            importer=new ResourceImporter(res.toFile(),Arrays.asList(output),new ResourceImporter.Cache(){public boolean verified(ResourceImporter.Entry e,File f){return false;}public void remember(ResourceImporter.Entry e,File f){}},cancelled,(n,b,t)->{});
            resources=new OfficialResources(importer,cache.toFile(),MIRROR);
        }
        void prepare()throws Exception {
            OfficialResources.Part part=new OfficialResources.Part();part.name="raw";
            part.payloads.add(new OfficialResources.Payload(PATH,3,hash(DATA,"MD5"),badSourceSha?String.join("",Collections.nCopies(64,"0")):hash(DATA,"SHA-256")));
            OfficialResources.Raw row=new OfficialResources.Raw();row.entry=output;row.offset=1;row.version=0;
            resources.prepare(Arrays.asList(part),Collections.emptyMap(),Arrays.asList(row));
        }
        void assertSuccess()throws Exception {
            require(Arrays.equals(Files.readAllBytes(res.resolve(output.name)),new byte[]{2,3}),"Original raw slice bytes changed");
            require(hash(Files.readAllBytes(res.resolve(output.name)),"SHA-256").equals(output.sha256),"Independent final SHA mismatch");
            require(Arrays.equals(Files.readAllBytes(cache.resolve(PATH)),DATA),"Source cache committed unverified bytes");
            require(!Files.exists(cache.resolve(PATH+".part")) && !Files.exists(res.resolve(output.name+".f7-build.part")),"Temporary file leaked");
        }
        void assertFailed()throws Exception {
            require(!Files.exists(res.resolve(output.name)),"Failed transfer committed final output");
            require(!Files.exists(cache.resolve(PATH)),"Failed transfer committed source cache");
            require(!Files.exists(cache.resolve(PATH+".part")) && !Files.exists(res.resolve(output.name+".f7-build.part")),"Failed transfer leaked temporary file");
        }
        public void close()throws Exception {
            importer.close();
            try(java.util.stream.Stream<Path> files=Files.walk(root)){for(Path file:(Iterable<Path>)files.sorted(Comparator.reverseOrder())::iterator)Files.delete(file);}
        }
    }
    static void successfulAllCodes()throws Exception {
        setup();String relative="next?stage=1";String second=new URL(new URL(HUB),relative).toExternalForm();
        String third="https://huggingface.co/datasets/offline/resolve/main/stage2?download=true";
        String fourth="https://cdn-lfs.hf.co/blob?X-Amz-Signature=ab%2Bcd&Expires=123";
        String fifth="https://cas-bridge.xethub.hf.co/xet?Policy=a%2Fb&Signature=b%3D";
        String last="https://signed.cdn.invalid/object?Signature=c%2Bd&Key-Pair-Id=key";
        Response hub=new Response(301,relative,null);hub.originCredential=true;responses.put(HUB,hub);
        responses.put(second,new Response(302,"/datasets/offline/resolve/main/stage2?download=true",null));
        responses.put(third,new Response(303,fourth,null));responses.put(fourth,new Response(307,fifth,null));
        responses.put(fifth,new Response(308,last,null));responses.put(last,new Response(200,null,DATA));
        try(Fixture f=new Fixture()){f.prepare();f.assertSuccess();}
        require(connections.size()==7 && connections.get(0).getURL().toExternalForm().equals(OFFICIAL),"Official-first fallback order lost");
        require(connections.get(6).getURL().toExternalForm().equals(last),"Signed CDN query rewritten");
        require(connections.get(6).inputClosed,"Successful response stream leaked");allDisconnected();scenarios++;
    }
    static void officialSuccessNoFallback()throws Exception {
        setup();responses.put(OFFICIAL,new Response(200,null,DATA));
        try(Fixture f=new Fixture()){f.prepare();f.assertSuccess();}
        require(connections.size()==1,"Mirror contacted despite verified official transfer");allDisconnected();scenarios++;
    }
    static void rejected(String name,String location,String expected)throws Exception {
        setup();responses.put(HUB,new Response(302,location,null));
        try(Fixture f=new Fixture()) {
            try{f.prepare();throw new AssertionError(name+" accepted");}catch(IOException error){require(error.getMessage().contains(expected),name+": "+error);}
            f.assertFailed();
        }
        require(connections.size()==2,name+" opened forbidden redirect target");allDisconnected();scenarios++;
    }
    static void hopLimit(boolean success)throws Exception {
        setup();String url=HUB;
        for(int i=0;i<9;i++) {
            String next="https://cdn.invalid/hop"+(i+1)+"?signed="+i;
            responses.put(url,i==8 && success?new Response(200,null,DATA):new Response(302,next,null));url=next;
        }
        try(Fixture f=new Fixture()) {
            if(success){f.prepare();f.assertSuccess();}
            else{try{f.prepare();throw new AssertionError("Ninth redirect accepted");}catch(IOException e){require(e.getMessage().contains("Too many"),e.toString());}f.assertFailed();}
        }
        require(connections.size()==10,"Hop bound differs from eight redirects");allDisconnected();scenarios++;
    }
    static void transferFailure(String name,byte[] bytes,boolean stream)throws Exception {
        setup();Response response=new Response(200,null,bytes);response.streamFailure=stream;responses.put(HUB,response);
        try(Fixture f=new Fixture()) {
            try{f.prepare();throw new AssertionError(name+" accepted");}catch(IOException e){require(e.getMessage().contains(stream?"scripted input failure":bytes.length>3?"Oversized":"digest mismatch"),e.toString());}
            f.assertFailed();
        }
        allDisconnected();scenarios++;
    }
    static void shaOnlyMismatch()throws Exception {
        setup();responses.put(HUB,new Response(200,null,DATA));
        try(Fixture f=new Fixture(true)) {
            try{f.prepare();throw new AssertionError("SHA mismatch accepted despite correct MD5");}catch(IOException e){require(e.getMessage().contains("digest mismatch"),e.toString());}
            f.assertFailed();
        }
        allDisconnected();scenarios++;
    }
    static void responseCodeFailure()throws Exception {
        setup();Response response=new Response(200,null,DATA);response.statusFailure=true;responses.put(HUB,response);
        try(Fixture f=new Fixture()) {
            try{f.prepare();throw new AssertionError("Status I/O failure accepted");}catch(IOException e){require(e.getMessage().contains("scripted status failure"),e.toString());}
            f.assertFailed();
        }
        allDisconnected();scenarios++;
    }
    static void cancellationBetweenRedirects()throws Exception {
        setup();
        try(Fixture f=new Fixture()) {
            Response redirect=new Response(307,"https://signed.cdn.invalid/not-opened?Signature=secret",null);
            redirect.onStatus=()->f.cancelled.set(true);responses.put(HUB,redirect);
            try{f.prepare();throw new AssertionError("Redirect cancellation ignored");}catch(ResourceImporter.Cancelled expected){}
            f.assertFailed();
        }
        require(connections.size()==2,"Cancelled redirect opened another host");allDisconnected();scenarios++;
    }
    public static void main(String[] args)throws Exception {
        // This factory handles EVERY protocol. Any unscripted URL fails before
        // a real socket, DNS lookup, TLS connection or HTTP request can exist.
        URL.setURLStreamHandlerFactory(protocol->new URLStreamHandler(){protected URLConnection openConnection(URL url)throws IOException{
            Response response=responses.get(url.toExternalForm());if(response==null)throw new AssertionError("Unscripted URL blocked: "+url);
            Connection connection=new Connection(url,response);connections.add(connection);return connection;
        }});
        officialSuccessNoFallback();successfulAllCodes();
        rejected("missing Location",null,"Missing");rejected("blank Location","  ","Missing");
        rejected("loop",HUB,"loop");rejected("HTTP downgrade","http://cdn.invalid/a","HTTPS");
        rejected("userinfo","https://user:pass@cdn.invalid/a","HTTPS");rejected("fragment","https://cdn.invalid/a#fragment","HTTPS");
        hopLimit(true);hopLimit(false);
        transferFailure("wrong digest",new byte[]{9,8,7},false);transferFailure("oversized",new byte[]{9,2,3,4},false);
        transferFailure("stream failure",DATA,true);shaOnlyMismatch();responseCodeFailure();cancellationBetweenRedirects();
        System.out.println(scenarios+" real production redirect/fallback/hash/cancellation contracts passed; network=mock-only");
    }
}
