"""Source-bound data candidate for all 32 mainline menu entries.

Reads only original 640 literal tables plus the frozen pre-promotion StoryCity /
StoryMission snapshots (read-only). Emits the historical candidate asset under
runtime/project7_mainline32_data_candidate and a review report. The live
production catalogs are promoted by tools/project7_mainline32_production.py;
this writer stays reproducible against the frozen base copies and never edits
the live selector/COC source. It never marks a menu ready.

Writer: python3 tools/project7_mainline32_data_candidate.py --write
Verifier: python3 tools/project7_mainline32_data_candidate.py --check
"""
from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import re
import sys
import zlib
from collections import Counter, defaultdict, OrderedDict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from runtime.project7_dream_catalog.produce import literal  # literal-only marshal reader

CDATA = ROOT / "analysis/android640-scripts/com/data/cdata"
OUT = ROOT / "runtime/project7_mainline32_data_candidate"
REPORT_JSON = ROOT / "reports/mainline32-data-candidate.json"
REPORT_MD = ROOT / "reports/mainline32-data-candidate.md"
SCHEMA = "project7-mainline32-data-candidate-v1"
CITY_CATALOG = ROOT / "runtime/project7_story_city_catalog/catalog-v1.json.gz"
PRODUCTION_BASE = OUT / "production-base"
MISSION_CATALOG = PRODUCTION_BASE / "catalog-v1.tsv"
# Historical provenance paths stay identical to the pre-promotion source files.
REPORT_PATHS = {
    "story_mission_catalog": ROOT / "runtime/project7_story_mission_catalog/catalog-v1.tsv",
    "economy_extra": ROOT / "runtime/project7_story_mission_catalog/economy-extra.tsv",
}
EVENT_GRAPH = ROOT / "analysis/project7/manager/assets/event_graph.tsv"
WEEKS = ROOT / "analysis/project7/manager/assets/weeks.tsv"
ENTRY_POLICY_DIS = ROOT / "analysis/project7/manager/com.project7.localmanager.LocalStoryEntryPolicy.dis"

SOURCE_PINS = {
    "mainline_score_info": "dbab43659cd8a4c2983bc3ae46b340465b51b7b227c472523e4ac7d89a79ccff",
    "chapter_mission_data": "c637bbf1665c8118b238c702145a22df0ceaf860bdf80595edbcf0d20882cdb4",
    "event_content": "0ddb80bbe56259a2f54acdb7accef49ad390240b0cac504ba1375a3c8976afe7",
    "event_condition": "1ab7a968ebc01bccfa9419172ed92e91d9d491aa7288d616f2c8181de5389ec1",
    "city_data": "155ebc4d9c63c15fa921b8b3753617ef6c1d4cde2604a72263798e46c7aa775f",
    "story_route": "53f3161471d82c9abe562c41982b51f5d01a1651400d3c6fd58433b2629614b1",
    "mainline_mutex": "703e64835f5235d6c2d79fd5b7b1513b44f99eebbfcb0a2c1582efee4f9bd350",
    "story_target": "db10e54c07f8f446b10cd5a9c1e357849fe065f0f6a5c306c689547171d9db0d",
    "mission": "2019aab0289ffdac6aacde82b21cd283ef0c8d8afb6bb264d087e8cde262390f",
}
FIXED_PINS = {
    "story_city_catalog": "af2328b97372c27fd392b5b399d03daa17fa73acdd35d2b1ad5b0a8f07218069",
    "story_mission_catalog": "5f456b8d257c02f2b430aafcb36102ab240771f9e6d8fec4e3a67a79b23ede5a",
    "event_graph": "7a0f781c0a84b2fc46b1f71b0dcc6f85e80b4047ba415e8af25a08e97f11c9ba",
    "weeks": "dbb0a5d64492e18243a332c93c4a855f5572661922bd26b870b48a96b8ffaa55",
    "entry_policy_dis": "d153de71b6612b17608a7489c4ddca490109c5b6a683e5a1adeca82b6442ea56",
    "const_py": "926483f82a397faeb9002ba504e08461d7f36dc4dbb669d0789710a392909b0a",
    "economy_review": "03c1645a4c6cd126be73edf813bfdca076a1e40e916ee2cc5b976a1918b65b02",
    "economy_base": "46ece8bf692c0446c95e8a56d3ab514ef7f90e65dde1f0c48e2c29177a56b19d",
    "economy_extra": "22ecd8625063e4d75165c928e2b3443c37f1a64dfa6d6ac0268e6e23be2ea529",
}
ECONOMY_REVIEW = ROOT / "reports/root-mainline32-economy-coverage.json"
ECONOMY_BASE = ROOT / "analysis/project7/manager/assets/economy.tsv"
ECONOMY_EXTRA = PRODUCTION_BASE / "economy-extra.tsv"
AREA_FIELDS = ("areaFree", "areaFight", "areaLock", "areaUnlock")
DEDICATED = {2, 3, 5, 6, 10, 11, 12, 13, 32}
CITY_OWNER = {25}
ORIGINAL_ENTRY_SUPPORTED = (1, 2, 3, 5, 6, 9, 11, 13, 32)

# Menu -> original story_route family. The family is derived from the original
# init-chain enterStoryRoute events / mainline_mutex where present. The remaining
# rows are source-semantic joins recorded with their evidence below. This is one
# selector row per menu, never a per-event hand-written table.
ROUTE_FAMILY = {
    1: "1", 2: "4", 3: "3", 4: "5", 5: "6", 6: "7", 7: "8", 8: "9",
    9: "10", 10: "11", 11: "12", 12: "13", 13: "14", 14: "15", 15: "16",
    16: "17", 17: "18", 18: "19", 19: "20", 20: "21", 21: "22", 22: "23",
    23: "25", 24: "26", 25: "27", 26: "29", 27: "30", 28: "31", 29: "32",
    30: "33", 31: "34", 32: "35",
}
SEMANTIC_EVIDENCE = {
    1: "StoryRouteType.NORMAL='1'; menu chapter 1-1 is 正轨 (normal route)",
    3: "StoryRouteType.ANTUONIEWA='3'; LocalArkCityEngine handles route '3-1'",
    5: "StoryRouteType.DAILY='6'; LocalFreeCityEngine handles routes '6','6-3'",
    8: "StoryRouteType.JIAOHUI='9-1'..'9-3'; init closure has no enterStoryRoute",
    9: "StoryRouteType.WENZI='10'; LocalWenziCityEngine handles route '10'",
    10: "StoryRouteType.ALAN='11-1'; LocalAlanCityEngine handles '11','11-2','11-4'",
    11: "LocalChapterCityEngine.active is q7ChapterMenu==11 or rt '12'/'12-*'",
    12: "StoryRouteType.DAERWEILA_BRANCH1='13-1'; LocalWenziCityEngine/LocalDalviraCityEngine handle '13'",
    17: "story_target 18-1..18-8: 钟遥/司篁; menu detail 终焉的命轮 术士/星盘",
    26: "story_target 29-1..29-4: 冰封的艺术馆/活骸零; menu detail 大雪/气候异常",
    28: "story_target 31-1..31-8: 怜烟/陆久/300万/情报值; menu detail 资本市场",
    29: "story_target 32-1..32-7: 窃贼/卢森仓库; menu detail 酒店失窃",
}

FIELD_CONSUMERS = [
    ("score.id", "int", "LocalStoryEntryPolicy.supports(menu); StoryCityPolicy scope/menu wiring", True, "story city menus[].id"),
    ("score.name", "str", "client storyline_main/main_item; story city menus[].name", True, "story city menus[].name"),
    ("score.init_event", "int", "LocalWeekCatalog.entrances -> LocalWeekEngine.resetProgress; client StoryMember.requestEnterStory", True, "story city menus[].init"),
    ("score.requires", "tuple[tuple[int,...],...]", "LocalWeekEngine.canEnter; client StoryMember.canEnterRoute", True, "story city menus[].requires"),
    ("score.level", "int", "client mainline list; story city menus[].level", True, "story city menus[].level"),
    ("score.chapter", "str", "client storyline_main/main_item display chapter", False, ""),
    ("score.sort_id", "int", "client mainline list ordering", False, ""),
    ("score.category", "str", "client mainline category filter", False, ""),
    ("score.img", "str", "client mainline icon", False, ""),
    ("score.dir_img", "str", "client mainline directory/background image", False, ""),
    ("score.detail_img", "int", "client mainline detail image", False, ""),
    ("score.cgs", "tuple[int,...]", "client mainline CG strip", False, ""),
    ("score.all_cgs", "tuple[int,...]", "client mainline CG collection", False, ""),
    ("score.musics", "tuple[str,...]", "client mainline music", False, ""),
    ("score.short_intro", "str", "client mainline card text", False, ""),
    ("score.detail_intro", "str", "client mainline detail text", False, ""),
    ("score.gonglue", "str", "client mainline unlock hint", False, ""),
    ("event.events", "tuple[int,...]", "LocalEventCatalog.successors; event_graph successors column", True, "event_graph"),
    ("event.completeConds", "dict[str,tuple[int,...]]", "LocalEventCatalog completeConditions; event_graph completeConditions column", True, "event_graph"),
    ("event.dialog", "int", "LocalEventCatalog dialog/complete condition", True, "event_graph"),
    ("event.priority", "int", "LocalEventCatalog priority", True, "event_graph"),
    ("event.eventType", "int", "LocalEventCatalog flags", True, "event_graph flags"),
    ("event.isAutoTriggerEvent", "bool", "LocalEventCatalog flags/trigger", True, "event_graph"),
    ("event.repeatable", "bool", "LocalEventCatalog flags", True, "event_graph"),
    ("event.emergencyEvent", "bool", "LocalEventCatalog emergency classification", True, "event_graph flags"),
    ("event.isLeaveEmergencyEvent", "bool", "LocalEventCatalog emergency handoff", True, "event_graph flags"),
    ("event.release", "bool", "LocalEventCatalog release", True, "event_graph"),
    ("event.completeEnterMainPanel", "bool", "LocalEventCatalog completion/UI", True, "event_graph flags"),
    ("event.mutexEvent", "set[int]", "LocalEventCatalog @mutex rows", True, "event_graph @mutex"),
    ("event.enterStoryRoute", "str", "LocalEventCatalog.routes via @route; LocalServiceEngine selector", True, "event_graph @route when present"),
    ("event.areaFree", "tuple[int,...]", "LocalEventCatalog.cityEffects -> LocalChapterCityEngine.refresh/StoryCityPolicy.refresh", True, "event_graph @cityEffect; StoryCityPolicy catalog only menu25"),
    ("event.areaFight", "tuple[int,...]", "LocalEventCatalog.cityEffects -> LocalChapterCityEngine.refresh/StoryCityPolicy.refresh", True, "event_graph @cityEffect; StoryCityPolicy catalog only menu25"),
    ("event.areaLock", "tuple[int,...]", "LocalEventCatalog.cityEffects -> LocalChapterCityEngine.refresh/StoryCityPolicy.refresh", True, "event_graph @cityEffect; StoryCityPolicy catalog only menu25"),
    ("event.areaUnlock", "tuple[int,...]", "LocalEventCatalog.cityEffects -> LocalChapterCityEngine.refresh/StoryCityPolicy.refresh", True, "event_graph @cityEffect; StoryCityPolicy catalog only menu25"),
    ("event.areaFall", "tuple[int,...]", "city/fall area effect; no current StoryCity catalog field", False, ""),
    ("event.areaCR7", "tuple[int,...]", "CR7 area state; no current data-side catalog field", False, ""),
    ("event.batchChangeBlackcore", "dict", "LocalChapterCityEngine blackcore batch; no current data-side catalog field", False, ""),
    ("event.cityMusic", "str", "client city music; no data-side catalog field", False, ""),
    ("event.contentFinishBattle", "int", "client event finish/battle UI; no current data-side catalog field", False, ""),
    ("event.contentFinishUI", "int", "client event finish UI; no current data-side catalog field", False, ""),
    ("event.enterBattle", "int", "LocalEventCatalog @battle rows / LocalEventBattleEngine admission", True, "event_graph @battle"),
    ("event.daily_wish", "int", "daily wish mechanism; no current data-side catalog field", False, ""),
    ("event.huohaihua", "int", "special city effect; no current data-side catalog field", False, ""),
    ("event.intelligence", "int", "LocalIntelligenceEngine; no current data-side catalog field", False, ""),
    ("event.procFailClue", "tuple[int,...]", "clue/fail-clue flow; no current data-side catalog field", False, ""),
    ("event.isEmergencyEvent", "bool", "LocalEventCatalog.isEmergency", True, "event_graph flags/emergency"),
    ("event.name", "str", "client/local event display; event_graph has no name column", False, ""),
    ("event.changeBlackcore", "dict[int,int]", "LocalChapterCityEngine/LocalEventEngine blackcore state", False, ""),
    ("event.friendly", "dict[int,int]", "LocalEventCatalog.cityEffects friendly field -> LocalChapterCityEngine.applyFriendly", True, "event_graph @cityEffect"),
    ("event.rewards", "tuple[int,...]", "LocalEventEngine reward delivery (reward_common tables)", False, ""),
    ("event.notepadId", "tuple[int,...]", "LocalEventCatalog @note rows", True, "event_graph @note"),
    ("event.patrolEvent", "int", "LocalEventCatalog @patrolExcluded/@trigger patrol wiring", True, "event_graph @patrolExcluded/@trigger"),
    ("event.procClue", "tuple[int,...]", "LocalEventCatalog @clue/@puzzleClue rows", True, "event_graph @clue/@puzzleClue"),
    ("event.rel_heroes", "tuple", "client/social event relation; no data-side catalog field", False, ""),
    ("event.socialMsgId", "tuple[int,...]", "LocalEventCatalog @social rows", True, "event_graph @social"),
    ("event.privateMsgId", "int", "LocalEventCatalog @privateReply rows", True, "event_graph @privateReply"),
    ("event.weekResult", "dict", "LocalWeekEngine week result handoff; no menu-scoped candidate field", False, ""),
    ("event.autoStart", "int", "LocalEventCatalog trigger autoStart", True, "event_graph @trigger"),
    ("event.ui", "int", "client UI transition", False, ""),
    ("event.priorityGroup", "int", "LocalEventCatalog @trigger priority group", True, "event_graph @trigger"),
    ("event.completeRouteTarget", "int", "LocalEventCatalog @targetEffect/@targetCount", True, "event_graph @targetEffect/@targetCount"),
    ("event.city_attention", "tuple", "client city attention marker; no data-side catalog field", False, ""),
    ("event.cityTheme", "str", "client city theme; no data-side catalog field", False, ""),
    ("event.buildBuilding", "tuple", "LocalEventCatalog @build rows; LocalConstructionEngine", True, "event_graph @build"),
    ("event.destroyAreaPatrolBuild", "tuple", "area/patrol build destruction; no data-side catalog field", False, ""),
    ("event.destroyPatrolBuild", "tuple", "patrol build destruction; no data-side catalog field", False, ""),
    ("event.exclam", "int", "client exclamation/UI marker; no data-side catalog field", False, ""),
    ("event.gainRelyVal", "int", "city engine rely counter; no data-side catalog field", False, ""),
    ("event.gainSupportVal", "int", "city engine support counter; no data-side catalog field", False, ""),
    ("event.gainYisakeVal", "int", "Isak/area counter; no data-side catalog field", False, ""),
    ("event.gonglueHeroes", "tuple[int,...]", "client strategy hero list; no data-side catalog field", False, ""),
    ("event.ban_heroes", "tuple[int,...]", "hero ban/availability state; no data-side catalog field", False, ""),
    ("event.cineLockHeroes", "tuple[int,...]", "cinematic hero lock; no data-side catalog field", False, ""),
    ("event.recoverBanHeroes", "tuple[int,...]", "hero recovery state; no data-side catalog field", False, ""),
    ("event.refreshMission", "int", "mission refresh trigger; no data-side catalog field", False, ""),
    ("event.weekResultInAdvance", "int", "week result advance trigger; no data-side catalog field", False, ""),
    ("event.dream_id", "int", "dream/huisu mechanism; no data-side catalog field", False, ""),
    ("event.special_agreement", "dict", "generic agreement enum dispatch; no current data-side catalog field", False, ""),
    ("event.puzzle_room", "int", "StoryCity puzzle room data", True, "runtime/project7_story_city_catalog/puzzle-extra.tsv"),
    ("chapter.key", "(area,specialStage,route,status)", "StoryMissionBridge chapter lookup; LocalCityProgress status/mapStages/stages/consumeVictory", False, "current mission catalog covers route27 keys only"),
    ("chapter.section", "dict[0..9,tuple[int,...]]", "StoryMissionBridge.mapStages groups; LocalCityProgress.cs/sl", False, "current mission catalog covers route27 keys only"),
    ("chapter.specialStage", "int", "candidate selector key; current bridge requires 0", False, "current mission catalog requires 0"),
    ("chapter.status", "int", "LocalCityProgress.status", False, "current mission catalog covers route27 rows only"),
    ("route.family", "str", "LocalEventCatalog.routes/@route + LocalServiceEngine route selector", True, "event_graph @route rows only"),
    ("route.branches", "tuple[str,...]", "story_route selector; LocalServiceEngine route family gate", False, "story city route_keys only 27 family"),
    ("route.mainline_mutex", "dict", "EventResetWeek/mainline mutex handling", False, ""),
    ("area.area_require", "dict[route,tuple[int,...]]", "LocalChapterCityEngine.locked/LocalCityProgress status chain; StoryCityPolicy requirements", True, "story city areas[].raw.area_require (raw; scope menu25)"),
    ("week.route_row", "(entry,init_event,requires)", "LocalWeekCatalog.entrances; LocalWeekEngine.resetProfile/canEnter", True, "weeks.tsv component"),
    ("week.endings", "rows", "LocalWeekCatalog.endings; LocalWeekEngine.completedResult", True, "weeks.tsv component"),
    ("week.settlement", "rows", "LocalWeekCatalog.settlements; LocalWeekEngine settlement", True, "weeks.tsv component"),
    ("week.score", "rows", "LocalWeekCatalog scores/scoreEvents/cgScores/battleScores/cityScores/bonuses", True, "weeks.tsv component"),
]

BUNDLED_EVENT_FIELDS = {
    field.split(".", 1)[1]
    for field, _shape, _consumer, bundled, _where in FIELD_CONSUMERS
    if field.startswith("event.") and bundled
}


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical(value) -> bytes:
    return json.dumps(value, sort_keys=True, ensure_ascii=True, separators=(",", ":"), allow_nan=False).encode("ascii")


def require(ok, message):
    if not ok:
        raise ValueError(message)


def load_tables():
    tables = {}
    files = {}
    for name, digest in SOURCE_PINS.items():
        path = CDATA / (name + ".marshal")
        raw = path.read_bytes()
        require(sha(raw) == digest, "Source pin changed " + name)
        files[name] = str(path.relative_to(ROOT))
        tables[name] = literal(path)
    for name, path, digest in (
        ("story_city_catalog", CITY_CATALOG, FIXED_PINS["story_city_catalog"]),
        ("story_mission_catalog", MISSION_CATALOG, FIXED_PINS["story_mission_catalog"]),
        ("event_graph", EVENT_GRAPH, FIXED_PINS["event_graph"]),
        ("weeks", WEEKS, FIXED_PINS["weeks"]),
        ("entry_policy_dis", ENTRY_POLICY_DIS, FIXED_PINS["entry_policy_dis"]),
        ("const_py", ROOT / "analysis/original-py-640/com/const.py", FIXED_PINS["const_py"]),
        ("economy_review", ECONOMY_REVIEW, FIXED_PINS["economy_review"]),
        ("economy_base", ECONOMY_BASE, FIXED_PINS["economy_base"]),
        ("economy_extra", ECONOMY_EXTRA, FIXED_PINS["economy_extra"]),
    ):
        raw = path.read_bytes()
        require(sha(raw) == digest, "Fixed asset pin changed " + name)
        files[name] = str(REPORT_PATHS.get(name, path).relative_to(ROOT))
    return tables, files


def condition_routes(condition):
    value = (condition or {}).get("conds", {}).get(52)
    if isinstance(value, str):
        return set(re.findall(r"'([^']+)'", value))
    if isinstance(value, set):
        return set(value)
    return set()


def condition_events(condition):
    value = (condition or {}).get("conds", {}).get(1)
    if isinstance(value, str):
        return {int(v) for v in re.findall(r"\d+", value)}
    if isinstance(value, (set, tuple, list)):
        return {int(v) for v in value}
    return set()


def event_closure(successors, seed):
    seen = set()
    queue = [seed]
    while queue:
        event = queue.pop(0)
        if event in seen:
            continue
        require(len(seen) < 200000, "Event closure bound")
        seen.add(event)
        queue.extend(successors.get(event, ()))
    return seen


def area_kind(row):
    if row.get("virtual") == 1:
        return "virtual"
    if row.get("show_build") == 1 and row.get("show_upgrade") == 1:
        return "normal"
    return "auxiliary"


def parse_mission_catalog_routes():
    routes = defaultdict(set)
    keys = []
    for line in MISSION_CATALOG.read_text(encoding="utf-8").splitlines():
        row = line.split("\t")
        if row and row[0] == "C":
            require(len(row) == 6, "Mission catalog C row")
            routes[row[3]].add(row[3])
            keys.append((int(row[1]), int(row[2]), row[3], int(row[4])))
    return routes, keys


def load_city_catalog():
    raw = gzip.decompress(CITY_CATALOG.read_bytes())
    return json.loads(raw)


def parse_weeks_routes():
    rows = {}
    for line in WEEKS.read_text(encoding="utf-8").splitlines():
        row = line.split("\t")
        if len(row) == 4 and row[0] == "route":
            entry = int(row[1])
            requires = []
            if row[3]:
                for group in row[3].split("|"):
                    requires.append([int(v) for v in group.split(",") if v])
            rows[entry] = {"entry": entry, "init_event": int(row[2]), "requires": requires}
    return rows


def inherited_mission(missions, scene, chain=()):
    require(scene not in chain and scene in missions, "Mission inheritance %s" % scene)
    row = missions[scene]
    parent = row.get("inherit_mission")
    base = inherited_mission(missions, parent, chain + (scene,)) if parent else {}
    merged = dict(base)
    merged.update(row)
    return merged


def existing_economy_rows():
    rows = {}
    for path in (ECONOMY_BASE, ECONOMY_EXTRA):
        for line in path.read_text(encoding="utf-8").splitlines():
            row = line.split("\t")
            if len(row) >= 2 and row[0] == "M":
                rows[int(row[1])] = row[2:]
    return rows


def build():
    require(sha(MISSION_CATALOG.read_bytes()) == FIXED_PINS["story_mission_catalog"],
            "Frozen pre-promotion mission base changed")
    require(sha(ECONOMY_EXTRA.read_bytes()) == FIXED_PINS["economy_extra"],
            "Frozen pre-promotion economy base changed")
    tables, files = load_tables()
    scores = tables["mainline_score_info"]
    chapters = tables["chapter_mission_data"]
    events = tables["event_content"]
    conditions = tables["event_condition"]
    areas = tables["city_data"]
    story_routes = tables["story_route"]
    mutex = tables["mainline_mutex"]
    missions = tables["mission"]

    require(set(scores) == set(range(1, 33)), "Mainline menu set changed")
    require(len(story_routes) == 34, "Story route family count changed")
    story_target = tables["story_target"]
    const_text = (ROOT / "analysis/original-py-640/com/const.py").read_text(encoding="utf-8", errors="replace")
    for token in ("ANTUONIEWA", "DAILY", "JIAOHUI", "WENZI", "ALAN", "ZHOUNIAN", "DAERWEILA_BRANCH1", "NORMAL"):
        require(token in const_text, "Semantic evidence const missing " + token)
    for menu in (17, 26, 28, 29):
        family = ROUTE_FAMILY[menu]
        branches = set(story_routes[family]["routes"]) | {family}
        require(any(route in story_target for route in branches), "Semantic evidence story_target missing menu %d" % menu)
    require(len(areas) == 13, "City area count changed")
    require(len(ORIGINAL_ENTRY_SUPPORTED) == 9, "Original entry allowlist changed")
    require(ORIGINAL_ENTRY_SUPPORTED == (1, 2, 3, 5, 6, 9, 11, 13, 32), "Original entry allowlist values changed")
    require(b"1032" in ENTRY_POLICY_DIS.read_bytes(), "Ordinary opening evidence missing")

    city_catalog = load_city_catalog()
    economy_review = json.loads(ECONOMY_REVIEW.read_text(encoding="utf-8"))
    reported_missing = set(economy_review["missing_economy_scenes"])
    require(city_catalog["public_ready_ids"] == [], "Current city catalog became ready")
    current_scope_menus = set(city_catalog["scope_menus"])
    current_route_keys = set(city_catalog["route_keys"])
    mission_route_keys, mission_chapter_keys = parse_mission_catalog_routes()
    week_rows = parse_weeks_routes()
    require(len(week_rows) == 32, "Weeks entry set changed")

    successors = {event: tuple(row.get("events", ())) for event, row in events.items()}
    route_events = defaultdict(set)
    for event, row in events.items():
        route = row.get("enterStoryRoute")
        if route:
            route_events[str(route)].add(event)
    trigger_events = defaultdict(set)
    for event, condition in conditions.items():
        for route in condition_routes(condition):
            trigger_events[route].add(event)

    menus = []
    for menu in range(1, 33):
        score = scores[menu]
        init = score["init_event"]
        require(init in events, "Missing init event %d" % init)
        init_row = events[init]
        chain = event_closure(successors, init)
        chain_routes = {str(events[e]["enterStoryRoute"]) for e in chain if events[e].get("enterStoryRoute")}
        chain_families = {route.split("-")[0] for route in chain_routes}
        family = ROUTE_FAMILY[menu]
        require(family in story_routes, "Missing story_route family " + family)
        mutex_row = mutex.get(family)
        mutex_route = str(mutex_row["belong_route"]) if mutex_row else None
        require(mutex_row is None or mutex_row["init_event"] == init, "mainline_mutex init mismatch")
        selector_branches = sorted(set(story_routes[family]["routes"]) | {family})
        chapter_extra_branches = sorted({key[2] for key in chapters if key[2].split("-")[0] == family and key[2] not in selector_branches})
        branches = selector_branches
        branch_set = set(branches)

        direct = family in chain_families or family == mutex_route
        if direct:
            evidence_kind = "source-direct"
            evidence = []
            for event in sorted(chain):
                route = events[event].get("enterStoryRoute")
                if route and route.split("-")[0] == family:
                    evidence.append("enterStoryRoute %d:%s" % (event, route))
            if family == mutex_route:
                evidence.append("mainline_mutex %s.belong_route=%s" % (menu, mutex_route))
        else:
            evidence_kind = "source-semantic"
            evidence = ["init-chain families=" + ",".join(sorted(chain_families) or ["<none>"]), SEMANTIC_EVIDENCE[menu]]

        chapter_rows = []
        branch_coverage = []
        scene_ids = []
        status_values = Counter()
        special_values = Counter()
        for branch in branches:
            rows = [key for key in chapters if key[2] == branch]
            branch_scenes = []
            for key in sorted(rows):
                row = chapters[key]
                # Original key order is (area, status, route, specialStage).
                body_key = (row["chapter"], row["status"], row["route"], row["specialStage"])
                key_body_swapped = key != body_key
                if key_body_swapped:
                    require(key[0] == row["chapter"] and key[2] == row["route"], "Chapter key/body area+route mismatch")
                    require({key[1], key[3]} == {row["status"], row["specialStage"]}, "Unsupported chapter key/body mismatch")
                groups = row["section"]
                require(set(groups) == set(range(10)), "Chapter section index shape")
                section = [list(groups[i]) for i in range(10)]
                scenes = [scene for group in section for scene in group]
                for scene in scenes:
                    require(scene in missions, "Unknown chapter scene %d" % scene)
                require(row["chapter"] in areas, "Unknown chapter area %d" % row["chapter"])
                normal_c_row_compatible = (
                    key[1] == 0
                    and key[3] == 0
                    and 1 <= key[0] <= 8
                    and re.fullmatch(r"[0-9]+(?:-[0-9]+)?", key[2]) is not None
                    and all(len(group) <= 1 for group in section)
                    and bool(scenes)
                )
                if normal_c_row_compatible:
                    descriptor = "normal-c-row"
                elif key == (6, 0, "10-6", 11):
                    descriptor = "selector11-descriptor"
                else:
                    descriptor = "non-normal-key"
                chapter_rows.append(OrderedDict((
                    ("key", list(key)),
                    ("area", key[0]),
                    ("status", key[1]),
                    ("route", key[2]),
                    ("special", key[3]),
                    ("body_special_stage", row["specialStage"]),
                    ("body_status", row["status"]),
                    ("key_body_swapped", key_body_swapped),
                    ("normal_c_row_compatible", normal_c_row_compatible),
                    ("descriptor", descriptor),
                    ("section", section),
                    ("scenes", scenes),
                )))
                branch_scenes.extend(scenes)
                scene_ids.extend(scenes)
                status_values[key[1]] += 1
                special_values[key[3]] += 1
            branch_coverage.append(OrderedDict((
                ("route", branch),
                ("chapter_keys", len(rows)),
                ("scenes", len(branch_scenes)),
            )))
        chapter_rows = sorted(chapter_rows, key=lambda row: (row["route"], row["area"], row["special"], row["status"]))
        scene_ids = sorted(set(scene_ids))

        menu_events = set(chain)
        for branch in branches:
            menu_events |= route_events.get(branch, set())
            menu_events |= trigger_events.get(branch, set())
        bound_event_fields = sorted({field for event in menu_events for field in events.get(event, {})})
        unconsumed_event_fields = sorted(set(bound_event_fields) - BUNDLED_EVENT_FIELDS)
        effect_rows = []
        effect_field_counts = Counter()
        effect_area_ids = set()
        for event in sorted(menu_events):
            row = events.get(event, {})
            values = {}
            for field in AREA_FIELDS:
                ids = sorted({int(v) for v in row.get(field, ())})
                if ids:
                    values[field] = ids
                    effect_field_counts[field] += len(ids)
                    effect_area_ids.update(ids)
            if values:
                effect_rows.append(OrderedDict((("event", event), *values.items())))

        bound_area_ids = set(effect_area_ids) | {row["area"] for row in chapter_rows}
        area_requirements = []
        for area in sorted(areas):
            requirement = areas[area].get("area_require") or {}
            hit = {route: list(ids) for route, ids in sorted(requirement.items()) if route in branch_set}
            if hit:
                area_requirements.append(OrderedDict((("area", area), ("routes", hit))))
                bound_area_ids.add(area)
        area_rows = []
        for area in sorted(bound_area_ids):
            require(area in areas, "Unknown bound area %d" % area)
            row = areas[area]
            area_rows.append(OrderedDict((
                ("id", area),
                ("kind", area_kind(row)),
                ("name", row.get("name", "")),
                ("show_build", row.get("show_build", 0)),
                ("show_upgrade", row.get("show_upgrade", 0)),
                ("virtual", row.get("virtual", 0)),
            )))

        has_chapters = bool(chapter_rows)
        if menu in DEDICATED:
            primary = "existing-dedicated-primitive"
            classification_reason = "original dedicated engine/primitive already owns this route family"
        elif menu in CITY_OWNER:
            primary = "existing-city-owner"
            classification_reason = "current StoryCityPolicy/COC owner; candidate does not change ownership"
        elif has_chapters:
            primary = "shared-table-driven-chapter"
            classification_reason = "chapter_mission_data rows present; generic table-driven chapter path"
        else:
            primary = "unknown-normal-city-candidate"
            classification_reason = "no chapter rows and no proven dedicated owner; normal city candidate with original-consumer proof pending; no engine invented"

        gaps = []
        if not has_chapters:
            gaps.append(OrderedDict((
                ("kind", "data"),
                ("id", "chapter-mission-data-absent"),
                ("detail", "chapter_mission_data has no rows for route family %s (%s); no chapter scenes can be sourced" % (family, ",".join(branches))),
                ("consumer", "StoryMissionBridge / LocalCityProgress / LocalChapterCityEngine"),
            )))
        if menu == 8:
            gaps.append(OrderedDict((
                ("kind", "primitive"),
                ("id", "route-primitive-missing"),
                ("detail", "init 498 closure 499,500,501,503..507,1108,1106,1107,1109 contains no enterStoryRoute and no trigger 52 route; std.rt stays '1'"),
                ("consumer", "LocalEventCatalog.routes @route / LocalServiceEngine route selector"),
            )))
        if menu == 9:
            gaps.append(OrderedDict((
                ("kind", "selector"),
                ("id", "selector11-descriptor-owned-by-menu10"),
                ("detail", "row [6,0,10-6,11] = (area=6,status=0,route=10-6,specialStage=11) is menu10's selector11 descriptor; it is excluded from generic family10 C rows and not flattened"),
                ("consumer", "StoryMissionBridge special selector11 descriptor"),
            )))
        if menu == 12:
            gaps.append(OrderedDict((
                ("kind", "primitive"),
                ("id", "wenzi-state-initializer-missing"),
                ("detail", "q7WenziCity needs an rt-10-derived city effect/state before route13/Dalvira; fresh menu12 entry has no initializer"),
                ("consumer", "LocalWenziCityEngine/LocalDalviraCityEngine"),
            )))
        if menu not in current_scope_menus:
            gaps.append(OrderedDict((
                ("kind", "scope"),
                ("id", "outside-current-selector-scope"),
                ("detail", "current story city catalog scope_menus=%s ready=[]" % sorted(current_scope_menus)),
                ("consumer", "StoryCityPolicy.owned/resolve"),
            )))
        if not any(branch in current_route_keys for branch in branches):
            gaps.append(OrderedDict((
                ("kind", "selector"),
                ("id", "route-family-not-in-current-selector"),
                ("detail", "no branch of family %s is in the current route_keys set" % family),
                ("consumer", "StoryCityPolicy route resolution"),
            )))
        if chapter_extra_branches:
            gaps.append(OrderedDict((
                ("kind", "selector"),
                ("id", "selector-table-omits-chapter-branches"),
                ("detail", "chapter_mission_data has rows for %s but story_route family %s does not list those branches" % (",".join(chapter_extra_branches), family)),
                ("consumer", "story_route -> LocalEventCatalog.routes/LocalServiceEngine selector"),
            )))

        score_fields = sorted(score)
        bundled_score = [key for key in score_fields if key in ("id", "name", "init_event", "requires", "level")]
        event_fields = sorted(init_row)
        score_unconsumed = [key for key in score_fields if key not in bundled_score]
        route_evidence_ids = sorted(event for event in chain if events[event].get("enterStoryRoute") and str(events[event]["enterStoryRoute"]).split("-")[0] == family)
        week = OrderedDict((
            ("entry", menu),
            ("init_event", init),
            ("requires", [list(group) for group in (score.get("requires") or ())]),
            ("weeks_route_row", week_rows[menu]),
            ("matches_weeks_route_row", week_rows[menu]["init_event"] == init),
        ))
        require(week["matches_weeks_route_row"], "Weeks route row mismatch for menu %d" % menu)

        entry = OrderedDict((
            ("original_supports", menu in ORIGINAL_ENTRY_SUPPORTED),
            ("current_scope_menu", menu in current_scope_menus),
            ("candidate_ready", False),
            ("enable_entry", False),
        ))

        menu_row = OrderedDict((
            ("id", menu),
            ("name", score.get("name", "")),
            ("chapter", score.get("chapter", "")),
            ("sort_id", score.get("sort_id", 0)),
            ("category", score.get("category", "")),
            ("level", score.get("level", 0)),
            ("requires", [list(group) for group in (score.get("requires") or ())]),
            ("init_event", init),
            ("week", week),
            ("route", OrderedDict((
                ("family", family),
                ("branches", branches),
                ("evidence_kind", evidence_kind),
                ("evidence", evidence),
                ("chain_route_families", sorted(chain_families)),
                ("mainline_mutex", mutex_row),
                ("extra_descriptor_routes", ["10-6"] if menu == 10 else []),
                ("family_graph_complete", menu != 10),
                ("graph_note", "menu10 spans route10-6 via selector11; family11 alone is not a complete reachability graph" if menu == 10 else "single-family data row; reachability not claimed"),
            ))),
            ("selector", OrderedDict((
                ("family", family),
                ("branches", branches),
                ("chapter_route_keys", sorted({row["route"] for row in chapter_rows})),
                ("in_current_selector", any(branch in current_route_keys for branch in branches)),
                ("current_scope_route_keys", sorted(set(branches) & current_route_keys)),
            ))),
            ("chapter_keys", len(chapter_rows)),
            ("chapters", chapter_rows),
            ("descriptor_rows", [row["key"] for row in chapter_rows if row["descriptor"] != "normal-c-row"]),
            ("branch_coverage", branch_coverage),
            ("branches_without_chapter_rows", [b["route"] for b in branch_coverage if not b["chapter_keys"]]),
            ("scenes", scene_ids),
            ("areas", area_rows),
            ("area_requirements", area_requirements),
            ("events", OrderedDict((
                ("init_chain", sorted(chain)),
                ("route_events", sorted({event for branch in branches for event in route_events.get(branch, ())})),
                ("trigger_events", sorted({event for branch in branches for event in trigger_events.get(branch, ())})),
                ("bound_count", len(menu_events)),
            ))),
            ("effects", effect_rows),
            ("effect_field_counts", dict(sorted(effect_field_counts.items()))),
            ("status_values", dict(sorted(status_values.items()))),
            ("special_stage_values", dict(sorted(special_values.items()))),
            ("entry", entry),
            ("primary_class", primary),
            ("classification_reason", classification_reason),
            ("consumer_proof", "pending" if primary == "unknown-normal-city-candidate" else "existing-owner"),
            ("gaps", gaps),
            ("ready", False),
            ("fields", OrderedDict((
                ("score_present", score_fields),
                ("score_bundled", bundled_score),
                ("score_unconsumed", score_unconsumed),
                ("init_event_present", event_fields),
                ("bound_event_fields", bound_event_fields),
                ("unconsumed_event_fields", unconsumed_event_fields),
                ("init_event_route_evidence_events", route_evidence_ids),
                ("chapter_shape", "(chapter,specialStage,route,status)->{0..9:tuple[int,...]}" if has_chapters else None),
                ("chapter_consumed_by_current_mission_catalog", any(tuple(row["key"]) in mission_chapter_keys for row in chapter_rows)),
                ("chapter_keys_in_current_mission_catalog", sum(1 for row in chapter_rows if tuple(row["key"]) in mission_chapter_keys)),
                ("effect_fields", sorted(effect_field_counts)),
                ("effect_consumed_by_current_story_city_catalog", menu in current_scope_menus),
            ))),
        ))
        menus.append(menu_row)

    require(len(menus) == 32, "Menu count")
    shared_menus = [menu for menu in menus if menu["primary_class"] == "shared-table-driven-chapter"]
    shared_rows = [row for menu in shared_menus for row in menu["chapters"]]
    generic_rows = [row for row in shared_rows if row["normal_c_row_compatible"]]
    selector11_rows = [row for row in shared_rows if row["descriptor"] == "selector11-descriptor"]
    require(len(shared_menus) == 13 and len(shared_rows) == 473, "Shared 13-menu chapter row contract changed")
    require(len(generic_rows) == 472, "Generic C-row contract changed")
    require(len(selector11_rows) == 1 and selector11_rows[0]["key"] == [6, 0, "10-6", 11], "selector11 descriptor row changed")
    chapter_keys_seen = set()
    scene_area = {}
    for row in generic_rows:
        chapter_key = (row["area"], row["route"])
        require(chapter_key not in chapter_keys_seen, "Duplicate C key %s" % (chapter_key,))
        chapter_keys_seen.add(chapter_key)
        for scene in row["scenes"]:
            require(scene_area.get(scene, row["area"]) == row["area"], "Scene cross-area collision %d" % scene)
            scene_area[scene] = row["area"]
    shared_c_rows = build_shared_c_rows(generic_rows, scene_area)
    all_shared_scenes = sorted({scene for row in shared_rows for scene in row["scenes"]})
    economy_rows = []
    generated_m = {}
    economy_success_events = {}
    for scene in all_shared_scenes:
        mission_row = inherited_mission(missions, scene)
        fields = [mission_row.get(name, default) for name, default in (
            ("va", 0), ("fatigue", 0), ("overFatigue", 0), ("force_recommend", 0),
            ("least_hero_num", 1), ("max_hero_num", 3), ("prize", 1),
        )]
        require(all(type(value) is int and value >= 0 for value in fields), "Mission economy type %d" % scene)
        generated_m[scene] = [str(value) for value in fields]
        economy_rows.append("M\t%d\t%s" % (scene, "\t".join(map(str, fields))))
        condition = mission_row.get("cond", ()) or ()
        condition_event = mission_row.get("cond_event", 0) or 0
        if condition or condition_event:
            economy_rows.append("G\t%d\t%s" % (scene, "\t".join(map(str, [condition_event, *condition]))))
        success = mission_row.get("successEvent") or ()
        if success:
            economy_success_events[str(scene)] = list(success)
    existing_rows = existing_economy_rows()
    existing_m = set(existing_rows)
    overlap = sorted(existing_m & set(all_shared_scenes))
    existing_mismatch = [(scene, generated_m[scene], existing_rows[scene]) for scene in overlap if generated_m[scene] != existing_rows[scene]]
    require(not existing_mismatch, "Existing economy rows differ from source derivation: %s" % (existing_mismatch[:3],))
    economy_m_scenes = [int(row.split("\t")[1]) for row in economy_rows if row.startswith("M\t")]
    missing_before = sorted(set(all_shared_scenes) - existing_m)
    shared_c_economy = ("# Original mission economy rows for the 13 shared chapter menus; batch source conversion\n" + "\n".join(economy_rows) + "\n").encode("utf-8")
    require(len(all_shared_scenes) == 173, "Shared economy scene contract changed")
    require(len(economy_m_scenes) == 173, "Shared economy M row contract changed")
    require(missing_before == sorted(set(reported_missing)), "Economy missing set differs from frozen review")
    require(set(economy_m_scenes) - existing_m == set(reported_missing), "Economy missing scene arithmetic")
    economy_candidate = OrderedDict((
        ("policy", "shared-13-uniform-original-mission-economy-v1"),
        ("scenes", len(all_shared_scenes)),
        ("m_rows", len(economy_m_scenes)),
        ("g_rows", sum(1 for row in economy_rows if row.startswith("G\t"))),
        ("existing_explicit_m_scenes", len(existing_m & set(all_shared_scenes))),
        ("existing_m_rows_checked", len(overlap)),
        ("existing_m_rows_match_source", not existing_mismatch),
        ("missing_before", len(missing_before)),
        ("missing_after", 0),
        ("action_cost_distribution", dict(sorted(Counter(str(value) for value in (
            inherited_mission(missions, scene).get("va", 0) for scene in all_shared_scenes
        )).items()))),
        ("area1_contract", {str(scene): OrderedDict((
            ("ch", inherited_mission(missions, scene).get("ch")),
            ("system_type", inherited_mission(missions, scene).get("system_type")),
            ("va", inherited_mission(missions, scene).get("va")),
            ("fatigue", inherited_mission(missions, scene).get("fatigue")),
            ("overFatigue", inherited_mission(missions, scene).get("overFatigue")),
            ("least_hero_num", inherited_mission(missions, scene).get("least_hero_num")),
            ("max_hero_num", inherited_mission(missions, scene).get("max_hero_num")),
            ("cond_event", inherited_mission(missions, scene).get("cond_event")),
            ("cond", list(inherited_mission(missions, scene).get("cond") or ())),
            ("successEvent", list(inherited_mission(missions, scene).get("successEvent") or ())),
        )) for scene in all_shared_scenes if inherited_mission(missions, scene).get("ch") == 1 and scene in (22010, 22011, 22012)}),
        ("asset", "shared-c-economy.tsv"),
        ("sha256", sha(shared_c_economy)),
        ("admission_note", "LocalEconomyEngine.begin/finish guard missions.containsKey(scene); absent M skips the mission economy branch and is not a proven hang, but it bypasses mission cost/admission; candidate rows close the 148-scene gap and still require real Gateway finish/cost verification"),
    ))
    area1_rows = [row for row in generic_rows if row["area"] == 1]
    area1_scenes = sorted({scene for row in area1_rows for scene in row["scenes"]})
    area1_menus = sorted({menu["id"] for menu in shared_menus for row in menu["chapters"] if row["normal_c_row_compatible"] and row["area"] == 1})
    c_row_candidate = OrderedDict((
        ("policy", "shared-13-normal-c-row-candidate-v1"),
        ("key_order", ["area", "status", "route", "specialStage"]),
        ("menus", [menu["id"] for menu in shared_menus]),
        ("rows_total", len(shared_rows)),
        ("generic_c_rows", len(generic_rows)),
        ("selector11_descriptor_rows", len(selector11_rows)),
        ("selector11_keys", [row["key"] for row in selector11_rows]),
        ("selector11_owner_menu", 10),
        ("selector11_route", "10-6"),
        ("selector11_note", "menu10 spans route10-6; a single family is not a complete reachability graph"),
        ("area1_rows", len(area1_rows)),
        ("area1_scenes", area1_scenes),
        ("area1_menus", area1_menus),
        ("area1_note", "original LocalCityProgress.dis:223 consumeVictory rejects area<2 with fixed -2 action; verify real Gateway finish against the original 640 cost contract before import, do not remove the guard parser-only"),
        ("a_rows", len(scene_area)),
        ("asset", "shared-c-rows.tsv"),
        ("sha256", sha(shared_c_rows)),
        ("note", "generic C/A rows only; selector11 key [6,0,10-6,11] stays a four-token descriptor and is not flattened"),
    ))
    require(all(menu["ready"] is False for menu in menus), "A candidate menu became ready")
    require(all(menu["entry"]["enable_entry"] is False for menu in menus), "Entry enablement leaked")
    require(not (set(ROUTE_FAMILY.values()) & {"2", "24", "28"}), "Unused route family claimed")
    require(len({menu["route"]["family"] for menu in menus}) == 32, "Route family not 1:1")

    class_counts = Counter(menu["primary_class"] for menu in menus)
    chapter_keys_total = sum(menu["chapter_keys"] for menu in menus)
    scenes_total = sum(len(menu["scenes"]) for menu in menus)
    effect_rows_total = sum(len(menu["effects"]) for menu in menus)
    area_total = sum(len(menu["areas"]) for menu in menus)
    claimed_routes = {branch for menu in menus for branch in menu["route"]["branches"]}
    unclaimed_keys = sorted(key for key in chapters if key[2] not in claimed_routes)
    unclaimed_rows = [OrderedDict((
        ("key", list(key)),
        ("route", key[2]),
        ("scenes", [scene for group in chapters[key]["section"].values() for scene in group]),
    )) for key in unclaimed_keys]
    selector_table_gaps = [
        OrderedDict((("id", "story-route-23-5-omitted"), ("detail", "chapter_mission_data has 7 rows for 23-5 but story_route family 23 lists only 23-1..23-4; menu22 cannot select 23-5 from the current selector table"))),
        OrderedDict((("id", "route--1-not-a-menu-family"), ("detail", "route -1 normal-first-week chapter rows are not represented by any story_route family/menu entry"))),
        OrderedDict((("id", "route-24-unclaimed"), ("detail", "story_route family 24 and chapter rows 24-1..24-5 exist but no mainline menu entry claims them"))),
    ]
    non27_chapter_keys = sum(1 for menu in menus if menu["route"]["family"] != "27" for _ in menu["chapters"])
    menu25 = next(menu for menu in menus if menu["id"] == 25)
    branch_totals = {
        "with_chapters": sum(1 for menu in menus if menu["chapter_keys"]),
        "without_chapters": sum(1 for menu in menus if not menu["chapter_keys"]),
        "partial_branch_coverage": sum(1 for menu in menus if 0 < sum(1 for b in menu["branch_coverage"] if b["chapter_keys"]) < len(menu["branch_coverage"])),
    }
    require(class_counts == Counter({
        "existing-dedicated-primitive": 9,
        "existing-city-owner": 1,
        "shared-table-driven-chapter": 13,
        "unknown-normal-city-candidate": 9,
    }), "Classification counts changed: %s" % dict(class_counts))

    catalog = OrderedDict((
        ("schema", SCHEMA),
        ("policy", "source-table-data-candidate-v1; no entry enablement; ready=[]"),
        ("source_pins", SOURCE_PINS),
        ("fixed_asset_pins", FIXED_PINS),
        ("source_files", files),
        ("current_catalog", OrderedDict((
            ("scope_menus", sorted(current_scope_menus)),
            ("ready_ids", city_catalog["public_ready_ids"]),
            ("route_keys", sorted(current_route_keys)),
            ("mission_catalog_route_keys", sorted(mission_route_keys)),
            ("mission_catalog_chapter_keys", len(mission_chapter_keys)),
        ))),
        ("selector", OrderedDict((
            ("story_route_families", OrderedDict((family, sorted(set(row["routes"]) | {family})) for family, row in sorted(story_routes.items(), key=lambda item: int(item[0])))),
            ("menu_route_family", OrderedDict((str(menu), family) for menu, family in sorted(ROUTE_FAMILY.items()))),
            ("unused_families", ["2", "24", "28"]),
        ))),
        ("menus", menus),
        ("c_row_candidate", c_row_candidate),
        ("economy_candidate", economy_candidate),
        ("unclaimed_chapter_rows", OrderedDict((
            ("count", len(unclaimed_rows)),
            ("routes", sorted({row["route"] for row in unclaimed_rows})),
            ("rows", unclaimed_rows),
        ))),
        ("selector_table_gaps", selector_table_gaps),
        ("ready_ids", []),
        ("scope_menus", []),
        ("entry_enablement", False),
        ("counts", OrderedDict((
            ("menus", len(menus)),
            ("classes", dict(sorted(class_counts.items()))),
            ("chapter_keys", chapter_keys_total),
            ("non27_chapter_keys", non27_chapter_keys),
            ("menu25_chapter_keys", menu25["chapter_keys"]),
            ("menu25_current_catalog_overlap", menu25["fields"]["chapter_keys_in_current_mission_catalog"]),
            ("unclaimed_chapter_keys", len(unclaimed_rows)),
            ("unclaimed_by_route", dict(sorted(Counter(row["route"] for row in unclaimed_rows).items()))),
            ("unclaimed_routes", sorted({row["route"] for row in unclaimed_rows})),
            ("scenes", scenes_total),
            ("effect_rows", effect_rows_total),
            ("area_rows", area_total),
            ("menus_with_chapters", branch_totals["with_chapters"]),
            ("menus_without_chapters", branch_totals["without_chapters"]),
            ("menus_with_partial_branch_coverage", branch_totals["partial_branch_coverage"]),
            ("shared_c_rows", OrderedDict((
                ("rows_total", c_row_candidate["rows_total"]),
                ("generic_c_rows", c_row_candidate["generic_c_rows"]),
                ("selector11_descriptor_rows", c_row_candidate["selector11_descriptor_rows"]),
                ("a_rows", c_row_candidate["a_rows"]),
                ("area1_rows", c_row_candidate["area1_rows"]),
                ("area1_menus", c_row_candidate["area1_menus"]),
                ("area1_scenes", c_row_candidate["area1_scenes"]),
            ))),
            ("economy", OrderedDict((
                ("scenes", economy_candidate["scenes"]),
                ("m_rows", economy_candidate["m_rows"]),
                ("g_rows", economy_candidate["g_rows"]),
                ("existing_explicit_m_scenes", economy_candidate["existing_explicit_m_scenes"]),
                ("missing_before", economy_candidate["missing_before"]),
                ("missing_after", 0),
            ))),
            ("original_entry_supported", list(ORIGINAL_ENTRY_SUPPORTED)),
            ("current_scope_menus", sorted(current_scope_menus)),
        ))),
    ))
    catalog_bytes = canonical(catalog)
    require(len(catalog_bytes) < 8_000_000, "Candidate catalog bound")
    gz = gzip.compress(catalog_bytes, compresslevel=9, mtime=0)
    menus_tsv = build_menus_tsv(menus)
    chapters_tsv = build_chapters_tsv(menus)
    contract = OrderedDict((
        ("schema", SCHEMA),
        ("asset", "catalog-v1.json.gz"),
        ("asset_sha256", sha(gz)),
        ("asset_size", len(gz)),
        ("expanded_sha256", sha(catalog_bytes)),
        ("expanded_size", len(catalog_bytes)),
        ("menus_tsv_sha256", sha(menus_tsv)),
        ("chapters_tsv_sha256", sha(chapters_tsv)),
        ("shared_c_rows_sha256", sha(shared_c_rows)),
        ("shared_c_rows", c_row_candidate),
        ("shared_c_economy_sha256", sha(shared_c_economy)),
        ("economy_candidate", economy_candidate),
        ("source_pins", SOURCE_PINS),
        ("fixed_asset_pins", FIXED_PINS),
        ("counts", catalog["counts"]),
        ("ready_ids", []),
        ("scope_menus", []),
        ("entry_enablement", False),
        ("policy", "data candidate only; live selector/COC/source unchanged; no D8/APK/native"),
    ))
    contract_bytes = (json.dumps(contract, indent=2, ensure_ascii=False, sort_keys=True) + "\n").encode("utf-8")
    return catalog, catalog_bytes, gz, contract, contract_bytes, menus_tsv, chapters_tsv, shared_c_rows, shared_c_economy


def build_shared_c_rows(rows, scene_area):
    lines = ["P7STORYMISSIONS\t1\tshared-13-normal-candidate"]
    for row in sorted(rows, key=lambda r: (r["area"], r["route"], r["special"], r["status"])):
        lines.append("C\t%d\t%d\t%s\t%d\t%s" % (
            row["area"], row["special"], row["route"], row["status"],
            ";".join(",".join(map(str, group)) for group in row["section"]),
        ))
    for scene in sorted(scene_area):
        lines.append("A\t%d\t%d" % (scene, scene_area[scene]))
    return ("\n".join(lines) + "\n").encode("utf-8")


def build_menus_tsv(menus):
    lines = ["# menu\tname\tchapter\tinit_event\troute_family\tbranches\tchapter_keys\tscenes\tbound_events\tarea_effect_rows\tareas\tprimary_class\toriginal_supports\tready"]
    for menu in menus:
        lines.append("\t".join(map(str, (
            menu["id"], menu["name"], menu["chapter"], menu["init_event"],
            menu["route"]["family"], ",".join(menu["route"]["branches"]),
            menu["chapter_keys"], len(menu["scenes"]), menu["events"]["bound_count"],
            len(menu["effects"]), ",".join(str(area["id"]) for area in menu["areas"]),
            menu["primary_class"], int(menu["entry"]["original_supports"]), 0,
        ))))
    return ("\n".join(lines) + "\n").encode("utf-8")


def build_chapters_tsv(menus):
    lines = ["# menu\tarea\tstatus\troute\tspecial_stage\tsections\tscenes"]
    for menu in menus:
        for row in menu["chapters"]:
            lines.append("\t".join(map(str, (
                menu["id"], row["area"], row["status"], row["route"], row["special"],
                ";".join(",".join(map(str, group)) for group in row["section"]),
                ",".join(map(str, row["scenes"])),
            ))))
    return ("\n".join(lines) + "\n").encode("utf-8")


def write_report(catalog, contract, catalog_bytes, gz, menus_tsv, chapters_tsv, shared_c_rows):
    counts = catalog["counts"]
    generated = [
        "runtime/project7_mainline32_data_candidate/catalog-v1.json.gz",
        "runtime/project7_mainline32_data_candidate/contract-v1.json",
        "runtime/project7_mainline32_data_candidate/menus.tsv",
        "runtime/project7_mainline32_data_candidate/chapters.tsv",
        "runtime/project7_mainline32_data_candidate/shared-c-rows.tsv",
        "runtime/project7_mainline32_data_candidate/shared-c-economy.tsv",
        "reports/mainline32-data-candidate.json",
        "reports/mainline32-data-candidate.md",
    ]
    commands = [
        {"command": "python3 tools/project7_mainline32_data_candidate.py --write", "exit": 0, "role": "build candidate assets + reports"},
        {"command": "python3 tools/project7_mainline32_data_candidate.py --check", "exit": 0, "role": "verify pins, hashes, 32 menus, ready=[]"},
    ]
    consumers = [OrderedDict((("field", f), ("shape", s), ("consumer", c), ("bundled", b), ("bundled_where", w))) for f, s, c, b, w in FIELD_CONSUMERS]
    mechanisms = [
        ("entry", "LocalStoryEntryPolicy / LocalWeekEngine", "weeks.tsv route row; score.init_event/requires", "menu week/entry rows", "data present for 32; capability gate unchanged"),
        ("route-selector", "LocalEventCatalog.routes (@route) / LocalServiceEngine", "event_content.enterStoryRoute; event_condition 52", "route.family/branches/evidence per menu", "20 direct, 12 source-semantic; menu8 primitive missing"),
        ("chapter-stage-status", "StoryMissionBridge / LocalCityProgress / LocalChapterCityEngine", "chapter_mission_data key/section/status", "619 chapter rows, 453 scenes", "19 menus have rows; 13 absent; 16 partial branches"),
        ("area-effects", "LocalEventCatalog.cityEffects -> LocalChapterCityEngine.refresh / StoryCityPolicy.refresh", "event_content areaFree/areaFight/areaLock/areaUnlock", "100 area-effect rows", "event_graph has data; StoryCityPolicy scopes menu25 only"),
        ("week-status", "LocalWeekEngine / LocalWeekCatalog", "weeks.tsv route/ending/settlement/score", "week route row per menu", "week rows unchanged; endings/settlement not menu-scoped"),
        ("battle-admission-settlement", "LocalGatewayServer / LocalEconomyEngine", "mission scene ids; economy/suppression rows", "472 generic C + 173 M/G economy rows", "economy rows generated; real Gateway finish/cost still required"),
    ]
    integration = [
        "1. Data only (this ticket): candidate asset + contract + reports; no live selector/COC/Java/Hook edit; ready=[].",
        "2. Feed the 13 shared-table-driven menus' chapter rows (menus 4,9,17,19,20,22,23,24,27,28,29,30,31) into StoryMissionBridge as additional C/A rows and the 173-scene economy M/G rows together; keep selector11 descriptor separate; run the real Gateway finish path and verify the original 640 consumeVictory area<2/-2 cost guard before import; never remove that guard parser-only.",
        "3. Keep menu10 ownership explicit: it spans route10-6 via selector11; family11 alone is not a complete reachability graph.",
        "4. Feed areaFree/areaFight/areaLock/areaUnlock event rows for the same menus into the existing @cityEffect/LocalEventCatalog path; add no second city owner.",
        "5. Extend route selection only through existing LocalEventCatalog.routes/@route and LocalServiceEngine families; route families 2,24,28 remain unclaimed; menu 8 still needs an original @route/trigger witness.",
        "6. Keep week rows (weeks.tsv entry/init/requires) unchanged; they already carry all 32 entries and are consumed by LocalWeekCatalog.",
        "7. Re-run the StoryCity/StoryMission host suites with ready=[]; any later enablement is a separate explicit decision, never a data-candidate side effect.",
    ]
    report = OrderedDict((
        ("schema", "project7-mainline32-data-candidate-report-v1"),
        ("status", "static-data-candidate; no D8/APK/native; no readiness change"),
        ("sources", catalog["source_files"]),
        ("pins", OrderedDict((("source", SOURCE_PINS), ("fixed", FIXED_PINS)))),
        ("outputs", OrderedDict((
            ("catalog", "runtime/project7_mainline32_data_candidate/catalog-v1.json.gz"),
            ("contract", "runtime/project7_mainline32_data_candidate/contract-v1.json"),
            ("menus_tsv", "runtime/project7_mainline32_data_candidate/menus.tsv"),
            ("chapters_tsv", "runtime/project7_mainline32_data_candidate/chapters.tsv"),
            ("shared_c_rows", "runtime/project7_mainline32_data_candidate/shared-c-rows.tsv"),
            ("shared_c_economy", "runtime/project7_mainline32_data_candidate/shared-c-economy.tsv"),
            ("asset_sha256", contract["asset_sha256"]),
            ("expanded_sha256", contract["expanded_sha256"]),
            ("menus_tsv_sha256", contract["menus_tsv_sha256"]),
            ("chapters_tsv_sha256", contract["chapters_tsv_sha256"]),
            ("shared_c_rows_sha256", contract["shared_c_rows_sha256"]),
            ("shared_c_economy_sha256", contract["shared_c_economy_sha256"]),
        ))),
        ("counts", counts),
        ("classification", OrderedDict((
            ("existing-dedicated-primitive", [m["id"] for m in catalog["menus"] if m["primary_class"] == "existing-dedicated-primitive"]),
            ("existing-city-owner", [m["id"] for m in catalog["menus"] if m["primary_class"] == "existing-city-owner"]),
            ("shared-table-driven-chapter", [m["id"] for m in catalog["menus"] if m["primary_class"] == "shared-table-driven-chapter"]),
            ("unknown-normal-city-candidate", [m["id"] for m in catalog["menus"] if m["primary_class"] == "unknown-normal-city-candidate"]),
        ))),
        ("menus", [OrderedDict((
            ("id", m["id"]),
            ("name", m["name"]),
            ("chapter", m["chapter"]),
            ("init_event", m["init_event"]),
            ("requires", m["requires"]),
            ("route_family", m["route"]["family"]),
            ("route_branches", m["route"]["branches"]),
            ("route_evidence_kind", m["route"]["evidence_kind"]),
            ("route_evidence", m["route"]["evidence"]),
            ("chapter_keys", m["chapter_keys"]),
            ("scenes", len(m["scenes"])),
            ("branch_coverage", m["branch_coverage"]),
            ("branches_without_chapter_rows", m["branches_without_chapter_rows"]),
            ("chapter_keys_in_current_mission_catalog", m["fields"]["chapter_keys_in_current_mission_catalog"]),
            ("areas", [area["id"] for area in m["areas"]]),
            ("effect_events", [row["event"] for row in m["effects"]]),
            ("effect_field_counts", m["effect_field_counts"]),
            ("status_values", m["status_values"]),
            ("special_stage_values", m["special_stage_values"]),
            ("bound_event_count", m["events"]["bound_count"]),
            ("selector", m["selector"]),
            ("week", m["week"]),
            ("entry", m["entry"]),
            ("primary_class", m["primary_class"]),
            ("classification_reason", m["classification_reason"]),
            ("consumer_proof", m["consumer_proof"]),
            ("gaps", m["gaps"]),
            ("unconsumed_score_fields", m["fields"]["score_unconsumed"]),
            ("unconsumed_event_fields", m["fields"]["unconsumed_event_fields"]),
            ("ready", False),
        )) for m in catalog["menus"]]),
        ("field_consumers", consumers),
        ("mechanism_coverage", [OrderedDict((("mechanism", m), ("owner", o), ("source_fields", d), ("candidate_rows", c), ("state", st))) for m, o, d, c, st in mechanisms]),
        ("c_row_candidate", catalog["c_row_candidate"]),
        ("economy_candidate", catalog["economy_candidate"]),
        ("limits", [
            "Route families and event binding are data projections; init-chain ∪ route-entry ∪ trigger-52 is an overapproximation, not a reachability/satisfiability proof.",
            "Twelve route-family rows are source-semantic joins recorded in SEMANTIC_EVIDENCE; they are not runtime-observed route selection.",
            "Chapter rows are source rows only; no battle admission, settlement, economy or profile behavior is exercised or claimed.",
        ]),
        ("unclaimed_chapter_rows", catalog["unclaimed_chapter_rows"]),
        ("selector_table_gaps", catalog["selector_table_gaps"]),
        ("integration_order", integration),
        ("commands", commands),
        ("scope_guards", OrderedDict((
            ("live_selector_coc_edited", False),
            ("d8_apk_native", False),
            ("ready_ids", []),
            ("entry_enablement", False),
            ("current_scope_menus", catalog["current_catalog"]["scope_menus"]),
            ("original_entry_supported", list(ORIGINAL_ENTRY_SUPPORTED)),
        ))),
        ("verification", OrderedDict((
            ("asset_sha256", contract["asset_sha256"]),
            ("expanded_sha256", contract["expanded_sha256"]),
            ("menus", counts["menus"]),
            ("ready_ids", []),
        ))),
        ("generated_files", generated),
    ))
    REPORT_JSON.parent.mkdir(exist_ok=True)
    REPORT_JSON.write_text(json.dumps(report, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")

    lines = [
        "# Mainline 32-menu data candidate",
        "",
        "Static data-side candidate only. No D8/APK/native, no entry enablement, no live selector/COC/Java/Hook edit. `ready=[]` and `scope_menus=[]`.",
        "",
        "## Method",
        "- Original 640 literal tables: `mainline_score_info`, `event_content`, `event_condition`, `chapter_mission_data`, `city_data`, `story_route`, `mainline_mutex`, `mission`.",
        "- One deterministic selector row per menu from init-chain `enterStoryRoute` / `mainline_mutex`; 12 rows are source-semantic joins with recorded evidence (const/engine/route-target text). No per-event hand editing.",
        "- Current catalogs read only for scope comparison: StoryCity `scope_menus=[25]`, `ready=[]`; StoryMission only route27 keys.",
        "- Event binding is init-chain `events` ∪ `enterStoryRoute` ∪ trigger-52 events: an overapproximation, not a reachability or satisfiability proof.",
        "",
        "## Counts",
        "- menus: %d; ready_ids: []; entry_enablement: false" % counts["menus"],
        "- classes: %s" % json.dumps(counts["classes"], sort_keys=True),
        "- chapter keys: %d (non-27: %d); scenes: %d; area-effect rows: %d" % (counts["chapter_keys"], counts["non27_chapter_keys"], counts["scenes"], counts["effect_rows"]),
        "- menu25 family27 rows: %d; overlap with current StoryMission catalog: %d" % (counts["menu25_chapter_keys"], counts["menu25_current_catalog_overlap"]),
        "- unclaimed chapter rows: %d routes=%s" % (counts["unclaimed_chapter_keys"], ",".join(counts["unclaimed_routes"])),
        "- menus with chapter rows: %d; without: %d; partial branch coverage: %d" % (counts["menus_with_chapters"], counts["menus_without_chapters"], counts["menus_with_partial_branch_coverage"]),
        "",
        "## Menu table",
        "| # | name | init | route family | branches | chapter keys | scenes | bound events | effect rows | areas | class | entry |",
        "|---:|---|---:|---|---|---:|---:|---:|---:|---|---|---|",
    ]
    for m in catalog["menus"]:
        lines.append("| %s | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s |" % (
            m["id"], m["name"], m["init_event"], m["route"]["family"],
            ",".join(m["route"]["branches"]), m["chapter_keys"], len(m["scenes"]),
            m["events"]["bound_count"], len(m["effects"]),
            ",".join(str(a["id"]) for a in m["areas"]), m["primary_class"],
            "orig" if m["entry"]["original_supports"] else "closed",
        ))
    lines += [
        "",
        "## Data shapes and unconsumed fields",
        "Each menu row carries `score` fields, init-event fields, chapter rows `(chapter,specialStage,route,status)->{0..9:tuple}`, branch coverage, area requirements, area effect rows, week row, selector row and gaps.",
        "",
        "| field | shape | original consumer | bundled | where |",
        "|---|---|---|---|---|",
    ]
    for f, s, c, b, w in FIELD_CONSUMERS:
        lines.append("| `%s` | `%s` | %s | %s | %s |" % (f, s, c, "yes" if b else "no", w or "-"))
    lines += [
        "",
        "## Shared mechanism coverage",
        "| mechanism | owner | source fields | candidate rows | state |",
        "|---|---|---|---|---|",
    ]
    for m, o, d, c, st in mechanisms:
        lines.append("| %s | %s | %s | %s | %s |" % (m, o, d, c, st))
    lines += [
        "",
        "## Generic C/A candidate (shared 13)",
        "- Asset `runtime/project7_mainline32_data_candidate/shared-c-rows.tsv`, sha256 `%s`." % contract["shared_c_rows_sha256"],
        "- 13 shared menus / %d source rows; %d generic C rows; %d selector11 descriptor row `[6,0,10-6,11]` = `[area=6,status=0,route=10-6,specialStage=11]`; %d A rows." % (
            counts["shared_c_rows"]["rows_total"], counts["shared_c_rows"]["generic_c_rows"], counts["shared_c_rows"]["selector11_descriptor_rows"], counts["shared_c_rows"]["a_rows"]),
        "- Original key order is `(area,status,route,specialStage)`; the body row fields agree, so selector11 is `status=0,specialStage=11`, not status11.",
        "- The selector11 row is menu10's descriptor and is not flattened into generic C rows; menu10 family11 alone is not a complete reachability graph.",
        "- Area1 generic rows: %d rows, menus=%s, scenes=%s. Original `LocalCityProgress.dis:223` consumeVictory rejects area<2 with fixed -2 action; verify real Gateway finish against the original 640 cost contract before import, do not remove the guard parser-only." % (
            counts["shared_c_rows"]["area1_rows"], ",".join(map(str, counts["shared_c_rows"]["area1_menus"])), ",".join(map(str, counts["shared_c_rows"]["area1_scenes"]))),
        "- Adding rows alone is not playable: reuse original economy/party/fatigue contracts; this asset is a data candidate only.",
    ]
    lines += [
        "",
        "## Economy candidate (shared 13)",
        "- Asset `runtime/project7_mainline32_data_candidate/shared-c-economy.tsv`, sha256 `%s`." % contract["shared_c_economy_sha256"],
        "- %d distinct scenes, %d M rows, %d G rows; all va=2; existing explicit M coverage %d, missing before %d, missing after 0." % (
            counts["economy"]["scenes"], counts["economy"]["m_rows"], counts["economy"]["g_rows"],
            counts["economy"]["existing_explicit_m_scenes"], counts["economy"]["missing_before"]),
        "- Area1 contract 22010..22012: va2/fatigue5/overFatigue25/party1..3; 22010 cond_event5053, 22011 depends22010, 22012 depends22011 + successEvent10006.",
        "- `LocalEconomyEngine.begin/finish` guard `missions.containsKey(scene)`; absent M skips the mission economy branch and is not a proven hang, but bypasses cost/admission. Candidate M rows close the 148-scene gap; real Gateway finish/cost verification remains required.",
        "- Do not import only C/A: import the economy rows with C/A, then verify original cost/party/fatigue admission.",
    ]
    lines += [
        "",
        "## Exact gaps",
        "- 13 menus have no `chapter_mission_data` rows for their route family: 1(fam1), 2(fam4), 3(fam3), 6(fam7), 7(fam8), 8(fam9), 13(fam14), 14(fam15), 15(fam16), 16(fam17), 18(fam19), 21(fam22), 26(fam29). Data cannot be produced for absent source rows.",
        "- The 9 non-dedicated no-chapter-row menus (1,7,8,14,15,16,18,21,26) are `unknown-normal-city-candidate`, not new engines: normal city data projection with original-consumer proof pending; menu8 carries the explicit route-primitive gap.",
        "- Menu 8 additionally has no route primitive: init 498 closure 499,500,501,503..507,1106..1109 has no `enterStoryRoute` and no trigger-52 route; `std.rt` stays `1`.",
        "- Menu 12 has an existing dedicated engine plus the known `q7WenziCity` rt-10 state-initializer gap.",
        "- Menus 2,3,6,13 have dedicated engines but zero chapter rows; their stage path is engine/event-owned, not chapter-table-owned.",
        "- Partial branch coverage exists where a family has more branches than chapter rows (e.g. 17 fam18: 18/18-1; 27 fam30: 30-1/30-2).",
        "- Only menu 25 (family 27) is in the current StoryCity selector scope; all other families are candidate-only.",
        "- Unclaimed chapter rows outside the 32-menu selector: %d rows on routes %s (route -1 normal-first-week rows and unused families)." % (counts["unclaimed_chapter_keys"], ",".join(counts["unclaimed_routes"])),
        "- Selector-table gaps: story_route family 23 omits 23-5 although chapter rows exist; route -1 rows have no menu family; family 24 rows exist but no menu entry claims them.",
        "",
        "## Per-menu gaps",
    ]
    for m in catalog["menus"]:
        gap_text = "; ".join("%s(%s): %s" % (gap["kind"], gap["id"], gap["detail"]) for gap in m["gaps"]) or "none"
        lines.append("- %d %s: %s. Missing branch rows: %s. Unconsumed score fields: %s. Unconsumed event fields: %s" % (
            m["id"], m["name"], gap_text,
            ",".join(m["branches_without_chapter_rows"]) or "none",
            ",".join(m["fields"]["score_unconsumed"]) or "none",
            ",".join(m["fields"]["unconsumed_event_fields"]) or "none",
        ))
    lines += [
        "",
        "## Staged integration order",
    ]
    lines += ["%s" % step for step in integration]
    lines += [
        "",
        "## Commands",
    ]
    for cmd in commands:
        lines.append("- `%s` -> exit %s (%s)" % (cmd["command"], cmd["exit"], cmd["role"]))
    lines += [
        "",
        "## Hashes",
        "- catalog-v1.json.gz: `%s`" % contract["asset_sha256"],
        "- expanded: `%s`" % contract["expanded_sha256"],
        "- menus.tsv: `%s`" % contract["menus_tsv_sha256"],
        "- chapters.tsv: `%s`" % contract["chapters_tsv_sha256"],
        "- shared-c-rows.tsv: `%s`" % contract["shared_c_rows_sha256"],
        "- shared-c-economy.tsv: `%s`" % contract["shared_c_economy_sha256"],
        "",
        "## Boundaries",
        "- No D8/APK/native, no game execution, no profile/Store mutation.",
        "- No live selector/COC source, menu entry readiness, or production Java/Hook change.",
        "- This report does not claim full mainline gameplay or route completion; it is a reproducible data candidate.",
    ]
    REPORT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def check():
    contract = json.loads((OUT / "contract-v1.json").read_text(encoding="utf-8"))
    require(contract["schema"] == SCHEMA, "Contract schema")
    require(contract["ready_ids"] == [] and contract["scope_menus"] == [], "Readiness changed")
    asset = (OUT / "catalog-v1.json.gz").read_bytes()
    require(sha(asset) == contract["asset_sha256"], "Candidate asset hash changed")
    raw = gzip.decompress(asset)
    require(sha(raw) == contract["expanded_sha256"], "Expanded hash changed")
    catalog = json.loads(raw)
    require(catalog["schema"] == SCHEMA, "Catalog schema")
    require(catalog["ready_ids"] == [] and catalog["entry_enablement"] is False, "Catalog readiness")
    require(len(catalog["menus"]) == 32, "Menu count")
    require([m["id"] for m in catalog["menus"]] == list(range(1, 33)), "Menu order")
    require(all(m["ready"] is False and m["entry"]["enable_entry"] is False for m in catalog["menus"]), "Menu readiness")
    require(Counter(m["primary_class"] for m in catalog["menus"]) == Counter({
        "existing-dedicated-primitive": 9,
        "existing-city-owner": 1,
        "shared-table-driven-chapter": 13,
        "unknown-normal-city-candidate": 9,
    }), "Classification count")
    require(len({m["route"]["family"] for m in catalog["menus"]}) == 32, "Route family uniqueness")
    require(sha((OUT / "menus.tsv").read_bytes()) == contract["menus_tsv_sha256"], "menus.tsv hash")
    require(sha((OUT / "chapters.tsv").read_bytes()) == contract["chapters_tsv_sha256"], "chapters.tsv hash")
    shared_c = (OUT / "shared-c-rows.tsv").read_bytes()
    require(sha(shared_c) == contract["shared_c_rows_sha256"], "shared-c-rows.tsv hash")
    require(sum(1 for line in shared_c.decode().splitlines() if line.startswith("C\t")) == 472, "shared generic C row count")
    require(sum(1 for line in shared_c.decode().splitlines() if line.startswith("A\t")) == contract["shared_c_rows"]["a_rows"], "shared A row count")
    economy = (OUT / "shared-c-economy.tsv").read_bytes()
    require(sha(economy) == contract["shared_c_economy_sha256"], "shared-c-economy.tsv hash")
    require(sum(1 for line in economy.decode().splitlines() if line.startswith("M\t")) == 173, "economy M row count")
    require(all(line.split("\t")[2] == "2" for line in economy.decode().splitlines() if line.startswith("M\t")), "economy va distribution")
    require((REPORT_JSON).exists() and (REPORT_MD).exists(), "Reports missing")
    report = json.loads(REPORT_JSON.read_text(encoding="utf-8"))
    require(report["outputs"]["asset_sha256"] == contract["asset_sha256"], "Report asset hash")
    require(report["scope_guards"]["ready_ids"] == [] and report["scope_guards"]["entry_enablement"] is False, "Report readiness")
    print("PASS mainline32 data candidate: menus=32 ready=[] classes=%s" % json.dumps(catalog["counts"]["classes"], sort_keys=True))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.write:
        catalog, catalog_bytes, gz, contract, contract_bytes, menus_tsv, chapters_tsv, shared_c_rows, shared_c_economy = build()
        OUT.mkdir(parents=True, exist_ok=True)
        (OUT / "catalog-v1.json.gz").write_bytes(gz)
        (OUT / "contract-v1.json").write_bytes(contract_bytes)
        (OUT / "menus.tsv").write_bytes(menus_tsv)
        (OUT / "chapters.tsv").write_bytes(chapters_tsv)
        (OUT / "shared-c-rows.tsv").write_bytes(shared_c_rows)
        (OUT / "shared-c-economy.tsv").write_bytes(shared_c_economy)
        write_report(catalog, contract, catalog_bytes, gz, menus_tsv, chapters_tsv, shared_c_rows)
        check()
        return
    if args.check:
        check()
        return
    parser.error("choose --write or --check")


if __name__ == "__main__":
    main()
