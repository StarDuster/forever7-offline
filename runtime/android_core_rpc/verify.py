"""Compile actual manager API + Android32, then pure stock-engine host tests.
No game VM, ART, emulator, APK assembly, D8 or real profile access.
"""
from pathlib import Path
import hashlib,json,subprocess,shutil,time,sys,zipfile
ROOT=Path(__file__).resolve().parents[2];HERE=Path(__file__).resolve().parent
JDK=ROOT/'toolchains/java/jdk-17.0.21+9/Contents/Home/bin'
JAR=ROOT/'analysis/project7/host-original-engine/manager-translated-frames.jar'
JSON=ROOT/'toolchains/json-20240303.jar';ANDROID=ROOT/'toolchains/android-sdk/platforms/android-32/android.jar'
BUILD=ROOT/'analysis/project7/core-rpc-host'
# Verify controlled reflection and direct API against original pinned DEX metadata.
from loguru import logger
logger.remove()
from androguard.core.dex import DEX
with zipfile.ZipFile(Path.home()/'Downloads/Project7-local-manager-v2.10.1.apk') as archive:
    raw=archive.read('classes.dex')
assert hashlib.sha256(raw).hexdigest()=='087656832b8150984c81c997c7c1f3966da22902c5226b0f6ef2f3e71d602325'
classes={c.get_name():c for c in DEX(raw).get_classes()}
api=[]
def check_member(cls,name,descriptor,static,field=False):
    owner=classes['Lcom/project7/localmanager/'+cls+';']
    found=[m for m in (owner.get_fields() if field else owner.get_methods()) if m.get_name()==name and m.get_descriptor().replace(' ','')==descriptor]
    assert len(found)==1,(cls,name,descriptor)
    member=found[0];assert bool(member.get_access_flags()&8)==static
    api.append({'class':cls,'name':name,'descriptor':descriptor,'access':member.get_access_flags_string()})
for cls,name,desc,static,field in [
 ('LocalGatewayServer','profileProvider','Lcom/project7/localmanager/LocalGatewayServer$ProfileProvider;',False,True),
 ('LocalGatewayServer','writeFrame','(Ljava/io/OutputStream;I[B)V',False,False),
 ('LocalProfileStore','PROFILE_LOCK','Ljava/lang/Object;',True,True),
 ('LocalProfileStore','profilesDirectory','Ljava/io/File;',False,True),
 ('LocalProfileStore','readAll','(Ljava/io/File;)[B',True,False),
 ('LocalProfileStore','writeAtomic','(Ljava/io/File;[B)V',True,False),
 ('LocalProfileStore','resources','()Lcom/project7/localmanager/LocalResourceCatalog;',False,False),
 ('LocalResourceEngine','grant','(Lcom/project7/localmanager/LocalResourceEngine$Result;Lcom/project7/localmanager/LocalResourceCatalog;Ljava/lang/String;III)V',True,False),
 ('LocalResourceEngine','syncCurrencies','(Lcom/project7/localmanager/LocalResourceEngine$Result;)V',True,False),
 ('ProtoLite','entityMessage','([B[B[B)[B',True,False),
 ('LocalResourceEngine','array','([B)Ljava/util/List;',True,False),
 ('LocalResourceEngine$Result','<init>','([B)V',False,False),
 ('LocalResourceEngine$Result','add','(Ljava/lang/String;[B)V',False,False),
 ('LocalResourceEngine$Result','reward','()[B',False,False),
 ('LocalResourceEngine$Result','profile','[B',False,True),
 ('LocalResourceEngine$Result','replies','Ljava/util/List;',False,True),
 ('LocalResourceEngine$Reply','method','Ljava/lang/String;',False,True),
 ('LocalResourceEngine$Reply','parameters','[B',False,True),
 ('BsonLite','EMPTY_DOCUMENT','[B',True,True),
 ('BsonLite','document','([Ljava/lang/Object;)[B',True,False),
 ('BsonLite','documentValue','([BLjava/lang/String;)[B',True,False),
 ('BsonLite','arrayValue','([BLjava/lang/String;)[B',True,False),
 ('BsonLite','stringValue','([BLjava/lang/String;)Ljava/lang/String;',True,False),
 ('BsonLite','intValue','([BLjava/lang/String;)Ljava/lang/Integer;',True,False),
 ('BsonLite','numericValue','([BLjava/lang/String;)Ljava/lang/Number;',True,False),
 ('BsonLite','keys','([B)Ljava/util/List;',True,False),
 ('BsonLite','messagePackValue','([BZ)Ljava/lang/Object;',True,False),
 ('BsonLite','withProfileArray','([BLjava/lang/String;Ljava/util/List;)[B',True,False),
 ('BsonLite','withProfileInt','([BLjava/lang/String;I)[B',True,False),
 ('BsonLite','withProfileDocument','([BLjava/lang/String;[B)[B',True,False)]:check_member(cls,name,desc,static,field)

sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
assert sha(JAR)=='723440ecca7b479a9e1f1233222bbff92bfbf41dda18cdcd38d37a4d7ccaa685'
run_plan=subprocess.run([sys.executable,str(ROOT/'runtime/project7_cg_rewards/produce.py')],text=True,capture_output=True,check=True)
assert sha(JSON)=='3cf6cd6892e32e2b4c1c39e0f52f5248a2f5b37646fdfbb79a66b46b618414ed'
if BUILD.exists():shutil.rmtree(BUILD)
for name in ['host-platform','compile-only-stubs','production','tests']:(BUILD/name).mkdir(parents=True)
def run(*args):
 result=subprocess.run(list(map(str,args)),text=True,capture_output=True)
 if result.returncode:raise RuntimeError(result.stdout+result.stderr)
 return result
run(JDK/'javac','--release','8','-d',BUILD/'host-platform',*HERE.glob('host_stubs/**/*.java'))
run(JDK/'javac','--release','8','-d',BUILD/'compile-only-stubs',*HERE.glob('compile_stubs/**/*.java'))
run(JDK/'javac','--release','8','-cp',str(BUILD/'compile-only-stubs')+':'+str(ANDROID),'-d',BUILD/'production',*HERE.glob('src/**/*.java'))
production_names={p.name for p in (BUILD/'production').rglob('*.class')}
assert production_names=={'CoreGapBridge.class','CoreGapBridge$Access.class','CoreGapBridge$Rejected.class','CoreGapBridge$UncertainCommit.class','CgRewardPlan.class'},production_names
cp=':'.join(map(str,[BUILD/'host-platform',JAR,JSON,BUILD/'production']))
run(JDK/'javac','--release','8','-cp',cp,'-d',BUILD/'tests',*HERE.glob('host_tests/**/*.java'))
cp+=':'+str(BUILD/'tests')
start=time.monotonic()
result=run(JDK/'java','-Xverify:all','-cp',cp,'com.project7.localmanager.CoreGapHostTests',ROOT/'analysis/project7/manager/assets',BUILD/'consumer-cases.json')
(BUILD/'host-output.log').write_text(result.stdout+result.stderr)
consumer=run(sys.executable,HERE/'host_tests/consumer.py',BUILD/'consumer-cases.json')
print(result.stdout+consumer.stdout,end='')
report={'format':'project7-cg-original-engine-host-v1','status':'passed','elapsed_seconds':time.monotonic()-start,'stdout':result.stdout+consumer.stdout,'pinned_original_dex_api':api,'public_plan_check':run_plan.stdout,'original_translated_manager_sha256':sha(JAR),'orgjson_sha256':sha(JSON),'production_sources':{str(p.relative_to(ROOT)):sha(p) for p in HERE.glob('src/**/*.java')},'platform_seams':['Context','AssetManager','Os.rename','Log'],'android32_compile':True,'production_compile_uses_only_separate_stubs_and_androidjar':True,'production_class_names':sorted(production_names),'compile_stub_classes_packaged':False,'host_jvm_verify_all':True,'art_device_apk_d8':False,'trampoline_connected':False,'ui_exactly_once':False}
(ROOT/'reports/project7-cg-core-rpc-host.json').write_text(json.dumps(report,indent=2)+'\n')
