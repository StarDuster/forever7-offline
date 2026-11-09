import copy
import json
from pathlib import Path
import sys
import unittest
ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT/'runtime'), str(ROOT/'tools'), str(ROOT/'analysis/research-agent')]
from read_data_table import read as read_source
from read_literal_marshal import read as read_marshal
from offline_event_effects import plan_event_effects, classify_event_effects, apply_event_effects_snapshot


def original_tables():
    base=ROOT/'analysis/android640-scripts/com/data/cdata'
    tables={name:read_marshal(base/(name+'.marshal')) for name in
            ('city_data','mission','cg_data','item_data','hero_treasure','hero','skin',
             'private_msg','social_msg','story_clue_info','city_building','city_development')}
    tables.update({name:read_source(ROOT/'analysis/decompiled'/(name+'.py')) for name in
                   ('reward_common','notepad')})
    tables['attr_indices']=json.loads((ROOT/'tests/fixtures/combat-attribute-indices.json').read_text())['indices']
    return tables


def evidence_context(event, row):
    tokens=['%s:%s'%(kind,event) for kind in ('ui','puzzle','movie','caidan','activity','route','ending')]
    for field in ('enterBattle','contentFinishBattle'):
        values=row.get(field,())
        if isinstance(values,int):values=[values]
        tokens.extend('battle:%s'%i for i in values)
    return {'completed_callbacks':tokens}


def base_state(tables):
    hero_rows={str(h):{'ef':0,'cf':100,'sk':{},'ti':{'items':[],'mc':25}} for h in tables['hero']}
    for i,r in tables['skin'].items():
        hero_rows[str(r['hero'])]['sk']['%024x'%i]={'i':i,'u':'%024x'%i}
    item_ids=set(i for r in tables['reward_common'].values() for i in r.get('items',()))
    return {'completed_events':[], 'processing_events':[], 'available_events':[],
        'story':{'notes':{'p':{},'n':{},'pn':[],'ppn':False},'city_areas':{},'blackcores':{},'battle_wins':[]},
        'profile':{'heroes':hero_rows,'economy':{'version':1,'money':1000000,'exp':0,'level':1},
                   'treasures':{'version':1,'items':[]}},
        'gacha':{'items':[{'i':i,'u':'%024x'%(100000+i),'w':1000} for i in sorted(item_ids)]}}

class EventEffectsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tables=original_tables()
        cls.content=read_source(ROOT/'analysis/decompiled/event_content.py')
        cls.base=base_state(cls.tables)
    def setUp(self):self.state=copy.deepcopy(self.base)
    def run_event(self,e,context=None,state=None):
        return plan_event_effects(state or self.state,e,self.content,self.tables,
            context if context is not None else evidence_context(e,self.content[e]))
    def test_all_original_exclamation_rows_apply_real_counter_deltas_and_snapshot(self):
        rows = [(event, row) for event, row in self.content.items() if row.get('exclam')]
        self.assertEqual(len(rows), 94)
        for event, row in rows:
            with self.subTest(event=event):
                planned, notices, diagnostic = self.run_event(event)
                self.assertTrue(diagnostic['ready'], diagnostic)
                for operation, specification in row['exclam'].items():
                    entries = [specification] if len(specification) == 2 and type(specification[0]) is int else specification
                    for aid, delta in entries:
                        targets = sorted(self.tables['city_data']) if aid == 0 else [aid]
                        for target in targets:
                            self.assertEqual(planned['story']['city_op_exclam'][str(target)][operation], delta)
                snapshot = apply_event_effects_snapshot(planned, {'city':{'coe':{'stale':{}}}})
                self.assertEqual(snapshot['city']['coe'], planned['story']['city_op_exclam'])
                self.assertIn(('syncOpExclam', {'d':planned['story']['city_op_exclam']}), notices)
                again, notices, diagnostic = self.run_event(event, state=planned)
                self.assertEqual(again, planned)
                self.assertEqual(notices, [])

    def test_original_exclamation_pair_adds_then_removes_patrol_marker(self):
        first, _, diagnostic = self.run_event(50036)
        self.assertTrue(diagnostic['ready'], diagnostic)
        self.assertEqual(first['story']['city_op_exclam']['6']['patrol'], 1)
        second, _, diagnostic = self.run_event(50038, state=first)
        self.assertTrue(diagnostic['ready'], diagnostic)
        self.assertEqual(second['story']['city_op_exclam']['6']['patrol'], 0)

    def test_original_mission_reset_reopens_chain_without_erasing_history_or_granting_wins(self):
        from offline_stage import prepare_stage_admission, prepare_stage_finish
        self.state['story'].update(week=0, date=0, emergency=False,
            battle_wins=[22004,22005,22006,777], city_values={'av':24,'fv':80,'rv':0,'dv':0,'bf':0})
        self.state['day'] = {'stock_day':0}
        self.state['battle'] = {'version':1,'active':None,'receipts':[]}
        planned, notices, diagnostic = self.run_event(5050)
        self.assertTrue(diagnostic['ready'], diagnostic)
        self.assertEqual(planned['story']['battle_wins'], [22004,22005,22006,777])
        self.assertEqual(planned['story']['current_mission_wins'], [777])
        self.assertEqual(planned['story']['city_areas']['3']['stage']['cs'], 22004)
        self.assertIn(('refreshClientMission', {}), notices)
        planned['completed_events'].append(5050)  # normal caller commit boundary
        before = copy.deepcopy(planned)
        with self.assertRaises(ValueError):
            prepare_stage_admission(planned, {'t':1,'s':22005,'h':[24],'d':{'a':3}}, self.tables['mission'], lambda:'locked')
        self.assertEqual(planned, before)
        active, changed = prepare_stage_admission(planned, {'t':1,'s':22004,'h':[24],'d':{'a':3}}, self.tables['mission'], lambda:'actual-host-fight')
        self.assertTrue(changed)
        def settle(admission, actual):
            return dict(actual, r={} if not actual['w'] else {'money':1}), {'profile':copy.deepcopy(active['profile']), 'notices':[], 'granted':[]}
        lost, reply, effects, changed = prepare_stage_finish(active, {'t':1,'s':22004,'h':[24],'x':[],'w':0}, self.tables['mission'], self.tables['city_data'], settle, 'actual-host-fight')
        self.assertEqual(lost['story'], active['story'])
        won, reply, effects, changed = prepare_stage_finish(active, {'t':1,'s':22004,'h':[24],'x':[],'w':1}, self.tables['mission'], self.tables['city_data'], settle, 'actual-host-fight')
        self.assertEqual(won['story']['city_areas']['3']['stage']['cs'], 22005)
        self.assertNotIn(22005, won['story']['current_mission_wins'])
        self.assertNotIn(22006, won['story']['current_mission_wins'])
        self.assertEqual(won['story']['city_areas']['3']['st'][0], 1)
        self.assertEqual(won['story']['battle_wins'], [777,22004,22005,22006])
        self.assertEqual(won['story']['city_values']['av'], 22)

    def test_original_reset_family_requires_three_separate_actual_result_transactions(self):
        from offline_stage import prepare_stage_admission, prepare_stage_finish
        self.state['story'].update(week=0,date=0,emergency=False,
            city_values={'av':24,'fv':80,'rv':0,'dv':0,'bf':0})
        self.state['day'] = {'stock_day':0}
        self.state['battle'] = {'version':1,'active':None,'receipts':[]}
        state, notices, diagnostic = self.run_event(5050)
        self.assertTrue(diagnostic['ready'], diagnostic)
        state['completed_events'].append(5050)
        for index, scene in enumerate((22004,22005,22006)):
            with self.subTest(scene=scene):
                fight = 'host-actual-source-%s'%scene
                active, changed = prepare_stage_admission(state, {'t':1,'s':scene,'h':[24],'d':{'a':3}}, self.tables['mission'], lambda:fight)
                def settle(admission, actual):
                    return dict(actual,r={'money':1}), {'profile':copy.deepcopy(state['profile']), 'notices':[], 'granted':[]}
                parameters = {'t':1,'s':scene,'h':[24],'x':[],'w':1}
                state, reply, effects, changed = prepare_stage_finish(active, parameters, self.tables['mission'], self.tables['city_data'], settle, fight)
                self.assertTrue(changed)
                self.assertEqual(state['story']['current_mission_wins'], [22004,22005,22006][:index+1])
                self.assertEqual(state['story']['city_areas']['3']['st'][0], 0 if index == 2 else 1)
                replay, reply, effects, changed = prepare_stage_finish(state, parameters, self.tables['mission'], self.tables['city_data'], settle, fight)
                self.assertFalse(changed)
                self.assertEqual(replay,state)
        self.assertEqual(state['story']['city_values']['av'],18)
        self.assertEqual(len(state['battle']['receipts']),3)
        self.assertEqual(state['story']['city_areas']['3']['stage']['cs'],0)
        self.assertNotIn(30041,state['completed_events'])

    def test_mission_reset_during_active_fight_never_changes_progress_or_rewards(self):
        self.state['battle'] = {'active':{'fight_id':'actual-in-progress'}}
        planned, notices, diagnostic = self.run_event(5050)
        self.assertFalse(diagnostic['ready'], diagnostic)
        self.assertIn('active fight', diagnostic['reason'])
        self.assertEqual(planned,self.state)
        self.assertEqual(notices,[])

    def test_original_ark_refresh_uses_released_mission_and_real_source_condition(self):
        planned, notices, diagnostic = self.run_event(6012)
        self.assertTrue(diagnostic['ready'], diagnostic)
        self.assertEqual(planned['story']['city_areas']['4']['st'][0], 5)
        self.assertEqual(planned['story']['city_areas']['4']['stage']['cs'], 155)
        self.assertEqual(planned['story']['battle_wins'], [])
        self.assertIn(('refreshClientMission', {}), notices)

    def test_native_observed_autostart_notebooks_finish_once_and_leave_availability(self):
        from offline_story_engine import prepare_story_operation, begin_story_occurrence, refresh_story_events
        triggers = read_source(ROOT/'analysis/decompiled/event_condition.py')
        triggers = {event:triggers[event] for event in (1013254, 1005835)}
        for event in (1013254, 1005835):
            with self.subTest(event=event):
                state = copy.deepcopy(self.base)
                state['story'].update(week=0, date=0, route='1')
                state.update(conditions=[], event_traces=[])
                state['processing_events'] = [event]
                begin_story_occurrence(state, event)
                planned, notices = prepare_story_operation(state, 'start', {'e':event}, self.content, triggers, self.tables)
                self.assertIn(event, planned['completed_events'])
                self.assertNotIn(event, planned['processing_events'])
                self.assertNotIn(event, dict(planned['available_events']))
                self.assertIn(('completeEventReplyEnd', {'e':event}), notices)
                if event == 1005835:
                    self.assertEqual(planned['story']['notes']['n']['49'], [14901])
                refresh_story_events(planned, triggers, self.content)
                self.assertNotIn(event, dict(planned['available_events']))
                with self.assertRaises(ValueError):
                    prepare_story_operation(planned, 'start', {'e':event}, self.content, triggers, self.tables)

    def test_all_original_removal_rows_change_only_real_target_buildings(self):
        rows = [(e, r) for e, r in self.content.items() if r.get('destroyPatrolBuild') or r.get('destroyAreaPatrolBuild')]
        self.assertEqual(len(rows), 18)
        for event, row in rows:
            with self.subTest(event=event):
                state = copy.deepcopy(self.base)
                pairs = list(row.get('destroyAreaPatrolBuild', ()))
                if row.get('destroyPatrolBuild'):
                    pairs += [(1, bid) for bid in row['destroyPatrolBuild']]
                    state['city_actions'] = {'patrol':{'area':1, 'selected':event, 'events':[event]}}
                for aid, bid in pairs:
                    state['story']['city_areas'][str(aid)] = {'id':aid, 'lv':1, 'st':[0,False,False],
                        'bd':{'1':{'id':bid,'uuid':'a'*24},'2':{'id':1,'uuid':'b'*24}}}
                planned, notices, diagnostic = self.run_event(event, state=state)
                if event == 31:
                    # Unreleased selector0 row has no actual winning EVENT
                    # provenance and remains atomically pending.
                    self.assertFalse(diagnostic['ready'], diagnostic)
                    self.assertIn('missing-winning-party-provenance', diagnostic['reason'])
                    self.assertEqual(planned, state)
                    self.assertEqual(notices, [])
                    continue
                self.assertTrue(diagnostic['ready'], diagnostic)
                for aid, bid in pairs:
                    area = planned['story']['city_areas'][str(aid)]
                    self.assertNotIn('1', area['bd'])
                    self.assertEqual(area['bd']['2'], {'id':1,'uuid':'b'*24})
                    self.assertEqual(area['dbd']['1'], bid)
                    self.assertIn(('area_building_destroy', {'aid':aid,'bid':bid}), notices)
                self.assertEqual(planned.get('completed_events'), state['completed_events'])
                self.assertEqual(planned['story']['battle_wins'], state['story']['battle_wins'])

    def test_patrol_removal_without_actual_selected_context_is_atomic(self):
        planned, notices, diagnostic = self.run_event(7527)
        self.assertFalse(diagnostic['ready'], diagnostic)
        self.assertEqual(planned, self.state)
        self.assertEqual(notices, [])

    def test_original_event_building_preserves_occupied_slots_and_replays_once(self):
        self.state['story']['city_areas']['3'] = {'id':3, 'st':[0,False,False],
            'lv':1, 'bd':{'1':{'id':1,'uuid':'a'*24}}, 'dbd':{'2':34}}
        planned, notices, diagnostic = self.run_event(2067)
        self.assertTrue(diagnostic['ready'], diagnostic)
        area = planned['story']['city_areas']['3']
        self.assertEqual(area['bd']['1'], self.state['story']['city_areas']['3']['bd']['1'])
        self.assertEqual(area['bd']['2']['id'], 34)
        self.assertEqual(len(area['bd']['2']['uuid']), 24)
        self.assertNotIn('2', area['dbd'])
        again, notices, diagnostic = self.run_event(2067, state=planned)
        self.assertEqual(again, planned)
        self.assertEqual(notices, [])

    def test_all_original_building_effect_rows_insert_native_snapshots_and_capacity(self):
        for event in (471, 2067, 5314, 10000071, 6325):
            with self.subTest(event=event):
                state = copy.deepcopy(self.base)
                aid, (building, count) = next(iter(self.content[event]['buildBuilding'].items()))
                state['story']['city_areas'][str(aid)] = {'id':aid, 'st':[0,False,False],
                    'lv':1, 'bd':{}}
                planned, notices, diagnostic = self.run_event(event, state=state)
                self.assertTrue(diagnostic['ready'], diagnostic)
                values = list(planned['story']['city_areas'][str(aid)]['bd'].values())
                self.assertEqual([value['id'] for value in values], [building] * count)
                self.assertTrue(all(len(value['uuid']) == 24 for value in values))
                if event == 5314:
                    self.assertEqual(planned['story']['city_values']['rv'], 10)
                    self.assertEqual(planned['story']['city_areas'][str(aid)]['rv'], 10)

    def test_original_event_building_requires_real_free_developed_capacity(self):
        self.state['story']['city_areas']['3'] = {'id':3, 'st':[0,False,False],
            'lv':1, 'bd':{str(i):{'id':1,'uuid':'%024x'%i} for i in range(1,20)}}
        planned, notices, diagnostic = self.run_event(2067)
        self.assertFalse(diagnostic['ready'], diagnostic)
        self.assertEqual(planned, self.state)
        self.assertEqual(notices, [])

    def test_real_area_activation_uses_original_own_area_graph_root_and_preserves_progress(self):
        p,n,d=self.run_event(476)
        self.assertTrue(d['ready'],d)
        self.assertEqual(p['story']['city_areas']['2']['stage']['cs'],1101)
        self.assertEqual(p['story']['city_areas']['2']['st'][0],1)
        self.assertEqual(self.state['story']['city_areas'],{})
        p['story']['city_areas']['2']['stage']['cs']=1105
        p['story']['event_effect_receipts']={}
        q,_,d=self.run_event(476,state=p)
        self.assertEqual(q['story']['city_areas']['2']['stage']['cs'],1105)
    def test_real_fall_unlock_lock_and_blackcore_transfer(self):
        for e in (1078,1071):
            self.state,_,d=self.run_event(e)
            self.assertTrue(d['ready'],d)
        self.assertTrue(self.state['story']['city_areas']['2']['st'][2])
        self.state,_,d=self.run_event(1236)
        self.assertFalse(self.state['story']['city_areas']['2']['st'][2])
        self.assertEqual(self.state['story']['city_areas']['3']['st'][0],2)
        self.state['story']['blackcores']={'1':1,'2':2}
        p,n,d=self.run_event(7006)
        self.assertTrue(d['ready'],d)
        self.assertEqual(p['story']['blackcores'],{'1':2,'2':2})
        self.assertIn(('updateBlackCoreCamp',{'o':1,'n':2}),n)
    def test_real_notebook_generalizes_player_and_hero_journals(self):
        p,n,d=self.run_event(1000)
        self.assertTrue(d['ready'],d);self.assertIn(10044,p['story']['notes']['pn'])
        p,n,d=self.run_event(1015808)
        self.assertTrue(d['ready'],d)
        self.assertIn(111710,p['story']['notes']['n']['117'])
        self.assertIn(111710,p['story']['notes']['p']['117'])
    def test_real_cg_reward_and_friendship_then_replay_is_idempotent(self):
        p,n,d=self.run_event(35)
        self.assertTrue(d['ready'],d);self.assertTrue(p['story']['cgs'])
        again,n,d=self.run_event(35,state=p)
        self.assertEqual(p,again);self.assertFalse(n);self.assertEqual(d['status'],'already-applied')
        p,n,d=self.run_event(469)
        self.assertTrue(d['ready'],d)
        self.assertTrue(any(name=='updateFriendlyValue' for name,_ in n))
    def test_real_hero_ban_recovery_keeps_existing_outfit_equipment_fields(self):
        p,n,d=self.run_event(3275)
        self.assertTrue(d['ready'],d)
        self.assertEqual(p['profile']['heroes'],self.state['profile']['heroes'])
        self.assertIn('17',p['story']['banned_heroes'])
        q,n,d=self.run_event(3277,state=p)
        self.assertTrue(d['ready'],d);self.assertNotIn('17',q['story']['banned_heroes'])
    def test_real_route_and_ending_defer_until_committed_event_and_week_ui(self):
        p,n,d=self.run_event(510)
        self.assertTrue(d['ready'],d)
        self.assertNotIn('route',p['story'])
        self.assertEqual(d['deferred_handoffs'][0]['route'],'8-1')
        p,n,d=self.run_event(1431)
        self.assertTrue(d['ready'],d)
        self.assertNotIn('endings',p['story'])
        self.assertEqual(d['deferred_handoffs'][0]['result'],104)
        self.assertFalse(any(name=='showWeekResult' for name,_ in n))
    def test_real_ui_and_battle_require_actual_callbacks_not_empty_conditions(self):
        p,n,d=self.run_event(10000,context={})
        self.assertFalse(d['ready']);self.assertEqual(d['status'],'waiting')
        self.assertEqual(p,self.state);self.assertFalse(n)
        self.assertIn('ui:10000',[i['token'] for i in d['pending_callbacks']])
        p,n,d=self.run_event(1,context={})
        self.assertFalse(d['ready'])
        self.assertIn('battle:104',[i['token'] for i in d['pending_callbacks']])
    def test_unknown_effect_is_atomic_even_with_valid_notes_and_rewards(self):
        row=copy.deepcopy(self.content[35]);row['unconfirmedOfficialEffect']={1:9}
        p,n,d=plan_event_effects(self.state,35,{35:row},self.tables,{})
        self.assertFalse(d['ready']);self.assertEqual(p,self.state);self.assertFalse(n)
        self.assertEqual(d['unsupported_fields'],['unconfirmedOfficialEffect'])
    def test_late_invalid_reward_rolls_back_prior_notes_and_money(self):
        content={900:{'notepadId':(10044,),'rewards':(1,2)}}
        tables=dict(self.tables,reward_common={1:{'id':1,'money':50},2:{'id':2,'items':(1,),'itemsNum':(-999999,)}})
        p,n,d=plan_event_effects(self.state,900,content,tables,{})
        self.assertFalse(d['ready']);self.assertEqual(p,self.state);self.assertFalse(n)
    def test_real_item_cg_and_treasure_rewards_have_native_schema_and_stable_ids(self):
        p,n,d=self.run_event(206)
        self.assertTrue(d['ready'],d)
        self.assertTrue(p['profile']['treasures']['items'])
        for item in p['profile']['treasures']['items']:
            self.assertEqual(len(item['u']),24);self.assertTrue(item['tr']['attr'])
        again,_,d=self.run_event(206,state=p)
        self.assertEqual(p,again)
    def test_distinct_original_occurrences_reapply_without_reusing_receipt(self):
        c=evidence_context(469,self.content[469]);c['receipt_key']='week0:date0:469:1'
        p,_,d=self.run_event(469,c)
        c['receipt_key']='week1:date0:469:2';q,_,d=self.run_event(469,c,p)
        self.assertTrue(d['ready']);self.assertNotEqual(p['profile']['heroes'],q['profile']['heroes'])
    def test_real_clue_and_private_message_are_persistent_original_native_notices(self):
        p,n,d=self.run_event(1173)
        self.assertTrue(d['ready'],d);self.assertIn(50,p['story']['clues'])
        self.assertTrue(any(name=='syncClueInfo' for name,_ in n))
        p,n,d=self.run_event(420)
        self.assertTrue(d['ready'],d)
        self.assertIn('288',p['story']['social']['pm'])
        self.assertIn(('syncOnePrivateMsg',{'id':288,'c':p['story']['social']['pm']['288']}),n)
    def test_snapshot_projects_cgs_bans_notes_social_without_touching_permanent_hero_records(self):
        p,_,d=self.run_event(35)
        p['story'].update(banned_heroes={'17':200},cine_locked_heroes=[28],
            social={'pm':{'288':{'id':288,'rd':False,'rp':False,'rt':0}},'sm':{}})
        original={'heromgr':{'hrs':[(17,{'cs':'original'}) ,(28,{'cs':'other'})]},
                  'city':{},'sd':{'pm':{},'sm':{}}}
        snapshot=apply_event_effects_snapshot(p,original)
        self.assertEqual(snapshot['heromgr']['hrs'],[(28,{'cs':'other'})])
        self.assertEqual(snapshot['heromgr']['bhrs'],[(17,{'cs':'original'})])
        self.assertEqual(snapshot['heromgr']['c'],[28]);self.assertTrue(snapshot['cgs'])
        self.assertEqual(snapshot['sd']['pm']['288']['id'],288)
        self.assertEqual(len(original['heromgr']['hrs']),2)
    def test_canonical_empty_fields_clear_old_snapshot_week_locks_and_route_targets(self):
        state=copy.deepcopy(self.state)
        state['story'].update(cine_locked_heroes=[],route='new',route_targets={},
            banned_heroes={},cgs=[],new_cgs=[],social={'pm':{},'sm':{}},buildable_buildings=[])
        old={'heromgr':{'hrs':[(28,{})],'bhrs':[(17,{})],'c':[28]},
             'std':{'rt':'old','srt':[1,2]},'cgs':[1],'ccgs':[1],'ncgs':[1],
             'city':{'hb':[34]},'sd':{'pm':{'1':{}},'sm':{'1':{}}}}
        result=apply_event_effects_snapshot(state,old)
        self.assertEqual(result['heromgr']['c'],[]);self.assertEqual(result['heromgr']['bhrs'],[])
        self.assertEqual(result['std']['srt'],[]);self.assertEqual(result['cgs'],[])
        self.assertEqual(result['city']['hb'],[]);self.assertEqual(result['sd']['pm'],{})
    def test_absent_canonical_ban_field_preserves_existing_base_banned_heroes(self):
        old={'heromgr':{'hrs':[(28,{})],'bhrs':[(17,{})],'c':[28]}}
        result=apply_event_effects_snapshot(self.state,old)
        self.assertEqual(result['heromgr'],old['heromgr'])
    def test_account_proxy_without_profile_can_classify_metadata_but_not_grant_hero(self):
        state=dict(self.state,profile=None)
        p,n,d=plan_event_effects(state,8,self.content,self.tables,{})
        self.assertTrue(d['ready'],d)
        p,n,d=plan_event_effects(state,1001,self.content,self.tables,{})
        self.assertFalse(d['ready']);self.assertEqual(p,state)
    def test_historical_win_does_not_satisfy_a_fresh_enter_battle_occurrence(self):
        self.state['story']['battle_wins']=[104]
        p,n,d=self.run_event(1,context={})
        self.assertFalse(d['ready'])
        self.assertIn('battle:104',[v['token'] for v in d['pending_callbacks']])
        synthetic={900:{'contentFinishBattle':(104,)}}
        p,n,d=plan_event_effects(self.state,900,synthetic,self.tables,{})
        self.assertTrue(d['ready'],d)
    def test_embedded_shared_globals_needs_no_offline_module_import(self):
        namespace={}
        exec(compile((ROOT/'runtime/offline_event_effects.py').read_text(),'<embedded-effects>','exec'),namespace)
        p,n,d=namespace['plan_event_effects'](self.state,476,self.content,self.tables,{})
        self.assertTrue(d['ready'],d)
        self.assertEqual(self.state['story']['city_areas'],{})

if __name__=='__main__':unittest.main()
