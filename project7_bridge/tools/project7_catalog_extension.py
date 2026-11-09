#!/usr/bin/env python3
"""Pinned append-only Project7 catalog extension. No APK, game or profile execution."""
from __future__ import annotations
import _bootstrap  # noqa: E402,F401
import argparse,ast,collections,hashlib,json,math,pathlib,re
from _bootstrap import ROOT;BUNDLE=ROOT/'offline/current/data/project7_catalog'
BASE_SHA='0e4b3789f8c13945926ab90cf0f4ed5f797b6d426c7227a543e98cdd3af7813d'
CONTRACT_SHA='1d5627de39c2a960e368313dfa34c3a63c8f04de3ae46be30edee839dfb1a18f'
SOURCE_PINS={'hero.py':'12eb1bf71a023e221b1d90f6f66883440e27db9481e58a48d13fa7f3ed830fbf','skin.py':'eefbc750db5257c811ce2d42dfc845dcafc7eabbe12f8382735de8e8e5d12749','item_data.py':'33147214c197fccd38a3efc74542e94e05aeb794de8517d4775312b629340f68','hero_treasure.py':'e7c5cf4348b91c50edbde06d27fc11ac0562f27e4e130d9f391dc5ab213f4da1','const.py':'926483f82a397faeb9002ba504e08461d7f36dc4dbb669d0789710a392909b0a','chouka_hero_file.py':'e662be75c2d634834d05c7c89d69b3eca8564a790962076afb1df37c05c4c5fd'}
SHAPES={'H':6,'S':5,'I':6,'T':5,'V':2,'F':9,'N':9,'D':8,'C':3,'X':3,'B':5,'P':6}
LIMIT=8*1024*1024

def require(ok,message):
    if not ok:raise ValueError(message)
def sha(b):return hashlib.sha256(b).hexdigest()
def desc(b):return {'bytes':len(b),'sha256':sha(b)}
def encoded(x):return (json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(',',':'))+'\n').encode('utf-8')
def read_file(path,limit=LIMIT):
    path=pathlib.Path(path);require(path.is_file() and path.stat().st_size<=limit,'source file missing/size bound');data=path.read_bytes();require(len(data)<=limit,'source file grew beyond bound');return data
def number(s):
    require(bool(re.fullmatch(r'0|[1-9][0-9]*',s)) and int(s)<=2147483647,'invalid stock int');return int(s)
def parse_catalog(data,extension=False):
    require(isinstance(data,bytes) and len(data)<=LIMIT and b'\0' not in data,'catalog byte limit/type')
    result={k:{} for k in ('H','S','I','T')};lines=[];seen_lines=set()
    for line in data.decode('utf-8').splitlines():
        if not line or line.startswith('#'):continue
        require(line not in seen_lines,'duplicate catalog row');seen_lines.add(line);row=line.split('\t');tag=row[0]
        require(tag in SHAPES and len(row)==SHAPES[tag],'unsupported stock row shape')
        if extension:require(tag in ('S','I','T'),'extension may not add H/pool/other rows')
        lines.append(row)
        if tag not in result:continue
        key=(number(row[1]),number(row[2])) if tag=='T' else number(row[1]);require(key not in result[tag],'duplicate catalog ID')
        require((key[0] if isinstance(key,tuple) else key)>0,'zero catalog ID')
        if tag=='S':number(row[2]);number(row[3]);require(bool(row[4]),'empty skin name')
        if tag=='I':number(row[3]);number(row[4]);number(row[5]);require(bool(row[2]),'empty item name')
        if tag=='H':number(row[3]);number(row[4]);number(row[5])
        if tag=='T':
            require(1<=key[1]<=5,'invalid treasure quality');tricks=[number(v) for v in row[3].split(',')] if row[3] else [];require(len(tricks)==len(set(tricks)),'duplicate trick')
            attrs={}
            for field in row[4].split(',') if row[4] else []:
                pair=field.split(':');require(len(pair)==2 and bool(re.fullmatch(r'[ft][0-9]+',pair[0])),'invalid attr shape');value=float(pair[1]);require(math.isfinite(value) and pair[0] not in attrs,'invalid/duplicate attr');attrs[pair[0]]=value
        result[tag][key]=row
    return result,lines

def verify_full_target(catalog,targets):
    require(targets['format']=='project7-full-collection-target-v1','target format')
    hero_ids={r['id'] for r in targets['heroes']};skin_ids={r['id'] for r in targets['skins']};treasure_ids={r['id'] for r in targets['treasures']}
    require(len(hero_ids)==len(targets['heroes'])==140 and len(skin_ids)==len(targets['skins'])==494 and len(treasure_ids)==len(targets['treasures'])==380,'target identity cardinality')
    helpers={r['id'] for r in targets['heroes'] if r['grant']=='stock-addMissingHero'}
    require(helpers=={46,125} and set(catalog['H'])==hero_ids-helpers,'hidden heroes must remain outside H')
    require(set(catalog['S'])==skin_ids and set(catalog['T'])=={(i,q) for i in treasure_ids for q in range(1,6)},'full target ID set mismatch')
    skin_rows={r['id']:r for r in targets['skins']}
    for r in targets['skins']:
        row=catalog['S'][r['id']];require([number(row[2]),number(row[3]),row[4]]==[r['hero'],r['item'],r['catalogName']] and r['hero'] in hero_ids,'skin metadata mismatch')
        if r.get('isDyeSkin'):
            require(r.get('oriSkin') in skin_rows,'dye parent missing')
            require(skin_rows[r['oriSkin']]['hero']==r['hero'],'dye parent hero mismatch')
            require(r.get('sourceCanDye')==1,'dye source can_dye metadata mismatch')
        else:
            require(r.get('oriSkin') is None,'non-dye skin must not carry a parent')
    for r in targets['treasures']:
        require(r['id'] in catalog['I'],'treasure item missing')
        require(len(r['qualities'])==5 and {q['quality'] for q in r['qualities']}==set(range(1,6)),'target quality universe')
        for q in r['qualities']:
            require('era' not in q and 'su' not in q,'target quality must not encode extraRandom/suit state')
            row=catalog['T'][(r['id'],q['quality'])];attrs={k:float(v) for k,v in (f.split(':') for f in row[4].split(',') if f)}
            require(([number(v) for v in row[3].split(',')] if row[3] else [])==q['tricks'] and attrs=={x['name']:x['value'] for x in q['attrs']},'treasure metadata mismatch')

def extend_catalog(baseline,extension=None,contract=None,target_manifest=None,provenance=None):
    require(desc(baseline)=={'bytes':1168505,'sha256':BASE_SHA},'unsupported baseline hash/size')
    if extension is None:extension=read_file(BUNDLE/'extension.tsv',65536)
    if contract is None:contract=read_file(BUNDLE/'contract.json',65536)
    if target_manifest is None:target_manifest=read_file(BUNDLE/'target-manifest.json')
    if provenance is None:provenance=read_file(BUNDLE/'provenance.json',1024*1024)
    require(len(contract)<=1024*1024 and sha(contract)==CONTRACT_SHA,'contract pin mismatch')
    c=json.loads(contract);require(c['format']=='project7-catalog-extension-v1' and c['baseline']==desc(baseline),'unsupported contract')
    require(desc(extension)==c['extension'] and desc(target_manifest)==c['targets'] and desc(provenance)==c['provenance'],'bundled data tamper')
    before,_=parse_catalog(baseline);added,lines=parse_catalog(extension,True)
    require({k:len(v) for k,v in added.items()}=={'H':0,'S':40,'I':2,'T':10} and set(added['I'])=={1188,1343},'extension partition')
    for tag in added:require(not set(added[tag])&set(before[tag]),'extension overwrites existing ID')
    # Baseline ends with CRLF. Append only; preserve every original byte/flag/pool row.
    require(baseline.endswith(b'\n'),'baseline lacks line boundary')
    output=baseline+extension;require(desc(output)==c['output'],'extended output hash mismatch')
    final,_=parse_catalog(output);verify_full_target(final,json.loads(target_manifest))
    require(output[:len(baseline)]==baseline and len(final['H'])==138,'baseline preservation failure')
    return output

def apply(baseline_path,output,extension_path=None,contract_path=None,targets_path=None):
    output=pathlib.Path(output);require(not output.exists(),'output exists')
    b=read_file(baseline_path,1168505)
    result=extend_catalog(b,*[read_file(p) if p else None for p in (extension_path,contract_path,targets_path)])
    with output.open('xb') as f:f.write(result)
    return desc(result)

def flags(row):return {k:v for k,v in row.items() if 'forbid' in k or 'release' in k}
def project_treasure(row,indices):
    attrs=[];details=[]
    for key,prefix in (('secondAttrs','f'),('thridAttrs','t')):
        for name,bounds in sorted(row.get(key,{}).items()):
            require(name in indices and len(bounds)==2 and all(type(x) in (int,float) and math.isfinite(x) for x in bounds) and bounds[0]<=bounds[1],'invalid source attribute range')
            value=float(bounds[0]);attrs.append(f'{prefix}{indices[name]}:{value}');details.append({'name':prefix+str(indices[name]),'value':value,'sourceName':name,'sourceBounds':list(bounds),'sourceField':key})
    tricks=list(row.get('fixTrick',()));require(all(type(v) is int and v>0 for v in tricks),'invalid source tricks')
    return ','.join(map(str,tricks)),','.join(attrs),details

def maintainer_generate(baseline,tables_dir,const_path,hero_files_path,treasure_catalog,output):
    """Explicit source paths only; literal AST reads, never imports game modules."""
    from read_data_table import read
    baseline=read_file(baseline,1168505);require(desc(baseline)=={'bytes':1168505,'sha256':BASE_SHA},'unsupported baseline')
    output=pathlib.Path(output);require(not output.exists(),'output exists')
    paths={name:pathlib.Path(tables_dir)/name for name in ('hero.py','skin.py','item_data.py','hero_treasure.py')};paths.update({'const.py':pathlib.Path(const_path),'chouka_hero_file.py':pathlib.Path(hero_files_path)})
    source={}
    for name,path in paths.items():
        b=read_file(path,64*1024*1024);require(sha(b)==SOURCE_PINS[name],name+' source hash mismatch');source[name]=desc(b)
    hero,skin,item,tr=(read(paths[name]) for name in ('hero.py','skin.py','item_data.py','hero_treasure.py'));files=read(paths['chouka_hero_file.py'])
    tree=ast.parse(paths['const.py'].read_text());cls=next(n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='CombatAttrs');indices=ast.literal_eval(next(n.value for n in cls.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='NAME_TO_INDEX' for t in n.targets)))
    base,all_rows=parse_catalog(baseline);require(set(hero)-set(base['H'])=={46,125} and set(files)==set(base['H']),'hero baseline/source universe mismatch')
    require(set(base['H'])<=set(hero) and set(base['S'])<=set(skin) and len(base['H'])==138 and len(base['S'])==454 and len(base['T'])==1890,'base catalog counts')
    missing_skin=sorted(set(skin)-set(base['S']));treasure_ids=sorted({i for i,q in tr});missing_items=sorted(set(treasure_ids)-{i for i,q in base['T']})
    require(len(missing_skin)==40 and missing_items==[1188,1343] and all(i not in base['I'] for i in missing_items),'missing partition mismatch')
    existing_checked=0;name_deviations=[]
    for sid,row in base['S'].items():
        r=skin[sid];require([int(row[2]),int(row[3])]==[r['hero'],r['item']],'existing skin numeric mapping drift')
        if row[4]!=r['name']:name_deviations.append({'id':sid,'catalogName':row[4],'sourceName':r['name']})
    for key,row in base['T'].items():
        require(key in tr,'existing treasure absent from source');tricks,attrs,_=project_treasure(tr[key],indices)
        expected={k:float(v) for k,v in (a.split(':') for a in attrs.split(',') if a)};actual={k:float(v) for k,v in (a.split(':') for a in row[4].split(',') if a)}
        require(row[3]==tricks and actual==expected,'existing treasure projection mismatch');existing_checked+=1
    additions=[];provenance=[]
    for sid in missing_skin:
        r=skin[sid];require(r['id']==sid and r['hero'] in hero,'source skin foreign key');row=['S',sid,r['hero'],r['item'],r['name']];additions.append(row);provenance.append({'tag':'S','id':sid,'source':'skin.py','sourceKey':sid,'fields':['id','hero','item','name']})
    for tid in missing_items:
        r=item[tid];require(r['id']==tid and r['type']==5 and r['wrap']==1,'source treasure item');additions.append(['I',tid,r['name'],r['type'],r['wrap'],0]);provenance.append({'tag':'I','id':tid,'source':'item_data.py','sourceKey':tid,'heroSentinel':0,'sourceFlags':flags(r)})
        for q in range(1,6):
            t=tr[(tid,q)];require(t['id']==tid and t['class']==q,'source quality mismatch');tricks,attrs,detail=project_treasure(t,indices);additions.append(['T',tid,q,tricks,attrs]);provenance.append({'tag':'T','id':tid,'quality':q,'source':'hero_treasure.py','sourceKey':[tid,q],'attrs':detail,'fixTrick':list(t.get('fixTrick',()))})
    extension=('# Fixed official640 S/I/T extension; hidden heroes use stock addMissingHero; no H/pool changes.\n'+''.join('\t'.join(map(str,r))+'\n' for r in additions)).encode('utf-8');merged=baseline+extension;catalog,_=parse_catalog(merged)
    eq=read_file(treasure_catalog,16*1024*1024);require(sha(eq)=='ee8772f7c11a741f97cdefc3c4f1362b2ed7dbd7106e1929faf83638aca983ae','treasure catalog pin mismatch');eqkeys=[line.split('\t')[1] for line in eq.decode().splitlines() if line.startswith('EQ\t')];require(len(eqkeys)==len(set(eqkeys)) and all(f'{i}:{q}' in eqkeys for i in missing_items for q in range(1,6)),'existing EQ coverage mismatch')
    for sid,r in skin.items():
        if r.get('is_dye_skin'):
            parent=skin.get(r.get('ori_skin'))
            require(parent is not None and parent['hero']==r['hero'],'dye parent must exist on the same hero')
            require(r.get('can_dye')==1,'dye source can_dye metadata missing')
    targets={'format':'project7-full-collection-target-v1','policy':'explicit offline full collection; retain original forbid/release flags as metadata; no release/forbid filter on grant targets','heroes':[],'skins':[],'treasures':[],'profileConstraints':profile_constraints()}
    for hid in sorted(hero):
        r=hero[hid];require(hid in skin and skin[hid]['hero']==hid,'default skin mapping');targets['heroes'].append({'id':hid,'grant':'stock-addMissingHero' if hid in (46,125) else 'stock-grantAllHeroes','rank':r['hero_composite_init_rank'],'order':r['hero_composite_init_order'],'sourceName':r['show_name'],'modelId':r.get('model_id'),'sourceFlags':flags(r),'defaultSkin':hid,'modelUiVerified':False})
    for sid in sorted(skin):
        r=skin[sid];targets['skins'].append({'id':sid,'hero':r['hero'],'item':r['item'],'sourceName':r['name'],'catalogName':catalog['S'][sid][4],'variantId':sid,'baseId':r.get('ori_skin',sid),'isDyeSkin':r.get('is_dye_skin',0),'oriSkin':r.get('ori_skin'),'sourceFlags':flags(r),'modelId':r.get('model_id'),'sourceCanDye':r.get('can_dye'),'modelUiVerified':False})
    for tid in treasure_ids:
        r=item[tid];qualities=[]
        for q in range(1,6):
            t=tr[(tid,q)];tricks,attrs,details=project_treasure(t,indices);qualities.append({'quality':q,'tricks':list(t.get('fixTrick',())),'attrs':details})
        targets['treasures'].append({'id':tid,'sourceName':r['name'],'type':r['type'],'wrap':r.get('wrap'),'sourceFlags':flags(r),'qualities':qualities,'modelUiVerified':False})
    verify_full_target(catalog,targets);target_bytes=encoded(targets)
    prov={'format':'project7-catalog-provenance-v1','sourcePins':source,'newRows':provenance,'existingTreasureCompared':existing_checked,'existingTreasureMismatch':0,'existingSkinLabelDifferencesPreserved':name_deviations,'existingTreasureEqCatalog':desc(eq),'eqRowsForMissingTreasuresAlreadyPresent':10,'noEqRowsAdded':True}
    prov_bytes=encoded(prov);contract={'format':'project7-catalog-extension-v1','baseline':desc(baseline),'extension':desc(extension),'targets':desc(target_bytes),'provenance':desc(prov_bytes),'output':desc(merged),'partition':{'newS':40,'newI':2,'newT':10,'newH':0},'targetCounts':{'heroes':140,'stockH':138,'helperHeroes':2,'skins':494,'treasures':380,'treasureQualities':1900},'sourcePins':SOURCE_PINS,'noCdataModification':True,'noProfileMutation':True};contract_bytes=encoded(contract)
    output.mkdir(mode=0o755,parents=True)
    for n,b in [('extension.tsv',extension),('target-manifest.json',target_bytes),('provenance.json',prov_bytes),('contract.json',contract_bytes)]:
        (output/n).write_bytes(b)
    return {'contract':desc(contract_bytes),'extension':desc(extension),'targets':desc(target_bytes),'provenance':desc(prov_bytes),'output':desc(merged),'existingTCompared':existing_checked,'existingSLabelsPreserved':len(name_deviations)}

def profile_constraints():
    return {'hero':{'root':'heromgr','owned':'hrs','entrySchema':{'0':'int hero ID','1':'BSON hero document'},'stockHelper':'LocalResourceEngine.addMissingHero(Result,id,rank)','helperIds':[46,125],'helperRank':4,'helperOrder':1,'helperExpectedFields':{'sl':4,'so':1,'cf':100,'ef':0,'cat':None,'ti':{'items':[],'mc':25},'ar':{'o':1,'ss':3,'oa':{},'ot':{'_base_max_hp':60,'_base_phy_att_str':60,'_base_mag_att_str':60,'_base_phy_def':60,'_base_mag_def':60},'rotc':{},'sl':[]}},'helperDefaultSkinUuidHex':{str(i):f'{i:08x}00000000{i:08x}' for i in (46,125)},'noInventedH':True,'pendingTransfers':['ps->sk','pp/ppc->pa/pat'],'defaultSkinReferenceMustResolve':True},'skin':{'stockBatch':'LocalCollectionEngine.grantAll(profile,catalog,"skin")','ownedOrPending':['hero.sk','heromgr.ps'],'match':'exact variant i, fb=false; base ownership is insufficient','fields':{'i':'int skin variant ID','u':'BsonLite.UuidValue','fb':False,'cr':'stock purchasedSkin value','cd':'empty document','pd':'empty document','cwd':'empty document','pwd':'empty document','ias':False,'tr':'empty array'},'existingCurrentAndDefaultUuidReferencesPreserved':True,'perHeroOwnedPlusPendingMax':500},'treasure':{'root':'inv.items','stockGrant':'LocalResourceEngine.grant(result,catalog,"treasure",id,1,quality)','match':'exact id+quality, valid and non-disabled instance; preserve duplicates/disabled instances','fields':['cl','lv','x','f','ft','attr','era','su'],'attributeEncoding':{'n':'f/t+CombatAttrs index string','v':'BSON double, source lower bound'},'globalUuidUnique':True,'equipmentReferencesResolve':True,'preserveOriginalInstancesAndEquipmentReferences':True},'commit':{'owner':'single P7 BSON owner after full candidate validation','preconditions':['new profile exists','prestart exclusive lifecycle','old writers exited','saveWritersStopped'],'preserveUnknownFieldsAndBsonTypes':True,'singleAtomicCandidateCommit':True,'receiptMustVerifyExactTargetsEveryRun':True,'idempotentSkipExistingValidTargets':True},'acceptance':'exact IDs, all id-quality pairs, attrs/tricks, BSON types, non-disabled state and references; counts alone insufficient','runtimeModelUiPersistenceVerified':False}

def main():
    p=argparse.ArgumentParser(description=__doc__);sub=p.add_subparsers(dest='command',required=True)
    a=sub.add_parser('apply');a.add_argument('--baseline',required=True,type=pathlib.Path);a.add_argument('--output',required=True,type=pathlib.Path);a.add_argument('--extension',type=pathlib.Path);a.add_argument('--contract',type=pathlib.Path);a.add_argument('--targets',type=pathlib.Path)
    a=sub.add_parser('maintainer-generate');a.add_argument('--baseline',required=True,type=pathlib.Path);a.add_argument('--tables-dir',required=True,type=pathlib.Path);a.add_argument('--const',dest='const_path',required=True,type=pathlib.Path);a.add_argument('--hero-files',dest='hero_files_path',required=True,type=pathlib.Path);a.add_argument('--treasure-catalog',required=True,type=pathlib.Path);a.add_argument('--output',required=True,type=pathlib.Path)
    a=p.parse_args();kw=vars(a).copy();cmd=kw.pop('command')
    if cmd=='maintainer-generate':r=maintainer_generate(**kw)
    else:r=apply(kw['baseline'],kw['output'],kw['extension'],kw['contract'],kw['targets'])
    print(json.dumps(r,indent=2))
if __name__=='__main__':main()
