# -*- coding: ascii -*-
"""All original costume ownership plus native wardrobe safety hooks."""
import copy

REMAINING_IDS = (100021, 100031, 100191, 100201, 100271, 100272,
                 100311, 100401, 100421, 100441, 100641, 101001,
                 10080, 10081, 10149)


def migrate_remaining_wardrobe(profile, catalog, make_id, timestamp,
                                validate_profile, grant_skins):
    validate_profile(profile)
    candidate = copy.deepcopy(profile)
    for template in REMAINING_IDS:
        row = catalog.get(template)
        if not row or str(row['hero']) not in candidate['heroes']:
            raise ValueError('Missing original skin/hero row: %s' % template)
        hero = candidate['heroes'][str(row['hero'])]
        if row.get('is_dye_skin'):
            parent = catalog.get(row.get('ori_skin'))
            if (not parent or parent.get('hero') != row['hero'] or
                    parent.get('is_dye_skin') or
                    not any(s['i'] == row['ori_skin'] for s in hero['sk'].values())):
                raise ValueError('Missing owned same-hero dye parent: %s' % template)
        # The old helper scopes to released rows. This explicit subset adapter
        # reuses its instance schema without changing the authoritative cdata.
        scoped = dict(catalog)
        scoped[template] = dict(row, release=1)
        grant_skins(row['hero'], hero, [template], scoped, make_id,
                    timestamp, allow_dye=True)
    migration = 'all-original-remaining-15-costumes-v1'
    if migration not in candidate['migrations']:
        candidate['migrations'].append(migration)
    validate_profile(candidate)
    return candidate, candidate != profile


def wardrobe_title_counts(hero_id, owned, catalog, invisible_awake_ids=()):
    """Offline title policy: owned + catalog union, equal universe.

    Avoid the stock owned-all/released-only fraction and exclude styles hidden
    from the ordinary wardrobe. Preserve ordinary+dye UI grouping: no dye count.
    """
    eligible = set(i for i, row in catalog.items()
                   if row.get('hero') == hero_id and not row.get('is_dye_skin')
                   and i not in invisible_awake_ids)
    visible_owned = set(s['i'] for s in owned.values()
                        if s['i'] in eligible and not s.get('fb'))
    return len(visible_owned), len(eligible)


def costume_resource_preflight(template, catalog, model_catalog, exists):
    """Resolve exactly the original ModelBase search order, including attaches.

    Positive existence is only a preflight. Native loading and dye application
    still run through the original wardrobe and scene callbacks.
    """
    row = catalog.get(template)
    if not row:
        return False, ['skin:%s' % template]
    model = str(row['model_id'])
    paths = [prefix + '/' + model + '/' + model + '.gim'
             for prefix in ('hero', 'hero_skin', 'model_skin', 'model2', 'model')]
    found = next((p for p in paths if exists(p)), None)
    missing = [] if found else paths
    data = model_catalog.get(model, {})
    for field in ('attach_model', 'attach_real_model'):
        for name, socket, path in data.get(field, ()):
            if not exists(path):
                missing.append(path)
    return not missing, missing


def remaining_skin_resources_available(template):
    """Gateway pre-save guard; never mutates outfit on a missing entry."""
    if template not in REMAINING_IDS:
        return True
    import C_file
    import com.data.cdata.skin as skin_data
    import com.data.cdata.ui_model_data as model_data
    return costume_resource_preflight(template, skin_data.data, model_data.data,
        lambda path: bool(C_file.find_res_file(path, '')))[0]


def install_remaining_wardrobe_ui():
    import gg
    import C_file
    import com.const as const
    import com.data.cdata.skin as skin_data
    import com.data.cdata.ui_model_data as model_data
    import com.data.cdata.awake_consume_data as awake_data
    from cocos.panels.hero_wardrobe import Panel
    if getattr(Panel, '_f7_remaining_wardrobe', False):
        return
    original_title = Panel.refresh_title
    original_select = Panel.select_skin
    original_confirm = Panel.on_confirm_click
    original_dye = Panel.refresh_model_dye

    def message(text):
        gg.ui.panels.common_message.notify_message(text)

    def log(text):
        logger = globals().get('_f7_log')
        if logger:
            logger('WARDROBE_COMPLETION ' + text)

    def title(self):
        result = original_title(self)
        hero = gg.avatar.heroMgrData.getHero(self.hero_id)
        if hero:
            hidden = set(row['awake_skin'] for row in awake_data.data.values()
                         if row.get('awake_skin'))
            owned = dict((str(uid), {'i': skin.id, 'fb': skin.forbid})
                         for uid, skin in hero.skins.items())
            n, d = wardrobe_title_counts(self.hero_id, owned, skin_data.data, hidden)
            self.text_buy_num.setString('%d/%d' % (n, d))
        return result

    def fail_preview(self, transaction, reason):
        if getattr(self, '_f7_remaining_preview', None) is not transaction:
            return
        transaction['failed'] = True
        log('preview failed template=%s reason=%s' % (transaction['template'], reason))
        hero = gg.avatar.heroMgrData.getHero(transaction['hero'])
        if self.valid and self.hero_id == transaction['hero'] and hero:
            previous = transaction['previous']
            if previous in hero.skins:
                self._f7_remaining_preview = None
                try:
                    original_select(self, previous, True)
                except Exception as error:
                    log('previous preview restore failed: %s' % error)
        message(u'\u670d\u88c5\u8d44\u6e90\u52a0\u8f7d\u5931\u8d25\uff0c\u5df2\u4fdd\u7559\u539f\u7a7f\u7740')

    def select(self, skin_uuid, notify=True):
        hero = gg.avatar.heroMgrData.getHero(self.hero_id)
        skin = hero.skins.get(skin_uuid) if hero else None
        # Cancel obsolete callbacks even when the user selects an old costume.
        self._f7_remaining_preview = None
        if not skin or skin.id not in REMAINING_IDS or not notify:
            return original_select(self, skin_uuid, notify)
        ok, missing = costume_resource_preflight(skin.id, skin_data.data,
            model_data.data, lambda path: bool(C_file.find_res_file(path, '')))
        if not ok:
            log('missing resources template=%s paths=%r' % (skin.id, missing))
            message(u'\u670d\u88c5\u8d44\u6e90\u672a\u5c31\u7eea\uff0c\u5df2\u4fdd\u7559\u539f\u7a7f\u7740')
            return
        transaction = {'hero': self.hero_id, 'target': skin_uuid,
            'template': skin.id, 'model': str(skin_data.data[skin.id]['model_id']),
            'previous': getattr(self, 'skin_uuid', None) or hero.curSkin,
            'ready': False, 'failed': False}
        self._f7_remaining_preview = transaction
        try:
            result = original_select(self, skin_uuid, notify)
        except Exception as error:
            fail_preview(self, transaction, repr(error))
            return

        def check(attempt=0):
            if getattr(self, '_f7_remaining_preview', None) is not transaction:
                return
            if not self.valid or not self.visible or self.hero_id != transaction['hero']:
                self._f7_remaining_preview = None
                return
            scene = gg.city_container.get_current_scene()
            model = getattr(getattr(scene, 'scene_model', None), 'model', None)
            if (str(getattr(scene, 'real_model_id', '')) == transaction['model']
                    and model is not None and model.valid
                    and getattr(scene, 'model_can_touch', False)):
                try:
                    # Original preset dye shader path must also finish without
                    # error before the original confirm is allowed to save cs.
                    original_dye(self)
                except Exception as error:
                    fail_preview(self, transaction, repr(error))
                    return
                transaction['ready'] = True
                log('native preview loaded template=%s model=%s' %
                    (transaction['template'], transaction['model']))
            elif attempt >= 40:
                fail_preview(self, transaction, 'native model load timed out')
            else:
                gg.exec_delay(250, lambda: check(attempt + 1))
        gg.exec_delay(1, check)
        return result

    def confirm(self, sender, event):
        if event == const_touch_ended:
            hero = gg.avatar.heroMgrData.getHero(self.hero_id)
            skin = hero.skins.get(self.skin_uuid) if hero else None
            if skin and skin.id in REMAINING_IDS:
                tx = getattr(self, '_f7_remaining_preview', None)
                if not tx or tx['target'] != self.skin_uuid or not tx['ready'] or tx['failed']:
                    message(u'\u8bf7\u7b49\u5f85\u670d\u88c5\u9884\u89c8\u52a0\u8f7d\u5b8c\u6210')
                    return
        return original_confirm(self, sender, event)

    import cocosui as cc
    const_touch_ended = cc.ccui.TOUCH_EVENT_ENDED
    Panel.refresh_title = title
    Panel.select_skin = select
    Panel.on_confirm_click = confirm
    Panel._f7_remaining_wardrobe = True
