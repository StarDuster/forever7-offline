"""Reproduce the v43 auto-trigger candidate host on frozen production classes.

No D8/APK/device/native and no prepare run: the host merges the append-only
candidate asset with the frozen event_graph.tsv in memory.  Temp dirs are
deleted; only a compact evidence JSON is kept.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

R = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
BASE = R / "analysis/project7/story-city-integration-prepare-v43/project7-inputs-6i2v7gq2"
ASSETS = BASE / "stage/assets"
CLASSES = BASE / "compiled/production-classes"
MANAGER = R / "analysis/project7/story-city-coc-gateway-v36/manager-translated-frames.jar"
J = R / "toolchains/java/jdk-17.0.21+9/Contents/Home/bin"
SDK = R / "toolchains/android-sdk/platforms/android-32/android.jar"
JSON = R / "toolchains/json-20240303.jar"
CANDIDATE = R / "runtime/project7_event_auto_trigger_candidate"
TOOL = R / "tools/project7_event_auto_trigger_candidate.py"
EVIDENCE = R / "reports/auto-trigger-host-v43.json"
PINS = {
    "event_graph": "50d211e2108524dbce10e9babf9de77cf9faf9e331f8a70f8d1a8f6d771f927f",
    "weeks": "dbb0a5d64492e18243a332c93c4a855f5572661922bd26b870b48a96b8ffaa55",
    "manager": "a767c656b853d40d2e8acac835eac19ec2272da8cbee112a7428637d539bbc66",
}


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def run(*args):
    proc = subprocess.run(list(map(str, args)), capture_output=True, text=True, cwd=R)
    if proc.returncode != 0:
        raise SystemExit(proc.stdout + proc.stderr)
    return proc.stdout + proc.stderr


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--evidence", type=Path, default=EVIDENCE)
    args = parser.parse_args()

    contract = json.loads((CANDIDATE / "contract-v1.json").read_text(encoding="utf-8"))
    asset = CANDIDATE / "trigger-extra-v1.tsv"
    if sha(asset) != contract["asset_sha256"]:
        raise SystemExit("candidate asset hash mismatch")
    for name, path in (("event_graph", ASSETS / "event_graph.tsv"),
                       ("weeks", ASSETS / "weeks.tsv"),
                       ("manager", MANAGER)):
        if sha(path) != PINS[name]:
            raise SystemExit("pin mismatch: " + name)

    check_output = run(sys.executable, TOOL, "--check")
    if "PASS" not in check_output:
        raise SystemExit(check_output)

    temp = Path(tempfile.mkdtemp(prefix="auto-trigger-host-", dir="/tmp"))
    try:
        (temp / "tests").mkdir()
        (temp / "assets").mkdir()
        for name in ("event_graph.tsv", "new_player.bson", "weeks.tsv"):
            shutil.copy(ASSETS / name, temp / "assets" / name)
        compile_cp = ":".join(map(str, [SDK, MANAGER, CLASSES, JSON]))
        run(J / "javac", "--release", "8", "-cp", compile_cp, "-d", temp / "tests",
            *HERE.glob("host_tests/com/**/*.java"))
        runtime_cp = ":".join(map(str, [temp / "tests", MANAGER, CLASSES, JSON, SDK]))
        output = run(J / "java", "-Xverify:all", "-cp", runtime_cp,
                     "com.project7.localmanager.AutoTriggerMechanismHost",
                     temp / "assets", asset, CANDIDATE / "contract-v1.json")
        checks = int(re.search(r"^PASS (\d+)", output, re.M).group(1))
        evidence = {
            "schema": "project7-auto-trigger-host-v43",
            "status": "PASS",
            "checks": checks,
            "candidate_asset": str(asset.relative_to(R)),
            "candidate_sha256": sha(asset),
            "candidate_rows": contract["counts"]["candidate_rows"],
            "frozen_trigger_rows": contract["counts"]["frozen_trigger_rows"],
            "fallback_events": contract["counts"]["fallback_events"],
            "blocked_events": contract["counts"]["blocked_events"],
            "assets": str(ASSETS.relative_to(R)),
            "production_classes": str(CLASSES.relative_to(R)),
            "manager": str(MANAGER.relative_to(R)),
            "hashes": {"event_graph": PINS["event_graph"], "weeks": PINS["weeks"],
                       "manager": PINS["manager"],
                       "contract": sha(CANDIDATE / "contract-v1.json")},
            "command": " ".join([
                "python3 runtime/android_event_auto_trigger/verify.py",
            ]),
            "javac": "javac --release 8 -cp android.jar:manager.jar:production-classes:json host_tests/com/**/*.java",
            "java": "java -Xverify:all -cp tests:manager.jar:production-classes:json:android.jar "
                    "com.project7.localmanager.AutoTriggerMechanismHost <temp>/assets "
                    "runtime/project7_event_auto_trigger_candidate/trigger-extra-v1.tsv "
                    "runtime/project7_event_auto_trigger_candidate/contract-v1.json",
            "cases": [
                "%d candidate rows: frozen catalog absent, auto+release, merged catalog parsed" % contract["counts"]["candidate_rows"],
                "3490 frozen @trigger rows field-identical after append-only merge",
                "Unproven entry events remain rowless; route effects and successor edges alone do not establish a fallback",
                "%d blocked events keep no row; release/condition-code reasons asserted" % contract["counts"]["blocked_events"],
                "previously absent 1393: original engine cannot expose, merged 1393 matches/unblocked/available",
                "1393 negative: day 1, route 1, client operation 0 all blocked",
                "1323 fallback: week entrance row is 1323 and the engine supplies it with no trigger row",
            ],
            "no_prepare_no_d8_no_apk_no_native": True,
            "temp_cleanup": str(temp) + " removed",
            "output": output.strip(),
        }
        args.evidence.write_text(json.dumps(evidence, ensure_ascii=False, indent=1) + "\n")
        print(output.strip())
        print("PASS evidence=" + str(args.evidence.resolve()))
    finally:
        shutil.rmtree(temp, ignore_errors=True)


if __name__ == "__main__":
    main()
