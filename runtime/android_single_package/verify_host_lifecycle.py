"""Compile/run finite host lifecycle stubs ONLY; never game/Android/DEX execution."""
from pathlib import Path
import hashlib
import json
import shutil
import subprocess
import time

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
JDK = ROOT / 'toolchains/java/jdk-17.0.21+9/Contents/Home/bin'
OUTPUT = ROOT / 'analysis/project7/process-owner-host-tests'
if OUTPUT.exists(): shutil.rmtree(OUTPUT)
OUTPUT.mkdir(parents=True)
sources = sorted((HERE / 'src').rglob('*.java'))
stubs = sorted((HERE / 'host_stubs').rglob('*.java'))
tests = sorted((HERE / 'host_tests').rglob('*.java'))
command = [str(JDK / 'javac'), '-source', '8', '-target', '8', '-Xlint:-options',
           '-d', str(OUTPUT)] + [str(p) for p in sources + stubs + tests]
subprocess.run(command, check=True)
run_command = [str(JDK / 'java'), '-cp', str(OUTPUT),
               'com.project7.localmanager.ProcessOwnerHostTests']
started = time.monotonic()
result = subprocess.run(run_command, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=30)
log = ROOT / 'reports/project7-process-owner-host-tests.log'
log.write_text(result.stdout)
print(result.stdout, end='')
if result.returncode != 0: raise RuntimeError('Host lifecycle tests failed; inspect ' + str(log))
passed = [line[5:] for line in result.stdout.splitlines() if line.startswith('PASS ')]
if not passed or 'HOST_LIFECYCLE_TESTS_PASSED=' + str(len(passed)) not in result.stdout:
    raise RuntimeError('Missing host test success marker')
def file_hash(path):
    return {'path': str(path.relative_to(ROOT)), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}
report = {'status': 'finite_host_lifecycle_tests_passed_not_native_acceptance',
          'count': len(passed), 'passed': passed, 'seconds': time.monotonic() - started,
          'compile_command': command, 'run_command': run_command,
          'sources': [file_hash(p) for p in sources],
          'tests_and_stubs': [file_hash(p) for p in stubs + tests],
          'never_package': str(OUTPUT.relative_to(ROOT)),
          'scope': 'No real manager/Android/game/native/socket/profile data execution; production owner + driver run against explicit finite in-memory API stubs.'}
(ROOT / 'reports/project7-process-owner-host-tests.json').write_text(json.dumps(report, indent=2) + '\n')
