"""Original Store v1->v2 persistence proof using byte-pinned frozen v1 policy source."""
from pathlib import Path
import subprocess,tempfile,hashlib,json,argparse
ROOT=Path(__file__).resolve().parents[2];HERE=Path(__file__).resolve().parent
OLD_SHA='2a6255920030493c188e1159052add66d26765ee451ed761fe05f745df981a34'
def main():
 p=argparse.ArgumentParser();p.add_argument('--v1-source',type=Path,default=HERE/'host_tests/fixtures/HistoryDrawPolicy-v1.java.txt');p.add_argument('--output',type=Path,required=True);a=p.parse_args()
 if a.output.exists():raise FileExistsError(a.output)
 source=a.v1_source.read_bytes()
 if hashlib.sha256(source).hexdigest()!=OLD_SHA:raise ValueError('wrong frozen v1 source')
 java=ROOT/'toolchains/java/jdk-17.0.21+9/Contents/Home/bin';android=ROOT/'toolchains/android-sdk/platforms/android-32/android.jar';jar=ROOT/'analysis/project7/history-hook-v1/manager-translated-frames.jar';jsonjar=ROOT/'toolchains/json-20240303.jar'
 if hashlib.sha256(jar.read_bytes()).hexdigest()!='835a34a8cd6545d8204b5c7b77ea2bee515961e9685a6f837732670f0a0fc7b8':raise ValueError('wrong real engine jar')
 logs={}
 with tempfile.TemporaryDirectory() as t:
  out=Path(t)
  def run(cmd,name):
   r=subprocess.run(list(map(str,cmd)),capture_output=True,text=True);logs[name]={'returncode':r.returncode,'stdout':r.stdout,'stderr':r.stderr}
   if r.returncode:raise RuntimeError(name+'\n'+r.stdout+r.stderr)
  base=[java/'javac','-source','8','-target','8','-Xlint:-options']
  for name in ('core-api','core','history-api','v1','v2','host'):(out/name).mkdir()
  core=ROOT/'runtime/android_draw_policy'
  for path,api,dest in ((core,'core-api','core'),(HERE,'history-api','v2')):
   run([*base,'-cp',android,'-d',out/api,*(path/'compile_stubs').rglob('*.java')],api)
   run([*base,'-cp',str(android)+':'+str(out/api),'-d',out/dest,*(path/'src').rglob('*.java')],dest)
  old=out/'HistoryDrawPolicy.java';old.write_bytes(source)
  run([*base,'-cp',str(android)+':'+str(out/'history-api')+':'+str(out/'v2'),'-d',out/'v1',old],'v1-source')
  cp=':'.join(map(str,[out/'v2',out/'core',jar,jsonjar]));seams=[HERE/'host_tests/android/content/Context.java',HERE/'host_tests/android/content/res/AssetManager.java',HERE/'host_tests/android/system/Os.java',HERE/'host_tests/android/system/ErrnoException.java',HERE/'host_tests/com/project7/localmanager/HistoryV1ReloadHost.java']
  run([*base,'-cp',cp+':'+str(android),'-d',out/'host',*seams],'host-compile')
  common=[ROOT/'analysis/project7/fixed-component-v2-stage/assets',ROOT/'analysis/project7/extended-catalog-proof/resources.tsv',ROOT/'tools/project7_draw_ir/data/android-catalog-v2.tsv']
  run([java/'java','-Xverify:all','-cp',str(out/'host')+':'+str(out/'v1')+':'+cp,'com.project7.localmanager.HistoryV1ReloadHost','create',*common,ROOT/'runtime/project7_history_catalog/catalog-v1.tsv',out/'profile',ROOT/'runtime/project7_history_catalog/furniture-v1.tsv'],'v1-original-store-create')
  run([java/'java','-Xverify:all','-cp',str(out/'host')+':'+cp,'com.project7.localmanager.HistoryV1ReloadHost','consume',*common,ROOT/'runtime/project7_history_catalog/catalog-v2.tsv',out/'profile',ROOT/'runtime/project7_history_catalog/furniture-v1.tsv'],'v2-original-store-reload')
 a.output.write_text(json.dumps({'v1_policy_sha256':OLD_SHA,'no_runtime_stubs':True,'logs':logs,'scope':'two separate verified JVMs, original Store; synthetic profile only, no ART/UI/game'},indent=2)+'\n');print('HISTORY_ACTUAL_V1_TO_V2_STORE_PASS')
if __name__=='__main__':main()
