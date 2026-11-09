"""Inventory Android APK or iOS IPA without installing or running it."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import plistlib
import struct
import zipfile


def macho_slices(data):
    """Read Mach-O/FAT headers; cryptid describes executable encryption only."""
    if len(data) < 4:
        raise ValueError("Truncated executable")
    magic = data[:4]
    if magic in (b"\xca\xfe\xba\xbe", b"\xca\xfe\xba\xbf"):
        count = struct.unpack_from(">I", data, 4)[0]
        width = 32 if magic[-1] == 191 else 20
        if count > 32 or 8 + count * width > len(data):
            raise ValueError("Invalid FAT architecture table")
        result = []
        for i in range(count):
            start = 8 + i * width
            offset, size = struct.unpack_from(">QQ" if width == 32 else ">II", data, start + 8)
            if offset + size > len(data):
                raise ValueError("Truncated FAT slice")
            result.extend(macho_slices(data[offset:offset + size]))
        return result
    formats = {b"\xcf\xfa\xed\xfe": ("<", 32), b"\xce\xfa\xed\xfe": ("<", 28),
               b"\xfe\xed\xfa\xcf": (">", 32), b"\xfe\xed\xfa\xce": (">", 28)}
    if magic not in formats:
        raise ValueError("Not a Mach-O executable")
    endian, header_size = formats[magic]
    if len(data) < header_size:
        raise ValueError("Truncated Mach-O header")
    cpu, subtype, filetype, count, command_size = struct.unpack_from(endian + "5I", data, 4)
    end = header_size + command_size
    if end > len(data) or count > command_size // 8:
        raise ValueError("Invalid load command table")
    result = {"cpu_type": cpu, "cpu_subtype": subtype, "filetype": filetype,
              "architecture": {0x100000C: "arm64", 12: "arm", 0x1000007: "x86_64", 7: "x86"}.get(cpu, "unknown"),
              "encryption_commands": []}
    position = header_size
    for _ in range(count):
        command, size = struct.unpack_from(endian + "II", data, position)
        if size < 8 or position + size > end:
            raise ValueError("Invalid load command size")
        if command in (0x21, 0x2C):
            if size < 20:
                raise ValueError("Truncated encryption command")
            offset, length, cryptid = struct.unpack_from(endian + "3I", data, position + 8)
            result["encryption_commands"].append({"crypt_offset": offset, "crypt_size": length, "cryptid": cryptid})
        position += size
    result["encrypted"] = any(cmd["cryptid"] != 0 for cmd in result["encryption_commands"])
    return [result]


def inspect(path, check_crc=False):
    with path.open("rb") as handle:
        sha256 = hashlib.file_digest(handle, "sha256").hexdigest()
    with zipfile.ZipFile(path) as archive:
        files = archive.infolist()
        names = {entry.filename for entry in files}
        report = {"file": str(path.resolve()), "bytes": path.stat().st_size, "sha256": sha256,
                  "entries": len(files), "uncompressed_bytes": sum(entry.file_size for entry in files),
                  "extensions": dict(Counter(Path(entry.filename).suffix for entry in files)),
                  "runtime_tested": False}
        if "AndroidManifest.xml" in names:
            from loguru import logger
            logger.disable("androguard")
            from androguard.core.axml import AXMLPrinter
            root = AXMLPrinter(archive.read("AndroidManifest.xml")).get_xml_obj()
            ns = "{http://schemas.android.com/apk/res/android}"
            report.update({"platform": "android", "bundle_id": root.get("package"),
                           "version": root.get(ns + "versionName"), "build": root.get(ns + "versionCode"),
                           "architectures": sorted({name.split("/")[1] for name in names if name.startswith("lib/")})})
        else:
            plists = [name for name in names if name.startswith("Payload/") and name.endswith(".app/Info.plist") and name.count("/") == 2]
            if len(plists) != 1:
                raise ValueError("Expected one main iOS app bundle")
            info = plistlib.loads(archive.read(plists[0]))
            executable = info["CFBundleExecutable"]
            if "/" in executable or executable in (".", ".."):
                raise ValueError("Invalid bundle executable name")
            binary_name = str(Path(plists[0]).parent / executable)
            slices = macho_slices(archive.read(binary_name))
            report.update({"platform": "ios", "bundle_id": info.get("CFBundleIdentifier"),
                           "version": info.get("CFBundleShortVersionString"), "build": info.get("CFBundleVersion"),
                           "minimum_os": info.get("MinimumOSVersion"), "executable": binary_name,
                           "macho_slices": slices, "executable_encrypted": any(s["encrypted"] for s in slices),
                           "signature_present": any(name.startswith(str(Path(plists[0]).parent) + "/_CodeSignature/") for name in names)})
        report["npk_files"] = [{"path": f.filename, "bytes": f.file_size} for f in files if f.filename.endswith(".npk")]
        if check_crc:
            bad = archive.testzip()
            if bad:
                raise ValueError(f"ZIP CRC mismatch: {bad}")
            report["zip_crc_verified"] = True
        return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("package", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--check-crc", action="store_true")
    args = parser.parse_args()
    report = inspect(args.package, args.check_crc)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2))
    print(json.dumps({k: v for k, v in report.items() if k not in ("npk_files", "extensions")}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
