"""Finite v43 P7-gateway verification for menu10 entry/selector11 continuation.

Runs the host against the frozen v41 stage assets and manager frame, with the
reviewed StoryMissionBridge/StoryCityPolicy/StoryMenu* owners compiled from
source. The frozen Bridge class is byte-identical; menu10 entry is the only new
entry and menu12 stays disabled. No D8/APK/native and no COC Hook/patch input.
"""
from pathlib import Path
import hashlib
import json
import os
import re
import subprocess
import tempfile

R = Path(__file__).resolve().parents[4]
H = Path(__file__).resolve().parent
V41 = R / 'analysis/project7/story-city-integration-prepare-v43/project7-inputs-6i2v7gq2'
OWN = V41 / 'compiled/production-classes'
STAGE_ASSETS = V41 / 'stage/assets'
COMPILE_API = V41 / 'compiled/compile-api.jar'
FRAME = R / 'analysis/project7/story-city-coc-gateway-v36/manager-translated-frames.jar'
FRAME_PIN = 'a767c656b853d40d2e8acac835eac19ec2272da8cbee112a7428637d539bbc66'
CATALOG = H / 'catalog/special-selector-v1.json'
CATALOG_PIN = '5b9d6b01f7fd77ed63f1f301b39ef31db4d7b8fb644383aa28aadcec000404aa'
ENTRY = H / 'catalog/menu10-entry-v1.json'
ENTRY_PIN = '4bd8602a3999f142dfbdeb97aa3330f030c54f3099bb0ed36bde444bf85f9cae'
CITY = R / 'offline/current/java/android_story_city/src/com/project7/localmanager/StoryCityPolicy.java'
BRIDGE = R / 'offline/current/java/android_story_missions/src/com/project7/localmanager/StoryMissionBridge.java'
J = R / 'toolchains/java/jdk-17.0.21+9/Contents/Home/bin'
SDK = R / 'toolchains/android-sdk/platforms/android-32/android.jar'
JSONJAR = R / 'toolchains/json-20240303.jar'

FREEZE = {
    'assets/event_graph.tsv': '50d211e2108524dbce10e9babf9de77cf9faf9e331f8a70f8d1a8f6d771f927f',
    'assets/project7_story_city/catalog-v1.json.gz': 'af2328b97372c27fd392b5b399d03daa17fa73acdd35d2b1ad5b0a8f07218069',
    'assets/project7_story_city_virtual/virtual-data-v1.json': '83fae3199e308db88513f4a6e6bf6af2288ca749258e3d81b5c81451f8fec6de',
    'assets/suppression.tsv': '574d8c7e63a4ce648705b3f4d1cfbfced9e30fbf9cfd513cb09138290812bc86',
    'assets/economy.tsv': '44ff1083dee5021acf5e673acf92d4e2074e25db394e5dfba44b4c3ee38f0564',
    'assets/project7_story_shared/special-selector-v1.json': CATALOG_PIN,
}


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def rel(path):
    path = Path(path).resolve()
    try:
        return str(path.relative_to(R))
    except ValueError:
        return str(path)


def tree(root):
    root = Path(root)
    digest = hashlib.sha256()
    count = 0
    for path in sorted(p for p in root.rglob('*') if p.is_file()):
        digest.update(path.relative_to(root).as_posix().encode('utf-8'))
        digest.update(b'\0')
        digest.update(bytes.fromhex(sha(path)))
        digest.update(b'\n')
        count += 1
    return {'files': count, 'sha256': digest.hexdigest()}


assert OWN.is_dir() and (OWN / 'com/project7/localmanager/StoryMissionBridge.class').is_file()
MAIN_CLASSES = sorted(OWN.rglob('*.class'))
assert MAIN_CLASSES, 'production class directory is empty'
assert sha(FRAME) == FRAME_PIN, 'v41 frame pin changed'
assert sha(CATALOG) == CATALOG_PIN and sha(ENTRY) == ENTRY_PIN
for name, digest in FREEZE.items():
    assert sha(STAGE_ASSETS / name.split('assets/', 1)[1]) == digest, f'v41 stage asset changed: {name}'
SHARED = '\n'.join(p.read_text(encoding='utf-8') for p in sorted((H / 'src').rglob('*.java')))
assert 'StoryCityCocPolicy' not in SHARED and 'Project7StoryCityHook' not in SHARED, \
    'menu10 policy must stay independent of the COC hook/patch'

BEFORE = {
    'production_classes': {'path': rel(OWN), 'count': len(MAIN_CLASSES), **tree(OWN)},
    'stage_assets': tree(STAGE_ASSETS),
    'frame_jar': sha(FRAME),
    'shared_source': tree(H / 'src'),
    'catalog': sha(CATALOG),
    'entry_catalog': sha(ENTRY),
    'story_city_source': sha(CITY),
    'story_mission_bridge_source': sha(BRIDGE),
    'verify_gateway_py': sha(Path(__file__).resolve()),
}

B = Path(tempfile.mkdtemp(prefix='menu10-gateway-host-', dir=R / 'analysis/project7'))
for name in ('api', 'storycity', 'bridge', 'shared', 'platform', 'tests', 'assets'):
    (B / name).mkdir()


def run(*args):
    process = subprocess.run(list(map(str, args)), capture_output=True, text=True)
    assert process.returncode == 0, process.stdout + process.stderr
    return process.stdout + process.stderr


# The frozen v43 production classes are the runtime. The frozen manager frame supplies the real consumers. The reviewed owners are
# rebuilt from source; the Bridge class must stay byte-identical to v41 and the
# only packaged diffs are the scoped menu10 entry/city policy classes. Narrow
# host-only stubs add members omitted by the production compile API and never
# enter B/shared or the runtime classpath.
(B / 'stubs/com/project7/localmanager').mkdir(parents=True)
(B / 'stubs/com/project7/localmanager/LocalWeekCatalog.java').write_text(
    'package com.project7.localmanager;\n'
    'import java.util.*;\n'
    'final class LocalWeekCatalog { final Map<Integer,Integer> entrances = new HashMap<>(); }\n')
(B / 'stubs/com/project7/localmanager/LocalWeekEngine.java').write_text(
    'package com.project7.localmanager;\n'
    'final class LocalWeekEngine { static LocalResourceEngine.Result apply(byte[]p,LocalWeekCatalog c,'
    'LocalTutorialStore.Progress s,String m,byte[]a){return null;} static boolean canEnter(byte[]p,'
    'LocalWeekCatalog c,int r){return false;} }\n')
(B / 'stubs/com/project7/localmanager/LocalEventCatalog.java').write_text(
    'package com.project7.localmanager;\n'
    'import android.content.Context; import java.io.*; import java.util.*;\n'
    'final class LocalEventCatalog { final Map<Integer,byte[]> cityEffects=new HashMap<>();\n'
    ' static final class Event { boolean release; } Event get(int e){return null;}\n'
    ' Set<Integer> mutex(int e){return Collections.emptySet();}\n'
    ' LocalEventCatalog(Context c)throws IOException{} LocalEventCatalog(InputStream in)throws IOException{} }\n')
run(J / 'javac', '--release', '8', '-cp', ':'.join(map(str, [COMPILE_API, JSONJAR, SDK])),
    '-d', B / 'api', *sorted((B / 'stubs/com/project7/localmanager').glob('*.java')))
run(J / 'javac', '--release', '8',
    '-cp', ':'.join(map(str, [B / 'api', COMPILE_API, JSONJAR, SDK])),
    '-d', B / 'shared', BRIDGE, *H.glob('src/**/*.java'), CITY)
IDENTITY = {}
for name, frozen in (('StoryMissionBridge.class', True),
                     ('StoryMenuShared.class', True),
                     ('StoryMenu10Policy.class', True),
                     ('StoryMenuEntryData.class', True),
                     ('StoryCityPolicy.class', True)):
    packaged = OWN / 'com/project7/localmanager' / name
    rebuilt = B / 'shared/com/project7/localmanager' / name
    assert packaged.is_file() and rebuilt.is_file(), name
    same = sha(packaged) == sha(rebuilt)
    assert same == frozen, f'{name} packaged identity expected frozen={frozen}'
    IDENTITY[name] = {'frozen': frozen, 'packaged': sha(packaged), 'reviewed': sha(rebuilt)}

run(J / 'javac', '--release', '8', '-d', B / 'platform',
    *[x for x in R.glob('offline/current/java/android_core_rpc/host_stubs/**/*.java')
      if x.name not in ('AssetManager.java', 'Os.java')],
    *R.glob('offline/current/java/android_baiye_transactions/host_tests/android/**/*.java'),
    R / 'offline/current/java/android_week_reset/host_tests/android/system/Os.java')
COMPILE_CP = [B / 'tests', B / 'shared', B / 'platform', FRAME, OWN, JSONJAR, SDK]
run(J / 'javac', '--release', '8', '-cp', ':'.join(map(str, COMPILE_CP)), '-d', B / 'tests',
    *H.glob('host_tests/com/**/*.java'))

# Frozen v41 assets are hardlinked; only the reviewed entry asset is overlaid.
for path in Path(STAGE_ASSETS).rglob('*'):
    target = B / 'assets' / path.relative_to(STAGE_ASSETS)
    if path.is_dir():
        target.mkdir(parents=True, exist_ok=True)
    else:
        target.parent.mkdir(parents=True, exist_ok=True)
        os.link(path, target)
entry_target = B / 'assets/project7_story_shared/menu10-entry-v1.json'
entry_target.unlink()
entry_target.write_bytes(ENTRY.read_bytes())
assert sha(entry_target) == ENTRY_PIN

CP = [B / 'tests', B / 'platform', OWN, FRAME, JSONJAR, SDK]
output = run(J / 'java', '-Xverify:all', '-cp', ':'.join(map(str, CP)),
             'com.project7.localmanager.StoryMenu10GatewayHost', B / 'assets')
match = re.search(r'^PASS (\d+) ', output, re.M)
assert match, output
CHECKS = int(match.group(1))

AFTER = {
    'production_classes': {'path': rel(OWN), 'count': len(MAIN_CLASSES), **tree(OWN)},
    'stage_assets': tree(STAGE_ASSETS),
    'frame_jar': sha(FRAME),
    'shared_source': tree(H / 'src'),
    'catalog': sha(CATALOG),
    'entry_catalog': sha(ENTRY),
    'story_city_source': sha(CITY),
    'story_mission_bridge_source': sha(BRIDGE),
    'verify_gateway_py': sha(Path(__file__).resolve()),
}
assert BEFORE == AFTER, 'gateway host changed an input'
(B / 'gateway.stdout.log').write_text(output)
print(json.dumps({
    'status': 'PASS',
    'checks': CHECKS,
    'build': rel(B),
    'main_inputs': rel(OWN),
    'main_classes': len(MAIN_CLASSES),
    'stage_assets': rel(STAGE_ASSETS),
    'frame': rel(FRAME),
    'packaged_class_identity': IDENTITY,
    'input_drift': [],
    'gateway_stdout': rel(B / 'gateway.stdout.log'),
}, indent=2, sort_keys=True))
