"""Direct fixed-manager LocalServiceEngine.recover boundary host on current OWN/f81b."""
from pathlib import Path
import argparse,hashlib,json,shutil,subprocess,tempfile
ROOT=Path(__file__).resolve().parents[4];HERE=Path(__file__).resolve().parent
JDK=ROOT/'toolchains/java/jdk-17.0.21+9/Contents/Home/bin';JSON=ROOT/'toolchains/json-20240303.jar'
p=argparse.ArgumentParser();p.add_argument('--prepare',type=Path,default=ROOT/'analysis/project7/story-city-integration-prepare-v65/project7-inputs-83akv7as');p.add_argument('--manager-frames',type=Path,default=ROOT/'analysis/project7/action-ledger-code20-v2/manager-translated-frames.jar');p.add_argument('--evidence',type=Path,default=ROOT/'reports/project7-recover-semantics-host.json');a=p.parse_args();OWN=a.prepare/'compiled/production-classes';SRC=ROOT/'project7_bridge/android/android_project7_startup/verification_sources/recover'
manager_sha=hashlib.sha256(a.manager_frames.read_bytes()).hexdigest()
assert manager_sha=='f81b686eb3cfdb7e87f5c9eae5075652d08afb38c8d104ed81b3baebcb703c0f', 'unreviewed manager frames'
assert not (OWN/'com/project7/localmanager/LocalServiceEngine.class').exists(), 'OWN shadows original recovery engine'
host_sources={str(f.relative_to(ROOT)):hashlib.sha256(f.read_bytes()).hexdigest() for f in SRC.rglob('*.java')}
t=Path(tempfile.mkdtemp(prefix='recover-semantics-',dir='/tmp'))
def run(*cmd):
 r=subprocess.run(list(map(str,cmd)),capture_output=True,text=True,timeout=120)
 if r.returncode:raise SystemExit(r.stdout+r.stderr)
 return r.stdout+r.stderr
try:
 cp=':'.join(map(str,[OWN,a.manager_frames,JSON]))
 run(JDK/'javac','--release','8','-cp',cp,'-d',t,*HERE.glob('seams/**/*.java'),*(SRC/'com/project7/localmanager').glob('*.java'))
 out=run(JDK/'java','-Xverify:all','-cp',':'.join(map(str,[t,OWN,a.manager_frames,JSON])),'com.project7.localmanager.RecoverSemanticsHost')
 ev={'schema':'project7-recover-semantics-host-v1','status':'PASS','prepare':str(a.prepare),'manager_sha256':hashlib.sha256(a.manager_frames.read_bytes()).hexdigest(),'host_sources':host_sources,'output':out,'scope':'actual LocalServiceEngine.recover boundary; no production edit/D8/APK/native'};a.evidence.write_text(json.dumps(ev,indent=2)+'\n');print(out)
finally:shutil.rmtree(t)
