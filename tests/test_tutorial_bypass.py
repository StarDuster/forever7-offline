import importlib
from pathlib import Path
import sys
from types import SimpleNamespace, ModuleType
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'runtime'))
import offline_tutorials as tutorials


class TutorialBypassTests(unittest.TestCase):
    def setUp(self):
        self.callbacks = []
        self.messages = []
        tutorials._f7_log = self.messages.append

    def test_overlay_skip_schedules_story_continuation_exactly_once(self):
        completed = []
        fake = SimpleNamespace(exec_delay=lambda delay, callback: self.callbacks.append(callback))
        with patch.dict(sys.modules, {'gg': fake}):
            tutorials.skip_guidance(object(), 172, cb=lambda: completed.append(1000))
        self.assertEqual(completed, [])
        self.assertEqual(len(self.callbacks), 1)
        self.callbacks[0]()
        self.assertEqual(completed, [1000])

    def test_main_event_continues_original_ui_without_granting_completion(self):
        started = []
        avatar = SimpleNamespace(startEventUI=lambda event: started.append(event), completed_events=set())
        tutorials.continue_story_without_teaching(avatar, 1000)
        self.assertEqual(started, [1000])
        self.assertFalse(avatar.completed_events)

    def test_tutorial_requests_are_stopped_before_ui_lock_or_rpc(self):
        data = SimpleNamespace(clent_trigger_event_list=[172], finish_newbee=[])
        avatar = SimpleNamespace(newbeeData=data)
        self.assertFalse(tutorials.skip_newbee_request(avatar, 172))
        self.assertEqual(data.clent_trigger_event_list, [])
        self.assertEqual(data.finish_newbee, [])

    def test_installer_patches_only_teaching_confirm_not_ordinary_confirmation(self):
        targets = {
            'entity.avatar_attrs.NewbeeData': 'NewbeeData',
            'entity.avatar_members.NewbeeMember': 'Member',
            'entity.avatar_members.EventTriggerMember': 'Member',
            'cocos.panels.newbee_guidance': 'Panel',
            'cocos.panels.newbee_mask': 'Panel',
            'cocos.panels.combat_guide_hero': 'Panel',
            'cocos.panels.combat_guide_restrain': 'Panel',
            'cocos.panels.combat_monster': 'Panel',
            'cocos.panels.city_yanhua_guide': 'Panel',
            'cocos.panels.city': 'Panel',
            'cocos.panels.common_confirm': 'Panel'}
        modules = {}
        ordinary = lambda *args: 'ordinary confirmation'
        for name, class_name in targets.items():
            pieces = name.split('.')
            for size in range(1, len(pieces) + 1):
                current = '.'.join(pieces[:size])
                if current not in modules:
                    modules[current] = ModuleType(current)
                    modules[current].__path__ = []
                if size > 1:
                    setattr(modules['.'.join(pieces[:size - 1])], pieces[size - 1], modules[current])
            setattr(modules[name], class_name, type(class_name, (), {'notify_confirm': ordinary}))
        with patch.dict(sys.modules, modules):
            tutorials.install_tutorial_bypass()
        panel = modules['cocos.panels.common_confirm'].Panel
        self.assertIs(panel.notify_confirm, ordinary)
        self.assertIs(panel.notify_guide_bind, tutorials.skip_tutorial_panel)
        self.assertIs(modules['cocos.panels.combat_monster'].Panel.notify_show,
                      tutorials.skip_new_monster_tutorial)
        self.assertIs(modules['entity.avatar_members.EventTriggerMember'].Member.startEventNewbee,
                      tutorials.continue_story_without_teaching)

    def test_new_monster_skip_neither_freezes_nor_thaws_or_changes_discovery(self):
        monsters = [14, 15]
        def unexpected(*args):
            self.fail('Intro bypass must not show/hide the modal or change battle freeze state')
        panel = SimpleNamespace(frozen_by_other_system=True, discovered=[1],
                                notify_hide=unexpected, freeze_battle_logic=unexpected)
        original = dict(vars(panel))
        tutorials.skip_new_monster_tutorial(panel, monsters)
        self.assertEqual(monsters, [14, 15])
        self.assertEqual(vars(panel), original)
        self.assertEqual(self.callbacks, [])

    def test_disabled_tutorial_bypass_does_not_import_or_patch_panels(self):
        with patch.object(tutorials, 'SKIP_TUTORIAL_UI', False), patch(
                'builtins.__import__', side_effect=AssertionError('Disabled installer imported a panel')):
            tutorials.install_tutorial_bypass()


if __name__ == '__main__':
    unittest.main()
