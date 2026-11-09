"""Finite JVM host for actual Project7StartupPlatform.OwnedBackend.
Uses v63 OWN/f81b/full stage; only Android Service fields are host seams.
Ports 23333/23334 must be free. No D8/APK/native; temp output removed."""
from pathlib import Path
import argparse, hashlib, json, shutil, socket, subprocess, tempfile
ROOT=Path(__file__).resolve().parents[4]
HERE=Path(__file__).resolve().parent
JDK=ROOT/'toolchains/java/jdk-17.0.21+9/Contents/Home/bin'
JSON=ROOT/'toolchains/json-20240303.jar'
p=argparse.ArgumentParser()
p.add_argument('--prepare',type=Path,default=ROOT/'.offline-build-v8-authdiag-20261106')
p.add_argument('--manager-frames',type=Path,default=ROOT/'analysis/project7/action-ledger-code20-v2/manager-translated-frames.jar')
p.add_argument('--evidence',type=Path,default=ROOT/'reports/project7-owned-backend-host.json')
p.add_argument('--profile-fixture',type=Path,default=ROOT/'local-checkpoints/device-pulls/v7-after1004-20261106/files/profiles/offline_9b460eb9bee83d34cf4b1608.bson')
p.add_argument('--assets',type=Path)
a=p.parse_args(); OWN=a.prepare/'compiled/production-classes'; ASSETS=a.assets if a.assets else a.prepare/'stage/assets'
ANDROID=ROOT/'toolchains/android-sdk/platforms/android-32/android.jar'
SEAMS=HERE/'seams'; SRC=ROOT/'project7_bridge/android/android_project7_startup/verification_sources/owned_backend'
OWN_SOURCES=sorted((ROOT/'offline/current/java/android_single_package/src').rglob('*.java'))+sorted((ROOT/'project7_bridge/android/android_project7_startup/src').rglob('*.java'))+[ROOT/'offline/current/java/android_resource_init/src/com/forever7/offline/ResourceImporter.java',ROOT/'offline/current/java/android_resource_init/src/com/forever7/offline/Project7ResourceSnapshot.java']
for port in (23333,23334):
 s=socket.socket(); ok=s.connect_ex(('127.0.0.1',port)); s.close()
 if ok==0: raise SystemExit('port busy: %d'%port)
t=Path(tempfile.mkdtemp(prefix='owned-backend-',dir='/tmp'))
def run(*cmd):
 r=subprocess.run(list(map(str,cmd)),capture_output=True,text=True,timeout=180)
 if r.returncode: raise SystemExit(r.stdout+r.stderr)
 return r.stdout+r.stderr
try:
 run(JDK/'javac','--release','8','-cp',':'.join(map(str,[OWN,a.manager_frames,ANDROID])),'-d',t/'ours',*OWN_SOURCES)
 run(JDK/'javac','--release','8','-cp',':'.join(map(str,[t/'ours',OWN,a.manager_frames,JSON])),'-d',t,*SEAMS.glob('**/*.java'),*(SRC/'com/project7/localmanager').glob('*.java'))
 CP=':'.join(map(str,[t,t/'ours',OWN,a.manager_frames,JSON]))
 out=run(JDK/'java','-Xverify:all','-cp',CP,'com.project7.localmanager.ActualOwnedBackendHost',ASSETS,t/'profile')
 if 'READY=true HOOK=true IDENTITY=true CREDS=true FAILED=false' not in out or 'DRAINED' not in out: raise AssertionError(out)
 import socket as _socket
 for port in (23333,23334):
  probe=_socket.socket(); ok=probe.connect_ex(('127.0.0.1',port)); probe.close()
  if ok==0: raise AssertionError('port busy after real backend drained: %d'%port)
 proof=run(JDK/'java','-Xverify:all','-cp',CP,'com.project7.localmanager.ProfileHandoffRealProfileHost',ASSETS,a.profile_fixture)
 if 'HANDOFF_SAME_STORE=true CONSUMED_ONCE=true FULL_LOADS_PER_REQUEST=true STABLE_PERSISTED=true PROFILE_BYTES_IN_HANDOFF=false' not in proof:
  raise AssertionError(proof)
 ev={'schema':'project7-owned-backend-host-v1','status':'PASS','prepare':str(a.prepare),'manager_frames':str(a.manager_frames),'manager_sha256':hashlib.sha256(a.manager_frames.read_bytes()).hexdigest(),'output':out,'profile_fixture_sha256':hashlib.sha256(a.profile_fixture.read_bytes()).hexdigest(),'profile_proof_output':proof,'ports':{'23333':'free','23334':'free'},'scope':'actual OwnedBackend start/ready/identity/credentials/close/drain and one-shot handoff real-profile full-load/persistence on JVM; Android Service fields host seam only; no D8/APK/native; fixture copied to temp only'}
 ev['production_overlay_hashes']={str(f.relative_to(t/'ours')):hashlib.sha256(f.read_bytes()).hexdigest() for f in sorted((t/'ours').rglob('*.class'))}
 ev['production_class_hashes']={str(f.relative_to(OWN)):hashlib.sha256(f.read_bytes()).hexdigest() for f in sorted(OWN.rglob('*.class'))}
 ev['host_source_hashes']={str(f.relative_to(ROOT)):hashlib.sha256(f.read_bytes()).hexdigest() for f in sorted(SRC.rglob('*.java'))}
 ev['temporary_profile_and_classes_removed_on_exit']=True
 a.evidence.write_text(json.dumps(ev,indent=2)+'\n'); print(out)
finally: shutil.rmtree(t)
