"""Finite selector/current stock484 proof; source-only APIs, no runtime stubs."""
from pathlib import Path
import argparse,base64,hashlib,json,subprocess,tempfile,importlib.util
ROOT=Path(__file__).resolve().parents[2];HERE=Path(__file__).resolve().parent
SHA='1be1a7e09c5a2e42d31f9deff54c1d942657fca695c1a996579eefecf365e6fa'
ORIGINAL_SHA='af930ec43effa7ee491d5dd391e4ff338a7e540f25c7bed43f4a9fb54a002e78'
def main():
 p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);p.add_argument('--original-caller',action='store_true');a=p.parse_args();expected=ORIGINAL_SHA if a.original_caller else SHA
 if a.output.exists():raise FileExistsError(a.output)
 jar=ROOT/('analysis/project7/event-reset-week-hook-v2/manager-translated-frames.jar' if a.original_caller else 'analysis/project7/selector-hook-v1/manager-translated-frames.jar');android=ROOT/'toolchains/android-sdk/platforms/android-32/android.jar';jsonjar=ROOT/'toolchains/json-20240303.jar';java=ROOT/'toolchains/java/jdk-17.0.21+9/Contents/Home/bin'
 if hashlib.sha256(jar.read_bytes()).hexdigest()!=expected:raise ValueError('unexpected current manager')
 logs={}
 with tempfile.TemporaryDirectory() as t:
  out=Path(t)
  for n in ('core-api','core','history-api','history','rpc-api','rpc','selector-api','selector','host'):(out/n).mkdir()
  def run(cmd,name):
   r=subprocess.run(list(map(str,cmd)),capture_output=True,text=True);logs[name]={'returncode':r.returncode,'stdout':r.stdout,'stderr':r.stderr}
   if r.returncode:raise RuntimeError(name+'\n'+'\n'.join(x for x in r.stdout.splitlines() if not x.startswith('SELECTOR_FIXTURE '))+r.stderr)
   return r
  base=[java/'javac','-source','8','-target','8','-Xlint:-options']
  for src,api,prod in [(ROOT/'runtime/android_draw_policy','core-api','core'),(ROOT/'runtime/android_core_rpc','rpc-api','rpc')]:
   run([*base,'-cp',android,'-d',out/api,*(src/'compile_stubs').rglob('*.java')],api)
   run([*base,'-cp',str(android)+':'+str(out/api),'-d',out/prod,*(src/'src').rglob('*.java')],prod)
  run([*base,'-cp',android,'-d',out/'selector-api',*(HERE/'compile_stubs').rglob('*.java')],'selector-api')
  run([*base,'-cp',':'.join(map(str,[out/'selector-api',android])),'-d',out/'selector',*(ROOT/'runtime/android_history_draw/src').rglob('*.java'),*(HERE/'src').rglob('*.java')],'history-selector-source-only')
  cp=':'.join(map(str,[out/'selector',out/'history',out/'core',out/'rpc',jar,jsonjar]));run([*base,'-cp',cp+':'+str(android),'-d',out/'host',*(HERE/'host_tests').rglob('*.java')],'host-compile')
  r=run([java/'java','-Xverify:all','-Dp7.selector.caller='+str(not a.original_caller).lower(),'-cp',str(out/'host')+':'+cp,'com.project7.localmanager.SelectorEngineHost',ROOT/'analysis/project7/fixed-component-v2-stage/assets',ROOT/'analysis/project7/extended-catalog-proof/resources.tsv',ROOT/'tools/project7_draw_ir/data/android-catalog-v2.tsv',ROOT/'runtime/project7_history_catalog/catalog-v3.tsv',ROOT/'runtime/project7_history_catalog/furniture-v1.tsv',ROOT/'runtime/project7_selector_catalog/catalog-v1.tsv'],'actual-original-selector')
  print('\n'.join(x for x in r.stdout.splitlines() if not x.startswith('SELECTOR_FIXTURE ')))

  fixtures={line.split()[1]:base64.b64decode(line.split()[2]) for line in r.stdout.splitlines() if line.startswith('SELECTOR_FIXTURE ')}
  spec=importlib.util.spec_from_file_location('selector_original_consumers',HERE/'host_tests/consumers.py');module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);logs['original-consumers']=module.verify(fixtures);print('SELECTOR_ORIGINAL_CONSUMERS_PASS checks='+str(logs['original-consumers']['checks']))

 a.output.write_text(json.dumps({'manager_sha256':expected,'runtime_api_stubs':False,'logs':logs,'scope':'actual stock selector484 engine/Store, synthetic BSON; not ART/game/render'},ensure_ascii=False,indent=2)+'\n')
if __name__=='__main__':main()
