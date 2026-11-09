"""Compile/run inventory editor against the current classes7 manager cache.

The only extracted assets are the small fixed catalogs needed by resource and
history policy construction; the 1.2 GiB extracted APK asset cache is not used.
No D8/APK build/device/ART claim.
"""
from pathlib import Path
import hashlib, subprocess, tempfile, zipfile

R = Path(__file__).resolve().parents[2]
H = Path(__file__).resolve().parent
# Production sources moved to the offline tree; host_tests stayed here.
P = R / 'offline/current/java/android_baiye_transactions'
C = R / 'analysis/project7/final-host-cache'
J = R / 'toolchains/java/jdk-17.0.21+9/Contents/Home/bin'
SDK = R / 'toolchains/android-sdk/platforms/android-32/android.jar'
JAR = C / 'classes7-frames.jar'
JAR6 = C / 'classes6-frames.jar'
APK = R / 'builds/forever7-offline-v22-20261107.apk'
B = Path(tempfile.mkdtemp(prefix='inventory-editor-', dir=R / 'analysis/project7'))
for name in ('api', 'prod', 'platform', 'tests', 'assets'):
    (B / name).mkdir()

assert hashlib.sha256(JAR.read_bytes()).hexdigest() == '0a153e1b20447779cf453b3326a94db041897f0f85a5f1b9e89dfde072fd5191'
assert hashlib.sha256(JAR6.read_bytes()).hexdigest() == 'b1dbb7f4d520720f613dc78c886487494f84aad365d9410ec28fabf5d7f8c424'
with zipfile.ZipFile(APK) as archive:
    wanted = ('assets/resources.tsv', 'assets/treasure.tsv', 'assets/project7_history/catalog-v3.tsv',
                     'assets/project7_history/furniture-v1.tsv',
                     'assets/project7_selector/catalog-v1.tsv',
                     'assets/event_graph.tsv', 'assets/home.tsv')
    for member in wanted:
        data = archive.read(member)
        target = B / 'assets' / member[len('assets/'):]
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)

def run(*args):
    result = subprocess.run(list(map(str, args)), capture_output=True, text=True)
    assert result.returncode == 0, result.stdout + result.stderr
    return result.stdout + result.stderr

run(J / 'javac', '--release', '8', '-cp', SDK, '-d', B / 'api',
    *(P / 'compile_stubs').rglob('*.java'))
run(J / 'javac', '--release', '8', '-cp', str(SDK) + ':' + str(B / 'api'),
    '-d', B / 'prod', *(P / 'src').rglob('*.java'))
platform = [p for p in (R / 'runtime/android_core_rpc/host_stubs').rglob('*.java')
            if p.name not in ('AssetManager.java',)]
run(J / 'javac', '--release', '8', '-d', B / 'platform', *platform,
    H / 'host_tests/android/content/res/AssetManager.java')
cp = ':'.join(map(str, (B / 'platform', B / 'prod', JAR, JAR6,
                       R / 'toolchains/json-20240303.jar')))
run(J / 'javac', '--release', '8', '-cp', cp, '-d', B / 'tests',
    H / 'host_tests/com/project7/localmanager/BaiyeHost.java',
    H / 'host_tests/com/project7/localmanager/InventoryEditorHost.java')
out = run(J / 'java', '-Xverify:all', '-Xmx512m', '-XX:ActiveProcessorCount=2',
          '-Dp7.baiye.catalog=' + str(R / 'runtime/project7_baiye_catalog/catalog-v1.tsv'),
          '-Dp7.baiye.fragments=' + str(R / 'runtime/project7_baiye_catalog/fragments-v1.tsv'),
          '-cp', cp + ':' + str(B / 'tests'),
          'com.project7.localmanager.InventoryEditorHost', B / 'assets')
print(out, end='')
print(B)
