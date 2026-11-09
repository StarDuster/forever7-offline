# -*- coding: ascii -*-
"""Bounded route35 three-action policy; not official server reconstruction.

Pure copies only. Gateway persists before publishing original callbacks. No
clock, invented win, event completion, city reset or ordinary av refill exists.
"""
import copy

try:
    _fb_text = (basestring,)
except NameError:
    _fb_text = (str,)

FLASHBACK_POLICY = 'offline-route35-three-action-round-v1'
FLASHBACK_TERMINALS = (7761, 7766, 7772, 7778, 7783, 7786)


def flashback_context(state):
    story = state.get('story', {})
    value = story.get('route35_flashback')
    if (not isinstance(value, dict) or not value.get('active') or
            story.get('route') != '35-3' or story.get('date') != 6 or
            state.get('day', {}).get('stock_day') != 6 or
            value.get('week') != story.get('week')):
        return None
    validate_flashback_state(value)
    return value


def validate_flashback_state(value):
    if value is None:
        return
    if (not isinstance(value, dict) or value.get('version') != 1 or
            type(value.get('active')) is not bool or
            type(value.get('index')) is not int or not 1 <= value['index'] <= 7 or
            type(value.get('used_actions')) is not int or not 0 <= value['used_actions'] <= 3 or
            not isinstance(value.get('transition_receipts'), dict) or
            not isinstance(value.get('entry_occurrence'), _fb_text) or
            type(value.get('week')) is not int):
        raise ValueError('Invalid bounded flashback state')


def flashback_token(state):
    value = flashback_context(state)
    if value is None:
        return None
    return '%s:%s:%s' % (value['week'], value['entry_occurrence'], value['index'])


def flashback_data(state):
    value = flashback_context(state)
    return {'ff': bool(value), 'fd': value['index'] if value else 0,
            'fa': value['used_actions'] if value else 0,
            'fv': value['used_actions'] if value else 0}


def flashback_notice(state):
    data = flashback_data(state)
    return ('syncFlashbackData', {'d': {k: data[k] for k in ('ff', 'fd', 'fa')}})


def flashback_require_action(state):
    value = flashback_context(state)
    if value is not None and value['used_actions'] >= 3:
        raise ValueError('Flashback three-action round exhausted')
    return value is not None


def flashback_spend_action(state, token=None):
    if token is not None and token != flashback_token(state):
        raise ValueError('Reserved flashback round changed')
    if not flashback_require_action(state):
        if token is not None:
            raise ValueError('Reserved flashback context left')
        return []
    state['story']['route35_flashback']['used_actions'] += 1
    return [flashback_notice(state)]


def flashback_accept_entry(state, event, occurrence):
    """Called only by accepted original effect transaction, never raw trace."""
    story = state['story']
    if event == 7752:
        story.setdefault('route35_entry_authorization', {'week': story['week'],
            'occurrence': str(occurrence)})


def flashback_route_handoff(state, event):
    story = state['story']
    authorization = story.get('route35_entry_authorization')
    if event != 7754:
        value = story.get('route35_flashback')
        if value and story.get('route') != '35-3':
            value['active'] = False
        return []
    if (not authorization or authorization.get('week') != story.get('week') or
            7752 not in state.get('completed_events', []) or story.get('date') != 6 or
            state.get('day', {}).get('stock_day') != 6):
        raise ValueError('Actual accepted 7752/date6 required for flashback entry')
    if story.get('route35_flashback'):
        return []
    story['route35_flashback'] = {'version': 1, 'active': True,
        'week': story['week'], 'entry_occurrence': authorization['occurrence'],
        'index': 1, 'used_actions': 0, 'transition_receipts': {}, 'night_intent': None,
        'policy': FLASHBACK_POLICY}
    return [('syncStoryGeneralValue', {'v': 1}), flashback_notice(state), ('enterFlashback', {})]


def prepare_flashback_operation(state, operation, arguments, source_token=None, intent_id=None):
    candidate = copy.deepcopy(state)
    value = flashback_context(candidate)
    if value is None:
        return copy.deepcopy(state), [], False, {'pending': 'inactive_flashback'}
    token = flashback_token(candidate)
    if source_token != token:
        if (operation == 'requestFlashbackIncDay' and not arguments and
                value['used_actions'] == 0 and value.get('night_intent') is None):
            matches = [r for r in value['transition_receipts'].values()
                if r.get('source_token') == source_token and
                r.get('notices') and r['notices'][-1][0] == 'replyFlashbackIncDay' and
                r['notices'][-1][1] == {'d': value['index'], 'v': 0}]
            if len(matches) == 1:
                return copy.deepcopy(state), copy.deepcopy(matches[0]['notices']), False, {'replay': True}
        # A deferred old request cannot bind itself to the new round. The wire
        # has no id: no cached success is published for an ambiguous late RPC.
        return copy.deepcopy(state), [], False, {'pending': 'stale_flashback_receipt'}
    if operation == 'updateEventCondClient':
        if arguments != {'c': 102, 'v': '4'}:
            raise ValueError('Expected actual original NEXTDAY_CLICK')
        if not intent_id:
            raise ValueError('Actual reliable NEXTDAY_CLICK identity required')
        seen = value.setdefault('night_intent_receipts', {})
        if intent_id in seen and seen[intent_id] != token:
            return copy.deepcopy(state), [], False, {'pending': 'consumed_night_intent'}
        already_seen = intent_id in seen
        seen[intent_id] = token
        if value.get('night_intent') == token:
            return candidate, [], not already_seen, {'replay': True}
        value['night_intent'] = token
        facts = dict(candidate.get('conditions', []))
        current = facts.get(102)
        values = list(current) if isinstance(current, (list, tuple)) else ([] if current is None else [current])
        facts[102] = sorted(set(values + [4]))
        candidate['conditions'] = [[k, v] for k, v in sorted(facts.items())]
        return candidate, [], True, {}
    if operation != 'requestFlashbackIncDay' or arguments:
        raise ValueError('Expected original empty flashback RPC')
    if value['index'] == 7:
        return copy.deepcopy(state), [], False, {'pending': 'final_round_requires_actual_600_and_ending'}
    terminal = FLASHBACK_TERMINALS[value['index'] - 1]
    story = candidate['story']
    if (value.get('night_intent') != token or terminal not in candidate.get('completed_events', []) or
            candidate.get('processing_events') or story.get('pending_effects') or
            (candidate.get('battle') or {}).get('active') or
            story.get('patrol_pending') or story.get('patrol_reward_pending') or
            (candidate.get('city_actions') or {}).get('patrol')):
        return copy.deepcopy(state), [], False, {'pending': 'actual_night_terminal_or_gameplay_pending'}
    occurrence = story.get('event_occurrences', {}).get(str(terminal))
    if type(occurrence) is not int or occurrence < 1:
        return copy.deepcopy(state), [], False, {'pending': 'terminal_occurrence_missing'}
    receipt = '%s:%s:%s' % (token, terminal, occurrence)
    if receipt in value['transition_receipts']:
        return copy.deepcopy(state), [], False, {'replay': True}
    value['index'] += 1
    value['used_actions'] = 0
    value['night_intent'] = None
    facts = dict(candidate.get('conditions', []))
    current = facts.get(102)
    remaining = [v for v in (current if isinstance(current, (list, tuple)) else [current]) if v != 4]
    if remaining:
        facts[102] = remaining
    else:
        facts.pop(102, None)
    candidate['conditions'] = [[k, v] for k, v in sorted(facts.items())]
    notices = [('syncStoryGeneralValue', {'v': value['index']}), flashback_notice(candidate),
               ('replyFlashbackIncDay', {'d': value['index'], 'v': 0})]
    value['transition_receipts'][receipt] = {'source_token': token, 'notices': copy.deepcopy(notices)}
    return candidate, notices, True, {'policy': FLASHBACK_POLICY}
