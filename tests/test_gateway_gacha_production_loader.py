"""Original archive self-choice RPC through the actual production table loader.

The base integration harness installs original-table module fixtures. This class
explicitly removes its inherited gacha_tables lambda: every test calls the real
LocalProxy.gacha_tables method, including reliable RPC and restarted instances.
"""
import copy
import sys
from collections.abc import Mapping
from unittest.mock import patch
import test_gacha_gateway_pools as base
from offline_gacha_archive import archive_catalog,archive_make_session
from offline_gacha_special import original_self_choose_hash

gateway,rewards=base.gateway,base.rewards

class NativeTaggedRow(Mapping):
    """Native taggeddict semantics: mapping values, identity equality, plain deepcopy."""
    def __init__(self,values):self.values=dict(values)
    def __getitem__(self,key):return self.values[key]
    def __iter__(self):return iter(self.values)
    def __len__(self):return len(self.values)
    def __eq__(self,other):return self is other
    def __ne__(self,other):return self is not other
    def __deepcopy__(self,memo):return copy.deepcopy(self.values,memo)

class ProductionGachaLoaderTests(base.GatewayOriginalPoolIntegration):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.tables=dict(cls.tables)
        for name in ('activity_config','activity_template','hero_self_choose_info'):
            cls.tables[name]=rewards.read(rewards.ROOT/'analysis/android640-scripts/com/data/cdata'/(name+'.marshal'))
    def setUp(self):
        super().setUp()
        del self.proxy.__dict__['gacha_tables']
        self.assertIs(self.proxy.gacha_tables.__func__,gateway.LocalProxy.gacha_tables)
        tables=self.proxy.gacha_tables()
        row=next(row for row in archive_catalog(tables['chouka_info'])if row['wire_t']==265)
        self.archive=archive_make_session(row,{},rotation_uaid=175,
            rotations=tables['activity_config'],templates=tables['activity_template'])
    def native_tagged_archive(self):
        rows=dict(self.tables['activity_config'])
        rows[175]=NativeTaggedRow(rows[175])
        self.table('activity_config',rows)
        tables=self.proxy.gacha_tables()
        self.assertIs(tables['activity_config'][175],rows[175])
        row=next(r for r in archive_catalog(tables['chouka_info'])if r['wire_t']==265)
        archive=archive_make_session(row,{},rotation_uaid=175,
            rotations=tables['activity_config'],templates=tables['activity_template'])
        self.assertNotIsInstance(rows[175],dict)
        self.assertIs(type(archive['rotation']),dict)
        self.assertFalse(rows[175]==archive['rotation'])
        self.assertEqual(dict(rows[175].items()),archive['rotation'])
        for key,value in rows[175].items():
            self.assertIs(type(value),type(archive['rotation'][key]))
            self.assertEqual(value,archive['rotation'][key])
        return archive
    def reply(self):
        return next(payload for name,payload in reversed(self.owner.replies)if name=='replySetChooseHeroes')
    def choose(self,request_id=265175):
        self.owner.replies=[]
        self.proxy.reliable_call({'w':{'r':request_id,'m':'setChooseHeroes','p':{'t':265,'h':[81,33]}}})
        return self.reply()
    def test_actual_production_loader_loads_original_period_and_template(self):
        tables=self.proxy.gacha_tables()
        self.assertIs(tables['activity_config'],self.tables['activity_config'])
        self.assertIs(tables['activity_template'],self.tables['activity_template'])
        self.assertEqual(tables['activity_config'][175]['self_choose_S'],(135,33,123))
        self.assertEqual(tables['activity_config'][175]['self_choose_A'],(117,81,109))
        template=tables['activity_config'][175]['tmp_id']
        self.assertEqual(tables['activity_template'][template]['tmp_type'],88)
        self.assertEqual(self.archive['rotation'],tables['activity_config'][175])
    def test_actual_period175_reliable_choice_replay_and_restart(self):
        with patch.object(gateway,'offline_archive_context',return_value=self.archive):
            result=self.choose()
            self.assertEqual(result['r'],0)
            stamp=original_self_choose_hash(self.proxy.gacha_tables()['chouka_info'][265])
            self.assertEqual(result['h'],[stamp,33,81])
            self.assertEqual(self.owner.luckyDrawData.activity_data[265].choose_heroes,[stamp,33,81])
            saved=copy.deepcopy(self.proxy.progress_snapshot())
            self.choose()
            self.assertEqual(self.proxy.progress_snapshot(),saved)
            restarted=gateway.LocalProxy(None,self.owner,persistent=True)
            self.assertIs(restarted.gacha_tables.__func__,gateway.LocalProxy.gacha_tables)
            self.assertEqual(restarted.gacha_pools,self.proxy.gacha_pools)
            restarted.sync_gacha_native_state()
            self.assertEqual(self.owner.luckyDrawData.activity_data[265].choose_heroes,[stamp,33,81])
            self.assertIs(restarted.gacha_tables()['activity_config'],self.tables['activity_config'])
    def test_actual_period175_disk_failure_rejects_without_choice_or_receipt(self):
        before=copy.deepcopy(self.proxy.progress_snapshot())
        with patch.object(gateway,'offline_archive_context',return_value=self.archive),patch.object(self.proxy._store,'write',side_effect=OSError('full')):
            result=self.choose()
        self.assertNotEqual(result['r'],0)
        self.assertEqual(self.proxy.progress_snapshot(),before)
        restarted=gateway.LocalProxy(None,self.owner,persistent=True)
        self.assertEqual(restarted.gacha_pools,before['gacha_pools'])
    def test_native_tagged_identity_row_reliable_save_replay_and_restart(self):
        archive=self.native_tagged_archive()
        with patch.object(gateway,'offline_archive_context',return_value=archive):
            result=self.choose()
            self.assertEqual(result['r'],0)
            stamp=original_self_choose_hash(self.proxy.gacha_tables()['chouka_info'][265])
            self.assertEqual(result['h'],[stamp,33,81])
            saved=copy.deepcopy(self.proxy.progress_snapshot())
            self.choose()
            self.assertEqual(self.proxy.progress_snapshot(),saved)
            restarted=gateway.LocalProxy(None,self.owner,persistent=True)
            self.assertIs(restarted.gacha_tables.__func__,gateway.LocalProxy.gacha_tables)
            self.assertIsInstance(restarted.gacha_tables()['activity_config'][175],NativeTaggedRow)
            self.assertEqual(restarted.gacha_pools,self.proxy.gacha_pools)
            restarted.sync_gacha_native_state()
            self.assertEqual(self.owner.luckyDrawData.activity_data[265].choose_heroes,[stamp,33,81])
    def test_native_tagged_row_rejects_every_changed_field_and_key_or_tuple_drift(self):
        archive=self.native_tagged_archive()
        contexts=[]
        for key,value in archive['rotation'].items():
            changed=copy.deepcopy(archive)
            changed['rotation'][key]=value+1 if type(value)is int else value+(999,)
            contexts.append((key,changed))
        extra=copy.deepcopy(archive);extra['rotation']['unverified_extra']=1
        contexts.append(('extra-key',extra))
        missing=copy.deepcopy(archive);missing['rotation'].pop('payment_time')
        contexts.append(('missing-key',missing))
        list_changed=copy.deepcopy(archive);list_changed['rotation']['self_choose_A']=list(list_changed['rotation']['self_choose_A'])
        contexts.append(('tuple-to-list',list_changed))
        before=copy.deepcopy(self.proxy.progress_snapshot())
        for index,(label,context) in enumerate(contexts):
            with self.subTest(label=label),patch.object(gateway,'offline_archive_context',return_value=context):
                self.assertEqual(self.choose(265176+index)['r'],1812)
                self.assertEqual(self.proxy.progress_snapshot(),before)
    def test_missing_production_period_table_reproduces1812_without_commit(self):
        name='com.data.cdata.activity_config'
        before=copy.deepcopy(self.proxy.progress_snapshot())
        with patch.dict(sys.modules,{name:None}),patch.object(gateway,'offline_archive_context',return_value=self.archive):
            self.assertEqual(self.proxy.gacha_tables()['activity_config'],{})
            self.assertEqual(self.choose()['r'],1812)
        self.assertEqual(self.proxy.progress_snapshot(),before)
    def test_changed_archive_period_content_rejected1812_without_commit(self):
        context=copy.deepcopy(self.archive)
        context['rotation']['self_choose_A']=(81,)
        before=copy.deepcopy(self.proxy.progress_snapshot())
        with patch.object(gateway,'offline_archive_context',return_value=context):
            self.assertEqual(self.choose()['r'],1812)
        self.assertEqual(self.proxy.progress_snapshot(),before)

for name in list(vars(base.GatewayOriginalPoolIntegration)):
    if name.startswith('test_'):setattr(ProductionGachaLoaderTests,name,None)
