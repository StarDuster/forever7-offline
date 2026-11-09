# -*- coding: ascii -*-
"""Explicit local hero-only simulation, NOT original server probabilities.

Policy v1: free six-card groups, independent uniform whole-hero samples from
the supplied original-visible owned roster, no pity or fragments/treasures. Actual
client duplicate-conversion quantities are supplied by the adapter. Opening
a group fixes all outcomes. This module returns candidates; the caller must
commit them atomically before replying or applying inventory updates.
"""
import copy
import re

GACHA_POLICY = 'local-uniform-owned-heroes-free-v1'
try:
    _gacha_text_types = (basestring,)
except NameError:
    _gacha_text_types = (str,)


def new_gacha_state():
    return {'version': 1, 'policy': GACHA_POLICY, 'next_group': 1,
            'group': None, 'items': [], 'opened_total': 0, 'history': []}


def visible_simulation_heroes(profile, hero_catalog):
    """Keep forbidden archive records owned, outside new animation samples."""
    return sorted(int(key) for key in (profile or {}).get('heroes', {})
                  if int(key) in hero_catalog and not hero_catalog[int(key)].get('hero_forbid', False))


def validate_gacha_state(state):
    if state is None:
        return
    if (not isinstance(state, dict) or state.get('version') != 1 or
            state.get('policy') != GACHA_POLICY):
        raise ValueError('Unknown gacha save policy')
    for key in ('next_group', 'opened_total'):
        if type(state.get(key)) is not int or state[key] < (1 if key == 'next_group' else 0):
            raise ValueError('Invalid gacha counter')
    stage = state.get('axiliya_tutorial_stage', 0)
    if type(stage) is not int or not 0 <= stage <= 2:
        raise ValueError('Invalid original Axiliya tutorial version')
    if type(state.get('slots', 6)) is not int or not 1 <= state.get('slots', 6) <= 100:
        raise ValueError('Invalid configured group slots')
    ids = set()
    for item in state['items']:
        uid = item.get('u')
        if (not isinstance(uid, _gacha_text_types) or not re.match(r'^[0-9a-f]{24}\Z', uid) or uid in ids or
                type(item.get('i')) is not int or item['i'] <= 0 or
                type(item.get('w')) is not int or item['w'] <= 0):
            raise ValueError('Invalid simulated inventory stack')
        ids.add(uid)
    group = state['group']
    if group is not None:
        if (type(group['id']) is not int or not 0 < group['id'] < state['next_group'] or
                len(group['cards']) != state.get('slots', 6)):
            raise ValueError('Invalid six-card group')
        for index, card in enumerate(group['cards']):
            if (card.get('index') != index or type(card.get('is_open')) is not bool or
                    card.get('get_hero') is not False or card.get('hero_file') != 0 or
                    not isinstance(card.get('hero'), list) or len(card['hero']) != 1 or
                    type(card['hero'][0]) is not int or card['hero'][0] <= 0):
                raise ValueError('Invalid simulated hero result')
            for key, amount in card['hero_frag'].items():
                if not str(key).isdigit() or int(key) <= 0 or type(amount) is not int or amount <= 0:
                    raise ValueError('Invalid duplicate conversion')
    if not isinstance(state['history'], list) or len(state['history']) > 128:
        raise ValueError('Invalid bounded gacha history')


def prepare_gacha_group(state, owned_heroes, choose_index, duplicate_items):
    validate_gacha_state(state)
    result = copy.deepcopy(state) if state is not None else new_gacha_state()
    if result['group'] is not None:
        return result, False
    heroes = sorted(owned_heroes)
    if not heroes:
        raise ValueError('Hero-only simulation requires an owned roster')
    cards = []
    for index in range(result.get('slots', 6)):
        choice = choose_index(len(heroes))
        if type(choice) is not int or not 0 <= choice < len(heroes):
            raise ValueError('Random index outside roster')
        hero_id = heroes[choice]
        conversions = {str(key): amount for key, amount in duplicate_items(hero_id).items()}
        cards.append({'index': index, 'is_open': False, 'hero': [hero_id],
                      'get_hero': False, 'hero_file': 0, 'hero_frag': conversions})
    result['group'] = {'id': result['next_group'], 'cards': cards}
    result['next_group'] += 1
    validate_gacha_state(result)
    return result, True


def gacha_result_for_client(card):
    result = copy.deepcopy(card)
    # Stock batch settlement extends this array directly. Its own omitted-field
    # fallback is a tuple, so even a draw without activity rewards needs [].
    activity = result.setdefault('other_reward', {}).setdefault('activityReward', {})
    activity.setdefault('treasure', [])
    return result


def gacha_file_view(state):
    validate_gacha_state(state)
    if state is None or state['group'] is None:
        return {}
    # Unopened cards expose no predetermined outcomes.
    return {str(card['index']): gacha_result_for_client(card) if card['is_open'] else
            {'index': card['index'], 'is_open': False} for card in state['group']['cards']}


def open_gacha_cards(state, indices, make_id, stack_limit):
    validate_gacha_state(state)
    if state is None or state['group'] is None:
        raise ValueError('No pending six-card group')
    indices = list(indices)
    if len(indices) != len(set(indices)) or any(type(i) is not int or not 0 <= i < state.get('slots', 6) for i in indices):
        raise ValueError('Invalid card indices')
    result = copy.deepcopy(state)
    changed = False
    for index in indices:
        card = result['group']['cards'][index]
        if card['is_open']:
            continue
        for key, amount in sorted(card['hero_frag'].items()):
            item_id, remaining = int(key), amount
            maximum = stack_limit(item_id)
            if type(maximum) is not int or maximum < 1:
                raise ValueError('Missing valid item stack limit')
            for item in result['items']:
                if item['i'] == item_id:
                    added = min(remaining, max(0, maximum - item['w']))
                    item['w'] += added
                    remaining -= added
            while remaining:
                added = min(remaining, maximum)
                result['items'].append({'u': str(make_id()), 'i': item_id, 'w': added,
                                        'tt': 0, 'c': 0, 'le': 0, 'lo': None, 'ele': 0, 'ctt': 0})
                remaining -= added
        card['is_open'] = True
        result['opened_total'] += 1
        changed = True
    validate_gacha_state(result)
    return result, [gacha_result_for_client(result['group']['cards'][i]) for i in indices], changed


def quit_gacha_group(state):
    validate_gacha_state(state)
    if state is None or state['group'] is None:
        return copy.deepcopy(state), False
    result = copy.deepcopy(state)
    result['history'].append(copy.deepcopy(result['group']))
    result['history'] = result['history'][-128:]
    result['group'] = None
    return result, True
