"""Canonical group precedence, no-wish sentinel, and fenced real archive callbacks."""
import copy
from pathlib import Path
import sys
from types import ModuleType,SimpleNamespace as NS
import unittest
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'runtime'),str(ROOT/'analysis/research-agent'),str(ROOT/'tools')]
import offline_gacha_archive as archive
import offline_gacha_ui as ui
from read_literal_marshal import read

class ExistingGroupTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.table=read(ROOT/'analysis/android640-scripts/com/data/cdata/chouka_treasure_wish.marshal')
    def setUp(self):archive.offline_archive_clear()
    def tearDown(self):archive.offline_archive_clear()
    def group(self,pin=None):return {'id':7,'cards':[{'is_open':True,'original':'keep'}], 'special_context':pin or {}}
    def pools(self,wire,group):return {'pools':{str(wire):{'group':group}}}
    def requested(self,wire,table=None):
        table=table or self.table
        if wire==5:return archive.archive_make_session({'wire_t':wire,'category':'hero_treasure'},table,min(k for k,r in table.items()if r.get('drawType')==5))
        period=archive.archive_hero_wish_periods(table,wire)[0]
        return archive.archive_make_session({'wire_t':wire,'category':'hero_treasure'},table,hero_wish_id=period['hero_wish_id'])
    def test_allseven_wires_legacy_fullopen_precedence_cancel_restore_and_expiry(self):
        for wire in (5,1,119,126,143,154,164):
            requested=self.requested(wire);group=self.group();pools=self.pools(wire,group);before=copy.deepcopy(pools)
            conflict=archive.archive_entry_group_conflict(requested,pools,self.table)
            self.assertTrue(conflict['context']['no_wish'])
            old=archive.archive_effective_wish_context(requested,pools,self.table)
            self.assertTrue(old['no_wish']);self.assertEqual(old['effective_group_id'],7)
            restored=archive.archive_restore_group_context(conflict,pools,self.table)
            self.assertEqual(old,restored);self.assertEqual(pools,before)
            pools['pools'][str(wire)]['group']=None
            expired=archive.archive_effective_wish_context(restored,pools,self.table)
            self.assertTrue(expired['no_wish']);self.assertTrue(expired['expired_restore'])
            self.assertIsNone(archive.archive_restore_group_context(conflict,pools,self.table))
            self.assertEqual(archive.archive_effective_wish_context(requested,pools,self.table),requested)
    def test_t5_A_vs_B_and_hero_multi_epoch_binding_invalid_pin_and_newgroup_fences(self):
        ids=sorted(k for k,r in self.table.items()if r.get('drawType')==5)
        a,b=ids[0],ids[-1]
        requested=archive.archive_make_session({'wire_t':5,'category':'hero_treasure'},self.table,b)
        pools=self.pools(5,self.group({'policy':'offline-original-display-probability-treasure-wish-v1','wish_id':a}))
        old=archive.archive_effective_wish_context(requested,pools,self.table)
        self.assertEqual(old['wish_id'],a);self.assertTrue(ui.free_wish_selection_context(old,self.table))
        conflict=archive.archive_entry_group_conflict(requested,pools,self.table)
        pools['pools']['5']['group']['id']=8
        self.assertIsNone(archive.archive_restore_group_context(conflict,pools,self.table))
        pools['pools']['5']['group']=self.group({'policy':'offline-original-display-probability-treasure-wish-v1','wish_id':999999})
        with self.assertRaises(ValueError):archive.archive_effective_wish_context(requested,pools,self.table)
        # Synthetic second epoch preserves original row schemas/targets, testing
        # all hero wires without inventing actual extra production periods.
        for wire in (1,119,126,143,154,164):
            table=copy.deepcopy(self.table);oldperiod=archive.archive_hero_wish_periods(table,wire)[0]
            newids=[]
            for identifier in oldperiod['hero_wish_ids']:
                row=copy.deepcopy(table[identifier]);row['id']=identifier+10000;row['begin_time']=(2025,1,1);row['end_time']=(2025,2,1)
                table[row['id']]=row;newids.append(row['id'])
            requested=archive.archive_make_session({'wire_t':wire,'category':'hero_treasure'},table,hero_wish_id=min(newids))
            pin={'hero_wish_policy':'offline-original-hero-wish-period-v1','hero_wish_ids':oldperiod['hero_wish_ids']}
            pools=self.pools(wire,self.group(pin));conflict=archive.archive_entry_group_conflict(requested,pools,table)
            restored=archive.archive_restore_group_context(conflict,pools,table)
            self.assertEqual(restored['hero_wish_ids'],oldperiod['hero_wish_ids'])
            self.assertEqual(archive.archive_effective_wish_context(requested,pools,table),restored)
            pools['pools'][str(wire)]['group']['special_context']={}
            self.assertIsNone(archive.archive_restore_group_context(conflict,pools,table))
    def test_getters_no_wish_never_fallback_and_free_control_denied(self):
        archive._f7_archive_session={'wire_t':5,'no_wish':True}
        calls=[]
        getter=archive.make_archive_wish_getter(lambda *a:calls.append(a)or 123,self.table)
        groups=archive.make_archive_wish_group_getter(lambda *a:calls.append(a)or {1:[123]},self.table)
        self.assertIsNone(getter(None,5));self.assertEqual(groups(None,5),{});self.assertEqual(calls,[])
        provider=lambda:archive.offline_archive_context(5)
        valid=ui.make_free_wish_validation(lambda *a:0,provider,self.table)
        self.assertEqual(valid(None,5,1141),1882)
        show=ui.make_free_wish_window_show(lambda *a,**k:calls.append('opened'),provider,self.table)
        show(NS(),type='treasure_wish',yuanbao=0)
        self.assertEqual(calls,[])
    def test_original_tab_explicit_selection_clears_restore_but_internal_refresh_preserves(self):
        archive._f7_archive_session={'wire_t':1,'effective_group_id':7,'no_wish':True}
        seen=[]
        def original(panel,wire):
            seen.append((archive.offline_archive_context(),panel.draw_type))
            panel.draw_type=wire
        choose=archive.make_archive_direct_selection(original)
        panel=NS(draw_type=1)
        internal=archive.make_archive_preserved_selection(lambda panel:choose(panel,1))
        internal(panel)
        self.assertEqual(seen[-1][0]['effective_group_id'],7)
        choose(panel,1)
        self.assertIsNone(seen[-1][0]);self.assertIsNone(seen[-1][1])
        self.assertEqual(panel.draw_type,1);self.assertIsNone(archive.offline_archive_context())
    def test_destroyed_panel_or_removed_root_never_activates_delayed_restore(self):
        for kind in ('panel','root','owner','proxy','newgroup'):
            archive.offline_archive_clear();h=self.harness()
            with self.subTest(kind=kind),patch.dict(sys.modules,h.modules):
                self.select(h);callback=h.dialogs[-1][1]
                if kind=='panel':h.panel.valid=False
                elif kind=='root':next(n for n in h.created if n is not h.panel._node).removed=True
                elif kind=='owner':h.gg.avatar=object()
                elif kind=='proxy':h.gg._f7_avatar_proxy=NS()
                else:h.proxy.gacha_pools['pools']['119']['group']['id']+=1
                callback()
                self.assertEqual(h.entries,[]);self.assertEqual(h.sync,[])
                self.assertIsNone(archive.offline_archive_context())

    def harness(self,wire=119):
        created=[]
        class Node:
            def __init__(self):self.title='';self.value='';self.children=[];self.removed=False;created.append(self)
            @classmethod
            def create(cls,*args):return cls()
            def setTitleText(self,v):self.title=v
            def addTouchEventListener(self,cb):self.callback=cb
            def addChild(self,n,*a):self.children.append(n)
            def removeAllChildren(self):self.children=[]
            def removeFromParent(self):self.removed=True
            def convertToNodeSpace(self,p):return p
            def getString(self):return self.value
            def setString(self,v):self.value=v
            def __getattr__(self,n):
                if n.startswith('set')or n=='ignoreContentAdaptWithSize':return lambda *a:None
                raise AttributeError(n)
        modules={}
        def module(name,**values):
            obj=ModuleType(name);obj.__path__=[];obj.__dict__.update(values);modules[name]=obj;return obj
        for name in ('com','com.data','com.data.cdata'):module(name)
        module('com.const',SCENE_SUMMON=1)
        for name,data in (('chouka_info',{wire:{}}),('furniture_delivery',{}),('hero',{}),('hero_treasure',{}),('activity_config',{}),('activity_template',{}),('chouka_treasure_wish',self.table)):
            module('com.data.cdata.'+name,data=data)
        module('cocosui',ccui=NS(Button=Node,Layout=Node,TextField=Node,ScrollView=Node,TOUCH_EVENT_ENDED=2),cc=NS(Size=lambda *a:a,Vec2=lambda *a:a,Color3B=lambda *a:a,Color4B=lambda *a:a,Director=NS(getInstance=lambda:NS(getWinSize=lambda:NS(width=1050,height=620))),FileUtils=NS(getInstance=lambda:NS(isFileExist=lambda p:True))))
        dialogs=[];entries=[];sync=[];owner=object();pools=self.pools(wire,self.group())
        proxy=NS(owner=owner,gacha_pools=pools,sync_gacha_native_state=lambda wire=None:sync.append(archive.offline_archive_context(wire)))
        gg=module('gg',avatar=owner,_f7_avatar_proxy=proxy,city_container=NS(get_scene_by_key=lambda k:1,check_scene=lambda s:True),ui=NS(projplistinfo={},panels=NS(common_confirm=NS(notify_confirm=lambda msg,cb,**kw:dialogs.append((msg,cb,kw))))))
        panel=NS(_node=Node(),on_chouka_btn_click=lambda w:entries.append((w,archive.offline_archive_context())),_on_open_go_click=lambda:entries.append('Go'))
        return NS(created=created,modules=modules,dialogs=dialogs,entries=entries,sync=sync,owner=owner,proxy=proxy,gg=gg,panel=panel)
    def select(self,h,wire=119):
        archive.show_gacha_archive(h.panel)
        scroll=next(n for n in h.created if any('[t=%s]'%wire in c.title for c in n.children))
        next(n for n in scroll.children if '[t=%s]'%wire in n.title).callback(None,2)
        key='wish_id='if wire==5 else'hero_wish_id='
        next(n for n in scroll.children if key in n.title).callback(None,2)
        return scroll
    def test_direct_reentry_syncs_canonical_old_period_before_original_poster(self):
        h=self.harness(5);ids=sorted(k for k,r in self.table.items()if r.get('drawType')==5)
        old=ids[0];new=ids[-1]
        h.proxy.gacha_pools['pools']['5']['group']['special_context']={'policy':'offline-original-display-probability-treasure-wish-v1','wish_id':old}
        archive._f7_archive_session=archive.archive_make_session({'wire_t':5,'category':'hero_treasure'},self.table,new)
        seen=[];panel=NS(draw_type=5)
        with patch.dict(sys.modules,h.modules):
            choose=archive.make_archive_direct_selection(lambda p,w:seen.append((len(h.sync),archive.offline_archive_context(w))))
            choose(panel,5)
            self.assertEqual(seen[0][0],1)
            self.assertEqual(seen[0][1]['wish_id'],old)
            self.assertEqual(h.sync[0]['wish_id'],old)
            self.assertIsNone(archive._f7_archive_session)

    def test_actual_t5_restore_label_and_entry_keep_saved_epoch(self):
        h=self.harness(5);ids=sorted(k for k,r in self.table.items()if r.get('drawType')==5)
        old=ids[-1]
        h.proxy.gacha_pools['pools']['5']['group']['special_context']={'policy':'offline-original-display-probability-treasure-wish-v1','wish_id':old}
        before=copy.deepcopy(h.proxy.gacha_pools)
        with patch.dict(sys.modules,h.modules):
            self.select(h,5)
            self.assertEqual(h.entries,[]);self.assertEqual(h.sync,[])
            message,restore,kwargs=h.dialogs[-1]
            self.assertIn(str(old),message)
            self.assertIn(archive.archive_date(self.table[old]['begin_time']),message)
            restore()
            self.assertEqual(h.entries[0][1]['wish_id'],old)
            self.assertEqual(h.sync[0]['wish_id'],old)
            self.assertEqual(h.proxy.gacha_pools,before)

    def test_actual_cocos_conflict_before_mutation_cancel_restore_and_stale_callbacks(self):
        h=self.harness();prior={'wire_t':265,'category':'hero_treasure'};archive._f7_archive_session=copy.deepcopy(prior)
        with patch.dict(sys.modules,h.modules):
            scroll=self.select(h)
            self.assertEqual(h.entries,[]);self.assertEqual(h.sync,[]);self.assertEqual(archive.offline_archive_context(),prior)
            self.assertEqual(h.dialogs[-1][2]['confirm_label'],'恢复旧卡组')
            h.dialogs[-1][2]['cancel_cb']()
            self.assertEqual(h.entries,[]);self.assertEqual(archive.offline_archive_context(),prior)
            next(n for n in scroll.children if 'hero_wish_id='in n.title).callback(None,2)
            stale=h.dialogs[-1][1];h.proxy.gacha_pools['pools']['119']['group']['id']=8;stale()
            self.assertEqual(h.entries,[]);self.assertEqual(h.sync,[])
            next(n for n in scroll.children if 'hero_wish_id='in n.title).callback(None,2)
            owner_stale=h.dialogs[-1][1];h.gg.avatar=object();owner_stale()
            self.assertEqual(h.entries,[]);h.gg.avatar=h.owner
            next(n for n in scroll.children if 'hero_wish_id='in n.title).callback(None,2)
            restore=h.dialogs[-1][1];before=copy.deepcopy(h.proxy.gacha_pools);restore();restore()
            self.assertEqual(h.proxy.gacha_pools,before)
            self.assertEqual(h.entries[0][0],119);self.assertEqual(h.entries[1],'Go');self.assertEqual(len(h.sync),1)
            self.assertTrue(h.entries[0][1]['no_wish']);self.assertEqual(h.entries[0][1]['effective_group_id'],8)
            getter=archive.make_archive_wish_group_getter(lambda *a:{'leaked':True},self.table)
            self.assertEqual(getter(None,119),{})
            h.proxy.gacha_pools['pools']['119']['group']=None
            self.assertTrue(archive.offline_archive_context()['expired_restore'])
            self.assertFalse(archive.offline_archive_authorized(119))
