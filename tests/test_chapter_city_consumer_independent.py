"""Original CityData consumption of chapter notices, without native rendering.

Victories are modeled host results. Original UI effects are observable calls;
map/camera/animation execution is deliberately outside this harness.
"""
from contextlib import redirect_stdout
import copy
import io
from pathlib import Path
import sys
from types import SimpleNamespace
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / 'tests'), str(ROOT / 'runtime')]
import test_chapter_campaign as chapter_fixture
import test_gateway_integrations as gateway_fixture
from test_offline_rpc_rejections import original_definition


class Py2Dict(dict):
    def iteritems(self):
        return iter(self.items())

    def get(self, key, default=None):
        return super().get(key, py2_containers(default))


def py2_containers(value):
    if isinstance(value, dict):
        return Py2Dict({key: py2_containers(item) for key, item in value.items()})
    if isinstance(value, list):
        return [py2_containers(item) for item in value]
    if isinstance(value, tuple):
        return tuple(py2_containers(item) for item in value)
    return value


class OriginalCityConsumer:
    def __init__(self, areas):
        self.opened, self.fights, self.stage_updates = [], [], []
        noop = lambda *args, **kwargs: None
        panels = SimpleNamespace(city=SimpleNamespace(notify_update_area=noop,
            notify_update_stage=noop, notify_update_info=noop),
            city_entrance=SimpleNamespace(update_prop=noop),
            battle_stage=SimpleNamespace(notify_update_stage=lambda area:
                self.stage_updates.append(copy.deepcopy(area))),
            settlement_fullscreen=SimpleNamespace(
                notify_area_open=lambda areas: self.opened.append(list(areas)),
                notify_area_fight=lambda areas: self.fights.append(list(areas)),
                notify_area_cr=noop))
        namespace = {'gg': SimpleNamespace(ui=SimpleNamespace(panels=panels)),
            'const': SimpleNamespace(CityStatus=SimpleNamespace(FREE=0, FIGHT=1,
                FALL=2, STRIKE=5, ZHUISHA=6))}
        methods = {name: original_definition(ROOT / 'analysis/decompiled/CityData.py',
            name, namespace, decorated=False)
            for name in ('get_area_info', 'set_stages_info', 'set_area_info')}
        self.data = type('ExtractedOriginalCityData', (), methods)()
        self.data.areas_info = py2_containers({'area_' + key: copy.deepcopy(value) for key, value in areas.items()})
        self.data.area_building_obj, self.data.destroy_building = {}, {}
        self.data.owner = SimpleNamespace(logger=None)
        self.data.first_update_city_sfx_visible = noop
        self.data.proc_change_event = noop

    def deliver(self, notices):
        with redirect_stdout(io.StringIO()):
            for name, payload in notices:
                payload = py2_containers(copy.deepcopy(payload))
                if name == 'get_all_area_info_reply':
                    self.data.set_area_info(payload['ais'], payload['sm'])
                elif name == 'get_area_stages_reply':
                    self.data.set_stages_info(payload['ai'], payload['st'])


class ChapterOriginalCityConsumerTests(unittest.TestCase):
    def setUp(self):
        self.fixture = chapter_fixture.ChapterCampaignTests(methodName='runTest')
        self.fixture.setUp()
        for area in self.fixture.state['story']['city_areas'].values():
            area.setdefault('lv', 1)

    def test_negative_control_stage_only_loses_absent_area_and_cannot_activate_fall(self):
        stage = ('get_area_stages_reply', {'ai': 3, 'st': {'cs': 2101, 'sl': [[2101]]}})
        absent = OriginalCityConsumer({})
        absent.deliver([stage])
        self.assertEqual(absent.data.areas_info, {})
        fallen = OriginalCityConsumer({'3': {'id': 3, 'st': [2, False, False], 'bd': {}}})
        fallen.deliver([stage])
        self.assertEqual(fallen.data.get_area_info(3)['st'][0], 2)
        self.assertEqual(fallen.stage_updates, [])

    def test_actual_refresh_notices_update_absent_and_fallen_original_city_consumers(self):
        state = self.fixture.completed_area2()
        for present in (False, True):
            candidate = copy.deepcopy(state)
            if present:
                candidate['story']['city_areas']['3'] = {'id': 3, 'st': [2, False, False], 'bd': {}}
            consumer = OriginalCityConsumer(candidate['story']['city_areas'])
            notices = self.fixture.refresh(candidate)
            self.assertEqual(notices[0][0], 'get_all_area_info_reply')
            self.assertFalse(notices[0][1]['sm'])
            consumer.deliver(notices)
            area = consumer.data.get_area_info(3)
            self.assertEqual(area['st'][0], 1)
            self.assertEqual(area['stage'], candidate['story']['city_areas']['3']['stage'])
            self.assertEqual(consumer.opened, [])
            self.assertEqual(consumer.fights, [])
            self.assertTrue(any(area['id'] == 3 for area in consumer.stage_updates))

    def test_actual_gateway_enrichment_preserves_original_win_open_animation_order(self):
        state = self.fixture.state
        self.fixture.refresh(state)
        for scene in range(1101, 1106):
            state = self.fixture.finish(self.fixture.admit(state, scene))[0]
        consumer = OriginalCityConsumer(state['story']['city_areas'])
        won, _, effects, changed = self.fixture.finish(self.fixture.admit(state, 1106))
        self.assertTrue(changed)
        fixture = gateway_fixture.IntegratedGatewayTests(methodName='runTest')
        fixture.setUp()
        self.addCleanup(fixture.doCleanups)
        for name, rows in self.fixture.tables.items():
            fixture.table(name, rows)
        won, notices = fixture.proxy.enrich_city_plan(won, effects['notices'])
        full = [payload for name, payload in notices if name == 'get_all_area_info_reply']
        self.assertGreaterEqual(len(full), 2)
        self.assertTrue(full[0]['sm'])
        self.assertFalse(full[-1]['sm'])
        consumer.deliver(notices)
        self.assertEqual(consumer.opened, [[2]])
        self.assertEqual(consumer.data.get_area_info(2)['st'][0], 0)
        self.assertEqual(consumer.data.get_area_info(3)['st'][0], 1)
        self.assertEqual(consumer.data.get_area_info(3)['stage'],
            won['story']['city_areas']['3']['stage'])


if __name__ == '__main__':
    unittest.main()
