"""Compare typed catalog values, distinguishing data changes from byte changes."""
import argparse
from collections import Counter
import json
from pathlib import Path

from export_game_catalogs import encode, decode

ROOT = Path(__file__).resolve().parents[1]


def same(left, right):
    if type(left) is not type(right):
        return False
    if isinstance(left, dict):
        return left.keys() == right.keys() and all(same(left[key], right[key]) for key in left)
    if isinstance(left, (list, tuple)):
        return len(left) == len(right) and all(same(a, b) for a, b in zip(left, right))
    return left == right


def compare(android, ios):
    added = set(ios) - set(android)
    removed = set(android) - set(ios)
    changes, fields = [], Counter()
    for key in sorted(set(android) & set(ios), key=repr):
        if same(android[key], ios[key]):
            continue
        left, right = android[key], ios[key]
        changed = {}
        for field in sorted(set(left) | set(right), key=repr):
            if field in left and field in right and same(left[field], right[field]):
                continue
            change = {'android_present': field in left, 'ios_present': field in right}
            if field in left:
                change['android'] = encode(left[field])
            if field in right:
                change['ios'] = encode(right[field])
            changed[str(field)] = change
            fields[str(field)] += 1
        changes.append({'key': encode(key), 'fields': changed})
    return {'android_records': len(android), 'ios_records': len(ios),
            'added_to_ios': [encode(key) for key in sorted(added, key=repr)],
            'absent_from_ios': [encode(key) for key in sorted(removed, key=repr)],
            'changed_rows': len(changes), 'changed_field_counts': dict(fields),
            'changes': changes,
            'same_values': not added and not removed and not changes}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--android', type=Path, default=ROOT / 'analysis/catalogs')
    parser.add_argument('--ios', type=Path, default=ROOT / 'analysis/catalogs-ios')
    parser.add_argument('--output', type=Path, default=ROOT / 'reports/catalog-platform-differences.json')
    args = parser.parse_args()
    result = {'script_index': 640, 'native_compatibility_verified': False, 'tables': {}}
    for name in ('hero', 'skin', 'item_data', 'hero_treasure'):
        a = json.loads((args.android / (name + '.json')).read_text())
        b = json.loads((args.ios / (name + '.json')).read_text())
        data = compare(decode(a['data']), decode(b['data']))
        data['module_sha256'] = {'android': a['module']['sha256'], 'ios': b['module']['sha256']}
        result['tables'][name] = data
        print(json.dumps({name: {key: value for key, value in data.items() if key not in ('changes', 'module_sha256')}}, ensure_ascii=False))
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')


if __name__ == '__main__':
    main()
