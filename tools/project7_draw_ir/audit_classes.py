"""Maintainer-only fixed t1 hero/fragment rank audit; never infers from names."""
import argparse
import hashlib
import json
from fractions import Fraction
from pathlib import Path
from . import canonical
from .literal_marshal import read

PINS = {'hero':'5fd8f55649e12030a76ec34d50fcf10b414fc07cb8055437177be8ecf29f771e',
        'item_data':'b498b2fc3f850d416fba2c7c9fb3930ddee680f30cd0d6eb5fb6f59c3ca114b6'}


def audit(source_dir):
    tables={}
    for name, sha in PINS.items():
        path=Path(source_dir)/(name+'.marshal')
        if hashlib.sha256(path.read_bytes()).hexdigest()!=sha:
            raise ValueError('unsupported class source SHA')
        tables[name]=read(path)
    # Consume the fixed public source projection, not analysis paths.
    from .consumer import load
    ir=load()
    from . import untyped
    pools={k:untyped(v['source_row']) for k,v in ir['random_pools'].items()}
    common={int(k):untyped(v) for k,v in ir['reward_bundles'].items()}
    result={}
    for rid in [1095,371]:
        leaves=[]
        for cid,w in pools[str(rid)]['weights']:
            row=common[cid]
            if rid==1095:
                if set(row)-{'id','hero','tradeType'} or len(row.get('hero',()))!=1:
                    raise ValueError('unexpected whole-hero bundle')
                hid=row['hero'][0];detail={'hero_id':hid}
            else:
                if set(row)-{'id','items','itemsNum','tradeType'} or len(row.get('items',()))!=1 or row['itemsNum']!=(1,):
                    raise ValueError('unexpected fragment bundle')
                item=row['items'][0];meta=tables['item_data'][item]
                frag=meta.get('memoryFrag')
                if not isinstance(frag,tuple) or len(frag)!=2:
                    raise ValueError('unsupported memoryFrag shape')
                hid=frag[0];detail={'hero_id':hid,'item_id':item,'fragment_ordinal':frag[1]}
            rank=tables['hero'][hid]['hero_composite_init_rank']
            detail.update(common_reward_id=cid,weight=w,initial_rank=rank)
            leaves.append(detail)
        result[str(rid)]={'leaves':leaves,'all_initial_rank_4':all(r['initial_rank']==4 for r in leaves)}
    masses={}
    for branch in ir['outer']['pools'][0]['branches']:
        rid=str(branch['random_reward_refs'][0])
        for leaf in ir['random_pools'][rid]['branches']:
            row=common[leaf['id']]
            if row.get('hero') and len(row['hero'])==1:
                label='whole_hero_rank_'+str(tables['hero'][row['hero'][0]]['hero_composite_init_rank'])
            elif row.get('items') and len(row['items'])==1 and tables['item_data'][row['items'][0]].get('memoryFrag'):
                hid=tables['item_data'][row['items'][0]]['memoryFrag'][0]
                label='fragment_rank_'+str(tables['hero'][hid]['hero_composite_init_rank'])
            else:
                label='+'.join(k for k in ('hero','items','treasure','design_treasure','summoncoin','money') if row.get(k)) or 'unknown'
            masses[label]=masses.get(label,Fraction())+Fraction(*branch['mass'])*Fraction(*leaf['mass'])
    if sum(masses.values(),Fraction())!=1:raise ValueError('class mass mismatch')
    return {'schema':1,'sources':PINS,'rank_evidence':result,
            'base_class_mass':{k:[v.numerator,v.denominator] for k,v in sorted(masses.items())},
            'scope':'fixed base t1 buckets only; not effective odds with sequence/pity or gameplay grant validation'}

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--source-dir',required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    data=canonical(audit(a.source_dir))+b'\n'
    with a.output.open('xb') as f:f.write(data)
    print(hashlib.sha256(data).hexdigest(),len(data))
