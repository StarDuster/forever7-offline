"""Fixed public history IR consumer. No analysis, game code, xdis or network."""
import hashlib,json,zlib
from pathlib import Path
from .compiler import unique_object

DEFAULT=Path(__file__).resolve().parent/'data'/'history-v1'
CONTRACT_SHA256='e82923fd40899cc5bd98b51e1a056aefe2c1378d3f9782d6d1aeb8c25b1b66a9'
MAX_COMPRESSED=16*1024*1024
MAX_UNCOMPRESSED=128*1024*1024

def digest(data):return hashlib.sha256(data).hexdigest()

def inflate(data,size,sha):
    if not 0<size<=MAX_UNCOMPRESSED or len(data)>MAX_COMPRESSED:raise ValueError('decompression limits')
    obj=zlib.decompressobj(31)
    try:raw=obj.decompress(data,size+1)
    except zlib.error as e:raise ValueError('invalid gzip') from e
    if len(raw)!=size or not obj.eof or obj.unused_data or obj.unconsumed_tail:raise ValueError('truncated, trailing or oversized gzip')
    if digest(raw)!=sha:raise ValueError('uncompressed SHA mismatch')
    return raw

def load(directory=DEFAULT):
    directory=Path(directory);p=directory/'contract.json'
    if p.is_symlink() or not 0<p.stat().st_size<=65536:raise ValueError('contract path/limit')
    contract=p.read_bytes()
    if digest(contract)!=CONTRACT_SHA256:raise ValueError('unsupported contract SHA')
    contract=json.loads(contract,object_pairs_hook=unique_object);record=contract['artifact'];p=directory/'history-ir.json.gz'
    if p.is_symlink() or p.stat().st_size!=record['size'] or record['size']>MAX_COMPRESSED:raise ValueError('artifact size/path')
    packed=p.read_bytes()
    if digest(packed)!=record['sha256']:raise ValueError('compressed SHA mismatch')
    raw=inflate(packed,record['uncompressed_size'],record['uncompressed_sha256'])
    ir=json.loads(raw,object_pairs_hook=unique_object,parse_constant=lambda value:(_ for _ in ()).throw(ValueError('nonfinite JSON')))
    if ir.get('schema')!=1 or ir.get('all_runtime_enabled') is not False or ir.get('state_owner') is not False:raise ValueError('unsupported IR schema/runtime capability')
    ids=[p['wire_t'] for p in ir['ui_pools']]
    if len(ids)!=485 or len(set(ids))!=485 or any(type(t) is not int or t<=0 for t in ids):raise ValueError('invalid fixed UI IDs')
    return ir

def lookup(ir,wire_t):
    if type(wire_t) is not int or wire_t<=0:raise ValueError('explicit positive wire t required')
    for pool in ir['ui_pools']:
        if pool['wire_t']==wire_t:return pool
    for manual in ir['manual_ui_entries']:
        if manual['wire_t']==wire_t:
            return dict(manual,kind='friendship',epoch_utc=None,ui=None,issues=['manual_entry_metadata_requires_const_binding'],required_generic_seams=['independent_friend_RPC_and_wire_binding'],runtime_enabled_by_this_component=False)
    raise ValueError('unknown UI wire t; no normal fallback')
