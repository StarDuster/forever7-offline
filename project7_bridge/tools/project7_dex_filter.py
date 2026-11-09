"""Remove the pinned manual-login class definitions without rewriting game code.

The original ID tables and method/data bytes stay at their original offsets.
Class_defs and class_data are compacted, the unused tails become zero padding,
their map counts change, and DEX SHA1/Adler32 are recalculated. This is not an APK
builder and does not provide the replacement implementation by itself.
"""
import _bootstrap  # noqa: E402,F401
import argparse
import hashlib
import json
from pathlib import Path
import struct
import zlib

INPUT_SHA256 = 'bfdba3e247c0e51a8c121e875baa81e49fbf73c15a30d5f827d1fc2ad02b471f'
PREFIX = 'Lcom/netease/qrzd/Project7LoginDialog'
REMOVE = frozenset([PREFIX + ';', PREFIX + '$Candidate;', PREFIX + '$Form;',
                    PREFIX + '$1;'] +
                   [PREFIX + '$$ExternalSyntheticLambda%d;' % i for i in range(20)])


def require(condition, message):
    if not condition:
        raise ValueError(message)


def u32(data, offset):
    require(0 <= offset <= len(data) - 4, 'DEX offset outside file')
    return struct.unpack_from('<I', data, offset)[0]


def span(data, offset, count, width):
    require(0 <= offset <= len(data) and 0 <= count <= len(data) // width and
            offset + count * width <= len(data), 'DEX section outside file')
    return data[offset:offset + count * width]


def validate_header(data):
    require(len(data) >= 112 and data[:8] in (b'dex\n035\0', b'dex\n038\0'),
            'Unsupported DEX magic/version')
    require(u32(data, 32) == len(data) and u32(data, 36) == 112 and
            u32(data, 40) == 0x12345678, 'Unsupported DEX header')
    require(hashlib.sha1(data[32:]).digest() == data[12:32], 'DEX SHA1 mismatch')
    require(zlib.adler32(data[12:]) & 0xffffffff == u32(data, 8), 'DEX checksum mismatch')
    require(u32(data, 44) == 0 and u32(data, 48) == 0, 'Linked DEX not supported')
    require(u32(data, 104) + u32(data, 108) == len(data), 'Invalid DEX data range')


def string_at(data, index):
    count, table = u32(data, 56), u32(data, 60)
    require(index < count, 'Invalid string index')
    span(data, table, count, 4)
    offset = u32(data, table + index * 4)
    # Type descriptors have no embedded NUL, surrogate or modified-UTF8 escape.
    # Decode only their string_data after bounded ULEB128 length metadata.
    for i in range(5):
        require(offset < len(data), 'Short string length')
        value = data[offset]
        offset += 1
        if not value & 128:
            break
    else:
        raise ValueError('Invalid string length')
    end = data.find(b'\0', offset)
    require(end >= offset and end - offset < 65536, 'Invalid type descriptor')
    try:
        return data[offset:end].decode('utf-8')
    except UnicodeError as error:
        raise ValueError('Unsupported type descriptor encoding') from error


def definitions(data):
    validate_header(data)
    tc, to = u32(data, 64), u32(data, 68)
    cc, co = u32(data, 96), u32(data, 100)
    span(data, to, tc, 4)
    span(data, co, cc, 32)
    found = {}
    for i in range(cc):
        offset = co + i * 32
        type_index = u32(data, offset)
        require(type_index < tc, 'Invalid class type index')
        name = string_at(data, u32(data, to + type_index * 4))
        require(name not in found, 'Duplicate class definition')
        found[name] = data[offset:offset + 32]
    return found


def read_uleb(data, offset, limit):
    value = 0
    for i in range(5):
        require(offset < limit, 'Short class_data ULEB128')
        byte = data[offset]
        offset += 1
        require(i < 4 or byte < 16, 'Overflowing class_data ULEB128')
        value |= (byte & 127) << (7 * i)
        if not byte & 128:
            return value, offset
    raise ValueError('Invalid class_data ULEB128')


def compact_class_data(data, original, remove, maps):
    """ART requires every nonempty class_data item to have a declaring class.

    class_data offsets are referenced only by class_defs. Keep all other file
    offsets (notably code/debug items) fixed; move the retained encoded records
    verbatim within their original section and zero the released tail.
    """
    removed = {u32(row, 24) for name, row in original.items() if name in remove} - {0}
    retained = {u32(row, 24) for name, row in original.items() if name not in remove} - {0}
    require(not removed & retained, 'Shared removed/retained class_data')
    entries = [m for m in maps if m[0] == 0x2000]
    if not entries:
        require(not removed and not retained, 'Missing class_data map')
        return None, {}, None
    require(len(entries) == 1, 'Duplicate class_data section')
    kind, count, start, map_record = entries[0]
    end = min([m[2] for m in maps if m[2] > start] + [len(data)])
    cursor, rows = start, {}
    for unused in range(count):
        item_start = cursor
        sizes = []
        for i in range(4):
            size, cursor = read_uleb(data, cursor, end)
            require(size <= len(data), 'Oversized class_data count')
            sizes.append(size)
        for size, width in zip(sizes, (2, 2, 3, 3)):
            for i in range(size * width):
                unused_value, cursor = read_uleb(data, cursor, end)
        rows[item_start] = data[item_start:cursor]
    require(not any(data[cursor:end]), 'Nonzero class_data section tail')
    require(removed | retained <= rows.keys(), 'Class definition references missing class_data')
    require(len(removed) < len(rows), 'Cannot remove whole class_data section')
    kept, relocated, target = [], {}, start
    for offset, encoded in rows.items():
        if offset in removed:
            continue
        relocated[offset] = target
        kept.append(encoded)
        target += len(encoded)
    packed = b''.join(kept)
    return (start, end, packed + b'\0' * (end - start - len(packed))), relocated, (map_record + 4, len(kept))


def filter_class_definitions(data, remove, *, expected_sha256):
    """Exact-input utility; callers supply the full class set, never a prefix."""
    require(hashlib.sha256(data).hexdigest() == expected_sha256, 'Unexpected DEX input SHA256')
    remove = frozenset(remove)
    require(remove and all(isinstance(x, str) for x in remove), 'Empty/invalid removal set')
    original = definitions(data)
    require(remove <= original.keys(), 'Expected class definition missing')
    require(len(remove) < len(original), 'Cannot remove all class definitions')
    co, cc = u32(data, 100), u32(data, 96)
    require(co >= 112 and co % 4 == 0 and co + cc * 32 <= u32(data, 108),
            'Class table overlaps data/header')
    mo = u32(data, 52)
    require(mo >= u32(data, 108) and mo % 4 == 0, 'Invalid DEX map offset')
    mc = u32(data, mo)
    span(data, mo + 4, mc, 12)
    records, maps = [], []
    previous, kinds = -1, set()
    for i in range(mc):
        off = mo + 4 + i * 12
        kind, reserved, count, position = struct.unpack_from('<HHII', data, off)
        require(reserved == 0 and count > 0 and position > previous and position < len(data)
                and kind not in kinds, 'Invalid/duplicate/out-of-order map item')
        kinds.add(kind)
        require(kind != 0xf000, 'Indexed hiddenapi class data is not supported')
        previous = position
        maps.append((kind, count, position, off))
        if kind == 6:
            require(count == cc and position == co, 'Class map/header mismatch')
            records.append(off)
    require(len(records) == 1, 'Expected one class map entry')
    class_data, relocated, class_data_map = compact_class_data(data, original, remove, maps)
    kept = {}
    for name, row in original.items():
        if name in remove:
            continue
        updated = bytearray(row)
        offset = u32(row, 24)
        if offset:
            struct.pack_into('<I', updated, 24, relocated[offset])
        kept[name] = bytes(updated)
    packed = b''.join(kept.values())
    out = bytearray(data)
    out[co:co + cc * 32] = packed + b'\0' * (len(remove) * 32)
    struct.pack_into('<I', out, 96, len(kept))
    struct.pack_into('<I', out, records[0] + 4, len(kept))
    if class_data is not None:
        start, end, content = class_data
        out[start:end] = content
        struct.pack_into('<I', out, class_data_map[0], class_data_map[1])
    out[12:32] = hashlib.sha1(out[32:]).digest()
    struct.pack_into('<I', out, 8, zlib.adler32(out[12:]) & 0xffffffff)
    result = bytes(out)
    require(definitions(result) == kept, 'Retained class definitions changed')
    ranges = [(8, 32), (96, 100), (co, co + cc * 32), (records[0] + 4, records[0] + 8)]
    if class_data is not None:
        ranges += [(class_data[0], class_data[1]), (class_data_map[0], class_data_map[0] + 4)]
    # Prove all instructions, IDs, annotations and remaining map entries unchanged.
    cursor = 0
    for start, end in sorted(ranges):
        require(data[cursor:start] == result[cursor:start], 'Unexpected DEX byte mutation')
        cursor = end
    require(data[cursor:] == result[cursor:], 'Unexpected DEX trailing mutation')
    return result


def remove_manual_login(data):
    require(hashlib.sha256(data).hexdigest() == INPUT_SHA256, 'Unexpected DEX input SHA256')
    found = definitions(data)
    family = {name for name in found if name == PREFIX + ';' or name.startswith(PREFIX + '$')}
    require(family == REMOVE, 'Unexpected Project7 login family')
    return filter_class_definitions(data, REMOVE, expected_sha256=INPUT_SHA256)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input', type=Path)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    require(not args.output.exists(), 'Output already exists')
    original = args.input.read_bytes()
    result = remove_manual_login(original)
    with args.output.open('xb') as stream:
        stream.write(result)
    print(json.dumps({'removed_classes': len(REMOVE), 'bytes': len(result),
                      'sha256': hashlib.sha256(result).hexdigest(),
                      'replacement_still_required': True}))


if __name__ == '__main__':
    main()
