# -*- coding: ascii -*-
"""Original chapter_mission_data selectors as finite offline STAGE sources.

FIGHT1 -> chapter bucket0, exact-route-only lookup, section ordering and cs/sl
projection are local policies. Original selector membership is table evidence;
no selector is treated as a mission ID, a victory or an areaFree callback.
"""
import copy
import hashlib
import json
import math as _ssc_math
try:
    _ssc_text = (basestring,)
except NameError:
    _ssc_text = (str,)

SPECIAL_CITY_STAGE_POLICY = 'offline-original-chapter-special-stage-v1'


try:
    _ssc_integer_types = (int, long)
    _ssc_string_types = (str, unicode)
    _ssc_byte_type = str
except NameError:
    _ssc_integer_types = (int,)
    _ssc_string_types = (str,)
    _ssc_byte_type = bytes


def _ssc_plain_literal(value, for_json=False, visiting=None):
    """Copy original read-only tagged mappings without native objects.

    Chapter lookup preserves tuple keys and integer section keys. Mission
    snapshots use JSON's stable list/text-key representation before hashing,
    so the same current catalog matches a saved/reloaded descriptor.
    """
    if value is None or type(value) is bool or type(value) in _ssc_integer_types:
        return value
    if type(value) is float:
        if _ssc_math.isnan(value) or _ssc_math.isinf(value):
            raise ValueError('Nonfinite original special literal')
        return value
    if type(value) is _ssc_byte_type:
        try:
            return value.decode('utf-8')
        except UnicodeError:
            raise ValueError('Original special bytes require valid UTF-8')
    if type(value) in _ssc_string_types:
        return value
    items = getattr(value, 'items', None)
    if not callable(items) and type(value) not in (tuple, list):
        raise ValueError('Unsupported original special nonliteral object')
    visiting = set() if visiting is None else visiting
    identity = id(value)
    if identity in visiting or len(visiting) >= 64:
        raise ValueError('Cyclic or too deep original special literal')
    visiting.add(identity)
    try:
        if callable(items):
            result = {}
            for entry in items():
                if not isinstance(entry, (tuple, list)) or len(entry) != 2:
                    raise ValueError('Invalid original special mapping entry')
                key, item = entry
                key = _ssc_plain_literal(key, False, visiting)
                if for_json:
                    if isinstance(key, _ssc_text):
                        pass
                    elif type(key) in _ssc_integer_types:
                        key = str(key)
                    else:
                        raise ValueError('Unsupported original special JSON mapping key')
                try:
                    duplicate = key in result
                except TypeError:
                    raise ValueError('Nonliteral original special mapping key')
                if duplicate:
                    raise ValueError('Duplicate or ambiguous original special mapping key')
                result[key] = _ssc_plain_literal(item, for_json, visiting)
            return result
        values = [_ssc_plain_literal(item, for_json, visiting) for item in value]
        return tuple(values) if type(value) is tuple and not for_json else values
    finally:
        visiting.remove(identity)




def _ssc_hash(value):
    return hashlib.sha256(json.dumps(_ssc_plain_literal(value, True), sort_keys=True, separators=(',', ':'), allow_nan=False).encode('ascii')).hexdigest()


def _ssc_route(state):
    story = state.get('story', {})
    route = str(story.get('route', ''))
    subroute = story.get('subroute')
    return route if '-' in route or subroute is None else '%s-%s' % (route, subroute)


def _ssc_day(state):
    return state.get('day', {}).get('stock_day', state.get('story', {}).get('date'))


def _ssc_contexts(state):
    document = state.get('story', {}).get('special_city_stages')
    return {} if document is None else document['contexts']


def _ssc_live(state, context):
    return context['week'] == state['story'].get('week') and context['route'] == _ssc_route(state)


def resolve_special_city_stage(area, status, route, selector, chapters, missions):
    """Resolve only an exact original key; never infer a branch/base fallback."""
    if (type(area) is not int or area <= 0 or type(status) is not int or status not in (1, 5) or
            not isinstance(route, _ssc_text) or not route or type(selector) is not int or selector <= 0):
        raise ValueError('Invalid typed original chapter special selector')
    bucket = 0 if status == 1 else 5
    wanted = (area, bucket, route, selector)
    candidates = []
    for original_key, original_row in chapters.items():
        key = _ssc_plain_literal(original_key)
        # Native cdata uses taggeddict rows, not dict subclasses. Copy only
        # literals locally; keep the catalog's typed tuple lookup key intact.
        row = _ssc_plain_literal(original_row)
        if not isinstance(row, dict):
            raise ValueError('Original chapter selector row requires a mapping')
        fields = tuple(row.get(name) for name in ('chapter', 'status', 'route', 'specialStage'))
        if key == wanted or fields == wanted:
            if (key != fields or not isinstance(key, tuple) or len(key) != 4 or
                    any(type(fields[index]) is not int or type(key[index]) is not int for index in (0,1,3)) or
                    not isinstance(fields[2], _ssc_text)):
                raise ValueError('Original chapter selector key/row mismatch')
            candidates.append(row)
    if len(candidates) != 1:
        raise ValueError('Missing or ambiguous exact original chapter selector')
    row = candidates[0]
    sections = row.get('section')
    if (not isinstance(sections, dict) or set(sections) != set(range(10)) or
            any(type(key) is not int for key in sections)):
        raise ValueError('Unsupported original chapter section schema')
    groups, members, snapshots = [], [], {}
    for section in sorted(sections):
        values = sections[section]
        if not isinstance(values, (list, tuple)) or any(type(scene) is not int or scene <= 0 for scene in values):
            raise ValueError('Invalid original chapter section members')
        if values:
            groups.append(list(values))
        for scene in values:
            mission = _ssc_plain_literal(missions.get(scene, {}), True)
            if not isinstance(mission, dict):
                raise ValueError('Original special mission row requires a mapping')
            if (scene in members or mission.get('id') != scene or mission.get('release') != 1 or
                    mission.get('ch') != area or mission.get('system_type') != 1):
                raise ValueError('Original special mission is missing, duplicate, unreleased or mismatched')
            members.append(scene)
            snapshots[str(scene)] = mission
    if not members:
        raise ValueError('Original special selector has no playable section')
    descriptor = {'key':list(wanted), 'groups':groups, 'members':members,
        'missions':snapshots, 'section_policy':'first-unfinished-in-original-section-order'}
    descriptor['catalog_token'] = _ssc_hash(descriptor)
    return descriptor


def _ssc_route_proof(state, events):
    route = _ssc_route(state)
    completed = set(state.get('completed_events', []))
    consumed = state.get('week_protocol', {}).get('consumed_handoffs', [])
    sources = []
    for event in completed:
        row = events.get(event, {})
        token = 'route:%s' % event
        if row.get('release') and row.get('enterStoryRoute') == route and token in consumed:
            sources.append({'event':event, 'token':token})
    if len(sources) != 1:
        raise ValueError('Special selector requires one actual committed original route source')
    return sources[0]


def _ssc_stage(context):
    members = [scene for scene in context['descriptor']['members'] if scene not in context['wins']]
    return {'cs':members[0] if members else 0, 'sl':copy.deepcopy(context['descriptor']['groups'])}


def _ssc_notice(state):
    story = state['story']
    # Projection may precede model readiness. Real event UI is a separate path.
    return ('get_all_area_info_reply', {'ais':{'area_%s' % key:copy.deepcopy(area)
        for key, area in story.get('city_areas', {}).items()},
        'cd':copy.deepcopy(story.get('city_values', {})), 'sm':False})


def apply_special_city_stage_effects(state, event, row, tables, receipt):
    """Event-effect component, after actual original callback/condition gates.

    Call for every row at the end of its other effects. It replaces the old
    selector-as-mission loop. Caller commits the whole event transaction.
    """
    selectors = _ssc_plain_literal(row.get('areaSpecialStage', {}))
    contexts = _ssc_contexts(state)
    if not row.get('release'):
        if selectors:
            raise ValueError('Special selector cannot originate from an unreleased event')
        return []
    if not selectors:
        if row.get('refreshMission') or row.get('abandonMission'):
            for context in contexts.values():
                context['revoked'] = True
        return []
    if not row.get('release') or not isinstance(selectors, dict) or type(event) is not int or not isinstance(receipt, _ssc_text) or not receipt:
        raise ValueError('Special selector requires an actual released original occurrence')
    if state.get('battle', {}).get('active'):
        raise ValueError('Special selector replacement waits for the actual active fight')
    week, day, route = state['story'].get('week'), _ssc_day(state), _ssc_route(state)
    if type(week) is not int or week < 0 or type(day) is not int or not 0 <= day < 7:
        raise ValueError('Special selector requires current original week/day')
    route_source = _ssc_route_proof(state, tables.get('event_content', {}))
    prepared = []
    coc = state['story'].get('city_stage_provider') or {}
    for area, selector in sorted(selectors.items()):
        current = state['story'].get('city_areas', {}).get(str(area))
        if not current or current.get('id') != area or len(current.get('st', [])) != 3:
            raise ValueError('Special selector requires actual native city area status')
        if coc.get('week') == week and coc.get('route') == route and str(area) in coc.get('family', {}):
            raise ValueError('Different typed providers cannot own the same city area')
        descriptor = resolve_special_city_stage(area, current['st'][0], route, selector,
            tables.get('chapter_mission_data', {}), tables.get('mission', {}))
        previous = contexts.get(str(area))
        if previous and previous['source']['receipt'] == receipt:
            if previous['source']['event'] != event or previous['descriptor'] != descriptor:
                raise ValueError('Original special occurrence identity was reused')
            continue
        before = copy.deepcopy(current.get('stage'))
        if previous and not previous['revoked'] and current.get('stage') == previous['last_stage']:
            before = copy.deepcopy(previous['before_stage'])
        source = {'event':event, 'receipt':receipt, 'week':week, 'day':day, 'route':route,
            'selector':selector, 'area':area, 'route_source':copy.deepcopy(route_source)}
        context = {'policy':SPECIAL_CITY_STAGE_POLICY, 'week':week, 'route':route,
            'source':source, 'descriptor':descriptor, 'epoch':_ssc_hash(source),
            'wins':[], 'revoked':False, 'before_stage':before, 'last_stage':None}
        context['last_stage'] = _ssc_stage(context)
        prepared.append((str(area), context))
    if not prepared:
        return []
    document = state['story'].setdefault('special_city_stages', {'version':1, 'contexts':{}})
    notices = []
    for key, context in prepared:
        document['contexts'][key] = context
        state['story']['city_areas'][key]['stage'] = copy.deepcopy(context['last_stage'])
        notices.append(('get_area_stages_reply', {'ai':int(key), 'st':copy.deepcopy(context['last_stage'])}))
    notices.append(_ssc_notice(state))
    return notices


def special_city_stage_area_active(state, area):
    context = _ssc_contexts(state).get(str(area))
    return bool(context and _ssc_live(state, context) and not context['revoked'])


def special_city_stage_token(state):
    return (_ssc_route(state), state.get('story', {}).get('week'), _ssc_day(state),
        _ssc_hash(_ssc_contexts(state)))


def special_city_stage_admission(state, scene, area, mission, team):
    context = _ssc_contexts(state).get(str(area))
    if context is None or context['revoked']:
        return None
    mission = _ssc_plain_literal(mission, True)
    if not isinstance(mission, dict):
        raise ValueError('Original special mission row requires a mapping')
    story = state['story']
    status = story.get('city_areas', {}).get(str(area), {}).get('st', [])
    if (not isinstance(team, list) or any(type(hero) is not int for hero in team) or
            len(set(team)) != len(team) or not mission.get('least_hero_num',1) <= len(team) <= mission.get('max_hero_num',3) or
            any(str(hero) not in (state.get('profile') or {}).get('heroes', {}) or
                str(hero) in story.get('banned_heroes', {}) for hero in team)):
        raise ValueError('Special STAGE requires an actually owned and available original party')
    source, descriptor = context['source'], context['descriptor']
    route_source = source['route_source']
    day = _ssc_day(state)
    if (not _ssc_live(state, context) or type(day) is not int or not source['day'] <= day < 7 or
            len(status) != 3 or status[0] not in (1,5) or status[2] or
            descriptor['key'][1] != (0 if status[0] == 1 else 5) or
            route_source['event'] not in state.get('completed_events', []) or
            route_source['token'] not in state.get('week_protocol', {}).get('consumed_handoffs', []) or
            source['event'] not in state.get('completed_events', []) or
            story.get('event_effect_receipts', {}).get(source['receipt']) != source['event'] or
            scene != _ssc_stage(context)['cs'] or
            story['city_areas'][str(area)].get('stage') != context['last_stage'] or
            context['last_stage'] != _ssc_stage(context) or
            _ssc_hash(mission) != _ssc_hash(descriptor['missions'].get(str(scene)))):
        raise ValueError('Special STAGE source, route, native projection or original mission changed')
    return {'policy':SPECIAL_CITY_STAGE_POLICY, 'epoch':context['epoch'],
        'catalog_token':descriptor['catalog_token'], 'source':copy.deepcopy(source),
        'week':story['week'], 'route':_ssc_route(state), 'day':day,
        'area':area, 'scene':scene, 'team':list(team)}


def validate_special_city_stage_source(state, active, missions=None):
    token = active.get('special_city_stage_source')
    if token is None:
        return
    if active.get('city_stage_source') is not None or active.get('condition_mission_root') is not None:
        raise ValueError('Conflicting typed original STAGE source variants')
    request = active['request']
    context = _ssc_contexts(state).get(str(request['d']['a']))
    if not context:
        raise ValueError('Missing original special stage admission context')
    if missions is not None and request['s'] not in missions:
        raise ValueError('Missing current original special mission catalog row')
    mission = missions[request['s']] if missions is not None else context['descriptor']['missions'].get(str(request['s']))
    expected = special_city_stage_admission(state, request['s'], request['d']['a'], mission, request['h'])
    if expected != token:
        raise ValueError('Actual special STAGE source epoch/day changed')


def finish_special_city_stage(state, scene):
    context = _ssc_contexts(state)[str(state['battle']['active']['request']['d']['a'])]
    if scene not in context['wins']:
        context['wins'].append(scene)
    for field in ('battle_wins','current_mission_wins'):
        values = set(state['story'].get(field, state['story'].get('battle_wins', [])))
        values.add(scene)
        state['story'][field] = sorted(values)
    context['last_stage'] = _ssc_stage(context)
    area = context['source']['area']
    state['story']['city_areas'][str(area)]['stage'] = copy.deepcopy(context['last_stage'])
    return [('get_area_stages_reply', {'ai':area,'st':copy.deepcopy(context['last_stage'])}), _ssc_notice(state)]


def refresh_special_city_stages(state):
    notices = []
    for key, context in _ssc_contexts(state).items():
        if not _ssc_live(state, context) or context['revoked']:
            continue
        current = state['story'].get('city_areas', {}).get(key, {})
        if current.get('stage') != context['last_stage']:
            context['revoked'] = True
            continue
        notices.append(('get_area_stages_reply', {'ai':int(key), 'st':copy.deepcopy(context['last_stage'])}))
    if notices:
        notices.append(_ssc_notice(state))
    return notices


def expire_special_city_stages(state, route=None):
    document = state.get('story', {}).get('special_city_stages')
    if document is None:
        return []
    keys = [key for key, context in document['contexts'].items() if route is None or context['route'] != route]
    active = state.get('battle', {}).get('active') or {}
    if active.get('special_city_stage_source') and str(active['request']['d']['a']) in keys:
        raise ValueError('Actual special STAGE must finish or cancel before route departure')
    notices = []
    for key in keys:
        context = document['contexts'].pop(key)
        current = state['story'].get('city_areas', {}).get(key)
        if current is not None and not context['revoked'] and current.get('stage') == context['last_stage']:
            if context['before_stage'] is None:
                current.pop('stage', None)
            else:
                current['stage'] = copy.deepcopy(context['before_stage'])
        state['story'].setdefault('special_city_stage_history', []).append(copy.deepcopy(context))
        if current is not None:
            notices.append(('get_area_stages_reply', {'ai':int(key), 'st':copy.deepcopy(current.get('stage', {'cs':0,'sl':[]}))}))
    if notices:
        notices.append(_ssc_notice(state))
    return notices


def _ssc_valid_stage(stage):
    return (stage is None or isinstance(stage, dict) and set(stage) == set(('cs','sl')) and
        type(stage.get('cs')) is int and stage['cs'] >= 0 and isinstance(stage.get('sl'), list) and
        all(isinstance(group, list) and all(type(scene) is int and scene > 0 for scene in group) for group in stage['sl']))


def validate_special_city_stages(state):
    document = state.get('story', {}).get('special_city_stages')
    if document is None:
        return
    if not isinstance(document, dict) or document.get('version') != 1 or not isinstance(document.get('contexts'), dict):
        raise ValueError('Invalid special city stage document')
    for key, context in document['contexts'].items():
        if (not isinstance(key, _ssc_text) or not key.isdigit() or not isinstance(context, dict) or
                context.get('policy') != SPECIAL_CITY_STAGE_POLICY or type(context.get('week')) is not int or
                not isinstance(context.get('route'), _ssc_text) or not context['route'] or
                not isinstance(context.get('source'), dict) or not isinstance(context.get('descriptor'), dict) or
                not isinstance(context.get('wins'), list) or any(type(scene) is not int for scene in context['wins']) or type(context.get('revoked')) is not bool or
                not _ssc_valid_stage(context.get('before_stage')) or not _ssc_valid_stage(context.get('last_stage'))):
            raise ValueError('Invalid special city stage context')
        source, descriptor = context['source'], context['descriptor']
        if (type(source.get('area')) is not int or source.get('area') != int(key) or source.get('route') != context['route'] or type(source.get('week')) is not int or source.get('week') != context['week'] or
                type(source.get('event')) is not int or not isinstance(source.get('receipt'), _ssc_text) or not source['receipt'] or
                type(source.get('day')) is not int or not 0 <= source['day'] < 7 or
                type(source.get('selector')) is not int or source['selector'] <= 0 or not isinstance(source.get('route_source'), dict) or
                type(source['route_source'].get('event')) is not int or source['route_source'].get('token') != 'route:%s' % source['route_source']['event'] or
                context.get('epoch') != _ssc_hash(source)):
            raise ValueError('Invalid special city stage occurrence')
        rowkey = descriptor.get('key')
        if not isinstance(rowkey, list) or len(rowkey) != 4 or type(rowkey[0]) is not int or rowkey[0] != int(key) or type(rowkey[1]) is not int or rowkey[1] not in (0,5) or rowkey[2:] != [context['route'],source['selector']]:
            raise ValueError('Invalid special city stage table key')
        snapshots = descriptor.get('missions')
        groups = descriptor.get('groups')
        members = descriptor.get('members')
        if (not isinstance(snapshots, dict) or not isinstance(groups, list) or not groups or
                any(not isinstance(group,list) or not group or any(type(scene) is not int or scene <= 0 for scene in group) for group in groups) or
                members != [scene for group in groups for scene in group] or len(set(members)) != len(members) or
                set(snapshots) != set(str(scene) for scene in members) or not set(context['wins']).issubset(set(members))):
            raise ValueError('Invalid special city stage section binding')
        for scene in members:
            mission = snapshots[str(scene)]
            if (not isinstance(mission, dict) or mission.get('id') != scene or mission.get('ch') != int(key) or
                    mission.get('release') != 1 or mission.get('system_type') != 1):
                raise ValueError('Invalid special city original mission snapshot')
        unsigned = dict(descriptor)
        unsigned.pop('catalog_token', None)
        if descriptor.get('catalog_token') != _ssc_hash(unsigned) or context['last_stage'] != _ssc_stage(context):
            raise ValueError('Invalid special city stage catalog/projection fingerprint')
    active = state.get('battle', {}).get('active')
    if active:
        validate_special_city_stage_source(state, active)
