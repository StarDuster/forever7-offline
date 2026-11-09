# -*- coding: ascii -*-
"""Table-driven event lifecycle. Real traces/options/callbacks authorize effects."""
try:
    from offline_chapter_campaign import (resolve_normal_chapter, refresh_normal_chapters,
        normal_chapter_token, validate_normal_chapters, expire_normal_chapters,
        revoke_normal_chapter_projection, stage_projection_owner)
except ImportError:
    pass

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
    from offline_huisu import (huisu_context, huisu_token, validate_huisu_state,
        project_huisu, huisu_notice, huisu_std_projection, huisu_route_projection,
        city_action_context, dream_action_token, authorize_action_admission,
        commit_action_admission, event_execution_admission,
        resolve_event_execution_context, check_dream_contract,
        huisu_trigger_permitted, accept_huisu_event_completion,
        prepare_huisu_operation, mark_huisu_nextday, huisu_day_guard,
        reset_huisu_on_committed_day_or_week)
except ImportError:
    pass

try:
    from offline_battle_terminal import bind_event_terminal_context
except ImportError:
    pass

try:
    from offline_action_ledger import set_event_baseline
except ImportError:
    pass

import copy
try:
    from offline_story import evaluate_story_condition
    from offline_event_effects import plan_event_effects
    from offline_conditions import parse_original_condition_literal
except ImportError:
    pass


def evaluate_story_trigger(row, state, selected_starter_only=False):
    if not row.get('release'):
        return False
    decisions = [evaluate_story_condition(kind, value, state, selected_starter_only)
                 for kind, value in row.get('conds', {}).items()]
    if False in decisions:
        return False
    return None if None in decisions else True


def _ose_initial_seed_permitted(state, event, row, trigger):
    """One persisted fresh-world admission exempts only its bootstrap edge.

    This seed is minted by the fresh LocalProxy initializer, never from route,
    completion history or an unmarked available list. All other original facts
    remain authoritative. It is consumed in the actual start transaction.
    """
    story = state['story']
    origin = story.get('available_origins', {}).get(str(event))
    if (not isinstance(origin, dict) or origin.get('source') != 'offline-initial-seed' or
            origin.get('policy') != 'offline-fresh-entry-seed-v1' or
            origin.get('bootstrap_predecessor') != 6 or origin.get('context') != [0, 0, '1'] or
            [story.get('week'), story.get('date'), story.get('route')] != origin['context'] or
            story.get('emergency') is not True or not row.get('release') or
            not trigger or not trigger.get('release') or 'dream_id' in row):
        return False
    try:
        predecessors = parse_original_condition_literal(trigger.get('conds', {}).get(1, 'set()'))
    except (ValueError, TypeError):
        return False
    if not isinstance(predecessors, (set, list, tuple)) or set(predecessors) != set((6,)):
        return False
    if any(e in set(state.get('completed_events', [])) | set(state.get('processing_events', []))
           for e in row.get('mutexEvent', ())):
        return False
    return all(evaluate_story_condition(kind, value, state) is True
        for kind, value in trigger.get('conds', {}).items() if kind != 1)


def refresh_story_events(state, triggers, content):
    available = dict(state['available_events'])
    processing, completed = set(state['processing_events']), set(state['completed_events'])
    story = state['story']
    branches = {1038: 8, 1039: 7, 1040: 37}
    restored = set(hero for event, hero in branches.items() if event in completed | processing)
    if len(restored) > 1:
        raise ValueError('Conflicting original starter branch history')
    if restored:
        chosen = list(restored)[0]
        if story.get('starter_hero') not in (None, chosen):
            raise ValueError('Starter choice conflicts with completed branch')
        story['starter_hero'] = chosen
        story.setdefault('starter_source', 'original-event-history')
    for event, hero in branches.items():
        if hero != story.get('starter_hero'):
            available.pop(event, None)
    stamp = [story.get('week', 0), story.get('date', 0)]
    context_stamp = stamp + [story.get('route', '1')]
    origins = story.setdefault('available_origins', {})
    patrol_events = set(((state.get('city_actions') or {}).get('patrol') or {}).get('events', []))
    for event in list(available):
        origin = origins.get(str(event))
        if origin and origin.get('source') == 'offline-initial-seed':
            if not _ose_initial_seed_permitted(state, event, content.get(event, {}), triggers.get(event)):
                available.pop(event, None)
                origins.pop(str(event), None)
            continue
        if event not in triggers or event in patrol_events or origin and origin.get('source') != 'trigger':
            continue
        row = content.get(event, {})
        decision = evaluate_story_trigger(triggers[event], state, event in branches)
        if not huisu_trigger_permitted(state, event, row, triggers[event]):
            decision = False
        blocked = any(e in completed | processing for e in row.get('mutexEvent', ()))
        if blocked or decision is False or (decision is None and origin and origin.get('context') != context_stamp):
            available.pop(event, None)
            origins.pop(str(event), None)
        elif origin is None:
            origins[str(event)] = {'source': 'trigger', 'context': context_stamp}
    for event, trigger in sorted(triggers.items()):
        row = content.get(event, {})
        failure = story.get('event_terminal_failures', {}).get(str(event))
        if failure and failure.get('week') == story.get('week',0) and (not row.get('repeatable') or failure.get('day') == state.get('day',{}).get('stock_day',story.get('date',0))):
            available.pop(event,None)
            continue
        if not row.get('release') or event in processing or event in available:
            continue
        if event in completed:
            if not row.get('repeatable') or story.get('event_activation_dates', {}).get(str(event), stamp) == stamp:
                continue
        if event in branches and branches[event] != story.get('starter_hero'):
            continue
        if any(e in completed | processing for e in row.get('mutexEvent', ())):
            continue
        if (huisu_trigger_permitted(state, event, row, trigger) and
                evaluate_story_trigger(trigger, state, event in branches) is True):
            available[event] = 1
            origins[str(event)] = {'source': 'trigger', 'context': context_stamp}
    state['available_events'] = [[event, value] for event, value in sorted(available.items())]
    filter_daerweila_availability(state)


def story_occurrence_key(state, event):
    return '%s:%s:%s' % (state['story'].get('week', 0), event, state['story'].get('event_occurrences', {}).get(str(event), 0))


def begin_story_occurrence(state, event, content=None, triggers=None, parent_occurrence=None, tables=None):
    story = state['story']
    row, trigger = (content or {}).get(event, {}), (triggers or {}).get(event)
    if content is not None and not row.get('release'):
        raise ValueError('Original released event content required')
    execution = event_execution_admission(state, event, row, trigger, parent_occurrence)
    if parent_occurrence in story.get('event_contexts', {}) and execution is None:
        raise ValueError('Original successor dream context is stale')
    if 'dream_id' in row and not check_dream_contract(row, execution):
        raise ValueError('Actual dream occurrence provenance required')
    # Ordinary availability retains its existing admission contract, including
    # the explicit fresh-game seed. The additional full trigger recheck belongs
    # to dream providers; it must not fabricate a startup predecessor.
    if not parent_occurrence and trigger is not None and (execution is not None or 'dream_id' in row):
        if not huisu_trigger_permitted(state, event, row, trigger) or evaluate_story_trigger(trigger, state) is not True:
            raise ValueError('Actual original event trigger required at occurrence start')
    origin = story.get('available_origins', {}).get(str(event))
    if origin and origin.get('source') == 'offline-initial-seed':
        if not _ose_initial_seed_permitted(state, event, row, trigger):
            raise ValueError('Explicit fresh entry seed conditions changed')
        story['available_origins'].pop(str(event), None)
    occurrences = story.setdefault('event_occurrences', {})
    occurrences[str(event)] = occurrences.get(str(event), 0) + 1
    story.setdefault('event_callbacks', {})[str(event)] = []
    story.setdefault('event_activation_dates', {})[str(event)] = [story.get('week', 0), story.get('date', 0)]
    occurrence = story_occurrence_key(state, event)
    bind_event_terminal_context(state, event, occurrence)
    bind_daerweila_occurrence(state, event, occurrence, content or {}, triggers or {}, parent_occurrence, tables)
    if execution:
        story.setdefault('event_contexts', {})[occurrence] = execution
        value = huisu_context(state)
        if value and execution.get('origin') == 'entry':
            value['entry_occurrence'] = occurrence
        if value and execution.get('admission_id') in value['admissions']:
            value['admissions'][execution['admission_id']]['selected_occurrence'] = occurrence
    state['completed_events'] = [e for e in state['completed_events'] if e != event]
    state['event_traces'] = [entry for entry in state['event_traces'] if entry[0] != event]


def prepare_story_operation(state, operation, arguments, content, triggers, tables=None):
    candidate = copy.deepcopy(state)
    story = candidate['story']
    notices = []
    available = dict(candidate['available_events'])
    processing, completed = set(candidate['processing_events']), set(candidate['completed_events'])
    traces = {event: {key: set(values) for key, values in trace} for event, trace in candidate['event_traces']}

    def project():
        candidate['available_events'] = [[e, v] for e, v in sorted(available.items())]
        candidate['processing_events'], candidate['completed_events'] = sorted(processing), sorted(completed)
        candidate['event_traces'] = [[e, [[k, sorted(v)] for k, v in sorted(trace.items())]] for e, trace in sorted(traces.items())]

    def complete(event):
        project()
        receipt = story_occurrence_key(candidate, event)
        context = {'receipt_key': receipt, 'completed_callbacks': story.get('event_callbacks', {}).get(str(event), [])}
        planned, effects, diagnostic = plan_event_effects(candidate, event, content, tables, context)
        if not diagnostic['ready']:
            story.setdefault('pending_effects', {})[str(event)] = diagnostic
            return False
        candidate.clear()
        candidate.update(planned)
        # Preserve references used by the enclosing state machine after atomic
        # planner deep copy. These contain no native objects or callbacks.
        story.clear()
        story.update(candidate['story'])
        candidate['story'] = story
        notices.extend(effects)
        processing.discard(event)
        completed.add(event)
        stock_day = candidate.get('day', {}).get('stock_day')
        if type(stock_day) is int:
            story.setdefault('event_days', {})[str(event)] = {'week': story.get('week', 0), 'day': stock_day}
            if type(story.get('week_actions_spent')) is int:
                story.setdefault('event_action_baselines', {})[str(event)] = story['week_actions_spent']
        baseline = globals().get('set_event_baseline')
        if baseline is not None and type(story.get('week')) is int:
            # Explicit offline ACTIONAFTEREVENT baseline.  It rides in the same
            # state document as the completion effects; an invalid ledger
            # returns False and keeps code 20 unsupported.
            baseline(candidate, event, story['week'])
        available.pop(event, None)
        story.setdefault('event_history', [])
        if event not in story['event_history']:
            story['event_history'].append(event)
        story.setdefault('pending_effects', {}).pop(str(event), None)
        if event == 1021:
            story['pending_effects'].pop('successors-after-1004', None)
        project()
        if tables.get('chapter_mission_data'):
            notices.extend(refresh_normal_chapters(candidate, dict(tables, event_content=content)))
        notices.extend(accept_huisu_event_completion(candidate, event, receipt))
        notices.append(('completeEventReplyEnd', {'e': event}))
        return True

    def requirements_met(event):
        requirements = content[event].get('completeConds', {})
        if requirements:
            return all(set(values).issubset(traces.get(event, {}).get(kind, set())) for kind, values in requirements.items())
        return not content[event].get('dialog') or content[event]['dialog'] in traces.get(event, {}).get('dialog', set())

    if operation == 'option':
        parent, selected = arguments.get('e'), arguments.get('se')
        dispatch_source = arguments.get('_daerweila_source')
        if dispatch_source is not None and not daerweila_occurrence_matches(candidate, parent, dispatch_source):
            return candidate, []
        if (parent not in processing or selected not in content.get(parent, {}).get('events', ()) or
                not content.get(selected, {}).get('release')):
            raise ValueError('Invalid original event option')
        if ('dream_id' in content[parent] or story_occurrence_key(candidate, parent) in story.get('event_contexts', {}) or
                story_occurrence_key(candidate, parent) in story.get('daerweila_dispatch', {}).get('occurrences', {})) and not requirements_met(parent):
            raise ValueError('Actual original dream parent traces required before option')
        parent_occurrence = story_occurrence_key(candidate, parent)
        if complete(parent):
            for sibling in content[parent].get('events', ()):
                available.pop(sibling, None)
            project()
            begin_story_occurrence(candidate, selected, content, triggers, parent_occurrence, tables)
            completed.discard(selected)
            traces.pop(selected, None)
            processing.add(selected)
            available.pop(selected, None)
            notices.append(('startEventReply', {'e': selected, 'r': 1}))
            if requirements_met(selected) and not content[selected].get('events'):
                complete(selected)
    elif operation in ('trace', 'combat_win'):
        key, value = arguments.get('k'), arguments.get('d', {}).get('c')
        if key == 'battle' and operation != 'combat_win':
            return candidate, []
        if operation == 'combat_win':
            wins = story.setdefault('battle_wins', [])
            if value not in wins:
                wins.append(value)
        for event in sorted(processing):
            dispatch_source = arguments.get('_daerweila_source')
            if operation == 'trace' and dispatch_source is not None and not daerweila_occurrence_matches(candidate, event, dispatch_source):
                continue
            trace_source = arguments.get('_winning_terminal_trace_source')
            if operation == 'trace' and trace_source is not None:
                current_key = story_occurrence_key(candidate, event)
                if (current_key in story.get('event_terminal_contexts', {}) or
                        story.get('available_origins', {}).get(str(event), {}).get('source') == 'accepted_mission_result'):
                    if (trace_source.get('week') != story.get('week', 0) or
                            trace_source.get('occurrences', {}).get(str(event), 0) !=
                            story.get('event_occurrences', {}).get(str(event), 0)):
                        continue
            row = content.get(event)
            if not row:
                continue
            if operation == 'combat_win':
                expected = set(row.get('completeConds', {}).get('battle', ()))
                for field in ('contentFinishBattle', 'enterBattle'):
                    scenes = row.get(field, ())
                    expected.update(scenes if isinstance(scenes, (list, tuple, set)) else (scenes,))
                if value not in expected:
                    continue
                if row.get('enterBattle'):
                    source_event = arguments.get('source_event')
                    if source_event != event or arguments.get('source_receipt') != story_occurrence_key(candidate, event):
                        continue
                    source = arguments.get('source_occurrence')
                    current = [story.get('week', 0), story.get('event_occurrences', {}).get(str(event), 0)]
                    if source is not None and list(source) != current:
                        continue
            if operation == 'combat_win':
                callbacks = story.setdefault('event_callbacks', {}).setdefault(str(event), [])
                token = 'battle:%s' % value
                if token not in callbacks:
                    callbacks.append(token)
            if value is not None:
                traces.setdefault(event, {}).setdefault(key, set()).add(value)
            if requirements_met(event) and not row.get('events'):
                complete(event)
    elif operation in ('ui_complete', 'callback'):
        event = arguments.get('e')
        source = arguments.get('source_occurrence')
        current = [story.get('week', 0), story.get('event_occurrences', {}).get(str(event), 0)]
        if source is not None and list(source) != current:
            return candidate, []
        if event not in processing:
            if event in completed:
                return candidate, []
            raise ValueError('No matching original event callback')
        token = arguments.get('token', 'ui:%s' % event)
        expected = set('%s:%s' % (kind, event) for kind in ('ui', 'movie', 'puzzle', 'caidan', 'activity'))
        if token not in expected:
            raise ValueError('Unexpected original event callback')
        callbacks = story.setdefault('event_callbacks', {}).setdefault(str(event), [])
        if token not in callbacks:
            callbacks.append(token)
        if requirements_met(event) and not content[event].get('events'):
            complete(event)
    elif operation == 'start':
        event = arguments.get('e')
        if event not in processing or not content.get(event, {}).get('release'):
            raise ValueError('Event is not actually processing')
        if requirements_met(event) and not content[event].get('events'):
            complete(event)
    elif operation == 'external':
        event = arguments.get('e')
        row = content.get(event, {})
        permitted = bool(row.get('release') and row.get('client_event') and
            not any(e in completed | processing for e in row.get('mutexEvent', ())))
        if not huisu_trigger_permitted(candidate, event, row, triggers.get(event, {})):
            permitted = False
        if event in triggers:
            permitted = permitted and evaluate_story_trigger(triggers[event], candidate) is True
        if permitted and event not in completed and event not in processing:
            project()
            begin_story_occurrence(candidate, event, content, triggers, tables=tables)
            completed.discard(event)
            if not row.get('dialog') and not row.get('completeConds') and not row.get('events'):
                processing.add(event)
                if not complete(event):
                    processing.discard(event)
                    available[event] = 1
            else:
                available[event] = 1
            story.setdefault('available_origins', {})[str(event)] = {'source': 'external'}
        # Original dedicated reply is mandatory even for a refused request.
        notices.append(('triggerExternalEventReply', {}))
    else:
        raise ValueError('Unknown original story operation')
    project()
    refresh_story_events(candidate, triggers, content)
    if operation == 'external':
        notices.append(('pushEvents', {'a': candidate['available_events'], 'p': candidate['processing_events']}))
    return candidate, notices


def install_story_completion_observers():
    """Observe stock continuation boundaries after actual UI/movie/puzzle leave."""
    from entity.ClientAvatar import ClientAvatar
    if getattr(ClientAvatar, '_f7_story_completion_observers', False):
        return
    for method, field, kind in (('startMovie', 'ui', 'ui'),
                               ('startEventBattle', 'movie', 'movie'),
                               ('startEventUI', 'puzzle_room', 'puzzle'),
                               ('startPuzzleRoom', 'enter_caidan', 'caidan')):
        original = getattr(ClientAvatar, method)

        def wrap(original_method, original_field, token_kind):
            def observed(self, event, *args, **kwargs):
                proxy = getattr(self, 'server', None)
                source = None
                if proxy is not None and isinstance(getattr(proxy, 'story', None), dict):
                    source = [proxy.story.get('week', 0), proxy.story.get('event_occurrences', {}).get(str(event), 0)]
                result = original_method(self, event, *args, **kwargs)
                import com.data.cdata.event_content as content
                if content.data.get(event, {}).get(original_field):
                    proxy = getattr(self, 'server', None)
                    if proxy is not None and event in getattr(proxy, 'processing_events', ()):
                        proxy.defer(1, lambda: proxy.process_story('callback',
                            {'e': event, 'token': '%s:%s' % (token_kind, event), 'source_occurrence': source}))
                return result
            return observed
        setattr(ClientAvatar, method, wrap(original, field, kind))
    ClientAvatar._f7_story_completion_observers = True
