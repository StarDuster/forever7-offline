"""Static method-structure crosscheck against actual fixed P7 marshal, no exec."""
from pathlib import Path
import hashlib,json
ROOT=Path(__file__).resolve().parents[3]
import sys
sys.path.insert(0,str(ROOT))
from tools import bytecode27


def normalized(value):
 if hasattr(value,'co_code'):
  return {'code':bytes(value.co_code).hex(),'names':list(value.co_names),'varnames':list(value.co_varnames),'args':value.co_argcount,'flags':value.co_flags,'consts':[normalized(c) for c in value.co_consts]}
 if isinstance(value,(tuple,list)):return [normalized(c) for c in value]
 if isinstance(value,bytes):return {'bytes':value.hex()}
 if type(value) in (str,int,float,bool,type(None)):return value
 raise ValueError(type(value))


def method(code,name):
 found=[]
 def walk(c):
  if c.co_name==name:found.append(c)
  for child in c.co_consts:
   if hasattr(child,'co_code'):walk(child)
 walk(code)
 if len(found)!=1:raise ValueError('method selection not unique')
 return found[0]


def verify():
 selections={'cocos/comps/card_common/item_box':['set_info'],
             'game_scene/city_chouka':['get_summon_type'],
             'cocos/panels/card_open':['notify_scene_card_preview','notify_show2','notify_card_open'],
             'entity/avatar_members/LuckyDrawMember':['replyFile','replyLuckyDrawCard','showLuckyDrawLianchouRewards']}
 results=[]
 for module,names in selections.items():
  a=ROOT/'analysis/android640-scripts'/(module+'.marshal');b=ROOT/'analysis/project7/scripts'/(module+'.marshal')
  original,p7=bytecode27.read(a),bytecode27.read(b)
  for name in names:
   left=normalized(method(original,name));right=normalized(method(p7,name))
   if left!=right:raise ValueError('actual P7 consumer differs: '+module+':'+name)
   results.append({'module':module,'method':name,'equal':True,'method_structure_sha256':hashlib.sha256(json.dumps(left,sort_keys=True,separators=(',',':')).encode()).hexdigest(),'official_marshal_sha256':hashlib.sha256(a.read_bytes()).hexdigest(),'p7_marshal_sha256':hashlib.sha256(b.read_bytes()).hexdigest()})
 return {'checks':len(results),'results':results,'scope':'Method instruction/constant/name structure matches; P7 module-level extension not executed; scene initialization and native rendering not claimed'}
if __name__=='__main__':print(json.dumps(verify(),indent=2))
