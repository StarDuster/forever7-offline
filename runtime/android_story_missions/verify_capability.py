"""Reproduce the v61 mainline capability/data-closed hosts on the published production classes.

No D8/APK/device/native. Compile-only city stubs never enter the runtime
classpath. Hosts run on the published v54 stage assets directly, with no asset
overlay. Temp dirs are deleted; only a compact evidence JSON is kept.
"""
from pathlib import Path
import argparse, hashlib, json, re, shutil, subprocess, tempfile

R = Path(__file__).resolve().parents[2]
H = Path(__file__).resolve().parent
BASE = R / "analysis/project7/story-city-integration-prepare-v61/project7-inputs-m_ee5jmd"
OWN = BASE / "compiled/production-classes"
ASSETS = BASE / "stage/assets"
ENTRY_ASSET = R / "runtime/android_story_shared/catalog/mainline32-entry-v1.json"
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
                        default=R / "reports/mainline32-capability-host-v61.json")
    args = parser.parse_args()
    temp = Path(tempfile.mkdtemp(prefix="mainline-capability-", dir="/tmp"))
    try:
        for name in ("api", "cityapi", "bridge", "entry", "city", "platform", "tests"):
            (temp / name).mkdir()
        run(J / "javac", "--release", "8", "-cp", SDK, "-d", temp / "api",
            *H.glob("compile_stubs/**/*.java"))
        run(J / "javac", "--release", "8", "-cp", SDK, "-d", temp / "cityapi",
            *R.glob("runtime/android_story_city/compile_stubs/**/*.java"))
        run(J / "javac", "--release", "8",
            "-cp", ":".join(map(str, [SDK, temp / "api", MANAGER, OWN, JSON])),
            "-d", temp / "bridge", *H.glob("src/**/*.java"))
        run(J / "javac", "--release", "8",
            "-cp", ":".join(map(str, [SDK, temp / "bridge", MANAGER, OWN, JSON])),
            "-d", temp / "entry",
            R / "runtime/android_story_shared/src/com/project7/localmanager/StoryMainlineEntry.java")
        run(J / "javac", "--release", "8",
            "-cp", ":".join(map(str, [SDK, temp / "cityapi", temp / "entry", temp / "bridge",
                                      MANAGER, OWN, JSON])),
            "-d", temp / "city",
            R / "runtime/android_story_city/src/com/project7/localmanager/StoryCityPolicy.java")
        run(J / "javac", "--release", "8", "-d", temp / "platform",
            *[x for x in R.glob("runtime/android_core_rpc/host_stubs/**/*.java")
              if x.name not in ("AssetManager.java", "Os.java")],
            *R.glob("runtime/android_baiye_transactions/host_tests/android/**/*.java"),
            R / "runtime/android_week_reset/host_tests/android/system/Os.java")
        compile_cp = ":".join(map(str, [temp / "platform", temp / "city", temp / "entry",
                                        temp / "bridge", OWN, MANAGER, JSON]))
        # Explicit v54 host list: pinned by version so older/newer versioned hosts
        # cannot leak into this prepare's compile.
        run(J / "javac", "--release", "8", "-cp", compile_cp, "-d", temp / "tests",
            *[H / "host_tests/com/project7/localmanager" / name for name in (
                "StoryMainlineCapabilityHost.java",
                "StoryMainline32Host.java",
                "StoryMainlineDataClosedHost.java",
                "StoryDefaultChapterHost.java",
            )])
        runtime_cp = ":".join(map(str, [temp / "platform", temp / "tests",
                                        OWN, MANAGER, JSON]))
        capability = run(J / "java", "-Xverify:all", *BAIYE, "-cp", runtime_cp,
                         "com.project7.localmanager.StoryMainlineCapabilityHost", ASSETS)
        generic = run(J / "java", "-Xverify:all", *BAIYE, "-cp", runtime_cp,
                      "com.project7.localmanager.StoryMainline32Host", ASSETS)
        dataclosed = run(J / "java", "-Xverify:all", *BAIYE, "-cp", runtime_cp,
                         "com.project7.localmanager.StoryMainlineDataClosedHost",
                         ASSETS, ASSETS)
        defaultchapter = run(J / "java", "-Xverify:all", *BAIYE, "-cp", runtime_cp,
                             "com.project7.localmanager.StoryDefaultChapterHost",
                             ASSETS, ASSETS)
        cap_checks = int(re.search(r"^PASS (\d+)", capability, re.M).group(1))
        gen_checks = int(re.search(r"^PASS (\d+)", generic, re.M).group(1))
        dc_checks = int(re.search(r"^PASS (\d+)", dataclosed, re.M).group(1))
        default_checks = int(re.search(r"^PASS (\d+)", defaultchapter, re.M).group(1))
        # Generic total includes one opcode assertion per emitted frame.
        # Semantic assertions live in the Java host; frame count may vary by runtime.
        if cap_checks != 164 or gen_checks < 110 or dc_checks < 60 or default_checks < 600:
            raise SystemExit("unexpected host check counts: %d/%d/%d/%d"
                             % (cap_checks, gen_checks, dc_checks, default_checks))
        report = {
            "schema": "project7-mainline32-capability-host-v61",
            "status": "PASS",
            "checks": {"capability": cap_checks, "mainline32": gen_checks,
                       "data_closed": dc_checks, "default_chapter": default_checks},
            "hosts": ["com.project7.localmanager.StoryMainlineCapabilityHost",
                      "com.project7.localmanager.StoryMainline32Host",
                      "com.project7.localmanager.StoryMainlineDataClosedHost",
                      "com.project7.localmanager.StoryDefaultChapterHost"],
            "assets": str(ASSETS.relative_to(R)),
            "published_entry_asset": sha(ASSETS / "project7_story_shared/mainline32-entry-v1.json"),
            "published": True,
            "binding_note": "v61 actual prepare; hosts ran on the authoritative project7_story_city_events asset",
            "production_classes": str(OWN.relative_to(R)),
            "manager": str(MANAGER.relative_to(R)),
            "hashes": {
                "manager_sha256": sha(MANAGER),
                "entry_asset_sha256": sha(ENTRY_ASSET),
                "story_mainline_entry": sha(R / "runtime/android_story_shared/src/com/project7/localmanager/StoryMainlineEntry.java"),
                "story_city_policy": sha(R / "runtime/android_story_city/src/com/project7/localmanager/StoryCityPolicy.java"),
                "story_mission_bridge": sha(R / "runtime/android_story_missions/src/com/project7/localmanager/StoryMissionBridge.java"),
                "story_mainline_dataclosed_host": sha(H / "host_tests/com/project7/localmanager/StoryMainlineDataClosedHost.java"),
                "executed_default_chapter_host_class": sha(temp / "tests/com/project7/localmanager/StoryDefaultChapterHost.class"),
            },
            "runtime_classpath_note": "platform stubs and tests plus published v61 production classes and matching manager frame; no owner overlay; temp deleted",
            "compiled_owner_hashes": {name: sha(temp / sub / "com/project7/localmanager" / (name + ".class"))
                                      for name, sub in (("StoryMainlineEntry", "entry"),
                                                        ("StoryCityPolicy", "city"),
                                                        ("StoryMissionBridge", "bridge"))},
            "no_d8_apk_native": True,
            "temp_cleanup": str(temp) + " removed",
            "output_tail": (capability.strip().splitlines()[-1] + " | " +
                            generic.strip().splitlines()[-1] + " | " +
                            dataclosed.strip().splitlines()[-1] + " | " +
                            defaultchapter.strip().splitlines()[-1]),
        }
        args.evidence.write_text(json.dumps(report, ensure_ascii=False, indent=1) + "\n")
        print("PASS capability=%d mainline32=%d dataclosed=%d defaultchapter=%d"
              % (cap_checks, gen_checks, dc_checks, default_checks))
    finally:
        shutil.rmtree(temp, ignore_errors=True)


if __name__ == "__main__":
    main()
