# -*- coding: ascii -*-
"""Original snapshot weighted mixed rewards and whole-state atomic grants.

No filesystem/network operations. RNG, original hero conversion and treasure
constructors are injected. Never discard an unsupported bucket and reroll hero.
"""
import copy
import json
try:
    from offline_gacha_special import resolve_self_choose_item
except ImportError:
    pass
try:
    _gr_int = (int, long)
except NameError:
    _gr_int = (int,)

GACHA_REWARD_POLICY = 'original-snapshot-mixed-weights-v1'


def _gr_positive(value, label):
    if not isinstance(value, _gr_int) or isinstance(value, bool) or value <= 0:
        raise ValueError('Invalid original %s' % label)
    return value


def _gr_choose(entries, draw_integer):
    """Exact integer/rational original numeric weights; no uniform fallback."""
    ratios = []
    denominator = 1
    for value, weight in entries:
        if isinstance(weight, bool) or not isinstance(weight, _gr_int + (float,)) or weight < 0:
            raise ValueError('Invalid original random weight')
        if not weight:
            continue
        if isinstance(weight, float):
            numerator, divisor = weight.as_integer_ratio()
        else:
            numerator, divisor = weight, 1
        denominator = max(denominator, divisor)  # float denominators are powers of two
        ratios.append((value, numerator, divisor))
    weighted = [(value, numerator * (denominator // divisor)) for value,numerator,divisor in ratios]
    total = sum(weight for unused,weight in weighted)
    if not total:
        raise ValueError('Original pool has no positive-weight candidates')
    roll = draw_integer(total)
    if not isinstance(roll, _gr_int) or isinstance(roll, bool) or not 0 <= roll < total:
        raise ValueError('Injected random draw outside original weight total')
    for value,weight in weighted:
        if roll < weight:
            return value
        roll -= weight
    raise ValueError('Original weighted selection did not resolve')


def make_table_hero_result(tables, owned_heroes, fragment_progress=None):
    """Original LuckyDrawData.getHeroOrFileExchangeItems conversion metadata."""
    owned = set(int(hero) for hero in owned_heroes)
    ranks = {1:4253, 2:4254, 3:4255, 4:4256}
    def result(hero, piece):
        row = tables.get('hero', {}).get(hero)
        file_row = tables.get('chouka_hero_file', {}).get(hero)
        if row is None or file_row is None:
            raise ValueError('Missing original hero/fragment conversion metadata')
        if type(piece) is not int or not 0 <= piece <= file_row.get('file_num', 0):
            raise ValueError('Invalid original hero fragment ordinal')
        reward = {'hero':[hero], 'hero_file':piece, 'get_hero':hero not in owned and piece == 0, 'hero_frag':{}}
        if hero in owned:
            item = ranks.get(row.get('hero_composite_init_rank'))
            if not item:
                raise ValueError('Unknown original hero initial rank conversion')
            amounts = {item:1} if piece else {item:file_row.get('jj_hero_exchange',0),24:file_row.get('sp_hero_exchange',0)}
            reward['hero_frag'] = {str(item):amount for item,amount in amounts.items() if amount}
        return reward
    return result


def make_original_gacha_resolver(tables, draw_integer, make_treasure, hero_result, pool_context=None):
    """Return resolver(wire_t, ordinal, force_s=False) -> fixed mixed card.

    pool_context may provide inc_up_cnt keyed by original shared counter type.
    Original UP fields require that context; no unrelated pool ordinal substitutes
    for inherited counters. Original defaults always precede weighted selection.
    """
    normal = {}
    for key,row in tables.get('chouka_normal', {}).items():
        normal.setdefault(row.get('type'), []).append((key,row))
    for rows in normal.values():
        rows.sort(key=lambda entry:entry[0])

    def resolve(wire_t, ordinal, force_s=False):
        _gr_positive(wire_t, 'wire drawType'); _gr_positive(ordinal, 'draw ordinal')
        source = {'policy':GACHA_REWARD_POLICY, 'wire_t':wire_t, 'ordinal':ordinal, 'reward_ids':[], 'random_pools':[]}
        result = {'get_hero':False, 'hero_file':0, 'hero_frag':{},
            'other_reward':{'activityReward':{'treasure':[]}}, '_gacha_treasures':[], '_gacha_source':source}
        info = tables.get('chouka_info', {}).get(wire_t, {})
        source['inc_up_cnt_type'] = info.get('inc_up_cnt_type',0) if any(key in info for key in ('up_m','up_n','up_x','up_r')) else info.get('inc_up_cnt_type')
        source['is_up'] = False
        source['up_classification'] = 'original_row_when_present; defaults_are_not_inferred_UP'
        context = pool_context(wire_t,ordinal) if pool_context else {}
        context = context or {}
        override = tables.get('chouka_default', {}).get((wire_t,ordinal), {})
        if wire_t == 99:
            override = tables.get('chouka_friend_default', {}).get(ordinal, override)
        pool = override.get('pool')

        def hero(hid, piece):
            original_piece = piece
            piece = context.get('bless_fragment',lambda h,p:p)(hid,piece)
            if piece != original_piece:
                source.setdefault('fragment_blessing',[]).append({'hero':hid,'original_piece':original_piece,'piece':piece,'policy':'next-natural-target-lowest-missing-v1'})
            reward = hero_result(hid,piece)
            if not isinstance(reward, dict) or reward.get('hero') != [hid] or reward.get('hero_file',0) != piece:
                raise ValueError('Original hero converter returned mismatched result')
            result.setdefault('hero', []).append(hid)
            result['hero_file'] = piece
            result['get_hero'] = bool(result['get_hero'] or reward.get('get_hero'))
            for item,amount in reward.get('hero_frag', {}).items():
                result.setdefault('_gacha_item_trade_types',{})[str(item)] = tables.get('item_data',{}).get(int(item),{}).get('tradeType',0)
                _gr_positive(int(item),'conversion item'); _gr_positive(amount,'conversion amount')
                result['hero_frag'][str(item)] = result['hero_frag'].get(str(item),0) + amount

        def treasure(template, quality, quantity, trade, design=None):
            _gr_positive(quantity,'treasure quantity')
            if quantity > 100:
                raise ValueError('Original treasure quantity outside bounded transaction')
            identities = []
            for unused in range(quantity):
                item = make_treasure(template,quality,trade)
                if design is not None:
                    built = json.loads(design['dumps_info'])
                    built['u'] = item['u']
                    built['ctt'] = item.get('ctt',0)
                    item = built
                if item.get('i') != template or item.get('tr',{}).get('cl') != quality or not item.get('tr',{}).get('attr'):
                    raise ValueError('Original treasure constructor returned missing template/class/attributes')
                identities.append(str(item['u']))
                result['_gacha_treasures'].append(copy.deepcopy(item))
            result.setdefault('treasure', []).append([template,quality,quantity,identities])

        def common(reward_id, depth):
            if depth > 12:
                raise ValueError('Original nested reward depth exceeds bound')
            row = tables.get('reward_common', {}).get(reward_id)
            if row is None:
                raise ValueError('Missing original common reward %s' % reward_id)
            allowed = set(('id','tradeType','award_pool','hero','items','itemsNum','treasure','treasureNum','treasureLevel','design_treasure',
                'money','summoncoin','crystal','friendcoin','yuanbao','giftcoin','gift','skin','furniture'))
            unknown = sorted(set(row)-allowed)
            if unknown:
                raise ValueError('Unsupported original reward %s fields %s' % (reward_id,','.join(unknown)))
            source['reward_ids'].append(reward_id)
            for hid in row.get('hero', ()):
                hero(hid,0)
            items,counts = row.get('items',()),row.get('itemsNum',())
            if len(items) != len(counts):
                raise ValueError('Mismatched original item reward arrays')
            for iid,amount in zip(items,counts):
                _gr_positive(amount,'item quantity')
                definition = tables.get('item_data', {}).get(iid)
                if definition is None:
                    raise ValueError('Missing original reward item %s' % iid)
                chosen = resolve_self_choose_item(tables,wire_t,iid,amount,context)
                if chosen is not None:
                    source.setdefault('self_choose_items',[]).append([iid,amount])
                    for hid,piece in chosen:
                        hero(hid,piece)
                    continue
                fragment = definition.get('memoryFrag')
                if fragment:
                    if amount != 1 or len(fragment) != 2:
                        raise ValueError('Unsupported original fragment bundle')
                    hero(fragment[0],fragment[1])
                else:
                    result.setdefault('item', []).append([iid,amount])
                    result.setdefault('_gacha_item_trade_types',{})[str(iid)] = row.get('tradeType',definition.get('tradeType',0))
            ids,counts,classes = (row.get(key,()) for key in ('treasure','treasureNum','treasureLevel'))
            if ids and (len(ids) != len(counts) or len(ids) != len(classes)):
                raise ValueError('Mismatched original treasure reward arrays')
            if not ids and (counts or classes) and not row.get('design_treasure'):
                raise ValueError('Original treasure amounts lack template/design')
            for tid,amount,quality in zip(ids,counts,classes):
                treasure(tid,quality,amount,row.get('tradeType',0))
            if row.get('design_treasure'):
                design = tables.get('hero_treasure_generate', {}).get(row['design_treasure'])
                if design is None:
                    raise ValueError('Missing original designed treasure')
                if counts and len(counts)!=1 or classes and (len(classes)!=1 or classes[0]!=design['treasureClass']):
                    raise ValueError('Original designed treasure class/quantity mismatch')
                treasure(design['itemid'],design['treasureClass'],counts[0] if counts else 1,design.get('tradeType',row.get('tradeType',0)),design)
            for key in ('money','summoncoin','crystal','friendcoin','yuanbao','giftcoin','gift'):
                if key in row:
                    _gr_positive(row[key],key)
                    result[key] = result.get(key,0) + row[key]
            for key in ('skin','furniture'):
                if row.get(key):
                    result.setdefault(key, []).extend(copy.deepcopy(row[key]))
            nested = row.get('award_pool')
            if isinstance(nested,_gr_int) and not isinstance(nested,bool) and nested:
                random_pool(nested,depth+1)
            elif nested and not (isinstance(nested,(tuple,list)) and all(isinstance(value,str) for value in nested)):
                raise ValueError('Unsupported original award_pool schema')

        def random_pool(pool_id, depth=0):
            row = tables.get('reward_random', {}).get(pool_id)
            if row is None:
                raise ValueError('Missing original random reward pool %s' % pool_id)
            source['random_pools'].append(pool_id)
            common(_gr_choose(row.get('weights',()),draw_integer),depth+1)

        if context.get('treasure_wish_source'):
            source['treasure_wish'] = copy.deepcopy(context['treasure_wish_source'])
        if context.get('direct_hero_reward'):
            source['reward_ids'].append(context['original_common_reward_id'])
            hero(context['direct_hero_reward'],0)
        elif context.get('special_random_reward_ids'):
            for pool_id in context['special_random_reward_ids']:
                random_pool(pool_id)
        elif context.get('special_common_reward_ids'):
            for reward_id in context['special_common_reward_ids']:
                common(reward_id,0)
        elif pool:
            source['default_pool'] = pool
            random_pool(pool)
        else:
            if wire_t == 99:
                rows = sorted(tables.get('chouka_friend',{}).items())
            else:
                rows = normal.get(wire_t,[])
            positive = [(key,row) for key,row in rows if row.get('weight',0)>0]
            has_up_rules = any(key in info for key in ('up_m','up_n','up_x','up_r'))
            if has_up_rules:
                counts = context.get('inc_up_cnt')
                counter_type = info.get('inc_up_cnt_type',0)
                if not isinstance(counts,dict):
                    raise ValueError('Original UP pool requires persisted shared inc_up_cnt context')
                if info.get('up_x',999999) <= 0:
                    raise ValueError('Invalid original UP step size')
                count = counts.get(counter_type,counts.get(str(counter_type),0))
                if not isinstance(count,_gr_int) or count < 0:
                    raise ValueError('Invalid original shared UP count')
                up = [(key,row) for key,row in positive if row.get('is_up')]
                others = [(key,row) for key,row in positive if not row.get('is_up')]
                hard = count >= info.get('up_n',999999)
                steps = max(0,count-info.get('up_m',999999)) // info.get('up_x',999999)
                if hard or context.get('force_up'):
                    positive = up
                    source['forced_up'] = True
                elif steps and info.get('up_r',0):
                    total = sum(row['weight'] for key,row in positive)
                    up_total = sum(row['weight'] for key,row in up)
                    numerator = min(100*total,100*up_total+steps*info['up_r']*total)
                    selected_up = _gr_choose([(True,numerator),(False,100*total-numerator)],draw_integer)
                    positive = up if selected_up else others
                    source['soft_up_steps'] = steps
            elif context.get('force_up'):
                positive = [(key,row) for key,row in positive if row.get('is_up')]
                source['forced_up'] = True
            key,row = _gr_choose([((key,row),row.get('weight',0)) for key,row in positive],draw_integer)
            source['normal_row'] = key
            source['is_up'] = bool(row.get('is_up'))
            selected_pools = row.get('rewards' if wire_t == 99 else 'random_reward', ())
            owned = context.get('owned_heroes',set())
            matches = [(heroes,rewards) for heroes,rewards in row.get('replace_reward',()) if set(heroes).issubset(owned)]
            if matches:
                heroes,selected_pools = sorted(enumerate(matches),key=lambda pair:(-len(pair[1][0]),pair[0]))[0][1]
                source['replace'] = {'heroes':list(heroes),'policy':'pre-draw-owned-longest-original-order-v1'}
            for pool_id in selected_pools:
                random_pool(pool_id)
        if context.get('activity_finalize'):
            context['activity_finalize'](result,random_pool)
        if force_s:
            heroes = result.get('hero',[])
            if result.get('hero_file') or not heroes or not all(tables.get('hero',{}).get(hid,{}).get('hero_composite_init_rank') == 4 for hid in heroes):
                raise ValueError('Explicit S guarantee not fulfilled by original selected default/rule')
        if not source['reward_ids']:
            raise ValueError('Original draw produced no reward; no hero-only substitution')
        return result
    return resolve


def apply_original_gacha_rewards(state, cards, make_id, stack_limit, grant_hero=None, grant_extra=None, item_definitions=None, grant_pendant=None):
    """Return candidate, client cards, notices; all grants use canonical inventory.

    Caller passes ONLY newly-granted cards from pools(credit_items=False). No
    per-pool inventory merge. Constructors/converters must not write external
    state; failures discard this candidate and never change the input state.
    """
    candidate = copy.deepcopy(state)
    rendered, notices, updates = [], [], []
    inventory = candidate.setdefault('gacha',{}).setdefault('items',[])
    occupied = set(str(item['u']) for item in inventory)
    treasures = candidate['profile'].setdefault('treasures',{'version':1,'items':[]})['items']
    occupied.update(str(item['u']) for item in treasures)
    def item(template, amount, trade):
        _gr_positive(template,'item template'); _gr_positive(amount,'item amount')
        maximum = stack_limit(template)
        _gr_positive(maximum,'original item stack limit')
        remaining = amount
        for saved in inventory:
            if saved['i'] != template or saved.get('tr') or saved.get('tt',0) != trade:
                continue
            added = min(remaining,max(0,maximum-saved['w']))
            if added:
                saved['w'] += added
                updates.append(copy.deepcopy(saved))
                remaining -= added
        while remaining:
            uid = str(make_id())
            if len(uid)!=24 or any(char not in '0123456789abcdef' for char in uid) or uid in occupied:
                raise ValueError('Original inventory constructor returned invalid/duplicate ObjectId')
            occupied.add(uid)
            amount = min(remaining,maximum)
            record = {'u':uid,'i':template,'w':amount,'tt':trade,'c':0,'ctt':0,'le':0,'lo':None,'ele':0}
            inventory.append(record)
            updates.append(copy.deepcopy(record))
            remaining -= amount
    work = []
    for raw in cards:
        work.append((raw,True))
        work.extend((bonus,False) for bonus in raw.get('_gacha_bonus_cards',[]))
    for raw,primary in work:
        card = copy.deepcopy(raw)
        card.pop('_gacha_bonus_cards',None)
        own_jiaozhi = card.pop('_gacha_own_jiaozhi',card.get('jiaozhi',{}))
        trades = card.pop('_gacha_item_trade_types',{})
        for key,amount in card.get('hero_frag',{}).items():
            item(int(key),amount,trades.get(str(key),0))
        for template,amount in list(card.get('item',())) + list(own_jiaozhi.get('item',())):
            definition = (item_definitions or {}).get(template,{})
            if definition.get('type')==8 and definition.get('virtual_sub_type',definition.get('subtype'))==13:
                if not callable(grant_pendant):
                    raise ValueError('Original pendant requires canonical ownership grant')
                for unused in range(amount):
                    for converted,quantity in grant_pendant(candidate,definition):
                        item(converted,quantity,(item_definitions or {}).get(converted,{}).get('tradeType',0))
            else:
                item(template,amount,trades.get(str(template),0))
        if card.get('get_hero'):
            if not callable(grant_hero):
                raise ValueError('New hero requires injected original snapshot constructor')
            for hid in card.get('hero',()):
                record = grant_hero(candidate,hid)
                if not isinstance(record,dict):
                    raise ValueError('Original hero constructor did not return persistent snapshot')
                if str(hid) in candidate['profile']['heroes']:
                    raise ValueError('Prepared new hero reward conflicts with actual ownership')
                pending = candidate['profile'].get('hero_pending',{}).get('pp',{})
                for pendant in pending.pop(str(hid),[]):
                    if pendant not in record.setdefault('pa',[]):
                        record['pa'].append(pendant)
                candidate['profile']['heroes'][str(hid)] = copy.deepcopy(record)
        elif card.get('hero_file') and not card.get('hero_frag'):
            hid = card.get('hero',[None])[0]
            piece = card['hero_file']
            progress = candidate['gacha'].setdefault('hero_fragment_progress',{})
            progress[str(hid)] = progress.get(str(hid),0) | (1 << (piece-1))
        planned = card.pop('_gacha_treasures',[])
        summaries = card.get('treasure',[])
        if any(not isinstance(entry,(tuple,list)) or len(entry)!=4 or entry[2]!=len(entry[3]) for entry in summaries):
            raise ValueError('Invalid original treasure summary quantity/schema')
        summary_ids = [str(uid) for entry in summaries for uid in entry[3]]
        cursor = 0
        for template,quality,quantity,identities in summaries:
            for identity in identities:
                if cursor >= len(planned) or planned[cursor].get('i')!=template or planned[cursor].get('tr',{}).get('cl')!=quality:
                    raise ValueError('Treasure wire template/class disagrees with actual instance')
                cursor += 1
        if summary_ids != [str(saved.get('u')) for saved in planned]:
            raise ValueError('Treasure wire summary lacks matching canonical instance plan')
        for saved in planned:
            uid = str(saved.get('u'))
            if len(uid)!=24 or any(char not in '0123456789abcdef' for char in uid) or uid in occupied or not saved.get('tr',{}).get('attr'):
                raise ValueError('Missing actual original treasure attributes or unique ObjectId')
            occupied.add(uid)
            treasures.append(copy.deepcopy(saved))
            updates.append(copy.deepcopy(saved))
        economy = candidate['profile'].setdefault('economy',{})
        for key,canonical,notice in (('money','money','updateMoney'),('summoncoin','summoncoin','updateSummonCoin'),
                ('crystal','crystal','updateCrystal'),('friendcoin','friendcoin','updateFriendCoin')):
            if card.get(key):
                _gr_positive(card[key],key)
                economy[canonical] = economy.get(canonical,0)+card[key]
                payload = {'v':economy[canonical]}
                if key=='crystal':payload['bv']=economy.get('bind_crystal',0)
                notices.append((notice,payload))
        extras = {key:card[key] for key in ('skin','furniture','yuanbao','giftcoin','gift') if card.get(key)}
        if extras:
            if not callable(grant_extra):
                raise ValueError('Original extra reward requires explicit injected handler: %s'%','.join(sorted(extras)))
            extra_notices = grant_extra(candidate,copy.deepcopy(extras))
            notices.extend(extra_notices or [])
        card.pop('_gacha_source',None)
        card.setdefault('other_reward',{}).setdefault('activityReward',{}).setdefault('treasure',[])
        if primary:
            rendered.append(card)
    if updates:
        notices.append(('updateItems',{'i':updates}))
    return candidate, rendered, notices
