"""Check every adapter-facing manager API in actual DEX, then compile only.

This never runs APK code. Stubs compile into a separate directory and must not
be included in any DEX or APK. Result records compile-only verification.
"""
from pathlib import Path
import hashlib
import json
import subprocess
import shutil
import zipfile
from loguru import logger
logger.remove()
from androguard.core.dex import DEX
from androguard.core.axml import AXMLPrinter

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
APK = Path.home() / 'Downloads/Project7-local-manager-v2.10.1.apk'
PREFIX = 'Lcom/project7/localmanager/'
PINNED_APK_SHA256 = '0dcfbfa15141c0c2fca06ba8cede5b36492c7b1c60985e84b8c21923513c6c01'
PINNED_DEX_SHA256 = '087656832b8150984c81c997c7c1f3966da22902c5226b0f6ef2f3e71d602325'
if hashlib.sha256(APK.read_bytes()).hexdigest() != PINNED_APK_SHA256:
    raise RuntimeError('Manager APK pin changed')
with zipfile.ZipFile(APK) as z:
    dex_bytes = z.read('classes.dex')
    if hashlib.sha256(dex_bytes).hexdigest() != PINNED_DEX_SHA256:
        raise RuntimeError('Manager DEX pin changed')
    classes = {c.get_name(): c for c in DEX(dex_bytes).get_classes()}
    min_sdk = int(AXMLPrinter(z.read('AndroidManifest.xml')).get_xml_obj().find('uses-sdk').get('{http://schemas.android.com/apk/res/android}minSdkVersion'))
if dex_bytes[:8] != b'dex\n038\x00' or len(classes) != 649 or min_sdk != 26:
    raise RuntimeError('Pinned manager DEX038/649classes/minSdk26 changed')
checks = []

def require(condition, detail):
    if not condition: raise RuntimeError(detail)

def method(cls, name, descriptor, static=False):
    c = classes[PREFIX + cls + ';']
    found = [m for m in c.get_methods() if m.get_name() == name and m.get_descriptor() == descriptor]
    require(len(found) == 1, ('method mismatch', cls, name, descriptor))
    m = found[0]
    require(not m.get_access_flags() & 2, ('private method', cls, name))
    require(bool(m.get_access_flags() & 8) == static, ('static mismatch', cls, name))
    checks.append({'class': cls, 'method': name, 'descriptor': descriptor,
                   'access': m.get_access_flags_string()})

method('GatewayService', 'saveAccessBlocked', '()Z', True)
method('GatewayService', 'isRunning', '()Z', True)
for name, desc, access in [
    ('SAVE_ACCESS', 'Ljava/lang/Object;', 8),
    ('RUNNING', 'Ljava/util/concurrent/atomic/AtomicBoolean;', 8),
    ('lastServer', PREFIX + 'LocalGatewayServer;', 8),
    ('lastServerThread', 'Ljava/lang/Thread;', 8)]:
    f = next(f for f in classes[PREFIX+'GatewayService;'].get_fields() if f.get_name() == name)
    require(f.get_descriptor() == desc and f.get_access_flags() & access, ('field mismatch', name, desc))
    if name == 'SAVE_ACCESS': require(not f.get_access_flags() & 2, 'SAVE_ACCESS must be non-private')
    checks.append({'field': name, 'descriptor': desc, 'access': f.get_access_flags_string()})
for name in ('LocalProfileStore','LocalAccountStore','LocalTutorialStore','LocalEventCatalog',
             'LocalNewbeeCatalog','LocalCombatCatalog','LocalPatrolCatalog'):
    method(name, '<init>', '(Landroid/content/Context;)V')
require(PREFIX+'LocalGatewayServer$ProfileProvider;' in classes[PREFIX+'LocalProfileStore;'].get_interfaces(), 'ProfileProvider mismatch')
method('LocalGatewayServer','<init>', '(I '+PREFIX+'LocalAccountStore; '+PREFIX+'LocalGatewayServer$ProfileProvider; '+PREFIX+'LocalTutorialStore; '+PREFIX+'LocalEventCatalog; '+PREFIX+'LocalNewbeeCatalog; '+PREFIX+'LocalCombatCatalog; '+PREFIX+'LocalPatrolCatalog; '+PREFIX+'LocalGatewayServer$StatusListener;)V')
method('LocalGatewayServer$StatusListener','onStatus','(Z Ljava/lang/String;)V')
method('LocalBootstrapServer','<init>','(I Ljava/util/function/Supplier;)V')
method('LocalStartupMode','get','(Landroid/content/Context;)Ljava/lang/String;', True)
method('LocalStartupMode','set','(Landroid/content/Context; I)V', True)
for name in ('LocalGatewayServer','LocalBootstrapServer'):
    method(name,'run','()V'); method(name,'close','()V')
method('LocalGatewayServer','saveWritersStopped','()Z')

# Stable identity/profile bootstrap: exact same-package original APIs only.
method('LocalAccountStore', 'listAccounts', '()Ljava/util/List;')
method('LocalAccountStore', 'registerOne', '(Ljava/lang/String; Ljava/lang/String;)I')
method('LocalAccountStore', 'numericId', '(Ljava/lang/String;)I')
method('LocalAccountStore', 'authenticate', '(Ljava/lang/String; Ljava/lang/String;)'+PREFIX+'LocalAccountStore$Result;')
method('LocalTutorialStore', 'load', '(Ljava/lang/String;)'+PREFIX+'LocalTutorialStore$Progress;')
method('LocalTutorialStore', 'save', '(Ljava/lang/String; '+PREFIX+'LocalTutorialStore$Progress;)V')
method('LocalProfileStore', 'load', '(Ljava/lang/String; '+PREFIX+'LocalTutorialStore$Progress;)[B')
method('LocalAccountArchive', '<init>', '(Landroid/content/Context; '+PREFIX+'LocalAccountStore;)V')
method('LocalAccountArchive', 'snapshot', '(Ljava/lang/String;)'+PREFIX+'LocalAccountArchive$Snapshot;')
method('BsonLite', 'intValue', '([B Ljava/lang/String;)Ljava/lang/Integer;', True)
method('BsonLite', 'stringValue', '([B Ljava/lang/String;)Ljava/lang/String;', True)
for cls, name, descriptor, static in [
    ('LocalAccountStore', 'FILE_LOCK', 'Ljava/lang/Object;', True),
    ('LocalAccountStore$Result', 'accepted', 'Z', False),
    ('LocalAccountStore$Result', 'registered', 'Z', False),
    ('LocalAccountStore$Result', 'username', 'Ljava/lang/String;', False)]:
    selected = [f for f in classes[PREFIX+cls+';'].get_fields() if f.get_name() == name]
    require(len(selected) == 1, ('missing bootstrap field', cls, name))
    f = selected[0]
    require(f.get_descriptor() == descriptor and not f.get_access_flags() & 2 and bool(f.get_access_flags() & 8) == static,
            ('bootstrap field mismatch/private', cls, name, descriptor))
    checks.append({'class':cls, 'field':name, 'descriptor':descriptor, 'access':f.get_access_flags_string()})

javac = ROOT/'toolchains/java/jdk-17.0.21+9/Contents/Home/bin/javac'
android = ROOT/'toolchains/android-sdk/platforms/android-32/android.jar'
build = ROOT/'analysis/project7/single-package-adapter'
stubs = build/'compile-only-stubs'; output = build/'adapter-classes'
for directory in (stubs, output):
    if directory.exists(): shutil.rmtree(directory)
    directory.mkdir(parents=True, exist_ok=True)
common = [str(javac), '-source', '8', '-target', '8', '-Xlint:-options']
subprocess.run(common+['-cp',str(android),'-d',str(stubs),str(HERE/'compile_stubs/com/project7/localmanager/ManagerApiStubs.java')],check=True)
sources = sorted((HERE/'src/com/project7/localmanager').glob('*.java'))
subprocess.run(common+['-cp',str(android)+':'+str(stubs),'-d',str(output)]+[str(p) for p in sources],check=True)
compiled = sorted(output.rglob('*.class'))
allowed = {p.stem for p in sources}
if not compiled or not all(p.stem.split('$')[0] in allowed for p in compiled):
    raise RuntimeError('Compile stubs leaked into adapter output')
collisions = [str(p.relative_to(output)) for p in compiled
              if 'L' + p.relative_to(output).with_suffix('').as_posix() + ';' in classes]
if collisions: raise RuntimeError('Adapter collides with manager class definitions: ' + repr(collisions))
result = {'class_definition_collisions':collisions, 'status':'compiled_against_real_android32_and_dex_verified_stubs','runtime_verified':False,
          'manager_sha256':hashlib.sha256(APK.read_bytes()).hexdigest(),
          'manager_dex_sha256':hashlib.sha256(dex_bytes).hexdigest(),
          'manager_class_count':len(classes),'manager_dex_version':'038','manager_min_sdk':min_sdk,
          'api_checks':checks,
          'sources':[{ 'path':str(p.relative_to(ROOT)), 'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in sources],
          'adapter_classes':[{ 'path':str(p.relative_to(ROOT)), 'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in compiled],
          'never_package':str(stubs.relative_to(ROOT)),
          'remaining':['Final parent build input/DEX packaging integration','Actual Android/ART/native acceptance not performed']}
(ROOT/'reports/project7-single-package-adapter-compile.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'api_checks':len(checks),'adapter_classes':len(compiled),'runtime_verified':False}))
