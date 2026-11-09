"""Finite original Store/apply four-seam proof; no compile stubs at runtime."""
from pathlib import Path
import hashlib,json,subprocess,tempfile
ROOT=Path(__file__).resolve().parents[2];HERE=Path(__file__).resolve().parent

def main():
 java=ROOT/'toolchains/java/jdk-17.0.21+9/Contents/Home/bin';jar=ROOT/'analysis/project7/draw-policy-hook-v1/manager-translated-frames.jar';android=ROOT/'toolchains/android-sdk/platforms/android-32/android.jar';jsonjar=ROOT/'toolchains/json-20240303.jar'
 if hashlib.sha256(jar.read_bytes()).hexdigest()!='cfab06d2a803a91b62b597f1dadeae7a9a1e158453960a087efe690be2d5111e':raise ValueError('unsupported patched real engine')
 with tempfile.TemporaryDirectory() as tmp:
  out=Path(tmp)
  for n in ['stubs','production','harness']:(out/n).mkdir()
  def run(args):
   r=subprocess.run(list(map(str,args)),capture_output=True,text=True)
   if r.returncode:raise RuntimeError(r.stdout+r.stderr)
   return r
  base=[java/'javac','-source','8','-target','8','-Xlint:-options']
  run([*base,'-cp',':'.join(map(str,[jar,android])),'-d',out/'stubs',*(HERE/'compile_stubs').rglob('*.java')])
  run([*base,'-cp',':'.join(map(str,[out/'stubs',jar,android])),'-d',out/'production',*(HERE/'src').rglob('*.java')])
  cp=':'.join(map(str,[out/'production',jar,jsonjar]))
  run([*base,'-cp',cp+':'+str(android),'-d',out/'harness',*(HERE/'host_tests').rglob('*.java')])
  cmd=[java/'java','-Xverify:all','-cp',str(out/'harness')+':'+cp,'com.project7.localmanager.DrawPolicySeamHost',ROOT/'analysis/project7/fixed-component-v2-stage/assets',ROOT/'analysis/project7/extended-catalog-proof/resources.tsv',ROOT/'tools/project7_draw_ir/data/android-catalog-v2.tsv']
  result=run(cmd)
  import base64,importlib.util
  fixtures={line.split()[1]:base64.b64decode(line.split()[2]) for line in result.stdout.splitlines() if line.startswith('DRAW_FAILURE ')}
  spec=importlib.util.spec_from_file_location('draw_failure_consumer_probe',HERE/'host_tests/verify_original_consumers.py');probe=importlib.util.module_from_spec(spec);spec.loader.exec_module(probe)
  failure=probe.verify_failure_rpc(fixtures)
  print('\n'.join(line for line in result.stdout.splitlines() if not line.startswith('DRAW_FAILURE ')))
  print('ORIGINAL_FAILURE_RPC_CONSUMER_PASS '+json.dumps(failure,sort_keys=True))
if __name__=='__main__':main()
