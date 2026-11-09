# -*- coding: ascii -*-
"""Atomic original-table event effects. No game imports, timers, saves or completion.

Offline policy: deterministic minimum treasure rolls; duplicate owned heroes and
skins remain owned rather than being converted to invented fragment rewards.
Original client callbacks are mandatory for UI/puzzle/movie/route/ending effects.
"""
try:
    from offline_chapter_campaign import (resolve_normal_chapter, refresh_normal_chapters,
        normal_chapter_token, validate_normal_chapters, expire_normal_chapters,
        revoke_normal_chapter_projection, stage_projection_owner, normal_chapter_event_replacements, mark_normal_chapter_activation)
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
        expire_city_stage_provider, city_stage_provider_pending_source)
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
    from offline_battle_terminal import resolve_winning_party_fatigue
except ImportError:
    pass

import copy
import hashlib
try:
    from offline_yumi import apply_yumi_event, yumi_projection
    from offline_route_agreements import (AGREEMENT_VALUES, apply_route_agreement,
        project_route_agreements)
except ImportError:
    pass
try:
    from offline_stage import current_mission_wins, refresh_condition_city_missions
    from offline_intelligence import build_event_intelligence, intelligence_sync_notice
except ImportError:
    pass

try:
    _event_text = (basestring,)
except NameError:
    _event_text = (str,)

EVENT_METADATA = frozenset(('name', 'release', 'eventType', 'repeatable',
    'priority', 'priorityGroup', 'completeConds', 'completeEnterMainPanel',
    'isAutoTriggerEvent', 'emergencyEvent', 'isEmergencyEvent', 'dialog',
    'events', 'mutexEvent', 'autoStart', 'rel_heroes', 'patrolEvent', 'newbee',
    'newbee_event', 'client_event', 'city_attention', 'stay_inc_week'))
EVENT_EFFECT_FIELDS = frozenset(('dream_id', 'notepadId', 'rewards', 'isLeaveEmergencyEvent',
    'areaFight', 'areaFree', 'areaFall', 'areaUnlock', 'areaLock', 'areaStrike',
    'areaCR7', 'areaSpecialStage', 'changeBlackcore', 'batchChangeBlackcore',
    'ban_heroes', 'recoverBanHeroes', 'cineLockHeroes', 'gonglueHeroes',
    'huohaihua', 'completeRouteTarget', 'cityMusic', 'cityTheme',
    'enterStoryRoute', 'weekResult', 'weekResultInAdvance',
    'daily_wish', 'privateMsgId', 'socialMsgId', 'procClue', 'procFailClue',
    'gainBaiyuVal', 'gainRelyVal', 'gainSupportVal', 'gainYisakeVal', 'getCenterConfidence', 'buildBuilding', 'exclam', 'destroyPatrolBuild', 'destroyAreaPatrolBuild', 'refreshMission', 'abandonMission', 'complete_newbee_patrol', 'intelligence'))
EVENT_CALLBACK_FIELDS = {'ui': 'ui', 'movie': 'movie', 'puzzle_room': 'puzzle',
    'enter_caidan': 'caidan', 'enter_huodong': 'activity', 'contentFinishUI': 'ui',
    'enterBattle': 'battle', 'contentFinishBattle': 'battle'}
REWARD_METADATA = frozenset(('id', 'tradeType', 'award_pool'))
REWARD_EFFECT_FIELDS = frozenset(('hero', 'skin', 'init_skin', 'friends', 'fatigue',
    'cg', 'items', 'itemsNum', 'money', 'crystal', 'friendcoin', 'summoncoin',
    'buildFund', 'treasure', 'treasureNum', 'treasureLevel', 'buildableBuilding',
    'destroyBuliding'))


def classify_event_effects(row):
    keys = set(row)
    agreement = row.get('special_agreement')
    if isinstance(agreement, _event_text) and (agreement == 'enter_flashback' or agreement in AGREEMENT_VALUES):
        keys.discard('special_agreement')
    return {'metadata': sorted(keys & EVENT_METADATA),
            'effects': sorted(keys & EVENT_EFFECT_FIELDS),
            'callbacks': sorted(keys & set(EVENT_CALLBACK_FIELDS)),
            'unsupported_fields': sorted(keys - EVENT_METADATA - EVENT_EFFECT_FIELDS - set(EVENT_CALLBACK_FIELDS))}


def _int(value, label):
    if type(value) is not int:
        raise ValueError('%s requires an integer' % label)
    return value


def _ids(value, label):
    if not isinstance(value, (list, tuple, set)) or any(type(v) is not int for v in value):
        raise ValueError('%s requires original integer IDs' % label)
    return list(value)


def _unique_add(values, value):
    if value not in values:
        values.append(value)


def _stable_id(key, occupied):
    for attempt in range(100):
        uid = hashlib.sha256(('%s:%d' % (key, attempt)).encode('utf-8')).hexdigest()[:24]
        if uid not in occupied:
            occupied.add(uid)
            return uid
    raise ValueError('Deterministic item ObjectId collision')


def _default_area(area_id, tables):
    if area_id not in tables.get('city_data', {}):
        raise ValueError('Missing original city_data area %s' % area_id)
    missions = tables.get('mission', {})
    rows = {i: r for i, r in missions.items() if r.get('ch') == area_id
            and r.get('system_type') == 1 and r.get('type') == 7
            and r.get('release', 1)}
    targets = set(i for r in rows.values() for i in r.get('nextstagenums', ()) if i in rows)
    roots = sorted(set(rows) - targets)
    result = {'id': area_id, 'st': [2, False, False], 'lv': 1, 'bd': {}}
    if roots:
        # Table-derived offline policy: first released graph root, never a
        # mission from a different area. Preserve advanced stages on re-entry.
        result['stage'] = {'cs': roots[0], 'sl': [[roots[0]]]}
    return result


def _callbacks_needed(event, row, state, context):
    observed = set(context.get('completed_callbacks', ()))
    needed = []
    for field, kind in sorted(EVENT_CALLBACK_FIELDS.items()):
        value = row.get(field)
        if not value:
            continue
        if kind == 'battle':
            scenes = value if isinstance(value, (tuple, list, set)) else [value]
            for scene in scenes:
                token = 'battle:%s' % scene
                if token not in observed and (field == 'enterBattle' or
                        scene not in state.get('story', {}).get('battle_wins', [])):
                    needed.append({'token': token, 'field': field, 'value': scene,
                                   'source': 'accepted actual combat finish, never client trace'})
        else:
            token = '%s:%s' % (kind, event)
            if token not in observed:
                needed.append({'token': token, 'field': field, 'value': copy.deepcopy(value),
                               'source': 'original client completion callback'})
    # Deduplicate shared UI/battle requirement fields without losing provenance.
    return list({item['token']: item for item in needed}.values())



def _event_city_capacities(story, catalog, hero_count):
    """Original CityBuildings base/synergy rules, without executing game code."""
    areas, totals = {}, {'fv': 0, 'rv': 0, 'dv': 0}
    for key, current in story.get('city_areas', {}).items():
        value = {'fv': 0, 'rv': 0, 'dv': 0}
        if current.get('st', [2])[0] == 0:
            ids = [building['id'] for building in current.get('bd', {}).values()]
            for field, source, district, multiplier, perhero in (
                    ('fv','force_val',3,5,6), ('rv','research_val',8,10,11),
                    ('dv','dev_val',13,15,16)):
                amount = sum(catalog.get(bid, {}).get(source, 0) for bid in ids)
                producers = sum(bool(catalog.get(bid, {}).get(source, 0) > 0 or bid == perhero) for bid in ids)
                amount += ids.count(district) * producers + ids.count(perhero) * min(30, hero_count)
                for unused in range(ids.count(multiplier)): amount = (amount * 3 + 1) // 2
                value[field] = amount
                totals[field] += amount
        areas[key] = value
    return areas, totals


def _event_refresh_selected_missions(story, missions):
    """Refresh existing selected area stage lists, never all routes or wins."""
    abandoned, wins = set(story.get('abandoned_missions', [])), set(story.get('battle_wins', []))
    changed, notices = [], []
    for key, current in story.get('city_areas', {}).items():
        if 'stage' not in current: continue
        area_id = int(key)
        old = copy.deepcopy(current['stage'])
        stage = old or {'cs': 0, 'sl': []}
        groups = []
        for group in stage.get('sl', []):
            values = []
            for scene in group:
                mission = missions.get(scene)
                if scene not in abandoned and mission and mission.get('ch') == area_id and mission.get('release', 1):
                    values.append(scene)
            if values: groups.append(values)
        flat = [scene for group in groups for scene in group]
        selected = stage.get('cs', 0)
        if selected not in flat or selected in wins:
            selected = next((scene for scene in flat if scene not in wins), 0)
        current['stage'] = {'cs': selected, 'sl': groups}
        if old != current['stage']: changed.append(area_id)
        notices.append(('get_area_stages_reply', {'ai': area_id, 'st': copy.deepcopy(current['stage'])}))
    return changed, notices

def plan_event_effects(state, event_id, event_catalog, tables=None, context=None):
    """Return (candidate, notices, diagnostic), with atomic failure semantics.

    Does not add completed_events or activate successors. Call after original
    dialogue/option/completeConds proof. context.completed_callbacks uses strings
    ui:<event>, puzzle:<event>, movie:<event>, route:<event>, ending:<event> and
    battle:<scene>. receipt_key identifies an occurrence across reload/retries.
    tables are original literal catalogs, not arbitrary behavior providers.
    """
    tables, context = tables or {}, context or {}
    row = event_catalog.get(event_id)
    diag = {'event': event_id, 'ready': False, 'status': 'unsupported',
            'unsupported_fields': [], 'pending_callbacks': [], 'policies': []}
    if not row:
        diag['reason'] = 'event is absent from original catalog'
        return copy.deepcopy(state), [], diag
    classification = classify_event_effects(row)
    diag.update(classification)
    diag['pending_callbacks'] = _callbacks_needed(event_id, row, state, context)
    if classification['unsupported_fields']:
        diag['reason'] = 'original effect field requires an explicit implementation'
        return copy.deepcopy(state), [], diag
    if diag['pending_callbacks']:
        diag['status'] = 'waiting'
        return copy.deepcopy(state), [], diag
    candidate = copy.deepcopy(state)
    story = candidate.setdefault('story', {})
    receipt = str(context.get('receipt_key', event_id))
    ledger = story.setdefault('event_effect_receipts', {})
    if receipt in ledger:
        if ledger[receipt] != event_id:
            diag['reason'] = 'receipt key belongs to a different event'
            return copy.deepcopy(state), [], diag
        diag.update(ready=True, status='already-applied')
        return candidate, [], diag
    execution = resolve_event_execution_context(candidate, receipt, row, tables)
    if ((receipt in story.get('event_contexts', {}) and execution is None) or
            not check_dream_contract(row, execution)):
        diag.update(status='waiting', reason='actual_compatible_dream_occurrence_required')
        return copy.deepcopy(state), [], diag
    if 'dream_id' in row:
        diag['policies'].append('offline-route20-dream-context-v1' if execution['kind'] == 'route20_huisu' else 'existing-route35-flashback-context')
        diag['execution_context'] = execution
        story.setdefault('event_context_audit', {})[receipt] = copy.deepcopy(execution)
    notices, item_updates, added_cgs, reward = [], [], [], {}
    affected_areas = set()
    heroes = (candidate.get('profile') or {}).get('heroes', {})

    def hero(hid):
        value = heroes.get(str(hid))
        if value is None:
            raise ValueError('Missing owned original hero %s; no fabricated snapshot' % hid)
        return value

    def cg(cg_id):
        definition = tables.get('cg_data', {}).get(cg_id)
        if definition is None:
            raise ValueError('Missing original CG %s' % cg_id)
        if definition.get('skip'):
            return
        values = story.setdefault('cgs', [])
        if cg_id not in values:
            values.append(cg_id)
            _unique_add(story.setdefault('new_cgs', []), cg_id)
            added_cgs.append(cg_id)

    def area(aid):
        _int(aid, 'area')
        values = story.setdefault('city_areas', {})
        if str(aid) not in values:
            values[str(aid)] = _default_area(aid, tables)
        affected_areas.add(aid)
        current = values[str(aid)]
        if not isinstance(current.get('st'), (list, tuple)) or len(current['st']) != 3:
            raise ValueError('Invalid saved native area status')
        current['st'] = list(current['st'])
        return current

    def inventory_item(template, quantity, source):
        catalog = tables.get('item_data', {})
        if template not in catalog:
            raise ValueError('Missing original inventory template %s' % template)
        _int(quantity, 'item quantity')
        if template == 13624:
            definition = catalog[template]
            if str(story.get('route')) not in ('31','31-4') or definition.get('type') != 8 or definition.get('subtype') != 82 or definition.get('virtual_sub_type') != 82:
                raise ValueError('Unsupported original virtual bounty reward outside verified route31 scope')
            before = _int(story.get('general_value',0),'route31 general value')
            after = before + quantity
            if before < 0 or after < 0:
                raise ValueError('Insufficient route31 bounty balance')
            story['general_value'] = after
            story.setdefault('general_value_reward_receipts',{}).setdefault(receipt,[]).append({
                'event':event_id,'reward':source,'item':template,'amount':quantity,
                'before':before,'after':after,'route':str(story['route']),
                'policy':'offline-original-route31-virtual82-to-general-value-v1'})
            notices.append(('syncStoryGeneralValue',{'v':after}))
            # Original reward presentation keeps the virtual item icon/quantity;
            # it is never credited as an ordinary persistent inventory stack.
            reward.setdefault('item',[]).append([template,quantity])
            diag['policies'].append('offline finite route31 virtual82 bounty converts to StoryData.gr; no inventory credit or legacy inventory migration')
            return
        if 'gacha' not in candidate or not isinstance(candidate['gacha'].get('items'), list):
            raise ValueError('Missing persistent common inventory (gacha.items)')
        values = candidate['gacha']['items']
        item = next((i for i in values if i['i'] == template and not i.get('tr')), None)
        if item is None:
            if quantity < 0:
                raise ValueError('Insufficient inventory for event debit')
            occupied = set(i['u'] for i in values)
            item = {'i': template, 'u': _stable_id('event-item:%s:%s' % (receipt, template), occupied),
                    'w': 0, 'c': 0, 'ctt': 0, 'tt': 0, 'le': 0, 'lo': None, 'ele': 0}
            values.append(item)
        if item['w'] + quantity < 0:
            raise ValueError('Insufficient event item balance')
        item['w'] += quantity
        item_updates.append(copy.deepcopy(item))
        if item['w'] == 0:
            values.remove(item)
        reward.setdefault('item', []).append([template, quantity])

    def treasure(template, quantity, quality, trade_type, reward_id):
        definition = tables.get('hero_treasure', {}).get((template, quality))
        indices = tables.get('attr_indices', {})
        if definition is None or template not in tables.get('item_data', {}):
            raise ValueError('Missing original treasure/class metadata')
        if type(quantity) is not int or not 0 <= quantity <= 100:
            raise ValueError('Invalid event treasure count')
        values = candidate['profile'].get('treasures', {}).get('items')
        if not isinstance(values, list):
            raise ValueError('Missing persistent treasure inventory')
        attrs = []
        for field, prefix in (('secondAttrs', 'f'), ('thridAttrs', 't')):
            for name, limits in sorted(definition.get(field, {}).items()):
                if name not in indices or len(limits) != 2:
                    raise ValueError('Missing original treasure attribute index/range')
                attrs.append({'n': prefix + str(indices[name]), 'v': limits[0]})
        if not attrs:
            raise ValueError('Refusing attribute-less event treasure')
        occupied = set(i['u'] for i in values)
        granted_ids = []
        for index in range(quantity):
            uid = _stable_id('event-treasure:%s:%s:%s:%s:%s' %
                (receipt, reward_id, template, quality, index), occupied)
            item = {'i': template, 'u': uid, 'w': 1, 'c': 0, 'ctt': 0, 'tt': trade_type,
                    'tr': {'cl': quality, 'lv': 1, 'x': 0, 'f': False,
                           'ft': list(definition.get('fixTrick', ())), 'attr': attrs,
                           'era': [], 'su': []}}
            values.append(item)
            granted_ids.append(uid)
            item_updates.append(copy.deepcopy(item))
        reward.setdefault('treasure', []).append([template, quality, quantity, granted_ids])
        diag['policies'].append('event treasures use original class attribute minima, level1; deterministic stable IDs')

    try:
        if 'complete_newbee_patrol' in row:
            if _int(row['complete_newbee_patrol'], 'complete_newbee_patrol') != 1:
                raise ValueError('Unknown original tutorial patrol completion flag')
            protocol = candidate.get('city_actions') or {}
            patrol = protocol.get('patrol') or {}
            admission = patrol.get('admission_id')
            day = candidate.get('day', {}).get('stock_day', story.get('date'))
            if (not admission and patrol.get('area') == 1 and patrol.get('selected') == event_id and
                    story.get('week') == 0 and day == 0):
                legacy = [saved for saved in protocol.get('receipts', []) if any(name == 'enter_patrol_reply' and
                    payload.get('s') and event_id in payload.get('ev', []) for name,payload in saved.get('notices', []))]
                if len(legacy) == 1:
                    admission = legacy[0]['id']
                    patrol.update(admission_id=admission,week=0,day=0)
                    diag['policies'].append('legacy active first-week patrol is bound to its unique saved original admission receipt')
            admitted = any(saved.get('id') == admission and any(name == 'enter_patrol_reply' and
                payload.get('s') and event_id in payload.get('ev', []) for name,payload in saved.get('notices', []))
                for saved in protocol.get('receipts', []))
            if (not admission or not admitted or patrol.get('area') != 1 or patrol.get('selected') != event_id or
                    event_id not in patrol.get('events', []) or not patrol.get('heroes') or
                    any(str(hid) not in heroes for hid in patrol['heroes']) or
                    story.get('week') != 0 or day != 0 or patrol.get('week') != 0 or patrol.get('day') != 0):
                raise ValueError('Missing actual first-week central-court selected patrol admission')
            story.setdefault('tutorial_patrol_receipts', {})[receipt] = {
                'event':event_id, 'admission_id':admission, 'area':1,
                'heroes':list(patrol['heroes']), 'week':0, 'day':0}
            diag['policies'].append('tutorial patrol completion records real selected original admission; caller alone completes event and clears patrol')
        if 'daily_wish' in row:
            if not isinstance(row['daily_wish'],(list,tuple)):raise ValueError('Original daily wish requires an ordered list')
            wishes=_ids(row['daily_wish'],'daily_wish')
            catalog=tables.get('daily_wish',{})
            if not wishes or any(wish not in catalog for wish in wishes):
                raise ValueError('Missing original daily wish definition')
            validate_daily_wish(story,catalog)
            story['daily_wish']=wishes
            story['daily_wish_read']=False
            story.setdefault('daily_wish_hero',0)
            story['daily_wish_generation']=story.get('daily_wish_generation',0)+1
            story['daily_wish_source']={'event':event_id,'receipt':receipt,'policy':'offline-current-letter-replacement-v1'}
            notices.append(daily_wish_notice(story))
            diag['policies'].append('daily wish text replaces current letter; ordinary day retains it, new week resets; no action/award/hero-clear implied')
        # Validate reward schemas before changing any candidate state. All later
        # errors still discard candidate/notices as a whole.
        rewards = []
        for rid in _ids(row.get('rewards', ()), 'rewards'):
            definition = tables.get('reward_common', {}).get(rid)
            if definition is None:
                raise ValueError('Missing original reward %s' % rid)
            unknown = set(definition) - REWARD_METADATA - REWARD_EFFECT_FIELDS
            if unknown:
                diag['unsupported_fields'] = ['reward.%s' % k for k in sorted(unknown)]
                raise ValueError('Unsupported original reward fields')
            rewards.append((rid, definition))
        # Native notebook data: original type1 player journal, type2/3 hero.
        for note in _ids(row.get('notepadId', ()), 'notepadId'):
            definition = tables.get('notepad', {}).get(note)
            if not definition:
                raise ValueError('Missing original notebook entry %s' % note)
            notes = story.setdefault('notes', {'p': {}, 'n': {}, 'pn': [], 'ppn': False})
            if definition.get('type') == 1:
                _unique_add(notes['pn'], note)
                if not definition.get('no_new'):
                    notes['ppn'] = True
            elif definition.get('type') in (2, 3) and definition.get('heroId'):
                hid = str(definition['heroId'])
                _unique_add(notes['n'].setdefault(hid, []), note)
                if not definition.get('no_new'):
                    _unique_add(notes['p'].setdefault(hid, []), note)
                if definition.get('clear'):
                    _unique_add(story.setdefault('completed_hero_notes', []), note)
                    diag['policies'].append('clear notebook flag records finished hero note; journal history retained')
            else:
                raise ValueError('Unsupported original notebook type')
            for cid in definition.get('cg', ()):
                cg(cid)
        if row.get('notepadId'):
            notices.append(('syncAllNote', {'nd': copy.deepcopy(story['notes'])}))
        for field, storage, table, notice in (('privateMsgId','pm','private_msg','syncOnePrivateMsg'),
                ('socialMsgId','sm','social_msg','syncOneSocialMsg')):
            for mid in _ids(row.get(field, ()), field):
                definition = tables.get(table, {}).get(mid)
                if not definition: raise ValueError('Missing original %s %s' % (table, mid))
                values = story.setdefault('social', {'pm': {}, 'sm': {}})[storage]
                key = str(mid)
                if key not in values:
                    timestamp = context.get('timestamp', 0)
                    _int(timestamp, 'notification timestamp')
                    if storage == 'pm':
                        values[key] = {'id': mid, 'rd': False, 'rp': False, 'rt': timestamp}
                    else:
                        values[key] = {'id': mid, 'r': False, 'to': None,
                            'e': definition.get('event', 0), 'l': [], 'rt': timestamp, 'ct': 0, 'a': False}
                    notices.append((notice, {'id': mid, 'c': copy.deepcopy(values[key])}))
                    diag['policies'].append('offline message retained until explicit read/expire/reset; never auto-trigger its event')
        clue_changed = False
        for field, target in (('procClue','clues'), ('procFailClue','failed_clues')):
            for clue in _ids(row.get(field, ()), field):
                if clue not in tables.get('story_clue_info', {}):
                    raise ValueError('Missing original story clue %s' % clue)
                _unique_add(story.setdefault(target, []), clue)
                clue_changed = True
        if clue_changed:
            story['clues_read'] = False
            notices.append(('syncClueInfo', {'cl': list(story.get('clues', [])),
                'cr': False, 'dr': list(story.get('clue_details_read', {}).items()),
                'fc': list(story.get('failed_clues', [])), 'ie': False}))
        line_changed = False
        for field, target in (('gainRelyVal','rely_value'), ('gainSupportVal','support_value')):
            if field in row:
                story[target] = story.get(target, 0) + _int(row[field], field)
                line_changed = True
        if line_changed:
            notices.append(('syncSailafeimuLineData', {'srv': story.get('rely_value',0),
                'ssv': story.get('support_value',0), 'u': True}))
        notices.extend(apply_yumi_event(story, event_id, row))
        if row.get('special_agreement') in AGREEMENT_VALUES:
            notices.extend(apply_route_agreement(story, event_id, row,
                context.get('native_story_seed')))
        if 'gainYisakeVal' in row:
            delta = _int(row['gainYisakeVal'], 'gainYisakeVal')
            story['yisake_value'] = story.get('yisake_value',0) + delta
            notices.append(('syncYisakeVal', {'iv': story['yisake_value'], 'av': delta}))
        if 'getCenterConfidence' in row:
            values = story.setdefault('city_values', {})
            delta = _int(row['getCenterConfidence'], 'getCenterConfidence')
            values['cc'] = values.get('cc',0) + delta
            notices.append(('addCenterConfidence', {'v': delta, 'c': values['cc']}))
        actual_normal = (candidate.get('battle') or {}).get('active') or {}
        explicit_area_writes = set()
        for field in ('areaFight','areaFall','areaFree','areaStrike','areaLock','areaUnlock','areaCR7'):
            explicit_area_writes.update(_ids(row.get(field,()),field))
        if actual_normal.get('normal_chapter_source') and actual_normal['request']['d']['a'] in explicit_area_writes:
            raise ValueError('Actual normal fight blocks original area status/lock replacement')
        mark_normal_chapter_activation(candidate,event_id,row,receipt)
        for field, status in (('areaFight', 1), ('areaFall', 2), ('areaFree', 0), ('areaStrike', 5)):
            for aid in _ids(row.get(field, ()), field):
                current = area(aid)
                current['st'][0] = status
        for field, locked in (('areaUnlock', False), ('areaLock', True)):
            for aid in _ids(row.get(field, ()), field):
                area(aid)['st'][2] = locked
        for aid in _ids(row.get('areaCR7', ()), 'areaCR7'):
            current = area(aid)
            current['st'][1] = True
            current['st'][0] = 4 if current['st'][0] == 2 else 3
        for aid in row.get('areaSpecialStage', {}):
            # Original values select chapter_mission_data, never mission IDs.
            area(aid)
        if 'exclam' in row:
            if not isinstance(row['exclam'], dict):
                raise ValueError('Invalid original operation exclamation map')
            counters = story.setdefault('city_op_exclam', {})
            for operation, specification in sorted(row['exclam'].items()):
                if not isinstance(operation, _event_text) or not isinstance(specification, (tuple, list)):
                    raise ValueError('Invalid original operation exclamation entry')
                entries = [specification] if len(specification) == 2 and type(specification[0]) is int else specification
                for entry in entries:
                    if not isinstance(entry, (tuple, list)) or len(entry) != 2:
                        raise ValueError('Invalid original operation exclamation pair')
                    aid, delta = entry
                    _int(aid, 'exclamation area'); _int(delta, 'exclamation delta')
                    if aid != 0 and aid not in tables.get('city_data', {}):
                        raise ValueError('Missing original exclamation area')
                    targets = sorted(tables.get('city_data', {})) if aid == 0 else [aid]
                    if not targets:
                        raise ValueError('Missing original all-area exclamation catalog')
                    if aid == 0:
                        diag['policies'].append('offline policy: area0 expands original city_data IDs; add signed delta per named operation, preserve negative counts')
                    for target in targets:
                        values = counters.setdefault(str(target), {})
                        values[operation] = _int(values.get(operation, 0), 'saved exclamation count') + delta
            notices.append(('syncOpExclam', {'d': copy.deepcopy(counters)}))
        destroy_pairs = []
        if row.get('destroyPatrolBuild'):
            patrol = (candidate.get('city_actions') or {}).get('patrol')
            if not patrol or patrol.get('selected') != event_id or event_id not in patrol.get('events', []):
                raise ValueError('Missing actual selected patrol context for building removal')
            destroy_pairs.extend((patrol['area'], bid) for bid in _ids(row['destroyPatrolBuild'], 'destroyPatrolBuild'))
        for pair in row.get('destroyAreaPatrolBuild', ()):
            if not isinstance(pair, (tuple, list)) or len(pair) != 2:
                raise ValueError('Invalid original area building removal pair')
            destroy_pairs.append(tuple(pair))
        for aid, bid in destroy_pairs:
            _int(aid, 'removed building area'); _int(bid, 'removed building ID')
            if aid not in tables.get('city_data', {}) or bid not in tables.get('city_building', {}):
                raise ValueError('Missing original area/building removal catalog')
            current = story.get('city_areas', {}).get(str(aid))
            if current is None:
                continue
            for slot, building in list(current.get('bd', {}).items()):
                if isinstance(building, dict) and building.get('id') == bid:
                    del current['bd'][slot]
                    current.setdefault('dbd', {})[str(slot)] = bid
                    affected_areas.add(aid)
                    notices.append(('area_building_destroy', {'aid': aid, 'bid': bid}))
            diag['policies'].append('offline removal policy: delete only actual matching buildings in original target area; absent target is no-op, keep destroyed-slot tombstone')
        for aid, specification in row.get('buildBuilding', {}).items():
            if not isinstance(specification, (list, tuple)) or len(specification) != 2:
                raise ValueError('Invalid original event building specification')
            building, count = specification
            _int(building, 'event building'); _int(count, 'event building count')
            if building not in tables.get('city_building', {}) or not 1 <= count <= 100:
                raise ValueError('Missing original event building catalog or invalid count')
            current = area(aid)
            if current['st'][0] != 0:
                raise ValueError('Event building requires an original FREE area')
            slots = sorted(slot for (area_id, slot), definition in tables.get('city_development', {}).items()
                if area_id == aid and definition['level_require'] <= current['lv'])
            if not slots:
                raise ValueError('Missing original developed event building slots')
            free = [slot for slot in slots if str(slot) not in current['bd']]
            if len(free) < count:
                raise ValueError('Insufficient developed event building slots')
            occupied = set(value.get('uuid') for saved in story['city_areas'].values()
                for value in saved.get('bd', {}).values() if isinstance(value, dict))
            for slot in free[:count]:
                current['bd'][str(slot)] = {'id': building,
                    'uuid': _stable_id('event-building:%s:%s:%s' % (receipt, aid, slot), occupied)}
                current.setdefault('dbd', {}).pop(str(slot), None)
            current['mbn'] = len(slots)
            diag['policies'].append('original event building uses first developed free slots; never displaces existing buildings')
        abandoned = _ids(row.get('abandonMission', ()), 'abandonMission')
        if abandoned or row.get('refreshMission'):
            if (candidate.get('battle') or {}).get('active'):
                raise ValueError('Mission refresh/reset waits for the actual active fight to finish')
            for scene in abandoned:
                if scene not in tables.get('mission', {}):
                    raise ValueError('Missing original reset mission')
            affected_normal = normal_chapter_event_replacements(candidate,event_id,row,tables.get('mission',{}))
            revoke_normal_chapter_projection(candidate, affected_normal, 'explicit-mission-refresh')
            if abandoned:
                story['current_mission_wins'] = sorted(current_mission_wins(story) - set(abandoned))
                story.setdefault('mission_reset_receipts', {})[receipt] = list(abandoned)
                diag['policies'].append('offline retry reset changes current mission progress only; historical battle_wins and completed events remain proof, never a persistent blacklist')
            notices.extend(refresh_condition_city_missions(candidate, tables.get('mission', {}), event_id, tables.get('city_data', {})))
            diag['policies'].append('offline mission refresh rebuilds original cond_event/cond families; first eligible original ID, no inferred wins')
        blackcores = story.setdefault('blackcores', {})
        for bid, camp in row.get('changeBlackcore', {}).items():
            _int(bid, 'blackcore ID'); _int(camp, 'blackcore camp')
            if camp == 0:
                blackcores.pop(str(bid), None)
            else:
                blackcores[str(bid)] = camp
            notices.append(('updateBlackCore', {'c': camp, 'b': bid}))
        for old_camp, new_camp in row.get('batchChangeBlackcore', {}).items():
            _int(old_camp, 'blackcore old camp'); _int(new_camp, 'blackcore new camp')
            for bid, camp in list(blackcores.items()):
                if camp == old_camp:
                    if new_camp == 0: blackcores.pop(bid, None)
                    else: blackcores[bid] = new_camp
            notices.append(('updateBlackCoreCamp', {'o': old_camp, 'n': new_camp}))
        banned = story.setdefault('banned_heroes', {})
        for hid, reason in row.get('ban_heroes', {}).items():
            hero(hid); _int(reason, 'hero ban reason')
            banned[str(hid)] = reason
        if row.get('ban_heroes'):
            notices.append(('banHeroes', {'bhs': sorted(row['ban_heroes'])}))
        recovered = _ids(row.get('recoverBanHeroes', ()), 'recoverBanHeroes')
        for hid in recovered:
            hero(hid); banned.pop(str(hid), None)
        if recovered: notices.append(('recoverBanHeroes', {'rhs': recovered}))
        locked = _ids(row.get('cineLockHeroes', ()), 'cineLockHeroes')
        for hid in locked:
            hero(hid); _unique_add(story.setdefault('cine_locked_heroes', []), hid)
        if locked: notices.append(('cineLockHeroes', {'h': locked}))
        conquered = _ids(row.get('gonglueHeroes', ()), 'gonglueHeroes')
        for hid in conquered:
            hero(hid)['fd'] = True
            banned.pop(str(hid), None)
            _unique_add(story.setdefault('conquered_heroes', []), hid)
        if conquered:
            # No fabricated official clear reward. The original clear handler
            # accepts an empty per-hero reward map and updates actual ownership.
            notices.append(('gonglueHeroes', {'ghs': conquered, 'result': {}, 're': False, 'wd': False}))
            diag['policies'].append('hero clear grants state only; no invented repeat-clear rewards')
        for hid in _ids(row.get('huohaihua', ()), 'huohaihua'):
            hero(hid)['hhh'] = True
            notices.append(('huohaihuaReply', {'h': hid}))
        for route, target in row.get('completeRouteTarget', {}).items():
            _int(target, 'route target')
            story.setdefault('route_targets', {}).setdefault(str(route), [])
            _unique_add(story['route_targets'][str(route)], target)
        for field, notice in (('cityMusic', 'changeCityMusic'), ('cityTheme', 'changeCityTheme')):
            if field in row:
                value = _int(row[field], field)
                story[field] = value
                notices.append((notice, {'music' if field == 'cityMusic' else 'theme': value}))
        if row.get('isLeaveEmergencyEvent'): story['emergency'] = False
        if row.get('intelligence'):
            day = candidate.get('day',{}).get('stock_day',story.get('date'))
            intel_tables = dict(tables,event_content=event_catalog)
            data,sources = build_event_intelligence(story,event_id,row['intelligence'],intel_tables,receipt,day)
            story['intelligence'],story['intelligence_sources'] = data,sources
            notices.append(intelligence_sync_notice(candidate))
        handoffs = []
        if row.get('weekResult'):
            handoffs.append({'kind': 'week_result', 'event': event_id,
                'result': row['weekResult'], 'in_advance': bool(row.get('weekResultInAdvance')),
                'token': 'ending:%s' % event_id,
                'requires': 'completed-event-and-original-week-result-ui'})
        if row.get('enterStoryRoute'):
            handoffs.append({'kind': 'route', 'event': event_id,
                'route': row['enterStoryRoute'], 'token': 'route:%s' % event_id,
                'requires': 'completed-event-and-original-route-handoff'})
        if handoffs:
            story.setdefault('event_handoffs', {})[receipt] = copy.deepcopy(handoffs)
        diag['deferred_handoffs'] = handoffs
        for rid, definition in rewards:
            for hid in _ids(definition.get('hero', ()), 'reward hero'):
                hero(hid)
                reward.setdefault('hero', []).append(hid)
                diag['policies'].append('already owned hero retained; no invented duplicate fragments')
            for hid, delta in definition.get('friends', {}).items():
                h = hero(hid)
                h['ef'] = min(100, max(0, h.get('ef', 0) + _int(delta, 'friendliness')))
                notices.append(('updateFriendlyValue', {'h': hid, 'v': h['ef']}))
            for hid, delta in definition.get('fatigue', {}).items():
                if type(hid) is int and hid == 0:
                    audit, recovery_notices = resolve_winning_party_fatigue(
                        candidate, event_catalog, tables, event_id, receipt, rid, delta)
                    notices.extend(recovery_notices)
                    diag['policies'].append(audit['policy'])
                    diag.setdefault('winning_party_fatigue', []).append(audit)
                    continue
                h = hero(hid)
                h['cf'] = min(100, max(0, h.get('cf', 100) + _int(delta, 'fatigue')))
                notices.append(('updateCurFatigueValue', {'h': hid, 'v': h['cf']}))
            for cid in _ids(definition.get('cg', ()), 'reward cg'):
                cg(cid)
                if not tables['cg_data'][cid].get('skip'):
                    _unique_add(reward.setdefault('cg', []), cid)
            item_ids, amounts = definition.get('items', ()), definition.get('itemsNum', ())
            if len(item_ids) != len(amounts): raise ValueError('Mismatched item reward arrays')
            for tid, amount in zip(item_ids, amounts): inventory_item(tid, amount, rid)
            for field, key, notice in (('money','money','updateMoney'), ('crystal','crystal','updateCrystal'),
                    ('friendcoin','friendcoin','updateFriendCoin'), ('summoncoin','summoncoin','updateSummonCoin')):
                if field in definition:
                    economy = candidate['profile'].setdefault('economy', {'version':1,'money':0,'exp':0,'level':1})
                    value = economy.get(key, 0) + _int(definition[field], field)
                    if value < 0: raise ValueError('Insufficient %s for original event cost' % field)
                    economy[key] = value
                    payload = {'v': value}
                    if field == 'crystal': payload['bv'] = economy.get('bind_crystal', 0)
                    notices.append((notice, payload))
                    reward[field] = reward.get(field, 0) + definition[field]
            if 'buildFund' in definition:
                values = story.setdefault('city_values', {})
                values['bf'] = values.get('bf', 0) + _int(definition['buildFund'], 'buildFund')
                if values['bf'] < 0: raise ValueError('Insufficient city build fund')
                notices.append(('setBuildFund', {'b': values['bf']}))
            for template in _ids(definition.get('skin', ()), 'reward skin'):
                skin = tables.get('skin', {}).get(template)
                if not skin: raise ValueError('Missing original reward costume')
                h = hero(skin['hero'])
                if not any(s['i'] == template for s in h['sk'].values()):
                    raise ValueError('Costume absent from full original wardrobe; run existing ownership migration')
                reward.setdefault('skin', []).append(template)
            if definition.get('init_skin'):
                # Original initial-costume entitlement; full original wardrobe
                # already fulfills it without resetting the worn instance.
                diag['policies'].append('initial costume entitlement fulfilled by preserved full wardrobe')
            tids, nums, classes = (definition.get(k, ()) for k in ('treasure','treasureNum','treasureLevel'))
            if len(tids) != len(nums) or len(tids) != len(classes):
                raise ValueError('Unsupported treasure generator or mismatched arrays')
            for tid, num, quality in zip(tids, nums, classes):
                treasure(tid, num, quality, definition.get('tradeType', 0), rid)
            for building in _ids(definition.get('buildableBuilding', ()), 'buildableBuilding'):
                _unique_add(story.setdefault('buildable_buildings', []), building)
                notices.append(('add_hidden_building', {'hb': list(story['buildable_buildings'])}))
            for aid, building in definition.get('destroyBuliding', ()):
                current = area(aid)
                removed = current.setdefault('dbd', {})
                # Original reward lacks field slot; remove matching placed IDs
                # only. Never invent a field/building placement.
                for slot, value in list(current.get('bd', {}).items()):
                    if value == building or isinstance(value, (tuple,list)) and value and value[0] == building:
                        removed[str(slot)] = building
                        del current['bd'][slot]
        if row.get('buildBuilding') or destroy_pairs:
            before_areas, before_totals = _event_city_capacities(state.get('story', {}), tables['city_building'], len(heroes))
            after_areas, after_totals = _event_city_capacities(story, tables['city_building'], len(heroes))
            values = story.setdefault('city_values', {})
            for field in ('fv', 'rv', 'dv'):
                values[field] = values.get(field, 0) + after_totals[field] - before_totals[field]
            for aid in affected_areas:
                current = story['city_areas'][str(aid)]
                for field in ('fv', 'rv', 'dv'):
                    current[field] = current.get(field, 0) + after_areas[str(aid)][field] - before_areas.get(str(aid), {}).get(field, 0)
        notices.extend(apply_daerweila_event(candidate, event_id, row,
            dict(tables, event_content=event_catalog), receipt))
        if row.get('areaSpecialStage'):
            revoke_normal_chapter_projection(candidate, list(row['areaSpecialStage']), 'positive-special-source')
        special_notices = apply_special_city_stage_effects(candidate, event_id, row,
            dict(tables, event_content=event_catalog), receipt)
        notices.extend(special_notices)
        affected_areas.update(payload['ai'] for name, payload in special_notices if name == 'get_area_stages_reply')
        provider_notices = record_city_stage_occurrence(candidate, event_id, row, tables, receipt)
        revoke_normal_chapter_projection(candidate, [payload['ai'] for name,payload in provider_notices if name == 'get_area_stages_reply'], 'coc-source-write')
        notices.extend(provider_notices)
        affected_areas.update(payload['ai'] for name, payload in provider_notices if name == 'get_area_stages_reply')
        for aid in set(row.get('areaFight', ())) | set(row.get('areaStrike', ())):
            if not story['city_areas'][str(aid)].get('stage') and not city_stage_provider_pending_source(candidate, aid):
                # Proven selector0 source is minted only after this real event
                # joins completed_events and its atomic effect receipt exists.
                resolve_normal_chapter(aid, story['city_areas'][str(aid)]['st'][0],
                    normal_chapter_token(candidate)[0], tables.get('chapter_mission_data', {}), tables.get('mission', {}))
        if added_cgs: notices.append(('addCg', {'c': sorted(set(added_cgs))}))
        if item_updates: notices.append(('updateItems', {'i': item_updates}))
        if affected_areas:
            ais = {'area_%d' % aid: copy.deepcopy(story['city_areas'][str(aid)]) for aid in sorted(affected_areas)}
            notices.append(('get_all_area_info_reply', {'ais': ais,
                'cd': copy.deepcopy(story.get('city_values', {})), 'sm': False}))
        if reward: notices.append(('completeEventReplyStart', {'e': event_id, 'r': reward}))
        if row.get('special_agreement') == 'enter_flashback':
            if event_id != 7752:
                raise ValueError('Unknown flashback entry agreement')
            flashback_accept_entry(candidate, event_id, receipt)
        ledger[receipt] = event_id
        diag.update(ready=True, status='applied', receipt_key=receipt,
                    reward_count=len(rewards), affected_areas=sorted(affected_areas))
        return candidate, notices, diag
    except (ValueError, KeyError, TypeError, IndexError) as error:
        diag['reason'] = str(error)
        diag['status'] = ('blocked-state' if str(error).startswith(('Insufficient', 'Missing owned')) else 'unsupported')
        return copy.deepcopy(state), [], diag


def apply_event_effects_snapshot(state, base_snapshot):
    """Project durable effects onto original ClientAvatar loader field names.

    Call after normal profile/native-ObjectId hero snapshots were assembled.
    Existing unmodified loader fields remain intact; this never constructs hero
    objects or invents account reset/progression state.
    """
    snapshot = copy.deepcopy(base_snapshot)
    story = state.get('story', {})
    for source, target in (('cgs','cgs'), ('new_cgs','ncgs')):
        if source in story:
            snapshot[target] = sorted(set(story[source]))
    if 'cgs' in story:
        snapshot['ccgs'] = sorted(set(story.get('cur_cgs', story['cgs'])))
    if 'notes' in story: snapshot['np'] = copy.deepcopy(story['notes'])
    if 'social' in story:
        social = snapshot.setdefault('sd', {'sm':{}, 'pm':{}})
        for kind in ('sm','pm'):
            social[kind] = copy.deepcopy(story['social'].get(kind, {}))
    city = snapshot.setdefault('city', {})
    if 'intelligence' in story:
        snapshot['intelligence'] = copy.deepcopy(story['intelligence'])
    city.update(copy.deepcopy(story.get('city_values', {})))
    if 'city_op_exclam' in story: city['coe'] = copy.deepcopy(story['city_op_exclam'])
    if 'buildable_buildings' in story:
        city['hb'] = sorted(set(story['buildable_buildings']))
    if 'heromgr' in snapshot:
        manager = snapshot['heromgr']
        conquered=set(story.get('conquered_heroes',[]))
        for hero_id,record in list(manager.get('hrs',[]))+list(manager.get('bhrs',[])):
            if hero_id in conquered:record['cfd']=True
        if 'banned_heroes' in story:
            banned = set(int(h) for h in story['banned_heroes'])
            all_heroes = dict(list(manager.get('hrs', [])) + list(manager.get('bhrs', [])))
            manager['hrs'] = [(h, info) for h, info in sorted(all_heroes.items()) if h not in banned]
            manager['bhrs'] = [(h, info) for h, info in sorted(all_heroes.items()) if h in banned]
        if 'cine_locked_heroes' in story:
            manager['c'] = sorted(set(story['cine_locked_heroes']))
    std = snapshot.setdefault('std', {})
    std.update(daily_wish_notice(story)[1])
    std.update(huisu_std_projection(state))
    for key, field in (('cityMusic','cm'), ('cityTheme','ct'), ('clues','cl'),
            ('failed_clues','fc'), ('clues_read','cr'), ('clue_details_read','dr'),
            ('rely_value','srv'), ('support_value','ssv'), ('yisake_value','yiv'), ('general_value','gr')):
        if key in story: std[field] = copy.deepcopy(story[key])
    data = flashback_data(state)
    std.update({k: data[k] for k in ('ff', 'fd', 'fa')})
    if data['ff']:
        std['gr'] = data['fd']
    std.update(project_route_agreements(story, std))
    std.update(project_daerweila(state, std))
    route = story.get('route')
    if str(route) in ('31','31-4') and 'general_value' not in story:
        std['gr'] = 0
    if 'route_targets' in story:
        std['srt'] = sorted(set(story['route_targets'].get(route, [])))
    economy = (state.get('profile') or {}).get('economy', {})
    for source, field in (('money','money'), ('crystal','crystal'), ('bind_crystal','bind_crystal'),
                          ('friendcoin','friendCoin'), ('summoncoin','summonCoin')):
        if source in economy: snapshot[field] = economy[source]
    return snapshot


def validate_daily_wish(story, catalog=None):
    wishes = story.get('daily_wish',[])
    if not isinstance(wishes,list)or any(type(value)is not int or not 1<=value<=15 or catalog is not None and value not in catalog for value in wishes):
        raise ValueError('Unknown or damaged original daily wish IDs')
    if type(story.get('daily_wish_read',False))is not bool or type(story.get('daily_wish_hero',0))is not int or story.get('daily_wish_hero',0)<0:
        raise ValueError('Invalid original daily wish read/hero state')
    if type(story.get('daily_wish_generation',0))is not int or story.get('daily_wish_generation',0)<0:
        raise ValueError('Invalid daily wish occurrence')


def daily_wish_notice(story):
    validate_daily_wish(story)
    return ('syncDailyWish',{'dw':copy.deepcopy(story.get('daily_wish',[])),
        'dwh':story.get('daily_wish_hero',0),'dwr':story.get('daily_wish_read',False)})


def daily_wish_token(story):
    validate_daily_wish(story)
    return [story.get('week',0),story.get('daily_wish_generation',0),list(story.get('daily_wish',[]))]


def prepare_daily_wish_read(state, arguments, token, catalog):
    candidate=copy.deepcopy(state);story=candidate['story'];validate_daily_wish(story,catalog)
    if set(arguments)-set(('_cbid_',))or token!=daily_wish_token(story)or not story.get('daily_wish'):
        return candidate,False
    changed=not story.get('daily_wish_read',False)
    if changed:story['daily_wish_read']=True
    return candidate,changed


def daily_choice_token(state):
    story=state['story']
    return [story.get('week',0),story.get('event_occurrences',{}).get('8078',0)]


def prepare_daily_wish_choice(state, arguments, token, content, heroes):
    candidate=copy.deepcopy(state);story=candidate['story'];validate_daily_wish(story)
    if set(arguments)-set(('h','_cbid_'))or type(arguments.get('h'))is not int:
        raise ValueError('Daily wish hero requires explicit original user choice')
    if token!=daily_choice_token(state)or type(token[1])is not int or token[1]<=0:
        raise ValueError('Stale daily promise occurrence')
    row=content.get(8078,{})
    if 8078 not in state.get('processing_events',[])or tuple(row.get('ui',()))!=('promise_main','notify_show','1')or tuple(row.get('contentFinishUI',()))!=(4,)or tuple(row.get('completeConds',{}).get('ui',()))!=(4,):
        raise ValueError('Daily hero choice requires original active promise_main8078 UI4')
    occurrence='%s:8078:%s'%(token[0],token[1]);selected=arguments['h']
    receipts=story.setdefault('daily_wish_choice_receipts',{})
    if occurrence in receipts:
        if receipts[occurrence]['hero']!=selected:raise ValueError('Daily promise already chose another hero')
        return candidate,False
    traces=dict(state.get('event_traces',[])).get(8078,[])
    if 4 in dict(traces).get('ui',[])or 'ui:8078'in story.get('event_callbacks',{}).get('8078',[]):
        raise ValueError('Daily promise UI gate already completed')
    owned=state.get('profile',{}).get('heroes',{}).get(str(selected))
    cleared=selected in story.get('conquered_heroes',[])or bool(owned and owned.get('cfd')is True)
    if not owned or not cleared or not heroes.get(selected)or heroes[selected].get('dailyCannotGonglue'):
        raise ValueError('Hero is outside original conquered daily promise candidates')
    story['daily_wish_hero']=selected
    receipts[occurrence]={'hero':selected,'source_event':8078,'policy':'original-explicit-conquered-promise-choice-v1'}
    return candidate,True


def daily_wish_choice_committed(state):
    token=daily_choice_token(state);story=state['story']
    receipt=story.get('daily_wish_choice_receipts',{}).get('%s:8078:%s'%(token[0],token[1]))
    if not receipt or receipt.get('hero')!=story.get('daily_wish_hero'):
        return False
    hero=state.get('profile',{}).get('heroes',{}).get(str(receipt['hero']))
    return bool(hero and (hero.get('cfd')is True or receipt['hero']in story.get('conquered_heroes',[])))
