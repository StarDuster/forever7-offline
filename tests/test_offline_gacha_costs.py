import sys
from pathlib import Path
from types import SimpleNamespace, ModuleType
from unittest.mock import patch
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'runtime'))
from offline_gacha_costs import make_scoped_gacha_coin_check, make_scoped_gacha_request, install_gacha_dedicated_costs

class ScopedDrawCosts(unittest.TestCase):
    def test_only_original_draw_request_scope_is_free_and_exception_restores_scope(self):
        class Avatar:
            def coin(self,cost):return False
            def draw(self):return self.coin(200)
            def broken(self):
                if not self.coin(200):raise AssertionError('not scoped')
                raise ValueError('original request failed')
        Avatar.coin=make_scoped_gacha_coin_check(Avatar.coin)
        Avatar.draw=make_scoped_gacha_request(Avatar.draw,lambda avatar:avatar)
        Avatar.broken=make_scoped_gacha_request(Avatar.broken,lambda avatar:avatar)
        avatar=Avatar()
        self.assertFalse(avatar.coin(200));self.assertTrue(avatar.draw());self.assertFalse(avatar.coin(200))
        with self.assertRaises(ValueError):avatar.broken()
        self.assertEqual(avatar._f7_draw_coin_scope,0)
        self.assertFalse(avatar.coin(1))
    def test_native_daily_cap_check_runs_inside_free_scope(self):
        avatar=SimpleNamespace(_f7_draw_coin_scope=0)
        def can(data):
            if data.daily>=100:return False
            return avatar._f7_draw_coin_scope>0
        checked=make_scoped_gacha_request(can,lambda data:avatar)
        self.assertTrue(checked(SimpleNamespace(daily=99)))
        self.assertFalse(checked(SimpleNamespace(daily=100)))
        self.assertEqual(avatar._f7_draw_coin_scope,0)

    def test_production_installer_preserves_friend_caps_and_only_furniture_config_cost(self):
        class Avatar:
            def checkFriendCoin(self,n):return False
            def checkNewFriendCoin(self,n):return False
            def requestLuckyDrawFriendCard(self):return self.checkFriendCoin(200)
            def requestLuckyDrawNewFriendCard(self):return self.checkNewFriendCoin(200)
        avatar=Avatar()
        class Data:
            friend_draw_count=0
            def canSummonFriend(self):return self.friend_draw_count<100 and avatar.checkFriendCoin(200)
            def getLuckyDrawFriendConsume(self,*a):return [(179,200)]
            def checkFurnitureCardCost(self,t,*a,**kw):return False
            def getFurnitureCardConsume(self,t,*a,**kw):return [(24,10)]
        modules={name:ModuleType(name) for name in ('gg','entity','entity.ClientAvatar','entity.avatar_attrs','entity.avatar_attrs.LuckyDrawData','com','com.data','com.data.cdata','com.data.cdata.chouka_info')}
        modules['gg'].avatar=avatar;modules['entity.ClientAvatar'].ClientAvatar=Avatar;modules['entity.avatar_attrs.LuckyDrawData'].LuckyDrawData=Data
        modules['entity'].ClientAvatar=modules['entity.ClientAvatar'];modules['entity'].avatar_attrs=modules['entity.avatar_attrs'];modules['entity.avatar_attrs'].LuckyDrawData=modules['entity.avatar_attrs.LuckyDrawData']
        modules['com'].data=modules['com.data'];modules['com.data'].cdata=modules['com.data.cdata'];modules['com.data.cdata'].chouka_info=modules['com.data.cdata.chouka_info'];modules['com.data.cdata.chouka_info'].data={106:{'poolType':2},1:{'poolType':1}}
        with patch.dict(sys.modules,modules):
            install_gacha_dedicated_costs()
            self.assertTrue(avatar.requestLuckyDrawFriendCard());self.assertTrue(avatar.requestLuckyDrawNewFriendCard())
            self.assertFalse(avatar.checkFriendCoin(1));self.assertFalse(avatar.checkNewFriendCoin(1))
            data=Data();self.assertTrue(data.canSummonFriend());data.friend_draw_count=100;self.assertFalse(data.canSummonFriend())
            self.assertEqual(data.getLuckyDrawFriendConsume(),[])
            self.assertTrue(data.checkFurnitureCardCost(106));self.assertEqual(data.getFurnitureCardConsume(106),[(24,0)])
            self.assertFalse(data.checkFurnitureCardCost(1));self.assertEqual(data.getFurnitureCardConsume(1),[(24,10)])

if __name__=='__main__':unittest.main()
