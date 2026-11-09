# -*- coding: ascii -*-
"""Finite offline COC city STAGE provider over original client catalogs.

Selection, one-node projection and entry-owned target lock removal are explicit
local policy, not recovered official server algorithms. No event is completed
here and a real win never substitutes for a released areaFree callback.
"""
import copy
import hashlib
import json

try:
    _csp_text = (basestring,)
except NameError:
    _csp_text = (str,)

CITY_STAGE_PROVIDER_POLICY = 'offline-original-coc-city-stage-v1'


def original_city_stage_family(missions, coc_scenes):
    family = {}
    for scene in sorted(set(coc_scenes)):
        row = missions.get(scene, {})
        aid = row.get('ch')
        if (type(scene) is not int or type(aid) is not int or row.get('release') != 1 or
                row.get('system_type') != 2 or row.get('type') != 10 or
                not isinstance(row.get('target_hero'), (tuple, list)) or not row['target_hero'] or
                any(type(hero) is not int for hero in row['target_hero']) or aid in family):
            raise ValueError('Invalid or ambiguous original COC mission family')
        family[aid] = scene
    return family


def _csp_route(story):
    route = str(story.get('route', ''))
    subroute = story.get('subroute')
    return route if '-' in route or subroute is None else '%s-%s' % (route, subroute)


def _csp_requirements(row, route):
    values = row.get('area_require', {})
    return values.get(route, values.get(route.split('-')[0], values.get('-1')))


def _csp_day(state):
    return state.get('day', {}).get('stock_day', state.get('story', {}).get('date'))


def _csp_live(state, context):
    return context.get('week') == state['story'].get('week') and context.get('route') == _csp_route(state['story'])


def expire_city_stage_provider(state):
    """Restore only fields still equal to this provider's last projection."""
    story = state['story']
    context = story.get('city_stage_provider')
    if not context:
        return []
    if (state.get('battle', {}).get('active') or {}).get('city_stage_source'):
        raise ValueError('Actual provider battle must finish or be explicitly cancelled before route change')
    notices = []
    for key, saved in context.get('owned', {}).items():
        area = story.get('city_areas', {}).get(key)
        if area is None:
            continue
        last = saved.get('last', {})
        for field in ('status', 'lock', 'stage'):
            current = area.get('stage') if field == 'stage' else area['st'][0 if field == 'status' else 2]
            if field not in last or current != last[field]:
                continue
            if field == 'stage':
                if saved['before'].get('stage') is None:
                    area.pop('stage', None)
                else:
                    area['stage'] = copy.deepcopy(saved['before']['stage'])
            else:
                area['st'][0 if field == 'status' else 2] = saved['before'][field]
        # Native CityData.set_area_info merges keys rather than deleting them.
        # Retain a neutral restored placeholder so departure publishes FALL,
        # never leaves an old native FIGHT node after removing its server key.
        notices.append(('get_area_stages_reply', {'ai': int(key), 'st': copy.deepcopy(area.get('stage', {'cs':0,'sl':[]}))}))
    story.setdefault('city_stage_provider_history', []).append({
        'epoch': context['epoch'], 'route': context['route'], 'week': context['week'],
        'sources': copy.deepcopy(context['sources']), 'wins': copy.deepcopy(context['wins'])})
    story.pop('city_stage_provider', None)
    notices.append(_csp_city_notice(story))
    return notices


def _csp_own(context, area, created=False):
    return context['owned'].setdefault(str(area['id']), {'created':created,
        'before': {'status':area['st'][0], 'lock':area['st'][2], 'stage':copy.deepcopy(area.get('stage'))}, 'last':{}})


def _csp_city_notice(story):
    # Projection/recovery is not an ordinary area settlement. The original
    # consumer sends newly FIGHT nodes through the normal camera when sm=True;
    # projection may arrive before the city model/camera entries exist. Event UI
    # callbacks and ordinary battle settlement retain their own contracts.
    return ('get_all_area_info_reply', {'cd':copy.deepcopy(story.get('city_values', {})),
        'ais':{'area_%s' % key:copy.deepcopy(area) for key,area in story.get('city_areas', {}).items()}, 'sm':False})


def city_stage_provider_token(state):
    story = state.get('story', {})
    context = story.get('city_stage_provider') or {}
    authorization = {key:context.get(key) for key in ('sources','wins','superseded','lock_sources')}
    generation = hashlib.sha256(json.dumps(authorization, sort_keys=True, separators=(',', ':')).encode('ascii')).hexdigest()
    return (story.get('week'), _csp_route(story), _csp_day(state), context.get('epoch'), generation)


def refresh_city_stage_provider(state):
    story = state['story']
    context = story.get('city_stage_provider')
    if not context or not _csp_live(state, context):
        return []
    notices = []
    for key, scene in sorted(context['family'].items(), key=lambda pair:int(pair[0])):
        aid = int(key)
        if key in context.get('superseded', []):
            continue
        predecessor = context['predecessors'].get(key)
        pre = story.get('city_areas', {}).get(str(predecessor), {})
        if not predecessor or pre.get('st', [None])[0] != 0:
            continue
        requirements = context['requirements'].get(key)
        positive = (isinstance(requirements, (list, tuple)) and bool(requirements) and
            all(type(value) is int and value > 0 for value in requirements))
        if positive and not all(story.get('city_areas', {}).get(str(value), {}).get('st', [None])[0] == 0 for value in requirements):
            continue
        source = context['sources'].get(key)
        if source is None:
            # Only the entry's actually freed predecessor permits the initial
            # positive requirement projection. Sentinel0 never activates a node.
            if not positive or not set(requirements).issubset(set(context['entry_free'])):
                continue
            source = {'kind':'entry-positive-requirement', 'event':context['entry_event'],
                'receipt':context['entry_receipt'], 'day':context['entry_day']}
            context['sources'][key] = source
        area = story.setdefault('city_areas', {}).get(key)
        created = area is None
        if created:
            area = {'id':aid, 'st':[2,False,False], 'lv':1, 'bd':{}}
            story['city_areas'][key] = area
        owned = _csp_own(context, area, created)
        if source.get('kind') == 'entry-positive-requirement' and key not in context.setdefault('activated', []):
            area['st'][0] = 1
            owned['last']['status'] = 1
        if key not in context.setdefault('activated', []):
            context['activated'].append(key)
        if area['st'][0] not in (0,1):
            continue
        # Clear only the original entry lock, once per genuine target source.
        # A later explicit lock changes lock_sources and is never overridden.
        if area['st'][2] and context['lock_sources'].get(key) == context['entry_receipt'] and source['kind'] == 'areaFight' and positive:
            area['st'][2] = False
            # This target's committed activation supersedes the entry lock
            # for the current week; only cs/sl and synthetic status expire.
            context['lock_sources'][key] = 'provider:' + source['receipt']
        stage = {'cs':0 if scene in context['wins'] or area['st'][0] == 0 else scene, 'sl':[[scene]]}
        area['stage'] = stage
        owned['last']['stage'] = copy.deepcopy(stage)
        notices.append(('get_area_stages_reply', {'ai':aid, 'st':copy.deepcopy(stage)}))
    if notices:
        notices.append(_csp_city_notice(story))
    return notices


def record_city_stage_occurrence(state, event, row, tables, receipt):
    """Called only by the event-effect transaction after its callback gates."""
    story = state['story']
    context = story.get('city_stage_provider')
    target_route = row.get('enterStoryRoute')
    if target_route and row.get('release') and tables.get('coc_scenes') and tables.get('city_area_link_data'):
        family = original_city_stage_family(tables.get('mission', {}), tables['coc_scenes'])
        freed = list(row.get('areaFree', ()))
        requirements = {str(aid):_csp_requirements(tables.get('city_data', {}).get(aid, {}), target_route) for aid in family}
        predecessors = {str(info['link_area']):info['area'] for info in tables['city_area_link_data'].values()
            if info.get('link_area') in family and type(info.get('area')) is int}
        initial = [aid for aid in family
            if target_route in tables.get('city_data', {}).get(aid, {}).get('area_require', {}) and
            predecessors.get(str(aid)) in freed and predecessors[str(aid)] not in family and
            requirements[str(aid)] and
            all(type(value) is int and value > 0 and value in freed for value in requirements[str(aid)])]
        if initial:
            if context:
                expire_city_stage_provider(state)
            epoch = hashlib.sha256(('%s:%s:%s' % (story.get('week'),target_route,receipt)).encode('ascii')).hexdigest()
            predecessors = {str(info['link_area']):info['area'] for info in tables['city_area_link_data'].values()
                if info.get('link_area') in family and type(info.get('area')) is int}
            context = {'version':1, 'policy':CITY_STAGE_PROVIDER_POLICY, 'epoch':epoch,
                'week':story.get('week'), 'route':target_route, 'entry_event':event,
                'entry_receipt':receipt, 'entry_day':_csp_day(state), 'entry_free':freed,
                'family':{str(aid):scene for aid,scene in family.items()}, 'predecessors':predecessors,
                'requirements':requirements, 'sources':{}, 'owned':{}, 'wins':[], 'lock_sources':{}, 'superseded':[]}
            story['city_stage_provider'] = context
            # Offline overlap policy: the entry's explicit unlock wins over its
            # simultaneous lock, limited to the actually freed entry area.
            for aid in set(freed) & set(row.get('areaUnlock', ())) & set(row.get('areaLock', ())):
                area = story['city_areas'][str(aid)]
                owned = _csp_own(context, area)
                area['st'][2] = False
                # The source's explicit unlock commits under overlap policy.
    if not context or not row.get('release') or context['week'] != story.get('week'):
        return []
    if _csp_route(story) != context['route'] and target_route != context['route']:
        return []
    # Later explicit writes supersede owned fields even when values coincide.
    if receipt != context['entry_receipt']:
        for field, owned_field in (('areaFree','status'),('areaFight','status'),('areaFall','status'),
                ('areaStrike','status'),('areaLock','lock'),('areaUnlock','lock')):
            for aid in row.get(field, ()):
                context['owned'].get(str(aid), {}).get('last', {}).pop(owned_field, None)
    for aid in row.get('areaSpecialStage', {}):
        if str(aid) in context['family']:
            context['owned'].get(str(aid), {}).get('last', {}).pop('stage', None)
            if str(aid) not in context.setdefault('superseded', []):
                context['superseded'].append(str(aid))
    for aid in row.get('areaFight', ()):
        if str(aid) in context['family']:
            context['sources'][str(aid)] = {'kind':'areaFight', 'event':event, 'receipt':receipt, 'day':_csp_day(state)}
    for field in ('areaLock', 'areaUnlock'):
        for aid in row.get(field, ()):
            context['lock_sources'][str(aid)] = receipt
    return refresh_city_stage_provider(state)


def city_stage_provider_pending_source(state, area):
    context = state.get('story', {}).get('city_stage_provider')
    source = (context or {}).get('sources', {}).get(str(area))
    return bool(context and _csp_live(state, context) and source and
        str(area) in context['family'] and source.get('day', 7) <= _csp_day(state))


def city_stage_provider_admission(state, scene, area, mission, team):
    context = state.get('story', {}).get('city_stage_provider')
    if not context or str(area) not in context['family']:
        return None
    if str(area) in context.get('superseded', []):
        if scene == context['family'][str(area)]:
            raise ValueError('Original provider stage was superseded by a real area effect')
        return None
    if not _csp_live(state, context) or context['family'][str(area)] != scene:
        raise ValueError('Stale or mismatched original city provider stage')
    source = context['sources'].get(str(area))
    day = _csp_day(state)
    predecessor = context['predecessors'].get(str(area))
    target = state['story'].get('city_areas', {}).get(str(area), {})
    status = target.get('st', [])
    requirements = context['requirements'].get(str(area))
    if (not isinstance(requirements, (list,tuple)) or not requirements or
            any(type(value) is not int or value < 0 for value in requirements) or
            0 in requirements and list(requirements) != [0]):
        raise ValueError('Invalid original provider requirement schema')
    if (len(status) != 3 or status[0] != 1 or status[2] or
            isinstance(requirements, (list, tuple)) and all(type(value) is int and value > 0 for value in requirements) and
            not all(state['story'].get('city_areas', {}).get(str(value), {}).get('st', [None])[0] == 0 for value in requirements)):
        raise ValueError('Provider target lock/status or original positive requirements changed')
    if (not source or type(day) is not int or not 0 <= day < 7 or source['day'] > day or
            state['story'].get('city_areas', {}).get(str(predecessor), {}).get('st', [None])[0] != 0 or
            scene in context['wins'] or team != list(mission.get('target_hero', ()))):
        raise ValueError('Provider requires actual source, free predecessor and original fixed owned team')
    projected = state['story']['city_areas'][str(area)].get('stage')
    if projected != {'cs':scene,'sl':[[scene]]}:
        raise ValueError('Provider stage projection changed')
    return {'policy':CITY_STAGE_PROVIDER_POLICY, 'epoch':context['epoch'], 'route':context['route'],
        'week':context['week'], 'day':day, 'area':area, 'scene':scene, 'team':list(team), 'source':copy.deepcopy(source)}


def validate_city_stage_source(state, active):
    token = active.get('city_stage_source')
    if token is None:
        return
    request = active['request']
    expected = city_stage_provider_admission(state, request['s'], request['d']['a'],
        {'target_hero':request['h']}, request['h'])
    if token != expected:
        raise ValueError('Actual city provider source epoch/day changed')


def finish_city_stage_provider(state, scene):
    context = state['story']['city_stage_provider']
    if scene not in context['wins']:
        context['wins'].append(scene)
    story = state['story']
    for key in ('battle_wins','current_mission_wins'):
        wins = set(story.get(key, story.get('battle_wins', [])))
        wins.add(scene)
        story[key] = sorted(wins)
    return refresh_city_stage_provider(state)


def validate_city_stage_provider(state):
    context = state.get('story', {}).get('city_stage_provider')
    if context is None:
        return
    if (not isinstance(context, dict) or context.get('version') != 1 or
            context.get('policy') != CITY_STAGE_PROVIDER_POLICY or not isinstance(context.get('family'), dict) or
            not context.get('entry_receipt') or len(context.get('epoch','')) != 64 or
            type(context.get('week')) is not int or not isinstance(context.get('wins'), list) or
            any(type(scene) is not int for scene in context['wins']) or
            any(not isinstance(context.get(key), dict) for key in ('sources','owned','requirements','predecessors','lock_sources'))):
        raise ValueError('Invalid original city provider context')
    family = context['family']
    if (not family or any(not isinstance(key, _csp_text) or not key.isdigit() or type(scene) is not int for key,scene in family.items()) or
            len(set(family.values())) != len(family) or not set(context['wins']).issubset(set(family.values())) or
            not set(context['sources']).issubset(set(family)) or
            any(char not in '0123456789abcdef' for char in context['epoch']) or
            not isinstance(context.get('route'), _csp_text) or not context['route'] or
            type(context.get('entry_event')) is not int or type(context.get('entry_day')) is not int or
            not isinstance(context.get('entry_free'), list) or
            any(type(aid) is not int or aid <= 0 for aid in context['entry_free']) or
            not 0 <= context['entry_day'] < 7):
        raise ValueError('Invalid original city provider family or lineage')
    for field in ('activated','superseded'):
        values = context.get(field, [])
        if not isinstance(values, list) or any(not isinstance(key, _csp_text) for key in values) or not set(values).issubset(set(family)) or len(set(values)) != len(values):
            raise ValueError('Invalid original city provider node state')
    if set(context['requirements']) != set(family) or set(context['predecessors']) != set(family):
        raise ValueError('Incomplete original city provider catalog binding')
    for key,values in context['requirements'].items():
        if (not isinstance(values, (list,tuple)) or not values or
                any(type(value) is not int or value < 0 for value in values) or
                0 in values and list(values) != [0] or
                type(context['predecessors'][key]) is not int or context['predecessors'][key] <= 0):
            raise ValueError('Invalid original city provider area requirement')
    for key,source in context['sources'].items():
        if (not isinstance(source, dict) or source.get('kind') not in ('areaFight','entry-positive-requirement') or
                type(source.get('event')) is not int or not source.get('receipt') or
                type(source.get('day')) is not int or not context['entry_day'] <= source['day'] < 7):
            raise ValueError('Invalid original city provider occurrence')
    for key,owned in context['owned'].items():
        if (not isinstance(key, _csp_text) or not key.isdigit() or not isinstance(owned, dict) or type(owned.get('created')) is not bool or
                not isinstance(owned.get('before'), dict) or not isinstance(owned.get('last'), dict) or
                set(owned['last']) - set(('status','lock','stage')) or
                type(owned['before'].get('lock')) is not bool or type(owned['before'].get('status')) is not int):
            raise ValueError('Invalid original city provider projection ownership')
        for projection in (owned['before'], owned['last']):
            if ('status' in projection and (type(projection['status']) is not int or not 0 <= projection['status'] <= 6) or
                    'lock' in projection and type(projection['lock']) is not bool):
                raise ValueError('Invalid owned original city provider status')
            stage = projection.get('stage')
            if stage is not None and (not isinstance(stage, dict) or set(stage) != set(('cs','sl')) or
                    type(stage.get('cs')) is not int or stage['cs'] < 0 or not isinstance(stage.get('sl'), list) or
                    any(not isinstance(group, list) or any(type(scene) is not int or scene <= 0 for scene in group) for group in stage['sl'])):
                raise ValueError('Invalid owned original city provider stage')
    active = state.get('battle', {}).get('active')
    if active and active.get('city_stage_source'):
        validate_city_stage_source(state, active)
