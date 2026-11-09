# -*- coding: ascii -*-
"""Occurrence-bound original BattleType.EVENT admissions and actual finishes.

Wire type2 is EVENT, independent of mission.system_type. Owned system_type2 and typed fixed-cast system_type4 providers remain
separate; activity/test modes stay explicit.
Native combat data uses existing native_stage_combat_data stock calculators.
"""
try:
    from offline_role_mission import (ROLE_MISSION_POLICY, compile_role_mission,
        role_mission_tables, validate_role_descriptor, bind_role_admission,
        role_battle_source, _rm_literal, settle_role_loss, finalize_role_failure,
        prepare_role_giveup, prepare_role_rearm, validate_role_missions, native_role_combat_data)
except ImportError:
    pass

try:
    from offline_flashback import flashback_context, flashback_token
except ImportError:
    pass

try:
    from offline_battle_terminal import mint_event_terminal_offers
except ImportError:
    pass

import copy
import hashlib
import json

EVENT_BATTLE_POLICY = 'original-event-pve-occurrence-v1'
# Exact original com.const.QIANSHI_SCENE_SET; a native ownership exception,
# not an EVENT admission whitelist or permission to fabricate trial actors.
_EB_QIANSHI_SCENES = (401006,401009,401010,401011,401012)


def original_event_default_party(scene, mission, roster, banned):
    defaults = list(mission.get('defaultHeroes') or ())
    if mission.get('system_type') == 4:
        return defaults
    targets = set(mission.get('target_hero',())) if scene in _EB_QIANSHI_SCENES else set()
    return [hero for hero in defaults if hero in targets or str(hero) in roster and str(hero) not in banned]


def event_battle_snapshot(state):
    counts = {}
    for gate in state.get('story', {}).get('event_battle_gates', {}).values():
        if gate.get('status') in ('open', 'active') and gate.get('event') in state.get('processing_events', []):
            episode = gate.get('role_episode')
            count = episode['remaining'] if episode else 1
            counts[gate['scene']] = counts.get(gate['scene'], 0) + count
    return {'ab': [[scene, count] for scene, count in sorted(counts.items())]}


def prepare_event_battle_gate(state, event, event_catalog, receipt_key):
    candidate = copy.deepcopy(state)
    row = event_catalog.get(event)
    if not row or not row.get('release') or type(row.get('enterBattle')) is not int:
        return candidate, [], False
    if event not in candidate.get('processing_events', []):
        raise ValueError('Event battle gate requires this actual processing event')
    if receipt_key is None or not str(receipt_key):
        raise ValueError('Actual event occurrence key required')
    key = str(receipt_key)
    story = candidate['story']
    gates = story.setdefault('event_battle_gates', {})
    expected = {'event':event,'scene':row['enterBattle'],'occurrence':key}
    if key in gates:
        if any(gates[key].get(k) != v for k,v in expected.items()):
            raise ValueError('Occurrence gate collision')
    else:
        gates[key] = dict(expected,status='open',fight_id=None)
    story['event_battle_cursor'] = key
    counts = dict(event_battle_snapshot(candidate)['ab'])
    scene = row['enterBattle']
    notice = ('setEventBattleStage',{'s':scene,'n':counts.get(scene,0)})
    return candidate, [notice], candidate != state


def validate_event_battle_state(battle):
    if not isinstance(battle,dict) or battle.get('version') != 1 or not isinstance(battle.get('receipts'),list):
        raise ValueError('Invalid EVENT battle container')
    seen = set()
    for receipt in battle['receipts']:
        fingerprint = receipt.get('fingerprint', '')
        if (not receipt.get('fight_id') or receipt['fight_id'] in seen or not isinstance(receipt.get('reply'),dict) or
                len(fingerprint) != 64 or any(c not in '0123456789abcdef' for c in fingerprint)):
            raise ValueError('Invalid duplicate battle receipt')
        seen.add(receipt['fight_id'])
    active = battle.get('active')
    if active is None: return
    request = active.get('request',{})
    team = request.get('h')
    if (active.get('event_policy') != EVENT_BATTLE_POLICY or request.get('t') != 2 or
            type(request.get('s')) is not int or request.get('d') != {} or
            not isinstance(team,list) or not team or any(type(h) is not int for h in team) or
            len(set(team)) != len(team) or not active.get('fight_id') or active['fight_id'] in seen or
            set(active.get('heroes',{})) != set(str(h) for h in team) or
            set(active.get('confirmed_heroes',[])) != set(team) or
            not active.get('event_occurrence') or type(active.get('event_id')) is not int):
        raise ValueError('Invalid original EVENT admission')
    if active.get('party_kind') == 'trial':
        validate_role_descriptor(active.get('role_mission'))
    elif active.get('party_kind','owned') != 'owned':
        raise ValueError('Unknown EVENT party kind')
    if any(type(active.get(k)) is not int or active[k] < 1 for k in
            ('reward_level','hero_level','monster_level')):
        raise ValueError('Invalid pinned EVENT levels')
    if any(type(active.get('costs',{}).get(k)) is not int or active['costs'][k] < 0
           for k in ('actions','fatigue')):
        raise ValueError('Invalid pinned EVENT costs')


def prepare_event_battle_admission(state, arguments, missions, event_catalog, make_id, role_tables=None, role_owner=None):
    candidate = copy.deepcopy(state)
    battle = candidate.setdefault('battle',{'version':1,'active':None,'receipts':[]})
    request = {key:copy.deepcopy(arguments.get(key)) for key in ('t','s','h','d')}
    if type(request['t']) is not int or request['t'] != 2 or type(request['s']) is not int or request['d'] != {}:
        raise ValueError('Original EVENT requires wire t2 and empty d, not mission.system_type')
    if battle.get('active'):
        validate_event_battle_state(battle)
        active = battle['active']
        validate_role_missions(candidate)
        if missions.get(request['s'],{}).get('system_type') == 4 and active.get('party_kind') != 'trial':
            raise ValueError('Legacy untyped ROLE admission requires explicit clean retry')
        gate = candidate.get('story', {}).get('event_battle_gates', {}).get(active['event_occurrence'])
        if (active['request'] != request or not gate or gate.get('fight_id') != active['fight_id'] or
                gate.get('status') != 'active' or active['event_id'] not in candidate.get('processing_events', []) or
                candidate['story'].get('event_battle_cursor') != active['event_occurrence']):
            raise ValueError('Another actual battle/occurrence is active')
        return candidate, False
    scene, team = request['s'], request['h']
    mission = missions.get(scene)
    if not mission or not mission.get('release') or mission.get('system_type') not in (2,4):
        raise ValueError('Unsupported original event combat mode; system_type2 PVE only')
    trial = mission.get('system_type') == 4
    if trial and mission.get('customizeHero') != 1:
        raise ValueError('Unsupported ROLE event combat mode without complete fixed customization')
    if trial and role_tables is None:
        role_tables = role_mission_tables(scene)
    descriptor = compile_role_mission(scene, team, role_tables) if trial else None
    prize131_policy = scene == 131 and mission.get('id') == 131 and mission.get('prize') == 13
    if mission.get('prize',1) not in (0,1) and not prize131_policy:
        raise ValueError('Special event reward category requires a separate reward policy')
    profile = candidate.get('profile') or {}
    roster = profile.get('heroes',{})
    banned = candidate['story'].get('banned_heroes',{})
    targets = set(mission.get('target_hero',())) if scene in _EB_QIANSHI_SCENES else set()
    defaults = mission.get('defaultHeroes')
    if (not isinstance(team,list) or any(type(h) is not int for h in team) or
            len(set(team)) != len(team) or len(team) < mission.get('least_hero_num',1)):
        raise ValueError('Invalid original EVENT team size')
    if defaults:
        # Match the actual native ordered filter. The default fastpath only
        # checks least, preserving scene500 full2/max1 without granting heroes.
        if original_event_default_party(scene,mission,roster,banned) != team:
            raise ValueError('Original defaultHeroes ordered available party must be preserved')
    elif len(team) > mission.get('max_hero_num',3):
        raise ValueError('Selected EVENT team exceeds original maximum')
    story = candidate['story']
    if scene in story.get('abandoned_missions', []):
        raise ValueError('Original story abandoned this EVENT scene')
    gates = story.get('event_battle_gates',{})
    key = story.get('event_battle_cursor')
    gate = gates.get(key)
    if (not gate or gate.get('scene') != scene or gate.get('status') != 'open' or
            gate.get('event') not in candidate.get('processing_events',[]) or
            not event_catalog.get(gate.get('event'),{}).get('release') or
            event_catalog.get(gate.get('event'),{}).get('enterBattle') != scene):
        raise ValueError('No current original event occurrence admits this scene')
    profile = candidate.get('profile') or {}
    roster = profile.get('heroes',{})
    banned = story.get('banned_heroes',{})
    if not trial and any(str(h) not in roster for h in team):
        raise ValueError('EVENT team requires real original hero snapshots; unowned QIANSHI target assembly unsupported')
    if not trial and any(str(h) in banned and h not in targets for h in team):
        raise ValueError('Self-selected EVENT team requires available owned heroes')
    economy = profile.get('economy') or {}
    level = economy.get('level')
    hero_level = max(actor['fixed']['level'] for actor in descriptor['actors'].values()) if trial else mission.get('adjust_hero_lv',level)
    monster_level = mission.get('adjust_monster_lv', mission.get(
        'monsterLvFirstWeek' if story.get('week',0) == 0 else 'monsterLvSecondWeek', level))
    if any(type(v) is not int or v < 1 for v in (level,hero_level,monster_level)):
        raise ValueError('Missing original EVENT level configuration')
    if trial:
        monster_level = 1
    force = story.get('city_values',{}).get('fv',0)
    actions = mission.get('va',0)
    fatigue = mission.get('fatigue',0) if force >= mission.get('force_recommend',0) else mission.get('overFatigue',0)
    if any(type(v) is not int or v < 0 for v in (actions,fatigue)):
        raise ValueError('Invalid original EVENT costs')
    flashback = flashback_context(candidate)
    if flashback and ((candidate.get('city_actions') or {}).get('patrol') or
            story.get('patrol_pending') or story.get('patrol_reward_pending')):
        raise ValueError('Actual patrol must finish before flashback EVENT')
    if (not flashback and story.get('city_values',{}).get('av',0) < actions) or (not trial and any(roster[str(h)].get('cf',0) < fatigue for h in team)):
        raise ValueError('Insufficient original EVENT action/fatigue')
    fight = str(make_id())
    if not fight or any(r['fight_id'] == fight for r in battle['receipts']):
        raise ValueError('EVENT fight identity must be fresh')
    battle['active'] = {'event_policy':EVENT_BATTLE_POLICY,'event_id':gate['event'],
        'event_occurrence':key,'fight_id':fight,'request':request,
        'heroes':copy.deepcopy(descriptor['actors']) if trial else {str(h):copy.deepcopy(roster[str(h)]) for h in team},
        'party_kind':'trial' if trial else 'owned',
        'confirmed_heroes':list(team),'reward_level':level,'hero_level':hero_level,
        'monster_level':monster_level,'costs':{'actions':actions,'fatigue':fatigue},
        'raw_prize':mission.get('prize',1),
        'event_reward_policy':'scene131-prize13-enabled-base-offline-v1' if prize131_policy else 'original-prize0-or1'}
    if trial:
        if not isinstance(role_owner, (str,type(u''))) or not role_owner:
            raise ValueError('ROLE admission requires actual account identity')
        battle['active']['role_owner'] = role_owner
        bind_role_admission(candidate,gate,battle['active'],role_tables)
    if flashback:
        battle['active']['flashback_token'] = flashback_token(candidate)
    gate['status'],gate['fight_id'] = 'active',fight
    validate_event_battle_state(battle)
    validate_role_missions(candidate)
    return candidate, True


def _event_finish_fingerprint(arguments):
    payload={k:arguments.get(k) for k in ('t','s','h','x','w','e')}
    if type(payload['w']) in (int,bool) and payload['w'] in (0,1):payload['w']=int(payload['w'])
    return hashlib.sha256(json.dumps(payload,sort_keys=True,separators=(',',':')).encode('utf-8')).hexdigest()


def prepare_event_battle_finish(state, arguments, settle, source_fight_id, missions=None, event_catalog=None):
    candidate = copy.deepcopy(state)
    battle = candidate.get('battle')
    validate_event_battle_state(battle)
    validate_role_missions(candidate)
    fingerprint = _event_finish_fingerprint(arguments)
    active = battle.get('active')
    if active is None:
        if battle['receipts']:
            last=battle['receipts'][-1]
            if last['fight_id']==source_fight_id and last['fingerprint']==fingerprint:
                return candidate,copy.deepcopy(last['reply']),None,False
        raise ValueError('No matching EVENT finish admission')
    if active.get('party_kind') == 'trial' and missions is not None:
        if _rm_literal(missions.get(active['request']['s'],{})) != active['role_mission']['mission']:
            raise ValueError('Original ROLE mission changed before actual result')
    request=active['request']
    if (source_fight_id != active['fight_id'] or
            any(arguments.get(k)!=request[k] for k in ('t','s','h')) or
            not isinstance(arguments.get('x'),list) or len(set(arguments['x'])) != len(arguments['x']) or
            any(type(h) is not int or h not in active['confirmed_heroes'] for h in arguments['x']) or
            type(arguments.get('w')) not in (int,bool) or arguments['w'] not in (0,1)):
        raise ValueError('EVENT actual result identity/team mismatch')
    gate=candidate['story'].get('event_battle_gates',{}).get(active['event_occurrence'])
    if (not gate or gate.get('fight_id')!=source_fight_id or gate.get('status')!='active' or
            active['event_id'] not in candidate.get('processing_events', [])):
        raise ValueError('EVENT occurrence is not bound to this actual fight')
    actual=copy.deepcopy(arguments);actual['w']=int(actual['w'])
    reply,effects=settle(copy.deepcopy(active),actual)
    if (any(reply.get(k)!=actual[k] for k in ('t','s','h','x','w')) or
            not isinstance(reply.get('r'),dict) or not isinstance(effects.get('profile'),dict)):
        raise ValueError('EVENT settlement must preserve the actual engine result')
    if active.get('party_kind') == 'trial' and effects['profile'].get('heroes') != state['profile'].get('heroes'):
        raise ValueError('ROLE trial result cannot mutate permanent heroes')
    notices=copy.deepcopy(effects.get('notices',[]))
    completion=None
    terminal_failure=None
    if not actual['w']:
        if reply['r'] or effects['profile']!=state['profile'] or notices or effects.get('granted'):
            raise ValueError('Actual EVENT loss cannot grant economy or progress')
        fail_events = (missions or {}).get(request['s'], {}).get('failEvent', ())
        released_failures = [event for event in fail_events if (event_catalog or {}).get(event, {}).get('release')]
        exhausted = False
        if active.get('party_kind') == 'trial':
            exhausted = settle_role_loss(candidate,gate,active,source_fight_id)
            if exhausted:
                finalize_role_failure(candidate,gate,missions or {},event_catalog or {},'actual-budget-exhausted')
                terminal_failure = candidate['story'].get('event_terminal_failures',{}).get(str(active['event_id']))
        if released_failures and active.get('party_kind') != 'trial':
            gate['status'] = 'terminal-loss'
            terminal_failure = {'event':active['event_id'], 'occurrence':active['event_occurrence'],
                'fight_id':source_fight_id, 'scene':request['s'], 'outcome':0,
                'fail_events':list(released_failures), 'week':candidate['story'].get('week',0),
                'day':candidate.get('day',{}).get('stock_day',candidate['story'].get('date',0))}
            candidate['processing_events'] = [event for event in candidate['processing_events'] if event != active['event_id']]
            candidate['available_events'] = [entry for entry in candidate['available_events'] if entry[0] != active['event_id']]
            previous_pending = candidate['story'].get('pending_effects', {}).pop(str(active['event_id']), None)
            if previous_pending is not None:
                terminal_failure['superseded_pending_effect'] = copy.deepcopy(previous_pending)
            candidate['story'].setdefault('event_terminal_failures', {})[str(active['event_id'])] = copy.deepcopy(terminal_failure)
        elif active.get('party_kind') != 'trial':
            gate['status'],gate['fight_id']='open',None
    else:
        candidate['profile']=copy.deepcopy(effects['profile'])
        story=candidate['story'];city=story.setdefault('city_values',{})
        costs=active['costs']
        if active.get('flashback_token') is not None:
            if active['flashback_token'] != flashback_token(candidate):
                raise ValueError('Reserved EVENT flashback context changed')
        else:
            if city.get('av',0)<costs['actions']:raise ValueError('Reserved EVENT actions changed')
            if costs['actions']:city['av']-=costs['actions']
        for h in ([] if active.get('party_kind') == 'trial' else request['h']):
            hero=candidate['profile']['heroes'][str(h)]
            if hero.get('cf',0)<costs['fatigue']:raise ValueError('Reserved EVENT fatigue changed')
            hero['cf']-=costs['fatigue']
            if costs['fatigue']:notices.append(('updateCurFatigueValue',{'h':h,'v':hero['cf']}))
        gate['status']='won'
        completion={'event':active['event_id'],'occurrence':active['event_occurrence'],
            'fight_id':source_fight_id,'scene':request['s'],'token':'battle:%s'%request['s']}
        if active.get('party_kind') == 'trial':
            completion['party_kind'] = 'trial'
            completion['role_epoch'] = active['role_epoch']
            completion['provider'] = ROLE_MISSION_POLICY
            completion['party'] = list(request['h'])
            completion['catalog_token'] = active['role_mission']['catalog_token']
            gate['role_episode']['loss_consumed'] = True
            gate['role_episode']['audit'].append({'fight':source_fight_id,'epoch':active['role_epoch'],'outcome':1})
        story.setdefault('event_battle_wins',{})[active['event_occurrence']]=copy.deepcopy(completion)
        story['event_battle_wins'][active['event_occurrence']]['winning_terminal_provenance'] = {
            'party_kind':active.get('party_kind','owned'),
            'week': story.get('week', 0), 'party': copy.deepcopy(request['h']),
            'result_fingerprint': fingerprint}
        wins=story.setdefault('battle_wins',[])
        if request['s'] not in wins:wins.append(request['s']);wins.sort()
    counts=dict(event_battle_snapshot(candidate)['ab'])
    notices.append(('setEventBattleStage',{'s':request['s'],'n':counts.get(request['s'],0)}))
    battle['receipts'].append({'fight_id':source_fight_id,'fingerprint':fingerprint,
        'reply':copy.deepcopy(reply),'event_occurrence':active['event_occurrence'],
        'event_policy':EVENT_BATTLE_POLICY,'raw_prize':active.get('raw_prize'),
        'event_reward_policy':active.get('event_reward_policy'),
        'party_kind':active.get('party_kind','owned'),'role_epoch':active.get('role_epoch'),
        'provider':ROLE_MISSION_POLICY if active.get('party_kind') == 'trial' else EVENT_BATTLE_POLICY,
        'catalog_token':active.get('role_mission',{}).get('catalog_token')})
    if actual['w'] and missions is not None and event_catalog is not None:
        mint_event_terminal_offers(candidate, missions, event_catalog, active, battle['receipts'][-1])
    battle['receipts']=battle['receipts'][-32:];battle['active']=None
    validate_event_battle_state(battle)
    validate_role_missions(candidate)
    effects=dict(copy.deepcopy(effects),profile=copy.deepcopy(candidate['profile']),
        notices=notices,event_completion=completion,event_terminal_failure=terminal_failure)
    return candidate,reply,effects,True
