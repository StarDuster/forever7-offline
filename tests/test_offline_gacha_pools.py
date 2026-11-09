import copy
import json
from pathlib import Path
import sys
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'runtime'))
from offline_gacha import prepare_gacha_group
from offline_gacha_pools import *

class ConfiguredPoolTransactions(unittest.TestCase):
    def setUp(self):
        self.ids = iter('%024x' % i for i in range(1, 10000))
        self.initial = {'slots': 6, 'cap': 18, 'guarantee_at': 12, 'require_complete': True}
        self.friend = {'mode': 'direct', 'slots': 1, 'daily_cap': 100, 'batch_sizes': [1, 10]}
        self.calls = []
    def make_id(self):
        return next(self.ids)
    def resolve(self, wire, ordinal, force):
        self.calls.append((wire, ordinal, force))
        # Mixed original-client shapes: no all-whole-hero simplification.
        if ordinal % 3 == 0:
            return {'hero': [12], 'get_hero': False, 'hero_file': 0, 'hero_frag': {'4253': 2}, 'rank': 4 if force else 2}
        if ordinal % 3 == 1:
            return {'hero': [], 'hero_frag': {'24': 3}, 'treasure': [], 'rank': 0}
        return {'hero': [], 'hero_frag': {}, 'treasure': [{'i': 1003, 'u': 'original-equipment-id'}], 'rank': 0}
    def open(self, state, t, indices):
        return open_pool_cards(state, t, indices, self.make_id, lambda item: 5)
    def test_legacy_normal_migration_exact_fixed_results_inventory_and_idempotency(self):
        old, _ = prepare_gacha_group(None, [24], lambda n: 0, lambda h: {'4253': 2})
        state = new_gacha_pools_state(old)
        self.assertEqual(state['pools']['1'], old)
        same, changed = prepare_pool(state, 1, {'slots': 6}, lambda *a: self.fail('Reroll'))
        self.assertTrue(changed)  # records config without changing old cards
        self.assertEqual(same['pools']['1']['group'], old['group'])
        replay, changed = prepare_pool(same, 1, {'slots': 6}, lambda *a: self.fail('Reroll'))
        self.assertFalse(changed)
        self.assertEqual(replay, same)
    def test_wire354_is_isolated_from_pooltype1_and_hidden_until_open(self):
        state, _ = prepare_pool(None, 354, self.initial, self.resolve, lambda c: c['rank'] == 4)
        self.assertEqual(pool_opened_total(state, 1), 0)
        self.assertEqual(set(state['pools']), {'1', '354'})
        self.assertEqual(pool_file_view(state, 354), {str(i): {'index': i, 'is_open': False} for i in range(6)})
        fixed = json.loads(json.dumps(state))
        replay, changed = prepare_pool(fixed, 354, self.initial, lambda *a: self.fail('Reroll'))
        self.assertFalse(changed)
        self.assertEqual(replay, fixed)
    def test_mixed_rewards_and_same_slot_retry_no_double_item_or_equipment(self):
        state, _ = prepare_pool(None, 2, {'slots': 3}, self.resolve)
        after, cards, granted, changed = self.open(state, 2, [0, 1, 2])
        self.assertTrue(changed)
        self.assertEqual(len(granted), 3)
        self.assertEqual(cards[1]['treasure'], [{'i': 1003, 'u': 'original-equipment-id'}])
        retry, repeats, new, changed = self.open(json.loads(json.dumps(after)), 2, [1, 0])
        self.assertFalse(changed)
        self.assertEqual(new, [])
        self.assertEqual(retry, after)
        self.assertEqual(sum(x['w'] for x in pool_items(retry)), 5)
        self.assertEqual(repeats[0], cards[1])
    def test_initial12_s_and18_cap_use_resolver_ordinals_no_partial_group_retirement(self):
        state = None
        for group in range(3):
            state, _ = prepare_pool(state, 354, self.initial, self.resolve, lambda c: c['rank'] == 4)
            with self.assertRaises(ValueError): quit_pool(state, 354)
            state, _, _, _ = self.open(state, 354, [5, 4, 3, 2, 1, 0])
            state, _ = quit_pool(state, 354)
        self.assertIn((354, 12, True), self.calls)
        self.assertEqual(pool_opened_total(state, 354), 18)
        self.assertEqual(pool_opened_total(state, 1), 0)
        with self.assertRaises(ValueError): prepare_pool(state, 354, self.initial, self.resolve)
    def test_unsatisfied_guarantee_fails_without_mutating_source(self):
        state, _ = prepare_pool(None, 354, self.initial, self.resolve, lambda c: c['rank'] == 4)
        state, _, _, _ = self.open(state, 354, range(6));state, _ = quit_pool(state, 354)
        before = copy.deepcopy(state)
        with self.assertRaises(ValueError): prepare_pool(state, 354, self.initial, lambda *a: {'rank': 1}, lambda c: c['rank'] == 4)
        self.assertEqual(state, before)
    def test_friend_daily_limit_independent_newfriend_and_operation_replay(self):
        state, result, grants, changed = direct_pool_draw(None, 99, self.friend, 10, 'day0:1', '0', self.resolve, self.make_id, lambda i: 5)
        again, repeated, grants, changed = direct_pool_draw(state, 99, self.friend, 10, 'day0:1', '0', lambda *a: self.fail('Reroll'), self.make_id, lambda i: 5)
        self.assertEqual(again, state);self.assertEqual(repeated, result);self.assertEqual(grants, []);self.assertFalse(changed)
        for i in range(2, 11): state, _, _, _ = direct_pool_draw(state, 99, self.friend, 10, 'day0:%d' % i, '0', self.resolve, self.make_id, lambda i: 5)
        with self.assertRaises(ValueError): direct_pool_draw(state, 99, self.friend, 1, 'overflow', '0', self.resolve, self.make_id, lambda i: 5)
        state, _, _, _ = direct_pool_draw(state, 131, self.friend, 1, 'newfriend1', '0', self.resolve, self.make_id, lambda i: 5)
        self.assertEqual(pool_opened_total(state, 99), 100);self.assertEqual(pool_opened_total(state, 131), 1)
        state, _, _, _ = direct_pool_draw(state, 99, self.friend, 1, 'day1:1', '1', self.resolve, self.make_id, lambda i: 5)
        self.assertEqual(state['pools']['99']['daily_count'], 1)
    def test_lazy_reveal_actual_ordinal_shared_counter_and_replay_do_not_allocate_rewards(self):
        config={'slots':3,'lazy':True}
        state,_=prepare_pool(None,7,config,lambda *a:self.fail('Must not resolve at preparation'),seed_factory=lambda:'fixed7')
        state,_=prepare_pool(state,8,config,lambda *a:self.fail('Must not resolve at preparation'),seed_factory=lambda:'fixed8')
        calls=[]
        def reveal(t,n,force,seed,transaction):
            counters=transaction.setdefault('inc_up_cnt',{})
            before=counters.get('shared',0);counters['shared']=before+1
            calls.append((t,n,seed,before))
            return {'hero_frag':{},'item':[[1,1]]}
        state,_,_,_=open_pool_cards(state,7,[2],self.make_id,lambda i:5,credit_items=False,resolver=reveal)
        state,_,_,_=open_pool_cards(state,8,[1],self.make_id,lambda i:5,credit_items=False,resolver=reveal)
        state,_,_,_=open_pool_cards(state,7,[0],self.make_id,lambda i:5,credit_items=False,resolver=reveal)
        saved=copy.deepcopy(state)
        state,_,new,changed=open_pool_cards(state,7,[2],self.make_id,lambda i:5,credit_items=False,resolver=lambda *a:self.fail('Replay must not resolve'))
        self.assertEqual(calls,[(7,1,'fixed7',0),(8,1,'fixed8',1),(7,2,'fixed7',2)])
        self.assertEqual(state,saved);self.assertFalse(changed);self.assertEqual(new,[])

    def test_canonical_inventory_adapter_disables_internal_credit_without_losing_grants(self):
        state, _ = prepare_pool(None, 354, self.initial, self.resolve, lambda c: c['rank'] == 4)
        state, cards, newly, changed = open_pool_cards(state, 354, [0], lambda: self.fail('Canonical owner allocates IDs'), lambda i: self.fail('Canonical owner chooses stack limits'), credit_items=False)
        self.assertTrue(changed);self.assertEqual(newly[0]['hero_frag'], {'24': 3});self.assertEqual(pool_items(state), [])
        state, cards, newly, changed = open_pool_cards(state, 354, [0], self.make_id, lambda i: 5, credit_items=False)
        self.assertFalse(changed);self.assertEqual(newly, [])
        direct, cards, newly, changed = direct_pool_draw(None, 99, self.friend, 1, 'operation1', '0', self.resolve, self.make_id, lambda i: 5, credit_items=False)
        self.assertEqual(pool_items(direct), []);self.assertEqual(newly[0]['hero_frag'], {'24': 3})

    def test_retired_direct_receipt_never_rewards_again_and_no_implicit_furniture_cap(self):
        config = {'mode': 'direct', 'slots': 1, 'batch_sizes': [1]}
        state = None
        for i in range(130):
            state, _, _, _ = direct_pool_draw(state, 700, config, 1, 'operation%d' % i, '0', lambda *a: {'hero_frag': {}}, self.make_id, lambda i: 5)
        self.assertEqual(pool_opened_total(state, 700), 130)
        with self.assertRaises(ValueError):
            direct_pool_draw(state, 700, config, 1, 'operation0', '1', lambda *a: self.fail('Retired replay sampled'), self.make_id, lambda i: 5)

    def test_cross_pool_inventory_uuid_collision_and_invalid_index_roll_back(self):
        state, _ = prepare_pool(None, 2, {'slots': 1}, self.resolve)
        state, _, _, _ = self.open(state, 2, [0])
        state, _ = prepare_pool(state, 3, {'slots': 1}, self.resolve)
        before = copy.deepcopy(state)
        uid=pool_items(state)[0]['u']
        with self.assertRaises(ValueError):open_pool_cards(state, 3, [0], lambda: uid, lambda i: 5)
        for indices in ([True], [-1], [1], [0,0], []):
            with self.assertRaises(ValueError):self.open(state, 3, indices)
        self.assertEqual(state, before)

if __name__ == '__main__': unittest.main()
