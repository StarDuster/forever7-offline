"""Finite original 640 bodies with explicit Python2 iterator projection.
No game opcode/JNI/UI engine: only deterministic widget/scene boundary fixtures.
"""
from pathlib import Path
import ast,hashlib,importlib.util,os,sys,textwrap,types,unittest,json
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1]
NS=types.SimpleNamespace
spec=importlib.util.spec_from_file_location('draw_ui',ROOT/'offline/current/runtime/project7_draw_ui.py')
policy=importlib.util.module_from_spec(spec);spec.loader.exec_module(policy)
SOURCES={}
def original(module,name,env):
 p=ROOT/'analysis/research-agent'/(module+'.py');SOURCES[str(p.relative_to(ROOT))]=hashlib.sha256(p.read_bytes()).hexdigest()
 lines=p.read_text().splitlines(True);start=next(i for i,l in enumerate(lines) if l.startswith('    def '+name+'('));end=next((i for i in range(start+1,len(lines)) if lines[i].strip() and not lines[i].startswith('        ') and not lines[i].startswith('\n')),len(lines))
 src=textwrap.dedent(''.join(l for l in lines[start:end] if not l.lstrip().startswith('print ')));tree=ast.parse(src)
 class Py2(ast.NodeTransformer):
  def visit_Attribute(self,n):
   self.generic_visit(n);n.attr={'iteritems':'items'}.get(n.attr,n.attr);return n
 tree=ast.fix_missing_locations(Py2().visit(tree));exec(compile(tree,str(p),'exec'),env);return env[name]
def original_ui(name, env):
 p=ROOT/'analysis/original-py-640/cocos/ui_manager.py';SOURCES[str(p.relative_to(ROOT))]=hashlib.sha256(p.read_bytes()).hexdigest()
 lines=p.read_text().splitlines(True);start=next(i for i,l in enumerate(lines) if l.startswith('    def '+name+'('));end=next(i for i in range(start+1,len(lines)) if lines[i].strip() and not lines[i].startswith(('        ','\n')))
 src=textwrap.dedent(''.join(l for l in lines[start:end] if not l.lstrip().startswith('print ')));exec(compile(src,str(p),'exec'),env);return env[name]
def original_top(relative, name, env, kind='def'):
 p=ROOT/relative;SOURCES[str(p.relative_to(ROOT))]=hashlib.sha256(p.read_bytes()).hexdigest();lines=p.read_text().splitlines(True)
 start=next(i for i,l in enumerate(lines) if l.startswith(kind+' '+name+('(' if kind=='def' else '')));end=next((i for i in range(start+1,len(lines)) if lines[i].strip() and not lines[i].startswith((' ','\n'))),len(lines))
 exec(compile(''.join(lines[start:end]),str(p),'exec'),env);return env[name]
class Widget:
 def __init__(self):self.bright=True;self.visible=True
 def setBright(self,v):self.bright=v
 def setVisible(self,v):self.visible=v
 def setTouchEnabled(self,v):self.enabled=v
 def isBright(self):return self.bright
class Layout:
 def __init__(self):self.margin=NS(top=0,left=0)
 def getMargin(self):return self.margin
 def setMargin(self,m):self.margin=m
class Node:
 def __init__(self):self.layout=Layout();self.size=NS(height=60)
 def getLayoutParameter(self):return self.layout
 def getContentSize(self):return self.size
 def setVisible(self,v):self.visible=v
class Scroll(Node):
 def getInnerContainer(self):return self
 def setContentSize(self,s):self.size=s
 def jumpToPercentVertical(self,p):pass
 def refreshLayout(self):pass
class Comp:
 def __init__(self):self._node=Node()
 def set_info(self,cb,t,image):self._type=t
 def set_icon(self,*item):self.icon=item
class DrawUITests(unittest.TestCase):
 def setUp(self):
  self.pending=False;self.ct=18;self.calls=[]
  self.gg=types.ModuleType('gg');self.gg.avatar=NS(requestLuckyDrawFile=lambda *a:self.calls.append(('new',a)),requestLuckyDrawFileAndOpenAll=lambda *a:self.calls.append(('all',a)),doRequestLuckyDrawFileAndOpenAll=lambda *a:self.calls.append(('all_deferred',a)),level=10,luckyDrawData=NS(getIsOpenCard=lambda t:self.pending,getCardTimes=lambda t:self.ct,newbie_pool_stay=False),checkDrawInTime=lambda t:False,isNewbieLuckyAvailable=lambda:False,doRequestLuckyDrawFile=lambda *a:self.calls.append(('request',a)))
  self.gg.audio_mgr=NS(ui_sound=lambda *a:self.calls.append(('audio',a)))
  self.gg.ui=NS(panels=NS(newbee_guidance=NS(is_begin=True),_panels={},common_message=NS(notify_message=lambda *a:self.calls.append(('message',a)))))
  self.const=NS(LuckyDrawType=NS(NEWBIE=354,NORMAL=1,FRIEND=2,NEWFRIEND=3,ZHOUNIAN_3=99),CardPoolType=NS(TYPE_FURNITURE=9),NEWBIELUCKYLIMIT=18,LUCKYFRIENDDRAW_SORT=99)
  self.table=NS(data={1:dict(show_level_lower_bound=1,show_level_upper_bound=110,sort=1),354:dict(show_level_lower_bound=2,show_level_upper_bound=110,sort=2)})
  self.env={'gg':self.gg,'const':self.const,'CHOUKA_INFO_DATA':self.table,'cc':NS(ccui=NS(TOUCH_EVENT_ENDED=2))}
  Tab=type('Panel',(),{})
  # The full original bodies below are executed; unused entry bodies are ABI
  # fixture seams and are never described as original-function coverage.
  for n in ('init_button_comp','on_open_go_click','refresh_open_cost_coin_and_btn'):
   setattr(Tab,n,original('card_tab',n,self.env))
  def seam(name):
   def f(*args,**kwargs):
    panel=args[0] if args else None
    if name=='on_card_model_rotate' and panel is not None and hasattr(panel,'item_box_panel'):
     panel.item_box_panel.setVisible(True)
    if name=='set_is_open_file' and panel is not None and getattr(panel,'is_open_file',False):
     if hasattr(panel,'item_box_panel'):
      panel.item_box_panel.setVisible(True)
     if hasattr(panel,'model_card_panel'):
      panel.model_card_panel.setVisible(True)
     panel.cur_state='file_open'
    if name=='notify_open_file' and panel is not None and getattr(panel,'raise_notify',False):
     raise RuntimeError('fake notify')
    return self.calls.append((name,args[1:]))
   return f
  for n in ('on_chouka_btn_click','_on_open_go_click','_on_activity_click'):setattr(Tab,n,seam(n))
  Box=type('Panel',(),{})
  for n in ('_on_request_luckydrawfile','_on_request_luckydrawallfile','_on_open_click','on_open_click','on_open_all_click','enter_scene'):setattr(Box,n,original('card_box',n,self.env))
  for n in ('notify_open_file','on_card_model_rotate','set_is_open_file','leave_scene'):setattr(Box,n,seam(n))
  Box.refresh_open_cost_coin_and_btn=seam('box_refresh')
  Scene=type('Scene',(),{n:original('city_chouka',n,self.env) for n in ('change_scene_to_chouka_main','change_scene_to_activity')})
  self.classes=[Tab,Box,Scene];self.modules=[]
  for (name,attr),cls in zip(policy._TARGETS,self.classes):
   m=types.ModuleType(name);setattr(m,attr,cls);m.gg=self.gg;self.modules.append(m)
  # Function fixtures for otherwise unused endpoints must have actual gg globals.
  for cls in self.classes:
   for n,f in list(cls.__dict__.items()):
    if isinstance(f,types.FunctionType) :f.__globals__['gg']=self.gg
  self.patch=patch.dict(sys.modules,dict([('gg',self.gg)]+[(m.__name__,m) for m in self.modules]));self.patch.start();self.addCleanup(self.patch.stop)
 def install(self):return policy.install()
 def panel(self):
  p=self.classes[0]();p.valid=True;p.chouka_btn_comp=[];p.chouka_tab=Scroll();p.draw_type=354;p.load_comp=lambda *a:Comp();p.remove_comp=lambda *a:None;return p
 def test_whole_original_tab_no_pending_filters_and_normalizes(self):
  before=dict(self.table.data);state=self.install();p=self.panel();p.init_button_comp(354)
  self.assertEqual([t for t,s in p.draw_sort],[1,2]);self.assertEqual(self.calls[-1],('on_chouka_btn_click',(1,)));self.assertEqual(self.table.data,before);self.assertEqual(self.ct,18)
 def test_pending_354_public_menu_entries_hide_without_state_change(self):
  self.pending=True;before=dict(self.table.data);open_before=self.gg.avatar.luckyDrawData.getIsOpenCard(354)
  state=self.install();self.assertIsNone(state.menu_type(None));p=self.panel()
  p.init_button_comp(None);self.assertEqual([t for t,s in p.draw_sort],[1,2]);self.assertEqual(self.calls[-1],('on_chouka_btn_click',(1,)))
  self.calls=[];p.init_button_comp(354);self.assertEqual([t for t,s in p.draw_sort],[1,2]);self.assertEqual(self.calls[-1],('on_chouka_btn_click',(1,)))
  self.calls=[];p.on_chouka_btn_click(354);self.assertEqual(self.calls[-1],('on_chouka_btn_click',(1,)))
  self.gg.PanelJumpjumpcb='_on_request_luckydrawfile';self.gg.PanelJumpjumpcbParams=(354,False);self.calls=[]
  p=self.panel();p.init_button_comp(354);self.assertIsNone(self.gg.PanelJumpjumpcb);self.assertEqual(self.calls[-1],('on_chouka_btn_click',(1,)));self.assertFalse(any(c[0] in ('new','all','request') for c in self.calls))
  rows=policy._HistoryRows(self.table.data,state);self.assertNotIn(354,rows.keys());self.assertIsNotNone(rows.get(354))
  self.assertEqual(self.table.data,before);self.assertEqual(self.gg.avatar.luckyDrawData.getIsOpenCard(354),open_before)

 def test_whole_original_tab_pending_ct18_menu_hides_entry(self):
  self.pending=True;before=dict(self.table.data);self.install();p=self.panel();p.init_button_comp(354)
  self.assertEqual([t for t,s in p.draw_sort],[1,2]);self.assertEqual(self.calls[-1],('on_chouka_btn_click',(1,)));self.assertEqual(self.table.data,before);self.assertTrue(self.gg.avatar.luckyDrawData.getIsOpenCard(354));self.assertFalse(self.gg.avatar.checkDrawInTime(354));self.assertFalse(self.gg.avatar.luckyDrawData.newbie_pool_stay)
 def test_whole_original_go_pending_available_only_for_call(self):
  self.pending=True;self.install();p=self.panel();p.on_open_go_click(None,2)
  self.assertIn(('_on_open_go_click',()),self.calls);self.assertFalse(self.gg.avatar.isNewbieLuckyAvailable())
 def test_hidden_stale_go_is_cancelled_not_redirected_paid_normal(self):
  self.install();p=self.panel();p.on_open_go_click(None,2);p._on_activity_click(354)
  self.assertEqual(self.calls,[])
 def test_whole_original_scene_normalizes_before_enter_and_ckbg(self):
  self.install();s=self.classes[2]();s.checkSceneActive=lambda:True;s.second_camera=object();s.main_ui=None
  s.change_camera=lambda *a:None;s.ui_sound=lambda *a:None;s.unload_card_model=lambda:None;s.load_summon_main_model=lambda **k:None
  s.replaceCkbgByDrawType=lambda t:self.calls.append(('ckbg',t));self.gg.ui.panels.card_tab=NS(enter_scene=lambda **k:self.calls.append(('enter',k['_type'])))
  s.change_scene_to_chouka_main(354);self.assertEqual(self.calls,[('enter',1),('ckbg',1)])
  self.calls=[];self.pending=True;s.main_ui=None;s.change_scene_to_chouka_main(354);self.assertEqual(self.calls,[('enter',1),('ckbg',1)])
 def test_actual_deferred_consumer_cancels_only_stale354(self):
  self.install();b=self.classes[1]();b._do_init_card_info=lambda *a:None
  self.gg.PanelJumpjumpcb='_on_request_luckydrawfile';self.gg.PanelJumpjumpcbParams=(354,False)
  b.enter_scene(draw_type=1);self.assertEqual(self.calls,[]);self.assertIsNone(self.gg.PanelJumpjumpcb)
  self.gg.PanelJumpjumpcb='_on_request_luckydrawfile';self.gg.PanelJumpjumpcbParams=(1,True)
  b.enter_scene(draw_type=1);self.assertEqual(self.calls,[('request',(1,True))])
 def test_pending_deferred_consumer_preserves_original354(self):
  self.pending=True;self.install();b=self.classes[1]();b._do_init_card_info=lambda *a:None
  self.gg.PanelJumpjumpcb='_on_request_luckydrawfile';self.gg.PanelJumpjumpcbParams=(354,False);b.enter_scene(draw_type=354)
  self.assertEqual(self.calls,[('request',(354,False))])
 def test_quit_state_next_entry_hidden_and_other_jump_untouched(self):
  self.pending=True;s=self.install();self.pending=False
  self.gg.PanelJumpjumpcb='other';self.gg.PanelJumpjumpcbParams=(354,);p=self.panel();p.init_button_comp(354)
  self.assertNotIn(354,[t for t,x in p.draw_sort]);self.assertEqual(self.gg.PanelJumpjumpcb,'other')
 def test_install_repeat_and_generation_guards(self):
  s=self.install();self.assertIs(self.install(),s)
  self.modules[0].Panel=type('Panel',(),{})
  with self.assertRaises(RuntimeError):s.normalize(354)
 def test_cached_panel_guard(self):
  self.gg.ui.panels._panels['card_tab']=object()
  with self.assertRaises(RuntimeError):self.install()
 def test_real_multiclick_closure_receives_pending_facade(self):
  path=ROOT/'analysis/original-py-640/cocos/ui_utils.py'
  lines=path.read_text().splitlines(True);start=next(i for i,l in enumerate(lines) if l.startswith('def checkMultiClick('));end=next(i for i in range(start+1,len(lines)) if lines[i].strip() and not lines[i].startswith((' ','\n')))
  namespace={'gg':self.gg};exec(compile(''.join(l for l in lines[start:end] if not l.lstrip().startswith('print ')),str(path),'exec'),namespace)
  self.classes[0].on_open_go_click=namespace['checkMultiClick'](self.classes[0].on_open_go_click)
  self.pending=True;self.install();p=self.panel();p.on_open_go_click(None,2)
  self.assertIn(('_on_open_go_click',()),self.calls)
  self.assertFalse(self.gg.avatar.isNewbieLuckyAvailable())
 def test_decorated_stale_touch_keeps_original_release(self):
  path=ROOT/'analysis/original-py-640/cocos/ui_utils.py';lines=path.read_text().splitlines(True)
  start=next(i for i,l in enumerate(lines) if l.startswith('def checkMultiClick('));end=next(i for i in range(start+1,len(lines)) if lines[i].strip() and not lines[i].startswith((' ','\n')))
  cc=NS(ccui=NS(TOUCH_EVENT_BEGAN=0,TOUCH_EVENT_MOVED=1,TOUCH_EVENT_ENDED=2,TOUCH_EVENT_CANCELED=3))
  ns={'gg':self.gg,'cc':cc};exec(compile(''.join(l for l in lines[start:end] if not l.lstrip().startswith('print ')),str(path),'exec'),ns)
  self.classes[0].on_open_go_click=ns['checkMultiClick'](self.classes[0].on_open_go_click)
  self.gg.city=None;self.gg.ui.panels.newbee_guidance.is_begin=False
  sender=NS(isVisible=lambda:True,isTouchEnabled=lambda:True,release=lambda:self.calls.append(('release',())))
  self.gg.ui.cur_sender=sender;self.gg.ui.cur_panel=NS(valid=True);self.gg.ui.multi_click=1
  self.install();self.panel().on_open_go_click(sender,2)
  self.assertEqual(self.calls,[('release',())]);self.assertIsNone(self.gg.ui.cur_sender);self.assertEqual(self.gg.ui.multi_click,0)
 def test_whole_original_refresh_pending_ct18_button_bright(self):
  self.pending=True;self.install();p=self.panel()
  for name in ('once_cost_1','all_cost_2','all_cost_1','panel_open2','btn_open_go','panel_open','btn_open_choose','btn_open_go_text','btn_open_go_text_gry'):setattr(p,name,Widget())
  p.refresh_open_cost_coin_and_btn();self.assertTrue(p.btn_open_go.bright);self.assertTrue(p.btn_open_go_text.visible);self.assertFalse(p.btn_open_go_text_gry.visible)
 def test_method_tamper_and_gg_replacement_rejected(self):
  state=self.install();self.classes[0].init_button_comp=lambda *a:None
  with self.assertRaises(RuntimeError):self.install()
  with patch.dict(sys.modules,{'gg':types.ModuleType('gg')}):
   with self.assertRaises(RuntimeError):state.normalize(354)
 def test_original_quit_consumer_then_animation_callback_routes_normal(self):
  self.pending=True;self.install();self.const.SCENE_SUMMON='summon'
  scene=NS(on_reply_quit_file=lambda result,cb:cb(),begin_change_scene_to_chouka_main=lambda **k:self.calls.append(('route',policy_state.normalize(k['_type']))))
  self.gg.city_container=NS(get_scene_by_key=lambda k:scene,check_scene=lambda s:True)
  box=NS(item_nml_panel=NS(setVisible=lambda x:None,setTouchEnabled=lambda x:None),set_is_open_file=lambda x:None,draw_type=354,reset_file_lianchou_info=lambda:None)
  reply=original('card_box','on_reply_quit_file',self.env);box.on_reply_quit_file=lambda result:reply(box,result);self.gg.ui.panels.card_box=box
  self.gg.avatar.luckyDrawData.setIsFileOpen=lambda t,v:setattr(self,'pending',v)
  consumer=original('LuckyDrawMember','replyQuitFile',self.env);policy_state=getattr(self.classes[0],policy._MARKER)
  consumer(self.gg.avatar,True,354);self.assertFalse(self.pending);self.assertEqual(self.calls,[('route',1)])
 def test_both_delayed_kinds_cancel_only354(self):
  self.install();box=self.classes[1]();box._do_init_card_info=lambda *a:None
  for callback in ('_on_request_luckydrawfile','_on_request_luckydrawallfile'):
   self.gg.PanelJumpjumpcb=callback;self.gg.PanelJumpjumpcbParams=(354,);box.enter_scene(draw_type=1)
   self.assertEqual(self.calls,[]);self.assertIsNone(self.gg.PanelJumpjumpcb)
  self.gg.PanelJumpjumpcb='_on_request_luckydrawallfile';self.gg.PanelJumpjumpcbParams=(1,);box.enter_scene(draw_type=1)
  self.assertEqual(self.calls,[('all_deferred',(1,))])
 def test_box_direct_three_entries_block_without_pending(self):
  self.install();box=self.classes[1]();box.get_luckyDraw_type=lambda:354
  box.btn_open_once=Widget();box.btn_open_all=Widget();box.open_light=Widget()
  box.refresh_open_cost_coin_and_btn();box.on_open_click(None,2);box.on_open_all_click(None,2);box._on_open_click(354)
  self.assertFalse(box.btn_open_once.visible);self.assertFalse(box.btn_open_all.visible);self.assertEqual(self.calls,[])
 def test_activity_scene_blocked_returns_main_without_activity_or_auto_draw(self):
  self.install();scene=self.classes[2]();scene.change_scene_to_chouka_main=lambda t:self.calls.append(('main',t))
  self.gg.PanelJumpjumpcb='_on_request_luckydrawallfile';self.gg.PanelJumpjumpcbParams=(354,)
  scene.change_scene_to_activity(354);self.assertEqual(self.calls,[('main',1)]);self.assertIsNone(self.gg.PanelJumpjumpcb)
 def test_original_activity_scene_pending_ct18_preserved(self):
  self.pending=True;self.install();scene=self.classes[2]();scene.checkSceneActive=lambda:True;scene.change_camera=lambda *a:None;scene.ui_sound=lambda *a:None;scene.second_camera=object();scene.main_ui=None
  scene.get_luckyDraw_type=lambda:scene.draw_type;scene.replaceCkbgByDrawType=lambda t:self.calls.append(('ckbg',t));scene.unload_summon_main_model=lambda:None;scene.load_card_main_model=lambda:self.calls.append(('cardmodel',354))
  self.gg.ui.panels.card_box=NS(enter_scene=lambda **k:self.calls.append(('enteractivity',k['draw_type'])))
  scene.change_scene_to_activity(354);self.assertEqual(self.calls,[('ckbg',354),('cardmodel',354),('enteractivity',354)])
 def test_box_pending_ct18_completed_quit_original_preserved(self):
  self.pending=True;self.install();box=self.classes[1]();box.get_luckyDraw_type=lambda:354;box.is_cover=False;box.cur_state='file_completed';box.item_nml_panel=Widget()
  self.gg.avatar.notify_normal_close_file=lambda t:self.calls.append(('quit',t))
  box.on_open_click(None,2);self.assertEqual(self.calls,[('quit',354)])
  box.refresh_open_cost_coin_and_btn();self.assertEqual(self.calls[-1],('box_refresh',()))
 def test_removed_marker_cannot_rewrap_installed_methods(self):
  self.install()
  for cls in self.classes:delattr(cls,policy._MARKER)
  with self.assertRaises(RuntimeError):self.install()
 def test_ascii_python2_grammar(self):
  text=(ROOT/'offline/current/runtime/project7_draw_ui.py').read_text('ascii')
  from lib2to3.refactor import RefactoringTool
  RefactoringTool([]).refactor_string(text,'project7_draw_ui.py')
if __name__=='__main__':unittest.main()

# Historical policy tests share only fixture setup with the legacy 22 cases.
# They execute additional original method bodies, with explicit UI/network seams.
class HistoryUITests(unittest.TestCase):
 def setUp(self):
  DrawUITests.setUp(self)
  import time
  sys.path.insert(0,str(ROOT/'project7_bridge'/'tools'))
  sys.path.insert(0,str(ROOT/'offline'/'tools'))
  from read_data_table import read
  from project7_feature_assets import history_ui_policy
  self.policy_text=history_ui_policy(ROOT)
  source=(ROOT/'analysis/original-py-640/com/const.py').read_text().splitlines(True);namespace={}
  for name in ('LuckyDrawType','CardPoolType','LuckyDrawIdx','LuckyDrawConsumeStyle','VirtualItem'):
   start=next(i for i,l in enumerate(source) if l.startswith('class '+name+'('));end=next(i for i in range(start+1,len(source)) if source[i].strip() and not source[i].startswith((' ','\n')))
   exec(compile(''.join(source[start:end]),'<original literal enum>','exec'),namespace);setattr(self.const,name,namespace[name])
  self.const.MAX_SUMMON_TIMES_DAY=300;self.const.LUCKYFRIENDDRAW_SORT=20
  info=read(ROOT/'analysis/original-py-640/com/data/cdata/chouka_info.py');self.original_rows=info
  self.table.data=info;self.env.update({'const':self.const,'time':time,'helpers':NS(getHuoDongIds=lambda:([],[])),'chelpers':NS(formatMsgType5Consume=lambda costs:str(costs))})
  consume=read(ROOT/'analysis/original-py-640/com/data/cdata/chouka_consume.py');self.env['CHOUKA_CONSUME']=NS(data=consume)
  Data=type('OriginalMethodsData',(),{})
  for name in ('getIsOpenCard','getCardTimes','getCurCardTimesDay','getTotalTimes','getOpenTimes','getNotOpendCardIndexs','get_draw_info','getOpenConsume','getLuckyDrawConsume','canOpenFile','canOpenCard','canOpenCardByConsume','checkFileAndOpenAllCostByConsume','checkFileAndOpenAllCost','checkLeftAllCardsCostByConsume','checkLeftAllCardsCost','canRequestFile','set_draw_info','setIsFileOpen','addCardTimes'):
   setattr(Data,name,original('LuckyDrawData',name,self.env))
  Data.getLuckDrawNormalOnceHalfConsume=lambda obj:[(0,0)]
  data=Data();data.activity_data={};data.card_times=6;data.is_open_file=False;data.cur_card_times_day=0;data.draw_info={};data.newbie_pool_stay=False
  for t in (229,354,484):data.activity_data[t]=NS(card_times=6,cur_card_times_day=0,is_open_file=False,draw_info={})
  Avatar=type('OriginalMethodsAvatar',(),{})
  for name in ('checkActivity','checkDrawInTime','checkCanRequestLuckyDrawFile','doRequestLuckyDrawFile','requestLuckyDrawFile','requestFile','requestLuckyDrawCard','requestLuckyDrawFileAndOpenAll','doRequestLuckyDrawFileAndOpenAll','requestLuckyDrawAllLeftCard','requestQuitFile','getLuckyDrawTypeCoin','getLuckDrawTypeRewardCoin'):
   setattr(Avatar,name,original('LuckyDrawMember',name,self.env))
  Avatar.guessServerTime=lambda obj:1767225600;Avatar.isNewbieLuckyAvailable=lambda obj:False;Avatar.checkCanLogin777Chouka=lambda obj:False;Avatar.checkCanNewAchievementChouka=lambda obj:False
  Avatar.findItemByID=lambda obj,*a,**k:(0,[]);Avatar.activityOutTimeMessage=lambda obj,t:752
  Avatar.callServerMethod=lambda obj,m,p,**k:self.calls.append(('rpc',m,dict(p)))
  Avatar.callServerMethodReliable=Avatar.callServerMethod
  avatar=Avatar();avatar.luckyDrawData=data;avatar.level=1;avatar.summonCoin=0;avatar.yuanbao=0;avatar.giftCoin=7;avatar.giftCardData=NS(can_half_choose=lambda:False);avatar.methodPoolBase={}
  self.gg.avatar=avatar;self.gg.ui._lock={};self.gg.ui.recon_lock=0
  import tempfile
  self.doc_dir=tempfile.mkdtemp(prefix='draw-ui-selection-')
  self._old_game3d=sys.modules.get('game3d')
  game3d=types.ModuleType('game3d');game3d.get_doc_dir=lambda:self.doc_dir
  sys.modules['game3d']=game3d;self.addCleanup(self._restore_game3d)
  avatar.account='draw-host';policy._POOL_CACHE.clear()
  # Exactly 12 pools: two tests rely on 229/5 and one on an unselected-to-selected sweep.
  self.selection=(2,3,4,5,6,7,8,229,349,350,351,352)
  self.assertTrue(policy.set_pool_selection(self.selection))
  self.gg.ui.panels.wait=NS(notify_show=lambda *a:None,notify_hide=lambda:None,cancel_timer=lambda:None)
  for name in ('lock','unlock','reset_lock'):setattr(self.gg.ui,name,types.MethodType(original_ui(name,self.env),self.gg.ui))
  self.gg.ui.panels.card_moneyexchange=NS(notify_show=lambda *a,**k:self.calls.append(('exchange',a)))
  self.gg.ui.panels.common_confirm_3=NS(notify_confirm=lambda *a,**k:k['confirm_cb']())
  self.gg.exec_delay=lambda ms,cb:None
  self.gg.ui.actions=NS(card_tab=NS(arrow=NS(start=lambda:None)))
  for index,name in policy._HISTORY_METHODS:
   if name in ('on_open_click','on_open_all_click','notify_open_file','set_card_gift','update_avatar_info','on_card_once_click','on_card_left_or_ten_click','on_quit_click'):
    setattr(self.classes[index],name,original('card_tab' if index==0 else 'card_box',name,self.env))
   elif name not in self.classes[index].__dict__:
    def seam(*args,**kwargs):return None
    seam.__globals__['gg']=self.gg;setattr(self.classes[index],name,seam)
  # Original _on_open_go_click's scene/animation boundary is recorded; the
  # actual persistent deferred gg handoff is consumed by original box.enter_scene.
  def go(panel):self.calls.append(('go',panel.draw_type))
  go.__globals__['gg']=self.gg;self.classes[0]._on_open_go_click=go
  for module in self.modules:module.const=self.const
 def install(self):return policy.install(self.policy_text)
 def _restore_game3d(self):
  if self._old_game3d is None:sys.modules.pop('game3d',None)
  else:sys.modules['game3d']=self._old_game3d
  policy._POOL_CACHE.clear()
 def decorated_go(self):
  path=ROOT/'analysis/original-py-640/cocos/ui_utils.py';lines=path.read_text().splitlines(True)
  start=next(i for i,l in enumerate(lines) if l.startswith('def checkMultiClick('));end=next(i for i in range(start+1,len(lines)) if lines[i].strip() and not lines[i].startswith((' ','\n')))
  cc=NS(ccui=NS(TOUCH_EVENT_BEGAN=0,TOUCH_EVENT_MOVED=1,TOUCH_EVENT_ENDED=2,TOUCH_EVENT_CANCELED=3))
  ns={'gg':self.gg,'cc':cc};exec(compile(''.join(l for l in lines[start:end] if not l.lstrip().startswith('print ')),str(path),'exec'),ns)
  self.classes[0].on_open_go_click=ns['checkMultiClick'](self.classes[0].on_open_go_click)
  self.gg.ui.panels.newbee_guidance.is_begin=False;self.gg.city=NS(touch_id=-1)
  self.gg.ui.cur_sender=None;self.gg.ui.cur_panel=None;self.gg.ui.multi_click=0
  self.install()
 def sender(self,name='go'):
  return NS(isVisible=lambda:True,isTouchEnabled=lambda:True,
            retain=lambda:self.calls.append(('retain',name)),
            release=lambda:self.calls.append(('release',name)),
            getName=lambda:name)
 def go_panel(self):
  p=self.panel();p.draw_type=1;p.valid=True;return p
 def test_policy_original_multiclick_began_ended_shares_real_ui_ledger(self):
  self.decorated_go();p=self.go_panel();s=self.sender()
  p.on_open_go_click(s,0)
  self.assertIs(self.gg.ui.cur_sender,s);self.assertIs(self.gg.ui.cur_panel,p);self.assertEqual(self.gg.ui.multi_click,1)
  self.assertNotIn(('go',1),self.calls);self.assertEqual(self.calls.count(('retain','go')),1)
  p.on_open_go_click(s,2)
  self.assertIsNone(self.gg.ui.cur_sender);self.assertIsNone(self.gg.ui.cur_panel);self.assertEqual(self.gg.ui.multi_click,0)
  self.assertEqual(self.calls.count(('go',1)),1);self.assertEqual(self.calls.count(('release','go')),1)
 def test_policy_original_multiclick_canceled_clears_without_business(self):
  self.decorated_go();p=self.go_panel();s=self.sender()
  p.on_open_go_click(s,0);p.on_open_go_click(s,3)
  self.assertIsNone(self.gg.ui.cur_sender);self.assertIsNone(self.gg.ui.cur_panel);self.assertEqual(self.gg.ui.multi_click,0)
  self.assertNotIn(('go',1),self.calls);self.assertEqual(self.calls.count(('release','go')),1)
 def test_policy_original_multiclick_repeated_ended_business_once(self):
  self.decorated_go();p=self.go_panel();s=self.sender()
  p.on_open_go_click(s,0);p.on_open_go_click(s,2);p.on_open_go_click(s,2)
  self.assertEqual(self.calls.count(('go',1)),1);self.assertEqual(self.calls.count(('release','go')),1)
  self.assertIsNone(self.gg.ui.cur_sender);self.assertEqual(self.gg.ui.multi_click,0)
 def test_policy_original_multiclick_competing_sender_cannot_consume_or_release(self):
  self.decorated_go();p=self.go_panel();a=self.sender('a');b=self.sender('b')
  p.on_open_go_click(a,0);p.on_open_go_click(b,0);p.on_open_go_click(b,2)
  self.assertIs(self.gg.ui.cur_sender,a);self.assertIs(self.gg.ui.cur_panel,p);self.assertEqual(self.gg.ui.multi_click,1)
  self.assertNotIn(('go',1),self.calls);self.assertNotIn(('release','a'),self.calls);self.assertNotIn(('release','b'),self.calls)
  p.on_open_go_click(a,2)
  self.assertEqual(self.calls.count(('go',1)),1);self.assertEqual(self.calls.count(('release','a')),1)
  self.assertFalse([c for c in self.calls if c[0] in ('retain','release') and c[1]=='b'])
 def test_policy_original_multiclick_city_latch_blocks_and_clears(self):
  self.decorated_go();p=self.go_panel();s=self.sender();self.gg.city.touch_id=7
  p.on_open_go_click(s,0)
  self.assertIsNone(self.gg.ui.cur_sender);self.assertEqual(self.gg.ui.multi_click,0)
  self.assertNotIn(('go',1),self.calls);self.assertNotIn(('retain','go'),self.calls)
 def test_request_ui_keeps_non_gesture_state_local(self):
  state=self.install();view=policy._RequestUI(state,self.gg.avatar);view.epoch='local-epoch';view.leases.append('lease')
  self.assertNotIn('epoch',self.gg.ui.__dict__);self.assertNotIn('leases',self.gg.ui.__dict__)
  self.assertEqual(view.epoch,'local-epoch');self.assertEqual(view.leases,['lease'])
 def panel(self):
  p=DrawUITests.panel(self);p.chouka_down_arrow=Widget();return p
 def view(self):return policy._HistoryAvatar(self.gg.avatar,self.install())
 def test_policy_pending_354_rows_hide_but_get_preserves_direct_resume(self):
  self.gg.avatar.luckyDrawData.activity_data[354].is_open_file=True;before=dict(self.table.data);state=self.install();rows=policy._HistoryRows(self.table.data,state)
  self.assertNotIn(354,rows.keys());self.assertIsNotNone(rows.get(354));self.assertEqual(self.table.data,before)
  p=self.panel();p.init_button_comp(354);self.assertNotIn(354,[t for t,s in p.draw_sort]);self.assertEqual(self.calls[-1],('on_chouka_btn_click',(1,)))
  self.gg.PanelJumpjumpcb='_on_request_luckydrawfile';self.gg.PanelJumpjumpcbParams=(354,False);self.calls=[];p.init_button_comp(354);self.assertIsNone(self.gg.PanelJumpjumpcb);self.assertFalse(any(c[0] in ('new','all','request') for c in self.calls))

 def test_policy_enabled_hides_354_menu_but_preserves_direct_resume(self):
  self.gg.avatar.level=10;self.gg.avatar.luckyDrawData.activity_data[354].card_times=18;self.gg.avatar.luckyDrawData.activity_data[354].is_open_file=True
  state=self.install();p=self.panel();p.init_button_comp(354);self.assertNotIn(354,[t for t,v in p.draw_sort]);self.assertEqual(self.calls[-1],('on_chouka_btn_click',(1,)));self.assertNotEqual(state.history_aliases({'gg':self.gg,'CHOUKA_INFO_DATA':self.table})['CHOUKA_INFO_DATA'].data.get(354),None)
 def test_real_limitcall_keeps_rate_state_on_real_avatar(self):
  path=ROOT/'analysis/original-py-640/cutils/chelpers.py';lines=path.read_text().splitlines(True);start=next(i for i,l in enumerate(lines) if l.startswith('def limitcall('));end=next(i for i in range(start+1,len(lines)) if lines[i].strip() and not lines[i].startswith((' ','\n')))
  env={'time':NS(time=lambda:100),'gg':self.gg};exec(compile(''.join(lines[start:end]),str(path),'exec'),env)
  cls=type(self.gg.avatar);cls.requestLuckyDrawFile=env['limitcall'](1.8,True)(cls.requestLuckyDrawFile)
  self.view().requestLuckyDrawFile(229);self.assertGreater(self.gg.avatar.methodPoolBase['requestLuckyDrawFile'],100)
  first=len([c for c in self.calls if c[0]=='rpc']);self.view().requestLuckyDrawFile(229);self.assertEqual(len([c for c in self.calls if c[0]=='rpc']),first)
 def test_original_sync_owns_state_then_resume_reveal_and_quit(self):
  path=ROOT/'analysis/original-py-640/entity/avatar_attrs/LuckyDrawData.py';lines=path.read_text().splitlines(True);start=next(i for i,l in enumerate(lines) if l.startswith('class ActivityData('));end=next(i for i in range(start+1,len(lines)) if lines[i].startswith('class LuckyDrawData('));exec(compile(''.join(lines[start:end]).replace('.iteritems()', '.items()'),str(path),'exec'),self.env)
  self.env['LuckyDrawData']=NS(ActivityData=self.env['ActivityData']);self.gg.ui._tree=NS(proc_event=lambda *a,**k:None)
  sync=original('LuckyDrawMember','syncLuckyDrawActivityData',self.env);self.gg.avatar.luckyDrawData.activity_data.pop(229)
  sync(self.gg.avatar,229,{'ct':24,'iof':True,'cctd':0});data=self.gg.avatar.luckyDrawData;self.assertTrue(data.getIsOpenCard(229));self.assertEqual(data.getCardTimes(229),24)
  data.set_draw_info(229,{'0':{'index':0,'is_open':False}})
  state=self.install();view=policy._HistoryAvatar(self.gg.avatar,state);view.requestFile(229)
  box=self.classes[1]();box.get_luckyDraw_type=lambda:229;box.btn_quit=NS(setTouchEnabled=lambda v:None);box.set_btn_quit_touch=lambda:None;box.cur_state='activty_card_click';box._choose_card=lambda t:0
  box.on_card_once_click(None,2);view.requestQuitFile(229)
  self.assertIn(('rpc','requestFile',{'t':229}),self.calls);self.assertIn(('rpc','requestLuckyDrawCard',{'idx':0,'t':229,'nh':False}),self.calls);self.assertIn(('rpc','requestQuitFile',{'t':229}),self.calls)
  self.assertEqual(data.getCardTimes(229),24);self.assertEqual(data.get_draw_info(1),{});self.assertEqual(data.get_draw_info(229)['0']['index'],0)
 def test_unsupported_pending_resume_but_no_new_group_when_absent(self):
  # Current Main publishes all440 historical IDs. Exercise an explicit prior
  # admission fixture instead of assuming production always has a missing pool.
  manifest=json.loads(self.policy_text);t=manifest['ready_ids'].pop()
  self.policy_text=json.dumps(manifest,sort_keys=True,separators=(',',':'))
  with patch.object(policy,'_HISTORY_POLICY',hashlib.sha256(self.policy_text.encode('ascii')).hexdigest()):
   state=self.install();self.assertIn(t,state.history-state.ready);data=self.gg.avatar.luckyDrawData;data.activity_data[t]=NS(card_times=12,cur_card_times_day=0,is_open_file=True,draw_info={})
   view=policy._HistoryAvatar(self.gg.avatar,state);view.doRequestLuckyDrawFile(t);self.assertIn(('rpc','requestFile',{'t':t}),self.calls)
   self.calls=[];data.activity_data[t].is_open_file=False;view.doRequestLuckyDrawFile(t);self.assertEqual(self.calls,[])
 def test_original_balance_display_uses_true_giftcoin(self):
  state=self.install();t=next(t for t in state.selection() if self.original_rows[t].get('rewardCoin')==105)
  self.gg.avatar.getLuckDrawCoinBuy=lambda t:None
  p=self.panel();p.draw_type=t;p.on_add_summon_click=lambda:None;p.on_add_yuanbao_click=lambda:None;p.set_coin_info=lambda info:self.calls.append(('coins',info));p.refresh_open_cost_coin_and_btn=lambda:None;p.update_sp_banner=lambda:None
  p.update_avatar_info();info=next(c[1] for c in self.calls if c[0]=='coins');self.assertTrue(any(coin==105 and balance==7 for coin,balance,callback in info));self.assertEqual(self.gg.avatar.giftCoin,7)
 def test_all_ready_original_newgroup_zero_inventory_without_activity_rows(self):
  state=self.install();self.gg.avatar.luckyDrawData.activity_data.clear();view=policy._HistoryAvatar(self.gg.avatar,state)
  for draw_type in sorted(state.selection()):
   self.assertTrue(view.checkActivity(draw_type),draw_type);self.assertFalse(view.checkActivity(draw_type,pool_type=self.const.CardPoolType.TYPE_FURNITURE),draw_type);self.assertTrue(view.checkDrawInTime(draw_type),draw_type)
   view.requestLuckyDrawFile(draw_type)
  self.assertEqual([c[2]['t'] for c in self.calls if c[0]=='rpc' and c[1]=='requestLuckyDrawFile'],sorted(state.selection()));self.assertEqual(self.gg.avatar.luckyDrawData.activity_data,{})
 def test_normal_pool_low_balance_new_group_and_original_negative(self):
  state=self.install();original=self.gg.avatar.luckyDrawData
  for coin in (1,0):
   self.gg.avatar.summonCoin=coin
   self.assertFalse(original.canOpenFile(1))
   self.assertFalse(self.gg.avatar.checkCanRequestLuckyDrawFile(1))
   view=policy._HistoryAvatar(self.gg.avatar,state)
   self.assertTrue(view.luckyDrawData.canOpenFile(1))
   self.assertTrue(view.checkCanRequestLuckyDrawFile(1))
   self.calls=[];view.requestLuckyDrawFile(1)
   self.assertIn(('rpc','requestLuckyDrawFile',{'t':1}),self.calls)
   self.assertFalse(any(c[0]=='exchange' for c in self.calls))
  self.gg.avatar.summonCoin=0
  self.assertFalse(policy._HistoryAvatar(self.gg.avatar,state).luckyDrawData.canOpenFile(484))

 def test_normal_pool_new_group_all_open_positive(self):
  state=self.install();data=self.gg.avatar.luckyDrawData
  data.setIsFileOpen(1,False);self.gg.avatar.summonCoin=0
  view=policy._HistoryAvatar(self.gg.avatar,state)
  self.assertFalse(view.luckyDrawData.getIsOpenCard(1))
  self.assertTrue(view.luckyDrawData.canOpenFile(1))
  style=self.const.LuckyDrawConsumeStyle.STYLE_ONCE
  self.assertEqual(view.luckyDrawData.getLuckyDrawConsume(1,style),[(0,0)])
  self.assertEqual(view.luckyDrawData.getLuckyDrawConsume(1,self.const.LuckyDrawConsumeStyle.STYLE_FILE_ALL),[])
  self.assertFalse(view.luckyDrawData.canOpenCard(1))
  self.assertTrue(view.luckyDrawData.checkFileAndOpenAllCost(1))
  self.assertFalse(view.luckyDrawData.checkLeftAllCardsCost(1))
  self.calls=[];view.requestLuckyDrawFileAndOpenAll(1)
  self.assertIn(('rpc','requestLuckyDrawFileAndOpenAll',{'t':1}),self.calls)
  self.assertEqual(self.gg.avatar.summonCoin,0)

 def test_normal_pool_existing_group_rejects_all_open_but_allows_card(self):
  state=self.install();data=self.gg.avatar.luckyDrawData
  data.activity_data[1]=NS(card_times=6,cur_card_times_day=0,is_open_file=True,draw_info={i:dict(index=i,is_open=False) for i in range(6)});data.setIsFileOpen(1,True)
  self.gg.avatar.summonCoin=0
  view=policy._HistoryAvatar(self.gg.avatar,state)
  self.assertFalse(view.luckyDrawData.canOpenFile(1))
  self.assertTrue(view.luckyDrawData.canOpenCard(1))
  self.assertFalse(view.luckyDrawData.checkFileAndOpenAllCost(1))
  self.assertTrue(view.luckyDrawData.checkLeftAllCardsCost(1))
  self.calls=[];view.requestLuckyDrawFileAndOpenAll(1)
  self.assertFalse(any(c[0]=='rpc' and c[1]=='requestLuckyDrawFileAndOpenAll' for c in self.calls))
  self.calls=[];view.requestLuckyDrawCard(1)
  self.assertTrue(any(c[0]=='rpc' and c[1]=='requestLuckyDrawCard' and c[2].get('t')==1 and c[2].get('idx')==1 for c in self.calls))
  self.calls=[];view.requestLuckyDrawAllLeftCard(1)
  self.assertTrue(any(c[0]=='rpc' and c[1]=='requestLuckyDrawAllLeftCard' and c[2].get('t')==1 for c in self.calls))
  self.assertEqual(self.gg.avatar.summonCoin,0)

 def test_normal_pool_no_group_card_is_rejected(self):
  state=self.install();data=self.gg.avatar.luckyDrawData
  data.setIsFileOpen(1,False);self.gg.avatar.summonCoin=0
  view=policy._HistoryAvatar(self.gg.avatar,state)
  self.assertFalse(view.luckyDrawData.canOpenCard(1))
  self.calls=[];view.requestLuckyDrawCard(1)
  self.assertFalse(any(c[0]=='rpc' and c[1]=='requestLuckyDrawCard' for c in self.calls))

 def test_normal_pool_daily_cap_rejects_file_and_card(self):
  state=self.install();data=self.gg.avatar.luckyDrawData;data.setIsFileOpen(1,False);data.cur_card_times_day=300;self.gg.avatar.summonCoin=0
  view=policy._HistoryAvatar(self.gg.avatar,state)
  self.calls=[];view.requestLuckyDrawFile(1)
  self.assertFalse(any(c[0]=='rpc' and c[1]=='requestLuckyDrawFile' for c in self.calls))
  self.assertTrue(any(c[0]=='message' and c[1]==(415,) for c in self.calls))

 def test_normal_pool_button_action_uses_free_gate(self):
  state=self.install();self.gg.avatar.summonCoin=0
  p=self.panel();p.draw_type=1;p.btn_normal_open_once_discount=NS(isBright=lambda:True)
  p.on_open_click(None,2)
  self.assertEqual(self.gg.PanelJumpjumpcb,'_on_request_luckydrawfile')
  self.assertEqual(self.gg.PanelJumpjumpcbParams,(1,False))
  self.assertFalse(any(c[0]=='exchange' for c in self.calls))

 def test_orb_item_box_hidden_until_notify_true_and_phase_cleared(self):
  self.install();b=self.classes[1]();b.scene_type='normal';b.auto_scroll=True;b.item_box_panel=Widget();b.model_card_auto_scroll=lambda v:setattr(b,'auto_scroll',v)
  b.notify_open_file(False)
  self.assertFalse(b.item_box_panel.visible);self.assertFalse(b.auto_scroll);self.assertIsNotNone(getattr(b,'_q7_orb_phase',None))
  b.item_box_panel.setVisible(True);b.on_card_model_rotate(force_update=True);self.assertFalse(b.item_box_panel.visible)
  b.item_box_panel.setVisible(True);b.set_is_open_file(True);self.assertFalse(b.item_box_panel.visible)
  b.notify_open_file(True);self.assertTrue(b.auto_scroll);self.assertIsNone(getattr(b,'_q7_orb_phase',None))
  b.item_box_panel.setVisible(True);b.on_card_model_rotate(force_update=True);self.assertTrue(b.item_box_panel.visible)

 def test_orb_empty_state_repeat_true_other_pool_and_force_update(self):
  self.install();b=self.classes[1]();b.scene_type='normal';b.auto_scroll=True;b.item_box_panel=Widget();b.model_card_auto_scroll=lambda v:setattr(b,'auto_scroll',v);b.cur_state=''
  b.notify_open_file(False);b.item_box_panel.setVisible(True);b.on_card_model_rotate(force_update=True);self.assertFalse(b.item_box_panel.visible)
  b.notify_open_file(True);self.assertIsNone(getattr(b,'_q7_orb_phase',None));self.assertTrue(b.auto_scroll)
  b.item_box_panel.setVisible(True);b.on_card_model_rotate(force_update=True);self.assertTrue(b.item_box_panel.visible)
  b.notify_open_file(True);self.assertTrue(b.item_box_panel.visible)
  b.auto_scroll=False;b.notify_open_file(True);self.assertFalse(b.auto_scroll)

 def test_orb_all_three_card_phases_and_owner_mismatch(self):
  self.install();b=self.classes[1]();b.scene_type='normal';b.auto_scroll=True;b.item_box_panel=Widget();b.model_card_auto_scroll=lambda v:setattr(b,'auto_scroll',v)
  for phase in ('card_click','','card_click_end'):
   b.cur_state=phase;b.notify_open_file(False);self.assertFalse(b.item_box_panel.visible);self.assertIsNotNone(getattr(b,'_q7_orb_phase',None))
   b.item_box_panel.setVisible(True);b.on_card_model_rotate(force_update=False);self.assertFalse(b.item_box_panel.visible)
   b.item_box_panel.setVisible(True);b.set_is_open_file(True);self.assertFalse(b.item_box_panel.visible)
   b.notify_open_file(True);self.assertIsNone(getattr(b,'_q7_orb_phase',None));self.assertTrue(b.auto_scroll)
  b.notify_open_file(False);self.assertIsNotNone(getattr(b,'_q7_orb_phase',None));b.item_box_panel.setVisible(True)
  old_phase=getattr(b,'_q7_orb_phase',None);b.scene_type='normal';self.gg.avatar.luckyDrawData=NS(getIsOpenCard=lambda t:False)
  b.on_card_model_rotate(force_update=False);self.assertIsNone(getattr(b,'_q7_orb_phase',None));self.assertTrue(b.auto_scroll)
  b.scene_type='friend';b.notify_open_file(False);self.assertIsNone(getattr(b,'_q7_orb_phase',None))

 def test_orb_repeated_true_defers_setter_ui_refresh_until_notify_true(self):
  self.install();b=self.classes[1]();b.scene_type='normal';b.draw_type=1;b.auto_scroll=True;b.cur_state='card_click';b.is_open_file=True
  b.item_box_panel=Widget();b.model_card_panel=Widget();b.model_card_auto_scroll=lambda v:setattr(b,'auto_scroll',v)
  b.notify_open_file(False);b.model_card_panel.setVisible(False);self.calls=[];before_phase=getattr(b,'_q7_orb_phase',None)
  b.set_is_open_file(True)
  self.assertFalse(any(c[0]=='set_is_open_file' for c in self.calls));self.assertFalse(b.item_box_panel.visible);self.assertFalse(b.model_card_panel.visible);self.assertEqual(b.cur_state,'card_click');self.assertIs(getattr(b,'_q7_orb_phase',None),before_phase)
  b.notify_open_file(True);self.assertIsNone(getattr(b,'_q7_orb_phase',None));self.assertTrue(b.auto_scroll)
  b.set_is_open_file(True);self.assertTrue(b.model_card_panel.visible);self.assertEqual(b.cur_state,'file_open')

 def test_orb_notify_false_exception_restores_phase_and_scroll(self):
  self.install();b=self.classes[1]();b.scene_type='normal';b.auto_scroll=True;b.item_box_panel=Widget();b.model_card_auto_scroll=lambda v:setattr(b,'auto_scroll',v);b.raise_notify=True
  with self.assertRaises(RuntimeError):b.notify_open_file(False)
  self.assertIsNone(getattr(b,'_q7_orb_phase',None));self.assertTrue(b.auto_scroll)

 def test_orb_phase_clears_on_leave_and_reentry(self):
  self.install();b=self.classes[1]();b.scene_type='normal';b.auto_scroll=True;b.item_box_panel=Widget();b.model_card_auto_scroll=lambda v:setattr(b,'auto_scroll',v)
  b.notify_open_file(False);self.assertIsNotNone(getattr(b,'_q7_orb_phase',None));b.leave_scene();self.assertIsNone(getattr(b,'_q7_orb_phase',None));self.assertTrue(b.auto_scroll)
  b.notify_open_file(False);b.enter_scene(draw_type=1);self.assertIsNone(getattr(b,'_q7_orb_phase',None));self.assertTrue(b.auto_scroll)

 def test_original_tab_cost_widgets_show_free_without_coin_mutation(self):
  self.install();p=self.panel();p.draw_type=229
  for name in ('once_cost_1','all_cost_2','all_cost_1','panel_open2','btn_open_go','panel_open','btn_open_choose'):setattr(p,name,Widget())
  p.once_cost_1_cost_coin_comp=NS(_node=Widget());p.once_cost_1_cost_txt=Widget();p.once_cost_1_cost_txt.setString=lambda text:setattr(p.once_cost_1_cost_txt,'text',text)
  import types
  p.set_open_cost_coin=types.MethodType(original('card_tab','set_open_cost_coin',self.env),p)
  p.refresh_open_cost_coin_and_btn();self.assertTrue(p.once_cost_1.visible);self.assertFalse(p.once_cost_1_cost_coin_comp._node.visible);self.assertTrue(p.once_cost_1_cost_txt.visible);self.assertEqual(p.once_cost_1_cost_txt.text,'免费');self.assertEqual(self.gg.avatar.summonCoin,0)
 def test_normal_pool_tab_cost_widgets_show_free_without_coin_mutation(self):
  self.install();p=self.panel();p.draw_type=1;self.gg.avatar.giftCardData=NS(can_half_choose=lambda:False)
  for name in ('once_cost_1','all_cost_2','all_cost_1','panel_open2','btn_open_go','panel_open','btn_open_choose','btn_normal_open_once_discount','btn_normal_open_once_discount_open_file','btn_normal_open_once_discount_gry','btn_normal_open_once_time_reset','normal_once_daily_cost_1_free','normal_all_cost1','normal_all_cost2'):
   setattr(p,name,Widget())
  for name in ('once_cost_1_cost_coin_comp','normal_discount_once_daily_cost_1_comp','normal_once_daily_cost_1_comp','normal_all_cost1_comp','normal_all_cost2_1','normal_all_cost2_2'):setattr(p,name,Comp())
  p.once_cost_1_cost_txt=Widget();p.once_cost_1_cost_txt.setString=lambda text:setattr(p.once_cost_1_cost_txt,'text',text)
  type(p).__getitem__=lambda self,key:Widget()
  import types
  p.set_open_cost_coin=types.MethodType(original('card_tab','set_open_cost_coin',self.env),p)
  for coin in (0,1):
   self.gg.avatar.summonCoin=coin;p.refresh_open_cost_coin_and_btn()
   self.assertFalse(p.normal_once_daily_cost_1_comp._node.visible);self.assertTrue(p.normal_once_daily_cost_1_free.visible);self.assertEqual(self.gg.avatar.summonCoin,coin)

 def test_yingshe_treasure_pool_not_extended_by_normal_free_gate(self):
  state=self.install();self.gg.avatar.summonCoin=0;view=policy._HistoryAvatar(self.gg.avatar,state)
  self.assertNotIn(5,policy._LOCAL_FREE_TYPES);self.assertIn(5,state.ready)
  self.assertTrue(state.is_local_free(5));self.assertTrue(view.luckyDrawData.canOpenCard(5))

 def test_original_box_single_and_all_zero_inventory_requests(self):
  self.install();b=self.classes[1]();b.get_luckyDraw_type=lambda:229;b.is_cover=False;b.cur_state='activty_main_in_with_oupo';b.is_open_file=False;b.getHuodongPanel=lambda t:None;b.btn_quit=NS(setTouchEnabled=lambda flag:None);b.set_btn_quit_touch=lambda:None
  b.on_open_click(None,2);b.on_open_all_click(None,2)
  self.assertIn(('rpc','requestLuckyDrawFile',{'t':229}),self.calls);self.assertIn(('rpc','requestLuckyDrawFileAndOpenAll',{'t':229}),self.calls);self.assertEqual(self.gg.avatar.yuanbao,0)
 def test_captured_avatar_view_cannot_cross_real_avatar_generation(self):
  view=self.view();data=view.luckyDrawData;self.gg.avatar=NS(luckyDrawData=NS())
  with self.assertRaises(RuntimeError):view.requestLuckyDrawFile(229)
  with self.assertRaises(RuntimeError):data.canOpenFile(229)
  self.assertEqual(self.calls,[])
 def test_invalid_history_gift_panel_keeps_original_early_return(self):
  self.install();p=self.classes[0]();p.valid=False;p.draw_type=229;p.set_card_gift()
 def test_all_ready_rows_level_unlock_expired_time_and_default_normal(self):
  state=self.install();p=self.panel();self.gg.avatar.A248ChoukaFin=lambda:False
  p.init_button_comp(None);shown={t for t,s in p.draw_sort};self.assertTrue(set(state.selection())<=shown);self.assertEqual(self.calls[-1],('on_chouka_btn_click',(1,)))
  self.assertNotIn(354,shown);self.assertTrue(shown.isdisjoint(state.history-state.ready));self.assertTrue(any(self.original_rows[t]['show_level_lower_bound']>1 for t in state.ready))
 def test_free_zero_inventory_original_member_new_group_and_other_pools_unchanged(self):
  state=self.install();view=policy._HistoryAvatar(self.gg.avatar,state);self.assertFalse(self.gg.avatar.checkDrawInTime(229));self.assertTrue(view.checkDrawInTime(229))
  view.requestLuckyDrawFile(229);self.assertIn(('rpc','requestLuckyDrawFile',{'t':229}),self.calls)
  self.calls=[];view.requestLuckyDrawFile(1);self.assertIn(('rpc','requestLuckyDrawFile',{'t':1}),self.calls);self.assertFalse(any(c[0]=='exchange' for c in self.calls));self.assertTrue(view.luckyDrawData.canOpenFile(1));self.assertFalse(view.luckyDrawData.canOpenFile(484));self.assertEqual(self.gg.avatar.summonCoin,0)
  import time
  self.gg.avatar.guessServerTime=lambda:time.mktime((2035,9,15,7,0,0,0,0,0));self.calls=[];view.requestLuckyDrawFile(484);self.assertFalse(any(c[0]=='rpc' for c in self.calls));self.assertTrue(any(c[0]=='exchange' for c in self.calls))
 def test_real_tab_click_writes_global_deferred_and_new_facade_consumes(self):
  self.install();p=self.panel();p.draw_type=229;p.btn_normal_open_once_discount=NS(isBright=lambda:True)
  p.on_open_click(None,2);self.assertEqual(self.gg.PanelJumpjumpcb,'_on_request_luckydrawfile');self.assertEqual(self.gg.PanelJumpjumpcbParams,(229,False))
  b=self.classes[1]();b._do_init_card_info=lambda *a:None;b.enter_scene(draw_type=229)
  self.assertIn(('rpc','requestLuckyDrawFile',{'t':229,'nh':False}),self.calls);self.assertIsNone(self.gg.PanelJumpjumpcb)
 def test_pending_history_newgroup_callback_becomes_original_resume_no_reroll(self):
  self.gg.avatar.luckyDrawData.activity_data[229].is_open_file=True;self.install();b=self.classes[1]();b._do_init_card_info=lambda *a:None
  self.gg.PanelJumpjumpcb='_on_request_luckydrawallfile';self.gg.PanelJumpjumpcbParams=(229,);b.enter_scene(draw_type=229)
  self.assertIn(('rpc','requestFile',{'t':229}),self.calls);self.assertFalse(any(c[0]=='rpc' and c[1].startswith('requestLuckyDrawFile') for c in self.calls))
 def test_no_pending_can_request_file_remains_original_false(self):
  view=self.view();self.assertFalse(view.luckyDrawData.canRequestFile(229));view.requestFile(229);self.assertEqual(self.calls,[])
 def test_policy_change_and_forged_ids_rejected(self):
  self.install();self.assertIs(self.install(),getattr(self.classes[0],policy._MARKER))
  bad=json.loads(self.policy_text);bad['ready_ids']=[]
  with self.assertRaises(ValueError):policy.install(json.dumps(bad))
 def test_checked_csb_present_preserved_missing_only_falls_back(self):
  state=self.install();t=next(t for t in state.selection() if self.original_rows[t].get('room_enter_index') not in (None,0,7));source=dict(self.original_rows[t]);queries=[]
  with patch.dict(sys.modules,{'C_file':NS(find_res_file=lambda path,base:queries.append(path) or 'resolved')}):self.assertEqual(policy._HistoryRows(self.table.data,state).get(t)['room_enter_index'],source['room_enter_index'])
  with patch.dict(sys.modules,{'C_file':NS(find_res_file=lambda path,base:'')}):self.assertEqual(policy._HistoryRows(self.table.data,state).get(t)['room_enter_index'],7)
  self.assertEqual(self.original_rows[t],source);self.assertTrue(state.missing_panels)
 def test_scoped_alias_readonly_other_writes_reach_real_owners(self):
  state=self.install();a=policy._HistoryAvatar(self.gg.avatar,state);a.synthetic_probe=9;self.assertEqual(self.gg.avatar.synthetic_probe,9)
  g=policy._View(self.gg,avatar=a);g.PanelJumpjumpcb='value';self.assertEqual(self.gg.PanelJumpjumpcb,'value')
  with self.assertRaises(RuntimeError):g.avatar=None
 def test_gift_progress_hidden_balance_and_original_counts_preserved(self):
  state=self.install();p=self.panel();p.draw_type=229;p.open_card_gift=Widget();p.open_card_bell_icon=Widget();p.open_card_zhongguojie_icon=NS(_node=Widget());p.set_card_gift()
  self.assertFalse(p.open_card_gift.visible);self.assertEqual(self.gg.avatar.giftCoin,7);self.assertEqual(self.gg.avatar.luckyDrawData.getCardTimes(229),6)

 def capture_original_callbacks(self):
  callbacks=[]
  def send(avatar,method,params,**kwargs):
   self.calls.append(('rpc',method,dict(params)));callbacks.append(kwargs['callback'])
  type(self.gg.avatar).callServerMethodReliable=send;type(self.gg.avatar).callServerMethod=send
  return callbacks
 def test_old_original_rpc_callback_cannot_unlock_after_reset_epoch(self):
  callbacks=self.capture_original_callbacks();self.view().doRequestLuckyDrawFile(229);old_epoch=self.gg.ui._lock
  self.gg.ui.reset_lock();self.assertIsNot(self.gg.ui._lock,old_epoch)
  self.view().doRequestLuckyDrawFile(229);callbacks[0]();callbacks[0]()
  self.assertEqual(self.gg.ui._lock['requestLuckyDrawFile'],1);self.assertEqual(self.gg.ui.recon_lock,1)
  callbacks[1]();self.assertEqual(self.gg.ui._lock['requestLuckyDrawFile'],0);self.assertEqual(self.gg.ui.recon_lock,0)
 def test_original_callbacks_once_do_not_consume_sibling_acquires(self):
  callbacks=self.capture_original_callbacks();view=self.view();view.doRequestLuckyDrawFile(229);view.doRequestLuckyDrawFile(229)
  callbacks[0]();callbacks[0]();self.assertEqual(self.gg.ui._lock['requestLuckyDrawFile'],1);self.assertEqual(self.gg.ui.recon_lock,1)
  callbacks[1]();callbacks[1]();self.assertEqual(self.gg.ui._lock['requestLuckyDrawFile'],0);self.assertEqual(self.gg.ui.recon_lock,0)
 def test_same_ui_epoch_avatar_change_still_releases_original_acquire(self):
  callbacks=self.capture_original_callbacks();self.view().doRequestLuckyDrawFile(229);self.gg.avatar=NS(luckyDrawData=NS())
  callbacks[0]();callbacks[0]();self.assertEqual(self.gg.ui._lock['requestLuckyDrawFile'],0);self.assertEqual(self.gg.ui.recon_lock,0)
 def test_changed_ui_instance_callback_does_not_touch_new_ui(self):
  callbacks=self.capture_original_callbacks();self.view().doRequestLuckyDrawFile(229);old_ui=self.gg.ui
  self.gg.ui=NS(_lock={'requestLuckyDrawFile':1},recon_lock=1,unlock=lambda *a:self.fail('old callback touched new UI'))
  callbacks[0]();self.assertEqual(self.gg.ui.recon_lock,1);self.assertEqual(old_ui.recon_lock,1)
 def test_replaced_ui_retires_only_captured_old_wait_timers(self):
  callbacks=self.capture_original_callbacks();cancelled=[];visible=[]
  old_wait=self.gg.ui.panels.wait
  old_wait.show_desc_timer=101;old_wait.disconnect_timer=102;old_wait.valid=True
  old_wait._node=NS(setVisible=visible.append)
  self.gg.exec_cancel=cancelled.append
  self.view().doRequestLuckyDrawFile(229);old_ui=self.gg.ui
  self.gg.exec_cancel=lambda handle:self.fail('used replacement scheduler')
  self.gg.ui=NS(_lock={'requestLuckyDrawFile':1},recon_lock=1,unlock=lambda *a:self.fail('unlocked replacement UI'))
  callbacks[0]();callbacks[0]()
  self.assertEqual(cancelled,[101,102]);self.assertEqual(visible,[False])
  self.assertIsNone(old_wait.disconnect_timer);self.assertEqual(self.gg.ui.recon_lock,1)
  self.assertEqual(old_ui.recon_lock,1)
 def test_old_original_confirmation_cannot_send_or_lock_new_avatar(self):
  callbacks=self.capture_original_callbacks();confirms=[];self.gg.ui.panels.common_confirm_3.notify_confirm=lambda *a,**k:confirms.append(k['confirm_cb'])
  self.view().requestLuckyDrawFileAndOpenAll(229);self.assertEqual(len(confirms),1);self.assertEqual(callbacks,[])
  self.gg.avatar=NS(luckyDrawData=NS())
  with self.assertRaises(RuntimeError):confirms[0]()
  self.assertEqual(callbacks,[]);self.assertEqual(self.gg.ui._lock,{});self.assertEqual(self.gg.ui.recon_lock,0)
 def test_repeated_original_confirmation_callbacks_bind_separate_leases(self):
  callbacks=self.capture_original_callbacks();confirms=[];self.gg.ui.panels.common_confirm_3.notify_confirm=lambda *a,**k:confirms.append(k['confirm_cb'])
  self.view().requestLuckyDrawFileAndOpenAll(229);confirms[0]();confirms[0]();self.assertEqual(len(callbacks),2)
  callbacks[0]();callbacks[0]();self.assertEqual(self.gg.ui._lock['requestLuckyDrawFileAndOpenAll'],1);self.assertEqual(self.gg.ui.recon_lock,1)
  callbacks[1]();self.assertEqual(self.gg.ui.recon_lock,0)

 def test_all_original_scoped_request_keys_respect_reset_epoch(self):
  callbacks=self.capture_original_callbacks();view=self.view();data=self.gg.avatar.luckyDrawData.activity_data[229]
  for method,args,key,pending in [('doRequestLuckyDrawFile',(229,),'requestLuckyDrawFile',False),('doRequestLuckyDrawFileAndOpenAll',(229,),'requestLuckyDrawFileAndOpenAll',False),('requestLuckyDrawCard',(0,229),'requestLuckyDrawCard',True),('requestQuitFile',(229,),'quitFile',True),('requestLuckyDrawAllLeftCard',(229,),'requestLuckyDrawAllLeftCard',True)]:
   data.is_open_file=pending;before=len(callbacks);getattr(view,method)(*args);self.assertGreater(len(callbacks),before,method)
   self.gg.ui.reset_lock();self.gg.ui.lock(key)
   for callback in callbacks[before:]:callback();callback()
   self.assertEqual(self.gg.ui._lock[key],1,method);self.assertEqual(self.gg.ui.recon_lock,1,method);self.gg.ui.unlock(key)
 def test_real_clientavatar_rpc_registration_and_original_carrier_cleanup(self):
  self.gg.avatar_callback_map={};self.gg.avatar_callback_need_result={};ids=iter((71,72));self.env['utils']=NS(RotatedIdGenerator=NS(genid=lambda:next(ids)))
  self.env['sys']=sys;sent=[];self.gg.avatar.server=NS(call_server_method=lambda m,p,e:sent.append((m,dict(p))))
  type(self.gg.avatar).callServerMethod=original('ClientAvatar','callServerMethod',self.env)
  env={'gg':self.gg,'StandardError':Exception,'xrange':range,'CLIENT_STUB':3,'Avatar':type('Avatar',(),{}),'MailBox':type('MailBox',(),{}),'_logger':NS(warn=lambda *a:None,error=lambda *a:None)}
  for name in ('ConvertError','RpcMethodArg','Dict'):original_top('analysis/original-py-640/lib/common/RpcMethodArgs.py',name,env,'class')
  original_top('analysis/original-py-640/lib/common/rpcdecorator.py','RpcMethod',env,'class');decorate=original_top('analysis/original-py-640/lib/common/rpcdecorator.py','rpc_method',env)
  carrier=decorate(3,(env['Dict']('_r_'),))(original('ReliableRpcMember','serverCallbackCarrier',env));avatar=self.gg.avatar
  self.gg.avatar.luckyDrawData.activity_data[229].is_open_file=True;view=self.view();view.requestLuckyDrawCard(0,229);self.assertEqual(sent[-1][1]['_cbid_'],71)
  self.gg.ui.reset_lock();view.requestLuckyDrawCard(0,229);carrier(avatar,{'_r_':{},'_cbid_':71})
  self.assertEqual(self.gg.ui._lock['requestLuckyDrawCard'],1);self.assertEqual(self.gg.ui.recon_lock,1);self.assertNotIn(71,self.gg.avatar_callback_map)
  carrier(avatar,{'_r_':{'_result_':False},'_cbid_':72});self.assertEqual(self.gg.ui.recon_lock,0);self.assertEqual(self.gg.avatar_callback_map,{})

 def test_old_original_confirmation_reset_epoch_rejected_new_scope_works(self):
  callbacks=self.capture_original_callbacks();confirms=[];self.gg.ui.panels.common_confirm_3.notify_confirm=lambda *a,**k:confirms.append(k['confirm_cb'])
  self.view().requestLuckyDrawFileAndOpenAll(229);self.assertEqual(len(confirms),1);self.gg.ui.reset_lock()
  with self.assertRaises(RuntimeError):confirms[0]()
  self.assertEqual(callbacks,[]);self.assertEqual(self.gg.ui._lock,{});self.assertEqual(self.gg.ui.recon_lock,0)
  self.view().requestLuckyDrawFileAndOpenAll(229);confirms[1]();self.assertEqual(len(callbacks),1);self.assertEqual(self.gg.ui.recon_lock,1)
  callbacks[0]();self.assertEqual(self.gg.ui.recon_lock,0)

# Pool selection layer: empty by default, capped at 12, identity-scoped and
# corrupt-safe. Only _Installation.allowed/admission is narrowed; the ready cost
# guard is unchanged.
class PoolSelectionTests(unittest.TestCase):
 def setUp(self):
  import tempfile
  self.dir=tempfile.mkdtemp(prefix='draw-ui-pool-')
  self._old_game3d=sys.modules.get('game3d')
  game3d=types.ModuleType('game3d');game3d.get_doc_dir=lambda:self.dir
  sys.modules['game3d']=game3d
  self.pending=set()
  self.gg=types.ModuleType('gg')
  self.gg.avatar=NS(account='pool-a',luckyDrawData=NS(getIsOpenCard=lambda t:t in self.pending))
  self.patch=patch.dict(sys.modules,{'gg':self.gg});self.patch.start()
  policy._POOL_CACHE.clear()
 def tearDown(self):
  self.patch.stop()
  if self._old_game3d is None:sys.modules.pop('game3d',None)
  else:sys.modules['game3d']=self._old_game3d
  policy._POOL_CACHE.clear()
 def state(self,ready,history=None):
  ready=sorted(ready);history=sorted(set(ready if history is None else history))
  if history:history=sorted(set(history)|set(ready))
  return policy._Installation([],[],self.gg,{'ready_ids':ready,'all_history_ids':history})
 def path(self,session='account:pool-a'):
  return policy._pool_path(session)
 def write(self,payload,session='account:pool-a'):
  with open(self.path(session),'wb') as stream:
   stream.write(payload if isinstance(payload,bytes) else json.dumps(payload).encode('ascii'))
  policy._POOL_CACHE.clear()
 def test_default_empty_selection_hides_every_history_pool(self):
  state=self.state([2,3],[2,3])
  self.assertEqual(policy.pool_selection(),frozenset())
  self.assertFalse(any(state.allowed(t) for t in (2,3)))
  self.assertTrue(state.allowed(1),'the memory gap pool is always reachable')
  self.assertTrue(state.allowed(131),'the friend pool is always reachable')
  self.assertTrue(state.allowed(5),'the treasure draw is always reachable')
  self.assertFalse(state.allowed(119),'a limited wish gap stays hidden')
  rows=policy._HistoryRows({1:{'sort':1},2:{'sort':2},3:{'sort':3}},state)
  self.assertEqual(rows.keys(),[1]);self.assertIsNone(rows.get(2))
  self.assertEqual(state.is_local_free(2),True,'cost-free guard stays tied to ready')
 def test_limited_pools_outside_the_catalog_follow_the_selection(self):
  state=self.state([2],[2])
  self.assertFalse(state.allowed(106),'a treasure pool is hidden by default')
  rows=policy._HistoryRows({1:{'sort':1},106:{'sort':10}},state)
  self.assertEqual(rows.keys(),[1])
  self.assertTrue(policy.set_pool_selection([106]))
  self.assertTrue(state.allowed(106));self.assertTrue(state.allowed(1))
  rows=policy._HistoryRows({1:{'sort':1},106:{'sort':10}},state)
  self.assertEqual(sorted(rows.keys()),[1,106])
 def test_hideable_uses_the_draw_table(self):
  table=types.ModuleType('com.data.cdata.chouka_info')
  table.data={1:{},131:{},354:{},484:{},106:{}}
  cdata=types.ModuleType('com.data.cdata');cdata.chouka_info=table
  data_pkg=types.ModuleType('com.data');data_pkg.cdata=cdata
  root=types.ModuleType('com');root.data=data_pkg
  modules=patch.dict(sys.modules,{'com':root,'com.data':data_pkg,
                                  'com.data.cdata':cdata,'com.data.cdata.chouka_info':table})
  modules.start()
  try:
   ids=policy._Installation([],[],self.gg,{'ready_ids':[2],'all_history_ids':[2]}).hideable()
   self.assertEqual(sorted(ids),[2,106,484],
                    'baseline pools stay out of the editor list')
  finally:
   modules.stop()
 def test_selected_pool_visible_unselected_hidden(self):
  self.assertTrue(policy.set_pool_selection([2,4]))
  state=self.state([2,3,4],[2,3,4])
  self.assertTrue(state.allowed(2));self.assertTrue(state.allowed(4))
  self.assertFalse(state.allowed(3))
  rows=policy._HistoryRows({2:{'sort':2},3:{'sort':3},4:{'sort':4}},state)
  self.assertEqual(sorted(rows.keys()),[2,4])
 def test_pending_pool_visible_even_if_unselected(self):
  self.pending.add(3)
  state=self.state([2,3],[2,3])
  self.assertEqual(policy.pool_selection(),frozenset())
  self.assertTrue(state.allowed(3),'a started draw must stay reachable')
  self.assertFalse(state.allowed(2))
  rows=policy._HistoryRows({2:{'sort':2},3:{'sort':3}},state)
  self.assertEqual(rows.keys(),[3]);self.assertIsNotNone(rows.get(3))
 def test_cap_twelve_enforced_on_write_and_read(self):
  self.assertFalse(policy.set_pool_selection(list(range(1,14))))
  self.assertEqual(policy.pool_selection(),frozenset(),'over-cap write keeps the old selection')
  self.assertTrue(policy.set_pool_selection(list(range(1,13))))
  self.assertEqual(len(policy.pool_selection()),12)
  self.write({'v':1,'session':'account:pool-a','ids':list(range(1,14))})
  self.assertEqual(policy.pool_selection(),frozenset(),'over-cap file is ignored, never raised')
  state=self.state(range(1,14))
  self.assertFalse(state.allowed(1),'an ignored file admits nothing')
 def test_corrupt_or_foreign_selection_file_is_empty(self):
  for payload in (b'{broken',b'[]',
                  {'v':2,'session':'account:pool-a','ids':[2]},
                  {'v':1,'session':'account:pool-b','ids':[2]},
                  {'v':1,'session':'account:pool-a','ids':['2']},
                  {'v':1,'session':'account:pool-a','ids':[2,2]},
                  {'v':1,'session':'account:pool-a','ids':[2],'extra':1}):
   self.write(payload)
   self.assertEqual(policy.pool_selection(),frozenset(),payload)
   state=self.state([2]);self.assertFalse(state.allowed(2))
 def test_selection_is_per_identity(self):
  self.assertTrue(policy.set_pool_selection([2]))
  self.gg.avatar.account='pool-b'
  self.assertEqual(policy.pool_selection(),frozenset(),'another account reads its own (empty) file')
  self.assertFalse(self.state([2]).allowed(2))
  self.assertTrue(policy.set_pool_selection([3]))
  self.assertEqual(sorted(policy.pool_selection()),[3])
  self.gg.avatar.account='pool-a'
  self.assertEqual(sorted(policy.pool_selection()),[2])
  self.assertNotEqual(self.path('account:pool-a'),self.path('account:pool-b'))
  self.assertTrue(os.path.isfile(self.path('account:pool-a')))
  self.assertTrue(os.path.isfile(self.path('account:pool-b')))
 def test_identityless_account_never_writes_or_reads(self):
  self.gg.avatar.account=''
  self.assertFalse(policy.set_pool_selection([2]))
  self.assertEqual(policy.pool_selection(),frozenset())
  self.assertEqual(policy._pool_path(''),'')
  self.assertEqual(os.listdir(self.dir),[])
 def test_write_invalidates_cache_and_is_strict(self):
  self.assertTrue(policy.set_pool_selection([2,3]))
  self.assertEqual(sorted(policy.pool_selection()),[2,3])
  self.assertTrue(policy.set_pool_selection([5]))
  self.assertEqual(sorted(policy.pool_selection()),[5])
  self.assertFalse(policy.set_pool_selection([0]))
  self.assertFalse(policy.set_pool_selection([-1]))
  self.assertFalse(policy.set_pool_selection([True]))
  self.assertFalse(policy.set_pool_selection('2'))
  self.assertEqual(sorted(policy.pool_selection()),[5])
