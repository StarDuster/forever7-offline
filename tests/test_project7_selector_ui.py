"""Actual640 choice request/typed reply/popup bodies with inert widget probes.
Frozen draw+friend installers coexist; no game/native scene execution.
"""
import ast,base64,contextlib,hashlib,importlib.util,io,json,sys,types,unittest
from pathlib import Path
from unittest.mock import patch
from tools.project7_selector_catalog import ui_policy,canonical
ROOT=Path(__file__).resolve().parents[1];NS=types.SimpleNamespace

def module(name,path):
 s=importlib.util.spec_from_file_location(name,ROOT/path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
friend=module('selector_friend_fixture','tests/test_project7_friend_ui.py');ui=module('selector_ui','runtime/project7_selector_ui.py');original=friend.original
class SelectorUiTests(unittest.TestCase):
 def setUp(self):
  friend.FriendUiTests.setUp(self)
  self.events=[];self.timers=[];self.tip_callbacks=[];self.confirm_callback=None
  self.gg.exec_delay=lambda ms,cb:(self.timers.append(cb) or len(self.timers))
  self.const.RotationType=NS(SELF_CHOOSE_HERO=314);self.const.DEBUG=False;self.const.LuckyDrawType.DUMP_TYPES=()
  heroes={h:{'hero_composite_init_rank':rank,'name':str(h)} for rank,ids in [(4,[67,91,121,135]),(3,[83,92,103,117])] for h in ids}
  roster={h:{'avaliable':int(h not in (135,117))} for h in heroes}
  self.env['filter']=lambda f,x:list(filter(f,x))
  self.env.update(HERO_DATA=NS(data=heroes),HERO_SELF_CHOOSE_INFO=NS(data=roster),helpers=NS(get_active_uaid=lambda r:(1,{'self_choose_S':[135],'self_choose_A':[117]})))
  for name in ('validSetChooseHeroes','setChooseHeroes'):
   setattr(self.Avatar,name,original('analysis/original-py-640/entity/avatar_members/LuckyDrawMember.py',name,self.env))
  self.Avatar.checkDrawInTime=lambda a,t:t==484
  for name in ('_genReliableRpcSeq','callServerMethodReliable','reSendRpc','_runRpc'):
   setattr(self.Avatar,name,original('analysis/original-py-640/entity/avatar_members/ReliableRpcMember.py',name,self.env))
  # Real original argument schema and rpc decorator class construction.
  old=module('selector_consumer_fixture','runtime/android_selector_draw/host_tests/consumers.py').old
  self.env.update(CLIENT_STUB=3,StandardError=Exception,_logger=NS(warn=lambda *a:None,error=lambda *a:None),EntityManager=NS(getentity=lambda p:None))
  for path,names in [('analysis/original-py-640/lib/common/RpcMethodArgs.py',['ConvertError','RpcMethodArg','NoLimit','NumeralLimit','Int','Bool','List','Dict','Avatar','MailBox']),('analysis/original-py-640/lib/common/rpcdecorator.py',['RpcMethod','rpc_method'])]:
   tree=ast.parse(str(old.FIX.refactor_string((ROOT/path).read_text(),path)));body=[n for n in tree.body if isinstance(n,(ast.FunctionDef,ast.ClassDef)) and n.name in names];exec(compile(ast.Module(body=body,type_ignores=[]),path+':selected','exec'),self.env)
  reply=original('analysis/original-py-640/entity/avatar_members/LuckyDrawMember.py','replySetChooseHeroes',self.env);self.Avatar.replySetChooseHeroes=self.env['rpc_method'](3,(self.env['Int']('r'),self.env['Int']('t'),self.env['List']('h')))(reply)
  self.Tab=self.classes[0]
  for n in ('on_init','on_open_choose_click'):setattr(self.Tab,n,original('analysis/original-py-640/cocos/panels/card_tab.py',n,self.env))
  for n in ('on_navigation_canvas_back','on_navigation_canvas_rebuild','on_navigation_canvas_ck','update_tips_info'):
   if not hasattr(self.Tab,n):setattr(self.Tab,n,lambda *a:None)
  self.Chooser=type('Panel',(),{})
  for n in ('notify_show','notify_close','on_close_click','on_btn_click'):setattr(self.Chooser,n,original('analysis/original-py-640/cocos/panels/card_hero_choose.py',n,self.env))
  tree=ast.parse(str(old.FIX.refactor_string((ROOT/'analysis/original-py-640/cocos/panels/card_hero_choose.py').read_text(),'chooser')));body=[n for n in tree.body if isinstance(n,ast.ClassDef) and n.name in ('UIConfig','UILogic')];exec(compile(ast.Module(body=body,type_ignores=[]),'chooser:selected','exec'),self.env)
  join=original('analysis/original-py-640/cutils/chelpers.py','join_ui_config',self.env,top=True)
  self.env['chelpers']=NS(join_ui_config=join,panel_notify_show_custom=lambda panel,custom:self.events.append(('custom',custom)))
  self.ChooserModule=types.ModuleType(ui._CHOOSER);self.ChooserModule.Panel=self.Chooser;self.ChooserModule.UIConfig=self.env['UIConfig'];self.ChooserModule.UILogic=self.env['UILogic']
  p=patch.dict(sys.modules,{ui._CHOOSER:self.ChooserModule});p.start();self.addCleanup(p.stop)
  self.Data=type('LuckyDrawData',(),{'getChooseHeroes':original('analysis/original-py-640/entity/avatar_attrs/LuckyDrawData.py','getChooseHeroes',self.env)})
  self.DataModule=types.ModuleType(ui._DATA);self.DataModule.LuckyDrawData=self.Data
  dp=patch.dict(sys.modules,{ui._DATA:self.DataModule});dp.start();self.addCleanup(dp.stop)
  self.policy=ui_policy();self.text=canonical(self.policy).decode('ascii')
  self.gg.avatar=None;self.selector=ui.install(self.text,friend.draw.policy._HistoryAvatar);self.gg.avatar=self.actor()
  self.gg.ui._tree=NS(proc_event=lambda name,**k:self.events.append(('event',name)))
  self.gg.ui.panels.common_confirm=NS(notify_confirm=lambda *a,**k:self.tip_callbacks.append(a[1] if len(a)>1 else k['confirm_cb']))
  self.gg.ui.panels.card_tab=None
  self.old=old
 def actor(self):
  a=friend.FriendUiTests.actor(self);a.rpcSeq=0;a.reliableRpcCache={};a.reliableRpcTimer={};a.reliableRpcState=True;a.clientSeq=0
  a.heroMgrData=NS(getHero=lambda h:None)
  a.luckyDrawData.activity_data={t:NS(choose_heroes=[0,0,0]) for t in (265,369,427,454,455,484)}
  if hasattr(self,'Data'):
   values=dict(a.luckyDrawData.__dict__);values.pop('getChooseHeroes',None);a.luckyDrawData=self.Data();a.luckyDrawData.__dict__.update(values)
  else:
   get=original('analysis/original-py-640/entity/avatar_attrs/LuckyDrawData.py','getChooseHeroes',self.env);a.luckyDrawData.getChooseHeroes=types.MethodType(get,a.luckyDrawData)
  a.server=NS(call_server_method=lambda name,params,entityid:self.sent.append((name,dict(params))))
  return a
 def popup(self,t=265):
  p=self.Tab();p.valid=True;p.on_init();p.draw_type=t
  chooser=self.Chooser();chooser.valid=True;chooser._node=friend.draw.Widget();chooser.curr_idx=0;chooser.ui_logic=self.env['UILogic'];chooser.ui_config=self.env['UIConfig']
  chooser.window_popup=lambda cb:cb();chooser.window_set_bg_close=lambda cb:None;chooser.destroy_self_layer=lambda:self.events.append(('destroy',))
  self.gg.ui.panels.card_tab=p;self.gg.ui.panels.card_hero_choose=chooser
  p.add_layer=lambda layer:layer
  p.proc_event=lambda name,**kwargs:kwargs.pop('_layer').notify_show(**kwargs)
  p.on_open_choose_click(None,2)
  return p,chooser
 def choose(self,t=265):
  p,c=self.popup(t);c.choose_heroes=[83,67];c.curr_idx=1;c.ui_logic.on_click_done(c);self.assertTrue(self.tip_callbacks);self.tip_callbacks.pop()();return p,c
 def fixture(self,name):
  d=json.loads((ROOT/'reports/project7-selector-ui-host-fixtures.json').read_text());return self.old.bson(base64.b64decode(d['fixtures'][name]))
 def test_original_popup_fixed_roster_and_original_reliable_request(self):
  p,c=self.popup();self.assertEqual(c.ui_logic.get_select_heroes(c),[83,92,103]);c.curr_idx=1;self.assertEqual(c.ui_logic.get_select_heroes(c),[67,91,121]);self.assertTrue(any('640' in text for path,text in c.custom['text'] if path=='popup.text'))
  c.choose_heroes=[83,67];c.curr_idx=1;c.ui_logic.on_click_done(c);self.tip_callbacks.pop()();self.assertEqual(self.sent[-1][0],'reliableRpcCall');self.assertEqual(self.sent[-1][1]['w']['m'],'setChooseHeroes');self.assertEqual(self.sent[-1][1]['w']['p'],{'t':265,'h':[83,67]});self.assertEqual(self.gg.ui._lock['setChooseHero'],1);self.assertEqual(len(self.gg.avatar.reliableRpcCache),1)
 def test_actual_typed_success_and_failure_via_original_runrpc(self):
  for t in (265,369,427,454,455):
   self.gg.avatar=self.actor();self.choose(t);self.gg.avatar._runRpc('replySetChooseHeroes',self.fixture('history_choose_'+str(t)),None);self.assertEqual(sum(self.gg.ui._lock.values()),0);self.assertEqual(self.gg.avatar.luckyDrawData.activity_data[t].choose_heroes,self.fixture('history_choose_'+str(t))['h'])
   self.gg.avatar=self.actor();self.choose(t);self.gg.avatar._runRpc('replySetChooseHeroes',self.fixture('history_choose_failure_'+str(t)),None);self.assertEqual(sum(self.gg.ui._lock.values()),0);self.assertEqual(self.gg.avatar.luckyDrawData.activity_data[t].choose_heroes,[0,0,0])
 def test_metadata_call_five_pool_success_false_and_stale_owners(self):
  meta=self.Avatar.replySetChooseHeroes.rpcmethod
  original_meta=self.selector.originals['replySetChooseHeroes'].rpcmethod
  self.assertIsNot(meta,original_meta);self.assertIsNot(meta.func,original_meta.func)
  self.assertEqual((meta.rpctype,meta.argtypes,meta.pub),(original_meta.rpctype,original_meta.argtypes,original_meta.pub))
  for t in (265,369,427,454,455):
   for failure in (False,True):
    self.gg.avatar=self.actor();self.choose(t)
    params=self.fixture(('history_choose_failure_' if failure else 'history_choose_')+str(t))
    meta.call(self.gg.avatar,None,params)
    self.assertEqual(sum(self.gg.ui._lock.values()),0)
    self.assertEqual(self.gg.avatar.luckyDrawData.activity_data[t].choose_heroes,[0,0,0] if failure else params['h'])
   self.gg.avatar=self.actor();self.choose(t);self.gg.ui.reset_lock();self.choose(t)
   meta.call(self.gg.avatar,None,self.fixture('history_choose_'+str(t)));self.assertEqual(self.gg.ui._lock['setChooseHero'],1)
   meta.call(self.gg.avatar,None,self.fixture('history_choose_'+str(t)));self.assertEqual(sum(self.gg.ui._lock.values()),0)
   self.gg.avatar=self.actor();self.choose(t);old=self.gg.avatar;self.gg.avatar=self.actor()
   meta.call(old,None,self.fixture('history_choose_'+str(t)))
   self.assertEqual(sum(self.gg.ui._lock.values()),0);self.assertEqual(self.gg.avatar.luckyDrawData.activity_data[t].choose_heroes,[0,0,0])
 def test_metadata_call_original484_delegates(self):
  self.gg.avatar.setChooseHeroes(484,[117,135])
  params={'r':0,'t':484,'h':[2074057200,135,117]}
  self.Avatar.replySetChooseHeroes.rpcmethod.call(self.gg.avatar,None,params)
  self.assertEqual(sum(self.gg.ui._lock.values()),0)
  self.assertEqual(self.gg.avatar.luckyDrawData.activity_data[484].choose_heroes,params['h'])
 def test_pool_switch_before_delayed_confirm_does_not_send(self):
  p,c=self.popup();c.choose_heroes=[83,67];c.curr_idx=1;c.ui_logic.on_click_done(c);cb=self.tip_callbacks.pop();p.draw_type=369
  with self.assertRaises(RuntimeError):cb()
  self.assertFalse(self.sent)
 def test_avatar_data_ui_epoch_replacements_cancel_confirmation(self):
  for changed in ('avatar','data','epoch'):
   self.gg.avatar=self.actor();p,c=self.popup();c.choose_heroes=[83,67];c.curr_idx=1;c.ui_logic.on_click_done(c);cb=self.tip_callbacks.pop()
   if changed=='avatar':self.gg.avatar=self.actor()
   elif changed=='data':self.gg.avatar.luckyDrawData=self.actor().luckyDrawData
   else:self.gg.ui.reset_lock()
   with self.assertRaises(RuntimeError):cb()
  self.assertFalse(self.sent)
 def test_old_avatar_typed_reply_cleanup_does_not_write_new_owner(self):
  self.choose();old=self.gg.avatar;self.gg.avatar=self.actor();old._runRpc('replySetChooseHeroes',self.fixture('history_choose_265'),None);self.assertEqual(sum(self.gg.ui._lock.values()),0);self.assertEqual(self.gg.avatar.luckyDrawData.activity_data[265].choose_heroes,[0,0,0])
 def test_reset_old_reply_does_not_unlock_new_epoch(self):
  self.choose();self.gg.ui.reset_lock();self.choose();self.gg.avatar._runRpc('replySetChooseHeroes',self.fixture('history_choose_265'),None);self.assertEqual(self.gg.ui._lock['setChooseHero'],1);self.gg.avatar._runRpc('replySetChooseHeroes',self.fixture('history_choose_265'),None);self.assertEqual(sum(self.gg.ui._lock.values()),0)
 def test_stale_popup_button_never_opens_new_owner_confirm(self):
  p,c=self.popup();c.choose_heroes=[83,67];old_done=c.custom['callback']['btn_done'][0];self.gg.avatar=self.actor()
  with self.assertRaises(RuntimeError):old_done(c)
  self.assertFalse(self.tip_callbacks)
 def test_original484_request_and_nonselector_popup_restore(self):
  p,c=self.popup();self.assertIsInstance(c.ui_logic,ui._Logic)
  c.notify_show(choose_heroes=[0,0],choose_order=[3,4],callback=lambda h:None)
  self.assertIs(c.ui_logic,self.env['UILogic']);self.assertEqual(c.ui_logic.get_select_heroes(c),[117])
  self.gg.avatar.setChooseHeroes(484,[117,135]);self.assertEqual(self.sent[-1][1]['w']['p'],{'t':484,'h':[117,135]})
 def test_duplicate_reply_has_no_second_unlock_or_event(self):
  self.choose();params=self.fixture('history_choose_265');self.gg.avatar._runRpc('replySetChooseHeroes',params,None);events=len(self.events);self.gg.avatar._runRpc('replySetChooseHeroes',params,None);self.assertEqual(sum(self.gg.ui._lock.values()),0);self.assertEqual(len(self.events),events)
 def test_same_key_two_requests_each_typed_reply_releases_one(self):
  self.gg.avatar.setChooseHeroes(265,[83,67]);self.gg.avatar.setChooseHeroes(265,[83,67]);self.assertEqual(self.gg.ui._lock['setChooseHero'],2)
  self.gg.avatar._runRpc('replySetChooseHeroes',self.fixture('history_choose_failure_265'),None);self.assertEqual(self.gg.ui._lock['setChooseHero'],1)
  self.gg.avatar._runRpc('replySetChooseHeroes',self.fixture('history_choose_failure_265'),None);self.assertEqual(sum(self.gg.ui._lock.values()),0)
 def test_retired_ui_reply_only_cancels_old_wait_and_hides_old_node(self):
  self.choose();old=self.gg.ui;wait=old.panels.wait;wait.show_desc_timer='show';wait.disconnect_timer='disconnect';new=NS(_lock={'setChooseHero':1},panels=NS(wait=NS(disconnect_timer='new')))
  self.gg.ui=new;self.gg.exec_cancel=lambda h:self.fail('new scheduler used');self.gg.avatar._runRpc('replySetChooseHeroes',self.fixture('history_choose_265'),None)
  self.assertEqual(self.cancelled,['show','disconnect']);self.assertFalse(wait._node.visible);self.assertEqual(new._lock,{'setChooseHero':1});self.assertEqual(self.gg.avatar.luckyDrawData.activity_data[265].choose_heroes,[0,0,0])
 def test_retired_chooser_close_does_not_destroy_new_ui(self):
  p,c=self.popup();self.gg.avatar=self.actor();c.notify_close();self.assertFalse(c._node.visible);self.assertNotIn(('destroy',),self.events)
 def test_destroyed_chooser_or_origin_panel_cannot_send(self):
  for part in ('chooser','origin'):
   p,c=self.popup();c.choose_heroes=[83,67];c.curr_idx=1;c.ui_logic.on_click_done(c);cb=self.tip_callbacks.pop();(c if part=='chooser' else p).valid=False
   with self.assertRaises(RuntimeError):cb()
  self.assertFalse(self.sent)
 def test_client_validation_invalid_candidate_does_not_acquire_or_send(self):
  self.gg.avatar.setChooseHeroes(265,[135,83]);self.assertFalse(self.sent);self.assertEqual(sum(self.gg.ui._lock.values()),0);self.assertFalse(self.selector.pending)
 def test_scope_candidates_ignore_player_owned_filter(self):
  p,c=self.popup();self.gg.avatar.heroMgrData.getHero=lambda h:object();self.assertEqual(c.ui_logic.get_select_heroes(c),[83,92,103]);c.curr_idx=1;self.assertEqual(c.ui_logic.get_select_heroes(c),[67,91,121])
 def test_malformed_typed_reply_cannot_unlock_new_request(self):
  self.choose();self.gg.avatar._runRpc('replySetChooseHeroes',{'r':0,'h':[0,67,83]},None);self.assertEqual(self.gg.ui._lock['setChooseHero'],1)
  self.gg.avatar._runRpc('replySetChooseHeroes',self.fixture('history_choose_failure_265'),None);self.assertEqual(sum(self.gg.ui._lock.values()),0)
 def test_original_reliable_retry_bound_to_old_scope(self):
  self.choose();old=self.timers[-1];before=len(self.sent);self.gg.avatar=self.actor()
  with self.assertRaises(RuntimeError):old()
  self.assertEqual(len(self.sent),before)
 def test_definite_transport_attributeerror_releases_scope_without_fake_reply(self):
  def fail(*a):raise AttributeError('synthetic transport')
  self.gg.avatar.server.call_server_method=fail;self.gg.avatar.setChooseHeroes(265,[83,67]);self.assertEqual(sum(self.gg.ui._lock.values()),0);self.assertEqual(self.gg.avatar.luckyDrawData.activity_data[265].choose_heroes,[0,0,0]);self.assertEqual(len(self.gg.avatar.reliableRpcCache),1)
 def test_replaced_target_panels_in_same_ui_cancel_old_confirmation(self):
  p,c=self.popup();c.choose_heroes=[83,67];c.curr_idx=1;c.ui_logic.on_click_done(c);old=self.tip_callbacks.pop();self.popup(369)
  with self.assertRaises(RuntimeError):old()
  self.assertFalse(self.sent)
 def test_five_pool_epoch_getter_ignores_dst_without_mutating_clock_or_ch(self):
  import calendar,time,copy
  class Clock:
   timezone=0
   def mktime(self,end):return calendar.timegm(end)+3600
   def __getattr__(self,name):return getattr(time,name)
  clock=Clock();self.env['time']=clock;data=self.gg.avatar.luckyDrawData
  for t in self.policy['ready_ids']:
   raw=[self.policy['epochs'][str(t)],67,83];data.activity_data[t].choose_heroes=raw[:];before=copy.deepcopy(data.activity_data[t].__dict__)
   self.assertEqual(data.getChooseHeroes(t,True),(True,raw));self.assertEqual(data.activity_data[t].__dict__,before);self.assertIs(self.env['time'],clock)
   data.activity_data[t].choose_heroes[0]-=1;self.assertEqual(data.getChooseHeroes(t,True),(False,[raw[0]-1,0,0]))
  data.activity_data[484].choose_heroes=[2074057200,135,117]
  self.assertEqual(data.getChooseHeroes(484,True),(False,[2074057200,0,0]));self.assertEqual(data.getChooseHeroes(484,False),(True,[2074057200,135,117]));self.assertIs(self.env['time'],clock)
 def test_getter_without_check_and_unknown_pool_are_original(self):
  data=self.gg.avatar.luckyDrawData;self.assertEqual(data.getChooseHeroes(999,True),(False,[0,0,0]));data.activity_data[265].choose_heroes=[1,67,83];self.assertEqual(data.getChooseHeroes(265,False),(True,[1,67,83]))
 def test_original_activity_loop_gate_uses_canonical_getter_under_dst(self):
  import calendar,time
  class Clock:
   timezone=0
   def mktime(self,end):return calendar.timegm(end)+3600
   def __getattr__(self,name):return getattr(time,name)
  self.env['time']=Clock();loop=original('analysis/original-py-640/cocos/panels/card_activity_base.py','can_play_loop',self.env)
  data=self.gg.avatar.luckyDrawData
  for t in self.policy['ready_ids']:
   data.activity_data[t].choose_heroes=[self.policy['epochs'][str(t)],67,83];self.assertTrue(loop(NS(cur_drawtype=t)))
   data.activity_data[t].choose_heroes[0]-=1;self.assertFalse(loop(NS(cur_drawtype=t)))
 def test_python2_ascii_and_idempotent_coinstall(self):
  from lib2to3.refactor import RefactoringTool
  RefactoringTool([]).refactor_string((ROOT/'runtime/project7_selector_ui.py').read_text('ascii'),'selector_ui');self.assertIs(ui.install(self.text,friend.draw.policy._HistoryAvatar),self.selector);self.assertIs(friend.friend.install(friend.draw.policy._HistoryAvatar),self.state);self.assertIs(friend.draw.policy.install(self.policy_text),self.drawstate)
