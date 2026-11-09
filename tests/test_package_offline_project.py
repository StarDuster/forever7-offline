"""Boundary tests for the local dependency-ready source bundle."""
import _paths  # noqa: E402,F401
import hashlib
import json
import subprocess
import sys
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import zipfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'offline' / 'current' / 'tools'))
COMPONENT = ROOT / 'vendor/project7/component-v2.10.1.zip'


@unittest.skipUnless(COMPONENT.is_file(), 'local pinned component unavailable')
class OfflineBundleTests(unittest.TestCase):
    def test_concurrent_output_is_preserved_and_own_failed_bundle_is_removed(self):
        import package_offline_project
        with tempfile.TemporaryDirectory(prefix='p7-bundle-race-') as temporary:
            temporary = Path(temporary)
            output = temporary / 'concurrent.zip'
            original_export = package_offline_project.export_source

            def export_then_create_output(source):
                original_export(source)
                output.write_bytes(b'other-build-output')

            with patch.object(package_offline_project, 'export_source',
                              side_effect=export_then_create_output):
                with self.assertRaises(FileExistsError):
                    package_offline_project.package(COMPONENT, output)
            self.assertEqual(output.read_bytes(), b'other-build-output')

            failed = temporary / 'failed.zip'
            original_write = zipfile.ZipFile.writestr

            def fail_bundle_write(archive, *args, **kwargs):
                if Path(archive.filename) == failed:
                    raise OSError('simulated bundle write failure')
                return original_write(archive, *args, **kwargs)

            with patch.object(zipfile.ZipFile, 'writestr', fail_bundle_write):
                with self.assertRaisesRegex(OSError, 'simulated bundle write failure'):
                    package_offline_project.package(COMPONENT, failed)
            self.assertFalse(failed.exists())

    def test_component_pin_rejection_and_source_inventory_separation(self):
        import package_offline_project
        with tempfile.TemporaryDirectory(prefix='p7-bundle-test-') as temporary:
            temporary = Path(temporary)
            bad = temporary / 'bad.zip'
            bad.write_bytes(b'not the component')
            with self.assertRaisesRegex(ValueError, 'Component offline input'):
                package_offline_project.package(bad, temporary / 'bad-bundle.zip')
            self.assertFalse((temporary / 'bad-bundle.zip').exists(),
                             'bad component must not leave an output')
            output = temporary / 'bundle.zip'
            result = package_offline_project.package(COMPONENT, output)
            self.assertTrue(output.is_file())
            self.assertEqual(result['component_sha256'], package_offline_project._component_pin()[0])
            with zipfile.ZipFile(output) as bundle:
                names = set(bundle.namelist())
                prefix = 'forever7-offline-project/'
                inventory = json.loads(bundle.read(prefix + 'EXPORT-INVENTORY.json'))
                self.assertNotIn('vendor/project7/component-v2.10.1.zip',
                                 {row['path'] for row in inventory})
                self.assertIn(prefix + '.offline-deps/component-v2.10.1.zip', names)
                self.assertIn(prefix + 'DEPENDENCY-INVENTORY.json', names)
                self.assertIn(prefix + 'BUNDLE-INVENTORY.json', names)
                dependency = json.loads(bundle.read(prefix + 'DEPENDENCY-INVENTORY.json'))
                self.assertEqual(dependency['component']['sha256'],
                                 hashlib.sha256(COMPONENT.read_bytes()).hexdigest())
            unpacked = temporary / 'unpacked'
            with zipfile.ZipFile(output) as bundle:
                bundle.extractall(unpacked)
            project = unpacked / 'forever7-offline-project'
            cached = project / '.offline-deps/component-v2.10.1.zip'
            self.assertEqual(hashlib.sha256(cached.read_bytes()).hexdigest(),
                             hashlib.sha256(COMPONENT.read_bytes()).hexdigest())
            resolved = subprocess.run(
                [sys.executable, 'project7_bridge/tools/project7_fetch_component.py'],
                cwd=project, capture_output=True, text=True, timeout=60)
            self.assertEqual(resolved.returncode, 0, resolved.stderr)
            self.assertIn(str(cached.resolve()), resolved.stdout)
            preflight = subprocess.run(
                [sys.executable, 'tools/build_offline_project.py', '--help'],
                cwd=project, capture_output=True, text=True, timeout=60)
            self.assertEqual(preflight.returncode, 0, preflight.stderr)


if __name__ == '__main__':
    unittest.main()
