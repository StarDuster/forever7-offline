"""Actual original161/7026 terminal recovery and durable source provenance."""
import copy
import json
from pathlib import Path
import sys
import unittest
ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT/'runtime'), str(ROOT/'tools'), str(ROOT/'analysis/research-agent'), str(ROOT/'tests')]
from test_offline_event_effects import original_tables, base_state
from read_data_table import read
from offline_event_battle import prepare_event_battle_gate, prepare_event_battle_admission, prepare_event_battle_finish
from offline_story_engine import begin_story_occurrence, prepare_story_operation
from offline_event_effects import plan_event_effects
from offline_battle_terminal import validate_event_terminal_state, WINNING_PARTY_FATIGUE_POLICY


class WinningPartyFatigueTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tables = original_tables()
        cls.events = read(ROOT/'analysis/decompiled/event_content.py')

    def state(self):
        state = base_state(self.tables)
        state['event_traces'] = []
        state['story'].update(week=0, date=0, route='1', city_values={'av':24,'fv':80,'rv':0,'dv':0,'bf':0,'ev':0})
        state['battle'] = {'version':1,'active':None,'receipts':[]}
        for hid, fatigue in ((24,7),(7,22),(8,15)):
            state['profile']['heroes'][str(hid)]['cf'] = fatigue
        return state

    def win(self, state=None, party=None, fight='actual-161', outcome=1):
        state = state or self.state()
        party = party or [24,7]
        state['processing_events'].append(7025)
        begin_story_occurrence(state,7025,self.events,{})
        key = '0:7025:%s' % state['story']['event_occurrences']['7025']
        state,_,_ = prepare_event_battle_gate(state,7025,self.events,key)
        args = {'t':2,'s':161,'h':party,'d':{}}
        state,_ = prepare_event_battle_admission(state,args,self.tables['mission'],self.events,lambda:fight)
        def settle(active, actual):
            reply = {k:copy.deepcopy(actual[k]) for k in ('t','s','h','x','w')}
            reply['r'] = {}
            return reply, {'profile':copy.deepcopy(state['profile']),'notices':[]}
        return prepare_event_battle_finish(state,dict(args,x=[party[0]],w=outcome,e=9),settle,fight,self.tables['mission'],self.events)[0]

    def start_terminal(self,state):
        state = copy.deepcopy(state)
        state['available_events'] = [entry for entry in state['available_events'] if entry[0] != 7026]
        state['processing_events'].append(7026)
        begin_story_occurrence(state,7026,self.events,{})
        return state

    def dialog(self,state,**extra):
        args = {'k':'dialog','d':{'c':7026}}
        args.update(extra)
        return prepare_story_operation(state,'trace',args,self.events,{},self.tables)

    def test_real_win_only_full_admitted_party_recovers_after_real_dialog_with_cg_blackcore(self):
        state = self.win()
        self.assertIn([7026,1],state['available_events'])
        self.assertEqual(state['profile']['heroes']['24']['cf'],7)
        proof = state['story']['event_terminal_offers']['7026']
        self.assertEqual(proof['party'],[24,7])
        self.assertEqual(proof['policy'],WINNING_PARTY_FATIGUE_POLICY)
        self.assertIsNone(state['battle']['active'])
        state = self.start_terminal(state)
        before = copy.deepcopy(state['profile']['heroes']['8'])
        done,notices = self.dialog(state)
        self.assertEqual([done['profile']['heroes'][str(h)]['cf'] for h in [24,7]], [100,100])
        self.assertEqual(done['profile']['heroes']['8'],before)
        self.assertIn(7026,done['completed_events'])
        self.assertIn(73,done['story']['cgs'])
        self.assertEqual(done['story']['blackcores'],{'3':1,'4':1})
        self.assertIn(('updateCurFatigueValue',{'h':24,'v':100}),notices)
        self.assertNotIn(0,[p['h'] for n,p in notices if n == 'updateCurFatigueValue'])
        audit = done['story']['event_terminal_effect_audit']['0:7026:1'][0]
        self.assertEqual([c['before'] for c in audit['changes']],[7,22])
        validate_event_terminal_state(done)

    def test_no_recovery_at_start_and_reload_idempotence(self):
        state = self.start_terminal(json.loads(json.dumps(self.win())))
        waiting,_ = prepare_story_operation(state,'start',{'e':7026},self.events,{},self.tables)
        self.assertEqual(waiting['profile'],state['profile'])
        done,_ = self.dialog(json.loads(json.dumps(waiting)))
        duplicate,notices = self.dialog(json.loads(json.dumps(done)))
        self.assertEqual(duplicate,done)
        self.assertEqual(notices,[])
        self.assertEqual(len(done['story']['event_terminal_effect_audit']['0:7026:1']),1)

    def test_pinned_party_survives_pruning_lineup_and_intervening_result(self):
        state = self.start_terminal(self.win())
        state['battle']['receipts'] = []
        state['profile']['lineup'] = [8]
        done,_ = self.dialog(json.loads(json.dumps(state)))
        self.assertEqual(done['profile']['heroes']['7']['cf'],100)
        self.assertEqual(done['profile']['heroes']['8']['cf'],15)

    def test_second_pending_offer_does_not_replace_first_party_or_origin(self):
        first = self.win()
        second = self.win(first,[8],'actual-second')
        self.assertEqual(second['story']['event_terminal_offers']['7026']['party'],[24,7])
        self.assertEqual(second['story']['available_origins']['7026']['fight_id'],'actual-161')
        done,_ = self.dialog(self.start_terminal(second))
        self.assertEqual(done['profile']['heroes']['8']['cf'],15)

    def test_loss_cannot_mint_winning_party(self):
        state = self.win(outcome=0)
        self.assertNotIn('7026',state['story'].get('event_terminal_offers',{}))
        self.assertNotIn([7026,1],state['available_events'])
        self.assertEqual(state['profile']['heroes']['24']['cf'],7)

    def test_missing_owned_or_corrupt_cf_rolls_back_all_reward_cg_blackcore(self):
        for corruption in ('missing','overmax','bool','missingcf'):
            with self.subTest(corruption=corruption):
                state = self.start_terminal(self.win())
                hero = state['profile']['heroes']['7']
                if corruption == 'missing':state['profile']['heroes'].pop('7')
                elif corruption == 'overmax':hero['cf'] = 101
                elif corruption == 'missingcf':hero.pop('cf')
                else:hero['cf'] = True
                before = copy.deepcopy(state)
                done,notices = self.dialog(state)
                self.assertEqual(done['profile'],before['profile'])
                self.assertEqual(done['story']['blackcores'],{})
                self.assertNotIn(73,done['story'].get('cgs',[]))
                self.assertIn(7026,done['processing_events'])
                self.assertEqual(notices,[])
                self.assertFalse(done['story'].get('event_effect_receipts',{}))

    def test_wrong_mapping_week_scene_or_party_proof_is_atomic(self):
        for field,value in (('week',1),('scene',137),('terminal_event',7029),('party',[24,24]),('party',[8]),('outcome',0)):
            state = self.start_terminal(self.win())
            state['story']['event_terminal_contexts']['0:7026:1'][field] = value
            done,notices = self.dialog(state)
            self.assertEqual(done['profile'],state['profile'])
            self.assertEqual(notices,[])
            self.assertIn(7026,done['processing_events'])

    def test_negative_selector_and_missing_actual_win_stay_pending(self):
        state = self.start_terminal(self.win())
        tables = copy.deepcopy(self.tables)
        tables['reward_common'][114]['fatigue'] = {0:-10}
        done,notices,diag = plan_event_effects(state,7026,self.events,tables,{'receipt_key':'0:7026:1'})
        self.assertFalse(diag['ready']);self.assertEqual(done,state);self.assertEqual(notices,[])
        state = self.state();state['processing_events'] = [7026]
        begin_story_occurrence(state,7026,self.events,{})
        done,_ = self.dialog(state)
        self.assertIn('missing-winning-party-provenance',done['story']['pending_effects']['7026']['reason'])

    def test_unambiguous_retained_legacy_backfill_and_pruned_legacy_pending(self):
        for retained in (True,False):
            state = self.win()
            state['story'].pop('event_terminal_offers')
            state['story']['available_origins']['7026'] = {'source':'accepted_mission_result','fight_id':'actual-161','scene':161,'outcome':1}
            if not retained:state['battle']['receipts'] = []
            state = self.start_terminal(state)
            done,_ = self.dialog(state)
            if retained:
                self.assertEqual(done['profile']['heroes']['7']['cf'],100)
                self.assertIn('0:7026:1',done['story']['event_terminal_contexts'])
                validate_event_terminal_state(done)
            else:
                self.assertEqual(done['profile']['heroes']['7']['cf'],22)
                self.assertIn('retained-receipt-required',done['story']['pending_effects']['7026']['reason'])

    def test_explicit_hero_reward_semantics_unchanged_and_original_maximum_caps_selector(self):
        state = self.start_terminal(self.win())
        tables = copy.deepcopy(self.tables)
        tables['reward_common'][114]['fatigue'] = {0:20,8:3}
        tables['hero'][7]['fatigueValue'] = 30
        done,notices,diag = plan_event_effects(state,7026,self.events,tables,{'receipt_key':'0:7026:1'})
        self.assertTrue(diag['ready'],diag)
        self.assertEqual([done['profile']['heroes'][str(h)]['cf'] for h in [24,7,8]],[27,30,18])
        self.assertIn(('updateCurFatigueValue',{'h':7,'v':30}),notices)

    def test_schema_accepts_legacy_absence_and_rejects_malformed_maps(self):
        validate_event_terminal_state(self.state())
        for field in ('event_terminal_offers','event_terminal_contexts','event_terminal_effect_audit'):
            for value in ([],{'7026':[]}):
                state = self.state();state['story'][field] = value
                with self.assertRaises(ValueError):validate_event_terminal_state(state)

    def test_week_reset_archives_proof_and_never_carries_it_to_new_week(self):
        import test_offline_week as week_fixture
        from offline_week import prepare_week_transition, read_week_history
        fixture = week_fixture.WeekCycleTests()
        fixture.setUp()
        state = self.start_terminal(self.win(party=[24]))
        for key in ('event_terminal_contexts','event_terminal_offers','available_origins',
                    'event_battle_gates','event_battle_wins','event_occurrences'):
            fixture.state['story'][key] = copy.deepcopy(state['story'].get(key,{}))
        fixture.state['processing_events'] = [7026]
        candidate,_,_ = prepare_week_transition(fixture.state,'handleResetWeekAsk','fatigue-reset',
            fixture.tables,authorized_reset=True)
        self.assertNotIn('event_terminal_contexts',candidate['story'])
        archive = read_week_history(candidate['week_protocol']['history'][0])
        self.assertEqual(archive['story']['event_terminal_contexts']['0:7026:1']['party'],[24])
        validate_event_terminal_state(candidate)

    def test_changed_fingerprint_or_retained_receipt_party_fails_closed(self):
        for mutation in ('fingerprint','receiptparty','retainedparty'):
            state = self.start_terminal(self.win())
            if mutation == 'fingerprint':
                state['story']['event_terminal_contexts']['0:7026:1']['result_fingerprint'] = 'f'*64
            elif mutation == 'receiptparty':
                state['battle']['receipts'][-1]['reply']['h'] = [8]
            else:
                state['battle']['receipts'] = []
                state['story']['event_terminal_contexts']['0:7026:1']['party'] = [8]
            done,notices = self.dialog(state)
            self.assertEqual(done['profile'],state['profile'])
            self.assertEqual(notices,[])
            self.assertIn(7026,done['processing_events'])

    def test_stale_queued_trace_cannot_complete_new_occurrence(self):
        state = self.start_terminal(self.win())
        for source in ({'week':1,'occurrences':{'7026':1}},{'week':0,'occurrences':{'7026':0}}):
            done,notices = self.dialog(state,_winning_terminal_trace_source=source)
            self.assertEqual(done['profile'],state['profile'])
            self.assertIn(7026,done['processing_events'])
            self.assertFalse(any(entry[0] == 7026 for entry in done['event_traces']))
            self.assertEqual(notices,[])
        done,_ = self.dialog(state,_winning_terminal_trace_source={'week':0,'occurrences':{'7026':1}})
        self.assertIn(7026,done['completed_events'])


if __name__ == '__main__':unittest.main()
