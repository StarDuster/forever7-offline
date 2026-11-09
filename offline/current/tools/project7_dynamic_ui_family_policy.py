"""Readonly fixed640 family UI projection. No admission or gameplay mutation."""
import _bootstrap  # noqa: E402,F401
import hashlib,json,sys,gzip
from pathlib import Path
from _bootstrap import ROOT
if str(ROOT) not in sys.path:sys.path.insert(0,str(ROOT))
from project7_dynamic_catalog import load,ASSET_SHA256,BASE_SHA
from project7_draw_history_ir.codec import untyped
SCHEMA='project7-dynamic-ui-families-v1'
DISPLAY_SHA='b8b1896980d5beed343923d2f780e17be4d55d1b94875583ad4a58a7a77b67b1'
ENTRY_SHA='bafe6f03ae31043110386e4c51d2f9184fee2433acda29427ca303034bad5573'
ENTRY_NAME='project7_dynamic_ui_families_entry_assets.json.gz'
DISPLAY_PATH=ROOT/'offline/current/runtime/project7_dynamic_ui_families_data.json.gz'
EXPANSION_SHA='04c2881148468bb2d93f6d5fed15b6db88b0684d53c2c94bcf36048269f872cb'
COMMON=('cocos/card_tab.csb','cocos/card_box.csb','cocos/card_common.csb','cocos/common_frame.csb','cocos/common_property.csb','cocos/common_icon.csb','cocos/hero_herolist_common.csb','cocos/res/hkytw5.ttf')
def canonical(value):return json.dumps(value,sort_keys=True,ensure_ascii=True,separators=(',',':')).encode('ascii')
def ui_policy(directory=None,display_path=None):
 directory=ROOT/'offline/current/data/project7_dynamic_catalog' if directory is None else Path(directory)
 x=load(directory);raw=(directory/'expansion-policy-v1.json').read_bytes()
 if hashlib.sha256(raw).hexdigest()!=EXPANSION_SHA:raise ValueError('Family policy binding mismatch')
 if display_path is None:
  display_path=next((c for c in (directory.parent/DISPLAY_PATH.name, ROOT/'offline'/'current'/'runtime'/DISPLAY_PATH.name) if c.is_file()), directory.parent/DISPLAY_PATH.name)
 packed=Path(display_path).read_bytes()
 if len(packed)>100000 or hashlib.sha256(packed).hexdigest()!=DISPLAY_SHA:raise ValueError('Display bundle binding mismatch')
 import zlib
 dec=zlib.decompressobj(31);expanded=dec.decompress(packed,200001)
 if len(expanded)>200000 or not dec.eof or dec.unused_data:raise ValueError('Display bundle bounds')
 display=json.loads(expanded)
 entry_path=next((c for c in (directory.parent/ENTRY_NAME, ROOT/'offline'/'current'/'runtime'/ENTRY_NAME) if c.is_file()), directory.parent/ENTRY_NAME)
 entry_packed=entry_path.read_bytes()
 if hashlib.sha256(entry_packed).hexdigest()!=ENTRY_SHA:raise ValueError('Entry asset binding mismatch')
 decoder=zlib.decompressobj(31);entry_raw=decoder.decompress(entry_packed,100001)
 if len(entry_raw)>100000 or not decoder.eof or decoder.unused_data:raise ValueError('Entry asset bounds')
 entries=json.loads(entry_raw);entry_assets={p['id']:p['assets'] for p in entries['pools']}
 expansion=json.loads(raw);ids=expansion['backend_policy_ids'];pools=[]
 if len(ids)!=46 or len(set(ids))!=46 or 485 not in ids:raise ValueError('Family candidate set changed')
 for p in x['pools']:
  t=p['pool']
  if t not in ids:continue
  info=untyped(p['raw']);charge=[untyped(r['raw']) for r in p['charge']];jz=[untyped(r['raw']) for r in p['jiaozhi']]
  family=('jz_charge_six' if len(charge)==6 else 'jz_charge_four') if jz else ('charge_only' if charge else ('ticket_only' if t in expansion['ticket_only_source_offline_free']['ids'] else ('legacy_plain' if t in (2,3) else 'base_repaired')))
  if jz and (len(jz)!=6 or len(charge) not in (4,6)):raise ValueError('Unsupported family row shape')
  if any(r['drawType']!=t for r in charge+jz):raise ValueError('Cross-pool source row')
  if len({r['id'] for r in charge})!=len(charge) or len({r['id'] for r in jz})!=len(jz):raise ValueError('Duplicate row')
  assets=list(COMMON)
  if charge:assets+=['cocos/card_jiaozhi_2.csb' if jz else 'cocos/card_leichong.csb','cocos/image/bbs/activity_39_mask_dispatch.png']
  if info.get('tabImgPath'):assets.append('cocos/image/card/tab/'+info['tabImgPath'])
  else:assets.append('cocos/image/card/tab/tab_main_jiyi.png')
  for row in charge+jz:
   if row.get('target_item'):
    meta=display['items'].get(str(row['target_item']))
    if meta is None:raise ValueError('Display target item closure missing')
    assets.append('cocos/image/item/common/%s.png'%meta['icon'])
  refs=set()
  for row in charge:refs.update(row.get('showrewards',()))
  for row in jz:refs.update(row.get('show_rewards',()))
  for ref in sorted(refs):
   common=display['common'].get(str(ref))
   if common is None:raise ValueError('Display common closure missing')
   for identity in common.get('items',()):
    meta=display['items'].get(str(identity))
    if meta is None:raise ValueError('Display item closure missing')
    if meta.get('release',False):assets.append('cocos/image/item/common/%s.png'%meta['icon'])
  if charge:
   last=max(charge,key=lambda r:r['id']);heroes=[display['items'][str(k)].get('heroid') for rid in last.get('showrewards',()) for k in display['common'][str(rid)].get('items',()) if display['items'][str(k)].get('heroid')]
   if not heroes:raise ValueError('Display max charge hero unresolved')
   assets.append('cocos/image/hero/skill_dazhao/%s.png'%heroes[0])
  if jz:assets.append('cocos/image/hero/skill_dazhao/%s.png'%jz[0]['target_hero'])
  assets=sorted(set(assets+entry_assets[t]))
  pools.append({'id':t,'family':family,'epoch':p['epoch'],'info':info,'charge':charge,'jiaozhi':jz,'required_assets':assets,'cost_policy':'history-free-v1','source_level_bounds':[info.get('show_level_lower_bound'),info.get('show_level_upper_bound')],'entry_policy':'original-available-panel-else-generic7','resource_gate':'bounded-source-and-metadata-closed-native-unverified'})
 if sorted(p['id'] for p in pools)!=ids:raise ValueError('Incomplete family projection')
 return {'schema':SCHEMA,'backend_sha256':ASSET_SHA256,'base_sha256':BASE_SHA,'expansion_sha256':EXPANSION_SHA,'candidate_ids':ids,'backend_scope':ids,'detail_ids':ids,'entry_sha256':ENTRY_SHA,'ui_comp':entries['ui_comp'],'display_sha256':DISPLAY_SHA,'display':display,'pools':pools,'verified_ids':ids,'publishable_ids':ids,'public_ready_ids':[],'policy':'fixed640-family-scoped-ui-v1'}
def main():
 import argparse
 ap=argparse.ArgumentParser();ap.add_argument('--directory',type=Path);ap.add_argument('--output',type=Path,required=True);ap.add_argument('--maintainer-source',type=Path);ap.add_argument('--maintainer-entry-archive',type=Path);a=ap.parse_args()
 if a.maintainer_entry_archive is not None:
  if a.maintainer_source is None:ap.error('--maintainer-source required for entry producer')
  print(json.dumps(maintainer_entry_assets(a.maintainer_entry_archive,a.maintainer_source,a.output),sort_keys=True));return
 if a.maintainer_source is not None:
  print(json.dumps(maintainer_display(a.maintainer_source,a.output),sort_keys=True));return
 b=canonical(ui_policy(a.directory))
 with a.output.open('xb') as f:f.write(b)
 print('bytes=%d SHA256=%s public_ready=[]'%(len(b),hashlib.sha256(b).hexdigest()))

def maintainer_display(source,output):
 """Explicit maintainer-only literal projection; consumer never imports decoder."""
 from project7_dynamic_catalog import PINS
 from project7_dream_catalog.produce import literal
 tables={};source=Path(source)
 for name in ('reward_common','item_data'):
  p=source/(name+'.marshal');raw=p.read_bytes()
  if hashlib.sha256(raw).hexdigest()!=PINS[name]:raise ValueError('Unsupported public source '+name)
  tables[name]=literal(p)
 data=load();expansion=json.loads((ROOT/'offline/current/data/project7_dynamic_catalog/expansion-policy-v1.json').read_text());refs=set()
 for p in data['pools']:
  if p['pool'] not in expansion['backend_policy_ids']:continue
  for r in p['charge']:refs.update(untyped(r['raw']).get('showrewards',()))
  for r in p['jiaozhi']:refs.update(untyped(r['raw']).get('show_rewards',()))
 common={k:tables['reward_common'][k] for k in sorted(refs)};ids={10387}
 for row in common.values():ids.update(row.get('items',()));ids.update(row.get('treasure',()))
 payload=canonical({'common':common,'items':{k:tables['item_data'][k] for k in sorted(ids)}});packed=gzip.compress(payload,mtime=0)
 if hashlib.sha256(packed).hexdigest()!=DISPLAY_SHA:raise ValueError('Display projection differs from frozen component')
 with Path(output).open('xb') as f:f.write(packed)
 return {'sha256':DISPLAY_SHA,'size':len(packed),'common':len(common),'items':len(ids)}


def maintainer_entry_assets(archive,source,output):
 """Explicit fixed public NPK + pinned literal source producer. No game code."""
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
 cd=literal(source);ids=json.loads((ROOT/'offline/current/data/project7_dynamic_catalog/expansion-policy-v1.json').read_text())['backend_policy_ids'];pools=[];allassets=set();used=set()
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
 for p in load()['pools']:
  t=p['pool']
  if t not in ids:continue
  info=untyped(p['raw']);idx=info.get('room_enter_index');assets=set()
  for core in ('card_tab','card_box','card_common','common_frame','common_property','common_icon','hero_herolist_common'):assets.update(getassets(core))
  if p['charge']:assets.update(getassets('card_jiaozhi_2' if p['jiaozhi'] else 'card_leichong'))
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
 out={'schema':'project7-dynamic-ui-family-entry-assets-v1','source_ui_comp_sha256':hashlib.sha256(raw).hexdigest(),'ui_comp':{i:cd[i] for i in sorted(used)},'pools':pools}
 b=canonical(out);z=gzip.compress(b,mtime=0)
 if hashlib.sha256(z).hexdigest()!=ENTRY_SHA:raise ValueError('Entry dependency projection changed')
 with Path(output).open('xb') as handle:handle.write(z)
 return {'sha256':ENTRY_SHA,'size':len(z),'assets':len(allassets),'ui_comp':len(used)}

if __name__=='__main__':main()
