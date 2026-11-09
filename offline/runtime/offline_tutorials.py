# -*- coding: ascii -*-
"""User-requested tutorial UI bypass; retains main-story continuations.

Install before creating ClientAvatar or UI panels. No completed-event/reward,
first-free-dye, prologue or furnishing-progress flags are fabricated here.
"""
SKIP_TUTORIAL_UI = True


def _continue_after_tutorial(callback):
    if callback is not None:
        if not callable(callback):
            raise TypeError('Tutorial continuation must be callable')
        import gg
        gg.exec_delay(1, callback)


def skip_guidance(self, start_id, cb=None):
    _f7_log('TUTORIAL UI SKIP guidance=%r callback=%s' % (start_id, cb is not None))
    _continue_after_tutorial(cb)


def skip_tutorial_panel(self, *args, **kwargs):
    _f7_log('TUTORIAL UI SKIP panel=%s' % self.__class__.__name__)
    _continue_after_tutorial(kwargs.get('cb'))


def skip_new_monster_tutorial(self, monsters):
    # Stock notify_show can also return before freezing under its debug flag.
    # Its caller continues the real combat event independently of this panel.
    _f7_log('TUTORIAL UI SKIP new monster introduction')


def no_newbee_trigger(self, event):
    return False


def clear_newbee_queue(self):
    self.clent_trigger_event_list = []
    return False


def skip_newbee_request(self, *args, **kwargs):
    self.newbeeData.clent_trigger_event_list = []
    return False


def continue_story_without_teaching(self, event):
    _f7_log('TUTORIAL UI SKIP main-event=%r; continuing original startEventUI' % event)
    return self.startEventUI(event)


def install_tutorial_bypass():
    if not SKIP_TUTORIAL_UI:
        return

    def replace(module_name, class_name, method_name, replacement):
        module = __import__(module_name, fromlist=[class_name])
        setattr(getattr(module, class_name), method_name, replacement)

    replace('entity.avatar_attrs.NewbeeData', 'NewbeeData', 'canNewbeeTrigger', no_newbee_trigger)
    replace('entity.avatar_attrs.NewbeeData', 'NewbeeData', 'checkAllNewbee', clear_newbee_queue)
    for method in ('clientTriggerNewbeeFromClient', 'clientAskTriggerNewbee',
                   'checkProcessingNewbee', 'triggerNewbee'):
        replace('entity.avatar_members.NewbeeMember', 'Member', method, skip_newbee_request)
    replace('entity.avatar_members.EventTriggerMember', 'Member',
            'startEventNewbee', continue_story_without_teaching)
    replace('cocos.panels.newbee_guidance', 'Panel', 'trigger_newbee_event', skip_guidance)
    replace('cocos.panels.newbee_guidance', 'Panel', 'notify_show', skip_tutorial_panel)
    for method in ('notify_mask_area', 'notify_mask_build', 'notify_mask_upgrade'):
        replace('cocos.panels.newbee_mask', 'Panel', method, skip_tutorial_panel)
    for module in ('combat_guide_hero', 'combat_guide_restrain', 'city_yanhua_guide'):
        replace('cocos.panels.' + module, 'Panel', 'notify_show', skip_tutorial_panel)
    replace('cocos.panels.combat_monster', 'Panel', 'notify_show', skip_new_monster_tutorial)
    replace('cocos.panels.city', 'Panel', 'on_yanhua_guide_click', skip_tutorial_panel)
    replace('cocos.panels.common_confirm', 'Panel', 'notify_guide_bind', skip_tutorial_panel)
    _f7_log('Tutorial UI entry points disabled; story callbacks and ordinary confirmations retained')


# Startup warning shown as an in-game private message.  The text is the same
# notice Project7 publishes in local_notice.txt.
PAID_WARNING_ID = 990001
PAID_WARNING_TITLE = u'\u8bf7\u52ff\u4ed8\u8d39\u8d2d\u4e70'
PAID_WARNING_TEXT = u'\u203b\u5982\u679c\u4f60\u5728\u4efb\u4f55\u5730\u65b9\u4ed8\u8d39\u8d2d\u4e70\u5230\u4e86\u672c\u6e38\u620f\uff0c\u90a3\u4e48\u4f60\u88ab\u9a97\u4e86\uff01\u8bf7\u52a1\u5fc5\u52a8\u52a8\u5c0f\u624b\uff0c\u70b9\u70b9\u4e3e\u62a5\uff0c\u8ba9\u574f\u4eba\u5f97\u5230\u5e94\u6709\u7684\u4ee3\u4ef7\uff01(^o^)\uff0f'
_PAID_WARNING_INSTALLED = False


def install_paid_warning():
    global _PAID_WARNING_INSTALLED
    if _PAID_WARNING_INSTALLED:
        return
    try:
        import time
        import com.data.cdata.private_msg as private_msg
        from entity.avatar_attrs.SocialData import PrivateMsg

        private_msg.data[PAID_WARNING_ID] = {
            'id': PAID_WARNING_ID,
            'contact_num': 60000,
            'npc': 60000,
            'title': PAID_WARNING_TITLE,
            'content': PAID_WARNING_TEXT,
        }

        from entity.ClientAvatar import ClientAvatar
        original_init = ClientAvatar.init_from_dict

        def init_with_paid_warning(self, bdict):
            result = original_init(self, bdict)
            try:
                msg = PrivateMsg({'id': PAID_WARNING_ID, 'rd': False, 'rp': False,
                                  'rt': time.time()})
                self.socialData.privateMsg[PAID_WARNING_ID] = msg
                import gg
                tree = getattr(getattr(gg, 'ui', None), '_tree', None)
                if tree is not None:
                    tree.proc_event('red_point_update', 'social', _children=True)
                    tree.proc_event('private_msg_add', PAID_WARNING_ID, _children=True)
            except Exception:
                pass
            return result

        ClientAvatar.init_from_dict = init_with_paid_warning
        _PAID_WARNING_INSTALLED = True
    except Exception:
        # Host/source checks may not provide the game package graph.  Never make
        # the warning optional dependency break startup.
        return
