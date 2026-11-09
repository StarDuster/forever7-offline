# -*- coding: ascii -*-
"""Table-driven normal city campaigns; explicit offline policy, not server code.

Sections are alternatives. Eligible members use a named local choice policy. No source
is inferred from current cs/sl, historical wins, or a route string alone.
"""
import copy
try:
    from offline_special_city_stage import _ssc_plain_literal, _ssc_hash, _ssc_route, _ssc_day, _ssc_text
except ImportError:
    pass

NORMAL_CHAPTER_POLICY = 'offline-original-normal-chapter-v1'


def _nc_contexts(state):
    return state.get('story', {}).get('normal_chapters', {}).get('contexts', {})


def _nc_live(state, context):
    return context.get('week') == state['story'].get('week') and context.get('route') == _ssc_route(state)


def resolve_normal_chapter(area, status, route, chapters, missions):
    if (type(area) is not int or not 1 <= area <= 8 or type(status) is not int or status not in (1,5) or
            not isinstance(route, _ssc_text) or not route):
        raise ValueError('Unsupported normal chapter area/status/route')
    bucket = 0 if status == 1 else 5
    routes = []
    for value in (route, route.split('-')[0], '-1'):
        if value not in routes:
            routes.append(value)
    # Normalize keys and rows together, rejecting duplicate native keys rather
    # than relying on Python bool/int equality or dict overwrite behavior.
    entries = []
    for key, row in chapters.items():
        key, row = _ssc_plain_literal(key), _ssc_plain_literal(row)
        if not isinstance(row, dict):
            raise ValueError('Invalid original chapter mapping')
        fields = tuple(row.get(name) for name in ('chapter','status','route','specialStage'))
        if key in [(area,bucket,value,0) for value in routes] or fields in [(area,bucket,value,0) for value in routes]:
            if (type(key) is not tuple or key != fields or len(key) != 4 or
                    any(type(key[index]) is not int for index in (0,1,3)) or not isinstance(key[2], _ssc_text)):
                raise ValueError('Original normal chapter key/row mismatch')
            entries.append((key,row))
    selected = None
    for value in routes:
        found = [(key,row) for key,row in entries if key == (area,bucket,value,0)]
        if found:
            if len(found) != 1:
                raise ValueError('Ambiguous original normal chapter key')
            selected = found[0]
            break
    if selected is None:
        raise ValueError('Missing original normal chapter key')
    key,row = selected
    sections = row.get('section')
    if (not isinstance(sections,dict) or set(sections) != set(range(10)) or
            any(type(index) is not int for index in sections)):
        raise ValueError('Invalid original normal chapter sections')
    groups, snapshots, members = [], {}, []
    for index in range(10):
        values = sections[index]
        if type(values) not in (tuple,list) or any(type(scene) is not int or scene <= 0 for scene in values):
            raise ValueError('Invalid original normal chapter member')
        if values:
            groups.append(list(values))
        for scene in values:
            mission = _ssc_plain_literal(missions.get(scene,{}), True)
            if (not isinstance(mission,dict) or scene in members or type(mission.get('id')) is not int or
                    mission.get('id') != scene or mission.get('release') != 1 or type(mission.get('release')) is bool or
                    mission.get('ch') != area or type(mission.get('ch')) is not int):
                raise ValueError('Unreleased, duplicate, alias or mismatched normal chapter member')
            if mission.get('system_type') != 1 or type(mission.get('system_type')) is not int:
                raise ValueError('Delegated COC/conditional chapter requires its actual provider')
            snapshots[str(scene)] = mission
            members.append(scene)
    if not members:
        raise ValueError('Empty original normal chapter')
    dependencies = {}
    for mission in snapshots.values():
        for parent in mission.get('cond',[]):
            if type(parent) is not int:
                raise ValueError('Invalid original prerequisite scene')
            if str(parent) not in snapshots:
                dependencies[str(parent)] = _ssc_plain_literal(missions.get(parent,{}),True)
    descriptor = {'dependency_missions':dependencies, 'key':list(key), 'requested_route':route,
        'fallback_kind':'exact' if key[2] == route else 'default' if key[2] == '-1' else 'base',
        'groups':groups, 'members':members, 'missions':snapshots,
        'section_policy':'actual-cond-event-first-then-original-section-order-v1',
        'lookup_policy':'missing-key-only-exact-base-default'}
    descriptor['catalog_token'] = _ssc_hash(descriptor)
    return descriptor


def stage_projection_owner(state, area):
    """Shared writer arbitration. Higher typed owners exclude condition writes."""
    story, key = state.get('story',{}), str(area)
    special = story.get('special_city_stages',{}).get('contexts',{}).get(key)
    positive = bool(special and not special.get('revoked') and _nc_live(state,special))
    coc = story.get('city_stage_provider') or {}
    coc_active = bool(_nc_live(state,coc) and key in coc.get('family',{}) and key not in coc.get('superseded',[]))
    if positive and coc_active:
        raise ValueError('Conflicting positive-special and COC owners')
    if positive:
        return 'positive-special'
    if coc_active:
        return 'coc'
    if key in story.get('condition_mission_roots',{}):
        return 'conditional'
    normal = _nc_contexts(state).get(key)
    if normal and _nc_live(state,normal) and not normal.get('revoked'):
        return 'normal'
    return None


def _nc_event_fields(row,fields):
    """Finite event projection: unrelated native set metadata is not state.

    Do not broaden the literal converter: every copied supported field remains
    strict, and duplicate supported native mapping keys still fail closed.
    """
    result = {}
    for original_key,value in row.items():
        key = _ssc_plain_literal(original_key)
        if key in fields:
            if key in result:
                raise ValueError('Duplicate supported original event field')
            result[key] = _ssc_plain_literal(value)
    return result


def _nc_events(state, tables, effect=None, area=None):
    result = []
    for receipt,event in state['story'].get('event_effect_receipts',{}).items():
        row = _nc_event_fields(tables.get('event_content',tables.get('events',{})).get(event,{}), ['release',effect] if effect else ['release'])
        if event not in state.get('completed_events',[]) or not row.get('release'):
            continue
        values = row.get(effect,[]) if effect else []
        if effect and (type(values) not in (list,tuple) or area not in values):
            continue
        result.append({'event':event,'receipt':receipt})
    return sorted(result,key=lambda item:(item['event'],item['receipt']))


def _nc_route_source(state,tables):
    route, week = _ssc_route(state), state['story'].get('week')
    transition = state.get('week_protocol',{}).get('transition')
    if (route == '1' and isinstance(transition,dict) and transition.get('target_week') == week and
            transition.get('source_week') == week-1 and transition.get('id') and
            transition.get('operation') in ('handleIncWeekAsk','handleResetWeekAsk','requestEnterStoryByEnding','requestEnterStory')):
        return {'kind':'fresh-week','transition':transition['id'],'week':week}
    events = tables.get('event_content',tables.get('events',{}))
    consumed = state.get('week_protocol',{}).get('consumed_handoffs',[])
    for event in reversed(state['story'].get('event_history',state.get('completed_events',[]))):
        row = _nc_event_fields(events.get(event,{}),['release','enterStoryRoute'])
        token = 'route:%s' % event
        if (event in state.get('completed_events',[]) and row.get('release') and row.get('enterStoryRoute') == route and token in consumed):
            return {'kind':'route-handoff','event':event,'token':token,'week':week}
    raise ValueError('Normal chapter lacks committed fresh-week or route handoff source')


def _nc_archive_hash_valid(context):
    if 'archive_reason' not in context:
        return True
    unsigned = dict(context)
    token = unsigned.pop('archive_token',None)
    return token == _ssc_hash(unsigned)


def _nc_receipt_chain(state,context,visiting=None):
    """Recheck frozen historical source receipts on every carried admission."""
    try:
        epoch = context['epoch']
        visiting = set() if visiting is None else visiting
        if epoch in visiting or len(visiting) > 16 or context['week'] != state['story']['week'] or not _nc_archive_hash_valid(context):
            return False
        visiting = visiting | {epoch}
        if epoch != _ssc_hash({'source':context['source'],'week':context['week'],'day':context['entry_day'],
                'route':context['route'],'catalog':context['descriptor']['catalog_token']}):
            return False
        source = context['source']; route = source['route_source']; story = state['story']
        if route.get('kind') == 'fresh-week':
            transition = state.get('week_protocol',{}).get('transition') or {}
            if transition.get('id') != route.get('transition') or transition.get('target_week') != context['week']:
                return False
        elif route.get('kind') == 'route-handoff':
            if route.get('event') not in state.get('completed_events',[]) or route.get('token') not in state.get('week_protocol',{}).get('consumed_handoffs',[]):
                return False
        else:
            return False
        activation = source['activation']; kind = activation.get('kind')
        if kind == 'fresh-week-area2':
            return route['kind'] == 'fresh-week' and context['descriptor']['key'][0] == 2
        proofs = activation.get('proofs',[activation])
        for proof in proofs:
            if proof.get('kind') in ('areaFight','areaStrike','event-free'):
                if proof.get('event') not in state.get('completed_events',[]) or story.get('event_effect_receipts',{}).get(proof.get('receipt')) != proof.get('event'):
                    return False
            elif proof.get('kind') in ('normal-clear','normal-route-carry'):
                parents = list(_nc_contexts(state).values()) + story.get('normal_chapter_history',[])
                matches = [parent for parent in parents if parent.get('epoch') == proof.get('epoch') and parent.get('wins') == proof.get('wins') and
                    (proof.get('kind') != 'normal-clear' or parent.get('complete')) and
                    (proof.get('kind') != 'normal-route-carry' or parent.get('archive_token') == proof.get('archive_token'))]
                if not any(_nc_receipt_chain(state,parent,visiting) for parent in matches):
                    return False
            else:
                return False
        return True
    except (ValueError,TypeError,KeyError,AttributeError):
        return False


def _nc_archived_valid(state,tables,context,area,complete=False,require_current=True,visiting=None):
    """Authenticate our own accepted current-week contexts, never basic saves."""
    try:
        if (type(context) is not dict or context.get('week') != state['story'].get('week') or
                context.get('revoked') or complete and not context.get('complete')):
            return False
        if not _nc_archive_hash_valid(context):
            return False
        visiting = set() if visiting is None else visiting
        identity = context.get('epoch')
        if identity in visiting or len(visiting) > 16:
            return False
        visiting = visiting | {identity}
        synthetic = {'story':dict(state['story'], route='__normal-source-validation__', normal_chapters={'version':1,'contexts':{str(area):context}})}
        validate_normal_chapters(synthetic)
        descriptor = context['descriptor']
        original = resolve_normal_chapter(area,1 if descriptor['key'][1] == 0 else 5,context['route'],
            tables.get('chapter_mission_data',{}),tables.get('mission',{}))
        if descriptor != original or require_current and not set(context['wins']).issubset(set(state['story'].get('current_mission_wins',[]))):
            return False
        source = context['source']; route_source = source['route_source']
        if route_source.get('week') != context['week']:
            return False
        if route_source.get('kind') == 'fresh-week':
            transition = state.get('week_protocol',{}).get('transition') or {}
            if (context['route'] != '1' or transition.get('id') != route_source.get('transition') or
                    transition.get('target_week') != context['week'] or transition.get('source_week') != context['week']-1):
                return False
        elif route_source.get('kind') == 'route-handoff':
            event = route_source.get('event')
            row = _nc_event_fields(tables.get('event_content',tables.get('events',{})).get(event,{}),['release','enterStoryRoute'])
            if (not row.get('release') or row.get('enterStoryRoute') != context['route'] or
                    event not in state.get('completed_events',[]) or route_source.get('token') != 'route:%s' % event or
                    route_source['token'] not in state.get('week_protocol',{}).get('consumed_handoffs',[])):
                return False
        else:
            return False
        activation = source['activation']; kind = activation.get('kind')
        if kind == 'fresh-week-area2':
            return area == 2 and route_source['kind'] == 'fresh-week'
        if kind in ('areaFight','areaStrike'):
            return {'event':activation.get('event'),'receipt':activation.get('receipt')} in _nc_events(state,tables,kind,area)
        if kind == 'normal-route-carry':
            matches = [parent for parent in state['story'].get('normal_chapter_history',[]) if
                parent.get('epoch') == activation.get('epoch') and parent.get('archive_token') == activation.get('archive_token') and
                parent.get('wins') == activation.get('wins') and parent.get('archive_reason') == 'route-handoff' and
                all(parent.get('descriptor',{}).get(field) == descriptor.get(field) for field in ('groups','missions','dependency_missions'))]
            return any(_nc_archived_valid(state,tables,parent,area,False,require_current,visiting) for parent in matches)
        if kind != 'area-require':
            return False
        requirements = _ssc_plain_literal(tables.get('city_data',{}).get(area,{}).get('area_require',{}))
        required = next((requirements[key] for key in (context['route'],context['route'].split('-')[0],'-1') if key in requirements),None)
        proofs = activation.get('proofs',[])
        if (type(required) not in (list,tuple) or not required or any(type(value) is not int or not 1 <= value <= 8 for value in required) or
                [proof.get('area') for proof in proofs] != list(required)):
            return False
        for proof in proofs:
            if proof.get('kind') == 'event-free':
                if {'event':proof.get('event'),'receipt':proof.get('receipt')} not in _nc_events(state,tables,'areaFree',proof['area']):
                    return False
            elif proof.get('kind') == 'normal-clear':
                candidates = list(_nc_contexts(state).values()) + state['story'].get('normal_chapter_history',[])
                matches = [parent for parent in candidates if parent.get('epoch') == proof.get('epoch') and parent.get('wins') == proof.get('wins')]
                if not any(_nc_archived_valid(state,tables,parent,proof['area'],True,False,visiting) for parent in matches):
                    return False
            else:
                return False
        return True
    except (ValueError,TypeError,KeyError,AttributeError):
        return False


def _nc_free_proof(state,tables,area):
    current = state['story'].get('city_areas',{}).get(str(area),{})
    if current.get('st',[None])[0] != 0:
        return None
    candidates = [_nc_contexts(state).get(str(area))] + list(reversed(state['story'].get('normal_chapter_history',[])))
    for context in candidates:
        if context and context.get('descriptor',{}).get('key',[None])[0] == area and _nc_archived_valid(state,tables,context,area,True):
            return {'kind':'normal-clear','area':area,'epoch':context['epoch'],'wins':list(context['wins'])}
    proofs = _nc_events(state,tables,'areaFree',area)
    return dict(proofs[-1],kind='event-free',area=area) if proofs else None


def mark_normal_chapter_activation(state,event,row,receipt):
    """Remember an actual effect occurrence; completion/ledger still gate it.

    A genuine explicit new activation starts a fresh per-area epoch with no
    inherited wins. Merely reading a status or old completed ID cannot do so.
    """
    fields = _nc_event_fields(row,['release','areaFight','areaStrike'])
    if not fields.get('release'):
        return
    for effect in ('areaFight','areaStrike'):
        areas = fields.get(effect,[])
        if type(areas) not in (tuple,list) or any(type(area) is not int for area in areas):
            raise ValueError('Invalid original normal activation areas')
        for area in areas:
            if not 1 <= area <= 8:
                continue
            active = state.get('battle',{}).get('active') or {}
            if active.get('normal_chapter_source') and active['request']['d']['a'] == area:
                raise ValueError('Actual normal battle blocks explicit reactivation')
            if type(event) is not int or not isinstance(receipt,_ssc_text) or not receipt:
                raise ValueError('Actual normal activation requires effect identity')
            state['story'].setdefault('normal_chapter_activations',{})[str(area)] = {
                'event':event,'receipt':receipt,'kind':effect,'week':state['story'].get('week')}


def derive_normal_campaign_source(state,area,tables):
    route_source = _nc_route_source(state,tables)
    current = state['story'].get('city_areas',{}).get(str(area))
    if current and (len(current.get('st',[])) != 3 or current['st'][2]):
        raise ValueError('Normal chapter cannot remove an original area lock')
    marker = state['story'].get('normal_chapter_activations',{}).get(str(area))
    if marker and marker.get('week') == state['story'].get('week'):
        effect = marker.get('kind')
        if effect in ('areaFight','areaStrike') and {'event':marker.get('event'),'receipt':marker.get('receipt')} in _nc_events(state,tables,effect,area):
            if current and current['st'][0] == (1 if effect == 'areaFight' else 5):
                return {'route_source':route_source,'activation':{'kind':effect,'event':marker['event'],'receipt':marker['receipt']}}
    if area == 2 and route_source['kind'] == 'fresh-week':
        if current and current['st'][0] == 1:
            return {'route_source':route_source,'activation':{'kind':'fresh-week-area2'}}
    existing = _nc_contexts(state).get(str(area))
    if (existing and _nc_live(state,existing) and not existing.get('revoked') and current and current['st'][0] == 1 and
            existing.get('source',{}).get('activation',{}).get('kind') == 'normal-route-carry' and
            existing['source'].get('route_source') == route_source and _nc_archived_valid(state,tables,existing,area)):
        # Once minted, the source remains pinned to the accepted ancestor;
        # later actual wins change our own projection, never that ancestor's.
        return copy.deepcopy(existing['source'])
    if current and current['st'][0] == 1:
        for previous in reversed(state['story'].get('normal_chapter_history',[])):
            activation = previous.get('source',{}).get('activation',{})
            origin = activation.get('origin_activation',activation)
            if (previous.get('archive_reason') != 'route-handoff' or origin.get('kind') != 'fresh-week-area2' or area != 2 or
                    previous.get('descriptor',{}).get('key',[None])[0] != area or current.get('stage') != previous.get('last_stage') or
                    not _nc_archived_valid(state,tables,previous,area)):
                continue
            selected = resolve_normal_chapter(area,1,_ssc_route(state),tables.get('chapter_mission_data',{}),tables.get('mission',{}))
            if all(previous['descriptor'].get(field) == selected.get(field) for field in ('groups','missions','dependency_missions')):
                return {'route_source':route_source,'activation':{'kind':'normal-route-carry','epoch':previous['epoch'],
                    'archive_token':previous['archive_token'],'wins':list(previous['wins']),'origin_activation':copy.deepcopy(origin)}}
    for effect,status in (('areaFight',1),('areaStrike',5)):
        proofs = _nc_events(state,tables,effect,area)
        if proofs and current and current['st'][0] == status:
            return {'route_source':route_source,'activation':dict(proofs[-1],kind=effect)}
    row = tables.get('city_data',{}).get(area,{})
    values = _ssc_plain_literal(row.get('area_require',{}))
    route = _ssc_route(state)
    required = next((values[key] for key in (route,route.split('-')[0],'-1') if key in values),None)
    if not required or type(required) not in (list,tuple) or any(type(value) is not int or not 1 <= value <= 8 for value in required):
        raise ValueError('Normal chapter has unknown or sentinel area prerequisites')
    proofs = [_nc_free_proof(state,tables,value) for value in required]
    if not all(proofs):
        raise ValueError('Normal chapter lacks genuine FREE predecessor sources')
    if current and current['st'][0] not in (1,2):
        raise ValueError('Explicit area status supersedes normal activation')
    return {'route_source':route_source,'activation':{'kind':'area-require','proofs':proofs}}


def _nc_stage(state,context):
    wins = set(context['wins'])
    current = set(state['story'].get('current_mission_wins',[])) | wins
    completed = set(state.get('completed_events',[]))
    for group in context['descriptor']['groups']:
        won = [scene for scene in group if scene in wins]
        if len(won) > 1:
            raise ValueError('Alternative section cannot have multiple campaign wins')
        if won:
            continue
        eligible = []
        for scene in group:
            row = context['descriptor']['missions'][str(scene)]
            prerequisites = row.get('cond',[])
            if type(prerequisites) is not list or any(type(value) is not int for value in prerequisites):
                raise ValueError('Unsupported normal mission prerequisites')
            parents = dict(context['descriptor'].get('dependency_missions',{}))
            parents.update(context['descriptor']['missions'])
            merge = len(prerequisites) > 1 and all(scene in parents.get(str(parent),{}).get('nextstagenums',[]) for parent in prerequisites)
            cond_met = any(parent in current for parent in prerequisites) if merge else set(prerequisites).issubset(current)
            if cond_met and (not row.get('cond_event') or row['cond_event'] in completed):
                eligible.append(scene)
        # Explicit offline choice, not a recovered server algorithm: actual
        # completed event-gated alternatives take priority, then table order.
        gated = [scene for scene in eligible if context['descriptor']['missions'][str(scene)].get('cond_event')]
        chosen = gated or eligible
        return {'cs':chosen[0] if chosen else 0,'sl':copy.deepcopy(context['descriptor']['groups'])}
    return {'cs':0,'sl':copy.deepcopy(context['descriptor']['groups'])}


def normal_chapter_token(state):
    return (_ssc_route(state),state['story'].get('week'),_ssc_day(state),_ssc_hash({'contexts':_nc_contexts(state),'activations':state['story'].get('normal_chapter_activations',{})}))


def refresh_normal_chapters(state,tables):
    """Project only proven campaigns. Legacy saves retain their existing play."""
    story = state['story']
    notices, pending = [], []
    before_structure = {key:(area.get('id'),copy.deepcopy(area.get('st'))) for key,area in story.get('city_areas',{}).items()}
    active = state.get('battle',{}).get('active')
    for area in range(1,9):
        key = str(area)
        if area == 1 and story.get('emergency') and not story.get('first_clearance_applied'):
            pending.append({'area':1,'reason':'original-tutorial-owner'})
            continue
        context = _nc_contexts(state).get(key)
        owner = stage_projection_owner(state,area)
        if owner in ('positive-special','coc','conditional'):
            continue
        current = story.get('city_areas',{}).get(key)
        if context and not _nc_live(state,context):
            if active and active.get('normal_chapter_source'):
                raise ValueError('Actual normal fight blocks route/week replacement')
            context['revoked'] = True
            pending.append({'area':area,'reason':'stale-route-context-requires-expiry'})
            continue
        marker = story.get('normal_chapter_activations',{}).get(key)
        marker_committed = bool(marker and marker.get('week') == story.get('week') and marker.get('event') in state.get('completed_events',[]) and
            story.get('event_effect_receipts',{}).get(marker.get('receipt')) == marker.get('event'))
        activation = context.get('source',{}).get('activation',{}) if context else {}
        reactivating = bool(marker_committed and context and any(marker.get(field) != activation.get(field) for field in ('event','receipt','kind')))
        if context and (context['revoked'] or context.get('complete')) and not reactivating:
            continue
        source = None
        try:
            source = derive_normal_campaign_source(state,area,tables)
            if reactivating and source['activation'] == {field:marker[field] for field in ('kind','event','receipt')}:
                if active:
                    raise ValueError('Actual battle blocks a new normal activation epoch')
                context['archive_reason'] = 'explicit-reactivation'
                context['archive_token'] = _ssc_hash(context)
                story.setdefault('normal_chapter_history',[]).append(copy.deepcopy(context))
                _nc_contexts(state).pop(key)
                context = None
            status = current['st'][0] if current and current['st'][0] in (1,5) else 1
            descriptor = resolve_normal_chapter(area,status,_ssc_route(state),tables.get('chapter_mission_data',{}),tables.get('mission',{}))
            carried = []
            if context is None:
                # Only this provider's archived accepted scene proofs from the
                # same current week survive an equivalent route handoff.
                for previous in reversed(story.get('normal_chapter_history',[])):
                    prior = previous.get('descriptor',{})
                    if (previous.get('archive_reason') == 'route-handoff' and (previous.get('source',{}).get('activation') == source['activation'] or
                            source['activation'].get('kind') == 'normal-route-carry' and source['activation'].get('epoch') == previous.get('epoch')) and
                            _nc_archived_valid(state,tables,previous,area) and
                            all(prior.get(field) == descriptor.get(field) for field in ('groups','missions','dependency_missions'))):
                        carried = [scene for scene in previous['wins'] if scene in story.get('current_mission_wins',[])]
                        break
            if context is None and current and not carried and not marker_committed:
                initial = _nc_stage(state,{'descriptor':descriptor,'wins':[]})
                previous_wins = set(story.get('battle_wins',[])) | set(story.get('current_mission_wins',[]))
                if (previous_wins.intersection(descriptor['members']) or
                        source['route_source']['kind'] == 'fresh-week' and source['activation']['kind'] == 'fresh-week-area2' and
                        current.get('stage',{}).get('cs') not in (None,initial['cs'])):
                    pending.append({'area':area,'reason':'unsupported-legacy-progress-retained'})
                    continue
            story.setdefault('normal_chapter_claims',{})[key] = {'week':story.get('week'),'route':_ssc_route(state)}
            if context:
                if context['source'] != source or context['descriptor'] != descriptor:
                    raise ValueError('Normal source/catalog changed; archived context retained')
                if not current or current.get('stage') != context['last_stage']:
                    context['revoked'] = True
                    raise ValueError('Explicit later writer superseded normal projection')
            else:
                if active:
                    raise ValueError('Cannot establish normal campaign during actual battle')
                day,week = _ssc_day(state),story.get('week')
                if type(day) is not int or not 0 <= day < 7 or type(week) is not int:
                    raise ValueError('Missing current normal chapter week/day')
                context = {'policy':NORMAL_CHAPTER_POLICY,'week':week,'route':_ssc_route(state),'entry_day':day,
                    'source':source,'descriptor':descriptor,'wins':carried,'revoked':False,'complete':False,
                    'before_stage':copy.deepcopy(current.get('stage')) if current else None,
                    'before_status':current['st'][0] if current else 2,'owns_status':not current or current['st'][0] == 2}
                context['epoch'] = _ssc_hash({'source':source,'week':week,'day':day,'route':context['route'],'catalog':descriptor['catalog_token']})
                if current is None:
                    current = {'id':area,'st':[1,False,False],'lv':1,'bd':{}}
                    story.setdefault('city_areas',{})[key] = current
                if context['owns_status']:
                    current['st'][0] = 1
                context['complete'] = all(any(scene in context['wins'] for scene in group) for group in descriptor['groups'])
                if context['complete']:
                    current['st'][0] = 0
                story.setdefault('normal_chapters',{'version':1,'contexts':{}})['contexts'][key] = context
            context.pop('blocked',None)
            stage = _nc_stage(state,context)
            if active and active.get('normal_chapter_source') and stage != context['last_stage']:
                raise ValueError('Actual normal fight freezes projection')
            context['last_stage'] = stage
            current['stage'] = copy.deepcopy(stage)
            notices.append(('get_area_stages_reply',{'ai':area,'st':copy.deepcopy(stage)}))
        except ValueError as error:
            if active and active.get('normal_chapter_source') and active['request']['d']['a'] == area:
                raise
            # A provenance-qualified but unsupported new catalog must not
            # silently fall through to the old arithmetic route.
            if 'source' in locals() and source is not None:
                story.setdefault('normal_chapter_claims',{})[key] = {'week':story.get('week'),'route':_ssc_route(state)}
            if context:
                context['blocked'] = str(error)
            pending.append({'area':area,'reason':str(error)})
    story['normal_chapter_pending'] = pending
    after_structure = {key:(area.get('id'),area.get('st')) for key,area in story.get('city_areas',{}).items()}
    if after_structure != before_structure:
        notices.insert(0,('get_all_area_info_reply',{'ais':{'area_%s'%key:copy.deepcopy(area) for key,area in story.get('city_areas',{}).items()},
            'cd':copy.deepcopy(story.get('city_values',{})),'sm':False}))
    return notices


def normal_chapter_admission(state,scene,area,mission,team):
    context = _nc_contexts(state).get(str(area))
    owner = stage_projection_owner(state,area)
    if owner in ('positive-special','coc','conditional'):
        return None
    claim = state['story'].get('normal_chapter_claims',{}).get(str(area))
    if not context:
        if claim == {'week':state['story'].get('week'),'route':_ssc_route(state)}:
            raise ValueError('Proven normal source has unsupported catalog; no basic fallback')
        return None
    if context['revoked'] or context.get('blocked'):
        raise ValueError('Normal campaign suspended; no basic fallback')
    unsigned = dict(context['descriptor'])
    unsigned.pop('catalog_token',None)
    if context['descriptor']['catalog_token'] != _ssc_hash(unsigned):
        raise ValueError('Normal pinned catalog fingerprint changed')
    if not _nc_receipt_chain(state,context):
        raise ValueError('Normal historical activation receipt chain changed')
    day,story = _ssc_day(state),state['story']
    current = story.get('city_areas',{}).get(str(area),{})
    status = current.get('st',[])
    mission = _ssc_plain_literal(mission,True)
    if (not _nc_live(state,context) or type(day) is not int or not context['entry_day'] <= day < 7 or
            len(status) != 3 or status[0] not in (1,5) or status[2] or context['complete'] or
            context['descriptor']['key'][1] != (0 if status[0] == 1 else 5) or
            current.get('stage') != context['last_stage'] or context['last_stage'] != _nc_stage(state,context) or
            scene != context['last_stage']['cs'] or scene in context['wins'] or
            mission != context['descriptor']['missions'].get(str(scene)) or
            any(str(hero) in story.get('banned_heroes',{}) for hero in team)):
        raise ValueError('Normal chapter source, projection, mission or party changed')
    # Recheck persistent receipts without depending on mutable catalog globals.
    source = context['source']; route_source = source['route_source']
    if route_source['kind'] == 'fresh-week':
        transition = state.get('week_protocol',{}).get('transition') or {}
        if transition.get('id') != route_source['transition'] or transition.get('target_week') != story['week']:
            raise ValueError('Missing genuine normal fresh-week receipt')
    elif (route_source['event'] not in state.get('completed_events',[]) or route_source['token'] not in state.get('week_protocol',{}).get('consumed_handoffs',[])):
        raise ValueError('Missing genuine normal route handoff')
    if source['activation'].get('kind') == 'normal-route-carry':
        activation = source['activation']
        parents = [parent for parent in story.get('normal_chapter_history',[]) if parent.get('epoch') == activation.get('epoch') and
            parent.get('archive_token') == activation.get('archive_token') and _nc_archive_hash_valid(parent) and
            parent.get('week') == story['week'] and parent.get('wins') == activation.get('wins') and
            set(parent['wins']).issubset(set(story.get('current_mission_wins',[])))]
        if not parents or not any(_nc_receipt_chain(state,parent) for parent in parents):
            raise ValueError('Normal route carry lost its genuine accepted source archive')
    proofs = source['activation'].get('proofs',[source['activation']])
    for proof in proofs:
        if source['activation']['kind'] == 'area-require' and story.get('city_areas',{}).get(str(proof['area']),{}).get('st',[None])[0] != 0:
            raise ValueError('Normal predecessor is no longer genuinely FREE')
        if 'event' in proof and (proof['event'] not in state.get('completed_events',[]) or story.get('event_effect_receipts',{}).get(proof['receipt']) != proof['event']):
            raise ValueError('Missing actual normal activation effect receipt')
        if proof.get('kind') == 'normal-clear':
            parents = list(_nc_contexts(state).values()) + story.get('normal_chapter_history',[])
            matches = [parent for parent in parents if parent.get('complete') and not parent.get('revoked') and
                parent.get('week') == story['week'] and _nc_archive_hash_valid(parent) and parent.get('epoch') == proof['epoch'] and parent.get('wins') == proof['wins'] and
                set(parent['wins']).issubset(set(story.get('current_mission_wins',[])))]
            if not matches:
                raise ValueError('Changed real predecessor victory source')
    return {'policy':NORMAL_CHAPTER_POLICY,'epoch':context['epoch'],'catalog_token':context['descriptor']['catalog_token'],
        'source':copy.deepcopy(source),'week':story['week'],'route':_ssc_route(state),'day':day,
        'area':area,'scene':scene,'team':list(team),'stage':copy.deepcopy(current['stage']),'status':list(status)}


def validate_normal_stage_source(state,active,missions=None):
    token = active.get('normal_chapter_source')
    if token is None:
        return
    if any(active.get(field) is not None for field in ('special_city_stage_source','city_stage_source','condition_mission_root')):
        raise ValueError('Conflicting normal STAGE owners')
    request = active['request']
    context = _nc_contexts(state).get(str(request['d']['a']))
    if not context:
        raise ValueError('Missing pinned normal context')
    mission = missions.get(request['s'],{}) if missions is not None else context['descriptor']['missions'].get(str(request['s']))
    if normal_chapter_admission(state,request['s'],request['d']['a'],mission,request['h']) != token:
        raise ValueError('Frozen actual normal battle source changed')


def finish_normal_chapter(state,scene):
    active = state['battle']['active']
    validate_normal_stage_source(state,active)
    context = _nc_contexts(state)[str(active['request']['d']['a'])]
    if scene != active['request']['s'] or scene in context['wins']:
        raise ValueError('Normal finish requires one genuine current battle')
    context['wins'].append(scene)
    for field in ('battle_wins','current_mission_wins'):
        state['story'][field] = sorted(set(state['story'].get(field,[])) | {scene})
    context['last_stage'] = _nc_stage(state,context)
    context['complete'] = all(any(scene in context['wins'] for scene in group) for group in context['descriptor']['groups'])
    area = state['story']['city_areas'][str(active['request']['d']['a'])]
    area['stage'] = copy.deepcopy(context['last_stage'])
    if context['complete']:
        area['st'][0] = 0
    return [('get_area_stages_reply',{'ai':area['id'],'st':copy.deepcopy(area['stage'])})]


def normal_chapter_event_replacements(state,event,row,missions):
    """Areas whose normal projection this actual event will replace/reset.

    A refresh flag alone is not a stage writer. Chapter-internal cond_event
    alternatives remain within the same grouped descriptor and keep full sl.
    The caller still commits the event and receipt before normal refresh.
    """
    abandoned = row.get('abandonMission',[])
    if type(abandoned) not in (list,tuple) or any(type(scene) is not int for scene in abandoned):
        raise ValueError('Invalid actual normal mission reset')
    contexts = _nc_contexts(state)
    result = set()
    for key,context in contexts.items():
        if context.get('revoked') or not _nc_live(state,context):
            continue
        if set(abandoned).intersection(context['descriptor']['members']):
            result.add(int(key))
    if not row.get('refreshMission'):
        return sorted(result)
    wins = set(state['story'].get('current_mission_wins',[]))
    for scene,definition in missions.items():
        if (definition.get('cond_event') != event or definition.get('release') != 1 or
                definition.get('system_type') not in (1,2)):
            continue
        area = definition.get('ch')
        context = contexts.get(str(area))
        if not context or context.get('revoked') or not _nc_live(state,context) or scene in context['descriptor']['members']:
            continue
        prerequisites = definition.get('cond',[])
        if type(prerequisites) not in (list,tuple) or any(type(parent) is not int for parent in prerequisites):
            raise ValueError('Invalid actual conditional replacement prerequisites')
        merge = len(prerequisites) > 1 and all(scene in missions.get(parent,{}).get('nextstagenums',[]) for parent in prerequisites)
        eligible = any(parent in wins for parent in prerequisites) if merge else set(prerequisites).issubset(wins)
        if eligible:
            result.add(area)
    return sorted(result)


def revoke_normal_chapter_projection(state,areas=None,reason='explicit-event-write'):
    """Writer hook preserves authority even when a later write is equal-valued."""
    active = state.get('battle',{}).get('active') or {}
    keys = set(str(area) for area in areas) if areas is not None else set(_nc_contexts(state))
    if active.get('normal_chapter_source') and str(active['request']['d']['a']) in keys:
        raise ValueError('Actual normal battle blocks explicit projection replacement')
    for key,context in _nc_contexts(state).items():
        if key in keys:
            context['revoked'] = True
            context['revocation_reason'] = reason


def expire_normal_chapters(state,route=None):
    contexts = _nc_contexts(state)
    keys = [key for key,context in contexts.items() if route is None or context['route'] != route]
    active = state.get('battle',{}).get('active') or {}
    if active.get('normal_chapter_source') and str(active['request']['d']['a']) in keys:
        raise ValueError('Actual normal battle blocks expiry')
    notices = []
    for key in keys:
        context = contexts.pop(key)
        current = state['story'].get('city_areas',{}).get(key)
        # A route departure never restores the previous route's stage.
        departing = route is not None and route != context['route']
        if departing:
            state['story'].setdefault('normal_chapter_claims',{})[key] = {'week':context['week'],'route':route}
        if (current and not departing and not context['revoked'] and _nc_live(state,context) and
                stage_projection_owner(state,int(key)) not in ('positive-special','coc','conditional') and
                current.get('stage') == context['last_stage']):
            if context['before_stage'] is None:
                current.pop('stage',None)
            else:
                current['stage'] = copy.deepcopy(context['before_stage'])
            if context['owns_status'] and not context['complete'] and current['st'][0] == 1:
                current['st'][0] = context['before_status']
        context['archive_reason'] = 'route-handoff' if departing else 'same-route-expiry'
        context['archive_token'] = _ssc_hash(context)
        state['story'].setdefault('normal_chapter_history',[]).append(copy.deepcopy(context))
        if current:
            notices.append(('get_area_stages_reply',{'ai':int(key),'st':copy.deepcopy(current.get('stage',{'cs':0,'sl':[]}))}))
    return notices


def validate_normal_chapters(state):
    document = state.get('story',{}).get('normal_chapters')
    if document is None:
        return
    if type(document) is not dict or document.get('version') != 1 or type(document.get('contexts')) is not dict:
        raise ValueError('Invalid normal chapter document')
    for key,context in document['contexts'].items():
        # Canonical save is plain JSON, never native objects or tuple keys.
        if _ssc_plain_literal(context,True) != context:
            raise ValueError('Noncanonical normal chapter state')
        if (not isinstance(key,_ssc_text) or not key.isdigit() or not 1 <= int(key) <= 8 or
                context.get('policy') != NORMAL_CHAPTER_POLICY or type(context.get('week')) is not int or
                type(context.get('entry_day')) is not int or not 0 <= context['entry_day'] < 7 or
                type(context.get('revoked')) is not bool or type(context.get('complete')) is not bool or
                type(context.get('wins')) is not list or len(set(context['wins'])) != len(context['wins']) or
                any(type(scene) is not int for scene in context['wins'])):
            raise ValueError('Invalid normal chapter context')
        descriptor = context['descriptor']; unsigned = dict(descriptor); unsigned.pop('catalog_token',None)
        if descriptor['catalog_token'] != _ssc_hash(unsigned) or descriptor['key'][0] != int(key) or descriptor['key'][3] != 0:
            raise ValueError('Invalid normal chapter catalog fingerprint')
        groups, members, snapshots = descriptor.get('groups'), descriptor.get('members'), descriptor.get('missions')
        if (type(groups) is not list or not groups or type(members) is not list or type(snapshots) is not dict or
                any(type(group) is not list or not group or any(type(scene) is not int or scene <= 0 for scene in group) for group in groups) or
                members != [scene for group in groups for scene in group] or len(set(members)) != len(members) or
                set(snapshots) != set(str(scene) for scene in members) or
                any(len(set(group).intersection(context['wins'])) > 1 for group in groups)):
            raise ValueError('Invalid normal grouped alternatives')
        for scene in members:
            mission = snapshots[str(scene)]
            if (type(mission) is not dict or type(mission.get('id')) is not int or mission['id'] != scene or
                    type(mission.get('ch')) is not int or mission['ch'] != int(key) or
                    type(mission.get('release')) is not int or mission['release'] != 1 or
                    type(mission.get('system_type')) is not int or mission['system_type'] != 1):
                raise ValueError('Invalid original normal mission snapshot')
        if context['complete'] != all(any(scene in context['wins'] for scene in group) for group in groups):
            raise ValueError('Invalid normal section completion')
        if (type(context.get('owns_status')) is not bool or type(context.get('before_status')) is not int or
                context['before_status'] not in (0,1,2,5) or not isinstance(context.get('route'),_ssc_text) or
                descriptor.get('requested_route') != context['route'] or
                descriptor['key'][1] not in (0,5) or type(descriptor['key'][1]) is not int):
            raise ValueError('Invalid normal projection ownership')
        if not set(context['wins']).issubset(set(descriptor['members'])):
            raise ValueError('Invalid normal chapter victory proof')
        if context['epoch'] != _ssc_hash({'source':context['source'],'week':context['week'],'day':context['entry_day'],'route':context['route'],'catalog':descriptor['catalog_token']}):
            raise ValueError('Invalid normal chapter source epoch')
        stage = context.get('last_stage')
        if (type(stage) is not dict or set(stage) != set(('cs','sl')) or type(stage.get('cs')) is not int or
                stage.get('sl') != descriptor['groups'] or stage['cs'] not in [0]+members or context['complete'] and stage['cs'] != 0):
            raise ValueError('Invalid canonical normal chapter projection')
        if not context.get('revoked') and _nc_live(state,context) and context['last_stage'] != _nc_stage(state,context):
            raise ValueError('Invalid normal chapter projection')
    active = state.get('battle',{}).get('active')
    if active:
        validate_normal_stage_source(state,active)
