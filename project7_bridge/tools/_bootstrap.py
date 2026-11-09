"""Make bridge and shared offline tooling importable from any cwd."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
for _path in (
        ROOT,
        ROOT / 'project7_bridge' / 'tools',
        ROOT / 'offline' / 'tools',
        ROOT / 'project7_bridge' / 'runtime',
        ROOT / 'offline' / 'runtime',
        ROOT / 'project7_bridge' / 'android',
        ROOT / 'offline' / 'current' / 'tools',
        ROOT / 'offline' / 'current' / 'runtime',
        ROOT / 'offline' / 'current' / 'data'):
    if str(_path) not in sys.path:
        sys.path.insert(0, str(_path))

from forever7_paths import *  # noqa: F401,F403,E402
