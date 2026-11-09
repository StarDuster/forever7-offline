"""Finite host Python protocol and extracted-original check leaves; no native acceptance."""
from pathlib import Path
import importlib.util,json,os,sys,tempfile,types,unittest
ROOT=Path(__file__).resolve().parents[2]
spec=importlib.util.spec_from_file_location('repair_hook',ROOT/'runtime/project7_startup_hook.py');hook=importlib.util.module_from_spec(spec);spec.loader.exec_module(hook)
NS=types.SimpleNamespace

def write_launch(root,generation='a'*32):
    text=json.dumps({'schema':1,'generation':generation},sort_keys=True,separators=(',',':')).encode('ascii')
    (root/'.p7-launch.json').write_bytes(text.ljust(256,b' '))
def patch(root):
    namespace={'_q7_snapshot_path':lambda:str(root/'snapshot.json')}
    exec('def original_verify():\n    return "unchanged"',namespace)
    return NS(_q7_verify_offline_resources=namespace['original_verify'],pconst=NS())

class RepairNotificationTests(unittest.TestCase):
    def test_fixed_wire_and_engine_generation_is_captured_once(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);write_launch(root);p=patch(root);events=[];policy=hook.StartupPolicy(p,'',events.append)
            write_launch(root,'b'*32) # same Python engine must never adopt another launch.
            policy.repair('resource_verify_failed')
            raw=(root/'.p7-repair-request.json').read_bytes();self.assertEqual(len(raw),256)
            self.assertEqual(raw.rstrip(),b'{"code":"resource_verify_failed","generation":"aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa","schema":1}')
            self.assertEqual(p.pconst.Q7_STARTUP_REPAIR_REQUIRED,'resource_verify_failed');self.assertEqual(events,['resource_verify_failed'])
            before=raw;policy.repair('unlisted_test_code');self.assertEqual((root/'.p7-repair-request.json').read_bytes(),before)
            self.assertFalse(list(root.glob('.p7-repair-request.tmp-*')))

    def test_missing_malformed_or_write_failure_keeps_original_repair(self):
        for bad in [None,b'{}',b' '*257,b'{"generation":"bad","schema":1}'.ljust(256,b' ')]:
            with tempfile.TemporaryDirectory() as d:
                root=Path(d)
                if bad is not None:(root/'.p7-launch.json').write_bytes(bad)
                p=patch(root);events=[];policy=hook.StartupPolicy(p,'',events.append);policy.repair('resource_query_failed')
                self.assertEqual(p.pconst.Q7_STARTUP_REPAIR_REQUIRED,'resource_query_failed');self.assertEqual(events,['resource_query_failed']);self.assertFalse((root/'.p7-repair-request.json').exists())
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);write_launch(root);p=patch(root);policy=hook.StartupPolicy(p,'');old=hook.os.rename
            try:
                hook.os.rename=lambda *a:(_ for _ in ()).throw(OSError('synthetic rename fault'))
                policy.repair('resource_download_failed')
            finally:hook.os.rename=old
            self.assertEqual(p.pconst.Q7_STARTUP_REPAIR_REQUIRED,'resource_download_failed');self.assertFalse((root/'.p7-repair-request.json').exists());self.assertFalse(list(root.glob('.p7-repair-request.tmp-*')))

    def test_original_check_failure_and_success_results_unchanged(self):
        # Reuse existing harness that extracts the actual P7 functions. Native check is
        # explicitly its finite check_npk/check_raw leaf, never claimed real C_file.
        sys.path.insert(0,str(ROOT/'tests'))
        from test_project7_startup_hook import ResourceHarness
        h=ResourceHarness();root=h.path.parent;write_launch(root)
        h.policy.repair_launch=hook._capture_repair_launch(patch(root));h.bad=True
        with self.assertRaises(ValueError):h.patch._q7_verify_offline_resources()
        self.assertIn('native_check',h.events);self.assertIsNone(h.policy.activation);self.assertFalse(hasattr(h.pconst,'INDEX'))
        raw=(root/'.p7-repair-request.json').read_bytes();self.assertEqual(json.loads(raw)['code'],'resource_verify_failed')
        h2=ResourceHarness();root2=h2.path.parent;write_launch(root2);h2.policy.repair_launch=hook._capture_repair_launch(patch(root2))
        state=h2.patch._q7_verify_offline_resources();self.assertEqual(state,h2.state);self.assertFalse((root2/'.p7-repair-request.json').exists())
        h2.patch._q7_activate_game_mode(state);self.assertTrue(h2.policy.live());self.assertFalse((root2/'.p7-repair-request.json').exists())

if __name__=='__main__':unittest.main()
