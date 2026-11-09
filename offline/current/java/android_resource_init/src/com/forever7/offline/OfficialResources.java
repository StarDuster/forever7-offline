package com.forever7.offline;

import java.io.*;
import java.net.*;
import java.security.*;
import java.util.*;
import java.util.zip.InflaterInputStream;

/** Fixed-version, pinned source reconstruction. Caller owns ResourceImporter's session lock. */
public final class OfficialResources {
    public static final class Payload {
        public final String path, md5, sha256; public final long size;
        public Payload(String path, long size, String md5, String sha256) {
            if (!path.matches("patch2\\.android\\.640/(?:[0-9]+/)?[a-zA-Z0-9_]+\\.(?:check|data)") || size < 0 || !md5.matches("[a-f0-9]{32}")) throw new IllegalArgumentException("Invalid pinned payload");
            this.path=path; this.size=size; this.md5=md5; this.sha256=sha256;
        }
    }
    public static final class Part {
        public String name; public Payload check; public List<Payload> payloads = new ArrayList<Payload>();
    }
    public static final class Raw {
        public ResourceImporter.Entry entry; public long offset; public int version;
    }
    private final ResourceImporter session; private final File cache; private final String mirror;
    public OfficialResources(ResourceImporter session, File cache, String mirror) throws IOException {
        this.session=session; this.cache=cache.getCanonicalFile(); this.mirror=mirror;
        if (!cache.isDirectory() && !cache.mkdirs()) throw new IOException("Cannot create source cache");
        if (mirror != null && !mirror.startsWith("https://")) throw new IOException("Mirror must use HTTPS");
    }
    private MessageDigest digest(String algorithm) throws IOException { try { return MessageDigest.getInstance(algorithm); } catch (NoSuchAlgorithmException e) { throw new IOException(e); } }
    private boolean valid(File file, long size, String expected, String algorithm) throws IOException {
        if (!file.isFile() || file.length()!=size) return false;
        MessageDigest hash=digest(algorithm); byte[] b=new byte[131072]; long count=0;
        try(InputStream in=new FileInputStream(file)) { int n; while((n=in.read(b))!=-1) { session.checkpoint(); count+=n; if(count>size)return false; hash.update(b,0,n); } }
        return ResourceImporter.hex(hash.digest()).equals(expected);
    }
    private HttpURLConnection openPayloadConnection(URL address) throws IOException {
        Set<String> visited=new HashSet<String>();
        for(int hops=0;hops<=8;hops++) {
            session.checkpoint();
            if(!"https".equalsIgnoreCase(address.getProtocol()) || address.getHost().isEmpty() || address.getUserInfo()!=null || address.getRef()!=null)
                throw new IOException("Resource download requires an HTTPS URL without user info or fragment");
            if(!visited.add(address.toExternalForm()))throw new IOException("Resource redirect loop");
            HttpURLConnection connection=(HttpURLConnection)address.openConnection();
            boolean retained=false;
            try {
                connection.setConnectTimeout(15000); connection.setReadTimeout(15000); connection.setInstanceFollowRedirects(false);
                connection.setRequestProperty("Accept-Encoding","identity");
                int status=connection.getResponseCode();
                if(status==200) { retained=true;return connection; }
                if(status!=301 && status!=302 && status!=303 && status!=307 && status!=308)
                    throw new IOException("CDN HTTP "+status);
                if(hops==8)throw new IOException("Too many resource redirects");
                String location=connection.getHeaderField("Location");
                if(location==null || location.trim().isEmpty())throw new IOException("Missing resource redirect location");
                // Signed CDN query parameters are expected on Hub redirects.
                // No credentials or authorization headers are forwarded.
                address=new URL(address,location);
            } finally { if(!retained)connection.disconnect(); }
        }
        throw new IOException("Too many resource redirects");
    }
    private File payload(Payload item) throws IOException {
        File file=new File(cache,item.path);
        if (!file.getCanonicalFile().equals(file.getAbsoluteFile())) throw new IOException("Cache symlink rejected");
        if(valid(file,item.size,item.md5,"MD5") && (item.sha256==null || valid(file,item.size,item.sha256,"SHA-256"))) return file;
        if(!file.getParentFile().isDirectory() && !file.getParentFile().mkdirs()) throw new IOException("Cannot create source cache parent");
        if(cache.getUsableSpace()<item.size+16777216L)throw new IOException("Insufficient source cache space");
        IOException failure=null;
        for(String base: mirror==null?new String[]{"https://g58.gph.netease.com/"}:new String[]{"https://g58.gph.netease.com/",mirror}) {
            File tmp=new File(file+".part"); HttpURLConnection connection=null;
            try {
                session.checkpoint();
                connection=openPayloadConnection(new URL(base+(base.endsWith("/")?"":"/")+item.path));
                MessageDigest md5=digest("MD5"), sha=digest("SHA-256"); long count=0;
                try(InputStream in=connection.getInputStream(); FileOutputStream out=new FileOutputStream(tmp)) {
                    byte[] b=new byte[131072]; int n; while((n=in.read(b))!=-1) { session.checkpoint(); count+=n; if(count>item.size)throw new IOException("Oversized CDN payload"); out.write(b,0,n); md5.update(b,0,n); sha.update(b,0,n); session.progress(item.path,count,item.size); } out.getFD().sync();
                }
                if(count!=item.size || !ResourceImporter.hex(md5.digest()).equals(item.md5) || (item.sha256!=null && !ResourceImporter.hex(sha.digest()).equals(item.sha256))) throw new IOException("CDN payload digest mismatch");
                session.checkpoint(); if(!tmp.renameTo(file)) throw new IOException("Cannot commit source cache"); return file;
            } catch(ResourceImporter.Cancelled e) { throw e; } catch(IOException e) { failure=e; }
            finally { if(connection!=null)connection.disconnect(); tmp.delete(); }
        }
        throw failure;
    }
    private static void le(RandomAccessFile out,long value) throws IOException { if(value<0 || value>0xffffffffL)throw new IOException("NPK integer overflow"); for(int i=0;i<4;i++)out.write((int)(value>>>(8*i))&255); }
    private void copy(RandomAccessFile in,RandomAccessFile out,long offset,long size) throws IOException {
        if(offset<0 || size<0 || offset>in.length()-size)throw new IOException("Slice exceeds source");
        in.seek(offset); byte[] b=new byte[131072]; while(size>0) { session.checkpoint(); int n=in.read(b,0,(int)Math.min(size,b.length)); if(n<0)throw new EOFException();out.write(b,0,n);size-=n; }
    }
    private void commit(File tmp,ResourceImporter.Entry entry) throws IOException {
        if(!valid(tmp,entry.bytes,entry.sha256,"SHA-256"))throw new IOException("Reconstructed resource digest mismatch: "+entry.name);
        session.checkpoint(); if(!tmp.renameTo(session.destination(entry)))throw new IOException("Cannot commit reconstructed resource");session.committed(entry);
    }
    public void prepare(List<Part> parts,Map<String,ResourceImporter.Entry> outputs,List<Raw> raw) throws IOException {
        for(Part part:parts) {
            if(part.name.equals("raw")) { prepareRaw(part,raw);continue; }
            ResourceImporter.Entry entry=outputs.get(part.name+".npk"); if(entry==null)throw new IOException("Unpinned output");
            if(session.verify(entry,false))continue;
            File destination=session.destination(entry); if(destination.getParentFile().getUsableSpace()<entry.bytes+16777216L)throw new IOException("Insufficient reconstruction space");
            List<long[]> rows=new ArrayList<long[]>();
            try(BufferedReader reader=new BufferedReader(new InputStreamReader(new InflaterInputStream(new FileInputStream(payload(part.check))),"US-ASCII"))) {
                String line; while((line=reader.readLine())!=null) {session.checkpoint(); if(line.trim().isEmpty())continue; if(rows.size()>2000000 || line.length()>1024)throw new IOException("Oversized check index"); String[] v=line.trim().split("\\s+"); if(v.length!=8)throw new IOException("Malformed check index");long[] r=new long[7];int[] ix={0,2,3,4,5,6,7};try {for(int i=0;i<7;i++)r[i]=Long.parseLong(v[ix[i]]);}catch(NumberFormatException e){throw new IOException(e);} rows.add(r); }
            }
            Collections.sort(rows,new Comparator<long[]>() {public int compare(long[] a,long[] b){return Long.compare(a[5],b[5]);}});
            Map<Long,Payload> versions=new HashMap<Long,Payload>();for(Payload p:part.payloads)versions.put(Long.parseLong(p.path.split("/")[1]),p);
            File tmp=new File(destination+".f7-build.part");
            try {
                try(RandomAccessFile out=new RandomAccessFile(tmp,"rw")) {
                    out.setLength(0);out.write(new byte[28]);List<long[]> records=new ArrayList<long[]>();Set<Long> ids=new HashSet<Long>(); long version=-1; RandomAccessFile source=null;
                    try {for(long[] r:rows) { if(!ids.add(r[0]))throw new IOException("Duplicate NPK ID");if(r[5]!=version) {if(source!=null)source.close();Payload p=versions.get(r[5]);if(p==null)throw new IOException("Missing pinned payload");source=new RandomAccessFile(payload(p),"r");version=r[5];} long position=out.getFilePointer();copy(source,out,r[6],r[1]);while(out.getFilePointer()%4!=0)out.write(0);records.add(new long[]{r[0],position,r[1],r[3],r[2],r[4],r[1]==r[3]&&r[2]==r[4]?0:2});}}finally{if(source!=null)source.close();}
                    long table=out.getFilePointer();Collections.sort(records,new Comparator<long[]>() {public int compare(long[] a,long[] b){return Long.compare(a[0],b[0]);}});for(long[] r:records)for(long v:r)le(out,v);out.seek(0);out.writeBytes("NXPK");le(out,records.size());le(out,0);le(out,0);le(out,2);le(out,table);le(out,0);out.getFD().sync();
                } commit(tmp,entry);
            }finally{tmp.delete();}
        }
    }
    private void prepareRaw(Part part,List<Raw> rows) throws IOException {
        Map<Integer,Payload> versions=new HashMap<Integer,Payload>();for(Payload p:part.payloads)versions.put(Integer.parseInt(p.path.split("/")[1]),p);
        for(Raw row:rows) { if(session.verify(row.entry,false))continue; File dest=session.destination(row.entry);if(dest.getParentFile().getUsableSpace()<row.entry.bytes+16777216L)throw new IOException("Insufficient raw output space");Payload p=versions.get(row.version);if(p==null)throw new IOException("Missing raw payload");File tmp=new File(dest+".f7-build.part");try {try(RandomAccessFile in=new RandomAccessFile(payload(p),"r");RandomAccessFile out=new RandomAccessFile(tmp,"rw")){out.setLength(0);copy(in,out,row.offset,row.entry.bytes);out.getFD().sync();}commit(tmp,row.entry);}finally{tmp.delete();} }
    }
}
