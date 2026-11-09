"""Original currency exchanges: pure canonical inventory transactions, no UI I/O."""
import copy
import hashlib
import json

ITEM_EXCHANGE_METHODS = ('memoryCrystalExchangeSuipian', 'summoncoinExchange', 'yuanbaoExchangeCrystal')
_EXCHANGE_MAX = 2147483647
try:
    _EXCHANGE_TEXT_TYPES = (basestring,)
except NameError:
    _EXCHANGE_TEXT_TYPES = (str,)


def _ex_int(value, positive=False):
    if type(value) is not int or value < (1 if positive else 0) or value > _EXCHANGE_MAX:
        raise ValueError('Invalid original exchange integer')
    return value


def validate_item_exchange(state):
    ledger = (state.get('gacha') or {}).get('item_exchange')
    if ledger is None:
        return
    if ledger.get('version') != 1 or not isinstance(ledger.get('receipts'), list):
        raise ValueError('Invalid item exchange ledger')
    ids = [row['id'] for row in ledger['receipts']]
    if len(ids) != len(set(ids)) or len(ids) > 4096:
        raise ValueError('Invalid item exchange receipt identities')
    if any(not isinstance(row.get('fingerprint'),_EXCHANGE_TEXT_TYPES) or len(row['fingerprint'])!=64 or row.get('method') not in ITEM_EXCHANGE_METHODS for row in ledger['receipts']):
        raise ValueError('Invalid exchange receipt fingerprint or method')
    if not isinstance(ledger.get('limits',{}),dict) or any(type(v)is not int or v<0 or v>_EXCHANGE_MAX for v in ledger.get('limits',{}).values()):
        raise ValueError('Invalid original exchange limit counters')


def prepare_item_exchange(state, method, arguments, tables, operation_id, make_id, now=None):
    """No mutation on failure. Caller persists before emitting success or deltas.

    Receipts are never evicted: after 4096 operations fail closed rather than
    allowing an old callback to spend again. Capacity is an explicit offline
    safety boundary, not an asserted original bag-capacity rule.
    """
    if method not in ITEM_EXCHANGE_METHODS or not isinstance(arguments, dict):
        raise ValueError('Unsupported currency exchange')
    validate_item_exchange(state)
    if not isinstance(operation_id, _EXCHANGE_TEXT_TYPES) or not operation_id or len(operation_id) > 300:
        raise ValueError('Missing stable exchange operation identity')
    args = dict((k,v) for k,v in arguments.items() if k != '_cbid_')
    fingerprint = hashlib.sha256(json.dumps([method,args],sort_keys=True,separators=(',',':')).encode('ascii')).hexdigest()
    old = (state.get('gacha') or {}).get('item_exchange', {})
    for receipt in old.get('receipts', []):
        if receipt['id'] == operation_id:
            if receipt['fingerprint'] != fingerprint:
                raise ValueError('Exchange replay arguments changed')
            return copy.deepcopy(state), [], False, {'success':True,'replay':True}
    if len(old.get('receipts', [])) >= 4096:
        raise ValueError('Exchange receipt capacity reached; existing save preserved')
    candidate = copy.deepcopy(state)
    ledger = candidate.setdefault('gacha',{}).setdefault('item_exchange',{'version':1,'receipts':[],'limits':{},'calendar_policy':'offline-UTC8-07-daily-Monday-weekly-v1'})
    inventory = candidate['gacha'].setdefault('items',[])
    economy = candidate['profile'].setdefault('economy',{})
    items = tables['item_data']
    updates, deleted, notices = [], [], []

    def debit_item(template, amount):
        eligible = [i for i in inventory if i['i']==template and not i.get('tr') and not i.get('lo') and not i.get('le')]
        if sum(_ex_int(i['w']) for i in eligible) < amount:
            raise ValueError('Insufficient available original item balance')
        left = amount
        for item in eligible:
            take = min(left,item['w']); item['w'] -= take; left -= take
            if take:
                if item['w']: updates.append(copy.deepcopy(item))
                else: deleted.append(item['u']); inventory.remove(item)
            if not left: break

    def credit_item(template, amount):
        definition = items[template]
        maximum = _ex_int(definition.get('wrap'),True)
        trade = _ex_int(definition.get('tradeType',0))
        _ex_int(amount,True)
        if sum(i['w'] for i in inventory if i['i']==template)+amount > _EXCHANGE_MAX:
            raise ValueError('Original item balance overflow')
        left = amount
        for item in inventory:
            if item['i']!=template or item.get('tt',0)!=trade or item.get('tr') or item.get('lo') or item.get('le'): continue
            take=min(left,max(0,maximum-item['w']))
            if take: item['w']+=take;left-=take;updates.append(copy.deepcopy(item))
            if not left:break
        needed=(left+maximum-1)//maximum
        if len(inventory)+needed>10000:
            raise ValueError('Offline exchange inventory safety capacity exceeded')
        occupied=set(str(i['u'])for i in inventory)
        for unused in range(needed):
            uid=str(make_id())
            if len(uid)!=24 or any(c not in '0123456789abcdef'for c in uid) or uid in occupied:raise ValueError('Invalid original ObjectId')
            occupied.add(uid);take=min(left,maximum);left-=take
            record={'u':uid,'i':template,'w':take,'tt':trade,'c':0,'ctt':0,'le':0,'lo':None,'ele':0}
            inventory.append(record);updates.append(copy.deepcopy(record))

    def balance(name):return _ex_int(economy.get(name,0))
    def spend(name, amount):
        if balance(name)<amount:raise ValueError('Insufficient canonical '+name)
        economy[name]=balance(name)-amount
    def grant(name, amount):economy[name]=_ex_int(balance(name)+amount)

    if method=='memoryCrystalExchangeSuipian':
        rows=args.get('ii')
        if set(args)!=set(['ii']) or not isinstance(rows,(list,tuple)) or not 1<=len(rows)<=4:raise ValueError('Invalid memory crystal exchange rows')
        totals={}
        for row in rows:
            if not isinstance(row,(list,tuple))or len(row)!=2:raise ValueError('Invalid memory crystal row')
            template,amount=_ex_int(row[0],True),_ex_int(row[1],True)
            definition=tables['memory_crystal_exchange'].get(template)
            if not definition or not definition.get('release') or definition.get('mc_itemid')!=template:raise ValueError('Unavailable original crystal conversion')
            totals[template]=_ex_int(totals.get(template,0)+amount,True)
        reward=0
        for template,amount in sorted(totals.items()):
            reward=_ex_int(reward+amount*_ex_int(tables['memory_crystal_exchange'][template]['suipian_num'],True),True)
            debit_item(template,amount)
        credit_item(tables['fragment_common_id'],reward)
        reply=('replyMemoryCrystalExchangeSuipian',{'ii':[[t,n]for t,n in sorted(totals.items())],'sp':reward})
    elif method=='yuanbaoExchangeCrystal':
        if set(args)!=set(['yn']):raise ValueError('Invalid diamond exchange args')
        amount=_ex_int(args['yn'],True);row=tables['center_bank'][('yuanbao','crystal')]
        ratio=row['ratio'];reward=amount*ratio
        if reward!=int(reward):raise ValueError('Nonintegral original crystal conversion')
        reward=_ex_int(int(reward),True)
        if amount>row.get('personLimit',_EXCHANGE_MAX):raise ValueError('Original per-person conversion limit exceeded')
        spend('yuanbao',amount);grant('crystal',reward)
        notices.extend([('exchangeYuanbaoBalance',{'v':economy['yuanbao']}),('updateCrystal',{'v':balance('crystal'),'bv':balance('bind_crystal')})])
        reply=('yuanbaoExchangeCrystalReply',{'yn':amount,'cn':reward})
    else:
        if set(args)!=set(['i']):raise ValueError('Invalid summon coin exchange args')
        index=_ex_int(args['i'],True);row=tables['summoncoin_exchange'].get(index)
        if not row:raise ValueError('Unknown original summoncoin conversion')
        day,week=item_exchange_period(now)
        for period,key,limit in [('week',week,row.get('weekly_num',0)),('day',day,row.get('daily_num',0))]:
            if limit:
                token=period+':'+key+':'+str(index);used=ledger['limits'].get(token,0)
                if used>=_ex_int(limit,True):raise ValueError('Original exchange limit reached')
                ledger['limits'][token]=used+1
        diamond=_ex_int(row.get('diamond',0));crystal=_ex_int(row.get('crystal',0))
        if not diamond and not crystal:raise ValueError('Unpriced original exchange')
        if diamond:spend('yuanbao',diamond);notices.append(('exchangeYuanbaoBalance',{'v':balance('yuanbao')}))
        if crystal:
            # Bound-first spending is an explicit offline policy; total original price unchanged.
            bound=min(balance('bind_crystal'),crystal);spend('bind_crystal',bound);spend('crystal',crystal-bound)
            notices.append(('updateCrystal',{'v':balance('crystal'),'bv':balance('bind_crystal')}))
        grant('summoncoin',_ex_int(row['summoncoin'],True));notices.append(('updateSummonCoin',{'v':balance('summoncoin')}))
        reply=('summoncoinExchangeReply',{'r':True,'i':index})
    if deleted:notices.insert(0,('deleteItems',{'i':deleted}))
    if updates:notices.insert(0,('updateItems',{'i':updates}))
    notices.append(reply)
    ledger['receipts'].append({'id':operation_id,'fingerprint':fingerprint,'method':method,'reply':copy.deepcopy(reply)})
    validate_item_exchange(candidate)
    return candidate,notices,True,{'success':True,'replay':False}


def item_exchange_period(now):
    # Explicit offline calendar policy. Original 7h-daily refresh is known;
    # weekly Monday07:00 UTC+8 is policy, not a claimed recovered server rule.
    if isinstance(now,bool) or not isinstance(now,(int,float)) or not 0 <= now <= 4102444800:
        raise ValueError('Missing valid exchange calendar clock')
    day=int((now+3600)//86400)
    return str(day),str((day+3)//7)


def item_exchange_limits(state, now):
    ledger=(state.get('gacha')or{}).get('item_exchange',{})
    day,week=item_exchange_period(now)
    result={'sdl':[],'swl':[]}
    for key,value in ledger.get('limits',{}).items():
        for prefix,field in [('week:'+week+':','swl'),('day:'+day+':','sdl')]:
            if key.startswith(prefix):result[field].append((int(key[len(prefix):]),value))
    return result
