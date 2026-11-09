"""Offline tests. No ADB/emulator/native VM invocation in this module."""
import ast
import copy
import importlib.util
import io
import json
from pathlib import Path
import sys
import tempfile
import struct
import zlib
from types import SimpleNamespace as NS
import unittest
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
sys.path.insert(0,str(ROOT/'runtime'))
from offline_store import OfflineSaveStore
import audit_wardrobe_readonly as host
spec=importlib.util.spec_from_file_location('wardrobe_native_probe',host.PROBE)
native=importlib.util.module_from_spec(spec);spec.loader.exec_module(native)

class FakeSkin:
    def __init__(self,template,uid,ias=False):
        self.id=template;self.uuid=uid;self.curDye={1:{'color':7}};self.pendingDye={};self.isInvisibleAwakeSkin=ias;self.forbid=False
    def getCurDyeScheme(self):return copy.deepcopy(self.curDye)

class FakeNative:
    def __init__(self,folder):
        self.now=100.;self.pending=[];self.calls=[];self.scene=None
        self.hero=NS(skins={'base':FakeSkin(99,'base'),'dye':FakeSkin(10080,'dye')},curSkin='base',lastNorCurSkin=None,awakeStage=1,awakeSkinStyle=False,wearPendantInfo=[8])
        self.profile={'heroes':{'99':{'cs':'base','pa':[8],'sk':{'base':{'i':99},'dye':{'i':10080,'cd':{'1':7}}}}},'economy':{'money':42}}
        self.save=Path(folder)/'save.json';OfflineSaveStore(str(self.save),lambda payload:None).write({'profile':self.profile,'seen':[]})
        self.owner=NS(heroMgrData=NS(getHero=lambda hero:self.hero if hero==99 else None))
        self.proxy=NS(owner=self.owner,profile=self.profile)
        common=NS(valid=True,visible=False,hero_id=99,on_tab_click=self.tab,on_navigation_canvas_back=self.back)
        wardrobe=NS(valid=True,visible=False,hero_id=99,preview_show=False,cur_page=1,skin_uuid='base',dye_skin_color=None,
            skin_comps=[NS(skin_uuid=uid,skin_id=skin.id,_node=NS(isVisible=lambda:True))for uid,skin in self.hero.skins.items()],
            get_model_by_skin=lambda template:{99:10129,10080:30141}[template],select_skin=self.select,enter_buy=self.enter_buy,exit_buy=self.exit_buy,ue_explor_skin=self.explore)
        wardrobe.comp_wardrobe=NS(skins=[],sub_comps=[])
        model=NS(valid=True,visible=False,hero_id=99,skin_id=None,skin_obj=None,skin_model_id=10129)
        herolist=NS(valid=True,visible=True,curr_show_hero_list=[99],on_hero_click=self.open)
        self.panels=NS(hero_common=common,hero_wardrobe=wardrobe,hero_model=model,hero_herolist=herolist)
        self.gg=NS(avatar=self.owner,_f7_avatar_proxy=self.proxy,ui=NS(panels=self.panels),city_container=NS(get_current_scene=lambda:self.scene,get_scene_by_key=lambda key:self.scene),
            exec_delay=lambda ms,callback:self.pending.append((ms,callback)))
        self.audit=native.ReadonlyWardrobeAudit(self.gg,str(Path(folder)/'status.json'),'run',{'renderer':'mock-no-GPU'},scene_key=1)
        self.gg._f7_readonly_wardrobe_audit=self.audit
    def replace_model(self,number):
        wrapper=NS(model=NS(valid=True,filename='hero_skin/%d.gim'%number),_animidle='idle_03',_anims=[],_touch_anim=None,_begin_touch_anim=None,_animcb=None)
        for name in native.AUDIT_TASKS:setattr(wrapper,name,None if name in('_task_model','_task_sfx')else[])
        self.scene.scene_model=wrapper;self.scene.real_model_id=number;self.panels.hero_model.skin_model_id=number
    def open(self,hero):
        self.calls.append(('on_hero_click',hero));self.scene=NS(real_model_id=10129,model_visible=True,all_thing_loaded=True,model_can_touch=True)
        self.replace_model(10129);self.panels.hero_common.visible=True;self.panels.hero_herolist.visible=False
    def tab(self,name,instant=False):
        self.calls.append(('on_tab_click',name,instant));self.panels.hero_wardrobe.visible=True;self.panels.hero_model.visible=True;self.panels.hero_common.visible=False;self.panels.hero_common.tab_now='wardrobe'
    def select(self,uid,notify=True):
        self.calls.append(('select_skin',uid,notify));self.panels.hero_wardrobe.skin_uuid=uid
        self.replace_model(30141 if self.hero.skins[uid].id==10080 else 10129)
    def enter_buy(self):self.calls.append(('enter_buy',));self.panels.hero_wardrobe.cur_page=2
    def exit_buy(self):self.calls.append(('exit_buy',));self.select(self.hero.curSkin);self.panels.hero_wardrobe.cur_page=1
    def explore(self,template,notify=True,dye_skin=None):
        self.calls.append(('ue_explor_skin',template,notify,dye_skin));self.panels.hero_wardrobe.skin_id=dye_skin or template;self.replace_model(30141)
    def back(self):
        self.calls.append(('on_navigation_canvas_back',));self.scene=None;self.panels.hero_herolist.visible=True
        for p in(self.panels.hero_common,self.panels.hero_wardrobe,self.panels.hero_model):p.visible=False
    def tick(self,count=1):
        for unused in range(count):
            if not self.pending:return
            delay,callback=self.pending.pop(0);self.now+=delay/1000.;callback()
    def until(self,phase,limit=100):
        for unused in range(limit):
            if self.audit.phase==phase:return
            self.tick()
        raise RuntimeError('Fake scheduler did not reach '+phase+': '+self.audit.phase)
    def start(self,**overrides):
        job={'job_id':'skin-10080','hero_id':99,'template_id':10080,'save_path':str(self.save),'timeout':5}
        job.update(overrides);self.audit.start(job)

class NativeAuditTests(unittest.TestCase):
    def setUp(self):
        self.folder=tempfile.TemporaryDirectory();self.addCleanup(self.folder.cleanup)
        self.env=FakeNative(self.folder.name)
        clock=patch.object(native.time,'time',lambda:self.env.now);clock.start();self.addCleanup(clock.stop)
    def test_owned_dye_three_samples_capture_handshake_original_return_no_persistent_change(self):
        e=self.env;before=copy.deepcopy(native.audit_raw_hero(e.hero));profile=copy.deepcopy(e.profile)
        e.start();e.until('ready_capture')
        self.assertEqual(e.audit.route['kind'],'owned');self.assertIsNone(e.panels.hero_model.skin_id)
        samples=e.audit.last['samples'];self.assertEqual(len(samples),3)
        self.assertTrue(all(row['common_visible']is False and row['common_tab']=='wardrobe'for row in samples))
        self.assertTrue(all(row['animations']['_animidle']=='idle_03'for row in samples))
        token=e.audit.capture_token;e.audit.checkpoint(token,'before')
        self.assertEqual(e.audit.phase,'capture_before')
        e.now+=.1;e.audit.checkpoint(token,'after',{'token':token,'sha256':'a'*64,'path':'actor.png'})
        self.assertEqual(e.audit.phase,'cleanup');e.until('idle')
        self.assertEqual(e.audit.last['result']['load_status'],'loaded_unreviewed')
        self.assertEqual(e.audit.last['result']['visual_status'],'unreviewed')
        self.assertEqual(native.audit_raw_hero(e.hero),before);self.assertEqual(e.profile,profile)
        self.assertEqual([c[0]for c in e.calls],['on_hero_click','on_tab_click','select_skin','on_navigation_canvas_back'])
    def test_current_baseline_does_not_select_skin_and_fences_actual_selected_uuid(self):
        e=self.env;e.start(job_id='hero-099-baseline',template_id=None);e.until('ready_capture')
        self.assertEqual(e.audit.template,99)
        self.assertFalse(any(c[0]=='select_skin'for c in e.calls))
        e.panels.hero_wardrobe.skin_uuid='dye'
        e.audit.checkpoint(e.audit.capture_token,'before')
        self.assertEqual(e.audit.phase,'paused')

    def test_preview_dye_changes_with_same_model_and_raw_collection_are_not_stable(self):
        e=self.env;before=copy.deepcopy(native.audit_raw_hero(e.hero));e.start();e.tick(3)
        self.assertEqual(e.audit.phase,'loading')
        e.panels.hero_wardrobe.cur_dye_color=['red'];e.tick()
        e.panels.hero_wardrobe.cur_dye_color=['blue'];e.tick()
        self.assertEqual(e.audit.phase,'loading')
        e.until('ready_capture')
        self.assertEqual(native.audit_raw_hero(e.hero),before)
        token=e.audit.capture_token
        e.hero.skins['dye'].getCurDyeScheme=lambda:{'preview_only_color':'different-with-same-owned-dye'}
        e.audit.checkpoint(token,'before')
        self.assertNotEqual(e.audit.phase,'capture_before')
        self.assertEqual(e.audit.result['load_status'],'failed')
        self.assertIn('stability mismatch',e.audit.result['reason'])
        self.assertEqual(native.audit_raw_hero(e.hero),before)

    def test_screenshot_wrong_token_selection_model_epoch_and_owner_fences(self):
        e=self.env;e.start();e.until('ready_capture');token=e.audit.capture_token
        with self.assertRaisesRegex(ValueError,'Stale'):e.audit.checkpoint('wrong','before')
        self.assertEqual(e.audit.phase,'ready_capture')
        e.panels.hero_wardrobe.skin_uuid='base';e.audit.checkpoint(token,'before')
        self.assertEqual(e.audit.phase,'paused');self.assertNotIn(('on_navigation_canvas_back',),e.calls)
        with self.assertRaisesRegex(RuntimeError,'One outstanding'):e.start()
    def test_permanent_mutation_pauses_never_restores_or_saves(self):
        e=self.env;e.start();e.until('ready_capture');e.hero.wearPendantInfo=[999]
        e.audit.checkpoint(e.audit.capture_token,'before')
        self.assertEqual(e.audit.phase,'paused');self.assertEqual(e.hero.wearPendantInfo,[999])
        self.assertIn('Readonly mutation',e.audit.last['reason'])
        self.assertNotIn(('on_navigation_canvas_back',),e.calls)
    def test_timeout_with_late_original_tasks_pauses_batch_not_next_hero(self):
        e=self.env;e.start(timeout=3);e.tick(2);e.scene.scene_model._task_model='original-task-not-cancelled'
        e.until('paused')
        self.assertEqual(e.audit.last['result']['load_status'],'timeout')
        self.assertEqual(e.scene.scene_model._task_model,'original-task-not-cancelled')
        self.assertNotIn(('on_navigation_canvas_back',),e.calls)
    def test_old_generation_or_replaced_controller_callback_does_not_write_current_status(self):
        e=self.env;e.start();before=Path(e.audit.status_path).read_text();e.gg._f7_readonly_wardrobe_audit=object();e.tick()
        self.assertEqual(Path(e.audit.status_path).read_text(),before)
    def test_ias_and_exact_catalog_preview_routes_no_uuid_or_dye_alias_fabrication(self):
        e=self.env;e.hero.skins['dye'].isInvisibleAwakeSkin=True;e.panels.hero_wardrobe.skin_comps=[]
        e.start();e.until('ready_capture');self.assertEqual(e.audit.route['kind'],'owned_ias')
        # Direct route selection can see filtered non-ias instances, but only
        # original offered catalog components can then authorize a preview.
        e.hero.skins['dye'].isInvisibleAwakeSkin=False
        self.assertEqual(native.audit_route(e.panels.hero_wardrobe,e.hero,10080)['kind'],'catalog')
    def test_owner_proxy_scene_panel_and_model_epoch_changes_pause_without_auto_back(self):
        for kind in ('owner','proxy','scene','panel','model'):
            with self.subTest(kind=kind):
                e=FakeNative(self.folder.name);self.env=e;e.start();e.until('ready_capture');token=e.audit.capture_token
                if kind=='owner':e.gg.avatar=object()
                elif kind=='proxy':e.gg._f7_avatar_proxy=object()
                elif kind=='scene':e.scene=NS()
                elif kind=='panel':e.panels.hero_model.visible=False
                else:e.replace_model(30141)
                e.audit.checkpoint(token,'before')
                self.assertEqual(e.audit.phase,'paused');self.assertNotIn(('on_navigation_canvas_back',),e.calls)
    def test_catalog_displayed_dye_pair_and_unreachable_cleanup_use_only_original_routes(self):
        for offered in (True,False):
            with self.subTest(offered=offered):
                e=FakeNative(self.folder.name);self.env=e;e.hero.skins['dye'].forbid=True
                e.panels.hero_wardrobe.comp_wardrobe.skins=[99]
                e.panels.hero_wardrobe.comp_wardrobe.sub_comps=[NS(skin_id=99,dye_skin=10080,_node=NS(isVisible=lambda:True))]if offered else[]
                e.start()
                if offered:
                    e.until('ready_capture');self.assertIn(('ue_explor_skin',99,True,10080),e.calls)
                    token=e.audit.capture_token;e.audit.checkpoint(token,'before');e.now+=.1
                    e.audit.checkpoint(token,'after',{'token':token,'sha256':'a'*64,'path':'actor.png'})
                    e.until('idle');self.assertEqual(e.audit.last['result']['load_status'],'loaded_unreviewed')
                else:
                    e.until('idle');self.assertEqual(e.audit.last['result']['load_status'],'original_UI_unreachable')
                    self.assertFalse(any(c[0]=='ue_explor_skin'for c in e.calls))
                self.assertIn(('enter_buy',),e.calls);self.assertIn(('exit_buy',),e.calls)
                self.assertEqual(e.hero.curSkin,'base');self.assertEqual(e.hero.wearPendantInfo,[8])
    def test_recover_requires_actor_original_return_drained_tasks_and_same_permanent_state(self):
        e=self.env;e.start();e.until('ready_capture');e.panels.hero_wardrobe.skin_uuid='base'
        e.audit.checkpoint(e.audit.capture_token,'before');self.assertEqual(e.audit.phase,'paused')
        with self.assertRaises(ValueError):e.audit.recover()
        old_scene=e.scene;e.back();old_scene.scene_model._task_model='late'
        with self.assertRaisesRegex(ValueError,'queues'):e.audit.recover()
        self.assertEqual(old_scene.scene_model._task_model,'late')
        old_scene.scene_model._task_model=None;generation=e.audit.generation;e.audit.recover()
        self.assertEqual(e.audit.phase,'idle');self.assertGreater(e.audit.generation,generation)

    def test_missing_readiness_fields_are_not_defaulted_to_ready_and_stability_spacing(self):
        e=self.env;e.open(99);del e.scene.scene_model._awake_task
        row=native.audit_readiness(e.scene,e.panels.hero_model,10129)
        self.assertFalse(row['ready']);self.assertIn('scene_model._awake_task',row['missing'])
        rows=[{'ready':True,'fingerprint':'same','time':t}for t in(1.,1.5,2.)]
        self.assertTrue(native.audit_stable(rows));rows[1]['time']=1.49;self.assertFalse(native.audit_stable(rows))
    def test_real_disk_envelope_payload_profiles_detect_changes_and_reject_damage(self):
        e=self.env;raw=e.save.read_bytes();profile,metadata=native.audit_disk_profile(raw)
        self.assertEqual(profile,e.profile);self.assertEqual(metadata['format'],1)
        envelope=json.loads(raw);envelope['payload']=json.dumps(envelope['payload'])
        self.assertEqual(native.audit_disk_profile(json.dumps(envelope))[0],e.profile)
        for bad in ({'profile':e.profile},{'format':1,'payload':None}):
            with self.assertRaises(ValueError):native.audit_disk_profile(json.dumps(bad))
        for payload in (None,{}, {'profile':None},'broken JSON'):
            damaged=json.loads(raw);damaged['payload']=payload
            with self.assertRaises(ValueError):native.audit_disk_profile(json.dumps(damaged))
        e.start();e.until('ready_capture')
        envelope=json.loads(raw);envelope['payload']['profile']['heroes']['99']['cs']='changed-on-disk'
        e.save.write_text(json.dumps(envelope));changed=e.save.read_bytes()
        e.audit.checkpoint(e.audit.capture_token,'before')
        self.assertEqual(e.audit.phase,'paused');self.assertIn('stored_profile',e.audit.last['reason'])
        self.assertEqual(e.save.read_bytes(),changed) # Never restore or re-encode user store.

    def test_run_owner_proxy_identity_cannot_change_between_jobs_even_with_same_profile(self):
        e=self.env;e.audit.inventory()
        e.gg.avatar=NS(heroMgrData=e.owner.heroMgrData)
        e.gg._f7_avatar_proxy=NS(owner=e.gg.avatar,profile=e.profile)
        with self.assertRaisesRegex(ValueError,'run owner/proxy'):e.audit.inventory()
        with self.assertRaisesRegex(ValueError,'run owner/proxy'):e.start()

    def test_no_native_assert_or_forbidden_mutating_handler_calls(self):
        source=host.PROBE.read_text(encoding='ascii');tree=ast.parse(source)
        self.assertFalse(any(isinstance(node,ast.Assert)for node in ast.walk(tree)))
        denied={'setSkinRequest','ue_skin_click','buySkin','sellSkin','setAwakeStage','setAwakeSkinStyle','setWearPendant','getPersistentDict'}
        called={node.func.attr for node in ast.walk(tree)if isinstance(node,ast.Call)and isinstance(node.func,ast.Attribute)}
        self.assertFalse(called&denied)

class HostAuditTests(unittest.TestCase):
    def test_default_cli_is_plan_only_and_keeps494_appearances_no_model_dedup(self):
        heroes={1:{},46:{},125:{}};skins={1:{'hero':1,'model_id':10},2:{'hero':1,'model_id':10,'is_dye_skin':True}}
        with tempfile.TemporaryDirectory()as folder,patch.object(host,'original_tables',return_value=(heroes,skins)),patch.object(host.subprocess,'check_output',side_effect=RuntimeError('NO ADB')),patch.object(host,'run_audit',side_effect=RuntimeError('NO EXECUTION')):
            self.assertEqual(host.main(['--out-dir',folder]),0)
            plan=json.loads((Path(folder)/'plan.json').read_text());self.assertEqual(len(plan['jobs']),5)
            self.assertEqual(sum(j['kind']=='skin'for j in plan['jobs']),2)
            self.assertEqual(plan['denominators']['dye_rows'],1)
            self.assertEqual((Path(folder)/'plan.json').stat().st_mode&0o777,0o600)
    def test_actual_catalog_plan140_494_99_and_hidden_separate(self):
        heroes,skins=host.original_tables();plan=host.make_plan(heroes,skins,run_id='offline-test')
        self.assertEqual(plan['denominators'],{'heroes':140,'skins':494,'dye_rows':99})
        self.assertEqual(len(plan['jobs']),634)
        self.assertEqual(len({j['template_id']for j in plan['jobs']if j['kind']=='skin'}),494)
        self.assertEqual({j['hero_id']for j in plan['jobs']if j['catalog_hidden_no_model']},{46,125})
    def test_status_parser_transport_serial_rpc_classification_and_no_execution_on_constructor(self):
        self.assertEqual(host.parse_status(json.dumps({'protocol':1,'run_id':'r','job_id':'j','phase':'cleanup'}),'r','j')['phase'],'cleanup')
        with self.assertRaises(ValueError):host.parse_status('{"protocol":1,"run_id":"wrong","phase":"idle"}','r')
        with self.assertRaises(ValueError):host.parse_status('{"protocol":1,"run_id":"r","job_id":"other","phase":"idle"}','r','j')
        with patch.object(host.subprocess,'check_output',side_effect=RuntimeError('NO ADB')):
            host.AdbTransport('emulator-5554')
            with self.assertRaises(ValueError):host.AdbTransport('physical-device')
        events=host.rpc_observations('1 RPC setSkinRequest {}\n2 RPC setSkinSeen {}\n3 RPC BUSINESS UNIMPLEMENTED buySkin {}\n4 RPC heartbeat {}\n5 other dye text')
        self.assertEqual([r['kind']for r in events],['forbidden','bookkeeping_or_read','forbidden','bookkeeping_or_read'])
    def test_nested_rpc_envelopes_are_exact_and_never_hide_writes(self):
        rows=["RPC reliableRpcCall {'w': {'m': 'pullEvents', 'p': {}, 'r': 57}, '_cbid_': 51}",
            'RPC reliableRpcCall {"w":{"m":"pullEvents","p":{},"r":57}}',
            "RPC reliableRpcCall {'w': {'m': 'setSkinRequest', 'p': {}, 'r': 1}}",
            "RPC reliableRpcCall {'w': {'m': 'reliableRpcCall', 'p': {'w': {'m': 'buySkin'}}, 'r': 1}}",
            "RPC reliableRpcCall {'w': {'m': 'pullEvents', 'p': {'h': 8}, 'r': 1}}",
            "RPC reliableRpcCall {'w': {'m': 'pullEvents', 'p': {}, 'r': True}}",
            "RPC reliableRpcCall {'w': {'m': 'pullEvents', 'p': {}, 'r': 1}, 'unexpected': 1}",
            "RPC reliableRpcCall {'w': broken",'RPC reliableRpcCall',
            "RPC reliableRpcCall {'w': {'m': 'unknownRead', 'p': {}, 'r': 1}}"]
        events=host.rpc_observations('\n'.join(rows))
        self.assertEqual([r['kind']for r in events],['derived_event_refresh','derived_event_refresh','forbidden']+['unclassified']*7)
        self.assertEqual(events[0]['inner_method'],'pullEvents')
        self.assertEqual(events[0]['line'],rows[0])

    def test_listener_noop_requires_exact_observed_parameters_and_matching_diagnostic(self):
        rows=["RPC regist_chat_channel_listener {'cn': 1, 'scn': 1}",
            'RPC UNIMPLEMENTED regist_chat_channel_listener',
            'RPC UNIMPLEMENTED regist_chat_channel_listener',
            "RPC regist_chat_channel_listener {'cn': 2, 'scn': 1}",
            "RPC regist_chat_channel_listener {'cn': True, 'scn': 1}",
            "RPC regist_chat_channel_listener {'cn': 1, 'scn': 1, 'extra': 1}",
            "RPC other_chat_read {}"]
        events=host.rpc_observations('\n'.join(rows))
        self.assertEqual([r['kind']for r in events],['verified_listener_noop']*2+['unclassified']*5)
        self.assertEqual(host.rpc_observations(rows[1])[0]['kind'],'unclassified')
        self.assertEqual(host.rpc_observations('RPC unknown_read_or_seen {}')[0]['kind'],'unclassified')

    def test_resume_attempt_budget_and_artifacts_never_overwrite_evidence(self):
        with tempfile.TemporaryDirectory()as folder:
            out=Path(folder);self.assertEqual(host.next_attempt([], 'j',out),0)
            original=out/'j-attempt0.png';host.exclusive_write(original,b'old screenshot')
            self.assertEqual(host.next_attempt([], 'j',out),1)
            self.assertEqual(host.next_attempt([{'job_id':'j','attempt':0}], 'j',out),1)
            with self.assertRaises(FileExistsError):host.exclusive_write(original,b'replaced')
            self.assertEqual(original.read_bytes(),b'old screenshot')
            host.exclusive_write(out/'j-attempt1.reserved',b'crashed before checkpoint')
            with self.assertRaisesRegex(RuntimeError,'budget exhausted'):host.next_attempt([], 'j',out)
            with self.assertRaisesRegex(RuntimeError,'budget exhausted'):host.next_attempt([{'job_id':'j','attempt':1}], 'j',out)
            with self.assertRaises(ValueError):host.next_attempt([{'job_id':'j','attempt':False}], 'j',out)

    def test_frame_handshake_rejects_old_epoch_and_does_not_grant_visual_pass(self):
        before={'generation':1,'token':'t','sample':{'fingerprint':'f','epoch':[1,2,3],'time':1}}
        after={'generation':1,'result':{'token':'t','after':{'fingerprint':'f','epoch':[1,2,3],'time':2}}}
        frame={'token':'t','sha256':'a'*64,'host_before':4,'host_captured':5,'host_after':6}
        host.validate_frame(before,after,frame)
        after['result']['after']['epoch']=[1,2,4]
        with self.assertRaises(ValueError):host.validate_frame(before,after,frame)
        plan={'jobs':[{}],'denominators':{'heroes':140,'skins':494}}
        records=[{'job_id':'j','result':{'load_status':'loaded_unreviewed'},'visual_review':{'verdict':'unreviewed'}}]
        self.assertEqual(host.summarize(records,plan)['statuses'],{'loaded_unreviewed':1})
        records[0]['visual_review']['verdict']='pass'
        self.assertEqual(host.summarize(records,plan)['statuses'],{'rendered_and_visually_reviewed':1})
    def test_host_orchestrator_end_to_end_fake_transport_handshake_and_checkpoint(self):
        with tempfile.TemporaryDirectory()as folder:
            out=Path(folder);e=FakeNative(folder)
            (out/'offline_progress.json').write_bytes(e.save.read_bytes())
            gpu=out/'gpu.json';gpu.write_text(json.dumps({'renderer':'mock','backend':'mock','device':'mock'}))
            submissions=[]
            class Transport:
                surfaceflinger_raw='mock offline test'
                def __init__(self,*a):pass
                def provenance(self,*a):return {'apk_sha256':'a'*64,'script_sha256':'b'*64,'gpu':'mock','resolution':'Physical size:1x1'}
                def submit(self,source,output):
                    submissions.append(source)
                    exec(compile(source,'fake-original-development-transport','exec'),{})
                def read(self,path):
                    e.tick()
                    return Path(host.STATUS).read_text()
                def shell(self,*args):return '0 offline_runtime.log'if args[0]=='wc'else''
                def run(self,*args,**kw):
                    e.now+=.1
                    def chunk(kind,data):return struct.pack('>I',len(data))+kind+data+struct.pack('>I',zlib.crc32(kind+data)&0xffffffff)
                    return b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>IIBBBBB',1,1,8,6,0,0,0))+chunk(b'IDAT',zlib.compress(b'\0\0\0\0\0'))+chunk(b'IEND',b'')
            plan=host.make_plan({99:{}},{10080:{'hero':99,'model_id':30141}},run_id='mock-run')
            plan['jobs']=[j for j in plan['jobs']if j['kind']=='skin']
            args=NS(gpu_provenance=gpu,serial='emulator-5554',adb=None,device_script='/mock/script',resume=False,timeout=5)
            with patch.dict(sys.modules,{'gg':e.gg,'com.const':NS(SCENE_HERO=1)}),patch.object(host,'AdbTransport',Transport),patch.object(host,'DOCS',folder),patch.object(host,'STATUS',str(out/'status.json')),patch.object(host.time,'sleep',lambda delay:None),patch.object(native.time,'time',lambda:e.now):
                host.run_audit(args,plan,out)
            rows=[json.loads(line)for line in(out/'checkpoint.jsonl').read_text().splitlines()]
            self.assertEqual(rows[0]['result']['load_status'],'loaded_unreviewed')
            self.assertEqual(rows[0]['frame']['sha256'],host.digest(Path(rows[0]['frame']['path']).read_bytes()))
            self.assertEqual(json.loads((out/'summary.json').read_text())['statuses'],{'loaded_unreviewed':1})
            self.assertEqual(json.loads((out/'inventory.json').read_text())['inventory']['digest'],json.loads((out/'inventory-final.json').read_text())['inventory']['digest'])
            self.assertEqual(len(submissions),5) # install/start/before/after/batch-final inventory.
            self.assertFalse(any(c[0]in('setSkinRequest','buySkin')for c in e.calls))
    def test_status_nonce_rejects_prior_idle_on_same_job_retry(self):
        packet=json.dumps({'protocol':1,'run_id':'r','job_id':'same','phase':'idle','request_nonce':'old'})
        with self.assertRaisesRegex(ValueError,'nonce'):host.parse_status(packet,'r','same','new')
        self.assertEqual(host.parse_status(packet,'r','same','old')['phase'],'idle')

    def test_png_and_resolution_parser_reject_header_only_or_wrong_dimensions(self):
        with self.assertRaises(ValueError):host.png_dimensions(b'\x89PNG\r\n\x1a\nnot-an-image')
        self.assertEqual(host.active_resolution('Physical size:1080x1920\nOverride size:720x1280'),[720,1280])
        with self.assertRaises(ValueError):host.active_resolution('unknown')

    def test_android_installed_path_and_packaged_script_stream_transport_without_adb(self):
        transport=host.AdbTransport('emulator-5554');apk='/data/app/~~a+b==/com.netease.qrzd-x==/base.apk'
        with patch.object(transport,'shell',return_value='a'*64+'  '+apk):
            self.assertEqual(transport.remote_sha(apk),'a'*64)
            with self.assertRaises(ValueError):transport.remote_sha('/data/app/../other')
        process=NS(communicate=lambda timeout:(b'original-script-bytes',b''),returncode=0)
        with patch.object(host.subprocess,'Popen',return_value=process)as popen:
            self.assertEqual(transport.packaged_script_sha(apk),host.digest(b'original-script-bytes'))
            self.assertEqual(popen.call_args.args[0][-5:],['exec-out','unzip','-p',apk,'assets/script.npk'])
    def test_default_plan_refuses_to_overwrite_existing_run_metadata(self):
        with tempfile.TemporaryDirectory()as folder,patch.object(host,'original_tables',return_value=({99:{}},{99:{'hero':99}})):
            host.main(['--out-dir',folder])
            raw=(Path(folder)/'plan.json').read_bytes()
            with self.assertRaisesRegex(ValueError,'Existing plan'):host.main(['--out-dir',folder])
            self.assertEqual((Path(folder)/'plan.json').read_bytes(),raw)

    def test_visual_review_cli_is_offline_and_binds_existing_frame_bytes(self):
        with tempfile.TemporaryDirectory()as folder:
            out=Path(folder);plan=host.make_plan({99:{}},{10080:{'hero':99}});host.dump(out/'plan.json',plan)
            image=out/'frame.png';image.write_bytes(b'mock-review-fixture-not-native')
            sha=host.digest(image.read_bytes())
            record={'run_id':plan['run_id'],'job_id':'skin-10080','result':{'load_status':'loaded_unreviewed'},'frame':{'sha256':sha,'path':str(image)}}
            (out/'checkpoint.jsonl').write_text(json.dumps(record)+'\n')
            reviews=out/'reviews.json';reviews.write_text(json.dumps([{'job_id':'skin-10080','frame_sha256':sha,'reviewer':'test-only','verdict':'pass','notes':'Mock fixture, not native material evidence'}]))
            with patch.object(host.subprocess,'check_output',side_effect=RuntimeError('NO ADB')):
                self.assertEqual(host.main(['--review',str(reviews),'--out-dir',folder]),0)
                self.assertEqual(json.loads((out/'summary.json').read_text())['coverage_by_kind']['skin'],{'rendered_and_visually_reviewed':1})
                image.write_bytes(b'modified')
                with self.assertRaisesRegex(ValueError,'bytes changed'):host.main(['--review',str(reviews),'--out-dir',folder])

    def test_command_payload_json_escaping_cannot_escape_source_or_select_other_method(self):
        source=host.source_call('start',{'job_id':"x');bad()\n",'hero_id':99})
        tree=ast.parse(source);self.assertNotIn('bad',{n.func.id for n in ast.walk(tree)if isinstance(n,ast.Call)and isinstance(n.func,ast.Name)})
        with self.assertRaises(ValueError):host.source_call('setSkinRequest',99)

if __name__=='__main__':unittest.main()
