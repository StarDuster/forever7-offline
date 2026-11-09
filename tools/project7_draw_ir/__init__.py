"""Readonly exact outer draw graph. This module never grants or samples rewards."""
import hashlib
import json
import math
from fractions import Fraction


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False).encode('utf-8')


def typed(value):
    """Lossless literal encoding, including integer/tuple dictionary keys."""
    if value is None or type(value) in (str, bool, int):
        return value
    if type(value) is float:
        if not math.isfinite(value):
            raise ValueError('nonfinite literal')
        return {'$float': value.hex()}
    if isinstance(value, dict):
        entries = [[typed(k), typed(v)] for k, v in value.items()]
        return {'$dict': sorted(entries, key=lambda p: canonical(p[0]))}
    if isinstance(value, (tuple, list)):
        return {'$tuple' if isinstance(value, tuple) else '$list': [typed(x) for x in value]}
    raise ValueError('unsupported literal type')


def weight(row):
    value = row.get('weight', 0)
    if type(value) not in (int, float) or isinstance(value, bool):
        raise ValueError('invalid weight')
    if isinstance(value, float) and not math.isfinite(value):
        raise ValueError('nonfinite weight')
    result = Fraction(str(value))
    if result < 0:
        raise ValueError('negative weight')
    return result


def compile_outer(normal, defaults):
    """Compile official chouka_normal/default shapes, preserving opaque leaf refs.

    Missing/zero weight excludes a row. Multiple reward_random references remain
    an ordered opaque tuple: no unproven split or reward classification is made.
    """
    pools = {}
    ids = set()
    for key, row in normal.items():
        if type(key) is not int or row.get('id') != key or key in ids:
            raise ValueError('invalid/duplicate row id')
        ids.add(key)
        wire = row.get('type')
        if type(wire) is not int or wire <= 0:
            raise ValueError('invalid wire t')
        w = weight(row)
        if not w:
            continue
        refs = row.get('random_reward')
        if not isinstance(refs, (tuple, list)) or not refs or any(type(x) is not int or x <= 0 for x in refs):
            raise ValueError('invalid reward_random references')
        pools.setdefault(wire, []).append((key, w, list(refs)))
    result = []
    for wire, rows in sorted(pools.items()):
        total = sum((r[1] for r in rows), Fraction())
        branches = []
        for key, w, refs in sorted(rows):
            p = w / total
            branches.append({'row_id': key, 'random_reward_refs': refs, 'weight': [w.numerator, w.denominator], 'mass': [p.numerator, p.denominator]})
        assert sum((Fraction(*r['mass']) for r in branches), Fraction()) == 1
        result.append({'wire_t': wire, 'total_weight': [total.numerator, total.denominator], 'branches': branches})
    overrides = []
    seen = set()
    for key, row in defaults.items():
        pair = (row.get('draw_type'), row.get('chouka_time'))
        if key != pair or any(type(x) is not int or x <= 0 for x in pair) or pair in seen:
            raise ValueError('invalid/duplicate default key')
        seen.add(pair)
        if 'pool' not in row:
            continue
        if type(row['pool']) is not int or row['pool'] <= 0:
            raise ValueError('invalid override pool')
        source = normal.get(row['pool'])
        if source is None:
            raise ValueError('missing default normal row reference')
        refs = source.get('random_reward')
        if not isinstance(refs, (tuple, list)) or not refs or any(type(x) is not int or x <= 0 for x in refs):
            raise ValueError('invalid default random_reward references')
        overrides.append({'wire_t': pair[0], 'ordinal': pair[1], 'normal_row_id': row['pool'], 'random_reward_refs': list(refs)})
    return {'schema': 1, 'stage': 'outer-only-unresolved-leaves', 'executable_rewards': False,
            'pools': result, 'ordinal_overrides': sorted(overrides, key=lambda r: (r['wire_t'], r['ordinal'])),
            'literal_tables': {'chouka_normal': typed(normal), 'chouka_default': typed(defaults)}}


def resolve_outer(ir, wire_t, ordinal):
    if type(wire_t) is not int or type(ordinal) is not int or ordinal <= 0:
        raise ValueError('invalid request')
    for row in ir['ordinal_overrides']:
        if (row['wire_t'], row['ordinal']) == (wire_t, ordinal):
            return {'override': row['normal_row_id'], 'random_reward_refs': row['random_reward_refs']}
    for pool in ir['pools']:
        if pool['wire_t'] == wire_t:
            return pool
    raise ValueError('unknown/empty wire pool')


def require_executable(ir):
    raise ValueError('reward_random/common leafchain not compiled; no executable rewards')


def untyped(value):
    """Decode our exact canonical literal representation (no code evaluation)."""
    if value is None or type(value) in (str, bool, int):
        return value
    if not isinstance(value, dict) or len(value)!=1:
        raise ValueError('invalid typed literal')
    tag, body = next(iter(value.items()))
    if tag == '$float':
        result=float.fromhex(body)
        if not math.isfinite(result):raise ValueError('nonfinite typed float')
        return result
    if tag in ('$tuple','$list'):
        items=[untyped(x) for x in body]
        return tuple(items) if tag=='$tuple' else items
    if tag=='$dict':
        result={}
        for k,v in body:
            key=untyped(k)
            if key in result:raise ValueError('duplicate typed key')
            result[key]=untyped(v)
        return result
    raise ValueError('unknown literal tag')
