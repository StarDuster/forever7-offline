"""Finite original640 calculator bodies for public detached trial projection.
Only named source classes/functions are compiled; imports/game module code never run.
"""
import ast,copy,math,types,hashlib,collections.abc
from pathlib import Path
from lib2to3.refactor import RefactoringTool
ROOT=Path(__file__).resolve().parents[4]
FIX=RefactoringTool(['lib2to3.fixes.fix_print','lib2to3.fixes.fix_except','lib2to3.fixes.fix_dict','lib2to3.fixes.fix_xrange','lib2to3.fixes.fix_map','lib2to3.fixes.fix_long','lib2to3.fixes.fix_numliterals'])
def calculators(load):
 N=types.SimpleNamespace;p=ROOT/'analysis/original-py-640';files={};trees={}
 def tree(name):
  if name not in trees:
   path=p/name;raw=path.read_bytes();files[name]=hashlib.sha256(raw).hexdigest();trees[name]=ast.parse(str(FIX.refactor_string(raw.decode(),str(path))))
  return trees[name]
 def cls(name,source):return next(n for n in tree(source).body if isinstance(n,ast.ClassDef)and n.name==name)
 def table(name):return N(data=load(name))
 env={'math':math,'collections':N(Mapping=collections.abc.Mapping)}
 util=copy.deepcopy(next(n for n in tree('com/utils/utils.py').body if isinstance(n,ast.FunctionDef)and n.name=='dict_add'));exec(compile(ast.fix_missing_locations(ast.Module(body=[util],type_ignores=[])),str(p/'com/utils/utils.py')+':dict_add','exec'),env);env['utils']=N(dict_add=env['dict_add'])
 const=N();env['const']=const
 for name in ('CombatAttrs','CalcTreasureFixAttr','ItemType','TradeType'):
  c=copy.deepcopy(cls(name,'com/const.py'));exec(compile(ast.fix_missing_locations(ast.Module(body=[c],type_ignores=[])),str(p/'com/const.py'),'exec'),env);setattr(const,name,env[name])
 mapping={'HeroDataMod':'hero','StarAttrDataMod':'hero_star_attr','StarSkillDataMod':'hero_star_skill','ArtifactAttrDataMod':'hero_artifact_attr','HeroPointData':'hero_artifact_allot_lv_point_data','ArtifactIncreaseDataMod':'artifact_increase','LIBERATE_TUPO':'liberate_tupo','LIBERATE_LV':'liberate_lv','TreasureDataMod':'hero_treasure','TreasureThirdAttrData':'hero_treasure_third_attr','TreasureExclusiveDataMod':'treasure_exclusive','TreasureSuitDataMod':'hero_treasure_suit','ITEM_DATA':'item_data'}
 for key,name in mapping.items():env[key]=table(name)
 env['gg']=N(avatar=N(level=1));types_out={}
 specs=[('ArtifactData','entity/avatar_attrs/HeroMgrData.py',['getOrderAttrSpecialPointInfo','calcAttr']),('HeroData','entity/avatar_attrs/HeroMgrData.py',['calcAllAttr','calcBaseAttr','calcStarAttr','calcArtifactAttr','calcTreasureAttr','getTreasureDisplayAttr','getTreasureSuit','countLiberateFixMaxLevel','caleLiberateAttr','getStarSkill','getArtifactSkill','getTreasureTricks','calcSkill']),('ItemData','entity/avatar_attrs/ItemData.py',['initFromDict','loadTreasure','updateTreasureStar','getTreasureExpData','_calcTreasureFixAttr','_calcTreasureThirdAttr','_calcTreasureExtraRandomAttr','_handleTreasureDeltaAttr','calcTreasureAttr'])]
 for name,path,methods in specs:
  c=type(name,(),{});types_out[name]=c;source=cls(name,path)
  for method in methods:
   fn=copy.deepcopy(next(n for n in source.body if isinstance(n,ast.FunctionDef)and n.name==method));fn.decorator_list=[];exec(compile(ast.fix_missing_locations(ast.Module(body=[fn],type_ignores=[])),str(p/path)+':'+method,'exec'),env);setattr(c,method,env[method])
 Hero=types_out['HeroData'];Hero.calcJibanTreasureAttr=lambda self:{};Hero.calcRoomSkillAttr=lambda self,attrs:({},None);Hero.getAwakedSkill=lambda self:[]
 return types_out,env,files

def project_actor(fixed,generators,load,cache):
 if not cache:cache.update(zip(('types','env','files'),calculators(load)))
 typ,env=cache['types'],cache['env'];Hero,Artifact,Item=(typ[n]for n in ('HeroData','ArtifactData','ItemData'));hero=Hero();hero.heroid=fixed['heroid'];hero.starLevel=fixed['starLevel'];hero.starOrder=fixed['starOrder'];level=fixed['level'];env['gg'].avatar.level=level
 artifact=Artifact();artifact.owner=hero;artifact.order=fixed['artifact']['order'];artifact.orderAttrs=dict(fixed['artifact']['attrs']);artifact.increase_lv=0;hero.artifact=artifact;lib=min(fixed.get('liberate',0),hero.countLiberateFixMaxLevel(level));hero.liberateHpLevel=hero.liberateAttackLevel=hero.liberateDefendLevel=lib;hero.treasureInv=types.SimpleNamespace(inv=[])
 for index,entry in enumerate(fixed['treasure']):
  import json
  g=generators[entry['item_gen_id']];payload=json.loads(g['dumps_info']);payload['u']='trial-source-%d'%index
  # Source generator supplies explicit exp; fixed reply policy scales detached equipment
  # to the source actor level, matching the stock MH producer convention.
  payload['tr']['x']=g.get('treasure_exp',0);payload['tr']['lv']=level;item=Item();item.treasureClass=payload['tr']['cl'];item.initFromDict(payload);hero.treasureInv.inv.append(item)
 stars,artifacts=hero.calcSkill();ai=[False,0]
 for item in hero.treasureInv.inv:
  if item.treasureExclusive and item.treasureExpDict.get('stage'):ai=[True,item.treasureExpDict['stage']];break
 return {'id':hero.heroid,'lv':level,'d':hero.calcAllAttr(level,True),'a':{},'s':[[list(p)for p in stars],[list(p)for p in artifacts]],'t':hero.getTreasureTricks(),'ai':ai,'as':0}
