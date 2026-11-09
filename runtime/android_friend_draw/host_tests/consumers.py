"""Actual selected640 friendship request/RPC/card_open functions with inert UI probes."""
import ast,base64,contextlib,hashlib,importlib.util,io
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
p=ROOT/'runtime/android_draw_policy/host_tests/verify_original_consumers.py'
spec=importlib.util.spec_from_file_location('original_draw_probe',p);old=importlib.util.module_from_spec(spec);spec.loader.exec_module(old)
NS=old.NS

def verify(fixtures):
 member='analysis/original-py-640/entity/avatar_members/LuckyDrawMember.py';args='analysis/original-py-640/lib/common/RpcMethodArgs.py';decorators='analysis/original-py-640/lib/common/rpcdecorator.py';card='analysis/original-py-640/cocos/panels/card_open.py'
 checks=0;locks=set();events=[];callbacks={};pending={};gg=NS(avatar_callback_map=callbacks,avatar_callback_need_result=pending)
 gg.ui=NS(lock=lambda n:locks.add(n),unlock=lambda n:locks.remove(n),_tree=NS(proc_event=lambda *a,**k:None),enable_settlement=lambda *a:None)
 data=NS(friend_draw=False,friend_draw_count=0,new_friend_draw_count=0,canSummonFriendFirst=lambda:True,checkCardFriendLianChou=lambda n:True,checkCardNewFriendLianChou=lambda n:True)
 actor=NS(luckyDrawData=data,checkFriendCoin=lambda n:True,checkNewFriendCoin=lambda n:True,checkInDaily7Falg=lambda n:True)
 gg.avatar=actor;gg.ui.panels=NS(common_message=NS(notify_message=lambda n:events.append(('message',n))),settlement_fullscreen=NS(check_gonglue_cache_result=lambda *a:None),card_box=NS(notify_scene_card_open=lambda r:events.append(('box',r))))
 panel=NS(notify_show=lambda r,p:events.append(('primary_single',r)),notify_show_friend_lianchou=lambda r,p:events.append(('primary_ten',r)))
 scene=NS(notify_friend_card_open=lambda r,cb:(events.append(('scene',r)),cb()))
 gg.city_container=NS(get_scene_by_key=lambda k:scene,check_scene=lambda s:s is scene)
 const=NS(SUMMON_FRIEND_COST=200,SUMMON_NEW_FRIEND_COST=200,MAX_SUMMON_FRIEND_TIMES_DAY=100,MAX_SUMMON_NEW_FRIEND_TIMES_DAY=100,SUMMON_FRIEND_LIANCHOU_TIMES=10,SUMMON_NEW_FRIEND_LIANCHOU_TIMES=10,SCENE_SUMMON=1)
 ns={'gg':gg,'const':const,'CLIENT_STUB':3,'_logger':NS(warn=lambda *a:None,error=lambda *a:None),'StandardError':Exception,'EntityManager':NS(getentity=lambda p:None)}
 def selected(path,names):
  tree=ast.parse(str(old.FIX.refactor_string((ROOT/path).read_text(),path)));body=[n for n in tree.body if isinstance(n,(ast.FunctionDef,ast.ClassDef)) and n.name in names];assert {n.name for n in body}==set(names);exec(compile(ast.Module(body=body,type_ignores=[]),path+':selected','exec'),ns)
 selected(args,['ConvertError','RpcMethodArg','NoLimit','NumeralLimit','Int','Bool','List','Dict','Avatar','MailBox']);selected(decorators,['RpcMethod','rpc_method'])
 wrapped={}
 for name in ['replyLuckyDrawFriendCard','replyLuckyDrawFriendLianChouCard','replyLuckyDrawNewFriendCard','replyLuckyDrawNewFriendLianChouCard','updateFriendDraw']:
  lines=(ROOT/member).read_text().splitlines();deco=next(lines[i-1].strip() for i,l in enumerate(lines) if l.startswith('    def '+name+'('));wrapped[name]=eval(compile(ast.parse(deco[1:],mode='eval'),member+':decorator','eval'),ns)(old.function(member,name,ns))
 # Callback carrier is an original separately decorated CLIENT_STUB, not synthetic reply metadata.
 carrier_path='analysis/original-py-640/entity/avatar_members/ReliableRpcMember.py'
 lines=(ROOT/carrier_path).read_text().splitlines();start=next(i for i,l in enumerate(lines) if l.startswith('    def serverCallbackCarrier('));end=start+1
 while end<len(lines) and (not lines[end].strip() or lines[end].startswith('        ')):end+=1
 source='\n'.join(l[4:] for l in lines[start:end])+'\n';exec(compile(source,carrier_path+':selected','exec'),ns)
 wrapped['serverCallbackCarrier']=ns['rpc_method'](3,(ns['Dict']('_r_'),))(ns['serverCallbackCarrier'])

 for name in ['notfit_friend_card_open','notify_friend_card_lianchou_open','notify_scene_friend_card_open','notify_scene_friend_card_lianchou_open']:
  fn=old.function(card,name,ns);setattr(panel,name,lambda *a,_fn=fn:_fn(panel,*a))
 gg.ui.panels.card_open=panel;queue=[];gg.ui.add_settlement=lambda owner,name,r:queue.append((name,r));gg.ui.proc_settlement=lambda:None
 with contextlib.redirect_stdout(io.StringIO()):
  for label,frames in fixtures.items():
   i=int(label.rsplit('_',1)[1]);name=['requestLuckyDrawFriendCard','requestLuckyDrawFriendLianChouCard','requestLuckyDrawNewFriendCard','requestLuckyDrawNewFriendLianChouCard'][i];cbid=(200 if label.startswith('success') else 300)+i
   def send(method,params,callback):assert method==name and params=={};callbacks[cbid]=callback
   actor.callServerMethod=send;events.clear();queue.clear();old.function(member,name,ns)(actor);assert len(locks)==1 and cbid in callbacks;checks+=1
   decoded={}
   for digest,raw in frames:
    params=old.bson(raw)
    for n,fn in wrapped.items():
     if hashlib.md5(n.encode()).digest()==digest:fn(actor,params);decoded[n]=params
   assert not locks and cbid not in callbacks;checks+=1
   body=decoded[name.replace('request','reply')];assert isinstance(body['r'],list if i%2 else dict);checks+=1
   if label.startswith('success'):
    assert body['st'] and len(queue)==1;checks+=1
    method,reward=queue.pop();getattr(panel,method)(reward);assert sum(e[0]=='scene' for e in events)==1 and sum(e[0]==('primary_ten' if i%2 else 'primary_single') for e in events)==1;checks+=1
    if i%2:assert len(body['r'])==10;checks+=1
   else:assert body['st'] is False and not queue and not any(e[0]=='scene' for e in events);checks+=1
   assert data.friend_draw==decoded['updateFriendDraw']['fd'];checks+=1
 return {'checks':checks,'sources':{p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in [member,args,decorators,card,carrier_path]},'scope':'original four request bodies/decorators/reply schemas/callback carrier and friendship card_open->scene callback routing; inert UI transport, not scene animation/render acceptance'}
