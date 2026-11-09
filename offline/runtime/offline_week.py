# -*- coding: ascii -*-
"""Actual earned endings, route handoffs, and asset-preserving week restarts.

All transitions return whole-state candidates. Commit before stock callbacks.
No timer awards an ending, completes a story, or calls an empty reset success.
"""
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
    from offline_special_city_stage import (apply_special_city_stage_effects,
        validate_special_city_stages, special_city_stage_token,
        refresh_special_city_stages, expire_special_city_stages)
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
    from offline_action_ledger import next_week_action_ledger
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
    from offline_huisu import (huisu_context, huisu_token, validate_huisu_state,
        project_huisu, huisu_notice, huisu_std_projection, huisu_route_projection, expire_huisu_on_route_handoff,
        city_action_context, dream_action_token, authorize_action_admission,
        commit_action_admission, event_execution_admission,
        resolve_event_execution_context, check_dream_contract,
        huisu_trigger_permitted, accept_huisu_event_completion,
        prepare_huisu_operation, mark_huisu_nextday, huisu_day_guard,
        reset_huisu_on_committed_day_or_week)
except ImportError:
    pass

import copy
import base64
import hashlib
import json
import zlib
try:
    from offline_yumi import ensure_yumi, yumi_projection
except ImportError:
    pass

WEEK_POLICY = 'original-basic-week-cycle-v1'
try:
    _wk_text = (basestring,)
except NameError:
    _wk_text = (str,)


def initial_week_state():
    return {'version': 1, 'result': None, 'history': [], 'transition': None,
            'consumed_handoffs': [], 'awaiting_avatar': False}


def _wk_int(value):
    return type(value) is int


def _wk_protocol(state):
    protocol = state.setdefault('week_protocol', initial_week_state())
    validate_week_state(protocol)
    return protocol


def _wk_handoff(state, handoff, content, kind, field):
    event = handoff.get('event')
    row = content.get(event)
    if (handoff.get('kind') != kind or not _wk_int(event) or event not in state.get('completed_events', []) or
            not row or not row.get('release') or field not in row):
        raise ValueError('Week handoff requires an actually completed original source event')
    value = handoff.get('result' if kind == 'week_result' else 'route')
    if value != row[field]:
        raise ValueError('Week handoff does not match original event effect')
    return event, row, value


def prepare_week_result(state, handoff, event_content, ending_catalog):
    candidate = copy.deepcopy(state)
    protocol = _wk_protocol(candidate)
    event, row, ending = _wk_handoff(candidate, handoff, event_content, 'week_result', 'weekResult')
    if not _wk_int(ending) or ending not in ending_catalog:
        raise ValueError('Unknown original ending')
    token = 'ending:%s' % event
    if handoff.get('token') != token:
        raise ValueError('Invalid original ending handoff identity')
    if protocol['result'] is not None:
        if protocol['result']['event'] != event or protocol['result']['ending'] != ending:
            raise ValueError('A different ending already settled this week')
        return copy.deepcopy(state), copy.deepcopy(protocol['result']['notices']), False
    day = candidate.get('day', {}).get('stock_day')
    if not _wk_int(day) or (day < 7 and not row.get('weekResultInAdvance')):
        raise ValueError('Original final day or explicit early-ending effect required')
    story = candidate['story']
    endings = set(story.get('endings', []))
    endings.add(ending)
    story['endings'] = sorted(endings)
    cg = ending_catalog[ending].get('cg')
    cgs = set(story.get('cgs', [])) | set(story.get('cg', []))
    old_cgs = set(cgs)
    if _wk_int(cg) and cg > 0:
        cgs.add(cg)
    story['cgs'] = sorted(cgs)
    story['cg'] = sorted(cgs)  # legacy saved-state compatibility only
    story['new_cgs'] = sorted(set(story.get('new_cgs', [])) | (cgs - old_cgs))
    # Event rewards were already applied by the real source event transaction.
    # No table-backed universal ending currency bonus has been established.
    reward = {'money': 0, 'exp': 0, 'item': [], 'hero': [], 'treasure': []}
    notices = []
    if cgs - old_cgs:
        notices.append(('addCg', {'c': sorted(cgs - old_cgs)}))
    notices.append(('showWeekResult', {'r': ending, 'rd': reward}))
    protocol['result'] = {'week': story['week'], 'event': event, 'ending': ending,
                          'token': token, 'notices': copy.deepcopy(notices),
                          'policy': WEEK_POLICY}
    protocol['consumed_handoffs'].append(token)
    return candidate, notices, True


def prepare_week_route_handoff(state, handoff, event_content, route_catalog):
    candidate = copy.deepcopy(state)
    protocol = _wk_protocol(candidate)
    event, row, route = _wk_handoff(candidate, handoff, event_content, 'route', 'enterStoryRoute')
    token = 'route:%s' % event
    if handoff.get('token') != token or not isinstance(route, _wk_text):
        raise ValueError('Invalid original route handoff')
    allowed = set(route_catalog)
    for definition in route_catalog.values():
        allowed.update(definition.get('routes', ()))
    if route not in allowed:
        raise ValueError('Route is not in original story_route')
    if token in protocol['consumed_handoffs']:
        return copy.deepcopy(state), [], False
    huisu_route_notices = expire_huisu_on_route_handoff(candidate, route)
    expire_daerweila_dispatch(candidate, route)
    provider = candidate['story'].get('city_stage_provider')
    provider_notices = expire_normal_chapters(candidate, route)
    provider_notices.extend(expire_special_city_stages(candidate, route))
    if provider and provider['route'] != route:
        provider_notices.extend(expire_city_stage_provider(candidate))
    candidate['story']['route'] = route
    provider_notices.extend(refresh_city_stage_provider(candidate))
    provider_notices.extend(refresh_special_city_stages(candidate))
    candidate['story']['sub_routes'] = []
    protocol['consumed_handoffs'].append(token)
    flashback_notices = flashback_route_handoff(candidate, event)
    if route.split('-')[0] == '7':
        ensure_yumi(candidate['story'])
        flashback_notices.append(('syncBaiyuInfos', {'d': yumi_projection(candidate['story'])}))
    return candidate, [('syncRoute', {'rt': route, 'srt': [], 'i': False, 'hsd': huisu_route_projection(candidate),
        'fbd': flashback_data(candidate) if candidate['story'].get('route35_flashback') else {}})] + provider_notices + huisu_route_notices + flashback_notices, True


def can_enter_week_route(state, entry, score_catalog):
    """Original StoryMember.canEnterRoute: AND groups of OR ending requirements."""
    if not _wk_int(entry) or entry not in score_catalog:
        return False
    week = state.get('story', {}).get('week')
    if entry == 5:
        return bool(_wk_int(week) and (week >= 3 or week == 2 and
                    state['story'].get('client_event_finish') is False))
    endings = set(state.get('story', {}).get('endings', []))
    return all(any(result in endings for result in group)
               for group in score_catalog[entry].get('requires', []))


def _wk_initial_city(tables, transaction_id):
    building = tables['building'][1]
    if building.get('research_val') != 5 or building.get('force_val') != 5 or building.get('dev_val') != 5:
        raise ValueError('Original Central Court base capacity changed')
    uuid = hashlib.sha256(('week-base:' + transaction_id).encode('utf-8')).hexdigest()[:24]
    def slots(aid):
        return sum(1 for (area, slot), row in tables['development'].items()
                   if area == aid and row['level_require'] <= 1)
    mission = tables['missions'].get(1101)
    if not mission or mission.get('ch') != 2 or mission.get('release') != 1:
        raise ValueError('Original first ordinary school stage missing')
    values = {'dv': 5, 'rv': 5, 'fv': 5, 'av': 24, 'bf': 0, 'ev': 0,
              'dvc': 5, 'pn': 1, 'uc': False, 'tbn': 0, 'tvn': 0, 'tpn': 0}
    areas = {'1': {'id': 1, 'lv': 1, 'st': [0, False, False], 'mbn': slots(1),
                   'bd': {'1': {'id': 1, 'uuid': uuid}}, 'dbd': {}, 'rv': 5, 'fv': 5, 'dv': 5,
                   'stage': {'cs': 0, 'sl': []}},
             '2': {'id': 2, 'lv': 1, 'st': [1, False, False], 'mbn': slots(2),
                   'bd': {}, 'dbd': {}, 'rv': 0, 'fv': 0, 'dv': 0,
                   'stage': {'cs': 1101, 'sl': [[1101]]}}}
    return values, areas


def prepare_week_transition(state, operation, transaction_id, tables, route=None,
                            authorized_reset=False, route_entry=None):
    """Return complete candidate, original reset/inc acknowledgement, changed.

    operations: handleIncWeekAsk, handleResetWeekAsk, requestEnterStoryByEnding.
    Source ending is required for increments. User-authorized restart may abandon
    current story without earning an ending. Both start a new indexed local week;
    this explicit offline policy retains an auditable archive for abandoned weeks.
    """
    if operation not in ('handleIncWeekAsk', 'handleResetWeekAsk', 'requestEnterStoryByEnding', 'requestEnterStory'):
        raise ValueError('Unsupported ordinary week transition')
    if not isinstance(transaction_id, _wk_text) or not transaction_id:
        raise ValueError('Persistent week transaction identity required')
    candidate = copy.deepcopy(state)
    protocol = _wk_protocol(candidate)
    previous = protocol.get('transition')
    if previous and previous['id'] == transaction_id:
        if previous['operation'] != operation:
            raise ValueError('Week identity reused for a different transition')
        return copy.deepcopy(state), copy.deepcopy(previous['notices']), False
    if protocol.get('awaiting_avatar'):
        raise ValueError('Complete original updateClientAvatar handshake before another week transition')
    reset = operation in ('handleResetWeekAsk', 'requestEnterStory')
    if not reset and protocol['result'] is None:
        raise ValueError('Next week requires an actual earned original ending')
    if reset and not authorized_reset:
        raise ValueError('Restart must originate from explicit player reset authorization')
    old_story = candidate['story']
    old_week = old_story.get('week')
    if not _wk_int(old_week) or old_week < 0:
        raise ValueError('Invalid source week')
    entry = route_entry
    if operation in ('requestEnterStory', 'requestEnterStoryByEnding') and not _wk_int(entry):
        raise ValueError('Original route selector requires its real integer entry ID')
    if entry is not None and not can_enter_week_route(candidate, entry, tables['scores']):
        raise ValueError('Original route ending/week requirements are not met')
    target_route = route if route is not None else '1'
    if target_route not in tables['routes']:
        raise ValueError('A starting week route must be an original root route')
    next_week = old_week + 1
    if next_week == 1 and entry in (None, 1):
        initial_event = 1030
    else:
        initial_event = tables['scores'].get(entry or 1, {}).get('init_event')
    content = tables['events'].get(initial_event)
    if not _wk_int(initial_event) or not content or not content.get('release'):
        raise ValueError('Original new-week starting event is missing')
    values, areas = _wk_initial_city(tables, transaction_id)
    item_catalog = tables['items']
    archive = {'week': old_week, 'transition_id': transaction_id, 'operation': operation,
               'abandoned': reset, 'result': copy.deepcopy(protocol['result']),
               'story': copy.deepcopy(old_story), 'conditions': copy.deepcopy(candidate.get('conditions', [])),
               'completed_events': copy.deepcopy(candidate.get('completed_events', [])),
               'processing_events': copy.deepcopy(candidate.get('processing_events', [])),
               'available_events': copy.deepcopy(candidate.get('available_events', [])),
               'event_traces': copy.deepcopy(candidate.get('event_traces', [])),
               'battle': copy.deepcopy(candidate.get('battle')),
               'owned_assets_sha256': hashlib.sha256(json.dumps(candidate.get('profile'), sort_keys=True).encode('utf-8')).hexdigest(),
               'gacha_sha256': hashlib.sha256(json.dumps(candidate.get('gacha'), sort_keys=True).encode('utf-8')).hexdigest()}
    details = {key: archive.pop(key) for key in ('story', 'conditions', 'processing_events',
               'available_events', 'event_traces', 'battle')}
    raw_details = json.dumps(details, sort_keys=True, separators=(',', ':')).encode('utf-8')
    archive['archive_sha256'] = hashlib.sha256(raw_details).hexdigest()
    archive['weekly_archive_zlib_b64'] = base64.b64encode(zlib.compress(raw_details)).decode('ascii')
    protocol['history'].append(archive)
    if isinstance(candidate.get('gacha'), dict):
        inventory = candidate['gacha'].get('items', [])
        cleared = [item for item in inventory if not item.get('tr') and
                   item_catalog.get(item.get('i'), {}).get('clear_inc_week')]
        cleared_ids = set(item['u'] for item in cleared)
        candidate['gacha']['items'] = [item for item in inventory if item['u'] not in cleared_ids]
        archive['cleared_week_items'] = copy.deepcopy(cleared)
    # Permanent collection ownership remains separate from per-week story facts.
    permanent = {key: copy.deepcopy(old_story[key]) for key in
        ('cg', 'cgs', 'endings', 'permanent_unlocks', 'route_unlocks', 'music', 'collections') if key in old_story}
    all_cgs = sorted(set(permanent.get('cgs', [])) | set(permanent.get('cg', [])))
    permanent.update(cgs=all_cgs, cg=all_cgs, new_cgs=[])
    candidate['story'] = dict(permanent, version=1, emergency=True, week=next_week, date=0,
        route=target_route, sub_routes=[], notes={'p': {}, 'n': {}, 'pn': [], 'ppn': False},
        starter_hero=None, starter_source=None, battle_wins=[], blackcores={},
        banned_heroes={}, cine_locked_heroes=[], conquered_heroes=[],
        clues=[], failed_clues=[], clues_read=False, clue_details_read={},
        rely_value=0, support_value=0, yisake_value=0, general_value=0,
        cityMusic=None, cityTheme=None,
        daily_wish=[], daily_wish_hero=0, daily_wish_read=False, daily_wish_generation=0,
        wuluClue=[], wuluClueReaded=False, wuluDetailReaded=[],
        reward_receipts=[], pending_effects={}, city_op_exclam={},
        intelligence={'is':[],'rd':False}, intelligence_sources={}, city_values=values, city_areas=areas)
    # Explicit offline ACTIONAFTEREVENT policy: the week owner resets the
    # action budget, so prior-generation baselines are unprovable.  Carry only
    # observed committed spend into a new generation; an absent/invalid ledger
    # stays unsupported.  Never re-create old baselines or synthesize zero.
    carry = globals().get('next_week_action_ledger')
    if carry is not None:
        carried = carry(old_story.get('action_ledger'))
        if carried is not None:
            candidate['story']['action_ledger'] = carried
    # Restore only weekly fatigue. Hero/skin/treasure/gacha ownership, equipment,
    # awakening, star ranks, friendly values, balances and random draws survive.
    for hero, record in candidate['profile']['heroes'].items():
        maximum = tables['hero'].get(int(hero), {}).get('fatigueValue')
        if not _wk_int(maximum) or maximum < 1:
            raise ValueError('Missing original owned hero maximum fatigue')
        record['cf'] = maximum
        if 'cfd' in record:
            record['cfd'] = False
    candidate['day'] = {'version': 1, 'stock_day': 0, 'intent': None, 'receipt': None, 'review': None}
    candidate['battle'] = {'version': 1, 'active': None, 'receipts': []}
    candidate['city_actions'] = {'version': 1, 'receipts': [], 'patrol': None}
    # Original event-content stay_inc_week is retention metadata. Project7
    # resetProgress intersects actual completions with its original stay catalog;
    # retain only earned events, never grant absent tutorial or future events.
    retained_events = sorted(event for event in candidate.get('completed_events', [])
        if tables.get('events', {}).get(event, {}).get('stay_inc_week'))
    candidate['conditions'], candidate['processing_events'], candidate['completed_events'], candidate['event_traces'] = [], [], retained_events, []
    candidate['available_events'] = [[initial_event, 1]]
    candidate['status'] = 'emergency'
    reply_name = 'handleResetWeekReply' if reset else 'handleIncWeekReply'
    notices = []
    if operation == 'requestEnterStory':
        notices.append(('replyEnterStory', {'r': True}))
    elif operation == 'requestEnterStoryByEnding':
        notices.append(('replyEnterStoryByEnding', {'r': True}))
    notices.append((reply_name, {}))
    protocol['transition'] = {'id': transaction_id, 'operation': operation, 'source_week': old_week,
                               'target_week': next_week, 'initial_event': initial_event,
                               'route_entry': entry, 'notices': copy.deepcopy(notices)}
    protocol['result'], protocol['consumed_handoffs'] = None, []
    protocol['awaiting_avatar'] = True
    if tables.get('chapter_mission_data'):
        notices.extend(refresh_normal_chapters(candidate, dict(tables, mission=tables.get('missions', {}), event_content=tables.get('events', {}))))
    return candidate, notices, True



def _wk_identity(value):
    return value.get('$oid') if isinstance(value, dict) and '$oid' in value else str(value)


def _wk_city_identity_form(value):
    # Only actual building identity fields differ at the native boundary.
    # All costs, statuses, flags (including building20.u), levels and stages
    # retain their exact values and types for the same-generation comparison.
    if isinstance(value, dict):
        return {key: (_wk_identity(item) if key == 'uuid' else _wk_city_identity_form(item))
                for key, item in value.items()}
    if isinstance(value, list):
        return [_wk_city_identity_form(item) for item in value]
    if isinstance(value, tuple):
        return tuple(_wk_city_identity_form(item) for item in value)
    return value



def _wk_skin_identity_form(skins):
    if not isinstance(skins, dict):
        return skins
    normalized = {}
    for key, value in skins.items():
        native = copy.deepcopy(value)
        if isinstance(native, dict) and 'u' in native:
            native['u'] = _wk_identity(native['u'])
        normalized[_wk_identity(key)] = native
    return normalized


def validate_full_week_avatar(snapshot, state):
    """Reject a partial success document before attempting native reconstruction."""
    required = ('st', 'name', 'an', 'uid', 'sv', 'role', 'level', 'money', 'exp',
                'weeknum', 'city', 'heromgr', 'inv', 'std', 'eventTrigger', 'np', 'cgs', 'ldd')
    if not isinstance(snapshot, dict) or any(key not in snapshot for key in required):
        raise ValueError('Week avatar must be a full realized original avatar snapshot')
    story = state['story']
    if (snapshot['weeknum'].get('w') != story['week'] or snapshot['weeknum'].get('d') != state['day']['stock_day'] or
            snapshot['std'].get('rt') != story['route'] or
            snapshot['city'].get('av') != story['city_values']['av'] or
            _wk_city_identity_form(snapshot['city'].get('areas')) != _wk_city_identity_form({'area_%s' % key: value for key, value in story['city_areas'].items()})):
        raise ValueError('Full avatar must represent the same committed new-week state')
    active_heroes = dict(snapshot['heromgr'].get('hrs', []))
    banned_heroes = dict(snapshot['heromgr'].get('bhrs', []))
    if set(active_heroes).intersection(banned_heroes):
        raise ValueError('Full avatar duplicated a hero across active and banned groups')
    native_heroes = dict(list(active_heroes.items()) + list(banned_heroes.items()))
    if state['story'].get('cine_locked_heroes') == [] and snapshot['heromgr'].get('c', []):
        raise ValueError('Full avatar retained a prior week cinematic hero lock')
    if set(str(hero) for hero in native_heroes) != set(state['profile']['heroes']):
        raise ValueError('Full avatar dropped owned heroes')
    for key, saved in state['profile']['heroes'].items():
        native = native_heroes[int(key)]
        if any(native.get(field) != saved[field] for field in ('sl', 'so', 'cf', 'ef', 'ar', 'as') if field in saved):
            raise ValueError('Full avatar altered owned hero or costume progression')
        if 'sk' in saved and _wk_skin_identity_form(native.get('sk')) != _wk_skin_identity_form(saved['sk']):
            raise ValueError('Full avatar changed owned costume identity or data')
        if 'cs' in saved and _wk_identity(native.get('cs')) != _wk_identity(saved['cs']):
            raise ValueError('Full avatar changed the selected owned costume')
        if 'lncs' in saved and _wk_identity(native.get('lncs')) != _wk_identity(saved['lncs']):
            raise ValueError('Full avatar changed the selected owned live costume')
        native_equipment = [_wk_identity(item['u']) for item in native.get('ti', {}).get('items', [])]
        saved_equipment = [_wk_identity(item['u']) for item in saved.get('ti', {}).get('items', [])]
        if native_equipment != saved_equipment:
            raise ValueError('Full avatar changed equipped treasure identities')
    if not (set(story.get('cgs', [])) | set(story.get('cg', []))).issubset(set(snapshot['cgs'])) or not set(story.get('endings', [])).issubset(set(snapshot['std'].get('ed', []))):
        raise ValueError('Full avatar dropped permanent earned CG or endings')
    economy = state['profile'].get('economy', {})
    if any(snapshot.get(key) != economy[key] for key in ('money', 'exp', 'level') if key in economy):
        raise ValueError('Full avatar changed persistent player balances')
    owned_items = list(state['profile'].get('treasures', {}).get('items', [])) + list((state.get('gacha') or {}).get('items', []))
    required_ids = set(_wk_identity(item['u']) for item in owned_items)
    native_ids = set(_wk_identity(item['u']) for item in snapshot['inv'].get('items', []))
    gacha = (state.get('gacha_pools') or {}).get('pools', {}).get('1') or state.get('gacha')
    if gacha and (snapshot['ldd'].get('ct') != gacha.get('opened_total', 0) or
                  bool(snapshot['ldd'].get('iof')) != (gacha.get('group') is not None)):
        raise ValueError('Full avatar dropped original gacha draw count or active group')
    native_inventory = {_wk_identity(item['u']): item for item in snapshot['inv'].get('items', [])}
    for item in owned_items:
        native_item = native_inventory.get(_wk_identity(item['u']))
        if native_item is not None and any(native_item.get(field) != item[field] for field in ('i', 'tr') if field in item):
            raise ValueError('Full avatar changed an owned inventory template or treasure progression')
        if native_item is not None and 'w' in item and native_item.get('w') != item['w']:
            raise ValueError('Full avatar changed an owned inventory quantity')
    if not required_ids.issubset(native_ids):
        raise ValueError('Full avatar dropped owned treasure or gacha inventory')
    if set(snapshot['eventTrigger'].get('ecm', [])) != set(state.get('completed_events', [])):
        raise ValueError('Full avatar invented or dropped completed story facts')
    return True


def prepare_week_avatar_reply(state, snapshot_builder, packb):
    """Actual original zlib/msgpack adapter, using gateway's realized template.

    builder receives the whole committed canonical state and overlays its native
    ObjectId/roster/inventory/CG/gacha data onto the complete realized template.
    packb must be original-compatible msgpack encoding, with native ExtendedJSON
    conversion supplied by gateway for ObjectId. Bytes are never persisted in JSON.
    """
    candidate = copy.deepcopy(state)
    protocol = _wk_protocol(candidate)
    snapshot = snapshot_builder(copy.deepcopy(candidate))
    validate_full_week_avatar(snapshot, candidate)
    packed = packb(snapshot)
    if not isinstance(packed, bytes) or not packed:
        raise ValueError('Original msgpack encoder must return nonempty bytes')
    wire = zlib.compress(packed)
    changed = bool(protocol.get('awaiting_avatar'))
    protocol['awaiting_avatar'] = False
    return candidate, [('updateClientAvatarReply', {'s': wire})], changed


def read_week_history(entry):
    """Decode a lossless weekly audit archive without duplicating owned assets."""
    if 'weekly_archive_zlib_b64' not in entry:
        return copy.deepcopy(entry)
    raw = zlib.decompress(base64.b64decode(entry['weekly_archive_zlib_b64'].encode('ascii')))
    if hashlib.sha256(raw).hexdigest() != entry.get('archive_sha256'):
        raise ValueError('Week history audit checksum mismatch')
    result = copy.deepcopy(entry)
    result.update(json.loads(raw.decode('utf-8')))
    return result


def validate_week_state(protocol):
    if (not isinstance(protocol, dict) or protocol.get('version') != 1 or
            not isinstance(protocol.get('history'), list) or
            not isinstance(protocol.get('consumed_handoffs'), list) or
            type(protocol.get('awaiting_avatar')) is not bool):
        raise ValueError('Invalid persisted week protocol')
    result = protocol.get('result')
    if result is not None and (not isinstance(result, dict) or
            any(not _wk_int(result.get(key)) for key in ('week', 'event', 'ending')) or
            not isinstance(result.get('notices'), list) or not result['notices'] or
            result['notices'][-1][0] != 'showWeekResult'):
        raise ValueError('Invalid persisted earned week result')
    transition = protocol.get('transition')
    if transition is not None and (not isinstance(transition, dict) or
            not isinstance(transition.get('id'), _wk_text) or not transition['id'] or
            not _wk_int(transition.get('source_week')) or
            transition.get('target_week') != transition['source_week'] + 1 or
            not isinstance(transition.get('notices'), list)):
        raise ValueError('Invalid persisted week transition receipt')
    if protocol['awaiting_avatar'] and transition is None:
        raise ValueError('Avatar handshake must belong to a committed transition')
