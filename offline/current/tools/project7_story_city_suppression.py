"""Source-bound COC mission-hero (MH) increment for route 27-1 scenes 482..488.

The fixed manager suppression.tsv has no MH rows for these scenes, so
LocalCombatCatalog.missionHero returns null and BsonLite.combatDataDocument
keeps the player's own hero document.  This tool owns exactly seven append-only
MH rows for 482:135..488:135 and nothing else.  Normal scenes, the baseline
suppression table, and player collection data are never modified.

Maintainer write mode reads the pinned original mission_hero_attr rows through
the original640 calculator already used by the story-mission catalog; consumer
mode only validates the bundled increment and appends it to the fixed table.
"""
import _bootstrap  # noqa: E402,F401
from pathlib import Path
import argparse, base64, hashlib, json, sys

from _bootstrap import ROOT
ASSET = ROOT / 'offline/current/data/project7_story_city_catalog/suppression-extra.tsv'
CONTRACT = ROOT / 'offline/current/data/project7_story_city_catalog/contract-v1.json'
VIRTUAL = ROOT / 'offline/current/data/project7_story_city_virtual/virtual-data-v1.json'
SOURCE = ROOT / 'analysis/project7/scripts/com/data/cdata'
BASELINE = ROOT / 'analysis/project7/manager/assets/suppression.tsv'

BASELINE_SHA256 = 'f77f4c691408bfa41ed1685e9813a02441e4ca87fa0c77ef67d277e0ff705777'
STORY_EXTENDED_SHA256 = 'b0f8cfa1637d65061f0f062ba78ef79e9fdee2b93889a9b832cb0cddd1160679'
EXTRA_SHA256 = '958688e27cfbec4b897508d04612e6cce49fe82d917af727a3fe3bbfc43272cd'
EXTENDED_SHA256 = '574d8c7e63a4ce648705b3f4d1cfbfced9e30fbf9cfd513cb09138290812bc86'
MH_SHA256 = '2415d5e80245fd3c008f00524f309b11c52099c687db3804d3c4981f94b32283'
VIRTUAL_SHA256 = '83fae3199e308db88513f4a6e6bf6af2288ca749258e3d81b5c81451f8fec6de'
SCENES = (482, 483, 484, 485, 486, 487, 488)
HERO = 135
POLICY = 'source-coc-route-27-1-v1'


def sha(data):
    return hashlib.sha256(data).hexdigest()


def require(value, message):
    if not value:
        raise ValueError(message)


def rows():
    require(ASSET.is_file(), 'COC suppression increment missing')
    raw = ASSET.read_bytes()
    require(sha(raw) == EXTRA_SHA256, 'COC suppression increment hash changed')
    require(raw.endswith(b'\n'), 'COC suppression line boundary')
    result = {}
    for line in raw.decode('ascii').splitlines():
        fields = line.split('\t')
        require(len(fields) == 3 and fields[0] == 'MH', 'COC suppression row schema')
        key = fields[1]
        scene, hero = key.split(':')
        require(int(scene) in SCENES and int(hero) == HERO and key not in result,
                'COC suppression key scope')
        result[key] = fields[2]
    require(list(result) == [f'{scene}:{HERO}' for scene in SCENES],
            'COC suppression scene order')
    from bson import BSON
    for key, value in result.items():
        decoded = BSON.encode(BSON(base64.b64decode(value)).decode())  # canonical BSON round-trip
        require(sha(decoded) == MH_SHA256, 'COC MH value changed ' + key)
        body = BSON(base64.b64decode(value)).decode()
        require(body.get('id') == HERO and body.get('lv') == 50 and body.get('d') and body.get('s'),
                'COC MH schema ' + key)
    return result


def check():
    data = rows()
    contract = json.loads(CONTRACT.read_text())
    require(contract.get('suppression_extra_sha256') == EXTRA_SHA256, 'Catalog contract extra pin')
    require(contract.get('suppression_extended_sha256') == EXTENDED_SHA256, 'Catalog contract extended pin')
    require(contract.get('suppression_baseline_sha256') == BASELINE_SHA256, 'Catalog contract baseline pin')
    hero = contract.get('coc_mission_hero') or {}
    require(hero.get('scenes') == list(SCENES) and hero.get('hero') == HERO and hero.get('rows') == 7,
            'Catalog contract COC hero scope')
    require(sha(BASELINE.read_bytes()) == BASELINE_SHA256, 'Manager suppression baseline changed')
    require(sha(VIRTUAL.read_bytes()) == VIRTUAL_SHA256, 'Story city virtual data changed')
    print(f'PASS source-bound COC suppression {len(data)} MH rows sha256={EXTRA_SHA256}')


def produce(source=SOURCE, virtual=VIRTUAL):
    """Maintainer-only deterministic write from pinned original tables."""
    sys.path.insert(0, str(ROOT))
    from project7_story_mission_catalog import literal, canonical, PINS
    from project7_story_mission_catalog.source_calculator import project_actor
    from bson import BSON
    source = Path(source)
    require(sha(VIRTUAL.read_bytes()) == VIRTUAL_SHA256, 'Story city virtual data changed')
    raw = (source / 'mission_hero_attr.marshal').read_bytes()
    require(sha(raw) == PINS['mission_hero_attr'], 'mission_hero_attr source pin')
    tables = {}
    def load(name):
        if name not in tables:
            path = source / (name + '.marshal')
            require(path.is_file(), 'Missing original table ' + name)
            tables[name] = literal(path)
        return tables[name]
    virtual_data = json.loads(VIRTUAL.read_text())
    generators = load('hero_treasure_generate')
    cache = {}
    lines = []
    expected = None
    for mission in virtual_data['missions']:
        scene = int(mission['scene'])
        require(scene in SCENES, 'Virtual scene order changed')
        fixed = mission['mission_hero_override']
        require(fixed and fixed.get('heroid') == HERO, 'Virtual mission hero changed')
        actor = project_actor(fixed, generators, load, cache)
        value = BSON.encode(canonical(actor))
        require(sha(value) == MH_SHA256, 'Projected COC MH changed')
        if expected is None:
            expected = value
        require(value == expected, 'COC MH differs by scene')
        lines.append('MH\t%d:%d\t%s' % (scene, HERO, base64.b64encode(value).decode()))
    raw = ('\n'.join(lines) + '\n').encode('ascii')
    require(sha(raw) == EXTRA_SHA256, 'Generated COC suppression hash changed')
    ASSET.write_bytes(raw)
    print(f'WROTE {ASSET} sha256={EXTRA_SHA256}')


def extend_asset(baseline, name='suppression.tsv'):
    """Append the fixed COC MH increment to the story-extended suppression table."""
    require(name == 'suppression.tsv', 'Unsupported COC suppression asset')
    baseline = bytes(baseline)
    require(sha(baseline) == STORY_EXTENDED_SHA256, 'Story-extended suppression baseline changed')
    data = rows()
    extra = ASSET.read_bytes()
    existing = {tuple(row.split('\t')[:2]) for row in baseline.decode('ascii').splitlines() if row and not row.startswith('#')}
    for key in data:
        require((key,) not in existing and ('MH', key) not in existing, 'COC suppression row conflict ' + key)
    result = baseline + extra
    require(sha(result) == EXTENDED_SHA256, 'COC suppression extension hash changed')
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--check', action='store_true')
    parser.add_argument('--write', action='store_true')
    parser.add_argument('--source', type=Path, default=SOURCE)
    args = parser.parse_args()
    if args.write:
        produce(args.source)
    else:
        check()


if __name__ == '__main__':
    main()
