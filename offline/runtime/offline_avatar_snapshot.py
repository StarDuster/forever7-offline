# -*- coding: ascii -*-
"""Native-loader snapshot boundaries and original reload wire encoding."""
import copy
import re
try:
    from offline_story import story_city_snapshot, story_week_snapshot, story_reward_snapshot
    from offline_profile import hero_snapshots_for_client
    from offline_event_battle import event_battle_snapshot
    from offline_event_effects import apply_event_effects_snapshot
    from offline_intelligence import native_intelligence_data
    from offline_gacha_special import gacha_pending_for_client
except ImportError:
    pass
try:
    _avatar_snapshot_text_types = (basestring,)
except NameError:
    _avatar_snapshot_text_types = (str,)


def native_city_snapshot(story):
    city = story_city_snapshot(story)
    for area in city['areas'].values():
        for building in area.get('bd', {}).values():
            identity = building.get('uuid')
            if isinstance(identity, _avatar_snapshot_text_types):
                if not re.match(r'^[0-9a-f]{24}\Z', identity):
                    raise ValueError('Expected serialized original building ObjectId')
                from common.IdManager import IdManager
                building['uuid'] = IdManager.str2id(identity)
    return city


def native_city_reply(name, parameters):
    result = copy.deepcopy(parameters)
    if name == 'get_all_area_info_reply':
        areas = result.get('ais', {})
    elif name == 'get_area_info_reply':
        areas = {'area_%d' % result['ai']['id']: result['ai']}
    else:
        return result
    normalized = native_city_snapshot({'city_areas': {
        str(area['id']): area for area in areas.values()}})['areas']
    if name == 'get_all_area_info_reply':
        result['ais'] = normalized
    else:
        result['ai'] = normalized['area_%d' % result['ai']['id']]
    return result


def build_local_avatar_snapshot(state, template):
    """Overlay canonical state onto a fully realized stock-loader template."""
    if not isinstance(template, dict) or 'inv' not in template or 'ldd' not in template:
        raise ValueError('A realized original avatar loader template is required')
    snapshot = copy.deepcopy(template)
    profile = state['profile']
    story = state['story']
    snapshot.update({key: profile['economy'][key] for key in ('money', 'exp', 'level')})
    if state.get('player_name'):
        snapshot['name'] = state['player_name']
    snapshot['heromgr'] = {'hrs': hero_snapshots_for_client(profile), 'cfs': None}
    snapshot['heromgr'].update(gacha_pending_for_client(profile, template.get('heromgr', {})))
    snapshot['weeknum'] = story_week_snapshot(story, state.get('day', {}))
    snapshot['std'].update({'rt': story.get('route', '1'), 'srt': copy.deepcopy(story.get('sub_routes', [])),
                            'ed': copy.deepcopy(story.get('endings', []))})
    transition = state.get('week_protocol', {}).get('transition') or {}
    if transition.get('target_week') == story.get('week'):
        # Original StoryData.initFromDict defaults, for specifically established
        # weekly fields only. Unknown template/permanent fields stay intact.
        for canonical, field, default_value in (
                ('clues', 'cl', []), ('failed_clues', 'fc', []), ('clues_read', 'cr', False),
                ('clue_details_read', 'dr', {}), ('rely_value', 'srv', 0),
                ('support_value', 'ssv', 0), ('yisake_value', 'yiv', 0),
                ('cityMusic', 'cm', None), ('cityTheme', 'ct', None)):
            snapshot['std'][field] = copy.deepcopy(story.get(canonical, default_value))
    snapshot['city'] = native_city_snapshot(story)
    snapshot['reward'] = story_reward_snapshot(story)
    snapshot['np'] = copy.deepcopy(story['notes'])
    snapshot['cgs'] = sorted(set(story.get('cgs', [])) | set(story.get('cg', [])))
    snapshot['ncgs'] = copy.deepcopy(story.get('new_cgs', []))
    snapshot['ccgs'] = copy.deepcopy(snapshot['cgs'])
    snapshot['bs'] = event_battle_snapshot(state)
    snapshot['eventTrigger'] = {'ae': copy.deepcopy(state['available_events']),
        'pe': copy.deepcopy(state['processing_events']), 'ecm': copy.deepcopy(state['completed_events']),
        'gle': [], 'ecd': {}}
    items = copy.deepcopy(profile.get('treasures', {}).get('items', []))
    items.extend(copy.deepcopy((state.get('gacha') or {}).get('items', [])))
    from common.IdManager import IdManager
    for item in items:
        item['u'] = IdManager.str2id(item['u'])
    snapshot['inv']['items'] = items
    try:
        from offline_gacha_gateway import gacha_snapshot_projection, gacha_economy_projection
    except ImportError:
        pass
    snapshot = gacha_economy_projection(state, snapshot)
    snapshot['ldd'] = gacha_snapshot_projection(state, snapshot['ldd'])
    snapshot = apply_event_effects_snapshot(state, snapshot)
    snapshot['intelligence'] = native_intelligence_data(story.get('intelligence',{'is':[],'rd':False}))
    return snapshot


def normalize_avatar_wire(value):
    """Normalize containers only. Preserve BSON IDs for original json_util."""
    if isinstance(value, dict):
        return {key: normalize_avatar_wire(item) for key, item in value.items()}
    if isinstance(value, (tuple, list, set)):
        return [normalize_avatar_wire(item) for item in value]
    return value


def pack_original_avatar(snapshot):
    # Original client embeds msgpack0.4.7; its top-level package has no dumps.
    # json_util.default emits {$oid:...}; the stock reload object_hook restores
    # the actual ObjectId type before hero/city/inventory loaders consume it.
    import msgpack.embed as native_msgpack
    from bson.json_util import default
    return native_msgpack.dumps(normalize_avatar_wire(snapshot), default=default, use_bin_type=False)
