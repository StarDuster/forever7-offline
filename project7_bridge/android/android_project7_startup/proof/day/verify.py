"""Actual prepared-v64 OWN + f81b manager frame + full staged assets day RPC host.

Part 1: direct real manager entries + Store/reload/duplicate/writer-failure.
Part 2: real loopback socket -> LocalGatewayServer.handleClient day dispatch.
The actual outer path sends no reply and closes on a dispatch IOException; the minimal
FailureSafeProfileProvider seam returns old-day updateDay + explicit error without
settlement/reward, keeps the persisted document exactly unchanged, and retry advances.
Duplicate recovery cases warm one rejected calendar, set full/partial power state at profile root,
and use inclusive request-epoch bounds only for the full-recovery jpvt stamp; partial timestamps are exact. No D8, no APK, no native/device, no prepare/stage write.
Only JVM host classes compile in a temporary directory removed on exit.
"""
from pathlib import Path
import argparse
import hashlib
import json
import shutil
import subprocess
import tempfile
import urllib.parse

ROOT = Path(__file__).resolve().parents[5]
HERE = Path(__file__).resolve().parent
JDK = ROOT / "toolchains/java/jdk-17.0.21+9/Contents/Home/bin"
JSON_JAR = ROOT / "toolchains/json-20240303.jar"
parser = argparse.ArgumentParser()
parser.add_argument("--prepare", type=Path,
                    default=ROOT / "analysis/project7/story-city-integration-prepare-v64/project7-inputs-cu6vion6")
args = parser.parse_args()
PREPARE = args.prepare
VERSION = PREPARE.parent.name.rsplit("-", 1)[-1]
FRAMES = ROOT / "analysis/project7/action-ledger-code20-v2/manager-translated-frames.jar"
STAGE = PREPARE / "stage"
ASSETS = STAGE / "assets"
OWN = PREPARE / "compiled/production-classes"
SEAMS = ROOT / "project7_bridge/android/android_project7_startup/proof/seams"
DAY_OS = HERE / "seams/android/system/Os.java"
LOG = ROOT / "offline/current/java/android_core_rpc/host_stubs/android/util/Log.java"
IFACE_FIX = ROOT / "analysis/project7/cg-v61-dispatch-host/InterfaceCallFix.java"
DEX_JARS = ROOT / "toolchains/dex2jar-v2.4/dex-tools-v2.4/lib"
FIXED_SOURCES = [
    ROOT / "offline/current/java/android_single_package/src/com/project7/localmanager/FailureSafeProfileProvider.java",
    ROOT / "offline/current/java/android_dream_mode/src/com/project7/localmanager/DreamStorage.java",
    ROOT / "offline/current/java/android_single_package/src/com/project7/localmanager/ManagerLifecycleDriver.java",
    ROOT / "offline/current/java/android_core_rpc/src/com/project7/localmanager/CoreGapBridge.java",
    ROOT / "offline/current/java/android_baiye_transactions/src/com/project7/localmanager/BaiyeGateway.java",
    ROOT / "offline/current/java/android_baiye_shop/src/com/project7/localmanager/BaiyeShopGateway.java",
    ROOT / "offline/current/java/android_story_basics/src/com/project7/localmanager/StoryBasicsGateway.java",
    ROOT / "offline/current/java/android_wish_draw/src/com/project7/localmanager/WishGateway.java",
]
REPORT = ROOT / ("reports/project7-day-rpc-" + VERSION + ".json")

CLASSES7_SHA = "6555e75c0a8432f78422408c0327a3d8b4593eef420bcd0bb74eb5c911665d51"
FRAMES_SHA = "f81b686eb3cfdb7e87f5c9eae5075652d08afb38c8d104ed81b3baebcb703c0f"
NEW_PLAYER_SHA = "6877cdc06532a11faa47e1855049f678db1c210de96caf1312c27c431b9875d7"
ECONOMY_SHA = "4c504ae5fc5a431fb6eeffd6fb48df614bbfa00f0c2a8a949e23d1cd4363ed9a"

sha = lambda path: hashlib.sha256(Path(path).read_bytes()).hexdigest()


def meta(path):
    path = Path(path)
    return {"path": str(path.relative_to(ROOT)), "bytes": path.stat().st_size, "sha256": sha(path)}


def temp_meta(path):
    path = Path(path)
    return {"path": "<temp>/" + path.name, "bytes": path.stat().st_size, "sha256": sha(path)}


def run(command):
    result = subprocess.run(list(map(str, command)), capture_output=True, text=True)
    if result.returncode:
        raise SystemExit(result.stdout + result.stderr)
    return result.stdout + result.stderr


def main():
    checks = []

    def check(condition, message):
        if not condition:
            raise AssertionError(message)
        checks.append(message)

    check(sha(STAGE / "classes7.dex") == CLASSES7_SHA, VERSION + " stage classes7.dex is 6555e75c")
    check(sha(FRAMES) == FRAMES_SHA, "manager translated frames are f81b686e")
    check(sha(ASSETS / "new_player.bson") == NEW_PLAYER_SHA, VERSION + " staged new_player.bson is pinned")
    check(sha(ASSETS / "economy.tsv") == ECONOMY_SHA, VERSION + " staged economy.tsv is pinned")
    offline = json.loads((PREPARE.parent / "offline-project-build.json").read_bytes())
    check(offline["original_unchanged"] is True, VERSION + " original backend is unchanged")
    check(offline["apk_built"] is False and offline["native_runtime_tested"] is False, VERSION + " prepare did not build APK or test native runtime")
    check(offline["production_classes"] == len(list(OWN.rglob("*.class"))), VERSION + " prepared class count matches OWN")
    build = json.loads((STAGE / "build-inputs.json").read_bytes())
    check(build["manager_dex"] == "classes7.dex", VERSION + " build binds classes7 as the manager dex")
    check(build["story_asset_extensions"]["assets/economy.tsv"] == ECONOMY_SHA, VERSION + " build economy extension pin matches")
    compiled = json.loads((PREPARE / "compiled/compile-inputs.json").read_bytes())
    check(len(list(OWN.rglob("*.class"))) > 0, VERSION + " OWN production classes exist")
    check(sum(group.get("production_classes", 0) for group in compiled["groups"]) == len(list(OWN.rglob("*.class"))), VERSION + " compile-inputs group class count matches OWN")
    check(compiled["dex_built"] is False and compiled["apk_built"] is False and compiled["native_verified"] is False, VERSION + " compile inputs remain JVM-only")
    group_order = {group["group"]: index for index, group in enumerate(compiled["groups"])}
    check(group_order["startup"] < min(group_order[name] for name in ("core-rpc", "dream-mode", "baiye-transactions", "wish-draw")),
          "startup group compiles before each unwrap consumer")
    startup_sources = next(group["sources"] for group in compiled["groups"] if group["group"] == "startup")
    check("offline/current/java/android_single_package/src/com/project7/localmanager/FailureSafeProfileProvider.java" in startup_sources,
          VERSION + " prepare includes the provider seam in the startup group")
    check((OWN / "com/project7/localmanager/FailureSafeProfileProvider.class").is_file(),
          VERSION + " OWN contains FailureSafeProfileProvider.class")
    for path in FIXED_SOURCES:
        prepared = compiled["source_hashes"].get(str(path))
        check(prepared == sha(path), VERSION + " prepared source hash matches: " + path.name)

    temporary = Path(tempfile.mkdtemp(prefix="p7-day-rpc-" + VERSION + "-"))
    try:
        seams = temporary / "seams"
        tests = temporary / "tests"
        socket_tests = temporary / "socket-tests"
        ifacefix = temporary / "ifacefix"
        for directory in (seams, tests, socket_tests, ifacefix):
            directory.mkdir(parents=True)

        seam_sources = [p for p in sorted(SEAMS.rglob("*.java")) if p.name != "Os.java"] + [DAY_OS, LOG]
        result = run([JDK / "javac", "--release", "8", "-Xlint:-options", "-d", seams, *seam_sources])
        check("error" not in result.lower(), "host platform/type seams compile with volatile fault seam")

        base = f"{seams}:{FRAMES}:{JSON_JAR}:{OWN}"
        result = run([JDK / "javac", "--release", "8", "-Xlint:-options", "-cp", base,
                      "-d", tests, HERE / "DayRpcV63Host.java"])
        check("error" not in result.lower(), "DayRpcV63Host compiles against prepared OWN + f81b frames")

        cases = temporary / "day-cases.json"
        origin = temporary / "class-origin.log"
        host = run([JDK / "java", "-Xverify:all",
                    "-Xlog:class+load=info:file=" + str(origin),
                    "-cp", f"{base}:{tests}",
                    "com.project7.localmanager.DayRpcV63Host", ASSETS, cases])
        check("PASS v63 real Reliable statusCheck" in host, "real statusCheck/calendar host PASS")

        consumer = run([ROOT / ".venv/bin/python", HERE / "day_consumer.py", cases,
                        temporary / "consumer-result.json"])
        check("PASS original day consumer" in consumer, "original 640 consumer fields/order PASS")
        consumer_result = json.loads((temporary / "consumer-result.json").read_bytes())
        cases_json = json.loads(cases.read_bytes())

        for name in ("LocalGatewayServer", "LocalProfileStore", "LocalEconomyEngine", "LocalEventEngine", "BsonLite", "ProtoLite"):
            rows = [line for line in origin.read_text().splitlines()
                    if f" com.project7.localmanager.{name} source:" in line]
            check(len(rows) == 1 and str(FRAMES) in urllib.parse.unquote(rows[0]), name + " loads from f81b frames")
        check(all(str(seams) not in line for line in origin.read_text().splitlines() if " com.project7.localmanager." in line),
              "platform seams do not shadow project7 manager classes")
        check("unknown_frames" in cases_json["calendar"], "calendar case records unrelated publication frame count")
        check(cases_json["calendar"]["day_before"] == 0 and cases_json["calendar"]["day_after"] == 1, "calendar case day 0 -> 1")
        check(cases_json["calendar"]["reload_day"] == 1 and cases_json["calendar"]["reload_city_av"] == 24, "calendar case reload day/city")
        check(cases_json["writer_failure"]["frames"] == [] and cases_json["writer_failure"]["day_after_failure"] == 0, "writer failure emits no reply and keeps day 0")
        check(cases_json["writer_failure"]["day_after_retry"] == 1, "writer failure retry advances once")
        check(cases_json["status_check_blocked"]["day_after"] == 0, "blocked statusCheck keeps day 0")
        check(cases_json["calendar"]["unknown_first_md5"] == hashlib.md5(b"syncNewAchievementData").hexdigest(),
              "first non-day calendar frame is stock syncNewAchievementData")

        dex_classpath = ":".join(sorted(str(p) for p in DEX_JARS.glob("*.jar")))
        run([JDK / "javac", "-nowarn", "-cp", dex_classpath, "-d", ifacefix, IFACE_FIX])
        hostfix = temporary / "manager-translated-frames-hostfix.jar"
        fixout = run([JDK / "java", "-cp", f"{ifacefix}:{dex_classpath}", "InterfaceCallFix", FRAMES, hostfix])
        check("interface_call_fixes=2" in fixout, "hostfix repairs exactly two dex2jar interface-call mistakes")

        socket_base = f"{seams}:{hostfix}:{JSON_JAR}:{OWN}"
        result = run([JDK / "javac", "--release", "8", "-Xlint:-options", "-cp", socket_base,
                      "-d", socket_tests, HERE / "DayRpcSocketHost.java"])
        check("error" not in result.lower(), "real-socket failure host compiles with prepared provider seam")
        socket_cases = temporary / "socket-cases.json"
        socket_origin = temporary / "socket-class-origin.log"
        socket = run([JDK / "java", "-Xverify:all",
                      "-Xlog:class+load=info:file=" + str(socket_origin),
                      "-cp", f"{socket_base}:{socket_tests}",
                      "com.project7.localmanager.DayRpcSocketHost", ASSETS, socket_cases])
        check("PASS real-socket day failure" in socket, "real-socket baseline/fixed day failure PASS")
        socket_json = json.loads(socket_cases.read_bytes())
        baseline = socket_json["baseline_outer"]
        fixed_case = socket_json["fixed_provider"]
        check(baseline["reply_frames"] == 0 and baseline["closed"] is True and baseline["timeout"] is False,
              "actual handleClient outer path sends no day reply and closes")
        check(baseline["day"] == 0 and baseline["city_av"] == 0, "baseline outer path keeps day/city")
        check(fixed_case["failure_frames"] == 2 and fixed_case["message"] is True and fixed_case["update_day"] == 0,
              "fixed seam sends message + old-day updateDay")
        check(fixed_case["settlement"] is False, "fixed seam sends no showDailySettlement/reward")
        check(fixed_case["progress_unchanged"] is True, "fixed seam leaves tutorial progress unchanged on a proven-uncommitted write")
        check(fixed_case["profile_exact_unchanged"] is True and fixed_case["day_after_failure"] == 0,
              "fixed failure leaves every persisted document field exactly unchanged")
        check(fixed_case["retry_update_day"] == 1 and fixed_case["retry_day"] == 1 and fixed_case["retry_city_av"] == 24,
              "retry after fixed failure advances once and persists day/city")
        uncertain = socket_json["uncertain_commit"]
        check(uncertain["reply_frames"] == 0 and uncertain["closed"] is True and uncertain["timeout"] is False,
              "uncertain after-rename commit sends no fallback and disconnects")
        check(uncertain["persisted_day"] == 1 and uncertain["reconnect_day"] == 1,
              "after-rename commit is visible after reconnect resync")
        wrapper = (ROOT / "offline/current/java/android_single_package/src/com/project7/localmanager/FailureSafeProfileProvider.java").read_text()
        check("synchronized (delegate)" in wrapper and "synchronized (profileLock())" in wrapper and "Arrays.equals(before, actual)" in wrapper and "progress.toProperties()" in wrapper,
              "provider seam locks Store + PROFILE_LOCK, strictly compares bytes, and rejects fallback on progress mutation")
        readable = (ROOT / "analysis/project7/research/readable/java/LocalProfileStore.java").read_text()
        start = readable.index("updateEconomy(String p20")
        body = readable[start:readable.index("updateProfile(String p5", start)]
        check(body.index("writeAtomic") < body.index("LocalEconomyEngine.reconcile"),
              "original updateEconomy writes the profile before post-write reconcile/recover progress mutations")
        for name in ("FailureSafeProfileProvider", "DreamStorage"):
            rows = [line for line in socket_origin.read_text().splitlines()
                    if f" com.project7.localmanager.{name} source:" in line]
            check(len(rows) == 1 and str(OWN) in urllib.parse.unquote(rows[0]), name + " loads from prepared OWN")
        check("FailureSafeProfileProvider" in (ROOT / "offline/current/java/android_single_package/src/com/project7/localmanager/ManagerLifecycleDriver.java").read_text(),
              "ManagerLifecycleDriver wires the provider seam")
        for path in [ROOT / "offline/current/java/android_dream_mode/src/com/project7/localmanager/DreamStorage.java",
                     ROOT / "offline/current/java/android_core_rpc/src/com/project7/localmanager/CoreGapBridge.java",
                     ROOT / "offline/current/java/android_baiye_transactions/src/com/project7/localmanager/BaiyeGateway.java",
                     ROOT / "offline/current/java/android_baiye_shop/src/com/project7/localmanager/BaiyeShopGateway.java",
                     ROOT / "offline/current/java/android_story_basics/src/com/project7/localmanager/StoryBasicsGateway.java",
                     ROOT / "offline/current/java/android_wish_draw/src/com/project7/localmanager/WishGateway.java"]:
            check(("FailureSafeProfileProvider.unwrap" in path.read_text()) or
                  ("unwrapProvider" in path.read_text()),
                  "original exact-store owner check unwraps wrapper: " + path.name)

        report = {
            "format": "project7-day-rpc-" + VERSION + "-v1",
            "status": "PASS_host_jvm_only_not_android_native",
            "prepare_version": VERSION,
            "production_change": {
                "scope": "minimal generic Store-write failure seam; no route logic rewrite",
                "files": [str(p.relative_to(ROOT)) for p in FIXED_SOURCES],
                "wiring": "ManagerLifecycleDriver constructs LocalGatewayServer with FailureSafeProfileProvider(LocalProfileStore)",
                "compatibility": "all original exact LocalProfileStore owner checks unwrap the provider wrapper (DreamStorage, CoreGapBridge, BaiyeGateway, BaiyeShopGateway, StoryBasicsGateway, WishGateway)",
                "in_prepared_v64": True,
                "v64_stage_prepare_untouched": True,
                "requires_next_prepare_rebuild": False,
            },
            "build_integration": {
                "new_class_group": "startup",
                "new_class": "offline/current/java/android_single_package/src/com/project7/localmanager/FailureSafeProfileProvider.java",
                "unwrap_consumers": ["core-rpc", "dream-mode", "baiye-transactions", "wish-draw"],
                "group_order_checked": True,
                "prepare_note": VERSION + " prepare includes the provider seam in the startup group and all unwrap consumers compile after it",
            },
            "preconditions": {
                "profile_source": VERSION + " stage/assets/new_player.bson only, plus legal weeknum/city/std fields",
                "stock_week": 1, "stock_day": 0, "city_action_value": 0,
                "prologue_passed": True, "in_emergency": False, "processing_events": [],
                "patrol_reward_pending": False, "q7_battle_empty": True, "std_ff": False,
                "target_result_preseeded": False,
                "fixture_stabilization": "warm one rejected calendar for stock defaults; set city jpv/jpvt/mjpv and root q7powerDay; full uses inclusive request epoch bounds only for jpvt, partial 100/now-10 is byte-exact",
            },
            "recovery_evidence": {
                "writer": "LocalServiceEngine.recover([B J)",
                "full_240": "jpvt is stamped with current epoch and jpv stays 240, regardless of day",
                "partial_359": "jpvt/jpv unchanged",
                "partial_360": "jpv increments once and jpvt is stamped now",
                "partial_10": "jpvt/jpv unchanged across seconds and old date",
                "duplicate_full": "city excluding jpvt exact; jpvt inclusive [requestStart,requestEnd]; root q7powerDay exact; jpv=240",
                "duplicate_partial": "city/weeknum/q7EconomyCommit/root q7powerDay byte-exact",
            },
            "inputs": {
                "prepare": meta(PREPARE / "stage/build-inputs.json"),
                "offline_project_build": meta(PREPARE.parent / "offline-project-build.json"),
                "compile_inputs": meta(PREPARE / "compiled/compile-inputs.json"),
                "stage_classes7": meta(STAGE / "classes7.dex"),
                "manager_frames": meta(FRAMES),
                "manager_frames_hostfix": temp_meta(hostfix),
                "interface_call_fix_source": meta(IFACE_FIX),
                "new_player": meta(ASSETS / "new_player.bson"),
                "economy": meta(ASSETS / "economy.tsv"),
                "own_class_count": len(list(OWN.rglob("*.class"))),
                "host_source": meta(HERE / "DayRpcV63Host.java"),
                "socket_host_source": meta(HERE / "DayRpcSocketHost.java"),
                "consumer_source": meta(HERE / "day_consumer.py"),
                "verify_source": meta(HERE / "verify.py"),
                "fixed_sources": {str(p.relative_to(ROOT)): meta(p) for p in FIXED_SOURCES},
                "fixed_classes": {
                    name: sha(OWN / "com/project7/localmanager" / (name + ".class"))
                    for name in ("FailureSafeProfileProvider", "DreamStorage", "ManagerLifecycleDriver",
                                 "CoreGapBridge", "BaiyeGateway", "BaiyeShopGateway",
                                 "StoryBasicsGateway", "WishGateway")
                },
            },
            "commands": {
                "host": [str(value).replace(str(temporary), "<temp>") for value in
                         [JDK / "java", "-Xverify:all", "-cp", f"{base}:{tests}",
                          "com.project7.localmanager.DayRpcV63Host", ASSETS, cases]],
                "socket_host": [str(value).replace(str(temporary), "<temp>") for value in
                                [JDK / "java", "-Xverify:all", "-cp", f"{socket_base}:{socket_tests}",
                                 "com.project7.localmanager.DayRpcSocketHost", ASSETS, socket_cases]],
                "consumer": [str(value).replace(str(temporary), "<temp>") for value in
                             [ROOT / ".venv/bin/python", HERE / "day_consumer.py", cases,
                              temporary / "consumer-result.json"]],
            },
            "host_stdout": host,
            "socket_stdout": socket,
            "consumer_stdout": consumer,
            "consumer": consumer_result,
            "checks": checks,
            "write_order_evidence": {
                "write_atomic_before_post_write_progress": True,
                "source": meta(ROOT / "analysis/project7/research/readable/java/LocalProfileStore.java"),
                "proof": "strict before bytes and progress properties under Store monitor + PROFILE_LOCK; only byte-identical profile and unchanged progress may return old-day unlock; after-rename fault disconnects and reconnect sees day 1",
            },
            "outer_path_evidence": {
                "source": meta(ROOT / "analysis/project7/research/readable/java/LocalGatewayServer.java"),
                "handleClient": "its catch table covers readFrame EOFException and parse-time IOException only; dispatch IOException escapes (readable handleClient catch at lines 818-821)",
                "run_worker": "lambda$run$5 catches Throwable, logs 'connection ended: IOException', closes the socket and removes the session; no updateDay/message is written",
                "socket_baseline": baseline,
            },
            "socket_cases": socket_json,
            "day_cases": {
                "status_check": {"entry": "LocalGatewayServer.handleReliableRpc -> handleDayRpc", "request_method": cases_json["status_check"]["request"]["method"], "day_before": 0, "day_after": 0,
                                 "reply": "statusCheckReply r=ok,s=nextday", "duplicate_read_only": True},
                "calendar": {"entry": "LocalGatewayServer.handleCalendar -> LocalProfileStore.updateEconomy", "request_method": cases_json["calendar"]["request"]["method"], "day_before": 0, "day_after": 1,
                             "city_av_after": 24, "reload_day": 1, "reload_city_av": 24,
                             "replies": [row["method"] for row in cases_json["calendar"]["frames"]],
                             "unknown_publication_frames": cases_json["calendar"]["unknown_frames"],
                             "unknown_first_keys": cases_json["calendar"].get("unknown_first_keys"),
                             "unknown_first_method": "syncNewAchievementData",
                             "duplicate_same_day": True, "duplicate_semantically_identical": True},
                "recovery_full": cases_json.get("recovery_full", {}),
                "recovery_partial": cases_json.get("recovery_partial", {}),
                "writer_failure_direct": {"reply_frames": 0, "day_after_failure": 0, "day_after_retry": 1, "progress_unchanged": True},
                "status_check_blocked": {"reply": "blocked", "day_before": 0, "day_after": 0, "no_updateDay": True},
                "writer_failure_socket": {"outer_path_no_reply_closed": True, "fixed_seam_message": True,
                                          "fixed_seam_old_day_unlock": 0, "fixed_seam_settlement": False,
                                          "exact_profile_unchanged": True, "progress_unchanged": True,
                                          "uncertain_after_rename_disconnects": True, "retry_day": 1},
            },
            "unknown_frame_note": "calendar unknown frames are stock achievement/task publications: first is syncNewAchievementData {d}; the remainder are createNewAchievementTask/updateAllAchievement style frames. None is a day method and only the day method set is asserted.",
            "limits": [
                "JVM translated frames only; no ART/D8/APK/device/native execution",
                "route-specific dialogue/battle/patrol/day-7 ending flows are outside this focused day host",
                "stored weeknum c/l are transient in the real reply; the stock store clears them after publishing showDailySettlement",
                "duplicate full 240 legitimately stamps jpvt=now; comparator allows only inclusive request-epoch bounds and requires all other fields exact; partial timestamp cases are exact",
                "the outer handleClient path is proven by a real loopback socket, not device/native networking",
            ],
            "no_d8_apk_native": True,
            "no_prepare_or_stage_write": True,
            "temporary_directory_removed_on_exit": True,
        }
        REPORT.write_text(json.dumps(report, indent=2) + "\n")
        print("PASS " + VERSION + " day RPC:", host.strip())
        print("PASS socket failure:", socket.strip())
        print("PASS consumer:", consumer.strip().splitlines()[0])
        print("checks=", len(checks))
    finally:
        shutil.rmtree(temporary, ignore_errors=True)


if __name__ == "__main__":
    main()
