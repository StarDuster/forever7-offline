"""Run the v55 mainline entry-closure host on the published v55 production classes.

No D8/APK/device/native. Temp dirs are deleted; only a compact evidence JSON is kept.
Legacy v54 host counts are carried as historical evidence, not rerun here.
"""
from pathlib import Path
import argparse, hashlib, json, re, shutil, subprocess, tempfile

R = Path(__file__).resolve().parents[2]
H = Path(__file__).resolve().parent
BASE = R / "analysis/project7/story-city-integration-prepare-v55/project7-inputs-n08vxood"
OWN = BASE / "compiled/production-classes"
ASSETS = BASE / "stage/assets"
ENTRY = R / "runtime/android_story_shared/catalog/mainline32-entry-v1.json"
MANAGER = R / "analysis/project7/action-ledger-code20-v2/manager-translated-frames.jar"
J = R / "toolchains/java/jdk-17.0.21+9/Contents/Home/bin"
SDK = R / "toolchains/android-sdk/platforms/android-32/android.jar"
JSON = R / "toolchains/json-20240303.jar"
BAIYE = [
    "-Dp7.baiye.catalog=" + str(R / "runtime/project7_baiye_catalog/catalog-v1.tsv"),
    "-Dp7.baiye.fragments=" + str(R / "runtime/project7_baiye_catalog/fragments-v1.tsv"),
    "-Dp7.baiye.shop=" + str(R / "runtime/project7_baiye_shop_catalog/catalog-v1.tsv"),
]


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def run(*args):
    proc = subprocess.run(list(map(str, args)), capture_output=True, text=True)
    if proc.returncode != 0:
        raise SystemExit(proc.stdout + proc.stderr)
    return proc.stdout + proc.stderr


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--evidence", type=Path,
                        default=R / "reports/mainline32-capability-host-v55.json")
    args = parser.parse_args()
    temp = Path(tempfile.mkdtemp(prefix="mainline-entry-closure-", dir="/tmp"))
    try:
        for name in ("platform", "tests"):
            (temp / name).mkdir()
        run(J / "javac", "--release", "8", "-d", temp / "platform",
            *[x for x in R.glob("runtime/android_core_rpc/host_stubs/**/*.java")
              if x.name not in ("AssetManager.java", "Os.java")],
            *R.glob("runtime/android_baiye_transactions/host_tests/android/**/*.java"),
            R / "runtime/android_week_reset/host_tests/android/system/Os.java")
        cp = ":".join(map(str, [temp / "platform", OWN, MANAGER, JSON]))
        run(J / "javac", "--release", "8", "-cp", cp, "-d", temp / "tests",
            H / "host_tests/com/project7/localmanager/StoryMainlineEntryClosureHost.java")
        output = run(J / "java", "-Xverify:all", *BAIYE,
                     "-cp", ":".join(map(str, [temp / "platform", temp / "tests",
                                               OWN, MANAGER, JSON])),
                     "com.project7.localmanager.StoryMainlineEntryClosureHost",
                     ASSETS, ASSETS)
        checks = int(re.search(r"^PASS (\d+)", output, re.M).group(1))
        if checks < 400:
            raise SystemExit("unexpected entry closure check count: %d" % checks)
        report = {
            "schema": "project7-mainline32-capability-host-v55",
            "status": "PASS",
            "checks": checks,
            "host": "com.project7.localmanager.StoryMainlineEntryClosureHost",
            "menus": [12, 19, 22, 25],
            "assets": str(ASSETS.relative_to(R)),
            "production_classes": str(OWN.relative_to(R)),
            "published_entry_asset": sha(ASSETS / "project7_story_shared/mainline32-entry-v1.json"),
            "entry_asset_sha256": sha(ENTRY),
            "manager_sha256": sha(MANAGER),
            "story_mainline_entry": sha(R / "runtime/android_story_shared/src/com/project7/localmanager/StoryMainlineEntry.java"),
            "story_city_policy": sha(R / "runtime/android_story_city/src/com/project7/localmanager/StoryCityPolicy.java"),
            "story_mission_bridge": sha(R / "runtime/android_story_missions/src/com/project7/localmanager/StoryMissionBridge.java"),
            "host_sha256": sha(H / "host_tests/com/project7/localmanager/StoryMainlineEntryClosureHost.java"),
            "legacy_v54": {"capability": 164, "mainline32": 110,
                           "data_closed": 1802, "default_chapter": 1345},
            "binding_note": "v55 published prepare; host runs on stage assets with no overlay",
            "no_d8_apk_native": True,
            "temp_cleanup": str(temp) + " removed",
            "output_tail": output.strip().splitlines()[-1],
        }
        args.evidence.write_text(json.dumps(report, ensure_ascii=False, indent=1) + "\n")
        print("PASS entry_closure=%d" % checks)
    finally:
        shutil.rmtree(temp, ignore_errors=True)


if __name__ == "__main__":
    main()
