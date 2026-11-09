"""Pure lossless compiler. Missing semantics are capabilities, never defaults."""
import calendar
import collections
import datetime
import json
from fractions import Fraction
from .codec import canonical,typed

META={'id','tradeType'}
KNOWN={'hero','items','itemsNum','treasure','treasureLevel','treasureNum','design_treasure','summoncoin','money'}

def numeric(v):
    if type(v) not in (int,float,Fraction):raise ValueError('invalid weight type')
    try:w=Fraction(v)
    except (ValueError,OverflowError):raise ValueError('nonfinite weight')
    if w<0:raise ValueError('negative weight')
    return w

def unique_object(pairs):
    result={}
    for key,value in pairs:
        if key in result:raise ValueError('duplicate JSON key')
        result[key]=value
    return result

def ratio(v):return [v.numerator,v.denominator]

def distribution(entries):
    rows=[]
    for source,target,value in entries:
        w=numeric(value)
        if w:rows.append((source,target,w))
    total=sum((w for _,_,w in rows),Fraction())
    return [{'source':s,'target':t,'weight':ratio(w),'mass':ratio(w/total)} for s,t,w in rows]

def epoch(value):
    if not value:return None
    if not isinstance(value,(tuple,list)) or len(value)!=9:raise ValueError('invalid calendar tuple')
    datetime.datetime(*value[:6])
    return calendar.timegm(value)

def compile_history(tables):
    info,normal,defaults,random,common=[tables[k] for k in ['chouka_info','chouka_normal','chouka_default','reward_random','reward_common']]
    for key,row in normal.items():
        if type(key) is not int or row.get('id')!=key:raise ValueError('normal ID mismatch')
        numeric(row.get('weight',0))
    pool_nodes={};bundle_nodes={};pool_issues={}
    def bundle(cid):
        if str(cid) in bundle_nodes:return bundle_nodes[str(cid)]
        if cid not in common:return None
        raw=common[cid];issues=[];tags=[];refs={};fields=set(raw)-META
        if raw.get('id')!=cid:issues.append('common_id_mismatch')
        unknown=fields-KNOWN
        if unknown:issues.append('unsupported_fields:'+','.join(sorted(unknown)))
        for iid in raw.get('items',()):
            definition=tables['item_data'].get(iid)
            if definition is None:issues.append('missing_item:'+str(iid));continue
            refs['item:'+str(iid)]=typed(definition)
            frag=definition.get('memoryFrag')
            if frag:
                tags.append('memory_fragment')
                if not isinstance(frag,(tuple,list)) or len(frag)!=2:issues.append('memoryFrag_shape')
                else:
                    hid,piece=frag;hero=tables['hero'].get(hid);file=tables['chouka_hero_file'].get(hid)
                    if hero is None or file is None:issues.append('missing_fragment_hero_metadata')
                    elif not 1<=piece<=file.get('file_num',0):issues.append('fragment_ordinal_out_of_range')
                    refs['fragment:'+str(iid)]={'hero_id':hid,'piece':piece,'hero':typed(hero),'file':typed(file)}
            if definition.get('type')==8:
                subtype=definition.get('subtype');tags.append('virtual_type8_subtype'+str(subtype))
                if subtype in range(61,68):issues.append('selection_policy_required');tags.append('virtual_choice_selector')
        for hid in raw.get('hero',()):
            hero=tables['hero'].get(hid)
            if hero is None:issues.append('missing_hero:'+str(hid))
            else:refs['hero:'+str(hid)]=typed(hero)
        design=raw.get('design_treasure')
        if design:
            definition=tables['hero_treasure_generate'].get(design)
            if definition is None:issues.append('missing_design:'+str(design))
            else:
                refs['design:'+str(design)]=typed(definition)
                if 'dumps_info' not in definition:issues.append('design_without_dumps_info')
                else:
                    try:
                        doc=json.loads(definition['dumps_info'],object_pairs_hook=unique_object,parse_constant=lambda value:(_ for _ in ()).throw(ValueError('nonfinite design JSON')))
                        if not isinstance(doc.get('tr'),dict) or doc.get('i')!=definition['itemid']:raise ValueError()
                        refs['design_tr']=typed(doc['tr'])
                    except (ValueError,TypeError,KeyError):issues.append('invalid_design_tr')
        if 'items' in raw and len(raw['items'])!=len(raw.get('itemsNum',())):issues.append('items_quantity_shape')
        if 'treasure' in raw:
            for field in ['treasureNum','treasureLevel']:
                if len(raw.get(field,()))!=len(raw['treasure']):issues.append('treasure_quantity_or_quality_shape')
        if raw.get('award_pool'):issues.append('award_pool_semantics_unresolved')
        component_fields=sorted(fields-{'itemsNum','treasureNum','treasureLevel'})
        node={'common_id':cid,'raw':typed(raw),'component_fields':component_fields,'bundle_atomic':True,'mechanism_tags':sorted(set(tags)),'references':refs,'issues':sorted(set(issues))}
        bundle_nodes[str(cid)]=node;return node
    def rr(rid):
        key=str(rid)
        if key in pool_nodes:return pool_nodes[key]
        if rid not in random:return None
        raw=random[rid];issues=[]
        if raw.get('id')!=rid:issues.append('random_id_mismatch')
        entries=[]
        try:
            for index,(cid,w) in enumerate(raw['weights']):entries.append((index,cid,w))
        except (TypeError,ValueError,KeyError):issues.append('weights_shape')
        branches=distribution(entries)
        if not branches:issues.append('empty_positive_distribution')
        for branch in branches:
            node=bundle(branch['target'])
            if node is None:issues.append('missing_common:'+str(branch['target']))
            elif node['issues']:issues.extend('leaf:'+str(branch['target'])+':'+i for i in node['issues'])
        node={'random_id':rid,'raw':typed(raw),'branches':branches,'issues':sorted(set(issues))};pool_nodes[key]=node;return node
    by_type=collections.defaultdict(list)
    for key,row in normal.items():by_type[row.get('type')].append((key,row))
    by_default=collections.defaultdict(list)
    for key,row in defaults.items():
        if key!=(row.get('draw_type'),row.get('chouka_time')):raise ValueError('default key mismatch')
        by_default[row['draw_type']].append(row)
    rows=[]
    for wire,raw in sorted(info.items()):
        if type(wire) is not int or wire<=0 or raw.get('drawType')!=wire:raise ValueError('wire key mismatch')
        family='furniture' if raw.get('poolType')==2 else 'friendship' if wire in (99,131) else 'six_cards'
        kind='furniture' if family=='furniture' else 'friendship' if family=='friendship' else 'normal' if wire==1 else 'newbie' if wire==354 else 'choice' if raw.get('self_choose') else 'plain'
        issues=[];mechanisms=[];base=[];overrides=[];rids=set()
        for key,row in sorted(by_type[wire]):
            w=numeric(row.get('weight',0))
            if not w:continue
            refs=row.get('random_reward')
            if not isinstance(refs,(tuple,list)) or not refs:issues.append('random_reference_shape:'+str(key));continue
            if len(refs)!=1:issues.append('multi_random_reference_semantics:'+str(key))
            base.append((key,list(refs),w))
            rids.update(refs)
            for field in ('wish_sort','replace_reward','is_up'):
                if row.get(field):mechanisms.append(field)
        branches=distribution((key,refs[0] if len(refs)==1 else refs,w) for key,refs,w in base)
        for default in sorted(by_default[wire],key=lambda r:r['chouka_time']):
            item={'ordinal':default['chouka_time'],'raw':typed(default)}
            if 'pool' in default:
                nid=default['pool'];item['normal_row_id']=nid;target=normal.get(nid)
                if target is None:issues.append('missing_default_normal:'+str(nid));item['unresolved']=True
                else:
                    refs=target.get('random_reward');item['normal_source']=typed(target);item['random_reward_refs']=typed(refs)
                    if not isinstance(refs,(tuple,list)) or len(refs)!=1:issues.append('default_random_reference_semantics:'+str(nid))
                    if isinstance(refs,(tuple,list)):rids.update(refs)
            overrides.append(item)
        for rid in sorted(rids):
            node=rr(rid)
            if node is None:issues.append('missing_random:'+str(rid))
            elif node['issues']:issues.extend('random:'+str(rid)+':'+i for i in node['issues'])
        if not branches:issues.append('no_positive_base_distribution')
        if kind=='choice':issues.append('per_pool_S_A_candidate_source_unresolved');mechanisms.append('self_choose')
        for field in ('inc_up_cnt_type','up_r','up_x','up_n','up_m','is_up_open','get_hero_extra_reward','consume_without_normal'):
            if raw.get(field):mechanisms.append(field)
        if family=='friendship':issues.append('independent_friend_protocol_binding_unresolved')
        if family=='furniture':issues.append('furniture_rotation_open_range_and_protocol_unresolved')
        if kind=='newbie':issues.append('policy_rejects_new_groups_preserves_existing')
        signature_mass=collections.defaultdict(Fraction)
        if not any(i.startswith(('multi_random','missing_random','random_reference')) for i in issues):
            for b in branches:
                node=pool_nodes.get(str(b['target']))
                if node:
                    for inner in node['branches']:
                        leaf=bundle_nodes.get(str(inner['target']))
                        if leaf:signature_mass['+'.join(leaf['component_fields']) or 'empty']+=Fraction(*b['mass'])*Fraction(*inner['mass'])
        total=sum(signature_mass.values(),Fraction())
        if branches and total!=1:issues.append('base_leaf_mass_unresolved')
        seams=['explicit_positive_wire_and_epoch','original_BSON_transaction_and_reply']
        if family=='friendship':seams+=['friend_RPC_and_wire_binding']
        if family=='furniture':seams+=['furniture_RPC_and_rotation_open_range']
        if kind=='choice':seams+=['epoch_bound_S_A_candidates','typed_choice_receipt']
        if mechanisms:seams+=['stateful_policy_review:'+m for m in sorted(set(mechanisms))]
        for rid in rids:
            node=pool_nodes.get(str(rid))
            if node:
                for branch in node['branches']:
                    leaf=bundle_nodes.get(str(branch['target']))
                    if leaf and 'design_treasure' in leaf['component_fields']:seams.append('original_tr_BSON_grant')
                    if leaf and 'memory_fragment' in leaf['mechanism_tags']:seams.append('original_hfp_conversion')
                    if leaf and len(leaf['component_fields'])>1:seams.append('atomic_generic_bundle_grant')
        for field in ['drawCoin','rewardCoin']:
            if field in raw and type(raw[field]) is int and raw[field] not in tables['item_data']:issues.append('missing_cost_item:'+field+':'+str(raw[field]))
        capability='independent_rpc_family' if family!='six_cards' else 'new_groups_disabled' if kind=='newbie' else 'unresolved' if issues else 'dynamic_policy_required' if mechanisms else 'static_hierarchy_closed'
        rows.append({'required_generic_seams':sorted(set(seams)),'wire_t':wire,'table_key':wire,'epoch_utc':epoch(raw.get('end_time')),'begin_utc':epoch(raw.get('begin_time')),'kind':kind,'rpc_family':family,'raw':typed(raw),'ui':{'level_min':raw.get('show_level_lower_bound'),'level_max':raw.get('show_level_upper_bound'),'sort':raw.get('sort',99),'recommend':raw.get('isRecommend'),'room_enter_type':raw.get('room_enter_type'),'title':raw.get('room_title'),'ui_six_card_tab_excluded':family=='furniture'},'cost_sources':{field:typed(raw[field]) for field in ['drawCoin','rewardCoin','fur_consume_item','lianchou_discount','use_diamond'] if field in raw},'choice_candidates':{'resolved':False,'reason':'no per-pool candidate mapping proved in supplied tables'} if kind=='choice' else None,'positive_base':branches,'default_rows':overrides,'referenced_random_ids':sorted(rids),'base_bundle_signature_mass':{k:ratio(v) for k,v in sorted(signature_mass.items())},'base_total_resolved_mass':ratio(total),'mechanism_tags':sorted(set(mechanisms)),'issues':sorted(set(issues)),'capability':capability,'visibility_rule':'separate_furniture_UI_rotation' if family=='furniture' else 'existing_pending_only' if kind=='newbie' else 'level_then_always' if kind=='normal' else 'level_then_original_time_window','runtime_enabled_by_this_component':False})
    independent={}
    if 'chouka_friend' in tables:
        entries=[];refs=set();friend_issues=[]
        for key,row in sorted(tables['chouka_friend'].items()):
            w=numeric(row.get('weight',0))
            if not w:continue
            values=row.get('rewards')
            if not isinstance(values,(tuple,list)) or len(values)!=1:friend_issues.append('friend_reward_ref_shape:'+str(key));continue
            entries.append((key,values[0],w));refs.update(values)
        for row in tables.get('chouka_friend_default',{}).values():
            if type(row.get('pool')) is int:refs.add(row['pool'])
        for rid in refs:
            if rr(rid) is None:friend_issues.append('missing_friend_random:'+str(rid))
        independent['friend_unbound_data']={'wire_binding_proven':False,'positive_rows':distribution(entries),'default_source':typed(tables.get('chouka_friend_default',{})),'random_refs':sorted(refs),'issues':friend_issues,'scope':'Literal dependency audit; not protocol/cost/default lifecycle implementation'}
    if 'furniture_delivery' in tables:
        independent['furniture_delivery']={'rows':len(tables['furniture_delivery']),'ui_wires_with_delivery':[r['wire_t'] for r in rows if r['rpc_family']=='furniture' and r['wire_t'] in tables['furniture_delivery']],'ui_wires_without_delivery':[r['wire_t'] for r in rows if r['rpc_family']=='furniture' and r['wire_t'] not in tables['furniture_delivery']],'rotation_open_range_resolved':False}
    summary={'ui_rows':len(rows),'kind_counts':dict(collections.Counter(r['kind'] for r in rows)),'rpc_family_counts':dict(collections.Counter(r['rpc_family'] for r in rows)),'capability_counts':dict(collections.Counter(r['capability'] for r in rows)),'referenced_random_count':len(pool_nodes),'referenced_common_count':len(bundle_nodes),'bundle_signature_counts':dict(collections.Counter('+'.join(r['component_fields']) for r in bundle_nodes.values())),'multi_component_common_ids':[r['common_id'] for r in bundle_nodes.values() if len(r['component_fields'])>1]}
    return {'schema':1,'scope':'all official640 UI metadata and referenced readonly hierarchy; no runtime integration','encoding_scope':'Lossless for decoded host literals; Python2 str/unicode identity is not independently represented' ,'ui_pools':rows,'manual_ui_entries':[{'wire_t':99,'rpc_family':'friendship','source':'card_tab appends FRIEND separately; absent from chouka_info','capability':'dependency_unresolved'}],'random_pools':pool_nodes,'common_bundles':bundle_nodes,'tables':{k:typed(v) for k,v in tables.items()},'summary':summary,'independent_family_data_audits':independent,'schema_field_counts':{name:dict(collections.Counter(k for row in table.values() for k in row)) for name,table in tables.items()},'state_owner':False,'all_runtime_enabled':False}
