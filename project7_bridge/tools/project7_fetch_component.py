#!/usr/bin/env python3
"""Resolve the pinned Project7 component from an explicit URL or offline input.

No implicit/copied component: URL or path is caller-supplied. The default cache is
`.offline-deps/component-v2.10.1.zip` (ignored/private), verified against the
descriptor before use. Official CDN URL is preferred when configured; this tool
does not invent a source URL.
"""
from __future__ import annotations
import _bootstrap  # noqa: E402,F401
import argparse, hashlib, json, os, shutil, tempfile, urllib.request
from pathlib import Path

from _bootstrap import ROOT
DESCRIPTOR = ROOT / 'upstream/project7/component.json'
CACHE = ROOT / '.offline-deps' / 'component-v2.10.1.zip'
MAX_BYTES = 128 * 1024 * 1024


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def expected():
    d = json.loads(DESCRIPTOR.read_text())
    return d['sha256'], d['bytes']


def verify(path: Path):
    sha_expected, size = expected()
    data = path.read_bytes()
    if len(data) != size or sha(data) != sha_expected:
        raise ValueError('Project7 component size/hash mismatch: ' + str(path))
    return data


def resolve(url: str | None = None, offline_input: Path | None = None) -> Path:
    sha_expected, size = expected()
    # Explicit source takes precedence over a valid cache. A bad explicit
    # offline input must fail instead of silently reusing an existing cache.
    if offline_input is not None:
        data = offline_input.read_bytes()
        if len(data) != size or sha(data) != sha_expected:
            raise ValueError('Offline Project7 component size/hash mismatch')
        CACHE.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.NamedTemporaryFile(dir=CACHE.parent, prefix=".component-", delete=False) as output:
            temp = Path(output.name)
            try:
                output.write(data)
                output.flush()
                os.fsync(output.fileno())
                os.replace(temp, CACHE)
            finally:
                temp.unlink(missing_ok=True)
        return CACHE
    url = url or os.environ.get('P7_COMPONENT_URL')
    if url:
        if not url.lower().startswith(('https://', 'http://')):
            raise ValueError('Project7 component URL must be http(s)')
        CACHE.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.NamedTemporaryFile(dir=CACHE.parent, prefix='.component-', delete=False) as temporary:
            temp = Path(temporary.name)
            try:
                with urllib.request.urlopen(url, timeout=60) as response:
                    length = 0
                    while True:
                        chunk = response.read(1024 * 1024)
                        if not chunk:
                            break
                        length += len(chunk)
                        if length > size:
                            raise ValueError('Project7 component download exceeds pinned size')
                        temporary.write(chunk)
                temporary.flush()
                os.fsync(temporary.fileno())
                if length != size or sha(temp.read_bytes()) != sha_expected:
                    raise ValueError('Project7 component download size/hash mismatch')
                os.replace(temp, CACHE)
            finally:
                temp.unlink(missing_ok=True)
        return CACHE
    if CACHE.is_file():
        try:
            verify(CACHE)
            return CACHE
        except ValueError:
            pass
    raise ValueError('Project7 component missing; supply P7_COMPONENT_URL or --offline-input (sha256 %s)' % sha_expected)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--url', help='explicit official/private component URL (or P7_COMPONENT_URL)')
    parser.add_argument('--offline-input', type=Path, help='pre-downloaded component zip')
    parser.add_argument('--output', type=Path, help='optional verified output path')
    args = parser.parse_args()
    path = resolve(args.url, args.offline_input)
    if args.output is not None:
        args.output.write_bytes(path.read_bytes())
        path = args.output
    print(json.dumps({'component': str(path), 'bytes': path.stat().st_size,
                      'sha256': sha(path.read_bytes())}, sort_keys=True))


if __name__ == '__main__':
    main()
