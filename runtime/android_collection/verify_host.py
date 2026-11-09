"""Host static DEX API audit + javac + synthetic transaction fault/restart tests.
No original DEX/ART/game execution; compile stubs are never packaging inputs.
"""
from pathlib import Path
import hashlib,json,subprocess,tempfile,re,base64,collections
ROOT=Path(__file__).resolve().parents[2];HERE=Path(__file__).resolve().parent
DEX_SHA='087656832b8150984c81c997c7c1f3966da22902c5226b0f6ef2f3e71d602325'
def sha(b):return hashlib.sha256(b).hexdigest()
def audit_dex():
 from loguru import logger
 logger.remove()
 from androguard.core.dex import DEX
 data=(ROOT/'analysis/project7/fixed-component-v2-stage/classes7.dex').read_bytes()
 if sha(data)!=DEX_SHA:raise ValueError('Pinned staged manager DEX mismatch')
 classes={c.get_name():c for c in DEX(data).get_classes()};prefix='Lcom/project7/localmanager/';checks=[]
 def method(cls,name,desc,static=False,private=False):
  rows=[m for m in classes[prefix+cls+';'].get_methods() if m.get_name()==name and m.get_descriptor()==desc]
  if len(rows)!=1 or bool(rows[0].get_access_flags()&8)!=static or private and not rows[0].get_access_flags()&2:raise ValueError((cls,name,desc,'API mismatch'))
  checks.append({'class':cls,'method':name,'descriptor':desc,'access':rows[0].get_access_flags_string()})
 def field(cls,name,desc,static=False):
  rows=[f for f in classes[prefix+cls+';'].get_fields() if f.get_name()==name and f.get_descriptor()==desc]
  if len(rows)!=1 or bool(rows[0].get_access_flags()&8)!=static:raise ValueError((cls,name,desc,'field mismatch'))
  checks.append({'class':cls,'field':name,'descriptor':desc,'access':rows[0].get_access_flags_string()})
 method('LocalProfileStore','features','()'+prefix+'LocalFeatureCatalog;',False);field('LocalFeatureCatalog','entries','Ljava/util/Map;');method('LocalSharedLiberateEngine','normalize','([B '+prefix+'LocalFeatureCatalog;)[B',True)
 method('LocalProfileStore','readAll','(Ljava/io/File;)[B',True,True);method('LocalProfileStore','writeAtomic','(Ljava/io/File; [B)V',True,True)
 field('LocalProfileStore','profilesDirectory','Ljava/io/File;');field('LocalProfileStore','PROFILE_LOCK','Ljava/lang/Object;',True)
 field('GatewayService','SAVE_ACCESS','Ljava/lang/Object;',True);method('GatewayService','isRunning','()Z',True);method('GatewayService','saveAccessBlocked','()Z',True)
 method('LocalResourceCatalog','<init>','(Ljava/io/InputStream;)V')
 for n in ['heroes','skins','treasures']:field('LocalResourceCatalog',n,'Ljava/util/Map;')
 field('LocalResourceCatalog$Skin','hero','I');field('LocalResourceCatalog$Hero','rank','I');field('LocalResourceEngine$Result','profile','[B');field('LocalLevelAdmin$HeroGrant','profile','[B')
 method('LocalResourceEngine$Result','<init>','([B)V')
 method('LocalLevelAdmin','grantAllHeroes','([B '+prefix+'LocalResourceCatalog;)'+prefix+'LocalLevelAdmin$HeroGrant;',True)
 method('LocalResourceEngine','addMissingHero','('+prefix+'LocalResourceEngine$Result; I I)V',True)
 method('LocalCollectionEngine','grantAll','([B '+prefix+'LocalResourceCatalog; Ljava/lang/String;)'+prefix+'LocalLevelAdmin$HeroGrant;',True)
 method('LocalResourceEngine','grant','('+prefix+'LocalResourceEngine$Result; '+prefix+'LocalResourceCatalog; Ljava/lang/String; I I I)V',True)
 method('BsonLite','document','([Ljava/lang/Object;)[B',True);method('BsonLite','withProfileDocument','([B Ljava/lang/String; [B)[B',True)
 return checks

def public_liberate_audit():
 # Decode only LS static public catalog rows, never profile/template BSON.
 from bson import BSON
 asset_root=ROOT/'analysis/project7/fixed-component-v2-stage/assets';groups={};sources=[]
 growth=(asset_root/'growth.tsv').read_bytes()
 if sha(growth)!='91674e9f6f7efc1b9e230d0aa99af0e97557b1f4b50eaa860c3a4d5c3cbc4457':raise ValueError('Pinned public growth asset changed')
 for path in sorted(asset_root.glob('*.tsv')):
  for line in path.read_text().splitlines():
   fields=line.split('\t')
   if len(fields)==3 and fields[0]=='LS':
    key='LS:'+fields[1]
    if key in groups:raise ValueError('Duplicate public LS row')
    groups[key]=BSON(base64.b64decode(fields[2])).decode()['liberate_share'];sources.append(path.name)
 expected={'LS:1':[34,122],'LS:2':[45,139],'LS:3':[63,145]}
 if groups!=expected:raise ValueError('Pinned shared-liberation groups changed')
 counts=collections.Counter(id for group in groups.values()for id in group)
 if any(n>1 for n in counts.values()):raise ValueError('Expected disjoint fixed LS groups')
 return {'public_asset':'growth.tsv','bytes':len(growth),'sha256':sha(growth),'groups':groups,'sources':sources,'disjoint':True,'other_public_tsv_ls_rows':0,'private_or_template_bson_read':False}

def run():
 checks=audit_dex();liberate_audit=public_liberate_audit();target_path=ROOT/'runtime/project7_catalog/target-manifest.json';target_bytes=target_path.read_bytes();target=json.loads(target_bytes)
 if sha(target_bytes)!='7e3849b6ed316b7cdc2ef9f103b90e0bc8e20f9b5da70ab3b585fbd72c0da62d':raise ValueError('Target pin mismatch')
 lines=[]
 for h in target['heroes']:lines.append('H\t'+str(h['id'])+'\t'+str(h['rank']))
 for s in target['skins']:lines.append('S\t'+str(s['id'])+'\t'+str(s['hero']))
 for t in target['treasures']:
  for q in t['qualities']:lines.append('\t'.join(['T',str(t['id']),str(q['quality']),','.join(map(str,q['tricks'])),','.join(a['name']+':'+str(a['sourceBounds'][0])+':'+str(a['sourceBounds'][1]) for a in q['attrs'])]))
 java=ROOT/'toolchains/java/jdk-17.0.21+9/Contents/Home/bin';android=ROOT/'toolchains/android-sdk/platforms/android-32/android.jar'
 with tempfile.TemporaryDirectory(prefix='project7-collection-host-') as temp:
  temp=Path(temp);stubs=temp/'compile-only-stubs';classes=temp/'production-classes';tests=temp/'synthetic-host-tests';stubs.mkdir();classes.mkdir();tests.mkdir();fixture=temp/'targets.tsv';fixture.write_text('\n'.join(lines)+'\n')
  subprocess.run([str(java/'javac'),'-source','8','-target','8','-Xlint:-options','-cp',str(android),'-d',str(stubs),*map(str,(HERE/'compile_stubs').rglob('*.java'))],check=True,capture_output=True)
  subprocess.run([str(java/'javac'),'-source','8','-target','8','-Xlint:-options','-cp',str(android)+':'+str(stubs),'-d',str(classes),*map(str,(HERE/'src').rglob('*.java'))],check=True,capture_output=True)
  production_classes=sorted(str(p.relative_to(classes)) for p in classes.rglob('*.class'))
  if any('StableIdentityBootstrap' in n or 'LocalProfileStore' in n for n in production_classes):raise ValueError('Compile stub leaked into production classes')
  subprocess.run([str(java/'javac'),'-source','8','-target','8','-Xlint:-options','-cp',':'.join(map(str,[android,stubs,classes])),'-d',str(tests),*map(str,(HERE/'host_tests').rglob('*.java'))],check=True,capture_output=True)
  result=subprocess.run([str(java/'java'),'-Xmx512m','-cp',':'.join(map(str,[tests,classes,stubs,android])),'com.project7.localmanager.CollectionHostTest',str(fixture)],check=False,capture_output=True,text=True)
  if result.returncode:raise RuntimeError('Synthetic host failed: '+result.stdout+'\n'+result.stderr)
 metrics={k:int(v) for k,v in re.findall(r'(initialBytes|finalBytes|firstGrantCalls|inputBytes|outputBytes|firstPassMillis)=(\d+)',result.stdout)}
 return {'fixed_public_liberate_groups':liberate_audit,'synthetic_metrics_not_original_engine_performance':metrics,'scope':'static DEX metadata, javac and synthetic host only; no original engine/ART/native execution','manager_dex_sha256':DEX_SHA,'api_checks':checks,'production_classes':production_classes,'compile_stubs_separate':True,'host_output':result.stdout.strip(),'target_sha256':sha(target_bytes)}
if __name__=='__main__':print(json.dumps(run(),indent=2))
