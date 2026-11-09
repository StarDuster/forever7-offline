"""v43 menu10 continuity evidence: entry 477 through 1141/selector320/1132-1136.

Rebuilt shared sources are used only to compile the hosts and to assert byte
identity against the frozen v43 production classes. The JVM classpath that
actually runs the hosts is tests, platform, frozen production classes, frame;
the rebuilt shared directory is never overlaid at runtime.

The continuity fixture is a consistent post-ending save: original ending 30 /
event 8310 / CG 159 receipts, tutorial foundation retained by the week reset,
and the prior ending's syncAllNote delivery consumed by the original ack owner.
Current menu10 events are not seeded. Area 3 FIGHT1 comes from ordinary city
state (area-2 battle 1106) and is read back from the profile, the original
LocalCityProgress.status and the original get_all_area_info wire.
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
INPUTS = R / 'analysis/project7/story-city-integration-prepare-v48/project7-inputs-jnw7fnyr'
OWN = INPUTS / 'compiled/production-classes'
STAGE = INPUTS / 'stage'
STAGE_ASSETS = STAGE / 'assets'
TARGET = STAGE / 'classes7.dex'
COMPILE_API = INPUTS / 'compiled/compile-api.jar'
FRAME = R / 'analysis/project7/action-ledger-code20-v2/manager-translated-frames.jar'
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

TARGET_PIN = '6555e75c0a8432f78422408c0327a3d8b4593eef420bcd0bb74eb5c911665d51'
FRAME_PIN = 'f81b686eb3cfdb7e87f5c9eae5075652d08afb38c8d104ed81b3baebcb703c0f'
PATCH_PIN = '10a840c9f2118dec57bd7f35f12573f4fca312b92aaaf1e6d270b5904bb0736a'
FREEZE = {
    'assets/event_graph.tsv': '18cc690b0bb84ac33e29378f9f2aa5d32e35447da771fdf64fc86b5d449139b5',
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
assert len(MAIN_CLASSES) == 247, f'v42 production class count changed: {len(MAIN_CLASSES)}'
assert sha(TARGET) == TARGET_PIN, 'manager target changed'
assert sha(FRAME) == FRAME_PIN, 'manager frame changed'
assert sha(PATCH) == PATCH_PIN, 'story city patch changed'
assert sha(CATALOG) == CATALOG_PIN and sha(ENTRY) == ENTRY_PIN
for name, digest in FREEZE.items():
    assert sha(STAGE_ASSETS / name.split('assets/', 1)[1]) == digest, f'v42 stage asset changed: {name}'
SHARED = '\n'.join(p.read_text(encoding='utf-8') for p in sorted((H / 'src').rglob('*.java')))
assert 'StoryCityCocPolicy' not in SHARED and 'Project7StoryCityHook' not in SHARED, \
    'menu10 policy must stay independent of the COC hook/patch'
assert 'focusArea' in (H / 'src/com/project7/localmanager/StoryMenu10Policy.java').read_text()

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
}

B = Path(tempfile.mkdtemp(prefix='menu10-continuity-', dir=R / 'analysis/project7'))
for name in ('api', 'shared', 'platform', 'tests', 'assets'):
    (B / name).mkdir()


def run(*args):
    process = subprocess.run(list(map(str, args)), capture_output=True, text=True)
    assert process.returncode == 0, process.stdout + process.stderr
    return process.stdout + process.stderr


# Narrow compile-only stubs matching the frozen compile API.
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
for name, unchanged in (('StoryMissionBridge.class', True),
                        ('StoryMenuShared.class', True),
                        ('StoryMenu10Policy.class', True),
                        ('StoryMenuEntryData.class', True),
                        ('StoryCityPolicy.class', True)):
    packaged = OWN / 'com/project7/localmanager' / name
    rebuilt = B / 'shared/com/project7/localmanager' / name
    assert packaged.is_file() and rebuilt.is_file(), name
    same = sha(packaged) == sha(rebuilt)
    assert same == unchanged, f'{name} packaged identity expected unchanged={unchanged}'
    IDENTITY[name] = {'unchanged': unchanged, 'packaged': sha(packaged), 'reviewed': sha(rebuilt)}

run(J / 'javac', '--release', '8', '-d', B / 'platform',
    *[x for x in R.glob('runtime/android_core_rpc/host_stubs/**/*.java')
      if x.name not in ('AssetManager.java', 'Os.java')],
    *R.glob('runtime/android_baiye_transactions/host_tests/android/**/*.java'),
    R / 'runtime/android_week_reset/host_tests/android/system/Os.java')
COMPILE_CP = [B / 'tests', B / 'shared', B / 'platform', FRAME, OWN, JSONJAR, SDK]
run(J / 'javac', '--release', '8', '-cp', ':'.join(map(str, COMPILE_CP)), '-d', B / 'tests',
    *H.glob('host_tests/com/**/*.java'))
# Frozen production classes are the runtime; rebuilt shared is compile/identity only.
CP = [B / 'tests', B / 'platform', OWN, FRAME, JSONJAR, SDK]

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

continuity_output = run(J / 'java', '-Xverify:all', '-cp', ':'.join(map(str, CP)),
                        'com.project7.localmanager.StoryMenu10ContinuityHost', B / 'assets', OWN)
match = re.search(r'^PASS (\d+) ', continuity_output, re.M)
assert match, continuity_output
CONTINUITY_CHECKS = int(match.group(1))
(B / 'continuity.stdout.log').write_text(continuity_output)

raw_output = run(J / 'java', '-Xverify:all', '-cp', ':'.join(map(str, CP)),
                 'com.project7.localmanager.StoryMenu10RawEntryHost', B / 'assets')
raww = re.search(r'^PASS (\d+) ', raw_output, re.M)
assert raww and int(raww.group(1)) == 182, raw_output
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
}
assert BEFORE == AFTER, 'continuity host changed an input'

EVIDENCE = R / 'reports/menu10-continuity-latest'
EVIDENCE.mkdir(parents=True, exist_ok=True)
for name in ('continuity.stdout.log', 'raw-entry.stdout.log', 'menu10-255.stdout.log'):
    shutil.copy2(B / name, EVIDENCE / name)

result = {
    'status': 'PASS',
    'continuity_checks': CONTINUITY_CHECKS,
    'raw_entry_checks': RAW_CHECKS,
    'gateway_checks': OLD_CHECKS,
    'inputs': rel(INPUTS),
    'build': rel(EVIDENCE),
    'main_classes': len(MAIN_CLASSES),
    'target': {'path': rel(TARGET), 'sha256': sha(TARGET)},
    'frame': {'path': rel(FRAME), 'sha256': sha(FRAME)},
    'patch': {'path': rel(PATCH), 'sha256': sha(PATCH)},
    'packaged_class_identity': IDENTITY,
    'input_drift': [],
    'production_fix': 'none at runtime: the frozen v43 production classes are used '
                      'unchanged; rebuilt shared classes are compile/identity only',
    'helper_scope': {
        'focusArea': 'host-facing wrapper over the existing Gateway updateEventCondClient; '
                     'no production caller',
        'complete1140': 'host-facing; this chain completes 1141 first, so the original '
                        'prerequisites would also hold; no production caller',
        'q7CompleteUiEvent': 'existing Project7 client-compat RPC, not an original-client RPC',
    },
    'test_adapter_corrections': [
        'entry payload is the original {i,o}; startEvent/clientTrace are original RPCs',
        'q7CompleteUiEvent is the existing Project7 client-compat RPC, not original-client',
        'before entry, the prior ending syncAllNote delivery is consumed by the original '
        'LocalProfileStore q7AckStoryDelivery owner',
        'area3 FIGHT1 is formed by the real Gateway ordinary area-2 stage admission/'
        'settlement chain ending at trace 1106; real getAreaStagesRequest returns the '
        'stage and LocalCityProgress.status agrees before focus',
    ],
    'fixture_prerequisites': [
        'captured post-settlement save: frozen weeks.tsv row 8310 -> ending30/CG159 '
        'supplies std.ed=[30], cgs=[159], q7EndingEvents 8310, baseline [8310], '
        'q7WeekCgBaseline [159]',
        'the prior ending one-shot syncAllNote delivery is consumed by the original '
        'LocalProfileStore q7AckStoryDelivery owner before entry',
        'tutorial foundation 1013/1043 retained by the original week reset',
        'ordinary city progression is driven through the real Gateway stage owner, '
        'not written into progress/profile',
        'no current menu10 event (477/478/479/1129/480/1140/1141) is seeded',
    ],
    'prior_ending_evidence': {
        'week_row': 8310,
        'ending': 30,
        'cg': 159,
        'delivery_ack': 'LocalProfileStore.updateServices q7AckStoryDelivery',
    },
    'runtime_classpath': 'tests, platform, frozen production classes, frame (no rebuilt shared overlay)',
    'continuity_stdout': rel(EVIDENCE / 'continuity.stdout.log'),
    'raw_entry_stdout': rel(EVIDENCE / 'raw-entry.stdout.log'),
    'gateway_stdout': rel(EVIDENCE / 'menu10-255.stdout.log'),
    'command': f'python3 {rel(Path(__file__).resolve())}',
}
(EVIDENCE / 'result.json').write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
print(json.dumps(result, indent=2, sort_keys=True))
shutil.rmtree(B)
