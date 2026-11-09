import gg, time
# Empty-condition events finish only after their native UI/movie/guide pipeline.
import entity.avatar_members.EventTriggerMember as _q7_event_member
import com.data.cdata.event_content as _q7_event_content
import com.const as _q7_const

# The server may replay startEventReply for an event the client already
# accepted (duplicate reliable request, reconnect, reload). The native lock is a
# plain counter owned only by completeEventDialog, so every replay used to stack
# another `wait_reward` reference whose only release had already been consumed.
# One record per event occurrence now owns at most one reference; replays are
# no-ops until the occurrence is retired, and a stalled echo is retried.
_Q7_CONTINUATION_STALL = 8.0

# `gg.ui._lock['wait_reward']` is global, so the reference has one owner even
# when a reconnect or a retry leaves two avatar objects with live records.
# Ownership is a token: a claim revokes the previous owner, and a release is a
# no-op unless it still holds the current token. That prevents an old avatar's
# echo or reconnect save from unlocking the panel a newer avatar claimed.
# Registry is bound once to the stable gg module, not recreated by re-exec.
Q7_CLIENT_EVENT_COMPAT_VERSION = 7
print('P7_CLIENT_EVENT_COMPAT version=7')
_q7_wait_reward_owner = None
_q7_wait_reward_token = None
_q7_wait_reward_state = None

def _q7_records(avatar):
    records = getattr(avatar, '_q7_settlement_continuations', None)
    if records is None:
        records = {}
        avatar._q7_settlement_continuations = records
    return records

def _q7_wait_reward_locked():
    is_lock = getattr(gg.ui, 'is_lock', None)
    try:
        if is_lock is not None:
            return bool(is_lock('wait_reward'))
        return bool((getattr(gg.ui, '_lock', None) or {}).get('wait_reward', 0))
    except Exception:
        return False

def _q7_wait_reward_registry():
    state = getattr(gg, '_q7_wait_reward_registry_v5', None)
    if state is None:
        state = {'owner': {'token': 0, 'record': None, 'avatar': None, 'event': None},
                 'token': [0], 'version': 7,
                 'legacy_untracked': _q7_wait_reward_locked()}
        setattr(gg, '_q7_wait_reward_registry_v5', state)
    else:
        # Keep the existing owner/token across compat re-exec; only upgrade the
        # marker so native logs identify the loaded patch.
        state['version'] = 7
    return state

def _q7_clear_wait_reward_owner(state=None):
    target = (state or _q7_wait_reward_state)['owner']
    target['token'] = 0
    target['record'] = None
    target['avatar'] = None
    target['event'] = None

_q7_wait_reward_state = _q7_wait_reward_registry()
_q7_wait_reward_owner = _q7_wait_reward_state['owner']
_q7_wait_reward_token = _q7_wait_reward_state['token']

def _q7_entry_valid(avatar, event, record):
    return bool(record is not None and not record.get('retired') and
                getattr(gg, 'avatar', None) is avatar and
                _q7_records(avatar).get(event) is record and
                getattr(getattr(avatar, 'weeknumData', None), 'weeknum', None) == record.get('week'))


def _q7_guarded_entry(name, original):
    def wrapped(self, event, *args, **kwargs):
        record = _q7_records(self).get(event)
        if not _q7_entry_valid(self, event, record):
            return None
        return original(self, event, *args, **kwargs)
    return wrapped


def _q7_start_event_ui(self, event):
    record = _q7_records(self).get(event)
    if record is not None and not _q7_entry_valid(self, event, record):
        return None
    data = _q7_event_content.data.get(event, {})
    ui_info = data.get('ui')
    if ui_info:
        panel, func = ui_info[:2]
        avatar = self
        occurrence = record.get('occurrence') if record is not None else None
        week = record.get('week') if record is not None else getattr(getattr(self, 'weeknumData', None), 'weeknum', None)
        def callback(*args, **kwargs):
            if (record is None or getattr(gg, 'avatar', None) is not avatar or
                    getattr(getattr(avatar, 'weeknumData', None), 'weeknum', None) != week or
                    _q7_records(avatar).get(event) is not record or
                    record.get('occurrence') is not occurrence):
                return None
            return avatar.startMovie(event)
        return getattr(getattr(gg.ui.panels, panel), func)(event, cb=callback, *ui_info[2:])
    return self.startMovie(event)


def _q7_capture_leave_callback(avatar, event, record, callback):
    occurrence = record.get('occurrence') if record is not None else None
    week = record.get('week') if record is not None else getattr(getattr(avatar, 'weeknumData', None), 'weeknum', None)
    def guarded(*args, **kwargs):
        if (record is None or
                getattr(gg, 'avatar', None) is not avatar or
                getattr(getattr(avatar, 'weeknumData', None), 'weeknum', None) != week or
                _q7_records(avatar).get(event) is not record or
                record.get('occurrence') is not occurrence):
            return None
        return callback(*args, **kwargs)
    return guarded


def _q7_start_caidan_scene(self, event):
    record = _q7_records(self).get(event)
    if not _q7_entry_valid(self, event, record):
        return None
    container = getattr(gg, 'city_container', None)
    original_get = getattr(container, 'get_scene_by_key', None)
    captured = []
    if callable(original_get):
        def get_scene(key):
            scene = original_get(key)
            setter = getattr(scene, 'setLeaveCallback', None)
            if callable(setter):
                captured.append((scene, setter))
                def set_leave(callback, scene=scene, setter=setter):
                    return setter(_q7_capture_leave_callback(self, event, record, callback))
                scene.setLeaveCallback = set_leave
            return scene
        container.get_scene_by_key = get_scene
    try:
        return self._q7_original_start_caidan_scene(event)
    finally:
        if callable(original_get):
            container.get_scene_by_key = original_get
        for scene, setter in reversed(captured):
            scene.setLeaveCallback = setter


def _q7_start_puzzle_room(self, event):
    record = _q7_records(self).get(event)
    if not _q7_entry_valid(self, event, record):
        return None
    room = getattr(gg, 'puzzle_room', None)
    setter = getattr(room, 'setLeaveCallback', None)
    if callable(setter):
        def set_leave(callback):
            return setter(_q7_capture_leave_callback(self, event, record, callback))
        room.setLeaveCallback = set_leave
    try:
        return self._q7_original_start_puzzle_room(event)
    finally:
        if callable(setter):
            room.setLeaveCallback = setter


def _q7_start_movie(self, event):
    # Capture the actual callback handed to play_movie. The guard protects the
    # full original rewardAfterMovie chain (leave + semaphore + battle) without
    # patching global leave_emergency or retaining a global movie owner.
    record = _q7_records(self).get(event)
    avatar = self
    logic = getattr(gg, 'logic', None)
    occurrence = record.get('occurrence') if record is not None else None
    week = record.get('week') if record is not None else getattr(getattr(self, 'weeknumData', None), 'weeknum', None)
    try:
        import cutils.chelpers as chelpers
    except Exception:
        chelpers = getattr(_q7_event_member, 'chelpers', None)
    original_play = getattr(chelpers, 'play_movie', None)
    if not callable(original_play):
        return self._q7_original_start_movie(event)

    def guarded_play(movie, callback, *args, **kwargs):
        def guarded_callback(*cb_args, **cb_kwargs):
            if (record is None or getattr(gg, 'avatar', None) is not avatar or
                    getattr(gg, 'logic', None) is not logic or
                    record.get('occurrence') is not occurrence or
                    getattr(getattr(avatar, 'weeknumData', None), 'weeknum', None) != week or
                    _q7_records(avatar).get(event) is not record):
                return None
            return callback(*cb_args, **cb_kwargs)
        return original_play(movie, guarded_callback, *args, **kwargs)

    if '_q7_original_play_movie' not in chelpers.__dict__:
        chelpers._q7_original_play_movie = original_play
    chelpers.play_movie = guarded_play
    try:
        return self._q7_original_start_movie(event)
    finally:
        chelpers.play_movie = original_play


def _q7_install_movie_guard(avatar_class):
    if '_q7_original_start_movie' not in avatar_class.__dict__:
        original = avatar_class.startMovie
        avatar_class._q7_original_start_movie = getattr(original, 'im_func', original)
    avatar_class.startMovie = _q7_start_movie


def _q7_acquire_wait_reward(avatar, event, record):
    # One owned reference is transferred with ownership; a legacy lock is never
    # adopted and never duplicated per transfer.
    state = record.get('_q7_reward_state') or _q7_wait_reward_state
    owner = state['owner']
    previous = owner.get('record')
    state['token'][0] += 1
    token = state['token'][0]
    record['_q7_reward_state'] = state
    inherited = previous is not None and previous is not record
    if inherited:
        record['unlock_on_release'] = previous.get('unlock_on_release', True)
        previous['unlock_on_release'] = False
        previous['lock'] = False
        previous['token'] = None
    record['lock'] = True
    record['token'] = token
    owner['record'] = record
    owner['token'] = token
    owner['avatar'] = id(avatar)
    owner['event'] = event
    if not inherited:
        if _q7_wait_reward_locked():
            if state.get('legacy_untracked'):
                gg.ui.lock('wait_reward')
            record['unlock_on_release'] = True
        else:
            gg.ui.lock('wait_reward')
            record['unlock_on_release'] = True
    return True

def _q7_release_wait_reward(record, reclaim_orphan=False):
    state = (record or {}).get('_q7_reward_state') or _q7_wait_reward_state
    owner = state['owner']
    if record is not None:
        token = record.get('token')
        owns = bool(token) and owner.get('token') == token and owner.get('record') is record
        record['lock'] = False
        record['token'] = None
        if owns:
            _q7_clear_wait_reward_owner(state)
            if record.get('unlock_on_release', True):
                gg.ui.unlock('wait_reward')
            record['unlock_on_release'] = False
            return True
        # Revoked/transferred: the current owner keeps the reference.
        if not reclaim_orphan:
            return False
    if reclaim_orphan and not owner.get('token') and not state.get('legacy_untracked') and _q7_wait_reward_locked():
        # A native lock taken before this asset loaded has no owner at all.
        gg.ui.unlock('wait_reward')
        return True
    return False

def _q7_release_whole_event(record):
    if not record or not record.pop('whole_event', False):
        return False
    logic = record.get('whole_event_logic')
    if logic is None:
        return False
    semaphore = getattr(logic, 'event_semaphore', None) or {}
    count = semaphore.get('wholeEvent', 0) if hasattr(semaphore, 'get') else 0
    if isinstance(count, int) and count <= 0:
        return False
    try:
        logic.enable_event('wholeEvent', check=False)
    except TypeError:
        logic.enable_event('wholeEvent')
    record['whole_event_logic'] = None
    return True


def _q7_cancel_continuation(avatar, event, phase='cancelled'):
    records = _q7_records(avatar)
    record = records.pop(event, None)
    if record is None:
        return None
    record['phase'] = phase
    handler = record.pop('handler', None)
    if handler:
        record['bus'].del_event_handler(_q7_const.GameEvent.SETTLEMENT_END, handler)
    _q7_release_wait_reward(record)
    _q7_release_whole_event(record)
    return record

def _q7_maybe_retire(avatar, event, record):
    if not record or record.get('retired'):
        return False
    if not (record.get('server_completed') and record.get('native_pipeline_done')):
        return False
    records = _q7_records(avatar)
    if records.get(event) is not record:
        return False
    record['retired'] = True
    records.pop(event, None)
    handler = record.pop('handler', None)
    if handler:
        record['bus'].del_event_handler(_q7_const.GameEvent.SETTLEMENT_END, handler)
    _q7_release_wait_reward(record)
    _q7_release_whole_event(record)
    return True


def _q7_release_continuations(avatar):
    records = _q7_records(avatar)
    for event in list(records):
        _q7_cancel_continuation(avatar, event)

def _q7_reconcile_wait_reward(avatar):
    # A continuation whose avatar object is gone leaves the global panel lock
    # behind. Reclaim it only when this avatar provably owns no reference.
    if avatar is None:
        return
    if _q7_wait_reward_state.get('legacy_untracked'):
        return
    if _q7_wait_reward_state['owner'].get('token'):
        return
    records = getattr(avatar, '_q7_settlement_continuations', None) or {}
    if not any(record.get('lock') for record in records.values()):
        if getattr(gg, 'avatar', None) is avatar and _q7_wait_reward_locked():
            gg.ui.unlock('wait_reward')

def _q7_native_rpc_body(method):
    rpcmethod = getattr(method, 'rpcmethod', None)
    body = getattr(rpcmethod, 'func', None)
    if body is not None:
        return body
    return getattr(method, 'im_func', method)

def _q7_complete_base(self, event):
    # startEventReply has already disabled wholeEvent before completeBase. Capture
    # that exact acquisition here; End may arrive before the dialog record exists.
    records = _q7_records(self)
    record = records.get(event)
    logic = getattr(gg, 'logic', None)
    week = getattr(getattr(self, 'weeknumData', None), 'weeknum', None)
    if record is None:
        record = records[event] = {'phase': 'base', 'lock': False, 'bus': None,
                                   'handler': None, 'since': time.time(),
                                   'whole_event': True, 'whole_event_logic': logic,
                                   'occurrence': object(), 'week': week,
                                   'server_completed': False,
                                   'native_pipeline_done': False}
    else:
        record.setdefault('whole_event_logic', logic)
        record.setdefault('week', week)
        record.setdefault('occurrence', object())
        if record.get('whole_event', False):
            record['whole_event_logic'] = record.get('whole_event_logic') or logic
    return self._q7_original_complete_base(event)


def _q7_complete_event_dialog(self, event):
    records = _q7_records(self)
    previous = records.get(event)
    if previous is not None and not previous.get('retired'):
        phase = previous.get('phase')
        if phase == 'created':
            if (not previous.get('server_completed') and
                    time.time() - previous.get('since', 0) >= _Q7_CONTINUATION_STALL):
                _q7_cancel_continuation(self, event, 'retried')
                record = None
            else:
                return
        elif phase in ('created', 'waiting', 'finished', 'caidan'):
            return
        elif phase in ('server_only', 'base'):
            record = previous
        else:
            return
    else:
        record = None
    if record is None:
        record = {'phase': 'created', 'lock': False, 'bus': None, 'handler': None,
                  'since': time.time(), 'whole_event': True,
                  'whole_event_logic': getattr(gg, 'logic', None),
                  'occurrence': object(),
                  'week': getattr(getattr(self, 'weeknumData', None), 'weeknum', None),
                  'server_completed': False, 'native_pipeline_done': False}
        records[event] = record
    else:
        record['phase'] = 'created'
        record['since'] = time.time()
        # Preserve a wholeEvent acquired by completeBase/server-only; never
        # disown it merely because the dialog record was reused.
        record.setdefault('whole_event', True)
        record.setdefault('whole_event_logic', getattr(gg, 'logic', None))
        record.setdefault('occurrence', object())
        record.setdefault('week', getattr(getattr(self, 'weeknumData', None), 'weeknum', None))
    record['echo_started'] = True
    # Preserve the native echo/dialogue barrier; completion follows UI/movie work.
    def continue_event(args):
        if records.get(event) is not record:
            return
        if gg.avatar is not self:
            _q7_cancel_continuation(self, event, 'superseded')
            return
        self.startSettlement(event)
    gg.city.touchable = True
    try:
        data = _q7_event_content.data[event]
    except KeyError:
        records.pop(event, None)
        raise
    _q7_acquire_wait_reward(self, event, record)
    if 'dialog' in data and not self.eventTriggerData.selectedEvent:
        self.clientTraceProcessingEvent('dialog', data['dialog'], callback=continue_event)
    else:
        self.callServerMethodReliable('reliableEcho', {}, callback=continue_event)

def _q7_start_settlement(self, event):
    records = _q7_records(self)
    record = records.get(event)
    adopted = record is None
    if record is None:
        record = records[event] = {'phase': 'created', 'lock': False, 'bus': None,
                                  'handler': None, 'since': time.time(),
                                  'whole_event': False, 'occurrence': object(),
                                  'week': getattr(getattr(self, 'weeknumData', None), 'weeknum', None),
                                  'server_completed': False, 'native_pipeline_done': False}
    if gg.avatar is not self:
        _q7_cancel_continuation(self, event, 'superseded')
        return
    if record.get('phase') not in ('created', 'server_only'):
        _q7_release_wait_reward(record, reclaim_orphan=adopted)
        return
    _q7_release_wait_reward(record, reclaim_orphan=adopted)
    record['phase'] = 'waiting'
    record['since'] = time.time()
    self._q7_pipeline_record = record

    def done(*args):
        handler = record.pop('handler', None)
        if handler:
            record['bus'].del_event_handler(_q7_const.GameEvent.SETTLEMENT_END, handler)
        if record['phase'] != 'waiting':
            return
        record['phase'] = 'caidan'
        record['settlement_done'] = True
        if gg.avatar is self and records.get(event) is record:
            self.startCaidanScene(event)

    if gg.ui._procing_settlement:
        record['bus'] = gg.event
        record['handler'] = done
        gg.event.add_event_handler(_q7_const.GameEvent.SETTLEMENT_END, done)
    else:
        done()

def _q7_start_event_reply(self, event, result):
    # A replay for a live occurrence is not a second start: it would disable
    # `wholeEvent` again and restack the native lock with no paired release.
    if result:
        record = _q7_records(self).get(event)
        if record is not None and not record.get('retired') and (
                record.get('phase') in ('created', 'waiting', 'finished', 'caidan')
                or record.get('server_completed')):
            if (record.get('phase') == 'created' and not record.get('server_completed') and
                    time.time() - record.get('since', 0) >= _Q7_CONTINUATION_STALL):
                _q7_cancel_continuation(self, event, 'retried')
            else:
                return
    return self._q7_original_start_event_reply(event, result)

def _q7_complete_event_reply_end(self, event):
    records = _q7_records(self)
    record = records.get(event)
    if record is None and event in getattr(self.eventTriggerData, 'processingEventsClient', ()):
        record = records[event] = {'phase': 'server_only', 'lock': False, 'bus': None,
                                   'handler': None, 'since': time.time(),
                                   'whole_event': False,
                                   'whole_event_logic': getattr(gg, 'logic', None),
                                   'occurrence': object(),
                                   'week': getattr(getattr(self, 'weeknumData', None), 'weeknum', None),
                                   'server_completed': False, 'native_pipeline_done': False}
    if record is not None and not record.get('retired'):
        record['server_completed'] = True
    try:
        return self._q7_original_complete_event_reply_end(event)
    finally:
        if record is not None:
            _q7_maybe_retire(self, event, record)

def _q7_start_event(self, event):
    records = _q7_records(self)
    record = records.get(event)
    if record is not None and not record.get('retired'):
        phase = record.get('phase')
        if phase in ('created', 'waiting', 'caidan', 'finished', 'server_only'):
            # Only a created record that never got its echo is a safe retry.
            # Waiting settlement, Caidan, and movie can legitimately exceed the
            # wall-clock stall window; never cancel them here.
            if (phase == 'created' and not record.get('server_completed') and
                    time.time() - record.get('since', 0) >= _Q7_CONTINUATION_STALL):
                _q7_cancel_continuation(self, event, 'retried')
            else:
                return False
        else:
            _q7_release_whole_event(record)
            records.pop(event, None)
    return self._q7_original_start_event(event)

def _q7_avatar_client_data_save(self, *args, **kwargs):
    # Ordinary updateClientAvatarReply mutates the same self; do not cancel a
    # live continuation there. Only a retired avatar object releases its own
    # records before its callbacks disappear.
    if getattr(gg, 'avatar', None) is not self:
        _q7_release_continuations(self)
    return self._q7_original_avatar_client_data_save(*args, **kwargs)

def _q7_reset_story_continuations(self):
    # Only the server's committed week entrance invokes this. An ordinary
    # avatar refresh/reconnect must keep the current story's native callbacks.
    # Each record releases only the references it can prove; a second pending
    # count would release foreign owners' remaining wholeEvent references.
    _q7_release_continuations(self)
    self._q7_finishing_ui_event = None
    self._q7_finishing_ui_record = None
    self._q7_pipeline_record = None

def _q7_update_day(self, day):
    # A rejection/retry sends the current day to release the native UI lock.
    # It is not another calendar transition and must not replay its animation.
    if day == self.weeknumData.daynum:
        gg.ui.unlock('updateDay')
        panel = getattr(gg.ui.panels, 'city', None)
        if panel and panel.valid:
            panel.next_day.setBright(True)
        return
    return self._q7_original_update_day(day)
def _q7_start_event_battle(self, event):
    self._q7_finishing_ui_event = event
    record = getattr(self, '_q7_pipeline_record', None)
    self._q7_pipeline_record = None
    if record is None:
        record = _q7_records(self).get(event)
    self._q7_finishing_ui_record = record
    return self._q7_original_start_event_battle(event)

def _q7_start_check_newbee(self):
    event = getattr(self, '_q7_finishing_ui_event', None)
    record = getattr(self, '_q7_finishing_ui_record', None)
    self._q7_finishing_ui_event = None
    self._q7_finishing_ui_record = None
    owns_record = record is not None and _q7_records(self).get(event) is record
    if event in self.eventTriggerData.processingEventsClient:
        data = _q7_event_content.data.get(event, {})
        if data and not data.get('dialog') and not data.get('completeConds') and not data.get('enterBattle'):
            if owns_record:
                if record.get('phase') == 'waiting':
                    record['phase'] = 'finished'
                self.callServerMethodReliable('q7CompleteUiEvent', {'e': event})
    try:
        result = self._q7_original_start_check_newbee()
    except Exception:
        # The native terminal did not complete: preserve the record and its
        # ownership so reconnect/week cancellation can release it correctly.
        raise
    if owns_record:
        # The original terminal released wholeEvent successfully. Only now mark
        # the native pipeline done and disown the released reference.
        record['whole_event'] = False
        record['native_pipeline_done'] = True
        _q7_maybe_retire(self, event, record)
    return result

def _q7_install_ui_event_bridge(avatar_class):
    # GameObjectMeta snapshots member functions onto ClientAvatar.
    avatar_class._q7_reset_story_continuations = _q7_reset_story_continuations
    if '_q7_original_complete_event_dialog' not in avatar_class.__dict__:
        complete = avatar_class.completeEventDialog
        avatar_class._q7_original_complete_event_dialog = getattr(complete, 'im_func', complete)
    avatar_class.completeEventDialog = _q7_complete_event_dialog
    if '_q7_original_start_settlement' not in avatar_class.__dict__:
        settlement = avatar_class.startSettlement
        avatar_class._q7_original_start_settlement = getattr(settlement, 'im_func', settlement)
    avatar_class.startSettlement = _q7_start_settlement
    if '_q7_original_update_day' not in avatar_class.__dict__:
        update = avatar_class.updateDay
        avatar_class._q7_original_update_day = getattr(update, 'im_func', update)
    avatar_class.updateDay = _q7_update_day
    if '_q7_original_start_check_newbee' not in avatar_class.__dict__:
        battle = avatar_class.startEventBattle
        check = avatar_class.startCheckNewbee
        avatar_class._q7_original_start_event_battle = getattr(battle, 'im_func', battle)
        avatar_class._q7_original_start_check_newbee = getattr(check, 'im_func', check)
    avatar_class.startEventBattle = _q7_start_event_battle
    avatar_class.startCheckNewbee = _q7_start_check_newbee
    if '_q7_original_start_event' not in avatar_class.__dict__:
        start = avatar_class.startEvent
        avatar_class._q7_original_start_event = getattr(start, 'im_func', start)
    avatar_class.startEvent = _q7_start_event
    if '_q7_original_avatar_client_data_save' not in avatar_class.__dict__:
        save = avatar_class.avatarClientDataSave
        avatar_class._q7_original_avatar_client_data_save = getattr(save, 'im_func', save)
    avatar_class.avatarClientDataSave = _q7_avatar_client_data_save
    if '_q7_original_start_event_reply' not in avatar_class.__dict__:
        avatar_class._q7_original_start_event_reply = _q7_native_rpc_body(avatar_class.startEventReply)
    avatar_class.startEventReply = _q7_event_member.rpc_method(_q7_event_member.CLIENT_STUB,
        (_q7_event_member.Int('e'), _q7_event_member.Int('r')))(_q7_start_event_reply)
    if '_q7_original_complete_event_reply_end' not in avatar_class.__dict__:
        avatar_class._q7_original_complete_event_reply_end = _q7_native_rpc_body(avatar_class.completeEventReplyEnd)
    avatar_class.completeEventReplyEnd = _q7_event_member.rpc_method(_q7_event_member.CLIENT_STUB,
        (_q7_event_member.Int('e'),))(_q7_complete_event_reply_end)
    _q7_install_movie_guard(avatar_class)
    if '_q7_original_complete_base' not in avatar_class.__dict__:
        avatar_class._q7_original_complete_base = avatar_class.completeBase
    avatar_class.completeBase = _q7_complete_base
    if '_q7_original_start_event_ui' not in avatar_class.__dict__:
        avatar_class._q7_original_start_event_ui = avatar_class.startEventUI
    avatar_class.startEventUI = _q7_start_event_ui
    for name, attr, wrapper in (
            ('startCaidanScene', '_q7_original_start_caidan_scene', _q7_start_caidan_scene),
            ('startPuzzleRoom', '_q7_original_start_puzzle_room', _q7_start_puzzle_room)):
        if attr not in avatar_class.__dict__ and hasattr(avatar_class, name):
            setattr(avatar_class, attr, getattr(avatar_class, name))
        setattr(avatar_class, name, wrapper)
    _q7_reconcile_wait_reward(gg.avatar)

_q7_install_ui_event_bridge(type(gg.avatar))
gg.avatar.callServerMethod('evalEcho', {'m': 'q7_native_ui_event_finish_v5'})

# Keep area-event completion outside the fullscreen panel's transient cb field.
import com.const as _q7_const
import cocos.panels.settlement_fullscreen as _q7_area_settlement

def _q7_notify_area_event(self, event, *areas, **kwargs):
    avatar = gg.avatar
    callback = kwargs.get('cb')
    opens, fights = [], []
    if not _q7_const.DEBUG_OFFLINE:
        for area in areas:
            area = int(area)
            info = avatar.cityData.get_area_info(area)
            if not info or not info.get('st'):
                continue
            if info['st'][0] == _q7_const.CityStatus.FREE:
                opens.append(area)
            else:
                fights.append(area)
    if (_q7_const.StoryRouteConst.ZHOUNIAN2_WEEK_REFRESH_EVENTID
            in avatar.eventTriggerData.completedEvents or avatar.storyData.change_week):
        fights = []
    batches = []
    if opens:
        if gg.ui.panels.battle_stage.valid:
            gg.ui.panels.battle_stage.visible_self_layer(False)
        batches.append(('notify_settlement_area_open', 'area_open', opens))
    if fights:
        batches.append(('notify_settlement_area_fight', 'area_fight', sorted(fights)))
    self.cb = None
    if not batches:
        if callback and gg.avatar is avatar:
            callback()
        return
    for index, (method, kind, values) in enumerate(batches):
        done = (avatar, callback) if index == len(batches) - 1 else None
        gg.ui.add_settlement('settlement_fullscreen', method, kind, values, _q7_area_done=done)
    gg.ui.proc_settlement()

def _q7_notify_settlement_area_open(self, stype, areas, _q7_area_done=False):
    result = self._q7_original_settlement_area_open(stype, areas)
    if _q7_area_done is not False:
        self._q7_area_done = _q7_area_done
        self.cb = None
    return result

def _q7_notify_settlement_area_fight(self, stype, areas, _q7_area_done=False):
    result = self._q7_original_settlement_area_fight(stype, areas)
    if _q7_area_done is not False:
        self._q7_area_done = _q7_area_done
        self.cb = None
    return result

def _q7_area_settlement_ended(self):
    done = getattr(self, '_q7_area_done', None)
    self._q7_area_done = None
    result = self._q7_original_area_settlement_ended()
    if done:
        avatar, callback = done
        if callback and gg.avatar is avatar:
            callback()
    return result

if not hasattr(_q7_area_settlement.Panel, '_q7_original_area_settlement_ended'):
    _q7_area_settlement.Panel._q7_original_settlement_area_open = _q7_area_settlement.Panel.notify_settlement_area_open
    _q7_area_settlement.Panel._q7_original_settlement_area_fight = _q7_area_settlement.Panel.notify_settlement_area_fight
    _q7_area_settlement.Panel._q7_original_area_settlement_ended = _q7_area_settlement.Panel.settlement_ended
    _q7_area_settlement.Panel.notify_area_event = _q7_notify_area_event
    _q7_area_settlement.Panel.notify_settlement_area_open = _q7_notify_settlement_area_open
    _q7_area_settlement.Panel.notify_settlement_area_fight = _q7_notify_settlement_area_fight
    _q7_area_settlement.Panel.settlement_ended = _q7_area_settlement_ended

gg.avatar.callServerMethod('evalEcho', {'m': 'q7_area_event_completion_v1'})

# Report native diary state without changing its layout or rendering contract.
import cocos.panels.diary_hero as _q7_diary_hero

def _q7_diary_report(message):
    try:
        gg.avatar.callServerMethod('evalEcho', {'m': message})
    except Exception:
        pass

def _q7_diary_refresh(self):
    notes = gg.avatar.notepadData.playerNote
    _q7_diary_report('q7_diary_view_v1 style=%s count=%s last=%s' % (
        getattr(self, 'style', ''), len(notes), notes[-1] if notes else 0))
    try:
        return self._q7_original_diary_refresh()
    except Exception:
        import traceback
        _q7_diary_report('q7_diary_render_failed_v1\n' + traceback.format_exc())
        raise

if not hasattr(_q7_diary_hero.Panel, '_q7_original_diary_refresh'):
    _q7_diary_hero.Panel._q7_original_diary_refresh = _q7_diary_hero.Panel.refresh
    _q7_diary_hero.Panel.refresh = _q7_diary_refresh

# Scene scrolling can run while on_load is still constructing the city widgets.
import cocos.panels.city as _q7_city_panel

def _q7_city_load(self, *args, **kwargs):
    self._q7_city_widgets_ready = False
    result = self._q7_original_city_load(*args, **kwargs)
    self._q7_city_widgets_ready = True
    return result

def _q7_city_destroy(self, *args, **kwargs):
    self._q7_city_widgets_ready = False
    return self._q7_original_city_destroy(*args, **kwargs)

def _q7_city_update(self, *args, **kwargs):
    if not self.valid or not getattr(self, '_q7_city_widgets_ready', True):
        return
    if not hasattr(self, 'xinwu_frame'):
        return
    return self._q7_original_city_update(*args, **kwargs)

def _q7_city_white_love(self):
    if not self.valid or not getattr(self, '_q7_city_widgets_ready', True):
        return
    # Also support the panel already created before this login patch arrives.
    if not hasattr(self, 'visible_semaphore') or not hasattr(self, 'whiteLove_showd'):
        return
    love = getattr(self, 'whiteLove', None)
    if love is None or getattr(love, '_node', None) is None:
        return
    return self._q7_original_city_white_love()

def _q7_install_city_lifecycle(panel_class, panel):
    if '_q7_original_city_load' not in panel_class.__dict__:
        panel_class._q7_original_city_load = panel_class.on_load
        panel_class._q7_original_city_destroy = panel_class.on_destroy
        panel_class._q7_original_city_white_love = panel_class.update_whiteLove_info
        panel_class.on_load = _q7_city_load
        panel_class.on_destroy = _q7_city_destroy
        panel_class.update_whiteLove_info = _q7_city_white_love
    if '_q7_original_city_update' not in panel_class.__dict__:
        panel_class._q7_original_city_update = panel_class.on_update
        panel_class.on_update = _q7_city_update
    # on_init stores bound methods, so an existing event handler must be rebound.
    handlers = getattr(panel, 'event_handlers', None)
    if handlers is not None and 'update_love_mark' in handlers:
        handlers['update_love_mark'] = panel.update_whiteLove_info

_q7_install_city_lifecycle(_q7_city_panel.Panel, getattr(gg.ui.panels, 'city', None))
gg.avatar.callServerMethod('evalEcho', {'m': 'q7_city_widgets_lifecycle_v2'})

# Only server-managed room visits change the native reset/dedup behavior.
import com.data.cdata.puzzle_room_clue as _q7_puzzle_clues

def _q7_puzzle_snapshot(self):
    snapshot = getattr(self, '_q7_puzzle_snapshot', None)
    if not isinstance(snapshot, tuple) or len(snapshot) != 4:
        return None
    week, event, visit, room = snapshot
    if event not in (4229, 6228, 7346) or visit < 1 or week < 0:
        return None
    if _q7_event_content.data.get(event, {}).get('puzzle_room') != room:
        return None
    return snapshot

def _q7_puzzle_sync(self, data):
    snapshot = _q7_puzzle_snapshot(self)
    if snapshot is None:
        return self._q7_original_puzzle_sync(data)
    allowed = set(clue for clue, row in _q7_puzzle_clues.data.items()
        if row['room_id'] == snapshot[3])
    if not isinstance(data, (list, tuple)) or any(type(clue) is not int for clue in data) or len(set(data)) != len(data) or not set(data).issubset(allowed):
        raise ValueError('invalid managed puzzle clue snapshot')
    result = self._q7_original_puzzle_sync(data)
    self.storyData.puzzle_room_clues = list(data)
    if getattr(self, '_q7_puzzle_last_snapshot', None) != snapshot:
        self._q7_puzzle_requested = None
        self._q7_puzzle_inflight = None
    self._q7_puzzle_last_snapshot = snapshot
    return result

def _q7_puzzle_unlock_touch(self, *args, **kwargs):
    result = self._q7_original_puzzle_unlock_touch(*args, **kwargs)
    avatar = gg.avatar
    inflight = getattr(avatar, '_q7_puzzle_inflight', None)
    if inflight is not None and inflight[2] is self:
        avatar._q7_puzzle_inflight = None
    return result

def _q7_puzzle_request(self, clue):
    snapshot = _q7_puzzle_snapshot(self)
    scene = getattr(gg, 'jiemi', None)
    if snapshot is not None and scene is not None:
        scene_class = type(scene)
        if '_q7_original_puzzle_unlock_touch' not in scene_class.__dict__:
            unlock = scene_class.unlock_touch
            scene_class._q7_original_puzzle_unlock_touch = getattr(unlock, 'im_func', unlock)
            scene_class.unlock_touch = _q7_puzzle_unlock_touch
        self._q7_puzzle_requested = (snapshot, clue, scene)
    return self._q7_original_puzzle_request(clue)

def _q7_puzzle_reply(self, result, clue, get_cg):
    snapshot = _q7_puzzle_snapshot(self)
    if snapshot is None:
        return self._q7_original_puzzle_reply(result, clue, get_cg)
    requested = getattr(self, '_q7_puzzle_requested', None)
    inflight = getattr(self, '_q7_puzzle_inflight', None)
    row = _q7_puzzle_clues.data.get(clue, {})
    if not result or row.get('room_id') != snapshot[3] or clue in self.storyData.puzzle_room_clues:
        gg.ui.unlock('puzzleRoomGetClue')
        # A duplicate during the original dialogue/animation must not unlock touch.
        if inflight is None and requested is not None and requested[:2] == (snapshot, clue):
            scene = getattr(gg, 'jiemi', None)
            if scene is requested[2]:
                scene.unlock_touch()
            self._q7_puzzle_requested = None
        return
    if requested is not None and requested[:2] == (snapshot, clue):
        self._q7_puzzle_inflight = requested
        self._q7_puzzle_requested = None
    return self._q7_original_puzzle_reply(result, clue, get_cg)

def _q7_puzzle_cg_rewards(self, reward):
    token = getattr(self, '_q7_puzzle_reward_context', None)
    self._q7_puzzle_reward_context = None
    snapshot = _q7_puzzle_snapshot(self)
    managed = isinstance(token, tuple) and len(token) == 4 and snapshot is not None
    managed = managed and token[:3] == snapshot[:3] and token[3] == 2 and snapshot[3] == 1
    if not managed:
        return self._q7_original_puzzle_cg_rewards(reward)
    seen = getattr(self, '_q7_puzzle_cg_seen', None)
    if seen is None:
        seen = self._q7_puzzle_cg_seen = set()
    if token in seen:
        return
    result = self._q7_original_puzzle_cg_rewards(reward)
    seen.add(token)
    return result

def _q7_install_puzzle_bridge(avatar_class):
    for original, replacement, method in (
        ('_q7_original_puzzle_sync', _q7_puzzle_sync, 'syncPuzzleRoomClue'),
        ('_q7_original_puzzle_request', _q7_puzzle_request, 'puzzleRoomGetClue'),
        ('_q7_original_puzzle_reply', _q7_puzzle_reply, 'puzzleRoomGetClueReturn'),
        ('_q7_original_puzzle_cg_rewards', _q7_puzzle_cg_rewards, 'cgRewards')):
        if original not in avatar_class.__dict__:
            native_method = getattr(avatar_class, method)
            setattr(avatar_class, original, getattr(native_method, 'im_func', native_method))
        setattr(avatar_class, method, replacement)

_q7_install_puzzle_bridge(type(gg.avatar))
gg.avatar.callServerMethod('evalEcho', {'m': 'q7_puzzle_room_bridge_v1'})
