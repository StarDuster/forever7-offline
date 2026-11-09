"""Compile production separately from stubs; run against verified original engine.
Synthetic BSON only; no user profiles, game code, ART, D8 or APK assembly.
"""
from pathlib import Path
import hashlib,json,subprocess,tempfile
ROOT=Path(__file__).resolve().parents[2];HERE=Path(__file__).resolve().parent

def main():
 java=ROOT/'toolchains/java/jdk-17.0.21+9/Contents/Home/bin';jar=ROOT/'analysis/project7/host-original-engine/manager-translated-frames.jar';android=ROOT/'toolchains/android-sdk/platforms/android-32/android.jar';jsonjar=ROOT/'toolchains/json-20240303.jar'
 if hashlib.sha256(jar.read_bytes()).hexdigest()!='723440ecca7b479a9e1f1233222bbff92bfbf41dda18cdcd38d37a4d7ccaa685':raise ValueError('unsupported real engine')
 with tempfile.TemporaryDirectory() as tmp:
  out=Path(tmp)
  for n in ['stubs','production','harness']:(out/n).mkdir()
  def run(args):
   r=subprocess.run(list(map(str,args)),capture_output=True,text=True)
   if r.returncode:raise RuntimeError(r.stdout+r.stderr)
   return r
  base=[java/'javac','-source','8','-target','8','-Xlint:-options']
  run([*base,'-cp',str(jar)+':'+str(android),'-d',out/'stubs',*(HERE/'compile_stubs').rglob('*.java')])
  run([*base,'-cp',':'.join(map(str,[out/'stubs',jar,android])),'-d',out/'production',*(HERE/'src').rglob('*.java')])
  cp=':'.join(map(str,[out/'production',jar,jsonjar]))
  run([*base,'-cp',cp+':'+str(android),'-d',out/'harness',*(HERE/'host_tests').rglob('*.java')])
  result=run([java/'java','-Xverify:all','-cp',str(out/'harness')+':'+cp,'com.project7.localmanager.DrawPolicyHost',ROOT/'tools/project7_draw_ir/data/android-catalog-v2.tsv',ROOT/'analysis/project7/extended-catalog-proof/resources.tsv'])
  import base64,importlib.util
  fixtures={line.split()[1]:base64.b64decode(line.split()[2]) for line in result.stdout.splitlines() if line.startswith('DRAW_FIXTURE ')}
  spec=importlib.util.spec_from_file_location('draw_consumer_probe',HERE/'host_tests/verify_original_consumers.py');probe=importlib.util.module_from_spec(spec);spec.loader.exec_module(probe)
  consumer=probe.verify(fixtures)
  print('\n'.join(line for line in result.stdout.splitlines() if not line.startswith('DRAW_FIXTURE ')))
  print('ORIGINAL_CONSUMER_HOST_PASS '+json.dumps(consumer,sort_keys=True))
if __name__=='__main__':main()
