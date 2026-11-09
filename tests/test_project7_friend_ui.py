"""Actual640 friendship/limitcall/UIManager plus frozen drawUI co-installation.
Synthetic owners and inert widgets/transport only, no game/native rendering.
"""
import contextlib,importlib.util,io,sys,time,types,unittest
from pathlib import Path
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1];NS=types.SimpleNamespace

def module(name,path):
 spec=importlib.util.spec_from_file_location(name,ROOT/path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
friend=module('friend_ui','runtime/project7_friend_ui.py');draw=module('friend_draw_fixture','tests/test_project7_draw_ui.py');furniture=module('friend_original_fixture','tests/test_project7_furniture_ui.py')
original=furniture.original
class FriendUiTests(unittest.TestCase):
 def setUp(self):
  capture=contextlib.redirect_stdout(io.StringIO());capture.__enter__();self.addCleanup(capture.__exit__,None,None,None)
  draw.HistoryUITests.setUp(self)
  self.sent=[];self.callbacks=[];self.cancelled=[];self.gg.exec_cancel=self.cancelled.append
  self.const.SUMMON_FRIEND_COST=200;self.const.SUMMON_NEW_FRIEND_COST=200;self.const.MAX_SUMMON_FRIEND_TIMES_DAY=100;self.const.MAX_SUMMON_NEW_FRIEND_TIMES_DAY=100;self.const.SUMMON_FRIEND_LIANCHOU_TIMES=10;self.const.SUMMON_NEW_FRIEND_LIANCHOU_TIMES=10
  self.const.VirtualItem.FRIENDCOIN=103;self.const.VirtualItem.NEWFRIENDCOIN=104
  self.env.update(time=time,sys=NS(excepthook=lambda *a:self.sent.append(('swallowed',)),exc_info=sys.exc_info),utils=NS(RotatedIdGenerator=NS(genid=lambda:len(self.callbacks)+1)))
  self.gg.avatar_callback_map={};self.gg.avatar_callback_need_result={}
  limit=original('analysis/original-py-640/cutils/chelpers.py','limitcall',self.env,top=True)
  self.Avatar=type('ClientAvatar',(),{})
  for name in friend._REQUESTS:setattr(self.Avatar,name,limit(1.8,True)(original('analysis/original-py-640/entity/avatar_members/LuckyDrawMember.py',name,self.env)))
  self.Avatar.callServerMethod=original('analysis/original-py-640/entity/ClientAvatar.py','callServerMethod',self.env)
  self.Avatar.checkFriendCoin=lambda a,n:a.friendCoin>=n;self.Avatar.checkNewFriendCoin=lambda a,n:a.newFriendCoin>=n;self.Avatar.checkInDaily7Falg=lambda a,n:self.no_confirm
  self.Avatar.tutorialIdentity=object();self.tutorial_identity=self.Avatar.tutorialIdentity
  self.Client=types.ModuleType(friend._TARGET);self.Client.ClientAvatar=self.Avatar
  patcher=patch.dict(sys.modules,{friend._TARGET:self.Client});patcher.start();self.addCleanup(patcher.stop)
  self.Box=self.classes[1]
  for name in ('on_init','_on_open_jiban_click','_on_open_friend_click','on_card_left_or_ten_click'):
   setattr(self.Box,name,original('analysis/original-py-640/cocos/panels/card_box.py',name,self.env))
  self.Box.get_luckyDraw_type=lambda p:1
  for name in ('notify_activity_panel_close','on_navigation_canvas_back','on_navigation_canvas_ck','on_navigation_canvas_rebuild'):
   if not hasattr(self.Box,name):setattr(self.Box,name,lambda *a:None)
  self.no_confirm=True;self.confirm=[]
  self.gg.ui.panels.common_confirm_3=NS(notify_confirm=lambda *a,**k:self.confirm.append(k['confirm_cb']))
  self.gg.ui.panels.wait=NS(valid=True,_node=draw.Widget(),show_desc_timer=None,disconnect_timer=None,notify_show=lambda *a:None,notify_hide=lambda:None,cancel_timer=lambda:None)
  self.gg.ui.panels.card_moneyexchange=NS(notify_show=lambda *a,**k:None)
  self.drawstate=draw.policy.install(self.policy_text)
  self.gg.avatar=None;self.state=friend.install(draw.policy._HistoryAvatar);self.gg.avatar=self.actor()
 def actor(self):
  a=self.Avatar();a.methodPoolBase={};a.friendCoin=10000;a.newFriendCoin=10000
  data=NS(friend_draw_count=0,new_friend_draw_count=0,friend_draw=False,getIsOpenCard=lambda t:False)
  data.canSummonFriendFirst=lambda:not data.friend_draw
  data.checkCardFriendLianChou=lambda n:a.friendCoin>=200*(n-(not data.friend_draw))
  data.checkCardNewFriendLianChou=lambda n:a.newFriendCoin>=200*n
  data.getLuckyDrawFriendConsume=lambda *a:[(103,1800)];data.getLuckyDrawNewFriendConsume=lambda *a:[(104,2000)]
  a.luckyDrawData=data
  def send(name,params,entityid):
   self.sent.append((name,dict(params)));self.callbacks.append(self.gg.avatar_callback_map[params['_cbid_']])
  a.server=NS(call_server_method=send);return a
 def box(self,state='friend_card_open'):
  p=self.Box();p.valid=True;p.on_init();p.cur_state=state;return p
 def test_real_coinstalled_ten_original_limitcall_owner_and_once_cleanup(self):
  p=self.box();before=self.gg.avatar;draw.policy.install(self.policy_text)
  p.on_card_left_or_ten_click(None,2)
  self.assertEqual(self.sent[0][0],'requestLuckyDrawFriendLianChouCard');self.assertIn('requestLuckyDrawFriendLianChouCard',before.methodPoolBase)
  self.assertEqual(self.gg.ui._lock,{'LuckyDrawFriendLianChouCard':1});self.callbacks[0]();self.callbacks[0]();self.assertEqual(sum(self.gg.ui._lock.values()),0)
  p.on_card_left_or_ten_click(None,2);self.assertEqual(len(self.sent),1)
  self.assertIs(self.Avatar.tutorialIdentity,self.tutorial_identity);self.assertIs(friend.install(draw.policy._HistoryAvatar),self.state)
 def test_four_requests_keep_real_single_ten_names_and_lock_keys(self):
  for name in friend._REQUESTS:
   getattr(self.gg.avatar,name)();self.assertEqual(self.sent[-1][0],name);self.assertEqual(self.gg.ui._lock[friend._LOCKS[name]],1);self.callbacks[-1]();self.assertEqual(sum(self.gg.ui._lock.values()),0)
 def test_old_avatar_callback_releases_its_ui_lease(self):
  self.box()._on_open_jiban_click();old=self.gg.avatar;self.gg.avatar=self.actor();self.callbacks[-1]();self.assertEqual(sum(self.gg.ui._lock.values()),0);self.assertIsNot(old,self.gg.avatar)
 def test_panel_old_avatar_cannot_send_to_new_owner(self):
  p=self.box();self.gg.avatar=self.actor()
  for name,args in [('_on_open_jiban_click',()),('_on_open_friend_click',()),('on_card_left_or_ten_click',(None,2))]:
   with self.assertRaises(RuntimeError):getattr(p,name)(*args)
  self.assertFalse(self.sent)
 def test_panel_data_replacement_rejected_and_fresh_panel_works(self):
  p=self.box();self.gg.avatar.luckyDrawData=self.actor().luckyDrawData
  with self.assertRaises(RuntimeError):p._on_open_jiban_click()
  self.box()._on_open_jiban_click();self.assertEqual(len(self.sent),1)
 def test_old_confirm_avatar_data_epoch_and_new_scope(self):
  for mutate in ('avatar','data','epoch'):
   self.no_confirm=False;self.gg.avatar=self.actor();p=self.box();p.on_card_left_or_ten_click(None,2);cb=self.confirm.pop()
   if mutate=='avatar':self.gg.avatar=self.actor()
   elif mutate=='data':self.gg.avatar.luckyDrawData=self.actor().luckyDrawData
   else:self.gg.ui.reset_lock()
   with self.assertRaises(RuntimeError):cb()
  self.assertFalse(self.sent);self.no_confirm=True;self.gg.avatar=self.actor();self.box().on_card_left_or_ten_click(None,2);self.assertEqual(len(self.sent),1)
 def test_reset_epoch_old_callback_does_not_unlock_new_request(self):
  self.gg.avatar.requestLuckyDrawFriendCard();old=self.callbacks[-1];self.gg.ui.reset_lock();self.gg.avatar.methodPoolBase.clear();self.gg.avatar.requestLuckyDrawFriendCard();old();self.assertEqual(self.gg.ui._lock,{'LuckyDrawFriendCard':1});self.callbacks[-1]();self.assertEqual(sum(self.gg.ui._lock.values()),0)
 def test_two_same_key_counts_once_each(self):
  self.gg.avatar.requestLuckyDrawFriendCard();first=self.callbacks[-1];self.gg.avatar.methodPoolBase.clear();self.gg.avatar.requestLuckyDrawFriendCard();second=self.callbacks[-1]
  self.assertEqual(self.gg.ui._lock['LuckyDrawFriendCard'],2);first();first();self.assertEqual(self.gg.ui._lock['LuckyDrawFriendCard'],1);second();self.assertEqual(sum(self.gg.ui._lock.values()),0)
 def test_retired_ui_only_cancels_captured_wait_with_captured_scheduler(self):
  oldui=self.gg.ui;oldwait=oldui.panels.wait;oldwait.show_desc_timer='old-show';oldwait.disconnect_timer='old-disconnect'
  self.gg.avatar.requestLuckyDrawFriendCard();callback=self.callbacks[-1];newui=NS(_lock={'LuckyDrawFriendCard':1},panels=NS(wait=NS(show_desc_timer='new-show',disconnect_timer='new-disconnect')))
  self.gg.ui=newui;self.gg.exec_cancel=lambda h:self.fail('new scheduler called');callback();callback()
  self.assertEqual(self.cancelled,['old-show','old-disconnect']);self.assertFalse(oldwait._node.visible);self.assertEqual(newui._lock,{'LuckyDrawFriendCard':1});self.assertEqual(newui.panels.wait.show_desc_timer,'new-show')
 def test_transport_throw_releases_even_when_original_swallows_attributeerror(self):
  def fail(*a):raise AttributeError('synthetic transport down')
  self.gg.avatar.server.call_server_method=fail;self.gg.avatar.requestLuckyDrawFriendCard();self.assertEqual(sum(self.gg.ui._lock.values()),0);self.assertIn(('swallowed',),self.sent);self.assertFalse(self.gg.avatar_callback_map)
 def test_nonfriend_ten_delegates_original_without_friend_admission(self):
  p=self.box('unrelated_state');self.gg.avatar=self.actor();p.on_card_left_or_ten_click(None,2);self.assertFalse(self.sent)
 def test_wrong_view_and_generation_rejected(self):
  fake=type('_HistoryAvatar',(),{})();fake._source=self.gg.avatar;fake._state=object()
  with self.assertRaises(RuntimeError):self.Avatar.requestLuckyDrawFriendCard(fake)
  old=self.gg.avatar;self.gg.avatar=self.actor()
  with self.assertRaises(RuntimeError):old.requestLuckyDrawFriendCard()
 def test_old_trusted_view_rejected_after_avatar_changes(self):
  view=draw.policy._HistoryAvatar(self.gg.avatar,self.drawstate);self.gg.avatar=self.actor()
  with self.assertRaises(RuntimeError):self.Avatar.requestLuckyDrawFriendCard(view)
  self.assertFalse(self.sent)
 def test_false_real_reply_then_original_carrier_cleans_scope(self):
  # Fixed actual Gateway fixture, not an invented success/failure shape.
  import ast,base64,hashlib,json
  probe=module('friend_real_probe','runtime/android_friend_draw/host_tests/consumers.py');old=probe.old
  data=json.loads((ROOT/'reports/project7-friend-draw-original-host.json').read_text())
  fixture={line.split(' ',2)[1]:line.split(' ',2)[2] for line in data['logs']['actual-original-friend']['stdout'].splitlines() if line.startswith('FRIEND_FIXTURE ')}
  ns=dict(self.env);ns.update(CLIENT_STUB=3,StandardError=Exception,_logger=NS(warn=lambda *a:None,error=lambda *a:None),EntityManager=NS(getentity=lambda p:None))
  for path,names in [('analysis/original-py-640/lib/common/RpcMethodArgs.py',['ConvertError','RpcMethodArg','NoLimit','NumeralLimit','Int','Bool','List','Dict','Avatar','MailBox']),('analysis/original-py-640/lib/common/rpcdecorator.py',['RpcMethod','rpc_method'])]:
   tree=ast.parse(str(old.FIX.refactor_string((ROOT/path).read_text(),path)));body=[n for n in tree.body if isinstance(n,(ast.FunctionDef,ast.ClassDef)) and n.name in names];exec(compile(ast.Module(body=body,type_ignores=[]),path+':selected','exec'),ns)
  self.gg.ui.panels.card_open=NS(notify_scene_friend_card_open=lambda *a:self.fail('false reward'),notify_scene_friend_card_lianchou_open=lambda *a:self.fail('false reward'))
  self.gg.ui.panels.settlement_fullscreen=NS(check_gonglue_cache_result=lambda *a:self.fail('false hero'))
  for i,name in enumerate(('requestLuckyDrawFriendCard','requestLuckyDrawFriendLianChouCard','requestLuckyDrawNewFriendCard','requestLuckyDrawNewFriendLianChouCard')):
   self.gg.avatar=self.actor();self.env['utils'].RotatedIdGenerator.genid=lambda i=i:300+i
   getattr(self.gg.avatar,name)();self.assertEqual(self.gg.ui._lock[friend._LOCKS[name]],1)
   reply=name.replace('request','reply');body=original('analysis/original-py-640/entity/avatar_members/LuckyDrawMember.py',reply,ns)
   typed=ns['rpc_method'](3,(ns['List' if i%2 else 'Dict']('r'),ns['Bool']('st')))(body)
   update=ns['rpc_method'](3,(ns['Bool']('fd'),))(original('analysis/original-py-640/entity/avatar_members/LuckyDrawMember.py','updateFriendDraw',ns))
   carrier_path=ROOT/'analysis/original-py-640/entity/avatar_members/ReliableRpcMember.py';lines=carrier_path.read_text().splitlines();start=next(j for j,l in enumerate(lines) if l.startswith('    def serverCallbackCarrier('));exec(compile('\n'.join(l[4:] for l in lines[start:start+2])+'\n',str(carrier_path)+':selected','exec'),ns);carrier=ns['rpc_method'](3,(ns['Dict']('_r_'),))(ns['serverCallbackCarrier'])
   methods={reply:typed,'updateFriendDraw':update,'serverCallbackCarrier':carrier}
   for part in fixture['failure_'+str(i)].split(','):
    digest,raw=map(base64.b64decode,part.split(':',1))
    for method,fn in methods.items():
     if hashlib.md5(method.encode()).digest()==digest:fn(self.gg.avatar,old.bson(raw))
   self.assertEqual(sum(self.gg.ui._lock.values()),0);self.assertNotIn(300+i,self.gg.avatar_callback_map)
 def test_scope_created_after_epoch_reset_still_runs_on_same_panel(self):
  self.no_confirm=False;p=self.box();p.on_card_left_or_ten_click(None,2);old=self.confirm.pop();self.gg.ui.reset_lock()
  with self.assertRaises(RuntimeError):old()
  self.gg.avatar.methodPoolBase.clear();p.on_card_left_or_ten_click(None,2);fresh=self.confirm.pop();fresh();self.assertEqual(len(self.sent),1);self.callbacks[-1]();self.assertEqual(sum(self.gg.ui._lock.values()),0)
 def test_replaced_gg_callback_only_retires_captured_wait(self):
  wait=self.gg.ui.panels.wait;wait.show_desc_timer=123;self.gg.avatar.requestLuckyDrawFriendCard();callback=self.callbacks[-1]
  replacement=types.ModuleType('gg');replacement.ui=NS(_lock={'LuckyDrawFriendCard':1})
  with patch.dict(sys.modules,{'gg':replacement}):callback();callback()
  self.assertEqual(self.cancelled,[123]);self.assertEqual(replacement.ui._lock,{'LuckyDrawFriendCard':1});self.assertFalse(wait._node.visible)
 def test_python2_ascii_grammar(self):
  from lib2to3.refactor import RefactoringTool
  RefactoringTool([]).refactor_string((ROOT/'runtime/project7_friend_ui.py').read_text('ascii'),'friend_ui')
