"""Finite actual furniture RPC decorator/reply methods; inert UI/transport probes."""
import ast,contextlib,hashlib,importlib.util,io
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
p=ROOT/'runtime/android_draw_policy/host_tests/verify_original_consumers.py'
spec=importlib.util.spec_from_file_location('original_draw_consumer_probe',p);old=importlib.util.module_from_spec(spec);spec.loader.exec_module(old)
NS=old.NS

def verify(fixtures,wire_t):
 member='analysis/original-py-640/entity/avatar_members/LuckyDrawMember.py';arguments='analysis/original-py-640/lib/common/RpcMethodArgs.py';decorators='analysis/original-py-640/lib/common/rpcdecorator.py'
 checks=0;locks=set();events=[];registered={};pending={};gg=NS(avatar_callback_map=registered,avatar_callback_need_result=pending)
 gg.ui=NS(lock=lambda n:locks.add(n),unlock=lambda n:locks.remove(n),_tree=NS(proc_event=lambda *a,**k:events.append(a)),panels=NS(settlement_window_summon=None,city=NS(valid=False),city_room_danchi_new=None))
 gg.city_container=NS(get_scene_by_key=lambda key:None,get_current_scene=lambda:None)
 const=NS(CardPoolType=NS(TYPE_FURNITURE=2),MAX_FURNITURE_TIMES_DAY=500,SUMMON_FURNITURE_LIANCHOU_TIMES=10,LuckyDrawConsumeStyle=NS(STYLE_FURNITURE_ONCE=1,STYLE_FURNITURE_TEN=2),SCENE_NEW_DANCHI_ROOM=44)
 data=NS(getCurCardTimesDay=lambda *a,**k:0,checkFurnitureCardCost=lambda *a,**k:True,setCurCardTimeDay=lambda *a:events.append(('ct',*a)),setFurnitureLianchouTimes=lambda *a:events.append(('lt',*a)))
 actor=NS(luckyDrawData=data,checkActivity=lambda *a,**k:True,checkDrawInTime=lambda *a:True)
 def send(method,params,callback):registered[77]=callback;events.append(('send',method,params))
 actor.callServerMethod=send
 ns={'gg':gg,'const':const,'CLIENT_STUB':3,'_logger':NS(warn=lambda *a:None,error=lambda *a:None),'StandardError':Exception,'EntityManager':NS(getentity=lambda p:None)}
 def selected(path,names):
  tree=ast.parse(str(old.FIX.refactor_string((ROOT/path).read_text(),str(path))));body=[n for n in tree.body if isinstance(n,(ast.FunctionDef,ast.ClassDef)) and n.name in names];assert {n.name for n in body}==set(names);exec(compile(ast.Module(body=body,type_ignores=[]),str(path)+':selected','exec'),ns)
 selected(arguments,['ConvertError','RpcMethodArg','NoLimit','NumeralLimit','Int','Bool','List','Dict','Avatar','MailBox']);selected(decorators,['RpcMethod','rpc_method'])
 with contextlib.redirect_stdout(io.StringIO()):
  for label,send_name,reply_name,event_name in [('single','requestLuckyDrawFurnitureCard','replyLuckyDrawFurnitureCard','furniture_reward'),('ten','requestLuckyDrawFurnitureLianchouCard','replyLuckyDrawFurnitureLianchouCard','lianchou_furniture_reward')]:
   lines=(ROOT/member).read_text().splitlines();signature=next(lines[i-1].strip() for i,line in enumerate(lines) if line.startswith('    def '+reply_name+'('));assert signature.startswith('@rpc_method(')
   decorator=eval(compile(ast.parse(signature[1:],mode='eval'),member+':decorator','eval'),ns);wrapped=decorator(old.function(member,reply_name,ns));sender=old.function(member,send_name,ns)
   sender(actor,wire_t);assert send_name in locks;checks+=1
   params=old.bson(fixtures[label]);assert params['rs'] is True and params['i']['t']==wire_t;params['_cbid_']=77;wrapped(actor,params);assert not locks and 77 not in registered;checks+=1
   assert any(e[0]==event_name for e in events);checks+=1
   sender(actor,wire_t);failure=old.bson(fixtures['failure_'+label]);assert failure['rs'] is False;failure['_cbid_']=77;wrapped(actor,failure);assert not locks and 77 not in registered;checks+=1
   assert ('ct',wire_t,params['i']['ct']) in events;checks+=1
 return {'checks':checks,'sources':{p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in [member,arguments,decorators]},'scope':'original RPC schema/decorator/request/reply/callback and furniture reward event dispatch; inert transport/UI probes, no renderer/ART acceptance'}

def verify_reward_paths(fixtures,pending_manager):
 from tools.project7_draw_history_ir.consumer import load
 from tools.project7_draw_history_ir.codec import untyped
 ir=load();items=untyped(ir['tables']['item_data']);events=[];checks=0
 const=NS(FurnitureCardRewardType=NS(TYPE_SKIN=2,TYPE_PENDENT=3,TYPE_FURNITURE=4,TYPE_NORMAL=1),ItemType=NS(FURNITURE=20),RewardType=NS(MAIL=9))
 lucky=NS(skip_show_dict={},skip_flag=False,addSkinShowCount=lambda skin:events.append(('skin_count',skin)))
 gg=NS(avatar=NS(luckyDrawData=lucky));ns={'gg':gg,'const':const,'ITEM_DATA':NS(data=items),'Panel':NS(ICON_PATH='icon/%s',IMG_PATH='image/%s')}
 get_furniture=old.function('analysis/original-py-640/entity/avatar_attrs/LuckyDrawData.py','getFurnitureDianCang',ns);lucky.getFurnitureDianCang=lambda reward:get_furniture(lucky,reward)
 fullscreen=NS(notify_skin_new=lambda skin,**k:events.append(('skin',skin)),notify_hero_new=lambda *a:None,notify_cg_new=lambda *a:None,notify_hero_suipian=lambda *a,**k:None)
 fullscreen_fn=old.function('analysis/original-py-640/cocos/panels/settlement_fullscreen.py','notify_reward',ns);fullscreen.notify_reward=lambda rtype,reward:fullscreen_fn(fullscreen,rtype,reward)
 class Node:
  def setVisible(self,value):self.visible=value
  def setString(self,value):self.text=value
  def loadTexture(self,value):self.texture=value
 pendant=NS(txt_pendant_transfer=Node(),num_transfer=Node(),pic_transfer=Node(),item_icon=Node(),item_name=Node(),item_txt=Node(),load_model=lambda item:events.append(('pendant_model',item)))
 pendant_fn=old.function('analysis/original-py-640/cocos/panels/city_room_danchi_open.py','refresh_pendant',ns);pendant.notify_show=lambda reward:pendant_fn(pendant,reward)
 gg.ui=NS(panels=NS(settlement_fullscreen=fullscreen,city_room_danchi_open=pendant));panel=NS(set_settlement_end=lambda:events.append(('settlement_end',)))
 display=old.function('analysis/original-py-640/cocos/panels/city_room_danchi_new.py','show_furniture_reward',ns)
 for label in ('skin_first','skin_repeat','pendant_first','pendant_repeat'):
  reward=old.bson(fixtures[label])['i']['rwd'];events.clear();display(panel,reward)
  if label.startswith('skin'):
   source=reward['skin'][0][0];skin=items[source]['skin'];assert events.count(('skin',skin))==1 and events.count(('skin_count',skin))==1;checks+=1
   # An rtype2 item-only reply is not an adequate skin display proof.
   missing=dict(reward);missing.pop('skin');events.clear();display(panel,missing);assert not any(e[0]=='skin' for e in events);checks+=1
  else:
   source=reward['pendantExchange'][0][0] if label.endswith('repeat') else reward['item'][0][0]
   assert events.count(('pendant_model',source))==1 and items[source].get('subtype')==13;checks+=1
   if label.endswith('repeat'):assert pendant.txt_pendant_transfer.visible and int(pendant.num_transfer.text)==reward['pendantExchange'][0][3];checks+=1
  assert 'activityReward' not in reward and 'other_reward' not in reward;checks+=1
 # Actual complete original wardrobe method with pending BSON and inert widgets.
 hm=old.bson(pending_manager);skins={int(k):v for k,v in hm.get('ps',{}).items()};times={int(k):v for k,v in hm.get('psc',{}).items()}
 mgr=NS(getAllHeroes=lambda:{},getHero=lambda hero:None,pendingSkins=skins,pendingSkinsCreateTime=times,pendingPendant={},pendingPendantCreateTime={});gg.avatar.heroMgrData=mgr
 skin_meta={meta['skin']:{'item':identity} for identity,meta in items.items() if type(meta.get('skin')) is int}
 ns.update(SkinDataMod=NS(data=skin_meta),ITEM_DECORATION_DATA=NS(data={}))
 class Bag:
  FORBID_SHOW=1;FORBID_SELL=2;FORBID_NONE=0;select_index=0
  def __init__(self):self.sort=lambda values:values;self.gridScrollViewYC=NS(update_data_info=lambda *a,**k:None);self.sliderYC=NS(refresh=lambda:None);self.refresh_yichu_item_detail=lambda:None
  def __getattr__(self,key):value=Node();setattr(self,key,value);return value
  def __getitem__(self,key):return Node()
 bag=Bag();old.function('analysis/original-py-640/cocos/panels/bag_main.py','refresh_Yichu',ns)(bag)
 assert len(bag.showMsg)==sum(map(len,skins.values())) and all(msg['c']>=0 and msg.get('nohero') for msg in bag.showMsg);checks+=1
 return {'checks':checks,'sources':{p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in ['analysis/original-py-640/cocos/panels/city_room_danchi_new.py','analysis/original-py-640/cocos/panels/settlement_fullscreen.py','analysis/original-py-640/cocos/panels/city_room_danchi_open.py','analysis/original-py-640/cocos/panels/bag_main.py','analysis/original-py-640/entity/avatar_attrs/LuckyDrawData.py']},'scope':'selected original full reward routing/skin notification/pendant display data and pending wardrobe method; inert UI widgets and skin-item metadata projection, no animation/render/scene acceptance'}
