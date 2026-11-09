"""Original seven route agreement effects; caller owns admission and receipt atomicity.

Canonical top-level names match StoryData; Yumi uses only story['yumi']['ysg'].
Day reset is an explicit offline successful-commit policy. New story projections
write false flags even when the supplied original snapshot belongs to last week.
"""
import copy
try:
    _ROUTE_STRING_TYPES = (basestring,)
except NameError:
    _ROUTE_STRING_TYPES = (str,)
try:
    from offline_yumi import ensure_yumi, yumi_projection
except ImportError:
    pass  # Embedded runtime concatenates Yumi definitions before this module.

_ROUTE_FLAGS = {
    'wulu_special_goodnight': 'wsg',
    'jiaohui_special_goodnight': 'jsg',
    'alanSpecialGoodNight': 'alsg',
    'show_daerweila_head': 'sdh',
    'daerweila_human_lock': 'dwhl',
    'daerweila_devil_lock': 'dwdl',
}
_ROUTE_WULU = {'wuluClue': ('wlc', []), 'wuluClueReaded': ('wlr', False),
        'wuluDetailReaded': ('wldr', [])}
AGREEMENT_VALUES = frozenset(('1', '2', '5', '6', 'daerweila_clue_open',
    'daerweila_clue_close', 'daerweila_human_close', 'daerweila_devil_close'))
# Shared by the classifier and executor: original string values, never event IDs.
AGREEMENT_MECHANISMS = dict((value, 'yumi' if value == '2' else 'route_agreement')
                            for value in AGREEMENT_VALUES)



def _flag(story, name):
    value = story.get(name, False)
    if type(value) is not bool:
        raise ValueError('Invalid route agreement flag: ' + name)
    return value


def _wulu(story, native_std=None):
    seed = native_std or {}
    result = {}
    for name, (wire, default) in _ROUTE_WULU.items():
        value = copy.deepcopy(story.get(name, seed.get(wire, default)))
        if wire == 'wldr' and isinstance(value, dict):
            value = [list(pair) for pair in value.items()]
        if wire == 'wlr':
            if type(value) is not bool: raise ValueError('Invalid Wulu read flag')
        elif not isinstance(value, list):
            raise ValueError('Invalid Wulu list: ' + wire)
        result[wire] = value
    result['wsg'] = _flag(story, 'wulu_special_goodnight')
    return result


def apply_route_agreement(story, event, row, native_std=None):
    """Apply an admitted original row by its agreement value; no completion, route selection or awards.

    native_std supplies existing Wulu clue data only. Locks/flags must be canonical;
    use original attribute names when importing an existing StoryData into story.
    Garden '2' belongs exclusively to apply_yumi_event. The caller must check
    trusted table membership, engine conditions, callbacks and durable receipts.
    """
    value = row.get('special_agreement')
    if value is None: return []
    if not isinstance(value, _ROUTE_STRING_TYPES): raise ValueError('Agreement must be original string')
    if type(event) is not int: raise ValueError('Agreement event must be integer')
    if value not in AGREEMENT_VALUES: raise ValueError('Unknown route agreement')
    if value == '2': return []
    if value == '1':
        ensure_yumi(story)['ysg'] = True
        return [('syncBaiyuInfos', {'d': yumi_projection(story)})]
    if value == '5':
        body = _wulu(story, native_std)
        story['wulu_special_goodnight'] = True
        # Capture the seed once; later full notices must not erase original clues.
        for name, (wire, _) in _ROUTE_WULU.items():
            story[name] = copy.deepcopy(body[wire])
        body['wsg'] = True
        return [('syncWuluLineData', body)]
    if value == '6':
        family = str(story.get('route', '')).split('-', 1)[0]
        if family == '9':
            story['jiaohui_special_goodnight'] = True
            return [('syncJiaohuiSpecialNight', {'jsn': True})]
        if family == '11':
            story['alanSpecialGoodNight'] = True
            return [('syncAlanSpecialNight', {'asn': True})]
        raise ValueError('Agreement 6 requires route family 9 or 11')
    if value in ('daerweila_clue_open', 'daerweila_clue_close'):
        opened = value == 'daerweila_clue_open'
        story['show_daerweila_head'] = opened
        return [('daerweilaClueComp', {'s': opened})]
    human = _flag(story, 'daerweila_human_lock') or value == 'daerweila_human_close'
    devil = _flag(story, 'daerweila_devil_lock') or value == 'daerweila_devil_close'
    story['daerweila_human_lock'] = human
    story['daerweila_devil_lock'] = devil
    return [('daerweilaDispatchClose', {'h': human, 'd': devil})]


def project_route_agreements(story, base_std):
    result = copy.deepcopy(base_std)
    for name, wire in _ROUTE_FLAGS.items(): result[wire] = _flag(story, name)
    result.update(_wulu(story, base_std))
    # Project complete Yumi data to prevent stale previous-week goodnight/garden.
    result.update(yumi_projection(story))
    return result


def reset_route_goodnights(story, native_std=None):
    """Call only after successful day commit, never on next-day window opening."""
    notices = []
    if yumi_projection(story)['ysg']:
        ensure_yumi(story)['ysg'] = False
        notices.append(('syncBaiyuInfos', {'d': yumi_projection(story)}))
    if _flag(story, 'wulu_special_goodnight'):
        body = _wulu(story, native_std)
        story['wulu_special_goodnight'] = False
        body['wsg'] = False
        notices.append(('syncWuluLineData', body))
    if _flag(story, 'jiaohui_special_goodnight'):
        story['jiaohui_special_goodnight'] = False
        notices.append(('syncJiaohuiSpecialNight', {'jsn': False}))
    if _flag(story, 'alanSpecialGoodNight'):
        story['alanSpecialGoodNight'] = False
        notices.append(('syncAlanSpecialNight', {'asn': False}))
    return notices


def route_goodnight_notices(story, names):
    """Replay current canonical values, never a stale previously-cleared flag."""
    result = []
    for name in names:
        if name == 'syncBaiyuInfos':
            body = {'d': yumi_projection(story)}
        elif name == 'syncWuluLineData':
            body = _wulu(story)
        elif name == 'syncJiaohuiSpecialNight':
            body = {'jsn': _flag(story, 'jiaohui_special_goodnight')}
        elif name == 'syncAlanSpecialNight':
            body = {'asn': _flag(story, 'alanSpecialGoodNight')}
        else:
            raise ValueError('Unknown route night synchronization')
        result.append((name, body))
    return result


def validate_route_agreements(story):
    """Pure validation for persisted canonical agreement state."""
    for name in _ROUTE_FLAGS: _flag(story, name)
    _wulu(story)
    yumi_projection(story)
