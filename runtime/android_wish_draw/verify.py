"""Finite current-manager Store proof. No API stubs on runtime classpath."""
from pathlib import Path
import argparse,hashlib,json,subprocess,tempfile
a=argparse.ArgumentParser();a.add_argument("--regression",action="store_true");args=a.parse_args()
R=Path(__file__).resolve().parents[2];H=Path(__file__).resolve().parent
J=R/'toolchains/java/jdk-17.0.21+9/Contents/Home/bin';SDK=R/'toolchains/android-sdk/platforms/android-32/android.jar'
JAR=R/'analysis/project7/selector-hook-v1/manager-translated-frames.jar';assert hashlib.sha256(JAR.read_bytes()).hexdigest()=='1be1a7e09c5a2e42d31f9deff54c1d942657fca695c1a996579eefecf365e6fa'
BASE=R/'analysis/project7/dynamic-baiye-integration-prepare-v2/project7-inputs-jtvbtgki';OWN=BASE/'compiled/production-classes';ASSETS=BASE/'stage/assets'
B=Path(tempfile.mkdtemp(prefix='wish-host-',dir=R/'analysis/project7'))
def run(*args):
 p=subprocess.run(list(map(str,args)),capture_output=True,text=True);assert p.returncode==0,p.stdout+p.stderr;return p.stdout+p.stderr
for n in ('api','dynamic-api','production','platform','tests'):(B/n).mkdir()
sources=list(H.glob('src/**/*.java'));tracked=sources+list(H.glob('compile_stubs/**/*.java'))+[p for name in ('android_dynamic_draw','android_history_draw','android_selector_draw')for p in (R/'runtime'/name/'src').rglob('*.java')]+list((R/'runtime/project7_wish_catalog').glob('*'))+[R/'tools/project7_wish_catalog.py'];pins={str(p.relative_to(R)):hashlib.sha256(p.read_bytes()).hexdigest()for p in tracked}
run(J/'javac','--release','8','-cp',SDK,'-d',B/'api',*H.glob('compile_stubs/**/*.java'))
run(J/'javac','--release','8','-cp',SDK,'-d',B/'dynamic-api',*R.glob('runtime/android_dynamic_draw/compile_stubs/**/*.java'))
run(J/'javac','--release','8','-cp',str(SDK)+':'+str(B/'dynamic-api'),'-d',B/'production',*R.glob('runtime/android_dynamic_draw/src/**/*.java'),*R.glob('runtime/android_history_draw/src/**/*.java'),*R.glob('runtime/android_selector_draw/src/**/*.java'))
run(J/'javac','--release','8','-cp',':'.join(map(str,[B/'api',B/'production',OWN,SDK])),'-d',B/'production',*sources)
shop=R/'runtime/android_baiye_shop'
run(J/'javac','--release','8','-d',B/'platform',*[p for p in R.glob('runtime/android_core_rpc/host_stubs/**/*.java')if p.name not in ('AssetManager.java','Os.java','Context.java')],*H.glob('host_tests/android/**/*.java'))
cp=':'.join(map(str,[B/'platform',JAR,R/'toolchains/json-20240303.jar',B/'production',OWN]))
run(J/'javac','--release','8','-cp',cp,'-d',B/'tests',*H.glob('host_tests/com/**/*.java'),R/'runtime/android_baiye_transactions/host_tests/com/project7/localmanager/BaiyeHost.java',*R.glob('runtime/android_dynamic_draw/host_tests/com/**/*.java'),R/'runtime/android_selector_draw/host_tests/com/project7/localmanager/SelectorEngineHost.java')
def abi(text):
 result={};previous=''
 for line in text.splitlines():
  clean=line.strip()
  if clean.startswith('descriptor:'):
   descriptor=clean.split(':',1)[1].strip();kind='method' if descriptor.startswith('(') else 'field'
   if '(' in previous:
    name=previous.split('(',1)[0].split()[-1]
    if '.' in name:name='<init>'
   else:name=previous.rstrip(';').split()[-1]
   result[(kind,name,descriptor)]=tuple(word for word in ('public','protected','private','static','final')if word in previous.split())
  elif clean:previous=clean
 return result
mismatches=[];checked=0
for p in(B/'api').rglob('*.class'):
 name=p.relative_to(B/'api').as_posix()[:-6].replace('/','.')
 declared=abi(run(J/'javap','-p','-s','-classpath',B/'api',name));actual=abi(run(J/'javap','-p','-s','-classpath',JAR,name))
 for member,flags in declared.items():
  checked+=1
  if actual.get(member)!=flags:mismatches.append([name,member,flags,actual.get(member)])
assert not mismatches,mismatches
(B/'abi-result.json').write_text(json.dumps({'checked':checked,'mismatches':mismatches},indent=2)+'\n')
producer=run(R/'.venv/bin/python',H/'host_tests/reliable_producer.py',B/'reliable-producer.json');print(producer,end='');(B/'reliable-producer.log').write_text(producer)
out=run(J/'java','-Xverify:all','-Dp7.baiye.catalog='+str(R/'runtime/project7_baiye_catalog/catalog-v1.tsv'),'-Dp7.baiye.fragments='+str(R/'runtime/project7_baiye_catalog/fragments-v1.tsv'),'-Dp7.baiye.shop='+str(R/'runtime/project7_baiye_shop_catalog/catalog-v1.tsv'),'-cp',cp+':'+str(B/'tests'),'com.project7.localmanager.WishChooseHost',ASSETS,R/'runtime/project7_wish_catalog/catalog-v1.json',B/'consumer-cases.json',B/'reliable-producer.json');print(out,end='');(B/'stdout.log').write_text(out)
groups=run(J/'java','-Xverify:all','-Dp7.baiye.catalog='+str(R/'runtime/project7_baiye_catalog/catalog-v1.tsv'),'-Dp7.baiye.fragments='+str(R/'runtime/project7_baiye_catalog/fragments-v1.tsv'),'-Dp7.baiye.shop='+str(R/'runtime/project7_baiye_shop_catalog/catalog-v1.tsv'),'-cp',cp+':'+str(B/'tests'),'com.project7.localmanager.WishGroupHost',ASSETS,R/'runtime/project7_wish_catalog/catalog-v1.json',B/'group-consumer-cases.json');print(groups,end='');(B/'groups.log').write_text(groups)
consumer=run(R/'.venv/bin/python',H/'host_tests/consumer.py',B/'consumer-cases.json',B/'group-consumer-cases.json');print(consumer,end='');(B/'consumer.log').write_text(consumer)
if args.regression:
 fixture=B/'old485-oracle.json';manifest=json.loads((BASE/'compiled/compile-inputs.json').read_text())
 for row in manifest['classes']:
  path=OWN/row['path'];assert path.stat().st_size==row['bytes'] and hashlib.sha256(path.read_bytes()).hexdigest()==row['sha256']
 public=[R/'analysis/project7/fixed-component-v2-stage/assets',R/'analysis/project7/extended-catalog-proof/resources.tsv',R/'tools/project7_draw_ir/data/android-catalog-v2.tsv',R/'runtime/project7_history_catalog/catalog-v3.tsv',R/'runtime/project7_history_catalog/furniture-v1.tsv',R/'runtime/project7_selector_catalog/catalog-v1.tsv',R/'runtime/project7_dynamic_catalog/catalog-v1.json.gz']
 oldcp=':'.join(map(str,[B/'platform',B/'tests',OWN,JAR,R/'toolchains/json-20240303.jar']))
 oracle=run(J/'java','-Xverify:all','-cp',oldcp,'com.project7.localmanager.DynamicUpgradeHost',*public,'oracle',fixture);(B/'old485.log').write_text(oracle)
 for mode in ('current','family','selector'):
  out=run(J/'java','-Xverify:all','-Dp7.wish='+str(R/'runtime/project7_wish_catalog/catalog-v1.json'),'-cp',cp+':'+str(B/'tests'),'com.project7.localmanager.WishCompatibilityHost',*public,mode,fixture);(B/('regression-'+mode+'.log')).write_text(out);print('\n'.join(line for line in out.splitlines() if not line.startswith(('DYNAMIC_FIXTURE ','SELECTOR_FIXTURE '))))
assert pins=={str(p.relative_to(R)):hashlib.sha256(p.read_bytes()).hexdigest()for p in tracked}
(B/'result.json').write_text(json.dumps({'status':'PASS','source_hashes':pins,'manager_sha256':hashlib.sha256(JAR.read_bytes()).hexdigest(),'classes':[str(p.relative_to(B/'production'))for p in(B/'production').rglob('*.class')],'runtime_api_stubs':False,'scope':'all nine backend candidates original Store finite tests; public UI/Main not integrated; no APK/native/game'},indent=2)+'\n');print(B)
