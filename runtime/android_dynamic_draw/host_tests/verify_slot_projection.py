"""Finite original640 function probes; inert scene ABI, no renderer/game import."""
import re,ast,contextlib,hashlib,io,json,random,types
from lib2to3.refactor import RefactoringTool,get_fixers_from_package
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];NS=types.SimpleNamespace
FIX=RefactoringTool(get_fixers_from_package('lib2to3.fixes'))
def method(path,name,namespace):
 source=re.sub(r'\basync\b','async_cb',(ROOT/path).read_text())
 tree=ast.parse(str(FIX.refactor_string(source,path)))
 found=[m for c in tree.body if isinstance(c,ast.ClassDef) for m in c.body if isinstance(m,ast.FunctionDef) and m.name==name]
 assert len(found)==1
 node=found[0];node.decorator_list=[];exec(compile(ast.Module(body=[node],type_ignores=[]),path+':selected','exec'),namespace);return namespace[name]
def verify():
 path='analysis/original-py-640/game_scene/city_chouka.py';events=[];cards={str(i):{'index':i,'is_open':False,'sp_card':False,'rand':0,'hero':[],'item':[],'treasure':[],'hero_file':0,'q7DynamicEntropy':'opaque-'+str(i)} for i in range(6)}
 class Model:
  def bind_scene(self,s):pass
  def set_camera(self,c):pass
  def load_model(self,name,**kwargs):events.append(('load',name,kwargs['async_cb']))
 actor=NS(luckyDrawData=NS(get_draw_info=lambda t:cards));gg=NS(avatar=actor,scene_mgr=NS(cache={1:object()}))
 env={'gg':gg,'ui_utils':NS(SceneModel=Model),'random':random}
 scene=NS(get_luckyDraw_type=lambda:485,scene_id=1,scene_cam=object(),normal_card_name=['opaque-back'],specital_card_name=['opaque-special'],model_card_list=[],summon_model_dict={7:(None,'revealed-hero')},get_summon_type=lambda result,exchange=False:(events.append(('resolve-visible',result)) or 7),_on_card_model=lambda *a:events.append(('onmodel',a)))
 load=method(path,'load_card_model',env)
 with contextlib.redirect_stdout(io.StringIO()):load(scene,0)
 assert len(events)==6 and all(e[1]=='opaque-back' for e in events)
 for e in list(events):e[2]()
 assert all(e[1][2] is None for e in events if e[0]=='onmodel')
 cards['2'].update(is_open=True,hero=[147]);events.clear();scene.model_card_list=[]
 with contextlib.redirect_stdout(io.StringIO()):load(scene,0)
 assert sum(e[0]=='resolve-visible' for e in events)==1
 assert sum(e[0]=='load' and e[1]=='revealed-hero' for e in events)==1
 # Reply entry does not inspect reward payload before subsequent card loading.
 ev=[];reply=method(path,'on_reply_request_file',{})
 reply(NS(unload_summon_main_model=lambda:ev.append('unload'),load_card_main_model=lambda:ev.append('load')),True,{'0':cards['0']});assert ev==['unload','load']
 return {'schema':'project7-dynamic-slot-projection-proof-v1','checks':5,'pass':True,'source_sha256':hashlib.sha256((ROOT/path).read_bytes()).hexdigest(),'scope':'actual selected original640 scene load/reply bodies; six unopened opaque cards use generic backside and callback result=None; exactly one opened card uses its committed primary','limits':['inert model ABI, no native rendering','item_box early is_open guard separately static-reviewed','only these entry bodies, not every possible extension consumer']}
if __name__=='__main__':print(json.dumps(verify(),sort_keys=True))
