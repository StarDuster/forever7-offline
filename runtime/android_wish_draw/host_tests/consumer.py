"""Selected whole original640 typed consumers; inert UI/network only."""
import sys,json,types
from pathlib import Path
R=Path(__file__).resolve().parents[3]
s=(R/'runtime/android_baiye_transactions/host_tests/consumer.py').read_text().split("cases=json.loads(Path(sys.argv[1]).read_text())",1)[0]
exec(compile(s,'original-consumer-platform-setup','exec'),globals())
cases=json.loads(Path(sys.argv[1]).read_text());N=types.SimpleNamespace
class Typed(DictArg):
 def __init__(self,n,t):super(Typed,self).__init__(n);self.t=t
 def convert(self,v):
  if type(v)is not self.t:raise ConvertError()
  return v
 def default_val(self):return self.t()
A.replySetChooseTreasure=rpc(3,(Typed('r',int),Typed('t',int),Typed('i',list)))(h.original('analysis/original-py-640/entity/avatar_members/LuckyDrawMember.py','replySetChooseTreasure',env))
A.syncTreasureWishInfo=rpc(3,(Typed('t',int),Typed('tw_id',int),Typed('s',int)))(h.original('analysis/original-py-640/entity/avatar_members/LuckyDrawMember.py','syncTreasureWishInfo',env))
env['const'].LuckyDrawType=N(NORMAL=1,YINGSHE=5)
a.luckyDrawData=N(activity_data={5:N(choose_treasure=[],treasure_wish={})});ui.lock('setChooseTreasure');a.replySetChooseTreasure(cases['success']);assert ui._lock['setChooseTreasure']==0 and a.luckyDrawData.activity_data[5].choose_treasure==[1,1096,1]
a.syncTreasureWishInfo({'t':5,'tw_id':1,'s':0});assert a.luckyDrawData.activity_data[5].treasure_wish=={1:0}
ui.lock('setChooseTreasure');a.replySetChooseTreasure(cases['failure']);assert ui._lock['setChooseTreasure']==0 and a.luckyDrawData.activity_data[5].choose_treasure==[1,1096,1]
print('PASS original typed wish choose success/failure unlock, ctr and tw state')

if len(sys.argv)>2:
 groups=json.loads(Path(sys.argv[2]).read_text())
 A.syncWishGroupInfo=rpc(3,(Typed('t',int),Typed('i',list)))(h.original('analysis/original-py-640/entity/avatar_members/LuckyDrawMember.py','syncWishGroupInfo',env))
 t=groups['wish']['t'];a.luckyDrawData.activity_data[t]=N(wish_info={})
 A.syncWishGroupInfo.rpcmethod.call(a,None,groups['wish'])
 assert a.luckyDrawData.activity_data[t].wish_info==dict(groups['wish']['i'])
 print('PASS original syncWishGroupInfo metadata.call consumes authoritative c/f/a pairs')
