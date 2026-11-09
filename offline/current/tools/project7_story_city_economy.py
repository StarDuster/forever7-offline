"""Append-only COC mission economy rows for route 27-1 scenes 482..488."""
import _bootstrap  # noqa: E402,F401
from pathlib import Path
import hashlib

from _bootstrap import ROOT
EXTRA = ROOT / 'offline/current/data/project7_story_city_catalog/economy-extra.tsv'
EXTRA_SHA256 = '013348079e415e0c6d0746897fa2dadb3423d20c7a34cb638372d22126e5026e'
BASE_EXTENDED_SHA256 = '037e36ab1a517ba7a0972764eed25807c64139a2e9358ed72923d065f01ab0d9'
FINAL_SHA256 = '4c504ae5fc5a431fb6eeffd6fb48df614bbfa00f0c2a8a949e23d1cd4363ed9a'
SCENES = (482, 483, 484, 485, 486, 487, 488)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def extend_asset(base):
    extra = EXTRA.read_bytes()
    if sha(extra) != EXTRA_SHA256:
        raise ValueError('COC economy increment hash changed')
    rows = extra.decode('ascii').splitlines()
    if len(rows) != 45 or [row.split('\t')[1] for row in rows[:7]] != [str(x) for x in SCENES]:
        raise ValueError('COC/menu32 economy increment scope')
    if any(row.split('\t')[0] not in ('M','G') for row in rows[7:]):
        raise ValueError('menu32 economy row kind')
    if not base.endswith(b'\n'):
        base += b'\n'
    if any(row.encode('ascii') in base for row in rows):
        raise ValueError('COC economy increment already present')
    result = base + extra
    if sha(base) != BASE_EXTENDED_SHA256:
        raise ValueError('COC economy base is not the story-mission extension')
    if sha(result) != FINAL_SHA256:
        raise ValueError('COC economy final hash changed')
    return result


def check():
    from project7_story_mission_catalog import extend_asset as extend_mission
    base = (ROOT / 'analysis/project7/manager/assets/economy.tsv').read_bytes()
    result = extend_asset(extend_mission(base, 'economy.tsv'))
    print('PASS source-bound COC economy 7 rows sha256=' + sha(result))


if __name__ == '__main__':
    check()
