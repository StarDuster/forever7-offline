"""Source-only production compilation + deterministic compact graph boundary checks."""
from pathlib import Path
import subprocess,tempfile
ROOT=Path(__file__).resolve().parents[2];HERE=Path(__file__).resolve().parent

def main():
 from tools.project7_history_catalog import project
 data,_=project();java=ROOT/'toolchains/java/jdk-17.0.21+9/Contents/Home/bin';android=ROOT/'toolchains/android-sdk/platforms/android-32/android.jar';jar=ROOT/'analysis/project7/newbie354-hook-v1/manager-translated-frames.jar'
 with tempfile.TemporaryDirectory() as t:
  p=Path(t)
  for name in ['api','prod','host']:(p/name).mkdir()
  def run(cmd):
   r=subprocess.run(list(map(str,cmd)),capture_output=True,text=True)
   if r.returncode:raise RuntimeError(r.stdout+r.stderr)
   return r
  base=[java/'javac','-source','8','-target','8','-Xlint:-options']
  run([*base,'-cp',android,'-d',p/'api',*(HERE/'compile_stubs').rglob('*.java')]);run([*base,'-cp',str(android)+':'+str(p/'api'),'-d',p/'prod',*(HERE/'src').rglob('*.java')])
  run([*base,'-cp',str(p/'prod')+':'+str(jar),'-d',p/'host',HERE/'host_tests/com/project7/localmanager/HistoryCatalogHost.java',HERE/'host_tests/com/project7/localmanager/HistoryFurnitureCatalogHost.java'])
  (p/'catalog.tsv').write_bytes(data)
  result=run([java/'java','-Xverify:all','-cp',':'.join(map(str,[p/'host',p/'prod',jar])),'com.project7.localmanager.HistoryCatalogHost',p/'catalog.tsv'])
  print(result.stdout,end='')
  furniture=run([java/'java','-Xverify:all','-cp',':'.join(map(str,[p/'host',p/'prod',jar])),'com.project7.localmanager.HistoryFurnitureCatalogHost',ROOT/'runtime/project7_history_catalog/furniture-v1.tsv'])
  print(furniture.stdout,end='')
if __name__=='__main__':
 import sys
 sys.path.insert(0,str(ROOT))
 main()
