"""Restore pinned ordinary-draw DEX seams without an end-user recompiler.

This does not install the policy implementation: the build must also compile
CoreDrawPolicy and package its fixed public catalog before publishing an APK.
"""
import _bootstrap  # noqa: E402,F401
import hashlib
import json
from pathlib import Path

from project7_component import restore
from project7_dex_filter import u32, validate_header

from _bootstrap import ROOT
DATA = ROOT / 'project7_bridge/runtime/project7_draw_patch'
SOURCE_SHA = 'dfb15ecd8e12ff99c3f3595ecc680b014a0233943eacd3aca3c81555709f8e10'
TARGET_SHA = '20f19471d1e73f3b32b4cc28300973eb3168cdfea8ddb1c46fe1ccd1e1306eae'
PATCH_SHA = '1e60415a91e3269b1718d240b2a0c01da44abe4b2c86007cc913e6350678c2f7'
CONTRACT_SHA = '03cced1776c26a473008ec5583076fdcaf20abc45d279af72a7c81cdee7e2879'
TARGET_SIZE = 1155616


def sha(data):
    return hashlib.sha256(data).hexdigest()


def apply_draw_hook(manager, patch=None, contract=None):
    if sha(manager) != SOURCE_SHA:
        raise ValueError('Unsupported manager core-RPC baseline for draw policy')
    patch = (DATA / 'ordinary-hooks.xor-zlib').read_bytes() if patch is None else patch
    contract = (DATA / 'contract.json').read_bytes() if contract is None else contract
    if sha(patch) != PATCH_SHA or sha(contract) != CONTRACT_SHA:
        raise ValueError('Draw patch/contract pin mismatch')
    info = json.loads(contract)
    if (info['format'] != 'project7-normal-draw-seams-v1' or
            info['source'] != {'bytes': len(manager), 'sha256': SOURCE_SHA} or
            info['target'] != {'bytes': TARGET_SIZE, 'sha256': TARGET_SHA}):
        raise ValueError('Draw source/target contract mismatch')
    target = restore(manager, patch, TARGET_SIZE)
    if sha(target) != TARGET_SHA or target[:8] != b'dex\n038\0':
        raise ValueError('Draw reconstructed DEX mismatch')
    validate_header(target)
    if u32(target, 96) != 649:
        raise ValueError('Draw patch changed manager class definitions')
    return target, info
