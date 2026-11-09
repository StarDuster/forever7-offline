"""Actual original ReliableRpcMember initial+pre-ACK resend, finite transport seam."""
import sys,json,types,collections
from pathlib import Path
R=Path(__file__).resolve().parents[3]
s=(R/'runtime/android_baiye_transactions/host_tests/consumer.py').read_text().split("cases=json.loads(Path(sys.argv[1]).read_text())",1)[0]
exec(compile(s,'original-rpc-platform-setup','exec'),globals())
env['collections']=collections;timers=[]
gg.exec_delay=lambda delay,callback:timers.append(callback) or callback
gg.exec_cancel=lambda callback:None
for name in('initReliableRpc','_genReliableRpcSeq','callServerMethodReliable','reSendRpc'):
 setattr(A,name,h.original('analysis/original-py-640/entity/avatar_members/ReliableRpcMember.py',name,env))
class IntArg(DictArg):
 def convert(self,v):
  if type(v)is not int:raise ConvertError()
  return v
 def default_val(self):return 0
A.reliableRpcAck=rpc(3,(IntArg('s'),))(h.original('analysis/original-py-640/entity/avatar_members/ReliableRpcMember.py','reliableRpcAck',env))
a.initReliableRpc();a.callServerMethodReliable('setChooseTreasure',{'t':5,'i':1096});a.reSendRpc(1)
assert len(sent)==2 and all(m=='reliableRpcCall' for m,p in sent)
packets=[json.loads(json.dumps(p))for m,p in sent];assert packets[0]==packets[1] and packets[0]['w']['r']==1
A.reliableRpcAck.rpcmethod.call(a,None,{'s':1});a.reSendRpc(1);assert len(sent)==2 and not a.reliableRpcCache
Path(sys.argv[1]).write_text(json.dumps({'pre_ack_packets':packets,'after_ack_extra_packets':0},sort_keys=True)+'\n')
print('PASS original reliable initial + same-seq pre-ACK resend; ACK stops further sends')
