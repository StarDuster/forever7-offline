package com.project7.localmanager;

import android.content.Context;
import java.io.*;
import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.util.*;

/** Immutable, hash-authorized named request bindings, independent of externalEvents. */
public final class RequestEventCatalog {
    public static final String ASSET = "offline/request-events.tsv";
    public static final String SHA256 = "7088dabb1a5b84609f8b23154992660d6239389be0d54316549d2dfa94d7c475";
    static final class Binding {
        final String name, digest, completion;
        final int event, type, flags, dialog, newbee, priority;
        final boolean serverIdle;
        private final String[] trigger;
        Binding(String[] f) {
            if (f.length != 24) throw new IllegalArgumentException("Request event column count");
            name=f[0];digest=f[1];event=Integer.parseInt(f[2]);type=Integer.parseInt(f[3]);
            flags=Integer.parseInt(f[4]);dialog=Integer.parseInt(f[5]);newbee=Integer.parseInt(f[6]);priority=Integer.parseInt(f[7]);completion=f[8];
            if(!f[9].equals("true")&&!f[9].equals("false"))throw new IllegalArgumentException("Invalid idle policy");
            serverIdle=Boolean.parseBoolean(f[9]);
            trigger=Arrays.copyOfRange(f,10,24);
            if (!name.matches("request[A-Za-z0-9]+") || !digest.equals(hex(hash("MD5",name.getBytes(StandardCharsets.UTF_8)))) ||
                    event<=0 || type<=0 || (flags & 128)!=0 || !trigger[0].equals("@trigger") || !trigger[1].equals(Integer.toString(event)) ||
                    !(completion.equals("immediate") || completion.equals("start")))
                throw new IllegalArgumentException("Invalid request binding");
        }
        String[] triggerColumns(){return trigger.clone();}
    }
    private final Map<String,Binding> names;
    private RequestEventCatalog(byte[] bytes) {
        if (!SHA256.equals(hex(hash("SHA-256",bytes)))) throw new IllegalArgumentException("Request event catalog hash");
        Map<String,Binding> map=new LinkedHashMap<>();
        for(String line:new String(bytes,StandardCharsets.US_ASCII).split("\n")) {
            if(line.isEmpty() || line.startsWith("#"))continue;
            Binding b=new Binding(line.split("\t",-1));
            if(map.put(b.name,b)!=null)throw new IllegalArgumentException("Duplicate request event");
        }
        if(map.isEmpty())throw new IllegalArgumentException("Empty request catalog");
        names=Collections.unmodifiableMap(map);
    }
    public static RequestEventCatalog prepare(Context context)throws IOException {
        try(InputStream in=context.getAssets().open(ASSET)){return fromBytes(read(in));}
    }
    public static RequestEventCatalog fromBytes(byte[] bytes){return new RequestEventCatalog(bytes.clone());}
    Binding find(String name,byte[] digest) {
        Binding b=names.get(name);
        return b!=null && digest!=null && b.digest.equals(hex(digest))?b:null;
    }
    String requestForDigest(byte[] digest){if(digest==null)return null;String hex=hex(digest);for(Binding b:names.values())if(b.digest.equals(hex))return b.name;return null;}
    public Set<String> requests(){return names.keySet();}
    private static byte[] read(InputStream in)throws IOException {
        ByteArrayOutputStream out=new ByteArrayOutputStream();byte[] block=new byte[4096];int n;
        while((n=in.read(block))!=-1){if(out.size()+n>65536)throw new IOException("Request catalog bound");out.write(block,0,n);}return out.toByteArray();
    }
    static byte[] hash(String algorithm,byte[] bytes){try{return MessageDigest.getInstance(algorithm).digest(bytes);}catch(Exception e){throw new IllegalStateException(e);}}
    static String hex(byte[] bytes){StringBuilder s=new StringBuilder();for(byte b:bytes)s.append(String.format(Locale.ROOT,"%02x",b&255));return s.toString();}
}
