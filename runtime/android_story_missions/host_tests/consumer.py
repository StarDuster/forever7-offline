"""Finite original640 typed admission consumer, explicit rendering seam."""
import importlib.util,json,sys,types
from pathlib import Path
R=Path(__file__).resolve().parents[3];sys.path.insert(0,str(R));N=types.SimpleNamespace
spec=importlib.util.spec_from_file_location('original_ui',R/'tests/test_project7_furniture_ui.py');h=importlib.util.module_from_spec(spec);spec.loader.exec_module(h)
events=[];env={'gg':N(ui=N(unlock=lambda:events.append('unlock'))),'CombatData':N(STATE_OFFLINE=4),'STATE_NONE':0}
D=type('OriginalCombatData',(),{})
for name in ('setState','offlineFaild','offlineStart'):setattr(D,name,h.original('analysis/original-py-640/entity/avatar_attrs/CombatData.py',name,env))
A=type('Avatar',(),{});A.combatOfflineReply=h.original('analysis/original-py-640/entity/avatar_members/CombatMember.py','combatOfflineReply',env)
a=A();a.combatData=D();a.logger=N(info=lambda *args:None);a.battleOfflineOnReply=lambda *args:events.append(('battle',args));cases=json.loads(Path(sys.argv[1]).read_text())
for key in ('empty','wrong','wrong_area'):
 a.combatData.state=4;events.clear();r=cases[key];a.combatOfflineReply(r['t'],r['s'],r['f'],r['h'],r['d'],r['c']);assert events==['unlock'] and a.combatData.state==0
r=cases['success'];events.clear();a.combatData.state=4;a.combatOfflineReply(r['t'],r['s'],r['f'],r['h'],r['d'],r['c']);assert events[0]=='unlock'and events[1][0]=='battle'and a.combatData.scene==315 and a.combatData.heroes==[14]
assert r['c']['hero_lv']==60 and r['c']['monster_lv']==1
print('PASS original640 combatOfflineReply unlock/offlineFaild on actual wrong/empty t0; source315 t2 enters original battle consumer with lv60/monster1')
