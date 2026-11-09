"""Finite isolated original consumer functions with inert UI/platform probes.
No game module imports, scene runtime, rendering or player state execution.
"""
import ast,base64,contextlib,hashlib,io,struct,textwrap,types
from pathlib import Path
from lib2to3.refactor import RefactoringTool
ROOT=Path(__file__).resolve().parents[3]
NS=types.SimpleNamespace
FIX=RefactoringTool(['lib2to3.fixes.fix_print','lib2to3.fixes.fix_except','lib2to3.fixes.fix_dict','lib2to3.fixes.fix_xrange'])

def bson(data):
 def document(raw,array=False):
  if struct.unpack_from('<i',raw)[0]!=len(raw) or raw[-1]!=0:raise ValueError('BSON envelope')
  p=4;out={}
  while p<len(raw)-1:
   tag=raw[p];p+=1;e=raw.index(0,p);key=raw[p:e].decode();p=e+1
   if tag in (3,4):n=struct.unpack_from('<i',raw,p)[0];v=document(raw[p:p+n],tag==4);p+=n
   elif tag==16:v=struct.unpack_from('<i',raw,p)[0];p+=4
   elif tag==18:v=struct.unpack_from('<q',raw,p)[0];p+=8
   elif tag==1:v=struct.unpack_from('<d',raw,p)[0];p+=8
   elif tag==8:v=bool(raw[p]);p+=1
   elif tag==2:n=struct.unpack_from('<i',raw,p)[0];p+=4;v=raw[p:p+n-1].decode();p+=n
   elif tag==7:v=raw[p:p+12].hex();p+=12
   elif tag==10:v=None
   else:raise ValueError('unsupported fixture BSON type '+str(tag))
   if key in out:raise ValueError('duplicate BSON')
   out[key]=v
  return [out[str(i)] for i in range(len(out))] if array else out
 return document(data)


def function(path,name,namespace):
 text=(ROOT/path).read_text();lines=text.splitlines(True)
 start=next(i for i,line in enumerate(lines) if line.startswith('    def '+name+'('))
 end=start+1
 while end<len(lines) and not (lines[end].startswith('    def ') or lines[end].startswith('    @')):end+=1
 source=str(FIX.refactor_string(textwrap.dedent(''.join(lines[start:end]))+'\n',str(path)))
 tree=ast.parse(source)
 # Only selected method body; no original module imports or class initialization.
 if any(isinstance(n,(ast.Import,ast.ImportFrom)) for n in ast.walk(tree)):raise ValueError('consumer method imports')
 exec(compile(tree,str(path)+':'+name,'exec'),namespace)
 return namespace[name]


def verify(fixtures):
 member='analysis/original-py-640/entity/avatar_members/LuckyDrawMember.py'
 item='analysis/original-py-640/cocos/comps/card_common/item_box.py'
 card='analysis/original-py-640/cocos/panels/card_open.py'
 city='analysis/original-py-640/game_scene/city_chouka.py'
 current={};events=[];settled=[]
 class Data:
  def set_draw_info(self,t,info,index=None):
   if index is None:current.clear();current.update(info)
   else:current[str(index)]=info
  def get_draw_info(self,t):return current
  def get_draw_info_index(self,t,i):return current.get(str(i))
  def addCardTimes(self,t,n):pass
 panel=NS(notify_reward=lambda r,p:settled.append(p),check_gonglue_cache_result=lambda *a,**k:None,notify_appstore_common=lambda:None)
 cardbox=NS(on_reply_request_file=lambda *a:events.append(('file',a)),notify_scene_card_open=lambda r:None)
 ui=NS(panels=NS(settlement_fullscreen=panel,settlement_window=panel,card_box=cardbox,card_open=NS(notify_scene_card_open=lambda r:None)),add_settlement=lambda *a:events.append(('preview',a)),proc_settlement=lambda:None,enable_settlement=lambda v:None)
 const=NS(RewardType=NS(MAIL=1),ItemType=NS(CHOOSE_HERO_FRAGMENT=999),VirtualItem=NS(GIFTCOIN=105),SCENE_SUMMON=1,DESIGN_WIDTH=100,DESIGN_HEIGHT=100)
 gg=NS(ui=ui,avatar=NS(luckyDrawData=Data()),game_width=100,game_height=100,scale_height=1,scale_width=1)
 namespace={'gg':gg,'const':const,'ITEM_DATA':NS(data={}), 'HERO_DATA':NS(data={})}
 self=NS(luckyDrawData=gg.avatar.luckyDrawData)
 replyFile=function(member,'replyFile',namespace);reply=function(member,'replyLuckyDrawCard',namespace);batch=function(member,'showLuckyDrawLianchouRewards',namespace)
 preview=function(card,'notify_scene_card_preview',namespace)
 original_open=function(card,'notify_scene_card_open',namespace)
 ui.panels.card_open.notify_scene_card_open=lambda info:original_open(NS(),info)
 result={};checks=0
 with contextlib.redirect_stdout(io.StringIO()):
  for label,data in fixtures.items():
   info=bson(data)
   if label=='unopened_hero':
    replyFile(self,True,{'0':info},1);before=len(events);preview(NS(),0,1);assert len(events)==before;checks+=1
   else:
    settled.clear();before_primary=len(events);reply(self,True,info,{},1);assert len(events)==before_primary+1;checks+=1
    assert settled and all(p==settled[0] for p in settled);result[label]=settled[0];checks+=1
    before=len(events);preview(NS(),info['index'],1);assert len(events)==before+1;checks+=1
  for label,payload in result.items():
   assert all(not payload[k] for k in ('hero','treasure','item','fragment','treasure_trans')),label
   checks+=1
  assert bson(fixtures['opened_hero'])['hero'];assert bson(fixtures['treasure'])['treasure'];assert bson(fixtures['design'])['treasure'];assert bson(fixtures['duplicate_hero'])['hero_frag'];assert bson(fixtures['currency'])['item']==[[90,8]];checks+=5
  settled.clear();batch(self,[bson(fixtures['currency']),bson(fixtures['treasure'])],1)
  assert not settled[0]['item'] and not settled[0]['treasure'];checks+=1
 # Original item_box gate with a sentinel at first visible=True boundary.
 class VisibleBoundary(Exception):pass
 class Node:
  visible=None
  def setVisible(self,v):
   self.visible=v
   if v:raise VisibleBoundary()
  def getParent(self):return NS(getWorldPosition=lambda:NS(x=0,y=0))
  def setPosition(self,v):pass
 node=Node();scene=NS(get_card_model=lambda i:NS(model=NS(world_position=(0,0,0))),scene_cam=NS(world_to_screen=lambda p:(0,0)))
 gg.city_container=NS(get_scene_by_key=lambda k:scene,check_scene=lambda s:True)
 namespace['cc']=NS(cc=NS(Vec2=lambda x,y:(x,y)))
 set_info=function(item,'set_info',namespace)
 box=NS(_node=node,_panel=NS(_node=NS(getContentSize=lambda:NS(height=100,width=100))),_force_hide=False)
 current.clear();current['0']=bson(fixtures['unopened_hero']);set_info(box,0,1);assert node.visible is False;checks+=1
 current['0']=bson(fixtures['opened_hero'])
 try:set_info(box,0,1)
 except VisibleBoundary:checks+=1
 else:raise AssertionError('opened result never crossed visibility gate')
 namespace['SummonType']=NS(FRIEND_LIANCHOU='batch',NONE='none',TREASURE='treasure',ITEM='item',HERO_FRAGMENT='fragment',HERO='hero')
 summon_type=function(city,'get_summon_type',namespace)
 for label,expected in [('currency','item'),('treasure','treasure'),('design','treasure'),('opened_hero','hero'),('memory','fragment')]:
  assert summon_type(NS(),bson(fixtures[label]))==expected
  checks+=1
 sources={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in [member,item,card,city]}
 return {'checks':checks,'sources':sources,'scope':'isolated original consumer methods and inert UI probes; not scene initialization or renderer/native acceptance'}


def verify_failure_rpc(fixtures,wire_t=1):
 """Original CLIENT_STUB decorator/arg conversion + sender callback unlock.
 Transport callback ID is an explicit inert host seam, not a gateway replay test.
 """
 member='analysis/original-py-640/entity/avatar_members/LuckyDrawMember.py'
 decorators='analysis/original-py-640/lib/common/rpcdecorator.py'
 arguments='analysis/original-py-640/lib/common/RpcMethodArgs.py'
 checks=0;locks=set();events=[];registered={};pending={}
 logger=NS(warn=lambda *a:None,error=lambda *a:None)
 gg=NS(avatar_callback_map=registered,avatar_callback_need_result=pending)
 ui=NS(lock=lambda name:locks.add(name),unlock=lambda name:locks.remove(name))
 gg.ui=ui
 data=NS(setIsFileOpen=lambda t,v:events.append(('file_flag',v)))
 actor=NS(luckyDrawData=data)
 gg.avatar=NS(newbeeData=NS(checkAllNewbee=lambda:None))
 const=NS(LuckyDrawType=NS(NORMAL=1),SCENE_SUMMON=1)
 scene=NS(on_reply_draw_file=lambda result:events.append(('scene_reply',result)))
 gg.city_container=NS(get_scene_by_key=lambda key:scene,check_scene=lambda scene:True)
 box=NS(valid=True,scene_type=wire_t,get_scene_type=lambda t:wire_t,get_luckyDraw_type=lambda:wire_t,
        set_is_open_file=lambda v:events.append(('box_file',v)),notify_open_file=lambda v:events.append(('open_notice',v)),
        set_state=lambda v:events.append(('state',v)),btn_progress=NS(setVisible=lambda v:None))
 ui.actions=NS(card_box=NS(main_in=NS(stop=lambda:events.append(('main_in','stop'))),main_close=NS(start=lambda:events.append(('main_close','start')))))
 ui.panels=NS(card_box=box)
 ns={'gg':gg,'const':const,'_logger':logger,'CLIENT_STUB':3,'EntityManager':NS(getentity=lambda p:None),'StandardError':Exception}
 def selected(path,names):
  raw=(ROOT/path).read_text()
  parsed=ast.parse(str(FIX.refactor_string(raw,str(path))))
  body=[node for node in parsed.body if isinstance(node,(ast.FunctionDef,ast.ClassDef)) and node.name in names]
  assert {node.name for node in body}==set(names)
  exec(compile(ast.Module(body=body,type_ignores=[]),str(path)+':selected','exec'),ns)
 selected(arguments,['ConvertError','RpcMethodArg','NoLimit','NumeralLimit','Int','Bool','List','Dict','Avatar','MailBox'])
 selected(decorators,['RpcMethod','rpc_method'])
 on_reply=function('analysis/original-py-640/cocos/panels/card_box.py','on_reply_draw_file',ns)
 box.on_reply_draw_file=lambda result,t:on_reply(box,result,t)
 def reliable(method,params,callback):
  registered[77]=callback;events.append(('send',method));return None
 actor.callServerMethodReliable=reliable
 with contextlib.redirect_stdout(io.StringIO()):
  for label,send_name,reply_name in [
   ('failure_file','doRequestLuckyDrawFile','replyLuckyDrawFile'),
   ('failure_all','doRequestLuckyDrawFileAndOpenAll','replyLuckyDrawFileAndOpenAll')]:
   params=bson(fixtures[label]);assert params['rt'] is False and params['t']==wire_t
   text=(ROOT/member).read_text().splitlines()
   signature=next(text[i-1].strip() for i,line in enumerate(text) if line.startswith('    def '+reply_name+'('))
   assert signature.startswith('@rpc_method(')
   decorator=eval(compile(ast.parse(signature[1:],mode='eval'),str(member)+':actual_decorator','eval'),ns)
   original=function(member,reply_name,ns);wrapped=decorator(original)
   sender=function(member,send_name,ns);sender(actor,wire_t);assert locks;checks+=1
   params['_cbid_']=77;wrapped(actor,params)
   assert not locks and 77 not in registered;checks+=1
   if label=='failure_file':
    assert ('scene_reply',False) in events and ('state','card_click') in events;checks+=1
   else:
    assert params['trwd']==[] and params['ffs']=={};checks+=1
   # Actual arg classes also provide safe defaults when false payload lacks them.
   if label=='failure_all':
    sender(actor,wire_t);short={'rt':False,'t':wire_t,'_cbid_':77};wrapped(actor,short)
    assert not locks and 77 not in registered;checks+=1
 return {'checks':checks,'sources':{p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in [member,decorators,arguments,'analysis/original-py-640/cocos/panels/card_box.py']},'scope':'actual CLIENT_STUB decorator, original arg conversion/defaults, original false handlers and reliable-sender callbacks; transport/scene actions inert probes, not full network/UI runtime'}
