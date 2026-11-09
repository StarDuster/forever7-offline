"""Original day5 entry with read-only cdata rows; finite host fixture, not playthrough."""
import ast
import builtins
import copy
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.dont_write_bytecode = True
sys.path[:0] = [str(ROOT/'runtime'),str(ROOT/'tools'),str(ROOT/'analysis/research-agent'),str(ROOT/'tests')]
import offline_huisu as candidate
if Path(candidate.__file__).resolve() != (ROOT/'runtime/offline_huisu.py').resolve():
    raise RuntimeError('Live proof requires the current runtime module')
import offline_story_engine as engine
import offline_day as day_api
from test_offline_event_effects import original_tables, base_state
from read_data_table import read
from read_literal_marshal import read as read_marshal


class ReadOnlyNativeRow:
    """Non-dict mapping; deepcopy identity is deliberately not normalization."""
    def __init__(self, values):self.values = dict(values)
    def items(self):return list(self.values.items())
    def get(self,key,default=None):return self.values.get(key,default)
    def __getitem__(self,key):return self.values[key]
    def __len__(self):return len(self.values)
    def __deepcopy__(self,memo):return self


class DuplicateNativeRow(ReadOnlyNativeRow):
    def __init__(self,pairs):self.pairs = pairs
    def items(self):return self.pairs
    def __len__(self):return len(self.pairs)


class HuisuNativeRowTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.api = dict(vars(candidate),prepare_story_operation=engine.prepare_story_operation,
            begin_story_occurrence=engine.begin_story_occurrence,refresh_story_events=engine.refresh_story_events,
            prepare_gateway_day_operation=day_api.prepare_gateway_day_operation)
        cls.events = read(ROOT/'analysis/decompiled/event_content.py')
        cls.triggers = read(ROOT/'analysis/decompiled/event_condition.py')
        cls.original_rows = read_marshal(ROOT/'analysis/android640-scripts/com/data/cdata/story_dream.marshal')
        cls.original_tables = original_tables()

    def setUp(self):
        # Explicit finite history:6379 was completed before this boundary.
        # No lookup or candidate code grants it,6380,6383,or their successors.
        events = {e:self.events[e] for e in (6380,6383,6395,6396,6397)}
        triggers = {e:self.triggers[e] for e in events if e in self.triggers}
        self.row = ReadOnlyNativeRow(self.original_rows[('20',5)])
        self.tables = dict(self.original_tables,event_content=events,event_condition=triggers,
            story_dream={('20',5):self.row})
        self.state = base_state(self.tables)
        self.state.update(event_traces=[],conditions=[[101,0]],completed_events=[6379],
            day=dict(day_api.initial_day_state(),stock_day=5),battle={'version':1,'active':None,'receipts':[]})
        self.state['story'].update(week=2,date=5,route='20',emergency=False,
            city_values={'av':24,'fv':50,'rv':0,'dv':0,'bf':0,'ev':0})

    def call(self,name,*args,**kwargs):return self.api[name](*args,**kwargs)
    def reserve(self,state=None,tables=None,**kwargs):
        return self.call('prepare_huisu_operation',state or self.state,'requestStoryhuisu',{},
            tables or self.tables,operation_id='owner-A:actual-day5-entry',**kwargs)
    def rest(self):
        self.state,_,_,_ = self.call('prepare_gateway_day_operation',self.state,'statusCheck',{'s':'nextday'},[],stock_day=5)
        self.state,_,_,_ = self.call('prepare_gateway_day_operation',self.state,'updateEventCondClient',{'c':102,'v':'4'})
    def start(self,event):
        self.call('refresh_story_events',self.state,self.tables['event_condition'],self.tables['event_content'])
        self.assertIn(event,dict(self.state['available_events']))
        self.call('begin_story_occurrence',self.state,event,self.tables['event_content'],self.tables['event_condition'])
        self.state['available_events']=[pair for pair in self.state['available_events'] if pair[0] != event]
        self.state['processing_events'].append(event)
        self.story('start',{'e':event})
    def story(self,op,args):
        self.state,notices = self.call('prepare_story_operation',self.state,op,args,
            self.tables['event_content'],self.tables['event_condition'],self.tables)
        return notices

    def test_original_readonly_day5_row_extracts_only_two_ids_without_completion(self):
        self.assertNotIsInstance(self.row,dict)
        self.assertIs(copy.deepcopy(self.row),self.row)
        before = copy.deepcopy(self.state)
        selected = self.call('_hs_table_entry',self.state,self.tables)
        self.assertEqual(selected,{'event':6380,'goodnight_event':6383})
        self.assertIsInstance(selected,dict)
        entered,notices,changed,diagnostic = self.reserve()
        self.assertTrue(changed,diagnostic)
        self.assertEqual([name for name,_ in notices],['syncRoute','syncHuiSuData'])
        self.assertEqual(entered['story']['route20_huisu']['entry_event'],6380)
        self.assertEqual(entered['story']['route20_huisu']['night_event'],6383)
        self.assertEqual(entered['story']['route20_huisu']['phase'],'entering')
        self.assertEqual(entered['completed_events'],[6379])
        self.assertEqual(entered['available_events'],[])
        self.assertEqual(entered['processing_events'],[])
        self.assertEqual(entered['profile'],before['profile'])
        self.assertEqual(self.state,before)
        reloaded = json.loads(json.dumps(entered))
        self.call('validate_huisu_document',reloaded)
        repeated,_,changed,diagnostic = self.reserve(reloaded)
        self.assertFalse(changed);self.assertTrue(diagnostic['replay'])
        self.assertEqual(repeated,reloaded)

    def test_actual_original_entry_still_requires_rest_dialog_and_successor_choice(self):
        self.state,_,_,diagnostic = self.reserve()
        before = copy.deepcopy(self.state)
        with self.assertRaises(ValueError):
            self.call('begin_story_occurrence',self.state,6380,self.tables['event_content'],self.tables['event_condition'])
        self.assertEqual(self.state,before)
        self.rest();self.start(6380)
        self.assertNotIn(6380,self.state['completed_events'])
        self.story('trace',{'k':'dialog','d':{'c':6380}})
        self.assertNotIn(6380,self.state['completed_events'])
        self.assertEqual(self.state['story']['route20_huisu']['phase'],'entering')
        self.story('option',{'e':6380,'se':6395})
        self.assertIn(6380,self.state['completed_events'])
        self.assertEqual(self.state['story']['route20_huisu']['phase'],'active')
        self.assertIn(6395,self.state['processing_events'])
        self.story('trace',{'k':'dialog','d':{'c':6395}})
        self.assertIn(6395,self.state['completed_events'])
        self.assertNotIn(6383,self.state['completed_events'])
        self.assertEqual(self.state['story']['date'],5)

    def test_real_night6383_remains_gated_by_rest_intent_dialog_and_choice(self):
        self.state,_,_,_ = self.reserve();self.rest();self.start(6380)
        self.story('trace',{'k':'dialog','d':{'c':6380}})
        self.story('option',{'e':6380,'se':6395})
        self.story('trace',{'k':'dialog','d':{'c':6395}})
        self.call('refresh_story_events',self.state,self.tables['event_condition'],self.tables['event_content'])
        self.assertNotIn(6383,dict(self.state['available_events']))
        self.rest()
        self.call('mark_huisu_nextday',self.state,'owner-A:night-rest',self.call('huisu_token',self.state))
        self.start(6383)
        self.assertNotIn(6383,self.state['completed_events'])
        self.story('trace',{'k':'dialog','d':{'c':6383}})
        self.assertNotIn(6383,self.state['completed_events'])
        self.story('option',{'e':6383,'se':6396})
        self.assertIn(6383,self.state['completed_events'])
        self.assertIn(6396,self.state['processing_events'])
        self.story('trace',{'k':'dialog','d':{'c':6396}})
        self.assertIn(6396,self.state['completed_events'])
        self.assertEqual(self.state['story']['date'],5)
        self.assertIsNone(self.call('huisu_day_guard',self.state))

    def test_missing_original_predecessor_busy_emergency_and_stale_source_reject(self):
        for alteration in ('predecessor','busy','emergency','stale','legacy'):
            state = copy.deepcopy(self.state)
            kwargs = {}
            if alteration == 'predecessor':state['completed_events']=[]
            elif alteration == 'busy':state['processing_events']=[777]
            elif alteration == 'emergency':state['story']['emergency']=True
            elif alteration == 'legacy':state['completed_events'].append(6380)
            else:
                kwargs['source_token']=dict(self.call('huisu_request_source',state),week=99)
            before = copy.deepcopy(state)
            entered,notices,changed,diagnostic = self.reserve(state,**kwargs)
            self.assertFalse(changed,diagnostic)
            self.assertEqual(entered,before);self.assertEqual(notices,[])
            self.assertNotIn('route20_huisu',entered['story'])

    def test_scalar_type_missing_row_and_duplicate_supported_field_fail_closed(self):
        for field,value in (('event',True),('event','6380'),('event',object()),('goodnight_event',None),('goodnight_event',False),('goodnight_event',6383.0)):
            row = dict(self.original_rows[('20',5)])
            row[field] = value
            tables = dict(self.tables,story_dream={('20',5):ReadOnlyNativeRow(row)})
            entered,notices,changed,diagnostic = self.reserve(tables=tables)
            self.assertFalse(changed);self.assertEqual(diagnostic['pending'],'no_executable_huisu_table_entry')
            self.assertEqual(entered,self.state);self.assertEqual(notices,[])
        for row in (object(),[('event',6380)],DuplicateNativeRow([('event',6380),('event',6380),('goodnight_event',6383)])):
            tables = dict(self.tables,story_dream={('20',5):row})
            entered,_,changed,diagnostic = self.reserve(tables=tables)
            self.assertFalse(changed);self.assertEqual(entered,self.state)
            self.assertEqual(diagnostic['pending'],'no_executable_huisu_table_entry')

    def test_exact_tuple_lookup_fallback_and_unreleased_original_entry_stay_guarded(self):
        state = copy.deepcopy(self.state);state['story']['route']='20-5'
        entered,_,changed,diagnostic = self.reserve(state)
        self.assertTrue(changed,diagnostic)
        self.assertEqual(entered['story']['route20_huisu']['route'],'20-5')
        self.assertEqual(entered['story']['route20_huisu']['entry_event'],6380)
        for table_name in ('event_content','event_condition'):
            tables = dict(self.tables)
            tables[table_name] = copy.deepcopy(tables[table_name])
            tables[table_name][6380]['release'] = False
            entered,_,changed,diagnostic = self.reserve(tables=tables)
            self.assertFalse(changed);self.assertEqual(entered,self.state)
            self.assertEqual(diagnostic['pending'],'original_huisu_entry_unavailable')

    def test_unconsumed_metadata_not_copied_and_canonical_state_mapping_rejected(self):
        row = dict(self.original_rows[('20',5)],unused_native_metadata=object())
        tables = dict(self.tables,story_dream={('20',5):ReadOnlyNativeRow(row)})
        entered,_,changed,diagnostic = self.reserve(tables=tables)
        self.assertTrue(changed,diagnostic)
        json.dumps(entered)
        self.assertNotIn('unused_native_metadata',entered['story']['route20_huisu'])
        invalid = ReadOnlyNativeRow(entered['story']['route20_huisu'])
        with self.assertRaises(ValueError):self.call('validate_huisu_state',invalid)
        self.assertIs(self.row.values['event'],self.original_rows[('20',5)]['event'])


class FlatHuisuNativeRowTests(HuisuNativeRowTests):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        from patch_bootstrap import embedded_loader
        assignment = ast.parse(embedded_loader(ROOT/'runtime').splitlines()[0]).body[0]
        source = ast.literal_eval(assignment.value)
        original = (ROOT/'runtime/offline_huisu.py').read_text(encoding='ascii')
        if source.count(original) != 1:raise RuntimeError('Expected current live huisu source in actual loader')
        real_import = builtins.__import__
        def imports(name,globals=None,locals=None,fromlist=(),level=0):
            if name.startswith('offline_'):raise ImportError('No host modules in actual live flat test')
            return real_import(name,globals,locals,fromlist,level)
        cls.api = {'__builtins__':dict(vars(builtins),__import__=imports),'__name__':'actual_live_huisu_flat'}
        exec(compile(source,'<actual-live-flat-huisu>','exec'),cls.api,cls.api)


if __name__ == '__main__':unittest.main()
