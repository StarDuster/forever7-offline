# -*- coding: ascii -*-
"""Ordinary original STAGE battles and city progression as pure transactions.

Offline policy: original mission costs are reserved at admission and charged on
actual accepted wins only (Project7 reference). Real losses pay no reward/cost.
No timer, area entry, dialogue callback or host test manufactures a client win.
"""
try:
    from offline_special_city_stage import (special_city_stage_area_active,
        special_city_stage_admission, validate_special_city_stage_source,
        finish_special_city_stage)
except ImportError:
    pass

try:
    from offline_city_stage_provider import (original_city_stage_family,
        record_city_stage_occurrence, refresh_city_stage_provider,
        city_stage_provider_admission, validate_city_stage_source,
        finish_city_stage_provider, validate_city_stage_provider,
        expire_city_stage_provider)
except ImportError:
    pass

try:
    from offline_flashback import (flashback_context, flashback_token, flashback_data,
        flashback_notice, flashback_require_action, flashback_spend_action,
        flashback_accept_entry, flashback_route_handoff, prepare_flashback_operation,
        validate_flashback_state)
except ImportError:
    pass

try:
    from offline_chapter_campaign import (normal_chapter_admission, validate_normal_stage_source,
        finish_normal_chapter, stage_projection_owner)
except ImportError:
    pass

import copy
import hashlib
import json

STAGE_POLICY = 'original-basic-city-stage-cycle-v1'


def _stage_int(value):
    return type(value) is int


def validate_stage_battle_state(battle):
    if not isinstance(battle, dict) or battle.get('version') != 1:
        raise ValueError('Unsupported battle transaction state')
    if not isinstance(battle.get('receipts'), list) or len(battle['receipts']) > 32:
        raise ValueError('Invalid stage receipts')
    seen = set()
    for receipt in battle['receipts']:
        fingerprint = receipt.get('fingerprint', '')
        if (not receipt.get('fight_id') or receipt['fight_id'] in seen or
                not isinstance(receipt.get('reply'), dict) or len(fingerprint) != 64 or
                any(char not in '0123456789abcdef' for char in fingerprint)):
            raise ValueError('Invalid stage receipt')
        seen.add(receipt['fight_id'])
    active = battle.get('active')
    if active is None:
        return
    request = active.get('request', {})
    team = request.get('h')
    if (not active.get('fight_id') or request.get('t') != 1 or
            not _stage_int(request.get('s')) or not isinstance(request.get('d'), dict) or
            not _stage_int(request['d'].get('a')) or not isinstance(team, list) or not team or
            any(not _stage_int(hero) for hero in team) or len(set(team)) != len(team) or
            set(active.get('heroes', {})) != set(str(hero) for hero in team) or
            set(active.get('confirmed_heroes', [])) != set(team)):
        raise ValueError('Invalid active original STAGE battle')
    if active['fight_id'] in seen:
        raise ValueError('Active fight already has a settlement receipt')
    if 'stage_policy' in active:
        costs = active.get('costs', {})
        if (active['stage_policy'] != STAGE_POLICY or
                any(not _stage_int(costs.get(key)) or costs[key] < 0
                    for key in ('actions', 'fatigue')) or
                any(not _stage_int(active.get(key)) or active[key] < 1
                    for key in ('reward_level', 'hero_level', 'monster_level'))):
            raise ValueError('Invalid pinned ordinary-stage policy or cost')


def basic_city_stage_chain(area_id, state, missions):
    """Original normal-city family; every derived ID is verified against cdata.

    Project7 mapStages normal-city family supplies six stages per area, not a
    grant of six wins or six unlocked admissions. sl is the stock display list;
    cs and accepted battle_wins enforce the first unfinished stage.
    """
    if not _stage_int(area_id) or not 1 <= area_id <= 8:
        raise ValueError('Special or virtual city battle requires its own policy')
    if area_id == 1:
        stages = [101]
    else:
        stages = [(area_id - 1) * 1000 + 100 + index for index in range(1, 7)]
        if area_id == 2 and 20007 in state.get('completed_events', []):
            stages[-1] = 1107
    for scene in stages:
        row = missions.get(scene)
        if not row or row.get('release') != 1 or row.get('ch') != area_id or row.get('system_type') != 1:
            raise ValueError('Original normal-city stage catalog is incomplete')
    return stages


def original_stage_cost(mission, force):
    if not _stage_int(force) or force < 0:
        raise ValueError('Missing current original city force')
    action = mission.get('va', 0)
    fatigue = mission.get('fatigue', 0)
    recommendation = mission.get('force_recommend', 0)
    if not _stage_int(recommendation) or recommendation < 0:
        raise ValueError('Invalid original recommended force')
    if force < recommendation:
        fatigue = mission.get('overFatigue', 0)
    if any(not _stage_int(value) or value < 0 for value in (action, fatigue)):
        raise ValueError('Invalid original mission cost')
    return {'actions': action, 'fatigue': fatigue}


def original_stage_levels(mission, week, player_level):
    """Use original mission adjustments; second-week table applies after week0.

    The later-week choice is an explicit offline scaling policy; no invented
    monster multiplier is applied beyond the original configured level.
    """
    hero_level = mission.get('adjust_hero_lv', player_level)
    monster_level = mission.get('adjust_monster_lv',
        mission.get('monsterLvFirstWeek' if week == 0 else 'monsterLvSecondWeek', player_level))
    if any(not _stage_int(value) or value < 1 for value in (hero_level, monster_level)):
        raise ValueError('Invalid original stage combat levels')
    return hero_level, monster_level


def prepare_stage_admission(state, arguments, missions, make_id, stock_day=None):
    candidate = copy.deepcopy(state)
    battle = candidate.setdefault('battle', {'version': 1, 'active': None, 'receipts': []})
    validate_stage_battle_state(battle)
    request = {key: copy.deepcopy(arguments.get(key)) for key in ('t', 's', 'h', 'd')}
    scene, team, detail = request['s'], request['h'], request['d']
    if (request['t'] != 1 or not _stage_int(scene) or scene == 101 or
            not isinstance(detail, dict) or set(detail) != set(('a',)) or
            not _stage_int(detail.get('a')) or not isinstance(team, list) or
            any(not _stage_int(hero) for hero in team) or len(set(team)) != len(team)):
        raise ValueError('Expected a normal STAGE request; scene101 retains its original tutorial handler')
    active = battle['active']
    if active is not None:
        validate_city_stage_source(candidate, active)
        validate_special_city_stage_source(candidate, active, missions)
        validate_normal_stage_source(candidate, active, missions)
        if active['request'] != request:
            raise ValueError('Another actual battle is active')
        return candidate, False
    story = candidate.get('story', {})
    day = candidate.get('day', {}).get('stock_day', stock_day)
    # Original const.MAX_DAYNUM=8; WeekNumData.isFinalDay guards d >= 7.
    if not _stage_int(day) or not 0 <= day < 7:
        raise ValueError('Original final-day guard or missing stock day')
    if flashback_context(candidate) is not None and ((candidate.get('city_actions') or {}).get('patrol') or
            story.get('patrol_pending') or story.get('patrol_reward_pending')):
        raise ValueError('Actual patrol must finish before flashback STAGE')
    if story.get('emergency'):
        raise ValueError('Emergency story must complete before ordinary city battles')
    area_id = detail['a']
    area = story.get('city_areas', {}).get(str(area_id))
    condition_root = story.get('condition_mission_roots', {}).get(str(area_id))
    provider_context = story.get('city_stage_provider')
    if provider_context and str(area_id) in provider_context['family']:
        condition_root = None
    owner = stage_projection_owner(candidate, area_id)
    if owner == 'normal':
        condition_root = None
    special_active = special_city_stage_area_active(candidate, area_id)
    if special_active:
        condition_root = None
    statuses = (1, 5) if condition_root is not None or special_active or owner == 'normal' else (1,)
    if (not area or area.get('id') != area_id or not isinstance(area.get('st'), (list, tuple)) or
            len(area['st']) < 3 or area['st'][0] not in statuses or area['st'][2]):
        raise ValueError('Area is not an unlocked original FIGHT/STRIKE area')
    mission = missions.get(scene)
    if not mission or mission.get('ch') != area_id or mission.get('release') != 1:
        raise ValueError('Scene does not belong to the admitted released area')
    stage = area.get('stage', {})
    provider_source = city_stage_provider_admission(candidate, scene, area_id, mission, team)
    special_source = special_city_stage_admission(candidate, scene, area_id, mission, team)
    normal_source = normal_chapter_admission(candidate, scene, area_id, mission, team)
    if provider_source is not None and special_source is not None:
        raise ValueError('Conflicting typed city STAGE providers')
    if special_source is not None or provider_source is not None or normal_source is not None:
        chain = [scene]
    elif condition_root is not None:
        expected_stage, chain = condition_mission_stage(story, missions, condition_root, set(candidate.get('completed_events', [])))
        if stage != expected_stage or expected_stage['cs'] != scene:
            raise ValueError('Condition city stage is not the actually eligible original mission')
        if any(str(hero) in story.get('banned_heroes', {}) for hero in team):
            raise ValueError('Condition city team contains a currently banned hero')
    else:
        chain = basic_city_stage_chain(area_id, candidate, missions)
        if scene not in chain:
            raise ValueError('Special route/scene requires its own progression policy')
        if (stage.get('cs') != scene or not any(scene in group for group in stage.get('sl', [])) or
                not set(chain[:chain.index(scene)]).issubset(set(story.get('battle_wins', [])))):
            raise ValueError('Stage or its actual victory prerequisites are not unlocked')
    if not mission.get('least_hero_num', 1) <= len(team) <= mission.get('max_hero_num', 3):
        raise ValueError('Invalid original stage team size')
    profile = candidate.get('profile') or {}
    roster = profile.get('heroes', {})
    if any(str(hero) not in roster for hero in team):
        raise ValueError('Stage team must contain owned heroes')
    city = story.get('city_values', {})
    costs = original_stage_cost(mission, city.get('fv'))
    if (provider_source is not None or special_source is not None or normal_source is not None) and flashback_context(candidate) is not None:
        raise ValueError('City provider cannot use flashback action budget')
    flashback = flashback_require_action(candidate)
    if not _stage_int(city.get('av')) or (not flashback and city['av'] < costs['actions']):
        raise ValueError('Insufficient original action value')
    if any(not _stage_int(roster[str(hero)].get('cf')) or
           roster[str(hero)]['cf'] < costs['fatigue'] for hero in team):
        raise ValueError('Insufficient original hero fatigue')
    economy = profile.get('economy') or {}
    if not _stage_int(economy.get('level')):
        raise ValueError('Missing persistent battle reward level')
    levels = original_stage_levels(mission, story.get('week', 0), economy['level'])
    fight_id = str(make_id())
    if not fight_id or any(r['fight_id'] == fight_id for r in battle['receipts']):
        raise ValueError('Battle identity must be fresh')
    battle['active'] = {'fight_id': fight_id, 'request': request,
                        'heroes': {str(hero): copy.deepcopy(roster[str(hero)]) for hero in team},
                        'confirmed_heroes': list(team), 'reward_level': economy['level'],
                        'costs': costs, 'hero_level': levels[0], 'monster_level': levels[1],
                        'stage_policy': STAGE_POLICY}
    if special_source is not None:
        battle['active']['special_city_stage_source'] = special_source
    if provider_source is not None:
        battle['active']['city_stage_source'] = provider_source
    if normal_source is not None:
        battle['active']['normal_chapter_source'] = normal_source
    if flashback:
        battle['active']['flashback_token'] = flashback_token(candidate)
    if condition_root is not None:
        battle['active']['condition_mission_root'] = condition_root
    validate_stage_battle_state(battle)
    return candidate, True


def stage_finish_fingerprint(arguments):
    payload = {key: arguments.get(key) for key in ('t', 's', 'h', 'x', 'w', 'e')}
    if type(payload['w']) in (int, bool) and payload['w'] in (0, 1):
        payload['w'] = int(payload['w'])
    return hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(',', ':')).encode('utf-8')).hexdigest()


def _stage_city_notice(story):
    # set_city_data does not apply areas. Use the original area synchronizer.
    return ('get_all_area_info_reply', {'cd': copy.deepcopy(story['city_values']),
        'ais': {'area_%s' % key: copy.deepcopy(value) for key, value in story['city_areas'].items()},
        'sm': True})



def _unlock_original_basic_city_areas(state, missions, city_catalog):
    """Only original route prerequisites and locks unlock normal FIGHT areas."""
    story = state['story']
    pending = []
    route = str(story.get('route', '-1'))
    subroute = story.get('subroute')
    route_key = '%s-%s' % (route, subroute) if subroute is not None else route
    for next_area, row in sorted(city_catalog.items()):
        if not _stage_int(next_area) or not 1 <= next_area <= 8 or next_area == 1:
            continue
        existing = story['city_areas'].get(str(next_area))
        if existing and existing.get('st', [None])[0] != 2:
            continue
        requirements = row.get('area_require', {})
        prerequisites = requirements.get(route_key, requirements.get(route, requirements.get('-1')))
        if not isinstance(prerequisites, (list, tuple)) or not prerequisites:
            pending.append({'area': next_area, 'reason': 'unknown_original_area_requirements'})
            continue
        if any(not _stage_int(required) or not 1 <= required <= 8 for required in prerequisites):
            pending.append({'area': next_area, 'reason': 'special_route_area_requirements'})
            continue
        if not all(story['city_areas'].get(str(required), {}).get('st', [None])[0] == 0
                   for required in prerequisites):
            continue
        new_chain = basic_city_stage_chain(next_area, state, missions)
        if existing and existing.get('st', [None])[2]:
            continue
        if existing is None:
            existing = {'id': next_area, 'st': [1, False, False], 'lv': 1, 'bd': {}}
            story['city_areas'][str(next_area)] = existing
        else:
            existing['st'] = list(existing['st'])
            existing['st'][0] = 1
        existing['stage'] = {'cs': new_chain[0], 'sl': [[stage] for stage in new_chain]}
    return pending


def _prepare_stage_clearance(state, scene, missions, city_catalog):
    """Advance exactly the won area; unlock only satisfied original area edges.

    Caller must possess an accepted real result for scene. This private planning
    helper is called only inside finish below; it never records fictitious wins.
    Default-route area requirements come from city_data.area_require[-1].
    Route overrides with sentinel0/virtual dependencies remain explicitly pending.
    """
    candidate = copy.deepcopy(state)
    story = candidate['story']
    mission = missions[scene]
    area_id = mission['ch']
    area = story['city_areas'][str(area_id)]
    area['st'] = list(area['st'])
    current = current_mission_wins(story)
    current.add(scene)
    if 'current_mission_wins' in story:
        story['current_mission_wins'] = sorted(current)
    condition_root = (candidate.get('battle', {}).get('active') or {}).get('condition_mission_root')
    if condition_root is not None:
        if story.get('condition_mission_roots', {}).get(str(area_id)) != condition_root:
            raise ValueError('Condition mission root changed during actual fight')
        history = set(story.get('battle_wins', []))
        history.add(scene)
        story['battle_wins'] = sorted(history)
        story['current_mission_wins'] = sorted(current)
        stage, family = condition_mission_stage(story, missions, condition_root, set(candidate.get('completed_events', [])))
        area['stage'] = stage
        ordinary_pending = []
        if set(family).issubset(current):
            area['st'][0] = 0
            if 1 <= area_id <= 8:
                ordinary = basic_city_stage_chain(area_id, candidate, missions)
                if scene == ordinary[-1] and set(ordinary).issubset(current):
                    ordinary_pending = _unlock_original_basic_city_areas(candidate, missions, city_catalog)
        record_original_mission_edges(story, missions, scene)
        refresh_condition_city_missions(candidate, missions, city_catalog=city_catalog)
        return candidate, ordinary_pending + copy.deepcopy(story.get('pending_mission_edges', []))
    chain = basic_city_stage_chain(area_id, candidate, missions)
    position = chain.index(scene)
    wins = set(story.get('battle_wins', []))
    wins.add(scene)
    story['battle_wins'] = sorted(wins)
    pending = []
    if position + 1 < len(chain):
        successor = chain[position + 1]
        if successor not in mission.get('nextstagenums', ()):
            raise ValueError('Original next-stage link does not match the selected city chain')
        area['stage'] = {'cs': successor, 'sl': [[stage] for stage in chain]}
    else:
        area['st'][0] = 0
        area['stage'] = {'cs': 0, 'sl': [[stage] for stage in chain]}
        pending.extend(_unlock_original_basic_city_areas(candidate, missions, city_catalog))
    return candidate, pending


def prepare_stage_finish(state, arguments, missions, city_catalog, settle, source_fight_id):
    """Whole-state atomic plan. settle(active, actual)->reply, reward effects.

    Effects require a fully prepared profile plus notices/granted; caller's
    existing table reward engine may supply it. Real source fight ID is mandatory
    because the original finish RPC has no identity field. Publish after save.
    """
    candidate = copy.deepcopy(state)
    battle = candidate.get('battle')
    validate_stage_battle_state(battle)
    fingerprint = stage_finish_fingerprint(arguments)
    active = battle['active']
    if active is None:
        if battle['receipts']:
            receipt = battle['receipts'][-1]
            if source_fight_id == receipt['fight_id'] and fingerprint == receipt['fingerprint']:
                return candidate, copy.deepcopy(receipt['reply']), None, False
        raise ValueError('No matching actual stage admission')
    if active['fight_id'] != source_fight_id or active.get('stage_policy') != STAGE_POLICY:
        raise ValueError('Finish source does not match active stage policy/admission')
    validate_city_stage_source(candidate, active)
    validate_special_city_stage_source(candidate, active, missions)
    validate_normal_stage_source(candidate, active, missions)
    request = active['request']
    if (any(arguments.get(key) != request[key] for key in ('t', 's', 'h')) or
            not isinstance(arguments.get('x'), list) or len(set(arguments['x'])) != len(arguments['x']) or
            any(not _stage_int(hero) or hero not in active['confirmed_heroes'] for hero in arguments['x']) or
            type(arguments.get('w')) not in (int, bool) or arguments['w'] not in (0, 1)):
        raise ValueError('Invalid actual stage result')
    actual = copy.deepcopy(arguments)
    actual['w'] = int(actual['w'])
    reply, effects = settle(copy.deepcopy(active), actual)
    if (any(reply.get(key) != actual[key] for key in ('t', 's', 'h', 'x', 'w')) or
            not isinstance(reply.get('r'), dict) or not isinstance(effects.get('profile'), dict)):
        raise ValueError('Reward must preserve actual result and full profile')
    notices = copy.deepcopy(effects.get('notices', []))
    pending = []
    if actual['w'] == 0:
        if reply['r'] or effects['profile'] != state['profile'] or notices or effects.get('granted'):
            raise ValueError('Actual loss cannot grant economy, rewards or progression')
    else:
        candidate['profile'] = copy.deepcopy(effects['profile'])
        costs = active['costs']
        story = candidate['story']
        city = story['city_values']
        if active.get('flashback_token') is not None:
            notices.extend(flashback_spend_action(candidate, active['flashback_token']))
        else:
            if flashback_context(candidate) is not None:
                raise ValueError('Stage admitted outside current flashback context')
            if city['av'] < costs['actions']:
                raise ValueError('Reserved stage actions changed before settlement')
            city['av'] -= costs['actions']
        for hero in request['h']:
            record = candidate['profile']['heroes'][str(hero)]
            if record['cf'] < costs['fatigue']:
                raise ValueError('Reserved hero fatigue changed before settlement')
            record['cf'] -= costs['fatigue']
            notices.append(('updateCurFatigueValue', {'h': hero, 'v': record['cf']}))
        if active.get('normal_chapter_source') is not None:
            notices.extend(finish_normal_chapter(candidate, request['s']))
        elif active.get('special_city_stage_source') is not None:
            notices.extend(finish_special_city_stage(candidate, request['s']))
        elif active.get('city_stage_source') is not None:
            notices.extend(finish_city_stage_provider(candidate, request['s']))
        else:
            candidate, pending = _prepare_stage_clearance(candidate, request['s'], missions, city_catalog)
        notices.append(_stage_city_notice(candidate['story']))
        reply['r']['stage'] = request['s']
    battle = candidate['battle']
    battle['receipts'].append({'fight_id': active['fight_id'], 'fingerprint': fingerprint,
                               'reply': copy.deepcopy(reply)})
    battle['receipts'] = battle['receipts'][-32:]
    battle['active'] = None
    validate_stage_battle_state(battle)
    effects = dict(copy.deepcopy(effects), profile=copy.deepcopy(candidate['profile']),
                   notices=notices, pending_progression=pending)
    return candidate, reply, effects, True


def current_mission_wins(story):
    """Current retry progress, separate from retained historical battle proof."""
    wins = story.get('current_mission_wins', story.get('battle_wins', []))
    if not isinstance(wins, list) or any(not _stage_int(scene) for scene in wins):
        raise ValueError('Invalid current original mission progress')
    return set(wins)


def original_condition_mission_family(missions, root, completed_events, source_scene=None, wins=None):
    row = missions.get(root, {})
    event, aid = row.get('cond_event'), row.get('ch')
    event_proof = _stage_int(event) and event in completed_events
    edge_proof = (source_scene in (wins or set()) and source_scene in missions and
        (root in missions[source_scene].get('nextstagenums', ()) or source_scene in row.get('cond', ())))
    if (not (event_proof or edge_proof) or not _stage_int(aid) or
            row.get('release') != 1 or row.get('system_type') not in (1, 2)):
        raise ValueError('Condition city mission requires actual original event/edge proof')
    family = set((root,))
    for unused in range(len(missions)):
        additions = set()
        for scene, definition in missions.items():
            prerequisites = definition.get('cond', ())
            if (scene not in family and definition.get('release') == 1 and
                    definition.get('ch') == aid and definition.get('system_type') in (1, 2) and
                    isinstance(prerequisites, (tuple, list)) and any(parent in family for parent in prerequisites) and
                    (not definition.get('cond_event') or definition['cond_event'] in completed_events)):
                additions.add(scene)
        if not additions:
            break
        family.update(additions)
    return sorted(family)


def condition_mission_stage(story, missions, root, completed_events):
    wins = current_mission_wins(story)
    source = story.get('condition_mission_sources', {}).get(str(missions[root]['ch']))
    family = original_condition_mission_family(missions, root, completed_events, source, wins)
    ready = []
    for scene in family:
        prerequisites = missions[scene].get('cond', ())
        if not isinstance(prerequisites, (list, tuple)) or any(not _stage_int(parent) for parent in prerequisites):
            raise ValueError('Unsupported original condition mission prerequisites')
        if scene not in wins and original_mission_prerequisites_met(missions, scene, wins):
            ready.append(scene)
    # Explicit offline choice policy: first original ID among equally legal
    # unfinished nodes. sl displays the original family; cs alone admits combat.
    return {'cs': min(ready) if ready else 0, 'sl': [[scene] for scene in family]}, family


def refresh_condition_city_missions(state, missions, completing_event=None, city_catalog=None):
    """Rebuild event-activated families using real conditions/current wins only.

    This is an explicit offline policy over original catalogs, not reconstruction
    of the unavailable official server. It never manufactures any battle result.
    """
    story = state['story']
    completed = set(state.get('completed_events', []))
    if completing_event is not None:
        completed.add(completing_event)
    roots_by_area = {}
    wins = current_mission_wins(story)
    for scene, row in missions.items():
        event, aid = row.get('cond_event'), row.get('ch')
        if (event in completed and _stage_int(aid) and row.get('release') == 1 and
                row.get('system_type') in (1, 2) and
                (scene in wins or original_mission_prerequisites_met(missions, scene, wins))):
            roots_by_area.setdefault(aid, []).append(scene)
    notices = []
    selected_roots = story.setdefault('condition_mission_roots', {})
    for key, area in sorted(story.get('city_areas', {}).items()):
        aid = int(key)
        if area.get('st', [None])[0] not in (1, 5):
            continue
        if stage_projection_owner(state, aid) in ('positive-special', 'coc'):
            continue
        active = state.get('battle', {}).get('active') or {}
        if active.get('normal_chapter_source') and active['request']['d']['a'] == aid:
            continue
        roots = roots_by_area.get(aid, [])
        preferred = [scene for scene in roots if missions[scene]['cond_event'] == completing_event]
        previous = selected_roots.get(str(aid))
        if preferred:
            root = min(preferred)
        elif previous in roots:
            root = previous
        elif previous is not None and story.get('condition_mission_sources', {}).get(str(aid)) in wins:
            root = previous
        elif roots:
            history = {event:index for index,event in enumerate(story.get('event_history', []))}
            root = min(roots, key=lambda scene:(-history.get(missions[scene]['cond_event'], -1), scene))
        else:
            continue
        normal = story.get('normal_chapters', {}).get('contexts', {}).get(str(aid))
        if (normal and not normal.get('revoked') and normal.get('week') == story.get('week') and
                root in normal.get('descriptor', {}).get('members', [])):
            # A chapter-internal event alternative remains at its original
            # section position; it is not a new one-node conditional family.
            if previous in normal['descriptor']['members']:
                selected_roots.pop(str(aid), None)
            continue
        stage, family = condition_mission_stage(story, missions, root, completed)
        selected_roots[str(aid)] = root
        if root in roots:
            story.setdefault('condition_mission_sources', {}).pop(str(aid), None)
        area['stage'] = stage
        notices.append(('get_area_stages_reply', {'ai': aid, 'st': copy.deepcopy(stage)}))
    if city_catalog is not None:
        notices.extend(reconcile_original_mission_edges(state, missions, city_catalog))
    notices.append(('refreshClientMission', {}))
    return notices


def original_mission_prerequisites_met(missions, scene, wins):
    prerequisites = missions[scene].get('cond', ())
    if not isinstance(prerequisites, (list, tuple)) or any(not _stage_int(parent) for parent in prerequisites):
        raise ValueError('Unsupported original mission prerequisite schema')
    if len(prerequisites) > 1 and all(scene in missions.get(parent, {}).get('nextstagenums', ()) for parent in prerequisites):
        # Original four merge nodes have alternative predecessor entrances,
        # each explicitly pointing here. One accepted incoming edge is enough.
        return any(parent in wins for parent in prerequisites)
    return set(prerequisites).issubset(wins)


def record_original_mission_edges(story, missions, source):
    if source not in current_mission_wins(story):
        raise ValueError('Outgoing mission edges require actual current source win')
    targets = set(missions[source].get('nextstagenums', ()))
    targets.update(scene for scene, row in missions.items() if source in row.get('cond', ()))
    edges = story.setdefault('condition_mission_edges', {})
    for target in sorted(targets):
        if target == source:
            continue
        sources = edges.setdefault(str(target), [])
        if source not in sources:
            sources.append(source)


def _mission_edge_route_guard(story, aid, city_catalog):
    row = city_catalog.get(aid)
    if row is None:
        return 'missing_original_target_area'
    route = str(story.get('route', '-1'))
    subroute = story.get('subroute')
    exact = '%s-%s' % (route, subroute) if subroute is not None else route
    requirements = row.get('area_require', {})
    values = requirements.get(exact, requirements.get(route, requirements.get('-1')))
    if not isinstance(values, (tuple, list)) or not values:
        return 'unknown_original_route_area_requirements'
    if any(not _stage_int(required) or required == 0 for required in values):
        return 'unproven_original_route_sentinel'
    if not all(story.get('city_areas', {}).get(str(required), {}).get('st', [None])[0] == 0 for required in values):
        return 'original_route_area_prerequisites_not_free'
    return None


def reconcile_original_mission_edges(state, missions, city_catalog):
    story = state['story']
    wins = current_mission_wins(story)
    completed = set(state.get('completed_events', []))
    pending, candidates, notices = [], {}, []
    for key, sources in sorted(story.get('condition_mission_edges', {}).items(), key=lambda item:int(item[0])):
        target = int(key)
        row = missions.get(target, {})
        aid = row.get('ch')
        proven = [source for source in sources if source in wins and source in missions and
            (target in missions[source].get('nextstagenums', ()) or source in row.get('cond', ()))]
        if target in wins or not proven:
            continue
        area = story.get('city_areas', {}).get(str(aid))
        reason = None
        if row.get('release') != 1 or row.get('system_type') not in (1, 2) or not _stage_int(aid):
            reason = 'unsupported_original_target_mission'
        elif not original_mission_prerequisites_met(missions, target, wins):
            reason = 'original_target_mission_prerequisites_not_won'
        elif row.get('cond_event') and row['cond_event'] not in completed:
            reason = 'original_target_event_not_completed'
        elif not area or area.get('st', [None])[0] not in (1, 5):
            reason = 'target_waits_for_original_area_fight_or_strike'
        elif len(area['st']) < 3 or area['st'][2]:
            reason = 'original_target_area_locked'
        else:
            reason = _mission_edge_route_guard(story, aid, city_catalog)
        if reason:
            pending.append({'source':min(proven), 'target':target, 'area':aid, 'reason':reason})
            continue
        root = story.get('condition_mission_roots', {}).get(str(aid))
        if root is not None:
            stage, family = condition_mission_stage(story, missions, root, completed)
            if target in family or stage['cs'] and not set(family).issubset(wins):
                continue
        candidates.setdefault(aid, []).append((target, min(proven)))
    for aid, options in sorted(candidates.items()):
        if stage_projection_owner(state, aid) in ('positive-special', 'coc', 'normal'):
            continue
        target, source = min(options)
        story.setdefault('condition_mission_sources', {})[str(aid)] = source
        story.setdefault('condition_mission_roots', {})[str(aid)] = target
        stage, family = condition_mission_stage(story, missions, target, completed)
        story['city_areas'][str(aid)]['stage'] = stage
        notices.append(('get_area_stages_reply', {'ai':aid, 'st':copy.deepcopy(stage)}))
    story['pending_mission_edges'] = pending
    return notices
