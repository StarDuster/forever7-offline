"""Original 640 event consumer + generic in-flight start coalescing.

No game runtime/transport: the exact original startEvent/startEventReply/
tryNotifyEvent/pullEventsReply consumers run with explicit UI/member seams.
"""
import _paths  # noqa: E402,F401
import ast, importlib.util, sys, textwrap, types, unittest
from pathlib import Path
from unittest.mock import patch
from lib2to3.refactor import RefactoringTool

ROOT = Path(__file__).resolve().parents[1]
NS = types.SimpleNamespace
FIX = RefactoringTool(['lib2to3.fixes.fix_print', 'lib2to3.fixes.fix_except',
                       'lib2to3.fixes.fix_dict', 'lib2to3.fixes.fix_xrange'])
spec = importlib.util.spec_from_file_location('startup_hook', ROOT / 'runtime/project7_startup_hook.py')
hook = importlib.util.module_from_spec(spec)
spec.loader.exec_module(hook)


def original(name, env):
    path = ROOT / 'analysis/original-py-640/entity/avatar_members/EventTriggerMember.py'
    lines = path.read_text().splitlines(True)
    start = next(i for i, line in enumerate(lines) if line.startswith('    def ' + name + '('))
    end = start + 1
    while end < len(lines) and not (lines[end].startswith('    def ') or lines[end].startswith('    @')):
        end += 1
    source = textwrap.dedent(''.join(lines[start:end])) + '\n'
    tree = ast.parse(str(FIX.refactor_string(source, str(path))))
    exec(compile(tree, str(path) + ':' + name, 'exec'), env)
    return env[name]


class Arg(object):
    def __init__(self, name, kind=None):
        self.name = name
        self.kind = kind
    def getname(self):
        return self.name
    def convert(self, value):
        if self.kind is not None and type(value) is not self.kind:
            raise ValueError('typed value')
        return value
    def default_val(self):
        return 0



def make_member(env, rpc):
    member = type('Member', (object,), {})
    member.startEvent = original('startEvent', env)
    member.canStartEvent = original('canStartEvent', env)
    member.tryNotifyEvent = original('tryNotifyEvent', env)
    member.filterProcessingEvents = original('filterProcessingEvents', env)
    member.isEmergencyEvent = original('isEmergencyEvent', env)
    member.filterEventWithClientLimit = original('filterEventWithClientLimit', env)
    member.getEventsWithPriority = original('getEventsWithPriority', env)
    member.startEventReply = rpc(3, (Arg('e', int), Arg('r', int)))(original('startEventReply', env))
    member.pullEventsReply = rpc(3, (Arg('a'), Arg('p')))(original('pullEventsReply', env))
    member.pushEvents = rpc(3, (Arg('a'), Arg('p')))(original('pushEvents', env))
    member.eventOnLogin = rpc(3, (Arg('d'),))(original('eventOnLogin', env))
    return member


class _Py2Method(object):
    def __init__(self, function):
        self.im_func = function


def metaclass_copy(member):
    """Run the actual GameObjectMeta member-copy loop on a prebuilt Member."""
    source = (ROOT / 'analysis/original-py-640/com/base/game_object.py').read_text()
    start = source.index('class GameObjectMember')
    end = source.index('\nclass ', source.index('class GameObjectMeta'))
    lines = []
    for line in source[start:end].splitlines():
        lines.append('        method_cache[cls] = []' if 'method_cache[cls] = filter' in line else line)
    class _Updater(object):
        update_funcs = {}
        def insert(self, *args):
            pass
    class _UpdaterMgr(object):
        @classmethod
        def inst(cls):
            return _Updater()
    class _Inspect(object):
        @staticmethod
        def getmembers(obj, predicate=None):
            return [] if predicate else list(obj.__dict__.items())
        @staticmethod
        def ismethod(value):
            return isinstance(value, _Py2Method)
    module = types.ModuleType('com.base.game_object')
    module.members_cache = {}
    env = {'update_mgr': types.SimpleNamespace(UpdaterMgr=_UpdaterMgr),
           'LogManager': types.SimpleNamespace(), 'inspect': _Inspect,
           'sys': sys, 'types': types, 'members_cache': module.members_cache,
           'method_cache': {}}
    exec(compile('\n'.join(lines), 'game_object', 'exec'), env)
    base = env['GameObjectMember']
    metaclass = env['GameObjectMeta']
    module.members_cache[member] = [(name, _Py2Method(getattr(member, name)))
                                    for name in ('startEvent', 'eventOnLogin')]
    avatar = metaclass('ClientAvatar', (member,), {})
    return avatar, module


class EventInflightTests(unittest.TestCase):
    def setUp(self):
        self.event = 1030
        self.event2 = 1013254
        self.gg = types.ModuleType('gg')
        self._old_gg = sys.modules.get('gg')
        sys.modules['gg'] = self.gg
        self.addCleanup(self._restore_gg)
        self.gg.logic = NS(event_valid=True, event_semaphore={}, disable_event=lambda *a: setattr(self.gg.logic, 'event_valid', False))
        self.gg.emergency = NS(in_emergency=True)
        self.gg.battle = NS(_started=False)
        self.gg.ui = NS(lock=self.lock, unlock=self.unlock, panels=NS(city_event=None))
        self.contents = {self.event: {'release': True, 'priority': 1,
                                      'isEmergencyEvent': True, 'autoStart': True,
                                      'completeEnterMainPanel': False},
                         self.event2: {'release': True, 'priority': 1,
                                       'isEmergencyEvent': True, 'autoStart': True,
                                       'completeEnterMainPanel': False}}
        self.env = {'gg': self.gg, 'EventContentDataMod': NS(data=self.contents),
                    'const': NS(DEBUG_SKIP_EVENT=False, StoryRouteConst=NS(ZHOUNIAN2_TRIGGER_EVENTID=1)),
                    'print': lambda *a, **k: None}
        text = (ROOT / 'analysis/original-py-640/lib/common/rpcdecorator.py').read_text()
        source = text[text.index('class RpcMethod('):text.index('\ndef expose_to_client')]
        rpc_env = {'gg': self.gg, 'CLIENT_STUB': 3, 'Avatar': type('AvatarArg', (), {}),
                   'MailBox': type('MailboxArg', (), {}), 'ConvertError': ValueError,
                   '_logger': NS(warn=lambda *a: None, error=lambda *a: None)}
        exec(compile(str(FIX.refactor_string(source, 'rpcdecorator')), 'rpcdecorator', 'exec'), rpc_env)
        self.rpc = rpc_env['rpc_method']
        self.Member = make_member(self.env, self.rpc)
        self.avatar = self.member()
        self.gg.avatar = self.avatar
        self.avatar.logger = NS(debug=lambda *a: None)
        self.avatar.eventTriggerData = NS(
            availableEvents={}, processingEventsServer={self.event},
            processingEventsClient=set(), gmLockEvents=set(),
            addProcessingEvent=lambda e: self.avatar.eventTriggerData.processingEventsClient.add(e),
            initFromDict=lambda data: (self.avatar.eventTriggerData.processingEventsClient.clear(), setattr(self.gg.logic, 'event_valid', True)))
        self.avatar.weeknumData = NS(weeknum=1)
        self.avatar.queryEventOptAsk = lambda e: self.queries.append(e)
        self.avatar.completeBase = lambda e: self.business.append(e)
        self.avatar.last_request = None
        self.avatar.callServerMethodReliable = self.send
        self.gg.ui.panels.city_event = NS(notify_events=self.notify)
        self.sends = []
        self.callbacks = []
        self.active_at_send = []
        self.locks = 0
        self.lock_depth = []
        self.queries = []
        self.business = []
        self.fail_unlock = False

    def _restore_gg(self):
        if self._old_gg is None:
            sys.modules.pop('gg', None)
        else:
            sys.modules['gg'] = self._old_gg

    def lock(self, name):
        self.locks += 1
        self.lock_depth.append(name)

    def unlock(self, name):
        if self.fail_unlock:
            raise RuntimeError('reliable callback failure')
        self.locks -= 1
        if self.lock_depth:
            self.lock_depth.pop()

    def send(self, method, parameters, callback=None, needresult=False):
        self.sends.append((method, dict(parameters)))
        self.callbacks.append(callback)
        state = getattr(self.avatar, '_q7_event_inflight_state', {}) or {}
        self.active_at_send.append(parameters.get('e') in state.get('pending', {}))

    def notify(self, events):
        for event in events:
            self.avatar.startEvent(event)

    def member(self):
        return self.Member()

    def reply(self, event, result):
        self.avatar.startEventReply({'e': event, 'r': result})

    def test_old_consumer_ten_pulls_send_ten_and_new_helper_sends_one(self):
        self.avatar.tryNotifyEvent()
        for _ in range(9):
            self.avatar.tryNotifyEvent()
        self.assertEqual(len(self.sends), 10)
        self.assertEqual(self.locks, 10)

        owner = hook.install_event_trigger_inflight(self.Member, self.rpc)
        self.assertIs(owner, hook.install_event_trigger_inflight(self.Member, self.rpc))
        self.avatar._q7_event_inflight_state = None
        self.sends[:] = []
        self.callbacks[:] = []
        self.active_at_send[:] = []
        self.locks = 0
        self.lock_depth[:] = []
        self.avatar.tryNotifyEvent()
        for _ in range(9):
            self.avatar.tryNotifyEvent()
        self.assertEqual(len(self.sends), 1)
        self.assertEqual(self.locks, 1)
        self.assertEqual(self.active_at_send, [True])
        self.assertIn(self.event, self.avatar._q7_event_inflight_state['pending'])

    def test_success_once_duplicate_pull_and_late_reply_do_not_reopen(self):
        hook.install_event_trigger_inflight(self.Member, self.rpc)
        for _ in range(10):
            self.avatar.tryNotifyEvent()
        self.assertEqual(len(self.sends), 1)
        self.reply(self.event, 1)
        self.assertIn(self.event, self.avatar.eventTriggerData.processingEventsClient)
        self.assertIn(self.event, self.avatar._q7_event_inflight_state['pending'])
        self.assertEqual(self.queries, [self.event])
        self.assertEqual(self.business, [self.event])
        self.callbacks[0](None)
        self.assertNotIn(self.event, self.avatar._q7_event_inflight_state['pending'])
        self.assertEqual(self.locks, 0)
        self.reply(self.event, 1)
        for _ in range(10):
            self.avatar.tryNotifyEvent()
        self.assertEqual(self.queries, [self.event, self.event])
        self.assertEqual(self.business, [self.event])
        self.assertEqual(len(self.sends), 1)

    def test_failure_and_sync_exception_allow_retry(self):
        hook.install_event_trigger_inflight(self.Member, self.rpc)
        self.avatar.tryNotifyEvent()
        self.reply(self.event, 0)
        self.callbacks[0](None)
        self.assertEqual(self.locks, 0)
        self.assertNotIn(self.event, self.avatar.eventTriggerData.processingEventsClient)
        self.avatar.tryNotifyEvent()
        self.assertEqual(len(self.sends), 2)
        self.reply(self.event, 1)
        self.callbacks[-1](None)
        self.assertEqual(self.business, [self.event])
        self.assertEqual(self.locks, 0)

        self.avatar.eventTriggerData.processingEventsClient.clear()
        self.avatar.eventTriggerData.processingEventsServer.add(self.event2)
        self.avatar.eventTriggerData.availableEvents = {self.event2: {'saved': True}}
        self.avatar.callServerMethodReliable = lambda *a, **k: (_ for _ in ()).throw(IOError('sync'))
        with self.assertRaises(IOError):
            self.avatar.startEvent(self.event2)
        self.assertEqual(self.locks, 0)
        self.assertIn(self.event2, self.avatar.eventTriggerData.availableEvents)
        self.avatar.callServerMethodReliable = self.send
        self.avatar.startEvent(self.event2)
        self.assertEqual([p['e'] for m, p in self.sends][-1], self.event2)
        self.reply(self.event2, 1)
        self.callbacks[-1](None)
        self.assertEqual(self.locks, 0)

    def test_reliable_callback_exception_clears_marker(self):
        hook.install_event_trigger_inflight(self.Member, self.rpc)
        self.avatar.eventTriggerData.processingEventsServer.add(self.event2)
        self.avatar.startEvent(self.event2)
        self.fail_unlock = True
        with self.assertRaises(RuntimeError):
            self.callbacks[-1](None)
        self.assertNotIn(self.event2, self.avatar._q7_event_inflight_state['pending'])
        self.fail_unlock = False
        self.avatar.callServerMethodReliable = self.send
        self.avatar.startEvent(self.event2)
        self.assertEqual([p['e'] for m, p in self.sends].count(self.event2), 2)

    def test_parallel_events_have_independent_markers_and_business(self):
        hook.install_event_trigger_inflight(self.Member, self.rpc)
        self.avatar.eventTriggerData.processingEventsServer = {self.event, self.event2}
        self.avatar.tryNotifyEvent()
        self.assertEqual(sorted(p['e'] for m, p in self.sends), [self.event, self.event2])
        self.assertEqual(self.locks, 2)
        self.assertEqual(sorted(p['e'] for m, p in self.sends), sorted([self.event, self.event2]))
        self.reply(self.event, 1)
        self.reply(self.event2, 1)
        for callback in self.callbacks:
            callback(None)
        self.assertEqual(self.business, [self.event])
        self.assertEqual(self.locks, 0)

    def test_reload_and_week_cleanup_allow_new_start(self):
        hook.install_event_trigger_inflight(self.Member, self.rpc)
        self.avatar.tryNotifyEvent()
        self.reply(self.event, 1)
        self.avatar.eventOnLogin({'d': {}})
        self.avatar.tryNotifyEvent()
        self.assertEqual(len(self.sends), 2)

        self.reply(self.event, 1)
        self.avatar.pullEventsReply({'a': [], 'p': []})
        self.assertIn(self.event, self.avatar.eventTriggerData.processingEventsClient)
        old_data = self.avatar.eventTriggerData
        self.avatar.weeknumData = NS(weeknum=2)
        queries_before = len(self.queries)
        self.avatar.eventTriggerData = NS(
            availableEvents={}, processingEventsServer={self.event},
            processingEventsClient=set(), gmLockEvents=set(),
            addProcessingEvent=lambda e: self.avatar.eventTriggerData.processingEventsClient.add(e),
            initFromDict=lambda data: None)
        self.reply(self.event, 1)
        self.callbacks[-1](None)
        self.assertGreaterEqual(len(self.queries), queries_before)
        self.gg.logic.event_valid = True
        self.avatar.tryNotifyEvent()
        self.assertEqual(len(self.sends), 3)
        self.assertIn(self.event, self.avatar._q7_event_inflight_state['pending'])
        self.assertIsNot(old_data, self.avatar.eventTriggerData)

    def test_real_rpc_metadata_and_owner_preserved(self):
        owner = hook.install_event_trigger_inflight(self.Member, self.rpc)
        self.assertTrue(hasattr(self.Member.eventOnLogin, 'rpcmethod'))
        self.assertIs(getattr(self.Member.eventOnLogin, '_q7_event_inflight_owner'), owner)
        self.assertIs(getattr(self.Member.startEvent, '_q7_event_inflight_owner'), owner)
        self.avatar.eventTriggerData.processingEventsServer = {self.event}
        self.avatar.tryNotifyEvent()
        self.gg.avatar_callback_map = {}
        self.gg.avatar_callback_need_result = {}
        self.reply(self.event, 1)
        self.assertEqual(self.business, [self.event])
        self.assertIsInstance(self.gg.avatar_callback_map, dict)

    def test_avatar_class_copied_before_install_is_rebound_without_double_wrap(self):
        # GameObjectMeta copies raw Member functions onto ClientAvatar. Reproduce
        # that identity first, then install: Member-only wrapping is insufficient.
        Avatar = type('ClientAvatar', (object,), {})
        for name in ('startEvent', 'eventOnLogin'):
            setattr(Avatar, name, hook._raw(getattr(self.Member, name)))
        old = dict((name, hook._raw(getattr(Avatar, name))) for name in
                   ('startEvent', 'eventOnLogin'))
        game_object = types.ModuleType('com.base.game_object')
        game_object.members_cache = {self.Member: list(old.items())}
        with patch.dict(sys.modules, {'com.base.game_object': game_object}):
            owner = hook.install_event_trigger_inflight(self.Member, self.rpc, Avatar)
            self.assertIs(hook.install_event_trigger_inflight(self.Member, self.rpc, Avatar), owner)
        for name in old:
            self.assertIs(hook._raw(getattr(Avatar, name)), hook._raw(getattr(self.Member, name)))
            self.assertIsNot(hook._raw(getattr(Avatar, name)), old[name])
        cache = dict((name, hook._raw(value)) for name, value in game_object.members_cache[self.Member])
        self.assertIs(cache['startEvent'], hook._raw(self.Member.startEvent))
        self.assertIs(cache['startEventReply'], hook._raw(self.Member.startEventReply))

    def test_actual_gameobjectmeta_copy_before_install_rebinds(self):
        avatar, module = metaclass_copy(self.Member)
        old = dict((name, hook._raw(getattr(avatar, name))) for name in
                   ('startEvent', 'eventOnLogin'))
        with patch.dict(sys.modules, {'com.base.game_object': module}):
            owner = hook.install_event_trigger_inflight(self.Member, self.rpc, avatar)
            self.assertIs(hook.install_event_trigger_inflight(self.Member, self.rpc, avatar), owner)
        for name in old:
            self.assertIs(hook._raw(getattr(avatar, name)), hook._raw(getattr(self.Member, name)))
            self.assertIsNot(hook._raw(getattr(avatar, name)), old[name])
        cache = dict((name, hook._raw(value)) for name, value in module.members_cache[self.Member])
        self.assertIs(cache['startEvent'], hook._raw(self.Member.startEvent))
        self.assertIs(cache['eventOnLogin'], hook._raw(self.Member.eventOnLogin))

    def test_weeknum_inplace_reset_ignores_old_reply_before_new_request(self):
        hook.install_event_trigger_inflight(self.Member, self.rpc)
        self.avatar.tryNotifyEvent()
        self.reply(self.event, 1)
        self.avatar.eventOnLogin({'d': {}})
        self.avatar.tryNotifyEvent()
        self.assertIn(self.event, self.avatar._q7_event_inflight_state['pending'])
        queries = len(self.queries)
        business = len(self.business)
        self.avatar.weeknumData.weeknum = 2
        self.reply(self.event, 1)
        self.callbacks[-1](None)
        self.assertGreaterEqual(len(self.queries), queries)
        self.avatar.eventTriggerData.processingEventsClient.clear()
        self.gg.logic.event_valid = True
        self.avatar.tryNotifyEvent()
        self.assertEqual(len(self.sends), 3)
        self.reply(self.event, 1)
        self.assertGreaterEqual(len(self.business), business)

    def test_reliable_cache_full_precheck_no_lock_or_available_pop(self):
        hook.install_event_trigger_inflight(self.Member, self.rpc)
        self.avatar.reliableRpcCache = dict((i, None) for i in range(100))
        self.avatar.eventTriggerData.availableEvents = {self.event: {'saved': True}}
        self.assertFalse(self.avatar.startEvent(self.event))
        self.assertEqual(self.sends, [])
        self.assertEqual(self.locks, 0)
        self.assertIn(self.event, self.avatar.eventTriggerData.availableEvents)
        self.assertNotIn(self.event, self.avatar._q7_event_inflight_state['pending'])

    def test_unsolicited_typed_reply_without_active_start_is_consumed(self):
        hook.install_event_trigger_inflight(self.Member, self.rpc)
        self.avatar.eventTriggerData.processingEventsServer = {self.event}
        self.reply(self.event, 1)
        self.assertEqual(self.queries, [self.event])
        self.assertEqual(self.business, [self.event])
        self.assertEqual(self.sends, [])

    def test_start_event_option_typed_reply_is_not_gated(self):
        hook.install_event_trigger_inflight(self.Member, self.rpc)
        self.contents[1011] = {'release': True, 'priority': 1,
                               'isEmergencyEvent': True, 'autoStart': True,
                               'completeEnterMainPanel': False}
        self.avatar.eventTriggerData.processingEventsServer = {1011}
        self.reply(1011, 1)
        self.assertEqual(self.queries, [1011])
        self.assertEqual(self.business, [1011])
        self.assertEqual(self.sends, [])

    def test_social_event_typed_reply_is_not_gated(self):
        hook.install_event_trigger_inflight(self.Member, self.rpc)
        self.avatar.eventTriggerData.processingEventsServer = {self.event2}
        self.reply(self.event2, 1)
        self.assertEqual(self.queries, [self.event2])
        self.assertEqual(self.business, [self.event2])
        self.assertEqual(self.sends, [])

    def test_python2_unbound_method_attribute_write_requires_im_func(self):
        class Unbound(object):
            __slots__ = ('im_func',)
            def __init__(self, function):
                object.__setattr__(self, 'im_func', function)
            def __setattr__(self, name, value):
                raise AttributeError('unbound instancemethod attribute write forbidden')

        def function():
            return None
        method = Unbound(function)
        with self.assertRaises(AttributeError):
            method._q7_event_inflight_owner = object()
        raw = hook._raw(method)
        self.assertIs(raw, function)
        raw._q7_event_inflight_owner = 'owner'
        self.assertEqual(function._q7_event_inflight_owner, 'owner')

    def test_new_class_method_attribute_writes_use_raw(self):
        source = (ROOT / 'runtime/project7_startup_hook.py').read_text()
        import re
        forbidden = re.compile(r'\b(?:member|avatar|cls)\.(?:startEvent|eventOnLogin|startEventReply|pullEventsReply|pushEvents)\s*\.\s*_q7')
        self.assertIsNone(forbidden.search(source))
        self.assertIn('_raw(member.startEvent)._q7_event_inflight_owner', source)

    def test_1013254_uses_the_same_generic_path(self):
        hook.install_event_trigger_inflight(self.Member, self.rpc)
        self.avatar.eventTriggerData.processingEventsServer = {self.event2}
        for _ in range(8):
            self.avatar.tryNotifyEvent()
        self.assertEqual(len(self.sends), 1)
        self.assertEqual(self.sends[0][1]['e'], self.event2)
        self.reply(self.event2, 1)
        self.assertEqual(self.business, [self.event2])


if __name__ == '__main__':
    unittest.main()
