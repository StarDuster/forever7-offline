"""Real original typed decorator/body, reliable producer and counted UI locks.
No native dispatch/sockets: the transport identity here is an explicit seam;
actual controller/channel/late entity lookup is tested in test_wish_transport.
"""
import _paths  # noqa: E402,F401
import collections,sys,types,unittest
from unittest.mock import patch
from tests.test_project7_wish_ui import original,wish,NS
from tests import test_project7_wish_ui as readonly
from tests.test_project7_wish_transport import original_class,Log
class ChooseGuardTests(unittest.TestCase):
 def setUp(self):
  readonly.ReadViewTests.setUp(self);self.actor.yuanbao=10000;self.channel=object();self.sent=[];self.timers=[];self.events=[]
  self.state.resources=lambda *a,**k:None;self.state.draw_owner=object();self.state.history_avatar_type=lambda actor,owner:actor
  self.gg.exec_delay=lambda delay,cb:self.timers.append(cb);self.gg.avatar_callback_map={};self.gg.avatar_callback_need_result={}
  ui=self.gg.ui;ui.recon_lock=0;ui._tree=NS(proc_event=lambda *a,**k:self.events.append((a,k)))
  ui.panels.wait=NS(notify_show=lambda *a:None,notify_hide=lambda:None,cancel_timer=lambda:None);ui.panels.common_message=NS(notify_message=lambda code:self.events.append(code))
  for name in ('lock','unlock','reset_lock'):setattr(ui,name,types.MethodType(original('analysis/original-py-640/cocos/ui_manager.py',name,{'gg':self.gg}),ui))
  argsenv={}
  for name in ('ConvertError','RpcMethodArg','NoLimit','NumeralLimit','Int','List'):original_class('lib/common/RpcMethodArgs.py',name,argsenv)
  rpcenv={'gg':self.gg,'_logger':Log(),'Avatar':type('AvatarArg',(),{}),'MailBox':type('MailBoxArg',(),{}),'ConvertError':argsenv['ConvertError'],'CLIENT_STUB':3}
  original_class('lib/common/rpcdecorator.py','RpcMethod',rpcenv);decorate=original('analysis/original-py-640/lib/common/rpcdecorator.py','rpc_method',rpcenv,top=True)
  self.env.update(CHOUKA_WISH_TREASURE_CHOOSE=NS(data=self.state.choose),ITEM_STORE_WISH_CHANGE=NS(data=self.state.fees))
  valid=original('analysis/original-py-640/entity/avatar_members/LuckyDrawMember.py','validSetChooseTreasure',self.env)
  choose=original('analysis/original-py-640/entity/avatar_members/LuckyDrawMember.py','setChooseTreasure',self.env)
  reply=original('analysis/original-py-640/entity/avatar_members/LuckyDrawMember.py','replySetChooseTreasure',self.env)
  self.member=type('Member',(),{'replySetChooseTreasure':decorate(3,(argsenv['Int']('r'),argsenv['Int']('t'),argsenv['List']('i')))(reply),'setChooseTreasure':choose})
  self.module=types.ModuleType('finite.WishMember');self.module.Member=self.member;self.module.rpc_method=decorate
  self.modules=patch.dict(sys.modules,{self.module.__name__:self.module,'gg':self.gg});self.modules.start();self.addCleanup(self.modules.stop)
  transport=NS(check=lambda:True,transport=lambda actor:self.channel if actor is self.gg.avatar else None)
  self.owner=wish._MemberOwner(self.gg,self.module,self.member,transport)
  old=self.owner.original;self.owner.wrapper=decorate(old.rpcmethod.rpctype,old.rpcmethod.argtypes,old.rpcmethod.pub)(self.owner.reply);self.owner.wrapper.__name__=old.__name__;self.member.replySetChooseTreasure=self.owner.wrapper
  self.actor.validSetChooseTreasure=types.MethodType(valid,self.actor);self.actor.server=NS(call_server_method=lambda *a,**k:self.sent.append((a,k)))
  renv={'gg':self.gg,'collections':collections}
  for name in ('initReliableRpc','_genReliableRpcSeq','callServerMethodReliable','reSendRpc'):setattr(self.actor,name,types.MethodType(original('analysis/original-py-640/entity/avatar_members/ReliableRpcMember.py',name,renv),self.actor))
  self.actor.initReliableRpc();self.actor.callServerMethod=types.MethodType(original('analysis/original-py-640/entity/ClientAvatar.py','callServerMethod',{'gg':self.gg,'sys':sys}),self.actor)
  self.state.member_owner=self.owner;self.renew()
 def renew(self):
  self.scope=wish._Scope(self.state,self.panel,self.panel,5);self.panel._q7_wish_scope=self.scope
 def choose(self):return self.owner.choose(self.scope,5,1096)
 def reply(self,ret=0,info=None,metadata=False):
  values={'r':ret,'t':5,'i':[1,1096,1]if info is None else info}
  if metadata:return self.owner.wrapper.rpcmethod.call(self.actor,None,values)
  return self.owner.wrapper(self.actor,values)
 def test_original_send_and_both_typed_entries_apply_once(self):
  for metadata in(False,True):
   self.choose();self.assertEqual(self.gg.ui._lock['setChooseTreasure'],1);self.reply(metadata=metadata);self.assertEqual(self.gg.ui._lock['setChooseTreasure'],0);self.assertEqual(self.actor.luckyDrawData.activity_data[5].choose_treasure,[1,1096,1])
   self.actor.luckyDrawData.activity_data[5].choose_treasure=[1,0,0];self.reply();self.assertEqual(self.gg.ui.recon_lock,0)
  self.assertEqual(len(self.sent),2)
 def test_reset_old_reply_drains_without_unlocking_new_lock_or_data(self):
  self.choose();self.gg.ui.reset_lock();self.gg.ui.lock('setChooseTreasure');self.renew()
  with self.assertRaises(RuntimeError):self.choose()
  self.reply();self.assertEqual(self.gg.ui._lock['setChooseTreasure'],1);self.assertEqual(self.actor.luckyDrawData.activity_data[5].choose_treasure,[0,0,0]);self.assertIsNone(self.owner.pending)
  self.gg.ui.unlock('setChooseTreasure');self.choose();self.reply();self.assertEqual(self.gg.ui.recon_lock,0)
 def test_failure_empty_info_drains_unique_pending_and_double_reply_no_second_unlock(self):
  self.choose();self.reply(ret=1885,info=[],metadata=True);self.gg.ui.lock('setChooseTreasure');self.reply(ret=1885,info=[]);self.assertEqual(self.gg.ui._lock['setChooseTreasure'],1);self.assertEqual(self.actor.luckyDrawData.activity_data[5].choose_treasure,[0,0,0])
 def test_pre_send_validation_and_resource_failure_no_pending_or_lock(self):
  self.actor.yuanbao=0;self.choose();self.assertIsNone(self.owner.pending);self.assertEqual(self.sent,[]);self.assertEqual(self.gg.ui.recon_lock,0)
  def missing(*a,**k):raise RuntimeError('resource unavailable')
  self.state.resources=missing
  with self.assertRaises(RuntimeError):self.choose()
  self.assertIsNone(self.owner.pending);self.assertEqual(self.gg.ui._lock,{})
 def test_send_exception_quarantines_no_second_charge_until_real_result(self):
  def fail(*a,**k):raise IOError('ambiguous send')
  self.actor.server.call_server_method=fail
  with self.assertRaises(IOError):self.choose()
  self.assertTrue(self.owner.pending.sent)
  with self.assertRaises(RuntimeError):self.choose()
  self.reply(ret=1885,info=[]);self.assertIsNone(self.owner.pending)
 def test_old_deferred_scope_before_send_no_rpc_no_lock(self):
  self.gg.ui.reset_lock()
  with self.assertRaises(RuntimeError):self.choose()
  self.assertEqual(self.sent,[]);self.assertEqual(self.gg.ui._lock,{})
 def test_wrong_pool_typed_cannot_consume_pending_or_allow_second_charge(self):
  self.choose();pending=self.owner.pending;self.owner.wrapper(self.actor,{'r':0,'t':119,'i':[]});self.assertIs(self.owner.pending,pending);self.assertEqual(self.gg.ui._lock['setChooseTreasure'],1)
  with self.assertRaises(RuntimeError):self.choose()
  self.reply();self.assertIsNone(self.owner.pending);self.assertEqual(self.gg.ui.recon_lock,0)
 def test_same_channel_replaced_entity_reply_drains_old_quarantine_without_data(self):
  self.choose();old=self.actor;new=NS(luckyDrawData=NS(activity_data={5:NS(choose_treasure=[0,0,0])}));self.gg.avatar=new
  self.owner.wrapper(new,{'r':0,'t':5,'i':[1,1096,1]})
  self.assertIsNone(self.owner.pending);self.assertEqual(new.luckyDrawData.activity_data[5].choose_treasure,[0,0,0]);self.assertEqual(old.luckyDrawData.activity_data[5].choose_treasure,[0,0,0]);self.assertEqual(self.gg.ui.recon_lock,0)
 def test_new_accepted_channel_retires_old_owned_count_without_reset(self):
  self.choose();self.assertEqual(self.gg.ui._lock['setChooseTreasure'],1);self.channel=object();self.renew();self.choose();self.assertEqual(self.gg.ui._lock['setChooseTreasure'],1);self.reply();self.assertEqual(self.gg.ui.recon_lock,0)
 def test_early_installer_rejects_unscoped_original_producer_before_lock(self):
  self.member.replySetChooseTreasure=self.owner.original;self.member.setChooseTreasure=self.owner.original_choose
  actor=self.gg.avatar;self.gg.avatar=None
  modules={'entity.avatar_members.LuckyDrawMember':self.module,'com.base.game_object':NS(members_cache={})}
  with patch.dict(sys.modules,modules),patch.object(wish,'_EARLY',None):
   early=wish.install_member_guard(self.owner.transport_owner);self.gg.avatar=actor
   early.member.setChooseTreasure(actor,5,1096)
   self.assertEqual(self.sent,[]);self.assertEqual(self.gg.ui._lock,{});self.assertIn(1882,self.events)
   self.assertIs(wish.install_member_guard(self.owner.transport_owner),early)
   Avatar=type('Avatar',(),{'replySetChooseTreasure':early.wrapper,'setChooseTreasure':early.business_wrapper});self.assertTrue(early.check_avatar(Avatar))
 def test_late_materialized_exact_copy_checked_without_early_import_or_recursion(self):
  with patch.dict(sys.modules,{'entity.ClientAvatar':None}):self.assertIs(self.owner.check(),self.owner)
  Avatar=type('ClientAvatar',(),{'replySetChooseTreasure':self.owner.wrapper,'setChooseTreasure':self.owner.original_choose});module=types.ModuleType('entity.ClientAvatar');module.ClientAvatar=Avatar
  with patch.dict(sys.modules,{'entity.ClientAvatar':module}):
   self.assertIs(self.owner.check(),self.owner);self.assertTrue(self.owner.check_avatar(Avatar));self.assertIs(self.owner.transport(self.actor),self.channel)
 def test_wrong_materialized_either_copy_rejects_before_send_and_pending_consumption(self):
  for name in ('setChooseTreasure','replySetChooseTreasure'):
   expected={'replySetChooseTreasure':self.owner.wrapper,'setChooseTreasure':self.owner.original_choose}
   Avatar=type('ClientAvatar',(),expected);module=types.ModuleType('entity.ClientAvatar');module.ClientAvatar=Avatar
   with patch.dict(sys.modules,{'entity.ClientAvatar':module}):
    setattr(Avatar,name,lambda *args:None)
    before=len(self.sent)
    with self.assertRaises(RuntimeError):self.choose()
    self.assertEqual(len(self.sent),before);self.assertEqual(self.gg.ui.recon_lock,0)
    setattr(Avatar,name,expected[name]);self.choose();pending=self.owner.pending;setattr(Avatar,name,lambda *args:None)
    with self.assertRaises(RuntimeError):self.reply(metadata=True)
    self.assertIs(self.owner.pending,pending);self.assertEqual(self.gg.ui._lock['setChooseTreasure'],1)
    setattr(Avatar,name,expected[name]);self.reply(ret=1885,info=[]);self.assertIsNone(self.owner.pending);self.assertEqual(self.gg.ui.recon_lock,0)
 def test_actual_resend_same_logical_rpc_and_old_channel_cannot_send(self):
  self.choose();self.timers[0]();self.assertEqual(len(self.sent),2);self.assertEqual(self.sent[0],self.sent[1]);self.channel=object()
  with self.assertRaises(RuntimeError):self.timers[-1]()
  self.assertEqual(len(self.sent),2)
if __name__=='__main__':unittest.main()
