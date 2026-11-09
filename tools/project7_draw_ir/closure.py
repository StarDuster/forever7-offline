"""Exact hierarchical readonly selection; no RNG, counters, spending or grants."""
from fractions import Fraction
from . import compile_outer, resolve_outer, typed, weight


def ratio(v):
    return [v.numerator, v.denominator]


def weighted(rows):
    rows = list(rows)
    if any(type(identity) is not int or identity <= 0 for identity, w in rows) or len({identity for identity, w in rows}) != len(rows):
        raise ValueError('invalid/duplicate weighted reference')
    positive = [(identity, weight({'weight': w})) for identity, w in rows]
    positive = [(identity, w) for identity, w in positive if w]
    if len({k for k, w in positive}) != len(positive) or not positive:
        raise ValueError('duplicate/empty positive weighted references')
    total = sum((w for k, w in positive), Fraction())
    return [{'id': k, 'weight': ratio(w), 'mass': ratio(w / total)} for k, w in positive]


def compile_t1(normal, defaults, random, common):
    all_normal = normal
    normal = {k:v for k,v in all_normal.items() if v.get('type') == 1}
    defaults = {k:v for k,v in defaults.items() if v.get('draw_type') == 1}
    outer = compile_outer(all_normal, defaults)
    outer['pools'] = [p for p in outer['pools'] if p['wire_t'] == 1]
    relevant = set(normal) | {row['pool'] for row in defaults.values() if row.get('pool')}
    outer['literal_tables']['chouka_normal'] = typed({k:all_normal[k] for k in relevant})
    if len(outer['pools']) != 1 or outer['pools'][0]['wire_t'] != 1:
        raise ValueError('missing positive t1 base pool')
    refs = set()
    for pool in outer['pools']:
        for branch in pool['branches']:
            if len(branch['random_reward_refs']) != 1:
                raise ValueError('multi-ID random_reward semantics unproven')
            refs.update(branch['random_reward_refs'])
    for row in outer['ordinal_overrides']:
        if len(row['random_reward_refs']) != 1:
            raise ValueError('multi-ID default random_reward semantics unproven')
        refs.update(row['random_reward_refs'])
    pools, rewards = {}, {}
    for rid in sorted(refs):
        if rid not in random or random[rid].get('id') != rid:
            raise ValueError('missing/mismatched reward_random')
        branches = weighted(random[rid].get('weights', ()))
        for branch in branches:
            cid = branch['id']
            if type(cid) is not int or cid not in common or common[cid].get('id') != cid:
                raise ValueError('missing/mismatched reward_common')
            reward = common[cid]
            if reward.get('award_pool'):
                raise ValueError('nested award_pool semantics unproven')
            rewards[str(cid)] = typed(reward)
        pools[str(rid)] = {'branches': branches, 'source_row': typed(random[rid])}
    # Metadata such as tradeType is retained, never treated as a payout component.
    component_keys = ('hero', 'items', 'treasure', 'design_treasure', 'summoncoin', 'money')
    signatures = {}
    masses = {}
    for branch in outer['pools'][0]['branches']:
        rid = branch['random_reward_refs'][0]
        for leaf in pools[str(rid)]['branches']:
            row = common[leaf['id']]
            signature = '+'.join(k for k in component_keys if row.get(k)) or 'unknown'
            signatures[signature] = signatures.get(signature, 0) + 1
            masses[signature] = masses.get(signature, Fraction()) + Fraction(*branch['mass']) * Fraction(*leaf['mass'])
    if sum(masses.values(), Fraction()) != 1:
        raise ValueError('hierarchical probability mass not conserved')
    return {'schema': 1, 'scope': 't1-fixed-base-reward-selection-only',
            'stock_grants_implemented': False, 'ordinal_lifecycle_proven': False,
            'outer': outer, 'random_pools': pools, 'reward_bundles': rewards,
            'base_component_signature_mass': {k: ratio(v) for k,v in sorted(masses.items())},
            'base_branch_signature_counts': signatures}


def ticket_select(branches, numerator, denominator):
    """Select using a caller-provided exact rational in [0,1), no float rounding."""
    if type(numerator) is not int or type(denominator) is not int or denominator <= 0 or not 0 <= numerator < denominator:
        raise ValueError('invalid entropy fraction')
    masses = [Fraction(*branch['mass']) for branch in branches]
    if not masses or any(m <= 0 for m in masses) or sum(masses, Fraction()) != 1:
        raise ValueError('invalid weighted mass')
    point, cumulative = Fraction(numerator, denominator), Fraction()
    for branch in branches:
        cumulative += Fraction(*branch['mass'])
        if point < cumulative:
            return branch
    raise ValueError('invalid weighted graph')


def select_bundle(ir, *, ordinal, outer_ticket, inner_ticket):
    """Return one entire typed common bundle. Caller owns ordinal semantics.

    This is a pure data selector, not a grant or an implementation of official
    server pity/guarantees. Never use it to mutate existing/pending stock slots.
    """
    node = resolve_outer(ir['outer'], 1, ordinal)
    if 'override' in node:
        if len(node['random_reward_refs']) != 1:
            raise ValueError('ambiguous default random references')
        rid = node['random_reward_refs'][0]
    else:
        branch = ticket_select(node['branches'], *outer_ticket)
        refs = branch['random_reward_refs']
        if len(refs) != 1:
            raise ValueError('ambiguous random references')
        rid = refs[0]
    leaf = ticket_select(ir['random_pools'][str(rid)]['branches'], *inner_ticket)
    return {'random_reward_id': rid, 'common_reward_id': leaf['id'],
            'bundle': ir['reward_bundles'][str(leaf['id'])]}
