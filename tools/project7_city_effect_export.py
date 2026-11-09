"""Export the complete original640 city-effect projection into event_graph @cityEffect.

The frozen component graph previously published only the manager-consumed subset.
This writer merges every owned original event_content field (area status/lock,
areaFall, areaCR7, hero, building) into the existing @cityEffect documents and
preserves non-city fields already published (for example friendly). It is
deterministic: existing documents stay in place, missing rows are appended in
event-id order, and fields use a fixed canonical order.

Writer/verifier: python3 tools/project7_city_effect_export.py --check
"""
from __future__ import annotations

import argparse
import base64
import hashlib
import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from runtime.project7_dream_catalog.produce import literal  # noqa: E402

CDATA = ROOT / "analysis/android640-scripts/com/data/cdata"
EVENT_CONTENT_PIN = "0ddb80bbe56259a2f54acdb7accef49ad390240b0cac504ba1375a3c8976afe7"
GRAPH = ROOT / "analysis/project7/story-city-integration-prepare-v49/project7-inputs-pm_gioka/stage/assets/event_graph.tsv"
CANON = (
    "areaFree", "areaFight", "areaLock", "areaUnlock", "areaFall", "areaCR7",
    "cineLockHeroes", "banHeroes", "recoverBanHeroes", "friendly",
)
OWNED = tuple(f for f in CANON if f != "friendly")


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def require(ok, message):
    if not ok:
        raise SystemExit("FAIL city effect export: " + message)


def decode(data, pos=0):
    size = struct.unpack("<i", data[pos:pos + 4])[0]
    end = pos + size
    index = pos + 4
    out = {}
    while index < end - 1:
        kind = data[index]
        index += 1
        stop = data.index(b"\x00", index)
        key = data[index:stop].decode("utf-8")
        index = stop + 1
        if kind == 0x10:
            out[key] = struct.unpack("<i", data[index:index + 4])[0]
            index += 4
        elif kind == 0x12:
            out[key] = struct.unpack("<q", data[index:index + 8])[0]
            index += 8
        elif kind == 0x02:
            length = struct.unpack("<i", data[index:index + 4])[0]
            out[key] = data[index + 4:index + 3 + length].decode("utf-8")
            index += 4 + length
        elif kind in (0x03, 0x04):
            nested, index = decode(data, index)
            out[key] = nested
        else:
            raise SystemExit("FAIL city effect export: BSON type %d" % kind)
    return out, end


def element(key: str, value) -> bytes:
    raw = key.encode("utf-8") + b"\x00"
    if isinstance(value, bool):
        return b"\x08" + raw + (b"\x01" if value else b"\x00")
    if isinstance(value, int):
        return b"\x10" + raw + struct.pack("<i", value)
    if isinstance(value, dict):
        return b"\x03" + raw + document(value, sort_keys=False)
    if isinstance(value, (list, tuple)):
        return b"\x04" + raw + document({str(i): v for i, v in enumerate(value)})
    raise SystemExit("FAIL city effect export: value type")


def document(values, sort_keys=True) -> bytes:
    keys = list(values)
    if sort_keys:
        keys.sort()
    body = b"".join(element(key, values[key]) for key in keys)
    return struct.pack("<i", len(body) + 5) + body + b"\x00"


def ordered(values):
    rank = {name: index for index, name in enumerate(CANON)}
    keys = sorted(values, key=lambda name: (rank.get(name, len(CANON)), name))
    return {key: values[key] for key in keys}


# buildBuilding is an existing dedicated registry payload; never coerce it to ids.
# StoryCityPolicy treats it as external/unknown, so it is preserved byte-for-byte.
PRESERVED_FIELDS = ("buildBuilding",)


def load_effects():
    path = CDATA / "event_content.marshal"
    require(sha(path.read_bytes()) == EVENT_CONTENT_PIN, "event_content pin")
    table = literal(path)
    effects = {}
    for event, row in table.items():
        values = {}
        for field in OWNED:
            ids = row.get(field)
            if not ids:
                continue
            require(all(isinstance(v, int) for v in ids), "integer %s" % field)
            require(len(set(ids)) == len(ids), "duplicate %s" % field)
            values[field] = tuple(ids)
        if values:
            effects[event] = values
    return effects


def load_buildings():
    table = literal(CDATA / "event_content.marshal")
    out = {}
    for event, row in table.items():
        value = row.get("buildBuilding")
        if isinstance(value, dict):
            def norm(val):
                if isinstance(val, dict):
                    return {str(i): int(v) for i, v in val.items()}
                if isinstance(val, (tuple, list)):
                    return {str(i): int(v) for i, v in enumerate(val)}
                return val
            out[event] = {str(k): norm(val) for k, val in value.items()}
    return out


def export(graph_bytes: bytes, effects, buildings=None) -> bytes:
    lines = graph_bytes.decode("ascii").splitlines()
    seen = set()
    out = []
    for line in lines:
        cols = line.split("\t")
        if cols[0] == "@cityEffect" and len(cols) >= 3:
            event = int(cols[1])
            require(event not in seen, "duplicate cityEffect %d" % event)
            seen.add(event)
            merged, _ = decode(base64.b64decode(cols[2]))
            for field, ids in effects.get(event, {}).items():
                merged[field] = list(ids)
            if buildings and event in buildings:
                merged["buildBuilding"] = buildings[event]
            out.append("@cityEffect\t%d\t%s" % (event, base64.b64encode(document(ordered(merged))).decode("ascii")))
        else:
            out.append(line)
    for event in sorted(effects):
        if event in seen:
            continue
        out.append("@cityEffect\t%d\t%s" % (event, base64.b64encode(document(ordered(effects[event]))).decode("ascii")))
    return ("\n".join(out) + "\n").encode("ascii")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--graph", type=Path, default=GRAPH)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    effects = load_effects()
    data = export(args.graph.read_bytes(), effects, load_buildings())
    if args.output:
        args.output.write_bytes(data)
    print("PASS cityEffects=%d sha256=%s" % (
        sum(1 for line in data.splitlines() if line.startswith(b"@cityEffect")), sha(data)))


if __name__ == "__main__":
    main()
