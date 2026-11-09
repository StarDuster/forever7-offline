package com.project7.localmanager;
import java.io.*;
import java.nio.*;
import java.nio.charset.*;
import java.util.*;

/** Strict read-only BSON view; mutations remain exclusively in original P7 engines. */
final class DrawPolicyBson {
    static final int MAX=64*1024*1024;
    static final class Value {
        final int type; final byte[] bytes; final LinkedHashMap<String,Value> fields;
        Value(int t,byte[] b,LinkedHashMap<String,Value> f){type=t;bytes=b;fields=f;}
        Value get(String k){return fields==null?null:fields.get(k);}
        Collection<Value> values() throws IOException {need(fields!=null,"EXPECTED_CONTAINER");return fields.values();}
        Integer stockInteger()throws IOException {if(type==16)return le(bytes,0);if(type==18){long n=ByteBuffer.wrap(bytes).order(ByteOrder.LITTLE_ENDIAN).getLong();if(n>=Integer.MIN_VALUE&&n<=Integer.MAX_VALUE)return (int)n;}return null;}
        int integer()throws IOException {Integer n=stockInteger();need(n!=null,"EXPECTED_STOCK_INTEGER");return n;}
        double decimal()throws IOException {need(type==1,"EXPECTED_DOUBLE");double d=ByteBuffer.wrap(bytes).order(ByteOrder.LITTLE_ENDIAN).getDouble();need(!Double.isNaN(d)&&!Double.isInfinite(d),"NONFINITE_DOUBLE");return d;}
        boolean bool()throws IOException {need(type==8,"EXPECTED_BOOL");return bytes[0]!=0;}
        String string()throws IOException {need(type==2,"EXPECTED_STRING");return utf(bytes,4,bytes.length-5);}
        String uuid(boolean legacyString)throws IOException {
            if(type==7 && bytes.length==12){char[] s=new char[24];char[] hex="0123456789abcdef".toCharArray();for(int i=0;i<12;i++){s[i*2]=hex[(bytes[i]&255)>>>4];s[i*2+1]=hex[bytes[i]&15];}return new String(s);}
            if(legacyString&&type==2){String s=string();need(s.matches("[0-9a-f]{24}"),"BAD_LEGACY_UUID");return s;}
            throw new IOException("EXPECTED_OBJECTID");
        }
    }
    static void need(boolean ok,String reason)throws IOException{if(!ok)throw new IOException("Draw policy: "+reason);}
    static int le(byte[] b,int p)throws IOException{need(p>=0&&p+4<=b.length,"TRUNCATED_BSON");return (b[p]&255)|((b[p+1]&255)<<8)|((b[p+2]&255)<<16)|(b[p+3]<<24);}
    static String utf(byte[] b,int start,int n)throws IOException{
        try{return StandardCharsets.UTF_8.newDecoder().onMalformedInput(CodingErrorAction.REPORT).onUnmappableCharacter(CodingErrorAction.REPORT).decode(ByteBuffer.wrap(b,start,n)).toString();}catch(Exception e){throw new IOException("Invalid BSON UTF8",e);}
    }
    static Value parse(byte[] data)throws IOException{need(data!=null&&data.length<=MAX,"BSON_LIMIT");return document(data,0,3);}
    private static int zero(byte[] b,int p)throws IOException{int start=p;while(p<b.length&&b[p]!=0)p++;need(p<b.length&&p-start<=MAX,"UNTERMINATED_CSTRING");return p;}
    private static int stringEnd(byte[] b,int p)throws IOException{int n=le(b,p);need(n>0&&(long)p+4+n<=b.length&&b[p+3+n]==0,"BAD_STRING_LENGTH");return p+4+n;}
    private static Value document(byte[] b,int depth,int type)throws IOException{
        need(depth<=64&&b.length>=5&&le(b,0)==b.length&&b[b.length-1]==0,"BAD_BSON_DOCUMENT");
        LinkedHashMap<String,Value> fields=new LinkedHashMap<>();int p=4;
        while(p<b.length-1){int t=b[p++]&255;int end=zero(b,p);String name=utf(b,p,end-p);p=end+1;int start=p;Value child=null;
            switch(t){
            case 1:case 9:case 17:case 18:p+=8;break;
            case 2:case 13:case 14:p=stringEnd(b,p);break;
            case 3:case 4:int n=le(b,p);need(n>=5&&(long)p+n<=b.length-1,"BAD_NESTED_BSON");p+=n;child=document(Arrays.copyOfRange(b,start,p),depth+1,t);break;
            case 5:int size=le(b,p);need(size>=0&&(long)p+5+size<=b.length-1,"BAD_BINARY_LENGTH");p+=5+size;break;
            case 7:p+=12;break;
            case 8:need(p<b.length&&(b[p]==0||b[p]==1),"BAD_BOOL");p++;break;
            case 6:case 10:case 127:case 255:break;
            case 11:p=zero(b,p)+1;p=zero(b,p)+1;break;
            case 12:p=stringEnd(b,p)+12;break;
            case 15:int total=le(b,p);need(total>=14&&(long)p+total<=b.length-1,"BAD_CODE_SCOPE");p+=total;break;
            case 16:p+=4;break;case 19:p+=16;break;
            default:throw new IOException("Unsupported BSON type "+t);
            }
            need(p<=b.length-1&&fields.size()<1000000&&!fields.containsKey(name),"DUPLICATE_OR_TRUNCATED_BSON");
            fields.put(name,child==null?new Value(t,Arrays.copyOfRange(b,start,p),null):child);
        }
        need(p==b.length-1,"BAD_DOCUMENT_END");
        if(type==4){int i=0;for(String key:fields.keySet())need(key.equals(Integer.toString(i++)),"NONCANONICAL_ARRAY_KEYS");}
        return new Value(type,b,fields);
    }
    static Value required(Value v,String k)throws IOException{Value r=v.get(k);need(r!=null,"MISSING_FIELD_"+k);return r;}
    static int integer(Value v,String k)throws IOException{return required(v,k).integer();}
    static List<Integer> ints(Value array)throws IOException{List<Integer> r=new ArrayList<>();for(Value v:array.values())r.add(v.integer());return r;}
    static boolean equal(Value a,Value b){return a!=null&&b!=null&&a.type==b.type&&Arrays.equals(a.bytes,b.bytes);}
}
