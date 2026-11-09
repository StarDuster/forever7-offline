"""Finite original640 RPC parser, NewbeeMember/Data bodies; no game runtime."""
import ast,importlib.util,sys,types,unittest
from pathlib import Path
from unittest.mock import patch
from lib2to3.refactor import RefactoringTool
R=Path(__file__).resolve().parents[1];FIX=RefactoringTool(['lib2to3.fixes.fix_print','lib2to3.fixes.fix_except','lib2to3.fixes.fix_xrange'])
def load(name,path):
 s=importlib.util.spec_from_file_location(name,R/path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
helper=load('tutorial_original_helper','tests/test_project7_furniture_ui.py');helper.FIX=RefactoringTool(['lib2to3.fixes.fix_print','lib2to3.fixes.fix_except','lib2to3.fixes.fix_dict','lib2to3.fixes.fix_xrange','lib2to3.fixes.fix_filter']);original=helper.original
class Arg:
 def __init__(self,n,kind):self.n=n;self.kind=kind
 def getname(self):return self.n
 def convert(self,v):
  if type(v)is not self.kind:raise ValueError('invalid typed value')
  return v
 def default_val(self):return [] if self.kind is list else 0
class Tests(unittest.TestCase):
 def setUp(self):
  self.p=load('tutorial_policy','runtime/project7_tutorial_completion.py');self.gg=types.ModuleType('gg');self.gg.avatar=None;self.gg.avatar_callback_map={};self.gg.avatar_callback_need_result={};self.delayed=[];self.gg.exec_delay=lambda ms,cb:self.delayed.append(cb)
  self.env={'gg':self.gg,'CLIENT_STUB':3,'Avatar':type('AvatarArg',(),{}),'MailBox':type('MailboxArg',(),{}),'ConvertError':ValueError,'_logger':types.SimpleNamespace(warn=lambda*a:None,error=lambda*a:None)}
  text=(R/'analysis/original-py-640/lib/common/rpcdecorator.py').read_text();source=text[text.index('class RpcMethod('):text.index('\ndef expose_to_client')];exec(str(FIX.refactor_string(source,'rpcdecorator')),self.env)
  rpc=self.env['rpc_method'];self.M=type('Member',(),{});self.C=type('Member',(),{});self.L=type('Member',(),{});self.E=type('Member',(),{});self.Room=type('Member',(),{});self.BBS=type('Panel',(),{});self.Danchi=type('Panel',(),{'_q7_furniture_ui_owner':object()});self.Designer=type('Panel',(),{});self.FM=type('Member',(),{})
  for n,key,kind in [('triggerClientNewbee','e',int),('triggerProcessingEvent','pe',list)]:setattr(self.M,n,rpc(3,(Arg(key,kind),))(original('analysis/original-py-640/entity/avatar_members/NewbeeMember.py',n,self.env)))
  self.C.area_build_request=original('analysis/original-py-640/entity/avatar_members/CityMember.py','area_build_request',self.env)
  self.M.finishNewbee=original('analysis/original-py-640/entity/avatar_members/NewbeeMember.py','finishNewbee',self.env)
  self.finish_identity=self.M.finishNewbee
  legacy=load('tutorial_legacy','runtime/offline_tutorials.py');self.legacy=legacy
  for name in ('clientTriggerNewbeeFromClient','clientAskTriggerNewbee','checkProcessingNewbee','triggerNewbee'):setattr(self.M,name,legacy.skip_newbee_request)
  for cls,name,args in [(self.C,'area_build_reply',(Arg('rs',bool),Arg('aid',int),Arg('ext',dict))),(self.L,'replyLuckyDrawFile',(Arg('rt',bool),Arg('t',int)))]:
   path='CityMember' if cls is self.C else 'LuckyDrawMember'
   setattr(cls,name,rpc(3,args)(original('analysis/original-py-640/entity/avatar_members/'+path+'.py',name,self.env)))
  for cls,mod,name,args in [
   (self.C,'CityMember','get_city_data_reply',(Arg('cd',dict),)),
   (self.E,'EventTriggerMember','startEventReply',(Arg('e',int),Arg('r',int))),
   (self.Room,'RoomMember','calcCrystalReply',(Arg('rd',list),)),
   (self.Room,'RoomMember','activeSkillReply',(Arg('sk',int),Arg('op',int),Arg('lv',int))),
   (self.L,'LuckyDrawMember','replyLuckyDrawFurnitureCard',(Arg('rs',bool),Arg('i',dict)))]:
   setattr(cls,name,rpc(3,args)(original('analysis/original-py-640/entity/avatar_members/'+mod+'.py',name,self.env)))
  noop=lambda *a,**k:None
  self.env['const']=types.SimpleNamespace(RewardType=types.SimpleNamespace(EVENT=1),SCENE_NEW_DANCHI_ROOM=7)
  self.gg.city_container=types.SimpleNamespace(get_scene_by_key=lambda *a:None)
  self.gg.logic=types.SimpleNamespace(event_valid=True,disable_event=lambda *a:None,enable_event=lambda *a:None)
  self.gg.ui=types.SimpleNamespace(enable_settlement=noop,_tree=types.SimpleNamespace(proc_event=noop),panels=types.SimpleNamespace(city_shuzhi_jiejing=types.SimpleNamespace(valid=False),settlement_window=types.SimpleNamespace(notify_build_new=noop,notify_reward=noop),city_entrance=types.SimpleNamespace(notify_process=noop),card_box=types.SimpleNamespace(on_reply_draw_file=noop)))
  self.env['cc']=types.SimpleNamespace(ccui=types.SimpleNamespace(TOUCH_EVENT_BEGAN=0,TOUCH_EVENT_ENDED=2,TOUCH_EVENT_MOVED=1,TOUCH_EVENT_CANCELED=3))
  multi=original('analysis/original-py-640/cocos/ui_utils.py','checkMultiClick',self.env,top=True)
  self.Danchi.on_close_click=multi(original('analysis/original-py-640/cocos/panels/city_room_danchi_new.py','on_close_click',self.env))
  self.ND=type('NewbeeData',(),{})
  self.ND.initFromDict=original('analysis/original-py-640/entity/avatar_attrs/NewbeeData.py','initFromDict',self.env)
  self.FM.saveFurnitureScheme=original('analysis/original-py-640/entity/avatar_members/FurnitureMember.py','saveFurnitureScheme',self.env)
  self.env['FURNITURE_DATA']=types.SimpleNamespace(data={51:{'itemid':10118,'name':'syntheticTV','sub_category':[1]}})
  self.env['ITEM_DATA']=types.SimpleNamespace(data={10118:{'furniture':51}})
  Furniture=type('Furniture',(),{})
  for name in ('__init__','setEntity'):setattr(Furniture,name,original('analysis/original-py-640/cocos/panels/city_room_zhuangxiu.py',name,self.env))
  self.env['Furniture']=Furniture
  self.Designer.add_furniture_data=original('analysis/original-py-640/cocos/panels/city_room_zhuangxiu.py','add_furniture_data',self.env)
  self.Designer.notify_show=original('analysis/original-py-640/cocos/panels/city_room_zhuangxiu.py','notify_show',self.env)
  self.Designer.refresh_panel=original('analysis/original-py-640/cocos/panels/city_room_zhuangxiu.py','refresh_panel',self.env)
  self.BBS.notify_show=lambda *a,**k:None
  self.BBS.notify_close=original('analysis/original-py-640/cocos/panels/bbs_home.py','notify_close',self.env)
  modules={'entity.avatar_members.FurnitureMember':types.SimpleNamespace(Member=self.FM),'cocos.panels.city_room_zhuangxiu':types.SimpleNamespace(Panel=self.Designer,ITEM_DATA=types.SimpleNamespace(data={10118:{'furniture':51}})),'entity.avatar_attrs.NewbeeData':types.SimpleNamespace(NewbeeData=self.ND),'cocos.panels.city_room_danchi_new':types.SimpleNamespace(Panel=self.Danchi),'cocos.panels.bbs_home':types.SimpleNamespace(Panel=self.BBS),'gg':self.gg,'entity.avatar_members.NewbeeMember':types.SimpleNamespace(Member=self.M,rpc_method=rpc),'entity.avatar_members.CityMember':types.SimpleNamespace(Member=self.C),'entity.avatar_members.LuckyDrawMember':types.SimpleNamespace(Member=self.L),'entity.avatar_members.EventTriggerMember':types.SimpleNamespace(Member=self.E),'entity.avatar_members.RoomMember':types.SimpleNamespace(Member=self.Room),'com.base.game_object':types.SimpleNamespace(members_cache={})}
  self.patch=patch.dict(sys.modules,modules);self.patch.start();self.addCleanup(self.patch.stop);self.state=self.p.install();self.p.install_panels();self.a=self.actor();self.gg.avatar=self.a
 def actor(self):
  a=self.M();a.newbeeData=types.SimpleNamespace(clent_trigger_event_list=[],finish_newbee=[],processing_event=[],canNewbeeTrigger=lambda x:False)
  a.newbeeData.finishNewbee=types.MethodType(original('analysis/original-py-640/entity/avatar_attrs/NewbeeData.py','finishNewbee',self.env),a.newbeeData)
  a.cityData=types.SimpleNamespace(get_area_building=lambda n:{'1':2},set_city_data=lambda *a:None)
  a.roomData=types.SimpleNamespace(setRoomSysSkillInfo=lambda *a:None);a.noticeCityAction=lambda:None
  a.logger=types.SimpleNamespace(debug=lambda *a:None);a.queryEventOptAsk=lambda *a:None;a.completeBase=lambda *a:None
  a.eventTriggerData=types.SimpleNamespace(processingEventsClient=set());a.eventTriggerData.addProcessingEvent=a.eventTriggerData.processingEventsClient.add
  a.weeknumData=types.SimpleNamespace(weeknum=3,isFinalDay=lambda:False)
  a.last_build_field=1;a.luckyDrawData=types.SimpleNamespace(setIsFileOpen=lambda *a:None,setCurCardTimeDay=lambda *a:None);a.newbeeData.checkAllNewbee=lambda:None
  a.sent=[];a.callServerMethodReliable=lambda n,p,**kw:a.sent.append((n,p));return a
 def test_nine_actual_rpc_finish_localfn_and_dedup(self):
  ids=sorted(self.p._DISMISS);self.a.triggerProcessingEvent({'pe':list(ids)});self.assertEqual([p['e'][0]for n,p in self.a.sent],ids);self.assertEqual(self.a.newbeeData.finish_newbee,ids)
  self.a.triggerProcessingEvent({'pe':list(ids)});self.assertEqual(len(self.a.sent),9)
 def test_reentrant_notification_once(self):
  def send(n,p):self.a.sent.append((n,p));self.a.triggerClientNewbee({'e':10})
  self.a.callServerMethodReliable=send;self.a.triggerClientNewbee({'e':10});self.assertEqual(len(self.a.sent),1)
 def test_send_failure_retry_not_marked(self):
  self.a.callServerMethodReliable=lambda *a:(_ for _ in ()).throw(IOError('fixture'))
  with self.assertRaises(IOError):self.a.triggerClientNewbee({'e':10})
  self.a.callServerMethodReliable=lambda n,p:self.a.sent.append((n,p));self.a.triggerClientNewbee({'e':10});self.assertEqual(len(self.a.sent),1)
 def test_owner_reconnect_replays_authoritative_pending(self):
  old=self.a;old.triggerClientNewbee({'e':10});self.a=self.actor();self.gg.avatar=self.a;old.triggerClientNewbee({'e':93});self.assertEqual(len(old.sent),1)
  self.a.triggerProcessingEvent({'pe':[10]});self.assertEqual(len(self.a.sent),1)
 def test_actions_require_started_and_success_no_marker_fabrication(self):
  self.C.area_build_reply(self.a,{'rs':True,'aid':1,'ext':{}});self.assertFalse(self.a.sent)
  self.a.triggerProcessingEvent({'pe':[20,24,90,30,5,253]});self.assertFalse(self.a.sent)
  self.C.area_build_reply(self.a,{'rs':False,'aid':1,'ext':{}});self.assertFalse(self.a.sent)
  self.C.area_build_request(self.a,1,1,2,[]);self.a.sent.clear()
  self.C.area_build_reply(self.a,{'rs':True,'aid':1,'ext':{}});self.assertEqual([p['e']for n,p in self.a.sent],[[20],[24]])
  self.L.replyLuckyDrawFile(self.a,{'rt':False,'t':1});self.assertEqual(len(self.a.sent),2)
  self.L.replyLuckyDrawFile(self.a,{'rt':True,'t':1});self.assertEqual(self.a.sent[-1][1],{'e':[90]});self.assertNotIn(27,self.a.newbeeData.finish_newbee)
 def test_legacy_identities_and_install_guard(self):
  self.assertIs(self.state,self.p.install());self.assertIs(self.M.finishNewbee,self.finish_identity)
  for name in ('clientTriggerNewbeeFromClient','clientAskTriggerNewbee','checkProcessingNewbee','triggerNewbee'):self.assertIs(getattr(self.M,name),self.legacy.skip_newbee_request)
 def test_actual_action_consumers_only_positive_started(self):
  self.a.triggerProcessingEvent({'pe':[30,150,151,230,240,250]})
  self.assertEqual(self.a.sent[-1][1],{'e':[150]});self.a.sent.clear()
  self.C.get_city_data_reply(self.a,{'cd':{'uc':False}});self.assertFalse(self.a.sent)
  self.C.get_city_data_reply(self.a,{'cd':{'uc':True}})
  self.E.startEventReply(self.a,{'e':1011,'r':0});self.assertEqual(len(self.a.sent),1)
  self.E.startEventReply(self.a,{'e':1011,'r':1})
  self.Room.calcCrystalReply(self.a,{'rd':[]});self.assertEqual(len(self.a.sent),2)
  self.Room.calcCrystalReply(self.a,{'rd':[{'id':1}]})
  self.Room.activeSkillReply(self.a,{'sk':1102,'op':0,'lv':1});self.assertEqual(len(self.a.sent),3)
  self.Room.activeSkillReply(self.a,{'sk':1101,'op':0,'lv':1})
  self.L.replyLuckyDrawFurnitureCard(self.a,{'rs':False,'i':{}});self.assertEqual(len(self.a.sent),4)
  self.L.replyLuckyDrawFurnitureCard(self.a,{'rs':True,'i':{'t':2,'ct':1,'rwd':{'id':1}}})
  self.assertEqual([p['e'][0]for n,p in self.a.sent],[151,30,230,240,250])
 def test_bbs_original_close_retires_only_bound_root5(self):
  self.a.triggerClientNewbee({'e':5});p=self.BBS();p.valid=True;p.anim_timer=None
  noop=lambda *a,**k:None
  p.light_jingshenli=noop;p.proc_event=noop;p.notify_hide=noop;p.visible_self_layer=noop;p.reset_bbs_anim=noop
  self.gg.ui.actions=types.SimpleNamespace(bbs_home=types.SimpleNamespace(**dict((n,types.SimpleNamespace(stop=noop))for n in ['loop','banner','memory','expbook'])))
  self.gg.logic.game_state=types.SimpleNamespace(current=0);self.env['const'].GameState=types.SimpleNamespace(CITY=1)
  self.gg.audio_mgr=types.SimpleNamespace(ui_sound=noop);self.gg.exec_delay=noop
  p.notify_show();p.notify_close();self.assertEqual(self.a.sent[-1][1],{'e':[5]});self.assertNotIn(4,self.a.newbeeData.finish_newbee)
  old=self.a;self.a=self.actor();self.gg.avatar=self.a;self.a.triggerClientNewbee({'e':5});p.notify_close();self.assertFalse(self.a.sent)
 def test_delivery_close_original_callback_sync_and_async(self):
  noop=lambda *a,**k:None;callbacks=[];self.external=[];self.stages=[]
  self.a.newbeeData.init_zhuangxiu_stage=3;self.a.triggerExternalEvent=self.external.append;self.a.passInitZhuangxiu=self.stages.append
  self.gg.ui.panels.newbee_guidance=types.SimpleNamespace(is_begin=True)
  self.gg.ui.actions=types.SimpleNamespace(city_room_danchi_new=types.SimpleNamespace(close=types.SimpleNamespace(start=callbacks.append)))
  self.gg.audio_mgr=types.SimpleNamespace(ui_sound=noop)
  panel=self.Danchi();panel.valid=True;panel._q7_furniture_generation=(self.a,self.a.luckyDrawData);panel.destroy_self_layer=noop
  self.a.triggerClientNewbee({'e':253});panel.on_close_click(None,2);self.assertFalse(self.a.sent)
  callbacks.pop()();self.assertEqual(self.a.sent[-1][1],{'e':[253]});self.assertEqual(self.external,[391]);self.assertEqual(self.stages,[4])
  self.a.triggerProcessingEvent({'pe':[]});self.a.newbeeData.finish_newbee=[];self.a.triggerClientNewbee({'e':253})
  self.gg.ui.actions.city_room_danchi_new.close.start=lambda cb:cb()
  panel.on_close_click(None,2);self.assertEqual(self.a.sent[-1][1],{'e':[253]});self.assertEqual(self.stages,[4,4])
 def test_delivery_stale_callback_no_newowner_business(self):
  noop=lambda *a,**k:None;callbacks=[];destroyed=[]
  self.gg.ui.panels.newbee_guidance=types.SimpleNamespace(is_begin=True);self.gg.ui.actions=types.SimpleNamespace(city_room_danchi_new=types.SimpleNamespace(close=types.SimpleNamespace(start=callbacks.append)));self.gg.audio_mgr=types.SimpleNamespace(ui_sound=noop)
  panel=self.Danchi();panel._q7_furniture_generation=(self.a,self.a.luckyDrawData);panel.destroy_self_layer=lambda:destroyed.append(True)
  panel.on_close_click(None,2);self.a=self.actor();self.gg.avatar=self.a;self.a.triggerClientNewbee({'e':253});callbacks.pop()();self.assertFalse(self.a.sent);self.assertEqual(destroyed,[True]);self.assertFalse(panel.cover)
 def test_login_original_pe_safe_tick_current_city_fact(self):
  data=self.ND();self.gg.avatar=None;data.initFromDict({'pe':[10,151],'fn':[]})
  self.assertEqual(len(self.delayed),1);self.assertFalse(self.a.sent)
  self.a.newbeeData=data;data.finishNewbee=types.MethodType(original('analysis/original-py-640/entity/avatar_attrs/NewbeeData.py','finishNewbee',self.env),data)
  self.a.cityData.useCanteen=True;self.gg.avatar=self.a;self.delayed.pop()()
  self.assertEqual([p['e']for n,p in self.a.sent],[[10],[151]])
 def test_superseded_or_oldowner_login_tick_no_finish(self):
  data=self.ND();data.initFromDict({'pe':[10]});data.initFromDict({'pe':[]});self.a.newbeeData=data
  self.delayed[0]();self.assertFalse(self.a.sent)
  self.a.newbeeData=types.SimpleNamespace();self.delayed[1]();self.assertFalse(self.a.sent)
 def test_delivery_old_callback_cannot_destroy_reinitialized_layer(self):
  noop=lambda *a,**k:None;callbacks=[];destroyed=[]
  self.gg.ui.panels.newbee_guidance=types.SimpleNamespace(is_begin=True);self.gg.ui.actions=types.SimpleNamespace(city_room_danchi_new=types.SimpleNamespace(close=types.SimpleNamespace(start=callbacks.append)));self.gg.audio_mgr=types.SimpleNamespace(ui_sound=noop)
  panel=self.Danchi();panel._q7_furniture_generation=(self.a,self.a.luckyDrawData);panel.destroy_self_layer=lambda:destroyed.append(True)
  panel.on_close_click(None,1);self.assertFalse(callbacks)
  panel.on_close_click(None,2);panel._q7_furniture_generation=(self.a,self.a.luckyDrawData);panel.cover=True
  callbacks.pop()();self.assertFalse(destroyed);self.assertTrue(panel.cover)
 def test_original_scheme_save_requires_bound_current_tv_and_true_result(self):
  self.a.triggerClientNewbee({'e':211});self.a.furnitureData=types.SimpleNamespace(curSchemeType='home',scheme={'home':{'cur':'s1'}})
  panel=self.Designer();panel.valid=True
  items=[types.SimpleNamespace(itemid=1,key='x',wrap=1,selected=False)]*4+[self.env['Furniture'](51)]
  noop=lambda *a,**k:None
  def node():
   layout=types.SimpleNamespace(getMargin=lambda:types.SimpleNamespace(top=0,left=0),setMargin=noop)
   return types.SimpleNamespace(setVisible=noop,setScale=noop,getContentSize=lambda:types.SimpleNamespace(width=100,height=50),getLayoutParameter=lambda:layout,setInnerContainerSize=noop,requestDoLayout=noop,scrollToLeft=noop)
  panel.furniture_item_dict=dict(zip([0,1,2,3,10118],items));panel.furnitures={};panel.filter_furniture=lambda *a:True;panel.sort_furniture=lambda a:list(a)
  panel.fur_category=1;panel.fur_sub_category=1;panel.scroll_empty=node();panel.left_arrow=node();panel.right_arrow=node();panel.scrollview=node()
  panel.list_comp=[types.SimpleNamespace(_node=node(),set_item=noop,set_select=noop,set_rt_num=noop)for i in items]
  panel.check_show_arrow=noop;panel.refresh_drawing_warning_info=noop;panel.refresh_furniture_data=noop;panel.init_category=noop;panel.refresh_red=noop;panel.getCurFurnitureInfo=lambda:('home','s1')
  self.env['cc'].cc=types.SimpleNamespace(Size=lambda *a:a)
  self.gg.ui.actions=types.SimpleNamespace(city_room_zhuangxiu=types.SimpleNamespace(open=types.SimpleNamespace(start=noop),bottom_in=types.SimpleNamespace(start=noop)))
  panel.notify_show('home','s1');panel.refresh_panel()
  self.assertEqual(self.a._p7_tutorial_furniture_target[3],'')
  # Execute the actual designer's empty-key UUID branch; model construction
  # and its original tree notification are explicit rendering/event seams.
  import textwrap
  lines=(R/'analysis/original-py-640/game_scene/components/FurnitureDesignerComp.py').read_text().splitlines(True)
  start=[i for i,line in enumerate(lines) if line.startswith('    def createEntity(')][-1]
  end=next(i for i in range(start+1,len(lines)) if lines[i].startswith('    def '))
  env={'IdManager':types.SimpleNamespace(IdManager=types.SimpleNamespace(genid=lambda:'tv'))}
  exec(str(FIX.refactor_string(textwrap.dedent(''.join(lines[start:end]))+'\n','actual-createEntity')),env)
  created={}
  def model_create(key,data,pos):
   created[key]=types.SimpleNamespace(id=51,key=key);panel.add_furniture_data(key,created[key]);return True
  designer=types.SimpleNamespace(furnitureMgr=types.SimpleNamespace(createEntity=model_create,getEntity=created.get))
  result=env['createEntity'](designer,'',{'id':51},(0,0,0),setEdit=False)
  self.assertEqual(result.key,'tv')
  self.assertEqual(self.a._p7_tutorial_furniture_target[3],'tv')
  # Original create selected a real entity; subsequent sort moves it from index4.
  panel.sort_furniture=lambda values:sorted(values,key=lambda item:not item.selected)
  panel.refresh_panel();self.assertEqual(panel.panel_furnitures[0].key,'tv')
  self.assertEqual(self.a._p7_tutorial_furniture_target[3],'tv')
  callbacks=[];cleanup=[]
  self.a.callServerMethod=lambda name,params,**kwargs:callbacks.append(kwargs['callback'])
  self.FM.saveFurnitureScheme(self.a,'home','s1',{'t':'home','e':{'tv':{'id':51}}},cleanup.append)
  callbacks.pop()(False);self.assertFalse(self.a.sent);self.assertEqual(cleanup,[False])
  self.FM.saveFurnitureScheme(self.a,'home','s1',{'t':'home','e':{'tv':{'id':239}}},cleanup.append)
  callbacks.pop()(True);self.assertFalse(self.a.sent)
  self.FM.saveFurnitureScheme(self.a,'home','s1',{'t':'home','e':{'tv':{'id':51}}},cleanup.append)
  callbacks.pop()(True);self.assertEqual(self.a.sent[-1][1],{'e':[211]});self.assertEqual(cleanup,[False,True,True])
 def test_copied_avatar_identity_check(self):
  Avatar=type('ClientAvatar',(),dict(self.state.member_copies));self.assertTrue(self.state.check_avatar(Avatar))
  Avatar.triggerClientNewbee=lambda *a:None
  with self.assertRaises(RuntimeError):self.state.check_avatar(Avatar)
 def test_original_gameobject_meta_copies_and_registers_adapter(self):
  import inspect
  path=R/'analysis/original-py-640/com/base/game_object.py';text=path.read_text();body=text[text.index('class GameObjectMeta('):text.index('class GameObject(object):')]
  base=type('GameObjectMember',(),{});mapping=dict(self.state.member_copies);mapping['finishNewbee']=self.M.finishNewbee;mapping['triggerNewbee']=self.M.triggerNewbee
  renamed=[]
  for name,function in mapping.items():
   function.im_func=function
   if hasattr(function,'rpcmethod'):
    renamed.append((function,function.__name__));function.__name__='_@call_by_server_'+name
  try:
   env={'GameObjectMember':base,'members_cache':{},'method_cache':{},'inspect':types.SimpleNamespace(getmembers=inspect.getmembers,ismethod=lambda f:isinstance(f,types.FunctionType)),'update_mgr':types.SimpleNamespace(UpdaterMgr=types.SimpleNamespace(inst=lambda:types.SimpleNamespace(update_funcs={},insert=lambda *a:None))),'sys':types.SimpleNamespace(reloading=False)}
   fix=RefactoringTool(['lib2to3.fixes.fix_print','lib2to3.fixes.fix_tuple_params','lib2to3.fixes.fix_filter']);exec(str(fix.refactor_string(body,'GameObjectMeta')),env)
   member=type('CopiedMember',(base,),mapping);Avatar=env['GameObjectMeta']('ClientAvatar',(member,),{'METHOD_HASH_DICT':{}})
   self.assertTrue(self.state.check_avatar(Avatar));self.assertEqual(Avatar.METHOD_HASH_DICT['ClientAvatar'][hash('triggerClientNewbee')],'triggerClientNewbee')
   actor=Avatar();actor.__dict__.update(self.a.__dict__);self.gg.avatar=actor
   Avatar.triggerClientNewbee.rpcmethod.call(actor,None,{'e':10});self.assertEqual(actor.sent[-1][1],{'e':[10]})
  finally:
   for function,name in renamed:function.__name__=name
 def test_actual_furniture_installer_two_phase_coinstallation(self):
  helper.FurnitureUiTests.setUpClass();fixture=helper.FurnitureUiTests();fixture.setUp();self.addCleanup(fixture.doCleanups)
  furniture_owner=fixture.install();actor=fixture.gg.avatar
  # Original close is outside furniture's method set, precisely the new hook seam.
  fixture.env['cc'].ccui.TOUCH_EVENT_BEGAN=0;fixture.env['cc'].ccui.TOUCH_EVENT_MOVED=1;fixture.env['cc'].ccui.TOUCH_EVENT_CANCELED=3
  multi=original('analysis/original-py-640/cocos/ui_utils.py','checkMultiClick',fixture.env,top=True)
  fixture.Panel.on_close_click=multi(original('analysis/original-py-640/cocos/panels/city_room_danchi_new.py','on_close_click',fixture.env))
  self.state.observers=[row for row in self.state.observers if row[0]not in (self.BBS,self.Danchi,self.Designer)]
  self.state.modules=[row for row in self.state.modules if not row[0].startswith('cocos.panels.')]
  self.state.panels=None;self.state.gg=fixture.gg;fixture.gg.avatar=None
  self.p.install_panels();fixture.gg.avatar=actor
  self.assertIs(fixture.install(),furniture_owner);self.assertIs(self.p.install_panels(),self.state)
 def test_login_tick_superseded_by_original_rpc_clear(self):
  data=self.ND();data.initFromDict({'pe':[10]});self.a.newbeeData=data
  data.canNewbeeTrigger=lambda *a:False;data.clent_trigger_event_list=[]
  data.finishNewbee=types.MethodType(original('analysis/original-py-640/entity/avatar_attrs/NewbeeData.py','finishNewbee',self.env),data)
  self.a.triggerProcessingEvent({'pe':[]});self.delayed.pop()()
  self.assertFalse(self.a.sent);self.assertEqual(data.processing_event,[])
 def test_login_tick_cannot_erase_new_server_started_root(self):
  data=self.ND();data.initFromDict({'pe':[10]});self.a.newbeeData=data
  data.canNewbeeTrigger=lambda *a:False;data.clent_trigger_event_list=[]
  data.finishNewbee=types.MethodType(original('analysis/original-py-640/entity/avatar_attrs/NewbeeData.py','finishNewbee',self.env),data)
  self.a.triggerClientNewbee({'e':211});self.delayed.pop()()
  self.assertFalse(self.a.sent)
  self.assertIn(211,getattr(self.a,self.p._STATE)['started'])
  self.assertNotIn(10,getattr(self.a,self.p._STATE)['started'])
 def test_delivery_finish_enqueue_failure_still_original_close_cleanup(self):
  noop=lambda *a,**k:None;callbacks=[];destroyed=[];stages=[]
  self.gg.ui.panels.newbee_guidance=types.SimpleNamespace(is_begin=True);self.gg.ui.actions=types.SimpleNamespace(city_room_danchi_new=types.SimpleNamespace(close=types.SimpleNamespace(start=callbacks.append)));self.gg.audio_mgr=types.SimpleNamespace(ui_sound=noop)
  self.a.newbeeData.init_zhuangxiu_stage=3;self.a.triggerExternalEvent=lambda *a:stages.append('event');self.a.passInitZhuangxiu=stages.append
  panel=self.Danchi();panel._q7_furniture_generation=(self.a,self.a.luckyDrawData);panel.destroy_self_layer=lambda:destroyed.append(True)
  self.a.triggerClientNewbee({'e':253});panel.on_close_click(None,2)
  self.a.callServerMethodReliable=lambda *a:(_ for _ in ()).throw(IOError('fixture enqueue'))
  with self.assertRaises(IOError):callbacks.pop()()
  self.assertFalse(panel.cover);self.assertEqual(destroyed,[True]);self.assertFalse(stages)
  self.assertNotIn(253,self.a.newbeeData.finish_newbee);self.assertIn(253,getattr(self.a,self.p._STATE)['started'])
 def test_native_metadata_dispatch_hits_same_adapter(self):
  self.M.triggerClientNewbee.rpcmethod.call(self.a,None,{'e':10})
  self.M.triggerProcessingEvent.rpcmethod.call(self.a,None,{'pe':[93]})
  self.assertEqual([p['e']for n,p in self.a.sent],[[10],[93]])
  self.M.triggerClientNewbee.rpcmethod.call(self.a,None,{'_':{0:120}})
  self.assertEqual(self.a.sent[-1][1],{'e':[120]})
 def test_build_target_is_original_central_build2(self):
  self.a.triggerProcessingEvent({'pe':[20,24]})
  self.C.area_build_reply(self.a,{'rs':True,'aid':2,'ext':{}});self.assertFalse(self.a.sent)
  self.a.cityData.get_area_building=lambda n:{'1':3}
  self.C.area_build_reply(self.a,{'rs':True,'aid':1,'ext':{}});self.assertFalse(self.a.sent)
  self.a.cityData.get_area_building=lambda n:{'1':2}
  self.C.area_build_request(self.a,1,1,2,[]);self.a.sent.clear()
  self.C.area_build_reply(self.a,{'rs':True,'aid':1,'ext':{}});self.assertEqual(len(self.a.sent),2)
 def test_authoritative_absence_allows_new_started_cycle(self):
  self.a.triggerClientNewbee({'e':10});self.a.triggerProcessingEvent({'pe':[]});self.a.triggerClientNewbee({'e':10});self.assertEqual(len(self.a.sent),2)
 def test_unapproved_and_invalid_no_finish(self):
  self.a.triggerProcessingEvent({'pe':[5,74,211,253,999]});self.assertFalse(self.a.sent)
  self.a.triggerClientNewbee({'e':'10'});self.assertFalse(self.a.sent)
 def test_metadata_parser_and_callback_preserved(self):
  before=self.state.originals['triggerClientNewbee'];after=self.M.triggerClientNewbee
  self.assertIsNot(after.rpcmethod,before.rpcmethod);self.assertEqual(after.rpcmethod.argtypes,before.rpcmethod.argtypes);self.assertEqual(after.__name__,before.__name__)
  seen=[];self.gg.avatar_callback_map[7]=lambda *a:seen.append(a)
  self.gg.avatar_callback_need_result={};self.a.triggerClientNewbee({'e':10,'_cbid_':7});self.assertEqual(len(seen),1)
 def test_python2_grammar(self):
  from lib2to3.pgen2 import driver
  from lib2to3 import pygram,pytree
  driver.Driver(pygram.python_grammar,convert=pytree.convert).parse_string((R/'runtime/project7_tutorial_completion.py').read_text())
if __name__=='__main__':unittest.main()
