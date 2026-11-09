# -*- coding: ascii -*-
"""Finite offline dream context policy, never an original-server assertion.

Only a real request establishes route20 provenance. Three accepted patrols use
an independent budget. Original trigger/choice/dialogue/battle proof remains
mandatory. JSON catalogs normalize native tuples to lists; only that container
normalization is accepted for the exact string sentinel.
"""
import copy
try:
    from offline_flashback import flashback_context, flashback_token
    from offline_conditions import parse_original_condition_literal
except ImportError:
    pass
try:
    _hs_text = (basestring,)
except NameError:
    _hs_text = (str,)

HUISU_POLICY = 'offline-route20-dream-context-v1'


def validate_huisu_state(value):
    if value is None:
        return
    if (not isinstance(value, dict) or value.get('version') != 1 or
            value.get('policy') != HUISU_POLICY or
            value.get('phase') not in ('entering', 'active', 'left') or
            any(type(value.get(k)) is not int for k in ('week', 'stock_day', 'condition_date', 'generation', 'entry_event', 'used_actions')) or
            not 0 <= value['stock_day'] <= 5 or value['generation'] < 1 or
            value['entry_event'] < 1 or not 0 <= value['used_actions'] <= 3 or
            not isinstance(value.get('route'), _hs_text) or not value['route'] or
            type(value.get('night_event')) is not int or value['night_event'] < 1 or
            not isinstance(value.get('entry_operation'), _hs_text) or not value['entry_operation'] or
            not isinstance(value.get('admissions'), dict) or len(value['admissions']) != value['used_actions']):
        raise ValueError('Invalid versioned huisu context')
    for identity, admission in value['admissions'].items():
        if (not isinstance(identity, _hs_text) or not identity or not isinstance(admission, dict) or
                not isinstance(admission.get('fingerprint'), _hs_text) or len(admission['fingerprint']) != 64 or
                any(c not in '0123456789abcdef' for c in admission['fingerprint']) or
                admission.get('token') != _hs_value_token(value) or
                type(admission.get('area')) is not int or not isinstance(admission.get('heroes'), list) or
                len(admission['heroes']) > 3 or any(type(h) is not int for h in admission['heroes']) or
                len(set(admission['heroes'])) != len(admission['heroes'])):
            raise ValueError('Invalid huisu admission provenance')
    if value['phase'] in ('active', 'left') and not value.get('entry_occurrence'):
        raise ValueError('Active huisu requires actual entry occurrence')
    if value.get('entry_occurrence') is not None and not isinstance(value['entry_occurrence'], _hs_text):
        raise ValueError('Invalid huisu entry occurrence')
    if value.get('night_intent') not in (None, _hs_value_token(value)):
        raise ValueError('Invalid huisu night token')


def _hs_value_token(value):
    return 'route20_huisu:%s:%s:%s:%s' % (value['week'], value['stock_day'], value['route'], value['generation'])


def huisu_context(state, include_left=False):
    story = state.get('story', {})
    value = story.get('route20_huisu')
    validate_huisu_state(value)
    if value is None:
        return None
    if (value['week'] != story.get('week') or value['stock_day'] != state.get('day', {}).get('stock_day') or
            value['route'] != story.get('route') or value['condition_date'] != story.get('date')):
        return None
    if value['phase'] == 'left' and not include_left:
        return None
    return value


def huisu_token(state):
    value = huisu_context(state, True)
    return _hs_value_token(value) if value else None


def city_action_context(state, operation):
    value, flashback = huisu_context(state), flashback_context(state)
    if value and flashback:
        raise ValueError('Incompatible simultaneous dream providers')
    if value:
        if value['phase'] != 'active' or operation not in ('enterPatrolRequest', 'patrolReward'):
            raise ValueError('Huisu context permits active dream patrol only')
        return {'kind': 'route20_huisu', 'token': huisu_token(state)}
    if flashback:
        return {'kind': 'route35_flashback', 'token': flashback_token(state)}
    return None


def dream_action_token(state):
    value = huisu_context(state)
    if value and flashback_context(state):
        raise ValueError('Incompatible simultaneous dream providers')
    return huisu_token(state) if value else flashback_token(state)


def project_huisu(state):
    value = huisu_context(state, True)
    active = bool(value and value['phase'] in ('entering', 'active'))
    return {'hs': [], 'hsf': active, 'hst': value['used_actions'] if active else 0,
            'lhs': bool(value and value['phase'] == 'left' or _hs_day_stamp(state) in state.get('story', {}).get('huisu_left_days', []))}


def huisu_notice(state):
    return ('syncHuiSuData', {'d': project_huisu(state)})


def huisu_route_projection(state):
    data = project_huisu(state)
    return {k: data[k] for k in ('hs', 'hsf', 'hst')}


def huisu_std_projection(state):
    data = project_huisu(state)
    return {'hsu': data['hs'], 'hsf': data['hsf'], 'hst': data['hst'], 'lhs': data['lhs']}


def _hs_table_entry(state, tables):
    story = state.get('story', {})
    route, day = story.get('route'), state.get('day', {}).get('stock_day')
    if not isinstance(route, _hs_text) or type(day) is not int:
        return None
    catalog = tables.get('story_dream', {})
    row = catalog.get((route, day)) or catalog.get((route.split('-')[0], day))
    # Original cdata rows may be read-only tagged mappings, not dicts. Only
    # these two scalar fields cross into the plain persisted context; all
    # existing integer, prerequisite, route/day and busy checks remain below.
    items = getattr(row, 'items', None)
    if not callable(items):
        return None
    selected = {}
    try:
        for pair in items():
            if not isinstance(pair, (tuple, list)) or len(pair) != 2:
                return None
            key, value = pair
            if isinstance(key, _hs_text) and key in ('event', 'goodnight_event'):
                if key in selected:
                    return None
                selected[key] = value
    except (TypeError, ValueError):
        return None
    return selected


def _hs_busy(state):
    story = state.get('story', {})
    return bool(state.get('processing_events') or story.get('pending_effects') or
        (state.get('battle') or {}).get('active') or (state.get('city_actions') or {}).get('patrol') or
        story.get('patrol_pending') or story.get('patrol_reward_pending'))


def _hs_remove_nextday(state):
    facts = dict(state.get('conditions', []))
    value = facts.get(102)
    values = list(value) if isinstance(value, (list, tuple)) else ([] if value is None else [value])
    values = [v for v in values if v != 4]
    if values:
        facts[102] = values
    else:
        facts.pop(102, None)
    state['conditions'] = [[k, v] for k, v in sorted(facts.items())]


def huisu_request_source(state):
    story = state.get('story', {})
    return {'token': huisu_token(state), 'week': story.get('week'),
        'stock_day': state.get('day', {}).get('stock_day'), 'route': story.get('route'),
        'generation': story.get('huisu_generation', 0)}


def _hs_enter_notices(state):
    story = state['story']
    # Original syncRoute owns the false->true animation edge. Publish before
    # syncHuiSuData, including reliable replay after a publication failure.
    return [('syncRoute', {'rt': story['route'], 'srt': copy.deepcopy(story.get('sub_routes', [])),
        'i': False, 'hsd': huisu_route_projection(state), 'fbd': {}}), huisu_notice(state)]


def prepare_huisu_operation(state, operation, arguments, tables, source_token=None, operation_id=None):
    candidate = copy.deepcopy(state)
    story = candidate['story']
    value = huisu_context(candidate, True)
    if arguments:
        raise ValueError('Expected original empty huisu RPC')
    if operation == 'requestStoryhuisuOut':
        if value is None or value['phase'] == 'left':
            return candidate, [huisu_notice(candidate)], False, {'inactive': True}
        if source_token != huisu_token(candidate):
            return copy.deepcopy(state), [], False, {'pending': 'stale_huisu_context'}
        if _hs_busy(candidate) or value['phase'] != 'active':
            return copy.deepcopy(state), [], False, {'pending': 'actual_huisu_gameplay_pending'}
        value['phase'] = 'left'
        value['exit_receipt'] = source_token
        return candidate, [('recoverStoryline', {}), huisu_notice(candidate)], True, {'policy': HUISU_POLICY}
    if operation != 'requestStoryhuisu' or not operation_id:
        raise ValueError('Real reliable huisu entry identity required')
    if isinstance(source_token, dict):
        source = source_token
        expected = huisu_request_source(candidate)
        same_request = bool(value and value['entry_operation'] == operation_id)
        if (any(source.get(k) != expected.get(k) for k in ('week', 'stock_day', 'route')) or
                not same_request and source != expected):
            return copy.deepcopy(state), [], False, {'pending': 'stale_huisu_entry_source'}
        source_token = source.get('token')
    if value:
        # Same-day tombstone forbids refill; retry resumes the exact occurrence.
        notices = [huisu_notice(candidate)] if value['phase'] == 'left' else _hs_enter_notices(candidate)
        return candidate, notices, False, {'replay': True, 'phase': value['phase']}
    if source_token is not None:
        return copy.deepcopy(state), [], False, {'pending': 'stale_huisu_entry'}
    if _hs_day_stamp(candidate) in story.get('huisu_left_days', []):
        return copy.deepcopy(state), [huisu_notice(candidate)], False, {'pending': 'same_day_huisu_already_left'}
    row = _hs_table_entry(candidate, tables)
    entry = row.get('event') if isinstance(row, dict) else None
    if (type(entry) is not int or entry <= 0 or type(row.get('goodnight_event')) is not int or row.get('goodnight_event', 0) < 1 or flashback_context(candidate) or
            not 0 <= candidate.get('day', {}).get('stock_day', -1) <= 5):
        return copy.deepcopy(state), [], False, {'pending': 'no_executable_huisu_table_entry'}
    content, triggers = tables.get('event_content', {}), tables.get('event_condition', {})
    if not content.get(entry, {}).get('release') or not triggers.get(entry, {}).get('release'):
        return copy.deepcopy(state), [], False, {'pending': 'original_huisu_entry_unavailable'}
    try:
        prerequisites = parse_original_condition_literal(triggers[entry].get('conds', {}).get(1, 'set()'))
        if not isinstance(prerequisites, (set, list, tuple)) or any(type(e) is not int for e in prerequisites):
            raise ValueError('Invalid original entry predecessor set')
    except (ValueError, TypeError):
        return copy.deepcopy(state), [], False, {'pending': 'unsupported_entry_predecessors'}
    if not set(prerequisites).issubset(set(candidate.get('completed_events', []))):
        return copy.deepcopy(state), [], False, {'pending': 'actual_entry_predecessors_required'}
    if entry in candidate.get('completed_events', []):
        return copy.deepcopy(state), [], False, {'pending': 'unsupported_legacy_dream_continuation'}
    if _hs_busy(candidate) or story.get('emergency'):
        return copy.deepcopy(state), [], False, {'pending': 'actual_huisu_gameplay_pending'}
    generation = story.get('huisu_generation', 0) + 1
    story['huisu_generation'] = generation
    story['route20_huisu'] = {'version': 1, 'policy': HUISU_POLICY, 'week': story['week'],
        'stock_day': candidate['day']['stock_day'], 'condition_date': story['date'],
        'route': story['route'], 'generation': generation, 'phase': 'entering',
        'entry_event': entry, 'night_event': row.get('goodnight_event'),
        'entry_operation': operation_id, 'entry_occurrence': None,
        'used_actions': 0, 'admissions': {}, 'night_intent': None}
    return candidate, _hs_enter_notices(candidate), True, {'policy': HUISU_POLICY, 'awaits': 'actual_entry_trigger'}


def authorize_action_admission(state, operation, operation_id, fingerprint, source_token=None):
    provider = city_action_context(state, operation)
    if provider and source_token is not None and source_token != provider['token']:
        raise ValueError('Reserved dream action context changed')
    if provider and provider['kind'] == 'route20_huisu':
        if _hs_busy(state):
            raise ValueError('Actual dream dialogue/battle/patrol pending')
        value = huisu_context(state)
        admission = value['admissions'].get(operation_id)
        if admission and admission['fingerprint'] != fingerprint:
            raise ValueError('Reliable dream identity reused')
        if admission is None and value['used_actions'] >= 3:
            raise ValueError('Huisu three-action budget exhausted')
    return provider


def commit_action_admission(state, provider, operation_id, fingerprint, area, heroes):
    if not provider or provider['kind'] != 'route20_huisu':
        return []
    if provider['token'] != huisu_token(state):
        raise ValueError('Reserved huisu admission changed')
    value = huisu_context(state)
    if operation_id not in value['admissions']:
        if value['used_actions'] >= 3:
            raise ValueError('Huisu three-action budget exhausted')
        value['admissions'][operation_id] = {'fingerprint': fingerprint, 'token': provider['token'],
            'area': area, 'heroes': list(heroes), 'selected_occurrence': None}
        value['used_actions'] += 1
    return [huisu_notice(state)]


def event_execution_admission(state, event, row, trigger=None, parent_occurrence=None, patrol_selection=False):
    """Bind only accepted parent edges or actual table trigger/admission facts."""
    story = state['story']
    if parent_occurrence:
        parent = story.get('event_contexts', {}).get(parent_occurrence)
        if parent and resolve_event_execution_context(state, parent_occurrence, {}, {}) is not None:
            result = copy.deepcopy(parent)
            result.update(origin='successor', parent_occurrence=parent_occurrence, source_event=event)
            return result
    value = huisu_context(state, True)
    patrol = (state.get('city_actions') or {}).get('patrol')
    provider = None
    if value:
        provider = {'kind': 'route20_huisu', 'token': huisu_token(state)}
    elif flashback_context(state):
        provider = {'kind': 'route35_flashback', 'token': flashback_token(state)}
    if provider is None:
        return None
    result = dict(provider, route=story.get('route'), week=story.get('week'), date=story.get('date'), source_event=event)
    if value and event == value.get('night_event') and value.get('night_intent') == _hs_value_token(value):
        result.update(origin='trigger', night_chain=True)
        return result
    if value and value['phase'] == 'left':
        return None
    if value and value['phase'] == 'entering' and event == value['entry_event']:
        result['origin'] = 'entry'
        return result
    if patrol and (event in patrol.get('events', []) or patrol_selection) and patrol.get('context_kind') == provider['kind'] and patrol.get('context_token') == provider['token']:
        result.update(origin='patrol', admission_id=patrol.get('admission_id'))
        return result
    # Trigger provenance is permitted only for non-patrol rows, evaluated by
    # the caller. Marker-only rows with no original condition stay unknown.
    conditions = (trigger or {}).get('conds', {})
    if conditions and not any(k in conditions for k in (3, 10)):
        result['origin'] = 'trigger'
        return result
    return None


def _hs_execution_shape(context):
    return bool(isinstance(context, dict) and
        context.get('kind') in ('route20_huisu', 'route35_flashback') and
        context.get('origin') in ('entry', 'patrol', 'trigger', 'successor') and
        isinstance(context.get('token'), _hs_text) and context['token'] and
        isinstance(context.get('route'), _hs_text) and context['route'] and
        all(type(context.get(k)) is int for k in ('week', 'date', 'source_event')))


def resolve_event_execution_context(state, occurrence, row=None, tables=None):
    context = state.get('story', {}).get('event_contexts', {}).get(str(occurrence))
    if not _hs_execution_shape(context):
        return None
    kind = context.get('kind')
    token = huisu_token(state) if kind == 'route20_huisu' else flashback_token(state) if kind == 'route35_flashback' else None
    story = state.get('story', {})
    if (token is None or token != context.get('token') or context.get('week') != story.get('week') or
            context.get('route') != story.get('route') or context.get('date') != story.get('date')):
        return None
    if kind == 'route20_huisu' and huisu_context(state, True)['phase'] == 'left' and not context.get('night_chain'):
        return None
    if kind == 'route20_huisu' and context.get('origin') == 'patrol':
        if context.get('admission_id') not in huisu_context(state)['admissions']:
            return None
    return copy.deepcopy(context)


def check_dream_contract(row, execution_context):
    if 'dream_id' not in row:
        return True
    marker = row['dream_id']
    return bool(isinstance(marker, (tuple, list)) and len(marker) == 1 and
                isinstance(marker[0], _hs_text) and marker[0] == '-1' and _hs_execution_shape(execution_context))


def huisu_trigger_permitted(state, event, row, trigger, patrol_selection=False):
    value = huisu_context(state, True)
    if value:
        if event == value['entry_event'] and value['phase'] != 'entering':
            return False
        if event == value.get('night_event') and (value['phase'] not in ('active', 'left') or value.get('night_intent') != huisu_token(state)):
            return False
    if 'dream_id' in row:
        return check_dream_contract(row, event_execution_admission(state, event, row, trigger, patrol_selection=patrol_selection))
    return True


def accept_huisu_event_completion(state, event, occurrence):
    value = huisu_context(state, True)
    if value and event == value['entry_event'] and value['phase'] == 'entering' and value.get('entry_occurrence') == occurrence:
        value['phase'] = 'active'
        _hs_remove_nextday(state)
        state.get('day', {})['intent'] = None
        return [huisu_notice(state)]
    if value and event == value.get('night_event') and value.get('night_intent') == huisu_token(state):
        value['night_occurrence'] = occurrence
    return []


def mark_huisu_nextday(state, intent_id, source_token=None):
    value = huisu_context(state, True)
    if value is None:
        return
    if source_token != _hs_value_token(value) or not intent_id:
        raise ValueError('Actual huisu NEXTDAY identity/context required')
    if value['phase'] != 'entering':
        value['night_intent'] = _hs_value_token(value)
        value['night_intent_id'] = intent_id


def huisu_day_guard(state):
    value = huisu_context(state, True)
    if value is None:
        return None
    if (_hs_busy(state) or value['phase'] == 'entering' or
            value.get('night_intent') != _hs_value_token(value) or not value.get('night_occurrence') or
            value.get('night_event') not in state.get('completed_events', [])):
        return 'actual_huisu_night_chain_required'
    context = state['story'].get('event_contexts', {}).get(value['night_occurrence'])
    if not context or context.get('token') != _hs_value_token(value):
        return 'actual_huisu_night_provenance_required'
    return None


def _hs_day_stamp(state):
    return '%s:%s' % (state.get('story', {}).get('week'), state.get('day', {}).get('stock_day'))


def expire_huisu_on_route_handoff(state, next_route):
    value = state.get('story', {}).get('route20_huisu')
    if value and value['route'] != next_route:
        story = state['story']
        story.setdefault('huisu_context_history', {})[_hs_value_token(value)] = copy.deepcopy(value)
        stamp = _hs_day_stamp(state)
        if stamp not in story.setdefault('huisu_left_days', []):
            story['huisu_left_days'].append(stamp)
        story.pop('route20_huisu', None)
        return [huisu_notice(state)]
    return []


def reset_huisu_on_committed_day_or_week(state):
    state.get('story', {}).pop('route20_huisu', None)
    return [huisu_notice(state)]


def validate_huisu_document(state):
    """Cross-check active schema, admissions and lineage at save/load boundaries."""
    story = state.get('story', {})
    value = story.get('route20_huisu')
    validate_huisu_state(value)
    if value is not None and huisu_context(state, True) is None:
        raise ValueError('Persisted huisu context does not match original week/day/route')
    contexts = story.get('event_contexts', {})
    if not isinstance(contexts, dict):
        raise ValueError('Invalid dream occurrence lineage')
    for occurrence, context in contexts.items():
        if (not isinstance(occurrence, _hs_text) or not isinstance(context, dict) or
                context.get('kind') not in ('route20_huisu', 'route35_flashback') or
                context.get('origin') not in ('entry', 'patrol', 'trigger', 'successor') or
                not isinstance(context.get('token'), _hs_text) or not context['token'] or
                not isinstance(context.get('route'), _hs_text) or
                any(type(context.get(k)) is not int for k in ('week', 'date', 'source_event'))):
            raise ValueError('Invalid persisted dream occurrence lineage')
    patrol = (state.get('city_actions') or {}).get('patrol')
    if patrol and patrol.get('context_kind') == 'route20_huisu':
        if value is None or value['phase'] != 'active' or patrol.get('context_token') != _hs_value_token(value):
            raise ValueError('Persisted dream patrol requires active admitted context')
        admission = value['admissions'].get(patrol.get('admission_id'))
        if not admission or admission['area'] != patrol.get('area') or admission['heroes'] != patrol.get('heroes'):
            raise ValueError('Persisted dream patrol admission is absent')
    if patrol and patrol.get('context_kind') == 'route35_flashback':
        if patrol.get('context_token') != flashback_token(state):
            raise ValueError('Persisted flashback patrol round changed')
