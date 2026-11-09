# -*- coding: ascii -*-
"""Offline-only shadow-equipment capacity projection for the current Avatar.

Only Avatar.invData (the unlinked shadow-equipment bag) gets projected TREASURE
total/subbag capacities. Original InvData.checkBagFull / InvData.isFullByIDs /
InvMember.checkUnlinkTreasureFull bodies stay unchanged, so ordinary admission
semantics still run against the projected numbers. Hero.treasureInv maxCost,
ordinary item wrap, trade and every other InvData instance are untouched.

The fixed policy embeds the complete 380x5 target template identities. Runtime
capacity is recomputed as:

    target-sub/total + pre-existing non-target records + explicit draw margin

and reprojected only after ClientAvatar.init_from_dict (login/rebuild); refresh
does not raise a limit while items are added. The normal (non-exclusive) list
shows subbag 1 capacity and the exclusive list shows subbag 2 capacity, both for
the currently displayed list, never the combined total. Original list contents
and GridScrollView pagination are unchanged. The explicit draw margin is 100
per subbag (200 total) per load.
"""
import hashlib
import json
import sys

POLICY_SHA256 = 'c2ea59efb4ed1d48eed87090e0fee87f4bcbe61843ad2b6c2cdffa78a46361a9'
TARGET_MANIFEST_SHA256 = '7e3849b6ed316b7cdc2ef9f103b90e0bc8e20f9b5da70ab3b585fbd72c0da62d'
FORMAT = 'project7-shadow-capacity-policy-v1'
_AVATAR_MARKER = '_q7_shadow_capacity_owner'
_PANEL_MARKER = '_q7_shadow_capacity_display_owner'
_INV_MARKER = '_q7_shadow_capacity_projection'
try:
    _TEXT_TYPES = (basestring,)
except NameError:
    _TEXT_TYPES = (str, bytes)


def _raw(function):
    return getattr(function, 'im_func', getattr(function, '__func__', function))


def _globals(function):
    function = _raw(function)
    return getattr(function, 'func_globals', getattr(function, '__globals__', {}))


def _load_policy(policy_data):
    if policy_data is None:
        raise RuntimeError('Embedded fixed shadow-capacity policy required')
    if not isinstance(policy_data, _TEXT_TYPES):
        raise ValueError('Shadow-capacity policy must be ASCII JSON text')
    try:
        binary = policy_data.encode('ascii') if not isinstance(policy_data, bytes) else policy_data
    except UnicodeError:
        raise ValueError('Shadow-capacity policy is not ASCII')
    if hashlib.sha256(binary).hexdigest() != POLICY_SHA256:
        raise ValueError('Shadow-capacity policy hash mismatch')
    try:
        policy = json.loads(binary)
    except (TypeError, ValueError):
        raise ValueError('Invalid shadow-capacity policy JSON')
    if (policy.get('format') != FORMAT or
            policy.get('source', {}).get('target_manifest_sha256') != TARGET_MANIFEST_SHA256 or
            policy.get('margin_total') != 2 * policy.get('draw_margin_per_subbag') or
            policy.get('target_total') != 1900 or
            policy.get('target_subbag_counts') != {'1': 1210, '2': 690}):
        raise ValueError('Unexpected shadow-capacity policy')
    ids = policy.get('target_template_ids')
    if (not isinstance(ids, list) or len(ids) != 380 or
            ids != sorted(set(ids)) or any(type(value) is not int for value in ids)):
        raise ValueError('Invalid shadow-capacity target identities')
    margin = policy.get('draw_margin_per_subbag')
    if type(margin) is not int or margin < 1 or margin > 10000:
        raise ValueError('Invalid shadow-capacity draw margin')
    return policy


class _Installation(object):
    def __init__(self, policy, gg, const, avatar_module, panel_module):
        self.policy = policy
        self.gg = gg
        self.const = const
        self.avatar_module = avatar_module
        self.panel_module = panel_module
        self.avatar_type = avatar_module.ClientAvatar
        self.panel_type = panel_module.Panel
        self.target_ids = frozenset(policy['target_template_ids'])
        self.target_subbag = dict((int(key), value)
                                  for key, value in policy['target_subbag_counts'].items())
        self.margin = policy['draw_margin_per_subbag']
        self.margin_total = policy['margin_total']
        self.category = const.ItemType.CATEGORY_TREASURE
        self.hero_treasure = const.ItemType.HERO_TREASURE
        self.records = []

    def current_globals(self):
        if sys.modules.get('gg') is not self.gg:
            raise RuntimeError('Shadow-capacity gg generation changed; fresh install required')
        if self.avatar_module.gg is not self.gg or self.panel_module.gg is not self.gg:
            raise RuntimeError('Shadow-capacity module contains stale gg')
        return self.gg

    def current_inv(self):
        self.current_globals()
        avatar = getattr(self.gg, 'avatar', None)
        return getattr(avatar, 'invData', None) if avatar is not None else None

    def project(self, inv):
        """Project one exact InvData instance; never mutates class-level limits."""
        if type(getattr(inv, 'categorySize', None)) is not dict:
            raise RuntimeError('InvData categorySize missing')
        if type(getattr(inv, 'subCategorySize', None)) is not dict:
            raise RuntimeError('InvData subCategorySize missing')
        if type(getattr(inv, 'inv', None)) is not list:
            raise RuntimeError('InvData item list missing')
        if self.category not in inv.categorySize:
            raise RuntimeError('Original TREASURE category limit missing')
        existing_subbag = {}
        existing_total = 0
        target_total = 0
        for item in inv.inv:
            if getattr(item, 'type', None) != self.hero_treasure:
                continue
            target_total += 1
            if getattr(item, 'itemid', None) in self.target_ids:
                continue
            existing_total += 1
            subbag = getattr(item, 'subbag', 0)
            existing_subbag[subbag] = existing_subbag.get(subbag, 0) + 1
        subbag1 = self.target_subbag[1] + existing_subbag.get(1, 0) + self.margin
        subbag2 = self.target_subbag[2] + existing_subbag.get(2, 0) + self.margin
        # Keep both subbags reachable under the total, and never shrink below
        # the records already carried by this exact instance plus the margin.
        subbag1 = max(subbag1, self._current_subbag(inv, 1) + self.margin)
        subbag2 = max(subbag2, self._current_subbag(inv, 2) + self.margin)
        total = max(self.policy['target_total'] + existing_total + self.margin_total,
                    subbag1, subbag2, target_total + self.margin_total)
        inv.categorySize[self.category] = total
        inv.subCategorySize[(self.category, 1)] = subbag1
        inv.subCategorySize[(self.category, 2)] = subbag2
        inv.size = sum(inv.categorySize.values())
        record = {'format': FORMAT,
                  'target_total': self.policy['target_total'],
                  'existing_non_target': existing_total,
                  'subbag_1': subbag1,
                  'subbag_2': subbag2,
                  'total': total}
        inv.__dict__[_INV_MARKER] = record
        return record

    def _current_subbag(self, inv, subbag):
        count = 0
        for item in inv.inv:
            if (getattr(item, 'type', None) == self.hero_treasure and
                    getattr(item, 'subbag', 0) == subbag):
                count += 1
        return count

    def project_avatar(self, avatar):
        inv = getattr(avatar, 'invData', None)
        if inv is None:
            return None
        return self.project(inv)

    def check_avatar(self, avatar):
        self.current_globals()
        if type(avatar) is not self.avatar_type:
            raise RuntimeError('Shadow-capacity Avatar generation changed')
        return self.project_avatar(avatar)

    def check_avatar_class(self, avatar_type):
        """Class-assembly check; instance projection remains in check_avatar/check."""
        self.current_globals()
        if avatar_type is not self.avatar_type:
            raise RuntimeError('Shadow-capacity Avatar class generation changed')
        return self.check()

    def display_limit(self, instance):
        """Capacity for the currently displayed non-exclusive/exclusive subbag.

        Projection is load-scoped: refresh/display never reprojects, so the
        explicit draw margin cannot silently grow while items are added.
        """
        inv = self.current_inv()
        if inv is None:
            return None
        if _INV_MARKER not in inv.__dict__:
            self.project(inv)
        subbag = 2 if bool(getattr(instance, 'zhuanshu_show', False)) else 1
        return inv.subCategorySize[(self.category, subbag)]

    def update_capacity_label(self, instance, limit=None):
        if limit is None:
            limit = self.display_limit(instance)
        if limit is None:
            return
        try:
            instance['main.num.num_last'].setString('/%d' % limit)
        except (KeyError, AttributeError):
            pass

    def update_display(self, instance):
        inv = self.current_inv()
        if inv is None:
            return
        zhuanshu = bool(getattr(instance, 'zhuanshu_show', False))
        limit = self.display_limit(instance)
        count = 0
        for item in inv.inv:
            if getattr(item, 'type', None) != self.hero_treasure:
                continue
            if bool(getattr(item, 'treasureExclusive', False)) != zhuanshu:
                continue
            count += 1
        self.update_capacity_label(instance, limit)
        if not getattr(self.const.InvQueryReturnMsg, 'NEW_TREASURELIST', 0):
            instance.num.setVisible(not zhuanshu)
            instance['main.text'].setVisible(not zhuanshu)
            instance.num.setString('%d' % count)
            if count > limit:
                instance.num.setColor(self.panel_module.cc.cc.Color3B(254, 88, 61))
                instance.btn_treasure_full_tips.setVisible(not zhuanshu)
            else:
                instance.num.setColor(self.panel_module.cc.cc.Color3B(0, 0, 0))
                instance.btn_treasure_full_tips.setVisible(False)
        else:
            instance['main.num'].setVisible(not zhuanshu)
            instance['main.text'].setVisible(not zhuanshu)
            if count >= limit:
                instance['main.num.num'].setVisible(False)
                instance['main.num.num_full'].setVisible(True)
                instance['main.num.num_full'].setString('%d' % count)
                instance['main.num.tips'].setVisible(True)
                instance['main.btn_cuiqu.light'].setVisible(True)
                instance['main.btn_hecheng.light'].setVisible(True)
            else:
                instance['main.num.num'].setVisible(True)
                instance['main.num.num_full'].setVisible(False)
                instance['main.num.num'].setString('%d' % count)
                instance['main.num.tips'].setVisible(False)
                instance['main.btn_cuiqu.light'].setVisible(False)
                instance['main.btn_hecheng.light'].setVisible(False)

    def apply(self):
        existing_avatar = getattr(self.avatar_type, _AVATAR_MARKER, None)
        existing_panel = getattr(self.panel_type, _PANEL_MARKER, None)
        if existing_avatar is not None or existing_panel is not None:
            if existing_avatar is not self or existing_panel is not self:
                raise RuntimeError('Partial shadow-capacity class cache requires fresh engine')
            return self.check()
        original_init = _raw(getattr(self.avatar_type, 'init_from_dict', None))
        original_refresh = _raw(getattr(self.panel_type, 'refresh', None))
        original_on_load = _raw(getattr(self.panel_type, 'on_load', None))
        for name, function, count in (('init_from_dict', original_init, 2),
                                      ('refresh', original_refresh, 3),
                                      ('on_load', original_on_load, 1)):
            code = getattr(function, 'func_code', getattr(function, '__code__', None))
            if code is None or code.co_argcount != count:
                raise RuntimeError('Original shadow-capacity consumer ABI changed: ' + name)
        installation = self

        def init_from_dict(instance, bdict):
            result = original_init(instance, bdict)
            installation.project_avatar(instance)
            return result
        init_from_dict.__name__ = getattr(original_init, '__name__', 'init_from_dict')

        def refresh(instance, resort=False, lastRow=False):
            result = original_refresh(instance, resort, lastRow)
            installation.update_display(instance)
            return result
        refresh.__name__ = getattr(original_refresh, '__name__', 'refresh')

        def on_load(instance):
            result = original_on_load(instance)
            installation.update_capacity_label(instance)
            return result
        on_load.__name__ = getattr(original_on_load, '__name__', 'on_load')

        setattr(self.avatar_type, 'init_from_dict', init_from_dict)
        setattr(self.panel_type, 'refresh', refresh)
        setattr(self.panel_type, 'on_load', on_load)
        setattr(self.avatar_type, _AVATAR_MARKER, self)
        setattr(self.panel_type, _PANEL_MARKER, self)
        self.records.append((self.avatar_type, 'init_from_dict', original_init, init_from_dict))
        self.records.append((self.panel_type, 'refresh', original_refresh, refresh))
        self.records.append((self.panel_type, 'on_load', original_on_load, on_load))
        avatar = getattr(self.gg, 'avatar', None)
        if avatar is not None:
            self.check_avatar(avatar)
        return self

    def check(self):
        self.current_globals()
        for cls, name, original, replacement in self.records:
            if _raw(getattr(cls, name, None)) is not replacement:
                raise RuntimeError('Shadow-capacity method identity changed: ' + name)
        avatar = getattr(self.gg, 'avatar', None)
        if avatar is not None:
            if type(avatar) is not self.avatar_type:
                raise RuntimeError('Shadow-capacity Avatar generation changed')
            self.project_avatar(avatar)
        return self


def install(policy_data=None):
    """Install after clean, before the first Avatar/profile load.

    Repeating the identical install is safe. Changed classes/modules or a
    second policy requires a fresh engine; no old caches are repaired in place.
    """
    policy = _load_policy(policy_data)
    gg = __import__('gg')
    const = __import__('com.const', fromlist=['ItemType'])
    avatar_module = __import__('entity.ClientAvatar', fromlist=['ClientAvatar'])
    panel_module = __import__('cocos.panels.treasure_treasurelist', fromlist=['Panel'])
    if (getattr(avatar_module, 'gg', gg) is not gg or
            getattr(panel_module, 'gg', gg) is not gg or
            getattr(panel_module, 'const', const) is not const):
        raise RuntimeError('Shadow-capacity import contains stale gg/const')
    existing_avatar = getattr(avatar_module.ClientAvatar, _AVATAR_MARKER, None)
    existing_panel = getattr(panel_module.Panel, _PANEL_MARKER, None)
    if existing_avatar is not None or existing_panel is not None:
        if (not isinstance(existing_avatar, _Installation) or
                existing_panel is not existing_avatar or
                existing_avatar.policy != policy or
                existing_avatar.gg is not gg or
                existing_avatar.const is not const or
                existing_avatar.avatar_module is not avatar_module or
                existing_avatar.panel_module is not panel_module or
                existing_avatar.avatar_type is not avatar_module.ClientAvatar or
                existing_avatar.panel_type is not panel_module.Panel):
            raise RuntimeError('Shadow-capacity owner/policy changed; fresh engine required')
        return existing_avatar.check()
    installation = _Installation(policy, gg, const, avatar_module, panel_module)
    return installation.apply()
