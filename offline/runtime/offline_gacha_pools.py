# -*- coding: ascii -*-
"""Pool-isolated atomic candidates; sampling is supplied by the original-table adapter.

No probabilities or reward buckets are invented here. Resolver(wire_t, ordinal,
force_s) returns the complete original client reward dict (hero, hero_frag,
treasure, etc). Caller commits candidate plus profile/equipment before replying.
Only newly_granted cards may be applied to external inventory. Integrated callers
should pass credit_items=False and apply all rewards to one canonical inventory
atomically. Legacy isolated callers may credit local hero_frag stacks here; never
merge those historical stacks into a consumable inventory on every snapshot.
Costs may be disabled by the explicit offline adapter; rarity never follows costs.
"""
import copy
try:
    from offline_gacha import (new_gacha_state, validate_gacha_state,
                               gacha_result_for_client)
except ImportError:
    pass

POLICY = 'original-configured-mixed-rewards-pool-transactions-v1'
try:
    TEXT = (basestring,)
except NameError:
    TEXT = (str,)


def new_gacha_pools_state(legacy_normal=None):
    if legacy_normal is not None:
        validate_gacha_state(legacy_normal)
    return {'version': 1, 'policy': POLICY,
            'pools': {'1': copy.deepcopy(legacy_normal or new_gacha_state())}}


def _pool(state, wire_t):
    if type(wire_t) is not int or wire_t <= 0:
        raise ValueError('Invalid original wire drawType')
    return state['pools'].get(str(wire_t))


def _new_pool(config):
    slots = config.get('slots', 6)
    if type(slots) is not int or not 1 <= slots <= 100:
        raise ValueError('Invalid configured slot count')
    return {'version': 1, 'policy': POLICY, 'slots': slots, 'next_group': 1,
            'group': None, 'items': [], 'opened_total': 0, 'history': [],
            'allocated_total': 0, 's_seen': False, 'day_key': None,
            'daily_count': 0, 'receipts': [], 'retired_operations': [], 'config': copy.deepcopy(config)}


def validate_gacha_pools_state(state):
    if not isinstance(state, dict) or state.get('version') != 1 or state.get('policy') != POLICY or not isinstance(state.get('pools'), dict):
        raise ValueError('Unknown configured pool state')
    all_ids = set()
    for key, pool in state['pools'].items():
        if not isinstance(key, TEXT) or not key.isdigit() or int(key) <= 0:
            raise ValueError('Invalid saved wire pool')
        for counter in ('next_group', 'opened_total'):
            if type(pool.get(counter)) is not int or pool[counter] < (1 if counter == 'next_group' else 0):
                raise ValueError('Invalid configured pool counter')
        slots = pool.get('slots', 6)
        if type(slots) is not int or not 1 <= slots <= 100:
            raise ValueError('Invalid saved slot count')
        group = pool.get('group')
        if group is not None:
            if len(group['cards']) != slots or type(group['id']) is not int or not 0 < group['id'] < pool['next_group']:
                raise ValueError('Invalid configured group')
            for i, card in enumerate(group['cards']):
                if card.get('index') != i or type(card.get('is_open')) is not bool:
                    raise ValueError('Invalid configured card')
        if len(pool.get('history', [])) > 128 or len(pool.get('receipts', [])) > 128:
            raise ValueError('Unbounded pool history')
        for item in pool.get('items', []):
            uid = item.get('u')
            if not isinstance(uid, TEXT) or len(uid) != 24 or any(c not in '0123456789abcdef' for c in uid) or uid in all_ids or type(item.get('i')) is not int or item['i'] <= 0 or type(item.get('w')) is not int or item['w'] <= 0:
                raise ValueError('Invalid cross-pool inventory instance')
            all_ids.add(uid)
        config = pool.get('config', {})
        cap = config.get('cap')
        if cap is not None and pool['opened_total'] > cap:
            raise ValueError('Configured lifetime cap exceeded')
        if type(pool.get('daily_count', 0)) is not int or pool.get('daily_count', 0) < 0:
            raise ValueError('Invalid daily counter')


def _candidate(state):
    value = new_gacha_pools_state() if state is None else copy.deepcopy(state)
    validate_gacha_pools_state(value)
    return value


def _configured(state, wire_t, config):
    pool = _pool(state, wire_t)
    if pool is None:
        pool = _new_pool(config)
        state['pools'][str(wire_t)] = pool
    elif pool.get('config') is None:
        # Old normal state is adopted without changing fixed cards or items.
        pool['config'] = copy.deepcopy(config)
        pool['slots'] = config.get('slots', 6)
        if pool.get('group') and len(pool['group']['cards']) != pool['slots']:
            raise ValueError('Configured slots conflict with saved original group')
    elif pool['config'] != config:
        raise ValueError('Pool configuration drift requires explicit migration')
    return pool


def _resolve(resolver, wire_t, ordinal, force_s):
    card = resolver(wire_t, ordinal, force_s)
    if not isinstance(card, dict):
        raise ValueError('Original reward resolver must return a dict')
    card = copy.deepcopy(card)
    card.pop('index', None)
    card.pop('is_open', None)
    for key, amount in card.get('hero_frag', {}).items():
        if not str(key).isdigit() or int(key) <= 0 or type(amount) is not int or amount <= 0:
            raise ValueError('Invalid configured item reward')
    return card


def prepare_pool(state, wire_t, config, resolver, is_s=None, seed_factory=None):
    """Return (candidate, changed); groups are fixed before any result is exposed.

    config slots/cap/daily_cap/guarantee_at/require_complete are explicit original
    rules. Resolver must prioritize original chouka_default[(wire_t, ordinal)].
    is_s(card) recognizes original hero rank; guarantee fallback is only requested
    at configured ordinal and resolver must supply a real eligible S result.
    """
    out = _candidate(state)
    pool = _configured(out, wire_t, config)
    if pool['group'] is not None:
        return out, out != state
    if config.get('mode', 'cards') != 'cards':
        raise ValueError('Direct pool cannot create a card group')
    slots = pool.get('slots', 6)
    cap = config.get('cap')
    if cap is not None and pool['opened_total'] + slots > cap:
        raise ValueError('Original lifetime draw cap reached')
    if config.get('lazy'):
        if seed_factory is None:
            import random
            seed_factory = lambda: str(random.getrandbits(128))
        pool['group'] = {'id': pool['next_group'], 'cards': [
            {'index': i, 'is_open': False, '_gacha_seed': str(seed_factory())}
            for i in range(slots)]}
        pool['next_group'] += 1
        validate_gacha_pools_state(out)
        return out, True
    start = pool.get('allocated_total', pool['opened_total'])
    cards = []
    seen = pool.get('s_seen', False)
    guarantee = config.get('guarantee_at')
    for i in range(slots):
        ordinal = start + i + 1
        force = bool(guarantee and ordinal == guarantee and not seen)
        card = _resolve(resolver, wire_t, ordinal, force)
        if force and (is_s is None or not is_s(card)):
            raise ValueError('Configured original S guarantee was not satisfied')
        if is_s and is_s(card):
            seen = True
        card.update(index=i, is_open=False)
        cards.append(card)
    pool['group'] = {'id': pool['next_group'], 'cards': cards}
    pool['next_group'] += 1
    pool['allocated_total'] = start + slots
    # Tracks fixed results rather than claiming they have already been awarded.
    pool['s_seen'] = seen
    validate_gacha_pools_state(out)
    return out, True


def _credit(pool, card, make_id, stack_limit):
    for key, amount in sorted(card.get('hero_frag', {}).items()):
        item_id, remaining = int(key), amount
        maximum = stack_limit(item_id)
        if type(maximum) is not int or maximum < 1:
            raise ValueError('Missing original stack limit')
        for item in pool['items']:
            if item['i'] == item_id:
                added = min(remaining, max(0, maximum - item['w']))
                item['w'] += added
                remaining -= added
        while remaining:
            added = min(remaining, maximum)
            pool['items'].append({'u': str(make_id()), 'i': item_id, 'w': added,
                                 'tt': 0, 'c': 0, 'le': 0, 'lo': None, 'ele': 0, 'ctt': 0})
            remaining -= added


def open_pool_cards(state, wire_t, indices, make_id, stack_limit, credit_items=True, resolver=None, is_s=None):
    """Return candidate, client_cards, newly_granted_cards, changed.

    Arbitrary original treasure/hero fields survive exactly; caller atomically
    applies only newly_granted_cards to profile/equipment. Replays grant nothing.
    credit_items=False delegates item credit to caller canonical inventory.
    """
    out = _candidate(state)
    pool = _pool(out, wire_t)
    if pool is None or pool['group'] is None:
        raise ValueError('No fixed group in requested wire pool')
    indices = list(indices)
    if not indices or len(set(indices)) != len(indices) or any(type(i) is not int or not 0 <= i < pool.get('slots', 6) for i in indices):
        raise ValueError('Invalid pool card indices')
    newly = []
    for i in indices:
        card = pool['group']['cards'][i]
        if card['is_open']:
            continue
        if '_gacha_seed' in card and not card.get('_gacha_resolved'):
            if resolver is None:
                raise ValueError('Original lazy pool requires reveal resolver')
            ordinal = pool['opened_total'] + 1
            guarantee = pool.get('config', {}).get('guarantee_at')
            force = bool(guarantee and ordinal == guarantee and not pool.get('s_seen', False))
            resolved = resolver(wire_t, ordinal, force, card['_gacha_seed'], out)
            if not isinstance(resolved, dict):
                raise ValueError('Lazy resolver returned invalid reward')
            if force and (is_s is None or not is_s(resolved)):
                raise ValueError('Original reveal ordinal guarantee not satisfied')
            for private in ('index', 'is_open'):
                resolved.pop(private, None)
            card.update(copy.deepcopy(resolved))
            card['_gacha_resolved'] = True
            card['_gacha_ordinal'] = ordinal
            if is_s and is_s(card):
                pool['s_seen'] = True
        if credit_items:
            _credit(pool, card, make_id, stack_limit)
        card['is_open'] = True
        pool['opened_total'] += 1
        newly.append(gacha_result_for_client(card))
    validate_gacha_pools_state(out)
    return out, [gacha_result_for_client(pool['group']['cards'][i]) for i in indices], newly, bool(newly)


def pool_file_view(state, wire_t):
    if state is None:
        return {}
    validate_gacha_pools_state(state)
    pool = _pool(state, wire_t)
    if pool is None or pool['group'] is None:
        return {}
    return {str(c['index']): gacha_result_for_client(c) if c['is_open'] else
            {'index': c['index'], 'is_open': False} for c in pool['group']['cards']}


def quit_pool(state, wire_t):
    out = _candidate(state)
    pool = _pool(out, wire_t)
    if pool is None or pool['group'] is None:
        return out, False
    if pool.get('config', {}).get('require_complete') and any(not c['is_open'] for c in pool['group']['cards']):
        raise ValueError('Original limited group must be completed before retiring')
    pool['history'].append(copy.deepcopy(pool['group']))
    pool['history'] = pool['history'][-128:]
    pool['group'] = None
    return out, True


def direct_pool_draw(state, wire_t, config, count, operation_id, day_key,
                     resolver, make_id, stack_limit, credit_items=True, contextual_resolver=None):
    """Friend/newfriend independent direct transactions, with bounded replay IDs.

    config mode=direct,daily_cap=100,batch_sizes=[1,10]. day_key must be supplied
    from the persisted game-day contract. No wall-clock reset or debit hidden here.
    """
    out = _candidate(state)
    pool = _configured(out, wire_t, config)
    if config.get('mode') != 'direct' or type(count) is not int or count not in config.get('batch_sizes', [1, 10]) or not isinstance(operation_id, TEXT) or not operation_id or len(operation_id) > 200 or not isinstance(day_key, TEXT) or not day_key:
        raise ValueError('Invalid original direct-pool operation')
    if operation_id in pool.get('retired_operations', []):
        raise ValueError('Old operation already committed; no reward replay')
    for receipt in pool['receipts']:
        if receipt['id'] == operation_id:
            if receipt['count'] != count:
                raise ValueError('Replay ID has conflicting draw count')
            return out, copy.deepcopy(receipt['results']), [], False
    if pool['day_key'] != day_key:
        pool['day_key'], pool['daily_count'] = day_key, 0
    daily_cap = config.get('daily_cap')
    if daily_cap is not None and pool['daily_count'] + count > daily_cap:
        raise ValueError('Original friend daily limit reached')
    lifetime_cap = config.get('cap')
    if lifetime_cap is not None and pool['opened_total'] + count > lifetime_cap:
        raise ValueError('Original lifetime draw cap reached')
    results = []
    for i in range(count):
        card = (_resolve(resolver, wire_t, pool['opened_total'] + 1, False)
                if contextual_resolver is None else copy.deepcopy(contextual_resolver(wire_t,
                    pool['opened_total'] + 1, False, operation_id + ':' + str(i), out)))
        card.update(index=i, is_open=True)
        if credit_items:
            _credit(pool, card, make_id, stack_limit)
        pool['opened_total'] += 1
        pool['daily_count'] += 1
        results.append(gacha_result_for_client(card))
    pool['receipts'].append({'id': operation_id, 'count': count, 'results': copy.deepcopy(results)})
    if len(pool['receipts']) > 128:
        retired = pool['receipts'][:-128]
        pool.setdefault('retired_operations', []).extend(r['id'] for r in retired)
        pool['receipts'] = pool['receipts'][-128:]
    validate_gacha_pools_state(out)
    return out, results, copy.deepcopy(results), True


def pool_opened_total(state, wire_t):
    if state is None:
        return 0
    validate_gacha_pools_state(state)
    pool = _pool(state, wire_t)
    return pool['opened_total'] if pool else 0


def pool_items(state):
    if state is None:
        return []
    validate_gacha_pools_state(state)
    return [copy.deepcopy(item) for key in sorted(state['pools'], key=int)
            for item in state['pools'][key].get('items', [])]
