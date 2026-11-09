"""Exact original manager JVM + isolated Android32 compile; no D8/APK/game."""
from pathlib import Path
import subprocess,tempfile,hashlib,json,sys
ROOT=Path(__file__).resolve().parents[2];HERE=Path(__file__).resolve().parent
PATCHED='--patched' in sys.argv
JAR=ROOT/('analysis/project7/event-reset-week-hook-v2/manager-translated-frames.jar' if PATCHED else 'analysis/project7/dream-lifecycle-hook-v1/manager-translated-frames.jar');assert hashlib.sha256(JAR.read_bytes()).hexdigest()==('af930ec43effa7ee491d5dd391e4ff338a7e540f25c7bed43f4a9fb54a002e78' if PATCHED else '2ed4ab9dea04f1b90947415da5ebd405f44f20512b157d74805130603accbb0a')
JDK=ROOT/'toolchains/java/jdk-17.0.21+9/Contents/Home/bin';ANDROID=ROOT/'toolchains/android-sdk/platforms/android-32/android.jar';JSON=ROOT/'toolchains/json-20240303.jar';BUILD=Path(tempfile.mkdtemp(prefix='event-reset-week-host-',dir=ROOT/'analysis/project7'));DREAM=ROOT/'runtime/android_dream_mode'
def run(*args):
 p=subprocess.run(list(map(str,args)),text=True,capture_output=True)
 if p.returncode:raise RuntimeError(p.stdout+p.stderr)
 return p.stdout+p.stderr
for assets in ('analysis/project7/manager/assets','analysis/project7/fixed-component-v2-stage/assets'):
 assert hashlib.sha256((ROOT/assets/'new_player.bson').read_bytes()).hexdigest()=='6877cdc06532a11faa47e1855049f678db1c210de96caf1312c27c431b9875d7'
sources=sorted([p for p in HERE.rglob('*') if p.is_file() and p.suffix in ('.java','.py') and '__pycache__' not in str(p)]+[p for folder in (DREAM/'src',DREAM/'compile_stubs') for p in folder.rglob('*.java')]);before={str(p):hashlib.sha256(p.read_bytes()).hexdigest()for p in sources}
for n in ['api','production','dreamapi','dream','platform','tests']:(BUILD/n).mkdir()
for src,api,prod in [(HERE,'api','production'),(DREAM,'dreamapi','dream')]:
 run(JDK/'javac','--release','8','-cp',ANDROID,'-d',BUILD/api,*src.glob('compile_stubs/**/*.java'))
 run(JDK/'javac','--release','8','-cp',str(ANDROID)+':'+str(BUILD/api),'-d',BUILD/prod,*src.glob('src/**/*.java'))
run(JDK/'javac','--release','8','-d',BUILD/'platform',*[p for p in ROOT.glob('runtime/android_core_rpc/host_stubs/**/*.java')if p.name not in ('AssetManager.java','Os.java')],*HERE.glob('host_tests/android/**/*.java'))
cp=':'.join(map(str,[BUILD/'platform',JAR,JSON,BUILD/'production',BUILD/'dream']))
run(JDK/'javac','--release','8','-cp',cp,'-d',BUILD/'tests',HERE/'host_tests/com/project7/localmanager/EventResetWeekHost.java')
out=run(JDK/'java','-Xverify:all','-Dp7.reset.patched='+str(PATCHED).lower(),'-Dp7.reset.catalog='+str(ROOT/'runtime/project7_week_reset/catalog-v1.tsv'),'-cp',cp+':'+str(BUILD/'tests'),'com.project7.localmanager.EventResetWeekHost',ROOT/'analysis/project7/manager/assets');print(out,end='');(BUILD/'stdout.log').write_text(out);print('host_artifacts='+str(BUILD))
assert before=={str(p):hashlib.sha256(p.read_bytes()).hexdigest()for p in sources},'source drift'

if '--gateway' in sys.argv:
 support=Path(sys.argv[sys.argv.index('--gateway')+1]).resolve();inventory=json.loads((support.parent/'support-host-inputs.json').read_text());assert Path(inventory['production_directory'])==support
 for path,digest in inventory['source_sha256'].items():assert hashlib.sha256(Path(path).read_bytes()).hexdigest()==digest,path
 for path,digest in inventory['production_class_sha256'].items():assert hashlib.sha256((support/path).read_bytes()).hexdigest()==digest,path
 overlay=Path(inventory['asset_overlay'])
 for path,digest in inventory['assets'].items():assert hashlib.sha256((overlay/path).read_bytes()).hexdigest()==digest,path
 gcp=cp+':'+str(support)
 run(JDK/'javac','--release','8','-cp',gcp,'-d',BUILD/'tests',HERE/'host_tests/com/project7/localmanager/EventResetWeekGatewayHost.java')
 extra=run(JDK/'java','-Xverify:all','-Dp7.reset.patched='+str(PATCHED).lower(),'-Dp7.reset.catalog='+str(ROOT/'runtime/project7_week_reset/catalog-v1.tsv'),'-Dp7.reset.support.assets='+str(overlay),'-cp',gcp+':'+str(BUILD/'tests'),'com.project7.localmanager.EventResetWeekGatewayHost',ROOT/'analysis/project7/fixed-component-v2-stage/assets',BUILD/'gateway-cases.json');print(extra,end='');(BUILD/'stdout.log').write_text(out+extra)

# Inspect descriptors/visibility without loading compile-only definitions.
def abi(text):
 result={};previous=''
 for line in text.splitlines():
  clean=line.strip()
  if clean.startswith('descriptor:'):
   descriptor=clean.split(':',1)[1].strip();kind='method' if descriptor.startswith('(') else 'field'
   if '(' in previous:
    name=previous.split('(',1)[0].split()[-1]
    if '.' in name:name='<init>'
   else:name=previous.rstrip(';').split()[-1]
   flags=tuple(word for word in ('public','protected','private','static','final') if word in previous.split())
   result[(kind,name,descriptor)]=flags
  elif clean:previous=clean
 return result
mismatches=[];checked=0
for path in (BUILD/'api').rglob('*.class'):
 name=path.relative_to(BUILD/'api').as_posix()[:-6].replace('/','.')
 declared=abi(run(JDK/'javap','-p','-s','-classpath',BUILD/'api',name))
 actual=abi(run(JDK/'javap','-p','-s','-classpath',(BUILD/'dream' if name.endswith('.DreamCoordinator') else JAR),name))
 for member,flags in declared.items():
  checked+=1
  if actual.get(member)!=flags:mismatches.append([name,member,flags,actual.get(member)])
assert not mismatches,mismatches
(BUILD/'abi-result.json').write_text(json.dumps({'members_with_constructors_checked':checked,'descriptor_visibility_static_final_mismatches':mismatches},indent=2)+'\n')
print('PASS exact stub ABI including constructor visibility/static/final:',checked)

if PATCHED and '--gateway' in sys.argv:
 consumer=run(ROOT/'.venv/bin/python',HERE/'host_tests/consumer.py',BUILD/'gateway-cases.json',BUILD/'consumer-result.json');print(consumer,end='');(BUILD/'stdout.log').write_text(out+extra+consumer)

assert before=={str(p):hashlib.sha256(p.read_bytes()).hexdigest()for p in sources},'final source drift'
report={'status':'PASS','actual_manager_sha256':hashlib.sha256(JAR.read_bytes()).hexdigest(),'patched_private_dispatch':PATCHED,'build':str(BUILD),'android32_compile':True,'runtime_no_compile_stubs':True,'abi':json.loads((BUILD/'abi-result.json').read_text()),'source_sha256':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest()for p in sources},'catalog_sha256':hashlib.sha256((ROOT/'runtime/project7_week_reset/catalog-v1.tsv').read_bytes()).hexdigest(),'checks':['pure METHODS before asset prepare','all enabled bindings plus disabled/missing/invalid/busy guards','original reset primitives and writer/Week.recover, no black-letter consumption','awaiting-only idempotent reply; completed/processing old packet no reset','v1/policy/hash/event/white/sourceCommit/menu metadata replay faults rejected','unique original resetEvents/entrances menu, original temporary rt and legal successor route effects','actual original effects closure/ACK completes for three sources','closure flag/residual ledger/IO refusal preserves old facts','ordinary null engine and pending/null engine/template boundary','profile commit then Properties failure fresh Store/Week recovery same id','actual original producer/reset reply/avatar payload/emergency callback finite consumer'],'limits':['offline event continuation policy, not original server recovery','authoritative completed facts seeded in finite host fixture; no whole-plot reachability claim','closure-incomplete guard test injects the original ThreadLocal flag on publication, not a synthetic >8-rules engine claim','selected original functions, rendering/entity creation/network boundaries explicit','wire only e cannot disambiguate extremely late packets after a genuine new same-event completion','no D8/APK/device/game/ART acceptance']}
if '--gateway' not in sys.argv:
 report['checks']=report['checks'][:5]
 report['limits'].append('gateway/effects/null-engine/reply consumer cases not requested in this run')
elif not PATCHED:
 report['checks']=[item for item in report['checks'] if not item.startswith(('unique original resetEvents/entrances menu, original temporary rt and legal successor','profile commit then Properties failure','actual original producer/reset reply'))]
 report['limits'].append('actual patched dispatcher and original consumer cases not requested in this run')
(BUILD/'result.json').write_text(json.dumps(report,indent=2)+'\n')
print('result='+str(BUILD/'result.json'))
