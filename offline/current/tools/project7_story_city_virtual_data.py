"""Source-bound virtual COC data contract for the project7 story city.

Read-only over original cdata tables. Emits a mergeable data contract for
virtual areas 10000..10003, COC scenes 482..488, and puzzle room 4. It does not
write the runtime catalog, StoryCityPolicy, or any consumer artifact.
"""
import _bootstrap  # noqa: E402,F401
from pathlib import Path
import argparse
import gzip
import hashlib
import json
import re
import sys

from _bootstrap import ROOT
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from project7_dream_catalog.produce import literal  # noqa: E402

SCHEMA = 'project7-story-city-virtual-data-v1'
POLICY = 'source-coc-route-27-1-v1'
NAMESPACE = 'q7StoryCity'
ROUTE = '27-1'
ROUTE_FAMILY = '27'
TARGET_HERO = 135
VIRTUAL_AREAS = (10000, 10001, 10002, 10003)
COC_SCENES = (482, 483, 484, 485, 486, 487, 488)
CORE_VIRTUAL_SCENES = (482, 484, 486, 487)
INTERSTITIAL_SCENES = (483, 485, 488)
CHAIN_AREAS = (7, 10000, 6, 10001, 4, 10002, 10003, 2)
DEFAULT_SOURCE = ROOT / 'analysis/project7/scripts/com/data/cdata'
DEFAULT_OUTPUT = ROOT / 'analysis/project7/story-city-virtual-data-v1'
DEFAULT_CATALOG = ROOT / 'analysis/project7/story-city-catalog-v1/catalog-v1.json.gz'
CLIENT = ROOT / 'analysis/original-py-640'
DECOMPILED = ROOT / 'analysis/decompiled'

# Original cdata pins. The same bytes are present in analysis/scripts and
# analysis/android640-scripts; the project7 tree is the pinned source.
PINS = {
    'city_data': '155ebc4d9c63c15fa921b8b3753617ef6c1d4cde2604a72263798e46c7aa775f',
    'city_virtual_area': 'dda839275cf285534e963c4bfac07bf1d1d9beb205b06681273eb9942c3582d3',
    'chapter_mission_data': 'c637bbf1665c8118b238c702145a22df0ceaf860bdf80595edbcf0d20882cdb4',
    'mission': '2019aab0289ffdac6aacde82b21cd283ef0c8d8afb6bb264d087e8cde262390f',
    'mission_hero_attr': '25647eaa103bb23bc22c27910e1f119e7ed2f169f52ac440dee69f573a60cc8b',
    'coc_area_link_data': 'ef14e11a29bce26f5d96bf440245437ee870f5a133e42e05e3acf1a1171e4889',
    'city_area_link_data': '017b12541c4dcab208c6f26f9c44539bb932e7d77cc93d6eae32f8ef71ed768c',
    'city_area_sfx_data': '3cf373224396ca82cd630a22a5f0450b7b684af26dec4dbc57045b1f6ea19a83',
    'puzzle_room': '03c4cbbeb686abc956565f552ad57113e083d38f9a0e6e5589c6ba6e53fe9812',
    'puzzle_room_clue': 'ab6a6e7ff5daf8380216d3bbe45897b6ced36db803eba0e8c14b0d18b52a647e',
    'puzzle_room_camera': '17dabc4084df225d28e26ca6fd50e9767d6dee3c683f9309cc25b8e0c48f7b1e',
    'event_content': '0ddb80bbe56259a2f54acdb7accef49ad390240b0cac504ba1375a3c8976afe7',
    'event_condition': '1ab7a968ebc01bccfa9419172ed92e91d9d491aa7288d616f2c8181de5389ec1',
    'event_condition_map': '23b53c490ceb982784bb854d7c8c5fd0fcd637b8419639b35f522551fdbddd0a',
    'storyroute_tip': 'b9dc0588f1bdc64a1937b41c8c771c54fc369cc3e20357d63c22b02f1850748f',
    'story_route': '53f3161471d82c9abe562c41982b51f5d01a1651400d3c6fd58433b2629614b1',
    'hero': '5fd8f55649e12030a76ec34d50fcf10b414fc07cb8055437177be8ecf29f771e',
    'battle_event': '594b21b0469b8e0d4dcf40a1d5d729c2116f63ac02d3bf852f58a0130abae35f',
    'city_fight_reward': '3899909239b4c9ab64ee07d341defab5fe87316ad2dc0e0d5161f97934ae5204',
    'reward_random': '8680b7d5a5e1befa9011647317c88fdaf63aff80889c36ed44f249678cd46262',
    'reward_common': '6f60386ce336a186ee01ee606a4d67df43674275272f787f082dbef8582e6fde',
    'story_clue_info': '7fef35f420d888892a4c3f023bd0db017b0858d64f6da4aab19daa7645280882',
}

CITATION_FILES = {
    'const': CLIENT / 'com/const.py',
    'city_data_py': CLIENT / 'entity/avatar_attrs/CityData.py',
    'battle_stage_member': CLIENT / 'entity/avatar_members/BattleStageMember.py',
    'combat_member': CLIENT / 'entity/avatar_members/CombatMember.py',
    'event_logic': CLIENT / 'combat/logic/logic/event_logic.py',
    'logic_event_base': CLIENT / 'combat/logic/logic/events/event_base.py',
    'view_event_base': CLIENT / 'combat/view/logic/events/event_base.py',
    'event_anqixian11': CLIENT / 'combat/logic/logic/events/event_anqixian11.py',
    'battle_stage_panel': CLIENT / 'cocos/panels/battle_stage.py',
    'city_jiemi': CLIENT / 'game_scene/city_jiemi.py',
    'story_member': CLIENT / 'entity/avatar_members/StoryMember.py',
    'storyline_27': CLIENT / 'cocos/members/storyline/storyline_27.py',
    'decompiled_event_content': DECOMPILED / 'event_content.py',
}

# Table -> decompiled data line used only for file:line citations.
TABLE_DATA_LINE = {
    'city_data': 16,
    'city_virtual_area': 16,
    'chapter_mission_data': 16,
    'mission': 16,
    'mission_hero_attr': 16,
    'coc_area_link_data': 14,
    'city_area_link_data': 14,
    'city_area_sfx_data': 14,
    'puzzle_room': 14,
    'puzzle_room_clue': 14,
    'puzzle_room_camera': 14,
    'event_condition': 15,
    'event_condition_map': 14,
    'storyroute_tip': 15,
    'story_route': 14,
    'hero': 15,
    'mission_dialogue': 15,
    'battle_event': 17,
    'city_fight_reward': 15,
    'story_clue_info': 14,
}

TABLE_PATH = {
    name: 'analysis/original-py-640/com/data/cdata/%s.py' % name
    for name in TABLE_DATA_LINE
}


class Checker(object):
    def __init__(self):
        self.count = 0

    def __call__(self, condition, message):
        if not condition:
            raise ValueError(message)
        self.count += 1


def sha_bytes(value):
    return hashlib.sha256(value).hexdigest()


def sha_file(path):
    return sha_bytes(Path(path).read_bytes())


def jsonable(value):
    if isinstance(value, (set, frozenset)):
        return sorted((jsonable(item) for item in value), key=canonical_sort_key)
    if isinstance(value, (list, tuple)):
        return [jsonable(item) for item in value]
    if isinstance(value, dict):
        return {str(key): jsonable(item) for key, item in value.items()}
    if isinstance(value, bytes):
        return value.decode('utf-8')
    name = type(value).__name__
    if name == 'UnicodeForPython3':
        return str(value)
    if name == 'LongTypeForPython3':
        return int(value)
    return value


def canonical_sort_key(value):
    return json.dumps(jsonable(value), sort_keys=True, ensure_ascii=True,
                      separators=(',', ':'))


def canonical(value):
    return json.dumps(jsonable(value), sort_keys=True, ensure_ascii=True,
                      separators=(',', ':'), allow_nan=False).encode('ascii')


def pretty(value):
    return json.dumps(jsonable(value), sort_keys=True, ensure_ascii=False,
                      indent=1, allow_nan=False) + '\n'


def read_text(path):
    return Path(path).read_text(encoding='utf-8')


def load_source(source, checker):
    tables = {}
    for name, digest in sorted(PINS.items()):
        path = Path(source) / (name + '.marshal')
        checker(path.is_file(), 'Missing source table %s' % name)
        actual = sha_file(path)
        checker(actual == digest, 'Source pin changed for %s: %s' % (name, actual))
        tables[name] = literal(path)
    return tables


def class_block(text, name):
    match = re.search(r'(?m)^class %s\([^\n]*\):\n(.*?)(?=^class |\Z)' % re.escape(name),
                      text, re.S)
    if not match:
        raise ValueError('Missing const class %s' % name)
    return match.group(1)


def class_int(text, class_name, field):
    block = class_block(text, class_name)
    match = re.search(r'(?m)^\s*%s\s*=\s*(-?\d+)' % re.escape(field), block)
    if not match:
        raise ValueError('Missing const %s.%s' % (class_name, field))
    return int(match.group(1))


def class_text(text, class_name, field):
    block = class_block(text, class_name)
    match = re.search(r"(?m)^\s*%s\s*=\s*'([^']*)'" % re.escape(field), block)
    if not match:
        raise ValueError('Missing const %s.%s' % (class_name, field))
    return match.group(1)


def line_of_row(path, key):
    if not Path(path).is_file():
        return None
    text = read_text(path)
    pattern = r'(?<![\d])%d: \(TD\(' % key
    found = [match.start() for match in re.finditer(pattern, text)]
    if not found:
        return None
    return text[:found[0]].count('\n') + 1


def citation(path, lines, claim, key=None):
    result = {
        'path': str(Path(path).relative_to(ROOT)),
        'lines': str(lines),
        'claim': claim,
        'sha256': sha_file(path) if Path(path).is_file() else None,
    }
    if key is not None:
        result['key'] = str(key)
    return result


def table_citation(name, key, claim):
    return citation(ROOT / TABLE_PATH[name], TABLE_DATA_LINE[name], claim, key)


def listify(value):
    if value is None:
        return []
    if isinstance(value, (set, frozenset)):
        return sorted(value, key=canonical_sort_key)
    if isinstance(value, (list, tuple)):
        return list(value)
    return [value]


def condition_set(value):
    """Original event_condition values may be typed sets or literal strings."""
    if isinstance(value, (set, frozenset)):
        return set(jsonable(item) for item in value)
    if isinstance(value, (list, tuple)):
        return set(jsonable(item) for item in value)
    if not isinstance(value, str):
        return set()
    text = value.strip()
    match = re.match(r'^set\((.*)\)$', text, re.S)
    body = match.group(1) if match else text.strip('[]()')
    result = set()
    for quoted, single, number in re.findall(r'"([^"]*)"|\'([^\']*)\'|(-?\d+)', body):
        if number:
            result.add(int(number))
        elif quoted or single:
            result.add(quoted or single)
    return result


def strip_virtual(row):
    copy = dict(row)
    copy.pop('virtual', None)
    return copy


def entry_sequence(mission, checker):
    paths = listify(mission.get('mission_path'))
    checker(len(paths) == 1, 'Mission %s must have one mission_path' % mission.get('id'))
    match = re.match(r'^暗棋线(\d+)$', paths[0])
    checker(match is not None, 'Unexpected mission_path %r' % paths[0])
    return int(match.group(1)) - 10, paths[0]


def build(source, catalog_path):
    checker = Checker()
    tables = load_source(source, checker)
    city = tables['city_data']
    virtual = tables['city_virtual_area']
    chapters = tables['chapter_mission_data']
    missions = tables['mission']
    hero_attrs = tables['mission_hero_attr']
    links = tables['coc_area_link_data']
    city_links = tables['city_area_link_data']
    area_sfx = tables['city_area_sfx_data']
    puzzle_rooms = tables['puzzle_room']
    puzzle_clues = tables['puzzle_room_clue']
    puzzle_cameras = tables['puzzle_room_camera']
    events = tables['event_content']
    conditions = tables['event_condition']
    condition_map = tables['event_condition_map']
    route_tips = tables['storyroute_tip']
    story_routes = tables['story_route']
    heroes = tables['hero']
    battle_events = tables['battle_event']
    fight_rewards = tables['city_fight_reward']
    random_rewards = tables['reward_random']
    common_rewards = tables['reward_common']
    story_clues = tables['story_clue_info']

    const_text = read_text(CITATION_FILES['const'])
    const = {
        'ROUTE_27': class_text(const_text, 'StoryRouteType', 'ROUTE_27'),
        'ROUTE_27_BRANCH1': class_text(const_text, 'StoryRouteType', 'ROUTE_27_BRANCH1'),
        'ROUTE_27_BRANCH2': class_text(const_text, 'StoryRouteType', 'ROUTE_27_BRANCH2'),
        'MissionMode_MAIN_MISSION': class_int(const_text, 'MissionMode', 'MAIN_MISSION'),
        'MissionType_SURVIVE_TIME': class_int(const_text, 'MissionType', 'SURVIVE_TIME'),
        'BattleType_STAGE': class_int(const_text, 'BattleType', 'STAGE'),
        'UnitCamp_CAMP1': class_int(const_text, 'UnitCamp', 'CAMP1'),
        'UnitCamp_MONSTER': class_int(const_text, 'UnitCamp', 'MONSTER'),
        'UnitCamp_NEUTRAL': class_int(const_text, 'UnitCamp', 'NEUTRAL'),
        'CityStatus_FREE': class_int(const_text, 'CityStatus', 'FREE'),
        'CityStatus_FIGHT': class_int(const_text, 'CityStatus', 'FIGHT'),
        'CityStatus_FALL': class_int(const_text, 'CityStatus', 'FALL'),
        'CityStatus_STRIKE': class_int(const_text, 'CityStatus', 'STRIKE'),
    }
    checker(const['ROUTE_27'] == ROUTE_FAMILY, 'Route 27 constant changed')
    checker(const['ROUTE_27_BRANCH1'] == ROUTE, 'Route 27-1 constant changed')
    checker(const['ROUTE_27_BRANCH2'] == '27-2', 'Route 27-2 constant changed')
    checker(const['MissionMode_MAIN_MISSION'] == 2, 'Main mission mode changed')
    checker(const['MissionType_SURVIVE_TIME'] == 10, 'Survive-time mission type changed')
    checker(const['BattleType_STAGE'] == 1, 'STAGE battle type changed')

    coc_match = re.search(r'(?m)^COC_HERO_LIMIT_SCENE\s*=\s*\(([^)]*)\)', const_text)
    checker(coc_match is not None, 'Missing COC_HERO_LIMIT_SCENE')
    coc_scenes = tuple(int(value) for value in re.findall(r'\d+', coc_match.group(1)))
    checker(coc_scenes == (482, 483, 484, 485, 486, 486, 487, 488),
            'COC_HERO_LIMIT_SCENE changed: %r' % (coc_scenes,))
    checker(set(COC_SCENES).issubset(set(coc_scenes)),
            'COC scene set is not covered by COC_HERO_LIMIT_SCENE')

    route_family = story_routes[ROUTE_FAMILY]
    checker(route_family['id'] == ROUTE_FAMILY, 'Story route 27 id mismatch')
    checker(ROUTE in route_family['routes'], 'Story route 27 lacks 27-1')
    checker('27-2' in route_family['routes'], 'Story route 27 lacks 27-2')

    # Area rows and the original link chain.
    chain_rows = sorted(links.values(), key=lambda row: row['id'])
    checker(len(chain_rows) == 8, 'Expected eight COC link rows')
    checker([row['id'] for row in chain_rows] == list(range(1, 9)),
            'COC link ids are not 1..8')
    checker(city_links == links, 'city_area_link_data differs from coc_area_link_data')
    chain = []
    previous = None
    for row in chain_rows:
        checker(row.get('model_name') == 'area%d' % row['area'],
                'Unexpected link model for area %s' % row['area'])
        if previous is not None:
            checker(row.get('pre_id') == previous['id'],
                    'Link pre_id chain broken at %s' % row['id'])
            checker(previous.get('link_area') == row['area'],
                    'Link area chain broken at %s' % row['id'])
        chain.append(row['area'])
        previous = row
    checker(tuple(chain) == CHAIN_AREAS, 'COC area link chain changed: %r' % (chain,))
    checker([row['area'] for row in chain_rows if row.get('link_area')] ==
            [7, 10000, 6, 10001, 4, 10002, 10003],
            'COC link source areas changed')

    hero_row = heroes[TARGET_HERO]
    checker(hero_row['name'] == '彼安汀', 'Target hero 135 changed')

    areas = []
    for area_id in VIRTUAL_AREAS:
        row = city[area_id]
        virtual_row = virtual[area_id]
        checker(row['id'] == area_id and row.get('virtual') == 1,
                'Area %s is not an original virtual area' % area_id)
        checker(strip_virtual(row) == virtual_row,
                'city_virtual_area/%s differs from city_data' % area_id)
        previous_rows = [item for item in chain_rows if item.get('link_area') == area_id]
        next_rows = [item for item in chain_rows if item['area'] == area_id]
        checker(len(previous_rows) == 1, 'Area %s needs one predecessor link' % area_id)
        checker(len(next_rows) == 1, 'Area %s needs one successor link' % area_id)
        previous_area = previous_rows[0]['area']
        next_area = next_rows[0]['link_area']
        require = row['area_require']
        sfx = area_sfx[(ROUTE, area_id)]
        checker(sfx['area'] == area_id and sfx['id'] == ROUTE,
                'Area sfx row mismatch for %s' % area_id)
        areas.append({
            'id': area_id,
            'kind': 'virtual',
            'name': row['name'],
            'desc': row['desc'],
            'area_require': row['area_require'],
            'route_requirement': listify(require.get(ROUTE)),
            'default_requirement': listify(require.get('-1')),
            'pre_area': previous_area,
            'next_area': next_area,
            'chain_index': CHAIN_AREAS.index(area_id),
            'sfx': sfx,
            'city_virtual_area_row': virtual_row,
            'original_row': row,
            'citations': [
                table_citation('city_data', area_id,
                               'virtual area %s row (virtual=1)' % area_id),
                table_citation('city_virtual_area', area_id,
                               'virtual area %s projection row' % area_id),
                table_citation('coc_area_link_data', next_rows[0]['id'],
                               'area %s link row' % area_id),
            ],
        })

    # Scene/chapter/mission closure.
    scene_rows = []
    for scene in COC_SCENES:
        sequence, mission_path = entry_sequence(missions[scene], checker)
        mission = missions[scene]
        area_id = mission['ch']
        kind = 'virtual' if area_id in VIRTUAL_AREAS else 'normal'
        checker(kind == ('virtual' if scene in CORE_VIRTUAL_SCENES else 'normal'),
                'Scene %s area kind changed' % scene)
        checker(mission['id'] == scene, 'Mission key %s mismatched' % scene)
        checker(mission['release'] == 1, 'Mission %s is not released' % scene)
        checker(mission['system_type'] == const['MissionMode_MAIN_MISSION'],
                'Mission %s is not MAIN_MISSION' % scene)
        checker(mission['type'] == const['MissionType_SURVIVE_TIME'],
                'Mission %s is not SURVIVE_TIME' % scene)
        checker(listify(mission.get('target_hero')) == [TARGET_HERO],
                'Mission %s target_hero changed' % scene)
        checker(mission['least_hero_num'] == 1 and mission['max_hero_num'] == 1,
                'Mission %s party bounds changed' % scene)
        checker(mission['va'] == 2, 'Mission %s action cost changed' % scene)
        checker(mission['prize'] == 1, 'Mission %s prize flag changed' % scene)
        for absent in ('fatigue', 'overFatigue', 'force_recommend'):
            checker(absent not in mission, 'Mission %s now defines %s' % (scene, absent))
        checker('cost' not in mission and 'items' not in mission and 'money' not in mission,
                'Mission %s now has an unexpected item cost field' % scene)
        checker(mission['limit_time'] == 1800, 'Mission %s limit_time changed' % scene)
        times = listify(mission.get('mission_time'))
        checker(len(times) == 3 and times[0] == '限时', 'Mission %s mission_time changed' % scene)
        timer_seconds = int(times[1])
        timeout_result = int(times[2])
        checker(timer_seconds in (120, 180), 'Mission %s timer changed' % scene)
        checker(timeout_result == 5, 'Mission %s timeout sentinel changed' % scene)

        chapter_rows = []
        for key, row in chapters.items():
            if any(scene in listify(group) for group in row['section'].values()):
                chapter_rows.append((key, row))
        checker(len(chapter_rows) == 1, 'Scene %s must have one chapter row' % scene)
        chapter_key, chapter = chapter_rows[0]
        checker(chapter_key == (area_id, 0, ROUTE, 0),
                'Scene %s chapter key changed: %r' % (scene, (chapter_key,)))
        checker(chapter['chapter'] == area_id and chapter['route'] == ROUTE and
                chapter['specialStage'] == 0 and chapter['status'] == 0,
                'Scene %s chapter row mismatch' % scene)
        groups = {int(key): listify(value) for key, value in chapter['section'].items()}
        checker(set(groups) == set(range(10)), 'Scene %s chapter groups changed' % scene)
        hits = [index for index in range(10) if groups[index] == [scene]]
        checker(len(hits) == 1, 'Scene %s is not a single chapter group member' % scene)
        for index in range(10):
            if index != hits[0]:
                checker(groups[index] == [], 'Scene %s chapter group %s is not empty' % (scene, index))

        attr = hero_attrs[(scene, TARGET_HERO)]
        checker(attr['mission_id'] == scene and attr['heroid'] == TARGET_HERO,
                'Mission hero attr %s mismatch' % scene)
        checker(attr['hero_name'] == hero_row['name'], 'Mission hero name %s mismatch' % scene)

        setup_events = []
        for event_id in listify(mission.get('init_events')):
            checker(event_id in battle_events, 'Scene %s battle event %s missing' % (scene, event_id))
            setup_events.append({'id': event_id, 'row': battle_events[event_id]})

        event_id = 1435 + sequence - 1
        checker(event_id in events, 'Scene %s completion event %s missing' % (scene, event_id))
        event_row = events[event_id]
        checker(event_row['completeConds'].get('battle') == (scene,),
                'Scene %s completion event battle mismatch' % scene)
        checker(event_id in conditions, 'Scene %s entry condition missing' % scene)
        condition_row = conditions[event_id]
        checker(ROUTE in condition_set(condition_row['conds'].get(52)),
                'Scene %s entry condition route changed' % scene)
        checker('%d:1' % area_id in condition_set(condition_row['conds'].get(100)),
                'Scene %s entry click area changed' % scene)
        checker(event_row.get('release') is False, 'Scene %s entry event release changed' % scene)

        wire = {
            'protocol': 'combatOfflineRequest',
            't': const['BattleType_STAGE'],
            's': scene,
            'h': [TARGET_HERO],
            'd': {'a': area_id},
            'battle_type': const['BattleType_STAGE'],
            'battle_type_name': 'STAGE',
        }
        virtual_area = next((item for item in areas if item['id'] == area_id), None)
        scene_rows.append({
            'sequence': sequence,
            'scene': scene,
            'key': str(scene),
            'area': area_id,
            'area_kind': kind,
            'area_chain': list(CHAIN_AREAS),
            'chain_index': CHAIN_AREAS.index(area_id),
            'area_gate': {
                'area': area_id,
                'kind': kind,
                'area_require': city[area_id]['area_require'],
                'route_requirement': listify(city[area_id]['area_require'].get(ROUTE)),
                'family_route_requirement': listify(city[area_id]['area_require'].get(ROUTE_FAMILY)),
                'pre_area': virtual_area['pre_area'] if virtual_area else None,
                'next_area': virtual_area['next_area'] if virtual_area else None,
            },
            'family': 'coc-stealth',
            'route': ROUTE,
            'mission_path': mission_path,
            'name': mission['name'],
            'desc': mission['desc'],
            'require': mission.get('require'),
            'data_source': mission.get('dataSource'),
            'event_module': {
                'name': 'event_anqixian11',
                'resolution': 'direct' if scene == 482 else 'inherit_mission',
                'inherit_mission': mission.get('inherit_mission'),
            },
            'system_type': {
                'value': mission['system_type'],
                'name': 'MAIN_MISSION',
            },
            'type': {
                'value': mission['type'],
                'name': 'SURVIVE_TIME',
            },
            'chapter': {
                'key': list(chapter_key),
                'group': hits[0],
                'section': chapter['section'],
            },
            'map': {
                'name': mission.get('mapName'),
                'paths': listify(mission.get('map_path')),
                'end_position': listify(mission.get('end_position')),
                'angle': mission.get('angle'),
                'pre_load': listify(mission.get('pre_load')),
                'music': mission.get('music'),
                'sound': mission.get('sound'),
            },
            'init_events': setup_events,
            'wire': wire,
            'party': {
                'target_hero': [TARGET_HERO],
                'minimum': mission['least_hero_num'],
                'maximum': mission['max_hero_num'],
                'forced': True,
                'forced_by': 'COC_HERO_LIMIT_SCENE',
                'request_heroes': [TARGET_HERO],
            },
            'target_hero': {
                'id': TARGET_HERO,
                'name': hero_row['name'],
                'hero_type': hero_row.get('hero_type'),
                'attack_type': hero_row.get('attack_type'),
                'armor_type': hero_row.get('armor_type'),
                'fatigue_value': hero_row.get('fatigueValue'),
                'config': attr,
            },
            'cost': {
                'action': mission['va'],
                'fatigue': mission.get('fatigue', 0),
                'va': mission['va'],
                'overFatigue': mission.get('overFatigue', 0),
                'force_recommend': mission.get('force_recommend', 0),
                'items': [],
                'money': 0,
                'formula': 'action=va; fatigue=fatigue if force>=force_recommend else overFatigue',
                'source_fields': {
                    'va': mission['va'],
                    'fatigue': 'absent',
                    'overFatigue': 'absent',
                    'force_recommend': 'absent',
                },
            },
            'time': {
                'mission_time': times,
                'timer_seconds': timer_seconds,
                'timeout_win_camp': timeout_result,
                'timeout_win': (timeout_result == const['UnitCamp_CAMP1']),
                'limit_seconds': mission['limit_time'],
                'timeout_outcome': 'failure' if timeout_result not in
                    (const['UnitCamp_CAMP1'],) else 'victory',
            },
            'reward': {
                'prize': mission['prize'],
                'per_mission_reward_id': None,
                'successEvent': mission.get('successEvent'),
                'failEvent': mission.get('failEvent'),
                'completion_event': event_id,
                'base_table': 'city_fight_reward',
                'base_key': 'player_level_at_admission',
                'drop_pool_ids': [304],
                'drop_policy': 'level-based offline reimplementation; original server authoritative',
            },
            'success': {
                'kind': 'event_completion',
                'event': event_id,
                'completeConds': event_row.get('completeConds'),
                'evidence': 'event_content[%d].completeConds.battle contains %d' % (event_id, scene),
            },
            'fail': {
                'kind': 'timeout',
                'timer_seconds': timer_seconds,
                'win_camp': timeout_result,
                'win': timeout_result == const['UnitCamp_CAMP1'],
                'failEvent': mission.get('failEvent'),
                'evidence': 'mission_time[2] is passed to finish_combat(win_camp) and the client compares battle.camp == win_camp',
            },
            'drop': {
                'mission_specific': False,
                'pool_ids': [304],
                'table': 'reward_random',
                'policy': 'level-based offline reimplementation; original server authoritative',
            },
            'original_row': mission,
            'mission_hero_override': attr,
            'economy': [
                mission['va'], mission.get('fatigue', 0), mission.get('overFatigue', 0),
                mission.get('force_recommend', 0), mission['least_hero_num'],
                mission['max_hero_num'], mission['prize'],
            ],
            'citations': [
                table_citation('mission', scene, 'mission row %s' % scene),
                table_citation('chapter_mission_data', list(chapter_key),
                               'chapter row for scene %s' % scene),
                table_citation('mission_hero_attr', list((scene, TARGET_HERO)),
                               'hero 135 combat config for scene %s' % scene),
                table_citation('coc_area_link_data', next(
                    row['id'] for row in chain_rows if row['area'] == area_id),
                    'area link for scene %s' % scene),
                table_citation('city_area_sfx_data', list((ROUTE, area_id)),
                               'route 27-1 area sfx for scene %s' % scene),
                citation(CITATION_FILES['const'], '2109-2110',
                         'COC_HERO_LIMIT_SCENE contains all seven scenes'),
                citation(CITATION_FILES['battle_stage_member'], '86-107',
                         'stage admission then forces heroes=list(target_hero)'),
                citation(CITATION_FILES['combat_member'], '72-79',
                         "wire {'t': type, 's': scene, 'h': heroes, 'd': data}"),
                citation(CITATION_FILES['city_data_py'], '171-181',
                         'action=va and fatigue/overFatigue cost fields'),
                citation(CITATION_FILES['logic_event_base'], '272-298',
                         'mission_time timer and limit_time expiry'),
                citation(CITATION_FILES['view_event_base'], '738',
                         'win flag is battle.camp == win_camp'),
            ],
            'entry_event': {'id': event_id, 'row': event_row, 'condition': condition_row},
        })

    checker([row['sequence'] for row in scene_rows] == list(range(1, 8)),
            'COC scene sequence is not 1..7')
    checker([row['name'] for row in scene_rows] ==
            ['交界潜行 · 一', '交界潜行 · 二', '交界潜行 · 三', '交界潜行 · 四',
             '交界潜行 · 五', '交界潜行 · 六', '交界潜行 · 七'],
            'COC scene names changed')

    # Puzzle room 4 and its clues.
    room = puzzle_rooms[4]
    checker(room['room_id'] == 4, 'Puzzle room 4 id changed')
    checker(room['clear_event'] == 3444 and room['not_clear_event'] == 3455,
            'Puzzle room 4 clear events changed')
    checker(room['scene_name'] == 'scene2/hd/g58_jtwj_hd.scn',
            'Puzzle room 4 scene changed')
    trigger = events[3437]
    checker(trigger.get('puzzle_room') == 4, 'Puzzle room 4 trigger changed')
    checker(trigger.get('patrolEvent') == 1, 'Puzzle room 4 is not a patrol event')
    checker(3444 in events and 3455 in events, 'Puzzle room 4 clear events missing')
    checker(3444 in listify(events[3455].get('mutexEvent')), 'Puzzle clear mutex changed')
    checker(3455 in listify(events[3444].get('mutexEvent')), 'Puzzle fail mutex changed')
    trigger_condition = conditions[3437]
    checker('27-2' in condition_set(trigger_condition['conds'].get(52)),
            'Puzzle room 4 route condition changed')
    checker(3444 in condition_set(trigger_condition['conds'].get(11)),
            'Puzzle room 4 not-completed condition changed')
    checker(3436 in condition_set(trigger_condition['conds'].get(1)),
            'Puzzle room 4 predecessor changed')
    checker(condition_map[754]['id'] == 3437, 'Puzzle condition map changed')

    clue_rows = [dict(row, id=key) for key, row in sorted(puzzle_clues.items())
                 if row['room_id'] == 4]
    checker([row['id'] for row in clue_rows] == [17, 18, 19, 20, 21],
            'Puzzle room 4 clues changed')
    camera_rows = [dict(row, id=key) for key, row in sorted(puzzle_cameras.items())
                   if row['room_id'] == 4]
    checker([row['id'] for row in camera_rows] == [9, 10, 11, 12, 13],
            'Puzzle room 4 cameras changed')
    tip_key = ('27-2', 5)
    checker(tip_key in route_tips, 'Puzzle route tip 27-2/day5 missing')
    tip = route_tips[tip_key]
    checker(listify(tip['check_paras']) == [3444], 'Puzzle route tip check changed')

    puzzle_clue_context = []
    for clue_id, row in sorted(story_clues.items()):
        if row.get('route') == '27-2':
            puzzle_clue_context.append({
                'clue_id': clue_id,
                'area_id': row.get('area_id'),
                'condition_text': row.get('condition_text'),
                'short_info': row.get('short_info'),
                'long_info_sha256': sha_bytes(row.get('long_info', '').encode('utf-8')),
            })
    checker(len(puzzle_clue_context) == 5, 'Route 27-2 story clue set changed')
    checker([item['clue_id'] for item in puzzle_clue_context] == [133, 134, 135, 136, 137],
            'Route 27-2 story clue ids changed')

    puzzle = {
        'room': {
            'id': 4,
            'row': room,
            'scene_name': room['scene_name'],
            'bgm': room['bgm'],
            'camera_name': room['camera_name'],
            'client_dialogue': room['client_dialogue'],
        },
        'events': {
            'trigger': {'id': 3437, 'row': trigger, 'condition': trigger_condition},
            'clear': {'id': 3444, 'row': events[3444]},
            'not_clear': {'id': 3455, 'row': events[3455]},
        },
        'route': {
            'id': '27-2',
            'family': '27',
            'tip': {'key': list(tip_key), 'row': tip},
            'story_route': story_routes['27'],
        },
        'clues': clue_rows,
        'cameras': camera_rows,
        'wire': {
            'protocol': 'puzzleRoomGetClue',
            'args': {'c': '<clue_id>'},
            'reply': 'puzzleRoomGetClueReturn',
            'reply_fields': ['r', 'c', 'g'],
            'state': 'storyData.puzzle_room_clues',
            'clue_ids': [row['id'] for row in clue_rows],
        },
        'story_clue_context': puzzle_clue_context,
        'linkage': {
            'target_hero': TARGET_HERO,
            'target_hero_name': hero_row['name'],
            'route_family': '27',
            'virtual_area_dependency': False,
            'note': ('Puzzle room 4 is a patrol event on route 27-2 '
                     '(condition 3437), not gated by areas 10000..10003. '
                     'It shares the COC/Bianca story line with route 27-1.'),
        },
        'citations': [
            table_citation('puzzle_room', 4, 'puzzle room 4 row'),
            table_citation('puzzle_room_clue', 17, 'quest clue 17 row'),
            table_citation('puzzle_room_clue', 21, 'quest clue 21 row'),
            table_citation('puzzle_room_camera', 9, 'puzzle camera 9 row'),
            table_citation('puzzle_room_camera', 13, 'puzzle camera 13 row'),
            citation(CITATION_FILES['story_member'], '423-436',
                     'puzzleRoomGetClue request/reply contract'),
            citation(CITATION_FILES['city_jiemi'], '78-88',
                     'puzzle room clue model selection by room_id'),
            citation(CITATION_FILES['city_jiemi'], '187-190',
                     'clue click calls puzzleRoomGetClue(clue_id)'),
            citation(ROOT / 'offline/runtime/offline_conditions.py', '203-238',
                     'offline condition mapping: kind 3 patrol area, kind 8 area status, kind 52 route'),
        ],
    }

    # Reward/drop boundary evidence.
    reward_levels = sorted(fight_rewards)
    checker(reward_levels == list(range(1, 201)),
            'city_fight_reward level set changed')
    checker(all(listify(row.get('items')) == [304] for row in fight_rewards.values()),
            'city_fight_reward item pool changed')
    pool = random_rewards[304]
    weights = list(pool['weights'])
    checker(len(weights) == 154, 'reward_random 304 weight count changed')
    checker(dict(weights)[0] == 147000, 'reward_random 304 no-drop weight changed')
    checker(sum(weight for _, weight in weights) == 174084,
            'reward_random 304 weight total changed')
    nonzero = [reward_id for reward_id, weight in weights if reward_id != 0]
    checker(len(nonzero) == 153, 'reward_random 304 reward id count changed')
    checker(all(reward_id in common_rewards for reward_id in nonzero),
            'reward_random 304 references missing reward_common rows')
    for reward_id in nonzero:
        definition = common_rewards[reward_id]
        checker(set(definition) == {'id', 'treasure', 'treasureNum', 'treasureLevel', 'tradeType'},
                'reward_common %s schema changed' % reward_id)

    reward_model = {
        'per_mission_reward_id': None,
        'prize_field': 1,
        'base_table': {
            'name': 'city_fight_reward',
            'rows': len(fight_rewards),
            'levels': [min(reward_levels), max(reward_levels)],
            'fields': ['lv', 'money', 'exp', 'friendly', 'items', 'show_items',
                       'green_show_items', 'not_green_show_items', 'empty_show_items'],
            'samples': {str(level): {
                key: fight_rewards[level].get(key)
                for key in ('lv', 'money', 'exp', 'friendly', 'items')
            } for level in (1, 50, 100, 150, 200)},
        },
        'drop_pool': {
            'id': 304,
            'weights_entries': len(weights),
            'no_drop_reward_id': 0,
            'no_drop_weight': dict(weights)[0],
            'reward_entries': len(nonzero),
            'weight_total': sum(weight for _, weight in weights),
            'reward_common_rows': len(common_rewards),
            'weights_sha256': sha_bytes(canonical(weights)),
        },
        'policy': ('No mission-scoped reward row exists. The original client forwards '
                   'the battle result to the server; only a local offline '
                   'reimplementation maps player level to city_fight_reward and then '
                   'weighted pool 304 to reward_common.'),
        'offline_compat_policy': {
            'status': 'inferred/offline, not original-server exact',
            'win_only': True,
            'action_cost': 'mission.va (2) once, same transaction as win',
            'base_reward': 'city_fight_reward[player_level]',
            'drop': 'reward_random[304] -> reward_common; preserve no-drop',
            'loss_reward': 'none',
            'commit': 'one Profile/Progress transaction/receipt; replay must not recharge/regrant',
        },
        'citations': [
            table_citation('city_fight_reward', 1, 'level-1 fight reward row'),
            table_citation('city_fight_reward', 200, 'level-200 fight reward row'),
            citation(ROOT / 'analysis/project7/scripts/com/data/cdata/reward_random.marshal',
                     'key 304', 'weighted drop pool 304', 304),
            citation(ROOT / 'analysis/project7/scripts/com/data/cdata/reward_common.marshal',
                     'key 833', 'first treasure definition referenced by pool 304', 833),
            citation(ROOT / 'analysis/project7/scripts/com/data/cdata/reward_common.marshal',
                     'key 5773', 'last treasure definition referenced by pool 304', 5773),
        ],
    }

    # Event references around the route; effects stay owned by CityCoreA.
    progression = []
    for event_id in range(1432, 1453):
        row = events.get(event_id)
        if row is None:
            continue
        fields = {field: listify(row[field]) for field in
                  ('areaFree', 'areaFight', 'areaLock', 'areaUnlock', 'areaFall', 'areaStrike')
                  if row.get(field)}
        progression.append({
            'id': event_id,
            'name': row.get('name'),
            'area_effects': fields,
            'events': listify(row.get('events')),
            'completeConds': row.get('completeConds'),
            'condition': conditions.get(event_id),
            'owner': 'CityCoreA',
            'consume': False,
        })

    # Live catalog compatibility (read-only).
    live = {'available': False}
    catalog_path = Path(catalog_path) if catalog_path else None
    if catalog_path and catalog_path.is_file():
        packed = catalog_path.read_bytes()
        root = json.loads(gzip.decompress(packed))
        checker(root.get('schema') == 'project7-story-city-v1',
                'Live story city schema changed')
        live_areas = {row['id']: row for row in root['areas']}
        live_missions = root['missions']
        live_chapters = root['chapters']
        checker(all(area_id in live_areas and live_areas[area_id]['kind'] == 'virtual'
                    for area_id in VIRTUAL_AREAS),
                'Live catalog lacks a virtual area')
        for scene in CORE_VIRTUAL_SCENES:
            row = live_missions.get(str(scene))
            checker(row is not None, 'Live catalog lacks scene %s' % scene)
            checker(row['wire'] == 1 and row['party'] == [TARGET_HERO],
                    'Live catalog wire/party changed for %s' % scene)
            checker(row['minimum'] == 1 and row['maximum'] == 1,
                    'Live catalog party bounds changed for %s' % scene)
            checker(row['economy'] == [2, 0, 0, 0, 1, 1, 1],
                    'Live catalog economy changed for %s' % scene)
            checker(row['mission_hero_override'] is not None,
                    'Live catalog missing the promoted hero override for %s' % scene)
        checker(all(str(scene) in live_missions for scene in INTERSTITIAL_SCENES),
                'Live catalog missing an interstitial COC scene')
        live_chapter_keys = {(row['area'], row['route'], tuple(tuple(group) for group in row['groups']))
                             for row in live_chapters}
        for scene in CORE_VIRTUAL_SCENES:
            area_id = missions[scene]['ch']
            found = any(area == area_id and route == ROUTE and
                        [list(group) for group in groups] == [[scene]] + [[]] * 9
                        for area, route, groups in live_chapter_keys)
            checker(found, 'Live catalog chapter projection changed for %s' % scene)
        live = {
            'available': True,
            'schema': root['schema'],
            'asset_sha256': sha_bytes(packed),
            'expanded_sha256': sha_bytes(json.dumps(root, sort_keys=True,
                                                     ensure_ascii=True,
                                                     separators=(',', ':')).encode('ascii')),
            'virtual_areas': [area_id for area_id in VIRTUAL_AREAS if area_id in live_areas],
            'present_scenes': [scene for scene in COC_SCENES if str(scene) in live_missions],
            'missing_scenes': [scene for scene in COC_SCENES if str(scene) not in live_missions],
            'mission_hero_override_present': [
                scene for scene in COC_SCENES
                if live_missions[str(scene)].get('mission_hero_override') is not None
            ],
        }
    else:
        live['note'] = 'live catalog not present at %s' % catalog_path

    citations = [
        citation(CITATION_FILES['const'], '2109-2110',
                 'COC_HERO_LIMIT_SCENE = (482,483,484,485,486,486,487,488)'),
        citation(CITATION_FILES['const'], '1921-1922', 'BattleType.STAGE = 1'),
        citation(CITATION_FILES['const'], '1957-1959', 'MissionMode.MAIN_MISSION = 2'),
        citation(CITATION_FILES['const'], '860-870', 'MissionType.SURVIVE_TIME = 10'),
        citation(CITATION_FILES['const'], '918-919', 'TIMEBAR_MISSION includes SURVIVE_TIME'),
        citation(CITATION_FILES['const'], '3219-3226', 'CityStatus FREE/FIGHT/FALL/STRIKE'),
        citation(CITATION_FILES['city_data_py'], '171-181', 'stage action/fatigue cost'),
        citation(CITATION_FILES['battle_stage_member'], '86-107',
                 'virtual area admission and forced COC party'),
        citation(CITATION_FILES['combat_member'], '72-79', 'combatOfflineRequest wire'),
        citation(CITATION_FILES['battle_stage_panel'], '207-208',
                 'hero button hidden and qianxing shown for COC scenes'),
        citation(CITATION_FILES['event_logic'], '24-45',
                 'dataSource event module, inherit_mission fallback'),
        citation(CITATION_FILES['event_anqixian11'], '8-17',
                 'event_anqixian11 only schedules the minimap'),
        citation(CITATION_FILES['logic_event_base'], '263-266',
                 'mission init_events are processed as battle setup events'),
        citation(CITATION_FILES['logic_event_base'], '272-298',
                 'mission_time timer runs finish_combat(int(mission_succ))'),
        citation(CITATION_FILES['view_event_base'], '738',
                 'client win flag is battle.camp == win_camp'),
        citation(CITATION_FILES['storyline_27'], '142-161',
                 'virtual area visibility follows predecessor FREE state'),
        citation(CITATION_FILES['storyline_27'], '225-231',
                 'virtual area click allowed only on route 27-1 with FIGHT status'),
        citation(CITATION_FILES['story_member'], '423-436', 'puzzleRoomGetClue contract'),
        citation(CITATION_FILES['city_jiemi'], '187-190', 'puzzle clue click'),
        citation(ROOT / 'offline/runtime/offline_stage.py', '88-101',
                 'current virtual area family is rejected by basic_city_stage_chain'),
        citation(ROOT / 'offline/runtime/offline_battle.py', '204-300',
                 'offline settlement maps reward_level to city_fight_reward and pool 304'),
        table_citation('city_fight_reward', 1, 'base fight reward row'),
        citation(ROOT / 'analysis/project7/scripts/com/data/cdata/reward_random.marshal',
                 'key 304', 'weighted drop pool 304', 304),
        citation(CITATION_FILES['decompiled_event_content'], '246',
                 'event rows 3437/3444/3455 for puzzle room 4', 3437),
        citation(CITATION_FILES['decompiled_event_content'], '26',
                 'event rows 1435..1452 for COC progression', 1435),
    ]
    for scene in COC_SCENES:
        citations.append(table_citation('mission', scene, 'COC mission row'))
        citations.append(table_citation('mission_hero_attr', list((scene, TARGET_HERO)),
                                        'COC hero config row'))
        citations.append(table_citation('chapter_mission_data', list((missions[scene]['ch'], 0, ROUTE, 0)),
                                        'COC chapter row'))
    for area_id in VIRTUAL_AREAS:
        citations.append(table_citation('city_data', area_id, 'virtual area row'))
        citations.append(table_citation('city_virtual_area', area_id, 'virtual area projection'))
    citations.append(table_citation('puzzle_room', 4, 'puzzle room 4 row'))
    for clue_id in (17, 21):
        citations.append(table_citation('puzzle_room_clue', clue_id, 'puzzle room 4 clue'))
    for camera_id in (9, 13):
        citations.append(table_citation('puzzle_room_camera', camera_id, 'puzzle room 4 camera'))
    citations.append(table_citation('event_condition', 3437, 'puzzle room 4 trigger condition'))
    citations.append(table_citation('storyroute_tip', list(('27-2', 5)),
                                    'puzzle room 4 route tip'))
    citations.append(table_citation('coc_area_link_data', 1, 'COC link chain head'))
    citations.append(table_citation('coc_area_link_data', 8, 'COC link chain tail'))
    citations.append(table_citation('city_area_sfx_data', list((ROUTE, 10000)),
                                    'route 27-1 virtual area sfx'))

    boundaries = {
        'official_policy': [
            'Mission admission and team selection are client-side; result settlement '
            'and drops are server-authoritative in the original game.',
            'The legacy offline_stage.basic_city_stage_chain 1..8 rejection is a legacy reference only '
            'and is not current Main evidence. Main dispatch is fixed DEX/StoryCity/Gateway; the 482..488 '
            'family must be admitted through that actual dispatch and remains unproven here.',
            'Area status/lock effects belong to the CityCoreA cityEffects contract and are not '
            'reproduced here; progression events are reference-only.',
            'Namespace remains q7StoryCity; this contract does not enable Main or menu 25.',
        ],
        'unknown': [
            'The objective-complete success trigger lives in the PvE scene asset '
            '(g58_*_pve.scn), not in cdata; only timeout failure and battle completion events '
            'are table-derivable.',
            'mission_time[2] literal 5 is not a UnitCamp value; timeout is derived to be a '
            'failure from battle.camp == win_camp, not from a documented constant.',
            'Client dialogue IDs 21491..21495 for clues 17..21 are preserved from cdata; their '
            'dialogue-table text still needs a static literal/source join. The clue_des text is '
            'available from decompiled puzzle_room_clue and must not be dropped.',
            'Original server reward/drop rule for MAIN_MISSION scenes is not present in client '
            'tables; city_fight_reward is the offline runtime mapping, not proven original policy.',
            'Event condition kinds 3/4/8/52/100/102 are server-side; the offline runtime mapping '
            'is cited only to explain the literal values.',
        ],
        'derived': [
            'Scene 482 resolves event_anqixian11 directly; 483..488 resolve it through '
            'inherit_mission=482 because no event_anqixianNN modules exist for 12..17.',
            'COC party is exactly [135] because BattleStageMember replaces heroes with '
            'list(target_hero) before admission.',
            'Timeout is failure because the third mission_time value (5) is not CAMP1 (1) and '
            'the client compares battle.camp == win_camp.',
        ],
    }

    merge = {
        'target_schema': 'project7-story-city-v1',
        'namespace': NAMESPACE,
        'areas': 'Replace/verify the four virtual rows 10000..10003; pre_area/next_area come from coc_area_link_data.',
        'chapters': 'Verify the four virtual chapter rows and add the three interstitial rows keyed [area,0,"27-1",0]; the live catalog omits 483/485/488.',
        'missions': 'Replace/verify 482/484/486/487 and add 483/485/488 with wire=1, party=[135], minimum=maximum=1, economy=[2,0,0,0,1,1,1].',
        'mission_hero_override': 'Use mission_hero_override from this contract; the live producer keys mission_hero_attr by (scene,135) but reads an integer, yielding null.',
        'puzzle_room': 'Puzzle room 4 needs a new catalog field/version; the live project7-story-city-v1 catalog has no puzzle section.',
        'do_not_consume': ['progression_events (CityCoreA owns cityEffects)', 'area status/lock projections'],
    }

    data = {
        'schema': SCHEMA,
        'policy': POLICY,
        'consumer_namespace': NAMESPACE,
        'scope': {
            'family': 'coc-stealth-route-27-1',
            'route': ROUTE,
            'route_family': ROUTE_FAMILY,
            'target_hero': TARGET_HERO,
            'virtual_areas': list(VIRTUAL_AREAS),
            'scenes': list(COC_SCENES),
            'virtual_scenes': list(CORE_VIRTUAL_SCENES),
            'interstitial_scenes': list(INTERSTITIAL_SCENES),
            'puzzle_rooms': [4],
        },
        'client_constants': const,
        'source_pins': PINS,
        'route': {
            'id': ROUTE_FAMILY,
            'chapters': route_family['routes'],
            'branch': {'id': ROUTE, 'name': 'ROUTE_27_BRANCH1'},
            'puzzle_branch': {'id': '27-2', 'name': 'ROUTE_27_BRANCH2'},
        },
        'areas': areas,
        'area_links': chain_rows,
        'missions': scene_rows,
        'progression_events': progression,
        'puzzle_room': puzzle,
        'reward_model': reward_model,
        'live_catalog': live,
        'merge': merge,
        'boundaries': boundaries,
        'citation_method': (
            'Each citation points at the decompiled source row line or the client '
            'logic line. Data values come from the pinned .marshal tables; the cited '
            '.py rows were cross-checked against those pins during authoring and the '
            'file sha256 is recorded with every citation.'),
        'citations': citations,
        'checks': {'count': checker.count, 'passed': checker.count, 'failed': 0},
    }
    return data, checker


def summarize(data, data_bytes, pretty_bytes):
    sections = {
        'areas': data['areas'],
        'missions': data['missions'],
        'puzzle_room': data['puzzle_room'],
        'reward_model': data['reward_model'],
        'route': data['route'],
    }
    return {
        'schema': SCHEMA,
        'policy': POLICY,
        'consumer_namespace': NAMESPACE,
        'data_file': 'virtual-data-v1.json',
        'data_sha256': sha_bytes(data_bytes),
        'data_size': len(pretty_bytes),
        'generator': {
            'path': 'tools/project7_story_city_virtual_data.py',
            'sha256': sha_file(Path(__file__)),
        },
        'source_pins': PINS,
        'source_pin_set_sha256': sha_bytes(canonical(PINS)),
        'section_hashes': {name: sha_bytes(canonical(value))
                           for name, value in sections.items()},
        'counts': {
            'virtual_areas': len(data['areas']),
            'chapters': len(data['missions']),
            'missions': len(data['missions']),
            'virtual_missions': len(data['scope']['virtual_scenes']),
            'interstitial_missions': len(data['scope']['interstitial_scenes']),
            'puzzle_rooms': 1,
            'puzzle_clues': len(data['puzzle_room']['clues']),
            'puzzle_cameras': len(data['puzzle_room']['cameras']),
            'progression_events': len(data['progression_events']),
            'citations': len(data['citations']),
        },
        'checks': data['checks'],
        'merge': data['merge'],
        'live_catalog': data['live_catalog'],
        'boundaries': data['boundaries'],
    }


def write_output(output, data, contract, force):
    output = Path(output)
    if output.exists() and not force:
        raise ValueError('Existing output refused: %s' % output)
    output.mkdir(parents=True, exist_ok=True)
    data_text = pretty(data)
    (output / 'virtual-data-v1.json').write_text(data_text, encoding='utf-8')
    (output / 'contract-v1.json').write_text(
        json.dumps(contract, sort_keys=True, ensure_ascii=False, indent=1) + '\n',
        encoding='utf-8')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, default=DEFAULT_SOURCE)
    parser.add_argument('--catalog', type=Path, default=DEFAULT_CATALOG)
    parser.add_argument('--output', type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument('--force', action='store_true')
    parser.add_argument('--check', action='store_true',
                        help='Rebuild and compare with the existing output')
    args = parser.parse_args()

    data, checker = build(args.source, args.catalog)
    data_bytes = canonical(data)
    if args.check:
        existing = json.loads((args.output / 'virtual-data-v1.json').read_text(encoding='utf-8'))
        contract = json.loads((args.output / 'contract-v1.json').read_text(encoding='utf-8'))
        if canonical(existing) != data_bytes:
            raise SystemExit('Virtual data differs from source')
        if contract['data_sha256'] != sha_bytes(data_bytes):
            raise SystemExit('Contract hash differs from source')
        print(json.dumps({'status': 'ok', 'data_sha256': sha_bytes(data_bytes),
                          'checks': checker.count}, sort_keys=True))
        return

    data_text = pretty(data)
    contract = summarize(data, data_bytes, data_text.encode('utf-8'))
    write_output(args.output, data, contract, args.force)
    print(json.dumps({
        'output': str(args.output),
        'data_sha256': contract['data_sha256'],
        'checks': checker.count,
    }, sort_keys=True))


if __name__ == '__main__':
    main()
