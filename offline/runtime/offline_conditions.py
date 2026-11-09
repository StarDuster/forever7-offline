# -*- coding: ascii -*-
"""Original EventCond classes with typed, read-only, three-state offline facts.

True/False are proven by current canonical facts; None means absent producer or
unsupported syntax. Known false predicates exclude a row even when another is
unknown. No eval/ast, no APK imports, no mutation, no history-as-current facts.
"""
try:
    from offline_flashback import (flashback_context, flashback_token, flashback_data,
        flashback_notice, flashback_require_action, flashback_spend_action,
        flashback_accept_entry, flashback_route_handoff, prepare_flashback_operation,
        validate_flashback_state)
except ImportError:
    pass

try:
    from offline_action_ledger import code20_condition_values
except ImportError:
    pass

import re
try:
    _oc_text = (basestring,)
    _oc_int_types = (int, long)
except NameError:
    _oc_text = (str,)
    _oc_int_types = (int,)

_OC_ABSENT = object()
_OC_ALL = set((1, 9, 10, 24, 34, 35, 36, 42, 43, 102))
_OC_ANY2 = set((17, 29, 41, 48))
_OC_NONE = set((11, 25, 44))
_OC_SCALAR_SET = set((3, 52, 100))
_OC_INTERVAL = set((4, 7, 16, 21, 26, 27, 28, 30, 45, 46, 49, 50, 51, 53, 54))
_OC_THRESHOLD = set((12, 13, 14, 15, 33, 38, 39, 40))
_OC_MINMAX = set((5, 6, 19, 23, 31, 37))
_OC_DICT_GE = set((20, 22, 32))
_OC_KINDS = (_OC_ALL | _OC_ANY2 | _OC_NONE | _OC_SCALAR_SET | _OC_INTERVAL |
             _OC_THRESHOLD | _OC_MINMAX | _OC_DICT_GE | set((8, 18, 47, 101)))


def _oc_integer(value):
    return isinstance(value, _oc_int_types) and not isinstance(value, bool)


class _OriginalLiteralReader(object):
    """Bounded numbers/quoted strings/containers/set grammar, never code."""
    def __init__(self, value):
        self.value, self.at, self.nodes = value, 0, 0

    def whitespace(self):
        while self.at < len(self.value) and self.value[self.at].isspace(): self.at += 1

    def literal(self, depth=0):
        self.nodes += 1
        if depth > 12 or self.nodes > 2048: raise ValueError('Literal bound exceeded')
        self.whitespace()
        if self.at >= len(self.value): raise ValueError('Truncated original literal')
        char = self.value[self.at]
        if char in ('\"', "'"):
            self.at += 1
            out = []
            while self.at < len(self.value):
                current = self.value[self.at]; self.at += 1
                if current == char: return ''.join(out)
                if current == '\\':
                    if self.at >= len(self.value): raise ValueError('Truncated quoted literal')
                    current = self.value[self.at]; self.at += 1
                    escape = {'\\': '\\', "'": "'", '"': '"', 'n': '\n', 't': '\t', 'r': '\r'}
                    if current not in escape: raise ValueError('Unsupported quoted escape')
                    current = escape[current]
                out.append(current)
            raise ValueError('Unterminated quoted literal')
        if char in '[({':
            self.at += 1
            closing = {'[': ']', '(': ')', '{': '}'}[char]
            items = []
            self.whitespace()
            if self.at < len(self.value) and self.value[self.at] == closing:
                self.at += 1
                return {} if char == '{' else (() if char == '(' else [])
            while True:
                key = self.literal(depth + 1)
                self.whitespace()
                if char == '{':
                    if self.at >= len(self.value) or self.value[self.at] != ':': raise ValueError('Expected original dict colon')
                    self.at += 1
                    item = self.literal(depth + 1)
                    items.append((key, item))
                else: items.append(key)
                self.whitespace()
                if self.at >= len(self.value): raise ValueError('Unclosed original container')
                if self.value[self.at] == closing:
                    self.at += 1; break
                if self.value[self.at] != ',': raise ValueError('Expected original container comma')
                self.at += 1; self.whitespace()
                if self.at < len(self.value) and self.value[self.at] == closing:
                    self.at += 1; break
            try:
                return dict(items) if char == '{' else (tuple(items) if char == '(' else items)
            except (TypeError, ValueError):
                raise ValueError('Unhashable original literal key')
        for name in ('frozenset', 'set'):
            if self.value.startswith(name, self.at):
                self.at += len(name); self.whitespace()
                if self.at >= len(self.value) or self.value[self.at] != '(': raise ValueError('Expected set literal')
                self.at += 1; self.whitespace()
                if self.at < len(self.value) and self.value[self.at] == ')':
                    self.at += 1; return set()
                items = self.literal(depth + 1); self.whitespace()
                if self.at >= len(self.value) or self.value[self.at] != ')' or not isinstance(items, (tuple, list, set, frozenset)):
                    raise ValueError('Invalid set literal')
                self.at += 1
                try: return set(items)
                except TypeError: raise ValueError('Unhashable original set member')
        match = re.match(r'[+-]?\d+', self.value[self.at:])
        if match:
            self.at += len(match.group(0)); return int(match.group(0))
        raise ValueError('Unsupported original literal token')


def parse_original_condition_literal(value):
    """Return parsed value, raise ValueError for unsupported or oversized syntax."""
    budget = [0]
    def validate(item, depth=0):
        budget[0] += 1
        if budget[0] > 4096: raise ValueError('Native literal node bound exceeded')
        if depth > 12: raise ValueError('Native literal bound exceeded')
        if item is None or isinstance(item, (bool,) + _oc_int_types + _oc_text): return
        if isinstance(item, dict):
            if len(item) > 2048: raise ValueError('Native literal bound exceeded')
            for key, element in item.items(): validate(key, depth + 1); validate(element, depth + 1)
            return
        if isinstance(item, (list, tuple, set, frozenset)):
            if len(item) > 2048: raise ValueError('Native literal bound exceeded')
            for element in item: validate(element, depth + 1)
            return
        raise ValueError('Unsupported native condition value')
    if not isinstance(value, _oc_text):
        validate(value); return value
    if len(value) > 8192: raise ValueError('Original condition text too large')
    reader = _OriginalLiteralReader(value)
    result = reader.literal(); reader.whitespace()
    if reader.at != len(value): raise ValueError('Unexpected original literal suffix')
    return result


def _oc_interval(value, actual):
    if not _oc_integer(actual): return None
    if isinstance(value, _oc_text):
        if len(value) > 8192: return None
        match = re.match(r'^\s*([\[(])\s*([+-]?\d+)?\s*,\s*([+-]?\d+)?\s*([\])])\s*$', value)
        if match:
            left, low, high, right = match.groups()
            low = int(low) if low is not None else None
            high = int(high) if high is not None else None
            low_inc, high_inc = left == '[', right == ']'
        elif re.match(r'^\s*[+-]?\d+\s*$', value):
            low = high = int(value); low_inc = high_inc = True
        else: return None
    elif _oc_integer(value):
        low = high = value; low_inc = high_inc = True
    elif isinstance(value, (list, tuple)) and len(value) == 2 and all(_oc_integer(v) or v is None for v in value):
        low, high = value; low_inc = high_inc = isinstance(value, list)
    else: return None
    if low is not None and high is not None and low > high: return None
    if low is not None and (actual < low or actual == low and not low_inc): return False
    if high is not None and (actual > high or actual == high and not high_inc): return False
    return True


def _oc_lookup(mapping, key, absent=_OC_ABSENT):
    if not isinstance(mapping, dict): return absent
    return mapping.get(key, mapping.get(str(key), absent))


def _oc_set(value):
    if not isinstance(value, (set, frozenset, list, tuple)): return None
    try: return set(tuple(v) if isinstance(v, list) else v for v in value)
    except TypeError: return None


def _oc_patrol(state, context):
    if 'patrol' in context: return context['patrol']
    if 'patrol_area' in context or 'patrol_heroes' in context:
        return {'area': context.get('patrol_area'), 'heroes': context.get('patrol_heroes')}
    return state.get('city_actions', {}).get('patrol')


def _oc_inventory(state):
    profile = state.get('profile')
    if not isinstance(profile, dict): return None
    treasure = profile.get('treasures')
    gacha = state.get('gacha')
    if not isinstance(treasure, dict) and not isinstance(gacha, dict): return None
    return list((treasure or {}).get('items', [])) + list((gacha or {}).get('items', []))


def _oc_fact(kind, state, context, required):
    for supplied in (context.get('condition_values', {}), state.get('condition_values', {})):
        result = _oc_lookup(supplied, kind)
        if result is not _OC_ABSENT: return result
    story = state.get('story', {})
    city = story.get('city_values', {})
    profile = state.get('profile') or {}
    roster = profile.get('heroes')
    patrol = _oc_patrol(state, context)
    if kind in (1, 17): return state.get('completed_events')
    if kind == 11:
        if 'completed_events' not in state or 'processing_events' not in state: return None
        return set(state['completed_events']) | set(state['processing_events'])
    if kind == 9: return story.get('battle_wins')
    if kind == 4: return story.get('date')
    if kind == 16: return story.get('week')
    if kind == 52: return story.get('route')
    if kind in (24, 25):
        if context.get('selected_starter_only'):
            return [] if story.get('starter_hero') is None else [story['starter_hero']]
        return None if roster is None else set(int(hero) for hero in roster)
    if kind in (3, 10, 29):
        if not patrol: return _OC_ABSENT if kind == 3 else set()
        if kind == 3: return patrol.get('area')
        if kind == 10: return patrol.get('heroes')
        area = _oc_lookup(story.get('city_areas'), patrol.get('area'))
        return None if area is _OC_ABSENT else set(b['id'] for b in area.get('bd', {}).values())
    if kind == 100:
        return context.get('click_area', _oc_lookup(dict(state.get('conditions', [])), 100))
    if kind == 101:
        if 'emergency' in story: return int(story['emergency'])
        return _oc_lookup(dict(state.get('conditions', [])), 101, None)
    if kind == 102:
        if context.get('client_operations') is not None: value = context['client_operations']
        else: value = _oc_lookup(dict(state.get('conditions', [])), 102, [])
        return [value] if _oc_integer(value) else value
    if kind == 7: return profile.get('economy', {}).get('level')
    if kind == 33: return profile.get('economy', {}).get('money')
    if kind in (21, 26, 27, 28, 30):
        return city.get({21: 'bf', 26: 'fv', 27: 'rv', 28: 'dv', 30: 'cc'}[kind])
    if kind in (8, 47):
        areas = story.get('city_areas')
        if not isinstance(areas, dict): return None
        # Original CityData.get_area_state returns default FALL2 for absent areas.
        return {key: _oc_lookup(areas, key, {}).get('st', [2])[0] for key in required}
    if kind == 18:
        areas = story.get('city_areas')
        if not isinstance(areas, dict): return None
        return {int(key): set(b['id'] for b in area.get('bd', {}).values()) for key, area in areas.items()}
    if kind == 22:
        areas = story.get('city_areas')
        return None if not isinstance(areas, dict) else {int(key): area.get('lv') for key, area in areas.items()}
    if kind == 5:
        inventory = _oc_inventory(state)
        if inventory is None: return None
        totals = {key: 0 for key in required}
        for item in inventory:
            if not _oc_integer(item.get('i')) or not _oc_integer(item.get('w')): return None
            totals[item['i']] = totals.get(item['i'], 0) + item['w']
        return totals
    if kind in (6, 37, 32):
        if not isinstance(roster, dict): return None
        field = {6: 'ef', 37: 'cf', 32: 'oa'}[kind]
        # HeroData.initFromDict uses top-level oa=False, NOT ar.oa (order attrs).
        return {int(hero): record.get(field, False if kind == 32 else None) for hero, record in roster.items()}
    if kind == 23:
        cores = story.get('blackcores')
        if not isinstance(cores, dict): return None
        counts = {key: 0 for key in required}
        for camp in cores.values():
            if not _oc_integer(camp): return None
            if camp: counts[camp] = counts.get(camp, 0) + 1
        return counts
    if kind in (42, 48):
        if 'cgs' not in story and 'cg' not in story: return None
        return set(story.get('cgs', [])) | set(story.get('cg', []))
    if kind == 12: return state.get('day', {}).get('actions_spent')
    if kind in (13, 14, 15): return context.get({13: 'insight_sum', 14: 'construct_sum', 15: 'leadership_sum'}[kind])
    if kind in (38, 39, 40):
        if not patrol or not isinstance(patrol.get('heroes'), (list, tuple)): return None
        abilities = context.get('abilities', patrol.get('abilities', {}))
        field = {38: 'insight', 39: 'construct', 40: 'leadership'}[kind]
        values = [_oc_lookup(abilities, hero, {}).get(field) for hero in patrol['heroes']]
        return sum(values) if all(_oc_integer(value) for value in values) else None
    if kind == 19:
        values = {}
        for event in required:
            if event not in state.get('completed_events', []): continue
            baseline = _oc_lookup(story.get('event_days', {}), event, None)
            day = state.get('day', {}).get('stock_day')
            if not isinstance(baseline, dict) or not _oc_integer(day): values[event] = None
            elif baseline.get('week') == story.get('week') and _oc_integer(baseline.get('day')): values[event] = day - baseline['day']
        return values
    if kind == 20:
        # Explicit offline ledger owner; an absent/invalid ledger is unknown,
        # never zero.  The old inline week_actions_spent branch remains only as
        # its same-week legacy reader inside offline_action_ledger.
        reader = globals().get('code20_condition_values')
        if reader is not None:
            try:
                return reader(state, required, state.get('completed_events', []))
            except (ValueError, TypeError, KeyError):
                return dict((event, None) for event in required)
        values = {}
        for event in required:
            if event not in state.get('completed_events', []): continue
            baseline = _oc_lookup(story.get('event_action_baselines', {}), event, None)
            spent = story.get('week_actions_spent')
            stamp = _oc_lookup(story.get('event_days', {}), event, None)
            same_week = (isinstance(stamp, dict) and _oc_integer(stamp.get('week')) and
                         stamp.get('week') == story.get('week'))
            if (_oc_integer(spent) and _oc_integer(baseline) and 0 <= baseline <= spent and same_week):
                values[event] = spent - baseline
            else:
                values[event] = None
        return values
    if kind == 45:
        # Original HeroData.huohaihua is initDict['hhh'] (default False) and
        # HeroMgrMember.huohaihuaReply sets it True.  The original event effect
        # 'huohaihua' writes the same per-hero flag.  bhrs/banned_heroes is the
        # separate ban/recover mechanic, not this count.
        if not isinstance(roster, dict): return None
        count = 0
        for hero in roster.values():
            if not isinstance(hero, dict): return None
            flag = hero.get('hhh', False)
            if type(flag) is not bool: return None
            if flag: count += 1
        return count
    if kind in (46, 49):
        if not isinstance(roster, dict): return None
        field = 'ef' if kind == 46 else 'cf'
        values = [hero.get(field) for hero in roster.values()]
        if not all(_oc_integer(value) for value in values): return None
        return sum(value >= 50 if kind == 46 else value < 20 for value in values)
    if kind == 50:
        if not isinstance(roster, dict): return None
        current = set(story.get('conquered_heroes', []))
        current.update(int(key) for key, hero in roster.items() if hero.get('cfd') is True)
        return len(current)
    if kind == 54 and flashback_context(state) is not None:
        return flashback_context(state)['index']
    if kind == 54 and str(story.get('route', '')).split('-')[0] == '35':
        return None
    if kind in (51, 53, 54):
        names = {51: ('baiyu_value', 'baiyuval'), 53: ('yisake_value', 'yisake_intimate_val'), 54: ('general_value',)}[kind]
        for name in names:
            if name in context: return context[name]
            if name in story: return story[name]
        # Original StoryData.gr starts at zero. Only verified bounty routes
        # use this default; route35's unrelated cycle-index producer is unknown.
        if kind == 54 and str(story.get('route')) in ('31','31-4'):
            return 0
        # Never derive GeneralValue from a universal inventory item count.
        return None
    if kind in (34, 35, 36, 41):
        inventory = _oc_inventory(state)
        if inventory is None or not isinstance(roster, dict): return None
        equipped = set(item['u'] for hero in roster.values() for item in hero.get('ti', {}).get('items', []))
        pairs = set()
        for item in inventory:
            if not item.get('tr'): continue
            quality = item['tr'].get('cl')
            if not _oc_integer(item.get('i')) or not _oc_integer(quality): return None
            is_equipped = item['u'] in equipped
            if kind == 34 and not is_equipped or kind == 35 and is_equipped: continue
            pairs.add((item['i'], quality))
        return pairs
    if kind in (43, 44): return context.get('hero_files', story.get('hero_files'))
    if kind == 31:
        # Original HeroData.starLevel=sl and starOrder=so (initFromDict requires
        # both).  The client compares them as starLevel*MAX_STAR_ORDER+starOrder
        # with const.HeroStar.MAX_STAR_ORDER=4: city_shuzhi_zhiyuan_window.py:79,
        # activity_212_stage.py:430, battle_herolist.py:770, hero_star.py:152.
        # A 4-4 hero is therefore 4*4+4=20, matching table value {hero:(20,)}.
        if not isinstance(roster, dict): return None
        values = {}
        for hero in required:
            record = _oc_lookup(roster, hero)
            if record is _OC_ABSENT: continue
            if not isinstance(record, dict): return None
            star_level, star_order = record.get('sl'), record.get('so')
            if not (_oc_integer(star_level) and _oc_integer(star_order)): return None
            values[hero] = star_level * 4 + star_order
        return values
    return None


def evaluate_offline_condition(kind, table_value, full_state, context=None):
    if not _oc_integer(kind) or kind not in _OC_KINDS: return None
    context = context or {}
    if table_value is None or isinstance(table_value, _oc_text) and not table_value.strip(): return True
    try:
        required = table_value if kind in _OC_INTERVAL else parse_original_condition_literal(table_value)
        if kind in _OC_ALL | _OC_ANY2 | _OC_NONE | _OC_SCALAR_SET:
            empty_check = _oc_set(required)
            if empty_check is None: return None
            if not empty_check: return kind in _OC_ALL | _OC_NONE
        if kind in _OC_MINMAX | _OC_DICT_GE | set((8, 18, 47)):
            if not isinstance(required, dict): return None
            if not required: return kind not in (8, 18)
        actual = _oc_fact(kind, full_state, context, required)
        if kind in _OC_INTERVAL: return _oc_interval(required, actual)
        if kind in _OC_THRESHOLD:
            return actual >= required if _oc_integer(actual) and _oc_integer(required) else None
        if kind == 101:
            return int(actual) == required if isinstance(actual, (bool,) + _oc_int_types) and _oc_integer(required) else None
        if kind in _OC_ALL | _OC_ANY2 | _OC_NONE | _OC_SCALAR_SET:
            wanted = _oc_set(required)
            if wanted is None: return None
            if kind in _OC_SCALAR_SET:
                if actual is _OC_ABSENT: return False
                if actual is None or isinstance(actual, (dict, list, tuple, set, frozenset)): return None
                return actual in wanted
            available = _oc_set(actual)
            if available is None: return None
            if kind in _OC_ALL: return wanted.issubset(available)
            if kind in _OC_ANY2: return bool(wanted & available)
            return not bool(wanted & available)
        if kind in _OC_MINMAX | _OC_DICT_GE | set((8, 18, 47)):
            if not isinstance(required, dict) or not isinstance(actual, dict): return None
            results = []
            for key, wanted in required.items():
                present = _oc_lookup(actual, key)
                if present is _OC_ABSENT: results.append(False); continue
                if present is None: results.append(None); continue
                if kind in _OC_MINMAX:
                    valid = isinstance(wanted, (list, tuple)) and len(wanted) == 2 and all(_oc_integer(v) for v in wanted)
                    results.append(wanted[0] <= present <= wanted[1] if valid and _oc_integer(present) else None)
                elif kind in _OC_DICT_GE:
                    valid = isinstance(present, (bool,) + _oc_int_types) and isinstance(wanted, (bool,) + _oc_int_types)
                    results.append(present >= wanted if valid else None)
                elif kind in (8, 47):
                    group = _oc_set(wanted)
                    results.append(present in group if group is not None else None)
                else:
                    group, have = _oc_set(wanted), _oc_set(present)
                    results.append(bool(group & have) if group is not None and have is not None else None)
            if kind in (8, 18):
                if any(result is True for result in results): return True
                return None if any(result is None for result in results) else False
            if any(result is False for result in results): return False
            return None if any(result is None for result in results) else True
    except (ValueError, TypeError, KeyError, IndexError, OverflowError, AttributeError):
        return None
    return None


def evaluate_offline_trigger(row, full_state, context=None):
    if not isinstance(row, dict): return None
    if not row.get('release'): return False
    conditions = row.get('conds', {})
    if not isinstance(conditions, dict): return None
    unknown = False
    for kind, value in conditions.items():
        result = evaluate_offline_condition(kind, value, full_state, context)
        if result is False: return False
        if result is None: unknown = True
    return None if unknown else True
