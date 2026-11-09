import copy
import sys
import unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'runtime'))
sys.path.insert(0, str(ROOT / 'analysis/research-agent'))
from offline_profile import migrate_full_hero_roster, migrate_released_wardrobe, migrate_awakening_wardrobe, change_awakening_style
from test_offline_profile import empty_hero
from read_literal_marshal import read

class AwakeningTests(unittest.TestCase):
    def setUp(self):
        base = ROOT / 'analysis/android640-scripts/com/data/cdata'
        self.heroes = read(base / 'hero.marshal')
        self.skins = read(base / 'skin.marshal')
        self.awake = read(base / 'awake_consume_data.marshal')
        ids = iter('%024x' % n for n in range(1, 2000))
        self.make_id = lambda: next(ids)
        profile, _ = migrate_full_hero_roster(None, self.heroes, self.skins, lambda _: empty_hero(), self.make_id, 123)
        self.original, _ = migrate_released_wardrobe(profile, self.skins, self.awake, self.make_id, 123)
        self.profile, _ = migrate_awakening_wardrobe(self.original, self.heroes, self.skins, self.awake, self.make_id, 123)

    def test_real_catalog_migration_unlocks_118_styles_idempotently(self):
        self.assertEqual(sum(s.get('ias', False) for h in self.profile['heroes'].values() for s in h['sk'].values()), 118)
        for hid, hero in self.profile['heroes'].items():
            if hero.get('as'):
                self.assertEqual(hero['as'], 1)
                self.assertEqual(hero['ar']['aao'], self.awake[(int(hid), 1)]['artifact_level_up'])
            self.assertEqual(hero['cs'], self.original['heroes'][hid]['cs'])
        again, changed = migrate_awakening_wardrobe(self.profile, self.heroes, self.skins, self.awake, lambda: self.fail('duplicate'), 999)
        self.assertFalse(changed)
        self.assertEqual(again, self.profile)

    def test_toggle_repeat_revert_and_reopen_after_normal_change(self):
        hero = self.profile['heroes']['24']
        original = hero['cs']
        result = change_awakening_style(self.profile, 24, True, self.heroes, self.awake)
        self.assertTrue(hero['sk'][result['newsi']]['ias'])
        change_awakening_style(self.profile, 24, True, self.heroes, self.awake)
        self.assertEqual(hero['lncs'], original)
        change_awakening_style(self.profile, 24, False, self.heroes, self.awake)
        self.assertEqual(hero['cs'], original)
        other = next(uid for uid, s in hero['sk'].items() if s['i'] == 10023)
        hero['cs'], hero['ass'] = other, False
        change_awakening_style(self.profile, 24, True, self.heroes, self.awake)
        change_awakening_style(self.profile, 24, False, self.heroes, self.awake)
        self.assertEqual(hero['cs'], other)

    def test_invalid_requests_do_not_mutate_profile(self):
        before = copy.deepcopy(self.profile)
        for hid, enabled in ((99999, True), (24, 'true')):
            with self.assertRaises(ValueError):
                change_awakening_style(self.profile, hid, enabled, self.heroes, self.awake)
        self.assertEqual(before, self.profile)

    def test_preserves_higher_progression(self):
        self.profile['heroes']['24']['as'] = 4
        self.profile['heroes']['24']['ar']['aao'] = 31
        again, _ = migrate_awakening_wardrobe(self.profile, self.heroes, self.skins, self.awake, self.make_id, 999)
        self.assertEqual(again['heroes']['24']['as'], 4)
        self.assertEqual(again['heroes']['24']['ar']['aao'], 31)

    def test_gateway_callback_and_persistence_failure(self):
        import tempfile
        from types import ModuleType
        from unittest.mock import patch
        from test_local_gateway import gateway, Owner
        gateway.change_awakening_style = change_awakening_style
        modules = {name: ModuleType(name) for name in
                   ('com', 'com.data', 'com.data.cdata', 'com.data.cdata.hero',
                    'com.data.cdata.awake_consume_data')}
        modules['com.data.cdata.hero'].data = self.heroes
        modules['com.data.cdata.awake_consume_data'].data = self.awake
        with tempfile.TemporaryDirectory() as folder, patch.dict(sys.modules, modules):
            gateway._f7_doc = folder
            gateway._f7_log = lambda _: None
            owner = Owner()
            proxy = gateway.LocalProxy(None, owner, persistent=True)
            proxy.profile = copy.deepcopy(self.profile)
            proxy.save_progress()
            proxy.change_awake_skin_style({'hid': 24, 'ss': True, '_cbid_': 17})
            self.assertEqual(owner.replies[-1][0], 'replyChangeAwakeSkinStyle')
            self.assertEqual(owner.replies[-1][1]['_cbid_'], 17)
            saved = copy.deepcopy(proxy.profile)
            with patch.object(proxy._store, 'write', side_effect=OSError('disk full')):
                with self.assertRaises(OSError):
                    proxy.change_awake_skin_style({'hid': 24, 'ss': False, '_cbid_': 18})
            self.assertEqual(proxy.profile, saved)
            self.assertEqual(owner.replies[-1], ('serverCallbackCarrier', {'_r_': {}, '_cbid_': 18}))
            ordinary = saved['heroes']['24']['lncs']
            with patch.object(proxy._store, 'write', side_effect=OSError('disk full')):
                with self.assertRaises(OSError):
                    proxy.set_skin({'h': 24, 'sid': ordinary, '_cbid_': 20})
            self.assertEqual(proxy.profile, saved)
            self.assertEqual(owner.replies[-1][0], 'setSkinReply')
            self.assertFalse(owner.replies[-1][1]['s'])
            self.assertEqual(owner.replies[-1][1]['_cbid_'], 20)
            proxy.change_awake_skin_style({'hid': 99999, 'ss': True, '_cbid_': 19})
            self.assertEqual(owner.replies[-1][1]['_cbid_'], 19)

    def test_embedded_sources_share_globals_without_offline_profile_import(self):
        from types import ModuleType
        from unittest.mock import patch
        modules = {name: ModuleType(name) for name in
                   ('com', 'com.data', 'com.data.cdata', 'com.data.cdata.hero',
                    'com.data.cdata.awake_consume_data')}
        modules['com.data.cdata.hero'].data = self.heroes
        modules['com.data.cdata.awake_consume_data'].data = self.awake
        scope = {'__name__': 'embedded_runtime'}
        exec(compile((ROOT / 'runtime/offline_profile.py').read_text(), 'embedded_profile', 'exec'), scope)
        exec(compile((ROOT / 'runtime/offline_wardrobe_completion.py').read_text(), 'embedded_wardrobe', 'exec'), scope)
        exec(compile((ROOT / 'runtime/offline_battle.py').read_text(), 'embedded_battle', 'exec'), scope)
        exec(compile((ROOT / 'runtime/offline_transport.py').read_text(), 'embedded_transport', 'exec'), scope)
        exec(compile((ROOT / 'runtime/offline_stage.py').read_text(), 'embedded_stage', 'exec'), scope)
        exec(compile((ROOT / 'runtime/offline_day.py').read_text(), 'embedded_day', 'exec'), scope)
        exec(compile((ROOT / 'runtime/offline_story.py').read_text(), 'embedded_story', 'exec'), scope)
        exec(compile((ROOT / 'runtime/offline_postbattle.py').read_text(), 'embedded_postbattle', 'exec'), scope)
        exec(compile((ROOT / 'runtime/local_gateway.py').read_text(), 'embedded_gateway', 'exec'), scope)
        proxy = object.__new__(scope['LocalProxy'])
        proxy.profile = copy.deepcopy(self.profile)
        proxy.save_progress = lambda: None
        replies = []
        proxy.reply = lambda *args: replies.append(args)
        with patch.dict(sys.modules, dict(modules, offline_profile=None)):
            proxy.change_awake_skin_style({'hid': 24, 'ss': True, '_cbid_': 91})
        self.assertEqual(replies[-1][0], 'replyChangeAwakeSkinStyle')
        self.assertEqual(replies[-1][2], 91)
