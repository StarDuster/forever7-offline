package com.project7.localmanager;
import java.nio.file.*;
import java.io.*;
import java.util.*;
/** Deterministic exact interval tests over actual fixed public source; not grant proof. */
public final class HistoryFurnitureCatalogHost {
    static int checks;
    static void check(boolean ok,String why){if(!ok)throw new AssertionError(why);checks++;}
    static Random point(int value){return new Random(){public int nextInt(int bound){if(value>=bound)throw new AssertionError("bad bound");return value;}};}
    public static void main(String[] args)throws Exception{
        byte[] data=Files.readAllBytes(Paths.get(args[0]));HistoryFurniturePolicy.prepareStream(new ByteArrayInputStream(data));int pools=0;
        for(String line:new String(data,"US-ASCII").split("\n")){
            if(!line.startsWith("F\t"))continue;String[] cells=line.split("\t");int t=Integer.parseInt(cells[1]);HistoryBson.Value spec=HistoryBson.parse(Base64.getDecoder().decode(cells[2]));check(spec.get("enabled").bool()&&HistoryFurniturePolicy.acceptsPool(t),"all real historical source pools enabled");pools++;
            int outer=0;for(HistoryBson.Value row:spec.get("base").values()){
                int weight=HistoryBson.integer(row,"w");check(Arrays.equals(HistoryFurniturePolicy.chooseOuter(Collections.emptyList(),point(outer),t),row.bytes)&&Arrays.equals(HistoryFurniturePolicy.chooseOuter(Collections.emptyList(),point(outer+weight-1),t),row.bytes),"outer interval endpoints");outer+=weight;
                List<byte[]> options=new ArrayList<>();for(HistoryBson.Value option:row.get("options").values())options.add(option.bytes);
                int inner=0;for(HistoryBson.Value option:row.get("options").values()){int w=HistoryBson.integer(option,"w");check(Arrays.equals(HistoryFurniturePolicy.chooseInner(options,point(inner),t),option.bytes)&&Arrays.equals(HistoryFurniturePolicy.chooseInner(options,point(inner+w-1),t),option.bytes),"inner interval endpoints");inner+=w;}
            }
            for(Map.Entry<String,HistoryBson.Value> defaultRow:spec.get("defaults").fields.entrySet())check(Arrays.equals(HistoryFurniturePolicy.defaultRow(null,"G",Integer.parseInt(defaultRow.getKey()),t),defaultRow.getValue().bytes),"per-t exact default RR row");
        }
        check(pools==40&&HistoryFurniturePolicy.acceptsPool(162)&&!HistoryFurniturePolicy.acceptsPool(1)&&!HistoryFurniturePolicy.acceptsPool(354)&&!HistoryFurniturePolicy.acceptsPool(484),"family scope and old162 admission");
        byte[] tampered=data.clone();tampered[0]^=1;boolean failed=false;try{HistoryFurniturePolicy.prepareStream(new ByteArrayInputStream(tampered));}catch(IOException expected){failed=true;}check(failed&&HistoryFurniturePolicy.acceptsPool(106),"SHA tamper rejects new snapshot, valid snapshot preserved");
        Thread.currentThread().interrupt();failed=false;try{HistoryFurniturePolicy.prepareStream(new ByteArrayInputStream(data));}catch(IOException expected){failed=true;}finally{Thread.interrupted();}check(failed&&HistoryFurniturePolicy.acceptsPool(106),"cancel does not publish replacement");
        System.out.println("HISTORY_FURNITURE_EXACT_INTERVAL_PASS checks="+checks+" pools="+pools+"; no sampling/grant/renderer claim");
    }
}
