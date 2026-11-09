"""Download the selected official Android runtime tools into this workspace.

Uses the pinned URLs/sizes/checksums discovered from Google's SDK repository
and Eclipse Adoptium's release metadata. Does not modify global SDK settings.
"""
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
from pathlib import Path
import subprocess
import tarfile
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
DESTINATIONS = {"platform-tools": "android-sdk", "emulator": "android-sdk",
                "system-image": "android-sdk/system-images/android-30/google_apis", "jre": "java"}


def install(item):
    archive = ROOT / "toolchains/downloads" / item["url"].rsplit("/", 1)[-1]
    archive.parent.mkdir(parents=True, exist_ok=True)
    algorithm = "sha256" if item.get("sha256") else "sha1"
    def valid():
        if not archive.exists() or archive.stat().st_size != item["size"]:
            return False
        with archive.open("rb") as handle:
            return hashlib.file_digest(handle, algorithm).hexdigest() == item[algorithm]
    if not valid():
        temporary = archive.with_suffix(archive.suffix + ".part")
        with urllib.request.urlopen(item["url"], timeout=60) as response, temporary.open("wb") as out:
            size = 0
            while block := response.read(1024 * 1024):
                size += len(block)
                if size > item["size"]:
                    raise ValueError("Tool download exceeds published size")
                out.write(block)
        temporary.replace(archive)
        if not valid():
            raise ValueError(f"Tool checksum mismatch: {item['name']}")
    destination = ROOT / "toolchains" / DESTINATIONS[item["name"]]
    destination.mkdir(parents=True, exist_ok=True)
    if archive.suffix == ".zip":
        subprocess.run(["/usr/bin/unzip", "-oq", str(archive), "-d", str(destination)], check=True)
    else:
        with tarfile.open(archive) as handle:
            handle.extractall(destination, filter="data")
    print(f"Verified and extracted: {item['name']}", flush=True)


def main():
    selected = json.loads((ROOT / "evidence/android-toolchains.json").read_text())
    with ThreadPoolExecutor(max_workers=4) as pool:
        list(pool.map(install, selected))


if __name__ == "__main__":
    main()
