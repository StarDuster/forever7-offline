import hashlib
from http.server import ThreadingHTTPServer
import json
from pathlib import Path
import plistlib
import struct
import sys
import tempfile
import threading
from types import SimpleNamespace
import unittest
import urllib.error
import urllib.request
import zipfile
import zlib

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))
from bytecode27 import decode
from build_update_snapshot import build as build_update
from inspect_package import inspect, macho_slices
from rebuild_npk import rebuild
from resource_npk import string_id
from read_data_table import read as read_table
from offline_server import byte_range, make_handler


class BytecodeTests(unittest.TestCase):
    def test_fused_load_relocates_jump_that_needs_extended_argument(self):
        # Expanding a fused load moves a 16-bit jump target beyond 65535.
        # Both the newly needed prefix and the fused instruction must count.
        raw = b"\x94\xff\xff\xad\x01\x00" + b"\x26" * 65529 + b"\x53"
        code = SimpleNamespace(co_code=raw, co_consts=(None, 1), co_varnames=("self",),
                               co_filename="fixture.py", co_name="example", co_lnotab=b"")
        decode(code)
        self.assertEqual(code.co_code[:6], b"\x91\x01\x00\x72\x05\x00")
        self.assertEqual(code.co_code[6:12], b"\x7c\x00\x00\x64\x01\x00")
        self.assertEqual(len(code.co_code), 65542)
        self.assertEqual(code.co_code[65541], 83)

    def test_unknown_opcode_is_rejected(self):
        code = SimpleNamespace(co_code=b"\xff\0\0", co_consts=(), co_varnames=(),
                               co_filename="fixture.py", co_name="example", co_lnotab=b"")
        with self.assertRaisesRegex(ValueError, "Unknown opcode"):
            decode(code)


class ArchiveTests(unittest.TestCase):
    def test_filename_hash_matches_original_client_index_entries(self):
        self.assertEqual(string_id('redirect.nxs'), 0xfb54f059)
        self.assertEqual(string_id('init.nxs'), 0xacb9b80e)
        self.assertEqual(string_id('packed\\dialogue1.png'), 0xc2f6c59d)

    def test_patch_manifest_keeps_native_bootstrap_from_base_archive(self):
        # redirect.nxs exists in the APK, but is absent from script.check.
        # Omitting it produces a valid archive which the native VM cannot boot.
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            folder = root / 'patch2.android.640'
            (folder / '0').mkdir(parents=True)
            payload = folder / '0/script.data'
            payload.write_bytes(b'NEW')
            check = folder / 'script.check'
            check.write_bytes(zlib.compress(b'42 00000000000000000000000000000000 3 1 3 1 0 0\n'))
            manifest = root / 'version'
            manifest.write_text('0=script:%s:3\nscript=1 %s:%s\n' % (
                hashlib.md5(payload.read_bytes()).hexdigest(),
                hashlib.md5(check.read_bytes()).hexdigest(), check.stat().st_size))
            baseline = root / 'base.npk'
            # Native preamble is also retained verbatim. The manifest's module
            # supersedes the old version while an APK-only bootstrap survives.
            baseline.write_bytes(struct.pack('<4s5I', b'NXPK', 2, 0, 0, 2, 36)
                                 + b'BOOT' + b'OLDRDRCT'
                                 + struct.pack('<7I', 42, 28, 3, 3, 11, 12, 0)
                                 + struct.pack('<7I', 0xfb54f059, 31, 5, 5, 21, 22, 0))
            output = root / 'script.npk'
            rebuild(root, 'android', 640, 'script', manifest, output, baseline)
            data = output.read_bytes()
            self.assertEqual(data[24:28], b'BOOT')
            header = struct.unpack_from('<4s5I', data)
            self.assertEqual(header[1], 2)
            records = [struct.unpack_from('<7I', data, header[-1] + 28 * i) for i in range(2)]
            actual = {row[0]: data[row[1]:row[1] + row[2]] for row in records}
            self.assertEqual(actual, {42: b'NEW', 0xfb54f059: b'RDRCT'})
            self.assertEqual(records[1][4:6], (21, 22))

    def test_rebuild_uses_checked_offsets_and_preserves_packed_bytes(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = root / "patch2.ios.640/0/script.data"
            source.parent.mkdir(parents=True)
            source.write_bytes(b"skipABC")
            check = root / "patch2.ios.640/script.check"
            check.write_bytes(zlib.compress(b"42 00000000000000000000000000000000 3 1 3 1 0 4\n"))
            manifest = root / "version"
            manifest.write_text(f"0=script:{hashlib.md5(source.read_bytes()).hexdigest()}:7\n"
                                f"script=1 {hashlib.md5(check.read_bytes()).hexdigest()}:{check.stat().st_size}\n")
            output = root / "script.npk"
            rebuild(root, "ios", 640, "script", manifest, output)
            data = output.read_bytes()
            header = struct.unpack_from("<4s6I", data)
            self.assertEqual(header, (b"NXPK", 1, 0, 0, 2, 32, 0))
            self.assertEqual(data[28:31], b"ABC")
            self.assertEqual(struct.unpack_from("<7I", data, 32), (42, 28, 3, 3, 1, 1, 0))
            source.write_bytes(b"skipBAD")
            with self.assertRaisesRegex(ValueError, "MD5 mismatch"):
                rebuild(root, "ios", 640, "script", manifest, root / "bad.npk")
            self.assertFalse((root / "bad.npk.part").exists())


class IpaTests(unittest.TestCase):
    @staticmethod
    def binary(cryptid):
        header = struct.pack("<8I", 0xFEEDFACF, 0x100000C, 0, 2, 1, 24, 0, 0)
        return header + struct.pack("<6I", 0x2C, 24, 4096, 2048, cryptid, 0)

    def test_detects_encrypted_and_unencrypted_executables(self):
        for cryptid in (0, 1):
            self.assertEqual(macho_slices(self.binary(cryptid))[0]["encrypted"], bool(cryptid))

    def test_ipa_inventory_does_not_claim_runtime_compatibility(self):
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "fixture.ipa"
            with zipfile.ZipFile(path, "w") as archive:
                archive.writestr("Payload/Game.app/Info.plist", plistlib.dumps({
                    "CFBundleIdentifier": "test.fixture", "CFBundleExecutable": "Game",
                    "CFBundleShortVersionString": "1.0", "CFBundleVersion": "1"}))
                archive.writestr("Payload/Game.app/Game", self.binary(1))
            result = inspect(path, check_crc=True)
            self.assertTrue(result["executable_encrypted"])
            self.assertTrue(result["zip_crc_verified"])
            self.assertFalse(result["runtime_tested"])


class DataTableTests(unittest.TestCase):
    def test_reads_generator_aliases_and_tagged_dict_without_imports(self):
        with tempfile.TemporaryDirectory() as temporary:
            source = Path(temporary) / 'table.py'
            source.write_text("import module_that_does_not_exist\nl0 = ((1000,), set([1, 2]))\n"
                              "data = {1000: TD({'dialog': l0[0], 'mutex': l0[1], 'offset': -2})}\n")
            self.assertEqual(read_table(source), {1000: {'dialog': (1000,), 'mutex': {1, 2}, 'offset': -2}})

    def test_rejects_executable_expression_without_creating_its_target(self):
        with tempfile.TemporaryDirectory() as temporary:
            source, marker = [Path(temporary) / name for name in ('table.py', 'marker')]
            source.write_text("data = __import__('pathlib').Path(%r).write_text('executed')\n" % str(marker))
            with self.assertRaisesRegex(ValueError, 'Unsupported expression'):
                read_table(source)
            self.assertFalse(marker.exists())


class PrivateUpdateTests(unittest.TestCase):
    def test_delta_check_order_supports_native_release_batch_reader(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            original = root / 'cdn/patch2.ios.640'
            (original / '0').mkdir(parents=True)
            payload = original / '0/script.data'
            payload.write_bytes(b'OLD')
            check = original / 'script.check'
            check.write_bytes(zlib.compress(b'2897852430 00000000000000000000000000000000 3 1 3 1 0 0\n'))
            manifest = root / 'patch2.ios.640.version'
            manifest.write_text('0=script:%s:3\nscript=1 %s:%s\n' % (
                hashlib.md5(payload.read_bytes()).hexdigest(), hashlib.md5(check.read_bytes()).hexdigest(), check.stat().st_size))

            def archive(path, init):
                values = [(0x3e9933a5, b'BOOK'), (0xacb9b80e, init), (0xfb54f059, b'BOOT')]
                data, records = bytearray(b'\0' * 28), []
                for fid, value in values:
                    records.append((fid, len(data), len(value), len(value), 1, 1, 0))
                    data.extend(value)
                table = len(data)
                for row in records:
                    data.extend(struct.pack('<7I', *row))
                data[:24] = struct.pack('<4s5I', b'NXPK', len(records), 0, 0, 2, table)
                path.write_bytes(data)

            before, after = root / 'before.npk', root / 'after.npk'
            archive(before, b'OLD')
            archive(after, b'PATCHED')
            destination = root / 'update'
            build_update('ios', manifest, root / 'cdn', before, after, 641, destination)
            new = destination / 'patch2.ios.641'
            data = (new / '641/script.data').read_bytes()
            rows = [line.split() for line in zlib.decompress((new / 'script.check').read_bytes()).decode().splitlines()]
            # The native release reader consumes concatenated chunks in row
            # order and may ignore offsets. An extra before init catches the
            # tempting but invalid append-only modification of script.check.
            cursor, recovered = 0, {}
            for row in rows:
                self.assertEqual(row[6], '641')
                self.assertEqual(int(row[7]), cursor)
                size = int(row[2])
                recovered[int(row[0])] = data[cursor:cursor + size]
                cursor += size
            self.assertEqual(cursor, len(data))
            self.assertEqual(recovered, {0x3e9933a5: b'BOOK', 0xacb9b80e: b'PATCHED', 0xfb54f059: b'BOOT'})


class MirrorTests(unittest.TestCase):
    def test_byte_ranges(self):
        self.assertEqual(byte_range("bytes=-3", 10), (7, 9, True))
        self.assertEqual(byte_range("bytes=4-99", 10), (4, 9, True))
        for value in ("bytes=10-", "bytes=6-3", "bytes=-0", "bytes=0-1,4-5"):
            with self.assertRaises(ValueError):
                byte_range(value, 10)

    def test_real_http_partial_head_and_unknown_login(self):
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "payload"
            path.write_bytes(b"0123456789")
            handler = make_handler({"/patch2.ios.640/0/script.data": path,
                                    "/patch2.ios.640/version": path})
            handler.log_message = lambda *args: None
            server = ThreadingHTTPServer(("127.0.0.1", 0), handler)
            thread = threading.Thread(target=server.serve_forever, daemon=True)
            thread.start()
            base = f"http://127.0.0.1:{server.server_port}"
            try:
                request = urllib.request.Request(base + "/patch2.ios.640/0/script.data", headers={"Range": "bytes=2-5"})
                with urllib.request.urlopen(request) as response:
                    self.assertEqual(response.status, 206)
                    self.assertEqual(response.headers["Content-Range"], "bytes 2-5/10")
                    self.assertEqual(response.read(), b"2345")
                with urllib.request.urlopen(urllib.request.Request(base + "/patch2.ios.640/0/script.data", method="HEAD")) as response:
                    self.assertEqual(response.headers["Content-Length"], "10")
                    self.assertEqual(response.read(), b"")
                with urllib.request.urlopen(urllib.request.Request(base + '/patch2.ios.640', method='HEAD')) as response:
                    self.assertEqual(response.status, 200)
                    self.assertEqual(response.read(), b'')
                for route in ("/login", "/../requirements.txt", "/%2e%2e/requirements.txt"):
                    with self.assertRaises(urllib.error.HTTPError) as error:
                        urllib.request.urlopen(base + route)
                    self.assertEqual(error.exception.code, 404)
                with urllib.request.urlopen(base + "/_offline/status") as response:
                    self.assertFalse(json.load(response)["game_gateway_implemented"])
            finally:
                server.shutdown()
                thread.join()
                server.server_close()


if __name__ == "__main__":
    unittest.main()
