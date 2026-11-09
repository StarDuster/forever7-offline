"""Derive the v49 32-menu capability dependency matrix.

Reads the frozen original 640 literal tables, the promoted production mission
catalog/economy rows and the frozen v49 story/event assets. Emits the report
pair and the small proved-entry asset consumed by StoryMainlineEntry. It never
edits LocalStoryEntryPolicy.SUPPORTED or writes per-event rows.

Writer: .venv/bin/python tools/project7_mainline32_capability_matrix.py --write
Verifier: .venv/bin/python tools/project7_mainline32_capability_matrix.py --check
"""
from __future__ import annotations
import _bootstrap  # noqa: E402,F401

import argparse
import base64
import gzip
import hashlib
import json
import re
import struct
import sys
from collections import Counter, OrderedDict, defaultdict
from pathlib import Path

from _bootstrap import ROOT
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from project7_dream_catalog.produce import literal  # noqa: E402

CDATA = ROOT / "analysis/android640-scripts/com/data/cdata"
CAND = ROOT / "offline/current/data/project7_mainline32_data_candidate/catalog-v1.json.gz"
STAGE = ROOT / "analysis/project7/story-city-integration-prepare-v61/project7-inputs-m_ee5jmd/stage/assets"
EVENT_GRAPH = STAGE / "event_graph.tsv"
WEEKS = STAGE / "weeks.tsv"
MISSION_CATALOG = STAGE / "project7_story_missions/catalog-v1.tsv"
ECONOMY = STAGE / "economy.tsv"
ECONOMY_EXTRA = ROOT / "offline/current/data/project7_story_mission_catalog/economy-extra.tsv"
ENTRY_ASSET = ROOT / "offline/current/java/android_story_shared/catalog/mainline32-entry-v1.json"
STAGE_ENTRY_ASSET = STAGE / "project7_story_shared/mainline32-entry-v1.json"
REPORT_JSON = ROOT / "reports/mainline32-capability-matrix-v61.json"
REPORT_MD = ROOT / "reports/mainline32-capability-matrix-v61.md"

SCHEMA = "project7-mainline32-entry-v1"
REPORT_SCHEMA = "project7-mainline32-capability-matrix-v61"
PROVEN = (4, 12, 17, 19, 20, 22, 23, 24, 25, 27, 28, 29, 30, 31)
DEFAULT_PROVEN = (7, 8, 14, 15, 16, 18, 21, 26)
# Entry-proven menus whose city effects stay with an existing dedicated owner.
DEDICATED_CITY = {12, 25}
# Default-chapter menus whose route-only effects now have landed Gateway host proof.
ROUTE_EFFECTS_PROVEN = (8, 14, 15, 21, 26)
DEFAULT_ROUTE = "1"
DEFAULT_SCENE = 101
DEFAULT_AREA = 1
ORIGINAL_SUPPORTED = (1, 2, 3, 5, 6, 9, 11, 13, 32)
DEDICATED = {2, 3, 5, 6, 10, 11, 12, 13, 32}
CITY_OWNER = {25}
AREA_FIELDS = ("areaFree", "areaFight", "areaLock", "areaUnlock")
HERO_EFFECT_FIELDS = ("cineLockHeroes", "banHeroes", "recoverBanHeroes")
SOURCE_ONLY_FIELDS = ("areaStrike", "destroyAreaPatrolBuild")
EXTERNAL_EFFECT_FIELDS = ("buildBuilding",)
SOURCE_PINS = {
    "mainline_score_info": "dbab43659cd8a4c2983bc3ae46b340465b51b7b227c472523e4ac7d89a79ccff",
    "chapter_mission_data": "c637bbf1665c8118b238c702145a22df0ceaf860bdf80595edbcf0d20882cdb4",
    "event_condition": "1ab7a968ebc01bccfa9419172ed92e91d9d491aa7288d616f2c8181de5389ec1",
    "event_content": "0ddb80bbe56259a2f54acdb7accef49ad390240b0cac504ba1375a3c8976afe7",
    "mainline_mutex": "703e64835f5235d6c2d79fd5b7b1513b44f99eebbfcb0a2c1582efee4f9bd350",
    "mission": "2019aab0289ffdac6aacde82b21cd283ef0c8d8afb6bb264d087e8cde262390f",
}
EXPECTED_PINS = {
    "event_graph": "dabe8f6ed779137cdcad221ee7a4867f552a0c8ef591b40c6af9e7bf9aa0f2bb",
    "mission_catalog": "ce54f931f6d462d0c6fabb1f03dabf47ddc54780d89e3ec78fe21d9a6d7ef0d9",
    "economy": "4c504ae5fc5a431fb6eeffd6fb48df614bbfa00f0c2a8a949e23d1cd4363ed9a",
}


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def require(ok, message):
    if not ok:
        raise SystemExit("FAIL mainline32 matrix: " + message)


def load_tables():
    for name, digest in SOURCE_PINS.items():
        path = CDATA / (name + ".marshal")
        require(sha(path.read_bytes()) == digest, "source pin " + name)
    tables = {name: literal(CDATA / (name + ".marshal")) for name in SOURCE_PINS}
    return tables


def parse_graph():
    rows = set()
    triggers = set()
    for line in EVENT_GRAPH.read_text(encoding="utf-8").splitlines():
        cols = line.split("\t")
        if not cols or not cols[0] or cols[0].startswith("#"):
            continue
        if cols[0] == "@trigger":
            triggers.add(int(cols[1]))
        elif cols[0].startswith("@"):
            continue
        else:
            rows.add(int(cols[0]))
    return rows, triggers


def _bson_document(data):
    """Minimal reader for the frozen @cityEffect BSON payloads (int/string/array/doc)."""
    index = 4
    out = {}
    while index < len(data) - 1:
        kind = data[index]
        index += 1
        end = data.index(b"\x00", index)
        key = data[index:end].decode("utf-8")
        index = end + 1
        if kind == 0x10:
            out[key] = struct.unpack("<i", data[index:index + 4])[0]
            index += 4
        elif kind == 0x12:
            out[key] = struct.unpack("<q", data[index:index + 8])[0]
            index += 8
        elif kind == 0x02:
            size = struct.unpack("<i", data[index:index + 4])[0]
            out[key] = data[index + 4:index + 3 + size].decode("utf-8")
            index += 4 + size
        elif kind in (0x03, 0x04):
            size = struct.unpack("<i", data[index:index + 4])[0]
            out[key] = _bson_document(data[index:index + size])
            index += size
        else:
            raise SystemExit("FAIL mainline32 matrix: unsupported cityEffect BSON type %d" % kind)
    return out


def parse_city_effects():
    effects = {}
    for line in EVENT_GRAPH.read_text(encoding="utf-8").splitlines():
        cols = line.split("\t")
        if cols[0] == "@cityEffect" and len(cols) >= 3:
            effects[int(cols[1])] = _bson_document(base64.b64decode(cols[2]))
    return effects


def parse_weeks():
    routes = {}
    endings = defaultdict(list)
    for line in WEEKS.read_text(encoding="utf-8").splitlines():
        cols = line.split("\t")
        if cols[0] == "route" and len(cols) >= 4:
            requires = []
            if cols[3]:
                requires = [[int(v) for v in group.split(",")] for group in cols[3].split("|")]
            routes[int(cols[1])] = {"init": int(cols[2]), "requires": requires}
        elif cols[0] == "ending" and len(cols) >= 5:
            endings[int(cols[2])].append({
                "event": int(cols[1]), "ending": int(cols[2]),
                "cg": int(cols[3]), "flag": int(cols[4]),
            })
    return routes, endings


def parse_catalog():
    c_keys, m_scenes, g_scenes, success = set(), set(), set(), {}
    for line in MISSION_CATALOG.read_text(encoding="utf-8").splitlines():
        row = line.split("\t")
        if row[0] == "C":
            c_keys.add((int(row[1]), row[3], int(row[2]), int(row[4])))
        elif row[0] == "S":
            success[int(row[1])] = [int(v) for v in row[2].split(",")]
    for path in (ECONOMY, ECONOMY_EXTRA):
        if not path.is_file():
            continue
        for line in path.read_text(encoding="utf-8").splitlines():
            if not line or line.startswith("#"):
                continue
            row = line.split("\t")
            if row[0] == "M":
                m_scenes.add(int(row[1]))
            elif row[0] == "G":
                g_scenes.add(int(row[1]))
    return c_keys, m_scenes, g_scenes, success


def effect_fields(effects):
    out = OrderedDict()
    for row in effects:
        for field in AREA_FIELDS:
            if field in row:
                ids = out.setdefault(field, set())
                ids.update(int(v) for v in row[field])
    return OrderedDict((field, sorted(ids)) for field, ids in out.items())


def classify_chapters(menu, catalog, production_c):
    chapter_rows = catalog["chapters"]
    normal = [row for row in chapter_rows if row["normal_c_row_compatible"]]
    descriptors = [row for row in chapter_rows if not row["normal_c_row_compatible"]]
    promoted = [row for row in normal if (row["area"], row["route"], row["status"], row["special"]) in production_c]
    if menu in DEDICATED:
        return "dedicated-owner", len(normal), len(promoted), len(descriptors)
    if not chapter_rows:
        return "absent", 0, 0, 0
    if len(promoted) == len(normal):
        return "promoted", len(normal), len(promoted), len(descriptors)
    if promoted:
        return "partial", len(normal), len(promoted), len(descriptors)
    return "missing", len(normal), len(promoted), len(descriptors)


def build():
    tables = load_tables()
    catalog = json.loads(gzip.decompress(CAND.read_bytes()))
    require(catalog["schema"] == "project7-mainline32-data-candidate-v1", "candidate schema")
    require(len(catalog["menus"]) == 32, "menu count")
    require([m["id"] for m in catalog["menus"]] == list(range(1, 33)), "menu ids")
    graph_rows, graph_triggers = parse_graph()
    city_effects = parse_city_effects()
    week_routes, week_endings = parse_weeks()
    production_c, economy_m, economy_g, success = parse_catalog()
    conditions = tables["event_condition"]
    content = tables["event_content"]

    menus = []
    for menu in catalog["menus"]:
        mid = menu["id"]
        bound = set(menu["events"]["init_chain"]) | set(menu["events"]["route_events"]) | set(menu["events"]["trigger_events"])
        require(bound <= graph_rows, "event row %d" % mid)
        cond_types = Counter()
        for event in bound:
            row = conditions.get(event)
            if row:
                cond_types.update(row.get("conds", {}).keys())
        missing_triggers = sorted(
            event for event in bound
            if event in conditions and content.get(event, {}).get("isAutoTriggerEvent")
            and content.get(event, {}).get("release") is True
            and event not in graph_triggers
            and event not in menu["events"]["init_chain"]
            and event not in menu["events"]["route_events"]
        )
        chapter_status, normal_c, promoted_c, descriptors = classify_chapters(mid, menu, production_c)
        effects = effect_fields(menu["effects"])
        effect_supported = set(effects) <= set(AREA_FIELDS)
        graph_effect_types = Counter()
        for event in bound:
            graph_effect_types.update(city_effects.get(event, {}).keys())
        source_only_types = Counter()
        for event in bound:
            row = content.get(event, {})
            for field in SOURCE_ONLY_FIELDS:
                if row.get(field):
                    source_only_types[field] += len(row[field])
        hero_effect_rows = sum(count for field, count in graph_effect_types.items() if field in HERO_EFFECT_FIELDS)
        friendly_effect_rows = graph_effect_types.get("friendly", 0)
        unknown_effect_fields = sorted(
            set(graph_effect_types) - set(AREA_FIELDS) - set(HERO_EFFECT_FIELDS)
            - {"friendly", "areaFall", "areaCR7"} - set(EXTERNAL_EFFECT_FIELDS))
        scenes = menu["scenes"]
        missing_m = sorted(scene for scene in scenes if scene not in economy_m)
        gates = sorted(scene for scene in scenes if scene in economy_g)
        ending_ids = sorted({v for group in menu["requires"] for v in group})
        ending_rows = {str(ending): week_endings.get(ending, []) for ending in ending_ids}
        missing_endings = sorted(ending for ending in ending_ids if not week_endings.get(ending))
        week = week_routes.get(mid)
        require(week is not None, "week route row %d" % mid)
        require(week["init"] == menu["init_event"], "week init mismatch %d" % mid)
        require(week["requires"] == menu["requires"], "week requires mismatch %d" % mid)

        if mid in PROVEN or mid in DEFAULT_PROVEN:
            effect_status = ("existing-dedicated" if effects and mid in (9, 10, 11, 12, 25)
                             else "generic-proven")
        elif mid in (9, 10, 11, 12, 25):
            effect_status = "existing-dedicated" if effects else "none"
        elif not effects:
            effect_status = "none"
        elif unknown_effect_fields:
            effect_status = "unknown-effect-type"
        elif missing_triggers or chapter_status in ("absent", "missing") or missing_m:
            effect_status = "reducer-ready-data-blocked"
        else:
            effect_status = "reducer-ready-unproven"

        if mid in ORIGINAL_SUPPORTED:
            entry = "original-allowlist"
        elif mid == 10:
            entry = "scoped-menu10"
        elif mid in PROVEN or mid in DEFAULT_PROVEN:
            entry = "scoped-proven"
        else:
            entry = "closed"

        if mid in PROVEN:
            role = "host-proven representative"
        elif mid in DEFAULT_PROVEN:
            role = "host-proven default chapter"
        elif mid in (9, 10, 11, 12, 25):
            role = "existing special/dedicated owner"
        elif mid in DEDICATED:
            role = "existing dedicated primitive"
        elif chapter_status == "promoted":
            role = "shared table-driven chapter"
        else:
            role = "data-absent; no engine inferred"

        route_only_effects = sorted(
            row["event"] for row in menu["effects"] if row["event"] not in menu["events"]["init_chain"])
        missing_ops = []
        if (chapter_status in ("absent", "missing") and mid not in DEDICATED
                and mid not in DEFAULT_PROVEN):
            missing_ops.append("chapter-scenes-absent")
        if (mid in DEFAULT_PROVEN and route_only_effects
                and mid not in ROUTE_EFFECTS_PROVEN):
            missing_ops.append("default-chapter-route-effects-absent")
        if missing_m:
            missing_ops.append("mission-economy-M-absent")
        if missing_triggers:
            missing_ops.append("event-auto-trigger-rows-absent")
        if effect_status == "unknown-effect-type":
            missing_ops.append("city-effect-type-unknown")
        if missing_endings:
            missing_ops.append("ending-row-absent")
        if chapter_status == "partial":
            missing_ops.append("chapter-route-partial")
        if not missing_ops and entry == "closed":
            missing_ops.append("shared-mechanism-not-host-proven")

        menus.append(OrderedDict((
            ("id", mid),
            ("name", menu["name"]),
            ("chapter", menu["chapter"]),
            ("level", menu["level"]),
            ("init_event", menu["init_event"]),
            ("requires", menu["requires"]),
            ("route_family", menu["route"]["family"]),
            ("branches", menu["route"]["branches"]),
            ("chapter_keys", len(menu["chapters"])),
            ("normal_c_rows", normal_c),
            ("promoted_c_rows", promoted_c),
            ("descriptor_rows", descriptors),
            ("chapter_status", chapter_status),
            ("default_chapter", mid in DEFAULT_PROVEN),
            ("default_stage", {"area": DEFAULT_AREA, "cs": DEFAULT_SCENE}
             if mid in DEFAULT_PROVEN else None),
            ("route_only_effect_events", route_only_effects if mid in DEFAULT_PROVEN else []),
            ("scenes", len(scenes)),
            ("first_scene", scenes[0] if scenes else None),
            ("areas", sorted({row["area"] for row in menu["chapters"]})),
            ("event_bound", len(bound)),
            ("event_condition_types", [int(k) for k in sorted(cond_types)]),
            ("event_condition_counts", {str(k): cond_types[k] for k in sorted(cond_types)}),
            ("event_missing_auto_triggers", missing_triggers),
            ("event_status", "complete" if not missing_triggers else "partial-trigger-rows"),
            ("effect_rows", len(menu["effects"])),
            ("effect_fields", effects),
            ("effect_status", effect_status),
            ("effect_types", dict(sorted(graph_effect_types.items()))),
            ("effect_hero_rows", hero_effect_rows),
            ("effect_friendly_rows", friendly_effect_rows),
            ("effect_unknown_fields", unknown_effect_fields),
            ("source_only_effect_fields", dict(sorted(source_only_types.items()))),
            ("effect_supported", effect_supported),
            ("economy_m_scenes", len([s for s in scenes if s in economy_m])),
            ("economy_m_missing", missing_m),
            ("economy_g_scenes", gates),
            ("economy_status", "complete" if not missing_m else "partial"),
            ("week_entry", week["init"]),
            ("week_requires", week["requires"]),
            ("week_status", "original-LocalWeekEngine"),
            ("ending_required", ending_ids),
            ("ending_rows", ending_rows),
            ("ending_status", "complete" if not missing_endings else "missing"),
            ("success_events", {str(s): success[s] for s in scenes if s in success}),
            ("owner", role),
            ("entry_status", entry),
            ("entry_enabled", entry in ("original-allowlist", "scoped-menu10", "scoped-proven")),
            ("unsupported_operations", missing_ops),
        )))

    require(len(menus) == 32, "matrix menu count")
    enabled = [menu["id"] for menu in menus if menu["entry_enabled"]]
    newly = [menu["id"] for menu in menus if menu["entry_status"] == "scoped-proven"]
    require(newly == sorted(PROVEN + DEFAULT_PROVEN), "proven set")
    require(set(enabled) == set(ORIGINAL_SUPPORTED) | {10} | set(PROVEN) | set(DEFAULT_PROVEN),
            "enabled set")

    residual = Counter()
    for menu in menus:
        residual.update(menu["unsupported_operations"])
    counts = {
        "menus": len(menus),
        "entry_enabled": enabled,
        "newly_enterable": newly,
        "entry_closed": [menu["id"] for menu in menus if not menu["entry_enabled"]],
        "chapter_status": dict(Counter(menu["chapter_status"] for menu in menus)),
        "effect_status": dict(Counter(menu["effect_status"] for menu in menus)),
        "event_status": dict(Counter(menu["event_status"] for menu in menus)),
        "economy_status": dict(Counter(menu["economy_status"] for menu in menus)),
        "unsupported_operations": dict(sorted(residual.items())),
        "menus_without_chapters": [m["id"] for m in menus if m["chapter_status"] == "absent"],
        "menus_with_missing_auto_triggers": [m["id"] for m in menus if m["event_missing_auto_triggers"]],
        "menus_with_missing_economy": [m["id"] for m in menus if m["economy_m_missing"]],
    }
    formerly_missing_owner = [m["id"] for m in menus if m["effect_status"] == "reducer-ready-data-blocked"]
    require(
        all(not m["effect_unknown_fields"] for m in menus),
        "unknown city effect type in scoped source",
    )
    effect_audit = OrderedDict((
        ("conclusion",
         "The former missing-generic-owner label was a co-missing-data false negative: every bound "
         "effect document is one of the area fields, the delegated hero fields, or the "
         "original-private friendly field. No menu carries an unknown effect type."),
        ("area_fields_owned", list(AREA_FIELDS) + ["areaFall", "areaCR7"]),
        ("hero_fields_delegated_to_original", list(HERO_EFFECT_FIELDS)),
        ("friendly_owner", "original private applyFriendly; absent from every scoped/owned menu"),
        ("external_registry_fields", list(EXTERNAL_EFFECT_FIELDS)),
        ("external_registry_owner", "LocalStoryRuleRegistry wenzi-building rule; not a city-reducer field"),
        ("source_only_fields", list(SOURCE_ONLY_FIELDS)),
        ("source_only_consumers", {
            "areaStrike": "LocalStoryRuleRegistry ark-raids rule (original640 manager; route3-1 "
                          "only); not bound to any of the 32 mainline menus",
            "destroyAreaPatrolBuild": "no original640 manager reference in the 468-class manager "
                                      "corpus; data-table column only",
        }),
        ("graph_rows", {
            "published": 851,
            "prior_projection": 855,
            "difference": "4 buildBuilding-only original events (471,5314,6325,10000071) are not "
                          "appended; event2067 buildBuilding is preserved",
        }),
        ("exported_semantics", {
            "areaFall": "exported from original640; StoryCityPolicy sets status 2",
            "areaCR7": "exported from original640; StoryCityPolicy sets core=true and status 4 "
                       "when the current status is 2, otherwise 3",
        }),
        ("source_only_note",
         "judged by original640 consumer necessity, not by frozen graph absence. These columns "
         "appear in original event_content for some menus (1,3,4,9,19,20,22) but no manager "
         "reducer consumes them; the authoritative @cityEffect rows publish the reducer-owned "
         "fields: areaFall/areaCR7 are owned by StoryCityPolicy; destroyAreaPatrolBuild has no "
         "original640 manager consumer; areaStrike belongs to the original ark-raids registry "
         "rule and is absent from all 32 mainline effect rows"),
        ("formerly_missing_generic_owner", formerly_missing_owner),
        ("menus_with_hero_effect_rows", [m["id"] for m in menus if m["effect_hero_rows"]]),
        ("menus_with_friendly_effect_rows", [m["id"] for m in menus if m["effect_friendly_rows"]]),
        ("source_only_rows", {
            str(m["id"]): m["source_only_effect_fields"]
            for m in menus if m["source_only_effect_fields"]
        }),
    ))

    entry_menu = []
    by_id = {menu["id"]: menu for menu in menus}
    for mid in PROVEN:
        menu = by_id[mid]
        first_rows = sorted(
            [row for row in catalog["menus"][mid - 1]["chapters"] if row["normal_c_row_compatible"]],
            key=lambda row: (row["area"], row["route"]))
        require(first_rows, "proven first chapter %d" % mid)
        first = first_rows[0]
        route_key = next((branch for branch in menu["branches"] if branch == first["route"]), first["route"])
        entry_menu.append(OrderedDict((
            ("id", mid),
            ("init", menu["init_event"]),
            ("route", route_key),
            ("family", menu["route_family"]),
            ("first_scene", first["scenes"][0]),
            ("first_area", first["area"]),
            ("chapter_keys", menu["normal_c_rows"]),
            ("scenes", menu["scenes"]),
            ("requires", menu["requires"]),
            ("effects_supported", menu["effect_supported"]),
            ("city_reducer", mid not in DEDICATED_CITY),
            ("effects", menu["effect_fields"]),
        )))
    for mid in DEFAULT_PROVEN:
        menu = by_id[mid]
        require(menu["chapter_status"] == "absent", "default chapter absent %d" % mid)
        require(menu["week_entry"] == menu["init_event"], "default week entrance %d" % mid)
        entry_menu.append(OrderedDict((
            ("id", mid),
            ("init", menu["init_event"]),
            ("route", DEFAULT_ROUTE),
            ("family", menu["route_family"]),
            ("first_scene", DEFAULT_SCENE),
            ("first_area", DEFAULT_AREA),
            ("chapter_keys", 0),
            ("scenes", 1),
            ("requires", menu["requires"]),
            ("effects_supported", True),
            ("city_reducer", True),
            ("effects", menu["effect_fields"]),
            ("default_chapter", True),
        )))
    entry_asset = OrderedDict((
        ("schema", SCHEMA),
        ("source_pins", SOURCE_PINS),
        ("policy", "only host-proven menus; original SUPPORTED unchanged; default_chapter rows use the original LocalCityProgress default stage"),
        ("proven", list(PROVEN) + list(DEFAULT_PROVEN)),
        ("menus", entry_menu),
    ))
    entry_bytes = json.dumps(entry_asset, ensure_ascii=True, sort_keys=False, separators=(",", ":")).encode("utf-8") + b"\n"
    entry_sha = sha(entry_bytes)

    report = OrderedDict((
        ("schema", REPORT_SCHEMA),
        ("checkpoint", "v61"),
        ("inputs", OrderedDict((
            ("prepare", "analysis/project7/story-city-integration-prepare-v61/project7-inputs-m_ee5jmd"),
            ("candidate", "offline/current/data/project7_mainline32_data_candidate/catalog-v1.json.gz"),
            ("candidate_sha256", sha(CAND.read_bytes())),
            ("event_graph_sha256", sha(EVENT_GRAPH.read_bytes())),
            ("mission_catalog_sha256", sha(MISSION_CATALOG.read_bytes())),
            ("economy_sha256", sha(ECONOMY.read_bytes())),
            ("weeks_sha256", sha(WEEKS.read_bytes())),
            ("source_pins", SOURCE_PINS),
            ("stage_pins", EXPECTED_PINS),
        ))),
        ("policy", "no directory coverage as playability; only host-proven menus are scoped entry-ready; "
                   "SUPPORTED is unchanged; no per-event writes"),
        ("counts", counts),
        ("effect_audit", effect_audit),
        ("shared_fixes", [
            "StoryMainlineEntry: packaged proven-menu capability + original Week canEnter/entrance check",
            "StoryCityPolicy: typed effect split on the existing single seam - area fields are reduced "
            "here, cineLockHeroes/banHeroes/recoverBanHeroes delegate to the original "
            "LocalChapterCityEngine.applyHeroes, friendly stays original-private and rejects, "
            "unknown fields reject; every effect event gets one receipt",
            "StoryMissionBridge.chapterReady: exact promoted chapter route/area presence for entry predicate",
        ]),
        ("source_hashes", {
            "offline/current/java/android_story_shared/src/com/project7/localmanager/StoryMainlineEntry.java": sha((ROOT / "offline/current/java/android_story_shared/src/com/project7/localmanager/StoryMainlineEntry.java").read_bytes()),
            "offline/current/java/android_story_city/src/com/project7/localmanager/StoryCityPolicy.java": sha((ROOT / "offline/current/java/android_story_city/src/com/project7/localmanager/StoryCityPolicy.java").read_bytes()),
            "offline/current/java/android_story_missions/src/com/project7/localmanager/StoryMissionBridge.java": sha((ROOT / "offline/current/java/android_story_missions/src/com/project7/localmanager/StoryMissionBridge.java").read_bytes()),
            "offline/current/java/android_story_missions/host_tests/com/project7/localmanager/StoryMainlineCapabilityHost.java": sha((ROOT / "offline/current/java/android_story_missions/host_tests/com/project7/localmanager/StoryMainlineCapabilityHost.java").read_bytes()),
            "offline/current/java/android_story_missions/host_tests/com/project7/localmanager/StoryMainlineDataClosedHost.java": sha((ROOT / "offline/current/java/android_story_missions/host_tests/com/project7/localmanager/StoryMainlineDataClosedHost.java").read_bytes()),
            "tools/project7_city_effect_export.py": sha((ROOT / "tools/project7_city_effect_export.py").read_bytes()),
            "tools/project7_mainline32_capability_matrix.py": sha(Path(__file__).read_bytes()),
            "offline/current/java/android_story_missions/verify_capability.py": sha((ROOT / "offline/current/java/android_story_missions/verify_capability.py").read_bytes()),
            "mainline32-entry-v1.json": entry_sha,
        }),
        ("preserved", {
            "local_story_entry_policy_supported": list(ORIGINAL_SUPPORTED),
            "menu10": "unchanged scoped asset/policy/275 evidence",
            "menu12": "disabled",
            "coc_hook_patch": "unchanged",
            "special_selector": "[6,0,10-6,11] descriptor preserved",
            "default_minus_one": "original Bridge/LocalCityProgress fallback preserved",
            "event_graph": EXPECTED_PINS["event_graph"],
            "entry_asset": entry_sha,
            "published_entry_asset": sha(STAGE_ENTRY_ASSET.read_bytes()),
            "binding_note": "v49 actual prepare already packages this entry asset; hosts run on it directly",
        }),
        ("menus", menus),
        ("residual", OrderedDict((
            ("operation_counts", dict(sorted(residual.items()))),
            ("detail", {
                "chapter-scenes-absent": "no chapter_mission_data rows for the family; data-table absence only, not an entry gate (original fallback/policy owns entry)",
                "mission-economy-M-absent": "no original M row in promoted economy for these scenes",
                "event-auto-trigger-rows-absent": "event_condition rows exist but frozen event_graph has no @trigger row",
                "chapter-route-partial": "only part of the route family has promoted C rows",
                "shared-mechanism-not-host-proven": "data closure may exist; entry remains closed until a host proves it",
                "city-effect-type-unknown": "a bound effect document carries a field with no owner",
                "ending-row-absent": "required ending id has no weeks.tsv ending row",
            }),
        ))),
        ("host_evidence", {
            "status": "PASS",
            "host": "com.project7.localmanager.StoryMainlineEntryClosureHost",
            "checks": 447,
            "proven": [
                "menus 12/19/22/25: original requestEnterStory positive, persisted wrong-ending refusal, entryReady before/after, week reload",
                "menus 12/19/22/25 representative promoted chapter t1: getAreaStages + original admission/settlement; 19/22 advance 1114/1120 -> 1115; 12 one-scene 359 completion; 25 promoted COC 488 admission/reward/pending reload",
                "menus 19/22 shared reducer receipt/state + reload (1256 areaFree5, 1357 areaFight2)",
                "menu25 StoryCity catalog event1424 receipt/areaFree7/areaLock1; menu12 remains on the existing Dalvira dedicated owner (no shared reducer)",
            ],
            "legacy": {
            "host": "com.project7.localmanager.StoryMainlineDataClosedHost",
            "checks": 1802,
            "proven": [
                "menus 4/17/23/24/27/29/30/31: original requestEnterStory, positive/negative canEnter, persisted wrong-ending Gateway refusal (r=false, entry state unchanged, repeated refusal byte-stable), committed+persisted week, reload",
                "init-chain area effects and receipts for 4/17/23/24/27/30/31; menu29 real 1678 route event reducer",
                "menus 4/23 real city-chapter t1: original Status->getAreaStages cs22007/1121, t1 admission/settlement, battle trace, area2 advance 22008/1122, reload (gate 5052/1375, tutorial 1013/1043, receipt-carrying prerequisite seed)",
                "menu23 host-simulated battle fixture: synthetic prerequisites (route25-6/day7/hero102/completed7596), trigger8753 offer, t2/scene462 admission, original finish, battle462 trace, dialog completion, reload; not a natural route or native battle",
                "exported event1331 areaFall, event3017 areaCR7 2->4, event3020 areaCR7 ->3, save/reload",
                "unknown/duplicate areaFall rejection publishes nothing",
                "hero cineLockHeroes delegation (event 6401), receipt replay idempotent",
                "unknown field and friendly rejection publish no candidate",
            ],
            },
            "capability_host": {
                "host": "com.project7.localmanager.StoryMainlineCapabilityHost",
                "checks": 164,
                "proven": ["menu20 original requestEnterStory + 1323..1331 chain + generic effects + persisted reload",
                           "menu28 original requestEnterStory + persisted reload",
                           "menu10/menu12/special-selector guard checks"],
            },
            "query_battle_host": {
                "host": "com.project7.localmanager.StoryMainline32Host",
                "checks": 110,
                "proven": ["generic status/stages", "default -1 and unknown-route fallback",
                           "real Store begin/loss/win/replay", "mission economy va=2",
                           "success outcome offer", "route switch/new week/mutex"],
            },
            "day_ending_evidence": {
                "host": "menu10 continuity (preserved)",
                "checks": 275,
                "proven": ["original day/week transition", "ending event/CG receipt", "week reset"],
            },
            "default_chapter_host": {
                "host": "com.project7.localmanager.StoryDefaultChapterHost",
                "checks": 2784,
                "sha256": "abcee429476d77046cd3da9cbe9f19548b18c36b20a9a98c50e2942aa1e71ccc",
                "evidence": "reports/mainline32-capability-host-v61.json",
                "proven": ["menus 7/8/14/15/16/18/21/26: original requestEnterStory, default area1 cs101, t1 admission/settlement, dialog-chain effects, per-menu battle101 reload",
                           "tutorial 1000->1001->1002->1004 gateway chain and resetProgress preserves 1004",
                           "area2 default 1101->1102 advance",
                           "negative menu33 / missing endings / no-seed original high-school gate",
                           "menu23 synthetic event-battle fixture only (not t1)",
                           "route-only effects host-proven on v61 OWN/assets: 14 (1184/2161 route15-1), 15 (5216 route16-5 locks 1,2,3,4,5,7,8; 5219 route16-6 locks 2..8), 26 (1621 route29-1 free2..8+lock1..8; 1637 unlock1..8); receipt/state/lock + save/reload",
                           "menu8 real triggers on v61: 30015/40012 offered by frozen @trigger after original battle facts, original 2049->2055->2054 route 9-3, then 30045/40042 offered by @trigger with area3/4 status and 1129/7195 mutex negatives; receipt/unlock/reload",
                           "menu21 real triggers on v61: 1347 offered only after clientOp 4 with 1339/route22-1 and 1345 mutex; 1346 is the 1345 @outcome successor (battle418) and is not offered by 1347; receipt/unlock/reload"],
            },
            "evidence": "reports/mainline32-capability-host-v61.json",
            "verifier": "offline/current/java/android_story_missions/verify_capability.py",
            "manager": "analysis/project7/action-ledger-code20-v2/manager-translated-frames.jar",
            "assets": "analysis/project7/story-city-integration-prepare-v61/project7-inputs-m_ee5jmd/stage/assets",
            "binding": {
                "published_entry_asset": sha(STAGE_ENTRY_ASSET.read_bytes()),
                "runtime_entry_asset": entry_sha,
                "published": True,
                "note": "v61 actual prepare; host ran on the published stage assets, no overlay",
            },
            "limit": "limited representative mechanisms; battle evidence is a host-simulated win on a synthetic prerequisite fixture, not a natural route or native battle; menu25 uses a synthetic COC predecessor 10003 and pending completion; no full route replay and no D8/APK/native",
            "commands": [
                "javac --release 8 hosts + StoryCityPolicy/StoryMissionBridge/StoryMainlineEntry over v61 production classes and manager-translated-frames.jar",
                "java -Xverify:all com.project7.localmanager.StoryMainlineCapabilityHost <v61 stage/assets>",
                "java -Xverify:all com.project7.localmanager.StoryMainline32Host <v61 stage/assets>",
                "java -Xverify:all com.project7.localmanager.StoryMainlineDataClosedHost <v61 stage/assets> <v61 stage/assets>",
                "java -Xverify:all com.project7.localmanager.StoryDefaultChapterHost <v61 stage/assets> <v61 stage/assets>",
                "java -Xverify:all com.project7.localmanager.StoryMainlineEntryClosureHost <v61 stage/assets> <v61 stage/assets>",
            ],
        }),
        ("temp_cleanup", "host temp dirs are deleted by the verifier"),
    ))
    report_bytes = json.dumps(report, ensure_ascii=False, indent=1).encode("utf-8") + b"\n"
    return report, report_bytes, entry_bytes, entry_sha


def markdown(report):
    c = report["counts"]
    audit = report["effect_audit"]
    host = report["host_evidence"]
    menu_rows = []
    for menu in report["menus"]:
        gaps = ", ".join(menu["unsupported_operations"]) or "-"
        menu_rows.append(
            "| {id} | {name} | {init} | {family} | {chapter} | {promoted}/{normal} | "
            "{effect} | {economy} | {entry} | {gaps} |".format(
                id=menu["id"], name=menu["name"], init=menu["init_event"],
                family=menu["route_family"], chapter=menu["chapter_status"],
                promoted=menu["promoted_c_rows"], normal=menu["normal_c_rows"],
                effect=menu["effect_status"], economy=menu["economy_status"],
                entry=menu["entry_status"], gaps=gaps))
    return """# Mainline 32 capability matrix (v61)

Status: analysis + scoped implementation; no D8/APK/native, no global entry enable.

- Menus accounted: **%d/32**
- Entry enabled: `%s` (original allowlist plus scoped menu10 and host-proven `%s`)
- Newly enterable: `%s`
- Entry closed: `%s`
- Chapter status: `%s`
- Effect status: `%s`
- Event status: `%s`
- Economy status: `%s`
- Residual operations: `%s`

## Shared mechanisms

- `StoryMainlineEntry` packages only proven menus. `capability(menu)` is false before prepare and for every other menu; `entryReady` additionally requires the original Week entrance and `LocalWeekEngine.canEnter`.
- `StoryCityPolicy` is the single city refresh seam and now splits by effect type. Area fields are reduced here, including exported `areaFall` (status 2) and `areaCR7` (core=true; status 4 when current status is 2 else 3); `cineLockHeroes/banHeroes/recoverBanHeroes` are delegated to the original `LocalChapterCityEngine.applyHeroes`; `friendly` remains the original private owner and rejects on the scoped path; unknown fields reject. Every effect event gets exactly one receipt before it can replay, and a hero failure restores the profile and replies.
- `StoryMissionBridge.chapterReady` checks exact promoted chapter route/area presence. The special selector `[6,0,10-6,11]` is not flattened, and default/unknown route fallback is unchanged.
- Menu10, menu12, COC hook/patch and `LocalStoryEntryPolicy.SUPPORTED` are preserved.

## Effect audit (consumer-necessity check)

- Conclusion: %s
- Area fields owned: `%s`; hero fields delegated: `%s`.
- Friendly: %s.
- External registry field: `%s` (%s).
- Source-only fields `%s`: %s.
- Graph rows: %s published, %s prior; %s.
- Former `missing-generic-owner` menus: `%s` (all are reducer-ready; their blockers are co-missing trigger/chapter/economy data).
- Menus with hero effect rows: `%s`; friendly rows: `%s`; unknown types: none.

## Host evidence and binding

- `%s` PASS **%d** on the **published v61 prepare** (248 production classes) and its stage assets: menus 12/19/22/25 original requestEnterStory positive, persisted wrong-ending refusal, entryReady before/after, week reload; representative promoted chapter t1 for 19/22 (1114/1120 -> 1115), menu12 one-scene 359 completion, menu25 promoted COC 488 admission/reward/pending reload; shared receipts for 19 (1256 areaFree5) and 22 (1357 areaFight2); menu25 StoryCity 1424 receipt/lock. Menu12 remains on the existing Dalvira dedicated owner. Menu25 uses a synthetic COC predecessor 10003 and does not claim natural route completion.
- v61 host evidence: Capability 164, Mainline32 110, DataClosed 1802, DefaultChapter **2784**; menu10 continuity 275. Route-only receipts for 8/14/15/21/26 now use real trigger/outcome consumers.
- v61 packages combined entry asset `%s` (identical bytes to the runtime asset `%s`, 22 entry rows); hosts ran on that published prepare with no overlay. Frozen v48/v51/v52/v53 artifacts remain historical and untouched; no D8/APK/native or repackaging step was used.
- Preserved `StoryMainlineCapabilityHost` PASS **%d**: menu20/28 entry and effects, menu10/menu12 guards.
- Preserved `StoryMainline32Host` PASS **%d** and menu10 continuity PASS **275**.

## Per-menu matrix

| menu | name | init | route | chapter | C rows | effect | economy | entry | unsupported |
|---:|---|---|---|---|---:|---|---|---|---|
%s

## Limits

- Directory coverage is not playability. Only the menus above with `scoped-proven` or original allowlist entries are entry-enabled.
- Missing chapter rows are recorded as data absence, not as a reason to invent a per-route engine.
- `event-auto-trigger-rows-absent` is a frozen event_graph gap; it is not silently patched and is listed per menu.
- Full client battle render/native completion, full route replay and plot playback remain outside this evidence.
""" % (
        c["menus"], ", ".join(map(str, c["entry_enabled"])),
        ", ".join(map(str, c["newly_enterable"])), ", ".join(map(str, c["newly_enterable"])),
        ", ".join(map(str, c["entry_closed"])), c["chapter_status"], c["effect_status"],
        c["event_status"], c["economy_status"], c["unsupported_operations"],
        audit["conclusion"], ", ".join(audit["area_fields_owned"]),
        ", ".join(audit["hero_fields_delegated_to_original"]), audit["friendly_owner"],
        ", ".join(audit["external_registry_fields"]), audit["external_registry_owner"],
        ", ".join(audit["source_only_fields"]), audit["source_only_note"],
        audit["graph_rows"]["published"], audit["graph_rows"]["prior_projection"],
        audit["graph_rows"]["difference"],
        ", ".join(map(str, audit["formerly_missing_generic_owner"])),
        ", ".join(map(str, audit["menus_with_hero_effect_rows"])),
        ", ".join(map(str, audit["menus_with_friendly_effect_rows"])),
        host["host"], host["checks"],
        report["preserved"]["published_entry_asset"], host["binding"]["runtime_entry_asset"],
        host["capability_host"]["checks"], host["query_battle_host"]["checks"],
        "\n".join(menu_rows))


def write():
    report, report_bytes, entry_bytes, entry_sha = build()
    ENTRY_ASSET.parent.mkdir(parents=True, exist_ok=True)
    ENTRY_ASSET.write_bytes(entry_bytes)
    report["preserved"]["entry_asset"] = entry_sha
    report_bytes = json.dumps(report, ensure_ascii=False, indent=1).encode("utf-8") + b"\n"
    REPORT_JSON.write_bytes(report_bytes)
    REPORT_MD.write_text(markdown(report), encoding="utf-8")
    print("PASS write file=mainline32-capability-matrix-v61.json entry_sha256=%s" % entry_sha)


def entry_only():
    _, _, entry_bytes, entry_sha = build()
    ENTRY_ASSET.parent.mkdir(parents=True, exist_ok=True)
    ENTRY_ASSET.write_bytes(entry_bytes)
    print("PASS entry menus=%d sha256=%s" % (len(PROVEN + DEFAULT_PROVEN), entry_sha))


def check():
    report, _, entry_bytes, entry_sha = build()
    require(ENTRY_ASSET.read_bytes() == entry_bytes, "runtime entry asset bytes")
    live = json.loads(REPORT_JSON.read_text(encoding="utf-8"))
    require(live["schema"] == REPORT_SCHEMA, "report schema")
    require(live["counts"] == report["counts"], "report counts")
    require(live["preserved"]["entry_asset"] == entry_sha, "entry asset hash")
    require(live["counts"]["menus"] == 32, "report menu count")
    require(live["counts"]["newly_enterable"] == sorted(PROVEN + DEFAULT_PROVEN), "proven set")
    require(len(live["menus"]) == 32, "report entries")
    for menu in live["menus"]:
        require(menu["entry_enabled"] == (menu["id"] in ORIGINAL_SUPPORTED or menu["id"] == 10
                                          or menu["id"] in PROVEN or menu["id"] in DEFAULT_PROVEN),
                "entry flag %d" % menu["id"])
    print("PASS check menus=32 newly=%s entry_enabled=%d entry_sha256=%s"
          % (sorted(PROVEN + DEFAULT_PROVEN), len(live["counts"]["entry_enabled"]), entry_sha))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--entry", action="store_true")
    args = parser.parse_args()
    if args.entry:
        entry_only()
    elif args.write:
        write()
        check()
    elif args.check:
        check()
    else:
        parser.error("choose --write or --check")


if __name__ == "__main__":
    main()
