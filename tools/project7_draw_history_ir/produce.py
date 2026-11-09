"""Maintainer-only pinned public literal producer. No game imports/network."""
import argparse,hashlib,json,os,struct,tempfile,zlib
from pathlib import Path
from tools.project7_draw_ir.literal_marshal import read
from .codec import canonical,typed
from .compiler import compile_history
PINS={
'chouka_friend':'d25f6c53a8cdc89a571bf917b3cfa87960e0b850c10135c967db6534312d1487',
'chouka_friend_default':'4a4021b5d5d21973e20a2f428dba2eae3895172367dd9287d1ff52193892334f',
'furniture_delivery':'f5dd05449f73541a45a709b81b10d31c31d3d66ab90f6393cde1874c8c6c97a5',
'chouka_info':'b0c2d54fabf49da649a1102d65e3417acfd9d25e94fb91ff603ebfd7f5eecc32',
'chouka_normal':'936b936c59212bba1eaffd910505354b8913f85ba38401d3463a65195a7e4c32',
'chouka_default':'d21e19de8ab9911e3face6f8e0e1c869224fb9da76764de23545820270ef6a59',
'reward_random':'8680b7d5a5e1befa9011647317c88fdaf63aff80889c36ed44f249678cd46262',
'reward_common':'e6433f6a6d521fa57fb98a3d49c3f5194f9c5268ecaf24e114b70e9e89114c29',
'item_data':'b498b2fc3f850d416fba2c7c9fb3930ddee680f30cd0d6eb5fb6f59c3ca114b6',
'hero_self_choose_info':'664378ac922d2f0b288d8f70530ab92303de9f080d4e463dbbd9cda066c4aeb6',
'hero':'5fd8f55649e12030a76ec34d50fcf10b414fc07cb8055437177be8ecf29f771e',
'chouka_hero_file':'3acfd4335b3a8b0e7e32c051712c2e172c553c20155c8faf89503641238725a0',
'hero_treasure_generate':'771ceb6415660c9b9650b458f5b988ffb48c4cbf1344d059723a8affbd92b6b6'}
sha=lambda data:hashlib.sha256(data).hexdigest()

def produce(source,output):
 output=Path(output)
 if output.exists():raise FileExistsError(output)
 tables={};sources={}
 for name,pin in PINS.items():
  p=Path(source)/(name+'.marshal')
  if not 0<p.stat().st_size<=32*1024*1024:raise ValueError('source size limit '+name)
  raw=p.read_bytes()
  if sha(raw)!=pin:raise ValueError('unsupported source SHA '+name)
  tables[name]=read(p);sources[name]={'marshal_sha256':pin,'marshal_size':len(raw),'rows':len(tables[name]),'projection_sha256':sha(canonical(typed(tables[name])))}
 ir=compile_history(tables);data=canonical(ir)+b'\n'
 compressor=zlib.compressobj(9,zlib.DEFLATED,-15)
 packed=b'\x1f\x8b\x08\x00\x00\x00\x00\x00\x02\xff'+compressor.compress(data)+compressor.flush()+struct.pack('<II',zlib.crc32(data),len(data))
 contract={'schema':1,'sources':sources,'artifact':{'path':'history-ir.json.gz','sha256':sha(packed),'size':len(packed),'uncompressed_sha256':sha(data),'uncompressed_size':len(data)},'summary':ir['summary'],'scope':'readonly data only; no player state/runtime pool integration'}
 output.parent.mkdir(parents=True,exist_ok=True)
 with tempfile.TemporaryDirectory(dir=output.parent) as t:
  stage=Path(t)/'data';stage.mkdir()
  for name,blob in {'history-ir.json.gz':packed,'contract.json':canonical(contract)+b'\n','capabilities.json':canonical({'summary':ir['summary'],'pools':[{k:r[k] for k in ['wire_t','kind','rpc_family','capability','mechanism_tags','issues']} for r in ir['ui_pools']]})+b'\n'}.items():
   with (stage/name).open('xb') as f:f.write(blob);f.flush();os.fsync(f.fileno())
  if output.exists():raise FileExistsError(output)
  os.rename(stage,output)
 return contract
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--source-dir',required=True,type=Path);p.add_argument('--output',required=True,type=Path);a=p.parse_args();print(json.dumps(produce(a.source_dir,a.output),indent=2))
