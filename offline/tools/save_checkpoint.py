#!/usr/bin/env python3
"""Private Project7 (single-APK) save checkpoint helper.

This tool operates only on already-pulled, app-private ``files`` directories.
It never talks to a device, an emulator, adb, or a running gateway.

The save contract implemented here is the one written by the stock manager
classes bundled with the single APK:

    <files>/accounts.properties             account -> credential record
    <files>/account-ids.properties          account -> numeric id
    <files>/p7-bootstrap/identity.properties  StableIdentityBootstrap journal
    <files>/profiles/<account>.bson         LocalProfileStore profile
    <files>/tutorials/<account>.properties  LocalTutorialStore Progress v2

Only the profile and the tutorial file are story/state.  The account registry
and the bootstrap journal are identity anchors: they are *read* for binding
and are never copied into a checkpoint, because the record value is credential
material.  The account-record SHA-256 stored in the manifest is the same digest
StableIdentityBootstrap writes as ``accountRecordSha256``.

Exit codes: 0 success, 2 usage, 3 refused/verification failure, 1 unexpected.
"""

from __future__ import annotations
import _bootstrap  # noqa: E402,F401

import argparse
import datetime as _dt
import hashlib
import json
import os
import re
import shutil
import struct
import sys
from pathlib import Path

MANIFEST_SCHEMA = "project7-save-checkpoint/v1"
TOOL_FORMAT = 1
PROGRESS_SCHEMA = "2"

PROFILE_MAX_BYTES = 32 * 1024 * 1024
PROGRESS_MAX_BYTES = 4 * 1024 * 1024
MANIFEST_MAX_BYTES = 2 * 1024 * 1024
REGISTRY_MAX_BYTES = 4 * 1024 * 1024
IDENTITY_MAX_BYTES = 64 * 1024

ACCOUNT_RE = re.compile(r"^offline_[0-9a-f]{24}$")
ACCOUNT_NAME_RE = re.compile(r"^[A-Za-z0-9_.-]{1,32}$")
LABEL_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,63}$")
HEX64_RE = re.compile(r"^[0-9a-f]{64}$")
COMMIT_RE = re.compile(r"^[0-9a-f]{24}$")
INT_RE = re.compile(r"^-?(0|[1-9][0-9]*)$")
DAY_RE = re.compile(r"^-?[0-9]+:-?[0-9]+$")
SCENE_RE = re.compile(r"^$|^[0-9]+$")
UTC_RE = re.compile(r"^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z$")

# LocalAccountStore.isTemplateAccount treats these as built-in templates.
TEMPLATE_ACCOUNTS = frozenset({"tencolors", "hakopania"})

# LocalTutorialStore.Progress schema 2 keys required by
# StableIdentityBootstrap.preflight (PROGRESS_KEYS).
REQUIRED_PROGRESS_KEYS = (
    "schemaVersion",
    "availableEvents",
    "processingEvents",
    "completedEvents",
    "initPrologue",
    "processingNewbees",
    "finishedNewbees",
    "inEmergency",
    "status",
    "scene",
    "patrol.count",
    "patrol.area",
    "patrol.day",
    "patrol.actions",
    "patrol.sandglass",
    "economy.commit",
    "week.commit",
    "week.index",
    "patrol.favor",
    "patrol.rewardPending",
    "patrol.heroes",
    "patrol.events",
    "patrol.replays",
)

SET_FIELDS = (
    "availableEvents",
    "processingEvents",
    "completedEvents",
    "processingNewbees",
    "finishedNewbees",
    "patrol.heroes",
    "patrol.events",
    "patrol.replays",
)
INT_FIELDS = (
    "patrol.count",
    "patrol.area",
    "patrol.actions",
    "patrol.sandglass",
    "week.index",
    "patrol.favor",
)
BOOL_FIELDS = ("initPrologue", "inEmergency", "patrol.rewardPending")
STRING_FIELDS = ("status", "scene", "patrol.day")
COMMIT_FIELDS = ("economy.commit", "week.commit")

DYNAMIC_KEY_PATTERNS = (
    (re.compile(r"^patrol\.fatigue\.([1-9][0-9]*)$"), "int_map", "patrol_fatigue"),
    (re.compile(r"^patrol\.friendly\.([1-9][0-9]*)$"), "int_map", "patrol_friendly"),
    (re.compile(r"^patrol\.bonus\.([1-9][0-9]*)$"), "int_map", "patrol_bonus"),
    (re.compile(r"^condition\.([^\s]+)$"), "int_set_map", "conditions"),
    (re.compile(r"^event\.completed\.([1-9][0-9]*)$"), "posint_map", "event_completions"),
    (re.compile(r"^event\.day\.([1-9][0-9]*)$"), "day_map", "event_days"),
)

MILESTONES = ("hospital-menu-v1", "collection-menu-v1", "login-v1")

DEVICE_PATH_PREFIXES = (
    "/data/",
    "/sdcard/",
    "/storage/",
    "/mnt/",
    "/system/",
    "/vendor/",
    "/product/",
)


class Refusal(Exception):
    """A deliberate, stable refusal with a machine-readable code."""

    def __init__(self, code: str, detail: str):
        super().__init__(f"{code}: {detail}")
        self.code = code
        self.detail = detail


# ---------------------------------------------------------------------------
# small utilities
# ---------------------------------------------------------------------------


def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical_json(value) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")


def utc_now() -> str:
    return _dt.datetime.now(_dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def read_limited(path: Path, limit: int, code: str) -> bytes:
    if path.is_symlink():
        raise Refusal(code, f"refusing symlink: {path}")
    if not path.is_file():
        raise Refusal(code, f"not a regular file: {path}")
    size = path.stat().st_size
    if size <= 0 or size > limit:
        raise Refusal(code, f"invalid size {size} for {path}")
    with open(path, "rb") as handle:
        data = handle.read(limit + 1)
    if len(data) != size or len(data) > limit:
        raise Refusal(code, f"file changed while reading: {path}")
    return data


def label_dir(root: Path, label: str) -> Path:
    if not LABEL_RE.match(label or ""):
        raise Refusal("LABEL_INVALID", f"label must match {LABEL_RE.pattern}")
    return root / label


def resolve_files_root(path: Path) -> Path:
    """Accept either a ``files`` directory or a parent that contains ``files``."""
    if not path.exists():
        raise Refusal("ROOT_NOT_FOUND", f"directory does not exist: {path}")
    if not path.is_dir():
        raise Refusal("ROOT_NOT_DIRECTORY", f"not a directory: {path}")
    nested = path / "files"
    if nested.is_dir() and (nested / "profiles").is_dir():
        return nested
    return path


def _assert_local_target(path: Path) -> None:
    candidates = {os.path.abspath(os.fspath(path)), os.path.realpath(os.fspath(path))}
    for resolved in candidates:
        for prefix in DEVICE_PATH_PREFIXES:
            if resolved.startswith(prefix):
                raise Refusal(
                    "DEVICE_PATH_REFUSED",
                    f"restore target looks like a live device path: {resolved}",
                )
        if "/Android/data/" in resolved:
            raise Refusal(
                "DEVICE_PATH_REFUSED",
                f"restore target looks like external Android storage: {resolved}",
            )


def _check_absent_or_regular(path: Path, code: str) -> None:
    if path.exists() and (path.is_symlink() or not path.is_file()):
        raise Refusal(code, f"unexpected file type: {path}")


# ---------------------------------------------------------------------------
# java.util.Properties subset (load side only)
# ---------------------------------------------------------------------------


def _ends_with_odd_backslashes(text: str) -> bool:
    count = 0
    index = len(text) - 1
    while index >= 0 and text[index] == "\\":
        count += 1
        index -= 1
    return count % 2 == 1


def _java_unescape(text: str) -> str:
    out = []
    index = 0
    while index < len(text):
        char = text[index]
        index += 1
        if char != "\\":
            out.append(char)
            continue
        if index >= len(text):
            raise Refusal("PROPERTIES_PARSE", "dangling backslash escape")
        escaped = text[index]
        index += 1
        if escaped == "u":
            digits = text[index : index + 4]
            if len(digits) != 4 or not re.match(r"^[0-9a-fA-F]{4}$", digits):
                raise Refusal("PROPERTIES_PARSE", "malformed \\uXXXX escape")
            out.append(chr(int(digits, 16)))
            index += 4
        elif escaped == "t":
            out.append("\t")
        elif escaped == "n":
            out.append("\n")
        elif escaped == "r":
            out.append("\r")
        elif escaped == "f":
            out.append("\f")
        else:
            out.append(escaped)
    return "".join(out)


def _split_property(line: str) -> tuple[str, str]:
    key_chars: list[str] = []
    index = 0
    length = len(line)
    escaped = False
    while index < length:
        char = line[index]
        if escaped:
            key_chars.append("\\")
            key_chars.append(char)
            escaped = False
            index += 1
            continue
        if char == "\\":
            escaped = True
            index += 1
            continue
        if char in "=: \t\f":
            break
        key_chars.append(char)
        index += 1
    if escaped:
        raise Refusal("PROPERTIES_PARSE", "dangling backslash in key")
    key = _java_unescape("".join(key_chars))
    while index < length and line[index] in " \t\f":
        index += 1
    if index < length and line[index] in "=:":
        index += 1
        while index < length and line[index] in " \t\f":
            index += 1
    value = _java_unescape(line[index:])
    if not key:
        raise Refusal("PROPERTIES_PARSE", "empty property key")
    return key, value


def parse_java_properties(data: bytes, code: str = "PROPERTIES_PARSE") -> dict[str, str]:
    """Parse the subset of java.util.Properties.load used by the stock stores.

    Rejects duplicate keys, dangling continuations and malformed escapes.  The
    stock ``Properties.store`` writer never emits any of those, so a duplicate
    key means the file was hand-edited or corrupted.
    """
    try:
        text = data.decode("latin-1")
    except UnicodeDecodeError as error:  # pragma: no cover - latin-1 never fails
        raise Refusal(code, f"cannot decode properties: {error}") from None
    physical = re.split(r"\r\n|\r|\n", text)
    result: dict[str, str] = {}
    index = 0
    while index < len(physical):
        raw = physical[index]
        index += 1
        stripped = raw.lstrip(" \t\f")
        if not stripped:
            continue
        if stripped[0] in "#!":
            continue
        logical = stripped
        while _ends_with_odd_backslashes(logical):
            if index >= len(physical):
                raise Refusal(code, "dangling line continuation")
            logical = logical[:-1] + physical[index].lstrip(" \t\f")
            index += 1
        key, value = _split_property(logical)
        if key in result:
            raise Refusal(code, f"duplicate key {key!r}")
        result[key] = value
    return result


def java_properties_escape(text: str, key: bool = False) -> str:
    """Escape a value the way java.util.Properties.store does (ASCII subset)."""
    out = []
    for char in text:
        if char == "\\":
            out.append("\\\\")
        elif char == "\t":
            out.append("\\t")
        elif char == "\n":
            out.append("\\n")
        elif char == "\r":
            out.append("\\r")
        elif char == "\f":
            out.append("\\f")
        elif char in "=:" or (key and char in " #!"):
            out.append("\\" + char)
        elif char == " " and key:
            out.append("\\ ")
        elif ord(char) < 0x20 or ord(char) > 0x7E:
            out.append("\\u%04X" % ord(char))
        else:
            out.append(char)
    return "".join(out)


# ---------------------------------------------------------------------------
# strict BSON decoder (stdlib only)
# ---------------------------------------------------------------------------


class BSONError(ValueError):
    pass


def _need(data: bytes, position: int, count: int, end: int) -> None:
    if count < 0 or position < 0 or position + count > end:
        raise BSONError("truncated BSON element")


def _i32(data: bytes, position: int, end: int) -> int:
    _need(data, position, 4, end)
    return struct.unpack_from("<i", data, position)[0]


def _i64(data: bytes, position: int, end: int) -> int:
    _need(data, position, 8, end)
    return struct.unpack_from("<q", data, position)[0]


def _cstring(data: bytes, position: int, end: int) -> tuple[str, int]:
    stop = data.find(b"\x00", position, end)
    if stop < 0:
        raise BSONError("unterminated cstring")
    raw = data[position:stop]
    try:
        return raw.decode("utf-8"), stop + 1
    except UnicodeDecodeError:
        raise BSONError("invalid UTF-8 in cstring") from None


def _string(data: bytes, position: int, end: int) -> tuple[str, int]:
    length = _i32(data, position, end)
    if length < 1:
        raise BSONError("invalid string length")
    start = position + 4
    _need(data, start, length, end)
    if data[start + length - 1] != 0:
        raise BSONError("string is not NUL terminated")
    try:
        value = data[start : start + length - 1].decode("utf-8")
    except UnicodeDecodeError:
        raise BSONError("invalid UTF-8 string") from None
    return value, start + length


def _decode_document(data: bytes, start: int, limit: int) -> tuple[dict, int]:
    size = _i32(data, start, limit)
    if size < 5:
        raise BSONError("document too small")
    end = start + size
    if end > limit:
        raise BSONError("document length exceeds buffer")
    position = start + 4
    document: dict = {}
    while position < end - 1:
        element_type = data[position]
        position += 1
        name, position = _cstring(data, position, end)
        if name in document:
            raise BSONError(f"duplicate BSON key {name!r}")
        value, position = _decode_value(data, position, end, element_type)
        document[name] = value
    if position != end - 1 or data[end - 1] != 0:
        raise BSONError("document terminator mismatch")
    return document, end


def _decode_value(data: bytes, position: int, end: int, element_type: int):
    if element_type == 0x01:  # double
        _need(data, position, 8, end)
        return struct.unpack_from("<d", data, position)[0], position + 8
    if element_type == 0x02:  # string
        return _string(data, position, end)
    if element_type == 0x03:  # embedded document
        return _decode_document(data, position, end)
    if element_type == 0x04:  # array
        document, next_position = _decode_document(data, position, end)
        expected = [str(i) for i in range(len(document))]
        if list(document.keys()) != expected:
            raise BSONError("non-canonical BSON array keys")
        return list(document.values()), next_position
    if element_type == 0x05:  # binary
        length = _i32(data, position, end)
        if length < 0:
            raise BSONError("negative binary length")
        start = position + 5
        _need(data, start, length, end)
        return {"$binary": data[start : start + length], "$type": data[position + 4]}, start + length
    if element_type == 0x06:  # deprecated undefined
        return {"$undefined": True}, position
    if element_type == 0x07:  # ObjectId
        _need(data, position, 12, end)
        return {"$oid": data[position : position + 12].hex()}, position + 12
    if element_type == 0x08:  # boolean
        _need(data, position, 1, end)
        if data[position] not in (0, 1):
            raise BSONError("invalid boolean byte")
        return bool(data[position]), position + 1
    if element_type == 0x09:  # UTC datetime (milliseconds)
        return _i64(data, position, end), position + 8
    if element_type == 0x0A:  # null
        return None, position
    if element_type == 0x0B:  # regex
        pattern, position = _cstring(data, position, end)
        options, position = _cstring(data, position, end)
        return {"$regex": pattern, "$options": options}, position
    if element_type == 0x0C:  # DBPointer
        namespace, position = _string(data, position, end)
        _need(data, position, 12, end)
        return {"$dbpointer": namespace, "$oid": data[position : position + 12].hex()}, position + 12
    if element_type in (0x0D, 0x0E):  # JavaScript / symbol
        return _string(data, position, end)
    if element_type == 0x0F:  # code with scope
        total = _i32(data, position, end)
        if total < 14:
            raise BSONError("invalid code_w_scope length")
        code_end = position + total
        if code_end > end:
            raise BSONError("code_w_scope exceeds buffer")
        code, inner = _string(data, position + 4, code_end)
        scope, inner = _decode_document(data, inner, code_end)
        if inner != code_end:
            raise BSONError("code_w_scope length mismatch")
        return {"$code": code, "$scope": scope}, code_end
    if element_type == 0x10:  # int32
        value = _i32(data, position, end)
        return value, position + 4
    if element_type == 0x11:  # timestamp
        _need(data, position, 8, end)
        return int.from_bytes(data[position : position + 8], "little", signed=False), position + 8
    if element_type == 0x12:  # int64
        return _i64(data, position, end), position + 8
    if element_type == 0x13:  # decimal128
        _need(data, position, 16, end)
        return {"$decimal128": data[position : position + 16].hex()}, position + 16
    if element_type == 0x7F:  # max key
        return {"$maxkey": True}, position
    if element_type == 0xFF:  # min key
        return {"$minkey": True}, position
    raise BSONError(f"unsupported BSON element type 0x{element_type:02x}")


def bson_decode(data: bytes) -> dict:
    if len(data) < 5:
        raise BSONError("buffer too small")
    declared = int.from_bytes(data[:4], "little", signed=True)
    if declared != len(data):
        raise BSONError(f"declared length {declared} != actual {len(data)}")
    document, position = _decode_document(data, 0, len(data))
    if position != len(data):
        raise BSONError("trailing bytes after BSON document")
    return document


# ---------------------------------------------------------------------------
# typed accessors
# ---------------------------------------------------------------------------


def _type_name(value) -> str:
    if value is None:
        return "null"
    if type(value) is bool:
        return "bool"
    if type(value) is int:
        return "int"
    if type(value) is str:
        return "str"
    if type(value) is dict:
        return "document"
    if type(value) is list:
        return "array"
    return type(value).__name__


def _require_int(document: dict, key: str, code: str, path: str) -> int:
    if key not in document:
        raise Refusal(code, f"{path}.{key} is missing")
    value = document[key]
    if type(value) is not int:
        raise Refusal(code, f"{path}.{key} must be int, got {_type_name(value)}")
    if not -(2**31) <= value < 2**31:
        raise Refusal(code, f"{path}.{key} outside int32 range")
    return value


def _require_int64(document: dict, key: str, code: str, path: str) -> int:
    if key not in document:
        raise Refusal(code, f"{path}.{key} is missing")
    value = document[key]
    if type(value) is not int:
        raise Refusal(code, f"{path}.{key} must be int, got {_type_name(value)}")
    return value


def _require_str(document: dict, key: str, code: str, path: str) -> str:
    if key not in document:
        raise Refusal(code, f"{path}.{key} is missing")
    value = document[key]
    if type(value) is not str:
        raise Refusal(code, f"{path}.{key} must be str, got {_type_name(value)}")
    return value


def _optional_int(document: dict, key: str, code: str, path: str) -> int | None:
    if key not in document:
        return None
    value = document[key]
    if type(value) is not int:
        raise Refusal(code, f"{path}.{key} must be int, got {_type_name(value)}")
    return value


def _optional_str(document: dict, key: str, code: str, path: str) -> str | None:
    if key not in document:
        return None
    value = document[key]
    if type(value) is not str:
        raise Refusal(code, f"{path}.{key} must be str, got {_type_name(value)}")
    return value


def _require_document(document: dict, key: str, code: str, path: str) -> dict:
    if key not in document:
        raise Refusal(code, f"{path}.{key} is missing")
    value = document[key]
    if type(value) is not dict:
        raise Refusal(code, f"{path}.{key} must be document, got {_type_name(value)}")
    return value


# ---------------------------------------------------------------------------
# profile inspection
# ---------------------------------------------------------------------------


def inspect_profile(data: bytes, account: str, numeric_id: int) -> dict:
    try:
        document = bson_decode(data)
    except BSONError as error:
        raise Refusal("PROFILE_BSON_INVALID", str(error)) from None

    stored_account = _require_str(document, "account", "PROFILE_SCHEMA", "profile")
    stored_alias = _require_str(document, "an", "PROFILE_SCHEMA", "profile")
    stored_uid = _require_int(document, "uid", "PROFILE_SCHEMA", "profile")
    if stored_account != account or stored_alias != account:
        raise Refusal(
            "PROFILE_IDENTITY_MISMATCH",
            f"profile account={stored_account!r} an={stored_alias!r} expected {account!r}",
        )
    if stored_uid != numeric_id:
        raise Refusal(
            "PROFILE_IDENTITY_MISMATCH",
            f"profile uid={stored_uid} expected numeric id {numeric_id}",
        )

    weeknum = _require_document(document, "weeknum", "PROFILE_SCHEMA", "profile")
    week_index = _require_int(weeknum, "w", "PROFILE_SCHEMA", "profile.weeknum")
    week_day = _require_int(weeknum, "d", "PROFILE_SCHEMA", "profile.weeknum")
    if week_index < 0 or week_day < 0:
        raise Refusal("PROFILE_SCHEMA", "weeknum w/d must be non-negative")

    save_version = _optional_int(document, "sv", "PROFILE_SCHEMA", "profile")
    level = _optional_int(document, "level", "PROFILE_SCHEMA", "profile")

    battle = document.get("q7Battle")
    if battle is not None and type(battle) is not dict:
        raise Refusal("PROFILE_SCHEMA", "profile.q7Battle must be a document")
    battle_open = bool(battle)

    week_receipt = None
    raw_week = document.get("q7WeekTransition")
    if raw_week is not None:
        if type(raw_week) is not dict:
            raise Refusal("PROFILE_SCHEMA", "profile.q7WeekTransition must be a document")
        receipt_id = _require_str(raw_week, "id", "PROFILE_WEEK_RECEIPT", "q7WeekTransition")
        if not COMMIT_RE.match(receipt_id):
            raise Refusal(
                "PROFILE_WEEK_RECEIPT",
                f"q7WeekTransition.id is not a 24-hex commit id: {receipt_id!r}",
            )
        receipt_week = _require_int(raw_week, "week", "PROFILE_WEEK_RECEIPT", "q7WeekTransition")
        receipt_method = _require_str(raw_week, "method", "PROFILE_WEEK_RECEIPT", "q7WeekTransition")
        receipt_route = _require_int(raw_week, "route", "PROFILE_WEEK_RECEIPT", "q7WeekTransition")
        receipt_progress = _require_document(
            raw_week, "progress", "PROFILE_WEEK_RECEIPT", "q7WeekTransition"
        )
        for key in REQUIRED_PROGRESS_KEYS:
            if key not in receipt_progress:
                raise Refusal(
                    "PROFILE_WEEK_RECEIPT",
                    f"q7WeekTransition.progress missing {key!r}",
                )
            if type(receipt_progress[key]) is not str:
                raise Refusal(
                    "PROFILE_WEEK_RECEIPT",
                    f"q7WeekTransition.progress.{key} must be str",
                )
        if receipt_progress.get("schemaVersion") != PROGRESS_SCHEMA:
            raise Refusal(
                "PROFILE_WEEK_RECEIPT",
                "q7WeekTransition.progress.schemaVersion is not 2",
            )
        if receipt_progress.get("week.commit") != receipt_id:
            raise Refusal(
                "PROFILE_WEEK_RECEIPT",
                "q7WeekTransition.progress.week.commit does not equal receipt id",
            )
        if receipt_progress.get("week.index") != str(receipt_week):
            raise Refusal(
                "PROFILE_WEEK_RECEIPT",
                "q7WeekTransition.progress.week.index does not equal receipt week",
            )
        week_receipt = {
            "id": receipt_id,
            "week": receipt_week,
            "method": receipt_method,
            "route": receipt_route,
            "progress_sha256": sha256_hex(canonical_json(receipt_progress)),
        }

    economy_receipt_id = None
    raw_economy = document.get("q7EconomyCommit")
    if raw_economy is not None:
        if type(raw_economy) is not dict:
            raise Refusal("PROFILE_SCHEMA", "profile.q7EconomyCommit must be a document")
        economy_receipt_id = _require_str(
            raw_economy, "id", "PROFILE_ECONOMY_RECEIPT", "q7EconomyCommit"
        )
        if not COMMIT_RE.match(economy_receipt_id):
            raise Refusal(
                "PROFILE_ECONOMY_RECEIPT",
                f"q7EconomyCommit.id is not a 24-hex commit id: {economy_receipt_id!r}",
            )

    collection_receipt = None
    raw_collection = document.get("q7FullCollectionReceiptV1")
    if raw_collection is not None:
        if type(raw_collection) is not dict:
            raise Refusal("PROFILE_SCHEMA", "profile.q7FullCollectionReceiptV1 must be a document")
        collection_receipt = {
            "schema": _require_int(
                raw_collection, "schema", "PROFILE_COLLECTION_RECEIPT", "q7FullCollectionReceiptV1"
            ),
            "policy": _require_str(
                raw_collection, "policy", "PROFILE_COLLECTION_RECEIPT", "q7FullCollectionReceiptV1"
            ),
        }
        for key in ("targets", "catalog", "contract"):
            value = _require_str(
                raw_collection, key, "PROFILE_COLLECTION_RECEIPT", "q7FullCollectionReceiptV1"
            )
            if not HEX64_RE.match(value):
                raise Refusal(
                    "PROFILE_COLLECTION_RECEIPT",
                    f"q7FullCollectionReceiptV1.{key} is not a SHA-256 hex digest",
                )
            collection_receipt[key] = value

    counts = {}
    hero_manager = document.get("heromgr")
    if hero_manager is not None:
        if type(hero_manager) is not dict:
            raise Refusal("PROFILE_SCHEMA", "profile.heromgr must be a document")
        heroes = hero_manager.get("hrs")
        if heroes is not None:
            if type(heroes) is list:
                counts["hero_records"] = len(heroes)
            elif type(heroes) is dict:
                counts["hero_records"] = len(heroes)
            else:
                raise Refusal(
                    "PROFILE_SCHEMA", "profile.heromgr.hrs must be a document or array"
                )
        extra_skins = hero_manager.get("es")
        if extra_skins is not None:
            if type(extra_skins) is not list:
                raise Refusal("PROFILE_SCHEMA", "profile.heromgr.es must be an array")
            counts["extra_skin_ids"] = len(extra_skins)
    inventory = document.get("inv")
    if inventory is not None:
        if type(inventory) is not dict:
            raise Refusal("PROFILE_SCHEMA", "profile.inv must be a document")
        items = inventory.get("items")
        if items is not None:
            if type(items) is not list:
                raise Refusal("PROFILE_SCHEMA", "profile.inv.items must be an array")
            counts["inventory_items"] = len(items)

    return {
        "account": account,
        "numeric_id": stored_uid,
        "save_version": save_version,
        "level": level,
        "top_level_key_count": len(document),
        "week": {"index": week_index, "day": week_day},
        "battle_open": battle_open,
        "week_receipt": week_receipt,
        "economy_receipt_id": economy_receipt_id,
        "collection_receipt": collection_receipt,
        "counts": counts,
    }


# ---------------------------------------------------------------------------
# Progress (tutorials/*.properties) inspection
# ---------------------------------------------------------------------------


def _parse_canonical_int(text: str, key: str) -> int:
    if not INT_RE.match(text or ""):
        raise Refusal("PROGRESS_VALUE_INVALID", f"{key}={text!r} is not a canonical integer")
    value = int(text)
    if not -(2**31) <= value < 2**31:
        raise Refusal("PROGRESS_VALUE_INVALID", f"{key}={text!r} outside int32 range")
    return value


def _parse_id_set(text: str, key: str) -> tuple[int, ...]:
    if text.strip() == "":
        return ()
    parts = text.split(",")
    values = []
    seen = set()
    for part in parts:
        if part != part.strip() or not re.match(r"^[1-9][0-9]*$", part):
            raise Refusal("PROGRESS_VALUE_INVALID", f"{key} has non-canonical id {part!r}")
        value = int(part)
        if value > 2**31 - 1:
            raise Refusal("PROGRESS_VALUE_INVALID", f"{key} id outside int32 range")
        if value in seen:
            raise Refusal("PROGRESS_VALUE_INVALID", f"{key} repeats id {value}")
        seen.add(value)
        values.append(value)
    return tuple(values)


def _check_sorted(name: str, values: tuple[int, ...]) -> None:
    if name == "completedEvents":
        return
    if list(values) != sorted(values):
        raise Refusal("PROGRESS_VALUE_INVALID", f"{name} is not sorted like Progress.join()")


def inspect_progress(data: bytes) -> dict:
    properties = parse_java_properties(data)

    missing = [key for key in REQUIRED_PROGRESS_KEYS if key not in properties]
    if missing:
        raise Refusal(
            "PROGRESS_SCHEMA",
            f"missing required Progress keys: {', '.join(sorted(missing))}",
        )
    if properties["schemaVersion"] != PROGRESS_SCHEMA:
        raise Refusal(
            "PROGRESS_SCHEMA",
            f"schemaVersion={properties['schemaVersion']!r}, expected '2'",
        )

    known = set(REQUIRED_PROGRESS_KEYS)
    dynamic: dict[str, dict] = {
        "patrol_fatigue": {},
        "patrol_friendly": {},
        "patrol_bonus": {},
        "conditions": {},
        "event_completions": {},
        "event_days": {},
    }
    for key in properties:
        if key in known:
            continue
        matched = False
        for pattern, kind, bucket in DYNAMIC_KEY_PATTERNS:
            match = pattern.match(key)
            if not match:
                continue
            matched = True
            identifier = match.group(1)
            text = properties[key]
            if kind == "int_map":
                value = _parse_canonical_int(text, key)
                dynamic[bucket][int(identifier)] = value
            elif kind == "int_set_map":
                dynamic[bucket][identifier] = _parse_id_set(text, key)
            elif kind == "posint_map":
                value = _parse_canonical_int(text, key)
                if value <= 0:
                    raise Refusal(
                        "PROGRESS_VALUE_INVALID",
                        f"{key}={value} must be positive",
                    )
                dynamic[bucket][int(identifier)] = value
            elif kind == "day_map":
                if not DAY_RE.match(text or ""):
                    raise Refusal(
                        "PROGRESS_VALUE_INVALID", f"{key}={text!r} is not a day 'w:d'"
                    )
                dynamic[bucket][int(identifier)] = text
            break
        if not matched:
            raise Refusal("PROGRESS_SCHEMA", f"unknown Progress v2 key {key!r}")

    sets: dict[str, tuple[int, ...]] = {}
    for name in SET_FIELDS:
        sets[name] = _parse_id_set(properties[name], name)
        _check_sorted(name, sets[name])

    ints: dict[str, int] = {}
    for name in INT_FIELDS:
        ints[name] = _parse_canonical_int(properties[name], name)
    if ints["week.index"] < 0:
        raise Refusal("PROGRESS_VALUE_INVALID", "week.index must be non-negative")
    if ints["patrol.count"] < 0 or ints["patrol.area"] < 0 or ints["patrol.favor"] < 0:
        raise Refusal(
            "PROGRESS_VALUE_INVALID",
            "patrol.count/patrol.area/patrol.favor must be non-negative",
        )
    if ints["patrol.actions"] < -1 or ints["patrol.sandglass"] < -1:
        raise Refusal(
            "PROGRESS_VALUE_INVALID",
            "patrol.actions/patrol.sandglass must be >= -1",
        )

    bools: dict[str, bool] = {}
    for name in BOOL_FIELDS:
        text = properties[name]
        if text not in ("true", "false"):
            raise Refusal("PROGRESS_VALUE_INVALID", f"{name}={text!r} is not true/false")
        bools[name] = text == "true"

    strings: dict[str, str] = {}
    for name in STRING_FIELDS:
        strings[name] = properties[name]
    if not strings["status"] or any(ord(char) < 0x20 for char in strings["status"]):
        raise Refusal("PROGRESS_VALUE_INVALID", "status must be a non-empty printable string")
    if not SCENE_RE.match(strings["scene"]):
        raise Refusal("PROGRESS_VALUE_INVALID", f"scene={strings['scene']!r} is not numeric")
    if strings["patrol.day"] != "" and not DAY_RE.match(strings["patrol.day"]):
        raise Refusal(
            "PROGRESS_VALUE_INVALID",
            f"patrol.day={strings['patrol.day']!r} is not a day 'w:d'",
        )

    commits = {}
    for name in COMMIT_FIELDS:
        value = properties[name]
        if value != "" and not COMMIT_RE.match(value):
            raise Refusal(
                "PROGRESS_VALUE_INVALID",
                f"{name}={value!r} is not a 24-hex commit id",
            )
        commits[name] = value

    if bools["inEmergency"] != (strings["status"] == "emergency"):
        raise Refusal(
            "STORY_INCONSISTENT",
            f"inEmergency={bools['inEmergency']} with status={strings['status']!r}",
        )

    return {
        "schema": PROGRESS_SCHEMA,
        "sets": sets,
        "ints": ints,
        "bools": bools,
        "strings": strings,
        "commits": commits,
        "conditions": dynamic["conditions"],
        "event_completions": dynamic["event_completions"],
        "event_days": dynamic["event_days"],
        "patrol_fatigue": dynamic["patrol_fatigue"],
        "patrol_friendly": dynamic["patrol_friendly"],
        "patrol_bonus": dynamic["patrol_bonus"],
    }


# ---------------------------------------------------------------------------
# story / consistency / milestone
# ---------------------------------------------------------------------------


def build_consistency(profile: dict, progress: dict) -> dict:
    completed = set(progress["sets"]["completedEvents"])
    processing = set(progress["sets"]["processingEvents"])
    available = set(progress["sets"]["availableEvents"])
    finished = set(progress["sets"]["finishedNewbees"])
    processing_newbees = set(progress["sets"]["processingNewbees"])

    if completed & processing:
        raise Refusal(
            "STORY_INCONSISTENT",
            f"events both completed and processing: {sorted(completed & processing)}",
        )
    if processing_newbees & finished:
        raise Refusal(
            "STORY_INCONSISTENT",
            f"newbees both processing and finished: {sorted(processing_newbees & finished)}",
        )

    counters = progress["event_completions"]
    counter_only = sorted(set(counters) - completed)
    if counter_only:
        raise Refusal(
            "STORY_INCONSISTENT",
            f"event.completed counters without completedEvents: {counter_only}",
        )
    day_only = sorted(set(progress["event_days"]) - completed)
    available_completed = sorted(available & completed)

    if progress["ints"]["week.index"] != profile["week"]["index"]:
        raise Refusal(
            "CONSISTENCY_WEEK_MISMATCH",
            f"Progress week.index={progress['ints']['week.index']} "
            f"!= profile.weeknum.w={profile['week']['index']}",
        )

    week_commit = progress["commits"]["week.commit"]
    receipt = profile["week_receipt"]
    if receipt is not None:
        if receipt["id"] != week_commit:
            raise Refusal(
                "CONSISTENCY_WEEK_RECEIPT",
                f"q7WeekTransition.id={receipt['id']} != week.commit={week_commit!r}",
            )
        if receipt["week"] != profile["week"]["index"]:
            raise Refusal(
                "CONSISTENCY_WEEK_RECEIPT",
                f"q7WeekTransition.week={receipt['week']} != weeknum.w={profile['week']['index']}",
            )
    elif week_commit != "":
        # LocalWeekEngine.recover only acts when a receipt exists, so a
        # consumed/absent receipt with a non-empty commit is a stable state.
        pass

    economy_commit = progress["commits"]["economy.commit"]
    if profile["economy_receipt_id"] is not None:
        if profile["economy_receipt_id"] != economy_commit:
            raise Refusal(
                "CONSISTENCY_ECONOMY_RECEIPT",
                f"q7EconomyCommit.id={profile['economy_receipt_id']} "
                f"!= economy.commit={economy_commit!r}",
            )

    warnings = []
    if available_completed:
        warnings.append(
            "available_completed_overlap:" + ",".join(str(v) for v in available_completed)
        )
    if day_only:
        warnings.append(
            "event_day_without_completed:" + ",".join(str(v) for v in day_only)
        )

    return {
        "completed_processing_disjoint": True,
        "processing_finished_newbees_disjoint": True,
        "completion_counters_subset": True,
        "week_index_matches_profile": True,
        "week_receipt_matches": receipt is not None,
        "economy_receipt_matches": profile["economy_receipt_id"] is not None,
        "battle_closed": not profile["battle_open"],
        "warnings": warnings,
    }


def build_story_block(progress: dict, milestone: str) -> dict:
    event_completions = [
        [event, count] for event, count in sorted(progress["event_completions"].items())
    ]
    return {
        "milestone": milestone,
        "init_prologue": progress["bools"]["initPrologue"],
        "in_emergency": progress["bools"]["inEmergency"],
        "status": progress["strings"]["status"],
        "scene": progress["strings"]["scene"],
        "week_index": progress["ints"]["week.index"],
        "week_commit": progress["commits"]["week.commit"],
        "completed_events": list(progress["sets"]["completedEvents"]),
        "available_events": list(progress["sets"]["availableEvents"]),
        "processing_events": list(progress["sets"]["processingEvents"]),
        "processing_newbees": list(progress["sets"]["processingNewbees"]),
        "finished_newbees": list(progress["sets"]["finishedNewbees"]),
        "patrol_reward_pending": progress["bools"]["patrol.rewardPending"],
        "event_completions": event_completions,
        "quiescent": (
            not progress["sets"]["processingEvents"]
            and not progress["sets"]["processingNewbees"]
            and not progress["bools"]["patrol.rewardPending"]
        ),
    }


def _story_digest(story_without_digest: dict) -> str:
    return sha256_hex(canonical_json(story_without_digest))


def enforce_milestone(story: dict, profile: dict, progress: dict) -> None:
    milestone = story["milestone"]
    problems: list[str] = []
    if profile["battle_open"]:
        problems.append("q7Battle is not empty")
    if profile["week_receipt"] is not None or story["week_commit"] != "":
        problems.append("a week transition receipt/commit is present")
    if story["week_index"] != 0 or profile["week"]["index"] != 0:
        problems.append(
            f"first-run checkpoint requires week 0, got Progress={story['week_index']} "
            f"profile={profile['week']['index']}"
        )

    completed = set(progress["sets"]["completedEvents"])
    processing = set(progress["sets"]["processingEvents"])
    available = set(progress["sets"]["availableEvents"])

    if milestone == "hospital-menu-v1":
        # "Arrival" is proven by event 1000 being engaged: either its prologue
        # is complete or it is the event currently being processed.  A
        # pre-hospital fresh save only has 1000 in availableEvents.
        if not (1000 in completed or 1000 in processing):
            problems.append(
                "event 1000 (hospital prologue) is neither completed nor processing"
            )
        if story["status"] not in ("city", "emergency"):
            problems.append(
                f"status must be city or emergency, got {story['status']!r}"
            )
    elif milestone == "collection-menu-v1":
        if story["status"] != "bbs":
            problems.append(
                f"collection menu requires status=bbs, got {story['status']!r}"
            )
        if 1000 not in completed:
            problems.append("collection menu requires hospital prologue event 1000 completed")
        if progress["bools"]["inEmergency"]:
            problems.append("collection menu must not be in emergency state")
    elif milestone == "login-v1":
        if story["status"] not in ("emergency", "city"):
            problems.append("status must be emergency or city")
        if completed:
            problems.append("login checkpoint already has completed story events")
        if processing:
            problems.append("login checkpoint has a processing story event")
        if progress["sets"]["processingNewbees"]:
            problems.append("login checkpoint has a processing newbee")
        if progress["bools"]["patrol.rewardPending"]:
            problems.append("login checkpoint has a pending patrol reward")
        if 1000 not in available:
            problems.append("login checkpoint does not offer event 1000")
    else:
        problems.append(f"unknown milestone {milestone!r}")
    if problems:
        raise Refusal("MILESTONE_UNMET", "; ".join(problems))


def build_progress_block(profile: dict, progress: dict, consistency: dict) -> dict:
    return {
        "schema": progress["schema"],
        "commits": dict(progress["commits"]),
        "ints": dict(progress["ints"]),
        "bools": dict(progress["bools"]),
        "strings": dict(progress["strings"]),
        "counts": {
            "available_events": len(progress["sets"]["availableEvents"]),
            "completed_events": len(progress["sets"]["completedEvents"]),
            "processing_events": len(progress["sets"]["processingEvents"]),
            "processing_newbees": len(progress["sets"]["processingNewbees"]),
            "finished_newbees": len(progress["sets"]["finishedNewbees"]),
            "patrol_heroes": len(progress["sets"]["patrol.heroes"]),
            "patrol_events": len(progress["sets"]["patrol.events"]),
            "patrol_replays": len(progress["sets"]["patrol.replays"]),
            "event_completions": len(progress["event_completions"]),
            "event_days": len(progress["event_days"]),
            "conditions": len(progress["conditions"]),
            "patrol_fatigue": len(progress["patrol_fatigue"]),
            "patrol_friendly": len(progress["patrol_friendly"]),
            "patrol_bonus": len(progress["patrol_bonus"]),
        },
        "set_sha256": {
            name: sha256_hex(",".join(str(v) for v in progress["sets"][name]).encode("ascii"))
            for name in SET_FIELDS
        },
        "consistency": consistency,
    }


# ---------------------------------------------------------------------------
# account registry / identity binding
# ---------------------------------------------------------------------------


def account_record_digest(record: str) -> str:
    """StableIdentityBootstrap.accountFingerprint = sha256(record UTF-8)."""
    return sha256_hex(record.encode("utf-8"))


def read_registry(root: Path) -> tuple[dict[str, str], dict[str, int]]:
    accounts_path = root / "accounts.properties"
    ids_path = root / "account-ids.properties"
    for path in (accounts_path, ids_path):
        _check_absent_or_regular(path, "REGISTRY_INVALID")
    if not accounts_path.is_file():
        raise Refusal("REGISTRY_INVALID", f"missing {accounts_path}")
    if not ids_path.is_file():
        raise Refusal("REGISTRY_INVALID", f"missing {ids_path}")
    accounts = parse_java_properties(
        read_limited(accounts_path, REGISTRY_MAX_BYTES, "REGISTRY_INVALID"),
        "REGISTRY_INVALID",
    )
    ids_raw = parse_java_properties(
        read_limited(ids_path, REGISTRY_MAX_BYTES, "REGISTRY_INVALID"),
        "REGISTRY_INVALID",
    )
    ids: dict[str, int] = {}
    used: set[int] = set()
    for name, value in accounts.items():
        if not ACCOUNT_NAME_RE.match(name):
            raise Refusal("REGISTRY_INVALID", f"malformed account name {name!r}")
        if not value:
            raise Refusal("REGISTRY_INVALID", f"empty account record for {name!r}")
    for name, text in ids_raw.items():
        if not ACCOUNT_NAME_RE.match(name):
            raise Refusal("REGISTRY_INVALID", f"malformed account id name {name!r}")
        if not INT_RE.match(text or ""):
            raise Refusal("REGISTRY_INVALID", f"malformed numeric id for {name!r}")
        value = int(text)
        if value <= 0 or value == 2**31 - 1 or value in used:
            raise Refusal("REGISTRY_INVALID", f"invalid or duplicate numeric id {value}")
        used.add(value)
        ids[name] = value
    return accounts, ids


def read_identity(root: Path, require_ready: bool) -> dict | None:
    path = root / "p7-bootstrap" / "identity.properties"
    if path.exists():
        _check_absent_or_regular(path, "IDENTITY_INVALID")
    if not path.is_file():
        return None
    properties = parse_java_properties(
        read_limited(path, IDENTITY_MAX_BYTES, "IDENTITY_INVALID"),
        "IDENTITY_INVALID",
    )
    if properties.get("schema") != "1" or properties.get("backend") != "project7":
        raise Refusal("IDENTITY_SCHEMA", "identity journal schema/backend mismatch")
    account = properties.get("account", "")
    if not ACCOUNT_RE.match(account):
        raise Refusal("IDENTITY_SCHEMA", f"identity journal account is not offline_<24hex>: {account!r}")
    phase = properties.get("phase", "")
    step = properties.get("step", "")
    if phase not in ("PREPARING", "READY"):
        raise Refusal("IDENTITY_SCHEMA", f"invalid identity phase {phase!r}")
    if step not in ("IDENTITY_WRITTEN", "ACCOUNT_BOUND", "PROFILE_STARTED", "PROFILE_SAVED"):
        raise Refusal("IDENTITY_SCHEMA", f"invalid identity step {step!r}")
    if require_ready and (phase != "READY" or step != "PROFILE_SAVED"):
        raise Refusal(
            "IDENTITY_NOT_READY",
            f"identity journal phase/step is {phase}/{step}; a checkpoint requires READY/PROFILE_SAVED",
        )
    numeric_text = properties.get("numericId", "0")
    if not INT_RE.match(numeric_text or ""):
        raise Refusal("IDENTITY_SCHEMA", f"malformed identity numericId {numeric_text!r}")
    numeric_id = int(numeric_text)
    if step != "IDENTITY_WRITTEN" and numeric_id <= 0:
        raise Refusal("IDENTITY_SCHEMA", "bound identity journal has no numericId")
    record_hash = properties.get("accountRecordSha256")
    if record_hash is not None and not HEX64_RE.match(record_hash):
        raise Refusal("IDENTITY_SCHEMA", "identity accountRecordSha256 is not 64 hex")
    if phase == "READY" and (numeric_id <= 0 or record_hash is None):
        raise Refusal("IDENTITY_SCHEMA", "READY identity journal is missing its binding")
    manager_dex = properties.get("managerDex")
    if manager_dex is not None and not HEX64_RE.match(manager_dex):
        raise Refusal("IDENTITY_SCHEMA", "identity managerDex is not 64 hex")
    return {
        "schema": 1,
        "backend": "project7",
        "phase": phase,
        "step": step,
        "account": account,
        "numeric_id": numeric_id,
        "account_record_sha256": record_hash,
        "manager_dex": manager_dex,
        "post_profile_policy": properties.get("postProfilePolicy"),
    }


def bind_account(root: Path, account: str, require_ready_identity: bool) -> dict:
    if account in TEMPLATE_ACCOUNTS:
        raise Refusal(
            "TEMPLATE_ACCOUNT_REFUSED",
            f"{account!r} is a built-in template/manager account; refusing to copy it",
        )
    if not ACCOUNT_RE.match(account or ""):
        raise Refusal(
            "ACCOUNT_INVALID",
            "account must be the generated bootstrap form offline_<24 lowercase hex>",
        )
    accounts, ids = read_registry(root)
    if account not in accounts:
        raise Refusal("ACCOUNT_NOT_BOUND", f"{account!r} is not present in accounts.properties")
    if account not in ids:
        raise Refusal("ACCOUNT_NOT_BOUND", f"{account!r} is not present in account-ids.properties")
    record_digest = account_record_digest(accounts[account])
    numeric_id = ids[account]
    identity = read_identity(root, require_ready=require_ready_identity)
    if identity is not None:
        if identity["account"] != account:
            raise Refusal(
                "IDENTITY_MISMATCH",
                f"identity journal account={identity['account']!r} != {account!r}",
            )
        if identity["numeric_id"] != numeric_id:
            raise Refusal(
                "IDENTITY_MISMATCH",
                f"identity numericId={identity['numeric_id']} != account-ids={numeric_id}",
            )
        if identity["account_record_sha256"] != record_digest:
            raise Refusal(
                "IDENTITY_MISMATCH",
                "identity accountRecordSha256 does not match accounts.properties",
            )
    return {
        "name": account,
        "numeric_id": numeric_id,
        "record_sha256": record_digest,
        "identity": identity,
    }


def check_no_pending_or_temp(root: Path, account: str) -> None:
    journal_root = root / "save-transactions"
    if journal_root.is_dir():
        for entry in journal_root.iterdir():
            if entry.is_dir() and (entry / "pending.properties").is_file():
                raise Refusal(
                    "PENDING_SAVE_TRANSACTION",
                    f"unfinished import journal: {entry}",
                )
    for entry in root.glob(".p7-restore-*.journal"):
        raise Refusal("PENDING_RESTORE", f"unfinished restore journal: {entry}")
    for entry in root.glob(".p7-restore-backup-*"):
        raise Refusal("PENDING_RESTORE", f"unfinished restore backup: {entry}")
    for name in (
        "accounts.properties.tmp",
        "account-ids.properties.tmp",
        "p7-bootstrap/identity.properties.tmp",
        f"profiles/{account}.bson.tmp",
        f"tutorials/{account}.properties.tmp",
    ):
        path = root / name
        if path.exists():
            raise Refusal("STALE_TEMP_FILE", f"interrupted write left {path}")


# ---------------------------------------------------------------------------
# manifest build / verify
# ---------------------------------------------------------------------------


def _derive(profile_bytes: bytes, progress_bytes: bytes, account: str, numeric_id: int,
            milestone: str) -> dict:
    profile = inspect_profile(profile_bytes, account, numeric_id)
    progress = inspect_progress(progress_bytes)
    consistency = build_consistency(profile, progress)
    story = build_story_block(progress, milestone)
    enforce_milestone(story, profile, progress)
    story["digest"] = _story_digest({k: v for k, v in story.items() if k != "digest"})
    return {
        "profile": profile,
        "progress": build_progress_block(profile, progress, consistency),
        "story": story,
        "consistency": consistency,
    }


def _check_manifest_shape(manifest: dict, label: str) -> None:
    if not isinstance(manifest, dict):
        raise Refusal("MANIFEST_INVALID", "manifest is not a JSON object")
    expected = {
        "schema", "label", "created_utc", "milestone", "account",
        "files", "profile", "progress", "story", "consistency", "tool",
    }
    extra = set(manifest) - expected
    missing = expected - set(manifest)
    if extra or missing:
        raise Refusal(
            "MANIFEST_INVALID",
            f"manifest keys mismatch (extra={sorted(extra)}, missing={sorted(missing)})",
        )
    if manifest["schema"] != MANIFEST_SCHEMA:
        raise Refusal("MANIFEST_SCHEMA", f"unsupported manifest schema {manifest['schema']!r}")
    if manifest["label"] != label or not LABEL_RE.match(manifest["label"]):
        raise Refusal("MANIFEST_INVALID", "manifest label does not equal requested label")
    if not isinstance(manifest["created_utc"], str) or not UTC_RE.match(manifest["created_utc"]):
        raise Refusal("MANIFEST_INVALID", "created_utc is not YYYY-MM-DDTHH:MM:SSZ")
    if manifest["milestone"] not in MILESTONES:
        raise Refusal("MANIFEST_INVALID", f"unknown milestone {manifest['milestone']!r}")

    account = manifest["account"]
    if not isinstance(account, dict) or set(account) != {
        "name", "numeric_id", "record_sha256", "identity"
    }:
        raise Refusal("MANIFEST_INVALID", "account block has the wrong shape")
    if not ACCOUNT_RE.match(account["name"] or "") or account["name"] in TEMPLATE_ACCOUNTS:
        raise Refusal("MANIFEST_INVALID", "manifest account is not a generated offline account")
    if type(account["numeric_id"]) is not int or account["numeric_id"] <= 0:
        raise Refusal("MANIFEST_INVALID", "manifest numeric_id must be positive int")
    if not isinstance(account["record_sha256"], str) or not HEX64_RE.match(account["record_sha256"]):
        raise Refusal("MANIFEST_INVALID", "manifest record_sha256 is not 64 hex")
    identity = account["identity"]
    if identity is not None:
        if not isinstance(identity, dict) or set(identity) != {
            "schema", "backend", "phase", "step", "account", "numeric_id",
            "account_record_sha256", "manager_dex", "post_profile_policy",
        }:
            raise Refusal("MANIFEST_INVALID", "manifest identity block has the wrong shape")
        if identity["schema"] != 1 or identity["backend"] != "project7":
            raise Refusal("MANIFEST_INVALID", "manifest identity schema/backend is not 1/project7")
        if identity["account"] != account["name"]:
            raise Refusal("MANIFEST_INVALID", "manifest identity account mismatch")
        if identity["phase"] != "READY" or identity["step"] != "PROFILE_SAVED":
            raise Refusal("MANIFEST_INVALID", "manifest identity is not READY/PROFILE_SAVED")
        if identity["numeric_id"] != account["numeric_id"]:
            raise Refusal("MANIFEST_INVALID", "manifest identity numericId mismatch")
        if identity["account_record_sha256"] != account["record_sha256"]:
            raise Refusal("MANIFEST_INVALID", "manifest identity record hash mismatch")

    files = manifest["files"]
    if not isinstance(files, list) or len(files) != 2:
        raise Refusal("MANIFEST_INVALID", "manifest must list exactly profile+tutorial")
    roles = {}
    for entry in files:
        if not isinstance(entry, dict) or set(entry) != {"role", "path", "bytes", "sha256"}:
            raise Refusal("MANIFEST_INVALID", "file entry has the wrong shape")
        if entry["role"] not in ("profile", "tutorial") or entry["role"] in roles:
            raise Refusal("MANIFEST_INVALID", "duplicate or unknown file role")
        roles[entry["role"]] = entry
        if type(entry["bytes"]) is not int or entry["bytes"] <= 0:
            raise Refusal("MANIFEST_INVALID", "file size must be positive int")
        if not isinstance(entry["sha256"], str) or not HEX64_RE.match(entry["sha256"]):
            raise Refusal("MANIFEST_INVALID", "file sha256 is not 64 hex")
    name = account["name"]
    expected_paths = {
        "profile": f"files/profiles/{name}.bson",
        "tutorial": f"files/tutorials/{name}.properties",
    }
    for role, expected_path in expected_paths.items():
        if role not in roles or roles[role]["path"] != expected_path:
            raise Refusal("MANIFEST_INVALID", f"{role} path must be {expected_path}")

    if not isinstance(manifest["tool"], dict) or manifest["tool"].get("format") != TOOL_FORMAT:
        raise Refusal("MANIFEST_INVALID", "unsupported tool format")
    if set(manifest["tool"]) != {"format", "name"}:
        raise Refusal("MANIFEST_INVALID", "tool block has the wrong shape")
    for block in ("profile", "progress", "story", "consistency"):
        if type(manifest[block]) is not dict:
            raise Refusal("MANIFEST_INVALID", f"{block} block is not an object")
    if not isinstance(manifest["story"].get("digest"), str):
        raise Refusal("MANIFEST_INVALID", "story digest is missing")
    if not HEX64_RE.match(manifest["story"]["digest"]):
        raise Refusal("MANIFEST_INVALID", "story digest is not 64 hex")


def _load_manifest(checkpoint: Path, label: str) -> dict:
    path = checkpoint / "manifest.json"
    if not path.is_file() or path.is_symlink():
        raise Refusal("MANIFEST_MISSING", f"no manifest at {path}")
    try:
        manifest = json.loads(
            read_limited(path, MANIFEST_MAX_BYTES, "MANIFEST_INVALID").decode("utf-8")
        )
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise Refusal("MANIFEST_INVALID", f"cannot parse manifest: {error}") from None
    _check_manifest_shape(manifest, label)
    return manifest


def _load_checkpoint_files(checkpoint: Path, manifest: dict) -> tuple[bytes, bytes]:
    result = {}
    for entry in manifest["files"]:
        path = checkpoint / entry["path"]
        limit = PROFILE_MAX_BYTES if entry["role"] == "profile" else PROGRESS_MAX_BYTES
        data = read_limited(path, limit, "CHECKPOINT_FILE_INVALID")
        if len(data) != entry["bytes"]:
            raise Refusal(
                "MANIFEST_HASH_MISMATCH",
                f"{entry['path']} size {len(data)} != manifest {entry['bytes']}",
            )
        if sha256_hex(data) != entry["sha256"]:
            raise Refusal(
                "MANIFEST_HASH_MISMATCH",
                f"{entry['path']} sha256 does not match manifest",
            )
        result[entry["role"]] = data
    return result["profile"], result["tutorial"]


def _reject_extra_checkpoint_files(checkpoint: Path, manifest: dict) -> None:
    allowed = {"manifest.json"} | {entry["path"] for entry in manifest["files"]}
    for current, directories, filenames in os.walk(checkpoint):
        current_path = Path(current)
        if current_path.is_symlink():
            raise Refusal("CHECKPOINT_FILE_INVALID", f"symlink in checkpoint: {current_path}")
        for directory in list(directories):
            if (current_path / directory).is_symlink():
                raise Refusal(
                    "CHECKPOINT_FILE_INVALID",
                    f"symlink in checkpoint: {current_path / directory}",
                )
        for filename in filenames:
            relative = (current_path / filename).relative_to(checkpoint).as_posix()
            if relative not in allowed:
                raise Refusal(
                    "CHECKPOINT_FILE_EXTRA",
                    f"unexpected file in checkpoint: {relative}",
                )
    for relative in allowed:
        if (checkpoint / relative).is_symlink():
            raise Refusal("CHECKPOINT_FILE_INVALID", f"symlink: {relative}")


def verify_checkpoint(label: str, root: Path, binding: Path | None = None) -> dict:
    checkpoint = label_dir(root, label)
    if not checkpoint.is_dir():
        raise Refusal("CHECKPOINT_NOT_FOUND", f"no checkpoint at {checkpoint}")
    manifest = _load_manifest(checkpoint, label)
    _reject_extra_checkpoint_files(checkpoint, manifest)
    profile_bytes, progress_bytes = _load_checkpoint_files(checkpoint, manifest)
    account = manifest["account"]["name"]
    numeric_id = manifest["account"]["numeric_id"]
    derived = _derive(profile_bytes, progress_bytes, account, numeric_id, manifest["milestone"])

    if manifest["profile"] != derived["profile"]:
        raise Refusal("MANIFEST_PROFILE_MISMATCH", "profile metadata differs from checkpoint bytes")
    if manifest["progress"] != derived["progress"]:
        raise Refusal("MANIFEST_PROGRESS_MISMATCH", "Progress metadata differs from checkpoint bytes")
    if manifest["consistency"] != derived["consistency"]:
        raise Refusal("MANIFEST_CONSISTENCY_MISMATCH", "consistency block differs from checkpoint bytes")
    story = dict(derived["story"])
    digest = story.pop("digest")
    manifest_story = dict(manifest["story"])
    manifest_digest = manifest_story.pop("digest", None)
    if manifest_story != story:
        raise Refusal("MANIFEST_STORY_MISMATCH", "story block differs from checkpoint bytes")
    if manifest_digest != digest or not isinstance(manifest_digest, str):
        raise Refusal("MANIFEST_STORY_MISMATCH", "story digest does not match")

    binding_info = None
    if binding is not None:
        binding_root = resolve_files_root(binding)
        bound = bind_account(binding_root, account, require_ready_identity=False)
        if bound["record_sha256"] != manifest["account"]["record_sha256"]:
            raise Refusal(
                "BINDING_ACCOUNT_RECORD_MISMATCH",
                "binding accounts.properties record hash differs from checkpoint",
            )
        if bound["numeric_id"] != numeric_id:
            raise Refusal(
                "BINDING_NUMERIC_ID_MISMATCH",
                f"binding numeric id {bound['numeric_id']} != checkpoint {numeric_id}",
            )
        identity = manifest["account"]["identity"]
        if identity is not None and bound["identity"] is not None:
            if bound["identity"]["manager_dex"] != identity["manager_dex"]:
                binding_info = {"artifact_mismatch": True}
        binding_info = binding_info or {"artifact_mismatch": False}

    return {
        "label": label,
        "account": account,
        "numeric_id": numeric_id,
        "milestone": manifest["milestone"],
        "created_utc": manifest["created_utc"],
        "profile_sha256": [entry for entry in manifest["files"] if entry["role"] == "profile"][0]["sha256"],
        "tutorial_sha256": [entry for entry in manifest["files"] if entry["role"] == "tutorial"][0]["sha256"],
        "completed_events": len(story["completed_events"]),
        "finished_newbees": len(story["finished_newbees"]),
        "warnings": derived["consistency"]["warnings"],
        "binding": binding_info,
    }


# ---------------------------------------------------------------------------
# export / restore
# ---------------------------------------------------------------------------


def _file_signature(path: Path) -> tuple[int, int, int, int]:
    status = path.stat()
    return (status.st_dev, status.st_ino, status.st_size, status.st_mtime_ns)


def export_checkpoint(label: str, source: Path, account: str, root: Path,
                      milestone: str, replace: bool = False) -> dict:
    if milestone not in MILESTONES:
        raise Refusal("MILESTONE_INVALID", f"milestone must be one of {MILESTONES}")
    source_root = resolve_files_root(source)
    checkpoint = label_dir(root, label)
    if checkpoint.exists() and not replace:
        raise Refusal("CHECKPOINT_EXISTS", f"{checkpoint} already exists (use --replace)")
    if checkpoint.exists() and (checkpoint.is_symlink() or not checkpoint.is_dir()):
        raise Refusal("CHECKPOINT_EXISTS", f"{checkpoint} is not a plain directory")

    binding = bind_account(source_root, account, require_ready_identity=True)
    check_no_pending_or_temp(source_root, account)

    profile_path = source_root / "profiles" / f"{account}.bson"
    tutorial_path = source_root / "tutorials" / f"{account}.properties"
    if not profile_path.is_file():
        raise Refusal("PROFILE_MISSING", f"missing {profile_path}")
    if not tutorial_path.is_file():
        raise Refusal("TUTORIAL_MISSING", f"missing {tutorial_path}")
    before_profile = _file_signature(profile_path)
    before_tutorial = _file_signature(tutorial_path)
    profile_bytes = read_limited(profile_path, PROFILE_MAX_BYTES, "PROFILE_INVALID")
    tutorial_bytes = read_limited(tutorial_path, PROGRESS_MAX_BYTES, "TUTORIAL_INVALID")
    if _file_signature(profile_path) != before_profile or _file_signature(tutorial_path) != before_tutorial:
        raise Refusal("SOURCE_CHANGED_DURING_READ", "source files changed; stop the writer and retry")

    derived = _derive(
        profile_bytes, tutorial_bytes, account, binding["numeric_id"], milestone
    )

    manifest = {
        "schema": MANIFEST_SCHEMA,
        "label": label,
        "created_utc": utc_now(),
        "milestone": milestone,
        "account": binding,
        "files": [
            {
                "role": "profile",
                "path": f"files/profiles/{account}.bson",
                "bytes": len(profile_bytes),
                "sha256": sha256_hex(profile_bytes),
            },
            {
                "role": "tutorial",
                "path": f"files/tutorials/{account}.properties",
                "bytes": len(tutorial_bytes),
                "sha256": sha256_hex(tutorial_bytes),
            },
        ],
        "profile": derived["profile"],
        "progress": derived["progress"],
        "story": derived["story"],
        "consistency": derived["consistency"],
        "tool": {"format": TOOL_FORMAT, "name": "save_checkpoint.py"},
    }

    root.mkdir(parents=True, exist_ok=True)
    staging = root / f".staging-{label}-{os.getpid()}"
    if staging.exists():
        shutil.rmtree(staging)
    try:
        staging.mkdir(mode=0o700)
        (staging / "files").mkdir(mode=0o700)
        (staging / "files" / "profiles").mkdir(mode=0o700)
        (staging / "files" / "tutorials").mkdir(mode=0o700)
        _write_new(staging / "files" / "profiles" / f"{account}.bson", profile_bytes)
        _write_new(staging / "files" / "tutorials" / f"{account}.properties", tutorial_bytes)
        _write_new(
            staging / "manifest.json",
            json.dumps(manifest, indent=2, sort_keys=True).encode("utf-8") + b"\n",
        )
        _fsync_directory(staging)
        superseded = None
        if checkpoint.exists():
            superseded = root / f".superseded-{label}-{os.getpid()}"
            if superseded.exists():
                shutil.rmtree(superseded)
            os.replace(checkpoint, superseded)
        try:
            os.replace(staging, checkpoint)
        except OSError:
            if superseded is not None and not checkpoint.exists():
                os.replace(superseded, checkpoint)
            raise
        if superseded is not None:
            shutil.rmtree(superseded, ignore_errors=True)
        _fsync_directory(root)
    finally:
        if staging.exists():
            shutil.rmtree(staging, ignore_errors=True)

    return {
        "label": label,
        "path": str(checkpoint),
        "account": account,
        "numeric_id": binding["numeric_id"],
        "milestone": milestone,
        "profile_sha256": manifest["files"][0]["sha256"],
        "tutorial_sha256": manifest["files"][1]["sha256"],
        "completed_events": derived["story"]["completed_events"],
        "warnings": derived["consistency"]["warnings"],
    }


def _write_new(path: Path, data: bytes) -> None:
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    descriptor = os.open(path, flags, 0o600)
    try:
        view = memoryview(data)
        while view:
            written = os.write(descriptor, view)
            if written <= 0:
                raise OSError("short write")
            view = view[written:]
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def _fsync_directory(path: Path) -> None:
    try:
        descriptor = os.open(path, os.O_RDONLY)
    except OSError:
        return
    try:
        os.fsync(descriptor)
    except OSError:
        pass
    finally:
        os.close(descriptor)


def restore_checkpoint(label: str, target: Path, root: Path, dry_run: bool = False) -> dict:
    report = verify_checkpoint(label, root)
    checkpoint = label_dir(root, label)
    manifest = _load_manifest(checkpoint, label)
    account = manifest["account"]["name"]
    numeric_id = manifest["account"]["numeric_id"]

    _assert_local_target(target)
    target_root = resolve_files_root(target)
    # Do not follow a symlinked root into a device tree.
    _assert_local_target(target_root)

    bound = bind_account(target_root, account, require_ready_identity=False)
    if bound["record_sha256"] != manifest["account"]["record_sha256"]:
        raise Refusal(
            "TARGET_ACCOUNT_RECORD_MISMATCH",
            "target accounts.properties record hash differs from the checkpoint binding",
        )
    if bound["numeric_id"] != numeric_id:
        raise Refusal(
            "TARGET_NUMERIC_ID_MISMATCH",
            f"target numeric id {bound['numeric_id']} != checkpoint {numeric_id}",
        )
    identity = manifest["account"]["identity"]
    artifact_mismatch = False
    if identity is not None and bound["identity"] is not None:
        artifact_mismatch = (
            bound["identity"]["manager_dex"] != identity["manager_dex"]
            or bound["identity"]["post_profile_policy"] != identity["post_profile_policy"]
        )
        if artifact_mismatch:
            report["warnings"].append("artifact_mismatch")

    check_no_pending_or_temp(target_root, account)

    profile_destination = target_root / "profiles" / f"{account}.bson"
    tutorial_destination = target_root / "tutorials" / f"{account}.properties"
    if tutorial_destination.exists() and not profile_destination.exists():
        raise Refusal(
            "TARGET_PROGRESS_WITHOUT_PROFILE",
            "target has a tutorial file but no profile; refusing to fabricate a profile",
        )
    if profile_destination.exists():
        existing = read_limited(profile_destination, PROFILE_MAX_BYTES, "TARGET_PROFILE_UNREADABLE")
        try:
            existing_document = bson_decode(existing)
        except BSONError as error:
            raise Refusal(
                "TARGET_PROFILE_UNREADABLE",
                f"cannot identify the existing target profile: {error}",
            ) from None
        existing_account = existing_document.get("account")
        existing_uid = existing_document.get("uid")
        if existing_account != account or existing_uid != numeric_id:
            raise Refusal(
                "TARGET_PROFILE_ACCOUNT_MISMATCH",
                "existing target profile belongs to a different account/numeric id",
            )

    profile_bytes = (checkpoint / "files" / "profiles" / f"{account}.bson").read_bytes()
    tutorial_bytes = (checkpoint / "files" / "tutorials" / f"{account}.properties").read_bytes()

    plan = {
        "label": label,
        "account": account,
        "numeric_id": numeric_id,
        "target": str(target_root),
        "profile_destination": str(profile_destination),
        "tutorial_destination": str(tutorial_destination),
        "profile_sha256": sha256_hex(profile_bytes),
        "tutorial_sha256": sha256_hex(tutorial_bytes),
        "dry_run": dry_run,
        "warnings": report["warnings"],
    }
    if dry_run:
        return plan

    profile_destination.parent.mkdir(parents=True, exist_ok=True)
    tutorial_destination.parent.mkdir(parents=True, exist_ok=True)
    transaction_id = hashlib.sha256((account + ":" + label).encode("utf-8")).hexdigest()[:16]
    journal = target_root / f".p7-restore-{transaction_id}.journal"
    backup_dir = target_root / f".p7-restore-backup-{transaction_id}"
    profile_temp = profile_destination.parent / f".p7-restore-{transaction_id}.tmp"
    tutorial_temp = tutorial_destination.parent / f".p7-restore-{transaction_id}.tmp"
    for temp in (profile_temp, tutorial_temp):
        if temp.exists():
            temp.unlink()
    if journal.exists() or backup_dir.exists():
        raise Refusal("PENDING_RESTORE", "restore transaction marker already exists")

    profile_existed = profile_destination.exists()
    tutorial_existed = tutorial_destination.exists()
    profile_backup = backup_dir / "profile.bson"
    tutorial_backup = backup_dir / "progress.properties"
    backup_dir.mkdir(parents=True, exist_ok=False)
    try:
        if profile_existed:
            _write_new(profile_backup, profile_destination.read_bytes())
        if tutorial_existed:
            _write_new(tutorial_backup, tutorial_destination.read_bytes())
        _write_new(journal, json.dumps({
            "schema": "project7-restore-transaction/v1",
            "account": account,
            "label": label,
            "phase": "prepared",
            "profile": {"destination": str(profile_destination), "existed": profile_existed, "backup": str(profile_backup)},
            "tutorial": {"destination": str(tutorial_destination), "existed": tutorial_existed, "backup": str(tutorial_backup)},
        }, sort_keys=True).encode("ascii"))
        _fsync_directory(target_root)
    except OSError as error:
        raise Refusal("RESTORE_IO_FAILED", str(error)) from None

    try:
        _write_new(profile_temp, profile_bytes)
        _write_new(tutorial_temp, tutorial_bytes)
        _fsync_directory(profile_destination.parent)
        _fsync_directory(tutorial_destination.parent)
        os.replace(profile_temp, profile_destination)
        os.replace(tutorial_temp, tutorial_destination)
        _fsync_directory(profile_destination.parent)
        _fsync_directory(tutorial_destination.parent)
    except OSError as error:
        # Keep the marker and backups if rollback itself cannot complete: the
        # target is then explicitly recognizable as mixed and future restores refuse.
        try:
            if profile_existed:
                os.replace(profile_backup, profile_destination)
            elif profile_destination.exists():
                profile_destination.unlink()
            if tutorial_existed:
                os.replace(tutorial_backup, tutorial_destination)
            elif tutorial_destination.exists():
                tutorial_destination.unlink()
            _fsync_directory(profile_destination.parent)
            _fsync_directory(tutorial_destination.parent)
            journal.unlink(missing_ok=True)
            shutil.rmtree(backup_dir, ignore_errors=True)
            for temp in (profile_temp, tutorial_temp):
                temp.unlink(missing_ok=True)
            raise Refusal("RESTORE_IO_ROLLED_BACK", str(error)) from None
        except OSError as rollback_error:
            raise Refusal("RESTORE_MIXED", f"{error}; rollback failed: {rollback_error}") from None

    journal.unlink(missing_ok=True)
    shutil.rmtree(backup_dir, ignore_errors=True)
    for temp in (profile_temp, tutorial_temp):
        temp.unlink(missing_ok=True)

    restored_profile = profile_destination.read_bytes()
    restored_tutorial = tutorial_destination.read_bytes()
    if sha256_hex(restored_profile) != plan["profile_sha256"]:
        raise Refusal("RESTORE_READBACK_MISMATCH", "profile read-back hash differs")
    if sha256_hex(restored_tutorial) != plan["tutorial_sha256"]:
        raise Refusal("RESTORE_READBACK_MISMATCH", "tutorial read-back hash differs")
    post = _derive(restored_profile, restored_tutorial, account, numeric_id, manifest["milestone"])
    if post["story"] != manifest["story"]:
        raise Refusal("RESTORE_READBACK_MISMATCH", "restored story block differs from manifest")
    return plan


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def _default_root() -> Path:
    return ROOT / "local-checkpoints" / "store"


def _emit(payload: dict, as_json: bool) -> None:
    if as_json:
        print(json.dumps(payload, indent=2, sort_keys=True))
        return
    for key, value in payload.items():
        if isinstance(value, list):
            value = ", ".join(str(item) for item in value) if value else "(none)"
        print(f"{key}: {value}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Export/verify/restore a private Project7 single-APK save checkpoint.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    export = subparsers.add_parser("export", help="write a checkpoint from a files directory")
    export.add_argument("label")
    export.add_argument("--from", dest="source", required=True, type=Path)
    export.add_argument("--account", required=True)
    export.add_argument("--milestone", default="hospital-menu-v1", choices=MILESTONES)
    export.add_argument("--root", type=Path, default=_default_root())
    export.add_argument("--replace", action="store_true")
    export.add_argument("--json", action="store_true")

    verify = subparsers.add_parser("verify", help="re-hash and re-derive a checkpoint")
    verify.add_argument("label")
    verify.add_argument("--root", type=Path, default=_default_root())
    verify.add_argument("--binding", type=Path)
    verify.add_argument("--json", action="store_true")

    restore = subparsers.add_parser("restore", help="restore a checkpoint into a files directory")
    restore.add_argument("label")
    restore.add_argument("--to", dest="target", required=True, type=Path)
    restore.add_argument("--root", type=Path, default=_default_root())
    restore.add_argument("--dry-run", action="store_true")
    restore.add_argument("--json", action="store_true")

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    arguments = parser.parse_args(argv)
    try:
        if arguments.command == "export":
            payload = export_checkpoint(
                arguments.label,
                arguments.source,
                arguments.account,
                arguments.root,
                arguments.milestone,
                replace=arguments.replace,
            )
        elif arguments.command == "verify":
            payload = verify_checkpoint(arguments.label, arguments.root, arguments.binding)
        else:
            payload = restore_checkpoint(
                arguments.label,
                arguments.target,
                arguments.root,
                dry_run=arguments.dry_run,
            )
    except Refusal as refusal:
        print(f"REFUSED {refusal.code}: {refusal.detail}", file=sys.stderr)
        return 3
    _emit(payload, arguments.json)
    return 0


if __name__ == "__main__":
    sys.exit(main())
