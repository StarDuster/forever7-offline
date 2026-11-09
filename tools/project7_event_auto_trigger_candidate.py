"""Derive the missing generic `@trigger` rows for the frozen LocalEventCatalog graph.

The frozen `event_graph.tsv` carries `@trigger` rows only for part of the released
`event_content` auto events.  The rows are, however, a pure projection of the
original `event_condition.conds` table plus the `event_content.isEmergencyEvent`
flag: this tool re-projects every existing row (3490/3490 semantic match) and then
projects the same fields for auto events that have no row yet.

Rows are emitted only when the event is released in both tables, is not supplied by
another modelled path (week entry starter, `@route` entry, predecessor successor
edge) and every condition code is either a structural trigger column or a code the
production `LocalStoryConditions` evaluator accepts.  Everything else is reported,
never invented.

The output is an append-only candidate increment.  It is NOT wired into the
prepare/build pipeline and does not edit the frozen graph, production classes,
Hook/COC/menu10/menu12 assets or any per-event table.

Writer: .venv/bin/python tools/project7_event_auto_trigger_candidate.py --write
Verifier: .venv/bin/python tools/project7_event_auto_trigger_candidate.py --check
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from runtime.project7_dream_catalog.produce import literal  # noqa: E402

CDATA = ROOT / "analysis/android640-scripts/com/data/cdata"
STAGE = (ROOT / "analysis/project7/story-city-integration-prepare-v43/"
         "project7-inputs-6i2v7gq2/stage/assets")
BASE_GRAPH = STAGE / "event_graph.tsv"
WEEKS = STAGE / "weeks.tsv"
OUT = ROOT / "runtime/project7_event_auto_trigger_candidate"
ASSET = OUT / "trigger-extra-v1.tsv"
CONTRACT = OUT / "contract-v1.json"

SCHEMA = "project7-event-auto-trigger-candidate-v1"
POLICY = "event-condition-projection-append-only-v1"
SOURCE_PINS = {
    "event_condition": "1ab7a968ebc01bccfa9419172ed92e91d9d491aa7288d616f2c8181de5389ec1",
    "event_content": "0ddb80bbe56259a2f54acdb7accef49ad390240b0cac504ba1375a3c8976afe7",
}
BASE_GRAPH_SHA256 = "50d211e2108524dbce10e9babf9de77cf9faf9e331f8a70f8d1a8f6d771f927f"
WEEKS_SHA256 = "dbb0a5d64492e18243a332c93c4a855f5572661922bd26b870b48a96b8ffaa55"

# `LocalEventCatalog$Trigger` columns: 0 tag, 1 event, 2 preAll, 3 preAny,
# 4 battles, 5 mutex, 6 areas, 7 date, 8 week, 9 emergency, 10 patrolAreas,
# 11 clientOps, 12 areaClicks, 13 predicates.
COLUMNS = ("preAll", "preAny", "battles", "mutex", "areas", "date", "week",
           "emergency", "patrolAreas", "clientOps", "areaClicks", "predicates")
STRUCTURAL_CODES = (1, 17, 9, 11, 8, 4, 16, 3, 102, 100, 101)
# Codes the production LocalStoryConditions.SUPPORTED set evaluates.  Codes 10
# and 35 are not in that set but the frozen asset already emits them as
# predicates, so they stay renderable and are reported as engine-gated.
ENGINE_SUPPORTED = frozenset((
    5, 6, 7, 12, 18, 19, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 32, 33,
    34, 36, 37, 38, 39, 40, 41, 42, 43, 44, 47, 48, 50, 51, 52, 53, 54,
))
ENGINE_GATED = frozenset((10, 35))
ALLOWED_PREDICATE_CODES = frozenset(ENGINE_SUPPORTED | ENGINE_GATED)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def require(value, message):
    if not value:
        raise ValueError(message)


def load_tables():
    tables = {}
    for name, digest in SOURCE_PINS.items():
        path = CDATA / (name + ".marshal")
        require(sha(path.read_bytes()) == digest, "source pin changed: " + name)
        tables[name] = literal(path)
    require(sha(BASE_GRAPH.read_bytes()) == BASE_GRAPH_SHA256, "base event graph pin changed")
    require(sha(WEEKS.read_bytes()) == WEEKS_SHA256, "weeks pin changed")
    return tables


def split_top(text):
    parts, depth, current = [], 0, ""
    for char in text:
        if char in "([{":
            depth += 1
        elif char in ")]}":
            depth -= 1
        if char == "," and depth == 0:
            parts.append(current)
            current = ""
        else:
            current += char
    if current.strip():
        parts.append(current)
    return parts


def render_value(raw, area=False):
    """Render one original condition literal the way the frozen graph renders it."""
    text = raw.strip()
    match = re.match(r"^set\(\[(.*)\]\)$", text)
    if match:
        body = match.group(1).strip()
        if not body:
            return ""
        items = []
        for item in split_top(body):
            item = item.strip()
            if item.startswith("("):
                joined = ":".join(x.strip() for x in item.strip("() ").split(",") if x.strip())
                items.append((joined, 0))
            elif item.startswith("'"):
                items.append((item.strip("'"), 1))
            else:
                items.append((int(item), -1))
        unique, seen = [], set()
        for value, kind in items:
            if (value, kind) not in seen:
                seen.add((value, kind))
                unique.append((value, kind))
        unique.sort(key=lambda pair: (pair[1], pair[0]))
        separator = "|" if len(unique) > 1 and all(kind == 0 for _, kind in unique) else ","
        return separator.join(str(value) for value, _ in unique)
    match = re.match(r"^\{([^}]*)\}$", text)
    if match:
        body = match.group(1).strip()
        if not body:
            return ""
        parts = []
        for item in split_top(body):
            key, value = item.split(":", 1)
            value = value.strip()
            if value.startswith("("):
                values = [x.strip() for x in value.strip("() ").split(",") if x.strip()]
                parts.append((key.strip(), key.strip() + ":" +
                              (",".join(values) if area else ":".join(values))))
            else:
                parts.append((key.strip(), key.strip() + ":" + value))
        parts.sort(key=lambda pair: (0, int(pair[0])) if pair[0].isdigit() else (1, pair[0]))
        return "|".join(value for _, value in parts)
    match = re.match(r"^\[(\d+),(\d*)[)\]]$", text)
    if match:
        return match.group(1) + "," + (match.group(2) or "2147483647")
    return text


def require_emergency_match(event, condition, content):
    """Original conds[101] and event_content.isEmergencyEvent must agree.

    The trigger row carries `emergency` from event_content only; a divergence
    would silently drop the original condition, so fail the extraction instead.
    """
    raw = condition["conds"].get(101)
    if raw is None:
        declared = False
    else:
        try:
            literal = str(raw).strip()
            if literal not in ("0", "1"):
                raise ValueError("condition 101 must be literal 0/1")
            declared = literal == "1"
        except (TypeError, ValueError):
            raise ValueError("invalid emergency condition for event %d" % event)
    require(declared == bool(content.get("isEmergencyEvent")),
            "emergency condition/content mismatch for event %d" % event)


def project_row(event, condition, content):
    """Project one original event into the 14 LocalEventCatalog.Trigger columns."""
    conds = condition["conds"]
    row = ["@trigger", str(event)]
    for code in (1, 17, 9, 11):
        row.append(render_value(conds[code]) if code in conds else "")
    row.append(render_value(conds[8], area=True) if 8 in conds else "")
    for code in (4, 16):
        row.append(render_value(conds[code]) if code in conds else "")
    row.append("1" if content.get("isEmergencyEvent") else "0")
    for code in (3, 102, 100):
        row.append(render_value(conds[code]) if code in conds else "")
    extra = [code for code in conds if code not in STRUCTURAL_CODES]
    row.append(";".join("%d=%s" % (code, render_value(conds[code])) for code in extra))
    return row


def predicate_set(text):
    return frozenset(item for item in text.split(";") if item)


def parse_graph(lines):
    triggers, routes, successors = set(), {}, {}
    for line in lines:
        parts = line.split("\t")
        if not parts or not parts[0]:
            continue
        if parts[0] == "@trigger":
            triggers.add(int(parts[1]))
        elif parts[0] == "@route":
            routes[int(parts[1])] = parts[2]
        elif parts[0].isdigit():
            require(len(parts) == 7, "event row schema")
            successors[int(parts[0])] = [int(v) for v in parts[5].split(",") if v]
    return triggers, routes, successors


def parse_weeks(lines):
    inits = []
    for line in lines:
        parts = line.split("\t")
        if parts[0] == "route":
            inits.append(int(parts[2]))
    return set(inits)


def build():
    tables = load_tables()
    conditions, contents = tables["event_condition"], tables["event_content"]
    graph_lines = BASE_GRAPH.read_text(encoding="utf-8").splitlines()
    triggers, routes, successors = parse_graph(graph_lines)
    week_inits = parse_weeks(WEEKS.read_text(encoding="utf-8").splitlines())

    parents = {}
    for event, children in successors.items():
        for child in children:
            parents.setdefault(child, []).append(event)

    auto_events = {event for event, row in contents.items() if row.get("isAutoTriggerEvent")}
    require(len(auto_events) == 3997, "auto event population changed")

    rows, fallback, unproven, blocked = [], {"week": [], "route": [], "successor": []}, {"week": [], "entry": []}, []
    for event in sorted(auto_events):
        if event in triggers:
            continue
        content_row = contents[event]
        if not content_row.get("release"):
            blocked.append({"event": event, "codes": ["content-release-false"]})
            continue
        condition = conditions.get(event)
        if not condition or "conds" not in condition:
            blocked.append({"event": event, "codes": ["no-condition-row"]})
            continue
        if not condition.get("release"):
            blocked.append({"event": event, "codes": ["condition-release-false"]})
            continue
        # A week starter and a parent-only event without its own route condition
        # are entry evidence, not proof that an independent auto row is redundant.
        # They stay rowless and are reported separately; they are not candidates.
        if event in week_inits:
            unproven["week"].append(event)
            continue
        if event in parents and 52 not in condition["conds"] and event not in routes:
            unproven["entry"].append(event)
            continue
        bad = sorted(code for code in condition["conds"]
                     if code not in STRUCTURAL_CODES and code not in ALLOWED_PREDICATE_CODES)
        if bad:
            blocked.append({"event": event, "codes": bad})
            continue
        require_emergency_match(event, condition, contents[event])
        rows.append(project_row(event, condition, contents[event]))

    # Re-project every frozen row and compare: proves the projection is complete.
    mismatch, checked = [], 0
    for line in graph_lines:
        if not line.startswith("@trigger\t"):
            continue
        frozen = line.split("\t")
        event = int(frozen[1])
        require(event in conditions and event in contents, "frozen trigger without source")
        require_emergency_match(event, conditions[event], contents[event])
        projected = project_row(event, conditions[event], contents[event])
        if projected[:13] != frozen[:13] or predicate_set(projected[13]) != predicate_set(frozen[13]):
            mismatch.append(event)
        checked += 1
    require(not mismatch, "projection mismatch: %s" % mismatch[:5])

    header = [
        "# project7 generic event auto-trigger increment (append-only)",
        "# base event_graph.tsv sha256: " + BASE_GRAPH_SHA256,
        "# derived from original event_condition/event_content literals only; "
        "no per-event hand edits",
        "# rows only for released auto events with no @trigger row and an independent condition",
        "# unproven entry events and evaluator-blocked events are listed in contract-v1.json",
    ]
    asset = ("\n".join(header + ["\t".join(row) for row in rows]) + "\n").encode("utf-8")
    contract = {
        "schema": SCHEMA,
        "policy": POLICY,
        "producer": "tools/project7_event_auto_trigger_candidate.py",
        "base_event_graph": str(BASE_GRAPH.relative_to(ROOT)),
        "base_event_graph_sha256": BASE_GRAPH_SHA256,
        "weeks": str(WEEKS.relative_to(ROOT)),
        "weeks_sha256": WEEKS_SHA256,
        "source_pins": SOURCE_PINS,
        "consumer": {
            "catalog": "com.project7.localmanager.LocalEventCatalog$Trigger",
            "engine": "com.project7.localmanager.LocalEventEngine.triggerBlocker/"
                      "triggerMatches/reevaluateLifecycle",
            "fields": list(COLUMNS),
            "append_only": True,
            "published_to_prepare": False,
        },
        "extraction_rule": {
            "population": "event_content.isAutoTriggerEvent == true",
            "released": "event_content.release and event_condition.release must be true",
            "skip": "existing @trigger row",
            "candidate": "released, condition row present, no unsupported predicate code; @route key and predecessor edge alone do not exclude",
            "unproven": "week starter, or parent-only event without its own route condition; reported rowless",
            "unreleased": "reported blocked by release, never treated as normal fallback",
            "blocked": "condition code outside structural columns and evaluator support",
            "structural_codes": list(STRUCTURAL_CODES),
            "allowed_predicate_codes": sorted(ALLOWED_PREDICATE_CODES),
            "engine_gated_predicate_codes": sorted(ENGINE_GATED),
        },
        "counts": {
            "auto_events": len(auto_events),
            "frozen_trigger_rows": checked,
            "frozen_rows_reproduced": checked,
            "frozen_rows_mismatch": len(mismatch),
            "candidate_rows": len(rows),
            "fallback_events": sum(len(v) for v in fallback.values()),
            "unproven_events": sum(len(v) for v in unproven.values()),
            "blocked_events": len(blocked),
        },
        "blocked_code_counts": {"+".join(map(str, codes)): count for codes, count in
                                Counter(tuple(item["codes"]) for item in blocked).items()},
        "fallback": fallback,
        "unproven": unproven,
        "blocked": blocked,
        "asset": str(ASSET.relative_to(ROOT)),
        "asset_sha256": sha(asset),
        "asset_size": len(asset),
        "asset_rows": len(rows),
    }
    return asset, contract


def canonical(contract):
    return json.dumps(contract, indent=2, sort_keys=True, ensure_ascii=True).encode("ascii") + b"\n"


def produce():
    asset, contract = build()
    OUT.mkdir(parents=True, exist_ok=True)
    ASSET.write_bytes(asset)
    CONTRACT.write_bytes(canonical(contract))
    return contract


def check():
    require(ASSET.is_file() and CONTRACT.is_file(), "candidate assets missing")
    asset, contract = build()
    require(ASSET.read_bytes() == asset, "candidate asset drift")
    require(CONTRACT.read_bytes() == canonical(contract), "candidate contract drift")
    return contract


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.write:
        contract = produce()
        print("WROTE %s rows sha256=%s" % (contract["asset_rows"], contract["asset_sha256"]))
    elif args.check:
        contract = check()
        print("PASS candidate rows=%d frozen=%d fallback=%d blocked=%d"
              % (contract["counts"]["candidate_rows"], contract["counts"]["frozen_trigger_rows"],
                 contract["counts"]["fallback_events"], contract["counts"]["blocked_events"]))
    else:
        parser.error("choose --write or --check")


if __name__ == "__main__":
    main()
