"""Free costs through the actual old/new furniture panel refresh bodies."""
import copy
from pathlib import Path
import re
import sys
import textwrap
from types import SimpleNamespace
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'runtime'),str(ROOT/'analysis/research-agent')]
from offline_gacha_costs import make_free_furniture_consume
from read_literal_marshal import read


def method(path,name,namespace):
    source=path.read_text()
    start=source.index('    def '+name+'(')
    following=re.search(r'\n    (?:def |@)',source[start+1:])
    body=source[start:start+1+following.start()] if following else source[start:]
    exec(textwrap.dedent(body),namespace)
    return namespace[name]


class NativeBoolNode:
    def __init__(self): self.visible=None;self.icons=[]
    def setVisible(self,value):
        if type(value) is not bool: raise TypeError('native bool binding rejects non-bool')
        self.visible=value
    def setBright(self,value): self.setVisible(value)
    def set_icon(self,*args): self.icons.append(args)


class OriginalFurnitureUiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        base=ROOT/'analysis/android640-scripts/com/data/cdata'
        cls.info=read(base/'chouka_info.marshal')
        cls.delivery=read(base/'furniture_delivery.marshal')

    def setUp(self):
        self.balance=0
        self.const=SimpleNamespace(LuckyDrawConsumeStyle=SimpleNamespace(
            STYLE_FURNITURE_ONCE=6,STYLE_FURNITURE_TEN=7),
            SUMMON_FURNITURE_LIANCHOU_TIMES=10,MAX_FURNITURE_TIMES_DAY=500)
        self.data=SimpleNamespace(getFurnitureLianchouTimes=lambda wire:0,
                                  getCurCardTimesDay=lambda wire:0)
        self.gg=SimpleNamespace(avatar=SimpleNamespace(luckyDrawData=self.data,
            findItemByID=lambda *args,**kw:(self.balance,)))
        namespace=dict(gg=self.gg,const=self.const,
            CHOUKA_INFO_DATA=SimpleNamespace(data=self.info),
            FURNITURE_DELIVERY_DATA=SimpleNamespace(data=self.delivery))
        self.original=method(ROOT/'analysis/research-agent/LuckyDrawData.py',
                             'getFurnitureCardConsume',namespace)
        self.free=make_free_furniture_consume(self.original,self.info)
        self.data.getFurnitureCardConsume=lambda wire,**kw:self.free(self.data,wire,**kw)

    def panel(self,wire,new):
        p=SimpleNamespace(curr_type=wire,fixed_type=0)
        for name in ('once_cost_free_txt','ten_cost_1','ten_cost_2','btn_once'):
            node=NativeBoolNode()
            setattr(p,name,[node] if new else node)
        for name in ('once_cost_comp','ten_cost_1_comp'):
            comp=NativeBoolNode();comp._node=NativeBoolNode()
            setattr(p,name,[comp] if new else comp)
        comps=[NativeBoolNode(),NativeBoolNode()]
        p.ten_cost_2_comps=[comps] if new else comps
        if new:p.show_discount=[[NativeBoolNode() for _ in range(3)]]
        else:
            for name in ('first_chou','second_chou','third_chou'):setattr(p,name,NativeBoolNode())
        return p

    def refresh(self,new):
        return method(ROOT/('analysis/decompiled/archive_city_room_danchi_new.py' if new
                           else 'analysis/decompiled/archive_city_room_danchi.py'),
                      'refresh_btn_card',dict(gg=self.gg,const=self.const))

    def test_actual_both_original_refresh_methods_reproduce_empty_cost_binding_failure(self):
        self.data.getFurnitureCardConsume=lambda *a,**kw:[]
        for new in (False,True):
            with self.assertRaisesRegex(TypeError,'native bool'):
                self.refresh(new)(self.panel(106,new))

    def test_all_original_furniture_cost_shapes_stay_nonempty_and_zero_in_both_panels(self):
        configs=copy.deepcopy(self.info)
        delivery=copy.deepcopy(self.delivery)
        wires=[w for w,r in self.info.items()if r.get('poolType')==2]
        self.assertEqual(len(wires),41)
        for balance in (0,1,100):
            self.balance=balance
            for wire in wires:
                for style in (6,7):
                    original=self.original(self.data,wire,_style=style)
                    costs=self.data.getFurnitureCardConsume(wire,_style=style)
                    self.assertTrue(costs)
                    self.assertEqual(costs,[(iid,0)for iid,num in original])
                for new in (False,True):
                    panel=self.panel(wire,new)
                    self.refresh(new)(panel)
                    free=panel.once_cost_free_txt[0] if new else panel.once_cost_free_txt
                    self.assertTrue(free.visible)
        self.assertEqual(configs,self.info)
        self.assertEqual(delivery,self.delivery)

    def test_other_pool_costs_delegate_without_mutating_original_result(self):
        original=[(24,10)]
        fn=make_free_furniture_consume(lambda *a,**kw:original,self.info)
        self.assertIs(fn(None,1),original)
        self.assertEqual(fn(None,106),[(24,0)])
        self.assertEqual(original,[(24,10)])


if __name__=='__main__':unittest.main()
