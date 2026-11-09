"""Finite original ClientAvatar week-avatar consumer.

Runs the real original 640 source bodies for:
  WeekNumMember.handleIncWeekReply
  ClientAvatar.updateClientAvatarAsk
  ClientAvatar.updateClientAvatarReply
  WeekNumMember.handleIncWeekUpdateAvatar

init_from_dict / on_entity_creation / avatarClientDataLoad remain recording
leaves. No NeoX opcode, renderer, JNI, emulator or native client. The decoded
avatar fields are validated by verify.py; this consumer captures the real
handler/callback order and the outgoing updateClientAvatarAsk request.
"""
from pathlib import Path
import hashlib
import json
import sys
import textwrap
import types
import zlib
import msgpack
from bson import json_util

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


order = []
sent = []
gg = NS(logic=NS(sdk_report=lambda channel: order.append(("sdk_report", channel))))
const = NS(ChannelReport=NS(WEEKEND="weekend"))
env = {"gg": gg, "const": const, "zlib": zlib, "msgpack": msgpack, "json_util": json_util}

handle_inc_week_reply = original("analysis/original-py-640/entity/avatar_members/WeekNumMember.py", "handleIncWeekReply", env)
handle_inc_week_update_avatar = original("analysis/original-py-640/entity/avatar_members/WeekNumMember.py", "handleIncWeekUpdateAvatar", env)
update_avatar_ask = original("analysis/original-py-640/entity/ClientAvatar.py", "updateClientAvatarAsk", env)
update_avatar_reply = original("analysis/original-py-640/entity/ClientAvatar.py", "updateClientAvatarReply", env)

client = NS()
client.handleIncWeekCb = lambda: order.append("handleIncWeekCb")
client.updateClientAvatarCb = None


def call_server(method, params):
    sent.append({"method": method, "params": params, "order": list(params.keys())})


def leaf_avatar_save():
    order.append("avatarClientDataSave")


def leaf_init(data):
    order.append("init_from_dict")
    order.append(("decoded_keys_prefix", tuple(list(data.keys())[:7])))


def leaf_entity():
    order.append("on_entity_creation")


def leaf_avatar_load():
    order.append("avatarClientDataLoad")


client.avatarClientDataSave = leaf_avatar_save
client.init_from_dict = leaf_init
client.on_entity_creation = leaf_entity
client.avatarClientDataLoad = leaf_avatar_load
client.callServerMethod = call_server
client.handleIncWeekReply = types.MethodType(handle_inc_week_reply, client)
client.handleIncWeekUpdateAvatar = types.MethodType(handle_inc_week_update_avatar, client)
client.updateClientAvatarAsk = types.MethodType(update_avatar_ask, client)
client.updateClientAvatarReply = types.MethodType(update_avatar_reply, client)

wire = Path(sys.argv[2]).read_bytes()
client.handleIncWeekReply()
assert sent == [{"method": "updateClientAvatarAsk", "params": {}, "order": []}], sent
client.updateClientAvatarReply(wire)

expected = [
    "avatarClientDataSave",
    "init_from_dict",
    ("decoded_keys_prefix", ("st", "name", "an", "hn", "uid", "sv", "role")),
    "on_entity_creation",
    "avatarClientDataLoad",
    ("sdk_report", "weekend"),
    "handleIncWeekCb",
]
assert order == expected, (order, expected)
assert client.updateClientAvatarCb is None, "original handler clears updateClientAvatarCb"
assert client.handleIncWeekCb is None, "original callback clears handleIncWeekCb"

cases = json.loads(Path(sys.argv[1]).read_text())
result = {
    "status": "PASS",
    "source_sha256": pins,
    "wire_sha256": hashlib.sha256(wire).hexdigest(),
    "wire_bytes": len(wire),
    "decoded_bytes": len(zlib.decompress(wire)),
    "request": sent[0],
    "callback_order": [
        "avatarClientDataSave",
        "updateClientAvatarAsk",
        "zlib.decompress",
        "msgpack.loads(object_hook=bson.json_util.object_hook)",
        "init_from_dict(recording leaf)",
        "on_entity_creation(recording leaf)",
        "avatarClientDataLoad(recording leaf)",
        "sdk_report(WEEKEND)",
        "handleIncWeekCb",
    ],
    "actual_order": order,
    "cases_week": cases["handoff"]["week"],
    "limits": [
        "selected original source bodies only; no NeoX opcode/renderer/JNI/emulator",
        "init_from_dict, on_entity_creation, avatarClientDataLoad are recording leaves",
        "decoded field values are asserted by verify.py; this consumer asserts handler/callback order",
        "no native or UI claim",
    ],
}
Path(sys.argv[3]).write_text(json.dumps(result, indent=2) + "\n")
print("PASS original avatar consumer: handleIncWeekReply -> updateClientAvatarAsk -> updateClientAvatarReply -> handleIncWeekUpdateAvatar")
