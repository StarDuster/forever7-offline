"""Candidate family projection and original finite consumers, no native rendering."""
import _paths  # noqa: E402,F401
import hashlib,json,types,unittest
from pathlib import Path
from unittest.mock import patch
from project7_dynamic_ui_family_policy import ui_policy,canonical
from tests import test_project7_dynamic_ui as old
ROOT=Path(__file__).resolve().parents[1]
families=old.module('dynamic_families_candidate','offline/current/runtime/project7_dynamic_ui_families.py')
class FamilyPolicyTests(unittest.TestCase):
 def test_complete46_projection_is_not_admission(self):
  x=ui_policy();self.assertEqual(len(x['pools']),46);self.assertEqual(x['candidate_ids'],x['backend_scope']);self.assertEqual(x['detail_ids'],x['candidate_ids']);self.assertEqual(x['verified_ids'],x['candidate_ids']);self.assertEqual(x['public_ready_ids'],[])
  from collections import Counter
  self.assertEqual(Counter(p['family'] for p in x['pools']),dict(legacy_plain=2,charge_only=11,base_repaired=7,jz_charge_four=23,jz_charge_six=1,ticket_only=2))
  p=next(p for p in x['pools'] if p['id']==283);self.assertEqual(len(p['charge']),6);self.assertEqual(max(r['times'] for r in p['charge']),220)
 def test_policy_pin_duplicate_and_tamper(self):
  x=ui_policy();families._policy(canonical(x));x['detail_ids']=[2]
  with self.assertRaises(ValueError):families._policy(canonical(x))
  with self.assertRaises(ValueError):families._policy('{"schema":1,"schema":2}')
 def test_display_bundle_complete_tamper_and_reproducible(self):
  import tempfile
  from project7_dynamic_ui_family_policy import maintainer_display,DISPLAY_SHA
  with tempfile.TemporaryDirectory() as temp:
   p=Path(temp)/'display.gz';meta=maintainer_display(ROOT/'analysis/android640-scripts/com/data/cdata',p)
   self.assertEqual((meta['common'],meta['items']),(238,120));self.assertEqual(hashlib.sha256(p.read_bytes()).hexdigest(),DISPLAY_SHA)
   with self.assertRaises(FileExistsError):maintainer_display(ROOT/'analysis/android640-scripts/com/data/cdata',p)
   p.write_bytes(p.read_bytes()[:-1]+b'x')
   with self.assertRaises(ValueError):ui_policy(display_path=p)
 def test_export_root_consumer_has_no_analysis_dependency(self):
  import tempfile,shutil
  with tempfile.TemporaryDirectory() as temp:
   runtime=Path(temp)/'runtime';directory=runtime/'project7_dynamic_catalog';shutil.copytree(ROOT/'offline/current/data/project7_dynamic_catalog',directory)
   shutil.copy2(ROOT/'offline/current/runtime/project7_dynamic_ui_families_data.json.gz',runtime/'project7_dynamic_ui_families_data.json.gz');shutil.copy2(ROOT/'offline/current/runtime/project7_dynamic_ui_families_entry_assets.json.gz',runtime/'project7_dynamic_ui_families_entry_assets.json.gz')
   self.assertEqual(ui_policy(directory),ui_policy())
   (runtime/'project7_dynamic_ui_families_data.json.gz').unlink()
   with self.assertRaises(FileNotFoundError):ui_policy(directory)
 def test_fixed_entry_producer_and_python2_runtime_grammar(self):
  import tempfile
  from project7_dynamic_ui_family_policy import maintainer_entry_assets,ENTRY_SHA
  with tempfile.TemporaryDirectory() as temp:
   path=Path(temp)/'entry.gz';meta=maintainer_entry_assets(ROOT/'analysis/deployment/android/Documents/res/cocos.npk',ROOT/'analysis/android640-scripts/com/data/cdata',path)
   self.assertEqual(meta['ui_comp'],80);self.assertEqual(meta['assets'],137);self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(),ENTRY_SHA)
   with self.assertRaises(FileExistsError):maintainer_entry_assets(Path(temp)/'not-input',Path(temp),path)
  old.slot.FIX.refactor_string((ROOT/'offline/current/runtime/project7_dynamic_ui_families.py').read_text('ascii'),'family-runtime')
 def test_fixed_raw_rows_lossless(self):
  from project7_dynamic_catalog import load
  from project7_draw_history_ir.codec import untyped
  data={p['pool']:p for p in load()['pools']}
  for p in ui_policy()['pools']:
   self.assertEqual(p['info'],untyped(data[p['id']]['raw']));self.assertEqual(p['charge'],[untyped(r['raw']) for r in data[p['id']]['charge']]);self.assertEqual(p['jiaozhi'],[untyped(r['raw']) for r in data[p['id']]['jiaozhi']]);self.assertEqual(p['cost_policy'],'history-free-v1')
class FamilyConsumerTests(unittest.TestCase):
 begin=old.DynamicUiTests.begin;retired=old.DynamicUiTests.retired;click=old.DynamicUiTests.click
 actor=old.DynamicUiTests.actor;grid=old.DynamicUiTests.grid;comp=old.DynamicUiTests.comp;panel=old.DynamicUiTests.panel;box=old.DynamicUiTests.box
 def setUp(self):
  x=ui_policy();pilot=next(p for p in x['pools'] if p['id']==485);x['info']=pilot['info'];x['charge']=pilot['charge'];x['jiaozhi']=pilot['jiaozhi'];x['detail_ids']=x['candidate_ids'] # explicit HOST-ONLY gate fixture, never production policy
  self.patchers=[patch.object(old,'ui',families),patch.object(old,'policy',lambda:x),patch.object(families,'_POLICY_RAW_SHA',hashlib.sha256(canonical(x)).hexdigest())]
  for p in self.patchers:p.start();self.addCleanup(p.stop)
  old.DynamicUiTests.setUp(self)
  self.gg.avatar.luckyDrawData.activity_data.update({p['id']:old.NS(card_times=0,is_open_file=True,jiaozhi_count={},jiaozhi_rewards={},replace_count={}) for p in x['pools']})
  from project7_dynamic_catalog import load
  from project7_draw_history_ir.codec import untyped
  from read_data_table import read
  data=load();self.env['ITEM_DATA'].data.update(untyped(data['items']));self.env['RewardCommonDataMod'].data.update(untyped(data['common']));self.env['HeroDataMod'].data.update(read(ROOT/'analysis/original-py-640/com/data/cdata/hero.py'))
  self.gg.ui.actions.card_leichong.activity_in=old.Action()
  # Each real module has its own Panel global. The source-function fixture
  # shares a namespace, so explicitly restore that exact per-module binding.
  cls=self.dynamic.classes[5];cls.IMG_SHADER=None;cls.IMG_PATH='cocos/image/hero/skill_dazhao/%d.png';cls.IMG_MASK='cocos/image/bbs/activity_39_mask_dispatch.png';cls.FULLNAME='[%s]';cls.NAME='[%s]'
  for name in families._METHODS[5]:
   fn=self.dynamic.originals[5,name];ns=dict(fn.__globals__);ns['Panel']=cls;self.dynamic.originals[5,name]=types.FunctionType(fn.__code__,ns,fn.__name__,fn.__defaults__,fn.__closure__)
  cls=self.dynamic.classes[6]
  for name in families._METHODS[6]:
   fn=self.dynamic.originals[6,name];ns=dict(fn.__globals__);ns['Panel']=cls;self.dynamic.originals[6,name]=types.FunctionType(fn.__code__,ns,fn.__name__,fn.__defaults__,fn.__closure__)
 def test_activity_base_fixed_tables_and_delayed_hide_generation(self):
  cls=self.dynamic.classes[6];cls.PANEL_TYPE_DYNAMIC=1;cls.PANEL_TYPE_STATIC=2;panel=cls();panel.valid=True;panel._node=old.Widget();panel.on_init();panel.cur_drawtype=283;panel.panel_type=1;panel.anim={'end':[]};panel.destroy=lambda:self.events.append(('destroy-activity',))
  self.gg.ui.panels.card_activity_base=panel;scope=self.dynamic.scope(panel)
  tables=scope.aliases({'CHOUKA_INFO_DATA':self.env['CHOUKA_INFO_DATA'],'UI_COMP_DATA':old.NS(data={})})
  self.assertEqual(tables['CHOUKA_INFO_DATA'].data[283]['drawType'],283);self.assertEqual(len(tables['UI_COMP_DATA'].data.keys()),80)
  panel.notify_hide();held=self.timers[-1];self.gg.avatar=self.actor()
  with self.assertRaises(RuntimeError):held()
  self.assertNotIn(('destroy-activity',),self.events)
 def test_all46_scoped_info_rows_and_jz_time(self):
  for p in self.ui_policy['pools']:
   box=self.box();box.draw_type=p['id'];scope=self.dynamic.scope(box);a=families._Avatar(scope)
   self.assertEqual(a.getChoukaInfoDataByType(p['id'])['drawType'],p['id']);self.assertEqual(scope.t,p['id'])
   for row in p['jiaozhi']:self.assertTrue(a.checkJiaozhiInTime((p['id'],row['id'])))
 def test_explicit_pre_request_guard_exact_owner_and_missing_resource(self):
  self.assertTrue(self.dynamic.before_request(283,self.gg.avatar));self.assertFalse(self.dynamic.before_request(1,self.gg.avatar))
  with self.assertRaises(RuntimeError):self.dynamic.before_request(283,object())
  with patch.dict(old.sys.modules,{'C_file':old.NS(find_res_file=lambda *a:False)}):
   with self.assertRaises(RuntimeError):self.dynamic.before_request(283,self.gg.avatar)
 def test_all46_same_authorized_free_ui_shape(self):
  data=self.gg.avatar.luckyDrawData;data.getLuckyDrawConsume=types.MethodType(old.original('analysis/original-py-640/entity/avatar_attrs/LuckyDrawData.py','getLuckyDrawConsume',self.env),data);data.getOpenConsume=types.MethodType(old.original('analysis/original-py-640/entity/avatar_attrs/LuckyDrawData.py','getOpenConsume',self.env),data)
  self.dynamic.draw_owner.ready=frozenset(self.ui_policy['candidate_ids']) # trusted published-policy host fixture only
  for t in self.ui_policy['candidate_ids']:
   box=self.box();box.draw_type=t;view=families._Avatar(self.dynamic.scope(box)).luckyDrawData
   self.assertEqual(view.getLuckyDrawConsume(t),[(0,0)]);self.assertEqual(view.getOpenConsume(t),0)
 def test_exact_wish_delegate_is_single_dispatch_and_no_current_cycle(self):
  state=self.dynamic
  class Delegate:
   def __init__(obj):obj.families_owner=state;obj.draw_owner=state.draw_owner;obj.detail_indices=(0,2,6);obj.detail_classes=(state.classes[0],state.classes[2],state.classes[6]);obj.detail_ids=(5,);obj.policy={'schema':'host-protocol-fixture','ids':[5]};obj.policy_sha256=hashlib.sha256(canonical(obj.policy)).hexdigest();obj.calls=[]
   def invoke_detail(obj,index,name,original,instance,args,kwargs):
    obj.families_owner.current();obj.calls.append((index,name,args,kwargs));return 'delegated'
  owner=Delegate();state.register_detail_delegate(owner,(5,),owner.invoke_detail);self.assertEqual(owner.calls,[]);self.assertIs(state.register_detail_delegate(owner,(5,),owner.invoke_detail),owner)
  tips=state.classes[2]();tips._type=5;token=object();tips._q7_dynamic_scope=token
  self.assertEqual(tips.set_info(_type=5),'delegated');self.assertIs(tips._q7_dynamic_scope,token);self.assertEqual(owner.calls[-1][3],{'_type':5})
  self.assertEqual(tips.canShowWishPanel(3),'delegated');self.assertEqual(owner.calls[-1][2],(3,));self.assertEqual(len(owner.calls),2)
  activity=state.classes[6]();activity.cur_drawtype=5;activity._q7_dynamic_scope=token;self.assertEqual(activity.refresh_tips(),'delegated');self.assertEqual(owner.calls[-1][:2],(6,'refresh_tips'));self.assertIs(activity._q7_dynamic_scope,token)
  self.assertIs(state.detail_original(2,'on_tips_click'),state.originals[2,'on_tips_click'])
  with self.assertRaises(RuntimeError):state.detail_original(2,'set_info')
  # Unmatched other pools execute the exact original body and never delegate.
  plain=state.classes[6]();plain.cur_drawtype=1;plain.yingzhuang_tips=old.Widget();before=len(owner.calls);plain.refresh_tips();self.assertFalse(plain.yingzhuang_tips.visible);self.assertEqual(len(owner.calls),before)
  with self.assertRaises(RuntimeError):state.register_detail_delegate(Delegate(),(5,),Delegate().invoke_detail)
  held=tips.on_tips_click;self.assertEqual(held(None,2),'delegated');count=len(owner.calls)
  owner.policy['ids']=[119]
  with self.assertRaises(RuntimeError):tips.update_wish_num(0.2)
  with self.assertRaises(RuntimeError):held(None,2)
  self.assertEqual(len(owner.calls),count)
 def test_all46_original_cardbox_tips_preserve_detail_entry(self):
  for row in self.ui_policy['pools']:
   with self.subTest(t=row['id']):
    box=self.box();box.draw_type=row['id'];events=[];box.add_layer=lambda layer:layer;box.proc_event=lambda event,t,**kw:events.append((event,t,kw['_layer']))
    tips=self.comp(2,box);tips.add_layer=box.add_layer;tips.proc_event=box.proc_event;tips.set_info(row['id'])
    self.assertEqual(tips.show_jiaozhi,bool(row['jiaozhi']));self.assertEqual(tips.show_leichong,bool(row['charge']))
    if row['jiaozhi']:
     self.gg.ui.panels.card_jiaozhi_2=object();tips.on_tips_click(None,2);self.assertEqual(events[-1],('show',row['id'],self.gg.ui.panels.card_jiaozhi_2))
    elif row['charge']:
     self.gg.ui.panels.card_leichong=object();tips.on_tips_click(None,2);self.assertEqual(events[-1],('show',row['id'],self.gg.ui.panels.card_leichong))
    else:self.assertEqual(events,[])
 def test_original_tab_component_all46_real_fallback_and_assets(self):
  from read_data_table import read
  source='analysis/original-py-640/cocos/comps/card_common/tab.py';env=dict(self.env);env['HUODONG_MAIN']=old.NS(data=read(ROOT/'analysis/original-py-640/com/data/cdata/huodong_main.py'));env['UI_COMP_DATA']=old.NS(data=read(ROOT/'analysis/original-py-640/com/data/cdata/ui_comp_data.py'))
  lines=(ROOT/'analysis/original-py-640/com/const.py').read_text().splitlines(True);start=next(i for i,l in enumerate(lines) if l.startswith('class DanchiRemindType('));end=next(i for i in range(start+1,len(lines)) if lines[i].strip() and not lines[i].startswith((' ','\n')));namespace={};exec(compile(''.join(lines[start:end]),'<original literal enum>','exec'),namespace);self.const.DanchiRemindType=namespace['DanchiRemindType']
  cls=type('Comp',(),{'FILE_PATH':'cocos/image/card/tab/','IMG_PATH':{'normal':'tab_main_jiyi.png'},'__getitem__':lambda obj,k:obj.nodes.setdefault(k,old.Widget())});env['Comp']=cls
  parsed=old.ast.parse(str(old.slot.FIX.refactor_string((ROOT/source).read_text(),source)));bodies={n.name:n for declaration in parsed.body if isinstance(declaration,old.ast.ClassDef) for n in declaration.body if isinstance(n,old.ast.FunctionDef)}
  for name in ('getHdDataByDanchiId','getLeftTimeDesc','set_info','set_red_point'):
   node=bodies[name];node.decorator_list=[];exec(compile(old.ast.Module(body=[node],type_ignores=[]),source+':complete-selected-body','exec'),env);setattr(cls,name,env[name])
  for row in self.ui_policy['pools']:
   with self.subTest(t=row['id']):
    obj=cls();obj.nodes={};obj.image=old.Widget();obj.image_jingxuan=old.Widget();obj.jingxuan_hero_img=old.Widget();obj.shader=None;obj.img_shader=old.NS(shader=None);obj.tips=old.Widget();obj.time_txt_start=old.Widget();obj.time_num=old.Widget();obj.time_txt_end=old.Widget();obj.red_point=old.Widget();obj.set_info(lambda t:None,row['id'],row['info'].get('tabImgPath',''))
    self.assertEqual(obj._type,row['id']);self.assertIn(obj.image.texture,row['required_assets'])
    if obj.jingxuan_hero_img.texture:self.assertIn(obj.jingxuan_hero_img.texture,row['required_assets'])
 def test_rows_do_not_keep_rotated_foreign_epoch(self):
  x=families._Rows({9:{'drawType':283},10:{'drawType':1}}, {8:{'drawType':283,'times':220}},'charge',{283})
  self.assertEqual(x.keys(),[10,8]);self.assertIsNone(x.get(9));r=x[8];r['times']=0;self.assertEqual(x[8]['times'],220)
  y=families._Rows({(283,9):{'id':9},(1,3):{'id':3}},{(283,8):{'id':8}},'jiaozhi',{283});self.assertEqual(y.keys(),[(1,3),(283,8)]);self.assertIsNone(y.get((283,9)))
 def test_closed_candidate_never_enters_detail(self):
  self.dynamic.policy['detail_ids']=[];families._POLICY_RAW_SHA=hashlib.sha256(canonical(self.dynamic.policy)).hexdigest()
  with self.assertRaises(RuntimeError):self.panel().notify_show(283)

 def test_original_jz_four_and_six_rows_without_hardcoded485(self):
  for t in [p['id'] for p in self.ui_policy['pools'] if p['jiaozhi']]:
   with self.subTest(t=t):
    panel=self.panel();panel.notify_show(t)
    self.assertEqual(panel.draw_type,t);self.assertEqual(panel.hero,next(p for p in self.ui_policy['pools'] if p['id']==t)['jiaozhi'][0]['target_hero'])
    panel.do_btn_leichou_click()
    rows=next(p for p in self.ui_policy['pools'] if p['id']==t)['charge'];self.assertEqual(len(panel.leichou_list_comps),len(rows))

 def test_original_charge_only_all11(self):
  for row in [p for p in self.ui_policy['pools'] if p['family']=='charge_only']:
   with self.subTest(t=row['id']):
    cls=self.dynamic.classes[5];panel=cls();panel.nodes={};panel._node=old.Widget();panel.valid=True;panel.on_init();self.gg.ui.panels.card_leichong=panel
    panel.remove_comp=lambda c:None;panel.load_comp=lambda *a,**k:self.comp(3,panel);panel.destroy_self_layer=lambda:None;panel.on_load();panel.notify_show(row['id'])
    self.assertGreater(panel.hero,0);self.assertEqual(panel._type,row['id']);self.assertEqual(len(panel.list_comps) if len(row['charge'])>2 else len([r for r in panel.reward_info if r._node.visible]),len(row['charge']))

# Reuse the original485 consumer/lifecycle assertions against this single new
# owner; no production import of the old adapter is introduced.
for name in ('test_actual_helper_fixed_display_oracles','test_original_jiaozhi_ignores_expired_only_within_scoped_panel','test_original_charge_pages_use_fixed_four_rows_not_rotation','test_tips_to_original_jz2_entry_and_blessing_ui_predicate','test_frozen_companions_reinstall_and_record_identity','test_old_avatar_data_and_ui_callbacks_never_reach_current_actions','test_old_lock_epoch_rejected_but_new_show_scope_works','test_same_avatar_reinit_retires_old_callbacks','test_same_avatar_box_reinit_retires_old_component_callback','test_old_show_and_parent_component_callbacks_rejected','test_other_pool_rows_and_real_time_are_never_overwritten','test_actual_checkmulti_retains_once_and_normal_end_releases_once','test_retained_begin_avatar_change_end_cleanup_without_business','test_retained_begin_ui_change_end_cleans_only_old_ui','test_same_sender_new_begin_old_bound_end_cannot_release_new_gesture','test_ambiguous_overlapping_begin_cancels_and_refuses_business','test_click_cleanup_does_not_touch_reset_rpc_dictionary','test_original_memorybless_to_original_tooltip_positive'):
 setattr(FamilyConsumerTests,name,getattr(old.DynamicUiTests,name))

from tests import test_project7_draw_ui as drawtest
class SharedRequestGuardTests(unittest.TestCase):
 setUp=drawtest.HistoryUITests.setUp;install=drawtest.HistoryUITests.install;view=drawtest.HistoryUITests.view;capture_original_callbacks=drawtest.HistoryUITests.capture_original_callbacks
 def owner(self,state):
  class Owner:
   def __init__(obj):obj.draw_owner=state;obj.policy={'verified_ids':[229],'detail_ids':[229]};obj.available=True;obj.seen=[]
   def before_request(obj,t,avatar):
    obj.seen.append((t,avatar))
    if not obj.available:raise RuntimeError('Required public resource absent')
  return Owner()
 def test_original_request_fails_before_lock_and_rpc_when_resource_missing(self):
  state=self.install();owner=self.owner(state);state.register_request_guard(owner,[229],owner.before_request);owner.available=False
  for method,args in [('requestLuckyDrawFile',(229,)),('requestLuckyDrawFileAndOpenAll',(229,)),('requestLuckyDrawCard',(0,229)),('requestFile',(229,)),('requestLuckyDrawAllLeftCard',(229,))]:
   with self.subTest(method=method):
    with self.assertRaises(RuntimeError):getattr(self.view(),method)(*args)
  self.assertEqual(self.gg.ui._lock,{});self.assertEqual(self.gg.ui.recon_lock,0);self.assertFalse(any(c[0]=='rpc' for c in self.calls))
 def test_original_delayed_confirm_rechecks_before_real_acquire(self):
  callbacks=self.capture_original_callbacks();state=self.install();owner=self.owner(state);state.register_request_guard(owner,[229],owner.before_request);confirms=[];self.gg.ui.panels.common_confirm_3.notify_confirm=lambda *a,**k:confirms.append(k['confirm_cb'])
  self.view().requestLuckyDrawFileAndOpenAll(229);self.assertEqual(len(confirms),1);owner.available=False
  with self.assertRaises(RuntimeError):confirms[0]()
  self.assertEqual(callbacks,[]);self.assertEqual(self.gg.ui._lock,{});self.assertEqual(self.gg.ui.recon_lock,0)
 def test_same_avatar_replaced_data_cannot_acquire_old_confirmation(self):
  callbacks=self.capture_original_callbacks();state=self.install();owner=self.owner(state);state.register_request_guard(owner,[229],owner.before_request);confirms=[];self.gg.ui.panels.common_confirm_3.notify_confirm=lambda *a,**k:confirms.append(k['confirm_cb'])
  self.view().requestLuckyDrawFileAndOpenAll(229);self.assertEqual(len(confirms),1);self.gg.avatar.luckyDrawData=old.NS(getIsOpenCard=lambda t:True)
  with self.assertRaises(RuntimeError):confirms[0]()
  self.assertEqual(callbacks,[]);self.assertEqual(self.gg.ui._lock,{});self.assertEqual(self.gg.ui.recon_lock,0)
 def test_exact_registration_and_stale_avatar(self):
  state=self.install();owner=self.owner(state);state.register_request_guard(owner,[229],owner.before_request);self.assertIs(state.register_request_guard(owner,[229],owner.before_request),owner)
  other=self.owner(state)
  with self.assertRaises(RuntimeError):state.register_request_guard(other,[229],other.before_request)
  with self.assertRaises(RuntimeError):state.register_request_guard(owner,[229],lambda *a:None)
  with self.assertRaises(RuntimeError):state.check_request_guard(229,object())
  with self.assertRaises(RuntimeError):state.register_request_guard(other,[1],other.before_request)
 def test_quit_and_old_callback_cleanup_do_not_recheck_resource_gate(self):
  callbacks=self.capture_original_callbacks();state=self.install();owner=self.owner(state);state.register_request_guard(owner,[229],owner.before_request)
  self.view().doRequestLuckyDrawFile(229);owner.available=False;callbacks[0]();self.assertEqual(self.gg.ui.recon_lock,0)
  self.gg.avatar.luckyDrawData.activity_data[229].is_open_file=True;self.view().requestQuitFile(229);self.assertTrue(any(c[0]=='rpc' and c[1]=='requestQuitFile' for c in self.calls));callbacks[-1]();self.assertEqual(self.gg.ui.recon_lock,0)

class ComposedActivityEntryTests(unittest.TestCase):
 setUp=FamilyConsumerTests.setUp;actor=FamilyConsumerTests.actor;grid=FamilyConsumerTests.grid;comp=FamilyConsumerTests.comp;panel=FamilyConsumerTests.panel;box=FamilyConsumerTests.box
 def test_original_real_load_and_notify_show_all41_composed_shells(self):
  from legacy_csb_reader import Reader,widgets,field
  from read_data_table import read
  from unittest.mock import MagicMock
  import re
  class Node(old.Widget):
   def __init__(n,name):super(Node,n).__init__();n.name=name;n.parent=None;n.children={};n.x=0;n.y=0;n.data=old.NS(set_info=lambda *a:None)
   def getName(n):return n.name
   def setName(n,v):n.name=v
   def getChildren(n):return list(n.children.values())
   def getChildByName(n,name):return n.children.get(name)
   def addChild(n,child,*a):n.children[child.name]=child;child.parent=n
   def removeFromParent(n):
    if n.parent:n.parent.children.pop(n.name,None);n.parent=None
   def setPositionX(n,v):n.x=v
   def getPositionX(n):return n.x
   def setPositionY(n,v):n.y=v
   def getPositionY(n):return n.y
   def setRotation(n,v):n.rotation=v
   def setAnimation(n,*a):pass
  def load(path,normalize=False):
   w=widgets(Reader(path).read());nodes={}
   for v in w:
    key=re.sub(r'>[^.]+\.[^.]+','',v['path']);parent,_,name=key.rpartition('.');n=Node(name or key);nodes[key]=n
    if parent:nodes[parent].addChild(n)
   root=nodes[next(iter(nodes))]
   if normalize:
    for n in root.getChildren():
     for suffix in ('_iphonex_left','_iphonex_right'):
      if n.name.endswith(suffix):root.children.pop(n.name);n.setName(n.name[:-len(suffix)]);root.children[n.name]=n
   return root
  class Panel:
   PANEL_PREFIX='card_activity_%d';LOAD_DIR='cocos';PANEL_TYPE_DYNAMIC=1;PANEL_TYPE_STATIC=2;STATIC_LIST=[7];PANEL_POOL={-1:'card_activity_61',-3:'card_activity_62',-2:'card_zixuan'};PATH_HERO='cocos/image/hero/card/';PATH_TITLE='cocos/image/card/'
   def __getitem__(obj,key):
    n=obj._node
    for name in key.split('.'):
     n=n.getChildByName(name)
     if n is None:return None # actual optional lookup ABI, mandatory calls then fail
    return n
   def iter_comp(obj):return [] # explicit native replacement/comp-constructor seam
  rows={p['id']:p['info'] for p in ui_policy()['pools']};comp=read(ROOT/'analysis/original-py-640/com/data/cdata/ui_comp_data.py')
  source='analysis/original-py-640/cocos/panels/card_activity_base.py';gg=old.NS(avatar=old.NS(heroMgrData=old.NS(getHero=lambda h:None),luckyDrawData=old.NS(activity_data={})),ui=old.NS(projplistinfo={},replace_comp=lambda *a,**k:None))
  current={};loads=[]
  class Action(old.Action):
   def play(obj,*args):obj.events.append(('play',len(args))) # native callback stays deferred
  def action(file,name):return Action() if name in current['actions'] else None
  cc=old.NS(ccs=old.NS(GUIReader=old.NS(getInstance=lambda:old.NS(widgetFromBinaryFile=lambda f,a:load(current['path']))),ActionManagerEx=old.NS(getInstance=lambda:old.NS(getActionByName=action))),cc=old.NS(CallFunc=old.NS(create=lambda f:f),SpriteFrameCache=old.NS(getInstance=lambda:old.NS(addSpriteFrames=lambda p:loads.append(p)))),ccsp=old.NS(SkeletonAnimation=old.NS(createWithFile=lambda *a:Node('spine'))))
  env={'gg':gg,'cc':cc,'const':old.NS(DEBUG_UI_JSON=False),'Panel':Panel,'CHOUKA_INFO_DATA':old.NS(data=rows),'UI_COMP_DATA':old.NS(data=comp)}
  prototype=Panel;Panel=self.dynamic.classes[6]
  for key in ('PANEL_PREFIX','LOAD_DIR','PANEL_TYPE_DYNAMIC','PANEL_TYPE_STATIC','STATIC_LIST','PANEL_POOL','PATH_HERO','PATH_TITLE','__getitem__','iter_comp'):setattr(Panel,key,prototype.__dict__[key])
  gg=self.gg;gg.ui.projplistinfo={};gg.ui.replace_comp=lambda *a,**k:None;env['gg']=gg;env['Panel']=Panel
  parsed=old.ast.parse(str(old.slot.FIX.refactor_string((ROOT/source).read_text(),source)));bodies={n.name:n for n in old.ast.walk(parsed) if isinstance(n,old.ast.FunctionDef)}
  for name in ('on_load','real_load','real_load_anim','notify_show','refresh_tips','set_jiaozhi','refresh_ui_idxs','refresh_self_choose','can_play_loop','common_node_setting','hero_1__hero__image','hero_2__hero__image','hero_1__name','hero_2__name','title__text_2','on_info_click','on_chest_click'):
   node=bodies[name];node.decorator_list=[];exec(compile(old.ast.Module(body=[node],type_ignores=[]),source+':complete-selected-body','exec'),env);self.dynamic.originals[6,name]=env[name]
  checked=[]
  for p in ui_policy()['pools']:
   idx=p['info'].get('room_enter_index')
   if not idx or idx==7:continue
   with self.subTest(t=p['id']):
    name=Panel.PANEL_POOL.get(idx,Panel.PANEL_PREFIX%idx);path=ROOT/'analysis/project7/dynamic-family-entry-probe-v1'/(name+'.csb');tree=Reader(path).read();current.update(path=path,actions={field(n,'name')['value'] for n in field(field(tree,'animation'),'actionlist')['children']})
    obj=Panel();obj._node=load(ROOT/'analysis/project7/dynamic-ui-resources-v1/card_activity_base.csb',True);obj.valid=True;gg.ui.panels.card_activity_base=obj;obj.on_init();obj.cur_activity_id=idx;obj.cur_drawtype=p['id'];obj.logger=MagicMock();obj.on_load();obj.notify_show()
    self.assertIsNotNone(obj['top_right.tips_jiaozhi']);self.assertIsNotNone(obj['activity_1']);self.assertIsNotNone(obj['activity']);self.assertIsNotNone(obj['top_middle']);self.assertEqual(obj.cur_drawtype,p['id']);checked.append(p['id'])
  self.assertEqual(len(checked),41)

def _all46_original_request_chain(self):
 # Execute the complete canonical640 class bodies, not the legacy source
 # extractor; decorators are omitted only to enumerate46 fixtures immediately.
 for relative,cls,names in [('entity/avatar_members/LuckyDrawMember.py',type(self.gg.avatar),('checkActivity','checkDrawInTime','checkCanRequestLuckyDrawFile','doRequestLuckyDrawFile','requestLuckyDrawFile','requestFile','requestLuckyDrawCard','requestLuckyDrawFileAndOpenAll','doRequestLuckyDrawFileAndOpenAll','requestLuckyDrawAllLeftCard','requestQuitFile','getLuckyDrawTypeCoin','getLuckDrawTypeRewardCoin')),('entity/avatar_attrs/LuckyDrawData.py',type(self.gg.avatar.luckyDrawData),('getIsOpenCard','getCardTimes','getCurCardTimesDay','getTotalTimes','getOpenTimes','getNotOpendCardIndexs','get_draw_info','getOpenConsume','getLuckyDrawConsume','canOpenFile','canOpenCard','canOpenCardByConsume','checkFileAndOpenAllCostByConsume','checkFileAndOpenAllCost','checkLeftAllCardsCostByConsume','checkLeftAllCardsCost','canRequestFile'))]:
  path=ROOT/'analysis/original-py-640'/relative;parsed=old.ast.parse(str(old.slot.FIX.refactor_string(path.read_text(),str(path))));bodies={node.name:node for decl in parsed.body if isinstance(decl,old.ast.ClassDef) for node in decl.body if isinstance(node,old.ast.FunctionDef)}
  for name in names:
   node=bodies[name];node.decorator_list=[];exec(compile(old.ast.Module(body=[node],type_ignores=[]),str(path)+':complete-selected-body','exec'),self.env);setattr(cls,name,self.env[name])
 state=self.install();ids=ui_policy()['candidate_ids'];state.history=frozenset(set(state.history)|set(ids));state.ready=frozenset(set(state.ready)|set(ids));owner=self.owner(state);owner.policy={'verified_ids':ids,'detail_ids':ids};state.register_request_guard(owner,ids,owner.before_request);callbacks=[];data=self.gg.avatar.luckyDrawData
 def send(actor,method,params,**kwargs):
  self.calls.append(('rpc',method,dict(params)))
  if 'callback' in kwargs:callbacks.append(kwargs['callback'])
 type(self.gg.avatar).callServerMethod=send;type(self.gg.avatar).callServerMethodReliable=send
 for t in ids:
  with self.subTest(t=t):
   data.activity_data[t]=old.NS(card_times=0,cur_card_times_day=0,is_open_file=False,draw_info={});self.calls.clear();callbacks.clear()
   self.view().requestLuckyDrawFile(t);self.assertEqual([c[1] for c in self.calls if c[0]=='rpc'],['requestLuckyDrawFile']);callbacks[-1]()
   # Existing pending is an input fixture, not a simulated successful reply.
   data.activity_data[t].is_open_file=True;data.activity_data[t].draw_info={str(i):{'is_open':False} for i in range(6)};self.calls.clear();self.view().requestLuckyDrawFile(t);self.assertEqual([c[1] for c in self.calls if c[0]=='rpc'],['requestFile'])
   self.calls.clear();self.view().requestLuckyDrawCard(0,t);self.assertEqual([c[1] for c in self.calls if c[0]=='rpc'],['requestLuckyDrawCard']);callbacks[-1]()
   self.calls.clear();self.view().requestLuckyDrawAllLeftCard(t);self.assertEqual([c[1] for c in self.calls if c[0]=='rpc'],['requestLuckyDrawAllLeftCard']);callbacks[-1]()
   self.calls.clear();self.view().requestQuitFile(t);self.assertEqual([c[1] for c in self.calls if c[0]=='rpc'],['requestQuitFile']);callbacks[-1]()
   data.activity_data[t].is_open_file=False;self.calls.clear();self.view().requestLuckyDrawFileAndOpenAll(t);self.assertEqual([c[1] for c in self.calls if c[0]=='rpc'],['requestLuckyDrawFileAndOpenAll']);callbacks[-1]()
   self.assertEqual(data.activity_data[t].card_times,0);self.assertEqual(self.gg.ui.recon_lock,0);self.assertEqual(self.gg.avatar.summonCoin,0);self.assertEqual(self.gg.avatar.yuanbao,0)
SharedRequestGuardTests.test_original_all46_new_single_all_resume_quit=_all46_original_request_chain
