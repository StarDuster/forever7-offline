"""Assemble the game's complete local Documents resource tree from the CDN snapshot."""
import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import zlib

from preserve_cdn import parse_manifest
from rebuild_npk import rebuild, verify

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--platform", choices=["android", "ios"], required=True)
    parser.add_argument("--root", type=Path, default=ROOT / "originals/cdn")
    parser.add_argument("--index", type=int, default=640)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--script-base", type=Path, help="Original APK's script.npk, needed to preserve redirect.nxs")
    args = parser.parse_args()
    prefix = f"patch2.{args.platform}.{args.index}"
    manifest = ROOT / f"evidence/{prefix}.version"
    entries = parse_manifest(args.platform, args.index, manifest.read_text())
    known = {entry["path"]: entry for entry in entries}
    parts = [entry["part"] for entry in entries if entry["kind"] == "check"]
    for part in parts:
        if part == "raw":
            continue
        target = args.output / ("script.npk" if part == "script" else f"res/{part}.npk")
        provenance = target.with_suffix(".provenance.json")
        if target.exists() and provenance.exists():
            data = json.loads(provenance.read_text())
            if (data.get("index") == args.index and data.get("platform") == args.platform
                    and (part != "script" or not args.script_base or data.get("preserved_base_entries"))):
                with target.open("rb") as handle:
                    if hashlib.file_digest(handle, "sha256").hexdigest() == data["sha256"]:
                        print(f"Verified existing {part}", flush=True)
                        continue
        rebuild(args.root, args.platform, args.index, part, manifest, target,
                args.script_base if part == "script" else None)
    check_path = f"{prefix}/raw.check"
    verify(args.root / check_path, known[check_path])
    groups = {}
    for line in zlib.decompress((args.root / check_path).read_bytes()).decode().splitlines():
        if not line.strip():
            continue
        filename, md5, size, version, offset = line.split()
        path = PurePosixPath(filename)
        if path.is_absolute() or ".." in path.parts or ":" in filename or "\\" in filename:
            raise ValueError("Invalid raw asset path")
        groups.setdefault(int(version), []).append((path, md5, int(size), int(offset)))
    count = total = 0
    for version, rows in groups.items():
        relative = f"{prefix}/{version}/raw.data"
        source = args.root / relative
        verify(source, known[relative])
        with source.open("rb") as handle:
            for name, md5, size, offset in rows:
                if offset < 0 or size < 0 or offset + size > source.stat().st_size:
                    raise ValueError("Raw entry exceeds payload")
                handle.seek(offset)
                data = handle.read(size)
                if hashlib.md5(data).hexdigest() != md5:
                    raise ValueError(f"Raw asset MD5 mismatch: {name}")
                destination = args.output / "res" / str(name)
                destination.parent.mkdir(parents=True, exist_ok=True)
                destination.write_bytes(data)
                count += 1
                total += size
    report = {"platform": args.platform, "index": args.index, "npk_parts": len(parts) - 1,
              "raw_files_verified": count, "raw_bytes": total, "runtime_tested": False}
    args.output.joinpath("assembly-report.json").write_text(json.dumps(report, indent=2))
    print(json.dumps(report), flush=True)


if __name__ == "__main__":
    main()
