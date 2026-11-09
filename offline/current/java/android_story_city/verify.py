"""Finite original JVM consumers; no Android runtime, D8, APK, or player files.

--inputs points at the current Main compiled production-classes directory (or its
parent ``compiled`` directory). Every input byte is fingerprinted before and after
execution; any drift fails the run. Compile-only descriptors are never on the
runtime classpath. Product data comes from runtime/; analysis is read-only host
evidence for the fixed manager event graph and stage assets.
"""
from pathlib import Path
import argparse, hashlib, json, re, shutil, subprocess, sys, tempfile

R = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(R))
from project7_story_city_suppression import EXTENDED_SHA256 as CITY_SUPPRESSION_EXTENDED_SHA, EXTRA_SHA256 as CITY_SUPPRESSION_SHA, extend_asset as extend_city_suppression

H = Path(__file__).resolve().parent
MANAGER_PIN = 'fee369231e8924923f774cdbda4961f91b6ab87cee237b249cff8229b535f1c6'
FRAME_PIN = 'a767c656b853d40d2e8acac835eac19ec2272da8cbee112a7428637d539bbc66'
FRAMES = {
    'core': (R/'analysis/project7/story-city-hook-v1/manager-translated-frames.jar', 'ade6df097e24be3a7514157f2999cd4e32975a26251a817ffc19b869637412e9'),
    'union': (R/'analysis/project7/story-city-coc-gateway-v1/manager-translated-frames.jar', 'a767c656b853d40d2e8acac835eac19ec2272da8cbee112a7428637d539bbc66'),
}
DEFAULT_INPUTS = R/'analysis/project7/wish-ui-full-prepare-v1/project7-inputs-h72zx6uo/compiled/production-classes'
BASE_ASSETS = R/'analysis/project7/wish-ui-full-prepare-v1/project7-inputs-h72zx6uo/stage/assets'
PARSER = argparse.ArgumentParser()
PARSER.add_argument('--inputs', type=Path, default=DEFAULT_INPUTS, help='Current Main compiled production-classes or compiled directory')
PARSER.add_argument('--frame', choices=sorted(FRAMES), default='union', help='core-only or union (gateway query seam) candidate frame')
ARGS = PARSER.parse_args()
OWN = ARGS.inputs.expanduser().resolve()
if (OWN/'production-classes').is_dir() and not (OWN/'com/project7/localmanager').is_dir():
    OWN = OWN/'production-classes'
assert (OWN/'com/project7/localmanager/EventResetWeekPolicy.class').is_file(), f'Main week-reset class missing: {OWN}'
assert (OWN/'com/project7/localmanager/StoryMissionBridge.class').is_file(), f'Main story bridge missing: {OWN}'
MAIN_CLASSES = sorted(OWN.rglob('*.class'))
assert len(MAIN_CLASSES) == 236, f'current Main class count changed: {len(MAIN_CLASSES)}'
J = R/'toolchains/java/jdk-17.0.21+9/Contents/Home/bin'
SDK = R/'toolchains/android-sdk/platforms/android-32/android.jar'
JSON = R/'toolchains/json-20240303.jar'
M, FRAMES_JAR_PIN = FRAMES[ARGS.frame]
CATALOG = R/'offline/current/data/project7_story_city_catalog/catalog-v1.json.gz'
CATALOG_CONTRACT = R/'offline/current/data/project7_story_city_catalog/contract-v1.json'
CATALOG_ECONOMY = R/'offline/current/data/project7_story_city_catalog/economy-extra.tsv'
VIRTUAL = R/'offline/current/data/project7_story_city_virtual/virtual-data-v1.json'
VIRTUAL_CONTRACT = R/'offline/current/data/project7_story_city_virtual/contract-v1.json'
CATALOG_SUPPRESSION = R/'offline/current/data/project7_story_city_catalog/suppression-extra.tsv'
MISSION = R/'offline/current/data/project7_story_mission_catalog/catalog-v1.tsv'
EVENT_GRAPH = R/'analysis/project7/manager/assets/event_graph.tsv'
WEEKS = R/'analysis/project7/manager/assets/weeks.tsv'
PREFLIGHT = R/'analysis/project7/wish-ui-full-prepare-v1/read-only-preflight-result.json'
BAIYE = {
    'catalog': R/'offline/current/data/project7_baiye_catalog/catalog-v1.tsv',
    'fragments': R/'offline/current/data/project7_baiye_catalog/fragments-v1.tsv',
    'shop': R/'offline/current/data/project7_baiye_shop_catalog/catalog-v1.tsv',
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
        name = path.relative_to(root).as_posix()
        file_digest = sha(path)
        digest.update(name.encode('utf-8')); digest.update(b'\0')
        digest.update(bytes.fromhex(file_digest)); digest.update(b'\n')
        count += 1
    return {'files': count, 'sha256': digest.hexdigest()}


def fingerprints():
    return {
        'main_classes': {'path': rel(OWN), **tree(OWN)},
        'main_compile_inputs': sha(OWN.parent/'compile-inputs.json') if (OWN.parent/'compile-inputs.json').is_file() else None,
        'frames_jar': sha(M),
        'story_city_catalog': sha(CATALOG),
        'story_city_catalog_contract': sha(CATALOG_CONTRACT),
        'story_city_catalog_economy': sha(CATALOG_ECONOMY),
        'story_city_catalog_suppression': sha(CATALOG_SUPPRESSION),
        'story_city_virtual': sha(VIRTUAL),
        'story_city_virtual_contract': sha(VIRTUAL_CONTRACT),
        'story_mission_catalog': sha(MISSION),
        'manager_event_graph': sha(EVENT_GRAPH),
        'manager_weeks': sha(WEEKS),
        'story_mission_bridge_source': tree(R/'offline/current/java/android_story_missions/src'),
        'platform_host_stubs': {
            'core': tree(R/'offline/current/java/android_core_rpc/host_stubs'),
            'baiye_android': tree(R/'offline/current/java/android_baiye_transactions/host_tests/android'),
            'os': sha(R/'offline/current/java/android_week_reset/host_tests/android/system/Os.java'),
        },
        'toolchain': {
            'javac': sha(J/'javac'),
            'java': sha(J/'java'),
            'android_jar': sha(SDK),
            'json_jar': sha(JSON),
        },
        'policy_source': tree(H/'src'),
        'compile_stubs': tree(H/'compile_stubs'),
        'host_tests': tree(H/'host_tests'),
        'verify_py': sha(Path(__file__).resolve()),
    }


BEFORE = fingerprints()
assert BEFORE['frames_jar'] == FRAMES_JAR_PIN, 'Story city frame jar pin changed'
assert BEFORE['story_city_catalog'] == 'af2328b97372c27fd392b5b399d03daa17fa73acdd35d2b1ad5b0a8f07218069', 'story city catalog pin changed'
assert BEFORE['story_city_virtual'] == '83fae3199e308db88513f4a6e6bf6af2288ca749258e3d81b5c81451f8fec6de', 'story city virtual data pin changed'
assert BEFORE['story_city_catalog_suppression'] == CITY_SUPPRESSION_SHA, 'story city COC suppression pin changed'
import gzip
CATALOG_DATA = json.loads(gzip.decompress(CATALOG.read_bytes()))
assert len(CATALOG_DATA['areas']) == 13, 'catalog area count changed'
assert len(CATALOG_DATA['chapters']) == 46, 'catalog chapter count changed'
assert len(CATALOG_DATA['missions']) == 25, 'catalog mission count changed'
assert all(str(scene) in CATALOG_DATA['missions'] and CATALOG_DATA['missions'][str(scene)]['party'] == [135] for scene in (482, 483, 484, 485, 486, 487, 488)), 'COC mission rows changed'
VIRTUAL_DATA = json.loads(VIRTUAL.read_bytes())
assert [int(m['key']) for m in VIRTUAL_DATA['missions']] == [482, 483, 484, 485, 486, 487, 488], 'virtual COC order changed'
B = Path(tempfile.mkdtemp(prefix='story-city-host-', dir=R/'analysis/project7'))


def run(*a):
    p = subprocess.run(list(map(str, a)), capture_output=True, text=True)
    assert p.returncode == 0, p.stdout + p.stderr
    return p.stdout + p.stderr


for n in ('api', 'production', 'bridge', 'platform', 'tests', 'assets'):
    (B/n).mkdir()
shutil.copytree(BASE_ASSETS, B/'assets', dirs_exist_ok=True)
for sub, src, name in [
    ('project7_story_city', R/'offline/current/data/project7_story_city_catalog', 'catalog-v1.json.gz'),
    ('project7_story_city_virtual', R/'offline/current/data/project7_story_city_virtual', 'virtual-data-v1.json'),
    ('project7_story_missions', R/'offline/current/data/project7_story_mission_catalog', 'catalog-v1.tsv'),
]:
    (B/'assets'/sub).mkdir(parents=True, exist_ok=True)
    shutil.copy(src/name, B/'assets'/sub/name)
shutil.copy(EVENT_GRAPH, B/'assets/event_graph.tsv')
shutil.copy(WEEKS, B/'assets/weeks.tsv')
economy = (B/'assets/economy.tsv').read_bytes()
assert b'M\t482\t' not in economy, 'base economy already carries COC mission rows'
extra = CATALOG_ECONOMY.read_bytes()
if economy and not economy.endswith(b'\n'):
    economy += b'\n'
(B/'assets/economy.tsv').write_bytes(economy + extra)
shutil.copy(CATALOG_SUPPRESSION, B/'assets/suppression-extra.tsv')
shutil.copy(B/'assets/suppression.tsv', B/'assets/suppression-baseline.tsv')
suppression = (B/'assets/suppression.tsv').read_bytes()
assert hashlib.sha256(suppression).hexdigest() == 'b0f8cfa1637d65061f0f062ba78ef79e9fdee2b93889a9b832cb0cddd1160679', 'base suppression is not story-extended'
(B/'assets/suppression.tsv').write_bytes(extend_city_suppression(suppression))
assert hashlib.sha256((B/'assets/suppression.tsv').read_bytes()).hexdigest() == CITY_SUPPRESSION_EXTENDED_SHA, 'COC suppression extension hash changed' 
# Compile-only descriptors are isolated in B/api and never enter the runtime classpath.
run(J/'javac', '--release', '8', '-cp', SDK, '-d', B/'api', *H.glob('compile_stubs/**/*.java'))
run(J/'javac', '--release', '8', '-cp', str(SDK)+':'+str(B/'api'), '-d', B/'production', *H.glob('src/**/*.java'))
run(J/'javac', '--release', '8', '-cp', str(SDK)+':'+str(M), '-d', B/'bridge', *R.glob('offline/current/java/android_story_missions/src/**/*.java'))
run(J/'javac', '--release', '8', '-d', B/'platform', *[x for x in R.glob('offline/current/java/android_core_rpc/host_stubs/**/*.java') if x.name not in ('AssetManager.java', 'Os.java')], *R.glob('offline/current/java/android_baiye_transactions/host_tests/android/**/*.java'), R/'offline/current/java/android_week_reset/host_tests/android/system/Os.java')
RUNTIME_CP = [B/'platform', B/'production', OWN, B/'bridge', M, JSON]
CP = ':'.join(map(str, RUNTIME_CP))
assert str(B/'api') not in CP, 'compile-only StoryCity descriptors must not be on runtime classpath'
run(J/'javac', '--release', '8', '-cp', CP, '-d', B/'tests', *H.glob('host_tests/com/**/*.java'))
out = run(J/'java', '-Xverify:all', '-cp', CP+':'+str(B/'tests'), 'com.project7.localmanager.StoryCityHost', B/'assets')
match = re.search(r'^PASS (\d+) ', out, re.M)
assert match, out
CHECKS = int(match.group(1))
baiye = ['-Dp7.baiye.catalog='+str(BAIYE['catalog']), '-Dp7.baiye.fragments='+str(BAIYE['fragments']), '-Dp7.baiye.shop='+str(BAIYE['shop'])]
coc = run(J/'java', '-Xverify:all', *baiye, '-cp', CP+':'+str(B/'tests'), 'com.project7.localmanager.StoryCityCocHost', B/'assets')
coc_match = re.search(r'^PASS (\d+) ', coc, re.M)
assert coc_match, coc
COC_CHECKS = int(coc_match.group(1))
assert all(f'COC {scene} ' in coc for scene in (482, 483, 484, 485, 486, 487, 488)), coc
AFTER = fingerprints()
if BEFORE != AFTER:
    drift = {key: [BEFORE.get(key), AFTER.get(key)] for key in set(BEFORE)|set(AFTER) if BEFORE.get(key) != AFTER.get(key)}
    (B/'input-drift.json').write_text(json.dumps(drift, indent=2, sort_keys=True)+'\n')
    raise SystemExit(f'input drift after execution: {json.dumps(drift, sort_keys=True)}')
(B/'stdout.log').write_text(out)
(B/'coc.log').write_text(coc)
REPORT = {
    'status': 'PASS',
    'main_inputs': rel(OWN),
    'main_class_files': len(MAIN_CLASSES),
    'main_classes_sha256': BEFORE['main_classes']['sha256'],
    'input_sha256': BEFORE,
    'input_drift': [],
    'runtime_no_story_api_stubs': True,
    'checks': CHECKS,
    'coc_checks': COC_CHECKS,
    'pins': {
        'manager_sha256': MANAGER_PIN,
        'frame_sha256': FRAME_PIN,
        'frame_artifact': ARGS.frame,
        'frames_jar_sha256': BEFORE['frames_jar'],
        'available_frames': {name: {'path': rel(path), 'sha256': pin} for name, (path, pin) in FRAMES.items()},
        'catalog_sha256': BEFORE['story_city_catalog'],
        'catalog_contract_sha256': BEFORE['story_city_catalog_contract'],
        'catalog_economy_sha256': BEFORE['story_city_catalog_economy'],
        'catalog_suppression_sha256': BEFORE['story_city_catalog_suppression'],
        'suppression_extended_sha256': CITY_SUPPRESSION_EXTENDED_SHA,
        'virtual_data_sha256': BEFORE['story_city_virtual'],
        'mission_catalog_sha256': BEFORE['story_mission_catalog'],
        'manager_event_graph_sha256': BEFORE['manager_event_graph'],
        'manager_weeks_sha256': BEFORE['manager_weeks'],
    },
    'main_snapshot': rel(OWN),
    'main_preflight': rel(PREFLIGHT),
    'frame_jar': rel(M),
    'catalog_sha256': BEFORE['story_city_catalog'],
    'source_hashes': {rel(x): sha(x) for x in sorted(H.rglob('*.java'))},
    'menu_ready': False,
    'offline_compat': {
        'policy': 'source-city-coc-offline-v1',
        'reward': 'original-offline-city-fight-reward-v1',
        'pending_event': 'server-pending-mission-event-v1',
        'mission_hero': 'source-coc-route-27-1-v1 (7 MH rows 482:135..488:135)',
        'gate_fixture': 'per-scene predecessor free + current available + legacy q7ChapterLocks cleared; no full 1424 city-progression claim',
    },
    'evidence_boundary': (
        'Host executes real LocalProfileStore begin/finish, original LocalEconomyEngine level reward/once-only receipt, '
        'LocalTutorialStore save/load, and LocalEventEngine completion for each 482..488. Each scene is admitted only when its '
        'own chain predecessor is free and its area is available; wrong party/area/type, insufficient actions, locked/unfree/'
        'not-available gates, admission replay and duplicate Store finish are negative-checked. The source mission events '
        '1435..1441 are release=false and normally server-created; the named offline policy adds exactly that pending event. '
        'The fixture represents the per-scene gate state (predecessor free/current available) and clears the legacy lock overlay; '
        'it does not prove the full 1424 route-27-1 city progression or dialog production. '
        'For mission heroes, the unextended suppression table returns null missionHero for all seven scenes; the seven appended '
        'MH rows make missionHero return the fixed 135 override, and combatDataDocument replaces only the admitted scene hero '
        'document while leaving the player profile, owned hero list, normal MH rows, and non-COC scenes unchanged.'
    ),
    'limits': [
        'synthetic profile/gate fixture; no player template, account, or live server',
        'offline pending mission event is explicit: original 1435..1441 are server-created release=false events',
        'reward uses existing pinned manager city_fight_reward; original server drop rule remains unknown',
        'COC MH rows are append-only and scope-protected to 482:135..488:135; normal MH rows and player hero documents are unchanged',
        'MH values are produced by the pinned original640 calculator from mission_hero_attr; no live player collection is imported',
        'legacy q7ChapterLocks from event 1424 are cleared in the per-scene fixture; full 27-1 lock progression not proven',
        'compile-only descriptors are isolated; no StoryCity API stubs on runtime classpath',
        'menu25 admission remains gated: public_ready_ids is empty and supports(25) is false',
        'no D8/APK/device/emulator/game/native battle acceptance',
    ],
}
(B/'result.json').write_text(json.dumps(REPORT, indent=2)+'\n')
print(out, end='')
print(coc, end='')
print(f'checks={CHECKS} coc_checks={COC_CHECKS} inputs={rel(OWN)} classes={len(MAIN_CLASSES)}')
print(B)
