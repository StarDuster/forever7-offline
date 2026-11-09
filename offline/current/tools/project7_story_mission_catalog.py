"""Source-bound normal chapter family and released TRUNK trial public projection.
Only literal original tables and the pinned original JVM calculator are evaluated.
No profile import, Store write, D8, APK, game or emulator.
"""
import _bootstrap  # noqa: E402,F401
from pathlib import Path
import argparse,base64,hashlib,json,subprocess,sys,tempfile,math
from _bootstrap import ROOT;OUT=ROOT/'offline/current/data/project7_story_mission_catalog'
PINS={'mission':'2019aab0289ffdac6aacde82b21cd283ef0c8d8afb6bb264d087e8cde262390f','mission_hero_attr':'25647eaa103bb23bc22c27910e1f119e7ed2f169f52ac440dee69f573a60cc8b','chapter_mission_data':'c637bbf1665c8118b238c702145a22df0ceaf860bdf80595edbcf0d20882cdb4','event_content':'0ddb80bbe56259a2f54acdb7accef49ad390240b0cac504ba1375a3c8976afe7'}
JAR=ROOT/'analysis/project7/reliable-scope-hook-v1/manager-translated-frames.jar';MANAGER='248375abc553e42def8906ad43e4364e81bba13df694dbb355c61ebfbde90ce4'
BASELINE_PINS={'economy.tsv':'46ece8bf692c0446c95e8a56d3ab514ef7f90e65dde1f0c48e2c29177a56b19d','suppression.tsv':'f77f4c691408bfa41ed1685e9813a02441e4ca87fa0c77ef67d277e0ff705777'}
EXTRA_PINS={'economy-extra.tsv':'79474d999f2e796213a61207bed5cc1d4a2faae1a2ab62ec555e9af649ad2f85','suppression-extra.tsv':'80ae9aa4824b766d332d15bc40f0d5d0c871b874ac0cf12af929e9fe2176e3c7'}
def canonical(x):
 if isinstance(x,dict):return {k:canonical(v)for k,v in sorted(x.items())}
 if isinstance(x,(list,tuple)):return [canonical(v)for v in x]
 return x
def sha(b):return hashlib.sha256(b).hexdigest()
def require(v,m):
 if not v:raise ValueError(m)
def run(*args):
 p=subprocess.run(list(map(str,args)),capture_output=True,text=True);require(p.returncode==0,p.stdout+p.stderr);return p.stdout

def literal(path):
 from bytecode27 import read
 from xdis.bytecode import Bytecode
 from xdis.opcodes import opcode_27
 aliases={'TD':'literal_dict','set':'literal_set','True':True,'False':False,'None':None}
 stack=[];started=False
 for number,ins in enumerate(Bytecode(read(path),opcode_27)):
  if number>=4000000 or len(stack)>200000:raise ValueError('Literal bound')
  op,count=ins.opname,ins.arg or 0
  if not started:
   if op=='STORE_NAME' and ins.argval=='_reload_all':started=True
   continue
  if op=='LOAD_CONST':stack.append(int(ins.argval) if isinstance(ins.argval,int) and type(ins.argval) is not bool else ins.argval)
  elif op=='LOAD_NAME':stack.append(aliases[ins.argval])
  elif op=='STORE_NAME':aliases[ins.argval]=stack.pop()
  elif op in ('BUILD_TUPLE','BUILD_LIST','BUILD_SET'):
   values=stack[-count:] if count else []
   if count:del stack[-count:]
   stack.append(tuple(values) if op=='BUILD_TUPLE' else set(values) if op=='BUILD_SET' else list(values))
  elif op=='BUILD_MAP':stack.append({})
  elif op=='STORE_MAP':
   key,value=stack.pop(),stack.pop();stack[-1][key]=value
  elif op=='BINARY_SUBSCR':
   key,value=stack.pop(),stack.pop();stack.append(value[key])
  elif op=='UNARY_NEGATIVE':stack.append(-stack.pop())
  elif op=='CALL_FUNCTION':
   if count not in (0,1):raise ValueError('Nonliteral call arity')
   value=stack.pop() if count else None;fn=stack.pop()
   if fn=='literal_dict' and count==1 and isinstance(value,dict):stack.append(dict(value))
   elif fn=='literal_set' and (count==0 or isinstance(value,(list,tuple,set))):stack.append(set(value or ()))
   else:raise ValueError('Nonliteral constructor')
  elif op=='RETURN_VALUE':
   if not isinstance(aliases.get('data'),dict):raise ValueError('No literal data')
   def validate(value,depth=0):
    if depth>100:raise ValueError('Literal nesting bound')
    if value is None or type(value) in (str,bool,int,float):return
    if isinstance(value,dict):
     for k,v in value.items():validate(k,depth+1);validate(v,depth+1)
    elif isinstance(value,(tuple,list,set)):
     for v in value:validate(v,depth+1)
    else:raise ValueError('Nonliteral value type')
   validate(aliases['data'])
   return aliases['data']
  else:raise ValueError('Nonliteral opcode '+op)
 raise ValueError('Truncated literal data')

def project(directory):
 sys.path.insert(0,str(ROOT))
 from bson import BSON,ObjectId
 pins={};tables={};previous=json.loads((OUT/'pins.json').read_text())if(OUT/'pins.json').exists()else {}
 def load(n):
  if n not in tables:
   p=directory/(n+'.marshal');b=p.read_bytes();digest=sha(b);expected=PINS.get(n,previous.get('source_pins',{}).get(n));require(expected is None or digest==expected,'Source changed '+n);pins[n]=digest;tables[n]=literal(p)
  return tables[n]
 mission,heroes,chapters,events=(load(n)for n in ('mission','mission_hero_attr','chapter_mission_data','event_content'))
 trials={r['enterBattle']:eid for eid,r in events.items() if r.get('release') and r.get('eventType')==1 and r.get('enterBattle') in mission and mission[r['enterBattle']].get('release')==1 and mission[r['enterBattle']].get('system_type')==4 and mission[r['enterBattle']].get('customizeHero')==1}
 require(len(trials)==5,'TRUNK family changed')
 # Exact source-key family. Runtime does not truncate route names or inherit nextstagenums.
 chosen={k:r for k,r in chapters.items() if k[1]==0 and k[3]==0 and k[2].split('-')[0]=='27'}
 # Retain all chapter keys/sections for this route family; selector activates only complete normal singleton rows.
 lines=['P7STORYMISSIONS\t1\texact-route-normal-v1'];provenance=[];economy=[];seens=set();closures={}
 # Original manager has no G row for 3106. Its two source conditions are alternate
 # route prerequisites, not a conjunction. A linear G row cannot encode OR, so
 # admission remains the area/current-stage gate for both branches.
 BRANCH_OR_GATES={3106:(3105,3114)}
 def inherited(scene,chain=()):
  require(scene not in chain,'Mission inheritance cycle');r=mission[scene];parent=r.get('inherit_mission');base=inherited(parent,chain+(scene,)) if parent else {};return dict(base,**r)
 for key,row in sorted(chosen.items()):
  require(key==(row['chapter'],row['specialStage'],row['route'],row['status']),'Chapter key/body conflict')
  groups=row['section'];require(set(groups)==set(range(10)),'Section indices')
  values=[s for i in range(10)for s in groups[i]]
  # Other battle-mode families remain exported in public source JSON but are not activated by this normal-stage policy.
  if not values or any(len(groups[i])>1 for i in range(10)) or any(mission[s].get('system_type')!=1 or mission[s].get('release')!=1 for s in values):continue
  lines.append('\t'.join(map(str,('C',*key,';'.join(','.join(map(str,groups[i]))for i in range(10))))))
  provenance.append({'key':list(key),'sections':{str(i):list(groups[i])for i in range(10)}})
  for s in values:
   if s in seens:continue
   seens.add(s);r=inherited(s);require(r['ch']==key[0],'Mission/chapter area conflict');chain=[];cur=s
   while True:
    require(cur not in chain,'Inheritance cycle');chain.append(cur);parent=mission[cur].get('inherit_mission')
    if not parent:break
    require(parent in mission,'Missing inherited mission');cur=parent
   fields=[r.get(n,d)for n,d in [('va',0),('fatigue',0),('overFatigue',0),('force_recommend',0),('least_hero_num',1),('max_hero_num',3),('prize',1)]]
   require(all(type(v)is int and v>=0 for v in fields),'Economy numeric source')
   economy.append('\t'.join(map(str,('M',s,*fields))))
   # Keep source cond_event/cond only. Do not carry parent nextstagenums into new branch sequencing.
   cond=r.get('cond',());event=r.get('cond_event',0)
   if (event or cond) and not (s in BRANCH_OR_GATES and tuple(cond)==BRANCH_OR_GATES[s]):economy.append('\t'.join(map(str,('G',s,event,*cond))))
   lines.append('A\t%d\t%d'%(s,r['ch']));closures[str(s)]={'chain':chain,'row':r,'economy':fields,'odds':r.get('odds',()),'rewardPool':r.get('rewardPool'),'prize':r.get('prize',1)}
 # Detached source trial equipment profiles are calculator inputs only, never stored.
 require(sha(JAR.read_bytes())==MANAGER,'Original manager changed');assets=ROOT/'analysis/project7/manager/assets';base_supp=(assets/'suppression.tsv').read_bytes();base_econ=(assets/'economy.tsv').read_bytes();generators=load('hero_treasure_generate');baseheroes=load('hero');starattrs=load('hero_star_attr');monsters=load('monster')
 build=Path(tempfile.mkdtemp(prefix='story-catalog-',dir=ROOT/'analysis/project7'));ins=build/'inputs';outs=build/'outputs';classes=build/'classes';platform=build/'platform';ins.mkdir();outs.mkdir();classes.mkdir();platform.mkdir()
 trialsource={};actor_source={};keys=[]
 # Existing source-derived MH oracle is recalculated by the same projector, catching incomplete mapping.
 oracle=next((k for k in heroes if k==(418,10)),None);require(oracle,'Missing original MH oracle')
 for scene in sorted(set(trials)|{oracle[0]}):
  party=mission[scene]['defaultHeroes'] if scene in trials else (oracle[1],)
  if scene in trials:
   m=mission[scene];require(m['least_hero_num']<=len(party)<=m['max_hero_num'],'Source party bounds');lines.append('\t'.join(map(str,('T',scene,trials[scene],','.join(map(str,party)),m['least_hero_num'],m['max_hero_num'],m.get('retry_times',0)))))
   source=m['dataSource'];spawns=load('refresh_monster_'+source);levels={monsters[r['protoid']].get('level',1)for r in spawns.values()};require(len(levels)==1,'Mixed source monster levels need exact unit policy');monster_level=next(iter(levels));trialsource[str(scene)]={'event':trials[scene],'mission':m,'monster_source':source,'monster_base_level':monster_level,'actors':{}}
  for hero in party:
   r=heroes[scene,hero];require(r['mission_id']==scene and r['heroid']==hero,'MH identity');items=[];refs=[]
   for i,e in enumerate(r['treasure']):
    require(set(e)=={'item_gen_id'},'Unsupported trial equipment generator');g=generators[e['item_gen_id']];item=json.loads(g['dumps_info']);require(item['i']==g['itemid'],'Item generator identity');item['tr']['x']=g.get('treasure_exp',0);item['tr']['lv']=r['level'];item['u']=ObjectId('%024x'%(i+1));items.append(item);refs.append({'generator':e['item_gen_id'],'row':g})
   ar=r['artifact'];lib=r.get('liberate',0);hd={'sl':r['starLevel'],'so':r['starOrder'],'oa':bool(ar['order']),'ar':{'o':ar['order'],'oa':ar['attrs'],'il':0},'ti':{'items':items},'ls':4 if lib else 0,'lh':lib,'la':lib,'ld':lib,'as':r.get('awake',0)}
   (ins/f'{scene}-{hero}-{r["level"]}.bson').write_bytes(BSON.encode({'level':r['level'],'heromgr':{'hrs':[[hero,hd]]}}));keys.append((scene,hero));actor_source[scene,hero]=r
   if scene in trials:trialsource[str(scene)]['actors'][str(hero)]={'row':r,'equipment':refs}
 j=ROOT/'toolchains/java/jdk-17.0.21+9/Contents/Home/bin';sdk=ROOT/'toolchains/android-sdk/platforms/android-32/android.jar';run(j/'javac','--release','8','-cp',JAR,'-d',classes,ROOT/'offline/current/java/android_story_missions/host_tests/com/project7/localmanager/TrialProjector.java')
 # Host calculator loads Context symbols; use compile-only Android classes but never invoke Android API.
 run(j/'java','-Xverify:all','-cp',':'.join(map(str,[JAR,sdk,classes,ROOT/'toolchains/json-20240303.jar'])),'com.project7.localmanager.TrialProjector',assets,ins,outs)
 suppression=[];projected={}
 base_map={tuple(r.split('\t')[:2]):r for r in base_supp.decode().splitlines()if r and not r.startswith('#')}
 attrs={'_base_max_hp':('_hp_delta','star_factor_base_max_hp',1),'_base_phy_att_str':('_phy_str_delta','star_factor_base_phy_att_str',0),'_base_mag_att_str':('_mag_str_delta','star_factor_base_mag_att_str',0),'_base_phy_def':('_phy_def_delta','star_factor_base_phy_def',0),'_base_mag_def':('_mag_def_delta','star_factor_base_mag_def',0)}
 from project7_story_mission_catalog.source_calculator import project_actor
 calc_cache={};oracle_difference={}
 for scene,hero in keys:
  r=actor_source[scene,hero];a=project_actor(r,generators,load,calc_cache)
  require(set(a)=={'id','lv','d','a','s','t','ai','as'} and a['d'] and a['s'][0],'Complete original MH schema')
  if scene==oracle[0]:
   expected=BSON(base64.b64decode(base_map['MH',f'{scene}:{hero}'].split('\t')[2])).decode();require(set(a)==set(expected),'Original MH schema oracle');require(set(a['d'])==set(expected['d']) and all(math.isclose(a['d'][k],v,rel_tol=1e-12,abs_tol=1e-8)for k,v in expected['d'].items()),'Original640 calculator numeric oracle');require(set(a['t'])==set(expected['t']) and all(a[k]==expected[k]for k in ('id','s','ai','as','lv','a')),'Original640 skills/tricks/artifact oracle');oracle_difference={'source640':a,'stock_old':expected,'note':'Original640 source methods numerically match existing418/10 within 1e-12, exact skills/artifact/exclusive and tricks set. Ordering and roundoff may differ.'};continue
  projected[f'{scene}:{hero}']=a;suppression.append('MH\t%d:%d\t%s'%(scene,hero,base64.b64encode(BSON.encode(canonical(a))).decode()))
 for scene in sorted(trials):
  m=mission[scene];levels={heroes[scene,h]['level']for h in m['defaultHeroes']};require(len(levels)==1,'Mixed trial hero levels');mc={'adjust_hero_lv':next(iter(levels))};mc.update({k:m[k]for k in ('adjust_hero_lv','adjust_monster_lv')if k in m});suppression.append('MC\t%d\t%s'%(scene,base64.b64encode(BSON.encode(mc)).decode()));lv=trialsource[str(scene)]['monster_base_level'];sm={'first':lv,'second':lv};suppression.append('SM\t%d\t%s'%(scene,base64.b64encode(BSON.encode(sm)).decode()))
 def append(base,rows):
  require(base.endswith(b'\n'),'Baseline line boundary');existing={tuple(r.split('\t')[:2]):r for r in base.decode().splitlines()if r and not r.startswith('#')};added=[]
  for row in rows:
   key=tuple(row.split('\t')[:2]);require(key not in existing or row==existing[key],'Conflicting public catalog row '+str(key))
   if key not in existing:existing[key]=row;added.append(row)
  return base+(''.join(r+'\n'for r in added)).encode()
 require(not previous.get('calculator_source_pins') or all(calc_cache['files'].get(k)==v for k,v in previous['calculator_source_pins'].items()),'Original calculator source changed')
 public={'schema':1,'chapters':provenance,'missions':closures,'trial_source':trialsource,'projected_trials':projected,'calculator_source_pins':calc_cache['files'],'old_mh_schema_oracle':oracle_difference,'source_pins':pins,'projection_policy':'Original640 calculator function bodies; generator explicit treasure_exp and actor level for detached equipment is named offline policy trial-equipment-at-actor-level-v1; old418 MH is schema oracle only. No inventory import.'}
 results={'catalog-v1.tsv':('\n'.join(lines)+'\n').encode(),'economy-extra.tsv':append(base_econ,economy)[len(base_econ):],'suppression-extra.tsv':append(base_supp,suppression)[len(base_supp):],'public-source-v1.json':(json.dumps(public,ensure_ascii=False,sort_keys=True,indent=2)+'\n').encode()}
 manifest={'schema':1,'calculator_source_pins':calc_cache['files'],'source_pins':pins,'manager_sha256':MANAGER,'baseline_assets':{n:sha((assets/n).read_bytes())for n in ('economy.tsv','suppression.tsv','combat_skills.tsv','combat_attrs.tsv','growth.tsv','home.tsv')},'outputs':{n:sha(v)for n,v in results.items()},'chapters':len(provenance),'missions':len(seens),'trials':len(trials),'host_build':str(build.relative_to(ROOT)),'policy':'exact-route-normal-v1; no implicit route creation; retry_times source metadata only; no retry terminal policy'}
 return results,manifest

def extend_asset(baseline:bytes,name:str)->bytes:
 """Append source-bound rows to the exact original public asset; no in-place edits."""
 require(name in ('economy.tsv','suppression.tsv'),'Unsupported story asset')
 manifest=json.loads((OUT/'pins.json').read_text());extra_name=name.replace('.tsv','-extra.tsv');extra=(OUT/extra_name).read_bytes()
 require(sha(baseline)==BASELINE_PINS[name]==manifest['baseline_assets'][name],'Story asset baseline pin changed '+name)
 require(sha(extra)==EXTRA_PINS[extra_name]==manifest['outputs'][extra_name],'Story increment pin changed')
 require(baseline.endswith(b'\n'),'Story baseline line boundary')
 rows={tuple(r.split('\t')[:2]):r for r in baseline.decode().splitlines()if r and not r.startswith('#')}
 for r in extra.decode().splitlines():
  key=tuple(r.split('\t')[:2]);require(key not in rows,'Story row conflict '+str(key));rows[key]=r
 return baseline+extra

def main():
 p=argparse.ArgumentParser();p.add_argument('--cdata',type=Path);p.add_argument('--write',action='store_true');a=p.parse_args()
 if a.write:
  require(a.cdata,'Explicit original public cdata required');results,m=project(a.cdata);OUT.mkdir(exist_ok=True)
  for n,b in results.items():(OUT/n).write_bytes(b)
  (OUT/'pins.json').write_text(json.dumps(m,indent=2)+'\n')
 else:
  m=json.loads((OUT/'pins.json').read_text())
  for n,digest in m['outputs'].items():require(sha((OUT/n).read_bytes())==digest,'Bundled public data changed '+n)
 print('PASS source-bound story mission catalog')
if __name__=='__main__':main()
