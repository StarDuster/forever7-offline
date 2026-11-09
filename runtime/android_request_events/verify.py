"""Android32/stubs-only compile + pinned original manager JVM finite proof.
No D8/APK/game/VM/device. Platform Context/AssetManager seams are host only.
"""
from pathlib import Path
import subprocess,hashlib,shutil,json,tempfile,sys
ROOT=Path(__file__).resolve().parents[2];HERE=Path(__file__).resolve().parent
JDK=ROOT/'toolchains/java/jdk-17.0.21+9/Contents/Home/bin';JAR=ROOT/('analysis/project7/request-event-hook-v1/manager-translated-frames.jar' if '--patched' in sys.argv else 'analysis/project7/host-original-engine/manager-translated-frames.jar');ANDROID=ROOT/'toolchains/android-sdk/platforms/android-32/android.jar';JSON=ROOT/'toolchains/json-20240303.jar'
assert hashlib.sha256((ROOT/'analysis/project7/manager/assets/new_player.bson').read_bytes()).hexdigest()=='6877cdc06532a11faa47e1855049f678db1c210de96caf1312c27c431b9875d7'
assert hashlib.sha256(JAR.read_bytes()).hexdigest()==('998594438eabb12f201157ea4344fd6574df76bfa37e6dc60233766234b72f3c' if '--patched' in sys.argv else '723440ecca7b479a9e1f1233222bbff92bfbf41dda18cdcd38d37a4d7ccaa685')
BUILD=Path(tempfile.mkdtemp(prefix='request-events-host-',dir=ROOT/'analysis/project7'))
def run(*args):
 p=subprocess.run(list(map(str,args)),capture_output=True,text=True)
 if p.returncode:raise RuntimeError(p.stdout+p.stderr)
 return p.stdout+p.stderr
for n in ['stubs','production','platform','tests']:(BUILD/n).mkdir()
run(JDK/'javac','--release','8','-d',BUILD/'stubs',*HERE.glob('compile_stubs/**/*.java'))
run(JDK/'javac','--release','8','-cp',str(ANDROID)+':'+str(BUILD/'stubs'),'-d',BUILD/'production',*HERE.glob('src/**/*.java'))
assert not (BUILD/'production/com/project7/localmanager/LocalEventEngine.class').exists()
run(JDK/'javac','--release','8','-d',BUILD/'platform',*[p for p in ROOT.glob('runtime/android_core_rpc/host_stubs/**/*.java') if p.name!='AssetManager.java'],*HERE.glob('host_stubs/**/*.java'))
cp=':'.join(map(str,[BUILD/'platform',JAR,JSON,BUILD/'production']))
if '--patched' in sys.argv:cp+=':'+str(ROOT/'analysis/project7/history-host-fixture-v1/production')+':'+str(ROOT/'analysis/project7/one-command-newbie354-v6/project7-inputs-c5igz3j9/compiled/production-classes')
run(JDK/'javac','--release','8','-cp',cp,'-d',BUILD/'tests',*[p for p in HERE.glob('host_tests/**/*.java') if p.name!='EndingTriggerHost.java'])
cp+=':'+str(BUILD/'tests')
output=run(JDK/'java','-Xverify:all','-cp',cp,'com.project7.localmanager.RequestEventsHost',ROOT/'runtime/project7_request_events/request-events.tsv',ROOT/'analysis/project7/fixed-component-stage/assets/event_graph.tsv')
gateway_options=(['-Dp7.history.assets='+str(ROOT/'analysis/project7/history-host-fixture-v1/assets'),'-Dp7.dispatch.prefix=true'] if '--patched' in sys.argv else [])+['-Dp7.ending.asset='+str(ROOT/'runtime/project7_request_events/ending-trigger-v1.json')]
gateway_output=run(JDK/'java','-Xverify:all',*gateway_options,'-cp',cp,'com.project7.localmanager.RequestGatewayHost',ROOT/'analysis/project7/manager/assets',ROOT/'runtime/project7_request_events/request-events.tsv',BUILD/'gateway-cases.json')
(BUILD/'gateway-stdout.log').write_text(gateway_output)
consumer=run(sys.executable,HERE/'host_tests/consumer.py',BUILD/'gateway-cases.json',BUILD/'consumer-result.json')
print(consumer,end='')
(BUILD/'stdout.log').write_text(output);print(output,end='');print(gateway_output,end='')

classes=sorted(p.relative_to(BUILD/'production').as_posix() for p in (BUILD/'production').rglob('*.class'))
assert len(classes)==10 and all(Path(name).stem.split('$')[0] in {'RequestEventCatalog','RequestEventAdmission','RequestEventGateway','EndingTriggerCatalog'} for name in classes),classes
abi=run(JDK/'javap','-p','-s','-classpath',JAR,'com.project7.localmanager.LocalEventEngine','com.project7.localmanager.LocalEventCatalog$Trigger','com.project7.localmanager.LocalEventCatalog$Event','com.project7.localmanager.LocalTutorialStore$Progress')
(BUILD/'stock-abi.txt').write_text(abi)
report={'format':'project7-request-events-host-v1','status':'PASS','original_framed_jar_sha256':hashlib.sha256(JAR.read_bytes()).hexdigest(),'java_verify_all':True,'android32_compile_only_stubs':True,'compile_stubs_packaged':False,'production_classes':classes,'stdout':output,'gateway_stdout':gateway_output,'build':str(BUILD),'stock_abi_path':str(BUILD/'stock-abi.txt'),'consumer_result':str(BUILD/'consumer-result.json'),'wire_cases':str(BUILD/'gateway-cases.json'),'history_fixture':({'source':'history-host-fixture-v1','gate':'all historical entries disabled, ordinary resource effects only; not final catalog acceptance'} if '--patched' in sys.argv else None),'source_sha256':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in HERE.glob('src/**/*.java')},'artifact_boundary':'original store/helper effects/frames/consumer finite proof; actual dispatch prefix integration tested separately; no native/game acceptance','no_D8_APK_VM_game_device':True}
(ROOT/('reports/project7-request-events-prefix-host.json' if '--patched' in sys.argv else 'reports/project7-request-events-host.json')).write_text(json.dumps(report,indent=2)+'\n')
