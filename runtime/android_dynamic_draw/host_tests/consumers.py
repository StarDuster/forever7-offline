"""Finite original typed consumers on actual dynamic Store replies; no native UI."""
import base64,contextlib,copy,hashlib,importlib.util,io,types
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];NS=types.SimpleNamespace
p=ROOT/'runtime/android_draw_policy/host_tests/verify_original_consumers.py';spec=importlib.util.spec_from_file_location('dynamic_old_consumers',p);old=importlib.util.module_from_spec(spec);spec.loader.exec_module(old)
def verify(fixtures):
 import sys
 sys.path.insert(0,str(ROOT));from tools.project7_dynamic_catalog import load
 from tools.project7_draw_history_ir.codec import untyped
 d=load();items=untyped(d['items']);events=[];settled=[];activity=NS(jiaozhi_count={},jiaozhi_rewards={991:42},replace_count={998:9});ldd=NS(activity_data={485:activity},inc_up_cnt={1:71},set_draw_info=lambda *a:None,addCardTimes=lambda *a:None)
 panel=NS(notify_reward=lambda r,p:settled.append(copy.deepcopy(p)),check_gonglue_cache_result=lambda *a,**k:None,notify_appstore_common=lambda:None)
 const=NS(RewardType=NS(MAIL=1),ItemType=NS(CHOOSE_HERO_FRAGMENT=21),VirtualItem=NS(GIFTCOIN=105));ui=NS(panels=NS(settlement_fullscreen=panel,settlement_window=panel,card_open=NS(notify_scene_card_open=lambda info:events.append(info))))
 gg=NS(ui=ui,avatar=NS(luckyDrawData=ldd));env={'gg':gg,'const':const,'HERO_DATA':NS(data={147:{'hero_composite_init_rank':4}}),'ITEM_DATA':NS(data=items)};actor=NS(luckyDrawData=ldd)
 member='analysis/original-py-640/entity/avatar_members/LuckyDrawMember.py';reply=old.function(member,'replyLuckyDrawCard',env);sync=old.function(member,'syncJiaozhiData',env);batch=old.function(member,'showLuckyDrawLianchouRewards',env);checks=0
 with contextlib.redirect_stdout(io.StringIO()):
  sync(actor,old.bson(fixtures['full_sync'])['i']);assert activity.jiaozhi_count[147]==7 and activity.jiaozhi_count[777]==91;checks+=1
  assert activity.jiaozhi_rewards=={991:42,"future":{"x":"opaque"}} and activity.replace_count[998]==9 and activity.replace_count["other"]=={"nested":True} and activity.jiaozhi_count["unknown-target"]=="opaque" and activity.replace_count[147]==1 and ldd.inc_up_cnt=={1:71};checks+=1
  for label in ('full','last','duplicate'):
   params=old.bson(fixtures[label]);info=params['info'];before=len(events);settled.clear();reply(actor,params['rt'],info,params.get('prog',{}),params['t']);assert len(events)==before+1 and settled;checks+=1
   payload=settled[-1]
   # Only real extras appear in generic settlement, never the primary memory.
   assert not payload['fragment'];checks+=1
   if label=='last':assert len(payload['treasure'])==1 and not payload['hero'];checks+=1
   if label=='duplicate':assert [10052,220] in payload['item'] and not any(i==16673 for i,n in payload['item']);checks+=1
  settled.clear();batch(actor,[old.bson(fixtures['full'])['info'],old.bson(fixtures['last'])['info']],485);assert settled and len(settled[-1]['treasure'])==2;checks+=1
 # Actual ActivityData init plus original reply/addCardTimes in real Result frame
 # order, starting with no activity object. Final original sync follows reply.
 data_source='analysis/original-py-640/entity/avatar_attrs/LuckyDrawData.py'
 Activity=type('ActivityData',(),{'__init__':old.function(data_source,'__init__',env),'initFromDict':old.function(data_source,'initFromDict',env)})
 env['LuckyDrawData']=NS(ActivityData=Activity);gg.ui._tree=NS(proc_event=lambda *a,**k:None);const.LuckyDrawType=NS(NORMAL=1)
 slot_spec=importlib.util.spec_from_file_location('dynamic_slot_loader',Path(__file__).with_name('verify_slot_projection.py'));slot=importlib.util.module_from_spec(slot_spec);slot_spec.loader.exec_module(slot);init=slot.method(member,'syncLuckyDrawActivityData',env);all_reply=old.function(member,'replyLuckyDrawFileAndOpenAll',env);add=old.function(data_source,'addCardTimes',env)
 ldd.addCardTimes=lambda t,n:add(ldd,t,n);ldd.setIsFileOpen=lambda *a:None;gg.ui.panels.card_box=NS(set_file_lianchou_info=lambda *a:None,on_reply_draw_file=lambda *a:None)
 ldd.activity_data.clear();seen=0
 with contextlib.redirect_stdout(io.StringIO()):
  for frame in old.bson(fixtures['all_sync_order'])['frames']:
   p=frame['params']
   if frame['method']=='syncLuckyDrawActivityData':init(actor,p['t'],p['d'])
   elif frame['method']=='syncJiaozhiData':
    assert 485 in ldd.activity_data;sync(actor,p['i']);seen+=1
   else:all_reply(actor,p['rt'],p['trwd'],p.get('ffs',{}),p['t'])
 assert seen==6 and ldd.activity_data[485].card_times==6;checks+=2
 failed=old.verify_failure_rpc({'failure_file':fixtures['failure_file'],'failure_all':fixtures['failure_all']},wire_t=485);checks+=failed['checks']
 return {'checks':checks,'failure_consumers':failed,'sources':{member:hashlib.sha256((ROOT/member).read_bytes()).hexdigest()},'scope':'actual original syncJiaozhiData, single and batch result bodies plus original group-failure RPC schema/decorator/sender cleanup; inert UI. Not rendering, full scene initialization or dynamic archived-time UI.'}
