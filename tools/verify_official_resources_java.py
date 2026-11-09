"""Reconstruct pinned official resources using the TWO REAL production Java classes.

No downloader and no reconstruction algorithm lives here. All source cache files
are preflighted read-only before Java can run. Outputs exist one at a time in an
exclusive marker-owned scratch directory and are deleted after independent SHA.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import time
import uuid
from preserve_cdn import parse_manifest

ROOT=Path(__file__).resolve().parents[1]
MARKER='.official-java-verifier-owned'
JAVA_FILES=['runtime/android_resource_init/src/com/forever7/offline/OfficialResources.java',
            'runtime/android_resource_init/src/com/forever7/offline/ResourceImporter.java',
            'tools/java/OfficialResourceFullVerifier.java']

def digests(path):
    md5,sha=hashlib.md5(),hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda:stream.read(1024*1024),b''):
            md5.update(block);sha.update(block)
    return md5.hexdigest(),sha.hexdigest()

def metadata(path):
    st=path.stat()
    return [st.st_dev,st.st_ino,st.st_size,st.st_mtime_ns,st.st_mode]

def clean_owned_scratch(path,parent,token):
    path,parent=Path(path),Path(parent).resolve()
    if path.is_symlink() or path.resolve().parent!=parent or not path.name.startswith('official-java-'):
        raise ValueError('Refusing cleanup outside exclusive verifier scratch')
    if (path/MARKER).read_text()!=token:
        raise ValueError('Scratch ownership token mismatch')
    shutil.rmtree(path)

def write_json(path,value):
    path.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n')

def run(args):
    started=time.monotonic()
    plan=json.loads(args.plan.read_text());manifest=json.loads(args.manifest.read_text())
    if plan['version']!=640 or plan['platform']!='android':raise ValueError('Only original fixed Android640 plan supported')
    if digests(args.version_manifest)[1]!=plan['pinned_version_manifest_sha256']:raise ValueError('Original version manifest pin mismatch')
    published={r['path']:r for r in parse_manifest('android',640,args.version_manifest.read_text())}
    expected=plan['npk_output_manifest']['entries']
    all_expected=expected+[{'name':r['path'].removeprefix('res/'),'bytes':r['size'],'sha256':r['sha256']}for r in plan['raw_files']]
    if {r['name']:r for r in manifest['entries']}!={r['name']:r for r in all_expected}:raise ValueError('Production output manifest disagrees with source-plan NPK/raw pins')
    cache=args.cache.resolve();report_dir=args.report_dir.resolve();report_dir.mkdir(parents=True,exist_ok=True)
    # Never overwrite a prior completed/partial verification evidence set.
    if any((report_dir/name).exists()for name in ('summary.json','preflight.jsonl','outputs.jsonl')):raise ValueError('Report directory already contains verification evidence')
    sources=[];valid={};snapshots={}
    with (report_dir/'preflight.jsonl').open('w') as log:
        for part in plan['parts']:
            for item in [dict(part['check'],sha256=part.get('check_sha256'))]+part['payloads']:
                name=item['path'];row={'path':name,'expected_size':item['size'],'expected_md5':item['md5'],'expected_sha256':item.get('sha256'),'ok':False}
                try:
                    official=published[name]
                    if (official['size'],official['md5'])!=(item['size'],item['md5']):raise ValueError('Source plan disagrees with published fixed-version pin')
                    path=cache/name
                    if path.resolve()!=path.absolute() or not path.is_file():raise ValueError('Source missing, not regular, or symbolic link')
                    before=metadata(path)
                    actual_md5,actual_sha=digests(path)
                    row.update(actual_size=path.stat().st_size,actual_md5=actual_md5,actual_sha256=actual_sha)
                    if metadata(path)!=before:raise ValueError('Source changed during preflight')
                    if before[2]!=item['size'] or actual_md5!=item['md5'] or item.get('sha256') and actual_sha!=item['sha256']:raise ValueError('Source digest or size mismatch')
                    valid[name]=True;snapshots[name]=before;row['ok']=True
                except (OSError,ValueError,KeyError) as error:row['error']=str(error);valid[name]=False
                log.write(json.dumps(row)+'\n');log.flush();sources.append(row)
            print('preflight part='+part['part']+' sources='+str(len(sources)),flush=True)
    bypart={p['part']:p for p in plan['parts']}
    outputs=[];skipped=[]
    for entry in expected:
        part=bypart[entry['name'][:-4]]
        required=[part['check']['path']]+[i['path']for i in part['payloads']]
        missing=[p for p in required if not valid.get(p)]
        if missing:skipped.append(dict(entry,missing_sources=missing))
        else:outputs.append(('N',entry['name'],entry['bytes'],entry['sha256'],part['part']))
    rawpart=bypart['raw'];rawversions={int(p['path'].split('/')[1]):p for p in rawpart['payloads']}
    for raw in plan['raw_files']:
        name=raw['path'].removeprefix('res/')
        required=[rawpart['check']['path'],rawversions[raw['version']]['path']]
        missing=[p for p in required if not valid.get(p)]
        if missing:skipped.append({'name':name,'missing_sources':missing})
        else:outputs.append(('R',name,raw['size'],raw['sha256'],raw['version'],raw['offset']))
    outputs.sort(key=lambda row:row[2])
    maximum=max((row[2]for row in outputs),default=0)
    parent=args.scratch_parent.resolve();parent.mkdir(parents=True,exist_ok=True)
    free=shutil.disk_usage(parent).free
    if free<maximum+256*1024*1024:raise ValueError('Insufficient safe space for largest single output plus256MiB margin')
    scratch=Path(tempfile.mkdtemp(prefix='official-java-',dir=parent));token=uuid.uuid4().hex;(scratch/MARKER).write_text(token)
    summary={'scope':'host real-production Java reconstruction, NOT native fresh download','source_plan_sha256':digests(args.plan)[1],
        'production_manifest_sha256':digests(args.manifest)[1],'version_manifest_sha256':digests(args.version_manifest)[1],
        'java_source_sha256':{f:digests(ROOT/f)[1]for f in JAVA_FILES},'cache':str(cache),'source_files':len(sources),'verified_sources':sum(r['ok']for r in sources),
        'source_gaps':[r for r in sources if not r['ok']],'scheduled_outputs':len(outputs),'skipped_outputs':skipped,
        'output_bytes_scheduled':sum(row[2]for row in outputs),'scratch':str(scratch),'largest_single_output_bytes':maximum,'free_bytes_before':free}
    write_json(report_dir/'summary.json',summary)
    try:
        lines=[]
        for part in plan['parts']:
            check=part['check'];lines.append(('C',part['part'],check['path'],check['size'],check['md5'],part.get('check_sha256')or'-'))
            for item in part['payloads']:lines.append(('D',part['part'],item['path'],item['size'],item['md5'],'-'))
        lines.extend(outputs);(scratch/'plan.tsv').write_text(''.join('\t'.join(map(str,row))+'\n'for row in lines))
        java=args.java_home.resolve()/'bin';classes=scratch/'classes';classes.mkdir()
        subprocess.run([str(java/'javac'),'-source','8','-target','8','-Xlint:-options','-d',str(classes)]+[str(ROOT/f)for f in JAVA_FILES],check=True)
        with (report_dir/'java.log').open('w') as log:
            result=subprocess.run([str(java/'java'),'-Xmx256m','-cp',str(classes),'OfficialResourceFullVerifier',str(scratch/'plan.tsv'),str(cache),str(scratch),str(report_dir/'outputs.jsonl')],stdout=log,stderr=subprocess.STDOUT)
        rows=[json.loads(line)for line in (report_dir/'outputs.jsonl').read_text().splitlines()]
        completed=[r for r in rows if not r.get('summary')];java_summary=next((r for r in rows if r.get('summary')),None)
        changed=[name for name,before in snapshots.items()if not (cache/name).exists()or metadata(cache/name)!=before]
        summary.update(java_exit_code=result.returncode,java_summary=java_summary,completed_outputs=len(completed),verified_outputs=sum(r['ok']for r in completed),
            verified_npk=sum(r['ok']and r['kind']=='npk'for r in completed),verified_raw=sum(r['ok']and r['kind']=='raw'for r in completed),
            verified_bytes=sum(r['actual_bytes']for r in completed if r['ok']),source_metadata_changed=changed,
            all_output_files_deleted=all(r['deleted']for r in completed),seconds=round(time.monotonic()-started,3))
        summary['ok']=bool(result.returncode==0 and java_summary and len(completed)==312 and all(r['ok']for r in completed)and not changed and not skipped and all(r['deleted']for r in completed))
    finally:
        clean_owned_scratch(scratch,parent,token);summary['scratch_deleted']=not scratch.exists();write_json(report_dir/'summary.json',summary)
    print(json.dumps(summary,ensure_ascii=False),flush=True)
    return 0 if summary['ok']else 1

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--plan',type=Path,default=ROOT/'reports/official-asset-source-plan.json')
    parser.add_argument('--manifest',type=Path,default=ROOT/'runtime/android_resource_init/resource_manifest.json')
    parser.add_argument('--version-manifest',type=Path,default=ROOT/'evidence/patch2.android.640.version')
    parser.add_argument('--cache',type=Path,default=ROOT/'originals/cdn')
    parser.add_argument('--java-home',type=Path,default=ROOT/'toolchains/java/jdk-17.0.21+9/Contents/Home')
    parser.add_argument('--scratch-parent',type=Path,default=ROOT/'analysis/official-java-verifier-scratch')
    parser.add_argument('--report-dir',type=Path,default=ROOT/'reports/official-java-full-rebuild')
    return run(parser.parse_args())
if __name__=='__main__':raise SystemExit(main())
