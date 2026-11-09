#!/usr/bin/env python3
"""Pinned Project7 static capsule producer/consumer. Never builds or executes APKs."""
from __future__ import annotations
import _bootstrap  # noqa: E402,F401
import argparse, hashlib, json, pathlib, struct, zipfile, zlib

PINS = {'official_apk':'12e57f77059f7f3964585f3a615410f3f9625101d885883cd4de4397f490c503', 'game':'17d93b3cba528b6da7ad94e9e0ed4def92f45ea94e16c85c72919c8ae6c699e8', 'manager':'0dcfbfa15141c0c2fca06ba8cede5b36492c7b1c60985e84b8c21923513c6c01', 'official640':'9284e0e00e18a04cb6169e5bbffbec3fd23037fa7dd19893fea3a3510ea1bb06'}
COMPONENT_SHA256='ccbde188251c68eb23a4af1d0b6aef1946236d527d2a70f30058277e5a7b7a0d'
HEADER=struct.Struct('<4s5I'); ENTRY=struct.Struct('<7I'); LIMIT=128*1024*1024
DEXES=['classes.dex']+[f'classes{i}.dex' for i in range(2,6)]
def sha(b): return hashlib.sha256(b).hexdigest()
def descriptor(b): return {'size':len(b),'sha256':sha(b)}
def require(ok, message):
    if not ok: raise ValueError(message)
def check(b, d): require(descriptor(b)==d,'size/hash mismatch')
def pinned(path,key):
    b=pathlib.Path(path).read_bytes(); require(sha(b)==PINS[key],f'unsupported {key} SHA'); return b

def safe_name(name):
    require(isinstance(name,str) and name and '\\' not in name and not name.startswith('/') and all(x not in ('','.','..') for x in name.split('/')), 'unsafe member path')
    return name

def members(z, limit=LIMIT):
    names=z.namelist(); require(len(names)==len(set(names)), 'duplicate ZIP member')
    for n in names:
        safe_name(n.rstrip('/')); i=z.getinfo(n)
        require(not i.flag_bits&1 and i.file_size<=limit and i.compress_type in (zipfile.ZIP_STORED,zipfile.ZIP_DEFLATED) and ((i.external_attr >> 16) & 0o170000) in (0,0o100000,0o040000),'unsupported/encrypted/oversize member')
    return names

def delta(base,target):
    require(max(len(base),len(target))<=LIMIT,'delta too large')
    return zlib.compress(bytes(v ^ (base[i] if i<len(base) else 0) for i,v in enumerate(target)),9)
def restore(base, packed, size):
    require(type(size) is int and 0<=size<=LIMIT,'invalid delta size')
    d=zlib.decompressobj(); raw=d.decompress(packed,size+1)
    require(len(raw)==size and d.eof and not d.unused_data and not d.unconsumed_tail,'invalid/bounded zlib stream')
    return bytes(v ^ (base[i] if i<len(base) else 0) for i,v in enumerate(raw))

def npk(data):
    require(len(data)>=28,'short NXPK'); magic,n,a,b,v,table=HEADER.unpack_from(data)
    require(magic==b'NXPK' and (a,b,v)==(0,0,2) and table>=28 and table+n*28==len(data),'unsupported NXPK')
    rows=[ENTRY.unpack_from(data,table+i*28) for i in range(n)]
    require(len({r[0] for r in rows})==n,'duplicate FID')
    for r in rows: require(28<=r[1]<=r[1]+r[2]<=table and r[3]<=LIMIT and r[6] in (0,1,2),'invalid NXPK entry')
    spans=sorted((r[1],r[1]+r[2]) for r in rows)
    require(all(x[1]<=y[0] for x,y in zip(spans,spans[1:])),'overlapping NXPK')
    return {r[0]:(r,data[r[1]:r[1]+r[2]]) for r in rows}
def overlay(rows):
    out=bytearray(b'\0'*28); index=[]
    for row,payload in rows:
        index.append((row[0],len(out),*row[2:])); out.extend(payload); out.extend(b'\0'*(-len(out)%4))
    table=len(out)
    for r in index: out.extend(ENTRY.pack(*r))
    out[:24]=HEADER.pack(b'NXPK',len(index),0,0,2,table)
    return bytes(out)

def produce(official_apk,official640,game,manager,output):
    import io
    output=pathlib.Path(output); require(not output.exists(),'output exists')
    original=pinned(official_apk,'official_apk'); base_script=pinned(official640,'official640')
    target=pinned(game,'game'); mgr=pinned(manager,'manager')
    blobs={}; records=[]
    def add(path,kind,b,t,**extra):
        blob=f'payload/{len(records):03d}.bin'; packed=delta(b,t) if kind=='xor-zlib' else t
        blobs[blob]=packed; records.append({'path':path,'kind':kind,'base':descriptor(b),'target':descriptor(t),'blob':blob,'stored':descriptor(packed),**extra})
    with zipfile.ZipFile(io.BytesIO(original)) as oz,zipfile.ZipFile(io.BytesIO(target)) as tz,zipfile.ZipFile(io.BytesIO(mgr)) as mz:
        members(oz,2**31);members(tz,2**31);mn=members(mz)
        for name in DEXES: add(name,'xor-zlib',oz.read(name),tz.read(name),role='game-dex',source='game:'+name)
        add('assets/neox.xml','xor-zlib',oz.read('assets/neox.xml'),tz.read('assets/neox.xml'),role='game-config',source='game:assets/neox.xml')
        bm=npk(base_script); tm=npk(tz.read('assets/project7_local.npk'))
        require(set(bm)==set(tm),'changed FID universe')
        changed=[fid for fid in sorted(tm) if bm[fid][1]!=tm[fid][1] or bm[fid][0][2:]!=tm[fid][0][2:]]
        require(len(changed)==20,'unsupported changed script count')
        for fid in changed:
            row,t=tm[fid]; add(f'script/{fid:08x}','xor-zlib',bm[fid][1],t,fid=fid,entry=list(row),base_entry=list(bm[fid][0]),role='game-script',source=f'game:assets/project7_local.npk#{fid:08x}')
        add('classes7.dex','literal',b'',mz.read('classes.dex'),role='manager-dex',source='manager:classes.dex')
        assets=sorted(n for n in mn if n.startswith('assets/') and not n.endswith('/'))
        require(len(assets)==63,'unsupported bundled assets')
        for name in assets: add(name,'literal',b'',mz.read(name),role='manager-asset',source='manager:'+name)
    manifest={'format':'project7-fixed-component-v2','min_api':26,'pins':PINS,'records':records,'scope':'5 game DEX deltas,1 game neox.xml delta,20 packed NXPK deltas,unchanged manager DEX and 63 APK-bundled public assets; no private state'}
    with zipfile.ZipFile(output,'x',compression=zipfile.ZIP_STORED) as z:
        for name,b in [('manifest.json',json.dumps(manifest,sort_keys=True,separators=(',',':')).encode()),*sorted(blobs.items())]:
            i=zipfile.ZipInfo(name,(1980,1,1,0,0,0));i.external_attr=0o100600<<16;z.writestr(i,b)
    return descriptor(output.read_bytes())

def materialize(component,official_apk,official640,expected_sha256=None):
    import io
    capsule=pathlib.Path(component).read_bytes()
    require(sha(capsule)==(expected_sha256 or COMPONENT_SHA256),'component SHA mismatch')
    original=pinned(official_apk,'official_apk'); script=pinned(official640,'official640'); bm=npk(script)
    result={}; script_rows=[]
    with zipfile.ZipFile(io.BytesIO(capsule)) as z,zipfile.ZipFile(io.BytesIO(original)) as oz:
        names=members(z); members(oz,2**31)
        require(z.getinfo('manifest.json').file_size<1024*1024,'manifest too large')
        m=json.loads(z.read('manifest.json')); require(m['format']=='project7-fixed-component-v2' and m['pins']==PINS and m['min_api']==26,'unsupported manifest')
        records=m['records'];require(len(records)==90,'unsupported record count')
        require(set(names)=={'manifest.json'}|{r['blob'] for r in records} and len({r['blob'] for r in records})==len(records),'unsupported members')
        require(len({r['path'] for r in records})==len(records),'duplicate output')
        for r in records:
            path=safe_name(r['path']);safe_name(r['blob']); packed=z.read(r['blob']);check(packed,r['stored'])
            if path in DEXES or path=='assets/neox.xml':
                require(r['kind']=='xor-zlib' and r['role']==('game-config' if path=='assets/neox.xml' else 'game-dex'),'game member must be role-pinned delta');base=oz.read(path)
            elif path.startswith('script/'):
                fid=r['fid']; require(path==f'script/{fid:08x}' and fid in bm and r['base_entry']==list(bm[fid][0]),'wrong NXPK baseline');base=bm[fid][1]
                require(r['role']=='game-script' and r['entry'][0]==fid and len(r['entry'])==7 and r['entry'][6] in (0,1,2) and r['entry'][3]<=LIMIT and r['kind']=='xor-zlib','invalid NXPK metadata')
            else:
                require((path=='classes7.dex' and r['role']=='manager-dex') or (path.startswith('assets/') and r['role']=='manager-asset'),'unsupported output');require(r['kind']=='literal','unsupported codec');base=b''
            check(base,r['base']);t=restore(base,packed,r['target']['size']) if r['kind']=='xor-zlib' else packed;check(t,r['target'])
            if path.startswith('script/'):
                require(r['entry'][2]==len(t),'NXPK payload length');script_rows.append((r['entry'],t))
            else: result[path]=t
        require(len(script_rows)==20 and set(DEXES)<=set(result) and len([p for p in result if p.startswith('assets/')])==64 and 'assets/neox.xml' in result and 'classes7.dex' in result,'unsupported partition')
        require(result['classes7.dex'][:8]==b'dex\n038\0','manager DEX038 required')
    result['project7-script-overlay.npk']=overlay(script_rows);npk(result['project7-script-overlay.npk'])
    return m,result

def apply(component,official_apk,official640,output,expected_sha256=None):
    output=pathlib.Path(output);require(not output.exists(),'output exists')
    m,files=materialize(component,official_apk,official640,expected_sha256)
    output.mkdir(mode=0o700,parents=True)
    for name,b in sorted(files.items()):
        p=output/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b);p.chmod(0o600)
    report={'format':'project7-stage-v1','min_api':26,'component':descriptor(pathlib.Path(component).read_bytes()),'inputs':{'official_apk':PINS['official_apk'],'official640':PINS['official640']},'files':[{'path':n,**descriptor(b)} for n,b in sorted(files.items())]}
    (output/'stage-manifest.json').write_text(json.dumps(report,indent=2)+'\n');return report

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('command',choices=['produce','verify','apply']);p.add_argument('--component',type=pathlib.Path);p.add_argument('--official-apk',required=True,type=pathlib.Path);p.add_argument('--official640',required=True,type=pathlib.Path);p.add_argument('--game',type=pathlib.Path);p.add_argument('--manager',type=pathlib.Path);p.add_argument('--output',type=pathlib.Path);p.add_argument('--component-sha256');a=p.parse_args()
    if a.command=='produce': r=produce(a.official_apk,a.official640,a.game,a.manager,a.output)
    elif a.command=='apply':r=apply(a.component,a.official_apk,a.official640,a.output,a.component_sha256)
    else:
        m,f=materialize(a.component,a.official_apk,a.official640,a.component_sha256);r={'verified':True,'files':len(f),'min_api':m['min_api']}
    print(json.dumps(r,indent=2))
if __name__=='__main__':main()
