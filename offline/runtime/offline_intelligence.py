# -*- coding: ascii -*-
"""Finite original6004 intelligence13..18 transactions; no random generation.

One canonical story.intelligence. Constructors are original-table derived,
UUIDs are stable per actual source occurrence, and callers save before notices.
"""
import copy
import hashlib

INTELLIGENCE_POLICY = 'original-6004-assault-intelligence-v1'
_INTEL_AREAS = {13:3,14:4,15:5,16:6,17:7,18:8}
_INTEL_AFFECTS = {13:22,14:21,15:20,16:19,17:18,18:17}
try:
    _intel_text = (basestring,)
except NameError:
    _intel_text = (str,)


def _intel_uuid(value):
    return isinstance(value,_intel_text) and len(value)==24 and all(c in '0123456789abcdef' for c in value)


def validate_intelligence_story(story):
    data = story.get('intelligence')
    if data is None:
        return
    if not isinstance(data,dict) or not isinstance(data.get('is'),list) or type(data.get('rd')) is not bool:
        raise ValueError('Invalid original intelligence collection')
    seen = set()
    sources = story.get('intelligence_sources',{})
    for record in data['is']:
        uid = record.get('uuid')
        if (record.get('id') not in _INTEL_AREAS or not _intel_uuid(uid) or uid in seen or
                type(record.get('day')) is not int or type(record.get('ld')) is not int or
                any(type(record.get(key)) is not bool for key in ('op','hd','ep')) or
                record.get('hdd') is not None and type(record['hdd']) is not int or
                not isinstance(record.get('afs'),list) or not isinstance(sources.get(uid),dict)):
            raise ValueError('Invalid persisted original intelligence record/source')
        seen.add(uid)
        for affect in record['afs']:
            auid = affect.get('uuid')
            if (affect.get('id') != _INTEL_AFFECTS[record['id']] or not _intel_uuid(auid) or
                    auid in seen or type(affect.get('ld')) is not int or 'rd' not in affect):
                raise ValueError('Invalid original intelligence affect')
            seen.add(auid)


def intelligence_data(state):
    return copy.deepcopy(state.get('story',{}).get('intelligence',{'is':[],'rd':False}))


def intelligence_sync_notice(state):
    # RPC Dict('is') wraps the Data.initFromDict {'is':records,'rd':bool}.
    return ('syncAllIntelligence', {'is':intelligence_data(state)})


def native_intelligence_data(data):
    from common.IdManager import IdManager
    result = copy.deepcopy(data)
    for record in result.get('is',[]):
        if isinstance(record.get('uuid'),_intel_text):
            record['uuid'] = IdManager.str2id(record['uuid'])
        for affect in record.get('afs',[]):
            if isinstance(affect.get('uuid'),_intel_text):
                affect['uuid'] = IdManager.str2id(affect['uuid'])
    return result


def build_event_intelligence(story, event, ids, tables, occurrence, day):
    """Return canonical collection and provenance, without mutating the input."""
    if event != 6004 or not isinstance(ids,(list,tuple)) or any(i not in _INTEL_AREAS for i in ids):
        raise ValueError('Unsupported original intelligence source/IDs')
    if type(day) is not int or day < 0 or type(story.get('week')) is not int:
        raise ValueError('Missing original intelligence week/day')
    data = copy.deepcopy(story.get('intelligence',{'is':[],'rd':False}))
    sources = copy.deepcopy(story.get('intelligence_sources',{}))
    occupied = set(record['uuid'] for record in data['is'])
    for iid in ids:
        definition = tables.get('intelligence',{}).get(iid)
        if not definition or tuple(definition.get('handleAffects',())) != (_INTEL_AFFECTS[iid],):
            raise ValueError('Missing original assault intelligence definition')
        if any(definition.get(field) for field in ('createAffects','autoHandleAffects','notHandleAffects','expireAffects')):
            raise ValueError('Unimplemented original intelligence automatic effect')
        affect = tables.get('intelligence_affect',{}).get(_INTEL_AFFECTS[iid])
        if not affect or not affect.get('events') or any(not tables.get('event_content',{}).get(event,{}).get('release') for event in affect['events']):
            raise ValueError('Missing released original intelligence affect/event catalog')
        area = story.get('city_areas',{}).get(str(_INTEL_AREAS[iid]))
        if not area or len(area.get('st',[])) != 3 or not area['st'][1]:
            continue
        uid = hashlib.sha256(('intelligence:%s:%s'%(occurrence,iid)).encode('ascii')).hexdigest()[:24]
        source = {'event':event,'occurrence':str(occurrence),'week':story['week'],'day':day,'id':iid,'policy':INTELLIGENCE_POLICY}
        if uid in occupied:
            if sources.get(uid) != source:
                raise ValueError('Original intelligence source UUID collision')
            continue
        lifetime = definition.get('lastDay',1)
        if type(lifetime) is not int or lifetime < 1:
            raise ValueError('Invalid original intelligence lifetime')
        free = area['st'][0] == 0
        data['is'].append({'id':iid,'uuid':uid,'day':day,'hd':free,'hdd':day if free else None,
            'op':free or definition.get('openNeed',0)==0,'ld':lifetime,'ep':False,'afs':[]})
        sources[uid] = source
        occupied.add(uid)
        data['rd'] = False
    return data,sources


def _intel_auto_handle(state):
    changed = False
    day = state.get('day',{}).get('stock_day',state['story'].get('date',0))
    for record in state['story'].get('intelligence',{}).get('is',[]):
        area = state['story'].get('city_areas',{}).get(str(_INTEL_AREAS[record['id']]))
        if not record['hd'] and not record['ep'] and area and area.get('st',[None])[0] == 0:
            record.update(hd=True,hdd=day,op=True)
            changed = True
    return changed


def prepare_intelligence_operation(state, operation, arguments, tables):
    """Whole candidate, original notices, changed; no saves/native callbacks."""
    operations = ('syncAllIntelligenceRequest','readTodayIntelligence','openIntelligenceRequest','handleIntelligenceRequest')
    if operation not in operations:
        raise ValueError('Unsupported original intelligence RPC')
    candidate = copy.deepcopy(state)
    story = candidate['story']
    validate_intelligence_story(story)
    story.setdefault('intelligence',{'is':[],'rd':False})
    _intel_auto_handle(candidate)
    params = {key:value for key,value in arguments.items() if key != '_cbid_'}
    if operation in operations[:2]:
        if params:
            raise ValueError('Original intelligence sync/read takes no arguments')
        if operation == 'readTodayIntelligence':
            story['intelligence']['rd'] = True
            return candidate,[],candidate != state
        return candidate,[intelligence_sync_notice(candidate)],candidate != state
    if set(params) != set(('uuid',)) or not _intel_uuid(params['uuid']):
        raise ValueError('Invalid original intelligence UUID')
    record = next((r for r in story['intelligence']['is'] if r['uuid']==params['uuid']),None)
    if record is None:
        raise ValueError('No current original intelligence UUID')
    source = story.get('intelligence_sources',{}).get(record['uuid'],{})
    if source.get('event') != 6004 or source.get('week') != story.get('week') or 6004 not in candidate.get('completed_events',[]):
        raise ValueError('Intelligence lacks actually completed current-week source event')
    if record['ep'] or record['ld'] <= 0:
        raise ValueError('Original intelligence is expired')
    definition = tables.get('intelligence',{}).get(record['id'])
    if not definition:
        raise ValueError('Missing original intelligence cost definition')
    if operation == 'openIntelligenceRequest' and record['op'] or operation == 'handleIntelligenceRequest' and record['hd']:
        notices = [intelligence_sync_notice(candidate)] if candidate != state else []
        return candidate,notices,candidate != state
    if operation == 'handleIntelligenceRequest' and not record['op']:
        raise ValueError('Original intelligence has not been opened')
    cost = definition.get('openNeed' if operation=='openIntelligenceRequest' else 'handleNeed',0)
    city = story.get('city_values',{})
    if type(cost) is not int or cost < 0 or type(city.get('dvc')) is not int or city['dvc'] < cost:
        raise ValueError('Insufficient original spendable development dvc')
    city['dvc'] -= cost
    notices = []
    if operation == 'openIntelligenceRequest':
        record['op'] = True
        reply = ('openIntelligenceSuccess',{'uuid':record['uuid']})
    else:
        day = candidate.get('day',{}).get('stock_day',story.get('date'))
        if type(day) is not int:
            raise ValueError('Missing actual intelligence handling day')
        record.update(hd=True,hdd=day)
        available = dict(candidate.get('available_events',[]))
        events = []
        for aid in definition.get('handleAffects',()):
            if aid != _INTEL_AFFECTS[record['id']]:
                raise ValueError('Unsupported original intelligence affect kind')
            affect = tables.get('intelligence_affect',{}).get(aid)
            if not affect:
                raise ValueError('Missing original intelligence affect definition')
            auid = hashlib.sha256(('intelligence-affect:%s:%s'%(record['uuid'],aid)).encode('ascii')).hexdigest()[:24]
            lifetime = affect.get('expireTime',1)
            record['afs'].append({'id':aid,'uuid':auid,'ld':99999 if lifetime==-1 else lifetime,'rd':None})
            for event in affect.get('events',()):
                row = tables.get('event_content',{}).get(event)
                if not row or not row.get('release'):
                    raise ValueError('Missing released original intelligence event')
                if event in candidate.get('processing_events',[]) or event in candidate.get('completed_events',[]) and not row.get('repeatable'):
                    continue
                available[event] = 1
                story.setdefault('available_origins',{})[str(event)] = {
                    'source':'accepted_intelligence_handle','uuid':record['uuid'],'affect_uuid':auid,
                    'affect':aid,'week':story['week']}
                events.append(event)
        candidate['available_events'] = [[event,value]for event,value in sorted(available.items())]
        reply = ('handleIntelligenceSuccess',{'uuid':record['uuid']})
        notices.append(('pushEvents',{'a':copy.deepcopy(candidate['available_events']),'p':copy.deepcopy(candidate.get('processing_events',[]))}))
    city_notice = ('get_all_area_info_reply',{'ais':{'area_%s'%key:copy.deepcopy(area)for key,area in story.get('city_areas',{}).items()},'cd':copy.deepcopy(city),'sm':False})
    notices = [city_notice,intelligence_sync_notice(candidate)] + notices + [reply]
    if operation == 'handleIntelligenceRequest':
        notices.extend(('triggerIntelligenceEvents',{'e':event})for event in events)
    validate_intelligence_story(story)
    return candidate,notices,candidate != state


def advance_intelligence_day(state, source_day, target_day):
    """Exact original ld tick for this finite catalog; no ambient generation."""
    if target_day == source_day or not state['story'].get('intelligence',{}).get('is'):
        return []
    if type(source_day) is not int or target_day != source_day+1:
        raise ValueError('Original intelligence requires one actual next-day transition')
    validate_intelligence_story(state['story'])
    for record in state['story']['intelligence']['is']:
        record['ld'] -= 1
        if record['ld'] <= -1:
            record['ep'] = True
        for affect in record['afs']:
            affect['ld'] -= 1
    state['story']['intelligence']['rd'] = False
    _intel_auto_handle(state)
    return [intelligence_sync_notice(state)]
