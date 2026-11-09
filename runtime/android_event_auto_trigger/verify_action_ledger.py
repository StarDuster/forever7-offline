# -*- coding: utf-8 -*-
"""Minimal representative host for the offline code20 action ledger.

Exercises the same transaction shape as LocalProxy: observe story.city_values.av
before/after an accepted action, record the committed delta with a stable
receipt id, persist the whole document atomically, and roll back the in-memory
state on failure.  Also covers reload, duplicate/retry, invalid and old saves.
This is a static host check; it is not device or original-server proof.
"""
import copy
import json
import os
import sys
import tempfile
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, 'runtime'))
sys.path.insert(0, os.path.join(ROOT, 'tools'))
from export_game_catalogs import decode
from offline_action_ledger import (ACTION_LEDGER_POLICY, action_spent_since_event,
    initial_action_ledger, record_committed_spend, set_event_baseline)
from offline_conditions import evaluate_offline_condition as cond
from offline_store import OfflineSaveStore
from offline_week import prepare_week_result, prepare_week_transition


def seed_state(week=3, completed=()):
    return {'scenario': 'opening-development-v1', 'player_name': 'ledger-host',
            'story': {'version': 1, 'week': week, 'date': 2, 'route': '5',
                      'city_values': {'av': 24}},
            'day': {'stock_day': 1}, 'completed_events': list(completed),
            'processing_events': [], 'conditions': [], 'profile': {'heroes': {}},
            'gacha': {}, 'gacha_pools': {}, 'battle': {}, 'city_actions': {},
            'week_protocol': {}, 'status': 'city', 'available_events': [],
            'event_traces': []}


def week_owner_state():
    """State accepted by the real offline_week owner, not a synthetic week."""
    fixture = json.loads(open(os.path.join(ROOT, 'tests', 'fixtures',
                                           'offline_week_cdata.json')).read())
    tables = decode(fixture['tables'])
    state = {'story': {'version': 1, 'week': 0, 'date': 7, 'route': '1',
             'sub_routes': [1], 'emergency': False, 'cg': [11], 'endings': [2],
             'notes': {'p': {}, 'n': {}, 'pn': [123], 'ppn': False},
             'battle_wins': [101, 1101], 'blackcores': {'2': 1},
             'pending_effects': {},
             'city_values': {'av': 0, 'bf': 300, 'rv': 20, 'dv': 10, 'fv': 30},
             'city_areas': {'1': {'id': 1, 'lv': 3, 'st': [0, False, False], 'bd': {}}}},
             'profile': {'heroes': {'24': {'sl': 3, 'so': 2, 'cf': 10, 'ef': 75,
                 'cs': 'a' * 24, 'sk': {'a' * 24: {'u': 'a' * 24, 'i': 24}},
                 'ti': {'items': [{'u': 'b' * 24}]}, 'as': 2}},
                 'economy': {'version': 1, 'money': 12345, 'exp': 300, 'level': 7},
                 'treasures': {'version': 1, 'items': [{'u': 'b' * 24, 'i': 1002}]}},
             'gacha': {'opened_total': 99, 'items': [{'u': 'c' * 24, 'i': 1003}],
                       'group': {'cards': [1, 2]}},
             'completed_events': [8029], 'processing_events': [], 'available_events': [],
             'conditions': [[102, 4]], 'event_traces': [[8029, [['dialog', [8029]]]]],
             'battle': {'version': 1, 'active': None, 'receipts': []},
             'day': {'version': 1, 'stock_day': 7, 'intent': None, 'receipt': None,
                     'review': None},
             'status': 'city', 'player_name': 'host-name'}
    handoff = {'kind': 'week_result', 'event': 8029, 'result': 1,
               'token': 'ending:8029', 'in_advance': False}
    return state, tables, handoff


def check_week_owner_ledger():
    state, tables, handoff = week_owner_state()
    record_committed_spend(state, 5, 'city:old')
    set_event_baseline(state, 8029, 0)
    earned = prepare_week_result(state, handoff, tables['events'], tables['endings'])[0]
    transitioned, unused, changed = prepare_week_transition(
        earned, 'handleIncWeekAsk', 'ledger:week', tables)
    check(changed, 'real week transition changed')
    ledger = transitioned['story']['action_ledger']
    check(ledger['generation'] == 2, 'week owner advances generation')
    check(ledger['spent'] == 5, 'week owner preserves committed spend')
    check(ledger['baselines'] == {}, 'week owner drops prior-generation baselines')
    check(ledger['receipts'] == [], 'week owner resets bounded receipts')
    check(action_spent_since_event(transitioned, 8029) is None,
          'prior-generation baseline is unknown after the real week owner')
    check(set_event_baseline(transitioned, 510, 1), 'new-generation baseline')
    check(ledger['baselines']['510']['generation'] == 2, 'new baseline generation')
    record_committed_spend(transitioned, 2, 'city:new')
    check(action_spent_since_event(transitioned, 510) == 2,
          'new-generation delta counts only new actions')
    # No ledger in the source save must stay absent, never a fresh zero.
    missing, tables, handoff = week_owner_state()
    transitioned, unused, changed = prepare_week_transition(
        prepare_week_result(missing, handoff, tables['events'], tables['endings'])[0],
        'handleIncWeekAsk', 'ledger:none', tables)
    check('action_ledger' not in transitioned['story'],
          'week owner never synthesizes a ledger')


class Host(object):
    """Single-writer host with one atomic progress document."""

    def __init__(self, path, state):
        self.store = OfflineSaveStore(path, validate=lambda payload: None)
        self.state = copy.deepcopy(state)
        self.fail_write = False
        self.store.write(self.state)

    def _commit(self, candidate):
        previous = self.state
        if self.fail_write:
            self.state = previous
            return False
        try:
            self.store.write(candidate)
        except Exception:
            self.state = previous
            return False
        self.state = candidate
        return True

    def action(self, cost, receipt_id):
        previous = copy.deepcopy(self.state)
        candidate = copy.deepcopy(previous)
        old = candidate['story']['city_values']['av']
        candidate['story']['city_values']['av'] = old - cost
        spent = old - candidate['story']['city_values']['av']
        if spent > 0:
            record_committed_spend(candidate, spent, receipt_id)
        return self._commit(candidate)

    def complete(self, event):
        candidate = copy.deepcopy(self.state)
        if event not in candidate['completed_events']:
            candidate['completed_events'].append(event)
        set_event_baseline(candidate, event, candidate['story']['week'])
        return self._commit(candidate)


def check(condition, message):
    if not condition:
        raise AssertionError(message)


def reload_host(path):
    host = Host.__new__(Host)
    host.store = OfflineSaveStore(path, validate=lambda payload: None)
    host.state = host.store.load()
    host.fail_write = False
    return host


def main():
    folder = tempfile.mkdtemp(prefix='p7-action-ledger-')
    path = os.path.join(folder, 'progress.json')
    try:
        host = Host(path, seed_state())
        check(cond(20, '{510:1}', host.state) is False,
              'incomplete event is known false, not a ledger fact')

        check(host.complete(510), 'completion save')
        check(action_spent_since_event(host.state, 510) == 0, 'baseline starts at zero')
        check(host.action(2, 'city:alpha'), 'first accepted action')
        check(action_spent_since_event(host.state, 510) == 2, 'two committed points')
        check(cond(20, '{510:2}', host.state) is True, 'exact threshold passes')
        check(cond(20, '{510:3}', host.state) is False, 'higher threshold fails')

        # A failed store write leaves no trace in memory or on disk.
        host.fail_write = True
        check(not host.action(2, 'city:beta'), 'save failure is reported')
        host.fail_write = False
        check(action_spent_since_event(host.state, 510) == 2, 'failed action not counted')
        reloaded = reload_host(path)
        check(action_spent_since_event(reloaded.state, 510) == 2, 'failure rolled back on disk')

        # Retry of the same accepted operation: av is unchanged, so the host
        # records nothing.  A duplicate receipt id is a second guard.
        before = copy.deepcopy(reloaded.state)
        check(host.action(0, 'city:alpha'), 'retry stays a successful no-op')
        check(host.state['story']['city_values']['av'] == before['story']['city_values']['av'],
              'retry did not charge twice')
        check(action_spent_since_event(host.state, 510) == 2, 'retry not counted')
        candidate = copy.deepcopy(host.state)
        check(record_committed_spend(candidate, 2, 'city:alpha') is False,
              'duplicate receipt is rejected')
        check(action_spent_since_event(candidate, 510) == 2, 'duplicate not counted')

        # Reload from disk preserves both the total and the completion baseline.
        host.action(3, 'battle:one')
        check(host.action(1, 'city:gamma'), 'third accepted action')
        check(action_spent_since_event(host.state, 510) == 6, 'six committed points')
        reloaded = reload_host(path)
        check(action_spent_since_event(reloaded.state, 510) == 6, 'reload preserves the fact')
        check(cond(20, '{510:6}', reloaded.state) is True, 'reloaded predicate passes')

        # A real repeat completion moves the baseline; later actions count from it.
        check(reloaded.complete(510), 'repeat completion save')
        check(action_spent_since_event(reloaded.state, 510) == 0, 'repeat baseline resets')
        check(reloaded.action(1, 'city:delta'), 'action after repeat completion')
        check(action_spent_since_event(reloaded.state, 510) == 1, 'delta after repeat baseline')

        # Cross-week proof uses the real offline_week owner, which rebuilds the
        # story document and resets the action budget.  It preserves committed
        # spend, advances the ledger generation and drops stale baselines.
        check_week_owner_ledger()

        # Old save: completed event but no ledger and no baseline -> unknown.
        old = seed_state(completed=[510])
        old_path = os.path.join(folder, 'old.json')
        old_store = OfflineSaveStore(old_path, validate=lambda payload: None)
        old_store.write(old)
        old_state = OfflineSaveStore(old_path, validate=lambda payload: None).load()
        check(action_spent_since_event(old_state, 510) is None, 'old save is unknown')
        check(cond(20, '{510:0}', old_state) is None, 'old save never becomes zero/success')

        # Legacy same-week evidence remains supported; no ledger is required.
        legacy = seed_state(completed=[510])
        legacy['story'].update(week_actions_spent=12, event_action_baselines={'510': 4},
                               event_days={'510': {'week': 3, 'day': 1}})
        check(action_spent_since_event(legacy, 510) == 8, 'legacy same-week baseline')
        legacy['story']['event_days']['510']['week'] = 2
        check(action_spent_since_event(legacy, 510) is None, 'legacy other-week is unknown')
        check(cond(20, '{510:0}', legacy) is None, 'legacy other-week never false/zero')
        legacy['story']['week_actions_spent'] = 2
        legacy['story']['event_days']['510']['week'] = 3
        check(action_spent_since_event(legacy, 510) is None,
              'legacy baseline above total is unknown')

        # Invalid ledger: stays untouched, every fact is unknown, actions still work.
        broken = seed_state(completed=[510])
        broken['story']['action_ledger'] = initial_action_ledger()
        broken['story']['action_ledger']['spent'] = '7'
        broken_path = os.path.join(folder, 'broken.json')
        broken_host = Host(broken_path, broken)
        check(broken_host.action(1, 'city:broken'), 'invalid ledger does not block actions')
        check(broken_host.state['story']['action_ledger']['spent'] == '7',
              'invalid ledger is not overwritten')
        check(action_spent_since_event(broken_host.state, 510) is None,
              'invalid ledger is unknown')
        check(cond(20, '{510:0}', broken_host.state) is None,
              'invalid ledger never becomes zero/success')

        counts = {'policy': ACTION_LEDGER_POLICY, 'conditions_checked': 7}
        print('PASS action ledger host: %(policy)s checks=%(conditions_checked)d '
              'commit/failure/retry/duplicate/reload/old-save/invalid-ledger' % counts)
    finally:
        for name in os.listdir(folder):
            try:
                os.unlink(os.path.join(folder, name))
            except OSError:
                pass
        os.rmdir(folder)


if __name__ == '__main__':
    main()
