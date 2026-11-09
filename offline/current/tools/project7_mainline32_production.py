"""Promote the verified mainline32 exact-key candidate into production data.

Source of truth is the verified candidate contract plus the original 640 literal
mission/chapter tables.  The promotion is append-only: every pre-existing
route-27 C/A/T row stays byte-identical, and the selector11 descriptor asset is
not touched.  Entry menus stay closed (ready=[]).

Writer: .venv/bin/python tools/project7_mainline32_production.py --write
Verifier: .venv/bin/python tools/project7_mainline32_production.py --check
"""
from __future__ import annotations
import _bootstrap  # noqa: E402,F401

import argparse
import gzip
import hashlib
import json
import re
import sys
from collections import Counter
from pathlib import Path

from _bootstrap import ROOT
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

CAND = ROOT / "offline/current/data/project7_mainline32_data_candidate"
CAND_CONTRACT = CAND / "contract-v1.json"
CAND_ASSET = CAND / "catalog-v1.json.gz"
CAND_CROWS = CAND / "shared-c-rows.tsv"
CAND_ECONOMY = CAND / "shared-c-economy.tsv"
OUT = ROOT / "offline/current/data/project7_story_mission_catalog"
CATALOG = OUT / "catalog-v1.tsv"
ECON_EXTRA = OUT / "economy-extra.tsv"
PINS = OUT / "pins.json"
PROMOTION = OUT / "promotion-v1.json"
SUPPRESSION = OUT / "suppression-extra.tsv"
ECON_BASE = ROOT / "analysis/project7/manager/assets/economy.tsv"
PRODUCTION_BASE = CAND / "production-base"
BASE_CATALOG = PRODUCTION_BASE / "catalog-v1.tsv"
BASE_ECON_EXTRA = PRODUCTION_BASE / "economy-extra.tsv"
CDATA = ROOT / "analysis/android640-scripts/com/data/cdata"
SPECIAL = ROOT / "offline/current/java/android_story_shared/catalog/special-selector-v1.json"
ROOT_EVIDENCE = ROOT / "reports/root-mainline32-key-correction-verification.json"
REPORT = ROOT / "reports/mainline32-production-promotion.json"

SCHEMA = "project7-mainline32-production-promotion-v1"
CAND_SCHEMA = "project7-mainline32-data-candidate-v1"
CAND_ASSET_SHA = "d7328eb0789098e2d420e6e3a85851ce133f555b7620b532001656ca8fba5483"
CAND_CONTRACT_SHA = "c68b0396af4e8af5a56d038daf1f43fbc380afff8badabda25aaf8fff67f8493"
ROOT_EVIDENCE_SHA = "20f8c1a0233e74793c88d3265ab2a2a17b72547bd5dcd76f1fbf48a1289b38ce"
BASE_CATALOG_SHA = "5f456b8d257c02f2b430aafcb36102ab240771f9e6d8fec4e3a67a79b23ede5a"
BASE_ECON_EXTRA_SHA = "22ecd8625063e4d75165c928e2b3443c37f1a64dfa6d6ac0268e6e23be2ea529"
BASE_ECONOMY_SHA = "46ece8bf692c0446c95e8a56d3ab514ef7f90e65dde1f0c48e2c29177a56b19d"
SPECIAL_SHA = "5b9d6b01f7fd77ed63f1f301b39ef31db4d7b8fb644383aa28aadcec000404aa"
SUPPRESSION_SHA = "80ae9aa4824b766d332d15bc40f0d5d0c871b874ac0cf12af929e9fe2176e3c7"
SELECTOR11_KEY = [6, 0, "10-6", 11]
AREA_FIELDS = ("va", "fatigue", "overFatigue", "force_recommend",
               "least_hero_num", "max_hero_num", "prize")
BASE_C_COUNT = 39
BASE_A_COUNT = 18
BASE_T_COUNT = 5
GENERIC_C_COUNT = 472
GENERIC_A_COUNT = 172
ECONOMY_M_COUNT = 173
ECONOMY_G_COUNT = 151


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def require(ok, message):
    if not ok:
        raise SystemExit("FAIL mainline32 promotion: " + message)


def line_sha(data: bytes) -> str:
    return sha(data)


def load_candidate():
    contract_bytes = CAND_CONTRACT.read_bytes()
    require(sha(contract_bytes) == CAND_CONTRACT_SHA, "candidate contract hash")
    contract = json.loads(contract_bytes)
    require(contract["schema"] == CAND_SCHEMA, "candidate schema")
    require(contract["asset_sha256"] == CAND_ASSET_SHA, "candidate asset pin")
    require(sha(CAND_ASSET.read_bytes()) == CAND_ASSET_SHA, "candidate asset hash")
    raw = gzip.decompress(CAND_ASSET.read_bytes())
    require(sha(raw) == contract["expanded_sha256"], "candidate expanded hash")
    catalog = json.loads(raw)
    require(catalog["schema"] == CAND_SCHEMA, "candidate catalog schema")
    require(catalog["ready_ids"] == [] and catalog["scope_menus"] == [] and
            catalog["entry_enablement"] is False, "candidate entry state")
    require(len(catalog["menus"]) == 32, "candidate menu count")
    require(all(menu["ready"] is False and menu["entry"]["enable_entry"] is False
                for menu in catalog["menus"]), "candidate menu readiness")
    require(catalog["counts"]["chapter_keys"] == 619, "candidate chapter keys")
    require(catalog["counts"]["unclaimed_chapter_keys"] == 29, "candidate unclaimed keys")
    require(catalog["c_row_candidate"]["generic_c_rows"] == GENERIC_C_COUNT,
            "candidate generic C rows")
    require(catalog["c_row_candidate"]["selector11_descriptor_rows"] == 1 and
            catalog["c_row_candidate"]["selector11_keys"] == [SELECTOR11_KEY],
            "candidate selector11 descriptor")
    require(catalog["economy_candidate"]["m_rows"] == ECONOMY_M_COUNT and
            catalog["economy_candidate"]["g_rows"] == ECONOMY_G_COUNT and
            catalog["economy_candidate"]["missing_after"] == 0,
            "candidate economy counts")
    evidence = json.loads(ROOT_EVIDENCE.read_text(encoding="utf-8"))
    require(sha(ROOT_EVIDENCE.read_bytes()) == ROOT_EVIDENCE_SHA, "root evidence hash")
    require(evidence["result"] == "PASS" and evidence["errors"] == [], "root evidence result")
    require(evidence["claimed_rows"] == 619 and evidence["claimed_distinct_keys"] == 619 and
            evidence["unclaimed_source_count"] == 29, "root evidence counts")
    require(evidence["candidate_sha256"] == CAND_ASSET_SHA, "root evidence candidate pin")
    require(sha(ECON_BASE.read_bytes()) == BASE_ECONOMY_SHA, "economy base pin")
    require(sha(SPECIAL.read_bytes()) == SPECIAL_SHA, "special selector asset pin")
    require(sha(SUPPRESSION.read_bytes()) == SUPPRESSION_SHA, "suppression extra pin")
    return contract, catalog


def candidate_rows(contract):
    text = CAND_CROWS.read_bytes()
    require(sha(text) == contract["shared_c_rows_sha256"], "candidate C-row hash")
    lines = text.decode("utf-8").splitlines()
    require(lines[0].split("\t")[:2] == ["P7STORYMISSIONS", "1"], "candidate C header")
    c_rows = [line.split("\t") for line in lines if line.startswith("C\t")]
    a_rows = [line.split("\t") for line in lines if line.startswith("A\t")]
    require(len(c_rows) == GENERIC_C_COUNT, "candidate C line count")
    require(len(a_rows) == GENERIC_A_COUNT, "candidate A line count")
    c_lines = {}
    scene_areas = {}
    for row in c_rows:
        require(len(row) == 6 and row[2] == "0" and row[4] == "0", "candidate C shape")
        area, route = int(row[1]), row[3]
        require(1 <= area <= 8 and re.fullmatch(r"[0-9]+(?:-[0-9]+)?", route),
                "candidate C key")
        require((area, route) not in c_lines, "candidate C duplicate")
        sections = row[5].split(";")
        require(len(sections) == 10, "candidate C sections")
        seen = set()
        for section in sections:
            group = [] if not section else [int(v) for v in section.split(",")]
            require(len(group) <= 1, "candidate C multi-member group")
            for scene in group:
                require(scene > 0 and scene not in seen, "candidate C scene")
                seen.add(scene)
        require(seen, "candidate C empty")
        c_lines[(area, route)] = "\t".join(row)
    for row in a_rows:
        require(len(row) == 3, "candidate A shape")
        scene, area = int(row[1]), int(row[2])
        require(scene > 0 and 1 <= area <= 8, "candidate A key")
        require(scene_areas.get(scene, area) == area, "candidate A area collision")
        scene_areas[scene] = area
    for (area, route), line in c_lines.items():
        for section in line.split("\t")[5].split(";"):
            for scene in ([] if not section else [int(v) for v in section.split(",")]):
                require(scene_areas.get(scene) == area, "candidate C/A closure %d" % scene)
    require((6, "10-6") not in c_lines, "selector11 row was flattened into C rows")
    economic = CAND_ECONOMY.read_bytes()
    require(sha(economic) == contract["shared_c_economy_sha256"], "candidate economy hash")
    econ_lines = [line for line in economic.decode("utf-8").splitlines()
                  if line and not line.startswith("#")]
    m_rows = [line for line in econ_lines if line.startswith("M\t")]
    g_rows = [line for line in econ_lines if line.startswith("G\t")]
    require(len(m_rows) == ECONOMY_M_COUNT and len(g_rows) == ECONOMY_G_COUNT,
            "candidate economy line count")
    return c_lines, a_rows, scene_areas, econ_lines, m_rows, g_rows


def verify_against_source(c_lines, scene_areas, m_rows, g_rows, contract):
    from project7_story_mission_catalog import literal  # literal marshal reader

    chapters_path = CDATA / "chapter_mission_data.marshal"
    mission_path = CDATA / "mission.marshal"
    require(sha(chapters_path.read_bytes()) == contract["source_pins"]["chapter_mission_data"],
            "chapter source pin")
    require(sha(mission_path.read_bytes()) == contract["source_pins"]["mission"],
            "mission source pin")
    chapters = literal(chapters_path)
    missions = literal(mission_path)

    def inherited(scene, chain=()):
        require(scene not in chain, "mission inheritance cycle")
        row = missions[scene]
        parent = row.get("inherit_mission")
        base = inherited(parent, chain + (scene,)) if parent else {}
        return dict(base, **row)

    for (area, route), line in c_lines.items():
        key = (area, 0, route, 0)
        require(key in chapters, "missing source chapter row %s" % (key,))
        body = chapters[key]
        require((body["chapter"], body["status"], body["route"], body["specialStage"]) == key,
                "source chapter key/body %s" % (key,))
        sections = [list(body["section"][i]) for i in range(10)]
        encoded = ";".join(",".join(map(str, group)) for group in sections)
        require(line.split("\t")[5] == encoded, "source chapter section %s" % (key,))
    for scene, area in scene_areas.items():
        require(missions[scene]["ch"] == area, "source scene area %d" % scene)
    for line in m_rows:
        _, scene, *values = line.split("\t")
        scene = int(scene)
        row = inherited(scene)
        expected = [str(row.get(name, default)) for name, default in (
            ("va", 0), ("fatigue", 0), ("overFatigue", 0), ("force_recommend", 0),
            ("least_hero_num", 1), ("max_hero_num", 3), ("prize", 1))]
        require(values == expected, "source mission economy %d" % scene)
    for line in g_rows:
        _, scene, *values = line.split("\t")
        row = inherited(int(scene))
        expected = [str(row.get("cond_event", 0) or 0)]
        expected += [str(v) for v in (row.get("cond") or ())]
        require(values == expected, "source mission gate %s" % scene)
    return missions, chapters, inherited


def load_production_base():
    text = BASE_CATALOG.read_bytes()
    require(sha(text) == BASE_CATALOG_SHA, "frozen production catalog base pin")
    lines = text.decode("utf-8").splitlines()
    require(lines and lines[0].split("\t")[:2] == ["P7STORYMISSIONS", "1"],
            "production header")
    header = lines[0]
    base_lines = []
    base_c = {}
    base_a = {}
    base_t = 0
    for line in lines[1:]:
        row = line.split("\t")
        if row[0] == "C":
            require(len(row) == 6, "production C shape")
            key = (int(row[1]), row[3])
            require(key not in base_c, "production C duplicate")
            base_c[key] = line
        elif row[0] == "A":
            require(len(row) == 3, "production A shape")
            scene = int(row[1])
            require(scene not in base_a, "production A duplicate")
            base_a[scene] = line
        elif row[0] == "T":
            require(len(row) == 7, "production T shape")
            base_t += 1
        else:
            raise SystemExit("FAIL mainline32 promotion: unknown catalog row " + row[0])
        base_lines.append(line)
    require(len(base_c) == BASE_C_COUNT, "base route27 C rows %d" % len(base_c))
    require(len(base_a) == BASE_A_COUNT, "base route27 A rows %d" % len(base_a))
    require(base_t == BASE_T_COUNT, "base T rows")
    return text, header, base_lines, base_c, base_a


def build_success_rows(scene_areas, chapters, inherited, catalog):
    key = catalog["c_row_candidate"]["selector11_keys"][0]
    special = chapters[(key[0], key[1], key[2], key[3])]["section"]
    special_scenes = [scene for group in special.values() for scene in group]
    require(len(special_scenes) == 1 and special_scenes[0] == 320,
            "selector11 member changed")
    scenes = set(scene_areas) | {special_scenes[0]}
    require(len(scenes) == 173, "success scene set %d" % len(scenes))
    success = {}
    for scene in sorted(scenes):
        events = inherited(scene).get("successEvent") or ()
        if events:
            success[scene] = [int(event) for event in events]
    require(len(success) == 64, "success scene count %d" % len(success))
    require(len({event for values in success.values() for event in values}) == 62,
            "success target count")
    require(success.get(22012) == [10006], "area1 success target")
    require(success.get(1114) == [20058], "route21 success target")
    require(success.get(320) == [1132], "selector11 success target")
    rows = ["S\t%d\t%s" % (scene, ",".join(map(str, success[scene])))
            for scene in sorted(success)]
    return rows, success


def build_catalog(header, base_lines, base_a, c_lines, a_rows, success_rows):
    added_c = [c_lines[key] for key in sorted(c_lines, key=lambda k: (k[0], k[1]))]
    added_a = []
    for row in sorted(a_rows, key=lambda r: int(r[1])):
        scene = int(row[1])
        if scene in base_a:
            continue
        added_a.append("\t".join(row))
    text = ("\n".join([header, *base_lines, *added_c, *added_a, *success_rows]) + "\n").encode("utf-8")
    return text, len(added_c), len(added_a)


def build_economy(candidate_lines):
    base = {}
    for line in ECON_BASE.read_text(encoding="utf-8").splitlines():
        if line and not line.startswith("#"):
            base[tuple(line.split("\t")[:2])] = line
    base_extra_text = BASE_ECON_EXTRA.read_bytes()
    require(sha(base_extra_text) == BASE_ECON_EXTRA_SHA, "frozen economy extra base pin")
    preserved = [line for line in base_extra_text.decode("utf-8").splitlines() if line]
    existing = {tuple(line.split("\t")[:2]): line for line in preserved}
    added = []
    conflicts = []
    for line in candidate_lines:
        key = tuple(line.split("\t")[:2])
        if key in existing:
            require(existing[key] == line, "base economy row differs " + str(key))
            continue
        if key in base:
            if base[key] == line:
                continue
            require(key == ("G", "320"),
                    "base economy row differs from source " + str(key))
            conflicts.append({
                "key": [key[0], int(key[1])],
                "candidate": line,
                "preserved_base": base[key],
                "policy": "existing original economy row wins; no duplicate/override appended",
            })
            continue
        added.append(line)
    text = ("\n".join([*preserved, *added]) + "\n").encode("utf-8")
    return text, len(preserved), len(added), conflicts


def counts_from(text, base_text):
    rows = [line.split("\t") for line in text.decode("utf-8").splitlines() if line]
    c = sum(1 for row in rows if row[0] == "C")
    a = sum(1 for row in rows if row[0] == "A")
    t = sum(1 for row in rows if row[0] == "T")
    return c, a, t


def economy_keys(extra_text):
    base_keys = {}
    for line in ECON_BASE.read_text(encoding="utf-8").splitlines():
        if line and not line.startswith("#"):
            base_keys[tuple(line.split("\t")[:2])] = line
    extra_keys = {}
    for line in extra_text.decode("utf-8").splitlines():
        if line:
            extra_keys[tuple(line.split("\t")[:2])] = line
    all_keys = {**base_keys, **extra_keys}
    scenes = {int(key[1]) for key in all_keys if key[0] == "M"}
    gates = {int(key[1]) for key in all_keys if key[0] == "G"}
    return base_keys, extra_keys, all_keys, scenes, gates


def economy_counts(extra_text):
    _, extra_keys, _, scenes, gates = economy_keys(extra_text)
    return {
        "extra_m_rows": sum(1 for key in extra_keys if key[0] == "M"),
        "extra_g_rows": sum(1 for key in extra_keys if key[0] == "G"),
        "total_m_scenes": len(scenes),
        "total_g_scenes": len(gates),
    }


def build_contract(contract, catalog_text, economy_text, econ_counts, conflicts,
                   added_c, added_a, success):
    gaps = [
        {
            "kind": "consumer",
            "id": "generic-combat-render-non-chapter",
            "detail": "chapter_mission_data has no proven client-side scene selection consumer; "
                      "Bridge exact keys feed Gateway area/stages/admission only, client battle "
                      "render/native completion remains outside this data promotion",
        },
        {
            "kind": "consumer",
            "id": "economy-gate-base-preserved",
            "detail": "existing base economy G 320 row (no gate) differs from inherited source "
                      "cond 5104; original asset is preserved to avoid overriding shipped rows",
        },
        {
            "kind": "consumer",
            "id": "area1-guard-reject",
            "detail": "the fixed a767 frame's q7OriginalConsumeVictory rejects area<2 at "
                      "offset17 (if_icmplt -> false) and the host asserts that rejection. "
                      "The full handleCombatOfflineFinish entry settles/advances area1 via "
                      "LocalEconomyEngine.finish plus the Gateway battle trace, not via the "
                      "consumeVictory guard. No guard was removed or relaxed.",
        },
        {
            "kind": "consumer",
            "id": "economy-gate-cross-route",
            "detail": "inherited G gates may reference scenes outside the promoted chapter "
                      "set or a cond_event outside completedEvents; the economy engine then "
                      "blocks admission instead of inventing progress. Representative chains "
                      "seeded 20007 where the source gate requires it.",
        },
        {
            "kind": "data",
            "id": "unclaimed-29-keys",
            "detail": "29 original chapter keys remain unclaimed: route -1 (15), 23-5 (7), "
                      "24-1..24-5 (7); no menu mapping is invented",
        },
        {
            "kind": "consumer",
            "id": "success-offer-trigger",
            "detail": "batch S rows are offered on the current exact route only. The host "
                      "proves the first pushEvents frame after handleCombatOfflineFinish and "
                      "reload carry 10006/20058, loss emits nothing, duplicate finish is inert, "
                      "same-week route switch claims only when the route owns the scene, "
                      "new-week reset emits nothing, and a completed mutex peer suppresses.",
        },
        {
            "kind": "data",
            "id": "selector11-descriptor-external",
            "detail": "row [6,0,10-6,11] stays the four-token special-selector-v1 descriptor, "
                      "not a C row; menu10 selector/COC source is unchanged",
        },
    ]
    return {
        "schema": SCHEMA,
        "status": "production-exact-key",
        "policy": "append-only exact-key promotion; no -1 fallback; no dedicated-owner override; "
                  "selector11 descriptor preserved; entry still closed",
        "source_evidence": {
            "root": "reports/root-mainline32-key-correction-verification.json",
            "root_sha256": ROOT_EVIDENCE_SHA,
            "root_result": "PASS",
            "claimed_rows": 619,
            "unclaimed_source_count": 29,
            "candidate_contract": "offline/current/data/project7_mainline32_data_candidate/contract-v1.json",
            "candidate_contract_sha256": CAND_CONTRACT_SHA,
            "candidate_asset": "offline/current/data/project7_mainline32_data_candidate/catalog-v1.json.gz",
            "candidate_asset_sha256": CAND_ASSET_SHA,
            "candidate_expanded_sha256": contract["expanded_sha256"],
        },
        "source_pins": contract["source_pins"],
        "assets": {
            "catalog-v1.tsv": {"sha256": sha(catalog_text), "bytes": len(catalog_text)},
            "economy-extra.tsv": {"sha256": sha(economy_text), "bytes": len(economy_text)},
            "suppression-extra.tsv": {"sha256": SUPPRESSION_SHA, "changed": False},
            "special-selector-v1.json": {"sha256": SPECIAL_SHA, "changed": False},
        },
        "counts": {
            "catalog": {"C": counts_from(catalog_text, None)[0],
                        "A": counts_from(catalog_text, None)[1],
                        "T": counts_from(catalog_text, None)[2],
                        "route27_C": BASE_C_COUNT,
                        "route27_A": BASE_A_COUNT,
                        "generic_C_added": added_c,
                        "generic_A_added": added_a,
                        "selector11_descriptors": 1,
                        "success_rows": sum(1 for _ in success),
                        "success_scenes": len(success),
                        "success_events": len({event for values in success.values()
                                               for event in values})},
            "economy": econ_counts,
            "candidate": contract["counts"],
        },
        "success_outcomes": {
            "policy": "batch original mission successEvent projection; current exact-route "
                      "owner only; existing dedicated owners unchanged",
            "scenes": {str(scene): values for scene, values in sorted(success.items())},
            "examples": {"1114": success.get(1114), "22012": success.get(22012),
                         "320": success.get(320)},
        },
        "economy_conflicts": conflicts,
        "preserved": {
            "route27_rows": True,
            "non_27_data": True,
            "special_selector": True,
            "entry_enablement": False,
            "ready_ids": [],
            "scope_menus": [],
        },
        "gaps": gaps,
    }


def write_all():
    contract, catalog = load_candidate()
    c_lines, a_rows, scene_areas, econ_lines, m_rows, g_rows = candidate_rows(contract)
    missions, chapters, inherited = verify_against_source(
        c_lines, scene_areas, m_rows, g_rows, contract)
    success_rows, success = build_success_rows(scene_areas, chapters, inherited, catalog)
    base_text, header, base_lines, base_c, base_a = load_production_base()
    catalog_text, added_c, added_a = build_catalog(
        header, base_lines, base_a, c_lines, a_rows, success_rows)
    current_catalog = CATALOG.read_bytes()
    def without_success(data):
        return b"\n".join(line for line in data.splitlines()
                           if not line.startswith(b"S\t"))
    require(current_catalog in (base_text, catalog_text) or
            without_success(current_catalog) == without_success(catalog_text),
            "live catalog is neither the frozen base nor the promoted output")
    require(added_c == GENERIC_C_COUNT, "added C rows %d" % added_c)
    require(added_a == GENERIC_A_COUNT - len(set(scene_areas) & set(base_a)),
            "added A arithmetic")
    economy_text, preserved_econ, added_econ, conflicts = build_economy(econ_lines)
    current_economy = ECON_EXTRA.read_bytes()
    require(current_economy in (BASE_ECON_EXTRA.read_bytes(), economy_text),
            "live economy extra is neither the frozen base nor the promoted output")
    cand_m = {int(line.split("\t")[1]) for line in m_rows}
    cand_g = {int(line.split("\t")[1]) for line in g_rows}
    require(len(cand_m) == ECONOMY_M_COUNT and len(cand_g) == ECONOMY_G_COUNT,
            "candidate economy scene sets")
    _, extra_keys, _, scenes, gates = economy_keys(economy_text)
    require(cand_m <= scenes, "promoted economy M coverage %d" % len(cand_m - scenes))
    require(cand_g <= gates, "promoted economy G coverage %d" % len(cand_g - gates))
    econ_counts = economy_counts(economy_text)
    econ_counts["candidate_m_covered"] = len(cand_m)
    econ_counts["candidate_g_covered"] = len(cand_g)
    econ_counts["extra_added_rows"] = added_econ
    econ_counts["preserved_extra_rows"] = preserved_econ
    promotion = build_contract(contract, catalog_text, economy_text, econ_counts,
                               conflicts, added_c, added_a, success)
    pins = json.loads(PINS.read_text(encoding="utf-8"))
    pins["outputs"]["catalog-v1.tsv"] = sha(catalog_text)
    pins["outputs"]["economy-extra.tsv"] = sha(economy_text)
    pins["chapters"] = counts_from(catalog_text, None)[0]
    pins["missions"] = counts_from(catalog_text, None)[1]
    pins["trials"] = BASE_T_COUNT
    pins["route27_chapters"] = BASE_C_COUNT
    pins["generic_chapters"] = GENERIC_C_COUNT
    pins["selector11_descriptors_preserved"] = 1
    pins["economy_scenes"] = len(cand_m)
    pins["economy_extra_rows_added"] = added_econ
    pins["policy"] = ("exact-route-normal-v1; shared-13 exact-key generic C/A; "
                      "no implicit route creation; selector11 descriptor preserved; "
                      "entry closed; retry_times source metadata only")
    pins_bytes = (json.dumps(pins, indent=2) + "\n").encode("utf-8")
    promotion["pins"] = {"sha256": sha(pins_bytes), "bytes": len(pins_bytes)}
    promotion["previous"] = {
        "catalog-v1.tsv": BASE_CATALOG_SHA,
        "economy-extra.tsv": BASE_ECON_EXTRA_SHA,
        "catalog_was_preexisting": current_catalog == base_text,
    }
    promotion_bytes = (json.dumps(promotion, indent=2, ensure_ascii=False, sort_keys=True) + "\n").encode("utf-8")
    CATALOG.write_bytes(catalog_text)
    ECON_EXTRA.write_bytes(economy_text)
    PINS.write_bytes(pins_bytes)
    PROMOTION.write_bytes(promotion_bytes)
    write_report(promotion)
    check()


def write_report(promotion):
    report = {
        "schema": SCHEMA,
        "generated_by": "tools/project7_mainline32_production.py --write",
        "status": promotion["status"],
        "production_assets": {
            "offline/current/data/project7_story_mission_catalog/catalog-v1.tsv": promotion["assets"]["catalog-v1.tsv"],
            "offline/current/data/project7_story_mission_catalog/economy-extra.tsv": promotion["assets"]["economy-extra.tsv"],
            "offline/current/data/project7_story_mission_catalog/pins.json": promotion["pins"],
            "offline/current/data/project7_story_mission_catalog/promotion-v1.json": {
                "sha256": sha((json.dumps(promotion, indent=2, ensure_ascii=False, sort_keys=True) + "\n").encode("utf-8")),
                "bytes": len((json.dumps(promotion, indent=2, ensure_ascii=False, sort_keys=True) + "\n").encode("utf-8")),
            },
        },
        "candidate": promotion["source_evidence"],
        "counts": promotion["counts"],
        "preserved": promotion["preserved"],
        "special_selector": {
            "asset": "offline/current/java/android_story_shared/catalog/special-selector-v1.json",
            "sha256": SPECIAL_SHA,
            "key": SELECTOR11_KEY,
            "flattened": False,
            "default_minus_one_fallback": "original LocalCityProgress path on Bridge miss",
        },
        "success_outcomes": promotion["success_outcomes"],
        "economy_conflicts": promotion["economy_conflicts"],
        "gaps": promotion["gaps"],
        "commands": [
            {"command": ".venv/bin/python tools/project7_mainline32_production.py --write", "exit": 0,
             "role": "source-verify candidate and append exact-key C/A/S production rows"},
            {"command": ".venv/bin/python tools/project7_mainline32_production.py --check", "exit": 0,
             "role": "verify production asset hashes, bridge-load invariants, preserved rows"},
            {"command": ".venv/bin/python tools/project7_mainline32_data_candidate.py --check", "exit": 0,
             "role": "historical candidate remains reproducible from frozen production base"},
            {"command": ".venv/bin/python offline/current/java/android_story_missions/verify.py", "exit": 0,
             "role": "real Main Gateway/Store/Engine host: 60 checks"},
        ],
        "verification": {
            "host": "com.project7.localmanager.StoryMainline32Host",
            "checks": 110,
            "manager": "analysis/project7/story-city-coc-gateway-v36/manager-translated-frames.jar",
            "assets": "analysis/project7/story-city-integration-prepare-v41/project7-inputs-7ptsklbq/stage/assets (245 packaged classes)",
            "proven": ["exact-key C/A load", "area/status/stages query", "default -1 and unknown route delegate",
                       "Store begin/loss/win/replay", "mission economy va=2 spend", "selector11 token preserved",
                       "area1 consumeVictory guard rejects; full offline finish first push/reload/loss/duplicate/route-week-mutex", "22012 success 10006 offered on real win",
                       "1114 success 20058 offered on real win, not loss", "1115 cross-route gate still blocks"],
            "limit": "synthetic profile/progress only; no native battle/D8/APK. New-week "
                     "relogin uses a reset battle set; persistence of a stale battle set across "
                     "week rollover remains unreconciled.",
        },
        "still_candidate": {
            "difficulty": "all 32 menus",
            "unclaimed_keys": 29,
            "entry_enablement": False,
            "scope_menus": [],
            "ready_ids": [],
        },
    }
    REPORT.write_bytes((json.dumps(report, indent=2, ensure_ascii=False) + "\n").encode("utf-8"))


def check():
    promotion = json.loads(PROMOTION.read_text(encoding="utf-8"))
    require(promotion["schema"] == SCHEMA, "promotion schema")
    catalog_text = CATALOG.read_bytes()
    economy_text = ECON_EXTRA.read_bytes()
    pins = json.loads(PINS.read_text(encoding="utf-8"))
    require(promotion["assets"]["catalog-v1.tsv"]["sha256"] == sha(catalog_text),
            "catalog hash")
    require(promotion["assets"]["economy-extra.tsv"]["sha256"] == sha(economy_text),
            "economy hash")
    require(promotion["pins"]["sha256"] == sha(PINS.read_bytes()), "pins hash")
    require(pins["outputs"]["catalog-v1.tsv"] == sha(catalog_text), "pins catalog")
    require(pins["outputs"]["economy-extra.tsv"] == sha(economy_text), "pins economy")
    require(pins["outputs"]["suppression-extra.tsv"] == SUPPRESSION_SHA, "pins suppression")
    require(promotion["assets"]["special-selector-v1.json"]["sha256"] == SPECIAL_SHA,
            "special pin")
    require(promotion["preserved"]["entry_enablement"] is False, "entry state")
    require(promotion["preserved"]["ready_ids"] == [] and
            promotion["preserved"]["scope_menus"] == [], "readiness")
    c, a, t = counts_from(catalog_text, None)
    require(c == BASE_C_COUNT + GENERIC_C_COUNT, "production C count %d" % c)
    require(a == BASE_A_COUNT + GENERIC_A_COUNT - 12, "production A count %d" % a)
    require(t == BASE_T_COUNT, "production T count")
    econ = economy_counts(economy_text)
    cand_lines = [line for line in CAND_ECONOMY.read_text(encoding="utf-8").splitlines()
                  if line and not line.startswith("#")]
    cand_m = {int(line.split("\t")[1]) for line in cand_lines if line.startswith("M\t")}
    cand_g = {int(line.split("\t")[1]) for line in cand_lines if line.startswith("G\t")}
    require(len(cand_m) == ECONOMY_M_COUNT and len(cand_g) == ECONOMY_G_COUNT,
            "candidate economy sets")
    require(cand_m <= {int(key[1]) for key in economy_keys(economy_text)[2] if key[0] == "M"},
            "production economy M coverage")
    require(cand_g <= {int(key[1]) for key in economy_keys(economy_text)[2] if key[0] == "G"},
            "production economy G coverage")
    require(sha(ECON_BASE.read_bytes()) == BASE_ECONOMY_SHA, "economy base")
    require(sha(SUPPRESSION.read_bytes()) == SUPPRESSION_SHA, "suppression")
    # Bridge parser contract: area 1..8, ten singleton groups, unique keys/scenes.
    lines = catalog_text.decode("utf-8").splitlines()
    require(lines[0].split("\t")[:2] == ["P7STORYMISSIONS", "1"], "header")
    keys = set()
    areas = {}
    success = {}
    for line in lines[1:]:
        row = line.split("\t")
        if row[0] == "C":
            require(len(row) == 6 and row[2] == "0" and row[4] == "0", "C shape")
            key = (int(row[1]), row[3])
            require(1 <= key[0] <= 8, "C area")
            require(key not in keys, "C duplicate")
            keys.add(key)
            sections = row[5].split(";")
            require(len(sections) == 10 and all(len(s.split(",")) <= 1 if s else True
                                                for s in sections), "C sections")
        elif row[0] == "A":
            scene, area = int(row[1]), int(row[2])
            require(1 <= area <= 8 and scene not in areas, "A shape")
            areas[scene] = area
        elif row[0] == "S":
            require(len(row) == 3, "S shape")
            scene = int(row[1])
            events = [int(value) for value in row[2].split(",")]
            require(scene > 0 and events and len(set(events)) == len(events)
                    and scene not in success, "S row")
            success[scene] = events
        else:
            require(row[0] == "T", "row type")
    require((6, "10-6") not in keys, "selector11 flattened")
    require(len(success) == 64 and sum(len(v) for v in success.values()) == 64,
            "success row/scene count")
    require(len({event for values in success.values() for event in values}) == 62,
            "success target count")
    require(success.get(1114) == [20058] and success.get(22012) == [10006]
            and success.get(320) == [1132], "success examples")
    for line in lines[1:]:
        row = line.split("\t")
        if row[0] == "C":
            for section in row[5].split(";"):
                for scene in ([] if not section else [int(v) for v in section.split(",")]):
                    require(areas.get(scene) == int(row[1]), "C/A closure %d" % scene)
    print("PASS mainline32 production promotion: C=%d A=%d T=%d S=%d economyM=%d economyG=%d "
          "selector11=preserved entry=closed" % (c, a, t, len(success),
                                                 econ["total_m_scenes"],
                                                 econ["total_g_scenes"]))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.write:
        write_all()
    elif args.check:
        check()
    else:
        parser.error("choose --write or --check")


if __name__ == "__main__":
    main()
