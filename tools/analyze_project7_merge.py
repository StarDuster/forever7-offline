"""Static, reproducible inputs/conflicts for a single Project7 APK.

Never installs or executes either input. Outputs metadata and selected DEX
instructions, not a merged/signed APK. Original files remain unchanged.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import xml.etree.ElementTree as ET
import zipfile

from loguru import logger
logger.remove()
from androguard.core.apk import APK
from androguard.core.dex import DEX

ROOT = Path(__file__).resolve().parents[1]
ANDROID = '{http://schemas.android.com/apk/res/android}'


def digest(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda: f.read(1048576), b''):
            h.update(block)
    return h.hexdigest()


def inspect(path, out, label):
    apk = APK(str(path))
    manifest = apk.get_android_manifest_xml()
    application = manifest.find('application')
    classes = {}
    hooks = []
    startup_calls = []
    with zipfile.ZipFile(path) as archive:
        if label == 'game':
            (out / 'game-neox.xml').write_bytes(archive.read('assets/neox.xml'))
        entries = {x.filename: {'size': x.file_size, 'crc32': '%08x' % x.CRC}
                   for x in archive.infolist()}
        for name in archive.namelist():
            if not re.fullmatch(r'classes\d*\.dex', name):
                continue
            dex = DEX(archive.read(name))
            for cls in dex.get_classes():
                classes[cls.get_name()] = name
                if label != 'game':
                    continue
                for method in cls.get_methods():
                    instructions = [(i.get_name(), i.get_output()) for i in method.get_instructions()]
                    matches = [v for op, v in instructions if op.startswith('const-string') and
                               ('project7' in v.lower() or re.search(r'(?<![0-9])2333[34](?![0-9])', v))]
                    calls = [v for op, v in instructions if op.startswith('invoke') and
                             any(s in v for s in ('OfflinePatchInstaller;', 'Project7LoginDialog;'))]
                    if calls and cls.get_name() == 'Lcom/netease/qrzd/Client;':
                        startup_calls.append({'class': cls.get_name(), 'method': method.get_name(),
                                              'descriptor': method.get_descriptor(), 'calls': calls})
                    if matches:
                        file = out / ('game-hook-%03d.dis' % len(hooks))
                        file.write_text('CLASS %s\nMETHOD %s %s\n%s\n' %
                                        (cls.get_name(), method.get_name(), method.get_descriptor(),
                                         '\n'.join(op + ' ' + v for op, v in instructions)))
                        hooks.append({'class': cls.get_name(), 'method': method.get_name(),
                                      'descriptor': method.get_descriptor(), 'dex': name,
                                      'matches': matches, 'evidence': str(file.relative_to(ROOT))})
    resources = apk.get_android_resources()
    public = {}
    for package in resources.get_packages_names():
        for item in ET.fromstring(resources.get_public_resources(package)):
            public[item.attrib['id']] = dict(item.attrib, package=package)
    info = {'path': str(path), 'sha256': digest(path), 'bytes': path.stat().st_size,
            'package': apk.get_package(), 'version': apk.get_androidversion_name(),
            'min_sdk': apk.get_min_sdk_version(), 'target_sdk': apk.get_target_sdk_version(),
            'main_activity': apk.get_main_activity(),
            'application': {k.removeprefix(ANDROID): v for k, v in application.attrib.items()},
            'services': apk.get_services(), 'dex_files': sorted(set(classes.values())),
            'class_count': len(classes), 'entry_count': len(entries),
            'resource_count': len(public), 'hooks': hooks, 'startup_calls': startup_calls}
    return info, entries, classes, public


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--game', type=Path, default=Path.home() / 'Downloads/Project7-game-v1.6.1.apk')
    parser.add_argument('--manager', type=Path, default=Path.home() / 'Downloads/Project7-local-manager-v2.10.1.apk')
    parser.add_argument('--stage', action='store_true', help='Stage manager DEX/assets only; does not create an APK')
    args = parser.parse_args()
    out = ROOT / 'analysis/project7/merge'
    out.mkdir(parents=True, exist_ok=True)
    game, ge, gc, gr = inspect(args.game, out, 'game')
    manager, me, mc, mr = inspect(args.manager, out, 'manager')
    assets = sorted(n for n in me if n.startswith('assets/'))
    conflicts = [{'path': n, 'game': ge[n], 'manager': me[n]} for n in assets if n in ge]
    resource_collisions = [{'id': n, 'game': gr[n], 'manager': mr[n]} for n in mr if n in gr]
    tool_names = ('aapt', 'aapt2', 'd8', 'apksigner', 'zipalign', 'apktool', 'jadx', 'baksmali', 'smali')
    tools = {n: [str(p.relative_to(ROOT)) for p in (ROOT / 'toolchains').rglob(n) if p.is_file()]
             for n in tool_names}
    report = {'format': 'project7-single-apk-integration-inventory-v1',
              'reproduce': '.venv/bin/python tools/analyze_project7_merge.py',
              'static_only': True, 'merged_apk_built': False, 'runtime_verified': False,
              'game': game, 'manager': manager, 'toolchains': tools,
              'duplicate_classes': sorted(set(gc) & set(mc)),
              'manager_dex_mapping': {name: 'classes%d.dex' % (len(game['dex_files']) + i + 1)
                                      for i, name in enumerate(manager['dex_files'])},
              'manager_assets': [{'path': n, **me[n]} for n in assets],
              'asset_path_conflicts': conflicts, 'resource_id_collisions': resource_collisions,
              'manager_native_libraries': sorted(n for n in me if n.startswith('lib/')),
              'integration_constraints': [
                  'Rename added DEX files; never overwrite game classes.dex.',
                  'Resource IDs are global inside one APK; manager resource table cannot simply replace game resources.arsc.',
                  'Keep original game Application and launcher chain unless a verified lifecycle adapter deliberately wraps them.',
                  'Use a headless gateway lifecycle adapter or re-link all manager UI resources and references.',
                  'Start gateway and bootstrap before client login; await readiness rather than a fixed delay.',
                  'Store merged app profiles under its own Context, and explicitly migrate any old manager private data.',
                  'Manager requires API26 versus game API23: raise merged minSdk to26 initially or implement/verify compatibility shims.',
                  'Retain GatewayService static running/save-lock semantics when replacing its notification and overlay lifecycle.',
                  'Full offline installation requires resource bundling/installer validation beyond this code merge.'
              ]}
    if args.stage:
        if report['duplicate_classes'] or conflicts:
            raise ValueError('Resolve class/assets conflicts before staging')
        stage = out / 'staging'
        stage.mkdir(exist_ok=True)
        mapping = dict(report['manager_dex_mapping'])
        mapping.update({n: n for n in assets})
        changes = []
        with zipfile.ZipFile(args.manager) as archive:
            for source, destination in sorted(mapping.items()):
                target_file = (stage / destination).resolve()
                if not target_file.is_relative_to(stage.resolve()):
                    raise ValueError('Unsafe staged path')
                data = archive.read(source)
                target_file.parent.mkdir(parents=True, exist_ok=True)
                target_file.write_bytes(data)
                changes.append({'action': 'add', 'source_entry': source,
                                'destination_entry': destination, 'bytes': len(data),
                                'sha256': hashlib.sha256(data).hexdigest()})
        manifest = {'format': 'project7-merge-staging-v1', 'status': 'inputs_only_not_installable',
                    'base_apk': game['path'], 'base_sha256': game['sha256'],
                    'manager_apk': manager['path'], 'manager_sha256': manager['sha256'],
                    'files': changes, 'omitted': ['resources.arsc', 'res/', 'AndroidManifest.xml', 'original signatures'],
                    'remaining': ['headless startup adapter and running/save-lock semantics',
                                  'game launch readiness hook and no-login local profile selection',
                                  'Manifest minSdk/lifecycle changes', 'APK repack/align/sign/verify',
                                  'native runtime and clean install verification']}
        (stage / 'changes.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')
        report['staging'] = {'path': str(stage.relative_to(ROOT)), 'files': len(changes),
                             'bytes': sum(x['bytes'] for x in changes), 'installable': False}
    target = ROOT / 'reports/project7-merge-inventory.json'
    target.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({'report': str(target.relative_to(ROOT)), 'duplicate_classes': len(report['duplicate_classes']),
                      'asset_path_conflicts': len(conflicts), 'resource_id_collisions': len(resource_collisions),
                      'game_hook_methods': len(game['hooks'])}, ensure_ascii=False))


if __name__ == '__main__':
    main()
