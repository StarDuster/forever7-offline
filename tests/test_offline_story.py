import copy
import json
from pathlib import Path
import sys
import tempfile
from types import ModuleType
import unittest
from unittest.mock import patch
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'runtime'))
from offline_story import initial_story_state, prepare_opening_story, refresh_opening_triggers, prepare_starter_choice, story_trigger_eligible

class OpeningStoryTests(unittest.TestCase):
    def setUp(self):
        raw = json.loads((ROOT / 'tests/fixtures/opening-story.json').read_text())
        self.content = {int(k): v for k, v in raw['content'].items()}
        self.triggers = {int(k): dict(v, conds={int(n): value for n, value in v['conds'].items()}) for k, v in raw['triggers'].items()}
        self.rewards = {int(k): v for k, v in raw['rewards'].items()}
        self.state = {'available_events': [[1000, 1]], 'processing_events': [], 'completed_events': [],
                      'event_traces': [], 'story': initial_story_state(), 'profile': {'heroes': {'24': {}}}}

    def act(self, operation, args):
        self.state, notices = prepare_opening_story(self.state, operation, args, self.content, self.triggers, self.rewards)
        return notices

    def start(self, event):
        self.assertIn(event, dict(self.state['available_events']))
        self.state['available_events'] = [r for r in self.state['available_events'] if r[0] != event]
        self.state['processing_events'].append(event)
        return self.act('start', {'e': event})

    def dialog(self, event):
        return self.act('trace', {'k': 'dialog', 'd': {'c': event}})

    def test_actual_dialogue_options_and_loop_reach_first_area_fight(self):
        self.start(1000)
        self.dialog(9999)
        self.assertNotIn(1000, self.state['completed_events'])
        notices = self.dialog(1000)
        self.assertIn(('syncAllNote', {'nd': {'p': {}, 'n': {}, 'pn': [10044], 'ppn': True}}), notices)
        self.assertIn(1006, dict(self.state['available_events']))
        self.assertNotIn(1001, dict(self.state['available_events']))
        self.start(1006)
        self.dialog(1006)
        self.assertIn(1006, self.state['processing_events'])
        self.assertFalse(set((1015, 1016, 1017)) & set(dict(self.state['available_events'])))
        for parent, selected in ((1006, 1015), (1015, 1018), (1018, 1016), (1016, 1018), (1018, 1019), (1019, 8)):
            self.act('option', {'e': parent, 'se': selected, 'op': 0})
        self.assertIn(8, self.state['completed_events'])
        self.assertFalse(self.state['story']['emergency'])
        self.assertIn(1001, dict(self.state['available_events']))
        self.assertFalse(set((1015, 1016, 1017, 1019)) & set(dict(self.state['available_events'])))
        self.start(1001)
        notices = self.dialog(1001)
        self.assertIn(('completeEventReplyStart', {'e': 1001, 'r': {'hero': [24]}}), notices)
        before = copy.deepcopy(self.state)
        self.assertFalse(self.dialog(1001))
        self.assertEqual(self.state, before)
        self.start(1002)
        self.dialog(1002)
        self.act('option', {'e': 1002, 'se': 1004, 'op': 0})
        self.content[1021] = {'dialog': 1021, 'completeConds': {'dialog': [1021]}, 'newbee_event': 90}
        self.act('option', {'e': 1004, 'se': 1021, 'op': 1})
        self.assertIn(1004, self.state['completed_events'])
        self.assertEqual(self.state['story']['city_areas']['1']['stage'], {'cs': 101, 'sl': [[101]]})
        self.assertIn(1021, self.state['processing_events'])
        self.assertEqual(list(self.state['profile']['heroes']), ['24'])

    def test_invalid_option_and_unimplemented_effect_preserve_processing(self):
        self.start(1000)
        self.content[1000]['areaFight'] = [1]
        self.content[1000]['rewards'] = [999]
        notices = self.dialog(1000)
        self.assertFalse(notices)
        self.assertIn(1000, self.state['processing_events'])
        self.assertFalse(self.state['story']['city_areas'])
        self.assertFalse(self.state['story']['notes']['pn'])
        before = copy.deepcopy(self.state)
        with self.assertRaises(ValueError):
            self.act('option', {'e': 1000, 'se': 1001})
        self.assertEqual(self.state, before)

    def test_external_20030_is_durable_idempotent_and_has_dedicated_unlock_reply(self):
        notices = self.act('external', {'e': 20030})
        self.assertEqual(notices[0], ('triggerExternalEventReply', {}))
        self.assertEqual(self.state['completed_events'], [20030])
        before = copy.deepcopy(self.state)
        self.act('external', {'e': 20030})
        self.assertEqual(self.state, before)
        self.assertEqual(self.act('external', {'e': 99999}), [('triggerExternalEventReply', {})])
        self.assertEqual(self.state, before)

    def test_embedded_gateway_callback_order_disk_rollback_and_restart(self):
        scope = {'__name__': 'embedded_story_runtime'}
        for name in ('offline_store.py', 'offline_wardrobe_completion.py', 'offline_transport.py', 'offline_event_battle.py', 'offline_battle.py', 'offline_profile.py', 'offline_stage.py', 'offline_week.py', 'offline_day.py', 'offline_conditions.py', 'offline_story.py', 'offline_event_effects.py', 'offline_story_engine.py', 'offline_city_actions.py', 'offline_avatar_snapshot.py', 'offline_postbattle.py', 'offline_gacha.py', 'local_gateway.py'):
            exec(compile((ROOT / 'runtime' / name).read_text(), name, 'exec'), scope)
        from test_local_gateway import Owner
        modules = {name: ModuleType(name) for name in ('com', 'com.data', 'com.data.cdata', 'com.data.cdata.event_content', 'com.data.cdata.event_condition', 'com.data.cdata.reward_common', 'com.data.cdata.notepad')}
        modules['com.data.cdata.event_content'].data = self.content
        modules['com.data.cdata.event_condition'].data = self.triggers
        modules['com.data.cdata.reward_common'].data = self.rewards
        modules['com.data.cdata.notepad'].data = {10044: {'type': 1}}
        with tempfile.TemporaryDirectory() as folder, patch.dict(sys.modules, dict(modules, offline_story=None)):
            scope['_f7_doc'], scope['_f7_log'] = folder, lambda _: None
            owner = Owner()
            proxy = scope['LocalProxy'](None, owner, persistent=True)
            def rpc(method, args, callback=7):
                proxy.reliable_call({'w': {'m': method, 'p': args, 'r': 1}, '_cbid_': callback})
            rpc('startEvent', {'e': 1000})
            rpc('clientTraceProcessingEvent', {'k': 'dialog', 'd': {'c': 1000}})
            self.assertIn(1006, proxy.available_events)
            proxy = scope['LocalProxy'](None, owner, persistent=True)
            self.assertIn(1006, proxy.available_events)
            self.assertEqual(proxy.story['notes']['pn'], [10044])
            rpc('startEvent', {'e': 1006})
            owner.replies.clear()
            rpc('startEventOption', {'e': 1006, 'se': 1015, 'op': 0}, 9)
            names = [n for n, args in owner.replies]
            self.assertLess(names.index('serverCallbackCarrier'), names.index('startEventReply'))
            self.assertIn(1015, proxy.processing_events)
            saved = proxy.progress_snapshot()
            owner.replies.clear()
            with patch.object(proxy._store, 'write', side_effect=OSError('disk full')):
                with self.assertRaises(OSError):
                    rpc('triggerExternalEvent', {'e': 20030}, 10)
            self.assertEqual(proxy.progress_snapshot(), saved)
            self.assertEqual([n for n, args in owner.replies], ['reliableRpcAck', 'triggerExternalEventReply', 'serverCallbackCarrier'])
            owner.replies.clear()
            rpc('triggerExternalEvent', {'e': 20030}, 11)
            self.assertIn(20030, proxy.completed_events)
            restored = scope['LocalProxy'](None, Owner(), persistent=True)
            self.assertIn(20030, restored.completed_events)
            self.assertEqual(sum(n == 'triggerExternalEventReply' for n, args in owner.replies), 1)

    def test_unknown_story_version_and_bad_containers_are_rejected(self):
        from test_local_gateway import gateway, Owner
        with tempfile.TemporaryDirectory() as folder:
            gateway._f7_doc, gateway._f7_log = folder, lambda _: None
            proxy = gateway.LocalProxy(None, Owner(), persistent=True)
            saved = proxy.progress_snapshot()
            for key, bad in (('version', 2), ('notes', []), ('city_areas', []), ('reward_receipts', {})):
                corrupt = copy.deepcopy(saved)
                corrupt['story'][key] = bad
                with self.assertRaises(ValueError):
                    gateway.validate_gateway_progress(corrupt)
            legacy = copy.deepcopy(saved)
            legacy.pop('story')
            legacy['completed_events'] = [1000, 8]
            legacy['available_events'] = []
            proxy.restore_progress(legacy)
            self.assertEqual(proxy.story['notes']['pn'], [10044])
            self.assertFalse(proxy.story['emergency'])

    def test_original_choice_callback_runs_after_touch_finishes_without_dead_node_access(self):
        from types import SimpleNamespace
        from offline_story import install_story_ui_compatibility
        order, pending = [], []
        class Choice:
            def set_click_cb(self, callback):
                self.click_cb = callback
            def on_click(self):
                order.append('touch-began')
                self.click_cb()
                if not self.node_alive:
                    raise RuntimeError('self == NULL')
                order.append('touch-color-restored')
        modules = {name: ModuleType(name) for name in ('cocos', 'cocos.comps', 'cocos.comps.dialogue_common', 'cocos.comps.dialogue_common.choose')}
        modules['cocos.comps.dialogue_common.choose'].Comp = Choice
        modules['gg'] = SimpleNamespace(exec_delay=lambda delay, callback: pending.append(callback))
        with patch.dict(sys.modules, modules):
            install_story_ui_compatibility()
            installed = Choice.set_click_cb
            install_story_ui_compatibility()
            self.assertIs(Choice.set_click_cb, installed)
            choice = Choice()
            choice.node_alive = True
            def original_continuation():
                order.append('original-dialogue-continuation')
                choice.node_alive = False
            choice.set_click_cb(original_continuation)
            choice.on_click()
            choice.on_click()
            self.assertEqual(len(pending), 1)
            self.assertTrue(choice.node_alive)
            self.assertEqual(order, ['touch-began', 'touch-color-restored'] * 2)
            pending.pop()()
            self.assertFalse(choice.node_alive)
            self.assertEqual(order[-1], 'original-dialogue-continuation')

            forwarded = []
            reused = Choice()
            reused.set_click_cb(lambda *args, **kwargs: forwarded.append((args, kwargs)))
            reused.click_cb(7, source='original')
            reused.click_cb(8, source='duplicate')
            self.assertEqual(len(pending), 1)
            pending.pop()()
            self.assertEqual(forwarded, [((7,), {'source': 'original'})])
            reused.click_cb(9, source='later')
            pending.pop()()
            self.assertEqual(forwarded[-1], ((9,), {'source': 'later'}))

    def test_player_selection_avoids_all_owned_hero_branches_and_resumes_original_1043(self):
        self.state['profile']['heroes'].update({'7': {}, '8': {}, '37': {}})
        self.state['story']['emergency'] = False
        self.state['story']['city_areas'] = {'1': {'st': [1, False, False]}}
        self.state['completed_events'] = [1021]
        self.state['available_events'] = []
        refresh_opening_triggers(self.state, self.triggers)
        self.assertFalse(set((1038, 1039, 1040)) & set(dict(self.state['available_events'])))
        for hero, event in ((8, 1038), (7, 1039), (37, 1040)):
            selected = prepare_starter_choice(self.state, hero, self.triggers)
            self.assertEqual(set(dict(selected['available_events'])) & {1038, 1039, 1040}, {event})
            selected['available_events'] = []
            selected['processing_events'] = [event]
            selected, _ = prepare_opening_story(selected, 'trace', {'k': 'dialog', 'd': {'c': event}}, self.content, self.triggers, self.rewards)
            self.assertIn(1043, dict(selected['available_events']))
            selected['processing_events'].append(1043)
            selected, notices = prepare_opening_story(selected, 'trace', {'k': 'battle', 'd': {'c': 101}}, self.content, self.triggers, self.rewards)
            self.assertIn(1043, selected['processing_events'])
            self.assertNotIn(('completeEventReplyEnd', {'e': 1043}), notices)
            selected, notices = prepare_opening_story(selected, 'combat_win', {'k': 'battle', 'd': {'c': 101}}, self.content, self.triggers, self.rewards)
            self.assertIn(1043, selected['completed_events'])
        restored = copy.deepcopy(self.state)
        restored['completed_events'].append(1039)
        refresh_opening_triggers(restored, self.triggers)
        self.assertEqual(restored['story']['starter_hero'], 7)
        self.assertEqual(restored['story']['starter_source'], 'original-event-history')
        with self.assertRaises(ValueError):
            prepare_starter_choice(restored, 8, self.triggers)

    def test_typed_conditions_reject_unknown_and_keep_owned_roster_distinct_from_choice(self):
        self.state['profile']['heroes']['7'] = {}
        self.assertTrue(story_trigger_eligible({'release': True, 'conds': {24: 'set([7])'}}, self.state))
        self.assertFalse(story_trigger_eligible({'release': True, 'conds': {24: 'set([7])'}}, self.state, True))
        self.assertFalse(story_trigger_eligible({'release': True, 'conds': {999: '1'}}, self.state))
        self.state['story']['city_areas'] = {'1': {'st': [1, False, False]}, '2': {'st': [0, False, False]}}
        self.assertTrue(story_trigger_eligible({'release': True, 'conds': {8: '{1: (1,), 2: (0,1)}'}}, self.state))
        self.assertTrue(story_trigger_eligible({'release': True, 'conds': {8: '{1: (1,), 2: (2,)}'}}, self.state))
        self.assertFalse(story_trigger_eligible({'release': True, 'conds': {8: '{1: (0,), 2: (2,)}'}}, self.state))

    def test_original_picker_cancel_keeps_nonmodal_reentry_without_saving_or_forced_reopen(self):
        from types import SimpleNamespace
        from offline_story import offer_story_starter_choice
        pending, saved, layers = [], [], []
        class Button:
            @classmethod
            def create(cls):
                return cls()
            def __getattr__(self, name):
                return lambda *args: None
            def addTouchEventListener(self, callback):
                self.touch = callback
            def setVisible(self, visible):
                self.visible = visible
        class Picker:
            valid = False
            def notify_close(self):
                self.valid = False
        picker = Picker()
        parent = SimpleNamespace(valid=True, _node=SimpleNamespace(addChild=lambda *args: None))
        parent.add_layer = lambda panel: layers.append(panel) or 'original-picker-layer'
        def show_event(name, **kwargs):
            picker.choose_heroes = kwargs['choose_heroes']
            picker.ui_logic, picker.ui_config = kwargs['ui_logic'], kwargs['ui_config']
            picker.valid = True
        parent.proc_event = show_event
        owner = object()
        proxy = SimpleNamespace(owner=owner, completed_events={1021}, story=initial_story_state(),
            defer=lambda delay, callback: pending.append(callback),
            confirm_story_starter=lambda selected: saved.append(selected) or True)
        engine = SimpleNamespace(avatar=owner, logic=SimpleNamespace(game_state=SimpleNamespace(current=6)),
            ui=SimpleNamespace(_dialogue=None, panels=SimpleNamespace(city=parent, card_hero_choose=picker)))
        const = ModuleType('com.const')
        const.GameState = SimpleNamespace(CITY=6)
        ui = ModuleType('cocos.panels.card_hero_choose')
        ui.UILogic, ui.UIConfig = type('OriginalLogic', (), {}), type('OriginalConfig', (), {})
        modules = {'gg': engine, 'com': ModuleType('com'), 'com.const': const, 'cocosui': SimpleNamespace(ccui=SimpleNamespace(Button=Button, TOUCH_EVENT_ENDED=2), cc=SimpleNamespace(Size=lambda *a: a, Vec2=lambda *a: a)), 'cocos': ModuleType('cocos'), 'cocos.panels': ModuleType('cocos.panels'), ui.__name__: ui}
        with patch.dict(sys.modules, modules):
            offer_story_starter_choice(proxy)
            pending.pop()()
            self.assertEqual(picker.ui_logic.get_select_heroes(picker), [7, 8, 37])
            self.assertTrue(parent._f7_story_entry.visible)
            picker.notify_close()
            offer_story_starter_choice(proxy)
            self.assertFalse(pending)
            self.assertFalse(saved)
            self.assertIsNone(proxy.story['starter_hero'])
            parent._f7_story_entry.touch(parent._f7_story_entry, 2)
            pending.pop()()
            self.assertTrue(picker.valid)
            picker.choose_heroes[0] = 8
            picker.ui_logic.on_click_done(picker)
            self.assertEqual(saved, [8])
            self.assertFalse(picker.valid)
