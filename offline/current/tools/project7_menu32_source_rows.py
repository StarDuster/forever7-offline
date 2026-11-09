"""Derive menu32 route35 C/A/M candidate rows from original640 literals only.

Not wired into prepare. S rows are absent because the original source has no
successEvent/completeConds success mapping for these scenes.
"""
import _bootstrap  # noqa: E402,F401
import hashlib, json, sys
from pathlib import Path
from _bootstrap import ROOT
if str(ROOT) not in sys.path: sys.path.insert(0, str(ROOT))
from project7_dream_catalog.produce import literal
CDATA = ROOT / "analysis/android640-scripts/com/data/cdata"
OUT = ROOT / "offline/current/data/project7_mainline32_data_candidate/menu32-candidate-rows.tsv"
PINS = {
 "chapter_mission_data": "c637bbf1665c8118b238c702145a22df0ceaf860bdf80595edbcf0d20882cdb4",
 "mission": "2019aab0289ffdac6aacde82b21cd283ef0c8d8afb6bb264d087e8cde262390f",
}
def sha(b): return hashlib.sha256(b).hexdigest()
def require(ok, msg):
    if not ok: raise SystemExit("FAIL menu32 rows: " + msg)
def inherited(missions, scene, chain=()):
    require(scene not in chain and scene in missions, "inheritance %s" % scene)
    row = missions[scene]; parent = row.get("inherit_mission")
    base = inherited(missions, parent, chain + (scene,)) if parent else {}
    merged = dict(base); merged.update(row); return merged
def build():
    tables = {}
    for name, pin in PINS.items():
        path = CDATA / (name + ".marshal")
        require(sha(path.read_bytes()) == pin, "source pin " + name)
        tables[name] = literal(path)
    chapters, missions = tables["chapter_mission_data"], tables["mission"]
    rows, scenes = [], set()
    for key, row in sorted(chapters.items()):
        if str(key[2]).split("-")[0] != "35" or key[1] != 0 or key[3] != 0: continue
        groups = row["section"]; require(set(groups) == set(range(10)), "sections %s" % (key,))
        values = [s for i in range(10) for s in groups[i]]
        require(values and all(len(groups[i]) <= 1 for i in range(10)), "singleton %s" % (key,))
        require(all(missions[s].get("system_type") == 1 and missions[s].get("release") == 1 for s in values), "normal release")
        rows.append("C\t%d\t%d\t%s\t%d\t%s" % (key[0], key[1], key[2], key[3], ";".join(",".join(map(str, groups[i])) for i in range(10))))
        for s in values:
            if s in scenes: continue
            scenes.add(s); r = inherited(missions, s)
            require(r.get("ch") == key[0], "area %s" % s)
            fields = [r.get(n, d) for n, d in [("va",0),("fatigue",0),("overFatigue",0),("force_recommend",0),("least_hero_num",1),("max_hero_num",3),("prize",1)]]
            require(all(type(v) is int and v >= 0 for v in fields), "economy %s" % s)
            rows.append("A\t%d\t%d" % (s, r["ch"]))
            rows.append("M\t%d\t%s" % (s, "\t".join(map(str, fields))))
            cond_event = r.get("cond_event", 0) or 0
            cond = list(r.get("cond") or ())
            if cond_event or cond:
                rows.append("\t".join(map(str, ("G", s, cond_event, *cond))))
    require(sum(1 for x in rows if x.startswith("C\t")) == 28, "C count")
    require(sum(1 for x in rows if x.startswith("A\t")) == 21, "A count")
    require(sum(1 for x in rows if x.startswith("M\t")) == 21, "M count")
    require(sum(1 for x in rows if x.startswith("G\t")) == 17, "G count")
    body = ("# original640 route35 menu32 candidate rows; C/A/M/G; S absent by source\n" + "\n".join(rows) + "\n").encode()
    return body
if __name__ == "__main__":
    body = build()
    OUT.write_bytes(body)
    print("PASS menu32 candidate rows sha256=%s rows=%d output=%s" % (sha(body), body.count(b"\n") - 2, OUT.relative_to(ROOT)))
