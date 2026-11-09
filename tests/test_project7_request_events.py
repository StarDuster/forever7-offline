"""Fixed public catalog invariants; original engine proof is separate verify.py."""
from pathlib import Path
import hashlib,importlib.util,json,re,unittest
ROOT=Path(__file__).resolve().parents[1];DATA=ROOT/'runtime/project7_request_events'
class RequestEventCatalogTests(unittest.TestCase):
 def test_catalog_hash_and_java_pin(self):
  blob=(DATA/'request-events.tsv').read_bytes();pins=json.loads((DATA/'pins.json').read_text());digest=hashlib.sha256(blob).hexdigest()
  self.assertEqual(pins['payload_sha256'],digest)
  self.assertIn('SHA256 = "'+digest+'"',(ROOT/'runtime/android_request_events/src/com/project7/localmanager/RequestEventCatalog.java').read_text())
 def test_digest_and_original_trigger_columns(self):
  row=[l for l in (DATA/'request-events.tsv').read_text().splitlines() if not l.startswith('#')][0].split('\t')
  self.assertEqual(len(row),24);self.assertEqual(row[1],hashlib.md5(row[0].encode()).hexdigest());self.assertEqual(row[3:9],['1','60','0','0','10','immediate'])
  self.assertEqual(row[17:20],['0,0','3,2147483647','0']);self.assertEqual(row[-1],'42=281');self.assertEqual(row[9],'true')
 def test_fixed_producer_default_uses_no_analysis_inputs(self):
  spec=importlib.util.spec_from_file_location('request_producer',DATA/'produce.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
  self.assertEqual(len(m.PINNED_INPUT_SHA256),4)
  for digest in m.PINNED_INPUT_SHA256:self.assertRegex(digest,'^[a-f0-9]{64}$')
 def test_business_code_uses_no_event_id_branch_or_new_profile_owner(self):
  source=(ROOT/'runtime/android_request_events/src/com/project7/localmanager/RequestEventAdmission.java').read_text()
  self.assertNotIn('417',source);self.assertNotIn('markCompleted',source);self.assertNotIn('writeAtomic',source);self.assertIn('"triggerMatches"',source)
if __name__=='__main__':unittest.main()
