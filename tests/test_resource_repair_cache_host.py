"""Run cache repair regression against production Java, without D8 or Android."""
import _paths  # noqa: E402,F401
from pathlib import Path
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
JAVA = ROOT / 'toolchains/java/jdk-17.0.21+9/Contents/Home/bin'
BASE = ROOT / 'offline/current/java/android_resource_init'


@unittest.skipUnless((JAVA / 'javac').is_file() and (JAVA / 'java').is_file(),
                     'Host JDK required')
class ResourceRepairCacheHostTests(unittest.TestCase):
    def test_corrupt_metadata_cache_is_invalidated_before_zip_repair(self):
        sources = [BASE / 'src/com/forever7/offline/ResourceImporter.java',
                   BASE / 'tests/ResourceImporterHostTest.java',
                   BASE / 'tests/ResourceRepairCacheHostTest.java']
        with tempfile.TemporaryDirectory(prefix='f7-repair-regression-') as output:
            compile_result = subprocess.run(
                [str(JAVA / 'javac'), '-source', '8', '-target', '8',
                 '-Xlint:-options', '-d', output, *map(str, sources)],
                capture_output=True, text=True, timeout=60)
            self.assertEqual(compile_result.returncode, 0, compile_result.stderr)
            result = subprocess.run(
                [str(JAVA / 'java'), '-cp', output, 'ResourceRepairCacheHostTest'],
                capture_output=True, text=True, timeout=30)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn('PASS stale-cache corruption -> invalidation -> new-session ZIP repair',
                          result.stdout)
            self.assertIn('PASS Activity-order importZip(force=true) replaces same-metadata bad disk in one import',
                          result.stdout)


if __name__ == '__main__':
    unittest.main()
