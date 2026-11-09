"""Apply the pinned manager RPC projection gate after the BSON no-op delta.

Fixed xor-zlib delta only; the generator and host evidence live in the isolated
manager-rpc-projection-fix-v1 candidate. No D8/APK/device action at build time.
"""
from __future__ import annotations
import _bootstrap  # noqa: E402,F401

import argparse
import json
from pathlib import Path

from project7_component import restore, sha
from project7_dex_filter import definitions, validate_header

from _bootstrap import ROOT
PATCH_DIR = ROOT / 'project7_bridge/runtime/project7_manager_rpc_projection_patch'
CONTRACT = PATCH_DIR / 'contract.json'
PATCH = PATCH_DIR / 'seams.xor-zlib'
FORMAT = 'project7-manager-rpc-projection-v1'


def _contract():
    info = json.loads(CONTRACT.read_text())
    if info.get('format') != FORMAT:
        raise ValueError('Manager RPC projection contract format mismatch')
    return info


def _verify_source(info):
    pin = info.get('source_class')
    if not isinstance(pin, dict):
        raise ValueError('Manager RPC projection source smali pin missing')
    from forever7_paths import resolve_recorded_path
    path = resolve_recorded_path(pin['path'])
    if not path.is_file():
        raise ValueError('Manager RPC projection source smali missing')
    data = path.read_bytes()
    if len(data) != pin['bytes'] or sha(data) != pin['sha256']:
        raise ValueError('Manager RPC projection source smali pin mismatch')


def apply_manager_rpc_projection(manager: bytes):
    info = _contract()
    _verify_source(info)
    source = info['source']
    patch_info = info['patch']
    target_info = info['target']
    if len(manager) != source['bytes'] or sha(manager) != source['sha256']:
        raise ValueError('Manager RPC projection source manager mismatch')
    patch = PATCH.read_bytes()
    if len(patch) != patch_info['bytes'] or sha(patch) != patch_info['sha256']:
        raise ValueError('Manager RPC projection delta pin mismatch')
    target = restore(manager, patch, target_info['bytes'])
    if sha(target) != target_info['sha256']:
        raise ValueError('Manager RPC projection target mismatch')
    validate_header(target)
    found = definitions(target)
    if len(found) != info['class_count']:
        raise ValueError('Manager RPC projection class count changed')
    for name in info['guard_classes']:
        if name not in found:
            raise ValueError('Manager RPC projection guard class missing: ' + name)
    return target, info


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise ValueError('Output exists')
    target, info = apply_manager_rpc_projection(args.source.read_bytes())
    args.output.write_bytes(target)
    print(json.dumps({'bytes': len(target), 'sha256': sha(target),
                      'source': info['source'], 'target': info['target']}, sort_keys=True))


if __name__ == '__main__':
    main()
