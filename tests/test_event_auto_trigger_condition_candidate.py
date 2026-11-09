"""The 16-row condition increment must stay separate, exact and code-20 free."""
import hashlib
import json
import sys
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from project7_event_auto_trigger_condition_candidate import (  # noqa: E402
    ASSET, BASE_ASSET, build, NEW_CODES)

EXPECTED = [548, 549, 550, 551, 552, 3024, 5058, 7065, 7068, 7070, 7072,
            7079, 8014, 1000105, 1000112, 1000312]


def sha(data):
    return hashlib.sha256(data).hexdigest()


class ConditionCandidateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.asset, cls.contract = build()

    def test_counts(self):
        counts = self.contract["counts"]
        self.assertEqual(counts["condition_candidate_rows"], 16)
        self.assertEqual(counts["base_candidate_rows"], 222)
        self.assertEqual(counts["combined_candidate_rows"], 238)
        self.assertEqual(counts["code20_blocked_events"], 17)

    def test_exact_event_set(self):
        self.assertEqual(self.contract["events"], EXPECTED)
        self.assertEqual(self.contract["code20_blocked"],
                         [3103, 3104, 3105, 3106, 3107, 3108, 3109, 3110,
                          3111, 3112, 3113, 3114, 5042, 1001916, 1001917,
                          1001918, 1001919])

    def test_rows_only_target_codes_and_no_code20(self):
        rows = [line.split("\t", -1) for line in self.asset.decode().splitlines()
                if line and not line.startswith("#")]
        self.assertEqual(len(rows), 16)
        for row in rows:
            self.assertEqual(len(row), 14)
            self.assertEqual(row[0], "@trigger")
            codes = {int(item.split("=", 1)[0]) for item in row[13].split(";") if item}
            self.assertTrue(codes & NEW_CODES, row[1])
            self.assertNotIn(20, codes, row[1])

    def test_base_candidate_is_untouched(self):
        self.assertEqual(sha(BASE_ASSET.read_bytes()),
                         self.contract["base_candidate"]["asset_sha256"])
        self.assertEqual(sha(ASSET.read_bytes()), self.contract["asset_sha256"])

    def test_written_contract_matches(self):
        if not (ASSET.parent / "contract-v1.json").exists():
            self.skipTest("candidate not written")
        written = json.loads((ASSET.parent / "contract-v1.json").read_text(encoding="utf-8"))
        self.assertEqual(written, self.contract)


if __name__ == "__main__":
    unittest.main()
