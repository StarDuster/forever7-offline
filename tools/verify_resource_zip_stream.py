"""Exercise the production ZIP importer at full size without a second asset copy.

Streams an unseekable archive with ZIP64 central-directory offsets to Java. Existing targets are
never written: the production skip branch still hashes every member's bytes.
This verifies full archive/ZIP64 compatibility, not fresh native installation.
"""
import argparse
import hashlib
import io
import json
from pathlib import Path
import shutil
import subprocess
import time
import zipfile

ROOT = Path(__file__).resolve().parents[1]


class Pipe(io.RawIOBase):
    def __init__(self, stream):
        self.stream, self.bytes = stream, 0

    def writable(self):
        return True

    def write(self, data):
        written = self.stream.write(data)
        self.bytes += written
        return written

    def tell(self):
        return self.bytes

    def flush(self):
        if not self.stream.closed:
            self.stream.flush()


def verify(resources, work, java_home):
    manifest_path = ROOT / 'runtime/android_resource_init/resource_manifest.json'
    manifest = json.loads(manifest_path.read_text())
    entries = manifest['entries']
    if (len(entries) != manifest['files'] or
            sum(row['bytes'] for row in entries) != manifest['bytes']):
        raise ValueError('Manifest aggregate mismatch')
    resources = resources.resolve(strict=True)
    before = {}
    for row in entries:
        relative = Path(row['name'])
        if relative.is_absolute() or '..' in relative.parts:
            raise ValueError('Unsafe manifest path')
        path = resources / relative
        if path != path.resolve(strict=True) or not path.is_file():
            raise ValueError('Nonregular or symlink source: ' + row['name'])
        stat = path.stat()
        if stat.st_size != row['bytes']:
            raise ValueError('Source size mismatch: ' + row['name'])
        before[path] = (stat.st_dev, stat.st_ino, stat.st_size, stat.st_mtime_ns)
    work.mkdir(parents=True, exist_ok=False)
    classes = work / 'classes'
    classes.mkdir()
    sources = [ROOT / 'runtime/android_resource_init/src/com/forever7/offline/ResourceImporter.java',
               ROOT / 'tools/java/ResourceZipStreamVerifier.java']
    snapshots = []
    for source in sources:
        destination = work / source.name
        shutil.copyfile(source, destination)
        snapshots.append(destination)
    plan = work / 'plan.tsv'
    plan.write_text(''.join('%s\t%s\t%s\n' % (r['name'], r['bytes'], r['sha256']) for r in entries))
    subprocess.run([str(java_home / 'bin/javac'), '-d', str(classes),
                    *map(str, snapshots)], check=True)
    started = time.monotonic()
    with (work / 'java.log').open('w') as log:
        process = subprocess.Popen([str(java_home / 'bin/java'), '-Xmx128m', '-cp', str(classes),
            'ResourceZipStreamVerifier', str(plan), str(resources), str(work / 'result.json')],
            stdin=subprocess.PIPE, stdout=log, stderr=subprocess.STDOUT)
        pipe = Pipe(process.stdin)
        try:
            with zipfile.ZipFile(pipe, 'w', compression=zipfile.ZIP_DEFLATED,
                                 compresslevel=0, allowZip64=True) as archive:
                for row in entries:
                    with (resources / row['name']).open('rb') as source:
                        info = zipfile.ZipInfo('res/' + row['name'])
                        info.file_size = row['bytes']
                        info.compress_type = zipfile.ZIP_DEFLATED
                        info._compresslevel = 0
                        with archive.open(info, 'w') as target:
                            shutil.copyfileobj(source, target, length=1024 * 1024)
            pipe.flush()
            process.stdin.close()
            if process.wait() != 0:
                raise RuntimeError('Production importer failed; inspect ' + str(work / 'java.log'))
        except BaseException:
            if not process.stdin.closed:
                try:
                    process.stdin.close()
                except OSError:
                    pass
            if process.poll() is None:
                process.terminate()
            process.wait()
            raise
    for path, identity in before.items():
        stat = path.stat()
        if (stat.st_dev, stat.st_ino, stat.st_size, stat.st_mtime_ns) != identity:
            raise ValueError('Source changed: ' + str(path))
    result = json.loads((work / 'result.json').read_text())
    if result['archive_bytes'] != pipe.bytes or result['entries'] != len(entries):
        raise ValueError('Archive or entry accounting mismatch')
    result.update(seconds=round(time.monotonic() - started, 3),
        zip64_central_directory=pipe.bytes > zipfile.ZIP64_LIMIT,
        member_sizes_known=True,
        zip_method='DEFLATED level0 streamed with data descriptors',
        manifest_sha256=hashlib.sha256(manifest_path.read_bytes()).hexdigest(),
        source_sha256={s.name: hashlib.sha256(s.read_bytes()).hexdigest() for s in snapshots},
        limitations=['Existing-target branch only; fresh import uses separate tests.',
                     'Host production Java; Android SAF and native complete archive unverified.'])
    (work / 'result.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--resources', type=Path, required=True)
    parser.add_argument('--work', type=Path, required=True)
    parser.add_argument('--java-home', type=Path, required=True)
    args = parser.parse_args()
    verify(args.resources, args.work, args.java_home)
