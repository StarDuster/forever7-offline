"""Interop leaf: actual Python capture/notify functions, Java-created launch marker."""
from pathlib import Path
import importlib.util,sys,types
ROOT=Path(__file__).resolve().parents[3]
spec=importlib.util.spec_from_file_location('interop_hook',ROOT/'runtime/project7_startup_hook.py');hook=importlib.util.module_from_spec(spec);spec.loader.exec_module(hook)
namespace={'_q7_snapshot_path':lambda:str(Path(sys.argv[1])/'snapshot.json')}
exec('def verify():\n    return None',namespace)
launch=hook._capture_repair_launch(types.SimpleNamespace(_q7_verify_offline_resources=namespace['verify']))
assert launch is not None
hook._notify_repair(launch,'resource_verify_failed')
