"""Install a development bootstrap hook in init.start inside script.npk.

The hook reads offline_bootstrap.py from the game's document directory. Its
source is compiled by the client's own Python 2.7 interpreter. All other module
payloads remain byte-identical. This tool does not sign APK/IPA packages.
"""
import _bootstrap  # noqa: E402,F401
import argparse
import copy
import ctypes
import io
import json
from pathlib import Path
import struct
import zlib

from xdis.unmarshal import load_code

from extract_scripts import ScriptArchive
from marshal27 import dumps

LOADER = """import os, game3d
_f7_entry_path = os.path.join(game3d.get_doc_dir(), 'offline_bootstrap.py')
if os.path.isfile(_f7_entry_path):
    exec compile(open(_f7_entry_path, 'rb').read(), _f7_entry_path, 'exec') in globals(), globals()
else:
    _f7_original_start()
"""


def instruction(opcode, argument):
    return bytes([opcode]) + struct.pack("<H", argument)


def embedded_loader(runtime_directory):
    bootstrap = (runtime_directory / 'offline_bootstrap.py').read_text(encoding='ascii')
    gateway = ((runtime_directory / 'offline_store.py').read_text(encoding='ascii') + '\n'
               + (runtime_directory / 'offline_wardrobe_completion.py').read_text(encoding='ascii') + '\n'
               + (runtime_directory / 'offline_profile.py').read_text(encoding='ascii') + '\n'
               + (runtime_directory / 'offline_transport.py').read_text(encoding='ascii') + '\n'
               + (runtime_directory / 'offline_battle_terminal.py').read_text(encoding='ascii') + '\n'
               + (runtime_directory / 'offline_role_mission.py').read_text(encoding='ascii') + '\n'
               + (runtime_directory / 'offline_event_battle.py').read_text(encoding='ascii') + '\n'
               + (runtime_directory / 'offline_battle.py').read_text(encoding='ascii') + '\n'
               + (runtime_directory / 'offline_flashback.py').read_text(encoding='ascii') + '\n'
               + (runtime_directory / 'offline_huisu.py').read_text(encoding='ascii') + '\n'
               + (runtime_directory / 'offline_city_stage_provider.py').read_text(encoding='ascii') + '\n'
               + (runtime_directory / 'offline_special_city_stage.py').read_text(encoding='ascii') + '\n'
               + (runtime_directory / 'offline_chapter_campaign.py').read_text(encoding='ascii') + '\n'
               + (runtime_directory / 'offline_stage.py').read_text(encoding='ascii') + '\n'
               + (runtime_directory / 'offline_intelligence.py').read_text(encoding='ascii') + '\n'
               + (runtime_directory / 'offline_yumi.py').read_text(encoding='ascii') + '\n'
               + (runtime_directory / 'offline_route_agreements.py').read_text(encoding='ascii') + '\n'
               + (runtime_directory / 'offline_week.py').read_text(encoding='ascii') + '\n'
               + (runtime_directory / 'offline_day.py').read_text(encoding='ascii') + '\n'
               + (runtime_directory / 'offline_action_ledger.py').read_text(encoding='ascii') + '\n'
               + (runtime_directory / 'offline_conditions.py').read_text(encoding='ascii') + '\n'
               + (runtime_directory / 'offline_daerweila.py').read_text(encoding='ascii') + '\n'
               + (runtime_directory / 'offline_story.py').read_text(encoding='ascii') + '\n'
               + (runtime_directory / 'offline_event_effects.py').read_text(encoding='ascii') + '\n'
               + (runtime_directory / 'offline_story_engine.py').read_text(encoding='ascii') + '\n'
               + (runtime_directory / 'offline_native_story_callbacks.py').read_text(encoding='ascii') + '\n'
               + (runtime_directory / 'offline_city_actions.py').read_text(encoding='ascii') + '\n'
               + (runtime_directory / 'offline_avatar_snapshot.py').read_text(encoding='ascii') + '\n'
               + (runtime_directory / 'offline_postbattle.py').read_text(encoding='ascii') + '\n'
               + (runtime_directory / 'offline_treasure.py').read_text(encoding='ascii') + '\n'
               + (runtime_directory / 'offline_gacha.py').read_text(encoding='ascii') + '\n'
               + (runtime_directory / 'offline_gacha_pools.py').read_text(encoding='ascii') + '\n'
               + (runtime_directory / 'offline_gacha_special.py').read_text(encoding='ascii') + '\n'
               + (runtime_directory / 'offline_gacha_gateway.py').read_text(encoding='ascii') + '\n'
               + (runtime_directory / 'offline_gacha_rewards.py').read_text(encoding='ascii') + '\n'
               + (runtime_directory / 'offline_gacha_costs.py').read_text(encoding='ascii') + '\n'
               + (runtime_directory / 'offline_gacha_archive.py').read_text(encoding='ascii') + '\n'
               + (runtime_directory / 'offline_gacha_ui.py').read_text(encoding='ascii') + '\n'
               + (runtime_directory / 'offline_tutorials.py').read_text(encoding='ascii') + '\n'
               + (runtime_directory / 'offline_rpc_rejections.py').read_text(encoding='ascii') + '\n'
               + (runtime_directory / 'offline_item_exchange.py').read_text(encoding='ascii') + '\n'
               + (runtime_directory / 'local_gateway.py').read_text(encoding='ascii'))
    # Source literals remain ASCII for the client's restricted codecs module.
    return ("_f7_embedded_gateway_source = %r\n" % gateway
            + "exec compile(%r, 'offline_bootstrap.py', 'exec') in globals(), globals()\n" % bootstrap)


def patch_code(module, loader=LOADER):
    constants = list(module.co_consts)
    matches = [i for i, value in enumerate(constants) if hasattr(value, "co_code") and value.co_name == "start"]
    if len(matches) != 1:
        raise ValueError("Expected one init.start function")
    index = matches[0]
    original = constants[index]
    if original.co_argcount or original.co_freevars or original.co_cellvars:
        raise ValueError("Unexpected start function signature")
    wrapper = copy.copy(original)
    wrapper.co_consts = (loader, None, original)
    wrapper.co_names = ("globals", "_f7_original_start")
    wrapper.co_varnames = ()
    wrapper.co_nlocals = 0
    wrapper.co_stacksize = 3
    wrapper.co_lnotab = b""
    # NeoX opcodes: CONST, MAKE_FUNCTION, STORE_GLOBAL; exec in globals twice.
    wrapper.co_code = (instruction(153, 2) + instruction(136, 0) + instruction(113, 1)
                       + instruction(153, 0) + instruction(155, 0) + instruction(131, 0)
                       + bytes([66, 64]) + instruction(153, 1) + bytes([83]))
    constants[index] = wrapper
    module.co_consts = tuple(constants)
    return module


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("archive", type=Path)
    parser.add_argument("--module-index", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--embed-runtime", type=Path,
                        help="Embed this runtime directory so startup needs no external Python files")
    args = parser.parse_args()
    archive = ScriptArchive(args.archive)
    found = []
    for line in args.module_index.open():
        item = json.loads(line)
        if item["filename"].replace("\\", "/") == "init.py":
            found.append(int(item["sign"], 16))
    if len(found) != 1:
        raise ValueError("Could not identify the exact init.py module")
    sign = found[0]
    match = [i for i, record in enumerate(archive.entries) if record[0] == sign]
    if len(match) != 1:
        raise ValueError("Ambiguous/missing init.py archive entry")
    index = match[0]
    module = load_code(io.BytesIO(archive.read(index)), 62211, code_objects={})
    loader = embedded_loader(args.embed_runtime) if args.embed_runtime else LOADER
    module = patch_code(module, loader)
    cleartext = dumps(module)
    # Inverse of redirect.py's documented decode sequence.
    reversed_code = cleartext[::-1]
    scrambled = bytes(value ^ 154 if i < 128 else value for i, value in enumerate(reversed_code))
    compressed = zlib.compress(scrambled)
    buffer = ctypes.create_string_buffer(compressed, len(compressed))
    if archive.lib.f7_rotor(archive.key, buffer, len(compressed), 1):
        raise MemoryError("Could not allocate rotor state")
    replacement = buffer.raw
    args.output.parent.mkdir(parents=True, exist_ok=True)
    records = []
    with args.output.open("w+b") as out:
        out.write(b"\0" * 28)
        for i, record in enumerate(archive.entries):
            fid, offset, size, original_size, checksum1, checksum2, flags = record
            if i == index:
                payload = replacement
                size = original_size = len(payload)
                # The client checksum algorithm is not yet identified. These
                # metadata values are intentionally not presented as verified.
                # Retain the existing opaque fields while testing the native
                # reader. Their role (checksum/encoding) is still under audit.
                flags = 0
            else:
                payload = archive.data[offset:offset + size]
            position = out.tell()
            out.write(payload)
            out.write(b"\0" * (-out.tell() % 4))
            records.append((fid, position, size, original_size, checksum1, checksum2, flags))
        offset = out.tell()
        for record in sorted(records):
            out.write(struct.pack("<7I", *record))
        out.seek(0)
        out.write(struct.pack("<4s5I", b"NXPK", len(records), 0, 0, 2, offset))
        out.write(archive.data[24:28])
    check = ScriptArchive(args.output)
    target = next(i for i, record in enumerate(check.entries) if record[0] == sign)
    roundtrip = load_code(io.BytesIO(check.read(target)), 62211, code_objects={})
    wrapper = next(value for value in roundtrip.co_consts if hasattr(value, "co_code") and value.co_name == "start")
    if wrapper.co_consts[0] != loader:
        raise ValueError("Patched module did not round-trip")
    print(json.dumps({"output": str(args.output), "patched_module": "init.py", "entry_sign": hex(sign),
                      "other_module_payloads_unchanged": True, "runtime_embedded": bool(args.embed_runtime),
                      "native_runtime_verified": False}))


if __name__ == "__main__":
    main()
