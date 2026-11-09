"""Host replay of extracted original Python bodies, NOT native acceptance.

Native nodes/engine operations below are explicit finite stand-ins. Unmodeled
operations raise AttributeError. No APK, game VM, device or native API is run.
"""
import ast
import builtins
import copy
import hashlib
from pathlib import Path
import re
import sys
import textwrap
from types import MethodType, ModuleType, SimpleNamespace as NS
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'runtime'))
FIXTURE = ROOT / 'tests/fixtures/project7_area_settlement_original.py.txt'


def original_method(source, name, namespace):
    start = source.index('    def ' + name + '(')
    following = re.search(r'\n    (?:def |@)', source[start + 1:])
    body = source[start:start + 1 + following.start()] if following else source[start:source.rindex('\n\nreturn')] if '\n\nreturn' in source[start:] else source[start:]
    # Normalize print syntax only; keep the original control flow/bodies.
    body = body.replace("print 'settlement_ended ======================================'", "print('settlement_ended ======================================')")
    body = body.replace("print 'isLeaveEmergencyEvent', event", "print('isLeaveEmergencyEvent', event)")
    body = body.replace('print e\n', 'print(e)\n')
    exec(compile(textwrap.dedent(body), '<original-panel:' + name + '>', 'exec'), namespace)
    return namespace[name]


class OriginalAreaCallbackTests(unittest.TestCase):
    def setUp(self):
        self.delays = []
        self.calls = []
        self.const = NS(DEBUG_OFFLINE=False, CityStatus=NS(FREE=0, FIGHT=1),
            StoryRouteConst=NS(ZHOUNIAN2_WEEK_REFRESH_EVENTID=999),
            GameEvent=NS(ONE_SETTLEMENT_END=1, SETTLEMTN_START=2, SETTLEMENT_END=3), SCENE_NEW_DANCHI_ROOM=123,
            CityTheme=NS(REMINISCENCE=9), XUANWO_AREA_ID=99)
        self.gg = ModuleType('gg')
        proxy = NS(story={'week': 1, 'event_occurrences': {'101': 1, '102': 1}}, processing_events=[101, 102])
        self.avatar = NS(server=proxy, cityData=NS(get_area_info=lambda aid: {'st': [0 if aid == 1 else 1]},
            update_city_sfx_visible=lambda aid: self.calls.append(('sfx', aid))),
            eventTriggerData=NS(completedEvents=[]), storyData=NS(change_week=False, route='1', cityTheme=0),
            newbeeData=NS(checkAllNewbee=lambda: self.calls.append('newbee')))
        proxy.owner = self.avatar
        self.gg.avatar = self.avatar
        self.gg.exec_delay = lambda delay, cb: self.delays.append((delay, cb))
        self.gg.logic = NS(disable_event=lambda key: None, enable_event=lambda key: self.calls.append('enable'))
        self.gg.city_container = NS(get_scene_by_key=lambda key: None)
        self.gg.audio_mgr = NS(ui_sound=lambda key: None)
        self.gg.city = NS(city_focus=lambda aid, cb: self.delays.append(('focus', cb)),
                          area_models={2: NS(), 3: NS()})
        self.gg.sfx_mgr = NS(play_sfx_at_model_socket=lambda *a, **kw: self.delays.append(('sfx', lambda: kw['cb'](NS(life_span=1), None, None))))
        namespace = dict(gg=self.gg, const=self.const,
            SFX_FILE={'area_fight': {'-1': ('sfx', 'head', (False, 1))}}, SFX_FILE_REMINISCENCE={},
            cc=NS(cc=NS(FadeOut=NS(create=lambda value: value)), ccui=NS(TOUCH_EVENT_ENDED=2)))
        self.Panel = type('Panel', (), {'UI_SOUND': {}, 'CITY_CR_SCALE': {}})
        namespace['Panel'] = self.Panel
        source = FIXTURE.read_text()
        for name in ('on_init', 'notify_reward', 'notify_area_event', 'notify_area_open', 'notify_area_fight',
                     'notify_settlement_area_open', 'notify_settlement_area_fight',
                     'settlement_ended', '_close_panel', 'process_area_op_end', 'city_attention'):
            setattr(self.Panel, name, original_method(source, name, namespace))
        self.Panel.on_cg_share_close = lambda panel: None
        self.Panel.build_highest = lambda panel: self.build(panel)
        self.Panel.destroy_self_layer = lambda panel: self.destroy(panel)
        self.Panel.proc_event_handler = lambda panel, *args: self.calls.append('one-end')
        self.Panel.add_highest = lambda panel, *args: None
        self.Panel.process_area_op_begin = lambda panel: setattr(panel, 'area_op_queue_idx', panel.area_op_queue_idx + 1)
        self.Panel.anim_out = lambda panel, cb: self.anim_out(panel, cb)
        self.Panel.notify_reward_test = lambda panel, cb: self.reward(panel, cb)
        self._panel = None
        self.queue = []
        city = NS(visible_functional=lambda value: None)
        hidden = NS(valid=False, visible=False)
        test = self
        class Panels(NS):
            @property
            def settlement_fullscreen(self): return test.panel
        panels = Panels(city=city,
            battle_stage=NS(valid=False), settlement_info=NS(notify_hide=lambda: None),
            settlement_fullscreen_fashion=NS(is_playing=lambda: False),
            dialogue=NS(can_proc_settlement=lambda: True))
        for name in ('settlement_window', 'settlement_success_failure', 'settlement_break',
                     'settlement_clear', 'settlement_emoji_accomplish', 'settlement_player_upgrade'):
            setattr(panels, name, hidden)
        self.gg.ui = NS(panels=panels, _settlement_list=self.queue, _settlement_enable=0,
            _procing_settlement=False, need_release_ui_memory=lambda: False,
            proc_event_handler=lambda *a: None, purge_unuse=lambda: None)
        queue_source = (ROOT / 'tests/fixtures/project7_area_queue_original.py.txt').read_text()
        for name in ('add_settlement', 'has_settlement', 'proc_settlement'):
            setattr(self.gg.ui, name, MethodType(original_method(queue_source, name, namespace), self.gg.ui))
        self.content = NS(data={101: {'ui': ('settlement_fullscreen', 'notify_area_event', '1', '2')},
                                    102: {'ui': ('settlement_fullscreen', 'notify_area_event', '2')}})

    @property
    def panel(self):
        if self._panel is None:
            self._panel = self.make_panel()
        return self._panel

    def make_panel(self):
        panel = self.Panel()
        panel.on_init()
        panel.valid = panel.visible = False
        node = NS(setCascadeOpacityEnabled=lambda value: None, setOpacity=lambda value: None,
                  runAction=lambda value: None)
        panel._node = panel.img = node
        panel.anims = {}; panel.panels = {}; panel.close_anim = None
        panel.fight_cover = False
        panel.city_intro = NS(disappear=lambda: None)
        panel.hero_img = panel.hero_shadow = NS(setVisible=lambda value: None)
        return panel

    def anim_out(self, panel, cb):
        self.assertIs(panel, self.panel)
        self.delays.append(('anim_out', cb))

    def build(self, panel):
        self.assertIs(panel, self.panel)
        panel.valid = panel.visible = True

    def destroy(self, panel):
        self.assertIs(panel, self.panel)
        panel.valid = panel.visible = False
        self._panel = None

    def reward(self, panel, cb):
        self.build(panel); panel.stype = 'reward'; panel.cb = cb

    def proc(self):
        return self.gg.ui.proc_settlement()

    def install(self, installer=None):
        if installer is None:
            from offline_native_story_callbacks import install_native_story_callbacks
            installer = install_native_story_callbacks
        modules = {'gg': self.gg}
        for name in ('com', 'com.const', 'com.data', 'com.data.cdata', 'com.data.cdata.event_content',
                     'cocos', 'cocos.panels', 'cocos.panels.settlement_fullscreen',
                     'com.data.cdata.event_condition', 'com.data.cdata.reward_common'):
            modules[name] = ModuleType(name)
        modules['com.const'].__dict__.update(vars(self.const))
        modules['com.data.cdata.event_content'].data = self.content.data
        modules['com.data.cdata.event_condition'].data = {}
        modules['com.data.cdata.reward_common'].data = {}
        modules['cocos.panels.settlement_fullscreen'].Panel = self.Panel
        for name, module in list(modules.items()):
            if '.' in name:
                parent, child = name.rsplit('.', 1)
                setattr(modules[parent], child, module)
        scheduler = self.gg.exec_delay
        with patch.dict(sys.modules, modules):
            installer()
            installer()
        self.assertIs(self.gg.exec_delay, scheduler)
        # Runtime closures import gg when executing.
        self.module_patch = patch.dict(sys.modules, modules)
        self.module_patch.start(); self.addCleanup(self.module_patch.stop)

    def python2_class_methods(self):
        """Model Python 2 class lookup without changing the extracted bodies."""
        panel_class = self.Panel
        class StrictUnboundMethod:
            def __init__(self, function):
                self.im_func = function
            def __call__(self, receiver, *args, **kwargs):
                if not isinstance(receiver, panel_class):
                    raise TypeError('unbound method requires Panel instance')
                return self.im_func(receiver, *args, **kwargs)
        class Python2Method:
            def __init__(self, function):
                self.function = function
            def __get__(self, instance, owner):
                if instance is None:
                    return StrictUnboundMethod(self.function)
                return MethodType(self.function, instance)
        for name in ('notify_area_event', 'notify_settlement_area_open',
                     'notify_settlement_area_fight', 'settlement_ended',
                     '_close_panel', 'process_area_op_end', 'city_attention'):
            setattr(panel_class, name, Python2Method(getattr(panel_class, name)))

    def test_python2_unbound_method_rejects_continuation_negative_control(self):
        from offline_native_story_callbacks import _F7StoryPanelContinuation
        self.python2_class_methods()
        continuation = _F7StoryPanelContinuation(self.panel)
        for name in ('settlement_ended', '_close_panel',
                     'process_area_op_end', 'city_attention'):
            with self.subTest(method=name):
                with self.assertRaisesRegex(TypeError, 'requires Panel instance'):
                    getattr(self.Panel, name)(continuation)

    def test_python2_methods_managed_open_fight_and_unmanaged_reward(self):
        self.check_python2_methods_managed_open_fight_and_reward()

    def test_python2_methods_actual_flat_managed_open_fight_and_reward(self):
        self.check_python2_methods_managed_open_fight_and_reward(
            self.flat_namespace()['install_native_story_callbacks'])

    def check_python2_methods_managed_open_fight_and_reward(self, installer=None):
        self.python2_class_methods()
        self.install(installer)
        self.panel.notify_area_event(101, 1, 2, cb=lambda: self.calls.append('area'))
        self.finish_open()
        self.assertNotIn('area', self.calls)
        self.finish_fight()
        self.assertEqual(self.calls.count('area'), 1)
        self.panel.notify_reward_test(lambda: self.calls.append('reward'))
        self.panel.settlement_ended()
        self.assertEqual(self.calls.count('reward'), 1)
        self.assertEqual(self.calls.count('one-end'), 3)

    def test_python2_methods_unmanaged_reward_ended(self):
        self.python2_class_methods()
        self.install()
        self.panel.notify_reward_test(lambda: self.calls.append('reward'))
        panel = self.panel
        panel.settlement_ended()
        self.assertFalse(panel.valid)
        self.assertEqual(self.calls.count('reward'), 1)
        self.assertEqual(self.calls.count('one-end'), 1)

    def test_python2_methods_managed_close_panel(self):
        self.python2_class_methods()
        self.install()
        self.panel.notify_area_event(101, 1, cb=lambda: self.calls.append('area'))
        self.panel.cover = False; self.panel.focus_area_id = 0
        self.panel.panels = {'area_open': 'city'}
        self.gg.ui.actions = NS(settlement_fullscreen=NS(loop=NS(stop=lambda: None), bg_close=NS(start=lambda: None)))
        self.panel._close_panel()
        self.take(500)()
        self.assertEqual(self.calls.count('area'), 1)
        self.assertEqual(self.calls.count('one-end'), 1)

    def test_original_body_negative_control_open_plus_fight_continues_early(self):
        self.panel.notify_area_event(101, 1, 2, cb=lambda: self.calls.append('area'))
        first = self.panel
        self.finish_open()
        self.assertIsNot(first, self.panel)
        self.assertEqual(self.panel.stype, 'area_fight')
        self.assertIn('area', self.calls)  # Fight terminal has not run.
        self.assertTrue(self.panel.valid)

    def test_original_body_negative_control_second_dispatch_overwrites_active_cb(self):
        self.panel.notify_area_event(101, 1, cb=lambda: self.calls.append('area'))
        first = self.panel
        self.panel.notify_area_event(102, 2, cb=lambda: self.calls.append('next'))
        self.finish_open()
        self.assertIsNot(first, self.panel)
        self.assertNotIn('area', self.calls)
        self.assertIn('next', self.calls)  # Next fight has only just started.

    def take(self, key):
        index = next(i for i, (kind, cb) in enumerate(self.delays) if kind == key)
        return self.delays.pop(index)[1]

    def finish_open(self):
        self.panel.process_area_op_end()
        self.take('anim_out')()
        ending = self.take(250)
        ending()
        return ending

    def finish_fight(self):
        self.take('focus')()
        self.take('sfx')()
        ending = self.take(850)
        ending()
        return ending

    def flat_namespace(self):
        sys.path.insert(0, str(ROOT / 'tools'))
        from patch_bootstrap import embedded_loader
        source = ast.literal_eval(ast.parse(embedded_loader(ROOT / 'runtime').splitlines()[0]).body[0].value)
        real_import = builtins.__import__
        blocked = []
        def guarded_import(name, *args, **kwargs):
            if name.startswith('offline_'):
                blocked.append(name)
                raise ImportError('standalone offline modules are absent')
            return real_import(name, *args, **kwargs)
        namespace = {'__name__': 'actual_flat_area_runtime',
                     '__builtins__': dict(vars(builtins), __import__=guarded_import)}
        exec(compile(source, '<actual-flat-area-runtime>', 'exec'), namespace)
        self.assertTrue(blocked)
        return namespace

    def test_actual_embedded_flat_installer_works_with_offline_imports_blocked(self):
        namespace = self.flat_namespace()
        installer = namespace['install_native_story_callbacks']
        self.assertIs(installer.__globals__, namespace)
        self.install(installer)
        self.panel.notify_area_event(101, 1, 2, cb=lambda: self.calls.append('area'))
        self.finish_open(); self.finish_fight()
        self.assertEqual(self.calls.count('area'), 1)
        self.assertIs(self.Panel.notify_area_event.__globals__, namespace)

    def test_original_ui_movie_observer_and_flat_gateway_storage_rollback(self):
        n = self.flat_namespace()
        n['_f7_log'] = lambda message: None
        source = (ROOT / 'analysis/decompiled/EventTriggerMember.py').read_text()
        avatar_type = type('ClientAvatar', (), {})
        avatar = avatar_type(); avatar.__dict__.update(vars(self.avatar))
        self.avatar = self.gg.avatar = avatar
        self.content.data[101].update(release=True, completeConds={})
        namespace = {'gg': self.gg, 'EventContentDataMod': self.content}
        for name in ('startEventUI', 'startMovie'):
            setattr(avatar_type, name, original_method(source, name, namespace))
        avatar_type.startEventBattle = lambda a, event: self.calls.append(('battle', event))
        avatar_type.startPuzzleRoom = lambda a, event: None
        proxy = n['LocalProxy'](None, avatar)
        avatar.server = proxy
        proxy.processing_events = {101}
        state = proxy.progress_snapshot(); n['begin_story_occurrence'](state, 101)
        proxy.restore_progress(state)
        proxy.defer = lambda delay, cb: self.delays.append(('observer', cb))
        proxy.story_effect_tables = lambda: {}
        proxy.enrich_city_plan = lambda state, notices: (state, notices)
        proxy.sync_daerweila_projection = lambda: None
        proxy.process_week_handoffs = lambda: None
        proxy.reply = lambda name, payload: self.calls.append(('reply', name))
        self.install(n['install_native_story_callbacks'])
        entity = ModuleType('entity'); client = ModuleType('entity.ClientAvatar')
        client.ClientAvatar = avatar_type; entity.ClientAvatar = client
        with patch.dict(sys.modules, {'entity': entity, 'entity.ClientAvatar': client}):
            n['install_story_completion_observers']()
        before = proxy.progress_snapshot()
        avatar.startEventUI(101)
        self.assertEqual(proxy.progress_snapshot(), before)
        self.finish_open()
        self.assertFalse(any(kind == 'observer' for kind, cb in self.delays))
        self.finish_fight()
        self.assertEqual(proxy.processing_events, {101})
        observed = self.take('observer')
        # Existing LocalProxy storage transaction must roll back its own proof.
        proxy._saved_progress = copy.deepcopy(before)
        def write_failure(state): raise OSError('disk full')
        proxy._store = NS(write=write_failure)
        with self.assertRaisesRegex(OSError, 'disk full'): observed()
        self.assertEqual(proxy.progress_snapshot(), before)
        self.assertFalse(any(call == ('reply', 'completeEventReplyEnd') for call in self.calls))
        proxy._store = None
        observed()  # Same existing callback can retry after storage recovers.
        self.assertIn(101, proxy.completed_events)
        committed = proxy.progress_snapshot()
        observed()
        self.assertEqual(proxy.progress_snapshot(), committed)
        self.assertEqual(self.calls.count(('reply', 'completeEventReplyEnd')), 1)

    def test_open_plus_sorted_fight_only_last_actual_terminal_resumes(self):
        self.install()
        self.panel.notify_area_event(101, 3, 1, 2, cb=lambda: self.calls.append('area'))
        self.assertEqual(self.panel.stype, 'area_open')
        self.assertEqual(self.queue[0][2][1], [2, 3])
        self.finish_open()
        self.assertNotIn('area', self.calls)
        # Both actual city-focus/SFX chains must end before the last callback.
        self.take('focus')(); self.take('sfx')(); self.take(850)()
        self.assertNotIn('area', self.calls)
        self.take(150)(); self.take('focus')(); self.take('sfx')(); self.take(850)()
        self.assertEqual(self.calls.count('area'), 1)
        self.assertEqual(self.calls.count('one-end'), 2)

    def test_late_open_producer_cannot_finish_next_fight_or_reward(self):
        self.install()
        self.panel.notify_area_event(101, 1, 2, cb=lambda: self.calls.append('area'))
        self.panel.process_area_op_end()
        old_animation = self.take('anim_out')
        old_animation(); old_ended = self.take(250); old_ended()
        self.assertEqual(self.panel.stype, 'area_fight')
        old_animation(); self.take(250)(); old_ended()
        self.panel.settlement_ended()  # A bare stale signal has no identity.
        self.assertEqual(self.calls.count('one-end'), 1)
        self.assertNotIn('area', self.calls)
        self.finish_fight()
        self.assertEqual(self.calls.count('area'), 1)
        self.gg.ui.add_settlement('settlement_fullscreen', 'notify_reward_test', lambda: self.calls.append('reward'))
        self.proc(); old_ended()
        self.assertNotIn('reward', self.calls)
        self.panel.settlement_ended()
        self.assertEqual(self.calls.count('reward'), 1)

    def test_late_fight_sfx_chain_cannot_resume_new_event(self):
        self.install()
        self.panel.notify_area_event(101, 2, cb=lambda: self.calls.append('area'))
        self.take('focus')(); self.take('sfx')(); old_sfx_end = self.take(850)
        self.panel.notify_area_event(102, 1, cb=lambda: self.calls.append('next'))
        old_sfx_end()
        self.assertEqual(self.calls.count('area'), 1)
        self.assertEqual(self.panel.stype, 'area_open')
        old_sfx_end()
        self.assertEqual(self.calls.count('one-end'), 1)
        self.assertNotIn('next', self.calls)
        self.finish_open()
        self.assertEqual(self.calls.count('next'), 1)

    def test_area_to_reward_and_reward_to_area_keep_own_callbacks(self):
        self.install()
        self.panel.notify_area_event(101, 1, cb=lambda: self.calls.append('area'))
        self.gg.ui.add_settlement('settlement_fullscreen', 'notify_reward_test', lambda: self.calls.append('reward'))
        self.finish_open()
        self.assertEqual(self.calls.count('area'), 1)
        self.assertNotIn('reward', self.calls)
        self.assertIsNotNone(self.panel.cb)
        self.panel.notify_area_event(102, 1, cb=lambda: self.calls.append('next'))
        self.assertIsNotNone(self.panel.cb)  # Enqueue must not erase active reward.
        self.panel.settlement_ended()
        self.assertEqual(self.calls.count('reward'), 1)
        self.assertNotIn('next', self.calls)
        self.finish_open()
        self.assertEqual(self.calls.count('next'), 1)

    def test_area_ended_does_not_erase_reward_cb_installed_during_area(self):
        self.install()
        self.panel.notify_area_event(101, 1, cb=lambda: self.calls.append('area'))
        reward_callback = lambda: self.calls.append('reward')
        self.panel.cb = reward_callback
        old_panel = self.panel
        self.finish_open()
        self.assertIs(old_panel.cb, reward_callback)
        self.assertEqual(self.calls.count('area'), 1)
        self.assertNotIn('reward', self.calls)

    def test_original_notify_reward_cb_is_preserved_but_not_stolen_by_area(self):
        self.install()
        self.panel.notify_area_event(101, 1, cb=lambda: self.calls.append('area'))
        old_panel = self.panel
        legacy = lambda: self.calls.append('legacy')
        # Actual original notify_reward body writes cb on the existing Panel.
        # Transporting that unrelated legacy reward cb is explicitly out of
        # scope: preserve its field, never mislabel it as an area continuation.
        old_panel.notify_reward('reward', {}, cb=legacy)
        self.finish_open()
        self.assertIs(old_panel.cb, legacy)
        self.assertEqual(self.calls.count('area'), 1)
        self.assertNotIn('legacy', self.calls)

    def test_original_notify_reward_active_before_area_keeps_callback_order(self):
        self.install()
        self.panel.notify_reward_test(None)  # Explicit renderer leaf.
        self.panel.notify_reward('reward', {}, cb=lambda: self.calls.append('legacy'))
        self.panel.notify_area_event(101, 1, cb=lambda: self.calls.append('area'))
        self.panel.settlement_ended()
        self.assertEqual(self.calls.count('legacy'), 1)
        self.assertNotIn('area', self.calls)
        self.finish_open()
        self.assertEqual(self.calls.count('area'), 1)

    def test_owner_proxy_week_occurrence_and_processing_guards(self):
        for mutate in ('avatar', 'owner', 'proxy', 'week', 'occurrence', 'processing'):
            with self.subTest(mutate=mutate):
                self.setUp(); self.install()
                self.panel.notify_area_event(101, 1, cb=lambda: self.calls.append('area'))
                self.panel.process_area_op_end(); self.take('anim_out')(); ending = self.take(250)
                if mutate == 'avatar': self.gg.avatar = NS(newbeeData=self.avatar.newbeeData)
                elif mutate == 'owner': self.avatar.server.owner = NS()
                elif mutate == 'proxy': self.avatar.server = NS()
                elif mutate == 'week': self.avatar.server.story['week'] += 1
                elif mutate == 'occurrence': self.avatar.server.story['event_occurrences']['101'] += 1
                else: self.avatar.server.processing_events.remove(101)
                ending()
                self.assertNotIn('area', self.calls)
                self.assertEqual(self.calls.count('one-end'), 1)
                self.assertFalse(self.panel.valid)

    def test_source_rechecked_after_original_proc_starts_next_batch(self):
        self.install()
        self.panel.notify_area_event(101, 1, cb=lambda: self.calls.append('area'))
        original_proc = self.gg.ui.proc_settlement
        def change_week():
            self.avatar.server.story['week'] += 1
            original_proc()
        self.gg.ui.proc_settlement = change_week
        self.finish_open()
        self.assertNotIn('area', self.calls)

    def test_same_event_restart_rejects_exact_old_generated_terminal(self):
        self.install()
        self.panel.notify_area_event(101, 1, cb=lambda: self.calls.append('old'))
        self.panel.process_area_op_end(); self.take('anim_out')(); old = self.take(250)
        self.avatar.server.story['event_occurrences']['101'] += 1
        self.panel.destroy_self_layer()  # Native world rebuild is an explicit leaf.
        self.panel.notify_area_event(101, 1, cb=lambda: self.calls.append('new'))
        old()
        self.assertTrue(self.panel.valid)
        self.assertNotIn('old', self.calls)
        self.assertNotIn('one-end', self.calls)
        self.finish_open()
        self.assertEqual(self.calls.count('new'), 1)

    def test_stale_queued_batch_never_runs_original_area_start(self):
        self.install()
        self.panel.notify_reward_test(lambda: self.calls.append('reward'))
        self.panel.notify_area_event(101, 1, cb=lambda: self.calls.append('area'))
        self.avatar.server.story['week'] += 1
        self.panel.settlement_ended()
        self.assertEqual(self.queue, [])
        self.assertFalse(self.panel.valid)
        self.assertEqual(self.calls.count('reward'), 1)
        self.assertNotIn('area', self.calls)

    def test_missing_area_info_and_debug_offline_do_not_create_terminal(self):
        self.install()
        self.avatar.cityData.get_area_info = lambda aid: None
        self.panel.notify_area_event(101, 1, cb=lambda: self.calls.append('area'))
        self.assertEqual(self.queue, [])
        self.avatar.cityData.get_area_info = lambda aid: {'st': [0]}
        sys.modules['com.const'].DEBUG_OFFLINE = True
        self.panel.notify_area_event(101, 1, cb=lambda: self.calls.append('area'))
        self.assertEqual(self.queue, [])
        self.assertNotIn('area', self.calls)
        self.assertEqual(self.avatar.server.processing_events, [101, 102])

    def test_empty_areas_remain_pending_but_explicit_native_suppression_resumes(self):
        self.install()
        self.panel.notify_area_event(101, cb=lambda: self.calls.append('empty'))
        self.assertEqual(self.panel._f7_story_area_diagnostic, 'no-native-area-batch')
        self.assertNotIn('empty', self.calls)
        for mode in ('change_week', 'anniversary'):
            if mode == 'change_week': self.avatar.storyData.change_week = True
            else:
                self.avatar.storyData.change_week = False
                self.avatar.eventTriggerData.completedEvents = [999]
            self.panel.notify_area_event(101, 2, cb=lambda: self.calls.append(mode))
            self.assertEqual(self.panel._f7_story_area_diagnostic, 'native-area-fights-suppressed')
            self.assertEqual(self.calls.count(mode), 1)
        self.assertEqual(self.queue, [])
        self.assertNotIn('one-end', self.calls)
        self.assertEqual(self.avatar.server.processing_events, [101, 102])

    def test_mixed_missing_area_info_does_not_start_partial_batch(self):
        self.install()
        self.avatar.cityData.get_area_info = lambda aid: {'st': [0]} if aid == 1 else None
        self.panel.notify_area_event(101, 1, 2, cb=lambda: self.calls.append('area'))
        self.assertEqual(self.queue, [])
        self.assertFalse(self.panel.valid)
        self.assertNotIn('area', self.calls)
        self.assertEqual(self.panel._f7_story_area_diagnostic, 'unavailable-native-area-info')

    def test_expired_current_panel_can_close_and_release_valid_next_queue(self):
        self.install()
        self.panel.notify_area_event(101, 1, cb=lambda: self.calls.append('old'))
        old_panel = self.panel
        self.avatar.server.story['week'] += 1
        self.panel.notify_area_event(102, 1, cb=lambda: self.calls.append('new'))
        self.finish_open()
        self.assertFalse(old_panel.valid)
        self.assertIsNot(old_panel, self.panel)
        self.assertTrue(self.panel.valid)
        self.assertNotIn('old', self.calls)
        self.assertEqual(self.calls.count('one-end'), 1)
        old_panel.settlement_ended()  # Captured unscoped old bound method.
        self.assertTrue(self.panel.valid)
        self.assertEqual(self.calls.count('one-end'), 1)
        self.finish_open()
        self.assertEqual(self.calls.count('new'), 1)

    def test_exact_close_panel_delay_captures_expected_batch(self):
        self.install()
        self.panel.notify_area_event(101, 1, cb=lambda: self.calls.append('area'))
        self.panel.cover = False; self.panel.focus_area_id = 0
        self.panel.panels = {'area_open': 'city'}
        self.gg.ui.actions = NS(settlement_fullscreen=NS(loop=NS(stop=lambda: None), bg_close=NS(start=lambda: None)))
        self.panel._close_panel()
        ending = self.take(500)
        ending(); ending()
        self.assertEqual(self.calls.count('area'), 1)
        self.assertEqual(self.calls.count('one-end'), 1)

    def test_reentrant_and_raising_callbacks_are_consumed_before_call(self):
        self.install()
        holder = []
        def callback():
            self.calls.append('area')
            holder[0]()
            raise ValueError('original callback failure')
        self.panel.notify_area_event(101, 1, cb=callback)
        self.panel.process_area_op_end(); self.take('anim_out')(); holder.append(self.take(250))
        with self.assertRaisesRegex(ValueError, 'original callback failure'): holder[0]()
        holder[0]()
        self.assertEqual(self.calls.count('area'), 1)

    def test_original_base_lifecycle_constructs_once_and_evicts_destroyed_panel(self):
        source = (ROOT / 'analysis/decompiled/ui_panel.py').read_text()
        namespace = {}
        for name in ('_do_init', '_do_destroy', 'load'):
            original_method(source, name, namespace)
        self.assertIn('on_init', namespace['_do_init'].__code__.co_names)
        self.assertNotIn('on_init', namespace['load'].__code__.co_names)
        names = namespace['_do_destroy'].__code__.co_names
        self.assertIn('_panels', names)
        self.assertIn('pop', names)
        self.assertIn('delattr', names)
        # Finite host lifecycle below models those boundaries; renderer/native
        # load/destroy leaves are NOT represented as native validation.
        panel = self.panel
        self.build(panel); self.build(panel)
        self.assertIs(self.panel, panel)
        self.destroy(panel)
        self.assertIsNot(self.panel, panel)

    def test_fixture_provenance_and_facade_identity_static_boundary(self):
        self.assertEqual(hashlib.sha256(FIXTURE.read_bytes()).hexdigest(), '9c6d13c5f163427f64ccda0c16bb424254803ea16dfa5588f8776569ea630c46')
        for name in ('settlement_ended', '_close_panel', 'process_area_op_end', 'city_attention'):
            ns = {}; original_method(FIXTURE.read_text(), name, ns)
            # Real Panel is only accessed through attrs/bound methods: no
            # super/base/native calls receiving facade as an explicit self arg.
            code = ns[name].__code__
            self.assertNotIn('super', code.co_names)
            self.assertNotIn('isinstance', code.co_names)
            start = FIXTURE.read_text().index('    def ' + name + '(')
            following = re.search(r'\n    (?:def |@)', FIXTURE.read_text()[start + 1:])
            body = FIXTURE.read_text()[start:start + 1 + following.start()] if following else FIXTURE.read_text()[start:FIXTURE.read_text().rindex('\n\nreturn')]
            body = body.replace("print 'settlement_ended ======================================'", "print('settlement_ended ======================================')")
            tree = ast.parse(textwrap.dedent(body))
            parents = {child: parent for parent in ast.walk(tree) for child in ast.iter_child_nodes(parent)}
            for node in ast.walk(tree):
                if isinstance(node, ast.Name) and node.id == 'self':
                    self.assertIsInstance(parents[node], ast.Attribute)
                    self.assertIs(parents[node].value, node)


if __name__ == '__main__': unittest.main()
