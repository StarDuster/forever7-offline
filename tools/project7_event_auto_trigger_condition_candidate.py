"""Derive the 16 auto-trigger rows enabled by manager condition codes 31/45/46/49.

This is a separate append-only increment next to the frozen 222-row candidate.
It refuses to touch that asset, code-20 rows, the frozen graph or the prepare
stage.  Every emitted row is re-projected from the original
`event_condition`/`event_content` literals with the same projection as
`project7_event_auto_trigger_candidate.py`; the only difference is that the four
codes proven by `Project7StoryConditionCodesHook` are now evaluator-supported.

Writer: .venv/bin/python tools/project7_event_auto_trigger_condition_candidate.py --write
Verifier: .venv/bin/python tools/project7_event_auto_trigger_condition_candidate.py --check
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

import project7_event_auto_trigger_candidate as base  # noqa: E402

OUT = ROOT / "runtime/project7_event_auto_trigger_condition_candidate"
ASSET = OUT / "trigger-extra-conditions-v1.tsv"
CONTRACT = OUT / "contract-v1.json"
SCHEMA = "project7-event-auto-trigger-condition-candidate-v1"
POLICY = "event-condition-projection-append-only-v1"
NEW_CODES = frozenset((31, 45, 46, 49))
BASE_CANDIDATE = ROOT / "runtime/project7_event_auto_trigger_candidate"
BASE_ASSET = BASE_CANDIDATE / "trigger-extra-v1.tsv"
BASE_CONTRACT = BASE_CANDIDATE / "contract-v1.json"
BASE_ASSET_SHA256 = "597ddb4cc68503cc0046092a40248defa98bfdd738aecd75de139261f8d9caa7"
BASE_CONTRACT_SHA256 = "690dda4e19de6a50ace311b640c44577ed2d930fbbf5067202983815c77366f4"
ALLOWED = frozenset(base.ALLOWED_PREDICATE_CODES | NEW_CODES)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def require(value, message):
    if not value:
        raise ValueError(message)


def event_rows(path):
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line or line.startswith("#"):
            continue
        parts = line.split("\t", -1)
        require(len(parts) == 14 and parts[0] == "@trigger", "candidate row schema")
        rows.append(int(parts[1]))
    return rows


def predicate_codes(row):
    codes = set()
    for item in row.split(";"):
        if item:
            codes.add(int(item.split("=", 1)[0]))
    return codes


def build():
    require(sha(BASE_ASSET.read_bytes()) == BASE_ASSET_SHA256, "222-row candidate asset changed")
    require(sha(BASE_CONTRACT.read_bytes()) == BASE_CONTRACT_SHA256, "222-row candidate contract changed")
    frozen_asset = event_rows(BASE_ASSET)
    tables = base.load_tables()
    conditions, contents = tables["event_condition"], tables["event_content"]
    graph_lines = base.BASE_GRAPH.read_text(encoding="utf-8").splitlines()
    triggers, routes, successors = base.parse_graph(graph_lines)
    week_inits = base.parse_weeks(base.WEEKS.read_text(encoding="utf-8").splitlines())
    parents = {}
    for event, children in successors.items():
        for child in children:
            parents.setdefault(child, []).append(event)
    auto_events = {event for event, row in contents.items() if row.get("isAutoTriggerEvent")}
    require(len(auto_events) == 3997, "auto event population changed")

    rows, blocked20, blocked_other = [], [], []
    for event in sorted(auto_events):
        if event in triggers:
            continue
        content_row = contents[event]
        condition = conditions.get(event)
        if not content_row.get("release") or not condition or not condition.get("release"):
            blocked_other.append(event)
            continue
        if event in week_inits:
            continue
        if event in parents and 52 not in condition["conds"] and event not in routes:
            continue
        codes = set(condition["conds"])
        target = sorted(codes & NEW_CODES)
        if not target:
            if 20 in codes:
                blocked20.append(event)
            elif event not in set(frozen_asset):
                blocked_other.append(event)
            continue
        # No row may also need a code outside the proven manager set.
        bad = sorted(code for code in codes
                     if code not in base.STRUCTURAL_CODES and code not in ALLOWED)
        require(not bad, "event %d needs unsupported %r" % (event, bad))
        require(not (codes & {20}), "event %d mixes code 20 with 31/45/46/49" % event)
        base.require_emergency_match(event, condition, content_row)
        row = base.project_row(event, condition, content_row)
        require(predicate_codes(row[13]) & NEW_CODES, "projected row lost a target code: %d" % event)
        rows.append(row)

    require(len(rows) == 16, "condition candidate population changed: %d" % len(rows))
    require(len(blocked20) == 17, "code-20 population changed: %d" % len(blocked20))
    emitted = {int(row[1]) for row in rows}
    require(not (emitted & set(frozen_asset)), "condition row collides with 222-row candidate")
    require(not (emitted & triggers), "condition row collides with frozen @trigger")

    # Existing candidate rows still project exactly, so separation is not accidental.
    for line in BASE_ASSET.read_text(encoding="utf-8").splitlines():
        if not line or line.startswith("#"):
            continue
        event = int(line.split("\t", 1)[1].split("\t", 1)[0])
        projected = base.project_row(event, conditions[event], contents[event])
        require(projected == line.split("\t"), "222-row projection changed: %d" % event)

    header = [
        "# project7 manager condition-code increment (append-only, 31/45/46/49)",
        "# base event_graph.tsv sha256: " + base.BASE_GRAPH_SHA256,
        "# separate from runtime/project7_event_auto_trigger_candidate/trigger-extra-v1.tsv (222 rows)",
        "# rows only for released auto events whose only evaluator gap was 31/45/46/49",
        "# code-20 events stay rowless in this increment",
    ]
    asset = ("\n".join(header + ["\t".join(row) for row in rows]) + "\n").encode("utf-8")
    contract = {
        "schema": SCHEMA,
        "policy": POLICY,
        "producer": "tools/project7_event_auto_trigger_condition_candidate.py",
        "manager_seam": "runtime/project7_story_condition_codes_patch/contract.json",
        "base_event_graph": str(base.BASE_GRAPH.relative_to(ROOT)),
        "base_event_graph_sha256": base.BASE_GRAPH_SHA256,
        "weeks": str(base.WEEKS.relative_to(ROOT)),
        "weeks_sha256": base.WEEKS_SHA256,
        "source_pins": base.SOURCE_PINS,
        "consumer": {
            "catalog": "com.project7.localmanager.LocalEventCatalog$Trigger",
            "engine": "com.project7.localmanager.LocalEventEngine.triggerBlocker/"
                      "triggerMatches/reevaluateLifecycle",
            "evaluator": "com.project7.localmanager.LocalStoryConditions.evaluate",
            "fields": list(base.COLUMNS),
            "append_only": True,
            "published_to_prepare": False,
        },
        "extraction_rule": {
            "population": "event_content.isAutoTriggerEvent == true and no @trigger row",
            "released": "event_content.release and event_condition.release must be true",
            "candidate": "blocked only by manager codes 31/45/46/49",
            "blocked": "any code outside structural columns and the 39-code evaluator set; code 20 stays blocked",
            "structural_codes": list(base.STRUCTURAL_CODES),
            "allowed_predicate_codes": sorted(ALLOWED),
            "added_predicate_codes": sorted(NEW_CODES),
        },
        "counts": {
            "auto_events": len(auto_events),
            "frozen_trigger_rows": len(triggers),
            "condition_candidate_rows": len(rows),
            "base_candidate_rows": len(frozen_asset),
            "combined_candidate_rows": len(rows) + len(frozen_asset),
            "code20_blocked_events": len(blocked20),
            "other_blocked_events": len(blocked_other),
        },
        "events": sorted(emitted),
        "code20_blocked": blocked20,
        "base_candidate": {
            "asset": str(BASE_ASSET.relative_to(ROOT)),
            "asset_sha256": BASE_ASSET_SHA256,
            "contract": str(BASE_CONTRACT.relative_to(ROOT)),
            "contract_sha256": BASE_CONTRACT_SHA256,
        },
        "asset_sha256": sha(asset),
        "commands": {
            "write": ".venv/bin/python tools/project7_event_auto_trigger_condition_candidate.py --write",
            "check": ".venv/bin/python tools/project7_event_auto_trigger_condition_candidate.py --check",
        },
        "no_prepare_no_d8_no_apk_no_native": True,
    }
    return asset, contract


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    asset, contract = build()
    if args.write:
        OUT.mkdir(parents=True, exist_ok=True)
        ASSET.write_bytes(asset)
        CONTRACT.write_text(json.dumps(contract, indent=2, sort_keys=True, ensure_ascii=True) + "\n", encoding="utf-8")
    elif args.check:
        require(sha(ASSET.read_bytes()) == contract["asset_sha256"], "condition candidate asset hash mismatch")
        require(json.loads(CONTRACT.read_text(encoding="utf-8")) == contract, "condition candidate contract mismatch")
    print("PASS condition-candidate rows=%d base=%d combined=%d code20=%d other_blocked=%d"
          % (contract["counts"]["condition_candidate_rows"],
             contract["counts"]["base_candidate_rows"],
             contract["counts"]["combined_candidate_rows"],
             contract["counts"]["code20_blocked_events"],
             contract["counts"]["other_blocked_events"]))


if __name__ == "__main__":
    main()
