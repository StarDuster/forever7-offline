from pathlib import Path
import hashlib
import struct
import subprocess
import sys
import tempfile
import unittest
import zlib

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from project7_dex_filter import (INPUT_SHA256, REMOVE, definitions,
                                 filter_class_definitions, remove_manual_login, u32)


def signed(data):
    result = bytearray(data)
    result[12:32] = hashlib.sha1(result[32:]).digest()
    struct.pack_into('<I', result, 8, zlib.adler32(result[12:]) & 0xffffffff)
    return bytes(result)


def fixture():
    """Structural zero-method fixture; it is not an Android runtime test."""
    names = [b'Lex/A;', b'Lex/B;', b'Lex/C;']
    strings, types, classes = 112, 124, 136
    data_offset = 232
    result = bytearray(data_offset)
    for i, name in enumerate(names):
        struct.pack_into('<I', result, strings + i * 4, len(result))
        struct.pack_into('<I', result, types + i * 4, i)
        struct.pack_into('<8I', result, classes + i * 32,
                         i, 1, 0xffffffff, 0, 0xffffffff, 0, 0, 0)
        result.extend(bytes([len(name)]) + name + b'\0')
    result.extend(b'\0' * (-len(result) % 4))
    map_offset = len(result)
    rows = [(0, 1, 0), (1, 3, strings), (2, 3, types), (6, 3, classes),
            (0x2002, 3, data_offset), (0x1000, 1, map_offset)]
    result.extend(struct.pack('<I', len(rows)))
    for kind, count, offset in rows:
        result.extend(struct.pack('<HHII', kind, 0, count, offset))
    result[:8] = b'dex\n035\0'
    for offset, value in [(32, len(result)), (36, 112), (40, 0x12345678),
                          (52, map_offset), (56, 3), (60, strings), (64, 3),
                          (68, types), (96, 3), (100, classes),
                          (104, len(result) - data_offset), (108, data_offset)]:
        struct.pack_into('<I', result, offset, value)
    return signed(result)


class Project7DexFilterTests(unittest.TestCase):
    def apply(self, data, remove=('Lex/B;',)):
        return filter_class_definitions(data, remove,
                                        expected_sha256=hashlib.sha256(data).hexdigest())

    def test_compacts_only_definitions_and_leaves_zero_padding(self):
        before = fixture()
        after = self.apply(before)
        self.assertEqual(list(definitions(after)), ['Lex/A;', 'Lex/C;'])
        co = u32(before, 100)
        self.assertEqual(after[co + 64:co + 96], b'\0' * 32)
        self.assertEqual(len(after), len(before))
        for name, row in definitions(after).items():
            self.assertEqual(row, definitions(before)[name])
        self.assertEqual(after[u32(before, 108):u32(before, 52)],
                         before[u32(before, 108):u32(before, 52)])

    def test_missing_empty_or_entire_set_is_rejected(self):
        for names in ((), ('Lex/D;',), tuple(definitions(fixture()))):
            with self.subTest(names=names), self.assertRaises(ValueError):
                self.apply(fixture(), names)

    def test_input_pin_and_checksum_are_required(self):
        data = fixture()
        with self.assertRaisesRegex(ValueError, 'SHA256'):
            filter_class_definitions(data, ['Lex/B;'], expected_sha256='0' * 64)
        corrupted = bytearray(data)
        corrupted[-1] ^= 1
        with self.assertRaisesRegex(ValueError, 'SHA1'):
            self.apply(bytes(corrupted))

    def test_wrong_class_map_and_bounds_are_rejected(self):
        data = fixture()
        wrong = bytearray(data)
        map_item = u32(data, 52) + 4 + 3 * 12
        struct.pack_into('<I', wrong, map_item + 4, 2)
        with self.assertRaisesRegex(ValueError, 'map/header'):
            self.apply(signed(wrong))
        short = bytearray(data)
        struct.pack_into('<I', short, 100, len(data) - 4)
        with self.assertRaisesRegex(ValueError, 'outside file'):
            self.apply(signed(short))

    def test_duplicate_class_definition_rejected(self):
        data = bytearray(fixture())
        struct.pack_into('<I', data, u32(data, 100) + 32, 0)
        with self.assertRaisesRegex(ValueError, 'Duplicate'):
            self.apply(signed(data))

    def test_hiddenapi_indexed_class_metadata_is_rejected(self):
        data = bytearray(fixture())
        offset = u32(data, 52) + 4 + 4 * 12
        struct.pack_into('<H', data, offset, 0xf000)
        with self.assertRaisesRegex(ValueError, 'hiddenapi'):
            self.apply(signed(data))

    def test_real_supported_dex_independent_parser_and_retained_code(self):
        path = ROOT / 'analysis/project7/official-build-inputs-v1/classes3.dex'
        if not path.is_file():
            self.skipTest('Maintainer pinned materialization absent')
        data = path.read_bytes()
        self.assertEqual(hashlib.sha256(data).hexdigest(), INPUT_SHA256)
        filtered = remove_manual_login(data)
        self.assertEqual(set(definitions(data)) - set(definitions(filtered)), REMOVE)
        from loguru import logger
        logger.disable('androguard')
        from androguard.core.dex import DEX
        original, target = DEX(data), DEX(filtered)
        self.assertEqual({c.get_name() for c in original.get_classes()} - REMOVE,
                         {c.get_name() for c in target.get_classes()})
        def method_code(dex):
            return {(cls.get_name(), method.get_name(), method.get_descriptor()):
                    (method.get_code().get_raw() if method.get_code() else None)
                    for cls in dex.get_classes() if cls.get_name() not in REMOVE
                    for method in cls.get_methods()}
        self.assertEqual(method_code(original), method_code(target))
        tool = ROOT / 'toolchains/build-tools/android-37.0/dexdump'
        if tool.is_file():
            with tempfile.TemporaryDirectory() as directory:
                dex = Path(directory) / 'classes3.dex'
                dex.write_bytes(filtered)
                checked = subprocess.run([str(tool), '-c', str(dex)], capture_output=True, text=True)
                self.assertEqual(checked.returncode, 0, checked.stderr)
                self.assertIn('Checksum verified', checked.stdout)
        with self.assertRaises(ValueError):
            remove_manual_login(filtered)


if __name__ == '__main__':
    unittest.main()
