"""Focused v63/f81b host for the shared ending-trigger gateway consumer.

Uses the actual published v63 compiled OWN classes, the f81b manager frame JAR,
and the full v63 stage assets. Only the host test class is compiled; no production
owner source is recompiled, no asset is filtered, and no synthetic event graph is
injected. Proves ordinary/reliable manager dispatch reaches the shared gateway,
the current original failed-rule table yields typed false, and state is unchanged.

No D8, APK, game, emulator or device.
"""
from pathlib import Path
import argparse
import hashlib
import json
import shutil
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
JDK = ROOT / 'toolchains/java/jdk-17.0.21+9/Contents/Home/bin'
ANDROID = ROOT / 'toolchains/android-sdk/platforms/android-32/android.jar'
JSON_JAR = ROOT / 'toolchains/json-20240303.jar'
STAGE = ROOT / 'analysis/project7/story-city-integration-prepare-v63/project7-inputs-m5cehde8/stage'
COMPILED = ROOT / 'analysis/project7/story-city-integration-prepare-v63/project7-inputs-m5cehde8/compiled'
MANAGER_JAR = ROOT / 'analysis/project7/action-ledger-code20-v2/manager-translated-frames.jar'
MANAGER_SHA = 'f81b686eb3cfdb7e87f5c9eae5075652d08afb38c8d104ed81b3baebcb703c0f'
HOST = HERE / 'host_tests/com/project7/localmanager/EndingTriggerHost.java'


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def run(*args):
    process = subprocess.run([str(value) for value in args], capture_output=True, text=True)
    if process.returncode:
        raise RuntimeError(process.stdout + process.stderr)
    return process.stdout + process.stderr


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--prepare', type=Path)
    args = parser.parse_args()
    actual_prepare = args.prepare is not None
    if actual_prepare:
        globals()['STAGE'] = args.prepare / 'stage'
        globals()['COMPILED'] = args.prepare / 'compiled'
    check = {
        'manager_jar_sha256': sha(MANAGER_JAR),
        'stage_build_inputs_sha256': sha(STAGE / 'build-inputs.json'),
        'compiled_inputs_sha256': sha(COMPILED / 'compile-inputs.json'),
        'ending_catalog_sha256': sha(STAGE / 'assets/offline/ending-trigger-v1.json'),
        'request_event_catalog_sha256': sha(STAGE / 'assets/offline/request-events.tsv'),
    }
    assert check['manager_jar_sha256'] == MANAGER_SHA, check
    report = json.loads((COMPILED / 'compile-inputs.json').read_text())
    assert len(report['classes']) >= 252, len(report['classes'])
    assert any(row['path'] == 'com/project7/localmanager/EndingTriggerCatalog.class' for row in report['classes'])
    assert check['ending_catalog_sha256'] == '1792a804aba72c806a7bb73dce3a42baf52695ff0edc5b476fbbe05c89095431', check
    work = Path(tempfile.mkdtemp(prefix='ending-trigger-v63-', dir=ROOT / 'analysis/project7'))
    try:
        platform, tests = work / 'platform', work / 'tests'
        platform.mkdir(); tests.mkdir()
        run(JDK / 'javac', '--release', '8', '-d', platform,
            *[p for p in ROOT.glob('runtime/android_core_rpc/host_stubs/**/*.java') if p.name != 'AssetManager.java'],
            *HERE.glob('host_ending_stubs/**/*.java'))
        classpath = ':'.join(map(str, (platform, MANAGER_JAR, JSON_JAR, COMPILED / 'production-classes')))
        run(JDK / 'javac', '--release', '8', '-cp', classpath, '-d', tests, HOST)
        output = work / 'cases.json'
        stdout = run(JDK / 'java', '-Xverify:all', '-cp', classpath + ':' + str(tests),
                     'com.project7.localmanager.EndingTriggerHost', STAGE / 'assets', output)
        cases = json.loads(output.read_text())
        after = {
            'stage_build_inputs_sha256': sha(STAGE / 'build-inputs.json'),
            'ending_catalog_sha256': sha(STAGE / 'assets/offline/ending-trigger-v1.json'),
            'request_event_catalog_sha256': sha(STAGE / 'assets/offline/request-events.tsv'),
        }
        assert after['ending_catalog_sha256'] == check['ending_catalog_sha256'], after
        assert after['request_event_catalog_sha256'] == check['request_event_catalog_sha256'], after
        result = {
            'format': 'project7-ending-trigger-v66-host-v1' if actual_prepare else 'project7-ending-trigger-v63-host-v1',
            'mode': 'compiled' if actual_prepare else 'baseline',
            'status': 'PASS',
            'scope': ('v66' if actual_prepare else 'v63') + ' actual compiled OWN + f81b manager + full stage assets; ordinary/reliable dispatch; no D8/APK/native',
            'stage': str(STAGE),
            'compiled': str(COMPILED),
            'manager_jar': str(MANAGER_JAR),
            'checks': check,
            'checks_after': after,
            'production_classes': len(report['classes']),
            'stdout': stdout,
            'cases': cases,
            'commands': [
                'python3 runtime/android_request_events/verify_ending_trigger.py',
                'javac --release 8 host-ending-stubs + host test only (production classes are v63 compiled inputs)',
                'java -Xverify:all -cp platform:f81b-manager:json:' + ('v66' if actual_prepare else 'v63') + '-production-classes:tests com.project7.localmanager.EndingTriggerHost ' + ('v66' if actual_prepare else 'v63') + '/stage/assets cases.json',
            ],
            'boundaries': [
                'current original mainline_week_info has no nonzero false_event; host proves typed rejection only',
                'stock snapshot reconciles known daily/login ldd and city.jpvt before the request; host captures after that and requires request bytes + canonical event/week/claim/ending documents unchanged',
                'synthetic positive remains a helper unit test, not a host story/event claim',
                'exact original server success ordering and week advance remain unproven',
            ],
        }
        evidence = 'reports/project7-ending-trigger-v66-host.json' if actual_prepare else 'reports/project7-ending-trigger-host.json'
        (ROOT / evidence).write_text(json.dumps(result, indent=2) + '\n')
        print('PASS ' + ('v66' if actual_prepare else 'v63') + '/f81b real dispatch: production no-rule typed false; no push/effect/completion; Progress/profile unchanged')
        print('report=' + evidence)
    finally:
        shutil.rmtree(work, ignore_errors=True)


if __name__ == '__main__':
    main()
