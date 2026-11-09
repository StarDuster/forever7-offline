import copy
from pathlib import Path
import sys
import unittest
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'runtime'))
from offline_battle import prepare_first_battle_admission, prepare_battle_finish

class FirstBattleTests(unittest.TestCase):
    def setUp(self):
        self.profile = {'heroes': {'24': {'equipment': ['preserved'], 'as': 1}}}
        self.story = {'city_areas': {'1': {'st': [1, False, False], 'stage': {'cs': 101, 'sl': [[101]]}}}}
        self.missions = {101: {'release': 1, 'ch': 1, 'least_hero_num': 1, 'max_hero_num': 3, 'map_path': ['scene/pve/g58_zyt_pve.scn']}}
        self.request = {'t': 1, 's': 101, 'h': [24], 'd': {'a': 1}}

    def admit(self, state=None):
        return prepare_first_battle_admission(state, self.profile, self.story, self.request, self.missions, lambda: 'fight-one')

    def test_admission_pins_original_hero_state_without_manufacturing_result(self):
        battle, changed = self.admit()
        self.assertTrue(changed)
        self.assertEqual(battle['active']['heroes']['24'], self.profile['heroes']['24'])
        self.assertFalse(battle['receipts'])
        again, changed = self.admit(battle)
        self.assertFalse(changed)
        self.assertEqual(again, battle)
        self.profile['heroes']['24']['equipment'].append('later')
        self.assertEqual(battle['active']['heroes']['24']['equipment'], ['preserved'])

    def test_unknown_mission_team_or_locked_area_is_rejected(self):
        before = copy.deepcopy(self.profile)
        for mutate in (lambda: self.request.update(s=999), lambda: self.request.update(h=[24, 24]), lambda: self.story['city_areas'].clear()):
            self.setUp()
            mutate()
            with self.assertRaises(ValueError):
                self.admit()
        self.assertEqual(self.profile, before)

    def test_actual_loss_is_preserved_and_duplicate_does_not_settle_twice(self):
        battle, _ = self.admit()
        result = {'t': 1, 's': 101, 'h': [24], 'x': [], 'w': 0, 'e': {}}
        calls = []
        def settle(active, args):
            calls.append(active['fight_id'])
            return dict((k, args[k]) for k in ('t', 's', 'h', 'x', 'w')) | {'r': {}}, {'won': False}
        done, reply, effects, changed = prepare_battle_finish(battle, result, settle)
        self.assertEqual(reply['w'], 0)
        self.assertFalse(effects['won'])
        self.assertIsNone(done['active'])
        again, repeat, effects, changed = prepare_battle_finish(done, result, settle)
        self.assertFalse(changed)
        self.assertEqual(reply, repeat)
        self.assertEqual(calls, ['fight-one'])
        self.assertIsNone(effects)

    def test_finish_cannot_change_actual_result_and_bad_result_preserves_admission(self):
        battle, _ = self.admit()
        before = copy.deepcopy(battle)
        result = {'t': 1, 's': 101, 'h': [24], 'x': [], 'w': 0, 'e': {}}
        with self.assertRaises(ValueError):
            prepare_battle_finish(battle, result, lambda active, args: (dict(args, w=1, r={}), {}))
        self.assertEqual(battle, before)

    def test_embedded_admission_uses_stock_calculators_and_persists_before_reply(self):
        import json
        import tempfile
        from types import ModuleType, SimpleNamespace
        from unittest.mock import patch
        from test_local_gateway import Owner
        scope = {'__name__': 'embedded_battle'}
        for name in ('offline_store.py', 'offline_wardrobe_completion.py', 'offline_profile.py', 'offline_transport.py', 'offline_stage.py', 'offline_week.py', 'offline_day.py', 'offline_conditions.py', 'offline_story.py', 'offline_event_effects.py', 'offline_story_engine.py', 'offline_city_actions.py', 'offline_avatar_snapshot.py', 'offline_postbattle.py', 'offline_event_battle.py', 'offline_battle.py', 'offline_treasure.py', 'offline_gacha.py', 'local_gateway.py'):
            exec(compile((ROOT / 'runtime' / name).read_text(), name, 'exec'), scope)
        native_hero = SimpleNamespace(calcSkill=lambda: ([(11, 2)], [(22, 3)]),
            calcAllAttr=lambda level: {'_base_max_hp': 123, '_hp_delta': 7},
            calcTricks=lambda: [44, 45], getCurSkinObj=lambda: SimpleNamespace(getPersistentDict=lambda: {'i': 20124, 'u': 'f' * 24, 'cd': {'1': [1, 2, 3]}}))
        modules = {n: ModuleType(n) for n in ('common', 'common.IdManager', 'com', 'com.data', 'com.data.cdata', 'com.data.cdata.mission')}
        modules['common.IdManager'].IdManager = SimpleNamespace(genid=lambda: 'f' * 24, id2str=lambda value: str(value))
        modules['com.data.cdata.mission'].data = self.missions
        modules['C_file'] = SimpleNamespace(find_res_file=lambda path, root: 'resolved-original-resource')
        for name, data in (('skin', {20124: {'hero': 24, 'model_id': 24}}), ('ui_model_data', {})):
            module = ModuleType('com.data.cdata.' + name)
            module.data = data
            modules[module.__name__] = module
        with tempfile.TemporaryDirectory() as folder, patch.dict(sys.modules, dict(modules, offline_battle=None)):
            scope['_f7_doc'], scope['_f7_log'] = folder, lambda _: None
            owner = Owner()
            owner.id, owner.level = 'original-entity', 1
            owner.heroMgrData = SimpleNamespace(getHero=lambda hid: native_hero,
                getArtifactInfo=lambda hid: (True, 3), getAwakeStage=lambda hid: 1)
            proxy = scope['LocalProxy'](None, owner, persistent=True)
            hero = json.loads((ROOT / 'tests/fixtures/native-hero24.json').read_text())['hero']
            proxy.profile = {'version': 1, 'heroes': {'24': hero}, 'migrations': []}
            proxy.story['city_areas'] = {'1': {'id': 1, 'st': [1, False, False], 'stage': {'cs': 101, 'sl': [[101]]}, 'lv': 1, 'bd': {}}}
            proxy.save_progress()
            proxy.ensure_battle_economy()
            proxy.handle_battle_admission(self.request, 7)
            reply_name, reply = owner.replies[-1]
            self.assertEqual(reply_name, 'combatOfflineReply')
            self.assertEqual(reply['_cbid_'], 7)
            cdata = reply['c']['heroes'][str(('', 24))]
            self.assertEqual(cdata['d'], {'_base_max_hp': 123, '_hp_delta': 7})
            self.assertEqual(cdata['s'], [[[11, 2]], [[22, 3]]])
            self.assertEqual(cdata['ai'], [True, 3])
            self.assertEqual(cdata['as'], 1)
            self.assertEqual(cdata['t'], [44, 45])
            self.assertEqual(reply['c']['skins'][0]['i'], 20124)
            self.assertEqual(reply['c']['heroes'][str(('original-entity', 24))], cdata)
            restored = scope['LocalProxy'](None, Owner(), persistent=True)
            self.assertEqual(restored.battle['active']['fight_id'], reply['f'])
            self.assertFalse(restored.battle['receipts'])
            original_fight = reply['f']
            proxy.handle_battle_admission(self.request, 8)
            self.assertEqual(owner.replies[-1][1]['f'], original_fight)
            self.assertFalse(proxy.battle['receipts'])
            proxy.battle = scope['initial_battle_state']()
            proxy.save_progress()
            with patch.object(proxy._store, 'write', side_effect=OSError('disk full')):
                with self.assertRaises(OSError):
                    proxy.handle_battle_admission(self.request, 9)
            self.assertIsNone(proxy.battle['active'])
            self.assertEqual(owner.replies[-1][1]['t'], 0)
            self.assertEqual(owner.replies[-1][1]['_cbid_'], 9)

    def test_original_client_boolean_win_is_accepted_but_arbitrary_truthy_values_are_not(self):
        for win in (True, False):
            battle, _ = self.admit()
            args = {'t': 1, 's': 101, 'h': [24], 'x': [], 'w': win, 'e': {}}
            done, reply, effects, changed = prepare_battle_finish(battle, args,
                lambda active, actual: (dict(actual, r={}), {}))
            self.assertIs(type(reply['w']), int)
            self.assertEqual(reply['w'], int(win))
            repeat = dict(args, w=int(win))
            _, replay, _, changed = prepare_battle_finish(done, repeat, lambda *args: self.fail('duplicate'))
            self.assertFalse(changed)
            for invalid in (2, -1, 'true', 1.0):
                with self.assertRaises(ValueError):
                    prepare_battle_finish(battle, dict(args, w=invalid), lambda *args: self.fail('invalid'))

    def test_receipts_are_bounded_and_never_turn_losses_into_progression(self):
        battle = None
        for number in range(40):
            battle, _ = prepare_first_battle_admission(battle, self.profile, self.story, self.request,
                self.missions, lambda number=number: 'fight-%s' % number)
            result = {'t': 1, 's': 101, 'h': [24], 'x': [], 'w': False, 'e': {'attempt': number}}
            battle, reply, _, _ = prepare_battle_finish(battle, result,
                lambda active, actual: (dict(actual, r={}), {}))
        self.assertEqual(len(battle['receipts']), 32)
        self.assertEqual(battle['receipts'][-1]['fight_id'], 'fight-39')
        self.assertTrue(all(receipt['reply']['w'] == 0 for receipt in battle['receipts']))
        self.assertTrue(all(len(receipt['fingerprint']) == 64 for receipt in battle['receipts']))


class ActualBattleEconomyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import json
        sys.path.insert(0, str(ROOT / 'analysis/research-agent'))
        from read_literal_marshal import read
        base = ROOT / 'analysis/android640-scripts/com/data/cdata'
        cls.treasures = read(base / 'hero_treasure.marshal')
        cls.pools = read(base / 'reward_random.marshal')
        cls.rewards = read(base / 'reward_common.marshal')
        cls.fight_rewards = read(base / 'city_fight_reward.marshal')
        cls.levels = read(base / 'player_exp.marshal')
        cls.city_catalog = read(base / 'city_data.marshal')
        cls.missions = read(base / 'mission.marshal')
        cls.indices = json.loads((ROOT / 'tests/fixtures/combat-attribute-indices.json').read_text())['indices']

    def profile(self):
        return {'heroes': {'24': {'ef': 0, 'cf': 100}},
                'economy': {'version': 1, 'level': 1, 'exp': 0, 'money': 10000},
                'treasures': {'version': 1, 'items': []}}

    def test_every_actual_pool_304_nonzero_outcome_has_constructible_original_attributes(self):
        from offline_treasure import make_table_treasure_reward
        allowed = {'id', 'treasure', 'treasureNum', 'treasureLevel', 'tradeType'}
        checked = 0
        for reward_id, weight in self.pools[304]['weights']:
            if reward_id == 0:
                continue
            definition = self.rewards[reward_id]
            self.assertFalse(set(definition) - allowed)
            self.assertEqual(len(definition['treasure']), len(definition['treasureNum']))
            self.assertEqual(len(definition['treasure']), len(definition['treasureLevel']))
            for template, count, quality in zip(definition['treasure'], definition['treasureNum'], definition['treasureLevel']):
                item = make_table_treasure_reward(template, quality, self.treasures, self.indices, lambda: 'f' * 24, 123, definition['tradeType'])
                self.assertTrue(item['tr']['attr'])
                self.assertEqual(item['tr']['cl'], quality)
                self.assertEqual(item['tr']['ft'], list(self.treasures[(template, quality)].get('fixTrick', ())))
            checked += 1
        self.assertEqual(checked, len(self.pools[304]['weights']) - 1)

    def test_real_level_one_win_pays_original_money_exp_and_friendly_and_stable_drop(self):
        from offline_battle import settle_first_battle_economy
        from offline_treasure import make_table_treasure_reward
        profile = self.profile()
        calls = []
        def grant(template, quality, trade_type):
            calls.append(template)
            return make_table_treasure_reward(template, quality, self.treasures, self.indices, lambda: '%024x' % len(calls), 123, trade_type)
        result = {'t': 1, 's': 101, 'h': [24], 'x': [], 'w': 1, 'e': {}}
        # Exercise an actual nonzero pool outcome, not just its no-drop branch.
        for number in range(1000):
            active = {'fight_id': 'tested-fight-%s' % number, 'reward_level': 1}
            reply, effects = settle_first_battle_economy(profile, active, result, self.fight_rewards, self.levels, self.pools, self.rewards, grant)
            if effects['granted']:
                break
        self.assertTrue(effects['granted'])
        self.assertEqual(effects['profile']['economy'], {'version': 1, 'level': 2, 'exp': 700, 'money': 13267})
        self.assertEqual(effects['profile']['heroes']['24']['ef'], 1)
        self.assertEqual(effects['profile']['heroes']['24']['cf'], 100)
        self.assertEqual(reply['r']['money'], 3267)
        self.assertEqual(reply['r']['exp'], 2000)
        self.assertEqual((reply['r']['ol'], reply['r']['oe'], reply['r']['cl'], reply['r']['ce']), (1, 0, 2, 700))
        self.assertEqual(reply['r']['treasure'][0][3][0], effects['granted'][0]['u'])
        self.assertEqual(profile, self.profile())
        loss = dict(result, w=0)
        losing, effects = settle_first_battle_economy(profile, active, loss, self.fight_rewards, self.levels, self.pools, self.rewards, lambda *args: self.fail('loss cannot grant'))
        self.assertEqual(losing['w'], 0)
        self.assertEqual(losing['r'], {})
        self.assertEqual(effects['profile'], profile)

    def test_embedded_gateway_finish_is_atomic_replay_safe_and_can_abandon_or_restart(self):
        import hashlib
        import json
        import tempfile
        from types import ModuleType, SimpleNamespace
        from unittest.mock import patch
        from test_local_gateway import Owner
        from test_offline_transport import FakeEngine
        scope = {'__name__': 'embedded_full_battle'}
        for name in ('offline_store.py', 'offline_wardrobe_completion.py', 'offline_profile.py', 'offline_transport.py', 'offline_stage.py', 'offline_week.py', 'offline_day.py', 'offline_conditions.py', 'offline_story.py', 'offline_event_effects.py', 'offline_story_engine.py', 'offline_city_actions.py', 'offline_avatar_snapshot.py', 'offline_postbattle.py', 'offline_event_battle.py', 'offline_battle.py', 'offline_treasure.py', 'offline_gacha.py', 'local_gateway.py'):
            exec(compile((ROOT / 'runtime' / name).read_text(), name, 'exec'), scope)
        fixture = json.loads((ROOT / 'tests/fixtures/opening-story.json').read_text())
        content = {int(k): v for k, v in fixture['content'].items()}
        triggers = {int(k): dict(v, conds={int(n): value for n, value in v['conds'].items()}) for k, v in fixture['triggers'].items()}
        modules = {n: ModuleType(n) for n in ('common', 'common.IdManager', 'com', 'com.const', 'com.data', 'com.data.cdata')}
        for name, data in (('mission', {101: {'release': 1, 'ch': 1, 'least_hero_num': 1, 'max_hero_num': 3, 'map_path': ['scene/pve/g58_zyt_pve.scn']}}),
                           ('city_fight_reward', self.fight_rewards), ('city_development', {}), ('city_data', self.city_catalog), ('player_exp', self.levels),
                           ('reward_random', self.pools), ('reward_common', self.rewards),
                           ('hero_treasure', self.treasures), ('event_content', content), ('event_condition', triggers)):
            module = ModuleType('com.data.cdata.' + name)
            module.data = data
            modules[module.__name__] = module
        for number in range(1000, 2000):
            fight_id = '%024x' % number
            seed = ('first-battle-drop-v1:%s:304:0' % fight_id).encode('ascii')
            if int(hashlib.sha256(seed).hexdigest(), 16) % sum(w for r, w in self.pools[304]['weights']) >= 147000:
                break
        generated = iter([fight_id] + ['%024x' % n for n in range(5000, 5100)])
        modules['com.data.cdata.mission'].data[101].update(fixture['postbattle_missions']['101'])
        modules['com.data.cdata.mission'].data[1101] = fixture['postbattle_missions']['1101']
        modules['common.IdManager'].IdManager = SimpleNamespace(genid=lambda: next(generated), id2str=str, str2id=lambda uid: ('native', uid))
        modules['com.const'].CombatAttrs = SimpleNamespace(NAME_TO_INDEX=self.indices)
        modules['C_file'] = SimpleNamespace(find_res_file=lambda path, root: 'resolved-original-resource')
        for name, data in (('skin', {24: {'hero': 24, 'model_id': 24}}), ('ui_model_data', {})):
            module = ModuleType('com.data.cdata.' + name)
            module.data = data
            modules[module.__name__] = module
        native_hero = SimpleNamespace(calcSkill=lambda: ([(11, 2)], [(22, 3)]),
            calcAllAttr=lambda level: {'_base_max_hp': 123}, calcTricks=lambda: [44],
            getCurSkinObj=lambda: SimpleNamespace(getPersistentDict=lambda: {'i': 24, 'u': 'f' * 24}))
        engine = FakeEngine()
        modules['gg'] = engine
        with tempfile.TemporaryDirectory() as folder, patch.dict(sys.modules, dict(modules, offline_battle=None)):
            scope['_f7_doc'], scope['_f7_log'] = folder, lambda _: None
            owner = Owner()
            owner.id, owner.level = 'live-identity', 1
            owner.heroMgrData = SimpleNamespace(getHero=lambda hid: native_hero, getArtifactInfo=lambda hid: (False, 0), getAwakeStage=lambda hid: 1)
            proxy = scope['LocalProxy'](None, owner, persistent=True)
            hero = json.loads((ROOT / 'tests/fixtures/native-hero24.json').read_text())['hero']
            proxy.profile = {'version': 1, 'heroes': {'24': hero}, 'migrations': [], 'economy': self.profile()['economy'], 'treasures': {'version': 1, 'items': []}}
            proxy.story.update(emergency=False, starter_hero=7, starter_source='player-choice', city_areas={'1': {'id': 1, 'st': [1, False, False], 'stage': {'cs': 101, 'sl': [[101]]}, 'lv': 1, 'bd': {}}})
            proxy.available_events, proxy.completed_events, proxy.processing_events = {}, {8, 1000, 1001, 1002, 1004, 1021, 1039}, {1043}
            proxy.save_progress()
            request = {'t': 1, 's': 101, 'h': [24], 'd': {'a': 1}}
            proxy.handle_battle_admission(request, 7)
            self.assertEqual(proxy.battle['active']['fight_id'], fight_id)
            # Restart preserves the admission and same-team replay keeps its id.
            restored = scope['LocalProxy'](None, owner, persistent=True)
            self.assertEqual(restored.battle, proxy.battle)
            restored.handle_battle_admission(request, 8)
            self.assertEqual(restored.battle['active']['fight_id'], fight_id)
            proxy = restored
            proxy.handle_battle_hero_switch({'t': 1, 's': 101, 'h': 24})
            self.assertEqual(owner.replies[-1][0], 'combatOfflineHeroConfirm')
            actual = {'t': 1, 's': 101, 'h': [24], 'x': [], 'w': True, 'e': {'elapsed': 15}}
            saved = proxy.progress_snapshot()
            owner.replies.clear()
            with patch.object(proxy._store, 'write', side_effect=OSError('disk full')):
                with self.assertRaises(OSError):
                    proxy.handle_battle_finish(actual, fight_id)
            self.assertEqual(proxy.progress_snapshot(), saved)
            self.assertFalse(owner.replies)
            owner.combatData = SimpleNamespace(fight_id=fight_id)
            proxy.call_server_method('combatOfflineFinish', actual)
            self.assertFalse(owner.replies)
            engine.exec_cancel_all()
            engine.drain()
            self.assertIsNone(proxy.battle['active'])
            self.assertIn(1043, proxy.completed_events)
            self.assertEqual(proxy.profile['economy']['money'], 13267)
            self.assertEqual(proxy.profile['economy']['level'], 2)
            self.assertEqual(proxy.profile['economy']['exp'], 700)
            self.assertEqual(len(proxy.profile['treasures']['items']), 1)
            reward = [args for name, args in owner.replies if name == 'combatOfflineReward'][-1]
            self.assertEqual(reward['w'], 1)
            self.assertEqual(reward['r']['treasure'][0][3][0][0], 'native')
            paid = proxy.progress_snapshot()
            proxy.handle_battle_finish(actual, fight_id)
            self.assertEqual(proxy.progress_snapshot(), paid)
            self.assertEqual(len(proxy.battle['receipts']), 1)
            self.assertEqual(proxy.story['city_areas']['1']['st'][0], 0)
            self.assertEqual(proxy.story['city_areas']['2']['stage']['cs'], 1101)
            self.assertIn(10000, proxy.available_events)
            self.assertNotIn(10000, proxy.completed_events)
            proxy.handle_battle_admission(request, 9)
            self.assertIsNone(proxy.battle['active'])  # Cleared area is not a FIGHT admission.
            self.assertEqual(owner.replies[-1][1]['t'], 0)
            no_old_reward = copy.deepcopy(proxy.profile)
            owner.replies.clear()
            proxy.handle_battle_finish(actual, 'unmatched-old-source')
            self.assertEqual(proxy.profile, no_old_reward)
            self.assertFalse(owner.replies)
            abandoning = scope['LocalProxy'](None, owner, persistent=False)
            abandoning.restore_progress(saved)  # Independent pre-result unit fixture.
            abandoning.reset_pending_battle()
            self.assertIsNone(abandoning.battle['active'])
            self.assertEqual(abandoning.profile, saved['profile'])
            self.assertIn(fight_id, abandoning.battle['abandoned'])
