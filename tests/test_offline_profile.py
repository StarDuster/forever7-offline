import copy
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'runtime'))
from offline_profile import grant_profile_skins, validate_hero_profile, migrate_full_hero_roster, migrate_released_wardrobe


def empty_hero():
    hero = json.loads((ROOT / 'tests/fixtures/native-hero24.json').read_text())['hero']
    hero['sk'], hero['cs'] = {}, None
    return hero


class OfflineProfileTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        raw = json.loads((ROOT / 'tests/fixtures/hero24-skins.json').read_text())
        cls.catalog = {int(key): value for key, value in raw['rows'].items()}

    def test_grant_is_idempotent_and_current_skin_is_a_real_owned_default_instance(self):
        hero = empty_hero()
        ids = iter(['000000000000000000000001', '000000000000000000000002'])
        grant_profile_skins(24, hero, [24, 10023], self.catalog, lambda: next(ids), 123)
        before = copy.deepcopy(hero)
        grant_profile_skins(24, hero, [24, 10023], self.catalog, lambda: self.fail('Duplicate grant'), 999)
        self.assertEqual(hero, before)
        self.assertEqual(hero['sk'][hero['cs']]['i'], 24)
        self.assertEqual({skin['i'] for skin in hero['sk'].values()}, {24, 10023})
        validate_hero_profile({'version': 1, 'heroes': {'24': hero}, 'migrations': []})

    def test_special_unreleased_transformation_is_not_silently_granted_as_ordinary_costume(self):
        with self.assertRaises(ValueError):
            grant_profile_skins(24, empty_hero(), [10081], self.catalog, lambda: '0' * 24, 123)

    def test_skin_cannot_be_granted_to_another_hero(self):
        with self.assertRaises(ValueError):
            grant_profile_skins(20, empty_hero(), [10023], self.catalog, lambda: '0' * 24, 123)

    def test_invalid_current_id_and_uuid4_are_rejected_before_native_loading(self):
        hero = empty_hero()
        grant_profile_skins(24, hero, [24], self.catalog, lambda: '0' * 24, 123)
        profile = {'version': 1, 'heroes': {'24': hero}, 'migrations': []}
        hero['cs'] = None
        with self.assertRaises(ValueError):
            validate_hero_profile(profile)
        instance = '12345678-1234-1234-1234-123456789012'
        hero['sk'] = {instance: {'i': 24, 'u': instance}}
        hero['cs'] = instance
        with self.assertRaises(ValueError):
            validate_hero_profile(profile)

    def test_same_instance_id_cannot_be_used_by_two_heroes(self):
        hero = empty_hero()
        grant_profile_skins(24, hero, [24], self.catalog, lambda: '0' * 24, 123)
        with self.assertRaises(ValueError):
            validate_hero_profile({'version': 1, 'heroes': {'24': hero, '20': copy.deepcopy(hero)}, 'migrations': []})

    def test_all_140_heroes_migrate_once_preserving_selection_and_upgrades(self):
        data = json.loads((ROOT / 'tests/fixtures/all-hero-roster.json').read_text())
        heroes = {int(key): value for key, value in data['heroes'].items()}
        skins = {int(key): value for key, value in data['skins'].items()}
        ids = iter('%024x' % value for value in range(1, 200))
        first, changed = migrate_full_hero_roster(None, heroes, skins,
            lambda hero_id: empty_hero(), lambda: next(ids), 123)
        self.assertTrue(changed)
        self.assertEqual(len(first['heroes']), 140)
        self.assertEqual(sum(len(hero['sk']) for hero in first['heroes'].values()), 141)
        self.assertTrue({'46', '125'} <= set(first['heroes']))
        for key, hero in first['heroes'].items():
            row = heroes[int(key)]
            self.assertEqual((hero['sl'], hero['so']),
                             (row['hero_composite_init_rank'], row['hero_composite_init_order']))
        hero = first['heroes']['24']
        hero['cs'] = next(uid for uid, skin in hero['sk'].items() if skin['i'] == 10023)
        hero['sl'], hero['so'] = 4, 4
        second, changed = migrate_full_hero_roster(first, heroes, skins,
            lambda _: self.fail('Must not reconstruct saved heroes'),
            lambda: self.fail('Must not grant duplicate instances'), 999)
        self.assertFalse(changed)
        self.assertEqual(first, second)
        self.assertEqual(second['heroes']['24']['sk'][second['heroes']['24']['cs']]['i'], 10023)
        self.assertEqual((second['heroes']['24']['sl'], second['heroes']['24']['so']), (4, 4))

    def test_released_wardrobe_preserves_saved_dyes_and_matches_catalog_plan(self):
        sys.path.insert(0, str(ROOT / 'analysis/research-agent'))
        from read_literal_marshal import read
        base = ROOT / 'analysis/android640-scripts/com/data/cdata'
        skins = read(base / 'skin.marshal')
        heroes = read(base / 'hero.marshal')
        awake = read(base / 'awake_consume_data.marshal')
        ids = iter('%024x' % value for value in range(1, 1000))
        original, _ = migrate_full_hero_roster(None, heroes, skins,
            lambda _: empty_hero(), lambda: next(ids), 123)
        h = original['heroes']['24']
        h['cs'] = next(uid for uid, skin in h['sk'].items() if skin['i'] == 10023)
        h['sk'][h['cs']]['cd'] = {'1': [12, 34, 56]}
        before = copy.deepcopy(original)
        result, changed = migrate_released_wardrobe(original, skins, awake,
            lambda: next(ids), 456)
        self.assertTrue(changed)
        self.assertEqual(original, before)
        expected = json.loads((ROOT / 'reports/full-wardrobe-grant-plan.json').read_text())
        actual = {skin['i'] for h in result['heroes'].values() for skin in h['sk'].values()}
        self.assertEqual(actual, set(expected['retain_or_grant_candidate_ids']))
        self.assertEqual(len(actual), 361)
        for key, h in original['heroes'].items():
            self.assertEqual(result['heroes'][key]['cs'], h['cs'])
            for uid, skin in h['sk'].items():
                self.assertEqual(result['heroes'][key]['sk'][uid], skin)
        again, changed = migrate_released_wardrobe(result, skins, awake,
            lambda: self.fail('Duplicate instance allocation'), 789)
        self.assertFalse(changed)
        self.assertEqual(again, result)

    def test_invalid_dye_parent_aborts_without_mutating_saved_profile(self):
        hero = empty_hero()
        grant_profile_skins(24, hero, [24], self.catalog, lambda: '0' * 24, 123)
        original = {'version': 1, 'heroes': {'24': hero}, 'migrations': []}
        before = copy.deepcopy(original)
        skins = dict(self.catalog)
        skins[999999] = {'hero': 24, 'release': 1, 'is_dye_skin': True, 'ori_skin': -1}
        with self.assertRaises(ValueError):
            migrate_released_wardrobe(original, skins, {}, lambda: '1' * 24, 456)
        self.assertEqual(original, before)


if __name__ == '__main__':
    unittest.main()
