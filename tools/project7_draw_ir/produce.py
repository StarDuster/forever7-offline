"""Pinned maintainer projection. Consumers use bundled JSON, never marshal/code."""
import argparse
import hashlib
import json
import os
import tempfile
from pathlib import Path
from . import canonical, typed
from .closure import compile_t1
from .literal_marshal import read

PINS = {
'chouka_normal': '936b936c59212bba1eaffd910505354b8913f85ba38401d3463a65195a7e4c32',
'chouka_default': 'd21e19de8ab9911e3face6f8e0e1c869224fb9da76764de23545820270ef6a59',
'reward_random': '8680b7d5a5e1befa9011647317c88fdaf63aff80889c36ed44f249678cd46262',
'reward_common': 'e6433f6a6d521fa57fb98a3d49c3f5194f9c5268ecaf24e114b70e9e89114c29'}


def produce(source_dir, output):
    output = Path(output)
    if output.exists():
        raise FileExistsError(output)
    tables, provenance = {}, {}
    for name, expected in PINS.items():
        path = Path(source_dir) / (name + '.marshal')
        if hashlib.sha256(path.read_bytes()).hexdigest() != expected:
            raise ValueError('unsupported source SHA: ' + name)
        tables[name] = read(path)
        projection = canonical(typed(tables[name]))
        provenance[name] = {'marshal_sha256': expected, 'projection_sha256': hashlib.sha256(projection).hexdigest(), 'rows': len(tables[name])}
    ir = compile_t1(tables['chouka_normal'], tables['chouka_default'], tables['reward_random'], tables['reward_common'])
    files = {'t1-reward-ir.json': canonical(ir) + b'\n',
             'public-source-tables.json': canonical({k:typed(v) for k,v in tables.items()}) + b'\n'}
    contract = {'schema': 1, 'sources': provenance, 'artifacts': {k:{'sha256':hashlib.sha256(v).hexdigest(),'size':len(v)} for k,v in files.items()},
                'counts': {'random_pools':len(ir['random_pools']), 'common_bundles':len(ir['reward_bundles']), 'ordinal_overrides':len(ir['outer']['ordinal_overrides'])},
                'limits': ['No stock grants, server scheduling, pity, ordinal lifecycle or gameplay acceptance proven', 'No player state or network; all common bundle fields preserved']}
    files['contract.json'] = canonical(contract) + b'\n'
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=output.parent) as temp:
        stage = Path(temp) / 'data'; stage.mkdir()
        for name, data in files.items():
            with (stage/name).open('xb') as f:
                f.write(data);f.flush();os.fsync(f.fileno())
        if output.exists():
            raise FileExistsError(output)
        os.rename(stage, output)
    return contract

if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--source-dir', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    print(json.dumps(produce(a.source_dir, a.output), indent=2))
