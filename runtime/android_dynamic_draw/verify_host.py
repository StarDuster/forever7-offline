"""Independent data/slot/reducer checkpoint, explicitly not a stock Store proof."""
import argparse,hashlib,importlib.util,json,subprocess,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];HERE=Path(__file__).resolve().parent

def main():
 p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);a=p.parse_args()
 if a.output.exists():raise FileExistsError(a.output)
 java=ROOT/'toolchains/java/jdk-17.0.21+9/Contents/Home/bin';logs={}
 def run(command,name):
  r=subprocess.run(list(map(str,command)),cwd=ROOT,capture_output=True,text=True);logs[name]={'returncode':r.returncode,'stdout':r.stdout,'stderr':r.stderr}
  if r.returncode:raise RuntimeError(name+'\n'+r.stderr)
 with tempfile.TemporaryDirectory() as td:
  run([java/'javac','-source','8','-target','8','-Xlint:-options','-d',td,HERE/'src/com/project7/localmanager/DynamicSlotPlan.java',HERE/'src/com/project7/localmanager/DynamicTransition.java',*sorted((HERE/'host_tests').glob('*.java'))],'javac')
  for name in ('DynamicSlotPlanHost','DynamicTransitionHost'):run([java/'java','-Xverify:all','-cp',td,name],name)
 path=HERE/'host_tests/verify_slot_projection.py';s=importlib.util.spec_from_file_location('dynamic_slot',path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);logs['original-slot-projection']=m.verify()
 report={'schema':'project7-dynamic-preflight-host-v1','logs':logs,'stock_engine_executed':False,'no_runtime_readiness_claim':True,'scope':'pure immutable plan/reducer and selected original640 function bodies with inert native seams; not grant/Store/typed-sync proof'}
 a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print('PASS dynamic preflight (not original Store)')
if __name__=='__main__':main()
