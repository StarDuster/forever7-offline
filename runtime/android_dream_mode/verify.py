"""Static Android32 compile and finite pure reducer + stock BSON/writer proof.
This does not claim actual patrol/night runner or gateway coordination is wired.
"""
from pathlib import Path
import subprocess,tempfile,hashlib
ROOT=Path(__file__).resolve().parents[2];HERE=Path(__file__).resolve().parent
JDK=ROOT/'toolchains/java/jdk-17.0.21+9/Contents/Home/bin';ANDROID=ROOT/'toolchains/android-sdk/platforms/android-32/android.jar';JAR=ROOT/'analysis/project7/host-original-engine/manager-translated-frames.jar';JSON=ROOT/'toolchains/json-20240303.jar'
assert hashlib.sha256(JAR.read_bytes()).hexdigest()=='723440ecca7b479a9e1f1233222bbff92bfbf41dda18cdcd38d37a4d7ccaa685'
BUILD=Path(tempfile.mkdtemp(prefix='dream-mode-host-',dir=ROOT/'analysis/project7'))
def run(*args):
 p=subprocess.run(list(map(str,args)),text=True,capture_output=True)
 if p.returncode:raise RuntimeError(p.stdout+p.stderr)
 return p.stdout+p.stderr
for n in ['stubs','production','platform','tests']:(BUILD/n).mkdir()
run(JDK/'javac','--release','8','-d',BUILD/'stubs',*HERE.glob('compile_stubs/**/*.java'))
run(JDK/'javac','--release','8','-cp',str(ANDROID)+':'+str(BUILD/'stubs'),'-d',BUILD/'production',*HERE.glob('src/**/*.java'))
assert not (BUILD/'production/com/project7/localmanager/BsonLite.class').exists()
run(JDK/'javac','--release','8','-d',BUILD/'platform',*ROOT.glob('runtime/android_core_rpc/host_stubs/**/*.java'))
cp=':'.join(map(str,[BUILD/'platform',JAR,JSON,BUILD/'production']))
run(JDK/'javac','--release','8','-cp',cp,'-d',BUILD/'tests',*[p for p in HERE.glob('host_tests/**/*.java') if p.name!='DreamCombinedHost.java'])
output=run(JDK/'java','-Xverify:all','-cp',cp+':'+str(BUILD/'tests'),'com.project7.localmanager.DreamStateHost',ROOT/'runtime/project7_dream_catalog/catalog-v1.tsv',ROOT/'analysis/project7/manager/assets/event_graph.tsv');(BUILD/'stdout.log').write_text(output);print(output,end='')

more=run(JDK/"java","-Xverify:all","-cp",cp+":"+str(BUILD/"tests"),"com.project7.localmanager.DreamCoordinatorHost",ROOT/"analysis/project7/manager/assets",ROOT/"runtime/project7_dream_catalog/catalog-v1.tsv",BUILD/"entry-frames.json");(BUILD/"stdout.log").write_text(output+more);print(more,end="");print("host_artifacts="+str(BUILD))

consumer=run(ROOT/".venv/bin/python",HERE/"host_tests/entry_consumer.py",BUILD/"entry-frames.json",BUILD/"entry-consumer-result.json");print(consumer,end="");(BUILD/"stdout.log").write_text(output+more+consumer)

extra=run(JDK/"java","-Xverify:all","-cp",cp+":"+str(BUILD/"tests"),"com.project7.localmanager.DreamFailureWeekHost",ROOT/"analysis/project7/manager/assets",ROOT/"runtime/project7_dream_catalog/catalog-v1.tsv");print(extra,end="");(BUILD/"stdout.log").write_text(output+more+consumer+extra)
