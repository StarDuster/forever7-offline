"""Actual history-seam manager + original Store finite proof, no stub runtime."""
from pathlib import Path
import subprocess,tempfile,hashlib,argparse,json,base64,importlib.util
ROOT=Path(__file__).resolve().parents[2];HERE=Path(__file__).resolve().parent
JAR_SHA='9afdd92cf2f2670e6d5769a629c6efbd047b9ac25355ea4b7e9c7456af90aeb9'

def main():
 parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path);a=parser.parse_args()
 jar=ROOT/'analysis/project7/furniture-hook-v3/manager-translated-frames.jar';jsonjar=ROOT/'toolchains/json-20240303.jar';android=ROOT/'toolchains/android-sdk/platforms/android-32/android.jar';java=ROOT/'toolchains/java/jdk-17.0.21+9/Contents/Home/bin'
 if hashlib.sha256(jar.read_bytes()).hexdigest()!=JAR_SHA:raise ValueError('wrong actual history JAR')
 if a.output is not None and a.output.exists():raise FileExistsError(a.output)
 with tempfile.TemporaryDirectory() as t:
  out=Path(t)
  for n in ['history-api','history-prod','core-api','core-prod','host']:(out/n).mkdir()
  logs={}
  def run(cmd,name):
   r=subprocess.run(list(map(str,cmd)),capture_output=True,text=True);logs[name]={'stdout':r.stdout,'stderr':r.stderr,'returncode':r.returncode}
   if r.returncode:raise RuntimeError(name+'\n'+r.stdout+r.stderr)
   return r
  base=[java/'javac','-source','8','-target','8','-Xlint:-options']
  for source,api,prod in [(ROOT/'runtime/android_draw_policy','core-api','core-prod'),(HERE,'history-api','history-prod')]:
   run([*base,'-cp',android,'-d',out/api,*(source/'compile_stubs').rglob('*.java')],api)
   run([*base,'-cp',str(android)+':'+str(out/api),'-d',out/prod,*(source/'src').rglob('*.java')],prod)
  cp=':'.join(map(str,[out/'history-prod',out/'core-prod',jar,jsonjar]))
  run([*base,'-cp',cp+':'+str(android),'-d',out/'host',*(HERE/'host_tests').rglob('*.java')],'compile-harness')
  cmd=[java/'java','-Xverify:all','-cp',str(out/'host')+':'+cp,'com.project7.localmanager.HistoryEngineHost',ROOT/'analysis/project7/fixed-component-v2-stage/assets',ROOT/'analysis/project7/extended-catalog-proof/resources.tsv',ROOT/'tools/project7_draw_ir/data/android-catalog-v2.tsv',ROOT/'runtime/project7_history_catalog/catalog-v2.tsv',ROOT/'runtime/project7_history_catalog/furniture-v1.tsv']
  r=run(cmd,'actual-engine-store')
  print('\n'.join(line for line in r.stdout.splitlines() if not line.startswith(('HISTORY_FAILURE ','HISTORY_GIFT_FIXTURE '))))
  failures={line.split()[1]:base64.b64decode(line.split()[2]) for line in r.stdout.splitlines() if line.startswith('HISTORY_FAILURE ')}
  spec=importlib.util.spec_from_file_location('actual_original_history_consumers',ROOT/'runtime/android_draw_policy/host_tests/verify_original_consumers.py');probe=importlib.util.module_from_spec(spec);spec.loader.exec_module(probe)
  cleanup=probe.verify_failure_rpc(failures,wire_t=17);logs['original-failure-rpc-consumer']=cleanup
  print('HISTORY_ORIGINAL_FAILURE_RPC_PASS '+json.dumps(cleanup,sort_keys=True))
  evidence={'original_history_manager_sha256':JAR_SHA,'runtime_compile_stubs_included':False,'android_sdk_jar_at_runtime':False,'command':list(map(str,cmd)),'logs':logs,'source_files':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in (HERE/'src').rglob('*.java')},'scope':'actual translated stock engine/Store, synthetic profile only; no ART/renderer/game/SDK-native acceptance'}
  if a.output is not None:
   with a.output.open('x') as f:json.dump(evidence,f,ensure_ascii=False,indent=2);f.write('\n')
if __name__=='__main__':main()
