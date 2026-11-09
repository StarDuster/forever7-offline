import _paths  # noqa: E402,F401
from pathlib import Path
import sys
import tempfile
import unittest
import zipfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'project7_bridge' / 'tools'))
from project7_build_inputs import patch_manifest, prepare, validate_loader
from android_resource_init import patch_resource_manifest


class Project7BuildInputTests(unittest.TestCase):
    def test_loader_preserves_asset_priority_and_refuses_document_override(self):
        def xml(loaders):
            return ('<ppg3d><filesystems><filesystem name="script">' + loaders +
                    '</filesystem></filesystems></ppg3d>').encode()
        local = '<loader name="npk" opener="asset" root="project7_local" />'
        base = '<loader name="npk" opener="asset" root="script" />'
        self.assertEqual([row['root'] for row in validate_loader(xml(local + base))],
                         ['project7_local', 'script'])
        for invalid in (base + local, local + base + '<loader opener="os" root="%DOC_DIR%" />',
                        local.replace('asset', 'os') + base):
            with self.assertRaises(ValueError):
                validate_loader(xml(invalid))

    def test_original_manifest_platform_and_launcher_are_consumable_by_independent_parser(self):
        path = ROOT / 'originals/forever7-netease-83.apk'
        if not path.is_file():
            self.skipTest('Supported original APK not supplied')
        from loguru import logger
        logger.disable('androguard')
        from androguard.core.axml import AXMLPrinter
        with zipfile.ZipFile(path) as apk:
            data = apk.read('AndroidManifest.xml')
        before = AXMLPrinter(data).get_xml_obj()
        after = AXMLPrinter(patch_manifest(data)).get_xml_obj()
        ns = '{http://schemas.android.com/apk/res/android}'
        self.assertEqual(after.find('uses-sdk').get(ns + 'minSdkVersion'), '26')
        self.assertEqual(before.find('uses-sdk').get(ns + 'targetSdkVersion'),
                         after.find('uses-sdk').get(ns + 'targetSdkVersion'))
        self.assertEqual([dict(x.attrib) for x in before.findall('uses-permission')],
                         [dict(x.attrib) for x in after.findall('uses-permission')])
        launchers = [activity.get(ns + 'name') for activity in after.find('application').findall('activity')
                     for intent in activity.findall('intent-filter')
                     if any(action.get(ns + 'name') == 'android.intent.action.MAIN'
                            for action in intent.findall('action'))]
        self.assertEqual(launchers, ['com.forever7.offline.Project7ResourceInitActivity'])
        stock = next(activity for activity in after.find('application').findall('activity')
                     if activity.get(ns + 'name') == 'com.netease.qrzd.Client')
        self.assertNotEqual(stock.get(ns + 'exported'), 'true')
        self.assertFalse(stock.findall('intent-filter'))
        with self.assertRaises(ValueError):
            patch_manifest(patch_manifest(data))
        legacy = AXMLPrinter(patch_resource_manifest(data)).get_xml_obj()
        self.assertEqual(legacy.find('uses-sdk').get(ns + 'minSdkVersion'),
                         before.find('uses-sdk').get(ns + 'minSdkVersion'))
        legacy_launchers = [activity.get(ns + 'name') for activity in legacy.find('application').findall('activity')
                           for intent in activity.findall('intent-filter')
                           if any(action.get(ns + 'name') == 'android.intent.action.MAIN'
                                  for action in intent.findall('action'))]
        self.assertEqual(legacy_launchers, ['com.forever7.offline.ResourceInitActivity'])
        with self.assertRaises(ValueError):
            patch_manifest(patch_resource_manifest(data))

    def test_refuses_existing_stage_without_touching_its_contents(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / 'existing'
            target.mkdir()
            sentinel = target / 'sentinel'
            sentinel.write_bytes(b'keep this stage')
            with self.assertRaisesRegex(ValueError, 'already exists'):
                prepare(Path('not-read.apk'), Path('not-read.npk'), target)
            self.assertEqual(sentinel.read_bytes(), b'keep this stage')


if __name__ == '__main__':
    unittest.main()
