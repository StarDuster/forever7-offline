"""Finite synthetic original354 preservation and patched new-group refusal proof."""
from pathlib import Path
import argparse,hashlib,subprocess,tempfile,importlib.util,json,base64
ROOT=Path(__file__).resolve().parents[2];HERE=Path(__file__).resolve().parent

def main():
 p=argparse.ArgumentParser();p.add_argument('--jar',type=Path,default=ROOT/'analysis/project7/host-original-engine/manager-translated-frames.jar');p.add_argument('--sha256',default='723440ecca7b479a9e1f1233222bbff92bfbf41dda18cdcd38d37a4d7ccaa685');p.add_argument('--expect-block',action='store_true');p.add_argument('--report-output',type=Path);a=p.parse_args()
 if hashlib.sha256(a.jar.read_bytes()).hexdigest()!=a.sha256:raise ValueError('host JAR SHA mismatch')
 java=ROOT/'toolchains/java/jdk-17.0.21+9/Contents/Home/bin';android=ROOT/'toolchains/android-sdk/platforms/android-32/android.jar';jsonjar=ROOT/'toolchains/json-20240303.jar'
 with tempfile.TemporaryDirectory() as tmp:
  out=Path(tmp)
  for n in ['api','production','harness']:(out/n).mkdir()
  def run(args):
   r=subprocess.run(list(map(str,args)),capture_output=True,text=True)
   if r.returncode:raise RuntimeError(r.stdout+r.stderr)
   return r
  base=[java/'javac','-source','8','-target','8','-Xlint:-options']
  run([*base,'-cp',android,'-d',out/'api',*(HERE/'compile_stubs').rglob('*.java')])
  run([*base,'-cp',str(out/'api')+':'+str(android),'-d',out/'production',*(HERE/'src').rglob('*.java')])
  cp=':'.join(map(str,[out/'production',a.jar,jsonjar]))
  run([*base,'-cp',cp+':'+str(android),'-d',out/'harness',*(HERE/'host_tests').rglob('*.java')])
  cmd=[java/'java','-Xverify:all','-Dp7.newbie.block.expected='+str(a.expect_block).lower(),'-cp',str(out/'harness')+':'+cp,'com.project7.localmanager.Newbie354BlockHost',ROOT/'analysis/project7/extended-catalog-proof/resources.tsv']
  result=run(cmd);evidence={'jar_sha256':a.sha256,'expect_block':a.expect_block,'command':list(map(str,cmd)),'runtime_compile_stubs_included':False,'stdout':result.stdout,'failure_consumers':{}};print('\n'.join(line for line in result.stdout.splitlines() if not line.startswith('NEWBIE_FAILURE ')))
  if a.expect_block:
   spec=importlib.util.spec_from_file_location('original_failure_consumers',HERE/'host_tests/verify_original_consumers.py');probe=importlib.util.module_from_spec(spec);spec.loader.exec_module(probe)
   # Reuse original decorator/arg/default/callback probe with explicit wire t354.
   groups={}
   for line in result.stdout.splitlines():
    if line.startswith('NEWBIE_FAILURE '):
     _,ct,label,encoded=line.split();groups.setdefault(ct,{})[label]=base64.b64decode(encoded)
   for ct,fixtures in groups.items():
    proof=probe.verify_failure_rpc(fixtures,wire_t=354);evidence['failure_consumers'][ct]=proof;print('NEWBIE354_FAILURE_RPC '+ct+' '+json.dumps(proof,sort_keys=True))
  if a.report_output is not None:
   with a.report_output.open('x') as f:json.dump(evidence,f,ensure_ascii=False,indent=2);f.write('\n')
if __name__=='__main__':main()
