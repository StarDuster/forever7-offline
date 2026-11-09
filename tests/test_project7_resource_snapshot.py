"""Host-only resource snapshot parser and real Java publication checks."""
import _paths  # noqa: E402,F401
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import zlib
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'offline'/'current'/'tools'))
import project7_resource_snapshot as s

class SnapshotTests(unittest.TestCase):
    def test_npk_positive_uint32_and_source_offset(self):
        text=b'4294967295 0123456789abcdef0123456789abcdef 7 4294967295 12 3000000000 640 19'
        rows,count=s.convert_check('camera',1,zlib.compress(text),{640:26})
        self.assertEqual(count,1)
        self.assertEqual(rows,[[640,[[4294967295,'0123456789abcdef0123456789abcdef',7,4294967295,12,3000000000,19]]]])
    def test_raw_relative_names_and_version_removal(self):
        rows,count=s.convert_check('raw',1,zlib.compress(b'sound/output/a.fsb 0123456789abcdef0123456789abcdef 4 0 3'),{0:7})
        self.assertEqual(rows,[[0,[['sound/output/a.fsb','0123456789abcdef0123456789abcdef',4,3]]]])
        self.assertEqual(count,1)
        prefixed,_=s.convert_check('raw',1,zlib.compress(b'res/sound/output/a.fsb 0123456789abcdef0123456789abcdef 4 0 3'),{0:7})
        self.assertEqual(prefixed,rows)
    def test_official_zero_length_npk_record_is_not_empty_check(self):
        # Real official indexes contain zero-length records; retain their metadata.
        rows,n=s.convert_check('common',1,zlib.compress(b'1 d41d8cd98f00b204e9800998ecf8427e 0 0 0 0 257 0'),{257:180})
        self.assertEqual(rows[0][1][0],[1,'d41d8cd98f00b204e9800998ecf8427e',0,0,0,0,0])
    def test_bad_records_and_bounds(self):
        valid=b'1 0123456789abcdef0123456789abcdef 7 8 9 10 0 3'
        cases=[valid+b'\n'+valid,valid.replace(b' 7 ',b' -1 '),valid.replace(b' 8 ',b' 4294967296 '),valid.rsplit(b' ',1)[0],b'',valid.replace(b' 0 3',b' 999 3')]
        for raw in cases:
            with self.assertRaises(ValueError):s.convert_check('camera',1,zlib.compress(raw),{0:10})
        with self.assertRaises(ValueError):s.convert_check('camera',99,zlib.compress(valid),{0:10})
        with self.assertRaises(ValueError):s.convert_check('camera',1,zlib.compress(valid),{0:9})
        for name in ['../a','res/res/sound/a','sound/../a','sound//a','sound\\a']:
            with self.assertRaises(ValueError):s.convert_check('raw',1,zlib.compress((name+' 0123456789abcdef0123456789abcdef 1 0 0').encode()),{0:1})
    def test_zlib_truncation_trailing_and_limit(self):
        for data in [zlib.compress(b'a')[:-1],zlib.compress(b'a')+b'trailing',zlib.compress(b''),b'bad']:
            with self.assertRaises((ValueError,zlib.error)):s.unpack_check(data)
        from unittest.mock import patch
        with patch.object(s,'MAX_CHECK',32):
            with self.assertRaises(ValueError):s.unpack_check(zlib.compress(b'x'*100000))
    def test_version_duplicates_and_complete_shape(self):
        manifest=b'0=camera:0123456789abcdef0123456789abcdef:19\ncamera=1 0123456789abcdef0123456789abcdef:2\n'
        packs,parts=s.parse_version(manifest)
        self.assertEqual(packs,[[0,[['camera','0123456789abcdef0123456789abcdef',19]]]])
        self.assertEqual(parts,{'camera':[1,['0123456789abcdef0123456789abcdef',2]]})
        for damaged in [manifest+manifest.splitlines()[0]+b'\n',manifest+manifest.splitlines()[1]+b'\n',manifest.replace(b'camera=1',b'camera=9'),manifest.replace(b'camera=1',b'other=1'),b'0=\n']:
            with self.assertRaises(ValueError):s.parse_version(damaged)
    def test_fingerprint_order_and_duplicate(self):
        a={'name':'a.npk','bytes':1,'sha256':'1'*64};b={'name':'b.npk','bytes':2,'sha256':'2'*64}
        expected=hashlib.sha256(('a.npk\t1\t'+'1'*64+'\nb.npk\t2\t'+'2'*64+'\n').encode()).hexdigest()
        self.assertEqual(s.entries_fingerprint([b,a]),expected)
        with self.assertRaises(ValueError):s.entries_fingerprint([a,a])
    def test_existing_output_refused_before_inputs(self):
        with tempfile.TemporaryDirectory() as t:
            with self.assertRaisesRegex(ValueError,'output exists'):s.generate('missing','missing','missing','missing','missing','missing',t)
    def test_real_generated_snapshot_independent_records(self):
        directory=ROOT/'analysis/project7/resource-snapshot'
        if not directory.is_dir():self.skipTest('Generated local snapshot unavailable')
        payload=(directory/'project7-resource-snapshot.json').read_bytes();state=json.loads(payload)
        self.assertEqual(set(state),{'schema','version','platform','parts','packs','manifest'})
        self.assertEqual((state['schema'],state['version'],state['platform']),(1,455,'android'))
        self.assertEqual(len(payload),17437832)
        self.assertEqual((len(state['parts']),len(state['packs']),len(state['manifest'])),(37,191,38))
        self.assertNotIn('script',dict(state['parts']));self.assertIn('script',state['manifest'])
        plan=json.loads((ROOT/'reports/official-asset-source-plan.json').read_bytes())
        count=0
        for part,versions in state['parts']:
            source=next(p for p in plan['parts'] if p['part']==part)
            packed=(ROOT/'originals/cdn/objects'/source['check']['md5']).read_bytes()
            self.assertEqual(hashlib.sha256(packed).hexdigest(),source['check_sha256'])
            grouped={}
            for line in zlib.decompress(packed).decode('ascii').splitlines():
                fields=line.split()
                if part=='raw':
                    version=int(fields[3]);info=[fields[0],fields[1],int(fields[2]),int(fields[4])]
                else:
                    version=int(fields[6]);info=[int(fields[0]),fields[1],*map(int,fields[2:6]),int(fields[7])]
                grouped.setdefault(version,[]).append(info);count+=1
            self.assertEqual(versions,[[v,rows] for v,rows in grouped.items()])
        self.assertEqual(count,199853)
        # Numeric lines and named lines are independently checked against all source text.
        text=(ROOT/'upstream/project7/provenance/patch2.android.640.version').read_text()
        numeric=[line for line in text.splitlines() if line.split('=')[0].isdigit()]
        self.assertEqual([v for v,_ in state['packs']],[int(line.split('=')[0]) for line in numeric])
        for (version,rows),line in zip(state['packs'],numeric):
            self.assertEqual(rows,[[p,m,int(n)] for p,m,n in (item.split(':') for item in line.split('=')[1].split())])
        for line in text.splitlines():
            name,spec=line.split('=')
            if name.isdigit():continue
            kind,pin=spec.split();md5,size=pin.split(':')
            self.assertEqual(state['manifest'][name],[int(kind),[md5,int(size)]])
        reproduction=ROOT/'analysis/project7/resource-snapshot-reproduction'
        if reproduction.is_dir():
            for name in ['project7-resource-snapshot.json','project7-resource-binding.json','check-provenance.json']:
                self.assertEqual((directory/name).read_bytes(),(reproduction/name).read_bytes())
    def test_java_real_importer_publication(self):
        java=ROOT/'toolchains/java/jdk-17.0.21+9/Contents/Home/bin'
        if not (java/'javac').is_file():self.skipTest('Host JDK unavailable')
        sources=[ROOT/'offline/current/java/android_resource_init/src/com/forever7/offline/ResourceImporter.java',ROOT/'offline/current/java/android_resource_init/src/com/forever7/offline/Project7ResourceSnapshot.java',ROOT/'offline/current/java/android_resource_init/tests/Project7ResourceSnapshotHostTest.java',ROOT/'offline/current/java/android_resource_init/tests/Project7ResourceFastStartHostTest.java']
        with tempfile.TemporaryDirectory() as t:
            subprocess.run([str(java/'javac'),'-source','8','-target','8','-Xlint:-options','-d',t,*map(str,sources)],check=True,capture_output=True)
            result=subprocess.run([str(java/'java'),'-cp',t,'Project7ResourceSnapshotHostTest'],check=True,capture_output=True,text=True)
            self.assertIn('312 force checks, 10 failure cases',result.stdout)
            fast=subprocess.run([str(java/'java'),'-cp',t,'com.forever7.offline.Project7ResourceFastStartHostTest'],check=True,capture_output=True,text=True)
            self.assertIn('53 scenarios, 15 expected failure cases',fast.stdout)
if __name__=='__main__':unittest.main()
