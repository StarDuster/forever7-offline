# -*- coding: ascii -*-
"""Finite offline Yumi policy; original client wire projection, no UI completion.

Unknown server rules are explicit policy: one medicine per ten herbs, clamp,
accepted mission291 win settlement only. New-week story rebuild clears this state.
"""
import copy

YUMI_METHODS = ('makeYumiDrug', 'consumeYumiDrag')

def yumi_context(state):
    s = state.get('story', {})
    return (s.get('week'), str(s.get('route', '1')), s.get('route_generation', 0),
            tuple(state.get('week_protocol', {}).get('consumed_handoffs', [])))

def validate_yumi(story):
    y = story.get('yumi')
    if y is None: return
    if not isinstance(y, dict) or y.get('version') != 1: raise ValueError('Invalid Yumi state')
    for k in ('byv', 'ycn', 'byn', 'hyn'):
        if type(y.get(k)) is not int or y[k] < 0: raise ValueError('Invalid Yumi counter')
    if y['byv'] > 100: raise ValueError('Invalid Yumi value')
    for k in ('ysg', 'slm', 'ycyo'):
        if type(y.get(k)) is not bool: raise ValueError('Invalid Yumi flag')
    if not isinstance(y.get('receipts'), dict): raise ValueError('Invalid Yumi ledger')
    if story.get('baiyu_value') != y['byv']: raise ValueError('Yumi condition mirror mismatch')

def ensure_yumi(story):
    if 'yumi' not in story:
        v = story.get('baiyu_value', story.get('baiyuval', 50))
        if type(v) is not int or not 0 <= v <= 100: raise ValueError('Invalid legacy Yumi value')
        story['yumi'] = dict(version=1, byv=v, ysg=False, slm=False, ycyo=False,
                             ycn=0, byn=0, hyn=0, receipts={})
        story['baiyu_value'] = v
    validate_yumi(story)
    return story['yumi']

def yumi_projection(story):
    validate_yumi(story)
    legacy = story.get('baiyu_value', story.get('baiyuval', 50))
    if type(legacy) is not int or not 0 <= legacy <= 100:
        raise ValueError('Invalid legacy Yumi value')
    y = story.get('yumi') or dict(byv=legacy, ysg=False, slm=False, ycyo=False,ycn=0,byn=0,hyn=0)
    d = dict((k, y[k]) for k in ('byv','ysg','slm','ycyo','ycn','byn','hyn'))
    d['rt'] = str(story.get('route','1'))
    return d

def apply_yumi_event(story, event, row):
    delta = row.get('gainBaiyuVal')
    opening = row.get('special_agreement') == '2'
    if delta is None and not opening: return []
    if delta is not None and type(delta) is not int:
        raise ValueError('Unverified Yumi event producer')
    y = ensure_yumi(story)
    if delta is not None: y['byv'] = max(0,min(100,y['byv']+delta))
    if opening: y['ycyo'] = True
    story['baiyu_value'] = y['byv']
    return [('openYumiYaocaoyuan' if opening else 'syncBaiyuInfos', {'d':yumi_projection(story)})]

def prepare_yumi_operation(state, method, arguments, identity, context):
    candidate = copy.deepcopy(state)
    s = candidate['story']
    if method not in YUMI_METHODS or not identity: raise ValueError('Invalid Yumi request')
    if tuple(context) != yumi_context(state): raise ValueError('Stale Yumi route/week')
    t = arguments.get('t')
    if type(t) is not int or t not in (1,2): raise ValueError('Invalid original drug type')
    y = ensure_yumi(s)
    key = str(identity)
    signature = [method,t]
    if key in y['receipts']:
        receipt = y['receipts'][key]
        previous_signature = receipt.get('signature') if isinstance(receipt, dict) else receipt
        if previous_signature != signature: raise ValueError('Yumi receipt collision')
        if isinstance(receipt, dict): return candidate, copy.deepcopy(receipt['reply']), False
        # Legacy receipts did not retain the original transition; do not invent it.
        raise ValueError('Legacy Yumi receipt has no durable original reply')
    if str(s.get('route')) != '7' or not y['ycyo']: raise ValueError('Yumi facility unavailable')
    field = 'byn' if t == 1 else 'hyn'
    before = y['byv']
    if method == 'makeYumiDrug':
        if y['ycn'] < 10: raise ValueError('Insufficient herbs')
        y['ycn'] -= 10; y[field] += 1
    else:
        if y[field] < 1: raise ValueError('Insufficient medicine')
        y[field] -= 1; y['byv'] = max(0,min(100,before+(2 if t == 1 else -2)))
    s['baiyu_value'] = y['byv']
    reply = {'rs':True,'i':{'_type':t,'b':before,'d':yumi_projection(s)}}
    y['receipts'][key] = {'signature':signature, 'before':before, 'after':y['byv'], 'reply':copy.deepcopy(reply)}
    validate_yumi(s)
    return candidate, reply, True

def settle_yumi_herbs(previous, candidate, parameters, active):
    """Caller must already have accepted the actual battle result exactly once."""
    if parameters.get('s') != 291 or parameters.get('w') != 1: return []
    if not active or active.get('request',{}).get('s') != 291: raise ValueError('Missing real garden battle')
    count = (parameters.get('e') or {}).get('yaocao_num')
    if type(count) is not int or count < 0: raise ValueError('Invalid actual herb count')
    y = ensure_yumi(candidate['story'])
    key = 'battle:'+str(active['fight_id'])
    if key in y['receipts']: raise ValueError('Garden fight already settled')
    y['ycn'] += count; y['receipts'][key] = ['battle291',count]
    return [('syncBaiyuInfos', {'d':yumi_projection(candidate['story'])})]
