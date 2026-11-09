"""Bounded protocol/UI leaf proof; no Android/native execution or DEX/APK output."""
from pathlib import Path
import hashlib,json,subprocess,shutil,time
ROOT=Path(__file__).resolve().parents[2];HERE=Path(__file__).resolve().parent
JDK=ROOT/'toolchains/java/jdk-17.0.21+9/Contents/Home/bin';BUILD=ROOT/'analysis/project7/repair-host-verification'
if BUILD.exists():shutil.rmtree(BUILD)
BUILD.mkdir(parents=True)
sources=sorted((HERE/'src').rglob('*.java'));stubs=sorted((HERE/'host_stubs').rglob('*.java'));tests=sorted((HERE/'host_tests').rglob('*.java'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
frozen={str(p):sha(p) for p in sources+stubs+tests+[HERE/'host_tests/send_python_marker.py',ROOT/'runtime/project7_startup_hook.py']}
def run(command):
 r=subprocess.run(list(map(str,command)),capture_output=True,text=True,timeout=30)
 if r.returncode:raise RuntimeError(r.stdout+r.stderr)
 return r.stdout+r.stderr
compile=[JDK/'javac','-source','8','-target','8','-Xlint:-options','-d',BUILD,*sources,*stubs,*tests];run(compile)
command=[JDK/'java','-Xverify:all','-cp',BUILD,'com.forever7.offline.RepairHostTests',ROOT/'.venv/bin/python',HERE/'host_tests/send_python_marker.py'];start=time.monotonic();output=run(command);print(output,end='')
passed=[v[5:] for v in output.splitlines() if v.startswith('PASS ')];assert len(passed)==4 and 'REPAIR_HOST_GROUPS_PASSED=4' in output
for path,expected in frozen.items():assert sha(Path(path))==expected
(ROOT/'reports/project7-repair-host-tests.log').write_text(output)
(ROOT/'reports/project7-repair-host-tests.json').write_text(json.dumps({'status':'finite_protocol_files_and_explicit_android_ui_leaves_passed_not_android_native_acceptance','groups':len(passed),'passed':passed,'seconds':time.monotonic()-start,'compile_command':list(map(str,compile)),'run_command':list(map(str,command)),'sources':[{'path':str(p.relative_to(ROOT)),'sha256':sha(p)} for p in sources+stubs+tests+[HERE/'host_tests/send_python_marker.py',ROOT/'runtime/project7_startup_hook.py']],'never_package':['runtime/android_project7_repair/host_stubs','runtime/android_project7_repair/host_tests',str(BUILD.relative_to(ROOT))],'scope':'Real bounded file protocol, temp write/fsync/atomic replace and host JVM. FileObserver events, main queue, Activity/Application and AlertDialog are explicit host leaves; no inotify/Android/JNI/client process exit accepted.'},indent=2)+'\n')
