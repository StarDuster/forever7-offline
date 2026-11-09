package com.project7.localmanager;
import java.io.*;
import java.nio.*;
import java.nio.file.*;
import java.util.*;
import static com.project7.localmanager.CollectionBson.*;

/** Synthetic host engine for transaction fault testing. NOT the original P7 engine. */
public final class CollectionHostTest {
    static void check(boolean v,String s){if(!v)throw new AssertionError(s);}
    static Value i(int n){return new Value(16,ByteBuffer.allocate(4).order(ByteOrder.LITTLE_ENDIAN).putInt(n).array(),null);}
    static Value d(double n){return new Value(1,ByteBuffer.allocate(8).order(ByteOrder.LITTLE_ENDIAN).putDouble(n).array(),null);}
    static Value bool(boolean b){return new Value(8,new byte[]{(byte)(b?1:0)},null);}
    static Value str(String s)throws Exception{byte[] b=s.getBytes("UTF-8");ByteBuffer out=ByteBuffer.allocate(b.length+5).order(ByteOrder.LITTLE_ENDIAN);out.putInt(b.length+1);out.put(b);out.put((byte)0);return new Value(2,out.array(),null);}
    static Value oid(String s){byte[] b=new byte[12];for(int n=0;n<12;n++)b[n]=(byte)Integer.parseInt(s.substring(n*2,n*2+2),16);return new Value(7,b,null);}
    static Value doc(Object... pairs)throws Exception{LinkedHashMap<String,Value> m=new LinkedHashMap<>();for(int n=0;n<pairs.length;n+=2)m.put((String)pairs[n],(Value)pairs[n+1]);return container(3,m);}
    static Value arr(Collection<Value> values)throws Exception{LinkedHashMap<String,Value>m=new LinkedHashMap<>();int n=0;for(Value v:values)m.put(Integer.toString(n++),v);return container(4,m);}
    static Value container(int type,Map<String,Value> m)throws Exception{ByteArrayOutputStream out=new ByteArrayOutputStream();for(Map.Entry<String,Value> e:m.entrySet()){out.write(e.getValue().type);out.write(e.getKey().getBytes("UTF-8"));out.write(0);out.write(e.getValue().bytes);}out.write(0);byte[] body=out.toByteArray();ByteBuffer b=ByteBuffer.allocate(body.length+4).order(ByteOrder.LITTLE_ENDIAN);b.putInt(body.length+4);b.put(body);return new Value(type,b.array(),new LinkedHashMap<>(m));}
    static Value put(Value root,String key,Value value)throws Exception{Map<String,Value> m=new LinkedHashMap<>(root.fields);m.put(key,value);return container(root.type,m);}
    static Value remove(Value root,String key)throws Exception{Map<String,Value>m=new LinkedHashMap<>(root.fields);m.remove(key);return container(root.type,m);}
    static Value get(Value root,String key)throws Exception{return CollectionValidator.container(root,key);}
    static String uid(int n){return String.format(Locale.ROOT,"f0000000%016x",(long)n);}
    static Value skin(int sid,String uuid,boolean defaultSkin)throws Exception{Value v=doc("i",i(sid),"u",defaultSkin?str(uuid):oid(uuid),"fb",bool(false));if(!defaultSkin){v=put(v,"cr",i(1));v=put(v,"ias",bool(false));v=put(v,"tr",arr(Collections.emptyList()));for(String name:Arrays.asList("cd","pd","cwd","pwd"))v=put(v,name,doc());}return v;}
    static Value hero(int id)throws Exception{String uuid=String.format(Locale.ROOT,"%08x%016x",id,(long)id);return doc("sl",i(4),"so",i(1),"cf",i(100),"ef",i(0),"cat",new Value(10,new byte[0],null),"ar",doc("o",i(1),"ss",i(3),"oa",doc(),"rotc",doc(),"sl",arr(Collections.emptyList()),"ot",doc("_base_max_hp",i(60),"_base_phy_att_str",i(60),"_base_mag_att_str",i(60),"_base_phy_def",i(60),"_base_mag_def",i(60))),"ti",doc("items",arr(Collections.emptyList()),"mc",i(25)),"cs",oid(uuid),"sk",doc(uuid,skin(id,uuid,true)),"unknownHeroField",str("retained"));}
    static Value treasure(CollectionTargets.Treasure t,String u,boolean forbid)throws Exception{List<Value>attrs=new ArrayList<>(),tricks=new ArrayList<>();for(Map.Entry<String,CollectionTargets.Attr>a:t.attrs.entrySet())attrs.add(doc("n",str(a.getKey()),"v",d((a.getValue().low+a.getValue().high)/2)));for(int v:t.tricks)tricks.add(i(v));return doc("i",i(t.id),"u",oid(u),"w",i(1),"c",i(0),"ctt",i(1),"tr",doc("cl",i(t.quality),"f",bool(forbid),"ft",arr(tricks),"attr",arr(attrs),"lv",i(1),"x",i(0),"era",arr(Collections.emptyList()),"su",arr(Collections.emptyList())));}
    static CollectionTargets targets(Path path)throws Exception{
        CollectionTargets t=new CollectionTargets();for(String line:Files.readAllLines(path)){String[]f=line.split("\t",-1);if(f[0].equals("H")){t.heroes.add(Integer.parseInt(f[1]));t.ranks.put(Integer.parseInt(f[1]),Integer.parseInt(f[2]));}else if(f[0].equals("S"))t.skins.put(Integer.parseInt(f[1]),Integer.parseInt(f[2]));else{List<Integer> tricks=new ArrayList<>();if(!f[3].isEmpty())for(String s:f[3].split(","))tricks.add(Integer.parseInt(s));Map<String,CollectionTargets.Attr>a=new LinkedHashMap<>();if(!f[4].isEmpty())for(String s:f[4].split(",")){String[]v=s.split(":");a.put(v[0],new CollectionTargets.Attr(Double.parseDouble(v[1]),Double.parseDouble(v[2])));}CollectionTargets.Treasure r=new CollectionTargets.Treasure(Integer.parseInt(f[1]),Integer.parseInt(f[2]),tricks,a);t.treasures.put(r.key(),r);}}t.validate();return t;
    }
    static final class FakeEngine implements FullCollectionInitializer.Engine {
        final CollectionTargets targets;static int sequence=100;int grants;long inputBytes,outputBytes;boolean dropUnknown,suppressGrant,badNormalize;final Set<String>granted=new HashSet<>();
        FakeEngine(CollectionTargets t){targets=t;}
        public List<List<Integer>> liberateGroups(){Iterator<Integer>it=targets.heroes.iterator();int first=it.next(),second=it.next();return Arrays.asList(Arrays.asList(first,second),Arrays.asList(second,46,125));}
        public byte[] normalize(byte[] p)throws Exception {
            Value root=parse(p),mgr=get(root,"heromgr"),hrs=get(mgr,"hrs");
            for(List<Integer> group:liberateGroups()){
                List<String> owned=new ArrayList<>();int[] max=new int[4];boolean valid=true;
                for(Map.Entry<String,Value> e:hrs.fields.entrySet())if(group.contains(integer(e.getValue(),"0"))){owned.add(e.getKey());Value h=required(e.getValue(),"1");for(int n=0;n<4;n++){Value v=h.get(CollectionLiberateRules.FIELDS.get(n));if(v!=null&&v.stockInteger()==null){valid=false;continue;}int value=v==null?0:v.integer();if(value<0||(n==0&&value>4))valid=false;max[n]=Math.max(max[n],value);}}
                if(!valid||owned.size()<2)continue;
                for(String index:owned){Value pair=hrs.get(index),h=required(pair,"1");for(int n=0;n<4;n++){String f=CollectionLiberateRules.FIELDS.get(n);Value v=h.get(f);if((v==null?0:v.integer())!=max[n])h=put(h,f,i(max[n]));}hrs=put(hrs,index,put(pair,"1",h));}
            }
            if(badNormalize){Value pair=hrs.get("0"),h=required(pair,"1");h=put(h,"lh",i(integer(h,"lh")+1));hrs=put(hrs,"0",put(pair,"1",h));}
            return put(root,"heromgr",put(mgr,"hrs",hrs)).bytes;
        }
        public byte[] heroes(byte[] p)throws Exception{Value r=parse(p),mgr=get(r,"heromgr"),hrs=get(mgr,"hrs");Set<Integer> existing=CollectionValidator.scan(p,targets).heroes.keySet();for(int id:targets.heroes)if(id!=46&&id!=125&&!existing.contains(id))hrs=put(hrs,Integer.toString(hrs.fields.size()),arr(Arrays.asList(i(id),put(hero(id),"sl",i(targets.ranks.get(id))))));return put(r,"heromgr",put(mgr,"hrs",hrs)).bytes;}
        public byte[] helper(byte[] p,int id)throws Exception{if(CollectionValidator.scan(p,targets).heroes.containsKey(id))return p;Value r=parse(p),mgr=get(r,"heromgr"),hrs=get(mgr,"hrs"),h=put(hero(id),"sl",i(targets.ranks.get(id)));String key=Integer.toString(id);Value ps=get(mgr,"ps"),pending=ps.get(key);if(pending!=null){Value sk=get(h,"sk");for(int sid:ints(pending)){String u=uid(sequence++);sk=put(sk,u,skin(sid,u,false));}h=put(h,"sk",sk);mgr=put(mgr,"ps",put(ps,key,arr(Collections.emptyList())));}for(String[] move:new String[][]{{"pp","pa"},{"ppc","pat"}}){Value from=get(mgr,move[0]),v=from.get(key);if(v!=null){h=put(h,move[1],v);mgr=put(mgr,move[0],remove(from,key));}}return put(r,"heromgr",put(mgr,"hrs",put(hrs,Integer.toString(hrs.fields.size()),arr(Arrays.asList(i(id),h))))).bytes;}
        public byte[] skins(byte[] p)throws Exception{
            Value r=parse(p),mgr=get(r,"heromgr"),hrs=get(mgr,"hrs");Set<Integer> existing=CollectionValidator.scan(p,targets).skins;
            for(Map.Entry<String,Value> e:new ArrayList<>(hrs.fields.entrySet())){Value pair=e.getValue();int hid=integer(pair,"0");Value h=required(pair,"1"),sk=get(h,"sk");for(Map.Entry<Integer,Integer>s:targets.skins.entrySet())if(s.getValue()==hid&&!existing.contains(s.getKey())){String u=uid(sequence++);sk=put(sk,u,skin(s.getKey(),u,false));}h=put(h,"sk",sk);hrs=put(hrs,e.getKey(),put(pair,"1",h));}
            r=put(r,"heromgr",put(mgr,"hrs",hrs));if(dropUnknown)r=remove(r,"unknownRoot");return r.bytes;
        }
        public byte[] treasure(byte[] p,int id,int q)throws Exception{if(suppressGrant)return p;inputBytes+=p.length;grants++;granted.add(id+":"+q);Value r=parse(p),inv=get(r,"inv"),items=get(inv,"items");String u=uid(sequence++);Value item=CollectionHostTest.treasure(targets.treasures.get(id+":"+q),u,false);Value tr=required(item,"tr");List<Value> attrs=new ArrayList<>();for(Map.Entry<String,CollectionTargets.Attr>a:targets.treasures.get(id+":"+q).attrs.entrySet())attrs.add(doc("n",str(a.getKey()),"v",d(a.getValue().low)));item=put(item,"tr",put(tr,"attr",arr(attrs)));items=put(items,Integer.toString(items.fields.size()),item);byte[] out=put(r,"inv",put(inv,"items",items)).bytes;outputBytes+=out.length;return out;}
        public byte[] receipt(byte[] p)throws Exception{return put(parse(p),FullCollectionInitializer.RECEIPT,doc("schema",i(1),"policy",str(FullCollectionInitializer.POLICY),"targets",str(CollectionTargets.TARGET_SHA),"catalog",str(CollectionTargets.CATALOG_SHA),"contract",str(CollectionTargets.CONTRACT_SHA))).bytes;}
    }
    static final class Memory implements FullCollectionInitializer.Storage {byte[] bytes;int writes;boolean stopped=true,failWrite;Memory(byte[]b){bytes=b;}public byte[]read(){return bytes.clone();}public void write(byte[]b)throws Exception{if(failWrite)throw new IOException("synthetic pre-rename failure");bytes=b.clone();writes++;}public void stopped()throws Exception{need(stopped,"SYNTHETIC_ACTIVE_WRITER");}}
    // Synthetic disk boundary only; original Android Os.rename is not executed here.
    static final class SyntheticDisk implements FullCollectionInitializer.Storage {
        final Path file;int commits;boolean failAfterSync;
        SyntheticDisk(Path p){file=p;}
        public byte[]read()throws Exception{return Files.readAllBytes(file);}
        public void stopped(){ }
        public void write(byte[] candidate)throws Exception{
            Path temp=file.resolveSibling(file.getFileName()+".tmp");if(Files.exists(temp))Files.delete(temp);
            try(FileOutputStream out=new FileOutputStream(temp.toFile())){out.write(candidate);out.getFD().sync();}
            if(failAfterSync)throw new IOException("synthetic crash after temp fsync");
            Files.move(temp,file,StandardCopyOption.ATOMIC_MOVE,StandardCopyOption.REPLACE_EXISTING);commits++;
        }
    }
    interface Work {void run()throws Exception;}
    static int failed;
    static void refuse(Work w)throws Exception{try{w.run();throw new AssertionError("Unexpected acceptance");}catch(IOException expected){failed++;}}
    static Value aliasTreasure()throws Exception{return doc("cl",i(1),"f",bool(false),"ft",arr(Arrays.asList(i(4),i(8))),"attr",arr(Arrays.asList(doc("n",str("hp"),"v",d(12.5)))),"lv",i(1),"x",i(0),"era",arr(Collections.emptyList()),"su",arr(Collections.emptyList()));}
    static Value aliasItem()throws Exception{return doc("i",i(1258),"u",oid(uid(8001)),"w",i(1),"c",i(0),"ctt",i(0),"tr",aliasTreasure(),"future",doc("int",i(7),"sequence",arr(Arrays.asList(i(4),i(8)))));}
    static Value aliasReorder(Value v)throws Exception{List<String> names=new ArrayList<>(v.fields.keySet());Collections.reverse(names);Map<String,Value> m=new LinkedHashMap<>();for(String k:names){Value x=v.get(k);m.put(k,x.type==3?aliasReorder(x):x);}return container(v.type,m);}
    static Value aliasHero(int id,List<Value> items)throws Exception{Value h=hero(id);return put(h,"ti",put(h.get("ti"),"items",arr(items)));}
    static Value aliasRoot(List<Value> inv,List<List<Value>> equips)throws Exception{List<Value> hrs=new ArrayList<>();int h=2;for(List<Value> items:equips)hrs.add(doc("0",i(h),"1",aliasHero(h++,items)));return doc("inv",doc("items",arr(inv)),"heromgr",doc("hrs",arr(hrs)),"unrelated",doc("preserve",str("exact")));}
    static CollectionValidator.Index acceptAlias(String label,Value root,int uuids)throws Exception{byte[] snapshot=root.bytes.clone();CollectionValidator.Index x=CollectionValidator.scan(root.bytes,CollectionHostTest.currentTargets);check(x.uuids.size()==uuids,label+" UUID union");check(Arrays.equals(snapshot,root.bytes),label+" read only");checks++;System.out.println("PASS "+label);return x;}
    static void rejectAlias(String label,Value root)throws Exception{try{CollectionValidator.scan(root.bytes,CollectionHostTest.currentTargets);throw new AssertionError(label+" accepted");}catch(IOException expected){checks++;System.out.println("PASS "+label);}}
    static CollectionTargets currentTargets;static int checks;
    static byte[] initial(CollectionTargets t)throws Exception{
        int hid=t.heroes.iterator().next();Iterator<CollectionTargets.Treasure>it=t.treasures.values().iterator();CollectionTargets.Treasure a=it.next(),b=it.next(),disabled=it.next();Value hero=hero(hid);hero=put(hero,"ls",new Value(18,ByteBuffer.allocate(8).order(ByteOrder.LITTLE_ENDIAN).putLong(3).array(),null));hero=put(hero,"lh",new Value(18,ByteBuffer.allocate(8).order(ByteOrder.LITTLE_ENDIAN).putLong(9000).array(),null));hero=put(hero,"la",i(500));hero=put(hero,"ld",i(600));Value existingHidden=hero(125);for(String f:CollectionLiberateRules.FIELDS)existingHidden=put(existingHidden,f,i(0));String equipped=uid(2);hero=put(hero,"ti",doc("items",arr(Arrays.asList(treasure(b,equipped,false))),"mc",i(25)));hero=put(hero,"jbt",arr(Arrays.asList(oid(equipped),new Value(10,new byte[0],null))));
        return doc("uid",i(7),"account",str("synthetic"),"an",str("synthetic"),"unknownRoot",new Value(18,new byte[]{1,2,3,4,5,6,7,8},null),"heromgr",doc("ps",doc("46",arr(Arrays.asList(i(46))),"999",arr(Arrays.asList(i(123)))),"pp",doc("46",arr(Arrays.asList(i(17)))),"ppc",doc("46",arr(Arrays.asList(arr(Arrays.asList(i(17),i(1)))))),"hrs",arr(Arrays.asList(arr(Arrays.asList(i(hid),hero)),arr(Arrays.asList(i(125),existingHidden))))),"inv",doc("items",arr(Arrays.asList(treasure(a,uid(1),false),treasure(disabled,uid(3),true))))).bytes;
    }
    public static void main(String[]args)throws Exception{
        CollectionTargets targets=targets(Paths.get(args[0]));currentTargets=targets;byte[] initial=initial(targets);
        Value alias=aliasItem();
        acceptAlias("alias_inv_one_hero",aliasRoot(Arrays.asList(alias),Arrays.asList(Arrays.asList(alias))),2);
        acceptAlias("alias_inv_multiple_heroes",aliasRoot(Arrays.asList(alias),Arrays.asList(Arrays.asList(alias),Arrays.asList(alias))),3);
        acceptAlias("alias_equipment_only",aliasRoot(Collections.emptyList(),Arrays.asList(Arrays.asList(alias),Arrays.asList(alias))),3);
        acceptAlias("alias_document_key_order_ignored",aliasRoot(Arrays.asList(alias),Arrays.asList(Arrays.asList(aliasReorder(alias)))),2);
        rejectAlias("alias_same_container_inventory_duplicate",aliasRoot(Arrays.asList(alias,alias),Collections.emptyList()));
        rejectAlias("alias_same_container_equipment_duplicate",aliasRoot(Collections.emptyList(),Arrays.asList(Arrays.asList(alias,alias))));
        rejectAlias("alias_same_uuid_different_item",aliasRoot(Arrays.asList(alias),Arrays.asList(Arrays.asList(put(alias,"i",i(1259))))));
        rejectAlias("alias_same_uuid_different_unknown_field",aliasRoot(Arrays.asList(alias),Arrays.asList(Arrays.asList(put(alias,"future",doc("int",i(8),"sequence",arr(Arrays.asList(i(4),i(8)))))))));
        rejectAlias("alias_same_numeric_value_different_bson_type",aliasRoot(Arrays.asList(alias),Arrays.asList(Arrays.asList(put(alias,"future",doc("int",new Value(18,ByteBuffer.allocate(8).order(ByteOrder.LITTLE_ENDIAN).putLong(7).array(),null),"sequence",arr(Arrays.asList(i(4),i(8)))))))));
        rejectAlias("alias_nested_array_order_matters",aliasRoot(Arrays.asList(alias),Arrays.asList(Arrays.asList(put(alias,"future",doc("int",i(7),"sequence",arr(Arrays.asList(i(8),i(4)))))))));
        rejectAlias("alias_missing_unknown_field",aliasRoot(Arrays.asList(alias),Arrays.asList(Arrays.asList(remove(alias,"future")))));
        rejectAlias("alias_ordinary_item_cross_container_mirror",aliasRoot(Arrays.asList(remove(alias,"tr")),Arrays.asList(Arrays.asList(remove(alias,"tr")))));
        String skinId=String.format(Locale.ROOT,"%08x%016x",2,2L);Value skinCollision=put(alias,"u",oid(skinId));
        rejectAlias("alias_inventory_skin_collision",aliasRoot(Arrays.asList(skinCollision),Arrays.asList(Collections.emptyList())));
        rejectAlias("alias_equipment_skin_collision",aliasRoot(Collections.emptyList(),Arrays.asList(Arrays.asList(skinCollision))));
        rejectAlias("alias_same_second_container_duplicate_after_inv_alias",aliasRoot(Arrays.asList(alias),Arrays.asList(Arrays.asList(alias,alias))));
        rejectAlias("alias_same_third_container_duplicate_after_multiple_aliases",aliasRoot(Arrays.asList(alias),Arrays.asList(Arrays.asList(alias),Arrays.asList(alias,alias))));
        acceptAlias("alias_same_uuid_across_three_containers",aliasRoot(Arrays.asList(alias),Arrays.asList(Arrays.asList(alias),Arrays.asList(alias))),3);
        Value h2=hero(2),h3=hero(3);Value duplicateSkin=skin(3,skinId,false);h3=put(h3,"sk",doc(skinId,duplicateSkin));h3=put(h3,"cs",oid(skinId));
        rejectAlias("alias_duplicate_skin_uuid",doc("inv",doc("items",arr(Collections.emptyList())),"heromgr",doc("hrs",arr(Arrays.asList(doc("0",i(2),"1",h2),doc("0",i(3),"1",h3))))));
        // Real equip mirror in the full-transaction fixture: original inv item mirrored into hero ti.
        Value mirrorRoot=parse(initial),mirrorMgr=get(mirrorRoot,"heromgr"),mirrorHrs=get(mirrorMgr,"hrs"),mirrorPair=mirrorHrs.get("0"),mirrorPair2=mirrorHrs.get("1");
        Value mirrorHero=required(mirrorPair,"1"),mirrorTi=required(mirrorHero,"ti"),mirrorItems=get(mirrorTi,"items"),mirrorDoc=get(get(mirrorRoot,"inv"),"items").get("0");
        Value mirrorHero2=put(mirrorHero,"ti",put(mirrorTi,"items",put(mirrorItems,Integer.toString(mirrorItems.fields.size()),mirrorDoc)));
        Value mirrorHeroB=required(mirrorPair2,"1"),mirrorTiB=required(mirrorHeroB,"ti"),mirrorItemsB=get(mirrorTiB,"items");
        Value mirrorHero2B=put(mirrorHeroB,"ti",put(mirrorTiB,"items",put(mirrorItemsB,Integer.toString(mirrorItemsB.fields.size()),mirrorDoc)));
        mirrorRoot=put(mirrorRoot,"heromgr",put(mirrorMgr,"hrs",put(put(mirrorHrs,"1",put(mirrorPair2,"1",mirrorHero2B)),"0",put(mirrorPair,"1",mirrorHero2))));
        byte[] mirrorBytes=mirrorRoot.bytes.clone();
        CollectionValidator.Index mirrorFirst=CollectionValidator.scan(mirrorRoot.bytes,targets),mirrorSecond=CollectionValidator.scan(mirrorRoot.bytes,targets);
        check(mirrorFirst.uuids.equals(mirrorSecond.uuids)&&Arrays.equals(mirrorBytes,mirrorRoot.bytes),"mirror scan twice read only");
        CollectionValidator.preserved(mirrorFirst,mirrorSecond);
        Memory mirrored=new Memory(mirrorBytes);FakeEngine mirrorEngine=new FakeEngine(targets);
        FullCollectionInitializer.transact(mirrored,mirrorEngine,targets,"synthetic",7,FullCollectionInitializer.NO_FAULTS);
        check(mirrored.writes==1&&mirrorEngine.grants==1898,"mirror first start commits once with unchanged grant count");
        Value readback=parse(mirrored.bytes);Value readHrs=get(get(readback,"heromgr"),"hrs");
        for(String key:Arrays.asList("0","1")){Value hero=required(readHrs.get(key),"1"),items=get(required(hero,"ti"),"items");check(Arrays.equals(items.get(Integer.toString(items.fields.size()-1)).bytes,mirrorDoc.bytes),"original mirror document bytes preserved after first start");}
        FakeEngine mirrorRepeat=new FakeEngine(targets);
        FullCollectionInitializer.transact(mirrored,mirrorRepeat,targets,"synthetic",7,FullCollectionInitializer.NO_FAULTS);
        check(mirrored.writes==1&&mirrorRepeat.grants==0,"second start idempotent zero extra grants/no write");
        Value reread=parse(mirrored.bytes);Value rereadHrs=get(get(reread,"heromgr"),"hrs");
        for(String key:Arrays.asList("0","1")){Value hero=required(rereadHrs.get(key),"1"),items=get(required(hero,"ti"),"items");check(Arrays.equals(items.get(Integer.toString(items.fields.size()-1)).bytes,mirrorDoc.bytes),"original mirror document bytes preserved after second start");}
        Memory memory=new Memory(initial);FakeEngine engine=new FakeEngine(targets);
        long firstStart=System.nanoTime();FullCollectionInitializer.transact(memory,engine,targets,"synthetic",7,FullCollectionInitializer.NO_FAULTS);long firstMillis=(System.nanoTime()-firstStart)/1000000L;long firstInputBytes=engine.inputBytes,firstOutputBytes=engine.outputBytes;
        check(memory.writes==1,"one complete candidate commit");check(engine.grants==1898,"skip existing valid inventory and equipped pairs; grant missing forbidden pair");check(!engine.granted.contains(targets.treasures.values().iterator().next().key()),"existing pair not regranted");
        byte[] complete=memory.bytes.clone();CollectionValidator.Index before=CollectionValidator.scan(initial,targets),after=CollectionValidator.scan(complete,targets);CollectionValidator.preserved(before,after,after);check(after.heroes.get(125).get("lh").integer()==9000&&after.heroes.get(125).get("ls").integer()==3,"existing hidden hero receives exact required shared-group max");check(after.heroes.get(targets.heroes.iterator().next()).get("ls").type==18,"unchanged existing int64 progress type preserved");CollectionValidator.complete(after,targets);check(after.uuids.size()>=2394,"full distinct instance set");
        engine=new FakeEngine(targets);FullCollectionInitializer.transact(memory,engine,targets,"synthetic",7,FullCollectionInitializer.NO_FAULTS);check(memory.writes==1&&engine.grants==0,"repeat exact targets no writes/instances");
        // Receipt never exempts target verification: remove one valid pair, repair exactly one.
        Value root=parse(complete),inv=get(root,"inv"),items=get(inv,"items");List<Value> list=new ArrayList<>(items.fields.values());list.remove(0);root=put(root,"inv",put(inv,"items",arr(list)));Memory damaged=new Memory(root.bytes);FakeEngine repair=new FakeEngine(targets);FullCollectionInitializer.transact(damaged,repair,targets,"synthetic",7,FullCollectionInitializer.NO_FAULTS);check(repair.grants==1&&damaged.writes==1,"matching receipt missing target repaired");
        for(String point:Arrays.asList("AFTER_READ","AFTER_HERO_BATCH","AFTER_HIDDEN_HELPERS","AFTER_SKIN_BATCH","AFTER_VALIDATION","BEFORE_COMMIT")){
            Memory m=new Memory(complete);refuse(()->FullCollectionInitializer.transact(m,new FakeEngine(targets),targets,"synthetic",7,p->{if(p.equals(point))throw new IOException("synthetic fault");}));check(Arrays.equals(m.bytes,complete)&&m.writes==0,"failure preserved old complete save");
        }
        Memory partial=new Memory(initial);refuse(()->FullCollectionInitializer.transact(partial,new FakeEngine(targets),targets,"synthetic",7,p->{if(p.equals("AFTER_TREASURE_1"))throw new IOException("partial grant");}));check(Arrays.equals(partial.bytes,initial)&&partial.writes==0,"partial candidate never committed");
        Memory writeFailure=new Memory(complete);writeFailure.bytes=remove(parse(complete),FullCollectionInitializer.RECEIPT).bytes;byte[] prior=writeFailure.bytes.clone();writeFailure.failWrite=true;refuse(()->FullCollectionInitializer.transact(writeFailure,new FakeEngine(targets),targets,"synthetic",7,FullCollectionInitializer.NO_FAULTS));check(Arrays.equals(prior,writeFailure.bytes),"pre-rename preserves original");
        Memory restart=new Memory(prior);refuse(()->FullCollectionInitializer.transact(restart,new FakeEngine(targets),targets,"synthetic",7,p->{if(p.equals("AFTER_COMMIT"))throw new IOException("simulated crash after atomic rename");}));check(restart.writes==1,"crash happened after full commit");FullCollectionInitializer.transact(restart,new FakeEngine(targets),targets,"synthetic",7,FullCollectionInitializer.NO_FAULTS);check(restart.writes==1,"restart fully revalidates without second commit");
        Memory active=new Memory(complete);active.stopped=false;refuse(()->FullCollectionInitializer.transact(active,new FakeEngine(targets),targets,"synthetic",7,FullCollectionInitializer.NO_FAULTS));
        Memory lost=new Memory(complete);FakeEngine malicious=new FakeEngine(targets);malicious.dropUnknown=true;refuse(()->FullCollectionInitializer.transact(lost,malicious,targets,"synthetic",7,FullCollectionInitializer.NO_FAULTS));check(Arrays.equals(lost.bytes,complete),"unknown root loss rejected");
        Memory collision=new Memory(put(parse(initial),FullCollectionInitializer.RECEIPT,str("foreign")).bytes);refuse(()->FullCollectionInitializer.transact(collision,new FakeEngine(targets),targets,"synthetic",7,FullCollectionInitializer.NO_FAULTS));
        refuse(()->FullCollectionInitializer.transact(new Memory(complete),new FakeEngine(targets),targets,"wrong",7,FullCollectionInitializer.NO_FAULTS));
        // Strict parser and reference/type faults use only locally generated fixture BSON.
        check(parse(new byte[]{12,0,0,0,16,120,0,1,0,0,0,0}).get("x").integer()==1,"independent known BSON bytes");
        refuse(()->parse(new byte[]{19,0,0,0,16,120,0,1,0,0,0,16,120,0,2,0,0,0,0}));
        refuse(()->parse(Arrays.copyOf(initial,initial.length-1)));
        Memory badId=new Memory(put(parse(initial),"uid",str("7")).bytes);refuse(()->FullCollectionInitializer.transact(badId,new FakeEngine(targets),targets,"synthetic",7,FullCollectionInitializer.NO_FAULTS));
        Value firstRoot=parse(initial),firstMgr=get(firstRoot,"heromgr"),firstHrs=get(firstMgr,"hrs"),firstPair=firstHrs.fields.values().iterator().next(),firstHero=required(firstPair,"1");
        Value danglingHero=put(firstHero,"cs",oid(uid(999999)));Value dangling=put(firstRoot,"heromgr",put(firstMgr,"hrs",put(firstHrs,"0",put(firstPair,"1",danglingHero))));
        refuse(()->FullCollectionInitializer.transact(new Memory(dangling.bytes),new FakeEngine(targets),targets,"synthetic",7,FullCollectionInitializer.NO_FAULTS));
        Value initialInv=get(firstRoot,"inv"),initialItems=get(initialInv,"items");String collisionId=String.format(Locale.ROOT,"%08x%016x",46,46L);Value collisionItem=doc("i",i(99999),"u",oid(collisionId),"w",i(1));
        Value defaultCollision=put(firstRoot,"inv",put(initialInv,"items",put(initialItems,Integer.toString(initialItems.fields.size()),collisionItem)));
        refuse(()->FullCollectionInitializer.transact(new Memory(defaultCollision.bytes),new FakeEngine(targets),targets,"synthetic",7,FullCollectionInitializer.NO_FAULTS));
        Memory missingWithReceipt=new Memory(root.bytes);FakeEngine noGrant=new FakeEngine(targets);noGrant.suppressGrant=true;refuse(()->FullCollectionInitializer.transact(missingWithReceipt,noGrant,targets,"synthetic",7,FullCollectionInitializer.NO_FAULTS));check(missingWithReceipt.writes==0,"same receipt cannot bypass incomplete exact target");
        Memory becameActive=new Memory(complete);refuse(()->FullCollectionInitializer.transact(becameActive,new FakeEngine(targets),targets,"synthetic",7,p->{if(p.equals("AFTER_HERO_BATCH"))becameActive.stopped=false;}));check(becameActive.writes==0,"late active writer gate prevents commit");
        Value completeRoot=parse(complete),completeMgr=get(completeRoot,"heromgr"),completeHrs=get(completeMgr,"hrs");
        for(Map.Entry<String,Value> e:completeHrs.fields.entrySet())if(integer(e.getValue(),"0")==46){Value h=required(e.getValue(),"1");check(ints(required(h,"pa")).equals(Arrays.asList(17)),"original pending pendant transfer");Value lostH=remove(h,"pa");Value lostRoot=put(completeRoot,"heromgr",put(completeMgr,"hrs",put(completeHrs,e.getKey(),put(e.getValue(),"1",lostH))));refuse(()->CollectionValidator.preserved(before,CollectionValidator.scan(lostRoot.bytes,targets),after));break;}
        Value duplicateInventory=put(firstRoot,"inv",put(initialInv,"items",put(initialItems,"1",put(initialItems.get("1"),"u",oid(uid(1))))));refuse(()->CollectionValidator.scan(duplicateInventory.bytes,targets));
        Memory invalidNormalize=new Memory(complete);FakeEngine badNormalize=new FakeEngine(targets);badNormalize.badNormalize=true;refuse(()->FullCollectionInitializer.transact(invalidNormalize,badNormalize,targets,"synthetic",7,FullCollectionInitializer.NO_FAULTS));check(invalidNormalize.writes==0,"unproven normalization delta rejected");
        refuse(()->FullCollectionInitializer.cancellationPoint(()->true));Thread.currentThread().interrupt();try{refuse(()->FullCollectionInitializer.cancellationPoint(()->false));}finally{Thread.interrupted();}
        Path diskDirectory=Files.createTempDirectory("p7-collection-synthetic-");
        try {
            Path file=diskDirectory.resolve("synthetic.bson");Files.write(file,prior);SyntheticDisk disk=new SyntheticDisk(file);disk.failAfterSync=true;
            refuse(()->FullCollectionInitializer.transact(disk,new FakeEngine(targets),targets,"synthetic",7,FullCollectionInitializer.NO_FAULTS));
            check(Arrays.equals(Files.readAllBytes(file),prior)&&disk.commits==0&&Files.exists(diskDirectory.resolve("synthetic.bson.tmp")),"fsynced partial candidate leaves authoritative original intact");
            disk.failAfterSync=false;FullCollectionInitializer.transact(disk,new FakeEngine(targets),targets,"synthetic",7,FullCollectionInitializer.NO_FAULTS);check(disk.commits==1&&!Files.exists(diskDirectory.resolve("synthetic.bson.tmp")),"retry cleans owned temporary and commits once");
            SyntheticDisk restarted=new SyntheticDisk(file);FullCollectionInitializer.transact(restarted,new FakeEngine(targets),targets,"synthetic",7,FullCollectionInitializer.NO_FAULTS);check(restarted.commits==0,"new host process model revalidates completed receipt without write");
        } finally {try(java.nio.file.DirectoryStream<Path>stream=Files.newDirectoryStream(diskDirectory)){for(Path p:stream)Files.delete(p);}Files.delete(diskDirectory);}
        System.out.println("ALIAS_CONTRACT_PASS checks="+checks+" mirrorBytes="+mirrorDoc.bytes.length+" firstGrants=1898 secondGrants=0 firstWrites=1 secondWrites=1; START_AND_SCAN_TWICE_MIRROR_PRESERVED");
        System.out.println("SYNTHETIC_METRICS initialBytes="+initial.length+" finalBytes="+complete.length+" firstGrantCalls=1898 inputBytes="+firstInputBytes+" outputBytes="+firstOutputBytes+" firstPassMillis="+firstMillis+"; NOT original-engine/mobile performance");
        System.out.println("SYNTHETIC HOST ONLY:140 heroes/494 skins/1900 pairs, one commit, idempotence, receipt repair; "+failed+" fault cases passed. Original P7 engine/ART/native not executed.");
    }
}
