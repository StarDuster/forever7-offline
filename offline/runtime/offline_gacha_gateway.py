# -*- coding: ascii -*-
"""Original per-wire loader projection and one-time legacy transaction migration."""
import copy
try:
    from offline_gacha_special import project_special_gacha_snapshot, validate_special_gacha_state
    from offline_gacha import new_gacha_state
    from offline_gacha_pools import new_gacha_pools_state, validate_gacha_pools_state
except ImportError:
    pass


def migrate_gateway_gacha_state(state):
    candidate = copy.deepcopy(state)
    if candidate.get('gacha') is None:
        candidate['gacha'] = new_gacha_state()
    if candidate.get('gacha_pools') is None:
        candidate['gacha_pools'] = new_gacha_pools_state(candidate['gacha'])
        # Inventory belongs only to canonical gacha.items, never pool history.
        candidate['gacha_pools']['pools']['1']['items'] = []
        candidate['gacha']['group'] = None
    validate_gacha_pools_state(candidate['gacha_pools'])
    validate_special_gacha_state(candidate)
    normal = candidate['gacha_pools']['pools'].get('1', {})
    candidate['gacha']['opened_total'] = normal.get('opened_total', 0)
    return candidate


def original_pool_config(wire, configurations):
    if wire == 354:
        raise ValueError('Initial pool explicitly disabled by user; saved state preserved')
    if wire in (99, 131):
        return {'mode': 'direct', 'slots': 1, 'batch_sizes': [1, 10], 'daily_cap': 100}
    row = configurations.get(wire)
    if not row or row.get('drawType', wire) != wire:
        raise ValueError('No original configured wire pool')
    if row.get('poolType', 1) == 2:
        return {'mode': 'direct', 'slots': 1, 'batch_sizes': [1, 10]}
    result = {'slots': row.get('times', 6), 'lazy': True}
    return result


def gacha_snapshot_projection(state, template, configurations=None, special_context=None):
    out = copy.deepcopy(template)
    pools = (state.get('gacha_pools') or {}).get('pools', {})
    normal = pools.get('1') or state.get('gacha') or {}
    story = state.get('story') or {}
    day_key = '%s:%s' % (story.get('week', 0), story.get('date', 0))
    def daily(pool):
        return pool.get('daily_count', 0) if pool.get('day_key') in (None, day_key) else 0
    out.update(ct=normal.get('opened_total', 0), iof=bool(normal.get('group')),
               cctd=daily(normal),
               hfp=copy.deepcopy((state.get('gacha') or {}).get('hero_fragment_progress', {})))
    out['axlyn'] = (state.get('gacha') or {}).get('axiliya_tutorial_stage', out.get('axlyn', 0))
    out.setdefault('wi',[])
    previous = dict(out.get('ad', []))
    configured = set((configurations or {}).keys()) | set(int(k) for k in pools)
    out['ad'] = []
    for wire in sorted(configured - set([1, 99])):
        pool = pools.get(str(wire), {})
        info = copy.deepcopy(previous.get(wire, previous.get(str(wire), {})))
        info.update(ct=pool.get('opened_total', 0), iof=bool(pool.get('group')),
                    cctd=daily(pool), lt=pool.get('batch_count', 0))
        for key in ('tw', 'wi', 'jzc', 'jzr', 'rc'):
            info.setdefault(key, [])
        info.setdefault('ff', [])
        info.setdefault('ch', [0, 0, 0]);info.setdefault('ctr', [0, 0, 0])
        out['ad'].append((wire, info))
    friend, newfriend = pools.get('99', {}), pools.get('131', {})
    out['fd'] = bool(friend.get('opened_total', 0)) or out.get('fd', False)
    out['fdc'], out['nfdc'] = daily(friend), daily(newfriend)
    out['inc_up_cnt'] = copy.deepcopy((state.get('gacha_pools') or {}).get('inc_up_cnt', {}))
    out['iuc'] = [(int(key), value) for key, value in out['inc_up_cnt'].items()]
    return project_special_gacha_snapshot(state,out,special_context)


def gacha_economy_projection(state, snapshot):
    out = copy.deepcopy(snapshot)
    balances = (state.get('profile') or {}).get('economy', {})
    for canonical, wire in (('summoncoin', 'summonCoin'), ('friendcoin', 'friendCoin'),
                            ('newfriendcoin', 'newFriendCoin'), ('giftcoin', 'giftCoin'),
                            ('yuanbao', 'yuanbao'), ('crystal', 'crystal'), ('bind_crystal', 'bind_crystal')):
        if canonical in balances:
            out[wire] = balances[canonical]
    return out
