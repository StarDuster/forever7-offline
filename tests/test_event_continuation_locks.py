"""Event 4007-class stall: one `wait_reward` reference per occurrence.

Executes the real `runtime/project7_event_continuation/client_event_compat.py`
source against the original 640 `rpcdecorator`/`RpcMethodArgs` sources, with
synthetic UI/gateway boundaries. Checks the lock invariant that duplicate
startEventReply replays, reconnect, lost echo, and multi-week replay all leave
balanced:

    gg.ui._lock['wait_reward'] == number of live continuation records holding it

No game process, device, emulator, APK, D8 or account is touched.
"""
from pathlib import Path
import os
import sys
import types
import unittest
import ast
import textwrap
from lib2to3.refactor import RefactoringTool

ROOT = Path(__file__).resolve().parents[1]
COMPAT = Path(os.environ.get('P7_COMPAT_PATH')
              or ROOT / 'runtime/project7_event_continuation/client_event_compat.py')
MANAGER_COMPAT = ROOT / 'analysis/project7/manager/assets/client_event_compat.py'


def _module(name):
    module = types.ModuleType(name)
    module.__path__ = []
    sys.modules[name] = module
    if '.' in name:
        parent, leaf = name.rsplit('.', 1)
        if parent not in sys.modules:
            _module(parent)
        setattr(sys.modules[parent], leaf, module)
    return module


def _exec(path, namespace, drop=()):
    source = path.read_text()
    lines = []
    for line in source.splitlines():
        if line.strip() == 'return' and line[:1] not in (' ', '\t'):
            continue  # decompiled modules end with a module-level return
        if any(token in line for token in drop):
            continue
        lines.append(line)
    exec(compile('\n'.join(lines), str(path), 'exec'), namespace)
    return namespace


_FIX = RefactoringTool(['lib2to3.fixes.fix_print', 'lib2to3.fixes.fix_except',
                       'lib2to3.fixes.fix_dict', 'lib2to3.fixes.fix_xrange'])


def _original_method(name, env):
    path = ROOT / 'analysis/original-py-640/entity/avatar_members/EventTriggerMember.py'
    lines = path.read_text().splitlines(True)
    start = next(i for i, line in enumerate(lines) if line.startswith('    def ' + name + '('))
    end = start + 1
    while end < len(lines) and not (lines[end].startswith('    def ') or lines[end].startswith('    @')):
        end += 1
    source = textwrap.dedent(''.join(lines[start:end]))
    tree = ast.parse(str(_FIX.refactor_string(source, str(path))))
    exec(compile(tree, str(path) + ':' + name, 'exec'), env)
    return env[name]


def _load_rpc():
    _module('gg')
    id_module = _module('common.IdManager')
    id_module.IdManager = types.SimpleNamespace(str2id=lambda value: value,
                                                id2str=lambda value: value,
                                                genid=lambda: 1)
    entity_module = _module('common.EntityManager')
    entity_module.EntityManager = types.SimpleNamespace(getentity=lambda placeholder: None)
    syspathhelper = _module('syspathhelper')
    syspathhelper.addpath = lambda *a, **k: None
    log_module = _module('mobilelog.LogManager')
    log_module.LogManager = types.SimpleNamespace(
        get_logger=lambda *a, **k: types.SimpleNamespace(warn=lambda *a, **k: None,
                                                         error=lambda *a, **k: None))

    args_ns = {'__name__': 'common.RpcMethodArgs', 'StandardError': Exception}
    _exec(ROOT / 'analysis/original-py-640/lib/common/RpcMethodArgs.py', args_ns,
          drop=('setdefaultencoding', 'reload(sys)'))
    args_module = _module('common.RpcMethodArgs')
    args_module.__dict__.update(args_ns)

    ns = {'__name__': 'common.rpcdecorator', 'xrange': range, 'StandardError': Exception}
    _exec(ROOT / 'analysis/original-py-640/lib/common/rpcdecorator.py', ns)
    for name in ('Int', 'Dict', 'List', 'Str', 'BinData', 'Avatar', 'MailBox',
                 'RpcMethodArg', 'ConvertError'):
        ns[name] = getattr(args_module, name)
    return ns


class FakeUI(object):
    def __init__(self):
        self._lock = {}
        self._procing_settlement = False
        self.panels = types.SimpleNamespace(dialogue=types.SimpleNamespace(forcehide=False))
        self.hide = 0

    def lock(self, key='default', show_panel=True):
        self._lock[key] = self._lock.get(key, 0) + 1

    def unlock(self, key='default', show_panel=True):
        if key in self._lock:
            self._lock[key] = max(0, self._lock[key] - 1)
        else:
            self.hide += 1

    def is_lock(self, key=None):
        if key is None:
            return any(self._lock.values())
        return bool(self._lock.get(key, 0))

    def wait_reward(self):
        return self._lock.get('wait_reward', 0)


class EventData(object):
    def __init__(self):
        self.selectedEvent = None
        self.processingEventsClient = set()
        self.semaphore = {'default': 0}
    def addProcessingEvent(self, event):
        self.processingEventsClient.add(event)
    def delProcessingEvent(self, event):
        self.processingEventsClient.discard(event)


class Avatar(object):
    """Projected ClientAvatar: native bodies only, no 3D/UI runtime."""

    def __init__(self, gg):
        self.gg = gg
        self.logger = types.SimpleNamespace(debug=lambda *a, **k: None)
        self.eventTriggerData = EventData()
        self.echoes = []
        self.traces = []
        self.sent = []
        self.scenes = []
        self.leaves = 0
        self.movies = 0
        self.movie_callbacks = []
        self.city_scene_callbacks = []
        self.city_scene = types.SimpleNamespace()
        self.city_scene.setLeaveCallback = self._set_city_leave
        self.saved = 0
        self.weeknumData = types.SimpleNamespace(daynum=4, weeknum=1)
        self.newbeeData = types.SimpleNamespace(checkAllNewbee=lambda: None)
        self.eventTriggerData.completedEvents = set()
        self.queryEventOptAsk = lambda e: None
        self.battleEnterWithEventMode = lambda e: None
        self.checkEvents = lambda *a, **k: None
        self.noticePVETeam = lambda *a, **k: None

    # --- original member bodies (EventTriggerMember) ---
    def startEvent(self, event):
        self.sent.append(('startEvent', event))
        return True

    def startEventReply(self, event, result):
        self.sent.append(('startEventReply', event, result))
        if not result:
            return
        if self.gg.logic.event_semaphore.get('wholeEvent', 0):
            self.sent.append(('blocked', event))
            return
        self.eventTriggerData.processingEventsClient.add(event)
        self.gg.logic.disable_event('wholeEvent')
        self.completeBase(event)

    def completeBase(self, event):
        self.completeEventDialog(event)

    def completeEventDialog(self, event):
        self.gg.ui.lock('wait_reward')

    def startSettlement(self, event):
        self.gg.ui.unlock('wait_reward')

    def startEventBattle(self, event):
        return self.startCheckNewbee()

    def startCheckNewbee(self):
        self.gg.logic.enable_event('wholeEvent')

    def completeEventReplyEnd(self, event):
        self.sent.append(('completeEventReplyEnd', event))
        self.eventTriggerData.processingEventsClient.discard(event)

    def updateDay(self, day):
        return day

    def avatarClientDataSave(self):
        self.saved += 1

    def callServerMethodReliable(self, method, parameters, callback=None):
        record = {'method': method, 'parameters': dict(parameters), 'callback': callback}
        if method == 'reliableEcho':
            self.echoes.append(record)
        else:
            self.sent.append((method, dict(parameters)))
        return record

    def clientTraceProcessingEvent(self, key, value, callback=None):
        record = {'method': key, 'parameters': dict(value) if isinstance(value, dict) else value,
                  'callback': callback}
        self.traces.append(record)
        return record

    def callServerMethod(self, *args, **kwargs):
        return None

    def startCaidanScene(self, event):
        self.scenes.append(event)

    def startEventUI(self, event):
        return self.startMovie(event)

    def startMovie(self, event):
        self.movies += 1
        module = sys.modules.get('cutils.chelpers')
        if module is not None:
            return module.play_movie(None, lambda: self.movie_leave(event))
        return self.movie_leave(event)

    def _set_city_leave(self, callback):
        self.city_scene_callbacks.append(callback)
        return callback

    def movie_leave(self, event):
        self.leaves += 1
        return self.startEventBattle(event)

    # --- surfaces only referenced by the module-level installs ---
    def syncPuzzleRoomClue(self, *args, **kwargs):
        return None

    def puzzleRoomGetClue(self, *args, **kwargs):
        return None

    def puzzleRoomGetClueReturn(self, *args, **kwargs):
        return None

    def cgRewards(self, *args, **kwargs):
        return None


class Install(object):
    """One isolated import of the compat asset with fresh globals."""

    def __init__(self, original_chain=False):
        rpc = _load_rpc()
        self.rpc = rpc

        self.ui = FakeUI()
        self.events = []

        def disable(name):
            self.events.append(('disable', name))
            self.gg.logic.event_semaphore[name] = self.gg.logic.event_semaphore.get(name, 0) + 1

        def enable(name, check=True):
            self.events.append(('enable', name))
            self.gg.logic.event_semaphore[name] = max(0, self.gg.logic.event_semaphore.get(name, 0) - 1)

        gg_module = sys.modules['gg']
        for key in list(gg_module.__dict__):
            if not key.startswith('__'):
                delattr(gg_module, key)
        gg_module.__dict__.update(types.SimpleNamespace(
            ui=self.ui, avatar=None, city=types.SimpleNamespace(touchable=True),
            event=types.SimpleNamespace(add_event_handler=lambda *a: None,
                                        del_event_handler=lambda *a: None),
            logic=types.SimpleNamespace(event_valid=True, event_semaphore={'wholeEvent': 0},
                                        disable_event=disable, enable_event=enable,
                                        leave_emergency=lambda *a, **k: setattr(self.gg.avatar, 'leaves', self.gg.avatar.leaves + 1)),
            avatar_callback_map={}, avatar_callback_need_result={},
            exec_delay=lambda ms, cb: None, exec_cancel=lambda handle: None,
            jiemi=None, panels=types.SimpleNamespace(dialogue=types.SimpleNamespace(forcehide=False)),
            city_container=types.SimpleNamespace(push_scene=lambda *a: None,
                                                 get_scene_by_key=lambda *a: self.avatar.city_scene),
            puzzle_room=types.SimpleNamespace(setLeaveCallback=lambda cb: None)).__dict__)
        self.gg = gg_module

        event_member = _module('entity.avatar_members.EventTriggerMember')
        event_member.rpc_method = rpc['rpc_method']
        event_member.CLIENT_STUB = rpc['CLIENT_STUB']
        event_member.Int = rpc['Int']

        content = _module('com.data.cdata.event_content')
        content.data = {
            4007: {'ui': ('city', 'show_review'), 'autoStart': True},
            4008: {'dialog': (1,)},
            4009: {'isLeaveEmergencyEvent': True, 'movie': 'qa_movie'},
            4010: {'enter_caidan': 1, 'isLeaveEmergencyEvent': True},
        }
        const = _module('com.const')
        const.GameEvent = types.SimpleNamespace(SETTLEMENT_END='SETTLEMENT_END')
        const.DAXUANWO_EVENT = 0
        const.SCENE_CAIDAN = 'caidan'

        settlement = _module('cocos.panels.settlement_fullscreen')
        settlement.Panel = type('Panel', (), {
            'notify_settlement_area_open': lambda self, *a: None,
            'notify_settlement_area_fight': lambda self, *a: None,
            'settlement_ended': lambda self, *a: None,
            'notify_area_event': lambda self, *a: None,
        })
        diary = _module('cocos.panels.diary_hero')
        diary.Panel = type('Panel', (), {'refresh': lambda self, *a: None})
        city_panel = _module('cocos.panels.city')
        city_panel.Panel = type('Panel', (), {
            'on_load': lambda self, *a: None,
            'on_destroy': lambda self, *a: None,
            'on_update': lambda self, *a: None,
            'update_whiteLove_info': lambda self, *a: None,
        })
        puzzle = _module('com.data.cdata.puzzle_room_clue')
        puzzle.data = {}

        chelpers = _module('cutils.chelpers')
        chelpers.play_movie = lambda movie, callback, *a, **k: self.avatar.movie_callbacks.append(callback)

        # Project the RPC decorator onto the native methods the asset replaces.
        self.avatar_class = type('ProjectedClientAvatar', (Avatar,), {})
        if original_chain:
            env = {'gg': self.gg, 'const': const,
                   'EventContentDataMod': content,
                   'chelpers': chelpers,
                   'game3d': types.SimpleNamespace(CM_NO_CTRL=0),
                   'helpers': types.SimpleNamespace(toIntKeyDict=lambda d: d,
                                                    toStrKeyDict=lambda d: d),
                   'RESET_WEEK_EVENT': types.SimpleNamespace(data={}),
                   'ITEM_DATA': types.SimpleNamespace(data={})}
            for name in ('startEventReply', 'completeEventReplyEnd', 'completeBase',
                         'completeCityAttention',
                         'completeEventDialog', 'startSettlement', 'startCaidanScene',
                         'startPuzzleRoom', 'startEventUI', 'startMovie',
                         'startEventBattle', 'startCheckNewbee'):
                setattr(self.avatar_class, name, _original_method(name, env))
        self.avatar_class.startEventReply = rpc['rpc_method'](rpc['CLIENT_STUB'],
            (rpc['Int']('e'), rpc['Int']('r')))(getattr(self.avatar_class, 'startEventReply'))
        self.avatar_class.completeEventReplyEnd = rpc['rpc_method'](rpc['CLIENT_STUB'],
            (rpc['Int']('e'),))(getattr(self.avatar_class, 'completeEventReplyEnd'))
        self.avatar = self.avatar_class(self.gg)
        self.gg.avatar = self.avatar

        namespace = {'__name__': 'client_event_compat'}
        _exec(COMPAT, namespace)
        self.namespace = namespace

    def reply(self, event=4007, result=1, cbid=1000):
        self.avatar.startEventReply({'e': event, 'r': result, '_cbid_': cbid})

    def fire_echo(self, index=0):
        self.avatar.echoes[index]['callback']({'e': None})

    def server_end(self, event=4007):
        self.avatar.completeEventReplyEnd({'e': event})

    def finish_pipeline(self, event=4007):
        self.avatar.startEventBattle(event)
        self.avatar.startCheckNewbee()

    def locks(self):
        return self.ui.wait_reward()


class ContinuationLockTests(unittest.TestCase):
    def test_duplicate_start_event_replies_take_one_lock_and_one_echo(self):
        fixture = Install()
        for cbid in (1001, 1002, 1003, 1004):
            fixture.reply(cbid=cbid)
        self.assertEqual(fixture.locks(), 1)
        self.assertEqual(len(fixture.avatar.echoes), 1)
        self.assertEqual(fixture.avatar.sent.count(('startEventReply', 4007, 1)), 1)

        fixture.fire_echo()
        self.assertEqual(fixture.locks(), 0)
        self.assertEqual(fixture.avatar.scenes, [4007])

        fixture.finish_pipeline()
        self.assertEqual(fixture.avatar.sent.count(('q7CompleteUiEvent', {'e': 4007})), 1)

        # Three more replays while the pipeline/UI is live change nothing.
        for cbid in (1005, 1006, 1007):
            fixture.reply(cbid=cbid)
        self.assertEqual(fixture.locks(), 0)
        self.assertEqual(len(fixture.avatar.echoes), 1)

    def test_reconnect_releases_the_native_lock_once(self):
        fixture = Install()
        fixture.reply()
        self.assertEqual(fixture.locks(), 1)

        fixture.avatar.avatarClientDataSave()
        self.assertEqual(fixture.locks(), 1)
        self.assertIn(4007, fixture.avatar._q7_settlement_continuations)
        replacement = fixture.avatar_class(fixture.gg)
        fixture.gg.avatar = replacement
        fixture.avatar.avatarClientDataSave()
        self.assertEqual(fixture.locks(), 0)
        self.assertEqual(fixture.avatar.saved, 2)
        self.assertEqual(fixture.avatar._q7_settlement_continuations, {})

        # The new avatar is a different object; the old record must not hold a lock.
        replacement = fixture.avatar_class(fixture.gg)
        fixture.gg.avatar = replacement
        replacement.completeEventDialog(4007)
        self.assertEqual(fixture.locks(), 1)
        replacement.startSettlement(4007)
        self.assertEqual(fixture.locks(), 0)

    def test_lost_echo_retries_after_stall_without_leaking(self):
        fixture = Install()
        fixture.reply()
        self.assertEqual(fixture.locks(), 1)
        record = fixture.avatar._q7_settlement_continuations[4007]
        record['since'] -= 9.0
        fixture.reply(cbid=1002)
        self.assertEqual(fixture.locks(), 1)
        self.assertEqual(len(fixture.avatar.echoes), 2)
        # The late first echo is ignored; the retry owns the reference.
        fixture.fire_echo(0)
        self.assertEqual(fixture.locks(), 1)
        fixture.fire_echo(1)
        self.assertEqual(fixture.locks(), 0)

    def test_dialog_pipeline_does_not_release_a_successor_whole_event(self):
        fixture = Install()
        fixture.reply(4008)
        fixture.avatar.traces[0]['callback']({'e': None})
        fixture.finish_pipeline(4008)
        self.assertEqual(fixture.gg.logic.event_semaphore['wholeEvent'], 0)
        self.assertEqual(fixture.locks(), 0)
        fixture.reply(4007, cbid=2001)
        self.assertEqual(fixture.gg.logic.event_semaphore['wholeEvent'], 1)
        self.assertEqual(fixture.locks(), 1)
        fixture.avatar.completeEventReplyEnd(4008)
        self.assertEqual(fixture.gg.logic.event_semaphore['wholeEvent'], 1)
        self.assertEqual(fixture.locks(), 1)

    def test_stalled_replay_releases_whole_event_for_native_retry(self):
        fixture = Install()
        fixture.reply()
        self.assertEqual(fixture.gg.logic.event_semaphore['wholeEvent'], 1)
        record = fixture.avatar._q7_settlement_continuations[4007]
        record['since'] -= 9.0
        fixture.reply(cbid=1002)
        self.assertNotIn(('blocked', 4007), fixture.avatar.sent)
        self.assertEqual(fixture.gg.logic.event_semaphore['wholeEvent'], 1)
        self.assertEqual(len(fixture.avatar.echoes), 2)
        fixture.fire_echo(0)
        self.assertEqual(fixture.locks(), 1)
        self.assertEqual(fixture.gg.logic.event_semaphore['wholeEvent'], 1)
        fixture.fire_echo(1)
        self.assertEqual(fixture.locks(), 0)
        fixture.finish_pipeline()
        self.assertEqual(fixture.gg.logic.event_semaphore['wholeEvent'], 0)
        self.assertEqual(fixture.avatar.sent.count(('q7CompleteUiEvent', {'e': 4007})), 1)

    def test_stale_lock_is_adopted_not_stacked(self):
        fixture = Install()
        fixture.ui.lock('wait_reward')  # leaked by an avatar object that is gone
        fixture.reply()
        self.assertEqual(fixture.locks(), 1)
        fixture.fire_echo()
        self.assertEqual(fixture.locks(), 0)

    def test_settlement_after_avatar_replacement_does_not_touch_the_panel(self):
        fixture = Install()
        fixture.reply()
        fixture.gg.avatar = fixture.avatar_class(fixture.gg)
        fixture.fire_echo()
        self.assertEqual(fixture.locks(), 0)
        self.assertEqual(fixture.avatar.scenes, [])

    def test_multi_week_replay_allows_a_new_occurrence(self):
        fixture = Install()
        fixture.reply()
        fixture.fire_echo()
        fixture.finish_pipeline()
        fixture.avatar.completeEventReplyEnd({'e': 4007})
        self.assertEqual(fixture.avatar._q7_settlement_continuations, {})
        self.assertEqual(fixture.locks(), 0)

        fixture.reply(cbid=2001)
        self.assertEqual(fixture.locks(), 1)
        fixture.fire_echo(1)
        self.assertEqual(fixture.locks(), 0)
        self.assertEqual(fixture.avatar.scenes, [4007, 4007])

    def test_start_event_is_not_reissued_for_a_live_occurrence(self):
        fixture = Install()
        self.assertTrue(fixture.avatar.startEvent(4007))
        fixture.reply()
        self.assertFalse(fixture.avatar.startEvent(4007))
        fixture.fire_echo()
        fixture.finish_pipeline()
        # Native done without server completion keeps the fence until End.
        self.assertFalse(fixture.avatar.startEvent(4007))
        self.assertIn(4007, fixture.avatar._q7_settlement_continuations)
        fixture.server_end()
        self.assertNotIn(4007, fixture.avatar._q7_settlement_continuations)

    def test_stalled_pipeline_can_be_retried_explicitly(self):
        fixture = Install()
        fixture.ui._procing_settlement = True  # settlement still running: phase 'waiting'
        fixture.reply()
        fixture.fire_echo()
        self.assertEqual(fixture.locks(), 0)
        self.assertFalse(fixture.avatar.startEvent(4007))
        fixture.avatar._q7_settlement_continuations[4007]['since'] -= 9.0
        self.assertFalse(fixture.avatar.startEvent(4007))
        self.assertIn(4007, fixture.avatar._q7_settlement_continuations)
        self.assertEqual(fixture.locks(), 0)

    def _cross_avatar_transfer(self):
        fixture = Install()
        fixture.reply()                                  # avatar A claims
        first = fixture.avatar
        a_record = first._q7_settlement_continuations[4007]
        self.assertEqual(fixture.locks(), 1)
        self.assertTrue(a_record['lock'])
        replacement = fixture.avatar_class(fixture.gg)
        fixture.gg.avatar = replacement
        replacement.completeEventDialog(4007)            # avatar B claims
        b_record = replacement._q7_settlement_continuations[4007]
        self.assertEqual(fixture.locks(), 1)             # transferred, not stacked
        self.assertTrue(b_record['lock'])
        self.assertFalse(a_record['lock'])               # A was revoked
        self.assertNotEqual(a_record.get('token'), b_record.get('token'))
        return fixture, first, replacement, a_record, b_record

    def test_old_avatar_echo_cannot_release_the_new_owner(self):
        fixture, first, replacement, a_record, b_record = self._cross_avatar_transfer()
        fixture.fire_echo(0)                             # A's late echo
        self.assertEqual(fixture.locks(), 1)
        self.assertTrue(b_record['lock'])
        self.assertEqual(replacement.scenes, [])
        replacement.echoes[0]['callback']({'e': None})   # B's own echo
        self.assertEqual(fixture.locks(), 0)
        self.assertEqual(replacement.scenes, [4007])

    def test_old_avatar_reconnect_cannot_release_the_new_owner(self):
        fixture, first, replacement, a_record, b_record = self._cross_avatar_transfer()
        first.avatarClientDataSave()                     # A's reconnect save
        self.assertEqual(fixture.locks(), 1)
        self.assertTrue(b_record['lock'])
        self.assertEqual(first._q7_settlement_continuations, {})
        replacement.echoes[0]['callback']({'e': None})   # B's own echo
        self.assertEqual(fixture.locks(), 0)
        self.assertEqual(replacement.scenes, [4007])

    def test_stale_settlement_handler_cannot_advance_the_new_occurrence(self):
        fixture = Install()
        fixture.ui._procing_settlement = True
        fixture.reply()
        fixture.fire_echo()                              # occurrence 1 settling
        first = fixture.avatar._q7_settlement_continuations[4007]
        handler = first['handler']
        self.assertIsNotNone(handler)

        first['since'] -= 9.0
        self.assertFalse(fixture.avatar.startEvent(4007))
        self.assertIs(fixture.avatar._q7_settlement_continuations[4007], first)
        self.assertEqual(len(fixture.avatar.echoes), 1)

        handler()                                        # long settlement end
        self.assertEqual(fixture.avatar.scenes, [4007])
        self.assertIn(4007, fixture.avatar._q7_settlement_continuations)
        self.assertEqual(fixture.locks(), 0)

    def test_superseded_pipeline_cannot_complete_the_new_occurrence(self):
        fixture = Install()
        fixture.reply()
        fixture.fire_echo()                              # occurrence 1 -> pipeline id
        first = fixture.avatar._q7_settlement_continuations[4007]
        first['since'] -= 9.0
        self.assertFalse(fixture.avatar.startEvent(4007))
        self.assertIs(fixture.avatar._q7_settlement_continuations[4007], first)

        fixture.avatar.startEventBattle(4007)            # same live pipeline resumes
        fixture.avatar.startCheckNewbee()
        self.assertEqual(fixture.avatar.sent.count(('q7CompleteUiEvent', {'e': 4007})), 1)

    def test_server_end_before_echo_keeps_continuation_until_native_done(self):
        fixture = Install()
        fixture.reply()
        fixture.server_end()
        self.assertIn(4007, fixture.avatar._q7_settlement_continuations)
        self.assertEqual(fixture.locks(), 1)
        fixture.fire_echo()
        self.assertEqual(fixture.avatar.scenes, [4007])
        self.assertIn(4007, fixture.avatar._q7_settlement_continuations)
        fixture.finish_pipeline()
        self.assertNotIn(4007, fixture.avatar._q7_settlement_continuations)
        self.assertEqual(fixture.locks(), 0)

    def test_echo_wait_settlement_then_server_end_only_retires_after_native(self):
        fixture = Install()
        fixture.ui._procing_settlement = True
        fixture.reply()
        fixture.fire_echo()
        fixture.server_end()
        self.assertEqual(fixture.avatar.scenes, [])
        self.assertIn(4007, fixture.avatar._q7_settlement_continuations)
        record = fixture.avatar._q7_settlement_continuations[4007]
        record['handler']()
        self.assertEqual(fixture.avatar.scenes, [4007])
        self.assertIn(4007, fixture.avatar._q7_settlement_continuations)
        fixture.finish_pipeline()
        self.assertNotIn(4007, fixture.avatar._q7_settlement_continuations)

    def test_movie_stage_server_end_keeps_record_until_native_done(self):
        fixture = Install()
        fixture.reply()
        fixture.fire_echo()
        fixture.server_end()
        self.assertIn(4007, fixture.avatar._q7_settlement_continuations)
        fixture.finish_pipeline()
        self.assertNotIn(4007, fixture.avatar._q7_settlement_continuations)
        self.assertEqual(fixture.avatar.scenes, [4007])

    def test_native_done_then_server_end_retires_on_end(self):
        fixture = Install()
        fixture.reply()
        fixture.fire_echo()
        fixture.finish_pipeline()
        self.assertIn(4007, fixture.avatar._q7_settlement_continuations)
        fixture.server_end()
        self.assertNotIn(4007, fixture.avatar._q7_settlement_continuations)
        self.assertEqual(fixture.locks(), 0)

    def test_ui_only_q7complete_and_duplicate_ack_retire_once(self):
        fixture = Install()
        fixture.reply(4007)
        fixture.fire_echo()
        fixture.finish_pipeline(4007)
        self.assertEqual(fixture.avatar.sent.count(('q7CompleteUiEvent', {'e': 4007})), 1)
        fixture.server_end(4007)
        self.assertNotIn(4007, fixture.avatar._q7_settlement_continuations)
        fixture.server_end(4007)
        self.assertNotIn(4007, fixture.avatar._q7_settlement_continuations)
        self.assertEqual(fixture.locks(), 0)

    def test_v6_equivalent_server_end_before_echo_reproduces_missing_handoff(self):
        fixture = Install()
        # Recreate only the old v6 completeEventReplyEnd cancellation behavior
        # on this test avatar; the current source must not do this.
        def old_end(self, event):
            fixture.namespace['_q7_cancel_continuation'](self, event, 'completed')
            return self._q7_original_complete_event_reply_end(event)
        fixture.avatar_class.completeEventReplyEnd = fixture.rpc['rpc_method'](
            fixture.rpc['CLIENT_STUB'], (fixture.rpc['Int']('e'),))(old_end)
        fixture.reply()
        fixture.server_end()
        fixture.fire_echo()
        self.assertEqual(fixture.avatar.scenes, [])
        self.assertEqual(fixture.avatar._q7_settlement_continuations, {})

    def test_complete_chain_leave_emergency_once(self):
        fixture = Install()
        fixture.reply()
        fixture.fire_echo()
        fixture.avatar.startMovie(4007)
        fixture.avatar.movie_callbacks[-1]()
        fixture.server_end()
        self.assertEqual(fixture.avatar.leaves, 1)
        self.assertNotIn(4007, fixture.avatar._q7_settlement_continuations)
        self.assertEqual(fixture.locks(), 0)

    def test_old_movie_callback_cannot_leave_new_avatar(self):
        fixture = Install()
        fixture.reply()
        fixture.fire_echo()
        old = fixture.avatar
        old.startMovie(4007)
        old_callback = old.movie_callbacks[-1]
        replacement = fixture.avatar_class(fixture.gg)
        fixture.gg.avatar = replacement
        replacement._q7_settlement_continuations = {4007: {'phase': 'created', 'lock': False, 'since': 0,
                                                           'server_completed': False, 'native_pipeline_done': False,
                                                           'week': replacement.weeknumData.weeknum,
                                                           'occurrence': object(), 'whole_event': False}}
        replacement.startMovie(4007)
        old_callback()  # late old movie callback
        self.assertEqual(old.leaves, 0)
        self.assertEqual(replacement.leaves, 0)
        fixture.avatar.movie_callbacks[-1]()  # current callback
        self.assertEqual(replacement.leaves, 1)

    def test_long_movie_or_settlement_server_completed_keeps_record(self):
        fixture = Install()
        fixture.ui._procing_settlement = True
        fixture.reply()
        fixture.fire_echo()
        fixture.server_end()
        record = fixture.avatar._q7_settlement_continuations[4007]
        record['since'] -= 20.0
        for _ in range(5):
            self.assertFalse(fixture.avatar.startEvent(4007))
        self.assertIs(fixture.avatar._q7_settlement_continuations[4007], record)
        record['handler']()
        self.assertEqual(fixture.avatar.scenes, [4007])
        fixture.finish_pipeline()
        self.assertNotIn(4007, fixture.avatar._q7_settlement_continuations)

    def test_native_terminal_exception_preserves_ownership(self):
        fixture = Install()
        fixture.reply()
        fixture.fire_echo()
        record = fixture.avatar._q7_settlement_continuations[4007]
        def fail(self):
            raise RuntimeError('native terminal failed')
        fixture.avatar_class._q7_original_start_check_newbee = fail
        with self.assertRaises(RuntimeError):
            fixture.avatar.startCheckNewbee()
        self.assertIs(fixture.avatar._q7_settlement_continuations[4007], record)
        self.assertFalse(record.get('native_pipeline_done'))
        self.assertTrue(record.get('whole_event'))
        replacement = fixture.avatar_class(fixture.gg)
        fixture.gg.avatar = replacement
        fixture.avatar.avatarClientDataSave()
        self.assertEqual(fixture.gg.logic.event_semaphore['wholeEvent'], 0)
        self.assertNotIn(4007, fixture.avatar._q7_settlement_continuations)

    def test_created_timeout_dialog_rebuilds_record_without_unbound(self):
        fixture = Install()
        fixture.reply()
        record = fixture.avatar._q7_settlement_continuations[4007]
        record['since'] -= 9.0
        fixture.avatar.completeEventDialog(4007)
        replacement = fixture.avatar._q7_settlement_continuations[4007]
        self.assertIsNot(replacement, record)
        self.assertEqual(replacement.get('phase'), 'created')
        self.assertEqual(fixture.locks(), 1)

    def test_whole_event_release_uses_record_owned_logic(self):
        fixture = Install()
        fixture.reply()
        record = fixture.avatar._q7_settlement_continuations[4007]
        calls = []
        old_logic = types.SimpleNamespace(event_semaphore={'wholeEvent': 1},
                                          disable_event=lambda *a: None,
                                          enable_event=lambda *a, **k: calls.append('old'))
        new_logic = types.SimpleNamespace(event_semaphore={'wholeEvent': 0},
                                          disable_event=lambda *a: None,
                                          enable_event=lambda *a, **k: calls.append('new'))
        record['whole_event_logic'] = old_logic
        fixture.gg.logic = new_logic
        replacement = fixture.avatar_class(fixture.gg)
        fixture.gg.avatar = replacement
        fixture.avatar.avatarClientDataSave()
        self.assertEqual(calls, ['old'])
        self.assertEqual(new_logic.event_semaphore['wholeEvent'], 0)

    def test_real_original_640_caidan_ui_movie_chain(self):
        fixture = Install(original_chain=True)
        fixture.reply(4009)
        fixture.fire_echo()
        self.assertEqual(len(fixture.avatar.movie_callbacks), 1)
        fixture.avatar.movie_callbacks[-1]()
        self.assertEqual(fixture.avatar.leaves, 1)
        fixture.server_end(4009)
        self.assertNotIn(4009, fixture.avatar._q7_settlement_continuations)
        self.assertEqual(fixture.locks(), 0)

    def test_stale_caidan_leave_callback_does_not_advance_new_occurrence(self):
        fixture = Install(original_chain=True)
        fixture.reply(4010)
        fixture.fire_echo()
        self.assertEqual(len(fixture.avatar.city_scene_callbacks), 1)
        callback = fixture.avatar.city_scene_callbacks[0]
        fixture.avatar._q7_reset_story_continuations()
        callback()
        self.assertNotIn(4009, fixture.avatar.sent)
        self.assertNotIn(('q7CompleteUiEvent', {'e': 4010}), fixture.avatar.sent)
        self.assertEqual(fixture.avatar._q7_settlement_continuations, {})

    def test_caidan_scene_restores_same_scene_setter_identity_and_exception(self):
        fixture = Install(original_chain=True)
        original_get = fixture.gg.city_container.get_scene_by_key
        original_setter = fixture.avatar.city_scene.setLeaveCallback
        fixture.avatar._q7_settlement_continuations = {4010: {'phase': 'created', 'lock': False, 'since': 0,
                                                             'week': fixture.avatar.weeknumData.weeknum,
                                                             'occurrence': object(), 'whole_event': False,
                                                             'server_completed': False, 'native_pipeline_done': False}}
        fixture.avatar.startCaidanScene(4010)
        self.assertIs(fixture.gg.city_container.get_scene_by_key, original_get)
        self.assertEqual(getattr(fixture.avatar.city_scene.setLeaveCallback, '__func__', fixture.avatar.city_scene.setLeaveCallback),
                         getattr(original_setter, '__func__', original_setter))
        fixture.avatar._q7_settlement_continuations = {4010: {'phase': 'created', 'lock': False, 'since': 0,
                                                             'week': fixture.avatar.weeknumData.weeknum,
                                                             'occurrence': object(), 'whole_event': False,
                                                             'server_completed': False, 'native_pipeline_done': False}}
        fixture.avatar.startCaidanScene(4010)
        self.assertIs(fixture.gg.city_container.get_scene_by_key, original_get)
        def fail(self, event):
            fixture.gg.city_container.get_scene_by_key('x')
            raise RuntimeError('caidan failure')
        fixture.avatar_class._q7_original_start_caidan_scene = fail
        fixture.avatar._q7_settlement_continuations = {4010: {'phase': 'created', 'lock': False, 'since': 0,
                                                             'week': fixture.avatar.weeknumData.weeknum,
                                                             'occurrence': object(), 'whole_event': False,
                                                             'server_completed': False, 'native_pipeline_done': False}}
        with self.assertRaises(RuntimeError):
            fixture.avatar.startCaidanScene(4010)
        self.assertIs(fixture.gg.city_container.get_scene_by_key, original_get)
        self.assertEqual(getattr(fixture.avatar.city_scene.setLeaveCallback, '__func__', fixture.avatar.city_scene.setLeaveCallback),
                         getattr(original_setter, '__func__', original_setter))

    def test_runtime_asset_is_the_single_manager_source(self):
        if os.environ.get('P7_COMPAT_PATH'):
            self.skipTest('alternate compat under test')
        self.assertEqual(MANAGER_COMPAT.read_bytes(), COMPAT.read_bytes())

    def test_settlement_without_a_record_releases_the_orphaned_panel(self):
        fixture = Install()
        fixture.ui.lock('wait_reward')  # native lock taken before the asset loaded
        fixture.avatar.startSettlement(4007)
        self.assertEqual(fixture.locks(), 0)
        self.assertEqual(fixture.avatar.scenes, [4007])

    def test_week_reset_releases_only_owned_whole_event_reference(self):
        fixture = Install()
        fixture.gg.logic.event_semaphore['wholeEvent'] = 2
        fixture.avatar._q7_settlement_continuations = {
            4007: {'phase': 'waiting', 'lock': False, 'token': None,
                   'since': 0, 'whole_event': True,
                   'whole_event_logic': fixture.gg.logic},
            4008: {'phase': 'waiting', 'lock': False, 'token': None,
                   'since': 0},
        }
        fixture.avatar._q7_reset_story_continuations()
        self.assertEqual(fixture.gg.logic.event_semaphore['wholeEvent'], 1)
        self.assertEqual(fixture.avatar._q7_settlement_continuations, {})

    def test_week_reset_releases_every_reference(self):
        fixture = Install()
        fixture.reply()
        fixture.avatar._q7_settlement_continuations[4008] = {
            'phase': 'created', 'lock': False, 'bus': None, 'handler': None, 'since': 0}
        fixture.avatar._q7_reset_story_continuations()
        self.assertEqual(fixture.locks(), 0)
        self.assertEqual(fixture.avatar._q7_settlement_continuations, {})


if __name__ == '__main__':
    unittest.main()
