"""Finite real manager engine evidence only; no production policy or APK tools."""
from pathlib import Path
import hashlib,json,subprocess,tempfile
R=Path(__file__).resolve().parents[2]; H=Path(__file__).resolve().parent
jar=R/'analysis/project7/event-reset-week-hook-v2/manager-translated-frames.jar'
assert hashlib.sha256(jar.read_bytes()).hexdigest()=='af930ec43effa7ee491d5dd391e4ff338a7e540f25c7bed43f4a9fb54a002e78'
a=R/'analysis/project7/manager/assets';assert hashlib.sha256((a/'new_player.bson').read_bytes()).hexdigest()=='6877cdc06532a11faa47e1855049f678db1c210de96caf1312c27c431b9875d7'
b=Path(tempfile.mkdtemp(prefix='tutorial-blocker-host-',dir=R/'analysis/project7')); j=R/'toolchains/java/jdk-17.0.21+9/Contents/Home/bin'
# Previously verified platform seams only. These contain no engine/profile implementation.
platform=R/'analysis/project7/event-reset-week-host-rg_s00yv/platform'
cp=':'.join(map(str,[platform,jar,R/'toolchains/json-20240303.jar',R/'analysis/project7/event-reset-week-host-rg_s00yv/production']))
def run(*args):
 p=subprocess.run(list(map(str,args)),capture_output=True,text=True);assert p.returncode==0,p.stdout+p.stderr;return p.stdout+p.stderr
src=H/'host_tests/com/project7/localmanager/TutorialBlockerHost.java'
run(j/'javac','--release','8','-cp',cp,'-d',b,src)
out=run(j/'java','-Xverify:all','-cp',cp+':'+str(b),'com.project7.localmanager.TutorialBlockerHost',a);print(out,end='')
(b/'result.json').write_text(json.dumps({'status':'PASS','manager_sha256':hashlib.sha256(jar.read_bytes()).hexdigest(),'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'stdout':out,'limits':['private complete invoked directly: not claimed battle101 reached','93 begin only: no draw acceptance/card/reveal simulated','platform seams reused; all business engine/catalog/codec classes from pinned actual jar','no production changes or D8/APK/game']},indent=2)+'\n');print(b)

# Execute only installed replacement functions, no original game bytecode.
import importlib.util,types
spec=importlib.util.spec_from_file_location('tutorial_skip',R/'runtime/offline_tutorials.py');mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
avatar=types.SimpleNamespace(newbeeData=types.SimpleNamespace(clent_trigger_event_list=[10,93]),sent=[])
mod.skip_newbee_request(avatar,10);mod.skip_newbee_request(avatar,93)
assert avatar.newbeeData.clent_trigger_event_list==[] and avatar.sent==[]
print('PASS installed skip only clears local queue; no server finish invocation')
