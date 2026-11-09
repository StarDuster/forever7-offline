"""Whole original fusion producer/consumer and real rpcdecorator callback flow.
Network/render widgets and RPC scalar types are explicit finite host seams.
"""
import importlib.util,json,sys,types
from pathlib import Path
from lib2to3.refactor import RefactoringTool
R=Path(__file__).resolve().parents[3];sys.path.insert(0,str(R))
spec=importlib.util.spec_from_file_location('fusion_original',R/'tests/test_project7_furniture_ui.py');h=importlib.util.module_from_spec(spec);spec.loader.exec_module(h)
N=types.SimpleNamespace;events=[];rewards=[];sent=[]
gg=N(avatar_callback_map={},avatar_callback_need_result={})
env={'gg':gg,'const':N(RewardType=N(EVENT=1)),'utils':N(RotatedIdGenerator=N(genid=lambda:7))}
ui=N(_lock={},recon_lock=0,panels=N(wait=N(notify_show=lambda *a:None,notify_hide=lambda *a:None,cancel_timer=lambda *a:None),settlement_window=N(notify_reward=lambda k,r:rewards.append(r))),_tree=N(proc_event=lambda *a,**k:events.append(a)))
gg.ui=ui
for name in ('lock','unlock'):setattr(ui,name,types.MethodType(h.original('analysis/original-py-640/cocos/ui_manager.py',name,env),ui))
class ConvertError(Exception):pass
class DictArg:
 def __init__(self,n):self.n=n
 def getname(self):return self.n
 def default_val(self):return {}
 def convert(self,v):
  if type(v)is not dict:raise ConvertError()
  return v
env.update(CLIENT_STUB=3,ConvertError=ConvertError,Avatar=type('AvatarArg',(),{}),MailBox=type('MailboxArg',(),{}),_logger=N(warn=lambda*a:None,error=lambda*a:None))
source=(R/'analysis/original-py-640/lib/common/rpcdecorator.py').read_text();source=source[source.index('class RpcMethod('):source.index('\ndef expose_to_client')];exec(str(RefactoringTool(['lib2to3.fixes.fix_print','lib2to3.fixes.fix_except','lib2to3.fixes.fix_xrange']).refactor_string(source,'actual-rpc')),env)
rpc=env['rpc_method'];A=type('Avatar',(),{})
A.callServerMethod=h.original('analysis/original-py-640/entity/ClientAvatar.py','callServerMethod',env)
A.commonItemFusion=h.original('analysis/original-py-640/entity/avatar_members/InvMember.py','commonItemFusion',env)
A.commonItemFusionReply=rpc(3,(DictArg('r'),))(h.original('analysis/original-py-640/entity/avatar_members/InvMember.py','commonItemFusionReply',env))
import textwrap
carrier=(R/'analysis/original-py-640/entity/avatar_members/ReliableRpcMember.py').read_text().splitlines(True);start=next(i for i,line in enumerate(carrier)if line.startswith('    def serverCallbackCarrier('));exec(textwrap.dedent(''.join(carrier[start:start+2])),env)
A.carrier=rpc(3,(DictArg('_r_'),))(env['serverCallbackCarrier'])
a=A();gg.avatar=a;a.server=N(call_server_method=lambda method,params,eid:sent.append((method,dict(params))))
cases=json.loads(Path(sys.argv[1]).read_text())
a.commonItemFusion(10313,10314,2);assert sent[-1]==('commonItemFusionAsk',{'i':10313,'f':10314,'n':2,'_cbid_':7}) and ui._lock['commonItemFusion']==1
a.commonItemFusionReply(cases['success']);assert rewards==[cases['success']['r']] and events[-1]==('commonItemFusion',)
a.carrier(cases['callback']);assert ui._lock['commonItemFusion']==0 and 7 not in gg.avatar_callback_map
before=len(rewards);a.commonItemFusionReply(cases['failure']);assert len(rewards)==before and events[-1]==('commonItemFusion',)
print('PASS actual fusion producer/output count, reward/event consumer, original callback unlock; empty failure no reward')
if len(sys.argv)>2:
 fragment=json.loads(Path(sys.argv[2]).read_text());full=[];closed=[];messages=[]
 env['const'].RewardType.MAIL=2
 gg.ui.panels.settlement_fullscreen=N(notify_reward=lambda kind,r:full.append(r))
 gg.ui.panels.common_message=N(notify_message=messages.append)
 gg.ui.panels.card_memory_patch=N(valid=True,notify_hide=lambda:closed.append('patch'))
 gg.ui.panels.bag_hero_choose=N(valid=True,notify_close=lambda:closed.append('choose'))
 gg.ui.panels.bag_main=N(valid=True,refresh=lambda:closed.append('bag'))
 class BoolArg(DictArg):
  def default_val(self):return False
  def convert(self,v):
   if type(v)is not bool:raise ConvertError()
   return v
 A.requestExchangeSuipianWithItem=h.original('analysis/original-py-640/entity/avatar_members/LuckyDrawMember.py','requestExchangeSuipianWithItem',env)
 A.replyExchangeSuipianWithItem=rpc(3,(BoolArg('rs'),DictArg('i')))(h.original('analysis/original-py-640/entity/avatar_members/LuckyDrawMember.py','replyExchangeSuipianWithItem',env))
 A.invExchangeHeroFragmentAsk=h.original('analysis/original-py-640/entity/avatar_members/InvMember.py','invExchangeHeroFragmentAsk',env)
 A.invExchangeHeroFragmentReply=rpc(3,(BoolArg('r'),DictArg('i')))(h.original('analysis/original-py-640/entity/avatar_members/InvMember.py','invExchangeHeroFragmentReply',env))
 A.syncProgInfo=rpc(3,(DictArg('prog'),))(h.original('analysis/original-py-640/entity/avatar_members/LuckyDrawMember.py','syncProgInfo',env))
 a.invContainByIDs=lambda items:True;a.luckyDrawData=N(hero_file_progress={})
 a.requestExchangeSuipianWithItem(10126,13,1);assert sent[-1]==('requestExchangeSuipianWithItem',{'ii':10126,'hi':13,'fn':1,'_cbid_':7})
 a.syncProgInfo(fragment['prog']);assert a.luckyDrawData.hero_file_progress[13]==1
 for key in ('named_partial','named_duplicate','named_hero'):a.replyExchangeSuipianWithItem(fragment[key])
 assert full[-1]['memoryFrag'][0][0]['get_hero']is True
 before=len(rewards);a.replyExchangeSuipianWithItem(fragment['named_zero']);assert len(rewards)==before+1 and rewards[-1]['item']==[[4255,1]]
 a.carrier(fragment['named_callback']);assert ui._lock['requestExchangeSuipianWithItem']==0
 before=len(full);a.replyExchangeSuipianWithItem(fragment['named_failure']);assert len(full)==before and messages[-1]=='兑换失败'
 sent_before=len(sent);a.invExchangeHeroFragmentAsk(10954,13,1);assert sent[-1]==('invExchangeHeroFragmentAsk',{'i':10954,'h':13,'s':1}) and len(sent)==sent_before+1 and not gg.avatar_callback_map
 a.invExchangeHeroFragmentReply(fragment['select_partial']);assert closed==['patch','choose','bag'] and full[-1]['memoryFrag'][0][0]['frag']==1
 before=len(full);a.invExchangeHeroFragmentReply(fragment['select_failure']);assert len(full)==before and closed==['patch','choose','bag']
 print('PASS original named/select producers, typed memory/owned-list rewards, full hfp sync, exact panel close and named carrier; inv has no callback')
