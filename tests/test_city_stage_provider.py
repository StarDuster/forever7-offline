"""Original-table component contracts; synthetic host results, not native wins."""
import copy
import hashlib
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'runtime'))
from offline_city_stage_provider import (original_city_stage_family,
    record_city_stage_occurrence, refresh_city_stage_provider, expire_city_stage_provider,
    validate_city_stage_provider, city_stage_provider_token)
from offline_stage import prepare_stage_admission, prepare_stage_finish


class CityStageProviderTests(unittest.TestCase):
    def setUp(self):
        self.fixture = json.loads((ROOT / 'tests/fixtures/city_stage_provider_cdata.json').read_text())
        self.tables = {name:{int(k):v for k,v in self.fixture[name].items()}
            for name in ('mission','city_data','city_area_link_data')}
        self.tables['coc_scenes'] = self.fixture['coc_scenes']
        self.events = {int(k):v for k,v in self.fixture['events'].items()}
        self.state = {'story':{'route':'27-1','week':1,'date':0,'emergency':False,
            'city_values':{'av':24,'fv':100},'city_areas':{},'battle_wins':[]},
            'day':{'stock_day':0},'completed_events':[],
            'profile':{'economy':{'level':50,'money':0},'heroes':{'135':{'cf':100}}},
            'battle':{'version':1,'active':None,'receipts':[]}}
        self.occurrence(1424)

    def occurrence(self, event, row=None, receipt=None):
        # Model the event-effect component's prior native-area writes. This
        # helper is not a dialogue/option producer or native acceptance test.
        row = copy.deepcopy(row if row is not None else self.events[event])
        areas = self.state['story']['city_areas']
        for field,status in (('areaFree',0),('areaFight',1),('areaFall',2)):
            for aid in row.get(field,()):
                areas.setdefault(str(aid),{'id':aid,'st':[2,False,False],'lv':1,'bd':{}})['st'][0]=status
        for field,locked in (('areaUnlock',False),('areaLock',True)):
            for aid in row.get(field,()):
                areas.setdefault(str(aid),{'id':aid,'st':[2,False,False],'lv':1,'bd':{}})['st'][2]=locked
        return record_city_stage_occurrence(self.state,event,row,self.tables,receipt or 'actual-component-%s'%event)

    def admit(self, scene, state=None, identity=None):
        return prepare_stage_admission(state or self.state,
            {'t':1,'s':scene,'h':[135],'d':{'a':self.tables['mission'][scene]['ch']}},
            self.tables['mission'],lambda:identity or 'host-fight-%s'%scene)

    def finish(self, state, win=1):
        active=state['battle']['active']
        actual={key:copy.deepcopy(active['request'][key]) for key in ('t','s','h')}
        actual.update(x=[],w=win,e={})
        def settle(admission,result):
            reply=dict(result,r={});reply.pop('e')
            return reply,{'profile':copy.deepcopy(state['profile']),'notices':[],'granted':[]}
        return prepare_stage_finish(state,actual,self.tables['mission'],self.tables['city_data'],settle,active['fight_id'])

    def test_fixture_hashes_and_real_family_normalization(self):
        for name,digest in self.fixture['sha256'].items():
            self.assertEqual(hashlib.sha256((ROOT/name).read_bytes()).hexdigest(),digest)
        family=original_city_stage_family(self.tables['mission'],self.tables['coc_scenes'])
        self.assertEqual(set(family.values()),set(range(482,489)))
        self.assertEqual(set(family),{10000,6,10001,4,10002,10003,2})
        self.assertNotIn(507,family.values());self.assertNotIn(517,family.values())

    def test_original_entry_overlap_and_positive_requirement_only(self):
        areas=self.state['story']['city_areas']
        self.assertEqual(areas['7']['st'],[0,False,False])
        self.assertEqual(areas['10000']['stage'],{'cs':482,'sl':[[482]]})
        self.assertNotIn('10001',areas)
        self.assertTrue(areas['6']['st'][2]);self.assertTrue(areas['4']['st'][2])
        self.assertTrue(areas['1']['st'][2])
        validate_city_stage_provider(self.state)

    def test_all_seven_wins_require_real_downstream_free_effects(self):
        # Source activations can precede their linked predecessor's clearance.
        self.occurrence(1450);self.occurrence(1452)
        for scene,free_event,next_event in ((482,1442,1443),(483,1432,None),
                (484,1444,1445),(485,1433,None),(486,1446,1448),
                (487,1447,1449),(488,1434,None)):
            admitted,changed=self.admit(scene)
            self.assertTrue(changed)
            self.assertEqual(admitted['battle']['active']['costs'],{'actions':2,'fatigue':0})
            finished,reply,effects,changed=self.finish(admitted)
            self.assertTrue(changed)
            aid=str(self.tables['mission'][scene]['ch'])
            self.assertEqual(finished['story']['city_areas'][aid]['st'][0],1)
            self.assertEqual(finished['story']['city_areas'][aid]['stage']['cs'],0)
            self.assertNotIn(free_event,finished['completed_events'])
            self.state=finished
            self.occurrence(free_event)
            if next_event:self.occurrence(next_event)
        self.assertEqual(self.state['story']['city_values']['av'],10)
        self.assertEqual(self.state['profile']['heroes']['135']['cf'],100)
        self.assertEqual(self.state['story']['battle_wins'],list(range(482,489)))

    def test_loss_retry_and_duplicate_win_are_atomic(self):
        admitted,_=self.admit(482)
        lost,reply,effects,changed=self.finish(admitted,0)
        self.assertEqual(lost['story'],admitted['story']);self.assertEqual(reply['r'],{})
        retry,_=self.admit(482,lost,identity='retry482')
        won,reply,effects,changed=self.finish(retry)
        self.assertEqual(won['story']['city_values']['av'],22)
        active=retry['battle']['active'];actual={k:active['request'][k] for k in ('t','s','h')}
        actual.update(x=[],w=1,e={})
        again,reply,effects,changed=prepare_stage_finish(won,actual,self.tables['mission'],self.tables['city_data'],
            lambda *args:self.fail('duplicate settled twice'),active['fight_id'])
        self.assertFalse(changed);self.assertEqual(again,won)

    def test_stale_day_route_lock_and_unowned_team_reject_unchanged(self):
        admitted,_=self.admit(482)
        for alter in ('day','route','lock','fall'):
            changed=copy.deepcopy(admitted)
            if alter=='day':changed['day']['stock_day']=1
            if alter=='route':changed['story']['route']='27-2'
            if alter=='lock':changed['story']['city_areas']['10000']['st'][2]=True
            if alter=='fall':changed['story']['city_areas']['10000']['st'][0]=2
            before=copy.deepcopy(changed)
            with self.assertRaises(ValueError):self.finish(changed)
            self.assertEqual(changed,before)
        before=copy.deepcopy(self.state)
        self.state['profile']['heroes']={}
        with self.assertRaises(ValueError):self.admit(482)
        self.state=before
        with self.assertRaises(ValueError):
            prepare_stage_admission(self.state,{'t':1,'s':482,'h':[24],'d':{'a':10000}},self.tables['mission'],lambda:'bad')

    def test_later_lock_blocks_and_expiry_restores_only_owned_fields(self):
        self.occurrence(1442);self.occurrence(1443)
        areas=self.state['story']['city_areas']
        self.assertFalse(areas['6']['st'][2])
        self.occurrence(900001,{'release':True,'areaLock':[6]})
        refresh_city_stage_provider(self.state)
        self.assertTrue(areas['6']['st'][2])
        with self.assertRaises(ValueError):self.admit(483)
        self.occurrence(900002,{'release':True,'areaUnlock':[6]})
        self.assertFalse(areas['6']['st'][2])
        profile=copy.deepcopy(self.state['profile']);token=city_stage_provider_token(self.state)
        expire_city_stage_provider(self.state)
        self.assertFalse(areas['6']['st'][2])
        self.assertEqual(self.state['profile'],profile)
        self.assertNotEqual(city_stage_provider_token(self.state),token)
        self.assertNotIn('city_stage_provider',self.state['story'])
        self.assertIn('city_stage_provider_history',self.state['story'])

    def test_unrelated_entry_sentinel_and_unreleased_effects_do_not_activate(self):
        unrelated=copy.deepcopy(self.state)
        unrelated['story'].pop('city_stage_provider')
        unrelated['story']['route']='2'
        record_city_stage_occurrence(unrelated,900003,
            {'release':True,'enterStoryRoute':'2','areaFree':[1]},self.tables,'unrelated')
        self.assertNotIn('city_stage_provider',unrelated['story'])
        before=copy.deepcopy(self.state)
        record_city_stage_occurrence(self.state,1437,self.events[1437],self.tables,'false-wrapper')
        self.assertEqual(self.state,before)
        self.assertNotIn('10001',self.state['story']['city_areas'])

    def test_authorization_token_tracks_source_changes_and_validator_rejects_corruption(self):
        self.occurrence(1450)
        previous=city_stage_provider_token(self.state)
        self.occurrence(1450,receipt='distinct-real-occurrence')
        self.assertNotEqual(previous,city_stage_provider_token(self.state))
        for field,value in (('requirements',{'6':None}),('predecessors',{'6':0}),
                ('activated',['unknown']),('entry_free',['7'])):
            changed=copy.deepcopy(self.state)
            if isinstance(value,dict):changed['story']['city_stage_provider'][field].update(value)
            else:changed['story']['city_stage_provider'][field]=value
            with self.assertRaises(ValueError):validate_city_stage_provider(changed)
        changed=copy.deepcopy(self.state)
        changed['story']['city_stage_provider']['owned']['10000']['last']['lock']='bad'
        with self.assertRaises(ValueError):validate_city_stage_provider(changed)

    def test_pending_source_effect_commits_and_later_special_projection_is_retained(self):
        from offline_event_effects import plan_event_effects
        row=self.events[1450]
        candidate,notices,diag=plan_event_effects(self.state,1450,{1450:row},self.tables,
            {'receipt_key':'gated-host-component','completed_callbacks':['ui:1450']})
        self.assertTrue(diag['ready'],diag)
        self.assertIn('10001',candidate['story']['city_stage_provider']['sources'])
        self.assertEqual(candidate['story']['city_areas']['10001']['st'][0],1)
        self.assertNotIn('stage',candidate['story']['city_areas']['10001'])
        self.state['story']['city_areas']['10000']['stage']={'cs':507,'sl':[[507]]}
        self.occurrence(900004,{'release':True,'areaSpecialStage':{10000:507}})
        refresh_city_stage_provider(self.state)
        self.assertEqual(self.state['story']['city_areas']['10000']['stage']['cs'],507)
        with self.assertRaises(ValueError):self.admit(482)


    def test_expiry_publishes_neutral_virtual_placeholder_for_native_merge(self):
        notices=expire_city_stage_provider(self.state)
        # Original CityData.set_area_info merges, so omitted keys would leave
        # a native FIGHT node. Publish the restored FALL state explicitly.
        area=self.state['story']['city_areas']['10000']
        self.assertEqual(area['st'][0],2)
        full=[payload for name,payload in notices if name=='get_all_area_info_reply'][-1]
        self.assertEqual(full['ais']['area_10000']['st'][0],2)
        stages=[payload for name,payload in notices if name=='get_area_stages_reply' and payload['ai']==10000]
        self.assertEqual(stages,[{'ai':10000,'st':{'cs':0,'sl':[]}}])
        self.assertFalse(self.state['story']['city_areas']['7']['st'][2])


    def test_original_area_consumer_projection_avoids_virtual_camera_settlement(self):
        # Run only this isolated decompiled consumer method with inert host
        # dependencies, never original bytecode/native imports or a game VM.
        import ast
        import contextlib
        import io
        import textwrap
        from types import SimpleNamespace
        from lib2to3.refactor import RefactoringTool
        from offline_stage import _stage_city_notice
        original=(ROOT/'analysis/decompiled/CityData.py').read_text()
        start=original.index('    def set_area_info(')
        end=original.index('    def get_area_info(',start)
        selected=textwrap.dedent(original[start:end])
        translated=str(RefactoringTool(['lib2to3.fixes.fix_print',
            'lib2to3.fixes.fix_dict']).refactor_string(selected,'isolated-area-consumer'))
        tree=ast.parse(translated)
        self.assertEqual(len(tree.body),1)
        self.assertIsInstance(tree.body[0],ast.FunctionDef)
        self.assertEqual(tree.body[0].name,'set_area_info')
        calls=[]
        camera_models={}  # Early projection precedes city-model registration.
        def notify_fight(areas):
            calls.append(('fight',list(areas)))
            for area in areas:
                camera_models[area]
        panels=SimpleNamespace(city=SimpleNamespace(
            notify_update_area=lambda area:calls.append(('updated',area)),
            notify_update_stage=lambda:calls.append(('stages',None))),
            city_entrance=SimpleNamespace(update_prop=lambda:None),
            settlement_fullscreen=SimpleNamespace(
                notify_area_open=lambda areas:calls.append(('open',list(areas))),
                notify_area_fight=notify_fight,
                notify_area_cr=lambda areas:calls.append(('cr',list(areas)))))
        namespace={'gg':SimpleNamespace(ui=SimpleNamespace(panels=panels)),
            'const':SimpleNamespace(CityStatus=SimpleNamespace(FREE=0,FIGHT=1,FALL=2,STRIKE=5))}
        exec(compile(tree,'<isolated-original-set-area-info>','exec'),namespace)
        consume=namespace['set_area_info']
        def native_city():
            return SimpleNamespace(areas_info={},area_building_obj={},destroy_building={},
                first_update_city_sfx_visible=lambda area:None,proc_change_event=lambda:None)
        def apply(city,payload):
            with contextlib.redirect_stdout(io.StringIO()):
                consume(city,payload['ais'],payload['sm'])
        entry=[payload for name,payload in refresh_city_stage_provider(self.state)
            if name=='get_all_area_info_reply'][-1]
        # The former projection demonstrably enters the normal camera path.
        former=copy.deepcopy(entry);former['sm']=True
        with self.assertRaisesRegex(KeyError,'10000'):apply(native_city(),former)
        self.assertIn(('fight',[10000]),calls)
        calls[:]=[]
        city=native_city()
        apply(city,entry)
        self.assertEqual(city.areas_info['area_10000']['st'][0],1)
        self.assertEqual(city.areas_info['area_10000']['stage']['cs'],482)
        # Reconnection projects the same live source; expiry publishes FALL.
        reconnect=[payload for name,payload in refresh_city_stage_provider(self.state)
            if name=='get_all_area_info_reply'][-1]
        apply(city,reconnect)
        expiry=[payload for name,payload in expire_city_stage_provider(self.state)
            if name=='get_all_area_info_reply'][-1]
        apply(city,expiry)
        self.assertEqual(city.areas_info['area_10000']['st'][0],2)
        self.assertFalse(any(kind in ('fight','open') for kind,value in calls))
        # After normal city models load, genuine settlement remains enabled.
        camera_models[2]=object()
        city.areas_info['area_2']={'id':2,'st':[1,False,False],'bd':{}}
        normal_story={'city_values':{},'city_areas':{
            '2':{'id':2,'st':[0,False,False],'bd':{}}}}
        ordinary=_stage_city_notice(normal_story)[1]
        self.assertTrue(ordinary['sm'])
        apply(city,ordinary)
        self.assertIn(('open',[2]),calls)


if __name__=='__main__':unittest.main()
