"""Host-only contracts through original reply bodies and original RPC decoder."""
import ast
import copy
import importlib.util
from pathlib import Path
import sys
import re
import textwrap
from types import ModuleType, SimpleNamespace
import unittest
from unittest.mock import patch
import warnings

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'runtime'))
from offline_rpc_rejections import RPC_REJECTION_OPERATIONS, RPC_CALLBACK_REJECTION_OPERATIONS, prepare_rpc_rejection, make_ending_request_guard, make_puzzle_scene_guards, make_puzzle_ui_guards, make_puzzle_request_guard, make_puzzle_reply_guard
with warnings.catch_warnings():
    warnings.simplefilter('ignore', DeprecationWarning)
    from lib2to3.refactor import RefactoringTool


def original_tree(source, path):
    source = str(RefactoringTool(['lib2to3.fixes.fix_print', 'lib2to3.fixes.fix_except']).refactor_string(source, str(path)))
    return ast.parse(source)


def original_definition(path, name, namespace, decorated=True):
    lines = path.read_text().splitlines(True)
    start = next(i for i, line in enumerate(lines) if re.match(r'^ *(?:def|class) ' + re.escape(name) + r'\(', line))
    depth = len(lines[start]) - len(lines[start].lstrip())
    end = start + 1
    while end < len(lines):
        line = lines[end]
        if line.strip() and not line.lstrip().startswith('#') and len(line) - len(line.lstrip()) <= depth:
            break
        end += 1
    if decorated:
        while start and lines[start-1].lstrip().startswith('@'):
            start -= 1
    source = textwrap.dedent(''.join(lines[start:end]))
    node = next(node for node in ast.walk(original_tree(source, path))
                if isinstance(node, (ast.ClassDef, ast.FunctionDef)) and node.name == name)
    if not decorated and isinstance(node, ast.FunctionDef):
        node.decorator_list = []
    exec(compile(ast.Module(body=[node], type_ignores=[]), str(path), 'exec'), namespace)
    return namespace[name]


class NativeId:
    def __init__(self, value):
        if not isinstance(value, str) or len(value) != 24 or any(c not in '0123456789abcdef' for c in value):
            raise ValueError('invalid ObjectId')
        self.value = value


ID_MANAGER = SimpleNamespace(is_id_type=lambda value: isinstance(value, NativeId),
    bytes2id=lambda value: (_ for _ in ()).throw(ValueError('not binary')),
    str2id=NativeId)

HERO = ROOT / 'analysis/decompiled/HeroMgrMember.py'
LUCKY = ROOT / 'analysis/research-agent/LuckyDrawMember.py'
REWARD = ROOT / 'analysis/decompiled/RewardMember.py'
PREVIEW = ROOT / 'reports/rpc-rejections-HeroBuyPreviewMember-original.py'
CASES = [
    ('requestTryPlayBattle', PREVIEW, 'requestTryPlayBattle', (24, 265, 0), 'requestTryPlayBattle'),
    ('requestRandomRealtimeGiftBag', REWARD, 'requestRandomRealtimeGiftBag', (1,), 'requestRandomRealtimeGiftBag'),
    ('buyRealtimeGiftBag', REWARD, 'buyRealtimeGiftBag', (123,), 'buyRealtimeGiftBag'),
    ('incHeroStarOrder', HERO, 'incHeroStarRequest', (24, None), None),
    ('upgradeTreasure', HERO, 'upgradeTreasure', (24, '0123456789abcdef01234567'), None),
    ('upgradeTreasureTargetLv', HERO, 'upgradeTreasureTargetLv', (24, '0123456789abcdef01234567', 8), None),
    ('requestExchangeSuipianWithItem', LUCKY, 'requestExchangeSuipianWithItem', (1, 24, 5), 'requestExchangeSuipianWithItem'),
    ('requestExchangeActivityHeroProg', LUCKY, 'requestExchangeActivityHeroProg', (24, 5), 'requestExchangeActivityHeroProg'),
    ('giveCatFriendly', LUCKY, 'giveCatFriendly', (1, 0), 'giveCatFriendly'),
    ('yjtFragmentExchange', ROOT / 'analysis/decompiled/CommonMember.py', 'yjtFragmentExchange', ([(1, 2, 3)],), 'yjtFragmentExchange'),
    ('commonItemFusionAsk', ROOT / 'analysis/research-agent/InvMember.py', 'commonItemFusion', (1, 2, 4), 'commonItemFusion'),
    ('requestGetHero', HERO, 'requestGetHero', (1, 24), 'requestGetHero'),
    ('getCatHero', LUCKY, 'getCatHero', (0,), 'getCatHero'),
    ('requestAddAxiliyaMood', LUCKY, 'requestAddAxiliyaMood', (), 'requestAddAxiliyaMood'),
    ('requestCaijianOp', LUCKY, 'requestCaijianOp', (), 'requestCaijianOp'),
    ('requestGetAxiliyaHero', LUCKY, 'requestGetAxiliyaHero', (), 'requestGetAxiliyaHero'),
]


class OriginalReplyRejectionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        spec = importlib.util.spec_from_file_location('rpc_rejection_gateway', ROOT / 'runtime/local_gateway.py')
        cls.gateway = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.gateway)
        cls.gateway._f7_log = lambda message: None

    def setUp(self):
        self.locks, self.messages, self.pending, self.wires = [], [], [], []
        self.logs = []
        self.gateway._f7_log = self.logs.append
        self.addCleanup(lambda: self.assertFalse([line for line in self.logs if line.startswith('Reply ')]))
        self.callback_ids = []
        self.owner = SimpleNamespace()
        self.gg = SimpleNamespace(avatar=self.owner, avatar_callback_map={}, avatar_callback_need_result={},
            ui=SimpleNamespace(lock=lambda name=None, **kw: self.locks.append(name),
                unlock=lambda name=None, **kw: self.locks.remove(name),
                panels=SimpleNamespace(common_message=SimpleNamespace(notify_message=self.messages.append))))
        id_module = ModuleType('common.IdManager'); id_module.IdManager = ID_MANAGER
        self.modules = patch.dict(sys.modules, {'gg': self.gg, 'common.IdManager': id_module})
        self.modules.start(); self.addCleanup(self.modules.stop)
        namespace = {'StandardError': Exception, 'IdManager': ID_MANAGER, 'unicode': str}
        codec_path = ROOT / 'analysis/original-py-640/lib/common/RpcMethodArgs.py'
        for name in ('ConvertError', 'RpcMethodArg', 'NoLimit', 'NumeralLimit', 'Int', 'Bool', 'Dict', 'Uuid'):
            original_definition(codec_path, name, namespace)
        namespace.update(gg=self.gg, CLIENT_STUB=3, Avatar=type('Avatar', (), {}),
            MailBox=type('MailBox', (), {}), xrange=range,
            _logger=SimpleNamespace(warn=lambda *args: self.fail(args), error=lambda *args: self.fail(args)))
        decorator = ROOT / 'analysis/original-py-640/lib/common/rpcdecorator.py'
        original_definition(decorator, 'RpcMethod', namespace)
        original_definition(decorator, 'rpc_method', namespace)
        namespace['RGRD'] = SimpleNamespace(data={123: {'libaoquan_price': 0}})
        self.namespace = namespace
        self.gg.ui._tree = SimpleNamespace(proc_event=lambda *args, **kwargs: None)
        self.proxy = object.__new__(self.gateway.LocalProxy)
        self.proxy.owner = self.owner
        self.owner.server = self.proxy
        self.proxy.defer = lambda delay, callback: self.pending.append(callback)
        self.proxy.save_progress = lambda: self.fail('rejection attempted to persist')
        self.owner.reliableRpcAck = lambda body: self.wires.append(('reliableRpcAck', body))
        self.owner.luckyDrawData = SimpleNamespace(canGiveCatFriendly=lambda ty: True, canGetCatHero=lambda ty: True)
        self.owner.rewardData = SimpleNamespace(realtime_gift_bag=SimpleNamespace(
            lucky_tag=True, show_flag=0, gift_dict={123: (False, 1)}))
        self.owner.invContainByIDs = lambda costs: True
        self.owner.canUpgradeTreasure = lambda hero, uid: True
        def request(name, args, callback=None):
            if callback is not None:
                cbid = 'original-callback-17'
                self.callback_ids.append(cbid)
                self.gg.avatar_callback_map[cbid] = callback
                args = dict(args, _cbid_=cbid)
            self.proxy.call_server_method(name, args)
        self.owner.callServerMethod = request

    def test_official640_new_hang_paths_use_real_requests_and_negative_consumers(self):
        base = ROOT / 'analysis/original-py-640/entity/avatar_members'
        city, story, week = (base / name for name in ('CityMember.py', 'StoryMember.py', 'WeekNumMember.py'))
        def reliable(method, parameters, callback=None):
            cbid = 'official640-reliable-callback'
            if callback is not None:
                self.gg.avatar_callback_map[cbid] = callback
            envelope = {'w': {'m': method, 'p': parameters, 'r': 640}}
            if callback is not None:
                envelope['_cbid_'] = cbid
            self.pending.append(lambda: self.proxy.reliable_call(envelope))
        self.owner.callServerMethodReliable = reliable
        self.owner.cityData = SimpleNamespace(actionConsumeReward=True, currJingshenliAddTimes=0)
        self.owner.storyData = SimpleNamespace(change_week=False, puzzle_room_clues=[17])
        self.owner.handleIncWeekCb = None
        self.owner.weeknumData = SimpleNamespace(weeknum=2, daynum=0, level_score={0: 1})
        self.owner._getWeekLastLevel = lambda pair: 0
        self.namespace['AVGLevelInfoMod'] = SimpleNamespace(data={(1, 1): {'is_open': 1}})
        self.namespace['ActivityPowerRecoverData'] = SimpleNamespace(data={})
        self.namespace['const'] = SimpleNamespace(ActivityPower=SimpleNamespace(JINGSHENLI=1))
        self.owner.checkCanLogin777PowerTime = lambda: True
        self.owner.updateLastStoryLineClick = lambda: True
        self.gg.logic = SimpleNamespace(enter_emergency=lambda: self.fail('refusal advanced week'))
        for name, path, method, args, lock in (
            ('zhaiRequest', city, 'zhaiRequest', (), 'zhai'),
            ('requestRecoverJingshenli', city, 'requestRecoverJingshenli', (), 'requestRecoverJingshenli'),
            ('puzzleRoomGetClue', story, 'puzzleRoomGetClue', (999999,), 'puzzleRoomGetClue'),
            ('requestTriggerDaXuanWo', story, 'requestTriggerDaXuanWo', (), 'requestTriggerDaXuanWo'),
            ('requestChangeAVGLevel', week, 'requestChangeAVGLevel', (1, 1), 'requestChangeAVGLevel'),
            ('actionRewardRequest', city, 'actionRewardRequest', (), 'action_reward'),
            ('requestTriggerEventByEnding', story, 'requestTriggerEventByEnding', (123,), None)):
            with self.subTest(request=name):
                self.wires.clear(); self.messages.clear()
                self.install_reply(name, path)
                original = original_definition(path, method, self.namespace, decorated=False)
                if name == 'requestTriggerEventByEnding':
                    original = make_ending_request_guard(original)
                original(self.owner, *args)
                if lock:
                    self.assertEqual(self.locks, [lock])
                self.pending.pop()()
                self.assertEqual(self.locks, [])
                self.assertEqual(self.gg.avatar_callback_map, {})
                self.assertEqual(len(self.messages), 1)
                self.assertEqual(self.owner.storyData.puzzle_room_clues, [17])
                self.assertFalse(self.owner.storyData.change_week)
        self.assertIsNone(self.owner.handleIncWeekCb)

    def test_ending_refusal_restores_nondefault_prior_values_and_throttle(self):
        path = ROOT / 'analysis/original-py-640/entity/avatar_members/StoryMember.py'
        prior_callback = lambda: self.fail('prior callback must not execute')
        self.owner.storyData = SimpleNamespace(change_week=True, last_storyline_click=17)
        self.owner.weeknumData = SimpleNamespace(weeknum=2, daynum=3)
        self.owner.handleIncWeekCb = prior_callback
        self.owner.guessServerTime = lambda: 200
        update = original_definition(path, 'updateLastStoryLineClick', {'gg': self.gg}, decorated=False)
        self.owner.updateLastStoryLineClick = lambda: update(self.owner)
        self.gg.logic = SimpleNamespace(enter_emergency=lambda: self.fail('new week callback invoked'))
        self.install_reply('requestTriggerEventByEnding', path)
        request = make_ending_request_guard(original_definition(path, 'requestTriggerEventByEnding', self.namespace, decorated=False))
        request(self.owner, 123)
        self.assertEqual(self.owner.storyData.last_storyline_click, 200)
        self.assertIs(self.owner.handleIncWeekCb, self.gg.logic.enter_emergency)
        self.pending.pop()()
        self.assertTrue(self.owner.storyData.change_week)
        self.assertEqual(self.owner.storyData.last_storyline_click, 17)
        self.assertIs(self.owner.handleIncWeekCb, prior_callback)
        self.assertFalse(hasattr(self.owner, '_f7_ending_request_context'))
        self.assertEqual(self.wires, [('replyTriggerEventByEnding', {'r': False})])

    def test_ending_refusal_does_not_clear_new_week_or_replacement_callback(self):
        path = ROOT / 'analysis/original-py-640/entity/avatar_members/StoryMember.py'
        self.owner.storyData = SimpleNamespace(change_week=False)
        self.owner.weeknumData = SimpleNamespace(weeknum=2, daynum=0)
        self.owner.updateLastStoryLineClick = lambda: True
        self.gg.logic = SimpleNamespace(enter_emergency=lambda: None)
        self.install_reply('requestTriggerEventByEnding', path)
        make_ending_request_guard(original_definition(path, 'requestTriggerEventByEnding', self.namespace, decorated=False))(self.owner, 123)
        self.owner.weeknumData.weeknum = 3
        self.pending.pop()()
        self.assertTrue(self.owner.storyData.change_week)
        self.assertIs(self.owner.handleIncWeekCb, self.gg.logic.enter_emergency)
        self.assertEqual(self.wires, [])
        self.assertEqual(self.messages, [])

    def test_ending_refusal_does_not_undo_a_new_transition_before_native_week_sync(self):
        path = ROOT / 'analysis/original-py-640/entity/avatar_members/StoryMember.py'
        self.proxy.week_protocol = {'transition': None}
        self.owner.storyData = SimpleNamespace(change_week=False)
        self.owner.weeknumData = SimpleNamespace(weeknum=2, daynum=0)
        self.owner.updateLastStoryLineClick = lambda: True
        self.gg.logic = SimpleNamespace(enter_emergency=lambda: None)
        self.install_reply('requestTriggerEventByEnding', path)
        make_ending_request_guard(original_definition(path, 'requestTriggerEventByEnding', self.namespace, decorated=False))(self.owner, 123)
        self.proxy.week_protocol['transition'] = {'id': 'new-committed-transition'}
        self.pending.pop()()
        self.assertTrue(self.owner.storyData.change_week)
        self.assertIs(self.owner.handleIncWeekCb, self.gg.logic.enter_emergency)
        self.assertEqual(self.wires, [])
        self.assertEqual(self.messages, [])

    def test_canteen_replacement_panel_and_callback_are_preserved(self):
        self.gg.ui.panels.city_canteen = SimpleNamespace(cover=True)
        old = lambda *args: self.fail('success callback invoked')
        self.gg.avatar_callback_map['cb'] = old
        self.proxy.call_server_method('canteenRequest', {'_cbid_': 'cb'})
        newer = lambda *args: None
        replacement = SimpleNamespace(cover=True)
        self.gg.avatar_callback_map['cb'] = newer
        self.gg.ui.panels.city_canteen = replacement
        self.pending.pop()()
        self.assertTrue(replacement.cover)
        self.assertIs(self.gg.avatar_callback_map['cb'], newer)
        self.assertEqual(self.messages, [])

    def test_official640_yazhi_refusal_unlocks_without_fabricated_battle_result(self):
        self.owner.battleYazhiAvailable = lambda scene, heroes: True
        self.owner.battleYazhiReply = lambda payload: self.fail('success-only battle consumer invoked')
        original_definition(ROOT / 'analysis/original-py-640/entity/avatar_members/BattleStageMember.py',
                            'battleYazhiAsk', self.namespace, decorated=False)(self.owner, 1, 100, [24])
        self.assertEqual(self.locks, ['yazhi'])
        self.pending.pop()()
        self.assertEqual(self.locks, [])
        self.assertEqual(self.wires, [])
        self.assertEqual(len(self.messages), 1)

    def test_official640_mainline_cg_refusal_uses_false_consumer_and_preserves_claims(self):
        path = ROOT / 'analysis/original-py-640/entity/avatar_members/OddsAndEndsMember.py'
        self.owner.oddsAndEndsData = SimpleNamespace(mainline_cg_rewards={1: True})
        self.install_reply('requestMainlineCgRewards', path)
        original_definition(path, 'requestMainlineCgRewards', self.namespace, decorated=False)(self.owner, 1, 2)
        self.assertEqual(self.locks, ['requestMainlineCgRewards'])
        self.pending.pop()()
        self.assertEqual(self.locks, [])
        self.assertEqual(self.owner.oddsAndEndsData.mainline_cg_rewards, {1: True})
        self.assertEqual(self.wires, [('replyMainlineCgRewards', {'rs': False, 'i': {}})])

    def test_official640_destroy_refusal_never_invokes_destructive_original_callback(self):
        path = ROOT / 'analysis/original-py-640/entity/avatar_members/CityMember.py'
        self.gg.ui._tree.proc_event = lambda *args, **kwargs: self.fail('destroy refusal emitted business event')
        original_definition(path, 'player_destroy_building', self.namespace, decorated=False)(self.owner, 'uid')
        self.assertEqual(self.locks, ['building_destroy'])
        self.pending.pop()()
        self.assertEqual(self.locks, [])
        self.assertEqual(self.gg.avatar_callback_map, {})
        self.assertEqual(self.wires, [])
        self.assertEqual(len(self.messages), 1)

    def test_official640_canteen_refusal_uncovers_original_panel_without_success_animation(self):
        path = ROOT / 'analysis/original-py-640/entity/avatar_members/CityMember.py'
        self.owner.canteenRequest = lambda *args: original_definition(path, 'canteenRequest', self.namespace, decorated=False)(self.owner, *args)
        panel = SimpleNamespace(choosen_hero=[1], cover=False)
        self.owner.heroMgrData = SimpleNamespace(getHero=lambda hero: SimpleNamespace(getCurFatigueValue=lambda: 2))
        self.gg.ui.panels.city_canteen = panel
        original_definition(ROOT / 'analysis/original-py-640/cocos/panels/city_canteen.py', '_on_eat_click', {'gg': self.gg}, decorated=False)(panel)
        self.assertTrue(panel.cover)
        self.pending.pop()()
        self.assertFalse(panel.cover)
        self.assertEqual(self.gg.avatar_callback_map, {})
        self.assertEqual(self.wires, [])
        self.assertEqual(len(self.messages), 1)

    def test_callback_absent_new_requests_release_only_their_exact_lock(self):
        for request, lock in (('zhaiRequest', 'zhai'), ('requestTriggerDaXuanWo', 'requestTriggerDaXuanWo'),
                              ('requestChangeAVGLevel', 'requestChangeAVGLevel'), ('playerDestroyBuilding', 'building_destroy'),
                              ('actionRewardRequest', 'action_reward')):
            self.locks[:] = ['other', lock]
            if request in ('zhaiRequest', 'requestChangeAVGLevel'):
                base = ROOT / 'analysis/original-py-640/entity/avatar_members'
                self.install_reply(request, base / ('CityMember.py' if request == 'zhaiRequest' else 'WeekNumMember.py'))
            self.assertTrue(self.proxy.reject_unimplemented_rpc(request, {}))
            self.assertEqual(self.locks, ['other'])

    def test_new_unlock_callbacks_with_unregistered_wire_id_still_release_exact_lock(self):
        for request, lock in (('zhaiRequest', 'zhai'), ('requestTriggerDaXuanWo', 'requestTriggerDaXuanWo'),
                              ('requestChangeAVGLevel', 'requestChangeAVGLevel'), ('actionRewardRequest', 'action_reward')):
            self.locks[:] = ['other', lock]
            base = ROOT / 'analysis/original-py-640/entity/avatar_members'
            path = base / ('CityMember.py' if request == 'zhaiRequest' else 'WeekNumMember.py')
            self.install_reply(request, path)
            self.assertTrue(self.proxy.reject_unimplemented_rpc(request, {}, 'unregistered-id'))
            self.assertEqual(self.locks, ['other'])
            self.assertEqual(self.gg.avatar_callback_map, {})

    def install_original_puzzle_scene_flow(self):
        base = ROOT / 'analysis/original-py-640'
        self.owner.storyData = SimpleNamespace(route='non-managed-room', puzzle_room_clues=[])
        self.owner.weeknumData = SimpleNamespace(weeknum=4, daynum=2)
        self.proxy.week_protocol = {'transition': None}
        self.gg.game_width, self.gg.game_height = 1280, 720
        ui_methods = {name: original_definition(base / 'cocos/ui_manager.py', name, {'gg': self.gg}, decorated=False)
                      for name in ('lock', 'unlock', 'reset_lock')}
        ui_class = type('OriginalUIManagerBodies', (), ui_methods)
        make_puzzle_ui_guards(ui_class)
        ui = ui_class()
        ui._lock, ui.recon_lock = {}, 0
        ui.panels = SimpleNamespace(common_message=SimpleNamespace(notify_message=self.messages.append))
        self.wait_events = []
        ui.panels.wait = SimpleNamespace(notify_show=lambda *args: self.wait_events.append('show'),
            notify_hide=lambda: self.wait_events.append('hide'), cancel_timer=lambda: self.wait_events.append('cancel'))
        ui.panels.storyline_sailafeimu_search = SimpleNamespace(can_operate=True, timer=None)
        self.gg.ui = ui
        getter = original_definition(base / 'game_scene/city_base.py', 'main_ui', {'gg': self.gg}, decorated=False)
        city_base = SimpleNamespace(CityBase=type('NativeSceneBase', (), {'main_ui': property(getter)}))
        namespace = {'city_base': city_base, 'gg': self.gg,
                     'city_camera': SimpleNamespace(CityCamera=lambda: object()),
                     'const': SimpleNamespace(Touch=SimpleNamespace(FIELD_X=0, FIELD_Y=1))}
        scene_class = original_definition(base / 'game_scene/city_jiemi.py', 'Scene', namespace)
        make_puzzle_scene_guards(scene_class)
        scene = scene_class()
        scene.on_init(map_id='original/unmanaged-room', puzzle_room_id=8)
        self.picks = []
        scene.res_comp = SimpleNamespace(active_scn=SimpleNamespace(pick=lambda *args: (self.picks.append(args), None, None)))
        # pick's first item must be None; recording is the native dependency stub.
        def pick(*args):
            self.picks.append(args)
            return None, None, None
        scene.res_comp.active_scn.pick = pick
        self.gg.jiemi = scene
        path = base / 'entity/avatar_members/StoryMember.py'
        original_request = original_definition(path, 'puzzleRoomGetClue', self.namespace, decorated=False)
        guarded_request = make_puzzle_request_guard(original_request)
        self.owner.puzzleRoomGetClue = lambda clue: guarded_request(self.owner, clue)
        consumer = make_puzzle_reply_guard(original_definition(path, 'puzzleRoomGetClueReturn', self.namespace))
        def receive(payload):
            self.wires.append(('puzzleRoomGetClueReturn', copy.deepcopy(payload)))
            return consumer(self.owner, payload)
        self.owner.puzzleRoomGetClueReturn = receive
        return scene, ui

    def test_unmanaged_original_scene_false_consumer_restores_real_touch_caller_and_retry(self):
        scene, ui = self.install_original_puzzle_scene_flow()
        for clue in (901, 902):
            scene.getClue({'clue_id': clue})
            self.assertTrue(scene.lock_touch)
            scene.on_touches_ended((1, 2))
            self.assertEqual(len(self.picks), clue - 901)
            self.assertEqual(ui._lock, {'puzzleRoomGetClue': 1})
            self.pending.pop()()
            self.assertFalse(scene.lock_touch)
            self.assertEqual(ui._lock, {'puzzleRoomGetClue': 0})
            self.assertEqual(ui.recon_lock, 0)
            scene.on_touches_ended((1, 2))
        self.assertEqual(len(self.picks), 2)
        self.assertEqual(self.owner.storyData.puzzle_room_clues, [])
        self.assertEqual([body for name, body in self.wires], [
            {'r': False, 'c': 901, 'g': False}, {'r': False, 'c': 902, 'g': False}])
        self.assertIn('cancel', self.wait_events)

    def test_original_puzzle_two_requests_drain_counted_waits_in_either_order_and_duplicates_do_nothing(self):
        for reverse in (False, True):
            with self.subTest(reverse=reverse):
                scene, ui = self.install_original_puzzle_scene_flow()
                scene.getClue({'clue_id': 901})
                scene.getClue({'clue_id': 902})
                first, second = self.pending[:]
                self.pending.clear()
                deliver = (second, first) if reverse else (first, second)
                deliver[0]()
                self.assertTrue(scene.lock_touch)
                self.assertEqual(ui._lock['puzzleRoomGetClue'], 1)
                deliver[1]()
                self.assertFalse(scene.lock_touch)
                self.assertEqual(ui._lock['puzzleRoomGetClue'], 0)
                ui.lock('puzzleRoomGetClue')
                deliver[0](); deliver[1]()
                self.assertEqual(ui._lock['puzzleRoomGetClue'], 1)

    def test_old_puzzle_refusal_preserves_same_named_new_wait_and_scene_after_reset_or_manual_unlock(self):
        for reset in (False, True):
            with self.subTest(reset=reset):
                scene, ui = self.install_original_puzzle_scene_flow()
                scene.getClue({'clue_id': 901})
                old = self.pending.pop()
                if reset:
                    ui.reset_lock()
                else:
                    ui.unlock('puzzleRoomGetClue')
                scene.unlock_touch()
                scene.getClue({'clue_id': 902})
                new = self.pending.pop()
                old()
                self.assertTrue(scene.lock_touch)
                self.assertEqual(ui._lock['puzzleRoomGetClue'], 1)
                new()
                self.assertFalse(scene.lock_touch)
                self.assertEqual(ui._lock['puzzleRoomGetClue'], 0)

    def test_puzzle_refusal_never_releases_replaced_native_context_or_another_animation(self):
        for change in ('scene', 'avatar', 'ui', 'story', 'week', 'protocol', 'room', 'camera',
                       'panel', 'panel-busy', 'panel-timer', 'q7-inflight', 'already-unlocked'):
            with self.subTest(change=change):
                self.gg.avatar = self.owner
                scene, ui = self.install_original_puzzle_scene_flow()
                scene.getClue({'clue_id': 901})
                deliver = self.pending.pop()
                if change == 'scene':
                    self.gg.jiemi = SimpleNamespace(lock_touch=True)
                elif change == 'avatar':
                    self.gg.avatar = SimpleNamespace()
                elif change == 'ui':
                    self.gg.ui = SimpleNamespace(_lock={'puzzleRoomGetClue': 1})
                elif change == 'story':
                    self.owner.storyData = SimpleNamespace(route='non-managed-room', puzzle_room_clues=[])
                elif change == 'week':
                    self.owner.weeknumData.daynum += 1
                elif change == 'protocol':
                    self.proxy.week_protocol['transition'] = {'id': 'new'}
                elif change == 'room':
                    scene.room_id = 9
                elif change == 'camera':
                    scene.camera_state = 2
                elif change == 'panel':
                    ui.panels.storyline_sailafeimu_search = SimpleNamespace(can_operate=True, timer=None)
                elif change == 'panel-busy':
                    scene.main_ui.can_operate = False
                elif change == 'panel-timer':
                    scene.main_ui.timer = object()
                elif change == 'q7-inflight':
                    self.owner._q7_puzzle_inflight = ('native-success', 901, scene)
                elif change == 'already-unlocked':
                    scene.unlock_touch()
                    generation = scene._f7_puzzle_touch_generation
                deliver()
                if change == 'already-unlocked':
                    self.assertFalse(scene.lock_touch)
                    self.assertEqual(scene._f7_puzzle_touch_generation, generation)
                else:
                    self.assertTrue(scene.lock_touch)
                if change == 'scene':
                    self.assertTrue(self.gg.jiemi.lock_touch)
                if change == 'ui':
                    self.assertEqual(self.gg.ui._lock['puzzleRoomGetClue'], 1)
                self.owner.__dict__.pop('_q7_puzzle_inflight', None)

    def test_legitimate_original_success_animation_is_never_unlocked_by_late_refusal(self):
        scene, ui = self.install_original_puzzle_scene_flow()
        scene.getClue({'clue_id': 901})
        old = self.pending.pop()
        panel = scene.main_ui
        panel.total_num = 4
        panel.pro = SimpleNamespace(setPercent=lambda value: None)
        panel.cur_clues = SimpleNamespace(setString=lambda value: None)
        self.gg.audio_mgr = SimpleNamespace(ui_sound=lambda value: None)
        self.animation_callbacks = []
        self.gg.exec_delay = lambda delay, callback: self.animation_callbacks.append(callback) or object()
        play = original_definition(ROOT / 'analysis/original-py-640/cocos/panels/storyline_sailafeimu_search.py',
                                   'play_animation', {'gg': self.gg, 'time': SimpleNamespace(time=lambda: 0)}, decorated=False)
        panel.play_animation = lambda before, after: play(panel, before, after)
        ui.panels.dialogue = SimpleNamespace(trigger_client_dialogue_continue=lambda dialogue, end_cb: end_cb())
        self.namespace['PUZZLE_ROOM_CLUE'] = SimpleNamespace(data={901: {'client_dialogue': 123}})
        # The helper compiled the real consumer with the shared namespace above.
        self.owner.puzzleRoomGetClueReturn({'r': True, 'c': 901, 'g': False})
        self.assertEqual(self.owner.storyData.puzzle_room_clues, [901])
        self.assertFalse(panel.can_operate)
        self.assertIsNotNone(panel.timer)
        self.assertTrue(scene.lock_touch)
        ui.lock('puzzleRoomGetClue')
        old()
        self.assertTrue(scene.lock_touch)
        self.assertEqual(ui._lock['puzzleRoomGetClue'], 1)
        self.assertEqual(len(self.animation_callbacks), 1)

    def test_puzzle_cleanup_preserves_other_original_ui_lock_and_wait_accounting(self):
        scene, ui = self.install_original_puzzle_scene_flow()
        ui.lock('another-native-operation')
        scene.getClue({'clue_id': 901})
        self.pending.pop()()
        self.assertFalse(scene.lock_touch)
        self.assertEqual(ui._lock, {'another-native-operation': 1, 'puzzleRoomGetClue': 0})
        self.assertEqual(ui.recon_lock, 1)
        self.assertNotIn('cancel', self.wait_events)
        ui.unlock('another-native-operation')
        self.assertEqual(ui.recon_lock, 0)
        self.assertIn('cancel', self.wait_events)

    def test_foreign_backend_scene_caller_is_not_managed_by_local_refusal_guard(self):
        scene, ui = self.install_original_puzzle_scene_flow()
        self.owner.server = SimpleNamespace(owner=self.owner)
        scene.getClue({'clue_id': 901})
        self.pending.pop()()
        self.assertTrue(scene.lock_touch)
        self.assertFalse(hasattr(scene, '_f7_puzzle_latest_request'))
        self.assertEqual(ui._lock['puzzleRoomGetClue'], 0)

    def test_naked_ui_wait_drain_can_wake_only_the_completed_authorized_scene_request(self):
        for naked_first in (False, True):
            for reverse in (False, True):
                with self.subTest(naked_first=naked_first, reverse=reverse):
                    scene, ui = self.install_original_puzzle_scene_flow()
                    if naked_first:
                        self.owner.puzzleRoomGetClue(902)
                        naked = self.pending.pop()
                    scene.getClue({'clue_id': 901})
                    authorized = self.pending.pop()
                    if not naked_first:
                        self.owner.puzzleRoomGetClue(902)
                        naked = self.pending.pop()
                    deliveries = (naked, authorized) if reverse else (authorized, naked)
                    deliveries[0]()
                    self.assertTrue(scene.lock_touch)
                    self.assertEqual(ui._lock['puzzleRoomGetClue'], 1)
                    deliveries[1]()
                    self.assertFalse(scene.lock_touch)
                    self.assertEqual(ui._lock['puzzleRoomGetClue'], 0)
                    self.assertEqual(self.owner.storyData.puzzle_room_clues, [])
                    # Replaying naked B after a new wait must not run its wake-up.
                    scene.lock_touch = True
                    ui.lock('puzzleRoomGetClue')
                    naked()
                    self.assertTrue(scene.lock_touch)
                    self.assertEqual(ui._lock['puzzleRoomGetClue'], 1)

    def test_naked_avatar_puzzle_request_has_no_authority_to_unlock_scene(self):
        scene, ui = self.install_original_puzzle_scene_flow()
        # A retained prior same-clue token is not authority for a naked call.
        scene.getClue({'clue_id': 901})
        self.pending.pop()()
        scene.lock_touch = True
        self.owner.puzzleRoomGetClue(901)
        self.pending.pop()()
        self.assertTrue(scene.lock_touch)
        self.assertEqual(ui._lock['puzzleRoomGetClue'], 0)

    def test_existing_plain_and_reliable_handler_takes_precedence(self):
        handled = []
        self.proxy.handle_intelligence = lambda *args: handled.append(args)
        with patch.object(self.gateway, 'prepare_rpc_rejection', side_effect=AssertionError('fallback preceded handler')):
            self.proxy.call_server_method('readTodayIntelligence', {'x': 1})
            self.pending.pop()()
            self.proxy.reliable_call({'w': {'m': 'readTodayIntelligence', 'p': {'x': 2}, 'r': 3}, '_cbid_': 'cb'})
        self.assertEqual(handled, [('readTodayIntelligence', {'x': 1}), ('readTodayIntelligence', {'x': 2}, 'cb')])

    def test_owned_hero_progress_failure_releases_only_original_lock_without_success_reply(self):
        request = original_definition(LUCKY, 'checkProgressHeroFile', self.namespace, decorated=False)
        self.owner.luckyDrawData.getProgressingHeroes = lambda: [24]
        self.owner.heroMgrData = SimpleNamespace(getHero=lambda hid: object())
        self.owner.luckyDrawData.hero_file_progress = {24: 1, 25: 2}
        self.locks.append('other-original-operation')
        self.owner.replyProgressHeroFile = lambda *args: self.fail('success-only progress reply invoked')
        self.assertTrue(request(self.owner))
        self.assertEqual(self.locks, ['other-original-operation', 'changeProgressingHero'])
        self.pending.pop()()
        self.assertEqual(self.locks, ['other-original-operation'])
        self.assertEqual(self.owner.luckyDrawData.hero_file_progress, {24: 1, 25: 2})
        self.assertEqual(self.wires, [])
        self.assertEqual(len(self.messages), 1)

    def test_late_progress_failure_does_not_unlock_new_avatar(self):
        self.locks.append('changeProgressingHero')
        self.proxy.call_server_method('changeProgressingHero', {})
        self.gg.avatar = SimpleNamespace()
        self.pending.pop()()
        self.assertEqual(self.locks, ['changeProgressingHero'])
        self.assertEqual(self.messages, [])

    def test_memory_archive_scores_failure_does_not_overwrite_original_scores(self):
        path = ROOT / 'reports/baiye-score-request-original.py'
        self.owner.oddsAndEndsData = SimpleNamespace(mainline_totalScores={1: 700})
        self.owner.replyMainlineTotalScores = lambda *args: self.fail('success-only score reply invoked')
        original_definition(path, 'requestMainlineTotalScores', self.namespace, decorated=False)(self.owner)
        self.assertEqual(self.locks, ['requestMainlineTotalScores'])
        self.pending.pop()()
        self.assertEqual(self.locks, [])
        self.assertEqual(self.owner.oddsAndEndsData.mainline_totalScores, {1: 700})
        self.assertEqual(self.wires, [])
        self.assertEqual(len(self.messages), 1)

    def test_axiliya_false_events_execute_original_consumers_without_success_effects(self):
        event_names = {'requestAddAxiliyaMood': 'reply_addAxiliyaMood',
                       'requestCaijianOp': 'reply_caijianOp',
                       'requestGetAxiliyaHero': 'reply_getAxiliyaHero'}
        path = ROOT / 'reports/baiye-memory-room-consumers-original.py'
        seen = []
        consumers = dict((name, original_definition(path, name, {}, decorated=False))
                         for name in event_names.values())
        def dispatch(name, *args, **kwargs):
            seen.append(name)
            consumers[name](SimpleNamespace(), *args)
        self.gg.ui._tree.proc_event = dispatch
        for request in event_names:
            self.install_reply(request, LUCKY)
            original_definition(LUCKY, request, self.namespace, decorated=False)(self.owner)
            self.pending.pop()()
        self.assertEqual(seen, list(event_names.values()))
        self.assertEqual(self.locks, [])
        self.assertEqual(self.gg.avatar_callback_map, {})

    def install_original_counted_ui_locks(self):
        ui = self.gg.ui
        ui._lock, ui.recon_lock = {}, 0
        ui.panels.wait = SimpleNamespace(notify_show=lambda *args: None,
            notify_hide=lambda: None, cancel_timer=lambda: None)
        for name in ('lock', 'unlock', 'reset_lock'):
            method = original_definition(ROOT / 'analysis/decompiled/ui_manager.py', name,
                {'gg': self.gg}, decorated=False)
            setattr(ui, name, lambda *args, _method=method, **kwargs: _method(ui, *args, **kwargs))
        return ui

    def test_original_counted_default_locks_finish_two_independent_failures(self):
        ui = self.install_original_counted_ui_locks()
        self.install_reply('upgradeTreasure', HERO)
        request = original_definition(HERO, 'upgradeTreasure', self.namespace, decorated=False)
        for unused in range(2):
            request(self.owner, 24, '0123456789abcdef01234567')
        self.assertEqual(ui._lock, {'default': 2})
        self.pending.pop(0)()
        self.assertEqual(ui._lock, {'default': 1})
        self.pending.pop(0)()
        self.assertEqual(ui._lock, {'default': 0})
        self.assertEqual(ui.recon_lock, 0)

    def test_reset_counted_ui_lock_cancels_old_failure_without_consuming_new_wait(self):
        ui = self.install_original_counted_ui_locks()
        self.install_reply('upgradeTreasure', HERO)
        request = original_definition(HERO, 'upgradeTreasure', self.namespace, decorated=False)
        request(self.owner, 24, '0123456789abcdef01234567')
        ui.reset_lock()
        request(self.owner, 24, '0123456789abcdef01234567')
        self.pending.pop(0)()
        self.assertEqual(ui._lock, {'default': 1})
        self.assertEqual(self.wires, [])
        self.pending.pop(0)()
        self.assertEqual(ui._lock, {'default': 0})
        self.assertEqual(len(self.wires), 1)

    def test_reset_with_reused_callback_id_preserves_new_original_callback(self):
        ui = self.install_original_counted_ui_locks()
        self.install_reply('giveCatFriendly', LUCKY)
        request = original_definition(LUCKY, 'giveCatFriendly', self.namespace, decorated=False)
        request(self.owner, 1, 0)
        ui.reset_lock()
        request(self.owner, 1, 0)
        new_callback = self.gg.avatar_callback_map['original-callback-17']
        self.pending.pop(0)()
        self.assertIs(self.gg.avatar_callback_map['original-callback-17'], new_callback)
        self.assertEqual(ui._lock, {'giveCatFriendly': 1})
        self.pending.pop(0)()
        self.assertEqual(ui._lock, {'giveCatFriendly': 0})
        self.assertEqual(self.gg.avatar_callback_map, {})

    def install_reply(self, request_name, path):
        reply, body, message = prepare_rpc_rejection(request_name, {}, 'fixture-callback')
        if reply == 'serverCallbackCarrier':
            path = ROOT / 'analysis/original-py-640/entity/avatar_members/ReliableRpcMember.py'
        consumer = original_definition(path, reply, self.namespace)
        def receive(payload):
            self.wires.append((reply, copy.deepcopy(payload)))
            return consumer(self.owner, payload)
        setattr(self.owner, reply, receive)

    def test_every_registered_negative_uses_original_request_decoder_and_consumer(self):
        self.assertEqual(set(case[0] for case in CASES) | {'zhaiRequest', 'requestRecoverJingshenli', 'puzzleRoomGetClue', 'requestChangeAVGLevel', 'requestTriggerEventByEnding', 'requestTriggerDaXuanWo', 'actionRewardRequest', 'requestMainlineCgRewards'}, set(RPC_REJECTION_OPERATIONS))
        for name, path, request, args, lock in CASES:
            with self.subTest(request=name):
                self.locks.clear(); self.wires.clear(); self.messages.clear()
                self.install_reply(name, path)
                call = original_definition(path, request, self.namespace, decorated=False)
                call(self.owner, *args)
                self.assertEqual(self.locks, [lock])
                self.assertEqual(len(self.pending), 1)
                self.pending.pop()()
                self.assertEqual(self.locks, [])
                self.assertEqual(len(self.wires), 1)
                self.assertEqual(self.gg.avatar_callback_map, {})
                self.assertTrue(self.messages)
                self.assertEqual(self.wires[-1][0], prepare_rpc_rejection(name, {}, 'fixture-callback')[0])
                if name in ('giveCatFriendly', 'requestExchangeActivityHeroProg', 'requestExchangeSuipianWithItem'):
                    self.assertEqual(self.wires[-1][1]['_cbid_'], 'original-callback-17')
                self.assertFalse(self.pending)

    def test_callback_only_cases_use_exact_original_unlock_callbacks_on_reliable_transport(self):
        for name, path, request, args, lock in CASES:
            if name not in RPC_CALLBACK_REJECTION_OPERATIONS:
                continue
            with self.subTest(request=name):
                self.wires.clear(); self.messages.clear()
                self.install_reply(name, path)
                def send(method, parameters, callback):
                    self.gg.avatar_callback_map['outer-cbid-73'] = callback
                    self.proxy.reliable_call({'w': {'m': method, 'p': parameters, 'r': 73}, '_cbid_': 'outer-cbid-73'})
                self.owner.callServerMethod = send
                original_definition(path, request, self.namespace, decorated=False)(self.owner, *args)
                self.assertEqual(self.locks, [])
                self.assertEqual(self.gg.avatar_callback_map, {})
                self.assertEqual(self.wires, [('reliableRpcAck', {'s': 73}),
                    ('serverCallbackCarrier', {'_r_': {}, '_cbid_': 'outer-cbid-73'})])
                self.assertTrue(self.messages)

    def test_callback_only_registry_requires_callback_and_never_guesses_unknown_operations(self):
        for name in RPC_CALLBACK_REJECTION_OPERATIONS:
            for cbid in (None, 0, ''):
                self.assertIsNone(prepare_rpc_rejection(name, {}, cbid))
            self.assertEqual(prepare_rpc_rejection(name, {}, 'real-callback')[0], 'serverCallbackCarrier')
        self.assertIsNone(prepare_rpc_rejection('unknown', {}, 'real-callback'))

    def test_reliable_ack_is_separate_and_callback_id_is_exact(self):
        self.install_reply('giveCatFriendly', LUCKY)
        self.locks.append('giveCatFriendly')
        cbid = 'cb-\u767d\u591c-0017'
        self.gg.avatar_callback_map[cbid] = lambda *args: self.gg.ui.unlock('giveCatFriendly')
        self.proxy.reliable_call({'w': {'m': 'giveCatFriendly', 'p': {'id': 1, 'ty': 0}, 'r': 719}, '_cbid_': cbid})
        self.assertEqual(self.wires[0], ('reliableRpcAck', {'s': 719}))
        self.assertEqual(self.wires[1][1]['_cbid_'], cbid)
        self.assertEqual(self.locks, [])

    def test_late_plain_reply_never_unlocks_or_notifies_another_avatar(self):
        for replace_proxy_owner in (True, False):
            with self.subTest(replace_proxy_owner=replace_proxy_owner):
                self.gg.avatar = self.owner; self.proxy.owner = self.owner
                self.install_reply('requestTryPlayBattle', PREVIEW)
                self.proxy.call_server_method('requestTryPlayBattle', {'h': 24, 'd': 265})
                if replace_proxy_owner:
                    self.proxy.owner = SimpleNamespace()
                else:
                    self.gg.avatar = SimpleNamespace()
                self.pending.pop()()
                self.assertEqual(self.wires, [])
                self.assertEqual(self.messages, [])

    def test_unknown_and_success_only_consumers_are_not_registered(self):
        for name in ('notKnown', 'summoncoinExchange', 'memoryCrystalExchangeSuipian',
                     'yuanbaoExchangeCrystal', 'getCatHero',
                     'changeTreasureForbid', 'decomposeTreasure', 'composeTreasureBatch'):
            self.assertIsNone(prepare_rpc_rejection(name, {}))
            self.assertFalse(self.proxy.reject_unimplemented_rpc(name, {}))
        self.assertEqual(self.messages, [])

    def test_malformed_echo_fields_still_decode_into_original_negative_branch(self):
        for name, path, args, lock in (
            ('upgradeTreasureTargetLv', HERO, {'s': object(), 'l': []}, None),
            ('requestTryPlayBattle', PREVIEW, {'h': []}, 'requestTryPlayBattle'),
            ('buyRealtimeGiftBag', REWARD, {'i': {}}, 'buyRealtimeGiftBag')):
            self.install_reply(name, path)
            self.locks.append(lock)
            self.proxy.reject_unimplemented_rpc(name, args)
            self.assertEqual(self.locks, [])

    def test_falsy_callback_field_preserved_without_inventing_callback(self):
        self.install_reply('giveCatFriendly', LUCKY)
        self.proxy.reject_unimplemented_rpc('giveCatFriendly', {}, 0)
        self.assertIn('_cbid_', self.wires[-1][1])
        self.assertEqual(self.wires[-1][1]['_cbid_'], 0)

    def test_echo_ids_and_native_uuid_preserved_and_canonical_unchanged(self):
        uid = NativeId('0123456789abcdef01234567')
        profile = {'money': 123, 'heroes': {'24': {'star': 2}}}
        story = {'week': 1, 'receipts': []}
        self.proxy.profile, self.proxy.story = profile, story
        before = copy.deepcopy((profile, story))
        self.install_reply('upgradeTreasureTargetLv', HERO)
        self.locks.append(None)
        self.proxy.reject_unimplemented_rpc('upgradeTreasureTargetLv', {'h': 24, 's': uid, 'l': 8})
        payload = self.wires[-1][1]
        self.assertEqual(payload['s'].value, uid.value)
        self.assertEqual(payload['l'], 8)
        self.assertEqual((self.proxy.profile, self.proxy.story), before)
        self.assertIs(self.proxy.profile, profile)
        self.assertIs(self.proxy.story, story)

    def test_callback_session_change_suppresses_late_notice(self):
        self.install_reply('giveCatFriendly', LUCKY)
        self.gg.avatar_callback_map['cb'] = lambda *args: setattr(self.gg, 'avatar', SimpleNamespace())
        self.proxy.reject_unimplemented_rpc('giveCatFriendly', {}, 'cb')
        self.assertEqual(self.messages, [])

    def test_reliable_ack_session_change_cannot_redirect_rejection(self):
        self.install_reply('giveCatFriendly', LUCKY)
        self.owner.reliableRpcAck = lambda body: setattr(self.proxy, 'owner', SimpleNamespace())
        self.proxy.reliable_call({'w': {'m': 'giveCatFriendly', 'p': {}, 'r': 73}, '_cbid_': 'cb'})
        self.assertEqual(self.wires, [])
        self.assertEqual(self.messages, [])

    def test_module_is_ascii_python27_and_wired_in_both_loaders_and_allowlist(self):
        import json
        path = ROOT / 'runtime/offline_rpc_rejections.py'
        source = path.read_text(encoding='ascii')
        RefactoringTool([]).refactor_string(source, str(path))
        self.assertIn('runtime/offline_rpc_rejections.py', json.loads((ROOT / 'offline-project-allowlist.json').read_text())['files'])
        loader = (ROOT / 'runtime/offline_bootstrap.py').read_text(encoding='ascii')
        self.assertIn("'offline_rpc_rejections.py'", loader)
        self.assertLess(loader.index("+ _f7_rpc_rejections_source"), loader.index("+ open(_f7_gateway_path"))
        sys.path.insert(0, str(ROOT / 'tools'))
        import patch_bootstrap
        embedded = patch_bootstrap.embedded_loader(ROOT / 'runtime')
        module = ast.parse(embedded.splitlines()[0])
        payload = ast.literal_eval(module.body[0].value)
        self.assertIn(source, payload)
        self.assertLess(payload.index('def prepare_rpc_rejection('), payload.index('class LocalProxy('))
        exchange = (ROOT / 'runtime/offline_item_exchange.py').read_text(encoding='ascii')
        self.assertIn(exchange, payload)
        self.assertLess(payload.index('def prepare_item_exchange('), payload.index('class LocalProxy('))
        self.assertIn('runtime/offline_item_exchange.py', json.loads((ROOT / 'offline-project-allowlist.json').read_text())['files'])
        self.assertIn("+ _f7_item_exchange_source +", loader)


if __name__ == '__main__':
    unittest.main()
