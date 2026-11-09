"""Original predicate contracts plus canonical offline fact producers."""
import copy
import hashlib
import json
from pathlib import Path
import sys
import unittest
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'runtime'));sys.path.insert(0,str(ROOT/'tools'))
from export_game_catalogs import decode
from offline_conditions import evaluate_offline_condition as cond, evaluate_offline_trigger as trigger, parse_original_condition_literal


class OriginalConditionTests(unittest.TestCase):
    def setUp(self):
        self.fixture=json.loads((ROOT/'tests/fixtures/offline_conditions_cdata.json').read_text())
        self.schema=decode(self.fixture['schema'])
        self.state={'story':{'version':1,'week':2,'date':0,'route':'8-1','emergency':False,
                            'city_values':{'av':18,'bf':200,'fv':30,'rv':90,'dv':210,'cc':100},
                            'city_areas':{'1':{'id':1,'lv':3,'st':[0,False,False],'bd':{'1':{'id':21}}},
                                          '2':{'id':2,'lv':1,'st':[1,False,False],'bd':{}}},
                            'battle_wins':[101,1101], 'blackcores':{'1':1,'2':1,'3':2},
                            'cgs':[11,13], 'banned_heroes':{}, 'conquered_heroes':[]},
                    'profile':{'heroes':{'24':{'ef':100,'cf':15,'fd':True,'ar':{'oa':{1:99}},'ti':{'items':[{'u':'equipped'}]}},
                                         '8':{'ef':55,'cf':90,'cfd':True,'ti':{'items':[]}},
                                         '7':{'ef':0,'cf':100,'ti':{'items':[]}}},
                               'economy':{'level':12,'money':40000},
                               'treasures':{'items':[{'u':'equipped','i':1200,'w':1,'tr':{'cl':3}},
                                                     {'u':'free','i':1200,'w':1,'tr':{'cl':3}},
                                                     {'u':'other','i':1095,'w':1,'tr':{'cl':2}}]}},
                    'gacha':{'items':[{'u':'quest','i':3734,'w':1}]},
                    'completed_events':[8,510],'processing_events':[999],
                    'conditions':[[100,'5:1'],[102,4]],
                    'day':{'stock_day':3,'actions_spent':6},
                    'city_actions':{'patrol':None}}

    def test_original_source_hashes_and_all56_schema_classes(self):
        for path,digest in self.fixture['sha256'].items():
            self.assertEqual(hashlib.sha256((ROOT/path).read_bytes()).hexdigest(),digest)
        self.assertEqual(len(self.schema),56)
        import offline_conditions as module
        self.assertEqual(set(self.schema),module._OC_KINDS)
        self.assertEqual(self.schema[102],'AllSetCondition')
        self.assertEqual(self.schema[18],'AnySetInSetDictCondition')
        self.assertEqual(self.schema[22],'ReversedThresholdDictCondition')
        self.assertEqual(self.schema[100],'AnySetCondition')
        self.assertEqual(self.schema[54],'IntervalCondition')

    def test_safe_literal_parser_supports_real_native_sets_tuples_strings_and_dicts(self):
        self.assertEqual(parse_original_condition_literal('set([(1095,2)])'),{(1095,2)})
        self.assertEqual(parse_original_condition_literal("set(['8','8-1'])"),{'8','8-1'})
        self.assertEqual(parse_original_condition_literal('{1:(0,),2:(1,2)}'),{1:(0,),2:(1,2)})
        self.assertEqual(parse_original_condition_literal('set()'),set())
        self.assertEqual(parse_original_condition_literal({1:(0,)}),{1:(0,)})
        for text in ("__import__('os').system('bad')",'set([x for x in [1]])','{1:lambda:1}', '['*15+'1'+']'*15,'1'*9000):
            with self.assertRaises(ValueError):parse_original_condition_literal(text)
        source=(ROOT/'runtime/offline_conditions.py').read_text()
        self.assertNotIn('import ast',source)
        self.assertNotIn('eval(',source)

    def test_original_interval_inclusivity_open_bounds_and_independent_date(self):
        self.assertTrue(cond(4,'[0,0]',self.state)) # actualconditiondate0, NOT stockday3
        self.assertFalse(cond(4,'(0,1]',self.state))
        self.assertTrue(cond(16,'[1,)',self.state))
        self.assertTrue(cond(16,'(,3)',self.state))
        self.assertFalse(cond(16,'[3,)',self.state))
        self.assertTrue(cond(26,'[30,30]',self.state))
        self.assertFalse(cond(26,'(30,99)',self.state))
        self.assertIsNone(cond(26,'[99,30]',self.state))
        self.assertFalse(cond(7,'6000',self.state))
        self.assertTrue(cond(26,[30,30],self.state))
        self.assertFalse(cond(26,(30,30),self.state))

    def test_predecessors_and_mutex_use_current_week_facts_not_archived_history(self):
        self.state['week_protocol']={'history':[{'completed_events':[123]}]}
        self.assertTrue(cond(1,'set([8,510])',self.state))
        self.assertFalse(cond(1,'set([123])',self.state))
        self.assertTrue(cond(17,'set([8,123])',self.state))
        self.assertFalse(cond(11,'set([999])',self.state))
        self.assertTrue(cond(9,{101,1101},self.state))
        self.assertFalse(cond(9,{1102},self.state))

    def test_clientop_is_all_subset_and_click_is_exact_scalar(self):
        self.assertFalse(cond(102,'set([2,4])',self.state))
        self.assertTrue(cond(102,'set([4])',self.state))
        self.state['conditions']=[[102,[2,4]],[100,'5:1']]
        self.assertTrue(cond(102,{2,4},self.state))
        self.assertTrue(cond(100,"set(['5:1'])",self.state))
        self.assertFalse(cond(100,"set(['3:1','4:1'])",self.state))
        self.assertTrue(cond(100,{'3:1','4:1'},self.state,{'click_area':'4:1'}))
        self.state['conditions']=[]
        self.assertFalse(cond(100,{'5:1'},self.state))
        self.assertFalse(cond(102,{4},self.state))

    def test_area_any_and_all_are_distinct_and_absent_area_is_native_fall(self):
        self.assertTrue(cond(8,'{1:(0,),2:(0,)}',self.state))
        self.assertFalse(cond(47,'{1:(0,),2:(0,)}',self.state))
        self.assertTrue(cond(8,'{6:(2,)}',self.state))
        self.assertFalse(cond(8,'{6:(2,)}',self.state,{'condition_values':{8:{}}}))
        self.assertTrue(cond(18,'{1:(21,),2:(24,)}',self.state))
        self.assertFalse(cond(18,'{1:(24,),2:(21,)}',self.state))
        self.assertTrue(cond(22,'{1:3}',self.state))
        self.assertFalse(cond(22,'{1:4}',self.state))

    def test_patrol_uses_actual_team_context_and_native_ability_sums(self):
        patrol={'area':1,'heroes':[24,8]}
        context={'patrol':patrol,'abilities':{'24':{'insight':7,'construct':6,'leadership':6},
                                               '8':{'insight':4,'construct':7,'leadership':4}}}
        self.assertTrue(cond(3,{1},self.state,context))
        self.assertFalse(cond(3,{2},self.state,context))
        self.assertTrue(cond(10,{24,8},self.state,context))
        self.assertFalse(cond(10,{7},self.state,context)) #owned7 is NOT chosen
        self.assertTrue(cond(29,{21},self.state,context))
        self.assertTrue(cond(38,'11',self.state,context))
        self.assertFalse(cond(38,'12',self.state,context))
        self.assertTrue(cond(39,13,self.state,context))
        self.assertTrue(cond(40,10,self.state,context))
        self.assertIsNone(cond(38,10,self.state,{'patrol':patrol}))
        self.assertFalse(cond(3,{1},self.state))

    def test_items_minmax_and_actual_hero_friendship_fatigue_and_artifact(self):
        self.assertTrue(cond(5,'{3734:(1,1)}',self.state))
        self.assertFalse(cond(5,'{3734:(2,8)}',self.state))
        self.assertTrue(cond(5,'{9999:(0,0)}',self.state))
        self.assertTrue(cond(6,'{24:(100,100),8:(50,100)}',self.state))
        self.assertFalse(cond(6,'{7:(1,100)}',self.state))
        self.assertTrue(cond(37,'{24:(0,15)}',self.state))
        self.assertFalse(cond(32,'{24:1}',self.state)) #ar.oa attrs do NOT imply artifactopen
        self.state['profile']['heroes']['24']['oa']=True
        self.assertTrue(cond(32,'{24:1}',self.state))
        self.assertIsNone(cond(31,'{24:(20,999999)}',self.state))
        self.assertTrue(cond(31,'{24:(20,999999)}',self.state,{'condition_values':{31:{24:21}}}))

    def test_blackcore_minmax_counts_camps_and_cg_all_vs_any(self):
        self.assertTrue(cond(23,'{1:(2,8)}',self.state))
        self.assertFalse(cond(23,'{2:(0,0)}',self.state))
        self.assertTrue(cond(23,'{3:(0,0)}',self.state))
        self.assertTrue(cond(42,{11,13},self.state))
        self.assertFalse(cond(42,{11,12},self.state))
        self.assertTrue(cond(48,{11,12},self.state))

    def test_treasure_pair_classes_respect_equip_vs_unequip_even_same_template(self):
        self.assertTrue(cond(34,'set([(1200,3)])',self.state))
        self.assertTrue(cond(35,'set([(1200,3)])',self.state))
        self.assertTrue(cond(36,{(1200,3),(1095,2)},self.state))
        self.assertTrue(cond(41,{(1200,4),(1095,2)},self.state))
        self.assertFalse(cond(34,{(1095,2)},self.state))
        self.assertIsNone(cond(43,{(24,1)},self.state)) #ownedhero != ownedmemorypiece
        self.assertTrue(cond(43,{(24,1)},self.state,{'hero_files':{(24,1)}}))
        self.assertTrue(cond(44,{(7,1)},self.state,{'hero_files':{(24,1)}}))

    def test_ledger_conditions_require_actual_observed_transactions_and_completion(self):
        self.assertTrue(cond(12,'6',self.state))
        self.assertFalse(cond(12,'7',self.state))
        self.state['story'].update(week_actions_spent=12,event_action_baselines={'510':4},
                                  event_days={'510':{'week':2,'day':0}})
        self.assertTrue(cond(19,'{510:(3,3)}',self.state))
        self.assertTrue(cond(20,'{510:8}',self.state))
        self.assertFalse(cond(20,'{510:9}',self.state))
        self.assertIsNone(cond(20,'{510:8.5}',self.state)) #malformed threshold
        self.assertFalse(cond(19,'{123:(0,7)}',self.state))
        self.assertIsNone(cond(19,'{8:(0,7)}',self.state)) #legacycompleted8 lacks observedday
        self.state['story']['event_days']['510']['week']=1
        self.assertFalse(cond(19,'{510:(0,7)}',self.state))
        self.state['day'].pop('actions_spent')
        self.assertIsNone(cond(12,'6',self.state)) #never guess24-av

    def test_route_scalars_need_real_values_not_inferred_inventory_or_owned_heroes(self):
        self.assertTrue(cond(52,{'8','8-1'},self.state))
        self.assertFalse(cond(52,{'8'},self.state))
        self.state['gacha']['items'].append({'u':'not-universal','i':13624,'w':999})
        self.assertIsNone(cond(54,'[300,99999]',self.state))
        self.assertTrue(cond(54,'[300,99999]',self.state,{'general_value':300}))
        self.state['story']['general_value']=49
        self.assertTrue(cond(54,'[0,49]',self.state))
        self.assertFalse(cond(54,'[50,99999]',self.state))
        self.state['story'].update(yisake_value=70,baiyu_value=50)
        self.assertTrue(cond(53,'[70,)',self.state))
        self.assertTrue(cond(51,'[0,50]',self.state))
        self.assertTrue(cond(26,'[30,)',self.state))
        self.assertTrue(cond(27,'[90,90]',self.state))
        self.assertTrue(cond(28,'[200,300]',self.state))
        self.assertTrue(cond(33,'40000',self.state))

    def test_character_counts_are_current_facts_and_do_not_count_permanent_fd_as_new_clear(self):
        self.assertTrue(cond(46,'[2,2]',self.state))
        self.assertTrue(cond(49,'[1,1]',self.state))
        self.assertTrue(cond(50,'[1,1]',self.state)) #cfd8 only; permanentfd24 notnewclear
        self.state['story']['conquered_heroes']=[8,24]
        self.assertTrue(cond(50,'[2,2]',self.state))
        self.state['story']['banned_heroes']={'7':True,'8':True}
        self.assertTrue(cond(45,'[0,0]',self.state)) #ban list is not the huohaihua flag
        self.state['profile']['heroes']['24']['hhh']=True
        self.state['profile']['heroes']['8']['hhh']=True
        self.assertTrue(cond(45,'[2,2]',self.state))
        self.assertFalse(cond(45,'[3,)',self.state))
        self.state['profile']['heroes']['7']['hhh']='yes'
        self.assertIsNone(cond(45,'[2,2]',self.state)) #malformed flag is unknown
        self.state['profile']['heroes']['7']['hhh']=False
        self.assertIsNone(cond(45,'[x,1)',self.state)) #malformed interval
        self.assertTrue(cond(24,{7,8,24},self.state))
        self.assertFalse(cond(25,{7},self.state))
        self.state['story']['starter_hero']=24
        self.assertFalse(cond(24,{7},self.state,{'selected_starter_only':True}))

    def test_hero_star_uses_original_star_level_order_encoding(self):
        heroes=self.state['profile']['heroes']
        heroes['24'].update(sl=4,so=4)
        self.assertTrue(cond(31,'{24:(20,999999)}',self.state)) #4*4+4==20
        self.assertFalse(cond(31,'{24:(5,19)}',self.state))
        heroes['24']['so']=3
        self.assertTrue(cond(31,'{24:(19,19)}',self.state))
        self.assertFalse(cond(31,'{24:(20,999999)}',self.state))
        self.assertFalse(cond(31,'{999:(5,20)}',self.state)) #unowned hero is known false
        heroes['24']['sl']='4'
        self.assertIsNone(cond(31,'{24:(19,19)}',self.state)) #malformed star level
        heroes['24']['sl']=4
        self.assertTrue(cond(31,'{24:(19,19)}',self.state,{'condition_values':{31:{24:19}}}))
        self.assertFalse(cond(31,'{24:(19,19)}',self.state,{'condition_values':{31:{24:18}}}))

    def test_friendly_and_fatigue_counts_fail_closed_on_malformed_hero_values(self):
        heroes=self.state['profile']['heroes']
        self.assertTrue(cond(46,'[2,2]',self.state))
        self.assertTrue(cond(49,'[1,1]',self.state))
        heroes['24']['ef']='100'
        self.assertIsNone(cond(46,'[2,2]',self.state))
        heroes['24']['ef']=100
        heroes['7']['cf']=None
        self.assertIsNone(cond(49,'[1,1]',self.state))
        heroes['7']['cf']=100
        self.assertFalse(cond(46,'[3,3]',self.state))
        self.assertFalse(cond(49,'[2,2]',self.state))

    def test_three_state_row_false_shortcuts_unrelated_unknown_without_mutation(self):
        before=copy.deepcopy(self.state)
        row={'release':True,'conds':{999:'unknown',52:"set(['other'])",54:'[1,)'}}
        self.assertFalse(trigger(row,self.state))
        row['conds'][52]="set(['8-1'])"
        self.assertIsNone(trigger(row,self.state))
        self.state['story']['general_value']=2
        row['conds'].pop(999)
        self.assertTrue(trigger(row,self.state))
        self.state['story'].pop('general_value')
        self.assertEqual(self.state,before)
        self.assertIsNone(cond(999,None,self.state))
        self.assertTrue(cond(1,None,self.state))
        self.assertFalse(trigger({'release':False,'conds':{999:'unknown'}},self.state))

    def test_native_literal_and_original_string_forms_agree_and_embedded_namespace_works(self):
        source=(ROOT/'runtime/offline_conditions.py').read_text()
        scope={'__name__':'embedded_original_conditions'}
        exec(compile(source,'offline_conditions.py','exec'),scope)
        for kind,string,native in [(1,'set([8,510])',{8,510}),(8,'{1:(0,)}',{1:(0,)}),
                                   (6,'{24:(100,100)}',{24:(100,100)}),(102,'set([2,4])',{2,4})]:
            self.assertEqual(cond(kind,string,self.state),cond(kind,native,self.state))
            self.assertEqual(cond(kind,string,self.state),scope['evaluate_offline_condition'](kind,native,self.state))


    def test_original_empty_set_and_dict_predicates_have_mathematical_results(self):
        for kind in (1,9,10,24,34,35,36,42,43,102,11,25,44):
            self.assertTrue(cond(kind,set(),{}),kind)
        for kind in (17,29,41,48,3,52,100):
            self.assertFalse(cond(kind,set(),{}),kind)
        for kind in (5,6,19,23,31,37,20,22,32,47):
            self.assertTrue(cond(kind,{},{}),kind)
        for kind in (8,18):
            self.assertFalse(cond(kind,{},{}),kind)


if __name__=='__main__':unittest.main()
