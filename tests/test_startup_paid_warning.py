"""Host check for the startup anti-paid warning private message."""
import _paths  # noqa: E402,F401
import importlib.util
import sys
import types
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]


class PrivateMsg(object):
    def __init__(self, info):
        self.id = info['id']
        self.readed = info.get('rd', False)
        self.replyed = info.get('rp', False)
        self.reciveTime = info.get('rt')


class ClientAvatar(object):
    def init_from_dict(self, data):
        self.socialData = types.SimpleNamespace(privateMsg={})
        return self


class StartupPaidWarningTests(unittest.TestCase):
    def test_warning_is_seeded_as_unread_private_message(self):
        events = []
        private_msg = types.ModuleType('com.data.cdata.private_msg')
        private_msg.data = {}
        social = types.ModuleType('entity.avatar_attrs.SocialData')
        social.PrivateMsg = PrivateMsg
        client = types.ModuleType('entity.ClientAvatar')
        client.ClientAvatar = ClientAvatar
        gg = types.ModuleType('gg')
        gg.ui = types.SimpleNamespace(_tree=types.SimpleNamespace(
            proc_event=lambda *args, **kwargs: events.append((args, kwargs))))
        modules = {
            'com': types.ModuleType('com'),
            'com.data': types.ModuleType('com.data'),
            'com.data.cdata': types.ModuleType('com.data.cdata'),
            'com.data.cdata.private_msg': private_msg,
            'entity': types.ModuleType('entity'),
            'entity.avatar_attrs': types.ModuleType('entity.avatar_attrs'),
            'entity.avatar_attrs.SocialData': social,
            'entity.ClientAvatar': client,
            'gg': gg,
        }
        with patch.dict(sys.modules, modules):
            spec = importlib.util.spec_from_file_location(
                'warning_module', ROOT / 'offline/runtime/offline_tutorials.py')
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            module.install_paid_warning()
            entry = private_msg.data[module.PAID_WARNING_ID]
            self.assertEqual(entry['npc'], 60000)
            self.assertEqual(entry['title'], module.PAID_WARNING_TITLE)
            self.assertEqual(entry['content'], module.PAID_WARNING_TEXT)
            self.assertIn('被骗了', entry['content'])

            avatar = ClientAvatar()
            avatar.init_from_dict({})
            self.assertIn(module.PAID_WARNING_ID, avatar.socialData.privateMsg)
            self.assertFalse(avatar.socialData.privateMsg[module.PAID_WARNING_ID].readed)
            self.assertTrue(events)

    def test_tutorial_bypass_does_not_eagerly_import_client_avatar(self):
        """Paid-warning install must not materialize Member caches early."""
        modules = {}
        def module(name):
            value = types.ModuleType(name)
            value.__path__ = []
            modules[name] = value
            return value
        for name in ('entity', 'entity.avatar_attrs', 'entity.avatar_members',
                     'cocos', 'cocos.panels'):
            module(name)
        targets = (
            ('entity.avatar_attrs.NewbeeData', 'NewbeeData'),
            ('entity.avatar_members.NewbeeMember', 'Member'),
            ('entity.avatar_members.EventTriggerMember', 'Member'),
        ) + tuple(('cocos.panels.' + name, 'Panel') for name in (
            'newbee_guidance', 'newbee_mask', 'combat_guide_hero',
            'combat_guide_restrain', 'city_yanhua_guide', 'combat_monster',
            'city', 'common_confirm'))
        for name, clsname in targets:
            setattr(module(name), clsname, type(clsname, (), {}))
        saved = sys.modules.pop('entity.ClientAvatar', None)
        try:
            with patch.dict(sys.modules, modules):
                spec = importlib.util.spec_from_file_location(
                    'bypass_module', ROOT / 'offline/runtime/offline_tutorials.py')
                bypass = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(bypass)
                bypass._f7_log = lambda ignored: None
                bypass.install_tutorial_bypass()
                self.assertNotIn('entity.ClientAvatar', sys.modules)
        finally:
            if saved is not None:
                sys.modules['entity.ClientAvatar'] = saved


if __name__ == '__main__':
    unittest.main()
