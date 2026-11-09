"""Explicit source-export closure and boundary checks. No assembler or game execution."""
import _paths  # noqa: E402,F401
import ast,contextlib,hashlib,io,json,pathlib,shutil,subprocess,sys,tempfile,unittest,zipfile
from unittest.mock import patch
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'offline'/'current'/'tools'))
import export_offline_project as exporter
import build_project7_android as android_builder

def manifest():return json.loads((ROOT/'offline-project-allowlist.json').read_text())
def import_closure(entries, root=ROOT):
    """Conservative local closure, including imports inside maintainer functions.

    Resolve full package names and relative imports. A repository namespace is
    never a third-party dependency, and missing local modules must not disappear.
    """
    root=pathlib.Path(root)
    found=set();third_party=set();todo=list(entries)
    def local_module(name):
        candidates=[pathlib.PurePosixPath(*name.split('.'))]
        for prefix in ('offline/tools','project7_bridge/tools','offline/current/tools','offline/runtime','offline/current/runtime', 'offline/current/data', 'project7_bridge/runtime','project7_bridge/android','runtime'):
            candidates.append(pathlib.PurePosixPath(prefix,*name.split('.')))
        for candidate in candidates:
            for path in (candidate.with_suffix('.py'),candidate/'__init__.py'):
                if (root/path).is_file():
                    todo.append(path.as_posix())
                    # Importing a submodule also executes existing parent inits.
                    for parent in path.parents:
                        init=parent/'__init__.py'
                        if (root/init).is_file():todo.append(init.as_posix())
                    return True
            if (root/candidate).is_dir():
                # Namespace packages have no init, but may expose submodules
                # through `from package import module` below.
                for parent in (candidate,)+tuple(candidate.parents):
                    init=parent/'__init__.py'
                    if (root/init).is_file():todo.append(init.as_posix())
                return True
        return False
    def dependency(name):
        if local_module(name):return
        module=name.split('.')[0]
        if module in ('tools','runtime','offline','project7_bridge'):
            raise ValueError('Unresolved local import: '+name)
        if module not in sys.stdlib_module_names and module!='__future__':third_party.add(module)
    while todo:
        relative=todo.pop()
        if relative in found:continue
        found.add(relative);tree=ast.parse((root/relative).read_text())
        for n in ast.walk(tree):
            if isinstance(n,ast.Import):
                for alias in n.names:dependency(alias.name)
            elif isinstance(n,ast.ImportFrom):
                if n.level:
                    package=list(pathlib.PurePosixPath(relative).parent.parts)
                    if n.level>len(package):raise ValueError('Relative import escapes package')
                    name='.'.join(package[:len(package)-n.level+1]+([n.module] if n.module else []))
                else:name=n.module or ''
                if n.module:
                    dependency(name)
                    for alias in n.names:
                        if alias.name!='*':local_module(name+'.'+alias.name)
                else:
                    for alias in n.names:dependency(name+'.'+alias.name)
    return found,third_party

class SourceExportTests(unittest.TestCase):
    def test_dependency_scan_resolves_packages_and_nested_relative_imports(self):
        with tempfile.TemporaryDirectory() as t:
            root=pathlib.Path(t)
            fixtures={'tools/main.py':'from tools.pkg.codec import encode\nfrom tools.ns import extra\ndef produce():\n from runtime.producer import run\n',
                      'tools/pkg/__init__.py':'from . import codec\n',
                      'tools/pkg/codec.py':'from .helper import identity\nimport lz4.block\n',
                      'tools/pkg/helper.py':'import json\n',
                      'runtime/producer.py':'from tools.pkg import helper\nimport xdis\n',
                      'tools/ns/extra.py':'import json\n'}
            for name,content in fixtures.items():
                path=root/name;path.parent.mkdir(parents=True,exist_ok=True);path.write_text(content)
            closure,deps=import_closure(['tools/main.py'],root)
            self.assertEqual(closure,set(fixtures));self.assertEqual(deps,{'lz4','xdis'})
            (root/'tools/pkg/helper.py').write_text('from tools.missing import value\n')
            with self.assertRaisesRegex(ValueError,'Unresolved local import'):
                import_closure(['tools/main.py'],root)
    def test_explicit_complete_paths_and_legacy_preserved(self):
        data=manifest();paths=data['files'];self.assertEqual(len(paths),len(set(paths)));self.assertEqual(len(data['preserved_legacy_files']),63)
        self.assertTrue(set(data['preserved_legacy_files'])<=set(paths))
        for name in ('offline/current/runtime/project7_collection_visibility.py',
                     'offline/current/data/project7_collection_visibility/policy.json',
                     'offline/current/data/project7_collection_visibility/produce.py',
                     'offline/current/runtime/project7_draw_ui.py'):
            self.assertIn(name,paths)
        forbidden={'analysis','originals','toolchains','.venv','Downloads','host_stubs','host_tests','signing','__pycache__'}
        for name in paths:
            p=pathlib.PurePosixPath(name);self.assertFalse(p.is_absolute());self.assertFalse(set(p.parts)&forbidden);self.assertNotIn('..',p.parts);self.assertFalse(any(c in name for c in '*?['))
            self.assertNotIn(p.suffix.lower(),{'.apk','.npk','.bson','.p12','.jks','.keystore','.class','.dex','.jar','.dylib','.so'})
            source=ROOT/name;self.assertTrue(source.is_file(),name);self.assertFalse(source.is_symlink(),name)
        # Follow every production source group consumed by the real builder.
        # A hand-maintained subset missed newly added classes in later groups.
        from forever7_paths import java_module_root
        for directory in android_builder.SOURCE_DIRS:
            for source in (java_module_root(ROOT,directory)/'src').rglob('*.java'):self.assertIn(str(source.relative_to(ROOT)),paths)
        for directory in ['android_single_package','android_autologin','android_collection','android_core_rpc','android_draw_policy', 'android_story_city']:
            for source in (java_module_root(ROOT,directory)/'compile_stubs').rglob('*.java'):self.assertIn(str(source.relative_to(ROOT)),paths)
    def test_conservative_closure_includes_optional_maintenance_dependencies(self):
        closure,deps=import_closure(['tools/build_offline_project.py','project7_bridge/tools/build_project7_android.py'])
        self.assertTrue(closure<=set(manifest()['files']),sorted(closure-set(manifest()['files'])))
        # The conservative scan includes bytecode27's optional --decompile CLI.
        # Actual normal consumption without that dependency is checked below.
        self.assertEqual(deps,{'lz4','xdis','uncompyle6','bson','androguard'})
        requirements=(ROOT/'requirements-offline.txt').read_text();self.assertIn('lz4==',requirements);self.assertIn('xdis==',requirements)
        self.assertIn('uncompyle6==',(ROOT/'requirements.txt').read_text())
        self.assertIn('pymongo==',requirements)
        self.assertIn('androguard==4.1.4',requirements)
    def test_exported_consumers_and_fixed_ir_work_without_original_workspace(self):
        import lz4,xdis,bson,androguard
        paths=set(manifest()['files'])
        assets={'offline/current/tools/project7_draw_history_ir/data/history-v1/contract.json',
                'offline/current/tools/project7_draw_history_ir/data/history-v1/history-ir.json.gz'}
        self.assertTrue(assets<=paths)
        with tempfile.TemporaryDirectory() as t:
            root=pathlib.Path(t)
            for name in paths:
                destination=root/name;destination.parent.mkdir(parents=True,exist_ok=True)
                shutil.copyfile(ROOT/name,destination)
            before={p.relative_to(root).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()
                    for p in root.rglob('*') if p.is_file()}
            dependency_paths=sorted({str(pathlib.Path(m.__file__).resolve().parent.parent) for m in (lz4,xdis,bson,androguard)})
            program=r'''
import hashlib,importlib.abc,json,pathlib,sys
root=pathlib.Path(sys.argv[1]).resolve()
sys.dont_write_bytecode=True
# Match `python tools/build_offline_project.py`: only tools starts on sys.path.
# Explicit package-root setup, if needed, must come from the real consumer.
sys.path[:0]=[str(root/'offline'/'tools'),str(root/'project7_bridge'/'tools'),str(root/'offline'/'current'/'tools'),str(root/'offline'/'current'/'runtime'),str(root/'offline'/'current'/'data'),str(root/'offline'/'runtime'),str(root/'project7_bridge'/'runtime'),str(root/'runtime')]+json.loads(sys.argv[2])
class BlockMaintenanceDependencies(importlib.abc.MetaPathFinder):
 def find_spec(self,fullname,path=None,target=None):
  if fullname.split('.')[0] in {'uncompyle6','capstone','elftools'}:
   raise ImportError('Not a normal-build dependency: '+fullname)
sys.meta_path.insert(0,BlockMaintenanceDependencies())
import project7_build_inputs,build_project7_android
from project7_story_city_suppression import rows as suppression_rows
assert len(suppression_rows()) == 7
from project7_selector_catalog import verify,ui_policy,audit_history
from project7_feature_assets import dynamic_ui_policy,DYNAMIC_PUBLIC_READY_IDS,wish_ui_policy,WISH_PUBLIC_READY_IDS
dynamic_detail=json.loads(dynamic_ui_policy(root))
assert len(dynamic_detail['pools'])==46
assert dynamic_detail['detail_ids']==list(DYNAMIC_PUBLIC_READY_IDS)
assert dynamic_detail['public_ready_ids']==[]
wish_detail=json.loads(wish_ui_policy(root))
assert wish_detail['detail_ids']==list(WISH_PUBLIC_READY_IDS)
assert wish_detail['public_ready_ids']==[]
from project7_dynamic_catalog import load
assert not (root/'analysis').exists() and not (root/'originals').exists()
assert verify()['roster_counts']=={'A':3,'S':3}
assert ui_policy()['ready_ids']==[265,369,427,454,455]
assert len(audit_history()['pools'])==5
assert len(load()['pools'])==55
for module in tuple(sys.modules.values()):
 value=getattr(module,'__file__',None)
 if value and ('/project7_' in value or value.endswith('/bytecode27.py')):
  assert pathlib.Path(value).resolve().is_relative_to(root),value
print(json.dumps({'normal_imports':'PASS','selector_and_dynamic_assets':'PASS','maintenance_fixed_ir_audit':'PASS','analysis_required':False}))
'''
            result=subprocess.run([sys.executable,'-I','-S','-c',program,str(root),json.dumps(dependency_paths)],
                                  cwd=root,capture_output=True,text=True,timeout=60)
            self.assertEqual(result.returncode,0,result.stderr)
            self.assertFalse(json.loads(result.stdout)['analysis_required'])
            after={p.relative_to(root).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()
                   for p in root.rglob('*') if p.is_file()}
            self.assertEqual(before,after)
    def test_exact_fixed_payload_pins(self):
        pins={'vendor/project7/component-v2.10.1.zip':'ccbde188251c68eb23a4af1d0b6aef1946236d527d2a70f30058277e5a7b7a0d','project7_bridge/runtime/project7_official_baseline/official640-entry-patch.zip':'30294d1b11b372a7b675880e324e9927555d9f2711d9ff9240f3bfcb274f286f','offline/current/data/project7_resources/project7-resource-snapshot.json.gz':'9ce83088f69bc7480140aef46581e9a8a1748dd3d3d9cf3808d50504a4992da0','offline/current/data/project7_resources/project7-resource-binding.json':'9f7ae46a414f45a5e955d045297842b62b6fe26cdf4def5a2b800cbe73eb1be9','project7_bridge/runtime/project7_manager_rpc/dispatch.xor-zlib':'579576b5afa5609d63a1eb86de9181141b4649b82e54ee4afdc478686528dcc6','project7_bridge/runtime/project7_manager_rpc/contract.json':'69ebf52fdda55a7e995fde93d4714bb61992c00ba583e8b045b5db055e47720b','offline/current/data/project7_cg_rewards/public-data.json':'647a1ec62aa56d87a291ce1b9121cbd3a97cf5c00fa71e97d1f6e1d283080675'}
        for name,pin in pins.items():
            self.assertIn(name,manifest()['files'])
            with (ROOT/name).open('rb') as f:self.assertEqual(hashlib.file_digest(f,'sha256').hexdigest(),pin,name)
    def test_exporter_exact_inventory_and_nonoverwrite(self):
        with tempfile.TemporaryDirectory() as t:
            root=pathlib.Path(t).resolve();(root/'a.py').write_bytes(b'print("fixture")\n');allow=root/'list.json';allow.write_text(json.dumps({'files':['a.py']}));output=root/'source.zip'
            with patch.object(exporter,'ROOT',root),patch.object(exporter,'ALLOWLIST',allow):
                with contextlib.redirect_stdout(io.StringIO()):exporter.export(output)
                with zipfile.ZipFile(output) as z:
                    self.assertEqual(set(z.namelist()),{'forever7-offline-project/a.py','forever7-offline-project/EXPORT-INVENTORY.json'})
                    inventory=json.loads(z.read('forever7-offline-project/EXPORT-INVENTORY.json'));self.assertEqual(inventory,[{'path':'a.py','bytes':17,'sha256':hashlib.sha256(b'print("fixture")\n').hexdigest()}])
                prior=output.read_bytes()
                with self.assertRaisesRegex(ValueError,'already exists'):exporter.export(output)
                self.assertEqual(output.read_bytes(),prior)
    def test_exporter_duplicate_traversal_missing_and_symlink_fail(self):
        with tempfile.TemporaryDirectory() as t:
            root=pathlib.Path(t).resolve();(root/'real').write_bytes(b'x');(root/'link').symlink_to(root/'real');allow=root/'list.json';output=root/'source.zip'
            for paths in [['real','real'],['../real'],['missing'],['link']]:
                allow.write_text(json.dumps({'files':paths}))
                with patch.object(exporter,'ROOT',root),patch.object(exporter,'ALLOWLIST',allow):
                    with self.assertRaises(ValueError):exporter.export(output)
                self.assertFalse(output.exists())
if __name__=='__main__':unittest.main()
