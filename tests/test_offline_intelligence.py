"""Finite original assault intel13..18 contracts, with atomic host candidates."""
import copy
from pathlib import Path
import sys
import unittest
from types import SimpleNamespace
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'runtime'),str(ROOT/'tools'),str(ROOT/'analysis/research-agent')]
from test_offline_event_effects import original_tables,base_state,read_source,read_marshal
from offline_intelligence import (build_event_intelligence,prepare_intelligence_operation,advance_intelligence_day,
    validate_intelligence_story,native_intelligence_data)
from offline_story_engine import begin_story_occurrence,prepare_story_operation

_TABLES=None
_CONTENT=None

def intel_tables():
    global _TABLES,_CONTENT
    if _TABLES is None:
        _TABLES=original_tables()
        for name in ('intelligence','intelligence_affect'):
            _TABLES[name]=read_marshal(ROOT/'analysis/android640-scripts/com/data/cdata'/(name+'.marshal'))
        _CONTENT=read_source(ROOT/'analysis/decompiled/event_content.py')
        _TABLES['event_content']=_CONTENT
    return _TABLES


def intel_state():
    tables=intel_tables()
    state=base_state(tables)
    state.update(conditions=[],event_traces=[],day={'stock_day':5})
    state['story'].update(week=0,date=5,route='1',emergency=False,
        city_values={'av':24,'dv':205,'dvc':205,'fv':0,'rv':0,'ev':0,'bf':0},
        city_areas={str(a):{'id':a,'lv':1,'bd':{},'st':[3,True,False]}for a in range(3,9)})
    return state


def created_intelligence(state=None):
    state=copy.deepcopy(state) if state is not None else intel_state()
    state['processing_events'].append(6004)
    begin_story_occurrence(state,6004)
    state,notices=prepare_story_operation(state,'start',{'e':6004},_CONTENT,{},intel_tables())
    assert 6004 not in state['completed_events']
    state,notices=prepare_story_operation(state,'trace',{'k':'dialog','d':{'c':6004}},_CONTENT,{},intel_tables())
    assert 6004 in state['completed_events']
    return state,notices


class OriginalIntelligenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):intel_tables()
    def test_actual6004_dialogue_creates_only_CR_eligible_stable_records_and_not_raid_wins(self):
        state=intel_state()
        state['story']['city_areas']['4']['st'][1]=False
        del state['story']['city_areas']['8']
        state['story']['city_areas']['6']['st'][0]=0
        created,notices=created_intelligence(state)
        records=created['story']['intelligence']['is']
        self.assertEqual([r['id']for r in records],[13,15,16,17])
        self.assertTrue(next(r for r in records if r['id']==16)['hd'])
        self.assertEqual(created['story']['city_values']['dvc'],205)
        self.assertEqual(created['story']['battle_wins'],[])
        self.assertFalse(any(name=='triggerIntelligenceEvents'for name,p in notices))
        self.assertTrue(any(name=='syncAllIntelligence'and p['is']['is']==records for name,p in notices))
        validate_intelligence_story(created['story'])
        data,sources=build_event_intelligence(created['story'],6004,(13,14,15,16,17,18),intel_tables(),'0:6004:1',5)
        self.assertEqual(data,created['story']['intelligence'])
        self.assertEqual(sources,created['story']['intelligence_sources'])
    def test_all_original_handle_costs_affects_and_events_are_not_completed(self):
        for iid,cost,affect,event in ((13,5,22,6019),(14,5,21,6012),(15,30,20,6011),(16,45,19,6006),(17,60,18,6007),(18,70,17,6005)):
            with self.subTest(id=iid):
                state,_=created_intelligence()
                record=next(r for r in state['story']['intelligence']['is']if r['id']==iid)
                planned,notices,changed=prepare_intelligence_operation(state,'handleIntelligenceRequest',{'uuid':record['uuid']},intel_tables())
                self.assertTrue(changed)
                self.assertEqual(planned['story']['city_values']['dvc'],205-cost)
                self.assertEqual(planned['story']['city_values']['dv'],205)
                self.assertIn(event,dict(planned['available_events']))
                self.assertNotIn(event,planned['completed_events'])
                self.assertEqual(planned['story']['battle_wins'],[])
                current=next(r for r in planned['story']['intelligence']['is']if r['id']==iid)
                self.assertTrue(current['hd']);self.assertEqual(current['hdd'],5)
                self.assertEqual(current['afs'][0]['id'],affect)
                names=[name for name,p in notices]
                self.assertLess(names.index('syncAllIntelligence'),names.index('handleIntelligenceSuccess'))
                self.assertLess(names.index('handleIntelligenceSuccess'),names.index('triggerIntelligenceEvents'))
                replay,replies,changed=prepare_intelligence_operation(planned,'handleIntelligenceRequest',{'uuid':record['uuid']},intel_tables())
                self.assertFalse(changed);self.assertEqual(replay,planned);self.assertEqual(replies,[])
    def test_insufficient_closed_expired_wrong_uuid_or_stale_week_is_atomic(self):
        state,_=created_intelligence()
        uid=state['story']['intelligence']['is'][0]['uuid']
        for mode in ('cost','closed','expired','wrong','week'):
            value=copy.deepcopy(state);target=next(r for r in value['story']['intelligence']['is']if r['uuid']==uid)
            request=uid
            if mode=='cost':value['story']['city_values']['dvc']=0
            if mode=='closed':target['op']=False
            if mode=='expired':target['ep']=True
            if mode=='wrong':request='f'*24
            if mode=='week':value['story']['week']=1
            original=copy.deepcopy(value)
            with self.subTest(mode=mode):
                with self.assertRaises(ValueError):prepare_intelligence_operation(value,'handleIntelligenceRequest',{'uuid':request},intel_tables())
                self.assertEqual(value,original)
    def test_FREE_area_auto_handle_never_charges_or_offers_assault(self):
        state,_=created_intelligence()
        state['story']['city_areas']['3']['st'][0]=0
        planned,notices,changed=prepare_intelligence_operation(state,'syncAllIntelligenceRequest',{},intel_tables())
        self.assertTrue(changed)
        self.assertTrue(planned['story']['intelligence']['is'][0]['hd'])
        self.assertEqual(planned['story']['city_values']['dvc'],205)
        self.assertNotIn(6019,dict(planned['available_events']))
        self.assertEqual([n for n,p in notices],['syncAllIntelligence'])
    def test_read_open_and_day_ticks_are_canonical_and_idempotent(self):
        state,_=created_intelligence()
        record=state['story']['intelligence']['is'][0]
        # All original six openNeed0 entries start open; repeated open is free.
        same,notices,changed=prepare_intelligence_operation(state,'openIntelligenceRequest',{'uuid':record['uuid']},intel_tables())
        self.assertFalse(changed);self.assertEqual(same,state)
        read,notices,changed=prepare_intelligence_operation(state,'readTodayIntelligence',{},intel_tables())
        self.assertTrue(read['story']['intelligence']['rd']);self.assertEqual(notices,[])
        read['day']['stock_day']=6;read['story']['date']=6
        notices=advance_intelligence_day(read,5,6)
        self.assertEqual(read['story']['intelligence']['is'][0]['ld'],998)
        self.assertFalse(read['story']['intelligence']['rd'])
        self.assertEqual(notices[0][0],'syncAllIntelligence')
        self.assertEqual(advance_intelligence_day(read,6,6),[])
    def test_native_uuid_projection_preserves_matching_records_and_affects(self):
        from test_offline_week import ModelObjectId
        state,_=created_intelligence()
        uid=state['story']['intelligence']['is'][0]['uuid']
        state,notices,changed=prepare_intelligence_operation(state,'handleIntelligenceRequest',{'uuid':uid},intel_tables())
        with patch.dict(sys.modules,{'common.IdManager':SimpleNamespace(IdManager=SimpleNamespace(str2id=ModelObjectId))}):
            data=native_intelligence_data(state['story']['intelligence'])
        self.assertIsInstance(data['is'][0]['uuid'],ModelObjectId)
        self.assertIsInstance(data['is'][0]['afs'][0]['uuid'],ModelObjectId)
        self.assertEqual(str(data['is'][0]['uuid']),uid)
        self.assertIsInstance(state['story']['intelligence']['is'][0]['uuid'],str)
    def test_week_restart_archives_but_clears_actionable_old_intelligence_uuid(self):
        from test_offline_week import WeekCycleTests
        from offline_week import prepare_week_transition
        fixture=WeekCycleTests();fixture.setUp()
        intel,_=created_intelligence()
        fixture.state['story']['intelligence']=intel['story']['intelligence']
        fixture.state['story']['intelligence_sources']=intel['story']['intelligence_sources']
        old_uid=intel['story']['intelligence']['is'][0]['uuid']
        state,notices,changed=prepare_week_transition(fixture.state,'handleResetWeekAsk','real-host-reset',fixture.tables,authorized_reset=True)
        self.assertEqual(state['story']['intelligence'],{'is':[],'rd':False})
        self.assertEqual(state['story']['intelligence_sources'],{})
        with self.assertRaises(ValueError):prepare_intelligence_operation(state,'handleIntelligenceRequest',{'uuid':old_uid},intel_tables())


import test_gateway_integrations as gateway_fixtures
class IntelligenceGatewayTests(gateway_fixtures.IntegratedGatewayTests):
    @classmethod
    def setUpClass(cls):intel_tables()
    def ready(self):
        created,notices=created_intelligence()
        state=self.proxy.progress_snapshot()
        state['story'].update(created['story'])
        state['day']['stock_day']=5
        state['completed_events']=created['completed_events']
        for name in ('intelligence','intelligence_affect'):
            self.table(name,intel_tables()[name])
        self.table('event_content',_CONTENT)
        self.table('story_route',read_marshal(ROOT/'analysis/android640-scripts/com/data/cdata/story_route.marshal'))
        self.table('ending_data',{})
        self.proxy.restore_progress(state)
        self.proxy.save_progress()
        self.proxy.process_week_handoffs()
        self.assertEqual(self.proxy.story['route'],'3-1')
        self.owner.replies[:]=[]
        self.settlements=[]
        self.modules['gg'].ui=SimpleNamespace(enable_settlement=self.settlements.append)
        return self.proxy.story['intelligence']['is'][0]['uuid']
    def test_original_rpc_saves_before_success_uses_nested_is_and_native_uuid(self):
        uid=self.ready()
        self.proxy.handle_intelligence('handleIntelligenceRequest',{'uuid':uid})
        self.assertEqual(self.proxy.story['city_values']['dvc'],200)
        self.assertIn(6019,self.proxy.available_events)
        self.assertNotIn(6019,self.proxy.completed_events)
        names=[name for name,p in self.owner.replies]
        self.assertLess(names.index('syncAllIntelligence'),names.index('handleIntelligenceSuccess'))
        sync=next(p for n,p in self.owner.replies if n=='syncAllIntelligence')
        self.assertIn('is',sync['is'])
        self.assertEqual(sync['is']['is'][0]['uuid'],('native',uid))
        success=next(p for n,p in self.owner.replies if n=='handleIntelligenceSuccess')
        self.assertEqual(success['uuid'],('native',uid))
        saved=self.proxy._store.load()
        self.assertEqual(saved['story']['city_values']['dvc'],200)
        self.assertEqual(saved['story']['intelligence']['is'][0]['uuid'],uid)
        before=self.proxy.progress_snapshot();self.owner.replies[:]=[]
        self.proxy.handle_intelligence('handleIntelligenceRequest',{'uuid':uid})
        self.assertEqual(self.proxy.progress_snapshot(),before)
        self.assertFalse(any(n=='triggerIntelligenceEvents'for n,p in self.owner.replies))
        self.assertEqual(self.settlements,[True])
    def test_failed_save_restores_currency_records_and_publishes_no_success_or_trigger(self):
        uid=self.ready();before=self.proxy.progress_snapshot()
        with patch.object(self.proxy._store,'write',side_effect=OSError('disk full')):
            with self.assertRaises(OSError):self.proxy.handle_intelligence('handleIntelligenceRequest',{'uuid':uid})
        self.assertEqual(self.proxy.progress_snapshot(),before)
        self.assertEqual(self.owner.replies,[])
        self.assertEqual(self.settlements,[True])
    def test_insufficient_development_has_no_false_success_and_restores_settlement(self):
        uid=self.ready();self.proxy.story['city_values']['dvc']=0;self.proxy.save_progress()
        before=self.proxy.progress_snapshot()
        self.proxy.handle_intelligence('handleIntelligenceRequest',{'uuid':uid})
        self.assertEqual(self.proxy.progress_snapshot(),before)
        self.assertFalse(any(n in ('handleIntelligenceSuccess','triggerIntelligenceEvents')for n,p in self.owner.replies))
        self.assertEqual(self.settlements,[True])
