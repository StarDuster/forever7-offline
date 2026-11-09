"""Independent v43 raw menu10 requestEnterStory gateway evidence.

The only entry proof is the original client envelope on the fixed manager
LocalGatewayServer.handleReliableRpc; StoryMenu10Policy.enter / direct
LocalWeekEngine.apply are not used. This runner also replays the existing 255
check host unchanged, so the prior evidence remains a regression gate.

No D8/APK/native work. The manager target, translated frame and patch are
fingerprinted and must not drift during the run.
"""
from pathlib import Path
import hashlib
import json
import os
import re
import shutil
import subprocess
import tempfile

R = Path(__file__).resolve().parents[2]
H = Path(__file__).resolve().parent
INPUTS = R / 'analysis/project7/story-city-integration-prepare-v43/project7-inputs-6i2v7gq2'
OWN = INPUTS / 'compiled/production-classes'
STAGE = INPUTS / 'stage'
STAGE_ASSETS = STAGE / 'assets'
TARGET = STAGE / 'classes7.dex'
COMPILE_API = INPUTS / 'compiled/compile-api.jar'
FRAME = R / 'analysis/project7/story-city-coc-gateway-v36/manager-translated-frames.jar'
PATCH = R / 'runtime/project7_story_city_patch/seams.xor-zlib'
PRODUCER = R / 'tools/Project7StoryCityHook.java'
CATALOG = H / 'catalog/special-selector-v1.json'
CATALOG_PIN = '5b9d6b01f7fd77ed63f1f301b39ef31db4d7b8fb644383aa28aadcec000404aa'
ENTRY = H / 'catalog/menu10-entry-v1.json'
ENTRY_PIN = '4bd8602a3999f142dfbdeb97aa3330f030c54f3099bb0ed36bde444bf85f9cae'
CITY = R / 'runtime/android_story_city/src/com/project7/localmanager/StoryCityPolicy.java'
BRIDGE = R / 'runtime/android_story_missions/src/com/project7/localmanager/StoryMissionBridge.java'
J = R / 'toolchains/java/jdk-17.0.21+9/Contents/Home/bin'
SDK = R / 'toolchains/android-sdk/platforms/android-32/android.jar'
JSONJAR = R / 'toolchains/json-20240303.jar'

TARGET_PIN = 'fee369231e8924923f774cdbda4961f91b6ab87cee237b249cff8229b535f1c6'
FRAME_PIN = 'a767c656b853d40d2e8acac835eac19ec2272da8cbee112a7428637d539bbc66'
PATCH_PIN = '10a840c9f2118dec57bd7f35f12573f4fca312b92aaaf1e6d270b5904bb0736a'

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
assert len(MAIN_CLASSES) == 245, f'v42 production class count changed: {len(MAIN_CLASSES)}'
assert sha(TARGET) == TARGET_PIN, 'manager target changed'
assert sha(FRAME) == FRAME_PIN, 'manager frame changed'
assert sha(PATCH) == PATCH_PIN, 'story city patch changed'
assert sha(CATALOG) == CATALOG_PIN and sha(ENTRY) == ENTRY_PIN
for name, digest in FREEZE.items():
    assert sha(STAGE_ASSETS / name.split('assets/', 1)[1]) == digest, f'v42 stage asset changed: {name}'
SHARED = '\n'.join(p.read_text(encoding='utf-8') for p in sorted((H / 'src').rglob('*.java')))
assert 'StoryCityCocPolicy' not in SHARED and 'Project7StoryCityHook' not in SHARED, \
    'menu10 policy must stay independent of the COC hook/patch'

BEFORE = {
    'production_classes': {'path': rel(OWN), 'count': len(MAIN_CLASSES), **tree(OWN)},
    'stage_assets': tree(STAGE_ASSETS),
    'target': sha(TARGET),
    'frame_jar': sha(FRAME),
    'patch': sha(PATCH),
    'shared_source': tree(H / 'src'),
    'host_tests': tree(H / 'host_tests'),
    'catalog': sha(CATALOG),
    'entry_catalog': sha(ENTRY),
    'story_city_source': sha(CITY),
    'story_mission_bridge_source': sha(BRIDGE),
    'producer': sha(PRODUCER),
    'verify_gateway_py': sha(H / 'verify_gateway.py'),
    'verify_raw_entry_py': sha(Path(__file__).resolve()),
}

B = Path(tempfile.mkdtemp(prefix='menu10-raw-entry-', dir=R / 'analysis/project7'))
for name in ('api', 'storycity', 'bridge', 'shared', 'platform', 'tests', 'assets'):
    (B / name).mkdir()


def run(*args):
    process = subprocess.run(list(map(str, args)), capture_output=True, text=True)
    assert process.returncode == 0, process.stdout + process.stderr
    return process.stdout + process.stderr


# The frozen manager frame supplies the real consumers. Reviewed owners are
# rebuilt from source; narrow stubs only supply members omitted by the compile
# API and never enter B/shared or the runtime classpath.
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
    *[x for x in R.glob('runtime/android_core_rpc/host_stubs/**/*.java')
      if x.name not in ('AssetManager.java', 'Os.java')],
    *R.glob('runtime/android_baiye_transactions/host_tests/android/**/*.java'),
    R / 'runtime/android_week_reset/host_tests/android/system/Os.java')
COMPILE_CP = [B / 'tests', B / 'shared', B / 'platform', FRAME, OWN, JSONJAR, SDK]
run(J / 'javac', '--release', '8', '-cp', ':'.join(map(str, COMPILE_CP)), '-d', B / 'tests',
    *H.glob('host_tests/com/**/*.java'))

# Frozen v43 assets are hardlinked; only the reviewed menu10 entry asset is overlaid.
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

# Frozen v43 production classes are the runtime; rebuilt shared is compile/identity only.
CP = [B / 'tests', B / 'platform', OWN, FRAME, JSONJAR, SDK]
raw_output = run(J / 'java', '-Xverify:all', '-cp', ':'.join(map(str, CP)),
                 'com.project7.localmanager.StoryMenu10RawEntryHost', B / 'assets')
raww = re.search(r'^PASS (\d+) ', raw_output, re.M)
assert raww, raw_output
RAW_CHECKS = int(raww.group(1))
(B / 'raw-entry.stdout.log').write_text(raw_output)

old_output = run(J / 'java', '-Xverify:all', '-cp', ':'.join(map(str, CP)),
                 'com.project7.localmanager.StoryMenu10GatewayHost', B / 'assets')
oldw = re.search(r'^PASS (\d+) ', old_output, re.M)
assert oldw and int(oldw.group(1)) == 255, old_output
OLD_CHECKS = int(oldw.group(1))
(B / 'menu10-255.stdout.log').write_text(old_output)

AFTER = {
    'production_classes': {'path': rel(OWN), 'count': len(MAIN_CLASSES), **tree(OWN)},
    'stage_assets': tree(STAGE_ASSETS),
    'target': sha(TARGET),
    'frame_jar': sha(FRAME),
    'patch': sha(PATCH),
    'shared_source': tree(H / 'src'),
    'host_tests': tree(H / 'host_tests'),
    'catalog': sha(CATALOG),
    'entry_catalog': sha(ENTRY),
    'story_city_source': sha(CITY),
    'story_mission_bridge_source': sha(BRIDGE),
    'producer': sha(PRODUCER),
    'verify_gateway_py': sha(H / 'verify_gateway.py'),
    'verify_raw_entry_py': sha(Path(__file__).resolve()),
}
assert BEFORE == AFTER, 'raw entry host changed an input'

result = {
    'status': 'PASS',
    'checks': RAW_CHECKS,
    'regression_checks': OLD_CHECKS,
    'build': rel(B),
    'inputs': rel(INPUTS),
    'main_classes': len(MAIN_CLASSES),
    'target': {'path': rel(TARGET), 'sha256': sha(TARGET), 'bytes': TARGET.stat().st_size},
    'frame': {'path': rel(FRAME), 'sha256': sha(FRAME), 'bytes': FRAME.stat().st_size},
    'patch': {'path': rel(PATCH), 'sha256': sha(PATCH), 'bytes': PATCH.stat().st_size},
    'producer': {'path': rel(PRODUCER), 'sha256': sha(PRODUCER)},
    'packaged_class_identity': IDENTITY,
    'input_drift': [],
    'raw_entry_stdout': rel(B / 'raw-entry.stdout.log'),
    'menu10_255_stdout': rel(B / 'menu10-255.stdout.log'),
    'command': f'python3 {rel(Path(__file__).resolve())}',
}
EVIDENCE = R / 'reports/menu10-raw-entry-latest'
EVIDENCE.mkdir(parents=True, exist_ok=True)
for name in ('raw-entry.stdout.log', 'menu10-255.stdout.log'):
    shutil.copy2(B / name, EVIDENCE / name)
result['build'] = rel(EVIDENCE)
result['raw_entry_stdout'] = rel(EVIDENCE / 'raw-entry.stdout.log')
result['menu10_255_stdout'] = rel(EVIDENCE / 'menu10-255.stdout.log')
(EVIDENCE / 'result.json').write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
print(json.dumps(result, indent=2, sort_keys=True))
shutil.rmtree(B)
