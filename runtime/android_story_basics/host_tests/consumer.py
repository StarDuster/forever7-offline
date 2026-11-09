"""Execute finite original producer/consumer bodies; UI/RPC dispatch are host seams."""
import importlib.util,json,sys,types
from pathlib import Path
R=Path(__file__).resolve().parents[3];sys.path.insert(0,str(R))
spec=importlib.util.spec_from_file_location('original_harness',R/'tests/test_project7_furniture_ui.py');h=importlib.util.module_from_spec(spec);spec.loader.exec_module(h)
N=types.SimpleNamespace;sent=[];events=[]
gg=N(ui=N(_tree=N(proc_event=lambda *a,**kw:events.append(a))))
env={'gg':gg};A=type('Avatar',(),{})
for method,file in [('getShareLink','WeekNumMember'),('replyShareLink','WeekNumMember'),('readDailyWish','StoryMember'),('syncDailyWish','StoryMember')]:setattr(A,method,h.original('analysis/original-py-640/entity/avatar_members/'+file+'.py',method,env))
a=A();a.callServerMethod=lambda m,p:sent.append((m,p));a.storyData=N(dailyWishReaded=False)
P=type('Panel',(),{})
for method in ('set_share_link','check_click'):setattr(P,method,h.original('analysis/original-py-640/cocos/panels/cg_share_review.py',method,dict(env,time=N(time=lambda:10))))
p=P();p.valid=True;p.wait_for_link=True;p.share_link='pending';p.last_click=0;gg.ui.panels=N(cg_share_review=p)
cases=json.loads(Path(sys.argv[1]).read_text());a.getShareLink(7,[281]);assert sent[-1]==('getShareLink',{'e':7,'cg':[281]})
a.replyShareLink(cases['share']['l']);assert p.wait_for_link is False and p.share_link=='' and p.check_click() is False
# Client producer is optimistic. The gateway acknowledges with the existing typed sync.
a.readDailyWish();assert a.storyData.dailyWishReaded is True and sent[-1]==('readDailyWish',{})
r=cases['read'];a.storyData.dailyWishReaded=False;a.syncDailyWish(r['dw'],r['dwh'],r['dwr']);assert a.storyData.dailyWishReaded is True and a.storyData.dailyWish==[1,2] and a.storyData.dailyWishHero==14 and events[-1]==('daily_wish_update',)
print('PASS original share producer/reply/panel: wait released, unavailable link cannot share; original read producer/sync consumer/event')
