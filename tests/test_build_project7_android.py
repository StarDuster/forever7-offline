"""Pure helpers only. Never call build, D8, APK assembler, signer or device."""
from pathlib import Path
import hashlib
import io
import json
import os
import struct
import sys
import tempfile
import unittest
from unittest import mock
import warnings
import zipfile

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
import build_project7_android as module


def fixture_class(name):
    raw=name.encode('ascii')
    # Identity-only invalid-to-execute fixture. No executable method bodies.
    return b'\xca\xfe\xba\xbe'+struct.pack('>HHH',0,52,3)+b'\x01'+struct.pack('>H',len(raw))+raw+b'\x07\x00\x01'+struct.pack('>HHH',1,2,0)


class HelperTests(unittest.TestCase):
    def test_member_paths(self):
        for name in ('assets/script.npk','classes6.dex','META-INF/CERT.RSA'):
            self.assertEqual(module.safe_name(name),name)
        for name in ('','/x','../x','a/../x','a//x','a/./x','a\\x','x\0y'):
            with self.assertRaises(ValueError):module.safe_name(name)

    def test_signature_scope(self):
        for name in ('META-INF/MANIFEST.MF','meta-inf/cert.sf','META-INF/CERT.RSA','META-INF/SIG-CUSTOM'):
            self.assertTrue(module.is_signature(name))
        for name in ('assets/CERT.RSA','META-INF/services/a','META-INF/license.txt','META-INF/nested/CERT.RSA'):
            self.assertFalse(module.is_signature(name))

    def test_class_identity(self):
        name='com/project7/localmanager/CoreGapBridge$Access'
        self.assertEqual(module.class_name(fixture_class(name)),name)
        self.assertEqual(module.family('L'+name+';'),'Lcom/project7/localmanager/CoreGapBridge;')
        for data in (b'not java',fixture_class(name)[:-1],fixture_class('../escape')):
            with self.assertRaises(ValueError):module.class_name(data)
        raw=bytearray(fixture_class(name));raw[-4:-2]=b'\0\1'
        with self.assertRaises(ValueError):module.class_name(bytes(raw))

    def test_duplicate_zip_reader_and_payload_inventory(self):
        # Tiny generic ZIP fixtures in memory; no APK layout or APK assembly.
        memory=io.BytesIO()
        with zipfile.ZipFile(memory,'w') as archive:
            archive.writestr('payload.txt',b'fixed payload')
            archive.writestr('META-INF/CERT.SF',b'obsolete signature')
        with zipfile.ZipFile(io.BytesIO(memory.getvalue())) as archive:
            rows=module.zip_inventory(archive,True)
        self.assertEqual(rows,{'payload.txt':{'bytes':13,'sha256':hashlib.sha256(b'fixed payload').hexdigest()}})
        duplicate=io.BytesIO()
        with warnings.catch_warnings():
            warnings.simplefilter('ignore',UserWarning)
            with zipfile.ZipFile(duplicate,'w') as archive:
                archive.writestr('same',b'a');archive.writestr('same',b'b')
        with zipfile.ZipFile(io.BytesIO(duplicate.getvalue())) as archive:
            with self.assertRaises(ValueError):module.zip_inventory(archive)

    def test_d8_lambda_annotation_allowlist_is_exact(self):
        self.assertEqual(module.SYNTHETIC_D8_ALLOWED, {'Lcom/android/tools/r8/annotations/LambdaMethod;'})
        own = set(module.REQUIRED) | set(module.SYNTHETIC_D8_ALLOWED)
        allowed = {module.family(name) for name in module.REQUIRED}
        result = module.check_collisions(own, [], set(), set(module.REQUIRED), allowed)
        self.assertEqual(result['own_definitions'], len(own))
        with self.assertRaisesRegex(ValueError, 'Unexpected own DEX/API-stub definition'):
            module.check_collisions(own | {'Lcom/android/tools/r8/annotations/Other;'}, [], set(),
                                    set(module.REQUIRED), allowed)
        with self.assertRaisesRegex(ValueError, 'Unexpected own DEX/API-stub definition'):
            module.check_collisions(own | {'Lapi/NewStub;'}, [], set(), set(module.REQUIRED), allowed)

    def test_original_game_duplicates_are_not_own_collisions(self):
        own=set(module.REQUIRED)
        allowed={module.family(name) for name in own}
        result=module.check_collisions(own,[{'Lgame/A;','Lgame/Duplicate;'}, {'Lgame/B;','Lgame/Duplicate;'}],
            {'Lmanager/M;'},own,allowed)
        self.assertEqual(result['game_existing_duplicate_definitions'],1)
        with self.assertRaises(ValueError):module.check_collisions(own|{'Lmanager/M;'},[],{'Lmanager/M;'},own,allowed|{'Lmanager/M;'})
        with self.assertRaises(ValueError):module.check_collisions(own|{'Lapi/Stub;'},[],set(),own,allowed)
        with self.assertRaises(ValueError):module.check_collisions(own-{'Lcom/project7/localmanager/CoreGapBridge;'},[],set(),own,allowed)

    def test_output_aliases_and_immutability(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);original=root/'original.apk';original.write_bytes(b'fixed original')
            output=root/'out.apk';os.link(original,output)
            with self.assertRaises(ValueError):module.reject_output_alias(output,[original])
            output.unlink();output.symlink_to(original)
            with self.assertRaises(ValueError):module.reject_output_alias(output,[original])
            output.unlink();module.reject_output_alias(output,[original])
            with self.assertRaises(ValueError):module.reject_output_alias(root/'stage/out.apk',[original],(root/'stage',))
            inputs={str(original):module.file_sha(original)};module.assert_unchanged(inputs)
            original.write_bytes(b'changed')
            with self.assertRaises(ValueError):module.assert_unchanged(inputs)

    def test_inventory_symlink_and_duplicate_json(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);target=root/'target';target.write_text('source')
            (root/'link').symlink_to(target)
            with self.assertRaises(ValueError):module.stage_path(root,'link')
            document=root/'metadata.json';document.write_text('{"a":1,"a":2}')
            with self.assertRaises(ValueError):module.read_json(document)

    def test_certificate_pin_gate(self):
        expected='52893d575ae8e51b860ed744d6b5c36db3a2928d96100b0b6ac711630bbbee6b'
        self.assertEqual(module.require_expected_certificate(expected,expected),expected)
        self.assertEqual(module.require_expected_certificate(expected,expected.upper().replace(expected[0],expected[0])),expected)
        with self.assertRaisesRegex(ValueError,'certificate mismatch'):
            module.require_expected_certificate('0'*64,expected)
        with self.assertRaisesRegex(ValueError,'certificate mismatch'):
            module.require_expected_certificate(expected,'0'*64)

    def test_no_subprocess_from_import_or_helpers(self):
        with mock.patch.object(module.subprocess,'run',side_effect=AssertionError('assembly forbidden')):
            module.class_name(fixture_class('a/B'))
            module.check_collisions(set(module.REQUIRED),[],set(),set(module.REQUIRED),set(module.REQUIRED))
            with self.assertRaises(ValueError):module.preflight(Path('/missing.apk'),Path('/missing-stage'),Path('/missing-compiled'),Path('/out.apk'))


if __name__=='__main__':unittest.main()
