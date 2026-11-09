import importlib.util
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('gacha_archive', ROOT / 'runtime/offline_gacha_archive.py')
archive = importlib.util.module_from_spec(spec)
spec.loader.exec_module(archive)


class ArchiveTests(unittest.TestCase):
    def setUp(self):
        archive.offline_archive_clear()
        contracts = json.loads((ROOT / 'reports/gacha-pool-contracts.json').read_text())
        self.table = {row['wire_t']: row['configuration'] for row in contracts['all_pool_contracts']}
        self.rows = archive.archive_catalog(self.table)

    def test_complete_catalog_and_separate_furniture(self):
        self.assertEqual(len(self.rows), 485)
        self.assertNotIn(354, {row['wire_t'] for row in self.rows})
        self.assertEqual(len(archive.archive_filter(self.rows, category='furniture')), 41)
        self.assertEqual({row['wire_t'] for row in self.rows}, (set(self.table) | {99}) - {354})
        for row in self.rows:
            self.assertIn(row, archive.archive_filter(self.rows, str(row['wire_t'])))

    def test_legacy_furniture_106_uses_original_old_panel(self):
        row = next(row for row in self.rows if row['wire_t'] == 106)
        self.assertEqual(row['category'], 'furniture')
        self.assertEqual(row['furniture_panel'], 'city_room_danchi')
        self.assertEqual(row['configuration']['fur_consume_item'], [10051, 10])
        self.assertIn('cocos/city_room_danchi.csb', archive.archive_required_resources(row))
        self.assertEqual(archive.archive_entry_status(row, lambda path: True), '')
        self.assertEqual(archive.archive_furniture_panel(106, {490: {}}), 'city_room_danchi')
        self.assertEqual(archive.archive_furniture_panel(490, {490: {}}), 'city_room_danchi_new')
        (ROOT / 'runtime/offline_gacha_archive.py').read_text(encoding='ascii')

    def test_dates_preserved_and_searchable(self):
        original = json.dumps(self.table, sort_keys=True)
        row = next(row for row in self.rows if row['wire_t'] == 353)
        self.assertIn(row, archive.archive_filter(self.rows, archive.archive_date(row['begin'])))
        self.assertEqual(json.dumps(self.table, sort_keys=True), original)

    def test_selection_authorizes_only_one_wire(self):
        calls = []
        check = archive.make_archive_check(lambda owner, wire: calls.append(wire) or False)
        self.assertFalse(check(None, 354))
        archive._f7_archive_session = {'wire_t': 353, 'category': 'hero_treasure'}
        self.assertTrue(check(None, 353))
        self.assertFalse(check(None, 354))
        self.assertEqual(calls, [])
        context = archive.offline_archive_context()
        context['wire_t'] = 1
        self.assertTrue(archive.offline_archive_authorized(353))
        archive.offline_archive_clear()
        self.assertFalse(check(None, 354))

    def test_t5_explicit_period_required_and_bound_to_wire(self):
        table = {1: {'drawType': 5}, 2: {'drawType': 6}}
        row = next(row for row in self.rows if row['wire_t'] == 5)
        for wish_id in (None, 0, 2):
            with self.assertRaises(ValueError):
                archive.archive_make_session(row, table, wish_id)
        context = archive.archive_make_session(row, table, 1)
        self.assertEqual(context['wish_id'], 1)
        self.assertEqual(context['choice_cost_policy'], 'offline-free-treasure-wish-selection-v1')
        with self.assertRaises(ValueError):
            archive.archive_make_session({'wire_t': 354, 'category': 'hero_treasure'}, table, 1)

    def test_resource_failure_keeps_row_visible(self):
        row = next(row for row in self.rows if row['configuration'].get('room_enter_index') == -2)
        self.assertEqual(archive.archive_required_resources(row), ['cocos/card_zixuan.csb'])
        self.assertIn('card_zixuan.csb', archive.archive_entry_status(row, lambda path: False))
        self.assertIn(row, archive.archive_filter(self.rows))
        self.assertEqual(archive.archive_entry_status(row, lambda path: True), '')
        furniture = archive.archive_filter(self.rows, category='furniture')[0]
        self.assertEqual(archive.archive_entry_status(furniture, lambda path: True), '')
        self.assertIn('city_room_danchi.csb', archive.archive_entry_status(furniture, lambda path: False))


if __name__ == '__main__':
    unittest.main()
