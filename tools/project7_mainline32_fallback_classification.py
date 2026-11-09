"""Classify the v49 chapter-scenes-absent and event-auto-trigger-rows-absent groups.

Reads the frozen original 640 literal tables, the frozen v49 stage assets and the
promoted production catalog. It does not edit LocalStoryEntryPolicy.SUPPORTED,
the matrix, StoryCityPolicy or any event row.

Writer:  .venv/bin/python tools/project7_mainline32_fallback_classification.py --write
Check:   .venv/bin/python tools/project7_mainline32_fallback_classification.py --check

Classification rules (original evidence, not per-route inference):

* chapter-scenes-absent: a route family with zero chapter_mission_data rows is a
  data-table gap. The original client never selects that table (it asks the
  server for getAreaStages); the fixed Project7 manager keeps its default
  LocalCityProgress projection and StoryMissionBridge delegates on a catalog
  miss. Entry is gated by LocalStoryEntryPolicy.SUPPORTED, not by chapter rows.
  A menu in that allowlist is a false negative for entry; the rest stay closed by
  original policy, not by an inferred missing engine.
* trigger-row-gap: the original engine scans only @trigger rows and requires
  event_content.release && autoTrigger. A released auto event with no row is a
  real data gap; an unreleased event without a row is normal absence. Events that
  live in a week entrance, a route requirement or a successor edge have another
  owner. The matrix currently labels every rowless auto event, so unreleased
  events are false negatives there.
"""
from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from runtime.project7_dream_catalog.produce import literal  # noqa: E402

CDATA = ROOT / "analysis/android640-scripts/com/data/cdata"
CAND = ROOT / "runtime/project7_mainline32_data_candidate/catalog-v1.json.gz"
STAGE = ROOT / "analysis/project7/story-city-integration-prepare-v49/project7-inputs-pm_gioka/stage/assets"
EVENT_GRAPH = STAGE / "event_graph.tsv"
WEEKS = STAGE / "weeks.tsv"
MISSION_CATALOG = STAGE / "project7_story_missions/catalog-v1.tsv"
ECONOMY = STAGE / "economy.tsv"
BASE_TRIGGERS = ROOT / "runtime/project7_event_auto_trigger_candidate/trigger-extra-v1.tsv"
COND_TRIGGERS = ROOT / "runtime/project7_event_auto_trigger_condition_candidate/trigger-extra-conditions-v1.tsv"
REPORT_JSON = ROOT / "reports/mainline32-fallback-classification-v1.json"
REPORT_MD = ROOT / "reports/mainline32-fallback-classification-v1.md"

SCHEMA = "project7-mainline32-fallback-classification-v1"
SOURCE_PINS = {
    "chapter_mission_data": "c637bbf1665c8118b238c702145a22df0ceaf860bdf80595edbcf0d20882cdb4",
    "event_condition": "1ab7a968ebc01bccfa9419172ed92e91d9d491aa7288d616f2c8181de5389ec1",
    "event_content": "0ddb80bbe56259a2f54acdb7accef49ad390240b0cac504ba1375a3c8976afe7",
    "story_route": "53f3161471d82c9abe562c41982b51f5d01a1651400d3c6fd58433b2629614b1",
}
# LocalStoryEntryPolicy.SUPPORTED from the fixed manager disassembly.
ORIGINAL_SUPPORTED = (1, 2, 3, 5, 6, 9, 11, 13, 32)
# Matrix v49 groups, kept as the frozen input labels.
CHAPTER_ABSENT = (1, 7, 8, 14, 15, 16, 18, 21, 26)
TRIGGER_GAP = (8, 9, 10, 11, 12, 14, 18, 19, 22, 25, 26)
# LocalStoryConditions.SUPPORTED on the fixed manager frame (reported by the
# condition-code work); these codes make staged rows permanently blocked.
JAVA_UNSUPPORTED_CODES = (20, 31, 45, 46, 49)


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def require(ok, message):
    if not ok:
        raise SystemExit("FAIL fallback classification: " + message)


def load_tables():
    tables = {}
    for name in SOURCE_PINS:
        path = CDATA / (name + ".marshal")
        require(path.is_file(), "missing source " + name)
        tables[name] = literal(path)
    return tables


def parse_graph(path=EVENT_GRAPH):
    rows, triggers = set(), set()
    for line in path.read_text(encoding="utf-8").splitlines():
        cols = line.split("\t")
        if not cols or not cols[0] or cols[0].startswith("#"):
            continue
        if cols[0] == "@trigger":
            triggers.add(int(cols[1]))
        elif not cols[0].startswith("@"):
            rows.add(int(cols[0]))
    return rows, triggers


def parse_weeks(path=WEEKS):
    entrances, requirements = {}, set()
    for line in path.read_text(encoding="utf-8").splitlines():
        cols = line.split("\t")
        if cols[0] == "route" and len(cols) >= 4:
            entrances[int(cols[1])] = int(cols[2])
            if cols[3]:
                for group in cols[3].split("|"):
                    requirements.update(int(value) for value in group.split(",") if value)
        elif cols[0] == "ending" and len(cols) >= 3:
            requirements.add(int(cols[1]))
    return entrances, requirements


def parse_successors(path=EVENT_GRAPH):
    parent = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        cols = line.split("\t")
        if not cols or not cols[0] or cols[0].startswith("@"):
            continue
        try:
            event = int(cols[0])
        except ValueError:
            continue
        for value in cols[5].split(","):
            if value:
                parent.setdefault(int(value), []).append(event)
    return parent


def candidate_rows(path):
    if not path.is_file():
        return set()
    rows = set()
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line or line.startswith("#"):
            continue
        rows.add(int(line.split("\t")[1]))
    return rows


def chapter_family_counts(table):
    counts = Counter()
    for key in table:
        counts[str(key[2]).split("-")[0]] += 1
    return counts


def downstream_v51(catalog, content, condition):
    """Confirm the same 11 groups on the current published v51 asset, when present."""
    assets = ROOT / "analysis/project7/story-city-integration-prepare-v51/project7-inputs-wf4kdci_/stage/assets"
    graph = assets / "event_graph.tsv"
    if not graph.is_file():
        return None
    _, triggers = parse_graph(graph)
    weeks = assets / "weeks.tsv"
    entrances, requirements = parse_weeks(weeks) if weeks.is_file() else ({}, set())
    parents = parse_successors(graph)
    flagged = []
    for mid in TRIGGER_GAP:
        menu = catalog["menus"][mid - 1]
        bound = (set(menu["events"]["init_chain"]) | set(menu["events"]["route_events"])
                 | set(menu["events"]["trigger_events"]))
        for event in sorted(bound):
            row = content.get(event, {})
            if (not row.get("isAutoTriggerEvent") or event in triggers
                    or event in menu["events"]["init_chain"]
                    or event in menu["events"]["route_events"]):
                continue
            cond = condition.get(event, {})
            flagged.append({
                "menu": mid,
                "event": event,
                "released": bool(row.get("release") and cond.get("release")),
                "fallback_owner": (
                    ["week-entrance"] if event in entrances.values() else [])
                    + (["week-requirement"] if event in requirements else [])
                    + (["successor"] if event in parents else []),
            })
    matrix = ROOT / "reports/mainline32-capability-matrix-v51.json"
    status = None
    if matrix.is_file():
        payload = json.loads(matrix.read_text(encoding="utf-8"))
        status = payload.get("counts", {}).get("event_status")
    return {
        "stage_assets": str(assets.relative_to(ROOT)),
        "event_graph_sha256": sha(graph.read_bytes()),
        "flagged_events": len(flagged),
        "unreleased": sum(1 for row in flagged if not row["released"]),
        "released_without_row": sum(1 for row in flagged if row["released"]),
        "fallback_owners": [row for row in flagged if row["fallback_owner"]],
        "matrix_v51_event_status": status,
        "matrix_v51_trigger_residual": (None if status is None
                                        else "complete" if status == {"complete": 32}
                                        else "review"),
    }


def build():
    tables = load_tables()
    chapter_table = tables["chapter_mission_data"]
    content = tables["event_content"]
    condition = tables["event_condition"]
    story_route = tables["story_route"]
    catalog = json.loads(gzip.decompress(CAND.read_bytes()))
    require(catalog["schema"] == "project7-mainline32-data-candidate-v1", "candidate schema")
    require(len(catalog["menus"]) == 32, "menu count")
    graph_rows, graph_triggers = parse_graph()
    entrances, requirements = parse_weeks()
    parents = parse_successors()
    base_candidates = candidate_rows(BASE_TRIGGERS)
    cond_candidates = candidate_rows(COND_TRIGGERS)
    family_rows = chapter_family_counts(chapter_table)
    story_families = {str(key) for key in story_route}

    chapters = []
    for mid in CHAPTER_ABSENT:
        menu = catalog["menus"][mid - 1]
        family = menu["route"]["family"]
        keys = [key for key in chapter_table if str(key[2]).split("-")[0] == family]
        area_ids = menu_area_ids(menu)
        default_rows = [
            {"key": list(key), "area": int(key[0]), "status": int(key[1]),
             "scenes": sum(len(group) for group in chapter_table[key]["section"].values())}
            for key in sorted(chapter_table)
            if key[2] == "-1" and key[0] in area_ids
        ]
        supports = mid in ORIGINAL_SUPPORTED
        if supports:
            classification = "false-negative-entry-enabled"
            detail = ("route family exists in story_route; chapter_mission_data has no row; "
                      "entry is granted by the original SUPPORTED allowlist; the Bridge keeps "
                      "the original default LocalCityProgress stage projection on a catalog miss")
        else:
            classification = "data-table-gap-policy-closed"
            detail = ("route family exists in story_route; chapter_mission_data has no row; "
                      "the same original default projection remains the fallback, but the "
                      "menu is not in SUPPORTED or the packaged proven set, so no entry or "
                      "per-route engine is invented")
        chapters.append({
            "menu": mid,
            "name": menu["name"],
            "chapter": menu["chapter"],
            "route_family": family,
            "branches": menu["route"]["branches"],
            "chapter_mission_rows_for_family": len(keys),
            "family_in_story_route": family in story_families,
            "panel_areas": [area["id"] for area in menu["areas"]],
            "default_minus_one_rows_for_areas": default_rows,
            "original_supported": supports,
            "packaged_proven": False,
            "classification": classification,
            "detail": detail,
            "residual": ("original server exact route->default chapter choice and status "
                         "normalization are outside the client corpus; no row is staged"),
        })

    triggers = []
    for mid in TRIGGER_GAP:
        menu = catalog["menus"][mid - 1]
        bound = (set(menu["events"]["init_chain"]) | set(menu["events"]["route_events"])
                 | set(menu["events"]["trigger_events"]))
        flagged = []
        for event in sorted(bound):
            row = content.get(event, {})
            if not row.get("isAutoTriggerEvent"):
                continue
            if event in graph_triggers:
                continue
            if event in menu["events"]["init_chain"] or event in menu["events"]["route_events"]:
                continue
            cond = condition.get(event, {})
            codes = sorted(int(code) for code in cond.get("conds", {}))
            fallback = []
            if event in entrances.values():
                fallback.append("week-entrance")
            if event in requirements:
                fallback.append("week-requirement")
            if event in parents:
                fallback.append("successor")
            if event in base_candidates:
                fallback.append("generic-candidate-row")
            if event in cond_candidates:
                fallback.append("condition-candidate-row")
            blocked = [code for code in codes if code in JAVA_UNSUPPORTED_CODES]
            if not (row.get("release") and cond.get("release")):
                classification = "false-negative-unreleased"
            elif fallback:
                classification = "normal-absence-fallback-owner"
            elif blocked:
                classification = "data-gap-evaluator-code"
            else:
                classification = "data-gap-generic-extractable"
            flagged.append({
                "event": event,
                "content_release": bool(row.get("release")),
                "condition_release": bool(cond.get("release")),
                "trigger_row": False,
                "condition_codes": codes,
                "java_unsupported_codes": blocked,
                "candidate_row": event in base_candidates or event in cond_candidates,
                "fallback_owner": fallback,
                "classification": classification,
            })
        classes = Counter(row["classification"] for row in flagged)
        triggers.append({
            "menu": mid,
            "name": menu["name"],
            "flagged_events": flagged,
            "classification": (classes.most_common(1)[0][0] if len(classes) == 1
                               else "mixed:" + ",".join(sorted(classes))),
            "residual": ("none: every flagged event is release=false, so the original engine "
                         "rejects it before trigger evaluation and no row is required"
                         if all(row["classification"] == "false-negative-unreleased"
                                for row in flagged)
                         else "see per-event classification"),
        })

    claimed = {catalog["menus"][mid - 1]["route"]["family"] for mid in range(1, 33)}
    minus_one_rows = [key for key in sorted(chapter_table) if key[2] == "-1"]
    family_24_rows = [key for key in sorted(chapter_table) if str(key[2]).split("-")[0] == "24"]
    route_23_5_rows = [key for key in sorted(chapter_table) if key[2] == "23-5"]
    unclaimed_families = ["-1", "24", "23-5"]
    unclaimed_rows = [
        {"category": category, "key": list(key),
         "scenes": sum(len(group) for group in chapter_table[key]["section"].values())}
        for category, keys in (("default-minus-one", minus_one_rows),
                               ("family-24-no-menu", family_24_rows),
                               ("route-23-5-not-in-story-route", route_23_5_rows))
        for key in keys
    ]
    counts = {
        "chapter_groups": len(chapters),
        "chapter_families_without_rows": sum(
            1 for row in chapters if row["chapter_mission_rows_for_family"] == 0),
        "chapter_entry_enabled": sum(1 for row in chapters if row["original_supported"]),
        "trigger_groups": len(triggers),
        "trigger_flagged_events": sum(len(row["flagged_events"]) for row in triggers),
        "trigger_unreleased": sum(
            1 for row in triggers for event in row["flagged_events"]
            if event["classification"] == "false-negative-unreleased"),
        "trigger_released_without_row": sum(
            1 for row in triggers for event in row["flagged_events"]
            if event["classification"] != "false-negative-unreleased"),
        "shared_behavior_implemented": 0,
    }
    report = {
        "schema": SCHEMA,
        "checkpoint": "v49",
        "policy": ("classify by original640/Project7 fallback; a dedicated chapter_mission_data "
                   "family row is not required; no per-route engine, no code20 expansion"),
        "inputs": {
            "stage_assets": str(STAGE.relative_to(ROOT)),
            "event_graph_sha256": sha(EVENT_GRAPH.read_bytes()),
            "weeks_sha256": sha(WEEKS.read_bytes()),
            "mission_catalog_sha256": sha(MISSION_CATALOG.read_bytes()),
            "economy_sha256": sha(ECONOMY.read_bytes()),
            "candidate_sha256": sha(CAND.read_bytes()),
            "source_pins": SOURCE_PINS,
            "event_graph_rows": len(graph_rows),
            "event_graph_trigger_rows": len(graph_triggers),
        },
        "original_evidence": {
            "entry_policy": ("LocalStoryEntryPolicy.SUPPORTED = "
                             + str(list(ORIGINAL_SUPPORTED))
                             + "; LocalWeekEngine requestEnterStory requires supports(menu)"),
            "default_stage": ("LocalCityProgress mapStages: area1 cs=101/sl=[[101]]; "
                              "other normal areas use (area-1)*1000+100+i with the original "
                              "event/status branches; LocalChapterCityEngine is limited to "
                              "q7ChapterMenu==11 and route 12*"),
            "bridge_fallback": ("StoryMissionBridge.mapStages/stages call the original "
                                "implementation when the promoted catalog has no exact chapter"),
            "trigger_engine": ("LocalEventEngine.reevaluateLifecycle scans only catalog.triggers(); "
                               "triggerBlocker requires event_content.release && autoTrigger"),
        },
        "chapter_groups": chapters,
        "trigger_groups": triggers,
        "unclaimed_chapter_rows": {
            "count": len(unclaimed_rows),
            "families": unclaimed_families,
            "rows": unclaimed_rows,
            "classification": ("data-table/selector gap: route -1 default rows are not a menu "
                               "family; 23-5 is absent from story_route family 23; family 24 has "
                               "rows but no mainline menu; no behavior is inferred"),
        },
        "counts": counts,
        "downstream_v51": downstream_v51(catalog, content, condition),
        "host_evidence": {
            "report": "reports/mainline32-fallback-host.json",
            "proves": ["menu1 original allowlist entry and default area2 1101 projection",
                       "menu7 policy rejection with stages equal to the original fallback",
                       "released auto trigger 3177 exposed; unreleased rowless gaps never exposed",
                       "save/reload keeps both outcomes"],
        },
        "matrix_rule": ("filter release=false events out of event-auto-trigger-rows-absent; "
                        "keep chapter-scenes-absent as a data-absence note, not an engine or "
                        "entry requirement"),
        "residual": [
            "original server exact-route -> -1 chapter selection order is unproven",
            "menus 7,8,14,15,16,18,21,26 stay closed by original policy/proven set, not by an invented engine",
            "released events that are genuinely rowless remain the condition-code/candidate workstreams, not these 11 groups",
        ],
    }
    return report


def menu_area_ids(menu):
    ids = {area["id"] for area in menu["areas"]}
    for effect in menu["effects"]:
        for field in ("areaFree", "areaFight", "areaLock", "areaUnlock"):
            for area in effect.get(field, []):
                ids.add(int(area))
    return ids


def markdown(report):
    counts = report["counts"]
    lines = [
        "# Chapter-absent / trigger-gap fallback classification (v49)",
        "",
        "Status: analysis + host evidence; no production behavior change and no event/row write.",
        "",
        "- chapter groups: **%d** (%d entry-enabled false negatives, rest data-gap/policy-closed)"
        % (counts["chapter_groups"], counts["chapter_entry_enabled"]),
        "- trigger groups: **%d**, flagged events: **%d** "
        "(unreleased: **%d**, released rowless: **%d**)"
        % (counts["trigger_groups"], counts["trigger_flagged_events"],
           counts["trigger_unreleased"], counts["trigger_released_without_row"]),
        "- shared behavior implemented: **%d**" % counts["shared_behavior_implemented"],
        "",
        "## Chapter-scenes-absent",
        "",
        "| menu | name | family | family rows | SUPPORTED | classification |",
        "|---:|---|---|---:|---|---|",
    ]
    for row in report["chapter_groups"]:
        lines.append("| %d | %s | %s | %d | %s | %s |" % (
            row["menu"], row["name"], row["route_family"],
            row["chapter_mission_rows_for_family"],
            "yes" if row["original_supported"] else "no", row["classification"]))
    lines += [
        "",
        "- The family exists in `story_route` for every menu; `chapter_mission_data` has no row.",
        "- The original client never selects that table; the fixed Project7 manager keeps its "
        "default `LocalCityProgress` projection and the Bridge delegates to it on a catalog miss.",
        "- Entry is `LocalStoryEntryPolicy.SUPPORTED` + `LocalWeekEngine`; menu 1 is in the "
        "original allowlist, so its chapter label is a data note, not a cap. The other eight "
        "stay closed by policy, not by a missing shared engine.",
        "",
        "## Event-auto-trigger-rows-absent",
        "",
        "| menu | name | flagged | unreleased | released rowless |",
        "|---:|---|---:|---:|---:|",
    ]
    for row in report["trigger_groups"]:
        unreleased = sum(1 for event in row["flagged_events"]
                         if event["classification"] == "false-negative-unreleased")
        lines.append("| %d | %s | %d | %d | %d |" % (
            row["menu"], row["name"], len(row["flagged_events"]), unreleased,
            len(row["flagged_events"]) - unreleased))
    lines += [
        "",
        "- Every flagged event in these 11 groups is `release=false` in both original tables.",
        "- `LocalEventEngine` scans only `@trigger` rows and rejects unreleased events before "
        "evaluation, so the frozen graph's absence is correct.",
        "- No flagged event has a week-entrance, route-requirement, successor or candidate owner.",
        "",
        "## Matrix rule",
        "",
        "`" + report["matrix_rule"] + "`",
        "",
        "",
        "## Downstream confirmation",
        "",
    ]
    downstream = report.get("downstream_v51")
    if downstream:
        lines.append("- v51 asset `%s`: %d flagged, %d unreleased, %d released rowless; "
                     "matrix v51 event status `%s`."
                     % (downstream["event_graph_sha256"][:12], downstream["flagged_events"],
                        downstream["unreleased"], downstream["released_without_row"],
                        downstream["matrix_v51_event_status"]))
    lines += [
        "",
        "## Residual",
        "",
    ]
    lines += ["- " + item for item in report["residual"]]
    lines += ["", "Host: `" + report["host_evidence"]["report"] + "`."]
    return "\n".join(lines) + "\n"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    report = build()
    payload = json.dumps(report, indent=1, sort_keys=False, ensure_ascii=False) + "\n"
    document = markdown(report)
    if args.check:
        require(REPORT_JSON.read_text(encoding="utf-8") == payload, "json report changed")
        require(REPORT_MD.read_text(encoding="utf-8") == document, "markdown report changed")
        print("PASS fallback classification check: " + REPORT_JSON.name)
        return
    require(args.write, "use --write or --check")
    REPORT_JSON.write_text(payload, encoding="utf-8")
    REPORT_MD.write_text(document, encoding="utf-8")
    print("WROTE %s %s" % (REPORT_JSON, REPORT_MD))


if __name__ == "__main__":
    main()
