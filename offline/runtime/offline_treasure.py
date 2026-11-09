# -*- coding: ascii -*-
"""Table-derived offline treasures; stable instances, shared hero references."""
import copy
import re


def validate_treasure_inventory(state):
    if state is None:
        return
    if not isinstance(state, dict) or state.get('version') != 1:
        raise ValueError('Unsupported treasure inventory')
    if not isinstance(state.get('items'), list):
        raise ValueError('Missing treasure item inventory')
    ids = set()
    for item in state['items']:
        uid = item.get('u', '')
        if not re.match(r'^[0-9a-f]{24}\Z', uid) or uid in ids:
            raise ValueError('Invalid or duplicate treasure ObjectId')
        ids.add(uid)
        tr = item.get('tr', {})
        if type(item.get('i')) is not int or tr.get('cl') not in (1, 2, 3, 4, 5):
            raise ValueError('Invalid treasure template/class')
        if not tr.get('attr') or any(set(a) != set(('n', 'v')) for a in tr['attr']):
            raise ValueError('Treasure requires explicit attributes')


def migrate_treasure_inventory(state, catalog, item_catalog, attr_indices, make_id, timestamp):
    """One class-five instance per template, at table attribute range minima.

    This is an explicit deterministic offline roll, not a claim to reproduce
    server randomness. No hidden attributes or extra random rolls are invented.
    """
    validate_treasure_inventory(state)
    candidate = copy.deepcopy(state) if state is not None else {'version': 1, 'items': []}
    before = copy.deepcopy(candidate)
    owned = set(item['i'] for item in candidate['items'] if item['tr']['cl'] == 5)
    for (template, quality), row in sorted(catalog.items()):
        if quality != 5 or template in owned:
            continue
        if template not in item_catalog or (template, 1) not in catalog:
            raise ValueError('Missing original treasure item metadata')
        attrs = []
        for key, prefix in (('secondAttrs', 'f'), ('thridAttrs', 't')):
            for name, limits in sorted(row.get(key, {}).items()):
                if name not in attr_indices or len(limits) != 2 or limits[0] > limits[1]:
                    raise ValueError('Unresolved treasure attribute range')
                attrs.append({'n': prefix + str(attr_indices[name]), 'v': limits[0]})
        if not attrs:
            raise ValueError('Cannot grant attribute-less treasure')
        candidate['items'].append({'u': str(make_id()), 'i': template, 'w': 1, 'c': 0,
            'ctt': timestamp, 'tr': {'cl': quality, 'lv': 1, 'x': 0, 'f': False,
            'ft': list(row.get('fixTrick', ())), 'attr': attrs, 'era': [], 'su': []}})
        owned.add(template)
    candidate['migration'] = 'all-treasure-class5-table-minimum-roll-v1'
    validate_treasure_inventory(candidate)
    return candidate, candidate != before


def prepare_treasure_equipment(profile, inventory, method, arguments, catalog):
    """Prepare a validated replacement without mutating saved state.

    The native client permits the same global instance to be referenced by
    several heroes; replacing equipment changes hero references only.
    """
    candidate = copy.deepcopy(profile)
    hero_id = arguments.get('h')
    hero = candidate['heroes'].get(str(hero_id))
    if not hero:
        raise ValueError('Unknown equipment hero')
    previous = hero['ti']['items']
    sources = {0: inventory['items']}
    sources.update({int(hid): saved['ti']['items'] for hid, saved in candidate['heroes'].items()})
    if method == 'equipTreasureBatch':
        selection = arguments.get('i')
        if not isinstance(selection, dict):
            raise ValueError('Invalid equipment selection')
        selected, equips, seen, templates, cost = [], [], set(), [], 0
        for uid, source in sorted(selection.items()):
            if uid.lower() in seen or type(source) is not int or source not in sources:
                raise ValueError('Invalid or duplicate equipment source')
            seen.add(uid.lower())
            item = next((i for i in sources[source] if i['u'] == uid), None)
            if not item or item['tr'].get('f'):
                raise ValueError('Treasure is absent or forbidden')
            row = catalog.get((item['i'], item['tr']['cl']))
            if not row or (row.get('validHeroes') and hero_id not in row['validHeroes']):
                raise ValueError('Treasure is not valid for hero')
            templates.append(item['i'])
            if row.get('uniqueEquip') and templates.count(item['i']) > 1:
                raise ValueError('Duplicate unique treasure')
            cost += row.get('cost', 1)
            selected.append(copy.deepcopy(item))
            equips.append((uid, source, copy.deepcopy(item)))
        if cost > hero['ti']['mc']:
            raise ValueError('Treasure equipment exceeds capacity')
        result = {'h': hero_id, 'u': [i['u'] for i in previous if i['u'] not in seen],
                  'e': equips, 'pi': arguments.get('pi', '')}
        reply = 'equipTreasureBatchReply'
    elif method == 'unequipTreasure':
        uid = str(arguments.get('u'))
        if not any(i['u'] == uid for i in previous):
            raise ValueError('Treasure is not equipped')
        selected = [i for i in previous if i['u'] != uid]
        reply, result = 'unequipTreasureReply', {'h': hero_id, 'u': uid, 't': True}
    elif method == 'unequipAllTreasure':
        selected = []
        reply, result = 'unequipAllTreasureReply', {'h': hero_id, 'hinv': [], 't': True}
    else:
        raise ValueError('Unsupported equipment operation')
    hero['ti']['items'] = selected
    # Restore legacy detached items to the global inventory without duplication.
    global_inventory = copy.deepcopy(inventory)
    global_ids = set(i['u'] for i in global_inventory['items'])
    restored = []
    for item in previous:
        if item['u'] not in global_ids:
            global_inventory['items'].append(copy.deepcopy(item))
            restored.append(copy.deepcopy(item))
            global_ids.add(item['u'])
    return candidate, global_inventory, reply, result, restored


def make_table_treasure_reward(template, quality, catalog, attr_indices, make_id, timestamp, trade_type=1):
    """A new reward instance at the original class's explicit range minima."""
    row = catalog.get((template, quality))
    if not row:
        raise ValueError('Missing original reward treasure class')
    attrs = []
    for key, prefix in (('secondAttrs', 'f'), ('thridAttrs', 't')):
        for name, limits in sorted(row.get(key, {}).items()):
            if name not in attr_indices or len(limits) != 2 or limits[0] > limits[1]:
                raise ValueError('Unresolved reward treasure attribute')
            attrs.append({'n': prefix + str(attr_indices[name]), 'v': limits[0]})
    if not attrs:
        raise ValueError('Reward treasure requires real attributes')
    return {'u': str(make_id()), 'i': template, 'w': 1, 'c': 0, 'ctt': timestamp,
            'tt': trade_type, 'tr': {'cl': quality, 'lv': 1, 'x': 0, 'f': False,
            'ft': list(row.get('fixTrick', ())), 'attr': attrs, 'era': [], 'su': []}}
