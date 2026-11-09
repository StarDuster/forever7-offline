"""Host-only proof that each inline consumer unwraps a real FailureSafeProfileProvider."""
from pathlib import Path
import argparse,hashlib,json,shutil,subprocess,tempfile
ROOT=Path(__file__).resolve().parents[4]; HERE=Path(__file__).resolve().parent
JDK=ROOT/'toolchains/java/jdk-17.0.21+9/Contents/Home/bin'; JSON=ROOT/'toolchains/json-20240303.jar'
p=argparse.ArgumentParser();p.add_argument('--prepare',type=Path,default=ROOT/'analysis/project7/story-city-integration-prepare-v65/project7-inputs-83akv7as');p.add_argument('--manager-frames',type=Path,default=ROOT/'analysis/project7/action-ledger-code20-v2/manager-translated-frames.jar');p.add_argument('--evidence',type=Path,default=ROOT/'reports/project7-wrapper-unwrap-host.json');a=p.parse_args();OWN=a.prepare/'compiled/production-classes';A=a.prepare/'stage/assets';SRC=ROOT/'project7_bridge/android/android_project7_startup/verification_sources/wrapper'
t=Path(tempfile.mkdtemp(prefix='wrapper-unwrap-',dir='/tmp'))
def run(*cmd):
 r=subprocess.run(list(map(str,cmd)),capture_output=True,text=True,timeout=120)
 if r.returncode:raise SystemExit(r.stdout+r.stderr)
 return r.stdout+r.stderr
try:
 cp=':'.join(map(str,[OWN,a.manager_frames,JSON]))
 run(JDK/'javac','--release','8','-cp',cp,'-d',t,*HERE.glob('seams/**/*.java'),*(SRC/'com/project7/localmanager').glob('*.java'))
 out=run(JDK/'java','-Xverify:all','-cp',':'.join(map(str,[t,OWN,a.manager_frames,JSON])),'com.project7.localmanager.WrapperUnwrapHost',A)
 ev={'schema':'project7-wrapper-unwrap-host-v1','status':'PASS','prepare':str(a.prepare),'manager_sha256':hashlib.sha256(a.manager_frames.read_bytes()).hexdigest(),'output':out,'scope':'real FailureSafeProfileProvider instance passed to each inline unwrap helper; no D8/APK/native'};a.evidence.write_text(json.dumps(ev,indent=2)+'\n');print(out)
finally:shutil.rmtree(t)
