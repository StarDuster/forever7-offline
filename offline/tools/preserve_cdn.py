"""Preserve official patch manifests and payloads, verifying published MD5s.

URLs and filenames are reconstructed from the client's pconst, patch_part,
patch_info and pdownload modules. Downloads do not log in or execute payloads.
Identical Android/iOS payloads share one local content-addressed object.
"""
from __future__ import annotations
import _bootstrap  # noqa: E402,F401

import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import hashlib
import json
import os
from pathlib import Path
import re
import threading
import time
import urllib.request

from _bootstrap import ROOT
BASE = "https://g58.gph.netease.com/"
PART = re.compile(r"[a-z][a-z0-9_]*\Z")
MD5 = re.compile(r"[0-9a-f]{32}\Z")


def parse_manifest(platform, index, content):
    prefix = f"patch2.{platform}.{index}"
    result = []
    for line in content.splitlines():
        if not line.strip():
            continue
        name, spec = line.split("=", 1)
        if name.isdecimal():
            for item in spec.split():
                part, md5, size = item.split(":")
                if not PART.fullmatch(part) or not MD5.fullmatch(md5):
                    raise ValueError("Invalid payload entry")
                result.append({"platform": platform, "part": part,
                               "path": f"{prefix}/{int(name)}/{part}.data",
                               "md5": md5, "size": int(size), "kind": "data"})
        else:
            kind, spec = spec.split()
            md5, size = spec.split(":")
            if not PART.fullmatch(name) or not MD5.fullmatch(md5) or kind not in ("1", "2"):
                raise ValueError("Invalid check entry")
            result.append({"platform": platform, "part": name,
                           "path": f"{prefix}/{name}.check", "md5": md5,
                           "size": int(size), "kind": "check", "part_type": int(kind)})
    if any(item["size"] < 0 for item in result):
        raise ValueError("Negative file size")
    return result


def md5_file(path):
    with path.open("rb") as handle:
        return hashlib.file_digest(handle, "md5").hexdigest()


def fetch_verified(item, root):
    destination = root / "objects" / item["md5"]
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.exists():
        if destination.stat().st_size == item["size"] and md5_file(destination) == item["md5"]:
            return destination
        raise ValueError(f"Existing preserved object is corrupt: {destination}")
    last_error = None
    for attempt in range(3):
        temporary = destination.with_suffix(".part")
        try:
            digest = hashlib.md5()
            size = 0
            with urllib.request.urlopen(BASE + item["path"], timeout=45) as response, temporary.open("wb") as out:
                while block := response.read(1024 * 1024):
                    size += len(block)
                    if size > item["size"]:
                        raise ValueError("Response larger than published size")
                    digest.update(block)
                    out.write(block)
            if size != item["size"] or digest.hexdigest() != item["md5"]:
                raise ValueError(f"Size/MD5 mismatch: {item['path']}")
            temporary.replace(destination)
            return destination
        except Exception as exc:
            last_error = exc
            temporary.unlink(missing_ok=True)
            if attempt < 2:
                time.sleep(attempt + 1)
    raise RuntimeError(f"{item['path']}: {last_error}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--platform", choices=["android", "ios", "both"], default="both")
    parser.add_argument("--index", type=int, default=640)
    parser.add_argument("--parts", default="script", help="Comma-separated parts, or all")
    parser.add_argument("--checks-only", action="store_true")
    parser.add_argument("--download", action="store_true")
    parser.add_argument("--workers", type=int, default=6)
    parser.add_argument("--root", type=Path, default=ROOT / "originals/cdn")
    args = parser.parse_args()
    platforms = ["android", "ios"] if args.platform == "both" else [args.platform]
    entries = []
    for platform in platforms:
        manifest = ROOT / f"evidence/patch2.{platform}.{args.index}.version"
        if not manifest.exists():
            raise SystemExit(f"Preserve and inspect the official manifest first: {manifest}")
        entries.extend(parse_manifest(platform, args.index, manifest.read_text()))
    parts = set(args.parts.split(","))
    entries = [entry for entry in entries if (args.parts == "all" or entry["part"] in parts)
               and (not args.checks_only or entry["kind"] == "check")]
    grouped = {}
    for entry in entries:
        group = grouped.setdefault(entry["md5"], [])
        if group and group[0]["size"] != entry["size"]:
            raise ValueError("Same MD5 with inconsistent size")
        group.append(entry)
    total = sum(group[0]["size"] for group in grouped.values())
    print(json.dumps({"references": len(entries), "unique_files": len(grouped), "bytes": total,
                      "decimal_GB": round(total / 1e9, 3)}, ensure_ascii=False), flush=True)
    report_name = f"cdn-{args.platform}-{args.parts.replace(',', '-')}{'-checks' if args.checks_only else ''}"
    plan_path = ROOT / f"reports/{report_name}.plan.json"
    plan_path.write_text(json.dumps(entries, indent=2))
    if not args.download:
        return
    args.root.mkdir(parents=True, exist_ok=True)
    done, failed, saved = 0, [], 0
    started = last_report = time.monotonic()
    with ThreadPoolExecutor(max_workers=args.workers) as executor:
        tasks = {executor.submit(fetch_verified, group[0], args.root): group for group in grouped.values()}
        for task in as_completed(tasks):
            group = tasks[task]
            try:
                obj = task.result()
                for entry in group:
                    path = args.root / entry["path"]
                    path.parent.mkdir(parents=True, exist_ok=True)
                    if not path.exists():
                        os.link(obj, path)
                saved += group[0]["size"]
            except Exception as exc:
                failed.append({"paths": [item["path"] for item in group], "error": str(exc)})
            done += 1
            now = time.monotonic()
            if now - last_report >= 15 or done == len(tasks):
                print(f"{done}/{len(tasks)} files; {saved/1e9:.3f}/{total/1e9:.3f} GB; failures={len(failed)}", flush=True)
                last_report = now
    summary = {"files": len(grouped), "verified": len(grouped) - len(failed),
               "verified_bytes": saved, "seconds": round(time.monotonic() - started, 1), "failures": failed}
    (ROOT / f"reports/{report_name}.summary.json").write_text(json.dumps(summary, indent=2))
    print(json.dumps(summary), flush=True)
    if failed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
