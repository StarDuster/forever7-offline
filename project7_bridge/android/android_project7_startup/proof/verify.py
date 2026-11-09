"""Reuse published hosts against current v62 OWN + f81b manager frame + staged assets.

No D8, no APK, no Android runtime, no native, no user BSON/templates beyond staged public assets.
Only JVM host classes are compiled in a temporary directory that is removed on exit.
"""
from pathlib import Path
import argparse
import hashlib
import json
import shutil
import subprocess
import tempfile
import time

ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
JDK = ROOT / "toolchains/java/jdk-17.0.21+9/Contents/Home/bin"
JSON_JAR = ROOT / "toolchains/json-20240303.jar"
parser = argparse.ArgumentParser()
parser.add_argument("--prepare", type=Path, default=ROOT / "analysis/project7/story-city-integration-prepare-v62/project7-inputs-bbsfrjy6")
parser.add_argument("--manager-frames", type=Path, default=ROOT / "analysis/project7/action-ledger-code20-v2/manager-translated-frames.jar")
args = parser.parse_args()
PREPARE = args.prepare
OWN = PREPARE / "compiled/production-classes"
STAGE = PREPARE / "stage"
ASSETS = STAGE / "assets"
FRAMES = args.manager_frames
ORIGINAL_HOST = ROOT / "offline/current/java/android_collection/verification_sources"
REAL_COLLECTION = ORIGINAL_HOST / "com/project7/localmanager/RealCollectionHost.java"
IDENTITY_STUB = ROOT / "offline/current/java/android_collection/compile_stubs/com/project7/localmanager/StableIdentityBootstrap.java"

CLASSES7_SHA = "6555e75c0a8432f78422408c0327a3d8b4593eef420bcd0bb74eb5c911665d51"
FRAMES_SHA = "f81b686eb3cfdb7e87f5c9eae5075652d08afb38c8d104ed81b3baebcb703c0f"
CATALOG_SHA = "5e716bd9a34cfd678af9aba6385ba3fae92d4b17486ee480f76bd95320268e99"
TARGET_SHA = "7e3849b6ed316b7cdc2ef9f103b90e0bc8e20f9b5da70ab3b585fbd72c0da62d"
ORIGINAL_DEX_SHA = "087656832b8150984c81c997c7c1f3966da22902c5226b0f6ef2f3e71d602325"
TRIAL_SHA = "ce54f931f6d462d0c6fabb1f03dabf47ddc54780d89e3ec78fe21d9a6d7ef0d9"

sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()


def run(command, timeout=300):
    started = time.monotonic()
    result = subprocess.run(list(map(str, command)), capture_output=True, text=True, timeout=timeout)
    result.elapsed = time.monotonic() - started
    return result


def meta(path):
    path = Path(path)
    return {"path": str(path.relative_to(ROOT)), "bytes": path.stat().st_size, "sha256": sha(path)}


def main():
    checks = []
    def check(condition, message):
        if not condition:
            raise AssertionError(message)
        checks.append(message)

    check(sha(STAGE / "classes7.dex") == CLASSES7_SHA, "v62 classes7.dex is 6555e75c")
    check(sha(FRAMES) == FRAMES_SHA, "translated manager frames are f81b686e")
    check(sha(ASSETS / "resources.tsv") == CATALOG_SHA, "v62 resources.tsv is the pinned catalog")
    check(sha(ASSETS / "project7_catalog/target-manifest.json") == TARGET_SHA, "v62 target manifest is pinned")
    compiled = json.loads((PREPARE / "compiled/compile-inputs.json").read_bytes())
    for path, expected in compiled["source_hashes"].items():
        if "android_collection/src" in path or "android_project7_startup/src" in path or "android_autologin/src" in path:
            check(sha(ROOT / path) == expected, "source hash current: " + path.split("/")[-1])
    build = json.loads((PREPARE / "stage/build-inputs.json").read_bytes())
    check(build["story_mission_catalog_sha256"] == TRIAL_SHA, "v62 story mission catalog pin is ce54f931")

    temporary = Path(tempfile.mkdtemp(prefix="p7-startup-collection-autologin-"))
    try:
        seams = temporary / "seams"
        identity = temporary / "identity"
        collection_classes = temporary / "collection"
        startup_classes = temporary / "startup-binding"
        startup_tests = temporary / "startup-tests"
        for directory in (seams, identity, collection_classes, startup_classes, startup_tests):
            directory.mkdir(parents=True)

        result = run([JDK / "javac", "-source", "8", "-target", "8", "-Xlint:-options", "-d", seams,
                      *sorted((HERE / "seams").rglob("*.java"))])
        check(result.returncode == 0, "host platform/type seams compile")
        identity_source = identity / "com/project7/localmanager/StableIdentityBootstrap.java"
        identity_source.parent.mkdir(parents=True)
        identity_source.write_text(IDENTITY_STUB.read_text().replace("final class LocalProfileStore { }", ""))
        base = f"{seams}:{FRAMES}:{JSON_JAR}"
        result = run([JDK / "javac", "-source", "8", "-target", "8", "-Xlint:-options", "-cp", base,
                      "-d", identity, identity_source])
        check(result.returncode == 0, "collection compile-only identity type seam compiles")

        collection_cp = f"{base}:{identity}:{OWN}"
        result = run([JDK / "javac", "-source", "8", "-target", "8", "-Xlint:-options", "-cp", collection_cp,
                      "-d", collection_classes, REAL_COLLECTION, HERE / "collection/V62CollectionHost.java"])
        check(result.returncode == 0, "published RealCollectionHost + v62 prepare wrapper compile")

        startup_cp = f"{base}:{OWN}"
        result = run([JDK / "javac", "-source", "8", "-target", "8", "-Xlint:-options", "-cp", startup_cp,
                      "-d", startup_classes, HERE / "startup/StartupCredentialBindingHost.java"])
        check(result.returncode == 0, "coordinator credential-binding host compiles against v62 OWN")

        result = run([JDK / "javac", "-source", "8", "-target", "8", "-Xlint:-options", "-cp", startup_cp,
                      "-d", startup_tests,
                      HERE / "startup_host_stubs/android/app/Activity.java",
                      HERE / "startup_host_stubs/com/forever7/offline/ResourceInitActivity.java",
                      HERE / "StartupHostTests.java"])
        check(result.returncode == 0, "published StartupHostTests compile against v62 OWN")

        properties = [
            f"-Dp7.baiye.catalog={ROOT}/offline/current/data/project7_baiye_catalog/catalog-v1.tsv",
            f"-Dp7.baiye.fragments={ROOT}/offline/current/data/project7_baiye_catalog/fragments-v1.tsv",
            f"-Dp7.baiye.shop={ROOT}/offline/current/data/project7_baiye_shop_catalog/catalog-v1.tsv",
        ]
        collection = run([JDK / "java", "-Xverify:all", "-Xmx768m", *properties,
                          "-cp", f"{collection_cp}:{collection_classes}",
                          "com.project7.localmanager.V62CollectionHost",
                          ASSETS, ASSETS / "resources.tsv", ASSETS / "project7_catalog/target-manifest.json"])
        check(collection.returncode == 0, "v62 collection host exit 0")
        out = collection.stdout
        check(out.count("PREPARE PASS ") == 9, "collection host nine prepare calls pass")
        check("REAL_TRANSLATED_ENGINE_PASS heroes=140 skins=494 treasurePairs=1900 firstOriginalGrants=1900 "
              "firstPrivateWrites=1 initialBytes=217 finalBytes=475501 cumulativeInputBytes=543186885 "
              "cumulativeOutputBytes=543567045" in out, "real translated engine exact result")
        check("faultCases=3 repeatOriginalGrants=0 repairOriginalGrants=0" in out, "real engine fault/idempotence counters")
        check(out.count("MANAGER_CLASS ") == 8 and all(
            "manager-translated-frames.jar" in line for line in out.splitlines() if line.startswith("MANAGER_CLASS ")),
            "all eight original business classes load from f81b frames")
        check(out.count("OWN_CLASS ") == 5 and all(
            "story-city-integration-prepare-v62" in line and "compiled/production-classes" in line
            for line in out.splitlines() if line.startswith("OWN_CLASS ")),
            "collection bridge/targets/validator/initializer load from v62 OWN")

        binding = run([JDK / "java", "-Xverify:all", "-Xmx768m", *properties,
                       "-cp", f"{startup_cp}:{startup_classes}",
                       "com.project7.localmanager.StartupCredentialBindingHost", ASSETS], timeout=300)
        check(binding.returncode == 0, "coordinator credential-binding host exit 0")
        for marker in (
            "PASS real_bootstrap_prepared_identity_delivers_exact_credentials_into_coordinator_session_and_autologin",
            "PASS coordinator_reload_over_same_journal_keeps_identity_secret_and_autologin_delivery",
            "PASS profile_only_policy_never_publishes_session_or_autologin_credentials",
            "PASS coordinator_rejects_delivered_username_that_differs_from_prepared_identity",
            "PASS coordinator_rejects_prepared_identity_without_a_bound_numeric_id",
            "PASS credential_receiver_exception_fails_preparation_without_publishing_session",
            "STARTUP_CREDENTIAL_BINDING_PASSED=6",
        ):
            check(marker in binding.stdout, "binding marker: " + marker)

        existing = run([JDK / "java", "-cp", f"{seams}:{startup_tests}:{FRAMES}:{JSON_JAR}:{OWN}",
                        "com.project7.localmanager.StartupHostTests"])
        check(existing.returncode == 0, "published StartupHostTests exit 0")
        check("STARTUP_HOST_GROUPS_PASSED=17" in existing.stdout, "published coordinator host 17 groups pass")

        report = {
            "format": "project7-startup-collection-autologin-binding-v1",
            "status": "PASS_host_jvm_only_not_android_native",
            "prepare": meta(PREPARE / "stage/build-inputs.json"),
            "inputs": {
                "manager_dex": meta(STAGE / "classes7.dex"),
                "manager_frames": meta(FRAMES),
                "manager_class_count": 650,
                "resources_tsv": meta(ASSETS / "resources.tsv"),
                "target_manifest": meta(ASSETS / "project7_catalog/target-manifest.json"),
                "own_class_count": len(list(OWN.rglob("*.class"))),
                "own_key_classes": {
                    name: sha(OWN / "com/project7/localmanager" / (name + ".class"))
                    for name in ("CollectionBson", "CollectionStockBridge", "CollectionTargets",
                                 "CollectionValidator", "FullCollectionInitializer", "StableIdentityBootstrap",
                                 "StockIdentityStorage", "Project7StartupCoordinator", "Project7StartupPlatform",
                                 "SinglePackageGateway")
                },
                "autologin_classes": {
                    name: sha(OWN / "com/netease/qrzd" / (name + ".class"))
                    for name in ("AutoLoginCore", "Project7LoginDialog")
                },
            },
            "collection_command": [str(v).replace(str(temporary), "<temp>") for v in collection.args],
            "collection_stdout": collection.stdout,
            "collection_wall_seconds": round(collection.elapsed, 3),
            "binding_command": [str(v).replace(str(temporary), "<temp>") for v in binding.args],
            "binding_stdout": binding.stdout,
            "binding_wall_seconds": round(binding.elapsed, 3),
            "published_startup_host_command": [str(v).replace(str(temporary), "<temp>") for v in existing.args],
            "published_startup_host_stdout": existing.stdout,
            "autologin_existing_host": "offline/current/java/android_autologin/verify.py PASS AutoLoginHostTests + Android-32 compile",
            "host_injected_leaves": [
                "Project7StartupCoordinator.Services.publish returns a 312-entry receipt object instead of scanning real resources",
                "Project7RepairHost.Lease is a finite active host lease; no file watcher thread",
                "Project7StartupPlatform.OwnedBackend/SinglePackageGateway manager-process lifecycle is represented by HostBackend.start; no real gateway service",
                "AutoLoginCore dispatcher and input sink are host queues; no native login callback slot is executed",
                "android.app.Service and related Android types are type-only linkage stubs; no Android SDK jar at runtime and no Android behavior executes",
                "collection AssetManager maps staged public assets and rejects non-catalog TSVs in the collection host; the startup host exposes the staged asset tree so the nine prepare calls and profile templates can load",
            ],
            "native_residual": [
                "No DEX/ART/device/APK/native C_file execution; dex2jar frames and JVM verification only",
                "No real 312-entry resource download/import/hash scan or device resource acceptance",
                "No real Android Service/GatewayService process owner, SAVE_ACCESS concurrency, Activity lifecycle or native login callback",
            ],
            "no_d8_apk_native": True,
            "temporary_directory_removed_on_exit": True,
        }
        (ROOT / "reports/project7-startup-collection-autologin-binding.json").write_text(json.dumps(report, indent=2) + "\n")
        print("PASS v62+f81b collection:", collection.stdout.splitlines()[-2])
        print("PASS startup credential binding groups:", binding.stdout.strip().splitlines()[-1])
        print("PASS published StartupHostTests: 17 groups")
        print("PASS checks:", len(checks))
    finally:
        shutil.rmtree(temporary, ignore_errors=True)


if __name__ == "__main__":
    main()
