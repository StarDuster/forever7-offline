"""Finite original CityMember/CityData v66 area-reply consumer.

Runs the real original 640 source bodies for:
  CityMember.get_all_area_info_reply
  CityData.set_area_info
  CityData.set_city_data

plus the original CityData helpers those bodies reach (__init__, get_area_info,
get_area_state, first_update_city_sfx_visible, proc_change_event,
getPersistentDict) and the original CityStatus class. The input is the exact
get_all_area_info_reply frame parameters captured from the v66 pending
delivery through the real reliable pullEvents path, not a hand-built dict.

Single-packet mode keeps the existing contract:
    area_reply_consumer.py cases.json reply.bson out.json

Sequential mode applies the actual before reply and then the actual after
reply to the same CityData instance (no re-init between them) and replays the
after reply as a duplicate:
    area_reply_consumer.py cases.json before.bson after.bson out.json

Allowed stubs: BuildingFactory.createBuilding (records build infos), and the
UI/settlement/city-entrance notify leaves (record call order). No NeoX,
renderer, JNI, emulator, native client or production edit.
"""
from pathlib import Path
import base64
import copy
import hashlib
import json
import sys
import textwrap
import types

from bson import BSON

ROOT = Path(__file__).resolve().parents[5]
NS = types.SimpleNamespace
pins = {}

CITY_MEMBER = "analysis/original-py-640/entity/avatar_members/CityMember.py"
CITY_DATA = "analysis/original-py-640/entity/avatar_attrs/CityData.py"


def extract(relative, name, env, indent=4, kind="def", normalizations=(), class_name=None):
    path = ROOT / relative
    pins[relative] = hashlib.sha256(path.read_bytes()).hexdigest()
    lines = path.read_text().splitlines(True)
    prefix = " " * indent
    base = 0
    if class_name:
        base = next(i for i, line in enumerate(lines) if line.startswith("class %s(" % class_name))
    start = next(i for i in range(base, len(lines)) if lines[i].startswith(prefix + kind + " " + name + "("))
    end = next((i for i in range(start + 1, len(lines))
                if lines[i].strip() and not lines[i].startswith(prefix + " ") and not lines[i].startswith("\n")), len(lines))
    source = "".join(line for line in lines[start:end] if not line.lstrip().startswith("print "))
    for old, new in normalizations:
        source = source.replace(old, new)
    exec(compile(textwrap.dedent(source), str(path), "exec"), env)
    return env[name]


order = []
calls = []
created = []


def notify_area(area):
    order.append(("notify_update_area", area))


def notify_stage():
    order.append("notify_update_stage")


def notify_info():
    order.append("notify_update_info")


def entrance_prop():
    order.append("city_entrance.update_prop")


def area_open(areas):
    order.append(("notify_area_open", tuple(areas)))


def area_fight(areas):
    order.append(("notify_area_fight", tuple(areas)))


def area_cr(areas):
    order.append(("notify_area_cr", tuple(areas)))


class BuildingFactory(object):
    @staticmethod
    def createBuilding(avatar, logger, info, *args, **kwargs):
        created.append(dict(info))
        return NS(id=info.get("id"), uuid=info.get("uuid"))


panel_city = NS(notify_update_area=notify_area, notify_update_stage=notify_stage,
                notify_update_info=notify_info)
panels = NS(city=panel_city, city_entrance=NS(update_prop=entrance_prop),
            settlement_fullscreen=NS(notify_area_open=area_open,
                                     notify_area_fight=area_fight,
                                     notify_area_cr=area_cr))
gg = NS(ui=NS(panels=panels))
const = NS(CityStatus=NS(FREE=0, FIGHT=1, FALL=2, CR_FIGHT=3, CR_FALL=4, STRIKE=5, ZHUISHA=6))
CITY_BUILDING_DATA = NS(data={})

env = {
    "gg": gg,
    "const": const,
    "BuildingFactory": BuildingFactory,
    "CITY_BUILDING_DATA": CITY_BUILDING_DATA,
}

CityStatus = extract(CITY_DATA, "CityStatus", env, indent=0, kind="class")
env["CityStatus"] = CityStatus

CityData = type("CityData", (object,), {})
for name, kwargs in (
        ("__init__", {"class_name": "CityData"}),
        ("set_area_info", {"class_name": "CityData", "normalizations": ((".iteritems()", ".items()"),)}),
        ("get_area_info", {"class_name": "CityData"}),
        ("get_area_state", {"class_name": "CityData"}),
        ("first_update_city_sfx_visible", {"class_name": "CityData"}),
        ("proc_change_event", {"class_name": "CityData"}),
        ("getPersistentDict", {"class_name": "CityData"}),
        ("set_city_data", {"class_name": "CityData"}),
):
    setattr(CityData, name, extract(CITY_DATA, name, env, **kwargs))

handler = extract(CITY_MEMBER, "get_all_area_info_reply", env, class_name="Member")


owner = NS(logger=NS())
city = object.__new__(CityData)
CityData.__init__(city, owner)
# The decompiled __init__ stores the typo "patro_num"; the real login path
# (initFromDict) supplies patrol_num from 'pn' with default 1 before replies.
city.patrol_num = 1
for name in ("get_area_info", "get_area_state", "first_update_city_sfx_visible",
             "proc_change_event", "getPersistentDict", "set_area_info", "set_city_data"):
    setattr(city, name, types.MethodType(getattr(CityData, name), city))
city.subscriber.add(lambda persistent: order.append("change_event"))

original_set_area_info = city.set_area_info
original_set_city_data = city.set_city_data


def tracked_set_area_info(areas_info, settlement=True):
    calls.append(("set_area_info", settlement))
    return original_set_area_info(areas_info, settlement)


def tracked_set_city_data(city_data):
    calls.append("set_city_data")
    return original_set_city_data(city_data)


city.set_area_info = tracked_set_area_info
city.set_city_data = tracked_set_city_data

member = NS(cityData=city)
member.get_all_area_info_reply = types.MethodType(handler, member)


def run_packet(areas, values, settlement):
    start = len(order)
    member.get_all_area_info_reply(areas, values, settlement)
    return order[start:]


def expect_order(areas, open_area, fight_area, cr_area, settlement):
    expected = [("notify_update_area", area["id"]) for area in areas.values()]
    expected += ["notify_update_stage", "city_entrance.update_prop"]
    if settlement and open_area:
        expected.append(("notify_area_open", tuple(open_area)))
    if settlement and fight_area:
        expected.append(("notify_area_fight", tuple(fight_area)))
    if cr_area:
        expected.append(("notify_area_cr", tuple(cr_area)))
    expected += ["change_event", "change_event", "notify_update_info"]
    return expected


value_map = (("dv", "develop_val"), ("dvc", "develop_cur"), ("av", "action_val"),
             ("pv", "power_val"), ("lpc", "last_power_add_time"), ("bf", "build_fund"),
             ("fv", "force_val"), ("ev", "exp_val"), ("rv", "research_val"),
             ("pn", "patrol_num"), ("acr", "actionConsumeReward"),
             ("uc", "useCanteen"), ("rbn", "removeBuildNum"))
initial = {"develop_val": 0, "develop_cur": 0, "action_val": 0, "power_val": 0,
           "last_power_add_time": None, "build_fund": 0, "force_val": 0,
           "exp_val": 0, "research_val": 0, "patrol_num": 1,
           "actionConsumeReward": [], "useCanteen": False, "removeBuildNum": 0}


def plain(value):
    if isinstance(value, dict):
        return {str(key): plain(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [plain(item) for item in value]
    return value


def read_payload(path):
    raw = Path(path).read_bytes()
    return raw, BSON(raw).decode()


def validate_document(document):
    assert list(document.keys()) == ["ais", "cd", "sm"], list(document.keys())
    ais, cd, sm = document["ais"], document["cd"], document["sm"]
    assert isinstance(ais, dict) and ais, "ais document"
    assert isinstance(cd, dict), "cd document"
    assert isinstance(sm, bool), "sm bool"
    for key, info in ais.items():
        assert key == "area_%d" % info["id"], (key, info.get("id"))
        assert isinstance(info["st"], list) and len(info["st"]) == 3, (key, info["st"])
        assert isinstance(info["st"][0], int) and info["st"][0] in set(const.CityStatus.__dict__.values()), (key, info["st"])
        assert isinstance(info["st"][1], bool), (key, info["st"])
        assert isinstance(info["st"][2], bool), (key, info["st"])
        assert isinstance(info.get("bd", {}), dict), (key, info.get("bd"))
        assert isinstance(info.get("dbd", {}), dict), (key, info.get("dbd"))
    return ais, cd, sm


def status_transitions(areas):
    """Original set_area_info deltas relative to the current CityData state."""
    open_area = []
    fight_area = []
    cr_area = []
    for area_name, area_info in areas.items():
        now_info = city.areas_info.get(area_name, {"st": [const.CityStatus.FALL, False]})
        if not now_info["st"][1] and area_info["st"][1]:
            cr_area.append(area_info["id"])
        if now_info["st"][0] == const.CityStatus.FIGHT and area_info["st"][0] == const.CityStatus.FREE:
            open_area.append(area_info["id"])
        if now_info["st"][0] == const.CityStatus.FALL and area_info["st"][0] == const.CityStatus.FIGHT:
            fight_area.append(area_info["id"])
    return open_area, sorted(fight_area), cr_area


def city_values(city_data, previous=None):
    values = {}
    for key, attr in value_map:
        if key in city_data:
            values[attr] = city_data[key]
        elif previous is not None:
            values[attr] = previous[attr]
        else:
            values[attr] = initial[attr]
    return values


def run_pair(before_path, after_path, out_path):
    """Apply the actual before reply, then the actual after reply, to one CityData."""
    before_raw, before_doc = read_payload(before_path)
    after_raw, after_doc = read_payload(after_path)
    before_ais, before_cd, before_sm = validate_document(before_doc)
    after_ais, after_cd, after_sm = validate_document(after_doc)

    before_buildings = sum(len(info.get("bd", {})) for info in before_ais.values())
    after_buildings = sum(len(info.get("bd", {})) for info in after_ais.values())

    # First actual packet: fresh original CityData (empty areas_info -> FALL).
    before_open, before_fight, before_cr = status_transitions(before_ais)
    assert before_open == [], "fresh CityData starts FALL; FIGHT->FREE cannot occur"
    first = run_packet(before_ais, before_cd, before_sm)
    first_calls = list(calls)
    assert first_calls == [("set_area_info", before_sm), "set_city_data"], first_calls
    assert first == expect_order(before_ais, before_open, before_fight, before_cr, before_sm), first
    assert city.open_area == before_open, city.open_area
    assert len(created) == before_buildings, (len(created), before_buildings)

    for key, info in before_ais.items():
        area_id = info["id"]
        assert city.areas_info[key] is info, key
        assert len(city.area_building_obj[area_id]) == len(info.get("bd", {})), key
        assert city.destroy_building[area_id] == [(int(field), build) for field, build in info.get("dbd", {}).items()], key
        assert city.area_sfx_visible[area_id] == {(info["st"][0], info["st"][1]): True}, key
    first_values = city_values(before_cd)
    for key, attr in value_map:
        assert getattr(city, attr) == first_values[attr], (key, attr, getattr(city, attr), first_values[attr])
    first_sfx = {area_id: dict(states) for area_id, states in city.area_sfx_visible.items()}

    # 1004-only bridge expectation: area1 alone moves FIGHT(1) -> FREE(0).
    assert "area_1" in before_ais and "area_1" in after_ais, (list(before_ais), list(after_ais))
    before_status = before_ais["area_1"]["st"]
    after_status = after_ais["area_1"]["st"]
    assert before_status[0] == const.CityStatus.FIGHT, before_status
    assert after_status[0] == const.CityStatus.FREE, after_status
    assert after_status[1] == before_status[1] and after_status[2] == before_status[2], (before_status, after_status)
    changed = sorted(info["id"] for key, info in after_ais.items()
                     if key in before_ais and before_ais[key]["st"] != info["st"])
    assert changed == [1], changed

    # Second actual packet on the same CityData instance (no re-init/reset).
    after_open, after_fight, after_cr = status_transitions(after_ais)
    second = run_packet(after_ais, after_cd, after_sm)
    assert calls == [("set_area_info", before_sm), "set_city_data",
                     ("set_area_info", after_sm), "set_city_data"], calls
    assert second == expect_order(after_ais, after_open, after_fight, after_cr, after_sm), second
    assert after_open == [1], after_open
    assert city.open_area == [1], city.open_area
    assert len(created) == before_buildings + after_buildings, (len(created), before_buildings + after_buildings)
    second_open_area = list(city.open_area)
    second_calls = list(calls)
    second_sfx = {area_id: dict(states) for area_id, states in city.area_sfx_visible.items()}

    settlement_names = ("notify_area_open", "notify_area_fight", "notify_area_cr")
    first_settlement = [entry for entry in first if isinstance(entry, tuple) and entry[0] in settlement_names]
    second_settlement = [entry for entry in second if isinstance(entry, tuple) and entry[0] in settlement_names]
    second_open_events = [entry for entry in second_settlement if entry[0] == "notify_area_open"]
    # Actual original body: open_area is always assigned; the popup is gated by
    # settlement (sm) and a non-empty open_area. sm=false => no popup, no mandate.
    if after_sm:
        assert second_open_events == [("notify_area_open", (1,))], second_open_events
    else:
        assert second_open_events == [], second_open_events
    assert not any(entry[0] == "notify_area_open" for entry in first_settlement), first_settlement

    for key, info in after_ais.items():
        area_id = info["id"]
        assert city.areas_info[key] is info, key
        assert len(city.area_building_obj[area_id]) == len(info.get("bd", {})), key
        assert city.destroy_building[area_id] == [(int(field), build) for field, build in info.get("dbd", {}).items()], key
        expected_sfx = first_sfx.get(area_id) or {(info["st"][0], info["st"][1]): True}
        assert city.area_sfx_visible[area_id] == expected_sfx, (key, city.area_sfx_visible[area_id], expected_sfx)
    second_values = city_values(after_cd, first_values)
    for key, attr in value_map:
        assert getattr(city, attr) == second_values[attr], (key, attr, getattr(city, attr), second_values[attr])
    for key, info in before_ais.items():
        if key not in after_ais:
            assert city.areas_info[key] is info, key

    # Duplicate after packet: same original body, no second settlement/open.
    created_before_duplicate = len(created)
    settlement_before_duplicate = len(first_settlement) + len(second_settlement)
    duplicate = run_packet(copy.deepcopy(after_ais), copy.deepcopy(after_cd), after_sm)
    duplicate_settlement = [entry for entry in duplicate if isinstance(entry, tuple) and entry[0] in settlement_names]
    assert duplicate_settlement == [], duplicate_settlement
    assert city.open_area == [], city.open_area
    assert not any(entry[0] == "notify_area_open" for entry in duplicate_settlement), duplicate_settlement
    assert duplicate == ([("notify_update_area", info["id"]) for info in after_ais.values()] +
                         ["notify_update_stage", "city_entrance.update_prop",
                          "change_event", "change_event", "notify_update_info"]), duplicate
    assert len(created) - created_before_duplicate == after_buildings, "original body rebuilds buildings on replay"
    assert all(city.areas_info[key] == info for key, info in after_ais.items())

    result = {
        "status": "PASS",
        "mode": "pair",
        "source_sha256": pins,
        "executed_bodies": [
            "CityMember.get_all_area_info_reply",
            "CityData.set_area_info",
            "CityData.set_city_data",
            "CityData.__init__",
            "CityData.get_area_info",
            "CityData.get_area_state",
            "CityData.first_update_city_sfx_visible",
            "CityData.proc_change_event",
            "CityData.getPersistentDict",
            "CityStatus.initFromDict",
        ],
        "source_normalizations": [
            "Python 2 print statements removed only for source executability",
            ".iteritems() -> .items() in set_area_info only",
        ],
        "rpc": {"method": "get_all_area_info_reply", "params_order": ["ais", "cd", "sm"]},
        "before": {
            "payload_sha256": hashlib.sha256(before_raw).hexdigest(),
            "payload_bytes": len(before_raw),
            "payload_base64": base64.b64encode(before_raw).decode("ascii"),
            "decoded_payload": before_doc,
            "sm": before_sm,
            "handler_order": ["set_area_info(ais, sm)", "set_city_data(cd)"],
            "calls": [plain(entry) for entry in first_calls],
            "order": [plain(entry) for entry in first],
            "settlement": [plain(entry) for entry in first_settlement],
            "open_area": before_open,
            "fight_area": before_fight,
            "cr_area": before_cr,
            "buildings_created": before_buildings,
            "city_values": first_values,
            "area_sfx_visible": {str(key): sorted(list(state)) for key, state in first_sfx.items()},
        },
        "after": {
            "payload_sha256": hashlib.sha256(after_raw).hexdigest(),
            "payload_bytes": len(after_raw),
            "payload_base64": base64.b64encode(after_raw).decode("ascii"),
            "decoded_payload": after_doc,
            "sm": after_sm,
            "handler_order": ["set_area_info(ais, sm)", "set_city_data(cd)"],
            "calls": [plain(entry) for entry in second_calls[len(first_calls):]],
            "calls_cumulative": [plain(entry) for entry in second_calls],
            "order": [plain(entry) for entry in second],
            "settlement": [plain(entry) for entry in second_settlement],
            "open_area": second_open_area,
            "expected_open_area": after_open,
            "fight_area": after_fight,
            "cr_area": after_cr,
            "buildings_created": after_buildings,
            "city_values": second_values,
            "area_sfx_visible": {str(key): sorted(list(state)) for key, state in second_sfx.items()},
        },
        "transition": {
            "changed_area_ids": changed,
            "area_1": {"before": before_status, "after": after_status},
            "open_area": after_open,
            "open_area_updated": second_open_area == [1],
            "notify_area_open_fired": bool(second_open_events),
            "sm": after_sm,
            "rule": "open_area is assigned on every set_area_info; notify_area_open only when settlement(sm) is true and open_area is non-empty",
        },
        "duplicate_after": {
            "order": [plain(entry) for entry in duplicate],
            "settlement_before": settlement_before_duplicate,
            "settlement_after": settlement_before_duplicate + len(duplicate_settlement),
            "settlement_repeated": bool(duplicate_settlement),
            "open_area_after_replay": city.open_area,
            "buildings_rebuilt": len(created) - created_before_duplicate,
        },
        "limits": [
            "selected original source bodies only; no NeoX opcode/renderer/JNI/emulator",
            "BuildingFactory.createBuilding and city/settlement/entrance notify leaves are recording stubs",
            "no native, APK, D8 or UI acceptance claim",
            "CityData starts from the original __init__ (empty areas_info); a real login may preload initFromDict",
            "area_sfx_visible is initialized once per area by the original body; a later FIGHT->FREE on the same instance does not rewrite it",
            "strike_area and new_building are collected by the original body but unused; not observable",
        ],
    }
    Path(out_path).write_text(json.dumps(result, indent=2) + "\n")
    print("PASS original area consumer pair: before(sm=%s) -> after(sm=%s)" % (before_sm, after_sm))
    print("after open_area=%s popup=%s duplicate_settlement=%s" %
          (second_open_area, second_open_events, duplicate_settlement))
    return result


if len(sys.argv) == 5:
    run_pair(sys.argv[2], sys.argv[3], sys.argv[4])
    sys.exit(0)

payload = Path(sys.argv[2]).read_bytes()
document = BSON(payload).decode()
ais = document["ais"]
cd = document["cd"]
sm = document["sm"]

# Payload shape from the actual v66 frame.
assert list(document.keys()) == ["ais", "cd", "sm"], list(document.keys())
assert isinstance(ais, dict) and ais, "ais document"
assert isinstance(cd, dict), "cd document"
assert isinstance(sm, bool), "sm bool"
for key, info in ais.items():
    assert key == "area_%d" % info["id"], (key, info.get("id"))
    assert isinstance(info["st"], list) and len(info["st"]) == 3, (key, info["st"])
    assert isinstance(info["st"][0], int) and info["st"][0] in set(const.CityStatus.__dict__.values()), (key, info["st"])
    assert isinstance(info["st"][1], bool), (key, info["st"])
    assert isinstance(info["st"][2], bool), (key, info["st"])
    assert isinstance(info.get("bd", {}), dict), (key, info.get("bd"))
    assert isinstance(info.get("dbd", {}), dict), (key, info.get("dbd"))

expected_open = []  # fresh CityData default is FALL; FALL->FREE is not liberation
expected_fight = sorted(info["id"] for info in ais.values() if info["st"][0] == const.CityStatus.FIGHT)
expected_cr = [info["id"] for info in ais.values() if info["st"][1]]
expected_strike = [info["id"] for info in ais.values() if info["st"][0] == const.CityStatus.STRIKE]
building_total = sum(len(info.get("bd", {})) for info in ais.values())

first = run_packet(ais, cd, sm)
first_calls = list(calls)
assert first_calls == [("set_area_info", sm), "set_city_data"], first_calls
assert first == expect_order(ais, expected_open, expected_fight, expected_cr, sm), first
assert len(created) == building_total, (len(created), building_total)

for key, info in ais.items():
    area_id = info["id"]
    assert city.areas_info[key] is info, key
    assert len(city.area_building_obj[area_id]) == len(info.get("bd", {})), key
    assert city.destroy_building[area_id] == [(int(field), build) for field, build in info.get("dbd", {}).items()], key
    assert city.area_sfx_visible[area_id] == {(info["st"][0], info["st"][1]): True}, key
assert city.open_area == expected_open
assert city.patrol_num == cd.get("pn", 1)

first_values = {}
for key, attr in value_map:
    expected = cd[key] if key in cd else initial[attr]
    assert getattr(city, attr) == expected, (key, attr, getattr(city, attr), expected)
    first_values[attr] = getattr(city, attr)

# Same packet replayed byte-for-byte (decoded copy, unchanged bytes).
settlement_names = ("notify_area_open", "notify_area_fight", "notify_area_cr")
first_settlement = [entry for entry in first if isinstance(entry, tuple) and entry[0] in settlement_names]
created_before = len(created)
second = run_packet(copy.deepcopy(ais), copy.deepcopy(cd), sm)
assert calls == [("set_area_info", sm), "set_city_data"] * 2, calls
second_settlement = [entry for entry in second if isinstance(entry, tuple) and entry[0] in settlement_names]
assert second_settlement == [], second_settlement
assert second == ([("notify_update_area", info["id"]) for info in ais.values()] +
                  ["notify_update_stage", "city_entrance.update_prop",
                   "change_event", "change_event", "notify_update_info"]), second
assert len(created) - created_before == building_total, "original body rebuilds building objects on replay"
assert all(city.areas_info[key] == info for key, info in ais.items())

result = {
    "status": "PASS",
    "source_sha256": pins,
    "executed_bodies": [
        "CityMember.get_all_area_info_reply",
        "CityData.set_area_info",
        "CityData.set_city_data",
        "CityData.__init__",
        "CityData.get_area_info",
        "CityData.get_area_state",
        "CityData.first_update_city_sfx_visible",
        "CityData.proc_change_event",
        "CityData.getPersistentDict",
        "CityStatus.initFromDict",
    ],
    "source_normalizations": [
        "Python 2 print statements removed only for source executability",
        ".iteritems() -> .items() in set_area_info only",
    ],
    "payload_sha256": hashlib.sha256(payload).hexdigest(),
    "payload_bytes": len(payload),
    "payload_base64": base64.b64encode(payload).decode("ascii"),
    "decoded_payload": document,
    "capture_source": "real reliable pullEvents dispatch after the week handoff (dispatchReliableRpc -> pullEventsReply -> syncEventEffects)",
    "rpc": {
        "method": "get_all_area_info_reply",
        "params_order": list(document.keys()),
        "sm": sm,
    },
    "payload": {
        "area_keys": list(ais.keys()),
        "area_ids": [info["id"] for info in ais.values()],
        "statuses": {key: list(info["st"]) for key, info in ais.items()},
        "bd_count": sum(len(info.get("bd", {})) for info in ais.values()),
        "dbd_count": sum(len(info.get("dbd", {})) for info in ais.values()),
        "cd_keys": list(cd.keys()),
    },
    "first": {
        "handler_order": ["set_area_info(ais, sm)", "set_city_data(cd)"],
        "calls": [list(entry) if isinstance(entry, tuple) else entry for entry in first_calls],
        "order": [list(entry) if isinstance(entry, tuple) else entry for entry in first],
        "settlement": [list(entry) for entry in first_settlement],
        "expected_open_area": expected_open,
        "expected_fight_area": expected_fight,
        "expected_cr_area": expected_cr,
        "expected_strike_area": expected_strike,
        "buildings_created": building_total,
        "city_values": first_values,
        "area_sfx_visible": {str(key): sorted(list(state)) for key, state in city.area_sfx_visible.items()},
        "destroy_building": {str(key): value for key, value in city.destroy_building.items()},
    },
    "duplicate": {
        "same_payload_sha256": hashlib.sha256(payload).hexdigest(),
        "order": [list(entry) if isinstance(entry, tuple) else entry for entry in second],
        "settlement_calls_before": len(first_settlement),
        "settlement_calls_after": len(first_settlement) + len(second_settlement),
        "settlement_repeated": bool(second_settlement),
        "buildings_rebuilt": len(created) - created_before,
        "stage_entrance_change_notifications": "notify_update_stage" in second
                                                and "city_entrance.update_prop" in second
                                                and "change_event" in second,
    },
    "limits": [
        "selected original source bodies only; no NeoX opcode/renderer/JNI/emulator",
        "BuildingFactory.createBuilding and city/settlement/entrance notify leaves are recording stubs",
        "no native, APK, D8 or UI acceptance claim",
        "strike_area and new_building are collected by the original body but unused; not observable",
        "CityData starts from the original __init__ (empty areas_info); a real login may preload initFromDict. "
        "For this all-FALL packet the settlement deltas are identical (none)",
    ],
}
Path(sys.argv[3]).write_text(json.dumps(result, indent=2) + "\n")
print("PASS original area consumer: get_all_area_info_reply -> set_area_info(ais,sm) -> set_city_data(cd)")
print("first settlement=%s duplicate_settlement=%s" % (first_settlement, second_settlement))
