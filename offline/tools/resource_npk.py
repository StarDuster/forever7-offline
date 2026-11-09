"""Read plain NXPK resource entries by filename without importing game code.

Filename IDs reproduce neox::StringIDLegacy in this client's arm64 library;
cross-checked against redirect.nxs and init.nxs in both original packages.
The opaque per-entry checksum fields are preserved, not treated as CRC32.
"""
import _bootstrap  # noqa: E402,F401
import argparse
from pathlib import Path
import struct
import zlib

import lz4.block

MASK = 0xffffffff


def string_id(value):
    data = value.encode('utf-8') if isinstance(value, str) else value
    a, b, rotation = 0x37a8470e, 0x7758b42b, 0xf4fa8928
    blocks = [int.from_bytes(data[i:i + 4], 'little') for i in range(0, len(data), 4)]
    for value in blocks + [0x9be74448, 0x66f42c48]:
        rotation = ((rotation << 1) | (rotation >> 31)) & MASK
        mixed = rotation ^ 0x267b0b11
        a ^= value
        b ^= value
        product_a = (((b + mixed) & 0xbdeb77de) | 0x02040801) * a
        product_b = (((a + mixed) & 0x7d7ebbde) | 0x00804021) * b
        folded_a = (product_a >> 32) + (product_a & MASK) + bool(product_a >> 32)
        folded_b = ((product_b >> 31) & 0xfffffffe) + (product_b & MASK)
        a = ((folded_a & MASK) + (folded_a >> 32)) & MASK
        b = ((folded_b & MASK) + ((folded_b >> 31) & 2)) & MASK
    return a ^ b


class ResourceArchive:
    def __init__(self, path):
        self.path = Path(path)
        length = self.path.stat().st_size
        with self.path.open('rb') as handle:
            magic, count, a, b, version, offset = struct.unpack('<4s5I', handle.read(24))
            if magic != b'NXPK' or (a, b, version) != (0, 0, 2) or offset + count * 28 != length:
                raise ValueError('Unsupported NXPK layout')
            handle.seek(offset)
            table = handle.read(count * 28)
        self.entries = {}
        for record in struct.iter_unpack('<7I', table):
            fid, position, size, decoded_size, checksum1, checksum2, flags = record
            if fid in self.entries or position < 24 or position + size > offset or flags not in (0, 1, 2):
                raise ValueError('Invalid/unsupported resource index')
            self.entries[fid] = record

    def read_id(self, fid):
        _, position, size, decoded_size, _, _, flags = self.entries[fid]
        if decoded_size > 128 * 1024 * 1024:
            raise ValueError('Resource exceeds extraction limit')
        with self.path.open('rb') as handle:
            handle.seek(position)
            packed = handle.read(size)
        if len(packed) != size:
            raise ValueError('Truncated resource')
        if flags == 2:
            result = lz4.block.decompress(packed, uncompressed_size=decoded_size)
        elif flags == 1:
            result = zlib.decompress(packed)
        else:
            result = packed
        if len(result) != decoded_size:
            raise ValueError('Resource decoded size mismatch')
        return result

    def read(self, filename):
        # Resource paths are archive-relative, with backslashes in the index.
        return self.read_id(string_id(filename.replace('/', '\\').lower()))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('archive', type=Path)
    parser.add_argument('filename')
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    data = ResourceArchive(args.archive).read(args.filename)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(data)
    print('%s: %s bytes, prefix=%s' % (args.output, len(data), data[:32].hex()))


if __name__ == '__main__':
    main()
