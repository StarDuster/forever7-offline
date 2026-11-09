"""Whole original640 buy producer/Done/currency/callback consumers; inert widgets/network."""
import sys,json
from pathlib import Path
R=Path(__file__).resolve().parents[3]
# Reuse only the finite original RPC/UIManager setup, before any exchange case runs.
source=(R/'runtime/android_baiye_transactions/host_tests/consumer.py').read_text();prefix=source.split("cases=json.loads(Path(sys.argv[1]).read_text())",1)[0]
exec(compile(prefix,'original-consumer-platform-setup','exec'),globals())
cases=json.loads(Path(sys.argv[1]).read_text());closed=[]
class Typed(DictArg):
 def __init__(self,n,t):super(Typed,self).__init__(n);self.t=t
 def convert(self,v):
  if type(v)is not self.t:raise ConvertError()
  return v
 def default_val(self):return self.t()
N=types.SimpleNamespace
stores={int(k.split('_')[1]):{'item_num':v['itemid'],'item_sort':1,'use_now':False}for k,v in cases.items()if k.startswith('done_')}
env['ITEM_STORE_DATA']=N(data=stores);env['ITEM_DATA']=N(data={v['item_num']:{}for v in stores.values()});env['SKIN_DATA']=N(data={})
const=env['const'];const.RewardType.MAIL=2;const.CHIRSTMAS_PENDANT_ITEMID=-1;const.ItemStoreSort=N(SORT_SUPERMEMBERSHIP=99,SORT_SPECIAL_LOGIN=98);const.HeroBirthDayConst=N(HERO_BIRTHDAY_GIFTS=set());const.VirtualItemSub=N(CG=99);const.SANDGLASS_ITEM_ID=-2;const.HEIHAN_ITEM_ID=345
A.buyCardMallItem=h.original('analysis/original-py-640/entity/avatar_members/LuckyDrawMember.py','buyCardMallItem',env)
A.replyBuyCardMallItem=rpc(3,(Typed('r',bool),DictArg('i')))(h.original('analysis/original-py-640/entity/avatar_members/LuckyDrawMember.py','replyBuyCardMallItem',env))
args=tuple(Typed(n,list)for n in('d','w','t','m','z'))+(Typed('itemid',int),Typed('num',int),DictArg('result'),Typed('sd',int),Typed('silence',bool))
A.buyCardMallItemDone=rpc(3,args)(h.original('analysis/original-py-640/entity/avatar_members/LuckyDrawMember.py','buyCardMallItemDone',env))
A.updateGiftCoin=rpc(3,(Typed('v',int),))(h.original('analysis/original-py-640/entity/avatar_members/CommonMember.py','updateGiftCoin',env))
a.luckyDrawData=N(daily_item_num={},weekly_item_num={},total_item_num={},monthly_item_num={},restore_zhoumu=lambda z:None)
a.buyCardMallItem(8,1,'card_main');assert sent[-1]==('buyCardMallItem',{'store_id':8,'num':1,'source':'card_main','coin_type':0,'ext':{},'_cbid_':7})
a.updateGiftCoin(cases['gift']);assert a.giftCoin==499 and events[-1]==('update_giftcoin',)
for identity in stores:
 a.replyBuyCardMallItem({'r':True,'i':{}});a.buyCardMallItemDone(cases['done_'+str(identity)])
 assert a.luckyDrawData.daily_item_num[identity]==1 and a.luckyDrawData.total_item_num[identity]==1
 assert events[-1]==('buy_card_mall_item_done',)
assert len(rewards)==8
for identity in(157,158,617):assert cases['done_'+str(identity)]['result']['treasure']
a.carrier(cases['callback']);assert ui._lock['buyCardMallItem']==0 and not gg.avatar_callback_map
before=len(rewards);a.replyBuyCardMallItem({'r':False,'i':{}});assert len(rewards)==before and events[-1]==('hero_birthday_gift_close',)
print('PASS original8 Done ledgers/counters, real giftCoin immediate update, original request/callback unlock and negative no-reward')
