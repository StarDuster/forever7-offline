"""Source-bound Wish UI projection. No admission, game opcode, clock or wallet owner."""
import _bootstrap  # noqa: E402,F401
from pathlib import Path
import hashlib,json,sys,gzip
from _bootstrap import ROOT
if str(ROOT)not in sys.path:sys.path.insert(0,str(ROOT))
from project7_draw_history_ir.codec import untyped
ASSET_SHA='4abad0f105f6b2088632369e5ff86040791640c9724deb85d75c57660a168c91'
IDS=(5,119,126,143,154,164,397,426,445)
ENTRY_SHA='584a2e9abe5b21e2edad9dd4a82be74a697e158b26d55972a51ee8e6ca544905'
def canonical(data):
 # JSON object keys are strings at runtime. Normalize before sorting so a
 # numeric source table key and its parsed embedded form hash identically.
 plain=json.loads(json.dumps(data,ensure_ascii=True,separators=(',',':')))
 return json.dumps(plain,sort_keys=True,ensure_ascii=True,separators=(',',':')).encode('ascii')
def ui_policy(directory=None):
 directory=ROOT/'offline/current/data/project7_wish_catalog' if directory is None else Path(directory)
 p=directory/'catalog-v1.json';raw=p.read_bytes()
 if p.is_symlink()or len(raw)!=1019145 or hashlib.sha256(raw).hexdigest()!=ASSET_SHA:raise ValueError('Fixed wish source binding changed')
 entry_path=next((c for c in (directory.parent/'project7_wish_ui_entry_assets.json.gz', ROOT/'offline'/'current'/'runtime'/'project7_wish_ui_entry_assets.json.gz') if c.is_file()), directory.parent/'project7_wish_ui_entry_assets.json.gz');packed=entry_path.read_bytes()
 if entry_path.is_symlink()or hashlib.sha256(packed).hexdigest()!=ENTRY_SHA:raise ValueError('Wish entry dependency changed')
 entries=json.loads(gzip.decompress(packed));entry_assets={row['id']:row['assets']for row in entries['pools']}
 x=json.loads(raw);wish=untyped(x['wish']);choose=untyped(x['choose']);items=untyped(x['items']);fees=untyped(x['fees']);normal=untyped(x['normals']);pools=[]
 for d in x['dynamic']:
  t=d['pool'];info=untyped(d['raw']);rows={i:r for i,r in wish.items()if r['drawType']==t};jz=[untyped(r['raw'])for r in d['jiaozhi']]
  family='treasure'if t==5 else 'group'if rows else 'up'
  required=['cocos/card_box.csb','cocos/card_common.csb','cocos/common_icon.csb','cocos/common_property.csb','cocos/common_frame.csb']
  if family in('treasure','group'):required+=['cocos/card_yingzhuang.csb','cocos/activity_common_10.csb']
  if jz:required+=['cocos/card_jiaozhi.csb','cocos/image/bbs/activity_39_mask_dispatch.png']
  if family=='treasure':required+=['cocos/activity_102_window.csb']
  if family=='up':required+=['cocos/image/hero/hero_dialogue/%s.png'%h for h in info['check_heroes']]
  if jz:required+=['cocos/image/hero/skill_dazhao/%s.png'%jz[0]['target_hero']]
  pools.append({'id':t,'family':family,'info':info,'jiaozhi':jz,'wish_ids':sorted(rows),'required_assets':sorted(set(required+entry_assets[t])),'cost_policy':'history-free-v1','gift_policy':'history-source-gift-daily-cap-v1'})
 if sorted(p['id']for p in pools)!=list(IDS):raise ValueError('Nine source UI families changed')
 return {'schema':'project7-wish-ui-v1','backend_sha256':ASSET_SHA,'base_sha256':'b439ab44280a959cab8836595b65489fee3fd8482609ed3caa55477a66fd5c16','candidate_ids':list(IDS),'verified_ids':list(IDS),'detail_ids':list(IDS),'public_ready_ids':[],'verification':'finite-original-consumers-and-fixed-assets-not-native-ui','default_wish_scope':1,'entry_sha256':ENTRY_SHA,'ui_comp':entries['ui_comp'],'pools':pools,'wish':wish,'choose':choose,'fees':fees,'normals':normal,'items':items,'display_designs':untyped(x['display_designs']),'policies':x['policies']}
def main():
 import argparse
 p=argparse.ArgumentParser();p.add_argument('--directory',type=Path);p.add_argument('--output',type=Path,required=True);p.add_argument('--maintainer-entry-archive',type=Path);p.add_argument('--maintainer-source',type=Path);a=p.parse_args()
 if bool(a.maintainer_entry_archive)!=bool(a.maintainer_source):p.error('Both explicit maintainer inputs required')
 if a.maintainer_entry_archive:
  print(json.dumps(maintainer_entry_assets(a.maintainer_entry_archive,a.maintainer_source,a.output),sort_keys=True));return
 b=canonical(ui_policy(a.directory))
 with a.output.open('xb')as f:f.write(b)
 print('bytes=%d sha256=%s public=[]'%(len(b),hashlib.sha256(b).hexdigest()))
def maintainer_entry_assets(archive,source,output):
 """Explicit fixed public NPK + pinned literal source producer. No game code."""
 import gzip
 from pathlib import PurePosixPath
 import plistlib,tempfile
 from resource_npk import ResourceArchive,string_id
 from legacy_csb_reader import Reader,field
 from project7_dream_catalog.produce import literal
 if Path(output).exists() or Path(output).is_symlink():raise FileExistsError(output)
 ar=ResourceArchive(archive)
 snapshot=(ROOT/'offline/current/data/project7_resources/project7-resource-snapshot.json.gz').read_bytes()
 if hashlib.sha256(snapshot).hexdigest()!='9ce83088f69bc7480140aef46581e9a8a1748dd3d3d9cf3808d50504a4992da0':raise ValueError('Unsupported resource snapshot')
 snapshot=json.loads(gzip.decompress(snapshot));versions=next(p[1] for p in snapshot['parts'] if p[0]=='cocos');rows={r[0]:r for version,entries in versions for r in entries};read=ar.read;cache={}
 def verified_read(name):
  if name in cache:return cache[name]
  fid=string_id(name.replace('/','\\').lower());entry=ar.entries[fid];row=rows[fid]
  if row[2:6]!=[entry[2],entry[4],entry[3],entry[5]]:raise ValueError('Public resource index mismatch')
  data=read(name)
  if len(data)!=row[4] or hashlib.md5(data).hexdigest()!=row[1]:raise ValueError('Public resource payload mismatch')
  cache[name]=data;return data
 ar.read=verified_read
 mapping=json.loads(ar.read('projplistinfo'));source=Path(source)/'ui_comp_data.marshal';raw=source.read_bytes();
 if hashlib.sha256(raw).hexdigest()!='239075bbd0482fe1c63ae98192e9b92de093ddb32c7b85307ec09128ee594661':raise ValueError('Unsupported UI component source')
 cd=literal(source);catalog_raw=(ROOT/'offline/current/data/project7_wish_catalog/catalog-v1.json').read_bytes()
 if hashlib.sha256(catalog_raw).hexdigest()!=ASSET_SHA:raise ValueError('Wish backend source changed')
 catalog=json.loads(catalog_raw);pools=[];allassets=set();used=set()
 def getassets(name):
  out={'cocos/'+name+'.csb','cocos/projplistinfo'}
  frames=set()
  for plist in mapping.get(name+'.json',[]):
   if string_id(plist.replace('/','\\').lower()) not in ar.entries:continue
   out.add('cocos/'+plist);data=plistlib.loads(ar.read(plist));frames.update(data.get('frames',{}));meta=data.get('metadata',{});texture=meta.get('realTextureFileName',meta.get('textureFileName'))
   if not texture:raise ValueError(('plist lacks texture',plist))
   out.add('cocos/'+str(PurePosixPath(plist).parent/texture))
  if mapping.get(name+'.json'):
   with tempfile.TemporaryDirectory() as d:
    path=Path(d)/'source.csb';path.write_bytes(ar.read(name+'.csb'));tree=Reader(path).read()
   textures=[]
   def walk(n):
    path,kind=field(n,'path'),field(n,'resourceType')
    if path and kind and path['value'] and path['value']!='null':textures.append((path['value'],kind['value']))
    for child in n.get('children',[]):walk(child)
   walk(tree)
   missing={path for path,kind in textures if kind=='1'}-frames
   if missing:raise ValueError(('uncovered source spriteframes',name,sorted(missing)))
   for path,kind in textures:
    if kind=='0':out.add(path if path.startswith('cocos/') else 'cocos/'+path)
  return out
 for p in catalog['dynamic']:
  t=p['pool']
  info=untyped(p['raw']);idx=info.get('room_enter_index');assets=set()
  for core in ('card_tab','card_box','card_common','common_frame','common_property','common_icon','hero_herolist_common'):assets.update(getassets(core))
  if t==5:assets.update(getassets('card_yingzhuang'));assets.update(getassets('activity_102_window'));assets.update(getassets('activity_common_10'))
  if p['jiaozhi']:assets.update(getassets('card_jiaozhi'));assets.update(getassets('activity_common_10'))
  if idx and idx!=7:
   name={-1:'card_activity_61',-3:'card_activity_62',-2:'card_zixuan'}.get(idx,'card_activity_%s'%idx);assets.update(getassets('card_activity_base'));assets.update(getassets(name))
  for i in info.get('ui_idxs',()):
   used.add(i);row=cd[i];name=row['name'];img=row.get('image')
   if img:
    if name in ('hero_1.hero.image','hero_2.hero.image'):assets.add('cocos/image/hero/card/'+img)
    elif name=='title.text_2':assets.add('cocos/image/card/'+img)
    else:raise ValueError(('unresolved image consumer',name))
   if row.get('spine_file'):
    spine='spine/'+row['spine_file'];assets.update({'cocos/'+spine+'.json','cocos/'+spine+'.atlas'});atlas=ar.read(spine+'.atlas').decode('utf8')
    for line in atlas.splitlines():
     if line.strip().endswith(('.png','.jpg')):assets.add('cocos/'+str(PurePosixPath(spine).parent/line.strip()))
  for a in sorted(assets):
   try:ar.read(a.split('/',1)[1])
   except KeyError:raise ValueError(('missing direct reference',t,a))
  allassets.update(assets);pools.append({'id':t,'assets':sorted(assets)})
 out={'schema':'project7-wish-ui-entry-assets-v1','source_ui_comp_sha256':hashlib.sha256(raw).hexdigest(),'ui_comp':{i:cd[i] for i in sorted(used)},'pools':pools}
 b=canonical(out);z=gzip.compress(b,mtime=0)
 if hashlib.sha256(z).hexdigest()!=ENTRY_SHA:raise ValueError('Wish entry dependency projection changed')
 with Path(output).open('xb') as handle:handle.write(z)
 return {'sha256':hashlib.sha256(z).hexdigest(),'size':len(z),'assets':len(allassets),'ui_comp':len(used)}

if __name__=='__main__':main()

if __name__=='__main__':main()
