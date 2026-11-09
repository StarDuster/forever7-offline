"""Canonical normal campaigns through shared gateway, original consumer order."""
import copy
from pathlib import Path
import sys
from types import SimpleNamespace
import unittest
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'runtime'),str(ROOT/'tests')]
import test_chapter_campaign as campaign_fixture
import test_gateway_integrations as gateway_fixture
from test_local_gateway import gateway
from test_offline_rpc_rejections import original_definition
import offline_chapter_campaign as campaign
from offline_week import initial_week_state


class NormalChapterGatewayTests(unittest.TestCase):
    def setUp(self):
        fixture=campaign_fixture.ChapterCampaignTests(methodName='runTest');fixture.setUp()
        self.tables=copy.deepcopy(fixture.tables)
        self.f=gateway_fixture.IntegratedGatewayTests(methodName='runTest');self.f.setUp();self.addCleanup(self.f.doCleanups)
        self.proxy,self.owner=self.f.proxy,self.f.owner
        self.proxy.story.update(route='1',week=1,date=0)
        self.proxy.story['current_mission_wins']=[];self.proxy.story['battle_wins']=[]
        self.proxy.week_protocol=initial_week_state()
        self.proxy.week_protocol['transition']={'id':'host-model-actual-freshweek','operation':'handleResetWeekAsk','source_week':0,'target_week':1,'notices':[]}
        self.owner.weeknumData=SimpleNamespace(daynum=0,weeknum=1)
        self.f.engine.avatar=self.owner
        for name,rows in self.tables.items():self.f.table(name,rows)
        self.f.table('city_fight_reward',{1:{'money':0,'exp':0,'friendly':0}})
        self.f.table('reward_random',{});self.f.table('player_exp',{1:{'lv_exp':100}})
        state=self.proxy.progress_snapshot();campaign.refresh_normal_chapters(state,self.tables)
        self.proxy.restore_progress(state);self.proxy.save_progress();self.owner.replies[:]=[]

    def admit(self,scene=1101):
        self.proxy.handle_battle_admission({'t':1,'s':scene,'h':[24],'d':{'a':2}},7)
        return self.proxy.battle.get('active')

    def test_current_chapter_catalog_drift_before_admission_rejects_without_partial_refresh_save(self):
        self.assertEqual(self.proxy.story['normal_chapters']['contexts']['2']['last_stage']['cs'],1101)
        before=self.proxy.progress_snapshot()
        key=next(key for key in self.tables['chapter_mission_data'] if key==(2,0,'-1',0))
        sections=self.tables['chapter_mission_data'][key]['section']
        sections[1],sections[2]=sections[2],sections[1]
        self.assertIsNone(self.admit())
        self.assertEqual(self.proxy.progress_snapshot(),before)
        self.assertEqual(self.owner.replies[-1][1]['t'],0)

    def test_active_normal_resume_revalidates_current_whole_chapter_row(self):
        active=self.admit();self.assertIsNotNone(active)
        before=self.proxy.progress_snapshot();self.owner.replies[:]=[]
        key=(2,0,'-1',0);sections=self.tables['chapter_mission_data'][key]['section']
        sections[1],sections[2]=sections[2],sections[1]
        self.assertEqual(self.admit(),before['battle']['active'])
        self.assertEqual(self.proxy.progress_snapshot(),before)
        self.assertEqual(self.owner.replies[-1][1]['t'],0)

    def test_real_normal_win_keeps_original_true_settlement_and_chapter_full_groups(self):
        active=copy.deepcopy(self.admit());self.assertIsNotNone(active)
        self.proxy.handle_battle_finish({'t':1,'s':1101,'h':[24],'x':[],'w':1,'e':{}},active['fight_id'])
        context=self.proxy.story['normal_chapters']['contexts']['2']
        self.assertEqual(context['wins'],[1101]);self.assertEqual(context['last_stage']['cs'],1102)
        self.assertEqual(self.proxy.story['city_areas']['2']['stage']['sl'],context['descriptor']['groups'])
        self.assertTrue(any(name=='get_all_area_info_reply' and body['sm'] for name,body in self.owner.replies))
        self.assertFalse(any(context['last_stage']['cs']==0 for _ in [0]))

    def test_new_area_full_city_precedes_original_set_stages_consumer(self):
        # Modeled genuine full clear from this provider. This is a projection
        # consumer boundary fixture, not an assertion of six native victories.
        state=self.proxy.progress_snapshot();context=state['story']['normal_chapters']['contexts']['2']
        context['wins']=[group[0] for group in context['descriptor']['groups']]
        context['complete']=True;context['last_stage']={'cs':0,'sl':copy.deepcopy(context['descriptor']['groups'])}
        state['story']['city_areas']['2']['stage']=copy.deepcopy(context['last_stage']);state['story']['city_areas']['2']['st'][0]=0
        state['story']['current_mission_wins']=list(context['wins'])
        notices=campaign.refresh_normal_chapters(state,self.tables)
        self.assertIn('3',state['story']['city_areas'])
        names=[name for name,_ in notices]
        self.assertEqual(names[0],'get_all_area_info_reply');self.assertFalse(notices[0][1]['sm'])
        native_areas={};updates=[]
        gg=SimpleNamespace(ui=SimpleNamespace(panels=SimpleNamespace(battle_stage=SimpleNamespace(notify_update_stage=lambda area:updates.append(area['id'])))))
        namespace={'gg':gg,'const':SimpleNamespace(CityStatus=SimpleNamespace(FIGHT=1,STRIKE=5,ZHUISHA=6))}
        consumer=original_definition(ROOT/'analysis/decompiled/CityData.py','set_stages_info',namespace,decorated=False)
        data=SimpleNamespace(get_area_info=lambda aid:native_areas.get(aid))
        future=next(payload for name,payload in notices if name=='get_area_stages_reply' and payload['ai']==3)
        consumer(data,3,future['st']);self.assertEqual(native_areas,{})
        for name,payload in notices:
            if name=='get_all_area_info_reply':native_areas.update({area['id']:copy.deepcopy(area) for area in payload['ais'].values()})
            elif name=='get_area_stages_reply':consumer(data,payload['ai'],payload['st'])
        self.assertEqual(native_areas[3]['st'][0],1);self.assertEqual(native_areas[3]['stage'],state['story']['city_areas']['3']['stage'])
        self.assertIn(3,updates)


if __name__=='__main__':unittest.main()
