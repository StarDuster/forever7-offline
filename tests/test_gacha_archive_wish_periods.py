"""Pinned original-period and scoped getter integration checks; no native claim."""
import copy
import json
import unittest
from test_gacha_archive import ROOT, archive


class WishPeriodTests(unittest.TestCase):
    def setUp(self):
        self.periods = json.loads((ROOT / 'reports/treasure-wish-free-selection-ui-contract.json').read_text())['archive_periods']
        self.table = {row['wish_id']: row['original'] for row in self.periods}
        archive.offline_archive_clear()

    def tearDown(self):
        archive.offline_archive_clear()

    def test_all_129_periods_select_exact_id_and_preserve_dates(self):
        before = copy.deepcopy(self.table)
        treasures = {row['treasure_id']: {'name': row['name']} for row in self.periods}
        visible = archive.archive_wish_periods(self.table, 5, treasures)
        self.assertEqual(len(visible), 129)
        self.assertEqual({row['wish_id'] for row in visible}, set(self.table))
        self.assertEqual(archive.archive_wish_periods(self.table, 354), [])
        getter = archive.make_archive_wish_getter(lambda owner, wire: -1, self.table)
        for period in visible:
            archive._f7_archive_session = archive.archive_make_session(
                {'wire_t': 5, 'category': 'hero_treasure'}, self.table, period['wish_id'])
            self.assertEqual(getter(None, 5), period['wish_id'])
            self.assertEqual(archive.offline_archive_context()['begin_time'], tuple(period['begin']))
            self.assertIn(period, archive.archive_filter(visible, str(period['wish_id'])))
            self.assertIn(period, archive.archive_filter(visible, archive.archive_date(period['begin'])))
            self.assertIn(period, archive.archive_filter(visible, period['name']))
        self.assertEqual(self.table, before)

    def test_other_wire_invalid_or_cleared_context_delegates_original(self):
        calls = []
        getter = archive.make_archive_wish_getter(lambda owner, wire: calls.append(wire) or 77, self.table)
        for context, wire in [(None, 5), ({'wire_t': 6, 'wish_id': 1}, 5),
                              ({'wire_t': 5, 'wish_id': 1}, 6),
                              ({'wire_t': 5, 'wish_id': 999999}, 5),
                              ({'wire_t': 354, 'wish_id': 1}, 354)]:
            archive._f7_archive_session = context
            self.assertEqual(getter(None, wire), 77)
        self.assertEqual(calls, [5, 5, 6, 5, 354])

    def test_group_getter_returns_only_same_original_period_and_honors_fixed(self):
        table = {
            1: dict(drawType=5, gid=3, begin_time=[2019], end_time=[2020]),
            2: dict(drawType=5, gid=4, begin_time=[2019], end_time=[2020], fix_rate=1),
            3: dict(drawType=5, gid=3, begin_time=[2021], end_time=[2022]),
            4: dict(drawType=6, gid=3, begin_time=[2019], end_time=[2020])}
        calls = []
        getter = archive.make_archive_wish_group_getter(
            lambda owner, wire, fixed: calls.append((wire, fixed)) or {'original': []}, table)
        archive._f7_archive_session = {'wire_t': 5, 'wish_id': 1}
        self.assertEqual(getter(None, 5), {3: [1], 4: [2]})
        self.assertEqual(getter(None, 5, exlude_fixed=True), {3: [1]})
        self.assertEqual(getter(None, 6), {'original': []})
        archive.offline_archive_clear()
        self.assertEqual(getter(None, 5, True), {'original': []})
        self.assertEqual(calls, [(6, False), (5, True)])


if __name__ == '__main__':
    unittest.main()
