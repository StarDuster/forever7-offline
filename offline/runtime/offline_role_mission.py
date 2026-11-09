# -*- coding: ascii -*-
"""Finite original ROLE_MISSION trial cast and occurrence-bound challenge policy.

Original server assembly is unavailable. Artifact points, scalar liberation,
player-only prize1 and total-attempt retry interpretation are explicit offline
choices. Catalog literals are copied locally; no owned actor is ever replaced.
"""
import copy
import hashlib
import json
import math
try:
    from offline_wardrobe_completion import costume_resource_preflight
except ImportError:
    pass
try:
    _rm_text = (basestring,)
    _rm_integers = (int,long)
except NameError:
    _rm_text = (str,)
    _rm_integers = (int,)
ROLE_MISSION_POLICY = 'offline-original-role-event-trial-v1'


def _rm_literal(value, stack=None):
    """JSON durable snapshot; exact floats use lossless hexadecimal literals."""
    stack = set() if stack is None else stack
    if value is None or type(value) is bool or type(value) in _rm_integers:
        return value
    if isinstance(value, bytes) and not isinstance(value, str):
        return value.decode('utf-8', 'strict')
    if isinstance(value, _rm_text):
        if isinstance(value, str):
            try:
                return value.decode('utf-8', 'strict')
            except AttributeError:
                return value
        return value
    if type(value) is float:
        if math.isnan(value) or math.isinf(value):
            raise ValueError('Nonfinite ROLE catalog number')
        return {'__role_float__': value.hex()}
    ident = id(value)
    if ident in stack or len(stack) >= 64:
        raise ValueError('Cyclic ROLE catalog literal')
    stack.add(ident)
    try:
        if type(value) in (list, tuple):
            return [_rm_literal(item, stack) for item in value]
        if callable(getattr(value, 'items', None)):
            result = {}
            for key, item in value.items():
                if type(key) is int:
                    key = str(key)
                else:
                    key = _rm_literal(key, stack)
                if not isinstance(key, _rm_text) or key in result or key == '__role_float__':
                    raise ValueError('Ambiguous ROLE catalog literal key')
                result[key] = _rm_literal(item, stack)
            return result
        raise ValueError('Unsupported nonliteral ROLE catalog object')
    finally:
        stack.remove(ident)


def _rm_unpack(value):
    if type(value) is dict:
        if set(value) == set(['__role_float__']):
            return float.fromhex(value['__role_float__'])
        return {key: _rm_unpack(item) for key, item in value.items()}
    if type(value) is list:
        return [_rm_unpack(item) for item in value]
    return value


def _rm_hash(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=True,
        separators=(',', ':')).encode('ascii')).hexdigest()


def _rm_positive(value, label, maximum=100000):
    if type(value) is not int or not 0 < value <= maximum:
        raise ValueError('Invalid ROLE %s' % label)
    return value


def role_mission_tables(scene=None):
    names = ('mission', 'mission_hero_attr', 'hero', 'hero_star_attr',
        'hero_star_skill', 'hero_artifact_attr', 'hero_artifact_allot_lv_point_data',
        'hero_treasure_generate', 'hero_treasure', 'item_data', 'skin',
        'liberate_tupo', 'liberate_lv', 'treasure_exclusive', 'hero_treasure_suit',
        'skill', 'trick_data', 'monster', 'hero_treasure_third_attr')
    result = {name: __import__('com.data.cdata.' + name, fromlist=['data']).data for name in names}
    if scene is not None:
        mission = result['mission'].get(scene, {})
        source = mission.get('dataSource')
        if not isinstance(source, _rm_text) or not source or not all(c.isalnum() or c == '_' for c in source):
            raise ValueError('Unsupported original ROLE dataSource')
        for prefix in ('refresh_hero_', 'refresh_monster_'):
            result[prefix + source] = __import__('com.data.cdata.' + prefix + source, fromlist=['data']).data
    return result


def compile_role_mission(scene, team, tables):
    mission = _rm_literal(tables.get('mission', {}).get(scene, {}))
    if (mission.get('id') != scene or type(scene) is not int or mission.get('release') != 1 or
            mission.get('system_type') != 4 or mission.get('customizeHero') != 1 or
            type(team) is not list or not team or mission.get('defaultHeroes') != team or
            len(set(team)) != len(team) or any(type(hero) is not int for hero in team)):
        raise ValueError('Complete original ROLE4 customized default party required')
    if mission.get('target_hero') or mission.get('target_heroes'):
        raise ValueError('Partial ROLE target assembly requires separate policy')
    if mission.get('prize', 1) != 1 or any(mission.get(field, 0) != 0 for field in
            ('va', 'fatigue', 'overFatigue', 'force_recommend')):
        raise ValueError('ROLE trial supports player-only prize1 and zero costs')
    if (type(mission.get('system_type')) is not int or type(mission.get('customizeHero')) is not int or
            type(mission.get('release')) is not int or len(team) < mission.get('least_hero_num',1)):
        raise ValueError('Invalid original ROLE numeric mode or minimum party')
    attempts = _rm_positive(mission.get('retry_times'), 'total attempts', 100)
    actors, references = {}, {}
    item_ids, suit_ids, trick_ids = set(), set(), set()
    for index, hero in enumerate(team):
        row = _rm_literal(tables.get('mission_hero_attr', {}).get((scene, hero), {}))
        if (row.get('mission_id') != scene or row.get('heroid') != hero or row.get('pos_id') != index + 1 or
                set(row) - set(('mission_id','heroid','pos_id','hero_name','level','starLevel','starOrder',
                                'artifact','treasure','liberate','awake','skin_id'))):
            raise ValueError('Incomplete or unsupported original ROLE hero snapshot')
        for field, maximum in (('level',100),('starLevel',4),('starOrder',4)):
            _rm_positive(row.get(field), field, maximum)
        artifact = row.get('artifact')
        expected_attrs = set(('_base_max_hp','_base_phy_att_str','_base_mag_att_str','_base_phy_def','_base_mag_def'))
        if (type(artifact) is not dict or set(artifact) != set(('attrs','order')) or
                type(artifact['order']) is not int or not 0 <= artifact['order'] <= 30 or
                type(artifact['attrs']) is not dict or set(artifact['attrs']) != expected_attrs or
                any(type(value) is not int or value < 0 for value in artifact['attrs'].values()) or
                row.get('awake',0) != 0 or type(row.get('liberate',0)) is not int or not 0 <= row.get('liberate',0) <= 100):
            raise ValueError('Unsupported original ROLE artifact/liberation/awake snapshot')
        hero_row = _rm_literal(tables.get('hero', {}).get(hero, {}))
        star = _rm_literal(tables.get('hero_star_skill', {}).get((hero,row['starLevel'],row['starOrder']), {}))
        if not hero_row or not star.get('cumSkills') or (row['starLevel'],row['starOrder']) not in tables.get('hero_star_attr', {}):
            raise ValueError('Missing ROLE base/star calculator definitions')
        arti = _rm_literal(tables.get('hero_artifact_attr', {}).get((hero,artifact['order']), {}))
        if artifact['order'] and not arti:
            raise ValueError('Missing ROLE artifact definition')
        skill_pairs = list(star['cumSkills'].items()) + list(arti.get('cumskills',{}).items())
        if any((int(skill),level) not in tables.get('skill',{}) for skill,level in skill_pairs):
            raise ValueError('Missing ROLE skill resource definition')
        equipment = []
        if type(row.get('treasure')) is not list:
            raise ValueError('Missing ROLE fixed treasure list')
        for slot, entry in enumerate(row['treasure']):
            if type(entry) is not dict or set(entry) != set(['item_gen_id']):
                raise ValueError('Unsupported ROLE equipment generator')
            generator = entry['item_gen_id']
            template = _rm_literal(tables.get('hero_treasure_generate', {}).get(generator, {}))
            raw = template.get('dumps_info')
            if not isinstance(raw, _rm_text):
                raise ValueError('ROLE fixed template requires full dumps_info')
            fixed = _rm_literal(json.loads(raw))
            if (type(fixed) is not dict or type(fixed.get('i')) is not int or type(fixed.get('tr')) is not dict or
                    not fixed['tr'].get('attr') or fixed['i'] != template.get('itemid', template.get('id'))):
                raise ValueError('ROLE fixed template item mismatch')
            quality = fixed['tr'].get('cl',1)
            if type(quality) is not int or quality not in (1,2,3,4,5) or template.get('treasureClass') != quality:
                raise ValueError('ROLE fixed template class mismatch')
            definition = _rm_literal(tables.get('hero_treasure', {}).get((fixed['i'],quality), {}))
            item = _rm_literal(tables.get('item_data', {}).get(fixed['i'], {}))
            if not definition or not item or item.get('type') != 5:
                raise ValueError('Missing ROLE fixed treasure definition')
            # Original serialized IDs may alias. Never import them as assets.
            fixed['u'] = 'trial:%s:%s:%s' % (scene,hero,slot)
            item_ids.add(fixed['i'])
            suit_ids.update(fixed['tr'].get('su', []))
            trick_ids.update(fixed['tr'].get('ft', []))
            equipment.append({'generator':generator,'template':fixed})
            references['treasure:%s'%generator] = {'generator':template,'definition':definition,'item':item}
        skin = _rm_literal(tables.get('skin', {}).get(row.get('skin_id',hero), {}))
        if skin.get('hero') != hero or skin.get('id') != row.get('skin_id',hero):
            raise ValueError('Missing original ROLE default skin definition')
        references['hero:%s'%hero] = {'hero':hero_row,'star':star,'artifact':arti,'skin':skin,
            'star_attr':_rm_literal(tables['hero_star_attr'][(row['starLevel'],row['starOrder'])]),
            'skills':[[int(skill),level,_rm_literal(tables['skill'][(int(skill),level)])] for skill,level in skill_pairs]}
        actors[str(hero)] = {'fixed':row,'equipment':equipment}
    # Finite referenced calculator slices, never the whole original catalog.
    for name in ('hero_artifact_allot_lv_point_data','liberate_tupo','liberate_lv',
                 'treasure_exclusive','hero_treasure_suit','hero_treasure_third_attr'):
        selected = []
        for key,value in tables.get(name, {}).items():
            row = _rm_literal(value)
            use = (name == 'hero_artifact_allot_lv_point_data' and type(key) is int and 1 <= key <= max(actor['fixed']['artifact']['order'] for actor in actors.values()) or
                   name == 'liberate_tupo' and type(key) is tuple and key[0] in team or
                   name == 'liberate_lv' and type(key) is int and 0 <= key <= max(actor['fixed'].get('liberate',0) for actor in actors.values()) or
                   name == 'treasure_exclusive' and row.get('treasureId') in item_ids or
                   name == 'hero_treasure_suit' and type(key) is tuple and key[0] in suit_ids or
                   name == 'hero_treasure_third_attr')
            if use:
                selected.append([_rm_literal(key),row])
                trick_ids.update(row.get('trick',[]) if type(row.get('trick')) in (list,tuple) else [row['trick']] if row.get('trick') else [])
                trick_ids.update(row.get('addTrick',[]))
        references[name] = sorted(selected,key=lambda entry:json.dumps(entry[0]))
    references['tricks'] = [[_rm_literal(key),_rm_literal(value)] for key,value in sorted(tables.get('trick_data',{}).items()) if type(key) is tuple and key[0] in trick_ids]
    if any((trick,1) not in tables.get('trick_data',{}) for trick in trick_ids):
        raise ValueError('Missing ROLE treasure/suit trick definition')
    source = mission.get('dataSource')
    if not isinstance(source,_rm_text) or not source:
        raise ValueError('Missing original ROLE dataSource')
    for prefix in ('refresh_hero_', 'refresh_monster_'):
        rows = tables.get(prefix + source,{})
        if not rows:
            raise ValueError('Missing original ROLE spawn definitions')
        references[prefix + source] = [[_rm_literal(key),_rm_literal(value)] for key,value in sorted(rows.items(),key=lambda entry:repr(entry[0]))]
    references['monsters'] = {}
    for unused, value in tables['refresh_monster_' + source].items():
        monster = value.get('protoid')
        row = _rm_literal(tables.get('monster',{}).get(monster,{}))
        if type(monster) is not int or not row or type(row.get('level',1)) is not int:
            raise ValueError('Missing original ROLE monster definition')
        references['monsters'][str(monster)] = row
    descriptor = {'version':1,'policy':ROLE_MISSION_POLICY,'scene':scene,'party':list(team),
        'mission':mission,'actors':actors,'references':references,'total_attempts':attempts,
        'artifact_policy':'fixed-order-attrs-are-original-points-v1',
        'liberation_policy':'scalar-all-three-capped-by-trial-level-v1'}
    descriptor['catalog_token'] = _rm_hash(descriptor)
    return descriptor


def _rm_validate_plain(value):
    if value is None or type(value) is bool or type(value) in _rm_integers or isinstance(value,_rm_text):
        return
    if type(value) is list:
        for item in value:
            _rm_validate_plain(item)
        return
    if type(value) is dict:
        if any(not isinstance(key,_rm_text) for key in value):
            raise ValueError('Nontext canonical ROLE key')
        if '__role_float__' in value:
            if set(value) != set(['__role_float__']) or not isinstance(value['__role_float__'],_rm_text):
                raise ValueError('Invalid ROLE lossless number')
            try:
                number = float.fromhex(value['__role_float__'])
            except (TypeError,ValueError):
                raise ValueError('Invalid ROLE lossless number')
            if math.isnan(number) or math.isinf(number) or number.hex() != value['__role_float__']:
                raise ValueError('Noncanonical ROLE lossless number')
            return
        for item in value.values():
            _rm_validate_plain(item)
        return
    raise ValueError('Nonliteral canonical ROLE value')


def validate_role_descriptor(descriptor):
    if type(descriptor) is not dict:
        raise ValueError('Missing pinned ROLE descriptor')
    _rm_validate_plain(descriptor)
    raw = copy.deepcopy(descriptor)
    token = raw.pop('catalog_token',None)
    if token != _rm_hash(raw) or raw.get('policy') != ROLE_MISSION_POLICY or raw.get('version') != 1:
        raise ValueError('Corrupt pinned ROLE descriptor')
    party,mission,actors = raw.get('party'),raw.get('mission'),raw.get('actors')
    if (type(party) is not list or not party or any(type(hero) is not int or hero <= 0 for hero in party) or
            len(set(party)) != len(party) or type(mission) is not dict or type(actors) is not dict or
            set(actors) != set(str(hero) for hero in party) or mission.get('id') != raw.get('scene') or
            mission.get('system_type') != 4 or mission.get('customizeHero') != 1 or
            mission.get('defaultHeroes') != party or mission.get('retry_times') != raw.get('total_attempts') or
            type(raw.get('references')) is not dict):
        raise ValueError('Invalid pinned ROLE party/mission shape')
    for index,hero in enumerate(party):
        actor = actors[str(hero)]
        fixed = actor.get('fixed') if type(actor) is dict else None
        if (type(fixed) is not dict or fixed.get('heroid') != hero or fixed.get('mission_id') != raw['scene'] or
                fixed.get('pos_id') != index+1 or type(actor.get('equipment')) is not list):
            raise ValueError('Invalid pinned ROLE actor')
        _rm_positive(fixed.get('level'),'actor level',100)
    if json.loads(json.dumps(descriptor)) != descriptor:
        raise ValueError('Noncanonical ROLE snapshot')


def role_battle_source(state, occurrence=None):
    story = state.get('story', {})
    key = story.get('event_battle_cursor') if occurrence is None else occurrence
    gate = story.get('event_battle_gates', {}).get(key, {})
    episode = gate.get('role_episode') or {}
    return {'week':story.get('week',0),'route':story.get('route'),'day':state.get('day',{}).get('stock_day'), 'occurrence':key,'cursor':story.get('event_battle_cursor'),'scene':gate.get('scene'),
        'epoch':episode.get('epoch',0),'loss':episode.get('last_loss'),
        'fight':(state.get('battle',{}).get('active') or {}).get('fight_id')}


def bind_role_admission(state, gate, active, tables):
    week,day,route = state['story'].get('week'),state.get('day',{}).get('stock_day'),state['story'].get('route')
    parts = str(gate.get('occurrence','')).split(':')
    if (type(week) is not int or week < 0 or type(day) is not int or not 0 <= day < 7 or
            not isinstance(route,_rm_text) or not route or len(parts) != 3 or
            parts[0] != str(week) or parts[1] != str(gate.get('event')) or not parts[2].isdigit() or int(parts[2]) < 1):
        raise ValueError('ROLE requires actual current occurrence/week/day/route')
    descriptor = compile_role_mission(active['request']['s'],active['request']['h'],tables)
    episode = gate.get('role_episode')
    if episode is None:
        episode = {'policy':ROLE_MISSION_POLICY,'epoch':1,'remaining':descriptor['total_attempts'],
            'total':descriptor['total_attempts'],'catalog_token':descriptor['catalog_token'],
            'last_loss':None,'loss_consumed':True,'audit':[],'owner':active['role_owner'],'source_route':state['story'].get('route'),
            'source_day':state.get('day',{}).get('stock_day')}
        gate['role_episode'] = episode
    if (episode.get('policy') != ROLE_MISSION_POLICY or episode['remaining'] < 1 or
            episode['catalog_token'] != descriptor['catalog_token'] or episode.get('owner') != active['role_owner'] or episode.get('source_route') != state['story'].get('route')):
        raise ValueError('ROLE episode is paused or catalog changed')
    episode['rearm_pending'] = False
    active.update(party_kind='trial',role_mission=descriptor,role_epoch=episode['epoch'],
        role_attempt=episode['total']-episode['remaining']+1,
        event_reward_policy='role-player-level-economy-no-owned-hero-v1',
        heroes=copy.deepcopy(descriptor['actors']))


def native_role_combat_data(owner, active, mission):
    from entity.avatar_attrs.HeroMgrData import HeroData
    from entity.avatar_attrs.ItemData import ItemData
    from common.IdManager import IdManager
    import com.utils.SkinData as SkinData
    import com.data.cdata.skin as skin_data
    import com.data.cdata.ui_model_data as model_data
    import C_file
    if active.get('role_owner') != IdManager.id2str(owner.id):
        raise ValueError('ROLE actor belongs to another actual owner')
    descriptor = active.get('role_mission')
    validate_role_descriptor(descriptor)
    current_tables = role_mission_tables(active['request']['s'])
    current = compile_role_mission(active['request']['s'],active['request']['h'],current_tables)
    if current != descriptor:
        raise ValueError('Original ROLE catalog changed since admission')
    if not descriptor['mission'].get('map_path') or not all(C_file.find_res_file(path,'') for path in descriptor['mission']['map_path']):
        raise ValueError('Missing original ROLE scene resource')

    class _RoleDetachedHero(HeroData):
        def calcRoomSkillAttr(self, attrs):
            return {}, None
        def calcJibanTreasureAttr(self):
            return {}
        def calcTricks(self):
            return self.getTreasureTricks()

    heroes, skins = {}, []
    identity = IdManager.id2str(owner.id)
    for hero_id in descriptor['party']:
        actor = descriptor['actors'][str(hero_id)]
        fixed = _rm_unpack(actor['fixed'])
        hero = _RoleDetachedHero(hero_id)
        hero.starLevel,hero.starOrder = fixed['starLevel'],fixed['starOrder']
        hero.artifact.order = fixed['artifact']['order']
        hero.openArtifact = bool(hero.artifact.order)
        hero.artifact.orderAttrs = copy.deepcopy(fixed['artifact']['attrs'])
        hero.awakeStage = 0
        cap = hero.countLiberateFixMaxLevel(fixed['level'])
        liberation = min(fixed.get('liberate',0),cap)
        hero.liberateHpLevel = hero.liberateAttackLevel = hero.liberateDefendLevel = liberation
        for slot, equipment in enumerate(actor['equipment']):
            payload = _rm_unpack(equipment['template'])
            payload['u'] = IdManager.str2id(hashlib.sha256(('%s:%s:%s'%(active['fight_id'],hero_id,slot)).encode('utf-8')).hexdigest()[:24])
            item = ItemData(invId=hero_id)
            # loadTreasure consults self.treasureClass before assigning d.cl.
            item.treasureClass = payload['tr'].get('cl',1)
            item.initFromDict(payload)
            hero.treasureInv.insertItem(item)
        stars, artifacts = hero.calcSkill()
        skills = [[list(pair) for pair in stars],[list(pair) for pair in artifacts]]
        tricks = list(hero.calcTricks())
        data = {'id':hero_id,'d':hero.calcAllAttr(fixed['level']),'a':{},'s':skills,
            't':tricks,'ai':[False,0],'as':0,'lv':fixed['level']}
        for item in hero.treasureInv.inv:
            if item.treasureExclusive and item.treasureExpDict.get('stage'):
                data['ai'] = [True,item.treasureExpDict['stage']]
                break
        if not data['d'] or not skills[0]:
            raise ValueError('Incomplete original ROLE calculator projection')
        for trick in tricks:
            if (trick,1) not in current_tables['trick_data']:
                raise ValueError('Missing ROLE fixed trick definition')
        skin_id = fixed.get('skin_id') or hero_id
        if type(skin_id) in (list,tuple):
            skin_id = skin_id[0] if skin_id else None
        if type(skin_id) is not int:
            raise ValueError('Missing original ROLE default skin')
        available, missing = costume_resource_preflight(skin_id,skin_data.data,model_data.data,
            lambda path:bool(C_file.find_res_file(path,'')))
        if not available:
            raise ValueError('Missing original ROLE skin resources: %s'%missing)
        skin_uid = hashlib.sha256(('%s:skin:%s'%(active['fight_id'],hero_id)).encode('utf-8')).hexdigest()[:24]
        skin = SkinData.SkinData(skin_id,IdManager.str2id(skin_uid))
        skin_payload = dict(skin.getPersistentDict())
        skin_payload['u'] = skin_uid
        skins.append(_rm_unpack(_rm_literal(skin_payload)))
        heroes[str(('',hero_id))] = data
        heroes[str((identity,hero_id))] = copy.deepcopy(data)
    # AttrComp already preserves ROLE monster row.level; never inject adjusted
    # monster level into units. hero_lv is fallback only; each actor carries lv.
    return {'heroes':heroes,'skins':skins,'hero_lv':active['hero_level'],'monster_lv':1}


def settle_role_loss(state, gate, active, fight_id):
    episode = gate['role_episode']
    if active['role_epoch'] != episode['epoch'] or episode['remaining'] <= 0:
        raise ValueError('Stale ROLE attempt episode')
    episode['remaining'] -= 1
    episode['last_loss'],episode['loss_consumed'] = fight_id,False
    episode['audit'].append({'fight':fight_id,'epoch':episode['epoch'],'outcome':0,'remaining':episode['remaining']})
    gate['status'],gate['fight_id'] = 'open',None
    return episode['remaining'] == 0


def prepare_role_giveup(state, scene, source, missions, events):
    candidate = copy.deepcopy(state)
    validate_role_missions(candidate)
    if type(source) is not dict:
        raise ValueError('Missing captured ROLE source')
    if source != role_battle_source(candidate) or source.get('scene') != scene or candidate.get('battle',{}).get('active'):
        raise ValueError('Giveup requires exact most recent real loss source')
    gate = candidate['story'].get('event_battle_gates',{}).get(source['occurrence'])
    episode = gate.get('role_episode') if gate else None
    if not episode or episode['loss_consumed'] or not episode['last_loss'] or gate['status'] not in ('open','paused'):
        raise ValueError('No unconsumed actual ROLE loss')
    episode['loss_consumed'] = True
    notices = finalize_role_failure(candidate,gate,missions,events,'actual-giveup')
    return candidate, notices


def finalize_role_failure(state, gate, missions, events, reason):
    episode = gate['role_episode']
    failures = [event for event in missions.get(gate['scene'],{}).get('failEvent',()) if events.get(event,{}).get('release')]
    episode['remaining'] = 0
    episode['audit'].append({'reason':reason,'epoch':episode['epoch'],'loss':episode['last_loss']})
    gate['status'],gate['fight_id'] = ('terminal-loss' if failures else 'paused'),None
    notices = [('setEventBattleStage',{'s':gate['scene'],'n':0})]
    if failures:
        failure = {'event':gate['event'],'occurrence':gate['occurrence'],'fight_id':episode['last_loss'],
            'scene':gate['scene'],'outcome':0,'fail_events':failures,'week':state['story'].get('week',0),
            'day':state.get('day',{}).get('stock_day',0),'party_kind':'trial'}
        state['story'].setdefault('event_terminal_failures',{})[str(gate['event'])] = failure
        state['processing_events'] = [event for event in state['processing_events'] if event != gate['event']]
        state['available_events'] = [entry for entry in state['available_events'] if entry[0] != gate['event']]
        state['story'].get('pending_effects',{}).pop(str(gate['event']),None)
        available = dict(state['available_events'])
        for event in failures:
            if event not in state['completed_events'] or events[event].get('repeatable'):
                available[event] = 1
                state['story'].setdefault('available_origins',{})[str(event)] = {'source':'accepted_mission_result',
                    'scene':gate['scene'],'fight_id':episode['last_loss'],'outcome':0,'party_kind':'trial'}
        state['available_events'] = sorted([event,value] for event,value in available.items())
    return notices


def prepare_role_rearm(state, source):
    candidate = copy.deepcopy(state)
    validate_role_missions(candidate)
    if type(source) is not dict:
        raise ValueError('Missing captured ROLE source')
    if source != role_battle_source(candidate,source.get('occurrence')) or candidate.get('battle',{}).get('active'):
        raise ValueError('Stale paused ROLE confirmation')
    gate = candidate['story'].get('event_battle_gates',{}).get(source['occurrence'])
    if not gate or gate['status'] not in ('paused','open') or gate['event'] not in candidate['processing_events']:
        raise ValueError('No live paused ROLE episode')
    episode = gate['role_episode']
    if episode.get('source_route') != candidate['story'].get('route'):
        raise ValueError('Paused ROLE source route changed')
    candidate['story']['event_battle_cursor'] = source['occurrence']
    if gate['status'] == 'open':
        if not episode.get('rearm_pending') and not (episode.get('last_loss') and not episode.get('loss_consumed') and episode.get('remaining',0)>0):
            raise ValueError('ROLE source is already armed')
        episode['rearm_pending'] = True
        return candidate
    episode['epoch'] += 1
    episode.update(remaining=episode['total'],last_loss=None,loss_consumed=True,rearm_pending=True)
    gate['status'],gate['fight_id'] = 'open',None
    return candidate


def validate_role_missions(state):
    story = state.get('story',{})
    for key,gate in story.get('event_battle_gates',{}).items():
        episode = gate.get('role_episode')
        if episode is None:
            continue
        _rm_validate_plain(episode)
        parts = str(key).split(':')
        if (len(parts) != 3 or parts[0] != str(story.get('week',0)) or
                parts[1] != str(gate.get('event')) or not parts[2].isdigit() or int(parts[2]) < 1 or
                type(episode) is not dict or episode.get('policy') != ROLE_MISSION_POLICY or
                type(episode.get('epoch')) is not int or episode['epoch'] < 1 or
                type(episode.get('total')) is not int or episode['total'] < 1 or
                type(episode.get('remaining')) is not int or not 0 <= episode['remaining'] <= episode['total'] or
                not isinstance(episode.get('owner'),_rm_text) or not episode['owner'] or
                type(episode.get('loss_consumed')) is not bool or type(episode.get('audit')) is not list or
                gate.get('occurrence') != key or gate.get('status') not in ('open','active','paused','won','terminal-loss')):
            raise ValueError('Invalid canonical ROLE episode')
    active = state.get('battle',{}).get('active')
    if active and active.get('party_kind') == 'trial':
        validate_role_descriptor(active.get('role_mission'))
        gate = story.get('event_battle_gates',{}).get(active.get('event_occurrence'),{})
        episode = gate.get('role_episode',{})
        if (not isinstance(active.get('role_owner'),_rm_text) or not active['role_owner'] or
                not str(active.get('event_occurrence','')).startswith(str(story.get('week',0))+':') or
                type(active.get('role_epoch')) is not int or type(active.get('role_attempt')) is not int or
                active['role_mission']['party'] != active['request']['h'] or active.get('role_epoch') != episode.get('epoch') or active.get('role_owner') != episode.get('owner') or episode.get('source_route') != story.get('route') or
                active.get('heroes') != active['role_mission']['actors'] or
                active.get('costs') != {'actions':0,'fatigue':0} or
                active.get('role_attempt') != episode.get('total',0)-episode.get('remaining',0)+1 or
                active['role_mission']['catalog_token'] != episode.get('catalog_token') or
                gate.get('status') != 'active' or gate.get('fight_id') != active['fight_id']):
            raise ValueError('Unbound canonical ROLE admission')


def offer_paused_role_resume(proxy):
    """Original common_confirm, saved rearm first, original EVENT enter second."""
    import gg
    state = proxy.progress_snapshot()
    gates = state['story'].get('event_battle_gates',{})
    keys = [state['story'].get('event_battle_cursor')] + sorted(gates)
    source = None
    for key in keys:
        gate = gates.get(key,{})
        episode = gate.get('role_episode') or {}
        resumable = gate.get('status') == 'paused' or gate.get('status') == 'open' and (episode.get('rearm_pending') or
            episode.get('last_loss') and not episode.get('loss_consumed') and episode.get('remaining',0)>0)
        if (resumable and episode and gate.get('event') in state.get('processing_events',[]) and
                episode.get('source_route') == proxy.story.get('route') and
                str(key).startswith(str(proxy.story.get('week',0))+':')):
            source = role_battle_source(state,key)
            break
    if source is None or proxy.battle.get('active'):
        return
    owner = proxy.owner
    if getattr(proxy,'_role_pause_offer',None) is not None and getattr(proxy,'_role_pause_source',None) == source:
        return
    marker = object()
    proxy._role_pause_offer = marker
    proxy._role_pause_source = copy.deepcopy(source)
    def current():
        return (getattr(proxy,'_role_pause_offer',None) is marker and proxy.owner is owner and getattr(gg,'avatar',None) is owner and
            role_battle_source(proxy.progress_snapshot(),source['occurrence']) == source and
            proxy.story.get('event_battle_gates',{}).get(source['occurrence'],{}).get('status') in ('paused','open'))
    def cancel():
        if getattr(proxy,'_role_pause_offer',None) is marker:
            proxy._role_pause_offer = None
    def resume():
        if not current():
            cancel()
            return
        previous = proxy.progress_snapshot()
        candidate = prepare_role_rearm(previous,source)
        proxy.restore_progress(candidate)
        try:
            proxy.save_progress()
        except Exception:
            proxy.restore_progress(previous)
            cancel()
            return
        cancel()
        proxy.reply('setEventBattleStage',{'s':source['scene'],'n':candidate['story']['event_battle_gates'][source['occurrence']]['role_episode']['remaining']})
        owner.combatData.reset()
        owner.battleEnterWithEventMode(source['scene'])
    def show():
        if not current():
            cancel()
            return
        import com.const as const
        panel = gg.ui.panels.common_confirm
        if (gg.logic.game_state.current != const.GameState.CITY or gg.ui._dialogue or
                getattr(panel,'visible',False)):
            proxy.defer(200,guarded_show)
            return
        panel.notify_confirm(u'\u672c\u6b21\u6311\u6218\u5df2\u6682\u505c\uff0c\u5267\u60c5\u4ecd\u7b49\u5f85\u771f\u5b9e\u80dc\u5229\u3002',
            resume,confirm_label=u'\u91cd\u65b0\u6311\u6218',cancel_cb=cancel,cancel_label=u'\u7a0d\u540e')
    def guarded_show():
        try:
            return show()
        except Exception:
            cancel()
            raise
    proxy.defer(200,guarded_show)
