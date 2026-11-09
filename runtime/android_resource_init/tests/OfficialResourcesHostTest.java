import com.forever7.offline.*;
import java.io.*;
import java.nio.file.*;
import java.security.*;
import java.util.*;
import java.util.concurrent.atomic.AtomicBoolean;
import java.util.zip.DeflaterOutputStream;
public class OfficialResourcesHostTest {
 static String hash(byte[] b,String algorithm)throws Exception{StringBuilder s=new StringBuilder();for(byte v:MessageDigest.getInstance(algorithm).digest(b))s.append(String.format("%02x",v&255));return s.toString();}
 static OfficialResources.Payload cached(Path cache,String path,byte[] data,boolean check)throws Exception{Path file=cache.resolve(path);Files.createDirectories(file.getParent());Files.write(file,data);return new OfficialResources.Payload(path,data.length,hash(data,"MD5"),check?hash(data,"SHA-256"):null);}
 static void le(ByteArrayOutputStream out,int v){for(int i=0;i<4;i++)out.write(v>>>(8*i)&255);}
 public static void main(String[] args)throws Exception{
  Path root=Files.createTempDirectory("f7-official-test").resolve("Documents");Files.createDirectories(root);Path cache=root.resolve("cache");Files.createDirectories(cache);
  byte[] packed={1,2,3};ByteArrayOutputStream expected=new ByteArrayOutputStream();expected.write("NXPK".getBytes("US-ASCII"));for(int n:new int[]{1,0,0,2,32,0})le(expected,n);expected.write(packed);expected.write(0);for(int n:new int[]{42,28,3,3,7,7,0})le(expected,n);
  ResourceImporter.Entry npk=new ResourceImporter.Entry("hero.npk",60,hash(expected.toByteArray(),"SHA-256"));
  ResourceImporter.Entry raw=new ResourceImporter.Entry("sound/output/object.fsb",2,hash(new byte[]{2,3},"SHA-256"));
  AtomicBoolean cancelled=new AtomicBoolean(false);
  ResourceImporter.Cache verification=new ResourceImporter.Cache(){public boolean verified(ResourceImporter.Entry e,File f){return false;}public void remember(ResourceImporter.Entry e,File f){}};
  try(ResourceImporter importer=new ResourceImporter(root.resolve("res").toFile(),Arrays.asList(npk,raw),verification,cancelled,(n,b,t)->{})){
   OfficialResources.Part part=new OfficialResources.Part();part.name="hero";
   ByteArrayOutputStream compressed=new ByteArrayOutputStream();try(DeflaterOutputStream z=new DeflaterOutputStream(compressed)){z.write("42 00000000000000000000000000000000 3 7 3 7 0 0\n".getBytes("US-ASCII"));}
   part.check=cached(cache,"patch2.android.640/hero.check",compressed.toByteArray(),true);part.payloads.add(cached(cache,"patch2.android.640/0/hero.data",packed,false));
   OfficialResources.Part rp=new OfficialResources.Part();rp.name="raw";rp.payloads.add(cached(cache,"patch2.android.640/0/raw.data",packed,false));
   OfficialResources.Raw rr=new OfficialResources.Raw();rr.entry=raw;rr.offset=1;rr.version=0;
   Map<String,ResourceImporter.Entry> outputs=new HashMap<>();outputs.put(npk.name,npk);
   OfficialResources resources=new OfficialResources(importer,cache.toFile(),null);resources.prepare(Arrays.asList(part,rp),outputs,Arrays.asList(rr));
   if(!Files.isRegularFile(root.resolve("res/sound/output/object.fsb")) || Files.exists(root.resolve("res/res/sound/output/object.fsb")))throw new AssertionError("Original raw.check name sound/output/object.fsb must resolve beneath Documents/res exactly once");
   if(!importer.missing(true).isEmpty())throw new AssertionError("NPK/raw reconstruction mismatch");
   // Valid outputs must bypass all missing network sources on retry.
   Files.delete(cache.resolve("patch2.android.640/hero.check"));resources.prepare(Arrays.asList(part,rp),outputs,Arrays.asList(rr));
   cancelled.set(true);try{resources.prepare(Arrays.asList(part),outputs,Arrays.asList(rr));throw new AssertionError("Cancellation ignored");}catch(ResourceImporter.Cancelled good){}
   try{new ResourceImporter.Entry("res/../save.dat",1,raw.sha256);throw new AssertionError("Traversal accepted");}catch(IllegalArgumentException good){}
  }
  System.out.println("4 official cache/reconstruction/retry/cancellation contracts passed");
 }
}
