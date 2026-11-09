"""Host-only synthetic stable bootstrap checks; no manager DEX/Android/game execution."""
from pathlib import Path
import hashlib
import json
import shutil
import subprocess
import time

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
JDK = ROOT / 'toolchains/java/jdk-17.0.21+9/Contents/Home/bin'
OUTPUT = ROOT / 'analysis/project7/stable-bootstrap-host-tests'
if OUTPUT.exists(): shutil.rmtree(OUTPUT)
OUTPUT.mkdir(parents=True)
sources = sorted((HERE / 'src').rglob('*.java'))
stubs = sorted((HERE / 'host_stubs').rglob('*.java'))
tests = [HERE / 'host_tests/com/project7/localmanager/StableBootstrapHostTests.java']
command = [str(JDK / 'javac'), '-source', '8', '-target', '8', '-Xlint:-options', '-d', str(OUTPUT)] + [str(p) for p in sources + stubs + tests]
subprocess.run(command, check=True)
run = [str(JDK / 'java'), '-cp', str(OUTPUT), 'com.project7.localmanager.StableBootstrapHostTests']
started = time.monotonic()
result = subprocess.run(run, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=30)
(ROOT / 'reports/project7-stable-bootstrap-host-tests.log').write_text(result.stdout)
print(result.stdout, end='')
if result.returncode != 0: raise RuntimeError('Host bootstrap checks failed')
passed = [line[5:] for line in result.stdout.splitlines() if line.startswith('PASS ')]
if not passed or 'HOST_BOOTSTRAP_TESTS_PASSED=' + str(len(passed)) not in result.stdout:
    raise RuntimeError('Missing bootstrap host success marker')
def metadata(path):
    return {'path': str(path.relative_to(ROOT)), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}
report = {'status': 'finite_synthetic_storage_host_tests_passed_not_manager_or_native_acceptance',
          'count': len(passed), 'passed': passed, 'seconds': time.monotonic() - started,
          'compile_command': command, 'run_command': run,
          'sources': [metadata(p) for p in sources], 'tests_and_stubs': [metadata(p) for p in stubs + tests],
          'never_package': str(OUTPUT.relative_to(ROOT)),
          'scope': 'Production bootstrap/stock API driver/coordinator against synthetic Properties-based profile and in-memory API stubs; no real BSON, private save, manager DEX, Android or game execution.'}
(ROOT / 'reports/project7-stable-bootstrap-host-tests.json').write_text(json.dumps(report, indent=2) + '\n')
