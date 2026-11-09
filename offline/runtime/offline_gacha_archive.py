# -*- coding: ascii -*-
"""Independent, searchable historical catalog. No configuration dates are changed."""
_f7_archive_session = None
_f7_archive_owner = None
_f7_archive_selecting = 0
_f7_archive_self_choose_pools = frozenset((265, 369, 427, 454, 455, 484))
_f7_archive_hero_wish_pools = frozenset((1, 119, 126, 143, 154, 164))


def offline_archive_context(wire_t=None):
    import copy
    context = copy.deepcopy(_f7_archive_session) if _f7_archive_session else None
    try:
        import gg
    except ImportError:
        return context if wire_t is None or (context or {}).get('wire_t')==wire_t else None
    if _f7_archive_owner is not None and getattr(gg,'avatar',None) is not _f7_archive_owner:
        context = None
    proxy = getattr(gg,'_f7_avatar_proxy',None)
    if proxy is not None and getattr(proxy,'owner',None) is not None and getattr(gg,'avatar',None) is proxy.owner:
        import com.data.cdata.chouka_treasure_wish as wishes
        return archive_effective_wish_context(context,getattr(proxy,'gacha_pools',None),wishes.data,wire_t)
    return context if wire_t is None or (context or {}).get('wire_t')==wire_t else None


def offline_archive_authorized(wire_t):
    context = offline_archive_context(wire_t)
    return bool(wire_t != 354 and context and not context.get('expired_restore') and context.get('wire_t')==wire_t)


def offline_archive_clear():
    global _f7_archive_session, _f7_archive_owner
    _f7_archive_session = None
    _f7_archive_owner = None


def archive_wish_periods(table, wire_t, treasures=None):
    rows = []
    for wish_id, data in table.items():
        if wire_t != 354 and data.get('drawType', 0) == wire_t:
            item = data.get('treasure_id', 0)
            rows.append(dict(wish_id=wish_id, draw_type=wire_t,
                             begin=data.get('begin_time', ()), end=data.get('end_time', ()),
                             name=(treasures or {}).get(item, {}).get('name', str(item))))
    return sorted(rows, key=lambda row: row['wish_id'])


def archive_hero_wish_periods(table, wire_t, heroes=None):
    groups = {}
    for wish_id, data in table.items():
        if (wire_t in _f7_archive_hero_wish_pools and data.get('drawType') == wire_t
                and data.get('wish_type') == 2):
            period = (tuple(data['begin_time']), tuple(data['end_time']))
            groups.setdefault(period, []).append(wish_id)
    rows = []
    for (begin, end), ids in groups.items():
        ids = sorted(ids)
        names = [(heroes or {}).get(table[key]['wish_target'], {}).get('name',
                 str(table[key]['wish_target'])) for key in ids]
        rows.append(dict(hero_wish_id=ids[0], hero_wish_ids=ids, draw_type=wire_t,
                         begin=begin, end=end, name=u' / '.join(names)))
    return sorted(rows, key=lambda row: (row['begin'], row['hero_wish_id']))


def archive_scoped_hero_wish_ids(table, wire_t):
    context = offline_archive_context(wire_t)
    if (wire_t not in _f7_archive_hero_wish_pools or not context
            or context.get('wire_t') != wire_t
            or context.get('hero_wish_policy') != 'offline-original-hero-wish-period-v1'):
        return None
    ids = context.get('hero_wish_ids')
    for period in archive_hero_wish_periods(table, wire_t):
        if ids == period['hero_wish_ids']:
            return ids
    return None


def archive_make_session(row, wish_table, wish_id=None, rotation_uaid=None, rotations=None, templates=None, hero_wish_id=None):
    wire_t = row['wire_t']
    if wire_t == 354:
        raise ValueError('blocked pool')
    context = dict(wire_t=wire_t, category=row['category'])
    if wire_t in _f7_archive_hero_wish_pools:
        period = next((period for period in archive_hero_wish_periods(wish_table, wire_t)
                       if period['hero_wish_id'] == hero_wish_id), None)
        if period is None:
            raise ValueError('explicit complete original hero wish period required')
        context.update(hero_wish_ids=period['hero_wish_ids'],
                       hero_wish_policy='offline-original-hero-wish-period-v1')
    if wire_t == 5:
        selected = wish_table.get(wish_id, {})
        if wish_id is None or selected.get('drawType') != wire_t:
            raise ValueError('explicit matching wish period required')
        context.update(wish_id=wish_id, draw_type=wire_t,
                       begin_time=tuple(selected.get('begin_time', ())),
                       end_time=tuple(selected.get('end_time', ())),
                       choice_cost_policy='offline-free-treasure-wish-selection-v1')
    if wire_t in _f7_archive_self_choose_pools:
        selected = (rotations or {}).get(rotation_uaid, {})
        template = (templates or {}).get(selected.get('tmp_id'), {})
        if (rotation_uaid is None or template.get('tmp_type') != 88 or
                not selected.get('self_choose_S') or not selected.get('self_choose_A')):
            raise ValueError('explicit original candidate period required')
        import copy
        context.update(self_choose_wire=wire_t, rotation_uaid=rotation_uaid,
                       rotation=copy.deepcopy(selected),
                       rotation_policy='offline-archive-candidate-period-v1')
    return context


def archive_rotation_periods(rotations, templates):
    rows = []
    for uaid, data in rotations.items():
        if (templates.get(data.get('tmp_id'), {}).get('tmp_type') != 88 or
                not data.get('self_choose_S') or not data.get('self_choose_A')):
            continue
        span = data.get('open_range', ())
        rows.append(dict(rotation_uaid=uaid, begin=span[:6], end=span[6:12],
                         name=u'\u6863\u6848\u5019\u9009\u65f6\u671f S:%s A:%s' % (
                             ','.join(str(x) for x in data['self_choose_S']),
                             ','.join(str(x) for x in data['self_choose_A']))))
    return sorted(rows, key=lambda row: (tuple(row['begin']), row['rotation_uaid']))


def make_archive_rotation_getter(original, rotations, templates):
    def get(rotate_type, is_online=True):
        context = offline_archive_context()
        if (rotate_type == 88 and context and
                context.get('wire_t') in _f7_archive_self_choose_pools and
                context.get('self_choose_wire') == context.get('wire_t')):
            uaid = context.get('rotation_uaid')
            row = rotations.get(uaid, {})
            if (row and templates.get(row.get('tmp_id'), {}).get('tmp_type') == 88 and
                    row.get('self_choose_S') and row.get('self_choose_A') and
                    context.get('rotation') == dict(row.items())):
                import copy
                return uaid, copy.deepcopy(row)
        return original(rotate_type, is_online)
    return get


def install_archive_rotation_hooks():
    import com.utils.helpers as helpers
    import com.data.cdata.activity_config as rotations
    import com.data.cdata.activity_template as templates
    if getattr(helpers, '_f7_archive_rotation_installed', False):
        return
    helpers.get_active_uaid = make_archive_rotation_getter(
        helpers.get_active_uaid, rotations.data, templates.data)
    helpers._f7_archive_rotation_installed = True


def archive_scoped_wish_id(table, wire_t):
    context = offline_archive_context(wire_t)
    if context and wire_t == 5 and context.get('wire_t') == wire_t:
        wish_id = context.get('wish_id')
        if table.get(wish_id, {}).get('drawType') == wire_t:
            return wish_id
    return None


def make_archive_wish_getter(original, table):
    def get(self, _type):
        context = offline_archive_context(_type)
        if context and context.get('no_wish'):
            return None
        wish_id = archive_scoped_wish_id(table, _type)
        return wish_id if wish_id is not None else original(self, _type)
    return get


def make_archive_wish_group_getter(original, table):
    def get(self, _type, exlude_fixed=False):
        context = offline_archive_context(_type)
        if context and context.get('no_wish'):
            return {}
        wish_id = archive_scoped_wish_id(table, _type)
        hero_ids = archive_scoped_hero_wish_ids(table, _type)
        if wish_id is None and hero_ids is None:
            return original(self, _type, exlude_fixed)
        selected = table[wish_id] if wish_id is not None else None
        groups = {}
        for key, data in table.items():
            if (data.get('drawType') == _type and
                    ((hero_ids is not None and key in hero_ids) or
                     (selected is not None and data.get('begin_time') == selected.get('begin_time')
                      and data.get('end_time') == selected.get('end_time'))) and
                    not (exlude_fixed and data.get('fix_rate', 0))):
                groups.setdefault(data['gid'], []).append(key)
        return groups
    return get


def install_archive_wish_hooks():
    from entity.avatar_attrs.LuckyDrawData import LuckyDrawData
    import com.data.cdata.chouka_treasure_wish as wishes
    if getattr(LuckyDrawData, '_f7_archive_wish_installed', False):
        return
    LuckyDrawData.getTreasureWishIdByDrawType = make_archive_wish_getter(
        LuckyDrawData.getTreasureWishIdByDrawType, wishes.data)
    LuckyDrawData.getWishGroupInfoListsByDrawType = make_archive_wish_group_getter(
        LuckyDrawData.getWishGroupInfoListsByDrawType, wishes.data)
    LuckyDrawData._f7_archive_wish_installed = True


def archive_catalog(table, furniture_delivery=None):
    rows = []
    for wire_t, data in table.items():
        if wire_t == 354:
            continue
        category = 'furniture' if data.get('poolType') == 2 else 'hero_treasure'
        if wire_t == 131:
            category = 'friend'
        rows.append(dict(wire_t=wire_t, name=data.get('room_title') or u'\u672a\u547d\u540d\u5361\u6c60',
                         category=category, begin=data.get('begin_time', ()),
                         end=data.get('end_time', ()), configuration=data,
                         furniture_panel=archive_furniture_panel(wire_t, furniture_delivery or {})))
    if 99 not in table:
        rows.append(dict(wire_t=99, name=u'\u7f81\u7eca\u94fe\u7ed3', category='friend', begin=(), end=(), configuration={}))
    return sorted(rows, key=lambda row: row['wire_t'], reverse=True)


def archive_furniture_panel(wire_t, furniture_delivery):
    # Legacy pools use chouka_info directly; delivery is a newer subset.
    return 'city_room_danchi_new' if wire_t in furniture_delivery else 'city_room_danchi'


def archive_filter(rows, query='', category=None):
    query = query.strip().lower()
    return [row for row in rows if (not category or row['category'] == category)
            and (not query or query in (str(row.get('wire_t', row.get('wish_id', row.get('rotation_uaid', '')))) + ' ' + row['name'] + ' ' +
                 archive_date(row['begin']) + ' ' + archive_date(row['end'])).lower())]


def archive_date(value):
    return '%04d-%02d-%02d' % tuple(value[:3]) if len(value) >= 3 else u'\u65e0\u65e5\u671f'


def archive_required_resources(row, plists=None):
    data = row['configuration']
    if row['category'] == 'furniture':
        panel_name = row.get('furniture_panel', 'city_room_danchi')
        paths = ['cocos/' + panel_name + '.csb', 'cocos/city_common_2.csb']
        for template in (panel_name, 'city_common_2'):
            paths.extend('cocos/' + item for item in (plists or {}).get(template + '.json', []))
        return paths
    index = data.get('room_enter_index')
    paths = []
    if index and index != 7:
        template = {-1: 'card_activity_61', -2: 'card_zixuan', -3: 'card_activity_62'}.get(index, 'card_activity_%d' % index)
        paths.append('cocos/' + template + '.csb')
        paths.extend('cocos/' + item for item in (plists or {}).get(template + '.json', []))
    return paths


def archive_entry_status(row, resource_exists, scene_ready=True, plists=None):
    if not scene_ready:
        return u'\u539f\u53ec\u5524\u573a\u666f\u5c1a\u672a\u5c31\u7eea'
    missing = [path for path in archive_required_resources(row, plists) if not resource_exists(path)]
    if missing:
        return u'\u7f3a\u5c11\u539f\u754c\u9762\u8d44\u6e90\uff1a' + ', '.join(missing)
    return ''


def make_archive_check(original, activity=False):
    def checked(self, wire_t, *args, **kwargs):
        if wire_t == 354:
            return False
        if offline_archive_authorized(wire_t):
            if activity:
                import com.data.cdata.chouka_info as catalog
                pool_type = args[0] if args else kwargs.get('pool_type', 1)
                return catalog.data.get(wire_t, {}).get('poolType', 1) == pool_type
            return True
        return original(self, wire_t, *args, **kwargs)
    return checked


def install_gacha_archive():
    import cocos.panels.card_tab as card_tab
    from entity.ClientAvatar import ClientAvatar
    if getattr(card_tab.Panel, '_f7_archive_installed', False):
        return
    ClientAvatar.checkDrawInTime = make_archive_check(ClientAvatar.checkDrawInTime)
    ClientAvatar.checkActivity = make_archive_check(ClientAvatar.checkActivity, True)
    install_archive_furniture_hooks()
    install_archive_wish_hooks()
    install_archive_jiaozhi_hook()
    install_archive_rotation_hooks()
    original_select = card_tab.Panel.on_chouka_btn_click
    original_tabs = card_tab.Panel.init_button_comp

    def select(self, wire_t):
        if wire_t == 354:
            import gg
            gg.ui.panels.common_confirm.notify_confirm(u'\u521d\u9047\u5361\u6c60\u5df2\u6309\u8981\u6c42\u5c4f\u853d', lambda: None)
            self.cover = False
            return
        return make_archive_direct_selection(original_select)(self,wire_t)

    def tabs(self, force_type):
        if force_type == 354:
            import gg
            gg.ui.panels.common_confirm.notify_confirm(u'\u521d\u9047\u5361\u6c60\u5df2\u6309\u8981\u6c42\u5c4f\u853d', lambda: None)
            force_type = 1
        return make_archive_preserved_selection(original_tabs)(self,force_type)
    card_tab.Panel.on_chouka_btn_click = select
    card_tab.Panel.init_button_comp = tabs
    if hasattr(card_tab.Panel,'on_navigation_canvas_ck'):
        card_tab.Panel.on_navigation_canvas_ck = make_archive_preserved_selection(card_tab.Panel.on_navigation_canvas_ck)
    original = card_tab.Panel.on_load

    def loaded(self, *args, **kwargs):
        result = original(self, *args, **kwargs)
        import cocosui as cc
        button = cc.ccui.Button.create()
        button.setTitleText(u'\u5386\u53f2\u5361\u6c60\u6863\u6848')
        button.setTitleFontSize(22)
        button.ignoreContentAdaptWithSize(False)
        button.setContentSize(cc.cc.Size(210, 56))
        button.setPosition(cc.cc.Vec2(160, 180))
        button.setTouchEnabled(True)
        button.addTouchEventListener(lambda sender, event: show_gacha_archive(self) if event == cc.ccui.TOUCH_EVENT_ENDED else None)
        self._node.addChild(button, 120)
        return result
    card_tab.Panel.on_load = loaded
    card_tab.Panel._f7_archive_installed = True


def show_gacha_archive(panel):
    import cocosui as cc
    import gg
    import com.const as const
    import com.data.cdata.chouka_info as catalog
    import com.data.cdata.furniture_delivery as delivery
    rows = archive_catalog(catalog.data, delivery.data)
    root = cc.ccui.Layout.create()
    viewport = cc.cc.Director.getInstance().getWinSize()
    root.setContentSize(cc.cc.Size(1050, 620))
    root.setAnchorPoint(cc.cc.Vec2(0, 0))
    origin = panel._node.convertToNodeSpace(cc.cc.Vec2(max(0, (viewport.width - 1050) / 2), max(0, (viewport.height - 620) / 2)))
    root.setPosition(origin)
    root.setBackGroundColorType(1)
    root.setBackGroundColor(cc.cc.Color3B(25, 30, 45))
    root.setTouchEnabled(True)
    panel._node.addChild(root, 1000)
    state = {'category': None, 'period_row': None, 'active':True, 'request':0}
    import com.data.cdata.chouka_treasure_wish as wishes
    import com.data.cdata.hero as heroes
    import com.data.cdata.hero_treasure as treasures
    import com.data.cdata.activity_config as rotations
    import com.data.cdata.activity_template as templates

    def button(text, x, y, width, callback, parent=root):
        node = cc.ccui.Button.create()
        node.setTitleText(text)
        node.setTitleFontSize(20)
        node.setTitleColor(cc.cc.Color3B(245, 248, 255))
        node.ignoreContentAdaptWithSize(False)
        node.setContentSize(cc.cc.Size(width, 45))
        node.setPosition(cc.cc.Vec2(x, y))
        node.setTouchEnabled(True)
        node.addTouchEventListener(lambda sender, event: callback() if event == cc.ccui.TOUCH_EVENT_ENDED else None)
        backing = cc.ccui.Layout.create()
        backing.setContentSize(cc.cc.Size(width, 45))
        backing.setPosition(cc.cc.Vec2(x - width / 2, y - 22.5))
        backing.setBackGroundColorType(1)
        backing.setBackGroundColor(cc.cc.Color3B(49, 64, 89))
        parent.addChild(backing)
        parent.addChild(node, 1)
        return node

    # Keep an exit available even if a later native widget binding fails.
    def close_archive():
        state['active'] = False
        state['request'] += 1
        root.removeFromParent()
    button(u'\u5173\u95ed', 945, 590, 150, close_archive)
    field = cc.ccui.TextField.create(u'\u540d\u79f0 / wire ID / \u5386\u53f2\u65e5\u671f', '', 22)
    field.setPosition(cc.cc.Vec2(370, 535))
    field.setTextColor(cc.cc.Color4B(245, 248, 255, 255))
    field.setPlaceHolderColor(cc.cc.Color4B(195, 207, 225, 255))
    search_back = cc.ccui.Layout.create()
    search_back.setContentSize(cc.cc.Size(700, 45))
    search_back.setPosition(cc.cc.Vec2(20, 512))
    search_back.setBackGroundColorType(1)
    search_back.setBackGroundColor(cc.cc.Color3B(49, 64, 89))
    root.addChild(search_back)
    field.setTouchEnabled(True)
    root.addChild(field)
    scroll = cc.ccui.ScrollView.create()
    scroll.setContentSize(cc.cc.Size(1010, 475))
    scroll.setPosition(cc.cc.Vec2(20, 20))
    scroll.setDirection(1)
    scroll.setTouchEnabled(True)
    root.addChild(scroll)

    def activate(row,context):
        global _f7_archive_session, _f7_archive_owner, _f7_archive_selecting
        previous = _f7_archive_session
        previous_owner = _f7_archive_owner
        _f7_archive_session = context
        _f7_archive_owner = getattr(gg,'avatar',None)
        try:
            if row['wire_t'] == 5 or row['wire_t'] in _f7_archive_hero_wish_pools:
                proxy = getattr(gg, '_f7_avatar_proxy', None)
                if proxy is not None:
                    proxy.sync_gacha_native_state()
            if row['category'] == 'furniture':
                target = getattr(gg.ui.panels, row['furniture_panel'])
                layer = panel.add_layer(target)
                panel.proc_event('show', _curr_type=row['wire_t'], _children=True, _layer=layer)
                state['active'] = False
                root.removeFromParent()
                return
            # on_chouka_btn_click uses the original room_enter_index template;
            # no historical button component is needed to select this wire ID.
            _f7_archive_selecting += 1
            try:
                panel.on_chouka_btn_click(row['wire_t'])
            finally:
                _f7_archive_selecting -= 1
            state['active'] = False
            root.removeFromParent()
            # The stock poster exposes its separate S/A chooser before it
            # enables Open. Calling the private Go method bypasses that guard.
            if not row['configuration'].get('self_choose'):
                panel._on_open_go_click()
        except Exception as error:
            _f7_archive_session = previous
            _f7_archive_owner = previous_owner
            if row['wire_t'] == 5 or row['wire_t'] in _f7_archive_hero_wish_pools:
                proxy = getattr(gg, '_f7_avatar_proxy', None)
                if proxy is not None:
                    try:
                        proxy.sync_gacha_native_state()
                    except Exception:
                        # Rollback projection is best effort; always release the UI.
                        pass
            panel.cover = False
            gg.ui.panels.common_confirm.notify_confirm(u'\u539f\u5361\u6c60\u5165\u53e3\u672a\u80fd\u52a0\u8f7d\uff1a%s' % error, lambda: None)


    def enter(row, wish_id=None, rotation_uaid=None, hero_wish_id=None):
        state['request'] += 1
        request = state['request']
        if row['wire_t'] == 354:
            gg.ui.panels.common_confirm.notify_confirm(u'\u521d\u9047\u5361\u6c60\u5df2\u6309\u8981\u6c42\u5c4f\u853d', lambda: None)
            return
        if ((row['wire_t'] == 5 and wish_id is None) or
                (row['wire_t'] in _f7_archive_hero_wish_pools and hero_wish_id is None) or
                (row['wire_t'] in _f7_archive_self_choose_pools and rotation_uaid is None)):
            state['period_row'] = row
            field.setString('')
            render_periods()
            return
        scene = gg.city_container.get_scene_by_key(const.SCENE_SUMMON)
        files = cc.cc.FileUtils.getInstance()
        reason = archive_entry_status(row, files.isFileExist, gg.city_container.check_scene(scene), gg.ui.projplistinfo)
        if reason:
            gg.ui.panels.common_confirm.notify_confirm(reason, lambda: None)
            return
        try:
            context = archive_make_session(row, wishes.data, wish_id, rotation_uaid, rotations.data, templates.data, hero_wish_id)
        except ValueError as error:
            gg.ui.panels.common_confirm.notify_confirm(str(error), lambda: None)
            return
        proxy = getattr(gg,'_f7_avatar_proxy',None)
        owner = getattr(gg,'avatar',None)
        try:
            conflict = archive_entry_group_conflict(context,getattr(proxy,'gacha_pools',None),wishes.data)
        except ValueError as error:
            gg.ui.panels.common_confirm.notify_confirm(str(error),lambda:None)
            return
        if conflict:
            def current():
                return (state['active'] and archive_panel_alive(panel,root) and state['request']==request and getattr(gg,'avatar',None) is owner
                    and getattr(gg,'_f7_avatar_proxy',None) is proxy)
            def back():
                if current():
                    state['request'] += 1
                    render_periods()
            def restore():
                if not current():
                    return
                try:
                    restored = archive_restore_group_context(conflict,getattr(proxy,'gacha_pools',None),wishes.data)
                except ValueError as error:
                    gg.ui.panels.common_confirm.notify_confirm(str(error),lambda:None)
                    return
                if restored is None:
                    back()
                    return
                state['request'] += 1
                activate(row,restored)
            old_context = conflict['context']
            if old_context.get('no_wish'):
                label = u'\u65e0\u7948\u613f\u7ed1\u5b9a'
            else:
                identifiers = old_context.get('hero_wish_ids') or [old_context['wish_id']]
                original_period = wishes.data[identifiers[0]]
                label = u'%s [%s -> %s]' % (identifiers,archive_date(original_period.get('begin_time',())),archive_date(original_period.get('end_time',())))
            gg.ui.panels.common_confirm.notify_confirm(
                u'\u5f53\u524d\u5361\u7ec4\u4ecd\u5b58\u5728\uff08%s\uff09\uff0c\u4e0e\u6240\u9009\u65f6\u671f\u4e0d\u540c\u3002' % label,
                restore,confirm_label=u'\u6062\u590d\u65e7\u5361\u7ec4',cancel_cb=back,cancel_label=u'\u8fd4\u56de\u9009\u671f')
            return
        activate(row,context)

    def render_periods():
        row = state['period_row']
        if row['wire_t'] == 5:
            periods = archive_wish_periods(wishes.data, row['wire_t'], treasures.data)
            key = 'wish_id'
        elif row['wire_t'] in _f7_archive_hero_wish_pools:
            periods = archive_hero_wish_periods(wishes.data, row['wire_t'], heroes.data)
            key = 'hero_wish_id'
        else:
            periods = archive_rotation_periods(rotations.data, templates.data)
            key = 'rotation_uaid'
        visible = archive_filter(periods, field.getString())
        scroll.removeAllChildren()
        height = max(475, len(visible) * 65)
        scroll.setInnerContainerSize(cc.cc.Size(1010, height))
        for index, period in enumerate(visible):
            label = u'%s  [%s=%s]  %s -> %s' % (period['name'], key, period[key], archive_date(period['begin']), archive_date(period['end']))
            button(label, 505, height - index * 65 - 34, 995,
                   lambda selected=period: enter(row, selected.get('wish_id'), selected.get('rotation_uaid'), selected.get('hero_wish_id')), scroll)

    def render(category=None):
        state['period_row'] = None
        state['category'] = category
        visible = archive_filter(rows, field.getString(), category)
        scroll.removeAllChildren()
        height = max(475, len(visible) * 65)
        scroll.setInnerContainerSize(cc.cc.Size(1010, height))
        for index, row in enumerate(visible):
            suffix = {'furniture': u' \u00b7 \u5bb6\u5177', 'friend': u' \u00b7 \u53cb\u60c5', 'hero_treasure': u' \u00b7 \u795e\u5668\u4f7f/\u5f71\u88c5'}[row['category']]
            label = archive_row_label(row,suffix)
            button(label, 505, height - index * 65 - 34, 995, lambda selected=row: enter(selected), scroll)
    for text, x, category in [(u'\u5168\u90e8485', 110, None), (u'\u795e\u5668\u4f7f / \u5f71\u88c5', 340, 'hero_treasure'), (u'\u53cb\u60c5', 550, 'friend'), (u'\u5bb6\u5177', 730, 'furniture')]:
        button(text, x, 590, 190, lambda selected=category: render(selected))
    button(u'\u7b5b\u9009', 840, 535, 150, lambda: render_periods() if state['period_row'] else render(state['category']))
    render()


def install_archive_furniture_hooks():
    import cocos.panels.city_room_danchi_new as furniture
    import cocos.panels.city_room_danchi as legacy_furniture
    import com.data.cdata.furniture_delivery as delivery
    import com.data.cdata.chouka_info as catalog
    import com.utils.helpers as helpers
    original_time = helpers.get_rotation_time_range_text

    def wrap_init(original):
        def init_data(self, _curr_type=0):
            context = offline_archive_context()
            if context and context['category'] == 'furniture' and context['wire_t'] == _curr_type:
                self.type_list = [_curr_type]
                self.curr_type = _curr_type
                for name in ('left_arrow', 'right_arrow'):
                    arrow = getattr(self, name, None)
                    if arrow is not None and hasattr(arrow, 'setVisible'):
                        arrow.setVisible(False)
                return
            return original(self, _curr_type)
        return init_data

    def time_text(rotation_type):
        context = offline_archive_context()
        if context and context['category'] == 'furniture':
            wire_t = context['wire_t']
            if delivery.data.get(wire_t, {}).get('rotation_type') == rotation_type:
                data = catalog.data.get(wire_t, {})
                return u'\u79bb\u7ebf\u5386\u53f2\u6863\u6848\uff1a%s \u2192 %s' % (archive_date(data.get('begin_time', ())), archive_date(data.get('end_time', ())))
        return original_time(rotation_type)
    furniture.Panel.init_data = wrap_init(furniture.Panel.init_data)
    legacy_furniture.Panel.init_data = wrap_init(legacy_furniture.Panel.init_data)
    helpers.get_rotation_time_range_text = time_text


def make_archive_jiaozhi_checker(original, table):
    def check(self, key):
        row = table.get(key,{})
        if row and offline_archive_authorized(row.get('drawType')):
            return True
        return original(self,key)
    return check


def install_archive_jiaozhi_hook():
    from entity.avatar_members.LuckyDrawMember import Member as LuckyDrawMember
    import com.data.cdata.chouka_jiaozhi as table
    if getattr(LuckyDrawMember,'_f7_archive_jiaozhi_installed',False):
        return
    LuckyDrawMember.checkJiaozhiInTime = make_archive_jiaozhi_checker(LuckyDrawMember.checkJiaozhiInTime,table.data)
    LuckyDrawMember._f7_archive_jiaozhi_installed = True


def archive_row_label(row, suffix=''):
    if row['wire_t'] == 460:
        return u'460 \u8d44\u6599\u51b2\u7a81\uff1a\u666e\u901a\u5341\u7396/\u7ef4\u6069\uff1b\u5145\u80fd\u8fbe\u5c14\u7ef4\u62c9/\u83f2\u5c3c\u514b\uff08\u79bb\u7ebf\uff09'
    return u'%s  [t=%s]%s  %s \u2192 %s' % (row['name'], row['wire_t'], suffix, archive_date(row['begin']), archive_date(row['end']))


def archive_group_wish_context(group, wire, table):
    """Canonical extant group binding, including explicit legacy no-wish."""
    if wire not in _f7_archive_hero_wish_pools and wire!=5:
        return None
    pinned = group.get('special_context') or {}
    context = {'wire_t':wire,'category':'hero_treasure','effective_group_id':group['id']}
    if 'hero_wish_ids' in pinned or 'hero_wish_policy' in pinned:
        if wire not in _f7_archive_hero_wish_pools or pinned.get('hero_wish_policy')!='offline-original-hero-wish-period-v1':
            raise ValueError('Invalid saved hero wish group policy')
        ids = pinned.get('hero_wish_ids')
        period = next((p for p in archive_hero_wish_periods(table,wire)if p['hero_wish_ids']==ids),None)
        if period is None:
            raise ValueError('Invalid saved complete hero wish period')
        context.update(hero_wish_ids=list(ids),hero_wish_policy=pinned['hero_wish_policy'])
    elif 'wish_id' in pinned or pinned.get('policy')=='offline-original-display-probability-treasure-wish-v1':
        wish = pinned.get('wish_id')
        if wire!=5 or pinned.get('policy')!='offline-original-display-probability-treasure-wish-v1' or table.get(wish,{}).get('drawType')!=5:
            raise ValueError('Invalid saved treasure wish period')
        row = table[wish]
        context.update(wish_id=wish,draw_type=5,begin_time=tuple(row.get('begin_time',())),end_time=tuple(row.get('end_time',())),
            choice_cost_policy='offline-free-treasure-wish-selection-v1')
    else:
        context['no_wish'] = True
    return context


def archive_wish_binding(context):
    if not context or context.get('no_wish'):
        return ('no_wish',)
    if 'hero_wish_ids' in context:
        return ('hero',context.get('hero_wish_policy'),tuple(context['hero_wish_ids']))
    if 'wish_id' in context:
        return ('treasure',context['wish_id'])
    return ('no_wish',)


def archive_effective_wish_context(session, pools, table, wire=None):
    """Pure resolver. Existing groups take precedence even when all opened."""
    wire = wire if wire is not None else (session or {}).get('wire_t')
    group = ((pools or {}).get('pools',{}).get(str(wire)) or {}).get('group')
    if group is not None and (wire==5 or wire in _f7_archive_hero_wish_pools):
        return archive_group_wish_context(group,wire,table)
    if session and session.get('effective_group_id') is not None:
        # A restore session expires on actual retirement; never activate a
        # deferred period selection without another explicit archive choice.
        return {'wire_t':wire,'category':'hero_treasure','no_wish':True,'expired_restore':True}
    import copy
    return copy.deepcopy(session) if session and session.get('wire_t')==wire else None


def archive_entry_group_conflict(requested, pools, table):
    wire = requested['wire_t']
    group = ((pools or {}).get('pools',{}).get(str(wire)) or {}).get('group')
    if group is None or wire!=5 and wire not in _f7_archive_hero_wish_pools:
        return None
    old = archive_group_wish_context(group,wire,table)
    if archive_wish_binding(old)==archive_wish_binding(requested):
        return None
    return {'wire_t':wire,'group_id':group['id'],'binding':archive_wish_binding(old),'context':old}


def archive_restore_group_context(fence, pools, table):
    wire = fence['wire_t']
    group = ((pools or {}).get('pools',{}).get(str(wire)) or {}).get('group')
    if group is None or group.get('id')!=fence['group_id']:
        return None
    context = archive_group_wish_context(group,wire,table)
    return context if archive_wish_binding(context)==fence['binding'] else None


def archive_panel_alive(panel, root):
    if not getattr(panel,'valid',True) or getattr(root,'removed',False):
        return False
    parent = getattr(root,'getParent',None)
    if callable(parent):
        try:
            return parent() is not None
        except Exception:
            return False
    return True


def make_archive_preserved_selection(original):
    def preserved(self,*args,**kwargs):
        global _f7_archive_selecting
        _f7_archive_selecting += 1
        try:
            return original(self,*args,**kwargs)
        finally:
            _f7_archive_selecting -= 1
    return preserved


def make_archive_direct_selection(original):
    def select(self,wire,*args,**kwargs):
        if _f7_archive_selecting:
            archive_sync_wire(wire)
            return original(self,wire,*args,**kwargs)
        active = _f7_archive_session is not None
        offline_archive_clear()
        archive_sync_wire(wire)
        # Same-wire user selection changes the context too; let the original
        # tab refresh rather than early-return with a stale archive poster.
        previous = getattr(self,'draw_type',None)
        if active and previous==wire:self.draw_type=None
        try:
            return original(self,wire,*args,**kwargs)
        finally:
            if active and getattr(self,'draw_type',None) is None:self.draw_type=previous
    return select


def archive_sync_wire(wire):
    try:
        import gg
    except ImportError:
        return
    proxy = getattr(gg,'_f7_avatar_proxy',None)
    if proxy is not None and getattr(proxy,'owner',None) is not None and getattr(gg,'avatar',None) is proxy.owner:
        proxy.sync_gacha_native_state(wire)
