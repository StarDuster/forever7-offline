# -*- coding: utf-8 -*-
# Executed by the game's Python 2.7 interpreter, not by the host Python.
import os
import time
import game3d
import sys
import traceback

_f7_doc = game3d.get_doc_dir()
with open(os.path.join(_f7_doc, 'offline_boot_probe.txt'), 'w') as _f7_out:
    _f7_out.write('bootstrap reached at %s\n' % time.time())
    _f7_out.write('documents=%s\n' % _f7_doc)

def _f7_log(message):
    with open(os.path.join(_f7_doc, 'offline_runtime.log'), 'a') as handle:
        handle.write('%s %s\n' % (time.time(), message))


try:
    import patch.patch as _f7_patch
    _f7_clean = _f7_patch.clean

    def _f7_clean_for_local_start(state):
        _f7_log('Entering original patch cleanup')
        _f7_clean(state)
        _f7_log('Original patch cleanup complete')
        import com.const as local_const
        local_const.DEBUG_LOGIN = True
        local_const.DEBUG_OFFLINE = False
        local_const.DEBUG_DBX = False
        _f7_gateway_path = os.path.join(_f7_doc, 'local_gateway.py')
        if '_f7_embedded_gateway_source' in globals():
            _f7_gateway_source = _f7_embedded_gateway_source
        else:
            _f7_store_source = open(os.path.join(_f7_doc, 'offline_store.py'), 'rb').read()
            _f7_wardrobe_source = open(os.path.join(_f7_doc, 'offline_wardrobe_completion.py'), 'rb').read()
            _f7_profile_source = open(os.path.join(_f7_doc, 'offline_profile.py'), 'rb').read()
            _f7_tutorial_source = open(os.path.join(_f7_doc, 'offline_tutorials.py'), 'rb').read()
            _f7_transport_source = open(os.path.join(_f7_doc, 'offline_transport.py'), 'rb').read()
            _f7_battle_terminal_source = open(os.path.join(_f7_doc, 'offline_battle_terminal.py'), 'rb').read()
            _f7_role_mission_source = open(os.path.join(_f7_doc, 'offline_role_mission.py'), 'rb').read()
            _f7_event_battle_source = open(os.path.join(_f7_doc, 'offline_event_battle.py'), 'rb').read()
            _f7_battle_source = open(os.path.join(_f7_doc, 'offline_battle.py'), 'rb').read()
            _f7_huisu_source = open(os.path.join(_f7_doc, 'offline_huisu.py'), 'rb').read()
            _f7_flashback_source = open(os.path.join(_f7_doc, 'offline_flashback.py'), 'rb').read()
            _f7_city_stage_provider_source = open(os.path.join(_f7_doc, 'offline_city_stage_provider.py'), 'rb').read()
            _f7_special_city_stage_source = open(os.path.join(_f7_doc, 'offline_special_city_stage.py'), 'rb').read()
            _f7_chapter_campaign_source = open(os.path.join(_f7_doc, 'offline_chapter_campaign.py'), 'rb').read()
            _f7_stage_source = open(os.path.join(_f7_doc, 'offline_stage.py'), 'rb').read()
            _f7_intelligence_source = open(os.path.join(_f7_doc, 'offline_intelligence.py'), 'rb').read()
            _f7_yumi_source = open(os.path.join(_f7_doc, 'offline_yumi.py'), 'rb').read()
            _f7_route_agreements_source = open(os.path.join(_f7_doc, 'offline_route_agreements.py'), 'rb').read()
            _f7_week_source = open(os.path.join(_f7_doc, 'offline_week.py'), 'rb').read()
            _f7_day_source = open(os.path.join(_f7_doc, 'offline_day.py'), 'rb').read()
            _f7_action_ledger_source = open(os.path.join(_f7_doc, 'offline_action_ledger.py'), 'rb').read()
            _f7_conditions_source = open(os.path.join(_f7_doc, 'offline_conditions.py'), 'rb').read()
            _f7_daerweila_source = open(os.path.join(_f7_doc, 'offline_daerweila.py'), 'rb').read()
            _f7_story_source = open(os.path.join(_f7_doc, 'offline_story.py'), 'rb').read()
            _f7_effects_source = open(os.path.join(_f7_doc, 'offline_event_effects.py'), 'rb').read()
            _f7_story_engine_source = open(os.path.join(_f7_doc, 'offline_story_engine.py'), 'rb').read()
            _f7_native_story_source = open(os.path.join(_f7_doc, 'offline_native_story_callbacks.py'), 'rb').read()
            _f7_city_actions_source = open(os.path.join(_f7_doc, 'offline_city_actions.py'), 'rb').read()
            _f7_avatar_source = open(os.path.join(_f7_doc, 'offline_avatar_snapshot.py'), 'rb').read()
            _f7_postbattle_source = open(os.path.join(_f7_doc, 'offline_postbattle.py'), 'rb').read()
            _f7_treasure_source = open(os.path.join(_f7_doc, 'offline_treasure.py'), 'rb').read()
            _f7_gacha_source = open(os.path.join(_f7_doc, 'offline_gacha.py'), 'rb').read()
            _f7_gacha_pools_source = open(os.path.join(_f7_doc, 'offline_gacha_pools.py'), 'rb').read()
            _f7_gacha_special_source = open(os.path.join(_f7_doc, 'offline_gacha_special.py'), 'rb').read()
            _f7_gacha_gateway_source = open(os.path.join(_f7_doc, 'offline_gacha_gateway.py'), 'rb').read()
            _f7_gacha_rewards_source = open(os.path.join(_f7_doc, 'offline_gacha_rewards.py'), 'rb').read()
            _f7_gacha_costs_source = open(os.path.join(_f7_doc, 'offline_gacha_costs.py'), 'rb').read()
            _f7_gacha_archive_source = open(os.path.join(_f7_doc, 'offline_gacha_archive.py'), 'rb').read()
            _f7_gacha_ui_source = open(os.path.join(_f7_doc, 'offline_gacha_ui.py'), 'rb').read()
            _f7_rpc_rejections_source = open(os.path.join(_f7_doc, 'offline_rpc_rejections.py'), 'rb').read()
            _f7_item_exchange_source = open(os.path.join(_f7_doc, 'offline_item_exchange.py'), 'rb').read()
            _f7_gateway_source = (_f7_store_source + '\n' + _f7_wardrobe_source + '\n' + _f7_profile_source + '\n' +
                                  _f7_transport_source + '\n' + _f7_battle_terminal_source + '\n' + _f7_role_mission_source + '\n' + _f7_event_battle_source + '\n' + _f7_battle_source + '\n' + _f7_flashback_source + '\n' + _f7_huisu_source + '\n' + _f7_city_stage_provider_source + '\n' + _f7_special_city_stage_source + '\n' + _f7_chapter_campaign_source + '\n' + _f7_stage_source + '\n' + _f7_intelligence_source + '\n' + _f7_yumi_source + '\n' + _f7_route_agreements_source + '\n' + _f7_week_source + '\n' + _f7_day_source + '\n' + _f7_action_ledger_source + '\n' + _f7_conditions_source + '\n' + _f7_daerweila_source + '\n' + _f7_story_source + '\n' + _f7_effects_source + '\n' + _f7_story_engine_source + '\n' + _f7_native_story_source + '\n' + _f7_city_actions_source + '\n' + _f7_avatar_source + '\n' + _f7_postbattle_source + '\n' + _f7_treasure_source + '\n' + _f7_gacha_source + '\n' + _f7_gacha_pools_source + '\n' + _f7_gacha_special_source + '\n' + _f7_gacha_gateway_source + '\n' + _f7_gacha_rewards_source + '\n' + _f7_gacha_costs_source + '\n' + _f7_gacha_archive_source + '\n' + _f7_gacha_ui_source + '\n' + _f7_tutorial_source + '\n' + _f7_rpc_rejections_source + '\n' + _f7_item_exchange_source + '\n' + open(_f7_gateway_path, 'rb').read())
        _f7_log('Compiling local gateway source')
        _f7_gateway_code = compile(_f7_gateway_source, _f7_gateway_path, 'exec')
        _f7_log('Executing local gateway source')
        exec _f7_gateway_code in globals(), globals()
        _f7_log('Installing local gateway callbacks')
        install_gateway()
        _f7_log('Local flags installed after patch cleanup')

    _f7_patch.clean = _f7_clean_for_local_start
    _f7_patch.patch_hotfix.after_hotfix = lambda: True
    _f7_patch.pdrpf.drpf_update_success = lambda: None
    _f7_log('Starting local resources without online updater')
    _f7_patch.done(True)
    _f7_log('Game initialization scheduled')
except:
    _f7_log(traceback.format_exc())
    raise
