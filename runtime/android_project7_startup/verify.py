"""Finite host orchestration + real-source Android32 javac; never DEX/APK/game run."""
from pathlib import Path
import argparse
import hashlib
import json
import shutil
import subprocess
import time

ROOT=Path(__file__).resolve().parents[2]
HERE=Path(__file__).resolve().parent
parser=argparse.ArgumentParser()
parser.add_argument('--generated',type=Path,default=ROOT/'analysis/project7/official-build-inputs-v3/generated-java/com/forever7/offline/Project7BundledResources.java')
args=parser.parse_args()
JDK=ROOT/'toolchains/java/jdk-17.0.21+9/Contents/Home/bin'
ANDROID=ROOT/'toolchains/android-sdk/platforms/android-32/android.jar'
MANAGER_JAR=ROOT/'analysis/project7/action-ledger-code20-v2/manager-translated-frames.jar'
V63_OWN=ROOT/'analysis/project7/story-city-integration-prepare-v63/project7-inputs-m5cehde8/compiled/production-classes'
BUILD=ROOT/'analysis/project7/startup-coordinator-verification'
if BUILD.exists():shutil.rmtree(BUILD)
for name in ['host-only','compile-only-stubs','production-classes']:(BUILD/name).mkdir(parents=True)

def run(command,timeout=60):
    result=subprocess.run([str(v) for v in command],stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,timeout=timeout)
    if result.returncode:raise RuntimeError(result.stdout)
    return result.stdout

def meta(path):return {'path':str(path.relative_to(ROOT)), 'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}

own_sources=sorted((HERE/'src').rglob('*.java'))
startup_modules=[]
for module in ('android_draw_policy','android_history_draw','android_selector_draw',
               'android_dynamic_draw','android_wish_draw','android_story_missions',
               'android_story_city','android_trial_retry','android_mechanism_gateway'):
    startup_modules += sorted((ROOT/'runtime'/module/'src').rglob('*.java'))
owner_sources=sorted((ROOT/'runtime/android_single_package/src').rglob('*.java'))
core=ROOT/'runtime/android_autologin/src/com/netease/qrzd/AutoLoginCore.java'
host_stubs=sorted((HERE/'host_stubs').rglob('*.java'))+[ROOT/'runtime/android_single_package/host_stubs/com/project7/localmanager/ManagerApiStubs.java']
host_tests=sorted((HERE/'host_tests').rglob('*.java'))
host_frozen={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in owner_sources+[core]+own_sources+host_stubs+host_tests}
host_command=[JDK/'javac','-source','8','-target','8','-Xlint:-options','-cp',str(ANDROID)+':'+str(MANAGER_JAR)+':'+str(V63_OWN),'-d',BUILD/'host-only',*owner_sources,core,*own_sources ,*host_stubs,*host_tests]
run(host_command)
started=time.monotonic()
host_run=[JDK/'java','-cp',BUILD/'host-only','com.project7.localmanager.StartupHostTests']
host_output=run(host_run,30)
(ROOT/'reports/project7-startup-coordinator-host-tests.log').write_text(host_output)
print(host_output,end='')
passed=[line[5:] for line in host_output.splitlines() if line.startswith('PASS ')]
if not passed or 'STARTUP_HOST_GROUPS_PASSED='+str(len(passed)) not in host_output:raise RuntimeError('Missing host success marker')

compile_stubs=[ROOT/'runtime/android_single_package/compile_stubs/com/project7/localmanager/ManagerApiStubs.java',ROOT/'runtime/android_autologin/compile_stubs/com/netease/neox/NativeInterface.java']
stub_command=[JDK/'javac','-source','8','-target','8','-Xlint:-options','-cp',ANDROID,'-d',BUILD/'compile-only-stubs',*compile_stubs]
run(stub_command)
resources=sorted((ROOT/'runtime/android_resource_init/src').rglob('*.java'))
login=sorted((ROOT/'runtime/android_autologin/src').rglob('*.java'))
collection=sorted((ROOT/'runtime/android_collection/src').rglob('*.java'))
repair=sorted((ROOT/'runtime/android_project7_repair/src').rglob('*.java'))
production_sources=resources+owner_sources+login+collection+repair+own_sources+[args.generated]
production_frozen={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in production_sources}
production_command=[JDK/'javac','-source','8','-target','8','-Xlint:-options','-cp',str(ANDROID)+':'+str(BUILD/'compile-only-stubs')+':'+str(MANAGER_JAR)+':'+str(V63_OWN),'-d',BUILD/'production-classes',*production_sources]
run(production_command)
for path,expected in dict(host_frozen,**production_frozen).items():
    if hashlib.sha256(Path(path).read_bytes()).hexdigest()!=expected:
        raise RuntimeError('Input changed during verification: '+path)
compiled=sorted((BUILD/'production-classes').rglob('*.class'))
for forbidden in ['com/netease/neox/NativeInterface.class','com/project7/localmanager/GatewayService.class','com/project7/localmanager/LocalAccountStore.class','com/project7/localmanager/LocalGatewayServer.class','com/project7/localmanager/LocalProfileStore.class']:
    if (BUILD/'production-classes'/forbidden).exists():raise RuntimeError('Compile stub leaked into production output')
report={'status':'real_source_android32_compile_and_finite_host_orchestration_passed_not_android_acceptance',
        'host_groups':len(passed),'passed':passed,'seconds':time.monotonic()-started,
        'host_compile_command':list(map(str,host_command)),'host_run_command':list(map(str,host_run)),
        'production_compile_command':list(map(str,production_command)),
        'own_sources':[meta(p) for p in own_sources], 'production_sources':[meta(p) for p in production_sources],
        'host_inputs':[meta(p) for p in host_stubs+host_tests],
        'production_class_count':len(compiled), 'production_classes':[meta(p) for p in compiled],
        'never_package':[str((BUILD/'host-only').relative_to(ROOT)),str((BUILD/'compile-only-stubs').relative_to(ROOT))],
        'scope':'Real production sources compile together; host tests inject finite receipt/backend/base-Activity leaves. No actual resource hash scan/profile creation/collection engine/native callback/Android VM/game/device/APK execution.'}
(ROOT/'reports/project7-startup-coordinator-verification.json').write_text(json.dumps(report,indent=2)+'\n')
print('PASS Android32 combined production compile; classes='+str(len(compiled))+'; stubs isolated')
