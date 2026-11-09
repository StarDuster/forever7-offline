"""Independent Android32 javac + actual fixed current manager finite JVM tests."""
from pathlib import Path
import hashlib,json,subprocess,tempfile
R=Path(__file__).resolve().parents[2];H=Path(__file__).resolve().parent
J=R/'toolchains/java/jdk-17.0.21+9/Contents/Home/bin';SDK=R/'toolchains/android-sdk/platforms/android-32/android.jar'
JAR=R/'analysis/project7/selector-hook-v1/manager-translated-frames.jar';assert hashlib.sha256(JAR.read_bytes()).hexdigest()=='1be1a7e09c5a2e42d31f9deff54c1d942657fca695c1a996579eefecf365e6fa'
BASE=R/'analysis/project7/selector-tutorial-integration-prepare-v2/project7-inputs-yx6zoazx';OWN=BASE/'compiled/production-classes';ASSETS=BASE/'stage/assets'
B=Path(tempfile.mkdtemp(prefix='baiye-shop-host-',dir=R/'analysis/project7'))
def run(*args):
 p=subprocess.run(list(map(str,args)),capture_output=True,text=True);assert p.returncode==0,p.stdout+p.stderr;return p.stdout+p.stderr
TX=R/'runtime/android_baiye_transactions'
sources=list(H.rglob('*.java'))+list(TX.glob('src/**/*.java'));pins={str(p.relative_to(R)):hashlib.sha256(p.read_bytes()).hexdigest()for p in sources}
for name in ('api','production','platform','tests'):(B/name).mkdir()
run(J/'javac','--release','8','-cp',SDK,'-d',B/'api',*H.glob('compile_stubs/**/*.java'))
run(J/'javac','--release','8','-cp',str(SDK)+':'+str(B/'api'),'-d',B/'production',*H.glob('src/**/*.java'),*TX.glob('src/**/*.java'))
run(J/'javac','--release','8','-d',B/'platform',*[p for p in R.glob('runtime/android_core_rpc/host_stubs/**/*.java')if p.name not in ('AssetManager.java','Os.java')],*H.glob('host_tests/android/**/*.java'),R/'runtime/android_week_reset/host_tests/android/system/Os.java')
CP=':'.join(map(str,[B/'platform',JAR,R/'toolchains/json-20240303.jar',OWN,B/'production']))
run(J/'javac','--release','8','-cp',CP,'-d',B/'tests',*H.glob('host_tests/com/**/*.java'),*TX.glob('host_tests/com/**/*.java'))
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
out=run(J/'java','-Xverify:all','-Dp7.baiye.shop='+str(R/'runtime/project7_baiye_shop_catalog/catalog-v1.tsv'),'-Dp7.baiye.catalog='+str(R/'runtime/project7_baiye_catalog/catalog-v1.tsv'),'-Dp7.baiye.fragments='+str(R/'runtime/project7_baiye_catalog/fragments-v1.tsv'),'-cp',CP+':'+str(B/'tests'),'com.project7.localmanager.BaiyeShopHost',ASSETS,B/'consumer-cases.json');print(out,end='');(B/'stdout.log').write_text(out)
consumer=run(R/'.venv/bin/python',H/'host_tests/consumer.py',B/'consumer-cases.json');print(consumer,end='');(B/'consumer.log').write_text(consumer)
assert pins=={str(p.relative_to(R)):hashlib.sha256(p.read_bytes()).hexdigest()for p in sources}
(B/'result.json').write_text(json.dumps({'status':'PASS','actual_manager_sha256':hashlib.sha256(JAR.read_bytes()).hexdigest(),'sources':pins,'production_classes':[p.relative_to(B/'production').as_posix()for p in(B/'production').rglob('*.class')],'limits':['actual manager and166 own classes, explicit Android platform seams','no compile API classes on runtime path','current ownership reget is transparent offline policy','original calendar now argument is milliseconds','no D8/APK/game/device/ART']},indent=2)+'\n');print(B)
