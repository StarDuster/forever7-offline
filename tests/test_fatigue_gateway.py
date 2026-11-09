"""Actual gateway161/7026 save-before-notice and retry boundaries; host only."""
import copy
import hashlib
from pathlib import Path
import sys
import unittest
from unittest.mock import patch
ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT/'tests'),str(ROOT/'tools'),str(ROOT/'runtime'),str(ROOT/'analysis/research-agent')]
import test_gateway_integrations as fixtures
from read_data_table import read
from test_offline_event_effects import original_tables


class FatigueGatewayTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.content = read(ROOT/'analysis/decompiled/event_content.py')
        cls.tables = original_tables()

    def setUp(self):
        self.f = fixtures.IntegratedGatewayTests(methodName='runTest')
        self.f.setUp();self.addCleanup(self.f.doCleanups)
        self.proxy = self.f.proxy
        for name in ('mission','city_data','reward_common','cg_data','hero'):
            self.f.table(name,self.tables[name])
        self.f.table('event_content',self.content)
        self.proxy.profile['heroes']['24']['cf'] = 17
        self.proxy.available_events = {7025:1}
        self.proxy.reliable_call({'w':{'m':'startEvent','p':{'e':7025},'r':7025}})
        self.proxy.process_story('trace',{'k':'dialog','d':{'c':7025}})
        total = sum(w for _,w in self.f.stage['reward_pool304']['weights'])
        uid = next('%024x'%n for n in range(161000,162000)
            if int(hashlib.sha256(('stage-drop-v1:%024x:304:0'%n).encode()).hexdigest(),16)%total < 147000)
        self.f.modules['common.IdManager'].IdManager.genid = lambda:uid
        self.proxy.handle_battle_admission({'t':2,'s':161,'h':[24],'d':{}},7)
        self.active = copy.deepcopy(self.proxy.battle['active'])
        self.assertIsNotNone(self.active)
        self.result = {'t':2,'s':161,'h':[24],'x':[],'w':1,'e':{}}
        self.f.owner.replies[:] = []

    def finish(self):self.proxy.handle_battle_finish(self.result,self.active['fight_id'])
    def start_terminal(self):self.proxy.reliable_call({'w':{'m':'startEvent','p':{'e':7026},'r':7026}})
    def dialog(self):self.proxy.process_story('trace',{'k':'dialog','d':{'c':7026}})

    def test_actual_win_save_failure_rolls_back_winning_offer_and_retries(self):
        before = self.proxy.progress_snapshot()
        with patch.object(self.proxy._store,'write',side_effect=OSError('disk full')):
            with self.assertRaises(OSError):self.finish()
        self.assertEqual(self.proxy.progress_snapshot(),before)
        self.assertNotIn(7026,self.proxy.available_events)
        self.assertEqual(self.f.owner.replies,[])
        self.finish()
        self.assertIn(7026,self.proxy.available_events)
        self.assertEqual(self.proxy.story['event_terminal_offers']['7026']['party'],[24])
        self.assertEqual(self.proxy.profile['heroes']['24']['cf'],17)

    def test_terminal_save_failure_recovers_only_after_real_dialog_retry(self):
        self.finish();self.start_terminal()
        self.assertEqual(self.proxy.profile['heroes']['24']['cf'],17)
        self.assertNotIn(73,self.proxy.story.get('cgs',[]))
        before = self.proxy.progress_snapshot();self.f.owner.replies[:] = []
        with patch.object(self.proxy._store,'write',side_effect=OSError('disk full')):
            with self.assertRaises(OSError):self.dialog()
        self.assertEqual(self.proxy.progress_snapshot(),before)
        self.assertEqual(self.f.owner.replies,[])
        self.dialog()
        self.assertEqual(self.proxy.profile['heroes']['24']['cf'],100)
        self.assertIn(73,self.proxy.story['cgs'])
        self.assertEqual(self.proxy.story['blackcores'],{'3':1,'4':1})
        self.assertIn(('updateCurFatigueValue',{'h':24,'v':100}),self.f.owner.replies)
        self.assertIn(7026,self.proxy.completed_events)
        snapshot = self.proxy.progress_snapshot();self.dialog()
        self.assertEqual(self.proxy.progress_snapshot(),snapshot)


if __name__ == '__main__':unittest.main()
