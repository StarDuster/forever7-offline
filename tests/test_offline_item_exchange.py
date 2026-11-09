import copy
import sys
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'runtime'),str(ROOT/'analysis/research-agent')]
from read_literal_marshal import read
from offline_item_exchange import prepare_item_exchange,item_exchange_limits

class OriginalItemExchangeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tables={n:read(ROOT/'analysis/android640-scripts/com/data/cdata'/(n+'.marshal'))for n in ['item_data','memory_crystal_exchange','center_bank','summoncoin_exchange']}
        cls.tables['fragment_common_id']=24
    def setUp(self):
        self.clock=1700000000
        self.serial=100
        self.state={'profile':{'economy':{'yuanbao':100000,'crystal':100000,'bind_crystal':1000,'summoncoin':0}},'story':{'week':0,'day':0},'gacha':{'items':[{'u':'%024x'%1,'i':4253,'w':5,'tt':3,'c':0,'ctt':0,'le':0,'lo':None,'ele':0}]}}
    def uid(self):self.serial+=1;return '%024x'%self.serial
    def run_exchange(self,method,args,state=None,operation='one'):
        return prepare_item_exchange(state or self.state,method,args,self.tables,operation,self.uid,self.clock)
    def test_original_four_memory_crystal_rates_and_stack_trade(self):
        self.assertEqual({k:v['suipian_num']for k,v in self.tables['memory_crystal_exchange'].items()},{4253:10,4254:50,4255:80,4256:125})
        result,notices,changed,diag=self.run_exchange('memoryCrystalExchangeSuipian',{'ii':[[4253,5]]})
        self.assertTrue(changed);self.assertEqual(len(result['gacha']['items']),1)
        reward=result['gacha']['items'][0];self.assertEqual((reward['i'],reward['w'],reward['tt']),(24,50,3))
        self.assertIn(('deleteItems',{'i':['%024x'%1]}),notices)
        self.assertEqual(notices[-1],('replyMemoryCrystalExchangeSuipian',{'ii':[[4253,5]],'sp':50}))
        self.assertEqual(self.state['gacha']['items'][0]['w'],5)
    def test_duplicate_rows_aggregate_without_overdraft(self):
        result,_,_,_=self.run_exchange('memoryCrystalExchangeSuipian',{'ii':[[4253,2],[4253,3]]})
        self.assertEqual(result['gacha']['items'][0]['w'],50)
        with self.assertRaises(ValueError):self.run_exchange('memoryCrystalExchangeSuipian',{'ii':[[4253,3],[4253,3]]})
    def test_invalid_or_locked_or_unknown_items_never_mutate(self):
        for args in [{'ii':[[4253,0]]},{'ii':[[4253,-1]]},{'ii':[[4253,True]]},{'ii':[[24,1]]},{'ii':[[4253,6]]},{'ii':[[4253,1]],'extra':1}]:
            old=copy.deepcopy(self.state)
            with self.assertRaises(ValueError):self.run_exchange('memoryCrystalExchangeSuipian',args)
            self.assertEqual(old,self.state)
        self.state['gacha']['items'][0]['lo']='equipped'
        with self.assertRaises(ValueError):self.run_exchange('memoryCrystalExchangeSuipian',{'ii':[[4253,1]]})
    def test_receipt_replay_restart_and_argument_conflict(self):
        import json
        first,_,_,_=self.run_exchange('memoryCrystalExchangeSuipian',{'ii':[[4253,1]]})
        disk=json.loads(json.dumps(first));again,notices,changed,diag=self.run_exchange('memoryCrystalExchangeSuipian',{'ii':[[4253,1]]},disk)
        self.assertEqual(again,disk);self.assertEqual(notices,[]);self.assertFalse(changed);self.assertTrue(diag['replay'])
        with self.assertRaises(ValueError):self.run_exchange('memoryCrystalExchangeSuipian',{'ii':[[4253,2]]},disk)
    def test_stack_merge_and_split_exact_original_wrap(self):
        self.state['gacha']['items'].append(dict(self.state['gacha']['items'][0],u='%024x'%2,i=24,w=59999))
        result,_,_,_=self.run_exchange('memoryCrystalExchangeSuipian',{'ii':[[4253,1]]})
        self.assertEqual([i['w']for i in result['gacha']['items']if i['i']==24],[60000,9])
    def test_original_yuanbao_ratio_cost_and_overflow(self):
        result,notices,_,_=self.run_exchange('yuanbaoExchangeCrystal',{'yn':7})
        self.assertEqual(result['profile']['economy']['yuanbao'],99993);self.assertEqual(result['profile']['economy']['crystal'],100070)
        self.assertEqual(notices[-1],('yuanbaoExchangeCrystalReply',{'yn':7,'cn':70}))
        self.state['profile']['economy']['crystal']=2147483647
        with self.assertRaises(ValueError):self.run_exchange('yuanbaoExchangeCrystal',{'yn':1})
    def test_summon_original_limits_bound_first_and_day_week_reset(self):
        state=self.state
        for i in range(5):state,_,_,_=self.run_exchange('summoncoinExchange',{'i':4},state,'buy%d'%i)
        self.assertEqual(state['profile']['economy']['summoncoin'],35)
        self.assertEqual(state['profile']['economy']['bind_crystal'],0)
        self.assertEqual(item_exchange_limits(state,self.clock)['swl'],[(4,5)])
        with self.assertRaises(ValueError):self.run_exchange('summoncoinExchange',{'i':4},state,'six')
        state['story']['day']=1
        with self.assertRaises(ValueError):self.run_exchange('summoncoinExchange',{'i':4},state,'nextday')
        state['story']['week']=1
        with self.assertRaises(ValueError):self.run_exchange('summoncoinExchange',{'i':4},state,'storyweek')
        self.clock+=7*86400
        state,_,_,_=self.run_exchange('summoncoinExchange',{'i':4},state,'nextweek')
        self.assertEqual(item_exchange_limits(state,self.clock)['swl'],[(4,1)])
    def test_summon_diamond_real_cost_and_invalid_index(self):
        result,_,_,_=self.run_exchange('summoncoinExchange',{'i':3})
        self.assertEqual(result['profile']['economy']['yuanbao'],99720);self.assertEqual(result['profile']['economy']['summoncoin'],7)
        with self.assertRaises(ValueError):self.run_exchange('summoncoinExchange',{'i':9999})

if __name__=='__main__':unittest.main()
