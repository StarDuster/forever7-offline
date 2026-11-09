"""Finite original CG request/consumer source body adaptation; no marshal opcode runs."""
from pathlib import Path
import ast,hashlib,json,sys,textwrap,types
ROOT=Path(__file__).resolve().parents[3]
SOURCE=ROOT/'analysis/original-py-640/entity/avatar_members/OddsAndEndsMember.py'
assert hashlib.sha256(SOURCE.read_bytes()).hexdigest()=='552d9ae8501619968629477590c45a3b0688da42b864da2eca86566bf902afd5'
lines=SOURCE.read_text().splitlines(True)
def original_body(name):
 start=next(i for i,line in enumerate(lines) if line.startswith('    def '+name+'('))
 end=next((i for i in range(start+1,len(lines)) if lines[i].strip() and not lines[i].startswith('        ') and not lines[i].startswith('\n')),len(lines))
 source=textwrap.dedent(''.join(lines[start:end]))
 # Explicit Py3 finite adaptation: remove original diagnostic print only.
 source='\n'.join(line for line in source.splitlines() if not line.lstrip().startswith('print '))+'\n'
 return ast.parse(source)
cases=json.loads(Path(sys.argv[1]).read_text());events=[]
NS=types.SimpleNamespace
ui=NS(lock=lambda tag:events.append(('lock',tag)),unlock=lambda tag:events.append(('unlock',tag)),
 panels=NS(settlement_fullscreen=NS(notify_cg=lambda cg:events.append(('cg',cg))),
 settlement_window=NS(notify_reward=lambda kind,reward:events.append(('reward',kind,reward)))),
 _tree=NS(proc_event=lambda name,**kwargs:events.append(('event',name))))
namespace={'gg':NS(ui=ui),'const':NS(RewardType=NS(MAIL=6))}
for name in ('requestMainlineCgRewards','replyMainlineCgRewards'):
 exec(compile(original_body(name),'<finite-original-cg-source>','exec'),namespace)
Avatar=type('Avatar',(),{name:namespace[name] for name in ('requestMainlineCgRewards','replyMainlineCgRewards')})
client=Avatar();client.oddsAndEndsData=NS(mainline_cg_rewards={})
client.callServerMethod=lambda method,params:events.append(('rpc',method,params))
client.requestMainlineCgRewards(1,11);assert events[0]==('lock','requestMainlineCgRewards')
assert events[1]==('rpc','requestMainlineCgRewards',{'li':1,'cg':11})
events[:]=[]
client.replyMainlineCgRewards(cases['failure']['rs'],cases['failure']['i'])
assert events==[('unlock','requestMainlineCgRewards')] and not client.oddsAndEndsData.mainline_cg_rewards
events[:]=[]
reply=cases['success'];client.replyMainlineCgRewards(reply['rs'],reply['i'])
assert events[0]==('unlock','requestMainlineCgRewards') and events[1]==('cg',11)
assert events[2][0]=='reward' and events[2][2]['item']==[[329,700]] and events[3]==('event','reply_mainlineCgRewards')
assert client.oddsAndEndsData.mainline_cg_rewards=={11:True}
# Duplicate success reply really repeats original cosmetic UI; receipt is not UI exactly-once.
client.replyMainlineCgRewards(reply['rs'],reply['i']);assert len([e for e in events if e[0]=='cg'])==2
# Genuine BSON pair-array reconstructs original dict(intCG->Bool), blocking new local request.
client.oddsAndEndsData.mainline_cg_rewards=dict(cases['profile']['oaed']['mcr']);assert client.oddsAndEndsData.mainline_cg_rewards=={11:True}
events[:]=[];client.requestMainlineCgRewards(1,11);assert events==[]
print('PASS finite original CG request/consumer: genuine BSON reply unlocks; success UI; pair-array; duplicate UI explicitly repeatable')
