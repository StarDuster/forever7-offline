"""Finite ORIGINAL 640 function-body host execution; no NeoX/JNI/game/UI VM.
Explicit Py2 adaptations: print removal, iter* methods, eager filter, cmp sort,
integer division, xrange/unicode. UI node/Scene boundaries only are synthetic.
"""
from pathlib import Path
import ast,copy,functools,hashlib,importlib.util,json,sys,time,types,unittest,warnings
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools'))
from read_data_table import read
spec=importlib.util.spec_from_file_location('collection_visibility',ROOT/'runtime/project7_collection_visibility.py')
policy=importlib.util.module_from_spec(spec);spec.loader.exec_module(policy)
POLICY=(ROOT/'runtime/project7_collection_visibility/policy.json').read_text('ascii')
HERO=read(ROOT/'analysis/original-py-640/com/data/cdata/hero.py')
SKIN=read(ROOT/'analysis/original-py-640/com/data/cdata/skin.py')
INFO=read(ROOT/'analysis/original-py-640/com/data/cdata/hero_info.py')
COLLECT=read(ROOT/'analysis/original-py-640/com/data/cdata/collect_msg.py')
SOURCE_HASHES={}
NS=types.SimpleNamespace

def cmp(a,b):return (a>b)-(a<b)
def divide(a,b):return a//b if isinstance(a,int) and isinstance(b,int) else a/b
class Py2(ast.NodeTransformer):
 def visit_Attribute(self,node):
  self.generic_visit(node);node.attr={'iteritems':'items','iterkeys':'keys','itervalues':'values'}.get(node.attr,node.attr);return node
 def visit_BinOp(self,node):
  self.generic_visit(node)
  return ast.copy_location(ast.Call(func=ast.Name(id='_py2_div',ctx=ast.Load()),args=[node.left,node.right],keywords=[]),node) if isinstance(node.op,ast.Div) else node
 def visit_Call(self,node):
  self.generic_visit(node)
  if isinstance(node.func,ast.Name) and node.func.id=='sorted' and len(node.args)>1:
   fn=node.args.pop(1);node.keywords.append(ast.keyword(arg='key',value=ast.Call(func=ast.Name(id='_cmp_key',ctx=ast.Load()),args=[fn],keywords=[])))
  for k in node.keywords:
   if k.arg=='cmp':k.arg='key';k.value=ast.Call(func=ast.Name(id='_cmp_key',ctx=ast.Load()),args=[k.value],keywords=[])
  if isinstance(node.func,ast.Name) and node.func.id=='filter':
   return ast.copy_location(ast.Call(func=ast.Name(id='list',ctx=ast.Load()),args=[node],keywords=[]),node)
  return node

def original(relative,name,namespace,indent=4):
 path=ROOT/'analysis/original-py-640'/relative;SOURCE_HASHES[str(path.relative_to(ROOT))]=hashlib.sha256(path.read_bytes()).hexdigest()
 lines=path.read_text().splitlines(True);prefix=' '*indent
 scope=next((i for i,line in enumerate(lines) if line.startswith('class HeroMgrData(')),0) if relative=='entity/avatar_attrs/HeroMgrData.py' else 0
 start=next(i for i,line in enumerate(lines) if i>=scope and line.startswith(prefix+'def '+name+'('))
 end=next((i for i in range(start+1,len(lines)) if lines[i].strip() and not lines[i].startswith(prefix+' ') and not lines[i].startswith('\n')),len(lines))
 import textwrap
 source=textwrap.dedent(''.join(lines[start:end]));source='\n'.join(l for l in source.splitlines() if not l.lstrip().startswith('print '))+'\n'
 # One Py2 long literal is inside on_click, never selected. Selected functions
 # are syntactically Py3; semantic conversion above is explicit and bounded.
 tree=ast.fix_missing_locations(Py2().visit(ast.parse(source)))
 namespace.update({'cmp':cmp,'_cmp_key':functools.cmp_to_key,'_py2_div':divide,'xrange':range,
  'unicode':lambda value,encoding=None:value.decode(encoding or 'utf-8') if isinstance(value,bytes) else value})
 exec(compile(tree,'<finite-original-640-function>','exec'),namespace);return namespace[name]

class Node:
 def __init__(self):self.text=None;self.visible=None;self._node=self
 def setVisible(self,value):self.visible=value
 def setString(self,value):self.text=value
 def set_num(self,value):self.number=value
class BoundaryPanel:
 def __init__(self):self.valid=True;self.nodes={};self.calls=[]
 def __getitem__(self,key):return self.nodes.setdefault(key,Node())
 def __getattr__(self,key):
  if key.startswith(('text_','info_')):
   node=Node();setattr(self,key,node);return node
  raise AttributeError(key)
 def proc_event(self,*args,**kwargs):self.calls.append(('event',args))
class Hero:
 MAX_STAR_ORDER=5
 def __init__(self,hero_id):
  self.heroid=hero_id;self.skins={};self.curSkin=None;self.awakeSkinStyle=False;self.lastNorCurSkin=None
  self.openArtifact=False;self.artifact=NS(order=0);self.huohaihua=False
 def initFromDict(self,info):pass # Hero object construction boundary; ownership loop is original.
 def getShowedStarLevelAndOrder(self):return (1,0)

class VisibilityTests(unittest.TestCase):
 def module(self,name):
  if name in self.mods:return self.mods[name]
  if name not in self.saved:self.saved[name]=sys.modules.get(name)
  module=types.ModuleType(name);self.mods[name]=module;sys.modules[name]=module
  if '.' in name:
   parent,leaf=name.rsplit('.',1);setattr(self.module(parent),leaf,module)
  return module
 def setUp(self):
  self.saved={};self.mods={};self.hero=copy.deepcopy(HERO);self.skin=copy.deepcopy(SKIN)
  # Ensure no inherited game namespace executes/imports in the host harness.
  for name in ('entity.ClientAvatar','ClientAvatar'):
   self.saved[name]=sys.modules.pop(name,None)
  self.gg=self.module('gg');self.gg.avatar=None;self.gg.ui=NS(panels=NS(_panels={}),actions=NS(collect_info=NS(show=NS(start=lambda:None))))
  self.gg.ui._tree=NS(proc_event=lambda *args,**kwargs:self.events.append(('tree_event',args)))
  self.gg.audio_mgr=NS(ui_sound=lambda sound:None);self.events=[]
  self.gg.city_container=NS(add_scene=lambda *a:self.events.append('add_scene'),switch_simple_scene=lambda *a:self.events.append('switch_scene'))
  self.hdata=self.module('com.data.cdata.hero');self.hdata.data=self.hero
  self.sdata=self.module('com.data.cdata.skin');self.sdata.data=self.skin
  self.const=NS(DEBUG_HERO=False,DEBUG_OFFLINE=False,SCENE_HERO=7,StoryRouteType=NS(SET_XILO=set()),
   CollectInfoConst=NS(SHENQISHI=1,LIANDONG=2,YIJIETI=4),TREASURE_REFRESH_USE_ITEM_TYPE=NS(XILIANQUAN=0),
   DIALOGUE_MODEL_MAP={},HERO_HOME_MODEL_MAP={})
  self.cc=NS(ccui=NS(TOUCH_EVENT_ENDED=2))
  self.modules=[];self.classes=[]
  for name,cls in policy._TARGETS:
   m=self.module(name);m.gg=self.gg;m.HERO_DATA=self.hdata;m.SKIN_DATA=self.sdata;m.const=self.const;m.cc=self.cc
   m.time=time;m.HERO_INFO_DATA=NS(data=INFO);m.COLLECT_MSG=NS(data=COLLECT);m.LIANDONG_CAMP=NS(data={})
   C=type(cls,(BoundaryPanel,),{});setattr(m,cls,C);m.__dict__[cls]=C;self.modules.append(m);self.classes.append(C)
  mgrm=self.modules[0];mgrm.HeroDataMod=self.hdata;mgrm.SkinDataMod=self.sdata;mgrm.HeroData=Hero
  mgrm.helpers=NS(toIntKeyDict=lambda data:dict(data))
  for fn in ['initFromDict','getAllHeroes','getHero','getHeroSkin','getHeroModelId','isHeroBan']:
   setattr(self.classes[0],fn,original('entity/avatar_attrs/HeroMgrData.py',fn,mgrm.__dict__))
  helpers=self.module('cutils.chelpers');helpers.gg=self.gg;helpers.const=self.const;helpers.HERO_DATA=self.hdata
  original('cutils/chelpers.py','get_hero_model',helpers.__dict__,0);helpers.getHeroCollectMsg=lambda hero:(True,0,0,1)
  self.helpers=helpers
  targets=[(1,'update_heroes','cocos/panels/hero_herolist.py'),(1,'_cmp','cocos/panels/hero_herolist.py'),
   (1,'on_hero_click','cocos/panels/hero_herolist.py'),(2,'refresh','cocos/panels/collect_hero.py'),
   (3,'refresh_hero_info','cocos/panels/bbs_playerinfo_main.py'),(4,'refresh_title','cocos/panels/hero_wardrobe.py'),
   (5,'set_hero','cocos/comps/hero_herolist_common/wardrobe.py'),(6,'enter_scene','cocos/panels/hero_common.py'),
   (7,'notify_show','cocos/panels/collect_info.py'),(7,'notify_hide','cocos/panels/collect_info.py'),
   (7,'on_btn_close','cocos/panels/collect_info.py'),(7,'on_btn_return','cocos/panels/collect_info.py'),
   (7,'on_navigation_canvas_back','cocos/panels/collect_info.py')]
  for index,fn,path in targets:
   self.modules[index].chelpers=helpers;setattr(self.classes[index],fn,original(path,fn,self.modules[index].__dict__))
  def scene(**kwargs):self.events.append('SCENE_CONSTRUCTOR');return NS(set_ui_info=lambda info:self.events.append(('scene_info',info)))
  self.modules[1].city_heroshow=NS(Scene=scene)
  self.classes[1].HERO_NUM=6;self.classes[2].SORT_TYPE={}
  self.classes[7].destroy_self_layer=original('cocos/ui_tree.py','destroy_self_layer',self.modules[7].__dict__)
  self.originals={(i,name):getattr(C,name) for i,C in enumerate(self.classes) for name in C.__dict__ if callable(getattr(C,name))}
 def tearDown(self):
  for name,value in self.saved.items():
   if value is None:sys.modules.pop(name,None)
   else:sys.modules[name]=value
 def install(self,owned=None,all_skins=False):
  state=policy.install(POLICY);mgr=self.classes[0]();mgr.heroes={};mgr.bannedHeroes={};mgr.hero_shoucang=[]
  owned=list(self.hero) if owned is None else owned
  for hid in owned:
   hero=Hero(hid)
   skins=[sid for sid,data in self.skin.items() if data['hero']==hid] if all_skins else [hid]
   for sid in skins:
    if sid in self.skin:hero.skins['skin-'+str(sid)]=NS(id=sid)
   hero.curSkin=next(iter(hero.skins),None);hero.lastNorCurSkin=hero.curSkin;mgr.heroes[hid]=hero
  self.gg.avatar=NS(heroMgrData=mgr,storyData=NS(route='normal'),guessServerTime=lambda:2000000000)
  return state,mgr
 def list_panel(self):
  p=self.classes[1]();p.hero_type='all';p.weapon_type=0;p.attack_type=0;p.hero_shader=None;p.last_hero_click=0
  p.gridScrollView=NS(update_data_info=lambda count,data,**kw:p.calls.append(('grid',count,kw)))
  p.notify_attack_tips_hide=lambda:p.calls.append(('hide_tips',));p.curr_show_hero_list=[]
  return p
 def collect_panel(self):
  p=self.classes[2]();p.btn_clear=Node();p.filter_text='';p.style='shenqishi';p.genderType=0;p.heroType=0;p.battleAttrType=0;p.initStar=0;p.liandong_camp=0;p.sortType=0;p.empty_page=Node();p.page_switcher=object()
  p.gridScrollView=NS(update_data_info=lambda *a,**kw:None,set_page_switch=lambda *a,**kw:None);return p
 def test_original_lists_and_public_unowned_preserved(self):
  before=copy.deepcopy(self.hero);state,mgr=self.install()
  p=self.list_panel();p.update_heroes();self.assertEqual(set(p.curr_show_hero_list),set(self.hero));self.assertEqual(len(p.curr_show_hero_list),140)
  self.originals[(1,'update_heroes')](p);self.assertEqual(len(p.curr_show_hero_list),138)
  c=self.collect_panel();c.refresh();self.assertIn(46,c.sorted_list);c.style='yijieti';c.refresh();self.assertIn(125,c.sorted_list);c.style='shenqishi';c.refresh()
  normal=next(h for h,row in self.hero.items() if not row.get('hero_forbid',0) and h in c.sorted_list)
  mgr.heroes.pop(normal);c.refresh();self.assertIn(normal,c.sorted_list);self.assertTrue(mgr.isHeroDisplayable(normal));self.assertFalse(mgr.isHeroListVisible(normal))
  self.assertEqual(self.hero,before);self.assertNotIn(46,COLLECT);self.assertNotIn(125,COLLECT)
 def test_alias_hot_update_init_and_card(self):
  state,mgr=self.install(owned=[]);self.assertNotIn(46,mgr.q7_display_heroes)
  mgr.heroes[46]=Hero(46);self.assertIn(46,mgr.q7_display_heroes)
  mgr.initFromDict({'hrs':[(125,{})],'cfs':{}});self.assertIn(125,mgr.q7_display_heroes);self.assertNotIn(46,mgr.q7_display_heroes)
  p=self.classes[3]();p.refresh_hero_info(True,{});self.assertEqual(p.info_hero_num_total.text,'/139')
  p.refresh_hero_info(False,{'hn':1});self.assertEqual(p.info_hero_num_total.text,'/138')
 def test_actual_non_dye_counts_and_quick_both_branches(self):
  before=copy.deepcopy(self.skin);state,mgr=self.install(all_skins=True);total=0;legacy_total=0
  for hid in self.hero:
   p=self.classes[4]();p.hero_id=hid;p.refresh_title();number,denominator=map(int,p.text_buy_num.text.split('/'));self.assertEqual(number,denominator);total+=denominator
   self.originals[(4,'refresh_title')](p);legacy_total+=int(p.text_buy_num.text.split('/')[1])
  self.assertEqual((total,legacy_total),(395,390));self.assertEqual(self.skin,before)
  nonrelease=[sid for sid,row in self.skin.items() if not row.get('is_dye_skin',False) and row.get('release')!=1]
  self.assertEqual(len(nonrelease),5)
  for sid in nonrelease:
   hid=self.skin[sid]['hero'];comp=self.classes[5]();comp.sub_comps=[];comp.refresh=lambda:None;comp.select_skin=lambda *a,**kw:None
   comp.set_hero(hid,sid,'hero_wardrobe');self.assertIn(sid,comp.skins);self.assertFalse(any(self.skin[x].get('is_dye_skin',False) for x in comp.skins))
   comp.set_hero(hid,sid,'preview');self.assertIn(sid,comp.skins)
  # Original family/dye behavior is retained for an actually dyed selected row.
  dye=next(sid for sid,row in self.skin.items() if row.get('is_dye_skin',False) and row.get('release')==1)
  comp.set_hero(self.skin[dye]['hero'],dye,'preview');new_dyes={x for x in comp.skins if self.skin[x].get('is_dye_skin',False)}
  self.originals[(5,'set_hero')](comp,self.skin[dye]['hero'],dye,'preview');old_dyes={x for x in comp.skins if self.skin[x].get('is_dye_skin',False)}
  self.assertEqual(new_dyes,old_dyes)
 def test_owned_unreleased_selected_dye_preserves_original_family_semantics(self):
  state,mgr=self.install(all_skins=True)
  dye=next(sid for sid,row in self.skin.items() if row.get('is_dye_skin',False) and row.get('release')!=1)
  hid=self.skin[dye]['hero'];comp=self.classes[5]();comp.sub_comps=[];comp.refresh=lambda:None;comp.select_skin=lambda *a,**kw:None
  self.originals[(5,'set_hero')](comp,hid,dye,'preview');self.assertNotIn(dye,comp.skins)
  comp.set_hero(hid,dye,'preview');self.assertIn(dye,comp.skins)
  self.assertEqual([sid for sid in comp.skins if self.skin[sid].get('is_dye_skin',False)],[dye])
  comp.set_hero(hid,dye,'hero_wardrobe');self.assertFalse(any(self.skin[sid].get('is_dye_skin',False) for sid in comp.skins))
  title=self.classes[4]();title.hero_id=hid;title.refresh_title()
  expected=sum(1 for row in self.skin.values() if row['hero']==hid and not row.get('is_dye_skin',False))
  self.assertEqual(title.text_buy_num.text,'%d/%d'%(expected,expected))
 def test_reentrant_views_never_modify_globals_or_nested_rows(self):
  state,mgr=self.install();p=self.list_panel();seen=[]
  def inspect(*args,**kw):
   seen.append(self.modules[1].HERO_DATA is self.hdata and self.hero[46]['hero_forbid']==1)
   if len(seen)==1:p.update_heroes()
  p.gridScrollView.update_data_info=inspect;p.update_heroes();self.assertEqual(seen,[True,True])
 def info_panel(self):
  p=self.classes[7]();p.refreshNormal=lambda:None;p._show_tab=lambda:None;p._layer=None;p._parent=None
  self.gg.ui.panels.collect_info=p;self.gg.ui.panels.navigation_canvas=object();self.gg.ui.panels.hero_common=object();self.gg.ui.panels.common_message=NS(notify_message=lambda message:self.events.append('message'))
  return p
 def fallback_parent(self,panel):
  def add_layer(*children):
   layer=object();panel._layer=layer;panel._parent=NS(destroy_layer=lambda which:self.events.append(('destroy_layer',which)));return layer
  p=self.list_panel();p.add_layer=add_layer;return p
 def test_actual_resolver_pre_scene_fallback_close_and_normal_path(self):
  state,mgr=self.install();info=self.info_panel();p=self.fallback_parent(info)
  self.assertEqual(self.helpers.get_hero_model(46),10048);self.assertFalse(mgr.q7HasRenderableModel(46))
  self.assertEqual(self.helpers.get_hero_model(125),10176);self.assertFalse(mgr.q7HasRenderableModel(125))
  for hid in (46,125):
   self.events[:]=[];p.on_hero_click(hid);self.assertNotIn('SCENE_CONSTRUCTOR',self.events);self.assertEqual(info.heroid,hid)
   layer=info._layer;info.on_btn_close(None,2);self.assertIn(('destroy_layer',layer),self.events)
  p.on_hero_click(46);layer=info._layer;info.on_btn_return(None,2);self.assertIn(('destroy_layer',layer),self.events)
  p.on_hero_click(125);layer=info._layer;info.on_navigation_canvas_back();self.assertIn(('destroy_layer',layer),self.events)
  normal=next(h for h in self.hero if mgr.q7HasRenderableModel(h));self.events[:]=[]
  p.on_hero_click(normal);self.assertIn('SCENE_CONSTRUCTOR',self.events);self.assertIn('switch_scene',self.events)
  # Missing skin table row cannot take the HeroMgrData hero-id fallback into actor loading.
  mgr.heroes[normal].curSkin='unknown';mgr.heroes[normal].skins['unknown']=NS(id=987654)
  self.events[:]=[];p.on_hero_click(normal);self.assertNotIn('SCENE_CONSTRUCTOR',self.events)
  # A normal collect_info show resets only our fallback close route.
  info.notify_show(normal);self.events[:]=[];info.on_btn_close(None,2)
  self.assertTrue(any(x[0]=='tree_event' and x[1][0]=='colloct_sub_close' for x in self.events if isinstance(x,tuple)))
  self.assertFalse(any(isinstance(x,tuple) and x[0]=='destroy_layer' for x in self.events))
 def test_original_skin_resolver_all_public_rows_and_normal_original_body(self):
  state,mgr=self.install(all_skins=True);found=0;missing=0
  for sid,row in self.skin.items():
   hero=mgr.heroes[row['hero']];hero.curSkin='skin-'+str(sid)
   expected=str(int(row['model_id'])) in state.indexed_models
   self.assertEqual(mgr.q7HasRenderableModel(row['hero']),expected)
   found+=int(expected);missing+=int(not expected)
  self.assertEqual((found,missing),(492,2))
  info=self.info_panel();p=self.fallback_parent(info);normal=next(h for h in self.hero if mgr.q7HasRenderableModel(h))
  self.events[:]=[];self.originals[(1,'on_hero_click')](p,normal,'wardrobe');raw=list(self.events)
  self.events[:]=[];p.on_hero_click(normal,'wardrobe');self.assertEqual(self.events,raw)
 def test_reentrant_old_layer_close_cannot_clear_new_fallback_marker(self):
  state,mgr=self.install();info=self.info_panel();p=self.fallback_parent(info)
  p.on_hero_click(46);old=info._layer;once=[False]
  def destroy(layer):
   self.events.append(('destroy_layer',layer))
   if not once[0]:once[0]=True;p.on_hero_click(125)
  info._parent.destroy_layer=destroy
  info.on_btn_close(None,2);new=info._layer;self.assertIsNot(new,old)
  self.assertIs(info._q7_collection_fallback_layer[1],new)
  info.on_btn_close(None,2);self.assertNotIn('_q7_collection_fallback_layer',info.__dict__)
 def test_defensive_guard_and_unavailable_2d_never_enter_actor(self):
  state,mgr=self.install();info=self.info_panel();p=self.fallback_parent(info)
  info.refreshNormal=lambda:(_ for _ in ()).throw(KeyError('synthetic missing 2D'))
  p.on_hero_click(46);self.assertEqual(state.last_route,'two_d_unavailable');self.assertNotIn('SCENE_CONSTRUCTOR',self.events)
  p.add_layer=lambda *args:None;p.on_hero_click(46);self.assertEqual(state.last_route,'two_d_unavailable')
  common=self.classes[6]();common._set_jump=lambda *a:(_ for _ in ()).throw(AssertionError('actor jump'))
  common.refresh_set_hero=lambda *a,**kw:(_ for _ in ()).throw(AssertionError('actor load'))
  common.enter_scene({'hero_id':46});self.assertEqual(state.last_route,'blocked_before_actor_after_scene')
 def test_clone_defaults_closure_current_globals_and_py2_raw(self):
  ns={'ALIAS':NS(data={'v':1}),'late':2}
  exec('def factory(offset):\n def probe(value=3):\n  return value+offset+late+ALIAS.data["v"]\n return probe\n',ns)
  raw=ns['factory'](5);self.assertIs(policy._raw(NS(im_func=raw)),raw)
  self.assertEqual(policy._clone_call(raw,'ALIAS',NS(data={'v':7}),()),17)
  ns['late']=10;self.assertEqual(policy._clone_call(raw,'ALIAS',NS(data={'v':7}),()),25)
  self.assertEqual(ns['ALIAS'].data,{'v':1});self.assertEqual(raw(),19)
 def test_existing_actual_data_identity_and_unrelated_member_cache_preserved(self):
  mgr=self.classes[0]();mgr.initFromDict({'hrs':[(46,{})],'cfs':{}})
  self.gg.avatar=NS(heroMgrData=mgr)
  cache_module=self.module('com.base.game_object');sentinel=type('OriginalMember',(),{})
  original_cache={sentinel:[('untouched',object())]};cache_module.members_cache=original_cache;cache_module.method_cache={}
  state=policy.install(POLICY);self.assertTrue(mgr.isHeroListVisible(46));self.assertIn(46,mgr.q7_display_heroes)
  self.assertIs(cache_module.members_cache,original_cache);self.assertEqual(len(original_cache),1)
 def test_changed_module_class_or_dispatch_cache_rejected(self):
  cache_module=self.module('com.base.game_object');cache_module.members_cache={self.classes[0]:[]};cache_module.method_cache={}
  with self.assertRaises(RuntimeError):policy.install(POLICY)
  self.assertNotIn('isHeroDisplayable',self.classes[0].__dict__)
  cache_module.members_cache={};state,mgr=self.install()
  self.modules[2].Panel=type('Panel',(BoundaryPanel,),{})
  with self.assertRaises(RuntimeError):policy.install(POLICY)
 def test_install_identity_guards_and_python2_grammar(self):
  with warnings.catch_warnings():
   warnings.simplefilter('ignore',DeprecationWarning);from lib2to3.refactor import RefactoringTool
  RefactoringTool([]).refactor_string((ROOT/'runtime/project7_collection_visibility.py').read_text('ascii'),'visibility.py')
  state,mgr=self.install();self.assertIs(policy.install(POLICY),state)
  self.modules[1].Panel.update_heroes=lambda self:None
  with self.assertRaises(RuntimeError):policy.install(POLICY)
 def test_late_avatar_panel_cache_and_bad_policy_fail_closed(self):
  with self.assertRaises(ValueError):policy.install(POLICY+' ')
  late=self.module('entity.ClientAvatar');late.ClientAvatar=type('ClientAvatar',(),{})
  self.assertIsNotNone(policy.install(POLICY)) # mere Avatar class definition is not a Member cache hazard

 def test_invocation_uses_current_globals_or_refuses_changed_gg_generation(self):
  state,mgr=self.install();p=self.list_panel()
  self.modules[1].gg=types.ModuleType('foreign')
  with self.assertRaises(RuntimeError):p.update_heroes()
  self.modules[1].gg=self.gg
  sys.modules['gg']=types.ModuleType('new_generation')
  with self.assertRaises(RuntimeError):p.update_heroes()
 def test_cached_panel_and_incomplete_avatar_refused(self):
  self.gg.ui.panels._panels={'hero_herolist':object()}
  with self.assertRaises(RuntimeError):policy.install(POLICY)
  self.gg.ui.panels._panels={};self.gg.avatar=NS(heroMgrData=object())
  with self.assertRaises(RuntimeError):policy.install(POLICY)

def tearDownModule():
 # Machine-readable finite evidence for the report, never game-owned state.
 path=ROOT/'reports/project7-collection-visibility-implementation.sources.json'
 path.write_text(json.dumps(SOURCE_HASHES,indent=2)+'\n')
if __name__=='__main__':unittest.main()
