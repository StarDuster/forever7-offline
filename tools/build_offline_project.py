"""Public single-command build entry; implementation lives in offline/tools.

This launcher keeps the documented `tools/build_offline_project.py` path stable.
It inserts the source-tree roots before importing the implementation, so the
entry works from any current directory without duplicating build logic.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
for _path in (ROOT, ROOT / 'offline' / 'tools', ROOT / 'project7_bridge' / 'tools',
              ROOT / 'offline' / 'runtime', ROOT / 'project7_bridge' / 'runtime',
              ROOT / 'project7_bridge' / 'android'):
    if str(_path) not in sys.path:
        sys.path.insert(0, str(_path))

# Load the implementation under a unique module identity.  A plain
# `import build_offline_project` here would resolve back to this partially
# initialized launcher when tools/ is first on sys.path.
import importlib.util

_IMPL_PATH = ROOT / 'offline' / 'tools' / 'build_offline_project.py'
_spec = importlib.util.spec_from_file_location('_forever7_offline_build_impl', _IMPL_PATH)
_impl = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_impl)
globals().update({name: value for name, value in vars(_impl).items() if not name.startswith('__')})
main = _impl.main

if __name__ == '__main__':
    main()
