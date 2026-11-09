# -*- coding: ascii -*-
"""First battle clearance and the original liberation-UI completion boundary."""
import copy
import hashlib
import json
try:
    from offline_story import story_city_snapshot
except ImportError:
    pass  # Embedded runtime already defines this helper in its shared globals.


INITIAL_CITY_BUDGET_POLICY = 'offline-first-city-budget-v1'


def prepare_initial_city_budget(state):
    """One-time explicit offline budget after actual first101 clearance.

    Old zero-placeholder migration is restricted to this project's pristine
    bootstrap chronology. Contrary/bounded-away histories never justify refill.
    Date, events, victories and action-spend ledgers are never manufactured.
    """
    candidate = copy.deepcopy(state)
    story = candidate.get('story',{})
    day = candidate.get('day',{})
    diagnostic = {'policy':INITIAL_CITY_BUDGET_POLICY,'status':'not-eligible','reasons':[]}
    marker = story.get('initial_action_budget')
    if marker is not None and not (isinstance(marker,dict) and marker.get('version')==1 and
            marker.get('policy')==INITIAL_CITY_BUDGET_POLICY and marker.get('status')=='pending' and marker.get('source')=='fresh-offline-world'):
        diagnostic['status']='already-marked'
        return candidate,False,diagnostic
    if candidate.get('scenario') != 'opening-development-v1':
        diagnostic['reasons'].append('not-known-project-save-scenario')
    if story.get('week') != 0 or day.get('stock_day') != 0 or story.get('date') != 0:
        diagnostic['reasons'].append('not-initial-week-day')
    receipts = candidate.get('battle',{}).get('receipts',[])
    first = [r for r in receipts if r.get('reply',{}).get('t')==1 and r.get('reply',{}).get('s')==101 and r.get('reply',{}).get('w')==1 and r.get('fight_id')]
    if not first or not story.get('first_clearance_applied') or 101 not in story.get('battle_wins',[]):
        diagnostic['reasons'].append('no-actual-first101-clearance-receipt')
    city = story.get('city_values',{})
    available = city.get('av')
    if type(available) is not int or available < 0:
        diagnostic['reasons'].append('missing-or-invalid-authoritative-actions')
    if diagnostic['reasons']:
        return candidate,False,diagnostic
    if available > 0:
        story['initial_action_budget']={'version':1,'policy':INITIAL_CITY_BUDGET_POLICY,
            'status':'preserved-existing','granted':0,'old_av':available,'new_av':available,
            'week':0,'day':0,'source':'observed-existing-positive-budget','first_fight_id':first[-1]['fight_id']}
        diagnostic['status']='preserved-existing'
        return candidate,True,diagnostic
    if type(day.get('actions_spent')) is not int or day['actions_spent'] != 0:
        diagnostic['reasons'].append('missing-or-nonzero-day-action-ledger')
    if type(story.get('week_actions_spent')) is not int or story['week_actions_spent'] != 0:
        diagnostic['reasons'].append('missing-or-nonzero-week-action-ledger')
    if story.get('action_ledger_source') != 'observed-local-transactions-v1':
        diagnostic['reasons'].append('unknown-action-ledger-provenance')
    actions = candidate.get('city_actions')
    if not isinstance(actions,dict) or actions.get('version') != 1 or actions.get('receipts') or actions.get('patrol'):
        diagnostic['reasons'].append('city-action-history-or-patrol-present')
    if candidate.get('battle',{}).get('active'):
        diagnostic['reasons'].append('actual-battle-still-active')
    if any(r.get('reply',{}).get('t')!=1 or r.get('reply',{}).get('s')!=101 for r in receipts):
        diagnostic['reasons'].append('non101-battle-receipt-present')
    if set(story.get('battle_wins',[])) != set((101,)):
        diagnostic['reasons'].append('non101-victory-present')
    if any(scene != 101 for scene in story.get('current_mission_wins',[])) or story.get('condition_mission_roots') or story.get('mission_reset_receipts'):
        diagnostic['reasons'].append('subsequent-mission-progress-present')
    if any(day.get(key) is not None for key in ('receipt','intent','review')):
        diagnostic['reasons'].append('day-transition-evidence-present')
    if day.get('previous_values') is not None or story.get('date') != 0:
        diagnostic['reasons'].append('prior-day-values-present')
    week = candidate.get('week_protocol')
    if not isinstance(week,dict) or week.get('history') or week.get('transition') or week.get('result') or week.get('awaiting_avatar'):
        diagnostic['reasons'].append('week-transition-history-present')
    areas = story.get('city_areas',{})
    if set(areas) != set(('1','2')) or areas.get('1',{}).get('st',[None])[0]!=0 or areas.get('2',{}).get('st',[None])[0]!=1 or areas.get('2',{}).get('stage',{}).get('cs')!=1101:
        diagnostic['reasons'].append('not-pristine-first-clearance-city')
    if any(area.get('bd') or area.get('dbd') or area.get('lv')!=1 or len(area.get('st',[]))!=3 or area['st'][1:]!=[False,False] for area in areas.values()):
        diagnostic['reasons'].append('city-development-building-or-lock-evidence-present')
    if story.get('patrol_pending') or story.get('patrol_reward_pending'):
        diagnostic['reasons'].append('patrol-pending')
    if diagnostic['reasons']:
        return candidate,False,diagnostic
    proof = first[-1]
    digest = hashlib.sha256(json.dumps(proof,sort_keys=True,separators=(',',':')).encode('ascii')).hexdigest()
    story['initial_action_budget']={'version':1,'policy':INITIAL_CITY_BUDGET_POLICY,
        'status':'activated','amount':24,'granted':24,'old_av':0,'new_av':24,'week':0,'day':0,
        'source':'fresh-first-clearance' if marker else 'known-pristine-bootstrap-zero-placeholder',
        'first_fight_id':proof['fight_id'],'first_receipt_sha256':digest,
        'evidence':{'scenario':candidate['scenario'],'day_actions_spent':0,'week_actions_spent':0,
            'city_receipts':0,'battle_receipts':len(receipts),'wins':[101],
            'original_limit':'CityData.REC_ACTION_VAL=24','not_official101_reward':True}}
    city['av']=24
    diagnostic['status']='activated'
    return candidate,True,diagnostic


def apply_first_battle_clearance(state, mission_catalog):
    candidate = copy.deepcopy(state)
    story = candidate['story']
    actual_win = any(receipt.get('reply', {}).get('t') == 1 and
                     receipt.get('reply', {}).get('s') == 101 and
                     receipt.get('reply', {}).get('w') == 1
                     for receipt in candidate.get('battle', {}).get('receipts', []))
    if not actual_win and 101 not in story.get('battle_wins', []):
        return candidate, [], False
    if story.get('first_clearance_applied'):
        return candidate, [], False
    mission = mission_catalog.get(101, {})
    next_mission = mission_catalog.get(1101, {})
    if 1101 not in mission.get('nextstagenums', ()) or next_mission.get('ch') != 2:
        raise ValueError('Original first-clearance mission link changed')
    areas = story['city_areas']
    if '1' not in areas:
        raise ValueError('Accepted battle receipt has no admitted area')
    wins = story.setdefault('battle_wins', [])
    if 101 not in wins:
        wins.append(101)
        wins.sort()
    # Explicit first-clearance policy: accepted actual101win frees its area and
    # unlocks the next mission in its own area. Never put1101 in area1's stage.
    if areas['1']['st'][0] in (0, 1):
        areas['1']['st'][0] = 0
    if '2' not in areas:
        areas['2'] = {'id': 2, 'st': [1, False, False], 'lv': 1, 'bd': {},
                      'stage': {'cs': 1101, 'sl': [[1101]]}}
    story['first_clearance_applied'] = True
    candidate,budget_changed,budget_diagnostic = prepare_initial_city_budget(candidate)
    story = candidate['story']
    areas = story['city_areas']
    changed = candidate != state
    notices = []
    if areas != state['story']['city_areas'] or budget_changed:
        city = story_city_snapshot(story)
        values = city.pop('areas')
        # Let event10000's actual stock UI announce the change once. The
        # ordinary single-area callback would auto-play a duplicate animation.
        notices.append(('get_all_area_info_reply', {'ais': values, 'cd': city, 'sm': False}))
    return candidate, notices, changed


def install_postbattle_ui_completion():
    from entity.ClientAvatar import ClientAvatar
    if getattr(ClientAvatar, '_f7_postbattle_ui_completion', False):
        return
    original = ClientAvatar.startMovie

    def after_original_ui(self, event):
        result = original(self, event)
        if event == 10000:
            proxy = getattr(self, 'server', None)
            if proxy is not None and callable(getattr(proxy, 'complete_story_ui', None)):
                # startMovie is reached by the original notify_area_event cb,
                # after the player really finishes its settlement UI. Preserve
                # that continuation before scheduling the durable completion.
                proxy.defer(1, lambda: proxy.complete_story_ui(event))
        return result
    ClientAvatar.startMovie = after_original_ui
    ClientAvatar._f7_postbattle_ui_completion = True
