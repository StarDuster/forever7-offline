# -*- coding: ascii -*-
"""Original finite self-choice/treasure-target RPCs and virtual reward leaves.

No time rewrite, draw, inventory merge, or automatic user choice. Whole-state
candidates are committed by the gateway before original lock-releasing replies.
"""
import copy
import hashlib
import json
import time

SPECIAL_GACHA_OPERATIONS = frozenset(('setChooseHeroes','setChooseTreasure','setWishGroupAnimPlayed'))
SELF_CHOOSE_POOLS = frozenset((265,369,427,454,455,484))
SPECIAL_GACHA_POLICY = 'original-special-choice-v1'
FREE_TREASURE_WISH_POLICY = 'offline-free-treasure-wish-selection-v1'


try:
    _special_integer_types = (int,long)
except NameError:
    _special_integer_types = (int,)


def _special_int(value):
    return isinstance(value,_special_integer_types) and not isinstance(value,bool)


def original_self_choose_hash(configuration):
    end = configuration.get('end_time')
    if not isinstance(end,(list,tuple)) or len(end) != 9:
        raise ValueError('Missing original self-choice period end')
    return int(time.mktime(tuple(end)) - time.timezone)


def _special_container(state):
    return ((state.get('gacha_pools') or {}).get('special') or {})


def special_pool_context(state, wire, wish_id=None):
    row = _special_container(state).get('pools',{}).get(str(wire),{})
    current = row.get('ctr',[0,0,0])
    treasure = row.get('ctr_by_wish',{}).get(str(wish_id),current if current[0]==wish_id else [wish_id,0,0]) if wish_id is not None else current
    return {'choose_heroes':copy.deepcopy(row.get('ch',[0,0,0])),
            'choose_treasure':copy.deepcopy(treasure),
            'wish_id':row.get('wish_id')}


def validate_special_gacha_state(state):
    validate_charge_progress(state.get('gacha_pools') or {})
    special = (state.get('gacha_pools') or {}).get('special')
    if special is None:
        return
    if special.get('version') != 1 or special.get('policy') != SPECIAL_GACHA_POLICY or not isinstance(special.get('pools'),dict) or not isinstance(special.get('receipts'),list):
        raise ValueError('Unknown special gacha state')
    if len(special['receipts']) > 128 or len(special.get('retired_operations',[])) > 8192:
        raise ValueError('Special gacha replay history exceeds bound')
    for wire,row in special['pools'].items():
        if not str(wire).isdigit() or int(wire) == 354:
            raise ValueError('Disabled or invalid special pool')
        for key in ('ch','ctr'):
            values = row.get(key,[0,0,0])
            if not isinstance(values,list) or len(values)!=3 or any(not _special_int(v) or v<0 for v in values):
                raise ValueError('Invalid original special choice tuple')
        for key in ('jzc','jzr','rc'):
            values = row.get(key,{})
            if not isinstance(values,dict) or any(not str(k).isdigit() or not isinstance(v,_special_integer_types) or v<0 for k,v in values.items()):
                raise ValueError('Invalid finite original jiaozhi state')
        for period,values in row.get('ctr_by_wish',{}).items():
            if not str(period).isdigit() or not isinstance(values,list) or len(values)!=3 or any(not _special_int(v) or v<0 for v in values) or values[0]!=int(period):
                raise ValueError('Invalid original treasure choice period history')
        for group,data in row.get('wi',{}).items():
            if not str(group).isdigit() or type(data.get('c')) is not int or data['c']<0 or any(not isinstance(data.get(key),list) for key in ('f','a')):
                raise ValueError('Invalid original wish group state')
            if not set(data['a']).issubset(set(data['f'])):
                raise ValueError('Wish animations cannot imply unfinished rewards')


def _special_open(configuration, wire, context):
    if context.get('archive_wire_t') == wire:
        return True
    now = context.get('now')
    if not isinstance(now,(int,float)):
        return False
    current = tuple(time.gmtime(now)[:6])
    begin,end = configuration.get('begin_time'),configuration.get('end_time')
    return bool(begin and end and tuple(begin[:6]) <= current < tuple(end[:6]))


def _new_special(state):
    pools = state.get('gacha_pools')
    if not isinstance(pools,dict) or not isinstance(pools.get('pools'),dict):
        raise ValueError('Special RPC requires original pool-state migration first')
    return pools.setdefault('special',{'version':1,'policy':SPECIAL_GACHA_POLICY,'pools':{},'receipts':[],'retired_operations':[]})


def _choice_reply(operation, wire, current, ret):
    if operation == 'setChooseHeroes':
        return ('replySetChooseHeroes',{'r':ret,'t':wire,'h':copy.deepcopy(current.get('ch',[0,0,0]))})
    if operation == 'setChooseTreasure':
        return ('replySetChooseTreasure',{'r':ret,'t':wire,'i':copy.deepcopy(current.get('ctr',[0,0,0]))})
    return None


def prepare_special_gacha_operation(state,operation,arguments,tables,operation_id=None,context=None):
    """Return whole candidate, original notices, changed, diagnostic.

    context.archive_wire_t scopes date bypass to an actual archive session.
    context.wish_id must identify the exact original treasure-wish period.
    No latest-period inference or free-cost substitution is performed here.
    """
    if operation not in SPECIAL_GACHA_OPERATIONS:
        raise ValueError('No original special gacha RPC contract')
    context = context or {}
    args = {k:v for k,v in arguments.items() if k!='_cbid_'}
    wire = args.get('t')
    safe_wire = wire if _special_int(wire) else 0
    existing = copy.deepcopy(_special_container(state).get('pools',{}).get(str(wire),{}))
    if operation=='setChooseTreasure':
        existing['ctr'] = [0,0,0] if context.get('no_wish') else special_pool_context(state,wire,context.get('wish_id'))['choose_treasure']
    diagnostic = {'policy':SPECIAL_GACHA_POLICY,'success':False,'replay':False}
    def fail(code,reason):
        diagnostic.update(ret=code,reason=reason)
        reply = _choice_reply(operation,safe_wire,existing,code)
        return copy.deepcopy(state),[reply] if reply else [],False,diagnostic
    if not _special_int(wire) or wire <= 0 or wire == 354:
        return fail(1809 if operation=='setChooseHeroes' else 1882,'disabled-or-invalid-pool')
    validate_special_gacha_state(state)
    fingerprint = hashlib.sha256(json.dumps([operation,args],sort_keys=True,separators=(',',':')).encode('ascii')).hexdigest()
    if operation_id:
        special = _special_container(state)
        if operation_id in special.get('retired_operations',[]):
            return fail(1,'replay-receipt-retired-no-second-charge')
        for receipt in special.get('receipts',[]):
            if receipt['id'] == operation_id:
                if receipt['fingerprint'] != fingerprint:
                    return fail(1,'operation-id-reused-for-another-choice')
                diagnostic.update(success=True,replay=True,ret=0)
                return copy.deepcopy(state),copy.deepcopy(receipt['notices']),False,diagnostic
    if operation=='setChooseTreasure' and context.get('no_wish'):
        return fail(1882,'existing-group-has-no-wish-binding')
    configuration = tables.get('chouka_info',{}).get(wire)
    if not configuration:
        return fail(1809 if operation=='setChooseHeroes' else 1882,'missing-original-pool')
    if operation != 'setWishGroupAnimPlayed' and not _special_open(configuration,wire,context):
        return fail(1810 if operation=='setChooseHeroes' else 1882,'pool-period-not-active-or-archive-not-authorized')
    active = ((state.get('gacha_pools') or {}).get('pools',{}).get(str(wire)) or {}).get('group')
    if active and operation != 'setWishGroupAnimPlayed':
        return fail(1814 if operation=='setChooseHeroes' else 1884,'active-group-choice-context-is-immutable')
    candidate = copy.deepcopy(state)
    if operation == 'setChooseHeroes':
        if set(args)!=set(('t','h')) or wire not in SELF_CHOOSE_POOLS or not configuration.get('self_choose'):
            return fail(1809,'not-an-original-self-choice-pool')
        heroes = args.get('h')
        if not isinstance(heroes,(list,tuple)) or any(not _special_int(h) or h<0 for h in heroes):
            return fail(1811,'invalid-user-choice-list')
        heroes = [h for h in heroes if h]
        if len(heroes)!=2 or len(set(heroes))!=2:
            return fail(1811,'two-distinct-user-choices-required')
        selected_s,selected_a = [],[]
        rotation = context.get('rotation')
        if rotation is not None:
            uaid = context.get('rotation_uaid')
            original_rotation = tables.get('activity_config',{}).get(uaid)
            if context.get('self_choose_wire') != wire or context.get('rotation_policy') != 'offline-archive-candidate-period-v1' or not _special_int(uaid) or not original_rotation or tables.get('activity_template',{}).get(original_rotation.get('tmp_id'),{}).get('tmp_type') != 88 or dict(original_rotation.items()) != rotation:
                return fail(1812,'unverified-original-self-choice-candidate-period')
            rotation = original_rotation
        for hero in heroes:
            row = tables.get('hero',{}).get(hero,{})
            rank = row.get('hero_composite_init_rank')
            if rotation is None:
                allowed = bool(tables.get('hero_self_choose_info',{}).get(hero,{}).get('avaliable'))
            else:
                allowed = hero in rotation.get('self_choose_S',[]) if rank==4 else hero in rotation.get('self_choose_A',[])
            if not allowed:
                return fail(1812,'hero-not-in-original-allowed-candidates')
            if rank==4:selected_s.append(hero)
            elif rank==3:selected_a.append(hero)
            else:return fail(1813,'original-choice-requires-one-S-and-one-A')
        if len(selected_s)!=1 or len(selected_a)!=1:
            return fail(1813,'original-choice-requires-one-S-and-one-A')
        stamp = original_self_choose_hash(configuration)
        previous = existing.get('ch',[0,0,0])
        if previous[0]==stamp and (previous[1] or previous[2]):
            return fail(1814,'already-chosen-in-original-period')
        special = _new_special(candidate)
        row = special['pools'].setdefault(str(wire),{})
        row['ch'] = [stamp,selected_s[0],selected_a[0]]
        notices = [_choice_reply(operation,wire,row,0)]
    elif operation == 'setChooseTreasure':
        if set(args)!=set(('t','i')) or wire != 5:
            return fail(1882,'original-treasure-choice-is-YINGSHE-only')
        item = args.get('i')
        definition = tables.get('chouka_wish_treasure_choose',{}).get(item,{})
        if not _special_int(item) or not definition.get('can_choose'):
            return fail(1883,'item-not-in-original-choosable-treasures')
        wish = context.get('wish_id',existing.get('wish_id'))
        wish_row = tables.get('chouka_treasure_wish',{}).get(wish,{})
        if not _special_int(wish) or wish_row.get('drawType')!=wire:
            return fail(1882,'exact-original-wish-period-required')
        previous = existing.get('ctr_by_wish',{}).get(str(wish),existing.get('ctr',[0,0,0]))
        same = previous[0] == wish
        current = previous[1] if same else 0
        count = previous[2] if same else 0
        if item == (current or wish_row.get('treasure_id')):
            return fail(1884,'already-current-or-default-original-target')
        costs = tables.get('item_store_wish_change',{})
        if not costs or any(not _special_int(k) or k<=0 for k in costs):
            return fail(1885,'missing-original-target-change-cost-table')
        cost = costs.get(min(count+1,max(costs)),{}).get('cost')
        free = (context.get('choice_cost_policy') == FREE_TREASURE_WISH_POLICY and context.get('archive_wire_t') == 5)
        effective = 0 if free else cost
        economy = candidate.get('profile',{}).get('economy',{})
        if not _special_int(cost) or cost<0 or not free and (type(economy.get('yuanbao')) is not int or economy['yuanbao']<cost):
            return fail(1885,'insufficient-original-yuanbao')
        if effective:
            economy['yuanbao'] -= effective
        special = _new_special(candidate)
        row = special['pools'].setdefault(str(wire),{})
        history = row.setdefault('ctr_by_wish',{})
        old = row.get('ctr',[0,0,0])
        if old[0]:
            history.setdefault(str(old[0]),copy.deepcopy(old))
        row.update(ctr=[wish,item,count+1],wish_id=wish)
        history[str(wish)] = copy.deepcopy(row['ctr'])
        notices = ([('updateYuanBao',{'v':economy['yuanbao']})] if effective else []) + [_choice_reply(operation,wire,row,0)]
        diagnostic.update(original_cost=cost,effective_cost=effective,wish_id=wish,
            cost_policy='offline-free-treasure-wish-selection-v1' if free else 'original-item-store-wish-change')
    else:
        if set(args)!=set(('t','gi')) or not isinstance(args.get('gi'),(list,tuple)):
            return fail(1,'invalid-original-wish-animation-ack')
        special = _new_special(candidate)
        row = special['pools'].setdefault(str(wire),{})
        for entry in args['gi']:
            if not isinstance(entry,(list,tuple)) or len(entry)!=2:
                return fail(1,'invalid-original-wish-group-pair')
            group,played = entry
            data = row.get('wi',{}).get(str(group))
            if not _special_int(group) or data is None or not isinstance(played,(tuple,list)) or not set(played).issubset(set(data['f'])):
                return fail(1,'only-actually-completed-wishes-can-acknowledge-animation')
            data['a'] = sorted(set(data['a']) | set(played))
        notices = []
    if operation_id:
        if len(special.get('retired_operations',[])) >= 8192:
            return fail(1,'special-operation-history-full')
        special['receipts'].append({'id':operation_id,'fingerprint':fingerprint,'notices':[[name,copy.deepcopy(payload)] for name,payload in notices],
            'cost':{key:diagnostic[key]for key in ('original_cost','effective_cost','wish_id','cost_policy')if key in diagnostic}})
        if len(special['receipts'])>128:
            retired=special['receipts'].pop(0)
            special.setdefault('retired_operations',[]).append(retired['id'])
    validate_special_gacha_state(candidate)
    diagnostic.update(success=True,ret=0)
    return candidate,notices,candidate!=state,diagnostic


def resolve_self_choose_item(tables,wire,item_id,quantity,context):
    """Only actual original virtual61..67 leaves convert; weights are unchanged."""
    definition = tables.get('item_data',{}).get(item_id,{})
    subtype = definition.get('virtual_sub_type',definition.get('subtype'))
    if subtype not in range(61,68):
        return None
    if wire==354 or definition.get('card_pool')!=wire or wire not in SELF_CHOOSE_POOLS:
        raise ValueError('Original virtual self-choice item/card_pool mismatch')
    choice = context.get('choose_heroes',[0,0,0])
    if not isinstance(choice,(list,tuple)) or len(choice)!=3 or choice[0]!=original_self_choose_hash(tables.get('chouka_info',{}).get(wire,{})) or not choice[1] or not choice[2]:
        raise ValueError('Original virtual reward requires actual current-period user choice')
    if type(quantity) is not int or not 1<=quantity<=100:
        raise ValueError('Invalid original virtual self-choice quantity')
    slot = 1 if subtype in (61,63,64,65) else 2
    hero = choice[slot]
    piece = 0 if subtype in (61,62) else subtype-62 if slot==1 else subtype-65
    if piece:
        fragment = tables.get('hero_self_choose_info',{}).get(hero,{}).get('fragment_%s'%piece)
        if not fragment or tuple(tables.get('item_data',{}).get(fragment,{}).get('memoryFrag',())) != (hero,piece):
            raise ValueError('Missing original selected-hero fragment mapping')
    rank = tables.get('hero',{}).get(hero,{}).get('hero_composite_init_rank')
    if rank != (4 if slot==1 else 3):
        raise ValueError('Original selected hero rank disagrees with virtual reward slot')
    return [(hero,piece)]*quantity


def project_special_gacha_snapshot(state,template,context=None):
    result = copy.deepcopy(template)
    special = _special_container(state)
    if not special:
        return result
    activities = dict(result.get('ad',[]))
    for wire,row in special.get('pools',{}).items():
        if int(wire)==354:
            continue
        if int(wire)==1:
            if 'wi' in row:
                result['wi'] = [(int(k),copy.deepcopy(v))for k,v in sorted(row['wi'].items(),key=lambda item:int(item[0]))]
            continue
        data = activities.setdefault(int(wire),{})
        for key in ('ch','ctr'):
            if key in row:data[key]=copy.deepcopy(row[key])
        if int(wire)==5 and context and context.get('wire_t')==5 and context.get('no_wish'):
            data['ctr'] = [0,0,0]
        if int(wire)==5 and context and context.get('wire_t')==5 and not context.get('no_wish') and _special_int(context.get('wish_id')):
            wish = context['wish_id']
            current = row.get('ctr',[0,0,0])
            data['ctr'] = copy.deepcopy(row.get('ctr_by_wish',{}).get(str(wish),current if current[0]==wish else [wish,0,0]))
        for key in ('tw','wi','jzc','jzr','rc'):
            if key in row:data[key]=[(int(k),copy.deepcopy(v))for k,v in sorted(row[key].items(),key=lambda item:int(item[0]))]
    result['ad'] = [(int(wire),data)for wire,data in sorted(activities.items(),key=lambda item:int(item[0]))]
    return result

TREASURE_WISH_REVEAL_POLICY = 'offline-original-display-probability-treasure-wish-v1'


def prepare_treasure_wish_reveal(pools,tables,wire,wish_id,draw_integer):
    """Mutate only transaction-local pools; caller commits with the actual reward.

    The original formula is a CLIENT DISPLAY formula. Bernoulli sampling,
    replacement (not extra award), miss increment and hit reset are explicit
    offline policy, not recovered official hidden-server probabilities.
    """
    if wire != 5:
        raise ValueError('Finite treasure wish producer currently supports only original t5')
    wish = tables.get('chouka_treasure_wish',{}).get(wish_id,{})
    if wish.get('drawType')!=wire or wish.get('wish_type')!=1 or wish.get('times',0)<=0:
        raise ValueError('Missing exact supported original treasure wish period')
    special = _new_special({'gacha_pools':pools})
    row = special['pools'].setdefault(str(wire),{})
    steps = row.setdefault('tw',{})
    before = steps.get(str(wish_id),0)
    if not _special_int(before) or before<0:
        raise ValueError('Invalid original treasure wish step')
    if wish.get('begin_rate') != .02 or wish.get('step_rate') != .01 or wish['times'] != 6:
        raise ValueError('Unsupported original t5 wish probability parameters')
    numerator,denominator = min(100,2+before//wish['times']),100
    probability = numerator / float(denominator)
    roll = draw_integer(denominator)
    if not _special_int(roll) or not 0<=roll<denominator:
        raise ValueError('Wish RNG outside original display probability range')
    hit = roll<numerator
    reward_ids = []
    chosen = row.get('ctr_by_wish',{}).get(str(wish_id),row.get('ctr',[0,0,0]))
    selected = chosen[1] if chosen[0]==wish_id else 0
    if hit:
        reward_ids = list(tables.get('chouka_wish_treasure_choose',{}).get(selected,{}).get('rewards',())) if selected else list(wish.get('reward',()))
        if not reward_ids or any(r not in tables.get('reward_common',{}) for r in reward_ids):
            raise ValueError('Missing actual original wish common rewards')
    after = 0 if hit else before+1
    steps[str(wish_id)] = after
    source = {'policy':TREASURE_WISH_REVEAL_POLICY,'probability_evidence':'original-client-display-formula-only',
        'wish_id':wish_id,'step_before':before,'step_after':after,'display_probability':probability,
        'probability_ratio':[numerator,denominator],'branch':'wish-replacement' if hit else 'normal',
        'selected_treasure':selected,'reward_ids':reward_ids,
        'server_semantics':'offline-policy; no additional award; natural normal target remains possible'}
    return {'special_common_reward_ids':reward_ids,'treasure_wish_source':source},('syncTreasureWishInfo',{'t':wire,'tw_id':wish_id,'s':after})


JIAOZHI_POLICY = 'offline-finite-original-threshold-blessing-v1'


def jiaozhi_rows(tables, wire):
    if wire == 354:
        return []
    return sorted((row for row in tables.get('chouka_jiaozhi',{}).values()
                   if row.get('drawType') == wire), key=lambda row:row['id'])


def prepare_jiaozhi_context(pools, tables, wire, owned, fragments):
    """Transaction-local natural-fragment blessing; no random-rate changes."""
    row = _special_container({'gacha_pools':pools}).get('pools',{}).get(str(wire),{})
    def bless(hero, piece):
        if not piece or str(hero) in owned or hero in owned or row.get('rc',{}).get(str(hero),0) <= 0:
            return piece
        mask = fragments.get(str(hero),0)
        count = tables.get('chouka_hero_file',{}).get(hero,{}).get('file_num',3)
        missing = [p for p in range(1,count+1) if not mask & (1 << (p-1))]
        if not missing:
            return piece
        selected = piece if piece in missing else missing[0]
        row['rc'][str(hero)] -= 1
        return selected
    return {'owned_heroes':set(int(h) for h in owned),'bless_fragment':bless}


def finalize_jiaozhi_reveal(pools, tables, wire, card, random_pool):
    """One-shot thresholds, original reward pools, no recursive bonus counts.

    Count never resets; thresholds award once per pool lifetime. This finite
    offline recurrence policy is explicit because the server is unavailable.
    """
    source_kind = card.get('_gacha_source',{}).get('source_kind','primary_draw')
    if source_kind != 'primary_draw' and (source_kind != 'charge_threshold' or wire not in CHARGE_JIAOZHI_WIRES or card.get('hero_file')):
        return None
    rows = jiaozhi_rows(tables,wire)
    if not rows or not card.get('hero'):
        return None
    special = _new_special({'gacha_pools':pools})
    saved = special['pools'].setdefault(str(wire),{})
    counts,claimed,credits = [saved.setdefault(k,{}) for k in ('jzc','jzr','rc')]
    source = card.setdefault('_gacha_source',{})
    events = []
    for hero in card.get('hero',[]):
        applicable = [r for r in rows if r['target_hero']==hero]
        if not applicable:
            continue
        key = str(hero)
        before = counts.get(key,0)
        counts[key] = before + (1 if card.get('hero_file') else 3)
        for threshold in applicable:
            tid = str(threshold['id'])
            if claimed.get(tid) or counts[key] < threshold['jiaozhi_count']:
                continue
            # Mark before expansion: attached rewards cannot feed this counter.
            claimed[tid] = 1
            if threshold.get('open_hero_file'):
                credits[key] = credits.get(key,0)+1
            start = len(card.get('item',[]))
            for reward in threshold.get('rewards',()):
                random_pool(reward)
            bonus = card.get('item',[])[start:]
            if bonus:
                del card['item'][start:]
                card.setdefault('jiaozhi',{'item':[],'treasure':[]})['item'].extend(bonus)
            events.append(threshold['id'])
    source['jiaozhi'] = {'policy':JIAOZHI_POLICY,'threshold_ids':events,
        'recurrence':'once-per-pool-lifetime','counter_basis':'source-hero-piece-not-get_hero'}
    return ('syncJiaozhiData',{'i':{'t':wire,'jzc':[(int(k),v)for k,v in counts.items()],
        'jzr':[(int(k),v)for k,v in claimed.items()], 'rc':[(int(k),v)for k,v in credits.items()],
        'iuc':[(int(k),v)for k,v in pools.get('inc_up_cnt',{}).items()]}})


def advance_gacha_shadow(card, owned, fragments, tables):
    """Advance only after accepted resolution, including six-card batches."""
    for hero in card.get('hero',[]):
        key = str(hero)
        if not card.get('hero_file'):
            owned.add(key)
        elif key not in owned:
            fragments[key] = fragments.get(key,0) | (1 << (card['hero_file']-1))


def grant_original_pendant(state, definition):
    hero,pendant = definition['pendant']
    profile = state['profile']
    record = profile.get('heroes',{}).get(str(hero))
    if record is not None:
        owned = record.setdefault('pa',[])
    else:
        pending = profile.setdefault('hero_pending',{'ps':{},'psc':{},'pp':{},'ppc':{}})
        previous = pending.setdefault('pp',{})
        normalized = {}
        for key,values in previous.items():
            normalized.setdefault(str(key),[]).extend(v for v in values if v not in normalized.get(str(key),[]))
        pending['pp'] = normalized
        owned = normalized.setdefault(str(hero),[])
    if pendant in owned:
        return list(definition.get('pendant_trans',()))
    owned.append(pendant)
    return []


def gacha_pending_for_client(profile, template=None):
    pending = {key:copy.deepcopy((template or {}).get(key,{})) for key in ('ps','psc','pp','ppc')}
    for key in ('ps','psc','pp','ppc'):
        if key in profile.get('hero_pending',{}):
            pending[key] = copy.deepcopy(profile['hero_pending'][key])
    # Same recursive dictionary-only conversion as original helpers.toIntKeyDict.
    def native(value):
        if type(value) is not dict:
            return value
        result = {}
        for key,leaf in value.items():
            try:
                key = int(key)
            except (ValueError,TypeError):
                pass
            result[key] = native(leaf)
        return result
    return native(pending)


CHARGE_POLICY = 'offline-original-charge-once-no-retro-v1'
HERO_EXTRA_POLICY = 'offline-each-primary-raw-whole-extra-equipment-v1'
CHARGE_JIAOZHI_WIRES = frozenset((203,210,222,241,253,260,270,282,283,288,295,311,323,341,363,382,425,433,440,485,486,487,491))
CHARGE_HERO_CORRECTIONS = {266:115,267:114,268:65,269:116,270:36,271:59}


def original_charge_rows(tables, wire):
    if wire == 354:
        return []
    return sorted((row for row in tables.get('chouka_leiji_reward',{}).values()
                   if row.get('drawType')==wire),key=lambda row:(row['times'],row['id']))


def prepare_charge_crossings(pools, tables, wire, ordinal, reveal_id):
    """Record legacy baseline only on an actual new reveal, never retro-award."""
    rows = original_charge_rows(tables,wire)
    if not rows:
        return []
    saved = pools.setdefault('charge_progress',{'version':1,'policy':CHARGE_POLICY,'baselines':{},'claims':{}})
    if saved.get('version')!=1 or saved.get('policy')!=CHARGE_POLICY:
        raise ValueError('Unknown charge recurrence/migration policy')
    key = str(wire)
    if key not in saved['baselines']:
        saved['baselines'][key] = ordinal-1
        for row in rows:
            if row['times'] <= ordinal-1:
                saved['claims'].setdefault(str(row['id']),{'wire_t':wire,'threshold':row['times'],
                    'status':'historical-unimplemented-no-retro','baseline':ordinal-1,'common_ids':list(row['rewards'])})
    crossings = []
    for row in rows:
        if ordinal-1 < row['times'] <= ordinal and str(row['id']) not in saved['claims']:
            saved['claims'][str(row['id'])] = {'wire_t':wire,'period':'original-wire-lifetime',
                'threshold':row['times'],'reveal_id':reveal_id,'common_ids':list(row['rewards']),
                'status':'prepared','awards':[]}
            crossings.append(row)
    return crossings


def attach_activity_award(primary, bonus):
    """Separate settlement lists; primary hero_file/source never overwritten."""
    activity = primary.setdefault('other_reward',{}).setdefault('activityReward',{})
    activity.setdefault('treasure',[])
    activity.setdefault('item',[]).extend(copy.deepcopy(bonus.get('item',[])))
    activity['item'].extend([[int(item),amount] for item,amount in bonus.get('hero_frag',{}).items()])
    activity['treasure'].extend(copy.deepcopy(bonus.get('treasure',[])))
    if bonus.get('get_hero'):
        activity.setdefault('hero',[]).extend(copy.deepcopy(bonus.get('hero',[])))
    if bonus.get('hero_file') and not bonus.get('hero_frag'):
        activity.setdefault('fragment',[]).append([bonus['hero'][0],bonus['hero_file']])
    if bonus.get('jiaozhi'):
        if '_gacha_own_jiaozhi' not in primary:
            primary['_gacha_own_jiaozhi'] = copy.deepcopy(primary.get('jiaozhi',{}))
        dst = primary.setdefault('jiaozhi',{'item':[],'treasure':[]})
        for key in ('item','treasure'):
            dst[key].extend(copy.deepcopy(bonus['jiaozhi'].get(key,[])))
    primary.setdefault('_gacha_bonus_cards',[]).append(copy.deepcopy(bonus))


def prepare_gacha_activity_bonuses(pools, tables, wire, ordinal, primary, owned, fragments, resolve_bonus, notices):
    """Bounded source-qualified producer; bonuses never re-enter this function.

    primary -> charge rows/common order -> extra equipment -> next card is an
    explicit offline ordering policy. A bonus is an independent canonical plan.
    """
    advance_gacha_shadow(primary,owned,fragments,tables)
    source_id = '%s:%s'%(wire,ordinal)
    source = primary.setdefault('_gacha_source',{})
    source['source_kind'] = 'primary_draw'
    source['reveal_id'] = source_id
    for row in prepare_charge_crossings(pools,tables,wire,ordinal,source_id):
        receipt = pools['charge_progress']['claims'][str(row['id'])]
        for common_id in row['rewards']:
            correction = CHARGE_HERO_CORRECTIONS.get(row['id'])
            bonus = resolve_bonus(common_id,'charge_threshold',row['id'],correction)
            bonus_source = bonus.setdefault('_gacha_source',{})
            bonus_source.update(source_kind='charge_threshold',original_wire_t=wire,
                charge_row_id=row['id'],parent_reveal_id=source_id)
            if correction:
                bonus_source['conflict_policy'] = 'finite-six-original-charge-rows-entry-description-v1'
                bonus_source['corrected_hero'] = correction
            if wire in CHARGE_JIAOZHI_WIRES and not bonus.get('hero_file'):
                notice = finalize_jiaozhi_reveal(pools,tables,wire,bonus,
                    lambda rid: resolve_bonus(rid,'jiaozhi_threshold',row['id'],None,bonus))
                if notice:
                    notices.append(notice)
            advance_gacha_shadow(bonus,owned,fragments,tables)
            attach_activity_award(primary,bonus)
            receipt['awards'].append(copy.deepcopy(bonus))
        receipt['status'] = 'granted-with-primary-transaction'
    if not primary.get('hero_file'):
        for target,common_id in tables.get('chouka_info',{}).get(wire,{}).get('get_hero_extra_reward',()):
            for hero in primary.get('hero',[]):
                if hero!=target:
                    continue
                bonus = resolve_bonus(common_id,'hero_extra_reward',None,None)
                bonus.setdefault('_gacha_source',{}).update(source_kind='hero_extra_reward',
                    original_wire_t=wire,parent_reveal_id=source_id,policy=HERO_EXTRA_POLICY,target_hero=hero)
                attach_activity_award(primary,bonus)
                source.setdefault('hero_extra_receipts',[]).append(copy.deepcopy(bonus['_gacha_source']))
    return primary


def validate_charge_progress(pools):
    saved = pools.get('charge_progress')
    if saved is None:
        return
    if saved.get('version')!=1 or saved.get('policy')!=CHARGE_POLICY or not isinstance(saved.get('baselines'),dict) or not isinstance(saved.get('claims'),dict) or len(saved['claims'])>289:
        raise ValueError('Invalid finite charge progress')
    for wire,count in saved['baselines'].items():
        if not str(wire).isdigit() or int(wire)==354 or not _special_int(count) or count<0:
            raise ValueError('Invalid charge legacy baseline')
    for key,receipt in saved['claims'].items():
        if not str(key).isdigit() or not _special_int(receipt.get('wire_t')) or receipt['wire_t']==354 or not _special_int(receipt.get('threshold')) or receipt['threshold']<=0 or not isinstance(receipt.get('common_ids'),list):
            raise ValueError('Invalid original charge claim identity')
        if receipt.get('status') not in ('historical-unimplemented-no-retro','granted-with-primary-transaction'):
            raise ValueError('Incomplete charge plan cannot become durable')
        if receipt['status']=='granted-with-primary-transaction' and not isinstance(receipt.get('awards'),list):
            raise ValueError('Missing resolved charge award receipt')


HERO_WISH_WIRES = frozenset((1,119,126,143,154,164))
HERO_WISH_PERIOD_POLICY = 'offline-original-hero-wish-period-v1'
HERO_WISH_REVEAL_POLICY = 'offline-original-rule-hero-wish-v1'
HERO_WISH_UNITS = 1000000


def validate_hero_wish_period(tables, wire, identifiers):
    if wire not in HERO_WISH_WIRES or not isinstance(identifiers,(list,tuple)) or not identifiers or any(not _special_int(i) for i in identifiers) or len(set(identifiers))!=len(identifiers):
        raise ValueError('Missing exact finite original hero wish period')
    table = tables.get('chouka_treasure_wish',{})
    first = table.get(identifiers[0],{})
    if first.get('drawType')!=wire or first.get('wish_type')!=2 or not first.get('begin_time') or not first.get('end_time'):
        raise ValueError('Hero wish row/wire/type mismatch')
    expected = sorted(key for key,row in table.items() if row.get('drawType')==wire and row.get('wish_type')==2 and row.get('begin_time')==first['begin_time'] and row.get('end_time')==first['end_time'])
    if sorted(identifiers)!=expected:
        raise ValueError('Hero wish must pin the full original period')
    return [table[key] for key in expected]


def hero_wish_period_for_group(tables, wire, archive):
    if not archive or archive.get('wire_t')!=wire or 'hero_wish_ids' not in archive:
        return None
    if archive.get('hero_wish_policy')!=HERO_WISH_PERIOD_POLICY:
        raise ValueError('Unknown original hero wish archive policy')
    rows = validate_hero_wish_period(tables,wire,archive['hero_wish_ids'])
    return {'hero_wish_policy':HERO_WISH_PERIOD_POLICY,'hero_wish_ids':[row['id'] for row in rows]}


def _hero_wish_initialize(pools, tables, wire, identifiers, owned):
    rows = validate_hero_wish_period(tables,wire,identifiers)
    special = _new_special({'gacha_pools':pools})
    saved = special['pools'].setdefault(str(wire),{})
    periods = saved.setdefault('hero_wish_periods',{})
    key = ','.join(str(row['id']) for row in rows)
    wi = saved.setdefault('wi',{})
    if key not in periods:
        excluded = []
        for row in rows:
            group = wi.setdefault(str(row['gid']),{'c':0,'f':[],'a':[]})
            if str(row['wish_target']) in owned or row['wish_target'] in owned:
                if row['id'] not in group['f']:group['f'].append(row['id'])
                if row['id'] not in group['a']:group['a'].append(row['id'])
                excluded.append(row['id'])
        periods[key] = {'policy':HERO_WISH_REVEAL_POLICY,'row_ids':[row['id'] for row in rows],
            'preexisting_owned':excluded,'provenance':'preexisting_owned-no-award-no-draw-no-animation',
            'begin_time':list(rows[0]['begin_time']),'end_time':list(rows[0]['end_time'])}
    return rows,wi


def hero_wish_probabilities(rows, wi):
    """Exact integer display formula for the finite original 14 rows.

    Original rates/weights here divide one million exactly. Refuse unsupported
    fractions instead of rounding away categorical mass or inventing a pity.
    """
    groups = {}
    for row in rows:
        if row['id'] not in wi.get(str(row['gid']),{}).get('f',[]):
            groups.setdefault(row['gid'],[]).append(row)
    fixed,variable = {},[]
    for gid,entries in groups.items():
        amount = sum(int(round(row.get('fix_rate',0)*HERO_WISH_UNITS)) for row in entries)
        if amount:fixed[gid]=amount
        else:variable.append(gid)
    remaining = max(0,HERO_WISH_UNITS-sum(fixed.values()))
    rates = dict(fixed)
    for gid in variable:
        row = groups[gid][0]
        if type(row.get('times')) is not int or row['times']<=0:
            raise ValueError('Invalid original hero wish step divisor')
        count = wi.get(str(gid),{}).get('c',0)
        probability = min(HERO_WISH_UNITS,int(round(row.get('begin_rate',0)*HERO_WISH_UNITS))+(count//row['times'])*int(round(row.get('step_rate',0)*HERO_WISH_UNITS)))
        if remaining % len(variable):
            raise ValueError('Unsupported fractional original variable wish mass')
        rates[gid] = min(remaining//len(variable),probability)
    probabilities = {}
    for gid,entries in groups.items():
        weight = sum(row.get('wish_weight',0) for row in entries)
        for row in entries:
            numerator = rates[gid]*(row.get('wish_weight',0) if weight else 1)
            denominator = weight or len(entries)
            if numerator % denominator:
                raise ValueError('Unsupported fractional original hero wish weight')
            probabilities[row['id']] = numerator//denominator
    if sum(probabilities.values())>HERO_WISH_UNITS:
        raise ValueError('Original hero wish probability exceeds total mass')
    return probabilities,rates


def prepare_hero_wish_reveal(pools, tables, wire, pinned, owned, draw_integer):
    """Mutate transaction-local eligibility only for an accepted new reveal."""
    if pinned.get('hero_wish_policy')!=HERO_WISH_PERIOD_POLICY:
        raise ValueError('Unverified pinned original hero wish period')
    rows,wi = _hero_wish_initialize(pools,tables,wire,pinned.get('hero_wish_ids'),owned)
    probabilities,group_rates = hero_wish_probabilities(rows,wi)
    roll = draw_integer(HERO_WISH_UNITS)
    if not _special_int(roll) or not 0<=roll<HERO_WISH_UNITS:
        raise ValueError('Hero wish RNG outside original categorical mass')
    remaining,selected = roll,None
    for identifier,probability in sorted(probabilities.items()):
        if remaining<probability:
            selected=identifier
            break
        remaining-=probability
    chosen = next((row for row in rows if row['id']==selected),None)
    context = {'special_common_reward_ids':list(chosen['reward'])} if chosen else {}
    plan = {'policy':HERO_WISH_REVEAL_POLICY,'row_ids':[row['id'] for row in rows],
        'selected_row':selected,'roll':roll,'probability_denominator':HERO_WISH_UNITS,
        'row_probability_units':[[key,value]for key,value in sorted(probabilities.items())],
        'ordinary_probability_units':HERO_WISH_UNITS-sum(probabilities.values()),
        'before':copy.deepcopy(wi),'safe_times_policy':'metadata-only-not-enforced'}
    return context,plan


def finalize_hero_wish_reveal(pools, tables, wire, plan, card):
    """Only raw primary wholes complete f; extras never enter this transition."""
    saved = _special_container({'gacha_pools':pools})['pools'][str(wire)]
    wi = saved['wi']
    table = tables['chouka_treasure_wish']
    groups = {}
    for identifier in plan['row_ids']:
        row = table[identifier]
        if identifier not in wi[str(row['gid'])]['f']:
            groups.setdefault(row['gid'],[]).append(row)
    whole = set(card.get('hero',[])) if not card.get('hero_file') else set()
    for gid,rows in groups.items():
        group = wi[str(gid)]
        matches = [row['id'] for row in rows if row['wish_target'] in whole]
        fixed = any(row.get('fix_rate',0) for row in rows)
        group['c'] = group['c']+1 if fixed or not matches else 0
        group['f'] = sorted(set(group['f']) | set(matches))
    plan['after'] = copy.deepcopy(wi)
    card.setdefault('_gacha_source',{})['hero_wish'] = copy.deepcopy(plan)
    return ('syncWishGroupInfo',{'t':wire,'i':[(int(gid),copy.deepcopy(data))for gid,data in sorted(wi.items(),key=lambda pair:int(pair[0]))]})


def hero_wish_eligibility_view(state, tables, archive):
    """Prospective first-period f/a for original UI, without a state write."""
    if not archive or archive.get('wire_t') not in HERO_WISH_WIRES:
        return state
    pinned = hero_wish_period_for_group(tables,archive['wire_t'],archive)
    if not pinned:
        return state
    key = ','.join(str(identifier) for identifier in pinned['hero_wish_ids'])
    saved = _special_container(state).get('pools',{}).get(str(archive['wire_t']),{})
    if key in saved.get('hero_wish_periods',{}):
        return state
    candidate = copy.deepcopy(state)
    if not isinstance(candidate.get('gacha_pools'),dict):candidate['gacha_pools']={'pools':{}}
    _hero_wish_initialize(candidate['gacha_pools'],tables,archive['wire_t'],
        pinned['hero_wish_ids'],set(candidate.get('profile',{}).get('heroes',{})))
    return candidate
