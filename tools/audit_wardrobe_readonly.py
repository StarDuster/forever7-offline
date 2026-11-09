"""Plan by default. Only the sole native actor may explicitly use --execute.

Generates 140 hero baseline + 494 skin appearance jobs without model deduplication.
No subprocess, ADB, emulator, or app call is made during plan/dry-run/tests.
"""
from __future__ import annotations
import argparse
import ast
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import struct
import zlib
import sys
import time
import uuid

ROOT=Path(__file__).resolve().parents[1]
DOCS='/sdcard/Android/data/com.netease.qrzd/files/netease/qrzd/Documents'
STATUS=DOCS+'/wardrobe_readonly_status.json'
PROBE=ROOT/'tools/wardrobe_audit/native_probe.py'
FORBIDDEN=re.compile(r'(setSkin(?:Request)?|sellSkin|buySkin|[Dd]ye|[Ww]enlu|[Aa]wake|[Pp]endant|[Aa]ward|grant|exchange)',re.I)
SEEN=frozenset(('setSkinSeen','heartbeat','heartbeatServer'))


def digest(data):return hashlib.sha256(data).hexdigest()
def dump(path,value):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(value,ensure_ascii=True,indent=2)+'\n');path.chmod(0o600)
def catalog_hashes():
    base=ROOT/'analysis/android640-scripts/com/data/cdata'
    return {name:digest((base/(name+'.marshal')).read_bytes())for name in ('hero','skin')}
def original_tables():
    sys.path[:0]=[str(ROOT/'analysis/research-agent'),str(ROOT/'tools')]
    from read_literal_marshal import read
    base=ROOT/'analysis/android640-scripts/com/data/cdata'
    return read(base/'hero.marshal'),read(base/'skin.marshal')
def make_plan(heroes,skins,hero_filter=(),skin_filter=(),limit=None,run_id=None):
    jobs=[]
    selected=set(hero_filter);selected_skins=set(skin_filter)
    for hero in sorted(heroes):
        if selected and hero not in selected:continue
        jobs.append({'job_id':'hero-%03d-baseline'%hero,'hero_id':hero,'template_id':None,'kind':'hero_current',
            'catalog_hidden_no_model':hero in (46,125)})
        for template,row in sorted(skins.items()):
            if row.get('hero')!=hero or selected_skins and template not in selected_skins:continue
            jobs.append({'job_id':'skin-%05d'%template,'hero_id':hero,'template_id':template,'kind':'skin',
                'catalog_hidden_no_model':hero in(46,125),'catalog_is_dye':bool(row.get('is_dye_skin')),
                'catalog_ori_skin':row.get('ori_skin'),'catalog_model':row.get('model_id'),'catalog_release':row.get('release')})
    if limit is not None:jobs=jobs[:limit]
    return {'protocol':1,'run_id':run_id or uuid.uuid4().hex,'denominators':{'heroes':len(heroes),'skins':len(skins),
        'dye_rows':sum(bool(r.get('is_dye_skin'))for r in skins.values())},'jobs':jobs,
        'policy':'original-ui-readonly; no collection or model deduplication; load != visual review',
        'probe_sha256':digest(PROBE.read_bytes()),'catalog_sha256':catalog_hashes()}

def parse_status(raw,run_id,job_id=None,nonce=None):
    value=json.loads(raw)
    if value.get('protocol')!=1 or value.get('run_id')!=run_id:raise ValueError('Status run/protocol mismatch')
    if job_id is not None and value.get('job_id')!=job_id:raise ValueError('Status job mismatch')
    if nonce is not None and value.get('request_nonce')!=nonce:raise ValueError('Stale command status nonce')
    if value.get('phase')not in('idle','opening','loading','ready_capture','capture_before','cleanup','paused'):raise ValueError('Unknown native phase')
    return value

def rpc_payload(text):
    try:value=json.loads(text)
    except (ValueError,TypeError):
        try:value=ast.literal_eval(text)
        except (ValueError,SyntaxError,TypeError):return None
    return value if type(value)is dict else None


def rpc_observations(text):
    events=[]
    for line in text.splitlines():
        match=re.search(r'\bRPC(?:\s+(?:BUSINESS|UNIMPLEMENTED|SKIP))*\s+([A-Za-z_][A-Za-z_0-9]*)(.*)$',line)
        if not match:continue
        name=match[1];payload=rpc_payload(match[2].strip());inner=None
        kind='bookkeeping_or_read'if name in SEEN else'forbidden'if FORBIDDEN.search(name)else'unclassified'
        if 'chat'in name.lower():kind='unclassified'
        if name=='reliableRpcCall':
            wrapper=payload.get('w')if payload else None
            if type(wrapper)is dict and type(wrapper.get('m'))is str:
                inner=wrapper['m']
                # Exact verified cleanup read only; never trust the outer wrapper.
                if (set(payload)<=set(('w','_cbid_')) and set(wrapper)==set(('m','p','r'))
                    and type(wrapper['r'])is int and inner=='pullEvents'and wrapper['p']=={}):kind='derived_event_refresh'
                elif FORBIDDEN.search(inner):kind='forbidden'
                else:kind='unclassified'
            else:kind='unclassified'
        if name=='regist_chat_channel_listener':
            if payload=={'cn':1,'scn':1} and all(type(payload[k])is int for k in('cn','scn')):kind='verified_listener_noop'
            elif (match[2].strip()==''and 'UNIMPLEMENTED'in line[:match.start(1)]
                  and events and events[-1]['method']==name and events[-1]['kind']=='verified_listener_noop'
                  and events[-1].get('diagnostic')is not True):kind='verified_listener_noop'
            else:kind='unclassified'
        events.append({'diagnostic':'UNIMPLEMENTED'in line[:match.start(1)],'method':name,'inner_method':inner,'kind':kind,'line':line})
    return events


def next_attempt(records,job_id,out):
    used=[]
    for row in records:
        if row.get('job_id')!=job_id or 'attempt'not in row:continue
        attempt=row['attempt']
        if type(attempt)is not int or attempt not in(0,1):raise ValueError('Invalid checkpoint attempt')
        used.append(attempt)
    # Interrupted runs may have artifacts but no checkpoint. Never reuse those slots.
    for attempt in range(2):
        if any((Path(out)/('%s-attempt%d.%s'%(job_id,attempt,ext))).exists()for ext in('png','log','reserved')):used.append(attempt)
    attempt=max(used,default=-1)+1
    if attempt>=2:raise RuntimeError('Retry budget exhausted; review evidence or create an explicit new run')
    return attempt


def exclusive_write(path,data):
    path=Path(path)
    with path.open('xb')as handle:handle.write(data);handle.flush();os.fsync(handle.fileno())
    path.chmod(0o600)

def png_dimensions(raw):
    if not raw.startswith(b'\x89PNG\r\n\x1a\n'):raise ValueError('Not a PNG screenshot')
    position=8;dimensions=None;image_data=False;ended=False
    while position<len(raw):
        if position+12>len(raw):raise ValueError('Truncated PNG chunk')
        size=struct.unpack('>I',raw[position:position+4])[0];kind=raw[position+4:position+8]
        end=position+12+size
        if end>len(raw):raise ValueError('Truncated PNG payload')
        payload=raw[position+8:position+8+size]
        crc=struct.unpack('>I',raw[position+8+size:end])[0]
        if zlib.crc32(kind+payload)&0xffffffff!=crc:raise ValueError('PNG checksum mismatch')
        if kind==b'IHDR':
            if dimensions is not None or size!=13 or position!=8:raise ValueError('Invalid PNG header')
            dimensions=struct.unpack('>II',payload[:8])
        if kind==b'IDAT':image_data=True
        if kind==b'IEND':ended=True;break
        position=end
    if not dimensions or not all(0<v<=16384 for v in dimensions)or not image_data or not ended:raise ValueError('Incomplete PNG screenshot')
    return list(dimensions)

def active_resolution(text):
    matches=re.findall(r'(?:Physical|Override) size:\s*(\d+)x(\d+)',text)
    if not matches:raise ValueError('Device full-window resolution unavailable')
    return [int(v)for v in matches[-1]]

def validate_frame(before,after,frame):
    if before.get('token')!=after.get('result',{}).get('token')or frame.get('token')!=before.get('token'):raise ValueError('Frame token mismatch')
    if type(before.get('generation'))is not int or before['generation']<=0 or before.get('generation')!=after.get('generation'):raise ValueError('Frame job generation changed')
    b=before['sample'];a=after['result']['after']
    if b['fingerprint']!=a['fingerprint']or b['epoch']!=a['epoch']:raise ValueError('Frame/model epoch mismatch')
    if not(frame['host_before']<=frame['host_captured']<=frame['host_after']):raise ValueError('Screenshot host time order')
    if not re.fullmatch(r'[a-f0-9]{64}',frame['sha256']):raise ValueError('Screenshot SHA missing')
    if a['time']<b['time']:raise ValueError('Native time reversed')

def summarize(records,plan):
    latest={r['job_id']:r for r in records}
    counts={};coverage={'hero_current':{},'skin':{}};kinds={job.get('job_id'):job.get('kind')for job in plan['jobs']}
    for row in latest.values():
        result=row.get('result',{});status=result.get('load_status','failed')
        if status=='loaded_unreviewed':
            verdict=row.get('visual_review',{}).get('verdict')
            if verdict=='pass':status='rendered_and_visually_reviewed'
            elif verdict=='fail':status='visual_failed'
        counts[status]=counts.get(status,0)+1
        kind=kinds.get(row['job_id'])
        if kind in coverage:coverage[kind][status]=coverage[kind].get(status,0)+1
    return {'denominators':plan['denominators'],'planned_jobs':len(plan['jobs']),'completed_jobs':len(latest),'statuses':counts,'coverage_by_kind':coverage,
        'visual_rule':'Only explicit per-item reviewer pass changes loaded_unreviewed; originals retained. No allLoaded material pass.'}

class AdbTransport:
    """Created only after explicit --execute. Argument arrays, no host shell."""
    def __init__(self,serial,adb=None):
        if not re.fullmatch(r'emulator-\d+',serial or''):raise ValueError('Explicit isolated emulator serial required')
        self.base=[str(adb or ROOT/'toolchains/android-sdk/platform-tools/adb'),'-s',serial]
    def run(self,*args,binary=False):return subprocess.check_output(self.base+list(args),text=not binary,timeout=30)
    def shell(self,*args):return self.run('shell',*args).strip()
    def read(self,path):return self.shell('cat',path)
    def submit(self,source,out):
        self.shell('test','-f',DOCS+'/offline_development.flag')
        self.shell('test','!','-e',DOCS+'/offline_probe.py')
        match=re.search(r'package:com\.netease\.qrzd uid:(\d+)',self.shell('cmd','package','list','packages','-U','com.netease.qrzd'))
        if not match:raise ValueError('Cannot identify original app UID')
        context=self.shell('ls','-Z',DOCS+'/offline_boot_probe.txt').split()[0]
        if not context.startswith('u:object_r:media_rw_data_file:s0:'):raise ValueError('Unexpected original app context')
        local=Path(out)/'submitted-probe.py';local.write_text(source,encoding='ascii');local.chmod(0o600)
        staging=DOCS+'/offline_probe.py.part'
        self.run('push',str(local),staging);self.shell('chown',match[1]+':1078',staging);self.shell('chcon',context,staging)
        self.shell('mv',staging,DOCS+'/offline_probe.py')
    def remote_sha(self,path):
        if not re.fullmatch(r'/[A-Za-z0-9_./~+=@-]+',path)or '..'in path.split('/'):raise ValueError('Unsupported remote path')
        value=self.shell('sha256sum',path).split()[0]
        if not re.fullmatch(r'[a-f0-9]{64}',value):raise ValueError('Bad device hash')
        return value
    def packaged_script_sha(self,apk):
        if not re.fullmatch(r'/[A-Za-z0-9_./~+=@-]+',apk)or '..'in apk.split('/'):raise ValueError('Unsafe APK path')
        process=subprocess.Popen(self.base+['exec-out','unzip','-p',apk,'assets/script.npk'],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        try:
            data,error=process.communicate(timeout=60)
        except subprocess.TimeoutExpired:
            process.kill();process.communicate()
            raise TimeoutError('Installed script read timed out; no native audit jobs started')
        if process.returncode or not data:raise RuntimeError('Cannot read installed assets/script.npk; actor may supply --device-script for actual deployed override: '+error.decode('utf-8','replace'))
        return digest(data)
    def provenance(self,script,gpu):
        path=self.shell('pm','path','com.netease.qrzd').splitlines()
        if len(path)!=1 or not path[0].startswith('package:'):raise ValueError('Expected one APK; splits require separate actor review')
        self.surfaceflinger_raw=self.shell('dumpsys','SurfaceFlinger')
        renderer_lines=[line.strip()for line in self.surfaceflinger_raw.splitlines()if 'GLES:'in line or 'OpenGL ES'in line]
        return {'apk_sha256':self.remote_sha(path[0][8:]),'script_sha256':self.remote_sha(script)if script else self.packaged_script_sha(path[0][8:]),
            'script_device_path':script or 'installed-apk:assets/script.npk','gpu_actor_supplied':gpu,'device':self.shell('getprop','ro.hardware'),
            'resolution':self.shell('wm','size'),'surfaceflinger_renderer_lines':renderer_lines,'gpu_readback_unavailable':not bool(renderer_lines)}

def source_call(method,*args,nonce=None):
    if method not in ('start','checkpoint','inventory'):raise ValueError('Unsupported audit command')
    payload=json.dumps(list(args),ensure_ascii=True)
    return "import gg,json\n_a=gg._f7_readonly_wardrobe_audit\n_a.request_nonce=%r\n_a.%s(*json.loads(%r))\n"%(nonce,method,payload)

def wait_status(transport,plan,job_id,phases,timeout=60,nonce=None):
    deadline=time.monotonic()+timeout;last_error=None
    while time.monotonic()<deadline:
        try:
            status=parse_status(transport.read(STATUS),plan['run_id'],job_id,nonce)
            if status['phase']=='paused'or status['phase']in phases:return status
        except (ValueError,subprocess.CalledProcessError,KeyError)as error:last_error=str(error)
        time.sleep(.5)
    raise TimeoutError('No matching native status: '+str(last_error))

def run_audit(args,plan,out):
    gpu=json.loads(Path(args.gpu_provenance).read_text())
    if not all(gpu.get(k)for k in('renderer','backend','device')):raise ValueError('GPU provenance needs renderer/backend/device')
    transport=AdbTransport(args.serial,args.adb)
    identity=transport.provenance(args.device_script,gpu);identity['probe_sha256']=plan['probe_sha256']
    surface=out/'surfaceflinger-start.txt';surface.write_text(transport.surfaceflinger_raw);surface.chmod(0o600)
    provenance_path=out/'provenance.json'
    if args.resume and provenance_path.exists()and json.loads(provenance_path.read_text())!=identity:raise ValueError('Package/script/GPU identity changed; new audit required')
    dump(provenance_path,identity)
    native=PROBE.read_text(encoding='ascii');init_nonce=uuid.uuid4().hex
    init=native+"\nimport gg\n_old=getattr(gg,'_f7_readonly_wardrobe_audit',None)\nif _old is not None and _old.phase=='paused':_old.recover()\nif _old is not None and _old.phase!='idle':raise RuntimeError('Prior native audit not cleanly idle; sole actor must recover original UI first')\ngg._f7_readonly_wardrobe_audit=ReadonlyWardrobeAudit(gg,%r,%r,json.loads(%r))\ngg._f7_readonly_wardrobe_audit.request_nonce=%r\ngg._f7_readonly_wardrobe_audit.inventory()\n"%(STATUS,plan['run_id'],json.dumps(identity,ensure_ascii=True),init_nonce)
    transport.submit(init,out);inventory=wait_status(transport,plan,None,{'idle'},20,init_nonce)
    if inventory['phase']=='paused':raise RuntimeError(inventory)
    signature=inventory['inventory']['digest'];inventory_path=out/'inventory.json'
    if args.resume and inventory_path.exists():
        previous_inventory=json.loads(inventory_path.read_text())['inventory']
        if previous_inventory['digest']!=signature or previous_inventory.get('owner_key')!=inventory['inventory'].get('owner_key'):raise ValueError('Canonical inventory/owner changed; no save restoration allowed')
    dump(inventory_path,inventory)
    checkpoint=out/'checkpoint.jsonl';records=[json.loads(l)for l in checkpoint.read_text().splitlines()if l.strip()]if checkpoint.exists()else[]
    allowed_jobs={job['job_id']for job in plan['jobs']}
    if any(row.get('run_id')!=plan['run_id']or row.get('job_id')not in allowed_jobs for row in records):raise ValueError('Checkpoint run/job identity mismatch')
    done={r['job_id']for r in records if r.get('terminal')}
    for job in plan['jobs']:
        if job['job_id']in done:continue
        if job['hero_id']in(46,125):
            row={'run_id':plan['run_id'],'job_id':job['job_id'],'job':job,'terminal':True,'result':{'load_status':'original_hidden_no_model','reason':'Original46/125 no-model exclusion, not a rendered pass'}}
            with checkpoint.open('a')as handle:handle.write(json.dumps(row)+'\n')
            checkpoint.chmod(0o600)
            records.append(row);continue
        first_attempt=next_attempt(records,job['job_id'],out)
        for attempt in range(first_attempt,2):
            exclusive_write(out/('%s-attempt%d.reserved'%(job['job_id'],attempt)),b'Attempt reserved before native dispatch\n')
            started=time.time();dump(out/'active-job.json',{'job':job,'attempt':attempt,'started':started})
            offset=int(transport.shell('wc','-c',DOCS+'/offline_runtime.log').split()[0])
            current=dict(job,timeout=args.timeout,capture_timeout=30,save_path=DOCS+'/offline_progress.json',attempt=attempt)
            start_nonce=uuid.uuid4().hex
            transport.submit(source_call('start',current,nonce=start_nonce),out)
            status=wait_status(transport,plan,job['job_id'],{'ready_capture','idle'},args.timeout+20,start_nonce)
            frame=None
            if status['phase']=='ready_capture':
                token=status['token'];before_nonce=uuid.uuid4().hex
                transport.submit(source_call('checkpoint',token,'before',nonce=before_nonce),out)
                before=wait_status(transport,plan,job['job_id'],{'capture_before','idle'},15,before_nonce)
                if before['phase']=='capture_before':
                    host_before=time.time();png=transport.run('exec-out','screencap','-p',binary=True)
                    dimensions=png_dimensions(png)
                    if sorted(dimensions)!=sorted(active_resolution(identity.get('resolution',''))):raise ValueError('Screenshot is not the full native display resolution')
                    target=out/('%s-attempt%d.png'%(job['job_id'],attempt));exclusive_write(target,png)
                    frame={'path':str(target.resolve()),'dimensions':dimensions,'sha256':digest(png),'token':token,'host_before':host_before,'host_captured':time.time()}
                    after_nonce=uuid.uuid4().hex
                    transport.submit(source_call('checkpoint',token,'after',frame,nonce=after_nonce),out)
                    status=wait_status(transport,plan,job['job_id'],{'idle'},30,after_nonce);frame['host_after']=time.time()
                    if status.get('result',{}).get('load_status')=='loaded_unreviewed':validate_frame(before,status,frame)
                else:status=before
            logs=transport.shell('tail','-c','+'+str(offset+1),DOCS+'/offline_runtime.log')
            events=rpc_observations(logs)
            row={'run_id':plan['run_id'],'job_id':job['job_id'],'job':job,'attempt':attempt,'started':started,'finished':time.time(),'status':status,
                'result':status.get('result',{'load_status':'failed','reason':status.get('reason')}),'frame':frame,'observedRPCs':events,
                'visual_review':{'verdict':'unreviewed','notes':''}}
            logpath=out/('%s-attempt%d.log'%(job['job_id'],attempt));exclusive_write(logpath,logs.encode('utf-8'))
            forbidden=any(e['kind']in('forbidden','unclassified')for e in events)
            row['terminal']=status['phase']=='idle'and(row['result']['load_status']not in('failed','timeout')or attempt==1)
            if forbidden:row['result']['load_status']='failed';row['result']['reason']='Forbidden or unclassified outgoing RPC: read-only scope unverified';row['terminal']=False
            with checkpoint.open('a')as handle:handle.write(json.dumps(row,ensure_ascii=True)+'\n');handle.flush();os.fsync(handle.fileno())
            checkpoint.chmod(0o600)
            records.append(row);dump(out/'summary.json',summarize(records,plan))
            if status['phase']=='paused'or forbidden:raise RuntimeError('Batch paused; inspect checkpoint, original UI and pending tasks. No automatic reset or save overwrite.')
            if row['terminal']:break
    final_nonce=uuid.uuid4().hex
    transport.submit(source_call('inventory',nonce=final_nonce),out)
    final=wait_status(transport,plan,None,{'idle'},20,final_nonce)
    dump(out/'inventory-final.json',final)
    if final.get('inventory',{}).get('digest')!=signature:raise ValueError('Batch-final inventory changed; review, never restore save')
    dump(out/'summary.json',summarize(records,plan))

def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--out-dir',type=Path,default=ROOT/'reports/wardrobe-readonly-audit-plan')
    p.add_argument('--heroes',type=int,nargs='*',default=[]);p.add_argument('--skins',type=int,nargs='*',default=[]);p.add_argument('--limit',type=int)
    p.add_argument('--review',type=Path,help='Offline per-item review JSON; requires existing run and matching frame hashes, no ADB')
    p.add_argument('--execute',action='store_true',help='Sole native actor only: actually queue original UI probes/ADB captures')
    p.add_argument('--resume',action='store_true');p.add_argument('--serial');p.add_argument('--adb',type=Path)
    p.add_argument('--device-script',help='Optional effective loose script override; otherwise hash installed APK assets/script.npk without extracting it')
    p.add_argument('--gpu-provenance',type=Path);p.add_argument('--timeout',type=float,default=40)
    args=p.parse_args(argv)
    if args.timeout<3:p.error('--timeout must allow at least3 seconds')
    if args.limit is not None and args.limit<0:p.error('--limit must be nonnegative')
    out=args.out_dir.resolve();out.mkdir(parents=True,exist_ok=True);out.chmod(0o700)
    path=out/'plan.json'
    if args.resume or args.review:
        plan=json.loads(path.read_text())
        if plan['probe_sha256']!=digest(PROBE.read_bytes()):raise ValueError('Native probe changed; create a new audit run')
        if plan.get('catalog_sha256')!=catalog_hashes():raise ValueError('Catalog source changed; create a new audit plan')
    else:
        if path.exists():raise ValueError('Existing plan/run; use --resume or another output directory (never overwrite checkpoints)')
        heroes,skins=original_tables();plan=make_plan(heroes,skins,args.heroes,args.skins,args.limit);dump(path,plan)
    if args.review:
        if args.execute:raise ValueError('Review is offline; do not combine with --execute')
        reviews=json.loads(args.review.read_text());records=[json.loads(l)for l in(out/'checkpoint.jsonl').read_text().splitlines()if l.strip()]
        latest={r['job_id']:r for r in records}
        for review in reviews:
            row=latest[review['job_id']]
            if row.get('result',{}).get('load_status')!='loaded_unreviewed' or review.get('frame_sha256')!=row.get('frame',{}).get('sha256'):
                raise ValueError('Review must match a successfully loaded screenshot hash')
            frame_path=Path(row['frame']['path'])
            if not frame_path.is_file()or digest(frame_path.read_bytes())!=review['frame_sha256']:raise ValueError('Reviewed PNG is missing or its bytes changed')
            if review.get('verdict')not in('pass','fail','unreviewed')or not review.get('reviewer'):raise ValueError('Explicit reviewer and verdict required')
            row['visual_review']=review
        dump(out/'visual-review-ledger.json',reviews);dump(out/'summary.json',summarize(list(latest.values()),plan))
        print(json.dumps({'mode':'offline_visual_review_no_ADB','summary':str(out/'summary.json')}));return 0
    if not args.execute:
        print(json.dumps({'mode':'plan_only_no_ADB','plan':str(path),'jobs':len(plan['jobs']),'denominators':plan['denominators']}));return 0
    if not args.serial or not args.gpu_provenance:p.error('--execute requires --serial and --gpu-provenance')
    try:
        run_audit(args,plan,out)
    except Exception as error:
        active=json.loads((out/'active-job.json').read_text())if(out/'active-job.json').exists()else None
        dump(out/'fatal.json',{'run_id':plan['run_id'],'time':time.time(),'error':str(error),'active_job':active,'policy':'Queue halted; inspect original UI and native status before any resume. No save restoration.'})
        raise
    return 0

if __name__=='__main__':main()
