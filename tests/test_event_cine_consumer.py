"""Actual extracted original request producer vs canonical EVENT admission."""
from contextlib import redirect_stdout
import copy
import io
from pathlib import Path
import sys
from types import SimpleNamespace
import unittest
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'runtime'),str(ROOT/'tests'),str(ROOT/'analysis/research-agent')]
from test_offline_rpc_rejections import original_definition
from read_literal_marshal import read
from read_data_table import read as read_events
from offline_event_battle import prepare_event_battle_gate,prepare_event_battle_admission


class OriginalCineConsumerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.missions=read(ROOT/'analysis/android640-scripts/com/data/cdata/mission.marshal')
        cls.events=read_events(ROOT/'analysis/decompiled/event_content.py')
    def emit(self,scene,owned,banned=(),selected=None):
        calls,messages=[],[]
        const=SimpleNamespace(MissionMode=SimpleNamespace(CINE_SET={1,2}),QIANSHI_SCENE_SET=(401006,401009,401010,401011,401012),
            BattleType=SimpleNamespace(EVENT=2),BattleMode=SimpleNamespace(PVE=1))
        namespace={'const':const,'MissionDataMod':SimpleNamespace(data=self.missions),
            'gg':SimpleNamespace(ui=SimpleNamespace(panels=SimpleNamespace(
                battle_common=SimpleNamespace(notify_event=lambda *args:messages.append(('select',args))),
                common_message=SimpleNamespace(notify_message=lambda value:messages.append(value)))))}
        function=original_definition(ROOT/'analysis/decompiled/BattleStageMember.py','battleEnterWithEventMode',namespace,decorated=False)
        owner=SimpleNamespace(checkEventBattleStage=lambda scene:True,
            heroMgrData=SimpleNamespace(getHero=lambda hero,withBan=True:hero in owned and (withBan or hero not in banned)),
            combatOfflineRequest=lambda t,s,h,d:calls.append({'t':t,'s':s,'h':list(h),'d':d}))
        with redirect_stdout(io.StringIO()):function(owner,scene,list(selected or []))
        return calls,messages
    def admit(self,scene,owned,banned,args):
        event=next(event for event,row in self.events.items() if row.get('release') and row.get('enterBattle')==scene)
        state={'story':{'week':1,'route':'1','city_values':{'av':24,'fv':100},'banned_heroes':{str(hero):200 for hero in banned}},
            'profile':{'heroes':{str(hero):{'cf':100,'ef':0} for hero in owned},'economy':{'level':50}},
            'processing_events':[event],'completed_events':[],'battle':{'version':1,'active':None,'receipts':[]}}
        state=prepare_event_battle_gate(state,event,self.events,'1:%s:1'%event)[0]
        return prepare_event_battle_admission(state,args,self.missions,self.events,lambda:'actual-consumer-host')[0]

    def test_actual_default_full_and_partial_preserve_original_order_no_max_rejection(self):
        for scene in (413,420,500,400776,400969):
            defaults=list(self.missions[scene]['defaultHeroes'])
            for banned in ([],defaults[1:]):
                with self.subTest(scene=scene,banned=banned):
                    calls,messages=self.emit(scene,defaults,banned)
                    self.assertEqual(len(calls),1);self.assertEqual(messages,[])
                    expected=[hero for hero in defaults if hero not in banned]
                    self.assertEqual(calls[0]['h'],expected)
                    state=self.admit(scene,defaults,banned,calls[0])
                    self.assertEqual(state['battle']['active']['request'],calls[0])
                    self.assertEqual(state['story']['banned_heroes'],{str(hero):200 for hero in banned})
        self.assertEqual(self.missions[500]['max_hero_num'],1)
        self.assertEqual(self.emit(500,[109,113])[0][0]['h'],[109,113])

    def test_all_filtered_native_stops_before_rpc_backend_rejects_forged_full_set(self):
        defaults=[109,113];calls,messages=self.emit(500,defaults,defaults)
        self.assertEqual(calls,[]);self.assertEqual(messages,[179])
        with self.assertRaises(ValueError):self.admit(500,defaults,defaults,{'t':2,'s':500,'h':defaults,'d':{}})
        calls,messages=self.emit(500,[109]);self.assertEqual(calls[0]['h'],[109])
        self.admit(500,[109],[],calls[0])

    def test_exact_original_qianshi_target_exception_without_unowned_actor_fabrication(self):
        scene=401009;targets=list(self.missions[scene]['target_hero']);self.assertEqual(targets,[99])
        calls,messages=self.emit(scene,[24,99],[99],selected=[99,24])
        self.assertEqual(calls[0]['h'],[99,24]);self.assertEqual(messages,[])
        state=self.admit(scene,[24,99],[99],calls[0])
        self.assertEqual(state['battle']['active']['party_kind'],'owned')
        self.assertEqual(state['story']['banned_heroes'],{'99':200})
        calls,_=self.emit(scene,[24],selected=[99,24]);self.assertEqual(calls[0]['h'],[99,24])
        with self.assertRaisesRegex(ValueError,'unowned QIANSHI target assembly unsupported'):
            self.admit(scene,[24],[],calls[0])

    def test_ordinary_selected_ban_filter_and_role_native_bypass_remain_distinct(self):
        calls,messages=self.emit(120,[24,7],[7],selected=[7,24])
        self.assertEqual(calls[0]['h'],[24]);self.admit(120,[24,7],[7],calls[0])
        calls,messages=self.emit(426,[],[10])
        self.assertEqual(calls[0],{'t':2,'s':426,'h':[10],'d':{}})
        self.assertEqual(messages,[])


if __name__=='__main__':unittest.main()
