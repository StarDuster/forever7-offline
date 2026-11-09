# -*- coding: ascii -*-
"""Original-table dispatch provenance and explicit offline route13 policy.

One original pair earns one side once per week. No display, patrol, intro RPC,
synthetic dialogue, roster guess or historical terminal ID grants an award.
"""
import copy
import hashlib
import json
try:
    from offline_conditions import evaluate_offline_condition, parse_original_condition_literal
except ImportError:
    pass
try:
    _dw_text = (basestring,)
except NameError:
    _dw_text = (str,)

DAERWEILA_POLICY = 'offline-original-route13-dispatch-v1'
_DW_SIDES = ('human', 'devil')


def _dw_int(value):
    return type(value) is int and value > 0


def _dw_release(value):
    return type(value) in (int, bool) and value == 1


def _dw_fields(row, names):
    """Original taggeddict boundary: copy finite supported fields only."""
    items = getattr(row, 'items', None)
    if not callable(items):
        raise ValueError('Original dispatch row requires a read-only mapping')
    result = {}
    for pair in items():
        if not isinstance(pair, (list, tuple)) or len(pair) != 2:
            raise ValueError('Invalid original dispatch mapping entry')
        key, value = pair
        if isinstance(key, _dw_text) and key in names:
            if key in result:
                raise ValueError('Duplicate original dispatch field')
            result[key] = value
    return result


def _dw_ids(values):
    if not isinstance(values, (list, tuple)) or any(not _dw_int(v) for v in values) or len(set(values)) != len(values):
        raise ValueError('Original dispatch requires unique positive integer IDs')
    return list(values)


def _dw_hash(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=True, allow_nan=False).encode('ascii')).hexdigest()


def _dw_conditions(trigger):
    row = _dw_fields(trigger, ('release', 'conds'))
    if not _dw_release(row.get('release')) or not callable(getattr(row.get('conds'), 'items', None)):
        raise ValueError('Original released dispatch trigger required')
    conditions = {}
    for key, value in row['conds'].items():
        if type(key) is not int or not isinstance(value, _dw_text) or str(key) in conditions:
            raise ValueError('Original dispatch condition must be a literal text field')
        conditions[str(key)] = value
    return conditions


def compile_daerweila_dispatch(rows, events, triggers):
    """Compile original rows and exact successor edges, not an event whitelist."""
    if not callable(getattr(rows, 'items', None)):
        raise ValueError('Original daerweila_dispatch table required')
    pairs, nodes, conditions, used = {}, {}, {}, set()
    for key, original in rows.items():
        row = _dw_fields(original, ('human_event_id', 'devil_event_id', 'show_event_id', 'add_human_events', 'add_devil_events'))
        human, devil, show = row.get('human_event_id'), row.get('devil_event_id'), row.get('show_event_id')
        if (not isinstance(key, tuple) or len(key) != 2 or any(not _dw_int(v) for v in key) or
                key != (human, devil) or any(not _dw_int(v) for v in (human, devil, show)) or
                len(set((human, devil, show))) != 3 or any(v in used for v in (human, devil, show))):
            raise ValueError('Ambiguous original dispatch pair key')
        used.update((human, devil, show))
        terminal = {side: _dw_ids(row.get('add_' + side + '_events')) for side in _DW_SIDES}
        if any(not terminal[side] for side in _DW_SIDES):
            raise ValueError('Original dispatch terminal list is empty')
        for event in (show, human, devil):
            current = _dw_fields(events.get(event, {}), ('release',))
            if not _dw_release(current.get('release')):
                raise ValueError('Original dispatch show/root is unreleased')
            conditions[str(event)] = _dw_conditions(triggers.get(event, {}))
        routes = parse_original_condition_literal(conditions[str(show)].get('52', 'set()'))
        if not isinstance(routes, (set, list, tuple)) or not routes or any(not isinstance(r, _dw_text) or not r for r in routes):
            raise ValueError('Original dispatch route condition required')
        routes = sorted(set(routes))
        for event in (human, devil):
            branch_routes = parse_original_condition_literal(conditions[str(event)].get('52', 'set()'))
            if not isinstance(branch_routes, (list, tuple, set)) or set(branch_routes) != set(routes):
                raise ValueError('Original dispatch branch route conditions disagree')
        for side, root in (('human', human), ('devil', devil)):
            visiting, visited = set(), set()
            def visit(event):
                if event in visiting or len(visited) > 512:
                    raise ValueError('Cyclic or excessive original dispatch lineage')
                if event in visited:
                    return
                if str(event) in nodes:
                    raise ValueError('Original dispatch sides/pairs share an ambiguous event')
                current = _dw_fields(events.get(event, {}), ('release', 'events'))
                if not _dw_release(current.get('release')):
                    raise ValueError('Original dispatch lineage requires released events')
                children = _dw_ids(current.get('events', ()))
                visiting.add(event)
                # Register after traversing so same-side converging edges work.
                for child in children:
                    visit(child)
                visiting.remove(event)
                visited.add(event)
                nodes[str(event)] = {'pair': show, 'side': side, 'children': children}
            visit(root)
            if not set(terminal[side]).issubset(visited):
                raise ValueError('Original dispatch terminal is not reachable from its side')
        pairs[str(show)] = {'show': show, 'human': human, 'devil': devil, 'terminals': terminal, 'routes': routes}
    if set(pairs).intersection(nodes):
        raise ValueError('Original dispatch show cannot be a branch descendant')
    if not pairs or len(pairs) > 5:
        raise ValueError('Original dispatch table must fit the original five-slot consumer')
    result = {'pairs': pairs, 'nodes': nodes, 'conditions': conditions}
    result['token'] = _dw_hash(result)
    return result


def _dw_catalog(state, tables=None, events=None, triggers=None):
    tables = tables or {}
    doc = state.get('story', {}).get('daerweila_dispatch')
    if 'daerweila_dispatch' in tables:
        current = compile_daerweila_dispatch(tables['daerweila_dispatch'], events or tables.get('event_content', {}), triggers or tables.get('event_condition', {}))
        if doc and current != doc['catalog']:
            raise ValueError('Original dispatch catalog changed; source requires review')
        return current
    return doc['catalog'] if doc else None


def _dw_day(state):
    return state.get('day', {}).get('stock_day', state.get('story', {}).get('date'))


def _dw_locked(story, side):
    value = story.get('daerweila_' + side + '_lock', False)
    if type(value) is not bool:
        raise ValueError('Invalid canonical dispatch lock')
    return value


def _dw_baseline(state, std=None):
    story, std = state.get('story', {}), std or {}
    fresh = (state.get('week_protocol', {}).get('transition') or {}).get('target_week') == story.get('week')
    result = {}
    for side, wire in (('human', 'dwhv'), ('devil', 'dwdv')):
        value = story.get('daerweila_' + side, 0 if fresh else std.get(wire, 0))
        if type(value) is not int or not 0 <= value <= 5:
            raise ValueError('Invalid legacy dispatch count; no invented clamp')
        result[side] = value
    flag = story.get('daerweila_choose_asazile', False if fresh else std.get('dwca', False))
    if type(flag) is not bool or sum(result.values()) > 5:
        raise ValueError('Invalid legacy dispatch baseline')
    result['choose'] = flag
    return result


def _dw_ensure(state, catalog, std=None):
    story = state['story']
    if 'daerweila_dispatch' not in story:
        baseline = _dw_baseline(state, std)
        old_terminals = sorted(event for event in state.get('completed_events', []) if any(event in pair['terminals'][side] for pair in catalog['pairs'].values() for side in _DW_SIDES))
        pending = bool(baseline['human'] or baseline['devil'] or baseline['choose'] or old_terminals)
        story['daerweila_dispatch'] = {'version': 1, 'policy': DAERWEILA_POLICY,
            'week': story.get('week', 0), 'generation': 0, 'catalog': copy.deepcopy(catalog),
            'baseline': baseline, 'legacy_terminals': old_terminals, 'status': 'legacy-pending' if pending else 'active',
            'offers': {}, 'choices': {}, 'occurrences': {}, 'awards': {},
            'first_devil': {'phase': 'unseen', 'offer': None}, 'first_history': []}
    return story['daerweila_dispatch']


def _dw_counts(doc):
    return {side: doc['baseline'][side] + sum(award['side'] == side for award in doc['awards'].values()) for side in _DW_SIDES}


def _dw_require_active(state, doc):
    if doc['week'] != state['story'].get('week', 0) or doc['status'] != 'active':
        raise ValueError('legacy-or-stale-daerweila-provenance-pending')


def _dw_trigger(state, catalog, event):
    return all(evaluate_offline_condition(int(kind), value, state) is True for kind, value in catalog['conditions'][str(event)].items())


def daerweila_request_source(state):
    story = state.get('story', {})
    doc = story.get('daerweila_dispatch') or {}
    patrol = (state.get('city_actions') or {}).get('patrol') or {}
    return {'week': story.get('week', 0), 'day': _dw_day(state), 'route': story.get('route'),
        'generation': doc.get('generation', 0), 'patrol': patrol.get('admission_id'),
        'occurrences': copy.deepcopy(story.get('event_occurrences', {})),
        'choices': {key: value['choice'] for key, value in doc.get('occurrences', {}).items()}}


def daerweila_source_matches(state, source, event=None):
    if not isinstance(source, dict):
        return False
    current = daerweila_request_source(state)
    if any(source.get(k) != current.get(k) for k in ('week', 'day', 'route', 'generation', 'patrol')):
        return False
    return event is None or source.get('occurrences', {}).get(str(event), 0) == current['occurrences'].get(str(event), 0)


def prepare_daerweila_patrol_baseline(state, catalogs):
    if 'daerweila_dispatch' not in catalogs:
        return False
    tables = dict(catalogs, event_content=catalogs.get('content', {}), event_condition=catalogs.get('triggers', {}))
    catalog = _dw_catalog(state, tables)
    if state['story'].get('route') not in set(r for pair in catalog['pairs'].values() for r in pair['routes']):
        return False
    doc = _dw_ensure(state, catalog, catalogs.get('dispatch_baseline'))
    return doc['status'] != 'active'


def _dw_cancel_pending(doc, reason):
    if doc['first_devil']['phase'] == 'intro_pending':
        doc['first_history'].append(dict(doc['first_devil'], reason=reason))
        doc['first_devil'] = {'phase': 'unseen', 'offer': None}


def _dw_expire_sources(state, doc):
    patrol = (state.get('city_actions') or {}).get('patrol') or {}
    for offer in doc['offers'].values():
        if offer['status'] == 'offered' and (offer['patrol_id'] != patrol.get('admission_id') or
                offer['week'] != state['story'].get('week') or offer['day'] != _dw_day(state) or
                offer['route'] != state['story'].get('route')):
            offer['status'] = 'expired'
    first = doc['first_devil']
    if first['phase'] == 'intro_pending' and doc['offers'][first['offer']]['status'] != 'offered':
        _dw_cancel_pending(doc, 'source-expired')


def filter_daerweila_availability(state):
    doc = state.get('story', {}).get('daerweila_dispatch')
    if not doc:
        return
    refresh_daerweila_patrol(state)
    patrol = (state.get('city_actions') or {}).get('patrol') or {}
    allowed = set()
    for offer in doc['offers'].values():
        if (offer['status'] == 'offered' and offer['patrol_id'] == patrol.get('admission_id') and
                offer['week'] == state['story'].get('week') and offer['day'] == _dw_day(state) and
                offer['route'] == state['story'].get('route') and doc['status'] == 'active'):
            allowed.update(patrol.get('events', []))
    roots = set(event for pair in doc['catalog']['pairs'].values() for event in (pair['show'], pair['human'], pair['devil']))
    state['available_events'] = [pair for pair in state.get('available_events', []) if pair[0] not in roots or pair[0] in allowed]


def prepare_daerweila_patrol_delivery(state, catalogs, notices):
    tables = dict(catalogs, event_content=catalogs.get('content', {}), event_condition=catalogs.get('triggers', {}))
    catalog = _dw_catalog(state, tables)
    if not catalog:
        return notices
    roots = set(e for pair in catalog['pairs'].values() for e in (pair['show'], pair['human'], pair['devil']))
    relevant = any(name == 'enter_patrol_reply' and roots.intersection(body.get('ev', [])) for name, body in notices)
    if not relevant:
        return notices
    doc = state['story'].get('daerweila_dispatch')
    patrol = (state.get('city_actions') or {}).get('patrol')
    if doc:
        _dw_expire_sources(state, doc)
    if not doc or not patrol or patrol.get('selected') is not None or not any(o['status'] == 'offered' and o['patrol_id'] == patrol.get('admission_id') for o in doc['offers'].values()):
        raise ValueError('missing-current-paid-dispatch-offer; legacy or stale patrol cannot replay choice')
    _dw_require_active(state, doc)
    filter_daerweila_availability(state)
    result = []
    for name, body in notices:
        if name == 'enter_patrol_reply':
            body = dict(body, ev=list(patrol['events']))
        result.append((name, body))
    return result


def mint_daerweila_patrol_offers(state, catalogs, receipt):
    tables = dict(catalogs, event_content=catalogs.get('content', {}), event_condition=catalogs.get('triggers', {}))
    catalog = _dw_catalog(state, tables)
    if not catalog:
        return
    patrol = state.get('city_actions', {}).get('patrol')
    if not patrol or patrol.get('admission_id') != receipt['id']:
        raise ValueError('Actual paid patrol receipt required for dispatch')
    relevant = [pair for pair in catalog['pairs'].values() if pair['show'] in patrol['events']]
    if not relevant:
        return
    doc = _dw_ensure(state, catalog, catalogs.get('dispatch_baseline'))
    _dw_require_active(state, doc)
    _dw_expire_sources(state, doc)
    if receipt.get('fingerprint') is None or not any(r == receipt for r in state['city_actions']['receipts']):
        raise ValueError('Accepted actual patrol receipt required for dispatch')
    doc['generation'] += 1
    for pair in relevant:
        full = [pair['show'], pair['human'], pair['devil']]
        if (not set(full).issubset(set(patrol['events'])) or state['story'].get('route') not in pair['routes'] or
                not all(_dw_trigger(state, catalog, event) for event in full)):
            raise ValueError('Original dispatch show and both branches require actual patrol conditions')
        source = {'patrol_id': receipt['id'], 'patrol_fingerprint': receipt['fingerprint'],
            'week': doc['week'], 'day': _dw_day(state), 'route': state['story']['route'],
            'generation': doc['generation'], 'area': patrol['area'], 'heroes': list(patrol['heroes']),
            'pair': pair['show'], 'catalog_token': catalog['token'], 'verified_events': full}
        identity = _dw_hash(source)
        doc['offers'][identity] = dict(source, id=identity, status='offered', root=None)
    refresh_daerweila_patrol(state)


def refresh_daerweila_patrol(state):
    doc = state.get('story', {}).get('daerweila_dispatch')
    patrol = state.get('city_actions', {}).get('patrol')
    if not doc or not patrol:
        return
    available = dict(state.get('available_events', []))
    for offer in doc['offers'].values():
        if offer['patrol_id'] != patrol.get('admission_id') or offer['status'] != 'offered':
            continue
        pair = doc['catalog']['pairs'][str(offer['pair'])]
        valid = (offer['week'] == state['story'].get('week') and offer['day'] == _dw_day(state) and
            offer['route'] == state['story'].get('route') and str(offer['pair']) not in doc['awards'])
        allowed = [pair[side] for side in _DW_SIDES if valid and not _dw_locked(state['story'], side)]
        keep = allowed + ([pair['show']] if allowed else [])
        for event in (pair['show'], pair['human'], pair['devil']):
            if event not in keep:
                available.pop(event, None)
                patrol['events'] = [e for e in patrol['events'] if e != event]
    state['available_events'] = [[key, value] for key, value in sorted(available.items())]


def _dw_offer(state, doc, pair, side):
    _dw_require_active(state, doc)
    patrol = (state.get('city_actions') or {}).get('patrol') or {}
    matches = [o for o in doc['offers'].values() if o['patrol_id'] == patrol.get('admission_id') and o['pair'] == pair['show'] and o['status'] == 'offered']
    if len(matches) != 1:
        raise ValueError('missing-or-ambiguous-paid-dispatch-offer')
    offer = matches[0]
    if (offer['week'] != state['story'].get('week') or offer['day'] != _dw_day(state) or offer['route'] != state['story'].get('route') or
            offer['area'] != patrol.get('area') or offer['heroes'] != patrol.get('heroes') or
            patrol.get('week') != offer['week'] or patrol.get('day') != offer['day'] or
            any(str(hero) not in state.get('profile', {}).get('heroes', {}) for hero in offer['heroes']) or
            patrol.get('selected') not in (None, pair[side]) or _dw_locked(state['story'], side) or
            str(pair['show']) in doc['awards'] or any(c['pair'] == pair['show'] and c['status'] != 'expired' for c in doc['choices'].values()) or
            not set((pair['show'], pair[side])).issubset(set(patrol.get('events', []))) or
            not set((pair['show'], pair[side])).issubset(set(dict(state.get('available_events', [])))) or
            not all(_dw_trigger(state, doc['catalog'], event) for event in (pair['show'], pair[side]))):
        raise ValueError('Original dispatch source, availability, locks or conditions changed')
    retained = [r for r in state.get('city_actions', {}).get('receipts', []) if r.get('id') == offer['patrol_id']]
    if retained and (len(retained) != 1 or retained[0].get('fingerprint') != offer['patrol_fingerprint']):
        raise ValueError('Dispatch accepted patrol receipt mismatch')
    return offer


def prepare_daerweila_first_choice(state, arguments, tables, source):
    candidate = copy.deepcopy(state)
    if arguments or not daerweila_source_matches(candidate, source):
        raise ValueError('Original empty first-choice request requires captured current source')
    catalog = _dw_catalog(candidate, tables)
    doc = candidate['story'].get('daerweila_dispatch')
    if not catalog or not doc:
        raise ValueError('Actual dispatch patrol required before first devil intro')
    _dw_require_active(candidate, doc)
    _dw_expire_sources(candidate, doc)
    if doc['first_devil']['phase'] == 'continued':
        return candidate, False
    offers = []
    for pair in catalog['pairs'].values():
        try:
            offer = _dw_offer(candidate, doc, pair, 'devil')
            offers.append(offer)
        except ValueError:
            pass
    if len(offers) != 1:
        raise ValueError('First devil intro requires one unambiguous current dispatch pair')
    first = {'phase': 'intro_pending', 'offer': offers[0]['id']}
    if doc['first_devil'] == first:
        return candidate, False
    if doc['first_devil']['phase'] == 'intro_pending':
        old = doc['offers'].get(doc['first_devil']['offer'], {})
        if old.get('status') != 'expired':
            raise ValueError('Another first devil intro remains pending')
        doc['first_history'].append(copy.deepcopy(doc['first_devil']))
    doc['first_devil'] = first
    return candidate, True


def bind_daerweila_occurrence(state, event, occurrence, events, triggers, parent=None, tables=None):
    catalog = _dw_catalog(state, tables, events, triggers)
    if not catalog:
        return
    if str(event) in catalog['pairs']:
        raise ValueError('Dispatch show event is presentation only; choose an original branch')
    node = catalog['nodes'].get(str(event))
    if node is None:
        return
    doc = state['story'].get('daerweila_dispatch')
    if not doc:
        raise ValueError('missing-daerweila-choice-provenance')
    _dw_require_active(state, doc)
    pair = catalog['pairs'][str(node['pair'])]
    if parent is not None:
        previous = doc['occurrences'].get(parent)
        if not previous or previous['choice'] not in doc['choices']:
            raise ValueError('Actual dispatch parent occurrence required')
        choice = doc['choices'][previous['choice']]
        if (choice['status'] != 'active' or choice['pair'] != node['pair'] or choice['side'] != node['side'] or
                state['story'].get('event_effect_receipts', {}).get(parent) != previous['event'] or
                previous['event'] not in state.get('completed_events', []) or
                event not in events.get(previous['event'], {}).get('events', ()) or
                event not in catalog['nodes'][str(previous['event'])]['children']):
            raise ValueError('Original completed dispatch parent edge required')
        _dw_live_choice(state, choice)
        root = previous['choice']
    else:
        if event != pair[node['side']]:
            raise ValueError('Dispatch descendants require actual original parent lineage')
        _dw_expire_sources(state, doc)
        offer = _dw_offer(state, doc, pair, node['side'])
        if node['side'] == 'human' and doc['first_devil'].get('offer') == offer['id']:
            _dw_cancel_pending(doc, 'actual-human-branch-selected')
        if node['side'] == 'devil' and doc['first_devil']['phase'] != 'continued':
            if doc['first_devil'] != {'phase': 'intro_pending', 'offer': offer['id']}:
                raise ValueError('Actual first devil intro request must precede its continuation start')
            doc['first_devil'] = {'phase': 'continued', 'offer': offer['id']}
            state['story']['daerweila_choose_asazile'] = True
        root = occurrence
        choice = {'root': root, 'root_event': event, 'pair': node['pair'], 'side': node['side'],
            'offer': offer['id'], 'source': copy.deepcopy(offer), 'status': 'active'}
        doc['choices'][root] = choice
        offer['status'], offer['root'] = 'chosen', root
        available = dict(state['available_events'])
        for other in (pair['show'], pair['human'], pair['devil']):
            if other != event:
                available.pop(other, None)
        state['available_events'] = [[k, v] for k, v in sorted(available.items())]
    if occurrence in doc['occurrences']:
        raise ValueError('Dispatch occurrence already belongs to an immutable choice')
    doc['occurrences'][occurrence] = {'choice': root, 'parent': parent, 'event': event}


def _dw_live_choice(state, choice):
    source = choice['source']
    if (source['week'] != state['story'].get('week') or source['day'] != _dw_day(state) or
            source['route'] != state['story'].get('route') or choice['status'] != 'active'):
        raise ValueError('stale-daerweila-choice-occurrence')


def daerweila_occurrence_matches(state, event, source):
    doc = state.get('story', {}).get('daerweila_dispatch')
    key = '%s:%s:%s' % (state['story'].get('week', 0), event, state['story'].get('event_occurrences', {}).get(str(event), 0))
    if not doc or key not in doc['occurrences']:
        return True
    if not isinstance(source, dict):
        return False
    current = daerweila_request_source(state)
    context = doc['occurrences'][key]
    return (all(source.get(k) == current[k] for k in ('week', 'day', 'route')) and
        source.get('occurrences', {}).get(str(event), 0) == current['occurrences'].get(str(event), 0) and
        source.get('choices', {}).get(key) == context['choice'])


def daerweila_queued_operation_matches(state, operation, arguments, source, tables):
    catalog = _dw_catalog(state, tables)
    if not catalog:
        return True
    event = arguments.get('e')
    if operation == 'startEvent':
        if str(event) not in catalog['nodes'] and str(event) not in catalog['pairs']:
            return True
        if event in state.get('processing_events', []):
            if daerweila_occurrence_matches(state, event, source):
                return True
            doc = state['story'].get('daerweila_dispatch') or {}
            count = state['story'].get('event_occurrences', {}).get(str(event), 0)
            key = '%s:%s:%s' % (state['story'].get('week', 0), event, count)
            choice = doc.get('choices', {}).get(key)
            return bool(choice and isinstance(source, dict) and
                source.get('week') == choice['source']['week'] and source.get('day') == choice['source']['day'] and
                source.get('route') == choice['source']['route'] and source.get('patrol') == choice['source']['patrol_id'] and
                source.get('generation') == choice['source']['generation'] and
                source.get('occurrences', {}).get(str(event), 0) == count - 1)
        return daerweila_source_matches(state, source)
    if operation == 'startEventOption':
        return daerweila_occurrence_matches(state, event, source)
    if operation == 'clientTraceProcessingEvent':
        return all(daerweila_occurrence_matches(state, e, source) for e in state.get('processing_events', []))
    return True


def apply_daerweila_event(state, event, row, tables, receipt):
    catalog = _dw_catalog(state, tables)
    if not catalog or str(event) not in catalog['nodes']:
        return []
    node = catalog['nodes'][str(event)]
    doc = state['story'].get('daerweila_dispatch')
    context = (doc or {}).get('occurrences', {}).get(receipt)
    if not doc or not context or context['event'] != event:
        raise ValueError('missing-daerweila-terminal-or-branch-provenance')
    _dw_require_active(state, doc)
    choice = doc['choices'][context['choice']]
    _dw_live_choice(state, choice)
    dialog = row.get('dialog')
    if dialog is not None:
        traces = dict(dict(state.get('event_traces', [])).get(event, []))
        if not _dw_int(dialog) or dialog not in traces.get('dialog', []):
            raise ValueError('Actual original dispatch dialogue trace required')
    if (choice['pair'] != node['pair'] or choice['side'] != node['side'] or
            event not in state.get('processing_events', []) or _dw_locked(state['story'], choice['side'])):
        raise ValueError('Actual dispatch side/occurrence/lock required')
    if context['parent'] is not None:
        parent = doc['occurrences'].get(context['parent'], {})
        if state['story'].get('event_effect_receipts', {}).get(context['parent']) != parent.get('event'):
            raise ValueError('Actual dispatch parent receipt required')
    pair = catalog['pairs'][str(node['pair'])]
    if event not in pair['terminals'][node['side']]:
        return []
    if str(node['pair']) in doc['awards']:
        raise ValueError('Original dispatch pair already awarded this week')
    before = _dw_counts(doc)
    award = {'pair': node['pair'], 'side': node['side'], 'choice': context['choice'],
        'terminal': event, 'receipt': receipt, 'week': doc['week'], 'source': copy.deepcopy(choice['source']),
        'before': before, 'after': dict(before)}
    award['after'][node['side']] += 1
    if sum(award['after'].values()) > len(catalog['pairs']):
        raise ValueError('Dispatch count exceeds original unique-pair bound')
    doc['awards'][str(node['pair'])] = award
    choice['status'] = 'awarded'
    for side in _DW_SIDES:
        state['story']['daerweila_' + side] = award['after'][side]
    return [('offlineDaerweilaAward', copy.deepcopy(award))]


def expire_daerweila_dispatch(state, route):
    doc = state.get('story', {}).get('daerweila_dispatch')
    if not doc:
        return
    allowed = set(r for p in doc['catalog']['pairs'].values() for r in p['routes'])
    if route in allowed:
        if route != state['story'].get('route'):
            for offer in doc['offers'].values():
                if offer['status'] == 'offered':
                    offer['status'] = 'expired'
            for choice in doc['choices'].values():
                if choice['status'] == 'active':
                    choice['status'] = 'expired'
            _dw_cancel_pending(doc, 'actual-route-handoff')
        return
    for offer in doc['offers'].values():
        if offer['status'] == 'offered':
            offer['status'] = 'expired'
    for choice in doc['choices'].values():
        if choice['status'] == 'active':
            choice['status'] = 'expired'
    _dw_cancel_pending(doc, 'route-departure')


def project_daerweila(state, base_std=None):
    story = state.get('story', {})
    doc = story.get('daerweila_dispatch')
    values = _dw_counts(doc) if doc else _dw_baseline(state, base_std)
    choose = doc['first_devil']['phase'] == 'continued' or doc['baseline']['choose'] if doc else values['choose']
    return {'dwhv': values['human'], 'dwdv': values['devil'],
        'dwhl': _dw_locked(story, 'human'), 'dwdl': _dw_locked(story, 'devil'), 'dwca': bool(choose)}


def daerweila_sync_notices(state, base_std=None):
    value = project_daerweila(state, base_std)
    return [('syncDaerweilaLineData', {'dh': value['dwhv'], 'dd': value['dwdv'],
        'dhl': value['dwhl'], 'ddl': value['dwdl'], 'dca': value['dwca'], 'u': False}),
        ('daerweilaDispatchClose', {'h': value['dwhl'], 'd': value['dwdl']})]


def publish_daerweila_award(proxy, award):
    """Save already committed. Guard original increment and its late callback."""
    state, owner = proxy.progress_snapshot(), proxy.owner
    doc = state.get('story', {}).get('daerweila_dispatch')
    native = getattr(owner, 'storyData', None)
    def owner_live():
        if proxy.owner is not owner:
            return False
        try:
            import gg
            return getattr(gg, 'avatar', owner) is owner
        except ImportError:
            return True
    def absolute():
        if owner_live():
            latest = proxy.progress_snapshot()
            pending = (latest.get('story', {}).get('daerweila_dispatch') or {}).get('first_devil', {}).get('phase') == 'intro_pending'
            for name, body in daerweila_sync_notices(latest):
                current_native = getattr(owner, 'storyData', None)
                if name == 'syncDaerweilaLineData' and pending and getattr(current_native, 'daerweila_choose_asazile', False):
                    body['dca'] = True
                proxy.reply(name, body)
    if not owner_live():
        return
    if (not doc or doc['week'] != award.get('week') or _dw_counts(doc) != award.get('after') or
            doc['awards'].get(str(award.get('pair'))) != award or native is None or
            any(getattr(native, 'daerweila_' + side, None) != award['before'][side] for side in _DW_SIDES)):
        absolute()
        return
    try:
        import gg
        panel = gg.ui.panels.settlement_window
        original = panel.notify_daerweila
    except (ImportError, AttributeError):
        absolute()
        return
    had_override = 'notify_daerweila' in getattr(panel, '__dict__', {})
    saved_override = getattr(panel, '__dict__', {}).get('notify_daerweila')
    registered = [False]
    def notify(side, callback):
        def guarded():
            latest = proxy.progress_snapshot()
            current = latest.get('story', {}).get('daerweila_dispatch')
            same_panel = getattr(getattr(getattr(gg, 'ui', None), 'panels', None), 'settlement_window', None) is panel
            if (owner_live() and same_panel and getattr(owner, 'storyData', None) is native and current and current['week'] == award['week'] and
                    current['awards'].get(str(award['pair'])) == award and _dw_counts(current) == award['after'] and
                    all(getattr(native, 'daerweila_' + s, None) == award['after'][s] for s in _DW_SIDES)):
                callback()
            else:
                absolute()
        result = original(side, guarded)
        registered[0] = True
        return result
    try:
        panel.notify_daerweila = notify
    except (AttributeError, TypeError):
        absolute()
        return
    failed = False
    try:
        proxy.reply('addDaerweilaHumanityValue', {'t': award['side']})
    except Exception:
        failed = True
    finally:
        if had_override:
            panel.notify_daerweila = saved_override
        else:
            del panel.notify_daerweila
    if failed or not registered[0] or any(getattr(native, 'daerweila_' + side, None) != award['after'][side] for side in _DW_SIDES):
        absolute()


def _dw_plain_state(value):
    if value is None or type(value) in (int, bool) or isinstance(value, _dw_text):
        return
    if type(value) is list:
        for item in value:
            _dw_plain_state(item)
        return
    if type(value) is dict:
        for key, item in value.items():
            if not isinstance(key, _dw_text):
                raise ValueError('Dispatch save keys must be plain text')
            _dw_plain_state(item)
        return
    raise ValueError('Dispatch save requires plain literal state; no floats/native objects')


def _dw_validate_document(state):
    story = state.get('story', {})
    doc = story.get('daerweila_dispatch')
    if doc is None:
        _dw_baseline(state)
        return
    _dw_plain_state(doc)
    if (not isinstance(doc, dict) or doc.get('version') != 1 or doc.get('policy') != DAERWEILA_POLICY or
            type(doc.get('week')) is not int or doc['week'] != story.get('week', 0) or
            type(doc.get('generation')) is not int or doc['generation'] < 0 or
            doc.get('status') not in ('active', 'legacy-pending') or
            any(not isinstance(doc.get(k), dict) for k in ('catalog', 'baseline', 'offers', 'choices', 'occurrences', 'awards', 'first_devil')) or
            not isinstance(doc.get('legacy_terminals'), list) or not isinstance(doc.get('first_history'), list)):
        raise ValueError('Invalid canonical dispatch document')
    catalog = doc['catalog']
    unsigned = dict(catalog)
    unsigned.pop('token', None)
    if catalog.get('token') != _dw_hash(unsigned) or any(not isinstance(catalog.get(k), dict) for k in ('pairs', 'nodes', 'conditions')) or not 1 <= len(catalog['pairs']) <= 5:
        raise ValueError('Invalid canonical dispatch catalog')
    baseline = doc['baseline']
    if (set(baseline) != set(('human', 'devil', 'choose')) or type(baseline['choose']) is not bool or
            any(type(baseline[s]) is not int or not 0 <= baseline[s] <= len(catalog['pairs']) for s in _DW_SIDES) or
            sum(baseline[s] for s in _DW_SIDES) > len(catalog['pairs']) or
            doc['status'] == 'active' and (any(baseline.values()) or doc['legacy_terminals'])):
        raise ValueError('Invalid dispatch legacy baseline')
    for identity, offer in doc['offers'].items():
        if (not isinstance(offer, dict) or offer.get('id') != identity or offer.get('status') not in ('offered', 'chosen', 'expired') or
                offer.get('week') != doc['week'] or type(offer.get('day')) is not int or not 0 <= offer['day'] < 7 or
                not isinstance(offer.get('route'), _dw_text) or not offer['route'] or
                not _dw_int(offer.get('area')) or not isinstance(offer.get('patrol_id'), _dw_text) or not offer['patrol_id'] or
                not isinstance(offer.get('patrol_fingerprint'), _dw_text) or len(offer['patrol_fingerprint']) != 64 or
                any(c not in '0123456789abcdef' for c in offer['patrol_fingerprint']) or
                not isinstance(offer.get('heroes'), list) or not offer['heroes'] or any(not _dw_int(h) for h in offer['heroes']) or
                len(set(offer['heroes'])) != len(offer['heroes']) or str(offer.get('pair')) not in catalog['pairs'] or
                offer.get('status') == 'chosen' and offer.get('root') not in doc['choices'] or
                offer.get('status') != 'chosen' and offer.get('root') is not None or
                offer.get('catalog_token') != catalog['token'] or type(offer.get('generation')) is not int or not 1 <= offer['generation'] <= doc['generation']):
            raise ValueError('Invalid durable dispatch patrol offer')
        source = {k:v for k,v in offer.items() if k not in ('id', 'status', 'root')}
        pair = catalog['pairs'][str(offer['pair'])]
        if offer.get('verified_events') != [pair['show'], pair['human'], pair['devil']] or identity != _dw_hash(source):
            raise ValueError('Dispatch offer source fingerprint mismatch')
    for root, choice in doc['choices'].items():
        offer = doc['offers'].get(choice.get('offer')) if isinstance(choice, dict) else None
        if (not offer or choice.get('root') != root or offer.get('root') != root or
                choice.get('pair') != offer['pair'] or choice.get('side') not in _DW_SIDES or
                choice.get('status') not in ('active', 'awarded', 'expired') or choice.get('source', {}).get('id') != offer['id'] or
                choice['source'].get('status') != 'offered' or choice['source'].get('root') is not None or
                any(choice['source'].get(k) != offer[k] for k in offer if k not in ('status', 'root')) or
                choice.get('root_event') != catalog['pairs'][str(offer['pair'])][choice['side']] or
                doc['occurrences'].get(root, {}).get('choice') != root):
            raise ValueError('Invalid immutable dispatch choice')
    for occurrence, context in doc['occurrences'].items():
        choice = doc['choices'].get(context.get('choice')) if isinstance(context, dict) else None
        if (not choice or occurrence.split(':')[:2] != [str(doc['week']),str(context.get('event'))] or len(occurrence.split(':')) != 3 or
                not occurrence.split(':')[2].isdigit() or not 1 <= int(occurrence.split(':')[2]) <= story.get('event_occurrences', {}).get(str(context.get('event')), 0)):
            raise ValueError('Invalid dispatch occurrence linkage')
        node = catalog['nodes'].get(str(context.get('event')), {})
        parent = context.get('parent')
        if (node.get('pair') != choice['pair'] or node.get('side') != choice['side'] or
                parent is None and (occurrence != choice['root'] or context['event'] != choice['root_event']) or
                parent is not None and (parent not in doc['occurrences'] or doc['occurrences'][parent]['choice'] != context['choice'] or
                    context['event'] not in catalog['nodes'][str(doc['occurrences'][parent]['event'])]['children'] or
                    story.get('event_effect_receipts', {}).get(parent) != doc['occurrences'][parent]['event'])):
            raise ValueError('Invalid original dispatch successor edge')
    if len(doc['awards']) > len(catalog['pairs']):
        raise ValueError('Too many unique dispatch awards')
    for pair, award in doc['awards'].items():
        choice = doc['choices'].get(award.get('choice')) if isinstance(award, dict) else None
        if (not choice or pair != str(choice['pair']) or award.get('side') != choice['side'] or
                choice['status'] != 'awarded' or award.get('week') != doc['week'] or award.get('source') != choice['source'] or
                award.get('terminal') not in catalog['pairs'][pair]['terminals'][choice['side']] or
                doc['occurrences'].get(award.get('receipt'), {}).get('choice') != choice['root'] or
                doc['occurrences'][award['receipt']]['event'] != award['terminal'] or
                story.get('event_effect_receipts', {}).get(award['receipt']) != award['terminal']):
            raise ValueError('Invalid exactly-once dispatch award receipt')
        if (set(award.get('before', {})) != set(_DW_SIDES) or set(award.get('after', {})) != set(_DW_SIDES) or
                any(type(award['before'][s]) is not int or award['before'][s] < 0 or type(award['after'][s]) is not int or
                    award['after'][s] != award['before'][s] + int(s == award['side']) for s in _DW_SIDES)):
            raise ValueError('Invalid dispatch award before/after')
    previous = {side: doc['baseline'][side] for side in _DW_SIDES}
    for award in sorted(doc['awards'].values(), key=lambda a: sum(a['after'].values())):
        if award['before'] != previous:
            raise ValueError('Dispatch award sequence does not derive from unique receipts')
        previous = award['after']
    counts = _dw_counts(doc)
    if sum(counts.values()) > len(catalog['pairs']) or any(type(story.get('daerweila_' + s, counts[s])) is not int or story.get('daerweila_' + s, counts[s]) != counts[s] for s in _DW_SIDES):
        raise ValueError('Canonical dispatch counts disagree with unique awards')
    first = doc['first_devil']
    if (first.get('phase') not in ('unseen', 'intro_pending', 'continued') or
            first['phase'] == 'unseen' and first.get('offer') is not None or
            first['phase'] != 'unseen' and first.get('offer') not in doc['offers'] or
            first['phase'] == 'continued' and not any(c['offer'] == first['offer'] and c['side'] == 'devil' for c in doc['choices'].values())):
        raise ValueError('Invalid first devil intro provenance')
    _dw_locked(story, 'human'); _dw_locked(story, 'devil')


def validate_daerweila_state(state):
    try:
        _dw_validate_document(state)
    except (KeyError, TypeError, AttributeError, IndexError):
        raise ValueError('Malformed canonical dispatch state')
