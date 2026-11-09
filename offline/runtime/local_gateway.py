# -*- coding: utf-8 -*-
"""In-process gateway prototype, executed only inside the game's Python 2.7 VM.

Uses the actual ClientAccount/ClientAvatar classes and their snapshot loaders.
Unknown RPCs are logged for implementation; they are never reported as success.
"""
try:
    from offline_role_mission import (ROLE_MISSION_POLICY, compile_role_mission,
        role_mission_tables, validate_role_descriptor, bind_role_admission,
        role_battle_source, settle_role_loss, finalize_role_failure,
        prepare_role_giveup, prepare_role_rearm, validate_role_missions, native_role_combat_data, offer_paused_role_resume)
except ImportError:
    pass

try:
    from offline_chapter_campaign import (resolve_normal_chapter, refresh_normal_chapters,
        normal_chapter_token, validate_normal_chapters, expire_normal_chapters,
        revoke_normal_chapter_projection, stage_projection_owner)
except ImportError:
    pass

try:
    from offline_daerweila import (compile_daerweila_dispatch, validate_daerweila_state,
        daerweila_request_source, daerweila_source_matches, daerweila_occurrence_matches,
        daerweila_queued_operation_matches, prepare_daerweila_first_choice,
        bind_daerweila_occurrence, apply_daerweila_event, project_daerweila,
        daerweila_sync_notices, publish_daerweila_award, expire_daerweila_dispatch,
        prepare_daerweila_patrol_baseline, mint_daerweila_patrol_offers,
        prepare_daerweila_patrol_delivery, filter_daerweila_availability)
except ImportError:
    pass

try:
    from offline_special_city_stage import (apply_special_city_stage_effects,
        validate_special_city_stages, special_city_stage_token,
        refresh_special_city_stages, expire_special_city_stages)
except ImportError:
    pass

try:
    from offline_city_stage_provider import (original_city_stage_family,
        record_city_stage_occurrence, refresh_city_stage_provider,
        city_stage_provider_admission, validate_city_stage_source,
        finish_city_stage_provider, validate_city_stage_provider,
        expire_city_stage_provider, city_stage_provider_token)
except ImportError:
    pass

try:
    from offline_flashback import (flashback_context, flashback_token, flashback_data,
        flashback_notice, flashback_require_action, flashback_spend_action,
        flashback_accept_entry, flashback_route_handoff, prepare_flashback_operation,
        validate_flashback_state)
except ImportError:
    pass

try:
    from offline_huisu import (huisu_context, huisu_token, validate_huisu_state,
        project_huisu, huisu_notice, huisu_std_projection, huisu_route_projection, validate_huisu_document, huisu_request_source,
        city_action_context, dream_action_token, authorize_action_admission,
        commit_action_admission, event_execution_admission,
        resolve_event_execution_context, check_dream_contract,
        huisu_trigger_permitted, accept_huisu_event_completion,
        prepare_huisu_operation, mark_huisu_nextday, huisu_day_guard,
        reset_huisu_on_committed_day_or_week)
except ImportError:
    pass

try:
    from offline_native_story_callbacks import install_native_story_callbacks
except ImportError:
    pass

import copy
import json
import os
import sys
import time
import traceback
try:
    from offline_yumi import (YUMI_METHODS, validate_yumi, yumi_context, yumi_projection,
        prepare_yumi_operation, settle_yumi_herbs)
    from offline_route_agreements import validate_route_agreements
except ImportError:
    pass
try:
    from offline_item_exchange import ITEM_EXCHANGE_METHODS, prepare_item_exchange, validate_item_exchange, item_exchange_limits
except ImportError:
    pass
try:
    from offline_rpc_rejections import prepare_rpc_rejection, RPC_LOCAL_REJECTION_LOCKS, RPC_MISSING_CALLBACK_LOCKS, RPC_LOCAL_REJECTION_OPERATIONS, cleanup_rpc_rejection, ending_request_context_matches, install_ending_request_guard, install_puzzle_refusal_guard, capture_puzzle_rejection, puzzle_rejection_can_deliver, finish_puzzle_rejection
except ImportError:
    pass
try:
    from offline_transport import (AuthorizedEventStartDelivery, acquire_ui_lock_lease,
        ui_lock_lease_state, complete_ui_lock_lease, deliver_ui_lock_reply)
except ImportError:
    pass
try:
    from offline_gacha_pools import (validate_gacha_pools_state, prepare_pool, open_pool_cards,
        quit_pool, direct_pool_draw, pool_file_view, pool_opened_total)
    from offline_gacha_gateway import migrate_gateway_gacha_state, original_pool_config, gacha_snapshot_projection, gacha_economy_projection
    from offline_gacha_rewards import make_original_gacha_resolver, make_table_hero_result, apply_original_gacha_rewards
    from offline_gacha_costs import install_gacha_dedicated_costs
    from offline_gacha_archive import install_gacha_archive, offline_archive_context
    from offline_gacha_special import (SPECIAL_GACHA_OPERATIONS, prepare_special_gacha_operation, special_pool_context, validate_special_gacha_state, original_self_choose_hash, prepare_treasure_wish_reveal, TREASURE_WISH_REVEAL_POLICY, prepare_jiaozhi_context, finalize_jiaozhi_reveal, advance_gacha_shadow, grant_original_pendant, gacha_pending_for_client, prepare_gacha_activity_bonuses, hero_wish_period_for_group, prepare_hero_wish_reveal, finalize_hero_wish_reveal, HERO_WISH_PERIOD_POLICY, hero_wish_eligibility_view)
except ImportError:
    pass

try:
    from offline_intelligence import (prepare_intelligence_operation, native_intelligence_data,
        intelligence_sync_notice, validate_intelligence_story)
    from offline_postbattle import prepare_initial_city_budget
except ImportError:
    pass

if 'daily_wish_notice' not in globals():
    from offline_event_effects import (daily_wish_notice, daily_wish_token, validate_daily_wish,
        prepare_daily_wish_read, daily_choice_token, prepare_daily_wish_choice, daily_wish_choice_committed)

try:
    _f7_text_types = (basestring,)
except NameError:
    _f7_text_types = (str,)


try:
    from offline_battle_terminal import validate_event_terminal_state
except ImportError:
    pass

try:
    from offline_action_ledger import record_committed_spend, invalidate_action_ledger
except ImportError:
    pass


def validate_gateway_progress(state):
    validate_event_terminal_state(state)
    validate_daerweila_state(state)
    validate_special_city_stages(state)
    validate_normal_chapters(state)
    validate_role_missions(state)
    validate_item_exchange(state)
    if not isinstance(state, dict) or state.get('scenario') != 'opening-development-v1':
        raise ValueError('Unknown local progress scenario; existing save preserved')
    name = state.get('player_name')
    if name is not None and (not isinstance(name, _f7_text_types) or not 0 < len(name) <= 8):
        raise ValueError('Invalid saved player name')
    groups = []
    for key in ('available_events', 'processing_events', 'completed_events'):
        values = state[key]
        if not isinstance(values, list):
            raise ValueError('Invalid saved event list')
        if key == 'available_events' and any(not isinstance(entry, list) or len(entry) != 2 for entry in values):
            raise ValueError('Invalid available event records')
        ids = [entry[0] for entry in values] if key == 'available_events' else values
        if any(type(event) is not int or event <= 0 for event in ids):
            raise ValueError('Invalid saved event IDs')
        if len(ids) != len(set(ids)):
            raise ValueError('Duplicate saved event IDs')
        groups.append(set(ids))
    if any(groups[i] & groups[j] for i, j in ((0, 1), (0, 2), (1, 2))):
        raise ValueError('Conflicting event states')
    if not isinstance(state['conditions'], list) or not isinstance(state['event_traces'], list):
        raise ValueError('Invalid progress containers')
    validate_hero_profile(state.get('profile'))
    economy = (state.get('profile') or {}).get('economy')
    if economy is not None and (not isinstance(economy, dict) or economy.get('version') != 1 or
            any(type(economy.get(key)) is not int or economy[key] < 0 for key in ('money', 'exp', 'level')) or
            economy['level'] < 1):
        raise ValueError('Invalid persistent battle economy')
    if state.get('profile') and 'treasures' in state['profile']:
        validate_treasure_inventory(state['profile']['treasures'])
    if 'story' in state:
        story = state['story']
        validate_daily_wish(story)
        validate_yumi(story)
        validate_route_agreements(story)
        validate_city_stage_provider(state)
        if story.get('daily_wish_hero',0) and str(story['daily_wish_hero']) not in (state.get('profile')or{}).get('heroes',{}):
            raise ValueError('Daily wish hero is not owned')
        if not isinstance(story, dict) or story.get('version') != 1:
            raise ValueError('Unsupported opening story version')
        if (type(story.get('emergency')) is not bool or
                type(story.get('week')) is not int or type(story.get('date')) is not int or
                not isinstance(story.get('reward_receipts'), list) or
                any(type(event) is not int for event in story['reward_receipts']) or
                not isinstance(story.get('pending_effects'), dict) or
                not isinstance(story.get('city_areas'), dict)):
            raise ValueError('Invalid opening story state')
        validate_flashback_state(story.get('route35_flashback'))
        validate_huisu_document(state)
        if 'huisu_generation' in story and (type(story['huisu_generation']) is not int or story['huisu_generation'] < 0):
            raise ValueError('Invalid huisu generation')
        if 'event_contexts' in story and not isinstance(story['event_contexts'], dict):
            raise ValueError('Invalid persisted event execution lineage')
        if story.get('starter_hero') not in (None, 7, 8, 37):
            raise ValueError('Invalid selected opening starter')
        if 'route' in story and (not isinstance(story['route'], _f7_text_types) or not story['route']):
            raise ValueError('Invalid original story route')
        if 'city_values' in story and (not isinstance(story['city_values'], dict) or
                'areas' in story['city_values'] or
                any(type(story['city_values'].get(key)) is not int for key in ('dv', 'av', 'bf', 'fv', 'ev', 'rv'))):
            raise ValueError('Invalid authoritative city values')
        if (not isinstance(story.get('battle_wins', []), list) or
                any(type(stage) is not int for stage in story.get('battle_wins', [])) or
                not isinstance(story.get('blackcores', {}), dict) or
                any(not bid.isdigit() or type(camp) is not int for bid, camp in story.get('blackcores', {}).items()) or
                type(story.get('first_clearance_applied', False)) is not bool or
                (story.get('first_clearance_applied') and 101 not in story.get('battle_wins', []))):
            raise ValueError('Invalid post-battle story state')
        notes = story.get('notes')
        if (not isinstance(notes, dict) or not isinstance(notes.get('p'), dict) or
                not isinstance(notes.get('n'), dict) or not isinstance(notes.get('pn'), list) or
                any(type(note) is not int for note in notes['pn']) or type(notes.get('ppn')) is not bool):
            raise ValueError('Invalid opening notepad state')
        for area_id, area in story['city_areas'].items():
            if (not isinstance(area, dict) or str(area.get('id')) != area_id or
                    not isinstance(area.get('st'), list) or len(area['st']) != 3 or
                    not isinstance(area.get('bd'), dict) or
                    ('stage' in area and (not isinstance(area['stage'], dict) or
                     not isinstance(area['stage'].get('sl'), list) or type(area['stage'].get('cs')) is not int))):
                raise ValueError('Invalid opening city area')
    validate_gacha_state(state.get('gacha'))
    validate_intelligence_story(state.get('story',{}))
    if state.get('gacha_pools') is not None:
        validate_gacha_pools_state(state['gacha_pools'])
        validate_special_gacha_state(state)
    if 'battle' in state:
        if not isinstance(state['battle'], dict):
            raise ValueError('Missing persistent battle container')
        validate_battle_state(state['battle'])
    if 'day' in state:
        validate_day_state(state['day'])
    if 'city_actions' in state:
        validate_city_actions_state(state['city_actions'])
    if 'week_protocol' in state:
        validate_week_state(state['week_protocol'])
    for pair in state['conditions']:
        if not isinstance(pair, list) or len(pair) != 2 or type(pair[0]) is not int:
            raise ValueError('Invalid saved client condition')
    for pair in state['event_traces']:
        if not isinstance(pair, list) or len(pair) != 2 or type(pair[0]) is not int or not isinstance(pair[1], list):
            raise ValueError('Invalid saved event trace')
        for trace in pair[1]:
            if (not isinstance(trace, list) or len(trace) != 2 or
                    not isinstance(trace[0], _f7_text_types) or not isinstance(trace[1], list) or
                    any(not isinstance(value, _f7_text_types) and type(value) is not int for value in trace[1])):
                raise ValueError('Invalid saved trace values')


class SnapshotDict(dict):
    """Recover required initial fields from the client's own class defaults.

This is development instrumentation. The resulting schema is persisted for
review and must be made explicit before declaring gameplay compatibility.
"""

    def get(self, key, default=None):
        if key in self:
            return dict.__getitem__(self, key)
        if isinstance(default, dict):
            default = SnapshotDict(default)
        value = copy.deepcopy(default)
        self[key] = value
        return value

    def __missing__(self, key):
        frame = sys._getframe(1)
        obj = frame.f_locals.get('self')
        code = frame.f_code.co_code
        position = frame.f_lasti + 1
        attribute = None
        # NeoX LOAD_FAST(self), STORE_ATTR(name) after a subscription.
        if position + 6 <= len(code) and ord(code[position]) == 97 and ord(code[position + 3]) == 132:
            name_index = ord(code[position + 4]) | (ord(code[position + 5]) << 8)
            attribute = frame.f_code.co_names[name_index]
        if attribute and hasattr(obj, attribute):
            value = copy.deepcopy(getattr(obj, attribute))
        else:
            value = SnapshotDict()
        if isinstance(value, dict) and not isinstance(value, SnapshotDict):
            value = SnapshotDict(value)
        self[key] = value
        _f7_log('snapshot default %s.%s key=%r attr=%r type=%s' % (
            obj.__class__.__name__ if obj else '?', frame.f_code.co_name, key, attribute, type(value).__name__))
        return value


class LocalGateAddress(object):
    # Original GateData.recommand_addr is read by cutils.dctool_log even
    # during offline PVE. Keep the object shape, without opening a socket.
    def recommand_addr(self):
        return ('127.0.0.1', 18767)


class LocalRegion(object):
    region_name = 'Offline'
    gate_cur = LocalGateAddress()

    def gate_next(self):
        return self.gate_cur.recommand_addr()


class LocalWorld(object):
    host_id = 1
    server_id = 1
    server_name = 'Offline'
    region_name = 'Offline'
    server_state = 1
    region = LocalRegion()


class LocalProxy(object):
    _f7_puzzle_refusal_gateway = True
    def __init__(self, logic, owner, persistent=False):
        self.logic = logic
        import hashlib
        self._item_exchange_session = hashlib.sha256(os.urandom(32)).hexdigest()
        self._item_exchange_clock = time.time
        self.owner = owner
        self.status = None
        self.conditions = {}
        self.available_events = {1000: 1}
        self.processing_events = set()
        self.completed_events = set()
        self.event_traces = {}
        self._started_this_session = set()
        self._pending_event_starts = {}
        self._event_start_callback_receipts = set()
        self.player_name = None
        self.profile = None
        self.gacha = None
        self.gacha_pools = None
        self.story = initial_story_state()
        # Explicit local bootstrap admission; no original predecessor is
        # fabricated. Saved documents replace this marker during restore.
        self.story['available_origins'] = {'1000': {'source': 'offline-initial-seed',
            'policy': 'offline-fresh-entry-seed-v1', 'context': [0, 0, '1'],
            'bootstrap_predecessor': 6}}
        self.battle = initial_battle_state()
        self.day = initial_day_state()
        self.city_actions = initial_city_actions_state()
        self.week_protocol = initial_week_state()
        self.tutorial_log = []
        self._store = None
        self._saved_progress = self.progress_snapshot()
        if persistent:
            self._store = OfflineSaveStore(os.path.join(_f7_doc, 'offline_progress.json'), validate_gateway_progress)
            saved = self._store.load()
            if saved is not None:
                self.restore_progress(saved)
                self._saved_progress = copy.deepcopy(saved)
                _f7_log('Loaded local progress revision %s; recovered=%s' % (
                    self._store.revision, self._store.recovered))
            else:
                self.save_progress()

    def progress_snapshot(self):
        return {'scenario': 'opening-development-v1', 'player_name': self.player_name,
                'profile': copy.deepcopy(self.profile),
                'gacha': copy.deepcopy(self.gacha),
                'gacha_pools': copy.deepcopy(self.gacha_pools),
                'story': copy.deepcopy(self.story),
                'battle': copy.deepcopy(self.battle),
                'day': copy.deepcopy(self.day),
                'city_actions': copy.deepcopy(self.city_actions),
                'week_protocol': copy.deepcopy(self.week_protocol),
                'status': self.status, 'available_events': [list(item) for item in sorted(self.available_events.items())],
                'processing_events': sorted(self.processing_events),
                'completed_events': sorted(self.completed_events),
                'conditions': [[key, value] for key, value in sorted(self.conditions.items())],
                'event_traces': [[event, [[key, sorted(values)] for key, values in sorted(trace.items())]]
                                 for event, trace in sorted(self.event_traces.items())]}

    def restore_progress(self, state):
        validate_gateway_progress(state)
        self.gacha = copy.deepcopy(state.get('gacha'))
        self.gacha_pools = copy.deepcopy(state.get('gacha_pools'))
        self.battle = copy.deepcopy(state.get('battle', initial_battle_state()))
        self.day = copy.deepcopy(state.get('day', initial_day_state()))
        self.city_actions = copy.deepcopy(state.get('city_actions', initial_city_actions_state()))
        self.week_protocol = copy.deepcopy(state.get('week_protocol', initial_week_state()))
        self.story = copy.deepcopy(state.get('story', initial_story_state(state.get('completed_events', ()))))
        self.player_name, self.status = state['player_name'], state['status']
        self.profile = copy.deepcopy(state.get('profile'))
        self.available_events = dict(state['available_events'])
        self.processing_events = set(state['processing_events'])
        self.completed_events = set(state['completed_events'])
        self.conditions = dict(state['conditions'])
        self.event_traces = {event: {key: set(values) for key, values in trace}
                             for event, trace in state['event_traces']}

    def save_progress(self):
        state = self.progress_snapshot()
        try:
            if self._store is not None:
                self._store.write(state)
        except Exception:
            self.restore_progress(copy.deepcopy(self._saved_progress))
            _f7_log('Local progress write failed; state rolled back: %s' % traceback.format_exc())
            raise
        self._saved_progress = copy.deepcopy(state)

    def cancel_pending_calls(self):
        for delivery in self._pending_event_starts.values():
            delivery.close()
        self._pending_event_starts.clear()
        scheduler = getattr(self, '_rpc_scheduler', None)
        if scheduler is not None:
            scheduler.close()

    def destroy(self):
        self.cancel_pending_calls()
        self.owner = None

    def defer(self, delay, callback):
        import gg
        if self.owner is not None:
            schedule_local_rpc(self, gg, delay, callback)

    def call_server_method(self, name, parameters=None, entityid=None):
        import gg
        _f7_log('RPC %s %r' % (name, parameters))
        if name == 'login':
            self.cancel_pending_calls()

            def enter_avatar():
                self.cancel_pending_calls()
                create_avatar(self.logic)
            self.defer(1, enter_avatar)
        elif name == 'combatOfflineFinish':
            source_owner = self.owner
            source_role = role_battle_source(self.progress_snapshot())
            parameters = copy.deepcopy(parameters)
            source_fight = getattr(getattr(self.owner, 'combatData', None), 'fight_id', None)
            self.defer(1, lambda: self.handle_battle_finish(parameters, source_fight, source_owner, source_role))
        elif name == 'combatOfflineHeroSwitch':
            self.defer(1, lambda: self.handle_battle_hero_switch(parameters))
        elif name == 'combatOfflineHeroConfirm':
            self.defer(1, lambda: self.confirm_battle_hero(parameters))
        elif name in ('combatOfflineReset', 'combatRoomLeaveFromClient'):
            source_fight = getattr(getattr(self.owner, 'combatData', None), 'fight_id', None)
            self.defer(1, lambda: self.reset_pending_battle(source_fight))
        elif name == 'battleRealFailWithEventMode':
            source_owner = self.owner
            source = role_battle_source(self.progress_snapshot())
            arguments = copy.deepcopy(parameters or {})
            self.defer(1, lambda: self.handle_role_giveup(arguments, source, source_owner))
        elif name == 'daerweilaFirstChooseAsazile':
            dispatch_source = daerweila_request_source(self.progress_snapshot())
            source_owner = self.owner
            arguments = copy.deepcopy(parameters or {})
            self.defer(1, lambda: self.handle_daerweila_first_choice(arguments, dispatch_source, source_owner))
        elif name == 'requestStoryhuisuOut':
            token = huisu_token(self.progress_snapshot())
            source_owner = self.owner
            self.defer(1, lambda: self.process_huisu_operation(name, parameters or {}, token, source_owner=source_owner))
        elif name == 'requestFlashbackIncDay':
            token = flashback_token(self.progress_snapshot())
            source_owner = self.owner
            self.defer(1, lambda: self.process_flashback_operation(name, parameters or {}, token,
                source_owner=source_owner))
        elif name in ('incDayWhenNoActionVal', 'clearCurDailySettlement'):
            week = getattr(getattr(self.owner, 'weeknumData', None), 'weeknum', None)
            day = getattr(getattr(self.owner, 'weeknumData', None), 'daynum', None)
            self.defer(1, lambda: self.process_day_operation(name, parameters or {}, source_context=(week, day)))
        elif name in YUMI_METHODS:
            arguments = copy.deepcopy(parameters or {})
            source = self.yumi_request_source(name, arguments)
            self.defer(1, lambda: self.handle_yumi(name, arguments, source['identity'], source))
        elif name == 'readDailyWish':
            token=daily_wish_token(self.story);source_owner=self.owner
            self.defer(1,lambda:self.handle_daily_wish_read(parameters or {},token,source_owner))
        elif name in ('areaBuildRequest', 'areaLevelUpRequest', 'enterPatrolRequest', 'patrolReward'):
            serial = getattr(self, '_direct_city_sequence', 0) + 1
            self._direct_city_sequence = serial
            identity = self.city_operation_id('direct:%s' % serial)
            source_context = (self.owner, dream_action_token(self.progress_snapshot()))
            self.defer(1, lambda: self.handle_city_action(name, parameters or {}, identity,
                source_context=source_context))
        elif name in ('handleIncWeekAsk', 'handleResetWeekAsk', 'handleResetWeek',
                       'requestEnterStory', 'requestEnterStoryByEnding', 'updateClientAvatarAsk'):
            source_week = self.story.get('week')
            self.defer(1, lambda: self.process_week_operation(name, parameters or {}, source_week=source_week))
        elif name == 'heartbeatServer':
            self.defer(1, lambda: self.reply('on_heartbeat', {}))
        elif name == 'reliableRpcCall':
            request_name = (parameters.get('w') or {}).get('m')
            dedicated = request_name in ('requestLuckyDrawFriendCard', 'requestLuckyDrawNewFriendCard',
                'requestLuckyDrawFriendLianChouCard', 'requestLuckyDrawNewFriendLianChouCard',
                'requestLuckyDrawFurnitureCard', 'requestLuckyDrawFurnitureLianchouCard')
            gacha_scoped = request_name in SPECIAL_GACHA_OPERATIONS or dedicated
            scoped_request = gacha_scoped or request_name in YUMI_METHODS or request_name in ('startEvent','startEventOption','clientTraceProcessingEvent')
            if scoped_request:
                parameters = copy.deepcopy(parameters)
            source_operation = self.gacha_operation_source(request_name, (parameters.get('w') or {}).get('p') or {},
                parameters.get('_cbid_'), 'reliable:%s' % (parameters.get('w') or {}).get('r')) if gacha_scoped else None
            yumi_source = self.yumi_request_source(request_name, (parameters.get('w') or {}).get('p') or {},
                'reliable:%s' % (parameters.get('w') or {}).get('r'), parameters.get('_cbid_')) if request_name in YUMI_METHODS else None
            token = flashback_token(self.progress_snapshot())
            huisu_source = (huisu_request_source(self.progress_snapshot()) if request_name == 'requestStoryhuisu' else huisu_token(self.progress_snapshot()))
            action_source = dream_action_token(self.progress_snapshot())
            source_owner = self.owner
            provider_source = (city_stage_provider_token(self.progress_snapshot()), special_city_stage_token(self.progress_snapshot()), normal_chapter_token(self.progress_snapshot()))
            daily_token = daily_choice_token(self.progress_snapshot()) if (parameters.get('w')or{}).get('m')=='dailyPureChooseHero' else None
            gacha_source = self.gacha_presentation_token(((parameters.get('w')or{}).get('p')or{}).get('t',1)) if (parameters.get('w')or{}).get('m') in ('requestLuckyDrawFile','requestLuckyDrawFileAndOpenAll','requestLuckyDrawAllLeftCard') else None
            trace_source = {'week': self.story.get('week', 0),
                'occurrences': copy.deepcopy(self.story.get('event_occurrences', {}))} if request_name == 'clientTraceProcessingEvent' else None
            dispatch_source = daerweila_request_source(self.progress_snapshot())
            role_source = role_battle_source(self.progress_snapshot())
            self.defer(1, lambda: self.reliable_call(parameters, token, source_owner, daily_token, gacha_source, source_operation, yumi_source, huisu_source, action_source, provider_source, trace_source, dispatch_source, role_source))
        elif name in ITEM_EXCHANGE_METHODS:
            source_owner = self.owner
            self.defer(1, lambda: self.handle_item_exchange(name, parameters or {}, source_owner=source_owner))
        elif name == 'finishAxiliyaNewbee':
            source_owner = self.owner
            self.defer(1, lambda: self.handle_axiliya_tutorial(parameters or {}, source_owner))
        elif name in SPECIAL_GACHA_OPERATIONS:
            arguments = copy.deepcopy(parameters or {})
            source_operation = self.gacha_operation_source(name, arguments, arguments.get('_cbid_'))
            self.defer(1, lambda: self.handle_special_gacha(name, arguments, None, arguments.get('_cbid_'), source_operation))
        elif name == 'setPlayerName':
            self.defer(1, lambda: self.set_player_name(parameters))
        elif name == 'getAreaStagesRequest':
            self.defer(1, lambda: self.reply_area_stages(parameters))
        elif name in ('getAreaInfoRequest', 'getAllAreaInfoRequest'):
            self.defer(1, lambda: self.reply_city_areas(name, parameters))
        elif name in ('syncAllIntelligenceRequest','readTodayIntelligence','openIntelligenceRequest','handleIntelligenceRequest'):
            self.defer(1, lambda: self.handle_intelligence(name, parameters or {}))
        elif name in ('equipTreasureBatch', 'unequipTreasure', 'unequipAllTreasure'):
            self.defer(1, lambda: self.handle_treasure_equipment(name, parameters))
        elif name == 'changeAwakeSkinStyle':
            self.defer(1, lambda: self.change_awake_skin_style(parameters))
        elif name == 'setSkinRequest':
            self.defer(1, lambda: self.set_skin(parameters))
        elif name in ('requestLuckyDrawFriendCard', 'requestLuckyDrawNewFriendCard',
                       'requestLuckyDrawFriendLianChouCard', 'requestLuckyDrawNewFriendLianChouCard',
                       'requestLuckyDrawFurnitureCard', 'requestLuckyDrawFurnitureLianchouCard'):
            arguments = copy.deepcopy(parameters or {})
            source_operation = self.gacha_operation_source(name, arguments, arguments.get('_cbid_'))
            self.defer(1, lambda: self.handle_dedicated_gacha(name, arguments, source_operation=source_operation))
        elif name == 'requestCheckLuckyDrawFurnitureOpen':
            self.defer(1, lambda: self.reply('serverCallbackCarrier', {'_r_': True}, (parameters or {}).get('_cbid_')))
        elif name in ('requestFile', 'requestLuckyDrawCard', 'requestQuitFile'):
            presentation = self.gacha_presentation_token((parameters or {}).get('t',1))
            self.defer(1, lambda: self.handle_gacha(name, parameters, source_presentation=presentation))
        elif name == 'checkGamePlaySwitchAsk':
            import com.const as const
            game_play = parameters.get('g')
            import com.data.cdata.chouka_info as configured_draws
            card_panel = gg.ui.panels.card_tab
            selected = getattr(card_panel, 'draw_type', None)
            legal_pool = selected != 354 and (selected == 99 or selected in configured_draws.data)
            enabled = (game_play == const.GamePlayName.SUMMON or
                       (game_play == const.GamePlayName.FRIENDSUMMON and legal_pool))
            self.defer(1, lambda: self.reply('checkGamePlaySwitchReply', {
                'g': parameters['g'], 's': int(enabled),
                'm': '' if enabled else u'\u6b64\u529f\u80fd\u5c1a\u672a\u63a5\u5165\u79bb\u7ebf\u7248'}))
        elif name in ('tutorialBegin', 'tutorialEnd'):
            self.tutorial_log.append((name, parameters))
        elif name == 'queryEventOptAsk':
            self.defer(1, lambda: self.reply('queryEventOptReply', {'e': parameters['e'], 'd': []}))
        else:
            callback_id = parameters.get('_cbid_') if isinstance(parameters, dict) else None
            if not self.reject_unimplemented_rpc(name, parameters, callback_id, defer=True):
                _f7_log('RPC UNIMPLEMENTED %s' % name)

    def handle_axiliya_tutorial(self, parameters, source_owner):
        import gg
        if self.owner is not source_owner or getattr(gg, 'avatar', None) is not source_owner:
            return
        previous = self.progress_snapshot()
        saved = (previous.get('gacha') or {}).get('axiliya_tutorial_stage', 0)
        try:
            stage = parameters.get('sg')
            # Original city_axiliya supports versions 1/2; it reports completion,
            # not rewards or dialogue advancement. Preserve monotonic replay.
            if set(parameters) != set(['sg']) or type(stage) is not int or stage not in (1, 2):
                raise ValueError('Invalid original Axiliya tutorial version')
            if stage > saved:
                candidate = copy.deepcopy(previous)
                if candidate.get('gacha') is None:
                    candidate['gacha'] = new_gacha_state()
                candidate['gacha']['axiliya_tutorial_stage'] = stage
                self.restore_progress(candidate)
                self.save_progress()
                saved = stage
        except Exception:
            self.restore_progress(previous)
            source_owner.luckyDrawData.newbee_axiliya_finish_stage = saved
            gg.ui.panels.common_message.notify_message(
                u'\u5f15\u5bfc\u8fdb\u5ea6\u672a\u4fdd\u5b58\uff0c\u8bf7\u91cd\u8bd5')
            _f7_log('LOCAL AXILIYA tutorial not saved: %s' % traceback.format_exc())
            return
        source_owner.luckyDrawData.newbee_axiliya_finish_stage = saved

    def reject_unimplemented_rpc(self, name, parameters, callback_id=None, defer=False, source_owner=None):
        rejection = prepare_rpc_rejection(name, parameters, callback_id)
        local_lock = RPC_LOCAL_REJECTION_LOCKS.get(name)
        missing_callback_lock = RPC_MISSING_CALLBACK_LOCKS.get(name) if not callback_id else None
        local_only = name in RPC_LOCAL_REJECTION_OPERATIONS
        if rejection is None and local_lock is None and missing_callback_lock is None and not local_only:
            return False
        if source_owner is None:
            source_owner = self.owner
        import gg
        source_ui = getattr(gg, 'ui', None)
        source_locks = getattr(source_ui, '_lock', None)
        source_canteen = getattr(getattr(source_ui, 'panels', None), 'city_canteen', None)
        source_callbacks = getattr(gg, 'avatar_callback_map', None)
        source_callback = source_callbacks.get(callback_id) if isinstance(source_callbacks, dict) else None
        puzzle_context = capture_puzzle_rejection(source_owner, self, parameters) if name == 'puzzleRoomGetClue' else None
        ending_context = None
        if name == 'requestTriggerEventByEnding':
            ending_context = getattr(source_owner, '_f7_ending_request_context', None)
            if ending_context is not None:
                ending_context['dispatched'] = True

        def deliver():
            import gg
            if (source_owner is None or self.owner is not source_owner or
                    getattr(gg, 'avatar', source_owner) is not source_owner):
                return
            # Original reset_lock replaces this dictionary. Its previous waits
            # no longer exist; a late negative must not consume a new wait.
            if (getattr(gg, 'ui', None) is not source_ui or
                    isinstance(source_locks, dict) and getattr(source_ui, '_lock', None) is not source_locks):
                if (source_callback is not None and getattr(gg, 'avatar_callback_map', None) is source_callbacks and
                        source_callbacks.get(callback_id) is source_callback):
                    source_callbacks.pop(callback_id, None)
                    getattr(gg, 'avatar_callback_need_result', {}).pop(callback_id, None)
                return
            if (source_callback is not None and
                    (getattr(gg, 'avatar_callback_map', None) is not source_callbacks or
                     source_callbacks.get(callback_id) is not source_callback)):
                return
            if (name == 'requestTriggerEventByEnding' and ending_context is not None and
                    not ending_request_context_matches(source_owner, ending_context)):
                return
            if not puzzle_rejection_can_deliver(puzzle_context):
                return
            if local_only:
                # These callbacks have success-only UI effects; retire only the
                # exact captured callback instead of running it on a refusal.
                if (source_callback is not None and getattr(gg, 'avatar_callback_map', None) is source_callbacks and
                        source_callbacks.get(callback_id) is source_callback):
                    source_callbacks.pop(callback_id, None)
                    getattr(gg, 'avatar_callback_need_result', {}).pop(callback_id, None)
                if (name == 'canteenRequest' and source_canteen is not None and
                        getattr(getattr(source_ui, 'panels', None), 'city_canteen', None) is source_canteen):
                    source_canteen.cover = False
            cleanup_rpc_rejection(source_owner, name, callback_id if source_callback is not None else None, ending_context)
            if local_lock is not None or rejection is None:
                if local_lock is not None:
                    gg.ui.unlock(local_lock)
                if self.owner is source_owner and getattr(gg, 'avatar', source_owner) is source_owner:
                    gg.ui.panels.common_message.notify_message(
                        u'\u6b64\u529f\u80fd\u5c1a\u672a\u63a5\u5165\u79bb\u7ebf\u7248\uff0c'
                        u'\u672c\u6b21\u8bf7\u6c42\u672a\u6267\u884c')
                return
            reply, body, message = rejection
            # Preserve the exact callback field, including nonstandard falsy IDs;
            # the original decorator alone decides whether a callback is queued.
            if callback_id is not None:
                body = dict(body, _cbid_=callback_id)
            if puzzle_context is not None:
                puzzle_context['delivered'] = True
                source_ui._f7_puzzle_delivery_wait = puzzle_context['wait']
            try:
                self.reply(reply, body)
            finally:
                if puzzle_context is not None:
                    delattr(source_ui, '_f7_puzzle_delivery_wait')
            finish_puzzle_rejection(puzzle_context)
            if self.owner is source_owner and getattr(gg, 'avatar', source_owner) is source_owner:
                gg.ui.panels.common_message.notify_message(message)
        if defer:
            self.defer(1, deliver)
        else:
            deliver()
        return True

    def reply(self, name, parameters, callback_id=None):
        if name == 'offlineDaerweilaAward':
            publish_daerweila_award(self, parameters)
            return
        if name == 'startEventReply' and parameters.get('r') and parameters.get('e') in self.processing_events:
            owner = self.owner
            data = getattr(owner,'eventTriggerData',None)
            client = getattr(data,'processingEventsClient',None)
            # Original native avatar supplies this set. Minimal host/protocol
            # owners without native event data keep their direct reply behavior.
            if client is not None and hasattr(client,'__contains__'):
                import gg
                event = parameters['e']
                occurrence = story_occurrence_key({'story':self.story},event)
                avatar = getattr(gg,'avatar',None)
                key = (event,occurrence)
                if key in self._pending_event_starts:
                    if callback_id:
                        self._pending_event_starts[key].callback_ids.add(callback_id)
                    return
                def current():
                    return (self.owner is owner and getattr(gg,'avatar',None) is avatar and avatar is owner and
                        getattr(owner,'eventTriggerData',None) is data and event in self.processing_events and event not in self.completed_events and
                        story_occurrence_key({'story':self.story},event)==occurrence)
                def accepted():
                    return event in data.processingEventsClient
                def ready():
                    return bool(getattr(getattr(gg,'logic',None),'event_valid',False))
                def finish(was_accepted):
                    self._pending_event_starts.pop(key,None)
                    if was_accepted:
                        self._started_this_session.add(event)
                    elif delivery.emitted:
                        _f7_log('Original event start not accepted after ready delivery: event=%s occurrence=%s; awaiting explicit client retry' % (event,occurrence))
                    if delivery.emitted and callback_id:
                        self._event_start_callback_receipts.add((key,callback_id))
                    for waiting_id in sorted(delivery.callback_ids,key=repr):
                        if self.owner is not owner or getattr(gg,'avatar',None) is not avatar or avatar is not owner:
                            break
                        identity = (key,waiting_id)
                        if identity not in self._event_start_callback_receipts:
                            self._event_start_callback_receipts.add(identity)
                            self._immediate_reply('serverCallbackCarrier',{'_r_':{}},waiting_id)
                def emit():
                    primary = callback_id if callback_id and (key,callback_id) not in self._event_start_callback_receipts else None
                    if primary:
                        self._event_start_callback_receipts.add((key,primary))
                    self._immediate_reply(name,parameters,primary)
                delivery = AuthorizedEventStartDelivery(self.defer,current,ready,accepted,emit,finish)
                delivery.callback_ids = set([callback_id]) if callback_id else set()
                self._pending_event_starts[key] = delivery
                delivery.attempt()
                return
        self._immediate_reply(name,parameters,callback_id)

    def _immediate_reply(self, name, parameters, callback_id=None):
        try:
            if name == 'updateItems':
                parameters = dict(parameters, i=self.native_treasure_items(parameters['i']))
            if name in ('get_all_area_info_reply', 'get_area_info_reply'):
                parameters = native_city_reply(name, parameters)
            if name == 'syncAllIntelligence':
                parameters = dict(parameters)
                parameters['is'] = native_intelligence_data(parameters['is'])
            if name in ('handleIntelligenceSuccess','openIntelligenceSuccess'):
                from common.IdManager import IdManager
                parameters = dict(parameters,uuid=IdManager.str2id(parameters['uuid']))
            if callback_id:
                parameters = dict(parameters, _cbid_=callback_id)
            # CLIENT_STUB decorators accept the serialized argument dictionary,
            # even when the underlying Python function takes no arguments.
            getattr(self.owner, name)(parameters)
        except:
            _f7_log('Reply %s failed: %s' % (name, traceback.format_exc()))
            traceback.print_exc()

    def set_player_name(self, parameters):
        name = parameters['n']
        valid = isinstance(name, _f7_text_types) and 0 < len(name) <= 8
        if valid:
            self.player_name = name
            self.save_progress()
            self.owner.name = name
        self.reply('setPlayerNameReply', {'r': valid, 'in': bool(parameters.get('in'))})
        if valid:
            # The stock reply restores the optimistic local name; apply the
            # authoritative saved name after the callback has finished.
            self.owner.name = name

    def reliable_call(self, parameters, source_flashback_token=None, source_owner=None, source_daily_choice=None, source_gacha_presentation=None, source_gacha_operation=None, source_yumi_context=None, source_huisu_token=None, source_action_token=None, source_city_stage_token=None, source_story_trace=None, source_daerweila=None, source_role=None):
        rejection_owner = self.owner
        if source_owner is not None and source_owner is not self.owner:
            if isinstance(source_yumi_context, dict):
                self.finish_yumi_source(source_yumi_context, source_yumi_context.get('saved', False))
            return
        wrapper = parameters['w']
        name = wrapper['m']
        arguments = wrapper.get('p') or {}
        callback_id = parameters.get('_cbid_')
        if name in YUMI_METHODS and source_yumi_context is None:
            source_yumi_context = self.yumi_request_source(name, arguments, 'reliable:%s' % wrapper['r'], callback_id)
        if source_gacha_operation is None and (name in SPECIAL_GACHA_OPERATIONS or name in (
                'requestLuckyDrawFriendCard', 'requestLuckyDrawNewFriendCard',
                'requestLuckyDrawFriendLianChouCard', 'requestLuckyDrawNewFriendLianChouCard',
                'requestLuckyDrawFurnitureCard', 'requestLuckyDrawFurnitureLianchouCard')):
            source_gacha_operation = self.gacha_operation_source(name, arguments, callback_id, 'reliable:%s' % wrapper['r'])
        if (source_owner is not None and name in ('startEvent', 'startEventOption', 'clientTraceProcessingEvent') and
                (source_huisu_token != huisu_token(self.progress_snapshot()) or
                 source_flashback_token != flashback_token(self.progress_snapshot()))):
            self.reply('reliableRpcAck', {'s': wrapper['r']})
            if name == 'startEvent':
                self.reply('startEventReply', {'e': arguments.get('e'), 'r': 0}, callback_id)
            elif callback_id:
                self.reply('serverCallbackCarrier', {'_r_': {}}, callback_id)
            return
        if name in ('startEvent', 'startEventOption', 'clientTraceProcessingEvent'):
            dispatch_source = daerweila_request_source(self.progress_snapshot()) if source_owner is None else source_daerweila
            try:
                admitted = daerweila_queued_operation_matches(self.progress_snapshot(), name, arguments,
                    dispatch_source, self.story_effect_tables())
            except (ValueError, KeyError, TypeError):
                admitted = False
            if not admitted:
                self.reply('reliableRpcAck', {'s': wrapper['r']})
                if name == 'startEvent':
                    self.reply('startEventReply', {'e': arguments.get('e'), 'r': 0}, callback_id)
                elif callback_id:
                    self.reply('serverCallbackCarrier', {'_r_': {}}, callback_id)
                return
            arguments = dict(arguments)
            arguments.pop('_daerweila_source', None)
            arguments['_daerweila_source'] = dispatch_source
        # Receipt acknowledgment is separate from a business operation reply.
        self.reply('reliableRpcAck', {'s': wrapper['r']})
        if name in YUMI_METHODS:
            self.handle_yumi(name, arguments, source_yumi_context['identity'], source_yumi_context, callback_id)
            return
        if name=='dailyPureChooseHero':
            self.handle_daily_wish_choice(arguments,source_daily_choice if source_daily_choice is not None else daily_choice_token(self.progress_snapshot()),callback_id)
            return
        if name in ITEM_EXCHANGE_METHODS:
            self.handle_item_exchange(name, arguments, callback_id, 'reliable:%s:%s' % (self.owner.id,wrapper['r']), source_owner)
            return
        if name in SPECIAL_GACHA_OPERATIONS:
            self.handle_special_gacha(name, arguments, 'reliable:%s' % wrapper['r'], callback_id, source_gacha_operation)
            return
        if name in ('syncAllIntelligenceRequest','readTodayIntelligence','openIntelligenceRequest','handleIntelligenceRequest'):
            self.handle_intelligence(name,arguments,callback_id)
            return
        if name == 'requestStoryhuisu':
            self.process_huisu_operation(name, arguments, source_huisu_token, callback_id,
                self.city_operation_id('reliable:%s' % wrapper['r']), source_owner)
            return
        if name in ('areaBuildRequest', 'areaLevelUpRequest', 'enterPatrolRequest', 'patrolReward'):
            self.handle_city_action(name, arguments, self.city_operation_id('reliable:%s' % wrapper['r']), callback_id,
                source_context=(source_owner, source_action_token) if source_owner is not None else None)
            return
        if name == 'combatOfflineRequest':
            if source_owner is not None and source_city_stage_token != (city_stage_provider_token(self.progress_snapshot()), special_city_stage_token(self.progress_snapshot()), normal_chapter_token(self.progress_snapshot())):
                self.reply('combatOfflineReply', {'t':0,'s':arguments.get('s',0),'f':'','h':[],'d':{},'c':{}}, callback_id)
                return
            self.handle_battle_admission(arguments, callback_id,
                source_context=(source_owner, source_flashback_token, source_role) if source_owner is not None else None)
            return
        if name == 'statusCheck' and arguments.get('s') == 'nextday':
            self.process_day_operation(name, arguments, callback_id)
            return
        if name == 'triggerExternalEvent':
            self.process_story('external', arguments, callback_id)
            return
        if name == 'startEventOption':
            self.process_story('option', arguments, callback_id)
            return
        if name == 'getAreaStagesRequest':
            self.reply_area_stages(arguments, callback_id)
            return
        if name in ('getAreaInfoRequest', 'getAllAreaInfoRequest'):
            self.reply_city_areas(name, arguments, callback_id)
            return
        if name == 'requestCheckLuckyDrawFurnitureOpen':
            self.reply('serverCallbackCarrier', {'_r_': True}, callback_id)
            return
        if name in ('requestLuckyDrawFriendCard', 'requestLuckyDrawNewFriendCard',
                    'requestLuckyDrawFriendLianChouCard', 'requestLuckyDrawNewFriendLianChouCard',
                    'requestLuckyDrawFurnitureCard', 'requestLuckyDrawFurnitureLianchouCard'):
            identity = 'reliable:%s' % wrapper['r']
            self.handle_dedicated_gacha(name, arguments, callback_id, identity, source_gacha_operation)
            return
        if name in ('requestLuckyDrawFile', 'requestLuckyDrawFileAndOpenAll', 'requestLuckyDrawAllLeftCard'):
            self.handle_gacha(name, arguments, callback_id, source_gacha_presentation)
            return
        if name in ('equipTreasureBatch', 'unequipTreasure', 'unequipAllTreasure'):
            self.handle_treasure_equipment(name, arguments, callback_id)
            return
        if name == 'changeAwakeSkinStyle':
            self.change_awake_skin_style(arguments, callback_id)
            return
        if name == 'statusSwitch':
            self.status = arguments['s']
            self.save_progress()
            self.reply('statusSwitchReply', {'r': 'ok', 's': self.status}, callback_id)
            if self.status == 'city':
                offer_story_starter_choice(self)
                offer_paused_role_resume(self)
                offer_pending_battle_resume(self)
            return
        elif name == 'updateEventCondClient':
            if arguments.get('c') == 102 and arguments.get('v') == '4':
                if flashback_context(self.progress_snapshot()) is not None:
                    self.process_flashback_operation(name, {'c': 102, 'v': '4'},
                        (flashback_token(self.progress_snapshot()) if source_owner is None else source_flashback_token), callback_id,
                        intent_id='%s:%s' % (self.flashback_session_identity(), wrapper['r']))
                    return
                if huisu_context(self.progress_snapshot(), True) is not None:
                    self.process_day_operation(name, arguments, callback_id, huisu_source=(source_huisu_token, self.city_operation_id('reliable:%s' % wrapper['r'])))
                else:
                    self.process_day_operation(name, arguments, callback_id)
                return
            value = json.loads(arguments['v'])
            if arguments['c'] == 102:
                value = merge_client_operations(self.conditions.get(102), value)
            self.conditions[arguments['c']] = value
            self.save_progress()
        elif name == 'pullEvents':
            offer_paused_role_resume(self)
            try:
                self.refresh_story_triggers()
            except Exception:
                self.reply('serverCallbackCarrier', {'_r_': {}}, callback_id)
                raise
            offer_story_starter_choice(self)
            self.sync_daerweila_projection()
            self.reply('pullEventsReply', {
                'a': self.available_events.items(),
                'p': list(self.processing_events)}, callback_id)
            return
        elif name == 'startEvent':
            event = arguments['e']
            if event in self.available_events:
                previous = self.progress_snapshot()
                try:
                    candidate, unused = select_city_patrol_event(previous, event)
                    import com.data.cdata.event_content as _hs_content
                    import com.data.cdata.event_condition as _hs_triggers
                    # Bind dispatch before removing original branch availability.
                    begin_story_occurrence(candidate, event, _hs_content.data, _hs_triggers.data,
                        tables=self.story_effect_tables())
                    candidate['available_events'] = [entry for entry in candidate['available_events'] if entry[0] != event]
                    candidate['processing_events'].append(event)
                    candidate, gate_notices = self.prepare_story_gate(candidate, event)
                    self.restore_progress(candidate)
                    self.save_progress()
                except Exception:
                    self.restore_progress(previous)
                    dispatch = self.story.get('daerweila_dispatch') or {}
                    first = dispatch.get('first_devil', {})
                    offer = dispatch.get('offers', {}).get(first.get('offer'), {})
                    pair = dispatch.get('catalog', {}).get('pairs', {}).get(str(offer.get('pair')), {})
                    if first.get('phase') == 'intro_pending' and event == pair.get('devil'):
                        for sync_name, sync_body in daerweila_sync_notices(previous):
                            self.reply(sync_name, sync_body)
                    self.reply('startEventReply', {'e': event, 'r': 0}, callback_id)
                    raise
                for name, payload in gate_notices:
                    self.reply(name, payload)
                self.reply('startEventReply', {'e': event, 'r': 1}, callback_id)
                self.process_story('start', {'e': event})
                return
            if event in self.processing_events and event not in self._started_this_session:
                # A fresh client must re-enter an unfinished event after load.
                # A duplicate start in the same session must not re-enter it.
                previous = self.progress_snapshot()
                candidate, gate_notices = self.prepare_story_gate(previous, event)
                if candidate != previous:
                    self.restore_progress(candidate)
                    try:
                        self.save_progress()
                    except Exception:
                        self.restore_progress(previous)
                        self.reply('startEventReply', {'e': event, 'r': 0}, callback_id)
                        raise
                for name, payload in gate_notices:
                    self.reply(name, payload)
                self.reply('startEventReply', {'e': event, 'r': 1}, callback_id)
                self.process_story('start', {'e': event})
                return
            if event in self.processing_events and event in self._started_this_session:
                if callback_id:
                    key = (event,story_occurrence_key({'story':self.story},event))
                    identity = (key,callback_id)
                    if identity not in self._event_start_callback_receipts:
                        self._event_start_callback_receipts.add(identity)
                        self.reply('serverCallbackCarrier',{'_r_':{}},callback_id)
                return
            if event not in self.processing_events:
                self.reply('startEventReply', {'e': event, 'r': 0}, callback_id)
                return
        elif name == 'reliableEcho':
            pass
        elif name == 'clientTraceProcessingEvent':
            # The source stamp belongs to the queued request, never its payload.
            arguments = dict(arguments)
            arguments.pop('_winning_terminal_trace_source', None)
            if source_story_trace is not None:
                arguments['_winning_terminal_trace_source'] = source_story_trace
            self.process_story('trace', arguments, callback_id)
            return
        elif name in ('clientAskTriggerNewbee', 'checkProcessingEvent') and SKIP_TUTORIAL_UI:
            # Compatibility for an already-queued known teaching request.
            # Normal startup hooks prevent taking its UI lock or sending it.
            _f7_log('TUTORIAL RPC SKIP %s %r' % (name, arguments))
        else:
            if not self.reject_unimplemented_rpc(name, arguments, callback_id, source_owner=rejection_owner):
                _f7_log('RPC BUSINESS UNIMPLEMENTED %s %r' % (name, arguments))
            return
        if callback_id:
            self.reply('serverCallbackCarrier', {'_r_': {}}, callback_id)

    def change_awake_skin_style(self, parameters, callback_id=None):
        import com.data.cdata.hero as hero_data
        import com.data.cdata.awake_consume_data as awake_data
        callback_id = callback_id or parameters.get('_cbid_')
        previous = copy.deepcopy(self.profile)
        try:
            result = change_awakening_style(self.profile, parameters.get('hid'),
                parameters.get('ss'), hero_data.data, awake_data.data)
        except ValueError:
            # No invalid authoritative state; still complete the callback lock.
            self.reply('serverCallbackCarrier', {'_r_': {}}, callback_id)
            return
        try:
            self.save_progress()
        except Exception:
            self.profile = previous
            self.reply('serverCallbackCarrier', {'_r_': {}}, callback_id)
            raise
        self.reply('replyChangeAwakeSkinStyle', result, callback_id)

    def set_skin(self, parameters):
        hero_id, instance = parameters['h'], str(parameters['sid'])
        hero = (self.profile or {}).get('heroes', {}).get(str(hero_id))
        skin = hero['sk'].get(instance) if hero else None
        valid = bool(skin and not skin.get('fb') and not skin.get('ias'))
        if valid:
            valid = remaining_skin_resources_available(skin['i'])
        if valid:
            previous = copy.deepcopy(self.profile)
            hero['cs'], hero['ass'] = instance, False
            try:
                self.save_progress()
            except Exception:
                self.profile = previous
                self.reply('setSkinReply', {'s': False, 'sid': instance, 'ass': previous['heroes'][str(hero_id)].get('ass', False)}, parameters.get('_cbid_'))
                raise
        self.reply('setSkinReply', {'s': valid, 'sid': instance, 'ass': False}, parameters.get('_cbid_'))

    def ensure_treasure_inventory(self):
        from common.IdManager import IdManager
        import com.const as const
        import com.data.cdata.hero_treasure as treasure_data
        import com.data.cdata.item_data as item_data
        inventory, changed = migrate_treasure_inventory(self.profile.get('treasures'),
            treasure_data.data, item_data.data, const.CombatAttrs.NAME_TO_INDEX,
            IdManager.genid, int(time.time()))
        if changed:
            previous = copy.deepcopy(self.profile)
            self.profile['treasures'] = inventory
            try:
                self.save_progress()
            except Exception:
                self.profile = previous
                raise

    def native_treasure_items(self, items):
        from common.IdManager import IdManager
        result = copy.deepcopy(items)
        for item in result:
            if isinstance(item['u'], _f7_text_types):
                item['u'] = IdManager.str2id(item['u'])
        return result

    def handle_treasure_equipment(self, name, parameters, callback_id=None):
        import com.data.cdata.hero_treasure as treasure_data
        from common.IdManager import IdManager
        callback_id = callback_id or parameters.get('_cbid_')
        try:
            profile, inventory, reply, result, restored = prepare_treasure_equipment(
                self.profile, self.profile['treasures'], name, parameters, treasure_data.data)
        except (ValueError, KeyError, TypeError):
            self.reply('serverCallbackCarrier', {'_r_': {}}, callback_id)
            return
        previous = copy.deepcopy(self.profile)
        profile['treasures'] = inventory
        self.profile = profile
        try:
            self.save_progress()
        except Exception:
            self.profile = previous
            self.reply('serverCallbackCarrier', {'_r_': {}}, callback_id)
            raise
        if restored:
            self.reply('updateItems', {'i': self.native_treasure_items(restored)})
        if name == 'equipTreasureBatch':
            result['e'] = [(uid, source, self.native_treasure_items([item])[0])
                           for uid, source, item in result['e']]
        elif name == 'unequipTreasure':
            result['u'] = IdManager.str2id(result['u'])
        self.reply(reply, result, callback_id)

    def sync_gacha_items(self):
        from common.IdManager import IdManager
        items = copy.deepcopy((self.gacha or {}).get('items', []))
        items.extend(copy.deepcopy((self.profile or {}).get('treasures', {}).get('items', [])))
        if items:
            for item in items:
                item['u'] = IdManager.str2id(item['u'])
            self.reply('updateItems', {'i': items})

    def gacha_tables(self):
        tables = {}
        for name in ('chouka_normal', 'chouka_default', 'chouka_info', 'chouka_friend',
                     'chouka_friend_default', 'reward_random', 'reward_common', 'item_data',
                     'hero', 'chouka_hero_file', 'hero_treasure', 'hero_treasure_generate', 'skin', 'furniture_data',
                     'chouka_jiaozhi', 'chouka_leiji_reward', 'hero_self_choose_info', 'chouka_wish_treasure_choose', 'item_store_wish_change', 'chouka_treasure_wish', 'activity_config', 'activity_template'):
            try:
                tables[name] = __import__('com.data.cdata.' + name, fromlist=['data']).data
            except ImportError:
                tables[name] = {}
        return tables

    def sync_gacha_native_state(self, wire=None, refresh_cards=False):
        from entity.avatar_attrs.LuckyDrawData import ActivityData
        tables = self.gacha_tables()
        saved = self.progress_snapshot()
        ldd = self.owner.luckyDrawData
        effective = offline_archive_context(wire)
        view_state = hero_wish_eligibility_view(saved,tables,effective)
        view = gacha_snapshot_projection(view_state, {}, tables['chouka_info'],effective)
        ldd.card_times, ldd.is_open_file = view['ct'], view['iof']
        ldd.cur_card_times_day = view['cctd']
        ldd.hero_file_progress = {int(k): v for k, v in view['hfp'].items()}
        ldd.friend_draw, ldd.friend_draw_count = view['fd'], view['fdc']
        ldd.new_friend_draw_count = view['nfdc']
        ldd.inc_up_cnt = {int(k): v for k, v in view['inc_up_cnt'].items()}
        ldd.wish_info = dict(copy.deepcopy(view.get('wi',[])))
        for wire, data in view['ad']:
            if wire not in ldd.activity_data:
                ldd.activity_data[wire] = ActivityData(wire)
            activity = ldd.activity_data[wire]
            activity.card_times, activity.is_open_file = data['ct'], data['iof']
            activity.cur_card_times_day, activity.lianchou_times = data['cctd'], data['lt']
            activity.choose_heroes, activity.choose_treasure = copy.deepcopy(data['ch']), copy.deepcopy(data['ctr'])
            for field,key in (('treasure_wish','tw'),('wish_info','wi'),('jiaozhi_count','jzc'),('jiaozhi_rewards','jzr'),('replace_count','rc')):
                setattr(activity,field,dict(copy.deepcopy(data[key])))
        # Stock RPC replies own draw_info during reveal animations. In particular
        # replyFile restores the six-draw fake-file mask before async model load.
        # Canonical all-open results must not overwrite that presentation mask.
        if refresh_cards:
            for wire in (self.gacha_pools or {}).get('pools', {}):
                ldd.set_draw_info(int(wire), pool_file_view(self.gacha_pools, int(wire)))

    def native_gacha_card(self, card):
        from common.IdManager import IdManager
        result = copy.deepcopy(card)
        for key in list(result):
            if key.startswith('_gacha_'):
                result.pop(key)
        for field in ('treasure', 'treasure_trans'):
            for reward in result.get(field, []) + result.get('other_reward',{}).get('activityReward',{}).get(field,[]):
                reward[3] = [IdManager.str2id(uid) if isinstance(uid, _f7_text_types) else uid for uid in reward[3]]
        return result

    def grant_gacha_pendant(self, candidate, definition):
        manager = getattr(self.owner,'heroMgrData',None)
        template = getattr(self,'_snapshot_template',{}).get('heromgr',{})
        pending = candidate['profile'].setdefault('hero_pending',{})
        for key,attribute in (('ps','pendingSkins'),('psc','pendingSkinsCreateTime'),('pp','pendingPendant'),('ppc','pendingPendantCreateTime')):
            if key not in pending:
                pending[key] = {str(k):copy.deepcopy(v) for k,v in getattr(manager,attribute,template.get(key,{})).items()}
        return grant_original_pendant(candidate,definition)

    def grant_gacha_extras(self, candidate, extras, tables):
        from common.IdManager import IdManager
        notices = []
        for template in extras.get('skin', []):
            row = tables['skin'].get(template)
            if not row:
                raise ValueError('Missing original reward skin')
            hero_id = row['hero']
            hero = candidate['profile']['heroes'][str(hero_id)]
            if any(skin['i'] == template for skin in hero['sk'].values()):
                continue
            grant_profile_skins(hero_id, hero, [template], tables['skin'], IdManager.genid, int(time.time()), allow_dye=bool(row.get('is_dye_skin')))
        for key, notice in (('yuanbao', 'updateYuanBao'), ('giftcoin', 'updateGiftCoin')):
            if extras.get(key):
                if type(extras[key]) is not int or extras[key] <= 0:
                    raise ValueError('Invalid original currency reward')
                economy = candidate['profile']['economy']
                economy[key] = economy.get(key, 0) + extras[key]
                notices.append((notice, {'v': economy[key]}))
        if extras.get('furniture') or extras.get('gift'):
            raise ValueError('Unexpected unsupported extra schema; original furniture is item inventory')
        return notices

    def gacha_operation_frame(self):
        import gg
        panels = getattr(getattr(gg, 'ui', None), 'panels', None)
        frame = []
        # Submit modals can close immediately after sending their original RPC;
        # bind the lasting source/result containers, not those transient modals.
        for name in ('card_tab', 'card_box', 'card_open', 'card_yingzhuang',
                     'city_room_danchi_new', 'settlement_window_summon'):
            panel = getattr(panels, name, None)
            frame.append((id(panel), id(getattr(panel, '_node', None)), getattr(panel, 'valid', None),
                getattr(panel, '_f7_presentation_epoch', 0), getattr(panel, 'draw_type', None)))
        city = getattr(gg, 'city_container', None)
        scene = city.get_current_scene() if callable(getattr(city, 'get_current_scene', None)) else None
        return tuple(frame), id(scene)

    def gacha_operation_lock_name(self, name):
        if name == 'setChooseHeroes':
            return 'setChooseHero'
        if name == 'setChooseTreasure':
            return name
        if name.startswith('requestLuckyDrawFurniture'):
            return name
        if name.startswith('requestLuckyDraw'):
            return name[len('request'):]
        return None

    def gacha_lock_lease(self, name):
        import gg
        return acquire_ui_lock_lease(gg, self.gacha_operation_lock_name(name))

    def complete_gacha_lock_lease(self, source, after_reply=False):
        import gg
        return complete_ui_lock_lease(gg, source, after_reply)

    def gacha_reply(self, source, name, parameters, callback_id=None, allow_expired=False):
        import gg
        lease = source.get('lock_lease')
        if source.get('lock_tracking') and (lease is None or lease['released'] or lease['delivering']):
            return
        if self.gacha_operation_state(source, period=not allow_expired) is not None:
            self.reject_stale_gacha_operation(source)
            return
        return deliver_ui_lock_reply(gg, source, lambda: self.reply(name, parameters, callback_id))

    def gacha_operation_source(self, name, parameters, callback_id=None, request_id=None):
        import gg
        family = 'special' if name in SPECIAL_GACHA_OPERATIONS else 'dedicated'
        wire = parameters.get('t', 0) if family == 'special' or 'Furniture' in name else (131 if 'NewFriend' in name else 99)
        sequence = getattr(self, '_gacha_operation_sequence', 0) + 1
        self._gacha_operation_sequence = sequence
        callbacks = getattr(gg, 'avatar_callback_map', None)
        ui, generation, lease, tracking = self.gacha_lock_lease(name)
        identity = (name, request_id if request_id is not None else ('callback:%s' % callback_id if callback_id is not None else None))
        tickets = getattr(self, '_gacha_transport_tickets', {})
        old = tickets.get(identity) if identity[1] is not None else None
        if (tracking and lease is None and old is not None and old['ui'] is ui and
                old['lock_generation'] is generation):
            # A transport retry acquired no additional native lock. Reuse its
            # original owner/period/ticket and do not supersede a newer request.
            return old
        source = {'owner': self.owner, 'avatar': getattr(gg, 'avatar', self.owner),
            'proxy': getattr(gg, '_f7_avatar_proxy', self), 'frame': self.gacha_operation_frame(),
            'context': copy.deepcopy(offline_archive_context(wire) or {}), 'wire': wire,
            'name': name, 'family': family, 'sequence': sequence, 'callback_id': callback_id,
            'callback_map': callbacks, 'callback': callbacks.get(callback_id) if isinstance(callbacks, dict) else None,
            'ui': ui, 'lock_generation': generation, 'lock_lease': lease, 'lock_tracking': tracking}
        if tracking and identity[1] is not None:
            self._gacha_transport_tickets = tickets
            tickets[identity] = source
            # Completed old tickets are safe to evict: a retry without a new
            # native lock then has no lease and cannot invoke an unlock body.
            if len(tickets) > 512:
                for key, ticket in list(tickets.items()):
                    if len(tickets) <= 512:
                        break
                    if ticket is not source and (ticket['lock_lease'] is None or ticket['lock_lease']['released']):
                        tickets.pop(key, None)
        if name != 'setWishGroupAnimPlayed':
            if not hasattr(self, '_gacha_operation_sources'):
                self._gacha_operation_sources = {}
            self._gacha_operation_sources[name] = source
        return source

    def gacha_operation_state(self, source, period=True):
        import gg
        if (self.owner is not source['owner'] or source['avatar'] is not source['owner'] or source['proxy'] is not self or
                getattr(gg, 'avatar', self.owner) is not source['avatar'] or
                getattr(gg, '_f7_avatar_proxy', self) is not source['proxy']):
            return 'owner'
        if (self.gacha_operation_frame() != source['frame'] or
                source['name'] != 'setWishGroupAnimPlayed' and
                getattr(self, '_gacha_operation_sources', {}).get(source['name']) is not source):
            return 'presentation'
        callbacks = getattr(gg, 'avatar_callback_map', None)
        if source['callback_id'] is not None and isinstance(source['callback_map'], dict):
            if callbacks is not source['callback_map'] or callbacks.get(source['callback_id']) is not source['callback']:
                return 'callback'
        if period and (offline_archive_context(source['wire']) or {}) != source['context']:
            return 'period'
        return ui_lock_lease_state(gg, source)

    def gacha_scoped_operation_id(self, source, identity):
        import hashlib
        namespaces = getattr(self, '_gacha_rpc_namespaces', None)
        if namespaces is None:
            namespaces = self._gacha_rpc_namespaces = {}
        family = source['family']
        if family not in namespaces:
            namespaces[family] = ''.join('%02x' % value for value in bytearray(os.urandom(16)))
        period = hashlib.sha256(json.dumps(source['context'], sort_keys=True, separators=(',', ':')).encode('ascii')).hexdigest()
        return 'gacha-%s:%s:%s:%s:%s:%s' % (family, namespaces[family], source['wire'], source['name'], period, identity)

    def reject_stale_gacha_operation(self, source):
        import gg
        state = self.gacha_operation_state(source, period=False)
        callback_id = source['callback_id']
        if state == 'delivering':
            # Retry during its own native consumer owns no second reference.
            return
        if source.get('canonical_result_saved'):
            self.cancel_gacha_callback(source)
            self.complete_gacha_lock_lease(source)
            if (self.owner is source['owner'] and getattr(gg, 'avatar', self.owner) is source['avatar'] and
                    getattr(gg, '_f7_avatar_proxy', self) is source['proxy']):
                notify = getattr(getattr(getattr(getattr(gg, 'ui', None), 'panels', None), 'common_message', None), 'notify_message', None)
                if callable(notify):
                    notify(u'\u62bd\u53d6\u7ed3\u679c\u5df2\u4fdd\u5b58\uff0c\u8bf7\u91cd\u65b0\u8fdb\u5165\u67e5\u770b')
            _f7_log('LOCAL GACHA saved result retained; obsolete presentation cancelled: %s' % source['name'])
            return
        if state is not None:
            # Obsolete callbacks must not run their unscoped named unlock on a
            # newer panel/request. Remove only this exact old callback, and
            # never one also owned by the newer in-flight request.
            self.cancel_gacha_callback(source)
            self.complete_gacha_lock_lease(source)
            _f7_log('LOCAL GACHA cancelled; original lease completed without business consumer: %s %s' % (source['name'], state))
            return
        name, wire = source['name'], source['wire']
        if name in ('setChooseHeroes', 'setChooseTreasure'):
            row = special_pool_context(self.progress_snapshot(), wire, source['context'].get('wish_id'))
            if name == 'setChooseHeroes':
                self.gacha_reply(source, 'replySetChooseHeroes', {'r': 1809, 't': wire, 'h': row['choose_heroes']}, callback_id, allow_expired=True)
            else:
                self.gacha_reply(source, 'replySetChooseTreasure', {'r': 1882, 't': wire, 'i': row['choose_treasure']}, callback_id, allow_expired=True)
        elif source['family'] == 'dedicated':
            if name in ('requestLuckyDrawFriendCard', 'requestLuckyDrawFriendLianChouCard'):
                # Stock st=False still sets friend_draw=True. Its original
                # callback is unlock-only; do not invoke that business body.
                if callback_id is not None:
                    self.gacha_reply(source, 'serverCallbackCarrier', {'_r_': {}}, callback_id, allow_expired=True)
            else:
                failure = {'rs': False, 'i': {}} if 'Furniture' in name else {'st': False, 'r': [] if 'Lian' in name else {}}
                self.gacha_reply(source, name.replace('request', 'reply', 1), failure, callback_id, allow_expired=True)
        if self.gacha_operation_state(source, period=False) in (None, 'callback', 'completed'):
            notify = getattr(getattr(getattr(getattr(gg, 'ui', None), 'panels', None), 'common_message', None), 'notify_message', None)
            if callable(notify):
                notify(u'\u62bd\u53d6\u8bf7\u6c42\u5df2\u5931\u6548\uff0c\u672a\u6267\u884c\uff0c\u8bf7\u91cd\u65b0\u64cd\u4f5c')

    def cancel_gacha_callback(self, source):
        import gg
        callback_id = source['callback_id']
        latest = getattr(self, '_gacha_operation_sources', {}).get(source['name'])
        callbacks = getattr(gg, 'avatar_callback_map', None)
        if (self.owner is source['owner'] and source['callback'] is not None and callbacks is source['callback_map'] and
                callbacks.get(callback_id) is source['callback'] and
                not (latest is not source and latest and latest['callback'] is source['callback'])):
            callbacks.pop(callback_id, None)
            getattr(gg, 'avatar_callback_need_result', {}).pop(callback_id, None)

    def handle_dedicated_gacha(self, name, parameters, callback_id=None, operation_id=None, source_operation=None):
        callback_id = parameters.get('_cbid_') if callback_id is None else callback_id
        source_operation = source_operation or self.gacha_operation_source(name, parameters, callback_id)
        callback_id = source_operation['callback_id']
        if self.gacha_operation_state(source_operation) is not None:
            self.reject_stale_gacha_operation(source_operation)
            return
        import random
        import com.const as const
        from common.IdManager import IdManager
        furniture = 'Furniture' in name
        is_newfriend = 'NewFriend' in name
        batch = 'Lian' in name
        pool = parameters.get('t') if furniture else (131 if is_newfriend else 99)
        if operation_id is None and callback_id is not None:
            operation_id = 'callback:%s' % callback_id
        count = 10 if batch else 1
        reply_name = name.replace('request', 'reply', 1)
        result = {'rs': False, 'i': {}} if furniture else {'st': False, 'r': [] if batch else {}}
        previous, committed = self.progress_snapshot(), False
        try:
            tables = self.gacha_tables()
            config = original_pool_config(pool, tables['chouka_info'])
            if config.get('mode') != 'direct' or (furniture and tables['chouka_info'][pool].get('poolType') != 2):
                raise ValueError('Wrong original direct pool RPC family')
            if furniture:
                config['daily_cap'] = const.MAX_FURNITURE_TIMES_DAY
                count = const.SUMMON_FURNITURE_LIANCHOU_TIMES + 1 if batch else 1
                config['batch_sizes'] = [1, const.SUMMON_FURNITURE_LIANCHOU_TIMES + 1]
            candidate = migrate_gateway_gacha_state(previous)
            if operation_id is None:
                sequence = candidate['gacha_pools'].get('next_direct_operation', 1)
                operation_id = 'direct:%s:%s' % (pool, sequence)
                candidate['gacha_pools']['next_direct_operation'] = sequence + 1
            operation_id = self.gacha_scoped_operation_id(source_operation, operation_id)
            def make_treasure(template, quality, trade):
                return make_table_treasure_reward(template, quality, tables['hero_treasure'],
                    const.CombatAttrs.NAME_TO_INDEX, IdManager.genid, int(time.time()), trade)
            def reveal(wire, ordinal, force_s, seed, transaction):
                shared = transaction.setdefault('inc_up_cnt', {})
                resolver = make_original_gacha_resolver(tables, random.Random(seed).randrange, make_treasure,
                    make_table_hero_result(tables, candidate['profile']['heroes'], candidate['gacha'].get('hero_fragment_progress', {})),
                    lambda t, n: dict(special_pool_context({'gacha_pools':transaction},t),inc_up_cnt=shared))
                card = resolver(wire, ordinal, force_s)
                source = card.get('_gacha_source', {})
                counter = source.get('inc_up_cnt_type')
                if counter is not None:
                    key = str(counter)
                    shared[key] = 0 if source.get('is_up') else shared.get(key, shared.get(counter, 0)) + 1
                return card
            day_key = '%s:%s' % (self.story.get('week', 0), self.story.get('date', 0))
            candidate['gacha_pools'], cards, newly, changed = direct_pool_draw(candidate['gacha_pools'], pool, config,
                count, operation_id, day_key, None, IdManager.genid, lambda item: tables['item_data'][item]['wrap'],
                credit_items=False, contextual_resolver=reveal)
            candidate, rendered, notices = apply_original_gacha_rewards(candidate, newly, IdManager.genid,
                lambda item: tables['item_data'][item]['wrap'], grant_hero=lambda state, hid: native_default_hero_snapshot(hid),
                grant_extra=lambda state, extras: self.grant_gacha_extras(state, extras, tables),
                        item_definitions=tables['item_data'], grant_pendant=self.grant_gacha_pendant)
            saved_pool = candidate['gacha_pools']['pools'][str(pool)]
            if furniture and batch and newly:
                saved_pool['batch_count'] = saved_pool.get('batch_count', 0) + 1
            if candidate != previous:
                self.restore_progress(candidate)
                self.save_progress()
                committed = True
            source_operation['canonical_result_saved'] = True
            wire_cards = [self.native_gacha_card(card) for card in cards]
            if furniture:
                info = {'t': pool, 'ct': saved_pool['daily_count'], 'rwd': wire_cards if batch else wire_cards[0]}
                if batch:
                    info['lt'] = saved_pool.get('batch_count', 0)
                result = {'rs': True, 'i': info}
            else:
                result = {'st': True, 'r': wire_cards if batch else wire_cards[0]}
            for notice, payload in notices:
                self.reply(notice, payload)
            self.gacha_reply(source_operation, reply_name, result, callback_id)
            try:
                self.sync_gacha_native_state(pool, refresh_cards=False)
                view = gacha_snapshot_projection(self.progress_snapshot(), {})
                self.reply('updateCurTimesDay', {'cctd': view['cctd'], 'fdc': view['fdc'], 'nfdc': view['nfdc'],
                    'acctd': [(t, row['cctd']) for t, row in view['ad']]})
                self.reply('updateFriendDraw', {'fd': view['fd']})
            except Exception:
                _f7_log('LOCAL DIRECT GACHA projection pending: %s' % traceback.format_exc())
        except Exception:
            if source_operation.get('canonical_result_saved'):
                self.reject_stale_gacha_operation(source_operation)
            elif not committed:
                self.restore_progress(previous)
                if name in ('requestLuckyDrawFriendCard', 'requestLuckyDrawFriendLianChouCard'):
                    self.reject_stale_gacha_operation(source_operation)
                else:
                    self.gacha_reply(source_operation, reply_name, result, callback_id)
            _f7_log('LOCAL DIRECT GACHA rejected: %s' % traceback.format_exc())
            try:
                self.sync_gacha_native_state(pool, refresh_cards=False)
                self.reply('updateFriendDraw', {'fd': gacha_snapshot_projection(self.progress_snapshot(), {})['fd']})
            except Exception:
                pass

    def install_item_exchange_limit_check(self):
        import gg
        owner = self.owner
        data = owner.luckyDrawData
        original = data.checkSummoncoinExchangeNum
        if getattr(data,'_f7_item_exchange_limits',False):
            return
        def check(index,num=1):
            if self.owner is owner and getattr(gg,'avatar',None) is owner:
                projected = item_exchange_limits(self.progress_snapshot(),self._item_exchange_clock())
                data.summoncoin_daily_limit = dict(projected['sdl'])
                data.summoncoin_weekly_limit = dict(projected['swl'])
            return original(index,num)
        data.checkSummoncoinExchangeNum = check
        data._f7_item_exchange_limits = True

    def handle_item_exchange(self, name, parameters, callback_id=None, operation_id=None, source_owner=None):
        import gg
        from common.IdManager import IdManager
        import com.const as const
        origin_owner = self.owner
        if (source_owner is not None and source_owner is not origin_owner) or getattr(gg,'avatar',None) is not origin_owner:
            return
        callback_id = callback_id or parameters.get('_cbid_')
        previous = self.progress_snapshot()
        try:
            if operation_id is None:
                if callback_id is not None:
                    operation_id = 'callback:%s:%s:%s' % (self.owner.id,name,callback_id)
                else:
                    sequence = getattr(self,'_item_exchange_sequence',0)+1
                    self._item_exchange_sequence = sequence
                    operation_id = 'direct:%s:%s:%s' % (self.owner.id,name,sequence)
            operation_id = 'session:%s:%s' % (self._item_exchange_session,operation_id)
            tables = {'fragment_common_id':const.FRAGMENT_COMMON_ID}
            for table_name in ('item_data','memory_crystal_exchange','summoncoin_exchange','center_bank'):
                tables[table_name] = __import__('com.data.cdata.'+table_name,fromlist=['data']).data
            candidate,notices,changed,diagnostic = prepare_item_exchange(
                previous,name,parameters,tables,operation_id,IdManager.genid,self._item_exchange_clock())
            if changed:
                self.restore_progress(candidate)
                self.save_progress()
        except Exception:
            self.restore_progress(previous)
            if self.owner is not origin_owner or getattr(gg,'avatar',None) is not origin_owner:
                return
            if callback_id is not None:
                self.reply('serverCallbackCarrier',{'_r_':False},callback_id)
            try:
                gg.ui.panels.common_message.notify_message(u'\u5151\u6362\u5931\u8d25\uff1a\u8bf7\u68c0\u67e5\u6570\u91cf\u3001\u4f59\u989d\u548c\u9650\u6b21')
            except Exception:
                pass
            _f7_log('LOCAL ITEM EXCHANGE failed: %s' % traceback.format_exc())
            return
        for notice,payload in notices:
            if self.owner is not origin_owner or getattr(gg,'avatar',None) is not origin_owner:
                break
            if notice == 'exchangeYuanbaoBalance':
                payload = {'v':payload['v'],'fv':getattr(self.owner,'_freeYuanbao',0),
                    'dv':getattr(self.owner,'_debtYuanbao',0),'eby':getattr(self.owner,'_everBuy',{}),
                    'gc':getattr(self.owner,'_giftCard',{}),'chry':getattr(self.owner,'christmas_yuanbao',0),
                    'nyy':getattr(self.owner,'newyear_yuanbao',0),'mary':getattr(self.owner,'march_yuanbao',0),
                    'mayy':getattr(self.owner,'may_yuanbao',0),'novy':getattr(self.owner,'nov_yuanbao',0),
                    'yuanbao_20190130':getattr(self.owner,'yuanbao_20190130',0),
                    'yuanbao_20190403':getattr(self.owner,'yuanbao_20190403',0),'ybumba':0}
                notice = 'updateYuanbao'
            elif notice == 'deleteItems':
                payload = {'i':[IdManager.str2id(uid) for uid in payload['i']]}
            self.reply(notice,payload,callback_id if notice in
                ('replyMemoryCrystalExchangeSuipian','summoncoinExchangeReply','yuanbaoExchangeCrystalReply') else None)
        if diagnostic.get('replay') and callback_id is not None and self.owner is origin_owner and getattr(gg,'avatar',None) is origin_owner:
            self.reply('serverCallbackCarrier',{'_r_':{}},callback_id)
        _f7_log('LOCAL ITEM EXCHANGE %s %s' % (name,diagnostic))

    def handle_special_gacha(self, name, parameters, operation_id, callback_id=None, source_operation=None):
        callback_id = parameters.get('_cbid_') if callback_id is None else callback_id
        source_operation = source_operation or self.gacha_operation_source(name, parameters, callback_id)
        callback_id = source_operation['callback_id']
        if self.gacha_operation_state(source_operation) is not None:
            self.reject_stale_gacha_operation(source_operation)
            return
        previous = self.progress_snapshot()
        committed = False
        notices = []
        try:
            context = copy.deepcopy(source_operation['context'])
            context['archive_wire_t'] = context.get('wire_t')
            context['now'] = time.time()
            operation_id = self.gacha_scoped_operation_id(source_operation,
                operation_id if operation_id is not None else 'plain:%s' % source_operation['sequence'])
            candidate = migrate_gateway_gacha_state(previous)
            candidate,notices,changed,diagnostic = prepare_special_gacha_operation(
                candidate,name,parameters,self.gacha_tables(),operation_id,context)
            if diagnostic.get('success') and changed:
                self.restore_progress(candidate)
                self.save_progress()
                committed = True
            if diagnostic.get('success'):
                source_operation['canonical_result_saved'] = True
            for notice,payload in notices:
                if notice in ('replySetChooseHeroes', 'replySetChooseTreasure'):
                    self.gacha_reply(source_operation, notice, payload, callback_id)
                else:
                    self.reply(notice, payload)
            self.sync_gacha_native_state(parameters.get('t'), refresh_cards=False)
            _f7_log('LOCAL SPECIAL GACHA %s %s' % (name,diagnostic))
        except Exception:
            if source_operation.get('canonical_result_saved'):
                self.reject_stale_gacha_operation(source_operation)
            elif not committed:
                self.restore_progress(previous)
                # Release original reliable UI lock with failure, never success.
                wire = parameters.get('t',0)
                failure_context = source_operation['context']
                row = special_pool_context(previous,wire,failure_context.get('wish_id'))
                if failure_context.get('no_wish'):row['choose_treasure']=[0,0,0]
                if name == 'setChooseHeroes':
                    self.gacha_reply(source_operation, 'replySetChooseHeroes',{'r':1809,'t':wire,'h':row['choose_heroes']},callback_id)
                elif name == 'setChooseTreasure':
                    self.gacha_reply(source_operation, 'replySetChooseTreasure',{'r':1882,'t':wire,'i':row['choose_treasure']},callback_id)
            _f7_log('LOCAL SPECIAL GACHA rejected: %s' % traceback.format_exc())

    def gacha_presentation_token(self, wire):
        import gg
        panel=getattr(getattr(getattr(gg,'ui',None),'panels',None),'card_box',None)
        city=getattr(gg,'city_container',None)
        scene=city.get_current_scene() if callable(getattr(city,'get_current_scene',None)) else None
        group=(((self.gacha_pools or {}).get('pools',{}).get(str(wire))or{}).get('group')or{}).get('id')
        active=getattr(panel,'get_luckyDraw_type',None)
        active_wire=active() if callable(active) else getattr(panel,'draw_type',None)
        return (self.owner,panel,getattr(panel,'_node',None),scene,group,getattr(panel,'_f7_presentation_epoch',0),getattr(panel,'valid',False),active_wire,getattr(gg,'avatar',None),getattr(gg,'_f7_avatar_proxy',None))

    def gacha_store_inactive_file_view(self, wire, info):
        import gg
        panel=getattr(getattr(getattr(gg,'ui',None),'panels',None),'card_box',None)
        active=getattr(panel,'get_luckyDraw_type',None)
        if getattr(panel,'valid',False) and callable(active) and active()==wire:
            # A stale read of the same wire must not overwrite its newer mask.
            return
        self.owner.luckyDrawData.set_draw_info(wire,copy.deepcopy(info))

    def handle_gacha(self, name, parameters, callback_id=None, source_presentation=None):
        import random
        from common.IdManager import IdManager
        import com.const as const
        callback_id = callback_id or parameters.get('_cbid_')
        pool = parameters.get('t', 1)
        replies = {
            'requestFile': ('replyFile', {'info': {}}),
            'requestLuckyDrawFile': ('replyLuckyDrawFile', {}),
            'requestLuckyDrawCard': ('replyLuckyDrawCard', {'info': {}, 'prog': {}}),
            'requestQuitFile': ('replyQuitFile', {}),
            'requestLuckyDrawFileAndOpenAll': ('replyLuckyDrawFileAndOpenAll', {'trwd': [], 'ffs': {}}),
            'requestLuckyDrawAllLeftCard': ('replyLuckyDrawAllLeftCard', {'trwd': []})}
        reply_name, result = replies[name]
        result.update(rt=False, t=pool)
        previous = self.progress_snapshot()
        committed = False
        presentation_current = True
        try:
            if source_presentation is not None and source_presentation[0] is not self.owner:
                return
            presentation_current = source_presentation is None or source_presentation==self.gacha_presentation_token(pool)
            if name!='requestFile' and not presentation_current:
                raise ValueError('Stale card operation cannot change another group or panel frame')
            tables = self.gacha_tables()
            config = original_pool_config(pool, tables['chouka_info'])
            if config.get('mode', 'cards') != 'cards':
                raise ValueError('Wrong original RPC family for this pool')
            candidate = migrate_gateway_gacha_state(previous)
            before_pool = candidate['gacha_pools']['pools'].get(str(pool))
            if name in ('requestLuckyDrawFileAndOpenAll','requestLuckyDrawAllLeftCard'):
                existing=(before_pool or {}).get('group')
                if (name=='requestLuckyDrawAllLeftCard' and not existing) or (existing and all(card['is_open']for card in existing['cards'])):
                    raise ValueError('Existing completed group has no unrevealed cards; no empty six-draw success')
            if name in ('requestLuckyDrawFile','requestLuckyDrawFileAndOpenAll') and not (before_pool or {}).get('group') and tables['chouka_info'].get(pool,{}).get('self_choose'):
                choice = special_pool_context(candidate,pool)['choose_heroes']
                if choice[0] != original_self_choose_hash(tables['chouka_info'][pool]) or not choice[1] or not choice[2]:
                    raise ValueError('Original self-choice pool requires actual user choice before new group')
            if name == 'requestFile' and before_pool is None:
                # Reads do not create or charge a group.
                if not presentation_current:
                    self.gacha_store_inactive_file_view(pool,{})
                    if callback_id:self.reply('serverCallbackCarrier',{'_r_':True},callback_id)
                else:
                    self.reply(reply_name, result, callback_id)
                return
            def make_treasure(template, quality, trade):
                return make_table_treasure_reward(template, quality, tables['hero_treasure'],
                    const.CombatAttrs.NAME_TO_INDEX, IdManager.genid, int(time.time()), trade)
            context = candidate['gacha_pools'].setdefault('inc_up_cnt', {})
            resolver = make_original_gacha_resolver(tables, random.randrange, make_treasure,
                make_table_hero_result(tables, candidate['profile']['heroes'],
                    candidate['gacha'].get('hero_fragment_progress', {})),
                lambda wire, ordinal: dict(special_pool_context(candidate,wire),inc_up_cnt=context))
            wish_notices = []
            shadow_owned = set(candidate['profile']['heroes'])
            shadow_fragments = copy.deepcopy(candidate['gacha'].get('hero_fragment_progress',{}))
            def reveal(wire, ordinal, force_s, seed, transaction_pools):
                rng = random.Random(seed)
                selected_context = special_pool_context({'gacha_pools':transaction_pools},wire)
                pinned = ((transaction_pools.get('pools',{}).get(str(wire)) or {}).get('group') or {}).get('special_context',{})
                if pinned.get('policy') == TREASURE_WISH_REVEAL_POLICY:
                    wish_context,notice = prepare_treasure_wish_reveal(transaction_pools,tables,wire,pinned['wish_id'],rng.randrange)
                    selected_context.update(wish_context)
                    wish_notices.append(notice)
                hero_wish_plan = None
                if pinned.get('hero_wish_policy') == HERO_WISH_PERIOD_POLICY:
                    wish_context,hero_wish_plan = prepare_hero_wish_reveal(transaction_pools,tables,wire,pinned,shadow_owned,rng.randrange)
                    selected_context.update(wish_context)
                selected_context.update(prepare_jiaozhi_context(transaction_pools,tables,wire,shadow_owned,shadow_fragments))
                def activity_finalize(card,random_pool):
                    notice = finalize_jiaozhi_reveal(transaction_pools,tables,wire,card,random_pool)
                    if notice:
                        wish_notices.append(notice)
                selected_context['activity_finalize'] = activity_finalize
                shared = transaction_pools.setdefault('inc_up_cnt', {})
                exact = make_original_gacha_resolver(tables, rng.randrange, make_treasure,
                    make_table_hero_result(tables, shadow_owned, shadow_fragments),
                    lambda t, n: dict(selected_context,inc_up_cnt=shared))
                card = exact(wire, ordinal, force_s)
                if hero_wish_plan is not None:
                    wish_notices.append(finalize_hero_wish_reveal(transaction_pools,tables,wire,hero_wish_plan,card))
                def resolve_bonus(reward_id,kind,row_id,correction,parent=None):
                    bonus_context = special_pool_context({'gacha_pools':transaction_pools},wire)
                    bonus_context['special_random_reward_ids' if kind=='jiaozhi_threshold' else 'special_common_reward_ids'] = [reward_id]
                    if correction:
                        bonus_context.update(direct_hero_reward=correction,original_common_reward_id=reward_id)
                    bonus_resolver = make_original_gacha_resolver(tables,rng.randrange,make_treasure,
                        make_table_hero_result(tables,shadow_owned,shadow_fragments),lambda t,n:bonus_context)
                    bonus = bonus_resolver(wire,ordinal,False)
                    if parent is not None:
                        parent.setdefault('item',[]).extend(bonus.get('item',[]))
                        parent.setdefault('_gacha_item_trade_types',{}).update(bonus.get('_gacha_item_trade_types',{}))
                    return bonus
                prepare_gacha_activity_bonuses(transaction_pools,tables,wire,ordinal,card,
                    shadow_owned,shadow_fragments,resolve_bonus,wish_notices)
                source = card.get('_gacha_source', {})
                counter = source.get('inc_up_cnt_type')
                if counter is not None:
                    key = str(counter)
                    shared[key] = 0 if source.get('is_up') else shared.get(key, shared.get(counter, 0)) + 1
                for notice_name,notice_payload in wish_notices:
                    if notice_name == 'syncJiaozhiData':
                        notice_payload['i']['iuc'] = [(int(k),v) for k,v in shared.items()]
                return card
            def is_s(card):
                return not card.get('hero_file') and any(tables['hero'].get(h, {}).get('hero_composite_init_rank') == 4 for h in card.get('hero', []))
            if name in ('requestLuckyDrawFile', 'requestLuckyDrawFileAndOpenAll'):
                if not (before_pool or {}).get('group') and (offline_archive_context(pool) or {}).get('expired_restore'):
                    raise ValueError('Existing group retired; explicitly select an archive period or ordinary pool')
                candidate['gacha_pools'], unused = prepare_pool(candidate['gacha_pools'], pool, config, resolver, is_s)
                if not (before_pool or {}).get('group'):
                    hero_period = hero_wish_period_for_group(tables,pool,offline_archive_context() or {})
                    if hero_period:
                        candidate['gacha_pools']['pools'][str(pool)]['group'].setdefault('special_context',{}).update(hero_period)
                if pool == 5 and not (before_pool or {}).get('group'):
                    archive = offline_archive_context() or {}
                    wish_id = archive.get('wish_id') if archive.get('wire_t') == 5 else None
                    if wish_id is not None:
                        if tables['chouka_treasure_wish'].get(wish_id,{}).get('drawType') != 5:
                            raise ValueError('Archive wish period does not belong to original t5')
                        candidate['gacha_pools']['pools']['5']['group']['special_context'] = {'policy':TREASURE_WISH_REVEAL_POLICY,'wish_id':wish_id}
            cards, newly, notices = [], [], []
            if name in ('requestLuckyDrawCard', 'requestLuckyDrawFileAndOpenAll', 'requestLuckyDrawAllLeftCard'):
                saved_pool = candidate['gacha_pools']['pools'].get(str(pool), {})
                group = saved_pool.get('group')
                indices = [parameters.get('idx')] if name == 'requestLuckyDrawCard' else [i for i, card in enumerate((group or {}).get('cards', [])) if not card['is_open']]
                if indices:
                    candidate['gacha_pools'], cards, newly, changed = open_pool_cards(candidate['gacha_pools'], pool, indices,
                        IdManager.genid, lambda item: tables['item_data'][item]['wrap'], credit_items=False, resolver=reveal, is_s=is_s)
                    candidate, rendered, notices = apply_original_gacha_rewards(candidate, newly, IdManager.genid,
                        lambda item: tables['item_data'][item]['wrap'], grant_hero=lambda state, hid: native_default_hero_snapshot(hid),
                        grant_extra=lambda state, extras: self.grant_gacha_extras(state, extras, tables),
                        item_definitions=tables['item_data'], grant_pendant=self.grant_gacha_pendant)
                    rendered_by_index = {card['index']: card for card in rendered}
                    for card in candidate['gacha_pools']['pools'][str(pool)]['group']['cards']:
                        if card['index'] in rendered_by_index:
                            card.update(rendered_by_index[card['index']])
                    saved_pool = candidate['gacha_pools']['pools'][str(pool)]
                    day_key = '%s:%s' % (self.story.get('week', 0), self.story.get('date', 0))
                    if saved_pool.get('day_key') != day_key:
                        saved_pool['day_key'], saved_pool['daily_count'] = day_key, 0
                    saved_pool['daily_count'] = saved_pool.get('daily_count', 0) + len(newly)
                elif name == 'requestLuckyDrawCard':
                    raise ValueError('Invalid original card index')
            if name == 'requestQuitFile':
                candidate['gacha_pools'], unused = quit_pool(candidate['gacha_pools'], pool)
            candidate['gacha']['opened_total'] = pool_opened_total(candidate['gacha_pools'], 1)
            if candidate != previous:
                self.restore_progress(candidate)
                self.save_progress()
                committed = True
            if name == 'requestFile':
                result['info'] = {key: self.native_gacha_card(card) for key, card in pool_file_view(self.gacha_pools, pool).items()}
                result['rt'] = bool(result['info'])
            else:
                result['rt'] = True
            if name == 'requestLuckyDrawCard':
                result['info'] = self.native_gacha_card(cards[0])
                result['prog'] = copy.deepcopy((self.gacha or {}).get('hero_fragment_progress', {}))
            elif name in ('requestLuckyDrawFileAndOpenAll', 'requestLuckyDrawAllLeftCard'):
                result['trwd'] = [self.native_gacha_card(card) for card in cards]
                if 'ffs' in result:
                    result['ffs'] = {str(i): {'index': i, 'is_open': False} for i in range(config['slots'])}
            if any(card.get('get_hero') or card.get('jiaozhi') or card.get('_gacha_bonus_cards') for card in newly):
                notices.append(('syncHeroesData',{'d':hero_snapshots_for_client(self.profile)}))
                if self.profile.get('hero_pending'):
                    notices.append(('syncHeroMgrPendingData',{'d':gacha_pending_for_client(self.profile)}))
            for notice, payload in wish_notices + notices:
                self.reply(notice, payload)
            # Stock success callbacks increment native ct; restore exact persisted
            # counts AFTER replying, including idempotent retry callbacks.
            if not presentation_current:
                if name=='requestFile':self.gacha_store_inactive_file_view(pool,result['info'])
                if callback_id:self.reply('serverCallbackCarrier',{'_r_':True},callback_id)
            else:
                self.reply(reply_name, result, callback_id)
            try:
                self.sync_gacha_native_state(pool, refresh_cards=False)
            except Exception:
                _f7_log('LOCAL GACHA native projection pending: %s' % traceback.format_exc())
            _f7_log('LOCAL ORIGINAL GACHA t=%s operation=%s newly=%s total=%s' % (pool, name, len(newly), pool_opened_total(self.gacha_pools, pool)))
        except Exception:
            if not committed:
                self.restore_progress(previous)
            _f7_log('LOCAL ORIGINAL GACHA rejected: %s' % traceback.format_exc())
            if not committed:
                result['rt'] = False
                if not presentation_current:
                    if callback_id:self.reply('serverCallbackCarrier',{'_r_':True},callback_id)
                else:
                    self.reply(reply_name, result, callback_id)
            try:
                self.sync_gacha_native_state(pool, refresh_cards=False)
            except Exception:
                pass

    def handle_battle_admission(self, parameters, callback_id=None, source_context=None):
        from common.IdManager import IdManager
        import com.data.cdata.mission as mission_data
        scene = parameters.get('s')
        failure = {'t': 0, 's': scene if type(scene) is int else 0, 'f': '', 'h': [], 'd': {}, 'c': {}}
        previous = self.progress_snapshot()
        if source_context is not None:
            if source_context[0] is not self.owner:
                return
            if source_context[1] != flashback_token(previous):
                self.reply('combatOfflineReply', failure, callback_id)
                return
        try:
            if mission_data.data.get(scene, {}).get('system_type') == 4 and source_context is not None:
                captured = source_context[2] if len(source_context) > 2 else None
                current = role_battle_source(previous)
                if captured is None or any(captured.get(k) != current.get(k) for k in ('week','route','day','occurrence','scene','epoch')):
                    raise ValueError('Stale queued ROLE admission source')
            if parameters.get('t') == 2:
                import com.data.cdata.event_content as content
                candidate, changed = prepare_event_battle_admission(previous, parameters, mission_data.data, content.data, IdManager.genid, role_owner=IdManager.id2str(self.owner.id))
            elif scene == 101:
                battle, changed = prepare_first_battle_admission(self.battle, self.profile,
                    self.story, parameters, mission_data.data, IdManager.genid)
                candidate = copy.deepcopy(previous)
                candidate['battle'] = battle
            else:
                stock_day = getattr(getattr(self.owner, 'weeknumData', None), 'daynum', None)
                admission_state = copy.deepcopy(previous)
                normal_tables = self.story_effect_tables()
                if normal_tables.get('chapter_mission_data'):
                    refresh_normal_chapters(admission_state, normal_tables)
                candidate, changed = prepare_stage_admission(admission_state, parameters, mission_data.data,
                    IdManager.genid, stock_day=stock_day)
            active = candidate['battle']['active']
            if active.get('party_kind') == 'trial' and not changed:
                active['combat'] = native_role_combat_data(self.owner, active, mission_data.data[scene])
            if changed:
                active['reward_level'] = self.profile['economy']['level']
                active['combat'] = native_stage_combat_data(self.owner, active, mission_data.data[scene])
            result = dict(copy.deepcopy(active['request']), f=active['fight_id'],
                          c=copy.deepcopy(active['combat']))
            identity = IdManager.id2str(self.owner.id)
            for hero_id in active['request']['h']:
                result['c']['heroes'][str((identity, hero_id))] = copy.deepcopy(
                    result['c']['heroes'][str(('', hero_id))])
        except Exception:
            _f7_log('LOCAL BATTLE admission rejected: %s' % traceback.format_exc())
            self.reply('combatOfflineReply', failure, callback_id)
            offer_paused_role_resume(self)
            return
        if changed or candidate != previous:
            self.restore_progress(candidate)
            try:
                self.save_progress()
            except Exception:
                self.restore_progress(previous)
                self.reply('combatOfflineReply', failure, callback_id)
                raise
        if active.get('party_kind') == 'trial':
            count = dict(event_battle_snapshot(self.progress_snapshot())['ab']).get(scene,0)
            self.reply('setEventBattleStage', {'s':scene,'n':count})
        self.reply('combatOfflineReply', result, callback_id)
        self._battle_resume_offered = active['fight_id']

    def ensure_battle_economy(self):
        if 'economy' not in self.profile:
            previous = copy.deepcopy(self.profile)
            self.profile['economy'] = {'version': 1, 'money': 10000, 'exp': 0, 'level': 1}
            try:
                self.save_progress()
            except Exception:
                self.profile = previous
                raise

    def ensure_day_context(self):
        previous = self.progress_snapshot()
        if flashback_context(previous) is not None:
            self.day_failure_sync(operation, 'flashback_requires_original_nextday_protocol', callback_id)
            return
        candidate = copy.deepcopy(previous)
        values = offline_city_defaults()
        values.update(candidate['story'].get('city_values', {}))
        candidate['story']['city_values'] = values
        candidate['story'].setdefault('route', '1')
        candidate['story'].setdefault('sub_routes', [])
        candidate['story'].setdefault('week_actions_spent', 0)
        candidate['story'].setdefault('action_ledger_source', 'observed-local-transactions-v1')
        candidate['day'].setdefault('actions_spent', 0)
        candidate['day'].setdefault('stock_day', 0)
        candidate, unused = self.enrich_city_plan(candidate, [])
        if candidate != previous:
            self.restore_progress(candidate)
            try:
                self.save_progress()
            except Exception:
                self.restore_progress(previous)
                raise

    def record_action_spend(self, previous, candidate, receipt_id=None):
        old_city = previous.get('story', {}).get('city_values', {})
        new_city = candidate.get('story', {}).get('city_values', {})
        same_week = previous['story'].get('week') == candidate['story'].get('week')
        same_day = previous.get('day', {}).get('stock_day') == candidate.get('day', {}).get('stock_day')
        if not same_week:
            candidate['story']['week_actions_spent'] = 0
            candidate['day']['actions_spent'] = 0
        elif not same_day:
            candidate['day']['actions_spent'] = 0
        elif type(old_city.get('av')) is int and type(new_city.get('av')) is int:
            spent = max(0, old_city['av'] - new_city['av'])
            if spent:
                # Offline ACTIONAFTEREVENT policy: one observed av decrease per
                # accepted transaction.  A failed action never reaches here; a
                # retry/duplicate leaves av unchanged; the ledger receipt id is
                # the second guard.  False means that id was already charged.
                duplicate = False
                commit = globals().get('record_committed_spend')
                if commit is not None:
                    try:
                        result = commit(candidate, spent, receipt_id)
                    except (ValueError, TypeError):
                        # A receipt identity conflict (or otherwise unusable
                        # receipt) means the committed sequence can no longer
                        # prove this charge.  Invalidate the ledger so code 20
                        # returns no number; the action still commits and the
                        # legacy audit counters still advance.
                        invalidate = globals().get('invalidate_action_ledger')
                        if invalidate is not None and isinstance(candidate.get('story'), dict):
                            invalidate(candidate['story'])
                        try:
                            _f7_log('Action ledger invalidated by receipt conflict')
                        except NameError:
                            pass
                        result = None
                    else:
                        duplicate = result is False
                        if result is None:
                            try:
                                _f7_log('Action ledger invalid; code 20 stays unsupported')
                            except NameError:
                                pass
                if not duplicate:
                    candidate['story']['week_actions_spent'] = previous['story'].get('week_actions_spent', 0) + spent
                    candidate['day']['actions_spent'] = previous.get('day', {}).get('actions_spent', 0) + spent
        return candidate

    def enrich_city_plan(self, candidate, notices):
        if candidate.get('story', {}).get('city_areas'):
            normal_tables = self.story_effect_tables()
            if normal_tables.get('chapter_mission_data'):
                notices = list(notices) + refresh_normal_chapters(candidate, normal_tables)
        areas = candidate.get('story', {}).get('city_areas', {})
        if not areas:
            return candidate, notices
        import com.data.cdata.city_development as development
        for key, area in list(areas.items()):
            areas[key] = city_action_area_snapshot(area, development.data)
        refreshed = []
        for name, payload in notices:
            payload = copy.deepcopy(payload)
            if name == 'get_all_area_info_reply':
                city = story_city_snapshot(candidate['story'])
                payload['ais'] = city.pop('areas')
                payload['cd'] = city
            elif name == 'get_area_info_reply':
                key = str(payload['ai']['id'])
                payload['ai'] = copy.deepcopy(areas[key])
            refreshed.append((name, payload))
        return candidate, refreshed

    def city_operation_id(self, sequence):
        namespace = getattr(self, '_city_rpc_namespace', None)
        if namespace is None:
            namespace = str(self.owner.id)
            self._city_rpc_namespace = namespace
        return 'city:%s:%s' % (namespace, sequence)

    def city_failure_reply(self, operation, parameters, callback_id):
        if operation == 'enterPatrolRequest':
            self.reply('enter_patrol_reply', {'s': False, 'rs': False, 'ext': {}, 'ev': []}, callback_id)
            try:
                import gg
                if getattr(gg, 'avatar', None) is self.owner:
                    gg.ui.enable_settlement(True)
            except ImportError:
                pass
        elif operation in ('areaBuildRequest', 'areaLevelUpRequest'):
            reply = 'area_build_reply' if operation == 'areaBuildRequest' else 'area_level_up_reply'
            self.reply(reply, {'rs': False, 'aid': parameters.get('aid', 0), 'ext': {}}, callback_id)
        elif callback_id:
            self.reply('serverCallbackCarrier', {'_r_': {}}, callback_id)

    def handle_city_action(self, operation, parameters, operation_id, callback_id=None, source_context=None):
        if source_context is not None:
            if source_context[0] is not self.owner:
                return
            if source_context[1] != dream_action_token(self.progress_snapshot()):
                self.city_failure_reply(operation, parameters, callback_id)
                return
        from common.IdManager import IdManager
        import com.data.cdata.city_building as buildings
        import com.data.cdata.city_development as development
        import com.data.cdata.city_upgrade as upgrades
        import com.data.cdata.city_patrol as patrol
        import com.data.cdata.hero as heroes
        import com.data.cdata.event_condition as triggers
        import com.data.cdata.event_content as content
        catalogs = {'building': buildings.data, 'development': development.data,
            'upgrade': upgrades.data, 'patrol': patrol.data, 'hero': heroes.data,
            'triggers': triggers.data, 'content': content.data}
        previous = self.progress_snapshot()
        try:
            import com.data.cdata.daerweila_dispatch as dispatch_rows
            catalogs['daerweila_dispatch'] = dispatch_rows.data
            catalogs['dispatch_baseline'] = (getattr(self, '_snapshot_template', {}) or {}).get('std', {})
        except ImportError:
            pass
        try:
            abilities = (native_city_action_abilities(self.owner, parameters.get('hs', []))
                         if operation != 'patrolReward' else None)
            stock_day = getattr(getattr(self.owner, 'weeknumData', None), 'daynum', None)
            candidate, notices, changed, diagnostic = prepare_city_action(previous, operation,
                parameters, catalogs, operation_id, abilities, IdManager.genid, stock_day,
                evaluate_condition=lambda kind, value, state: evaluate_offline_condition(kind, value, state,
                    context={'abilities': abilities}))
            if (candidate.get('city_actions') or {}).get('patrol') and abilities:
                candidate['city_actions']['patrol']['abilities'] = copy.deepcopy(abilities)
            candidate, notices = self.enrich_city_plan(candidate, notices)
            candidate = self.record_action_spend(previous, candidate, 'city:' + operation_id)
            if operation == 'enterPatrolRequest':
                notices = prepare_daerweila_patrol_delivery(candidate, catalogs, notices)
            story_push = None
            if changed and not diagnostic.get('replay'):
                refresh_story_events(candidate,triggers.data,content.data)
                if candidate['available_events']!=previous['available_events'] or candidate['processing_events']!=previous['processing_events']:
                    story_push={'a':copy.deepcopy(candidate['available_events']),'p':copy.deepcopy(candidate['processing_events'])}
            if candidate != previous:
                self.restore_progress(candidate)
                try:
                    self.save_progress()
                except Exception:
                    self.restore_progress(previous)
                    self.city_failure_reply(operation, parameters, callback_id)
                    raise
        except (ValueError, KeyError, TypeError):
            _f7_log('LOCAL CITY action rejected: %s' % traceback.format_exc())
            self.city_failure_reply(operation, parameters, callback_id)
            return
        if diagnostic.get('replay'):
            updated = []
            for name, payload in notices:
                if name == 'notify_add_friendly':
                    continue
                if name == 'syncFlashbackData':
                    payload = flashback_notice(self.progress_snapshot())[1]
                if name == 'syncHuiSuData':
                    payload = huisu_notice(self.progress_snapshot())[1]
                payload = copy.deepcopy(payload)
                if name in ('updateFriendlyValue', 'updateCurFatigueValue'):
                    field = 'ef' if name == 'updateFriendlyValue' else 'cf'
                    payload['v'] = self.profile['heroes'][str(payload['h'])][field]
                updated.append((name, payload))
            candidate, notices = self.enrich_city_plan(self.progress_snapshot(), updated)
        # Native canStartEvent must see branches before patrol UI opens, even
        # when this is a changedFalse same-paid-patrol recovery or replay.
        if operation == 'enterPatrolRequest' and any(name == 'enter_patrol_reply' and body.get('s') for name, body in notices):
            self.sync_daerweila_projection()
            self.reply('pushEvents', {'a': sorted(self.available_events.items()), 'p': sorted(self.processing_events)})
            story_push = None
        for index, (name, payload) in enumerate(notices):
            self.reply(name, payload, callback_id if index == len(notices) - 1 else None)
        if callback_id and not notices:
            self.reply('serverCallbackCarrier', {'_r_': {}}, callback_id)
        if story_push is not None:
            self.reply('pushEvents',story_push)

    def sync_daerweila_projection(self):
        doc = self.story.get('daerweila_dispatch')
        if not doc:
            return
        import gg
        if getattr(gg, 'avatar', self.owner) is not self.owner:
            return
        native = getattr(self.owner, 'storyData', None)
        live_intro = doc['first_devil']['phase'] == 'intro_pending' and getattr(native, 'daerweila_choose_asazile', False)
        for name, body in daerweila_sync_notices(self.progress_snapshot()):
            if name == 'syncDaerweilaLineData' and live_intro:
                body['dca'] = True
            self.reply(name, body)

    def handle_daerweila_first_choice(self, arguments, source, source_owner):
        import gg
        if self.owner is not source_owner or getattr(gg, 'avatar', source_owner) is not source_owner:
            return
        previous = self.progress_snapshot()
        try:
            candidate, changed = prepare_daerweila_first_choice(previous, arguments, self.story_effect_tables(), source)
            if changed:
                self.restore_progress(candidate)
                try:
                    self.save_progress()
                except Exception:
                    self.restore_progress(previous)
                    raise
        except Exception:
            # Original direct empty RPC has no business ack. Correct its
            # optimistic flag on rejection/failure and let the original UI retry.
            for name, body in daerweila_sync_notices(self.progress_snapshot(),
                    (getattr(self, '_snapshot_template', {}) or {}).get('std', {})):
                self.reply(name, body)
            _f7_log('LOCAL DISPATCH first intro pending/rejected: %s' % traceback.format_exc())
            return

    def process_huisu_operation(self, operation, arguments, source_token, callback_id=None,
                                operation_id=None, source_owner=None):
        if source_owner is not None and source_owner is not self.owner:
            return
        previous = self.progress_snapshot()
        try:
            tables = self.story_effect_tables()
            candidate, notices, changed, diagnostic = prepare_huisu_operation(previous,
                operation, arguments, tables, source_token, operation_id)
            refresh_story_events(candidate, tables.get('event_condition', {}), tables.get('event_content', {}))
            if candidate != previous:
                self.restore_progress(candidate)
                try:
                    self.save_progress()
                except Exception:
                    self.restore_progress(previous)
                    raise
            try:
                for name, payload in notices:
                    self.reply(name, payload)
                if candidate['available_events'] != previous['available_events']:
                    self.reply('pushEvents', {'a': candidate['available_events'], 'p': candidate['processing_events']})
            finally:
                # Original reliable request callback only releases its UI lock.
                # It is independent of business success and publication retry.
                if callback_id:
                    pending_callback = callback_id
                    callback_id = None
                    self.reply('serverCallbackCarrier', {'_r_': {}}, pending_callback)
            if diagnostic.get('pending'):
                _f7_log('LOCAL HUISU pending: %r' % diagnostic)
        except (ValueError, KeyError, TypeError):
            if callback_id:
                self.reply('serverCallbackCarrier', {'_r_': {}}, callback_id)
            return
        except Exception:
            if callback_id:
                self.reply('serverCallbackCarrier', {'_r_': {}}, callback_id)
            raise

    def flashback_session_identity(self):
        identity = getattr(self, '_flashback_session_identity', None)
        if identity is None:
            identity = '%s:%s:%s' % (self.owner.id, time.time(), id(self))
            self._flashback_session_identity = identity
        return identity

    def flashback_failure_sync(self, operation):
        if operation != 'requestFlashbackIncDay':
            return
        value = flashback_context(self.progress_snapshot())
        if value is not None:
            # The original empty RPC locks before sending. Unchanged d/v lets
            # its own city animation callback release that lock after refusal.
            self.reply('replyFlashbackIncDay', {'d': value['index'], 'v': value['used_actions']})

    def process_flashback_operation(self, operation, arguments, source_token, callback_id=None,
                                    intent_id=None, source_owner=None):
        if source_owner is not None and source_owner is not self.owner:
            return
        import com.data.cdata.event_content as content
        import com.data.cdata.event_condition as triggers
        previous = self.progress_snapshot()
        try:
            candidate, notices, changed, diagnostic = prepare_flashback_operation(
                previous, operation, arguments, source_token, intent_id)
        except (ValueError, KeyError, TypeError):
            self.flashback_failure_sync(operation)
            _f7_log('LOCAL FLASHBACK rejected: %s' % traceback.format_exc())
            return
        if changed:
            refresh_story_events(candidate, triggers.data, content.data)
            self.restore_progress(candidate)
            try:
                self.save_progress()
            except Exception:
                self.restore_progress(previous)
                self.flashback_failure_sync(operation)
                raise
        for name, payload in notices:
            self.reply(name, payload)
        if callback_id:
            self.reply('serverCallbackCarrier', {'_r_': {}}, callback_id)
        if diagnostic.get('pending'):
            self.flashback_failure_sync(operation)
            _f7_log('LOCAL FLASHBACK not advanced: %r' % diagnostic)

    def day_failure_sync(self, operation, reason, callback_id=None):
        native_day = getattr(getattr(self.owner, 'weeknumData', None), 'daynum', None)
        current = self.day.get('stock_day', native_day)
        if operation == 'statusCheck':
            self.reply('statusCheckReply', {'r': 'fail', 's': 'nextday'}, callback_id)
        elif operation == 'incDayWhenNoActionVal' and type(current) is int:
            # Authoritative unchanged-day synchronization releases the original
            # updateDay UI wait. No daily review, reward or advance is emitted.
            self.reply('updateDay', {'d': current}, callback_id)
        elif callback_id:
            self.reply('serverCallbackCarrier', {'_r_': {}}, callback_id)
        _f7_log('LOCAL DAY not advanced: %r' % reason)
        if operation in ('statusCheck', 'incDayWhenNoActionVal'):
            self.defer(1, lambda: show_day_pending_notice(self, reason))

    def process_day_operation(self, operation, parameters, callback_id=None, source_context=None, huisu_source=None):
        import com.data.cdata.event_content as content
        import com.data.cdata.event_condition as triggers
        import com.data.cdata.fatigue_recover as fatigue
        import com.data.cdata.city_upgrade as upgrades
        previous = self.progress_snapshot()
        candidate = copy.deepcopy(previous)
        values = offline_city_defaults()
        values.update(candidate['story'].get('city_values', {}))
        candidate['story']['city_values'] = values
        candidate['story'].setdefault('route', '1')
        candidate['story'].setdefault('sub_routes', [])
        native_day = getattr(getattr(self.owner, 'weeknumData', None), 'daynum', None)
        stock_day = candidate['day'].get('stock_day', native_day)
        if source_context is not None:
            expected = (candidate['story']['week'], stock_day)
            receipt = candidate['day'].get('receipt')
            replay = (operation == 'incDayWhenNoActionVal' and not candidate['day'].get('intent') and
                      receipt and source_context == (receipt['week'], receipt['day']))
            if source_context != expected and not replay:
                self.day_failure_sync(operation, 'stale-native-day-context', callback_id)
                return
        if operation == 'updateEventCondClient' and huisu_context(candidate, True) is not None:
            if huisu_source is None:
                self.day_failure_sync(operation, 'actual_huisu_intent_identity_required', callback_id)
                return
            try:
                mark_huisu_nextday(candidate, huisu_source[1], huisu_source[0])
            except ValueError:
                self.day_failure_sync(operation, 'stale_huisu_nextday_context', callback_id)
                return
        candidate, blockers = scan_nextday_story_events(candidate, content.data, triggers.data)
        if operation == 'statusCheck':
            unused, future = scan_nextday_story_events(candidate, content.data, triggers.data, prospective_unknown=True)
            blockers.extend(item for item in future if item.get('reason') == 'unknown-reachable-nextday-condition')
        try:
            import gg
            import com.const as const
            if getattr(gg, 'avatar', None) is self.owner:
                if gg.logic.game_state.current != const.GameState.CITY:
                    blockers.append({'reason': 'not-in-city'})
                if gg.ui._dialogue:
                    blockers.append({'reason': 'actual-dialogue-in-progress'})
        except ImportError:
            pass
        plan = None
        if operation == 'incDayWhenNoActionVal' and not blockers:
            plan, provider_diagnostic = build_offline_daily_plan(candidate, fatigue.data, upgrades.data, stock_day)
        try:
            prepared, notices, changed, diagnostic = prepare_gateway_day_operation(candidate,
                operation, parameters, blockers=blockers, plan=plan, stock_day=stock_day, tables=self.story_effect_tables())
            if operation == 'updateEventCondClient' and diagnostic.get('condition_update'):
                facts = dict(prepared.get('conditions', []))
                facts[102] = merge_client_operations(dict(candidate.get('conditions', [])).get(102), 4)
                prepared['conditions'] = [[key, value] for key, value in sorted(facts.items())]
                prepared, after = scan_nextday_story_events(prepared, content.data, triggers.data)
                refresh_story_events(prepared, triggers.data, content.data)
            elif operation == 'incDayWhenNoActionVal' and changed:
                prepared, after = scan_nextday_story_events(prepared, content.data, triggers.data)
                refresh_story_events(prepared, triggers.data, content.data)
            prepared = self.record_action_spend(previous, prepared)
            changed = prepared != previous
            if changed:
                self.restore_progress(prepared)
                try:
                    self.save_progress()
                except Exception:
                    self.restore_progress(previous)
                    self.day_failure_sync(operation, 'local-save-failed', callback_id)
                    raise
        except (ValueError, KeyError, TypeError):
            self.day_failure_sync(operation, 'invalid-or-unsupported-day-state', callback_id)
            return
        if not notices and diagnostic.get('pending'):
            self.day_failure_sync(operation, diagnostic, callback_id)
            return
        if diagnostic.get('pending'):
            _f7_log('LOCAL DAY gated: %r' % diagnostic)
        for index, (name, result) in enumerate(notices):
            self.reply(name, result, callback_id if index == len(notices) - 1 else None)
        if callback_id and not notices:
            self.reply('serverCallbackCarrier', {'_r_': {}}, callback_id)
        if prepared['available_events'] != previous['available_events']:
            self.reply('pushEvents', {'a': list(sorted(self.available_events.items())), 'p': sorted(self.processing_events)})

    def handle_battle_hero_switch(self, parameters):
        active = self.battle.get('active')
        if (not active or parameters.get('t') != active['request']['t'] or parameters.get('s') != active['request']['s'] or
                parameters.get('h') not in active['request']['h']):
            return
        hero_id = parameters['h']
        data = copy.deepcopy(active['combat']['heroes'][str(('', hero_id))])
        self.reply('combatOfflineHeroConfirm', {'h': hero_id, 'd': data})

    def confirm_battle_hero(self, parameters):
        active = self.battle.get('active')
        if (active and parameters.get('t') == active['request']['t'] and parameters.get('s') == active['request']['s'] and
                parameters.get('h') in active['request']['h']):
            # All admitted team heroes are already in the persistent combat
            # snapshot; this acknowledgement grants no new hero or reward.
            _f7_log('LOCAL BATTLE hero confirmed %s' % parameters['h'])

    def reset_pending_battle(self, source_fight_id=None):
        if not self.battle.get('active'):
            return
        if source_fight_id is not None and source_fight_id != self.battle['active']['fight_id']:
            return
        previous = self.progress_snapshot()
        active = self.battle['active']
        self.battle.setdefault('abandoned', []).append(active['fight_id'])
        self.battle['abandoned'] = self.battle['abandoned'][-32:]
        self.battle['active'] = None
        if active.get('event_policy'):
            gate = self.story.get('event_battle_gates', {}).get(active['event_occurrence'])
            if gate and gate.get('fight_id') == active['fight_id']:
                gate['status'], gate['fight_id'] = 'open', None
                if active.get('party_kind') == 'trial':
                    gate['role_episode']['rearm_pending'] = True
        try:
            self.save_progress()
        except Exception:
            self.restore_progress(previous)
            raise
        if active.get('event_policy'):
            self._started_this_session.discard(active['event_id'])
            count = dict(event_battle_snapshot(self.progress_snapshot())['ab']).get(active['request']['s'], 0)
            self.reply('setEventBattleStage', {'s': active['request']['s'], 'n': count})

    def handle_battle_finish(self, parameters, source_fight_id, source_owner=None, source_role=None):
        from common.IdManager import IdManager
        import com.const as const
        import com.data.cdata.city_fight_reward as fight_rewards
        import com.data.cdata.player_exp as player_exp
        import com.data.cdata.reward_random as random_rewards
        import com.data.cdata.reward_common as common_rewards
        import com.data.cdata.hero_treasure as treasure_data
        import com.data.cdata.event_content as event_content
        import com.data.cdata.event_condition as event_condition
        import com.data.cdata.mission as mission_data
        import com.data.cdata.city_data as city_data
        active = self.battle.get('active')
        if source_owner is not None and source_owner is not self.owner:
            return
        if active and active.get('party_kind') == 'trial' and source_role is not None and source_role != role_battle_source(self.progress_snapshot()):
            return
        expected = (active or (self.battle.get('receipts') or [{}])[-1]).get('fight_id')
        if not source_fight_id or source_fight_id != expected:
            _f7_log('LOCAL BATTLE rejected unmatched source fight')
            return
        previous = self.progress_snapshot()

        def settle(admission, actual):
            def grant(template, quality, trade_type):
                return make_table_treasure_reward(template, quality, treasure_data.data,
                    const.CombatAttrs.NAME_TO_INDEX, IdManager.genid, int(time.time()), trade_type)
            return settle_stage_economy(self.profile, admission, actual,
                fight_rewards.data, player_exp.data, random_rewards.data, common_rewards.data,
                grant, mission_data.data[actual['s']])
        try:
            if parameters.get('t') == 2:
                candidate, reply, effects, changed = prepare_event_battle_finish(previous, parameters, settle, source_fight_id,
                    mission_data.data, event_content.data)
            elif parameters.get('s') == 101:
                battle, reply, effects, changed = prepare_battle_finish(self.battle, parameters, settle)
                candidate = copy.deepcopy(previous)
                candidate['battle'] = battle
                if changed:
                    candidate['profile'] = effects['profile']
            else:
                candidate, reply, effects, changed = prepare_stage_finish(previous, parameters,
                    mission_data.data, city_data.data, settle, source_fight_id)
            story_notices = []
            if changed:
                effects.setdefault('notices', []).extend(settle_yumi_herbs(previous, candidate, parameters, active))
                candidate = self.record_action_spend(previous, candidate, 'battle:' + str(source_fight_id))
                if active and (active.get('normal_chapter_source') is not None or
                               active.get('special_city_stage_source') is not None or
                               active.get('city_stage_source') is not None or
                               active.get('condition_mission_root') is not None or
                               active.get('request', {}).get('t') == 2):
                    # Only an accepted actual fight result can offer original
                    # success/fail events. Starting/refreshing a mission cannot.
                    field = 'successEvent' if parameters['w'] == 1 else 'failEvent'
                    if active.get('party_kind') == 'trial' and not parameters['w'] and not effects.get('event_terminal_failure'):
                        field = '_no_terminal_during_role_retry'
                    available = dict(candidate['available_events'])
                    for event in mission_data.data[parameters['s']].get(field, ()):
                        row = event_content.data.get(event, {})
                        if (row.get('release') and event not in candidate['processing_events'] and
                                (event not in candidate['completed_events'] or row.get('repeatable'))):
                            available[event] = 1
                            origins = candidate['story'].setdefault('available_origins', {})
                            if not (str(event) in candidate['story'].get('event_terminal_offers', {}) or
                                    origins.get(str(event), {}).get('source') == 'accepted_mission_result' and
                                    event in dict(previous.get('available_events', []))):
                                origins[str(event)] = {
                                    'source': 'accepted_mission_result', 'fight_id': source_fight_id,
                                    'scene': parameters['s'], 'outcome': parameters['w']}
                                if active.get('party_kind') == 'trial':
                                    origins[str(event)]['party_kind'] = 'trial'
                                    origins[str(event)]['provider'] = ROLE_MISSION_POLICY
                                    origins[str(event)]['role_epoch'] = active['role_epoch']
                    candidate['available_events'] = [[event, value] for event, value in sorted(available.items())]
                if parameters['w'] == 1:
                    if 'current_mission_wins' in candidate['story']:
                        current_wins = set(candidate['story']['current_mission_wins'])
                        current_wins.add(parameters['s'])
                        candidate['story']['current_mission_wins'] = sorted(current_wins)
                    proof = effects.get('event_completion') or {}
                    candidate, story_notices = prepare_story_operation(candidate, 'combat_win',
                        {'k': 'battle', 'd': {'c': parameters['s']}, 'source_event': proof.get('event'),
                         'source_receipt': proof.get('occurrence')}, event_content.data,
                        event_condition.data, self.story_effect_tables())
                    clearance_notices = []
                    if parameters['t'] == 1 and parameters['s'] == 101:
                        candidate, clearance_notices, unused = apply_first_battle_clearance(candidate, mission_data.data)
                    refresh_story_events(candidate, event_condition.data, __import__('com.data.cdata.event_content', fromlist=['data']).data)
                    story_notices = clearance_notices + story_notices
                for name, payload in story_notices:
                    if name == 'completeEventReplyEnd':
                        candidate, unused = complete_city_patrol_event(candidate, payload['e'])
                candidate, effects['notices'] = self.enrich_city_plan(candidate, effects['notices'])
                candidate, story_notices = self.enrich_city_plan(candidate, story_notices)
                self.restore_progress(candidate)
                try:
                    self.save_progress()
                except Exception:
                    self.restore_progress(previous)
                    raise
        except (ValueError, KeyError, TypeError):
            _f7_log('LOCAL BATTLE result rejected: %s' % traceback.format_exc())
            return
        if changed:
            terminal_failure = effects.get('event_terminal_failure')
            if terminal_failure:
                trigger_data = getattr(self.owner, 'eventTriggerData', None)
                remove_processing = getattr(trigger_data, 'delProcessingEvent', None)
                if callable(remove_processing):
                    remove_processing(terminal_failure['event'])
                self._started_this_session.discard(terminal_failure['event'])
                self.reply('pushEvents', {'a':sorted(self.available_events.items()), 'p':sorted(self.processing_events)})
            for name, result in effects['notices']:
                self.reply(name, result)
            if effects['granted']:
                self.reply('updateItems', {'i': self.native_treasure_items(effects['granted'])})
            for name, result in story_notices:
                self.reply(name, result)
        if not changed:
            receipts = self.battle.get('receipts') or []
            if receipts and receipts[-1].get('party_kind') == 'trial':
                count = dict(event_battle_snapshot(self.progress_snapshot())['ab']).get(parameters['s'],0)
                self.reply('setEventBattleStage',{'s':parameters['s'],'n':count})
        native_reply = copy.deepcopy(reply)
        for entry in native_reply['r'].get('treasure', []):
            entry[3] = [IdManager.str2id(uid) for uid in entry[3]]
        self.reply('combatOfflineReward', native_reply)
        if changed and parameters.get('t') == 2 and not parameters.get('w') and active:
            self._started_this_session.discard(active['event_id'])
        if changed:
            self.process_week_handoffs()
            if active and active.get('party_kind') == 'trial' and self.story.get('event_battle_gates',{}).get(active.get('event_occurrence'),{}).get('status') == 'paused':
                offer_paused_role_resume(self)

    def handle_role_giveup(self, parameters, source, source_owner):
        import gg
        if self.owner is not source_owner or getattr(gg,'avatar',None) is not source_owner:
            return
        import com.data.cdata.mission as missions
        import com.data.cdata.event_content as events
        previous = self.progress_snapshot()
        try:
            candidate, notices = prepare_role_giveup(previous, parameters.get('s'), source, missions.data, events.data)
            self.restore_progress(candidate)
            try:
                self.save_progress()
            except Exception:
                self.restore_progress(previous)
                raise
        except (ValueError,KeyError,TypeError):
            return
        failure = candidate['story'].get('event_terminal_failures',{}).get(str(previous['story']['event_battle_gates'][source['occurrence']]['event']))
        if failure:
            trigger = getattr(self.owner,'eventTriggerData',None)
            remove = getattr(trigger,'delProcessingEvent',None)
            if callable(remove):
                remove(failure['event'])
            self._started_this_session.discard(failure['event'])
        for name, payload in notices:
            self.reply(name,payload)
        self.reply('pushEvents', {'a':sorted(self.available_events.items()),'p':sorted(self.processing_events)})
        offer_paused_role_resume(self)

    def reply_area_stages(self, parameters, callback_id=None):
        previous = self.progress_snapshot()
        candidate = copy.deepcopy(previous)
        normal_tables = self.story_effect_tables()
        notices = refresh_normal_chapters(candidate, normal_tables) if normal_tables.get('chapter_mission_data') else []
        if candidate != previous:
            self.restore_progress(candidate)
            try:
                self.save_progress()
            except Exception:
                self.restore_progress(previous)
                raise
        for notice, payload in notices:
            if notice != 'get_area_stages_reply':
                self.reply(notice, payload)
        area_id = parameters.get('aid')
        area = self.story.get('city_areas', {}).get(str(area_id))
        if area and area.get('stage'):
            self.reply('get_area_stages_reply', {'ai': area_id, 'st': copy.deepcopy(area['stage'])},
                       callback_id or parameters.get('_cbid_'))
        else:
            self.reply('serverCallbackCarrier', {'_r_': {}}, callback_id or parameters.get('_cbid_'))

    def reply_city_areas(self, name, parameters, callback_id=None):
        callback_id = callback_id or parameters.get('_cbid_')
        city = story_city_snapshot(self.story)
        if name == 'getAllAreaInfoRequest':
            areas = city.pop('areas')
            self.reply('get_all_area_info_reply', {'ais': areas, 'cd': city, 'sm': False}, callback_id)
            return
        area_id = parameters.get('id')
        area = self.story.get('city_areas', {}).get(str(area_id))
        if area:
            self.reply('get_area_info_reply', {'ai': copy.deepcopy(area)}, callback_id)
        elif callback_id:
            self.reply('serverCallbackCarrier', {'_r_': {}}, callback_id)

    def confirm_story_starter(self, hero_id):
        import com.data.cdata.event_condition as event_condition
        previous = self.progress_snapshot()
        try:
            candidate = prepare_starter_choice(previous, hero_id, event_condition.data)
        except ValueError:
            return False
        self.restore_progress(candidate)
        try:
            self.save_progress()
        except Exception:
            self.restore_progress(previous)
            raise
        self.reply('pushEvents', {'a': list(sorted(self.available_events.items())),
                                  'p': sorted(self.processing_events)})
        if getattr(self, '_starter_initial_offered', False):
            install_story_continue_entry(self)
        return True

    def complete_story_ui(self, event):
        self.process_story('ui_complete', {'e': event})

    def ensure_postbattle_progress(self):
        import com.data.cdata.mission as mission_data
        import com.data.cdata.event_condition as event_condition
        previous = self.progress_snapshot()
        candidate, notices, changed = apply_first_battle_clearance(previous, mission_data.data)
        candidate,budget_changed,budget_diagnostic = prepare_initial_city_budget(candidate)
        if budget_diagnostic.get('reasons') and candidate['story'].get('city_values',{}).get('av') == 0:
            _f7_log('INITIAL BUDGET unchanged: %r'%budget_diagnostic)
        candidate, unused = self.enrich_city_plan(candidate, [])
        refresh_story_events(candidate, event_condition.data, __import__('com.data.cdata.event_content', fromlist=['data']).data)
        if candidate != previous:
            self.restore_progress(candidate)
            try:
                self.save_progress()
            except Exception:
                self.restore_progress(previous)
                raise

    def refresh_story_triggers(self):
        import com.data.cdata.event_condition as event_condition
        previous = self.progress_snapshot()
        candidate = copy.deepcopy(previous)
        refresh_story_events(candidate, event_condition.data, __import__('com.data.cdata.event_content', fromlist=['data']).data)
        if candidate != previous:
            self.restore_progress(candidate)
            try:
                self.save_progress()
            except Exception:
                self.restore_progress(previous)
                raise

    def process_week_handoffs(self):
        if not self.story.get('event_handoffs'):
            return
        import com.data.cdata.event_content as content
        import com.data.cdata.ending_data as endings
        import com.data.cdata.story_route as routes
        previous = self.progress_snapshot()
        candidate = copy.deepcopy(previous)
        notices = []
        consumed = set(candidate['week_protocol'].get('consumed_handoffs', []))
        for receipt, handoffs in sorted(candidate['story'].get('event_handoffs', {}).items()):
            for handoff in handoffs:
                if handoff.get('token') in consumed:
                    continue
                if handoff['kind'] == 'week_result':
                    candidate, replies, changed = prepare_week_result(candidate, handoff, content.data, endings.data)
                elif handoff['kind'] == 'route':
                    candidate, replies, changed = prepare_week_route_handoff(candidate, handoff, content.data, routes.data)
                else:
                    continue
                notices.extend(replies)
                consumed.update(candidate['week_protocol'].get('consumed_handoffs', []))
        normal_tables = self.story_effect_tables()
        if normal_tables.get('chapter_mission_data'):
            notices.extend(refresh_normal_chapters(candidate, normal_tables))
        if candidate != previous:
            import com.data.cdata.event_condition as triggers
            refresh_story_events(candidate, triggers.data, content.data)
            self.restore_progress(candidate)
            try:
                self.save_progress()
            except Exception:
                self.restore_progress(previous)
                raise
        for name, payload in notices:
            self.reply(name, payload)

    def process_week_operation(self, operation, parameters, callback_id=None, source_week=None):
        previous = self.progress_snapshot()
        try:
            if operation == 'updateClientAvatarAsk':
                candidate, notices, changed = prepare_week_avatar_reply(previous,
                    lambda state: build_local_avatar_snapshot(state, self._snapshot_template), pack_original_avatar)
            else:
                origin = self.story['week'] if source_week is None else source_week
                identity = 'week:%s:%s:%s:%s' % (origin, operation, parameters.get('i'), parameters.get('e'))
                replay = (self.week_protocol.get('transition') or {}).get('id') == identity
                if origin != self.story['week'] and not replay:
                    raise ValueError('Stale week transition request')
                tables = self.story_effect_tables()
                for key, name in (('events', 'event_content'), ('endings', 'ending_data'),
                        ('routes', 'story_route'), ('scores', 'mainline_score_info'),
                        ('building', 'city_building'), ('development', 'city_development'),
                        ('missions', 'mission'), ('items', 'item_data')):
                    tables[key] = __import__('com.data.cdata.' + name, fromlist=['data']).data
                authorized = operation in ('handleResetWeekAsk', 'requestEnterStory')
                actual = operation
                if operation == 'handleResetWeek':
                    import com.data.cdata.reset_week_event as reset_events
                    event = parameters.get('e')
                    authorized = replay or (event in self.completed_events and event in reset_events.data)
                    if not authorized:
                        raise ValueError('Automatic reset requires its actual completed original event')
                    actual = 'handleResetWeekAsk'
                candidate, notices, changed = prepare_week_transition(previous, actual, identity, tables,
                    authorized_reset=authorized, route_entry=parameters.get('i'))
                candidate, notices = self.enrich_city_plan(candidate, notices)
            if candidate != previous:
                self.restore_progress(candidate)
                try:
                    self.save_progress()
                except Exception:
                    self.restore_progress(previous)
                    raise
        except Exception:
            _f7_log('LOCAL WEEK pending: %s' % traceback.format_exc())
            if operation in ('requestEnterStory', 'requestEnterStoryByEnding'):
                self.reply('replyEnterStory' if operation == 'requestEnterStory' else 'replyEnterStoryByEnding', {'r': False}, callback_id)
            elif callback_id:
                self.reply('serverCallbackCarrier', {'_r_': {}}, callback_id)
            show_day_pending_notice(self, 'week-transition-not-committed')
            return
        for index, (name, payload) in enumerate(notices):
            if name == 'updateClientAvatarReply' and not callable(getattr(self.owner, 'updateClientAvatarCb', None)):
                self.owner.updateClientAvatarCb = lambda: None
            self.reply(name, payload, callback_id if index == len(notices) - 1 else None)
        if operation == 'updateClientAvatarAsk':
            self._started_this_session.clear()
            if self.gacha_pools:
                self.sync_gacha_native_state(refresh_cards=True)

    def prepare_story_gate(self, state, event):
        import com.data.cdata.event_content as content
        return_value = prepare_event_battle_gate(state, event, content.data, story_occurrence_key(state, event))
        return return_value[0], return_value[1]

    def yumi_request_frame(self):
        import gg
        panel = getattr(getattr(getattr(gg, 'ui', None), 'panels', None), 'storyline_yuni', None)
        city = getattr(gg, 'city_container', None)
        scene = city.get_current_scene() if callable(getattr(city, 'get_current_scene', None)) else None
        return (id(panel), id(getattr(panel, '_node', None)), getattr(panel, 'valid', None), id(scene))

    def yumi_request_source(self, method, arguments, request_id=None, callback_id=None, context=None, remember=True):
        import gg
        import hashlib
        if method not in YUMI_METHODS:
            raise ValueError('Unknown Yumi request contract')
        if not hasattr(self, '_yumi_rpc_namespace'):
            self._yumi_rpc_namespace = hashlib.sha256(os.urandom(32)).hexdigest()
        sequence = getattr(self, '_yumi_sequence', 0) + 1
        self._yumi_sequence = sequence
        ui, generation, lease, tracking = acquire_ui_lock_lease(gg, method)
        tickets = getattr(self, '_yumi_transport_tickets', {})
        key = (method, request_id)
        old = tickets.get(key) if request_id is not None and remember else None
        if lease is None and old is not None and old['ui'] is ui and old['lock_generation'] is generation:
            return old
        context = tuple(context) if context is not None else yumi_context(self.progress_snapshot())
        period = hashlib.sha256(json.dumps(context, separators=(',', ':')).encode('ascii')).hexdigest()
        identity = 'yumi:%s:%s:%s:%s' % (self._yumi_rpc_namespace, method, period,
            request_id if request_id is not None else 'plain:%s' % sequence)
        source = {'owner': self.owner, 'avatar': getattr(gg, 'avatar', self.owner),
            'proxy': getattr(gg, '_f7_avatar_proxy', self), 'context': context,
            'frame': self.yumi_request_frame(), 'arguments': copy.deepcopy(arguments),
            'identity': identity, 'method': method, 'callback_id': callback_id,
            'ui': ui, 'lock_generation': generation, 'lock_lease': lease, 'lock_tracking': tracking,
            'finished': False, 'saved': False}
        if request_id is not None and remember:
            self._yumi_transport_tickets = tickets
            tickets[key] = source
            if len(tickets) > 512:
                for old_key, ticket in list(tickets.items()):
                    if len(tickets) <= 512:
                        break
                    if ticket is not source and ticket['finished']:
                        tickets.pop(old_key, None)
        return source

    def yumi_session_current(self, source):
        import gg
        return (self.owner is source['owner'] and source['avatar'] is source['owner'] and source['proxy'] is self and
            getattr(gg, 'avatar', self.owner) is source['avatar'] and getattr(gg, '_f7_avatar_proxy', self) is self)

    def yumi_source_state(self, source, context=True):
        import gg
        if not self.yumi_session_current(source):
            return 'owner'
        if context and source['context'] != yumi_context(self.progress_snapshot()):
            return 'route-week'
        if self.yumi_request_frame() != source['frame']:
            return 'presentation'
        return ui_lock_lease_state(gg, source)

    def finish_yumi_source(self, source, saved=False, notify=False):
        import gg
        try:
            if saved and self.yumi_session_current(source) and source['context'] == yumi_context(self.progress_snapshot()):
                # Read-only sync uses current canonical state, never an old
                # receipt's pre-later-operation d, and emits no medicine event.
                self.reply('syncBaiyuInfos', {'d': yumi_projection(self.story)})
        finally:
            complete_ui_lock_lease(gg, source)
            source['finished'] = True
        if notify and saved and self.yumi_session_current(source):
            notice = getattr(getattr(getattr(getattr(gg, 'ui', None), 'panels', None), 'common_message', None), 'notify_message', None)
            if callable(notice):
                notice(u'\u64cd\u4f5c\u7ed3\u679c\u5df2\u4fdd\u5b58\uff0c\u8bf7\u91cd\u65b0\u8fdb\u5165\u67e5\u770b')

    def fail_yumi_source(self, source):
        import gg
        try:
            if self.yumi_source_state(source, context=False) is None:
                # Original rsn=2 specifically claims insufficient herbs/drugs;
                # a stale source or failed save uses original generic failure.
                payload = {'rs': False, 'i': {'rsn': 1, '_type': source['arguments'].get('t')}}
                # Original plain requests have no callback. Deliver the actual
                # typed consumer, not a carrier pretending the action succeeded.
                deliver_ui_lock_reply(gg, source,
                    lambda: getattr(source['owner'], source['method'] + 'Reply')(payload))
        finally:
            complete_ui_lock_lease(gg, source)
            source['finished'] = True

    def handle_yumi(self, method, arguments, identity, source, callback_id=None):
        import gg
        if not isinstance(source, dict):
            # Preserve direct host/older internal API without inferring player
            # clicks from argument equality or labeling them transport retries.
            owner, context = source
            if owner is not self.owner:
                return
            source = self.yumi_request_source(method, arguments, 'legacy:%s' % identity,
                callback_id, context, remember=False)
        if source['finished']:
            self.finish_yumi_source(source, source['saved'])
            return
        state = self.yumi_source_state(source)
        if state == 'delivering':
            return
        if state is not None:
            self.fail_yumi_source(source)
            return
        previous = self.progress_snapshot()
        try:
            candidate, payload, changed = prepare_yumi_operation(previous, method,
                source['arguments'], source['identity'], source['context'])
            if not changed:
                if candidate != previous:
                    raise ValueError('Yumi replay cannot alter canonical state')
                source['saved'] = True
                self.finish_yumi_source(source, saved=True)
                return
            self.restore_progress(candidate)
            self.save_progress()
            source['saved'] = True
            if self.yumi_source_state(source) is not None:
                self.finish_yumi_source(source, saved=True, notify=True)
                return
            # Direct typed CLIENT_STUB invocation keeps decoder/consumer errors
            # observable here; the common finally still completes its lease.
            deliver_ui_lock_reply(gg, source,
                lambda: getattr(source['owner'], method + 'Reply')(copy.deepcopy(payload)))
            source['finished'] = True
        except Exception:
            if source['saved']:
                _f7_log('LOCAL YUMI saved result retained; presentation failed: %s' % traceback.format_exc())
                self.finish_yumi_source(source, saved=True, notify=True)
            else:
                self.restore_progress(previous)
                _f7_log('LOCAL YUMI not committed: %s' % traceback.format_exc())
                self.fail_yumi_source(source)

    def handle_daily_wish_read(self, arguments, token, owner):
        if owner is not self.owner:return
        previous=self.progress_snapshot()
        try:
            import com.data.cdata.daily_wish as wishes
            candidate,changed=prepare_daily_wish_read(previous,arguments,token,wishes.data)
            if changed:
                self.restore_progress(candidate)
                try:self.save_progress()
                except Exception:
                    self.restore_progress(previous)
                    raise
        except Exception:
            _f7_log('LOCAL DAILY WISH read rejected: %s'%traceback.format_exc())
        self.reply(*daily_wish_notice(self.story))

    def handle_daily_wish_choice(self, arguments, token, callback_id=None):
        previous=self.progress_snapshot()
        try:
            import com.data.cdata.event_content as content
            import com.data.cdata.hero as heroes
            candidate,changed=prepare_daily_wish_choice(previous,arguments,token,content.data,heroes.data)
            if changed:
                self.restore_progress(candidate)
                try:self.save_progress()
                except Exception:
                    self.restore_progress(previous)
                    raise
        except Exception:
            _f7_log('LOCAL DAILY WISH choice rejected: %s'%traceback.format_exc())
        self.reply(*daily_wish_notice(self.story))
        if callback_id:self.reply('serverCallbackCarrier',{'_r_':{}},callback_id)
        if not daily_wish_choice_committed(self.progress_snapshot()):self.offer_daily_wish_retry(token)

    def offer_daily_wish_retry(self, token):
        import gg
        owner=self.owner
        marker=object()
        def current():
            state=self.progress_snapshot()
            return (self.owner is owner and getattr(gg,'avatar',None)is owner and getattr(gg,'_f7_avatar_proxy',None)is self
                and 8078 in self.processing_events and token==daily_choice_token(state) and not daily_wish_choice_committed(state))
        if not current() or getattr(self,'_daily_wish_retry',None)is not None:return
        self._daily_wish_retry=marker
        def cancel():
            if getattr(self,'_daily_wish_retry',None)is marker:self._daily_wish_retry=None
        def selected():
            started=time.time()
            def reopen():
                if getattr(self,'_daily_wish_retry',None)is not marker or not current():cancel();return
                panels=gg.ui.panels
                promise=getattr(panels,'promise_main',None)
                confirm=getattr(panels,'common_confirm',None)
                busy=(getattr(promise,'valid',False)and getattr(promise,'visible',False))or getattr(confirm,'visible',False)or bool(getattr(gg.ui,'_dialogue',None))
                if busy:
                    if time.time()-started<5:self.defer(50,reopen)
                    else:cancel()
                    return
                cancel()
                owner.startEventUI(8078)
            self.defer(1,reopen)
        try:
            gg.ui.panels.common_confirm.notify_confirm(u'\u9009\u62e9\u672a\u4fdd\u5b58\uff0c\u5267\u60c5\u4ecd\u5728\u7b49\u5f85\u672c\u6b21\u9009\u62e9\u3002',selected,
                confirm_label=u'\u91cd\u65b0\u9009\u62e9',cancel_cb=cancel)
        except (AttributeError,TypeError):cancel()

    def story_effect_tables(self):
        result = {}
        for name in ('reward_common', 'notepad', 'city_data', 'mission', 'cg_data',
                     'item_data', 'hero_treasure', 'hero', 'skin', 'private_msg',
                     'social_msg', 'story_clue_info', 'city_building', 'city_development',
                     'intelligence','intelligence_affect','daily_wish','story_dream','event_content','event_condition','city_area_link_data','chapter_mission_data','daerweila_dispatch'):
            try:
                result[name] = __import__('com.data.cdata.' + name, fromlist=['data']).data
            except ImportError:
                pass
        try:
            from com.const import CombatAttrs
            result['attr_indices'] = CombatAttrs.NAME_TO_INDEX
            import com.const as stage_const
            result['coc_scenes'] = sorted(set(stage_const.COC_HERO_LIMIT_SCENE))
        except (ImportError, AttributeError):
            pass
        return result

    def handle_intelligence(self,operation,parameters,callback_id=None):
        callback_id = callback_id or parameters.get('_cbid_')
        previous = self.progress_snapshot()
        arguments = dict(parameters)
        if 'uuid' in arguments:
            arguments['uuid'] = str(arguments['uuid'])
        def restore_rejected_handle():
            if operation == 'handleIntelligenceRequest':
                import gg
                restore = getattr(getattr(gg,'ui',None),'enable_settlement',None)
                if callable(restore):
                    restore(True)
        try:
            tables = self.story_effect_tables()
            tables['event_content'] = __import__('com.data.cdata.event_content',fromlist=['data']).data
            candidate,notices,changed = prepare_intelligence_operation(previous,operation,arguments,tables)
            candidate,notices = self.enrich_city_plan(candidate,notices)
            if candidate != previous:
                self.restore_progress(candidate)
                try:
                    self.save_progress()
                except Exception:
                    self.restore_progress(previous)
                    raise
        except (ValueError,KeyError,TypeError):
            _f7_log('LOCAL INTELLIGENCE not committed: %s'%traceback.format_exc())
            restore_rejected_handle()
            if operation == 'handleIntelligenceRequest':
                self.reply(*intelligence_sync_notice(previous))
            if callback_id:
                self.reply('serverCallbackCarrier',{'_r_':False},callback_id)
            return
        except Exception:
            restore_rejected_handle()
            raise
        if operation == 'handleIntelligenceRequest' and not any(name == 'handleIntelligenceSuccess' for name,payload in notices):
            restore_rejected_handle()
            if not any(name == 'syncAllIntelligence' for name,payload in notices):
                notices.insert(0,intelligence_sync_notice(candidate))
        for name,payload in notices:
            self.reply(name,payload)
        if callback_id:
            self.reply('serverCallbackCarrier',{'_r_':{}},callback_id)

    def process_story(self, operation, arguments, callback_id=None):
        import com.data.cdata.event_content as event_content
        import com.data.cdata.event_condition as event_condition
        import com.data.cdata.reward_common as reward_common
        try:
            state = self.progress_snapshot()
            # Import only missing current-week original clue/lock fields. This
            # is a migration seed, never inferred quest completion or a reset.
            native = getattr(self.owner, 'storyData', None)
            native_week = getattr(getattr(self.owner, 'weeknumData', None), 'weeknum', None)
            if native is not None and native_week == state['story'].get('week'):
                for field in ('wuluClue', 'wuluClueReaded', 'wuluDetailReaded',
                              'daerweila_human_lock', 'daerweila_devil_lock'):
                    value = getattr(native, field, None)
                    if field not in state['story'] and value is not None:
                        if field == 'wuluDetailReaded' and isinstance(value, dict):
                            value = list(value.items())
                        state['story'][field] = copy.deepcopy(value)
            if state.get('gacha') is None:
                state['gacha'] = new_gacha_state()
            promise_callback = operation in ('callback','ui_complete') and arguments.get('e')==8078 and arguments.get('token','ui:8078')=='ui:8078'
            promise_trace = operation=='trace' and arguments.get('k')=='ui' and (arguments.get('d')or{}).get('c')==4
            if 8078 in self.processing_events and (promise_callback or promise_trace) and not daily_wish_choice_committed(state):
                self.reply(*daily_wish_notice(self.story))
                if callback_id:self.reply('serverCallbackCarrier',{'_r_':{}},callback_id)
                self.offer_daily_wish_retry(daily_choice_token(state))
                return
            candidate, notices = prepare_story_operation(state, operation,
                arguments, event_content.data, event_condition.data, self.story_effect_tables())
            with_gates = []
            for name, payload in notices:
                if name == 'startEventReply' and payload.get('r'):
                    candidate, gates = self.prepare_story_gate(candidate, payload['e'])
                    with_gates.extend(gates)
                with_gates.append((name, payload))
                if name == 'completeEventReplyEnd':
                    candidate, unused = complete_city_patrol_event(candidate, payload['e'])
            candidate, notices = self.enrich_city_plan(candidate, with_gates)
        except (ValueError, KeyError, TypeError):
            if operation == 'external':
                self.reply('triggerExternalEventReply', {})
            if callback_id:
                self.reply('serverCallbackCarrier', {'_r_': {}}, callback_id)
            return
        previous = self.progress_snapshot()
        if candidate != previous:
            self.restore_progress(candidate)
            try:
                self.save_progress()
            except Exception:
                self.restore_progress(previous)
                if operation == 'external':
                    self.reply('triggerExternalEventReply', {})
                if callback_id:
                    self.reply('serverCallbackCarrier', {'_r_': {}}, callback_id)
                raise
        for name, result in notices:
            if name == 'startEventReply' and result.get('r') and result.get('e') not in self.processing_events:
                # This batch already committed completion/abandonment. Do not
                # start stale UI; independent reliable callbacks still follow.
                continue
            if operation == 'option' and name == 'startEventReply' and callback_id:
                self.reply('serverCallbackCarrier', {'_r_': {}}, callback_id)
                callback_id = None
            self.reply(name, result)
        # A completed trace/effect retry repairs a lost notice by absolute
        # projection. Never sync the committed after-count ahead of a new add.
        if not any(name == 'offlineDaerweilaAward' for name, result in notices):
            self.sync_daerweila_projection()
        if callback_id:
            self.reply('serverCallbackCarrier', {'_r_': {}}, callback_id)
        self.process_week_handoffs()
        offer_story_starter_choice(self)

    def trace_event(self, arguments):
        self.process_story('trace', arguments)


class LocalGate(object):
    def disconnect(self):
        pass

    def register_on_event_callback(self, event, callback):
        pass

    def unregister_on_event_callback(self, event, callback):
        pass


def create_avatar(logic):
    import gg
    from common.EntityFactory import EntityFactory
    from common.IdManager import IdManager
    previous_proxy = getattr(gg, '_f7_avatar_proxy', None)
    if previous_proxy is not None:
        previous_proxy.destroy()
    try:
        snapshot = SnapshotDict({
            'st': int(time.time()), 'name': u'\u79bb\u7ebf\u6307\u6325\u4f7f', 'an': u'offline',
            'uid': 1, 'sv': 1, 'role': 1, 'level': 1, 'money': 10000,
            'weeknum': SnapshotDict({'w': 0, 'd': 0, 'c': {}, 'l': {}}),
            'sd': SnapshotDict({'sm': {}, 'pm': {}}),
            'intelligence': SnapshotDict(),
            # A local empty base-room scheme, not an official server fixture.
            # knownScheme contains player_home; omitting its scheme causes the
            # stock city red-dot check to unpack None from checkSchemeTypeUnlock.
            'fnd': {'s': {'player_home': {'cur': 1, 1: {'t': 'player_home', 'e': {}}}},
                    'kns': ['player_home'], 'cst': 'player_home'},
            'heromgr': SnapshotDict({'hrs': [
                (hero_id, SnapshotDict({'sl': 1, 'so': 1, 'cf': 100,
                    'ar': SnapshotDict(), 'ef': 0, 'ti': SnapshotDict(), 'cat': None}))
                for hero_id in (24, 20, 27)], 'cfs': None}),
        })
        avatar = EntityFactory.instance().create_entity('ClientAvatar', IdManager.genid())
        proxy = LocalProxy(logic, avatar, persistent=True)
        gg._f7_avatar_proxy = proxy
        avatar.set_server(proxy)
        profile = ensure_initial_hero_profile(proxy)
        proxy.ensure_treasure_inventory()
        proxy.ensure_battle_economy()
        proxy.ensure_day_context()
        proxy.ensure_postbattle_progress()
        profile = proxy.profile
        snapshot.update({key: profile['economy'][key] for key in ('money', 'exp', 'level')})
        snapshot['np'] = copy.deepcopy(proxy.story['notes'])
        snapshot['weeknum'] = story_week_snapshot(proxy.story, proxy.day)
        snapshot['std'] = {'rt': proxy.story.get('route', '1'), 'srt': copy.deepcopy(proxy.story.get('sub_routes', []))}
        snapshot['reward'] = story_reward_snapshot(proxy.story)
        snapshot['city'] = native_city_snapshot(proxy.story)
        pending = gacha_pending_for_client(profile,snapshot.get('heromgr',{}))
        snapshot['heromgr'] = {'hrs': hero_snapshots_for_client(profile), 'cfs': None}
        snapshot['heromgr'].update(pending)
        snapshot['bs'] = event_battle_snapshot(proxy.progress_snapshot())
        if proxy.player_name:
            snapshot['name'] = proxy.player_name
        snapshot['eventTrigger'] = {'ae': list(proxy.available_events.items()),
                                    'pe': list(proxy.processing_events),
                                    'ecm': list(proxy.completed_events),
                                    'gle': [], 'ecd': {}}
        snapshot['std']['ed'] = copy.deepcopy(proxy.story.get('endings', []))
        snapshot = apply_event_effects_snapshot(proxy.progress_snapshot(), snapshot)
        snapshot['intelligence'] = native_intelligence_data(proxy.story.get('intelligence',{'is':[],'rd':False}))
        migrated = migrate_gateway_gacha_state(proxy.progress_snapshot())
        if migrated != proxy.progress_snapshot():
            proxy.restore_progress(migrated)
            proxy.save_progress()
        snapshot = gacha_economy_projection(proxy.progress_snapshot(), snapshot)
        snapshot['ldd'] = gacha_snapshot_projection(proxy.progress_snapshot(), snapshot.get('ldd', {}), proxy.gacha_tables()['chouka_info'])
        snapshot['ldd'].update(item_exchange_limits(proxy.progress_snapshot(),proxy._item_exchange_clock()))
        _f7_log('Loading a local ClientAvatar snapshot')
        avatar.init_from_dict(snapshot)
        proxy.install_item_exchange_limit_check()
        proxy._snapshot_template = copy.deepcopy(snapshot)
        proxy.sync_gacha_native_state(refresh_cards=True)
        with open(os.path.join(_f7_doc, 'offline_initial_snapshot.json'), 'w') as handle:
            json.dump(snapshot, handle, ensure_ascii=True, indent=2,
                      default=lambda value: list(value) if isinstance(value, set) else repr(value))
        avatar.on_entity_creation()
        import com.data.cdata.event_content as local_event_content
        with open(os.path.join(_f7_doc, 'offline_initial_events.json'), 'w') as handle:
            json.dump({key: dict(value) for key, value in local_event_content.data.items()
                       if 1000 <= key <= 1050}, handle, ensure_ascii=True, indent=2,
                      default=repr)
        _f7_log('ClientAvatar created; entering player state')
        avatar.on_become_player()
        proxy.sync_gacha_items()
        if proxy.week_protocol.get('awaiting_avatar'):
            proxy.defer(1, lambda: proxy.process_week_operation('updateClientAvatarAsk', {}))
        elif proxy.week_protocol.get('result'):
            for name, payload in proxy.week_protocol['result'].get('notices', []):
                if name == 'showWeekResult':
                    proxy.defer(1, lambda payload=copy.deepcopy(payload): proxy.reply('showWeekResult', payload))
        proxy.defer(1, proxy.process_week_handoffs)
        offer_story_starter_choice(proxy)
        offer_pending_battle_resume(proxy)
        offer_paused_role_resume(proxy)
        install_development_probe()
        offer_offline_entry()
    except:
        _f7_log(traceback.format_exc())
        traceback.print_exc()
        try:
            with open(os.path.join(_f7_doc, 'offline_partial_snapshot.json'), 'w') as handle:
                json.dump(snapshot, handle, ensure_ascii=True, indent=2,
                          default=lambda value: list(value) if isinstance(value, set) else repr(value))
        except:
            _f7_log('Could not serialize partial development snapshot')


def local_gate_connect(self):
    import gg
    import com.const as const
    from common.EntityFactory import EntityFactory
    from common.IdManager import IdManager
    try:
        self.gate_client = LocalGate()
        self.gate_timer = None
        account = EntityFactory.instance().create_entity('ClientAccount', IdManager.genid())
        account.set_server(LocalProxy(self, account))
        account.init_from_dict({})
        account.on_entity_creation()
        _f7_log('Local ClientAccount created')
        self.online_state.transition(const.OnlineState.LOGIN)
    except:
        _f7_log(traceback.format_exc())
        raise


def local_enter_login(self, source, data):
    import gg
    gg.username = 'offline'
    gg.display_name = u'\u79bb\u7ebf\u6307\u6325\u4f7f'
    gg.server_current = LocalWorld()
    gg.lost_server = False
    self.clear_client_exception()
    _f7_log('Bypassing login UI; connecting the in-process gateway')
    self.game_login()


def install_gateway():
    import game3d
    import logic.logic_state as state
    import logic.logic_init as initialization
    import cocos.ui_manager as ui_manager

    def skip_startup_op(self, ctrl_mode):
        import gg
        _f7_log('Skipping startup OP while testing local player initialization')
        gg.exec_delay(1, self.movie_done)

    state.Member.gs_enter_login = local_enter_login
    state.Member.gate_connect = local_gate_connect
    initialization.Member.movie_play = skip_startup_op
    def use_png_interface(self):
        import C_file
        # Both formats are shipped by the original game. Emulator GLES reports
        # ASTC support but rejects the actual compressed texture uploads.
        C_file.set_path_patch('cocos', 'cocos')
        _f7_log('Using the original PNG interface assets')

    ui_manager.UIManager.init_astc_modifer = use_png_interface
    # Android 11 can return null for the legacy process enumeration API;
    # the original JNI bridge aborts the VM in that case. Offline play has no
    # remote process-inspection service, so do not enter that native API.
    game3d.get_running_process = lambda: []
    install_tutorial_bypass()
    install_story_ui_compatibility()
    install_story_completion_observers()
    install_native_story_callbacks()
    install_ending_request_guard()
    install_puzzle_refusal_guard()
    install_remaining_wardrobe_ui()
    install_gacha_ui()
    install_gacha_entry_guard()
    install_gacha_dedicated_costs()
    install_gacha_archive()
    _f7_log('In-process gateway callbacks installed')


def install_development_probe():
    """Opt-in, app-local test commands; absent from ordinary startup."""
    import gg
    if not os.path.isfile(os.path.join(_f7_doc, 'offline_development.flag')):
        return
    install_local_purge_recovery(gg)
    gg._f7_probe_rearm = install_development_probe
    import com.const as const
    entry = gg.logic.game_state._cb[const.GameState.CITY]['enter']
    original_enter_city = entry['func']
    if original_enter_city is not None and not getattr(original_enter_city, '_f7_probe_city_hook', False):
        def enter_city_with_probe(*args, **kwargs):
            result = original_enter_city(*args, **kwargs)
            install_development_probe()
            return result
        enter_city_with_probe._f7_probe_city_hook = True
        entry['func'] = enter_city_with_probe
    generation = getattr(gg, '_f7_probe_generation', 0) + 1
    gg._f7_probe_generation = generation

    def poll():
        if gg._f7_probe_generation != generation:
            return
        command = os.path.join(_f7_doc, 'offline_probe.py')
        if os.path.isfile(command):
            last_command = command + '.last'
            os.rename(command, last_command)
            try:
                eval(compile(open(last_command, 'rb').read(), command, 'exec'), globals(), globals())
                _f7_log('Development command completed')
            except:
                _f7_log('Development command failed: %s' % traceback.format_exc())
        gg.exec_delay(1000, poll)

    gg.exec_delay(1000, poll)
