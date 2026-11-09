"""No D8/APK/device. Android32 javac then actual fixed original JVM consumers."""
from pathlib import Path
import argparse,hashlib,json,shutil,subprocess,sys,tempfile
R=Path(__file__).resolve().parents[2];H=Path(__file__).resolve().parent;sys.path.insert(0,str(R))
from tools.project7_story_mission_catalog import extend_asset
p=argparse.ArgumentParser();p.add_argument('--compiled',type=Path);p.add_argument('--atomic-week',action='store_true');p.add_argument('--main-production',action='store_true');p.add_argument('--week-baseline',action='store_true');p.add_argument('--inputs',type=Path,default=R/'analysis/project7/trial-seed-full-prepare-v1/project7-inputs-nejac7xh');p.add_argument('--manager',type=Path,default=R/'analysis/project7/trial-retry-hook-v1/manager-translated-frames.jar');a=p.parse_args();JAR=a.manager.resolve();J=R/'toolchains/java/jdk-17.0.21+9/Contents/Home/bin';SDK=R/'toolchains/android-sdk/platforms/android-32/android.jar'
BASE=a.inputs.resolve();OWN=(a.compiled.resolve()if a.compiled else BASE/'compiled')/'production-classes';B=Path(tempfile.mkdtemp(prefix='trial-retry-host-',dir=R/'analysis/project7'))
def run(*args):
 p=subprocess.run(list(map(str,args)),capture_output=True,text=True);assert p.returncode==0,p.stdout+p.stderr;return p.stdout+p.stderr
for name in ('api','production','platform','tests','assets'):(B/name).mkdir()
shutil.copytree(BASE/'stage/assets',B/'assets',dirs_exist_ok=True)
for name in ('economy.tsv','suppression.tsv'):(B/'assets'/name).write_bytes(extend_asset((R/'analysis/project7/manager/assets'/name).read_bytes(),name))
(B/'assets/project7_story_missions').mkdir(exist_ok=True);shutil.copy(R/'runtime/project7_story_mission_catalog/catalog-v1.tsv',B/'assets/project7_story_missions/catalog-v1.tsv')
run(J/'javac','--release','8','-cp',SDK,'-d',B/'api',*H.glob('compile_stubs/**/*.java'))
run(J/'javac','--release','8','-cp',str(SDK)+':'+str(B/'api'),'-d',B/'production',*H.glob('src/**/*.java'),*R.glob('runtime/android_story_missions/src/**/*.java'))
run(J/'javac','--release','8','-d',B/'platform',*[x for x in R.glob('runtime/android_core_rpc/host_stubs/**/*.java')if x.name not in ('AssetManager.java','Os.java')],*R.glob('runtime/android_baiye_transactions/host_tests/android/**/*.java'),R/'runtime/android_week_reset/host_tests/android/system/Os.java')
CP=':'.join(map(str,[B/'platform',JAR,R/'toolchains/json-20240303.jar',*([OWN,B/'production']if a.main_production else[B/'production',OWN])]))
run(J/'javac','--release','8','-cp',CP,'-d',B/'tests',*H.glob('host_tests/com/**/*.java'),R/'runtime/android_story_missions/host_tests/com/project7/localmanager/StoryMissionStoreHost.java')
out=run(J/'java','-Xverify:all','-Dp7.baiye.catalog='+str(R/'runtime/project7_baiye_catalog/catalog-v1.tsv'),'-Dp7.baiye.fragments='+str(R/'runtime/project7_baiye_catalog/fragments-v1.tsv'),'-cp',CP+':'+str(B/'tests'),'com.project7.localmanager.TrialRetryHost',B/'assets',B/'consumer-cases.json');print(out,end='');(B/'stdout.log').write_text(out)
week=run(J/'java','-Xverify:all','-Dp7.baiye.catalog='+str(R/'runtime/project7_baiye_catalog/catalog-v1.tsv'),'-Dp7.baiye.fragments='+str(R/'runtime/project7_baiye_catalog/fragments-v1.tsv'),'-cp',CP+':'+str(B/'tests'),'com.project7.localmanager.TrialWeekProbe',B/'assets',str(not a.week_baseline).lower());print(week,end='');(B/'week.log').write_text(week)
if a.atomic_week:
 atomic=run(J/'java','-Xverify:all','-Dp7.baiye.catalog='+str(R/'runtime/project7_baiye_catalog/catalog-v1.tsv'),'-Dp7.baiye.fragments='+str(R/'runtime/project7_baiye_catalog/fragments-v1.tsv'),'-cp',CP+':'+str(B/'tests'),'com.project7.localmanager.TrialAtomicWeekHost',B/'assets');print(atomic,end='');(B/'atomic-week.log').write_text(atomic)
consumer=run(R/'.venv/bin/python',H/'host_tests/consumer.py',B/'consumer-cases.json');print(consumer,end='');(B/'consumer.log').write_text(consumer)
(B/'result.json').write_text(json.dumps({'status':'PASS','inputs':str(BASE),'compiled':str(OWN),'atomic_week':a.atomic_week,'main_production_first':a.main_production,'week_baseline':a.week_baseline,'main_trial_class_sha256':hashlib.sha256((OWN/'com/project7/localmanager/TrialRetryGateway.class').read_bytes()).hexdigest(),'manager_sha256':hashlib.sha256(JAR.read_bytes()).hexdigest(),'source_hashes':{str(x.relative_to(R)):hashlib.sha256(x.read_bytes()).hexdigest()for x in H.rglob('*.java')},'catalog_pins':json.loads((R/'runtime/project7_story_mission_catalog/pins.json').read_text()),'limits':['synthetic profile/processing fixture; no native battle or original base27 route producer proof','named offline total3 / mandatory rearm policy; original server decrement timing not claimed','no compile stubs on runtime classpath','no D8/APK/emulator/device']},indent=2)+'\n');print(B)
