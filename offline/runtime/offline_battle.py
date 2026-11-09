# -*- coding: ascii -*-
"""Persistent admissions for actual stock-client local battle execution.

No timer or admission grants a win. Only the client's explicit finish result can
settle the matching active fight, through a separately verified reward handler.
"""
import copy
import json
import hashlib
try:
    from offline_role_mission import (ROLE_MISSION_POLICY, compile_role_mission,
        role_mission_tables, validate_role_descriptor, bind_role_admission,
        role_battle_source, settle_role_loss, finalize_role_failure,
        prepare_role_giveup, prepare_role_rearm, validate_role_missions, native_role_combat_data)
except ImportError:
    pass

try:
    from offline_stage import validate_stage_battle_state
    from offline_event_battle import validate_event_battle_state
    from offline_wardrobe_completion import costume_resource_preflight
except ImportError:
    pass
try:
    _battle_text_types = (basestring,)
except NameError:
    _battle_text_types = (str,)


def initial_battle_state():
    return {'version': 1, 'active': None, 'receipts': []}


def validate_battle_state(state):
    if state is None:
        return
    if not isinstance(state, dict) or state.get('version') != 1:
        raise ValueError('Unsupported offline battle state')
    if not isinstance(state.get('receipts'), list) or len(state['receipts']) > 32:
        raise ValueError('Invalid offline battle receipts')
    if not isinstance(state.get('abandoned', []), list) or len(state.get('abandoned', [])) > 32:
        raise ValueError('Invalid abandoned battle history')
    active = state.get('active')
    if isinstance(active, dict) and active.get('event_policy'):
        validate_event_battle_state(state)
        return
    if isinstance(active, dict) and isinstance(active.get('request'), dict) and active['request'].get('s') != 101:
        validate_stage_battle_state(state)
        return
    if active is not None:
        if (not isinstance(active, dict) or not isinstance(active.get('request'), dict) or
                not active.get('fight_id') or not isinstance(active.get('heroes'), dict)):
            raise ValueError('Invalid active offline battle')
        request = active['request']
        heroes = request.get('h')
        if (request.get('t') != 1 or request.get('s') != 101 or request.get('d') != {'a': 1} or
                not isinstance(heroes, list) or not 1 <= len(heroes) <= 3 or
                any(type(hero) is not int for hero in heroes) or len(set(heroes)) != len(heroes) or
                set(active['heroes']) != set(str(hero) for hero in heroes) or
                not isinstance(active['fight_id'], _battle_text_types) or
                not isinstance(active.get('confirmed_heroes'), list) or
                set(active['confirmed_heroes']) != set(heroes)):
            raise ValueError('Invalid persisted first-battle admission')
        if 'combat' in active and (not isinstance(active['combat'], dict) or
                not isinstance(active['combat'].get('heroes'), dict) or
                not isinstance(active['combat'].get('skins'), list) or
                len(active['combat']['skins']) != len(heroes)):
            raise ValueError('Invalid persisted original combat data')
    seen = set()
    for receipt in state['receipts']:
        if (not isinstance(receipt, dict) or not receipt.get('fight_id') or
                receipt['fight_id'] in seen or not isinstance(receipt.get('reply'), dict)):
            raise ValueError('Invalid offline battle receipt')
        fingerprint = receipt.get('fingerprint', '')
        if (not isinstance(fingerprint, _battle_text_types) or len(fingerprint) != 64 or
                any(char not in '0123456789abcdef' for char in fingerprint)):
            raise ValueError('Invalid battle receipt fingerprint')
        seen.add(receipt['fight_id'])


def prepare_first_battle_admission(state, profile, story, arguments, mission_catalog, make_id):
    validate_battle_state(state)
    candidate = copy.deepcopy(state) if state is not None else initial_battle_state()
    request = {key: copy.deepcopy(arguments.get(key)) for key in ('t', 's', 'h', 'd')}
    if request['t'] != 1 or request['s'] != 101 or request['d'] != {'a': 1}:
        raise ValueError('Only the verified first area battle is supported')
    mission = mission_catalog.get(101)
    heroes = request['h']
    if (not mission or not mission.get('release') or mission.get('ch') != 1 or
            not isinstance(heroes, list) or any(type(hid) is not int for hid in heroes) or
            len(set(heroes)) != len(heroes) or
            not mission.get('least_hero_num', 1) <= len(heroes) <= mission.get('max_hero_num', 3)):
        raise ValueError('Invalid first-battle team or mission')
    if mission.get('va', 0) != 0 or mission.get('fatigue', 0) != 0:
        raise ValueError('First-battle cost differs from verified original table')
    area = story.get('city_areas', {}).get('1')
    if (not area or area.get('st') != [1, False, False] or
            not any(101 in stages for stages in area.get('stage', {}).get('sl', []))):
        raise ValueError('First battle area/stage is not unlocked')
    roster = (profile or {}).get('heroes', {})
    if any(str(hid) not in roster for hid in heroes):
        raise ValueError('Battle requires owned heroes')
    active = candidate['active']
    if active is not None:
        if active['request'] != request:
            raise ValueError('Another offline fight is active')
        return candidate, False
    candidate['active'] = {'fight_id': str(make_id()), 'request': request,
                           'heroes': {str(hid): copy.deepcopy(roster[str(hid)]) for hid in heroes},
                           'confirmed_heroes': list(heroes)}
    validate_battle_state(candidate)
    return candidate, True


# The stock finish payload has no fight ID. This fingerprint deduplicates the
# latest finished admission only; a delayed old result after a new identical
# admission requires a live client fight-ID check at the gateway boundary.
def battle_finish_fingerprint(arguments):
    payload = {key: arguments.get(key) for key in ('t', 's', 'h', 'x', 'w', 'e')}
    if type(payload['w']) in (int, bool) and payload['w'] in (0, 1):
        payload['w'] = int(payload['w'])
    encoded = json.dumps(payload,
                         sort_keys=True, separators=(',', ':'))
    return hashlib.sha256(encoded.encode('utf-8')).hexdigest()


def prepare_battle_finish(state, arguments, settle):
    """Settle callback returns a reply and prepared effects; never invent w."""
    validate_battle_state(state)
    if state is None:
        raise ValueError('No admitted offline battle')
    candidate = copy.deepcopy(state)
    fingerprint = battle_finish_fingerprint(arguments)
    active = candidate['active']
    if active is None:
        if candidate['receipts'] and candidate['receipts'][-1]['fingerprint'] == fingerprint:
            return candidate, copy.deepcopy(candidate['receipts'][-1]['reply']), None, False
        raise ValueError('Finish does not match an active battle')
    request = active['request']
    if (arguments.get('t') != request['t'] or arguments.get('s') != request['s'] or
            arguments.get('h') != request['h'] or not isinstance(arguments.get('x'), list) or
            any(hid not in active['confirmed_heroes'] for hid in arguments['x']) or
            type(arguments.get('w')) not in (int, bool) or arguments['w'] not in (0, 1)):
        raise ValueError('Invalid offline battle result')
    actual = copy.deepcopy(arguments)
    actual['w'] = int(actual['w'])
    reply, effects = settle(copy.deepcopy(active), actual)
    if any(reply.get(key) != arguments.get(key) for key in ('t', 's', 'h', 'x', 'w')):
        raise ValueError('Settlement must preserve actual client result')
    if not isinstance(reply.get('r'), dict):
        raise ValueError('Missing explicit verified battle reward')
    candidate['receipts'].append({'fight_id': active['fight_id'], 'fingerprint': fingerprint,
                                  'reply': copy.deepcopy(reply)})
    candidate['receipts'] = candidate['receipts'][-32:]
    candidate['active'] = None
    validate_battle_state(candidate)
    return candidate, reply, effects, True


def native_stage_combat_data(owner, active, mission):
    """Use the stock hero calculators, including equipped treasure and skills."""
    if active.get('party_kind') == 'trial':
        return native_role_combat_data(owner, active, mission)
    import copy
    from common.IdManager import IdManager
    import C_file
    import com.data.cdata.skin as skin_data
    import com.data.cdata.ui_model_data as model_data
    paths = mission.get('map_path', ())
    if not paths or not all(C_file.find_res_file(path, '') for path in paths):
        raise ValueError('Original first-battle scene resource is absent')
    identity = IdManager.id2str(owner.id)
    hero_level = active.get('hero_level', mission.get('adjust_hero_lv', owner.level))
    if not isinstance(hero_level, int) or hero_level < 1:
        raise ValueError('Invalid original battle hero level')
    heroes, skins = {}, []
    for hero_id in active['request']['h']:
        hero = owner.heroMgrData.getHero(hero_id)
        if hero is None:
            raise ValueError('Missing native battle hero')
        star_skills, artifact_skills = hero.calcSkill()
        data = {'id': hero_id, 'd': hero.calcAllAttr(hero_level), 'a': {},
                's': [[list(pair) for pair in star_skills], [list(pair) for pair in artifact_skills]],
                't': list(hero.calcTricks()), 'ai': list(owner.heroMgrData.getArtifactInfo(hero_id)),
                'as': owner.heroMgrData.getAwakeStage(hero_id), 'lv': hero_level}
        if not data['d'] or not data['s'][0]:
            raise ValueError('Cannot admit hero without real attributes and skills')
        heroes[str(('', hero_id))] = data
        heroes[str((identity, hero_id))] = copy.deepcopy(data)
        skin = copy.deepcopy(hero.getCurSkinObj().getPersistentDict())
        available, missing = costume_resource_preflight(skin['i'], skin_data.data,
            model_data.data, lambda path: bool(C_file.find_res_file(path, '')))
        if not available:
            raise ValueError('Original selected battle skin resources are absent: %s' % missing)
        skins.append(skin)
    return {'heroes': heroes, 'skins': skins, 'hero_lv': hero_level,
            'monster_lv': active.get('monster_level', mission.get('monsterLvFirstWeek', 1))}


def native_first_battle_combat_data(owner, active, mission):
    return native_stage_combat_data(owner, active, mission)


def settle_stage_economy(profile, active, result, fight_rewards, player_exp,
                         random_rewards, common_rewards, grant_treasure, mission):
    """Original base rewards plus a documented deterministic weighted drop.

    Hashing the persisted fight ID chooses one original weighted pool outcome.
    Outcome zero means no item drop; it never suppresses real base money/exp.
    """
    candidate = copy.deepcopy(profile)
    reply = {key: copy.deepcopy(result[key]) for key in ('t', 's', 'h', 'x', 'w')}
    reply['r'] = {}
    notices, granted = [], []
    if result['w'] == 0:
        return reply, {'profile': candidate, 'notices': notices, 'granted': granted}
    economy = candidate.get('economy')
    if not economy:
        raise ValueError('Missing persistent original battle economy')
    level, previous_exp = economy['level'], economy['exp']
    base = fight_rewards.get(active.get('reward_level', level))
    if not base:
        raise ValueError('Missing original player-level fight reward')
    prize = mission.get('prize', 1)
    if (mission.get('id') == 131 and prize == 13 and active.get('request',{}).get('t') == 2 and
            active['request'].get('s') == 131 and active.get('raw_prize') == 13 and
            active.get('event_reward_policy') == 'scene131-prize13-enabled-base-offline-v1'):
        # The sole anomalous original flag has no recovered separate mapping.
        # Explicit bounded offline compatibility: player-level enabled base
        # reward, preserving raw13/policy in admission and settlement receipt.
        prize = 1
    if type(prize) is not int or prize not in (0, 1):
        raise ValueError('Unsupported original stage reward flag')
    money, experience = (base['money'], base['exp']) if prize else (0, 0)
    economy['money'] += money
    remaining = previous_exp + experience
    max_level = max(player_exp)
    while level < max_level:
        threshold = player_exp[level]['lv_exp']
        if type(threshold) is not int or threshold <= 0:
            raise ValueError('Invalid original player level threshold')
        if remaining < threshold:
            break
        remaining -= threshold
        level += 1
    if level == max_level:
        remaining = min(remaining, player_exp[level]['lv_exp'])
    economy['level'], economy['exp'] = level, remaining
    reward = {'money': money, 'exp': experience, 'oe': previous_exp,
              'ol': profile['economy']['level'],
              'ce': remaining, 'cl': level, 'item': [], 'hero': [], 'treasure': [], 'stage': result['s']}
    notices.extend([('updateMoney', {'v': economy['money']}),
                    ('updateExpAndLevel', {'e': remaining, 'lv': level})])
    for hero_id in ([] if active.get('party_kind') == 'trial' else result['h']):
        hero = candidate['heroes'][str(hero_id)]
        hero['ef'] = min(100, hero['ef'] + (base.get('friendly', 0) if prize else 0))
        notices.append(('updateFriendlyValue', {'h': hero_id, 'v': hero['ef']}))
    inventory = candidate.get('treasures')
    if not inventory:
        raise ValueError('Missing persistent treasure inventory')
    owned_ids = set(item['u'] for item in inventory['items'])
    for index, pool_id in enumerate(base.get('items', ()) if prize else ()):
        weights = random_rewards.get(pool_id, {}).get('weights')
        if not weights or any(type(weight) is not int or weight <= 0 for reward_id, weight in weights):
            raise ValueError('Invalid original battle drop pool')
        total = sum(weight for reward_id, weight in weights)
        tag = 'first-battle-drop-v1' if result['s'] == 101 else 'stage-drop-v1'
        seed = ('%s:%s:%s:%s' % (tag, active['fight_id'], pool_id, index)).encode('ascii')
        roll = int(hashlib.sha256(seed).hexdigest(), 16) % total
        selected = None
        for reward_id, weight in weights:
            if roll < weight:
                selected = reward_id
                break
            roll -= weight
        if selected == 0:
            continue
        definition = common_rewards.get(selected)
        allowed = set(('id', 'treasure', 'treasureNum', 'treasureLevel', 'tradeType'))
        if not definition or set(definition) - allowed:
            raise ValueError('Unsupported original weighted battle reward')
        templates = definition.get('treasure', ())
        counts, classes = definition.get('treasureNum', ()), definition.get('treasureLevel', ())
        if not templates or len(templates) != len(counts) or len(counts) != len(classes):
            raise ValueError('Malformed original treasure reward')
        for template, count, quality in zip(templates, counts, classes):
            if type(count) is not int or not 1 <= count <= 100:
                raise ValueError('Unsupported original treasure quantity')
            ids = []
            for unused in range(count):
                item = grant_treasure(template, quality, definition.get('tradeType', 1))
                if item['u'] in owned_ids:
                    raise ValueError('Reward treasure ObjectId collision')
                owned_ids.add(item['u'])
                inventory['items'].append(item)
                granted.append(copy.deepcopy(item))
                ids.append(item['u'])
            reward['treasure'].append([template, quality, count, ids])
    reply['r'] = reward
    return reply, {'profile': candidate, 'notices': notices, 'granted': granted}


def settle_first_battle_economy(profile, active, result, fight_rewards, player_exp,
                                 random_rewards, common_rewards, grant_treasure):
    return settle_stage_economy(profile, active, result, fight_rewards, player_exp,
        random_rewards, common_rewards, grant_treasure, {'prize': 1})


def offer_pending_battle_resume(proxy):
    """Resume from the original scene start, or explicitly abandon without pay."""
    active = proxy.battle.get('active')
    if (not active or getattr(proxy, '_battle_resume_offered', None) == active['fight_id'] or
            getattr(proxy, '_battle_resume_pending', False)):
        return
    proxy._battle_resume_pending = True
    fight_id = active['fight_id']
    resume_owner = proxy.owner
    role_source = role_battle_source(proxy.progress_snapshot()) if active.get('party_kind') == 'trial' else None
    def live():
        import gg
        current = proxy.battle.get('active')
        return (proxy.owner is resume_owner and getattr(gg,'avatar',None) is resume_owner and current and
            current.get('fight_id') == fight_id and
            (role_source is None or role_battle_source(proxy.progress_snapshot()) == role_source))

    def show():
        import gg
        import com.const as const
        current = proxy.battle.get('active')
        if not live():
            proxy._battle_resume_pending = False
            return
        panel = gg.ui.panels.common_confirm
        if (gg.logic.game_state.current != const.GameState.CITY or gg.ui._dialogue or
                (panel.valid and panel.visible)):
            proxy.defer(200, guarded_show)
            return

        def resume():
            current = proxy.battle.get('active')
            if live():
                proxy.owner.combatData.reset()
                request = current['request']
                if request['t'] == 2:
                    proxy.owner.battleEnterWithEventMode(request['s'], list(request['h']))
                else:
                    proxy.owner.battleEnterWithStageMode(request['d']['a'], request['s'], list(request['h']))

        def abandon():
            if not live():
                return
            proxy.reset_pending_battle(fight_id)
            proxy.owner.combatData.reset()
        panel.notify_confirm(
            u'\u4e0a\u6b21\u6218\u6597\u5c1a\u672a\u7ed3\u7b97\u3002#r\u7ee7\u7eed\u5c06\u4ece\u5173\u5361\u8d77\u70b9\u91cd\u65b0\u5f00\u59cb\uff1b\u653e\u5f03\u4e0d\u53d1\u653e\u5956\u52b1\u3002',
            resume, confirm_label=u'\u7ee7\u7eed\u6218\u6597', cancel_cb=abandon,
            cancel_label=u'\u653e\u5f03\u672c\u6b21\u6218\u6597')
        proxy._battle_resume_offered, proxy._battle_resume_pending = fight_id, False
    def guarded_show():
        try:
            return show()
        except Exception:
            proxy._battle_resume_pending = False
            raise
    proxy.defer(200, guarded_show)
