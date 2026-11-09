"""True LocalProxy ROLE transactions with explicit host combat projection stub."""
import copy
from pathlib import Path
import sys
from types import SimpleNamespace
import unittest
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'runtime'),str(ROOT/'tests'),str(ROOT/'analysis/research-agent')]
import test_role_mission as role_fixture
import test_gateway_integrations as gateway_fixture
from test_local_gateway import gateway
import offline_role_mission as role
from read_data_table import read as read_events


class RoleGatewayTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tables=role_fixture.original_role_tables()
        cls.events=read_events(ROOT/'analysis/decompiled/event_content.py')
    def setUp(self):
        self.f=gateway_fixture.IntegratedGatewayTests(methodName='runTest');self.f.setUp();self.addCleanup(self.f.doCleanups)
        self.proxy,self.owner=self.f.proxy,self.f.owner
        self.owner.weeknumData=SimpleNamespace(daynum=2,weeknum=1)
        self.proxy.story.update(route='10',week=1,date=2);self.proxy.day['stock_day']=2
        self.f.engine.avatar=self.owner
        self.deferred=[];self.confirms=[];self.enters=[]
        self.proxy.defer=lambda delay,callback:self.deferred.append(callback)
        self.owner.combatData=SimpleNamespace(fight_id=None,reset=lambda:None)
        self.owner.battleEnterWithEventMode=lambda scene:self.enters.append(scene)
        panel=SimpleNamespace(visible=False,valid=True,
            notify_confirm=lambda text,confirm_cb,**kwargs:self.confirms.append((text,confirm_cb,kwargs)))
        self.f.engine.ui=SimpleNamespace(panels=SimpleNamespace(common_confirm=panel),_dialogue=False)
        self.f.engine.logic=SimpleNamespace(game_state=SimpleNamespace(current='CITY'))
        self.f.modules['com.const'].GameState=SimpleNamespace(CITY='CITY')
        for name,rows in self.tables.items():self.f.table(name,rows)
        self.f.table('event_content',self.events);self.f.table('event_condition',{})
        self.f.table('city_fight_reward',{1:{'money':7,'exp':3,'friendly':9}})
        self.f.table('reward_random',{});self.f.table('player_exp',{1:{'lv_exp':100}})
        def projection(owner,active,mission):
            self.assertEqual(active['party_kind'],'trial')
            return {'heroes':{str(('',hero)):{'id':hero,'d':{'_base_max_hp':100},'s':[[[1,4]],[]],
                't':[],'ai':[False,0],'as':0,'lv':active['role_mission']['actors'][str(hero)]['fixed']['level']} for hero in active['request']['h']},
                'skins':[],'hero_lv':active['hero_level'],'monster_lv':1}
        context=patch.object(gateway,'native_stage_combat_data',projection);context.start();self.addCleanup(context.stop)
        context=patch.object(gateway,'native_role_combat_data',projection);context.start();self.addCleanup(context.stop)
        self.seq=0;self.owner.replies[:]=[]
    def start(self,scene=315):
        event=next(event for event,row in self.events.items() if row.get('release') and row.get('enterBattle')==scene)
        self.proxy.available_events={event:1};self.seq+=1
        self.proxy.reliable_call({'w':{'m':'startEvent','p':{'e':event},'r':self.seq}})
        self.assertIn(event,self.proxy.processing_events)
        return event
    def admit(self,scene=315):
        self.proxy.handle_battle_admission({'t':2,'s':scene,'h':list(self.tables['mission'][scene]['defaultHeroes']),'d':{}},7)
        active=self.proxy.battle.get('active');self.assertIsNotNone(active)
        self.owner.combatData.fight_id=active['fight_id'];return copy.deepcopy(active)
    def finish(self,active,win=0):
        self.proxy.handle_battle_finish({'t':2,'s':active['request']['s'],'h':active['request']['h'],'w':win,'x':[],'e':{}},active['fight_id'])
    def show(self):
        pending=list(self.deferred);self.deferred[:]=[]
        for callback in pending:callback()

    def test_actual_loss_remaining_notice_before_original_reward_and_real_retry_new_fight(self):
        self.start();active=self.admit();self.owner.replies[:]=[];before=copy.deepcopy(self.proxy.profile)
        self.finish(active)
        names=[name for name,_ in self.owner.replies]
        self.assertLess(names.index('setEventBattleStage'),names.index('combatOfflineReward'))
        self.assertIn(('setEventBattleStage',{'s':315,'n':2}),self.owner.replies)
        self.assertNotIn(7146,self.proxy.available_events);self.assertEqual(self.proxy.profile,before)
        retry=self.admit();self.assertNotEqual(retry['fight_id'],active['fight_id'])
        before=self.proxy.progress_snapshot();self.finish(active);self.assertEqual(self.proxy.progress_snapshot(),before)

    def test_actual_win_grants_player_economy_without_owned_trial_mutation_or_fake_dialog(self):
        event=self.start();before=copy.deepcopy(self.proxy.profile['heroes']);active=self.admit();self.finish(active,1)
        self.assertEqual(self.proxy.profile['heroes'],before)
        self.assertEqual(self.proxy.profile['economy']['money'],10007)
        self.assertIn(7145,self.proxy.available_events);self.assertNotIn(event,self.proxy.completed_events)
        self.assertEqual(self.proxy.story['available_origins']['7145']['party_kind'],'trial')
        self.assertFalse(self.proxy.story.get('event_terminal_offers'))
        self.assertFalse(any(name in ('updateFriendlyValue','updateCurFatigueValue') for name,_ in self.owner.replies))
        self.proxy.process_story('trace',{'k':'dialog','d':{'c':event}})
        self.assertIn(event,self.proxy.completed_events)

    def test_admission_and_loss_save_failure_rollback_before_native_delivery(self):
        self.start();before=self.proxy.progress_snapshot();self.owner.replies[:]=[]
        with patch.object(self.proxy._store,'write',side_effect=OSError('disk full')):
            with self.assertRaises(OSError):self.admit()
        self.assertEqual(self.proxy.progress_snapshot(),before)
        self.assertEqual(self.owner.replies[-1][1]['t'],0)
        active=self.admit();before=self.proxy.progress_snapshot();self.owner.replies[:]=[]
        with patch.object(self.proxy._store,'write',side_effect=OSError('disk full')):
            with self.assertRaises(OSError):self.finish(active)
        self.assertEqual(self.proxy.progress_snapshot(),before);self.assertEqual(self.owner.replies,[])
        self.finish(active)
        self.assertEqual(next(iter(self.proxy.story['event_battle_gates'].values()))['role_episode']['remaining'],2)

    def test_genuine_giveup_only_after_loss_and_stale_owner_or_source_cannot_progress(self):
        self.start();source=role.role_battle_source(self.proxy.progress_snapshot());before=self.proxy.progress_snapshot()
        self.proxy.handle_role_giveup({'s':315},source,self.owner)
        self.assertEqual(self.proxy.progress_snapshot(),before)
        active=self.admit();self.finish(active);source=role.role_battle_source(self.proxy.progress_snapshot());before=self.proxy.progress_snapshot()
        self.proxy.handle_role_giveup({'s':315},source,object());self.assertEqual(self.proxy.progress_snapshot(),before)
        self.proxy.handle_role_giveup({'s':316},source,self.owner);self.assertEqual(self.proxy.progress_snapshot(),before)
        self.proxy.handle_role_giveup({'s':315},source,self.owner)
        self.assertIn(7146,self.proxy.available_events);self.assertNotIn(7144,self.proxy.completed_events)
        after=self.proxy.progress_snapshot();self.proxy.handle_role_giveup({'s':315},source,self.owner)
        self.assertEqual(self.proxy.progress_snapshot(),after)

    def pause(self):
        self.start(426)
        for _ in range(3):self.finish(self.admit(426))
        self.show();self.assertEqual(len(self.confirms),1)
        return self.confirms[-1]

    def test_exhaustion_no_fail_branch_actual_city_confirm_rearms_before_original_enter(self):
        text,confirm,options=self.pause();before=self.proxy.progress_snapshot()
        self.assertIn(1342,self.proxy.processing_events);self.assertNotIn(1342,self.proxy.completed_events)
        self.assertEqual(self.enters,[])
        confirm()
        self.assertEqual(self.enters,[426]);self.assertIsNone(self.proxy.battle['active'])
        source=role.role_battle_source(self.proxy.progress_snapshot());gate=self.proxy.story['event_battle_gates'][source['occurrence']]
        self.assertEqual((gate['status'],gate['role_episode']['remaining'],gate['role_episode']['epoch']),('open',3,2))
        self.assertEqual(self.proxy._store.load()['story']['event_battle_gates'][source['occurrence']]['role_episode']['epoch'],2)
        confirm();self.assertEqual(self.enters,[426])
        active=self.admit(426);self.assertEqual(active['role_epoch'],2)

    def test_paused_confirm_save_failure_later_reoffer_cancel_and_stale_callbacks(self):
        text,confirm,options=self.pause();before=self.proxy.progress_snapshot()
        with patch.object(self.proxy._store,'write',side_effect=OSError('disk full')):confirm()
        self.assertEqual(self.proxy.progress_snapshot(),before);self.assertEqual(self.enters,[])
        role.offer_paused_role_resume(self.proxy);self.show();new=self.confirms[-1]
        confirm();self.assertEqual(self.enters,[])  # old UI callback cannot consume new offer
        new[2]['cancel_cb']();self.assertEqual(self.proxy.progress_snapshot(),before)
        role.offer_paused_role_resume(self.proxy);self.show();third=self.confirms[-1]
        self.proxy.story['week']+=1;third[1]();self.assertEqual(self.enters,[])

    def test_pending_open_rearm_survives_failed_admission_without_refunding_or_new_epoch(self):
        _,confirm,_=self.pause();confirm();source=role.role_battle_source(self.proxy.progress_snapshot())
        self.owner.replies[:]=[]
        with patch.object(gateway,'native_stage_combat_data',side_effect=ValueError('missing resource')):
            self.proxy.handle_battle_admission({'t':2,'s':426,'h':[10],'d':{}},8)
        self.assertIsNone(self.proxy.battle['active']);self.assertEqual(self.owner.replies[-1][1]['t'],0)
        self.show();self.assertGreaterEqual(len(self.confirms),2)
        self.confirms[-1][1]();after=role.role_battle_source(self.proxy.progress_snapshot())
        self.assertEqual(after['epoch'],source['epoch']);self.assertEqual(self.enters,[426,426])

    def test_queued_event_admission_pins_original_occurrence_and_week(self):
        self.start();source=role.role_battle_source(self.proxy.progress_snapshot())
        self.proxy.story['event_battle_cursor']='another-occurrence'
        self.proxy.handle_battle_admission({'t':2,'s':315,'h':[14],'d':{}},8,
            source_context=(self.owner,None,source))
        self.assertIsNone(self.proxy.battle['active']);self.assertEqual(self.owner.replies[-1][1]['t'],0)

    def test_duplicate_loss_republishes_remaining_before_reward_without_debit(self):
        self.start();active=self.admit();self.finish(active)
        before=self.proxy.progress_snapshot();self.owner.replies[:]=[]
        self.finish(active)
        self.assertEqual(self.proxy.progress_snapshot(),before)
        self.assertEqual(self.owner.replies[0],('setEventBattleStage',{'s':315,'n':2}))
        self.assertEqual(self.owner.replies[-1][0],'combatOfflineReward')

    def test_giveup_save_failure_keeps_real_loss_and_can_retry_original_request(self):
        self.start();active=self.admit();self.finish(active)
        source=role.role_battle_source(self.proxy.progress_snapshot());before=self.proxy.progress_snapshot()
        with patch.object(self.proxy._store,'write',side_effect=OSError('disk full')):
            with self.assertRaises(OSError):self.proxy.handle_role_giveup({'s':315},source,self.owner)
        self.assertEqual(self.proxy.progress_snapshot(),before);self.assertNotIn(7146,self.proxy.available_events)
        self.proxy.handle_role_giveup({'s':315},source,self.owner)
        self.assertIn(7146,self.proxy.available_events)

    def test_older_paused_occurrence_can_rebind_cursor_only_on_current_ui_confirmation(self):
        _,_,options=self.pause();options['cancel_cb']()
        key=self.proxy.story['event_battle_cursor']
        self.proxy.story['event_battle_cursor']='unrelated-current-source'
        role.offer_paused_role_resume(self.proxy);self.show()
        self.confirms[-1][1]()
        self.assertEqual(self.proxy.story['event_battle_cursor'],key)
        self.assertEqual(self.enters,[426])

    def test_transient_confirm_consumer_exception_does_not_strand_paused_entry(self):
        _,_,options=self.pause();options['cancel_cb']()
        before=self.proxy.progress_snapshot()
        panel=self.f.engine.ui.panels.common_confirm
        with patch.object(panel,'notify_confirm',side_effect=RuntimeError('transient original panel failure')):
            role.offer_paused_role_resume(self.proxy)
            with self.assertRaises(RuntimeError):self.show()
        self.assertIsNone(self.proxy._role_pause_offer)
        self.assertEqual(self.proxy.progress_snapshot(),before)
        self.assertEqual(self.enters,[])
        role.offer_paused_role_resume(self.proxy);self.show()
        self.assertEqual(len(self.confirms),2)


if __name__=='__main__':unittest.main()
