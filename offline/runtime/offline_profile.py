# -*- coding: ascii -*-
"""Explicit hero/skin snapshots derived from the original client loaders.

All heroes in the preserved playable hero catalog are granted explicitly.
Released ordinary and dye costumes are migrated separately from awakening
styles and treasure. ObjectIds are generated once, stored
as strings, and restored to native types at the loader boundary.
"""
import copy
import re
import time

try:
    from offline_wardrobe_completion import migrate_remaining_wardrobe
except ImportError:
    # Embedded Android sources share a namespace and are loaded before use.
    pass

try:
    _profile_text_types = (basestring,)
except NameError:
    _profile_text_types = (str,)


def validate_hero_profile(profile):
    if profile is None:
        return
    if not isinstance(profile, dict) or profile.get('version') != 1:
        raise ValueError('Unsupported hero profile version')
    heroes = profile.get('heroes')
    if not isinstance(heroes, dict) or not heroes:
        raise ValueError('Missing explicit hero records')
    if not isinstance(profile.get('migrations'), list):
        raise ValueError('Missing explicit profile migration history')
    all_ids = set()
    for hero_id, hero in heroes.items():
        if not isinstance(hero_id, _profile_text_types) or not hero_id.isdigit():
            raise ValueError('Hero profile keys must be serialized integer IDs')
        for required in ('sl', 'so', 'cf', 'ar', 'ef', 'ti', 'cat', 'sk', 'cs'):
            if required not in hero:
                raise ValueError('Missing required hero field: %s' % required)
        artifact = hero['ar']
        if not isinstance(artifact.get('sl'), list):
            raise ValueError('Artifact slots must be a list')
        for key in ('oa', 'ot', 'rotc'):
            if not isinstance(artifact.get(key), dict):
                raise ValueError('Artifact attributes must be dictionaries')
        if not isinstance(hero['ti'].get('items'), list) or 'mc' not in hero['ti']:
            raise ValueError('Invalid treasure inventory')
        skins = hero['sk']
        if not isinstance(skins, dict) or not skins or hero['cs'] not in skins:
            raise ValueError('Current skin must reference an owned default/selected instance')
        for instance, skin in skins.items():
            if not isinstance(instance, _profile_text_types) or not re.match(r'^[0-9a-f]{24}\Z', instance):
                raise ValueError('Expected a serialized ObjectId, not UUID4')
            if instance in all_ids or skin.get('u') != instance:
                raise ValueError('Duplicate or mismatched skin instance ID')
            all_ids.add(instance)
            if type(skin.get('i')) is not int:
                raise ValueError('Skin template ID must be an integer')


def grant_profile_skins(hero_id, hero, template_ids, skin_catalog, make_id, timestamp,
                        allow_dye=False):
    """Idempotently grant an explicitly selected, ordinary wardrobe subset."""
    owned = {skin['i'] for skin in hero['sk'].values()}
    for template in template_ids:
        row = skin_catalog.get(template)
        is_default = bool(row and template == hero_id and row.get('hero') == hero_id)
        if (not row or row.get('hero') != hero_id or
                (row.get('release') != 1 and not is_default) or
                (row.get('is_dye_skin', False) and not allow_dye)):
            raise ValueError('Skin is outside the verified ordinary wardrobe subset: %s' % template)
        if row.get('is_dye_skin', False):
            parent = skin_catalog.get(row.get('ori_skin'))
            if not parent or parent.get('hero') != hero_id or parent.get('is_dye_skin'):
                raise ValueError('Dye skin requires a same-hero ordinary parent')
        if template in owned:
            continue
        instance = str(make_id())
        if instance in hero['sk']:
            raise ValueError('Skin ObjectId collision')
        hero['sk'][instance] = {'i': template, 'u': instance, 'cd': {}, 'pd': {},
                                'cr': timestamp, 'dst': timestamp, 'cwi': None,
                                'cwd': {}, 'pwd': {}, 'ias': False, 'fb': False,
                                'pb': [], 'bd': {}, 'tr': []}
        owned.add(template)
    if hero['cs'] is None:
        defaults = [instance for instance, skin in hero['sk'].items() if skin['i'] == hero_id]
        if len(defaults) != 1:
            raise ValueError('A unique real default skin is required')
        hero['cs'] = defaults[0]


def native_default_hero_snapshot(hero_id):
    # Invoke the client's actual constructor, without inferring missing fields
    # from SnapshotDict. All required loader fields below come from that object.
    from entity.avatar_attrs.HeroMgrData import HeroData
    import com.data.cdata.hero as hero_data
    hero = HeroData(hero_id)
    artifact = hero.artifact
    row = hero_data.data[hero_id]
    return {'sl': row['hero_composite_init_rank'], 'so': row['hero_composite_init_order'],
            'cf': hero.curFatigueValue,
            'ef': hero.extraFriendlyValue, 'cat': hero.curAtrifactThresholdInfo,
            'ar': {'o': artifact.order, 'ss': artifact.slotSize,
                   'oa': copy.deepcopy(artifact.orderAttrs),
                   'ot': copy.deepcopy(artifact.orderAttrsThreshold),
                   'rotc': copy.deepcopy(artifact.randomOrderAttrsThresholdCount),
                   'sl': [], 'fn': artifact.fillnum, 'aao': artifact.awake_added_order,
                   'il': artifact.increase_lv},
            'ti': {'items': [], 'mc': hero.treasureInv.maxCost}, 'sk': {}, 'cs': None}


def migrate_full_hero_roster(profile, hero_catalog, skin_catalog, make_snapshot, make_id, timestamp):
    candidate = copy.deepcopy(profile)
    if candidate is None:
        candidate = {'version': 1, 'heroes': {}, 'migrations': []}
    changed = False
    if any(int(key) not in hero_catalog for key in candidate['heroes']):
        raise ValueError('Saved hero is absent from this catalog; existing profile preserved')
    for hero_id in sorted(hero_catalog):
        key = str(hero_id)
        if key not in candidate['heroes']:
            candidate['heroes'][key] = make_snapshot(hero_id)
            changed = True
        hero = candidate['heroes'][key]
        row = hero_catalog[hero_id]
        initial = (row['hero_composite_init_rank'], row['hero_composite_init_order'])
        if (hero['sl'], hero['so']) < initial:
            # Upgrade old constructor-only prototype records to the table's
            # actual initial rank/order; preserve any later player upgrades.
            hero['sl'], hero['so'] = initial
            changed = True
        before = len(hero['sk'])
        selected = (hero_id, 10023) if hero_id == 24 else (hero_id,)
        grant_profile_skins(hero_id, hero, selected, skin_catalog, make_id, timestamp)
        changed = changed or len(hero['sk']) != before
    migration = 'starter-defaults-and-hero24-two-skins-v1'
    if migration not in candidate['migrations']:
        candidate['migrations'].append(migration)
        changed = True
    full_migration = 'all-playable-heroes-v1'
    if full_migration not in candidate['migrations']:
        candidate['migrations'].append(full_migration)
        changed = True
    validate_hero_profile(candidate)
    return candidate, changed


def migrate_released_wardrobe(profile, skin_catalog, awake_catalog, make_id, timestamp):
    """Add ordinary/dye instances without resetting equipped skins or dyes.

    Awakening remains a separate style state machine; its templates must not
    accidentally become ordinary costumes merely because release is set.
    """
    validate_hero_profile(profile)
    candidate = copy.deepcopy(profile)
    awakening = set(row['awake_skin'] for row in awake_catalog.values()
                    if row.get('awake_skin'))
    by_hero = {}
    for template, row in skin_catalog.items():
        if row.get('release') == 1 and template not in awakening:
            hero_id = row['hero']
            if str(hero_id) not in candidate['heroes']:
                raise ValueError('Released costume refers to an absent hero')
            by_hero.setdefault(hero_id, []).append(template)
    changed = False
    for hero_id, templates in sorted(by_hero.items()):
        hero = candidate['heroes'][str(hero_id)]
        before = len(hero['sk'])
        grant_profile_skins(hero_id, hero, sorted(templates), skin_catalog,
                            make_id, timestamp, allow_dye=True)
        changed = changed or before != len(hero['sk'])
    migration = 'released-ordinary-and-dye-wardrobe-v1'
    if migration not in candidate['migrations']:
        candidate['migrations'].append(migration)
        changed = True
    validate_hero_profile(candidate)
    return candidate, changed


def migrate_awakening_wardrobe(profile, hero_catalog, skin_catalog, awake_catalog,
                                make_id, timestamp):
    """Offline unlock: grant the real stage-one style and its prerequisite stage.

    Preserve higher progression and equipment. Apply the table's artifact order
    increment when crossing stage zero, rather than simulating ordinary skins.
    """
    validate_hero_profile(profile)
    candidate = copy.deepcopy(profile)
    before = copy.deepcopy(candidate)
    for (hero_id, stage), row in sorted(awake_catalog.items()):
        template = row.get('awake_skin')
        if not template or not hero_catalog.get(hero_id, {}).get('open_awake'):
            continue
        hero = candidate['heroes'][str(hero_id)]
        skin_row = skin_catalog.get(template)
        if not row.get('has_skin') or not skin_row or skin_row.get('hero') != hero_id:
            raise ValueError('Invalid awakening costume configuration')
        if hero.get('as', 0) < stage:
            added = sum(awake_catalog[(hero_id, step)]['artifact_level_up']
                        for step in range(hero.get('as', 0) + 1, stage + 1))
            hero['ar']['aao'] = hero['ar'].get('aao', 0) + added
            hero['as'] = stage
        hero.setdefault('ass', False)
        hero.setdefault('lncs', None)
        # Reuse instance initialization only; the dedicated migration owns
        # eligibility and explicitly marks the resulting awakening instance.
        catalog = {template: dict(skin_row, release=1)}
        grant_profile_skins(hero_id, hero, [template], catalog, make_id, timestamp)
        for skin in hero['sk'].values():
            if skin['i'] == template:
                skin['ias'] = True
    migration = 'table-awakening-style-and-stage-unlock-v1'
    if migration not in candidate['migrations']:
        candidate['migrations'].append(migration)
    validate_hero_profile(candidate)
    return candidate, candidate != before


def change_awakening_style(profile, hero_id, enabled, hero_catalog, awake_catalog):
    """Validate and change style in place, returning the native reply payload."""
    hero = (profile or {}).get('heroes', {}).get(str(hero_id))
    if not hero or type(enabled) is not bool:
        raise ValueError('Invalid awakening style request')
    stage = hero.get('as', 0)
    if (not hero_catalog.get(hero_id, {}).get('open_awake') or
            not awake_catalog.get((hero_id, stage), {}).get('has_skin')):
        raise ValueError('Awakening style is not unlocked')
    old = hero['cs']
    if enabled:
        templates = set(row.get('awake_skin') for (hid, level), row in awake_catalog.items()
                        if hid == hero_id and level <= stage and row.get('awake_skin'))
        matches = sorted(uid for uid, skin in hero['sk'].items()
                         if skin['i'] in templates and skin.get('ias') and not skin.get('fb'))
        if len(matches) != 1:
            raise ValueError('Expected one owned awakening style')
        if not hero.get('ass'):
            hero['lncs'] = old
        selected = matches[0]
    else:
        selected = hero.get('lncs') if hero.get('ass') else old
        skin = hero['sk'].get(selected)
        if not skin or skin.get('ias') or skin.get('fb'):
            raise ValueError('Missing previous ordinary costume')
    hero['cs'], hero['ass'] = selected, enabled
    return {'hid': hero_id, 'ss': enabled, 'oldsi': old, 'newsi': selected,
            'lcs': hero.get('lncs'), 'st': old != selected}


def ensure_initial_hero_profile(proxy):
    from common.IdManager import IdManager
    import com.data.cdata.skin as skin_data
    import com.data.cdata.hero as hero_data
    import com.data.cdata.awake_consume_data as awake_data
    candidate, changed = migrate_full_hero_roster(proxy.profile, hero_data.data, skin_data.data,
                                                native_default_hero_snapshot, IdManager.genid, int(time.time()))
    candidate, wardrobe_changed = migrate_released_wardrobe(
        candidate, skin_data.data, awake_data.data, IdManager.genid, int(time.time()))
    candidate, awakening_changed = migrate_awakening_wardrobe(
        candidate, hero_data.data, skin_data.data, awake_data.data, IdManager.genid, int(time.time()))
    candidate, remaining_changed = migrate_remaining_wardrobe(
        candidate, skin_data.data, IdManager.genid, int(time.time()),
        validate_hero_profile, grant_profile_skins)
    changed = changed or wardrobe_changed or awakening_changed or remaining_changed
    if changed:
        previous = proxy.profile
        proxy.profile = candidate
        try:
            proxy.save_progress()
        except Exception:
            proxy.profile = previous
            raise
    return proxy.profile


def hero_snapshots_for_client(profile):
    from common.IdManager import IdManager
    validate_hero_profile(profile)
    result = []
    for key, saved in sorted(profile['heroes'].items()):
        hero = copy.deepcopy(saved)
        # The stock loader converts sk keys/u itself, but assigns cs directly.
        for item in hero['ti']['items']:
            item['u'] = IdManager.str2id(item['u'])
        hero['cs'] = IdManager.str2id(hero['cs'])
        if hero.get('lncs') is not None:
            hero['lncs'] = IdManager.str2id(hero['lncs'])
        result.append((int(key), hero))
    return result
