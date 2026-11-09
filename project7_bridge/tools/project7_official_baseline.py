#!/usr/bin/env python3
"""Reconstruct exact official640 NXPK from the pinned original APK and fixed entry patch.
Only binary packed-entry copying/deltas; no network or game bytecode execution.
"""
from __future__ import annotations
import _bootstrap  # noqa: E402,F401
import argparse,hashlib,io,json,os,pathlib,struct,tempfile,zipfile,zlib
from _bootstrap import ROOT
DEFAULT_COMPONENT=ROOT/'project7_bridge/runtime/project7_official_baseline/official640-entry-patch.zip'
COMPONENT_SHA256='30294d1b11b372a7b675880e324e9927555d9f2711d9ff9240f3bfcb274f286f'
APK_SHA256='12e57f77059f7f3964585f3a615410f3f9625101d885883cd4de4397f490c503'
BASE_SHA256='7a409a0defb6005877b5d325bcd4a5e62ccc6a1f03248a04c32ec5e7be1de1e6'
TARGET_SHA256='9284e0e00e18a04cb6169e5bbffbec3fd23037fa7dd19893fea3a3510ea1bb06'
HEADER=struct.Struct('<4s5I');ENTRY=struct.Struct('<7I')
MAX_NPK=128*1024*1024;MAX_ENTRY=16*1024*1024;MAX_COMPONENT=16*1024*1024;MAX_MANIFEST=32*1024*1024;MAX_COUNT=100000

def need(ok,message):
    if not ok:raise ValueError(message)
def sha(data):return hashlib.sha256(data).hexdigest()
def desc(data):return {'bytes':len(data),'sha256':sha(data)}
def check(data,expected):
    need(isinstance(expected,dict) and set(expected)=={'bytes','sha256'} and type(expected['bytes']) is int and expected['bytes']>=0 and isinstance(expected['sha256'],str) and len(expected['sha256'])==64 and all(c in '0123456789abcdef' for c in expected['sha256']),'invalid size/hash descriptor')
    need(desc(data)==expected,'size/hash mismatch')
def compact(obj):return json.dumps(obj,sort_keys=True,separators=(',',':')).encode('ascii')
def read_limited(path,limit):
    path=pathlib.Path(path);need(path.is_file() and path.stat().st_size<=limit,'input missing or exceeds limit')
    with path.open('rb') as f:data=f.read(limit+1)
    need(len(data)<=limit,'input grew beyond limit');return data

def bounded_zlib(data,size,limit):
    need(type(size) is int and 0<=size<=limit,'decompression size bound')
    obj=zlib.decompressobj();raw=obj.decompress(data,size+1)
    need(len(raw)==size and obj.eof and not obj.unconsumed_tail and not obj.unused_data,'invalid/truncated/trailing/oversize zlib')
    return raw

def safe_name(name):
    need(isinstance(name,str) and bool(name) and '\\' not in name and not name.startswith('/') and all(p not in ('','.','..') for p in name.split('/')),'unsafe ZIP member path')

def zip_members(z,limit):
    infos=z.infolist();need(len(infos)==len({i.filename for i in infos}),'duplicate ZIP member')
    for i in infos:
        safe_name(i.filename[:-1] if i.is_dir() else i.filename)
        need(i.compress_type in (zipfile.ZIP_STORED,zipfile.ZIP_DEFLATED) and not i.flag_bits&1 and i.file_size<=limit and ((i.external_attr>>16)&0o170000) in (0,0o100000,0o040000),'unsupported ZIP member')
    return {i.filename for i in infos}

def layout_rows(layout,size):
    need(len(layout)>=28 and type(size) is int and 28<=size<=MAX_NPK,'NPK/header size bound')
    magic,count,a,b,version,table=HEADER.unpack_from(layout)
    need(magic==b'NXPK' and (a,b,version)==(0,0,2) and 0<count<=MAX_COUNT and table>=28 and table+count*28==size and len(layout)==28+count*28,'unsupported NPK layout')
    rows=[ENTRY.unpack_from(layout,28+i*28) for i in range(count)]
    need(len({r[0] for r in rows})==count,'duplicate FID')
    for r in rows:need(28<=r[1]<=r[1]+r[2]<=table and r[2]<=MAX_ENTRY and r[3]<=MAX_ENTRY and r[6] in (0,1,2),'invalid entry bounds/flags')
    spans=sorted((r[1],r[1]+r[2]) for r in rows)
    need(all(a[1]<=b[0] for a,b in zip(spans,spans[1:])),'overlapping entries')
    return rows,table

def parse_npk(data):
    need(28<=len(data)<=MAX_NPK,'NPK size bound')
    table=HEADER.unpack_from(data)[-1];need(28<=table<=len(data),'NPK index offset')
    layout=data[:28]+data[table:];rows,table=layout_rows(layout,len(data));cursor=28
    for start,end in sorted((r[1],r[1]+r[2]) for r in rows):
        need(not any(data[cursor:start]),'nonzero layout padding/gap');cursor=end
    need(not any(data[cursor:table]),'nonzero trailing payload padding/gap')
    return rows,{r[0]:(r,data[r[1]:r[1]+r[2]]) for r in rows},layout

def _make_patch(base,target):
    """Generic binary core for maintainer and toy tests; public producer pins real inputs."""
    br,bm,bl=parse_npk(base);tr,tm,tl=parse_npk(target);records=[];blobs={};changes=0;metadata_changes=0
    for row in tr:
        fid=row[0];payload=tm[fid][1];old=bm.get(fid);record={'fid':fid,'base':desc(old[1]) if old else None,'target':desc(payload)}
        if old is not None and old[1]==payload:record['kind']='copy'
        else:
            name=f'payload/{fid:08x}.zlib';record['blob']=name
            if old is None:record['kind']='literal-zlib';packed=zlib.compress(payload,9)
            else:
                record['kind']='xor-zlib';packed=zlib.compress(bytes(v^(old[1][i] if i<len(old[1]) else 0) for i,v in enumerate(payload)),9);changes+=1
            record['stored']=desc(packed);blobs[name]=packed
        if old is not None and row[2:]!=old[0][2:]:metadata_changes+=1
        records.append(record)
    layout=zlib.compress(tl,9)
    manifest={'format':'project7-official640-entry-patch-v1','source_apk_sha256':APK_SHA256,'base':desc(base),'target':desc(target),'base_table':desc(bl[28:]),'target_table':desc(tl[28:]),'layout':{'raw':desc(tl),'stored':desc(layout)},'removed_fids':sorted(set(bm)-set(tm)),'records':records,'statistics':{'base_entries':len(br),'target_entries':len(tr),'copied_payloads':sum(r['kind']=='copy' for r in records),'changed_payloads':changes,'metadata_changed':metadata_changes,'added_fids':sorted(set(tm)-set(bm)),'removed_fids':sorted(set(bm)-set(tm)),'delta_payload_bytes':sum(len(b) for b in blobs.values())}}
    raw_manifest=compact(manifest);need(len(raw_manifest)<=MAX_MANIFEST,'manifest bound');stored_manifest=zlib.compress(raw_manifest,9)
    output=io.BytesIO()
    with zipfile.ZipFile(output,'w',compression=zipfile.ZIP_STORED) as z:
        for name,b in [('manifest.zlib',stored_manifest),('manifest-size.txt',str(len(raw_manifest)).encode('ascii')),('layout.zlib',layout),*sorted(blobs.items())]:
            i=zipfile.ZipInfo(name,(1980,1,1,0,0,0));i.external_attr=0o100600<<16;z.writestr(i,b)
    capsule=output.getvalue();need(len(capsule)<=MAX_COMPONENT,'component size bound');return capsule,manifest

def _restore(base,component,expected_component_sha256):
    need(len(component)<=MAX_COMPONENT and sha(component)==expected_component_sha256,'component SHA mismatch')
    br,bm,bl=parse_npk(base)
    with zipfile.ZipFile(io.BytesIO(component)) as z:
        names=zip_members(z,MAX_COMPONENT);need({'manifest.zlib','manifest-size.txt','layout.zlib'}<=names,'missing component metadata')
        size_text=z.read('manifest-size.txt');need(len(size_text)<=9 and size_text.isdigit(),'invalid manifest size')
        manifest=json.loads(bounded_zlib(z.read('manifest.zlib'),int(size_text),MAX_MANIFEST))
        need(manifest['format']=='project7-official640-entry-patch-v1' and manifest['source_apk_sha256']==APK_SHA256,'unsupported component format')
        check(base,manifest['base']);check(bl[28:],manifest['base_table'])
        packed_layout=z.read('layout.zlib');check(packed_layout,manifest['layout']['stored']);layout=bounded_zlib(packed_layout,manifest['layout']['raw']['bytes'],28+MAX_COUNT*28);check(layout,manifest['layout']['raw']);check(layout[28:],manifest['target_table'])
        rows,table=layout_rows(layout,manifest['target']['bytes']);target_map={r[0]:r for r in rows};records=manifest['records']
        need(isinstance(records,list) and all(type(r['fid']) is int and 0<=r['fid']<=0xffffffff for r in records) and all(type(fid) is int and 0<=fid<=0xffffffff for fid in manifest['removed_fids']),'invalid FID type/range')
        need(len(records)==len(rows) and len({r['fid'] for r in records})==len(records) and {r['fid'] for r in records}==set(target_map),'duplicate/missing/extra record FID')
        need(manifest['removed_fids']==sorted(set(bm)-set(target_map)),'removed FID mismatch')
        blob_names=[r['blob'] for r in records if 'blob' in r];need(len(blob_names)==len(set(blob_names)) and names=={'manifest.zlib','manifest-size.txt','layout.zlib'}|set(blob_names),'unsupported/duplicate/unlisted member')
        result=bytearray(manifest['target']['bytes']);result[:28]=layout[:28]
        for r in records:
            fid=r['fid'];row=target_map[fid];old=bm.get(fid);kind=r['kind'];need(r['target']['bytes']==row[2],'target entry payload size mismatch')
            if old is None:need(r['base'] is None and kind=='literal-zlib','added entry must be explicit literal');baseline=b''
            else:check(old[1],r['base']);baseline=old[1];need(kind in ('copy','xor-zlib'),'existing entry requires original baseline')
            if kind=='copy':need('blob' not in r and r['base']==r['target'],'invalid copy record');payload=baseline
            else:
                safe_name(r['blob']);need(r['blob']==f'payload/{fid:08x}.zlib','unexpected payload path');packed=z.read(r['blob']);check(packed,r['stored']);raw=bounded_zlib(packed,row[2],MAX_ENTRY)
                payload=raw if kind=='literal-zlib' else bytes(v^(baseline[i] if i<len(baseline) else 0) for i,v in enumerate(raw))
            check(payload,r['target']);result[row[1]:row[1]+row[2]]=payload
        result[table:]=layout[28:];result=bytes(result);check(result,manifest['target']);parse_npk(result)
    return result,manifest

def apk_script(path):
    path=pathlib.Path(path)
    with path.open('rb') as f:
        before=os.fstat(f.fileno());need(hashlib.file_digest(f,'sha256').hexdigest()==APK_SHA256,'unsupported original APK SHA');f.seek(0)
        with zipfile.ZipFile(f) as z:
            zip_members(z,2**31);entry=z.getinfo('assets/script.npk');need(entry.file_size<=MAX_NPK,'script member bound')
            with z.open(entry) as member:data=member.read(MAX_NPK+1)
        after=os.fstat(f.fileno());need((before.st_dev,before.st_ino,before.st_size,before.st_mtime_ns)==(after.st_dev,after.st_ino,after.st_size,after.st_mtime_ns),'APK changed during read')
    need(len(data)==62547912 and sha(data)==BASE_SHA256,'unsupported original script SHA/size');return data

def publish_new(path,data):
    path=pathlib.Path(path);need(not path.exists() and not path.is_symlink(),'output exists');path.parent.mkdir(parents=True,exist_ok=True)
    fd,temp=tempfile.mkstemp(prefix='.'+path.name+'-',suffix='.part',dir=path.parent)
    try:
        with os.fdopen(fd,'wb') as f:f.write(data);f.flush();os.fsync(f.fileno())
        # Atomic create-if-absent on the same filesystem, never replacing a racing output.
        os.link(temp,path)
    finally:
        os.unlink(temp)

def produce(official_apk,official640,output):
    output=pathlib.Path(output);need(not output.exists() and not output.is_symlink(),'output exists');base=apk_script(official_apk);target=read_limited(official640,MAX_NPK);need(sha(target)==TARGET_SHA256,'unsupported official640 SHA')
    patch,manifest=_make_patch(base,target);rebuilt,_=_restore(base,patch,sha(patch));need(rebuilt==target,'producer independent target bytes mismatch');publish_new(output,patch)
    return {'component':desc(patch),'statistics':manifest['statistics'],'layout_stored':manifest['layout']['stored'],'target':desc(target)}

def reconstruct(official_apk,output,component=DEFAULT_COMPONENT):
    output=pathlib.Path(output);need(not output.exists() and not output.is_symlink(),'output exists');patch=read_limited(component,MAX_COMPONENT);need(sha(patch)==COMPONENT_SHA256,'component SHA mismatch')
    base=apk_script(official_apk);result,manifest=_restore(base,patch,COMPONENT_SHA256);need(sha(result)==TARGET_SHA256,'official640 target pin mismatch');publish_new(output,result)
    return {'output':str(output),'bytes':len(result),'sha256':sha(result),'component_sha256':sha(patch),'statistics':manifest['statistics']}

def main():
    p=argparse.ArgumentParser(description=__doc__);sub=p.add_subparsers(dest='command',required=True)
    for name in ['produce','reconstruct']:
        a=sub.add_parser(name);a.add_argument('--official-apk',required=True,type=pathlib.Path);a.add_argument('--output',required=True,type=pathlib.Path)
        if name=='produce':a.add_argument('--official640',required=True,type=pathlib.Path)
        else:a.add_argument('--component',type=pathlib.Path,default=DEFAULT_COMPONENT)
    a=p.parse_args();kw=vars(a);cmd=kw.pop('command');print(json.dumps((produce if cmd=='produce' else reconstruct)(**kw),indent=2))
if __name__=='__main__':main()
