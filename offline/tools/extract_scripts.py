"""Inspect this client's NXPK scripts without executing any game bytecode.

The NXPK index layout is validated against the original archive; script decoding
is recovered from redirect.py inside the same archive. Does not handle encrypted
resource indexes or claim to be a general-purpose NetEase unpacker.
"""
from __future__ import annotations
import _bootstrap  # noqa: E402,F401

import argparse
import ctypes
import hashlib
import io
import json
from pathlib import Path, PurePosixPath
import struct
import subprocess
import sys
import zlib

import lz4.block
from xdis.unmarshal import load_code

from _bootstrap import ROOT
HEADER = struct.Struct("<4s5I")
ENTRY = struct.Struct("<7I")


def rotor_library():
    suffix = ".dylib" if sys.platform == "darwin" else ".so"
    source = ROOT / "offline/tools/rotor_compat.c"
    target = source.with_suffix(suffix)
    if not target.exists() or target.stat().st_mtime < source.stat().st_mtime:
        subprocess.run(["cc", "-O2", "-shared", "-fPIC", str(source), "-lm", "-o", str(target)], check=True)
    lib = ctypes.CDLL(str(target))
    lib.f7_rotor.argtypes = [ctypes.c_char_p, ctypes.c_void_p, ctypes.c_int, ctypes.c_int]
    lib.f7_rotor.restype = ctypes.c_int
    return lib


class ScriptArchive:
    def __init__(self, path):
        self.path = Path(path)
        self.data = self.path.read_bytes()
        magic, count, a, b, version, index = HEADER.unpack_from(self.data)
        if magic != b"NXPK" or (a, b, version) != (0, 0, 2):
            raise ValueError("Unsupported NXPK header")
        if index < HEADER.size or index + count * ENTRY.size != len(self.data):
            raise ValueError("Unsupported index size or trailing data")
        self.entries = [ENTRY.unpack_from(self.data, index + i * ENTRY.size) for i in range(count)]
        for _, offset, size, original_size, _, _, flags in self.entries:
            if offset < HEADER.size or offset + size > index or flags not in (0, 1, 2):
                raise ValueError("Encrypted/unsupported NXPK index or entry")
            if original_size > 128 * 1024 * 1024:
                raise ValueError("Entry exceeds the extraction limit")
        self.lib = rotor_library()
        dn, dt, df = "j2h56ogodh3se", "=dziaq.", '|os=5v7!"-234'
        self.key = (dn * 4 + (dt + dn + df) * 5 + "!#" + dt * 7 + df * 2 + "*&'").encode()

    def read(self, index):
        sign, offset, size, original_size, packed_checksum, checksum, flags = self.entries[index]
        data = self.data[offset:offset + size]
        # These two index checksums are NOT standard zlib CRC32 in this client.
        # Preserve them in the index; archive integrity is checked at APK ZIP level.
        if flags == 1:
            data = zlib.decompress(data)
        elif flags == 2:
            data = lz4.block.decompress(data, uncompressed_size=original_size)
        if len(data) != original_size:
            raise ValueError(f"Decoded size mismatch at entry {index}")
        if data[:1] != b"c":
            buf = ctypes.create_string_buffer(data, len(data))
            if self.lib.f7_rotor(self.key, buf, len(data), 0):
                raise MemoryError("Could not allocate rotor state")
            decompressor = zlib.decompressobj()
            data = decompressor.decompress(buf.raw, 128 * 1024 * 1024 + 1)
            if len(data) > 128 * 1024 * 1024 or not decompressor.eof:
                raise ValueError("Invalid/oversized decrypted script")
            data = bytes(x ^ 154 if i < 128 else x for i, x in enumerate(data))[::-1]
        if not data.startswith(b"c"):
            raise ValueError(f"Expected Python 2 code object at entry {index}")
        return data


def safe_module_path(filename, index):
    path = PurePosixPath(filename.replace("\\", "/"))
    if path.is_absolute() or ".." in path.parts or ":" in str(path):
        return Path("_unmapped") / f"{index:05d}.marshal"
    return Path(*path.parts).with_suffix(".marshal")


def describe(code):
    """Index names/constants only. xdis parses code; it never imports the module."""
    result = {"name": code.co_name, "line": code.co_firstlineno,
              "names": list(code.co_names), "vars": list(code.co_varnames),
              "strings": [], "children": []}
    for value in code.co_consts:
        if hasattr(value, "co_code"):
            result["children"].append(describe(value))
        elif isinstance(value, str):
            result["strings"].append(value)
        elif isinstance(value, bytes):
            result["strings"].append(value.decode("utf-8", errors="replace"))
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("archive", type=Path)
    parser.add_argument("--output", type=Path, default=ROOT / "analysis/scripts")
    parser.add_argument("--index", type=Path, default=ROOT / "reports/modules.jsonl")
    args = parser.parse_args()
    archive = ScriptArchive(args.archive)
    args.output.mkdir(parents=True, exist_ok=True)
    args.index.parent.mkdir(parents=True, exist_ok=True)
    failures = []
    seen = set()
    with args.index.open("w") as out:
        for index, entry in enumerate(archive.entries):
            try:
                data = archive.read(index)
                code = load_code(io.BytesIO(data), 62211, code_objects={})
                relative = safe_module_path(code.co_filename, index)
                if relative in seen:
                    relative = relative.with_name(f"{relative.stem}-{index}.marshal")
                seen.add(relative)
                destination = args.output / relative
                destination.parent.mkdir(parents=True, exist_ok=True)
                destination.write_bytes(data)
                record = {"index": index, "sign": f"{entry[0]:08x}",
                          "packed_checksum": f"{entry[4]:08x}", "checksum": f"{entry[5]:08x}",
                          "filename": code.co_filename, "output": str(relative),
                          "size": len(data), "sha256": hashlib.sha256(data).hexdigest(),
                          "code": describe(code)}
                out.write(json.dumps(record, ensure_ascii=False) + "\n")
            except Exception as exc:
                failures.append({"index": index, "error": f"{type(exc).__name__}: {exc}"})
            if (index + 1) % 2000 == 0:
                print(f"{index + 1}/{len(archive.entries)}; failures={len(failures)}", flush=True)
    summary = {"archive": str(args.archive), "entries": len(archive.entries),
               "extracted": len(archive.entries) - len(failures), "failures": failures}
    args.index.with_suffix(".summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2))
    print(json.dumps({k: v for k, v in summary.items() if k != "failures"}, ensure_ascii=False))
    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
