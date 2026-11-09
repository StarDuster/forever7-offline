"""Independent original-data timelines in host and actual embedded namespace.

Prior event availability and battle results are explicit host fixtures, not
native-earned route progress. The helper-level special-stage test explicitly
offers the original terminal event; gateway producer tests cover that bridge.
"""
import ast
import builtins
import copy
import json
from pathlib import Path
import sys
import unittest
from collections.abc import Mapping

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / 'runtime'), str(ROOT / 'tools'),
               str(ROOT / 'analysis/research-agent')]
from offline_event_battle import (prepare_event_battle_gate,
    prepare_event_battle_admission, prepare_event_battle_finish)
from offline_stage import prepare_stage_admission, prepare_stage_finish
from offline_story_engine import (begin_story_occurrence, prepare_story_operation,
                                  story_occurrence_key)
from offline_week import prepare_week_route_handoff
from offline_special_city_stage import (resolve_special_city_stage,
    validate_special_city_stages, expire_special_city_stages)
from offline_battle_terminal import validate_event_terminal_state
from patch_bootstrap import embedded_loader
from read_data_table import read
from read_literal_marshal import read as read_marshal
import test_offline_event_effects as fixtures


class ReadOnlyOriginalRow(Mapping):
    """Original data boundary: a mapping need not be a builtin dictionary.

    Retaining identity on deepcopy deliberately prevents deepcopy from hiding
    an opaque mapping in a descriptor that must survive JSON save/reload.
    """
    def __init__(self, values):
        self._values = dict(values)

    def __getitem__(self, key):
        return self._values[key]

    def __iter__(self):
        return iter(self._values)

    def __len__(self):
        return len(self._values)

    def __deepcopy__(self, memo):
        return self


class IndependentTerminalStageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tables = fixtures.original_tables()
        directory = ROOT / 'analysis/android640-scripts/com/data/cdata'
        cls.tables['chapter_mission_data'] = read_marshal(directory / 'chapter_mission_data.marshal')
        cls.tables['event_content'] = read(ROOT / 'analysis/decompiled/event_content.py')
        cls.routes = read_marshal(directory / 'story_route.marshal')
        cls.api = globals()

    def setUp(self):
        self.events = self.tables['event_content']
        self.state = fixtures.base_state(self.tables)
        self.state.update(event_traces=[], conditions=[],
            day={'version':1, 'stock_day':0, 'intent':None, 'receipt':None, 'review':None},
            battle={'version':1, 'active':None, 'receipts':[]})
        self.state['story'].update(week=0, date=0, route='10-1', emergency=False,
            city_values={'av':24, 'fv':80, 'rv':0, 'dv':0, 'bf':0, 'ev':0},
            city_areas={str(area):{'id':area, 'lv':1, 'st':[2,False,False], 'bd':{}}
                        for area in range(1, 10)})
        self.state['story']['city_areas']['6']['stage'] = {'cs':5101, 'sl':[[5101]]}

    def call(self, name, *args, **kwargs):
        return self.api[name](*args, **kwargs)

    def operation(self, operation, args):
        self.state, notices = self.call('prepare_story_operation', self.state,
            operation, args, self.events, {}, self.tables)
        return notices

    def begin(self, event):
        # Availability is an explicitly modeled prior history. The actual
        # original row and occurrence planner control every subsequent gate.
        self.call('begin_story_occurrence', self.state, event, self.events, {})
        self.state['processing_events'].append(event)
        return self.operation('start', {'e':event})

    def dialog(self, event):
        return self.operation('trace', {'k':'dialog', 'd':{'c':self.events[event]['dialog']}})

    def callback(self, event):
        return self.operation('callback', {'e':event, 'token':'ui:%s' % event,
            'source_occurrence':[0, self.state['story']['event_occurrences'][str(event)]]})

    def settle(self, admission, actual):
        return dict((key, copy.deepcopy(actual[key])) for key in ('t','s','h','x','w')) | {'r':{}}, {
            'profile':copy.deepcopy(self.state['profile']), 'notices':[], 'granted':[]}

    def event_win(self):
        self.state['profile']['heroes']['24']['cf'] = 7
        self.state['profile']['heroes']['7']['cf'] = 22
        self.begin(7025)
        occurrence = self.call('story_occurrence_key', self.state, 7025)
        self.state, _, _ = self.call('prepare_event_battle_gate', self.state, 7025, self.events, occurrence)
        request = {'t':2, 's':161, 'h':[24,7], 'd':{}}
        self.state, _ = self.call('prepare_event_battle_admission', self.state,
            request, self.tables['mission'], self.events, lambda:'independent-161')
        self.state, _, _, _ = self.call('prepare_event_battle_finish', self.state,
            dict(request, x=[24], w=1, e={}), self.settle, 'independent-161',
            self.tables['mission'], self.events)

    def special_source(self):
        self.begin(1129)
        self.dialog(1129)
        self.assertNotIn('special_city_stages', self.state['story'])
        key = self.call('story_occurrence_key', self.state, 1129)
        handoff = self.state['story']['event_handoffs'][key][0]
        self.state, _, changed = self.call('prepare_week_route_handoff', self.state,
            handoff, self.events, self.routes)
        self.assertTrue(changed)
        self.assertEqual(self.state['story']['route'], '10-6')
        # Original1140 has no dialog/UI/completeConds: genuine event start is
        # its completion boundary, unlike the later1132 dialogue/UI event.
        notices = self.begin(1140)
        self.assertIn(1140, self.state['completed_events'])
        self.assertEqual(self.state['story']['city_areas']['6']['stage'], {'cs':320,'sl':[[320]]})
        self.assertTrue(all(payload['sm'] is False for name,payload in notices
                            if name == 'get_all_area_info_reply'))
        return notices

    def stage_result(self, win):
        self.state, _ = self.call('prepare_stage_admission', self.state,
            {'t':1,'s':320,'h':[24,7],'d':{'a':6}}, self.tables['mission'],
            lambda:'independent-320')
        active = copy.deepcopy(self.state['battle']['active'])
        self.assertIn('special_city_stage_source', active)
        self.assertNotIn('city_stage_source', active)
        self.state, _, _, _ = self.call('prepare_stage_finish', self.state,
            {'t':1,'s':320,'h':[24,7],'x':[24],'w':win,'e':{}},
            self.tables['mission'], self.tables['city_data'], self.settle, active['fight_id'])

    def test_winning_party_survives_reload_and_uses_current_profile_at_terminal(self):
        self.event_win()
        self.assertEqual(self.state['profile']['heroes']['7']['cf'],22)
        self.assertNotIn(73,self.state['story'].get('cgs',[]))
        self.state = json.loads(json.dumps(self.state))
        self.state['battle']['receipts'] = []  # retained durable win proof is independent
        self.state['profile']['heroes']['24']['ef'] = 12345
        self.state['profile']['heroes']['7']['cf'] = 4
        self.state['profile']['lineup'] = [8]
        nonparty = copy.deepcopy(self.state['profile']['heroes']['8'])
        self.begin(7026)
        self.assertEqual(self.state['profile']['heroes']['7']['cf'],4)
        self.assertNotIn(73,self.state['story'].get('cgs',[]))
        notices = self.dialog(7026)
        self.assertEqual(self.state['profile']['heroes']['24']['ef'],12345)
        self.assertEqual(self.state['profile']['heroes']['8'],nonparty)
        self.assertEqual(self.state['profile']['heroes']['7']['cf'],100)
        self.assertIn(('updateCurFatigueValue',{'h':7,'v':100}), notices)
        self.assertIn(73,self.state['story']['cgs'])
        self.assertEqual(self.state['story']['blackcores'],{'3':1,'4':1})
        audit = self.state['story']['event_terminal_effect_audit']['0:7026:1'][0]
        self.assertEqual(audit['party'],[24,7])
        self.assertEqual([change['before'] for change in audit['changes']],[7,4])
        self.call('validate_event_terminal_state',self.state)
        committed = copy.deepcopy(self.state)
        self.assertEqual(self.dialog(7026),[])
        self.assertEqual(self.state,committed)

    def test_terminal_partial_invalid_party_never_commits_other_rewards(self):
        self.event_win(); self.begin(7026)
        self.state['profile']['heroes']['7']['cf'] = True
        before = copy.deepcopy(self.state)
        self.assertEqual(self.dialog(7026),[])
        self.assertEqual(self.state['profile'],before['profile'])
        self.assertEqual(self.state['story']['blackcores'],{})
        self.assertNotIn(73,self.state['story'].get('cgs',[]))
        self.assertIn(7026,self.state['processing_events'])
        self.assertFalse(self.state['story'].get('event_effect_receipts'))

    def test_special_original_table_win_requires_original_dialog_ui_before_free(self):
        self.special_source()
        self.state = json.loads(json.dumps(self.state))
        self.call('validate_special_city_stages',self.state)
        self.stage_result(1)
        area = self.state['story']['city_areas']['6']
        self.assertEqual(area['stage'],{'cs':0,'sl':[[320]]})
        self.assertEqual(area['st'][0],1)
        self.assertNotIn(3101,self.state['story']['battle_wins'])
        self.assertNotIn(4101,self.state['story']['battle_wins'])
        self.assertEqual(self.state['story']['city_values']['av'],22)
        self.assertEqual(self.state['profile']['heroes']['7']['cf'],95)
        self.assertEqual(self.tables['mission'][320]['successEvent'],(1132,))
        # Explicit helper-only terminal availability fixture. Full LocalProxy
        # producer/replay coverage is in the gateway tests, not asserted here.
        self.state['available_events'].append([1132,1])
        self.begin(1132); self.dialog(1132)
        self.assertEqual(self.state['story']['city_areas']['6']['st'][0],1)
        self.callback(1132)
        self.assertEqual(self.state['story']['city_areas']['6']['st'][0],1)
        self.operation('option',{'e':1132,'se':1133,'op':0})
        self.assertIn(1132,self.state['completed_events'])
        self.assertEqual(self.state['story']['city_areas']['6']['st'][0],0)
        self.call('expire_special_city_stages',self.state)
        self.assertEqual(self.state['story']['city_areas']['6']['stage'],{'cs':5101,'sl':[[5101]]})
        self.assertEqual(self.state['story']['city_areas']['6']['st'][0],0)

    def test_special_loss_and_exact_route_contract_have_no_invented_progress(self):
        for route in ('10','10-1','27-1'):
            with self.assertRaises(ValueError):
                self.call('resolve_special_city_stage',6,1,route,11,
                    self.tables['chapter_mission_data'],self.tables['mission'])
        self.special_source()
        before = copy.deepcopy(self.state)
        self.stage_result(0)
        self.assertEqual(self.state['profile'],before['profile'])
        self.assertEqual(self.state['story'],before['story'])
        self.assertNotIn(1132,dict(self.state['available_events']))
        self.assertNotIn(320,self.state['story']['battle_wins'])

    def test_original_readonly_rows_survive_real_effect_pipeline_and_json_resume(self):
        tables = dict(self.tables)
        chapters = self.tables['chapter_mission_data']
        tables['chapter_mission_data'] = {key:ReadOnlyOriginalRow(row)
                                           for key,row in chapters.items()}
        tables['mission'] = dict(tables['mission'])
        native_mission = dict(tables['mission'][320])
        # Original native rows contain UTF-8 bytes and a nonintegral float.
        native_mission['name'] = native_mission['name'].encode('utf-8')
        tables['mission'][320] = ReadOnlyOriginalRow(native_mission)
        tables['event_content'] = {key:ReadOnlyOriginalRow(row)
                                   for key,row in self.events.items()}
        self.tables, self.events = tables, tables['event_content']
        original_row = copy.deepcopy(native_mission)
        self.special_source()
        self.state = json.loads(json.dumps(self.state))
        self.call('validate_special_city_stages', self.state)
        snapshot = self.state['story']['special_city_stages']['contexts']['6']['descriptor']['missions']['320']
        self.assertIs(type(snapshot), dict)
        self.assertIs(type(snapshot['name']), str)
        self.assertEqual(snapshot['yazhi_factor'],native_mission['yazhi_factor'])
        self.assertEqual(native_mission,original_row)
        self.stage_result(1)
        self.assertEqual(self.state['story']['city_areas']['6']['stage']['cs'],0)
        self.assertEqual(self.state['story']['battle_wins'],[320])


class IndependentFlatTerminalStageTests(IndependentTerminalStageTests):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        source = ast.literal_eval(ast.parse(embedded_loader(ROOT/'runtime').splitlines()[0]).body[0].value)
        real_import = builtins.__import__
        def imports(name, globals=None, locals=None, fromlist=(), level=0):
            if name.startswith('offline_'):
                raise ImportError('production flat namespace')
            return real_import(name,globals,locals,fromlist,level)
        namespace = {'__name__':'independent_flat_terminal_stage',
            '__builtins__':dict(vars(builtins),__import__=imports)}
        exec(compile(source,'<actual-embedded-terminal-stage>','exec'),namespace,namespace)
        cls.api = namespace


if __name__ == '__main__': unittest.main()
