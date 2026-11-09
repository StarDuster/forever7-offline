"""Project fixed readonly historical IR into a compact runtime catalog.
No player state, game imports, network or per-pool handler code.
"""
import _bootstrap  # noqa: E402,F401
import argparse,base64,hashlib,json,math,struct
from pathlib import Path
import sys
if __package__ in (None, ""):
    sys.path.insert(0,str(_bootstrap.ROOT))
from project7_draw_history_ir.consumer import load,CONTRACT_SHA256
from project7_draw_history_ir.codec import untyped,canonical,typed

POLICY='history-free-v1'
GIFT_SOURCE_SHA256='b3b7e161c8a242d3618ad9ad7a987b5c020ec845e0c4a74f365a9665eafcb81c'
GIFT_ROW={'per_day':1,'gift_num':1,'chouka_time':6}  # exact fixed public chouka_gift[6]

def bson(document):
    chunks=[]
    for key,value in document.items():
        if not isinstance(key,str) or '\0' in key:raise ValueError('BSON key')
        if isinstance(value,dict):tag=3;data=bson(value)
        elif isinstance(value,list):tag=4;data=bson({str(i):v for i,v in enumerate(value)})
        elif value is None:tag=10;data=b''
        elif type(value) is bool:tag=8;data=bytes([int(value)])
        elif type(value) is int:tag=16;data=struct.pack('<i',value)
        elif type(value) is float:
            if not math.isfinite(value):raise ValueError('nonfinite design')
            tag=1;data=struct.pack('<d',value)
        elif type(value) is str:
            tag=2;raw=value.encode()+b'\0';data=struct.pack('<i',len(raw))+raw
        else:raise ValueError('unsupported BSON value')
        chunks.append(bytes([tag])+key.encode()+b'\0'+data)
    body=b''.join(chunks)+b'\0';return struct.pack('<i',len(body)+4)+body

def leaf(node, *, version=2):
    raw=untyped(node['raw']);fields=node['component_fields'];design='-';kind='unsupported';identity=0;count=1;quality=1;piece=0
    if len(fields)!=1:return (kind,identity,count,quality,piece,design)
    if fields==['hero'] and len(raw['hero'])==1:kind='hero';identity=raw['hero'][0]
    elif fields==['items'] and len(raw['items'])==len(raw.get('itemsNum',()))==1:
        identity=raw['items'][0];count=raw['itemsNum'][0];meta=untyped(node['references'].get('item:'+str(identity)))
        if meta is None:return (kind,identity,count,quality,piece,design)
        if meta.get('memoryFrag'):
            identity,piece=meta['memoryFrag'];kind='memory' if count==1 else 'unsupported'
        elif meta.get('type')==8 and meta.get('subtype')==10 and version>=2:
            skin=meta.get('skin');kind='skin' if type(skin) is int and skin>0 and count==1 else 'unsupported'
            if kind=='skin':
                design=base64.b64encode(bson({'i':identity,'skin':skin,'n':count})).decode();identity=skin
        elif meta.get('type')==8 and meta.get('subtype')==13 and version>=2:
            pendant=meta.get('pendant');trans=meta.get('pendant_trans',())
            valid=type(pendant) is tuple and len(pendant)==2 and all(type(v) is int and v>0 for v in pendant) and all(type(t) is tuple and len(t)==2 and all(type(v) is int and v>0 for v in t) for t in trans)
            kind='pendant' if valid else 'unsupported'
            if valid:design=base64.b64encode(bson({'i':identity,'n':count,'pendant':list(pendant),'trans':[list(t) for t in trans]})).decode()
        elif version>=3 and meta.get('type')==8 and type(meta.get('subtype')) is int and meta.get('subtype') in range(61,68):
            kind='selector' if count==1 and meta.get('virtual_sub_type')==meta['subtype'] and type(meta.get('card_pool')) is int else 'unsupported'
        elif meta.get('type')==8 and meta.get('subtype') in [10,13,61,62,63,64,65,66,67]:kind='unsupported' 
        else:kind='item'
    elif fields==['treasure'] and len(raw['treasure'])==1:
        kind='treasure';identity=raw['treasure'][0];count=raw['treasureNum'][0];quality=raw['treasureLevel'][0]
    elif fields==['design_treasure'] and 'design_tr' in node['references']:
        definition=untyped(node['references']['design:'+str(raw['design_treasure'])]);kind='treasure';identity=definition['itemid'];count=raw['treasureNum'][0];quality=raw.get('treasureLevel',(definition['treasureClass'],))[0];design=base64.b64encode(bson(untyped(node['references']['design_tr']))).decode()
    elif fields in [['summoncoin'],['money']]:kind='summonCoin' if fields==['summoncoin'] else 'money';count=raw[fields[0]];quality=0
    if count<=0 or count>1000000:kind='unsupported'
    return kind,identity,count,quality,piece,design

def project(*,gift_policy='history-source-gift-daily-cap-v1',version=2):
    if version not in (1,2,3):raise ValueError('unsupported catalog version')
    selector_contract=None;selector_audit=None
    if version>=3:
        from project7_selector_catalog import verify,audit_history
        selector_contract=verify();selector_audit=audit_history()
    ir=load();lines=['P7HISTORY\t1\t'+POLICY];report=[];used=set();all_leaf={int(k):leaf(v,version=version) for k,v in ir['common_bundles'].items()}
    for row in ir['ui_pools']:
        wire=row['wire_t']
        if row['rpc_family']!='six_cards' or wire in (1,354,484):continue
        raw=untyped(row['raw']);reasons=[]
        selector_pool=version>=3 and wire in (265,369,427,454,455) and row['kind']=='choice'
        candidate=(row['kind']=='plain' and row['capability']=='static_hierarchy_closed') or (selector_pool and any(p['pool']==wire for p in selector_audit['pools']))
        if not candidate:reasons.append('candidate_or_policy_unresolved')
        if raw.get('times')!=6:reasons.append('six_slot_shape_unverified')
        if not 0<(row['epoch_utc'] or 0)<=2147483647:reasons.append('epoch_outside_stock_int')
        rids=set(row['referenced_random_ids'])
        for rid in rids:
            pool=ir['random_pools'].get(str(rid))
            if pool is None:reasons.append('missing_random');continue
            for edge in pool['branches']:
                if all_leaf.get(edge['target'],('unsupported',))[0]=='unsupported':reasons.append('unsupported_positive_leaf')
        reward=raw.get('rewardCoin');gift=0
        if reward is not None:
            if type(reward) is int and reward>0 and gift_policy=='history-source-gift-daily-cap-v1':gift=1
            else:reasons.append('explicit_gift_not_supported')
        ready=candidate and not reasons
        ticket=raw.get('drawCoin',0)
        if type(ticket) is not int:ticket=0
        lines.append('P\t%d\t%d\t%d\t%d\t%d'%(wire,row['epoch_utc'] or 0,ticket,int(ready),gift))
        if reward is not None:lines.append('G\t%d\t%d\t%d\t%d\t%d'%(wire,reward,GIFT_ROW['gift_num'],GIFT_ROW['chouka_time'],GIFT_ROW['per_day']))
        report.append({'wire_t':wire,'ready':ready,'candidate_closed':candidate,'cost_policy':POLICY,'gift_policy':gift_policy,'reasons':sorted(set(reasons)),'source_raw':row['raw'],'selector_policy':selector_contract['policy'] if selector_pool else None})
        for b in row['positive_base']:
            n,d=b['weight']
            if d!=1 or not isinstance(b['target'],int):continue
            lines.append('B\t%d\t%d\t%d\t%d'%(wire,b['source'],n,b['target']))
        for d in row['default_rows']:
            if 'normal_row_id' not in d or d.get('unresolved'):continue
            refs=untyped(d['random_reward_refs'])
            if len(refs)==1:lines.append('O\t%d\t%d\t%d\t%d'%(wire,d['ordinal'],d['normal_row_id'],refs[0]))
        used.update(rids)
    leaves=set()
    for rid in sorted(used):
        pool=ir['random_pools'].get(str(rid))
        if pool is None:continue
        for b in pool['branches']:
            n,d=b['weight']
            if d!=1:raise ValueError('noninteger weights not represented')
            lines.append('R\t%d\t%d\t%d'%(rid,b['target'],n));leaves.add(b['target'])
    if version>=2:leaves.update(cid for cid,value in all_leaf.items() if value[0] in ('skin','pendant'))
    for cid in sorted(leaves):lines.append('L\t%d\t%s\t%d\t%d\t%d\t%d\t%s'%((cid,)+all_leaf[cid]))
    data=('\n'.join(lines)+'\n').encode('ascii')
    return data,{'schema':1,'selector_contract':selector_contract,'selector_positive_closure':selector_audit,'catalog_version':version,'gift_source':{'marshal_sha256':GIFT_SOURCE_SHA256,'literal':typed({6:GIFT_ROW})},'source_history_contract_sha256':CONTRACT_SHA256,'policy':POLICY,'ordinal_policy':'history-ordinal-reserve-on-group-v1','gift_policy':gift_policy,'ready_count':sum(p['ready'] for p in report),'pools':report,'asset_sha256':hashlib.sha256(data).hexdigest(),'asset_size':len(data),'no_runtime_or_store_owner':True}

def furniture_reward(node):
    """Whole original bundle for HomeEngine; never split components into choices."""
    raw=untyped(node['raw'])
    if node['component_fields']!=['items'] or len(raw['items'])!=len(raw.get('itemsNum',())):raise ValueError('unsupported furniture bundle')
    grants=[]
    for item,count in zip(raw['items'],raw['itemsNum']):
        meta=untyped(node['references'].get('item:'+str(item)))
        if meta is None or type(count) is not int or not 0<count<=1000000:raise ValueError('furniture item reference/count')
        grant={'i':item,'n':count,'skin':0,'furniture':meta.get('furniture',0),'pendant':[],'trans':[]}
        if meta.get('type')==8 and meta.get('subtype')==10:
            if type(meta.get('skin')) is not int:raise ValueError('skin mapping')
            grant['skin']=meta['skin']
        elif meta.get('type')==8 and meta.get('subtype')==13:
            pair=meta.get('pendant');trans=meta.get('pendant_trans',())
            if not isinstance(pair,tuple) or len(pair)!=2 or not all(type(v) is int and v>0 for v in pair):raise ValueError('pendant mapping')
            if any(len(t)!=2 or not all(type(v) is int and v>0 for v in t) for t in trans):raise ValueError('pendant trans')
            grant['pendant']=list(pair);grant['trans']=[list(t) for t in trans]
        elif meta.get('type')==8:raise ValueError('unsupported virtual furniture leaf')
        grants.append(grant)
    if not grants:raise ValueError('empty furniture bundle')
    return grants

def project_furniture(*,defaults_proven=True):
    ir=load();rows=[];report=[];delivery=untyped(ir['tables']['furniture_delivery'])
    def random_row(rid):
        source=ir['random_pools'].get(str(rid))
        if source is None or not source['branches']:raise ValueError('missing furniture random')
        options=[]
        for edge in source['branches']:
            n,d=edge['weight']
            if d!=1 or not 0<n<=2147483647:raise ValueError('furniture random weight')
            options.append({'w':n,'g':furniture_reward(ir['common_bundles'][str(edge['target'])]),'source_common':edge['target']})
        return {'options':options,'source_random':rid}
    for row in ir['ui_pools']:
        if row['rpc_family']!='furniture' or row['wire_t']==162:continue
        t=row['wire_t'];raw=untyped(row['raw']);reasons=[];base=[];defaults={}
        try:
            for edge in row['positive_base']:
                n,d=edge['weight']
                if d!=1 or not 0<n<=2147483647 or type(edge['target']) is not int:raise ValueError('furniture outer weight')
                entry=random_row(edge['target']);entry.update(w=n,source_normal=edge['source']);base.append(entry)
            if not base:raise ValueError('empty furniture outer')
            for entry in row['default_rows']:
                rid=untyped(entry['raw']).get('pool')
                if rid is not None:
                    if not defaults_proven:raise ValueError('furniture default direct RR resolver awaits independent evidence')
                    defaults[str(entry['ordinal'])]=random_row(rid)
        except ValueError as e:reasons.append(str(e))
        delivery_row=delivery.get(t,{});cost=delivery_row.get('fur_consume_item',raw.get('fur_consume_item'))
        if not isinstance(cost,tuple) or len(cost)!=2:reasons.append('missing furniture cost')
        data={'level':raw.get('show_level_lower_bound',1),'cost':[cost[0],0] if isinstance(cost,tuple) else [1,0],'ticket':0,'discount':[list(v) for v in raw.get('lianchou_discount',())],'permanent':False,'q7HistoryFurniturePolicy':'history-furniture-free-v1','source_cost':list(cost or ()),'source_epoch':row['epoch_utc'] or 0,'base':base,'defaults':defaults,'enabled':not reasons,'wire_t':t}
        rows.append('F\t%d\t%s'%(t,base64.b64encode(bson(data)).decode()))
        report.append({'wire_t':t,'ready':not reasons,'reasons':reasons,'source_raw':row['raw'],'source_mechanisms':row['mechanism_tags'],'delivery_source':typed(delivery_row)})
    data=('P7FURNITURE\t1\n'+'\n'.join(rows)+'\n').encode('ascii')
    return data,{'schema':1,'source_history_contract_sha256':CONTRACT_SHA256,'policy':'history-furniture-free-v1','legacy162_preserved':True,'default_policy':'source-direct-random-v1; fixed 640 tables and original162 G1/RR9174 factory oracle, not hidden-server reconstruction','wish_sort_policy':'source display ordering only; original integer weight distribution preserved','pools':report,'ready_count':sum(p['ready'] for p in report),'asset_size':len(data),'asset_sha256':hashlib.sha256(data).hexdigest()}

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);p.add_argument('--contract-output',type=Path,required=True);p.add_argument('--gift-policy',choices=['pending','history-source-gift-daily-cap-v1'],default='history-source-gift-daily-cap-v1');p.add_argument('--version',type=int,choices=[1,2,3],default=2);p.add_argument('--family',choices=['six_cards','furniture'],default='six_cards');a=p.parse_args()
    if a.output.exists() or a.contract_output.exists():raise FileExistsError('output exists')
    data,contract=project_furniture() if a.family=='furniture' else project(gift_policy=a.gift_policy,version=a.version)
    with a.output.open('xb') as f:f.write(data)
    with a.contract_output.open('xb') as f:f.write(canonical(contract)+b'\n')
    print(json.dumps({k:contract[k] for k in ['ready_count','asset_sha256','asset_size','policy','gift_policy'] if k in contract}))
