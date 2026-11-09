"""Apply the pinned BsonLite refresh no-op optimization to manager DEX.

The patch is a single-class method optimization. The generator is maintainer-only;
end-user builds consume the pinned xor-zlib delta and the small BsonLite DEX.
No runtime state/cache is involved.
"""
from __future__ import annotations
import _bootstrap  # noqa: E402,F401
import argparse, hashlib, json, subprocess, tempfile
from pathlib import Path
from project7_component import restore, sha
from project7_dex_filter import definitions, filter_class_definitions

from _bootstrap import ROOT
PATCH_DIR = ROOT / 'project7_bridge/runtime/project7_bson_fast_patch'
BSON_DEX = ROOT / 'project7_bridge/runtime/project7_bson_fast/BsonLite-fast.dex'
CONTRACT = PATCH_DIR / 'contract.json'
PATCH = PATCH_DIR / 'seams.xor-zlib'
BSON_CLASS = 'Lcom/project7/localmanager/BsonLite;'


def _contract():
    info = json.loads(CONTRACT.read_text())
    if info.get('format') != 'project7-bson-refresh-noop-v1':
        raise ValueError('Bson refresh no-op contract format mismatch')
    return info


def _verify_smali(info):
    pin = info.get('smali')
    if not isinstance(pin, dict):
        raise ValueError('Bson refresh no-op source smali pin missing')
    from forever7_paths import resolve_recorded_path
    path = resolve_recorded_path(pin['path'])
    if not path.is_file():
        raise ValueError('Bson refresh no-op source smali missing')
    data = path.read_bytes()
    if len(data) != pin['bytes'] or sha(data) != pin['sha256']:
        raise ValueError('Bson refresh no-op source smali pin mismatch')


def apply_bson_fast(manager: bytes):
    info = _contract()
    _verify_smali(info)
    if sha(manager) != info['source']['sha256'] or len(manager) != info['source']['bytes']:
        raise ValueError('Bson fast patch source manager mismatch')
    if sha(PATCH.read_bytes()) != info['patch']['sha256'] or len(PATCH.read_bytes()) != info['patch']['bytes']:
        raise ValueError('Bson fast patch delta pin mismatch')
    target = restore(manager, PATCH.read_bytes(), info['target']['bytes'])
    if sha(target) != info['target']['sha256']:
        raise ValueError('Bson fast patch target mismatch')
    found = definitions(target)
    if len(found) != info['class_count']:
        raise ValueError('Bson fast target class count changed')
    for name in info['guard']['classes']:
        if name not in found:
            raise ValueError('Bson fast guard class missing: ' + name)
    if BSON_CLASS not in found:
        raise ValueError('Bson fast class missing')
    return target, info


def generate(source: Path, bson_dex: Path, output: Path, d8: Path, android_jar: Path):
    info = _contract()
    manager = source.read_bytes()
    if sha(manager) != info['source']['sha256']:
        raise ValueError('Generator source manager mismatch')
    if sha(bson_dex.read_bytes()) != info['bson_dex']['sha256']:
        raise ValueError('Generator BsonLite DEX mismatch')
    if output.exists():
        raise ValueError('Output exists')
    with tempfile.TemporaryDirectory(prefix='p7-bson-gen-') as tmp:
        tmp = Path(tmp)
        filtered = filter_class_definitions(manager, {BSON_CLASS}, expected_sha256=sha(manager))
        (tmp / 'manager-without-bson.dex').write_bytes(filtered)
        (tmp / 'bson.dex').write_bytes(bson_dex.read_bytes())
        merged = tmp / 'merged'
        merged.mkdir()
        subprocess.run([str(d8), '--min-api', '26', '--output', str(merged), '--lib', str(android_jar),
                        str(tmp / 'manager-without-bson.dex'), str(tmp / 'bson.dex')], check=True)
        target = (merged / 'classes.dex').read_bytes()
    if sha(target) != info['target']['sha256']:
        raise ValueError('Generator D8 target differs from pinned contract')
    output.write_bytes(target)
    return {'bytes': len(target), 'sha256': sha(target)}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('command', nargs='?', choices=['generate'], default='generate')
    p.add_argument('--source', type=Path, required=True)
    p.add_argument('--bson-dex', type=Path, default=BSON_DEX)
    p.add_argument('--d8', type=Path, required=True)
    p.add_argument('--android-jar', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    print(json.dumps(generate(a.source, a.bson_dex, a.output, a.d8, a.android_jar), sort_keys=True))


if __name__ == '__main__':
    main()
