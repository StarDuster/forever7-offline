"""Host-run puzzle room 4 against the frozen v29 stage manager and merged graph.

Inputs are the pinned v29 prepare DEX, its merged event_graph.tsv, and the
dex2jar+FrameFix translation of that exact DEX (hash-chained below).  The host
itself drives only original consumers: LocalEventCatalog, LocalPatrolEngine ->
LocalEventEngine.startEvent, LocalProfileStore.updateServices, and
LocalEventEngine.trace.  No D8, APK, native, emulator, or source/C edits.

Exit 0 = accepted; any failed assertion/command = exit 1.
"""
from pathlib import Path
import hashlib, json, os, re, shutil, subprocess, sys, zipfile

R = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
BUILD = R / 'runtime/build/project7_story_city_puzzle_room4_stage'
STAGE = R / 'analysis/project7/story-city-integration-prepare-v36/project7-inputs-5w320euc/stage'
DEX = STAGE / 'classes7.dex'
GRAPH = STAGE / 'assets/event_graph.tsv'
BASE = R / 'analysis/project7/manager/assets/event_graph.tsv'
PRODUCTION = R / 'analysis/project7/story-city-integration-prepare-v36/project7-inputs-5w320euc/compiled'
EVIDENCE = R / 'analysis/project7/story-city-v26-gateway-evidence-20261104'
HOOK = R / 'analysis/project7/story-city-gateway-hook-v1'
FRAME_CANDIDATES = [R / 'analysis/project7/story-city-coc-gateway-v1/manager-translated-frames.jar', EVIDENCE / 'jar/stage-frames.jar', HOOK / 'manager-translated-frames.jar']
STORY_CATALOG = R / 'runtime/project7_story_city_catalog/catalog-v1.json.gz'
PUZZLE_EXTRA = R / 'runtime/project7_story_city_catalog/puzzle-extra.tsv'
VIRTUAL = R / 'runtime/project7_story_city_virtual/virtual-data-v1.json'
VIRTUAL_CONTRACT = R / 'runtime/project7_story_city_virtual/contract-v1.json'
HOST = HERE / 'host_tests/com/project7/localmanager/PuzzleRoom4StageHost.java'
J = R / 'toolchains/java/jdk-17.0.21+9/Contents/Home/bin'
SDK = R / 'toolchains/android-sdk/platforms/android-32/android.jar'
JSON = R / 'toolchains/json-20240303.jar'

DEX_SHA = 'fee369231e8924923f774cdbda4961f91b6ab87cee237b249cff8229b535f1c6'
GRAPH_SHA = '50d211e2108524dbce10e9babf9de77cf9faf9e331f8a70f8d1a8f6d771f927f'
BASE_SHA = '7a0f781c0a84b2fc46b1f71b0dcc6f85e80b4047ba415e8af25a08e97f11c9ba'
PATCH_SHA = '10a840c9f2118dec57bd7f35f12573f4fca312b92aaaf1e6d270b5904bb0736a'
FRAME_SHA = 'a767c656b853d40d2e8acac835eac19ec2272da8cbee112a7428637d539bbc66'
TRANSLATED_SHA = '630059423631ecf3b29b478724a4e4276564c071e2d7f9a00c0194a9f9495bed'
CATALOG_SHA = 'af2328b97372c27fd392b5b399d03daa17fa73acdd35d2b1ad5b0a8f07218069'
VIRTUAL_SHA = '83fae3199e308db88513f4a6e6bf6af2288ca749258e3d81b5c81451f8fec6de'
PUZZLE_CLUE_IDS = [17, 18, 19, 20, 21]


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def require(value, message):
    if not value:
        raise AssertionError(message)


def run(*args, cwd=R):
    printable = ' '.join(str(a) for a in args)
    print(f'$ {printable}', flush=True)
    process = subprocess.run([str(a) for a in args], cwd=str(cwd), capture_output=True, text=True)
    print(f'exit={process.returncode}', flush=True)
    if process.returncode != 0:
        print(process.stdout[-6000:], flush=True)
        print(process.stderr[-6000:], flush=True)
        raise SystemExit(f'command failed: {args[0]}')
    return process.stdout + process.stderr


def link_tree(source, target):
    target.mkdir(parents=True, exist_ok=True)
    for root, dirs, files in os.walk(source):
        relative = os.path.relpath(root, source)
        current = target if relative == '.' else target / relative
        current.mkdir(parents=True, exist_ok=True)
        for name in files:
            src, dst = Path(root) / name, current / name
            try:
                os.link(src, dst)
            except OSError:
                shutil.copy2(src, dst)


def stage_pins():
    require(sha(DEX) == DEX_SHA, f'stage classes7.dex sha changed: {sha(DEX)}')
    require(sha(GRAPH) == GRAPH_SHA, f'stage event_graph.tsv sha changed: {sha(GRAPH)}')
    require(sha(BASE) == BASE_SHA, f'base event_graph.tsv sha changed: {sha(BASE)}')
    build = json.loads((STAGE / 'build-inputs.json').read_text())
    binding = build['story_city_manager_binding']
    require(binding['target_sha256'] == DEX_SHA, 'stage manager binding target')
    require(binding['patch_sha256'] == PATCH_SHA, 'stage manager seam patch')
    require(binding['format'] == 'project7-story-city-gateway-puzzle-coc-seams-v6', 'stage manager seam format')
    require(binding['bytes'] == DEX.stat().st_size, 'stage manager binding size')
    merged = build['story_city_event_graph']
    require(merged['merged_sha256'] == GRAPH_SHA, 'stage graph binding')
    require((STAGE / 'assets/project7_story_city/catalog-v1.json.gz').is_file(),
            'stage story-city catalog missing')
    return build


def frame_path():
    for path in FRAME_CANDIDATES:
        if path.exists() and sha(path) == FRAME_SHA:
            return path
    raise AssertionError('no frame translation with the pinned stage sha')


def frame_pins(frame_file):
    require(sha(frame_file) == FRAME_SHA, f'stage frame sha changed: {sha(frame_file)}')
    with zipfile.ZipFile(frame_file) as archive:
        classes = [name for name in archive.namelist() if name.endswith('.class')]
        stubs = [name for name in classes if b'd2j fail translate' in archive.read(name)]
    require(len(classes) == 649, f'frame class count changed: {len(classes)}')
    require(not stubs, f'frame translation stubs: {stubs[:3]}')
    if (HOOK / 'classes7.dex').exists():
            return {'classes': len(classes), 'translation_stubs': 0}


def production_pins():
    manifest = json.loads((PRODUCTION / 'compile-inputs.json').read_text())
    listed = {row['path']: row['sha256'] for row in manifest['classes']}
    actual = sorted(path.relative_to(PRODUCTION / 'production-classes').as_posix()
                    for path in (PRODUCTION / 'production-classes').rglob('*.class'))
    require(len(actual) == 236, f'production class count changed: {len(actual)}')
    require(len(listed) == 236, 'compile-inputs class list changed')
    require(set(actual) == set(listed), 'production class set differs from compile-inputs')
    for relative in actual:
        require(sha(PRODUCTION / 'production-classes' / relative) == listed[relative],
                f'production class sha changed: {relative}')
    return {'classes': len(actual)}


def graph_delta():
    base = BASE.read_bytes()
    merged = GRAPH.read_bytes()
    require(merged.startswith(base), 'merged graph must preserve the base prefix byte-for-byte')
    extra = [row for row in PUZZLE_EXTRA.read_text().split('\n') if row.startswith('@puzzle')]
    require(len(extra) == 6, f'puzzle delta row count changed: {len(extra)}')
    require(merged == base + ('\n'.join(extra) + '\n').encode(), 'merged graph is not base plus the reviewed delta')
    rows = [row.split('\t') for row in merged.decode('utf-8').split('\n') if row.startswith('@puzzle')]
    require([row[1] for row in rows if row[0] == '@puzzleRoom'] == ['4229', '6228', '7346', '3437'], 'room row order')
    clue_rows = [row for row in rows if row[0] == '@puzzleClue']
    require([int(row[1]) for row in clue_rows] == list(range(1, 22)), 'clue row order 1..21')
    require(all(len(row) == 7 for row in rows if row[0] == '@puzzleRoom'), 'room rows stay 7 columns')
    require(all(len(row) == 4 for row in clue_rows), 'clue rows stay 4 columns (no camera column)')
    require(not any('camera' in row for row in merged.decode('utf-8').split('\n') if row.startswith('@puzzle')),
            'server puzzle rows must not carry camera client data')
    return {'base_prefix': True, 'appended_rows': len(extra), 'old_rooms': [4229, 6228, 7346],
            'old_clues': 16}


def camera_checks():
    require(sha(VIRTUAL) == VIRTUAL_SHA, f'virtual data sha changed: {sha(VIRTUAL)}')
    data = json.loads(VIRTUAL.read_text())
    contract = json.loads(VIRTUAL_CONTRACT.read_text())
    require(contract['data_file'] == 'virtual-data-v1.json' and contract['schema'] == 'project7-story-city-virtual-data-v1',
            'virtual contract identity')
    require(contract['counts']['puzzle_rooms'] == 1, 'virtual contract room count')
    require(contract['counts']['puzzle_clues'] == 5, 'virtual contract clue count')
    require(contract['counts']['puzzle_cameras'] == 5, 'virtual contract camera count')
    room = data['puzzle_room']
    clues = room['clues']
    cameras = room['cameras']
    require([row['id'] for row in clues] == PUZZLE_CLUE_IDS, 'virtual clue ids 17..21')
    require(all(row['room_id'] == 4 for row in clues), 'virtual clues are room 4')
    require(sorted(row['id'] for row in cameras) == [9, 10, 11, 12, 13], 'virtual cameras 9..13')
    require(all(row['room_id'] == 4 and row['camera_id'] == row['id'] for row in cameras), 'virtual camera rows')
    camera_names = {row['camera_name'] for row in cameras}
    require(len(camera_names) == 5, 'distinct virtual camera names')
    require(all(row['camera_name'] in camera_names for row in clues), 'clue camera references resolve')
    require(len({row['camera_name'] for row in clues}) == 5, 'clue camera names are distinct')
    require(len({row['clue_ui'] for row in clues}) == 5, 'clue ui images distinct')
    require(sorted(row['client_dialogue'] for row in clues) == [21491, 21492, 21493, 21494, 21495],
            'clue dialogue ids 21491..21495')
    require(all(row['client_dialogue'] > 0 and row['clue_des'] for row in clues), 'clue client text present')
    return {'clue_ids': PUZZLE_CLUE_IDS,
            'clue_to_camera': {row['id']: row['camera_name'] for row in clues},
            'camera_ids': sorted(row['id'] for row in cameras),
            'server_columns': ['clue', 'room', 'add_cg']}


def main():
    if BUILD.exists():
        shutil.rmtree(BUILD)
    BUILD.mkdir(parents=True)
    stage_pins()
    frame_file = frame_path()
    frame = frame_pins(frame_file)
    production = production_pins()
    delta = graph_delta()
    camera = camera_checks()
    require(sha(STORY_CATALOG) == CATALOG_SHA, f'story-city catalog sha changed: {sha(STORY_CATALOG)}')

    # Same frozen stage assets: catalog and virtual data are required and pinned.
    assets = BUILD / 'assets'
    link_tree(STAGE / 'assets', assets)
    require(sha(assets / 'project7_story_city/catalog-v1.json.gz') == CATALOG_SHA, 'stage catalog sha')

    platform, tests = BUILD / 'platform', BUILD / 'tests'
    platform.mkdir()
    tests.mkdir()
    platform_sources = [
        R / 'runtime/android_core_rpc/host_stubs/android/content/Context.java',
        R / 'runtime/android_core_rpc/host_stubs/android/util/Log.java',
        R / 'runtime/android_core_rpc/host_stubs/android/system/ErrnoException.java',
        R / 'runtime/android_baiye_transactions/host_tests/android/content/res/AssetManager.java',
        R / 'runtime/android_week_reset/host_tests/android/system/Os.java',
    ]
    run(J / 'javac', '--release', '8', '-cp', SDK, '-d', platform, *platform_sources)
    compile_cp = ':'.join(map(str, (platform, SDK, PRODUCTION / 'production-classes', frame_file, JSON)))
    run(J / 'javac', '--release', '8', '-cp', compile_cp, '-d', tests, HOST)

    runtime_cp = ':'.join(map(str, (platform, PRODUCTION / 'production-classes', frame_file, JSON, tests)))
    stage_only = run(J / 'java', '-Xverify:all', '-cp', runtime_cp,
                     'com.project7.localmanager.PuzzleRoom4StageHost',
                     STAGE / 'assets', DEX, GRAPH, 'stage-only')
    require('STAGE_ONLY catalog_prepare=ok owns=true' in stage_only, stage_only)

    output = run(J / 'java', '-Xverify:all', '-cp', runtime_cp,
                 'com.project7.localmanager.PuzzleRoom4StageHost', assets, DEX, GRAPH)
    checks = int(re.search(r'^PASS (\d+) actual v36-stage', output, re.M).group(1))
    require(checks >= 300, f'host check count low: {checks}')
    clear = re.search(r'^CLEAR (\S+) processing=3437 exit=3444 clues=5 reload_outcome=3444 terminal=3444 '
                      r'completed3455=false available3455=false$', output, re.M)
    fail = re.search(r'^FAIL (\S+) processing=3437 exit=3455 clues=4 reload_outcome=3455 replay=3437 '
                     r'retry_exit=3444 terminal=3444 completed3455=false available3455=false$', output, re.M)
    require(clear and fail, output)
    require('LEGACY rooms=4229,6228,7346 clues=1..16 catalog=accepted' in output, output)
    require('CAMERA server_clues=17..21 cg=0 profile_camera_keys=0' in output, output)
    require('PASS %d actual v36-stage' % checks in output, output)

    (BUILD / 'stage-only.log').write_text(stage_only)
    (BUILD / 'host.log').write_text(output)
    result = {
        'stage': str(STAGE),
        'stage_dex': {'path': str(DEX), 'sha256': DEX_SHA, 'bytes': DEX.stat().st_size},
        'stage_event_graph': {'path': str(GRAPH), 'sha256': GRAPH_SHA, 'bytes': GRAPH.stat().st_size},
        'stage_manager_binding': {'patch_sha256': PATCH_SHA, 'format': 'project7-story-city-gateway-puzzle-coc-seams-v6'},
        'stage_frame': {'path': str(frame_file), 'sha256': FRAME_SHA, 'classes': frame['classes'],
                        'translation_stubs': 0,
                        'provenance': 'dex2jar+FrameFix of stage/classes7.dex (v29 fixed stage)'},
        'production_classes': production,
        'graph_delta': delta,
        'story_city_catalog': {'path': str(STORY_CATALOG), 'sha256': CATALOG_SHA,
                               'present_in_stage': True, 'composed_for_routes': False},
        'camera_client_data': camera,
        'stage_only': {'catalog_prepare': 'ok', 'owns': True,
                       'reason': 'v29 stage/assets carries project7_story_city/catalog-v1.json.gz'},
        'host': {'path': str(HOST), 'checks': checks,
                 'entries': {'3437': 'LocalPatrolEngine.begin(area 7) -> LocalEventEngine.startEvent',
                             'puzzle': 'LocalProfileStore.updateServices q7PuzzleBegin/puzzleRoomGetClue/q7PuzzleExit',
                             'trace': 'LocalEventEngine.trace dialog 3437 then ui 1',
                             'persistence': 'LocalTutorialStore.save/load + LocalProfileStore.load'},
                 'clear': {'exit': 3444, 'clues': 5, 'reload_outcome': 3444, 'terminal': 3444},
                 'fail': {'exit': 3455, 'clues': 4, 'reload_outcome': 3455, 'replay': 3437,
                          'retry_exit': 3444, 'terminal': 3444},
                 'completed3455': False},
        'no_d8_apk_native': True,
        'provenance_hashes': {'driver': sha(__file__), 'host': sha(HOST), 'stage_build_inputs': sha(STAGE/'build-inputs.json'), 'stage_dex': DEX_SHA, 'stage_event_graph': GRAPH_SHA},
        'source_edits': False,
    }
    (BUILD / 'result.json').write_text(json.dumps(result, indent=2) + '\n')
    print(stage_only, end='')
    print(output, end='')
    print(f'stage hashes: dex={DEX_SHA} graph={GRAPH_SHA} frame={FRAME_SHA}')
    print(f'camera client data: {camera["clue_to_camera"]}')
    print(f'status=PASS checks={checks} build={BUILD}')


if __name__ == '__main__':
    main()
