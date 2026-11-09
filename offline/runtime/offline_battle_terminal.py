# -*- coding: ascii -*-
"""Durable actual EVENT winning-party terminal recovery, explicit offline policy.

All helpers mutate only caller-owned transaction candidates. No native objects,
UI lineup, inferred roster, or bounded receipt ring is a source of new proof.
"""
import copy

WINNING_PARTY_FATIGUE_POLICY = 'offline-winning-party-fatigue-recovery-v1'
_OBT_EVENT_POLICY = 'original-event-pve-occurrence-v1'
try:
    _obt_text = (basestring,)
except NameError:
    _obt_text = (str,)


def _obt_occurrence(value, week, event):
    if not isinstance(value, _obt_text):
        return False
    parts = value.split(':')
    return (len(parts) == 3 and parts[0] == str(week) and parts[1] == str(event)
            and parts[2].isdigit() and int(parts[2]) > 0)


def _obt_validate_proof(proof, state, terminal=None, occurrence=None):
    if not isinstance(proof, dict):
        raise ValueError('missing-winning-party-provenance')
    if proof.get('party_kind','owned') != 'owned':
        raise ValueError('trial-party-ineligible-for-owned-fatigue')
    party = proof.get('party')
    fingerprint = proof.get('result_fingerprint')
    if (proof.get('version') != 1 or type(proof.get('version')) is not int or
            proof.get('policy') != WINNING_PARTY_FATIGUE_POLICY or
            proof.get('battle_policy') != _OBT_EVENT_POLICY or
            proof.get('terminal_kind') != 'successEvent' or
            type(proof.get('outcome')) is not int or proof['outcome'] != 1 or
            any(type(proof.get(k)) is not int or proof[k] < (0 if k == 'week' else 1)
                for k in ('week', 'source_event', 'scene', 'terminal_event')) or
            not isinstance(proof.get('fight_id'), _obt_text) or not proof['fight_id'] or
            not isinstance(fingerprint, _obt_text) or len(fingerprint) != 64 or
            any(c not in '0123456789abcdef' for c in fingerprint) or
            not isinstance(party, list) or not party or
            any(type(h) is not int or h <= 0 for h in party) or len(set(party)) != len(party) or
            not _obt_occurrence(proof.get('source_event_occurrence'), proof['week'], proof['source_event'])):
        raise ValueError('invalid-winning-party-provenance')
    if ('source_day' in proof and (type(proof['source_day']) is not int or proof['source_day'] < 0) or
            'source_route' in proof and (not isinstance(proof['source_route'], _obt_text) or not proof['source_route'])):
        raise ValueError('invalid-winning-party-source-audit')
    story = state.get('story', {})
    if proof['week'] != story.get('week', 0) or terminal is not None and terminal != proof['terminal_event']:
        raise ValueError('stale-or-wrong-winning-party-terminal')
    key = proof['source_event_occurrence']
    gate = story.get('event_battle_gates', {}).get(key, {})
    won = story.get('event_battle_wins', {}).get(key, {})
    if (not isinstance(gate, dict) or not isinstance(won, dict) or
            gate.get('status') != 'won' or gate.get('event') != proof['source_event'] or
            gate.get('occurrence') != key or gate.get('scene') != proof['scene'] or
            gate.get('fight_id') != proof['fight_id'] or
            any(won.get(k) != v for k, v in (('event', proof['source_event']),
                ('occurrence', key), ('scene', proof['scene']), ('fight_id', proof['fight_id'])))):
        raise ValueError('missing-winning-party-source-gate')
    receipts = [r for r in state.get('battle', {}).get('receipts', []) if r.get('fight_id') == proof['fight_id']]
    if receipts:
        accepted = receipts[0]
        reply = accepted.get('reply', {})
        if (accepted.get('party_kind','owned') != 'owned' or len(receipts) != 1 or accepted.get('fingerprint') != proof['result_fingerprint'] or
                accepted.get('event_policy') != _OBT_EVENT_POLICY or accepted.get('event_occurrence') != key or
                reply.get('t') != 2 or reply.get('s') != proof['scene'] or reply.get('w') != 1 or
                reply.get('h') != proof['party']):
            raise ValueError('inconsistent-winning-party-accepted-receipt')
    if won.get('party_kind','owned') != 'owned' or won.get('winning_terminal_provenance',{}).get('party_kind','owned') != 'owned':
        raise ValueError('trial-party-ineligible-for-owned-fatigue')
    retained = won.get('winning_terminal_provenance')
    if retained is not None and (not isinstance(retained, dict) or
            any(retained.get(k) != proof[k] for k in ('week', 'party', 'result_fingerprint'))):
        raise ValueError('inconsistent-winning-party-source-proof')
    if occurrence is not None and (proof.get('terminal_occurrence') != occurrence or
            not _obt_occurrence(occurrence, proof['week'], proof['terminal_event'])):
        raise ValueError('wrong-winning-party-terminal-occurrence')
    if 'terminal_occurrence' in proof and not _obt_occurrence(proof['terminal_occurrence'], proof['week'], proof['terminal_event']):
        raise ValueError('invalid-winning-party-terminal-occurrence')


def _obt_original_mapping(proof, missions, events):
    mission = missions.get(proof['scene'], {})
    source = events.get(proof['source_event'], {})
    terminal = events.get(proof['terminal_event'], {})
    if (not mission.get('release') or mission.get('system_type') != 2 or
            not source.get('release') or source.get('enterBattle') != proof['scene'] or
            not terminal.get('release') or proof['terminal_event'] not in mission.get('successEvent', ())):
        raise ValueError('original-winning-terminal-mapping-required')


def mint_event_terminal_offers(state, missions, events, active, receipt):
    """Mint full request.h proof inside accepted result before active is cleared."""
    if active.get('party_kind','owned') != 'owned':
        return
    if active.get('event_policy') != _OBT_EVENT_POLICY or receipt.get('reply', {}).get('w') != 1:
        return
    story = state['story']
    available = dict(state.get('available_events', []))
    for event in missions.get(active['request']['s'], {}).get('successEvent', ()):
        row = events.get(event, {})
        if (not row.get('release') or event in state.get('processing_events', []) or
                event in state.get('completed_events', []) and not row.get('repeatable')):
            continue
        offers = story.setdefault('event_terminal_offers', {})
        # The first pending winning offer owns its party. A second real win
        # remains accepted without silently replacing the terminal claimant.
        if str(event) in offers:
            continue
        origin = story.get('available_origins', {}).get(str(event))
        if event in available and origin and origin.get('source') == 'accepted_mission_result':
            continue
        proof = {'version': 1, 'policy': WINNING_PARTY_FATIGUE_POLICY,
            'battle_policy': _OBT_EVENT_POLICY, 'fight_id': active['fight_id'],
            'result_fingerprint': receipt['fingerprint'], 'week': story.get('week', 0),
            'source_event': active['event_id'], 'source_event_occurrence': active['event_occurrence'],
            'scene': active['request']['s'], 'outcome': 1,
            'party': copy.deepcopy(active['request']['h']), 'terminal_event': event,
            'terminal_kind': 'successEvent', 'source_day': story.get('date', 0),
            'source_route': story.get('route', '1')}
        _obt_validate_proof(proof, state, event)
        _obt_original_mapping(proof, missions, events)
        offers[str(event)] = proof
        available[event] = 1
        story.setdefault('available_origins', {})[str(event)] = {
            'source': 'accepted_mission_result', 'fight_id': proof['fight_id'],
            'scene': proof['scene'], 'outcome': 1, 'week': proof['week'],
            'source_event': proof['source_event'], 'source_event_occurrence': proof['source_event_occurrence'],
            'result_fingerprint': proof['result_fingerprint']}
    state['available_events'] = [[event, value] for event, value in sorted(available.items())]


def bind_event_terminal_context(state, event, occurrence):
    """Pin a new terminal occurrence; dream event_contexts remain independent."""
    story = state['story']
    contexts = story.get('event_terminal_contexts', {})
    if occurrence in contexts:
        _obt_validate_proof(contexts[occurrence], state, event, occurrence)
        return
    offer = story.get('event_terminal_offers', {}).get(str(event))
    if offer is None:
        return
    _obt_validate_proof(offer, state, event)
    context = copy.deepcopy(offer)
    context['terminal_occurrence'] = occurrence
    _obt_validate_proof(context, state, event, occurrence)
    story.setdefault('event_terminal_contexts', {})[occurrence] = context
    story['event_terminal_offers'].pop(str(event), None)


def _obt_backfill(state, events, missions, event, occurrence):
    story = state['story']
    origin = story.get('available_origins', {}).get(str(event), {})
    if (origin.get('source') != 'accepted_mission_result' or
            type(origin.get('outcome')) is not int or origin.get('outcome') != 1):
        raise ValueError('missing-winning-party-provenance')
    matches = [r for r in state.get('battle', {}).get('receipts', [])
        if r.get('fight_id') == origin.get('fight_id') and r.get('event_policy') == _OBT_EVENT_POLICY
        and r.get('reply', {}).get('w') == 1 and r.get('reply', {}).get('t') == 2
        and r.get('reply', {}).get('s') == origin.get('scene')]
    if len(matches) != 1:
        raise ValueError('missing-winning-party-provenance:retained-receipt-required')
    receipt = matches[0]
    if receipt.get('party_kind','owned') != 'owned' or origin.get('party_kind','owned') != 'owned':
        raise ValueError('trial-party-ineligible-for-owned-fatigue')
    key = receipt.get('event_occurrence')
    gate = story.get('event_battle_gates', {}).get(key, {})
    proof = {'version': 1, 'policy': WINNING_PARTY_FATIGUE_POLICY,
        'battle_policy': _OBT_EVENT_POLICY, 'fight_id': receipt['fight_id'],
        'result_fingerprint': receipt.get('fingerprint'), 'week': story.get('week', 0),
        'source_event': gate.get('event'), 'source_event_occurrence': key,
        'scene': origin.get('scene'), 'outcome': 1, 'party': copy.deepcopy(receipt['reply'].get('h')),
        'terminal_event': event, 'terminal_kind': 'successEvent', 'terminal_occurrence': occurrence}
    _obt_validate_proof(proof, state, event, occurrence)
    _obt_original_mapping(proof, missions, events)
    for field in ('week', 'source_event', 'source_event_occurrence', 'result_fingerprint'):
        if field in origin and origin[field] != proof[field]:
            raise ValueError('ambiguous-winning-party-legacy-origin')
    story.setdefault('event_terminal_contexts', {})[occurrence] = proof
    return proof


def resolve_winning_party_fatigue(state, events, tables, event, occurrence, reward, amount):
    """Apply validated nonnegative recovery; return immutable before/after audit."""
    if type(amount) is not int or amount < 0:
        raise ValueError('unsupported-negative-or-invalid-selector0-fatigue')
    story = state['story']
    context = story.get('event_terminal_contexts', {}).get(occurrence)
    if context is None:
        context = _obt_backfill(state, events, tables.get('mission', {}), event, occurrence)
    _obt_validate_proof(context, state, event, occurrence)
    _obt_original_mapping(context, tables.get('mission', {}), events)
    current = '%s:%s:%s' % (story.get('week', 0), event, story.get('event_occurrences', {}).get(str(event), 0))
    if current != occurrence or event not in state.get('processing_events', []):
        raise ValueError('actual-processing-winning-terminal-required')
    changes = []
    for hid in context['party']:
        hero = (state.get('profile') or {}).get('heroes', {}).get(str(hid))
        maximum = tables.get('hero', {}).get(hid, {}).get('fatigueValue')
        if hero is None:
            raise ValueError('Missing owned original winning party hero %s' % hid)
        before = hero.get('cf')
        if (type(maximum) is not int or maximum < 1 or type(before) is not int or before < 0 or before > maximum):
            raise ValueError('invalid-winning-party-current-fatigue:%s' % hid)
        changes.append({'hero': hid, 'before': before, 'after': min(maximum, before + amount), 'maximum': maximum})
    for change in changes:
        state['profile']['heroes'][str(change['hero'])]['cf'] = change['after']
    audit = {'version': 1, 'policy': WINNING_PARTY_FATIGUE_POLICY,
        'reward': reward, 'amount': amount, 'terminal_event': event, 'terminal_occurrence': occurrence,
        'fight_id': context['fight_id'], 'result_fingerprint': context['result_fingerprint'],
        'source_event': context['source_event'], 'source_event_occurrence': context['source_event_occurrence'],
        'week': context['week'], 'scene': context['scene'], 'party': list(context['party']), 'changes': changes}
    story.setdefault('event_terminal_effect_audit', {}).setdefault(occurrence, []).append(copy.deepcopy(audit))
    notices = [('updateCurFatigueValue', {'h': change['hero'], 'v': change['after']}) for change in changes]
    return audit, notices


def validate_event_terminal_state(state):
    """Absent fields are valid legacy saves; present fields have strict shapes."""
    story = state.get('story', {})
    for field in ('event_terminal_offers', 'event_terminal_contexts', 'event_terminal_effect_audit'):
        if field in story and not isinstance(story[field], dict):
            raise ValueError('Invalid winning terminal map: ' + field)
    for key, proof in story.get('event_terminal_offers', {}).items():
        if not isinstance(proof, dict) or not isinstance(key, _obt_text) or key != str(proof.get('terminal_event')) or 'terminal_occurrence' in proof:
            raise ValueError('Invalid winning terminal offer key')
        _obt_validate_proof(proof, state, proof['terminal_event'])
    for key, proof in story.get('event_terminal_contexts', {}).items():
        if not isinstance(proof, dict):
            raise ValueError('Invalid winning terminal context')
        _obt_validate_proof(proof, state, proof.get('terminal_event'), key)
    for key, audits in story.get('event_terminal_effect_audit', {}).items():
        context = story.get('event_terminal_contexts', {}).get(key)
        if not context or not isinstance(audits, list) or not audits or story.get('event_effect_receipts', {}).get(key) != context['terminal_event']:
            raise ValueError('Invalid winning terminal effect audit linkage')
        for audit in audits:
            if (not isinstance(audit, dict) or audit.get('version') != 1 or
                    audit.get('policy') != WINNING_PARTY_FATIGUE_POLICY or
                    any(audit.get(k) != context.get(k) for k in ('terminal_event', 'terminal_occurrence',
                        'fight_id', 'result_fingerprint', 'source_event', 'source_event_occurrence', 'week', 'scene', 'party')) or
                    type(audit.get('reward')) is not int or audit['reward'] <= 0 or
                    type(audit.get('amount')) is not int or audit['amount'] < 0 or
                    not isinstance(audit.get('changes'), list) or len(audit['changes']) != len(context['party'])):
                raise ValueError('Invalid winning terminal effect audit')
            for hid, change in zip(context['party'], audit['changes']):
                if (not isinstance(change, dict) or change.get('hero') != hid or
                        any(type(change.get(k)) is not int for k in ('before', 'after', 'maximum')) or
                        change['maximum'] < 1 or not 0 <= change['before'] <= change['maximum'] or
                        change['after'] != min(change['maximum'], change['before'] + audit['amount'])):
                    raise ValueError('Invalid winning terminal fatigue audit')
