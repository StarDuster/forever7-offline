"""Maintainer projection of fixed t1 IR into small integer-weight Android catalog.
Mappings are fixed by the independently audited stock grant contract.
"""
import argparse
import hashlib
import base64
import json
import math
import struct
from pathlib import Path
from . import untyped
from .consumer import load
from .literal_marshal import read

DESIGN_SHA='771ceb6415660c9b9650b458f5b988ffb48c4cbf1344d059723a8affbd92b6b6'

def bson(document):
    chunks=[]
    for key,value in document.items():
        if not isinstance(key,str) or '\0' in key:raise ValueError('invalid BSON key')
        if isinstance(value,dict):tag=3;raw=bson(value)
        elif isinstance(value,list):tag=4;raw=bson({str(i):x for i,x in enumerate(value)})
        elif type(value) is bool:tag=8;raw=bytes([int(value)])
        elif value is None:tag=10;raw=b''
        elif type(value) is int:tag=16;raw=struct.pack('<i',value)
        elif type(value) is float:
            if not math.isfinite(value):raise ValueError('nonfinite BSON double')
            tag=1;raw=struct.pack('<d',value)
        elif type(value) is str:
            tag=2;b=value.encode('utf-8')+b'\0';raw=struct.pack('<i',len(b))+b
        else:raise ValueError('unsupported BSON value')
        chunks.append(bytes([tag])+key.encode('utf-8')+b'\0'+raw)
    body=b''.join(chunks)+b'\0'
    return struct.pack('<i',len(body)+4)+body

ITEM_SHA='b498b2fc3f850d416fba2c7c9fb3930ddee680f30cd0d6eb5fb6f59c3ca114b6'


def project(item_data,design_data):
    ir=load(); lines=['P7DRAW\t1\tnormal-ordinal-reserve-on-group-v1']
    for b in ir['outer']['pools'][0]['branches']:
        n,d=b['weight']
        if d!=1:raise ValueError('noninteger Android outer weight')
        lines.append('B\t%d\t%d\t%d'%(b['row_id'],n,b['random_reward_refs'][0]))
    for b in ir['outer']['ordinal_overrides']:
        lines.append('O\t%d\t%d\t%d'%(b['ordinal'],b['normal_row_id'],b['random_reward_refs'][0]))
    for rid,p in sorted(ir['random_pools'].items(),key=lambda v:int(v[0])):
        for b in p['branches']:
            n,d=b['weight']
            if d!=1:raise ValueError('noninteger Android inner weight')
            lines.append('R\t%s\t%d\t%d'%(rid,b['id'],n))
    for cid,v in sorted(ir['reward_bundles'].items(),key=lambda v:int(v[0])):
        row=untyped(v);kind='';identity=0;count=1;quality=1;file=0;design='-'
        if row.get('hero'):
            if len(row['hero'])!=1:raise ValueError('unsupported hero bundle')
            kind='hero';identity=row['hero'][0]
        elif row.get('items'):
            if len(row['items'])!=1 or len(row['itemsNum'])!=1:raise ValueError('unsupported items bundle')
            identity=row['items'][0];count=row['itemsNum'][0];kind='item'
            meta=item_data[identity]
            if meta.get('memoryFrag'):
                identity,file=meta['memoryFrag'];kind='memory'
                if count!=1:raise ValueError('multi-fragment grant semantics unsupported')
            elif 16639<=identity<=16645:raise ValueError('unresolved virtual item')
        elif row.get('treasure'):
            if len(row['treasure'])!=1:raise ValueError('unsupported treasure bundle')
            identity=row['treasure'][0];count=row['treasureNum'][0];quality=row['treasureLevel'][0];kind='treasure'
        elif row.get('design_treasure'):
            definition=design_data[row['design_treasure']];payload=json.loads(definition['dumps_info'])
            if payload['i']!=definition['itemid']:raise ValueError('design item mismatch')
            kind='treasure';identity=definition['itemid'];count=row['treasureNum'][0];quality=row.get('treasureLevel',(definition['treasureClass'],))[0]
            design=base64.b64encode(bson(payload['tr'])).decode('ascii')
        elif row.get('summoncoin'):
            kind='summonCoin';count=row['summoncoin'];quality=0
        else:raise ValueError('unsupported reward bundle')
        lines.append('L\t%s\t%s\t%d\t%d\t%d\t%d\t%s'%(cid,kind,identity,count,quality,file,design))
    return ('\n'.join(lines)+'\n').encode('ascii')

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--item-marshal',type=Path,required=True);p.add_argument('--design-marshal',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--contract-output',type=Path);a=p.parse_args()
    if hashlib.sha256(a.item_marshal.read_bytes()).hexdigest()!=ITEM_SHA:raise ValueError('unsupported item source SHA')
    if hashlib.sha256(a.design_marshal.read_bytes()).hexdigest()!=DESIGN_SHA:raise ValueError('unsupported design source SHA')
    if a.output.exists() or (a.contract_output is not None and a.contract_output.exists()):raise FileExistsError('output exists')
    items,designs=read(a.item_marshal),read(a.design_marshal)
    data=project(items,designs)
    with a.output.open('xb') as f:f.write(data)
    if a.contract_output is not None:
        from . import canonical,typed
        from .consumer import DEFAULT,CONTRACT_SHA256
        contract={'schema':1,'policy':'normal-ordinal-reserve-on-group-v1','asset_path':'project7_draw_policy/catalog-v2.tsv','asset_sha256':hashlib.sha256(data).hexdigest(),'asset_size':len(data),'t1_ir_contract_sha256':CONTRACT_SHA256,'item_data_marshal_sha256':ITEM_SHA,'design_marshal_sha256':DESIGN_SHA,'item_data_projection_sha256':hashlib.sha256(canonical(typed(items))).hexdigest(),'design_projection_sha256':hashlib.sha256(canonical(typed(designs))).hexdigest(),'default_reference':'chouka_default.pool -> chouka_normal row -> random_reward ID','stock_currency':'summonCoin kind, id0, count from common.summoncoin, quality0','stock_design':'q7Design is dumps_info.tr document only','scope':'pure fixed catalog; no player state, default lifecycle is explicitly offline policy'}
        with a.contract_output.open('xb') as f:f.write(canonical(contract)+b'\n')
    print(hashlib.sha256(data).hexdigest(),len(data))
