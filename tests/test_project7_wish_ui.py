"""Selected original640 UI/data consumers; native renderer/network are explicit seams."""
import _paths  # noqa: E402,F401
import ast,copy,hashlib,importlib.util,json,sys,textwrap,types,unittest
from pathlib import Path
from unittest.mock import patch
from lib2to3.refactor import RefactoringTool,get_fixers_from_package
from project7_wish_ui_policy import ui_policy,canonical
ROOT=Path(__file__).resolve().parents[1];NS=types.SimpleNamespace;FIX=RefactoringTool(get_fixers_from_package('lib2to3.fixes'))
spec=importlib.util.spec_from_file_location('wish_candidate',ROOT/'offline/current/runtime/project7_wish_ui.py');wish=importlib.util.module_from_spec(spec);spec.loader.exec_module(wish)
def original(path,name,env,top=False):
 lines=(ROOT/path).read_text().splitlines(True);prefix=''if top else'    ';start=next(i for i,l in enumerate(lines)if l.startswith(prefix+'def '+name+'('));end=start+1
 while end<len(lines)and not(lines[end].startswith(prefix+'def ')or lines[end].startswith(prefix+'@')or top and lines[end].startswith('class ')):end+=1
 tree=ast.parse(str(FIX.refactor_string(textwrap.dedent(''.join(lines[start:end]))+'\n',path)))
 class Division(ast.NodeTransformer):
  def visit_BinOp(self,node):
   self.generic_visit(node)
   return ast.copy_location(ast.Call(func=ast.Name(id='_py2_div',ctx=ast.Load()),args=[node.left,node.right],keywords=[]),node)if isinstance(node.op,ast.Div)else node
 env['_py2_div']=lambda a,b:a//b if isinstance(a,int)and isinstance(b,int)else a/b;tree=ast.fix_missing_locations(Division().visit(tree));exec(compile(tree,path+':finite-original','exec'),env);return env[name]
class ReadViewTests(unittest.TestCase):
 def setUp(self):
  self.policy=ui_policy();self.owned=set();self.gg=types.ModuleType('gg');self.gg.ui=NS(_lock={},panels=NS());self.actor=NS(guessServerTime=lambda:1793750400,heroMgrData=NS(getHero=lambda h:object()if h in self.owned else None));self.gg.avatar=self.actor
  data=NS(activity_data={},inc_up_cnt={1:0});self.actor.luckyDrawData=data
  for p in self.policy['pools']:data.activity_data[p['id']]=NS(choose_treasure=[0,0,0],treasure_wish={},wish_info={},card_times=0,is_open_file=False,jiaozhi_count={},jiaozhi_rewards={},replace_count={})
  self.state=NS(gg=self.gg,current=lambda:self.gg,pools={p['id']:p for p in self.policy['pools']},wish={int(k):v for k,v in self.policy['wish'].items()},choose={int(k):v for k,v in self.policy['choose'].items()},fees={int(k):v for k,v in self.policy['fees'].items()},normals={int(k):v for k,v in self.policy['normals'].items()},infos={p['id']:p['info']for p in self.policy['pools']},jiaozhi={},policy=self.policy,member_owner=None)
  self.state.group_ids=types.MethodType(wish._Installation.group_ids,self.state)
  self.env={'gg':self.gg,'const':NS(LuckyDrawType=NS(NORMAL=1,YINGSHE=5)),'time':__import__('time'),'helpers':NS(checkTimeRange=lambda *a:False),'CHOUKA_TREASURE_WISH':NS(data=copy.deepcopy(self.state.wish)),'CHOUKA_INFO_DATA':NS(data=self.state.infos),'CHOUKA_NORMAL_DATA':NS(data=self.state.normals)}
  for name in('getTreasureWishIdByDrawType','getTreasureWishStep','getTreasureWishProb','getTreasureWishVal','getChooseTreasure','getWishTypeByDrawType','getWishGroupInfoListsByDrawType','getWishGroupInfoDict','getWishGroupListTotalFixedRate','getWishGroupMaxCount','getWishGroupProbDicts','getWishGroupValueDict'):
   setattr(data,name,types.MethodType(original('analysis/original-py-640/entity/avatar_attrs/LuckyDrawData.py',name,self.env),data))
  self.state.draw_type=lambda panel:panel._type;self.panel=NS(valid=True,_type=5,_node=object(),event_handlers={});self.scope=wish._Scope(self.state,self.panel,self.panel,5);self.panel._q7_wish_scope=self.scope;self.view=wish._Data(self.scope,data)
 def test_fixed_nine_projection_not_public_admission(self):
  self.assertEqual(self.policy['candidate_ids'],list(wish._IDS));self.assertEqual(self.policy['public_ready_ids'],[]);self.assertEqual(len(self.state.wish),143);self.assertEqual(len(self.state.choose),117);self.assertEqual(len(self.state.fees),6)
 def test_runtime_canonical_policy_pin_and_fixed_entry_reproduction(self):
  import tempfile,shutil
  from project7_wish_ui_policy import maintainer_entry_assets,ENTRY_SHA
  raw=canonical(self.policy);self.assertEqual(wish._policy(raw)['candidate_ids'],list(wish._IDS));self.assertEqual(raw,canonical(json.loads(raw)))
  bad=json.loads(raw);bad['default_wish_scope']=2
  with self.assertRaises(ValueError):wish._policy(canonical(bad))
  with tempfile.TemporaryDirectory() as temp:
   target=Path(temp)/'entry.gz';meta=maintainer_entry_assets(ROOT/'analysis/deployment/android/Documents/res/cocos.npk',ROOT/'analysis/android640-scripts/com/data/cdata',target);self.assertEqual(meta['sha256'],ENTRY_SHA);self.assertEqual(meta['ui_comp'],6)
   runtime=Path(temp)/'runtime';directory=runtime/'project7_wish_catalog';shutil.copytree(ROOT/'offline/current/data/project7_wish_catalog',directory);shutil.copy2(target,runtime/'project7_wish_ui_entry_assets.json.gz');self.assertEqual(ui_policy(directory),self.policy)
   with self.assertRaises(FileExistsError):maintainer_entry_assets(Path(temp)/'absent',Path(temp),target)
   (runtime/'project7_wish_ui_entry_assets.json.gz').write_bytes(b'bad')
   with self.assertRaises(ValueError):ui_policy(directory)
  for path in ('offline/current/runtime/project7_wish_ui.py','offline/current/runtime/project7_wish_transport.py'):FIX.refactor_string((ROOT/path).read_text('ascii'),path)
 def test_original_expired_scope_zero_while_local_default_one(self):
  self.assertEqual(self.actor.luckyDrawData.getTreasureWishIdByDrawType(5),0);self.assertEqual(self.view.getTreasureWishIdByDrawType(5),1);self.assertEqual(self.scope.choice(),(True,[1,0,0]));self.assertEqual(self.actor.luckyDrawData.activity_data[5].choose_treasure,[0,0,0])
 def test_ctr_bound_scope_and_original_fee_counter(self):
  self.actor.luckyDrawData.activity_data[5].choose_treasure=[2,1096,7];self.assertEqual(self.view.getTreasureWishIdByDrawType(5),2);self.assertEqual(self.view.getChooseTreasure(5),(True,[2,1096,7]));self.assertEqual(self.state.fees[min(7+1,6)]['cost'],500)
 def test_original_py2_probability_staircase(self):
  ad=self.actor.luckyDrawData.activity_data[5]
  for s,p in[(0,.02),(5,.02),(6,.03),(11,.03),(12,.04)]:
   ad.treasure_wish={1:s};self.assertAlmostEqual(self.view.getTreasureWishProb(5),p);self.assertAlmostEqual(self.view.getTreasureWishVal(5),p*1000)
 def test_group_all_five_expired_raw_but_fixed_scope_live(self):
  for t in(119,126,143,154,164):
   self.assertEqual(self.actor.luckyDrawData.getWishGroupInfoListsByDrawType(t),{});groups=self.view.getWishGroupInfoListsByDrawType(t);self.assertEqual(set(sum(groups.values(),[])),{k for k,r in self.state.wish.items()if r['drawType']==t})
 def test_owned_seed_only_view_no_global_f_a_or_c_mutation(self):
  ad=self.actor.luckyDrawData.activity_data[119];ad.wish_info={20:{'c':17,'f':[],'a':[]},21:{'c':2,'f':[],'a':[]}};before=copy.deepcopy(ad.wish_info);self.owned.add(96)
  ids,gids=self.view.getWishGroupProbDicts(119);self.assertNotIn(19,ids);self.assertAlmostEqual(ids[20],.01);view=self.view.getWishGroupInfoDict(119,20);self.assertEqual(view,{'c':17,'f':[19],'a':[19]});self.assertEqual(ad.wish_info,before)
 def test_real_server_completion_still_needs_original_animation_ack(self):
  self.owned.add(96);ad=self.actor.luckyDrawData.activity_data[119];ad.wish_info={20:{'c':0,'f':[19],'a':[]}};self.assertEqual(self.view.getWishGroupInfoDict(119,20)['a'],[])
 def test_group_safe90_honest_next_probability(self):
  for t in(119,126,143,154,164):
   rows=[r for r in self.state.wish.values()if r['drawType']==t];a=next(r for r in rows if r.get('fix_rate'));self.actor.luckyDrawData.activity_data[t].wish_info={a['gid']:{'c':89,'f':[],'a':[]}};ids,gids=self.view.getWishGroupProbDicts(t);self.assertEqual(ids[a['id']],1);self.assertEqual(sum(ids.values()),1);self.assertTrue(all(p==0 for k,p in ids.items()if k!=a['id']))
 def test_group_c17_18_source_staircase_and_two_targets_share(self):
  ad=self.actor.luckyDrawData.activity_data[119]
  for c,p in[(17,.005),(18,.0075)]:ad.wish_info={20:{'c':c,'f':[],'a':[]}};ids,gids=self.view.getWishGroupProbDicts(119);self.assertAlmostEqual(ids[19],p);self.assertAlmostEqual(ids[20],p)
 def test_up_three_read_same_iuc_and_source_hard_limit(self):
  self.actor.luckyDrawData.inc_up_cnt={1:106,7:22}
  for t in(397,426,445):
   ad=self.view.activity_data[t];self.assertEqual(ad.get_top_rate(),1);self.assertAlmostEqual(ad.get_inc_up_prob(self.view),.01);self.assertFalse(ad.get_is_must_up(self.view));self.actor.luckyDrawData.inc_up_cnt[1]=180;self.assertAlmostEqual(ad.get_inc_up_prob(self.view),.99);self.assertTrue(ad.get_is_must_up(self.view));self.actor.luckyDrawData.inc_up_cnt[1]=106
  self.assertEqual(self.actor.luckyDrawData.inc_up_cnt,{1:106,7:22})
 def test_epoch_actor_data_guards(self):
  self.gg.ui._lock={}
  with self.assertRaises(RuntimeError):self.view.getTreasureWishIdByDrawType(5)
 def test_no_table_clock_or_nested_mutation(self):
  before=copy.deepcopy(self.env['CHOUKA_TREASURE_WISH'].data);self.view.getWishGroupProbDicts(119);self.assertEqual(before,self.env['CHOUKA_TREASURE_WISH'].data);self.assertFalse(self.env['helpers'].checkTimeRange(None,None))
if __name__=='__main__':unittest.main()
