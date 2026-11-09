"""Finite original friendship engine/Gateway/Store host proof; no runtime API stubs."""
from pathlib import Path
import argparse,base64,hashlib,json,subprocess,tempfile,importlib.util
ROOT=Path(__file__).resolve().parents[2];HERE=Path(__file__).resolve().parent
SHA='2ed4ab9dea04f1b90947415da5ebd405f44f20512b157d74805130603accbb0a'
def main():
 p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);a=p.parse_args()
 if a.output.exists():raise FileExistsError(a.output)
 jar=ROOT/'analysis/project7/dream-lifecycle-hook-v1/manager-translated-frames.jar';android=ROOT/'toolchains/android-sdk/platforms/android-32/android.jar';jsonjar=ROOT/'toolchains/json-20240303.jar';java=ROOT/'toolchains/java/jdk-17.0.21+9/Contents/Home/bin'
 if hashlib.sha256(jar.read_bytes()).hexdigest()!=SHA:raise ValueError('unexpected current manager')
 logs={}
 with tempfile.TemporaryDirectory() as t:
  out=Path(t)
  for n in ('core-api','core','history-api','history','rpc-api','rpc','host'):(out/n).mkdir()
  def run(cmd,name):
   r=subprocess.run(list(map(str,cmd)),capture_output=True,text=True);logs[name]={'returncode':r.returncode,'stdout':r.stdout,'stderr':r.stderr}
   if r.returncode:raise RuntimeError(name+'\n'+'\n'.join(x for x in r.stdout.splitlines() if not x.startswith('FRIEND_FIXTURE '))+r.stderr)
   return r
  base=[java/'javac','-source','8','-target','8','-Xlint:-options']
  for src,api,prod in [(ROOT/'runtime/android_draw_policy','core-api','core'),(ROOT/'runtime/android_history_draw','history-api','history'),(ROOT/'runtime/android_core_rpc','rpc-api','rpc')]:
   run([*base,'-cp',android,'-d',out/api,*(src/'compile_stubs').rglob('*.java')],api)
   run([*base,'-cp',str(android)+':'+str(out/api),'-d',out/prod,*(src/'src').rglob('*.java')],prod)
  cp=':'.join(map(str,[out/'history',out/'core',out/'rpc',jar,jsonjar]));run([*base,'-cp',cp+':'+str(android),'-d',out/'host',*(HERE/'host_tests').rglob('*.java')],'host-compile')
  r=run([java/'java','-Xverify:all','-cp',str(out/'host')+':'+cp,'com.project7.localmanager.FriendEngineHost',ROOT/'analysis/project7/fixed-component-v2-stage/assets',ROOT/'analysis/project7/extended-catalog-proof/resources.tsv',ROOT/'tools/project7_draw_ir/data/android-catalog-v2.tsv',ROOT/'runtime/project7_history_catalog/catalog-v2.tsv',ROOT/'runtime/project7_history_catalog/furniture-v1.tsv'],'actual-original-friend')
  print('\n'.join(x for x in r.stdout.splitlines() if not x.startswith('FRIEND_FIXTURE ')))
  fixtures={}
  for line in r.stdout.splitlines():
   if line.startswith('FRIEND_FIXTURE '):
    _,name,parts=line.split(' ',2);fixtures[name]=[(base64.b64decode(d),base64.b64decode(p)) for d,p in (part.split(':',1) for part in parts.split(','))]
  spec=importlib.util.spec_from_file_location('friend_original_consumers',HERE/'host_tests/consumers.py');module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);logs['original-consumers']=module.verify(fixtures);print('FRIEND_ORIGINAL_CONSUMERS_PASS checks='+str(logs['original-consumers']['checks']))
 a.output.write_text(json.dumps({'manager_sha256':SHA,'runtime_api_stubs':False,'logs':logs,'scope':'actual stock friendship engine/Gateway/Store, synthetic BSON; not ART/game/render'},ensure_ascii=False,indent=2)+'\n')
if __name__=='__main__':main()
