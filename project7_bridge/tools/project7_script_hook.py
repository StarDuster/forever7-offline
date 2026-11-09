"""Pinned P7 init.start overlay extension. Parse/rewrite only; never run game opcodes."""
import _bootstrap  # noqa: E402,F401
from pathlib import Path
import argparse
import copy
import ctypes
import hashlib
import io
import json
import struct
import zlib

from xdis.unmarshal import load_code
from extract_scripts import ScriptArchive
from marshal27 import dumps
from project7_auth_deadline import LOGIN_FID, patch_login
from patch_bootstrap import patch_code
from project7_feature_assets import (history_ui_policy, HISTORY_CATALOG_SHA,
                                     furniture_ui_policy, FURNITURE_CATALOG_SHA,
                                     selector_ui_policy, SELECTOR_CATALOG_SHA,
                                     dynamic_ui_policy, DYNAMIC_CATALOG_SHA, DYNAMIC_PUBLIC_READY_IDS,
                                     wish_ui_policy, WISH_CATALOG_SHA, WISH_PUBLIC_READY_IDS)

from _bootstrap import ROOT
from forever7_paths import EMBEDDED_RUNTIME_ORDER, EMBEDDED_RUNTIME_SOURCES, runtime_source
from py2_syntax_gate import check_sources
BASE_SHA256 = '9284e0e00e18a04cb6169e5bbffbec3fd23037fa7dd19893fea3a3510ea1bb06'
P7_SHA256 = '3e0d06ef611167c2e9917d87272eb143c3fb6d8118957be286e3809b19def061'
INIT_FID = 0xacb9b80e
EMBEDDED_SOURCES = EMBEDDED_RUNTIME_ORDER
TRIAL_UI_POLICY_SHA = 'f972b71641a864afd90606d697bcc09fcc031c6b28064159d147025acb8ed08a'
PYTHON_SOURCES = tuple(name for name in EMBEDDED_SOURCES if name.endswith('.py'))


def _embedded_path(root, name):
    return Path(root) / EMBEDDED_RUNTIME_SOURCES[name]


def _embedded_sources(root):
    """Read every embedded source once and reject what the 2.7 loader cannot take.

    The overlay compiles these with the game's own `compile()` after an
    `.decode('ascii')`.  Both failures are silent on device: a Python 3-only
    call such as `f(a, *b, c)` and a single non-ASCII byte in a comment each
    abort the overlay at load and leave a dead panel, while every host test
    still passes.  Fail the build instead.
    """
    raw = {name: _embedded_path(root, name).read_bytes()
           for name in EMBEDDED_SOURCES}
    check_sources({name: raw[name] for name in PYTHON_SOURCES})
    return {name: value.decode('ascii') for name, value in raw.items()}


def embedded_loader(root=ROOT, _sources=None, _draw_policy=None, _furniture_policy=None, _selector_policy=None, _dynamic_policy=None, _wish_policy=None, _render_mode='astc'):
    root = Path(root)
    sources = _sources if _sources is not None else _embedded_sources(root)
    hook, tutorials, collection, collection_policy, capacity, capacity_policy, draw_ui, furniture_ui, friend_ui, selector_ui, completion, dynamic_ui, trial_ui, trial_policy, wish_ui, wish_transport, inventory_ui = (sources[name] for name in EMBEDDED_SOURCES)
    if hashlib.sha256(trial_policy.encode('ascii')).hexdigest() != TRIAL_UI_POLICY_SHA:
        raise ValueError('Trial retry UI policy binding differs')
    draw_policy = _draw_policy if _draw_policy is not None else history_ui_policy(root)
    furniture_policy = _furniture_policy if _furniture_policy is not None else furniture_ui_policy(root)
    selector_policy = _selector_policy if _selector_policy is not None else selector_ui_policy(root)
    dynamic_policy = _dynamic_policy if _dynamic_policy is not None else dynamic_ui_policy(root)
    wish_policy = _wish_policy if _wish_policy is not None else wish_ui_policy(root)
    # The only imported game path is identical to original init.start. Resolve
    # runtime alias from this import, never invent patch_file/pconst imports.
    return ("import sys as _p7_sys\n"
            "if globals().get('_p7_start_invoked', False):\n"
            "    raise RuntimeError('P7 init.start already invoked')\n"
            "_p7_start_invoked = True\n"
            "import patch.patch\n"
            "_p7_candidates = []\n"
            "for _p7_obj in (patch, _p7_sys.modules.get('patch'), _p7_sys.modules.get('patch.patch')):\n"
            "    if callable(getattr(_p7_obj, '_q7_activate_game_mode', None)) and not any(_p7_obj is item for item in _p7_candidates):\n"
            "        _p7_candidates.append(_p7_obj)\n"
            "if len(_p7_candidates) != 1:\n"
            "    raise RuntimeError('Ambiguous P7 patch runtime module')\n"
            "_p7_namespace = {}\n"
            "exec compile(%r, 'project7_startup_hook.py', 'exec') in _p7_namespace, _p7_namespace\n" % hook
            + ("_p7_policy = _p7_namespace['install'](_p7_candidates[0], %r, "
               "collection_source=%r, collection_policy=%r, capacity_source=%r, capacity_policy=%r, draw_ui_source=%r, draw_ui_policy=%r, furniture_ui_source=%r, furniture_ui_policy=%r, friend_ui_source=%r, selector_ui_source=%r, selector_ui_policy=%r, tutorial_completion_source=%r, dynamic_ui_source=%r, dynamic_ui_policy=%r, trial_retry_source=%r, trial_retry_policy=%r, wish_ui_source=%r, wish_transport_source=%r, wish_ui_policy=%r, render_mode=%r)\n") % (tutorials, collection, collection_policy, capacity, capacity_policy, draw_ui, draw_policy, furniture_ui, furniture_policy, friend_ui, selector_ui, selector_policy, completion, dynamic_ui, dynamic_policy, trial_ui, trial_policy, wish_ui, wish_transport, wish_policy, _render_mode)
            + "_p7_editor_namespace = {}\n"
            + "exec compile(%r, 'project7_inventory_editor_ui.py', 'exec') in _p7_editor_namespace, _p7_editor_namespace\n" % inventory_ui
            + "_p7_editor_bind = _p7_editor_namespace['bind_startup'](_p7_candidates[0], _p7_policy)\n"
            + "_f7_original_start()\n")


def _sha(data):
    return hashlib.sha256(data).hexdigest()


def build_startup_overlay(base_script, p7_overlay, output, root=ROOT, render_mode='astc'):
    base, overlay = ScriptArchive(base_script), ScriptArchive(p7_overlay)
    if _sha(base.data) != BASE_SHA256 or _sha(overlay.data) != P7_SHA256:
        raise ValueError('Pinned official640/P7 archive changed')
    if len(overlay.entries) != 20 or len({r[0] for r in overlay.entries}) != 20:
        raise ValueError('Expected exact unique 20-entry P7 overlay')
    if any(r[0] == INIT_FID for r in overlay.entries):
        raise ValueError('P7 unexpectedly already overrides init')
    matches = [i for i, r in enumerate(base.entries) if r[0] == INIT_FID]
    if len(matches) != 1:
        raise ValueError('Official640 init FID ambiguous/missing')
    original_record = base.entries[matches[0]]
    clear = base.read(matches[0])
    original = load_code(io.BytesIO(clear), 62211, code_objects={})
    if original.co_filename.replace('\\', '/') != 'init.py':
        raise ValueError('Pinned init FID filename mismatch')
    root = Path(root)
    sources = _embedded_sources(root)
    draw_policy = history_ui_policy(root)
    furniture_policy = furniture_ui_policy(root)
    selector_policy = selector_ui_policy(root)
    dynamic_policy = dynamic_ui_policy(root)
    wish_policy = wish_ui_policy(root)
    loader = embedded_loader(root, sources, draw_policy, furniture_policy, selector_policy, dynamic_policy, wish_policy, render_mode)
    patched = patch_code(copy.deepcopy(original), loader)
    serialized = dumps(patched)
    # Roundtrip the Python2 marshal before rotor encoding too.
    parsed = load_code(io.BytesIO(serialized), 62211, code_objects={})
    start = next(c for c in parsed.co_consts if hasattr(c, 'co_code') and c.co_name == 'start')
    original_start = next(c for c in original.co_consts if hasattr(c, 'co_code') and c.co_name == 'start')
    if len(parsed.co_consts) != len(original.co_consts):
        raise ValueError('Unexpected init module constant change')
    for before, after in zip(original.co_consts, parsed.co_consts):
        if hasattr(before, 'co_code') and before.co_name == 'start':
            continue
        if dumps(before) != dumps(after):
            raise ValueError('Unrelated init module body changed')
    if start.co_consts[0] != loader or dumps(start.co_consts[2]) != dumps(original_start):
        raise ValueError('Original init.start not preserved')
    reverse = serialized[::-1]
    scrambled = bytes(v ^ 154 if i < 128 else v for i, v in enumerate(reverse))
    compressed = zlib.compress(scrambled)
    buffer = ctypes.create_string_buffer(compressed, len(compressed))
    if base.lib.f7_rotor(base.key, buffer, len(compressed), 1):
        raise MemoryError('Rotor encoder allocation failed')
    replacement = buffer.raw
    output = Path(output)
    if output.resolve() in (Path(base_script).resolve(), Path(p7_overlay).resolve()):
        raise ValueError('Output must not overwrite either pinned input')
    output.parent.mkdir(parents=True, exist_ok=True)
    login_records = [r for r in overlay.entries if r[0] == LOGIN_FID]
    if len(login_records) != 1:
        raise ValueError('Expected exactly one P7 login module')
    login_payload, login_clear, auth_report = patch_login(overlay, login_records[0])
    records = []
    with output.open('w+b') as stream:
        stream.write(b'\0' * 28)
        for record in overlay.entries:
            fid, offset, size, original_size, check1, check2, flags = record
            position = stream.tell()
            if fid == LOGIN_FID:
                stream.write(login_payload)
                size = original_size = len(login_payload)
                flags = 0
            else:
                stream.write(overlay.data[offset:offset+size])
            stream.write(b'\0' * (-stream.tell() % 4))
            records.append((fid, position, size, original_size, check1, check2, flags))
        position = stream.tell()
        stream.write(replacement)
        stream.write(b'\0' * (-stream.tell() % 4))
        # Same opaque checksum convention as existing patch_bootstrap. Do not
        # claim these fields are native-reader verified for modified payloads.
        records.append((INIT_FID, position, len(replacement), len(replacement),
                        original_record[4], original_record[5], 0))
        index = stream.tell()
        for record in sorted(records):
            stream.write(struct.pack('<7I', *record))
        stream.seek(0)
        stream.write(struct.pack('<4s5I', b'NXPK', 21, 0, 0, 2, index))
        stream.write(overlay.data[24:28])
    check = ScriptArchive(output)
    entry = next(i for i,r in enumerate(check.entries) if r[0] == INIT_FID)
    decoded = check.read(entry)
    if decoded != serialized:
        raise ValueError('Rotor/NXPK roundtrip failed')
    final = load_code(io.BytesIO(decoded), 62211, code_objects={})
    if dumps(final) != serialized:
        raise ValueError('Final xdis/marshal27 roundtrip failed')
    unchanged = []
    for record in overlay.entries:
        other = next(r for r in check.entries if r[0] == record[0])
        if record[0] == LOGIN_FID:
            login_index = next(i for i,r in enumerate(check.entries) if r[0] == LOGIN_FID)
            decoded_login = check.read(login_index)
            if decoded_login != login_clear or dumps(load_code(io.BytesIO(decoded_login), 62211, code_objects={})) != login_clear:
                raise ValueError('Login decoded marshal/rotor roundtrip failed')
            auth_report['decoded_roundtrip_verified'] = True
            continue
        before = overlay.data[record[1]:record[1]+record[2]]
        after = check.data[other[1]:other[1]+other[2]]
        if before != after or other[2:] != record[2:]:
            raise ValueError('P7 original entry changed')
        unchanged.append({'fid': '%08x' % record[0], 'payload_sha256': _sha(before)})
    if any(_embedded_path(root, name).read_bytes() != text.encode('ascii') for name, text in sources.items()):
        raise ValueError('Embedded startup source changed during preparation')
    return {'format': 'project7-python-startup-overlay-v1', 'output': str(output),
            'render_mode': render_mode, 'render_loader_option': True,
            'frida_required': False,
            'base_sha256': _sha(base.data), 'p7_input_sha256': _sha(overlay.data),
            'output_sha256': _sha(check.data), 'entries': 21, 'init_fid': '%08x' % INIT_FID,
            'loader_sha256': _sha(loader.encode('ascii')),
            'hook_source_sha256': _sha(sources['project7_startup_hook.py'].encode('ascii')),
            'tutorial_source_sha256': _sha(sources['offline_tutorials.py'].encode('ascii')),
            'tutorial_completion_embedded': True,
            'tutorial_completion_source_sha256': _sha(sources['project7_tutorial_completion.py'].encode('ascii')),
            'trial_retry_compat_embedded': True,
            'trial_retry_compat_source_sha256': _sha(sources['project7_trial_retry_compat.py'].encode('ascii')),
            'trial_retry_ui_policy_sha256': _sha(sources['android_trial_retry/trial-ui-policy-v1.json'].encode('ascii')),
            'collection_source_sha256': _sha(sources['project7_collection_visibility.py'].encode('ascii')),
            'collection_policy_sha256': _sha(sources['project7_collection_visibility/policy.json'].encode('ascii')),
            'collection_visibility_embedded': True,
            'capacity_source_sha256': _sha(sources['project7_shadow_capacity.py'].encode('ascii')),
            'capacity_policy_sha256': _sha(sources['project7_shadow_capacity/policy.json'].encode('ascii')),
            'shadow_capacity_embedded': True,
            'shadow_capacity_target_manifest_sha256': '7e3849b6ed316b7cdc2ef9f103b90e0bc8e20f9b5da70ab3b585fbd72c0da62d',
            'draw_ui_source_sha256': _sha(sources['project7_draw_ui.py'].encode('ascii')),
            'draw_ui_embedded': True,
            'history_ui_policy_embedded': True,
            'history_ui_catalog_sha256': HISTORY_CATALOG_SHA,
            'history_ui_policy_sha256': _sha(draw_policy.encode('ascii')),
            'friend_ui_embedded': True,
            'friend_ui_source_sha256': _sha(sources['project7_friend_ui.py'].encode('ascii')),
            'selector_ui_embedded': True,
            'selector_ui_source_sha256': _sha(sources['project7_selector_ui.py'].encode('ascii')),
            'selector_ui_catalog_sha256': SELECTOR_CATALOG_SHA,
            'selector_ui_policy_sha256': _sha(selector_policy.encode('ascii')),
            'dynamic_ui_embedded': True,
            'dynamic_ui_source_sha256': _sha(sources['project7_dynamic_ui_families.py'].encode('ascii')),
            'dynamic_ui_owner': 'project7_dynamic_ui_families.py',
            'dynamic_ui_policy_sha256': _sha(dynamic_policy.encode('ascii')),
            'dynamic_ui_catalog_sha256': DYNAMIC_CATALOG_SHA,
            'dynamic_ui_base_sha256': HISTORY_CATALOG_SHA,
            'dynamic_ui_public_ready_ids': list(DYNAMIC_PUBLIC_READY_IDS),
            'wish_ui_embedded': True,
            'wish_transport_embedded': True,
            'wish_ui_source_sha256': _sha(sources['project7_wish_ui.py'].encode('ascii')),
            'wish_transport_source_sha256': _sha(sources['project7_wish_transport.py'].encode('ascii')),
            'wish_ui_policy_sha256': _sha(wish_policy.encode('ascii')),
            'wish_ui_catalog_sha256': WISH_CATALOG_SHA,
            'wish_ui_public_ready_ids': list(WISH_PUBLIC_READY_IDS),
            'inventory_ui_embedded': True,
            'inventory_ui_source_sha256': _sha(sources['project7_inventory_editor_ui.py'].encode('ascii')),
            'furniture_ui_embedded': True,
            'furniture_ui_source_sha256': _sha(sources['project7_furniture_ui.py'].encode('ascii')),
            'furniture_ui_catalog_sha256': FURNITURE_CATALOG_SHA,
            'furniture_ui_policy_sha256': _sha(furniture_policy.encode('ascii')),
            'original_init_start_preserved': True, 'other_init_constants_unchanged': True,
            'original_p7_entries_unchanged': unchanged,
            'auth_deadline': auth_report,
            'xdis_marshal27_rotor_roundtrip': True, 'game_opcodes_executed': False,
            'native_reader_verified': False, 'opaque_modified_entry_checksums_verified': False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--base-script', required=True, type=Path)
    parser.add_argument('--p7-overlay', required=True, type=Path)
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--report', type=Path)
    args = parser.parse_args()
    report = build_startup_overlay(args.base_script, args.p7_overlay, args.output)
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report))


if __name__ == '__main__':
    main()
