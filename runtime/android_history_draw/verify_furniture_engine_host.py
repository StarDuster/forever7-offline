"""Actual furniture-hook HomeEngine/Store and original consumer finite proof."""
from pathlib import Path
import subprocess,tempfile,hashlib,argparse,json,base64,importlib.util,sys
ROOT=Path(__file__).resolve().parents[2];HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT))
JAR_SHA='9afdd92cf2f2670e6d5769a629c6efbd047b9ac25355ea4b7e9c7456af90aeb9'
def main():
 parser=argparse.ArgumentParser();parser.add_argument('--asset',type=Path,required=True);parser.add_argument('--output',type=Path,required=True);a=parser.parse_args()
 if a.output.exists():raise FileExistsError(a.output)
 jar=ROOT/'analysis/project7/furniture-hook-v3/manager-translated-frames.jar';android=ROOT/'toolchains/android-sdk/platforms/android-32/android.jar';jsonjar=ROOT/'toolchains/json-20240303.jar';java=ROOT/'toolchains/java/jdk-17.0.21+9/Contents/Home/bin'
 if hashlib.sha256(jar.read_bytes()).hexdigest()!=JAR_SHA:raise ValueError('wrong actual furniture manager jar')
 logs={}
 with tempfile.TemporaryDirectory() as tmp:
  out=Path(tmp)
  for name in ('core-api','core','api','prod','host'):(out/name).mkdir()
  def run(cmd,name):
   r=subprocess.run(list(map(str,cmd)),capture_output=True,text=True);logs[name]={'returncode':r.returncode,'stdout':r.stdout,'stderr':r.stderr}
   if r.returncode:raise RuntimeError(name+'\n'+r.stdout+r.stderr)
   return r
  base=[java/'javac','-source','8','-target','8','-Xlint:-options']
  for src,api,prod in ((ROOT/'runtime/android_draw_policy','core-api','core'),(HERE,'api','prod')):
   run([*base,'-cp',android,'-d',out/api,*(src/'compile_stubs').rglob('*.java')],api)
   run([*base,'-cp',str(android)+':'+str(out/api),'-d',out/prod,*(src/'src').rglob('*.java')],prod)
  cp=':'.join(map(str,[out/'prod',out/'core',jar,jsonjar]));run([*base,'-cp',cp+':'+str(android),'-d',out/'host',*(HERE/'host_tests').rglob('*.java')],'host-compile')
  r=run([java/'java','-Xverify:all','-cp',str(out/'host')+':'+cp,'com.project7.localmanager.HistoryFurnitureEngineHost',ROOT/'analysis/project7/fixed-component-v2-stage/assets',ROOT/'analysis/project7/extended-catalog-proof/resources.tsv',ROOT/'tools/project7_draw_ir/data/android-catalog-v2.tsv',ROOT/'runtime/project7_history_catalog/catalog-v2.tsv',a.asset],'actual-original-furniture')
  fixtures={line.split()[1]:base64.b64decode(line.split()[2]) for line in r.stdout.splitlines() if line.startswith('HISTORY_FURNITURE_FIXTURE ')}
  print('\n'.join(line for line in r.stdout.splitlines() if not line.startswith(('HISTORY_FURNITURE_FIXTURE ','HISTORY_FURNITURE_PENDING '))))
  spec=importlib.util.spec_from_file_location('original_furniture_consumer_probe',HERE/'host_tests/verify_furniture_consumers.py');module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
  pending=next(base64.b64decode(line.split()[1]) for line in r.stdout.splitlines() if line.startswith('HISTORY_FURNITURE_PENDING '));logs['original-reward-consumers']=module.verify_reward_paths(fixtures,pending);print('HISTORY_FURNITURE_ORIGINAL_REWARD_PASS checks='+str(logs['original-reward-consumers']['checks']));wire=module.old.bson(fixtures['single'])['i']['t'];logs['original-furniture-consumers']=module.verify(fixtures,wire);print('HISTORY_FURNITURE_ORIGINAL_RPC_PASS checks='+str(logs['original-furniture-consumers']['checks']))
 a.output.write_text(json.dumps({'actual_manager_sha256':JAR_SHA,'asset_sha256':hashlib.sha256(a.asset.read_bytes()).hexdigest(),'no_runtime_stubs':True,'logs':logs,'scope':'original HomeEngine/Store and selected original RPC consumers, synthetic profile only; no ART/render/game'},ensure_ascii=False,indent=2)+'\n')
if __name__=='__main__':main()
