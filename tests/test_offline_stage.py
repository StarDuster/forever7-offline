"""Host contracts with synthetic result inputs, never native win verification."""
import copy
import hashlib
import json
from pathlib import Path
import sys
import subprocess
import unittest
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'runtime'))
from offline_stage import (prepare_stage_admission, prepare_stage_finish,
    original_stage_cost, original_stage_levels, basic_city_stage_chain,
    validate_stage_battle_state)


class NormalStageTests(unittest.TestCase):
    def setUp(self):
        self.fixture = json.loads((ROOT / 'tests/fixtures/offline_stage_cdata.json').read_text())
        self.missions = {int(k): v for k, v in self.fixture['missions'].items()}
        self.city = {int(k): v for k, v in self.fixture['city_data'].items()}
        self.state = {'story': {'week': 0, 'date': 0, 'emergency': False,
                               'city_values': {'av': 24, 'fv': 50, 'rv': 5, 'dv': 5, 'bf': 0},
                               'city_areas': {'1': {'id': 1, 'lv': 1, 'bd': {}, 'st': [0, False, False],
                                                    'stage': {'cs': 0, 'sl': [[101]]}},
                                              '2': {'id': 2, 'lv': 1, 'bd': {}, 'st': [1, False, False],
                                                    'stage': {'cs': 1101, 'sl': [[1101]]}}},
                               'battle_wins': [101]},
                      'profile': {'economy': {'version': 1, 'level': 1, 'exp': 0, 'money': 10000},
                                  'heroes': {'24': {'cf': 100, 'ef': 0, 'sk': {'skin': {'i': 24}}}},
                                  'treasures': {'items': []}},
                      'completed_events': [8], 'day': {'stock_day': 0},
                      'battle': {'version': 1, 'active': None, 'receipts': []}}
        self.request = {'t': 1, 's': 1101, 'h': [24], 'd': {'a': 2}}
        self.counter = 0

    def admit(self, state=None, request=None):
        self.counter += 1
        return prepare_stage_admission(state or self.state, request or self.request,
                                       self.missions, lambda: 'fight-%s' % self.counter)

    def reward(self, active, result):
        # Deliberately a tiny fixture settler. Real catalog reward integration is
        # tested separately below against the existing original reward engine.
        reply = {k: copy.deepcopy(result[k]) for k in ('t', 's', 'h', 'x', 'w')}
        reply['r'] = {} if not result['w'] else {'money': 1, 'stage': 101}
        profile = copy.deepcopy(self.state['profile'])
        if result['w']:
            profile['economy']['money'] += 1
        return reply, {'profile': profile, 'notices': [], 'granted': []}

    def finish(self, state, win=1, settle=None, source=None):
        active = state['battle']['active']
        result = dict(active['request'], x=[], w=win, e={})
        result.pop('d')
        return prepare_stage_finish(state, result, self.missions, self.city,
                                    settle or self.reward, source or active['fight_id'])

    def test_original_fixture_hashes_and_all_ordinary_chains(self):
        for name, digest in self.fixture['sha256'].items():
            path = ROOT / ('analysis/android640-scripts/com/data/cdata/' + name + '.marshal')
            self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), digest)
        for area in range(1, 9):
            chain = basic_city_stage_chain(area, self.state, self.missions)
            self.assertEqual(len(chain), 1 if area == 1 else 6)
            for scene, successor in zip(chain, chain[1:]):
                self.assertIn(successor, self.missions[scene]['nextstagenums'])

    def test_area2_admission_reserves_real_cost_without_spending_or_winning(self):
        before = copy.deepcopy(self.state)
        candidate, changed = self.admit()
        self.assertTrue(changed)
        active = candidate['battle']['active']
        self.assertEqual(active['costs'], {'actions': 2, 'fatigue': 5})
        self.assertEqual((active['hero_level'], active['monster_level']), (1, 1))
        self.assertEqual(candidate['profile'], before['profile'])
        self.assertEqual(candidate['story'], before['story'])
        self.assertEqual(self.state, before)
        repeated, changed = self.admit(candidate)
        self.assertFalse(changed)
        self.assertEqual(repeated, candidate)

    def test_stage_skip_wrong_area_locked_team_and_special_modes_rejected(self):
        for mutation in ('skip', 'ch', 'locked', 'unowned', 'action', 'fatigue', 'mode', 'weekend', 'special'):
            self.setUp()
            if mutation == 'skip':
                self.state['story']['city_areas']['2']['stage']['sl'].append([1102])
                self.request['s'] = 1102
            if mutation == 'ch': self.request['d']['a'] = 1
            if mutation == 'locked': self.state['story']['city_areas']['2']['st'][2] = True
            if mutation == 'unowned': self.request['h'] = [999]
            if mutation == 'action': self.state['story']['city_values']['av'] = 1
            if mutation == 'fatigue': self.state['profile']['heroes']['24']['cf'] = 4
            if mutation == 'mode': self.request['t'] = 2
            if mutation == 'weekend': self.state['day']['stock_day'] = 7
            if mutation == 'special': self.missions[1101]['system_type'] = 999
            with self.assertRaises(ValueError, msg=mutation): self.admit()

    def test_actual_loss_preserves_costs_city_and_roster_and_replay(self):
        candidate, _ = self.admit()
        done, reply, effects, changed = self.finish(candidate, 0)
        self.assertTrue(changed)
        self.assertEqual(reply['w'], 0)
        self.assertEqual(reply['r'], {})
        self.assertEqual(done['story'], self.state['story'])
        self.assertEqual(done['profile'], self.state['profile'])
        self.assertIsNone(done['battle']['active'])
        result = {'t': 1, 's': 1101, 'h': [24], 'x': [], 'w': 0, 'e': {}}
        replay = prepare_stage_finish(done, result, self.missions, self.city,
                                     lambda *args: self.fail('duplicate cannot settle'), candidate['battle']['active']['fight_id'])
        self.assertFalse(replay[3])
        self.assertEqual(replay[1], reply)

    def test_real_result_win_charges_once_advances_only_area2_and_cannot_skip(self):
        candidate, _ = self.admit()
        done, reply, effects, changed = self.finish(candidate)
        self.assertEqual(done['story']['city_values']['av'], 22)
        self.assertEqual(done['profile']['heroes']['24']['cf'], 95)
        self.assertEqual(done['story']['city_areas']['2']['stage']['cs'], 1102)
        self.assertEqual(done['story']['city_areas']['2']['st'][0], 1)
        self.assertEqual(sorted(done['story']['city_areas']), ['1', '2'])
        self.assertEqual(done['story']['battle_wins'], [101, 1101])
        self.assertEqual(reply['r']['stage'], 1101)
        self.assertEqual(effects['notices'][-1][0], 'get_all_area_info_reply')
        self.assertIn('area_2', effects['notices'][-1][1]['ais'])
        self.assertEqual(candidate['profile']['heroes']['24']['cf'], 100)
        with self.assertRaises(ValueError): self.admit(done, dict(self.request, s=1103))
        self.admit(done, dict(self.request, s=1102))

    def test_forged_source_or_forged_win_settler_never_mutates_state(self):
        candidate, _ = self.admit()
        before = copy.deepcopy(candidate)
        with self.assertRaises(ValueError): self.finish(candidate, source='old-fight')
        def forge(active, result):
            reply, effects = self.reward(active, dict(result, w=1))
            return reply, effects
        with self.assertRaises(ValueError): self.finish(candidate, 0, forge)
        self.assertEqual(candidate, before)

    def test_force_penalty_and_original_later_week_levels(self):
        self.assertEqual(original_stage_cost(self.missions[2101], 0), {'actions': 2, 'fatigue': 25})
        self.assertEqual(original_stage_cost(self.missions[2101], 10), {'actions': 2, 'fatigue': 5})
        self.assertEqual(original_stage_levels(self.missions[1101], 1, 20), (20, 26))
        self.assertEqual(original_stage_levels(dict(self.missions[1101], adjust_hero_lv=7, adjust_monster_lv=9), 0, 20), (7, 9))

    def test_school_branch_is_real_event_condition_not_all_branch_unlock(self):
        self.state['completed_events'].append(20007)
        chain = basic_city_stage_chain(2, self.state, self.missions)
        self.assertEqual(chain[-1], 1107)
        self.assertNotIn(1106, chain)
        self.state['story']['battle_wins'] += [1101, 1102, 1103, 1104]
        self.state['story']['city_areas']['2']['stage'] = {'cs': 1105, 'sl': [[1105]]}
        admitted, _ = self.admit(request=dict(self.request, s=1105))
        done, _, _, _ = self.finish(admitted)
        self.assertEqual(done['story']['city_areas']['2']['stage']['cs'], 1107)
        self.state = done
        admitted, _ = self.admit(request=dict(self.request, s=1107))
        done, _, _, _ = self.finish(admitted)
        self.assertEqual(done['story']['city_areas']['2']['st'][0], 0)
        self.assertIn(1107, done['story']['battle_wins'])
        self.assertNotIn(1106, done['story']['battle_wins'])

    def test_complete_school_unlocks_only_required_next_areas(self):
        self.state['story']['city_areas']['2']['stage'] = {'cs': 1106, 'sl': [[1106]]}
        self.state['story']['battle_wins'] += [1101, 1102, 1103, 1104, 1105]
        self.request['s'] = 1106
        admitted, _ = self.admit()
        done, reply, effects, changed = self.finish(admitted)
        areas = done['story']['city_areas']
        self.assertEqual(areas['2']['st'][0], 0)
        self.assertEqual(areas['3']['stage']['cs'], 2101)
        self.assertEqual(areas['4']['stage']['cs'], 3101)
        self.assertNotIn('5', areas)
        self.assertNotIn('8', areas)

    def test_real_catalog_base_reward_engine_integrates_with_area2_transaction(self):
        from offline_battle import settle_first_battle_economy
        self.counter = 10  # deterministic native identity fixture
        state, _ = self.admit()
        pool = self.fixture['reward_pool304']
        weights = pool['weights']
        # Pin a real no-drop outcome from the unchanged original weight pool.
        for number in range(100):
            fight_id = 'stage-real-pool-%s' % number
            seed = ('first-battle-drop-v1:%s:304:0' % fight_id).encode('ascii')
            roll = int(hashlib.sha256(seed).hexdigest(), 16) % sum(w for _, w in weights)
            for reward_id, weight in weights:
                if roll < weight: break
                roll -= weight
            if reward_id == 0: break
        self.assertEqual(reward_id, 0)
        state['battle']['active']['fight_id'] = fight_id
        def settle(active, actual):
            return settle_first_battle_economy(self.state['profile'], active, actual,
                {1: self.fixture['fight_reward_level1']},
                {int(k): v for k, v in self.fixture['player_exp'].items()},
                {304: pool}, {}, lambda *args: self.fail('pinned real no-drop outcome'))
        done, reply, effects, changed = self.finish(state, settle=settle)
        self.assertEqual(reply['r']['money'], 3267)
        self.assertEqual(reply['r']['exp'], 2000)
        self.assertEqual(reply['r']['stage'], 1101)
        self.assertEqual(done['profile']['economy']['money'], 13267)
        self.assertEqual(done['profile']['economy']['level'], 2)
        self.assertEqual(done['profile']['heroes']['24']['ef'], 1)
        self.assertEqual(done['profile']['heroes']['24']['cf'], 95)

    def test_restarted_active_admission_preserves_cost_and_failed_save_publishes_nothing(self):
        admitted, _ = self.admit()
        restarted = json.loads(json.dumps(admitted))
        before = copy.deepcopy(restarted)
        prepared, reply, effects, changed = self.finish(restarted)
        self.assertEqual(restarted, before)
        self.assertEqual(prepared['story']['city_values']['av'], 22)
        published = []
        def persist(candidate):
            raise IOError('disk full')
        with self.assertRaises(IOError):
            persist(prepared)
            published.extend(effects['notices'])
        self.assertFalse(published)
        self.assertEqual(restarted, before)
        retry = self.finish(restarted)
        self.assertEqual(retry[0], prepared)

    def test_actual_static_table_types_day_boundary_and_school_branch(self):
        script = """
import sys,json
sys.path.insert(0,'analysis/research-agent')
from read_literal_marshal import read
from pathlib import Path
from bytecode27 import read as read_code
from xdis.bytecode import Bytecode
from xdis.opcodes import opcode_27
base=Path('analysis/android640-scripts/com/data/cdata')
city=read(base/'city_data.marshal'); missions=read(base/'mission.marshal')
require=city[3]['area_require']
previous=None; max_day=None
for instruction in Bytecode(read_code(base.parent.parent/'const.marshal'),opcode_27):
    if instruction.opname=='STORE_NAME' and instruction.argval=='MAX_DAYNUM': max_day=previous.argval
    previous=instruction
print(json.dumps({'max_day':max_day,'keys':list(sorted({type(k).__name__ for k in require})),
                  'values':list(sorted({type(v).__name__ for v in require.values()})),
                  'next_type':type(missions[1105]['nextstagenums']).__name__,
                  'branch_links':list(missions[1105]['nextstagenums']),
                  'school_default_requirements':list(city[2]['area_require']['-1'])}))
"""
        observed = json.loads(subprocess.check_output([str(ROOT / '.venv/bin/python'), '-c', script], cwd=ROOT))
        self.assertEqual(observed['max_day'], 8)
        self.assertEqual(observed['keys'], ['str'])
        self.assertEqual(observed['values'], ['tuple'])
        self.assertEqual(observed['next_type'], 'tuple')
        self.assertIn(1106, observed['branch_links'])
        self.assertIn(1107, observed['branch_links'])
        self.assertEqual(observed['school_default_requirements'], [1])
        self.state['day']['stock_day'] = observed['max_day'] - 2
        self.admit()
        self.state['day']['stock_day'] = observed['max_day'] - 1
        with self.assertRaises(ValueError): self.admit()

    def test_all_42_normal_city_stages_follow_original_links_and_dependencies(self):
        # Synthetic host results exercise the common transaction; this is not a
        # claim that any device battle or full route has been played.
        state = copy.deepcopy(self.state)
        accepted = 0
        for area in range(2, 9):
            for scene in basic_city_stage_chain(area, state, self.missions):
                state['story']['city_values']['av'] = 24
                state['profile']['heroes']['24']['cf'] = 100
                self.state = state
                request = dict(self.request, s=scene, d={'a': area})
                admitted, _ = self.admit(state, request)
                state, reply, effects, changed = self.finish(admitted)
                self.assertTrue(changed)
                self.assertEqual(reply['r']['stage'], scene)
                accepted += 1
            self.assertEqual(state['story']['city_areas'][str(area)]['st'][0], 0)
        self.assertEqual(accepted, 42)
        self.assertEqual(len(state['battle']['receipts']), 32)
        self.assertEqual(len(state['story']['battle_wins']), 43)
        validate_stage_battle_state(state['battle'])


if __name__ == '__main__':
    unittest.main()
