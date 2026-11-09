# -*- coding: ascii -*-
"""Original opening dialogue/option lifecycle; unsupported effects stay pending."""
import copy
import re
try:
    from offline_action_ledger import set_event_baseline
except ImportError:
    pass
try:
    from offline_conditions import evaluate_offline_condition
except ImportError:
    pass
try:
    _story_text_types = (basestring,)
except NameError:
    _story_text_types = (str,)

OPENING_STORY_EVENTS = (1000, 1006, 1015, 1016, 1017, 1018, 1019, 8, 1001, 1002, 1004,
                        1021, 1038, 1039, 1040, 1043, 10000, 1007, 1008, 1041, 1009, 1022, 1010)


def story_city_snapshot(story):
    # CityData.initFromDict assigns areas directly. Its getter requires the
    # original area_N keys, not integer IDs or their JSON string equivalents.
    city = {'dv': 0, 'av': 0, 'bf': 0, 'fv': 0, 'ev': 0, 'rv': 0}
    city.update(copy.deepcopy(story.get('city_values', {})))
    city['areas'] = {'area_%d' % int(key): copy.deepcopy(area)
                     for key, area in story.get('city_areas', {}).items()}
    return city


def story_reward_snapshot(story):
    return {'bc': [(int(bid), camp) for bid, camp in sorted(story.get('blackcores', {}).items())]}


def story_week_snapshot(story, day):
    review = day.get('review') or {'c': {}, 'l': {}}
    return {'w': story.get('week', 0), 'd': day.get('stock_day', 0),
            'c': copy.deepcopy(review['c']), 'l': copy.deepcopy(review['l'])}


def initial_story_state(completed=()):
    state = {'version': 1, 'emergency': True, 'week': 0, 'date': 0,
            'notes': {'p': {}, 'n': {}, 'pn': [], 'ppn': False},
            'starter_hero': None, 'starter_source': None,
            'route': '1', 'sub_routes': [],
            'wuluClue': [], 'wuluClueReaded': False, 'wuluDetailReaded': [],
            'daily_wish':[], 'daily_wish_hero':0, 'daily_wish_read':False, 'daily_wish_generation':0,
            'battle_wins': [], 'blackcores': {},
            'reward_receipts': [], 'pending_effects': {}, 'city_areas': {},
            'initial_action_budget':{'version':1,'policy':'offline-first-city-budget-v1',
                'status':'pending','source':'fresh-offline-world'}}
    if 1000 in completed:
        state['notes']['pn'], state['notes']['ppn'] = [10044], True
    if 8 in completed:
        state['emergency'] = False
    return state


def evaluate_story_condition(kind, value, state, selected_starter_only=False):
    return evaluate_offline_condition(kind, value, state,
        context={'selected_starter_only': selected_starter_only})


def story_trigger_eligible(row, state, selected_starter_only=False):
    if not row.get('release'):
        return False
    return all(evaluate_story_condition(kind, value, state, selected_starter_only) is True
               for kind, value in row.get('conds', {}).items())


def refresh_opening_triggers(state, triggers):
    available = dict(state['available_events'])
    branch_map = {1038: 8, 1039: 7, 1040: 37}
    facts = set(state['completed_events']) | set(state['processing_events'])
    restored = [hero for event, hero in branch_map.items() if event in facts]
    if len(restored) > 1:
        raise ValueError('Conflicting original starter branch history')
    if restored and state['story'].get('starter_hero') not in (None, restored[0]):
        raise ValueError('Starter selection conflicts with original history')
    if restored and state['story'].get('starter_hero') is None:
        state['story']['starter_hero'], state['story']['starter_source'] = restored[0], 'original-event-history'
    for event, hero in branch_map.items():
        if hero != state['story'].get('starter_hero'):
            available.pop(event, None)
    for event in OPENING_STORY_EVENTS:
        if event in available or event in state['processing_events'] or event in state['completed_events']:
            continue
        if event in triggers and story_trigger_eligible(triggers[event], state, event in branch_map):
            available[event] = 1
    state['available_events'] = [[event, value] for event, value in sorted(available.items())]


def prepare_opening_story(state, operation, arguments, content, triggers, rewards):
    candidate = copy.deepcopy(state)
    candidate.setdefault('story', initial_story_state())
    notices = []
    pending = candidate['story']['pending_effects']
    available = dict(candidate['available_events'])
    processing, completed = set(candidate['processing_events']), set(candidate['completed_events'])
    traces = {event: {key: set(values) for key, values in trace} for event, trace in candidate['event_traces']}

    def complete(event):
        row = content[event]
        known = set(('areaFight', 'autoStart', 'client_event', 'completeConds',
            'completeEnterMainPanel', 'dialog', 'emergencyEvent', 'eventType', 'events',
            'isAutoTriggerEvent', 'isEmergencyEvent', 'isLeaveEmergencyEvent', 'name',
            'newbee', 'newbee_event', 'contentFinishBattle', 'mutexEvent', 'notepadId',
            'priority', 'release', 'repeatable', 'rewards', 'ui', 'changeBlackcore'))
        if set(row) - known:
            pending[str(event)] = {'unsupported_fields': sorted(set(row) - known)}
            return False
        if row.get('ui'):
            expected = ('settlement_fullscreen', 'notify_area_event', '1', '2')
            if event != 10000 or tuple(row['ui']) != expected:
                pending[str(event)] = {'unsupported_ui': list(row['ui'])}
                return False
            if operation != 'ui_complete':
                pending[str(event)] = {'waiting': 'original-ui-callback', 'ui': list(row['ui'])}
                return False
            if 101 not in candidate['story'].get('battle_wins', []) or not candidate['story'].get('first_clearance_applied'):
                return False
        blackcores = row.get('changeBlackcore', {})
        if (not isinstance(blackcores, dict) or any(str(bid) != '1' or type(camp) is not int or camp != 1
                                                   for bid, camp in blackcores.items())):
            pending[str(event)] = {'unsupported_blackcore': copy.deepcopy(blackcores)}
            return False
        if row.get('areaFight'):
            if tuple(row['areaFight']) != (1,):
                pending[str(event)] = {'areaFight': list(row['areaFight'])}
                return False
            area = {'id': 1, 'st': [1, False, False], 'lv': 1, 'bd': {},
                    'stage': {'cs': 101, 'sl': [[101]]}}
        else:
            area = None
        reward_result = {}
        for reward_id in row.get('rewards', ()):
            reward = rewards.get(reward_id)
            if not reward or set(reward) - set(('id', 'hero', 'tradeType', 'award_pool')):
                pending[str(event)] = {'reward': reward_id}
                return False
            for hero_id in reward.get('hero', ()):
                if str(hero_id) not in (candidate.get('profile') or {}).get('heroes', {}):
                    pending[str(event)] = {'missing_hero': hero_id}
                    return False
            reward_result.setdefault('hero', []).extend(reward.get('hero', ()))
        if any(note != 10044 for note in row.get('notepadId', ())):
            pending[str(event)] = {'notepadId': list(row['notepadId'])}
            return False
        if area is not None:
            candidate['story'].setdefault('city_areas', {})['1'] = area
            notices.append(('get_area_info_reply', {'ai': copy.deepcopy(area)}))
        if row.get('notepadId'):
            notes = candidate['story']['notes']
            for note in row['notepadId']:
                if note not in notes['pn']:
                    notes['pn'].append(note)
                    notes['ppn'] = True
            notices.append(('syncAllNote', {'nd': copy.deepcopy(notes)}))
        if row.get('isLeaveEmergencyEvent'):
            candidate['story']['emergency'] = False
        for bid, camp in sorted(blackcores.items()):
            candidate['story'].setdefault('blackcores', {})[str(bid)] = camp
            notices.append(('updateBlackCore', {'c': camp, 'b': int(bid)}))
        processing.discard(event)
        completed.add(event)
        baseline = globals().get('set_event_baseline')
        if baseline is not None and type(candidate['story'].get('week')) is int:
            baseline(candidate, event, candidate['story']['week'])
        if event == 1021:
            pending.pop('successors-after-1004', None)
        if event == 1004:
            for child in row.get('events', ()):
                available[child] = 1
            pending['successors-after-1004'] = {'events': list(row.get('events', ()))}
        pending.pop(str(event), None)
        if reward_result and event not in candidate['story']['reward_receipts']:
            candidate['story']['reward_receipts'].append(event)
            notices.append(('completeEventReplyStart', {'e': event, 'r': reward_result}))
        notices.append(('completeEventReplyEnd', {'e': event}))
        return True

    if operation == 'external':
        event = arguments.get('e')
        row = content.get(event, {})
        accepted = (event == 20030 and row.get('release') and row.get('client_event') == 1
                    and not row.get('dialog') and not row.get('completeConds')
                    and 20029 not in processing and 20029 not in completed)
        if accepted:
            available.pop(event, None)
            processing.discard(event)
            if event not in completed:
                completed.add(event)
            notices.append(('triggerExternalEventReply', {}))
            notices.append(('pushEvents', {'a': list(sorted(available.items())), 'p': sorted(processing)}))
        else:
            # This dedicated business reply releases the original triggerEvent
            # lock even when the requested external event is unsupported.
            notices.append(('triggerExternalEventReply', {}))
    elif operation in ('trace', 'combat_win'):
        key, value = arguments['k'], arguments['d'].get('c')
        if key == 'battle' and operation != 'combat_win':
            return candidate, notices
        for event in sorted(processing):
            if event not in OPENING_STORY_EVENTS:
                continue
            trace = traces.setdefault(event, {})
            if value is not None:
                trace.setdefault(key, set()).add(value)
            requirements = content[event].get('completeConds', {})
            satisfied = bool(requirements) and all(set(values).issubset(trace.get(kind, set()))
                                                   for kind, values in requirements.items())
            if satisfied and not content[event].get('events'):
                complete(event)
    elif operation == 'option':
        parent, selected = arguments.get('e'), arguments.get('se')
        if (parent not in OPENING_STORY_EVENTS or parent not in processing or
                selected not in content[parent].get('events', ()) or
                selected not in OPENING_STORY_EVENTS):
            raise ValueError('Invalid original opening option')
        # Selection is the original authenticated dialogue option action. Some
        # original options bypass dialog traces via selectedEvent/reliableEcho.
        if not complete(parent):
            return candidate, notices
        for sibling in content[parent].get('events', ()):
            available.pop(sibling, None)
        completed.discard(selected)  # The original 1018 conversation can loop.
        processing.add(selected)
        available.pop(selected, None)
        traces.pop(selected, None)
        notices.append(('startEventReply', {'e': selected, 'r': 1}))
        if not content[selected].get('completeConds') and not content[selected].get('dialog'):
            complete(selected)
    elif operation == 'ui_complete':
        event = arguments.get('e')
        if event == 10000 and event in processing:
            complete(event)
        elif event != 10000 or event not in completed:
            raise ValueError('No matching original liberation UI is processing')
    elif operation == 'start':
        event = arguments['e']
        if event in OPENING_STORY_EVENTS and event in processing:
            row = content[event]
            if not row.get('dialog') and not row.get('completeConds'):
                complete(event)
    else:
        raise ValueError('Unknown opening story operation')
    candidate['available_events'] = [[event, value] for event, value in sorted(available.items())]
    candidate['processing_events'], candidate['completed_events'] = sorted(processing), sorted(completed)
    candidate['event_traces'] = [[event, [[key, sorted(values)] for key, values in sorted(trace.items())]]
                                 for event, trace in sorted(traces.items())]
    refresh_opening_triggers(candidate, triggers)
    return candidate, notices


def install_story_ui_compatibility():
    """Let the original touch handler finish before its callback destroys it."""
    from cocos.comps.dialogue_common.choose import Comp
    if getattr(Comp, '_f7_deferred_story_choice', False):
        return
    original = Comp.set_click_cb

    def set_deferred_click(self, callback):
        if callback is None:
            return original(self, None)
        queued = [False]

        def deferred(*args, **kwargs):
            if queued[0]:
                return
            queued[0] = True

            def run(callback_args=args, callback_kwargs=kwargs):
                queued[0] = False
                return callback(*callback_args, **callback_kwargs)
            import gg
            gg.exec_delay(1, run)
        return original(self, deferred)

    Comp.set_click_cb = set_deferred_click
    Comp._f7_deferred_story_choice = True


def prepare_starter_choice(state, hero_id, triggers):
    if hero_id not in (7, 8, 37) or 1021 not in state['completed_events']:
        raise ValueError('Starter dialogue choice is not available')
    candidate = copy.deepcopy(state)
    chosen = candidate['story'].get('starter_hero')
    if chosen is not None and chosen != hero_id:
        raise ValueError('Original starter branch is already selected')
    if str(hero_id) not in (candidate.get('profile') or {}).get('heroes', {}):
        raise ValueError('Starter branch requires an owned hero')
    candidate['story']['starter_hero'] = hero_id
    candidate['story']['starter_source'] = 'player-choice'
    refresh_opening_triggers(candidate, triggers)
    return candidate


def offer_story_starter_choice(proxy, manual=False):
    """Reuse the original hero picker for an explicit offline story decision."""
    if (1021 not in proxy.completed_events or proxy.story.get('starter_hero') is not None
            or getattr(proxy, '_starter_offer_pending', False)):
        return
    if getattr(proxy, '_starter_initial_offered', False) and not manual:
        install_story_continue_entry(proxy)
        return
    proxy._starter_offer_pending = True

    def show():
        import gg
        import com.const as const
        if proxy.owner is None or gg.avatar is not proxy.owner:
            proxy._starter_offer_pending = False
            return
        if proxy.story.get('starter_hero') is not None:
            proxy._starter_offer_pending = False
            return
        if gg.logic.game_state.current != const.GameState.CITY or gg.ui._dialogue:
            proxy.defer(100, guarded_show)
            return
        from cocos.panels.card_hero_choose import UILogic, UIConfig
        install_story_continue_entry(proxy)

        class StoryChoiceLogic(UILogic):
            @classmethod
            def get_select_heroes(cls, panel):
                return [7, 8, 37]

            @classmethod
            def on_click_done(cls, panel):
                selected = panel.choose_heroes[0]
                if selected in (7, 8, 37) and proxy.confirm_story_starter(selected):
                    panel.notify_close()

        class StoryChoiceConfig(UIConfig):
            @classmethod
            def get_choose_config(cls, panel):
                return {'visible': (('popup.bottom.txt', False),
                        ('popup.bottom.name', False), ('popup.bottom.btn_lastpage', False),
                        ('popup.bottom.btn_nextpage', False), ('popup.bottom.btn_done', True)),
                    'text': (('popup.text', u'\u9009\u62e9\u5f00\u573a\u5267\u60c5\u7684\u540c\u884c\u8005\uff0c\u51b3\u5b9a\u63a5\u4e0b\u6765\u7684\u5bf9\u8bdd'),)}
        panel = gg.ui.panels.card_hero_choose
        if not panel.valid:
            parent = gg.ui.panels.city
            layer = parent.add_layer(panel)
            parent.proc_event('show', _children=True, _layer=layer,
                choose_heroes=[0], choose_order=[1], callback=None,
                ui_logic=StoryChoiceLogic, ui_config=StoryChoiceConfig)
            proxy._starter_initial_offered = True
        proxy._starter_offer_pending = False
    def guarded_show():
        try:
            return show()
        except Exception:
            proxy._starter_offer_pending = False
            raise
    proxy.defer(100, guarded_show)


def install_story_continue_entry(proxy):
    """A nonmodal city entry remains after cancelling the original picker."""
    import gg
    import cocosui as cc
    import com.const as const
    if gg.logic.game_state.current != const.GameState.CITY:
        return
    parent = gg.ui.panels.city
    if not parent.valid:
        return
    if getattr(parent, '_f7_story_entry_node', None) is parent._node:
        button = parent._f7_story_entry
    else:
        button = cc.ccui.Button.create()
        button.setTitleText(u'\u7ee7\u7eed\u5f00\u573a\u5267\u60c5')
        button.setTitleFontSize(24)
        button.ignoreContentAdaptWithSize(False)
        button.setContentSize(cc.cc.Size(230, 64))
        button.setPosition(cc.cc.Vec2(130, 100))
        button.setTouchEnabled(True)

        def on_continue(sender, event):
            if event == cc.ccui.TOUCH_EVENT_ENDED and proxy.owner is gg.avatar:
                offer_story_starter_choice(proxy, manual=True)
        button.addTouchEventListener(on_continue)
        parent._node.addChild(button, 100)
        parent._f7_story_entry_node, parent._f7_story_entry = parent._node, button
    button.setVisible(proxy.story.get('starter_hero') is None)


def scan_nextday_story_events(state, content, triggers, prospective_unknown=False):
    """Fresh current-route pre-day scan; known false prunes unknown elsewhere.

    Ordinary optional availability is not a day blocker. Actual in-flight
    events and reachable NEXTDAY client-operation rows are evaluated afresh.
    """
    candidate = copy.deepcopy(state)
    blockers = []
    processing = set(candidate.get('processing_events', []))
    completed = set(candidate.get('completed_events', []))
    available = dict(candidate.get('available_events', []))
    if processing:
        blockers.append({'processing_events': sorted(processing)})
    if (candidate.get('battle') or {}).get('active'):
        blockers.append({'active_battle': True})
    if candidate.get('story', {}).get('emergency'):
        blockers.append({'emergency': True})
    pending = candidate.get('story', {}).get('pending_effects', {})
    blocking_pending = [key for key in pending if key.isdigit() and
        (int(key) in processing or (int(key) in available and
         (content.get(int(key), {}).get('newbee') or content.get(int(key), {}).get('isAutoTriggerEvent'))))]
    if blocking_pending:
        blockers.append({'pending_effects': sorted(blocking_pending)})
    for event in sorted(available):
        row = content.get(event)
        if row is None:
            blockers.append({'event': event, 'reason': 'missing-original-content'})
        elif row.get('newbee') or row.get('isAutoTriggerEvent'):
            blockers.append({'event': event, 'reason': 'available-mandatory-event'})
    evaluation = copy.deepcopy(candidate) if prospective_unknown else candidate
    if prospective_unknown:
        facts = dict(evaluation.get('conditions', []))
        facts[102] = merge_client_operations(facts.get(102), 4)
        evaluation['conditions'] = sorted(facts.items())
    for event, trigger in sorted(triggers.items()):
        conditions = trigger.get('conds', {})
        if not trigger.get('release') or 102 not in conditions or event in processing or event in completed:
            continue
        results = {kind: evaluate_story_condition(kind, value, evaluation)
                   for kind, value in conditions.items()}
        if any(value is False for value in results.values()):
            if not prospective_unknown:
                available.pop(event, None)
            continue
        unknown = sorted(kind for kind, value in results.items() if value is None)
        if unknown:
            blockers.append({'event': event, 'reason': 'unknown-reachable-nextday-condition', 'conditions': unknown})
            continue
        if prospective_unknown:
            continue
        row = content.get(event)
        if not row or not row.get('release'):
            if row is None:
                blockers.append({'event': event, 'reason': 'missing-nextday-content'})
            continue
        available[event] = 1
        if row.get('isAutoTriggerEvent') or row.get('newbee'):
            blockers.append({'event': event, 'reason': 'eligible-nextday-event'})
    candidate['available_events'] = [[event, value] for event, value in sorted(available.items())]
    return candidate, blockers


def merge_client_operations(previous, incoming):
    """Original CLIENTOP AllSet facts accumulate; payload may be one scalar."""
    def values(raw):
        if raw is None:
            return set()
        if type(raw) is int:
            return set((raw,))
        if isinstance(raw, (list, tuple, set)) and all(type(item) is int for item in raw):
            return set(raw)
        raise ValueError('Unsupported original CLIENTOP value')
    merged = sorted(values(previous) | values(incoming))
    return merged[0] if len(merged) == 1 else merged


def show_day_pending_notice(proxy, reason):
    import gg
    if proxy.owner is None or getattr(gg, 'avatar', None) is not proxy.owner or gg.ui._dialogue:
        return
    panel = gg.ui.panels.common_confirm
    if panel.valid and panel.visible:
        return
    if reason == 'local-save-failed':
        text = u'\u8fdb\u5ea6\u4fdd\u5b58\u5931\u8d25\uff0c\u65e5\u671f\u672a\u63a8\u8fdb\u3002\u8bf7\u7a0d\u540e\u91cd\u8bd5\u3002'
    else:
        text = u'\u8fd8\u6709\u5f85\u5904\u7406\u7684\u5267\u60c5\u3001\u884c\u52a8\u6216\u6761\u4ef6\uff0c\u65e5\u671f\u672a\u63a8\u8fdb\u3002'
    panel.notify_get(text)
