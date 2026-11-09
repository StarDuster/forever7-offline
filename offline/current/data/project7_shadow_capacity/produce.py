"""Maintainer-only producer for the fixed offline shadow-equipment capacity policy.

Reads the pinned complete-collection target and the pinned public item catalog.
No game/APK/device execution and no profile access. Runtime consumers receive
only the embedded ASCII policy text; they never read the analysis catalog.
"""
from pathlib import Path
import argparse
import hashlib
import json

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
TARGET = ROOT / 'offline/current/data/project7_catalog/target-manifest.json'
ITEMS = ROOT / 'analysis/catalogs/item_data.json'
TARGET_SHA256 = '7e3849b6ed316b7cdc2ef9f103b90e0bc8e20f9b5da70ab3b585fbd72c0da62d'
ITEMS_SHA256 = '017c2bc189682cdf02181a7e947fa740bf8b30b2942885ea10d6300b97328d51'
FORMAT = 'project7-shadow-capacity-policy-v1'
MARGIN_PER_SUBBAG = 100


def sha(data):
    return hashlib.sha256(data).hexdigest()


def encoded(data):
    return (json.dumps(data, sort_keys=True, separators=(',', ':')) + '\n').encode('ascii')


def project():
    target_bytes = TARGET.read_bytes()
    if sha(target_bytes) != TARGET_SHA256:
        raise ValueError('Complete-collection target changed')
    item_bytes = ITEMS.read_bytes()
    if sha(item_bytes) != ITEMS_SHA256:
        raise ValueError('Public item catalog changed')
    target = json.loads(target_bytes)
    catalog = json.loads(item_bytes)
    items = dict((int(key), value) for key, value in catalog['data']['items'])
    if target.get('format') != 'project7-full-collection-target-v1':
        raise ValueError('Unexpected target format')
    if len(target.get('treasures', ())) != 380:
        raise ValueError('Unexpected target template count')
    ids = []
    counts = {}
    for row in target['treasures']:
        template = row['id']
        qualities = row.get('qualities', ())
        if len(qualities) != 5 or set(q.get('quality') for q in qualities) != set((1, 2, 3, 4, 5)):
            raise ValueError('Incomplete target quality universe')
        if any('era' in q or 'su' in q for q in qualities):
            raise ValueError('Target qualities must not encode extraRandom/suit cultivation state')
        item = items.get(template)
        if item is None or item.get('type') != 5:
            raise ValueError('Target treasure lacks original item metadata')
        subbag = item.get('subbag')
        if subbag not in (1, 2):
            raise ValueError('Unexpected shadow-equipment subbag')
        ids.append(template)
        counts[str(subbag)] = counts.get(str(subbag), 0) + 5
    if ids != sorted(ids) or len(set(ids)) != 380:
        raise ValueError('Target template order/identity changed')
    total = sum(counts.values())
    if total != 1900 or counts.get('1', 0) + counts.get('2', 0) != total:
        raise ValueError('Target 1900 pair coverage changed')
    # Non-target pre-existing records are added by the runtime projection. The
    # margin is an explicit offline draw allowance, not official capacity.
    return {
        'draw_margin_per_subbag': MARGIN_PER_SUBBAG,
        'format': FORMAT,
        'margin_total': MARGIN_PER_SUBBAG * 2,
        'scope': ('current avatar.invData shadow-equipment TREASURE total/subbag '
                  'capacities only; hero treasureInv, ordinary wrap and trade unchanged'),
        'source': {'item_catalog_sha256': ITEMS_SHA256,
                   'target_manifest_sha256': TARGET_SHA256},
        'target_subbag_counts': counts,
        'target_template_ids': ids,
        'target_total': total,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    path = HERE / 'policy.json'
    if args.write:
        data = encoded(project())
        path.write_bytes(data)
        print(sha(data))
        return
    data = path.read_bytes()
    if data != encoded(project()):
        raise ValueError('Bundled shadow-capacity policy differs from pinned sources')
    print('PASS fixed shadow-capacity policy')


if __name__ == '__main__':
    main()
