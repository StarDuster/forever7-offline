from pathlib import Path
import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from android_resource_init import compile_resource_initializer, patch_resource_manifest, ENTRY, ORIGINAL

class AndroidResourceInitTests(unittest.TestCase):
    def test_bundled_allowlist_is_exact_preserved_manifest_excludes_code_and_saves(self):
        spec = json.loads((ROOT / 'reports/single-app-resource-initializer-spec.json').read_text())['resource_manifest']
        manifest = json.loads((ROOT / 'runtime/android_resource_init/resource_manifest.json').read_text())
        self.assertEqual(manifest['entries'][:36], spec['entries'])
        self.assertEqual(len(manifest['entries']), 312)
        plan = json.loads((ROOT / 'reports/official-asset-source-plan.json').read_text())
        self.assertEqual(manifest['entries'][36:], [dict(name=e['path'][4:], bytes=e['size'], sha256=e['sha256']) for e in plan['raw_files']])
        self.assertIn('sound/output/object.fsb', {e['name'] for e in manifest['entries']})
        self.assertFalse(any(e['name'].startswith('res/') for e in manifest['entries']))
        self.assertEqual(sum(e['bytes'] for e in manifest['entries']), 8010923732)
        self.assertEqual(manifest['files'], len(manifest['entries']))
        self.assertEqual(manifest['bytes'], sum(e['bytes'] for e in manifest['entries']))
        self.assertNotIn('script.npk', {e['name'] for e in manifest['entries']})

    def test_original_binary_manifest_preserves_permissions_and_moves_unique_launcher(self):
        from loguru import logger
        logger.disable('androguard')
        from androguard.core.axml import AXMLPrinter
        source = (ROOT / 'analysis/project7/merge/hook-main-decoded/AndroidManifest.xml').read_bytes()
        before = AXMLPrinter(source).get_xml_obj()
        after = AXMLPrinter(patch_resource_manifest(source)).get_xml_obj()
        ns = '{http://schemas.android.com/apk/res/android}'
        self.assertEqual([e.attrib for e in before.findall('uses-permission')], [e.attrib for e in after.findall('uses-permission')])
        launchers = [a.get(ns + 'name') for a in after.find('application').findall('activity')
            for f in a.findall('intent-filter') if any(x.get(ns+'name') == 'android.intent.action.MAIN' for x in f.findall('action'))]
        self.assertEqual(launchers, [ENTRY])
        stock = [a for a in after.find('application').findall('activity') if a.get(ns+'name') == ORIGINAL][0]
        self.assertEqual(stock.findall('intent-filter'), [])
        self.assertNotEqual(stock.get(ns+'exported'), 'true')
        with self.assertRaises(ValueError): patch_resource_manifest(patch_resource_manifest(source))

    def test_compile_android32_dex_and_host_import_cancel_recreation_contracts(self):
        java = ROOT / 'toolchains/java/jdk-17.0.21+9/Contents/Home/bin'
        source = ROOT / 'runtime/android_resource_init'
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)
            dex, manifest = compile_resource_initializer(ROOT, ROOT / 'toolchains', output)
            self.assertTrue(dex.read_bytes().startswith(b'dex\n'))
            subprocess.run([str(java/'javac'), '-source', '8', '-target', '8', '-Xlint:-options',
                '-cp', str(output/'resource-init-classes'), '-d', str(output/'resource-init-classes'),
                str(source/'tests/ResourceImporterHostTest.java'), str(source/'tests/OfficialResourcesHostTest.java'),
                str(source/'tests/OfficialResourcesRedirectHostTest.java')], check=True, capture_output=True)
            result = subprocess.run([str(java/'java'), '-cp', str(output/'resource-init-classes'),
                'ResourceImporterHostTest'], check=True, capture_output=True, text=True, timeout=20)
            self.assertIn('10 resource import contracts passed', result.stdout)
            official = subprocess.run([str(java/'java'), '-cp', str(output/'resource-init-classes'), 'OfficialResourcesHostTest'], check=True, capture_output=True, text=True, timeout=20)
            self.assertIn('4 official cache/reconstruction/retry/cancellation contracts passed', official.stdout)
            redirects = subprocess.run([str(java/'java'), '-cp', str(output/'resource-init-classes'), 'OfficialResourcesRedirectHostTest'], check=True, capture_output=True, text=True, timeout=20)
            self.assertIn('16 real production redirect/fallback/hash/cancellation contracts passed; network=mock-only', redirects.stdout)

if __name__ == '__main__': unittest.main()
