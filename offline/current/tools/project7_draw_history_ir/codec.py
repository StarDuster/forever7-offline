"""Canonical lossless literal codec; standard-library-only consumer support."""
import json
import math

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

def untyped(value):
    """Decode our exact canonical literal representation (no code evaluation)."""
    if value is None or type(value) in (str, bool, int):
        return value
    if not isinstance(value, dict) or len(value) != 1:
        raise ValueError('invalid typed literal')
    tag, body = next(iter(value.items()))
    if tag == '$float':
        result = float.fromhex(body)
        if not math.isfinite(result):
            raise ValueError('nonfinite typed float')
        return result
    if tag in ('$tuple', '$list'):
        items = [untyped(x) for x in body]
        return tuple(items) if tag == '$tuple' else items
    if tag == '$dict':
        result = {}
        for k, v in body:
            key = untyped(k)
            if key in result:
                raise ValueError('duplicate typed key')
            result[key] = untyped(v)
        return result
    raise ValueError('unknown literal tag')
