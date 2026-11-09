"""Export only reviewed source paths; never traverse the rest of the workspace.

The pinned Project7 component is an external dependency input, not source: it is
listed in the allowlist for dependency accounting but must never enter the source
ZIP. Its pin and fetch modes live in upstream/project7/component.json and
tools/project7_fetch_component.py.
"""
import _bootstrap  # noqa: E402,F401
import argparse
import hashlib
import json
from pathlib import Path
import zipfile

from _bootstrap import ROOT
ALLOWLIST = ROOT / 'offline-project-allowlist.json'
EXTERNAL_DEPENDENCIES = {'vendor/project7/component-v2.10.1.zip'}


def export(output):
    allow = json.loads(ALLOWLIST.read_text())['files']
    if len(allow) != len(set(allow)):
        raise ValueError('Duplicate allowlist path')
    paths = [name for name in allow if name not in EXTERNAL_DEPENDENCIES]
    checked = []
    for name in paths:
        relative = Path(name)
        if relative.is_absolute() or '..' in relative.parts:
            raise ValueError('Unsafe allowlist path')
        source = ROOT / relative
        if any(p.is_symlink() for p in [source, *source.parents]) or not source.is_file():
            raise ValueError('Missing/nonregular/symlink allowlist member: ' + name)
        if source.resolve() == output.resolve():
            raise ValueError('Output overlaps source')
        checked.append((name, source))
    if output.exists():
        raise ValueError('Export output already exists')
    inventory = []
    output.parent.mkdir(parents=True, exist_ok=True)
    try:
        with zipfile.ZipFile(output, 'x', compression=zipfile.ZIP_DEFLATED) as archive:
            for name, source in checked:
                data = source.read_bytes()
                archive.writestr('forever7-offline-project/' + name, data)
                inventory.append({'path': name, 'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest()})
            archive.writestr('forever7-offline-project/EXPORT-INVENTORY.json', json.dumps(inventory, indent=2) + '\n')
    except BaseException:
        output.unlink(missing_ok=True)
        raise
    print(json.dumps({'output': str(output), 'files': len(inventory), 'sha256': hashlib.sha256(output.read_bytes()).hexdigest()}))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    export(parser.parse_args().output)
