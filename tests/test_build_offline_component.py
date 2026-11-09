import _paths  # noqa: E402,F401
import subprocess, sys, tempfile, types, unittest
from pathlib import Path
from unittest import mock
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'offline'/'current'/'tools'))
import build_offline_project as build

def args(**kw):
    base=dict(component=None,component_offline_input=None,component_url=None)
    base.update(kw); return types.SimpleNamespace(**base)

class ComponentPriorityTests(unittest.TestCase):
    def test_public_launcher_imports_when_tools_is_first_on_sys_path(self):
        with tempfile.TemporaryDirectory() as d:
            program = (
                "import sys;"
                "sys.path.insert(0, %r);"
                "import build_offline_project as b;"
                "assert callable(b.select_component);"
                "assert callable(b.main)"
            ) % str(ROOT / 'tools')
            result = subprocess.run([sys.executable, '-c', program], cwd=d,
                                    capture_output=True, text=True, timeout=60)
            self.assertEqual(result.returncode, 0, result.stderr)

    def test_public_launcher_cli_runs_from_arbitrary_cwd(self):
        with tempfile.TemporaryDirectory() as d:
            result = subprocess.run(
                [sys.executable, str(ROOT / 'tools' / 'build_offline_project.py'), '--help'],
                cwd=d, capture_output=True, text=True, timeout=60)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn('--component-offline-input', result.stdout)
    def test_explicit_url_failure_does_not_fall_back_to_vendor(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d); vendor=root/'vendor/project7/component-v2.10.1.zip'; vendor.parent.mkdir(parents=True); vendor.write_bytes(b'vendor')
            with mock.patch('project7_fetch_component.resolve', side_effect=ValueError('explicit URL failed')) as resolve:
                with self.assertRaisesRegex(ValueError,'explicit URL failed'):
                    build.select_component(args(component_url='https://invalid.example/x.zip'),root=root,environ={})
                resolve.assert_called_once_with('https://invalid.example/x.zip',None)

    def test_explicit_offline_input_has_priority_over_vendor_and_url(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d); vendor=root/'vendor/project7/component-v2.10.1.zip'; vendor.parent.mkdir(parents=True); vendor.write_bytes(b'vendor')
            chosen=root/'chosen.zip'; chosen.write_bytes(b'chosen')
            with mock.patch('project7_fetch_component.resolve', return_value=chosen) as resolve:
                got=build.select_component(args(component_offline_input=chosen,component_url='https://invalid.example/x.zip'),root=root,environ={})
                self.assertEqual(got,chosen)
                resolve.assert_called_once_with(None,chosen)

    def test_bad_explicit_offline_input_is_not_hidden_by_real_cache(self):
        import shutil
        import project7_fetch_component as fetch
        with tempfile.TemporaryDirectory() as d:
            root=Path(d); cache=root/'cache.zip'
            source=ROOT/'.offline-deps/component-v2.10.1.zip'
            if not source.is_file(): self.skipTest('pinned component cache absent')
            shutil.copyfile(source,cache)
            bad=root/'bad.zip'; bad.write_bytes(b'not-the-component')
            with mock.patch.object(fetch,'CACHE',cache):
                with self.assertRaisesRegex(ValueError,'Offline Project7 component size/hash mismatch'):
                    build.select_component(args(component_offline_input=bad),root=root,environ={})

    def test_explicit_component_has_highest_priority(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d); chosen=root/'component.zip'; chosen.write_bytes(b'chosen')
            with mock.patch('project7_fetch_component.resolve') as resolve:
                self.assertEqual(build.select_component(args(component=chosen,component_url='https://invalid.example/x.zip'),root=root,environ={}),chosen)
                resolve.assert_not_called()

    def test_vendor_is_only_fallback(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d); vendor=root/'vendor/project7/component-v2.10.1.zip'; vendor.parent.mkdir(parents=True); vendor.write_bytes(b'vendor')
            with mock.patch('project7_fetch_component.resolve') as resolve:
                self.assertEqual(build.select_component(args(),root=root,environ={}),vendor)
                resolve.assert_not_called()

if __name__=='__main__': unittest.main()
