"""Execute the shipped flat runtime without host offline-module import fallbacks.

Only this project's source is executed. No original game bytecode, bootstrap
installation, app data, device, or native imports are executed.
"""
import ast
import builtins
import json
from pathlib import Path
import sys
import unittest
from lib2to3 import pygram, pytree
from lib2to3.pgen2 import driver

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from patch_bootstrap import embedded_loader


class GenericEmbeddedRuntimeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.loader = embedded_loader(ROOT / 'runtime')
        # Do not execute the bootstrap tail, which installs original game hooks.
        assignment = ast.parse(cls.loader.splitlines()[0]).body[0]
        assert isinstance(assignment, ast.Assign)
        assert assignment.targets[0].id == '_f7_embedded_gateway_source'
        cls.source = ast.literal_eval(assignment.value)
        cls.blocked = []
        real_import = builtins.__import__
        def imports(name, globals=None, locals=None, fromlist=(), level=0):
            if name.startswith('offline_'):
                cls.blocked.append(name)
                raise ImportError('No standalone offline modules in production flat runtime: ' + name)
            return real_import(name, globals, locals, fromlist, level)
        isolated_builtins = dict(vars(builtins), __import__=imports)
        cls.namespace = {'__builtins__': isolated_builtins, '__name__': 'flat_production_runtime'}
        cls.offline_modules_before = {k: v for k, v in sys.modules.items() if k.startswith('offline_')}
        exec(compile(cls.source, '<actual-embedded-gateway>', 'exec'), cls.namespace, cls.namespace)

    def state(self):
        n = self.namespace
        return {'story': n['initial_story_state'](), 'available_events': [],
            'processing_events': [], 'completed_events': [], 'event_traces': []}

    def test_flat_source_order_and_no_host_runtime_import_dependency(self):
        positions = []
        for filename in ('offline_yumi.py', 'offline_route_agreements.py', 'offline_week.py',
                         'offline_day.py', 'offline_event_effects.py', 'offline_native_story_callbacks.py'):
            original = (ROOT / 'runtime' / filename).read_text(encoding='ascii')
            self.assertIn(original, self.source)
            positions.append(self.source.index(original))
        self.assertEqual(positions, sorted(positions))
        self.assertTrue(self.blocked)
        self.assertIn('offline_yumi', self.blocked)
        self.assertIn('offline_route_agreements', self.blocked)
        after = {k: v for k, v in sys.modules.items() if k.startswith('offline_')}
        self.assertEqual(after, self.offline_modules_before)
        for name in ('apply_yumi_event', 'apply_route_agreement', 'prepare_story_operation',
                     'plan_event_effects', 'install_native_story_callbacks', 'LocalProxy'):
            self.assertIs(self.namespace[name].__globals__ if name != 'LocalProxy' else
                self.namespace[name].handle_yumi.__globals__, self.namespace)

    def test_python27_grammar_and_external_source_order_allowlist(self):
        parser = driver.Driver(pygram.python_grammar, convert=pytree.convert)
        parser.parse_string(self.source + '\n')
        parser.parse_string(self.loader + '\n')
        bootstrap = (ROOT / 'runtime/offline_bootstrap.py').read_text(encoding='ascii')
        parser.parse_string(bootstrap + '\n')
        # Inspect the actual fallback concatenation, without running bootstrap.
        concat = next(line for line in bootstrap.splitlines() if '_f7_transport_source + ' in line)
        variables = ('_f7_yumi_source', '_f7_route_agreements_source', '_f7_week_source',
                     '_f7_day_source', '_f7_effects_source')
        self.assertEqual([concat.index(v) for v in variables], sorted(concat.index(v) for v in variables))
        for filename in ('offline_yumi.py', 'offline_route_agreements.py', 'offline_native_story_callbacks.py'):
            self.assertIn("os.path.join(_f7_doc, '%s')" % filename, bootstrap)
        members = json.loads((ROOT / 'offline-project-allowlist.json').read_text())['files']
        self.assertEqual(len(members), 63)
        self.assertIn('runtime/offline_native_story_callbacks.py', members)
        self.assertIn('runtime/offline_daerweila.py', members)
        self.assertIn('runtime/offline_role_mission.py', members)
        self.assertIn('runtime/offline_chapter_campaign.py', members)
        self.assertIn('runtime/offline_battle_terminal.py', members)
        self.assertEqual(len(members), len(set(members)))
        for filename in ('runtime/offline_yumi.py', 'runtime/offline_route_agreements.py', 'runtime/offline_huisu.py'):
            self.assertIn(filename, members)

    def test_unseen_event_id_uses_generic_field_and_occurrence_ledger(self):
        n = self.namespace
        event = 987654321
        row = {'release': 1, 'gainBaiyuVal': 7, 'special_agreement': '2'}
        self.assertEqual(n['classify_event_effects'](row)['unsupported_fields'], [])
        state, notices, diagnostic = n['plan_event_effects'](self.state(), event, {event: row}, {},
            {'receipt_key': 'new-generic-occurrence'})
        self.assertTrue(diagnostic['ready'], diagnostic)
        self.assertEqual(state['story']['baiyu_value'], 57)
        self.assertTrue(state['story']['yumi']['ycyo'])
        replay, notices, diagnostic = n['plan_event_effects'](state, event, {event: row}, {},
            {'receipt_key': 'new-generic-occurrence'})
        self.assertEqual(replay['story']['baiyu_value'], 57)
        self.assertEqual(notices, [])
        # The planner is a transaction component, not a dialogue proof producer.
        self.assertEqual(state['completed_events'], [])

    def test_actual_story_engine_requires_dialog_before_generic_effect(self):
        n = self.namespace
        event, dialog = 987654322, 7654321
        content = {event: {'release': 1, 'dialog': dialog, 'gainBaiyuVal': -9,
                           'special_agreement': '1'}}
        state = self.state()
        state['processing_events'] = [event]
        n['begin_story_occurrence'](state, event)
        waiting, notices = n['prepare_story_operation'](state, 'start', {'e': event}, content, {}, {})
        self.assertNotIn(event, waiting['completed_events'])
        self.assertNotIn('yumi', waiting['story'])
        unrelated, notices = n['prepare_story_operation'](waiting, 'trace',
            {'k': 'dialog', 'd': {'c': dialog + 1}}, content, {}, {})
        self.assertNotIn('yumi', unrelated['story'])
        complete, notices = n['prepare_story_operation'](unrelated, 'trace',
            {'k': 'dialog', 'd': {'c': dialog}}, content, {}, {})
        self.assertIn(event, complete['completed_events'])
        self.assertEqual(complete['story']['baiyu_value'], 41)
        self.assertTrue(complete['story']['yumi']['ysg'])

    def test_agreement_values_apply_without_event_id_allowlist(self):
        n = self.namespace
        for offset, (value, field) in enumerate((('5', 'wulu_special_goodnight'),
                ('daerweila_clue_open', 'show_daerweila_head'),
                ('daerweila_human_close', 'daerweila_human_lock'),
                ('daerweila_devil_close', 'daerweila_devil_lock'))):
            event = 987654330 + offset
            row = {'release': 1, 'special_agreement': value}
            self.assertEqual(n['classify_event_effects'](row)['unsupported_fields'], [])
            state, notices, diagnostic = n['plan_event_effects'](self.state(), event, {event: row}, {}, {})
            self.assertTrue(diagnostic['ready'], diagnostic)
            self.assertTrue(state['story'][field])
        for route, field in (('9', 'jiaohui_special_goodnight'), ('11-1', 'alanSpecialGoodNight')):
            state = self.state(); state['story']['route'] = route
            row = {'release': 1, 'special_agreement': '6'}
            state, _, diagnostic = n['plan_event_effects'](state, 987654350, {987654350: row}, {}, {})
            self.assertTrue(diagnostic['ready'], diagnostic)
            self.assertTrue(state['story'][field])

    def test_literal_original_3147_row_keeps_dialog_gate_in_flat_engine(self):
        # Parse original table constants without executing any original code.
        from read_data_table import read
        row = read(ROOT / 'analysis/decompiled/event_content.py')[3147]
        self.assertEqual(row['special_agreement'], '2')
        self.assertEqual(row['dialog'], 3147)
        n = self.namespace
        state = self.state(); state['processing_events'] = [3147]
        n['begin_story_occurrence'](state, 3147)
        waiting, _ = n['prepare_story_operation'](state, 'start', {'e': 3147}, {3147: row}, {}, {})
        self.assertNotIn('yumi', waiting['story'])
        self.assertNotIn(3147, waiting['completed_events'])
        complete, notices = n['prepare_story_operation'](waiting, 'trace',
            {'k': 'dialog', 'd': {'c': 3147}}, {3147: row}, {}, {})
        self.assertIn(3147, complete['completed_events'])
        self.assertTrue(complete['story']['yumi']['ycyo'])
        self.assertIn('openYumiYaocaoyuan', [name for name, payload in notices])
