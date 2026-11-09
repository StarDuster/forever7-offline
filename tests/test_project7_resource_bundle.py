from pathlib import Path
import hashlib
import json
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from project7_resource_bundle import (BINDING_ASSET, DATA, SNAPSHOT_ASSET, SNAPSHOT_SHA,
                                      SNAPSHOT_SIZE, create_bundle, fixed_snapshot)
from project7_component import npk, overlay


class Project7ResourceBundleTests(unittest.TestCase):
    def test_fixed_project_metadata_requires_no_analysis_files(self):
        raw, binding = fixed_snapshot((DATA / 'project7-resource-snapshot.json.gz').read_bytes(),
                                      (DATA / 'project7-resource-binding.json').read_bytes())
        self.assertEqual(len(raw), SNAPSHOT_SIZE)
        self.assertEqual(hashlib.sha256(raw).hexdigest(), SNAPSHOT_SHA)
        snapshot = json.loads(raw)
        self.assertEqual(set(snapshot), {'schema', 'version', 'platform', 'parts', 'packs', 'manifest'})
        self.assertEqual((snapshot['version'], snapshot['platform']), (455, 'android'))
        self.assertEqual(binding['entryCount'], 312)

    def test_tampered_compressed_metadata_or_binding_is_rejected(self):
        packed = (DATA / 'project7-resource-snapshot.json.gz').read_bytes()
        binding = (DATA / 'project7-resource-binding.json').read_bytes()
        for p, b in [(packed[:-1] + bytes([packed[-1] ^ 1]), binding),
                     (packed, binding + b'\n')]:
            with self.assertRaisesRegex(ValueError, 'pin mismatch'):
                fixed_snapshot(p, b)

    def test_script_binding_generated_java_matches_real_publisher_api(self):
        stage = ROOT / 'analysis/project7/official-build-inputs-v1'
        if not stage.is_dir():
            self.skipTest('Maintainer materialized supported inputs absent')
        base = (stage / 'assets/script.npk').read_bytes()
        local = (stage / 'assets/project7_local.npk').read_bytes()
        files, source, binding = create_bundle(base, local)
        self.assertEqual(files['assets/' + SNAPSHOT_ASSET],
                         fixed_snapshot((DATA / 'project7-resource-snapshot.json.gz').read_bytes(),
                                        (DATA / 'project7-resource-binding.json').read_bytes())[0])
        raw_binding = files['assets/' + BINDING_ASSET]
        self.assertEqual(json.loads(raw_binding), binding)
        self.assertIn(hashlib.sha256(raw_binding).hexdigest().encode(), source)
        self.assertIn(hashlib.sha256(local).hexdigest().encode(), source)
        directory = ROOT / 'runtime/android_resource_init/src/com/forever7/offline'
        javac = ROOT / 'toolchains/java/jdk-17.0.21+9/Contents/Home/bin/javac'
        if javac.is_file():
            with tempfile.TemporaryDirectory() as temporary:
                temporary = Path(temporary)
                generated = temporary / 'Project7BundledResources.java'
                generated.write_bytes(source)
                result = subprocess.run([str(javac), '-source', '8', '-target', '8',
                                         '-Xlint:-options', '-d', str(temporary), str(generated),
                                         str(directory / 'ResourceImporter.java'),
                                         str(directory / 'Project7ResourceSnapshot.java')],
                                        capture_output=True, text=True)
                self.assertEqual(result.returncode, 0, result.stderr)
        rows = list(npk(local).values())
        row, payload = rows[0]
        rows[0] = (row, payload[:-1] + bytes([payload[-1] ^ 1]))
        changed = overlay(rows)
        _, changed_source, changed_binding = create_bundle(base, changed)
        self.assertNotEqual(changed_binding['scripts'][1]['sha256'], binding['scripts'][1]['sha256'])
        self.assertNotEqual(changed_source, source)
        with self.assertRaisesRegex(ValueError, 'baseline'):
            create_bundle(base + b'\0', local)


if __name__ == '__main__':
    unittest.main()
