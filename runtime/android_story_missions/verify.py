"""No D8/APK/device. Android32 javac then actual fixed original JVM consumers."""
from pathlib import Path
import argparse,hashlib,json,os,shutil,subprocess,sys,tempfile
R=Path(__file__).resolve().parents[2];H=Path(__file__).resolve().parent;sys.path.insert(0,str(R))
from tools.project7_story_mission_catalog import extend_asset
p=argparse.ArgumentParser();p.add_argument('--manager',type=Path,default=R/'analysis/project7/story-city-coc-gateway-v36/manager-translated-frames.jar');a=p.parse_args();JAR=a.manager.resolve();J=R/'toolchains/java/jdk-17.0.21+9/Contents/Home/bin';SDK=R/'toolchains/android-sdk/platforms/android-32/android.jar'
BASE=R/'analysis/project7/story-city-integration-prepare-v41/project7-inputs-7ptsklbq';OWN=BASE/'compiled/production-classes';B=Path(tempfile.mkdtemp(prefix='story-missions-host-',dir=R/'analysis/project7'))
BAIYE=['-Dp7.baiye.catalog='+str(R/'runtime/project7_baiye_catalog/catalog-v1.tsv'),'-Dp7.baiye.fragments='+str(R/'runtime/project7_baiye_catalog/fragments-v1.tsv'),'-Dp7.baiye.shop='+str(R/'runtime/project7_baiye_shop_catalog/catalog-v1.tsv')]
def run(*args):
 p=subprocess.run(list(map(str,args)),capture_output=True,text=True);assert p.returncode==0,p.stdout+p.stderr;return p.stdout+p.stderr
for name in ('api','production','platform','tests','assets'):(B/name).mkdir()
# Symlink the shared read-only stage assets; only small overrides are written.
for source in (BASE/'stage/assets').rglob('*'):
 rel=source.relative_to(BASE/'stage/assets');target=B/'assets'/rel
 if source.is_dir():target.mkdir(parents=True,exist_ok=True)
 else:
  target.parent.mkdir(parents=True,exist_ok=True);os.link(source,target)
def override(name,data):
 path=B/'assets'/name
 if path.is_symlink() or path.exists():path.unlink()
 path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(data)
require=__import__('hashlib').sha256
assert require((B/'assets/economy.tsv').read_bytes()).hexdigest()=='44ff1083dee5021acf5e673acf92d4e2074e25db394e5dfba44b4c3ee38f0564'
assert require((B/'assets/suppression.tsv').read_bytes()).hexdigest()=='574d8c7e63a4ce648705b3f4d1cfbfced9e30fbf9cfd513cb09138290812bc86'
(B/'assets/project7_story_missions').mkdir(exist_ok=True)
override('project7_story_missions/catalog-v1.tsv',(R/'runtime/project7_story_mission_catalog/catalog-v1.tsv').read_bytes())
for name in ('special-selector-v1.json','menu10-entry-v1.json'):
 override('project7_story_shared/'+name,(R/'runtime/android_story_shared/catalog'/name).read_bytes())

run(J/'javac','--release','8','-cp',SDK,'-d',B/'api',*H.glob('compile_stubs/**/*.java'))
run(J/'javac','--release','8','-cp',str(SDK)+':'+str(B/'api'),'-d',B/'production',*H.glob('src/**/*.java'))
run(J/'javac','--release','8','-d',B/'platform',*[x for x in R.glob('runtime/android_core_rpc/host_stubs/**/*.java')if x.name not in ('AssetManager.java','Os.java')],*R.glob('runtime/android_baiye_transactions/host_tests/android/**/*.java'),R/'runtime/android_week_reset/host_tests/android/system/Os.java')
CP=':'.join(map(str,[B/'platform',JAR,R/'toolchains/json-20240303.jar',OWN]))
run(J/'javac','--release','8','-cp',CP,'-d',B/'tests',*H.glob('host_tests/com/**/*.java'))
out=run(J/'java',*BAIYE,'-Xverify:all','-cp',CP+':'+str(B/'tests'),'com.project7.localmanager.StoryMissionHost',B/'assets');print(out,end='');(B/'stdout.log').write_text(out)
more=run(J/'java',*BAIYE,'-Xverify:all','-cp',CP+':'+str(B/'tests'),'com.project7.localmanager.StoryMissionStoreHost',B/'assets',B/'consumer-cases.json');print(more,end='');(B/'store.log').write_text(more)
consumer=run(R/'.venv/bin/python',H/'host_tests/consumer.py',B/'consumer-cases.json');print(consumer,end='');(B/'consumer.log').write_text(consumer)
generic=run(J/'java',*BAIYE,'-Xverify:all','-cp',CP+':'+str(B/'tests'),'com.project7.localmanager.StoryMainline32Host',B/'assets');print(generic,end='');(B/'mainline32.log').write_text(generic)
(B/'result.json').write_text(json.dumps({'status':'PASS','manager_sha256':hashlib.sha256(JAR.read_bytes()).hexdigest(),'source_hashes':{str(x.relative_to(R)):hashlib.sha256(x.read_bytes()).hexdigest()for x in H.rglob('*.java')},'catalog_pins':json.loads((R/'runtime/project7_story_mission_catalog/pins.json').read_text()),'mainline32_generic':{'host':'com.project7.localmanager.StoryMainline32Host','chains':['area2 route31-1 menu28 scenes 1124..1126','area1 route5 menu4 scenes 22010..22012 with 22012 success 10006','area2 route21 menu20 scene 1114 loss/win success 20058'],'checks':110,'evidence':['query/-1 and unknown-route fallback','real Store begin/loss/win/replay','postcommit victory trace and cs advance','mission economy M va=2 spend','selector11 token/area descriptor','area1 consumeVictory guard rejects; full offline finish first push/reload/loss/duplicate/route-week-mutex','batch success rows offered only on real win/current route','first pushEvents/save/reload carries success; loss no offer; duplicate inert; route switch/new week/mutex boundaries','1115 cross-route prerequisite still blocks admission'],'limit':'synthetic profile/progress only; success offer is triggered by the real post-victory status/stages consumer, not the immediate push frame; no native battle, rate, or client selection proof'},'limits':['synthetic profile/processing fixture; no native battle or original base27 route producer proof','retry policy not changed','no compile stubs on runtime classpath','no D8/APK/emulator/device']},indent=2)+'\n')
# Keep compact evidence, not another permanent stage/compiled copy.
EVIDENCE = R / 'reports/story-missions-host-latest'
EVIDENCE.mkdir(parents=True, exist_ok=True)
for artifact in B.iterdir():
    if artifact.is_file() and artifact.suffix in ('.json', '.log'):
        destination = EVIDENCE / artifact.name
        temporary = destination.with_suffix(destination.suffix + '.tmp')
        shutil.copyfile(artifact, temporary)
        temporary.replace(destination)
# This point is reached only after every verifier succeeded and evidence is saved.
shutil.rmtree(B)
print(EVIDENCE)
