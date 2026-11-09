"""Finite actual-manager dynamic/compatibility proof; no runtime API stubs."""
from pathlib import Path
import argparse,base64,hashlib,json,subprocess,tempfile,importlib.util
ROOT=Path(__file__).resolve().parents[2];HERE=Path(__file__).resolve().parent
SHA='1be1a7e09c5a2e42d31f9deff54c1d942657fca695c1a996579eefecf365e6fa'
ORIGINAL_SHA='af930ec43effa7ee491d5dd391e4ff338a7e540f25c7bed43f4a9fb54a002e78'
def main():
 p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);p.add_argument('--original-caller',action='store_true');p.add_argument('--selector-regression',action='store_true');p.add_argument('--family',action='store_true');p.add_argument('--upgrade-compat',action='store_true');a=p.parse_args();expected=ORIGINAL_SHA if a.original_caller else SHA
 if a.output.exists():raise FileExistsError(a.output)
 jar=ROOT/('analysis/project7/event-reset-week-hook-v2/manager-translated-frames.jar' if a.original_caller else 'analysis/project7/selector-hook-v1/manager-translated-frames.jar');android=ROOT/'toolchains/android-sdk/platforms/android-32/android.jar';jsonjar=ROOT/'toolchains/json-20240303.jar';java=ROOT/'toolchains/java/jdk-17.0.21+9/Contents/Home/bin'
 if hashlib.sha256(jar.read_bytes()).hexdigest()!=expected:raise ValueError('unexpected current manager')
 logs={}
 with tempfile.TemporaryDirectory() as t:
  out=Path(t)
  for n in ('core-api','core','history-api','history','rpc-api','rpc','selector-api','selector','host'):(out/n).mkdir()
  def run(cmd,name):
   r=subprocess.run(list(map(str,cmd)),capture_output=True,text=True);logs[name]={'returncode':r.returncode,'stdout':r.stdout,'stderr':r.stderr}
   if r.returncode:raise RuntimeError(name+'\n'+'\n'.join(x for x in r.stdout.splitlines() if not x.startswith(('SELECTOR_FIXTURE ','DYNAMIC_FIXTURE ')))+r.stderr)
   return r
  base=[java/'javac','-source','8','-target','8','-Xlint:-options']
  for src,api,prod in [(ROOT/'runtime/android_draw_policy','core-api','core'),(ROOT/'runtime/android_core_rpc','rpc-api','rpc')]:
   run([*base,'-cp',android,'-d',out/api,*(src/'compile_stubs').rglob('*.java')],api)
   run([*base,'-cp',str(android)+':'+str(out/api),'-d',out/prod,*(src/'src').rglob('*.java')],prod)
  run([*base,'-cp',android,'-d',out/'selector-api',*(ROOT/'runtime/android_dynamic_draw/compile_stubs').rglob('*.java')],'selector-api')
  run([*base,'-cp',':'.join(map(str,[out/'selector-api',android])),'-d',out/'selector',*(ROOT/'runtime/android_history_draw/src').rglob('*.java'),*(ROOT/'runtime/android_selector_draw/src').rglob('*.java'),*(ROOT/'runtime/android_dynamic_draw/src').rglob('*.java')],'history-selector-source-only')
  cp=':'.join(map(str,[out/'selector',out/'history',out/'core',out/'rpc',jar,jsonjar]));run([*base,'-cp',cp+':'+str(android),'-d',out/'host',*(ROOT/'runtime/android_selector_draw/host_tests/android').rglob('*.java'),*(HERE/'host_tests/com').rglob('*.java'),ROOT/'runtime/android_selector_draw/host_tests/com/project7/localmanager/SelectorEngineHost.java'],'host-compile')
  if a.upgrade_compat:
   frozen=ROOT/'analysis/project7/dynamic-baiye-integration-prepare-v2/project7-inputs-jtvbtgki/compiled';inventory=json.loads((frozen/'compile-inputs.json').read_text());old=frozen/'production-classes'
   for row in inventory['classes']:
    p=old/row['path'];assert p.stat().st_size==row['bytes'] and hashlib.sha256(p.read_bytes()).hexdigest()==row['sha256']
   expected_legacy={'DynamicCatalog':'cea31d9a61de89776ad6980e11cf765e9fccc6ee5067b18738405989c117c153','DynamicDrawPolicy':'d1d1da6bf10c78a08f5811b5a8eaf9269da6eb539edb2ef08e0bafee73d90a6a','DynamicTransition':'a3b3c0dd70f68378f6a7912d9f1c7353dd3030b9c08aeecfe5cc8d4a66bc7305','DynamicSlotPlan':'8153178711e66bcc14f27ae92e9d4744ed5b6329aac32e5ae8b79315320eddd1'}
   for name,digest in expected_legacy.items():assert inventory['source_hashes'][str(HERE/'src/com/project7/localmanager'/ (name+'.java'))]==digest
   fixture=ROOT/'analysis/project7'/('dynamic485-upgrade-'+a.output.stem+'.json')
   args=[ROOT/'analysis/project7/fixed-component-v2-stage/assets',ROOT/'analysis/project7/extended-catalog-proof/resources.tsv',ROOT/'tools/project7_draw_ir/data/android-catalog-v2.tsv',ROOT/'runtime/project7_history_catalog/catalog-v3.tsv',ROOT/'runtime/project7_history_catalog/furniture-v1.tsv',ROOT/'runtime/project7_selector_catalog/catalog-v1.tsv',ROOT/'runtime/project7_dynamic_catalog/catalog-v1.json.gz']
   oldcp=':'.join(map(str,[out/'host',old,jar,jsonjar]));r=run([java/'java','-Xverify:all','-cp',oldcp,'com.project7.localmanager.DynamicUpgradeHost',*args,'oracle',fixture],'old194-oracle')
   r=run([java/'java','-Xverify:all','-cp',str(out/'host')+':'+cp,'com.project7.localmanager.DynamicUpgradeHost',*args,'current',fixture],'new-source-compat')
  else:
   r=run([java/'java','-Xverify:all','-Dp7.selector.caller='+str(not a.original_caller).lower(),'-cp',str(out/'host')+':'+cp,('com.project7.localmanager.DynamicFamilyHost' if a.family else 'com.project7.localmanager.DynamicSelectorRegressionHost' if a.selector_regression else 'com.project7.localmanager.DynamicEngineHost'),ROOT/'analysis/project7/fixed-component-v2-stage/assets',ROOT/'analysis/project7/extended-catalog-proof/resources.tsv',ROOT/'tools/project7_draw_ir/data/android-catalog-v2.tsv',ROOT/'runtime/project7_history_catalog/catalog-v3.tsv',ROOT/'runtime/project7_history_catalog/furniture-v1.tsv',ROOT/'runtime/project7_selector_catalog/catalog-v1.tsv',ROOT/'runtime/project7_dynamic_catalog/catalog-v1.json.gz'],'actual-original-dynamic')
  inventory={'production_classes':len(list((out/'selector').rglob('*.class'))),'dynamic_classes':len(list((out/'selector/com/project7/localmanager').glob('Dynamic*.class'))),'source_hashes':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for folder in ('android_dynamic_draw','android_history_draw','android_selector_draw') for p in sorted((ROOT/'runtime'/folder/'src').rglob('*.java'))}}
  print('\n'.join(x for x in r.stdout.splitlines() if not x.startswith(('SELECTOR_FIXTURE ','DYNAMIC_FIXTURE '))))


  if not a.selector_regression and not a.family and not a.upgrade_compat:
   fixtures={line.split()[1]:base64.b64decode(line.split()[2]) for line in r.stdout.splitlines() if line.startswith('DYNAMIC_FIXTURE ')}
   spec=importlib.util.spec_from_file_location('dynamic_original_consumers',HERE/'host_tests/consumers.py');module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);logs['original-consumers']=module.verify(fixtures);print('DYNAMIC_ORIGINAL_CONSUMERS_PASS checks='+str(logs['original-consumers']['checks']))

 a.output.write_text(json.dumps({'manager_sha256':expected,'runtime_api_stubs':False,'inventory':inventory,'logs':logs,'scope':('frozen selector/484/v1-v2 pending regression with dynamic metadata prepared too' if a.selector_regression else 'old194 binary oracle versus current source: original485 pending compatibility' if a.upgrade_compat else '46 backend candidates: actual original engine/Store, synthetic BSON; public UI not integrated' if a.family else 'actual stock485 engine/Store and selected original consumers; not ART/game/render')},ensure_ascii=False,indent=2)+'\n')
if __name__=='__main__':main()
