package com.project7.localmanager;
import java.io.*;
import java.util.*;
import static com.project7.localmanager.CollectionBson.*;

/** Checks exact collection targets and byte preservation, never edits BSON. */
final class CollectionValidator {
    static final class Index {
        final Value root;final Map<Integer,Value> heroes=new LinkedHashMap<>();final Set<Integer> skins=new HashSet<>();
        final Set<String> treasures=new HashSet<>();
        /** Every identity UUID once; newTypes uses this as the "already existed" set. */
        final Set<String> uuids=new HashSet<>();
        private final Map<String,Instance> instances=new HashMap<>();
        Index(Value r){root=r;}
    }
    /** First sighting of a UUID: a wardrobe skin or an item inside one item container. */
    private static final class Instance {
        final boolean skin;final String container;final Value doc;
        Instance(boolean s,String c,Value d){skin=s;container=c;doc=d;}
    }
    static Value empty()throws IOException{return CollectionBson.parse(new byte[]{5,0,0,0,0});}
    static Value container(Value p,String key)throws IOException {Value v=p.get(key);if(v==null)return empty();need(v.type==3||v.type==4,"BAD_CONTAINER_"+key);return v;}
    /** Skin UUIDs are globally unique and may never coincide with an item instance. */
    static void skinUuid(Index index,String u)throws IOException{
        index.uuids.add(u);Instance prior=index.instances.get(u);
        need(prior==null,prior!=null&&!prior.skin?"SKIN_UUID_COLLISION":"DUPLICATE_SKIN_UUID");
        index.instances.put(u,new Instance(true,"skin",null));
    }
    /** Per-container item uniqueness; a foreign container must carry the exact same document. */
    static void itemUuid(Index index,String u,Value doc,String container)throws IOException{
        index.uuids.add(u);Instance prior=index.instances.get(u);
        if(prior==null){index.instances.put(u,new Instance(false,container,doc));return;}
        need(!prior.skin,"SKIN_UUID_COLLISION");
        need(!prior.container.equals(container),"DUPLICATE_INSTANCE_UUID");
        Value a=doc.get("tr"),b=prior.doc.get("tr");
        need(a!=null&&a.type==3&&b!=null&&b.type==3,"NON_TREASURE_MIRROR");
        need(semantic(doc,prior.doc),"MIRROR_ITEM_DOCUMENT_CONFLICT");
    }
    /** BSON type/value and array order strict; document key order irrelevant. */
    static boolean semantic(Value a,Value b){
        if(a==null||b==null||a.type!=b.type)return false;
        if(a.type==3){if(a.fields==null||b.fields==null||!a.fields.keySet().equals(b.fields.keySet()))return false;for(Map.Entry<String,Value> e:a.fields.entrySet())if(!semantic(e.getValue(),b.get(e.getKey())))return false;return true;}
        if(a.type==4){if(a.fields==null||b.fields==null||a.fields.size()!=b.fields.size())return false;Iterator<Value>x=a.fields.values().iterator(),y=b.fields.values().iterator();while(x.hasNext())if(!semantic(x.next(),y.next()))return false;return true;}
        return Arrays.equals(a.bytes,b.bytes);
    }
    static Index scan(byte[] bytes,CollectionTargets targets)throws IOException {
        Index index=new Index(parse(bytes));Value mgr=container(index.root,"heromgr");
        for(Value pair:container(mgr,"hrs").values()){
            int id=integer(pair,"0");Value hero=required(pair,"1");need(hero.type==3&&index.heroes.put(id,hero)==null,"DUPLICATE_HERO");
        }
        scanItems(container(container(index.root,"inv"),"items"),targets,index,"inv",null);
        for(Map.Entry<Integer,Value> e:index.heroes.entrySet()){
            int hid=e.getKey();Value hero=e.getValue(),skins=container(hero,"sk");Set<String> skinKeys=new HashSet<>();
            for(Map.Entry<String,Value> skin:skins.fields.entrySet()){
                Value doc=skin.getValue();int sid=integer(doc,"i");Value u=required(doc,"u");String uuid=u.uuid(sid==hid);
                if(u.type==2)need(uuid.equals(String.format(Locale.ROOT,"%08x%016x",hid,(long)hid)),"NONDEFAULT_STRING_SKIN_UUID");
                need(uuid.equals(skin.getKey()),"SKIN_UUID_KEY_MISMATCH");skinUuid(index,uuid);skinKeys.add(uuid);
                Value disabled=doc.get("fb");need(disabled!=null&&disabled.type==8,"BAD_SKIN_FB");
                if(!disabled.bool()&&targets.skins.containsKey(sid)){need(targets.skins.get(sid)==hid,"SKIN_WRONG_HERO");if(u.type==2||purchasedShape(doc))index.skins.add(sid);}
            }
            for(String key:Arrays.asList("cs","lncs")){Value ref=hero.get(key);if(ref!=null&&ref.type!=10)need(skinKeys.contains(ref.uuid(true)),"DANGLING_SKIN_REFERENCE");}
            Set<String> equipped=new HashSet<>();scanItems(container(container(hero,"ti"),"items"),targets,index,"hero."+hid,equipped);
            Value jbt=hero.get("jbt");if(jbt!=null)for(Value ref:jbt.values())if(ref.type!=10)need(equipped.contains(ref.uuid(false)),"DANGLING_JIBAN_TREASURE_REFERENCE");
            Value pending=container(mgr,"ps").get(Integer.toString(hid));int pendingCount=pending==null?0:pending.values().size();need(skins.fields.size()+pendingCount<=500,"WARDROBE_LIMIT");
        }
        return index;
    }
    private static void scanItems(Value items,CollectionTargets targets,Index index,String container,Set<String> equipped)throws IOException{
        Set<String> local=new HashSet<>();
        for(Value item:items.values()){
            int id=integer(item,"i");String u=required(item,"u").uuid(false);need(local.add(u),"DUPLICATE_INSTANCE_UUID");itemUuid(index,u,item,container);if(equipped!=null)equipped.add(u);
            Value tr=item.get("tr");if(tr==null)continue;need(tr.type==3,"BAD_TREASURE_DOC");Value q=tr.get("cl");if(q==null)continue;int quality=q.integer();String key=id+":"+quality;CollectionTargets.Treasure target=targets.treasures.get(key);
            if(target!=null&&matches(item,tr,target))index.treasures.add(key);
        }
    }
    private static boolean matches(Value item,Value tr,CollectionTargets.Treasure target)throws IOException{
        Value w=item.get("w");if(w!=null&&w.integer()<=0)return false;Value f=tr.get("f");if(f!=null&&f.bool())return false;
        Value ft=tr.get("ft"),attr=tr.get("attr");if(ft==null||attr==null)return false;
        if(!ints(ft).equals(target.tricks))return false;
        Map<String,Double> actual=new HashMap<>();for(Value a:attr.values()){String n=required(a,"n").string();double v=required(a,"v").decimal();need(actual.put(n,v)==null,"DUPLICATE_TREASURE_ATTRIBUTE");}
        for(Map.Entry<String,CollectionTargets.Attr> e:target.attrs.entrySet()){Double v=actual.get(e.getKey());if(v==null||v<e.getValue().low||v>e.getValue().high)return false;}
        return true;
    }
    private static boolean purchasedShape(Value skin)throws IOException {
        if(skin.get("cr")==null||skin.get("cr").type!=16||skin.get("ias")==null||skin.get("ias").type!=8||skin.get("tr")==null||skin.get("tr").type!=4)return false;
        for(String name:Arrays.asList("cd","pd","cwd","pwd"))if(skin.get(name)==null||skin.get(name).type!=3)return false;
        return true;
    }
    private static void int32(Value value,String... keys)throws IOException{for(String key:keys)need(required(value,key).type==16,"NEW_INT32_TYPE");}
    static void newTypes(Index before,Index after,CollectionTargets targets)throws IOException {
        for(Map.Entry<Integer,Value> entry:after.heroes.entrySet())if(!before.heroes.containsKey(entry.getKey())&&targets.heroes.contains(entry.getKey())) {
            int id=entry.getKey();Value hero=entry.getValue();int32(hero,"sl","so","cf","ef");need(integer(hero,"sl")==targets.ranks.get(id)&&integer(hero,"so")==1&&integer(hero,"cf")==100&&integer(hero,"ef")==0&&required(hero,"cat").type==10,"NEW_HERO_DEFAULTS");
            Value ti=required(hero,"ti"),ar=required(hero,"ar");int32(ti,"mc");int32(ar,"o","ss");need(integer(ti,"mc")==25&&required(ti,"items").type==4&&required(ti,"items").fields.isEmpty(),"NEW_HERO_TREASURE_DEFAULTS");
            need(integer(ar,"o")==1&&integer(ar,"ss")==3&&required(ar,"oa").type==3&&required(ar,"oa").fields.isEmpty()&&required(ar,"rotc").type==3&&required(ar,"rotc").fields.isEmpty()&&required(ar,"sl").type==4&&required(ar,"sl").fields.isEmpty(),"NEW_HERO_ARTIFACT_DEFAULTS");
            Value ot=required(ar,"ot");for(String key:Arrays.asList("_base_max_hp","_base_phy_att_str","_base_mag_att_str","_base_phy_def","_base_mag_def"))need(integer(ot,key)==60,"NEW_HERO_ARTIFACT_POINT");
            need(required(hero,"cs").uuid(false).equals(String.format(Locale.ROOT,"%08x%016x",id,(long)id)),"NEW_HERO_DEFAULT_SKIN_REFERENCE");
        }

        for(Value hero:after.heroes.values())for(Value skin:container(hero,"sk").values()) {
            Value u=required(skin,"u");if(!before.uuids.contains(u.uuid(true)))int32(skin,"i");if(!before.uuids.contains(u.uuid(true))&&u.type==7) {
                need(purchasedShape(skin),"NEW_PURCHASED_SKIN_SHAPE");need(!required(skin,"ias").bool()&&required(skin,"tr").fields.isEmpty(),"NEW_SKIN_DEFAULTS");
                for(String name:Arrays.asList("cd","pd","cwd","pwd"))need(required(skin,name).fields.isEmpty(),"NEW_SKIN_COLOR_DEFAULTS");
            }
        }
        List<Value> lists=new ArrayList<>();lists.add(container(container(after.root,"inv"),"items"));for(Value h:after.heroes.values())lists.add(container(container(h,"ti"),"items"));
        for(Value list:lists)for(Value item:list.values())if(!before.uuids.contains(required(item,"u").uuid(false))&&item.get("tr")!=null) {
            Value tr=item.get("tr");int32(item,"i","w","c","ctt");int32(tr,"cl","lv","x");CollectionTargets.Treasure target=targets.treasures.get(integer(item,"i")+":"+integer(tr,"cl"));if(target==null)continue;
            need(integer(item,"w")==1&&integer(item,"c")==0&&required(item,"ctt").type==16&&integer(tr,"lv")==1&&integer(tr,"x")==0&&!required(tr,"f").bool(),"NEW_TREASURE_DEFAULTS");
            for(String name:Arrays.asList("era","su"))need(required(tr,name).type==4&&required(tr,name).fields.isEmpty(),"NEW_TREASURE_ARRAY_DEFAULTS");
            Map<String,Double> attrs=new HashMap<>();for(Value a:required(tr,"attr").values())attrs.put(required(a,"n").string(),required(a,"v").decimal());
            for(Map.Entry<String,CollectionTargets.Attr> e:target.attrs.entrySet())need(attrs.get(e.getKey())!=null&&attrs.get(e.getKey())==e.getValue().low,"NEW_TREASURE_ATTRIBUTE_LOWER_BOUND");
        }
    }
    static void complete(Index i,CollectionTargets t)throws IOException {need(i.heroes.keySet().containsAll(t.heroes)&&i.skins.containsAll(t.skins.keySet())&&i.treasures.containsAll(t.treasures.keySet()),"INCOMPLETE_EXACT_TARGETS");}
    static void preserved(Index old,Index now)throws IOException{preserved(old,now,old);}
    static void preserved(Index old,Index now,Index approvedLiberate)throws IOException{
        Set<Integer> added=new HashSet<>(now.heroes.keySet());added.removeAll(old.heroes.keySet());
        for(Map.Entry<Integer,Value> e:old.heroes.entrySet()){need(now.heroes.containsKey(e.getKey())&&approvedLiberate.heroes.containsKey(e.getKey()),"EXISTING_HERO_REMOVED");for(String f:CollectionLiberateRules.FIELDS){Value expected=approvedLiberate.heroes.get(e.getKey()).get(f),actual=now.heroes.get(e.getKey()).get(f);need(expected==null?actual==null:equal(expected,actual),"LIBERATE_FINAL_MISMATCH");}}
        pendingTransfers(old,now,added);Map<String,Value> approved=new HashMap<>();Value pairs=container(container(old.root,"heromgr"),"hrs");for(Map.Entry<String,Value> pair:pairs.fields.entrySet()){int id=integer(pair.getValue(),"0");Value h=approvedLiberate.heroes.get(id);for(String f:CollectionLiberateRules.FIELDS)approved.put("heromgr.hrs."+pair.getKey()+".1."+f,h.get(f));}preserve(old.root,now.root,"",added,approved);
    }
    private static boolean moved(String path,Set<Integer> added){for(int id:added)if(path.equals("heromgr.ps."+id)||path.equals("heromgr.pp."+id)||path.equals("heromgr.ppc."+id))return true;return false;}
    private static void pendingTransfers(Index old,Index now,Set<Integer> added)throws IOException {
        Value mgr=container(old.root,"heromgr");
        for(int id:added){Value hero=now.heroes.get(id);String key=Integer.toString(id);Value pending=container(mgr,"ps").get(key);
            if(pending!=null){Set<Integer> actual=new HashSet<>();for(Value skin:container(hero,"sk").values())if(!required(skin,"fb").bool())actual.add(integer(skin,"i"));need(actual.containsAll(ints(pending)),"PENDING_SKIN_TRANSFER_LOST");}
            Value pp=container(mgr,"pp").get(key);if(pp!=null)need(equal(pp,hero.get("pa")),"PENDING_PENDANT_TRANSFER_LOST");
            Value ppc=container(mgr,"ppc").get(key);if(ppc!=null)need(equal(ppc,hero.get("pat")),"PENDING_PENDANT_TIME_TRANSFER_LOST");
        }
    }
    private static void preserve(Value before,Value after,String path,Set<Integer> added,Map<String,Value> approved)throws IOException{
        if(approved.containsKey(path)){Value expected=approved.get(path);need(expected==null?after==null:equal(expected,after),"LIBERATE_CHANGED_AFTER_NORMALIZE");return;}
        if(moved(path,added))return;
        if(path.matches("q7AchievementCounts\\.(?:1:\\[\\]|51:\\[[1-5]\\])")){if(equal(before,after))return;need(after!=null&&before.stockInteger()!=null&&after.type==16&&after.integer()>=before.integer()&&after.integer()<=100000000,"INVALID_STOCK_COUNTER_DELTA");return;}
        need(after!=null&&before.type==after.type,"EXISTING_FIELD_TYPE_OR_REMOVAL_"+path);
        if(before.fields!=null){for(Map.Entry<String,Value> e:before.fields.entrySet())preserve(e.getValue(),after.get(e.getKey()),path.isEmpty()?e.getKey():path+"."+e.getKey(),added,approved);return;}
        need(Arrays.equals(before.bytes,after.bytes),"EXISTING_FIELD_CHANGED_"+path);
    }
}
