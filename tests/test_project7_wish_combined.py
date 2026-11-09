"""Real frozen draw/friend/selector/family installers plus Wish class records.
Host-only admission fixture, inert native UI. Public policy remains closed.
"""
import _paths  # noqa: E402,F401
import hashlib,sys,types,unittest
from unittest.mock import patch
from tests import test_project7_dynamic_ui_families as family
from tests.test_project7_wish_ui import ROOT,NS,original,wish
from tests.test_project7_wish_transport import original_class
from project7_wish_ui_policy import ui_policy,canonical
class CombinedTests(unittest.TestCase):
 begin=family.FamilyConsumerTests.begin;retired=family.FamilyConsumerTests.retired;click=family.FamilyConsumerTests.click
 actor=family.FamilyConsumerTests.actor;grid=family.FamilyConsumerTests.grid;comp=family.FamilyConsumerTests.comp;panel=family.FamilyConsumerTests.panel;box=family.FamilyConsumerTests.box
 def setUp(self):
  family.FamilyConsumerTests.setUp(self)
  self.wp=ui_policy() # real source policy; public IDs remain empty, host pending only
  self.member=NS(check=lambda:True,transport=lambda actor:self.channel);self.channel=object()
  self.gg.avatar.luckyDrawData.activity_data.update({t:NS(card_times=0,is_open_file=True,choose_treasure=[0,0,0],treasure_wish={},wish_info={},jiaozhi_count={},jiaozhi_rewards={},replace_count={})for t in wish._IDS});self.gg.avatar.luckyDrawData.inc_up_cnt={1:0}
  env=dict(self.env);env['Panel']=self.Box
  for name in wish._METHODS[2]:setattr(self.Box,name,original('analysis/original-py-640/cocos/panels/card_box.py',name,env))
  for name in ('getTreasureWishStep','getTreasureWishProb','getTreasureWishVal','getChooseTreasure','getWishGroupInfoDict','getWishGroupListTotalFixedRate','getWishGroupMaxCount','getWishGroupProbDicts','getWishGroupValueDict'):
   setattr(self.gg.avatar.luckyDrawData,name,types.MethodType(original('analysis/original-py-640/entity/avatar_attrs/LuckyDrawData.py',name,env),self.gg.avatar.luckyDrawData))
  class Base:
   def __getitem__(panel,key):return panel.nodes.setdefault(key,family.old.Widget())
  env['ui_panel']=NS(UIPanel=Base);self.ym=types.ModuleType('cocos.panels.card_yingzhuang');self.jm=types.ModuleType('cocos.panels.card_jiaozhi')
  self.ym.Panel=original_class('cocos/panels/card_yingzhuang.py','Panel',dict(env));self.jm.Panel=original_class('cocos/panels/card_jiaozhi.py','Panel',dict(env))
  self.modules=patch.dict(sys.modules,{self.ym.__name__:self.ym,self.jm.__name__:self.jm});self.modules.start();self.addCleanup(self.modules.stop)
  self.owner=wish.install(canonical(self.wp),self.dynamic.history_avatar_type,self.state,self.dynamic,self.member)
 def test_exact_companion_records_reinstall_and_all_detail_delegate_indices(self):
  self.assertIs(self.owner.current(),self.gg);self.assertIs(self.dynamic.current(),self.gg);self.assertIs(self.selector.current(),self.gg);self.assertIs(self.drawstate.current(),self.gg)
  self.assertIs(wish.install(canonical(self.wp),self.dynamic.history_avatar_type,self.state,self.dynamic,self.member),self.owner)
  self.assertEqual(self.owner.detail_indices,(0,2,6))
  for t in wish._IDS:
   self.assertEqual(self.dynamic.detail_delegate(t),self.owner.invoke_detail)
   self.assertTrue(self.drawstate.check_request_guard(t,self.gg.avatar))
  # No class method owned by families was replaced by Wish.
  for cls,name,fn in self.dynamic.records:self.assertIs(wish._raw(getattr(cls,name)),fn)
 def test_original_activity_hide_delegates_same_scope_then_stale_timer_no_destroy(self):
  # Existing pending is authority for this finite room path, not public enablement.
  Activity=self.dynamic.classes[6];Activity.PANEL_TYPE_DYNAMIC=1;Activity.PANEL_TYPE_STATIC=2;panel=Activity();panel.valid=True;panel._node=family.old.Widget();panel.on_init();panel.cur_drawtype=119;panel.cur_activity_id=25;panel.panel_type=Activity.PANEL_TYPE_DYNAMIC;panel.anim={'end':[]};closed=[];panel.destroy=lambda:closed.append(True)
  self.gg.ui.panels.card_activity_base=panel
  panel.notify_hide();self.assertTrue(panel.cover);callback=self.timers[-1]
  # old show cannot destroy a reused room after new on_init generation.
  panel.on_init();panel.cur_drawtype=119;callback();self.assertEqual(closed,[])
if __name__=='__main__':unittest.main()
