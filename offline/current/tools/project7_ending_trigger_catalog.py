"""Regenerate the ending-trigger rule asset from the pinned original table.

Writer:  python3 tools/project7_ending_trigger_catalog.py --write
Checker: python3 tools/project7_ending_trigger_catalog.py --check

The source is the original 640 ``mainline_week_info`` literal table, decoded by
the same restricted literal reader used by the other Project7 catalogs.  Only
row/literal values are projected; no game code is executed.  The output stays a
byte-for-byte source of truth for ``assets/offline/ending-trigger-v1.json``.
"""
from __future__ import annotations
import _bootstrap  # noqa: E402,F401

import argparse
from collections import OrderedDict
import hashlib
import json
from pathlib import Path
import sys

from _bootstrap import ROOT
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from project7_dream_catalog.produce import literal  # literal-only marshal reader

SOURCE = ROOT / "analysis/android640-scripts/com/data/cdata/mainline_week_info.marshal"
SOURCE_SHA256 = "4a14531712d43d9b006c716a6364fbec0620f2b765ceb3a68505f8db4540b844"
OUTPUT = ROOT / "offline/current/data/project7_request_events/ending-trigger-v1.json"
SCHEMA = "project7-ending-trigger-v1"
POLICY = "open-new-enter-failed-rule-v1"
EXPECTED_OUTPUT_SHA256 = "1792a804aba72c806a7bb73dce3a42baf52695ff0edc5b476fbbe05c89095431"


def normalise_requires(value):
    if value == "":
        return []
    if not isinstance(value, (tuple, list)):
        raise ValueError("Invalid mainline_week_info requires")
    result = []
    for group in value:
        if not isinstance(group, (tuple, list)) or not group:
            raise ValueError("Invalid mainline_week_info requirement group")
        ids = []
        for entry in group:
            if type(entry) is not int or entry <= 0 or entry > 0x7fffffff:
                raise ValueError("Invalid mainline_week_info ending id")
            ids.append(entry)
        result.append(ids)
    return result


def normalise_row(row):
    if not isinstance(row, dict):
        raise ValueError("Invalid mainline_week_info rule")
    allowed = {"requires", "true_client_event", "false_client_event", "false_event", "open_chapters"}
    unseen = set(row) - allowed
    if unseen:
        raise ValueError("Unknown mainline_week_info rule fields: %r" % sorted(unseen))
    values = {}
    for name in ("true_client_event", "false_client_event", "false_event"):
        value = row.get(name, 0)
        if type(value) is not int or value < 0 or value > 0x7fffffff:
            raise ValueError("Invalid mainline_week_info %s" % name)
        values[name] = value
    chapters = row.get("open_chapters", ())
    if not isinstance(chapters, (tuple, list)):
        raise ValueError("Invalid mainline_week_info open_chapters")
    chapters = [entry for entry in chapters]
    if any(type(entry) is not int or entry <= 0 or entry > 0x7fffffff for entry in chapters):
        raise ValueError("Invalid mainline_week_info chapter id")
    return OrderedDict((
        ("requires", normalise_requires(row.get("requires", ""))),
        ("true_client_event", values["true_client_event"]),
        ("false_client_event", values["false_client_event"]),
        ("false_event", values["false_event"]),
        ("open_chapters", chapters),
    ))


def build():
    data = literal(SOURCE)
    if not isinstance(data, dict) or not data:
        raise ValueError("mainline_week_info is empty")
    weeks = OrderedDict()
    for key in sorted(data):
        if type(key) is not int or key <= 0:
            raise ValueError("Invalid mainline_week_info week key")
        entry = data[key]
        if not isinstance(entry, dict) or entry.get("id") != key:
            raise ValueError("mainline_week_info id mismatch")
        rows = entry.get("value")
        if not isinstance(rows, (tuple, list)) or not rows:
            raise ValueError("mainline_week_info rule list missing")
        weeks[str(key)] = [normalise_row(row) for row in rows]
    document = OrderedDict((
        ("schema", SCHEMA),
        ("policy", POLICY),
        ("source", OrderedDict((
            ("table", "mainline_week_info"),
            ("sha256", SOURCE_SHA256),
        ))),
        ("weeks", weeks),
    ))
    return (json.dumps(document, ensure_ascii=True, sort_keys=True, separators=(",", ":")) + "\n").encode("ascii")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--write", action="store_true")
    group.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if hashlib.sha256(SOURCE.read_bytes()).hexdigest() != SOURCE_SHA256:
        raise SystemExit("Original mainline_week_info source changed")
    output = build()
    digest = hashlib.sha256(output).hexdigest()
    if args.write:
        OUTPUT.parent.mkdir(parents=True, exist_ok=True)
        OUTPUT.write_bytes(output)
        print("sha256=%s" % digest)
        return
    if not OUTPUT.is_file() or OUTPUT.read_bytes() != output:
        raise SystemExit("Ending-trigger catalog differs from the pinned source")
    if digest != EXPECTED_OUTPUT_SHA256:
        raise SystemExit("Ending-trigger catalog hash pin mismatch")
    print("PASS sha256=%s" % digest)


if __name__ == "__main__":
    main()
