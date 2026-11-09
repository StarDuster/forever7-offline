"""Consumer for the fixed bundled t1 readonly selector; no analysis dependencies."""
import hashlib
import json
from pathlib import Path

CONTRACT_SHA256 = '6bdf4da90bafa0e03fe63d2196b082f5e8c193856b02a521e16891eca61790f8'
DEFAULT = Path(__file__).resolve().parent / 'data' / 'closure-v2'


def _object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError('duplicate JSON key')
        result[key] = value
    return result


def _read(path, expected, size):
    path = Path(path)
    if path.is_symlink() or path.stat().st_size != size:
        raise ValueError('unsupported artifact size/path')
    data = path.read_bytes()
    if hashlib.sha256(data).hexdigest() != expected:
        raise ValueError('artifact SHA mismatch')
    return json.loads(data, object_pairs_hook=_object,
                      parse_constant=lambda s: (_ for _ in ()).throw(ValueError('nonfinite JSON')))


def load(directory=DEFAULT):
    directory = Path(directory)
    path = directory / 'contract.json'
    if path.is_symlink() or not 0 < path.stat().st_size < 16384:
        raise ValueError('invalid fixed contract')
    data = path.read_bytes()
    if hashlib.sha256(data).hexdigest() != CONTRACT_SHA256:
        raise ValueError('unsupported contract SHA')
    contract = json.loads(data, object_pairs_hook=_object)
    record = contract['artifacts']['t1-reward-ir.json']
    return _read(directory/'t1-reward-ir.json', record['sha256'], record['size'])
