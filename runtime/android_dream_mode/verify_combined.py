"""Actual combined fixed manager dispatch/store seams only. No D8/APK/VM."""
from pathlib import Path
import sys,subprocess,hashlib,tempfile,json,os,urllib.parse,zipfile,shutil
ROOT=Path(__file__).resolve().parents[2];HERE=Path(__file__).resolve().parent
LIFECYCLE='--lifecycle' in sys.argv
RECOMPILE_SUPPORT='--recompile-support' in sys.argv
JAR=ROOT/('analysis/project7/dream-lifecycle-hook-v1/manager-translated-frames.jar' if LIFECYCLE else 'analysis/project7/dream-hook-v1/manager-translated-frames.jar')
assert hashlib.sha256(JAR.read_bytes()).hexdigest()==('2ed4ab9dea04f1b90947415da5ebd405f44f20512b157d74805130603accbb0a' if LIFECYCLE else 'f5efd2360c952fc740ec498549175039a0261d82fd9c555f61d3e7ececfa8907')
assert hashlib.sha256((ROOT/'analysis/project7/manager/assets/new_player.bson').read_bytes()).hexdigest()=='6877cdc06532a11faa47e1855049f678db1c210de96caf1312c27c431b9875d7'
JDK=ROOT/'toolchains/java/jdk-17.0.21+9/Contents/Home/bin';ANDROID=ROOT/'toolchains/android-sdk/platforms/android-32/android.jar';JSON=ROOT/'toolchains/json-20240303.jar';PROGRAM=Path(sys.argv[1]).resolve()
assert (PROGRAM/'com/project7/localmanager/HistoryDrawPolicy.class').is_file()
BUILD=Path(tempfile.mkdtemp(prefix='dream-combined-host-',dir=ROOT/'analysis/project7'))
def run(*args):
 p=subprocess.run(list(map(str,args)),text=True,capture_output=True)
 if p.returncode:raise RuntimeError(p.stdout+p.stderr)
 return p.stdout+p.stderr
owned_sources=[p for folder in ['runtime/android_dream_mode','runtime/android_request_events','runtime/android_core_rpc','runtime/android_mechanism_gateway'] for p in (ROOT/folder).rglob('*') if p.is_file() and p.suffix in ('.java','.py') and '__pycache__' not in str(p)]
owned_before={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in owned_sources}
for d in ['stubs','dream','reqstubs','request','platform','composite','tests','coreapi','core','historyapi','history','cgapi','cg']:(BUILD/d).mkdir()
run(JDK/'javac','--release','8','-d',BUILD/'stubs',*HERE.glob('compile_stubs/**/*.java'))
run(JDK/'javac','--release','8','-cp',str(ANDROID)+':'+str(BUILD/'stubs'),'-d',BUILD/'dream',*HERE.glob('src/**/*.java'))
REQUEST=ROOT/'runtime/android_request_events'
run(JDK/'javac','--release','8','-d',BUILD/'reqstubs',*REQUEST.glob('compile_stubs/**/*.java'))
run(JDK/'javac','--release','8','-cp',str(ANDROID)+':'+str(BUILD/'reqstubs'),'-d',BUILD/'request',*REQUEST.glob('src/**/*.java'))
run(JDK/'javac','--release','8','-d',BUILD/'platform',*[p for p in ROOT.glob('runtime/android_core_rpc/host_stubs/**/*.java') if p.name not in ('AssetManager.java','Os.java')],*HERE.glob('host_stubs/**/*.java'))
CG=ROOT/'runtime/android_core_rpc'
run(JDK/'javac','--release','8','-d',BUILD/'cgapi',*CG.glob('compile_stubs/**/*.java'))
run(JDK/'javac','--release','8','-cp',str(ANDROID)+':'+str(BUILD/'cgapi'),'-d',BUILD/'cg',*CG.glob('src/**/*.java'))
inventory=json.loads((PROGRAM.parent/'host-inputs.json').read_text())
assert Path(inventory['production_directory'])==PROGRAM
assert len(list(PROGRAM.rglob('*.class')))==17
support_compile_only_drift=[]
for path,digest in inventory['source_sha256'].items():
 actual=hashlib.sha256(Path(path).read_bytes()).hexdigest()
 if actual!=digest:
  assert RECOMPILE_SUPPORT and '/compile_stubs/' in path,path
  support_compile_only_drift.append({'path':path,'old_sha256':digest,'new_sha256':actual})
for path,digest in inventory['assets'].items():assert hashlib.sha256((PROGRAM.parent/'assets'/path).read_bytes()).hexdigest()==digest,path
SUPPORT=PROGRAM
ASSET_OVERLAY=PROGRAM.parent/'assets'
support_current_sources={}
if RECOMPILE_SUPPORT:
 SUPPORT=BUILD/'support-production';SUPPORT.mkdir()
 for folder,api,prod in [('android_draw_policy','coreapi','core'),('android_history_draw','historyapi','history')]:
  src=ROOT/'runtime'/folder
  for p in list(src.glob('src/**/*.java'))+list(src.glob('compile_stubs/**/*.java')):support_current_sources[str(p)]=hashlib.sha256(p.read_bytes()).hexdigest()
  run(JDK/'javac','--release','8','-cp',ANDROID,'-d',BUILD/api,*src.glob('compile_stubs/**/*.java'))
  run(JDK/'javac','--release','8','-cp',str(ANDROID)+':'+str(BUILD/api),'-d',BUILD/prod,*src.glob('src/**/*.java'))
  for p in (BUILD/prod).rglob('*.class'):
   target=SUPPORT/p.relative_to(BUILD/prod);assert not target.exists();target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,target)
if RECOMPILE_SUPPORT:
 ASSET_OVERLAY=BUILD/'support-assets';ASSET_OVERLAY.mkdir()
 for relative,digest in inventory['assets'].items():
  target=ASSET_OVERLAY/relative;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(PROGRAM.parent/'assets'/relative,target);assert hashlib.sha256(target.read_bytes()).hexdigest()==digest
 fresh={'production_directory':str(SUPPORT),'production_classes':17,'compile_stubs_in_runtime':False,'source_sha256':support_current_sources,'assets':inventory['assets'],'asset_overlay':str(ASSET_OVERLAY),'production_class_sha256':{str(p.relative_to(SUPPORT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in SUPPORT.rglob('*.class')}}
 (BUILD/'support-host-inputs.json').write_text(json.dumps(fresh,indent=2)+'\n')
 inventory=json.loads((BUILD/'support-host-inputs.json').read_text())
 for path,digest in inventory['source_sha256'].items():assert hashlib.sha256(Path(path).read_bytes()).hexdigest()==digest,path
 for path,digest in inventory['assets'].items():assert hashlib.sha256((ASSET_OVERLAY/path).read_bytes()).hexdigest()==digest,path
program_hashes={str(p.relative_to(SUPPORT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in SUPPORT.rglob('*.class')}
assert all(Path(name).stem.startswith(('History','CoreDrawPolicy','DrawPolicy')) for name in program_hashes)

cp=':'.join(map(str,[BUILD/'platform',JAR,JSON,BUILD/'dream',BUILD/'request',BUILD/'cg',SUPPORT]))
run(JDK/'javac','--release','8','-cp',cp,'-d',BUILD/'composite',*ROOT.glob('runtime/android_mechanism_gateway/src/**/*.java'));cp+=':'+str(BUILD/'composite')
run(JDK/'javac','--release','8','-cp',cp,'-d',BUILD/'tests',HERE/'host_tests/com/project7/localmanager/DreamCombinedHost.java');cp+=':'+str(BUILD/'tests')
out=run(JDK/'java','-Xverify:all','-Xlog:class+load=info:file='+str(BUILD/'class-origin.log'),'-Dp7.lifecycle='+str(LIFECYCLE).lower(),'-Dp7.repo='+str(ROOT),'-Dp7.overlay='+str(ASSET_OVERLAY),'-cp',cp,'com.project7.localmanager.DreamCombinedHost',ROOT/'analysis/project7/fixed-component-v2-stage/assets',BUILD/'combined-frames.json');(BUILD/'stdout.log').write_text(out);print(out,end='');print('host_artifacts='+str(BUILD))

consumer=run(ROOT/'.venv/bin/python',HERE/'host_tests/entry_consumer.py',BUILD/'combined-frames.json',BUILD/'consumer-result.json');print(consumer,end='');(BUILD/'stdout.log').write_text(out+consumer)
origin=(BUILD/'class-origin.log').read_text()
with zipfile.ZipFile(JAR) as jar:stock_defs={name for name in jar.namelist() if name.endswith('.class')}
program_dirs=[BUILD/'dream',BUILD/'request',BUILD/'cg',BUILD/'composite',SUPPORT]
own_defs={p.relative_to(d).as_posix() for d in program_dirs for p in d.rglob('*.class')}
assert not stock_defs&own_defs,sorted(stock_defs&own_defs)

for name in ['LocalProfileStore','LocalEventEngine','LocalPatrolEngine','LocalGatewayServer','LocalEconomyEngine','BsonLite','ProtoLite']+(['LocalWeekEngine'] if LIFECYCLE else []):
 rows=[line for line in origin.splitlines() if ' com.project7.localmanager.'+name+' source:' in line]
 assert len(rows)==1 and str(JAR) in urllib.parse.unquote(rows[0]),(name,rows)
assert '/stubs/' not in origin and '/reqstubs/' not in origin and '/coreapi/' not in origin and '/historyapi/' not in origin and '/cgapi/' not in origin
report={'status':'PASS','actual_manager_sha256':hashlib.sha256(JAR.read_bytes()).hexdigest(),'build':str(BUILD),'runtime_no_compile_stubs':True,'history_core_production':str(SUPPORT),'provided_support_compile_only_drift':support_compile_only_drift,'support_recompiled_current':RECOMPILE_SUPPORT,'support_host_inputs':str(BUILD/'support-host-inputs.json') if RECOMPILE_SUPPORT else str(PROGRAM.parent/'host-inputs.json'),'history_core_classes':program_hashes,'history_core_inputs':inventory,'class_origin':str(BUILD/'class-origin.log'),'checks':['actual private direct entry no ACK and reliable entry ACK-first+callback','actual private unknown direct false unchanged','actual original seq Result cache identity preserved, duplicate no second debit; new seq resumes pending; claim duplicate no business mutation','actual begin8/claim5 saved nonempty original candidate/terminal claim','actual Store.updateEconomy policy6 and original handleCalendar refresh seam','actual night negative same-day updateDay unlock consumer','actual Store writer failure no half exit','actual committed day+dream reset and postcommit op reset before reevaluation','actual original Gateway publication loop single route/hsd/pull','finite original P7/640 typed client producer/push/processing/start/callback/updateDay consumer'], 'limitations':['Android platform filesystem/context seams, not ART','finite function source projection and widget/network boundaries','no APK/D8/device/VM/native acceptance'],'composite_source_sha256':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in (ROOT/'runtime/android_mechanism_gateway/src').rglob('*.java')},'stock_program_definitions_disjoint':True,'request_coregap_source_sha256':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for folder in ['runtime/android_request_events/src','runtime/android_core_rpc/src'] for p in (ROOT/folder).rglob('*.java')},'source_sha256':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in HERE.rglob('*') if p.is_file() and '__pycache__' not in str(p)}}
if LIFECYCLE:report['checks']+=['actual complete8 emits current budget before original callback and cached begin replay','actual definite-precommit begin false Result uses original callback/reply/cache','actual claim-null emits message+completion-only carrier, no success tail; same seq retries successfully','actual matched private WeekRpc recovers old committed claim before updateServices','actual Store Week.apply creates new same-date transition and clears mode/context/receipt in same image','current Core7+History10 recompiled with exact new source/stub/asset host-inputs','original CityMember continuation observes budget, begin-negative/claim-negative callbacks unlock']
assert owned_before=={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in owned_sources},'Owned helper source drift during host proof'
(ROOT/('reports/project7-dream-lifecycle-host.json' if LIFECYCLE else 'reports/project7-dream-combined-host.json')).write_text(json.dumps(report,indent=2)+'\n')

assert program_hashes=={str(p.relative_to(SUPPORT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in SUPPORT.rglob("*.class")}

for path,digest in support_current_sources.items():assert hashlib.sha256(Path(path).read_bytes()).hexdigest()==digest,path
