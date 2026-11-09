# -*- coding: ascii -*-
"""Transactional stock-client day protocol, independent of route/economy policy.

All functions prepare copies. Persist the entire returned document atomically
before publishing notices. No elapsed-time, dialogue or battle completion is
inferred here. A rule provider supplies a settlement plan or an explicit pending
reason; client field evidence alone is not an official server economy formula.
"""
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

import copy
try:
    from offline_route_agreements import reset_route_goodnights, route_goodnight_notices
except ImportError:
    pass
try:
    from offline_flashback import flashback_context
except ImportError:
    pass
try:
    from offline_intelligence import advance_intelligence_day
except ImportError:
    pass


def initial_day_state():
    return {'version': 1, 'intent': None, 'receipt': None, 'review': None}


def _integer(value):
    return type(value) is int


def _daily_values(value):
    return (isinstance(value, dict) and
            all(_integer(value.get(k)) for k in ('rsv', 'dvv', 'frv')))


def validate_day_state(day):
    if not isinstance(day, dict) or day.get('version') != 1:
        raise ValueError('Unsupported offline day state')
    intent = day.get('intent')
    if intent is not None:
        if (not isinstance(intent, dict) or not _integer(intent.get('day')) or
                not _integer(intent.get('week')) or
                intent.get('phase') not in ('checked', 'clientop')):
            raise ValueError('Invalid day intent')
    review = day.get('review')
    if review is not None and not all(_daily_values(review.get(k)) for k in ('c', 'l')):
        raise ValueError('Invalid persisted daily settlement')
    receipt = day.get('receipt')
    if receipt is not None:
        if (not isinstance(receipt, dict) or not _integer(receipt.get('day')) or
                not _integer(receipt.get('week')) or not isinstance(receipt.get('notices'), list)):
            raise ValueError('Invalid day receipt')
        _validate_notices(receipt['notices'])
        names = receipt.get('route_sync_names', [])
        if (not isinstance(names, list) or len(names) != len(set(names)) or
                any(name not in ('syncBaiyuInfos', 'syncWuluLineData',
                    'syncJiaohuiSpecialNight', 'syncAlanSpecialNight') for name in names)):
            raise ValueError('Invalid route synchronization receipt')


def _validate_notices(notices):
    if (len(notices) < 3 or [n[0] for n in notices[-3:]] !=
            ['get_city_data_reply', 'updateDay', 'showDailySettlement']):
        raise ValueError('Invalid day callback sequence')
    for name, payload in notices[:-3]:
        if (name != 'updateCurFatigueValue' or not _integer(payload.get('h')) or
                not _integer(payload.get('v')) or not 0 <= payload['v'] <= 100):
            raise ValueError('Invalid daily hero callback')
    if not isinstance(notices[-3][1].get('cd'), dict) or not _integer(notices[-2][1].get('d')):
        raise ValueError('Invalid city/date callback')
    if not all(_daily_values(notices[-1][1].get(k)) for k in ('c', 'l')):
        raise ValueError('Daily review requires original rsv/dvv/frv fields')


def _pending(state, reason):
    return copy.deepcopy(state), [], False, {'pending': reason}


def prepare_day_operation(state, operation, arguments, blockers=None, plan=None):
    """Return (candidate, [(stock_method, args)], changed, diagnostic).

    State adapter schema: day_protocol + weeknum (stock w/d/c/l), city (stock
    snapshot), story (separate condition date/week), optionally profile.
    blockers MUST be a freshly computed exhaustive list of active/eligible or
    unknown pre-day events/effects/route interruptions; None means unverified.
    Empty list certifies all route conditions were evaluated. The caller must
    update CLIENTOP condition 102 to {4}, refresh original events, and pass a
    fresh blockers result before incDay. It must not call a timer to clear it.

    A plan is supplied by a route/economy provider, tied to source week/day and
    city, and containing next_day, condition_date, city, c, l and evidence.
    Optional profile is a fully prepared replacement, enabling fatigue/income
    changes in the SAME commit. This module never changes owned collections.
    No request ID exists in the original empty inc RPC: replay is pinned until
    a subsequent statusCheck explicitly arms the next day's intent.
    """
    source = copy.deepcopy(state)
    day = source.setdefault('day_protocol', initial_day_state())
    validate_day_state(day)
    weeknum, city = source.get('weeknum', {}), source.get('city', {})
    week, current = weeknum.get('w'), weeknum.get('d')
    if not _integer(week) or not _integer(current) or not _integer(city.get('av')):
        return _pending(state, 'missing_authoritative_day_or_city')
    if operation not in ('statusCheck', 'updateEventCondClient',
                         'incDayWhenNoActionVal', 'clearCurDailySettlement'):
        raise ValueError('Unsupported day operation')
    if operation == 'clearCurDailySettlement':
        if arguments:
            raise ValueError('clearCurDailySettlement takes no arguments')
        if day['review'] is None:
            return copy.deepcopy(state), [], False, {}
        day['review'] = None
        weeknum['c'], weeknum['l'] = {}, {}
        return source, [], True, {}
    if operation == 'incDayWhenNoActionVal' and arguments:
        raise ValueError('incDayWhenNoActionVal takes no arguments')
    receipt = day['receipt']
    if operation == 'incDayWhenNoActionVal' and day['intent'] is None and receipt:
        if (receipt['week'], receipt['day'] + 1) == (week, current):
            return copy.deepcopy(state), copy.deepcopy(receipt['notices']), False, {'replay': True}
    if city['av'] > 0 and not source.get('huisu_rest_bridge'):
        return _pending(state, 'action_value_positive')
    if operation == 'statusCheck':
        if arguments != {'s': 'nextday'}:
            raise ValueError('Only nextday status check belongs to day protocol')
        if blockers is None:
            return _pending(state, 'pre_day_event_scan_unverified')
        if blockers:
            return copy.deepcopy(state), [('statusCheckReply', {'r': 'event', 's': 'nextday'})], False, {'pending': copy.deepcopy(blockers)}
        intent = {'week': week, 'day': current, 'phase': 'checked'}
        if (day['intent'] and day['intent']['phase'] == 'clientop' and
                (day['intent']['week'], day['intent']['day']) == (week, current)):
            intent['phase'] = 'clientop'
        changed = day['intent'] != intent
        day['intent'] = intent
        return source, [('statusCheckReply', {'r': 'ok', 's': 'nextday'})], changed, {}
    intent = day['intent']
    if intent is None or (intent['week'], intent['day']) != (week, current):
        return _pending(state, 'nextday_status_check_required')
    if operation == 'updateEventCondClient':
        if arguments.get('c') != 102 or arguments.get('v') != '4':
            raise ValueError('Expected original CLIENTOP 102 JSON scalar 4')
        changed = intent['phase'] != 'clientop'
        intent['phase'] = 'clientop'
        # No invented RPC reply: original updateEventCondClient has no day reply.
        return source, [], changed, {'condition_update': {'type': 102, 'value': [4]}}
    if intent['phase'] != 'clientop':
        return _pending(state, 'nextday_clientop_required')
    if blockers is None or blockers:
        return _pending(state, 'pre_day_events_pending' if blockers else 'pre_day_event_scan_unverified')
    if plan is None:
        return _pending(state, 'daily_economy_or_route_rules_unverified')
    if (plan.get('source_week') != week or plan.get('source_day') != current or
            plan.get('source_city') != city):
        return _pending(state, 'stale_daily_settlement_plan')
    if (not plan.get('evidence') or not _integer(plan.get('next_day')) or
            plan['next_day'] != current + 1 or not _integer(plan.get('condition_date'))):
        raise ValueError('Settlement requires sourced next day and separate condition date')
    if ('source_profile' in plan and plan['source_profile'] != source.get('profile') or
            'source_date' in plan and plan['source_date'] != source.get('story', {}).get('date')):
        return _pending(state, 'stale_daily_settlement_plan')
    next_city = plan.get('city')
    if (not isinstance(next_city, dict) or not _integer(next_city.get('av')) or
            next_city['av'] < 0 or not all(k in next_city for k in city)):
        raise ValueError('Daily settlement requires complete city snapshot')
    if not all(_daily_values(plan.get(k)) for k in ('c', 'l')):
        raise ValueError('Daily settlement cannot use empty review dictionaries')
    notices = copy.deepcopy(plan.get('hero_notices', [])) + [('get_city_data_reply', {'cd': copy.deepcopy(next_city)}),
               ('updateDay', {'d': plan['next_day']}),
               ('showDailySettlement', {k: copy.deepcopy(plan[k]) for k in ('c', 'l')})]
    _validate_notices(notices)
    source['city'] = copy.deepcopy(next_city)
    weeknum.update(d=plan['next_day'], c=copy.deepcopy(plan['c']), l=copy.deepcopy(plan['l']))
    source.setdefault('story', {})['date'] = plan['condition_date']
    if 'profile' in plan:
        source['profile'] = copy.deepcopy(plan['profile'])
    day['review'] = copy.deepcopy(notices[-1][1])
    day['previous_values'] = copy.deepcopy(plan['c'])
    day['receipt'] = {'week': week, 'day': current, 'notices': copy.deepcopy(notices),
                      'evidence': copy.deepcopy(plan['evidence'])}
    day['intent'] = None
    validate_day_state(day)
    return source, notices, True, {}


def commit_day_operation(state, operation, arguments, persist, publish,
                         blockers=None, plan=None):
    """Persist before any callback. persist MUST atomically replace full state.

    A failed persist leaves input untouched and publishes nothing. Caller swaps
    its in-memory state to the returned candidate only on successful return.
    Publication failures retain committed replay receipt for retry/reconnect.
    """
    candidate, notices, changed, diagnostic = prepare_day_operation(
        state, operation, arguments, blockers, plan)
    if changed:
        persist(copy.deepcopy(candidate))
    for name, payload in notices:
        publish(name, copy.deepcopy(payload))
    return candidate, changed, diagnostic


def week_transition_boundary(state, operation):
    """Design boundary; no official reset whitelist or ending award is invented.

    Persistent ownership: profile heroes/skins/treasures, earned endings/CG and
    collection unlocks require separate retention policy. Per-week city, action,
    route, events and condition facts require explicit per-field reset rules.
    Full avatar must be committed before handleIncWeekReply/handleResetWeekReply,
    and updateClientAvatarReply must reconstruct that SAME committed avatar.
    """
    if operation not in ('handleIncWeekAsk', 'handleResetWeekAsk', 'handleResetWeek'):
        raise ValueError('Unknown week transition')
    return {'pending': 'week_reset_retention_and_full_avatar_rules_unverified',
            'operation': operation, 'mutates': False}


def prepare_gateway_day_operation(state, operation, arguments, blockers=None,
                                  plan=None, stock_day=None, tables=None):
    """Adapter for local_gateway's existing story/profile/conditions schema.

    day stores only protocol metadata plus stock_day (WeekNumData.d); condition
    DATE remains story.date. Pass stock_day from the real avatar at first use.
    story.city_values MUST contain authoritative scalar city data including av;
    missing values remain pending rather than adopting the display defaults.
    Plan.city uses the original area_N keys. Conditions persist original JSON
    scalar 4; the condition evaluator normalizes CLIENTOP to its required set.
    """
    if flashback_context(state) is not None:
        return copy.deepcopy(state), [], False, {'pending': 'flashback_requires_original_nextday_protocol'}
    if operation == 'incDayWhenNoActionVal' and huisu_day_guard(state):
        return copy.deepcopy(state), [], False, {'pending': huisu_day_guard(state)}
    original = copy.deepcopy(state)
    story = original.get('story', {})
    metadata = original.get('day', initial_day_state())
    current = metadata.get('stock_day', stock_day)
    values = copy.deepcopy(story.get('city_values', {}))
    values['areas'] = {'area_%s' % key: copy.deepcopy(value)
                       for key, value in story.get('city_areas', {}).items()}
    review = metadata.get('review') or {'c': {}, 'l': {}}
    entry_bridge = False
    if operation == 'statusCheck' and huisu_context(original, True) is None and tables:
        unused, unused_notices, entry_bridge, unused_diag = prepare_huisu_operation(
            original, 'requestStoryhuisu', {}, tables, operation_id='entry-rest-probe')
    normalized = {'day_protocol': copy.deepcopy(metadata),
                  'weeknum': {'w': story.get('week'), 'd': current,
                              'c': copy.deepcopy(review['c']), 'l': copy.deepcopy(review['l'])},
                  'city': values, 'story': copy.deepcopy(story),
                  'profile': copy.deepcopy(original.get('profile')),
                  'huisu_rest_bridge': huisu_context(original, True) is not None or entry_bridge}
    prepared, notices, changed, diagnostic = prepare_day_operation(
        normalized, operation, arguments, blockers, plan)
    if not changed and diagnostic.get('condition_update'):
        fact = dict(original.get('conditions', [])).get(102)
        present = fact if isinstance(fact, (list, tuple)) else [fact]
        changed = 4 not in present
    if not changed:
        if operation == 'incDayWhenNoActionVal' and diagnostic.get('replay'):
            names = (metadata.get('receipt') or {}).get('route_sync_names', [])
            notices = route_goodnight_notices(story, names) + notices
            if (metadata.get('receipt') or {}).get('huisu_reset'):
                notices = [huisu_notice(original)] + notices
        return original, notices, False, diagnostic
    original['day'] = prepared['day_protocol']
    original['day']['stock_day'] = prepared['weeknum']['d']
    new_city = prepared['city']
    original['story']['city_values'] = {k: copy.deepcopy(v) for k, v in new_city.items() if k != 'areas'}
    areas = new_city.get('areas', {})
    if any(not key.startswith('area_') or not key[5:].isdigit() for key in areas):
        raise ValueError('Expected original area_N city keys')
    original['story']['city_areas'] = {key[5:]: copy.deepcopy(value) for key, value in areas.items()}
    original['story']['date'] = prepared['story']['date']
    original['profile'] = prepared['profile']
    if 'condition_update' in diagnostic:
        conditions = dict(original.get('conditions', []))
        conditions[102] = 4
        original['conditions'] = [[k, v] for k, v in sorted(conditions.items())]
    if operation == 'incDayWhenNoActionVal':
        conditions = dict(original.get('conditions', []))
        operation_value = conditions.get(102)
        if operation_value == 4:
            conditions.pop(102, None)
        elif isinstance(operation_value, (list, tuple)):
            conditions[102] = [value for value in operation_value if value != 4]
        original['conditions'] = [[k, v] for k, v in sorted(conditions.items())]
    if operation == 'incDayWhenNoActionVal':
        # Prepared-only mutation; caller persists this whole candidate before
        # any night-reset notification. Original client already played dialogue.
        resets = reset_route_goodnights(original['story'])
        original['day']['receipt']['route_sync_names'] = [name for name, body in resets]
        notices = resets + notices
        notices.extend(advance_intelligence_day(original,current,original['day']['stock_day']))
        if 'route20_huisu' in original['story']:
            notices = reset_huisu_on_committed_day_or_week(original) + notices
            original['day']['receipt']['huisu_reset'] = True
    return original, notices, True, diagnostic


OFFLINE_DAY_POLICY = 'original-client-basic-city-cycle-v1'


def offline_city_defaults():
    """Explicit offline initial policy, matching original CityData.__init__."""
    return {'dv': 0, 'av': 0, 'bf': 0, 'fv': 0, 'ev': 0, 'rv': 0,
            'dvc': 0, 'pn': 1, 'uc': False}


def build_offline_daily_plan(state, fatigue_catalog, upgrade_catalog, stock_day=None):
    """Build an actual base-city day settlement under a documented offline rule.

    This is a playable local economy policy, not a claim of byte-for-byte
    official server behavior. Original CityData.REC_ACTION_VAL supplies 24;
    fatigue_recover supplies per-week recovery; city_upgrade.money_output
    supplies daily construction fund for FREE (0) areas. Current research,
    intelligence and force are city capacities, not repeated currency grants.
    Patrol friendship is awarded by actual patrol, never by simply ending day.

    Route-specific event effects still execute through the original event
    lifecycle. Provider refuses active gameplay, unfinished effects, special
    pending transitions and final-day overflow, without completing any event.
    Caller must still pass an exhaustive pre-day trigger scan to the protocol.
    """
    if flashback_context(state) is not None:
        return None, {'pending': 'flashback_requires_original_nextday_protocol'}
    if huisu_day_guard(state):
        return None, {'pending': huisu_day_guard(state)}
    story = state.get('story', {})
    day = state.get('day', {})
    week, current = story.get('week'), day.get('stock_day', stock_day)
    if not _integer(week) or not _integer(current) or not _integer(story.get('date')):
        return None, {'pending': 'missing_authoritative_day_context'}
    if current < 0 or current >= 7:
        return None, {'pending': 'ending_or_week_transition_required'}
    if story.get('emergency'):
        return None, {'pending': 'emergency_story_pending'}
    if state.get('processing_events') or story.get('pending_effects'):
        return None, {'pending': 'unfinished_original_story_effects'}
    if (state.get('battle') or {}).get('active'):
        return None, {'pending': 'actual_battle_pending'}
    if story.get('patrol_pending') or story.get('patrol_reward_pending'):
        return None, {'pending': 'actual_patrol_pending'}
    if story.get('pending_day_transition'):
        return None, {'pending': copy.deepcopy(story['pending_day_transition'])}
    values = copy.deepcopy(story.get('city_values', {}))
    for key in ('av', 'bf', 'dv', 'rv', 'fv'):
        if not _integer(values.get(key)) or values[key] < 0:
            return None, {'pending': 'missing_or_invalid_city_value:' + key}
    if values['av'] != 0 and huisu_context(state, True) is None:
        return None, {'pending': 'action_value_positive'}
    areas = story.get('city_areas', {})
    income = 0
    for key, area in areas.items():
        status = area.get('st', [])
        if not status or not _integer(status[0]):
            return None, {'pending': 'invalid_city_area_state:' + str(key)}
        if status[0] != 0:
            continue
        area_id = area.get('id')
        level = area.get('lv')
        if not _integer(area_id) or not _integer(level):
            return None, {'pending': 'missing_city_area_level:' + str(key)}
        rule = upgrade_catalog.get((area_id, level))
        if not rule or not _integer(rule.get('money_output')) or rule['money_output'] < 0:
            return None, {'pending': 'unsupported_city_daily_income:%s:%s' % (area_id, level)}
        income += rule['money_output']
    fatigue_rule = fatigue_catalog.get(week, fatigue_catalog.get(-1))
    if not fatigue_rule or not _integer(fatigue_rule.get('fatigue_recover')) or fatigue_rule['fatigue_recover'] < 0:
        return None, {'pending': 'missing_original_fatigue_recovery'}
    profile = copy.deepcopy(state.get('profile'))
    if not isinstance(profile, dict) or not isinstance(profile.get('heroes'), dict):
        return None, {'pending': 'missing_owned_hero_profile'}
    notices = []
    for key, hero in sorted(profile['heroes'].items()):
        if not str(key).isdigit() or not _integer(hero.get('cf')) or not 0 <= hero['cf'] <= 100:
            return None, {'pending': 'invalid_hero_fatigue:' + str(key)}
        fatigue = min(100, hero['cf'] + fatigue_rule['fatigue_recover'])
        if fatigue != hero['cf']:
            hero['cf'] = fatigue
            notices.append(('updateCurFatigueValue', {'h': int(key), 'v': fatigue}))
    city = copy.deepcopy(values)
    city['areas'] = {'area_%s' % key: copy.deepcopy(area) for key, area in areas.items()}
    source_city = copy.deepcopy(city)
    city.update(av=24, bf=values['bf'] + income, dvc=values['dv'], pn=1, uc=False)
    review = {'rsv': values['rv'], 'dvv': values['dv'], 'frv': values['fv']}
    previous = day.get('previous_values', review)
    if not _daily_values(previous):
        return None, {'pending': 'invalid_previous_daily_review'}
    plan = {'source_week': week, 'source_day': current, 'source_date': story['date'],
            'source_city': source_city, 'source_profile': copy.deepcopy(state['profile']),
            'next_day': current + 1, 'condition_date': story['date'] + 1,
            'city': city, 'profile': profile, 'hero_notices': notices,
            'c': review, 'l': copy.deepcopy(previous),
            'evidence': [OFFLINE_DAY_POLICY,
                         'CityData.REC_ACTION_VAL=24; original client capacity used as offline daily refill',
                         'fatigue_recover[week].fatigue_recover; clamp original fatigue to 100',
                         'city_upgrade[(FREE area id,lv)].money_output -> build fund',
                         'Project7 LocalEconomyEngine dailyValues rv/dv/fv and advanceDay reference',
                         'offline DATE policy increments existing condition date independently of stock day']}
    return plan, {'policy': OFFLINE_DAY_POLICY, 'construction_fund_income': income,
                  'fatigue_recovery': fatigue_rule['fatigue_recover'],
                  'automatic_friendship_reward': 0}
