# -*- coding: ascii -*-
"""Original city action RPCs, original team capabilities and patrol choices.

Pure copy transactions. Save whole candidate before any notices. Reliable RPC
identity must be namespaced by session; repeated identity never charges twice.
No chosen patrol event is marked complete and no battle outcome is inferred.
"""
try:
    from offline_daerweila import (compile_daerweila_dispatch, validate_daerweila_state,
        daerweila_request_source, daerweila_source_matches, daerweila_occurrence_matches,
        daerweila_queued_operation_matches, prepare_daerweila_first_choice,
        bind_daerweila_occurrence, apply_daerweila_event, project_daerweila,
        daerweila_sync_notices, publish_daerweila_award, expire_daerweila_dispatch,
        prepare_daerweila_patrol_baseline, mint_daerweila_patrol_offers,
        prepare_daerweila_patrol_delivery, filter_daerweila_availability)
except ImportError:
    pass

try:
    from offline_flashback import (flashback_context, flashback_token, flashback_data,
        flashback_notice, flashback_require_action, flashback_spend_action,
        flashback_accept_entry, flashback_route_handoff, prepare_flashback_operation,
        validate_flashback_state)
except ImportError:
    pass

import re
try:
    from offline_huisu import (huisu_context, huisu_token, validate_huisu_state,
        project_huisu, huisu_notice, huisu_std_projection, huisu_route_projection, validate_huisu_document,
        city_action_context, dream_action_token, authorize_action_admission,
        commit_action_admission, event_execution_admission,
        resolve_event_execution_context, check_dream_contract,
        huisu_trigger_permitted, accept_huisu_event_completion,
        prepare_huisu_operation, mark_huisu_nextday, huisu_day_guard,
        reset_huisu_on_committed_day_or_week)
except ImportError:
    pass

import copy
import hashlib
import json

CITY_ACTION_POLICY = 'original-basic-city-actions-v1'
try:
    _ca_text_types = (basestring,)
except NameError:
    _ca_text_types = (str,)


def initial_city_actions_state():
    return {'version': 1, 'receipts': [], 'patrol': None}


def native_city_action_abilities(owner, heroes):
    """Stock getters include star/order/fallen bonuses; no synthetic hero stats."""
    result = {}
    for hero_id in heroes:
        hero = owner.heroMgrData.getHero(hero_id)
        if hero is None:
            raise ValueError('Missing owned native city hero')
        result[str(hero_id)] = {'insight': hero.getInsightValue(),
                               'construct': hero.getConstructValue(),
                               'leadership': hero.getLeadershipValue()}
    return result


def _ca_int(value):
    return type(value) is int


def _ca_set(value):
    if not isinstance(value, _ca_text_types) or len(value) > 8192:
        return None
    value = value.strip()
    if value == 'set()':
        return set()
    if not re.match(r'^set\(\[\s*(?:\d+\s*(?:,\s*\d+\s*)*,?\s*)?\]\)$', value):
        return None
    try:
        return set(int(number) for number in re.findall(r'\d+', value))
    except ValueError:
        return None


def select_patrol_events(state, triggers, content, evaluate_condition=None):
    """Only inspect currently reachable patrol rows; false beats unknown.

    Unknown optional rows are reported and omitted, not a global city/day lock.
    Required/automatic reachable unknown rows stay pending before charging.
    """
    if evaluate_condition is None:
        # Android concatenates sources in one namespace, without sys.modules.
        evaluate_condition = globals().get('evaluate_story_condition')
    context = state.get('city_actions', {}).get('patrol')
    if not context:
        raise ValueError('Patrol facts require an actual admitted context')
    events, unknown = [], []
    completed = set(state.get('completed_events', []))
    processing = set(state.get('processing_events', []))
    for event, trigger in sorted(triggers.items()):
        conditions = trigger.get('conds', {})
        if not trigger.get('release') or event in completed or event in processing:
            continue
        operations = _ca_set(conditions.get(102, 'set()'))
        if not (3 in conditions or 10 in conditions or operations and 2 in operations):
            continue
        results = []
        for kind, value in conditions.items():
            if kind in (3, 10):
                required = _ca_set(value)
                result = None if required is None else (context['area'] in required if kind == 3
                          else required.issubset(set(context['heroes'])))
            elif kind == 102:
                required = _ca_set(value)
                result = None if required is None else required.issubset(set((2,)))
            else:
                result = evaluate_condition(kind, value, state) if evaluate_condition else None
            results.append((kind, result))
        if any(result is False for kind, result in results):
            continue
        unresolved = [kind for kind, result in results if result is None]
        row = content.get(event)
        if unresolved or row is None or not row.get('release'):
            if row is None or row.get('release'):
                unknown.append({'event': event, 'conditions': unresolved,
                                'required': bool(row and (row.get('isAutoTriggerEvent') or row.get('autoStart')))})
            continue
        if huisu_trigger_permitted(state, event, row, trigger, patrol_selection=True):
            events.append(event)
    return events, unknown


def _ca_counts(story, area_id=None):
    result = {}
    for key, area in story.get('city_areas', {}).items():
        if area_id is not None and str(area_id) != key:
            continue
        if area.get('st', [None])[0] != 0:
            continue
        for building in area.get('bd', {}).values():
            bid = building['id']
            result[bid] = result.get(bid, 0) + 1
    return result


def _ca_capacity(story, buildings, hero_count):
    totals = {'fv': 0, 'rv': 0, 'dv': 0}
    for area in story.get('city_areas', {}).values():
        if area.get('st', [None])[0] != 0:
            continue
        ids = [b['id'] for b in area.get('bd', {}).values()]
        for key, field, extra, factor, perhero in (
                ('fv', 'force_val', 3, 5, 6), ('rv', 'research_val', 8, 10, 11),
                ('dv', 'dev_val', 13, 15, 16)):
            amount = sum(buildings[bid].get(field, 0) for bid in ids)
            producers = sum(bool(buildings[bid].get(field, 0) > 0 or bid == perhero) for bid in ids)
            amount += ids.count(extra) * producers + ids.count(perhero) * min(30, hero_count)
            for unused in range(ids.count(factor)):
                amount = (amount * 3 + 1) // 2
            totals[key] += amount
    return totals



def city_action_area_snapshot(area, development_catalog):
    """Supply original mbn field from developed slots, including first UI load."""
    result = copy.deepcopy(area)
    aid, level = result.get('id'), result.get('lv')
    if not _ca_int(aid) or not _ca_int(level):
        raise ValueError('Original city area identity and development level required')
    result['mbn'] = sum(1 for (area_id, slot), row in development_catalog.items()
                        if area_id == aid and row['level_require'] <= level)
    result.setdefault('bd', {})
    result.setdefault('dbd', {})
    return result


def _ca_notice(story):
    return ('get_all_area_info_reply', {'ais': {'area_%s' % key: copy.deepcopy(value)
        for key, value in story['city_areas'].items()}, 'cd': copy.deepcopy(story['city_values']), 'sm': False})


def _ca_remove_buildings(story, building_id, area_id=None, count=None, unused_only=False):
    removed = 0
    for key, area in sorted(story['city_areas'].items()):
        if area_id is not None and key != str(area_id):
            continue
        for slot, building in list(area.get('bd', {}).items()):
            if (building['id'] == building_id and (not unused_only or not building.get('u')) and
                    (count is None or removed < count)):
                del area['bd'][slot]
                removed += 1
    return removed


def _ca_finish_context(state):
    context = state['city_actions']['patrol']
    if context:
        available = dict(state.get('available_events', []))
        for event in context['events']:
            available.pop(event, None)
        state['available_events'] = [[key, value] for key, value in sorted(available.items())]
    facts = dict(state.get('conditions', []))
    current = facts.get(102)
    if current == 2:
        facts.pop(102, None)
    elif isinstance(current, (list, tuple)):
        facts[102] = [value for value in current if value != 2]
    state['conditions'] = [[key, value] for key, value in sorted(facts.items())]
    state['city_actions']['patrol'] = None
    state['story']['patrol_pending'] = False
    state['story']['patrol_reward_pending'] = False


def select_city_patrol_event(state, event):
    """Call with original startEvent. It selects; it does not finish dialogue."""
    candidate = copy.deepcopy(state)
    context = candidate.get('city_actions', {}).get('patrol')
    if not context or event not in context['events']:
        return candidate, False
    if context.get('selected') not in (None, event):
        raise ValueError('Another patrol choice was already selected')
    changed = context.get('selected') != event
    context['selected'] = event
    return candidate, changed


def complete_city_patrol_event(state, event):
    """Call only AFTER original event planner really records completed event."""
    candidate = copy.deepcopy(state)
    context = candidate.get('city_actions', {}).get('patrol')
    if not context or context.get('selected') != event:
        return candidate, False
    if event not in candidate.get('completed_events', []):
        raise ValueError('Selected patrol dialogue or battle is not complete')
    _ca_finish_context(candidate)
    return candidate, True


def prepare_city_action(state, operation, arguments, catalogs, operation_id,
                        abilities=None, make_id=None, stock_day=None,
                        evaluate_condition=None):
    """Concrete original-table city transaction -> candidate,notices,changed,diag.

    catalogs: building/development/upgrade/patrol/hero + optional triggers/content.
    abilities: native_city_action_abilities(owner, hs), not caller UI estimates.
    operation_id: stable reliable callback identity scoped by client session.
    Base action policy has no undocumented money/EXP bonus; actual patrol choice
    grants original favor_reward only on patrolReward. Event rewards remain in
    the real original event planner. Native team selectors are never replaced.
    """
    if not operation_id:
        raise ValueError('Stable reliable operation identity required')
    if operation not in ('areaBuildRequest', 'areaLevelUpRequest', 'enterPatrolRequest', 'patrolReward'):
        raise ValueError('Unsupported city action RPC')
    candidate = copy.deepcopy(state)
    protocol = candidate.setdefault('city_actions', initial_city_actions_state())
    validate_city_actions_state(protocol)
    validate_huisu_document(candidate)
    payload = {key: value for key, value in arguments.items() if key != '_cbid_'}
    fingerprint = hashlib.sha256(json.dumps([operation, payload], sort_keys=True).encode('utf-8')).hexdigest()
    for receipt in protocol['receipts']:
        if receipt['id'] == operation_id:
            if receipt['fingerprint'] != fingerprint:
                raise ValueError('Reliable identity reused for a different city action')
            if receipt.get('context_token') is not None and receipt['context_token'] != dream_action_token(candidate):
                raise ValueError('Reliable dream admission belongs to stale context')
            return copy.deepcopy(state), copy.deepcopy(receipt['notices']), False, {'replay': True}
    if operation == 'enterPatrolRequest' and prepare_daerweila_patrol_baseline(candidate, catalogs):
        return candidate, [('enter_patrol_reply', {'s': False, 'rs': False, 'ext': {}, 'ev': []})], candidate != state, {'pending': 'legacy-daerweila-baseline-requires-verifiable-source'}
    notices, diagnostic = [], {'policy': CITY_ACTION_POLICY}
    story, profile = candidate['story'], candidate['profile']
    context = protocol.get('patrol')
    if operation == 'patrolReward':
        if payload:
            raise ValueError('patrolReward takes no arguments')
        if not context:
            return copy.deepcopy(state), [('serverCallbackCarrier', {'_r_': {}})], False, {'nothing_to_claim': True}
        if context.get('selected') is not None:
            raise ValueError('Chosen original patrol event must finish through its real event lifecycle')
        changes = {}
        for hero in context['heroes']:
            record = profile['heroes'][str(hero)]
            previous = record['ef']
            record['ef'] = min(100, previous + context['favor'][str(hero)])
            changes[str(hero)] = record['ef'] - previous
            notices.append(('updateFriendlyValue', {'h': hero, 'v': record['ef']}))
        _ca_finish_context(candidate)
        notices.extend([('notify_add_friendly', {'fr': changes, 'n': {}}),
                        ('serverCallbackCarrier', {'_r_': {}})])
    else:
        if operation == 'enterPatrolRequest' and set(payload) != set(('aid', 'hs')):
            raise ValueError('Invalid original patrol request fields')
        provider = city_action_context(candidate, operation)
        dream_patrol = bool(provider and provider['kind'] == 'route20_huisu')
        aid, heroes = payload.get('aid'), payload.get('hs')
        if not _ca_int(aid) or not isinstance(heroes, list) or not (0 if dream_patrol else 1) <= len(heroes) <= 3 or any(not _ca_int(h) for h in heroes) or len(set(heroes)) != len(heroes):
            raise ValueError('Invalid original city area/team parameters')
        if operation == 'enterPatrolRequest' and context:
            if context['area'] != aid or context['heroes'] != heroes or context.get('selected') is not None:
                raise ValueError('Another patrol choice is pending')
            return copy.deepcopy(state), [('enter_patrol_reply', {'s': True, 'rs': True, 'ext': {}, 'ev': list(context['events'])})], False, {'resume_patrol': True}
        if context or story.get('emergency') or (candidate.get('battle') or {}).get('active'):
            raise ValueError('Current real story/battle/patrol must finish first')
        day = candidate.get('day', {}).get('stock_day', stock_day)
        if not _ca_int(day) or not 0 <= day < 7:
            raise ValueError('Original MAX_DAYNUM8 final-day guard')
        area = story.get('city_areas', {}).get(str(aid))
        if not area or area.get('st', [None])[0] != 0 or len(area['st']) < 3 or area['st'][2]:
            raise ValueError('City action requires a real unlocked FREE area')
        if any(str(hero) not in profile['heroes'] for hero in heroes):
            raise ValueError('City team contains an unowned hero')
        if heroes and (not abilities or any(str(hero) not in abilities for hero in heroes)):
            raise ValueError('Missing original hero city capability calculation')
        all_counts, counts = _ca_counts(story), _ca_counts(story, aid)
        city = story['city_values']
        buildings = catalogs['building']
        before_capacity = _ca_capacity(story, buildings, len(profile['heroes']))
        before_area_capacity = {key: _ca_capacity({'city_areas': {key: value}}, buildings, len(profile['heroes']))
                                for key, value in story['city_areas'].items()}
        if operation == 'areaBuildRequest':
            if set(payload) != set(('aid', 'hs', 'fi', 'bi')):
                raise ValueError('Invalid original build request fields')
            slot, bid = payload['fi'], payload['bi']
            row = buildings.get(bid)
            if not _ca_int(slot) or not _ca_int(bid) or not row or not 1 <= bid <= 47 or row.get('ban') or row.get('clientBan'):
                raise ValueError('Unknown original building or hidden/disabled building')
            field = catalogs['development'].get((aid, slot))
            if not field or area['lv'] < field['level_require'] or str(slot) in area.get('bd', {}):
                raise ValueError('Building field is occupied or not developed')
            blueprints = set(story.get('buildable_buildings', ())) | set(city.get('hb', ())) | set(story.get('hidden_buildings', ()))
            if not row.get('init') and not row.get('pre') and bid not in blueprints:
                raise ValueError('Building blueprint not unlocked')
            if any(not all_counts.get(required) for required in row.get('pre', [])):
                raise ValueError('Original building predecessors missing')
            if aid in row.get('al', {}) and counts.get(bid, 0) >= row['al'][aid] or row.get('ml') and all_counts.get(bid, 0) >= row['ml']:
                raise ValueError('Original building area/city limit exceeded')
            local_pre = row.get('area_building_require', {})
            if local_pre and not any(counts.get(required, 0) >= number for required, number in local_pre.items()):
                raise ValueError('Original local building prerequisites missing')
            research = row['research_require']
            unused_coupons = sum(b['id'] == 20 and not b.get('u')
                for a in story['city_areas'].values() if a.get('st', [None])[0] == 0
                for b in a.get('bd', {}).values())
            coupons = min(unused_coupons, (research + 24) // 25)
            if city['rv'] < max(0, research - 25 * coupons):
                raise ValueError('Insufficient original city research')
            action, money, fatigue, required, skill = row['ac'], row['mc'], row['fc'], row['cr'], 'construct'
            bonus = all_counts.get(28, 0) * 3
        elif operation == 'areaLevelUpRequest':
            if set(payload) != set(('aid', 'hs', 'luv')) or not _ca_int(payload['luv']) or payload['luv'] != 1:
                raise ValueError('Original development advances exactly one level')
            row = catalogs['upgrade'].get((aid, area['lv'] + 1))
            if not row:
                raise ValueError('Area is at original maximum development')
            action, money, fatigue, required, skill = row['action_consume'], row['money_consume'], row['fatigue'], row['lead_require'], 'leadership'
            bonus = all_counts.get(27, 0) * 3
        else:
            if set(payload) != set(('aid', 'hs')) or area.get('pl'):
                raise ValueError('Patrol is locked or parameters invalid')
            row = catalogs['patrol'].get((aid, area['lv']))
            if not row:
                raise ValueError('Missing original patrol data')
            number = city.get('pn', 1)
            action, money, fatigue = row['action_consume'], 0, row['fatigue']
            if counts.get(21): action = 1
            if counts.get(22): fatigue = -25
            required, skill = row.get('ir%d' % number, row['ir']), 'insight'
            bonus = all_counts.get(26, 0) * 3
        if any(not _ca_int(v) or v < 0 for v in (action, money, required, bonus)) or not _ca_int(fatigue):
            raise ValueError('Invalid original city action costs')
        powers = [(abilities or {})[str(hero)].get(skill) for hero in heroes]
        if not dream_patrol and (any(not _ca_int(v) or v < 0 for v in powers) or sum(powers) + bonus < required):
            raise ValueError('Insufficient actual original team city capability')
        provider = authorize_action_admission(candidate, operation, operation_id, fingerprint)
        flashback = bool(provider and provider['kind'] == 'route35_flashback')
        if flashback:
            flashback_require_action(candidate)
        if (not flashback and not dream_patrol and city['av'] < action) or city['bf'] < money or (not dream_patrol and any(profile['heroes'][str(hero)]['cf'] < max(0, fatigue) for hero in heroes)):
            raise ValueError('Insufficient action/fund/fatigue')
        if operation == 'enterPatrolRequest':
            favor = {}
            for hero in heroes:
                gender = catalogs.get('hero', {}).get(hero, {}).get('gender')
                favor[str(hero)] = row['favor_reward'] + (counts.get(23, 0) if gender in (1, 4) else 0) + (counts.get(24, 0) if gender in (2, 4) else 0)
            protocol['patrol'] = {'area': aid, 'heroes': list(heroes), 'events': [], 'selected': None, 'favor': favor,
                'admission_id': operation_id, 'week': story.get('week', 0), 'day': day}
            if provider:
                protocol['patrol'].update(context_kind=provider['kind'], context_token=provider['token'])
            events, unknown = select_patrol_events(candidate, catalogs.get('triggers', {}), catalogs.get('content', {}), evaluate_condition)
            if any(entry['required'] for entry in unknown):
                return copy.deepcopy(state), [], False, {'pending': unknown}
            protocol['patrol']['events'] = events
            facts = dict(candidate.get('conditions', []))
            current = facts.get(102)
            operations = list(current) if isinstance(current, (list, tuple)) else ([] if current is None else [current])
            facts[102] = sorted(set(operations + [2]))
            candidate['conditions'] = [[key, value] for key, value in sorted(facts.items())]
            available = dict(candidate.get('available_events', []))
            available.update({event: 1 for event in events})
            candidate['available_events'] = [[key, value] for key, value in sorted(available.items())]
            story['patrol_pending'] = story['patrol_reward_pending'] = True
            if not dream_patrol:
                city['pn'] = city.get('pn', 1) + 1
                city['tpn'] = city.get('tpn', 0) + 1
                _ca_remove_buildings(story, 22, aid)
            else:
                protocol['patrol']['favor'] = {str(hero): 0 for hero in heroes}
                notices.extend(commit_action_admission(candidate, provider, operation_id, fingerprint, aid, heroes))
            diagnostic['optional_unknown_events'] = unknown
            notices.append(('enter_patrol_reply', {'s': True, 'rs': True, 'ext': {}, 'ev': events}))
        elif operation == 'areaBuildRequest':
            if make_id is None:
                raise ValueError('Original building identity generator required')
            building_uuid = str(make_id())
            if not building_uuid or any(b.get('uuid') == building_uuid for a in story['city_areas'].values() for b in a.get('bd', {}).values()):
                raise ValueError('Building identity must be fresh')
            area.setdefault('bd', {})[str(slot)] = {'id': bid, 'uuid': building_uuid}
            if coupons: _ca_remove_buildings(story, 20, count=coupons, unused_only=True)
            city['tbn'] = city.get('tbn', 0) + 1
            notices.append(('area_build_reply', {'rs': True, 'aid': aid, 'ext': {}}))
        else:
            area['lv'] += 1
            city['tvn'] = city.get('tvn', 0) + 1
            notices.append(('area_level_up_reply', {'rs': True, 'aid': aid, 'ext': {}}))
        area.update(city_action_area_snapshot(area, catalogs['development']))
        if flashback:
            notices.extend(flashback_spend_action(candidate))
        elif not dream_patrol:
            city['av'] -= action
        city['bf'] -= money
        fatigue_notices = []
        for hero in ([] if dream_patrol else heroes):
            record = profile['heroes'][str(hero)]
            record['cf'] = min(100, record['cf'] - fatigue)
            fatigue_notices.append(('updateCurFatigueValue', {'h': hero, 'v': record['cf']}))
        after_capacity = _ca_capacity(story, buildings, len(profile['heroes']))
        for key in ('fv', 'rv', 'dv'):
            city[key] += after_capacity[key] - before_capacity[key]
        for area_key, area_value in story['city_areas'].items():
            after_area = _ca_capacity({'city_areas': {area_key: area_value}}, buildings, len(profile['heroes']))
            for key in ('fv', 'rv', 'dv'):
                area_value[key] = area_value.get(key, 0) + after_area[key] - before_area_capacity[area_key][key]
        notices = fatigue_notices + [_ca_notice(story)] + notices
    receipt = {'id': operation_id, 'fingerprint': fingerprint, 'notices': copy.deepcopy(notices)}
    if operation != 'patrolReward' and provider:
        receipt['context_token'] = provider['token']
    protocol['receipts'].append(receipt)
    protocol['receipts'] = protocol['receipts'][-64:]
    if operation == 'enterPatrolRequest':
        mint_daerweila_patrol_offers(candidate, catalogs, receipt)
        notices = prepare_daerweila_patrol_delivery(candidate, catalogs, notices)
        receipt['notices'] = copy.deepcopy(notices)
    validate_city_actions_state(protocol)
    return candidate, notices, True, diagnostic


def validate_city_actions_state(protocol):
    if (not isinstance(protocol, dict) or protocol.get('version') != 1 or
            not isinstance(protocol.get('receipts'), list) or len(protocol['receipts']) > 64):
        raise ValueError('Invalid city action protocol')
    seen = set()
    for receipt in protocol['receipts']:
        identity = receipt.get('id')
        digest = receipt.get('fingerprint', '')
        if (not isinstance(identity, _ca_text_types) or not identity or identity in seen or
                not isinstance(digest, _ca_text_types) or len(digest) != 64 or
                any(char not in '0123456789abcdef' for char in digest) or
                not isinstance(receipt.get('notices'), list)):
            raise ValueError('Invalid city action receipt')
        seen.add(identity)
    context = protocol.get('patrol')
    if context is not None:
        if (not isinstance(context, dict) or not _ca_int(context.get('area')) or
                not isinstance(context.get('heroes'), list) or not (0 if context.get('context_kind') == 'route20_huisu' and isinstance(context.get('context_token'), _ca_text_types) and context.get('context_token', '').startswith('route20_huisu:') and context.get('admission_id') else 1) <= len(context['heroes']) <= 3 or
                any(not _ca_int(hero) for hero in context['heroes']) or len(set(context['heroes'])) != len(context['heroes']) or
                not isinstance(context.get('events'), list) or any(not _ca_int(event) for event in context['events']) or
                context.get('selected') is not None and context['selected'] not in context['events'] or
                not isinstance(context.get('favor'), dict) or
                any(not _ca_int(context['favor'].get(str(hero))) or context['favor'][str(hero)] < 0 for hero in context['heroes'])):
            raise ValueError('Invalid persisted original patrol context')
