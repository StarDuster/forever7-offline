"""Build the supported original APK into a local offline development APK."""
import _bootstrap  # noqa: E402,F401
import argparse
import hashlib
import io
import json
import os
from pathlib import Path
import secrets
import shutil
import subprocess
import sys
import tempfile
import zipfile

from _bootstrap import ROOT
APK_SHA256 = '12e57f77059f7f3964585f3a615410f3f9625101d885883cd4de4397f490c503'
SCRIPT640_SHA256 = '9284e0e00e18a04cb6169e5bbffbec3fd23037fa7dd19893fea3a3510ea1bb06'


def sha256(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def module_index(archive, destination):
    from extract_scripts import ScriptArchive
    from xdis.unmarshal import load_code
    source = ScriptArchive(archive)
    from resource_npk import string_id
    # Resolve the native filename ID, then verify the decoded module identity.
    # redirect.nxs is a native bootstrap payload rather than an init module.
    sign = string_id('init.nxs')
    matches = [number for number, entry in enumerate(source.entries) if entry[0] == sign]
    if len(matches) != 1:
        raise ValueError('Expected exactly one native init.nxs entry')
    code = load_code(io.BytesIO(source.read(matches[0])), 62211, code_objects={})
    if code.co_filename.replace('\\', '/') != 'init.py':
        raise ValueError('Native init.nxs entry does not decode to init.py')
    destination.write_text(json.dumps({'filename': 'init.py', 'sign': '%08x' % sign}) + '\n')



def prepare_scripts(base, work, offline=False):
    output = work / 'script640-original.npk'
    if output.exists():
        if output.is_symlink() or sha256(output) != SCRIPT640_SHA256:
            raise ValueError('Existing official640 script cache failed its fixed SHA-256')
        return output
    from preserve_cdn import parse_manifest, fetch_verified
    from rebuild_npk import rebuild, verify
    manifest = ROOT / 'upstream/project7/provenance/patch2.android.640.version'
    entries = [entry for entry in parse_manifest('android', 640, manifest.read_text()) if entry['part'] == 'script']
    cache = work / 'cdn'
    for entry in entries:
        target = cache / entry['path']
        if target.exists():
            verify(target, entry)
            continue
        if offline:
            raise ValueError('Offline cache is missing: ' + str(target))
        obj = fetch_verified(entry, cache)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(obj, target)
    rebuild(cache, 'android', 640, 'script', manifest, output, base)
    if sha256(output) != SCRIPT640_SHA256:
        raise ValueError('Reconstructed official640 script did not match the fixed baseline')
    return output


def prepare_project7_baseline(original, work):
    """The P7 route reconstructs640 from the original APK and fixed project delta.
    This step needs neither a second game package nor the official script CDN.
    """
    output = work / 'script640-original.npk'
    if output.exists():
        if output.is_symlink() or sha256(output) != SCRIPT640_SHA256:
            raise ValueError('Existing official640 script cache failed its fixed SHA-256')
        return output
    from project7_official_baseline import reconstruct
    reconstruct(original, output)
    if sha256(output) != SCRIPT640_SHA256:
        raise ValueError('Fixed official640 entry patch reconstructed the wrong baseline')
    return output


def toolchain_view(work, java_home, build_tools, android_jar):
    view = work / 'toolchain-view'
    links = {
        'java/jdk-17.0.21+9/Contents/Home/bin': java_home / 'bin',
        'java/jdk-17.0.21+9-jre/Contents/Home/bin': java_home / 'bin',
        'build-tools/android-37.0': build_tools,
        'android-sdk/platforms/android-32/android.jar': android_jar,
    }
    for relative, target in links.items():
        link = view / relative
        link.parent.mkdir(parents=True, exist_ok=True)
        if link.is_symlink():
            link.unlink()
        elif link.exists():
            raise ValueError('Refusing to replace existing toolchain path: ' + str(link))
        link.symlink_to(target.resolve(), target_is_directory=target.is_dir())
    return view


def select_component(args, root=ROOT, environ=None):
    """Explicit CLI > explicit env/local > cache > vendor default; never silently ignore explicit input."""
    environ = os.environ if environ is None else environ
    if args.component is not None:
        path = Path(args.component)
        if not path.is_file():
            raise ValueError('Explicit --component file does not exist')
        return path
    if args.component_offline_input is not None:
        from project7_fetch_component import resolve
        return resolve(None, Path(args.component_offline_input))
    if args.component_url is not None:
        from project7_fetch_component import resolve
        return resolve(args.component_url, None)
    offline = environ.get('P7_COMPONENT_OFFLINE_INPUT')
    if offline:
        from project7_fetch_component import resolve
        return resolve(None, Path(offline))
    url = environ.get('P7_COMPONENT_URL')
    if url:
        from project7_fetch_component import resolve
        return resolve(url, None)
    cache = root / '.offline-deps' / 'component-v2.10.1.zip'
    if cache.is_file():
        return cache
    vendor = root / 'vendor/project7/component-v2.10.1.zip'
    if vendor.is_file():
        return vendor
    from project7_fetch_component import resolve
    return resolve(None, None)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('original', type=Path)
    parser.add_argument('--build-dir', type=Path, default=ROOT / '.offline-build', help='Private build/cache/signing directory outside exported project')
    parser.add_argument('--output', type=Path, help='Default: beside the original with -offline.apk suffix')
    parser.add_argument('--backend', choices=('project7', 'legacy'), default='project7', help='Select one backend at build time; legacy is retained for comparison')
    parser.add_argument('--prepare-only', action='store_true', help='Project7: prepare and compile inputs only; never assemble/sign an APK')
    parser.add_argument('--render-mode', choices=('astc','png'), default='astc', help='Project7 render bootstrap: original ASTC default or explicit PNG compatibility')
    parser.add_argument('--java-home', type=Path, default=Path(os.environ.get('JAVA_HOME', str(ROOT / 'toolchains/java/jdk-17.0.21+9/Contents/Home'))), help='JDK 17 home containing bin/java, bin/javac, bin/keytool')
    parser.add_argument('--build-tools', type=Path, default=ROOT / 'toolchains/build-tools/android-37.0', help='Android SDK build-tools directory containing zipalign, lib/d8.jar, lib/apksigner.jar')
    parser.add_argument('--android-jar', type=Path, default=ROOT / 'toolchains/android-sdk/platforms/android-32/android.jar', help='Android SDK platform android.jar (API 32 tested)')
    parser.add_argument('--offline', action='store_true', help='Legacy: require verified script cache; Project7 script reconstruction is always local')
    parser.add_argument('--keystore', type=Path)
    parser.add_argument('--key-alias', default='forever7-local')
    parser.add_argument('--key-password-env', help='Environment variable containing supplied keystore password')
    parser.add_argument('--expected-cert-sha256', help='Fail before publish unless the signed APK certificate matches this SHA-256', default=None)
    parser.add_argument('--component', type=Path, help='Pinned Project7 component zip; otherwise default vendor path or P7_COMPONENT_URL')
    parser.add_argument('--component-url', help='Explicit Project7 component URL (or P7_COMPONENT_URL)')
    parser.add_argument('--component-offline-input', type=Path, help='Pre-downloaded pinned component zip')
    args = parser.parse_args()
    if args.prepare_only and args.backend != 'project7':
        parser.error('--prepare-only requires --backend project7')
    original = args.original.resolve()
    output = (args.output or original.with_name(original.stem + '-offline.apk')).resolve()
    work = args.build_dir.resolve()
    if original == output or original.is_relative_to(work):
        parser.error('Original APK must be outside build directory and differ from output')
    if work == ROOT or ROOT.is_relative_to(work):
        parser.error('Build directory must not contain the project')
    if sha256(original) != APK_SHA256:
        parser.error('Unsupported original APK SHA-256; expected ' + APK_SHA256)
    for path in [args.java_home / 'bin' / n for n in ('java', 'javac', 'keytool')] + [args.build_tools / n for n in ('zipalign', 'lib/d8.jar', 'lib/apksigner.jar')] + [args.android_jar]:
        if not path.is_file():
            parser.error('Missing toolchain file: ' + str(path))
    os.umask(0o077)
    work.mkdir(parents=True, exist_ok=True)
    work.chmod(0o700)
    if args.backend == 'project7':
        script = prepare_project7_baseline(original, work)
    else:
        with zipfile.ZipFile(original) as archive:
            if archive.namelist().count('assets/script.npk') != 1:
                raise ValueError('Expected exactly one original script.npk')
            base = work / 'apk-original-script.npk'
            with archive.open('assets/script.npk') as source, base.open('wb') as target:
                shutil.copyfileobj(source, target)
        script = prepare_scripts(base, work, args.offline)
    view = toolchain_view(work, args.java_home, args.build_tools, args.android_jar)
    run = None
    if args.backend == 'project7':
        from project7_build_inputs import prepare
        from project7_compile import compile_sources
        run = Path(tempfile.mkdtemp(prefix='project7-inputs-', dir=work))
        stage, compiled = run / 'stage', run / 'compiled'
        component = select_component(args)
        prepared = prepare(original, script, stage, component=component, render_mode=args.render_mode)
        compilation = compile_sources(stage, compiled, view)
        if args.prepare_only:
            report = {'backend': 'project7', 'original_sha256': APK_SHA256,
                      'original_unchanged': sha256(original) == APK_SHA256,
                      'stage': str(stage), 'compiled': str(compiled),
                      'production_classes': len(compilation['classes']),
                      'apk_built': False, 'native_runtime_tested': False,
                      'goal_complete': False}
            if not report['original_unchanged']:
                raise ValueError('Original APK changed during preparation')
            (work / 'offline-project-build.json').write_text(json.dumps(report, indent=2) + '\n')
            print(json.dumps(report))
            return
    else:
        index = work / 'moduleindex.jsonl'
        module_index(script, index)
        patched = work / 'script-offline.npk'
        subprocess.run([sys.executable, str(ROOT / 'offline/tools/patch_bootstrap.py'), str(script), '--module-index', str(index), '--output', str(patched), '--embed-runtime', str(ROOT / 'offline/runtime')], check=True)
    if args.keystore:
        if not args.keystore.is_file() or not args.key_password_env or not os.environ.get(args.key_password_env):
            parser.error('Supplied keystore needs an existing file and --key-password-env')
        password = os.environ[args.key_password_env]
        key = args.keystore.resolve()
    else:
        key = work / 'signing/offline-dev.p12'
        password_file = work / 'signing/password.txt'
        password_file.parent.mkdir(parents=True, exist_ok=True)
        if key.exists() and not password_file.exists():
            raise ValueError('Existing private signing key has no password file')
        if not password_file.exists():
            password_file.write_text(secrets.token_urlsafe(32))
        password_file.chmod(0o600)
        password = password_file.read_text()
    built = None
    if args.backend == 'project7':
        from build_project7_android import build
        built = build(original, stage, compiled, output, view, keystore=key, key_alias=args.key_alias, password=password, expected_certificate_sha256=args.expected_cert_sha256)
    else:
        from build_android import build
        built = build(original, patched, output, view, keystore=key, key_alias=args.key_alias, password=password)
    if sha256(original) != APK_SHA256:
        raise ValueError('Original APK changed during build')
    report = {'backend': args.backend, 'original_sha256': APK_SHA256, 'script_index': 640, 'original_unchanged': True,
              'output': str(output), 'output_sha256': sha256(output), 'render_mode': args.render_mode, 'native_runtime_tested': False,
              'event_battle_status': 'host-tested; native verification pending', 'goal_complete': False}
    if isinstance(built, dict):
        report['render_mode'] = built.get('render_mode', report['render_mode'])
        report['signature_certificate_sha256'] = built.get('signature_certificate_sha256')
    (work / 'offline-project-build.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report))
    if run is not None:
        shutil.rmtree(run)


if __name__ == '__main__':
    main()
