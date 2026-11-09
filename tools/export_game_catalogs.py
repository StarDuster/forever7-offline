"""Export verified local cdata catalogs without running game code.

Uses the restricted literal reader. Tagged JSON preserves tuple/set and
non-string dictionary keys; catalog presence is not ownership or resource QA.
"""
import argparse
from collections import Counter
from datetime import datetime
import hashlib
import json
from pathlib import Path
from zoneinfo import ZoneInfo

from read_data_table import read

ROOT = Path(__file__).resolve().parents[1]
TAG = '$f7type'


def encode(value):
    if isinstance(value, tuple):
        return {TAG: 'tuple', 'items': [encode(item) for item in value]}
    if isinstance(value, (set, frozenset)):
        return {TAG: type(value).__name__, 'items': [encode(item) for item in sorted(value, key=repr)]}
    if isinstance(value, list):
        return [encode(item) for item in value]
    if isinstance(value, dict):
        if all(isinstance(key, str) for key in value) and TAG not in value:
            return {key: encode(item) for key, item in value.items()}
        return {TAG: 'dict', 'items': [[encode(key), encode(item)] for key, item in value.items()]}
    if value is None or type(value) in (bool, int, float, str):
        return value
    raise ValueError('Unsupported catalog literal: %s' % type(value).__name__)


def decode(value):
    if isinstance(value, list):
        return [decode(item) for item in value]
    if not isinstance(value, dict):
        return value
    if TAG not in value:
        return {key: decode(item) for key, item in value.items()}
    kind = value[TAG]
    if kind == 'dict':
        return {decode(key): decode(item) for key, item in value['items']}
    constructors = {'tuple': tuple, 'set': set, 'frozenset': frozenset}
    if kind not in constructors:
        raise ValueError('Unknown catalog type tag')
    return constructors[kind](decode(item) for item in value['items'])


def export(sources, output, module_index, platform='android', marshal_root=None):
    tables = {name: read(path) for name, path in sources.items()}
    wanted = {'com/data/cdata/' + name + '.py': name for name in tables}
    metadata = {}
    with module_index.open() as handle:
        for line in handle:
            item = json.loads(line)
            name = wanted.get(item['filename'].replace('\\', '/'))
            if name:
                metadata[name] = {key: item[key] for key in ('sign', 'filename', 'sha256', 'size')}
                if marshal_root is not None:
                    raw = (marshal_root / item['output']).read_bytes()
                    if hashlib.sha256(raw).hexdigest() != item['sha256']:
                        raise ValueError('Extracted module does not match parsed index: %s' % name)
    if set(metadata) != set(tables):
        raise ValueError('Could not verify every module against the parsed archive index')
    output.mkdir(parents=True, exist_ok=True)
    counts = {}
    for name, data in tables.items():
        source = sources[name]
        document = {'format': 'f7-tagged-catalog-v1', 'platform': platform, 'script_index': 640,
                    'module': metadata[name], 'decompiled_source': str(source.relative_to(ROOT)),
                    'decompiled_sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
                    'record_count': len(data), 'data': encode(data)}
        raw = json.dumps(document, ensure_ascii=False, indent=2, allow_nan=False)
        if decode(json.loads(raw)['data']) != data:
            raise ValueError('Catalog type-preserving round trip failed: %s' % name)
        (output / (name + '.json')).write_text(raw + '\n')
        counts[name] = len(data)
    heroes, skins, items, treasures = [tables[name] for name in ('hero', 'skin', 'item_data', 'hero_treasure')]
    treasure_ids = {key[0] for key in treasures}
    missing_skin_heroes = sorted({row['hero'] for row in skins.values()} - set(heroes))
    missing_treasure_items = sorted(treasure_ids - set(items))
    missing_base_classes = sorted(item for item in treasure_ids if (item, 1) not in treasures)
    summary = {'recorded_at': datetime.now(ZoneInfo('Asia/Hong_Kong')).isoformat(), 'platform': platform, 'script_index': 640,
               'counts': counts, 'skin_hero_references_missing': missing_skin_heroes,
               'skin_release_flags': dict(Counter(str(row.get('release')) for row in skins.values())),
               'treasure_templates': len(treasure_ids),
               'treasure_item_types': dict(Counter(str(items[item].get('type')) for item in treasure_ids if item in items)),
               'treasure_classes': dict(Counter(str(key[1]) for key in treasures)),
               'treasure_item_references_missing': missing_treasure_items,
               'treasure_base_class_missing': missing_base_classes,
               'ownership_granted': False, 'resources_verified': False, 'native_menu_verified': False,
               'warning': '目录数量不是可解锁/已解锁数量；需实例UUID、合法字段、装备关系、资源和原界面验证。'}
    (output / 'summary.json').write_text(json.dumps(summary, ensure_ascii=False, indent=2) + '\n')
    if missing_skin_heroes or missing_treasure_items or missing_base_classes:
        raise ValueError('Catalog reference checks failed; see exported summary')
    return summary


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source-dir', type=Path, default=ROOT / 'analysis/decompiled')
    parser.add_argument('--platform', choices=('android', 'ios'), default='android')
    parser.add_argument('--module-index', type=Path)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    sources = {name: args.source_dir / (('ios-' if args.platform == 'ios' and name in ('item_data', 'hero_treasure') else '')
                                      + name + '.py') for name in ('hero', 'skin', 'item_data', 'hero_treasure')}
    index = args.module_index or ROOT / ('reports/android640-modules.jsonl' if args.platform == 'android' else 'reports/ios-modules.jsonl')
    output = args.output or ROOT / ('analysis/catalogs' if args.platform == 'android' else 'analysis/catalogs-ios')
    marshal_root = ROOT / ('analysis/android640-scripts' if args.platform == 'android' else 'analysis/ios-scripts')
    print(json.dumps(export(sources, output, index, args.platform, marshal_root), ensure_ascii=False))


if __name__ == '__main__':
    main()
