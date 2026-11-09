"""Independent original-data boundaries, with explicit host fixture history.

No native win is claimed. Prior admission/choice history is a fixture; actual
project event and battle planners consume modeled original traces/results.
Original bytecode is inspected as data, never imported or executed here.
"""
import ast
import builtins
import copy
import json
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / 'runtime'), str(ROOT / 'tools'),
               str(ROOT / 'analysis/research-agent')]
import offline_city_stage_provider as provider
from offline_city_stage_provider import (original_city_stage_family,
    refresh_city_stage_provider, validate_city_stage_provider)
from offline_event_effects import plan_event_effects
from offline_stage import prepare_stage_admission, prepare_stage_finish
from offline_story import initial_story_state
from offline_story_engine import (begin_story_occurrence, prepare_story_operation,
                                  story_occurrence_key, refresh_story_events)
from offline_week import prepare_week_route_handoff
from offline_store import OfflineSaveStore
from read_data_table import read
from read_literal_marshal import read as read_marshal
from bytecode27 import read as read_code
from xdis.bytecode import Bytecode
from xdis.opcodes import opcode_27
from patch_bootstrap import embedded_loader
import test_offline_event_effects as fixture


def original_coc_scenes():
    instructions = list(Bytecode(read_code(
        ROOT / 'analysis/android640-scripts/com/const.marshal'), opcode_27))
    for index, operation in enumerate(instructions):
        if operation.opname == 'STORE_NAME' and operation.argval == 'COC_HERO_LIMIT_SCENE':
            build = instructions[index - 1]
            assert build.opname == 'BUILD_TUPLE'
            values = instructions[index - 1 - build.arg:index - 1]
            assert all(item.opname == 'LOAD_CONST' for item in values)
            return tuple(item.argval for item in values)
    raise AssertionError('Missing original COC family constant')


class IndependentCityStageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tables = fixture.original_tables()
        base = ROOT / 'analysis/android640-scripts/com/data/cdata'
        cls.tables['city_area_link_data'] = read_marshal(base / 'city_area_link_data.marshal')
        cls.routes = read_marshal(base / 'story_route.marshal')
        cls.tables['coc_scenes'] = original_coc_scenes()
        cls.content = read(ROOT / 'analysis/decompiled/event_content.py')
        cls.triggers = read(ROOT / 'analysis/decompiled/event_condition.py')
        cls.api = globals()

    def setUp(self):
        self.state = fixture.base_state(self.tables)
        self.state['story'] = initial_story_state()
        self.state['story'].update(route='26-1', week=1, date=0, emergency=False,
            city_values={'av':24, 'fv':200, 'rv':0, 'dv':0, 'bf':0, 'ev':0},
            city_areas={str(a): {'id':a, 'lv':1, 'st':[2, False, False], 'bd':{}}
                        for a in range(1, 10)})
        # A preexisting ordinary projection must not be replaced permanently.
        self.state['story']['city_areas']['6']['stage'] = {'cs':5101, 'sl':[[5101]]}
        self.state.update(conditions=[[101, 0]], event_traces=[],
            day={'version':1, 'stock_day':0, 'intent':None, 'receipt':None, 'review':None},
            battle={'version':1, 'active':None, 'receipts':[]})
        self.serial = 0

    def call(self, name, *args, **kwargs):
        return self.api[name](*args, **kwargs)

    def operation(self, name, args):
        self.state, notices = self.call('prepare_story_operation', self.state, name,
            args, self.content, self.triggers, self.tables)
        return notices

    def begin(self, event):
        # This is the explicitly declared prior entry/choice admission fixture.
        self.call('begin_story_occurrence', self.state, event, self.content, self.triggers)
        self.state['processing_events'].append(event)
        return self.operation('start', {'e':event})

    def dialog(self, event):
        return self.operation('trace', {'k':'dialog', 'd':{'c':self.content[event]['dialog']}})

    def callback(self, event):
        return self.operation('callback', {'e':event, 'token':'ui:%s' % event,
            'source_occurrence':[1, self.state['story']['event_occurrences'][str(event)]]})

    def handoff(self, event):
        receipt = self.call('story_occurrence_key', self.state, event)
        request = self.state['story']['event_handoffs'][receipt][0]
        self.state, notices, changed = self.call('prepare_week_route_handoff',
            self.state, request, self.content, self.routes)
        self.assertTrue(changed)
        return notices

    def enter(self):
        self.begin(1424)
        self.assertNotIn('city_stage_provider', self.state['story'])
        self.dialog(1424)
        self.assertIn(1424, self.state['completed_events'])
        self.assertEqual(self.state['story']['route'], '26-1')
        self.assertNotIn('10000', self.state['story']['city_areas'])
        return self.handoff(1424)

    def admit(self, scene=482):
        self.serial += 1
        self.state, changed = self.call('prepare_stage_admission', self.state,
            {'t':1, 's':scene, 'h':[135], 'd':{'a':self.tables['mission'][scene]['ch']}},
            self.tables['mission'], lambda:'independent-fight-%s' % self.serial)
        self.assertTrue(changed)

    def finish(self, win):
        active = self.state['battle']['active']
        arguments = dict(t=1, s=active['request']['s'], h=[135], x=[], w=win, e={})
        def settle(admission, actual):
            return {key:copy.deepcopy(actual[key]) for key in ('t','s','h','x','w')} | {'r':{}}, {
                'profile':copy.deepcopy(self.state['profile']), 'notices':[], 'granted':[]}
        self.state, _, _, changed = self.call('prepare_stage_finish', self.state,
            arguments, self.tables['mission'], self.tables['city_data'], settle, active['fight_id'])
        self.assertTrue(changed)

    def reach_second_node(self):
        self.enter()
        self.admit(); self.finish(1)
        self.assertEqual(self.state['story']['city_areas']['10000']['st'][0], 1)
        self.call('refresh_story_events', self.state, self.triggers, self.content)
        self.assertIn(1442, dict(self.state['available_events']))
        self.begin(1442); self.dialog(1442)
        self.assertNotIn(1442, self.state['completed_events'])
        self.operation('option', {'e':1442, 'se':1443, 'op':0})
        self.assertEqual(self.state['story']['city_areas']['10000']['st'][0], 0)
        self.assertTrue(self.state['story']['city_areas']['6']['st'][2])
        self.callback(1443)
        self.assertEqual(self.state['story']['city_areas']['6']['stage'], {'cs':483,'sl':[[483]]})
        self.assertFalse(self.state['story']['city_areas']['6']['st'][2])

    def test_original_family_binding_and_deferred_entry_wire(self):
        self.assertEqual(self.tables['coc_scenes'], (482,483,484,485,486,486,487,488))
        notices = self.enter()
        self.assertTrue(any(name == 'get_all_area_info_reply' for name, _ in notices))
        family = self.call('original_city_stage_family', self.tables['mission'], self.tables['coc_scenes'])
        self.assertEqual(set(family), {10000,6,10001,4,10002,10003,2})
        self.assertNotIn(507, family.values()); self.assertNotIn(517, family.values())
        self.assertEqual(self.state['story']['city_areas']['10000']['stage'], {'cs':482,'sl':[[482]]})
        self.assertFalse(self.state['story']['city_areas']['7']['st'][2])
        self.assertTrue(self.state['story']['city_areas']['1']['st'][2])
        self.assertNotIn('10001', self.state['story']['city_areas'])

    def test_true_result_and_original_dialog_ui_chain_do_not_skip_free_events(self):
        self.reach_second_node()
        self.assertEqual(self.state['story']['city_values']['av'], 22)
        self.assertEqual(self.state['story']['battle_wins'], [482])
        self.assertNotIn(483, self.state['story']['battle_wins'])
        self.assertNotIn(1437, self.state['completed_events'])
        self.admit(483)
        before = copy.deepcopy(self.state)
        self.finish(0)
        self.assertEqual(self.state['story'], before['story'])
        self.assertEqual(self.state['profile'], before['profile'])

    def test_other_original_route_and_legacy_route_marker_cannot_activate_coc(self):
        self.begin(510); self.dialog(510); self.handoff(510)
        self.assertEqual(self.state['story']['route'], '8-1')
        self.assertNotIn('city_stage_provider', self.state['story'])
        self.state['story']['route'] = '27-1'
        self.call('refresh_city_stage_provider', self.state)
        self.assertNotIn('city_stage_provider', self.state['story'])

    def test_real_exit_keeps_new_area_effects_and_committed_target_unlock(self):
        self.reach_second_node()
        assets = copy.deepcopy(self.state['profile'])
        self.begin(1462); self.dialog(1462); self.handoff(1462)
        areas = self.state['story']['city_areas']
        self.assertEqual(self.state['story']['route'], '28-1')
        self.assertNotIn('city_stage_provider', self.state['story'])
        self.assertFalse(areas['6']['st'][2])
        self.assertEqual(areas['6']['st'][0], 0)
        self.assertEqual(areas['6']['stage'], {'cs':5101,'sl':[[5101]]})
        for aid in (1,2,3,4,5,7,8): self.assertTrue(areas[str(aid)]['st'][2])
        self.assertEqual(self.state['profile'], assets)

    def test_reload_preserves_source_and_stale_epoch_rejects_result(self):
        self.enter(); self.admit()
        with tempfile.TemporaryDirectory() as directory:
            path = str(Path(directory) / 'fixture.json')
            store = self.call('OfflineSaveStore', path, self.api['validate_city_stage_provider'])
            store.write(self.state)
            restored = self.call('OfflineSaveStore', path, self.api['validate_city_stage_provider']).load()
        # JSON intentionally normalizes original literal tuples to arrays.
        self.assertEqual(restored, json.loads(json.dumps(self.state)))
        self.state = restored
        resumed, changed = self.call('prepare_stage_admission', self.state,
            copy.deepcopy(self.state['battle']['active']['request']), self.tables['mission'],
            lambda:self.fail('resume cannot create a new fight'))
        self.assertFalse(changed)
        self.assertEqual(resumed, restored)
        self.state['story']['city_stage_provider']['epoch'] = 'f' * 64
        before = copy.deepcopy(self.state)
        with self.assertRaises(ValueError): self.finish(1)
        self.assertEqual(self.state, before)


# Run the same behavioral boundaries in the real concatenated namespace, with
# standalone offline imports blocked as they are in the production APK.
class IndependentFlatCityStageTests(IndependentCityStageTests):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        loader = embedded_loader(ROOT / 'runtime')
        source = ast.literal_eval(ast.parse(loader.splitlines()[0]).body[0].value)
        real_import = builtins.__import__
        def imports(name, globals=None, locals=None, fromlist=(), level=0):
            if name.startswith('offline_'): raise ImportError('production flat namespace')
            return real_import(name, globals, locals, fromlist, level)
        namespace = {'__name__':'independent_flat_city_stage',
            '__builtins__':dict(vars(builtins), __import__=imports)}
        exec(compile(source, '<actual-embedded-runtime>', 'exec'), namespace, namespace)
        cls.api = namespace


if __name__ == '__main__': unittest.main()
