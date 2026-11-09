"""Append-only entry-closure rows for the last mainline menus.

Source of truth is the original 640 literal chapter_mission_data / mission
tables. The delta is table-driven: it selects complete source chapter families
for the scoped menus (menu12 family 13, menu25 family 27) and appends only the
exact C/A/S rows that the live story-mission catalog does not already carry.

No per-scene hand-written rows, no entry readiness, no effect ownership and no
economy change (the COC 482..488 economy rows already come from the separate
story-city economy increment).

Writer: .venv/bin/python tools/project7_mainline_entry_closure.py --write
Verifier: .venv/bin/python tools/project7_mainline_entry_closure.py --check
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from collections import OrderedDict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from runtime.project7_dream_catalog.produce import literal  # noqa: E402

CDATA = ROOT / "analysis/android640-scripts/com/data/cdata"
OUT = ROOT / "runtime/project7_story_mission_catalog"
CATALOG = OUT / "catalog-v1.tsv"
CONTRACT = OUT / "entry-closure-v1.json"
BASE_CATALOG_SHA = "d81437791c78dfc309a6db2b96412d3c7ffe141e88b5492256b1fc77db8a8864"
SOURCE_PINS = {
    "chapter_mission_data": "c637bbf1665c8118b238c702145a22df0ceaf860bdf80595edbcf0d20882cdb4",
    "mission": "2019aab0289ffdac6aacde82b21cd283ef0c8d8afb6bb264d087e8cde262390f",
}
SCHEMA = "project7-mainline-entry-closure-v1"
FAMILIES = {"13": "menu12 chapter family", "27": "menu25 chapter family"}


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def require(ok, message):
    if not ok:
        raise SystemExit("FAIL entry closure: " + message)


def inherited(missions, scene, chain=()):
    require(scene not in chain, "mission inheritance cycle")
    row = missions[scene]
    parent = row.get("inherit_mission")
    base = inherited(missions, parent, chain + (scene,)) if parent else {}
    return dict(base, **row)


def source_rows():
    for name, digest in SOURCE_PINS.items():
        require(sha((CDATA / (name + ".marshal")).read_bytes()) == digest,
                "source pin " + name)
    chapters = literal(CDATA / "chapter_mission_data.marshal")
    missions = literal(CDATA / "mission.marshal")
    return chapters, missions


def parse_catalog(data: bytes):
    lines = data.decode("utf-8").splitlines()
    require(lines and lines[0].split("\t")[:2] == ["P7STORYMISSIONS", "1"], "catalog header")
    c_keys, c_lines, a_rows, s_rows = set(), {}, {}, {}
    for line in lines[1:]:
        row = line.split("\t")
        kind = row[0]
        if kind == "C":
            require(len(row) == 6 and row[2] == "0" and row[4] == "0", "catalog C shape")
            key = (int(row[1]), row[3])
            require(key not in c_keys, "catalog C duplicate")
            c_keys.add(key)
            c_lines[key] = line
        elif kind == "A":
            require(len(row) == 3, "catalog A shape")
            a_rows[int(row[1])] = int(row[2])
        elif kind == "S":
            require(len(row) == 3, "catalog S shape")
            s_rows[int(row[1])] = row[2]
        elif kind == "T":
            require(len(row) == 7, "catalog T shape")
    return lines, c_keys, c_lines, a_rows, s_rows


def delta(chapters, missions, c_keys, a_rows, s_rows):
    additions = []
    for key in sorted(chapters):
        area, special, route, status = key
        if special != 0 or status != 0:
            continue
        # Virtual city areas carry their own StoryCity chapters; the mission
        # catalog only indexes the original normal areas 1..8.
        if area < 1 or area > 8:
            continue
        family = route.split("-")[0]
        if family not in FAMILIES:
            continue
        if (area, route) in c_keys:
            continue
        row = chapters[key]
        require((row["chapter"], row["specialStage"], row["route"], row["status"]) == key,
                "source chapter key/body %s" % (key,))
        groups = [list(row["section"][i]) for i in range(10)]
        require(all(len(group) <= 1 for group in groups) and any(groups),
                "source chapter groups %s" % (key,))
        scenes = [scene for group in groups for scene in group]
        require(scenes, "source chapter empty %s" % (key,))
        closure = []
        for scene in scenes:
            require(scene in missions, "missing mission %d" % scene)
            mission = inherited(missions, scene)
            require(mission["ch"] == area, "mission/chapter area %d" % scene)
            if scene not in a_rows:
                closure.append(scene)
        additions.append((key, row, groups, scenes, closure))
    return additions


def build_lines(additions, a_rows, s_rows, missions):
    c_lines, a_lines, s_lines = [], [], []
    for key, row, groups, scenes, closure in additions:
        section = ";".join(",".join(map(str, group)) for group in groups)
        c_lines.append("\t".join(map(str, ("C", key[0], key[1], key[2], key[3], section))))
        for scene in closure:
            a_lines.append("A\t%d\t%d" % (scene, missions[scene]["ch"]))
            a_rows[scene] = missions[scene]["ch"]
        for scene in scenes:
            success = inherited(missions, scene).get("successEvent") or ()
            if scene in s_rows:
                require(",".join(map(str, success)) == s_rows[scene],
                        "success row changed %d" % scene)
                continue
            if success:
                value = ",".join(map(str, success))
                s_lines.append("S\t%d\t%s" % (scene, value))
                s_rows[scene] = value
    return c_lines, a_lines, s_lines


def compute(catalog_bytes):
    chapters, missions = source_rows()
    lines, c_keys, c_lines, a_rows, s_rows = parse_catalog(catalog_bytes)
    additions = delta(chapters, missions, c_keys, a_rows, s_rows)
    require(additions, "no entry-closure chapter rows selected")
    c_lines_new, a_lines_new, s_lines_new = build_lines(additions, a_rows, s_rows, missions)
    return OrderedDict((
        ("chapter_keys", [[key[0], key[2]] for key, *_ in additions]),
        ("chapter_rows", c_lines_new),
        ("area_rows", a_lines_new),
        ("success_rows", s_lines_new),
        ("scenes", sorted({scene for _, _, _, scenes, _ in additions for scene in scenes})),
    ))


def write():
    current = CATALOG.read_bytes()
    require(sha(current) == BASE_CATALOG_SHA, "catalog is not the v54 production base")
    result = compute(current)
    appended = current + ("\n".join(
        result["chapter_rows"] + result["area_rows"] + result["success_rows"]) + "\n").encode("utf-8")
    contract = OrderedDict((
        ("schema", SCHEMA),
        ("source_pins", SOURCE_PINS),
        ("families", FAMILIES),
        ("base_catalog_sha256", BASE_CATALOG_SHA),
        ("catalog_sha256", sha(appended)),
        ("chapter_count", len(result["chapter_keys"])),
        ("area_count", len(result["area_rows"])),
        ("success_count", len(result["success_rows"])),
        ("chapter_keys", result["chapter_keys"]),
        ("chapter_rows", result["chapter_rows"]),
        ("area_rows", result["area_rows"]),
        ("success_rows", result["success_rows"]),
        ("scenes", result["scenes"]),
        ("policy", "append-only source C/A/S rows for entry-proven chapter families; no economy, entry or effect change"),
    ))
    CATALOG.write_bytes(appended)
    CONTRACT.write_text(json.dumps(contract, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    pins = json.loads((OUT / "pins.json").read_text(encoding="utf-8"))
    pins["outputs"]["catalog-v1.tsv"] = contract["catalog_sha256"]
    _, _, c_lines, a_rows, _ = parse_catalog(appended)
    pins["chapters"] = len(c_lines)
    pins["missions"] = len(a_rows)
    pins["generic_chapters"] = len(c_lines) - int(pins.get("route27_chapters", 39))
    pins["entry_closure"] = {
        "contract": str(CONTRACT.relative_to(ROOT)),
        "contract_sha256": sha(CONTRACT.read_bytes()),
        "chapters": contract["chapter_count"],
        "scenes": contract["scenes"],
    }
    pins["policy"] = (pins.get("policy", "") +
                      "; entry-closure C/A/S delta from tools/project7_mainline_entry_closure.py")
    (OUT / "pins.json").write_text(json.dumps(pins, ensure_ascii=False, indent=2) + "\n",
                                   encoding="utf-8")
    print("PASS write chapters=%d areas=%d success=%d catalog=%s contract=%s"
          % (contract["chapter_count"], contract["area_count"],
             contract["success_count"], contract["catalog_sha256"],
             sha(CONTRACT.read_bytes())))


def check():
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    require(contract["schema"] == SCHEMA, "contract schema")
    require(sha(CATALOG.read_bytes()) == contract["catalog_sha256"], "catalog hash")
    base = CATALOG.read_bytes()
    for line in contract["chapter_rows"] + contract["area_rows"] + contract["success_rows"]:
        require(line.encode("utf-8") in base, "delta row missing")
    # Recompute from the declared base by stripping the appended rows.
    suffix = ("\n".join(contract["chapter_rows"] + contract["area_rows"] +
                        contract["success_rows"]) + "\n").encode("utf-8")
    require(base.endswith(suffix), "delta is not append-only")
    previous = base[:-len(suffix)]
    require(sha(previous) == contract["base_catalog_sha256"], "base hash")
    result = compute(previous)
    require(result["chapter_rows"] == contract["chapter_rows"], "chapter delta changed")
    require(result["area_rows"] == contract["area_rows"], "area delta changed")
    require(result["success_rows"] == contract["success_rows"], "success delta changed")
    print("PASS check chapters=%d catalog=%s" % (contract["chapter_count"],
                                                 contract["catalog_sha256"]))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.write:
        write()
        check()
    elif args.check:
        check()
    else:
        parser.error("choose --write or --check")


if __name__ == "__main__":
    main()
