#!/usr/bin/env python3
"""Run the actual 159-check COC wrapper host against the final v10 classes.

This is the migrated form of run.py: same unchanged
StoryCityCocGatewayHost.java, but the manager/policy classpath is the final
classes7/classes6 translation cache and assets come read-only from the final
APK fixture. Host-only; no D8/APK/device/Git.
"""
from pathlib import Path
import hashlib, json, subprocess, tempfile, shutil

ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
C = ROOT / "analysis/project7/final-host-cache"
A = C / "apk-assets/assets"
J = ROOT / "toolchains/java/jdk-17.0.21+9/Contents/Home/bin"
SDK = ROOT / "toolchains/android-sdk/platforms/android-32/android.jar"
JSONJAR = ROOT / "toolchains/json-20240303.jar"


def run(args, **kw):
    p = subprocess.run([str(a) for a in args], capture_output=True, text=True, **kw)
    if p.returncode:
        raise SystemExit((p.stdout or "") + (p.stderr or ""))
    return p.stdout + p.stderr


def main():
    expected = {
        "classes7.dex": "0b4c41a5461840fb7bdb02529732a2c6849d604893b6a9390b9a9404618d0eb4",
        "classes6.dex": "b4536196d2f91f803a91c392c6ed91bbdafada349e9a10542b15b91132eaaa3f",
    }
    for name, digest in expected.items():
        if hashlib.sha256((C / name).read_bytes()).hexdigest() != digest:
            raise SystemExit("final cache hash mismatch: " + name)
    w = Path(tempfile.mkdtemp(prefix="p7-coc-final-"))
    try:
        platform, tests = w / "platform", w / "tests"
        platform.mkdir(); tests.mkdir()
        core = [p for p in (ROOT / "runtime/android_core_rpc/host_stubs").rglob("*.java")
                if p.name not in ("AssetManager.java", "Os.java")]
        baiye = [p for p in (ROOT / "runtime/android_baiye_transactions/host_tests/android").rglob("*.java")
                 if p.name != "AssetManager.java"]
        run([J / "javac", "--release", "8", "-d", platform, *core, *baiye,
             ROOT / "runtime/android_week_reset/host_tests/android/system/Os.java",
             C / "hostsrc/android/content/res/AssetManager.java"])
        run([J / "javac", "--release", "8",
             "-cp", f"{C/'classes6-frames.jar'}:{platform}:{C/'classes7-frames.jar'}:{JSONJAR}:{SDK}",
             "-d", tests, HERE / "com/project7/localmanager/StoryCityCocGatewayHost.java"])
        out = w / "host-result.json"
        text = run([J / "java", "-Xverify:all",
                    "-cp", f"{C/'classes6-frames.jar'}:{platform}:{C/'classes7-frames.jar'}:{JSONJAR}:{tests}",
                    "-Dp7.baiye.catalog=" + str(A / "project7_baiye/catalog-v1.tsv"),
                    "-Dp7.baiye.fragments=" + str(A / "project7_baiye/fragments-v1.tsv"),
                    "-Dp7.baiye.shop=" + str(A / "project7_baiye_shop/catalog-v1.tsv"),
                    "com.project7.localmanager.StoryCityCocGatewayHost",
                    A, C / "classes7.dex", C / "classes7-frames.jar", C / "classes6-frames.jar", out])
        result = json.loads(out.read_text())
        result["command"] = "python3 runtime/android_project7_startup/proof/coc_wrapper/run_final_classes.py"
        result["final_classes"] = expected
        result["final_frames_jar_sha256"] = hashlib.sha256((C / "classes7-frames.jar").read_bytes()).hexdigest()
        result["assets_fixture"] = str(A.relative_to(ROOT))
        result["host_stdout"] = text.strip().splitlines()[-3:]
        report = ROOT / "reports/root-v10-final-coc-wrapper-host.json"
        report.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
        print(json.dumps({k: result[k] for k in ("status", "checks", "classes7_sha256")}, sort_keys=True))
        print("report=" + str(report))
    finally:
        shutil.rmtree(w, ignore_errors=True)


if __name__ == "__main__":
    main()
