"""Prepare a private CDN snapshot that installs the local init bootstrap.

Keeps original payloads and only appends the changed init module plus APK/IPA
bootstrap entries absent from the official script.check. The output is a local
experiment, not an official update. No package signature or device is changed.
"""
import argparse
import hashlib
import json
from pathlib import Path
import zlib

from extract_scripts import ScriptArchive
from preserve_cdn import parse_manifest


def build(platform, base_manifest, base_root, baseline_path, patched_path, index, output):
    baseline, patched = ScriptArchive(baseline_path), ScriptArchive(patched_path)
    original_records = {row[0]: row for row in baseline.entries}
    changed = []
    for row in patched.entries:
        old = original_records.get(row[0])
        if old is None or patched.data[row[1]:row[1] + row[2]] != baseline.data[old[1]:old[1] + old[2]]:
            changed.append(row[0])
    if changed != [0xacb9b80e] or set(original_records) != {row[0] for row in patched.entries}:
        raise ValueError('Expected exactly the init module to change, with all base entries retained')
    base_index = int(base_manifest.name.split('.')[2])
    base_prefix = 'patch2.%s.%s' % (platform, base_index)
    prefix = 'patch2.%s.%s' % (platform, index)
    if index <= base_index:
        raise ValueError('Private update index must be newer than the preserved snapshot')
    rows = [line.split() for line in zlib.decompress((base_root / base_prefix / 'script.check').read_bytes()).decode('ascii').splitlines() if line.strip()]
    row_index = {int(row[0]): i for i, row in enumerate(rows)}
    delta = bytearray()
    injected = []
    for row in patched.entries:
        fid, position, csize, usize, chash, uhash, flags = row
        if fid in row_index and fid not in changed:
            continue
        if flags not in (0, 2) or (0 if csize == usize and chash == uhash else 2) != flags:
            raise ValueError('Entry cannot be represented by the patch check format')
        payload = patched.data[position:position + csize]
        fields = [str(fid), hashlib.md5(payload).hexdigest(), str(csize), str(chash),
                  str(usize), str(uhash), str(index), str(len(delta))]
        delta.extend(payload)
        if fid in row_index:
            rows[row_index[fid]] = fields
        else:
            rows.append(fields)
        injected.append('%08x' % fid)
    destination = output / prefix
    (destination / str(index)).mkdir(parents=True, exist_ok=True)
    # The release client may use add_batch(ids, sizes, concatenated_data),
    # without consulting offsets. Keep each version's rows in payload order.
    rows.sort(key=lambda row: (int(row[6]), int(row[7])))
    check = destination / 'script.check'
    check.write_bytes(zlib.compress(('\n'.join(' '.join(row) for row in rows) + '\n').encode('ascii')))
    data_file = destination / str(index) / 'script.data'
    data_file.write_bytes(delta)
    lines = base_manifest.read_text().splitlines()
    lines = [('script=1 %s:%s' % (hashlib.md5(check.read_bytes()).hexdigest(), check.stat().st_size))
             if line.startswith('script=') else line for line in lines]
    lines.append('%s=script:%s:%s' % (index, hashlib.md5(delta).hexdigest(), len(delta)))
    manifest = destination / 'version'
    manifest.write_text('\n'.join(lines) + '\n')
    index_file = destination / ('patch2_' + platform)
    index_file.write_text(str(index) + '\n')
    for entry in parse_manifest(platform, base_index, base_manifest.read_text()):
        relative = Path(entry['path']).relative_to(base_prefix)
        if relative.as_posix() == 'script.check':
            continue
        alias = destination / relative
        alias.parent.mkdir(parents=True, exist_ok=True)
        if not alias.exists():
            alias.hardlink_to((base_root / entry['path']).resolve())
    routes = {'/' + entry['path'].replace(base_prefix + '/', prefix + '/', 1):
              str((base_root / entry['path']).resolve())
              for entry in parse_manifest(platform, base_index, base_manifest.read_text())}
    routes.update({'/' + prefix + '/version': str(manifest.resolve()),
                   '/' + prefix + '/script.check': str(check.resolve()),
                   '/' + prefix + '/%s/script.data' % index: str(data_file.resolve()),
                   '/pl/patch2_' + platform: str(index_file.resolve())})
    route_map = output / 'route-map.json'
    route_map.write_text(json.dumps(routes, indent=2) + '\n')
    report = {'platform': platform, 'private_index': index, 'base_index': base_index,
              'injected_entries': injected, 'delta_bytes': len(delta), 'script_entries': len(rows),
              'route_map': str(route_map.resolve()), 'device_tested': False,
              'original_executable_modified': False}
    (output / 'update-report.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--platform', choices=['ios', 'android'], required=True)
    parser.add_argument('--base-manifest', type=Path, required=True)
    parser.add_argument('--base-root', type=Path, required=True)
    parser.add_argument('--baseline', type=Path, required=True)
    parser.add_argument('--patched', type=Path, required=True)
    parser.add_argument('--index', type=int, default=641)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    build(args.platform, args.base_manifest, args.base_root, args.baseline, args.patched, args.index, args.output)


if __name__ == '__main__':
    main()
