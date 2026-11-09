import hashlib
import json
from pathlib import Path
import re
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'runtime'))
from offline_store import OfflineSaveError, OfflineSaveStore


def validate(payload):
    if not isinstance(payload, dict) or not isinstance(payload.get('completed'), list):
        raise ValueError('Invalid progress')


class OfflineStoreTests(unittest.TestCase):
    @staticmethod
    def native_envelope(payload_token, **fields):
        # Independent tokenizer to simulate the native writer's compact input.
        compact = re.sub(r'"(?:\\.|[^"\\])*"|[ \t\r\n]+',
                         lambda match: match.group(0) if match.group(0).startswith('"') else '',
                         payload_token)
        digest = hashlib.sha256(compact.encode('ascii')).hexdigest()
        metadata = {'format': 1, 'revision': 7, 'sha256': digest}
        metadata.update(fields)
        return ('{' + ','.join(json.dumps(key) + ':' + json.dumps(value)
                              for key, value in sorted(metadata.items())) +
                ',"payload":' + payload_token + '}').encode('ascii')

    def test_native_float_spelling_survives_reload_write_and_backup(self):
        # Actual embedded encoder spelling observed in the native save.
        token = '{"completed": [1000], "ratio": 0.59999999999999998}'
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'progress.json'
            original = self.native_envelope(token)
            path.write_bytes(original)
            store = OfflineSaveStore(str(path), validate)
            payload = store.load()
            self.assertEqual(payload, {'completed': [1000], 'ratio': 0.6})
            self.assertEqual(store.revision, 7)
            self.assertEqual(path.read_bytes(), original)
            payload['completed'].append(1001)
            store.write(payload)
            self.assertEqual(Path(str(path) + '.previous').read_bytes(), original)
            self.assertEqual(OfflineSaveStore(str(path), validate).load(), payload)
            path.write_bytes(b'{truncated')
            restored = OfflineSaveStore(str(path), validate)
            self.assertEqual(restored.load()['completed'], [1000])
            self.assertTrue(restored.recovered)

    def test_exact_raw_payload_hash_rejects_tampering_and_invalid_schema(self):
        good = self.native_envelope(
            '{"completed": [1000], "ratio": 0.59999999999999998}')
        store = OfflineSaveStore('unused', validate)
        for raw in (good.replace(b'1000', b'9999'),
                    good.replace(b'0.59999999999999998', b'0.7'),
                    self.native_envelope('{"completed": 1000, "ratio": 0.59999999999999998}'),
                    self.native_envelope('{"completed": [], "ratio": NaN}')):
            with self.subTest(raw=raw):
                with self.assertRaises((OfflineSaveError, ValueError)):
                    store._decode(raw)

    def test_payload_extraction_uses_top_level_field_and_preserves_strings(self):
        value = {'completed': [1000], 'ratio': 0.6,
                 'text': 'payload \\" a b\t\n \\ end',
                 'payload': {'payload': ' keep spaces '}}
        token = json.dumps(value, sort_keys=True, indent=2).replace(
            '0.6,', '0.59999999999999998,')
        # Metadata deliberately includes an earlier nested/string payload key.
        raw = self.native_envelope(token, note={'payload': 'irrelevant'},
                                   label='"payload": {ignored}')
        self.assertEqual(OfflineSaveStore('unused', validate)._decode(raw), (7, value))
        compact = OfflineSaveStore._raw_payload_bytes(raw.decode('ascii'))
        self.assertIn(b'0.59999999999999998', compact)
        self.assertEqual(json.loads(compact), value)

    def test_noncanonical_fallback_rejects_duplicate_envelope_fields(self):
        good = self.native_envelope(
            '{"completed": [1000], "ratio": 0.59999999999999998}')
        for extra in (b'"payload":{"completed":[]},', b'"revision":2,',
                      b'"sha256":"unused",'):
            with self.subTest(extra=extra):
                with self.assertRaises(OfflineSaveError):
                    OfflineSaveStore('unused', validate)._decode(b'{' + extra + good[1:])

    def test_noncanonical_fallback_keeps_format_and_size_guards(self):
        store = OfflineSaveStore('unused', validate)
        token = '{"completed": [], "ratio": 0.59999999999999998}'
        with self.assertRaises(OfflineSaveError):
            store._decode(self.native_envelope(token, format=2))
        for revision in (True, 0, -1, 1.5):
            with self.subTest(revision=revision):
                with self.assertRaises(OfflineSaveError):
                    store._decode(self.native_envelope(token, revision=revision))
        with patch.object(store, 'MAX_BYTES', 10):
            with self.assertRaises(OfflineSaveError):
                store._decode(self.native_envelope(token))

    def test_restart_recovers_saved_progress_without_repeating_event(self):
        with tempfile.TemporaryDirectory() as folder:
            path = str(Path(folder) / 'progress.json')
            first = OfflineSaveStore(path, validate)
            self.assertIsNone(first.load())
            first.write({'completed': [1000], 'name': '\u79bb\u7ebf'})
            second = OfflineSaveStore(path, validate)
            self.assertEqual(second.load(), {'completed': [1000], 'name': '\u79bb\u7ebf'})
            self.assertEqual(second.revision, 1)
            self.assertFalse(second.recovered)

    def test_interrupted_primary_save_leaves_previous_revision_readable(self):
        with tempfile.TemporaryDirectory() as folder:
            path = str(Path(folder) / 'progress.json')
            store = OfflineSaveStore(path, validate)
            store.write({'completed': [1000]})
            original = store._atomic_write

            def fail_primary(destination, raw):
                if destination == path:
                    raise OSError('Simulated disk full')
                original(destination, raw)

            with patch.object(store, '_atomic_write', side_effect=fail_primary):
                with self.assertRaises(OSError):
                    store.write({'completed': [1000, 1001]})
            self.assertEqual(store.revision, 1)
            self.assertEqual(OfflineSaveStore(path, validate).load(), {'completed': [1000]})

    def test_corrupt_primary_uses_last_good_and_does_not_overwrite_backup_with_corruption(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'progress.json'
            store = OfflineSaveStore(str(path), validate)
            store.write({'completed': [1000]})
            store.write({'completed': [1000, 1001]})
            path.write_text('{truncated')
            recovered = OfflineSaveStore(str(path), validate)
            self.assertEqual(recovered.load(), {'completed': [1000]})
            self.assertTrue(recovered.recovered)
            recovered.write({'completed': [1000, 1002]})
            path.write_text('{broken again')
            self.assertEqual(OfflineSaveStore(str(path), validate).load(), {'completed': [1000]})

    def test_corrupt_or_unknown_format_never_silently_resets_progress(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'progress.json'
            store = OfflineSaveStore(str(path), validate)
            store.write({'completed': [1000]})
            store.write({'completed': [1000, 1001]})
            envelope = json.loads(path.read_bytes())
            envelope['format'] = 99
            path.write_text(json.dumps(envelope))
            with self.assertRaises(OfflineSaveError):
                OfflineSaveStore(str(path), validate).load()
            self.assertEqual(json.loads(path.read_text())['format'], 99)

    def test_large_legitimate_history_roundtrip_and_oversize_write_preserves_original(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'progress.json'
            store = OfflineSaveStore(str(path), validate)
            old_format = {'completed': [1000], 'week_history': 'x' * (1024 * 1024 + 100)}
            store.write(old_format)
            self.assertGreater(path.stat().st_size, 1024 * 1024)
            self.assertEqual(OfflineSaveStore(str(path), validate).load(), old_format)
            original = path.read_bytes()
            with self.assertRaises(OfflineSaveError):
                store.write({'completed': [1000, 1001], 'week_history': 'x' * OfflineSaveStore.MAX_BYTES})
            self.assertEqual(path.read_bytes(), original)
            self.assertEqual(OfflineSaveStore(str(path), validate).load(), old_format)
            self.assertEqual(store.revision, 1)

    def test_tampered_progress_fails_checksum(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'progress.json'
            store = OfflineSaveStore(str(path), validate)
            store.write({'completed': [1000]})
            envelope = json.loads(path.read_bytes())
            envelope['payload']['completed'].append(9999)
            path.write_text(json.dumps(envelope))
            with self.assertRaises(OfflineSaveError):
                OfflineSaveStore(str(path), validate).load()


if __name__ == '__main__':
    unittest.main()
