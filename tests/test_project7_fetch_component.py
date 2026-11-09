import _paths  # noqa: E402,F401
import hashlib
import io
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import project7_fetch_component as component


class ComponentCacheTests(unittest.TestCase):
    def test_corrupt_cache_repaired_from_offline_input(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source, cache = root / 'input.zip', root / 'cache' / 'component.zip'
            data = b'verified component'
            source.write_bytes(data)
            cache.parent.mkdir()
            cache.write_bytes(b'corrupt')
            with patch.object(component, 'CACHE', cache), patch.object(component, 'expected', return_value=(hashlib.sha256(data).hexdigest(), len(data))):
                self.assertEqual(component.resolve(offline_input=source).read_bytes(), data)
            self.assertEqual(list(cache.parent.iterdir()), [cache])

    def test_small_download_flushed_and_failed_download_preserves_cache(self):
        with tempfile.TemporaryDirectory() as directory:
            cache = Path(directory) / 'component.zip'
            data = b'small verified payload'
            with patch.object(component, 'CACHE', cache), patch.object(component, 'expected', return_value=(hashlib.sha256(data).hexdigest(), len(data))):
                with patch.object(component.urllib.request, 'urlopen', return_value=io.BytesIO(data)):
                    component.resolve(url='https://example.invalid/component')
                self.assertEqual(cache.read_bytes(), data)
                cache.write_bytes(b'old corrupt cache')
                with patch.object(component.urllib.request, 'urlopen', return_value=io.BytesIO(b'wrong')):
                    with self.assertRaises(ValueError):
                        component.resolve(url='https://example.invalid/component')
                self.assertEqual(cache.read_bytes(), b'old corrupt cache')
                self.assertEqual(list(cache.parent.iterdir()), [cache])


if __name__ == '__main__':
    unittest.main()
