"""Build a local dependency-ready source bundle without changing source-export semantics.

The bundle contains the strict clean source export plus the pinned Project7 component
under `forever7-offline-project/.offline-deps/`. The component is explicitly marked
non-source and is never included in EXPORT-INVENTORY.json. No network access, APK,
asset extraction, private save, or signing key is used.
"""
from __future__ import annotations
import _bootstrap  # noqa: E402,F401

import argparse
import json
import tempfile
import zipfile
from pathlib import Path

from export_offline_project import export as export_source
from project7_component import sha

from _bootstrap import ROOT
COMPONENT_DESCRIPTOR = ROOT / 'upstream/project7/component.json'
EXTERNAL_COMPONENT = 'vendor/project7/component-v2.10.1.zip'
SOURCE_PREFIX = 'forever7-offline-project/'
COMPONENT_MEMBER = SOURCE_PREFIX + '.offline-deps/component-v2.10.1.zip'
DEPENDENCY_MEMBER = SOURCE_PREFIX + 'DEPENDENCY-INVENTORY.json'
BUNDLE_MEMBER = SOURCE_PREFIX + 'BUNDLE-INVENTORY.json'


def _component_pin():
    data = json.loads(COMPONENT_DESCRIPTOR.read_text())
    sha256 = data.get('sha256')
    size = data.get('bytes')
    if not isinstance(sha256, str) or len(sha256) != 64 or not isinstance(size, int) or size <= 0:
        raise ValueError('Invalid component descriptor')
    return sha256, size


def package(component_offline_input: Path, output: Path):
    component_offline_input = Path(component_offline_input)
    output = Path(output)
    if output.exists():
        raise ValueError('Output exists')
    expected_sha, expected_size = _component_pin()
    component = component_offline_input.read_bytes()
    if len(component) != expected_size or sha(component) != expected_sha:
        raise ValueError('Component offline input size/hash mismatch')
    with tempfile.TemporaryDirectory(prefix='p7-bundle-source-') as temporary:
        tmp = Path(temporary)
        source_zip = tmp / 'source.zip'
        export_source(source_zip)
        source_bytes = source_zip.read_bytes()
        with zipfile.ZipFile(source_zip) as source:
            names = source.namelist()
            if not names or any(not name.startswith(SOURCE_PREFIX) for name in names):
                raise ValueError('Unexpected source export layout')
            if any(name == SOURCE_PREFIX + '.offline-deps/component-v2.10.1.zip' for name in names):
                raise ValueError('Source export unexpectedly contains the component')
            inventory = json.loads(source.read(SOURCE_PREFIX + 'EXPORT-INVENTORY.json'))
            if len(inventory) != len(names) - 1:
                raise ValueError('Source inventory member count mismatch')
            for row in inventory:
                if row['path'] == EXTERNAL_COMPONENT:
                    raise ValueError('Source inventory contains external component')
                member = source.read(SOURCE_PREFIX + row['path'])
                if len(member) != row['bytes'] or sha(member) != row['sha256']:
                    raise ValueError('Source inventory hash mismatch: ' + row['path'])
            source_members = {name: source.read(name) for name in names}
        dependency = {
            'schema': 'forever7-local-dependency-bundle-v1',
            'purpose': 'Local private build dependency; not source and not redistributed',
            'source_prefix': SOURCE_PREFIX,
            'component': {
                'path': '.offline-deps/component-v2.10.1.zip',
                'bytes': len(component),
                'sha256': sha(component),
                'source': 'explicit --component-offline-input; verified against upstream/project7/component.json',
            },
            'source_export': {
                'sha256': sha(source_bytes),
                'inventory': SOURCE_PREFIX + 'EXPORT-INVENTORY.json',
                'semantics': 'source files only; dependency member is not in EXPORT-INVENTORY.json',
            },
            'excluded': ['original APK', 'full game resources', 'private saves', 'signing keys', 'toolchains', 'analysis'],
        }
        dependency_bytes = (json.dumps(dependency, indent=2, sort_keys=True) + '\n').encode()
        bundle_inventory = {
            'schema': 'forever7-local-bundle-v1',
            'source_export': {'sha256': sha(source_bytes), 'size': len(source_bytes)},
            'source_members': len(inventory),
            'component': {'bytes': len(component), 'sha256': sha(component)},
            'dependency_inventory': DEPENDENCY_MEMBER,
        }
        bundle_bytes = (json.dumps(bundle_inventory, indent=2, sort_keys=True) + '\n').encode()
        output.parent.mkdir(parents=True, exist_ok=True)
        created = False
        try:
            with zipfile.ZipFile(output, 'x', compression=zipfile.ZIP_STORED) as bundle:
                created = True
                for name in names:
                    bundle.writestr(name, source_members[name])
                bundle.writestr(COMPONENT_MEMBER, component)
                bundle.writestr(DEPENDENCY_MEMBER, dependency_bytes)
                bundle.writestr(BUNDLE_MEMBER, bundle_bytes)
        except BaseException:
            if created:
                output.unlink(missing_ok=True)
            raise
    return {
        'output': str(output),
        'bytes': output.stat().st_size,
        'sha256': sha(output.read_bytes()),
        'source_sha256': sha(source_bytes),
        'component_sha256': sha(component),
        'source_members': len(inventory),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--component-offline-input', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(package(args.component_offline_input, args.output), indent=2, sort_keys=True))


if __name__ == '__main__':
    main()
