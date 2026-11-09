"""Rebuild a plain-index NXPK from preserved official .check/.data files.

The entry layout follows patch_file.npk_index in the inspected client. Each
source .data/.check must match the MD5 and size in the official version file.
This preserves packed bytes; it does not execute/decompile or patch game logic.
"""
import _bootstrap  # noqa: E402,F401
import argparse
import hashlib
import json
from pathlib import Path
import struct
import zlib

from preserve_cdn import parse_manifest


def verify(path, entry):
    if path.stat().st_size != entry["size"]:
        raise ValueError(f"Size mismatch: {path}")
    with path.open("rb") as handle:
        digest = hashlib.file_digest(handle, "md5").hexdigest()
    if digest != entry["md5"]:
        raise ValueError(f"Published MD5 mismatch: {path}")


def rebuild(root, platform, index, part, manifest, output, base_archive=None):
    if part == "raw":
        raise ValueError("Raw files are not an NXPK archive")
    entries = parse_manifest(platform, index, manifest.read_text())
    known = {entry["path"]: entry for entry in entries if entry["part"] == part}
    prefix = f"patch2.{platform}.{index}"
    check_relative = f"{prefix}/{part}.check"
    check = root / check_relative
    verify(check, known[check_relative])
    rows = []
    for line in zlib.decompress(check.read_bytes()).decode("ascii").splitlines():
        if not line.strip():
            continue
        fid, file_hash, csize, chash, usize, uhash, version, offset = line.split()
        row = tuple(map(int, (fid, csize, chash, usize, uhash, version, offset)))
        if min(row) < 0 or len(file_hash) != 32:
            raise ValueError("Invalid check record")
        rows.append(row)
    ids = [row[0] for row in rows]
    if len(ids) != len(set(ids)):
        raise ValueError("Duplicate file IDs")
    by_version = {}
    for row in rows:
        by_version.setdefault(row[-2], []).append(row)
    output.parent.mkdir(parents=True, exist_ok=True)
    temporary = output.with_suffix(output.suffix + ".part")
    records = []
    preserved = []
    try:
        with temporary.open("w+b") as out:
            out.write(b"\0" * 28)
            for version, version_rows in sorted(by_version.items()):
                relative = f"{prefix}/{version}/{part}.data"
                source = root / relative
                verify(source, known[relative])
                with source.open("rb") as handle:
                    for fid, csize, chash, usize, uhash, _, offset in version_rows:
                        if offset + csize > source.stat().st_size:
                            raise ValueError("Check record exceeds payload")
                        handle.seek(offset)
                        data = handle.read(csize)
                        if len(data) != csize:
                            raise ValueError("Truncated payload")
                        position = out.tell()
                        out.write(data)
                        out.write(b"\0" * (-out.tell() % 4))
                        flags = 0 if csize == usize and chash == uhash else 2
                        records.append((fid, position, csize, usize, chash, uhash, flags))
            if base_archive is not None:
                if part != "script":
                    raise ValueError("Base extras are currently supported only for script archives")
                from extract_scripts import ScriptArchive
                baseline = ScriptArchive(base_archive)
                current_ids = {record[0] for record in records}
                # Official script.check omits redirect.nxs. The native importer
                # still needs the APK's bootstrap when this file is overlaid.
                for record in baseline.entries:
                    fid, old_offset, csize, usize, chash, uhash, flags = record
                    if fid in current_ids:
                        continue
                    position = out.tell()
                    out.write(baseline.data[old_offset:old_offset + csize])
                    out.write(b"\0" * (-out.tell() % 4))
                    records.append((fid, position, csize, usize, chash, uhash, flags))
                    preserved.append(f"{fid:08x}")
            table_offset = out.tell()
            for record in sorted(records):
                out.write(struct.pack("<7I", *record))
            out.seek(0)
            out.write(struct.pack("<4s5I", b"NXPK", len(records), 0, 0, 2, table_offset))
            out.write(baseline.data[24:28] if base_archive is not None else b"\0" * 4)
        temporary.replace(output)
    except BaseException:
        temporary.unlink(missing_ok=True)
        raise
    with output.open("rb") as handle:
        sha256 = hashlib.file_digest(handle, "sha256").hexdigest()
    result = {"platform": platform, "index": index, "part": part,
              "files": len(records), "payloads_verified": len(by_version),
              "size": output.stat().st_size, "sha256": sha256,
              "preserved_base_entries": preserved,
              "runtime_tested": False}
    output.with_suffix(".provenance.json").write_text(json.dumps(result, indent=2))
    print(json.dumps(result))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--platform", choices=["android", "ios"], required=True)
    parser.add_argument("--index", type=int, default=640)
    parser.add_argument("--part", default="script")
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--base-archive", type=Path, help="Preserve APK bootstrap entries absent from script.check")
    args = parser.parse_args()
    rebuild(args.root, args.platform, args.index, args.part, args.manifest, args.output, args.base_archive)


if __name__ == "__main__":
    main()
