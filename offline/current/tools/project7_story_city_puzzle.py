"""Append-only puzzle room 4 increment for the fixed LocalEventCatalog graph.

The publishable delta (``offline/current/data/project7_story_city_catalog/puzzle-extra.tsv``)
uses only directives understood by the original ``LocalEventCatalog`` parser:

* ``@puzzleRoom event room clear incomplete routes clues`` (exactly 7 columns)
* ``@puzzleClue clue room add_cg`` (exactly 4 columns)

Event 3437, clear 3444, fail 3455, their trigger/mutex/effect rows, and the
route 27-2 condition are already pinned in the fixed base graph; this tool
refuses to run if any of those source rows drift.  Client-only rows (route
27-2/day-5 tip, cameras 9..13, clue-to-camera names) have no catalog column and
are re-verified from ``offline/current/data/project7_story_city_virtual`` instead.

The merged graph is written under ``runtime/build``; the fixed manager asset is
never modified.  The original consumer probe lives in
``offline/current/java/android_story_city/host_tests/com/project7/localmanager/PuzzleRoom4Host.java``.
"""
import _bootstrap  # noqa: E402,F401
from pathlib import Path
import argparse
import hashlib
import json
import sys

from _bootstrap import ROOT
BASE = ROOT / 'analysis/project7/manager/assets/event_graph.tsv'
EXTRA = ROOT / 'offline/current/data/project7_story_city_catalog/puzzle-extra.tsv'
VIRTUAL = ROOT / 'offline/current/data/project7_story_city_virtual/virtual-data-v1.json'
CONTRACT = ROOT / 'offline/current/data/project7_story_city_virtual/contract-v1.json'
OUT = ROOT / 'runtime/build/project7_story_city_puzzle_room4'
SCHEMA = 'project7-story-city-puzzle-room4-v1'
TASK_ID = 'project7-story-city-puzzle-room4-v1'
BASE_SHA256 = '7a0f781c0a84b2fc46b1f71b0dcc6f85e80b4047ba415e8af25a08e97f11c9ba'
VIRTUAL_SHA256 = '83fae3199e308db88513f4a6e6bf6af2288ca749258e3d81b5c81451f8fec6de'
PARSED_DIRECTIVES = ('@puzzleRoom', '@puzzleClue')
PUZZLE_ROOM = '@puzzleRoom\t3437\t4\t3444\t3455\t27-2\t17,18,19,20,21'
PUZZLE_CLUES = tuple('@puzzleClue\t%d\t4\t0' % clue for clue in (17, 18, 19, 20, 21))
# Exact fixed-graph rows this increment depends on.  (line number is evidence only)
SOURCE_ROWS = {
    'event_3437': '3437\t168\t3437\t0\t3\t\tdialog=3437;ui=1',
    'trigger_3437': '@trigger\t3437\t3436\t\t\t3444\t7:0\t2,2\t\t0\t7\t2\t\t52=27,27-2',
    'event_3444': '3444\t32\t0\t0\t2\t\t',
    'mutex_3444': '@mutex\t3444\t3455',
    'event_3455': '3455\t32\t0\t0\t5\t\t',
    'mutex_3455': '@mutex\t3455\t3444',
    'effect_3444': '@effect\t3444\t\t\t\t20292',
}
SOURCE_ROW_LINES = {
    'event_3437': (SOURCE_ROWS['event_3437'], 2555),
    'trigger_3437': (SOURCE_ROWS['trigger_3437'], 11499),
    'event_3444': (SOURCE_ROWS['event_3444'], 2562),
    'mutex_3444': (SOURCE_ROWS['mutex_3444'], 14881),
    'event_3455': (SOURCE_ROWS['event_3455'], 2573),
    'mutex_3455': (SOURCE_ROWS['mutex_3455'], 14886),
    'effect_3444': (SOURCE_ROWS['effect_3444'], 17160),
}
EXPECTED_ROOM = {'event': 3437, 'id': 4, 'clear': 3444, 'incomplete': 3455,
                 'routes': {'27-2'}, 'clues': {17, 18, 19, 20, 21}}
EXPECTED_CONSUMER = {
    'status': 'accepted',
    'consumer': 'com.project7.localmanager.LocalEventCatalog',
    'class': 'com.project7.localmanager.LocalPuzzleEngine$Room',
    'method': '<init>([Ljava/lang/String;)V',
    'bound': 4,
    'required': 4,
    'message': 'invalid reviewed room',
    'clue_class': 'com.project7.localmanager.LocalPuzzleEngine$Clue',
    'clue_bound': 4,
    'missing_main_change': 'none; room/clue upper bound 4 is integrated in the fixed DEX candidate',
}


def sha_bytes(data):
    return hashlib.sha256(data).hexdigest()


def require(value, message):
    if not value:
        raise ValueError(message)


def data_rows(data):
    """Return non-comment, non-empty TSV rows, preserving order."""
    return [line for line in data.decode('utf-8').split('\n') if line and not line.startswith('#')]


def row_key(row):
    fields = row.split('\t')
    if fields[0].startswith('@'):
        return (fields[0], fields[1])
    return ('event', fields[0])


def row_map(rows, label):
    result = {}
    for row in rows:
        key = row_key(row)
        require(key not in result, 'duplicate %s row %r' % (label, key))
        result[key] = row
    return result


def directive_keys(rows):
    """Keys only for directives this increment may add (base has other non-unique keys)."""
    return {row_key(row) for row in rows if row.split('\t')[0] in PARSED_DIRECTIVES}


def validate_base(base_bytes, pin=BASE_SHA256):
    if pin is not None:
        require(sha_bytes(base_bytes) == pin, 'fixed event_graph.tsv pin changed')
    text = base_bytes.decode('utf-8')
    require(text.endswith('\n'), 'fixed graph line boundary')
    for name, row in SOURCE_ROWS.items():
        require(row in text, 'missing source pin ' + name)
    existing = directive_keys(data_rows(base_bytes))
    require(('@puzzleRoom', '3437') not in existing, 'room 4 already present in base')
    for clue in (17, 18, 19, 20, 21):
        require(('@puzzleClue', str(clue)) not in existing, 'clue %d already present in base' % clue)
    return existing


def validate_extra(extra_bytes, base_rows):
    require(extra_bytes.endswith(b'\n'), 'extra asset line boundary')
    rows = data_rows(extra_bytes)
    extra_rows = row_map(rows, 'extra')
    for key in extra_rows:
        require(key[0] in PARSED_DIRECTIVES, 'unsupported extra directive %r' % (key,))
        require(key not in base_rows, 'duplicate base row %r' % (key,))
    require(rows == [PUZZLE_ROOM, *PUZZLE_CLUES], 'extra rows changed')
    room_fields = PUZZLE_ROOM.split('\t')
    require(len(room_fields) == 7, 'puzzle room column count changed')
    event, room, clear, incomplete = (int(value) for value in room_fields[1:5])
    routes = set(room_fields[5].split(','))
    clues = {int(value) for value in room_fields[6].split(',')}
    require({'event': event, 'id': room, 'clear': clear, 'incomplete': incomplete,
             'routes': routes, 'clues': clues} == EXPECTED_ROOM, 'puzzle room fields changed')
    return extra_rows


def validate_virtual(virtual_bytes):
    require(sha_bytes(virtual_bytes) == VIRTUAL_SHA256, 'virtual data pin changed')
    document = json.loads(virtual_bytes)
    puzzle = document.get('puzzle_room') or {}
    room = puzzle.get('room') or {}
    events = puzzle.get('events') or {}
    trigger = events.get('trigger') or {}
    clear = events.get('clear') or {}
    fail = events.get('not_clear') or {}

    require(room.get('id') == 4, 'virtual puzzle room id changed')
    room_row = room.get('row') or {}
    require(room_row.get('clear_event') == 3444, 'virtual clear event changed')
    require(room_row.get('not_clear_event') == 3455, 'virtual fail event changed')
    require(trigger.get('id') == 3437, 'virtual trigger event changed')
    require((trigger.get('row') or {}).get('puzzle_room') == 4, 'virtual trigger room changed')
    require((trigger.get('row') or {}).get('mutexEvent') == [3444], 'virtual trigger mutex changed')
    require((clear.get('row') or {}).get('mutexEvent') == [3455], 'virtual clear mutex changed')
    require((fail.get('row') or {}).get('mutexEvent') == [3444], 'virtual fail mutex changed')

    clues = puzzle.get('clues') or []
    cameras = puzzle.get('cameras') or []
    require([row.get('id') for row in clues] == [17, 18, 19, 20, 21], 'virtual clue set changed')
    require([row.get('id') for row in cameras] == [9, 10, 11, 12, 13], 'virtual camera set changed')
    require(all(row.get('room_id') == 4 for row in clues), 'virtual clue room changed')
    require(all(row.get('camera_name') for row in clues), 'virtual clue camera missing')
    require(all(row.get('camera_id') == row.get('id') for row in cameras), 'virtual camera id changed')
    require(all(row.get('room_id') == 4 for row in cameras), 'virtual camera room changed')

    route = puzzle.get('route') or {}
    tip = route.get('tip') or {}
    tip_row = tip.get('row') or {}
    require(route.get('id') == '27-2', 'virtual route changed')
    require(tip.get('key') == ['27-2', 5], 'virtual tip key changed')
    require(tip_row.get('day') == 5 and tip_row.get('check_type') == 1, 'virtual tip policy changed')
    require(tip_row.get('check_paras') == [3444], 'virtual tip parameter changed')
    return {
        'room': room_row,
        'trigger_event': trigger.get('id'),
        'clear_event': room_row.get('clear_event'),
        'fail_event': room_row.get('not_clear_event'),
        'clues': {row['id']: row['camera_name'] for row in clues},
        'cameras': {row['id']: row['camera_name'] for row in cameras},
        'route_tip': tip,
    }


def merged_bytes(base_bytes, extra_bytes):
    """Append only the extra data rows; comments stay out of the runtime graph."""
    validate_base(base_bytes)
    base_rows = directive_keys(data_rows(base_bytes))
    validate_extra(extra_bytes, base_rows)
    extra_data = b'\n'.join(row.encode('utf-8') for row in data_rows(extra_bytes)) + b'\n'
    return base_bytes + extra_data


def build(verify_virtual=True):
    base_bytes = BASE.read_bytes()
    extra_bytes = EXTRA.read_bytes()
    validate_base(base_bytes)
    validate_extra(extra_bytes, directive_keys(data_rows(base_bytes)))
    merged = merged_bytes(base_bytes, extra_bytes)
    result = {
        'schema': SCHEMA,
        'task_id': TASK_ID,
        'base': {'path': str(BASE.relative_to(ROOT)), 'sha256': sha_bytes(base_bytes)},
        'extra': {'path': str(EXTRA.relative_to(ROOT)), 'sha256': sha_bytes(extra_bytes)},
        'merged': {'sha256': sha_bytes(merged), 'bytes': len(merged)},
        'rows': {'puzzleRoom': [PUZZLE_ROOM], 'puzzleClue': list(PUZZLE_CLUES)},
        'source_rows': {name: {'line': line, 'sha256': sha_bytes(row.encode('utf-8'))}
                        for name, (row, line) in SOURCE_ROW_LINES.items()},
        'consumer': EXPECTED_CONSUMER,
    }
    if verify_virtual:
        virtual_bytes = VIRTUAL.read_bytes()
        result['virtual'] = {'path': str(VIRTUAL.relative_to(ROOT)), 'sha256': sha_bytes(virtual_bytes)}
        result['client_metadata'] = validate_virtual(virtual_bytes)
    return merged, result


def produce(output=OUT):
    merged, contract = build()
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    target = output / 'event_graph.tsv'
    target.write_bytes(merged)
    contract['merged']['path'] = str(target.relative_to(ROOT))
    (output / 'contract-v1.json').write_text(json.dumps(contract, indent=2, sort_keys=True) + '\n')
    return contract


def check(output=OUT):
    output = Path(output)
    contract = json.loads((output / 'contract-v1.json').read_text())
    require(contract.get('schema') == SCHEMA, 'contract schema changed')
    require(contract.get('task_id') == TASK_ID, 'contract task id changed')
    require(sha_bytes(EXTRA.read_bytes()) == contract['extra']['sha256'], 'published puzzle extra changed')
    require(sha_bytes(BASE.read_bytes()) == contract['base']['sha256'], 'fixed graph changed')
    merged = merged_bytes(BASE.read_bytes(), EXTRA.read_bytes())
    require(sha_bytes(merged) == contract['merged']['sha256'], 'merged graph changed')
    require((output / 'event_graph.tsv').read_bytes() == merged, 'merged graph file changed')
    require(sha_bytes(VIRTUAL.read_bytes()) == contract['virtual']['sha256'], 'virtual data changed')
    validate_virtual(VIRTUAL.read_bytes())
    return contract


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true', help='write merged candidate under runtime/build')
    parser.add_argument('--check', action='store_true', help='verify published asset, pins and merged bytes')
    parser.add_argument('--output', type=Path, default=OUT)
    args = parser.parse_args()
    if args.write and args.check:
        parser.error('choose --write or --check')
    if args.write:
        print(json.dumps(produce(args.output), indent=2, sort_keys=True))
    elif args.check:
        contract = check(args.output)
        print('PASS puzzle-room-4 asset pins, source rows, merged bytes; consumer=%s bound=%d status=%s' % (
            contract['consumer']['class'], contract['consumer']['bound'], contract['consumer']['status']))
    else:
        contract = build()[1]
        print(json.dumps({k: contract[k] for k in ('task_id', 'base', 'extra', 'merged', 'consumer')},
                         indent=2, sort_keys=True))


if __name__ == '__main__':
    main()
