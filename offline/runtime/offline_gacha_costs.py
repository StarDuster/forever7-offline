# -*- coding: ascii -*-
"""Authorized free draw costs, scoped to original draw call stacks only."""


def make_scoped_gacha_coin_check(original):
    def checked(self, *args, **kwargs):
        if getattr(self, '_f7_draw_coin_scope', 0):
            return True
        return original(self, *args, **kwargs)
    return checked


def make_scoped_gacha_request(original, avatar_provider):
    def requested(self, *args, **kwargs):
        avatar = avatar_provider(self)
        previous = getattr(avatar, '_f7_draw_coin_scope', 0)
        avatar._f7_draw_coin_scope = previous + 1
        try:
            return original(self, *args, **kwargs)
        finally:
            avatar._f7_draw_coin_scope = previous
    return requested


def make_free_furniture_consume(original, configurations):
    def consume(self, wire_t, *args, **kwargs):
        costs = original(self, wire_t, *args, **kwargs)
        if configurations.get(wire_t, {}).get('poolType') == 2:
            # Stock old/new panels require a nonempty currency list, even free.
            return [(item, 0) for item, amount in costs]
        return costs
    return consume


def install_gacha_dedicated_costs():
    import gg
    from entity.ClientAvatar import ClientAvatar
    from entity.avatar_attrs.LuckyDrawData import LuckyDrawData
    import com.data.cdata.chouka_info as original_info
    if getattr(ClientAvatar, '_f7_dedicated_draw_costs', False):
        return
    for name in ('checkFriendCoin', 'checkNewFriendCoin'):
        if hasattr(ClientAvatar, name):
            setattr(ClientAvatar, name, make_scoped_gacha_coin_check(getattr(ClientAvatar, name)))
    for name in ('requestLuckyDrawFriendCard', 'requestLuckyDrawNewFriendCard',
                 'requestLuckyDrawFriendLianChouCard', 'requestLuckyDrawNewFriendLianChouCard'):
        if hasattr(ClientAvatar, name):
            setattr(ClientAvatar, name, make_scoped_gacha_request(getattr(ClientAvatar, name), lambda avatar: avatar))
    for name in ('canSummonFriend', 'canSummonNewFriend', 'checkCardFriendLianChou', 'checkCardNewFriendLianChou'):
        if hasattr(LuckyDrawData, name):
            setattr(LuckyDrawData, name, make_scoped_gacha_request(getattr(LuckyDrawData, name), lambda data: gg.avatar))
    for name in ('getLuckyDrawFriendConsume', 'getLuckyDrawNewFriendConsume'):
        if hasattr(LuckyDrawData, name):
            setattr(LuckyDrawData, name, lambda self, *args, **kwargs: [])
    def furniture_cost(original):
        def checked(self, wire_t, *args, **kwargs):
            if original_info.data.get(wire_t, {}).get('poolType') == 2:
                return True
            return original(self, wire_t, *args, **kwargs)
        return checked
    if hasattr(LuckyDrawData, 'checkFurnitureCardCost'):
        LuckyDrawData.checkFurnitureCardCost = furniture_cost(LuckyDrawData.checkFurnitureCardCost)
    if hasattr(LuckyDrawData, 'getFurnitureCardConsume'):
        LuckyDrawData.getFurnitureCardConsume = make_free_furniture_consume(
            LuckyDrawData.getFurnitureCardConsume, original_info.data)
    ClientAvatar._f7_dedicated_draw_costs = True
