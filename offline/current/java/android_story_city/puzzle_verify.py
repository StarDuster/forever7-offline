"""Host-run the real original LocalEventCatalog against the pinned puzzle delta.

This is source-stage host verification only: no Android runtime, D8, APK, game,
emulator, or native claim.  Exit codes: 0 accepted, 2 blocked by the original
reviewed-room bound, 1 test failure or infrastructure error.
"""
from pathlib import Path
import hashlib
import json
import re
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
BUILD = ROOT / 'runtime/build/project7_story_city_puzzle_room4'
BASE = ROOT / 'analysis/project7/manager/assets/event_graph.tsv'
FRAMES = ROOT / 'analysis/project7/story-city-gateway-hook-v1/manager-translated-frames.jar'
FRAMES_SHA256 = 'dcea974fb0ed2ec4db9bd62a3cce770ebe2ceb1f0d692b40565c73407222c68c'
JAVA_HOME = ROOT / 'toolchains/java/jdk-17.0.21+9/Contents/Home/bin'
SDK = ROOT / 'toolchains/android-sdk/platforms/android-32/android.jar'
HOST = HERE / 'host_tests/com/project7/localmanager/PuzzleRoom4Host.java'
TOOL = ROOT / 'tools/project7_story_city_puzzle.py'


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def run(*args):
    return subprocess.run(list(map(str, args)), capture_output=True, text=True)


def main():
    if sha(FRAMES) != FRAMES_SHA256:
        raise SystemExit('story-city frame jar pin changed')
    build = run(sys.executable, TOOL, '--write')
    if build.returncode != 0:
        print(build.stdout, end='')
        print(build.stderr, end='', file=sys.stderr)
        raise SystemExit(1)
    check = run(sys.executable, TOOL, '--check')
    if check.returncode != 0:
        print(check.stdout, end='')
        print(check.stderr, end='', file=sys.stderr)
        raise SystemExit(1)
    contract = json.loads((BUILD / 'contract-v1.json').read_text())
    merged = BUILD / 'event_graph.tsv'

    work = Path(tempfile.mkdtemp(prefix='verify-', dir=BUILD))
    classes = work / 'classes'
    classes.mkdir()
    clues_only = work / 'event_graph-clues-only.tsv'
    clue_rows = [row for row in (ROOT / 'offline/current/data/project7_story_city_catalog/puzzle-extra.tsv')
                 .read_text().split('\n') if row.startswith('@puzzleClue')]
    clues_only.write_bytes(BASE.read_bytes() + ('\n'.join(clue_rows) + '\n').encode())

    platform = [path for path in (ROOT / 'offline/current/java/android_core_rpc/host_stubs').rglob('*.java')
                if path.name != 'Os.java']
    platform.append(ROOT / 'offline/current/java/android_week_reset/host_tests/android/system/Os.java')
    compile_result = run(JAVA_HOME / 'javac', '--release', '8',
                         '-cp', str(SDK) + ':' + str(FRAMES),
                         '-d', str(classes), HOST, *platform)
    if compile_result.returncode != 0:
        shutil.rmtree(work, ignore_errors=True)
        print(compile_result.stdout, end='')
        print(compile_result.stderr, end='', file=sys.stderr)
        raise SystemExit(1)

    runtime_cp = ':'.join(map(str, (classes, FRAMES)))
    protocol = run(JAVA_HOME / 'java', '-Xverify:all', '-cp', runtime_cp,
                   'com.project7.localmanager.PuzzleRoom4Host',
                   str(BASE), str(merged), str(clues_only))
    output = protocol.stdout + protocol.stderr
    checks = re.search(r'(?:PASS|BLOCKED) (\d+) ', output)
    status = 'PASS' if protocol.returncode == 0 else 'BLOCKED' if protocol.returncode == 2 else 'FAIL'
    report = {
        'schema': 'project7-story-city-puzzle-room4-host-v1',
        'task_id': contract['task_id'],
        'status': status,
        'exit': protocol.returncode,
        'checks': int(checks.group(1)) if checks else 0,
        'base': {'path': str(BASE.relative_to(ROOT)), 'sha256': sha(BASE)},
        'merged': {'path': str(merged.relative_to(ROOT)), 'sha256': sha(merged)},
        'extra': contract['extra'],
        'puzzle_extra_sha256': sha(ROOT / 'offline/current/data/project7_story_city_catalog/puzzle-extra.tsv'),
        'frames_jar_sha256': sha(FRAMES),
        'consumer': contract['consumer'],
        'source_rows': contract['source_rows'],
        'stdout': output,
        'limits': [
            'original LocalEventCatalog aborts the merged graph at LocalPuzzleEngine$Room id bound 1..3',
            'clue-only probe aborts at LocalPuzzleEngine$Clue room bound 1..3',
            'puzzle_room_camera has no LocalEventCatalog column; cameras stay in the runtime virtual-data service',
        ],
    }
    (BUILD / 'host-result.json').write_text(json.dumps(report, indent=2, sort_keys=True) + '\n')
    shutil.rmtree(work, ignore_errors=True)
    print(output, end='')
    print('status=%s checks=%d exit=%d merged=%s' % (status, report['checks'], report['exit'], sha(merged)))
    if status == 'BLOCKED':
        print('blocked_by=' + contract['consumer']['class'] + ' bound=1..3 required=4')
    raise SystemExit(protocol.returncode)


if __name__ == '__main__':
    main()
