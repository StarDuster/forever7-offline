"""Build a locally signed Android development package with a patched script.

This does not bundle the separately preserved full resource snapshot. Signing
and ZIP alignment are verified before the output replaces an existing file.
The development certificate is generated locally and is not a release key.
"""
import _bootstrap  # noqa: E402,F401
import argparse
import copy
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import zipfile

from resource_npk import ResourceArchive
from android_resource_init import compile_resource_initializer, patch_resource_manifest

from _bootstrap import ROOT
DEV_PASSWORD = 'forever7-local-dev'


def build(original, script, output, toolchains, keystore=None, key_alias="forever7-local", password=None):
    if 0xfb54f059 not in ResourceArchive(script).entries:
        raise ValueError('Script archive is missing the native redirect bootstrap')
    java_home = toolchains / 'java/jdk-17.0.21+9-jre/Contents/Home/bin'
    build_tools = toolchains / 'build-tools/android-37.0'
    password = password or DEV_PASSWORD
    keystore = keystore or toolchains / 'signing/offline-dev.p12'
    if not keystore.exists():
        keystore.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run([str(java_home / 'keytool'), '-genkeypair', '-storetype', 'PKCS12',
                        '-keystore', str(keystore), '-storepass:env', 'F7_BUILD_KEY_PASSWORD',
                        '-alias', key_alias, '-keyalg', 'RSA', '-keysize', '2048',
                        '-validity', '3650', '-dname', 'CN=Forever7 Local Development'], check=True,
                       env=dict(os.environ, F7_BUILD_KEY_PASSWORD=password))
    keystore.chmod(0o600)
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='f7-build-', dir=output.parent) as directory:
        temporary = Path(directory)
        initializer_dex, initializer_manifest = compile_resource_initializer(ROOT, toolchains, temporary)
        unsigned, aligned, signed = [temporary / n for n in ('unsigned.apk', 'aligned.apk', 'signed.apk')]
        with zipfile.ZipFile(original) as source, zipfile.ZipFile(unsigned, 'w', allowZip64=False) as target:
            names = source.namelist()
            if names.count('assets/script.npk') != 1:
                raise ValueError('Expected exactly one assets/script.npk')
            dex_indices = [int(n[7:-4] or 1) for n in names if n.startswith('classes') and n.endswith('.dex') and (n[7:-4].isdigit() or n == 'classes.dex')]
            initializer_dex_name = 'classes%d.dex' % (max(dex_indices) + 1)
            for record in source.infolist():
                name = record.filename
                if name.upper().startswith('META-INF/') and name.upper().endswith(('.MF', '.SF', '.RSA', '.DSA', '.EC')):
                    continue
                replacement = copy.copy(record)
                with target.open(replacement, 'w') as destination:
                    if name == 'AndroidManifest.xml':
                        destination.write(patch_resource_manifest(source.read(record)))
                    elif name == 'assets/script.npk':
                        with script.open('rb') as data:
                            shutil.copyfileobj(data, destination, 1024 * 1024)
                    else:
                        with source.open(record) as data:
                            shutil.copyfileobj(data, destination, 1024 * 1024)
            target.write(initializer_dex, initializer_dex_name)
            target.write(initializer_manifest, 'assets/offline_resource_manifest.json')
        subprocess.run([str(build_tools / 'zipalign'), '-f', '4', str(unsigned), str(aligned)], check=True)
        unsigned.unlink()
        signer = [str(java_home / 'java'), '-jar', str(build_tools / 'lib/apksigner.jar')]
        subprocess.run(signer + ['sign', '--ks', str(keystore), '--ks-key-alias', key_alias,
                                '--ks-pass', 'env:F7_BUILD_KEY_PASSWORD', '--out', str(signed), str(aligned)], check=True, env=dict(os.environ, F7_BUILD_KEY_PASSWORD=password))
        subprocess.run(signer + ['verify', '--verbose', str(signed)], check=True)
        subprocess.run([str(build_tools / 'zipalign'), '-c', '4', str(signed)], check=True)
        with zipfile.ZipFile(signed) as archive:
            with archive.open('assets/script.npk') as data:
                actual = hashlib.file_digest(data, 'sha256').hexdigest()
        with script.open('rb') as data:
            expected = hashlib.file_digest(data, 'sha256').hexdigest()
        if actual != expected:
            raise ValueError('Signed APK contains an unexpected script archive')
        signed.replace(output)
    resource_manifest_hash = hashlib.sha256((ROOT / 'offline/current/java/android_resource_init/resource_manifest.json').read_bytes()).hexdigest()
    report = {'file': str(output), 'bytes': output.stat().st_size,
              'script_sha256': expected, 'signature_verified': True, 'zip_alignment_verified': True,
              'full_resource_snapshot_bundled': False, 'resource_initializer_included': True,
              'resource_initializer_native_tested': False, 'resource_manifest_sha256': resource_manifest_hash, 'runtime_tested': False,
              'development_build': True}
    output.with_suffix('.build.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('original', type=Path)
    parser.add_argument('--script', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--toolchains', type=Path, default=ROOT / 'toolchains')
    args = parser.parse_args()
    build(args.original, args.script, args.output, args.toolchains)


if __name__ == '__main__':
    main()
