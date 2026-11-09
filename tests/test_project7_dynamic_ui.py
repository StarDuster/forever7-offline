"""Fixed640 original dynamic UI functions + exact frozen companion installers.
Native widgets/scene transport are inert; this is not CSB binding/render evidence.
"""
import _paths  # noqa: E402,F401
import ast,copy,hashlib,importlib.util,json,sys,types,unittest
from pathlib import Path
from unittest.mock import patch
from project7_dynamic_ui_policy import policy,canonical
ROOT=Path(__file__).resolve().parents[1];NS=types.SimpleNamespace

def module(name,path):
 spec=importlib.util.spec_from_file_location(name,ROOT/path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
fixture=module('dynamic_selector_fixture','tests/test_project7_selector_ui.py');ui=module('dynamic_ui','offline/current/runtime/project7_dynamic_ui.py');original=fixture.original
slot=module('dynamic_original_method_loader','offline/current/java/android_dynamic_draw/host_tests/verify_slot_projection.py')

class Widget:
 def __init__(self):self._node=self;self.visible=True;self.text='';self.texture=None;self.callback=None;self.nodes={};self.data=self;self.margin=NS(top=0);self.size=NS(height=80,width=100);self.scale=1;self.items=[];self.references=0;self.touch=True
 def retain(self):self.references+=1
 def release(self):self.references-=1
 def isTouchEnabled(self):return self.touch
 def setVisible(self,v):self.visible=v
 def isVisible(self):return self.visible
 def setString(self,v):self.text=v
 def loadTexture(self,v):self.texture=v
 def setPercent(self,v):self.percent=v
 def setHighlighted(self,v):self.highlighted=v
 def setOpacity(self,v):self.opacity=v
 def setTouchEnabled(self,v):self.touch=v
 def addTouchEventListener(self,fn):self.callback=fn
 def getVirtualRenderer(self):return self
 def getSprite(self):return self
 def setGLProgramState(self,v):pass
 def getInnerContainer(self):return self
 def getLayoutParameter(self):return self
 def getMargin(self):return self.margin
 def setMargin(self,v):self.margin=v
 def getContentSize(self):return self.size
 def setContentSize(self,v):self.size=v
 def setScale(self,v):self.scale=v
 def getScale(self):return self.scale
 def getWorldPosition(self):return NS(x=0,y=0)
 def jumpToTop(self):pass
 def refreshLayout(self):pass
 def set_style(self,*a):self.style=a
 def set_item(self,*a):self.items.append(a)
 def set_yilingqu(self,v):self.claimed=v
 def getChildByName(self,k):return self.nodes.setdefault(k,Widget())

class Action:
 def __init__(self):self.events=[]
 def start(self):self.events.append('start')
 def stop(self):self.events.append('stop')
 def play(self):self.events.append('play')
 def load(self):self.events.append('load')
 def retain(self):pass
 def release(self):self.events.append('release')
 def initWithNode(self,node):return self

class DynamicUiTests(unittest.TestCase):
 actor=fixture.SelectorUiTests.actor
 def setUp(self):
  fixture.SelectorUiTests.setUp(self)
  contract_path=ROOT/'reports/terra-p7-gen-common-reward-contract.json';raw=contract_path.read_bytes();self.assertEqual(hashlib.sha256(raw).hexdigest(),'6d37842579965b71ba434393eb0bbab6298ee7a539b14044b17d32dc1493cca9');self.contract=json.loads(raw)
  for path,digest in self.contract['sha256'].items():self.assertEqual(hashlib.sha256((ROOT/path).read_bytes()).hexdigest(),digest)
  self.ui_policy=policy();self.ui_text=canonical(self.ui_policy).decode('ascii');self.detail_events=[]
  def enum(name):
   lines=(ROOT/'analysis/original-py-640/com/const.py').read_text().splitlines(True);start=next(i for i,l in enumerate(lines) if l.startswith('class '+name+'('));end=next(i for i in range(start+1,len(lines)) if lines[i].strip() and not lines[i].startswith((' ','\n')));namespace={};exec(compile(''.join(lines[start:end]),'<original640 literal enum>','exec'),namespace);return namespace[name]
  for name in ('ItemType','VirtualItemSub','TradeType','WishType'):setattr(self.const,name,enum(name))
  self.env['CHOUKA_JIAOZHI_DATA']=NS(data={(485,r['id']):copy.deepcopy(r) for r in self.ui_policy['jiaozhi']})
  self.rotated={r['id']:dict(r,showrewards=(999999,)) for r in self.ui_policy['charge']};self.rotated[900]={'id':900,'drawType':1,'times':17,'showrewards':()};self.env['CHOUKA_LEIJI_REWARD_DATA']=NS(data=self.rotated)
  items={int(k):v for k,v in self.contract['item_data_raw'].items()};common={int(k):v for k,v in self.contract['reward_common_raw'].items()};self.env.update(RewardCommonDataMod=NS(data=common),ItemDataMod=NS(data=items),ITEM_DATA=NS(data=items),TREASURE_DATA=NS(data={}),TreasureGenerateDataMod=NS(data={}))
  helpers=self.env['helpers'];helpers.genCommonReward=original('analysis/research-agent/helpers.py','genCommonReward',self.env,top=True);helpers.getLuckyDrawTreasureType=lambda:();helpers.getCurActivityTime=lambda:(2026,11,4,0,0,0,0,0,-1)
  self.Avatar.checkJiaozhiInTime=original('analysis/original-py-640/entity/avatar_members/LuckyDrawMember.py','checkJiaozhiInTime',self.env);self.Avatar.getChoukaInfoDataByType=original('analysis/original-py-640/entity/avatar_members/LuckyDrawMember.py','getChoukaInfoDataByType',self.env)
  self.env['HeroDataMod']=NS(data={147:{'name':'时鸩'},141:{'name':'席琳'}});self.env['CHOUKA_INFO']=self.env['CHOUKA_INFO_DATA'];self.env['ui_utils']=NS(checkMultiClick=lambda f:f,setRTDesc=lambda node,text,**k:node.setString(text),GridScrollView=lambda *a,**k:self.grid(a[1]))
  self.env['ui_utils'].checkMultiClick=original('analysis/original-py-640/cocos/ui_utils.py','checkMultiClick',self.env,top=True)
  self.env['cc'].ccui.TOUCH_EVENT_BEGAN=0;self.env['cc'].ccui.TOUCH_EVENT_MOVED=1;self.env['cc'].ccui.TOUCH_EVENT_CANCELED=3
  self.gg.ui.multi_click=0;self.gg.ui.cur_sender=None;self.gg.ui.cur_panel=None;self.gg.ui.panels.newbee_guidance=NS(is_begin=False)
  self.env['cc'].ccs=NS(ActionManagerEx=NS(getInstance=lambda:NS(getActionByName=lambda *a:Action())))
  self.gg.ui.shaders=NS(image=lambda name:NS(instance=lambda **k:NS(shader=None)));self.gg.ui.actions.card_jiaozhi_2=NS(activity_in=Action(),item_loop=Action());self.gg.ui.actions.card_leichong=NS(item_loop=Action())
  self.gg.audio_mgr=NS(ui_sound=lambda *a:None);self.gg.city=NS(touch_id=-1,notify_show_decoration=lambda *a:self.detail_events.append(('decoration',a)));self.gg.ui.panels.common_property=NS(notify_show=lambda *a:self.detail_events.append(('tooltip',a)))
  self.Box=self.classes[1];self.Box.get_luckyDraw_type=original('analysis/original-py-640/cocos/panels/card_box.py','get_luckyDraw_type',self.env)
  for n in ui._METHODS[0]:setattr(self.Box,n,original('analysis/original-py-640/cocos/panels/card_box.py',n,self.env))
  self.new_classes=[]
  for index,((name,attr),names) in enumerate(zip(ui._TARGETS[1:],ui._METHODS[1:]),1):
   cls=type(attr,(),{'__getitem__':lambda obj,key:obj.nodes.setdefault(key,Widget())})
   path='analysis/original-py-640/'+name.replace('.','/')+'.py'
   source=(ROOT/path).read_text();tree=ast.parse(str(slot.FIX.refactor_string(source,path)))
   for declaration in tree.body:
    if isinstance(declaration,ast.ClassDef):
     for node in declaration.body:
      if isinstance(node,ast.FunctionDef):
       decorated=bool(node.decorator_list);node.decorator_list=[];exec(compile(ast.Module(body=[node],type_ignores=[]),path+':selected','exec'),self.env);fn=self.env[node.name];setattr(cls,node.name,self.env['ui_utils'].checkMultiClick(fn) if decorated else fn)
   if index==1:
    cls.IMG_SHADER=None;cls.IMG_MASK='cocos/image/bbs/activity_39_mask_dispatch.png';cls.IMG_PATH='cocos/image/hero/skill_dazhao/%d.png';cls.TAB_INDEX_JIAOZHI=1;cls.TAB_INDEX_LEICHOU=2;self.env['Panel']=cls
   mod=types.ModuleType(name);setattr(mod,attr,cls);patcher=patch.dict(sys.modules,{name:mod});patcher.start();self.addCleanup(patcher.stop);self.new_classes.append(cls)
  p=patch.dict(sys.modules,{'C_file':NS(find_res_file=lambda path,suffix:True)});p.start();self.addCleanup(p.stop)
  self.dynamic=ui.install(self.ui_text,fixture.friend.draw.policy._HistoryAvatar,self.state)
  data=self.gg.avatar.luckyDrawData;data.activity_data[485]=NS(card_times=0,is_open_file=True,jiaozhi_count={147:0},jiaozhi_rewards={},replace_count={147:0});data.is_open_file=False;data.debug_test=False
  from read_data_table import read
  self.env['CHOUKA_TREASURE_WISH']=NS(data=read(ROOT/'analysis/original-py-640/com/data/cdata/chouka_treasure_wish.py'))
  self.Avatar.guessServerTime=lambda actor:1793750400
  for name in ('getCardTimes','getIsOpenCard','getWishTypeByDrawType','getWishGroupInfoListsByDrawType'):
   setattr(data,name,types.MethodType(original('analysis/original-py-640/entity/avatar_attrs/LuckyDrawData.py',name,self.env),data))
 def grid(self,panel):
  class Grid:
   def update_data_info(g,n,values,**kwargs):
    g.rows=[]
    for row in values:
     comp=self.comp(4,panel);comp.set_info(*row['set_info']);g.rows.append(comp)
   def on_update(g,elapsed):pass
  return Grid()
 def comp(self,index,panel):
  cls=self.dynamic.classes[index];c=cls();c.nodes={};c._node=Widget();c.valid=True;c._panel=panel;c.on_load();
  if index==2:panel.draw_tips=c
  return c
 def panel(self):
  p=self.new_classes[0]();p.nodes={};p._node=Widget();p.valid=True;p.on_init();self.gg.ui.panels.card_jiaozhi_2=p
  p.remove_comp=lambda c:None;p.load_comp=lambda *a,**k:self.comp(3,p);p.destroy_self_layer=lambda:self.detail_events.append(('close',p));p.on_load();return p
 def box(self):
  p=self.Box();p.valid=True;p._node=Widget();p.on_init();p.scene_type='activity';p.draw_type=485;self.gg.ui.panels.card_box=p
  p.add_layer=lambda layer:layer;p.proc_event=lambda event,t,**kwargs:kwargs['_layer'].notify_show(t);p.update_wish_banner=lambda **k:None;p.update_wish_left_info=lambda:None
  return p
 def begin(self,node):
  node.callback(node,0);fn=node.callback
  def held(unused,event):return fn(node,event)
  return held
 def retired(self,callback):
  try:callback(None,2)
  except RuntimeError:pass
 def click(self,node):
  node.callback(node,0);node.callback(node,2)
 def test_actual_helper_fixed_display_oracles(self):
  gen=self.env['helpers'].genCommonReward
  self.assertEqual(gen.__code__.co_argcount,4);self.assertEqual(gen.__code__.co_varnames[:4],('rewards','level','heroes','owner'));self.assertEqual(gen.__defaults__,(1,None,None))
  self.assertEqual(gen((62892,)),{'item':[(7589,1)]});self.assertEqual(gen((62945,62946)),{'item':[(16668,1),(16668,2)]});self.assertEqual(gen((62950,)),{'pendant':[(16673,1)]})
 def test_original_jiaozhi_ignores_expired_only_within_scoped_panel(self):
  self.assertFalse(self.gg.avatar.checkJiaozhiInTime((485,133)));before=copy.deepcopy(self.env['CHOUKA_JIAOZHI_DATA'].data);clock=self.env['time'];p=self.panel();p.notify_show(485)
  self.assertEqual(p.hero,147);self.assertEqual(p.jiaozhi_progress_num1.text,'0');self.assertEqual(p.jiaozhi_progress_num2.text,'/6');self.assertEqual(len(p.jiaozhi_scrollview.rows),6);self.assertEqual(before,self.env['CHOUKA_JIAOZHI_DATA'].data);self.assertIs(self.env['time'],clock);self.assertFalse(self.gg.avatar.checkJiaozhiInTime((485,133)))
 def test_original_charge_pages_use_fixed_four_rows_not_rotation(self):
  p=self.panel();before=copy.deepcopy(self.rotated);self.gg.avatar.luckyDrawData.activity_data[485].card_times=36;p.notify_show(485);p.do_btn_leichou_click()
  self.assertEqual(len(p.leichou_list_comps),4);self.assertEqual(set(c.idx for c in p.leichou_list_comps),{274,275,276,277});self.assertEqual(p.leichou_title_num2[1].text,'/180');self.assertEqual(p.hero,147);self.assertEqual(self.rotated,before)
 def test_tips_to_original_jz2_entry_and_blessing_ui_predicate(self):
  p=self.panel();box=self.box();tips=self.comp(2,box);tips.set_info(485);tips.on_jiaozhi_click();self.assertEqual(p.draw_type,485)
  d=self.gg.avatar.luckyDrawData.activity_data[485];d.jiaozhi_count[147]=4;d.replace_count[147]=1;tips.set_jiaozhi();self.assertTrue(tips.blessing.visible);self.gg.avatar.heroMgrData.getHero=lambda h:object();tips.set_jiaozhi();self.assertFalse(tips.blessing.visible)
 def test_frozen_companions_reinstall_and_record_identity(self):
  self.assertIs(fixture.friend.friend.install(fixture.friend.draw.policy._HistoryAvatar),self.state);self.assertIs(fixture.ui.install(self.text,fixture.friend.draw.policy._HistoryAvatar),self.selector);self.assertIs(fixture.friend.draw.policy.install(self.policy_text),self.drawstate);self.assertIs(ui.install(self.ui_text,fixture.friend.draw.policy._HistoryAvatar,self.state),self.dynamic)
 def test_public485_uses_real_main_policy_without_prior_pending(self):
  p=self.panel();data=self.gg.avatar.luckyDrawData;data.activity_data[485].is_open_file=False;ready=self.drawstate.ready
  p.notify_show(485)
  self.assertIs(self.drawstate.ready,ready);self.assertIn(485,ready);self.assertEqual(data.activity_data[485].card_times,0)
 def test_old_avatar_data_and_ui_callbacks_never_reach_current_actions(self):
  for changed in ('avatar','data','ui'):
   p=self.panel();p.notify_show(485);old=self.begin(p.btn_leichou);before=list(self.detail_events)
   if changed=='avatar':self.gg.avatar=self.actor()
   elif changed=='data':self.gg.avatar.luckyDrawData=self.actor().luckyDrawData
   else:self.gg.ui=NS(_lock={'new':1},panels=NS(),actions=NS())
   self.retired(old)
   self.assertEqual(self.detail_events,before)
   # Each mutation is isolated in its own original fixture generation.
   if changed!='ui':
    self.gg.avatar=self.actor();self.gg.avatar.luckyDrawData.activity_data[485]=NS(card_times=0,is_open_file=True,jiaozhi_count={147:0},jiaozhi_rewards={},replace_count={147:0});self.gg.avatar.luckyDrawData.debug_test=False;self.gg.avatar.luckyDrawData.getCardTimes=lambda t:self.gg.avatar.luckyDrawData.activity_data[t].card_times;self.gg.avatar.luckyDrawData.getIsOpenCard=lambda t:t==485
 def test_old_lock_epoch_rejected_but_new_show_scope_works(self):
  p=self.panel();p.notify_show(485);old=self.begin(p.btn_leichou);self.gg.ui.reset_lock()
  self.retired(old)
  p.notify_show(485);self.click(p.btn_leichou);self.assertEqual(p.curr_tab_index,2)
 def test_same_avatar_reinit_retires_old_callbacks(self):
  p=self.panel();p.notify_show(485);old=self.begin(p.btn_leichou);p.on_init();p.on_load()
  self.retired(old)
  p.notify_show(485);self.click(p.btn_leichou);self.assertEqual(p.curr_tab_index,2)
 def test_same_avatar_box_reinit_retires_old_component_callback(self):
  p=self.panel();box=self.box();tips=self.comp(2,box);tips.set_info(485);old=self.begin(tips._node);box.on_init()
  self.retired(old)
  box.scene_type='activity';box.draw_type=485;fresh=self.comp(2,box);fresh.set_info(485);self.click(fresh._node);self.assertEqual(p.draw_type,485)
 def test_old_show_and_parent_component_callbacks_rejected(self):
  p=self.panel();p.notify_show(485);old=self.begin(p.btn_leichou);component=next(c for c in p.jiaozhi_scrollview.rows if c.idx==(485,136));oldbless=component['brd1.memorybless'].callback
  self.assertEqual(component.hero,147);p.notify_show(485)
  self.retired(old)
  self.retired(oldbless)
 def test_required_resource_failure_and_other_pool_original_delegate(self):
  p=self.panel();sys.modules['C_file'].find_res_file=lambda path,suffix:path!='cocos/card_jiaozhi_2.csb'
  with self.assertRaises(RuntimeError):p.notify_show(485)
  p.notify_show(484);self.assertEqual(p.draw_type,484);self.assertEqual(self.gg.avatar.luckyDrawData.activity_data[485].card_times,0)
 def test_policy_table_generation_and_companion_identity_fail_closed(self):
  p=self.panel();p.notify_show(485);old=self.begin(p.btn_leichou);self.env['CHOUKA_LEIJI_REWARD_DATA'].data=dict(self.rotated)
  self.retired(old)
  with self.assertRaises(RuntimeError):ui.install(self.ui_text,fixture.friend.draw.policy._HistoryAvatar,object())
  bad=json.loads(self.ui_text);bad['epochs']['485']+=1
  with self.assertRaises(ValueError):ui.install(json.dumps(bad),fixture.friend.draw.policy._HistoryAvatar,self.state)
 def test_other_pool_rows_and_real_time_are_never_overwritten(self):
  p=self.panel();p.notify_show(485);scope=p._q7_dynamic_scope;before=copy.deepcopy(self.rotated);aliases=scope.aliases(self.env)
  self.assertIs(aliases['CHOUKA_LEIJI_REWARD_DATA'].data.get(900),self.rotated[900]);self.assertEqual(aliases['CHOUKA_LEIJI_REWARD_DATA'].data.get(277)['showrewards'],(62892,));self.assertEqual(self.rotated,before)
  avatar=aliases['gg'].avatar;self.assertTrue(avatar.checkJiaozhiInTime((485,133)));self.assertFalse(avatar.checkJiaozhiInTime((485,999)));self.assertFalse(avatar.checkJiaozhiInTime((484,133)));self.assertFalse(self.gg.avatar.checkJiaozhiInTime((485,133)))
 def test_charge_threshold_views_preserve_actual_counts(self):
  p=self.panel();d=self.gg.avatar.luckyDrawData.activity_data[485]
  for count in (11,12,35,36,89,90,179,180):
   d.card_times=count;p.notify_show(485);p.do_btn_leichou_click();self.assertEqual(p.leichou_title_num1[1].text,str(count));self.assertEqual(d.card_times,count);self.assertEqual(len(p.leichou_list_comps),4)
 def test_original_sync_payload_drives_same_tips_and_details(self):
  import base64
  report=json.loads((ROOT/'reports/project7-dynamic-original-engine-host-final.json').read_text());lines=report['logs']['actual-original-dynamic']['stdout'].splitlines();raw=next(l.split()[2] for l in lines if l.startswith('DYNAMIC_FIXTURE full_sync '));info=fixture.friend.module('dynamic_reply_bson','offline/current/java/android_draw_policy/host_tests/verify_original_consumers.py').bson(base64.b64decode(raw))['i'];self.gg.avatar.luckyDrawData.inc_up_cnt={1:71}
  sync=original('analysis/original-py-640/entity/avatar_members/LuckyDrawMember.py','syncJiaozhiData',self.env);sync(self.gg.avatar,info)
  p=self.panel();p.notify_show(485);p.do_btn_jiaozhi_click();self.assertEqual(p.jiaozhi_progress_num1.text,'6');self.assertTrue(p.jiaozhi_item_obtained.visible);self.assertEqual(self.gg.avatar.luckyDrawData.activity_data[485].jiaozhi_rewards[991],42)
 def test_python2_ascii_policy_projection_and_no_new_rpc_or_lock_owner(self):
  source=(ROOT/'offline/current/runtime/project7_dynamic_ui.py').read_bytes();source.decode('ascii');slot.FIX.refactor_string(source.decode('ascii'),'dynamic-ui');self.assertEqual(hashlib.sha256(canonical(policy())).hexdigest(),ui._POLICY_RAW_SHA)
  p=self.panel();before=dict(self.gg.ui._lock);sent=list(self.sent);p.notify_show(485);p.do_btn_leichou_click();self.assertEqual(self.gg.ui._lock,before);self.assertEqual(self.sent,sent);self.assertIs(self.Avatar.tutorialIdentity,self.tutorial_identity)
 def test_actual_checkmulti_retains_once_and_normal_end_releases_once(self):
  p=self.panel();p.notify_show(485);sender=p.btn_leichou;end=self.begin(sender)
  self.assertEqual((sender.references,self.gg.ui.multi_click),(1,1));end(None,2);end(None,2)
  self.assertEqual((sender.references,self.gg.ui.multi_click),(0,0));self.assertEqual(p.curr_tab_index,2)
 def test_retained_begin_avatar_change_end_cleanup_without_business(self):
  p=self.panel();p.notify_show(485);sender=p.btn_leichou;end=self.begin(sender);old_ui=self.gg.ui;self.gg.avatar=self.actor();before=p.curr_tab_index
  self.retired(end);self.retired(end);self.assertEqual(sender.references,0);self.assertEqual(old_ui.multi_click,0);self.assertIsNone(old_ui.cur_sender);self.assertEqual(p.curr_tab_index,before)
 def test_retained_begin_ui_change_end_cleans_only_old_ui(self):
  p=self.panel();p.notify_show(485);sender=p.btn_leichou;end=self.begin(sender);old_ui=self.gg.ui;new_sender=Widget();self.gg.ui=NS(multi_click=1,cur_sender=new_sender,cur_panel=object(),_lock={'rpc':3})
  self.retired(end);self.assertEqual(sender.references,0);self.assertEqual(old_ui.multi_click,0);self.assertEqual(self.gg.ui.multi_click,1);self.assertIs(self.gg.ui.cur_sender,new_sender);self.assertEqual(self.gg.ui._lock,{'rpc':3})
 def test_same_sender_new_begin_old_bound_end_cannot_release_new_gesture(self):
  p=self.panel();p.notify_show(485);sender=p.btn_leichou;old=self.begin(sender);old(None,2);p.do_btn_jiaozhi_click();new=self.begin(sender);token=self.gg.ui._q7_dynamic_click_lease
  old(None,2);self.assertIs(self.gg.ui._q7_dynamic_click_lease,token);self.assertEqual(sender.references,1);self.assertEqual(self.gg.ui.multi_click,1);self.assertEqual(p.curr_tab_index,1)
  new(None,2);self.assertEqual(sender.references,0);self.assertEqual(self.gg.ui.multi_click,0);self.assertEqual(p.curr_tab_index,2)
 def test_ambiguous_overlapping_begin_cancels_and_refuses_business(self):
  p=self.panel();p.notify_show(485);sender=p.btn_leichou;old=self.begin(sender);sender.callback(sender,0);self.assertEqual(sender.references,0);self.assertEqual(self.gg.ui.multi_click,0);self.assertEqual(p.curr_tab_index,1);old(None,2);self.assertEqual(p.curr_tab_index,1)
  self.click(sender);self.assertEqual(p.curr_tab_index,2)
 def test_close_after_pending_ends_cleans_current_panel_without_admission(self):
  p=self.panel();p.notify_show(485);self.gg.avatar.luckyDrawData.activity_data[485].is_open_file=False;self.click(p.btn_close);self.assertEqual(self.detail_events[-1],('close',p));self.assertIsNone(p.__dict__.get('_q7_dynamic_scope'));self.assertEqual(self.gg.ui.multi_click,0)
 def test_fixed_source_helper_code_object_and_boundary(self):
  from tools import bytecode27
  code=bytecode27.read(ROOT/'analysis/android640-scripts/com/utils/helpers.marshal');found=[c for c in code.co_consts if getattr(c,'co_name',None)=='genCommonReward'];self.assertEqual(len(found),1);c=found[0]
  self.assertEqual(c.co_firstlineno,697);self.assertEqual(c.co_argcount,4);self.assertEqual(tuple(c.co_varnames[:4]),('rewards','level','heroes','owner'));self.assertEqual(hashlib.sha256(c.co_code).hexdigest(),self.contract['helper']['decoded_code_sha256'])
 def test_current_rotation_generation_change_retires_bound_click(self):
  class Mapping(dict):pass
  rows=Mapping(self.rotated);rows._rot_id=1;rows._module=NS(data={});self.env['CHOUKA_LEIJI_REWARD_DATA'].data=rows
  p=self.panel();p.notify_show(485);sender=p.btn_leichou;end=self.begin(sender);rows._rot_id=2;self.retired(end);self.assertEqual(sender.references,0);self.assertEqual(p.curr_tab_index,1)
 def test_policy_projection_works_from_independent_fixed_data_directory(self):
  import tempfile,shutil
  from project7_dynamic_catalog import DEFAULT
  from project7_dynamic_ui_policy import ui_policy
  with tempfile.TemporaryDirectory() as td:
   for name in ('catalog-v1.json.gz','contract.json'):shutil.copyfile(DEFAULT/name,Path(td)/name)
   self.assertEqual(canonical(ui_policy(Path(td))),canonical(self.ui_policy))
 def test_true_csb_tree_literal_and_bounded_paths_and_actions(self):
  import re
  contract=json.loads((ROOT/'reports/terra-p7-legacy-csb-reader-contract.json').read_text());files={Path(f['file']).name:f for f in contract['files']}
  def norm(value):return re.sub(r'>[^.]+\.[^.]+','',value)
  wanted={name:{norm(w['path']) for w in f['widgets']} for name,f in files.items()}
  sources=[('panels/card_jiaozhi_2.py','card_jiaozhi_2.csb','panel'),('comps/card_common/tips.py','card_common.csb','panel.tips'),('comps/card_common/leichong_info_2.py','card_common.csb','panel.leichong_info_2'),('comps/card_common/jiaozhi_info.py','card_common.csb','panel.jiaozhi_info')]
  for relative,csb,prefix in sources:
   path=ROOT/'analysis/original-py-640/cocos'/relative;tree=ast.parse(str(slot.FIX.refactor_string(path.read_text(),str(path))))
   for n in ast.walk(tree):
    if isinstance(n,ast.Subscript) and isinstance(n.value,ast.Name) and n.value.id=='self' and isinstance(n.slice,ast.Constant) and isinstance(n.slice.value,str):self.assertIn(prefix+'.'+n.slice.value,wanted[csb])
  for i in range(1,4):
   self.assertIn('panel.leichong_info_2.brd%d.num'%i,wanted['card_common.csb']);self.assertIn('panel.leichong_info_2.item%d'%i,wanted['card_common.csb']);self.assertIn('panel.jiaozhi_info.brd%d.memorybless'%i,wanted['card_common.csb'])
   for j in range(1,3):self.assertIn('panel.jiaozhi_info.brd%d.item%d'%(i,j),wanted['card_common.csb'])
  for i in range(1,3):self.assertIn('panel.main_leichou.page_1.progress_1.info.info_%d'%i,wanted['card_jiaozhi_2.csb'])
  self.assertTrue({'activity_in','item_loop'}.issubset({a['name'] for a in files['card_jiaozhi_2.csb']['actions']}));self.assertTrue({'blessing','tips_change'}.issubset({a['name'] for a in files['card_common.csb']['actions']}))
  for f in contract['files']:self.assertEqual(hashlib.sha256((ROOT/f['file']).read_bytes()).hexdigest(),f['sha256'])
 def test_only485_shared_component_dependencies(self):
  from legacy_csb_reader import Reader,widgets
  def tree(name):return {x['path']:x for x in widgets(Reader(ROOT/'analysis/project7/dynamic-ui-resources-v1'/name).read())}
  frame=tree('common_frame.csb');prop=tree('common_property.csb');icon=tree('common_icon.csb');stars=tree('hero_herolist_common.csb')
  for key in ('Panel_1.item','Panel_1.head_little'):self.assertIn(key,frame)
  self.assertIn('Panel_5.tips_common.element>common_icon.elements',prop)
  for color in ('red','blue','yellow'):
   self.assertIn('Panel_11.elements.elements_'+color,icon);self.assertIn('Panel_11.elements.txt_'+color,icon)
  for color in ('green','blue','purple','gold','orange','red'):self.assertIn('Panel_14.star.'+color,stars)
  for i in range(1,6):self.assertIn('Panel_14.starlv.starlv%d'%i,stars)
  for prefix,t in [('Panel_1.head_little',frame),('Panel_11.elements',icon),('Panel_14.star',stars),('Panel_14.starlv',stars)]:self.assertFalse([k for k in t if (k==prefix or k.startswith(prefix+'.')) and '>' in k])
 def test_original_memorybless_to_original_tooltip_positive(self):
  from project7_dream_catalog.produce import literal
  from read_data_table import read
  from unittest.mock import MagicMock
  item_path=ROOT/'analysis/android640-scripts/com/data/cdata/item_data.marshal'
  self.assertEqual(hashlib.sha256(item_path.read_bytes()).hexdigest(),'b498b2fc3f850d416fba2c7c9fb3930ddee680f30cd0d6eb5fb6f59c3ca114b6')
  item=literal(item_path)[10387];hero=read(ROOT/'analysis/original-py-640/com/data/cdata/hero.py')[147]
  self.env['ITEM_DATA'].data[10387]=item
  hero_module=types.ModuleType('com.data.cdata.hero');hero_module.data={147:hero}
  com=types.ModuleType('com');data=types.ModuleType('com.data');cdata=types.ModuleType('com.data.cdata');com.data=data;data.cdata=cdata;cdata.hero=hero_module
  class IterDict(dict):
   def iteritems(self):return self.items()
  tip=NS();tip._node=MagicMock();tip.tips_common=MagicMock();tip.typeDict=IterDict(common=tip.tips_common);tip.commonTitle=MagicMock();tip.commonTxt=MagicMock();tip.commonbrd=MagicMock();tip.panel_destroy=MagicMock();tip.listener=MagicMock();tip.build_highest=MagicMock()
  tip.tips_common.getWorldPosition.return_value=NS(y=200);tip.tips_common.getAnchorPoint.return_value=NS(y=0);tip.tips_common.getContentSize.return_value=NS(height=80,width=100);tip.tips_common.getPosition.return_value=NS(y=200)
  rich=MagicMock();rich.getVirtualRendererSize.return_value=NS(height=20)
  self.env['cc'].ccui.RichText=NS(create=lambda:rich);self.env['cc'].cc=NS(Size=lambda x,y:NS(width=x,height=y),Vec2=lambda x,y:NS(x=x,y=y))
  parsed=[];self.env['ui_utils'].DialougeRtParser=NS(paser=lambda text,**kw:(parsed.append(text) or [],None))
  tip.notify_show=types.MethodType(original('analysis/original-py-640/cocos/panels/common_property.py','notify_show',self.env),tip);self.gg.ui.panels.common_property=tip
  panel=self.panel();panel.notify_show(485);comp=self.comp(4,panel);comp.set_info(138,485,147,0,0)
  with patch.dict(sys.modules,{'com':com,'com.data':data,'com.data.cdata':cdata,'com.data.cdata.hero':hero_module}):comp.on_memorybless(comp['brd1.memorybless'],2)
  tip.commonTitle.setString.assert_called_once_with(item['name']);self.assertEqual(parsed,[item['desc']%((hero['name'],)*3)]);self.assertIs(tip.nowPanel,tip.tips_common);rich.formatText.assert_called_once();self.assertEqual(comp.hero,147)
 def test_click_cleanup_does_not_touch_reset_rpc_dictionary(self):
  p=self.panel();p.notify_show(485);sender=p.btn_leichou;end=self.begin(sender);self.gg.ui.reset_lock();self.gg.ui._lock['newRequest']=7;new=self.gg.ui._lock;self.retired(end);self.assertIs(self.gg.ui._lock,new);self.assertEqual(new,{'newRequest':7});self.assertEqual(sender.references,0)
if __name__=='__main__':unittest.main()
