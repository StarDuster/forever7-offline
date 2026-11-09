"""Read-only finite original UI fee consumers for362/488; never install into a game.
Uses existing frozen history UI adapter with an explicit test-only ready policy.
"""
from pathlib import Path
import importlib.util,json,sys,types,hashlib
ROOT=Path(__file__).resolve().parents[3]
def verify():
 spec=importlib.util.spec_from_file_location('dynamic_fee_fixture',ROOT/'tests/test_project7_draw_ui.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
 fixture=m.HistoryUITests();fixture.setUp();checks=0
 try:
  policy=json.loads(fixture.policy_text);policy['ready_ids']=sorted(set(policy['ready_ids'])|{362,488});fixture.policy_text=json.dumps(policy);m.policy._HISTORY_POLICY=hashlib.sha256(json.dumps(policy,sort_keys=True,separators=(',',':')).encode('ascii')).hexdigest();state=fixture.install();actor=fixture.gg.avatar;data=actor.luckyDrawData;view=m.policy._HistoryAvatar(actor,state)
  old_spec=importlib.util.spec_from_file_location('dynamic_fee_original',ROOT/'runtime/android_draw_policy/host_tests/verify_original_consumers.py');old=importlib.util.module_from_spec(old_spec);old_spec.loader.exec_module(old)
  path='analysis/original-py-640/entity/avatar_attrs/LuckyDrawData.py'
  Activity=type('ActivityData',(),{'__init__':old.function(path,'__init__',fixture.env),'initFromDict':old.function(path,'initFromDict',fixture.env)})
  fixture.env['LuckyDrawData']=types.SimpleNamespace(ActivityData=Activity);fixture.gg.ui._tree=types.SimpleNamespace(proc_event=lambda *a,**k:None);fixture.gg.ui.panels.card_box=types.SimpleNamespace(on_reply_request_file=lambda *a:None)
  slot_spec=importlib.util.spec_from_file_location('dynamic_fee_methods',Path(__file__).with_name('verify_slot_projection.py'));slot=importlib.util.module_from_spec(slot_spec);slot_spec.loader.exec_module(slot)
  init=slot.method('analysis/original-py-640/entity/avatar_members/LuckyDrawMember.py','syncLuckyDrawActivityData',fixture.env);resume=old.function('analysis/original-py-640/entity/avatar_members/LuckyDrawMember.py','replyFile',fixture.env)
  for t in (362,488):
   assert fixture.original_rows[t]['consume_without_normal'];assert data.canOpenCardByConsume(t)is False;checks+=2
   assert view.checkCanRequestLuckyDrawFile(t)is True;view.requestLuckyDrawFile(t);view.requestLuckyDrawFileAndOpenAll(t);checks+=3
   init(actor,t,{'ct':6,'iof':True,'cctd':0});resume(actor,True,{str(i):{'index':i,'is_open':False}for i in range(6)},t)
   assert t in data.activity_data and len(data.activity_data[t].draw_info)==6;checks+=1
   view.requestFile(t);view.requestLuckyDrawCard(0,t);view.requestLuckyDrawAllLeftCard(t);view.requestQuitFile(t);checks+=4
   methods=[call[1]for call in fixture.calls if call[0]=='rpc'and call[2].get('t')==t]
   assert set(methods)=={'requestLuckyDrawFile','requestLuckyDrawFileAndOpenAll','requestFile','requestLuckyDrawCard','requestLuckyDrawAllLeftCard','requestQuitFile'},methods;checks+=1
   assert actor.summonCoin==0 and actor.yuanbao==0 and actor.giftCoin==7 and fixture.original_rows[t]['consume_without_normal']==1;checks+=1
  assert view.checkCanRequestLuckyDrawFile(1)is False;checks+=1
  return {'checks':checks,'ids':[362,488],'actual_ready_policy_test_only':True,'production_ui_modified':False,'scope':'actual original LuckyDrawMember/Data request fee methods, sync ActivityData and replyFile with existing history-free scoped adapter; inert network/UI, not whole scene/native acceptance'}
 finally:fixture.doCleanups()
if __name__=='__main__':print(json.dumps(verify(),sort_keys=True))
