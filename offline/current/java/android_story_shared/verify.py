"""Finite host verification for menu10 entry readiness and selector11 continuation.

Compiles the reviewed non-COC owners (StoryMissionBridge, the shared mechanism,
StoryCityPolicy) and drives the frozen v41 stage assets and manager frame. The
original manager frame supplies Store/event/city/week consumers. No D8, APK,
native, player file or COC file is written. menu10 is the only new entry;
menu12 remains disabled.
"""
from pathlib import Path
import argparse
import atexit
import base64
import gzip
import hashlib
import json
import os
import re
import shutil
import subprocess
import tempfile

R = Path(__file__).resolve().parents[4]
H = Path(__file__).resolve().parent
PARSER = argparse.ArgumentParser()
PARSER.add_argument('--keep-build', action='store_true',
                    help='Keep generated classes, copied assets and scratch profiles for debugging')
PARSER.add_argument('--inputs', type=Path,
                    default=R / 'analysis/project7/story-city-integration-prepare-v41/project7-inputs-7ptsklbq/compiled/production-classes',
                    help='Current Main compiled production-classes directory')
ARGS = PARSER.parse_args()
OWN = ARGS.inputs.expanduser().resolve()
if (OWN / 'production-classes').is_dir() and not (OWN / 'com/project7/localmanager').is_dir():
    OWN = OWN / 'production-classes'
assert (OWN / 'com/project7/localmanager/StoryMissionBridge.class').is_file(), f'Main story bridge missing: {OWN}'

FRAME = R / 'analysis/project7/story-city-coc-gateway-v36/manager-translated-frames.jar'
FRAME_PIN = 'a767c656b853d40d2e8acac835eac19ec2272da8cbee112a7428637d539bbc66'
CATALOG = H / 'catalog/special-selector-v1.json'
CATALOG_PIN = '5b9d6b01f7fd77ed63f1f301b39ef31db4d7b8fb644383aa28aadcec000404aa'
ENTRY = H / 'catalog/menu10-entry-v1.json'
ENTRY_PIN = '4bd8602a3999f142dfbdeb97aa3330f030c54f3099bb0ed36bde444bf85f9cae'
V41_ASSETS = R / 'analysis/project7/story-city-integration-prepare-v41/project7-inputs-7ptsklbq/stage/assets'
EVENT_GRAPH = V41_ASSETS / 'event_graph.tsv'
WEEKS = V41_ASSETS / 'weeks.tsv'
CITY = R / 'offline/current/java/android_story_city/src/com/project7/localmanager/StoryCityPolicy.java'
BRIDGE = R / 'offline/current/java/android_story_missions/src/com/project7/localmanager/StoryMissionBridge.java'
J = R / 'toolchains/java/jdk-17.0.21+9/Contents/Home/bin'
SDK = R / 'toolchains/android-sdk/platforms/android-32/android.jar'
JSONJAR = R / 'toolchains/json-20240303.jar'
COMPILE_API = R / 'analysis/project7/story-city-integration-prepare-v41/project7-inputs-7ptsklbq/compiled/compile-api.jar'
BASE_ASSETS = V41_ASSETS
MISSION_CATALOG = V41_ASSETS / 'project7_story_missions/catalog-v1.tsv'
CITY_CATALOG = V41_ASSETS / 'project7_story_city/catalog-v1.json.gz'
VIRTUAL = V41_ASSETS / 'project7_story_city_virtual/virtual-data-v1.json'
MAIN_CLASSES = sorted(OWN.rglob('*.class'))
assert MAIN_CLASSES, f'current Main class directory is empty: {OWN}'


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
        name = path.relative_to(root).as_posix()
        digest.update(name.encode('utf-8')); digest.update(b'\0')
        digest.update(bytes.fromhex(sha(path))); digest.update(b'\n')
        count += 1
    return {'files': count, 'sha256': digest.hexdigest()}


CATALOG_DATA = json.loads(CATALOG.read_text(encoding='utf-8'))


def _plain(value):
    if isinstance(value, dict):
        return {str(k): _plain(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_plain(v) for v in value]
    return value


def _original_table(path):
    src = re.sub(r'(?m)^return\s*$', 'pass', Path(path).read_text(encoding='utf-8'))
    ns = {'__name__': 'original_640'}
    exec(compile(src, str(path), 'exec'), ns)
    return ns['data']


CHAPTER = R / 'analysis/original-py-640/com/data/cdata/chapter_mission_data.py'
MISSION = R / 'analysis/original-py-640/com/data/cdata/mission.py'
EVENT_CONTENT = R / 'analysis/decompiled/event_content.py'
ORIGINAL_ROW = _plain(dict(_original_table(CHAPTER)[(6, 0, '10-6', 11)]))
ORIGINAL_MISSION = _plain(dict(_original_table(MISSION)[320]))
ORIGINAL_1140 = _original_table(EVENT_CONTENT)[1140]
assert ORIGINAL_ROW == CATALOG_DATA['selector']['row'], 'selector row is not the original 640 row'
assert ORIGINAL_MISSION == CATALOG_DATA['missions']['320'], 'mission320 is not the original 640 row'
assert ORIGINAL_1140['release'] is True and list(ORIGINAL_1140['areaFight']) == [6] and \
    dict(ORIGINAL_1140['areaSpecialStage']) == {6: 11}, '1140 occurrence is not the original row'
for name, path in (('chapter_mission_data', CHAPTER), ('mission', MISSION),
                   ('event_content', EVENT_CONTENT)):
    assert CATALOG_DATA['source']['sha256'][name] == sha(path), f'catalog provenance changed: {name}'

ENTRY_DATA = json.loads(ENTRY.read_text(encoding='utf-8'))
assert sha(ENTRY) == ENTRY_PIN, 'menu10 entry asset pin changed'
assert ENTRY_DATA['schema'] == 'project7-menu10-entry-v1' and ENTRY_DATA['menu'] == 10
assert ENTRY_DATA['entry']['open'] is True, 'menu10 scoped entry must be ready'
assert ENTRY_DATA['entry']['allowlist'] == 'LocalStoryEntryPolicy.SUPPORTED'
assert 'menu12' in ENTRY_DATA['entry']['reason'], 'menu12 must stay disabled'
assert ENTRY_DATA['entry']['preconditions'] and ENTRY_DATA['gaps']['entry']
assert ENTRY_DATA['rows']['chapter_selector']['row'] == ORIGINAL_ROW, 'entry selector row changed'
assert ENTRY_DATA['rows']['missions']['320'] == ORIGINAL_MISSION, 'entry mission320 changed'
assert ENTRY_DATA['rows']['mission_sha256']['320'] == CATALOG_DATA['mission_sha256']['320']
ORIGINAL_EVENTS = _original_table(EVENT_CONTENT)
for event in (1129, 1132, 1140, 1141):
    assert ENTRY_DATA['rows']['events'][str(event)] == _plain(dict(ORIGINAL_EVENTS[event])), \
        f'entry event row changed: {event}'
ORIGINAL_CITY = _original_table(R / 'analysis/original-py-640/com/data/cdata/city_data.py')[6]
assert ENTRY_DATA['rows']['city_area']['6'] == {k: _plain(ORIGINAL_CITY[k]) for k in
    ('id', 'name', 'show_build', 'show_upgrade', 'show_patrol', 'area_require')}, 'entry area6 changed'
ECONOMY = R / 'analysis/project7/manager/assets/economy.tsv'
assert ENTRY_DATA['rows']['economy']['tsv'] == next(
    line for line in ECONOMY.read_text(encoding='utf-8').splitlines() if line.startswith('M\t320\t'))
MISSION_ROWS = [line.split('\t') for line in MISSION_CATALOG.read_text(encoding='utf-8').splitlines()]
assert ENTRY_DATA['inventory']['p7_mission_catalog_area6_chapter_rows'] == sum(
    1 for row in MISSION_ROWS if row[:2] == ['C', '6']), 'area6 mission-catalog inventory changed'
assert ENTRY_DATA['inventory']['p7_mission_catalog_mission320'] == any(
    row[0] == 'A' and row[1] == '320' for row in MISSION_ROWS if len(row) > 2), \
    'mission320 mission-catalog inventory changed'
CITY_DATA = json.loads(gzip.open(CITY_CATALOG, 'rt', encoding='utf-8').read())
assert ENTRY_DATA['inventory']['p7_city_catalog_area6_chapters'] == sorted(
    row['route'] for row in CITY_DATA['chapters'] if row['area'] == 6), 'area6 city chapters changed'
assert ENTRY_DATA['inventory']['p7_city_catalog_effect1140'] == ('1140' in CITY_DATA['effects'])
assert ENTRY_DATA['inventory']['p7_city_catalog_effect1132'] == ('1132' in CITY_DATA['effects'])
GRAPH_ROWS = [line.split('\t') for line in EVENT_GRAPH.read_text(encoding='utf-8').splitlines()
              if line.startswith('@cityEffect\t1140\t')]
assert len(GRAPH_ROWS) == 1, 'manager event graph lost the 1140 city effect'
GRAPH_PAYLOAD = base64.b64decode(GRAPH_ROWS[0][2])
assert b'areaFight' in GRAPH_PAYLOAD and b'areaSpecialStage' not in GRAPH_PAYLOAD
assert ENTRY_DATA['inventory']['manager_event_graph_1140_areaFight'] == \
    ENTRY_DATA['rows']['events']['1140']['areaFight']
assert ENTRY_DATA['inventory']['manager_event_graph_1140_areaSpecialStage'] is None

SHARED_TEXT = '\n'.join(p.read_text(encoding='utf-8') for p in sorted((H / 'src').rglob('*.java')))
assert 'SUPPORTED.add' not in SHARED_TEXT and 'SUPPORTED.remove' not in SHARED_TEXT \
    and 'SUPPORTED =' not in SHARED_TEXT, \
    'shared mechanism must not mutate the original entry allowlist'
assert 'StoryCityCocPolicy' not in SHARED_TEXT and 'Project7StoryCityHook' not in SHARED_TEXT, \
    'shared mechanism must stay independent of COC hook/patch'

BEFORE = {
    'frames_jar': sha(FRAME),
    'main_classes': {'path': rel(OWN), **tree(OWN)},
    'shared_source': tree(H / 'src'),
    'host_tests': tree(H / 'host_tests'),
    'catalog': sha(CATALOG),
    'entry_catalog': sha(ENTRY),
    'event_graph': sha(EVENT_GRAPH),
    'weeks': sha(WEEKS),
    'mission_catalog': sha(MISSION_CATALOG),
    'original_chapter_mission_data': sha(CHAPTER),
    'original_mission': sha(MISSION),
    'original_event_content': sha(EVENT_CONTENT),
    'story_city_source': sha(CITY),
    'story_mission_bridge_source': sha(BRIDGE),
    'verify_py': sha(Path(__file__).resolve()),
}
assert BEFORE['frames_jar'] == FRAME_PIN, 'frame jar pin changed'
assert BEFORE['catalog'] == CATALOG_PIN, 'shared catalog pin changed'
assert BEFORE['entry_catalog'] == ENTRY_PIN, 'menu10 entry catalog pin changed'

B = Path(tempfile.mkdtemp(prefix='menu-shared-host-', dir=R / 'analysis/project7'))


def cleanup_generated():
    """Keep compact evidence, not a fresh copy of game assets per host run."""
    if ARGS.keep_build:
        return
    for name in ('api', 'storycity', 'bridge', 'shared', 'platform', 'tests',
                 'assets', 'scratch1', 'scratch2'):
        shutil.rmtree(B / name, ignore_errors=True)


atexit.register(cleanup_generated)
for n in ('api', 'storycity', 'bridge', 'shared', 'platform', 'tests', 'assets', 'scratch1', 'scratch2'):
    (B / n).mkdir()


def run(*args):
    p = subprocess.run(list(map(str, args)), capture_output=True, text=True)
    assert p.returncode == 0, p.stdout + p.stderr
    return p.stdout + p.stderr


# The frozen manager frame supplies the real package-private consumers. Three
# narrow host-only stubs add members that the production compile API omits
# (LocalWeekCatalog.entrances, LocalWeekEngine.canEnter and the event catalog
# InputStream constructor); they never enter B/shared or the runtime classpath.
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
PACKAGED_IDENTITY = {}
for name, frozen in (('StoryMissionBridge.class', True),
                     ('StoryMenuShared.class', True),
                     ('StoryMenu10Policy.class', False),
                     ('StoryMenuEntryData.class', False),
                     ('StoryCityPolicy.class', False)):
    packaged = OWN / 'com/project7/localmanager' / name
    rebuilt = B / 'shared/com/project7/localmanager' / name
    assert packaged.is_file() and rebuilt.is_file(), name
    same = sha(packaged) == sha(rebuilt)
    assert same == frozen, f'{name} packaged identity expected frozen={frozen}'
    PACKAGED_IDENTITY[name] = {'frozen': frozen, 'packaged': sha(packaged), 'reviewed': sha(rebuilt)}
run(J / 'javac', '--release', '8', '-d', B / 'platform',
    *[x for x in R.glob('offline/current/java/android_core_rpc/host_stubs/**/*.java') if x.name not in ('AssetManager.java', 'Os.java')],
    *R.glob('offline/current/java/android_baiye_transactions/host_tests/android/**/*.java'),
    R / 'offline/current/java/android_week_reset/host_tests/android/system/Os.java')
RUNTIME_CP = [B / 'tests', B / 'shared', B / 'platform', FRAME, OWN, JSONJAR, SDK]
run(J / 'javac', '--release', '8', '-cp', ':'.join(map(str, RUNTIME_CP)), '-d', B / 'tests',
    *H.glob('host_tests/com/**/*.java'))

def linktree(source, target):
    for path in Path(source).rglob('*'):
        out = Path(target) / path.relative_to(source)
        if path.is_dir():
            out.mkdir(parents=True, exist_ok=True)
        else:
            out.parent.mkdir(parents=True, exist_ok=True)
            os.link(path, out)


def override(sub, src, name):
    target = B / 'assets' / sub / name
    if target.exists() or target.is_symlink():
        target.unlink()
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(Path(src, name).read_bytes())


linktree(BASE_ASSETS, B / 'assets')
for sub, src, name in [
    ('project7_story_city', CITY_CATALOG.parent, CITY_CATALOG.name),
    ('project7_story_city_virtual', VIRTUAL.parent, VIRTUAL.name),
    ('project7_story_missions', MISSION_CATALOG.parent, MISSION_CATALOG.name),
    ('project7_story_shared', CATALOG.parent, CATALOG.name),
    ('project7_story_shared', ENTRY.parent, ENTRY.name),
]:
    override(sub, src, name)
override('.', EVENT_GRAPH.parent, EVENT_GRAPH.name)
override('.', WEEKS.parent, WEEKS.name)

shared_out = run(J / 'java', '-Xverify:all', '-cp', ':'.join(map(str, RUNTIME_CP)),
                 'com.project7.localmanager.StoryMenuSharedHost', B / 'assets', B / 'scratch1')
prod_out = run(J / 'java', '-Xverify:all', '-cp', ':'.join(map(str, RUNTIME_CP)),
               'com.project7.localmanager.StoryMenuProductionHost', B / 'assets', B / 'scratch2')
entry_out = run(J / 'java', '-Xverify:all', '-cp', ':'.join(map(str, RUNTIME_CP)),
                'com.project7.localmanager.StoryMenuEntryHost', B / 'assets')
shared_match = re.search(r'^PASS (\d+) ', shared_out, re.M)
prod_match = re.search(r'^PASS (\d+) ', prod_out, re.M)
entry_match = re.search(r'^PASS (\d+) ', entry_out, re.M)
assert shared_match and prod_match and entry_match, shared_out + '\n' + prod_out + '\n' + entry_out
CHECKS = int(shared_match.group(1))
PRODUCTION_CHECKS = int(prod_match.group(1))
ENTRY_CHECKS = int(entry_match.group(1))

AFTER = {
    'frames_jar': sha(FRAME),
    'main_classes': {'path': rel(OWN), **tree(OWN)},
    'shared_source': tree(H / 'src'),
    'host_tests': tree(H / 'host_tests'),
    'catalog': sha(CATALOG),
    'entry_catalog': sha(ENTRY),
    'event_graph': sha(EVENT_GRAPH),
    'weeks': sha(WEEKS),
    'mission_catalog': sha(MISSION_CATALOG),
    'original_chapter_mission_data': sha(CHAPTER),
    'original_mission': sha(MISSION),
    'original_event_content': sha(EVENT_CONTENT),
    'story_city_source': sha(CITY),
    'story_mission_bridge_source': sha(BRIDGE),
    'verify_py': sha(Path(__file__).resolve()),
}
if BEFORE != AFTER:
    drift = {k: [BEFORE.get(k), AFTER.get(k)] for k in set(BEFORE) | set(AFTER) if BEFORE.get(k) != AFTER.get(k)}
    (B / 'input-drift.json').write_text(json.dumps(drift, indent=2, sort_keys=True) + '\n')
    raise SystemExit(f'input drift after execution: {json.dumps(drift, sort_keys=True)}')
(B / 'shared.stdout.log').write_text(shared_out)
(B / 'production.stdout.log').write_text(prod_out)
(B / 'entry.stdout.log').write_text(entry_out)
print(json.dumps({
    'status': 'PASS',
    'checks': CHECKS,
    'production_checks': PRODUCTION_CHECKS,
    'entry_checks': ENTRY_CHECKS,
    'total_checks': CHECKS + PRODUCTION_CHECKS + ENTRY_CHECKS,
    'build': rel(B),
    'main_inputs': rel(OWN),
    'main_classes': len(MAIN_CLASSES),
    'input_sha256': BEFORE,
    'input_drift': [],
    'packaged_class_identity': PACKAGED_IDENTITY,
    'shared_stdout': rel(B / 'shared.stdout.log'),
    'production_stdout': rel(B / 'production.stdout.log'),
}, indent=2, sort_keys=True))
