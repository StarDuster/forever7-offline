"""Shared import roots for tests after the source-layout split."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
for _path in (
        ROOT,
        ROOT / 'offline' / 'tools',
        ROOT / 'project7_bridge' / 'tools',
        ROOT / 'offline' / 'current' / 'tools',
        ROOT / 'offline' / 'runtime',
        ROOT / 'offline' / 'current' / 'runtime',
        ROOT / 'offline' / 'current' / 'data',
        ROOT / 'project7_bridge' / 'runtime',
        ROOT / 'project7_bridge' / 'android',
        ROOT / 'runtime'):
    if str(_path) not in sys.path:
        sys.path.insert(0, str(_path))
