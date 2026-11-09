"""Ending-trigger catalog shape and current-original authorization boundary."""
from pathlib import Path
import hashlib
import json
import unittest

ROOT = Path(__file__).resolve().parents[1]
ASSET = ROOT / "runtime/project7_request_events/ending-trigger-v1.json"
SHA256 = "1792a804aba72c806a7bb73dce3a42baf52695ff0edc5b476fbbe05c89095431"
SOURCE_SHA256 = "4a14531712d43d9b006c716a6364fbec0620f2b765ceb3a68505f8db4540b844"


def authorized(document, source_week, endings):
    rules = document["weeks"].get(str(source_week + 1))
    if rules is None:
        return None
    known = set(endings)
    found = []
    for rule in rules:
        satisfied = True
        for group in rule["requires"]:
            if not any(ending in known for ending in group):
                satisfied = False
                break
        if satisfied or rule["false_client_event"] == 0 or rule["false_event"] == 0:
            continue
        found.append(rule["false_event"])
    if len(found) > 1:
        return "ambiguous"
    return found[0] if found else None


class CatalogTests(unittest.TestCase):
    def setUp(self):
        self.raw = ASSET.read_bytes()
        self.document = json.loads(self.raw)

    def test_pinned_source_and_canonical_bytes(self):
        self.assertEqual(hashlib.sha256(self.raw).hexdigest(), SHA256)
        self.assertEqual(self.document["schema"], "project7-ending-trigger-v1")
        self.assertEqual(self.document["source"], {"table": "mainline_week_info", "sha256": SOURCE_SHA256})
        rewrote = (json.dumps(self.document, ensure_ascii=True, sort_keys=True, separators=(",", ":")) + "\n").encode("ascii")
        self.assertEqual(rewrote, self.raw)

    def test_current_original_has_no_authorized_event(self):
        endings = [2, 3, 5, 6, 7, 8, 9, 19, 20, 21, 28, 29, 30, 36, 42, 43]
        for week in range(0, 5):
            for mask in range(1 << len(endings)):
                subset = {ending for index, ending in enumerate(endings) if mask & (1 << index)}
                self.assertIsNone(authorized(self.document, week, subset), (week, sorted(subset)))
        self.assertEqual(sum(len(rows) for rows in self.document["weeks"].values()), 6)

    def test_synthetic_rule_projects_only_for_host(self):
        document = json.loads(self.raw)
        document["weeks"]["1"][0].update(false_client_event=1, false_event=990001)
        self.assertEqual(authorized(document, 0, []), 990001)
        self.assertIsNone(authorized(document, 0, {2, 6, 7}))
        self.assertIsNone(authorized(document, 1, []))


if __name__ == "__main__":
    unittest.main()
