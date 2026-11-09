"""Operational capability audit of readonly data, never an enablement switch."""
from collections import Counter

def capabilities(ir):
    result=[]
    for row in ir['ui_pools']:
        tags=set()
        for rid in row['referenced_random_ids']:
            pool=ir['random_pools'].get(str(rid),{})
            for edge in pool.get('branches',[]):
                tags.update(ir['common_bundles'].get(str(edge['target']),{}).get('mechanism_tags',[]))
        extra=sorted(t for t in tags if t in ('virtual_type8_subtype10','virtual_type8_subtype13'))
        category='not_integrated'
        if row['rpc_family']!='six_cards':category='independent_rpc_not_implemented'
        elif row['kind']=='newbie':category='new_groups_disabled'
        elif row['issues']:category='unresolved_data_or_policy'
        elif row['mechanism_tags']:category='dynamic_policy_not_implemented'
        elif extra:category='virtual_item_grant_dispatch_unverified'
        else:category='static_selector_data_ready_grant_and_runtime_unimplemented'
        result.append({'wire_t':row['wire_t'],'epoch_utc':row['epoch_utc'],'base_graph_class':row['capability'],'execution_class':category,'runtime_enabled':False,'unverified_virtual_dispatch':extra,'required_generic_seams':row['required_generic_seams'],'issues':row['issues']})
    return {'schema':1,'scope':'execution readiness is distinct from positive graph closure','counts':dict(Counter(r['execution_class'] for r in result)),'pools':result,'all_runtime_enabled':False,'further_evidence':['Per-pool S/A candidates source for six self_choose pools','Explicit semantics for seven missing chouka_default normal references','Virtual subtype10/13 original grant/UI dispatch','Friend wire99/131 exact independent producer/consume/default lifecycle','Furniture rotation open_range and independent transaction/RPC','Official server sequence, pity, exclusion and reset semantics remain unproven']}
