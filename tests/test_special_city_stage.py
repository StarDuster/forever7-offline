"""Original selector/route consumers with synthetic host results, not native wins."""
import copy
import hashlib
import json
from pathlib import Path
import sys
import unittest
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'runtime'))
import offline_special_city_stage as special_stage
from offline_special_city_stage import (resolve_special_city_stage,
    apply_special_city_stage_effects, special_city_stage_token,
    validate_special_city_stages, validate_special_city_stage_source,
    expire_special_city_stages, refresh_special_city_stages)
from offline_stage import prepare_stage_admission, prepare_stage_finish
from offline_story import initial_story_state
from offline_story_engine import begin_story_occurrence, prepare_story_operation
from offline_week import prepare_week_route_handoff, initial_week_state


class NativeTaggedLiteral:
    """Read-only non-dict cdata mapping whose deepcopy retains the wrapper."""
    def __init__(self, values):self.values = dict(values)
    def items(self):return list(self.values.items())
    def get(self, key, default=None):return self.values.get(key, default)
    def __getitem__(self, key):return self.values[key]
    def __iter__(self):return iter(self.values)
    def __len__(self):return len(self.values)
    def __deepcopy__(self, memo):return self


class DuplicateTaggedLiteral(NativeTaggedLiteral):
    def __init__(self, entries):self.entries = entries
    def items(self):return self.entries


def tagged_literals(value, byte_text=False):
    if isinstance(value, dict):
        return NativeTaggedLiteral({key:tagged_literals(item, byte_text) for key,item in value.items()})
    if isinstance(value, tuple):return tuple(tagged_literals(item, byte_text) for item in value)
    if isinstance(value, list):return [tagged_literals(item, byte_text) for item in value]
    if byte_text and isinstance(value, str):return value.encode('utf-8')
    return value


class SpecialCityStageTests(unittest.TestCase):
    def setUp(self):
        self.fixture=json.loads((ROOT/'tests/fixtures/special_city_stage_cdata.json').read_text())
        self.tables={name:{int(key):row for key,row in self.fixture[name].items()} for name in
            ('mission','event_content','notepad','reward_common','cg_data','city_data')}
        chapters={}
        for entry in self.fixture['chapter_mission_data']:
            row=copy.deepcopy(entry['row']);row['section']={int(key):value for key,value in row['section'].items()}
            chapters[tuple(entry['key'])]=row
        self.tables['chapter_mission_data']=chapters
        self.events=self.tables['event_content']
        for row in self.events.values():
            if 'areaSpecialStage' in row:
                row['areaSpecialStage']={int(key):value for key,value in row['areaSpecialStage'].items()}
        self.state={'story':initial_story_state([8]),'day':{'stock_day':0},
            'battle':{'version':1,'active':None,'receipts':[]},'week_protocol':initial_week_state(),
            'available_events':[],'processing_events':[],'completed_events':[8],
            'event_traces':[],'conditions':[],
            'profile':{'economy':{'version':1,'level':50,'money':0,'exp':0},
                'heroes':{'24':{'cf':100,'ef':0}}}}
        self.state['story'].update(route='10',week=1,date=0,emergency=False,
            city_values={'av':24,'fv':50,'rv':0,'dv':0,'bf':0,'ev':0},
            city_areas={'6':{'id':6,'st':[0,False,False],'lv':1,'bd':{},
                'stage':{'cs':5101,'sl':[[5101]]}}})
        self.route()
        self.activate()

    def begin(self,event):
        self.state['processing_events']=sorted(set(self.state['processing_events'])|{event})
        begin_story_occurrence(self.state,event,self.events,{})
        self.state,notices=prepare_story_operation(self.state,'start',{'e':event},self.events,{},self.tables)
        return notices

    def route(self):
        self.begin(1129)
        self.assertEqual(self.state['story']['route'],'10')
        self.assertNotIn(1129,self.state['completed_events'])
        self.state,notices=prepare_story_operation(self.state,'trace',{'k':'dialog','d':{'c':1129}},self.events,{},self.tables)
        self.assertIn(1129,self.state['completed_events'])
        handoffs=[handoff for values in self.state['story']['event_handoffs'].values() for handoff in values if handoff['kind']=='route']
        self.state,notices,changed=prepare_week_route_handoff(self.state,handoffs[-1],self.events,self.fixture['story_route'])
        self.assertTrue(changed)
        self.assertEqual(self.state['story']['route'],'10-6')

    def activate(self):
        notices=self.begin(1140)
        self.assertIn(1140,self.state['completed_events'],self.state['story'].get('pending_effects'))
        self.assertEqual(self.state['story']['city_areas']['6']['stage'],{'cs':320,'sl':[[320]]})
        return notices

    def admit(self,state=None,identity='host-special320'):
        return prepare_stage_admission(state or self.state,
            {'t':1,'s':320,'h':[24],'d':{'a':6}},self.tables['mission'],lambda:identity)

    def finish(self,state,win=1,settler=None):
        active=state['battle']['active']
        actual={key:copy.deepcopy(active['request'][key]) for key in ('t','s','h')}
        actual.update(w=win,x=[],e={})
        def settle(admission,result):
            reply={key:copy.deepcopy(result[key]) for key in ('t','s','h','w','x')}
            reply['r']={}
            return reply,{'profile':copy.deepcopy(state['profile']),'notices':[],'granted':[]}
        return prepare_stage_finish(state,actual,self.tables['mission'],self.tables['city_data'],settler or settle,active['fight_id'])

    def test_native_tagged_resolver_preserves_typed_lookup_and_json_safe_snapshot(self):
        chapters = tagged_literals(self.tables['chapter_mission_data'])
        missions = tagged_literals(self.tables['mission'])
        self.assertNotIsInstance(chapters.get((6,0,'10-6',11)),dict)
        self.assertIs(copy.deepcopy(missions.get(320)),missions.get(320))
        resolved = resolve_special_city_stage(6,1,'10-6',11,chapters,missions)
        plain = resolve_special_city_stage(6,1,'10-6',11,self.tables['chapter_mission_data'],self.tables['mission'])
        self.assertEqual(resolved,plain)
        self.assertEqual(resolved,json.loads(json.dumps(resolved,ensure_ascii=True)))
        self.assertEqual(resolved['missions']['320']['yazhi_factor'],1.22666666667)
        self.assertIsInstance(resolved['missions']['320']['name'],str)
        self.assertEqual(chapters.items()[0][0],(6,0,'10-6',11))

    def test_native_utf8_bytes_and_nested_mappings_match_plain_original_literals(self):
        chapters = tagged_literals(self.tables['chapter_mission_data'],True)
        # Model Python2 UTF-8 route bytes inside the tuple lookup key as well.
        chapters = NativeTaggedLiteral({(6,0,b'10-6',11):chapters.get((6,0,'10-6',11))})
        missions = tagged_literals(self.tables['mission'],True)
        resolved = resolve_special_city_stage(6,1,'10-6',11,chapters,missions)
        plain = resolve_special_city_stage(6,1,'10-6',11,self.tables['chapter_mission_data'],self.tables['mission'])
        self.assertEqual(resolved,plain)
        self.assertEqual(resolved['missions']['320']['name'],self.tables['mission'][320]['name'])
        self.assertEqual(resolved,json.loads(json.dumps(resolved,ensure_ascii=True)))

    def test_native_tagged_real_event_source_save_reload_admission_and_result(self):
        self.tables['chapter_mission_data'] = tagged_literals(self.tables['chapter_mission_data'])
        self.tables['mission'] = tagged_literals(self.tables['mission'],True)
        events = dict(self.events)
        events[1140] = tagged_literals(events[1140])
        self.events = events
        self.tables['event_content'] = events
        notices = self.begin(1140)
        self.assertIn(1140,self.state['completed_events'],self.state['story'].get('pending_effects'))
        self.assertTrue(any(name == 'get_area_stages_reply' for name,_ in notices))
        self.state = json.loads(json.dumps(self.state,ensure_ascii=True))
        validate_special_city_stages(self.state)
        admitted,_ = self.admit()
        admitted = json.loads(json.dumps(admitted,ensure_ascii=True))
        validate_special_city_stages(admitted)
        validate_special_city_stage_source(admitted,admitted['battle']['active'],self.tables['mission'])
        won,_,_,changed = self.finish(admitted)
        self.assertTrue(changed)
        self.assertEqual(won['story']['city_areas']['6']['stage']['cs'],0)
        self.assertEqual(won['profile']['heroes']['24']['cf'],95)

    def test_native_mapping_snapshot_is_deep_and_shared_aliases_are_not_cycles(self):
        mission = copy.deepcopy(self.tables['mission'][320])
        shared = [1,NativeTaggedLiteral({'text':'original'})]
        mission['first_alias'] = shared
        mission['second_alias'] = shared
        mission['nested_map'] = NativeTaggedLiteral({0:NativeTaggedLiteral({'text':'unchanged'})})
        wrapped = NativeTaggedLiteral(mission)
        resolved = resolve_special_city_stage(6,1,'10-6',11,self.tables['chapter_mission_data'],{320:wrapped})
        snapshot = resolved['missions']['320']
        snapshot['first_alias'][1]['text'] = 'changed'
        snapshot['nested_map']['0']['text'] = 'changed'
        self.assertEqual(shared[1].get('text'),'original')
        self.assertEqual(mission['nested_map'].get(0).get('text'),'unchanged')
        self.assertEqual(snapshot['second_alias'][1]['text'],'original')

    def test_native_mapping_rejects_nonliteral_cycles_invalid_utf8_and_nonfinite(self):
        for bad in (object(),{1},float('nan'),float('inf'),b'\xff'):
            mission = copy.deepcopy(self.tables['mission'][320])
            mission['name'] = bad
            with self.subTest(bad=type(bad).__name__):
                with self.assertRaises(ValueError):
                    resolve_special_city_stage(6,1,'10-6',11,self.tables['chapter_mission_data'],{320:NativeTaggedLiteral(mission)})
        mission = copy.deepcopy(self.tables['mission'][320])
        cycle = []
        cycle.append(cycle)
        mission['name'] = cycle
        with self.assertRaisesRegex(ValueError,'Cyclic'):
            resolve_special_city_stage(6,1,'10-6',11,self.tables['chapter_mission_data'],{320:NativeTaggedLiteral(mission)})

    def test_native_mapping_rejects_duplicate_and_json_ambiguous_keys(self):
        for bad in (DuplicateTaggedLiteral([('name','first'),('name','second')]),
                    NativeTaggedLiteral({1:'int','1':'text'}),
                    DuplicateTaggedLiteral([(b'name','first'),('name','second')])):
            mission = copy.deepcopy(self.tables['mission'][320])
            mission['nested'] = bad
            with self.assertRaisesRegex(ValueError,'Duplicate or ambiguous'):
                resolve_special_city_stage(6,1,'10-6',11,self.tables['chapter_mission_data'],{320:NativeTaggedLiteral(mission)})
        chapters = DuplicateTaggedLiteral(list(self.tables['chapter_mission_data'].items()) * 2)
        with self.assertRaises(ValueError):
            resolve_special_city_stage(6,1,'10-6',11,chapters,self.tables['mission'])

    def test_original_fixture_and_exact_selector_not_mission_identifier(self):
        for name,digest in self.fixture['sha256'].items():
            self.assertEqual(hashlib.sha256((ROOT/name).read_bytes()).hexdigest(),digest)
        resolved=resolve_special_city_stage(6,1,'10-6',11,self.tables['chapter_mission_data'],self.tables['mission'])
        self.assertEqual(resolved['key'],[6,0,'10-6',11])
        self.assertEqual(resolved['groups'],[[320]])
        self.assertNotIn(11,self.tables['mission'])
        for route,status,selector in (('10',1,11),('10-1',1,11),('10-6',0,11),('10-6',5,11),('10-6',1,320)):
            with self.assertRaises(ValueError):resolve_special_city_stage(6,status,route,selector,self.tables['chapter_mission_data'],self.tables['mission'])

    def test_selector_resolution_rejects_mismatch_duplicate_and_unreleased(self):
        wanted=(6,0,'10-6',11)
        for mutation in ('key','duplicate','section','mission_area','mission_release','mission_mode'):
            chapters=copy.deepcopy(self.tables['chapter_mission_data']);missions=copy.deepcopy(self.tables['mission'])
            if mutation=='key':chapters[wanted]['route']='10'
            if mutation=='duplicate':chapters[(6,0,'10-6',12)]=copy.deepcopy(chapters[wanted])
            if mutation=='section':chapters[wanted]['section'][1]=[320]
            if mutation=='mission_area':missions[320]['ch']=4
            if mutation=='mission_release':missions[320]['release']=0
            if mutation=='mission_mode':missions[320]['system_type']=2
            with self.assertRaises(ValueError):resolve_special_city_stage(6,1,'10-6',11,chapters,missions)

    def test_true_source_starts_original_stage_and_win_does_not_free_or_follow_edges(self):
        before=copy.deepcopy(self.state)
        admitted,changed=self.admit()
        self.assertTrue(changed)
        active=admitted['battle']['active']
        self.assertEqual(active['request'],{'t':1,'s':320,'h':[24],'d':{'a':6}})
        self.assertEqual(active['costs'],{'actions':2,'fatigue':5})
        self.assertNotIn('city_stage_source',active)
        self.assertIn('special_city_stage_source',active)
        self.assertEqual(admitted['profile'],before['profile'])
        won,reply,effects,changed=self.finish(admitted)
        self.assertEqual(won['story']['city_values']['av'],22)
        self.assertEqual(won['profile']['heroes']['24']['cf'],95)
        self.assertEqual(won['story']['city_areas']['6']['st'],[1,False,False])
        self.assertEqual(won['story']['city_areas']['6']['stage']['cs'],0)
        self.assertEqual(won['story']['battle_wins'],[320])
        self.assertNotIn(1132,won['completed_events'])
        self.assertNotIn(3101,won['story']['battle_wins']);self.assertNotIn(4101,won['story']['battle_wins'])
        self.assertNotIn('condition_mission_edges',won['story'])
        self.assertEqual(self.state,before)

    def test_loss_and_duplicate_win_do_not_recharge(self):
        admitted,_=self.admit()
        lost,reply,effects,changed=self.finish(admitted,0)
        self.assertEqual(reply['r'],{})
        self.assertEqual(lost['profile'],self.state['profile'])
        self.assertEqual(lost['story'],self.state['story'])
        retry,_=self.admit(lost,'host-retry')
        won,reply,effects,changed=self.finish(retry)
        result={key:retry['battle']['active']['request'][key] for key in ('t','s','h')};result.update(w=1,x=[],e={})
        duplicate,reply,effects,changed=prepare_stage_finish(won,result,self.tables['mission'],self.tables['city_data'],
            lambda *args:self.fail('duplicate settlement'),retry['battle']['active']['fight_id'])
        self.assertFalse(changed);self.assertEqual(duplicate,won)

    def test_real_low_force_cost_and_owned_available_party(self):
        poor=copy.deepcopy(self.state);poor['story']['city_values']['fv']=4
        admitted,_=self.admit(poor)
        self.assertEqual(admitted['battle']['active']['costs'],{'actions':2,'fatigue':25})
        won,reply,effects,changed=self.finish(admitted)
        self.assertEqual(won['profile']['heroes']['24']['cf'],75)
        for alteration in ('banned','unowned','fatigue','locked'):
            invalid=copy.deepcopy(poor)
            if alteration=='banned':invalid['story']['banned_heroes']={'24':True}
            if alteration=='unowned':invalid['profile']['heroes']={}
            if alteration=='fatigue':invalid['profile']['heroes']['24']['cf']=24
            if alteration=='locked':invalid['story']['city_areas']['6']['st'][2]=True
            with self.assertRaises(ValueError):self.admit(invalid)

    def test_result_rejects_source_day_route_week_lock_party_and_catalog_drift(self):
        admitted,_=self.admit()
        with self.assertRaises(ValueError):validate_special_city_stage_source(admitted,admitted['battle']['active'],{})
        for alteration in ('day','route','week','receipt','lock','ban','unowned','conflict','mission'):
            invalid=copy.deepcopy(admitted)
            if alteration=='day':invalid['day']['stock_day']=1
            if alteration=='route':invalid['story']['route']='10'
            if alteration=='week':invalid['story']['week']=2
            if alteration=='receipt':invalid['story']['event_effect_receipts'].clear()
            if alteration=='lock':invalid['story']['city_areas']['6']['st'][2]=True
            if alteration=='ban':invalid['story']['banned_heroes']={'24':True}
            if alteration=='unowned':invalid['profile']['heroes'].clear()
            if alteration=='conflict':invalid['battle']['active']['city_stage_source']={}
            if alteration=='mission':invalid['story']['special_city_stages']['contexts']['6']['descriptor']['missions']['320']['va']=0
            before=copy.deepcopy(invalid)
            with self.assertRaises(ValueError):self.finish(invalid)
            self.assertEqual(invalid,before)

    def test_missing_actual_route_and_effect_proof_cannot_admit(self):
        for alteration in ('route_event','handoff','effect_event','receipt'):
            invalid=copy.deepcopy(self.state)
            if alteration=='route_event':invalid['completed_events'].remove(1129)
            if alteration=='handoff':invalid['week_protocol']['consumed_handoffs']=[]
            if alteration=='effect_event':invalid['completed_events'].remove(1140)
            if alteration=='receipt':invalid['story']['event_effect_receipts']={}
            with self.assertRaises(ValueError):self.admit(invalid)
        state=copy.deepcopy(self.state);state['week_protocol']['consumed_handoffs']=[]
        with self.assertRaises(ValueError):apply_special_city_stage_effects(state,1140,self.events[1140],self.tables,'another-source')

    def test_json_resume_source_generation_and_projection_ownership(self):
        validate_special_city_stages(self.state)
        resumed=json.loads(json.dumps(self.state))
        admitted,_=self.admit(resumed)
        validate_special_city_stages(admitted)
        with self.assertRaises(ValueError):expire_special_city_stages(admitted,'11-1')
        previous=special_city_stage_token(self.state)
        row=copy.deepcopy(self.events[1140])
        apply_special_city_stage_effects(self.state,1140,row,self.tables,'new-genuine-component-source')
        self.assertNotEqual(previous,special_city_stage_token(self.state))
        # Equal-valued later explicit refresh revokes projection ownership.
        apply_special_city_stage_effects(self.state,900001,{'release':True,'refreshMission':True},self.tables,'refresh')
        expire_special_city_stages(self.state,'11-1')
        self.assertEqual(self.state['story']['city_areas']['6']['stage'],{'cs':320,'sl':[[320]]})
        self.assertNotIn('6',self.state['story']['special_city_stages']['contexts'])
        validate_special_city_stages({'story':{}})

    def test_actual_area_free_and_later_stage_writes_survive_route_departure(self):
        admitted,_=self.admit();won,reply,effects,changed=self.finish(admitted)
        self.state=won
        # Terminal availability is gateway-owned; this fixture models its
        # already-admitted event, then runs actual dialog and UI gates.
        self.begin(1132)
        self.state,notices=prepare_story_operation(self.state,'trace',{'k':'dialog','d':{'c':1132}},self.events,{},self.tables)
        self.assertNotIn(1132,self.state['completed_events'])
        self.assertEqual(self.state['story']['city_areas']['6']['st'][0],1)
        self.state,notices=prepare_story_operation(self.state,'callback',{'e':1132,'token':'ui:1132'},self.events,{},self.tables)
        # 1132 has a successor; choose the actual original continuation.
        self.state,notices=prepare_story_operation(self.state,'option',{'e':1132,'se':1133},self.events,{},self.tables)
        self.assertIn(1132,self.state['completed_events'])
        self.assertEqual(self.state['story']['city_areas']['6']['st'][0],0)
        profile=copy.deepcopy(self.state['profile'])
        expire_special_city_stages(self.state,'11-1')
        self.assertEqual(self.state['story']['city_areas']['6']['stage'],{'cs':5101,'sl':[[5101]]})
        self.assertEqual(self.state['story']['city_areas']['6']['st'][0],0)
        self.assertEqual(self.state['profile'],profile)
        self.assertEqual(self.state['story']['battle_wins'],[320])


if __name__=='__main__':unittest.main()
