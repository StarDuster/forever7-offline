"""Compile eight fixed640 shop rows. Default consumption needs no original scripts.

This asset alone does not enable a product or prove its transaction/UI behavior.
Production grants must use the original Result/Store and a fresh treasure UUID.
"""
import _bootstrap  # noqa: E402,F401
import argparse
import base64
import hashlib
import json
from pathlib import Path
import sys

from _bootstrap import ROOT
DEFAULT = ROOT / 'offline/current/data/project7_baiye_shop_catalog'
POLICY = 'source640-baiye-shop-current-ownership-v1'
STORES = (8, 157, 158, 478, 480, 540, 595, 617)
PINS = {
    'item_store': '7555873fde108da083ef7c05c5891b847388b188c3a553d09264bcdf4dd573ff',
    'item_data': 'b498b2fc3f850d416fba2c7c9fb3930ddee680f30cd0d6eb5fb6f59c3ca114b6',
    'hero_treasure_generate': '771ceb6415660c9b9650b458f5b988ffb48c4cbf1344d059723a8affbd92b6b6',
}
ASSET_SHA256 = 'ae6523fd78136fa7a1ef893911ca191ff764a1fe7866d9101b62a518216a0501'
CONTRACT_SHA256 = '25ba6ebc952a2ce9862f89194036f2ca5debe9c90f62e4036c9cb01f7a07df7b'


def sha(data):
    return hashlib.sha256(data).hexdigest()


def canonical(value):
    return json.dumps(value, ensure_ascii=True, sort_keys=True,
                      separators=(',', ':'), allow_nan=False).encode('ascii')


def require(condition, message):
    if not condition:
        raise ValueError(message)


def integer(value, minimum=0):
    require(type(value) is int and minimum <= value <= 2147483647,
            'Shop int32 value')
    return value


def compile_tables(stores, items, designs):
    # Runtime fields: kind/item/q/quantity/payment/limits/design/reget/tr.
    lines = ['P7BAIYESHOP\t1\t' + POLICY]
    sources, clean_designs = {}, {}
    for identity in STORES:
        row = stores[identity]
        require(row['num'] == identity and row['open'] == 1 and
                row['item_sort'] == 1 and row.get('consume_items') == {},
                'Shop source domain')
        require(not any(row.get(k) for k in ('itemGroup', 'rewards', 'n_c_1',
                    'daily_num', 'monthly_num', 'zhoumu_limit', 'discount_huodong_id')),
                'Uncompiled shop mechanism')
        item = integer(row['item_num'], 1)
        quantity = integer(row.get('wrap_num', 1), 1)
        require(quantity == 1 and item in items, 'Shop item/quantity')
        payment_fields = [k for k in ('lipinquan', 'diamond', 'hdItemNum')
                          if row.get(k, 0)]
        require(len(payment_fields) == 1, 'Shop payment scope')
        field = payment_fields[0]
        cost = integer(row[field], 1)
        pay_kind = {'lipinquan': 'giftCoin', 'diamond': 'yuanbao',
                    'hdItemNum': 'item'}[field]
        pay_item = integer(row['hdItemid'], 1) if pay_kind == 'item' else 0
        require(pay_item == 0 or pay_item in items, 'Missing payment item')
        total = integer(row.get('buy_limit', 0))
        weekly = integer(row.get('weekly_num', 0))
        minimum_week = max(0, integer(row.get('less_week', 0)) - 1)
        kind, quality, design, reget_item, reget_amount, tr = 'item', 1, 0, 0, 0, '-'
        if row.get('design_treasure'):
            # Only tr survives compilation. The public template UUID is not copied.
            from project7_history_catalog import bson
            kind, quality = 'treasure', integer(row['treasure_class'], 1)
            design = integer(row['design_treasure'], 1)
            original = designs[design]
            value = json.loads(original['dumps_info'])
            require(original['itemid'] == value['i'] == item and
                    original['treasureClass'] == quality and
                    value['tr']['cl'] == quality, 'Design item/quality mismatch')
            tr = base64.b64encode(bson(value['tr'])).decode('ascii')
            reget_item, reget_amount = items[item]['reget_trans']
            integer(reget_item, 1)
            integer(reget_amount, 1)
            require(reget_item in items, 'Missing duplicate-conversion item')
            clean_designs[str(design)] = {'item': item, 'quality': quality,
                                         'tr': value['tr']}
        else:
            require(not row.get('treasure_class'), 'Unexpected quality without design')
        fields = ('S', identity, kind, item, quality, quantity, pay_kind, pay_item,
                  cost, total, weekly, minimum_week, design, reget_item, reget_amount, tr)
        lines.append('\t'.join(map(str, fields)))
        sources[str(identity)] = row
    raw = ('\n'.join(lines) + '\n').encode('ascii')
    contract = {'schema': 'project7-baiye-shop-source-v1', 'policy': POLICY,
                'source_marshal_sha256': PINS, 'source_rows': sources,
                'designs_without_uuid': clean_designs, 'asset_sha256': sha(raw),
                'asset_size': len(raw), 'store_ids': list(STORES),
                'payment_policy': 'source prices; checked original currency/inventory spend',
                'duplicate_policy': 'current bag/equipped ownership then source reget_trans; explicit offline policy, no lifetime receipt',
                'counter_policy': 'buy_limit=original total; weekly_num=original calendar weekly; less_week requires stored w+1',
                'stock1934': 'unchanged; original RR candidates match; no show_rewards grants',
                'data_only_artifact': True,
                'runtime_ready_proof': 'not inferred from data; see independent host and integration reports',
                'native_verified': False}
    return raw, contract


def produce(source, output):
    source, output = Path(source), Path(output)
    require(not output.exists() and not output.is_symlink(), 'Existing output refused')
    sys.path.insert(0, str(ROOT))
    from project7_dream_catalog.produce import literal
    tables = {}
    for name, expected in PINS.items():
        path = source / (name + '.marshal')
        require(path.is_file() and not path.is_symlink() and
                0 < path.stat().st_size < 64 * 1024 * 1024 and
                sha(path.read_bytes()) == expected, 'Unsupported source: ' + name)
        tables[name] = literal(path)
    raw, contract = compile_tables(tables['item_store'], tables['item_data'],
                                   tables['hero_treasure_generate'])
    output.mkdir(parents=True)
    (output / 'catalog-v1.tsv').write_bytes(raw)
    (output / 'contract-v1.json').write_bytes(canonical(contract) + b'\n')
    return contract


def verify(directory=DEFAULT):
    directory = Path(directory)
    blobs = {}
    for name, expected in (('catalog-v1.tsv', ASSET_SHA256),
                           ('contract-v1.json', CONTRACT_SHA256)):
        path = directory / name
        require(path.is_file() and not path.is_symlink() and
                0 < path.stat().st_size <= 65536, 'Shop asset bounds')
        blobs[name] = path.read_bytes()
        require(sha(blobs[name]) == expected, 'Shop asset/contract pin mismatch')
    contract = json.loads(blobs['contract-v1.json'])
    require(contract['source_marshal_sha256'] == PINS and
            contract['asset_sha256'] == ASSET_SHA256 and
            contract['asset_size'] == len(blobs['catalog-v1.tsv']) and
            contract['store_ids'] == list(STORES), 'Shop contract binding')
    lines = blobs['catalog-v1.tsv'].decode('ascii').splitlines()
    require(lines[0] == 'P7BAIYESHOP\t1\t' + POLICY and len(lines) == 9,
            'Shop header/scope')
    require([int(line.split('\t')[1]) for line in lines[1:]] == list(STORES),
            'Shop source IDs')
    return contract


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=('produce', 'verify'))
    parser.add_argument('--source', type=Path)
    parser.add_argument('--output', type=Path, default=DEFAULT)
    args = parser.parse_args()
    if args.command == 'produce':
        require(args.source is not None, 'Original source directory required')
        result = produce(args.source, args.output)
    else:
        result = verify(args.output)
    print(json.dumps({k: result[k] for k in ('asset_sha256', 'asset_size', 'store_ids')},
                     sort_keys=True))


if __name__ == '__main__':
    main()
