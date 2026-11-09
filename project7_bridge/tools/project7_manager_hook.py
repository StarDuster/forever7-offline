"""Apply a fixed single-method manager RPC prefix; no end-user DEX recompiler.

The Java producer is maintainer-only. End-user builds consume a pinned small
component delta and still require the real CoreGapBridge implementation in
their own classes6.dex; this module does not claim the helper is installed.
"""
import _bootstrap  # noqa: E402,F401
import hashlib
import json
from pathlib import Path

from project7_component import restore
from project7_dex_filter import u32, validate_header

from _bootstrap import ROOT
DATA = ROOT / 'project7_bridge/runtime/project7_manager_rpc'
SOURCE_SHA = '087656832b8150984c81c997c7c1f3966da22902c5226b0f6ef2f3e71d602325'
TARGET_SHA = 'dfb15ecd8e12ff99c3f3595ecc680b014a0233943eacd3aca3c81555709f8e10'
PATCH_SHA = '579576b5afa5609d63a1eb86de9181141b4649b82e54ee4afdc478686528dcc6'
CONTRACT_SHA = '69ebf52fdda55a7e995fde93d4714bb61992c00ba583e8b045b5db055e47720b'
TARGET_SIZE = 1155376


def sha(data):
    return hashlib.sha256(data).hexdigest()


def apply_manager_hook(manager, patch=None, contract=None):
    if sha(manager) != SOURCE_SHA:
        raise ValueError('Unsupported original manager DEX')
    if patch is None:
        patch = (DATA / 'dispatch.xor-zlib').read_bytes()
    if contract is None:
        contract = (DATA / 'contract.json').read_bytes()
    if sha(patch) != PATCH_SHA or sha(contract) != CONTRACT_SHA:
        raise ValueError('Manager RPC patch/contract pin mismatch')
    info = json.loads(contract)
    if (info['format'] != 'project7-manager-rpc-prefix-v1' or
            info['source'] != {'bytes': len(manager), 'sha256': SOURCE_SHA} or
            info['target'] != {'bytes': TARGET_SIZE, 'sha256': TARGET_SHA}):
        raise ValueError('Manager RPC source/target contract mismatch')
    target = restore(manager, patch, TARGET_SIZE)
    if sha(target) != TARGET_SHA or target[:8] != b'dex\n038\0':
        raise ValueError('Manager RPC reconstructed DEX mismatch')
    validate_header(target)
    if u32(target, 96) != 649:
        raise ValueError('Manager class definition count changed')
    return target, info
