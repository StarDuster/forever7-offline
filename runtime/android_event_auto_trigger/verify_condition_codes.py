"""Prove original semantics for auto-trigger condition codes 20/31/45/46/49.

Read-only host over the pinned original640 tables and the frozen auto-trigger
candidate contract.  It does not edit the asset, prepare/build inputs, manager
frame or device.  Results are per-code: a code is semantics-supported only when
the original predicate shape and a generic fact producer are both evidenced.
Code 20 has a proven predicate but no original client producer; it stays
explicit-fact-only and therefore unsupported for automatic trigger rows.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from collections import Counter, OrderedDict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
for path in (ROOT, ROOT / "runtime", ROOT / "tools"):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from offline_conditions import evaluate_offline_condition, parse_original_condition_literal  # noqa: E402
from runtime.project7_dream_catalog.produce import literal  # noqa: E402

CANDIDATE = ROOT / "runtime/project7_event_auto_trigger_candidate"
CONDITION = ROOT / "analysis/android640-scripts/com/data/cdata/event_condition.marshal"
CONTENT = ROOT / "analysis/android640-scripts/com/data/cdata/event_content.marshal"
EVIDENCE = ROOT / "reports/condition-codes-20-45-46-31-49.json"
TARGET_CODES = (20, 31, 45, 46, 49)
SEMANTICS_SUPPORTED = frozenset((31, 45, 46, 49))
UNPROVEN_PRODUCER = frozenset((20,))
MAX_STAR_ORDER = 4

ORIGINAL_EVIDENCE = {
    20: {
        "name": "COND_ACTIONAFTEREVENT",
        "class": "ReversedThresholdDictCondition",
        "source": [
            "analysis/original-py-640/com/const.py:3008 COND_ACTIONAFTEREVENT = 20",
            "analysis/decompiled/EventCond.py IDX_TO_TYPE[20] = ReversedThresholdDictCondition",
            "analysis/decompiled/cond_table.py:745-755 ReversedThresholdDictCondition.issubdict uses value[k] >= configured",
            "analysis/decompiled/cond_table.py:681-688 DictCondition.parse = frozenset(eval(s).items())",
        ],
        "shape": "{event_id: minimum_actions_after_that_event}",
        "predicate": "all required events completed and week actions since each completion >= threshold",
        "producer": "not present in the client corpus; server-only. Offline ledger baselines are policy, not original evidence.",
        "verdict": "predicate proven; automatic producer unproven",
    },
    31: {
        "name": "COND_HERO_STAR",
        "class": "MinMaxDictCondition",
        "source": [
            "analysis/original-py-640/com/const.py:3019 COND_HERO_STAR = 31",
            "analysis/decompiled/EventCond.py IDX_TO_TYPE[31] = MinMaxDictCondition",
            "analysis/decompiled/cond_table.py:713-723 MinMaxDictCondition checks min <= value <= max",
            "analysis/original-py-640/com/const.py:1175-1178 HeroStar.MAX_STAR_ORDER = 4",
            "analysis/original-py-640/entity/avatar_attrs/HeroMgrData.py:915-916 starLevel = sl, starOrder = so",
            "analysis/original-py-640/cocos/panels/city_shuzhi_zhiyuan_window.py:79 starLevel * 4 + starOrder",
            "analysis/original-py-640/cocos/panels/activity_212_stage.py:430 starLevel * MAX_STAR_ORDER + starOrder",
            "analysis/original-py-640/cocos/panels/battle_herolist.py:770 same encoding",
            "analysis/original-py-640/cocos/panels/hero_star.py:152 same encoding for star grid position",
        ],
        "shape": "{hero_id: (min_star, max_star)} with star = sl*4+so",
        "predicate": "every listed owned hero has min <= sl*4+so <= max; unowned hero is false",
        "producer": "owned hero sl/so in profile; 4-4 equals 20",
        "verdict": "predicate and producer proven",
    },
    45: {
        "name": "COND_HUOHAIHUA_NUM",
        "class": "IntervalCondition",
        "source": [
            "analysis/original-py-640/com/const.py:3033 COND_HUOHAIHUA_NUM = 45",
            "analysis/decompiled/EventCond.py IDX_TO_TYPE[45] = IntervalCondition",
            "analysis/decompiled/cond_table.py:80-138 IntervalCondition inclusive/exclusive integer interval",
            "analysis/original-py-640/entity/avatar_attrs/HeroMgrData.py:947 huohaihua = initDict.get('hhh', False)",
            "analysis/original-py-640/entity/avatar_members/HeroMgrMember.py:2661-2666 huohaihuaReply sets hero.huohaihua = True",
            "runtime/offline_event_effects.py:664-666 effect 'huohaihua' sets hero['hhh'] = True",
        ],
        "shape": "[min_count,max_count) over the number of owned heroes whose hhh flag is true",
        "predicate": "interval contains the hhh-true owned hero count",
        "producer": "profile hero hhh; missing hhh defaults false exactly as original initFromDict",
        "verdict": "predicate and producer proven; bhrs/banned_heroes is a different mechanic",
    },
    46: {
        "name": "COND_FRIENDLY_50_NUM",
        "class": "IntervalCondition",
        "source": [
            "analysis/original-py-640/com/const.py:3034 COND_FRIENDLY_50_NUM = 46",
            "analysis/decompiled/EventCond.py IDX_TO_TYPE[46] = IntervalCondition",
            "analysis/decompiled/cond_table.py:80-138 IntervalCondition",
            "analysis/original-py-640/entity/avatar_attrs/HeroMgrData.py:471-472 getFriendlyValue returns extraFriendlyValue (ef)",
            "analysis/original-py-640/entity/avatar_attrs/HeroMgrData.py:919 extraFriendlyValue = initDict['ef']",
            "analysis/original-py-640/com/data/cdata/hero_friendly_monster.marshal friendly=50 per hero",
            "analysis/android640-scripts/com/data/cdata/event_condition.marshal event 548 names 1位神器使的认可 with [1,999)",
            "analysis/android640-scripts/com/data/cdata/event_condition.marshal event 552 names 5位神器使的认可 with [5,999)",
        ],
        "shape": "[min_count,max_count) over owned heroes with ef >= 50",
        "predicate": "interval contains the count of owned heroes whose friendly value is at least 50",
        "producer": "profile hero ef",
        "verdict": "predicate and producer proven",
    },
    49: {
        "name": "COND_FATIGUE_UNDER_20_NUM",
        "class": "IntervalCondition",
        "source": [
            "analysis/original-py-640/com/const.py:3037 COND_FATIGUE_UNDER_20_NUM = 49",
            "analysis/decompiled/EventCond.py IDX_TO_TYPE[49] = IntervalCondition",
            "analysis/decompiled/cond_table.py:80-138 IntervalCondition",
            "analysis/original-py-640/entity/avatar_attrs/HeroMgrData.py:917 curFatigueValue = initDict['cf']",
            "analysis/original-py-640/entity/avatar_attrs/HeroMgrData.py:468-469 fatigueValue default source for the max",
            "analysis/android640-scripts/com/data/cdata/event_condition.marshal event 5058 uses [1,999) on 要主动成为活骸",
        ],
        "shape": "[min_count,max_count) over owned heroes with cf < 20",
        "predicate": "interval contains the count of owned heroes whose current fatigue is under 20",
        "producer": "profile hero cf",
        "verdict": "predicate and producer proven",
    },
}


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def base_state(heroes):
    return {
        "story": {"version": 1, "week": 6, "date": 6, "route": "5",
                  "emergency": False, "event_days": {}, "event_action_baselines": {},
                  "week_actions_spent": 0, "banned_heroes": {}},
        "profile": {"heroes": heroes},
        "completed_events": [], "processing_events": [],
        "day": {"stock_day": 6, "actions_spent": 0},
        "conditions": [],
    }


def check(condition, message):
    if not condition:
        raise AssertionError(message)


def star_heroes(required, inside):
    """Build one hero per required id with a star value in/out of every range."""
    heroes = {}
    for hero, bounds in required.items():
        found = None
        for level in range(1, 6):
            for order in range(1, MAX_STAR_ORDER + 1):
                value = level * MAX_STAR_ORDER + order
                ok = bounds[0] <= value <= bounds[1]
                if ok == inside:
                    found = (level, order)
                    break
            if found:
                break
        if found is None:
            return None
        heroes[hero] = {"sl": found[0], "so": found[1]}
    return heroes


def count_heroes(field, value, count):
    return {hero: {field: value} for hero in range(1, count + 1)}


def first_true_count(kind, value, field, good, bad, limit=12):
    for count in range(limit + 1):
        state = base_state(count_heroes(field, good, count))
        if evaluate_offline_condition(kind, value, state) is True:
            return count
    return None


def first_false_count(kind, value, field, good, bad, limit=12):
    for count in range(limit + 1):
        state = base_state(count_heroes(field, good, count))
        if evaluate_offline_condition(kind, value, state) is False:
            return count
    return None


def test_code(code, literal_text, checks):
    if code == 20:
        required = parse_original_condition_literal(literal_text)
        check(isinstance(required, dict) and required, "20 shape")
        state = base_state({})
        check(evaluate_offline_condition(20, literal_text, state) is False,
              "20 incomplete prerequisite is known false")
        completed = base_state({})
        completed["completed_events"] = list(required)
        check(evaluate_offline_condition(20, literal_text, completed) is None,
              "20 completed without baseline must stay unknown")
        exact = dict(required)
        check(evaluate_offline_condition(20, literal_text, state,
              {"condition_values": {20: exact}}) is True, "20 explicit pass")
        below = {key: value - 1 for key, value in required.items()}
        check(evaluate_offline_condition(20, literal_text, state,
              {"condition_values": {20: below}}) is False, "20 explicit fail")
        checks.append(("20", literal_text, "explicit-only"))
        return {"producer": "absent", "explicit_positive": True, "explicit_negative": True}

    if code == 31:
        required = parse_original_condition_literal(literal_text)
        check(isinstance(required, dict) and required, "31 shape")
        good = star_heroes(required, True)
        check(good is not None, "31 satisfiable")
        check(evaluate_offline_condition(31, literal_text, base_state(good)) is True, "31 pass")
        bad = star_heroes(required, False)
        if bad is not None:
            check(evaluate_offline_condition(31, literal_text, base_state(bad)) is False, "31 fail")
        malformed = {hero: dict(record, sl="4") for hero, record in good.items()}
        check(evaluate_offline_condition(31, literal_text, base_state(malformed)) is None, "31 malformed")
        unowned = base_state({hero: {"sl": 4, "so": 4} for hero in (9999,)})
        check(evaluate_offline_condition(31, literal_text, unowned) is False, "31 unowned false")
        checks.append(("31", literal_text, "positive/negative/malformed"))
        return {"positive": True, "negative": bad is not None, "malformed_unknown": True,
                "unowned_false": True}

    if code == 45:
        first = first_true_count(45, literal_text, "hhh", True, False)
        check(first is not None, "45 satisfiable")
        state = base_state(count_heroes("hhh", True, first))
        check(evaluate_offline_condition(45, literal_text, state) is True, "45 pass")
        false_count = first_false_count(45, literal_text, "hhh", True, False)
        check(false_count is not None, "45 falsifiable")
        malformed = base_state({"1": {"hhh": "yes"}})
        check(evaluate_offline_condition(45, literal_text, malformed) is None, "45 malformed")
        banned = base_state({})
        banned["story"]["banned_heroes"] = {"1": True, "2": True, "3": True}
        check(evaluate_offline_condition(45, "[0,1)", banned) is True, "45 ignores ban list")
        checks.append(("45", literal_text, "positive/negative/malformed"))
        return {"positive": True, "negative": True, "malformed_unknown": True,
                "ban_list_not_counted": True}

    if code in (46, 49):
        field, good, bad, predicate = (("ef", 50, 0, ">=50") if code == 46
                                       else ("cf", 0, 100, "<20"))
        first = first_true_count(code, literal_text, field, good, bad)
        check(first is not None, "%d satisfiable" % code)
        state = base_state(count_heroes(field, good, first))
        check(evaluate_offline_condition(code, literal_text, state) is True,
              "%d pass" % code)
        false_count = first_false_count(code, literal_text, field, good, bad)
        check(false_count is not None, "%d falsifiable" % code)
        malformed = base_state({"1": {field: "x"}})
        check(evaluate_offline_condition(code, literal_text, malformed) is None,
              "%d malformed" % code)
        checks.append((str(code), literal_text, "positive/negative/malformed"))
        return {"positive": True, "negative": True, "malformed_unknown": True,
                "threshold": predicate}

    raise AssertionError("unexpected code")


def java_supported_codes():
    import project7_event_auto_trigger_candidate as producer
    return set(producer.ENGINE_SUPPORTED)


def emergency_audit(condition, content):
    checked = 0
    mismatches = []
    for event, row in content.items():
        if not row.get("isAutoTriggerEvent"):
            continue
        checked += 1
        raw = condition.get(event, {}).get("conds", {}).get(101)
        try:
            declared = bool(int(str(raw).strip())) if raw is not None else False
        except (TypeError, ValueError):
            mismatches.append(event)
            continue
        if declared != bool(row.get("isEmergencyEvent")):
            mismatches.append(event)
    return {"auto_events_checked": checked, "mismatches": mismatches}


def build():
    contract = json.loads((CANDIDATE / "contract-v1.json").read_text(encoding="utf-8"))
    condition = literal(str(CONDITION))
    content = literal(str(CONTENT))
    blocked = [row for row in contract["blocked"]
               if any(code in TARGET_CODES for code in row["codes"])]
    check(len(blocked) == 33, "blocked population changed: %d" % len(blocked))

    grouped = OrderedDict()
    for row in blocked:
        for code in row["codes"]:
            if code in TARGET_CODES:
                grouped.setdefault(code, []).append(row["event"])
    check(dict((code, len(events)) for code, events in grouped.items()) ==
          {20: 17, 45: 6, 46: 6, 31: 3, 49: 1},
          "blocked code groups changed: %r" % {k: len(v) for k, v in grouped.items()})

    literals = {}
    code_results = {}
    checks = []
    for code in TARGET_CODES:
        values = sorted(set(condition[event]["conds"][code] for event in grouped[code]))
        literals[code] = values
        results = []
        for value in values:
            results.append({"value": value, "cases": test_code(code, value, checks)})
        check(results, "no literal for %d" % code)
        code_results[code] = results

    supported_events = sorted(row["event"] for row in blocked
                              if all(code in SEMANTICS_SUPPORTED for code in row["codes"]))
    blocked_events = [{"event": row["event"], "codes": row["codes"],
                       "reason": "no original producer for " + "+".join(
                           str(code) for code in row["codes"] if code in UNPROVEN_PRODUCER)}
                      for row in blocked if row["event"] not in supported_events]
    check(len(supported_events) == 16, "supported count changed")
    check(len(blocked_events) == 17, "blocked count changed")

    engine = java_supported_codes()
    check(not (set(TARGET_CODES) & engine), "fixed manager unexpectedly supports a target code")

    java_host = json.loads((ROOT / "reports/auto-trigger-host-v43.json").read_text(encoding="utf-8"))
    result = {
        "schema": "project7-condition-codes-20-45-46-31-49-v1",
        "scope": "Original640 predicate/fact semantics, Python generic evaluator host, and fixed v43/v44 manager frame; no prepare, D8, APK, device or native action",
        "status": "semantics_proven_16_of_33_java_manager_unsupported",
        "codes": {str(code): ORIGINAL_EVIDENCE[code] for code in TARGET_CODES},
        "literals": {str(code): literals[code] for code in TARGET_CODES},
        "code_host_results": {str(code): code_results[code] for code in TARGET_CODES},
        "counts": {
            "target_blocked_events": len(blocked),
            "semantics_supported_events": len(supported_events),
            "unproven_producer_events": len(blocked_events),
            "java_manager_supported_events": 0,
            "candidate_rows": contract["counts"]["candidate_rows"],
            "candidate_blocked_events": contract["counts"]["blocked_events"],
            "candidate_unproven_events": contract["counts"]["unproven_events"],
            "candidate_fallback_events": contract["counts"]["fallback_events"],
        },
        "semantics_supported_events": supported_events,
        "unsupported_events": blocked_events,
        "evaluator": {
            "path": "runtime/offline_conditions.py",
            "sha256": sha(ROOT / "runtime/offline_conditions.py"),
            "api": "evaluate_offline_condition / evaluate_offline_trigger",
            "supported_target_codes": sorted(SEMANTICS_SUPPORTED),
            "explicit_only_target_codes": sorted(UNPROVEN_PRODUCER),
        },
        "java_owner": {
            "class": "com.project7.localmanager.LocalStoryConditions",
            "manager": "analysis/project7/story-city-coc-gateway-v36/manager-translated-frames.jar",
            "manager_sha256": sha(ROOT / "analysis/project7/story-city-coc-gateway-v36/manager-translated-frames.jar"),
            "supported_set_excludes": sorted(TARGET_CODES),
            "integration": "fixed frame has no source/build input for these codes; no asset row may be staged",
        },
        "java_fixed_frame_host": {
            "report": "reports/auto-trigger-host-v43.json",
            "status": java_host.get("status"),
            "checks": java_host.get("checks"),
            "candidate_rows": java_host.get("candidate_rows"),
            "blocked_events": java_host.get("blocked_events"),
            "manager": java_host.get("manager"),
            "manager_sha256": java_host.get("hashes", {}).get("manager"),
        },
        "trigger_integration": {
            "safe": False,
            "staged_rows": 0,
            "reason": "the fixed manager frame returns unsupported for 20/31/45/46/49; semantic support alone must not enable rows",
        },
        "emergency_guard": emergency_audit(condition, content),
        "checks": len(checks),
        "host_checks": [{"code": code, "literal": value, "cases": kind}
                        for code, value, kind in checks],
        "commands": {
            "semantics_host": ".venv/bin/python runtime/android_event_auto_trigger/verify_condition_codes.py --write",
            "unit": ".venv/bin/python -m unittest discover -s tests -p test_offline_conditions.py",
            "guard_unit": ".venv/bin/python -m unittest discover -s tests -p test_event_auto_trigger_candidate.py",
            "candidate": ".venv/bin/python tools/project7_event_auto_trigger_candidate.py --check",
            "java_fixed_frame": ".venv/bin/python runtime/android_event_auto_trigger/verify.py",
        },
        "hashes": {
            "runtime/offline_conditions.py": sha(ROOT / "runtime/offline_conditions.py"),
            "tests/test_offline_conditions.py": sha(ROOT / "tests/test_offline_conditions.py"),
            "tests/test_event_auto_trigger_candidate.py": sha(ROOT / "tests/test_event_auto_trigger_candidate.py"),
            "tools/project7_event_auto_trigger_candidate.py": sha(ROOT / "tools/project7_event_auto_trigger_candidate.py"),
            "event_condition": sha(CONDITION),
            "event_content": sha(CONTENT),
            "candidate_asset": contract["asset_sha256"],
        },
        "no_prepare_no_d8_no_apk_no_native": True,
    }
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--evidence", type=Path, default=EVIDENCE)
    args = parser.parse_args()
    result = build()
    encoded = json.dumps(result, indent=2, sort_keys=True, ensure_ascii=True) + "\n"
    if args.write:
        args.evidence.write_text(encoded, encoding="utf-8")
    print("PASS %d condition-code checks: target=%d semantics-supported=%d java-manager-supported=%d unproven-producer=%d"
          % (result["checks"], result["counts"]["target_blocked_events"],
             result["counts"]["semantics_supported_events"],
             result["counts"]["java_manager_supported_events"],
             result["counts"]["unproven_producer_events"]))


if __name__ == "__main__":
    main()
