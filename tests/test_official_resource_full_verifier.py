"""Host verifier executes real production Java; no replacement importer."""
import hashlib
import json
from pathlib import Path
import shutil
import struct
import subprocess
import sys
import tempfile
import unittest
import zlib
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from verify_official_resources_java import JAVA_FILES,MARKER,clean_owned_scratch
JAVA=ROOT/'toolchains/java/jdk-17.0.21+9/Contents/Home/bin'

class FullVerifierSafetyTests(unittest.TestCase):
    def test_cleanup_requires_exclusive_child_and_matching_marker(self):
        with tempfile.TemporaryDirectory()as folder:
            parent=Path(folder);scratch=parent/'official-java-test';scratch.mkdir();(scratch/MARKER).write_text('own')
            source=parent/'source-cache';source.mkdir();(source/'keep').write_bytes(b'original')
            for path,token in ((source,'own'),(scratch,'wrong')):
                with self.assertRaises(ValueError):clean_owned_scratch(path,parent,token)
            self.assertEqual((source/'keep').read_bytes(),b'original')
            clean_owned_scratch(scratch,parent,'own');self.assertFalse(scratch.exists())

@unittest.skipUnless((JAVA/'javac').is_file(),'Local JDK required')
class FullVerifierProductionJavaTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp=tempfile.TemporaryDirectory();cls.classes=Path(cls.temp.name)/'classes';cls.classes.mkdir()
        subprocess.run([str(JAVA/'javac'),'-source','8','-target','8','-Xlint:-options','-d',str(cls.classes)]+[str(ROOT/f)for f in JAVA_FILES],check=True,capture_output=True)
    @classmethod
    def tearDownClass(cls):cls.temp.cleanup()
    def invoke(self,bad=False):
        with tempfile.TemporaryDirectory()as folder:
            root=Path(folder);cache=root/'source';scratch=root/'official-java-owned';scratch.mkdir();(scratch/MARKER).write_text('test')
            data=b'\1\2\3';check=zlib.compress(b'42 00000000000000000000000000000000 3 7 3 7 0 0\n')
            expected=b'NXPK'+struct.pack('<6I',1,0,0,2,32,0)+data+b'\0'+struct.pack('<7I',42,28,3,3,7,7,0)
            rows=[]
            for kind,part,path,content in [('C','hero','patch2.android.640/hero.check',check),('D','hero','patch2.android.640/0/hero.data',data),('D','raw','patch2.android.640/0/raw.data',data)]:
                file=cache/path;file.parent.mkdir(parents=True,exist_ok=True);file.write_bytes(content)
                rows.append((kind,part,path,len(content),hashlib.md5(content).hexdigest(),hashlib.sha256(content).hexdigest()if kind=='C'else'-'))
            rows += [('N','hero.npk',len(expected),'0'*64 if bad else hashlib.sha256(expected).hexdigest(),'hero'),('R','sound/output/object.fsb',2,hashlib.sha256(data[1:]).hexdigest(),0,1)]
            before={str(p.relative_to(cache)):hashlib.sha256(p.read_bytes()).hexdigest()for p in cache.rglob('*')if p.is_file()}
            plan=root/'plan.tsv';plan.write_text(''.join('\t'.join(map(str,row))+'\n'for row in rows));result=root/'outputs.jsonl'
            proc=subprocess.run([str(JAVA/'java'),'-cp',str(self.classes),'OfficialResourceFullVerifier',str(plan),str(cache),str(scratch),str(result)],capture_output=True,text=True)
            evidence=[json.loads(row)for row in result.read_text().splitlines()]
            after={str(p.relative_to(cache)):hashlib.sha256(p.read_bytes()).hexdigest()for p in cache.rglob('*')if p.is_file()}
            self.assertEqual(before,after);self.assertTrue(all(row['deleted']for row in evidence[:-1]))
            self.assertEqual(evidence[-1]['network_denial_probe_attempts'],1);self.assertEqual(evidence[-1]['network_attempts_during_reconstruction'],0)
            return proc,evidence
    def test_real_java_builds_exact_npk_and_raw_then_independently_hashes_deletes(self):
        proc,rows=self.invoke();self.assertEqual(proc.returncode,0,proc.stderr)
        self.assertEqual([row['ok']for row in rows[:-1]],[True,True]);self.assertEqual(rows[-1]['verified_bytes'],62)
    def test_production_digest_failure_reported_no_reroll_no_network(self):
        proc,rows=self.invoke(True);self.assertEqual(proc.returncode,1)
        self.assertFalse(rows[0]['ok']);self.assertTrue(rows[1]['ok']);self.assertEqual(rows[-1]['failures'],1)
