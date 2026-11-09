import copy
import sys
import unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'runtime'))
sys.path.insert(0, str(ROOT / 'analysis/research-agent'))
from read_literal_marshal import read
from test_offline_profile import empty_hero
from offline_profile import (migrate_full_hero_roster, migrate_released_wardrobe,
    migrate_awakening_wardrobe, grant_profile_skins, validate_hero_profile)
from offline_wardrobe_completion import (migrate_remaining_wardrobe, REMAINING_IDS,
    costume_resource_preflight, wardrobe_title_counts)

class WardrobeCompletionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        base = ROOT / 'analysis/android640-scripts/com/data/cdata'
        cls.heroes, cls.skins, cls.awake = [read(base / name) for name in
            ('hero.marshal', 'skin.marshal', 'awake_consume_data.marshal')]
    def setUp(self):
        self.ids = iter('%024x' % n for n in range(1, 3000))
        self.make_id = lambda: next(self.ids)
        p,_=migrate_full_hero_roster(None,self.heroes,self.skins,
            lambda _:empty_hero(),self.make_id,123)
        p,_=migrate_released_wardrobe(p,self.skins,self.awake,self.make_id,123)
        self.before,_=migrate_awakening_wardrobe(p,self.heroes,self.skins,self.awake,self.make_id,123)
    def migrate(self, p=None, catalog=None, make_id=None):
        return migrate_remaining_wardrobe(p or self.before,catalog or self.skins,
            make_id or self.make_id,456,validate_hero_profile,grant_profile_skins)
    def test_real_catalog_494_exact_templates_preserve_existing_and_idempotence(self):
        baseline=copy.deepcopy(self.before)
        p,changed=self.migrate()
        self.assertTrue(changed)
        self.assertEqual(self.before,baseline)
        self.assertEqual({s['i'] for h in p['heroes'].values() for s in h['sk'].values()},set(self.skins))
        self.assertEqual(sum(len(h['sk']) for h in p['heroes'].values()),494)
        for key,hero in baseline['heroes'].items():
            for field in hero:
                if field!='sk':self.assertEqual(hero[field],p['heroes'][key][field])
            for uid,skin in hero['sk'].items():self.assertEqual(skin,p['heroes'][key]['sk'][uid])
        again,changed=self.migrate(p)
        self.assertFalse(changed);self.assertEqual(again,p)
    def test_preserves_custom_dye_higher_progress_and_equipped_awakening(self):
        h=self.before['heroes']['24'];h['as']=3;h['ar']['aao']=21
        current=h['cs'];h['sk'][current]['cd']={1:[1,2,3]}
        awake=next(uid for uid,s in h['sk'].items() if s['ias'])
        h['lncs'],h['cs'],h['ass']=current,awake,True
        h['ti']['items']=[{'u':'a'*24,'i':1001}]
        p,_=self.migrate()
        for field in ('cs','lncs','ass','as','ar','ti'):self.assertEqual(h[field],p['heroes']['24'][field])
        self.assertEqual(h['sk'][current],p['heroes']['24']['sk'][current])
    def test_dye_parent_failure_and_uuid_collision_leave_original_untouched(self):
        before=copy.deepcopy(self.before);bad=dict(self.skins)
        del bad[bad[100021]['ori_skin']]
        with self.assertRaises(ValueError):self.migrate(catalog=bad)
        self.assertEqual(self.before,before)
        duplicate=next(iter(self.before['heroes']['38']['sk']))
        with self.assertRaises(ValueError):self.migrate(make_id=lambda:duplicate)
        self.assertEqual(self.before,before)
    def test_owned_presets_default_to_native_dye_not_copied_custom_dye(self):
        p,_=self.migrate()
        for template in REMAINING_IDS:
            h=p['heroes'][str(self.skins[template]['hero'])]
            s=next(s for s in h['sk'].values() if s['i']==template)
            self.assertEqual(s['cd'],{});self.assertEqual(s['pd'],{})
            self.assertFalse(s['ias']);self.assertFalse(s['fb'])
    def test_title_uses_same_universe_and_excludes_awakening_and_dye(self):
        p,_=self.migrate();hidden={r['awake_skin'] for r in self.awake.values() if r.get('awake_skin')}
        totals=[wardrobe_title_counts(int(k),h['sk'],self.skins,hidden) for k,h in p['heroes'].items()]
        self.assertTrue(all(n==d for n,d in totals));self.assertEqual(sum(d for n,d in totals),277)
    def test_resource_search_order_and_required_attachment_failure(self):
        calls=[]
        def exists(path):calls.append(path);return path=='hero_skin/30141/30141.gim'
        ok,missing=costume_resource_preflight(10080,self.skins,{},exists)
        self.assertTrue(ok);self.assertEqual(missing,[])
        self.assertEqual(calls,['hero/30141/30141.gim','hero_skin/30141/30141.gim'])
        models={'30141':{'attach_real_model':[(1,'socket','model/test/attach.gim')]}}
        ok,missing=costume_resource_preflight(10080,self.skins,models,exists)
        self.assertFalse(ok);self.assertEqual(missing,['model/test/attach.gim'])
    def test_missing_model_reports_real_paths_no_substitute_model(self):
        ok,missing=costume_resource_preflight(10081,self.skins,{},lambda _:False)
        self.assertFalse(ok);self.assertEqual(len(missing),5)
        self.assertTrue(all('/30142/30142.gim' in p for p in missing))


# Native lifecycle contract mocks exercise only new failure/commit boundaries;
# model rendering and preset colors still require the Android acceptance run.
class WardrobeUIContractTests(unittest.TestCase):
    def setUp(self):
        import types
        from unittest.mock import patch
        import offline_wardrobe_completion as completion
        self.completion=completion
        self.queue=[];self.messages=[];self.selects=[];self.confirms=[]
        self.missing=False;self.dye_error=False
        self.skin_old=types.SimpleNamespace(id=24,forbid=False)
        self.skin_new=types.SimpleNamespace(id=10081,forbid=False)
        hero=types.SimpleNamespace(skins={'old':self.skin_old,'new':self.skin_new},curSkin='old')
        self.hero=hero
        self.scene=types.SimpleNamespace(real_model_id=30142,model_can_touch=False,
            scene_model=types.SimpleNamespace(model=types.SimpleNamespace(valid=True)))
        case=self
        class Panel:
            valid=True;visible=True;hero_id=24;skin_uuid='old'
            def refresh_title(self):pass
            def select_skin(self,uid,notify=True):case.selects.append(uid);self.skin_uuid=uid
            def on_confirm_click(self,sender,event):case.confirms.append(self.skin_uuid)
            def refresh_model_dye(self):
                if case.dye_error:raise ValueError('native dye failed')
        self.Panel=Panel
        self.panel=Panel()
        modules={}
        def mod(name,**attrs):
            m=types.ModuleType(name);m.__path__=[]
            for k,v in attrs.items():setattr(m,k,v)
            modules[name]=m
            if '.' in name:
                parent,child=name.rsplit('.',1)
                if parent not in modules:mod(parent)
                setattr(modules[parent],child,m)
            return m
        mod('gg',avatar=types.SimpleNamespace(heroMgrData=types.SimpleNamespace(getHero=lambda _:hero)),
            ui=types.SimpleNamespace(panels=types.SimpleNamespace(common_message=types.SimpleNamespace(notify_message=self.messages.append))),
            city_container=types.SimpleNamespace(get_current_scene=lambda:self.scene),
            exec_delay=lambda ms,fn:self.queue.append(fn))
        mod('C_file',find_res_file=lambda path,unused:not self.missing)
        mod('com.const');mod('com.data.cdata.skin',data={24:{'hero':24,'model_id':'10020'},10081:{'hero':24,'model_id':'30142'}})
        mod('com.data.cdata.ui_model_data',data={});mod('com.data.cdata.awake_consume_data',data={})
        mod('cocos.panels.hero_wardrobe',Panel=Panel)
        mod('cocosui',ccui=types.SimpleNamespace(TOUCH_EVENT_ENDED=2))
        self.patch=patch.dict(sys.modules,modules);self.patch.start();self.addCleanup(self.patch.stop)
        completion.install_remaining_wardrobe_ui()
    def test_missing_resource_keeps_old_selection_and_outfit(self):
        self.missing=True;self.panel.select_skin('new')
        self.assertEqual(self.selects,[]);self.assertEqual(self.panel.skin_uuid,'old')
        self.assertEqual(self.hero.curSkin,'old');self.assertTrue(self.messages)
    def test_new_costume_can_load_and_confirm_without_validation_whitelist(self):
        self.panel.select_skin('new');self.panel.on_confirm_click(None,2)
        self.assertEqual(self.confirms,[])
        self.scene.model_can_touch=True;self.queue.pop(0)()
        self.panel.on_confirm_click(None,2)
        self.assertEqual(self.confirms,['new'])
        self.assertEqual(self.hero.curSkin,'old')  # Only original RPC may commit.
    def test_dye_failure_restores_prior_preview_and_never_confirms(self):
        self.panel.select_skin('new');self.scene.model_can_touch=True;self.dye_error=True
        self.queue.pop(0)()
        self.assertEqual(self.selects,['new','old'])
        self.assertEqual(self.panel.skin_uuid,'old');self.assertEqual(self.hero.curSkin,'old')
        self.assertEqual(self.confirms,[])
    def test_native_loader_timeout_restores_old_preview_without_committing(self):
        self.panel.select_skin('new')
        for _ in range(41):
            self.queue.pop(0)()
        self.assertEqual(self.selects,['new','old'])
        self.assertEqual(self.panel.skin_uuid,'old');self.assertEqual(self.hero.curSkin,'old')
        self.assertFalse(self.queue);self.assertTrue(self.messages)
    def test_abandoned_preview_cannot_restore_over_newer_selection(self):
        self.panel.select_skin('new');self.panel.select_skin('old')
        self.queue.pop(0)()
        self.assertEqual(self.selects,['new','old']);self.assertEqual(self.panel.skin_uuid,'old')

if __name__ == '__main__':
    unittest.main()
