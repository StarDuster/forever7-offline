"""Finite original 640 client day consumer: statusCheckAsk/Reply, incDayWhenNoActionVal,
updateDay and showDailySettlement bodies. No NeoX opcodes, renderer or emulator.
Requests must match the bytes the real v63 host sent; replies must drive the original handlers.
"""
from pathlib import Path
import base64, hashlib, json, sys, textwrap, types
from bson import BSON

ROOT = Path(__file__).resolve().parents[5]
NS = types.SimpleNamespace
pins = {}


def original(relative, name, env, indent=4, kind="def"):
    path = ROOT / relative
    pins[relative] = hashlib.sha256(path.read_bytes()).hexdigest()
    lines = path.read_text().splitlines(True)
    prefix = " " * indent
    start = next(i for i, line in enumerate(lines) if line.startswith(prefix + kind + " " + name + "("))
    end = next((i for i in range(start + 1, len(lines))
                if lines[i].strip() and not lines[i].startswith(prefix + " ") and not lines[i].startswith("\n")), len(lines))
    source = textwrap.dedent("".join(line for line in lines[start:end] if not line.lstrip().startswith("print ")))
    exec(compile(source, str(path), "exec"), env)
    return env[name]


locks = set()
events = []
sent = []
panels = NS(city=NS(notify_update_days=lambda **kw: events.append(("city_update", kw))),
             bbs_home=NS(notify_inc_day=lambda: events.append("bbs_inc_day")),
             city_3year=None)
ui = NS(lock=lambda key: locks.add(key), unlock=lambda key: locks.discard(key), panels=panels)
gg = NS(ui=ui, city=NS(update_weekday=lambda: events.append("update_weekday")))
env = {"gg": gg}
attrs = {}
for name in ("statusCheckAsk", "statusCheckReply", "_doStatusHandle"):
    attrs[name] = original("analysis/original-py-640/entity/avatar_members/StatusMember.py", name, env)
for name in ("incDayWhenNoActionVal", "canIncDay", "updateDay", "showDailySettlement"):
    attrs[name] = original("analysis/original-py-640/entity/avatar_members/WeekNumMember.py", name, env)

Avatar = type("FiniteOriginalDayAvatar", (), attrs)
avatar = Avatar()
avatar.logger = NS(error=lambda *a: None)
avatar.statusData = NS(statusCbInfo=None, cur="city")
avatar.weeknumData = NS(daynum=0, sandglass_not_today=True, curDailyData={}, lastDailyData={})
avatar.cityData = NS(action_val=0)
avatar.checkEvents = lambda: events.append("check_events")
avatar.tryCheckEventsMayLocked = lambda: events.append("try_check_events")


def rpc(kind):
    def capture(name, params):
        sent.append((kind, name, params, list(params.keys()), BSON.encode(params)))
    return capture


avatar.callServerMethodReliable = rpc("reliable")
avatar.callServerMethod = rpc("plain")


def decode(row):
    return BSON(base64.b64decode(row["parameters_b64"])).decode()


def apply_frames(frames):
    applied = []
    for row in frames:
        method, params = row["method"], decode(row)
        applied.append(method)
        if method == "statusCheckReply":
            avatar.statusCheckReply(params["r"], params["s"])
        elif method == "updateDay":
            avatar.updateDay(params["d"])
        elif method == "showDailySettlement":
            avatar.showDailySettlement(params["c"], params["l"])
    return applied


def request_match(row, actual):
    kind, name, params, order, encoded = actual
    assert name == row["method"], (name, row)
    assert encoded == base64.b64decode(row["parameters_b64"]), (encoded, row)
    return params, order


cases = json.loads(Path(sys.argv[1]).read_text())
checks = []

# 1. Original statusCheck request bytes and reply handler.
cb = []
avatar.statusCheckAsk("nextday", lambda: cb.append("success"))
assert "statusCheck" in locks, "original statusCheckAsk locks statusCheck"
params, order = request_match(cases["status_check"]["request"], sent[-1])
assert params == {"s": "nextday"} and order == ["s"], "original statusCheck field is s=nextday"
assert apply_frames(cases["status_check"]["frames"]) == ["reliableRpcAck", "statusCheckReply", "serverCallbackCarrier"]
assert "statusCheck" not in locks and cb == ["success"], "original statusCheckReply unlocks and calls successCb"
assert avatar.statusData.cur == "city", "original check reply does not change statusData.cur"
assert avatar.weeknumData.daynum == 0
checks.append("original statusCheckAsk sends exact host bytes {s:nextday}; original statusCheckReply unlocks/calls success without day change")

# duplicate statusCheck is read-only.
avatar.statusCheckAsk("nextday", lambda: cb.append("duplicate"))
apply_frames(cases["status_check"]["duplicate_frames"])
assert "duplicate" in cb and avatar.weeknumData.daynum == 0
checks.append("duplicate original statusCheckAsk/reply remains read-only")

# 2. Original incDay request bytes; original calendar updateDay lock/reply.
sent[:] = []
avatar.cityData.action_val = 0
locks.add("updateDay")
avatar.incDayWhenNoActionVal(False)
params, order = request_match(cases["calendar"]["request"], sent[-1])
assert params == {} and order == [], "original incDayWhenNoActionVal sends an empty document"
assert avatar.weeknumData.sandglass_not_today is False
applied = apply_frames(cases["calendar"]["frames"])
assert "showMessageStr" not in applied, "accepted calendar is not rejected"
assert "updateDay" not in locks, "original updateDay reply releases the calendar wait"
assert avatar.weeknumData.daynum == 1, "original updateDay applies persisted day 1"
assert avatar.weeknumData.curDailyData == {"rsv": 0, "dvv": 0, "frv": 0}
assert avatar.weeknumData.lastDailyData == {"rsv": 0, "dvv": 0, "frv": 0}
assert ("city_update", {"from_lastday": True}) in events and "bbs_inc_day" in events and "update_weekday" in events
assert "check_events" in events
checks.append("original incDayWhenNoActionVal sends empty document; original updateDay/showDailySettlement apply day 1/c/l and release UI")

# 3. Duplicate incDay reply is same-day rejection; no second settlement.
before_day, before_events = avatar.weeknumData.daynum, len(events)
locks.add("updateDay")
applied = apply_frames(cases["calendar"]["duplicate_frames"])
assert applied == ["showMessageStr", "updateDay"], applied
assert avatar.weeknumData.daynum == before_day == 1 and "updateDay" not in locks
assert len(events) == before_events + 3, "only original updateDay notifications repeat, no settlement handler"
checks.append("duplicate incDay replays same-day updateDay unlock/message without a second settlement")

# 4. Writer failure emits no reply: the original calendar wait stays locked; retry advances.
locks.add("updateDay")
assert cases["writer_failure"]["frames"] == [] and "updateDay" in locks
assert avatar.weeknumData.daynum == 1
apply_frames(cases["writer_failure"]["retry_frames"])
assert "updateDay" not in locks and avatar.weeknumData.daynum == 1
checks.append("writer failure leaves the original wait locked with no fake reply; retry publishes updateDay once")

# 5. Blocked statusCheck uses original failCb, not successCb.
fail, success = [], []
avatar.statusCheckAsk("nextday", lambda: success.append(1), lambda: fail.append(1))
applied = apply_frames(cases["status_check_blocked"]["frames"])
assert "showMessageStr" in applied and fail == [1] and success == []
assert "statusCheck" not in locks and avatar.statusData.cur == "city" and avatar.weeknumData.daynum == 1
checks.append("blocked statusCheck calls original failCb and message path without day change")

result = {"status": "PASS", "source_sha256": pins, "checks": checks,
          "limits": ["selected original source bodies only; no NeoX opcode/render/JNI",
                     "statusData/weeknumData/cityData and UI are explicit host objects",
                     "host BSON reply bytes are decoded and applied without re-encoding"]}
Path(sys.argv[2]).write_text(json.dumps(result, indent=2) + "\n")
print("PASS original day consumer:", "; ".join(checks))
