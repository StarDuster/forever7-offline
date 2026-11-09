#!/usr/bin/env python3
"""Generate a fixed Project7 six-field resource snapshot from local pinned checks.
No network, game execution, resource reconstruction, or APK assembly.
"""
from __future__ import annotations
import _bootstrap  # noqa: E402,F401
import argparse, hashlib, json, pathlib, re, struct, zlib
from _bootstrap import ROOT
PINS={'source_manifest':'421dd73952cdc4903a52c2f91f0283401b56acbb293a4cf693e149db612e3082','resource_manifest':'c2e926909541ea2070f58a3b5c702c8989c10db081d299abb6f1fc193ec8ae4f','source_plan':'26c20ff443c2c5f26e9e1302f23fd7178ad5257e366b141dd13ef9d903319efa','base_script':'9284e0e00e18a04cb6169e5bbffbec3fd23037fa7dd19893fea3a3510ea1bb06'}
MAX_CHECK=64*1024*1024; PART=re.compile(r'[a-z][a-z0-9_]*\Z'); MD5=re.compile(r'[0-9a-f]{32}\Z'); SHA=re.compile(r'[0-9a-f]{64}\Z')
def need(ok,message):
    if not ok:raise ValueError(message)
def sha(b):return hashlib.sha256(b).hexdigest()
def desc(b):return {'bytes':len(b),'sha256':sha(b)}
def compact(obj):return json.dumps(obj,ensure_ascii=True,separators=(',',':')).encode('ascii')
def load_pinned(path,key):
    path=regular(path);need(path.stat().st_size<=(MAX_CHECK if key=='base_script' else 4*1024*1024),'pinned source size bound');b=path.read_bytes();need(sha(b)==PINS[key],key+' SHA mismatch');return b

def integer(s,maximum=2**63-1):
    need(bool(re.fullmatch(r'0|[1-9][0-9]*',s)),'invalid unsigned integer');v=int(s);need(v<=maximum,'integer overflow');return v

def parse_version(data):
    text=data.decode('ascii');need(bool(text.strip()),'empty manifest');packs=[];manifest={};versions=set()
    for line in text.splitlines():
        need(bool(line) and line.count('=')==1,'invalid manifest line');name,spec=line.split('=')
        if name.isdecimal():
            version=integer(name,2**32-1);need(version not in versions,'duplicate version');versions.add(version);items=[];parts=set()
            for item in spec.split():
                fields=item.split(':');need(len(fields)==3,'invalid payload');part,md5,size=fields
                need(bool(PART.fullmatch(part)) and bool(MD5.fullmatch(md5)) and part not in parts,'invalid/duplicate pack part');parts.add(part);items.append([part,md5,integer(size)])
            need(bool(items),'empty pack');packs.append([version,items])
        else:
            need(bool(PART.fullmatch(name)) and name not in manifest,'invalid/duplicate manifest part');fields=spec.split();need(len(fields)==2 and fields[0] in ('1','2'),'unknown part type');pair=fields[1].split(':');need(len(pair)==2 and bool(MD5.fullmatch(pair[0])),'invalid check pin');manifest[name]=[int(fields[0]),[pair[0],integer(pair[1])]]
    need(bool(packs) and bool(manifest),'empty manifest section')
    need(all(p in manifest for _,rows in packs for p,_,_ in rows),'unknown payload part')
    return packs,manifest

def unpack_check(packed):
    need(0<len(packed)<=MAX_CHECK,'compressed check bound');d=zlib.decompressobj();raw=d.decompress(packed,MAX_CHECK+1)
    need(len(raw)<=MAX_CHECK and d.eof and not d.unconsumed_tail and not d.unused_data,'invalid/truncated/oversize check zlib')
    need(bool(raw),'empty check');return raw.decode('ascii')

def convert_check(part,kind,packed,payload_sizes):
    need(bool(PART.fullmatch(part)) and kind in (1,2),'unknown part/type')
    grouped={};seen=set();rows=unpack_check(packed).splitlines();need(bool(rows),'empty check')
    for line in rows:
        f=line.split();need(len(f)==(5 if part=='raw' else 8),'truncated/unknown check record')
        if part=='raw':
            name,md5,size,ver,offset=f;name=name.removeprefix('res/');need(name.startswith('sound/') and '\\' not in name and all(x not in ('','.','..') for x in name.split('/')),'unsafe raw name');key=name;size=integer(size);ver=integer(ver,2**32-1);offset=integer(offset);info=[name,md5,size,offset]
        else:
            fid,md5,csize,chash,usize,uhash,ver,offset=f;key=integer(fid,2**32-1);size=integer(csize,2**32-1);ver=integer(ver,2**32-1);offset=integer(offset);info=[key,md5,size,integer(chash,2**32-1),integer(usize,2**32-1),integer(uhash,2**32-1),offset]
        need(bool(MD5.fullmatch(md5)) and key not in seen,'bad md5/duplicate record');seen.add(key)
        need(ver in payload_sizes and offset+size<=payload_sizes[ver],'unknown version or out-of-bounds slice')
        grouped.setdefault(ver,[]).append(info)
    return [[v,info] for v,info in grouped.items()],len(seen)

def entries_fingerprint(entries):
    names=[e['name'] for e in entries];need(len(names)==len(set(names)) and bool(names),'duplicate/empty outputs')
    for e in entries:need(bool(SHA.fullmatch(e['sha256'])) and e['bytes']>0 and not e['name'].startswith('/') and all(x not in ('','.','..') for x in e['name'].split('/')),'invalid resource output')
    return sha(''.join(f"{e['name']}\t{e['bytes']}\t{e['sha256']}\n" for e in sorted(entries,key=lambda e:e['name'])).encode('ascii'))

def regular(path):
    path=pathlib.Path(path);need(path.absolute()==path.resolve() and path.is_file(),'not a canonical regular source');return path

def generate(source_manifest,resource_manifest,source_plan,cache,base_script,overlay,output):
    output=pathlib.Path(output);need(not output.exists(),'output exists')
    source=load_pinned(source_manifest,'source_manifest');resources=load_pinned(resource_manifest,'resource_manifest');plan_bytes=load_pinned(source_plan,'source_plan');base=load_pinned(base_script,'base_script');overlay_path=regular(overlay);need(overlay_path.stat().st_size==1454700,'overlay size mismatch');overlay_bytes=overlay_path.read_bytes()
    # Fixed component-derived script overlay is independently pinned in the stage report.
    from project7_component import COMPONENT_SHA256, npk
    need(desc(overlay_bytes)=={'bytes':1454700,'sha256':'3e0d06ef611167c2e9917d87272eb143c3fb6d8118957be286e3809b19def061'},'overlay pin mismatch')
    parsed_overlay=npk(overlay_bytes);need(0x35e8062b in parsed_overlay and sha(parsed_overlay[0x35e8062b][1])=='cd75d9d1be2c7672588283032ae99d7a9145bcc3a2feef6809d696dbf6344f82','pconst binding mismatch')
    packs,manifest=parse_version(source);plan=json.loads(plan_bytes);rm=json.loads(resources);need(plan['version']==640 and plan['platform']=='android','wrong plan')
    selected=plan['parts'];need(len(selected)==37 and len({p['part'] for p in selected})==37 and set(manifest)-{p['part'] for p in selected}=={'script'},'wrong selected coverage')
    published={(p,v):(md5,size) for v,items in packs for p,md5,size in items};parts=[];audit=[];total=0;raw_count=0
    for p in selected:
        part=p['part'];c=p['check'];kind,pin=manifest[part]
        need(pin==[c['md5'],c['size']] and kind==c['part_type'] and bool(SHA.fullmatch(p['check_sha256'])),'check manifest mismatch')
        sizes={}
        for row in p['payloads']:
            m=re.fullmatch(r'patch2\.android\.640/([0-9]+)/'+re.escape(part)+r'\.data',row['path']);need(m is not None,'payload path mismatch');v=integer(m[1],2**32-1);need(v not in sizes and published.get((part,v))==(row['md5'],row['size']),'duplicate/unknown payload version');sizes[v]=row['size']
        path=pathlib.Path(cache)/'objects'/c['md5']
        if not path.exists():path=pathlib.Path(cache)/c['path']
        path=regular(path);need(path.stat().st_size==c['size'] and c['size']<=MAX_CHECK,'compressed check size mismatch');b=path.read_bytes();need(len(b)==c['size'] and hashlib.md5(b).hexdigest()==c['md5'] and sha(b)==p['check_sha256'],'check SHA/MD5/size mismatch')
        versions,count=convert_check(part,kind,b,sizes);need(count==p['files'],'source plan record count mismatch');parts.append([part,versions]);total+=count
        if part=='raw':raw_count=count
        audit.append({'part':part,'path':str(path),'bytes':len(b),'md5':c['md5'],'sha256':sha(b),'records':count,'versions':len(versions)})
    expected_entries=plan['npk_output_manifest']['entries']+[{'name':x['path'].removeprefix('res/'),'bytes':x['size'],'sha256':x['sha256']} for x in plan['raw_files']]
    need(sorted(rm['entries'],key=lambda x:x['name'])==sorted(expected_entries,key=lambda x:x['name']) and rm['files']==312 and len(rm['entries'])==312,'resource manifest mismatch')
    raw_records={info[0]:info for part,vs in parts if part=='raw' for _,items in vs for info in items}
    for r in plan['raw_files']:need(raw_records.get(r['path'].removeprefix('res/'))==[r['path'].removeprefix('res/'),r['md5'],r['size'],r['offset']],'raw plan mismatch')
    need(len(packs)==191 and len(manifest)==38 and total==199853 and raw_count==276,'fixed coverage mismatch')
    snapshot=compact({'schema':1,'version':455,'platform':'android','parts':parts,'packs':packs,'manifest':manifest});need(len(snapshot)<=MAX_CHECK,'snapshot limit')
    contract={'schema':'project7-resource-binding-v1','clientVersion':455,'resourceVersion':640,'platform':'android','sourceManifestSha256':PINS['source_manifest'],'resourceManifestSha256':PINS['resource_manifest'],'sourcePlanSha256':PINS['source_plan'],'entryManifestSha256':entries_fingerprint(rm['entries']),'entryCount':312,'snapshotAsset':'project7-resource-snapshot.json','snapshotBytes':len(snapshot),'snapshotSha256':sha(snapshot),'componentSha256':COMPONENT_SHA256,'scripts':[{'name':'assets/script.npk',**desc(base)},{'name':'assets/project7_local.npk',**desc(overlay_bytes)}],'pconst':{'fid':'35e8062b','packedSha256':sha(parsed_overlay[0x35e8062b][1]),'clientVersion':455},'counts':{'parts':37,'packs':191,'manifest':38,'records':total,'npkParts':36,'npkRecords':total-raw_count,'rawFiles':raw_count}}
    contract_bytes=compact(contract);output.mkdir(mode=0o700,parents=True)
    for n,b in [('project7-resource-snapshot.json',snapshot),('project7-resource-binding.json',contract_bytes),('check-provenance.json',json.dumps(audit,indent=2).encode()+b'\n')]:
        (output/n).write_bytes(b);(output/n).chmod(0o600)
    return {'output':str(output),'snapshot':desc(snapshot),'contract':desc(contract_bytes),'counts':contract['counts'],'checks':audit,'entryManifestSha256':contract['entryManifestSha256'],'expected_size_evidence':17437832,'size_matches_prior_evidence':len(snapshot)==17437832}

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--source-manifest',type=pathlib.Path,default=ROOT/'upstream/project7/provenance/patch2.android.640.version');p.add_argument('--resource-manifest',type=pathlib.Path,default=ROOT/'offline/current/java/android_resource_init/resource_manifest.json');p.add_argument('--source-plan',type=pathlib.Path,default=ROOT/'reports/official-asset-source-plan.json');p.add_argument('--cache',type=pathlib.Path,default=ROOT/'originals/cdn');p.add_argument('--base-script',type=pathlib.Path,default=ROOT/'analysis/private-project-build/script640-original.npk');p.add_argument('--overlay',type=pathlib.Path,default=ROOT/'analysis/project7/fixed-component-v2-stage/project7-script-overlay.npk');p.add_argument('--output',type=pathlib.Path,default=ROOT/'analysis/project7/resource-snapshot');a=p.parse_args();print(json.dumps(generate(**vars(a)),indent=2))
if __name__=='__main__':main()
