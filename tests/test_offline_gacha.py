import copy
import json
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'runtime'))
from offline_gacha import (new_gacha_state, prepare_gacha_group, open_gacha_cards,
                           gacha_file_view, quit_gacha_group, validate_gacha_state)
from offline_store import OfflineSaveStore
from tempfile import TemporaryDirectory


class GachaTransactionTests(unittest.TestCase):
    def setUp(self):
        self.ids = iter('%024x' % i for i in range(1, 500))
        self.group, changed = prepare_gacha_group(None, [24, 20], lambda n: 0,
                                                   lambda hero: {4253: 3, 24: 7})
        self.assertTrue(changed)

    def test_fixed_six_results_resume_without_reroll_or_hidden_result_leak(self):
        same, changed = prepare_gacha_group(json.loads(json.dumps(self.group)), [20, 24],
                                            lambda n: self.fail('Must not reroll'), lambda h: {})
        self.assertFalse(changed)
        self.assertEqual(same, self.group)
        self.assertEqual(gacha_file_view(same), {str(i): {'index': i, 'is_open': False} for i in range(6)})

    def test_retry_same_slot_and_open_all_only_credit_once_with_real_stack_limits(self):
        opened, first, changed = open_gacha_cards(self.group, [2], lambda: next(self.ids), lambda i: 5)
        self.assertTrue(changed)
        self.assertEqual(self.group['opened_total'], 0)
        replay, second, changed = open_gacha_cards(opened, [2], lambda: self.fail('No new instance'), lambda i: 5)
        self.assertFalse(changed)
        self.assertEqual(first, second)
        self.assertEqual(opened, replay)
        all_opened, _, _ = open_gacha_cards(replay, range(6), lambda: next(self.ids), lambda i: 5)
        self.assertEqual(all_opened['opened_total'], 6)
        self.assertEqual(sum(x['w'] for x in all_opened['items'] if x['i'] == 4253), 18)
        self.assertEqual(sum(x['w'] for x in all_opened['items'] if x['i'] == 24), 42)
        self.assertTrue(all(x['w'] <= 5 for x in all_opened['items']))
        self.assertTrue(all(not x['get_hero'] for x in all_opened['group']['cards']))

    def test_failed_store_commit_preserves_previous_group_without_reward(self):
        with TemporaryDirectory() as folder:
            store = OfflineSaveStore(str(Path(folder) / 'save.json'), validate_gacha_state)
            store.write(self.group)
            candidate, _, _ = open_gacha_cards(self.group, [0], lambda: next(self.ids), lambda i: 99)
            candidate['items'][0]['w'] = -1
            with self.assertRaises(ValueError):
                store.write(candidate)
            self.assertEqual(store.load(), self.group)

    def test_quit_archives_open_flags_without_awarding_unopened_cards(self):
        opened, _, _ = open_gacha_cards(self.group, [0], lambda: next(self.ids), lambda i: 99)
        closed, changed = quit_gacha_group(opened)
        self.assertTrue(changed)
        self.assertEqual(closed['opened_total'], 1)
        self.assertEqual(closed['items'], opened['items'])
        self.assertEqual(closed['history'][0], opened['group'])
        next_group, _ = prepare_gacha_group(closed, [24], lambda n: 0, lambda hero: {})
        self.assertEqual(next_group['group']['id'], 2)

    def test_batch_reply_has_mutable_empty_activity_treasure_list_for_stock_settlement(self):
        saved, replies, _ = open_gacha_cards(self.group, range(6), lambda: next(self.ids), lambda i: 99)
        for result in replies:
            treasure = result['other_reward']['activityReward']['treasure']
            treasure.extend([])
            self.assertEqual(treasure, [])
        # Older persisted cards are adapted as well, without changing outcomes.
        restored, replay, changed = open_gacha_cards(json.loads(json.dumps(saved)), [0],
                                                   lambda: self.fail('No new grant'), lambda i: 99)
        self.assertFalse(changed)
        self.assertEqual(replay[0], replies[0])

    def test_invalid_indices_or_duplicate_instance_fail_without_modifying_input(self):
        before = copy.deepcopy(self.group)
        for invalid in ([6], [-1], [True], [0, 0]):
            with self.assertRaises(ValueError):
                open_gacha_cards(self.group, invalid, lambda: next(self.ids), lambda i: 99)
        with self.assertRaises(ValueError):
            open_gacha_cards(self.group, [0], lambda: '0' * 24, lambda i: 1)
        self.assertEqual(self.group, before)


if __name__ == '__main__':
    unittest.main()

class VisibleSimulationPoolTests(unittest.TestCase):
    def test_original_visible_pool_is_138_and_saved_group_is_never_rerolled(self):
        import sys
        from pathlib import Path
        from offline_gacha import visible_simulation_heroes, prepare_gacha_group
        root = Path(__file__).resolve().parents[1]
        sys.path.insert(0, str(root / 'analysis/research-agent'))
        from read_literal_marshal import read
        catalog = read(root / 'analysis/android640-scripts/com/data/cdata/hero.marshal')
        profile = {'heroes': {str(hero): {} for hero in catalog}}
        pool = visible_simulation_heroes(profile, catalog)
        self.assertEqual(len(profile['heroes']), 140)
        self.assertEqual(len(pool), 138)
        self.assertNotIn(46, pool)
        self.assertNotIn(125, pool)
        original, _ = prepare_gacha_group(None, [46], lambda size: 0, lambda hero: {4253: 1})
        replay, changed = prepare_gacha_group(original, pool, lambda size: self.fail('must not sample again'), lambda hero: self.fail('must not convert again'))
        self.assertFalse(changed)
        self.assertEqual(replay, original)
        self.assertEqual(original['group']['cards'][0]['hero'], [46])
