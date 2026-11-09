# -*- coding: utf-8 -*-
"""Typed, non-mutating rejection contracts for audited missing RPC handlers.

This is explicit lack of support, not an implementation of these businesses.
Only proved negative consumers or exact unlock-only callbacks are registered. Never
route a request here before checking real handlers, or infer success from ACK.
"""

import copy


RPC_TYPED_REJECTION_OPERATIONS = frozenset((
    'requestTryPlayBattle', 'requestRandomRealtimeGiftBag', 'buyRealtimeGiftBag',
    'incHeroStarOrder', 'upgradeTreasure', 'upgradeTreasureTargetLv',
    'requestExchangeSuipianWithItem', 'requestExchangeActivityHeroProg',
    'giveCatFriendly', 'requestAddAxiliyaMood', 'requestCaijianOp',
    'requestGetAxiliyaHero',
    'zhaiRequest', 'requestRecoverJingshenli', 'puzzleRoomGetClue',
    'requestChangeAVGLevel', 'requestTriggerEventByEnding', 'requestMainlineCgRewards',
))
RPC_CALLBACK_REJECTION_OPERATIONS = frozenset((
    'yjtFragmentExchange', 'commonItemFusionAsk', 'requestGetHero', 'getCatHero',
    'requestTriggerDaXuanWo', 'actionRewardRequest',
))
RPC_REJECTION_OPERATIONS = RPC_TYPED_REJECTION_OPERATIONS | RPC_CALLBACK_REJECTION_OPERATIONS

# This request has neither a callback nor a negative business reply. The exact
# original caller owns this fixed lock; releasing it must not replace hfp or
# invoke replyProgressHeroFile (which navigates even for empty rewards).
RPC_LOCAL_REJECTION_LOCKS = {
    'changeProgressingHero': 'changeProgressingHero',
    'requestMainlineTotalScores': 'requestMainlineTotalScores',
    'playerDestroyBuilding': 'building_destroy',
    'battleYazhiAsk': 'yazhi',
}


def prepare_rpc_rejection(name, parameters, callback_id=None):
    """Return original negative reply/carrier, payload, truthful notice, or None.

    No inventory, counters, costs, rewards, story, or save state is consulted or
    changed. UUID is echoed: original Uuid accepts the native ID or wire string,
    and None for a malformed/missing ID; the h=-1 branch never uses that ID.
    """
    if name not in RPC_REJECTION_OPERATIONS:
        return None
    args = parameters if isinstance(parameters, dict) else {}
    if name in RPC_CALLBACK_REJECTION_OPERATIONS:
        # Each original callback only unlocks its named lock. Do
        # not run its success-only business consumer, nor infer arbitrary cbids.
        # Original rpc_method does not dispatch falsy callback IDs.
        if not callback_id:
            return None
        reply, body = 'serverCallbackCarrier', {'_r_': {}}
    elif name == 'zhaiRequest':
        reply, body = 'zhaiReply', {'rs': False, 'reward': {}}
    elif name == 'requestRecoverJingshenli':
        reply, body = 'replyRecoverJingshenli', {'rs': False, 'i': {'rsn': 0}}
    elif name == 'puzzleRoomGetClue':
        reply, body = 'puzzleRoomGetClueReturn', {'r': False, 'c': _rejection_int(args.get('c')), 'g': False}
    elif name == 'requestChangeAVGLevel':
        reply, body = 'replyChangeAVGLevel', {'rs': False, 'lv': _rejection_int(args.get('lv')), 'slv': _rejection_int(args.get('slv'))}
    elif name == 'requestTriggerEventByEnding':
        reply, body = 'replyTriggerEventByEnding', {'r': False}
    elif name == 'requestMainlineCgRewards':
        reply, body = 'replyMainlineCgRewards', {'rs': False, 'i': {}}
    elif name == 'requestTryPlayBattle':
        reply, body = 'replyTryPlayBattle', {'e': {}, 's': 0, 'h': _rejection_int(args.get('h'))}
    elif name == 'requestRandomRealtimeGiftBag':
        reply, body = 'replayRandomRealtimeGiftBag', {'r': False}
    elif name == 'buyRealtimeGiftBag':
        reply, body = 'replyBuyRealtimeGiftBag', {'r': False, 'id': _rejection_int(args.get('i')), 'i': {}}
    elif name == 'incHeroStarOrder':
        reply, body = 'incHeroStarOrder', {'h': -1, 'artifact': False}
    elif name in ('upgradeTreasure', 'upgradeTreasureTargetLv'):
        reply, body = name + 'Reply', {'h': -1, 's': _rejection_uuid(args.get('s'))}
        if name == 'upgradeTreasureTargetLv':
            body['l'] = _rejection_int(args.get('l'))
    elif name == 'requestExchangeSuipianWithItem':
        reply, body = 'replyExchangeSuipianWithItem', {'rs': False, 'i': {'rsn': 0}}
    elif name == 'requestExchangeActivityHeroProg':
        reply, body = 'replyExchangeActivityHeroProg', {'r': False, 'i': {}}
    elif name == 'giveCatFriendly':
        reply, body = 'replyGiveCatFriendly', {'st': False, 'info': {}}
    elif name in ('requestAddAxiliyaMood', 'requestCaijianOp', 'requestGetAxiliyaHero'):
        reply, body = name.replace('request', 'reply', 1), {'rs': False, 'i': {}}
    message = (u'\u6b64\u529f\u80fd\u5c1a\u672a\u63a5\u5165\u79bb\u7ebf\u7248\uff0c'
               u'\u672c\u6b21\u8bf7\u6c42\u672a\u6267\u884c')
    return reply, body, message


def _rejection_int(value):
    try:
        return int(value)
    except (ValueError, TypeError, OverflowError):
        return 0


def _rejection_uuid(value):
    if value is None:
        return None
    from common.IdManager import IdManager
    if IdManager.is_id_type(value):
        return value
    for convert in (IdManager.bytes2id, IdManager.str2id):
        try:
            convert(value)
            return value
        except Exception:
            pass
    return None


RPC_MISSING_CALLBACK_LOCKS = {
    'zhaiRequest': 'zhai',
    'requestTriggerDaXuanWo': 'requestTriggerDaXuanWo',
    'requestChangeAVGLevel': 'requestChangeAVGLevel',
    'actionRewardRequest': 'action_reward',
}

RPC_LOCAL_REJECTION_OPERATIONS = frozenset(('playerDestroyBuilding', 'canteenRequest'))


def cleanup_rpc_rejection(owner, name, callback_id, ending_context=None):
    """Undo only audited request-local waits/optimistic ending markers."""
    import gg
    lock = RPC_MISSING_CALLBACK_LOCKS.get(name)
    if lock and not callback_id:
        gg.ui.unlock(lock)
    if name == 'requestTriggerEventByEnding' and ending_context is not None:
        restore_ending_request_context(owner, ending_context)


_ABSENT = object()


def make_ending_request_guard(original):
    """Snapshot before the unchanged original request writes temporary markers."""
    original = getattr(original, 'im_func', original)

    def request(self, *args, **kwargs):
        proxy = getattr(self, 'server', None)
        if getattr(proxy, 'owner', None) is not self or not hasattr(proxy, 'reject_unimplemented_rpc'):
            return original(self, *args, **kwargs)
        story = getattr(self, 'storyData', None)
        week = getattr(self, 'weeknumData', None)
        previous = getattr(self, '_f7_ending_request_context', _ABSENT)
        context = {'story': story, 'week': week, 'proxy': proxy, 'dispatched': False,
                   'week_stamp': (getattr(week, 'weeknum', None), getattr(week, 'daynum', None)),
                   'week_protocol': copy.deepcopy(getattr(proxy, 'week_protocol', None)),
                   'prior': (getattr(story, 'change_week', _ABSENT),
                             getattr(self, 'handleIncWeekCb', _ABSENT),
                             getattr(story, 'last_storyline_click', _ABSENT))}
        self._f7_ending_request_context = context
        try:
            return original(self, *args, **kwargs)
        finally:
            context['written'] = (getattr(story, 'change_week', _ABSENT),
                                  getattr(self, 'handleIncWeekCb', _ABSENT),
                                  getattr(story, 'last_storyline_click', _ABSENT))
            if not context['dispatched']:
                _restore_attribute(self, '_f7_ending_request_context', previous)
    return request


def ending_request_context_matches(owner, context):
    if context is None:
        return False
    story, week = context['story'], context['week']
    return (getattr(owner, '_f7_ending_request_context', None) is context and
            getattr(owner, 'server', None) is context['proxy'] and
            getattr(context['proxy'], 'owner', None) is owner and
            getattr(context['proxy'], 'week_protocol', None) == context['week_protocol'] and
            getattr(owner, 'storyData', None) is story and
            getattr(owner, 'weeknumData', None) is week and
            (getattr(week, 'weeknum', None), getattr(week, 'daynum', None)) == context['week_stamp'] and
            (getattr(story, 'change_week', _ABSENT), getattr(owner, 'handleIncWeekCb', _ABSENT),
             getattr(story, 'last_storyline_click', _ABSENT)) == context.get('written'))


def _restore_attribute(target, name, value):
    if value is _ABSENT:
        if hasattr(target, name):
            delattr(target, name)
    else:
        setattr(target, name, value)


def restore_ending_request_context(owner, context):
    if not ending_request_context_matches(owner, context):
        return
    story = context['story']
    change_week, callback, last_click = context['prior']
    _restore_attribute(story, 'change_week', change_week)
    _restore_attribute(owner, 'handleIncWeekCb', callback)
    _restore_attribute(story, 'last_storyline_click', last_click)
    delattr(owner, '_f7_ending_request_context')


def install_ending_request_guard():
    from entity.ClientAvatar import ClientAvatar
    if getattr(ClientAvatar, '_f7_ending_request_guard', False):
        return
    ClientAvatar.requestTriggerEventByEnding = make_ending_request_guard(ClientAvatar.requestTriggerEventByEnding)
    ClientAvatar._f7_ending_request_guard = True


_PUZZLE_LOCK = 'puzzleRoomGetClue'


def _puzzle_proxy(avatar):
    proxy = getattr(avatar, 'server', None)
    if (getattr(proxy, '_f7_puzzle_refusal_gateway', False) and
            getattr(proxy, 'owner', None) is avatar):
        return proxy
    return None


def _puzzle_waits(ui):
    locks = getattr(ui, '_lock', None)
    record = getattr(ui, '_f7_puzzle_wait_record', None)
    if record is None or record[0] is not locks:
        record = (locks, [])
        ui._f7_puzzle_wait_record = record
    return record[1]


def make_puzzle_ui_guards(ui_class):
    """Track only this native counted lock; keep every original lock body."""
    if ui_class.__dict__.get('_f7_puzzle_ui_guard', False):
        return
    original_lock = getattr(ui_class.lock, 'im_func', ui_class.lock)
    original_unlock = getattr(ui_class.unlock, 'im_func', ui_class.unlock)

    def lock(self, key='default', show_panel=True):
        result = original_lock(self, key, show_panel)
        if key == _PUZZLE_LOCK:
            _puzzle_waits(self).append(object())
        return result

    def unlock(self, key='default', show_panel=True):
        if key == _PUZZLE_LOCK:
            waits = _puzzle_waits(self)
            token = getattr(self, '_f7_puzzle_delivery_wait', None)
            if token is not None:
                if token not in waits:
                    return
                waits.remove(token)
            elif waits:
                waits.pop(0)
        return original_unlock(self, key, show_panel)

    ui_class.lock, ui_class.unlock = lock, unlock
    ui_class._f7_puzzle_ui_guard = True


def make_puzzle_scene_guards(scene_class):
    """Remember only the original clue caller and unlock-touch lifecycle."""
    if scene_class.__dict__.get('_f7_puzzle_scene_guard', False):
        return
    original_get = getattr(scene_class.getClue, 'im_func', scene_class.getClue)
    original_unlock = getattr(scene_class.unlock_touch, 'im_func', scene_class.unlock_touch)

    def unlock_touch(self, *args, **kwargs):
        self._f7_puzzle_touch_generation = getattr(self, '_f7_puzzle_touch_generation', 0) + 1
        return original_unlock(self, *args, **kwargs)

    def get_clue(self, clue_data):
        import gg
        avatar = getattr(gg, 'avatar', None)
        if _puzzle_proxy(avatar) is None or getattr(gg, 'jiemi', None) is not self:
            return original_get(self, clue_data)
        self._f7_puzzle_touch_generation = getattr(self, '_f7_puzzle_touch_generation', 0) + 1
        caller = (object(), avatar, clue_data.get('clue_id'))
        self._f7_puzzle_caller = caller
        self._f7_puzzle_active_caller = caller
        try:
            return original_get(self, clue_data)
        finally:
            if getattr(self, '_f7_puzzle_active_caller', None) is caller:
                delattr(self, '_f7_puzzle_active_caller')

    scene_class.unlock_touch, scene_class.getClue = unlock_touch, get_clue
    scene_class._f7_puzzle_scene_guard = True


def _puzzle_native_stamp(owner, scene):
    story = getattr(owner, 'storyData', None)
    week = getattr(owner, 'weeknumData', None)
    return (getattr(scene, 'scene_id', None), getattr(scene, 'room_id', None),
            getattr(scene, 'camera_state', None), getattr(scene, 'cur_zoom_target', None),
            getattr(story, 'route', None), tuple(getattr(story, 'puzzle_room_clues', ())),
            getattr(week, 'weeknum', None), getattr(week, 'daynum', None),
            getattr(owner, '_q7_puzzle_snapshot', None))


def make_puzzle_request_guard(original):
    original = getattr(original, 'im_func', original)

    def request(self, clue):
        import gg
        proxy, scene = _puzzle_proxy(self), getattr(gg, 'jiemi', None)
        caller = getattr(scene, '_f7_puzzle_caller', None)
        if proxy is None or getattr(gg, 'avatar', None) is not self:
            return original(self, clue)
        ui = gg.ui
        if (scene is None or caller is None or
                getattr(scene, '_f7_puzzle_active_caller', None) is not caller or
                caller[1] is not self or caller[2] != clue):
            # A naked request still owns its own native counted UI wait, but
            # receives no authority over any current scene touch lock.
            context = {'owner': self, 'proxy': proxy, 'scene': None, 'clue': clue,
                       'ui': ui, 'locks': getattr(ui, '_lock', None), 'delivered': False}
            self._f7_puzzle_request_context = context
            try:
                return original(self, clue)
            finally:
                if getattr(self, '_f7_puzzle_request_context', None) is context:
                    delattr(self, '_f7_puzzle_request_context')
        previous = getattr(scene, '_f7_puzzle_latest_request', None)
        context = {'owner': self, 'proxy': proxy, 'scene': scene, 'caller': caller, 'clue': clue,
                   'ui': ui, 'locks': getattr(ui, '_lock', None),
                   'story': getattr(self, 'storyData', None), 'week': getattr(self, 'weeknumData', None),
                   'native': _puzzle_native_stamp(self, scene),
                   'protocol': copy.deepcopy(getattr(proxy, 'week_protocol', None)),
                   'touch_generation': getattr(scene, '_f7_puzzle_touch_generation', None),
                   'panel': getattr(scene, 'main_ui', None), 'delivered': False, 'completed': False}
        batch = []
        if (previous is not None and previous['owner'] is self and previous['proxy'] is proxy and
                previous['ui'] is ui and previous['locks'] is context['locks'] and
                previous['story'] is context['story'] and previous['week'] is context['week'] and
                previous['native'] == context['native'] and previous['protocol'] == context['protocol']):
            batch = previous['batch']
        context['batch'] = batch
        batch.append(context)
        scene._f7_puzzle_latest_request = context
        self._f7_puzzle_request_context = context
        try:
            return original(self, clue)
        finally:
            # Original lock precedes dispatch. The gateway binds its exact token.
            if getattr(self, '_f7_puzzle_request_context', None) is context:
                delattr(self, '_f7_puzzle_request_context')
    return request


def capture_puzzle_rejection(owner, proxy, parameters):
    context = getattr(owner, '_f7_puzzle_request_context', None)
    if (context is None or context['proxy'] is not proxy or context['clue'] != (parameters if isinstance(parameters, dict) else {}).get('c')):
        return None
    waits = _puzzle_waits(context['ui'])
    if not waits:
        return None
    context['wait'] = waits[-1]
    return context


def puzzle_rejection_can_deliver(context):
    if context is None:
        return True
    return (not context['delivered'] and context.get('wait') in _puzzle_waits(context['ui']) and
            getattr(context['ui'], '_lock', None) is context['locks'])


def finish_puzzle_rejection(context):
    """After the original False body, release only this drained scene batch."""
    if context is None:
        return
    import gg
    if context['scene'] is None:
        # Draining an unrelated naked UI wait can wake an already-completed
        # authorized scene request. The naked call supplies no scene authority;
        # that original request must pass every current scene guard itself.
        followup = getattr(getattr(gg, 'jiemi', None), '_f7_puzzle_latest_request', None)
        if (followup is not None and followup.get('completed') and
                followup['owner'] is context['owner'] and followup['proxy'] is context['proxy'] and
                followup['ui'] is context['ui'] and followup['locks'] is context['locks']):
            finish_puzzle_rejection(followup)
        return
    context['completed'] = True
    scene = context['scene']
    latest = getattr(scene, '_f7_puzzle_latest_request', None)
    if latest is None or latest['batch'] is not context['batch'] or not latest['completed']:
        return
    owner, ui = latest['owner'], latest['ui']
    waits = _puzzle_waits(ui)
    if (getattr(gg, 'avatar', None) is not owner or _puzzle_proxy(owner) is not latest['proxy'] or
            getattr(gg, 'jiemi', None) is not scene or getattr(gg, 'ui', None) is not ui or
            getattr(ui, '_lock', None) is not latest['locks'] or waits or
            getattr(owner, 'storyData', None) is not latest['story'] or
            getattr(owner, 'weeknumData', None) is not latest['week'] or
            _puzzle_native_stamp(owner, scene) != latest['native'] or
            getattr(latest['proxy'], 'week_protocol', None) != latest['protocol'] or
            getattr(scene, '_f7_puzzle_caller', None) is not latest['caller'] or
            getattr(scene, '_f7_puzzle_touch_generation', None) != latest['touch_generation'] or
            not getattr(scene, 'lock_touch', False) or
            getattr(owner, '_q7_puzzle_inflight', None) is not None):
        return
    panel = latest['panel']
    if (getattr(scene, 'main_ui', None) is not panel or
            panel is not None and (getattr(panel, 'can_operate', True) is False or
                                   getattr(panel, 'timer', None) is not None)):
        return
    # No clue, CG, dialogue or success animation is dispatched here.
    scene.unlock_touch()
    delattr(scene, '_f7_puzzle_latest_request')


def make_puzzle_reply_guard(original):
    original = getattr(original, 'im_func', original)

    def reply(self, *args, **kwargs):
        import gg
        if _puzzle_proxy(self) is not None and args and isinstance(args[0], dict) and args[0].get('r'):
            scene = getattr(gg, 'jiemi', None)
            # A legitimate success owns touch until the original animation's
            # unlock_touch; an older negative cannot finish its scene batch.
            if scene is not None and hasattr(scene, '_f7_puzzle_latest_request'):
                delattr(scene, '_f7_puzzle_latest_request')
        return original(self, *args, **kwargs)
    return reply


def install_puzzle_refusal_guard():
    from entity.ClientAvatar import ClientAvatar
    from game_scene.city_jiemi import Scene
    from cocos.ui_manager import UIManager
    if getattr(ClientAvatar, '_f7_puzzle_refusal_guard', False):
        return
    make_puzzle_ui_guards(UIManager)
    make_puzzle_scene_guards(Scene)
    ClientAvatar.puzzleRoomGetClue = make_puzzle_request_guard(ClientAvatar.puzzleRoomGetClue)
    ClientAvatar.puzzleRoomGetClueReturn = make_puzzle_reply_guard(ClientAvatar.puzzleRoomGetClueReturn)
    ClientAvatar._f7_puzzle_refusal_guard = True
