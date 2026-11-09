#!/usr/bin/env python3
"""Re-run the real FailureSafeProfileProvider COC gateway host against a prepared stage.

This is a host-only JVM regression. It does not build an APK, install, or touch a device.
"""
from pathlib import Path
import argparse, hashlib, json, os, shutil, subprocess, tempfile

ROOT = Path(__file__).resolve().parents[5]
HERE = Path(__file__).resolve().parent
J = ROOT / 'toolchains/java/jdk-17.0.21+9/Contents/Home/bin'
SDK = ROOT / 'toolchains/android-sdk/platforms/android-32/android.jar'
JSON = ROOT / 'toolchains/json-20240303.jar'
D2J = ROOT / 'toolchains/dex2jar-v2.4/dex-tools-v2.4/d2j-dex2jar.sh'
LIB = str(ROOT / 'toolchains/dex2jar-v2.4/dex-tools-v2.4/lib/*')


def run(cmd, **kw):
    result = subprocess.run([str(x) for x in cmd], capture_output=True, text=True, **kw)
    if result.returncode:
        raise SystemExit((result.stdout or '') + (result.stderr or ''))
    return result.stdout + result.stderr


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--prepare', type=Path, required=True,
                        help='prepared project7-inputs directory containing stage/classes7.dex')
    parser.add_argument('--result', type=Path, default=ROOT / 'reports/project7-coc-wrapper-host-rerun.json')
    args = parser.parse_args()
    stage = args.prepare / 'stage'
    compiled = args.prepare / 'compiled/production-classes'
    classes7 = stage / 'classes7.dex'
    if not classes7.is_file() or not compiled.is_dir():
        raise SystemExit('prepared stage/classes7.dex or compiled production classes missing')
    work = Path(tempfile.mkdtemp(prefix='p7-coc-wrapper-'))
    try:
        frames = work / 'frames'
        platform = work / 'platform'
        tests = work / 'tests'
        framefix = work / 'framefix-classes'
        for directory in (frames, platform, tests, framefix):
            directory.mkdir(parents=True)
        manager = work / 'manager.jar'
        env = dict(os.environ, PATH=str(J) + ':' + os.environ.get('PATH', ''))
        run(['sh', D2J, '-f', '-o', manager, classes7], env=env)
        run([J / 'javac', '--release', '17', '-cp', LIB, '-d', framefix, HERE / 'FrameFix.java'])
        run([J / 'java', '-cp', f'{framefix}:{manager}:{SDK}:{LIB}', 'FrameFix', manager, frames / 'manager-translated-frames.jar'])
        core = [p for p in sorted((ROOT / 'offline/current/java/android_core_rpc/host_stubs').rglob('*.java'))
                if p.name not in ('AssetManager.java', 'Os.java')]
        baiye = sorted((ROOT / 'offline/current/java/android_baiye_transactions/host_tests/android').rglob('*.java'))
        run([J / 'javac', '--release', '8', '-d', platform, *core, *baiye,
             ROOT / 'offline/current/java/android_week_reset/host_tests/android/system/Os.java'])
        frames_jar = frames / 'manager-translated-frames.jar'
        run([J / 'javac', '--release', '8', '-cp', f'{compiled}:{platform}:{frames_jar}:{JSON}:{SDK}',
             '-d', tests, HERE / 'com/project7/localmanager/StoryCityCocGatewayHost.java'])
        host_result = work / 'host-result.json'
        output = run([J / 'java', '-Xverify:all',
                      '-cp', f'{compiled}:{platform}:{frames_jar}:{JSON}:{tests}',
                      '-Dp7.baiye.catalog=' + str(stage / 'assets/project7_baiye/catalog-v1.tsv'),
                      '-Dp7.baiye.fragments=' + str(stage / 'assets/project7_baiye/fragments-v1.tsv'),
                      '-Dp7.baiye.shop=' + str(stage / 'assets/project7_baiye_shop/catalog-v1.tsv'),
                      'com.project7.localmanager.StoryCityCocGatewayHost',
                      stage / 'assets', classes7, frames_jar, compiled, host_result])
        result = json.loads(host_result.read_text())
        result['command'] = 'python3 project7_bridge/android/android_project7_startup/proof/coc_wrapper/run.py --prepare <prepared-project7-inputs>'
        result['prepared_classes7_sha256'] = hashlib.sha256(classes7.read_bytes()).hexdigest()
        result['host_stdout'] = output.splitlines()[-8:]
        args.result.parent.mkdir(parents=True, exist_ok=True)
        args.result.write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
        print(json.dumps({k: result[k] for k in ('status', 'checks', 'classes7_sha256')}, sort_keys=True))
    finally:
        shutil.rmtree(work, ignore_errors=True)


if __name__ == '__main__':
    main()
