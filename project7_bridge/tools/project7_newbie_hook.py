"""Pinned pool-354 admission patch; existing groups retain original engine paths."""
import _bootstrap  # noqa: E402,F401
import hashlib
import json
from pathlib import Path

from project7_component import restore
from project7_dex_filter import u32, validate_header

from _bootstrap import ROOT
DATA = ROOT / 'project7_bridge/runtime/project7_newbie_patch'
SOURCE_SHA = '20f19471d1e73f3b32b4cc28300973eb3168cdfea8ddb1c46fe1ccd1e1306eae'
TARGET_SHA = 'd16990dff71677c55ecd54225cd1fdc82f06c3785c3258e5053e069f24df341f'
PATCH_SHA = '0f958f1d20821da1a98a3b3193632290b8049a35f4799098caaa34fb96da1c80'
CONTRACT_SHA = '2aa6b8fd26748a8c39e2cc1f363d4e0516941fc4a59e7bd82c0871e0d6b82a9f'
TARGET_SIZE = 1155644


def sha(data):
    return hashlib.sha256(data).hexdigest()


def apply_newbie_hook(manager, patch=None, contract=None):
    if sha(manager) != SOURCE_SHA:
        raise ValueError('Unsupported ordinary-policy DEX baseline for beginner block')
    patch = (DATA / 'new-group-block.xor-zlib').read_bytes() if patch is None else patch
    contract = (DATA / 'contract.json').read_bytes() if contract is None else contract
    if sha(patch) != PATCH_SHA or sha(contract) != CONTRACT_SHA:
        raise ValueError('Beginner-block patch/contract pin mismatch')
    info = json.loads(contract)
    if (info['format'] != 'project7-newbie354-new-group-block-v1' or
            info['source'] != {'bytes': len(manager), 'sha256': SOURCE_SHA} or
            info['target'] != {'bytes': TARGET_SIZE, 'sha256': TARGET_SHA}):
        raise ValueError('Beginner-block source/target contract mismatch')
    target = restore(manager, patch, TARGET_SIZE)
    if sha(target) != TARGET_SHA or target[:8] != b'dex\n038\0':
        raise ValueError('Beginner-block reconstructed DEX mismatch')
    validate_header(target)
    if u32(target, 96) != 649:
        raise ValueError('Beginner-block changed manager class definitions')
    return target, info
