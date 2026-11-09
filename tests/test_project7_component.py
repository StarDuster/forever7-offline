"""Host-only capsule primitives: independent expected bytes and malformed inputs."""
import io
import struct
import sys
import tempfile
import unittest
from unittest.mock import patch
import zipfile
import zlib
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
import project7_component as c

class ComponentTests(unittest.TestCase):
    def test_delta_known_xor_and_different_lengths(self):
        self.assertEqual(zlib.decompress(c.delta(b'ABC',b'ABD!')),b'\0\0\x07!')
        self.assertEqual(c.restore(b'ABC',zlib.compress(b'\0\0\x07!'),4),b'ABD!')
        self.assertEqual(c.restore(b'abcdef',c.delta(b'abcdef',b'x'),1),b'x')
        self.assertEqual(c.restore(b'a',c.delta(b'a',b''),0),b'')
    def test_bounded_and_tampered_streams(self):
        for data,size in [(zlib.compress(b'A'*100000),2),(zlib.compress(b'abc')+b'junk',3),(zlib.compress(b'abc')[:-1],3),(zlib.compress(b'abc'),4),(b'bad',3)]:
            with self.assertRaises((ValueError,zlib.error)):c.restore(b'',data,size)
        with self.assertRaises(ValueError): c.restore(b'',b'',c.LIMIT+1)
        with self.assertRaises(ValueError): c.check(b'a',c.descriptor(b'b'))
    def test_paths_and_duplicate_members(self):
        for name in ['../x','/x','a/../b','a//b','a\\b','./a','']:
            with self.assertRaises(ValueError):c.safe_name(name)
        b=io.BytesIO()
        with zipfile.ZipFile(b,'w') as z:
            z.writestr('a',b'a');z.writestr('a',b'b')
        with zipfile.ZipFile(io.BytesIO(b.getvalue())) as z:
            with self.assertRaises(ValueError):c.members(z)
    def test_nxpk_metadata_preserved_except_offset(self):
        # Independently construct an indexed archive with opaque non-CRC checksums.
        source=struct.pack('<4s5I',b'NXPK',1,0,0,2,32)+b'\x11\x22\x33\x44'+b'abc\0'+struct.pack('<7I',0x12345678,28,3,99,0xdeadbeef,0xcafebabe,2)
        row,payload=c.npk(source)[0x12345678]
        rebuilt=c.overlay([(row,payload)])
        self.assertEqual(rebuilt[28:31],b'abc')
        self.assertEqual(struct.unpack_from('<7I',rebuilt,32),(0x12345678,28,3,99,0xdeadbeef,0xcafebabe,2))
        self.assertEqual(c.npk(rebuilt)[0x12345678][1],b'abc')
        for damaged in [source+b'x',source[:32]+struct.pack('<7I',1,0,3,99,0,0,2)]:
            with self.assertRaises(ValueError):c.npk(damaged)
    def test_capsule_tamper_fails_before_reading_sources(self):
        with tempfile.TemporaryDirectory() as t:
            p=Path(t)/'component';p.write_bytes(b'tampered')
            with self.assertRaisesRegex(ValueError,'component SHA mismatch'):
                c.materialize(p,Path(t)/'missing-apk',Path(t)/'missing-npk')
    def test_duplicate_fid_rejected(self):
        entry=struct.pack('<7I',42,28,0,0,9,10,0)
        data=struct.pack('<4s5I',b'NXPK',2,0,0,2,28)+b'\0'*4+entry+entry
        with self.assertRaisesRegex(ValueError,'duplicate FID'): c.npk(data)
    def test_consumer_config_layout_baseline_and_no_reference_apks(self):
        with tempfile.TemporaryDirectory() as t:
            root=Path(t)
            def writezip(name,files):
                p=root/name
                with zipfile.ZipFile(p,'w') as z:
                    for n,b in files.items():z.writestr(n,b)
                return p
            base_xml=b'<filesystems>\n  <loader root="script"/>\n</filesystems>'
            target_xml=b'<filesystems>\n  <loader root="project7_local"/><loader root="script"/>\n</filesystems>'
            base_npk=c.overlay([((i,0,3,3,123,456,0),b'old') for i in range(20)])
            target_npk=c.overlay([((i,0,3,3,321,654,0),b'new') for i in range(20)])
            official=writezip('original.apk',{**{n:b'old-dex' for n in c.DEXES},'assets/neox.xml':base_xml})
            game=writezip('game.apk',{**{n:b'new-dex' for n in c.DEXES},'assets/neox.xml':target_xml,'assets/project7_local.npk':target_npk})
            manager=writezip('manager.apk',{'classes.dex':b'dex\n038\0'+b'x'*20,**{f'assets/toy{i}':b'public' for i in range(63)}})
            baseline=root/'official.npk';baseline.write_bytes(base_npk);component=root/'component.zip'
            # Toy source trust boundary is patched; record base/target hash checks remain active.
            with patch.object(c,'pinned',side_effect=lambda path,key:Path(path).read_bytes()):
                c.produce(official,baseline,game,manager,component)
                digest=c.sha(component.read_bytes());game.unlink();manager.unlink()
                m,files=c.materialize(component,official,baseline,digest)
                self.assertEqual(files['assets/neox.xml'],target_xml)
                self.assertEqual(len(files),71)
                self.assertEqual(len(m['records']),90)
                self.assertEqual([r['role'] for r in m['records']].count('manager-asset'),63)
                with self.assertRaisesRegex(ValueError,'component SHA mismatch'):
                    c.materialize(component,official,baseline,'0'*64)
                writezip('original.apk',{**{n:b'old-dex' for n in c.DEXES},'assets/neox.xml':base_xml+b' '})
                with self.assertRaisesRegex(ValueError,'size/hash mismatch'):
                    c.materialize(component,official,baseline,digest)
    def test_wrong_pin_and_existing_output_leave_input(self):
        with tempfile.TemporaryDirectory() as t:
            p=Path(t)/'bad';p.write_bytes(b'original')
            with self.assertRaises(ValueError):c.pinned(p,'official_apk')
            with self.assertRaises(ValueError):c.apply(p,p,p,p)
            self.assertEqual(p.read_bytes(),b'original')
if __name__=='__main__':unittest.main()
