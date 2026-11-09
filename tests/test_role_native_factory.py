"""Execute extracted original actor calculators in a detached host harness.

This verifies calculator inputs/isolation and original fixed-dump semantics;
resource availability is a host stub and does not establish native scene entry.
"""
import ast
import copy
import math
from pathlib import Path
import sys
from types import ModuleType,SimpleNamespace
import unittest
from unittest.mock import patch
import warnings
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'runtime'),str(ROOT/'tests'),str(ROOT/'analysis/research-agent')]
import offline_role_mission as role
import test_role_mission as fixtures
from read_literal_marshal import read


def extracted_classes(path,names,namespace):
    with warnings.catch_warnings():
        warnings.simplefilter('ignore',DeprecationWarning)
        from lib2to3.refactor import RefactoringTool,get_fixers_from_package
        translated=str(RefactoringTool(get_fixers_from_package('lib2to3.fixes')).refactor_string(path.read_text(),str(path)))
    tree=ast.parse(translated)
    selected=[node for node in tree.body if isinstance(node,ast.ClassDef) and node.name in names]
    exec(compile(ast.Module(body=selected,type_ignores=[]),str(path),'exec'),namespace,namespace)


def original_constant_literals(path):
    source=path.read_text().replace('return locals()','')
    tree=ast.parse(source)
    values={}
    for node in tree.body:
        if isinstance(node,ast.Assign) and len(node.targets)==1 and isinstance(node.targets[0],ast.Name):
            try:values[node.targets[0].id]=ast.literal_eval(node.value)
            except (ValueError,TypeError):pass
    return values


class RoleNativeFactoryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tables=fixtures.original_role_tables()
        base=ROOT/'analysis/android640-scripts/com/data/cdata'
        cls.extra={'third':read(base/'hero_treasure_third_attr.marshal')}

    def setUp(self):
        def no_owned(*args,**kwargs):raise AssertionError('Trial read permanent/account contribution')
        self.owner=SimpleNamespace(id='actual-owner',level=7,heroMgrData=SimpleNamespace(getHero=no_owned,
            getArtifactInfo=no_owned,getAwakeStage=no_owned,getAureoleTrick=no_owned),calcRoomSkillAttr=no_owned)
        self.gg=SimpleNamespace(avatar=self.owner)
        values=original_constant_literals(ROOT/'reports/astra-original-CombatAttrs-constants.txt')
        values['INDEX_TO_NAME']={value:key for key,value in values['NAME_TO_INDEX'].items()}
        values['ALL_VALID_ATTRS']=set().union(*(values[name] for name in ('BASE_SECOND_ATTRS','DELTA_ATTRS','BONUS_SECOND_ATTRS','THIRD_ATTRS','HIDDEN_ATTRS','DRAMA_ATTRS')))
        self.const=SimpleNamespace(CombatAttrs=SimpleNamespace(**values),
            CalcTreasureFixAttr=SimpleNamespace(**original_constant_literals(ROOT/'reports/astra-original-CalcTreasureFixAttr-constants.txt')),
            ItemType=SimpleNamespace(COMMON=1,HERO_TREASURE=5),TradeType=SimpleNamespace(FORBID=3),TreasureRarity=SimpleNamespace(B=1))
        def add(left,right):
            result=dict(left)
            for key,value in right.items():result[key]=result.get(key,0)+value
            return result
        utils=SimpleNamespace(dict_add=add)
        self.items=[]
        class DetachedInv:
            def __init__(self,invId=0):self.inv=[];self.invId=invId;self.maxCost=25
            def insertItem(inner,item):inner.inv.append(item);self.items.append(item)
        namespace={'__name__':'original_detached_calculators','gg':self.gg,'const':self.const,'math':math,
            'utils':utils,'UtilsWeakRef':SimpleNamespace(proxy=lambda owner:owner),'InvData':SimpleNamespace(InvData=DetachedInv)}
        for original,name in [('HeroDataMod','hero'),('StarAttrDataMod','hero_star_attr'),('StarSkillDataMod','hero_star_skill'),
            ('ArtifactAttrDataMod','hero_artifact_attr'),('HeroPointData','hero_artifact_allot_lv_point_data'),
            ('TreasureSuitDataMod','hero_treasure_suit'),('LIBERATE_TUPO','liberate_tupo'),('LIBERATE_LV','liberate_lv'),
            ('ITEM_DATA','item_data'),('TreasureDataMod','hero_treasure'),('TreasureExclusiveDataMod','treasure_exclusive')]:
            namespace[original]=SimpleNamespace(data=self.tables[name])
        namespace['ArtifactIncreaseDataMod']=SimpleNamespace(data={})
        namespace['TreasureThirdAttrData']=SimpleNamespace(data=self.extra['third'])
        namespace['AWAKE_CONSUME_DATA']=SimpleNamespace(data={})
        extracted_classes(ROOT/'analysis/decompiled/HeroMgrData.py',('HeroData','ArtifactData','SlotData'),namespace)
        extracted_classes(ROOT/'analysis/decompiled/ItemData.py',('ItemData',),namespace)
        self.namespace=namespace
        identity=SimpleNamespace(id2str=str,str2id=lambda text:text,genid=lambda:'host-only-id')
        skin_namespace={'__name__':'original_detached_skin','IdManager':identity,
            'helpers':SimpleNamespace(toStrKeyDict=lambda value:{str(key):item for key,item in value.items()})}
        extracted_classes(ROOT/'analysis/decompiled/SkinData.py',('SkinData',),skin_namespace)
        namespace['IdManager']=identity
        self.modules={name:ModuleType(name) for name in ('entity','entity.avatar_attrs','entity.avatar_attrs.HeroMgrData',
            'entity.avatar_attrs.ItemData','common','common.IdManager','com','com.utils','com.utils.SkinData',
            'com.data','com.data.cdata','com.data.cdata.skin','com.data.cdata.ui_model_data','C_file')}
        self.modules['entity.avatar_attrs.HeroMgrData'].HeroData=namespace['HeroData']
        self.modules['entity.avatar_attrs.ItemData'].ItemData=namespace['ItemData']
        self.modules['common.IdManager'].IdManager=identity
        self.modules['com.utils.SkinData'].SkinData=skin_namespace['SkinData']
        self.modules['com.data.cdata.skin'].data=self.tables['skin']
        self.modules['com.data.cdata.ui_model_data'].data={}
        self.modules['C_file'].find_res_file=lambda *args:'host-resource-stub'
        context=patch.dict(sys.modules,self.modules);context.start();self.addCleanup(context.stop)
        context=patch.object(role,'role_mission_tables',lambda scene=None:self.tables);context.start();self.addCleanup(context.stop)

    def active(self,scene):
        hero=list(self.tables['mission'][scene]['defaultHeroes'])
        descriptor=role.compile_role_mission(scene,hero,self.tables)
        return {'fight_id':'actual-host-fight','party_kind':'trial','role_owner':'actual-owner',
            'request':{'t':2,'s':scene,'h':hero,'d':{}},'role_mission':descriptor,'hero_level':100 if scene>400 else 60}

    def project(self,scene):
        return role.native_role_combat_data(self.owner,self.active(scene),self.tables['mission'][scene])

    def test_original_fixed_hero14_calculators_without_owned_or_room_aureole_access(self):
        combat=self.project(315);data=combat['heroes'][str(('',14))]
        self.assertEqual(data['lv'],60);self.assertEqual(data['s'][0],[[1130,4],[1132,4],[1133,4],[1134,4]])
        self.assertEqual(data['s'][1],[]);self.assertEqual(data['as'],0);self.assertEqual(data['ai'],[False,0])
        self.assertEqual(data['t'],[]);self.assertTrue(data['d']['_base_max_hp']>0)
        self.assertEqual(combat['skins'][0]['i'],14);self.assertEqual(combat['monster_lv'],1)
        self.assertEqual(self.items,[])
        before=copy.deepcopy(combat);self.owner.level=100
        self.assertEqual(self.project(315),before)

    def test_original_15_fixed_items_duplicates_unique_instances_no_capacity_enforcement(self):
        combat=self.project(426);data=combat['heroes'][str(('',10))]
        self.assertEqual(data['lv'],100);self.assertIn([8024,4],data['s'][1])
        self.assertEqual(len(self.items),15);self.assertEqual(len({item.uuid for item in self.items}),15)
        self.assertEqual(sum(item.treasureCost for item in self.items),42)
        self.assertEqual(combat['skins'][0]['i'],10);self.assertEqual(data['as'],0)
        self.assertTrue(data['d']['_base_phy_att_str']>0)
        # Explicit fixed-dump policy: generator18038 has3920 but dump lacksx.
        exclusive=self.items[0]
        self.assertEqual(self.tables['hero_treasure_generate'][18038]['treasure_exp'],3920)
        self.assertEqual(exclusive.treasureExp,0)
        self.assertEqual(exclusive.treasureExpDict.get('stage'),1)
        self.assertEqual(data['ai'],[True,1]);self.assertEqual(set(data['t']),{184,85,79})
        self.assertNotIn('_base_max_hp',exclusive.treasureFixAttr)  # a35 is ignored by original loader

    def test_source_catalog_drift_and_resource_failure_reject_before_owned_access(self):
        active=self.active(315)
        self.tables=copy.deepcopy(self.tables);self.tables['hero_star_skill'][(14,4,4)]['cumSkills'][1130]=3
        with self.assertRaises(ValueError):role.native_role_combat_data(self.owner,active,self.tables['mission'][315])
        self.tables['hero_star_skill'][(14,4,4)]['cumSkills'][1130]=4
        self.modules['C_file'].find_res_file=lambda *args:None
        with self.assertRaisesRegex(ValueError,'resource'):role.native_role_combat_data(self.owner,active,self.tables['mission'][315])


if __name__=='__main__':unittest.main()
