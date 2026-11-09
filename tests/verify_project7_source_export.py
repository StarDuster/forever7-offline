"""Audit/extract a source ZIP and run original-APK-only offline prepare in fresh roots.
Python network and original-workspace/cache access are denied in the child; only
javac/cc subprocesses are allowed. Never invokes D8, assembler, signing or game.
"""
import _paths  # noqa: E402,F401
from pathlib import Path,PurePosixPath
import argparse,hashlib,json,os,subprocess,tempfile,zipfile
ROOT=Path(__file__).resolve().parents[1]
FORBIDDEN={'originals','analysis','toolchains','.venv','Downloads','host_stubs','host_tests','signing','__pycache__'}
EXTENSIONS={'.apk','.npk','.bson','.p12','.jks','.keystore','.class','.dex','.jar','.dylib','.so'}
def require(ok,message):
    if not ok:raise ValueError(message)
def sha(path):
    with Path(path).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()

def check(zip_path,original,python,java_home,build_tools,android_jar,work):
    python=Path(python).absolute()  # Preserve the venv invocation path, not its interpreter symlink target.
    zip_path,original,java_home,build_tools,android_jar,work=map(lambda p:Path(p).resolve(),(zip_path,original,java_home,build_tools,android_jar,work))
    require(not work.exists(),'Validation work directory exists');work.mkdir(parents=True);extract=work/'extract';extract.mkdir();prefix='forever7-offline-project/'
    with zipfile.ZipFile(zip_path) as z:
        names=z.namelist();require(len(names)==len(set(names)),'Duplicate archive member')
        require(sum(i.file_size for i in z.infolist())<=256*1024*1024,'Source archive total bound')
        allowed=json.loads(z.read(prefix+'offline-project-allowlist.json'))['files'];inventory=json.loads(z.read(prefix+'EXPORT-INVENTORY.json'))
        require(len(allowed)==len(set(allowed)) and len(inventory)==len(allowed),'Bad explicit inventory')
        expected={prefix+n for n in allowed}|{prefix+'EXPORT-INVENTORY.json'};require(set(names)==expected,'Extra/missing ZIP member')
        bypath={r['path']:r for r in inventory};require(set(bypath)==set(allowed),'Inventory path set mismatch')
        for name in names:
            require(name.startswith(prefix),'Wrong ZIP root');relative=name[len(prefix):];parts=PurePosixPath(relative)
            require(not parts.is_absolute() and '..' not in parts.parts and '\\' not in relative and not(set(parts.parts)&FORBIDDEN),'Forbidden source path')
            require(parts.suffix.lower()not in EXTENSIONS,'Forbidden binary/private suffix')
            info=z.getinfo(name);require(info.file_size<=128*1024*1024 and ((info.external_attr>>16)&0o170000)in(0,0o100000),'Nonregular/large member')
            data=z.read(name)
            if relative!='EXPORT-INVENTORY.json':require(bypath[relative]['bytes']==len(data) and bypath[relative]['sha256']==hashlib.sha256(data).hexdigest(),'Inventory size/hash mismatch')
            target=extract/parts;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data)
    config={'original_root':str(ROOT.resolve()),'downloads':str((Path.home()/'Downloads').resolve()),'extract':str(extract),'build':str(work/'build'),'guard':str(work/'guard'),'original':str(original),'allowed_prefixes':[str(work),str(Path(os.sys.prefix).resolve()),str(python.parent.parent.resolve()),str(java_home),str(build_tools)],'allowed_files':[str(original),str(android_jar)],'audit':str(work/'python-audit.json')}
    guard=work/'guard';guard.mkdir();(guard/'config.json').write_text(json.dumps(config))
    launcher=guard/'launch.py';launcher.write_text('''import sys,os,json,runpy,socket,urllib.request
from pathlib import Path
config=json.loads((Path(__file__).parent/'config.json').read_text())
reads=set();processes=[];blocked=[]
def inside(path,root):return path==root or path.startswith(root+os.sep)
def permitted(path):return path in config['allowed_files'] or any(inside(path,p) for p in config['allowed_prefixes'])
def deny(reason):blocked.append(reason);raise PermissionError('Source validation blocked: '+reason)
def audit(event,args):
    if event=='open' and isinstance(args[0],(str,bytes,os.PathLike)):
        path=os.path.realpath(os.fsdecode(args[0]))
        if inside(path,config['downloads']) and not permitted(path):deny('Downloads input')
        if inside(path,config['original_root']) and not permitted(path):deny('original workspace/cache input')
        if inside(path,config['extract']):reads.add(os.path.relpath(path,config['extract']))
    if event in ('socket.connect','socket.getaddrinfo','socket.gethostbyname','socket.sendto','urllib.Request'):deny('network '+event)
    if event=='subprocess.Popen':
        executable=os.fsdecode(args[0]);name=os.path.basename(executable)
        if name not in ('cc','javac'):deny('non-prepare subprocess '+name)
        processes.append({'executable':executable,'arguments':list(args[1])})
sys.addaudithook(audit)
def no_network(*a,**k):deny('Python network API')
socket.create_connection=no_network;socket.getaddrinfo=no_network
urllib.request.urlopen=no_network;urllib.request.OpenerDirector.open=no_network
sys.path.insert(0,str(Path(config['extract'])/'tools'))
sys.argv=[str(Path(config['extract'])/'tools/build_offline_project.py')]+sys.argv[1:]
try:runpy.run_path(sys.argv[0],run_name='__main__')
finally:
    origins={}
    for name,module in list(sys.modules.items()):
        path=getattr(module,'__file__',None)
        if path:
            path=os.path.realpath(path)
            if inside(path,config['extract']):origins[name]=os.path.relpath(path,config['extract'])
            if inside(path,config['original_root']) and not permitted(path):blocked.append('original workspace module '+name)
    Path(config['audit']).write_text(json.dumps({'exported_file_opens':sorted(reads),'module_origins':origins,'subprocesses':processes,'blocked_operations':blocked,'network_calls_blocked':True,'third_party_versions':{name:getattr(sys.modules.get(name),'__version__',None) for name in ('lz4','xdis')}},indent=2)+'\\n')
''')
    command=[str(python),str(launcher),str(original),'--prepare-only','--offline','--build-dir',str(work/'build'),'--java-home',str(java_home),'--build-tools',str(build_tools),'--android-jar',str(android_jar)]
    env=os.environ.copy();env.pop('PYTHONPATH',None);env['PYTHONDONTWRITEBYTECODE']='1'
    result=subprocess.run(command,cwd=extract,env=env,capture_output=True,text=True)
    (work/'prepare.stdout.log').write_text(result.stdout);(work/'prepare.stderr.log').write_text(result.stderr)
    if result.returncode:raise RuntimeError('Clean export prepare failed; see '+str(work/'prepare.stderr.log'))
    audit=json.loads((work/'python-audit.json').read_text());require(not audit['blocked_operations'],'Denied dependency/network access attempted')
    report=json.loads((work/'build/offline-project-build.json').read_text());require(report['backend']=='project7' and not report['apk_built'] and report['original_unchanged'],'Not a successful static P7 prepare')
    require(not list((work/'build').rglob('*.apk')) and not list((work/'build').rglob('*.p12')),'APK/signing artifact appeared')
    # Every declared export file is audited independently, and every runtime source/data
    # open must originate in the extracted tree or newly generated private build roots.
    source_files=[{'path':n,'bytes':(extract/n).stat().st_size,'sha256':sha(extract/n)} for n in allowed]
    summary={'format':'project7-source-export-clean-prepare-v1','zip':{'path':str(zip_path),'bytes':zip_path.stat().st_size,'sha256':sha(zip_path)},'files':len(allowed),'zip_inventory_all_hashes_match':True,'fresh_extract':str(extract),'fresh_build':str(work/'build'),'initial_build_cache_present':False,'external_game_input':'supported original APK only','original_apk_sha256_after':sha(original),'toolchains_external_explicit':{'python':str(python),'java_home':str(java_home),'build_tools':str(build_tools),'android_jar':str(android_jar)},'python_audit':audit,'prepare_report':report,'source_files':source_files,'no_apk_or_signing_output':True,'native_runtime_tested':False,'candidate_not_final_delivery':True}
    (work/'validation.json').write_text(json.dumps(summary,indent=2)+'\n');return summary

def main():
    p=argparse.ArgumentParser(description=__doc__)
    for name in ['zip','original','python','java-home','build-tools','android-jar','work']:p.add_argument('--'+name,required=True,type=Path)
    a=p.parse_args();r=check(a.zip,a.original,a.python,a.java_home,a.build_tools,a.android_jar,a.work);print(json.dumps({k:v for k,v in r.items() if k not in ('source_files','python_audit')},indent=2))
if __name__=='__main__':main()
