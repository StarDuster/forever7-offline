"""Compile the single-app resource initializer and patch only binary manifest nodes."""
import _bootstrap  # noqa: E402,F401
from pathlib import Path
import hashlib
import json
import struct
import subprocess

ENTRY = 'com.forever7.offline.ResourceInitActivity'
PROJECT7_ENTRY = 'com.forever7.offline.Project7ResourceInitActivity'
ORIGINAL = 'com.netease.qrzd.Client'


def _chunks(data):
    position = 8
    while position < len(data):
        kind, header, size = struct.unpack_from('<HHI', data, position)
        if size < header or size < 8 or position + size > len(data):
            raise ValueError('Malformed binary manifest chunk')
        yield kind, data[position:position + size]
        position += size
    if position != len(data):
        raise ValueError('Truncated binary manifest')


def _length(data, offset, utf8):
    if utf8:
        n = data[offset]
        if n & 0x80:
            return ((n & 0x7f) << 8) | data[offset + 1], offset + 2
        return n, offset + 1
    n = struct.unpack_from('<H', data, offset)[0]
    if n & 0x8000:
        return ((n & 0x7fff) << 16) | struct.unpack_from('<H', data, offset + 2)[0], offset + 4
    return n, offset + 2


def _strings(chunk):
    count, styles, flags, start, style_start = struct.unpack_from('<IIIII', chunk, 8)
    if styles or style_start:
        raise ValueError('Unexpected styled manifest string pool')
    utf8 = bool(flags & 0x100)
    result = []
    header = struct.unpack_from('<H', chunk, 2)[0]
    for i in range(count):
        offset = start + struct.unpack_from('<I', chunk, header + i * 4)[0]
        size, offset = _length(chunk, offset, utf8)
        if utf8:
            size, offset = _length(chunk, offset, True)
            result.append(chunk[offset:offset + size].decode('utf-8'))
        else:
            result.append(chunk[offset:offset + size * 2].decode('utf-16-le'))
    return result


def _pool(strings):
    offsets, body = [], bytearray()
    for value in strings:
        raw = value.encode('utf-16-le')
        count = len(raw) // 2
        offsets.append(len(body))
        body += struct.pack('<H', count) if count < 0x8000 else struct.pack('<HH', 0x8000 | (count >> 16), count & 0xffff)
        body += raw + b'\0\0'
    body += b'\0' * (-len(body) % 4)
    start = 28 + 4 * len(strings)
    return struct.pack('<HHIIIIII', 1, 28, start + len(body), len(strings), 0, 0, start, 0) + struct.pack('<%dI' % len(strings), *offsets) + body


def _tag(chunk):
    return struct.unpack_from('<I', chunk, 20)[0]


def _attribute(chunk, strings, name):
    start, width, count = struct.unpack_from('<HHH', chunk, 24)
    if width != 20:
        raise ValueError('Unexpected manifest attribute encoding')
    for i in range(count):
        offset = 16 + start + i * width
        if strings[struct.unpack_from('<I', chunk, offset + 4)[0]] == name:
            yield offset


def patch_resource_manifest(data, entry=ENTRY):
    if entry not in (ENTRY, PROJECT7_ENTRY):
        raise ValueError('Unsupported resource initializer activity')
    chunks = list(_chunks(data))
    if not chunks or chunks[0][0] != 1:
        raise ValueError('Expected manifest string pool first')
    strings = _strings(chunks[0][1])
    if ENTRY in strings or PROJECT7_ENTRY in strings:
        raise ValueError('Resource initializer is already in manifest')
    if ORIGINAL not in strings:
        raise ValueError('Original stock activity was not found')
    strings.append(entry)
    new_name = len(strings) - 1
    # The stock launcher is ProtocolLauncher, which subsequently starts Client.
    # Move its MAIN filter to our activity rather than assuming Client owns it.
    filters = []
    opening = None
    depth = 0
    has_main = False
    for index, (kind, chunk) in enumerate(chunks):
        if kind == 0x102:
            tag = strings[_tag(chunk)]
            if tag == 'intent-filter' and opening is None:
                opening, depth, has_main = index, 0, False
            if opening is not None:
                depth += 1
                if tag == 'action':
                    for offset in _attribute(chunk, strings, 'name'):
                        value = struct.unpack_from('<I', chunk, offset + 16)[0]
                        has_main = has_main or strings[value] == 'android.intent.action.MAIN'
        elif kind == 0x103 and opening is not None:
            depth -= 1
            if depth == 0:
                if has_main:
                    filters.append((opening, index))
                opening = None
    if len(filters) != 1:
        raise ValueError('Expected exactly one original MAIN intent filter')
    begin, end = filters[0]
    launcher_filter = chunks[begin:end + 1]
    del chunks[begin:end + 1]
    first = last = None
    depth = 0
    for i, (kind, chunk) in enumerate(chunks):
        if kind == 0x102:
            if first is None and strings[_tag(chunk)] == 'activity':
                for offset in _attribute(chunk, strings, 'name'):
                    if struct.unpack_from('<I', chunk, offset + 16)[0] == strings.index(ORIGINAL):
                        first = i
                        depth = 0
            if first is not None:
                depth += 1
        elif kind == 0x103 and first is not None:
            depth -= 1
            if depth == 0:
                last = i
                break
    if first is None or last is None:
        raise ValueError('No exact original activity declaration')
    original = [(kind, bytes(chunk)) for kind, chunk in chunks[first:last + 1]]
    initializer = bytearray(chunks[first][1])
    for offset in _attribute(initializer, strings, 'name'):
        struct.pack_into('<I', initializer, offset + 8, new_name)
        struct.pack_into('<I', initializer, offset + 16, new_name)
    exported = list(_attribute(initializer, strings, 'exported'))
    if exported:
        for offset in exported:
            struct.pack_into('<I', initializer, offset + 8, 0xffffffff)
            initializer[offset + 15] = 0x12
            struct.pack_into('<I', initializer, offset + 16, 0xffffffff)
    else:
        count = struct.unpack_from('<H', initializer, 28)[0]
        attribute = struct.pack('<IIIHBBI', strings.index('http://schemas.android.com/apk/res/android'),
            strings.index('exported'), 0xffffffff, 8, 0, 0x12, 0xffffffff)
        initializer.extend(attribute)
        struct.pack_into('<I', initializer, 4, len(initializer))
        struct.pack_into('<H', initializer, 28, count + 1)
    chunks[first] = (0x102, bytes(initializer))
    # Clone stock activity attributes and metadata, excluding intent filters.
    # Original filters now lead to initializer; only its explicit verified
    # intent can enter the non-exported engine activity.
    client = []
    skip_depth = 0
    for kind, chunk in original:
        if kind == 0x102:
            if skip_depth or strings[_tag(chunk)] == 'intent-filter':
                skip_depth += 1
                continue
        elif kind == 0x103 and skip_depth:
            skip_depth -= 1
            continue
        client.append((kind, chunk))
    stock = bytearray(client[0][1])
    exported = list(_attribute(stock, strings, 'exported'))
    if exported:
        for offset in exported:
            struct.pack_into('<I', stock, offset + 8, 0xffffffff)
            stock[offset + 15] = 0x12  # TYPE_INT_BOOLEAN
            struct.pack_into('<I', stock, offset + 16, 0)
    # With no filters, an absent exported attribute also defaults to false.
    client[0] = (0x102, bytes(stock))
    chunks[last:last] = launcher_filter
    last += len(launcher_filter)
    chunks[last + 1:last + 1] = client
    chunks[0] = (1, _pool(strings))
    body = b''.join(chunk for kind, chunk in chunks)
    return struct.pack('<HHI', 3, 8, len(body) + 8) + body


def compile_resource_initializer(root, toolchains, output):
    directory = root / 'offline/current/java/android_resource_init'
    classes, dex = output / 'resource-init-classes', output / 'resource-init-dex'
    classes.mkdir(parents=True, exist_ok=True)
    dex.mkdir(parents=True, exist_ok=True)
    java = toolchains / 'java/jdk-17.0.21+9/Contents/Home/bin'
    android = toolchains / 'android-sdk/platforms/android-32/android.jar'
    sources = sorted((directory / 'src').rglob('*.java'))
    subprocess.run([str(java / 'javac'), '-source', '8', '-target', '8', '-Xlint:-options',
                    '-encoding', 'UTF-8', '-cp', str(android), '-d', str(classes)] + [str(p) for p in sources], check=True)
    subprocess.run([str(java / 'java'), '-cp', str(toolchains / 'build-tools/android-37.0/lib/d8.jar'),
                    'com.android.tools.r8.D8', '--min-api', '21', '--lib', str(android),
                    '--output', str(dex)] + [str(p) for p in sorted(classes.rglob('*.class'))], check=True)
    manifest = directory / 'resource_manifest.json'
    document = json.loads(manifest.read_text())
    if len(document['entries']) != 312 or sum(e['bytes'] for e in document['entries']) != 8010923732:
        raise ValueError('Unexpected original resource manifest')
    return dex / 'classes.dex', manifest
