"""Selected original choose/reply/epoch consumers on actual stock fixtures."""
import ast,contextlib,hashlib,importlib.util,io,time,types
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];NS=types.SimpleNamespace
p=ROOT/'runtime/android_draw_policy/host_tests/verify_original_consumers.py';spec=importlib.util.spec_from_file_location('selector_orig_probe',p);old=importlib.util.module_from_spec(spec);spec.loader.exec_module(old)
def public_items():
 import sys
 sys.path.insert(0,str(ROOT))
 from tools.project7_draw_history_ir.consumer import load
 from tools.project7_draw_history_ir.codec import untyped
 return untyped(load()['tables']['item_data'])
def verify(fixtures):
 checks=0;locks={'setChooseHero'};events=[];activity=NS(choose_heroes=[0,0,0]);data=NS(activity_data={484:activity});actor=NS(luckyDrawData=data)
 gg=NS(avatar=actor,avatar_callback_map={},avatar_callback_need_result={},ui=NS(unlock=lambda k:locks.remove(k),_tree=NS(proc_event=lambda *a,**k:events.append(a))))
 ns={'gg':gg,'CLIENT_STUB':3,'StandardError':Exception,'_logger':NS(warn=lambda *a:None,error=lambda *a:None),'EntityManager':NS(getentity=lambda p:None)}
 for path,names in [('analysis/original-py-640/lib/common/RpcMethodArgs.py',['ConvertError','RpcMethodArg','NoLimit','NumeralLimit','Int','Bool','List','Dict','Avatar','MailBox']),('analysis/original-py-640/lib/common/rpcdecorator.py',['RpcMethod','rpc_method'])]:
  tree=ast.parse(str(old.FIX.refactor_string((ROOT/path).read_text(),path)));body=[n for n in tree.body if isinstance(n,(ast.FunctionDef,ast.ClassDef)) and n.name in names];exec(compile(ast.Module(body=body,type_ignores=[]),path+':selected','exec'),ns)
 member='analysis/original-py-640/entity/avatar_members/LuckyDrawMember.py';reply=ns['rpc_method'](3,(ns['Int']('r'),ns['Int']('t'),ns['List']('h')))(old.function(member,'replySetChooseHeroes',ns))
 with contextlib.redirect_stdout(io.StringIO()):
  selected=old.bson(fixtures['choose']);reply(actor,selected);assert not locks and activity.choose_heroes==selected['h'] and len(events)==1;checks+=1
  saved=list(activity.choose_heroes);locks.add('setChooseHero');reply(actor,old.bson(fixtures['choose_failure']));assert not locks and activity.choose_heroes==saved and len(events)==1;checks+=1
  ns['const']=NS(LuckyDrawIdx=NS(HASH=0,S=1,A=2));ns['time']=time
  import sys
  sys.path.insert(0,str(ROOT/'tools'));from read_data_table import read
  table=read(ROOT/'analysis/original-py-640/com/data/cdata/chouka_info.py');ns['CHOUKA_INFO_DATA']=NS(data=table)
  ns['HERO_DATA']=NS(data=read(ROOT/'analysis/original-py-640/com/data/cdata/hero.py'));ns['ITEM_DATA']=NS(data=public_items())
  get=old.function('analysis/original-py-640/entity/avatar_attrs/LuckyDrawData.py','getChooseHeroes',ns)
  assert get(data,484,True)==(True,saved);checks+=1
  activity.choose_heroes=[saved[0]-1,*saved[1:]];assert get(data,484,True)==(False,[saved[0]-1,0,0]);checks+=1
  # Actual original replyLuckyDrawCard typed shape routes the stock primary once.
  primary=[];gg.ui.panels=NS(card_open=NS(notify_scene_card_open=lambda info:primary.append(info)),settlement_fullscreen=NS(check_gonglue_cache_result=lambda *a,**k:None,notify_reward=lambda *a:None),settlement_window=NS(notify_reward=lambda *a:None,notify_appstore_common=lambda:None))
  data.set_draw_info=lambda *a:None;data.addCardTimes=lambda *a:None
  ns['const'].RewardType=NS(MAIL=1);ns['const'].VirtualItem=NS(GIFTCOIN=105);ns['const'].ItemType=NS(CHOOSE_HERO_FRAGMENT=21)
  fn=old.function(member,'replyLuckyDrawCard',ns);params=old.bson(fixtures['store_open'])
  fn(actor,params['rt'],params['info'],params.get('prog',{}),params['t']);assert len(primary)==1;checks+=1
 return {'checks':checks,'sources':{str(path):hashlib.sha256((ROOT/path).read_bytes()).hexdigest() for path in [member,'analysis/original-py-640/entity/avatar_attrs/LuckyDrawData.py','analysis/original-py-640/lib/common/RpcMethodArgs.py','analysis/original-py-640/lib/common/rpcdecorator.py']},'scope':'actual choose success/failure through original RPC schema/decorator unlock/after_choose_hero, original epoch consumer and stock reveal primary route; inert UI, not rendering'}
