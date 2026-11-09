"""Host result fixtures; never a native victory or natural route27 history."""
import builtins
import copy
import hashlib
import json
from pathlib import Path
import sys
import unittest
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'runtime'))
import offline_chapter_campaign as campaign
from offline_stage import prepare_stage_admission, prepare_stage_finish, refresh_condition_city_missions


class Tagged:
    def __init__(self, value): self.value = value
    def items(self): return list(self.value.items())
    def get(self, key, default=None): return self.value.get(key,default)


def tagged(value):
    if type(value) is dict: return Tagged({key:tagged(item) for key,item in value.items()})
    if type(value) is list: return [tagged(item) for item in value]
    if type(value) is str: return value.encode('utf-8')
    return value


class ChapterCampaignTests(unittest.TestCase):
    def setUp(self):
        self.fixture=json.loads((ROOT/'tests/fixtures/chapter_campaign_cdata.json').read_text())
        self.tables={name:{int(key):value for key,value in self.fixture[name].items()} for name in ('mission','city_data','event_content')}
        self.tables['chapter_mission_data']={}
        for entry in self.fixture['chapter_mission_data']:
            row=entry['row'];row['section']={int(key):value for key,value in row['section'].items()}
            self.tables['chapter_mission_data'][tuple(entry['key'])]=row
        self.state={'story':{'week':1,'route':'1','emergency':False,'battle_wins':[], 'current_mission_wins':[],
            'city_values':{'av':24,'fv':100},'city_areas':{'1':{'id':1,'st':[0,False,False]},'2':{'id':2,'st':[1,False,False], 'stage':{'cs':1101,'sl':[[1101]]}}}},
            'day':{'stock_day':0},'completed_events':[],
            'week_protocol':{'transition':{'id':'actual-host-week','operation':'handleResetWeekAsk','source_week':0,'target_week':1},'consumed_handoffs':[]},
            'battle':{'version':1,'active':None,'receipts':[]},'profile':{'economy':{'level':50},'heroes':{'24':{'cf':100}}}}

    def refresh(self,state=None):
        return campaign.refresh_normal_chapters(state or self.state,self.tables)

    def admit(self,state,scene=None,area=2):
        scene=scene or state['story']['city_areas'][str(area)]['stage']['cs']
        return prepare_stage_admission(state,{'t':1,'s':scene,'h':[24],'d':{'a':area}},self.tables['mission'],lambda:'host-%s-%s'%(scene,len(state['battle']['receipts'])))[0]

    def finish(self,state,win=1):
        active=state['battle']['active']
        result={key:copy.deepcopy(active['request'][key]) for key in ('t','s','h')};result.update(w=win,x=[],e={})
        def settle(active,result):
            reply={key:copy.deepcopy(result[key]) for key in ('t','s','h','w','x')};reply['r']={}
            return reply,{'profile':copy.deepcopy(state['profile']),'notices':[],'granted':[]}
        return prepare_stage_finish(state,result,self.tables['mission'],self.tables['city_data'],settle,active['fight_id'])

    def route27(self,locked=False):
        # Modeled genuine prehistory. Event900001 is deliberately fixture-only,
        # not a claim that original route27 naturally unlocks area5.
        self.state['story'].update(route='27-1',event_history=[1424,900001],event_effect_receipts={'host-activation':900001})
        self.state['completed_events']=[1424,900001]
        self.state['week_protocol']['consumed_handoffs']=['route:1424']
        self.tables['event_content'][900001]={'release':True,'areaFight':[5]}
        self.state['story']['city_areas']['5']={'id':5,'st':[1,False,locked],'stage':{'cs':4101,'sl':[[4101]]}}
        self.refresh()
        return self.state

    def test_original_all_rows_shape_audit_and_resolution(self):
        counts={'selector0':0,'shape':0,'coc':0,'conditional':0,'unreleased_or_wrongch':0,'alias':0,'multi':0}
        resolved=0
        for key,row in self.tables['chapter_mission_data'].items():
            if key[3]:continue
            counts['selector0']+=1
            members=[scene for group in row['section'].values() for scene in group]
            if any(len(group)>1 for group in row['section'].values()):counts['multi']+=1
            rows=[self.tables['mission'][scene] for scene in members]
            if all(r.get('release')==1 and r.get('system_type')==1 and r.get('ch')==key[0] for r in rows):category='shape'
            elif key[0]==9:category='alias'
            elif all(r.get('system_type')==2 and r.get('type')==10 for r in rows):category='coc'
            elif key[1]==5:category='conditional'
            else:category='unreleased_or_wrongch'
            counts[category]+=1
            if category=='shape' and 1<=key[0]<=8:
                descriptor=campaign.resolve_normal_chapter(key[0],1 if key[1]==0 else 5,key[2],self.tables['chapter_mission_data'],self.tables['mission'])
                self.assertEqual(descriptor['key'],list(key));resolved+=1
            else:
                with self.assertRaises(ValueError):campaign.resolve_normal_chapter(key[0],1 if key[1]==0 else 5,key[2],self.tables['chapter_mission_data'],self.tables['mission'])
        self.assertEqual(counts,{'selector0':647,'shape':631,'coc':7,'conditional':6,'unreleased_or_wrongch':2,'alias':1,'multi':11})
        self.assertEqual(resolved,631) # Shape audit does not assert source playability.
        for path,digest in self.fixture['sha256'].items():self.assertEqual(hashlib.sha256((ROOT/path).read_bytes()).hexdigest(),digest)

    def test_fallback_missing_only_and_typed_schema(self):
        chapters=self.tables['chapter_mission_data'];missions=self.tables['mission']
        self.assertEqual(campaign.resolve_normal_chapter(5,1,'27-999',chapters,missions)['fallback_kind'],'base')
        self.assertEqual(campaign.resolve_normal_chapter(5,1,'unknown',chapters,missions)['fallback_kind'],'default')
        broken=copy.deepcopy(chapters);broken[(5,0,'27-999',0)]=copy.deepcopy(chapters[(5,0,'27',0)])
        broken[(5,0,'27-999',0)]['route']='27-999';broken[(5,0,'27-999',0)]['section'][0]=[401242]
        with self.assertRaises(ValueError):campaign.resolve_normal_chapter(5,1,'27-999',broken,missions)
        for area,status in ((True,1),(5,True),(9,1),(0,1)):
            with self.assertRaises(ValueError):campaign.resolve_normal_chapter(area,status,'27',chapters,missions)

    def test_native_tagged_utf8_float_and_json_stability(self):
        plain=campaign.resolve_normal_chapter(5,1,'27-1',self.tables['chapter_mission_data'],self.tables['mission'])
        wrapped=campaign.resolve_normal_chapter(5,1,'27-1',tagged(self.tables['chapter_mission_data']),tagged(self.tables['mission']))
        self.assertEqual(plain,wrapped);self.assertEqual(plain,json.loads(json.dumps(plain)))
        for bad in (object(),float('nan'),float('inf'),b'\xff',{1}):
            missions=copy.deepcopy(self.tables['mission']);missions[4129]['unexpected']=bad
            with self.assertRaises(ValueError):campaign.resolve_normal_chapter(5,1,'27-1',self.tables['chapter_mission_data'],missions)

    def test_fresh_week_and_legacy_without_fake_sources(self):
        before=copy.deepcopy(self.state);self.refresh()
        self.assertEqual(self.state['story']['city_areas']['2']['stage']['cs'],1101)
        self.assertEqual(self.state['completed_events'],[])
        self.assertIn('normal_chapter_source',self.admit(self.state)['battle']['active'])
        legacy=copy.deepcopy(before);legacy.pop('week_protocol');self.refresh(legacy)
        self.assertNotIn('normal_chapters',legacy['story'])
        self.assertNotIn('normal_chapter_source',self.admit(legacy)['battle']['active'])
        fake=copy.deepcopy(before);fake.pop('week_protocol');fake['story']['battle_wins']=[1101,1102]
        self.refresh(fake);self.assertNotIn('normal_chapters',fake['story'])

    def test_actual_host_results_route27_progress_costs_and_duplicate(self):
        state=self.route27();self.assertEqual(state['story']['city_areas']['5']['stage']['cs'],4129)
        self.assertNotIn(4130,self.tables['mission'][4129]['nextstagenums'])
        for scene in range(4129,4135):
            admitted=self.admit(state,scene,5)
            won,reply,effects,changed=self.finish(admitted)
            self.assertTrue(changed);self.assertEqual(won['story']['normal_chapters']['contexts']['5']['wins'],list(range(4129,scene+1)))
            actual={key:admitted['battle']['active']['request'][key] for key in ('t','s','h')};actual.update(w=1,x=[],e={})
            duplicate=prepare_stage_finish(won,actual,self.tables['mission'],self.tables['city_data'],lambda *args:self.fail('repeated reward'),admitted['battle']['active']['fight_id'])
            self.assertFalse(duplicate[3]);self.assertEqual(duplicate[0],won)
            state=json.loads(json.dumps(won));campaign.validate_normal_chapters(state)
        self.assertEqual(state['story']['city_areas']['5']['st'],[0,False,False])
        self.assertEqual(state['story']['city_areas']['5']['stage']['cs'],0)
        self.assertEqual(state['story']['city_values']['av'],12)
        self.assertEqual(state['profile']['heroes']['24']['cf'],70)
        self.assertNotIn(60096,state['completed_events']);self.assertNotIn(4101,state['story']['battle_wins'])

    def test_loss_retry_and_source_queue_fences(self):
        self.refresh();admitted=self.admit(self.state)
        lost,reply,effects,changed=self.finish(admitted,0)
        self.assertEqual(lost['story'],self.state['story']);self.assertEqual(lost['profile'],self.state['profile'])
        self.assertIsNotNone(self.admit(lost)['battle']['active'])
        token=campaign.normal_chapter_token(admitted)
        for change in ('day','route','week','lock','projection','receipt','team','mission'):
            state=copy.deepcopy(admitted);missions=copy.deepcopy(self.tables['mission'])
            if change=='day':state['day']['stock_day']=1
            if change=='route':state['story']['route']='2'
            if change=='week':state['story']['week']=2
            if change=='lock':state['story']['city_areas']['2']['st'][2]=True
            if change=='projection':state['story']['city_areas']['2']['stage']['cs']=1102
            if change=='receipt':state['week_protocol']['transition']['id']='wrong'
            if change=='team':state['battle']['active']['request']['h']=[25]
            if change=='mission':missions[1101]['va']=0
            with self.subTest(change=change):
                with self.assertRaises(ValueError):campaign.validate_normal_stage_source(state,state['battle']['active'],missions)
        with self.assertRaises(ValueError):campaign.expire_normal_chapters(admitted,'2')
        self.assertEqual(token,campaign.normal_chapter_token(admitted))

    def test_route27_lock_and_missing_activation_are_not_fabricated(self):
        self.route27(True);self.assertNotIn('5',self.state['story'].get('normal_chapters',{}).get('contexts',{}))
        with self.assertRaises(ValueError):self.admit(self.state,4129,5)
        self.assertTrue(self.state['story']['city_areas']['5']['st'][2])
        self.state['story']['city_areas']['5']['st'][2]=False
        self.state['story']['event_effect_receipts'].clear();self.refresh()
        self.assertNotIn('5',self.state['story'].get('normal_chapters',{}).get('contexts',{}))

    def test_multi_alternatives_real_cond_event_priority_and_one_win(self):
        descriptor=campaign.resolve_normal_chapter(2,1,'1',self.tables['chapter_mission_data'],self.tables['mission'])
        self.assertEqual(descriptor['groups'][-1],[1107,1106])
        self.refresh()
        state=self.state
        for scene in range(1101,1106):state=self.finish(self.admit(state,scene))[0]
        self.assertEqual(state['story']['city_areas']['2']['stage']['cs'],1106)
        state['completed_events'].append(20007)
        refresh_condition_city_missions(state,self.tables['mission'],completing_event=20007)
        self.assertNotIn('2',state['story'].get('condition_mission_roots',{}))
        self.refresh(state)
        self.assertEqual(state['story']['city_areas']['2']['stage']['cs'],1107)
        state=self.finish(self.admit(state,1107))[0]
        self.assertTrue(state['story']['normal_chapters']['contexts']['2']['complete'])
        self.assertNotIn(1106,state['story']['battle_wins'])
        for area,event,expected in ((3,30019,12101),(4,40013,13101)):
            desc=campaign.resolve_normal_chapter(area,1,'-1',self.tables['chapter_mission_data'],self.tables['mission'])
            context={'descriptor':desc,'wins':[]}
            modeled=copy.deepcopy(self.state);modeled['completed_events']=[event]
            stage=campaign._nc_stage(modeled,context)
            self.assertEqual(stage['cs'],expected)
            modeled['completed_events']=[]
            self.assertNotEqual(campaign._nc_stage(modeled,context)['cs'],expected)

    def test_ownership_condition_projection_and_restore_only_owned_fields(self):
        self.refresh();normal=copy.deepcopy(self.state['story']['city_areas']['2']['stage'])
        context=self.state['story']['normal_chapters']['contexts']['2']
        # Model an authenticated higher owner. Its actual producer is tested in
        # its own suite; this test proves shared writer arbitration.
        self.state['story']['special_city_stages']={'contexts':{'2':{'week':1,'route':'1','revoked':False}}}
        self.assertEqual(campaign.stage_projection_owner(self.state,2),'positive-special')
        changed=copy.deepcopy(self.tables['mission']);changed[1101]['cond_event']=20007
        self.state['completed_events']=[20007]
        refresh_condition_city_missions(self.state,changed)
        self.assertEqual(self.state['story']['city_areas']['2']['stage'],normal)
        self.state['story']['city_stage_provider']={'week':1,'route':'1','family':{'2':488}}
        with self.assertRaises(ValueError):campaign.stage_projection_owner(self.state,2)
        self.state['story'].pop('city_stage_provider');self.state['story'].pop('special_city_stages')
        self.state['story']['city_areas']['2']['stage']={'cs':999,'sl':[[999]]}
        campaign.expire_normal_chapters(self.state)
        self.assertEqual(self.state['story']['city_areas']['2']['stage']['cs'],999)

    def test_catalog_change_blocks_basic_fallback_and_resume_is_strict(self):
        self.refresh();state=json.loads(json.dumps(self.state));campaign.validate_normal_chapters(state)
        self.tables['chapter_mission_data'][(2,0,'-1',0)]['section'][0]=[1102]
        self.refresh(state)
        with self.assertRaises(ValueError):self.admit(state,1101)
        bad=copy.deepcopy(self.state);bad['story']['normal_chapters']['contexts']['2']['wins']=[1101,1101]
        with self.assertRaises(ValueError):campaign.validate_normal_chapters(bad)

    def test_merge_or_and_branch_exact_proof(self):
        desc=campaign.resolve_normal_chapter(7,1,'-1',self.tables['chapter_mission_data'],self.tables['mission'])
        context={'descriptor':desc,'wins':[6101,6102,6103,6104]}
        self.state['story']['current_mission_wins']=[6101,6102,6103,6104]
        self.assertEqual(campaign._nc_stage(self.state,context)['cs'],6105)
        self.assertNotIn(16104,context['wins'])
        desc=campaign.resolve_normal_chapter(3,1,'-1',self.tables['chapter_mission_data'],self.tables['mission'])
        context={'descriptor':desc,'wins':[12101]}
        self.state['story']['current_mission_wins']=[12101]
        stage=campaign._nc_stage(self.state,context)
        self.assertEqual(stage['cs'],12102) # exact 12101 branch remains gated by its actual event
        self.assertNotIn(2101,context['wins'])

    def test_legacy_progress_with_real_transition_is_not_reset(self):
        self.state['story']['battle_wins']=[1101]
        self.state['story']['city_areas']['2']['stage']={'cs':1102,'sl':[[scene] for scene in range(1101,1107)]}
        before=copy.deepcopy(self.state['story']['city_areas']['2'])
        self.refresh()
        self.assertNotIn('normal_chapters',self.state['story'])
        self.assertEqual(before,self.state['story']['city_areas']['2'])
        self.assertNotIn('normal_chapter_source',self.admit(self.state,1102)['battle']['active'])

    def test_final_day_cost_fatigue_bans_and_status_guards(self):
        self.refresh()
        for change in ('finalday','actions','fatigue','banned','free','fall','strike'):
            state=copy.deepcopy(self.state)
            if change=='finalday':state['day']['stock_day']=7
            if change=='actions':state['story']['city_values']['av']=0
            if change=='fatigue':state['profile']['heroes']['24']['cf']=0
            if change=='banned':state['story']['banned_heroes']={'24':True}
            if change=='free':state['story']['city_areas']['2']['st'][0]=0
            if change=='fall':state['story']['city_areas']['2']['st'][0]=2
            if change=='strike':state['story']['city_areas']['2']['st'][0]=5
            before=copy.deepcopy(state)
            with self.subTest(change=change):
                with self.assertRaises(ValueError):self.admit(state,1101)
                self.assertEqual(state,before)

    def test_equal_explicit_writer_and_changed_route_do_not_restore_old_stage(self):
        self.refresh();stage=copy.deepcopy(self.state['story']['city_areas']['2']['stage'])
        campaign.revoke_normal_chapter_projection(self.state,[2])
        campaign.expire_normal_chapters(self.state)
        self.assertEqual(self.state['story']['city_areas']['2']['stage'],stage)
        self.setUp();self.refresh()
        self.state['story']['route']='2'
        self.state['story']['city_areas']['2']['stage']={'cs':999,'sl':[[999]]}
        campaign.expire_normal_chapters(self.state,'2')
        self.assertEqual(self.state['story']['city_areas']['2']['stage']['cs'],999)

    def test_positive_dependency_requires_real_free_receipt_and_never_clears_lock(self):
        self.route27()
        self.state['story'].pop('normal_chapters',None)
        self.state['story']['event_effect_receipts']={}
        self.state['story']['city_areas']['3']={'id':3,'st':[0,False,False]}
        with self.assertRaises(ValueError):campaign.derive_normal_campaign_source(self.state,5,self.tables)
        self.tables['event_content'][900002]={'release':True,'areaFree':[3]}
        self.state['completed_events'].append(900002)
        self.state['story']['event_effect_receipts']={'host-free':900002}
        source=campaign.derive_normal_campaign_source(self.state,5,self.tables)
        self.assertEqual(source['activation']['kind'],'area-require')
        self.assertEqual([proof['area'] for proof in source['activation']['proofs']],[3])
        self.state['story']['city_areas']['5']['st'][2]=True
        with self.assertRaises(ValueError):campaign.derive_normal_campaign_source(self.state,5,self.tables)

    def test_area1_default107_with_real_source_and_actual_tutorial_guard(self):
        self.state['story'].update(route='27-1',event_history=[1424,900003],event_effect_receipts={'host-area1':900003})
        self.state['completed_events']=[1424,900003]
        self.state['week_protocol']['consumed_handoffs']=['route:1424']
        self.tables['event_content'][900003]={'release':True,'areaFight':[1]}
        self.state['story']['city_areas']['1']={'id':1,'st':[1,False,False],'stage':{'cs':101,'sl':[[101]]}}
        self.refresh()
        self.assertEqual(self.state['story']['city_areas']['1']['stage'],{'cs':107,'sl':[[107,101]]})
        admitted=self.admit(self.state,107,1)
        self.assertIn('normal_chapter_source',admitted['battle']['active'])
        with self.assertRaises(ValueError):self.admit(self.state,101,1)
        won=self.finish(admitted)[0]
        self.assertEqual(won['story']['city_areas']['1']['st'][0],0)
        self.assertEqual(won['story']['battle_wins'],[107])
        self.setUp();self.state['story']['emergency']=True
        self.state['story']['city_areas']['1']={'id':1,'st':[1,False,False],'stage':{'cs':101,'sl':[[101]]}}
        self.refresh()
        self.assertEqual(self.state['story']['city_areas']['1']['stage']['cs'],101)
        self.assertNotIn('1',self.state['story'].get('normal_chapters',{}).get('contexts',{}))

    def test_all_six_area1_route5_rows_use_actual5053_conditional_provider(self):
        self.assertEqual(self.tables['event_content'][5053]['areaFight'],[1])
        for route in ('5','5-1','5-2','5-3','5-4','5-5'):
            state=copy.deepcopy(self.state);state['story']['route']=route
            state['story']['city_areas']['1']={'id':1,'st':[1,False,False],'stage':{'cs':101,'sl':[[101]]}}
            refresh_condition_city_missions(state,self.tables['mission'])
            self.assertNotIn('1',state['story'].get('condition_mission_roots',{}))
            state['completed_events']=[5053]
            state['story']['event_effect_receipts']={'host-original5053':5053}
            refresh_condition_city_missions(state,self.tables['mission'],completing_event=5053)
            self.refresh(state)
            self.assertEqual(campaign.stage_projection_owner(state,1),'conditional')
            self.assertEqual(state['story']['city_areas']['1']['stage'],{'cs':22010,'sl':[[22010],[22011],[22012]]})
            for scene in (22010,22011,22012):
                state=self.finish(self.admit(state,scene,1))[0]
            self.assertEqual(state['story']['city_areas']['1']['st'][0],0)
            self.assertEqual(state['story']['battle_wins'],[22010,22011,22012])
            self.assertNotIn('1',state['story'].get('normal_chapters',{}).get('contexts',{}))

    def test_equivalent_route_handoff_carries_only_owned_actual_scene_wins(self):
        state=self.route27();state=self.finish(self.admit(state,4129,5))[0]
        old_epoch=state['story']['normal_chapters']['contexts']['5']['epoch']
        campaign.expire_normal_chapters(state,'27-2')
        state['story']['route']='27-2'
        self.tables['event_content'][900004]={'release':True,'enterStoryRoute':'27-2'}
        state['completed_events'].append(900004)
        state['story']['event_history'].append(900004)
        state['week_protocol']['consumed_handoffs'].append('route:900004')
        self.refresh(state)
        context=state['story']['normal_chapters']['contexts']['5']
        self.assertEqual(context['wins'],[4129]);self.assertNotEqual(context['epoch'],old_epoch)
        self.assertEqual(context['last_stage']['cs'],4130)
        self.assertEqual(state['story']['city_values']['av'],22)
        campaign.validate_normal_chapters(json.loads(json.dumps(state)))

    def test_event_replacement_hook_preserves_internal_alternatives(self):
        self.refresh()
        internal=self.tables['event_content'][20007]
        self.assertTrue(internal['refreshMission'])
        self.assertEqual(campaign.normal_chapter_event_replacements(self.state,20007,internal,self.tables['mission']),[])
        self.assertEqual(campaign.normal_chapter_event_replacements(self.state,999,{'refreshMission':1},self.tables['mission']),[])
        self.assertEqual(campaign.normal_chapter_event_replacements(self.state,999,{'abandonMission':[1102]},self.tables['mission']),[2])
        external=copy.deepcopy(self.tables['mission']);external[999001]={'id':999001,'ch':2,'release':1,'system_type':1,'cond_event':999,'cond':[]}
        self.assertEqual(campaign.normal_chapter_event_replacements(self.state,999,{'refreshMission':1},external),[2])
        external[999001]['cond']=[999002]
        self.assertEqual(campaign.normal_chapter_event_replacements(self.state,999,{'refreshMission':1},external),[])
        campaign.revoke_normal_chapter_projection(self.state,[2],'explicit-later-owner')
        self.state['completed_events'].append(20007)
        campaign.validate_normal_chapters(json.loads(json.dumps(self.state)))

    def raw_events(self):
        sys.path.insert(0,str(ROOT/'tools'))
        from read_data_table import read
        return read(ROOT/'analysis/decompiled/event_content.py')

    def completed_area2(self):
        self.refresh();state=self.state
        for scene in range(1101,1107):state=self.finish(self.admit(state,scene))[0]
        return state

    def actual_handoff(self,state,event=5023):
        from offline_week import initial_week_state,prepare_week_route_handoff
        events=self.raw_events();self.tables['event_content']=events
        protocol=initial_week_state();protocol.update(state['week_protocol'])
        protocol['transition']=dict(protocol['transition'],notices=[])
        state['week_protocol']=protocol
        state['completed_events'].append(event)
        state['story'].setdefault('event_history',[]).append(event)
        route=events[event]['enterStoryRoute']
        return prepare_week_route_handoff(state,{'kind':'route','event':event,'route':route,'token':'route:%s'%event},events,{route:{}})[0]

    def test_complete_archived_clear_survives_actual_pre_mutation_handoff(self):
        state=self.completed_area2();state=self.actual_handoff(state)
        self.assertEqual(state['story']['route'],'4')
        self.assertEqual(state['story']['city_areas']['2']['stage']['cs'],0)
        self.assertNotIn('2',state['story']['normal_chapters']['contexts'])
        proof=campaign._nc_free_proof(state,self.tables,2)
        self.assertEqual(proof['wins'],list(range(1101,1107)))
        source=campaign.derive_normal_campaign_source(state,3,self.tables)
        self.assertEqual(source['activation']['proofs'],[proof])
        notices=self.refresh(state)
        self.assertEqual(state['story']['city_areas']['3']['st'][0],1)
        self.assertEqual(notices[0][0],'get_all_area_info_reply');self.assertFalse(notices[0][1]['sm'])
        self.assertEqual(notices[1][0],'get_area_stages_reply')
        resumed=json.loads(json.dumps(state));campaign.validate_normal_chapters(resumed)
        scene=resumed['story']['city_areas']['3']['stage']['cs']
        if scene:self.admit(resumed,scene,3)

    def test_archived_clear_rejects_partial_otherweek_bad_hash_and_lost_current_proof(self):
        state=self.completed_area2();state=self.actual_handoff(state)
        self.assertIsNotNone(campaign._nc_free_proof(state,self.tables,2))
        for alteration in ('partial','week','hash','archivehash','epoch','progress','revoked','status','catalog','event'):
            bad=copy.deepcopy(state);tables=copy.deepcopy(self.tables)
            archive=bad['story']['normal_chapter_history'][0]
            if alteration=='partial':archive['wins'].pop();archive['complete']=False
            if alteration=='week':archive['week']=0
            if alteration=='hash':archive['descriptor']['catalog_token']='0'*64
            if alteration=='archivehash':archive['archive_token']='0'*64
            if alteration=='epoch':archive['epoch']='0'*64
            if alteration=='progress':bad['story']['current_mission_wins'].remove(1101)
            if alteration=='revoked':archive['revoked']=True
            if alteration=='status':bad['story']['city_areas']['2']['st'][0]=1
            if alteration=='catalog':tables['mission'][1101]['va']=999
            if alteration=='event':bad['week_protocol']['transition']['id']='wrong'
            with self.subTest(alteration=alteration):self.assertIsNone(campaign._nc_free_proof(bad,tables,2))
        partial=self.state
        self.refresh(partial);partial=self.finish(self.admit(partial,1101))[0]
        partial=self.actual_handoff(partial)
        partial['story']['city_areas']['2']['st'][0]=0 # deliberately bare FREE cannot complete receipt
        self.assertIsNone(campaign._nc_free_proof(partial,self.tables,2))

    def test_actual_before_mutation_expiry_never_restores_oldroute_or_basic_fallback(self):
        self.refresh();state=self.finish(self.admit(self.state,1101))[0]
        self.assertEqual(state['story']['city_areas']['2']['stage']['cs'],1102)
        state=self.actual_handoff(state)
        self.assertEqual(state['story']['city_areas']['2']['stage']['cs'],1102)
        self.assertEqual(state['story']['normal_chapter_claims']['2']['route'],'4')
        self.refresh(state)
        context=state['story']['normal_chapters']['contexts']['2']
        self.assertEqual(context['source']['activation']['kind'],'normal-route-carry')
        self.assertEqual(context['wins'],[1101]);self.assertEqual(context['last_stage']['cs'],1102)
        self.assertEqual(state['story']['city_values']['av'],22)
        resumed=json.loads(json.dumps(state));campaign.validate_normal_chapters(resumed)
        admitted=self.admit(resumed,1102)
        advanced=self.finish(admitted)[0]
        self.refresh(advanced)
        self.assertNotIn('blocked',advanced['story']['normal_chapters']['contexts']['2'])
        self.assertEqual(advanced['story']['city_areas']['2']['stage']['cs'],1103)
        self.admit(advanced,1103)
        again=self.actual_handoff(advanced,5039)
        self.refresh(again)
        self.assertEqual(again['story']['normal_chapters']['contexts']['2']['wins'],[1101,1102])
        self.admit(again,1103)
        self.setUp();self.refresh()
        campaign.expire_normal_chapters(self.state)
        self.assertEqual(self.state['story']['city_areas']['2']['stage'],{'cs':1101,'sl':[[1101]]})

    def test_partial_freshweek_carry_rejects_missing_or_changed_owned_history(self):
        self.refresh();state=self.finish(self.admit(self.state,1101))[0];state=self.actual_handoff(state)
        for alteration in ('missing','archivehash','transition','progress','stage','status'):
            bad=copy.deepcopy(state)
            if alteration=='missing':bad['story']['normal_chapter_history']=[]
            if alteration=='archivehash':bad['story']['normal_chapter_history'][0]['archive_token']='0'*64
            if alteration=='transition':bad['week_protocol']['transition']['id']='wrong'
            if alteration=='progress':bad['story']['current_mission_wins']=[]
            if alteration=='stage':bad['story']['city_areas']['2']['stage']={'cs':999,'sl':[[999]]}
            if alteration=='status':bad['story']['city_areas']['2']['st'][0]=2
            self.refresh(bad)
            with self.subTest(alteration=alteration):
                self.assertNotIn('2',bad['story']['normal_chapters']['contexts'])
                with self.assertRaises(ValueError):self.admit(bad,1102)

    def test_raw_native_event_sets_are_not_copied_into_canonical_normal_state(self):
        events=self.raw_events()
        self.assertIsInstance(events[20007]['mutexEvent'],set)
        self.tables['event_content']=events
        self.state['completed_events']=[20007]
        self.state['story']['event_effect_receipts']={'raw-event-receipt':20007}
        self.assertEqual(campaign._nc_events(self.state,self.tables,'areaFree',2),[])
        self.refresh();campaign.validate_normal_chapters(json.loads(json.dumps(self.state)))
        self.tables['event_content']={event:Tagged(row) for event,row in events.items()}
        self.assertEqual(campaign._nc_events(self.state,self.tables,'areaFree',2),[])
        supported_bad={20007:dict(events[20007],areaFree={2})}
        self.tables['event_content']=supported_bad
        with self.assertRaises(ValueError):campaign._nc_events(self.state,self.tables,'areaFree',2)

    def test_new_explicit_activation_starts_fresh_epoch_only_after_commit(self):
        state=self.completed_area2();old=state['story']['normal_chapters']['contexts']['2']['epoch']
        row={'release':True,'areaFight':[2],'mutexEvent':{123}}
        self.tables['event_content'][900100]=row
        campaign.mark_normal_chapter_activation(state,900100,row,'reactivate-2')
        self.refresh(state)
        self.assertEqual(state['story']['normal_chapters']['contexts']['2']['epoch'],old)
        state['story']['city_areas']['2']['st'][0]=1
        state['completed_events'].append(900100);state['story']['event_effect_receipts']={'reactivate-2':900100}
        self.refresh(state)
        context=state['story']['normal_chapters']['contexts']['2']
        self.assertNotEqual(context['epoch'],old);self.assertEqual(context['wins'],[])
        self.assertEqual(context['last_stage']['cs'],1101);self.assertFalse(context['complete'])
        self.assertEqual(state['story']['battle_wins'],list(range(1101,1107)))
        epoch=context['epoch'];campaign.mark_normal_chapter_activation(state,900100,row,'reactivate-2');self.refresh(state)
        self.assertEqual(state['story']['normal_chapters']['contexts']['2']['epoch'],epoch)
        admitted=self.admit(state,1101)
        with self.assertRaises(ValueError):campaign.mark_normal_chapter_activation(admitted,900100,row,'another')

    def test_flat_actual_import_blocked_module_works(self):
        original=builtins.__import__
        def blocked(name,*args,**kwargs):
            if name.startswith('offline_'):raise ImportError(name)
            return original(name,*args,**kwargs)
        namespace={'__builtins__':dict(vars(builtins),__import__=blocked)}
        for path in ('offline_special_city_stage.py','offline_city_stage_provider.py','offline_flashback.py','offline_chapter_campaign.py','offline_stage.py'):
            exec(compile((ROOT/'runtime'/path).read_text(),path,'exec'),namespace)
        descriptor=namespace['resolve_normal_chapter'](5,1,'27-1',tagged(self.tables['chapter_mission_data']),tagged(self.tables['mission']))
        if descriptor['groups'] != [[scene] for scene in range(4129,4135)]:raise AssertionError('Flat original groups drift')
        self.assertEqual(descriptor,json.loads(json.dumps(descriptor)))
        self.refresh()
        admitted,changed=namespace['prepare_stage_admission'](self.state,{'t':1,'s':1101,'h':[24],'d':{'a':2}},tagged(self.tables['mission']),lambda:'flat-host1101')
        self.assertTrue(changed)
        if admitted['battle']['active']['normal_chapter_source']['scene'] != 1101:raise AssertionError('Flat source missing')
        namespace['validate_normal_chapters'](json.loads(json.dumps(admitted)))


if __name__=='__main__':unittest.main()
