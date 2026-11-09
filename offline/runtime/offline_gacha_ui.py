# -*- coding: ascii -*-
"""Keep stock summon buttons/animation; make local t=1 simulation free."""


def is_local_gacha_pool(pool):
    if pool == 354:
        return False
    if pool in (1, 99):
        return True
    try:
        import com.data.cdata.chouka_info as catalog
        return pool in catalog.data
    except ImportError:
        return False


def free_wish_selection_context(context, wish_table, wire=5):
    if (wire != 5 or not context or context.get('no_wish') or context.get('wire_t') != 5
            or context.get('choice_cost_policy') != 'offline-free-treasure-wish-selection-v1'):
        return False
    wish = context.get('wish_id')
    return bool(wish is not None and wish_table.get(wish, {}).get('drawType') == 5)


def make_free_wish_window_show(original, context_provider, wish_table):
    def show(self, *args, **kwargs):
        self._f7_wish_show_token = getattr(self, '_f7_wish_show_token', 0) + 1
        context = context_provider()
        if kwargs.get('type') == 'treasure_wish' and context and context.get('no_wish'):
            self._f7_free_wish_period = None
            return
        free = (kwargs.get('type') == 'treasure_wish'
                and free_wish_selection_context(context, wish_table))
        self._f7_free_wish_period = context['wish_id'] if free else None
        if free:
            kwargs = dict(kwargs, yuanbao=0)
        return original(self, *args, **kwargs)
    return show


def make_free_wish_window_refresh(original, context_provider, wish_table):
    def refresh(self, *args, **kwargs):
        result = original(self, *args, **kwargs)
        context = context_provider()
        if (free_wish_selection_context(context, wish_table)
                and getattr(self, '_f7_free_wish_period', None) == context['wish_id']):
            self.price_num.setVisible(True)
            self.price_num.setString('0')
        return result
    return refresh


def make_free_wish_validation(original, context_provider, wish_table):
    def valid(self, wire, item_id):
        context = context_provider()
        if context and context.get('wire_t')==wire and context.get('no_wish'):
            return 1882
        result = original(self, wire, item_id)
        if (result == 1885
                and free_wish_selection_context(context_provider(), wish_table, wire)):
            return 0
        return result
    return valid


def make_free_wish_window_save(original, context_provider, wish_table,
                               ended_event, avatar_provider, panels_provider):
    def save(self, sender, event):
        context = context_provider()
        if context and context.get('no_wish') or (getattr(self,'_f7_free_wish_period',None) is not None and (not free_wish_selection_context(context,wish_table) or self._f7_free_wish_period!=context['wish_id'])):
            return
        if (not free_wish_selection_context(context, wish_table)
                or getattr(self, '_f7_free_wish_period', None) != context['wish_id']
                or self.yuanbao != 0):
            return original(self, sender, event)
        if (event != ended_event or not getattr(self, 'valid', False)
                or getattr(self, 'cover', False)):
            return
        selected = tuple(self.chooseList)
        panels = panels_provider()
        if not selected:
            panels.common_message.notify_message(1887)
            return
        if any(key in self.chooseListBak for key in selected):
            panels.common_message.notify_message(1884)
            return
        avatar = avatar_provider()
        show_token = self._f7_wish_show_token
        wish = context['wish_id']
        request = object()
        self._f7_wish_confirm_token = request
        consumed = [False]

        def current():
            now = context_provider()
            return (free_wish_selection_context(now, wish_table)
                and now['wish_id'] == wish and avatar_provider() is avatar
                and getattr(self, '_f7_wish_show_token', None) == show_token
                and getattr(self, '_f7_wish_confirm_token', None) is request
                and getattr(self, '_f7_free_wish_period', None) == wish
                and getattr(self, 'yuanbao', None) == 0
                and tuple(getattr(self, 'chooseList', ()) or ()) == selected)

        def confirmed():
            if consumed[0] or not current() or not getattr(self, 'valid', False):
                return
            consumed[0] = True
            items = [self.item_container.get(key) for key in selected]
            if any(item is None for item in items):
                panels.common_message.notify_message(1883)
                return
            if not self.clickConfirm(items):
                return
            self.cover = True
            close_consumed = [False]

            def closed():
                if close_consumed[0]:
                    return
                close_consumed[0] = True
                if not current() or not getattr(self, 'valid', False):
                    if self._f7_wish_show_token == show_token:
                        self.cover = False
                    return
                self.cover = False
                self.proc_event('treasure_select_list', items)
                self.remove_from_parent()
            self.window_close(closed)

        panels.common_confirm.notify_confirm(1886, confirmed, text_args=(0,))
    return save


def install_treasure_wish_free_ui():
    import gg
    import cocosui as cc
    import cocos.panels.activity_102_window as window
    import com.data.cdata.chouka_treasure_wish as wishes
    from entity.ClientAvatar import ClientAvatar
    if getattr(window.Panel, '_f7_free_wish_ui', False):
        return
    # Archive source is embedded into the same runtime globals as this module.
    def context_provider():
        return offline_archive_context(5)
    window.Panel.notify_show = make_free_wish_window_show(
        window.Panel.notify_show, context_provider, wishes.data)
    window.Panel.refresh = make_free_wish_window_refresh(
        window.Panel.refresh, context_provider, wishes.data)
    window.Panel.save_choice = make_free_wish_window_save(
        window.Panel.save_choice, context_provider, wishes.data,
        cc.ccui.TOUCH_EVENT_ENDED, lambda: gg.avatar, lambda: gg.ui.panels)
    ClientAvatar.validSetChooseTreasure = make_free_wish_validation(
        ClientAvatar.validSetChooseTreasure, context_provider, wishes.data)
    window.Panel._f7_free_wish_ui = True


def make_friend_currency_display_hook(original, animate_single):
    def display(self, result):
        if isinstance(result, dict):
            import copy
            result = copy.deepcopy(result)
            # The stock scene uses this presentation marker for friendship
            # positions and return animation, rather than normal slot indices.
            result['friendCard'] = True
        supported = ('money', 'crystal', 'summoncoin', 'friendcoin', 'yuanbao', 'giftcoin')
        currency_only = (isinstance(result, dict)
            and not any(result.get(key) for key in ('hero', 'treasure', 'treasure_trans', 'item'))
            and any(result.get(key, 0) > 0 for key in supported))
        if not currency_only:
            return original(self, result)
        return animate_single(self, result,
            lambda result=result, is_preview=False:
                self.notify_show_friend_lianchou([result], is_preview))
    return display


def make_gacha_entry_switch_guard(original, panel_provider, entry_gameplay):
    def checked(self, gamePlay, successCb, failCb=None):
        panel = panel_provider()
        if gamePlay != entry_gameplay or not getattr(panel, 'valid', False):
            return original(self, gamePlay, successCb, failCb)
        token = getattr(panel, '_f7_entry_request', 0) + 1
        panel._f7_entry_request = token

        def failed(message):
            if (panel_provider() is panel and getattr(panel, 'valid', False)
                    and getattr(panel, '_f7_entry_request', None) == token):
                panel.cover = False
            if failCb:
                return failCb(message)
        return original(self, gamePlay, successCb, failed)
    return checked


def make_gacha_rule_guard(original, rules, notify):
    def show_rule(self, sender, event):
        rule = self.can_show_rule()
        if rule and rule not in rules:
            import cc
            if event == cc.ccui.TOUCH_EVENT_ENDED:
                notify(u'\u8be5\u5386\u53f2\u5361\u6c60\u7684\u539f\u7248\u89c4\u5219\u6587\u672c\u7f3a\u5931')
            return
        return original(self, sender, event)
    return show_rule


def install_gacha_entry_guard():
    import gg
    import com.const as const
    from entity.ClientAvatar import ClientAvatar
    if getattr(ClientAvatar, '_f7_gacha_entry_guard', False):
        return
    ClientAvatar.checkGamePlaySwitch = make_gacha_entry_switch_guard(
        ClientAvatar.checkGamePlaySwitch, lambda: gg.ui.panels.card_tab,
        const.GamePlayName.FRIENDSUMMON)
    original_time_check = ClientAvatar.checkDrawInTime

    def enabled_time_check(self, draw_type, *args, **kwargs):
        if draw_type == 354:
            return False
        return original_time_check(self, draw_type, *args, **kwargs)

    ClientAvatar.checkDrawInTime = enabled_time_check
    import cocos.panels.card_tab as card_tab
    original_tabs = card_tab.Panel.init_button_comp

    def enabled_tabs(self, force_type=None):
        return original_tabs(self, 1 if force_type == 354 else force_type)

    card_tab.Panel.init_button_comp = enabled_tabs
    import com.data.cdata.rule_info_data as original_rules
    import cocos.panels.card_box as card_box
    for rule_panel in (card_tab.Panel, card_box.Panel):
        rule_panel.on_rule_click = make_gacha_rule_guard(
            rule_panel.on_rule_click, original_rules.data,
            lambda text: gg.ui.panels.common_message.notify_message(text))
    import cocos.panels.card_open as card_open

    def animate_currency_single(panel, result, callback):
        gg.ui.enable_settlement(False)
        scene = gg.city_container.get_scene_by_key(const.SCENE_SUMMON)
        if not gg.city_container.check_scene(scene):
            return
        return scene.notify_friend_card_open(result, cb=callback)

    card_open.Panel.notfit_friend_card_open = make_friend_currency_display_hook(
        card_open.Panel.notfit_friend_card_open, animate_currency_single)
    install_treasure_wish_free_ui()
    ClientAvatar._f7_gacha_entry_guard = True


def make_gacha_open_file_hook(original):
    def notify_open_file(self, enable):
        supported = self.scene_type in ('normal','activity')
        if supported and not enable:
            # The old item-box updater otherwise reclaims charging-orb touches.
            if not hasattr(self,'_f7_previous_auto_scroll'):
                self._f7_previous_auto_scroll = self.auto_scroll
            self.model_card_auto_scroll(False)
        result = original(self, enable)
        if supported:
            if not enable:
                self.item_box_panel.setVisible(False)
            elif hasattr(self, '_f7_previous_auto_scroll'):
                self.model_card_auto_scroll(self._f7_previous_auto_scroll)
                del self._f7_previous_auto_scroll
        return result
    return notify_open_file



def make_gacha_draw_file_reply_hook(original):
    def reply(self, result, wire):
        if result or not is_local_gacha_pool(wire):return original(self,result,wire)
        # The stock false branch closes controls even though no scene animation
        # starts. Do not enter that branch; retain the current group and panel.
        if not self.valid or self.get_luckyDraw_type()!=wire:return
        import gg
        proxy=getattr(gg,'_f7_avatar_proxy',None)
        if proxy is not None:
            proxy.sync_gacha_native_state(wire)
            opened=bool(((proxy.gacha_pools or {}).get('pools',{}).get(str(wire))or{}).get('group'))
            self.set_is_open_file(opened)
        self.refresh_state()
    return reply


def make_gacha_quit_file_reply_hook(original):
    def reply(self, result):
        if result or not is_local_gacha_pool(self.get_luckyDraw_type()):return original(self,result)
        if not self.valid:return
        # Only the failed quit owns this is_cover latch. Preserve reveal cover.
        self.is_cover=False
    return reply


def make_gacha_request_file_reply_hook(original):
    def reply(self, wire, result, info):
        if is_local_gacha_pool(wire) and self.get_luckyDraw_type()!=wire:return
        return original(self,wire,result,info)
    return reply

def install_gacha_ui():
    import com.const as const
    import entity.avatar_attrs.LuckyDrawData as lucky_data
    import cocos.panels.card_box as card_box
    import cocos.panels.common_confirm_3 as confirm_three
    cls = lucky_data.LuckyDrawData
    if getattr(cls, '_f7_free_simulation', False):
        return
    # The user explicitly disabled the initial-encounter pool.
    cls.isNewbieLuckyAvailable = lambda self: False

    import cocos.panels.card_tab as card_tab
    original_entry = card_tab.Panel._on_open_go_click

    def enabled_entry(self, *args, **kwargs):
        if getattr(self, 'draw_type', None) == 354:
            self.cover = False
            return
        import gg
        proxy = getattr(gg,'_f7_avatar_proxy',None)
        if proxy is not None:
            proxy.sync_gacha_native_state(getattr(self,'draw_type',None), refresh_cards=True)
        return original_entry(self, *args, **kwargs)

    card_tab.Panel._on_open_go_click = enabled_entry

    def wrap_cost(name, kind):
        original = getattr(cls, name)

        def local_cost(self, _type, *args, **kwargs):
            if not is_local_gacha_pool(_type):
                return original(self, _type, *args, **kwargs)
            if kind == 'open_file':
                return not self.getIsOpenCard(_type)
            if kind == 'open_card':
                return bool(self.getIsOpenCard(_type))
            if kind == 'amount':
                return 0
            if kind == 'costs':
                return [(const.VirtualItem.SUMMONCOIN, 0)]
            return True

        setattr(cls, name, local_cost)

    for name in ('canOpenFile', 'checkFileAndOpenAllCost'):
        wrap_cost(name, 'open_file')
    for name in ('canOpenCard', 'checkLeftAllCardsCost'):
        wrap_cost(name, 'open_card')
    for name in ('canOpenCardByConsume', 'checkFileAndOpenAllCostByConsume',
                 'checkLeftAllCardsCostByConsume'):
        wrap_cost(name, 'balance')
    for name in ('getOpenConsume', 'getOpenConsumeWithoutFree'):
        wrap_cost(name, 'amount')
    wrap_cost('getLuckyDrawConsume', 'costs')
    cls.getLuckDrawNormalOnceHalfConsume = lambda self: [(const.VirtualItem.SUMMONCOIN, 0)]

    original_init = card_box.Panel._do_init_card_info
    original_rule = card_box.Panel.on_rule_click

    def local_init(self, scene_type, draw_type):
        self._f7_presentation_epoch=getattr(self,'_f7_presentation_epoch',0)+1
        result = original_init(self, scene_type, draw_type)
        if is_local_gacha_pool(draw_type):
            if draw_type == const.LuckyDrawType.NORMAL:
                self.title.setString(u'\u8bb0\u5fc6\u9699\u95f4 \u00b7 \u514d\u8d39\u6a21\u62df')
            self.btn_rule.setVisible(True)
        return result

    def local_rule(self, sender, event):
        import cocosui as cc
        import gg
        import com.data.cdata.hero as hero_data
        if not is_local_gacha_pool(self.get_luckyDraw_type()):
            return original_rule(self, sender, event)
        if event == cc.ccui.TOUCH_EVENT_ENDED:
            gg.ui.panels.common_confirm.notify_confirm(
                u'\u514d\u8d39\u79bb\u7ebf\u6a21\u62df\u3002\u5404\u5361\u6c60\u5206\u522b\u4fdd\u5b58\u8fdb\u5ea6\u548c\u7ed3\u679c\uff0c\u4f7f\u7528\u5404\u81ea\u7684\u89d2\u8272\u3001\u788e\u7247\u3001\u5f71\u88c5\u7b49\u5956\u52b1\u914d\u7f6e\u3002#r\u6d3b\u52a8\u89c4\u5219\u53ef\u80fd\u4e0e\u539f\u670d\u52a1\u5668\u4e0d\u540c\u3002', lambda: None)

    card_box.Panel._do_init_card_info = local_init
    card_box.Panel.on_rule_click = local_rule
    card_box.Panel.notify_open_file = make_gacha_open_file_hook(card_box.Panel.notify_open_file)
    for name,adapter in (('on_reply_draw_file',make_gacha_draw_file_reply_hook),('on_reply_quit_file',make_gacha_quit_file_reply_hook),('on_reply_request_file',make_gacha_request_file_reply_hook)):
        if hasattr(card_box.Panel,name):setattr(card_box.Panel,name,adapter(getattr(card_box.Panel,name)))
    original_confirm = confirm_three.Panel.notify_confirm

    def local_confirm(self, message_id, *args, **kwargs):
        import gg
        if message_id in (1092, 1093) and is_local_gacha_pool(gg.ui.panels.card_box.get_luckyDraw_type()):
            values = kwargs.get('text_args')
            if values and len(values) == 2:
                kwargs['text_args'] = (values[0], u'\u514d\u8d39\uff08\u672c\u5730\u6a21\u62df\uff09')
        return original_confirm(self, message_id, *args, **kwargs)

    confirm_three.Panel.notify_confirm = local_confirm
    cls._f7_free_simulation = True
    _f7_log('Local t1 free cost hooks installed; stock animation callbacks retained')


def offer_offline_entry():
    """Offer original city or the currently running story without completing it."""
    import gg
    import com.const as const
    avatar = gg.avatar

    def enter_city():
        if gg.avatar is not avatar:
            return
        if gg.ui._dialogue:
            gg.ui.on_dialogue_end(gg.ui._dialogue)
        if gg.logic.game_state.current == const.GameState.CITY:
            return
        previous = getattr(gg, 'on_enter_city_cb', None)

        def ready():
            if previous:
                previous()
            install_development_probe()
            _f7_log('Offline entry: original city ready; story progress retained')

        gg.on_enter_city_cb = ready
        if gg.logic.game_state.current == const.GameState.EMERGENCY:
            gg.logic.leave_emergency()
        else:
            gg.logic.enter_city()

    def show():
        if gg.avatar is not avatar:
            return
        if gg.logic.game_state.current not in (const.GameState.CITY, const.GameState.EMERGENCY):
            gg.exec_delay(500, show)
            return
        panel = gg.ui.panels.common_confirm
        panel.notify_confirm(
            u'\u79bb\u7ebf\u6a21\u5f0f#r\u4e3b\u57ce\uff1a\u795e\u5668\u4f7f\u3001\u6362\u88c5\u3001\u514d\u8d39\u62bd\u5361#r\u4e5f\u53ef\u7ee7\u7eed\u5f53\u524d\u5267\u60c5',
            enter_city, confirm_label=u'\u8fdb\u5165\u4e3b\u57ce',
            cancel_cb=lambda: _f7_log('Offline entry: continuing original story'),
            cancel_label=u'\u7ee7\u7eed\u5267\u60c5')
        # Only this explicit navigation dialog overlays an active story.
        # Underlying story state remains untouched until a choice is made.
        panel.forcehide = False
        _f7_log('Offline entry choice shown')

    gg.exec_delay(1500, show)
