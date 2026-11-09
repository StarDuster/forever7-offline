"""Project the 17 code20-blocked auto events into an append-only prepare candidate.

The code20 ledger/provider seam is a maintainer manager candidate; these rows are
not published to prepare.  Projection uses the same original event_condition /
event_content tables and the same 14-column Trigger shape as the 222-row and
16-row candidates.  Every other blocked event stays blocked.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))

from project7_event_auto_trigger_candidate import (  # noqa: E402
    BASE_GRAPH_SHA256, load_tables, project_row, require)
from runtime.project7_dream_catalog.produce import literal  # noqa: E402

BASE_CONTRACT = ROOT / "runtime/project7_event_auto_trigger_candidate/contract-v1.json"
BASE_ASSET = ROOT / "runtime/project7_event_auto_trigger_candidate/trigger-extra-v1.tsv"
COND_ASSET = ROOT / "runtime/project7_event_auto_trigger_condition_candidate/trigger-extra-conditions-v1.tsv"
COND_CONTRACT = ROOT / "runtime/project7_event_auto_trigger_condition_candidate/contract-v1.json"
OUT = ROOT / "runtime/project7_action_ledger_integration_candidate"
ASSET = OUT / "trigger-extra-code20-v1.tsv"
CONTRACT = OUT / "contract-v1.json"
SUPPORTED = frozenset((5, 6, 7, 12, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28,
                       29, 30, 31, 32, 33, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44,
                       45, 46, 47, 48, 49, 50, 51, 52, 53, 54))
STRUCTURAL = frozenset((1, 17, 9, 11, 8, 4, 16, 3, 102, 100, 101))


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def rows(path):
    return [line.split("\t", -1) for line in Path(path).read_text(encoding="utf-8").splitlines()
            if line and not line.startswith("#")]


def build():
    require(sha(ROOT / "analysis/project7/story-city-integration-prepare-v43/"
                "project7-inputs-6i2v7gq2/stage/assets/event_graph.tsv") == BASE_GRAPH_SHA256,
            "base graph pin changed")
    base_contract = json.loads(BASE_CONTRACT.read_text(encoding="utf-8"))
    cond_contract = json.loads(COND_CONTRACT.read_text(encoding="utf-8"))
    events = sorted(int(row["event"]) for row in base_contract["blocked"]
                    if len(row["codes"]) == 1 and row["codes"][0] == 20)
    require(len(events) == 17, "code20 blocked population changed")
    require(set(events) == set(cond_contract["code20_blocked"]), "code20 event set changed")
    tables = load_tables()
    conditions, contents = tables["event_condition"], tables["event_content"]
    lines = [
        "# project7 code20 provider-gated append-only candidate (prepare-only)",
        "# base event_graph.tsv sha256: " + BASE_GRAPH_SHA256,
        "# rows require a valid LocalActionLedger completion baseline; no ledger means invalid/blocked",
    ]
    for event in events:
        condition, content = conditions[event], contents[event]
        require(condition.get("release") is True and content.get("release") is True,
                "code20 event not released: %d" % event)
        row = project_row(event, condition, content)
        codes = {int(item.split("=", 1)[0]) for item in row[13].split(";") if item}
        require(20 in codes, "code20 predicate missing for %d" % event)
        require(codes <= SUPPORTED | STRUCTURAL, "unsupported code for %d: %r" % (event, codes))
        lines.append("\t".join(row))
    return events, lines


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if not (args.write or args.check):
        parser.error("choose --write or --check")
    events, lines = build()
    if args.write:
        OUT.mkdir(parents=True, exist_ok=True)
        ASSET.write_text("\n".join(lines) + "\n", encoding="utf-8")
        base_assert = rows(BASE_ASSET)
        cond_assert = rows(COND_ASSET)
        require(len(base_assert) == 222 and len(cond_assert) == 16, "prior candidates changed")
        require(set(events) & {int(r[1]) for r in base_assert} == set(), "222 collision")
        require(set(events) & {int(r[1]) for r in cond_assert} == set(), "16 collision")
        contract = {
            "schema": "project7-action-ledger-integration-candidate-v1",
            "policy": "code20-provider-gated-append-only-v1",
            "base_event_graph_sha256": BASE_GRAPH_SHA256,
            "base_candidate": {"asset": str(BASE_ASSET.relative_to(ROOT)),
                               "asset_sha256": sha(BASE_ASSET), "rows": 222},
            "condition_candidate": {"asset": str(COND_ASSET.relative_to(ROOT)),
                                    "asset_sha256": sha(COND_ASSET), "rows": 16},
            "code20_candidate": {"asset": str(ASSET.relative_to(ROOT)),
                                 "asset_sha256": sha(ASSET), "rows": len(events),
                                 "events": events},
            "counts": {"combined_candidate_rows": 222 + 16 + len(events),
                       "fully_usable_condition_rows": 15,
                       "engine_gated_condition_rows": 1,
                       "code20_provider_gated_rows": len(events),
                       "content_release_false_blocked": 247},
            "code10_composite": {"event": 1000105, "code": 10,
                                 "scope": "LocalEventEngine patrolAreas/clientOps context only",
                                 "non_patrol": "LocalStoryConditions unsupported"},
            "consumer": {"row_gate": "valid LocalActionLedger baseline and completed event",
                         "no_fact": "invalid, satisfied=false; never passed",
                         "published_to_prepare": False},
            "no_d8_no_apk_no_native": True,
        }
        CONTRACT.write_text(json.dumps(contract, indent=2, sort_keys=True) + "\n",
                            encoding="utf-8")
        print("PASS code20 rows=%d combined=%d" % (len(events), 222 + 16 + len(events)))
        return
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    require(sha(ASSET) == contract["code20_candidate"]["asset_sha256"], "asset pin changed")
    written = rows(ASSET)
    require(len(written) == 17, "asset row count changed")
    require([int(r[1]) for r in written] == events, "asset event order changed")
    require(contract["counts"]["combined_candidate_rows"] == 255, "combined count changed")
    print("PASS code20 rows=%d combined=255" % len(events))


if __name__ == "__main__":
    main()
