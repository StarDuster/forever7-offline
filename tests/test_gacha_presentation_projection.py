"""Original six-card mask survives delayed native model loading and counters."""
import copy
import ast
import unittest
import random
import textwrap
from types import SimpleNamespace as NS
import test_gacha_gateway_pools as base

ROOT=base.rewards.ROOT

def original(path,name,namespace):
    source=(ROOT/path).read_text();start=source.index('    def '+name+'(')
    end=source.find('\n    def ',start+8)
    body=source[start:end if end>=0 else len(source)].split('\n    @')[0]
    # Only Python2 print/async keyword compatibility, not business behavior.
    body='\n'.join(line for line in body.splitlines()if not line.lstrip().startswith('print '))
    body=body.replace('async=', 'async_cb=')
    exec(compile(textwrap.dedent(body),str(path)+':'+name,'exec'),namespace)
    return namespace[name]

class GachaPresentationProjectionTests(base.GatewayOriginalPoolIntegration):
    def test_normal_original_mask_before_delayed_model_load(self):self._exercise_original_mask(1)

    def test_activity_original_mask_before_delayed_model_load(self):self._exercise_original_mask(5)

    def _exercise_original_mask(self,wire):
        pending=[];models=[]
        class Model:
            def bind_scene(self,scene):pass
            def set_camera(self,camera):pass
            def load_model(self,name,**kwargs):models.append(name)
        scene=NS(scene_id=1,scene_cam=object(),model_card_list=[],get_luckyDraw_type=lambda:wire,
            specital_card_name=['back-special'],normal_card_name=['back-normal'],
            summon_model_dict={'award':(None,'actual-award')},get_summon_type=lambda result,exchange=False:'award')
        self.owner.luckyDrawData.get_draw_info=lambda wire:self.draw_info.get(wire,{})
        gg=NS(avatar=self.owner,scene_mgr=NS(cache={1:object()}))
        ns={'gg':gg,'ui_utils':NS(SceneModel=Model),'random':random,'xrange':range}
        load=original('analysis/research-agent/city_chouka.py','load_card_model',ns)
        box=NS(valid=True,get_luckyDraw_type=lambda:wire,refresh_state=lambda:None,when_in_card_lianchou=lambda:None)
        box.check_file_lianchou=lambda:bool(getattr(box,'file_lianchou_results',[]))
        box.try_file_lianchou_clear=lambda:original('analysis/research-agent/card_box.py','try_file_lianchou_clear',{'gg':gg,'copy':copy})(box)
        def on_reply_request_file(wire,result,info):
            box.try_file_lianchou_clear()
            pending.append(lambda:load(scene,1))
        box.on_reply_request_file=on_reply_request_file
        gg.ui=NS(panels=NS(card_box=box))
        file_reply=original('analysis/research-agent/LuckyDrawMember.py','replyFile',{'gg':gg})
        self.owner.replyFile=lambda payload:file_reply(self.owner,payload['rt'],payload['info'],payload['t'])
        def batch_reply(payload):
            box.file_lianchou_results=payload['trwd'];box.file_lianchou_fake_results=payload['ffs']
        self.owner.replyLuckyDrawFileAndOpenAll=batch_reply
        self.rpc('requestLuckyDrawFileAndOpenAll',{'t':wire})
        saved=copy.deepcopy(self.proxy.progress_snapshot())
        self.assertTrue(all(card['is_open']for card in self.proxy.gacha_pools['pools'][str(wire)]['group']['cards']))
        self.rpc('requestFile',{'t':wire})
        self.assertEqual(len(pending),1)
        # Error and unrelated RPC projections must not clobber this mask either.
        self.rpc('requestLuckyDrawCard',{'t':wire,'idx':99})
        self.assertEqual(self.proxy.progress_snapshot(),saved)
        self.proxy.handle_special_gacha('setChooseHeroes',{'t':354,'h':[8,9]},'mask-special')
        self.assertEqual(self.proxy.progress_snapshot(),saved)
        self.proxy.sync_gacha_native_state(wire) # Default callers are counters-only.
        pending.pop()()
        self.assertEqual(models,['back-normal']*6)
        self.assertEqual(self.proxy.progress_snapshot(),saved)
        self.assertEqual((self.owner.luckyDrawData if wire==1 else self.owner.luckyDrawData.activity_data[wire]).card_times,6)
        self.proxy.handle_dedicated_gacha('requestLuckyDrawFriendCard',{},operation_id='mask-friend')
        self.assertTrue(all(not card['is_open']for card in self.draw_info[wire].values()))
        self.assertEqual(self.proxy.gacha_pools['pools'][str(wire)],saved['gacha_pools']['pools'][str(wire)])
        # The stock per-card update progressively reveals exactly that slot.
        actual_set=original('analysis/research-agent/LuckyDrawData.py','set_draw_info',
            {'const':NS(LuckyDrawType=NS(NORMAL=1))})
        mask=copy.deepcopy(self.draw_info[wire]);data=NS(draw_info=mask,activity_data={wire:NS(draw_info=mask)})
        first=self.proxy.native_gacha_card(self.proxy.gacha_pools['pools'][str(wire)]['group']['cards'][0])
        actual_set(data,wire,first,0)
        self.assertTrue(data.draw_info['0']['is_open'])
        self.assertTrue(all(not data.draw_info[str(i)]['is_open']for i in range(1,6)))
        # A real restored entry hydrates persisted awards, not an obsolete mask.
        restored=base.gateway.LocalProxy(None,self.owner,persistent=True)
        restored.gacha_tables=lambda:self.tables
        restored.sync_gacha_native_state(wire,refresh_cards=True)
        self.assertTrue(all(card['is_open']for card in self.draw_info[wire].values()))
        self.assertEqual(restored.gacha_pools,self.proxy.gacha_pools)

    def test_completed_batch_retries_are_false_and_keep_exact_saved_results(self):
        self.rpc('requestLuckyDrawFileAndOpenAll',{'t':1})
        saved=copy.deepcopy(self.proxy.progress_snapshot())
        for method in('requestLuckyDrawFileAndOpenAll','requestLuckyDrawAllLeftCard'):
            for repeat in range(2):
                replies=self.rpc(method,{'t':1,'_cbid_':77})
                response=next(v for n,v in replies if n==method.replace('request','reply',1))
                self.assertFalse(response['rt']);self.assertEqual(response['trwd'],[])
                self.assertEqual(response['_cbid_'],77)
                self.assertEqual(self.proxy.progress_snapshot(),saved)
        self.rpc('requestQuitFile',{'t':1})
        self.rpc('requestLuckyDrawFileAndOpenAll',{'t':1})
        self.assertEqual(self.proxy.gacha_pools['pools']['1']['opened_total'],12)
        self.assertEqual(self.proxy.gacha_pools['pools']['1']['history'][-1],saved['gacha_pools']['pools']['1']['group'])

    def test_deferred_file_read_lifetime_fences_old_pool_frame_group_and_owner(self):
        from unittest.mock import patch
        panel=NS(valid=True,_node=object(),_f7_presentation_epoch=1)
        scene=object()
        self.engine.ui=NS(panels=NS(card_box=panel))
        self.engine.city_container=NS(get_current_scene=lambda:scene)
        self.rpc('requestLuckyDrawFile',{'t':1})
        source=self.proxy.gacha_presentation_token(1)
        callbacks=[];self.owner.replyFile=lambda payload:callbacks.append(payload)
        saved=copy.deepcopy(self.proxy.progress_snapshot())
        # Same node/scene but a new original init frame is already a stale reply.
        self.proxy.call_server_method('requestFile',{'t':1,'_cbid_':78})
        panel._f7_presentation_epoch+=1
        self.engine.drain()
        self.assertEqual(callbacks,[])
        self.assertEqual(self.draw_info[1]['0']['is_open'],False)
        self.assertIn(('serverCallbackCarrier',{'_r_':True,'_cbid_':78}),self.owner.replies)
        self.assertEqual(self.proxy.progress_snapshot(),saved)
        # Late false from a nonexistent old pool also cannot close this frame.
        source=self.proxy.gacha_presentation_token(5);panel._f7_presentation_epoch+=1
        self.proxy.handle_gacha('requestFile',{'t':5},79,source)
        self.assertEqual(callbacks,[])
        # Failure after a table exception preserves old authoritative data.
        source=self.proxy.gacha_presentation_token(1);panel._f7_presentation_epoch+=1
        before=copy.deepcopy(self.draw_info)
        with patch.object(self.proxy,'gacha_tables',side_effect=ValueError('broken table')):
            self.proxy.handle_gacha('requestFile',{'t':1},80,source)
        self.assertEqual(callbacks,[]);self.assertEqual(self.draw_info,before)
        # Replaced group and replaced owner are independently fenced.
        source=self.proxy.gacha_presentation_token(1)
        self.rpc('requestQuitFile',{'t':1});self.rpc('requestLuckyDrawFile',{'t':1})
        self.proxy.handle_gacha('requestFile',{'t':1},81,source)
        self.assertEqual(callbacks,[])
        self.owner.replies=[]
        before=copy.deepcopy(self.proxy.progress_snapshot())
        self.proxy.call_server_method('requestQuitFile',{'t':1,'_cbid_':83})
        panel._f7_presentation_epoch+=1;self.engine.drain()
        self.assertEqual(self.proxy.progress_snapshot(),before)
        self.assertFalse(any(n=='replyQuitFile'for n,v in self.owner.replies))
        self.assertIn(('serverCallbackCarrier',{'_r_':True,'_cbid_':83}),self.owner.replies)
        self.owner.replies=[]
        self.proxy.call_server_method('requestQuitFile',{'t':1,'_cbid_':84});self.engine.drain()
        self.assertIsNone(self.proxy.gacha_pools['pools']['1']['group'])
        self.assertTrue(next(v for n,v in self.owner.replies if n=='replyQuitFile')['rt'])
        source=self.proxy.gacha_presentation_token(1)
        self.proxy.owner=NS()
        self.proxy.handle_gacha('requestFile',{'t':1},82,source)
        self.assertEqual(callbacks,[])

    def test_rapid_reliable_batch_and_late_single_card_never_retarget_next_group(self):
        for request in(501,502):
            self.proxy.call_server_method('reliableRpcCall',{'w':{'m':'requestLuckyDrawFileAndOpenAll','p':{'t':1},'r':request},'_cbid_':request})
        self.engine.drain()
        batches=[v for n,v in self.owner.replies if n=='replyLuckyDrawFileAndOpenAll']
        self.assertEqual(len(batches),1);self.assertTrue(batches[0]['rt'])
        self.assertEqual(len(batches[0]['trwd']),6)
        self.assertEqual(self.proxy.gacha_pools['pools']['1']['opened_total'],6)
        self.assertIn(('serverCallbackCarrier',{'_r_':True,'_cbid_':502}),self.owner.replies)
        old=copy.deepcopy(self.proxy.gacha_pools['pools']['1']['group'])
        self.proxy.call_server_method('requestLuckyDrawCard',{'t':1,'idx':0,'_cbid_':503})
        self.rpc('requestQuitFile',{'t':1});self.rpc('requestLuckyDrawFile',{'t':1})
        new=copy.deepcopy(self.proxy.progress_snapshot())
        self.engine.drain()
        self.assertEqual(self.proxy.progress_snapshot(),new)
        self.assertTrue(all(not card['is_open']for card in self.proxy.gacha_pools['pools']['1']['group']['cards']))
        self.assertIn(('serverCallbackCarrier',{'_r_':True,'_cbid_':503}),self.owner.replies)
        self.assertEqual(self.proxy.gacha_pools['pools']['1']['history'][-1],old)

    def test_stale_same_wire_read_preserves_new_mask_but_inactive_wire_gets_saved_data(self):
        self.rpc('requestLuckyDrawFileAndOpenAll',{'t':1})
        saved=copy.deepcopy(self.proxy.progress_snapshot())
        current=[1];panel=NS(valid=True,_node=object(),_f7_presentation_epoch=1,get_luckyDraw_type=lambda:current[0])
        self.engine.ui=NS(panels=NS(card_box=panel));self.engine.city_container=NS(get_current_scene=lambda:None)
        mask={str(i):{'index':i,'is_open':False}for i in range(6)}
        self.draw_info[1]=copy.deepcopy(mask)
        callbacks=[];self.owner.replyFile=lambda payload:callbacks.append(payload)
        self.proxy.call_server_method('requestFile',{'t':1,'_cbid_':91})
        panel._f7_presentation_epoch+=1;self.engine.drain()
        self.assertEqual(callbacks,[]);self.assertEqual(self.draw_info[1],mask)
        self.assertEqual(self.proxy.progress_snapshot(),saved)
        self.proxy.call_server_method('requestFile',{'t':1,'_cbid_':92})
        current[0]=5;self.engine.drain()
        self.assertEqual(callbacks,[])
        self.assertTrue(all(card['is_open']for card in self.draw_info[1].values()))
        self.assertEqual(self.proxy.progress_snapshot(),saved)

for name in list(vars(base.GatewayOriginalPoolIntegration)):
    if name.startswith('test_'):setattr(GachaPresentationProjectionTests,name,None)

class PresentationHydrationBoundaryTests(unittest.TestCase):
    def test_full_card_hydration_only_at_explicit_avatar_or_scene_entry(self):
        full=[];calls=[]
        for path in sorted((ROOT/'runtime').glob('*.py')):
            source=path.read_text()
            if 'sync_gacha_native_state('not in source:continue
            tree=ast.parse(source)
            def visit(node,scope='module'):
                if isinstance(node,ast.FunctionDef):scope=node.name
                if isinstance(node,ast.Call)and isinstance(node.func,ast.Attribute)and node.func.attr=='sync_gacha_native_state':
                    flag=next((kw.value for kw in node.keywords if kw.arg=='refresh_cards'),None)
                    calls.append((path.name,scope))
                    if flag is not None:
                        self.assertIsInstance(flag,ast.Constant)
                        if flag.value is True:full.append((path.name,scope))
                for child in ast.iter_child_nodes(node):visit(child,scope)
            visit(tree)
        self.assertEqual(set(full),{('local_gateway.py','create_avatar'),('local_gateway.py','process_week_operation'),('offline_gacha_ui.py','enabled_entry')})
        self.assertTrue(calls)
        tree=ast.parse((ROOT/'runtime/local_gateway.py').read_text())
        sync=next(node for node in ast.walk(tree)if isinstance(node,ast.FunctionDef)and node.name=='sync_gacha_native_state')
        self.assertIs(sync.args.defaults[-1].value,False)

class GachaFailureReplyAdapterTests(unittest.TestCase):
    def test_original_open_failure_retains_controls_and_success_runs_original_animation(self):
        from unittest.mock import patch
        import sys
        import offline_gacha_ui as ui
        events=[]
        node=lambda name:NS(setVisible=lambda value:events.append((name,value)))
        action=lambda name:NS(start=lambda:events.append((name,'start')),stop=lambda:events.append((name,'stop')))
        scene=NS(on_reply_draw_file=lambda value:events.append(('scene',value)))
        box=NS(valid=True,scene_type='normal',get_scene_type=lambda wire:'normal',get_luckyDraw_type=lambda:1,
            set_is_open_file=lambda value:events.append(('opened',value)),notify_open_file=lambda value:events.append(('notify',value)),
            set_state=lambda value:events.append(('state',value)),btn_progress=node('progress'),refresh_state=lambda:events.append(('refresh',True)))
        proxy=NS(gacha_pools={'pools':{}},sync_gacha_native_state=lambda wire:events.append(('sync',wire)))
        gg=NS(_f7_avatar_proxy=proxy,city_container=NS(get_scene_by_key=lambda key:scene,check_scene=lambda value:True),
            ui=NS(actions=NS(card_box=NS(main_in=action('main_in'),main_close=action('main_close')))))
        raw=original('analysis/research-agent/card_box.py','on_reply_draw_file',{'gg':gg,'const':NS(SCENE_SUMMON=1)})
        hook=ui.make_gacha_draw_file_reply_hook(raw)
        with patch.dict(sys.modules,{'gg':gg}):
            hook(box,False,1)
            self.assertEqual(events,[('sync',1),('opened',False),('refresh',True)])
            events[:]=[];hook(box,True,1)
            self.assertIn(('scene',True),events);self.assertIn(('main_close','start'),events)
            self.assertIn(('notify',False),events)
            events[:]=[];box.get_luckyDraw_type=lambda:5;hook(box,False,1)
            self.assertEqual(events,[])

    def test_original_quit_false_only_releases_its_cover_and_true_uses_scene_callback(self):
        import offline_gacha_ui as ui
        events=[];callbacks=[]
        scene=NS(on_reply_quit_file=lambda result,cb:callbacks.append(cb)if result else None,
            begin_change_scene_to_chouka_main=lambda **kw:events.append('transition'))
        box=NS(valid=True,is_cover=True,cover=True,draw_type=1,get_luckyDraw_type=lambda:1,
            refresh_state=lambda:events.append('refresh'),set_is_open_file=lambda value:events.append(('opened',value)),
            reset_file_lianchou_info=lambda:events.append('reset'),item_nml_panel=NS(setVisible=lambda value:None,setTouchEnabled=lambda value:None))
        gg=NS(city_container=NS(get_scene_by_key=lambda key:scene,check_scene=lambda value:True))
        raw=original('analysis/research-agent/card_box.py','on_reply_quit_file',{'gg':gg,'const':NS(SCENE_SUMMON=1)})
        hook=ui.make_gacha_quit_file_reply_hook(raw)
        hook(box,False)
        self.assertFalse(box.is_cover);self.assertTrue(box.cover)
        self.assertEqual(events,[]);self.assertEqual(callbacks,[])
        box.is_cover=True;hook(box,True)
        self.assertTrue(box.is_cover);callbacks.pop()()
        self.assertFalse(box.is_cover);self.assertIn('transition',events)

    def test_original_quit_click_failed_reply_and_200ms_controls_restore(self):
        import offline_gacha_ui as ui
        queue=[];touch={};scene=NS(card_opening=False)
        box=NS(valid=True,is_cover=False,cover=True,is_open_file=True,get_luckyDraw_type=lambda:1)
        for name in('btn_normal_open_once','btn_normal_open_all','btn_card_once','btn_card_left_or_ten'):
            setattr(box,name,NS(setTouchEnabled=lambda value,name=name:touch.update({name:value})))
        failed=ui.make_gacha_quit_file_reply_hook(lambda *args:self.fail('False quit must not start scene transition'))
        gg=NS(audio_mgr=NS(ui_sound=lambda sound:None),city_container=NS(get_current_scene=lambda:scene),
            avatar=NS(luckyDrawData=NS(getOpenTimes=lambda wire:6),notify_normal_close_file=lambda wire:queue.append((1,lambda:failed(box,False)))),
            exec_delay=lambda delay,cb:queue.append((delay,cb)))
        click=original('analysis/research-agent/card_box.py','on_quit_click',{'gg':gg,'cc':NS(ccui=NS(TOUCH_EVENT_ENDED=2))})
        click(box,None,2)
        self.assertTrue(box.is_cover);self.assertTrue(scene.card_opening)
        self.assertFalse(any(touch.values()))
        queue.sort(key=lambda row:row[0]);queue.pop(0)[1]()
        self.assertFalse(box.is_cover);self.assertTrue(box.cover)
        queue.pop(0)[1]()
        self.assertFalse(scene.card_opening);self.assertTrue(all(touch.values()))

    def test_original_cross_wire_file_reply_does_not_touch_active_panel(self):
        import offline_gacha_ui as ui
        events=[]
        box=NS(valid=True,get_luckyDraw_type=lambda:5,set_is_open_file=lambda result:events.append(('opened',result)),
            refresh_state=lambda:None,try_file_lianchou_clear=lambda:None)
        scene=NS(on_reply_request_file=lambda result,info:events.append(('scene',result)))
        gg=NS(city_container=NS(get_scene_by_key=lambda key:scene,check_scene=lambda value:True))
        raw=original('analysis/research-agent/card_box.py','on_reply_request_file',{'gg':gg,'const':NS(SCENE_SUMMON=1)})
        hook=ui.make_gacha_request_file_reply_hook(raw)
        hook(box,1,True,{'0':{}});hook(box,1,False,{})
        self.assertEqual(events,[])
        hook(box,5,True,{'0':{}});self.assertIn(('scene',True),events)
