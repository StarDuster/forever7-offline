"""Original whole page/comp/UP consumer bodies with strict original CSB paths.
Widget methods and animation execution are inert host seams, not native rendering.
"""
import _paths  # noqa: E402,F401
import copy,json,types,unittest
from tests import test_project7_wish_ui as readview
from tests.test_project7_wish_ui import ROOT,NS,original,wish
from tests.test_project7_wish_transport import original_class
from tests.test_project7_dynamic_ui import Widget as _Widget
class Widget(_Widget):
 def requestDoLayout(self):pass
class PageTests(unittest.TestCase):
 def setUp(self):
  readview.ReadViewTests.setUp(self);self.anim=[];self.timers=[];self.acks=[];self.changed=[]
  self.state.draw_owner=NS(panel_row=lambda row:row);self.state.history_avatar_type=lambda actor,owner:actor;self.state.allowed=lambda t:t in wish._IDS;self.state.resources=lambda *a,**k:None
  self.gg.city=None;self.gg.exec_delay=lambda ms,cb:self.timers.append(cb);self.gg.ui.cur_sender=None;self.gg.ui.cur_panel=None;self.gg.ui.multi_click=0;self.gg.ui.panels.newbee_guidance=NS(is_begin=False)
  self.actor.setWishGroupAnimPlayed=lambda t,info:self.acks.append((t,info));self.actor.yuanbao=10000
  class Action:
   def load(a):pass
   def stop(a):pass
   def start(a,callback=None):
    if callback:self.anim.append(callback)
   def play(a,*args):pass
   def initWithNode(a,node):return a
   def retain(a):pass
  self.cc=NS(ccui=NS(TOUCH_EVENT_BEGAN=0,TOUCH_EVENT_MOVED=1,TOUCH_EVENT_ENDED=2,TOUCH_EVENT_CANCELED=3),ccs=NS(ActionManagerEx=NS(getInstance=lambda:NS(getActionByName=lambda *a:Action()))),cc=NS(CallFunc=NS(create=lambda cb:cb)))
  self.gg.ui.actions=NS(card_yingzhuang=NS(**{n:Action()for n in ('activity_in','item_loop','pb_light','pb_loop','hero_loop','item_change')}))
  evidence=json.loads((ROOT/'reports/project7-wish-ui-resource-evidence.json').read_text());self.paths={r['virtual']:{w['path'].split('.',1)[1]for w in r['widgets']if '.'in w['path']}for r in evidence['members']}
  case=self
  class Base:
   def __getitem__(panel,key):
    if key not in panel.nodes:raise AssertionError('Missing original CSB node '+key)
    return panel.nodes[key]
   def build_layer(panel):return None
   def remove_comp(panel,c):pass
   def load_comp(panel,key,name,parent,node):
    cls=case.comps[name.rsplit('.',1)[1]];comp=cls();comp._node=Widget();prefix=name.split('.',1)[1]+'.';paths=case.paths['cocos/activity_common_10.csb'];comp.nodes={p[len(prefix):]:Widget()for p in paths if p.startswith(prefix)};comp.on_load();return comp
  self.base=Base
  compenv={'gg':self.gg,'cc':self.cc,'ui_comp':NS(UIComp=Base)};self.comps={}
  for name in ('a102_list_1','a102_list_2'):
   env=dict(compenv);self.comps[name]=original_class('cocos/comps/activity_common_10/'+name+'.py','Comp',env)
  from read_data_table import read
  env=dict(self.env);env.update(cc=self.cc,ui_panel=NS(UIPanel=Base),ITEM_DATA=NS(data={int(k):v for k,v in self.policy['items'].items()}),HeroDataMod=NS(data=read(ROOT/'analysis/original-py-640/com/data/cdata/hero.py')),ITEM_STORE_WISH_CHANGE=NS(data=self.state.fees),CHOUKA_WISH_TREASURE_CHOOSE=NS(data=self.state.choose),TreasureGenerateDataMod=NS(data={}),const=NS(WishType=NS(TYPE_TREASURE=1,TYPE_HERO=2),LuckyDrawType=NS(YINGSHE=5)))
  env['ui_utils']=NS(checkMultiClick=original('analysis/original-py-640/cocos/ui_utils.py','checkMultiClick',{'gg':self.gg,'cc':self.cc},top=True))
  self.Page=original_class('cocos/panels/card_yingzhuang.py','Panel',env);self.pageenv=env
  self.state.scope=types.MethodType(wish._Installation.scope,self.state);self.state.bind_callbacks=lambda *a:None
 def page(self,t):
  panel=self.Page();panel.nodes={p:Widget()for p in self.paths['cocos/card_yingzhuang.csb']};panel._node=Widget();panel.valid=True;panel.on_init();panel.on_load();panel.lucky_draw_type=t
  self.state.draw_type=lambda panel:panel.lucky_draw_type if hasattr(panel,'lucky_draw_type')else panel._type
  self.panel=panel;self.scope=wish._Scope(self.state,panel,panel,t);panel._q7_wish_scope=self.scope
  def method(name,*args,**kwargs):
   raw=wish._raw(getattr(self.Page,name));return wish._clone(raw,self.scope.aliases(wish._globals(raw)),self.gg)(panel,*args,**kwargs)
  panel.set_info=lambda:method('set_info');panel.set_scroll_view=lambda *a,**k:method('set_scroll_view',*a,**k)
  return panel,method
 def test_pool5_original_page_and_comp_source_probability_and_ctr(self):
  panel,call=self.page(5);call('set_info');call('set_scroll_view');self.assertEqual(panel.progress.percent,2);self.assertEqual(panel.added_comp[0].rate.text,'2.00%')
  self.actor.luckyDrawData.activity_data[5].choose_treasure=[2,1096,7];call('set_info');self.assertIn(self.state.items[1096]['name']if hasattr(self.state,'items')else self.policy['items'][1096]['name'],panel.treasure_name_text.text)
  self.assertEqual(self.actor.luckyDrawData.activity_data[5].choose_treasure,[2,1096,7])
 def test_all_five_original_group_lists_no_completed_target_probability(self):
  for t in (119,126,143,154,164):
   panel,call=self.page(t);ids=[k for k,r in self.state.wish.items()if r['drawType']==t];target=self.state.wish[ids[0]]['wish_target'];self.owned.add(target)
   info=call('set_scroll_view',True);self.assertNotIn(ids[0],info.get(self.state.wish[ids[0]]['gid'],[]));self.assertTrue(all(c.rate.text!='0.00%'or c.name.text for c in panel.added_comp));call('set_info');self.assertGreaterEqual(panel.progress.percent,0)
   self.owned.clear()
 def test_original_animation_ack_and_stale_action_and_timer_suppressed(self):
  panel,call=self.page(119);self.actor.luckyDrawData.activity_data[119].wish_info={20:{'c':0,'f':[19],'a':[]}};call('notify_show',119)
  self.assertEqual(self.acks,[]);self.anim[-1]();self.assertEqual(self.acks[0][0],119);self.assertEqual(self.acks[0][1][20],[19]);self.assertTrue(self.timers)
  old_timer=self.timers[-1];panel._q7_wish_scope=object();old_timer();self.assertTrue(panel.cover)
  before=len(self.acks);self.anim[-1]();self.assertEqual(len(self.acks),before)
 def test_original_paid_change_ui_fee_and_confirm_route_then_stale_confirm(self):
  self.actor.validSetChooseTreasure=types.MethodType(original('analysis/original-py-640/entity/avatar_members/LuckyDrawMember.py','validSetChooseTreasure',self.pageenv),self.actor)
  self.actor.getLuckyTreasureCache=lambda:{'synthetic':NS(itemid=1096,uuid='synthetic')}
  self.gg.ui.panels.activity_102_window=NS();channel=object();self.state.member_owner=NS(transport=lambda actor:channel,choose=lambda scope,t,item:self.changed.append((t,item)),check=lambda:True)
  panel,call=self.page(5);captured=[];panel.add_layer=lambda layer:layer;panel.proc_event=lambda *a,**kwargs:captured.append(kwargs)
  for cnt,price in ((0,100),(1,200),(2,300),(3,300),(4,500),(7,500)):
   self.actor.luckyDrawData.activity_data[5].choose_treasure=[1,0,cnt]
   call('on_btn_change_click',panel.btn_change,0);call('on_btn_change_click',panel.btn_change,2);self.assertEqual(captured[-1]['yuanbao'],price)
  confirm=captured[-1]['clickConfirm'];self.assertTrue(confirm([NS(itemid=1096)]));call('confirm_select_treasure_list',[NS(itemid=1096)]);self.assertEqual(self.changed,[(5,1096)])
  self.gg.ui._lock={}
  with self.assertRaises(RuntimeError):confirm([NS(itemid=1096)])
  self.assertEqual(self.changed,[(5,1096)])
 def test_real_retained_touch_stale_end_releases_only_own_reference(self):
  panel,call=self.page(5);self.state.classes=(self.Page,type('Jz',(),{}),type('Box',(),{}));self.state.originals={(0,n):wish._raw(getattr(self.Page,n))for n in wish._METHODS[0]}
  wish._Installation.bind_callbacks(self.state,panel,self.scope);node=panel.btn_change;node.callback(node,0);held=node.callback;self.assertEqual(node.references,1)
  self.gg.avatar=NS(luckyDrawData=NS());
  with self.assertRaises(RuntimeError):held(node,2)
  self.assertEqual(node.references,0);self.assertEqual(self.gg.ui.multi_click,0);self.assertIsNone(self.gg.ui.cur_sender)
 def test_all_four_original_old_jz_pages_render_real_zero_count_wish(self):
  env=dict(self.pageenv);self.state.jiaozhi={(p['id'],r['id']):r for p in self.policy['pools']for r in p['jiaozhi']};env['CHOUKA_JIAOZHI_DATA']=NS(data={});env['CHOUKA_INFO_DATA']=NS(data=self.state.infos)
  env['ui_utils']=NS(**env['ui_utils'].__dict__);env['ui_utils'].setRTDesc=lambda node,text,**kwargs:node.setString(text);env['ui_utils'].GridScrollView=lambda *a,**kwargs:NS(on_update=lambda elapsed:None)
  self.gg.ui.actions.card_jiaozhi=NS(activity_in=NS(load=lambda:None,start=lambda:None),item_loop=NS(load=lambda:None));self.gg.ui.shaders=NS(image=lambda name:NS(instance=lambda **kwargs:NS(shader=None,destroy=lambda:None)))
  Jz=original_class('cocos/panels/card_jiaozhi.py','Panel',env);self.state.draw_type=lambda p:p._type
  for t in (126,143,154,164):
   panel=Jz();panel.nodes={p:Widget()for p in self.paths['cocos/card_jiaozhi.csb']};panel._node=Widget();panel.valid=True;panel.on_init();panel.on_load();panel._type=t
   scope=wish._Scope(self.state,panel,panel,t);panel._q7_wish_scope=scope
   def call(name,*args):
    raw=wish._raw(getattr(Jz,name));return wish._clone(raw,scope.aliases(wish._globals(raw)),self.gg)(panel,*args)
   panel.set_info=lambda:call('set_info');panel.set_qiyuan=lambda:call('set_qiyuan');call('notify_show',t)
   self.assertEqual(panel.tab,1);self.assertTrue(panel.progress2.visible);self.assertTrue(panel.list_comps);self.assertEqual(self.actor.luckyDrawData.activity_data[t].jiaozhi_count,{})
 def test_original_box_wish_button_all_six_routes_with_retained_dispatch(self):
  Base=self.base
  class Box(Base):
   def get_luckyDraw_type(panel):return panel._type
  class Tips:pass
  class Activity:pass
  self.state.classes=(self.Page,type('Jz',(),{}),Box);self.state.detail_classes=(Box,Tips,Activity);self.state.jiaozhi={(p['id'],r['id']):r for p in self.policy['pools']for r in p['jiaozhi']}
  self.gg.audio_mgr=NS(ui_sound=lambda *args:None);self.gg.ui.panels.card_jiaozhi=NS(name='old-jz');self.gg.ui.panels.card_yingzhuang=NS(name='wish');self.gg.ui.panels.card_jiaozhi_2=NS(name='charge-jz')
  env=dict(self.pageenv);env['CHOUKA_JIAOZHI_DATA']=NS(data={});raw=original('analysis/original-py-640/cocos/panels/card_box.py','on_yingzhuang_wish_click',env)
  self.state.families_owner=NS(detail_original=lambda index,name:raw);self.state.draw_type=lambda panel:panel._type
  for t in (5,119,126,143,154,164):
   panel=Box();panel._type=t;panel._node=Widget();panel.valid=True;panel.event_handlers={};panel.yingzhuang_wish_tips=Widget();panel.update_wish_banner=lambda **k:None;panel.update_wish_left_info=lambda:None;panel.check_has_leichong=lambda:False;panel.add_layer=lambda layer:layer;calls=[];panel.proc_event=lambda *args,**kwargs:calls.append((args,kwargs))
   scope=wish._Scope(self.state,panel,panel,t);panel._q7_wish_scope=scope;wish._Installation.bind_callbacks(self.state,panel,scope);widget=panel.yingzhuang_wish_tips
   widget.callback(widget,0);widget.callback(widget,2);self.assertEqual(len(calls),1);self.assertEqual(calls[0][0],('show',t));self.assertEqual(calls[0][1]['_layer'].name,'old-jz'if t in(126,143,154,164)else'wish')
 def test_all_three_original_up_banner_projects_same_count(self):
  paths=self.paths['cocos/card_box.csb'];Base=self.base
  class Box(Base):
   HERO_DIALOGUE_PATH='cocos/image/hero/hero_dialogue/%s.png'
   def get_luckyDraw_type(panel):return panel._type
  env={'gg':self.gg,'Panel':Box,'CHOUKA_INFO_DATA':NS(data=self.state.infos),'CHOUKA_JIAOZHI_DATA':NS(data={})}
  raw=original('analysis/original-py-640/cocos/panels/card_box.py','update_sp_banner',env);self.state.originals={(2,'update_sp_banner'):raw};self.state.draw_type=lambda panel:panel._type
  for t in (397,426,445):
   self.state.infos[t]=dict(self.state.infos[t],yijieti=True,up_tips='UP');panel=Box();panel._type=t;panel.cur_state='activty_card_click';panel.valid=True;panel._node=Widget();panel.nodes={p:Widget()for p in paths}
   self.actor.luckyDrawData.inc_up_cnt[1]=106;wish._Installation.invoke(self.state,2,'update_sp_banner',panel,(),{})
   self.assertEqual(panel['main.top.sp_jindu.chongneng_num_1'].text,'75');self.assertEqual(panel['main.top.sp_jindu.gailv_up.num_1'].text,'1%');self.assertEqual(panel['main.top.sp_jindu.gailv_up.num_2'].text,'+1%')
if __name__=='__main__':unittest.main()
