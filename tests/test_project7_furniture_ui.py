"""Finite original panel/member/data bodies; widget/transport seams, no game runtime."""
import ast,base64,contextlib,hashlib,importlib.util,io,json,sys,textwrap,time,types,unittest
from pathlib import Path
from unittest.mock import patch
from lib2to3.refactor import RefactoringTool
from tools.project7_draw_history_ir.consumer import load
from tools.project7_draw_history_ir.codec import untyped
ROOT=Path(__file__).resolve().parents[1];NS=types.SimpleNamespace
spec=importlib.util.spec_from_file_location('furniture_ui',ROOT/'runtime/project7_furniture_ui.py');ui=importlib.util.module_from_spec(spec);spec.loader.exec_module(ui)
FIX=RefactoringTool(['lib2to3.fixes.fix_print','lib2to3.fixes.fix_except','lib2to3.fixes.fix_dict','lib2to3.fixes.fix_xrange'])
SOURCES={}
def original(path,name,env,top=False):
 p=ROOT/path;SOURCES[path]=hashlib.sha256(p.read_bytes()).hexdigest();lines=p.read_text().splitlines(True);prefix='' if top else '    '
 start=next(i for i,line in enumerate(lines) if line.startswith(prefix+'def '+name+'('));end=start+1
 while end<len(lines) and not (lines[end].startswith(prefix+'def ') or lines[end].startswith(prefix+'@') or (top and lines[end].startswith('class '))):end+=1
 source=textwrap.dedent(''.join(lines[start:end]))+'\n';tree=ast.parse(str(FIX.refactor_string(source,path)));exec(compile(tree,path+':'+name,'exec'),env);return env[name]
class Widget:
 def __init__(self,visible=True):self.visible=visible;self.calls=[];self.bright=True
 def isVisible(self):return self.visible
 def setVisible(self,v):self.visible=v
 def setBright(self,v):self.bright=v
 def setString(self,v):self.text=v
 def __getattr__(self,name):return lambda *a,**k:self.calls.append((name,a,k))
class Comp:
 def __init__(self):self._node=Widget();self.calls=[]
 def set_info(self,*a,**k):self.calls.append(('info',a,k))
 def set_icon(self,*a):self.calls.append(('icon',a))
 def set_not_stop_bg_music(self,v):pass
class Vec:
 def __init__(self,*a):self.args=a
 def add(self,v):pass

class FurnitureUiTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.ir=load();cls.info=untyped(cls.ir['tables']['chouka_info']);cls.delivery=untyped(cls.ir['tables']['furniture_delivery']);cls.normal=untyped(cls.ir['tables']['chouka_normal'])
  ids=sorted(p['wire_t'] for p in cls.ir['ui_pools'] if p['rpc_family']=='furniture' and p['wire_t']!=162)
  cls.policy={'schema':'project7-history-furniture-ui-v1','asset_sha256':ui._ASSET,'ready_ids':ids,'all_history_ids':ids}
  cls.text=json.dumps(cls.policy,sort_keys=True,separators=(',',':'))
 def setUp(self):
  redirect=contextlib.redirect_stdout(io.StringIO());redirect.__enter__();self.addCleanup(redirect.__exit__,None,None,None)
  self.events=[];self.locked=set();self.callbacks=[];self.gg=types.ModuleType('gg');self.gg.city=None
  self.gg.ui=NS(panels=NS(_panels={},settlement_window_summon=None,newbee_guidance=NS(is_begin=True),common_message=NS(notify_message=lambda code:self.events.append(('message',code)))),lock=lambda n:self.locked.add(n),unlock=lambda n:self.locked.remove(n))
  self.gg.audio_mgr=NS(ui_sound=lambda *a:None);self.gg.ui.actions=NS(city_room_danchi_new=NS(loop=NS(start=lambda:None),arrow=NS(start=lambda:None)))
  self.const=NS(CardPoolType=NS(TYPE_HERO_TREASURE=1,TYPE_FURNITURE=2),LuckyDrawType=NS(NORMAL=1,SHENGDAN=2,XINCHUN=3,STONE=4,TEST=-1),MAX_FURNITURE_TIMES_DAY=500,SUMMON_FURNITURE_LIANCHOU_TIMES=10,LuckyDrawConsumeStyle=NS(STYLE_FURNITURE_ONCE=1,STYLE_FURNITURE_TEN=2),FurnitureDrawingType=NS(TYPE_FIXED=1,TYPE_THREE=3,TYPE_COLLECTION=5))
  self.env={'gg':self.gg,'const':self.const,'time':time,'helpers':NS(getHuoDongIds=lambda:([],[]),get_active_uaid=lambda rotation:(None,None)),'cc':NS(ccui=NS(TOUCH_EVENT_ENDED=2),cc=NS(Color3B=lambda *a:a,Vec2=Vec)),'CHOUKA_INFO_DATA':NS(data=self.info),'FURNITURE_DELIVERY_DATA':NS(data=self.delivery),'CHOUKA_NORMAL_DATA':NS(data=self.normal)}
  self.gg.ui._lock={};self.gg.ui.recon_lock=0;self.gg.ui.panels.wait=NS(notify_show=lambda *a:self.events.append(('wait_show',)),notify_hide=lambda:self.events.append(('wait_hide',)),cancel_timer=lambda:self.events.append(('wait_cancel',)))
  for name in ('lock','unlock','reset_lock','is_lock'):
   setattr(self.gg.ui,name,types.MethodType(original('analysis/original-py-640/cocos/ui_manager.py',name,self.env),self.gg.ui))
  class Locked:
   def __contains__(inner,key):return self.gg.ui.is_lock(key)
   def __bool__(inner):return self.gg.ui.is_lock()
  self.locked=Locked()
  Data=type('OriginalFurnitureData',(),{})
  for name in ('getCurrActivedFurnitureCard','getCurCardTimesDay','setCurCardTimeDay','getFurnitureLianchouTimes','setFurnitureLianchouTimes','checkFurnitureCardCost','getFurnitureCardConsume'):
   setattr(Data,name,original('analysis/original-py-640/entity/avatar_attrs/LuckyDrawData.py',name,self.env))
  data=Data();data.activity_data={t:NS(cur_card_times_day=0,lianchou_times=0) for t in self.policy['ready_ids']+[162]};data.cur_card_times_day=0
  Avatar=type('OriginalFurnitureAvatar',(),{})
  for name in ('checkActivity','checkDrawInTime','requestLuckyDrawFurnitureCard','requestLuckyDrawFurnitureLianchouCard'):
   setattr(Avatar,name,original('analysis/original-py-640/entity/avatar_members/LuckyDrawMember.py',name,self.env))
  Avatar.findItemByID=lambda owner,*a,**k:(0,[]);Avatar.guessServerTime=lambda owner:1767225600
  def send(owner,method,params,callback=None,**kwargs):self.events.append(('rpc',method,dict(params)));self.callbacks.append(callback)
  Avatar.callServerMethod=send
  self.gg.avatar=Avatar();self.gg.avatar.luckyDrawData=data;self.gg.avatar.methodPoolBase={}
  self.module=types.ModuleType(ui._TARGET);Panel=type('OriginalFurniturePanel',(),{})
  path='analysis/original-py-640/cocos/panels/city_room_danchi_new.py'
  self.env['Panel']=Panel
  Panel.BOARD_PATH='cocos/image/activity/activity_121/';Panel.TEXTURE_PATH='cocos/image/city/city_room_danchi/'
  for name in ui._METHODS+('refresh','fixed_type','on_furniture_coin_buy'):
   fn=original(path,name,self.env);setattr(Panel,name,property(fn) if name=='fixed_type' else fn)
  self.module.Panel=Panel;self.Panel=Panel
  self.entry=types.ModuleType(ui._ENTRY);self.City=type('OriginalCityPanel',(),{});self.entry.Panel=self.City;self.entry.const=self.const;self.entry.cc=self.env['cc']
  self.const.MAX_DAYNUM=14;self.const.SCENE_CITY=10;self.const.SCENE_CITY_HOME=11
  entry_env=dict(self.env);entry_env['Panel']=self.City
  for name in ('on_back_home_click','do_city_danchi_click'):
   setattr(self.City,name,original('analysis/original-py-640/cocos/panels/city.py',name,entry_env))
  self.entry_env=entry_env
  self.City.visible_functional=original('analysis/original-py-640/cocos/panels/city.py','visible_functional',entry_env);self.gg.avatar.weeknumData=NS(weeknum=1,daynum=0,sandglass_working=False);self.gg.avatar.newbeeData=NS(init_zhuangxiu_stage=1);self.gg.avatar.letterData=NS(init_state=1)
  type(self.gg.avatar).getTotalCrystal=lambda actor:(0,False);type(self.gg.avatar).checkCrystalRemainLimit=lambda actor:True
  self.gg.scene_mgr=NS(active_scn_path=10);self.gg.city_container=NS(cur_scene_key=10,pop_and_push_scene=lambda key:self.events.append(('scene',key)))
  self.gg.ui.panels.common_confirm=NS(notify_confirm=lambda text,confirm_cb=None,**kwargs:setattr(self,'menu',(text,confirm_cb,kwargs)))
  self.entry_env.update(game3d=NS(PLATFORM_WIN32=0),STORY_DREAM_DATA=NS(data={}),CHANNEL_RUN_INFO=NS(data={}),CITY_DATA=NS(data={}))
  self.const.RotationType=NS(GUILD_BATTLE=84);self.gg.avatar.rotActMgrData={84:None};self.gg.avatar.storyData=NS(route='host',huisu_flag=False,flashback_flag=False)
  self.gg.avatar.smallActivityData=NS(monDailyCheckData=NS(checkCanNormalCheck=lambda gid:False));self.gg.avatar.rewardData=NS(wenziReward=False,recommend_giftbag=NS(getLeftTime=lambda:[0]))
  for name in ('isHuisuOrFlashback','needShowIcon','dailyCheckPosterAvailable','check_h5_open'):setattr(type(self.gg.avatar),name,lambda actor:False)
  type(self.gg.avatar).getCurrMonCheckGid=lambda actor:0;self.gg.platform=0;self.gg.config={'city_first_show':False};self.gg.channel_loginname='host'
  self.gg.ui.panels.bullet=NS(in_barrage=lambda panel:False,visible_barrage=lambda *a:None);self.gg.ui.panels.city_yanhua_main=NS(valid=False);self.gg.ui.panels.bbs_home=NS(visible_self_layer=lambda *a:None)
  self.gg.ui.actions.city=NS(open=NS(start=lambda:None),close=NS(start=lambda:None),day_shalou_loop=NS(start=lambda:None))
  self.gg.avatar.luckyDrawData.curr_furniture_pool=0
  self.mods={'gg':self.gg,ui._TARGET:self.module,ui._ENTRY:self.entry,'com.data.cdata.chouka_info':NS(data=self.info),'com.data.cdata.furniture_delivery':NS(data=self.delivery),'com.base.game_object':NS(members_cache={},method_cache={})}
  for name in ('com','com.data','com.data.cdata'):
   package=types.ModuleType(name);package.__path__=[];self.mods[name]=package
  self.mods['com'].data=self.mods['com.data'];self.mods['com.data'].cdata=self.mods['com.data.cdata'];self.mods['com.data.cdata'].furniture_delivery=self.mods['com.data.cdata.furniture_delivery']
  self.modules=patch.dict(sys.modules,self.mods);self.modules.start();self.addCleanup(self.modules.stop)
 def panel(self):
  p=self.Panel();p.curr_type=0;p.type_list=[];p.valid=True;p.show_anim=Widget();p.idle_anim=Widget()
  for name in ('fixed_draw','fixed_draw_sp','limit_draw','board','panel_title','info_1','info_2','btn_drawing','panel_tv','panel_tuzhi'):setattr(p,name,Widget())
  for name in ('left_arrow','right_arrow','title_pic','time_txt','light_list','btn_view_list','btn_shop','once_cost_free_txt','ten_cost_1','ten_cost_2','btn_once','btn_ten'):setattr(p,name,[Widget() for _ in range(3)])
  p.skin_imgs=[[Widget() for _ in range(n)] for n in (3,6,3)];p.skin_imgs_pos=[[(0,0)]*n for n in (3,6,3)];p.title_pic_pos=[(0,0)]*3
  p.furnitures_reward=[Widget(),Widget()];p.jiaju_comps3=[Comp() for _ in range(3)];p.dabi1_comp=Comp();p.dabi2_comp=Comp()
  p.once_cost_comp=[Comp() for _ in range(3)];p.ten_cost_1_comp=[Comp() for _ in range(3)];p.ten_cost_2_comps=[(Comp(),Comp()) for _ in range(3)];p.show_discount=[[Widget() for _ in range(3)] for _ in range(3)]
  return p
 def install(self):return ui.install(self.text)
 def view(self):return ui._Avatar(self.gg.avatar,self.state,self.gg.avatar)
 def test_all40_original_arrow_selector_and_buttons_send_exact_rpc(self):
  self.state=self.install();p=self.panel();p.init_data();seen=set()
  for index in range(40):
   seen.add(p.curr_type);p.on_btn_once_click(None,2);self.assertEqual(self.events[-1],('rpc','requestLuckyDrawFurnitureCard',{'t':p.curr_type}));self.callbacks.pop()()
   p.on_btn_ten_click(None,2);self.assertEqual(self.events[-1],('rpc','requestLuckyDrawFurnitureLianchouCard',{'t':p.curr_type}));self.callbacks.pop()()
   p.on_arrow_click(None,2,is_left=False)
  self.assertEqual(seen,set(self.policy['ready_ids']));self.assertFalse(self.locked);self.assertEqual(p.curr_type,p.type_list[0]);self.assertTrue(all(v.cur_card_times_day==0 for v in self.gg.avatar.luckyDrawData.activity_data.values()))
 def test_real_counts_owner_free_cost_and_legacy162_unchanged(self):
  self.state=self.install();v=self.view();t=384;source=self.gg.avatar.luckyDrawData
  self.assertEqual(v.luckyDrawData.getFurnitureCardConsume(t),[(11491,0)]);self.assertTrue(v.luckyDrawData.checkFurnitureCardCost(t));self.assertFalse(v.luckyDrawData.checkFurnitureCardCost(162));self.assertEqual(v.luckyDrawData.getFurnitureCardConsume(162),[(10225,10)])
  source.activity_data[t].cur_card_times_day=500;v.requestLuckyDrawFurnitureCard(t);self.assertFalse(any(e[0]=='rpc' for e in self.events));self.assertIn(('message',1314),self.events)
  source.activity_data[t].cur_card_times_day=490;v.requestLuckyDrawFurnitureLianchouCard(t);self.assertFalse(any(e[0]=='rpc' for e in self.events));self.assertIn(('message',1316),self.events)
  v.luckyDrawData.curr_furniture_pool=t;self.assertEqual(source.curr_furniture_pool,t)
  self.assertEqual(v.checkDrawInTime(162),self.gg.avatar.checkDrawInTime(162));self.assertFalse(v.checkActivity(t,pool_type=1));self.assertTrue(v.checkActivity(t,pool_type=2))
 def test_ui_restore_and_no_fake_promo_for_missing_delivery(self):
  self.state=self.install();p=self.panel();p.btn_shop[1].visible=False;p.board.visible=True
  p.init_data(106);p.refresh();self.assertFalse(p.board.visible);self.assertFalse(any(n.visible for n in p.skin_imgs[0]));self.assertIn('106',p.panel_title.text);self.assertEqual(p.fixed_type,0)
  self.assertEqual(self.info[106]['skin_infos'],p.info_1.text)
  p.curr_type=162;p.refresh();self.assertTrue(p.board.visible);self.assertFalse(p.btn_shop[1].visible);self.assertEqual(p.fixed_type,1)
 def test_real_destroy_write_through_and_generation_guards(self):
  self.state=self.install();p=self.panel();p.init_data(384);p.on_destroy();self.assertEqual(self.gg.avatar.luckyDrawData.curr_furniture_pool,384);self.assertIsNone(p.show_anim)
  stale=self.view();old=self.gg.avatar;self.gg.avatar=type(old)();self.gg.avatar.luckyDrawData=old.luckyDrawData
  with self.assertRaises(RuntimeError):stale.requestLuckyDrawFurnitureCard(384)
  self.gg.avatar=old;stale_data=stale.luckyDrawData;old.luckyDrawData=NS()
  with self.assertRaises(RuntimeError):stale_data.getCurCardTimesDay(384)
 def test_real_limitcall_state_on_original_avatar(self):
  env={'time':NS(time=lambda:100),'gg':self.gg};decor=original('analysis/original-py-640/cutils/chelpers.py','limitcall',env,top=True)
  cls=type(self.gg.avatar);cls.requestLuckyDrawFurnitureCard=decor(1.8,True)(cls.requestLuckyDrawFurnitureCard)
  self.state=self.install();v=self.view();v.requestLuckyDrawFurnitureCard(384);self.assertGreater(self.gg.avatar.methodPoolBase['requestLuckyDrawFurnitureCard'],100)
  count=len([e for e in self.events if e[0]=='rpc']);v.requestLuckyDrawFurnitureCard(384);self.assertEqual(len([e for e in self.events if e[0]=='rpc']),count)
 def test_policy_tamper_and_idempotence_and_binding_fail_closed(self):
  before=self.Panel.init_data
  with self.assertRaises(ValueError):ui.install(self.text.replace('384','385'))
  self.assertIs(self.Panel.init_data,before);self.state=self.install();self.assertIs(self.install(),self.state)
  self.Panel.on_arrow_click=lambda *a:None
  with self.assertRaises(RuntimeError):self.state.current()
 def test_real_multiclick_body_and_stale_callback_do_not_write_new_avatar(self):
  self.env['cc'].ccui.TOUCH_EVENT_BEGAN=0;self.env['cc'].ccui.TOUCH_EVENT_MOVED=1;self.env['cc'].ccui.TOUCH_EVENT_CANCELED=3
  decorate=original('analysis/original-py-640/cocos/ui_utils.py','checkMultiClick',self.env,top=True)
  self.Panel.on_btn_once_click=decorate(self.Panel.on_btn_once_click);self.gg.ui.panels.newbee_guidance.is_begin=False
  self.gg.ui.multi_click=0;self.gg.ui.cur_sender=None;self.gg.ui.cur_panel=None
  self.state=self.install();p=self.panel();p.init_data(384);sender=Widget();sender.isTouchEnabled=lambda:True
  p.on_btn_once_click(sender,0);p.on_btn_once_click(sender,2);self.assertEqual(self.events[-1],('rpc','requestLuckyDrawFurnitureCard',{'t':384}));self.assertEqual(self.gg.ui.multi_click,0)
  stale=self.callbacks.pop();old=self.gg.avatar;self.gg.avatar=type(old)();self.gg.avatar.luckyDrawData=old.luckyDrawData
  stale();self.assertFalse(self.locked)
 def test_scoped_alias_readonly_and_limit_flag_write_through(self):
  self.state=self.install();view=self.view();view._limitcall_furniture=123;self.assertEqual(self.gg.avatar._limitcall_furniture,123)
  self.assertEqual(view.luckyDrawData.getFurnitureCardConsume(_type=384),[(11491,0)])
  with self.assertRaises(RuntimeError):view.luckyDrawData=NS()
  with self.assertRaises(RuntimeError):view._source=NS()
 def test_actual_backend_reply_uses_original_rpc_schema_owner_and_callback(self):
  report=ROOT/'reports/project7-history-furniture-implementation.json'
  evidence=json.loads(report.read_text())['verification']['evidence']['furniture_original_engine_and_consumers']
  self.assertEqual(evidence['actual_manager_sha256'],'9afdd92cf2f2670e6d5769a629c6efbd047b9ac25355ea4b7e9c7456af90aeb9')
  stdout=evidence['logs']['actual-original-furniture']['stdout'];packet=next(base64.b64decode(line.split()[2]) for line in stdout.splitlines() if line.startswith('HISTORY_FURNITURE_FIXTURE skin_first '))
  oldspec=importlib.util.spec_from_file_location('furniture_bson_probe',ROOT/'runtime/android_draw_policy/host_tests/verify_original_consumers.py');probe=importlib.util.module_from_spec(oldspec);oldspec.loader.exec_module(probe);params=probe.bson(packet)
  wrapped=self.rpc_reply('replyLuckyDrawFurnitureCard')
  self.state=self.install();p=self.panel();p.init_data(params['i']['t']);owner=self.gg.avatar.luckyDrawData;owner_id=id(owner.activity_data);p.on_btn_once_click(None,2);self.assertIn('requestLuckyDrawFurnitureCard',self.locked)
  self.gg.avatar_callback_map[77]=self.callbacks.pop();params['_cbid_']=77
  with contextlib.redirect_stdout(io.StringIO()):wrapped(self.gg.avatar,params)
  self.assertFalse(self.locked);self.assertNotIn(77,self.gg.avatar_callback_map);self.assertEqual(owner.activity_data[params['i']['t']].cur_card_times_day,params['i']['ct']);self.assertEqual(id(owner.activity_data),owner_id)
  self.assertEqual([e[1][0] for e in self.events if e[0]=='event'],['furniture_reward']);self.assertEqual(params['i']['rwd']['skin'],[[3796,1]])
 def rpc_reply(self,name):
  self.env.update(CLIENT_STUB=3,_logger=NS(warn=lambda *a:None,error=lambda *a:None),StandardError=Exception,EntityManager=NS(getentity=lambda p:None));self.gg.avatar_callback_map={};self.gg.avatar_callback_need_result={}
  for path,names in [('analysis/original-py-640/lib/common/RpcMethodArgs.py',{'ConvertError','RpcMethodArg','NoLimit','NumeralLimit','Int','Bool','List','Dict','Avatar','MailBox'}),('analysis/original-py-640/lib/common/rpcdecorator.py',{'RpcMethod','rpc_method'})]:
   text=(ROOT/path).read_text();SOURCES[path]=hashlib.sha256(text.encode()).hexdigest();tree=ast.parse(str(FIX.refactor_string(text,path)));selected=[n for n in tree.body if isinstance(n,(ast.ClassDef,ast.FunctionDef)) and n.name in names];exec(compile(ast.Module(body=selected,type_ignores=[]),path,'exec'),self.env)
  path='analysis/original-py-640/entity/avatar_members/LuckyDrawMember.py';lines=(ROOT/path).read_text().splitlines();signature=next(lines[i-1].strip() for i,l in enumerate(lines) if l.startswith('    def '+name+'('));decorator=eval(compile(ast.parse(signature[1:],mode='eval'),path,'eval'),self.env)
  body=original(path,name,self.env);wrapped=decorator(body);self.const.SCENE_NEW_DANCHI_ROOM=44;self.gg.city_container.get_scene_by_key=lambda key:None;self.gg.city_container.get_current_scene=lambda:None;self.gg.ui._tree=NS(proc_event=lambda *a,**k:self.events.append(('event',a)))
  return wrapped
 def city(self,panel):
  city=self.City();city.valid=True;city.in_dialogue=False;city.visible_semaphore={};city.btn_home=Widget(False);city.visible_calls=[];city.left_bottom_icons=[NS(style=str(i),_node=Widget()) for i in range(6)]
  city.add_layer=lambda target:target;city.proc_event=lambda name,t,**kwargs:panel.init_data(t)
  city.init_update_area=True;city.visible=True;city.chat_main_show=False;city.pending_visible_func=[];city.comp_barrage=Comp();city.is_in_city=lambda:True
  for name in ('notify_story_custom','notify_check','notify_check_newbee','update_info_red','top_action','stop_top_action','check_visible_red_home','update_left_bottom_icon','refresh_action_reward','refresh_canteen','refresh_circus_caidan','update_whiteLove_info','play_power_anim','do_refresh_yanhua','notify_remind_enable','refresh_remind','visible_in_route','update_right_bottom_icon'):
   setattr(city,name,lambda *a,**k:None)
  for name in ('remind_panel','panel_top_left','city3d_areas','info_node','bbs_entrance','bbs_entrance_final','next_day','shalou_goodnight','btn_rushui','btn_huisu','btn_city','room_danchi','btn_room_shuzhi','info_entrance','spread','card_panel','panel_home','panel_home_hero_empty','panel_home_hero_exchange','panel_home_old','panel_home_new','panel_room','panel_time','power_nor','shalou_time'):setattr(city,name,Widget())
  self.gg.ui.panels.city_room_danchi_new=panel
  return city
 def test_original_home_navigation_reaches_all40_without_city_slot_or_week_mutation(self):
  self.state=self.install();p=self.panel();city=self.city(p);slots=[item.style for item in city.left_bottom_icons]
  self.assertIsNone(city.visible_functional(True));self.assertTrue(city.btn_home.visible);self.assertEqual(self.gg.avatar.weeknumData.weeknum,1)
  city.on_back_home_click(None,2);text,delivery,options=self.menu;self.assertIn('配送',options['confirm_label']);self.assertIn('居室',options['cancel_label'])
  delivery();self.assertEqual(set(p.type_list),set(self.policy['ready_ids']));p.on_btn_once_click(None,2);self.assertEqual(self.events[-1],('rpc','requestLuckyDrawFurnitureCard',{'t':p.curr_type}))
  self.assertEqual([item.style for item in city.left_bottom_icons],slots);self.assertEqual(self.gg.avatar.weeknumData.weeknum,1)
  self.gg.avatar.weeknumData.weeknum=3;city.on_back_home_click(None,2);self.menu[2]['cancel_cb']();self.assertIn(('scene',11),self.events)
 def test_navigation_visibility_and_deferred_generation_guards(self):
  self.state=self.install();p=self.panel();city=self.city(p);city.visible_semaphore={'dialogue':1};city.visible_functional(False);self.assertFalse(city.btn_home.visible)
  city.visible_semaphore={};city.in_dialogue=True;city.visible_functional(True);self.assertFalse(city.btn_home.visible)
  city.in_dialogue=False;city.on_back_home_click(None,2);callback=self.menu[1];old=self.gg.avatar;self.gg.avatar=type(old)();self.gg.avatar.luckyDrawData=old.luckyDrawData
  with self.assertRaises(RuntimeError):callback()
 def test_old_destroy_releases_only_its_resources_without_new_owner_write(self):
  self.state=self.install();p=self.panel();p.init_data(384);old=self.gg.avatar;old_data=old.luckyDrawData;old_data.curr_furniture_pool=108
  replacement=type(old)();replacement.luckyDrawData=NS(curr_furniture_pool=490);self.gg.avatar=replacement
  show,idle=p.show_anim,p.idle_anim;p.on_destroy();self.assertIsNone(p.show_anim);self.assertIsNone(p.idle_anim);self.assertEqual(old_data.curr_furniture_pool,108);self.assertEqual(replacement.luckyDrawData.curr_furniture_pool,490)
  self.assertEqual(sum(call[0]=='release' for call in show.calls),1);self.assertEqual(sum(call[0]=='release' for call in idle.calls),1)
  with self.assertRaises(RuntimeError):p.init_data(384)
 def test_original_ui_counter_cleanup_survives_avatar_change_and_is_once(self):
  self.state=self.install();p=self.panel();p.init_data(384);p.on_btn_once_click(None,2);old_callback=self.callbacks.pop();self.assertEqual(self.gg.ui._lock['requestLuckyDrawFurnitureCard'],1)
  old=self.gg.avatar;replacement=type(old)();replacement.luckyDrawData=old.luckyDrawData;replacement.methodPoolBase={};self.gg.avatar=replacement
  fresh=self.panel();fresh.init_data(384);fresh.on_btn_once_click(None,2);new_callback=self.callbacks.pop();self.assertEqual(self.gg.ui._lock['requestLuckyDrawFurnitureCard'],2)
  old_callback();self.assertEqual(self.gg.ui._lock['requestLuckyDrawFurnitureCard'],1);old_callback();self.assertEqual(self.gg.ui._lock['requestLuckyDrawFurnitureCard'],1);new_callback();self.assertFalse(self.locked);self.assertEqual(self.gg.ui.recon_lock,0)
 def test_original_reset_lock_prevents_old_callback_decrementing_new_request(self):
  self.state=self.install();p=self.panel();p.init_data(384);p.on_btn_once_click(None,2);old_callback=self.callbacks.pop();old_map=self.gg.ui._lock
  self.gg.ui.reset_lock();self.assertIsNot(self.gg.ui._lock,old_map);p.on_btn_once_click(None,2);new_callback=self.callbacks.pop()
  old_callback();self.assertEqual(self.gg.ui._lock['requestLuckyDrawFurnitureCard'],1);self.assertEqual(self.gg.ui.recon_lock,1);new_callback();self.assertFalse(self.locked)
 def test_original_false_rpc_after_avatar_change_cleans_only_its_counter(self):
  wrapped=self.rpc_reply('replyLuckyDrawFurnitureCard');self.state=self.install();p=self.panel();p.init_data(384);p.on_btn_once_click(None,2);self.gg.avatar_callback_map[77]=self.callbacks.pop()
  old=self.gg.avatar;replacement=type(old)();replacement.luckyDrawData=old.luckyDrawData;replacement.methodPoolBase={};self.gg.avatar=replacement
  fresh=self.panel();fresh.init_data(384);fresh.on_btn_once_click(None,2);next_callback=self.callbacks.pop()
  wrapped(replacement,{'rs':False,'i':{},'_cbid_':77});self.assertEqual(self.gg.ui._lock['requestLuckyDrawFurnitureCard'],1);self.assertNotIn(77,self.gg.avatar_callback_map);next_callback();self.assertFalse(self.locked)
 def test_request_exception_releases_the_original_claimed_lock(self):
  self.state=self.install();p=self.panel();p.init_data(384)
  def broken(actor,*a,**k):raise IOError('inert transport failure')
  type(self.gg.avatar).callServerMethod=broken
  with self.assertRaises(IOError):p.on_btn_once_click(None,2)
  self.assertFalse(self.locked);self.assertEqual(self.gg.ui.recon_lock,0)
 def test_reset_epoch_blocks_old_navigation_confirm_but_new_scope_works(self):
  self.state=self.install();p=self.panel();city=self.city(p);city.on_back_home_click(None,2);expired=self.menu[1];self.gg.ui.reset_lock()
  confirm_env={'gg':self.gg,'cc':self.env['cc']};self.env['cc'].ccui.TOUCH_EVENT_BEGAN=0;self.env['cc'].ccui.TOUCH_EVENT_CANCELED=3
  confirm=original('analysis/original-py-640/cocos/panels/common_confirm.py','on_confirm',confirm_env);do=original('analysis/original-py-640/cocos/panels/common_confirm.py','do_confirm',confirm_env);closed=[]
  dialog=NS(cb_confirm=expired,cb_ud=(),destroy=lambda:closed.append(True));dialog.do_confirm=lambda:do(dialog)
  with self.assertRaises(RuntimeError):confirm(dialog,None,2)
  self.assertEqual(closed,[True]);self.assertEqual(p.curr_type,0);city.on_back_home_click(None,2);self.menu[1]();self.assertIn(p.curr_type,self.policy['ready_ids'])
 def test_same_avatar_reset_expires_legacy_buy_confirm_without_buying(self):
  self.env['ITEM_DATA']=NS(data=untyped(self.ir['tables']['item_data']));store=self.delivery[162]['coin_store_id'];self.env['ITEM_STORE_DATA']=NS(data={store:{'diamond':100}})
  type(self.gg.avatar).buyCardMallItem=lambda actor,*a,**k:self.events.append(('buy',a))
  self.state=self.install();p=self.panel();p.init_data(384);p.curr_type=162;p.try_fast_buy(162);old=self.menu[1];self.gg.ui.reset_lock()
  with self.assertRaises(RuntimeError):old()
  self.assertFalse(any(e[0]=='buy' for e in self.events));p.try_fast_buy(162);self.menu[1]();self.assertTrue(any(e[0]=='buy' for e in self.events))
 def test_old_ui_cleanup_uses_original_wait_owner_not_replacement_ui(self):
  self.state=self.install();p=self.panel();p.init_data(384);p.on_btn_once_click(None,2);callback=self.callbacks.pop();old_ui=self.gg.ui;new_wait=[]
  new_ui=NS(_lock={},recon_lock=0,panels=NS(wait=NS(notify_show=lambda *a:new_wait.append('show'),notify_hide=lambda:new_wait.append('hide'),cancel_timer=lambda:new_wait.append('cancel'))))
  for name in ('lock','unlock','reset_lock','is_lock'):setattr(new_ui,name,types.MethodType(ui._raw(getattr(old_ui,name)),new_ui))
  self.gg.ui=new_ui;new_ui.lock('requestLuckyDrawFurnitureCard');new_wait[:]=[];callback()
  self.assertEqual(old_ui._lock['requestLuckyDrawFurnitureCard'],1);self.assertEqual(old_ui.recon_lock,1);self.assertEqual(new_ui._lock['requestLuckyDrawFurnitureCard'],1);self.assertEqual(new_ui.recon_lock,1);self.assertEqual(new_wait,[])
 def test_retired_wait_cancels_original_scheduler_and_never_destroys_new_wait(self):
  scheduled={};cancelled=[];new_cancel=[]
  def delay(ms,callback):key=len(scheduled)+1;scheduled[key]=callback;return key
  def cancel(key):cancelled.append(key);scheduled.pop(key,None)
  self.gg.exec_delay=delay;self.gg.exec_cancel=cancel;self.gg.ui.actions.wait=NS(round=NS(start=lambda:None))
  wait=NS(valid=True,_node=Widget(),show_desc_timer=None,disconnect_timer=None,build_highest=lambda:None,check_logout_to_login=lambda:False,destroy=lambda: self.fail('retired wait destroy must never run'))
  for name in ('notify_show','cancel_timer'):setattr(wait,name,types.MethodType(original('analysis/original-py-640/cocos/panels/wait.py',name,self.env),wait))
  self.gg.ui.panels.wait=wait;self.state=self.install();p=self.panel();p.init_data(384);p.on_btn_once_click(None,2);callback=self.callbacks.pop();self.assertEqual(len(scheduled),2)
  old_ui=self.gg.ui;new_ui=NS(_lock={'new':1},recon_lock=1,panels=NS(wait=NS()));self.gg.ui=new_ui;self.gg.exec_cancel=lambda key:new_cancel.append(key)
  callback();self.assertEqual(len(cancelled),2);self.assertEqual(scheduled,{});self.assertEqual(new_cancel,[]);self.assertFalse(wait._node.visible);self.assertIsNone(wait.show_desc_timer);self.assertIsNone(wait.disconnect_timer);self.assertEqual(new_ui._lock,{'new':1})
 def test_prebound_cache_rejected(self):
  self.gg.ui.panels._panels['city_room_danchi_new']=object()
  with self.assertRaises(RuntimeError):self.install()
if __name__=='__main__':unittest.main()
